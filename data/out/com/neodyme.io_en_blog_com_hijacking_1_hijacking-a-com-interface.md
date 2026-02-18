# https://neodyme.io/en/blog/com_hijacking_1/#hijacking-a-com-interface

Authored by:

- [Alain](https://neodyme.io/en/blog/author/alain) [x](https://x.com/0x4d5aC) [bluesky](https://bsky.app/profile/0x4d5a.bsky.social) [linkedin](https://www.linkedin.com/in/alain-r%C3%B6del-27ab42272/) [email](mailto:alain@neodyme.io)
- [Kolja](https://neodyme.io/en/blog/author/kolja) [linkedin](https://www.linkedin.com/in/kolja-grassmann-947b112b9/) [email](mailto:kolja@neodyme.io)

## Introduction [¶](https://neodyme.io/en/blog/com_hijacking_1/\#introduction)

Antivirus (AV) and Endpoint Detection and Response (EDR) products are critical in securing systems in enterprise environments or personal setups.
These products are designed to protect devices, but their widespread use — particularly in enterprises — means vulnerabilities in these products can significantly impact overall security.
We previously analyzed [Wazuh](https://neodyme.io/en/blog/wazuh_rce/) and found vulnerabilities that would have allowed lateral movement in the organization’s network.
In this series, we will discuss how we identified vulnerabilities in multiple security products that could, in theory, allow privilege escalation to `SYSTEM` on millions of devices, assuming initial access was gained.
We will introduce the general design of the targeted security products to give you some background information on the mechanisms that allowed us to escalate our privileges.

We also held a talk about this blog content at the 38c3 conference in Hamburg, Germany. You can find the talk (in German) and slides (English) at the very end of this blogpost.


![An overview of the CVEs we found during this research](https://neodyme.io/blog/com_hijacking_1/cve_list.png)

An overview of the CVEs we found during this research


## Technical Background [¶](https://neodyme.io/en/blog/com_hijacking_1/\#technical-background)

All the security products we examined include a user interface, which typically allows users to perform actions such as triggering filesystem scans, initiating updates, or modifying settings like excluded files.
For example, setting an exclusion should require high privileges to prevent malware from excluding itself from scans.
However, the user interface usually operates in the context of the user executing it. Especially in an enterprise setting, this user often lacks high privileges, as granting such privileges would violate good security practices.

### How does a low-privileged user change settings? [¶](https://neodyme.io/en/blog/com_hijacking_1/\#how-does-a-low-privileged-user-change-settings)

Since the user interface cannot directly perform privileged actions, such as setting exclusions, a separate system process with higher privileges is required to execute these changes on behalf of the user interface.
In our analysis, we will refer to:

- The user interface as the _front-end process_.
- The highly privileged system process as the _back-end process_.

To coordinate actions, the front-end process must communicate with the back-end process. Depending on the product, this communication occurs through named pipes, Remote Procedure Calls (RPC), or Component Object Model (COM) interfaces.
Across all products we examined, the back-end process ran with `SYSTEM` privileges.

### Security risks in back-end communication [¶](https://neodyme.io/en/blog/com_hijacking_1/\#security-risks-in-back-end-communication)

A natural concern arises:
Could malware abuse this communication to perform privileged actions?
If malicious software could directly interact with the back-end process, it could exploit this pathway to, for example, modify the registry or other sensitive settings.

To mitigate this, security products typically verify that actions initiated by the back-end process originate from a trusted source.
For example, they might check the signature of the executable initiating communication.

However, this safeguard is insufficient on its own, as Windows lacks strict boundaries between processes running under the same user account.
A process can read or write to the memory of other processes in the same user context.
It can even execute code within those processes.
As a result, malware could potentially hijack a trusted process to abuse its connection with the back-end process.

### Protections against code injection [¶](https://neodyme.io/en/blog/com_hijacking_1/\#protections-against-code-injection)

To address this risk, security vendors implement additional protections to secure the front-end process:

- **Filter Drivers**: These intercept system calls and prevent handles with privileges that could allow code injection from being created for the front-end process. This measure blocks many common code injection techniques, often relying on acquiring such handles.
- **DLL Allowlist Validation**: During our testing, we observed measures that verify the location of loaded DLLs against an allowlist to prevent loading of untrusted DLLs.

These defences significantly reduce the risk of untrusted code injection.

### Communication between front-end and back-end processes [¶](https://neodyme.io/en/blog/com_hijacking_1/\#communication-between-front-end-and-back-end-processes)

The diagram below illustrates the components involved in the communication between front-end and back-end processes:

![Overview of the components involved in typical communication between different processes of an EDR](https://neodyme.io/blog/com_hijacking_1/process_overview.png)

Overview of the components involved in typical communication between different processes of an EDR


Communication with the back-end process remains an attractive attack surface.
For example, attackers could exploit it to trigger privileged actions, such as modifying the registry, from an unprivileged context.
Manufacturers are aware of these risks and have implemented safeguards to prevent direct communication with the back-end process.
However, previously discovered vulnerabilities, such as those in Avast \[1,2\], have demonstrated that bypassing these protections is possible.

### Exploiting back-end communication [¶](https://neodyme.io/en/blog/com_hijacking_1/\#exploiting-back-end-communication)

To abuse back-end communication, an attacker must first establish a way to interact with the back-end process.
There are two primary approaches:

1. **Exploit validation logic flaws**: Identify weaknesses in the logic used by the back-end process to verify that requests originate from the front-end process.
2. **Inject code into the front-end process**: Attackers can indirectly communicate with the back-end process by executing code within the trusted front-end process.

In our research, we pursued the second approach.
Using COM hijacking, we successfully injected code into the front-end process, enabling us to communicate with the back-end process from within the trusted front-end.

## COM hijacking [¶](https://neodyme.io/en/blog/com_hijacking_1/\#com-hijacking)

Component Object Model (COM) interfaces provide additional functionality to applications, offering a framework for interprocess communication and object reuse.
For instance, Windows Runtime (WinRT) is implemented based on COM.
A key advantage of COM is its abstraction: developers using COM interfaces do not need to understand the underlying implementation, which could be written in another language, executed in a separate process, or even reside on a remote server in the case of Distributed COM (DCOM).

Some COM interfaces implement their functionality through DLLs that are dynamically loaded into the calling process when the interface is invoked.
Hijacking such a COM interface allows injecting a custom DLL into the calling process, enabling code execution within the process’s context.

To use a COM interface the developer invokes the `CoCreateInstance` with a GUID, which then leads to a search of the right COM interface and returns a COM object if the interface is found. The following graphic gives a high level overview of how this could work for the TaskScheduler interface:

![Example COM lookup of the ITaskScheduler COM object](https://neodyme.io/blog/com_hijacking_1/com_intro.png)

Example COM lookup of the ITaskScheduler COM object


The core idea of COM hijacking is to exploit the registry’s search order for COM interface definitions.
When a COM interface is accessed, the system first looks for its definition in the `HKEY_CURRENT_USER` (HKCU) registry hive before checking the `HKEY_LOCAL_MACHINE` (HKLM) hive.
If the COM interface uses a DLL to provide its functionality, the registry entry will include the path to the implementing DLL.
Since the HKCU hive belongs to the current user, it can be modified by processes running with that user’s privileges.
This means that any process running in the user’s context — including the front-end process of an EDR product running in the context of our unprivileged user — will prioritize COM definitions in the HKCU hive and stop searching once a match is found.
The following diagram shows the registry accesses before and after a COM hijack:

![Overview of the involved components](https://neodyme.io/blog/com_hijacking_1/com-hijacking.png)

Overview of the involved components


COM hijacking is most often discussed as a persistence technique.
For instance, attackers could hijack a COM interface known to be invoked, ensuring their payload is executed.
In our research, however, we employed COM hijacking differently.
Rather than using it solely for persistence, we specifically targeted the front-end process of EDR products to load a custom DLL.
This allowed us to execute code within the process context, leveraging the elevated privileges of the back-end process during communication.
Interestingly, this approach proved effective against many EDR products. There was similar research in the past, which abused COM hijacking to bypass the self defense of similar products \[5\]
Futhermore James Forshaw previously demonstrated its use against VirtualBox \[3\].

In all the EDR products we examined, COM interfaces were used in the front-end process.
Most of these interfaces were located under the HKLM hive, so there was no need to overwrite any data.
However, overwriting an interface in the HKCU hive would also have been possible.

After hijacking a COM interface, every invocation of the targeted interface in the user’s context would trigger our hijacked COM interface.
For our purposes, this enabled us to load our custom DLL into the front-end process whenever specific actions were performed, such as opening a file dialogue in the user interface.

Now that we have discussed COM-hijacking in theory, the next question is how we identified COM interfaces of interest within the front-end process.

## Identifying a hijackable COM interface [¶](https://neodyme.io/en/blog/com_hijacking_1/\#identifying-a-hijackable-com-interface)

The initial step in all the vulnerabilities we discovered involved achieving code execution in a front-end process via COM hijacking.
As this was similar across all the products we analyzed, we will outline the general process here instead of repeating it for each specific product.

We can see that each COM lookup is performed via a GUID that matches to an `CLSID` (Class ID). Now we can hunt for those GUIDs and figure out what COM objects are used by the product.

For each product, the first task was to identify a COM Interface used by the front-end process.

This required considering several factors:

- When is the COM interface invoked?
  - During the start of the UI
  - When entering a specific menu
- Is the COM interface used by other processes?
  - To avoid unintended consequences (e.g., disrupting explorer.exe), we ensured the interface was unique to the target process or could be safely used in parallel.

We used the `Process Monitor` from the `SysInternals` suit to identify relevant COM interfaces.
We first identified the process we wanted to target.
Then, we used a filter to view only events triggered by this process.
Next, we created a filter for registry events where the path contained `CLSID` and `InProcServer32`, indicating that the process tries to load a DLL used for a COM interface.

The following screenshot demonstrates how `explorer.exe` queries the relevant registry keys, providing insight into the COM interfaces it accesses:

![Accesses to COM interfaces by explorer.exe](https://neodyme.io/blog/com_hijacking_1/process_monitor_com.png)

Accesses to COM interfaces by explorer.exe


After identifying a potential COM interface, the next step was to confirm if the front-end process loaded the referenced DLL.
We monitored file interactions and filtered paths containing the DLL name to do this.
If the DLL was loaded, it would trigger a load event for the DLL specified in the registry:

![Loading a DLL related to COM](https://neodyme.io/blog/com_hijacking_1/process_monitor_dll.png)

Loading a DLL related to COM


Once a suitable interface was identified, the next step was to hijack it.

## Hijacking a COM interface [¶](https://neodyme.io/en/blog/com_hijacking_1/\#hijacking-a-com-interface)

One registry key we targeted across multiple products was:

```
Computer\\HKEY_LOCAL_MACHINE\\SOFTWARE\\Classes\\CLSID\\{9FC8E510-A27C-4B3B-B9A3-BF65F00256A8}
```

This COM interface loads the `dataexchange.dll` into the calling process.
To hijack the DLL, we first exported it:

```
reg export "HKLM\\SOFTWARE\\Classes\\CLSID\\{9FC8E510-A27C-4B3B-B9A3-BF65F00256A8}" .\export.reg /reg:64
```

Then, we opened the exported file `export.reg` in a text editor and changed the paths to `HKEY_CURRENT_USER`.
We also changed the file path to point to our custom DLL:

```
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\\SOFTWARE\\Classes\\CLSID\\{9FC8E510-A27C-4B3B-B9A3-BF65F00256A8}]

[HKEY_CURRENT_USER\\SOFTWARE\\Classes\\CLSID\\{9FC8E510-A27C-4B3B-B9A3-BF65F00256A8}\\InProcServer32]

@="C:\\\\poc\\\\dataxchange.dll"

"ThreadingModel"="Both"
```

Next, we imported the modified registry export:

```
reg import .\export.reg /reg:64
```

With these modifications, all calls to this COM interface from the context of our unprivileged user would invoke our custom DLL.
This might lead to problems with other processes, so we should remove the hijack when we are done with exploitation.

Our DLL must export the functions the original COM DLL would expose to ensure smooth operation.
This can be achieved by proxying calls to the original DLL using a template such as:

```
#include <windows.h>

#include <combaseapi.h>

#pragma comment( linker, "/export:DllGetClassObject" )

#define ORIGINAL_COM_DLL_PATH "C:\\Windows\\System32\\dataxchange.dll"

void Go(void) {

 // Our payload

}

BOOL APIENTRY DllMain(HMODULE hModule,  DWORD  ul_reason_for_call, LPVOID lpReserved) {

    switch (ul_reason_for_call)  {

    case DLL_PROCESS_ATTACH:

    break;

    case DLL_THREAD_ATTACH:

    break;

    case DLL_THREAD_DETACH:

    break;

    case DLL_PROCESS_DETACH:

        break;

 }

    return TRUE;

}

typedef HRESULT(WINAPI * tDllGetClassObject)(REFCLSID rclsid, REFIID riid, LPVOID* ppv);

STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID FAR* ppv) {

 // Start our payload

 Go();

 // Load the original DLL and proxy the function call to it

 tDllGetClassObject pDllGetClassObject;

 HMODULE hOrigDLL = LoadLibrary(ORIGINAL_COM_DLL_PATH);

 pDllGetClassObject = (tDllGetClassObject) GetProcAddress(hOrigDLL, "DllGetClassObject");

  if (!pDllGetClassObject)

    return S_FALSE;

 HRESULT hRes = pDllGetClassObject(rclsid, riid, ppv);

  return hRes;

}
```

At this point, we achieved code execution in the context of the targeted product.
So, the next step was to analyze the communication between the front-end and back-end processes for the specific product to get an idea of how to abuse this primitive.

## Named pipe communication [¶](https://neodyme.io/en/blog/com_hijacking_1/\#named-pipe-communication)

Named pipes are a common method for communication between a server and one or more clients.
They are accessible using a unique name (as the name suggests) and often serve as a communication channel between security products’ front-end and back-end processes.

![Typical Named Pipe Communication via the WinAPI](https://neodyme.io/blog/com_hijacking_1/named_pipes.png)

Typical Named Pipe Communication via the WinAPI


We found that the easiest way to find out if a product uses named pipes was to use IONinja’s Pipe Monitor feature.
For this, you click “New Session”, select “Pipe Monitor” and enable “Run as administrator”.
You can click the “Capture” button in the top-right corner to start capturing named pipe traffic:

![Starting IONinja](https://neodyme.io/blog/com_hijacking_1/ioninja_start.png)

Starting IONinja


![Listening to named pipes with IONinja](https://neodyme.io/blog/com_hijacking_1/ioninja_listen.png)

Listening to named pipes with IONinja


With this, you can interact with the product’s user interface to generate pipe traffic and watch for captured named pipe traffic that corresponds to the interaction.
In our experience, there should be little named pipe communication on a vanilla system, so identifying the relevant communication should be straightforward if you have installed the product on a dedicated system.

Having identified the communication in `IONinja`, we have a pipe name and a process that opens the named pipe or writes to it.
We now need to identify the logic.
For this, we can look for strings beginning with `\\.\pipe\`, used when creating a named pipe.
The logic that interacts with the named pipe will likely reference this string.
You will also see calls to the `CreateNamedPipe` and `ConnectNamedPipe` functions.

For our initial target, all of this turned out to be unnecessary: When capturing data over a named pipe, we observed plaintext communication, including what appeared to be a registry key:

![Registry path in named pipe traffic](https://neodyme.io/blog/com_hijacking_1/ioninja_registry.png)

Registry path in named pipe traffic


The next section will detail how we exploited this communication to gain high privileges.

## Replaying a recorded message [¶](https://neodyme.io/en/blog/com_hijacking_1/\#replaying-a-recorded-message)

As shown in the screenshot above, the traffic on the named pipe for our first target contained a registry path and was not obfuscated.
This message was sent every time we opened the front-end process.

Using `Process Monitor`, we observed that the back-end process accessed the registry key running as `SYSTEM`.
This seemed promising, as writing a registry key as `SYSTEM` could lead to privilege escalation…

To test this theory, we implemented the following steps:

1. **Prepare the Payload**: We wrote a small program and converted it into shellcode using [donut](https://github.com/TheWover/donut).
2. **Inject the Payload**: Using our previously via COM hijacking loaded DLL, we injected the shellcode into the process. In the shellcode, we unloaded the DLL after a short sleep and then sent the modified data. This approach bypassed logic in the target process that appeared to validate loaded DLLs. Although we didn’t confirm whether bypassing this validation was essential, avoiding an unsigned DLL during communication helped minimize suspicion.
3. **Initial Testing**: To confirm our ability to replay the message, we modified the registry path in the recorded message. The modified path was successfully written to the registry:

![Modified registry key written](https://neodyme.io/blog/com_hijacking_1/registry_test_write.png)

Modified registry key written


We discovered that our ability to write registry keys was restricted to locations under the manufacturer’s designated registry path.
This limitation prevented us from writing keys like `RunOnce`, which could enable privilege escalation.

However, we identified a promising registry key named `Application Path`.
This key pointed to an application folder under `C:\Program Files (x86)`.
By modifying this path to one writable by us, we hypothesized that any high-privilege process loading from this path could execute our files, granting high privileges.

So, we modified the message again, choosing a path that would fit into the message without modifying any offsets.
After injecting our DLL into the process, we replayed the modified message to overwrite the `Application Path`.
Following a system restart, we observed that one of the privileged EDR processes executed files from the modified `Application Path`.
By placing our payload in this directory, we successfully gained `SYSTEM` privileges:

![Processes being started from modified path as SYSTEM](https://neodyme.io/blog/com_hijacking_1/process_start.png)

Processes being started from modified path as SYSTEM


## Conclusion [¶](https://neodyme.io/en/blog/com_hijacking_1/\#conclusion)

This blog post explored the attack surface associated with the interaction between an AV/EDR’s front-end and back-end processes.
Key takeaways are:

- **Breaking Trust Assumptions**: Using COM hijacking, we demonstrated how the assumption that the front-end process is inherently trusted can be exploited.
- **Finding Hijackable Interfaces**: We described our methodology for identifying and hijacking COM interfaces.
- **Privilege Escalation via Named Pipes**: We detailed how one target product communicated via named pipes and how replaying recorded messages enabled us to escalate privileges to SYSTEM.

In the next blog post, we will explore reversing RPC via COM and present a more complex exploit to achieve `SYSTEM` privileges by targeting another security product.

## 38c3 Talk and Slides [¶](https://neodyme.io/en/blog/com_hijacking_1/\#38c3-talk-and-slides)

We also gave a talk about this research at 38c3, which you can checkout here (note that at the time of writing it is only available in German):

By revealing the content you are aware that third-parties may collect personal information

Reveal media.ccc.de stream

The slides for the talk can be found [on our GitHub](https://github.com/neodyme-labs/38c3_com_talk).

## Resources [¶](https://neodyme.io/en/blog/com_hijacking_1/\#resources)

1. [https://the-deniss.github.io/posts/2023/04/26/avast-privileged-arbitrary-file-create-on-quarantine.html](https://the-deniss.github.io/posts/2023/04/26/avast-privileged-arbitrary-file-create-on-quarantine.html)
2. [https://the-deniss.github.io/posts/avast-privileged-arbitrary-file-create-on-restore/](https://the-deniss.github.io/posts/avast-privileged-arbitrary-file-create-on-restore/)
3. [https://googleprojectzero.blogspot.com/2017/08/bypassing-virtualbox-process-hardening.html](https://googleprojectzero.blogspot.com/2017/08/bypassing-virtualbox-process-hardening.html)
4. [https://pentestlab.blog/2020/05/20/persistence-com-hijacking/](https://pentestlab.blog/2020/05/20/persistence-com-hijacking/)
5. [https://blog.silentsignal.eu/2018/01/08/bare-knuckled-antivirus-breaking/](https://blog.silentsignal.eu/2018/01/08/bare-knuckled-antivirus-breaking/)

On this page

01. [Introduction](https://neodyme.io/en/blog/com_hijacking_1/#introduction)

02. [Technical Background](https://neodyme.io/en/blog/com_hijacking_1/#technical-background)

    1. [How does a low-privileged user change settings?](https://neodyme.io/en/blog/com_hijacking_1/#how-does-a-low-privileged-user-change-settings)

    2. [Security risks in back-end communication](https://neodyme.io/en/blog/com_hijacking_1/#security-risks-in-back-end-communication)

    3. [Protections against code injection](https://neodyme.io/en/blog/com_hijacking_1/#protections-against-code-injection)

    4. [Communication between front-end and back-end processes](https://neodyme.io/en/blog/com_hijacking_1/#communication-between-front-end-and-back-end-processes)

    5. [Exploiting back-end communication](https://neodyme.io/en/blog/com_hijacking_1/#exploiting-back-end-communication)
03. [COM hijacking](https://neodyme.io/en/blog/com_hijacking_1/#com-hijacking)

04. [Identifying a hijackable COM interface](https://neodyme.io/en/blog/com_hijacking_1/#identifying-a-hijackable-com-interface)

05. [Hijacking a COM interface](https://neodyme.io/en/blog/com_hijacking_1/#hijacking-a-com-interface)

06. [Named pipe communication](https://neodyme.io/en/blog/com_hijacking_1/#named-pipe-communication)

07. [Replaying a recorded message](https://neodyme.io/en/blog/com_hijacking_1/#replaying-a-recorded-message)

08. [Conclusion](https://neodyme.io/en/blog/com_hijacking_1/#conclusion)

09. [38c3 Talk and Slides](https://neodyme.io/en/blog/com_hijacking_1/#38c3-talk-and-slides)

10. [Resources](https://neodyme.io/en/blog/com_hijacking_1/#resources)


- [COM](https://neodyme.io/en/blog/tag/com)
- [LPE](https://neodyme.io/en/blog/tag/lpe)
- [Windows](https://neodyme.io/en/blog/tag/windows)

Share: