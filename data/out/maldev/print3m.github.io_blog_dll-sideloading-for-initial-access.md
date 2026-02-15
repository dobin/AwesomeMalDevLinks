# https://print3m.github.io/blog/dll-sideloading-for-initial-access

[All posts](https://print3m.github.io/)

# DLL Sideloading for Initial Access – Red Team Operator's Guide

Created at: 2025-09-02

Replacing one of the DLL libraries is the easiest way to add your own functionality to a compiled program on Windows. We do not touch the main digitally signed EXE file, but replace one of the libraries loaded by the running process. This is a simple but still very effective method of confusing EDRs.

How can this be used for initial access? We need to find the right trusted software, subtly backdoor one of its DLLs not to disrupt the operation of the program, pack everything into an archive and send it to the victim. It sounds simple, but there are quite a few tricks and caveats that we should take into account during red team exercises.

## DLL Sideloading & DLL Proxying

DLL sideloading involves copying an application's executable file to another folder and substituting your own DLL libraries for those expected by the program. DLL sideloading is possible when the application loads DLL libraries using relative paths rather than absolute paths, i.e., it uses, for example, `LoadLibrary("./utils/math.dll")`. Most applications do this because the user can choose where to install the application on the system, and the application must work everywhere. This is not a particular vulnerability. You could even say it's a feature, as most applications do this intentionally. We will use this feature to substitute our own malicious DLL into a legitimate program, pack it, and send it to the victim. This way, our malware is launched by trusted software.

DLL Proxying is a technique used in DLL Sideloading to substitute your own code without disrupting the normal operation of the program. Everything looks legitimate, and your malicious code has been executed. I will discuss this technique in more detail later in this article.

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/1.png)

## Find the right software to backdoor

Perfect software to backdoor should be:

- Modular - Of course, the program must have some DLLs that we can backdoor. We are talking about custom software DLLs, not the system ones.
- "DLL Sideloadable" - The program must be vulnerable to DLL sideloading when moved to another location.
- Small - Remember, we want to send this to the victim. It can't be 20 gigabytes.
- Popular - It must be something common, something that EDR has seen millions of times across the globe. Think about archivers (7zip, WinRAR), lightweight editors (Notepad++), PDF readers, image viewers.
- Digitally signed - The program must be legit and digitally signed with valid certificate.

Do not use dual-use software! Some people use, for example, the Python interpreter and perform DLL Sideloading on it. It may work, but it makes no more sense than using a "regular" app. The Python interpreter itself can be suspicious, and we do not use anything Python-specific to take additional risks. The best software is the most ordinary, innocent and common one you can find.

> **NOTE**: Not every software has its own DLLs at all. Some programs only use system libraries. Some software has its own DLLs, but they are so obfuscated, with strange calling conventions and name mangling, that it's better not to touch them. Look for something else.

**Testing ideas**

To test whether the application is vulnerable to DLL sideloading suitable for Initial Access, follow these steps:

1. Install the application.
2. Copy the entire folder with installed application to another location.
3. Uninstall the original application (e.g. using control panel).
4. Try to run the copied application.

If everything works correctly, it means **we can start backdooring application's DLL files!**

**If the application crashes or not everything works correctly, then unfortunately we are out of luck.** The application probably needs some values in the Windows registry or configuration files in fixed locations, which it places there during installation. This prevents us from performing DLL Sideloading as an Initial Access vector. In reality, there is no other way than to test manually, because everything depends on the decisions made by the developers who created the application.

**Another problem is what happens when we deliver an application to a user who already has it installed.** Various things can happen here, including our EXE starting to use the original DLLs in the installation location. This means that our backdoor will not be launched or proxied functions will not work. **If there's a chance, test that too with already installed software!**

**Common software**

In the case of normal applications used by millions of people around the world, I suspect that majority of application DLL libraries will be vulnerable to DLL Sideloading. I have already written about this, but I will repeat: this is (mostly) not a bug, it is a feature.

You can find some known abusable applications at [hijacklibs.net](https://hijacklibs.net/). Keep in mind that this is by no means an exhaustive list, and finding vulnerable software manually is not that difficult.

Application categories worth checking out:

- File archivers
- Image / video viewers
- PDF viewers and editors
- Lightweight document viewers (Excel / Word / PowerPoint replacements)
- Password managers
- Lightweight code editors
- Lightweight graphic editors
- File managers
- FTP / SSH / whatever clients
- Note-taking applications
- Lightweight system administration tools

[Here is a good list of free apps](https://www.microsoft.com/en-in/store/top-free/apps/pc) that users most often install from the Windows Store. It's worth checking out.

Consider this list as inspiration for your search. I will show a specific example using Notepad++ later in this article.

**LOLBIN**

In the case of LOLBIN, the situation is slightly different. By LOLBIN, I mean applications built into Windows, usually located in the `%SYSTEM32%` folder. Some LOLBINs do not have their own libraries at all, they only use the default system libraries. In the case of LOLBIN DLLs, sideloading is no longer so certain, as they are usually located in a fixed and documented location, so theoretically they can refer to their libraries using absolute paths, as their location should not be changed.

Despite this, there are still LOLBINs signed by Microsoft that load their libraries using relative paths. You can find them at [hijacklibs.net](https://hijacklibs.net/#vendor:microsoft) by selecting the "sideloading" option in the search bar. People are, of course, constantly discovering new LOLBINs vulnerable to DLL sideloading. How to automate finding new ones is beyond the scope of this article.

## Find the right DLL to backdoor

Our target are custom application DLLs, not default system ones. I write more about why not to use system libraries in the section "OPSEC considerations". But how do you know which one to choose? Which one is really loaded and when – statically or dynamically? Stay with me.

**Lazy Method**

When we look at the folder with the installed application, we see an EXE file and usually several DLL libraries. Often, even from the names of the DLL files, we can tell which ones are used in which situations. For example, we can guess that `7z.dll` will be used by `7z.exe`, etc. There are usually not many DLL libraries in smaller programs. This method is often effective enough, although not very precise.

For example, in the 7Zip program folder, we see only 3 DLL files:

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/2.png)

**Effective Method**

To see all loaded DLL libraries, we can use the [Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon) program from the [Sysinternals](https://learn.microsoft.com/en-us/sysinternals/) package.

> **NOTE**: We can do something similar using Process Explorer, but in my opinion Process Monitor has better filtering and better output to our case.

Process Monitor allows us to filter out all Load Image events for a given process. This way, we can see exactly which DLL libraries are loaded and when exactly this happens. Process Monitor shows both DLLs loaded statically by IAT and dynamically during program execution. Nested DLL files, i.e., those loaded by other DLLs, are also shown, giving us a complete picture of the situation.

Process Monitor does not provide an easy way to distinguish between statically loaded DLLs and dynamically loaded DLLs. But this is not a big problem. First of all, this information is usually not very important. Secondly, if we want to, we can inspect binaries manually using tool like [PE-bear](https://github.com/hasherezade/pe-bear) to figure out what's included in the IAT (static linking).

Below is a list of DLLs loaded by `notepad++.exe`. Most of them are system DLLs, but there are also a few libraries loaded from the program folder. These are our target.

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/3.png)

> **NOTE**: If DLL Sideloading is to be used for Initial Access, after moving the program to another folder, the above "application" DLLs should be successfully found in the new location with no error.

## Backdoor the DLL function

Let's assume that we have decided to install a backdoor in Notepad++. Analysis of the program using Process Monitor showed that the `NppConverter.dll` library is loaded dynamically, which is ideal. Our goal is to write our own library with the same name, which will execute our backdoor code and not interrupt the normal operation of the program. In other words, we want to add our proxy DLL between the program and its original DLL.

For this purpose, we will use my tool: [DllShimmer](https://github.com/Print3M/DllShimmer). You can read about all the parameters on GitHub, but in short DllShimmer parses the original DLL and extracts information about exported functions. Based on this information, DllShimmer creates a boilerplate C++ file (`.cpp`). The generated file allows you to add your own code to each function exported from the original DLL without disrupting the normal operation of the program. No reverse engineering or instrumentation is required, because DllShimmer does not rely on function signatures.

Using DllShimmer is very easy. Provide the original DLL file and it will generate a new project with all the necessary files:

```
./DllShimmer-linux-amd64 -i NppConverter.dll -o project/ -x 'NppConverter2.dll' -m --debug-file 'C:\Users\john\Desktop\npp-dbg.txt'
```

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/4.png)

The code we will be editing is located in the `NppConverter.dll.cpp` file. Here are two example functions that we can backdoor.

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/5.png)

We also have `DllMain` at our disposal, which is executed automatically after loading the DLL into memory.

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/6.png)

So which function should we backdoor? I do not recommend backdooring `DllMain` because [it has a number of limitations](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-best-practices) (e.g., it cannot create new threads), which make it very difficult to use for executing shellcode. I write more about `DllMain` in the “OPSEC considerations" section.

So we want to backdoor some normal exported function used by Notepad++. But which functions are actually used? And when exactly? Fortunately, we don't have to guess. DllShimmer adds a lot of debugging information to the generated `.cpp` file. All we have to do is compile the generated C++ code, substitute our proxy DLL in the right place, and we get a full dump of the executed functions. We can backdoor each of them.

Compilation is very simple; just run the generated `compile.sh` file in the project directory.

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/7.png)

Now we change the name of the original DLL (`NppConverter.dll` -\> `NppConverter2.dll`) according to what we declared when generating the project in DllShimmer. And we put our proxy `NppConverter.dll` in the same place. Done, we can launch Notepad++. Unfortunately, an unexpected error has occurred.

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/8.png)

> **NOTE**: Most programs don't display such a nice error message as Notepad++. Usually, they just crash with no additional information.

To debug what exactly is going on, let's take a look at the `npp-dbg.txt` file created on the desktop. It contains a record of all actions performed on our proxy DLL.

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/9.png)
The proxy DLL has been loaded. The `isUnicode` function has been called. However, the attempt to load the original `NppConverter2.dll` has failed. We can see that the original DLL was searched for in the `C:\Program Files\Notepad++` directory, where it is not located. No wonder the program threw an error. We can quickly fix this by specifying the correct path to the original DLL in the `-x` parameter of DllShimmer.

```
./DllShimmer-linux-amd64 -i NppConverter.dll -o project/ -x '.\plugins\NppConverter\NppConverter2.dll' -m --debug-file 'C:\Users\john\Desktop\npp-dbg.txt'
```

With the new project, we repeat everything again and launch Notepad++.

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/10.png)

Now everything works as it should. Notepad++ launches correctly and is fully functional. In the `npp-dbg.txt` file, we can see exactly which functions from the original `NppConverter.dll` are being executed. We can backdoor any of them.

`getName` function looks good. Now let's go back to the previously generated C++ code and add a piece of code that mimics our backdoor. Remember to add the code inside the `if` condition, which protects us from multiple calls to our backdoor during a single program run.

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/11.png)

Now let's compile the project without debugging information (delete the section marked below from the `compile.sh` file) and put the proxy DLL back in the same place.

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/12.png)

We start Notepad++ as usual...

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/13.png)

It works! Notepad++ launches correctly, and a calculator also pops up, which means our backdoor worked. In a real Initial Access scenario, we should place code there that quickly establishes some kind of persistence or migrates to another process, because Notepad++ can be quickly closed by the user. Our backdoor is a standard C++ function, so all malware development techniques can be used here.

Let's see that the Export Address Table (EAT) of our proxy DLL is exactly the same as the EAT of the original DLL, i.e., they export exactly the same functions. There are no unnecessarily forwarded functions.

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/14.png)

Additionally, the IAT proxy DLL does not contain any suspicious records indicating that it is only a proxy. Everything looks completely normal.

![img](https://print3m.github.io/imgs/dll-sideloading-for-initial-access/15.png)

DllShimmer is not capable of backdooring every DLL in the world. I haven't come across one yet that I haven't been able to backdoor on a modern system, but it's worth reading about [Limitations](https://github.com/Print3M/DllShimmer?tab=readme-ov-file#limitations) of this tool.

## Payload Delivery

Payload delivery is no different from standard malware delivery. There is nothing innovative here. Create a folder with subfolders, add some harmless PDF files here and there, put the entire backdoored program in a nested subfolder. Create a LNK to the backdoored software in the main folder. Pack the entire thing into some container (e.g. `.zip`, `.7z`, `.rar`, `.iso`) and you are good to go!

## OPSEC considerations

In real-world redteam operations, it is worth keeping in mind a few OPSEC issues that I have not mentioned before.

**Backdooring System vs Application DLL**

In my opinion, it is always better to backdoor custom application DLLs. First of all, it is simpler in the case of Initial Access, where the entire program must be sent in a container. We do not have to look for any DLL Hijacking vulnerabilities, we just replace the existing DLL with a proxy. Secondly, it is definitely more stealthy. EDRs do not know application DLLs, they do not know what hashes they have and whether they have been changed. Even if the proxy DLL is not digitally signed, it looks much less suspicious than a well-known modified system library in the application folder.

**Backdooring `DllMain` vs Exported Function**

In my opinion, it is always better to backdoor an exported function and additionally protect the backdoor against multiple executions (DLlShimmer does this using a global mutex). As I mentioned above, `DllMain` has many limitations that hinder malware development. Besides, backdooring an exported function is more stealthy. `DllMain` can be executed without any problems by any sandbox. This is a standard method of testing malicious DLLs. The situation is different in the case of exported functions whose signature is unknown (custom application DLLs!) and it is not known how they should be run.

Of course, the backdoor should still be equipped with anti-sandbox techniques, because it can simply be executed in the sandbox along with the main EXE file. However, backdooring an exported function provides additional protection against arbitrary attempts to run the DLL itself.

**Backdooring LOLBIN vs Signed App vs Unsigned App**

Do not backdoor unsigned applications. The whole idea of using DLL Sideloading in Initial Access is to backdoor trusted, i.e., signed applications.

I can't answer the question about LOLBIN or the standard signed application. However, there are a few things to keep in mind when backdooring LOLBIN:

- It is easy to create a YARA rule that detects the execution of LOLBIN from an unusual location. Microsoft documentation often explicitly specifies the location of the LOLBINs.
- The libraries used by LOLBINs are signed by Microsoft, and their signatures are known to EDRs. Modification of such a library may be suspicious.
- Simply sending LOLBIN to the victim is suspicious. Default Windows programs are simply pre-installed, not downloaded from the internet.
- The list of LOLBINs vulnerable to DLL sideloading is known ( [hijacklibs.net](https://hijacklibs.net/)) and potentially monitored.

LOLBs are definitely the most trusted, after all, they were written by Microsoft itself. But that's why they are the most closely monitored...

**No parameters == best execution**

The most stealthy way to run an application with DLL sideloading is when we don't have to provide any parameters. This means that we can create a completely normal LNK file leading to a completely legitimate signed EXE file, without any parameters. The simpler the LNK, the better.

Of course, this is not always possible. Often, we want to display a decoy after launching our payload. However, it is worth considering a scenario that justifies running the program without a decoy as a “controlled error." For example, in the example described above, an empty Notepad++ will launch. The victim will probably report to us that “something is not working" or that “the file is empty." We will then politely apologize and send them the correct PDF, and in the meantime, our implant will have been launched. Creativity is required.

**Proxy DLL signing**

Here, the same rules apply as for classic malware. You can sign a DLL to lower its detection rate. It is not necessary, but it can sometimes help.

Expired certificate: Certificates sometimes leak, and although they are immediately invalidated by the company, they can still be used to increase the credibility of malware. Statistics of stolen certs: [https://certcentral.org/dashboard](https://certcentral.org/dashboard)

Self-signed certificate: Nothing special but signing the executable file almost always lowers detection rate, so it is always worth doing.

**Proxy DLL metadata**

Keep in mind the metadata produced during compilation of the proxy DLL. These are general rules for all malware development, so I won't go into detail here.

Things to keep in mind:

- linker paths
- compilation paths
- compilation timestamp
- compilation toolchain
- file properties

Ideally, all these values should be identical to those in the original DLL.