# https://research.checkpoint.com/2024/net-hooking-harmonizing-managed-territory/

## CATEGORIES

- [Android Malware23](https://research.checkpoint.com/category/android-malware/)
- [Artificial Intelligence4](https://research.checkpoint.com/category/artificial-intelligence-2/)
- [ChatGPT3](https://research.checkpoint.com/category/chatgpt/)
- [Check Point Research Publications443](https://research.checkpoint.com/category/threat-research/)
- [Cloud Security1](https://research.checkpoint.com/category/cloud-security/)
- [CPRadio44](https://research.checkpoint.com/category/cpradio/)
- [Crypto2](https://research.checkpoint.com/category/crypto/)
- [Data & Threat Intelligence1](https://research.checkpoint.com/category/data-threat-intelligence/)
- [Data Analysis0](https://research.checkpoint.com/category/data-analysis/)
- [Demos22](https://research.checkpoint.com/category/demos/)
- [Global Cyber Attack Reports395](https://research.checkpoint.com/category/threat-intelligence-reports/)
- [How To Guides13](https://research.checkpoint.com/category/how-to-guides/)
- [Ransomware3](https://research.checkpoint.com/category/ransomware/)
- [Russo-Ukrainian War1](https://research.checkpoint.com/category/russo-ukrainian-war/)
- [Security Report1](https://research.checkpoint.com/category/security-report/)
- [Threat and data analysis0](https://research.checkpoint.com/category/threat-and-data-analysis/)
- [Threat Research173](https://research.checkpoint.com/category/threat-research-2/)
- [Web 3.0 Security11](https://research.checkpoint.com/category/web3/)
- [Wipers0](https://research.checkpoint.com/category/wipers/)

![](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId20.png)

# .NET Hooking – Harmonizing Managed Territory


January 8, 2024

[Share on LinkedIn!](https://www.linkedin.com/shareArticle?mini=true&url=https://research.checkpoint.com/2024/net-hooking-harmonizing-managed-territory/%20-%20%20https://research.checkpoint.com/?p=29314;source=LinkedIn "Share on LinkedIn!") [Share on Facebook!](http://www.facebook.com/sharer.php?u=https://research.checkpoint.com/2024/net-hooking-harmonizing-managed-territory/%20-%20https://research.checkpoint.com/?p=29314 "Share on Facebook!") [Tweet this!](http://twitter.com/home/?status=.NET%20Hooking%20%E2%80%93%20Harmonizing%20Managed%20Territory%20-%20https://research.checkpoint.com/?p=29314%20via%20@kenmata "Tweet this!")

https://research.checkpoint.com/2024/net-hooking-harmonizing-managed-territory/

**Research by:** Jiri Vinopal

## Key Points

- _**Check Point Research (CPR) provides an introduction to .NET managed hooking using the Harmony library.**_
- _**We cover the most common examples of implementation using different types of Harmony patches.**_
- _**The practical example using Harmony hooking to defeat the notorious “ConfuserEx2” obfuscator results in the “ConfuserEx2\_String\_Decryptor” tool.**_
- _**CPR reveals a neat trick how to combine both debugging and hooking using the Harmony library (Harmony hooking from the dnSpyEx debugging context).**_

## Introduction

For a malware researcher, analyst, or reverse engineer, the ability to alter the functionality of certain parts of code is a crucial step, often necessary to reach a meaningful result during the analysis process. This kind of code instrumentation is usually reached by debugging, DBI (Dynamic Binary Instrumentation), or a simple hooking framework.

Managing the code execution of the desired process has always worked well for non-managed, native code. We have many useful tools and frameworks that are proven to be very effective.

The situation is a little bit different when we start to talk about altering the functionality of managed code, more specifically, applications that run on top of .NET. The ability to instrument the code on the managed layer is limited by the small number of tools that can safely do so. One that stands head and shoulders above the rest is the **[Harmony](https://github.com/pardeike/Harmony),** an open-source library for patching, replacing, and decorating .NET methods **during runtime**.

In some cases, it is possible to use other specific libraries and frameworks to modify the code of .NET Assemblies with direct patching or a complete rebuild of those files on disk, but such a solution is not always feasible. It becomes even less so as the logic of the original code becomes more fragile and sophisticated.

This is an especially sore point when dealing with malware samples that are protected and obfuscated in a way that touching them on the disk could easily destroy the original structure, causing undesirable behavior changes or a complete loss of functionality. Especially in these cases, modifying the code logic in memory **during runtime** is the convenient solution.

In this article, we introduce the concept of .NET managed hooking using the **Harmony** library, its internals, and common examples of implementation using different types of Harmony patches. We show how useful Harmony hooking can be in a practical exercise of defeating the notorious obfuscator “ **ConfuserEx2**” that resulted in the release of the “ **ConfuserEx2\_String\_Decryptor**” tool. The last section reveals a neat trick how to combine debugging and hooking using the Harmony library, or in other words, using Harmony hooking from the dnSpyEx debugging context.

## Introduction to .NET Managed Hooking Using Harmony

In one of our previous publications, we introduced a way to hook the native layer of .NET to alter the functionality of certain WIN API functions. See [dotRunpeX](https://research.checkpoint.com/2023/dotrunpex-demystifying-new-virtualized-net-injector-used-in-the-wild/) ( **Invoke-DotRunpeXextract** – preinjection of a native hooking library).

Generally, the managed hooking of .NET works a little bit differently than the hooking of its native layer, as we are targeting the higher level of the code representation ( **Intermediate Language**) that resides on the managed layer. This results in a similar instrumentation but with significantly better control over all executed instructions.

Most .NET-managed hooking tools work like simple patching libraries, allowing the original method to be replaced. This is the reason why we decided to go with the [Harmony2 library](https://harmony.pardeike.net/index.html), which goes one step further and gives us the ability to:

1. Keep the original method intact.
2. Execute code before and/or after the original method.
3. Modify the original IL code of the method with IL code processors.
4. Multiple co-existing hooks/patches that don´t conflict with each other.

The Harmony2 is a hooking library written in C# for patching, replacing, and decorating .NET methods during runtime. It uses a variation of hooking and focuses only on in-memory changes that don’t affect files on disk. It supports **Mono** and **.NET** environments on Windows, Unix, and macOS, targeting all programming languages that compile to [CIL](https://wikipedia.org/wiki/Common_Intermediate_Language) (also known as **Intermediate Language**, **IL code**, **MSIL**).

One of the main advantages of the Harmony library is that it operates only on in-memory code, so it does not touch the files on disk in any way. This comes in very handy, especially in cases where we are dealing with dotnet malware protected by some obfuscator in a way that the deobfuscation via .NET Assembly rebuilding is time-consuming and needs to be done very carefully so as not to destroy the original structure, which can lead to a complete loss of functionality.

The other advantage is that we are not limited to only hook .NET methods defined in the scope of one specific .NET Assembly, but we can alter the functionality of all referenced assemblies, especially those that come with and build the .NET Runtime.

**Bootstrapping and Injection**

It is important to note that the Harmony library does not provide the functionality to run our own code within an application that is not designed to execute foreign code. We need a way to inject at least the few lines that start the Harmony patching. This is usually done with a loader/injector (e.g., the GUI-based tool [ExtremeDumper](https://github.com/wwh1004/ExtremeDumper#inject-net-assemblies) can be used to inject the Harmony library into the .NET process) but can also be easily reached by using [Reflection](https://learn.microsoft.com/en-us/dotnet/framework/reflection-and-codedom/reflection).

### Types of Patches

For .NET method hooking, the Harmony library provides several types of patches: **Prefix**, **Postfix**, **Transpiler**, **Finalizer**, and **Reverse Patch**. Each of them serves a different purpose and gives different capabilities. The Prefix, Postfix, Transpiler, and Reverse Patch are the main subjects of this article, but we briefly explain all types below.

**Prefix**

A Prefix is a method that is executed **before** the original method. It is commonly used to:

- Access and edit the arguments of the original method.
- Skip the original method.
- Set the result of the original method – skipping the original is necessary.
- Set a custom state that can be recalled in the Postfix.
- Run a piece of code at the beginning that is guaranteed to be executed.

**Postfix**

A Postfix is a method that is executed **after** the original method. It is commonly used to:

- Read or change the result of the original method.
- Access the arguments of the original method.
- Read a custom state from the Prefix.

**Transpiler**

This method defines the Transpiler that **modifies** the code of the original method. It is supposed to be used in advanced cases where we need to modify the IL Code of the original method body. Transpilers are called in an earlier stage where the instructions of the original method are fed into them for processing, changing them to a final output of the instruction set that builds the new “ _**original**_” method. Transpilers are commonly used to:

- Modify the original method in detail (on the level of its IL Code).
- Change the whole logic of the original method.
- Change certain IL instructions.

**Finalizer**

A Finalizer is a method that **handles exceptions** and can change them. It is executed after all Postfixes. It wraps the original, all Prefixes, and Postfixes in a try/catch logic and is either called with `null` (no exception) or with an exception if one occurred. It is commonly used to:

- Run a piece of code at the end that is guaranteed to be executed.
- Handle exceptions and suppress them.
- Handle exceptions and alter them.

**Reverse Patch**

A Reverse Patch method is different from the previous types in that it **patches our own** methods instead of foreign original ones. It is a stub method in our code that “ _**becomes**_” the original or part of the original (via **Reverse Patch Transpiler**) method so we can use it or call it independently. The defined stub method needs to look like the original in some way (the same method signature). A Reverse Patch is commonly used to:

- Provide the **unmodified** original method (not affected by any applied patches) that can be called from our code, patches, or even from the patches that are applied to the method from which the Reverse Patch is created.
- Provide a **snapshot** of the method that is constructed from the original method and all the applied Transpilers.
- Provide a part of the original method by using the Reverse Patch Transpiler.
- Easily call private methods.

The simplified hooking logic summary of the Harmony library is shown below:

![](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId31-2-1024x580.png)Figure 1: Harmony library – Hooking logic (Source: “https://harmony.pardeike.net/articles/intro.html”).

## Common Examples of Implementation

In this section, we go through simple examples of implementation, focusing on the four most commonly used types of patches: **Prefix**, **Postfix**, **Transpiler**, and **Reverse Patch**. These patches are used for typical scenarios like reading and changing the arguments of the method, changing the result (return value), modifying the IL code of the original method, and as a way to call the unmodified version of the original method.

There are two common ways of creating and organizing patches using the Harmony library. One of them is using [annotation](https://harmony.pardeike.net/articles/annotations.html) – Patch Class – that simplifies patching by assuming that we set up annotated classes and define patch methods inside them. This is usually used to better organize patches and perform more types of patches on a single original method (combination of Prefix, Postfix, etc.).

The second one – [Manual Patching](https://harmony.pardeike.net/articles/basics.html#manual-patching) – gives us more control to put patches wherever we like as we refer to them ourselves, but we must rely greatly on the direct use of the reflection. For simplicity, in the common examples of implementation below, only **Manual Patching** is used.

Before we jump to hooking with the Harmony library, we need to create our sample application that will be a target for hooking and used in all the examples of common implementation. For that purpose, we can build a simple C#, Console App using .NET Framework (Release – x86) as shown below:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

namespace Example

{

internal class Program

{

public static int Sum(int a, int b)

{

return a + b;

}

static voidMain()

{

Console.WriteLine("Hook Me If You Can!!!");

int result = Sum(333, 333);

Console.WriteLine($"Result of the Sum: {result}");

}

}

}

namespace Example
{
internal class Program
{
public static int Sum(int a, int b)
{
return a + b;
}

static void Main()
{
Console.WriteLine("Hook Me If You Can!!!");

int result = Sum(333, 333);
Console.WriteLine($"Result of the Sum: {result}");
}
}
}

```
namespace Example
{
    internal class Program
    {
        public static int Sum(int a, int b)
        {
            return a + b;
        }

        static void Main()
        {
            Console.WriteLine("Hook Me If You Can!!!");

            int result = Sum(333, 333);
            Console.WriteLine($"Result of the Sum: {result}");
        }
    }
}
```

Checking the compiled binary and its execution in [dnSpyEx](https://github.com/dnSpyEx/dnSpy):

![Figure 2: The sample compiled application that will be used as a target for hooking - dnSpyEx execution.](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId39.png)Figure 2: The sample compiled application that will be used as a target for hooking – dnSpyEx execution.

As we noted previously, the Harmony library does not provide the functionality to run our own code within an application that is not designed to execute foreign code. Therefore, we need to create a loader/injector that will execute the hooking logic inside of the sample targeted application. The simplest and most straightforward solution is for us to use [Reflection](https://learn.microsoft.com/en-us/dotnet/framework/reflection-and-codedom/reflection).

By using reflection, we can simply create a loader – another C#, Console App using .NET Framework (Release – x86) – that directly loads the target application (using reflection) and implements the hooking logic with the use of Harmony library. Such a loader is used in all examples below where it is mainly the hooking logic that changes.

### Prefix – Changing the Method´s Arguments and Executing

One of the most common practical cases is just a simple hook that modifies the original arguments and continues the execution of the original method. For this purpose, we need to use the Prefix type of patch. The original method that is going to be hooked by a Prefix type of patch is not a method implemented by our targeted application itself but is a referenced method that resides inside of `System.Console.dll` Assembly with a signature: `void WriteLine(System.String)`.

**Step-by-Step Guide:**

1. Implement Harmony patch for Prefix “Manual Patching” `PreFix_WriteLine` – To change the argument value, it needs to be passed by reference, so adding the `ref` keyword is necessary. The return `bool` value of the Prefix patch method `PreFix_WriteLine` signals if the execution of the original method should be skipped (`false` – skip, `true` – do not skip).
2. Load the targeted application using reflection.
3. Install the Prefix patch for method `void Console.WriteLine(System.String)`.
4. Execute the `EntryPoint` of the targeted application (method `Example.Program.Main()`).

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

using System;

using System.Reflection;

using HarmonyLib;

namespace CaptainHook

{

internal class Hook

{

static voidMain()

{

// Loading the targeted application using reflection

Assembly assembly = Assembly.LoadFile(@"C:\\Example.exe");

// Installing the Prefix patch for method "void Console.WriteLine(System.String)"

MethodInfo target = typeof(Console).GetMethod("WriteLine", new\[\]{typeof(string)});

if(target == null)

throw newException("Could not resolve Console.WriteLine");

Harmony harmony = newHarmony("WriteLine");

MethodInfo patch = typeof(Hook).GetMethod("PreFix\_WriteLine");

harmony.Patch(target, newHarmonyMethod(patch));

// Executing the targeted application

assembly.EntryPoint.Invoke(null, null);

}

// Implementation of Harmony patch used for Prefix "Manual Patching"

public static bool PreFix\_WriteLine(ref string value)

{

if(value.Contains("Hook")){ value = "Captain Hook Was Here!!!"; }

returntrue; // Do not skip executing original Console.WriteLine()

}

}

}

using System;
using System.Reflection;
using HarmonyLib;

namespace CaptainHook
{
internal class Hook
{
static void Main()
{
// Loading the targeted application using reflection
Assembly assembly = Assembly.LoadFile(@"C:\\Example.exe");

// Installing the Prefix patch for method "void Console.WriteLine(System.String)"
MethodInfo target = typeof(Console).GetMethod("WriteLine", new\[\] { typeof(string) });
if (target == null)
throw new Exception("Could not resolve Console.WriteLine");

Harmony harmony = new Harmony("WriteLine");
MethodInfo patch = typeof(Hook).GetMethod("PreFix\_WriteLine");
harmony.Patch(target, new HarmonyMethod(patch));

// Executing the targeted application
assembly.EntryPoint.Invoke(null, null);
}

// Implementation of Harmony patch used for Prefix "Manual Patching"
public static bool PreFix\_WriteLine(ref string value)
{
if (value.Contains("Hook")) { value = "Captain Hook Was Here!!!"; }
return true; // Do not skip executing original Console.WriteLine()
}
}
}

```
using System;
using System.Reflection;
using HarmonyLib;

namespace CaptainHook
{
    internal class Hook
    {
        static void Main()
        {
            // Loading the targeted application using reflection
            Assembly assembly = Assembly.LoadFile(@"C:\Example.exe");

            // Installing the Prefix patch for method "void Console.WriteLine(System.String)"
            MethodInfo target = typeof(Console).GetMethod("WriteLine", new[] { typeof(string) });
            if (target == null)
                throw new Exception("Could not resolve Console.WriteLine");

            Harmony harmony = new Harmony("WriteLine");
            MethodInfo patch = typeof(Hook).GetMethod("PreFix_WriteLine");
            harmony.Patch(target, new HarmonyMethod(patch));

            // Executing the targeted application
            assembly.EntryPoint.Invoke(null, null);
        }

        // Implementation of Harmony patch used for Prefix "Manual Patching"
        public static bool PreFix_WriteLine(ref string value)
        {
            if (value.Contains("Hook")) { value = "Captain Hook Was Here!!!"; }
            return true; // Do not skip executing original Console.WriteLine()
        }
    }
}
```

As we can see below, the method `void Console.WriteLine(System.String)` was successfully hooked, and all its invocations were intercepted by the implemented Prefix patch `PreFix_WriteLine`. It only changed when the original argument contained the string value “ **Hook**” (e.g., “ **Hook Me If You Can!!!**” → “ **Captain Hook Was Here!!!**”).

![Figure 3: Prefix hook - Changing the arguments of the “Console.WriteLine()” method.](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId42.png)Figure 3: Prefix hook – Changing the arguments of the “Console.WriteLine()” method.

### Prefix – Changing the Result and Skipping the Original

It can sometimes be useful to completely skip the original method and simply set the result (the return value) for all its invocations. To skip the execution of the original method, we need to choose the Prefix type of patch as it is the one that is going to be executed before the original and can easily skip the original´s execution. The original method `Sum()` that is going to be hooked by a Prefix type of patch is now a method implemented by our targeted application itself with a signature: `System.Int32 Example.Program.Sum(System.Int32, System.Int32)`.

![Figure 4: The dnSpyEx view of the compiled original method “Sum()” - the target for hooking.](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId46.png)Figure 4: The dnSpyEx view of the compiled original method “Sum()” – the target for hooking.

Currently, this case is slightly different in the sense that we are hooking an original method that is part of the targeted application´s type – **runtime type**. The steps will change a little as well.

**Step-by-Step Guide:**

1. Implement Harmony patch for Prefix “Manual Patching” `PreFix_Sum` – To change the return value, the argument called `__result` (the type must match the return type of the original or be assignable from it) must be added to the original method´s parameters and passed by reference. Therefore, it is necessary to add the `ref` keyword to it. The return `bool` value (`false`) of the Prefix patch method `PreFix_Sum` signals that the execution of the original method should be skipped (`false` – skip, `true` – do not skip).
2. Load the targeted application using reflection.
3. Install the Prefix patch for method `System.Int32 Example.Program.Sum(System.Int32, System.Int32)` – As the targeted method is a part of the runtime type (loaded Assembly), we can´t use the `typeof()` operator or the `nameof()` expression, but we can use the Harmony [AccessTools](https://harmony.pardeike.net/articles/utilities.html#accesstools) as a shortcut for reflection to quickly locate it.
4. Execute the `EntryPoint` of the targeted application (method `Example.Program.Main()`).

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

using System;

using System.Reflection;

using HarmonyLib;

namespace CaptainHook

{

internal class Hook

{

static voidMain()

{

// Loading the targeted application using reflection

Assembly assembly = Assembly.LoadFile(@"C:\\Example.exe");

// Installing the Prefix patch for method "int Example.Program.Sum(int, int)"

// The targeted method resides in a runtime type - loaded Assembly

// We can use the Harmony AccessTools as a shortcut for reflection

MethodInfo target = AccessTools.Method("Example.Program:Sum");

if(target == null)

throw newException("Could not resolve Example.Program.Sum");

Harmony harmony = newHarmony("Sum");

MethodInfo patch = typeof(Hook).GetMethod("PreFix\_Sum");

harmony.Patch(target, newHarmonyMethod(patch));

// Executing the targeted application

assembly.EntryPoint.Invoke(null, null);

}

// Implementation of Harmony patch used for Prefix "Manual Patching"

public static bool PreFix\_Sum(ref int \_\_result, int a, int b)

{

\_\_result = a + b + 666000; // Setting the result - return value

returnfalse; // Skip executing the original Example.Program.Sum()

}

}

}

using System;
using System.Reflection;
using HarmonyLib;

namespace CaptainHook
{
internal class Hook
{
static void Main()
{
// Loading the targeted application using reflection
Assembly assembly = Assembly.LoadFile(@"C:\\Example.exe");

// Installing the Prefix patch for method "int Example.Program.Sum(int, int)"
// The targeted method resides in a runtime type - loaded Assembly
// We can use the Harmony AccessTools as a shortcut for reflection
MethodInfo target = AccessTools.Method("Example.Program:Sum");
if (target == null)
throw new Exception("Could not resolve Example.Program.Sum");

Harmony harmony = new Harmony("Sum");
MethodInfo patch = typeof(Hook).GetMethod("PreFix\_Sum");
harmony.Patch(target, new HarmonyMethod(patch));

// Executing the targeted application
assembly.EntryPoint.Invoke(null, null);
}

// Implementation of Harmony patch used for Prefix "Manual Patching"
public static bool PreFix\_Sum(ref int \_\_result, int a, int b)
{
\_\_result = a + b + 666000; // Setting the result - return value
return false; // Skip executing the original Example.Program.Sum()
}
}
}

```
using System;
using System.Reflection;
using HarmonyLib;

namespace CaptainHook
{
    internal class Hook
    {
        static void Main()
        {
            // Loading the targeted application using reflection
            Assembly assembly = Assembly.LoadFile(@"C:\Example.exe");

            // Installing the Prefix patch for method "int Example.Program.Sum(int, int)"
            // The targeted method resides in a runtime type - loaded Assembly
            // We can use the Harmony AccessTools as a shortcut for reflection
            MethodInfo target = AccessTools.Method("Example.Program:Sum");
            if (target == null)
                throw new Exception("Could not resolve Example.Program.Sum");

            Harmony harmony = new Harmony("Sum");
            MethodInfo patch = typeof(Hook).GetMethod("PreFix_Sum");
            harmony.Patch(target, new HarmonyMethod(patch));

            // Executing the targeted application
            assembly.EntryPoint.Invoke(null, null);
        }

        // Implementation of Harmony patch used for Prefix "Manual Patching"
        public static bool PreFix_Sum(ref int __result, int a, int b)
        {
            __result = a + b + 666000; // Setting the result - return value
            return false; // Skip executing the original Example.Program.Sum()
        }
    }
}
```

The method `System.Int32 Example.Program.Sum(System.Int32, System.Int32)` was successfully hooked, and its invocation was intercepted by the implemented Prefix patch `PreFix_Sum`. The execution of the original method was skipped, and the result (return value) was altered in a way that worked with the original arguments but modified the result as we wished (e.g., from “ **Sum(333, 333) → 666**” to “ **Sum(333, 333) → 666 + 666000 → 666666**”).

![Figure 5: Prefix hook - Changing the result of the “Example.Program.Sum()” and skipping its execution.](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId50.png)Figure 5: Prefix hook – Changing the result of the “Example.Program.Sum()” and skipping its execution.

### Postfix – Changing the Result of the Original

Another case is when we want to let the original method execute and instrument the execution with logic that depends on its result (return value). To do so, we use the Postfix type of patch, as that one is executed right after the original. Based on the returned result, we can implement different logic that either sets a new result or leaves it as is. The original method `Sum()` that is going to be hooked by a Postfix type of patch is a method implemented by our targeted application itself with a signature: `System.Int32 Example.Program.Sum(System.Int32, System.Int32)`.

**Step-by-Step Guide:**

1. Implement Harmony patch for Postfix “Manual Patching” `PostFix_Sum` – To change the return value, the argument called `__result` (the type must match the return type of the original or be assignable from it) must be added to the original method´s parameters and passed by reference. Therefore, adding the `ref` keyword to it is necessary.
2. Load the targeted application using reflection.
3. Install the Postfix patch for method `System.Int32 Example.Program.Sum(System.Int32, System.Int32)` – As the targeted method is a part of the runtime type (loaded Assembly), we can´t use the `typeof()` operator or the `nameof()` expression, but we can use the Harmony [AccessTools](https://harmony.pardeike.net/articles/utilities.html#accesstools) as a shortcut for reflection to quickly locate it.
4. Execute the `EntryPoint` of the targeted application (method `Example.Program.Main()`).

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

using System;

using System.Reflection;

using HarmonyLib;

namespace CaptainHook

{

internal class Hook

{

static voidMain()

{

// Loading the targeted application using reflection

Assembly assembly = Assembly.LoadFile(@"C:\\Example.exe");

// Installing the Postfix patch for method "int Example.Program.Sum(int, int)"

// The targeted method resides in a runtime type - loaded Assembly

// We can use the Harmony AccessTools as a shortcut for reflection

MethodInfo target = AccessTools.Method("Example.Program:Sum");

if(target == null)

throw newException("Could not resolve Example.Program.Sum");

Harmony harmony = newHarmony("Sum");

MethodInfo patch = typeof(Hook).GetMethod("PostFix\_Sum");

harmony.Patch(target, postfix: newHarmonyMethod(patch));

// Executing the targeted application

assembly.EntryPoint.Invoke(null, null);

}

// Implementation of Harmony patch used for Postfix "Manual Patching"

public static voidPostFix\_Sum(ref int \_\_result, int a, int b)

{// Checking the result of the original Example.Program.Sum()

if(\_\_result == 666)

{

\_\_result = a + b + 666000; // Setting the result - return value

}

}

}

}

using System;
using System.Reflection;
using HarmonyLib;

namespace CaptainHook
{
internal class Hook
{
static void Main()
{
// Loading the targeted application using reflection
Assembly assembly = Assembly.LoadFile(@"C:\\Example.exe");

// Installing the Postfix patch for method "int Example.Program.Sum(int, int)"
// The targeted method resides in a runtime type - loaded Assembly
// We can use the Harmony AccessTools as a shortcut for reflection
MethodInfo target = AccessTools.Method("Example.Program:Sum");
if (target == null)
throw new Exception("Could not resolve Example.Program.Sum");

Harmony harmony = new Harmony("Sum");
MethodInfo patch = typeof(Hook).GetMethod("PostFix\_Sum");
harmony.Patch(target, postfix: new HarmonyMethod(patch));

// Executing the targeted application
assembly.EntryPoint.Invoke(null, null);
}

// Implementation of Harmony patch used for Postfix "Manual Patching"
public static void PostFix\_Sum(ref int \_\_result, int a, int b)
{ // Checking the result of the original Example.Program.Sum()
if (\_\_result == 666)
{
\_\_result = a + b + 666000; // Setting the result - return value
}
}
}
}

```
using System;
using System.Reflection;
using HarmonyLib;

namespace CaptainHook
{
    internal class Hook
    {
        static void Main()
        {
            // Loading the targeted application using reflection
            Assembly assembly = Assembly.LoadFile(@"C:\Example.exe");

            // Installing the Postfix patch for method "int Example.Program.Sum(int, int)"
            // The targeted method resides in a runtime type - loaded Assembly
            // We can use the Harmony AccessTools as a shortcut for reflection
            MethodInfo target = AccessTools.Method("Example.Program:Sum");
            if (target == null)
                throw new Exception("Could not resolve Example.Program.Sum");

            Harmony harmony = new Harmony("Sum");
            MethodInfo patch = typeof(Hook).GetMethod("PostFix_Sum");
            harmony.Patch(target, postfix: new HarmonyMethod(patch));

            // Executing the targeted application
            assembly.EntryPoint.Invoke(null, null);
        }

        // Implementation of Harmony patch used for Postfix "Manual Patching"
        public static void PostFix_Sum(ref int __result, int a, int b)
        {   // Checking the result of the original Example.Program.Sum()
            if (__result == 666)
            {
                __result = a + b + 666000; // Setting the result - return value
            }
        }
    }
}
```

As we can see below, the method `System.Int32 Example.Program.Sum(System.Int32, System.Int32)` was successfully hooked, and its invocation was intercepted by the implemented Postfix patch `PostFix_Sum`. The original method was executed, and the result (return value) was altered only when it was equal to “ **666**” (e.g., “ **666**” **→** “ **666 + 666000**” **→** “ **666666**”).

![Figure 6: Postfix hook - Changing the specific result of the “Example.Program.Sum()”.](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId54.png)Figure 6: Postfix hook – Changing the specific result of the “Example.Program.Sum()”.

### Transpiler – Changing the IL Code of the Original

For the more advanced cases where we can´t reach certain instrumentation via patch types like Prefix or Postfix, and we want to work on the IL code level of the targeted method, the Transpiler type of patch comes into play.

We can think about the Transpiler as a post-compiler stage that can alter the “source code” of the original method, except that at runtime, it’s the IL code that changes. We can use the Transpiler to simply patch a few instructions or completely change the logic of the targeted method – all during runtime.

The IL code of the original method `Example.Program.Sum()` that is going to be altered by a Transpiler type of patch is a method implemented by our targeted application itself with an original IL code as follows:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

/\\* 0x00000251 02 \*/ IL\_0000: ldarg.0

/\\* 0x00000252 03 \*/ IL\_0001: ldarg.1

/\\* 0x00000253 58 \*/ IL\_0002: add

/\\* 0x00000254 2A \*/ IL\_0003: ret

/\\* 0x00000251 02 \*/ IL\_0000: ldarg.0
/\\* 0x00000252 03 \*/ IL\_0001: ldarg.1
/\\* 0x00000253 58 \*/ IL\_0002: add
/\\* 0x00000254 2A \*/ IL\_0003: ret

```
/* 0x00000251 02 */  IL_0000: ldarg.0
/* 0x00000252 03 */  IL_0001: ldarg.1
/* 0x00000253 58 */  IL_0002: add
/* 0x00000254 2A */  IL_0003: ret
```

As we want to slightly change the logic of this method, the IL code altered by our Transpiler patch should change in memory into:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

/\\* 0x00000000 02 \*/ IL\_0000: ldarg.0

/\\* 0x00000001 03 \*/ IL\_0001: ldarg.1

/\\* 0x00000002 59 \*/ IL\_0002: sub

/\\* 0x00000003 17 \*/ IL\_0003: ldc.i4.1

/\\* 0x00000004 58 \*/ IL\_0004: add

/\\* 0x00000005 2A \*/ IL\_0005: ret

/\\* 0x00000000 02 \*/ IL\_0000: ldarg.0
/\\* 0x00000001 03 \*/ IL\_0001: ldarg.1
/\\* 0x00000002 59 \*/ IL\_0002: sub
/\\* 0x00000003 17 \*/ IL\_0003: ldc.i4.1
/\\* 0x00000004 58 \*/ IL\_0004: add
/\\* 0x00000005 2A \*/ IL\_0005: ret

```
/* 0x00000000 02 */  IL_0000: ldarg.0
/* 0x00000001 03 */  IL_0001: ldarg.1
/* 0x00000002 59 */  IL_0002: sub
/* 0x00000003 17 */  IL_0003: ldc.i4.1
/* 0x00000004 58 */  IL_0004: add
/* 0x00000005 2A */  IL_0005: ret
```

**Step-by-Step Guide:**

1. Implement Harmony patch for Transpiler “Manual Patching” `Transpiler_Sum` – To define our stub method as Transpiler, both the return and argument types must be of type `IEnumerable<CodeInstruction>`.
2. Load the targeted application using reflection.
3. Install the Transpiler patch for the method `System.Int32 Example.Program.Sum(System.Int32, System.Int32)` – As the targeted method is a part of the runtime type (loaded Assembly), we can´t use the `typeof()` operator or the `nameof()` expression, but we can use the Harmony [AccessTools](https://harmony.pardeike.net/articles/utilities.html#accesstools) as a shortcut for reflection to quickly locate it.
4. Execute the `EntryPoint` of the targeted application (method `Example.Program.Main()`).

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

using System;

using System.Collections.Generic;

using System.Linq;

using System.Reflection;

using System.Reflection.Emit;

using HarmonyLib;

namespace CaptainHook

{

internal class Hook

{

static voidMain()

{

// Loading the targeted application using reflection

Assembly assembly = Assembly.LoadFile(@"C:\\Example.exe");

// Installing the Transpiler patch for method "int Example.Program.Sum(int, int)"

// The targeted method resides in a runtime type - loaded Assembly

// We can use the Harmony AccessTools as a shortcut for reflection

MethodInfo target = AccessTools.Method("Example.Program:Sum");

if(target == null)

throw newException("Could not resolve Example.Program.Sum");

Harmony harmony = newHarmony("Sum");

MethodInfo patch = typeof(Hook).GetMethod("Transpiler\_Sum");

harmony.Patch(target, transpiler: newHarmonyMethod(patch));

// Executing the targeted application

assembly.EntryPoint.Invoke(null, null);

}

// Implementation of Harmony patch used for Transpiler "Manual Patching"

public static IEnumerable<CodeInstruction>Transpiler\_Sum(IEnumerable<CodeInstruction> codes)

{// Changing the IL code of the original Example.Program.Sum()

// (a + b) will turn into (a - b + 1)

var instructions = new List<CodeInstruction>(codes);

for(var i = 0; i < instructions.Count; i++)

{

if(instructions\[i\].opcode == OpCodes.Add)

{

instructions.Insert(i, newCodeInstruction(OpCodes.Sub));

instructions.Insert(i + 1, newCodeInstruction(OpCodes.Ldc\_I4\_1));

break;

}

}

return instructions.AsEnumerable();

}

}

}

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;

namespace CaptainHook
{
internal class Hook
{
static void Main()
{
// Loading the targeted application using reflection
Assembly assembly = Assembly.LoadFile(@"C:\\Example.exe");

// Installing the Transpiler patch for method "int Example.Program.Sum(int, int)"
// The targeted method resides in a runtime type - loaded Assembly
// We can use the Harmony AccessTools as a shortcut for reflection
MethodInfo target = AccessTools.Method("Example.Program:Sum");
if (target == null)
throw new Exception("Could not resolve Example.Program.Sum");

Harmony harmony = new Harmony("Sum");
MethodInfo patch = typeof(Hook).GetMethod("Transpiler\_Sum");
harmony.Patch(target, transpiler: new HarmonyMethod(patch));

// Executing the targeted application
assembly.EntryPoint.Invoke(null, null);
}

// Implementation of Harmony patch used for Transpiler "Manual Patching"
public static IEnumerable<CodeInstruction> Transpiler\_Sum(IEnumerable<CodeInstruction> codes)
{ // Changing the IL code of the original Example.Program.Sum()
// (a + b) will turn into (a - b + 1)
var instructions = new List<CodeInstruction>(codes);
for (var i = 0; i < instructions.Count; i++)
{
if (instructions\[i\].opcode == OpCodes.Add)
{
instructions.Insert(i, new CodeInstruction(OpCodes.Sub));
instructions.Insert(i + 1, new CodeInstruction(OpCodes.Ldc\_I4\_1));
break;
}
}
return instructions.AsEnumerable();
}
}
}

```
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;

namespace CaptainHook
{
    internal class Hook
    {
        static void Main()
        {
            // Loading the targeted application using reflection
            Assembly assembly = Assembly.LoadFile(@"C:\Example.exe");

            // Installing the Transpiler patch for method "int Example.Program.Sum(int, int)"
            // The targeted method resides in a runtime type - loaded Assembly
            // We can use the Harmony AccessTools as a shortcut for reflection
            MethodInfo target = AccessTools.Method("Example.Program:Sum");
            if (target == null)
                throw new Exception("Could not resolve Example.Program.Sum");

            Harmony harmony = new Harmony("Sum");
            MethodInfo patch = typeof(Hook).GetMethod("Transpiler_Sum");
            harmony.Patch(target, transpiler: new HarmonyMethod(patch));

            // Executing the targeted application
            assembly.EntryPoint.Invoke(null, null);
        }

        // Implementation of Harmony patch used for Transpiler "Manual Patching"
        public static IEnumerable<CodeInstruction> Transpiler_Sum(IEnumerable<CodeInstruction> codes)
        {   // Changing the IL code of the original Example.Program.Sum()
            // (a + b) will turn into (a - b + 1)
            var instructions = new List<CodeInstruction>(codes);
            for (var i = 0; i < instructions.Count; i++)
            {
                if (instructions[i].opcode == OpCodes.Add)
                {
                    instructions.Insert(i, new CodeInstruction(OpCodes.Sub));
                    instructions.Insert(i + 1, new CodeInstruction(OpCodes.Ldc_I4_1));
                    break;
                }
            }
            return instructions.AsEnumerable();
        }
    }
}
```

We can see that the IL code of the original `System.Int32 Example.Program.Sum(System.Int32, System.Int32)` was successfully altered by the implemented Transpiler patch `Transpiler_Sum` and changed its logic from **(a + b)** to **(a – b + 1)**: “ **Sum(333, 333) → (333 – 333 + 1) → 1**”.

![Figure 7: Transpiler patch - Changing the IL code of the “Example.Program.Sum()”.](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId58.png)Figure 7: Transpiler patch – Changing the IL code of the “Example.Program.Sum()”.

### Reverse Patch and Unpatching – Calling the Original

As we already covered the most common types of patches ( **Prefix**, **Postfix**, **Transpiler**) and we know that all of them modify the original targeted method in some way, a few important questions come to mind:

1. How to remove patches applied to the targeted method so it can become the original again?
2. How to call the intact original method that is not affected by any implanted patches?

Answering the first question is quite easy, as one of the most useful features of the Harmony library is the ability to keep the original method content that is not affected by any applied patches. This original method content can be used for the reconstruction to remove all applied patches or, in other words, “ **unpatching**”.

Once a method is patched, the original method is destroyed, and all future versions will come from **Harmony** (using the original IL code). Therefore, the “ **unpatching**” is not a real unpatching but instead a patching with zero patches. It can completely remove all patches, or patches that are related to certain Harmony instances, or only a specific single patch. The different implementations of unpatching are trivial and can be demonstrated in the code below:

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

// Loading the targeted application using reflection

Assembly assembly = Assembly.LoadFile(@"C:\\Example.exe");

// Installing the Prefix patch for method "void Console.WriteLine(System.String)"

MethodInfo target = typeof(Console).GetMethod("WriteLine", new\[\]{typeof(string)});

if(target == null)

throw newException("Could not resolve Console.WriteLine");

Harmony harmony = newHarmony("WriteLine");

MethodInfo patch = typeof(Hook).GetMethod("PreFix\_WriteLine");

harmony.Patch(target, newHarmonyMethod(patch));

// Executing the targeted application - Console.WriteLine() is PATCHED

assembly.EntryPoint.Invoke(null, null);

\-\-\--------------------------------------------------------------------------

// Unpatching completely all applied patches

harmony.UnpatchAll();

// Unpatching all applied patches of one specific Hramony instance

harmony.UnpatchAll("WriteLine");

// Unpatching specific method from all applied Prefix patches

harmony.Unpatch(target, HarmonyPatchType.Prefix);

// Removing specific patch from specific method

harmony.Unpatch(target, patch);

\-\-\--------------------------------------------------------------------------

// Executing the targeted application - Console.WriteLine() is UNPATCHED

assembly.EntryPoint.Invoke(null, null);

// Implementation of Harmony patch used for Prefix "Manual Patching"

public static bool PreFix\_WriteLine(ref string value)

{

value = "Captain Hook Was Here!!!";

returntrue; // Do not skip executing original Console.WriteLine()

}

// Loading the targeted application using reflection
Assembly assembly = Assembly.LoadFile(@"C:\\Example.exe");
// Installing the Prefix patch for method "void Console.WriteLine(System.String)"
MethodInfo target = typeof(Console).GetMethod("WriteLine", new\[\] { typeof(string) });
if (target == null)
throw new Exception("Could not resolve Console.WriteLine");

Harmony harmony = new Harmony("WriteLine");
MethodInfo patch = typeof(Hook).GetMethod("PreFix\_WriteLine");
harmony.Patch(target, new HarmonyMethod(patch));
// Executing the targeted application - Console.WriteLine() is PATCHED
assembly.EntryPoint.Invoke(null, null);
\-\-\--------------------------------------------------------------------------
// Unpatching completely all applied patches
harmony.UnpatchAll();
// Unpatching all applied patches of one specific Hramony instance
harmony.UnpatchAll("WriteLine");
// Unpatching specific method from all applied Prefix patches
harmony.Unpatch(target, HarmonyPatchType.Prefix);
// Removing specific patch from specific method
harmony.Unpatch(target, patch);
\-\-\--------------------------------------------------------------------------
// Executing the targeted application - Console.WriteLine() is UNPATCHED
assembly.EntryPoint.Invoke(null, null);

// Implementation of Harmony patch used for Prefix "Manual Patching"
public static bool PreFix\_WriteLine(ref string value)
{
value = "Captain Hook Was Here!!!";
return true; // Do not skip executing original Console.WriteLine()
}

```
// Loading the targeted application using reflection
Assembly assembly = Assembly.LoadFile(@"C:\Example.exe");
// Installing the Prefix patch for method "void Console.WriteLine(System.String)"
MethodInfo target = typeof(Console).GetMethod("WriteLine", new[] { typeof(string) });
if (target == null)
    throw new Exception("Could not resolve Console.WriteLine");

Harmony harmony = new Harmony("WriteLine");
MethodInfo patch = typeof(Hook).GetMethod("PreFix_WriteLine");
harmony.Patch(target, new HarmonyMethod(patch));
// Executing the targeted application - Console.WriteLine() is PATCHED
assembly.EntryPoint.Invoke(null, null);
----------------------------------------------------------------------------
// Unpatching completely all applied patches
harmony.UnpatchAll();
// Unpatching all applied patches of one specific Hramony instance
harmony.UnpatchAll("WriteLine");
// Unpatching specific method from all applied Prefix patches
harmony.Unpatch(target, HarmonyPatchType.Prefix);
// Removing specific patch from specific method
harmony.Unpatch(target, patch);
----------------------------------------------------------------------------
// Executing the targeted application - Console.WriteLine() is UNPATCHED
assembly.EntryPoint.Invoke(null, null);

// Implementation of Harmony patch used for Prefix "Manual Patching"
public static bool PreFix_WriteLine(ref string value)
{
    value = "Captain Hook Was Here!!!";
    return true; // Do not skip executing original Console.WriteLine()
}
```

Noteworthy is that we can even process the unpatching from inside the patch itself. In that case, the first call to the targeted hooked method is intercepted by the patch executing all applied logic, but all subsequent calls are processed by the original.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

// Implementation of Harmony patch used for Prefix "Manual Patching"

public static bool PreFix\_WriteLine(ref string value)

{

// Unpatching completely all applied patches even this one

(newHarmony("ItDoesNotMatter")).UnpatchAll();

value = "Captain Hook Was Here!!!";

returntrue; // Do not skip executing original Console.WriteLine()

}

// Implementation of Harmony patch used for Prefix "Manual Patching"
public static bool PreFix\_WriteLine(ref string value)
{
// Unpatching completely all applied patches even this one
(new Harmony("ItDoesNotMatter")).UnpatchAll();
value = "Captain Hook Was Here!!!";
return true; // Do not skip executing original Console.WriteLine()
}

```
// Implementation of Harmony patch used for Prefix "Manual Patching"
public static bool PreFix_WriteLine(ref string value)
{
    // Unpatching completely all applied patches even this one
    (new Harmony("ItDoesNotMatter")).UnpatchAll();
    value = "Captain Hook Was Here!!!";
    return true; // Do not skip executing original Console.WriteLine()
}
```

The “ **unpatching**” is usually the best way to go if we want to either completely remove the applied patches for any reason or just remove a single patch instance. There is another much more convenient solution when it comes to using the original form of the method. If we need something like a copy of the original method, untouched by any kind of patches, that can be used and independently called from any location, even from its patch itself, and still not have to touch the applied patches in any way, a specific type of patch called “ **Reverse Patch**” is the right solution.

The **Reverse Patch** is a way to create a copy of the original method that we can later use and call ourselves. We can call it from our code, or patches, or even from the patches that are applied to the method from which the Reverse Patch is created. This kind of patch is different than the previous types in that it patches our own methods instead of foreign original ones. It is a stub method in our own code that “ _**becomes**_” the original method.

To be honest, we don’t have another way to go. What could possibly go wrong if we take the example from the section “ **Prefix – Changing the Method´s Arguments and Executing**” that applied a Prefix patch to the method `void WriteLine(System.String)` that resides in `System.Console.dll` Assembly and try to print some “string” to the console from the patch itself?

![Figure 8: Calling the patched method from the patch itself - StackOverflowException.](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId62.png)Figure 8: Calling the patched method from the patch itself – StackOverflowException.

If we take the same example but implement the Reverse Patch for the original method `void Console.WriteLine(System.String)`, we should be able to use it without any limitation causing similar exceptions.

**Step-by-Step Guide:**

1. Implement Harmony patch for Prefix “Manual Patching” `PreFix_WriteLine` – To change the argument value, it needs to be passed by reference, so adding the `ref` keyword is necessary. The return `bool` value of the Prefix patch method `PreFix_WriteLine` signals if the execution of the original method should be skipped (`false` – skip, `true` – do not skip).
2. Implement Harmony patch for Reverse Patch “Manual Patching” `MyWriteLine` – An empty stub method that needs to match the method signature of the original `void Console.WriteLine(System.String)`.
3. Load the targeted application using reflection.
4. Install the Prefix patch for the method `void Console.WriteLine(System.String)`.
5. Install the Reverse Patch for the method `void Console.WriteLine(System.String)`.
6. Execute the `EntryPoint` of the targeted application (method `Example.Program.Main()`).

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

using System;

using System.Reflection;

using HarmonyLib;

namespace CaptainHook

{

internal class Hook

{

static voidMain()

{

// Loading the targeted application using reflection

Assembly assembly = Assembly.LoadFile(@"C:\\Example.exe");

// Installing the Prefix patch for method "void Console.WriteLine(System.String)"

MethodInfo target = typeof(Console).GetMethod("WriteLine", new\[\]{typeof(string)});

if(target == null)

throw newException("Could not resolve Console.WriteLine");

Harmony harmony = newHarmony("WriteLine");

MethodInfo patch = typeof(Hook).GetMethod("PreFix\_WriteLine");

harmony.Patch(target, newHarmonyMethod(patch));

// Installing the Reverse Patch for method "void Console.WriteLine(System.String)"

MethodInfo rPatch = typeof(Hook).GetMethod("MyWriteLine");

var rPatcher = harmony.CreateReversePatcher(target, newHarmonyMethod(rPatch));

rPatcher.Patch();

// Executing the targeted application

assembly.EntryPoint.Invoke(null, null);

// Calling the Reverse Patch for Console.WriteLine()

MyWriteLine("Reverse Patch for Console.WriteLine() from Main!!!");

}

// Implementation of Harmony patch used for Reverse Patch "Manual Patching"

public static voidMyWriteLine(string value){}

// Implementation of Harmony patch used for Prefix "Manual Patching"

public static bool PreFix\_WriteLine(ref string value)

{

// Calling the Reverse Patch for Console.WriteLine() from PreFix\_WriteLine

MyWriteLine("Reverse Patch for Console.WriteLine() from PreFix\_WriteLine!!!");

if(value.Contains("Hook")){ value = "Captain Hook Was Here!!!"; }

returntrue; // Do not skip executing original Console.WriteLine()

}

}

}

using System;
using System.Reflection;
using HarmonyLib;

namespace CaptainHook
{
internal class Hook
{
static void Main()
{
// Loading the targeted application using reflection
Assembly assembly = Assembly.LoadFile(@"C:\\Example.exe");

// Installing the Prefix patch for method "void Console.WriteLine(System.String)"
MethodInfo target = typeof(Console).GetMethod("WriteLine", new\[\] { typeof(string) });
if (target == null)
throw new Exception("Could not resolve Console.WriteLine");

Harmony harmony = new Harmony("WriteLine");
MethodInfo patch = typeof(Hook).GetMethod("PreFix\_WriteLine");
harmony.Patch(target, new HarmonyMethod(patch));

// Installing the Reverse Patch for method "void Console.WriteLine(System.String)"
MethodInfo rPatch = typeof(Hook).GetMethod("MyWriteLine");
var rPatcher = harmony.CreateReversePatcher(target, new HarmonyMethod(rPatch));
rPatcher.Patch();

// Executing the targeted application
assembly.EntryPoint.Invoke(null, null);

// Calling the Reverse Patch for Console.WriteLine()
MyWriteLine("Reverse Patch for Console.WriteLine() from Main!!!");
}

// Implementation of Harmony patch used for Reverse Patch "Manual Patching"
public static void MyWriteLine(string value) { }

// Implementation of Harmony patch used for Prefix "Manual Patching"
public static bool PreFix\_WriteLine(ref string value)
{
// Calling the Reverse Patch for Console.WriteLine() from PreFix\_WriteLine
MyWriteLine("Reverse Patch for Console.WriteLine() from PreFix\_WriteLine!!!");

if (value.Contains("Hook")) { value = "Captain Hook Was Here!!!"; }
return true; // Do not skip executing original Console.WriteLine()
}
}
}

```
using System;
using System.Reflection;
using HarmonyLib;

namespace CaptainHook
{
    internal class Hook
    {
        static void Main()
        {
            // Loading the targeted application using reflection
            Assembly assembly = Assembly.LoadFile(@"C:\Example.exe");

            // Installing the Prefix patch for method "void Console.WriteLine(System.String)"
            MethodInfo target = typeof(Console).GetMethod("WriteLine", new[] { typeof(string) });
            if (target == null)
                throw new Exception("Could not resolve Console.WriteLine");

            Harmony harmony = new Harmony("WriteLine");
            MethodInfo patch = typeof(Hook).GetMethod("PreFix_WriteLine");
            harmony.Patch(target, new HarmonyMethod(patch));

            // Installing the Reverse Patch for method "void Console.WriteLine(System.String)"
            MethodInfo rPatch = typeof(Hook).GetMethod("MyWriteLine");
            var rPatcher = harmony.CreateReversePatcher(target, new HarmonyMethod(rPatch));
            rPatcher.Patch();

            // Executing the targeted application
            assembly.EntryPoint.Invoke(null, null);

            // Calling the Reverse Patch for Console.WriteLine()
            MyWriteLine("Reverse Patch for Console.WriteLine() from Main!!!");
        }

        // Implementation of Harmony patch used for Reverse Patch "Manual Patching"
        public static void MyWriteLine(string value) { }

        // Implementation of Harmony patch used for Prefix "Manual Patching"
        public static bool PreFix_WriteLine(ref string value)
        {
            // Calling the Reverse Patch for Console.WriteLine() from PreFix_WriteLine
            MyWriteLine("Reverse Patch for Console.WriteLine() from PreFix_WriteLine!!!");

            if (value.Contains("Hook")) { value = "Captain Hook Was Here!!!"; }
            return true; // Do not skip executing original Console.WriteLine()
        }
    }
}
```

The method `void Console.WriteLine(System.String)` was successfully hooked, and all its invocations were intercepted by the implemented Prefix patch `PreFix_WriteLine`. It only changed when the original argument contained the string value “ **Hook**” (e.g., “ **Hook Me If You Can!!!**” → “ **Captain Hook Was Here!!!**”). Furthermore, we can independently use the Reverse Patch `MyWriteLine` for the original `void Console.WriteLine(System.String)` and call it even from the Prefix patch `PreFix_WriteLine` that was applied to it.

![Figure 9: Reverse Patch - Calling the original method “Console.WriteLine()”.](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId65.png)Figure 9: Reverse Patch – Calling the original method “Console.WriteLine()”.

It is worth noting that during our walk-through of all common implementation examples, we tried to make it simple but still worked quite hard with the “ [**Manual Patching**](https://harmony.pardeike.net/articles/basics.html#manual-patching)” to create and organize patches using the Harmony library (avoiding the usage of “ [**Annotations**](https://harmony.pardeike.net/articles/annotations.html)”) as it highly relies on the reflection. Furthermore, we mostly directly used the reflection to get runtime types, methods, etc. The Harmony library also provides some [utilities](https://harmony.pardeike.net/articles/utilities.html) that can simplify a lot of things – e.g., a helper class `AccessTools` (wrapper that simplifies the reflection), `Traverse` (like a LINQ wrapper for classes), and more.

## Practical Harmony Usage – ConfuserEx2 String Decryptor

Encouraged by the knowledge from the previous sections, we can move forward to a simple, practical example that results in the creation of the [**ConfuserEx2 String Decryptor**](https://github.com/Dump-GUY/ConfuserEx2_String_Decryptor) tool.

Usually, when we are dealing with obfuscated dotnet malware, the first thing we target are encrypted constants, specifically string objects. Reconstruction of the original strings can often be a “shortcut” for revealing the crucial functionality, configuration, and other important aspects of the malware.

A significant amount of malware samples come in the form of obfuscated or protected code. Currently, there are more than a hundred known dotnet obfuscators that are either commercially or freely available as open-source projects. One of the most used protectors from the second group is the notorious [ConfuserEx2](https://mkaring.github.io/ConfuserEx/). This protector evolved from the first release known as Confuser to [ConfuserEx](https://github.com/yck1509/ConfuserEx), which later resulted in a fork introduced as [ConfuserEx2](https://github.com/mkaring/ConfuserEx).

While the vanilla version of ConfuserEx2 is heavily used by commodity malware, it is not so unusual to see it being used by advanced threat actors in a form that is slightly customized but enough to disable the functionality of freely available, known deobfuscators.

Even in the case of the vanilla version of ConfuserEx2, there are no publicly available, dedicated deobfuscators that can reliably allow the reconstruction of constants (mainly `string` objects and `char[]` arrays) protected by this obfuscator. In this section, we show how to create one such tool that uses the Harmony library to bypass some of the ConfuserEx2 checks, allowing us to proceed with the deobfuscation logic.

To find out how the ConfuserEx2 constants protection works, where the main problem is, and how we can defeat it, we built a simple C#, Console App using .NET Framework that became the target for the obfuscation.

![Figure 10: Example program as a target for the ConfuserEx2 obfuscation (dnSpyEx view).](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId75.png)Figure 10: Example program as a target for the ConfuserEx2 obfuscation (dnSpyEx view).

After applying ConfuserEx2 constants protection, our original example program turns into the obfuscated code that holds all `string` objects and `char[]` arrays in an encrypted form.

![Figure 11: ConfuserEx2 obfuscated example program - constants protected.](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId78.png)Figure 11: ConfuserEx2 obfuscated example program – constants protected.

One of the most straightforward ways to deobfuscate and reconstruct the original constants is based on a dynamic approach using reflection to simply invoke all the constants’ decryption functions with proper arguments. But once we check such decryption functions in a ConfuserEx2-protected binary, we can immediately spot something that protects the function invocation in exactly the way we want to do so.

![Figure 12: One of the constants’ decryption functions.](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId81.png)Figure 12: One of the constants’ decryption functions.

Notice the `Assembly.GetExecutingAssembly().Equals(Assembly.GetCallingAssembly())` check compares the .NET Assembly containing the currently executing code with the .NET Assembly that invoked the currently executing method and expects them to be equal. Of course, the dynamic approach using reflection to get rid of the obfuscation will fail to pass this check.

This is the exact moment where the Harmony library comes into play. We can implement a Prefix type of patch for the original method `GetCallingAssembly()` that hooks this function in a way that always returns the obfuscated .NET Assembly, no matter which assembly was originally responsible for the function invocation. This patch allows us to bypass the check and continue with our dynamic approach.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

// Targeted obfuscated .NET Assembly loaded via Reflection

static Assembly LoadedAssembly;

// Installing the Prefix patch for method "Assembly GetCallingAssembly()"

private static voidInstallHook()

{

var target = typeof(Assembly).GetMethod("GetCallingAssembly");

if(target == null)

throw newException("Could not resolve Assembly.GetCallingAssembly");

var harmony = newHarmony("GetCallingAssembly");

var stub = typeof(Program).GetMethod("PreFix\_GetCallingAssembly");

harmony.Patch(target, newHarmonyMethod(stub));

}

// Implementation of Harmony patch used for Prefix "Manual Patching"

public static bool PreFix\_GetCallingAssembly(ref Assembly \_\_result)

{

\_\_result = LoadedAssembly; // Setting the result - return value

returnfalse; // Skip executing the original GetCallingAssembly()

}

// Targeted obfuscated .NET Assembly loaded via Reflection
static Assembly LoadedAssembly;

// Installing the Prefix patch for method "Assembly GetCallingAssembly()"
private static void InstallHook()
{
var target = typeof(Assembly).GetMethod("GetCallingAssembly");
if (target == null)
throw new Exception("Could not resolve Assembly.GetCallingAssembly");

var harmony = new Harmony("GetCallingAssembly");
var stub = typeof(Program).GetMethod("PreFix\_GetCallingAssembly");
harmony.Patch(target, new HarmonyMethod(stub));
}

// Implementation of Harmony patch used for Prefix "Manual Patching"
public static bool PreFix\_GetCallingAssembly(ref Assembly \_\_result)
{
\_\_result = LoadedAssembly; // Setting the result - return value
return false; // Skip executing the original GetCallingAssembly()
}

```
// Targeted obfuscated .NET Assembly loaded via Reflection
static Assembly LoadedAssembly;

// Installing the Prefix patch for method "Assembly GetCallingAssembly()"
private static void InstallHook()
{
    var target = typeof(Assembly).GetMethod("GetCallingAssembly");
    if (target == null)
        throw new Exception("Could not resolve Assembly.GetCallingAssembly");

    var harmony = new Harmony("GetCallingAssembly");
    var stub = typeof(Program).GetMethod("PreFix_GetCallingAssembly");
    harmony.Patch(target, new HarmonyMethod(stub));
}

// Implementation of Harmony patch used for Prefix "Manual Patching"
public static bool PreFix_GetCallingAssembly(ref Assembly __result)
{
    __result = LoadedAssembly; // Setting the result - return value
    return false; // Skip executing the original GetCallingAssembly()
}
```

Enriching the Prefix patch implementation above with a .NET Assembly parsing logic (using [AsmResolver](https://github.com/Washi1337/AsmResolver) library) to properly find all invocations of constants’ decryption functions with corresponding arguments, and further invoking them via reflection, allows us to obtain the decrypted form of constants that helps to rebuild the deobfuscated sample. The complete source code is available [here](https://github.com/Dump-GUY/ConfuserEx2_String_Decryptor/blob/main/ConfuserEx2_String_Decryptor/ConfuserEx2_String_Decryptor/Program.cs) and results in a tool called “ **ConfuserEx2\_String\_Decryptor**”.

Using this tool to deobfuscate our example ConfuserEx2 protected program is shown below (40s GIF):

![](https://research.checkpoint.com/wp-content/uploads/2024/01/rId86-1.gif)Figure 13: Deobfuscation with the “ **ConfuserEx2\_String\_Decryptor**” tool (40s GIF).

## Harmony Hooking from the DnSpyEx Debugging Context

Regarding the instrumentation of the .NET code, the Harmony library has already proved to be very useful for some specific tasks (shown in the “ **Common Examples of Implementation**” section), especially when it comes to automating. However, we still do not have the best and easiest control over the exact moment when the Harmony patches are installed and uninstalled.

Let’s take an example code like the one shown below and imagine altering the functionality of the 5th → 8th invocations of the `void Console.WriteLine(System.String)` method.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

static voidMain()

{

Console.WriteLine("Hook Me If You Can!!!");

Console.WriteLine("Hook Me If You Can!!!");

Console.WriteLine("Hook Me If You Can!!!");

Console.WriteLine("Hook Me If You Can!!!");

Console.WriteLine("Hook Me If You Can!!!"); // Alter This

Console.WriteLine("Hook Me If You Can!!!"); // Alter This

Console.WriteLine("Hook Me If You Can!!!"); // Alter This

Console.WriteLine("Hook Me If You Can!!!"); // Alter This

Console.WriteLine("Hook Me If You Can!!!");

Console.WriteLine("Hook Me If You Can!!!");

Console.WriteLine("Hook Me If You Can!!!");

Console.WriteLine("Hook Me If You Can!!!");

}

static void Main()
{
Console.WriteLine("Hook Me If You Can!!!");
Console.WriteLine("Hook Me If You Can!!!");
Console.WriteLine("Hook Me If You Can!!!");
Console.WriteLine("Hook Me If You Can!!!");
Console.WriteLine("Hook Me If You Can!!!"); // Alter This
Console.WriteLine("Hook Me If You Can!!!"); // Alter This
Console.WriteLine("Hook Me If You Can!!!"); // Alter This
Console.WriteLine("Hook Me If You Can!!!"); // Alter This
Console.WriteLine("Hook Me If You Can!!!");
Console.WriteLine("Hook Me If You Can!!!");
Console.WriteLine("Hook Me If You Can!!!");
Console.WriteLine("Hook Me If You Can!!!");
}

```
static void Main()
{
    Console.WriteLine("Hook Me If You Can!!!");
    Console.WriteLine("Hook Me If You Can!!!");
    Console.WriteLine("Hook Me If You Can!!!");
    Console.WriteLine("Hook Me If You Can!!!");
    Console.WriteLine("Hook Me If You Can!!!"); // Alter This
    Console.WriteLine("Hook Me If You Can!!!"); // Alter This
    Console.WriteLine("Hook Me If You Can!!!"); // Alter This
    Console.WriteLine("Hook Me If You Can!!!"); // Alter This
    Console.WriteLine("Hook Me If You Can!!!");
    Console.WriteLine("Hook Me If You Can!!!");
    Console.WriteLine("Hook Me If You Can!!!");
    Console.WriteLine("Hook Me If You Can!!!");
}
```

In this simple case, we can very likely come up with some clumsy solution using just the Harmony library, but this will not work in much more complex situations.

Usually, when we want to have absolute control over the instrumentation of .NET code, using a managed debugger like [dnSpyEx](https://github.com/dnSpyEx/dnSpy) is the most convenient way. The main disadvantage is that in the case of a non-scriptable debugger, altering the functionality of certain parts of the code becomes a manual, time-consuming piece of work, far removed from automation.

If there was a way to effectively combine the debugging of dnSpyEx with the hooking features of the Harmony library, we could harness the strengths of both tools to their fullest extent. And the exciting part is, it’s already a reality.

First, we prepare the Harmony hooking library that is going to be used from the dnSpyEx debugging context. This example library hooks the `void Console.WriteLine(System.String)` function using the Prefix type of patch and contains two other methods, `InstallHook()` and `UninstallHook()`, that invoke the patching and unpatching.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

using System;

using System.Reflection;

using HarmonyLib;

namespace Captain\_HooK

{

public class HooK

{

public static voidUninstallHook()

{

(newHarmony("ItDoesNotMatter")).UnpatchAll("WriteLine");

}

public static voidInstallHook()

{

MethodInfo target = typeof(Console).GetMethod("WriteLine", new\[\]{typeof(string)});

if(target == null)

throw newException("Could not resolve Console.WriteLine");

Harmony harmony = newHarmony("WriteLine");

MethodInfo stub = typeof(HooK).GetMethod("PreFix\_WriteLine");

harmony.Patch(target, newHarmonyMethod(stub));

}

public static bool PreFix\_WriteLine(ref string value)

{

value = "Captain Hook Was Here!!!";

returntrue;

}

}

}

using System;
using System.Reflection;
using HarmonyLib;

namespace Captain\_HooK
{
public class HooK
{
public static void UninstallHook()
{
(new Harmony("ItDoesNotMatter")).UnpatchAll("WriteLine");
}

public static void InstallHook()
{
MethodInfo target = typeof(Console).GetMethod("WriteLine", new\[\] { typeof(string) });
if (target == null)
throw new Exception("Could not resolve Console.WriteLine");

Harmony harmony = new Harmony("WriteLine");
MethodInfo stub = typeof(HooK).GetMethod("PreFix\_WriteLine");
harmony.Patch(target, new HarmonyMethod(stub));
}

public static bool PreFix\_WriteLine(ref string value)
{
value = "Captain Hook Was Here!!!";
return true;
}
}
}

```
using System;
using System.Reflection;
using HarmonyLib;

namespace Captain_HooK
{
    public class HooK
    {
        public static void UninstallHook()
        {
            (new Harmony("ItDoesNotMatter")).UnpatchAll("WriteLine");
        }

        public static void InstallHook()
        {
            MethodInfo target = typeof(Console).GetMethod("WriteLine", new[] { typeof(string) });
            if (target == null)
                throw new Exception("Could not resolve Console.WriteLine");

            Harmony harmony = new Harmony("WriteLine");
            MethodInfo stub = typeof(HooK).GetMethod("PreFix_WriteLine");
            harmony.Patch(target, new HarmonyMethod(stub));
        }

        public static bool PreFix_WriteLine(ref string value)
        {
            value = "Captain Hook Was Here!!!";
            return true;
        }
    }
}
```

Next, we need to be able to load our prepared Harmony library from the dnSpyEx debugger and invoke the `InstallHook()` and `UninstallHook()` functions in the context of the debugged process. For that purpose, we can use the “ **Watch Window**” in the dnSpyEx debugger that has the ability to evaluate C# expressions in the context of the debugged application. An example of such expression evaluation is shown below.

![Figure 14: DnSpyEx debugger - Example of expression evaluation via “Watch Window”.](https://research.checkpoint.com/wp-content/uploads/2024/01/7YRZ5D22HF-rId90.png)Figure 14: DnSpyEx debugger – Example of expression evaluation via “Watch Window”.

The last thing we need to prepare is the magic incantations that will use the expression evaluation to invoke the functions `InstallHook()` and `UninstallHook()` at the precise moment we want to do so.

Plain text

Copy to clipboard

Open code in new window

EnlighterJS 3 Syntax Highlighter

// Invoke InstallHook()

((System.Reflection.Assembly.LoadFile(@"C:\\Captain\_HooK.dll").GetType("Captain\_HooK.HooK")).GetMethod("InstallHook")).Invoke(null, null);

// Invoke UninstallHook()

((System.Reflection.Assembly.LoadFile(@"C:\\Captain\_HooK.dll").GetType("Captain\_HooK.HooK")).GetMethod("UninstallHook")).Invoke(null, null);

// Invoke InstallHook()
((System.Reflection.Assembly.LoadFile(@"C:\\Captain\_HooK.dll").GetType("Captain\_HooK.HooK")).GetMethod("InstallHook")).Invoke(null, null);

// Invoke UninstallHook()
((System.Reflection.Assembly.LoadFile(@"C:\\Captain\_HooK.dll").GetType("Captain\_HooK.HooK")).GetMethod("UninstallHook")).Invoke(null, null);

```
// Invoke InstallHook()
((System.Reflection.Assembly.LoadFile(@"C:\Captain_HooK.dll").GetType("Captain_HooK.HooK")).GetMethod("InstallHook")).Invoke(null, null);

// Invoke UninstallHook()
((System.Reflection.Assembly.LoadFile(@"C:\Captain_HooK.dll").GetType("Captain_HooK.HooK")).GetMethod("UninstallHook")).Invoke(null, null);
```

Putting it all together, using the dnSpyEx “ **Watch Window**” expression evaluation to perform the Harmony hooking from the debugging context is shown below (45s GIF):

![](https://research.checkpoint.com/wp-content/uploads/2024/01/rId93-2.gif)Figure 15: Harmony hooking from the dnSpyEx debugging context (45s GIF).

## Conclusion

In this article, we introduced .NET managed hooking using the **Harmony** library and its internals. We presented examples of implementations that covered the most common usage of the Harmony library and its different types of patches.

These examples demonstrate how powerful .NET hooking can be and more importantly, how easy and straightforward it is to implement .NET instrumentation once we use the Harmony library.

We showed how useful the Harmony hooking is in a practical example involving the notorious obfuscator “ConfuserEx2” that results in the release of the publicly available tool “ **ConfuserEx2\_String\_Decryptor**”.

Finally, we revealed a neat trick how to use the Harmony hooking from the dnSpyEx debugging context. This combination of debugging and hooking gave us the ability to automate the instrumentation of .NET code, still preserving full control over its state of execution.

One of the main advantages of the .NET hooking is that it operates only on in-memory code, so it does not touch the files on disk in any way. This comes in very handy, especially in cases where we are dealing with dotnet malware protected by an obfuscator in a way that the deobfuscation via .NET Assembly rebuilding is time-consuming and needs to be done very carefully so as not to destroy the original structure, which can later lead to a complete loss of functionality.

The other advantage is that we are not only limited to hook .NET methods defined in the scope of one specific .NET Assembly, but we can alter the functionality of _all_ referenced assemblies, especially those that come with and build the .NET Runtime.

Even though we mostly focused on the basics of .NET hooking and just briefly touched on its practical uses, our readers gained a lot of information on how to construct a shortcut for malware analysis in areas like: .NET Instrumentation, Tracing, Deobfuscation, etc.

## References

Harmony Library: [https://github.com/pardeike/Harmony](https://github.com/pardeike/Harmony)

Harmony Library – Documentation: [https://harmony.pardeike.net/](https://harmony.pardeike.net/)

ExtremeDumper: [https://github.com/wwh1004/ExtremeDumper](https://github.com/wwh1004/ExtremeDumper)

DnSpyEx: [https://github.com/dnSpyEx/dnSpy](https://github.com/dnSpyEx/dnSpy)

ConfuserEx2 Protector: [https://github.com/mkaring/ConfuserEx](https://github.com/mkaring/ConfuserEx)

AsmResolver: [https://github.com/Washi1337/AsmResolver](https://github.com/Washi1337/AsmResolver)

ConfuserEx2 String Decryptor: [https://github.com/Dump-GUY/ConfuserEx2\_String\_Decryptor](https://github.com/Dump-GUY/ConfuserEx2_String_Decryptor)

[![](https://research.checkpoint.com/wp-content/uploads/2022/10/back_arrow.svg)\\
\\
\\
GO UP](https://research.checkpoint.com/2024/net-hooking-harmonizing-managed-territory/#single-post)

[BACK TO ALL POSTS](https://research.checkpoint.com/latest-publications/)

## POPULAR POSTS

[![](https://research.checkpoint.com/wp-content/uploads/2023/01/AI-1059x529-copy.jpg)](https://research.checkpoint.com/2023/opwnai-cybercriminals-starting-to-use-chatgpt/)

- Artificial Intelligence
- ChatGPT
- Check Point Research Publications

[OPWNAI : Cybercriminals Starting to Use ChatGPT](https://research.checkpoint.com/2023/opwnai-cybercriminals-starting-to-use-chatgpt/)

[![](https://research.checkpoint.com/wp-content/uploads/2019/01/Fortnite_1021x580.jpg)](https://research.checkpoint.com/2019/hacking-fortnite/)

- Check Point Research Publications
- Threat Research

[Hacking Fortnite Accounts](https://research.checkpoint.com/2019/hacking-fortnite/)

[![](https://research.checkpoint.com/wp-content/uploads/2022/12/OpenAIchatGPT_header.jpg)](https://research.checkpoint.com/2022/opwnai-ai-that-can-save-the-day-or-hack-it-away/)

- Artificial Intelligence
- ChatGPT
- Check Point Research Publications

[OpwnAI: AI That Can Save the Day or HACK it Away](https://research.checkpoint.com/2022/opwnai-ai-that-can-save-the-day-or-hack-it-away/)

### BLOGS AND PUBLICATIONS

[![](https://research.checkpoint.com/wp-content/uploads/2017/08/WannaCry-Post-No-Image-1021x450.jpg)](https://research.checkpoint.com/2017/the-next-wannacry-vulnerability-is-here/)

- Check Point Research Publications

August 11, 2017

### “The Next WannaCry” Vulnerability is Here

[![](https://research.checkpoint.com/wp-content/uploads/2018/01/rubyminer.jpg)](https://research.checkpoint.com/2018/rubyminer-cryptominer-affects-30-ww-networks/)

- Check Point Research Publications

January 11, 2018

### ‘RubyMiner’ Cryptominer Affects 30% of WW Networks

[![](https://research.checkpoint.com/wp-content/uploads/2020/02/CheckPointResearchTurkishRat_blog_header.jpg)](https://research.checkpoint.com/2020/the-turkish-rat-distributes-evolved-adwind-in-a-massive-ongoing-phishing-campaign/)

- Check Point Research Publications
- Global Cyber Attack Reports
- Threat Research

February 17, 2020

### “The Turkish Rat” Evolved Adwind in a Massive Ongoing Phishing Campaign

[![](https://research.checkpoint.com/wp-content/uploads/2017/08/WannaCry-Post-No-Image-1021x450.jpg)](https://research.checkpoint.com/2017/the-next-wannacry-vulnerability-is-here/)

- Check Point Research Publications

August 11, 2017

### “The Next WannaCry” Vulnerability is Here

[![](https://research.checkpoint.com/wp-content/uploads/2018/01/rubyminer.jpg)](https://research.checkpoint.com/2018/rubyminer-cryptominer-affects-30-ww-networks/)

- Check Point Research Publications

January 11, 2018

### ‘RubyMiner’ Cryptominer Affects 30% of WW Networks

[![](https://research.checkpoint.com/wp-content/uploads/2020/02/CheckPointResearchTurkishRat_blog_header.jpg)](https://research.checkpoint.com/2020/the-turkish-rat-distributes-evolved-adwind-in-a-massive-ongoing-phishing-campaign/)

- Check Point Research Publications
- Global Cyber Attack Reports
- Threat Research

February 17, 2020

### “The Turkish Rat” Evolved Adwind in a Massive Ongoing Phishing Campaign

[![](https://research.checkpoint.com/wp-content/uploads/2017/08/WannaCry-Post-No-Image-1021x450.jpg)](https://research.checkpoint.com/2017/the-next-wannacry-vulnerability-is-here/)

- Check Point Research Publications

August 11, 2017

### “The Next WannaCry” Vulnerability is Here

- 1
- 2
- 3

## We value your privacy!

BFSI uses cookies on this site. We use cookies to enable faster and easier experience for you. By continuing to visit this website you agree to our use of cookies.

ACCEPT

REJECT