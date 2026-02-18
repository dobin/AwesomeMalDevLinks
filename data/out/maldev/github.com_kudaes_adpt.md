# https://github.com/Kudaes/ADPT

[Skip to content](https://github.com/Kudaes/ADPT#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Kudaes/ADPT) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Kudaes/ADPT) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Kudaes/ADPT) to refresh your session.Dismiss alert

{{ message }}

[Kudaes](https://github.com/Kudaes)/ **[ADPT](https://github.com/Kudaes/ADPT)** Public

- [Notifications](https://github.com/login?return_to=%2FKudaes%2FADPT) You must be signed in to change notification settings
- [Fork\\
24](https://github.com/login?return_to=%2FKudaes%2FADPT)
- [Star\\
199](https://github.com/login?return_to=%2FKudaes%2FADPT)


DLL proxying for lazy people


### License

[Apache-2.0 license](https://github.com/Kudaes/ADPT/blob/main/LICENSE)

[199\\
stars](https://github.com/Kudaes/ADPT/stargazers) [24\\
forks](https://github.com/Kudaes/ADPT/forks) [Branches](https://github.com/Kudaes/ADPT/branches) [Tags](https://github.com/Kudaes/ADPT/tags) [Activity](https://github.com/Kudaes/ADPT/activity)

[Star](https://github.com/login?return_to=%2FKudaes%2FADPT)

[Notifications](https://github.com/login?return_to=%2FKudaes%2FADPT) You must be signed in to change notification settings

# Kudaes/ADPT

main

[**1** Branch](https://github.com/Kudaes/ADPT/branches) [**0** Tags](https://github.com/Kudaes/ADPT/tags)

[Go to Branches page](https://github.com/Kudaes/ADPT/branches)[Go to Tags page](https://github.com/Kudaes/ADPT/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Kudaes](https://avatars.githubusercontent.com/u/9372136?v=4&size=40)](https://github.com/Kudaes)[Kudaes](https://github.com/Kudaes/ADPT/commits?author=Kudaes)<br>[Minor fix](https://github.com/Kudaes/ADPT/commit/2c7f81905eb0a7afeca9f5a338a570113785f39d)<br>3 months agoDec 1, 2025<br>[2c7f819](https://github.com/Kudaes/ADPT/commit/2c7f81905eb0a7afeca9f5a338a570113785f39d) · 3 months agoDec 1, 2025<br>## History<br>[24 Commits](https://github.com/Kudaes/ADPT/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Kudaes/ADPT/commits/main/) 24 Commits |
| [ExportTracer](https://github.com/Kudaes/ADPT/tree/main/ExportTracer "ExportTracer") | [ExportTracer](https://github.com/Kudaes/ADPT/tree/main/ExportTracer "ExportTracer") | [Update](https://github.com/Kudaes/ADPT/commit/18f19c8ce0bfb064d675e7f0dd887791c5633ead "Update") | 8 months agoJun 27, 2025 |
| [Generator](https://github.com/Kudaes/ADPT/tree/main/Generator "Generator") | [Generator](https://github.com/Kudaes/ADPT/tree/main/Generator "Generator") | [Minor fix](https://github.com/Kudaes/ADPT/commit/2c7f81905eb0a7afeca9f5a338a570113785f39d "Minor fix") | 3 months agoDec 1, 2025 |
| [Images](https://github.com/Kudaes/ADPT/tree/main/Images "Images") | [Images](https://github.com/Kudaes/ADPT/tree/main/Images "Images") | [Initial commit](https://github.com/Kudaes/ADPT/commit/dbad1f74c0dfbf262f309bc13705aa4d7c04cb8a "Initial commit") | 2 years agoMar 21, 2024 |
| [ProxyDll](https://github.com/Kudaes/ADPT/tree/main/ProxyDll "ProxyDll") | [ProxyDll](https://github.com/Kudaes/ADPT/tree/main/ProxyDll "ProxyDll") | [Proxy Dll generation enhanced](https://github.com/Kudaes/ADPT/commit/98ad4f73303afba3332965a23a74b4a7cc9b17c9 "Proxy Dll generation enhanced") | 3 months agoNov 26, 2025 |
| [.gitignore](https://github.com/Kudaes/ADPT/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/Kudaes/ADPT/blob/main/.gitignore ".gitignore") | [Initial commit](https://github.com/Kudaes/ADPT/commit/dbad1f74c0dfbf262f309bc13705aa4d7c04cb8a "Initial commit") | 2 years agoMar 21, 2024 |
| [LICENSE](https://github.com/Kudaes/ADPT/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/Kudaes/ADPT/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/Kudaes/ADPT/commit/dbad1f74c0dfbf262f309bc13705aa4d7c04cb8a "Initial commit") | 2 years agoMar 21, 2024 |
| [README.md](https://github.com/Kudaes/ADPT/blob/main/README.md "README.md") | [README.md](https://github.com/Kudaes/ADPT/blob/main/README.md "README.md") | [Update README.md](https://github.com/Kudaes/ADPT/commit/afe7245db173c459b7c14d98b1413c5f2e785391 "Update README.md") | 3 months agoNov 26, 2025 |
| View all files |

## Repository files navigation

# Description

[Permalink: Description](https://github.com/Kudaes/ADPT#description)

Another Dll Proxying Tool is exactly what it sounds like, another tool that allows you to automate the exploitation of dll hijack/sideloading opportunities. The goal was to create a simple tool for lazy people like me, meaning that I could abuse these hijack opportunities without having to:

- Open Api Monitor or reverse anything in order to find out which exported functions from the original dll are being called in the first place.
- Use GHidra or any other reversing tool in order to obtain any function's signature (in/out parameters and so on).
- Translate C types and structs to Rust in order to recreate those exported function definitions.
- Run my payload on DllMain.

With just a little bit of assembly code you can avoid all of those annoying steps, making the exploitation of this hijack opportunities pretty fast and simple. Besides that, ADPT comes with a few additional features that I've found useful:

- Proxied exported functions also keep the original ordinals values, meaning that they can be called that way instead of by name.
- You can run your payload in the calling thread instead of spawning a new one, allowing you to hijack the program execution. This is useful in some cases to prevent the process from dying.
- The payload can be run on a separate thread either by using `std::thread` or using a native method (`NtCreateThreadEx`). IDK why would this be useful, but whatever.

The "bad" news are:

- You still need to use Procmon like tools to identify the hijack opportunity.
- Your payload has to be written in Rust :) (or you could write it in any other language, compile it to a dll and use [Dinvoke\_rs](https://github.com/Kudaes/DInvoke_rs) to map it into the process...).
- This tool only supports 64 bits dlls.

# Structure

[Permalink: Structure](https://github.com/Kudaes/ADPT#structure)

This tool contains three different projects:

- `Generator` is the main one and its goal is to programmatically create the dlls needed to automate the exploitation of the hijack opportunities.
- `ExportTracer` is a template project that is used to create a dll that will trace the exported functions called by the vulnerable binary. This allows you to identify in which exported function put your payload code.
- Once we have find out which exported function from the original dll we want to hijack, `ProxyDll` is used as a template project in order to generate the final dll, allowing you to add your payload code on it.

All of these projects must be compiled on `release` mode. Initally, both `ExportTracer` and `ProxyDll` will be empty, so you just need to compile `Generator` in order to start using the tool.
I'm using relative paths within this tool, so keep the three projects in the same directory to prevent failures.

# Usage

[Permalink: Usage](https://github.com/Kudaes/ADPT#usage)

A while ago [I commented on Twitter](https://twitter.com/_Kudaes_/status/1648749432635105280) about what I called a "delayed" dll sideloading opportunity on `gdi32full.dll`. This dll, after some specific actions, will delayed-import the `TextShaping` dll, creating all sort of hijacking opportunities. In order to prove the ADPT usage, I'll show you how to exploit this dll sideload on ProcessHacker (which is one of the countless binaries that suffer from this delayed dll sideloading thing).

First, we need to figure out which TextShaping.dll's (which is by default located at `C:\Windows\System32\textshaping.dll`) exported functions are being called from ProcessHacker. To do so, we use `Generator` to create a tracing dll:

```
C:\Users\User\Desktop\ADPT\Generator\target\release> generator.exe -m trace -p C:\Windows\System32\TextShaping.dll
```

This command will generate the code and files required by the `ExportTracer` project. Once completed, compile `ExportTracer` on `release` mode, which should generate the file `.\ExportTracer\target\x86_64-pc-windows-msvc\release\exporttracer.dll`. Rename this dll to `TextShaping.dll` and plant it on ProcessHacker directory. Then, just fire up ProcessHacker. The tracer dll will log each one of the called exported functions to a log file, which by default will be written to `C:\Windows\Temp\result.log`. You can change the location of this log file at the time of creating the tracer dll by using the flag `-l`.

The log file will contain one line for each called exported function, allowing you to obtain the name of those functions and in which order they are being called. Below you can see an example of this log file:

[![Called functions log file example.](https://github.com/Kudaes/ADPT/raw/main/Images/LogFile.PNG)](https://github.com/Kudaes/ADPT/blob/main/Images/LogFile.PNG)

With that info, you just need to indicate to the `Generator` the exported function that you want to use in order to run your payload. I'm going to use the first function that has been called, `ShapingCreateFontCacheData` (to select a function exclusively exported by ordinal use the name `OrdinalPlaceholder<num>` where `<num>` is the ordinal itself):

```
C:\Users\User\Desktop\ADPT\Generator\target\release> generator.exe -m proxy -p C:\Windows\System32\TextShaping.dll -e ShapingCreateFontCacheData
```

Similarly to the previous command, this one will create the files required by the `ProxyDll` template project. Once the command has been completed, you can add your payload code in `.\ProxyDll\src\lib.rs:payload_execution()`. By default, the payload is just an infinite loop, which allows you to check that the sideloading has been successful by inspecting the process' threads. But before that, remember to compile the `ProxyDll` project on `release` mode, which will generate the file `.\ProxyDll\target\x86_64-pc-windows-msvc\release\proxydll.dll`. Once again, rename that file to `TextShaping.dll` and plant it on the ProcessHacker directory. Run ProcessHacker one more time and check that the new thread running the infinite loop has been spawned.

[![Payload running on a new thread.](https://github.com/Kudaes/ADPT/raw/main/Images/PH.PNG)](https://github.com/Kudaes/ADPT/blob/main/Images/PH.PNG)

As it can be seen, our payload is running on the thread with TID `4032`. The payload will run just once. All the exported functions, including the one used to run the payload, are in the end proxied to the corresponding function of the original `TextShaping` dll, allowing the process to run normally. I mean, as any other dll proxying tool would do. Just check the `Modules` tab in PH to see that both dlls are loaded in the process:

[![Dll proxying going on.](https://github.com/Kudaes/ADPT/raw/main/Images/Proxy.PNG)](https://github.com/Kudaes/ADPT/blob/main/Images/Proxy.PNG)

Finally, some binaries will terminate the process if you dont hijack the main thread. To prevent them from doing so, the current thread can be hijacked by using the flag `-c`. In that case, the hijacked exported function won't spawn a new thread to run the payload, but instead it will be run on the current thread, preventing it from reaching the process termination point.

# Considerations

[Permalink: Considerations](https://github.com/Kudaes/ADPT#considerations)

Some issues may arise when trying to use this tool, but in my experience they are simple to fix or circumvent:

- If at the time of compiling the tracer or proxy dll you are getting `error LNK2005: symbol already defined` error messages from the linker, just uncomment the line 6 of the `.cargo\config` file and try again or pass the flag `-f` to the `Generator`.
- If for any reason you need to statically link the C runtime in your dlls, [check this out](https://github.com/Kudaes/rust_tips_and_tricks?tab=readme-ov-file#vcruntime) or pass the flag `-r` to the `Generator`.

If you find any other issue, report it to me!

## About

DLL proxying for lazy people


### Topics

[rust](https://github.com/topics/rust "Topic: rust") [dll](https://github.com/topics/dll "Topic: dll") [dll-proxying](https://github.com/topics/dll-proxying "Topic: dll-proxying")

### Resources

[Readme](https://github.com/Kudaes/ADPT#readme-ov-file)

### License

[Apache-2.0 license](https://github.com/Kudaes/ADPT#Apache-2.0-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Kudaes/ADPT).

[Activity](https://github.com/Kudaes/ADPT/activity)

### Stars

[**199**\\
stars](https://github.com/Kudaes/ADPT/stargazers)

### Watchers

[**3**\\
watching](https://github.com/Kudaes/ADPT/watchers)

### Forks

[**24**\\
forks](https://github.com/Kudaes/ADPT/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FKudaes%2FADPT&report=Kudaes+%28user%29)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Kudaes/ADPT).

## Languages

- [Rust100.0%](https://github.com/Kudaes/ADPT/search?l=rust)

You can’t perform that action at this time.