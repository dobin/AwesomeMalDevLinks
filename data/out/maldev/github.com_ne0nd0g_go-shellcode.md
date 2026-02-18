# https://github.com/Ne0nd0g/go-shellcode

[Skip to content](https://github.com/Ne0nd0g/go-shellcode#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Ne0nd0g/go-shellcode) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Ne0nd0g/go-shellcode) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Ne0nd0g/go-shellcode) to refresh your session.Dismiss alert

{{ message }}

[Ne0nd0g](https://github.com/Ne0nd0g)/ **[go-shellcode](https://github.com/Ne0nd0g/go-shellcode)** Public

- [Notifications](https://github.com/login?return_to=%2FNe0nd0g%2Fgo-shellcode) You must be signed in to change notification settings
- [Fork\\
236](https://github.com/login?return_to=%2FNe0nd0g%2Fgo-shellcode)
- [Star\\
1.2k](https://github.com/login?return_to=%2FNe0nd0g%2Fgo-shellcode)


A repository of Windows Shellcode runners and supporting utilities. The applications load and execute Shellcode using various API calls or techniques.


### License

[GPL-3.0 license](https://github.com/Ne0nd0g/go-shellcode/blob/master/LICENSE)

[1.2k\\
stars](https://github.com/Ne0nd0g/go-shellcode/stargazers) [236\\
forks](https://github.com/Ne0nd0g/go-shellcode/forks) [Branches](https://github.com/Ne0nd0g/go-shellcode/branches) [Tags](https://github.com/Ne0nd0g/go-shellcode/tags) [Activity](https://github.com/Ne0nd0g/go-shellcode/activity)

[Star](https://github.com/login?return_to=%2FNe0nd0g%2Fgo-shellcode)

[Notifications](https://github.com/login?return_to=%2FNe0nd0g%2Fgo-shellcode) You must be signed in to change notification settings

# Ne0nd0g/go-shellcode

master

[**3** Branches](https://github.com/Ne0nd0g/go-shellcode/branches) [**0** Tags](https://github.com/Ne0nd0g/go-shellcode/tags)

[Go to Branches page](https://github.com/Ne0nd0g/go-shellcode/branches)[Go to Tags page](https://github.com/Ne0nd0g/go-shellcode/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Ne0nd0g](https://avatars.githubusercontent.com/u/5638474?v=4&size=40)](https://github.com/Ne0nd0g)[Ne0nd0g](https://github.com/Ne0nd0g/go-shellcode/commits?author=Ne0nd0g)<br>[Fixed UUID & added EnumerateLoadedModules](https://github.com/Ne0nd0g/go-shellcode/commit/cea4e9c8af45a8c19554b590f8586c03d4a22d2b)<br>5 years agoOct 29, 2021<br>[cea4e9c](https://github.com/Ne0nd0g/go-shellcode/commit/cea4e9c8af45a8c19554b590f8586c03d4a22d2b) · 5 years agoOct 29, 2021<br>## History<br>[15 Commits](https://github.com/Ne0nd0g/go-shellcode/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Ne0nd0g/go-shellcode/commits/master/) 15 Commits |
| [cmd](https://github.com/Ne0nd0g/go-shellcode/tree/master/cmd "cmd") | [cmd](https://github.com/Ne0nd0g/go-shellcode/tree/master/cmd "cmd") | [Fixed UUID & added EnumerateLoadedModules](https://github.com/Ne0nd0g/go-shellcode/commit/cea4e9c8af45a8c19554b590f8586c03d4a22d2b "Fixed UUID & added EnumerateLoadedModules") | 5 years agoOct 29, 2021 |
| [LICENSE](https://github.com/Ne0nd0g/go-shellcode/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/Ne0nd0g/go-shellcode/blob/master/LICENSE "LICENSE") | [Initial commit](https://github.com/Ne0nd0g/go-shellcode/commit/2cddc8f871081f291de6e4cf18d7207b5b1e688a "Initial commit") | 6 years agoMar 21, 2020 |
| [README.MD](https://github.com/Ne0nd0g/go-shellcode/blob/master/README.MD "README.MD") | [README.MD](https://github.com/Ne0nd0g/go-shellcode/blob/master/README.MD "README.MD") | [Added NtQueueApcThreadEx](https://github.com/Ne0nd0g/go-shellcode/commit/6173363a9f84fa4417b53a0987cc16b74258f6a9 "Added NtQueueApcThreadEx") | 5 years agoJun 11, 2021 |
| [go.mod](https://github.com/Ne0nd0g/go-shellcode/blob/master/go.mod "go.mod") | [go.mod](https://github.com/Ne0nd0g/go-shellcode/blob/master/go.mod "go.mod") | [Added EarlyBird technique](https://github.com/Ne0nd0g/go-shellcode/commit/c4717fc5a9498b36dbe79d81500f77bb95bfc1bd "Added EarlyBird technique") | 5 years agoJun 10, 2021 |
| [go.sum](https://github.com/Ne0nd0g/go-shellcode/blob/master/go.sum "go.sum") | [go.sum](https://github.com/Ne0nd0g/go-shellcode/blob/master/go.sum "go.sum") | [Added EarlyBird technique](https://github.com/Ne0nd0g/go-shellcode/commit/c4717fc5a9498b36dbe79d81500f77bb95bfc1bd "Added EarlyBird technique") | 5 years agoJun 10, 2021 |
| View all files |

## Repository files navigation

# go-shellcode

[Permalink: go-shellcode](https://github.com/Ne0nd0g/go-shellcode#go-shellcode)

`go-shellcode` is a repository of Windows Shellcode runners and supporting utilities. The applications load and execute Shellcode using various API calls or techniques.

The available Shellcode runners include:

- [CreateFiber](https://github.com/Ne0nd0g/go-shellcode#CreateFiber)
- [CreateProcess](https://github.com/Ne0nd0g/go-shellcode#CreateProcess)
- [CreateProcessWithPipe](https://github.com/Ne0nd0g/go-shellcode#CreateProcessWithPipe)
- [CreateRemoteThread](https://github.com/Ne0nd0g/go-shellcode#CreateRemoteThred)
- [CreateRemoteThreadNative](https://github.com/Ne0nd0g/go-shellcode#CreateRemoteThreadNative)
- [CreateThread](https://github.com/Ne0nd0g/go-shellcode#CreateThread)
- [CreateThreadNative](https://github.com/Ne0nd0g/go-shellcode#CreateThreadNative)
- [EarlyBird](https://github.com/Ne0nd0g/go-shellcode#EarlyBird)
- [EtwpCreateEtwThread](https://github.com/Ne0nd0g/go-shellcode#EtwpCreateEtwThread)
- [NtQueueApcThreadEx (local)](https://github.com/Ne0nd0g/go-shellcode#NtQueueApcThreadEx-(local))
- [RtlCreateUserThread](https://github.com/Ne0nd0g/go-shellcode#RtlCreateUserThread)
- [Syscall](https://github.com/Ne0nd0g/go-shellcode#Syscall)
- [Shellcode Utils](https://github.com/Ne0nd0g/go-shellcode#ShellcodeUtils)
- [UuidFromStringA](https://github.com/Ne0nd0g/go-shellcode#UuidFromStringA)

## CreateFiber

[Permalink: CreateFiber](https://github.com/Ne0nd0g/go-shellcode#createfiber)

This application leverages the Windows [CreateFiber](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createfiber) function from the `Kernel32.dll` to execute shellcode within this application's process. This is usefull when you want to avoid remote process injection and want to avoid calling `CreateThread`. This application **DOES NOT** leverage functions from the `golang.org/x/sys/windows` package. The most significant difference is that this application loads all the necessary DLLs and Procedures itself and uses the procedure's Call() function.

**NOTE:** I have not figured out way to have the process exit and you will have to manually terminate it.

The application can be compiled with the following command on a Windows host from the project's root directory:

`set GOOS=windows GOARCH=amd64;go build -o CreateFiber.exe .\cmd\CreateFiber\main.go`

## CreateProcess

[Permalink: CreateProcess](https://github.com/Ne0nd0g/go-shellcode#createprocess)

This application leverages the Windows [CreateProcess](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw) function from `Kernel32.dll`. The process is created in a suspended state, the [AddressOfEntryPoint](https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_optional_header32) in the `IMAGE_OPTIONAL_HEADER` structure is updated to execute shellcode in the childprocess, and then the process is resumed. This is a type of process hollowing but the existing PE is **NOT** unmapped and the ThreadContext is **NOT** updated. The provided shellcode architecture (i.e. x86 or x64) must match the architecture of the child process.

The application can be compiled with the following command on a Windows host from the project's root directory:

`set GOOS=windows GOARCH=amd64;go build -o CreateProcess.exe .\cmd\CreateProcess\main.go`

## CreateProcessWithPipe

[Permalink: CreateProcessWithPipe](https://github.com/Ne0nd0g/go-shellcode#createprocesswithpipe)

This application leverages the Windows [CreateProcess](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw) function from `Kernel32.dll`. The process is created in a suspended state, the [AddressOfEntryPoint](https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_optional_header32) in the `IMAGE_OPTIONAL_HEADER` structure is updated to execute shellcode in the childprocess, and then the process is resumed. This is a type of process hollowing but the existing PE is **NOT** unmapped and the ThreadContext is **NOT** updated. The provided shellcode architecture (i.e. x86 or x64) must match the architecture of the child process.

This application differs from [CreateProcess](https://github.com/Ne0nd0g/go-shellcode#CreateProcess) because it will collect any data written to **STDOUT** or **STDERR** in the child process and return it to the parent process. Data is collected by using the [CreatePipe](https://docs.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-createpipe) function to create an anonymous pipe that the parent and child process communicate over. This is usefull when using tools like [Donut](https://github.com/TheWover/donut) to execute a .NET assembly in a child process as shellcode and to retrieve the output of the executed program. The following command can be used to generate position-independent shellcode to run [Seatbelt](https://github.com/GhostPack/Seatbelt) with Donut [v0.9.3](https://github.com/TheWover/donut/releases/tag/v0.9.3):

`.\donut.exe -o donut_v0.9.3_Seatbelt.bin -x 2 -c Seatbelt.Program -m Main -p "ARPTable" Seatbelt.exe`

The application can be compiled with the following command on a Windows host from the project's root directory:

`set GOOS=windows GOARCH=amd64;go build -o CreateProcessWithPipe.exe .\cmd\CreateProcessWithPipe\main.go`

## CreateRemoteThread

[Permalink: CreateRemoteThread](https://github.com/Ne0nd0g/go-shellcode#createremotethread)

This application leverages the Windows [CreateRemoteThread](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread) function from `Kernel32.dll` to execute shellocde in a remote process. The application requires that the target process to inject into is already running. The targe Process Identifier (PID) can provided at runtime for testing using the `-pid` command line flag. Hardcode the PID in the following line of code for operational use by replacing the `0` with your target PID:

`pid := flag.Int("pid", 0, "Process ID to inject shellcode into")`

This application leverages functions from the `golang.org/x/sys/windows` package, where feasible, like the [`windows.OpenProcess()`](https://github.com/golang/sys/blob/a7d97aace0b0/windows/zsyscall_windows.go#L1197). The application can be compiled wit the following command on a Windows host from the project's root directory:

`set GOOS=windows GOARCH=amd64;go build -o CreateRemoteThread.exe .\cmd\CreateRemoteThread\main.go`

## CreateRemoteThreadNative

[Permalink: CreateRemoteThreadNative](https://github.com/Ne0nd0g/go-shellcode#createremotethreadnative)

This application leverages the Windows [CreateRemoteThread](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread) function from `Kernel32.dll` to execute shellocde in a remote process. The application requires that the target process to inject into is already running. The targe Process Identifier (PID) can provided at runtime for testing using the `-pid` command line flag. Hardcode the PID in the following line of code for operational use by replacing the `0` with your target PID:

`pid := flag.Int("pid", 0, "Process ID to inject shellcode into")`

This application **DOES NOT** leverage functions from the `golang.org/x/sys/windows` package. The most significant difference is that this application loads all the necessary DLLs and Procedures itself and uses the procedure's Call() function. The application can be compiled with the following command on Windows host from the project's root directory:

`set GOOS=windows GOARCH=amd64;go build -o CreateRemoteThreadNative.exe .\cmd\CreateRemoteThreadNative\main.go`

## CreateThread

[Permalink: CreateThread](https://github.com/Ne0nd0g/go-shellcode#createthread)

This application leverages the Windows [CreateThread](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createthread) function from `Kernel32.dll` to execute shellcode within this application's process. This is usefull when you want to avoid remote process injection. This application leverages functions from the `golang.org/x/sys/windows` package, where feasible, like the [windows.VirtualAlloc()\`](https://github.com/golang/sys/blob/a7d97aace0b0/windows/zsyscall_windows.go#L1712). The application can be compiled with the following command on Windows host from the project's root directory:

`set GOOS=windows GOARCH=amd64;go build -o CreateThread.exe .\cmd\CreateThread\main.go`

## CreateThreadNative

[Permalink: CreateThreadNative](https://github.com/Ne0nd0g/go-shellcode#createthreadnative)

This application leverages the Windows [CreateThread](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createthread) function from the `Kernel32.dll` to execute shellcode within this application's process. This is usefull when you want to avoid remote process injection. This application **DOES NOT** leverage functions from the `golang.org/x/sys/windows` package. The most significant difference is that this application loads all the necessary DLLs and Procedures itself and uses the procedure's Call() function. The application can be compiled with the following command on Windows host from the project's root directory:

`set GOOS=windows GOARCH=amd64;go build -o CreateThreadNative.exe .\cmd\CreateThreadNative\main.go`

## EarlyBird

[Permalink: EarlyBird](https://github.com/Ne0nd0g/go-shellcode#earlybird)

The application leverages the Windows [CreateProcess](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw) function to create a process in a suspended state. Once the child process is suspended, the Windows [QueueUserAPC](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc) function is used to add a UserAPC to the child process that points to the allocate shellcode. Next, [ResumeThread](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-resumethread) is called, which subsequently calls the undocumented [NtTestAlert](http://undocumented.ntinternals.net/) function that will execute the created UserAPC and in turn the shellcode. This is usefull because the shellcode will execute before AV/EDR can hook functions to support detection. Reference [New 'Early Bird' Code Injection Technique Discovered](https://www.cyberbit.com/blog/endpoint-security/new-early-bird-code-injection-technique-discovered/). The application can be compiled with the following command on Windows host from the project's root directory:

`export GOOS=windows GOARCH=amd64;go build -o goEarlyBird.exe cmd\EarlyBird\main.go`

## EtwpCreateEtwThread

[Permalink: EtwpCreateEtwThread](https://github.com/Ne0nd0g/go-shellcode#etwpcreateetwthread)

This application leverages the Windows [EtwpCreateEtwThread](https://www.geoffchappell.com/studies/windows/win32/ntdll/api/etw/index.htm) function from `ntdll.dll` to execute shellcode within this application's process. Original work by [TheWover](https://gist.github.com/TheWover/b2b2e427d3a81659942f4e8b9a978dc3). This is usefull when you want to avoid remote process injection. This application **DOES NOT** leverage functions from the `golang.org/x/sys/windows` package. The most significant difference is that this application loads all the necessary DLLs and Procedures itself and uses the procedure's Call() function. The application can be compiled with the following command on a Windows host from the project's root directory:

`set GOOS=windows GOARCH=amd64;go build -o EtwpCreateEtwThread.exe .\cmd\EtwpCreateEtwThread\main.go`

## NtQueueApcThreadEx (local)

[Permalink: NtQueueApcThreadEx (local)](https://github.com/Ne0nd0g/go-shellcode#ntqueueapcthreadex-local)

This application uses the undocumented [NtQueueApcThreadEx](https://docs.rs/ntapi/0.3.1/ntapi/ntpsapi/fn.NtQueueApcThreadEx.html) to create a "Special User APC" in the current thread of the current process to execute shellcode. Because the shellcode is loaded and executed in the current process, it is "local". This same technique can be used for a remote process. _NOTE:_ This will only work on Windows 7 or later. Reference [APC Series: User APC API](https://repnz.github.io/posts/apc/user-apc/).

`export GOOS=windows GOARCH=amd64;go build -o goNtQueueApcThreadEx-Local.exe cmd\NtQueueApcThreadEx-Local\main.go`

## RtlCreateUserThread

[Permalink: RtlCreateUserThread](https://github.com/Ne0nd0g/go-shellcode#rtlcreateuserthread)

This application leverages the Windows [RtlCreateUserThread](https://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented%20Functions%2FExecutable%20Images%2FRtlCreateUserThread.html) function from `ntdll.dll` to execute shellocde in a remote process. The application requires that the target process to inject into is already running. The targe Process Identifier (PID) can provided at runtime for testing using the `-pid` command line flag. Hardcode the PID in the following line of code for operational use by replacing the `0` with your target PID:

`pid := flag.Int("pid", 0, "Process ID to inject shellcode into")`

This application **DOES NOT** leverage functions from the `golang.org/x/sys/windows` package. The most significant difference is that this application loads all the necessary DLLs and Procedures itself and uses the procedure's Call() function. The application can be compiled with the following command on a Windows host from the project's root directory:

`set GOOS=windows GOARCH=amd64;go build -o RtlCreateUserThread.exe .\cmd\RtlCreateUserThread\main.go`

## Syscall

[Permalink: Syscall](https://github.com/Ne0nd0g/go-shellcode#syscall)

This application executes Shellcode in the current running proccess by making a Syscall on the Shellcode's entry point. This application **DOES NOT** leverage functions from the `golang.org/x/sys/windows` package. The application can be compiled with the following command on a Windows host from the project's root directory:

`set GOOS=windows GOARCH=amd64;go build -o Syscall.exe .\cmd\Syscall\main.go`

## UuidFromStringA

[Permalink: UuidFromStringA](https://github.com/Ne0nd0g/go-shellcode#uuidfromstringa)

This application leverages the Windows [UuidFromStringA](https://docs.microsoft.com/en-us/windows/win32/api/rpcdce/nf-rpcdce-uuidfromstringa) function to load shellcode to a memory address and then calls the [EnumSystemLocalesA](https://docs.microsoft.com/en-us/windows/win32/api/winnls/nf-winnls-enumsystemlocalesa) function to execute the shellcode. This method of loading and executing shellcode was derived from nccgroup's [RIFT: Analysing a Lazarus Shellcode Execution Method](https://research.nccgroup.com/2021/01/23/rift-analysing-a-lazarus-shellcode-execution-method/). For this application, memory is allocated on the heap and it does not use VirtualAlloc. The application can be compiled with the following command on a Windows host from the project's root directory:

`set GOOS=windows GOARCH=amd64;go build -o UuidFromString.exe .\cmd\UuidFromString\main.go`

## ShellcodeUtils

[Permalink: ShellcodeUtils](https://github.com/Ne0nd0g/go-shellcode#shellcodeutils)

This application is used to transform shellcode binary files. The program depends that the input file is a binary file (.bin) that contains the hex bytes of the shellcode. ShellcodeUtils can just base64 encode your input file or it can XOR, RC4, or AES256-GCM encrypt it. The tools can also be used to decrypt files as well.

ShellcodeUtils help menu:

```
  -base64
        Base64 encode the output. Can be used with or without encryption
  -i string
        Input file path of binary file
  -key string
        Encryption key
  -mode string
        Mode of operation to perform on the input file [encrypt,decrypt] (default "encrypt")
  -nonce string
        Nonce, in hex, used to decrypt an AES256 input file. Only used during decryption
  -o string
        Output file path
  -salt string
        Salt, in hex, used to generate an AES256 32-byte key through Argon2. Only used during decryption
  -type string
        The type of encryption to use [xor, aes256, rc4, null]
  -v    Enable verbose output
```

Example of only Base64 encoding the input file and saving it a text file:

```
PS C:\Users\bob> .\ShellcodeUtils.exe -i C:\Users\bob\calc.bin -o C:\Users\bob\calc.b64.txt -base64 -v
[-]Output directory: C:\Users\bob\
[-]Output file name: calc.b64.txt
[-]File contents (hex): 505152535657556a605a6863616c6354594883ec2865488b32488b7618488b761048ad488b30488b7e3003573c8b5c17288b741f204801fe8b541f240fb72c178d5202ad813c0757696e4575ef8b741f1c4801fe8b34ae4801f799ffd74883c4305d5f5e5b5a5958c3
[-]No encryption type provided, continuing on...
[+]Output (string):
UFFSU1ZXVWpgWmhjYWxjVFlIg+woZUiLMkiLdhhIi3YQSK1IizBIi34wA1c8i1wXKIt0HyBIAf6LVB8kD7csF41SAq2BPAdXaW5Fde+LdB8cSAH+izSuSAH3mf/XSIPEMF1fXltaWVjD
[+] encrypt input and wrote 140 bytes to: C:\Users\bob\calc.b64.txt
```

Example XOR encrypting input file with a key of `Sh3!1z` AND base64 encoding the output:

```
PS C:\Users\bob> .\ShellcodeUtils.exe -i C:\Users\bob\calc.bin -o C:\Users\bob\calc.xor.b64.txt -mode encrypt -type xor -key Sh3!1z -v
[-]Output directory: C:\Users\bob\
[-]Output file name: calc.xor.b64.txt
[-]File contents (hex): 505152535657556a605a6863616c6354594883ec2865488b32488b7618488b761048ad488b30488b7e3003573c8b5c17288b741f204801fe8b541f240fb72c178d5202ad813c0757696e4575ef8b741f1c4801fe8b34ae4801f799ffd74883c4305d5f5e5b5a5958c3
[-]XOR encrypting input file with key: Sh3!1z
[+]Output (hex):
03396172672d0602537b5919320450756832d0841b4479f16120b8572932d81e23699c32d8587baa4f4a503f0faa6d6d7be3473e11325296b8752e5e5cdf1f36bc2851c5b21d362d3a067654def127772f693084d85c9d69308dca97e469b2be63356c7f6a200a30f0
[+]xor encrypt input and wrote 105 bytes to: C:\Users\bob\calc.xor.b64.txt
```

Example AES256-GCM encrypting the input file with a password of `Sh3!1z` WITHOUT base64 encoding the ouput:

```
PS C:\Users\bob> .\ShellcodeUtils.exe -i C:\Users\bob\calc.bin -o C:\Users\bob\calc.aes.bin -mode encrypt -type aes256 -key Sh3!1z -v
[-]Output directory: C:\Users\bob\
[-]Output file name: calc.aes.bin
[-]File contents (hex): 505152535657556a605a6863616c6354594883ec2865488b32488b7618488b761048ad488b30488b7e3003573c8b5c17288b741f204801fe8b541f240fb72c178d5202ad813c0757696e4575ef8b741f1c4801fe8b34ae4801f799ffd74883c4305d5f5e5b5a5958c3
[-]AES256 encrypting input file
[+]Argon2 salt (hex): db6126d3ac640f8aaa67cda74b8cf1d2c54513db7bf4fbe3422d1b276af1367e
[+]AES256 key (32-bytes) derived from input password Sh3!1z (hex): 096a40f1aef38dd9b5d63284acc19727c4420dd98f21ea052112bef63eb7d94a
[+]AES256 nonce (hex): 13802153c4b2fb6a3e545ff4
[+]Output (hex):
44a974233e37b460dc2181b16846f265e8e3a07959abf9c8760f7d0ac8029575e67571ea5b313bc8b011739db57c690ec156a4b0bba4e4d632c35c1490aeaac24f5ae05e90934adf57798ee3c702a3c27073fe976fbcc6ee5db355da186c1add58913e41a8c5716a0fcfc27371f0cae906e50e680366496a00
[+]aes256 encrypt input and wrote 121 bytes to: C:\Users\bob\calc.aes.bin
```

AES256 requires a 32-byte key. This program uses the Argon2 ID algorithm to take the password provided with the `-key` input paramter to derive a 32-byte key while using a randomly generate salt. You will need the same input password and the salt used with the Argon2 algorithm and the same nonce used with the AES256 algorithm to successfull decrypt the file. Alternatively, the decryption function _could_ be updated to just use the 32-byte Argon2 key instead of the input password and salt.

> **NOTE:** It is up to the operator to decide to just use the generated Argon2 key or to use the password and salt that are used to generate the password.

Example AES256 decrypting the input file:

```
PS C:\Users\bob> .\ShellcodeUtils.exe -i C:\Users\bob\calc.aes.bin -o C:\Users\bob\calc.aes.decrypted.bin -mode decrypt -type aes256 -key Sh3!1z -nonce 13802153c4b2fb6a3e545ff4 -salt db6126d3ac640f8aaa67cda74b8cf1d2c54513db7bf4fbe3422d1b276af1367e -v
[-]Output directory: C:\Users\bob\
[-]Output file name: calc.aes.decrypted.bin
[-]File contents (hex): 44a974233e37b460dc2181b16846f265e8e3a07959abf9c8760f7d0ac8029575e67571ea5b313bc8b011739db57c690ec156a4b0bba4e4d632c35c1490aeaac24f5ae05e90934adf57798ee3c702a3c27073fe976fbcc6ee5db355da186c1add58913e41a8c5716a0fcfc27371f0cae906e50e680366496a00
[-]AES256 decrypting input file
[-]Argon2 salt (hex): db6126d3ac640f8aaa67cda74b8cf1d2c54513db7bf4fbe3422d1b276af1367e
[-]AES256 key (hex): 096a40f1aef38dd9b5d63284acc19727c4420dd98f21ea052112bef63eb7d94a
[-]AES256 nonce (hex): 13802153c4b2fb6a3e545ff4
[+]Output (hex):
505152535657556a605a6863616c6354594883ec2865488b32488b7618488b761048ad488b30488b7e3003573c8b5c17288b741f204801fe8b541f240fb72c178d5202ad813c0757696e4575ef8b741f1c4801fe8b34ae4801f799ffd74883c4305d5f5e5b5a5958c3
[+]aes256 decrypt input and wrote 105 bytes to: C:\Users\bob\calc.aes.decrypted.bin
```

The application can be compiled with the following command on a Windows host from the project's root directory:

`set GOOS=windows GOARCH=amd64;go build -o ShellcodeUtils.exe .\cmd\ShellcodeUtils\main.go`

## About

A repository of Windows Shellcode runners and supporting utilities. The applications load and execute Shellcode using various API calls or techniques.


### Resources

[Readme](https://github.com/Ne0nd0g/go-shellcode#readme-ov-file)

### License

[GPL-3.0 license](https://github.com/Ne0nd0g/go-shellcode#GPL-3.0-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Ne0nd0g/go-shellcode).

[Activity](https://github.com/Ne0nd0g/go-shellcode/activity)

### Stars

[**1.2k**\\
stars](https://github.com/Ne0nd0g/go-shellcode/stargazers)

### Watchers

[**24**\\
watching](https://github.com/Ne0nd0g/go-shellcode/watchers)

### Forks

[**236**\\
forks](https://github.com/Ne0nd0g/go-shellcode/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FNe0nd0g%2Fgo-shellcode&report=Ne0nd0g+%28user%29)

## [Releases](https://github.com/Ne0nd0g/go-shellcode/releases)

No releases published

## [Packages\  0](https://github.com/users/Ne0nd0g/packages?repo_name=go-shellcode)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Ne0nd0g/go-shellcode).

## Languages

- [Go100.0%](https://github.com/Ne0nd0g/go-shellcode/search?l=go)

You can’t perform that action at this time.