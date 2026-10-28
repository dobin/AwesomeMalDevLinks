# https://trainsec.net/library/windows-internals/dll-injection-with-setwineventhook-the-accessibility-hook-as-an-injector/

[Skip to content](https://trainsec.net/library/windows-internals/dll-injection-with-setwineventhook-the-accessibility-hook-as-an-injector/#content)

# DLL Injection with SetWinEventHook: The Accessibility Hook as an Injector

- October 12, 2026

![Pavel Yosifovich](https://trainsec.net/wp-content/uploads/2026/09/pavel-yosifovich-animated.webp)

Author

[Pavel Yosifovich](https://trainsec.net/author/pavel-yosifovich/)

Pavel Yosifovich has 25+ years as Software developer, trainer, consultant, author, and speaker. Co-author of “Windows Internals”. Author of “Windows Kernel Programming”, “Windows 10 System Programming, as well as System and kernel programming courses and “Windows Internals” series.

Pavel Yosifovich, co-author of “Windows Internals 7th Edition, Part 1” and author of “Windows Native API Programming”, adds one more technique to a list that already has several entries: injecting a DLL into another process. You may have thought we were done with injection methods. We are not. This one rides on [`SetWinEventHook`](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwineventhook), an API that exists for accessibility, and it has the same quiet appeal as the **SetWindowsHookEx** hook: you never explicitly write a single byte into the target. You register for some UI events, hand Windows a DLL, and the infrastructure loads that DLL into the processes that raise those events. This post is for Windows systems programmers, malware analysts, and anyone who likes to understand a mechanism by watching it fail first and then fixing it.

![DLL Injection with SetWinEventHook](https://i.ytimg.com/vi/0LH1MySzPFc/hqdefault.jpg)

## What Injection Methods Came Before This One?

Before the new trick, a quick recap of what we have already covered, because it frames why this one is interesting. The most fundamental is [`CreateRemoteThread`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread), where you create a thread in the target whose start function is `LoadLibrary` and whose argument is the path to your DLL. Then there is [`QueueUserAPC`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc), which queues an APC that runs `LoadLibrary` the same way, once a thread in the target goes alertable. There is a newer [`QueueUserAPC2`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc2) built around a special user mode APC that does not need the thread to wait in an alertable state, which I have not demonstrated and leave as an exercise. There is [`SetWindowsHookEx`](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowshookexw), which is the closest cousin to today’s technique: you provide a hook function in a DLL and user32.dll does the injecting into every process on the desktop that has UI. And there is plain shellcode, which can do anything, so we used it only as one example among many.

The thing to notice is that the two hook-based methods, `SetWindowsHookEx` and the one in this video, never do anything intentional to write into the target. You supply a callback and the system takes care of the rest. The price is that they only work against processes that have UI and are connected to the same desktop as the calling thread.

## How Does SetWinEventHook Become an Injector?

`SetWinEventHook` is, officially, an accessibility API. It is a bit confusing because the name is so close to `SetWindowsHookEx`, and both are about UI events, but this one works at a higher level, the one screen readers and automation tools use. We are not here for accessibility. We are here because the API has the same shape as the window hook: register for events, and the callback can be marshaled back to your process, or run inside the context of whatever process raised the event. That second option is the DLL injection.

The call takes a range of events, a module handle for the DLL, a callback, a process ID and thread ID to scope it, and a set of flags. Since any single event is enough to get our DLL loaded, we ask for everything with `EVENT_MIN` and `EVENT_MAX` from the [event constants](https://learn.microsoft.com/en-us/windows/win32/winauto/event-constants). For scope, a process ID and thread ID of zero means every thread of every process we are allowed to reach, which is to say every UI process on the current desktop. You cannot point this at an arbitrary process of your choosing: processes in session 0, or processes with no UI, are off the table. Other than that, you can scope to one process, even one thread, or go wide with zero.

## Why Does Nothing Happen at First?

Here is where it gets practical, because the obvious first attempt does not work. Start simple: register for all events, pass NULL for the module so the callback stays in the current process, use the `WINEVENT_OUTOFCONTEXT` flag so events are marshaled back to you, and add `WINEVENT_SKIPOWNPROCESS` and `WINEVENT_SKIPOWNTHREAD` for good measure, since you rarely care about your own events. Write an `on_event` callback matching the [`WINEVENTPROC`](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nc-winuser-wineventproc) prototype, which is a mighty one, and print the parameters.

Run it and the process exits immediately, so of course no events arrive. Fine, keep it alive. The temptation is `sleep` forever, or some infinite loop. Do that and you still get nothing, not even when you open Notepad and bang on it. This is the kind of thing you only solve by reading the documentation carefully. These events arrive from other processes, and they have to be delivered somehow. The mechanism is the ordinary Windows message queue. So you need a message pump: [`GetMessage`](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getmessage) in a loop, then [`DispatchMessage`](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-dispatchmessage).

Put a breakpoint in the callback and you can watch the plumbing: `SetWinEventHook` created a hidden window, that window is the target for notifications from other processes, and `DispatchMessage` calls its window procedure, which calls your callback. Remove the breakpoint and events flood in, because a normal desktop has a lot of UI activity. With the accessibility API you could turn each event into a real object and ask its name and type, but that is a different topic.

## How Do You Turn Marshaling Into Real Injection?

So far there is no DLL and no injection, just events marshaled into our process. To make it real, three things change.

First, the module. It can no longer be NULL. You have to load the DLL you want to inject into your own process first, and that loaded module is the one the system then injects everywhere else. That feels backwards, but it is how the API works: load it once locally, and later you can even exit, because the DLL only needs to be loaded once to be available for injection. Loading it by a bare name depends on the current directory, which from the debugger is not what you want, so use [`GetModuleFileName`](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulefilenamew) to get the executable’s full path, strip the file name back to the last backslash with `wcsrchr`, append your DLL name, and call [`LoadLibrary`](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryw) on that. Now it loads from the executable directory regardless of the current directory.

Second, the callback moves into the DLL. It cannot live in the executable, because the executable is not what gets injected. The callback does not need to do anything useful, it does not even need a print. It only needs to exist, because the first time it is called the DLL is already loaded into the target, which was the whole point. You find its address in the loaded DLL with [`GetProcAddress`](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getprocaddress), and to keep the compiler happy you cast the result with `decltype` to a pointer to that monstrous `WINEVENTPROC` type.

Third, and this is the mistake I make on camera so you do not have to, **`GetProcAddress`** comes back NULL at first. The reason is that the callback in the DLL is just a function, and a function is not exported. You have to export it. You can use a DEF file, which I have done in other examples, or the shorter route: mark it `extern "C"` so the C++ name mangling does not turn the name into something unrecognizable, and [`__declspec(dllexport)`](https://learn.microsoft.com/en-us/cpp/cpp/dllexport-dllimport) so the linker actually exports it. Rebuild, and now `GetProcAddress` returns a real pointer.

## In-Context Versus Out-of-Context: The Flag That Actually Injects

With the DLL loaded, the callback exported, and the handle in hand, call `SetWinEventHook` and watch Process Explorer. Scope it to one Notepad by its process ID so you do not inject into half the system. The DLL should appear in the target’s module list. It does not. Open Notepad, nothing.

The reason is the flag. We are still passing `WINEVENT_OUTOFCONTEXT`, which means “marshal the events back to me,” and that never injects anything. What injects the DLL is `WINEVENT_INCONTEXT`, which tells the system to run the callback in the context of the process where the event occurred. Once you switch to in-context, the message pump is no longer strictly needed, since notifications run in the other process, not yours. You still have to keep your process alive at least until the first event injects the DLL, so a sleep is the simplest placeholder. Run it without the debugger, open Notepad, and now Process Explorer shows your DLL loaded in the target. That is the injection.

## How Do You Clean Up Properly?

The sleep is a placeholder. The cleaner design is to create an event object, let the injected DLL signal it once it is loaded, and have the injector wait on that event instead of sleeping. When the event is signaled, call [`UnhookWinEvent`](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-unhookwinevent) to tear down the hook. The DLL is already loaded in the target and stays there, so unhooking does not undo the injection. It just means you stop running your callback inside the target on every event. From an offensive standpoint that matters: a callback that keeps firing in the target burns time and leaves an obvious signal that something is afoot. If you want to stay quiet, inject once and unhook.

## What This Means Practically

- `SetWinEventHook` is an accessibility API, but with `WINEVENT_INCONTEXT` and a DLL module it becomes a DLL injector, and you never explicitly write into the target
- Like `SetWindowsHookEx`, it only reaches UI processes on the same desktop, so session 0 and non-UI processes are out
- `EVENT_MIN` to `EVENT_MAX` catches everything, and the first event is enough to get the DLL loaded
- Nothing arrives without a message pump, because events are delivered through a hidden window and the normal message queue
- Load the DLL into your own process first with a path built from `GetModuleFileName`, then pass its handle to the hook
- The callback must live in the DLL and be exported, so use `extern "C"` and `__declspec(dllexport)` or a DEF file, or `GetProcAddress` returns NULL
- `WINEVENT_OUTOFCONTEXT` only marshals events back to you; `WINEVENT_INCONTEXT` is the flag that injects
- For a clean exit, signal an event from the DLL and `UnhookWinEvent`, which stops the callback without unloading the DLL

## Keep Learning

If you want to understand these techniques well enough to build and detect them, these TrainSec courses go deeper:

- [Malware Analysis and Development](https://trainsec.net/courses/malware-analysis-and-development/): injection techniques like this one, how they are built, and how they look to a defender
- [Windows System Programming](https://trainsec.net/courses/windows-system-programming/): the Win32 foundations this relies on, from `LoadLibrary` and `GetProcAddress` to the message queue
- [EDR Internals: Research and Development](https://trainsec.net/courses/edr-internals-research-development/): how an endpoint product watches for exactly this kind of cross-process behavior

Related reading in the knowledge library: [DLL Injection with Windows Application Verifier](https://trainsec.net/library/windows-internals/dll-injection-with-windows-application-verifier/), a very different injection route that loads your DLL right after ntdll through the Image File Execution Options key, and [Windows Privileges and SeDebugPrivilege](https://trainsec.net/library/windows-internals/windows-privileges-sedebugprivilege/), which covers the privilege the more direct injection methods often need to touch a process you do not own.

* * *

![blue depth](https://trainsec.net/wp-content/uploads/2024/07/blue-depth.svg)

![Pavel Yosifovich](https://trainsec.net/wp-content/uploads/2026/09/pavel-yosifovich-animated.webp)

About the author

[Pavel Yosifovich](https://trainsec.net/)

Pavel Yosifovich has 25+ years as Software developer, trainer, consultant, author, and speaker. Co-author of “Windows Internals”. Author of “Windows Kernel Programming”, “Windows 10 System Programming, as well as System and kernel programming courses and “Windows Internals” series.

[All my courses and publications](https://trainsec.net/author/pavel-yosifovich/)