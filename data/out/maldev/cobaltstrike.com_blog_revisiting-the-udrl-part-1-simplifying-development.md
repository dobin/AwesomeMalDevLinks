# https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-1-simplifying-development

This website uses cookies. You may change your settings at any time.

AcceptReject AllManage Cookies

Cookie Preferences

[Home](https://www.cobaltstrike.com/) » [Blog](https://www.cobaltstrike.com/blog/) » Revisiting the User-Defined Reflective Loader Part 1: Simplifying Development

# Revisiting the User-Defined Reflective Loader Part 1: Simplifying Development

This blog post accompanies a new addition to the Arsenal Kit – The User-Defined Reflective Loader Visual Studio (UDRL-VS). Over the past few months, we have received a lot of feedback from our users that whilst the flexibility of the UDRL is great, there is not enough information/example code to get the most out of this feature. The intention of this kit is to lower the barrier to entry for developing and debugging custom reflective loaders. This post includes a walkthrough of creating a UDRL in Visual Studio that facilitates debugging, an introduction to UDRL-VS, and an overview of how to apply a UDRL to Beacon.

**Note:** _There are many people out there that prefer to use tools such as MingGW/GCC/LD/GDB etc. and we salute you. However, this post is intended for those of us that like the simplicity of Visual Studio and enjoy a GUI. To develop this template we used Visual Studio Community 2022._

### Reflective Loading

Beacon is just a Dynamic Link Library (DLL). As a result, it needs to be “loaded” for us to work with it. There are many different ways to load a DLL in Windows, but [Reflective DLL Injection](https://github.com/stephenfewer/ReflectiveDLLInjection), first published by Stephen Fewer in 2008, provides the means to load a DLL completely in memory. There is a lot of information available regarding [PE files](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format), [reflective loading](https://securityintelligence.com/posts/defining-cobalt-strike-reflective-loader/), and even [improving upon Reflective DLL Injection](https://disman.tl/2015/01/30/an-improved-reflective-dll-injection-technique.html). Therefore, this post will not delve into this in much detail. Fundamentally though, a reflective loader must:

- Allocate some memory.
- Copy the target DLL into that memory allocation.
- Parse the target DLL’s imports/load the required modules/resolve function addresses.
- Rebase the DLL (fix the relocations).
- Locate the DLL’s Entry Point.
- Execute the Entry Point.

In Stephen Fewer’s original implementation, the code used to load the DLL into memory is compiled into the DLL and “ [exported](https://learn.microsoft.com/en-us/cpp/build/exporting-from-a-dll?view=msvc-170)” as a function. This is how Beacon’s default reflective loader works; if you inspect Beacon’s exported functions you’ll find one called `ReflectiveLoader()` which is where the magic happens. The following screenshot shows Beacon’s Export Address Table (EAT) and its `ReflectiveLoader()` function in [CFF Explorer](https://ntcore.com/?page_id=388).

![](https://www.cobaltstrike.com/app/uploads/2023/07/cffexplorer_beacon-reflective-loader-function.png)Figure 1. Beacon’s Export Address Table in CFF Explorer.

**Note:** _Typically, when a reflective loader is implemented in this fashion, a small shellcode stub is also written to the start of the PE file (over the DOS header) to ensure that execution is correctly directed to the right place (the `ReflectiveLoader()` function). This is what makes it position independent as it’s possible to simply write the reflective DLL to memory, start a thread and let it run._

In 2017, an [analysis of the Double Pulsar User Mode Injector](https://blog.f-secure.com/doublepulsar-usermode-analysis-generic-reflective-dll-loader/) ( _Double Pulsar_) leaked by Shadow Brokers showed an alternate approach to reflective loading ( [archive link](https://web.archive.org/web/20171118102938/https:/www.countercept.com/our-thinking/doublepulsar-usermode-analysis-generic-reflective-dll-loader/)). _Double Pulsar_ differed because it was not compiled into the DLL but prepended in front of it. This approach allowed it to reflectively load any DLL. Later in 2017, the [Shellcode Reflective DLL Injection](https://www.netspi.com/blog/technical/adversary-simulation/srdi-shellcode-reflective-dll-injection/) (sRDI) project was released which used a similar approach. [sRDI](https://github.com/monoxgas/sRDI) is able to take an arbitrary PE file and make it _position independent_ which means it can also be used to load Beacon.

The following high-level diagram shows the different locations of the reflective loader between Stephen Fewer’s approach and _Double Pulsar_.

![](https://www.cobaltstrike.com/app/uploads/2023/07/diagram_different-locations-of-reflective-loader-1024x483.png)Figure 2. The different locations of `ReflectiveLoader()`.

### The User-Defined Reflective Loader (UDRL)

The UDRL is an important aspect of Cobalt Strike’s evasion strategy. Cobalt Strike achieves “ _evasion through flexibility_”, meaning we give you the tools you need to modify default behaviors and customize Beacon to your liking. This was something that Raphael Mudge felt strongly about and will remain a key part of the Cobalt Strike strategy moving forward.

As described above, Beacon’s default `ReflectiveLoader()` is compiled into Beacon and _exported_. As a result, the UDRL was originally intended to work in the same fashion. The Teamserver would take a given UDRL and use it to overwrite Beacon’s default `ReflectiveLoader()` function. A great example of a UDRL that utilizes this workflow is [BokuLoader](https://github.com/boku7/BokuLoader) by Bobby Cooke.

In this blog post, we’ll be exploring the same approach used by _Double Pulsar_ and will therefore append Beacon to our loader as shown in Figure 2. _TitanLdr_ by [Austin Hudson](https://twitter.com/ilove2pwn_) is an excellent example of a UDRL that uses this approach. [AceLdr](https://github.com/kyleavery/AceLdr) by Kyle Avery is another very good example that also includes some additional functionality for [avoiding memory scanners](https://www.blackhillsinfosec.com/avoiding-memory-scanners/).

There are likely many other UDRLs available, and without a doubt even more that have not been made public. The above projects have been mentioned as they are impressive public examples. If you’ve developed a UDRL for Cobalt Strike yourself and you’d like to share it, you can submit it to the [Cobalt Strike Community Kit](https://cobalt-strike.github.io/community_kit/).

### Enter Visual Studio

The original UDRL example provided in the Arsenal Kit is a slightly modified version of Stephen Fewer’s [reflective loader](https://github.com/stephenfewer/ReflectiveDLLInjection), so here we’ll also start in the same place. To save a lot of unnecessary content, we will not cover the process of creating an empty Visual Studio project and copy/pasting code. The only slight difference at this stage however is that our project files were created with the .cpp extension. This minor change to .cpp allows the project to access some additional functionality (more on this later). For clarity, the folder layout of the project after copy/pasting Stephen Fewer’s code has been illustrated below.

```
UDRL-VS/
├── Header Files/
│ ├── ReflectiveDLLInjection.h
│ └── ReflectiveLoader.h
├── Source Files/
└── ReflectiveLoader.cpp
```

The purpose of this Visual Studio project is to create a PE executable file that contains our reflective loader. This executable file can then be compiled in either _Debug_ mode or _Release_ mode. In _Debug_ mode it can be used in combination with Visual Studio’s debugger to step through the code and _Debug_ our loader. In _Release_ mode, we can strip our loader out of the resulting executable and prepend it to Beacon to create a _Double Pulsar_ style payload as illustrated in Figure 2.

To compile the project and ensure that it executes correctly, we need to change some of Visual Studio’s Project Settings. These have been outlined below:

- [Entry Point](https://learn.microsoft.com/en-us/cpp/build/reference/entry-entry-point-symbol?view=msvc-170) ( _ReflectiveLoader_) – This setting changes the default starting address to Stephen Fewer’s `ReflectiveLoader()` function. A custom entry point would normally be problematic for a traditional PE file and require some manual initialization. However, Stephen Fewer’s code is _position independent_, so this won’t be a problem.
- [Enable Intrinsic Functions](https://learn.microsoft.com/en-us/cpp/build/reference/oi-generate-intrinsic-functions?view=msvc-170) ( _Yes_) – [Intrinsic functions](https://learn.microsoft.com/en-us/cpp/intrinsics/compiler-intrinsics?view=msvc-170) are built into the compiler and make it possible to “ _call_” certain assembly instructions. These functions are “ _inlined_” automatically which means the compiler inserts them at compile time.
- [Ignore All Default Libraries](https://learn.microsoft.com/en-us/cpp/build/reference/nodefaultlib-ignore-libraries?view=msvc-170) ( _Yes_) – This setting will alert us when we call external functions (as that would not be _position independent_).
- [Basic Runtime Checks](https://learn.microsoft.com/en-us/cpp/build/reference/rtc-run-time-error-checks?view=msvc-170) ( _Default_) – This setting is configured correctly in _Release_ mode by default, but changing it in the _Debug_ configuration disables some runtime error checking that will throw an error due to our custom entry point.
- Optimization – We’ve enabled several of Visual Studio’s different Optimization settings and opted to favor smaller code where possible. However, at certain points in the template we’ve disabled it to ensure our code works as expected.

**Note:** _Optimization can be great because it makes our code smaller and faster. However, it’s important to know what can be optimized and what can’t, which is made even more complex when writing position independent code. If you run into problems, it can be worth checking whether something is being optimized away by the compiler._

### Function Positioning

In this post, we are using the _Double Pulsar_ approach to reflective loading. Therefore, after compiling the _Release_ build, we will extract the loader from the resulting executable and prepend it to Beacon to create our payload. As part of this model, we need to ensure that the loaders’ entry point sits at the very start of the shellcode. We also need to make sure that we can identify the end of the loader in order to find out where Beacon begins. This has been illustrated in the following high-level diagram:

![](https://www.cobaltstrike.com/app/uploads/2023/07/diagram_ldrEnd-and-beacon-2.png)Figure 3. A high-level overview of Function Positioning.

There are different ways to achieve this “ _positioning_”, however, for the purposes of this template we have used the [code\_seg](https://learn.microsoft.com/en-us/cpp/preprocessor/code-seg?view=msvc-170) [pragma directive](https://learn.microsoft.com/en-us/cpp/preprocessor/pragma-directives-and-the-pragma-keyword?view=msvc-170). `code_seg` can be used to specify which section is used to store specific functions. These sections can then be ordered using [alphabetical values](https://devblogs.microsoft.com/oldnewthing/20181107-00/?p=100155) e.g `.text$a`. This is possible because the linker takes the section names and splits them at the first dollar sign, the value after it is then used to sort the sections which facilitates the alphabetical ordering. A similar approach to function ordering can also be seen in both TitanLdr/AceLdr in [link.ld](https://github.com/kyleavery/AceLdr/blob/main/src/link.ld).

In the example below, we have placed the `ReflectiveLoader()` function within `.text$a` to ensure that it is positioned at the start of the `.text` section and therefore the start of the payload. The remaining functions in `ReflectiveLoader.cpp` have been placed inside `.text$b` to ensure that they are located after `ReflectiveLoader()`. The compiler can order the functions within a given section however it chooses, so this approach of using `$a` and `$b` enforces the required layout.

```
#pragma code_seg(".text$a")
ULONG_PTR WINAPI ReflectiveLoader(VOID) {
[…SNIP…]
}
#pragma code_seg(".text$b")
[…SNIP…]
```

**Note:** _In some public examples of reflective loaders, a small shellcode stub is used at the very start of execution to ensure stack alignment. This approach is not explicitly required in our template at this point as the loader is intended for use with memory allocation/thread creation APIs for simplicity. It should therefore be aligned correctly. If you do require this stack alignment, it would still be possible to use a similar shellcode stub in this model but it can be left as an exercise for the reader. Matt Graeber’s [Writing Optimized Windows Shellcode in C](https://exploitmonday.blogspot.com/2013/08/writing-optimized-windows-shellcode-in-c.html) and the associated [PIC\_Bindshell](https://github.com/mattifestation/PIC_Bindshell) code demonstrate this. In addition, it can also be found in TitanLdr/Aceldr in [start.asm](https://github.com/kyleavery/AceLdr/blob/main/src/asm/start.asm)._

We can use the same approach described above to also locate the end of the loader. In the code snippet below, we have used the `code_seg` directive once more to position the `LdrEnd()` function. Previously, we used `$a` to position `ReflectiveLoader()` at the start of the `.text` section and here we are using `$z` to position `LdrEnd()` at the end of it.

```
#pragma code_seg(".text$z")
void LdrEnd() {}
```

The following high-level diagram illustrates the code sections described above.

![](https://www.cobaltstrike.com/app/uploads/2023/07/diagram_ldrEnd-and-beacon-alphabetical.png)Figure 4. A high-level overview of Function Positioning with alphabetical values.

The _Release_ build is designed to work with the Teamserver which will append Beacon to our loader. As part of the _Debug_ build, we need to simulate the _Release_ mode behavior. The `code_seg` directive can also be used in combination with the [declspec](https://learn.microsoft.com/en-us/cpp/cpp/declspec?view=msvc-170) [allocate](https://learn.microsoft.com/en-us/cpp/cpp/allocate?view=msvc-170) specifier to position the contents of data items. In the example below, we use the `code_seg` directive to specify a section, and then use the `declspec` specifier to place the contents of `Beacon.h` (`unsigned char beacon_dll[]`) within it. This logic was placed in `End.h`/`End.cpp` for simplicity.

```
#ifdef _DEBUG
#pragma code_seg(".text$z")
__declspec(allocate(".text$z"))
#include "Beacon.h"
#endif
```

The folder layout after adding the above files to the project has been illustrated below.

```
UDRL-VS/
├── Header Files/
│   ├── Beacon.h
│   ├── End.h
│   ├── ReflectiveDLLInjection.h
│   └── ReflectiveLoader.h
├── Source Files/
    ├── End.cpp
    └── ReflectiveLoader.cpp
```

This is the crux of our development environment, by positioning `LdrEnd()`/`Beacon.h` we’re able to easily find the location of Beacon. This change to Stephen Fewer’s original code has been shown below.

```
#ifdef _DEBUG
    uiLibraryAddress = (ULONG_PTR)beacon_dll;
#elif _WIN64
    uiLibraryAddress = (ULONG_PTR)&ldr_end + 1;
[…SNIP…]
#endif
```

**Note:** _The x86 version of the Release build works in a slightly different fashion to the one described above. Positioning `LdrEnd()` and referencing its address works in x64 because the compiler identifies it using relative addressing. Disassembling the binary shows a “load effective address” at `[rip + offset]` (`LEA RSI,[RIP+0X6B9]`). This approach does not work in x86 because the absolute address of `LdrEnd()` is calculated at compile time. Therefore, it points to a completely incorrect location when the loader is prepended to Beacon (`MOV EBX, 0X401600`). To provide support for x86, we recycled Stephen Fewer’s `caller()` function in our template and renamed it to `GetLocation()`. This function simply returns the calling function’s return address via the `_ReturnAddress()` intrinsic function. Instead of referencing the address of `LdrEnd()` in x86, we call it, which in turn calls `GetLocation()`. We then use simple pointer arithmetic to work out the location of Beacon. We could’ve done this for both x86 and x64 but included both to show the two approaches and highlight the difference._

At this point, we now have an operational Debug build. We can set a breakpoint, click “ _Local Windows Debugger_”, and use all the features of Visual Studio’s debugger.

### The UDRL-VS Kit

In the previous section we used Stephen Fewer’s original reflective DLL injection code to show that only minor modifications were required to get up and running. However, we wanted to take this a step further and provide a template to support developing and debugging UDRLs for Cobalt Strike.

As part of creating this template, we have attempted to simplify Stephen Fewer’s original code by splitting it into separate functions, removing unused code, updating types and providing more descriptive variable names. In addition, we have also provided some helper functions to speed up writing _position independent code_ (PIC). The following sections provide an overview of these helper functions. For additional help writing PIC, there is an excellent public framework available called [ShellcodeStdio](https://github.com/jackullrich/ShellcodeStdio) that also demonstrates the techniques described below.

#### Compile Time Hashing

In Stephen Fewer’s original code, several hashes had been pre-calculated and included in `ReflectiveLoader.h`. This solution works well, but to simplify it further and make it easier for you to include your own hashes, we have added “compile time hashing”.

As the CPP reference states, the “ [`constexpr`](https://en.cppreference.com/w/cpp/language/constexpr)” specifier makes it possible to “evaluate the value of a function or variable at compile time”. Therefore, it is possible to use the `constexpr` specifier as part of a hash function to ensure that the hash is generated at compile time. This means instead of pre-calculating hashes and including them in our header file, we can have the compiler/preprocessor hash our strings for us.

**Note:** _Compile time hashing will help us more in a subsequent post, but at this point, an added benefit is that it makes it easier to rotate Stephen Fewer’s `HASH_KEY` value used to hash the strings. It is not a silver bullet but changing the `HASH_KEY` could help to push back on simple static signatures._

In the template, we have replaced Stephen Fewer’s static hash values with calls to `CompileTimeHash()`.

```
constexpr DWORD KERNEL32DLL_HASH = CompileTimeHash("kernel32.dll");
constexpr DWORD NTDLLDLL_HASH = CompileTimeHash ("ntdll.dll");

constexpr DWORD LOADLIBRARYA_HASH = CompileTimeHash("LoadLibraryA");
constexpr DWORD GETPROCADDRESS_HASH = CompileTimeHash("GetProcAddress");
constexpr DWORD VIRTUALALLOC_HASH = CompileTimeHash("VirtualAlloc");
constexpr DWORD NTFLUSHINSTRUCTIONCACHE_HASH = CompileTimeHash("NtFlushInstructionCache");
```

**Note:** _We have also modified the original `hash()` function in the template to normalize strings to uppercase before hashing so that “lOadLiBrarYa” and “LoadLibraryA” result in the same hash._

#### PRINT()

It can be helpful to print strings as part of debugging, but as we mentioned earlier, a custom entry point can affect startup routines, etc. This means that at the start of execution we do not have direct access to the C/C++ standard library or any Windows APIs.

As part of simplifying Stephen Fewer’s original code, we broke it down into independent functions. As a result, we now have a `GetProcAddressByHash()` function in `Utils.cpp` that we can use to resolve function addresses. To save a lot of time and effort we have used this to create a `_printf()` function for _Debug_ purposes and included it in our template. This `_printf()` function works in the same way as the original `printf()` so you can give it format specifiers and use it to print variables, etc. We also wrapped it into a [macro](https://www.geeksforgeeks.org/macros-and-its-types-in-c-cpp/) called `PRINT()` which will only generate the `_printf()` calls when the project is compiled in _Debug_ mode.

```
PRINT("[+] Beacon Start Address: %p\n", beaconBaseAddress);
```

Here is a screenshot of the above function in action. We have printed the location of Beacon and then found it using the disassembly view in Visual Studio.

![](https://www.cobaltstrike.com/app/uploads/2023/07/finding-beacon-MZ.png)Figure 5. Finding Beacon’s MZ Header with a call to `PRINT()`.

#### Strings

Strings are saved into the `.data`/`.rdata` section of a PE file and will therefore be unavailable once we extract the loader (which will be exclusively found in the `.text` section). It’s therefore important to understand how strings are created and stored within a PE file. [Compiler Explorer](https://godbolt.org/) is an excellent website for seeing how your code is assembled and even color codes the input/output. The following screenshot shows three different approaches to declaring strings in C++.

![](https://www.cobaltstrike.com/app/uploads/2023/07/compilerExplorer_strings-1024x537.png)Figure 6. A demonstration of how strings are created and stored with Compiler Explorer.

The first declaration uses an array initializer; this has been highlighted in yellow. The output window shows how move instructions are used to construct the string one byte at a time. This means that all the code is found within the `.text` section.

The next approach uses a string literal to initialize the data. As shown in the purple output, the bytes of the string are copied into the array from the `.data` section. This has been broken down and explained below.

```
lea    rax, QWORD PTR string$[rsp]     ; load the address of where the string will be on the stack (destination address)
lea    rcx, OFFSET FLAT : $SG2657      ; load the address of the string in the .data section (source address)
mov    rdi, rax			       ; save destination address into destination pointer (RDI)
mov    rsi, rcx			       ; save source address into source pointer (RSI)
mov    ecx, 12 			       ; save the size of the string into the count register (ECX)
rep    movsb  		               ; move a single byte from RDI to RSI and repeat based on ECX (size of string)
```

In the final example, a char pointer is initialized with a string literal. As shown in the red output, it references the value in the `.data` section. This has also been broken down and explained below.

```
lea    rax, OFFSET FLAT:$SG2658        ; load the address of the string in the .data section
mov    QWORD PTR stringPtr$[rsp], rax  ; save the address of the string on the stack
```

After reviewing the above, we can see the only real option for us when writing PIC is to either avoid using strings (not always possible) or use the first approach in the example above.

```
char helloWorld[] = {'H','e','l','l','o',' ','W','o','r','l','d','\0'};
```

As with everything when writing PIC, this is a little clumsy and cumbersome. However, [Evan McBroom](https://gist.github.com/EvanMcBroom/d7f6a8fe3b4d8f511b132518b9cf80d7) has provided a very simple and elegant solution to this problem. Evan discovered that when using the `constexpr` specifier to initialize a char array with a string literal, the resulting string was constructed in the same fashion as the array initializer described above. The following screenshot demonstrates this with Compiler Explorer.

![](https://www.cobaltstrike.com/app/uploads/2023/07/compilerExplorer_ebconstexpr-1024x395.png)Figure 7. A demonstration of Evan McBroom’s PIC string with Compiler Explorer.

Evan wrapped this into two macros that can be used to create both ASCII strings and wide strings.

```
#define PIC_STRING(NAME, STRING) constexpr char NAME[]{ STRING }
#define PIC_WSTRING(NAME, STRING) constexpr wchar_t NAME[]{ STRING }
```

We have added these two macros to the template, this can be seen in the following example.

```
PIC_STRING(example, "[!] Hello World\n");
PRINT(example);
```

### Release Mode

The ability to develop and debug inside Visual Studio is great, but what about using this loader in production? The great thing about writing a PIC loader is that everything we need is located inside the resulting PE files’ `.text` section. This means we can use a simple Python script to extract our compiled executable’s `.text` section and voila, we have our UDRL!

**Note:** _This is why we used the “Function Positioning” described earlier. We needed to ensure that our `ReflectiveLoader()` function was positioned correctly at the very start of the `.text` section, which becomes the very start of the UDRL (aka the loader)._

There are many examples of Python scripts that do something similar; both _TitanLdr_ and _[AceLdr](https://github.com/kyleavery/AceLdr/blob/main/scripts/extract.py)_ have similar scripts in their respective repositories. We have also included a script in the Arsenal kit template called `udrl.py`. Visual Studio allows us to incorporate this script as a post-build event and so the Release build will automatically create `udrl-vs.bin` in the relevant Output Directory.

To simplify testing and development, `udrl.py` also facilitates shellcode execution. This allows you to quickly test the loader without having to go via the Teamserver. We’d strongly recommend using this frequently to test your work. When writing PIC, things will often work in Debug mode but not in Release mode. For example, you can easily be caught out by forgetting the `constepxr`specifier, by forgetting to initialize pointers, or by using strings that aren’t PIC.

```
C:\> py.exe udrl.py prepend-udrl .\beacon.x64.bin .\x64\Release\udrl-vs.exe

            _      _
           | |    | |
  _   _  __| |_ __| |  _ __  _   _
 | | | |/ _` | '__| | | '_ \| | | |
 | |_| | (_| | |  | |_| |_) | |_| |
  \__,_|\__,_|_|  |_(_) .__/ \__, |
                      | |     __/ |
                      |_|    |___/

[+] Success: Extracted loader
[*] Size of loader: 1229
[+] Start Address: 0x1b690d90000
[+] Shellcode Executed
```

**Note:** _Make sure to use the 32-bit version of Python when testing x86 loaders. It will save you a couple of minutes of confusion…_

Previously we used the _Double Pulsar_ approach to loading because it simplified our Development/Debugging and provided an alternate way to write a UDRL. However, there is no reason why we can’t still use the “original” UDRL workflow and simply replace Beacon’s default loader with the one we have created.

The UDRL-VS template contains an additional Build Configuration called “Release (Stephen Fewer)”. This Build Configuration still creates the same PIC loader, however, instead of using the _`LdrEnd()`_ function to calculate the location of Beacon, it uses Stephen Fewer’s original approach of walking backward through memory to find the start address of the DLL that is being loaded (Beacon).

To make it easy to test this type of loader, we have also included an option in `udrl.py` to overwrite Beacon’s default loader and execute the resulting payload.

```
C:\> py.exe udrl.py stomp-udrl .\beacon.x64.bin ".\x64\Release (Stephen Fewer)\udrl-vs.exe"

            _      _
           | |    | |
  _   _  __| |_ __| |  _ __  _   _
 | | | |/ _` | '__| | | '_ \| | | |
 | |_| | (_| | |  | |_| |_) | |_| |
  \__,_|\__,_|_|  |_(_) .__/ \__, |
                      | |     __/ |
                      |_|    |___/

[+] Success: Extracted loader
[*] Size of loader: 1277
[*] Found ReflectiveLoader - RVA: 0x17aa4       File Offset: 0x16ea4
[+] Success: Applied UDRL to DLL
[+] Start Address: 0x27239a20000
[+] Shellcode Executed
```

Once your loader has been tested and works as expected, it can be used in combination with an Aggressor Script to make it operational. We don’t strictly need to use Aggressor. We could use a script like `udrl.py` to create the payload, however, Aggressor Script has several functions that will simplify customization in subsequent posts and saves writing extra code.

We can use some very simple Aggressor Scripts to apply our loaders to Beacon. The following example demonstrates how to append Beacon to our loader (almost a carbon copy of the one used by _TitanLdr_/ _[AceLdr](https://github.com/kyleavery/AceLdr/blob/main/bin/AceLdr.cna)_).

```
set BEACON_RDLL_GENERATE {
        # Declare local variables
	local('$arch $beacon $fileHandle $ldr $path $payload');
	$beacon = $2;
	$arch = $3;

	# Check the payload architecture
	if($arch eq "x64") {
            $path = getFileProper(script_resource("x64"), "Release", "udrl-vs.bin");
	}
        else if ($arch eq "x86") {
            $path = getFileProper(script_resource("Release"), "udrl-vs.bin");
	}
        else {
            warn("Error: Unsupported architecture: $arch");
            return $null;
        }

	# Read the UDRL from the supplied binary file
	$fileHandle = openf( $path );
	$ldr = readb( $fileHandle, -1 );
	closef( $fileHandle );
	if ( strlen( $ldr ) == 0 ) {
		warn("Error: Failed to read udrl-vs.bin");
		return $null;
	}

	# Prepend UDRL to Beacon and output the modified payload.
	return $ldr.$beacon;
}
```

The following example demonstrates how to overwrite Beacon’s default loader with our own. We still read the loader in the same fashion, but this time we call `setup_reflective_loader()`. This function does the heavy lifting for us; it finds the current `ReflectiveLoader()` function in Beacon and replaces it with the one provided.

```
set BEACON_RDLL_GENERATE {
        # Declare local variables
	local('$arch $beacon $fileHandle $ldr $path $payload');
	$beacon = $2;
	$arch = $3;

	# Check the payload architecture.
	if($arch eq "x64") {
            $path = getFileProper(script_resource("x64"), "Release (Stephen Fewer)", "udrl-vs.bin");
        }
        else if ($arch eq "x86") {
            $path = getFileProper(script_resource("Release (Stephen Fewer)"), "udrl-vs.bin");
	}
        else {
            warn("Error: Unsupported architecture: $arch");
            return $null;
        }

	# Read the UDRL from the supplied binary file
	$fileHandle = openf( $path );
	$ldr = readb( $fileHandle, -1 );
	closef( $fileHandle );
	if ( strlen( $ldr ) eq 0 ) {
		warn("Error: Failed to read udrl-vs.bin");
		return $null;
	}

	# Overwrite Beacon's ReflectiveLoader() with UDRL
	$payload = setup_reflective_loader($beacon, $ldr);


	# Output the modified payload.
	return $payload;
}
```

If we load either of the scripts above into Cobalt Strike and export a payload, we’ll see a message in the Script Console confirming that the custom loader was used. The resulting shellcode can then be used in combination with a Stage0 of your choosing.

### Closing Thoughts

That concludes the first post of this series Revisiting the UDRL. As part of this post we have created a Visual Studio project with several Quality of Life (QoL) improvements. We’re now able to develop, debug and operationalize both Stephen Fewer’s original reflective loader and the _Double Pulsar_ concept for Cobalt Strike using Visual Studio. The template developed as part of this project can be found in the Arsenal Kit under _udrl-vs_ in “kits”. In the [next installment](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking) we’ll explore some evasive techniques as well as how to modify default behaviors.

![](https://www.cobaltstrike.com/app/uploads/2023/09/Cobalt-author-photo.png)

#### [Robert Bearsby](https://www.cobaltstrike.com/profile/robert-bearsby)

Senior Cybersecurity Researcher

[View Profile](https://www.cobaltstrike.com/profile/robert-bearsby)

TOPICS


- [Development](https://www.cobaltstrike.com/blog?_sft_cornerstone=development "Development")
- [Red Team](https://www.cobaltstrike.com/blog?_sft_cornerstone=red-team "Red Team")