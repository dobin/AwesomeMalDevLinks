# https://fluxsec.red/event-tracing-for-windows-threat-intelligence-rust-consumer

# Reading Event Tracing for Windows Threat Intelligence

Malware thought it could sneak past your EDR. Spoiler: It didn’t. Here’s how to make it regret its life choices.

* * *

## Intro

Now we can get into some more really cool stuff by utilising the Event Tracing for Windows: Threat Intelligence (ETW:TI) provider. I have actually talked about bypassing
ETW in my blog post [EDR Evasion ETW patching in Rust](https://fluxsec.red/etw-patching-rust).

That post deals with patching out certain telemetry signals from a usermode process, blinding the EDR to those signals. However; as stated there, we cannot patch out the
Threat Intelligence provider as this is emitted from within the kernel itself. To do so, you’d require kernelmode execution and then to patch out those signals so no
ETW signals are emitted.

I’ve made a short proof of concept video you can checkout on my YouTube channel:

Event Tracing for Windows Threat Intelligence for a Rust EDR - YouTube

[Photo image of FluxSec](https://www.youtube.com/channel/UCQMxJOLahofVDOQClNRqLJw?embeds_referring_euri=https%3A%2F%2Ffluxsec.red%2F)

FluxSec

418 subscribers

[Event Tracing for Windows Threat Intelligence for a Rust EDR](https://www.youtube.com/watch?v=t2qx0xTDnCI)

FluxSec

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

More videos

## More videos

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=t2qx0xTDnCI&embeds_referring_euri=https%3A%2F%2Ffluxsec.red%2F)

0:00

0:00 / 6:50

•Live

•

ETW Threat Intelligence is a goldmine of additional telemetry we cannot get though driver callback routines alone. These include:

1. Allocating memory (either in the local or remote process0)
2. Changing the protection of memory
3. Queueing an APC (see my blog post on bypassing EDR via [Queue User APC](https://fluxsec.red/apc-queue-injection-rust), this is something we can detect with Sanctum EDR via ETW:TI)
4. Suspend / resume process
5. Suspend / resume thread
6. And more!

These are all super useful sources of information that we can use to combat modern malware in this EDR project!

Pulling all of this together is my [Ghost Hunting](https://fluxsec.red/edr-syscall-hooking) technique, which we can use to detect
foul play at malware trying to implement ‘classic’ antivirus and EDR evasion techniques like those I have already blogged about before.

## Requirements

In order to start receiving ETW:TI signals, we need:

1. A service running as Protected Process Light
2. An Early Launch Antimalware driver and certificate
3. A logging mechanism (we will use the Windows Event Log)

Points 1 and 2 are covered in my previous blog post, [Creating a Protected Process Light](https://fluxsec.red/creating-a-ppl-protected-process-light-in-rust-windows)
and point 3 you can check out my [logging](https://github.com/0xflux/Sanctum/blob/main/sanctum_ppl_runner/src/logging.rs) module of the project.

## Threat Intelligence basics

With the requirements in place, we are ready to write the ETW:Threat Intelligence consumer!

One thing to note; this will block the main thread in the service - so we will want to run this in its **own OS thread**.

First of all, getting started with this was a little daunting as there is not much information about the Threat Intelligence provider in terms of implementation,
so the first port of call is to run this in powershell, which will give us all the information we could want to know at this stage about ETW:TI.

```shell
wevtutil gp Microsoft-Windows-Threat-Intelligence
```

What this gives us, is the **GUID** of the provider which we need to subscribe to it, as well as all the tasks and keywords the provider has to offer.

![Windows Event Tracing for Windows Threat Intelligence](https://fluxsec.red/static/images/etw_1.png)

The opcodes are split into two parts:

1. **Tasks:** These are the major component of the provider. These are given an integer identifier.
2. **Keywords:** These are a 64-bit bitmask used to indicate an events membership in a set of categories.

I have taken these out and set them as constants in our **tracing.rs** module ( [link](https://github.com/0xflux/Sanctum/blob/main/sanctum_ppl_runner/src/tracing.rs))
and they look as follows:

```rust
const KERNEL_THREATINT_TASK_ALLOCVM: u16                = 1;
const KERNEL_THREATINT_TASK_PROTECTVM: u16              = 2;
const KERNEL_THREATINT_TASK_MAPVIEW: u16                = 3;
const KERNEL_THREATINT_TASK_QUEUEUSERAPC: u16           = 4;
const KERNEL_THREATINT_TASK_SETTHREADCONTEXT: u16       = 5;
const KERNEL_THREATINT_TASK_READVM: u16                 = 6;
const KERNEL_THREATINT_TASK_WRITEVM: u16                = 7;
const KERNEL_THREATINT_TASK_SUSPENDRESUME_THREAD: u16   = 8;
const KERNEL_THREATINT_TASK_SUSPENDRESUME_PROCESS: u16  = 9;
const KERNEL_THREATINT_TASK_DRIVER_DEVICE: u16          = 10;

// Keyword masks for ETW:TI
const KERNEL_THREATINT_KEYWORD_ALLOCVM_LOCAL: u64                           = 0x1;
const KERNEL_THREATINT_KEYWORD_ALLOCVM_LOCAL_KERNEL_CALLER: u64             = 0x2;
const KERNEL_THREATINT_KEYWORD_ALLOCVM_REMOTE: u64                          = 0x4;
const KERNEL_THREATINT_KEYWORD_ALLOCVM_REMOTE_KERNEL_CALLER: u64            = 0x8;
const KERNEL_THREATINT_KEYWORD_PROTECTVM_LOCAL: u64                         = 0x10;
const KERNEL_THREATINT_KEYWORD_PROTECTVM_LOCAL_KERNEL_CALLER: u64           = 0x20;
const KERNEL_THREATINT_KEYWORD_PROTECTVM_REMOTE: u64                        = 0x40;
const KERNEL_THREATINT_KEYWORD_PROTECTVM_REMOTE_KERNEL_CALLER: u64          = 0x80;
const KERNEL_THREATINT_KEYWORD_MAPVIEW_LOCAL: u64                           = 0x100;
const KERNEL_THREATINT_KEYWORD_MAPVIEW_LOCAL_KERNEL_CALLER: u64             = 0x200;
const KERNEL_THREATINT_KEYWORD_MAPVIEW_REMOTE: u64                          = 0x400;
const KERNEL_THREATINT_KEYWORD_MAPVIEW_REMOTE_KERNEL_CALLER: u64            = 0x800;
const KERNEL_THREATINT_KEYWORD_QUEUEUSERAPC_REMOTE: u64                     = 0x1000;
const KERNEL_THREATINT_KEYWORD_QUEUEUSERAPC_REMOTE_KERNEL_CALLER: u64       = 0x2000;
const KERNEL_THREATINT_KEYWORD_SETTHREADCONTEXT_REMOTE: u64                 = 0x4000;
const KERNEL_THREATINT_KEYWORD_SETTHREADCONTEXT_REMOTE_KERNEL_CALLER: u64   = 0x8000;
const KERNEL_THREATINT_KEYWORD_READVM_LOCAL: u64                            = 0x10000;
const KERNEL_THREATINT_KEYWORD_READVM_REMOTE: u64                           = 0x20000;
const KERNEL_THREATINT_KEYWORD_WRITEVM_LOCAL: u64                           = 0x40000;
const KERNEL_THREATINT_KEYWORD_WRITEVM_REMOTE: u64                          = 0x80000;
const KERNEL_THREATINT_KEYWORD_SUSPEND_THREAD: u64                          = 0x100000;
const KERNEL_THREATINT_KEYWORD_RESUME_THREAD: u64                           = 0x200000;
const KERNEL_THREATINT_KEYWORD_SUSPEND_PROCESS: u64                         = 0x400000;
const KERNEL_THREATINT_KEYWORD_RESUME_PROCESS: u64                          = 0x800000;
const KERNEL_THREATINT_KEYWORD_FREEZE_PROCESS: u64                          = 0x1000000;
const KERNEL_THREATINT_KEYWORD_THAW_PROCESS: u64                            = 0x2000000;
const KERNEL_THREATINT_KEYWORD_CONTEXT_PARSE: u64                           = 0x4000000;
const KERNEL_THREATINT_KEYWORD_EXECUTION_ADDRESS_VAD_PROBE: u64             = 0x8000000;
const KERNEL_THREATINT_KEYWORD_EXECUTION_ADDRESS_MMF_NAME_PROBE: u64        = 0x10000000;
const KERNEL_THREATINT_KEYWORD_READWRITEVM_NO_SIGNATURE_RESTRICTION: u64    = 0x20000000;
const KERNEL_THREATINT_KEYWORD_DRIVER_EVENTS: u64                           = 0x40000000;
const KERNEL_THREATINT_KEYWORD_DEVICE_EVENTS: u64                           = 0x80000000;
const KERNEL_THREATINT_KEYWORD_READVM_REMOTE_FILL_VAD: u64                  = 0x100000000;
const KERNEL_THREATINT_KEYWORD_WRITEVM_REMOTE_FILL_VAD: u64                 = 0x200000000;
const KERNEL_THREATINT_KEYWORD_PROTECTVM_LOCAL_FILL_VAD: u64                = 0x400000000;
const KERNEL_THREATINT_KEYWORD_PROTECTVM_LOCAL_KERNEL_CALLER_FILL_VAD: u64  = 0x800000000;
const KERNEL_THREATINT_KEYWORD_PROTECTVM_REMOTE_FILL_VAD: u64               = 0x1000000000;
const KERNEL_THREATINT_KEYWORD_PROTECTVM_REMOTE_KERNEL_CALLER_FILL_VAD: u64 = 0x2000000000;
```

As you can see - these are quite self descriptive. Taking an example we will build out here as a POC of this process working,
if our **malware.exe** allocates memory in a remote process, then we would expect to receive information about:

**Task:** KERNEL\_THREATINT\_TASK\_ALLOCVM (1) with a bitmask of **KERNEL\_THREATINT\_KEYWORD\_ALLOCVM\_REMOTE** (4).

And in fact, this is exactly what we can infer from the signal:

![Detecting VirtualAllocEx EDR](https://fluxsec.red/static/images/rem_mem_etw.png)

We do successfully detect memory being allocated in a remote process, which was done via `VirtualAllocEx`.

## Implementation

Okay so, there’s a couple of milestones we need to meet in order to get this working:

1. Initialise a **EVENT\_TRACE\_PROPERTIES** structure and register the session
2. Configure the trace session
3. Deliver tracing events to our callback routine
4. Process the event in the callback

### Initialisation

To perform the initialisation, we need to create a [EVENT\_TRACE\_PROPERTIES](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-event_trace_properties)
structure, which **importantly** contains space at the end of the struct for the session name.

We heap allocate a buffer which is the size of the struct, plus the length of the session name (multiplied by the size of a wide char so we don’t cut our string in half!)
and set some flags, importantly: **EVENT\_TRACE\_REAL\_TIME\_MODE** as we don’t want to trace to a file. We also have to set the total size of the structure and where the offset
is of the session name (remember, our struct is \[size of struct + (length of string \* 2)\]).

Then, we copy the session name into the buffer and we are good to call [StartTraceW](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-starttracew). We also
need to pass in a handle of type [CONTROLTRACE\_HANDLE](https://microsoft.github.io/windows-docs-rs/doc/windows/Win32/System/Diagnostics/Etw/struct.CONTROLTRACE_HANDLE.html)
which is our way of interacting with the session.

This section looks as follows:

```rust
let mut handle = CONTROLTRACE_HANDLE::default();

let mut wide_name: Vec<u16> = "SanctumETWThreatIntelligence\0".encode_utf16().collect();
let session_name = PCWSTR::from_raw(wide_name.as_ptr());

// SAFETY: null pointer for getting the session name length checked above.
let total_size: usize = size_of::<EVENT_TRACE_PROPERTIES>() + (wide_name.len() * size_of::<u16>());

// allocate a buffer for the properties plus the session name (len calculated above)
let mut buffer = vec![0u8; total_size];
// get a mutable pointer to the start of the buffer, casting as EVENT_TRACE_PROPERTIES
let properties = buffer.as_mut_ptr() as *mut EVENT_TRACE_PROPERTIES;

if properties.is_null() {
    event_log("Buffer was null for EVENT_TRACE_PROPERTIES. Cannot proceed safely.", EVENTLOG_ERROR_TYPE, EventID::GeneralError);
    std::process::exit(1);
}

// allocate the correct parameters for the EVENT_TRACE_PROPERTIES in the buffer.
// SAFETY: Null pointer checked above.
unsafe {
    (*properties).Wnode.BufferSize = total_size as _;
    (*properties).Wnode.Flags = EVENT_TRACE_REAL_TIME_MODE;
    (*properties).LogFileMode = EVENT_TRACE_REAL_TIME_MODE;
    // set logger name offset to the right of the structure
    (*properties).LoggerNameOffset = size_of::<EVENT_TRACE_PROPERTIES>() as _;
}
let logger_name_ptr = unsafe {
    // copy the session name into the buffer
    let logger_name_ptr = (buffer.as_mut_ptr() as usize + (*properties).LoggerNameOffset as usize) as *mut u16;
    copy_nonoverlapping(wide_name.as_ptr(), logger_name_ptr, wide_name.len());

    logger_name_ptr
};
let embedded_session_name = PCWSTR::from_raw(logger_name_ptr);

let status = unsafe { StartTraceW(
    &mut handle,
    embedded_session_name,
    properties)
};
if status.is_err() {
    event_log(&format!("Unable to register ETW:TI session. Failed with Win32 error: {:?}", status), EVENTLOG_ERROR_TYPE, EventID::GeneralError);
    std::process::exit(1);
}
```

### Configuring the session

Now that we have registered it, we need to call [EnableTraceEx2](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-enabletraceex2)
which configures how the trace session operates.

**Importantly** here we can configure which keywords we want to filter on, we can either apply a bitmask in here or, set all bits to true via `u64::MAX`
so we receive all events. This would be something to play around with if you want some tuning.

At this point we also need to provide the GUID (which we talked about in an above section), for this we can define a constant:

```rust
const ETW_TI_GUID: windows::core::GUID = windows::core::GUID::from_u128(0xf4e1897c_bb5d_5668_f1d8_040f4d8dd344);
```

And the implementation looks like:

```rust
let status = unsafe {
    EnableTraceEx2(
        handle,
        &ETW_TI_GUID,
        EVENT_CONTROL_CODE_ENABLE_PROVIDER.0,
        TRACE_LEVEL_VERBOSE as _,
        u64::MAX, // set all bits in the mask
        0,
        0,
        None,
    )
};
```

### Deliver events to the callback

The mechanism for event tracing is that we have a callback routine (similar to those we used in the driver). In order to do this we first must initialise
an [EVENT\_TRACE\_LOGFILEW](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-event_trace_logfilew) configuring a few flags and fields,
but **importantly** we provide a function pointer to the structure which tells the system where our callback routine is.

We then call [OpenTraceW](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-opentracew) which sets this up.

This as as follows:

```rust
{
    let mut log_file = EVENT_TRACE_LOGFILEW::default();
    log_file.LoggerName = PWSTR(session_name.as_mut_ptr());
    log_file.Anonymous1.ProcessTraceMode = PROCESS_TRACE_MODE_REAL_TIME | PROCESS_TRACE_MODE_EVENT_RECORD;
    log_file.Anonymous2.EventRecordCallback = Some(trace_callback);

    let trace_handle = unsafe { OpenTraceW(&mut log_file) };
}

/// A callback routine that handles trace events, allowing them to be processed as required
unsafe extern "system" fn trace_callback(record: *mut EVENT_RECORD) {
    // the callback fn
}
```

And then, we run ProcessTrace which is a blocking function (hence having to take this off the main thread) which delivers trace events to the consumer.

```rust
let status = unsafe { ProcessTrace(&[trace_handle], None, None) };
```

### The callback routine

For our callback routine, we have access to a [EVENT\_RECORD](https://learn.microsoft.com/en-us/windows/win32/api/evntcons/ns-evntcons-event_record) structure which contains
information on the event, such as the Process ID (pid), which task triggered the event, as well as the bitmask.

There is a **UserData** field which Microsoft say:

Event specific data. To parse this data, see Retrieving Event Data Using TDH. If the Flags member of EVENT\_HEADER
contains EVENT\_HEADER\_FLAG\_STRING\_ONLY, the data is a null-terminated Unicode string that you do not need TDH to parse.

Now; I’m not entirely sure the best way to parse this out and what may even be in there (I may have to attach a debugger or dump some memory to have a look) - but I will
tackle this at a later date. I believe it is likely this will contain some useful information for us, though we may not specifically need it for
[Ghost Hunting](https://fluxsec.red/edr-syscall-hooking).

From my code here, you can tweak it to start playing about with some pattern matching on the task and keyword masks to get whatever notifications you like! I have also written
a small function to get the process image from the PID which allows us to explicitly filter on processes with **malware** and **notepad** in their image which will make
log hunting easier for us, seeing as **malware.exe** is doing bad things to **notepad.exe** :E.

I have found through this, even though the service is running in the context of **SYSTEM** at **Protected Process Light**, we cannot get a handle to **SYSTEM** processes. Which I
guess makes sense, but this is a potential blind spot. The only way I can realistically see process injection into a SYSTEM process working is via DLL Sideloading, but I would like
to hope that processes running at **SYSTEM** will only load signed, trusted libraries?

Anyway, the code:

```rust
/// A callback routine that handles trace events, allowing them to be processed as required
unsafe extern "system" fn trace_callback(record: *mut EVENT_RECORD) {
    if record.is_null() {
        event_log("Event was a null pointer in the tracer callback routine.", EVENTLOG_ERROR_TYPE, EventID::GeneralError);
        return;
    }

    // SAFETY: Null pointer dereference checked above
    let event_header = unsafe {&(*record).EventHeader};
    let descriptor_id = event_header.EventDescriptor.Id;
    let task = event_header.EventDescriptor.Task;
    let keyword = event_header.EventDescriptor.Keyword;
    let level = event_header.EventDescriptor.Level;
    let pid = event_header.ProcessId;

    // lookup the process image name
    let process_image = {
        match get_process_image_from_pid(pid, event_header) {
            Ok(s) => s,
            Err(_) => return,
        }
    };

    if process_image.to_ascii_lowercase().contains("malware") || process_image.to_ascii_lowercase().contains("notepad") {

        if keyword & KERNEL_THREATINT_KEYWORD_ALLOCVM_REMOTE == KERNEL_THREATINT_KEYWORD_ALLOCVM_REMOTE {
            event_log(&format!("Remote memory allocation caught for pid: {}, image: {}. Data: {:?}", pid, process_image, event_header.EventDescriptor), EVENTLOG_SUCCESS, EventID::ProcessOfInterestTI);
        }

    }

}

/// Get the process image as a string for a given pid
///
/// # Errors
/// This function will return an error if it cannot get a handle to the pid, or there was a string conversion error from the image buffer.
/// This function is unable to get a handle to SYSTEM processes.
fn get_process_image_from_pid(pid: u32, event_header: &EVENT_HEADER) -> Result<String, ()> {
    let process_handle = match unsafe { OpenProcess(PROCESS_ALL_ACCESS, false, pid) } {
        Ok(h) => h,
        Err(e) => {
            event_log(&format!("Failed to open process for pid: {pid} from event information: {:?}. Error: {e}", event_header.EventDescriptor), EVENTLOG_ERROR_TYPE, EventID::GeneralError);
            return Err(());
        },
    };

    let mut process_img_buffer: Vec<u16> = vec![0u16; MAX_PATH as _];
    let len = unsafe { GetProcessImageFileNameW(process_handle, process_img_buffer.as_mut_slice()) };
    if len == 0 {
        event_log(&format!(
            "Failed to get process image for pid: {pid} from event information: {:?}. Win32 Error: {}",
                event_header.EventDescriptor,
                unsafe { GetLastError().0} ),
            EVENTLOG_ERROR_TYPE,
            EventID::GeneralError
        );
        return Err(());
    }

    let process_image: String = match String::from_utf16(&process_img_buffer) {
        Ok(mut s) => {
            s.truncate(len as _);
            s
        },
        Err(e) => {
            event_log(
                &format!(
                "Failed to convert image name to string for process: {pid} from event information: {:?}. Error: {e}",
                    event_header.EventDescriptor
                ),
                EVENTLOG_ERROR_TYPE,
                EventID::GeneralError
            );
            return Err(());
        },
    };

    Ok(process_image)
}
```

## Next steps

If you are following along - I would spend some time just flat out logging as much as you can to the event system (or a file) and making some really
rich prints of what ETW:TI is emitting.

If you havent been following along and want to have a go - I would recommend cloning my whole project at the
[commit e861d80](https://github.com/0xflux/Sanctum/tree/e861d80cf00317280d29b1add7b573778daae772), and getting yourself a self-signed ELAM certificate
[detailed in this blog post](https://fluxsec.red/creating-a-ppl-protected-process-light-in-rust-windows) and running it. I don’t think the driver needs to
be running (as I seem to get PPL execution without the driver running) so you don’t have to worry about environment config the driver / Sanctum project needs.
Basically, follow the instructions in my [blog post](https://fluxsec.red/creating-a-ppl-protected-process-light-in-rust-windows) and running **sanctum\_ppl\_runner**
will allow you to run the ETW:TI tracing!

For me, the next steps now are to implement these ETW events with my EDR, and start detecting malware - seeing if I can also find a clever way of tuning any false positives
in a way which can grow at scale.

As a reminder what this looks like in the event viewer when **malware.exe** tries to inject into **notepad.exe** (included in the Sanctum project):

![Detecting VirtualAllocEx EDR](https://fluxsec.red/static/images/rem_mem_etw.png)

Until next time, ciao!