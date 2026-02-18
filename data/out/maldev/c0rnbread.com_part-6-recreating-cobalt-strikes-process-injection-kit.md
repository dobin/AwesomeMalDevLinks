# https://c0rnbread.com/part-6-recreating-cobalt-strikes-process-injection-kit/

# Background

Process injection or code injection is a technique in which you copy and execute arbitrary code to a target process. It is often used in Offensive Security to execute tasks under the context of another legitimate process on the system.

Before this blog my Mythic C2 agent, [Xenon](https://github.com/MythicAgents/Xenon?ref=c0rnbread.com), only implemented process injection for executing .NET assemblies in-memory, but I planned on using it for post-ex commands going forward.

Since malware has used process injection for decades, this is going to be one of the most suspicious things Xenon will need to do. It’s an easy detection/signature point, especially for an open-source tool like this one. That is why I wanted to support user-defined process injection methods.

Obviously, users could always edit the agent’s source code directly and change the default process injection method, but I wanted to tackle the challenge of supporting previously written kits.

Something like Cobalt Strike’s _Process Injection Kit_.

# Why Inject?

Let’s just get this part out of the way.

So why do we want to do process injection in the first place? The original thinking behind doing remote process injection was to “protect” the main beaconing process from crashing and disperse memory artifacts away from its own process.

**Without process injection**

- You have a C2 beacon running in `a.exe`.
- The operator runs a `mimikatz` task.
- The agent tries to execute it, but it crashes or gets detected.
- Result: `a.exe` dies and you lose your entire foothold.

**With process injection**

- The beacon is still running in `a.exe`.
- The operator runs a `mimikatz` task.
- Instead of executing inside itself, `a.exe` injects mimikatz’s position-independent code into `legit.exe`.
- If `legit.exe` crashes, the task fails but `a.exe` is still alive and beaconing.

# Cobalt Strike - Process Injection Kit

The Process Injection Kit in CS is a feature that implements two “hook” functions for post-exploitation commands that use post-ex DLLs.

_Hooks allow Aggressor Script to intercept and change Cobalt Strike behavior._

The two hooks in CS are [PROCESS\_INJECT\_SPAWN](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_hooks.htm?ref=c0rnbread.com#PROCESS_INJECT_SPAWN) and [PROCESS\_INJECT\_EXPLICIT](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_hooks.htm?ref=c0rnbread.com#PROCESS_INJECT_EXPLICIT).

`PROCESS_INJECT_SPAWN` \- spawns a temporary process and then injects into it.

`PROCESS_INJECT_EXPLICIT` \- injects into an already running process.

If using the process injection kit, these hook functions override the default process injection technique. It basically allows the operator to define custom injection functionality to avoid detections/signatures.

## Spawn Injection Commands

In Cobalt Strike, specific commands use the fork & run technique. The main purpose for this is to ‘protect’ the beacon from crashing or detection. Although in today’s world I think fork & run is probably going to hurt you on detections.

| **Beacon Command** | **Aggressor Script function** | **UI Interface** |
| --- | --- | --- |
| chromedump |  |  |
| dcsync | &bdcsync |  |
| elevate | &belevate | \[beacon\] -> Access -> Elevate |
|  |  | \[beacon\] -> Access -> Golden Ticket |
| hashdump | &bhashdump | \[beacon\] -> Access -> Dump Hashes |
| keylogger | &bkeylogger |  |
| logonpasswords | &blogonpasswords | \[beacon\] -> Access -> Run Mimikatz |
|  |  | \[beacon\] -> Access -> Make Token (use a hash) |
| mimikatz | &bmimikatz |  |
|  | &bmimikatz\_small |  |
| net | &bnet | \[beacon\] -> Explore -> Net View |
| portscan | &bportscan | \[beacon\] -> Explore -> Port Scan |
| powerpick | &bpowerpick |  |
| printscreen | &bprintscreen |  |
| pth | &bpassthehash |  |
| runasadmin | &brunasadmin |  |
|  |  | \[target\] -> Scan |
| screenshot | &bscreenshot | \[beacon\] -> Explore -> Screenshot |
| screenwatch | &bscreenwatch |  |
| ssh | &bssh | \[target\] -> Jump -> ssh |
| ssh-key | &bssh\_key | \[target\] -> Jump -> ssh-key |
|  |  | \[target\] -> Jump -> \[exploit\] (use a hash) |

Commands that support the `PROCESS_INJECT_SPAWN` hook in 4.5

## Explicit Injection Commands

Explicit injection doesn’t spawn a temporary process, but injects into an already existing process on the target host.

| **Beacon Command** | **Aggressor Script function** | **UI Interface** |
| --- | --- | --- |
| browserpivot | &bbrowserpivot | \[beacon\] -> Explore -> Browser Pivot |
| chromedump |  |  |
| dcsync | &bdcsync |  |
| dllinject | &bdllinject |  |
| hashdump | &bhashdump |  |
| inject | &binject | \[Process Browser\] -> Inject |
| keylogger | &bkeylogger | \[Process Browser\] -> Log Keystrokes |
| logonpasswords | &blogonpasswords |  |
| mimikatz | &bmimikatz |  |
|  | &bmimikatz\_small |  |
| net | &bnet |  |
| portscan | &bportscan |  |
| printscreen |  |  |
| psinject | &bpsinject |  |
| pth | &bpassthehash |  |
| screenshot |  | \[Process Browser\] -> Screenshot (Yes) |
| screenwatch |  | \[Process Browser\] -> Screenshot (No) |
| shinject | &bshinject |  |
| ssh | &bssh |  |
| ssh-key | &bssh\_key |  |

Commands that support the `PROCESS_INJECT_EXPLICIT` hook in 4.5

# Mythic Implementation

### Disclaimer

It should be stated that in modern C2 implants there has been a big shift away from the fork & run technique to in-process execution. Most modern implants rely heavily on in-process execution of BOF files. This is because fork & run is “louder” from an events perspective, because it involves remote process injection which has become increasingly more detectable.

So why did I bother reimplementing Process Injection Kit at all?

Really for these purposes:

- Learn about it’s implementation in Cobalt Strike.
- Provide the option to use your own process injection techniques without modifying Xenon’s code base.

BOF files do have some key advantages over fork & run:

- A plethora of open-source examples
- Rapid development
- Small memory footprint
- In-process execution

## Default Injection

Xenon’s default injection method is a basic APC injection, a very well signatured behavior that will most likely be flagged by AV engines (but maybe not ).

## Register Kit

To start, I introduced a new Mythic command, `register_process_inject_kit`, to the Xenon agent. It allows you to upload a custom process injection kit into Xenon.

Process Injection Kit's are implemented as Beacon Object Files (BOFs) and uploaded through the modal.

Currently only `PROCESS_INJECT_SPAWN` behavior is supported which spawns a **new** sacrificial process to perform process injection.

For now, it takes two arguments `--enabled` and `--inject_spawn`.

- `--enabled` \- Enables **ALL** Xenon payloads to use the custom injection method.
- `--inject_spawn` \- Saves a BOF file as the new injection kit.

Once your kit is registered all supported commands will use the BOF to perform injection.

### Commands

Currently these are the only commands that will be overridden by the process injection kit.

- `execute_assembly`
- `mimikatz`

## The Pipe Problem

At this point in the implementation I found myself stuck in a pickle.

1. User uploads their BOF (kit) with `register_process_inject_kit`
2. User runs a fork & run command
3. Server sends command to agent
4. Agent executes kit to inject shellcode into remote process

How do we get the output from a remote process?

Previously this was easy because we controlled the code that spawned the remote process and could use _anonymous pipes_ to get the process’s output. But now the user controls the spawning functionality in their BOF.

I thought, well, their BOF can use the internal BeaconAPIs I’ve defined like `BeaconSpawnTemporaryProcess` , so should I just modify that to use an anonymous pipe?

But then the calling code (their code) would need to pass a handle to the function then check it for output.

I could modify the function to use a named pipe, but then what if they don’t use the BeaconAPIs to spawn the sacrificial process? Then they wouldn’t get any output still.

Unfortunately this would make my implementation incompatible with people’s already existing Process Injection Kits.

**More shellcoding…**

To avoid this I did something wacky, that turned out to be similar to what Cobalt Strike did.

I created a PIC stub which gets prepended to all post-ex PIC that does the following:

1. Walks the Process Environment Block (PEB) to find the addresses for `CreateFileA` and `SetStdHandle`
2. Calls `CreateFileA` to create a named pipe with a known string
3. Calls `SetStdHandle` to set the stdout and stderr in the _current process_ to the named pipe
4. Jumps to the next block of shellcode

Now when the post-ex PIC executes in that process it will write all output to our named pipe. In our main beacon process we can just read data from that named pipe until there’s none left.

xenon → injects stub+shellcode → stub sets output to `\\\\.\\pipe\\something`→ shellcode executes

I discovered this was similar to how Cobalt Strike implements output retrieval from remote processes. The difference is they do not use donut-shellcode, but instead a custom PIC DLL reflective loader (DRL) that sets the output in the current process to a named pipe.

beacon → injects DRL+DLL→ DRL sets output to `\\\\.\\pipe\\something` → DLL executes

## Development

If you want to write your own process injection kit refer to Cobalt Strike’s [documentation](https://www.cobaltstrike.com/blog/process-injection-update-in-cobalt-strike-4-5?ref=c0rnbread.com).

Here is a simple example:

```c
#include <windows.h>
#include "beacon.h"

/* is this an x64 BOF */
BOOL is_x64() {
#if defined _M_X64
   return TRUE;
#elif defined _M_IX86
   return FALSE;
#endif
}

/* See gox86 and gox64 entry points */
void go(char * args, int alen, BOOL x86) {
   STARTUPINFOA        si;
   PROCESS_INFORMATION pi;
   datap               parser;
   short               ignoreToken;
   char *              dllPtr;
   int                 dllLen;

   /* Warn about crossing to another architecture. */
   if (!is_x64() && x86 == FALSE) {
      BeaconPrintf(CALLBACK_ERROR, "Warning: inject from x86 -> x64");
   }
   if (is_x64() && x86 == TRUE) {
      BeaconPrintf(CALLBACK_ERROR, "Warning: inject from x64 -> x86");
   }

   /* Extract the arguments */
   BeaconDataParse(&parser, args, alen);
   ignoreToken = BeaconDataShort(&parser);
   dllPtr = BeaconDataExtract(&parser, &dllLen);

   /* zero out these data structures */
   __stosb((void *)&si, 0, sizeof(STARTUPINFO));
   __stosb((void *)&pi, 0, sizeof(PROCESS_INFORMATION));

   /* setup the other values in our startup info structure */
   si.dwFlags = STARTF_USESHOWWINDOW;
   si.wShowWindow = SW_HIDE;
   si.cb = sizeof(STARTUPINFO);

   /* Ready to go: spawn, inject and cleanup */
   if (!BeaconSpawnTemporaryProcess(x86, ignoreToken, &si, &pi)) {
      BeaconPrintf(CALLBACK_ERROR, "Unable to spawn %s temporary process.", x86 ? "x86" : "x64");
      return;
   }
   BeaconInjectTemporaryProcess(&pi, dllPtr, dllLen, 0, NULL, 0);
   BeaconCleanupProcess(&pi);
}

void gox86(char * args, int alen) {
   go(args, alen, TRUE);
}

void gox64(char * args, int alen) {
   go(args, alen, FALSE);
}
```

**IMPORTANT** \- The BOF injection kit must parse two arguments passed from Mythic, regardless if it uses them:

`ignoreToken` \- Boolean value that Xenon doesn’t use yet, but still needs to be there.

`dllPtr` \- A pointer to the beginning of the shellcode being executed.

The example code above is essentially the same behavior as Xenon's default process injection method. It can be easily modified to change the injection behavior to something custom, and that's where the advantage is.

Using `register_process_inject_kit` the injection behavior can be changed at any point in the running payload without compiling a new payload.

You can compile the example BOF with the following:

```bash
x86_64-w64-mingw32-gcc -o inject_spawn.x64.o -c inject_spawn.c
```

Then register the new kit with the `register_process_inject_kit` command to the Mythic server.

![](https://c0rnbread.com/content/images/2025/09/image.png)`register_process_inject_kit` command

Now all supported commands will use your new process injection behavior!

![](https://c0rnbread.com/content/images/2025/09/image-1.png)Injecting .NET assembly shellcode

### Examples

If your like me, you might just want to use some publicly available kits out there.

Here are some real-world examples of modified injection kits:

- [InjectKit](https://github.com/REDMED-X/InjectKit?ref=c0rnbread.com) \- Indirect syscalls via the Tartarus Gate method.
- [secinject](https://github.com/apokryptein/secinject?ref=c0rnbread.com) \- Section Mapping Process Injection (secinject): Cobalt Strike BOF
- [CB\_process\_Inject](https://github.com/vgeorgiev90/CB_process_Inject?ref=c0rnbread.com) \- A simple process injection kit for cobalt strike based on syscalls

## Wrapping Up

I mostly went through this process, because I thought the idea of swapping out process injection methods on the fly was cool.

Practically speaking I would probably opt for in-process BOF execution on a real engagement.

## Read more

[**Part 5: Cough Cough 🤧** \\
\\
Adding a COFF loader, Cobalt Strike BOFs, crashing and crashing\\
\\
Intro\\
\\
BOFs might be the most popular format for post-exploitation tooling in the cyber space. There are a bunch of reasons for that which we will discuss below.\\
\\
So I really wanted Xenon to be compatible with the plethora of](https://c0rnbread.com/part-5-cough-cough/)[**Part 4: Getting an Upgrade ⚒️** \\
\\
yes… i named this one after the minecraft achievement.\\
\\
The Httpx container, malleable C2 profiles, and wininet.\\
\\
Flexible Request Profiles\\
\\
To be honest, this is where I spent the bulk of my development for this project.\\
\\
Up to this point, the http C2 profile served it’s purpose and allowed](https://c0rnbread.com/part-4-getting-an-upgrade/)[**Part 3: Doing a Task** \\
\\
Mythic request types (checkin & get\_tasking & post\_response)\\
\\
Getting Tasks\\
\\
Now that we performed an initial check-in to the teamserver, we (the agent) need to continuously check for new tasks to execute. In Mythic this can be done with a get\_tasking request. The format for this style](https://c0rnbread.com/part-3-doing-a-task/)[**Part 2: Getting a Callback** \\
\\
translation containers and checking in\\
\\
Agent\\
\\
Data Serialization\\
\\
I decided to build off of the Talon agent by @Cracked5pider. It uses a data serialization format “type, size, data” to pack and parse data. This allows the agent to send serialized binary data instead of worrying about creating JSON in C](https://c0rnbread.com/part-2-getting-a-callback/)