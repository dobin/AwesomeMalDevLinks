# https://rastamouse.me/cpl-hook-chains/

Despite what some would lead you to believe, [Crystal Kit](https://github.com/rasta-mouse/Crystal-Kit) is not, and was never intended to be, an all-encompassing nirvana of evasion tradecraft. It was a simple project to experiment with [Crystal Palace](https://tradecraftgarden.org/crystalpalace.html) (CPL) by applying evasion tradecraft to Cobalt Strike's Beacon. There are some capabilities of CPL that I lean into more than others, and some that I ignore completely. My decision not to do something in Crystal Kit isn't a reflection of CPL.

CPL has also come a long way in a relatively short space of time. Its original focus was on applying tradecraft to DLL loaders but has since become a cornucopia of merging, hooking, COFFs, PIC, PICOs, bin2bin transformations, and loads more. I have not kept Crystal Kit's architecture in-step with CPL as it's matured, and one area where that's very apparent is in the way it does its IAT hooking.

### Single hooks

CPL's `__resolve_hook()` intrinsic was originally only accessible via the `addhook "MOD$Func" "hook"` command, where `MOD$Func` represents an API to hook (e.g. `KERNEL32$Sleep`) and `hook` is the hook function that execution is redirected to. Crystal Kit registers hooks for a bunch of APIs and implements all of its evasion tradecraft in the corresponding hook function for each. The following is an example of the Sleep hook:

```c
#include <windows.h>
#include "memory.h"
#include "spoof.h"

VOID WINAPI _Sleep( DWORD dwMilliseconds )
{
    //
    // mask memory
    if ( dwMilliseconds >= 1000 ) {
        maskMemory( TRUE );
    }

    //
    // do the spoofed api call
    FUNCTION_CALL call = { 0 };

    call.ptr       = ( PVOID )( KERNEL32$Sleep );
    call.argc      = 1;
    call.args[ 0 ] = spoof_arg( dwMilliseconds );

    spoofCall( &call );

    //
    // unmask memory
    if ( dwMilliseconds >= 1000 ) {
        maskMemory( FALSE );
    }
}
```

mask.c

You can see that the tradecraft I opted to implement here is gargoyle-style sleep obfuscation with some call stack spoofing. However, the issue with this approach is that it doesn't align with CPL's goal of modular tradecraft. In such a paradigm, you want the sleep obfuscation and stack spoofing code to be completely separate. The way Crystal Kit is built today, it's not a 100% straight-forward process to replace the stack spoofing implementation with another one, replace it with different tradecraft (such as a syscall), or even remove the tradecraft entirely, without heavy code modifications.

### Hook chains

CPL has\* an interesting way of addressing this by way of hook "chains", which allow you to register multiple hook functions for an API. You begin by registering a hook chain using the `addhook "MOD$Func"` command (you do not provide a hook function), e.g. `addhook "KERNEL32$Sleep"`.

\*️⃣

Hook chains were added after Crystal Kit was first written, so although I jest in the blog's title that I did it wrong, there was no other way at the time 😃

You then register multiple hooks in the order you want them to be applied using the `attach "MOD$Func" "hook"` command (not the `addhook` command).

To recreate the example above, we'd use one hook to apply the sleep obfuscation by doing `attach "KERNEL32$Sleep" _Sleep_Mask` \- but instead of setting up the spoofed API call - it will just call the regular DFR function.

```c
#include <windows.h>
#include "memory.h"

DECLSPEC_IMPORT VOID WINAPI KERNEL32$Sleep( DWORD );

VOID WINAPI _Sleep_Mask( DWORD dwMilliseconds )
{
    //
    // mask memory
    if ( dwMilliseconds >= 1000 ) {
        maskMemory( TRUE );
    }

    //
    // do the sleep
    KERNEL32$Sleep( dwMilliseconds );

    //
    // unmask memory
    if ( dwMilliseconds >= 1000 ) {
        maskMemory( FALSE );
    }
}
```

mask.c

You then register a second hook - `attach "KERNEL32$Sleep" "_Sleep_Spoof"` \- to perform the stack spoofing.

```c
#include <windows.h>
#include "spoof.h"

DECLSPEC_IMPORT VOID WINAPI KERNEL32$Sleep( DWORD );

VOID WINAPI _Sleep_Spoof( DWORD dwMilliseconds )
{
    //
    // spoof the api call
    FUNCTION_CALL call = { 0 };

    call.ptr       = ( PVOID )( KERNEL32$Sleep );
    call.argc      = 1;
    call.args[ 0 ] = spoof_arg( dwMilliseconds );

    spoofCall( &call );
}
```

spoof.c

In this arrangement, `KERNEL32$Sleep` in the DLL's IAT would be hooked to point at `_Sleep_Mask`, and `KERNEL32$Sleep` in `_Sleep_Mask` would be hooked to point at `_Sleep_Spoof`. It also allows the masking code to live in its own file, `mask.c`, and the stack spoofing code to exist in its own file, `spoof.c`. They never need mix or be aware of each other.

You would likely put each group of hooks in their own spec file, e.g:

```text
x64:
  load "bin/mask.x64.o"
    merge

  attach "KERNEL32$Sleep" "_Sleep_Mask"
```

mask.spec

```text
x64:
  load "bin/spoof.x64.o"
    merge

  attach "KERNEL32$Sleep" "_Sleep_Spoof"
```

spoof.spec

And then tie everything together in a top-level spec file, something like:

```text
x64:
  load "bin/hooks.x64.o"    # this is where __resolve_hook() lives
    make object +optimize   # make it a PICO

  # register hook chains
  addhook "KERNEL32$Sleep"
  addhook "..."

  # process & merge tradecraft specs
  run "mask.spec"
  run "spoof.spec"
  run "..."
    export
    link "..."
```

loader.spec

Throw in some `dprintf`'s to verify the hook chain.

```text
[+] _Sleep_Mask
    |-> masking: 0x00007FF4E2AE0000 (1024)
    |-> masking: 0x00007FF4E2AE1000 (196096)
    |-> masking: 0x00007FF4E2B11000 (27648)
    |-> masking: 0x00007FF4E2B18000 (8704)
    |-> masking: 0x00007FF4E2B2A000 (512)

  [+] _Sleep_Mask
      |-> calling KERNEL32$Sleep

  [+] _Sleep_Spoof
      |-> ptr: 0x00007FFDEAF81A10
      |-> argc: 1
      |-> args[0]: 0BB8

  [+] _Sleep_Mask
    |-> unmasking: 0x00007FF4E2AE0000 (1024)
    |-> unmasking: 0x00007FF4E2AE1000 (196096)
    |-> unmasking: 0x00007FF4E2B11000 (27648)
    |-> unmasking: 0x00007FF4E2B18000 (8704)
    |-> unmasking: 0x00007FF4E2B2A000 (512)
```

This design makes swapping, adding, and removing tradecraft as simple as 1-line changes in the spec file, rather than at the code level. If no hook is registered then DFR references revert back to standard API calls.

### Conclusion

This post provided a quick look at hook chains in Crystal Palace and how they're useful for layering tradecraft compared to using single hooks. The specification files are pretty flexible - if you didn't want to hardcode specific spec files, you could probably pass them in as a `%VAR` and use a `foreach` to process each one automagically.

### You might also like...

28


Jul


## COFF Mixing - Hiding in Plain Sight

4 min read


[COFF Mixing - Hiding in Plain Sight](https://rastamouse.me/coff-mixing/)

05


Jun


## BOF Cocktails in Cobalt Strike

2 min read


[BOF Cocktails in Cobalt Strike](https://rastamouse.me/bof-cocktails-in-cobalt-strike/)

26


May


## Module Stomping PIC

4 min read


[Module Stomping PIC](https://rastamouse.me/module-stomping-pic/)

25


Apr


## Atomic BOFs

5 min read


[Atomic BOFs](https://rastamouse.me/atomic-bofs/)

09


Apr


## Crystal Mask

8 min read


[Crystal Mask](https://rastamouse.me/crystal-mask/)