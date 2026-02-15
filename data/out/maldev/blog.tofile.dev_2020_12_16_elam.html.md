# https://blog.tofile.dev/2020/12/16/elam.html

# tl;dr

I created a tool to [run arbitrary programs as Protected Process Light (PPL)](https://github.com/pathtofile/PPLRunner),
then used this tool with [Sealighter](https://github.com/pathtofile/Sealighter) to get events from the
`Microsoft-Windows-Threat-Intelligence` ETW Provider.

# Protecting AntiMalware Services

(Note this isn’t the best description of PPL and AntiMalware, sorry)
There are some processes and services on Windows that Microsoft doesn’t want even Administrators to be
able to inspect or tamper with. An example would be programs that provide AntiMalware capabilities - if
an administrator could simply tamper with these processes, then so could a malicious actor with high
enough privileges.

When AntiMalware processes are started, they have a special flag inside their `EPROCESS` struct in the kernel,
that marks them as a `Protected Process Light`, or PPL. Both the Binary and any DLLs must be signed by Microsoft,
with a certificate that also signs a corresponding Early Launch AntiMalware (ELAM) Kernel Driver. In order to get
an ELAM driver signed, you must submit the driver to Microsoft, who will assess it to ensure both you and the driver are legitimate and not a danger to users.

This is an involved process, however if you are able to convince Microsoft you are legitimate, processes run as
AntiMalware PPL have a number of special characteristics:

- They cannot be stopped or killed by an Admin or non-PPL process
- They cannot be inspected by non-PPL debuggers (Although kernel debuggers still work)
- They get access to the `Microsoft-Windows-Threat-Intelligence` ETW Provider

The 3rd point was the most interesting to me - Regular programs can subscribe to this Provider, but the kernel
will only send events to processes that are marked PPL. So I wanted to learn what the process was to create PPL process and if it was possible to get my [Sealighter](https://github.com/pathtofile/Sealighter) ETW Tracer marked as PPL, so I could see that events from the `Threat-Intelligence` Provider look like.

# Getting a Cert

Due to the requirement of having to submit code to Microsoft to review, even if you have a legitimate code signing
certificate (or “find” one), this would not be enough to create an ELAM driver and PPL service.

You could use [James Forshaw’s](https://googleprojectzero.blogspot.com/2018/10/injecting-code-into-windows-protected.html) technique of doing shenanigans such as injecting into an existing PPL process, but I wanted to learn at how to create a legitimate ELAM driver and PPL process.

So instead I opted to put my test machine into [testsigning](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/the-testsigning-boot-configuration-option) mode, which alters Windows behaviour a little bit, but otherwise
allows us to sign our own drivers and programs with Microsoft. This is done by running the following and rebooting:

```
bcdedit /set testsigning on
```

To generate a self-signed code signing certificate, we can use PowerShell:

```
# Create a new certificate in our Cert Store:
$cert = New-SelfSignedCertificate -certstorelocation "Cert:\CurrentUser\My" -HashAlgorithm SHA256 -Subject "CN=ppl_runner" -TextExtension @("2.5.29.37={text}1.3.6.1.4.1.311.61.4.1,1.3.6.1.5.5.7.3.3")

# Export from Store to a file, so we can use it across multiple machines
$password = "password"   # never do this in real life...
$passwordSecure = ConvertTo-SecureString -String $password -Force -AsPlainText
Export-PfxCertificate -cert $cert -FilePath "ppl_runner.pfx" -Password $passwordSecure
```

**Note:** It is important that the certificate was hashed using SHA256, and that is has both the ‘Code Signing’ and ‘Early Launch’ EKU text extensions.

To sign any binary with this certificate, get `signtool.exe` from the Windows SDKs and run:

```
signtool.exe sign /fd SHA256 /a /v /ph /f "ppl_runner.pfx" /p "password" <binary_path>
```

# Creating an ELAM Driver

PPL Processes are typically services, and must be assosiated with an ELAM Driver.

The ELAM Driver doesn’t need to actually do anything (mine was just an empty `DriverEntry` function),
and as we’ll see below doesn’t actually need to be installed.
However it must have a resource named `MSElamCertInfoID`, which looks like this:

```
MicrosoftElamCertificateInfo  MSElamCertInfoID
{
      1,            // 1 certificate
      L"<hash>\0",  // 'to-be-signed' hash
      0x800C,       // Cert is SHA256
      L"\0"         // No extra EKUs
}
```

The `to-be-signed` hash isn’t the easiest thing to calculate: we can either run `certmgr.exe –v`
on a binary that has been already signed with the certificate, or we can use
[this awesome PowerShell script](https://gist.github.com/mattifestation/660d7e17e43e8f32c38d820115274d2e)
from Matt Graeber. If using `certmgr` make sure to put the hash down with no spaces, e.g.:

```
MicrosoftElamCertificateInfo  MSElamCertInfoID
{
      1,
      L"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\0",
      0x800C,
      L"\0"
}
```

Microsoft have an [example ELAM Driver on GitHub](https://github.com/microsoft/Windows-driver-samples/tree/master/security/elam), and I’ve published my driver code [here](https://github.com/pathtofile/PPLRunner/tree/main/elam_driver).

# Creating an AntiMalware Service

Once the ELAM driver was built with a `MSElamCertInfoID` resource and signed, we need to create the assosiated PPL service.
The service itself can just be a normal service with a `ServiceMain`, etc., but in order to create the service,
we must first create an ‘installer’, which will do two things:

## Step 1. Install ELAM Cert

First we need to ‘install’ the ELAM Cert, which in `testsigning` mode must be done once per boot. In C, this is as simple as:

```
HANDLE FileHandle = NULL;
// Open a handle to the driver file
FileHandle = CreateFileW(
    L"full\\path\\to\\driver.sys",
    FILE_READ_DATA,
    FILE_SHARE_READ,
    NULL,
    OPEN_EXISTING,
    FILE_ATTRIBUTE_NORMAL,
    NULL
);
if (FileHandle == INVALID_HANDLE_VALUE) {
    return GetLastError();
}

// Install the certificate
if (InstallElamCertificateInfo(FileHandle) == FALSE)
{
    return GetLastError();
}
```

`InstallElamCertificateInfo` Will look in the `MSElamCertInfoID` resource, check the certificate is valid, and install it.
The driver can be anywhere on disk, and once the certificate is installed, we don’t need it again, and don’t need to actually run it. However in `testsigning` mode this step needs to be repeated if the machine reboots.

## Step 2. Create the Service

Once the certificate is installed, the installer can now create the service and mark it as AntiMalware PPL:

```
// Open a handle the the Service Manager
SC_HANDLE hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
if (hSCManager == NULL) {
    return GetLastError();
}

// Create an own-process service
SC_HANDLE hService = CreateService(
    hSCManager,
    L"ppl_runner",
    L"ppl_runner",
    SCManagerAccess,
    SERVICE_WIN32_OWN_PROCESS,
    SERVICE_DEMAND_START,
    SERVICE_ERROR_NORMAL,
    L"full\\path\\to\\service\\binary.exe",
    NULL, NULL, NULL, NULL, NULL
);
if (hService == NULL) {
    return GetLastError();
}

// Mark new service to start as PROTECTED_ANTIMALWARE_LIGHT
SERVICE_LAUNCH_PROTECTED_INFO info;
info.dwLaunchProtected = SERVICE_LAUNCH_PROTECTED_ANTIMALWARE_LIGHT;
if (ChangeServiceConfig2(hService, SERVICE_CONFIG_LAUNCH_PROTECTED, &info) == FALSE) {
    return GetLastError();
}
```

## Step 3: Start Service

If the steps above completed successfully, then we can start the service from the commandline:

```
net.exe start ppl_runner
```

An Administrator can start the PPL Service, but they cannot stop it once it starts.
To confirm the process is marked as PPL, we can open [Process Explorer from Sysinternals](https://docs.microsoft.com/en-us/sysinternals/downloads/process-explorer),
then look in the ‘Protection’ column, which should look like this:

![Process Explorer Output showing PPL](https://blog.tofile.dev/assets/ppl_01.png)

# Launching a child.

Following the above process, we now have our own service with arbitrary code running as
AntiMalware PPL.

This alone should be enough to start experimentations, however I wanted to be able to run
any program as PPL. But a service must have a `ServiceMain`, and do other things services do.

I wanted to be able to take any regular executable, either mine or other people’s, and run them as PPL to
see how they behave.

It turns out PPL Services are allowed to call `CreateProcess` to run arbitrary binaries, provided:

- The binary is signed with the same certificate as the service
- Any DLLs the binary uses are also signed by the certificate

From the service, we just need to pass a few extra values into the `StartupInfoEx` struct:

```
// Create and initialise StartupInfoEx and Attribute List
STARTUPINFOEXW StartupInfoEx = { 0 };
SIZE_T AttributeListSize = 0;
StartupInfoEx.StartupInfo.cb = sizeof(StartupInfoEx);
InitializeProcThreadAttributeList(NULL, 1, 0, &AttributeListSize);
if (AttributeListSize == 0) {
    return GetLastError();
}
StartupInfoEx.lpAttributeList =
    (LPPROC_THREAD_ATTRIBUTE_LIST)HeapAlloc(GetProcessHeap(), 0, AttributeListSize);
if (InitializeProcThreadAttributeList(StartupInfoEx.lpAttributeList, 1, 0, &AttributeListSize) == FALSE) {
    return GetLastError();
}

// Set ProtectionLevel to be the same as the service, i.e. AntiMalware PPL
DWORD ProtectionLevel = PROTECTION_LEVEL_SAME;
if (UpdateProcThreadAttribute(StartupInfoEx.lpAttributeList,
    0,
    PROC_THREAD_ATTRIBUTE_PROTECTION_LEVEL,
    &ProtectionLevel,
    sizeof(ProtectionLevel),
    NULL,
    NULL) == FALSE)
{
    return GetLastError();
}

// Start Process (hopefully)
PROCESS_INFORMATION ProcessInformation = { 0 };
if (CreateProcess(NULL,
    L"full\\path\\to\\child\\binary.exe --with-arguments",
    NULL,
    NULL,
    FALSE,
    EXTENDED_STARTUPINFO_PRESENT | CREATE_PROTECTED_PROCESS,
    NULL,
    NULL,
    (LPSTARTUPINFOW)&StartupInfoEx,
    &ProcessInformation) == FALSE)
{
    // If the binary isn't signed properly this will be ERROR_INVALID_IMAGE_HASH
    return GetLastError();
}
```

If everything is successful, the service will start the child process, which should
also be marked as AntiMalware PPL.

# Putting it all together - PPLRunner

I’ve combined all the above techniques into a tool I’ve called [PPLRunner](https://github.com/pathtofile/PPLRunner).

PPLRunner is an ELAM Driver and PPl service that when started will:

1. look in the `HKLM\SOFTWARE\PPL_RUNNER` registry key for a binary and arguments to run
2. Start the binary as AntiMalware PPL
3. Stop itself, so it can be run again with out having to reboot or become PPL to kill it.

It has made it easy to quickly start any program as PPL, so I could test out what I can and can’t do as PPL.

The project signs all the binaries at build-time with a self-signed certificate,
and provides the certificate and key to sign other binaries as well.

# Using PPLRunner with ETW.

Now I had the ability to run (almost) any program as PPL, I wanted to see what events from the special
`Microsoft-Windows-Threat-Intelligence` ETW Provider looked like.

A while ago I created [Sealighter](https://github.com/pathtofile/Sealighter), a program that can subscribe
to arbitrary ETW Providers and convert their events to JSON, logging the output to either the console, a file,
or the Event Log.

I opted to report events the Event Log, so I [instaled the Sealighter Manifest](https://github.com/pathtofile/Sealighter/blob/main/docs/INSTALLATION.md#log-to-windows-event-log). I then signed the Sealighter binary with the same
certificate that I used for PPLRunner, and set PPLRunner to run Sealighter
with the following config:

```
{
    "session_properties": {
        "session_name": "Sealighter-Trace",
        "output_format": "event_log"
    },
     "user_traces": [\
        {\
            "trace_name": "TI-Trace",\
            "provider_name": "Microsoft-Windows-Threat-Intelligence"\
        }\
    ]
}
```

I started PPLRunner and Sealighter, and sure enough as Sealighter was PPL events started to appear in the Event Log:
![Event Log showing Sealighter Events](https://blog.tofile.dev/assets/ppl_02.png)

And could then use PowerShell to dump the events to disk:

```
$events = Get-WinEvent -LogName "Sealighter/Operational"
foreach ($event in $events) {
    $event_json = ConvertFrom-Json $event.Message
    $filename = ".\" + $event_json.header.timestamp.replace(":","").replace(" ","_") + ".json"
    $event_json | ConvertTo-Json -depth 100 | Set-Content $filename
}
```

The end result was numerous events like the following:

```
{
  "header":  {
    "activity_id":  "{00000000-0000-0000-0000-000000000000}",
    "event_flags":  576,
    "event_id":  6,
    "event_name":  "",
    "event_opcode":  0,
    "event_version":  1,
    "process_id":  2872,
    "provider_name":  "Microsoft-Windows-Threat-Intelligence",
    "task_name":  "KERNEL_THREATINT_TASK_ALLOCVM",
    "thread_id":  3908,
    "timestamp":  "2020-12-12 12:14:02Z",
    "trace_name":  "TI-Trace"
  },
  "properties":  {
      "AllocationType":  4096,
      "BaseAddress":  "0x7DF417BC1000",
      "CallingProcessCreateTime":  "2020-12-12 12:10:21Z",
      "CallingProcessId":  2872,
      "CallingProcessProtection":  0,
      "CallingProcessSectionSignatureLevel":  0,
      "CallingProcessSignatureLevel":  0,
      "CallingProcessStartKey":  5910974510923849,
      "CallingThreadCreateTime":  "2020-12-12 12:10:25Z",
      "CallingThreadId":  3908,
      "OriginalProcessCreateTime":  "2020-12-12 12:10:21Z",
      "OriginalProcessId":  2872,
      "OriginalProcessProtection":  0,
      "OriginalProcessSectionSignatureLevel":  0,
      "OriginalProcessSignatureLevel":  0,
      "OriginalProcessStartKey":  5910974510923849,
      "ProtectionMask":  32,
      "RegionSize":  "0x1000",
      "TargetProcessCreateTime":  "2020-12-12 12:10:21Z",
      "TargetProcessId":  2872,
      "TargetProcessProtection":  0,
      "TargetProcessSectionSignatureLevel":  0,
      "TargetProcessSignatureLevel":  0,
      "TargetProcessStartKey":  5910974510923849
    }
}
```

# Conclusion

This blog is much longer than I expected, but I wanted to share my explorations
into PPL and AntiMalware.

I hope both [PPLRunner](https://github.com/pathtofile/PPLRunner) and
[Sealighter](https://github.com/pathtofile/Sealighter) make it easy for others
to start learning about Protected Processes and the `Threat-Intelligence` provider,
and encourage others to learn more about what goes on ‘under the hood’ in Windows.

# Further Reading

- [https://docs.microsoft.com/en-us/windows/win32/services/protecting-anti-malware-services-](https://docs.microsoft.com/en-us/windows/win32/services/protecting-anti-malware-services-)
- [https://www.crowdstrike.com/blog/protected-processes-part-3-windows-pki-internals-signing-levels-scenarios-signers-root-keys/](https://www.crowdstrike.com/blog/protected-processes-part-3-windows-pki-internals-signing-levels-scenarios-signers-root-keys/)
- [https://googleprojectzero.blogspot.com/2018/10/injecting-code-into-windows-protected.html](https://googleprojectzero.blogspot.com/2018/10/injecting-code-into-windows-protected.html)
- Chapter 3, Windows Internals Part 1 (#1 resource for anything Windows honestly)