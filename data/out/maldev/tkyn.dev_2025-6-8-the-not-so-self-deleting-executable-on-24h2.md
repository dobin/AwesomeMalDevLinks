# https://tkyn.dev/2025-6-8-The-Not-So-Self-Deleting-Executable-on-24h2/

Arctic Theme

# The Not So Self Deleting Executable on 24h2

_2025/06/08_

# [TL;DR :](https://tkyn.dev/2025-6-8-The-Not-So-Self-Deleting-Executable-on-24h2/\#TL-DR "TL;DR :") TL;DR :

When executing malware in contested territory clearing your tracks is very important. Hence the Lloyd Labs self delete technique which has had interpretations published by many researchers throughout the years.

Today we explore why this doesn’t work as expected in 24H2 and how to fix it!

# [Overview:](https://tkyn.dev/2025-6-8-The-Not-So-Self-Deleting-Executable-on-24h2/\#Overview "Overview:") Overview:

- [https://github.com/LloydLabs/delete-self-poc](https://github.com/LloydLabs/delete-self-poc)
- BOF implementations: [https://github.com/EspressoCake/Self\_Deletion\_BOF/blob/main/src/main.c](https://github.com/EspressoCake/Self_Deletion_BOF/blob/main/src/main.c)
  - [https://github.com/seventeenman/SelfDel-BOF](https://github.com/seventeenman/SelfDel-BOF)
- [https://github.com/Octoberfest7/Mutants\_Sessions\_Self-Deletion?tab=readme-ov-file#self-deletion](https://github.com/Octoberfest7/Mutants_Sessions_Self-Deletion?tab=readme-ov-file#self-deletion)
- [https://github.com/secur30nly/go-self-delete](https://github.com/secur30nly/go-self-delete)

I was first made aware of this technique from a Xeet from JonasLyk.

[https://x.com/jonasLyk/status/1350401461985955840](https://x.com/jonasLyk/status/1350401461985955840)

[https://pbs.twimg.com/media/Er2W8NFXIAAWZ5a?format=png&name=4096x4096](https://pbs.twimg.com/media/Er2W8NFXIAAWZ5a?format=png&name=4096x4096)

It follows this pattern:

```
1. Open a file with DELETE desired access
2. Rename the unnamed primary :$DATA stream
3. Close the first handle
4. Open the original filename again with DELETE
5. Set the disposition to delete = true
6. Close the handle
7. File deleted
```

The public PoCs for this follow the same pattern.

```
- **`GetModuleFileNameW(NULL, wcPath, MAX_PATH)`**
    → Get path of current executable.

- **`ds_open_handle(wcPath)`**
    → Calls: `CreateFileW(wcPath, DELETE, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL)`
    → Opens the file with delete permissions.

- **`ds_rename_handle(hCurrent)`**
    → Allocates memory for `FILE_RENAME_INFO`
    → `RtlSecureZeroMemory(...)` to zero out struct
    → `RtlCopyMemory(...)` to copy `DS_STREAM_RENAME`
    → `SetFileInformationByHandle(hHandle, FileRenameInfo, pfRename, size)`
    → ==Renames file to alternate data stream (ADS).==

- **`CloseHandle(hCurrent)`**
    → Closes renamed handle.

- **`ds_open_handle(wcPath)`**
    → Reopens the file.

- **`ds_deposite_handle(hCurrent)`**
    → Sets `FILE_DISPOSITION_INFO.DeleteFile = TRUE`
    → `SetFileInformationByHandle(hHandle, FileDispositionInfo, &fDelete, sizeof(fDelete))`

- **`CloseHandle(hCurrent)`**
    → Triggers file deletion.

- **`PathFileExistsW(wcPath)`**
    → Verifies whether the file has been deleted.
```

# [Investigation:](https://tkyn.dev/2025-6-8-The-Not-So-Self-Deleting-Executable-on-24h2/\#Investigation "Investigation:") Investigation:

While this technique works perfectly on Windows version 23H2 (for reasons we’ll explore later), Windows 11 24H2 exhibits unexpected behavior.

![](https://tkyn.dev/assets/images/bang/Pasted_image_20250501104910.png)

This image shows a comparison between Windows 23H2 (left) and Windows 11 24H2 (right). In 24H2, while the file appears empty, it actually still exists on disk its contents have merely been moved to an alternate data stream instead of being deleted. The data persists in this alternate stream rather than the default one, which defeats the purpose of self deletion.

Let’s examine what this looks like in Procmon.

**23H2:**

![](https://tkyn.dev/assets/images/bang/Pasted_image_20250501105650.png)

**24H2:**

![](https://tkyn.dev/assets/images/bang/image.png)

Based on these observations, we can see that the technique produces different results on 24H2, specifically failing during the SetDispositionInformationFile call.

To investigate further, I downloaded the NTFS.sys samples for both 23H2 and 24H2 from [https://winbindex.m417z.com/?file=ntfs.sys](https://winbindex.m417z.com/?file=ntfs.sys). After analyzing these files in Ghidra, I identified NtfsSetDispositionInfo as the function responsible for the error.

I then set up Kernel debugging on a fresh machine using NTSTATUS debugging. This allows NTFS to trigger a breakpoint when returning specific NTSTATUS codes. The required commands are `ed Ntfs!NtfsStatusDebugFlags 2` followed by `ed Ntfs!NtfsStatusBreakOnStatus 0xc0000121` to catch our error.

[https://www.osr.com/blog/2018/10/17/ntfs-status-debugging/](https://www.osr.com/blog/2018/10/17/ntfs-status-debugging/)

[https://www.osr.com/blog/2021/01/21/mitigating-the-i30bitmap-ntfs-bug/](https://www.osr.com/blog/2021/01/21/mitigating-the-i30bitmap-ntfs-bug/)

Here there are a couple things to make note of:

![](https://tkyn.dev/assets/images/bang/Pasted_image_20250501114030.png)

This is the disassembly that leads to the breakpoint triggered by the error. The specific error code is 0xF216D. Microsoft provides these debugging codes to help track the exact sequence of events that cause the error.

Using WinDbg’s disassembly output, I matched the instructions to Ghidra’s code flow graph. I traced the execution path backward from the 0xF216D debug code to its origin.

I then compared this with the 23H2 code to identify differences. Though I attempted to use automated diffing tools ( [https://github.com/clearbluejar/ghidriff](https://github.com/clearbluejar/ghidriff)), my lack of experience with them led me to manually compare how 23H2’s NtfsSetDispositionInfo and 24H2’s version handled file deletion decisions.

![](https://tkyn.dev/assets/images/bang/Pasted_image_20250501115337.png)

I investigated numerous rabbit holes here that I would like to explore further in the future, such as how 24H2 improved the handling of setting delete disposition on directories rather than files.

Ideally, I would have set a breakpoint in a kernel debugging session for 23H2 to directly compare execution paths, but I hadn’t set up a VM for this purpose.

By using the POSIX SEMANTICS flag this allows the deletion to continue.

| FILE\_DISPOSITION\_POSIX\_SEMANTICS | 0x00000002 | Specifies the system should perform a POSIX-style delete. See more info in Remarks. |
| --- | --- | --- |

Here’s some code to do it! I uploaded the whole project to Github but this is the most important part:

```
FILE_DISPOSITION_INFORMATION_EX dispo = {};
dispo.Flags = FILE_DISPOSITION_DELETE | FILE_DISPOSITION_POSIX_SEMANTICS;

IO_STATUS_BLOCK iosb = {};
NTSTATUS status = NtSetInformationFile(hFile, &iosb, &dispo, sizeof(dispo), FileDispositionInformationEx);
if (status < 0) {
    DWORD err = RtlNtStatusToDosError(status);
    std::wcerr << L"[!] NtSetInformationFile failed. NTSTATUS: 0x" << std::hex << status
        << L", Win32: " << std::dec << err << std::endl;
    CloseHandle(hFile);
    HeapFree(GetProcessHeap(), 0, pRename);
    return FALSE;
}
```

[https://github.com/MaangoTaachyon/SelfDeletion-Updated](https://github.com/MaangoTaachyon/SelfDeletion-Updated)

![](https://tkyn.dev/assets/images/bang/image%201.png)

Now working on 24H2!

![](https://tkyn.dev/assets/images/bang/image%202.png)

BOF implementation demo:

[https://youtu.be/Ai99vNO4nEY](https://youtu.be/Ai99vNO4nEY)

I was made aware of this through a discord message and an issue that was raised in the Github repo

[https://github.com/LloydLabs/delete-self-poc/issues/6](https://github.com/LloydLabs/delete-self-poc/issues/6)

![](https://tkyn.dev/assets/images/bang/image%203.png)

![](https://tkyn.dev/assets/images/bang/image%204.png)

![](https://tkyn.dev/assets/images/bang/image%205.png)

![](https://tkyn.dev/assets/images/bang/image%206.png)

### [Extra info!](https://tkyn.dev/2025-6-8-The-Not-So-Self-Deleting-Executable-on-24h2/\#Extra-info "Extra info!") Extra info!

- **Read-Only File Protection**:
  - Debug Code: `0xf20b9`
  - When the file has read-only attributes and the caller doesn’t have the right flags
- **Access Check Failure**:
  - Debug Code: `0xf20e7`
  - When TxfAccessCheck fails (permission denied)
- **Reparse Point Flag**:
  - Debug Code: `0xf2102`
  - When the file has a reparse point flag set
- **File Not Deletable (General Case)**:
  - Debug Code: `0xf21df`
  - When NtfsIsFileDeleteable returns false
- **Memory Mapped File Special Cases**:
  - Debug Code: `0xf216d`
  - When special handling for memory-mapped files fails
- **Cannot Flush Memory-Mapped Image Section**:
  - Debug Code: `0xf2159`
  - When MmFlushImageSection fails for a memory-mapped file
- **Failed to Create Handle for Memory-Mapped File**:
  - Debug Code: `0xf2160`
  - When NtfsCreatePosixDeleteHandleForMemoryMappedFile fails

Big thanks to [sixtyvividtails](https://x.com/sixtyvividtails/)!