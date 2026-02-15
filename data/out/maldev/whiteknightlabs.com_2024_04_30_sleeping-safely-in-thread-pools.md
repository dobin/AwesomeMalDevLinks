# https://whiteknightlabs.com/2024/04/30/sleeping-safely-in-thread-pools/

![White Knight Labs Training Bundle](https://whiteknightlabs.com/wp-content/uploads/2025/12/WKL_Click-Here_R1-01.jpg)[Full Bundle](https://buy.stripe.com/5kQcN55DFb5K8Rggfg9IQ0t "Full Bundle")[2 Class Bundle](https://buy.stripe.com/5kQbJ14zB7Ty8Rg9QS9IQ0y "2 Class Bundle")[3 Class Bundle](https://buy.stripe.com/fZu8wPc235Lq3wW0gi9IQ0x "3 Class Bundle")

[![White Knight Labs Logo](https://whiteknightlabs.com/wp-content/uploads/2024/08/Logo-v2.png)](https://whiteknightlabs.com/)

Menu

Edit Template

# Sleeping Safely in Thread Pools

- ghatcher
- April 30, 2024
- Uncategorized

_A thread pool is a collection of worker threads that efficiently execute asynchronous callbacks on behalf of the application. The thread pool is primarily used to reduce the number of application threads and provide management of the worker threads. Applications can queue work items, associate work with waitable handles, automatically queue based on a timer, and bind with I/O._

– [MSDN \| Thread Pools](https://learn.microsoft.com/en-us/windows/win32/procthread/thread-pools)

The red team community has developed a general awareness of the utility of thread pools for process injection on Windows. [Safebreach published detailed research last year](https://www.safebreach.com/blog/process-injection-using-windows-thread-pools/) describing how they may be used for remote process injection. White Knight Labs teaches the relevant techniques in our [Offensive Development training course](https://training.whiteknightlabs.com/offensive-development-training).

This blog post, however, discusses another use of thread pools that is relevant to red teamers: their use as an alternative to a sleeping main thread in a C2 agent or other post-exploitation offensive capability. This technique has been observed in use by real world threat actors before and is not a novel technique developed by myself or White Knight Labs. However, since we have not observed public discussion of the technique in red team communities, we have determined it to be a worthwhile topic that deserves more awareness. Let us now compare the standard technique of using a sleeping thread with this alternative option.

## The Problem with Sleeping Threads

C2 developers often face a dilemma where their agent must be protected while it is sleeping. It sleeps because it awaits new work. While the agent sleeps, all sorts of protections have been constructed to ward off dangerous memory scanners that may hunt it in its repose. Many of those mechanisms protect its memory, such as encryption of memory artifacts or ensuring the memory storage locations fly innocuous flags. Today we do not speak of memory protections, rather of threads and their call stacks.

Specifically, we are concerned about reducing the signature of our threads. The concern for which C2 developers delve into the complexities of call stack evasion is that their agent must periodically sleep its main thread. That main thread’s call stack may include suspicious addresses indicating how it came to be run. For example, code in some unbacked memory such as dynamically allocated shellcode may have hidden the C2 agent in safely image-backed memory before executing it. But the thread that ran that agent could still keep a call stack that includes an address in unbacked memory. Therefore the call stack must be “cleaned” in some way.

Using thread pools to periodically run functionality instead of a sleeping main thread avoids this issue. By creating a timer-queue timer (which uses thread pools to run a callback function on a timer), the main thread can allow itself to die safe in the knowledge that its mission of executing work will be taken up by the thread pool. Once the sleep period is completed, the thread pool will create a new thread and run whatever callback function it was setup for. This would likely be the “heartbeat” function that checks for new work. The thread pool will automatically create a new thread with a clean call stack or handoff the execution to an existing worker thread.

## Comparing the Code

Let us suppose we have a simple, mock C2 agent that includes the following simplified code:

```
void get_work() {
    std::cout << "Getting work from C2 server...\n";

	<...Snipped...>
}

void do_work() {
    std::cout << "Doing all the work that the red team operator tasked for me...\n";
}

void obfuscate() {
    std::cout << "Obfuscating memory before waiting again...\n";
}

void heartbeat(bool fromTimer) {

    if (fromTimer == true)
        std::cout << "Heartbeat from timer...\n";
    else
        std::cout << "Heartbeat from sleeper...\n";

    std::cout << "Current Thread ID: " << GetCurrentThreadId() << "\n";
    std::cout << "Hearbeat callstack:\n" << std::stacktrace::current() << "\n";

    get_work();
    do_work();

    obfuscate();
}
```

This part of our code is common between our two case studies. We have a `heartbeat` function that is called periodically after `SLEEP_PERIOD` amount of milliseconds. The `heartbeat` function checks for new work from the C2 server, executes it, and then sets up any obfuscation before it sleeps again.

We will use MDSec’s [BeaconHunter](https://github.com/3lp4tr0n/BeaconHunter/tree/main) and [Process Hacker](https://processhacker.sourceforge.io/) to inspect our process after using both techniques. BeaconHunter monitors for processes with threads in the `Wait:DelayExecution` state, tracks their behavior, and calculates a detection score that estimates how likely they are to be a beacon. It was designed to [demonstrate detection of Cobalt Strike’s implant BEACON](https://www.mdsec.co.uk/2022/07/part-2-how-i-met-your-beacon-cobalt-strike/#).

### Sleeping Thread Example

Now suppose our agent uses a sleeping thread to wait. The simplified code would look something like this:

```
DWORD WINAPI sleeper(_In_ LPVOID lpParameter) {
    while (true) {
        std::cout << "Sleeping for " << SLEEP_PERIOD << " milliseconds...\n";
        Sleep(SLEEP_PERIOD);
        heartbeat(false);
    }
}
```

That is the code that runs in our hypothetical C2 implant’s main thread. All it does is sleep and then run the `heartbeat` function once it wakes.

Now we’ll run our mock C2 agent and inspect it. With Process Hacker you can see that the main thread spends most of its time sleeping in the `Wait:DelayExecution` state.

![](https://whiteknightlabs.com/wp-content/uploads/2024/04/image-7-1024x867.png)

Now let’s take a look at what BeaconHunter thinks about us:

![](https://whiteknightlabs.com/wp-content/uploads/2024/04/image-6-1024x481.png)

BeaconHunter has observed our main sleeping thread, as well as our callbacks on the network, and decided that we are worthy of a higher score for suspicious behavior.

### Thread Pools Timer Example

Now let’s try rewriting our mock C2 implant to use a thread pool and timer instead.

```
// The timer callback must have this function signature
void CALLBACK ticktock(void*, BOOLEAN)
{
    heartbeat(true);
}

DWORD WINAPI timer(_In_ LPVOID lpParameter) {
    std::cout << "Setting timer for every " << SLEEP_PERIOD << " milliseconds...\n";

    // create the timer to run the hearbeat
    CreateTimerQueueTimer(&hTimer, NULL, ticktock, NULL, SLEEP_PERIOD, SLEEP_PERIOD, 0);

    // Use WT_TRANSFER_IMPERSONATION to ensure any impersonation we may have used in our current thread is persisted
    //CreateTimerQueueTimer(&hTimer, NULL, ticktock, NULL, SLEEP_PERIOD, SLEEP_PERIOD, WT_TRANSFER_IMPERSONATION);

    // Exit the thread that sets up the timer so that we can see that the heartbeat continues even without a sleeping thread
    ExitThread(0);

    // You could later delete the timer with:
    // DeleteTimerQueueTimer(NULL, hTimer, NULL);
}
```

In this example we use [`CreateTimerQueueTimer`](https://learn.microsoft.com/en-us/windows/win32/api/threadpoollegacyapiset/nf-threadpoollegacyapiset-createtimerqueuetimer) to create a timer-queue timer. When the timer expires every SLEEP\_PERIOD milliseconds our callback function `ticktock` will be executed by a thread pool worker thread. Once we have setup the timer, we exit our original thread to allow the timer to take over management of executing our heartbeat function.

Another option would be to trigger the callback on some kind of event rather than a timer. For that, you may use the `RegisterWaitForSingleObject`function.

Now that we have re-configured our mock C2 implant to use a thread pool, let’s inspect our process again with Process Hacker:

![Thread Pools](https://whiteknightlabs.com/wp-content/uploads/2024/04/image-4-1024x403.png)

This screenshot contains several interesting bits of information.

1. Our thread pool worker thread(s) that are running our callback function are waiting in the `Wait:WrQueue` state rather than `Wait:DelayExecution`.
2. Our start address for the thread(s) running our code is different. Rather than the start address being a main sleeping thread or some function that called it, the start address is instead `ntdll.dll!RtlClearThreadWorkOnBehalfTicket+0x70`. This is consistent for all of our worker threads. This is important because it means that any thread creation telemetry such as kernel callbacks or ETW events will show a thread creation record for our worker threads with a start address in `ntdll.dll` rather than the address of our callback function that is doing our C2 implant’s work. This is helpful for evading detections that monitor for creation of threads that run code in unbacked memory.
3. As such, our call stack is different. While our call stack does include our implant code during the execution of the callback function (shown on the right), our worker threads do not include any of our implant code in their call stack while they are waiting on the timer (shown on the left). Therefore do not have to do any of the call stack evasion that we may normally do for our sleeping thread.
4. The Thread ID changed between two of our heartbeats. This is because the thread pool manages which worker thread is used to run the callback function and it may occasionally switch the assigned thread. Therefore the suspicious behavior will not always run in the same thread. Keep in mind that this could affect some functionality in your C2 implant, such as impersonation. Refer to the [documentation](https://learn.microsoft.com/en-us/windows/win32/api/threadpoollegacyapiset/nf-threadpoollegacyapiset-createtimerqueuetimer) for `CreateTimerQueueTimer` on how to handle those issues.

Because the waiting state of our worker thread is not `Wait:DelayExecution`, BeaconHunter does not notice our process at all and it is absent in the list of possible beacons:

![](https://whiteknightlabs.com/wp-content/uploads/2024/04/image-5-1024x601.png)

## Which Thread Pool APIs Should You Use?

If you read the MSDN article [linked](https://learn.microsoft.com/en-us/windows/win32/procthread/thread-pools) at the top, then you will know that there are [two documented APIs](https://learn.microsoft.com/en-us/windows/win32/procthread/thread-pool-api) for thread pools. A “legacy” API and a “new” API. The legacy API was re-architected in Windows Vista before the new architecture thread pools were implemented entirely in usermode. Now they are managed in the kernel by the `TpWorkerFactory` object type and are exposed through the syscalls below:

- NtWorkerFactoryWorkerReady
- NtCreateWorkerFactory
- NtQueryInformationWorkerFactory
- NtReleaseWorkerFactoryWorker
- NtSetInformationWorkerFactory
- NtShutdownWorkerFactory
- NtWaitForWorkViaWorkerFactory

In our example, we use the legacy API call `CreateTimerQueueTimer` for the sake of backwards-compatibility. The new API is more flexible and may be a more desirable option if you expect to only run your C2 implant on newer versions of Windows than Vista. If you are writing a C2 agent using thread pools, then you will need to be aware of how these APIs have changed over time and the reliability considerations of using them on different versions of Windows.

For the most part, the Safebreach blog post covers the relevant NT APIs for Thread Pools in enough detail that we do not need to cover them here. As an extra challenge, you could implement this technique entirely using those syscalls. But that is out of scope for this introductory blog post. And, since there is not anything necessarily suspicious about the use of thread pool APIs, it is questionable whether limiting your API use to the syscalls provides a significant OpSec advantage.

## Thread Pool OpSec

Speaking of OpSec, we should ask the question at this point: Does this technique result in a more OPSEC friendly method of sleeping your implant?

My answer is yes—with a caveat. Our use of thread pools to run our code is by no means undetectable. It simply has _different_ indicators than the standard technique of using a sleeping thread. It does not _lack_ indicators.

For example, an EDR could inspect the context of `TpWorkerFactory`objects or worker threads to discover the specified callback function. This would let it observe what code thread pools are actually executing.

So yes, in the current state of tradecraft, this approach has relatively novel indicators compared to a sleeping thread and that is an advantage. Time will prove whether those differences remain advantages or merely variety.

#### Recent Posts

- [Backdooring Electron Applications](https://whiteknightlabs.com/2026/01/20/backdooring-electron-applications/)
- [UEFI Vulnerability Analysis Using AI Part 3: Scaling Understanding, Not Just Context](https://whiteknightlabs.com/2026/01/13/uefi-vulnerability-analysis-using-ai-part-3-scaling-understanding-not-just-context/)
- [The New Chapter of Egress Communication with Cobalt Strike User-Defined C2](https://whiteknightlabs.com/2026/01/06/the-new-chapter-of-egress-communication-with-cobalt-strike-user-defined-c2/)
- [UEFI Vulnerability Analysis using AI Part 2: Breaking the Token Barrier](https://whiteknightlabs.com/2025/12/30/uefi-vulnerability-analysis-using-ai-part-2-breaking-the-token-barrier/)
- [Just-in-Time for Runtime Interpretation - Unmasking the World of LLVM IR Based JIT Execution](https://whiteknightlabs.com/2025/12/23/just-in-time-for-runtime-interpretation-unmasking-the-world-of-llvm-ir-based-jit-execution/)

#### Recent Comments

### Let’s Chat

#### Strengthen your digital stronghold.

![desigen](https://whiteknightlabs.com/wp-content/uploads/2024/08/desigen-1.png)

Reach out to us today and discover the potential of bespoke cybersecurity solutions designed to reduce your business risk.

What is 5 + 5 ? ![Refresh icon](https://whiteknightlabs.com/wp-content/plugins/ds-cf7-math-captcha/assets/img/icons8-refresh-30.png)![Refreshing captcha](https://whiteknightlabs.com/wp-content/plugins/ds-cf7-math-captcha/assets/img/446bcd468478f5bfb7b4e5c804571392_w200.gif)

Answer for 5 + 5

reCAPTCHA

[![footer logo](https://whiteknightlabs.com/wp-content/uploads/2024/08/footer-logo.png)](https://whiteknightlabs.com/)

[Linkedin-in](https://www.linkedin.com/company/white-knight-labs/)[X-twitter](https://twitter.com/WKL_cyber)[Discord](https://discord.gg/qRGBT2TcEV)

#### [Call: 877-864-4204](tel:877-864-4204)

#### [Email: sales@whiteknightlabs.com](mailto:sales@whiteknightlabs.com)

#### [Send us a message](https://whiteknightlabs.com/2024/04/30/sleeping-safely-in-thread-pools/\#chat)

#### Assessment

- [VIP Home Security](https://whiteknightlabs.com/vip-home-cybersecurity-assessments)
- [Password Audit](https://whiteknightlabs.com/password-audit-service)
- [Embedded Devices](https://whiteknightlabs.com/embedded-security-testing)
- [OSINT](https://whiteknightlabs.com/osint-services)
- [AD Assessment](https://whiteknightlabs.com/active-directory-security-assessment)
- [Dark Web Scanning](https://whiteknightlabs.com/dark-web-scanning)
- [Smart Contract Audit](https://whiteknightlabs.com/smart-contract-audit)

#### Penetration Testing

- [Network Penetration Test](https://whiteknightlabs.com/network-penetration-testing-services)
- [Web App Penetration Test](https://whiteknightlabs.com/web-application-penetration-testing)
- [Mobile App Penetration Test](https://whiteknightlabs.com/mobile-application-penetration-testing)
- [Wireless Penetration Test](https://whiteknightlabs.com/wireless-penetration-testing)
- [Cloud Penetration Test](https://whiteknightlabs.com/cloud-penetration-testing)
- [Physical Penetration Testing](https://whiteknightlabs.com/physical-penetration-testing/)

#### Simulation and Emulation

- [Red Team – Adversarial Emulation](https://whiteknightlabs.com/red-team-engagements)
- [Social Engineering Attack Simulation](https://whiteknightlabs.com/social-engineering-testing)
- [Ransomware Attack Simulation](https://whiteknightlabs.com/ransomware-attack-simulation)

#### Compliance and Advisory

- [Framework Consulting](https://whiteknightlabs.com/framework-consulting)
- [Gap Assessments](https://whiteknightlabs.com/gap-assessments)
- [Compliance-as-a-Service](https://whiteknightlabs.com/compliance-as-a-service-caas)
- [DevSecOps Engineering](https://whiteknightlabs.com/devsecops-engineering)

#### Incident Response

- [Incident Response](https://whiteknightlabs.com/incident-response)

#### Copyright © 2026 White Knight Labs \| All rights reserved

#### [Contact Us](https://whiteknightlabs.com/contact-us/)

Edit Template

![](https://whiteknightlabs.com/2024/04/30/sleeping-safely-in-thread-pools/)

![](https://whiteknightlabs.com/2024/04/30/sleeping-safely-in-thread-pools/)

reCAPTCHA