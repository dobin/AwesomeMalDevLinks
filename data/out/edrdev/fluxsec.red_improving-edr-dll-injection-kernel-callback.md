# https://fluxsec.red/improving-edr-dll-injection-kernel-callback

# Making improvements to the EDR DLL injection

Ensuring the Sanctum EDR properly loads the EDR DLL at the right time!

* * *

## Intro

You can check this project out on [GitHub](https://github.com/0xflux/Sanctum)!

I have made a few changes I wanted to document as to how I am injecting the EDR’s DLL into target processes.

Originally the injection took place in usermode on notification that a new process had started. This notification came from the Sanctum driver, and in a loop the EDR usermode engine polls the driver for any new notifications per short interval.

This was inefficient as there was a delay between the process starting and the EDR’s DLL being injected. As a temporary measure, I made the ‘malware.exe’ sleep for a short period to allow the usermode engine to detect the new process and do its thing.

Obviously, real malware does no such thing!

## Solution

I wanted to move more control to the driver to make the DLL injection happen; whilst the driver was sending the notification, it had no fine grain control over the process.

One consideration was allowing the EDR to inject the DLL into the newly created processes during the image load callback routine. Whilst possible with a bit care, I do not like the idea of a kernelmode / SYSTEM thread running something from usermode - this feels like a breach of the security model. Whilst we could hash the EDR’s DLL to make sure no tampering occurred (i.e. giving a threat actor access to a SYSTEM thread), I would rather avoid this entirely. The thread in the DLL would be short lived, only setting up hooking, but still - lets not take that risk! Threat model, threat model, threat model!

What I decided to do instead, is utilise the image load callback from `PsSetLoadImageNotifyRoutine`. We can register our callback routine like so:

```rust
// to register
unsafe { PsSetLoadImageNotifyRoutine(Some(image_load_callback)) }

// to unregister
let _ = unsafe { PsRemoveLoadImageNotifyRoutine(Some(image_load_callback)) };

// callback prototype
extern "C" fn image_load_callback(
    image_name: *mut _UNICODE_STRING,
    pid: HANDLE,
    image_info: *mut _IMAGE_INFO,
) {
    // ..
}
```

The strategy here, is to send a message to the usermode engine a new process image has been loaded under certain conditions, i.e. an `exe` has been mapped into memory. At this point; we want to instruct the engine to inject the EDR DLL (so that we are doing so from a non-SYSTEM thread). This means writing an IOCTL for the engine to poll the driver for any new such events.

We don’t need to write an IOCTL for notification of this being completed, instead we can use the callback and look for the **sanctum.dll** being mapped into the process. We then wait for the subsequent image load being completed before we allow the process to execute, and we hold this state with a loop and a sleep waiting for the condition to be met. Using a **KEVENT** would likely be more efficient; but this can wait for a future refactor.

To manage this, we create a struct called `ImageLoadQueueForInjector` (with no fields, as we use globally tracked mutex’s via my [wdk-mutex](https://fluxsec.red/wdk-mutex-windows-driver-mutex) crate). This struct just acts as an interface for us to easily interact with the fields wrapped by the **wdk-mutex**. Thread safe access is required for the data we want to use as any thread may invoke the callback - so if this happens concurrently, we safely need to lock the data contained within - and the easiest way to do this in the windows kernel in Rust is with my **wdk-mutex** crate.

The **ImageLoadQueueForInjector** has 6 methods implemented on it:

- `init` which simply initialises the globally allocated mutex’s and underlying data;
- `queue_process_for_usermode` which tracks newly created processes which require the **sanctum.dll** being loaded;
- `add_dll_injected_for_pid` which is called by `queue_process_for_usermode` which adds the process to a separate queue. The process will then be removed from this separate queue by `remove_pid_from_injection_waitlist` once the EDR DLL has been mapped;
- `remove_pid_from_injection_waitlist` removes the pid from the aforementioned waitlist;
- `pid_in_waitlist` determines whether the process is in the waitlist; if it isn’t then the process can be started, if it is, we loop until the process is removed from the waitlist by `remove_pid_from_injection_waitlist`;
- `drain_queue` drains a queue wrapped in a **wdk-mutex** so that buffers can be sent to usermode after an IOCTL poll.

We then use the image load callback to wait on the sanctum DLL being loaded; once this event takes place we can remove the pid from the waitlist, and break from the loop allowing the process to run - this ensures the process is properly hooked, Ghost Hunting can take place, and other protections we have against malware defeating the DLL are running.

The code is as follows:

```rust
extern "C" fn image_load_callback(
    image_name: *mut _UNICODE_STRING,
    pid: HANDLE,
    image_info: *mut _IMAGE_INFO,
) {

    // Check that we aren't dealing with a driver load, we dont care about those for now
    if pid.is_null() {
        return;
    }

    // Check the inbound pointers
    if image_info.is_null() || image_name.is_null() {
        println!(
            "[sanctum] [-] Pointers were null in image_load_callback, and this is unexpected."
        );
        return;
    }

    // SAFETY: Pointers validated above
    let image_name = unsafe { *image_name };
    let image_info = unsafe { *image_info };

    let name_slice = slice_from_raw_parts(image_name.Buffer, (image_name.Length / 2) as usize);
    let name = String::from_utf16_lossy(unsafe { &*name_slice }).to_lowercase();

    // For now only concern ourselves with image loads where its an exe, except in the event its the sanctum EDR DLL -
    // see below comments for why.
    if name.contains(".dll") && !name.contains("sanctum.dll") {
        return;
    }

    // Now we are into the 'meat' of the callback routine. To see why we are doing what we are doing here,
    // please refer to the function definition. In a nutshell, queue the process creation, the usermode engine
    // will poll the driver for new processes; the driver will wait for notification our DLL is injected.
    //
    // We can get around waiting on an IOCTL to come back from usermode by seeing when "sanctum.dll" is mapped into
    // the PID. This presents one potential 'vulnerability' in that a malicious process could attempt to inject a DLL
    // named "sanctum.dll" into our process; we can get around this by maintaining a second Grt mutex which contains
    // the PIDs that are pending the sanctum dll being injected. In the event the PID has been removed (aka we have a
    // sanctum.dll injected in) we know either foul play is detected (a TA is trying to exploit this vulnerability in the
    // implementation), or a unforeseen sanctum related error has occurred.
    //
    // **NOTE**: Handling the draining of the `ImageLoadQueueForInjector` and adding the pid to the pending `Grt` is handled
    // in the `driver_communication` module - we dont need to worry about that implementation here, it will happen here
    // as if 'by magic'. See the implementation there for more details.
    //
    // In either case; we can freeze the process and alert the user to possible malware / dump the process / kill the process
    // etc.
    //
    // Depending on performance; we could also fast hash the "sanctum.dll"  bytes to see whether it matches the expected DLL -
    // this *may* be more performant than accessing the Grt, but for now, this works.
    if name.ends_with("sanctum.dll") {
        if ImageLoadQueueForInjector::remove_pid_from_injection_waitlist(pid as usize).is_err() {
            // todo handle threat detection here
        }
    }

    // For now, only inject into these processes whilst we test
    if !(name.contains("notepad.exe")
        || name.contains("malware.exe")
        || name.contains("powershell.exe"))
    {
        return;
    }

    println!(
        "Adding process: {:?}, pid: {}, base: {:p} to ImageLoadQueueForInjector",
        name, pid as usize, image_info.ImageBase
    );

    ImageLoadQueueForInjector::queue_process_for_usermode(pid as usize);

    let delay_as_duration = Duration::from_millis(300);
    let mut thread_sleep_time = LARGE_INTEGER {
        QuadPart: -((delay_as_duration.as_nanos() / 100) as i64),
    };

    loop {
        // todo I'd rather use a KEVENT than a loop - just need to think about the memory model for it.
        // Tried implementing this now, but as im at POC phase it required quite a bit of a refactor, so i'll do this in the
        // future more likely. Leaving the todo in to work on this later :)
        // The least we can do is make the threat alertable so we aren't starving too many resources.
        let _ =
            unsafe { KeDelayExecutionThread(KernelMode as _, TRUE as _, &mut thread_sleep_time) };

        if !ImageLoadQueueForInjector::pid_in_waitlist(pid as usize) {
            println!("[sanctum] [i] DLL injected into PID: {}!", pid as usize);
            break;
        }
    }
}
```

It’s also worth noting, that another, perhaps more obvious option, would be to do the above on a process start callback. The problem with this, is that the process has not yet set itself up, nor has the first thread started executing during process creation (as far as I’m aware), so doing so could lead to many, many issues within the process itself. Injecting the DLL on image load has no draw backs as the `.exe` image does not run until this callback is complete.

## Conclusion

And that’s about it, we now can remove the sleep from the ‘malware’ to make sure the EDR DLL is injected straight away.