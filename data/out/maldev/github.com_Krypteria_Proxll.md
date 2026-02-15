# https://github.com/Krypteria/Proxll

[Skip to content](https://github.com/Krypteria/Proxll#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Krypteria/Proxll) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Krypteria/Proxll) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Krypteria/Proxll) to refresh your session.Dismiss alert

{{ message }}

[Krypteria](https://github.com/Krypteria)/ **[Proxll](https://github.com/Krypteria/Proxll)** Public

- [Notifications](https://github.com/login?return_to=%2FKrypteria%2FProxll) You must be signed in to change notification settings
- [Fork\\
10](https://github.com/login?return_to=%2FKrypteria%2FProxll)
- [Star\\
41](https://github.com/login?return_to=%2FKrypteria%2FProxll)


Proxll is a tool designed to simplify the generation of proxy DLLs while addressing common conflicts related to windows.h


### License

[Apache-2.0 license](https://github.com/Krypteria/Proxll/blob/main/LICENSE)

[41\\
stars](https://github.com/Krypteria/Proxll/stargazers) [10\\
forks](https://github.com/Krypteria/Proxll/forks) [Branches](https://github.com/Krypteria/Proxll/branches) [Tags](https://github.com/Krypteria/Proxll/tags) [Activity](https://github.com/Krypteria/Proxll/activity)

[Star](https://github.com/login?return_to=%2FKrypteria%2FProxll)

[Notifications](https://github.com/login?return_to=%2FKrypteria%2FProxll) You must be signed in to change notification settings

# Krypteria/Proxll

main

[**1** Branch](https://github.com/Krypteria/Proxll/branches) [**0** Tags](https://github.com/Krypteria/Proxll/tags)

[Go to Branches page](https://github.com/Krypteria/Proxll/branches)[Go to Tags page](https://github.com/Krypteria/Proxll/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Krypteria](https://avatars.githubusercontent.com/u/55555187?v=4&size=40)](https://github.com/Krypteria)[Krypteria](https://github.com/Krypteria/Proxll/commits?author=Krypteria)<br>[Update README.md](https://github.com/Krypteria/Proxll/commit/56011eac79afd09221548213e7eec3a9b8f466e8)<br>2 years agoOct 8, 2024<br>[56011ea](https://github.com/Krypteria/Proxll/commit/56011eac79afd09221548213e7eec3a9b8f466e8) · 2 years agoOct 8, 2024<br>## History<br>[5 Commits](https://github.com/Krypteria/Proxll/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Krypteria/Proxll/commits/main/) 5 Commits |
| [img](https://github.com/Krypteria/Proxll/tree/main/img "img") | [img](https://github.com/Krypteria/Proxll/tree/main/img "img") | [readme imgs added](https://github.com/Krypteria/Proxll/commit/15a45b90969810d78427dfd5b3d214c34d1e18af "readme imgs added") | 2 years agoOct 8, 2024 |
| [proxllGen](https://github.com/Krypteria/Proxll/tree/main/proxllGen "proxllGen") | [proxllGen](https://github.com/Krypteria/Proxll/tree/main/proxllGen "proxllGen") | [repo init](https://github.com/Krypteria/Proxll/commit/edee432527fe4f049ab4734cbcd6688292263423 "repo init") | 2 years agoOct 8, 2024 |
| [template](https://github.com/Krypteria/Proxll/tree/main/template "template") | [template](https://github.com/Krypteria/Proxll/tree/main/template "template") | [repo init](https://github.com/Krypteria/Proxll/commit/edee432527fe4f049ab4734cbcd6688292263423 "repo init") | 2 years agoOct 8, 2024 |
| [LICENSE](https://github.com/Krypteria/Proxll/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/Krypteria/Proxll/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/Krypteria/Proxll/commit/5f5e46a7c593ed0feb1f9089d0f1f1c2bd222443 "Initial commit") | 2 years agoOct 8, 2024 |
| [README.md](https://github.com/Krypteria/Proxll/blob/main/README.md "README.md") | [README.md](https://github.com/Krypteria/Proxll/blob/main/README.md "README.md") | [Update README.md](https://github.com/Krypteria/Proxll/commit/56011eac79afd09221548213e7eec3a9b8f466e8 "Update README.md") | 2 years agoOct 8, 2024 |
| View all files |

## Repository files navigation

## What is and how to use Proxll

[Permalink: What is and how to use Proxll](https://github.com/Krypteria/Proxll#what-is-and-how-to-use-proxll)

Releasing a proxy DLL generator in almost 2025 is coming a bit late to the game, I know. But I decided to make my own implementation for fun and learning as well as taking the opportunity to talk about a common problem while designing a proxy DLL application in C++.

I'll go into a bit more detail below about what problem I'm talking about, but for those who want to skip that part, Proxll is used in the following way:

#### 1- Locate the proxy DLL oportunity

[Permalink: 1- Locate the proxy DLL oportunity](https://github.com/Krypteria/Proxll#1--locate-the-proxy-dll-oportunity)

The first step is to identify a situation where DLL proxying is useful. For this, I recommend using both [Process Monitor](https://learn.microsoft.com/es-es/sysinternals/downloads/procmon) and [API Monitor](http://www.rohitab.com/apimonitor).

#### 2- Compile ProxllGen.exe

[Permalink: 2- Compile ProxllGen.exe](https://github.com/Krypteria/Proxll#2--compile-proxllgenexe)

Proxll needs to be compiled using **x86\_64-w64-mingw32-g++** so MinGW for 64-bit installed it's needed. Once installed, Proxll has a makefile to facilitate compilation. Simply run **mingw32-make.exe** in the project folder to build..

```
D:\Proxll\proxllGen> mingw32-make.exe
[*] Compiling proxllGen.exe (x64)
[+] ProxllGen compiled at \proxllGen\bin
```

#### 3- Generate a proxy DLL template using ProxllGen.exe

[Permalink: 3- Generate a proxy DLL template using ProxllGen.exe](https://github.com/Krypteria/Proxll#3--generate-a-proxy-dll-template-using-proxllgenexe)

The next step is to generate a template of the legitimate DLL we want to proxy, to do it, we execute the following command:

```
proxllGen.exe <DLL absolute path> <function name>
```

```
D:\Proxll\proxllGen\bin> proxllGen.exe C:\Windows\System32\version.dll GetFileVersionInfoA
[+] Template generated at \Proxll\template
```

_Note: the path of the DLL must be the same as on the target machine and the function name can be `DllMain`_

The execution of the command will leave the following relevant files in the `\template` folder:

| File | Description |
| --- | --- |
| t\_core.cpp | Contains the functions that have dependencies on the Windows API as well as the function that will run the malicious code |
| /include/t\_core.h | Defines the prototype of the function that executes the malicious code, making it accessible from `t_exported.cpp`. (More details in the TL;DR section.) |
| t\_exported.cpp | Contains the definition of the exported functions from the legitimate DLL |
| exported.def | .def file used to link the functions defined in `t_exported.cpp` to those in the legitimate DLL |

#### 4- Proxy DLL compilation

[Permalink: 4- Proxy DLL compilation](https://github.com/Krypteria/Proxll#4--proxy-dll-compilation)

Once the template has been generated and the code we want to run has been added, the proxy DLL can be compiled using **mingw32-make.exe** in the `\template` folder.

```
D:\Proxll\template> mingw32-make.exe
[*] Compiling proxy DLL (x64)
[+] Proxy DLL generated at \template\bin
```

_Note: Proxll uses debug prints to give feedback during the execution process of the resulting DLL. These prints can be viewed with [DebugView](https://learn.microsoft.com/es-es/sysinternals/downloads/debugview)._

## TL;DR Proxy DLL & Proxll approach

[Permalink: TL;DR Proxy DLL & Proxll approach](https://github.com/Krypteria/Proxll#tldr-proxy-dll--proxll-approach)

In this section, I’ll explain what a proxy DLL is. If you're already familiar with the concept, feel free to skip ahead.

In general terms, a proxy DLL is a DLL whose functions act as an intermediary (or "front end") for functions defined in another DLL. This may sound unusual, but it's something the operating system itself does in various contexts.

An example of legitimate use can be seen in forwarded exported functions. In the following example we can see how the `VerLanguageNameA` and `VerLanguageNameW` functions of `C:\Windows\System32\version.dll` points to the memory address to their equivalents in `KERNEL32.dll`.

[![forwardedExport](https://github.com/Krypteria/Proxll/raw/main/img/forwardedExport.png)](https://github.com/Krypteria/Proxll/blob/main/img/forwardedExport.png)

While this is legitimate, anything poorly implemented can become a problem. As a simple example of this casuistry, let's assume the following case of a program looking for a DLL in two potential locations:

```
HMODULE hLegitDll = LoadLibrary("C:\\Programs\\LegitApp\\dll\\legit.dll");
if(hLegitDll == NULL){
	hLegitDll = LoadLibrary("C:\\Programs\\LegitApp\\legit.dll");
	if(hLegitDll == NULL){
		//Error handling
	}
}
```

If `legit.dll` is in the second location, we find the following in Process Monitor:
[![procmon](https://github.com/Krypteria/Proxll/raw/main/img/procmon.png)](https://github.com/Krypteria/Proxll/blob/main/img/procmon.png)

If a malicious user had write permissions on the first path, he could deploy a DLL named `legit.dll` and execute code via the `legitApp` process. But what would happen to legitApp? Well, it would crash sooner or later due to several factors.

Let's assume that the `legitApp` process makes the following call after the DLL is loaded:

```
pLegitExportedFunc3 exportedFunc = (pLegitExportedFun3)GetProcAddress(hLegitDll, "legitExportedFunc3");
if(exportedFunc == NULL){
	//Error handling
}

size_t c = 0;
exportedFunc(3, 4, &c);
printf("Result: %d\n", c);
```

The most direct approach would be to execute our code in the `DllMain` of the malicious DLL. However, this would not prevent the `LegitApp` process from calling `legitExportedFunc3` and crashing once our code has finished executing. In this type of situation, creating a DLL proxy can solve the problem.

if we want to run our code without causing `LegitApp` to crash, the proxy DLL must do the following:

- Set forwarded exports for all functions except the one we want to use.
- Locate the memory address of the function we are impersonating to execute our code.
- Establish some kind of blocking mechanism to prevent the malicious code from executing multiple times (we don't know how many times the process calls the function).
- Execute the malicious code/payload.
- Execute the actual function from its memory address and return the result of the execution.

Using `Proxll` to automate this process and adding as a payload a code that writes the _poc.txt_ file to the LegitApp path, we get the following:
[![poc_1](https://github.com/Krypteria/Proxll/raw/main/img/poc_1.png)](https://github.com/Krypteria/Proxll/blob/main/img/poc_1.png)

[![](https://github.com/Krypteria/Proxll/raw/main/img/poc_2.png)](https://github.com/Krypteria/Proxll/blob/main/img/poc_2.png)

## Proxll Approach

[Permalink: Proxll Approach](https://github.com/Krypteria/Proxll#proxll-approach)

While developing the tool I encountered a well-known problem in C++. The problems caused by the inclusion of `windows.h`

Specifically, I encountered the following problem:

[![compilationError](https://github.com/Krypteria/Proxll/raw/main/img/compilationError.png)](https://github.com/Krypteria/Proxll/blob/main/img/compilationError.png)

If we try to define a function already defined in `windows.h`, we get a "conflicting declaration of C function" error, which leaves us with the following options:

- Define the function with the parameters defined in `windows.h` to make an overload (unfeasible without much effort).
- Try to eliminate the `windows.h` dependency (unfeasible, without windows.h we are very limited when it comes to interact with the OS).

After trying several options, I came up with the following idea (which is not new): "Maybe I can split the DLL code into two .cpp files, one for the functions that have `windows.h` dependencies and another for defining all the exported functions."

So, that’s what I did. The template generated by `proxllGen.exe` has the following structure:

[![](https://github.com/Krypteria/Proxll/raw/main/img/proxll.png)](https://github.com/Krypteria/Proxll/blob/main/img/proxll.png)

This structure allows us to continue using `windows.h` in `t_core.cpp` while eliminating the redefinition error by separating the exported functions into the `t_exported.cpp` file. Since the exported functions in `t_exported.cpp` must access `windows.h`, this file includes the header `t_core.h`, which provides access to the `proxllCore` function defined in `t_core.cpp`. This setup allows the use of `windows.h` without needing to include it directly in `t_exported.cpp`.

## About

Proxll is a tool designed to simplify the generation of proxy DLLs while addressing common conflicts related to windows.h


### Topics

[dll](https://github.com/topics/dll "Topic: dll") [cpp](https://github.com/topics/cpp "Topic: cpp") [redteam](https://github.com/topics/redteam "Topic: redteam") [dll-proxy](https://github.com/topics/dll-proxy "Topic: dll-proxy")

### Resources

[Readme](https://github.com/Krypteria/Proxll#readme-ov-file)

### License

[Apache-2.0 license](https://github.com/Krypteria/Proxll#Apache-2.0-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Krypteria/Proxll).

[Activity](https://github.com/Krypteria/Proxll/activity)

### Stars

[**41**\\
stars](https://github.com/Krypteria/Proxll/stargazers)

### Watchers

[**2**\\
watching](https://github.com/Krypteria/Proxll/watchers)

### Forks

[**10**\\
forks](https://github.com/Krypteria/Proxll/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FKrypteria%2FProxll&report=Krypteria+%28user%29)

## [Releases](https://github.com/Krypteria/Proxll/releases)

No releases published

## [Packages\  0](https://github.com/users/Krypteria/packages?repo_name=Proxll)

No packages published

## Languages

- [C++95.2%](https://github.com/Krypteria/Proxll/search?l=c%2B%2B)
- [C2.6%](https://github.com/Krypteria/Proxll/search?l=c)
- [Makefile2.2%](https://github.com/Krypteria/Proxll/search?l=makefile)

You can’t perform that action at this time.