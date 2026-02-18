# https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit

This website uses cookies. You may change your settings at any time.

AcceptReject AllManage Cookies

Cookie Preferences

[Home](https://www.cobaltstrike.com/) » [Blog](https://www.cobaltstrike.com/blog/) » Create a proxy DLL with artifact kit

# Create a proxy DLL with artifact kit

Tuesday 02 November, 2021

DLL attacks (hijacking, proxying, etc) are a challenge defenders must face. They can be leveraged in a Red Team engagement to help measure these defenses. Have you used this technique? In this post, I’ll walk through an example of adding a DLL proxy to beacon.dll for use in a DLL Proxy attack.

## What is a DLL Proxying?

To begin with, this is not a new technique. I’ve seen it used some, but not always understood in practice. Other DLL hijacking attacks tend to be used more often, but Red Teams can benefit by adding this technique to their toolbox.

DLL proxying is an attack that falls in the DLL hijacking category.

> Adversaries may execute their own malicious payloads by hijacking the search order used to load DLLs. Windows systems use a common method to look for required DLLs to load into a program.
>
> MITRE ATT&CK defines this as [Hijack Execution Flow: DLL Search Order Hijacking](https://attack.mitre.org/techniques/T1574/001/).

A common way this is abused is to find a process that loads a “ghost” DLL. This is a DLL that is called by the process, but doesn’t actually exist. The calling process ignores this and continues. An attacker can add their own DLL in place of this ghost DLL. This works great, but can be rare.

What if you could modify an existing DLL without breaking the application that depends on that functionality?

This is DLL proxying. It allows an attacker to hijack the execution flow of a process but keep the original functionality of the application. Let’s walk through the attack flow.

![](https://www.cobaltstrike.com/app/uploads/2023/01/proxy.def_.diagram-1024x710-1.png)DLL Proxy Attack Flow Diagram

Let’s say some process uses math.dll to perform calculations. Someprocess.exe loads math.dll and makes calls to its exported functions as needed. This is why we use external libraries.

If we want to hijack this process, we could easily replace math.dll with something malicious, but this would break the application. We don’t want that. This may draw attention to what we are doing. We need to copy math.dll to original.dll. Replace math.dll with a version that will forward the the legitimate calls to the new original.dll. And finally, use math.dll to load whatever malicious function we want.

In order to do this we need…

1. The ability to create and write files
2. The ability to find a target DLL that is loaded by an application
3. The ability to extract the exports from a target DLL
4. The ability to create a DLL that will ‘proxy’ the original exports to a copy of the original DLL

The post is using one technique for DLL proxying to specifically show how to use artifact kit to create this proxy DLL. There are several projects that explore this concept. A quick search can yield a wealth of resources on the topic. One of particular interest is the [DueDLLigence](https://github.com/mandiant/DueDLLigence) project. It is an interesting approach that uses a framework to easily allow the development malicious DLLs.

## Let’s Start with a Simple DLL Proxy Example

Let’s walk through a simple example to help clear this up.

This example uses code that can be found [here](https://github.com/Cobalt-Strike/ProxyDLLExample).

In this example we assume that the **hello.dll** is the DLL being call by our target process. It will become the target of our proxy attack. This is similar to math.dll in the diagram.

### Steps to find, build, and use a proxy DLL

#### 1) Understand the execution flow of a process to understand which DLLs are loaded.

We need to start by understanding which DLLs are loaded by a process. The [sysinternals](https://docs.microsoft.com/en-us/sysinternals/) tool **process explorer** works great here.

## Real World Tip

I won’t call out any vendor here. My examples simply use rundll32.exe as my ‘application’. Just consider rundll32.exe some real target (maybe a chat application) that uses hello.dll.

The AppData directory is a great place to find candidates for user level persistence. Unlike C:\\Program Files, c:\\users\\USER\\AppData is user controlled. Many applications are installed here. cough, cough, chat clients.

A quick tip on using process explorer is to filter out what you need before running. In this case, I only want to see Load Image from my target process.

![](https://www.cobaltstrike.com/app/uploads/2023/01/procmon_filter.png)Procmon Filter

To simulate an application starting up and making calls to its DLLs, I use:

[view source](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#printSource "print") [?](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#about "?")

|     |     |
| --- | --- |
| `1` | `rundll32.exe hello.dll, hello` |

to have rundll32 call the hello function.

![](https://www.cobaltstrike.com/app/uploads/2023/01/Hello_world.png)rundll32 loads hello.dll and calls the hello function

In the process explorer output, we see that our application loads hello.dll

![](https://www.cobaltstrike.com/app/uploads/2023/01/procmon_hello.dll_.png)Procmon

Great, we found a candidate DLL in our target application.

Another option to search for targets is to use the [DLL\_Imports\_BOF](https://github.com/EspressoCake/DLL_Imports_BOF). This project allows you to search for target applications during an engagement.

> This is a `BOF` to enumerate `DLL` files to-be-loaded by a given `PE` file. Depending on the number of arguments, this will allow an operator to either view a listing of anticipated imported `DLL` files, or to view the imported functions for an anticipated `DLL`.

No matter what you use, the goal is to understand what DLLs are in play and what exports those DLLs use.

### 2) Identify the DLL exports.

DLL exports are the functions that an external process can call to use that functionality. It is a core feature of a DLL.

Look at the exports of hello.dll:

If you are following along, compile hello.dll:

[view source](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#printSource "print") [?](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#about "?")

|     |     |
| --- | --- |
| `1` | `x86_64-w64-mingw32-gcc -m64 -c -Os hello.c -Wall -shared -masm=intel` |

|     |     |
| --- | --- |
| `2` | `x86_64-w64-mingw32-dllwrap -m64 --def hello.def hello.o -o hello.dll` |

There are several ways to get the exported function from a DLL.

I included a simple python script, **get\_exports.py**, to extract the exports and format for use in a .def file.

[view source](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#printSource "print") [?](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#about "?")

|     |     |
| --- | --- |
| `1` | `python3 get_exports.py --target hello.dll` |

![](https://www.cobaltstrike.com/app/uploads/2023/01/get_exports.png)get\_exports.py output

You can also use something like `dumpbin` from Visual Studio

[view source](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#printSource "print") [?](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#about "?")

|     |     |
| --- | --- |
| `1` | `dumpbin /exports hello.dll` |

![](https://www.cobaltstrike.com/app/uploads/2023/01/dumpbin_hello.dll_.png)dumpbin output

The point of this is to get a list of the legitimate exported functions from the target DLL. This will give us what we need to build our proxy.

### 3) Build the proxy.dll.

In this example, I’m writing a proxy in .C to be compiled with MinGW. This shows the process, but could be very different depending on how you build your DLL. No matter what you do, you will be generating a DLL that forward functions.

Add the exported functions to proxy.def:

![](https://www.cobaltstrike.com/app/uploads/2023/01/proxy_def.png)proxy.def updated with the hello.dll functions

> A module-definition or DEF file (\*.def) is a text file containing one or more module statements that describe various attributes of a DLL. If you are not using the **`__declspec(dllexport)`** keyword to export the DLL’s functions, the DLL requires a DEF file.
>
> https://docs.microsoft.com/en-us/cpp/build/exporting-from-a-dll-using-def-files?view=msvc-160

Let’s break down the export **hello=original.hello @1**:

![](https://www.cobaltstrike.com/app/uploads/2023/01/proxy.def_.diagram-1024x301-1.png)

This is creating the “hello” export for proxy.dll. Calls made to this function are forwarded to the hello function in original.dll. The @1 is the ordinal. (Ordinals are another way a function may be called. It does not always need to match, but can help if ordinals are used.)

#### **proxy.c**

proxy.c is a very basic DLL. It will run the payload function and if a remote target calls a remote function, it will proxy based on the exports set in proxy.def. The payload function is blocking. This is just a simple example. You should create a thread or use some other non-blocking method.

We are ready to compile proxy.dll

[view source](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#printSource "print") [?](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#about "?")

|     |     |
| --- | --- |
| `1` | `x86_64-w64-mingw32-gcc -m64 -c -Os  proxy.c -Wall -shared -masm=intel` |

|     |     |
| --- | --- |
| `2` | `x86_64-w64-mingw32-dllwrap -m64 --def proxy.def proxy.o -o proxy.dll` |

### 4) Move the files to the target.

To simulate a real attack you must:

- rename the original dll (hello.dll) to original.dll or what you set in the proxy.def file.
- rename proxy.dll to the original file name (hello.dll)

Output after moving and naming the files on the target system.

[view source](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#printSource "print") [?](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#about "?")

|     |     |
| --- | --- |
| `1` | `Directory of Y:\temp\proxydll` |

|     |     |
| --- | --- |
| `2` |  |

|     |     |
| --- | --- |
| `3` | `10/28/2021  01:53 PM    &lt;DIR>          .` |

|     |     |
| --- | --- |
| `4` | `10/28/2021  01:37 PM    &lt;DIR>          ..` |

|     |     |
| --- | --- |
| `5` | `10/28/2021  01:37 PM           280,185 hello.dll    &lt;- This was proxy.dll` |

|     |     |
| --- | --- |
| `6` | `10/28/2021  01:23 PM           280,167 original.dll &lt;- This was hello.dll` |

### 5) Test the proxy.

Let’s simulate some process following its normal process of loading hello.dll and calling the hello function by using rundll32.exe.

The following command acts more or less the same as an application starting, loading a DLL, and calling a function from that DLL.

[view source](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#printSource "print") [?](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#about "?")

|     |     |
| --- | --- |
| `1` | `rundll32 hello.dll, hello` |

![](https://www.cobaltstrike.com/app/uploads/2023/01/hello_from_proxy.png)The payload function from the proxy DLL

![](https://www.cobaltstrike.com/app/uploads/2023/01/Hello_world-1.png)The hello function from the original DLL

We called the proxy DLL (hello.dll) using rundll32 as an example target for a DLL loading attack. It executed our payload function and the original function.

That’s it. There really isn’t much to this attack, but it can be very effective. A proxy DLL is just a DLL that proxies legitimate calls and runs your own payload. Proxy attacks allow an attacker to hijack execution flow but keep the original functionality of the application.

## Let’s extend this to the Cobalt Strike Artifact Kit

Licensed users of Cobalt Strike have access to the [artifact kit](https://www.cobaltstrike.com/help-artifact-kit). This kit provide a way to modify several aspects of the .exe or .dll beacon payloads. Think of this as a beacon ‘loader’. The kit can be loaded by Cobalt Strike as an aggressor script to update how .exe or .dll payloads are built.

Now that we know the primitives from our example, we can easily update kit with the changes needed to convert beacon.dll into a proxy.

Modify the file **src-main/dllmain.de** f by adding **hello=original.hello @1** as an export option. This is the same as what was done in the example.

Build the kit using the build.sh script. By default, this will compile all kit techniques. Let it build them all. We will pick one to load.

Load the artifact kit aggressor script to tell Cobalt Strike to use the newly create template when building a payload. In this case we will use the ‘pipe’ technique. The aggressor script can be found in dist-pipe/artifact.cna after the build is complete.

Cobalt Strike -> Script Manager

Load -> dist-pipe/artifact.cna

Generate a Beacon DLL payload

Attacks -> Packages -> Windows Executable (S)

```
Listener: Choose Your listener
Output:   Windows DLL
x64:      X
```

![](https://www.cobaltstrike.com/app/uploads/2023/01/Screen-Shot-2021-10-29-at-12.17.40-PM.png)

Click Generate and save as hello.dll.

Remember, this is the proxy DLL. It will replace the target DLL and the the target DLL will be renamed to original.dll.

![](https://www.cobaltstrike.com/app/uploads/2023/01/artifact_output.png)Modified version of artifact.cna to output messages to the script console when the artifact kit is used

Let’s take a look at this beacon DLL payload (hello.dll):

[view source](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#printSource "print") [?](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#about "?")

|     |     |
| --- | --- |
| `1` | `dumpbin /exports hello.dll` |

![](https://www.cobaltstrike.com/app/uploads/2023/01/dumpbin_proxy.png)exports of hello.dll (proxy)

We see the DLL has the default exports for beacon.dll and the new forwarding export.

Let’s test as we did before by using rundll32 as the target process that we want to attack.

[view source](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#printSource "print") [?](https://www.cobaltstrike.com/blog/create-a-proxy-dll-with-artifact-kit#about "?")

|     |     |
| --- | --- |
| `1` | `rundll32 hello.dll, hello` |

![](https://www.cobaltstrike.com/app/uploads/2023/01/new_beacon.png)Received a new beacon

hello.dll runs the beacon payload, and the hello function call was successfully proxied.

![](https://www.cobaltstrike.com/app/uploads/2023/01/Hello_world-2.png)

At this point, we turned beacon.dll in a proxy.

## What Next?

This example only shows how to make beacon a DLL proxy. The artifact kit is a way to customize beacon.exe or beacon.dll. It can be used to help bypass AV/EDR. Consider exploring the possibilities of using the kit. Or, forget the artifact kit altogether and write your own beacon loader as a proxy DLL.

Using rundll32 isn’t exciting, but the attack technique itself is a great method for persistence. Many applications are installed in

c:\\users\\USER\\AppData

This directory is writable by the user (vs something like c:\\program files). This means an attacker with control over a target can find a target process and create a proxy DLL for that target. Take a look at the application installed in AppData, you may find a nice target.

## Defensive Considerations

A great preventative control for this attack is for applications to validate the DLLs it loads. If a rouge/untrusted DLL is used, the application will not allow it to execute. During the writing of this post, I tested by targeting a popular chat application. It used digital signatures to validate the loaded DLLs. This worked great, except the user was presented with a popup asking if they would like to run the “untrusted” code. Clicking OK allowed my payload to run (partial win?). Prevention is great, be we need to ensure we can detect attacks when it fails.

Do not allow user controlled applications to be installed in user controlled directories. Install applications in directories the user can use but not modify (i.e., C:\\Program Files).

File integrity monitoring may help.

Fortunately, the payloads executed from this attack the same. The proxy DLL is just a loader. The payloads executed by this loader may be detected through the normal means of a robust security operations program.

## References

- Example code [https://github.com/Cobalt-Strike/ProxyDLLExample](https://github.com/Cobalt-Strike/ProxyDLLExample)
- MITRE ATT&CK [Hijack Execution Flow: DLL Search Order Hijacking](https://attack.mitre.org/techniques/T1574/001/)
- DueDLLigence [https://github.com/mandiant/DueDLLigence](https://github.com/mandiant/DueDLLigence)
- DLL Imports BOF [DLL\_Imports\_BOF](https://github.com/EspressoCake/DLL_Imports_BOF)
- A great post on DLL Hijacking [https://www.netspi.com/blog/technical/adversary-simulation/adaptive-dll-hijacking/](https://www.netspi.com/blog/technical/adversary-simulation/adaptive-dll-hijacking/)

![](https://www.cobaltstrike.com/app/uploads/2023/07/joe-vest-circle-outline.png)

#### [Joe Vest](https://www.cobaltstrike.com/profile/joe-vest)

[View Profile](https://www.cobaltstrike.com/profile/joe-vest)

TOPICS


- [Red Team](https://www.cobaltstrike.com/blog?_sft_cornerstone=red-team "Red Team")