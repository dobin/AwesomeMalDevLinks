# https://medium.com/@persic.eno/dllparty-abusing-thread-pool-internals-for-shellcodeless-dll-injection-7c84106f7745

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=---top_nav_layout_nav-------------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40persic.eno%2Fdllparty-abusing-thread-pool-internals-for-shellcodeless-dll-injection-7c84106f7745&source=post_page---top_nav_layout_nav-----------------------global_nav--------------------)

[Medium Logo](https://medium.com/?source=---top_nav_layout_nav-------------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav--------------------)

[Search](https://medium.com/search?source=---top_nav_layout_nav-------------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40persic.eno%2Fdllparty-abusing-thread-pool-internals-for-shellcodeless-dll-injection-7c84106f7745&source=post_page---top_nav_layout_nav-----------------------global_nav--------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page---header_tags--7c84106f7745-----------------------------------------)

[Process Injection](https://medium.com/tag/process-injection?source=post_page---header_tags--7c84106f7745-----------------------------------------)

[Malware Development](https://medium.com/tag/malware-development?source=post_page---header_tags--7c84106f7745-----------------------------------------)

# DLLParty — Abusing thread pool internals for shellcodeless DLL injection

[![epersic](https://miro.medium.com/v2/da:true/resize:fill:32:32/0*qrl_CiHTvrxhOptx)](https://medium.com/@persic.eno?source=post_page---byline--7c84106f7745-----------------------------------------)

[epersic](https://medium.com/@persic.eno?source=post_page---byline--7c84106f7745-----------------------------------------)

Follow

11 min read

·

Oct 1, 2026

3

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D7c84106f7745&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40persic.eno%2Fdllparty-abusing-thread-pool-internals-for-shellcodeless-dll-injection-7c84106f7745&source=---header_actions--7c84106f7745---------------------post_audio_button--------------------)

Share

## **Motivation**

Recently I was experimenting with vibecoding custom beacons, injecting beacon code into common open-source DLLs and compiling the malicious code together with legitimate DLL code as a way to avoid having to deal with unbacked memory and “dirty” callstacks. Having your beacon compiled as part of a DLL rather than as shellcode has its pros and cons, one of the major cons being you lose the process injection options, as most modern process injection techniques rely on your code being in a shellcode format.

Previously when thread pools were used to perform a DLL injection it was always through an assembly trampoline or shellcode, like in this research [here](https://0xdarkvortex.dev/proxying-dll-loads-for-hiding-etwti-stack-tracing/) from Paranoid Ninja.

In this blog I am going to try and answer the following question: Is it possible to coerce Windows internals to load the DLL for you without using any shellcode?

PS: This technique builds heavily on P [oolParty](https://blackhat.com/archive/europe/2023/briefings/schedule/#the-pool-party-you-will-never-forget-new-process-injection-techniques-using-windows-thread-pools-35446) technique, with one key difference — We won’t use any shellcode at all! No code execution from unbacked memory and in certain cases even no calls to VirtualAllocEx.

### **Classic DLL injection and why it’s bad**

Classic DLL injection has the following flow:

1. Allocate the memory in the process you want to inject the DLL to with VirtualAllocEx, this place will be used to store the path of the DLL we want to inject.
2. Use WriteProcessMemory to write the DLLpath into the allocated memory from the first step.
3. Call CreateRemoteThreadEx with the following arguments: Pointer to LoadLibrary function and a pointer to dllPath string that we stored earlier. This will create a thread in another process that will execute LoadLibrary function loading the DLL from our path into the targeted process.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ysvpHVadnlqurS4-wUt5Ow.png)

This combination of APIs is strongly associated with injection with the most critical one being CreateRemoteThreadEx, very few legitimate processes have a legitimate need to create a thread in another process, mostly debuggers and other development tools. Windows has kernel callbacks that trigger when a thread is created, seeing that the creator of the thread isn’t the same process as the one the thread is being created in is a major red flag. Beyond classic Windows Kernel callbacks ETW TI allows for monitoring both VirtualAllocEx and WriteProcessMemory calls. However, detecting only VirtualAllocEx or only WriteProcessMemory calls very often isn’t a big enough indicator to raise the detection by itself.

### Windows thread pools and Poolparty

I won’t go into detail on how Windows thread pools or Poolparty technique work. I suggest reading the original Poolparty research for that, there is also this [website](https://racoten.github.io/Self-Taught-Course/Project/PoolParty/PoolParty_index.html) that does a pretty good job of explaining it, even though there are some mistakes in pseudo code examples.

Brief overview: Windows thread pools are a feature where Windows keeps alive so-called “Worker threads”, you can delegate any tasks you want to be executed asynchronously to them. The tasks are delegated in the form of callback functions. You give the thread pool a callback function you want to be executed, it puts it onto a queue and a worker thread that doesn’t have a job currently fetches it and executes your callback function. This is done because the creation of new threads is expensive, this way the cost of smaller parallel tasks executed in separate threads is way smaller.

Poolparty technique abuses this feature by manually putting work onto another processe’s thread pool queue (the queue is called IOCP), with the callback pointing to the shellcode that was previously written into the target process memory, rather than pointing to a legitimate callback function. That way the worker thread that picks up that callback will execute the shellcode.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*C94gFqBQILJEHcOapi7vVA.png)

### DLLParty

When using thread pools legitimately, callback function needs to have one of the predefined signatures:

![](https://miro.medium.com/v2/resize:fit:281/1*DqZ9mxHAoYlQhxGXMT9tcw.png)

Thread pool wait callback signature

![](https://miro.medium.com/v2/resize:fit:271/1*P7_tPFbF9ZpEQKjF4fzz3w.png)

Thread pool work callback signature

![](https://miro.medium.com/v2/resize:fit:278/1*nTkvC0o2KuixW1tN1_rEZA.png)

Thread pool timer callback signature

These are just a few examples, there are more of them. The thing you may notice they all have in common is the first parameter: a pointer to TP\_CALLBACK\_INSTANCE structure. Let’s take a look at LoadLibraryA definition.

![](https://miro.medium.com/v2/resize:fit:200/1*F_4kc0Aov51OiwWfUBu7DQ.png)

LoadLibraryA signature

The function takes only 1 argument, a pointer to the string. A pointer is simply an address in memory, whether it points to TP\_CALLBACK\_INSTANCE or a string is up to the function receiving the pointer, in this case LoadLibraryA and the callback function, to interpret it.

The idea is the following: If we can manipulate the TP\_CALLBACK\_INSTANCE object in a stable way and change it to “C:\\path\\to\\dll.dll”, path of the DLL we want to inject, it is possible to set the callback function directly to LoadLibraryA from kernel32.dll, it will read the string from the pointer and load the DLL without us having to execute any custom shellcode in the target process, all done by kernel32 function and a worker thread.

The problem is TP\_CALLBACK\_INSTANCE is not user-controlled, it is internally built by Windows itself.

### TP\_CALLBACK\_INSTANCE

Normal and expected worker thread call stack looks something like this:

![](https://miro.medium.com/v2/resize:fit:404/1*_GV48Apj7is5awgAaGNm2A.png)

Worker thread stack

TppWorkerThread function is the “main” function of every worker thread whose oversimplified code is this:

```
void TppWorkerThread(TP_POOL* pool)
{
    TP_CALLBACK_INSTANCE instance = {};

    RegisterWorkerWithPool(pool, &worker);

    while (true)
    {
        WaitForWork();

        TASK* task = GetNextTask(pool);
        if (!task)
            break;

        PopulateCallbackInstance(&instance, task);

        task->Callback(&instance, task->Context);

        CleanupAndResetInstance(&instance);
    }

    UnregisterWorkerFromPool(pool);
}
```

This is highly simplified but it gives us a good intuitive picture of how the function works and what its tasks are. It has a while loop where it waits for tasks.

We can start from here and work back to determine exactly how and where pointer to TP\_CALLBACK\_INSTANCE is crafted.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*EDzRBuraJZ-ns3G9RP_Few.png)

Callback function invocation

This snippet of code shows where the callback function is being invoked, from here we can see that the pointer is crafted right before the invocation using x64 lea instruction, since the first parameter (rcx on x64 calling convention), is located at rsp+0x178. This tells us two things: TP\_CALLBACK\_INSTANCE object is located on the stack (read/write memory by default) and object location remains stable relative to rsp register before the callback is executed in the TppWorkerThread function. This is good news because this means that we can locate the object while the worker thread is waiting to pick up some work. We can abuse this by first injecting our own bytes at rsp+0x178 and then adding work to the queue effectively controlling what the pointer points to.

![](https://miro.medium.com/v2/resize:fit:353/1*vlCbn8OyDfhYpoZcbTWTPQ.png)

Stack schema with injected bytes

The only thing that remains to be seen is how the TP\_CALLBACK\_INSTANCE object is actually populated, if the whole object is populated before the work is picked up our injected bytes will be overwritten. Since we know that TP\_CALLBACK\_INSTANCE object begins at rsp+0x178 we can simply look at all instructions writing to memory locations after rsp+0x178 to see how the object is populated.

The TP\_CALLBACK\_INSTANCE is populated in many steps, but the one we really only care about is the one that is the closest to rsp+0x178, because that will tell us if we have any space to work with regarding bytes that remain untouched during the population.

And as it turns out, most of the time we do!

After looking through the function the first address that seems to be populated inside of TP\_CALLBACK\_INSTANCE object is rsp+0x1d0. This means that we have 0x1d0–0x178(88) bytes of memory that remain untouched before the worker thread calls the callback function!

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:583/1*VS2y3nw1qHP-uSL3SNGoOA.png)

Populating of TP\_CALLBACK\_INSTANCE

The prefix is reserved for conditional internal callback bookkeeping. On the ordinary paths tested here, those fields were unused and remained zero.

### Locating TP\_CALLBACK\_INSTANCE object

Now that we know that we can safely inject our own bytes to the beginning of the TP\_CALLBACK\_INSTANCE object and Windows will internally craft a pointer pointing to them, effectively passing a string to the function (DLL path in DLLinjection case) we need to be able to reliably locate the TP\_CALLBACK\_INSTANCE object.

## Get epersic’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

The first approach would be to use the [GetThreadContext](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getthreadcontext) function to read the RSP register directly. This approach has several downsides. Since we cannot tell which worker thread from the thread pool will pick up our work, we need to enumerate all the threads in the process and open handles to all of them and overwrite the bytes at rsp+0x178 on all threads stacks. Although unsuspended context reads frequently produced usable values during testing, Microsoft does not guarantee a valid context for a running thread. This approach is therefore inherently racy and was replaced by direct worker-list traversal.

Second approach doesn’t require enumerating or opening handles to any of the threads. Lets take a look at what else is there on the stack inside of TppWorkerThread function frame.

At the beginning of the function 0x168 bytes are set to 0, starting from rsp+0x140.

![](https://miro.medium.com/v2/resize:fit:520/1*GhAo9T57Iwn_6a_7umPGAA.png)

Initial stack initialization

You may notice that this is 0x38 bytes before the beginning of TP\_CALLBACK\_INSTANCE object (0x178–0x140). Those bytes are populated with metadata before the main while loop.

TppWorkerThread calls TppPoolAddWorker function and passes it pointer to rsp+0x140.

![](https://miro.medium.com/v2/resize:fit:517/1*p72Lfp59a70utLmeIFZk5w.png)

TppPoolAddWorker call

TppPoolAddWorker then inserts the pool worker-list head.

![](https://miro.medium.com/v2/resize:fit:513/1*xZQaz7oYfhSjcqDaf_eFEA.png)

Moves the pointer the the rsp+0x140 to rdi and rcx into rbx.

![](https://miro.medium.com/v2/resize:fit:380/1*nEc17q6uarEO0aI9iboaWg.png)

Loading of initial values

Loads that pointer into rax and offset 0x60 of rbx(previously rcx) back to rcx:

![](https://miro.medium.com/v2/resize:fit:433/1*xS9RadwtbKIAUdbYjYEDJQ.png)

And moves pointers that it just crafted into memory locations it just calculated:

![](https://miro.medium.com/v2/resize:fit:482/1*9viYKYvxTnKH5rH50nVngg.png)

What this sequence actually just did was create or update a linked list.

The thing I didn’t mention is what was in the rsi register from the first snippet “TppPoolAddWorker call” in this sequence. In RSI register was an address of TP\_POOL object.

During classic poolparty we fetch TP\_POOL object like this:

```
WORKER_FACTORY_BASIC_INFORMATION wfbi;
NtQueryInformationWorkerFactory_t NtQueryInformationWorkerFactory =
  (NtQueryInformationWorkerFactory_t)GetProcAddress(
    GetModuleHandleA("ntdll"),"NtQueryInformationWorkerFactory"
    );

NtQueryInformationWorkerFactory(
  wf_dup_handle,WorkerFactoryBasicInformation,&wfbi,sizeof(wfbi),NULL);

target_pool_ptr = wfbi.StartParameter;
target_worker_factory = wf_dup_handle;

FULL_TP_POOL_PREFIX pool = {0};
SIZE_T bytes_read =0;
ReadProcessMemory(
    proc_handle,target_pool_ptr,&pool,sizeof(pool),&bytes_read));
```

TP\_POOL structure definition (not 100% correct but good enough):

```
typedef struct _FULL_TP_POOL_PREFIX {
    TPP_REFCOUNT Refcount;              // 0x00
    LONG Padding;                       // 0x04
    TPP_POOL_QUEUE_STATE QueueState;    // 0x08
    TPP_QUEUE *TaskQueue[3];            // 0x10
    TPP_NUMA_NODE *NumaNode;            // 0x28
    GROUP_AFFINITY *ProximityInfo;      // 0x30
    PVOID WorkerFactory;                // 0x38
    PVOID CompletionPort;               // 0x40
    SRWLOCK WorkerListLock;              // 0x48
    BYTE Unknown50[0x10];               // 0x50
    LIST_ENTRY WorkerListHead;           // 0x60
} FULL_TP_POOL_PREFIX;
```

So lets go through the assembly one more time:

```
mov rdx [rsp+0x140] //pointer to the structure before TP_CALLBACK_INSTANCE
                    //is passed to rdx
mov rcx,rsi //pointer to TP_POOL is moved to rcx(calling convention)
mov [rdx+0x30] rcx //stores pointer to TP_POOL to rsp+0x140+0x30 (0x170)
mov rdi,rdx //moves rsp+0x140 to rdi
mov rbx,rcx //pointer to TP_POOL moved to rbx
lea rax,[rdi+0x10] //loads the address of rsp+0x140+0x10 to rax
lea rcx [rbx+0x60] //loads the address of the head of the list to rcx!!
mov rdx, [rcx+0x08]  //moves the address of the current tail to rdx
mov [rax],rcx //Saves the pointer to head of the list to rsp+0x140+0x10
              //Because the new worker is inserted to the tail of the list (flink)
mov [rax+0x8],rdx // stores the address of previous tail into current structure
mov [rdx], rax            //oldTail->Flink = node
mov [rcx+0x08], rax       //head->Blink = node
```

Which means that by fetching TP\_POOL of a worker factory we get access to the linked list that contains all structures that are always 0x38 bytes before our targeted TP\_CALLBACK\_INSTANCE object, we can easily fetch TP\_CALLBACK\_INSTANCE pointer by adding 0x28 the address stored in the list. This is a much better approach, no new handles opened, no loud context reading APIs and no thread enumeration.

So to recap the to-do list:

1. Find all TP\_CALLBACK\_INSTANCE objects in the pool we are going to post work to.
2. Inject the DLL path string into the beginning of TP\_CALLBACK\_INSTANCE
3. Set a callback function to LoadLibraryA
4. Push the callback into queue (just like normal poolparty)

And it works!

![](https://miro.medium.com/v2/resize:fit:547/1*NwZZEEbYfs-bfTd9Yiu-0g.png)

DLLparty execution

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*4ovZmjy3n4zWlsWvBPPEag.png)

Dll injection into notepad

We get a callstack that looks like this:

![](https://miro.medium.com/v2/resize:fit:281/1*It3h7jszjho5EeyGWiIhHA.png)

DLLParty callstack

### Avoiding VirtualAllocEx

In the standard PoolParty technique VirtualAllocEx is called 2 times. First it’s called to allocate space for the shellcode and second time it’s called to allocate space for a variant specific TP structure that is pushed onto the IOCP queue. Let’s take a loo at the TP\_DIRECT PoolParty variant. TP\_DIRECT object is created and pushed onto the IOCP queue. TP\_DIRECT object is only 72 bytes big, not a lot of space is needed to store that. Since we already have pointers to READ/WRITE stack memory (TP\_CALLBACK\_INSTANCE pointers) we can choose one of those, subtract some offset(experimentally it seems 0x500 works fine) so that the object doesn’t get overwritten by function calls that happen before the callback is invoked. We already don’t have to call VirtualAllocEx for the shellcode allocation, because we aren’t using any. And we can store the TP structure on the not yet used stack to avoid having to use VirtualAllocEx the second time.

![](https://miro.medium.com/v2/resize:fit:700/1*JqfTSBKg6h-aUz8lmqHRfA.png)

Stack draft

### Conclusion

This technique isn’t actually just a DLL injection, it allows you to coerce a worker thread to call any function that matches chosen callback signature. If you take a quick look back to beginning of this blog you will see different signatures callback functions need to have depending on the type of callback we want to execute. Now we know that you can control PTP\_CALLBACK\_INSTANCE, the first parameter. Second parameter is controllable by default. There are callback signature that have other parameters after these two, if we can also control all of those we can make worker threads execute even more functions, but this is a topic for some further research perhaps.

Exact offsets that I mentioned here can change from build to build, this was done on the latest Windows 10 build, but the general technique should remain the same for a longer time because it would require changing how TppWorkerThread works or changing TP\_INSTANCE\_CALLBACK structure.

The callstack where TppWorkerThread calls LoadLibraryA is still kinda suspicious. TppWorkerThread is a hardcoded compiled function, why is it calling LoadLibraryA? If you look at the source code there is a set number of functions it calls + the callback functions that are always user defined. The point is it is not suspicious enough, it’s one legitimate kernel32 function calling another, no unbacked memory, no heavily monitored API calls, no triggering kernel callbacks. It might look super suspicious to us after this research but to an EDR or even an analyst that didn’t go in depth on thread pool internals it likely won’t. It certainly looks much cleaner than unbacked shellcode.

The [POC](https://github.com/epersic/DLLParty/tree/main) that I provided is just a demonstration of the technique, if you want to use it in actual evasion scenarios make sure to modify the code with OPSEC in mind.

If anyone actually made it this far, thanks for reading and I hope you found this interesting! :D

PS: This is my first research blog, any and all criticism and suggestions are welcome!

By [epersic](https://www.linkedin.com/in/eno-per%C5%A1i%C4%87-2a993a30b/)

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page---footer_tags--7c84106f7745-----------------------------------------)

[Process Injection](https://medium.com/tag/process-injection?source=post_page---footer_tags--7c84106f7745-----------------------------------------)

[Malware Development](https://medium.com/tag/malware-development?source=post_page---footer_tags--7c84106f7745-----------------------------------------)

[![epersic](https://miro.medium.com/v2/resize:fill:48:48/0*qrl_CiHTvrxhOptx)](https://medium.com/@persic.eno?source=post_page---post_author_info--7c84106f7745-----------------------------------------)

[![epersic](https://miro.medium.com/v2/resize:fill:64:64/0*qrl_CiHTvrxhOptx)](https://medium.com/@persic.eno?source=post_page---post_author_info--7c84106f7745-----------------------------------------)

Follow

[**Written by epersic**](https://medium.com/@persic.eno?source=post_page---post_author_info--7c84106f7745-----------------------------------------)

[3 followers](https://medium.com/@persic.eno/followers?source=post_page---post_author_info--7c84106f7745-----------------------------------------)

· [1 following](https://medium.com/@persic.eno/following?source=post_page---post_author_info--7c84106f7745-----------------------------------------)

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----7c84106f7745-----------------------------------------)

[Status](https://status.medium.com/?source=post_page-----7c84106f7745-----------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----7c84106f7745-----------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----7c84106f7745-----------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----7c84106f7745-----------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----7c84106f7745-----------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----7c84106f7745-----------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----7c84106f7745-----------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----7c84106f7745-----------------------------------------)

reCAPTCHA

Recaptcha requires verification.

protected by **reCAPTCHA**