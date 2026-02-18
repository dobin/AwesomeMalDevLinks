# https://elliotonsecurity.com/perfect-dll-hijacking/

# Perfect DLL Hijacking

2023-10-19  Elliot Killick [Twitter](https://twitter.com/ElliotKillick "Twitter")[GitHub](https://github.com/ElliotKillick "GitHub")

DLL Hijacking (sometimes also referred to as DLL Side-Loading or DLL Preloading) is a technique that enables third-party code to be injected into a legitimate process (EXE) by fooling it into loading the wrong library (DLL). The most common way this happens is by placing your lookalike DLL higher up in the search order than the intended DLL, thereby getting your DLL selected first by the Windows library loader.

While mostly being a decisive technique, DLL hijacking has always had one **huge** disadvantage in the way that it executes our third-party code once loaded into the process. It's known as **Loader Lock**, and when our third-party code is run, it's subject to all its strict limitations. These include creating processes, doing network I/O, calling registry functions, creating graphical windows, loading additional libraries, and much more. Trying to do any of these things under Loader Lock may **crash or hang** the application.

Until now, only satisfactory (but needing something more), soon-to-break, or sometimes a tad over-engineered solutions for this problem have existed. So today, we're doing 100% original research reverse engineering the Windows library loader to not just cleanly workaround Loader Lock but, in the end, disable it outright. Plus, coming up with some stable mitigation & detection mechanisms defenders can use to help guard against DLL hijacking.

## About DllMain [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#about-dllmain)

`DllMain` is a DLL's initialization function under Windows. Whenever a DLL is loaded, `DllMain` is called and the code inside it (e.g. our third-party code) is executed. `DllMain` is run under Loader Lock which, as previously mentioned, puts some limitations on what can be done safely from `Dllmain`.

[![](https://elliotonsecurity.com/perfect-dll-hijacking/library-load-dllmain-loader-lock-state-transitions.png)](https://elliotonsecurity.com/perfect-dll-hijacking/library-load-dllmain-loader-lock-state-transitions.png)

**Specifically, Microsoft would just like to make us aware of _[one minor caveat](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-best-practices#general-best-practices)_ about doing anything from `DllMain`:**

> You should never perform the following tasks from within DllMain:
>
> - Call LoadLibrary or LoadLibraryEx (either directly or indirectly). This can cause a deadlock or a crash.
> - Call GetStringTypeA, GetStringTypeEx, or GetStringTypeW (either directly or indirectly). This can cause a deadlock or a crash.
> - Synchronize with other threads. This can cause a deadlock.
> - Acquire a synchronization object that is owned by code that is waiting to acquire the loader lock. This can cause a deadlock.
> - Initialize COM threads by using CoInitializeEx. Under certain conditions, this function can call LoadLibraryEx.
> - Call the registry functions.
> - Call CreateProcess. Creating a process can load another DLL.
> - Call ExitThread. Exiting a thread during DLL detach can cause the loader lock to be acquired again, causing a deadlock or a crash.
> - Call CreateThread. Creating a thread can work if you do not synchronize with other threads, but it is risky.
> - Call ShGetFolterPathW. Calling shell/known folder APIs can result in thread synchronization, and can therefore cause deadlocks.
> - Create a named pipe or other named object (Windows 2000 only). In Windows 2000, named objects are provided by the Terminal Services DLL. If this DLL is not initialized, calls to the DLL can cause the process to crash.
> - Use the memory management function from the dynamic C Run-Time (CRT). If the CRT DLL is not initialized, calls to these functions can cause the process to crash.
> - Call functions in User32.dll or Gdi32.dll. Some functions load another DLL, which may not be initialized.
> - Use managed code.

As laid out by Microsoft, these are the "Best Practices" for what can be done safely from `DllMain` without potentially bad things or unintended side effects happening, if not a deadlock or crash all together. Ah yes, these limitations have caused so many, so much pain! _A moment of silence for all the Win32 devs, please._

## Where We're At [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#where-we-re-at)

The starting point for my research was primarily an informative article called **["Adaptive DLL Hijacking"](https://www.netspi.com/blog/technical/adversary-simulation/adaptive-dll-hijacking/) by security professional Nick Landers (@monoxgas) at NetSPI**. This is exceptional research and I've experimented with some of the resulting techniques and tools (such as Koppeling) myself in the past. As with all fantastic research, it must be innovated upon further, which is exactly what we're doing today!

Current projects around the Internet for performing **universal** DLL hijacking (only involving `DllMain`) all require you to do one of two problematic actions:

1. Change memory protection (with `VirtualProtect`)
2. Modify pointers

Number one is less than ideal because anti-malware solutions flag on `VirtualProtect` operations. Especially ones that create read-write-execute memory or convert memory from read-write ➜ read-execute. This is for good reason because changing executable memory protection is indicative of self-modifying code techniques, which is perhaps the easiest way to bypass static anti-malware detections. A process with [arbitrary code guard (ACG)](https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/exploit-protection-reference#arbitrary-code-guard) enabled blocks creation or modification of executable memory altogether.

I've seen some cases where API call instrumentation with [Microsoft Detours](https://github.com/microsoft/Detours) was used as a technique. While it may work, it results in a largely increased DLL size and anti-malware solutions will flag this down without a second thought. Also, it's not ACG compatible because it changes exectuable memory protection.

Number two is also less than ideal because pointers are the target of almost all next-generation exploit mitigations. For instance, a function's return address on the stack being modified to get code execution after Locker Lock is released. This technique had a good run where it was applicable but is due to break under an upcoming exploit mitigation called Intel Control-flow Enforcement Technology (CET). CET cross-references function return addresses on the stack with a "shadow stack" locked away in the CPU hardware to ensure they're valid and untampered with; otherwise, forcefully terminating the offending process. There will probably come a day when all pointers are authenticated 1:1, so it's best to future-proof our techniques by avoiding pointer modification entirely.

In other words, we're striving for a data-only technique.

I've also noticed that some existing techniques, while versatile, are a bit long/complex or are designed for either dynamic load (`LoadLibrary`) or static loads (typically not including process startup, e.g. due to `NtContinue`). Some methods also need to feature stable process continuation.

Avoiding these problematic actions are requirements for the new techniques we will be exploring here.

## Security Researcher Mindset [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#security-researcher-mindset)

When you're exploring unchartered territory, it's easy to become confused and give up too quickly. This is why it's important to remind ourselves of what we have to work with so creativity can take hold. For me, before researching this, I had just come out of exploiting, and responsibly reporting to HackerOne, a memory corruption issue (e.g. a buffer overflow) where the bug I had found allowed untrusted data to control the destination of a `call` instruction (i.e. arbitrary **call**) thus eventually giving way to arbitrary code execution on a remote computer.

In the context of a DLL hijacking, we are granted access to **all three** basic primitives, including arbitrary **read, write, and call** to _anywhere_ in the program's (virtual) memory (!). We also have easy access to **tons** of [weird machines](https://en.wikipedia.org/wiki/Weird_machine) (many, many lines of code) that exist in Windows libraries because we're the ones writing the code (even if our code is run under Loader Lock in `DllMain`). Furthermore, we can interact with weird machines outside our hijacked process' virtual memory space by using system calls to talk to the kernel. It's easy to take these luxuries for granted until you're under more constrained attack scenarios.

All this is to say that the odds that there don't exist many mechanisms that can allow us to cleanly (e.g. without changing memory protection) redirect code execution from `DllMain` after Loader Lock is released (or even find out how to disable it altogether) are essentially zero. As researchers, we can explore confidently, knowing we will find what we seek. This is the mindset I began my search with.

![Information alert](https://elliotonsecurity.com/assets/images/alert-icons/circle-info-solid.svg)Info

Loader lock isn't a security boundary, just a nuisance for some programming use cases and DLL hijacking. However, that doesn't mean some of the same thought processes can't apply.

"Lock" here refers to a mutex (short for [mutual exclusion](https://en.wikipedia.org/wiki/Lock_(computer_science))) which is a concept in concurrency. If you studied computer science, then there's a good chance you learned about it.

## Our Target [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#our-target)

We're going to be attempting our DLL hijacking techniques on a program built into Windows by default: `C:\Program Files\Windows Defender\Offline\OfflineScannerShell.exe`

[![](https://elliotonsecurity.com/perfect-dll-hijacking/offlinescannershell-location.png)](https://elliotonsecurity.com/perfect-dll-hijacking/offlinescannershell-location.png)

Attempting to start this program (just with a double-click) will yield this error clearly showing it's susceptible to DLL hijacking:

[![](https://elliotonsecurity.com/perfect-dll-hijacking/offlinescannershell-mpclient-dll-not-found-error.png)](https://elliotonsecurity.com/perfect-dll-hijacking/offlinescannershell-mpclient-dll-not-found-error.png)

This occurs because `mpclient.dll` is located in `C:\Program Files\Windows Defender`, one directory up from the program's current `Offline` folder. So, correctly running this program requires first setting your current working directory (CWD) to `C:\Program Files\Windows Defender` (most easily done using CMD). This causes the real `mpclient.dll` to be in the search path thus `OfflineScannerShell.exe` runs successfully:

```cmd
C:\>cd C:\Program Files\Windows Defender
C:\Program Files\Windows Defender>Offline\OfflineScannerShell.exe

C:\Program Files\Windows Defender>echo %ERRORLEVEL%
0
```

However, if we set the CWD to anywhere else like our user profile (`C:\Users\<YOUR_USERNAME>`) then when `OfflineScannerShell.exe` looks for `mpclient.dll` we can make it will load our copy at `C:\Users\<YOUR_USERNAME>\mpclient.dll`!

Any path contained within the `PATH` global envirnonment variable (printed here with CMD) will also work:

```cmd
C:\Users\user>echo %PATH%
C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Windows\System32\OpenSSH\;C:\Users\<YOUR_USERNAME>\AppData\Local\Microsoft\WindowsApps
```

`C:\Users\<YOUR_USERNAME>\AppData\Local\Microsoft\WindowsApps` is another perfect user-writable spot that exists on Windows by **default** which `OfflineScannerShell.exe` (or any other program) will load DLLs from if you don't so much as want to set the current working directory.

As we will find out later, there are **tons of other potential DLL hijacking targets baked into Windows and beyond** that we could employ our new techniques on, but I just like this one.

### Our Payload [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#our-payload)

For our example payload, we will be launching the Calculator application by doing:

```c
ShellExecute(NULL, L"open", L"calc", NULL, NULL, SW_SHOW);
```

**However, it's important to note that realistically, you would continue running out of the legitimate (but hijacked) process; otherwise, that defeats the purpose of DLL hijacking (in most scenarios).** For red teaming, spawning a reverse shell (e.g. with Metasploit or Colbalt Strike) in the legitimate process while otherwise letting the program run as normal (with no sign that anything out of the ordinary has happened) would probably be the ideal final payload.

Why `ShellExecute`? Well, `ShellExecute` works amazingly well as a litmus test for anything that could go wrong in NTDLL. This is because it's widely known the vast amount of Windows subsystems this one API call interacts with. Everything from the library loader, to COM/COM+ infrastructure, using ALPC, RPC, WinRT storage calls, CRT functions, registry functions, it even creates an entire **new thread** just to launch that one application, the calculator (`calc` or `C:\Windows\System32\calc.exe`)! `ShellExecute` is probably the single most bloated and complex API call in the whole of Windows API (after `ShellExecuteEx`, of course). So, it stands to reason that we can validate the success of a technique in practice by calling it.

As with most things involving `DllMain`, trying to call `ShellExecute` (and especially `ShellExecute`) without doing anything else fails spectacularly with an ominous deadlock at `ntdll!NtAlpcSendWaitReceivePort` (??) causing the program to hang indefinitely:

[![](https://elliotonsecurity.com/perfect-dll-hijacking/shellexecute-initial-deadlock-point.png)](https://elliotonsecurity.com/perfect-dll-hijacking/shellexecute-initial-deadlock-point.png)

Searching that function up (or any of its neighbors) yields little to no results because it's nearly all entirely undocumented! I love it when that happens.

Other times, you can crash with an `ntdll!TppRaiseInvalidParameter` exception because an internal function wanted to raise a nice [NTSTATUS](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/596a1078-e883-4972-9bbc-49e60bebca55) (in this case, `STATUS_INVALID_PARAMETER`) a few miles deep into the call stack (???). Try to mess around, and you might face a no-nonsense memory Access Violation. Like a box of chocolates, you can never really know what you're going to get.

Let's see if we can change that!

### The Perfect Candidate [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#the-perfect-candidate)

`OfflineScannerShell.exe` is what I would call a "worst-case scenario" in terms of DLL hijacking (at least with already existing techniques). This makes it perfect for ensuring our new techniques will work universally. What makes `OfflineScannerShell.exe` a worst-case scenario comes down to a few things:

- Won't call exports of hijackable DLL, so using `DllMain` to redirect code execution is a must
  - Many programs with hijackable DLLs exit early unless very specific preconditions
    - Often times, it's not possible to meet these preconditions
  - I verified this for `OfflineScannerShell.exe` by setting a breakpoint on every function exported by `MpClient.dll` then running the program to check for breakpoint hits
- Program exits _immediately_ after starting (doesn't stay open, idle, or wait)
- Hijackable DLL is loaded statically; especially at **process startup** (not dynamically loaded by calling `LoadLibrary` at program run-time)
  - Generally speaking, because you're deeper in library loader internals (the process is still starting up)

That's basically it. **If your target program calls an export of your hijackable DLL at some point in its lifetime, then you're golden because you can just redirect code execution from there without having to worry about the struggles of `DllMain` and `Loader Lock` at all.** This is sometimes referred to as DLL proxying. However, in the majority of cases I've seen when a DLL is hijackable, it's usually a very obscure library that's called a few times very deep into the application's code where there may be no way of easily (if at all) reaching unless the program is called in exactly the correct environment. Anything else, and it will simply exit immediately because, for example, you're running a service executable which links with a hijackable DLL. But, as soon as you run the service executable, it's going to see it wasn't started correctly (as a [Windows service](https://en.wikipedia.org/wiki/Windows_service)) and immediately close. This complicates what should be a simple hijacking process, considering we were already granted code execution in `DllMain` when the application started, just under the infamous Loader Lock.

As I learned, the only favorable thing about `OfflineScannerShell.exe` from a DLL hijacking perspective is that it links with a C runtime (CRT); in other words, it's not a pure Windows API (Win32) program. The vast majority of programs in Windows link with a CRT, though, so it's not a unique advantage. Why this is favorable, we will cover later.

## New Techniques [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#new-techniques)

### Racing the Main Thread [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#racing-the-main-thread)

This technique mainly builds on insights from "Adaptive DLL Hijacking" posted on NetSPI.

My initial expansions on this technique could not achieve a 100% success rate for our target. However, it provided a good learning experience, hence why I included it. At the end of this section, I hint at a slightly different approach to our expansions on this technique, for which a 100% success rate is achievable (more to come soon).

**If you only want the best _shiny_ new techniques available right now, then feel free to skip ahead to the [next section](https://elliotonsecurity.com/perfect-dll-hijacking/#escaping-at-the-exit).**

#### Initial Experiments [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#initial-experiments)

As Microsoft states in the aforementioned "Best Practices" documentation, calling `CreateThread` from `DllMain` "can work":

```c
// DllMain boilerplate code (required in every DLL)
BOOL WINAPI DllMain(HINSTANCE hinstDll, DWORD fdwReason, LPVOID lpvReserved)
{
    switch (fdwReason)
    {
    case DLL_PROCESS_ATTACH:
        // Create a thread
        // Thread runs our "CustomPayloadFunction" (not shown here)
        DWORD threadId;
        HANDLE newThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)CustomPayloadFunction, NULL, 0, &threadId);
    }

    return TRUE;
}
```

And it does! But there's a catch because the thread created by calling `CreateThread` will wait (in more ways than one) until we leave `DllMain` to begin execution. Pulling this off then requires that we call `CreateThread`, allow the program to exit `DllMain` (Loader Lock and friends are released shortly thereafter), and hope that the thread is created before the main thread exits the program.

Creating a thread is a relatively expensive operation, so if our target program exits fairly quickly, we may not win this race. Perhaps somehow we can improve our chances of success...

##### Improving our odds [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#improving-our-odds)

Somehow like by calling `SetThreadPriority` to raise the priority of our newly queued thread to the **hightest level** (`THREAD_PRIORITY_TIME_CRITICAL`) while dropping the priority of the main thread to **as low as it will go** (`THREAD_PRIORITY_IDLE`; which one level lower in priority than even `THREAD_PRIORITY_LOWEST`)!

Extending our previous code, we can add this after `CreateThread`:

```c
SetThreadPriority(newThread, THREAD_PRIORITY_TIME_CRITICAL);
SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_IDLE);

// Then return from DllMain and cross our fingers...
```

For `OfflineScannerShell.exe`, setting thread priority didn't t turn out to be necessary because enough is done before program exit to make time for the new thread to spawn anyway. However, it did moderately help to increase win rate in a simpler test bench I put together solely for loading our DLL statically at process startup. So, we will count this experiment as a minor success.

##### Stopping the main thread [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#stopping-the-main-thread)

Now that we've reached `CustomPayloadFunction` in our new thread, we need to quickly stop the main thread before it exits the program. Suspending our main thread with `SuspendThread` from our new thread is the most obvious way to accomplish this so we will go with that. To do that, `SuspendThread` requires a handle to the desired thread.

Easy enough, slightly modifying our previous `CreateThread`, we first get our current (main) thread handle with [GetCurrentThread](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getcurrentthread). Next, we pass this thread handle as an argument to `CustomPayloadFunction` like this:

```c
// Pass result of GetCurrentThread() as an argument to CustomPayloadFunction
HANDLE newThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)CustomPayloadFunction, GetCurrentThread(), 0, &threadId);
```

Then proceed to suspend it in `CustomPayloadFunction` (our new thread):

```c
VOID CustomPayloadFunction(HANDLE mainThread) {
    SuspendThread(mainThread);

    ...
}
```

But, there's a sneaky bug. **Can you spot it?**

This is a mistake I made myself years ago (working in another context). However, at the time, I was only a novice C and Win32 programmer with no WinDbg experience, so I couldn't quickly figure it out then. Then I forgot about the issue entirely and worked on more pressing matters.

The bug stems from the fact that `GetCurrentThread` does **not** return a handle; it returns a **pseudo** handle. `GetCurrentThread` is merely a stub that (on x86-64) always returns the constant `0xFFFFFFFFFFFFFFFE`:

[![](https://elliotonsecurity.com/perfect-dll-hijacking/getcurrentthread-disassembly.png)](https://elliotonsecurity.com/perfect-dll-hijacking/getcurrentthread-disassembly.png)

Thus, passing that value to our new thread will cause it to refer to the thread it was passed to, _not_ the thread we called `GetCurrentThread` on. The bug is quite subtle and easy to miss (especially if you're less familiar with Win32 programming as was I some years ago when initially attempting this idea). The correct approach for accomplishing what we want is:

```c
HANDLE mainThread = OpenThread(THREAD_SUSPEND_RESUME, FALSE, GetCurrentThreadId());
```

We create a **real** handle to the main thread from the current thread **ID** which can then correctly be passed as an argument to our new thread. Giving our handle only the minimum `THREAD_SUSPEND_RESUME` permissions required, our use case works out perfectly.

Under normal circumstances, passing our new thread the main thread's ID and then creating a handle from it on the new thread would probably result in clearer code. In our unique situation, though, we want to suspend the main thread from our new thread _as fast as possible_ so opening the handle ahead of time is the better choice. We just have to be extra careful about not forgetting to `CloseHandle` from our new thread so we don't leak resources. Windows also limits the number of handles a single process can have, so if an adversary can leak large amounts of handles, that could effectively DoS our application. Anyway, this isn't a lesson in programming but it's always good to know best practices (as we ironically continue to steamroll all of them)!

##### The problem with SuspendThread... [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#the-problem-with-suspendthread)

The final challenge to overcome with this technique is one Microsoft has summarized well for us in their [SuspendThread](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-suspendthread#remarks) documentation:

> This function is primarily designed for use by debuggers. It is not intended to be used for thread synchronization. Calling SuspendThread on a thread that owns a synchronization object, such as a mutex or critical section, can lead to a deadlock if the calling thread tries to obtain a synchronization object owned by a suspended thread. To avoid this situation, a thread within an application that is not a debugger should signal the other thread to suspend itself. The target thread must be designed to watch for this signal and respond appropriately.

This entails the biggest problem with the race approach. In `OfflineScannerShell.exe`, this issue surfaces every ten or so executions because the main thread will be suspended while it's doing a heap memory allocation/free. In Windows, each process has a default heap provided by the system (you can get it with the `GetProcessHeap` function). This heap is created with the `HEAP_NO_SERIALIZE` flag (serialization referring to operations being doing in _series_ as opposed to in _parallel_) unset which means that calls to heap allocation and free functions cause the heap to become locked then unlocked to ensure thread safety. For performance reasons, it may be desirable to create a non-serializing heap (`HeapCreate` with `HEAP_NO_SERIALIZE` set), in which case it would be the programmer's responsibility to either only use that heap on a single thread or ensure safe access across threads. We can do a one-time removal of the process heap lock by calling `HeapUnlock(GetProcessHeap())` from our new thread. However, this breaks thread safety guarantees which could cause the program to crash or other unintended side effects.

For example, in our tests we're using `ShellExecute` running `calc` as our final payload to run from the new thread. Well, `ShellExecute` (among many other Win32 functions) must make allocations to the process heap to work, which is where a deadlock could occur if we don't unlock the heap. It's worth noting that I've yet to realize the risk of a crash upon `HeapUnlock`, however, the chance of one occurring is non-zero as soon as we `HeapUnlock(GetProcessHeap())` then our new thread or another thread does a `HeapAlloc` (or an equivalent like `malloc`).

[![](https://elliotonsecurity.com/perfect-dll-hijacking/heap-allocate-deadlock-thread-1.png)](https://elliotonsecurity.com/perfect-dll-hijacking/heap-allocate-deadlock-thread-1.png)

[![](https://elliotonsecurity.com/perfect-dll-hijacking/heap-allocate-deadlock-thread-2.png)](https://elliotonsecurity.com/perfect-dll-hijacking/heap-allocate-deadlock-thread-2.png)

_Deadlock occurs because the suspended main thread is holding the heap lock (i.e. critical section) while the new thread tries to acquire it. Neither party can make progress, so the program hangs indefinitely._

#### A Different Approach? [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#a-different-approach)

In this technique's current state, assuming you want to keep the host process running until its natural end (and we do), this solution can only be 99% effective at best. It was an interesting experiment, but we can do better.

In essence, we need to be able to control where the main thread is when we suspend it from the new thread. The cleanest way I can think of doing this is by using locks to our advantage. We could acquire some lock in `DllMain` (stay with me here) that would cause the main thread to stop at a predictable point in the code because it's waiting to acquire the same lock. When our new thread launches, we run our payload, then release that lock so the program can continue to run freely like normal (and to ensure we don't exit too quickly). Using this method, we wouldn't even have to do any thread suspension because the locks do all our work for us! I have yet to try this because I only came up with the idea while writing this article, but it sounds like a winning strategy.

More on this in another article!

#### Detection Heuristics [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#detection-heuristics)

Still, calling `CreateThread` from `DllMain` (along with some other heuristics) could be used as a signature for detection by anti-malware software so for red teaming the technique leaves something to be desired. If defenders want to use this as a heuristic for detecting DLL hijacking then I advise you to hook where `ntdll!LdrpCallInitRoutine` initially calls into our DLL using the code pointer at our library's `LDR_DATA_TABLE_ENTRY.EntryPoint` (that would lead to `<DLL_NAME>!dllmain_dispatch` in our case). You can see what this [call stack](https://elliotonsecurity.com/perfect-dll-hijacking/#our-payload) looks like from an image shown previously in the Our Payload section. If you see any potentially suspicious Windows API calls like `CreateThread` being made in that interval, it could be a symptom of DLL hijacking. It's essential to do it like this instead of simply analyzing the call stack whenever certain suspicious Windows API functions are called because the call stack can too easily be temporarily spoofed. Even with Intel CET, the call stack can still be temporarily faked (e.g. before calling `CreateThread`), followed by changing it back to pass the return address integrity check on function (`DllMain`) return.

### Escaping at the Exit [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#escaping-at-the-exit)

[![](https://elliotonsecurity.com/perfect-dll-hijacking/atexit-sign.jpg)](https://elliotonsecurity.com/perfect-dll-hijacking/atexit-sign.jpg)

In [standard C](https://en.wikipedia.org/wiki/ANSI_C), there exists a function called `atexit` whose purpose is to (no surprise) run the given function at program exit. So, if we simply set an exit trap using `atexit` from `DllMain`, then when the program exits, we can escape the fiery blaze of Loader Lock:

```c
// DllMain boilerplate code (required in every DLL)
BOOL WINAPI DllMain(HINSTANCE hinstDll, DWORD fdwReason, LPVOID lpvReserved)
{
    switch (fdwReason)
    {
    case DLL_PROCESS_ATTACH:
        // CustomPayloadFunction will be called at program exit
        atexit(CustomPayloadFunction);
    }

    return TRUE;
}
```

So, we get to `CustomPayloadFunction` (shown as `payload` here), and after hours of debugging and head scratching, what we find next may shock you:

[![](https://elliotonsecurity.com/perfect-dll-hijacking/dll-atexit-handler-runs-under-loader-lock.png)](https://elliotonsecurity.com/perfect-dll-hijacking/dll-atexit-handler-runs-under-loader-lock.png)

**The `atexit` handler is also run under Loader Lock!! -\_-**

Coming to this realization took quite some work, too, as I needed a straightforward way to check whether Loader Lock was present. The only (poor) method I had for checking the presence of Loader Lock at that point was doing things that I figured must be impossible under Loader Lock. If those things succeeded, I assumed we must be free of Loader Lock (hint: this did not work).

That was until stumbling upon this **super helpful tidbit of information** on the Old New Thing blog by Raymond Chen (a veteran Windows internals expert at Microsoft): **[`!critsec ntdll!LdrpLoaderLock`](https://devblogs.microsoft.com/oldnewthing/20140808-00/?p=293)**

Considering Loader Lock problems are quite common in Windows API (Win32) programming, I think this information should be prominently available in the official Microsoft documentation (perhaps in a "Debugging" section) instead of only existing on a couple old blog posts, scattered across various issue trackers, and now here too. It's also worth noting that this lock was nowhere to be found in the output of `!locks -v`. That command lists some locks, but for whatever reason, `ntdll!LdrpLoaderLock` (even when locked) isn't included. So, there was no easy way of finding this out without scouring the Internet, searching debug symbol names, or setting breakpoints on NTDLL critical section functions (although I was unaware of how Loader Lock was implemented then).

```
0:000> !locks -v

CritSec ntdll!RtlpProcessHeapsListLock+0 at 00007ff94e17ace0
LockCount          NOT LOCKED
RecursionCount     0
OwningThread       0
EntryCount         0
ContentionCount    0

CritSec +13d202c0 at 0000024a13d202c0
LockCount          NOT LOCKED
RecursionCount     0
OwningThread       0
EntryCount         0
ContentionCount    0

... *snip* More unnamed (i.e. no debug symbols available or dynamically allocated) locks *snip* ...

CritSec SHELL32!g_lockObject+0 at 00007ff94d3684b0
LockCount          NOT LOCKED
RecursionCount     0
OwningThread       0
EntryCount         0
ContentionCount    0
```

In any case, with this fabulous `!critsec ntdll!LdrpLoaderLock` WinDbg command, we can instantly know whether or not Loader Lock is `*** Locked` or `NOT LOCKED` and in this case it was most certainly locked:

```
0:000> !critsec ntdll!LdrpLoaderLock

CritSec ntdll!LdrpLoaderLock+0 at 00007ffb30af65c8
WaiterWoken        No
LockCount          0
RecursionCount     1
OwningThread       26e0
EntryCount         0
ContentionCount    0
*** Locked
```

**So, I guess this technique just isn't viable, oh well, we tried...**

**Or is it?** What if I told you that (on Windows) there are, in fact **two** types of `atexit` (an **undocumented implementation detail**)! Well, that's exactly what I found out through a bit of reverse engineering. And the best part? The handler for one of them does **not** run under Loader Lock:

[![](https://elliotonsecurity.com/perfect-dll-hijacking/atexit-onexit-disassembly.png)](https://elliotonsecurity.com/perfect-dll-hijacking/atexit-onexit-disassembly.png)

_`_onexit` is a Microsoft extension which standard C `atexit` passes directly through to; these functions are equivalent_

Notice the two `call` instructions in the `_onexit` function. The first is to `_crt_atexit` (CRT is the C runtime), and the second is to `_register_onexit_function`. Which one is called depends on a `cmp` (compare) followed by a `jne` (jump if not equal) instruction. Specifically, if address `0x00007ff943783058 != 0xFFFFFFFFFFFFFFFF`, then we will jump to the call for `_register_onexit_function`, otherwise, `_crt_atexit` will be called.

Through experimentation, I learned that all this is testing for is if the call to `atexit`/`_onexit` was from an EXE or a DLL. If run from an EXE, the value at that address will be equal to `0xFFFFFFFFFFFFFFFF`, while in a DLL it's some other value. Why this is - I don't really know, but, it just is.

So, we've established that `atexit`/`_onexit` calls `_register_onexit_function` from a DLL, whereas `_crt_atexit` will be called from an EXE. You may have already guessed by now, but the one that we want to call - the one whose handler runs sans Loader Lock - is `_crt_atexit`!

![Information alert](https://elliotonsecurity.com/assets/images/alert-icons/circle-info-solid.svg)CRT Refresher

The C runtime (CRT) provides many basic application facilities, it's what gives programmers access to functions defined by the C (and sometimes C++) standard. Memory allocations functions like `malloc` and `free`, string comparison with `strcmp`, file access operations with `fopen`/`fread`/`fwrite`, and much more are all standard C functions! Complying by this standard, a developer can (in theory) write one C/C++ program that works across all platforms at no extra cost.

Let's get down to code and do it:

```c
#include <process.h> // For CRT atexit functions

// DllMain boilerplate code (required in every DLL)
BOOL WINAPI DllMain(HINSTANCE hinstDll, DWORD fdwReason, LPVOID lpvReserved)
{
    switch (fdwReason)
    {
    case DLL_PROCESS_ATTACH:
        // CustomPayloadFunction will be called at program exit
        // Note: These call the ucrtbase!_crt_atexit and ucrtbase!_crt_at_quick_exit functions
        _crt_atexit(CustomPayloadFunction);
        _crt_at_quick_exit(CustomPayloadFunction);
    }

    return TRUE;
}
```

**Try it out on `OfflineScannerShell.exe` and... it doesn't work.** But wait, it **does work** on a simple test bench I have set up where I'm building (using Visual Studio) both a sample target EXE and hijacking DLL (loading statically at process startup)?

Here's what the call stack looks like when the `atexit`/`_onexit` handler made by calling `_crt_atexit` is run on program exit in our test bench, also proving that **Loader Lock is no more**:

[![](https://elliotonsecurity.com/perfect-dll-hijacking/crt-atexit-handler-runs-without-loader-lock.png)](https://elliotonsecurity.com/perfect-dll-hijacking/crt-atexit-handler-runs-without-loader-lock.png)

_`ConsoleApplication2` is our sample target EXE and `Dll2` is our sample hijacking DLL_

I already had a suspicion, and this quick look in WinDbg pointed me in the right direction. The problem is that `OfflineScannerShell.exe` and our hijacking DLL are linked to entirely different CRTs which do not share the same state. `OfflineScannerShell.exe` is linked with the OG `msvcrt.dll` (this thing has backwards compatibility in Windows for ages), and our DLL is linked to the newer Universal CRT (the UCRT at `C:\Windows\System32\ucrtbase.dll`) only made available as a built-in system library starting with Windows 10. This is on Visual Studio 2022. However, note that older versions of Visual Studio may still link to the Visual C++ (`vcruntime`) CRT without a [UCRT base](https://learn.microsoft.com/en-us/cpp/porting/upgrade-your-code-to-the-universal-crt) (MinGW compilation allows full reliance on the UCRT during dynamic linking). You might be familiar with programs installing their own Visual C++ Redistributable runtimes:

[![](https://elliotonsecurity.com/perfect-dll-hijacking/visual-c++-redistributable-installer.png)](https://elliotonsecurity.com/perfect-dll-hijacking/visual-c++-redistributable-installer.png)

[![](https://elliotonsecurity.com/perfect-dll-hijacking/visual-c++-redistributable-installed.png)](https://elliotonsecurity.com/perfect-dll-hijacking/visual-c++-redistributable-installed.png)

**`msvcrt.dll` is the oldest C runtime in Windows. It's existed as a built-in system library since Windows 95 and still exists in the `C:\Windows\System32` of modern Windows installations.** It provides a terribly broken, in terms of compliance to the C standard, C runtime. It's so broken, in fact, that Microsoft removed developers' ability to link to it using Visual Studio long ago. However, Microsoft understands their own bugs and, as a result, still links to it for many programs that ship with Windows (unless it's a pure Win32 application without a CRT or possibly uses the newer UCRT released with Windows 10). All this is in line with Microsoft's uncontested reputation as the king of backward compatibility. That's the jist of it. Check out the [full backstory](https://stackoverflow.com/a/36189986) at your own risk.

Back to working out of `DllMain`, using the standard `GetModuleHandle`/`GetProcAddress` method to locate and call the `atexit` in `msvcrt.dll` works:

```c
msvcrtHandle = GetModuleHandle(L"msvcrt");
if (msvcrtHandle == NULL)
    return;
FARPROC msvcrtAtexitAddress = GetProcAddress(msvcrtHandle, "atexit");

// Prototype function with one argument
// Argument: A function pointer (CustomPayloadFunction) whose return type is irrelevant (`void`) and has no arguments (another `void`)
// Both of these functions use the standard C calling convention known as "cdecl"
typedef int(__cdecl* msvcrtAtexitType)(void (__cdecl*)(void));

// Cast msvcrtAtexitAddress as a type of msvcrtAtexitType so we can call it as prototyped above
msvcrtAtexitType msvcrtAtexit = (msvcrtAtexitType)(msvcrtAtexitAddress);

// Call MSVCRT atexit!
msvcrtAtexit(CustomPayloadFunction);
```

However, it's quite long and anti-malware solutions tend not to like these functions. Can we come up with something more succinct? Why yes, but we will have to switch out of Visual Studio and compile with a specific version of the Windows Driver Kit (WDK). Using WDK (which, despite its name, can also compile regular user-mode programs), we can link **directly** to `msvcrt.dll`! Compiling with MinGW likely works, too. This turns the contents of our `DllMain` (after boilerplate) back into a single line of code:

```c
atexit(CustomPayloadFunction);
```

Now that is clean.

#### Detection Heuristics [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#detection-heuristics-1)

Due to only containing a single line of code, this technique doesn't leave much in the way of detection. `atexit` works entirely intra-process, meaning kernel callbacks won't find anything. I'm also not immediately aware of any security product hooking user-mode calls for anything outside of `ntdll.dll`/`kernel32.dll` (or at least certainly not CRT DLLs). User-mode hooks exist in a program's (virtual) memory, which makes bypassing them always possible. This is unlike kernel callbacks, where a user-mode program has no privileges to touch the kernel (that's a hard security boundary which would require a privilege escalation exploit). So, this technique is evasive as far as common run-time indicators go.

Doing static analysis to detect calling `atexit` (or `_onexit`) inside of `DllMain` could work at first. However, it would only start a cat-and-mouse game and be trivially easy to bypass. For example, an attacker could call to `atexit` anywhere in their DLL code (outside of `DllMain`, in unused code), emit a unique identifier in the code (e.g. using `db` assembly instructions), then use an **egg hunter** (typically used in exploit development but could also be used to evade detection in this context) to search for that identifier with the address to `atexit` right after it. A tiny bit of assembly to dynamically `call` that address, probably stored in a register (e.g. `call rax`), is all it would take then.

Of course, there's nothing suspicious about `atexit` (e.g. in the Import Address Table of a binary) on its own, unlike `CreateRemoteThread` as an obvious counter-example.

A heuristic could be created that detects if a process is spending an abnormally long time in `atexit` handlers. Let's call it a bonus if the heuristic detects a benign application spending an exorbitant amount of time in `atexit` handlers as that sounds like it would probably be a bug to me. This could be combined with detecting entries in the CRT `_onexit_table_t` table pointing to DLL code. In particular, if sensitive Win32 functions are used (detect this with kernel callbacks) during execution of the DLL's `atexit` handler.

**An interesting realization is that `atexit` could be used as a _natural_ method for ensuring an attacker's real payload is never executed under a malware analysis sandbox** _if_ the sandbox isn't running the sample DLL in a program (EXE) linked with the same CRT as the DLL's target program (e.g. MSVCRT for `OfflineScannerShell.exe`). Malware analyis services like [Hybrid Analysis](https://www.hybrid-analysis.com/) should **ensure DLL samples are run in at least both UCRT and MSVCRT environments to catch this sandbox evasion trick.**

While one could further improve identification of this particular technique, I think that effort would be better spent detecting the broader class of DLL hijacking, which we will discuss later.

#### Approved by Microsoft®? [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#approved-by-microsoft-r)

By setting a breakpoint on `msvcrt!atexit`, I've been able to spot one occurrence of Microsoft themselves calling the same CRT `atexit` typically used by EXEs under Loader Lock:

[![](https://elliotonsecurity.com/perfect-dll-hijacking/microsoft-calls-crt-atexit-under-loader-lock.png)](https://elliotonsecurity.com/perfect-dll-hijacking/microsoft-calls-crt-atexit-under-loader-lock.png)

So there you have it, it's essentially...

![Success alert](https://elliotonsecurity.com/assets/images/alert-icons/badge-check.svg)Microsoft Approved

We're already doing this in production. 😎

Alright, alright, while Loader Lock is present here, there's still the clear difference between calling the CRT `atexit` from the CRT DLL code versus any other DLL calling it. Someone could call `FreeLibrary` on our DLL, causing our `atexit` handler to vanish from memory while it's still referenced by the CRT. This dangling pointer would then cause a crash on exit.

However, this is a more minor problem than one may think. It turns out that, for DLLs loaded statically (at least at process startup), `FreeLibrary` won't decrement the library's reference count thereby ensuring our DLL is never unloaded from memory, even if explicitly freed many times (confirmed in testing). In the dynamic loading case (`LoadLibrary`), we can call `LdrAddRefDll` (an NTDLL export) to increment the reference count on our DLL because the loader will never unload a library if its reference count is non-zero. All in all, as long as you throw in a `LdrAddRefDll` (and your EXE is linked with the correct CRT; otherwise, there will simply be no effect), this technique is guaranteed to be **100% safe™**.

### Unlocking Loader Lock [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#unlocking-loader-lock)

Okay, all this is great. But what if we want to run our final payload _straight_ from `DllMain`? Not deferring it to later, I'm talking about unlocking the loader while still in `DllMain`. At which point, we can do everything we want to do, with `DllMain` still in the call stack if we want it to be. Well, it took a small feat in reverse engineering the Windows loader (contained within `ntdll.dll`), but after some hours in WinDbg I figured it out.

From research done in our previous technique, we already know that if we want to change the status of Loader Lock, we will have to modify the critical section at `ntdll!LdrpLoaderLock`. But we can't do that without knowing the location of the `ntdll!LdrpLoaderLock` symbol, which we won't know outside our debugger (where Microsoft's debug symbols are automatically downloaded). Technically, it's possible to download debug symbols for the current Microsoft binary files ahead of time, have our process load them, and then look up their locations in our process. However, that's complex and not a tenable solution to me.

Searching the Internet about the Loader Lock critical section, I came across the ReactOS source code for a promising function called [LdrUnlockLoaderLock](https://doxygen.reactos.org/d7/d55/ldrapi_8c.html#a62b7a5edb61dfa0876b4e928cf510922). ReactOS is an open source reimplementation of Windows built from the ground up by reverse engineering Microsoft Windows - so it goes without saying that their work is invaluable.

Checking with `dumpbin.exe /exports C:\Windows\System32\ntdll.dll` (`dumpbin.exe` is a tool installed with Visual Studio), I was able to confirm that `LdrUnlockLoaderLock` is an export of `ntdll.dll` which means we could easily get its location via dynamic linking or `GetProcAddress` then presumably call it to unlock the loader!

Taking a look at the function signature for `LdrUnlockLoaderLock` from the ReactOS source code, it seems to take a `Cookie` parameter:

```c
// NOTE: I have since fixed a bug in ReactOS where the cookie value was origianlly of type ULONG; not ULONG_PTR
// https://github.com/reactos/reactos/pull/6188
// This article has been updated to reflect this fix.
NTSTATUS NTAPI LdrUnlockLoaderLock ( IN ULONG Flags,
                                     IN ULONG_PTR Cookie OPTIONAL
    )
```

And if we don't provide a `Cookie`, then it returns early:

```c
/* If we don't have a cookie, just return */
if (!Cookie) return STATUS_SUCCESS;
```

The `Cookie` (just a magic number that isn't stored) is calculated based on the thread ID (as retrieved by `GetCurrentThreadId` or directly from the TEB), which means we could, in theory, easily create a valid cookie value ourselves...

Interestingly, setting a breakpoint on `LdrUnlockLoaderLock` reveals that it was never called throughout the execution of our target application. Whereas looking into ReactOS code shows that their loader calls `LdrUnlockLoaderLock` calls this function quite frequently. At the time of writing, ReactOS targets Windows Server 2003 (also supporting pieces of Windows 7+ API). So, it makes sense that the loader's inner workings have significantly changed between then and newer versions of Windows. I was going to do the work to calculate these cookie values (the formula appears to have also changed since ReactOS), but by that point I had already almost finished work on another method of retrieving loader lock by searching assembly code, so we will leave reversing the exact formula for another time.

Looking to the modern `LdrUnlockLoaderLock` function shows that it internally calls a little function named: **`LdrpReleaseLoaderLock`**

One look at the code for this guy, and I have a feeling we're going to get along just fine!

```asm
lea     rcx, [ntdll!LdrpLoaderLock (7ff94e1765c8)]
call    ntdll!RtlLeaveCriticalSection (7ff94e03f230)
```

`LdrpReleaseLoaderLock` isn't exported by NTDLL, though, so to get at it, we will search the disassembly of an exported function which is known to call `LdrpReleaseLoaderLock` and then extract its address from there. Using the [\# WinDbg command](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/---search-for-disassembly-pattern-) we can search for patterns in NTDLL's disassembly:

```
0:000> # "call    ntdll!LdrpReleaseLoaderLock" <NTDLL_ADDRESS> L9999999
ntdll!LdrpDecrementModuleLoadCountEx+0x79:
00007ff9'4e01fd11 e84ee90200      call    ntdll!LdrpReleaseLoaderLock (00007ff9'4e04e664)
ntdll!LdrShutdownThread+0x201:
00007ff9'4e027651 e80e700200      call    ntdll!LdrpReleaseLoaderLock (00007ff9'4e04e664)
ntdll!LdrpInitializeThread+0x213:
00007ff9'4e02794 b e8146d0200      call    ntdll!LdrpReleaseLoaderLock (00007ff9'4e04e664)
ntdll!LdrpPrepareModuleForExecution+0xc9:
00007ff9'4e04d951 e80e0d0000      call    ntdll!LdrpReleaseLoaderLock (00007ff9'4e04e664)
ntdll!LdrEnumerateLoadedModules+0x85:
00007ff9`4e06d955 e80a0dfeff      call    ntdll!LdrpReleaseLoaderLock (00007ff9`4e04e664)
ntdll!LdrUnlockLoaderLock+0x63:
00007ff9`4e08e023 e83c06fcff      call    ntdll!LdrpReleaseLoaderLock (00007ff9`4e04e664)
ntdll!LdrUnlockLoaderLock+0x71:
00007ff9`4e08e031 e82e06fcff      call    ntdll!LdrpReleaseLoaderLock (00007ff9`4e04e664)
ntdll!LdrShutdownThread$fin$2+0x10:
00007ff9'4e0b4ac7 e8989bf9ff      call    ntdll!LdrpReleaseLoaderLock (00007ff9'4e04e664)
ntdll!LdrpInitializeThread$fin$2+0x10:
00007ff9'4e0b4b2f e8309bf9ff      call    ntdll!LdrpReleaseLoaderLock (00007ff9'4e04e664)
ntdll!LdrEnumerateLoadedModules$fin$0+0x10:
00007ff9'4e0b59f5 e86a8cf9ff      call    ntdll!LdrpReleaseLoaderLock (00007ff9'4e04e664)
ntdll!RtlExitUserProcess+0x5f3c1:
00007ff9'4e0ccda1 e8be18f8ff      call    ntdll!LdrpReleaseLoaderLock (00007ff9'4e04e664)
ntdll!LdrpInitializeImportRedirection+0x46d72:
00007ff9'4e0d8976 e8e95cf7ff      call    ntdll!LdrpReleaseLoaderLock (00007ff9'4e04e664)
ntdll!LdrInitShimEngineDynamic+0xde:
00007ff9`4e0e068e e8d1dff6ff      call    ntdll!LdrpReleaseLoaderLock (00007ff9`4e04e664)
ntdll!LdrpInitializeProcess+0x1f6e:
00007ff9'4e0e3e2e e831a8f6ff      call    ntdll!LdrpReleaseLoaderLock (00007ff9'4e04e664)
ntdll!LdrpCompleteProcessCloning+0x93:
00007ff9`4e0e4bfb e8649af6ff      call    ntdll!LdrpReleaseLoaderLock (00007ff9`4e04e664)
```

As you can see, there are many potential jumping-off points to locate `ntdll!LdrpReleaseLoaderLock` from. However, we already know `ntdll!LdrUnlockLoaderLock` is exported, and it seems like the most straightforward approach, so we will search from there. The code for this is nothing special; it just searches for the correct call opcode, performs some extra validation, extracts the (rel32 encoded) address proceeding the `call` instruction, and then prototypes the `LdrpReleaseLoaderLock` function so we can call it. I took the further step of extracting the address of the `ntdll!LdrpLoaderLock` critical section from `LdrpReleaseLoaderLock` so we can also re-lock it (using `EnterCriticalSection`) before returning from `DllMain` to ensure safety. Now in `DllMain`, we check and...

```
0:000> !critsec ntdll!LdrpLoaderLock

CritSec ntdll!LdrpLoaderLock+0 at 00007ff94e1765c8
LockCount          NOT LOCKED
RecursionCount     0
OwningThread       0
EntryCount         0
ContentionCount    0
```

Now that we've unlocked Loader Lock from `DllMain`, let's bravely call `ShellExecute` opening `calc`! Anddd.. it doesn't work - yet. But, we've made valuable progress! Recall from the [Our Payload](https://elliotonsecurity.com/perfect-dll-hijacking/#our-payload) section that we were originally deadlocking in `ntdll!NtAlpcSendWaitReceivePort`:

[![](https://elliotonsecurity.com/perfect-dll-hijacking/shellexecute-initial-deadlock-point-stack-trace.png)](https://elliotonsecurity.com/perfect-dll-hijacking/shellexecute-initial-deadlock-point-stack-trace.png)

With Loader Lock released, we now surpass this point! Leading us to our next obstacle:

[![](https://elliotonsecurity.com/perfect-dll-hijacking/shellexecute-deadlock-main-thread-creates-new-thread.png)](https://elliotonsecurity.com/perfect-dll-hijacking/shellexecute-deadlock-main-thread-creates-new-thread.png)

[![](https://elliotonsecurity.com/perfect-dll-hijacking/shellexecute-deadlock-new-thread-loader.png)](https://elliotonsecurity.com/perfect-dll-hijacking/shellexecute-deadlock-new-thread-loader.png)

Remember how `ShellExecute` spawns a new thread? Well, that thread got spawned successfully, but its starting up is inteacting with the library loader thus creating contention on some resources.

Solving this was primarily a trial-and-error task along with some tracing back of the assembly code; every time the program hung, I did something that let it go a little bit further, then rinse and repeat.

For spawning a new thread, though, it essentially comes down to two things:

- Win32 Events
  - Use [SetEvent](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-setevent) to signal them
  - If they're not signalled, then the new thread will hang on them forever with `NtWaitForSingleObject`
- The loader work in progress state: `ntdll!LdrpWorkInProgress`
  - This is not a critical section or event; just a 1 or 0 in `ntdll.dll`'s memory
  - This appears to be some loader state in NTDLL's memory

We can list all Win32 Events in WinDbg with this command:

```
0:000> !handle 0 8 Event
Handle 4
  Object Specific Information
    Event Type Manual Reset
    Event is Waiting
Handle c
  Object Specific Information
    Event Type Auto Reset
    Event is Waiting
Handle 3c
  Object Specific Information
    Event Type Auto Reset
    Event is Set
Handle 40
  Object Specific Information
    Event Type Auto Reset
    Event is Waiting
Handle b0
  Object Specific Information
    Event Type Auto Reset
    Event is Waiting
... *snip* More events *snip* ...
13 handles of type Event
```

We set the necessary events (these identifiers appear to never change)...

```c
SetEvent((HANDLE)0x40);
SetEvent((HANDLE)0x4);
```

Preload the libraries `ShellExecute` loads in the current thread before spawning its own new thread (we will talk about this)...

```c
LoadLibrary(L"SHCORE");
LoadLibrary(L"msvcrt");
LoadLibrary(L"combase");
LoadLibrary(L"RPCRT4");
LoadLibrary(L"bcryptPrimitives");
LoadLibrary(L"shlwapi");
LoadLibrary(L"windows.storage.dll"); // Need DLL extension for this one because it contains a dot in the name
LoadLibrary(L"Wldp");
LoadLibrary(L"advapi32");
LoadLibrary(L"sechost");
```

Locate and flip the `ntdll!LdrpWorkInProgress` status so loader work can occur in the new thread spawned by `ShellExecute`...

```c
PBOOL LdrpWorkInProgress = getLdrpWorkInProgressAddress();
*LdrpWorkInProgress = FALSE;
```

Like `ntdll!LdrpLoaderLock`, we use an NTDLL exported function, in this case `RtlExitUserProcess`, as a jumping-off point to locate `ntdll!LdrpWorkInProgress`.

We go for a `ShellExecute`...

#### Mission Accomplished! [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#mission-accomplished)

**AND IT WORKS!** Our `calc` pops (all threads launched by `ShellExecute` work successfully; it turns out `ShellExecute` spawns more threads), then we clean up before returning from `DllMain` to avoid crashing/deadlocking later. I've confirmed by manually stepping through `OfflineScannerShell.exe` that our target works perfectly fine until its natural end with an exit code of 0 (success)!

Here's the high-level overview for fully unlocking the library loader as we have implemented in code:

```c
#define RUN_PAYLOAD_DIRECTLY_FROM_DLLMAIN

VOID LdrFullUnlock(VOID) {
    // Fully unlock the Windows library loader

    //
    // Initialization
    //

    const PCRITICAL_SECTION LdrpLoaderLock = getLdrpLoaderLockAddress();
    const HANDLE events[] = {(HANDLE)0x4, (HANDLE)0x40};
    const SIZE_T eventsCount = sizeof(events) / sizeof(events[0]);
    const PBOOL LdrpWorkInProgress = getLdrpWorkInProgressAddress();

    //
    // Preparation
    //

    LeaveCriticalSection(LdrpLoaderLock);
    // Preparation steps past this point are necessary if you will be creating new threads
    // And other scenarios, generally I notice it's necessary whenever a payload indirectly calls: __delayLoadHelper2
#ifdef RUN_PAYLOAD_DIRECTLY_FROM_DLLMAIN
    preloadLibrariesForCurrentThread();
#endif
    modifyLdrEvents(TRUE, events, eventsCount);
    // This is so we don't hang in ntdll!ldrpDrainWorkQueue of the new thread (launched by ShellExecute) when it's loading more libraries
    // ntdll!LdrpWorkInProgress must be TRUE while libraries are being loaded in the current thread
    // ntdll!LdrpWorkInProgress must be FALSE while libraries are loading in the newly spawned thread
    // For this reason, we must preload the libraries ShellExecute will load in the current thread before spawning a new thread
    *LdrpWorkInProgress = FALSE;

    //
    // Run our payload!
    //

#ifdef RUN_PAYLOAD_DIRECTLY_FROM_DLLMAIN
    // Libraries loaded by API call(s) on the current thread must be preloaded
    payload();
#else
    DWORD payloadThreadId;
    HANDLE payloadThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)payload, NULL, 0, &payloadThreadId);
    if (payloadThread)
        WaitForSingleObject(payloadThread, INFINITE);
#endif

    //
    // Cleanup
    //

    // Must set ntdll!LdrpWorkInProgress back to TRUE otherwise we crash/deadlock in NTDLL library loader code sometime after returning from DllMain
    // The crash/deadlock occurs to due to concurrent operations happening in other threads
    // The problem arises due to ntdll!TppWorkerThread threads by default (https://devblogs.microsoft.com/oldnewthing/20191115-00/?p=103102)
    *LdrpWorkInProgress = TRUE;
    // Reset these events to how they were to be safe (although it doesn't appear to be necessary at least in our case)
    modifyLdrEvents(FALSE, events, eventsCount);
    // Reacquire loader lock to be safe (although it doesn't appear to be necessary at least in our case)
    // Don't use the ntdll!LdrLockLoaderLock function to do this because it has the side effect of increasing ntdll!LdrpLoaderLockAcquisitionCount which we probably don't want
    EnterCriticalSection(LdrpLoaderLock);
}
```

**After repeated testing, it's achieved an impressive 100% success rate! It works every time.**

There's still a bit more loader reverse engineering work to be done if we want to call `ShellExecute` (or other Windows API calls) without having to preload libraries for the current thread. To figure this out, I recommend setting breakpoints on functions `NtSetEvent`, `NtResetEvent`, `RtlEnterCriticalSection`, `RtlLeaveCriticalSection` and `NtWaitForSingleObject`. Setting read/write watchpoints and searching (with the `#` command as we did before) NTDLL's disassembly for references to loader state variables like `ntdll!LdrpWorkInProgress` would probably help, too. Basically, finding some piece of NTDLL state you can set before calling `ShellExecute` that will trigger `ntdll!LdrpWorkInProgress` to become `FALSE` on its own in the first thread launched by `ShellExecute`. That's one theory on what needs to happen, but it's most likely more subtle than that (involving some overlooked control flow; possibly touching `ntdll!LdrpWorkInProgress` won't even be necessary then). There must be a way to do it. However, it would take some looking into. Feel free to take a shot at this yourself!

Alternatively, we can work around this minor inconvenience entirely by setting `ntdll!LdrpWorkInProgress` to `FALSE`, calling `CreateThread` (this never loads additional libraries), waiting on the new thread from `DllMain` with `WaitForSingleObject(payloadThread, INFINITE)`, then calling `ShellExecute` (or any payload we want) from our new thread - no "library preloading" required. This workaround is what I recommend for utilizing this technique in practice. However, in this demonstration, I wanted to fulfill precisely what I set out to do by running `ShellExecute` _directly_ from `DllMain`!

To verify that our `ShellExecute` litmus test holds up in reality, I also tried performing a number of other complex operations from `DllMain` (`RUN_PAYLOAD_DIRECTLY_FROM_DLLMAIN` undefined) that failed prior to unlocking the loader. This includes successfully downloading a file using WinHTTP; a notable improvement over first deadlocking when we call `WinHttpOpen` because `WINHTTP_DLL::Startup` internally calls into `__delayLoadHelper2` to load `ws2_32.dll`. **Everything I've attempted thus far has worked flawlessly!** **Update from the future:** Actually dummy, the reason you are getting this specific deadlock in the `ntdll!LdrpDrainWorkQueue` function was because you were accidentally messing with the loader internals (specifically resetting the `ntdll!LdrpWorkCompleteEvent`, which at the time you were completely confused on the function of because you kept messing with the loader's locks/state leading to outcomes that would not usually occur) while running this test. However, you were right that [WinHTTP from `DllMain` can deadlock you](https://github.com/ElliotKillick/operating-system-design-review/tree/main/windows/winhttp-dllmain-debugging.log) (just not in the way you described) and that Windows delay loading is not a good thing.

#### Safety! [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#safety)

Safety, safety, safety, calling `ShellExecute` from `DllMain` safety, okay, let's talk about safety! The most obvious unsafe thing being done in this technique is directly interacting with NTDLL at all. In Windows, anything in NTDLL is subject to change across Windows versions. Microsoft exposes many NTDLL functions through a stable KERNEL32 API which can be depended on to stay the same. With that said, I tried to target parts of NTDLL that have probably remained largely untouched to decrease the chance of breakage occurring in this way. For example, I used straightforward and smaller NTDLL exports like `LdrUnlockLoaderLock` and `RtlExitUserProcess` as jumping-off points for locating some of the NTDLL internals we need to make this work.

Let's assume the implementation details we depend on are mature, making them likely to stay the same. Also, that we already have the addresses for the NTDLL internals we need (maybe we can lookup debug symbols in our process). How safe is it then?

Some technical Windows experts might say that how we use the loader's internal synchronization mechanisms violates a lock hierarchy. Therefore, even if it never becomes an issue in our process alone, some remote process could legally spawn a thread into our process and do some unspecified concurrent operations with the loader, thus causing a deadlock/crash. I've maintained the loader's lock hierarchy as best I can, given that we don't have access to any internal Microsoft documentation. To keep in line with our goal of **respecting the lock hierarchy**, we avoid lock order inversion issues by locking back up in the same order that the loader presumably locks in (this is also implemented for events in `modifyLdrEvents`).

For instance, one well-known case where the NT kernel will spawn a thread into your process is for handling `Ctrl+C` events. However, that can only happen on console subsystem programs whereas `OfflineScannerShell.exe` is a Windows subsystem (GUI) program.

At best, what we're doing is [priority inversion](https://en.wikipedia.org/wiki/Priority_inversion), which, while not being a good practice from a performance point of view due to causing a high-priority task to wait for a lower-priority task, is still not a deadlock/crash. At worst, we are violating a lock hierarchy or leaving the loader in an inconsistent state, which means bad things _could_ happen.

If you're writing a real production application, then it goes without saying: don't try this at home. The point of this research is only to prove that fully unlocking the loader is _technically_ possible (and on top of that, it's pretty epic). If you deploy this Loader Lock Rube Goldberg machine in production to millions of users, that's on you! Then again, technically possible is the best kind of possible. ;)

[![](https://elliotonsecurity.com/perfect-dll-hijacking/technically-correct-meme.jpg)](https://elliotonsecurity.com/perfect-dll-hijacking/technically-correct-meme.jpg)

Really, though, if you're a developer writing production-grade software, don't do this - please. Even if you believe it's stable enough for you and don't wish to heed Microsoft's guidelines, searching assembly code to locate NTDLL internals in the same way will fail on non-Microsoft implementations of Windows. Also, the Wine and ReactOS loaders (based mostly on reverse engineered Windows Server 2003 code) looks nothing like the modern Windows 10 loader, so crashes due to significant changes in the implementation are inevitable.

As a side note, Wine's implementation of the `LdrUnlockLoaderLock` [Native API](https://en.wikipedia.org/wiki/Windows_Native_API) function (at `dlls/ntdll/loader.c` in the Wine source tree) looks like this:

```c
NTSTATUS WINAPI LdrUnlockLoaderLock( ULONG flags, ULONG_PTR magic )
{
    if (magic)
    {
        if (magic != GetCurrentThreadId()) return STATUS_INVALID_PARAMETER_2;
        RtlLeaveCriticalSection( &loader_section );
    }
    return STATUS_SUCCESS;
}
```

Incredibly simple and without the unnecessary calculations based around the thread ID to create a `Cookie`/`magic` value. So, at least on free implementations of Windows, it's straightforward to release the Loader Lock without any bloat. Note that the `flags` parameter, used for controlling whether an error should be returned or raised as an exception, is currently unimplemented on Wine. This is an outstanding beginner-friendly contribution for anyone interested in helping out with Wine!

## Is Loader Lock Only Problematic on Windows? [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#is-loader-lock-only-problematic-on-windows)

**tl;dr yes.**

A module constructor is equivalent to `DllMain` on non-Windows platforms such as Mac & Linux (in addition to the functionality being accessible in a cross-platform manner through programming languages like C++, in which case I have confirmed Windows also runs thoseroutines under Loader Lock from `dllmain_dispatch` shortly before `DllMain` itself is). Like a library's `DllMain`, a module constructor is run when the library is loaded (for unloads, there is also the module destructor). On Linux with the GCC compiler, any function can be marked with `__attribute__((constructor))` to run at load-time just as `DllMain` is.

Just like Windows, Linux (using glibc), of course, also has a 'loader lock' (or mutex) that ensures safety from race conditions across threads (I've read the source code).

So, _why then_ if you search on Google for issues related to the respective loader locks do you only get problems arising on the Windows side of things. And _why then_ does only Microsoft, and not GNU, have this very long list of things you should not do while under loader lock. These issues just don't happen on Unix-like operating systems!

Investigating the architectural differences surrounding the Windows and Linux (glibc) loaders is what I intend to do in another article (this one has gone on long enough).

![Information alert](https://elliotonsecurity.com/assets/images/alert-icons/circle-info-solid.svg)Technicality Nitpick

In Windows, a "mutex" refers to an inter-process lock whereas a critical section refers to an intra-process lock. However, these terms are used generically and interchangeably throughout this article.

Also, know that my background is mostly in Unix-like operating systems, so, if something I said regarding Windows isn't precisely correct then my bad.

## Mitigation & Detection [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#mitigation-detection)

**Preventing a lookalike DLL from being loaded in the first place will always be our most robust guard against DLL hijacking.** For once an attacker has code running on the system, we can only implement reactive measures, at which point, it's virtually always game over from an academic point of view (i.e. it turns into an infinite cat-and-mouse game).

Luckily, there is one surefire method of detecting DLL hijacking of statically loaded libraries built into Windows. Check the exports of the DLL in question, looking for symbol names that are duplicates of the names present in signed Microsoft DLLs (e.g. shipped with Windows at least). If a DLL unsigned by Microsoft exports many of the same symbol names as a Microsoft-signed DLL, then there's a good chance its intention is to hijack. This works because the Windows library loader will bail out early (before executing any `DllMain`s) if it sees that a DLL is missing an export required by the EXE:

[![](https://elliotonsecurity.com/perfect-dll-hijacking/offlinescannershell-mpclient-dll-missing-export-error.png)](https://elliotonsecurity.com/perfect-dll-hijacking/offlinescannershell-mpclient-dll-missing-export-error.png)

This could be combined with other detection factors, like whether the DLL on disk also shares the same filename as the DLL it's duplicating exports from or whether it exists in the `PATH` global environment variable or current working directory (CWD) of the running program to form a robust heuristic for DLL hijacking at least of built-in libraries.

It's a good idea to keep an eye on user-writable directories in the `PATH` by default such as `C:\Users\<YOUR_USERNAME>\AppData\Local\Microsoft\WindowsApps` (as shown ealier). The same goes for the CWD if it's user-writable. This is especially true if `cmd.exe` or likewise is the parent process that CWD is being inherited from. **Libraries loaded from either the user-writable `PATH` or CWD (these come last in the search order) should always be put under extra scrutiny.** This also goes for a user-writable program directory if the program looks to have been copied from a _non_ user-writable location.

Checking exports doesn't work for dynamically loaded DLLs (loaded via `LoadLibrary`). Although, loading DLLs this way is much less common.

To protect against that, one could detect Microsoft programs loading DLLs that aren't signed by Microsoft. This mitigation, in fact, already exists in Windows! Here's how we can use the [Set-ProcessMitigation](https://learn.microsoft.com/en-us/powershell/module/processmitigations/set-processmitigation) PowerShell cmdlet to effectively patch our target `OfflineScannerShell.exe` against DLL hijacking:

```ps1
Set-ProcessMitigation -Enable MicrosoftSignedOnly -Name OfflineScannerShell.exe
```

**And now, when we try hijacking any program named `OfflineScannerShell.exe`, we will receive an error message notifying us that our non-Microsoft signed DLL has been blocked:**

[![](https://elliotonsecurity.com/perfect-dll-hijacking/offlinescannershell-mpclient-dll-unsigned-by-microsoft-error.png)](https://elliotonsecurity.com/perfect-dll-hijacking/offlinescannershell-mpclient-dll-unsigned-by-microsoft-error.png)

So, just throw that registry value into all the systems in your organization and just like that, you will have easily foiled any hijacking attempts against `OfflineScannerShell.exe`!!

## Wrapping Up [🔗](https://elliotonsecurity.com/perfect-dll-hijacking/\#wrapping-up)

We have successfully innovated on previous research to uncover some novel clean & universal DLL hijacking techniques! We also learned a good bit about concurrency, the Windows library loader, modern Windows internals, WinDbg, and demystified the inner workings of Loader Lock. With any luck, our discoveries and mitigation/detection work will help push the security industry forward!

In Windows alone, there are countless opportunities for code injection into **Microsoft signed** programs using DLL hijacking (made better using our new techniques). In fact, security expert Wietze Beukema (@Wietze) has already compiled a list including hundreds of these programs with his project **[HijackLibs](https://hijacklibs.net/)** ( **Sigma detections included**)!

Our new DLL hijacking methods are also helpful for simplifying privilege escalation exploits where a privileged application accidentally loads an attacker-controlled DLL. This can happen for a variety of reasons, such as when a privileged application is missing a DLL, potentially causing it to load from a user-writable path.

Apologies for not posting an article in two months. Going forward, I'm committed to publishing more shorter articles (still of the same quality) so I can share new content regularly. This article is about 9000 words long, so researching for then writing at most 1000 words per-article should get me there. More good stuff to come!

See the **complete, open source code** for everything we talked about here on the [LdrLockLiberator](https://github.com/ElliotKillick/LdrLockLiberator) GitHub repository!

Share on:

- [X / Twitter](https://twitter.com/intent/tweet?text=https://elliotonsecurity.com/perfect-dll-hijacking/ "Share on X/Twitter")
- [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://elliotonsecurity.com/perfect-dll-hijacking/ "Share on LinkedIn")
- [Hacker News](https://news.ycombinator.com/submitlink?u=https://elliotonsecurity.com/perfect-dll-hijacking/ "Share on Hacker News")
- [Reddit](https://www.reddit.com/submit?url=https://elliotonsecurity.com/perfect-dll-hijacking/ "Share on Reddit")

[dll hijacking](https://elliotonsecurity.com/categories/dll-hijacking/) [reverse engineering](https://elliotonsecurity.com/categories/reverse-engineering/) [adversary simulation](https://elliotonsecurity.com/categories/adversary-simulation/) [defense engineering](https://elliotonsecurity.com/categories/defense-engineering/) [security](https://elliotonsecurity.com/categories/security/) [#windows](https://elliotonsecurity.com/tags/windows/) [#technical](https://elliotonsecurity.com/tags/technical/)

[Explore Similar Content ➤](https://elliotonsecurity.com/)