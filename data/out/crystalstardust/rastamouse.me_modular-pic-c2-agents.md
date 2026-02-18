# https://rastamouse.me/modular-pic-c2-agents/

All post-exploitation C2 agents that I'm aware of are implemented as a single rDLL or PIC blob. This means that all of their core logic such as check-in's, processing tasks, sending output, etc, are all mashed into a single executable blob. If an agent is implemented as an rDLL, then it is also mapped into memory in a predictable way (i.e. each section is written to an RVA from the PE's base address, as defined by the section headers).

[Crystal Palace](https://tradecraftgarden.org/crystalpalace.html) provides loading capabilities that are written as "Position-Independent Code Objects", aka PICOs, as an alternative to DLLs (although it supports DLLs as well). One of the benefits of PICOs over DLLs is that you have more flexibility in where they are loaded into memory. For instance, the data section of a PICO does not have to live adjacent to its executable section. And if you have multiple PICOs that interact with each other, they can all be living in completely disparate regions of memory.

This makes it possible (at least in theory) to write a C2 agent that is made up of multiple individual PICOs, rather than a singular monolithic DLL or PIC code base. Each PICO could be responsible for a single aspect of the agent's functionality; e.g. for check-in, task processing, evasion capabilities, and so on. This architecture would also allow authors to easily swap out different PICOs depending on their needs; e.g. swap an HTTP-comms PICO with an SMB one; swap out one stack spoofing implementation for another, and so on.

The intention of this post is to show how the Crystal Palace ecosystem can facilitate this design. I will demonstrate how to load multiple PICOs from a loader, how one PICO can execute code in another PICO, and how you can dynamically patch data into a PICO at link-time.

## PICOs

First - what are PICOs? [PICOs](https://tradecraftgarden.org/docs.html#picos) are a Crystal Palace convention for embedding and running COFF files. They are an abstraction above PIC with lots of conveniences restored, such as being able to use strings and constants, as well as a calling convention for Win32 APIs.

Here's an example of a simple 'hello world' PICO.

```c
#include <windows.h>

WINBASEAPI int WINAPI USER32$MessageBoxW (HWND hWnd, LPCWSTR lpText, LPCWSTR lpCaption, UINT uType);

void go() {
    USER32$MessageBoxW(NULL, L"Hello World!", L"PICO", MB_OK);
}
```

msgbox.c

These can be built as object files (COFFs) as x86 and x64 using mingw32.

```text
x86_64-w64-mingw32-gcc -DWIN_X64 -shared -masm=intel -Wall -Wno-pointer-arith -c src/msgbox.c -o bin/msgbox.x64.o
i686-w64-mingw32-gcc -DWIN_X86 -shared -masm=intel -Wall -Wno-pointer-arith -c src/msgbox.c -o bin/msgbox.x86.o
```

## Reflective Loader

This PICO can be appended to a Crystal Palace reflective loader. The loader will locate the PICO at runtime, write its data and code sections into two different regions of memory, (perform some other bits of magic), and then call its entry point.

```c
/*
 * Copyright (C) 2025 Raphael Mudge, Adversary Fan Fiction Writers Guild
 *
 * This file is part of Tradecraft Garden
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License along
 *  with this program; if not, see <https://www.gnu.org/licenses/>.
 */

/* function prototypes */
void ReflectiveLoader();

/* this is the REAL entry point to this whole mess and it needs to go first! */
__attribute__((noinline, no_reorder)) void go() {
	ReflectiveLoader();
}

/*
 * loader.h is a refactored Reflective Loader and some macros/definitions we need.
 * it has several functions intended to be used across loaders.
 */
#include "loaderdefs.h"
#include "loader.h"

/* header to run picos */
#include "picorun.h"

/*
 * implementations of findFunctionByHash and findModulebyHash by walking the
 * Export Address Table.
 */
#include "resolve_eat.h"

/* build a table of functions we need */
#define WIN32_FUNC( x ) __typeof__( x ) * x

typedef struct {
	WIN32_FUNC(LoadLibraryA);
	WIN32_FUNC(GetProcAddress);
	WIN32_FUNC(VirtualAlloc);
} WIN32FUNCS;

/*
 * Need other hashes?
 *
 * https://github.com/ihack4falafel/ROR13HashGenerator
 */
#define KERNEL32DLL_HASH	0x6A4ABC5B
#define LOADLIBRARYA_HASH	0xEC0E4E8E
#define GETPROCADDRESS_HASH	0x7C0DFCAA
#define VIRTUALALLOC_HASH	0x91AFCA54

void resolveFunctions(WIN32FUNCS * funcs) {

	char * hModule = (char *)findModuleByHash(KERNEL32DLL_HASH);

	funcs->LoadLibraryA   = (__typeof__(LoadLibraryA) *)   findFunctionByHash(hModule, LOADLIBRARYA_HASH);
	funcs->GetProcAddress = (__typeof__(GetProcAddress) *) findFunctionByHash(hModule, GETPROCADDRESS_HASH);
 	funcs->VirtualAlloc   = (__typeof__(VirtualAlloc) *)   findFunctionByHash(hModule, VIRTUALALLOC_HASH);
}

/*
 * This is the Crystal Palace convention for getting data linked with this loader.
 */
char __MSGBOXPICO__[0] __attribute__((section("msgbox_pico")));

#ifdef WIN_X86
__declspec(noinline) ULONG_PTR caller( VOID ) { return (ULONG_PTR)WIN_GET_CALLER(); }

char * getMsgBoxPICO() {
	return PTR_OFFSET(caller(), (ULONG_PTR)&__MSGBOXPICO__ + 5);
}
#else
char * getMsgBoxPICO() {
	return (char *)&__MSGBOXPICO__;
}
#endif

/* Reflective loader logic */
void ReflectiveLoader() {

	WIN32FUNCS   funcs;

	char       * pico;
	char       * dstData;
	char       * dstCode;

	/* resolve win32 functions */
	resolveFunctions(&funcs);

	/* find our PICO appended to this loader */
	pico = getMsgBoxPICO();

	/* allocate memory for the PICO */
	dstData = funcs.VirtualAlloc(NULL, PicoDataSize(pico), MEM_RESERVE|MEM_COMMIT|MEM_TOP_DOWN, PAGE_READWRITE);
	dstCode = funcs.VirtualAlloc(NULL, PicoCodeSize(pico), MEM_RESERVE|MEM_COMMIT|MEM_TOP_DOWN, PAGE_EXECUTE_READWRITE);

	/* load the PICO into destination address */
	PicoLoad((IMPORTFUNCS *)&funcs, pico, dstCode, dstData);

	/* execute the PICO */
	PicoEntryPoint(pico, dstCode) (NULL);
}
```

loader.c

I think most of this is straight-forward if you've worked with a reflective loader before. As you can probably see, the somewhat unique part to Crystal Palace is the "placeholder" to reference the PICO that will be linked.

```c
char __MSGBOXPICO__[0] __attribute__((section("msgbox_pico")));
```

The `PicoCodeSize`, `PicoLoad`, and `PicoEntryPoint` functions are provided by `picorun.h`. This code is included in the [Tradecraft Garden samples](https://tradecraftgarden.org/tradecraft.html), so I won't explain their functionality in detail here. Essentially, each embedded PICO is prepended with a small data stub that helps the loader figure out how large the PICO is, and where its code and data sections are.

## Specification Files

Crystal Palace uses [specification files](https://tradecraftgarden.org/docs.html#specfiles) to link one or more PICOs (and/or DLLs) to a loader. The following is a basic example with comments for each line.

```text
name     "Modular PICOs"
author   "Rasta Mouse"

x86:
	load "bin/loader.x86.o"			# read loader.x86.o from disk
		make pic					# turn it into PIC

		load "bin/msgbox.x86.o"		# read msgbox.x86.o from disk
			make object				# turn it into a PICO
			export					# convert PICO into raw bytes
			link "msgbox_pico"		# link PICO bytes to the __MSGBOXPICO__ section defined in the loader

		export						# export the combined loader + PICO blob

x64:
	load "bin/loader.x64.o"			# read loader.x64.o from disk
		make pic					# turn it into PIC

		load "bin/msgbox.x64.o"		# read msgbox.x64.o from disk
			make object				# turn it into a PICO
			export					# convert PICO into raw bytes
			link "msgbox_pico"		# link PICO bytes to the __MSGBOXPICO__ section defined in the loader

		export						# export the combined loader + PICO blob
```

loader.spec

## piclink

The `piclink` utility can then used to process that spec file and output the final combined PIC blob (i.e. loader + PICO).

```text
$ ./piclink ../garden/pico_demo/loader.spec x64 test.x64.bin
```

The included `run` utility (which is just a shellcode runner) should produce the message box.

![](https://rastamouse.me/content/images/2025/07/image.png)

## Multiple PICOs

Now that we have one simple PICO working, we want to add another. Not just another PICO that will be executed from the loader, but a PICO that can call this PICO...

To demonstrate this, I'm going to refactor the MessageBox PICO to accept an `lpText` parameter, pass that to the MessageBoxW API, and then return the result. That means that anything calling this PICO will need to provide the string to display.

```c
#include <windows.h>

WINBASEAPI int WINAPI USER32$MessageBoxW (HWND hWnd, LPCWSTR lpText, LPCWSTR lpCaption, UINT uType);

int go(LPCWSTR lpText) {
    return USER32$MessageBoxW(NULL, lpText, L"PICO", MB_OKCANCEL);
}
```

msgbox.c

I'll also create a header file with a type definition that we'll need in a bit.

```c
typedef int (*MessageBoxPICO)(LPCWSTR lpText);
```

msgbox.h

Now let's create a 'loop' PICO. This will just call the MessageBox PICO on a loop until the cancel button is selected. Within it, we define a function prototype that matches that of the target PICO's entry point (i.e. a single `LPCWSTR` parameter and returns `int`), just like we do when calling Win32 APIs.

```c
#include <windows.h>

/* our MessageBox PICO - where ever it is... */
DECLSPEC_IMPORT int MessageBoxPICO(LPCWSTR lpText);

void go() {

	/* keep showing the message box until cancelled */
	while (TRUE) {
		if (MessageBoxPICO(L"Hello from another PICO!") == IDCANCEL) {
			break;
		}
	}
}
```

loop.c

The loader is also updated so it can be linked to this new PICO.

```c
char __LOOPPICO__[0] __attribute__((section("loop_pico")));

...

char * getExecPICO() {
	return (char *)&__LOOPPICO__;
}

... etc ...
```

loader.c

We also need to update the `WIN32FUNCS` (in `loader.c`) with the typedef we put in `msgbox.h`. `IMPORTFUNCS` is a subset of functions in `WIN32FUNCS`. We can see that `PicoLoad` casts `WIN32FUNCS` to `IMPORTFUNCS`, which works because the first two members are the same.

```c
PicoLoad((IMPORTFUNCS *)&funcs, pico, dstCode, dstData);

...

typedef struct {
	WIN32_FUNC(LoadLibraryA);
	WIN32_FUNC(GetProcAddress);
	WIN32_FUNC(VirtualAlloc);
} WIN32FUNCS;

...

typedef struct {
	__typeof__(LoadLibraryA)   * LoadLibraryA;
	__typeof__(GetProcAddress) * GetProcAddress;
} IMPORTFUNCS;
```

One of the tasks `PicoLoad` performs is to loop over the functions in `IMPORTFUNCS` and patch their pointers into the target PICO. This is how we're going to patch the function pointer for the MessageBox PICO into the loop PICO!

To facilitate this, add a new member to `WIN32FUNCS`.

```c
#include "msgbox.h"

typedef struct {
	WIN32_FUNC(LoadLibraryA);
	WIN32_FUNC(GetProcAddress);
	MessageBoxPICO messageBoxPICO;  // <- add this here, the position is important because of the casting to IMPORTFUNCS
	WIN32_FUNC(VirtualAlloc);
} WIN32FUNCS;
```

loader.c

In the loader, we load the MessageBox PICO into memory and then set the `WIN32FUNCS` member to the entry point (i.e. go function) in the PICO's executable code section. We don't call this PICO, but proceed to loading and calling the loop PICO instead.

```c
void ReflectiveLoader() {

	WIN32FUNCS   funcs;

	char       * msgBoxPico;
	char       * msgBoxDstData;
	char       * msgBoxDstCode;

	char       * loopPico;
	char       * loopDstData;
	char       * loopDstCode;

	/* resolve win32 functions */
	resolveFunctions(&funcs);

	/* read MsgBox PICO appended to this loader */
	msgBoxPico = getMsgBoxPICO();

	/* allocate memory for MsgBox PICO */
	msgBoxDstData = funcs.VirtualAlloc(NULL, PicoDataSize(msgBoxPico), MEM_RESERVE|MEM_COMMIT|MEM_TOP_DOWN, PAGE_READWRITE);
	msgBoxDstCode = funcs.VirtualAlloc(NULL, PicoCodeSize(msgBoxPico), MEM_RESERVE|MEM_COMMIT|MEM_TOP_DOWN, PAGE_EXECUTE_READWRITE);

	/* load MsgBox PICO into memory */
	PicoLoad((IMPORTFUNCS *)&funcs, msgBoxPico, msgBoxDstCode, msgBoxDstData);

	/*
	 * but we don't execute it!
	 * instead, set messageBoxPICO
	 * pointer on WIN32FUNCS
	 */

	funcs.messageBoxPICO = (MessageBoxPICO)PicoEntryPoint(msgBoxPico, msgBoxDstCode);

	/* get the loop PICO */
	loopPico    = getLoopPICO();
	loopDstData = funcs.VirtualAlloc(NULL, PicoDataSize(loopPico), MEM_RESERVE|MEM_COMMIT|MEM_TOP_DOWN, PAGE_READWRITE);
	loopDstCode = funcs.VirtualAlloc(NULL, PicoCodeSize(loopPico), MEM_RESERVE|MEM_COMMIT|MEM_TOP_DOWN, PAGE_EXECUTE_READWRITE);

	/* now load and call the loop PICO */
	PicoLoad((IMPORTFUNCS *)&funcs, loopPico, loopDstCode, loopDstData);
	PicoEntryPoint(loopPico, loopDstCode)(NULL);
}
```

The final step is to add an entry for the loop PICO in the loader specification and use the `import` command to map the function pointer to the relevant symbol in the PICO. This is required as Crystal Palace prepends the PICO with the correct `PICO_DIRECTIVE_PATCH` data for the patching to take place.

```text
x64:
	load "bin/loader.x64.o"
		make pic

		load "bin/msgbox.x64.o"
			make object
			export
			link "msgbox_pico"

		load "bin/exec.x64.o"
			make object
			import "LoadLibraryA, GetProcAddress, MessageBoxPICO"	# patch function pointers!
			export
			link "exec_pico"

		export
```

loader.spec

💡

Note that LoadLibraryA and GetProcAddress always need to be defined first.

As before, we get our message boxes.

![](https://rastamouse.me/content/images/2025/07/image-2.png)

## Patching Data

Another cool thing you can do is patch data into a PICO via the spec file. For example, instead of hardcoding "Hello from another PICO!" we can patch in something different. This would obviously be useful for patching in C2 listener configurations and other dynamic pieces of data that an agent might need.

In the PICO, initialise a global variable that will hold the patched data.

```c
#include <windows.h>

/* our MessageBox PICO - where ever it is... */
DECLSPEC_IMPORT int MessageBoxPICO(LPCWSTR lpText);

/* initialise a global variable */
wchar_t msg[64] = { '\n' };

void go() {

	/* keep showing the message box until cancelled */
	while (TRUE) {
		if (MessageBoxPICO(msg) == IDCANCEL) {
			break;
		}
	}
}
```

💡

The data must be initialised, otherwise it ends up in the .bss section which is not supported by Crystal Palace.

Then in the spec file, add a `patch` command.

```text
load "bin/loop.x64.o"
    make object
    patch "msg" $MSG  # "msg" is the "symbol" in the code, $MSG is the input variable
    import "LoadLibraryA, GetProcAddress, MessageBoxPICO"
    export
    link "loop_pico"
```

You can then pass the data in via `piclink`:

```text
$ ./piclink ../garden/pico_demo/loader.spec x64 test.x64.bin MSG=480065006C006C006F00200057006F0072006C006400
```

Strings are a little awkward because you have to provide them as hex, but we can see it working 😄

![](https://rastamouse.me/content/images/2025/07/image-3.png)

## Conclusion

I have demonstrated how multiple PICOs can be loaded into memory by a reflective loader; configured to accept parameters and return data; and how to dynamically patch data into them at link-time. I hope you can visualise how such an architecture can be extended to build a modular C2 agent.

The [tradecraft garden](https://tradecraftgarden.org/tradecraft.html) provides lots of interesting code samples that could form the foundation for adding evasion PICOs. For example, the [Stack Cutting](https://tradecraftgarden.org/stackcutting.html) sample shows how a 'hooking' PICO could hook arbitrary APIs executed by other PICOs, and then push those API calls through a 'proxy' PICO to perform call stack spoofing. Additionally, a 'mask' PICO could be used to mask and unmask memory of all your PICOs when the agent is asleep.

My interest in this architecture is to challenge assumptions about how a post-ex C2 agent might look in memory.

I hope this also gives you malware authors and defenders food for thought 😀