# https://cybergeeks.tech/a-deep-dive-into-brute-ratel-c4-payloads/

[Skip to content](https://cybergeeks.tech/a-deep-dive-into-brute-ratel-c4-payloads/#content)

Summary

[Brute Ratel C4](https://bruteratel.com/) is a Red Team & Adversary Simulation software that can be considered an alternative to Cobalt Strike. In this blog post, we’re presenting a technical analysis of a Brute Ratel badger/agent that doesn’t implement all the recent features of the framework. There aren’t a lot of Brute Ratel samples available in the wild. The malware implements the API hashing technique and comes up with a configuration that contains the C2 server, the user-agent used during the network communications, a password used for authentication with the C2 server, and a key used for encrypting data transmitted to the C2 server. The badger takes control of the infected machine by executing 63 different commands issued by the C2 server. The first 20 commands will be described in this blog post, while the rest of them will be detailed in an upcoming blog post.

Technical analysis

SHA256: d71dc7ba8523947e08c6eec43a726fe75aed248dfd3a7c4f6537224e9ed05f6f

This is a 64-bit executable. The malware pushes the code to be executed on the stack in order to evade Antivirus and EDR software:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/1.jpg)Figure 1

It implements the API hashing technique, which uses the “ROR EDI,0xD” instruction to compute 4-byte hashes that are compared with pre-computed ones (Figure 2).

![](https://cybergeeks.tech/wp-content/uploads/2023/08/2.jpg)Figure 2

The VirtualAllocEx API is used to allocate a new memory area that will store a DLL file (0x3000 = **MEM\_COMMIT** \| **MEM\_RESERVE**, 0x40 = **PAGE\_EXECUTE\_READWRITE**):

![](https://cybergeeks.tech/wp-content/uploads/2023/08/3-1024x107.jpg)Figure 3

The Brute Ratel C4 configuration is stored in clear text however, in recent versions, the config is [encrypted and Base64-encoded](https://unit42.paloaltonetworks.com/brute-ratel-c4-tool/). It contains the C2 IP address and port number, the user-agent used during the network communications, a password used to authenticate with the C2 server, a key used to encrypt data transmitted to the C2 server, and the URI:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/4-1024x220.jpg)Figure 4![](https://cybergeeks.tech/wp-content/uploads/2023/08/5-1024x204.jpg)Figure 5

A thread that executes the entry point of the new DLL is created via a function call to CreateRemoteThread:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/6-1024x128.jpg)Figure 6

The process extracts a pointer to the PEB from gs:\[0x60\] and another one to the [PEB\_LDR\_DATA](https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb_ldr_data) structure (+0x18), which contains information about the loaded DLLs. The InMemoryOrderModuleList doubly-linked list contains the loaded DLLs for the current process:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/7.jpg)Figure 7

The malicious binary allocates new memory for another DLL that implements the main functionality using VirtualAlloc:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/8-1024x89.jpg)Figure 8

LoadLibraryA is utilized to load multiple DLLs into the address space of the current process:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/9-1024x72.jpg)Figure 9

The malware retrieves the address of relevant functions by calling the GetProcAddress method:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/10-1024x65.jpg)Figure 10

The binary flushes the instruction cache for the current process using the NtFlushInstructionCache function (see Figure 11).

![](https://cybergeeks.tech/wp-content/uploads/2023/08/11-1024x75.jpg)Figure 11

Finally, the malware passes the execution flow to the newly constructed DLL:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/12.jpg)Figure 12

As we can see below, one of the export functions of the DLL is called “badger\_http\_1”, which reveals a Brute Ratel agent/badger.

![](https://cybergeeks.tech/wp-content/uploads/2023/08/13.jpg)Figure 13![](https://cybergeeks.tech/wp-content/uploads/2023/08/14.jpg)Figure 14

The FreeConsole method is used to detach the process from its console:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/15.jpg)Figure 15

The DLL repeats the process of finding functions address, as highlighted in Figure 16.

![](https://cybergeeks.tech/wp-content/uploads/2023/08/16.jpg)Figure 16

The process extracts the system time and passes the result to the srand function:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/17-1024x44.jpg)Figure 17

The atoi method is utilized to convert the port number to integer:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/18-1024x45.jpg)Figure 18

The malicious process creates an unnamed mutex object by calling the CreateMutexA API, as displayed in Figure 19.

![](https://cybergeeks.tech/wp-content/uploads/2023/08/19-1024x179.jpg)Figure 19

GetUserNameW is used to obtain the username associated with the current thread:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/20-1024x66.jpg)Figure 20

GetComputerNameExW is used to obtain the NetBIOS name associated with the local machine:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/21-1024x74.jpg)Figure 21

The badger retrieves a pseudo handle for the current process using GetCurrentProcess:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/22.jpg)Figure 22

The OpenProcessToken API is utilized to open the access token associated with the process (0x8 = **TOKEN\_QUERY**):

![](https://cybergeeks.tech/wp-content/uploads/2023/08/23-1024x73.jpg)Figure 23

The malware verifies if the token is elevated using the GetTokenInformation method (0x14 = **TokenElevation**):

![](https://cybergeeks.tech/wp-content/uploads/2023/08/24-1024x109.jpg)Figure 24

It obtains the current process ID via a function call to GetCurrentProcessId:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/25.jpg)Figure 25

GetModuleFileNameW is utilized to extract the path of the executable file of the process:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/26-1024x83.jpg)Figure 26

The above path is Base64-encoded using the CryptBinaryToStringW API (0x40000001 = **CRYPT\_STRING\_NOCRLF** \| **CRYPT\_STRING\_BASE64**):

![](https://cybergeeks.tech/wp-content/uploads/2023/08/27-1024x101.jpg)Figure 27

The process retrieves version information about the current operating system using RtlGetVersion:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/28-1024x44.jpg)Figure 28

The WSAStartup function initiates the use of the Winsock DLL by the current process:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/29-1024x55.jpg)Figure 29

The badger constructs a JSON that stores the password extracted from the configuration, the computer name, the OS version, the Base64-encoded executable path, the username, and the process ID:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/30-1.jpg)Figure 30

The JSON is encrypted using the XOR operator (key = “abcd@123” from configuration) and transformed by other operations:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/31-1024x89.jpg)Figure 31![](https://cybergeeks.tech/wp-content/uploads/2023/08/32.jpg)Figure 32![](https://cybergeeks.tech/wp-content/uploads/2023/08/33.jpg)Figure 33

The user-agent passed to the InternetOpenW function seems to indicate that the product was used by Deloitte China (Figure 34).

![](https://cybergeeks.tech/wp-content/uploads/2023/08/34-1024x117.jpg)Figure 34

The process connects to the C2 server on port 80 by calling the InternetConnectW function:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/35-1024x135.jpg)Figure 35

It creates a POST request to the “/content.php” resource using HttpOpenRequestW, as displayed below.

![](https://cybergeeks.tech/wp-content/uploads/2023/08/36-1024x160.jpg)Figure 36

The security flags for the handle are changed using the InternetSetOptionW API (0x1100 = **SECURITY\_FLAG\_IGNORE\_CERT\_CN\_INVALID** \| **SECURITY\_FLAG\_IGNORE\_UNKNOWN\_CA**):

![](https://cybergeeks.tech/wp-content/uploads/2023/08/37-1024x90.jpg)Figure 37

HttpAddRequestHeadersW can be used to add one or more HTTP request headers to the handle however, the second parameter is NULL during malware’s execution (0x20000000 = **HTTP\_ADDREQ\_FLAG\_ADD**):

![](https://cybergeeks.tech/wp-content/uploads/2023/08/38-1024x92.jpg)Figure 38

The process encodes the encrypted JSON using Base64 and exfiltrates the resulting data using HttpSendRequestW:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/39-1024x176.jpg)Figure 39

It verifies whether the C2 server sends any data back via a function call to InternetQueryDataAvailable:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/40-1024x102.jpg)Figure 40

The C2 server’s response is read using InternetReadFile:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/41-1024x134.jpg)Figure 41

The response is Base64-decoded and decrypted using the same key that was previously mentioned. The “auth” field is set to the decrypted information, and another request is made to the C2 server, asking for commands:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/42.jpg)Figure 42

[FakeNet-NG](https://github.com/mandiant/flare-fakenet-ng) was used to simulate the network communications with the C2 server. After decoding and decrypting the response, the first 2 bytes represent the command to be executed followed by additional parameters if necessary. A new thread handles the commands execution:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/43-1024x144.jpg)Figure 43

We’ll now describe the commands that can be issued by the C2 server.

**0x2C74 ID**– Exfiltrate file content to the C2 server

The PathFileExistsA API is utilized to confirm if the target file exists on the system:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/44-1024x44.jpg)Figure 44

The file is opened via a function call to CreateFileA (0x80000000 = **GENERIC\_READ**, 0x1 = **FILE\_SHARE\_READ**, 0x3 = **OPEN\_EXISTING**):

![](https://cybergeeks.tech/wp-content/uploads/2023/08/45-1024x127.jpg)Figure 45

The content is read by calling the ReadFile method, as shown in Figure 46.

![](https://cybergeeks.tech/wp-content/uploads/2023/08/46-1024x108.jpg)Figure 46

The data is sent to the C2 server along with the “\[+\] Download complete” message or the message shown in the figure below.

![](https://cybergeeks.tech/wp-content/uploads/2023/08/47.jpg)Figure 47

**0xA905 ID** – Copy files

The malware copies an existing file to a new file using CopyFileA:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/48-1024x74.jpg)Figure 48

**0x9B84 ID** – Move files

The process moves an existing file to another using the MoveFileA function (Figure 49).

![](https://cybergeeks.tech/wp-content/uploads/2023/08/49-1024x55.jpg)Figure 49

**0x13A1 ID** – Create files and populate them with content received from the C2 server

Firstly, the file is created via a function call to CreateFileA:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/50-1024x126.jpg)Figure 50

The received data is Base64-decoded using CryptStringToBinaryA and written to the file:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/51-1024x110.jpg)Figure 51

**0xE993 ID** – Delete files

DeleteFileA is used to delete the target files, as highlighted below:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/52-1024x44.jpg)Figure 52

**0x0605 ID** – Close handles

The badger closes an object handle (i.e. file, process) using the CloseHandle API:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/53-1024x63.jpg)Figure 53

**0x3F61 ID** – Create directories

The malicious binary has the ability to create directories using the CreateDirectoryA method:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/54-1024x56.jpg)Figure 54

**0x1139 ID** – Change the current directory for the process

SetCurrentDirectoryA is utilized to perform the desired operation (see Figure 55).

![](https://cybergeeks.tech/wp-content/uploads/2023/08/55-1024x45.jpg)Figure 55

**0x3C9F ID** – Obtain the current directory for the process

The malware extracts the current directory for the process by calling the GetCurrentDirectoryW API:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/56-1024x64.jpg)Figure 56

**0x8F40 ID** – Delete directories

The process deletes a target directory only if it’s empty using RemoveDirectoryA:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/57-1024x45.jpg)Figure 57

**0x0A32 ID** – Retrieve the Last-Write time for files/directories

The files are enumerated in the current directory using the FindFirstFileW and FindNextFileW functions:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/58-1024x57.jpg)Figure 58![](https://cybergeeks.tech/wp-content/uploads/2023/08/59-1024x56.jpg)Figure 59

For each of the file or directory that matches the pattern, the binary calls the CreateFileW API:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/60-1024x126.jpg)Figure 60

The process retrieves the Last-Write time via a function call to GetFileTime:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/61-1024x98.jpg)Figure 61

The file time is converted to system time format using FileTimeToSystemTime:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/62-1024x75.jpg)Figure 62

Finally, the above time is converted to the currently active time zone:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/63-1024x71.jpg)Figure 63

**0x3D1D ID** – Change the Desktop wallpaper

The malicious process opens the “TranscodedWallpaper” file that contains the Desktop wallpaper:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/64-1024x203.jpg)Figure 64

The above file is filled in with content received from the C2 server (Figure 65).

![](https://cybergeeks.tech/wp-content/uploads/2023/08/65-1024x108.jpg)Figure 65

The SystemParametersInfoA method is utilized to change the Desktop wallpaper (0x14 = **SPI\_SETDESKWALLPAPER**, 0x1 = **SPIF\_UPDATEINIFILE**):

![](https://cybergeeks.tech/wp-content/uploads/2023/08/66-1024x90.jpg)Figure 66

**0xD53F ID** – Retrieve the username

This command is used to obtain the username associated with the current thread:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/67-1024x64.jpg)Figure 67

**0x0609 ID** – Retrieve the available disk drives

The malware extracts a bitmask that contains the available disk drives by calling the GetLogicalDrives API, as shown in Figure 68.

![](https://cybergeeks.tech/wp-content/uploads/2023/08/68.jpg)Figure 68

**0xC144 ID** – Extract all device drivers

EnumDeviceDrivers is utilized to obtain the load address for all device drivers:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/69-1024x75.jpg)Figure 69

Using the above address, the process retrieves the name of the device driver by calling the GetDeviceDriverBaseNameA method:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/70-1024x80.jpg)Figure 70

**0x0A01 ID** – Compute the number of minutes that have elapsed since the system was started

The GetTickCount function is used to extract the number of milliseconds and a simple calculation is performed (see Figure 71).

![](https://cybergeeks.tech/wp-content/uploads/2023/08/71.jpg)Figure 71

**0x73E6 ID** – Argument Spoofing

The badger has the ability to hide the arguments by modifying the process environment block (PEB):

![](https://cybergeeks.tech/wp-content/uploads/2023/08/72-1024x48.jpg)Figure 72

**0x8AFA ID** – Parent PID Spoofing

This command can be used to spoof the parent process ID in order to evade EDR software or other solutions:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/73-1024x48.jpg)Figure 73

**0xC929 ID** – Extract child process name

The binary could spawn multiple processes that can be displayed using this command (Figure 74).

![](https://cybergeeks.tech/wp-content/uploads/2023/08/74-1024x56.jpg)Figure 74

**0x9E72 ID** – Display pipes name

The malware displays the name of a previously created pipe:

![](https://cybergeeks.tech/wp-content/uploads/2023/08/75-1024x56.jpg)Figure 75

The other 30 relevant commands will be detailed in a second blog post.

INDICATORS OF COMPROMISE

SHA256: d71dc7ba8523947e08c6eec43a726fe75aed248dfd3a7c4f6537224e9ed05f6f

C2 server: 45.77.172.28

User-agent: trial@deloitte.com.cn

References

MSDN: [https://docs.microsoft.com/en-us/windows/win32/api/](https://docs.microsoft.com/en-us/windows/win32/api/)

FakeNet-NG: [https://github.com/mandiant/flare-fakenet-ng](https://github.com/mandiant/flare-fakenet-ng)

Unit42: [https://unit42.paloaltonetworks.com/brute-ratel-c4-tool/](https://unit42.paloaltonetworks.com/brute-ratel-c4-tool/)

4.77votes

Article Rating

2 Comments

Oldest

NewestMost Voted

Inline Feedbacks

View all comments

![JavadYassarii](https://secure.gravatar.com/avatar/990b5b5bfed4d782bb677e15be6fef4feef26e39459bd05b9fe6daa11814a38a?s=64&d=mm&r=g)

JavadYassarii

[Share On X](https://twitter.com/intent/tweet?text=nicewaiting%20for%20next%20partit%20would%20be%20good%20to%20check%20Night...%20&url=https%3A%2F%2Fcybergeeks.tech%2Fa-deep-dive-into-brute-ratel-c4-payloads%2F%23comment-166 "Share On X")

2 years ago

nice

waiting for next part

it would be good to check NightHawk samples too

0

![trackback](https://cybergeeks.tech/wp-content/plugins/wpdiscuz/assets/img/trackback.png)

[A DEEP DIVE INTO BRUTE RATEL C4 PAYLOADS – BU-CERT](https://cert.bournemouth.ac.uk/a-deep-dive-into-brute-ratel-c4-payloads/)

[Share On X](https://twitter.com/intent/tweet?text=[%E2%80%A6]%20Read%20more%E2%80%A6%20[%E2%80%A6]&url=https%3A%2F%2Fcybergeeks.tech%2Fa-deep-dive-into-brute-ratel-c4-payloads%2F%23comment-167 "Share On X")

2 years ago

\[…\] Read more… \[…\]

2

wpDiscuz

Insert