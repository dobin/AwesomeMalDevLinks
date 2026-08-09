# https://blog.trailofbits.com/2026/05/05/c/c-checklist-challenges-solved/

Page content

We recently added a [C/C++ security checklist](https://appsec.guide/docs/languages/c-cpp/) to the Testing Handbook and [challenged readers to spot the bugs in two code samples](https://blog.trailofbits.com/2026/04/09/master-c-and-c-with-our-new-testing-handbook-chapter/): a deceptively simple Linux ping program and a Windows driver registry handler. If you found the `inet_ntoa` global buffer gotcha or the missing `RTL_QUERY_REGISTRY_TYPECHECK` flag, nice work. If not, here’s a full walkthrough of both challenges, plus a deep dive into how the Windows registry type confusion escalates from a local denial of service to a kernel write primitive.

Since we first released the new C/C++ security checklist, we also developed a new Claude skill, [c-review](https://github.com/trailofbits/skills/tree/main/plugins/c-review). It turns the checklist into bug-finding prompts that an LLM can run against a codebase. It’s also platform and threat-model aware. Run these commands to install the skill:

```
claude skills add-marketplace https://github.com/trailofbits/skills
claude skills enable c-review --marketplace trailofbits/skills
```

## The Linux ping program challenge

The Linux warmup challenge we showed you in the last blog post has an obvious command injection issue.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>

#define ALLOWED_IP "127.3.3.1"

int main() {
    char ip_addr[128];
    struct in_addr to_ping_host, trusted_host;

    // get address
    if (!fgets(ip_addr, sizeof(ip_addr), stdin))
        return 1;
    ip_addr[strcspn(ip_addr, "\n")] = 0;

    // verify address
    if (!inet_aton(ip_addr, &to_ping_host))
        return 1;
    char *ip_addr_resolved = inet_ntoa(to_ping_host);

    // prevent SSRF
    if ((ntohl(to_ping_host.s_addr) >> 24) == 127)
        return 1;

    // only allowed
    if (!inet_aton(ALLOWED_IP, &trusted_host))
        return 1;
    char *trusted_resolved = inet_ntoa(trusted_host);

    if (strcmp(ip_addr_resolved, trusted_resolved) != 0)
        return 1;

    // ping
    char cmd[256];
    snprintf(cmd, sizeof(cmd), "ping '%s'", ip_addr);
    system(cmd);
    return 0;
}
```

There are three validations that have to be bypassed before the `system` call can be reached with malicious inputs:

1. The [`inet_aton` function](https://man7.org/linux/man-pages/man3/inet.3.html) “converts the Internet host address from the IPv4 numbers-and-dots notation into binary form” and “returns nonzero if the address is valid, zero if not.” Theoretically, if we provide an invalid IPv4 string as input, then the program should return early.
2. The `ntohl` call aims to prevent server-side request forgery (SSRF) attacks by disallowing addresses in 127.0.0.0/8 range.
3. The parsed IP address is normalized with an `inet_ntoa` call and compared against the `ALLOWED_IP`. We are only allowed to ping localhost, which should not be possible given the SSRF check (making the code effectively broken with this configuration).

The issue with the `inet_aton` function is that it [accepts trailing garbage](https://sourceware.org/bugzilla/show_bug.cgi?id=20018). This behavior is not documented on its man page, making it a likely source of vulnerabilities. In our challenge, one can simply send “127.0.0.1 ‘; anything #” as valid input.

The gotcha with `inet_ntoa` is that it returns a pointer to a global buffer. Therefore, subsequent calls to the function overwrite previous outputs. In the challenge, `ip_addr_resolved` and `trusted_resolved` are the same pointer. When we provide “1.2.3.4” as input, `ip_addr_resolved` points to the string “1.2.3.4”, the SSRF check passes, the second call to `inet_ntoa` makes the `ip_addr_resolved` pointer point to “127.3.3.1”, and so the `strcmp` check passes too.

There are a few more functions that return pointers to static buffers; these are documented in the new C/C++ Testing Handbook chapter.

## The Windows driver registry challenge

We showed you this Windows Driver Framework (WDF) request handler from a Windows driver and asked you to spot the bugs.

```c
NTSTATUS
InitServiceCallback(
  _In_ WDFREQUEST Request
)
{
  NTSTATUS status;
  PWCHAR regPath = NULL;
  size_t bufferLength = 0;

  // fetch the product registry path from the request
  status = WdfRequestRetrieveInputBuffer(Request, 4, &regPath, &bufferLength);
  if (!NT_SUCCESS(status))
  {
    TraceEvents(
      TRACE_LEVEL_ERROR,
      TRACE_QUEUE,
      "%!FUNC! Failed to retrieve input buffer. Status: %d", (int)status
    );
    return status;
  }
  /* check that the buffer size is a null-terminated
     Unicode (UTF-16) string of a sensible size */
  if (bufferLength < 4 ||
    bufferLength > 512 ||
    (bufferLength % 2) != 0 ||
    regPath[(bufferLength / 2) - 1] != L'\0')
  {
    TraceEvents(
      TRACE_LEVEL_ERROR,
      TRACE_QUEUE,
      "%!FUNC! Buffer length %d was incorrect.", (int)bufferLength
    );
    return STATUS_INVALID_PARAMETER;
  }

  ProductVersionInfo version = { 0 };
  HandlerCallback handlerCallback = NewCallback;
  int readValue = 0;
  // read the major version from the registry
  RTL_QUERY_REGISTRY_TABLE regQueryTable[2];
  RtlZeroMemory(regQueryTable, sizeof(RTL_QUERY_REGISTRY_TABLE) * 2);
  regQueryTable[0].Name = L"MajorVersion";
  regQueryTable[0].EntryContext = &readValue;
  regQueryTable[0].Flags = RTL_QUERY_REGISTRY_DIRECT;
  regQueryTable[0].QueryRoutine = NULL;
  status = RtlQueryRegistryValues(
    RTL_REGISTRY_ABSOLUTE,
    regPath,
    regQueryTable,
    NULL,
    NULL
  );
  if (!NT_SUCCESS(status))
  {
    TraceEvents(
      TRACE_LEVEL_ERROR,
      TRACE_QUEUE,
      "%!FUNC! Failed to query registry. Status: %d", (int)status
    );
    return status;
  }
  TraceEvents(
    TRACE_LEVEL_INFORMATION,
    TRACE_QUEUE,
    "%!FUNC! Major version is %d",
    (int)readValue
  );
  version.Major = readValue;
  if (version.Major < 3)
  {
    // versions prior to 3.0 need an additional check
    RtlZeroMemory(regQueryTable, sizeof(RTL_QUERY_REGISTRY_TABLE) * 2);
    regQueryTable[0].Name = L"MinorVersion";
    regQueryTable[0].EntryContext = &readValue;
    regQueryTable[0].Flags = RTL_QUERY_REGISTRY_DIRECT;
    regQueryTable[0].QueryRoutine = NULL;
    status = RtlQueryRegistryValues(
      RTL_REGISTRY_ABSOLUTE,
      regPath,
      regQueryTable,
      NULL,
      NULL
    );
    if (!NT_SUCCESS(status))
    {
      TraceEvents(
        TRACE_LEVEL_ERROR,
        TRACE_QUEUE,
        "%!FUNC! Failed to query registry. Status: %d",
        (int)status
      );
      return status;
    }
    TraceEvents(
      TRACE_LEVEL_INFORMATION,
      TRACE_QUEUE,
      "%!FUNC! Minor version is %d", (int)readValue
    );
    version.Minor = readValue;
    if (!DoesVersionSupportNewCallback(version))
    {
      handlerCallback = OldCallback;
    }
  }
  SetGlobalHandlerCallback(handlerCallback);
}
```

The intended behavior of the code is to read some software version information from the registry using the `RtlQueryRegistryValues` API, then select one of two possible callback functions depending on that version information.

### An attacker-controlled registry path

The first bug is that the path to the registry key is provided in the request, without validating the path string or checking that the caller is authorized to access the specified registry key. This means that anyone who can call into this handler can pick which registry key gets read, even if they ordinarily wouldn’t have access to that key. How this path string is interpreted depends on the `RelativeTo` parameter of the `RtlQueryRegistryValues` call. In this case, `RelativeTo` is set to `RTL_REGISTRY_ABSOLUTE`, which means that the path will be treated as an absolute path to a registry key object (e.g., `\Registry\User\CurrentUser`). There are two main reasons why this is a potential security issue.

First, if an attacker can control which registry key is being read, then they can point it at a registry key they control the contents of, allowing them to further manipulate the driver behavior. This may lead to logical inconsistencies (e.g., the wrong callback being set) or, as we will see shortly, enable exploitation of security issues elsewhere in the code.

Second, this enables a confused deputy attack that can be used to leak registry information that would normally be inaccessible to the user due to access controls. For example, a registry key might have a DACL applied that prevents normal users from enumerating its subkeys or reading any of the values inside those keys. Since the handler doesn’t check whether the call has sufficient rights to read the key, and the code emits a trace message and passes back the status code from `RtlQueryRegistryValues`, it can be used as an oracle to check for the existence of any registry key. It can also be used to leak any registry value named `MajorVersion` (and sometimes also `MinorVersion`) anywhere in the registry, but this is unlikely to be particularly useful in practice.

### Missing type checks with RTL\_QUERY\_REGISTRY\_DIRECT

The more serious bugs in this case arise from the flags set in the `RTL_QUERY_REGISTRY_TABLE` structs. The `RtlQueryRegistryValues` API takes in an array of these structs, terminated by an all-zero entry, to describe which registry values should be read from the specified key and how they should be processed and returned. There are two primary modes of operation here: callback or direct. In callback mode, which is the default, the `QueryRoutine` field of the struct points to a callback function that receives the value read from the registry. In direct mode, the `QueryRoutine` field is ignored and the value is instead written directly to a buffer whose location is passed in the `EntryContext` field. Direct mode is selected by including `RTL_QUERY_REGISTRY_DIRECT` in the `Flags` field.

In our example, the `MajorVersion` value is read using the following code:

```c
HandlerCallback handlerCallback = NewCallback;
  int readValue = 0;
  // read the major version from the registry
  RTL_QUERY_REGISTRY_TABLE regQueryTable[2];
  RtlZeroMemory(regQueryTable, sizeof(RTL_QUERY_REGISTRY_TABLE) * 2);
  regQueryTable[0].Name = L"MajorVersion";
  regQueryTable[0].EntryContext = &readValue;
  regQueryTable[0].Flags = RTL_QUERY_REGISTRY_DIRECT;
  regQueryTable[0].QueryRoutine = NULL;
  status = RtlQueryRegistryValues(
    RTL_REGISTRY_ABSOLUTE,
    regPath,
    regQueryTable,
    NULL,
    NULL
  );
```

Here, `RTL_QUERY_REGISTRY_DIRECT` is used to select direct mode, and the buffer points to `readValue`, which is an integer variable on the stack. You might notice something important, though: at no point has the code specified what type of value is being read, nor has it specified the size of the buffer. It is clear from the context that this code is expecting to read a `REG_DWORD`, but what if the `MajorVersion` value isn’t a `REG_DWORD`?

### A first attempt at exploitation

Let’s try to exploit this using a `REG_QWORD`. A `REG_DWORD` value is a 32-bit unsigned integer, whereas a `REG_QWORD` is a 64-bit unsigned integer, so if we make `MajorVersion` a `REG_QWORD` value instead, then we should be able to overwrite four bytes immediately after `readValue` on the stack. Since `HKEY_CURRENT_USER` is writable by low-privilege users, we can create a key somewhere in there, place a `REG_QWORD` value called `MajorVersion` in there, and pass the path of that key to the driver. And success, we get a BSOD!

Except… it’s not quite what we wanted. The bugcheck code is `KERNEL_SECURITY_CHECK_FAILURE`, which isn’t really what we would expect if we successfully overwrote some of the stack. Why is this happening? The answer is in the [documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-rtlqueryregistryvalues):

> Starting with Windows 8, if an `RtlQueryRegistryValues` call accesses an untrusted hive, and the caller sets the `RTL_QUERY_REGISTRY_DIRECT` flag for this call, the caller must additionally set the `RTL_QUERY_REGISTRY_TYPECHECK` flag. A violation of this rule by a call from user mode causes an exception. A violation of this rule by a call from kernel mode causes a 0x139 bug check (`KERNEL_SECURITY_CHECK_FAILURE`).
>
> Only system hives are trusted. An `RtlQueryRegistryValues` call that accesses a system hive does not cause an exception or a bug check if the `RTL_QUERY_REGISTRY_DIRECT` flag is set and the `RTL_QUERY_REGISTRY_TYPECHECK` flag is not set. However, as a best practice, the `RTL_QUERY_REGISTRY_TYPECHECK` flag should always be set if the `RTL_QUERY_REGISTRY_DIRECT` flag is set.
>
> Similarly, in versions of Windows before Windows 8, as a best practice, an `RtlQueryRegistryValues` call that sets the `RTL_QUERY_REGISTRY_DIRECT` flag should additionally set the `RTL_QUERY_REGISTRY_TYPECHECK` flag. However, failure to follow this recommendation does not cause an exception or a bug check.
> This protective behavior was introduced as a response to [MS11-011](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2011/ms11-011), in which this registry type confusion bug was first reported.

To summarize, if you try to read from an untrusted registry hive using `RtlQueryRegistryValues` with `RTL_QUERY_REGISTRY_DIRECT` set but without also setting `RTL_QUERY_REGISTRY_TYPECHECK`, then Windows will automatically raise a bugcheck to crash the system and prevent the operation from succeeding.

The `RTL_QUERY_REGISTRY_TYPECHECK` flag allows the caller to specify an expected type as part of the query table entry, thus mitigating the type confusion bug. Since this flag is not set in our example, a bugcheck will be triggered if we attempt to read from any registry hive other than the following trusted system hives:

- `\REGISTRY\MACHINE\HARDWARE`
- `\REGISTRY\MACHINE\SOFTWARE`
- `\REGISTRY\MACHINE\SYSTEM`
- `\REGISTRY\MACHINE\SECURITY`
- `\REGISTRY\MACHINE\SAM`

`HKEY_CURRENT_USER` is not included within this set, which explains why we saw the `KERNEL_SECURITY_CHECK_FAILURE` bugcheck when we tried to exploit it that way. This downgrades us from a potential kernel privilege escalation bug to a local denial of service. Still a bug, but not quite as exciting.

### Finding writable keys in trusted hives

However, who says we can’t write values somewhere within these trusted hives? All it takes is a single key within one of those hives with a DACL that allows a lower-privileged user to write to it. Finding these isn’t too hard; the [NtObjectManager powershell module](https://www.powershellgallery.com/packages/NtObjectManager/) has a command named `Get-AccessibleKey` that is perfect for the task:

`Get-AccessibleKey \Registry\Machine -Recurse -Access SetValue`

This command searches recursively within the `\Registry\Machine` object namespace for keys that the current process has permissions to set values within. Running it as a regular desktop user returns thousands of options that can be written without UAC elevation! Nice.

However, for style points, we can go one step further. [Mandatory integrity control (MIC)](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control), one of the key access control features in Windows that underpins UAC, allows processes to run with higher or lower privileges than would normally be assigned to the user that ran them. Most desktop processes run at the medium integrity level (IL). Elevating a process via UAC (often referred to as “run as administrator”) typically increases the process’s IL to high. There is also a low IL, which is often used to sandbox certain processes for security reasons, significantly limiting which resources they can access. Any securable object on Windows can have a mandatory label applied to its system access control list (SACL), and that mandatory label specifies the ILs that are allowed to access the object. The SACL is checked before the DACL, meaning that the IL check must pass even if the DACL would normally grant the user permissions to access the object. This means that a process running with a low-integrity security token cannot access a medium-integrity object, and a process running with a medium-integrity security token cannot access a high-integrity object. So, can we find any cases where we could write to one of the trusted system hives from a low-integrity process?

To check for keys that are accessible at a low IL, the first thing we want to do is duplicate our process token and apply a low integrity label to it:

`$token = Get-NtToken -Primary -Duplicate -IntegrityLevel Low`

This gives us a copy of our current process’s security token that behaves as if we were running at a low IL. Using this, we then rerun the scan, passing in that modified token:

`Get-AccessibleKey \Registry\Machine -Recurse -Access SetValue -Token $token`

This does actually return a few results, on both Windows 10 and 11. Here are two of the most interesting:

`\REGISTRY\MACHINE\SOFTWARE\Microsoft\DRM``\REGISTRY\MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\PlayReady\Troubleshooter`

Both of these keys allow a low-integrity token to write to them. The `DRM` key’s DACL has fairly complex permissions applied but grants the Set Value permission to the Everyone group. The `PlayReady\Troubleshooter` key’s DACL grants Full Control to Users, ALL APPLICATION PACKAGES, and ALL RESTRICTED APP PACKAGES. Either of these two keys can be abused to plant controlled registry values within a trusted system hive from a low privilege level.

(Note: Whether or not the driver’s request endpoint can be called from a low IL is a different matter, but this is just for fun and style points, so let’s ignore that for now.)

If we set a `REG_QWORD` value called `MajorVersion` in the `DRM` key, then pass that key’s path to the WDF handler, we can now overwrite four bytes of stack past the end of `readValue` with values that we control. Since `handlerCallback` was declared adjacent to `readValue`, there’s a chance that we can overwrite half of that function pointer! If that callback is called later, then we obtain partial control over the instruction pointer, which is a fairly strong primitive for local privilege escalation (LPE). This does depend on stack alignment, however, and it would not be surprising if the 32-bit `readValue` variable ended up 64-bit aligned, leaving a gap, so this approach may not get us far in practice.

Can we do better?

### A string is a type of integer, right?

Ok, so far we’ve only explored what happens when we exploit the type confusion with `REG_QWORD`, but what happens if we use `REG_SZ`?

![“Samuel L. Jackson meme”](https://blog.trailofbits.com/2026/05/05/c/c-checklist-challenges-solved/cc-checklist-challenges-solved-image-1_hu_fe8665a0cbfe6e6b.webp)

In the case of `REG_SZ` (i.e., a string value), the documentation says the following about `RtlQueryRegistryValues`’ behavior in direct mode:

> A null-terminated Unicode string (such as `REG_SZ`, `REG_EXPAND_SZ`):
> `EntryContext` must point to an initialized `UNICODE_STRING` structure. If the `Buffer` member of `UNICODE_STRING` is NULL, the routine allocates storage for the string data. Otherwise, it stores the string data in the buffer that `Buffer` points to.

Let’s try exploiting this. `RtlQueryRegistryValues` will interpret the `EntryContext` field as if it were a `UNICODE_STRING` struct, but it’s actually pointing at `readValue`, which is an `int`. Here’s what a `UNICODE_STRING` looks like:

```c
typedef struct _UNICODE_STRING {
  USHORT Length;
  USHORT MaximumLength;
  PWSTR  Buffer;
} UNICODE_STRING, *PUNICODE_STRING;
```

In the first call that the code makes to `RtlQueryRegistryValues`, when reading `MajorVersion`, the value of `readValue` has been initialized to zero. Since `readValue` is four bytes and a `USHORT` is two bytes, interpreting `readValue` as a `UNICODE_STRING` at that time will result in both `Length` and `MaximumLength` being zero and `Buffer` containing whatever’s immediately after `readValue` in the stack. Since the length of the buffer is zero, `RtlQueryRegistryValues` will just return `STATUS_BUFFER_TOO_SMALL` and not attempt to write to the `Buffer` field.

However, let’s take a look at the second call to `RtlQueryRegistryValues`:

```c
version.Major = readValue;
  if (version.Major < 3)
  {
    // versions prior to 3.0 need an additional check
    RtlZeroMemory(regQueryTable, sizeof(RTL_QUERY_REGISTRY_TABLE) * 2);
    regQueryTable[0].Name = L"MinorVersion";
    regQueryTable[0].EntryContext = &readValue;
    regQueryTable[0].Flags = RTL_QUERY_REGISTRY_DIRECT;
    regQueryTable[0].QueryRoutine = NULL;
    status = RtlQueryRegistryValues(
      RTL_REGISTRY_ABSOLUTE,
      regPath,
      regQueryTable,
      NULL,
      NULL
    );
    // ...
```

This part of the code first checks if the `MajorVersion` value is less than three and, if so, reads the `MinorVersion` value using the same approach as before. A key observation here is that `readValue` is not reinitialized between the calls. This gives us some extra control: by leaving `MajorVersion` as a `REG_DWORD`, as originally intended by the code, we can have the first `RtlQueryRegistryValues` call load a value into `readValue`. Then, when the second call to `RtlQueryRegistryValues` is made, to read `MinorVersion`, we control the first four bytes of data pointed to by `EntryContext`. If `MinorVersion` is a `REG_SZ` value, a type confusion occurs where `RtlQueryRegistryValues` expects `EntryContext` to point to a `UNICODE_STRING`, causing the contents of the `MajorVersion` integer to be reinterpreted as the `Length` and `MaximumLength` fields. The only restriction is that we need the major version check to pass (i.e., `version.Major` must be less than 3) in order for the second registry query to take place. However, this turns out to be easy: if we set the `MajorVersion` value to `0xF000F002`, the code will interpret this as `-268374014` because `readValue` is a signed 32-bit integer. The `Length` and `MaximumLength` fields, however, are unsigned 16-bit integers, causing the `0xF000F002` value to get interpreted as the following when type confused as a `UNICODE_STRING`:

```c
USHORT Length = F000;
  USHORT MaximumLength = F002;
  PWSTR  Buffer = ????????`????????;
```

The `Buffer` field ends up pointing at whatever’s next in the stack. If we combine this current approach with the `REG_QWORD` trick from before, we can also overwrite four bytes of the `Buffer` pointer during the `MajorVersion` read. This means we partially control the address being written to, we fully control the length of what is written, and we can write any UTF-16 string there. This gets us a semi-controlled write-what-where primitive in the kernel. Nice!

But can we do _even better_?

### A fully controlled stack overwrite with REG\_BINARY

Let’s take a look at what happens if we try a `REG_BINARY` value instead. Here’s what the documentation has to say about such values in direct mode:

> Nonstring data with size, in bytes, greater than `sizeof(ULONG)`:
> The buffer pointed to by `EntryContext` must begin with a signed `LONG` value. The magnitude of the value must specify the size, in bytes, of the buffer. If the sign of the value is negative, `RtlQueryRegistryValues` will only store the data of the key value. Otherwise, it will use the first `ULONG` in the buffer to record the value length, in bytes, the second `ULONG` to record the value type, and the rest of the buffer to store the value data.

This one is a bit more complicated, with two possible cases for the format of the buffer. In both cases, the buffer pointed to by `EntryContext` is expected to be prefilled with a signed `LONG` value that tells `RtlQueryRegistryValues` how large the buffer is. A `LONG` is just a 32-bit integer, so a signed `LONG` is functionally equivalent to `int` for this case. The interesting part is that this length value can either be positive or negative. If the value is negative, the API will copy the `REG_BINARY` data directly into the buffer pointed to by `EntryContext`. If the value is positive, it will first write the length of the `REG_BINARY` data into the first `ULONG` of the buffer, then it will write the `REG_BINARY` type value into the second `ULONG` of the buffer, and finally it will copy the `REG_BINARY` data into the remainder of the buffer.

You may have figured out the exploit already here. The `MinorVersion` registry value is only read when the `MajorVersion` is less than 3. If we set `MajorVersion` to some negative number, this check will pass. This negative number ends up left in `readValue` for the second `RtlQueryRegistryValues` call. If the `MinorVersion` value is a `REG_BINARY`, `RtlQueryRegistryValues` treats the first `ULONG` in the “buffer” as being the signed length field. Since our “buffer” is just whatever was in `readValue` from the previous call, this causes `RtlQueryRegistryValues` to copy the contents of the registry value into the “buffer,” which is really just stack memory starting at `readBytes`. Since we control the magnitude of the negative number, we therefore control the purported length of the buffer, allowing us to control the length of the overwrite. And, since the contents of the `REG_BINARY` value can be anything we like, it means we control what is overwritten.

For example, if we create a `REG_DWORD` value called `MajorVersion` with a value of `0xFFFFFFF4`, then create a `REG_BINARY` value called `MinorVersion` with a value of `00 00 00 00 DE AD BE EF DE AD BE EF`, this causes the first `RtlQueryRegistryValues` call to fill `readValue` with -12, which the second `RtlQueryRegistryValues` call interprets as a 12-byte buffer where only the binary should be copied. This results in `RtlQueryRegistryValues` copying `00 00 00 00` into `readValue`, then writing `DE AD BE EF DE AD BE EF` onto the stack afterwards. Assuming that the `handlerCallback` function pointer is stored after the `readValue` variable on the stack, we can now overwrite it with whatever we like. If this callback is invoked anywhere in the future, we gain control over the instruction pointer, leading to a kernel LPE.

But can we do _even better still_? If you think you can, get in touch! We’d love to hear your tips and tricks.

## Your turn

These challenges only scratch the surface of what the [C/C++ Testing Handbook chapter](https://appsec.guide/docs/languages/c-cpp/) covers—from seccomp sandbox escapes to Windows path traversal via WorstFit Unicode bugs. Read the chapter and follow the checklist against a codebase you know well. Pair it with a run of the [c-review skill](https://github.com/trailofbits/skills/tree/main/plugins/c-review), if you’re inclined. If you find a pattern we haven’t documented yet, open a PR. We’d especially love to hear from anyone who found a cleaner exploitation path for the driver challenge than the ones we showed here. And, as always, if you need help securing your C/C++ systems, [contact us](https://www.trailofbits.com/contact/).