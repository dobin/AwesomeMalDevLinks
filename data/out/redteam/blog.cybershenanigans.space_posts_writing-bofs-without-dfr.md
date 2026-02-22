# https://blog.cybershenanigans.space/posts/writing-bofs-without-dfr/

## Contents

# Writing Beacon Object Files Without DFR

[Matt Ehrnschwender](https://blog.cybershenanigans.space/whoami/ "Author")

2024-11-18 5347 words
26 minutes

Contents

## Intro

[Beacon Object Files](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_main.htm) have become very popular for red teams to add additional capabilities on the fly without needing to include the overhead of a reflective DLL or .NET assembly. This advantage comes at the cost of Beacon Object Files being a little bit awkward to develop. One development quirk is the need to prefix imported symbols with the associated library name where the symbol can be found. This concept, known as [Dynamic Function Resolution](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_dynamic-func-resolution.htm) (or DFR), is how the BOF tells the BOF loader where to find external symbols.

What if I told you that you do not need to write these DFR prototypes in your code when developing BOFs?

![/posts/writing-bofs-without-dfr/images/meme.jpg](https://blog.cybershenanigans.space/posts/writing-bofs-without-dfr/images/meme.jpg)

## TL; DR

[objcopy](https://www.man7.org/linux/man-pages/man1/objcopy.1.html) supports redefining symbol names in object files using the `--redefine-sym` or `--redefine-syms` flag. This can be used to translate imported symbols from the normal system definition to the DFR format during post-processing.

## The Need For DFR

An important thing to note about Beacon Object Files is that the resulting file a BOF loader loads is a generic [COFF](https://en.wikipedia.org/wiki/COFF) file. This may seem rather obvious to people who have written BOFs before, but it is important to note because it helps identify what exactly a BOF loader has to work with and what data it lacks.

One piece of information that a COFF contains is a [symbol table](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#coff-symbol-table). This is an array of structures listing both the symbols that the COFF defines and the external symbols that the COFF requires. Each symbol definition includes the name of the symbol as is declared in the source file itself. What the symbol table lacks is the name of the external library where the symbol can be found. The linker’s job is to take these symbols from the symbol table and search for them in a predefined set of libraries. Since BOFs do not go through a linking stage, this job is passed on to the BOF loader. Linkers will perform a brute-force style search to locate these symbols which is not the most ideal approach for a BOF loader.

This is where the DFR concept comes into play. Instead of performing this brute-force search every single time a BOF is loaded, the library names are instead integrated directly into the symbol name. The way this is done is by prefixing the symbol name with the library name and separating them with a dollar sign (`$`). For example, if a BOF requires the symbol `CreateFileA` and that symbol lives in `kernel32.dll`, the BOF would instead define the symbol `KERNEL32$CreateFileA` and the BOF loader will know to search for the `CreateFileA` symbol in `kernel32`.

## DFR Issues

This method of prepending the library name along with the symbol name works and has been the pretty standard way of defining imports in BOFs but there can be some issues with this approach.

### Mismatched Prototypes

Since an already declared symbol needs to be redeclared using the DFR format, this manual redeclaration could potentially not match the original one exactly due to a typo. For basic functions, this error may be easy to find but for more complicated functions, it can be a little bit more difficult to identify.

Some functions in the Windows API are known to include a rather large number of parameters. Take [CreateProcessWithLogonW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createprocesswithlogonw) as an example. This is what the DFR declaration would look like in order to use this function in a BOF.

|     |
| --- |
| ```c<br>DECLSPEC_IMPORT BOOL WINAPI ADVAPI32$CreateProcessWithLogonW(<br>	LPCWSTR lpUsername,<br>	LPCWSTR lpDomain,<br>	LPCWSTR lpPassword,<br>	DWORD dwLogonFlags,<br>	LPCWSTR lpApplicationName,<br>	LPWSTR lpCommandLine,<br>	DWORD dwCreationFlags,<br>	LPVOID lpEnvironment,<br>	LPCWSTR lpCurrentDirectory,<br>	LPSTARTUPINFOW lpStartupInfo,<br>	LPPROCESS_INFORMATION lpProcessInformation);<br>``` |

If a parameter is swapped, omitted, or the type is wrong in the declaration, the function may not behave how it is expected to behave. The exact issue that occurs will depend on what part of the declaration is incorrect. In some cases, the function may work during one run but fail in another one. Like with many things related to C development, it just depends on how the computer is feeling at that moment in time if it is going to work or not ¯\\\_(ツ)\_/¯.

Regardless of what error is returned when this type of issue occurs, this mistake can only be spotted by manually reviewing the code and double checking that the DFR prototype matches the original one exactly.

#### C++, the Savior

In the [“Simplifying BOF Development: Debug, Test, and Save Your B(e)acon”](https://www.cobaltstrike.com/blog/simplifying-bof-development) blog post by Fortra, [Henri Nurmi](https://x.com/HenriNurmi) mentioned using the C++11 [decltype](https://en.cppreference.com/w/cpp/language/decltype) specifier to help solve this issue.

This pattern is less error-prone since the new DFR symbol declaration is constructed directly from the original one.

The same `CreateProcessWithLogonW` prototype would look something like this using decltype.

|     |
| --- |
| ```c<br>DECLSPEC_IMPORT decltype(CreateProcessWithLogonW) ADVAPI32$CreateProcessWithLogonW;<br>``` |

The original function prototype does not need to be manually rewritten since it is provided by decltype.

The caveat here is that you need a C++ compiler to compile the BOF so it requires dealing with some C++ specific nuances like [name mangling](https://learn.microsoft.com/en-us/cpp/build/reference/decorated-names?view=msvc-170) but it does make declaring DFR prototypes a lot easier.

### Executable Generation

During the testing phases of developing a BOF, it is helpful to compile the code into an executable or integrate it into a testing framework. Adding the DFR specification to imported symbols means that they will not be resolvable by the system linker. The system linker is unaware of the DFR format and interprets the `<library>$<symbol>` value as the symbol name itself.

There are some workarounds for this.

* * *

Filename: `examplebof.c`

|     |
| --- |
| ```c<br>#include <windows.h><br>#include <lmcons.h><br>#include "beacon.h"<br>DECLSPEC_IMPORT DWORD WINAPI KERNEL32$GetCurrentProcessId(void);<br>DECLSPEC_IMPORT BOOL WINAPI ADVAPI32$GetUserNameA(LPSTR, LPDWORD);<br>void go(void) {<br>    DWORD pid = KERNEL32$GetCurrentProcessId();<br>    BeaconPrintf(CALLBACK_OUTPUT, "Current process id: %lu", pid);<br>    char username[UNLEN + 1] = {0};<br>    if (ADVAPI32$GetUserNameA(username, &(DWORD){ sizeof(username) }) == TRUE) {<br>        BeaconPrintf(CALLBACK_OUTPUT, "Username: %s", username);<br>    }<br>}<br>// Main function for building as an executable<br>int main() {<br>    go();<br>    return 0;<br>}<br>``` |

* * *

Attempting to compile this example BOF as an executable throws `undefined reference` errors when linking.

|     |
| --- |
| ```bash<br>matt@laptop :: ~/Documents/dev/writing-bofs-without-dfr-example >> x86_64-w64-mingw32-gcc -o examplebof.exe examplebof.c<br>/usr/lib/gcc/x86_64-w64-mingw32/14.1.1/../../../../x86_64-w64-mingw32/bin/ld: /tmp/ccQizFTo.o:examplebof.c:(.text+0x14): undefined reference to `__imp_KERNEL32$GetCurrentProcessId'<br>/usr/lib/gcc/x86_64-w64-mingw32/14.1.1/../../../../x86_64-w64-mingw32/bin/ld: /tmp/ccQizFTo.o:examplebof.c:(.text+0x3b): undefined reference to `__imp_BeaconPrintf'<br>/usr/lib/gcc/x86_64-w64-mingw32/14.1.1/../../../../x86_64-w64-mingw32/bin/ld: /tmp/ccQizFTo.o:examplebof.c:(.text+0x73): undefined reference to `__imp_ADVAPI32$GetUserNameA'<br>/usr/lib/gcc/x86_64-w64-mingw32/14.1.1/../../../../x86_64-w64-mingw32/bin/ld: /tmp/ccQizFTo.o:examplebof.c:(.text+0x97): undefined reference to `__imp_BeaconPrintf'<br>collect2: error: ld returned 1 exit status<br>matt@laptop :: ~/Documents/dev/writing-bofs-without-dfr-example 1 >><br>``` |

A common way of fixing this issue is by wrapping all of the DFR prototypes in an `#ifdef` macro and choosing which version of the symbol to use depending on if that macro is defined or not. The DFR symbol and the system symbol can be aliased to a common name in order to refer to the different variants based on the configuration.

* * *

Filename: `examplebof.c`

|     |
| --- |
| ```c<br>#include <windows.h><br>#include <lmcons.h><br>#include "beacon.h"<br>#ifdef BOF<br>// Use DFR if `BOF` is defined<br>DECLSPEC_IMPORT DWORD WINAPI KERNEL32$GetCurrentProcessId(void);<br>#define kernel32_GetCurrentProcessId KERNEL32$GetCurrentProcessId<br>DECLSPEC_IMPORT BOOL WINAPI ADVAPI32$GetUserNameA(LPSTR, LPDWORD);<br>#define advapi32_GetUserNameA ADVAPI32$GetUserNameA<br>#else // BOF<br>// Do not use DFR if `BOF` is not defined<br>#define kernel32_GetCurrentProcessId GetCurrentProcessId<br>#define advapi32_GetUserNameA GetUserNameA<br>#endif // BOF<br>void go(void) {<br>    DWORD pid = kernel32_GetCurrentProcessId();<br>    BeaconPrintf(CALLBACK_OUTPUT, "Current process id: %lu", pid);<br>    char username[UNLEN + 1] = {0};<br>    if (advapi32_GetUserNameA(username, &(DWORD){ sizeof(username) }) == TRUE) {<br>        BeaconPrintf(CALLBACK_OUTPUT, "Username: %s", username);<br>    }<br>}<br>#ifndef BOF<br>// Create a main function to wrap the BOF entrypoint<br>int main() {<br>    go();<br>    return 0;<br>}<br>#endif // BOF<br>``` |

* * *

Passing in the `-DBOF` flag during compilation will use the DFR import declarations and omitting that flag will use the normal system declarations. Both of the symbols are aliased with `<libname>_<symbol>` so that the correct symbol is used when referring to them.

|     |
| --- |
| ```bash<br># For compiling with the BOF DFR imports<br>x86_64-w64-mingw32-gcc -DBOF -c -o examplebof.o examplebof.c<br># For compiling the executable with the normal system imports<br>x86_64-w64-mingw32-gcc -o examplebof.exe examplebof.c<br>``` |

Compiling it with a Makefile

* * *

Filename: `Makefile`

|     |
| --- |
| ```makefile<br>CC = x86_64-w64-mingw32-gcc<br>RM = rm -vf<br>sources := examplebof.c<br>objs := $(sources:.c=.o)<br>.PHONY: all clean<br>all : examplebof.bof.o examplebof.exe<br>clean:<br>	$(RM) examplebof.bof.o examplebof.exe $(objs)<br>examplebof.o : examplebof.c beacon.h<br>examplebof.bof.o : examplebof.c beacon.h<br>%.bof.o : %.c<br>	$(CC) -DBOF $(CFLAGS) $(TARGET_ARCH) -c $(OUTPUT_OPTION) $<<br>% : %.o<br>%.exe : %.o<br>	$(LINK.o) $^ $(LDLIBS) -o $@<br>``` |

* * *

|     |
| --- |
| ```bash<br>matt@laptop :: ~/Documents/dev/writing-bofs-without-dfr-example >> make<br>x86_64-w64-mingw32-gcc -DBOF   -c -o examplebof.bof.o examplebof.c<br>x86_64-w64-mingw32-gcc    -c -o examplebof.o examplebof.c<br>x86_64-w64-mingw32-gcc   examplebof.o  -o examplebof.exe<br>/usr/lib/gcc/x86_64-w64-mingw32/14.1.1/../../../../x86_64-w64-mingw32/bin/ld: examplebof.o:examplebof.c:(.text+0x3b): undefined reference to `__imp_BeaconPrintf'<br>/usr/lib/gcc/x86_64-w64-mingw32/14.1.1/../../../../x86_64-w64-mingw32/bin/ld: examplebof.o:examplebof.c:(.text+0x97): undefined reference to `__imp_BeaconPrintf'<br>collect2: error: ld returned 1 exit status<br>make: *** [Makefile:20: examplebof.exe] Error 1<br>matt@laptop :: ~/Documents/dev/writing-bofs-without-dfr-example 2 >><br>``` |

The BOF version compiles successfully; however, the executable version still yields a few `undefined reference` linking errors.

The linker is failing to find the Beacon API (BeaconPrintf) symbols. These symbols typically reside in a BOF loader and are resolved during the loading process so they do not live anywhere on the system for the linker to find.

A workaround for this issue is to create mock implementations of the Beacon API and link them in when compiling the executable version. The provided Visual Studio BOF template mentioned in the [“Simplifying BOF Development: Debug, Test, and Save Your B(e)acon”](https://www.cobaltstrike.com/blog/simplifying-bof-development) blog post uses this strategy ( [Cobalt-Strike/bof-vs/BOF-template/base/mock.cpp#L391](https://github.com/Cobalt-Strike/bof-vs/blob/855a33afacd6efad3eaceebe42c5ece4a435d91d/BOF-Template/base/mock.cpp#L391)).

The mock Beacon API implementations can be ported over in a way that works with this BOF. Ideally, these would be implemented in a static library that can be reused across different projects but since `BeaconPrintf` is the only function needed for this project, it is fine to just include it along with the BOF.

* * *

Filename: `beacon_mock.c`

|     |
| --- |
| ```c<br>#include "beacon_mock.h"<br>#include <assert.h><br>#include <stdarg.h><br>#include <stdio.h><br>/// BeaconPrintf implementation for printing to stdout.<br>/// Based off of https://github.com/Cobalt-Strike/bof-vs/blob/855a33afacd6efad3eaceebe42c5ece4a435d91d/BOF-Template/base/mock.cpp#L391 but ported to C<br>void BeaconPrintf(int type, const char *fmt, ...) {<br>	printf("[Output Callback: (0x%02x)]: ", type);<br>	va_list args;<br>	va_start(args, fmt);<br>	vprintf(fmt, args);<br>	puts("");<br>	assert(fflush(stdout) == 0);<br>	va_end(args);<br>}<br>``` |

* * *

Filename: `beacon_mock.h`

|     |
| --- |
| ```c<br>#ifndef BEACON_MOCK_H<br>#define BEACON_MOCK_H<br>#define CALLBACK_OUTPUT      0x0<br>#define CALLBACK_OUTPUT_OEM  0x1e<br>#define CALLBACK_OUTPUT_UTF8 0x20<br>#define CALLBACK_ERROR       0x0d<br>void BeaconPrintf(int type, const char *fmt, ...);<br>#endif // BEACON_MOCK_H<br>``` |

* * *

Filename: `examplebof.c`

|     |
| --- |
| ```c<br>#include <windows.h><br>#include <lmcons.h><br>#ifdef BOF<br>// Include the regular beacon.h definitions when compiling as a BOF<br>#include "beacon.h"<br>DECLSPEC_IMPORT DWORD WINAPI KERNEL32$GetCurrentProcessId(void);<br>#define kernel32_GetCurrentProcessId KERNEL32$GetCurrentProcessId<br>DECLSPEC_IMPORT BOOL WINAPI ADVAPI32$GetUserNameA(LPSTR, LPDWORD);<br>#define advapi32_GetUserNameA ADVAPI32$GetUserNameA<br>#else // BOF<br>// Include the mock Beacon API definitions when compiling as a standalone executable<br>#include "beacon_mock.h"<br>#define kernel32_GetCurrentProcessId GetCurrentProcessId<br>#define advapi32_GetUserNameA GetUserNameA<br>#endif // BOF<br>void go(void) {<br>    DWORD pid = kernel32_GetCurrentProcessId();<br>    BeaconPrintf(CALLBACK_OUTPUT, "Current process id: %lu", pid);<br>    char username[UNLEN + 1] = {0};<br>    if (advapi32_GetUserNameA(username, &(DWORD){ sizeof(username) }) == TRUE) {<br>        BeaconPrintf(CALLBACK_OUTPUT, "Username: %s", username);<br>    }<br>}<br>#ifndef BOF<br>// Create a main function to wrap the BOF entrypoint<br>int main() {<br>    go();<br>    return 0;<br>}<br>#endif // BOF<br>``` |

* * *

And adjusting the Makefile above to include the new mock Beacon API implementations

* * *

Filename: `Makefile`

|     |
| --- |
| ```makefile<br>CC = x86_64-w64-mingw32-gcc<br>RM = rm -vf<br>sources := examplebof.c beacon_mock.c<br>objs := $(sources:.c=.o)<br>.PHONY: all clean<br>all : examplebof.bof.o examplebof.exe<br>clean:<br>	$(RM) examplebof.bof.o examplebof.exe $(objs)<br>examplebof.exe : examplebof.o beacon_mock.o<br>examplebof.bof.o : examplebof.c beacon.h<br>examplebof.o : examplebof.c beacon_mock.h<br>beacon_mock.o : beacon_mock.c beacon_mock.h<br>%.bof.o : %.c<br>	$(CC) -DBOF $(CFLAGS) $(TARGET_ARCH) -c $(OUTPUT_OPTION) $<<br>% : %.o<br>%.exe : %.o<br>	$(LINK.o) $^ $(LDLIBS) -o $@<br>``` |

* * *

Compiling this as both a BOF and a standalone executable should work now since there is an implementation for `BeaconPrintf` present that the linker can find.

|     |
| --- |
| ```bash<br>matt@laptop :: ~/Documents/dev/writing-bofs-without-dfr-example >> ls<br>beacon.h  beacon_mock.c  beacon_mock.h  examplebof.c  Makefile<br>matt@laptop :: ~/Documents/dev/writing-bofs-without-dfr-example >> make<br>x86_64-w64-mingw32-gcc -DBOF   -c -o examplebof.bof.o examplebof.c<br>x86_64-w64-mingw32-gcc    -c -o examplebof.o examplebof.c<br>x86_64-w64-mingw32-gcc    -c -o beacon_mock.o beacon_mock.c<br>x86_64-w64-mingw32-gcc   examplebof.o beacon_mock.o  -o examplebof.exe<br>matt@laptop :: ~/Documents/dev/writing-bofs-without-dfr-example >> ls<br>beacon.h  beacon_mock.c  beacon_mock.h  beacon_mock.o  examplebof.bof.o  examplebof.c  examplebof.exe  examplebof.o  Makefile<br>matt@laptop :: ~/Documents/dev/writing-bofs-without-dfr-example >> wine ./examplebof.exe<br>002c:fixme:winediag:loader_init wine-staging 9.15 is a testing version containing experimental patches.<br>002c:fixme:winediag:loader_init Please mention your exact version when filing bug reports on winehq.org.<br>[Output Callback: (0x00)]: Current process id: 32<br>[Output Callback: (0x00)]: Username: matt<br>matt@laptop :: ~/Documents/dev/writing-bofs-without-dfr-example >><br>``` |

## Symbol Redefining With Objcopy

As seen above, this method for managing DFR imports can be a little bit of a hassle. It requires various macros and other helpers in the source code causing a lot of clutter. It would be nice if there was a way to write a BOF like a normal C program but manage the DFR aspects separately outside of the source code.

This is possible using something like [objcopy](https://www.man7.org/linux/man-pages/man1/objcopy.1.html).

Objcopy is a tool from the [GNU Binutils](https://www.gnu.org/software/binutils/) designed to manipulate object files. The Binutils have been around for over two decades and are pretty common on most Linux systems. Objcopy supports various different object file formats including COFFs.

One feature that objcopy includes is the ability to rename symbols using the `--redefine-sym` flag. This allows changing the name of a symbol in an existing object file.

Here is how this can be utilized with Beacon Object Files.

The example BOF code above can be rewritten to remove all of the DFR specifics.

* * *

Filename: `examplebof.c`

|     |
| --- |
| ```c<br>#include <windows.h><br>#include <lmcons.h><br>#include "beacon.h"<br>void go(void) {<br>    DWORD pid = GetCurrentProcessId();<br>    BeaconPrintf(CALLBACK_OUTPUT, "Current process id: %lu", pid);<br>    char username[UNLEN + 1] = {0};<br>    if (GetUserNameA(username, &(DWORD){ sizeof(username) }) == TRUE) {<br>        BeaconPrintf(CALLBACK_OUTPUT, "Username: %s", username);<br>    }<br>}<br>``` |

* * *

Compiling this version of the example BOF and using it with [TrustedSec’s COFFLoader](https://github.com/trustedsec/COFFLoader) will fail.

|     |
| --- |
| ```powershell<br>PS C:\Users\User\Documents\writing-bofs-without-dfr-example> .\COFFLoader.exe go .\examplebof.bof.o<br>Got contents of COFF file<br>Running/Parsing the COFF file<br>Machine 0x8664<br>Number of sections: 7<br>TimeDateStamp : 0<br>PointerToSymbolTable : 0x2C2<br>NumberOfSymbols: 21<br>OptionalHeaderSize: 0<br>Characteristics: 4<br>...<br>Doing Relocations of section: 0<br>        VirtualAddress: 0x14<br>        SymbolTableIndex: 0x12<br>        Type: 0x4<br>        SymPtr: 0x1A<br>        SymVal: __imp_GetCurrentProcessId<br>        SectionNumber: 0x0<br>Failed to resolve symbol<br>Returning<br>Failed to run/parse the COFF file<br>PS C:\Users\User\Documents\writing-bofs-without-dfr-example><br>``` |

COFFLoader throws an error during the processing of the `__imp_GetCurrentProcessId` symbol because it is unable to parse out the library name.

Using objcopy, the imported symbols in the example BOF can be rewritten to match the DFR format. This is what the BOF loader expects to see when resolving these imported symbols.

|     |
| --- |
| ```bash<br>objcopy \<br>	--redefine-sym '__imp_GetCurrentProcessId=__imp_KERNEL32$GetCurrentProcessId' \<br>	--redefine-sym '__imp_GetUserNameA=__imp_ADVAPI32$GetUserNameA' \<br>	examplebof.bof.o examplebof-redefined.bof.o<br>``` |

[Rabin2](https://book.rada.re/tools/rabin2/intro.html) can be used to verify that the symbols were renamed properly.

* * *

File: `examplebof.bof.o`

|     |
| --- |
| ```bash<br>matt@laptop :: ~/Documents/dev/writing-bofs-without-dfr-example >> rabin2 -s examplebof.bof.o<br>[Symbols]<br>nth paddr      vaddr      bind   type size lib name                          demangled<br>――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――<br>0   0x00000000 0x00000000 LOCAL  FILE 4        .file<br>0   0x0000012c 0x00000000 GLOBAL FUNC 4        go<br>0   0x0000012c 0x00000000 LOCAL  SECT 4        .text<br>0   0x00000000 0x000000b0 LOCAL  SECT 4        .data<br>0   0x00000000 0x000000c0 LOCAL  SECT 4        .bss<br>0   0x000001dc 0x000000d0 LOCAL  SECT 4        .rdata<br>0   0x0000020c 0x00000100 LOCAL  SECT 4        .xdata<br>0   0x0000021c 0x00000110 LOCAL  SECT 4        .pdata<br>0   0x00000228 0x00000120 LOCAL  UNK  4        .rdata$zzz<br>0   ---------- ---------- NONE   UNK  4        imp.__imp_GetCurrentProcessId<br>0   ---------- ---------- NONE   UNK  4        imp.__imp_BeaconPrintf<br>0   ---------- ---------- NONE   UNK  4        imp.__imp_GetUserNameA<br>``` |

* * *

File: `examplebof-redefined.bof.o`

|     |
| --- |
| ```bash<br>matt@laptop :: ~/Documents/dev/writing-bofs-without-dfr-example >> rabin2 -s example-redefined.bof.o<br>[Symbols]<br>nth paddr      vaddr      bind   type size lib name                                   demangled<br>―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――<br>0   0x00000000 0x00000000 LOCAL  FILE 4        .file<br>0   0x0000012c 0x00000000 GLOBAL FUNC 4        go<br>0   0x0000012c 0x00000000 LOCAL  SECT 4        .text<br>0   0x00000000 0x000000b0 LOCAL  SECT 4        .data<br>0   0x00000000 0x000000c0 LOCAL  SECT 4        .bss<br>0   0x000001dc 0x000000d0 LOCAL  SECT 4        .rdata<br>0   0x0000020c 0x00000100 LOCAL  SECT 4        .xdata<br>0   0x0000021c 0x00000110 LOCAL  SECT 4        .pdata<br>0   0x00000228 0x00000120 LOCAL  UNK  4        .rdata$zzz<br>0   ---------- ---------- NONE   UNK  4        imp.__imp_KERNEL32$GetCurrentProcessId<br>0   ---------- ---------- NONE   UNK  4        imp.__imp_BeaconPrintf<br>0   ---------- ---------- NONE   UNK  4        imp.__imp_ADVAPI32$GetUserNameA<br>``` |

* * *

Testing the newly generated BOF with the redefined symbols now works with COFFLoader

|     |
| --- |
| ```powershell<br>PS C:\Users\User\Documents\writing-bofs-without-dfr-example> .\COFFLoader.exe go .\example-redefined.bof.o<br>Got contents of COFF file<br>Running/Parsing the COFF file<br>Machine 0x8664<br>Number of sections: 7<br>TimeDateStamp : 0<br>PointerToSymbolTable : 0x2C2<br>NumberOfSymbols: 21<br>OptionalHeaderSize: 0<br>Characteristics: 4<br>...<br>: Section: 0, Value: 0x0<br>        : Section: 7, Value: 0x0<br>        8: Section: 0, Value: 0x0<br>        : Section: 0, Value: 0x0<br>        : Section: 0, Value: 0x0<br>        : Section: 0, Value: 0x0<br>Back<br>Returning<br>Ran/parsed the coff<br>Outdata Below:<br>Current process id: 9028<br>Username: User<br>PS C:\Users\User\Documents\writing-bofs-without-dfr-example><br>``` |

That command line flag is the only thing needed to get this BOF working. The source can stay how it is without needing the DFR declarations.

Having to specify the import renaming on the command line every time can become difficult to manage as more imports are added. This can be simplified by storing the name mappings inside a dedicated file.

### Adding An Imports.txt

Objcopy has a `--redefine-syms` flag which allows specifying a file with the list of symbol redefinitions instead of needing to pass them on the command line each time. The format for this file is: the current symbol name, a space, and the new name for the symbol. These redefinitions can be listed multiple times in the file on separate lines.

Here is how to create an imports.txt file for the example BOF above.

* * *

Filename: `imports.txt`

|     |
| --- |
| ```txt<br>__imp_GetCurrentProcessId __imp_KERNEL32$GetCurrentProcessId<br>__imp_GetUserNameA __imp_ADVAPI32$GetUserNameA<br>``` |

* * *

Rerunning objcopy with the symbols specified in the `imports.txt` file should redefine all of the needed BOF imports.

|     |
| --- |
| ```bash<br>objcopy --redefine-syms=imports.txt example.bof.o example-redefined.bof.o<br>``` |

Checking the symbol table with rabin2 confirms that the new symbol names were applied correctly.

|     |
| --- |
| ```bash<br>matt@laptop :: ~/Documents/dev/writing-bofs-without-dfr-example >> rabin2 -s example-redefined.bof.o<br>[Symbols]<br>nth paddr      vaddr      bind   type size lib name                                   demangled<br>―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――<br>0   0x00000000 0x00000000 LOCAL  FILE 4        .file<br>0   0x0000012c 0x00000000 GLOBAL FUNC 4        go<br>0   0x0000012c 0x00000000 LOCAL  SECT 4        .text<br>0   0x00000000 0x000000b0 LOCAL  SECT 4        .data<br>0   0x00000000 0x000000c0 LOCAL  SECT 4        .bss<br>0   0x000001dc 0x000000d0 LOCAL  SECT 4        .rdata<br>0   0x0000020c 0x00000100 LOCAL  SECT 4        .xdata<br>0   0x0000021c 0x00000110 LOCAL  SECT 4        .pdata<br>0   0x00000228 0x00000120 LOCAL  UNK  4        .rdata$zzz<br>0   ---------- ---------- NONE   UNK  4        imp.__imp_KERNEL32$GetCurrentProcessId<br>0   ---------- ---------- NONE   UNK  4        imp.__imp_BeaconPrintf<br>0   ---------- ---------- NONE   UNK  4        imp.__imp_ADVAPI32$GetUserNameA<br>``` |

This provides a way of specifying the BOF imports in a separate file outside of the source code itself. The BOF can be written like any other normal C program without needing to make special BOF-specific adjustments for managing imports.

## So How Does This Work?

This will do a deep dive into what _exactly_ objcopy is doing under the hood to make this work. Objcopy is from the **GNU** Binutils, so that means it may not work well on non-free platforms \*cough cough Windows\*. LLVM has their own version of objcopy ( [llvm-objcopy](https://llvm.org/docs/CommandGuide/llvm-objcopy.html)) which does work on Windows; however, it may be nice to have a standalone tool dedicated to this. A custom tool can add a lot of flexibility or other features that cater more towards BOF development.

Before diving in, it is good to get familiar with the raw file structure of a COFF. Not just what each of the components (file header, section headers, relocations, etc.) are but also where they are located inside the raw file. Taking a hex dump of a COFF and labeling each component would look like this.

* * *

Hexdump output for `examplebof.bof.o`

|     |
| --- |
| ```txt<br>───────────────────────────────────────────────────────────────────<br>00000000: 6486 0700 0000 0000 c202 0000 1500 0000  d............... COFF File Header<br>                   ┌───────────────────────────────────────────────<br>00000010: 0000 0400│2e74 6578 7400 0000 0000 0000  .....text....... COFF Section<br>───────────────────┘                                                Headers<br>00000020: 0000 0000 b000 0000 2c01 0000 6802 0000  ........,...h...<br>00000030: 0000 0000 0600 0000 2000 5060 2e64 6174  ........ .P`.dat<br>00000040: 6100 0000 0000 0000 0000 0000 0000 0000  a...............<br>00000050: 0000 0000 0000 0000 0000 0000 0000 0000  ................<br>00000060: 4000 50c0 2e62 7373 0000 0000 0000 0000  @.P..bss........<br>00000070: 0000 0000 0000 0000 0000 0000 0000 0000  ................<br>00000080: 0000 0000 0000 0000 8000 50c0 2e72 6461  ..........P..rda<br>00000090: 7461 0000 0000 0000 0000 0000 3000 0000  ta..........0...<br>000000a0: dc01 0000 0000 0000 0000 0000 0000 0000  ................<br>000000b0: 4000 5040 2e78 6461 7461 0000 0000 0000  @.P@.xdata......<br>000000c0: 0000 0000 1000 0000 0c02 0000 0000 0000  ................<br>000000d0: 0000 0000 0000 0000 4000 3040 2e70 6461  ........@.0@.pda<br>000000e0: 7461 0000 0000 0000 0000 0000 0c00 0000  ta..............<br>000000f0: 1c02 0000 a402 0000 0000 0000 0300 0000  ................<br>00000100: 4000 3040 2f34 0000 0000 0000 0000 0000  @.0@/4..........<br>00000110: 0000 0000 4000 0000 2802 0000 0000 0000  ....@...(.......<br>                             ┌─────────────────────────────────────<br>00000120: 0000 0000 0000 0000│4000 5040 5557 4881  ........@.P@UWH. Raw data for<br>─────────────────────────────┘                                      each section<br>00000130: ec48 0100 0048 8dac 2480 0000 0048 8b05  .H...H..$....H..<br>00000140: 0000 0000 ffd0 8985 bc00 0000 8b85 bc00  ................<br>00000150: 0000 4189 c048 8d05 0000 0000 4889 c2b9  ..A..H......H...<br>00000160: 0000 0000 488b 0500 0000 00ff d048 8d55  ....H........H.U<br>00000170: b0b8 0000 0000 b920 0000 0048 89d7 f348  ....... ...H...H<br>00000180: ab48 89fa 8802 4883 c201 c745 ac01 0100  .H....H....E....<br>00000190: 0048 8d55 ac48 8d45 b048 89c1 488b 0500  .H.U.H.E.H..H...<br>000001a0: 0000 00ff d083 f801 751f 488d 45b0 4989  ........u.H.E.I.<br>000001b0: c048 8d05 1800 0000 4889 c2b9 0000 0000  .H......H.......<br>000001c0: 488b 0500 0000 00ff d090 4881 c448 0100  H.........H..H..<br>000001d0: 005f 5dc3 9090 9090 9090 9090 4375 7272  ._].........Curr<br>000001e0: 656e 7420 7072 6f63 6573 7320 6964 3a20  ent process id: <br>000001f0: 256c 7500 5573 6572 6e61 6d65 3a20 2573  %lu.Username: %s<br>00000200: 0000 0000 0000 0000 0000 0000 0111 0585  ................<br>00000210: 1103 0901 2900 0270 0150 0000 0000 0000  ....)..p.P......<br>00000220: a800 0000 0000 0000 4743 433a 2028 474e  ........GCC: (GN<br>00000230: 5529 2031 342e 312e 3120 3230 3234 3036  U) 14.1.1 202406<br>00000240: 3037 2028 4665 646f 7261 204d 696e 4757  07 (Fedora MinGW<br>00000250: 2031 342e 312e 312d 332e 6663 3430 2900   14.1.1-3.fc40).<br>                             ┌─────────────────────────────────────<br>00000260: 0000 0000 0000 0000│1400 0000 1200 0000  ................ Relocation data<br>─────────────────────────────┘<br>00000270: 0400 2c00 0000 0a00 0000 0400 3b00 0000  ..,.........;...<br>00000280: 1300 0000 0400 7300 0000 1400 0000 0400  ......s.........<br>00000290: 8800 0000 0a00 0000 0400 9700 0000 1300  ................<br>000002a0: 0000 0400 0000 0000 0400 0000 0300 0400  ................<br>000002b0: 0000 0400 0000 0300 0800 0000 0c00 0000  ................<br>              ┌────────────────────────────────────────────────────<br>000002c0: 0300│2e66 696c 6500 0000 0000 0000 feff  ...file......... Symbol Table<br>──────────────┘<br>000002d0: 0000 6701 6578 616d 706c 6562 6f66 2e63  ..g.examplebof.c<br>000002e0: 0000 0000 0000 676f 0000 0000 0000 0000  ......go........<br>000002f0: 0000 0100 2000 0201 0000 0000 0000 0000  .... ...........<br>00000300: 0000 0000 0000 0000 0000 2e74 6578 7400  ...........text.<br>00000310: 0000 0000 0000 0100 0000 0301 a800 0000  ................<br>00000320: 0600 0000 0000 0000 0000 0000 0000 2e64  ...............d<br>00000330: 6174 6100 0000 0000 0000 0200 0000 0301  ata.............<br>00000340: 0000 0000 0000 0000 0000 0000 0000 0000  ................<br>00000350: 0000 2e62 7373 0000 0000 0000 0000 0300  ...bss..........<br>00000360: 0000 0301 0000 0000 0000 0000 0000 0000  ................<br>00000370: 0000 0000 0000 2e72 6461 7461 0000 0000  .......rdata....<br>00000380: 0000 0400 0000 0301 2500 0000 0000 0000  ........%.......<br>00000390: 0000 0000 0000 0000 0000 2e78 6461 7461  ...........xdata<br>000003a0: 0000 0000 0000 0500 0000 0301 1000 0000  ................<br>000003b0: 0000 0000 0000 0000 0000 0000 0000 2e70  ...............p<br>000003c0: 6461 7461 0000 0000 0000 0600 0000 0301  data............<br>000003d0: 0c00 0000 0300 0000 0000 0000 0000 0000  ................<br>000003e0: 0000 0000 0000 0f00 0000 0000 0000 0700  ................<br>000003f0: 0000 0301 3800 0000 0000 0000 0000 0000  ....8...........<br>00000400: 0000 0000 0000 0000 0000 1a00 0000 0000  ................<br>00000410: 0000 0000 0000 0200 0000 0000 3400 0000  ............4...<br>00000420: 0000 0000 0000 0000 0200 0000 0000 4700  ..............G.<br>                                       ┌───────────────────────────<br>00000430: 0000 0000 0000 0000 0000 0200│5a00 0000  ............Z... String Table<br>───────────────────────────────────────┘<br>00000440: 2e72 6461 7461 247a 7a7a 002e 7264 6174  .rdata$zzz..rdat<br>00000450: 6124 7a7a 7a00 5f5f 696d 705f 4765 7443  a$zzz.__imp_GetC<br>00000460: 7572 7265 6e74 5072 6f63 6573 7349 6400  urrentProcessId.<br>00000470: 5f5f 696d 705f 4265 6163 6f6e 5072 696e  __imp_BeaconPrin<br>00000480: 7466 005f 5f69 6d70 5f47 6574 5573 6572  tf.__imp_GetUser<br>00000490: 4e61 6d65 4100                           NameA.<br>───────────────────────────────────────────────────────────────────<br>``` |

* * *

The important parts are the symbol table, section headers, and the string table. Conveniently, the string table is located at the end of the file.

How do these bits relate to each other? The symbol table and section headers contain string data which may reference the string table. Each structure will set aside 8 bytes in the name field for holding this string data.

The formats for the name fields are outlined in the [Section Table (Section Headers)](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#section-table-section-headers) and the [COFF Symbol Table](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#coff-symbol-table) PE format documentation.

This can be examined by looking at the entry for the `.text` section in the hex dump above.

|     |
| --- |
| ```txt<br>                                               Name (8 bytes)<br>                                                 │<br>                   ╭───────────────────┬─────────┴────┬─────╮<br>00000010:          │2e74 6578 7400 0000│0000 0000     │.text│......<br>                   ╰───────────────────╯              ╰─────╯<br>00000020: 0000 0000 b000 0000 2c01 0000 6802 0000  ........,...h...<br>00000030: 0000 0000 0600 0000 2000 5060            ........ .P`    <br>``` |

Since the name for this section can fit in the 8 bytes set aside for the name field, it is embedded inline with the section metadata.

What happens if the section name is longer than 8 bytes?

That is where the string table comes into play. Instead of the name field containing the name of the section, it will contain a forward slash (/) at the start and then an ASCII number with the index into the string table where the name of the section lies.

This occurs with the last section header in the above hex dump example.

|     |
| --- |
| ```txt<br>                The name field in this instance is "/4" meaning that the name<br>                of the section is really in the string table starting at the<br>                fourth index.<br>                                               Name (8 bytes)<br>                                                 │<br>                   ╭───────────────────┬─────────┴────┬────────╮<br>00000100:          │2f34 0000 0000 0000│0000 0000     │/4......│....<br>                   ╰───────────────────╯              ╰────────╯<br>00000110: 0000 0000 4000 0000 2802 0000 0000 0000  ....@...(.......<br>00000120: 0000 0000 0000 0000                      ........<br>``` |

And the value in the string table at that index is “.rdata$zzz”.

|     |
| --- |
| ```txt<br>        Real name of the section<br>                 │<br>00000430:        │                      5a00 0000              Z...<br>         ╭───────┴───────────────────┬─────────────┬──────────╮<br>00000440:│2e72 6461 7461 247a 7a7a 00│2e 7264 6174 │.rdata$zzz│.rdat<br>         ╰───────────────────────────╯             ╰──────────╯<br>00000450: 6124 7a7a 7a00 5f5f 696d 705f 4765 7443  a$zzz.__imp_GetC<br>00000460: 7572 7265 6e74 5072 6f63 6573 7349 6400  urrentProcessId.<br>00000470: 5f5f 696d 705f 4265 6163 6f6e 5072 696e  __imp_BeaconPrin<br>00000480: 7466 005f 5f69 6d70 5f47 6574 5573 6572  tf.__imp_GetUser<br>00000490: 4e61 6d65 4100                           NameA.<br>``` |

One important thing to note is where this index is based from in the string table. The first four bytes of the string table (0x43c – 0x43f) is the size field. This is a little-endian integer (0x5a) that contains the size of the string table including the size field itself. The data for the string table starts at 0x440 with the size of that data being the value in the size field minus the size of that field (0x5a - 4 = 0x56).

The index defined in the section header is not based from the start of the string table data but rather the start of the string table including the size field.

Symbol names follow the same pattern but with one difference. The difference is outlined in the [Symbol Name Representation](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#symbol-name-representation) PE format documentation.

Instead of the first byte of the name starting with a forward slash to signify that the name string is located in the string table, the first four bytes of the name field will be set to NULL and the next four bytes are the string table index. This index is a regular 4 byte, little-endian integer rather than an ASCII decimal number like in the section headers. The name index in the symbol table follows the same rule as the section header name where that index is based from the beginning of the string table starting at the size field instead of where the string data starts.

In the example hex dump, the last symbol in the symbol table contains a symbol name longer than 8 bytes.

|     |
| --- |
| ```txt<br>           First four bytes are all 0<br>                                   │     The symbol name is in the string<br>                                   │     table at index 0x47<br>                                   │            │<br>                                  ╭┴────────┬───┴╮<br>00000420:                         │0000 0000│4700│           ....G.<br>                                  ╰─────────┤    │<br>         ╭──────────────────────────────────╯    │<br>         │    ╭──────────────────────────────────╯<br>00000430:│0000│0000 0000 0000 0000 0200            ............<br>         ╰────╯<br>``` |

The string table

|     |
| --- |
| ```txt<br>00000430:                               5a00 0000               Z...<br>00000440: 2e72 6461 7461 247a 7a7a 002e 7264 6174   .rdata$zzz..rdat<br>00000450: 6124 7a7a 7a00 5f5f 696d 705f 4765 7443   a$zzz.__imp_GetC<br>00000460: 7572 7265 6e74 5072 6f63 6573 7349 6400   urrentProcessId.<br>00000470: 5f5f 696d 705f 4265 6163 6f6e 5072 696e   __imp_BeaconPrin<br>                 ╭────────────────────────────────╮   ┌─────────────╮<br>00000480: 7466 00│5f 5f69 6d70 5f47 6574 5573 6572│ tf│__imp_GetUser│<br>         ╭───────┘      ╭─────────┬───────────────┴┬──┘  ┌──────────┘<br>00000490:│4e61 6d65 4100│         │                │NameA│<br>         └──────────────┘         │                └─────┘<br>                                  │<br>               The name of this symbol is "__imp_GetUserNameA"<br>``` |

This shows how the string table is connected to the section headers and the symbol table. Now, on to how the symbol renaming works.

### DIY Symbol Renaming

Due to the nature of how the section headers and symbol table interact with the string table, the action of renaming a symbol is pretty straightforward.

The first thing to do is to find the symbol table entry of the symbol which needs to be renamed. The name field will either hold the symbol name as a byte string or an index into the string table depending on if the name is longer than 8 bytes. If the current symbol name and new name it needs to be renamed to are both 8 bytes in length or less, the new name can be inserted directly into the name field replacing the old value. Nothing else in the COFF needs to be modified.

It is a lot more common for symbol names to be longer than 8 bytes which requires a little bit more work. There are a few ways that a symbol can be renamed but this will go over the “naive” way and another way by directly replacing the old string with the new one in the string table.

#### The Naive Way

Remember earlier in this blog post during the section explaining the COFF file layout it was mentioned that the string table is “conveniently” located at the end of the file? The reason this is convenient is because arbitrary strings can be appended to it without needing to update other parts of the COFF!

COFF metadata will occasionally contain references to other parts of the file. Inserting or removing any data in the middle of the file will cause various components to shift around. This requires going back through the COFF to make sure any old file references are updated to account for this shift. Appending data does not cause this shift so the file references will stay valid.

To rename a symbol the naive way, the new symbol name can simply be appended to the end of the string table while updating the string table size field to account for the added string. All that is left to do is change the name field in the COFF symbol table entry to reference the newly added string. The rest of the COFF can stay as is since this method does not cause any other parts of the file to shift around. The old name string can be left where it is and it will simply exist as a couple extra bytes of unused data.

This approach may not be the most ideal when a lot of symbols need to be renamed since the old symbol names will take up space.

#### Replacing the Current String Table Entry with the New One

Another option for renaming a symbol is by replacing the current symbol name in the string table with the new name. The only difference here is that the other string table references in the section headers and symbol table will need to be adjusted to account for any shifts. If a symbol needs to be renamed with a new name 9 bytes longer than the original one, any section headers or symbol table entries that reference strings past this string will need their indexes increased by 9 due to the size change.

## Wrapping Up

The purpose of this blog post is to showcase a lesser known tool from the GNU Binutils that people may not be too familiar with. Its ability to redefine symbols inside an object file is something that can be utilized in Beacon Object File development. BOFs do not need their imports to be manually declared in DFR format inside the source code. They can be managed separately while the code focuses more on what the BOF is being developed to do. Keeping the source code more inline with how traditional C code is written allows it to better integrate with existing development tools.

Another takeaway is the concept of “decoupling” the constraints of software designed to run in atypical environments from the software itself. Keeping the software more generic makes it easier to work with when needing to test or debug it. Finding alternative ways of dealing with these constraints outside of the code, either through libraries or other tooling, means that the code can focus only on what it is being designed to do while the various environmental factors are handled elsewhere.

Using a dedicated tool for managing imported functions in Beacon Object Files is one example of how this decoupling concept can be applied.

Updated on 2024-11-18

[Development](https://blog.cybershenanigans.space/tags/development/), [Beacon-Object-Files](https://blog.cybershenanigans.space/tags/beacon-object-files/)Back \| [Home](https://blog.cybershenanigans.space/)

[Thanatos: Installation and Usage](https://blog.cybershenanigans.space/posts/thanatos-agent-usage/ "Thanatos: Installation and Usage") [Embedding Files in C/C++ Programs](https://blog.cybershenanigans.space/posts/embedding-files-in-c-cpp-programs/ "Embedding Files in C/C++ Programs")

[Back to Top](https://blog.cybershenanigans.space/posts/writing-bofs-without-dfr/# "Back to Top")[View Comments](https://blog.cybershenanigans.space/posts/writing-bofs-without-dfr/# "View Comments")