# https://fluxsec.red/ghost-hunting-open-process

# Ghost hunting OpenProcess

A look at the Ghost Hunting technique for detecting stealthy malware that bypasses syscall hooks in EDR environments. This post focuses on detecting OpenProcess abuse by correlating syscall hooks and kernel events.

* * *

## Intro

If you are not already following the project - you can check it out on [GitHub](https://github.com/0xflux/Sanctum/), and I would recommend you read my previous Ghost Hunting articles,
particularly [this one](https://fluxsec.red/edr-syscall-hooking).

So, up unto this point, we have managed to create [syscall stub hooks](https://fluxsec.red/implementing-syscall-hooking-rust) in the EDR which alter execution flow to an injected DLL of our making to inspect arguments being passed into the
function. Ghost Hunting is my technique in which we look to spot malware evading syscall hooks in environments where EDR operate. We are
also able to communicate with the engine via [IPC](https://fluxsec.red/communicating-from-hooked-syscall-rust) (interprocess communication), all with Rust.

Now we need to look at the logic for how Ghost Hunting works - as mentioned in my previous post, doing so in an OpenProcess hook is a little difficult and will not be **0 ms** detection speed, instead it will be within a predefined time window
which I have set (for now) as `600 ms`. This is quite slow in terms of execution speed - but OpenProcess is only at the **start** of the chain for process injection that we are trying to combat (as our first overall technique), and there
are better opportunities later down the line where I think Ghost Hunting will really shine as a technique (as mentioned [here](https://fluxsec.red/edr-syscall-hooking#ghost-hunting)).

**One foreseeable problem** with this by itself, is that a malware loader will have been and gone by the time 600 ms rolls around. I have two rebuttals to this; primarily - we can delay execution of CreateRemoteThread / APC Queue Hijacking techniques
until the ghost hunting technique has closed the 600 ms window; secondary - this technique is still valid in a sandbox environment where you can wait these time delays for the ghost hunting period to close.

## The logic

So for **OpenProcess**, we have the function **ZwOpenProcess** hooked (you can see it in action in my [YouTube video](https://www.youtube.com/watch?v=I2krfjCsRp0)). We need to think about how Ghost Hunting can spring into
action to detect syscall abuse.

The current problem I see with this, if we were to move the logic into the driver so that we will **only** issue a handle when our DLL usermode syscall stub signals the **syscall**, we will enter a time where we are potentially
spinning system threads waiting for the ‘approval’ to come from usermode.

Alternatively, what if we sent an IOCTL from our syscall hook to the kernel before we call **syscall**; in principal this sounds okay - however, I can see this leading to race conditions - equally, when a driver gets a handle to something
via **ObOpenObjectByPointer**, our callback routine is triggered. In that case, no usermode “this pid is opening a handle” will be received and we may quickly enter undefined behaviour.

So, **my approach** here is to use this as a logging function for userland, raising the risk score if within a specified time period a handle (via driver interception) does not match up with a hooked syscall IPC message.

Given the risk score is raised by this behaviour, we have other opportunities slightly later to catch malware trying to do bad things, in places where we probably can justify a little delay in an action happening.
Catching handles is too noisy. There are simply too many, making it impractical to justify delaying system execution based solely on handle creation.

So, diagrammatically the **ghost hunting** process for OpenProcess will look like:

![Ghost Hunting EDR Technique Open Process diagram Rust Windows EDR Driver](https://fluxsec.red/static/images/edr_ghost_open_proc.jpg)

Ultimately, we have two inputs (one from the driver, one from the hooked syscall via our DLL) - event receivers are in place in the **core** module of the EDR, which then pass the data through to **process\_monitor** which is responsible for
tracking process data.

Every loop ( **20 ms**) the function **poll\_ghost\_timer** will be run, which determines whether there’s been too much time between one input and another; essentially
saying - **if we do not receive both inputs within x amount of time, we are declaring that suspicious**. This will likely require some tweaking, but currently the period is set to **600 ms**.

## Rust channels

So, looking to the implementation of this; we first need a way of doing something with the IPC message from the hooked syscall (if this is foreign to you, check my [previous blog post](https://fluxsec.red/communicating-from-hooked-syscall-rust)).

To do this, we will use channels, which we can use via Tokio, to pass messages between threads or Tokio tasks. An **mpsc channel** is basically a tuple containing a transmitter, and receiver, where we can send data from one task / thread via the
transmitter, to the receiver.

Let’s implementing this in the **core** module of the EDR. Before the main event loop, we create a new `mpsc::channel` like so:

```rust
let (tx, mut rx) = mpsc::channel(1000);
```

So here we simply specify the transmitter, **tx**, and receiver **rx**, setting the channels capacity to 1000.

Next, we move the transmitter into the task like so:

```rust
tokio::spawn(async {
    run_ipc_for_injected_dll(tx).await;
});
```

This function is going to loop waiting for IPC messages from our hooked syscalls in foreign processes. Inside of `run_ipc_for_injected_dll` we need to Arc and clone the transmitter (as it involves some move semantics across tokio tasks / threads),
and then we can use that (it will be called **tx\_cl**) to send some received data from the IPC.

```rust
pub async fn run_ipc_for_injected_dll(
    tx: Sender<OpenProcessData>
) {
    let tx_arc = Arc::new(tx);
    loop {
        let tx_cl = Arc::clone(&tx_arc);

        // ... got an IPC connection so make a new task to deal with it
        tokio::spawn(async move {
            // ... read the data as per the previous blog post, then send it out of the task / thread via mpsc
            tx_cl.send(open_process_data).await;
        }
    }
}
```

Once `tx_cl.send(open_process_data).await` completes, our receiver will be able to get the data and do something with it.

### Receiver

So on the receiver, back in the core, in the event loop, we can try receive data. If there is no data to receive, it will simply continue execution to the next thing. If it does receive data, then we can do something with it. That looks like
so (we have to get a lock to **self.process\_monitor** as it is wrapped in an **RwLock**):

```rust
//
// Enter the polling & decision making loop, this here is the core / engine of the usermode engine.
//
loop {
    // See if there is a message from the injected DLL
    if let Ok(open_process_data) = rx.try_recv() {
        let mut lock = self.process_monitor.write().await;
        lock.ghost_hunt_open_process_add(open_process_data.pid as u64, ApiOrigin::SyscallHook);
    }

    // ...
}
```

## Receiving the event from the driver

Equally, in the same event loop in **core**, we see if we have any new handle notifications from the driver, and if so, deal with those:

```rust
// process all handles
if !driver_messages.handles.is_empty() {
    for item in driver_messages.handles {
        self.process_monitor.write().await.add_handle_driver_notified(
            item.source_pid,
            item.dest_pid,
            item.rights_given,
            item.rights_desired,
        );
    }
}
```

## Ghost Hunting

The actual logic for **add\_handle\_driver\_notified** isn’t all that interesting, essentially it itself calls **ghost\_hunt\_open\_process\_add**; which will add the event to an internal structure
tracking the event, importantly with an enum identifying whether the event was emitted from the syscall hook, or the driver. This way we can make equal matches for the events; otherwise one easy
EDR bypass technique for this would be for malware to directly call the SSN for opening a process twice; cancelling out each other without proper integrity.

Note, we use **SystemTime** as this is serialisable via Serde, whereas **Instant** isn’t (if memory serves me correctly).

The implementation is as follows:

```rust
impl ProcessMonitor {
    pub fn ghost_hunt_open_process_add(&mut self, pid: u64, syscall_origin: ApiOrigin) {
        if let Some(process) = self.processes.get_mut(&pid) {
            //
            // If the timers are empty; then its the first in so we can add it to the list straight up.
            // Else, we will look for a match on the type; if we
            //
            if process.ghost_hunting_timers.is_empty() {
                process.ghost_hunting_timers.push(GhostHuntingTimers {
                    pid: pid as u32,
                    timer: SystemTime::now(),
                    syscall_type: SyscallType::OpenProcess,
                    origin: syscall_origin,
                });
            } else {
                let mut index: usize = 0;
                for timer in &mut process.ghost_hunting_timers {
                    match syscall_origin {
                        //
                        // If the origin was from the kernel, then we are looking to match on an inbound equivalent
                        // notification from a hooked syscall; and vice-versa for if the first notification came from a
                        // syscall.
                        // If that condition is true; then remove that item from the queue. If not - do not remove and add
                        // a new queued item. The timers will then catch any bad state.
                        // We want to return out of this operation once it has completed. If there was not a successful match
                        // then add it - the timer will take care of the ghost hunting process.
                        //
                        ApiOrigin::Kernel => {
                            if timer.origin == ApiOrigin::SyscallHook && timer.syscall_type == SyscallType::OpenProcess {
                                let _ = process.ghost_hunting_timers.remove(index);
                                return;
                            }
                        },
                        ApiOrigin::SyscallHook => {
                            if timer.origin == ApiOrigin::Kernel && timer.syscall_type == SyscallType::OpenProcess {
                                let _ = process.ghost_hunting_timers.remove(index);
                                return;
                            }
                        },
                    }

                    index += 1;
                }

                // we did not match, so add the element
                process.ghost_hunting_timers.push(GhostHuntingTimers {
                    pid: pid as u32,
                    timer: SystemTime::now(),
                    syscall_type: SyscallType::OpenProcess,
                    origin: syscall_origin,
                });
            }
        } else {
            // todo ok something very wrong if this gets called!!
            let log = Log::new();
            log.log(LogLevel::NearFatal, "Open Process from DLL request made that can not be found in active process list.");
        }

    }
}
```

## Polling for the Ghost Hunting technique

As mentioned we do poll the Ghost Hunt timer; what we want to do is check both a signal from the driver and a signal from the hooked syscall
were received within some defined period of time. If not, this is a sign of badness.

We enumerate each process we track in the **ProcessMonitor**, and check for active timers.

```rust
impl ProcessMonitor {
    pub fn poll_ghost_timer(&mut self) {
        //
        // For each process we are tracking; determine if any timers are active from syscall stubs. If no timers are active then
        // we can simply ignore them. If they are active, then we should have received a driver notification matching the event
        // the syscall hooked within that time frame. If no such event is received; something untoward is going on, and as such,
        // elevate the risk score of the process.
        //

        const MAX_WAIT: Duration = Duration::from_millis(600);

        for (_, process) in self.processes.iter_mut() {
            //
            // In here process each hooked syscall where we expect an emission from the kernel
            //
            if !process.ghost_hunting_timers.is_empty() {
                let mut index: usize = 0; // index of iterator over the ghost timers
                for item in &process.clone().ghost_hunting_timers {
                    if let Ok(t) = item.timer.elapsed() {
                        if t > MAX_WAIT {
                            process.update_process_risk_score(SyscallType::OpenProcess as i16);
                            process.ghost_hunting_timers.remove(index);
                            println!("******* RISK SCORE RAISED AS TIMER EXCEEDED");
                            break;
                        }
                    }

                    index += 1;
                }
            }
        }
    }
}
```

## Challenge to other security researchers

If you are reading this as a security researcher / professional; I’d love you to try figure out a way around this detection mechanism. If you do experiment with this and find
a way around it, please get in touch via [Twitter](https://x.com/0xfluxsec) or email me at **fluxsec@proton.me**, as I would love to see this mechanism bypassed so I can carry on
improving the detection logic / Ghost Hunting technique! (If accepting this challenge, either do it hypothetically, or if you want to run it against the EDR set a small sleep before
your payload runs as the DLL is mapped ~ 60 - 120 ms after a process called “malware.exe” starts - i need to hard map the DLL in earlier, that is todo soon. Also, if you are testing
against the edr, make sure your payload has “malware” in its file name).

This should detect hells gate, direct/indirect syscalls and remapping NTDLL.