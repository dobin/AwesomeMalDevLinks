# https://github.com/whokilleddb/funcshenanigans

[Skip to content](https://github.com/whokilleddb/funcshenanigans#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/whokilleddb/funcshenanigans) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/whokilleddb/funcshenanigans) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/whokilleddb/funcshenanigans) to refresh your session.Dismiss alert

{{ message }}

[whokilleddb](https://github.com/whokilleddb)/ **[funcshenanigans](https://github.com/whokilleddb/funcshenanigans)** Public

- [Notifications](https://github.com/login?return_to=%2Fwhokilleddb%2Ffuncshenanigans) You must be signed in to change notification settings
- [Fork\\
3](https://github.com/login?return_to=%2Fwhokilleddb%2Ffuncshenanigans)
- [Star\\
37](https://github.com/login?return_to=%2Fwhokilleddb%2Ffuncshenanigans)


A bunch of shenanigans using functions, VEH and more


[37\\
stars](https://github.com/whokilleddb/funcshenanigans/stargazers) [3\\
forks](https://github.com/whokilleddb/funcshenanigans/forks) [Branches](https://github.com/whokilleddb/funcshenanigans/branches) [Tags](https://github.com/whokilleddb/funcshenanigans/tags) [Activity](https://github.com/whokilleddb/funcshenanigans/activity)

[Star](https://github.com/login?return_to=%2Fwhokilleddb%2Ffuncshenanigans)

[Notifications](https://github.com/login?return_to=%2Fwhokilleddb%2Ffuncshenanigans) You must be signed in to change notification settings

# whokilleddb/funcshenanigans

main

[**1** Branch](https://github.com/whokilleddb/funcshenanigans/branches) [**0** Tags](https://github.com/whokilleddb/funcshenanigans/tags)

[Go to Branches page](https://github.com/whokilleddb/funcshenanigans/branches)[Go to Tags page](https://github.com/whokilleddb/funcshenanigans/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>![author](https://github.githubassets.com/images/gravatars/gravatar-user-420.png?size=40)<br>DB<br>[spellcheck](https://github.com/whokilleddb/funcshenanigans/commit/72b98f04b8aeb3158010a8a8231d06ce82c3127c)<br>8 months agoJun 8, 2025<br>[72b98f0](https://github.com/whokilleddb/funcshenanigans/commit/72b98f04b8aeb3158010a8a8231d06ce82c3127c) · 8 months agoJun 8, 2025<br>## History<br>[6 Commits](https://github.com/whokilleddb/funcshenanigans/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/whokilleddb/funcshenanigans/commits/main/) 6 Commits |
| [imgs](https://github.com/whokilleddb/funcshenanigans/tree/main/imgs "imgs") | [imgs](https://github.com/whokilleddb/funcshenanigans/tree/main/imgs "imgs") | [Updated README.md](https://github.com/whokilleddb/funcshenanigans/commit/477a1dd3fd0e566e6e0b5593e7d803408d1180aa "Updated README.md") | 8 months agoJun 8, 2025 |
| [includes](https://github.com/whokilleddb/funcshenanigans/tree/main/includes "includes") | [includes](https://github.com/whokilleddb/funcshenanigans/tree/main/includes "includes") | [Updated README](https://github.com/whokilleddb/funcshenanigans/commit/f2bbe76de700d0c64beb3a57358c8cad7419a24a "Updated README") | 8 months agoJun 8, 2025 |
| [src](https://github.com/whokilleddb/funcshenanigans/tree/main/src "src") | [src](https://github.com/whokilleddb/funcshenanigans/tree/main/src "src") | [spellcheck](https://github.com/whokilleddb/funcshenanigans/commit/72b98f04b8aeb3158010a8a8231d06ce82c3127c "spellcheck") | 8 months agoJun 8, 2025 |
| [.gitignore](https://github.com/whokilleddb/funcshenanigans/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/whokilleddb/funcshenanigans/blob/main/.gitignore ".gitignore") | [Updated README](https://github.com/whokilleddb/funcshenanigans/commit/f2bbe76de700d0c64beb3a57358c8cad7419a24a "Updated README") | 8 months agoJun 8, 2025 |
| [Makefile](https://github.com/whokilleddb/funcshenanigans/blob/main/Makefile "Makefile") | [Makefile](https://github.com/whokilleddb/funcshenanigans/blob/main/Makefile "Makefile") | [Function Fluctuation](https://github.com/whokilleddb/funcshenanigans/commit/12aa29ab94cbc0803f2e83c0ae1b528ec4c36650 "Function Fluctuation") | 8 months agoJun 8, 2025 |
| [README.md](https://github.com/whokilleddb/funcshenanigans/blob/main/README.md "README.md") | [README.md](https://github.com/whokilleddb/funcshenanigans/blob/main/README.md "README.md") | [spellcheck](https://github.com/whokilleddb/funcshenanigans/commit/72b98f04b8aeb3158010a8a8231d06ce82c3127c "spellcheck") | 8 months agoJun 8, 2025 |
| View all files |

## Repository files navigation

# FuncShenanigans

[Permalink: FuncShenanigans](https://github.com/whokilleddb/funcshenanigans#funcshenanigans)

This research was inspired by the [Shellcode Fluctuation](https://github.com/mgeeky/ShellcodeFluctuation) technique along with [this blog about a self mutating program](https://ephemeral.cx/2013/12/writing-a-self-mutating-x86_64-c-program/). So far we have seen the fluctuation technique be used for things like Shellcode and entire PEs, but I wanted to try and use this technique for something simpler - fluctuating just one function.

The goal was to experiment with function bounds, memory protection and VEHs. This repository documents the results of such experiments in a very rough way, documenting the techniques as we go.

## Pre-requisites

[Permalink: Pre-requisites](https://github.com/whokilleddb/funcshenanigans#pre-requisites)

- Mingw Compiler
- Make

Note that all the C code discussed here is very Mingw specific, but I am sure there is a way to make this work with MSVC compiler as well.

## Bounding functions

[Permalink: Bounding functions](https://github.com/whokilleddb/funcshenanigans#bounding-functions)

Looking at `bound.c` you will see that it contains the following functions:

```
__attribute__((aligned(FUNC_SIZE)))
VOID fluctuate() {
	for (int i = 0; i < 5; i++) {
		SYSTEMTIME st = { 0 };
		GetLocalTime(&st);
		printf("\tCurrent Time: %02d:%02d:%02d\n", st.wHour, st.wMinute, st.wSecond);
		Sleep(1000);
	}
  printf("\n");
}

// Boundary function to mark the end bound of the function to fluctuate
__attribute__((aligned(FUNC_SIZE)))
void __boundary_func() {}
```

There are two functions here: `fluctuate()` and `__boundary_func()`:

- `fluctuate()` contains the actual code which we want to _fluctuate_ (or experiment with)
- `__boundary_func()` is an empty function which marks the "end" of the `fluctuate()` function. We use this function address to mark the beginning of the next _page_ in memory (more on this later).

Now the next thing, both functions have the `__attribute__((aligned(FUNC_SIZE)))` where `FUNC_SIZE` is set to 4096 which is the size of one page of memory on Windows (page size on Windows is 4KB = 4\*1024 bytes). Having the consecutive functions aligned to 4096 bytes ensures that the `fluctuate()` function occupies the whole page as the next `__boundary_func()` needs to be aligned to 4096 bytes as well, ensuring that it starts at the very next page of memory.

This arrangement is required for this technique to work - that our functions are confided to a single page (it can be more than one page - but this is a simple PoC so we are not going to dip into that can of worms).

Therefore, after compilation, the code should look something like:

```
+++++++++++++++++++++++ Page start
|                     |
|     fluctuate()     | < One page of memory >
|                     |
+++++++++++++++++++++++ End of function
|                     |
|     Garbage Data    |
|                     |
+++++++++++++++++++++++ Next page start
|                     |
|  __boundary_func()  |
|                     |
+++++++++++++++++++++++
```

We need the `fluctuate()` function to occupy one page of memory because when we change the memory permissions of a region of memory, we change the memory permissions of the page as a whole. Having other data or functions in that memory region might cause unexpected behaviour.

We can also make sure that the `fluctuate()` function starts at the beginning of a new page by using `VirtualQuery()` (see `get_mem_base_address()` function in `common.c`).

We can also verify this setup in windbg as:

[![](https://github.com/whokilleddb/funcshenanigans/raw/main/imgs/align.png)](https://github.com/whokilleddb/funcshenanigans/blob/main/imgs/align.png)

We see that after the code for the `fluctuate()` function ends, the page is filled with a nop sled till the beginning of the next page who's start is marked by the address of the `__boundary_func()`, showing that our code works as intended.

## Experiment 1: Replacing functionality

[Permalink: Experiment 1: Replacing functionality](https://github.com/whokilleddb/funcshenanigans#experiment-1-replacing-functionality)

> See: `replace.c`

My first thought with this, inspired from [this blog about a self mutating program](https://ephemeral.cx/2013/12/writing-a-self-mutating-x86_64-c-program/) was: "What if I replace the functionality of the code?"

My initial idea was to have a benign function, but then use some VEH magic to replace it's functionality at runtime to run malicious code. And that's what I did!

Let's look at the main function:

```
int main() {
	printf("[+] Function Addr: \t\t0x%p\n", fluctuate);
	printf("[+] End Bound:     \t\t0x%p\n\n", __boundary_func);

    get_mem_base_address((LPVOID)fluctuate);

	// Register VEH
	PVOID p_veh_h = AddVectoredExceptionHandler(1, (PVECTORED_EXCEPTION_HANDLER)replacer_veh);
	if (p_veh_h == NULL) {
		printf("[-] AddVectoredExceptionHandler() failed\n");
		return -1;
	}
	printf("\n[+] Registered VEH\n");

	printf("[+] Calling function without fluctuation:\n\n");
	fluctuate();

    // Convert Page into RW
    DWORD oldp = 0;

    do {
        printf("[+] Pre-shenanigans function hexdump(first 16 bytes):\n\n");
        hexdump(fluctuate, FUNC_SIZE/256);
        printf("\n");

        // Change Page to RW
        if (!VirtualProtect((LPVOID)fluctuate, FUNC_SIZE, PAGE_READWRITE, &oldp)) {
            eprint("VirtualProtect");
            break;
        }

        // XOR it
        byte_xor((unsigned char *)fluctuate, FUNC_SIZE, XOR_BYTE);

        printf("[+] Post encryption function hexdump(first 16 bytes):\n\n");
        hexdump(fluctuate, FUNC_SIZE/256);
        printf("\n");

        // Change permission to NO_ACCESS
        if (!VirtualProtect((LPVOID)fluctuate, FUNC_SIZE, PAGE_NOACCESS, &oldp)) {
            eprint("VirtualProtect");
            break;
        }

        fluctuate();
        printf("---------------------------------------------------------------------------\n");

    } while(FALSE);


	if (p_veh_h) RemoveVectoredExceptionHandler(p_veh_h);
	return 0;
}
```

The first interesting thing to note here is that we register a VEH called `replacer_veh`. We will get to that later. Next up, inside the `do-while` loop, we first print the first 16 bytes of the `fluctuate` function just so that we can compare our results later.

Next, we use `VirtualProtect()` to change the page permissions of `fluctuate` to RW and use a single byte XOR encryption to encrypt the memory of the function (pardon my use of single byte XOR - I am lazy).

Once the memory region is encrypted, we again print the first 16 bytes to demonstrate that the XOR was successful. Finally, we change the page permission to `PAGE_NOACCESS` to prevent any sort of R/W operations at all. So, now the page not only lacks RX permissions, it is also full of garbage code.

Finally, we call the `fluctuate()` function again. Since we have the function's page set to RW, an exception is triggered and out VEH aka `replacer_veh()` is called. Let's look at the VEH code:

```
LONG WINAPI replacer_veh(PEXCEPTION_POINTERS pExceptionInfo) {
	PVOID p_exec_addr = pExceptionInfo->ExceptionRecord->ExceptionAddress;

  	// Check if Exception if within our boundary
    if ((p_exec_addr > (PVOID)__boundary_func) || (p_exec_addr < (PVOID)fluctuate)) {
        printf("[-] Unhandled Exception Occured at: 0x%p\n", p_exec_addr);
        return EXCEPTION_CONTINUE_SEARCH;
    }

	if (pExceptionInfo->ExceptionRecord->ExceptionCode != EXCEPTION_ACCESS_VIOLATION) {
		printf("[+] Invalid Exception code found: 0x%lx\n", pExceptionInfo->ExceptionRecord->ExceptionCode);
		return EXCEPTION_CONTINUE_SEARCH;
	}
    printf("[-] Exception Code: 0x%lx\n", pExceptionInfo->ExceptionRecord->ExceptionCode);

    // Change function permission to RW
    DWORD oldp = 0;
    if (!VirtualProtect((LPVOID)fluctuate, FUNC_SIZE, PAGE_READWRITE, &oldp)) {
        eprint("VirtualProtect");
        return EXCEPTION_CONTINUE_SEARCH;
    }

    unsigned char shellcode[] = {
        <hello world shellcode>
    };

    // Write payload to function
    SIZE_T b_written = 0;
    if (!WriteProcessMemory((HANDLE)-1, (LPVOID)fluctuate, shellcode, sizeof(shellcode), &b_written)) {
        eprint("WriteProcessMemory");
        return EXCEPTION_CONTINUE_SEARCH;
    }
    printf("[+] Replaced function with shellcode!\n");

    if (!VirtualProtect((LPVOID)fluctuate, FUNC_SIZE, PAGE_EXECUTE_READ, &oldp)) {
        eprint("VirtualProtect");
        return EXCEPTION_CONTINUE_SEARCH;
    }
    printf("[+] Continuing function call as normal:\n\n");

	return EXCEPTION_CONTINUE_EXECUTION;
}
```

Its a very easy to understand function. First, when an exception is occurred, we check if it originates from the page containing the `fluctuate()` function and is of the type `EXCEPTION_ACCESS_VIOLATION` . If not, we return a `EXCEPTION_CONTINUE_SEARCH`.

However, if these conditions are satisfied, we proceed to use `VirtualProtect()` to make it writeable and use `WriteProcessMemory` to overwrite the function code with our shellcode. Finally, we mark the page as executable and return the flow of execution back to the program with `EXCEPTION_CONTINUE_EXECUTION`.

So just to put it everything together:

- We register a VEH to handle the exception we would throw in the future
- We make the page containing the code of `fluctuate()` as RW, encrypt it and then again change the memory permissions to `PAGE_NOACCESS`
- Calling `fluctuate()` now causes an access `ACCESS VIOLATION` exception
- Our VEH verifies the exception was raise within the page bounds and is of the right type
- It then marks the page as RW, writes our shellcode to it, marks the page as executable, and continues execution like nothing happened
- Profit!

With everything put together, it should look something like this:

[![](https://github.com/whokilleddb/funcshenanigans/raw/main/imgs/replace.png)](https://github.com/whokilleddb/funcshenanigans/blob/main/imgs/replace.png)

A couple of things to note here:

- You _technically_ dont need to encrypt the memory for this to work, but it helps with the PoC and would be more relevant later
- Any code placed after the second/tampered `fluctuate()` code is never guaranteed to work
- You can also fetch the shellcode remotely at runtime to be more evasive

However, this experiment was not novel. We also dont get to actually use the functionality exposed by `fluctuate()` for that matter, which brings us to the next experiment. With the knowledge about page boundaries and some more, we can move onto the next experiment where we actually _fluctuate_ the function.

## Experiment 2: Actually Fluctuating It

[Permalink: Experiment 2: Actually Fluctuating It](https://github.com/whokilleddb/funcshenanigans#experiment-2-actually-fluctuating-it)

> See: `fluctuator.c`

This time, we want to _fluctuate_ our function for real, so that it is encrypted in memory until it is called, and goes back to being encrypted when it's done. For that, first lets take a look at the main function and some globals:

```
// Globals
HANDLE g_htimer_queue = NULL;
HANDLE g_htimer = NULL;

int main() {
	printf("[+] Function Addr: \t\t0x%p\n", fluctuate);
	printf("[+] End Bound:     \t\t0x%p\n\n", __boundary_func);

    get_mem_base_address((LPVOID)fluctuate);

    // Register VEH
	PVOID p_veh_h = AddVectoredExceptionHandler(1, (PVECTORED_EXCEPTION_HANDLER)fluctuator_veh);
	if (p_veh_h == NULL) {
		printf("[-] AddVectoredExceptionHandler() failed\n");
		return -1;
	}
	printf("\n[+] Registered VEH\n");

    do {
        printf("[+] Calling function without fluctuation:\n\n");

        fluctuate();

        // Create Timer queue
        if (!g_htimer_queue) {
            g_htimer_queue = CreateTimerQueue();
            if (g_htimer_queue == NULL) {
                eprint("CreateTimerQueue");
                break;
            }
        }

        if (!CreateTimerQueueTimer(&g_htimer, g_htimer_queue, (WAITORTIMERCALLBACK)encryptor_wrapper, NULL, 0, 0x00, 0x00)) {
            eprint("CreateTimerQueue");
            break;
        }

        printf("[+] Created Timer to encrypt function\n");

        // Make sure function is encrypted
        Sleep(FLUCT_DURATION);

        printf("[+] Calling fluctuating function:\n\n");

        fluctuate();
        printf("[============================== END ==============================]\n");

    } while(FALSE);

    if (p_veh_h) RemoveVectoredExceptionHandler(p_veh_h);

    return 0;
}
```

Just like before, the first interesting thing we do is register a VEH `fluctuator_veh` which we will talk about later. The next interesting part of the code is:

```
g_htimer_queue = CreateTimerQueue();
CreateTimerQueueTimer(&g_htimer, g_htimer_queue, (WAITORTIMERCALLBACK)fluctuator, NULL, 0, 0x00, 0x00);
```

We create a a queue for timers using [`CreateTimerQueue()`](https://learn.microsoft.com/en-us/windows/win32/api/threadpoollegacyapiset/nf-threadpoollegacyapiset-createtimerqueue) and then add a timer to it using [`CreateTimerQueueTimer()`](https://learn.microsoft.com/en-us/windows/win32/api/threadpoollegacyapiset/nf-threadpoollegacyapiset-createtimerqueuetimer). Essentially what we are doing here is creating a timer which would execute the `encryptor_wrapper()` function after 0 milliseconds.

We then sleep for `FLUCT_DURATION`(which has been set to 1s=1000 milliseconds in our case) to make sure that the `encryptor_wrapper()` has done its jobs and the we call the `fluctuate()` function again.

Now, before we take a look at the rest of the functions, we first take a look at the `protect()` function:

```
void protect(BOOL encrypt) {
    DWORD oldp = 0;
    if (!VirtualProtect((LPVOID)fluctuate, FUNC_SIZE, PAGE_READWRITE, &oldp)) {
        eprint("VirtualProtect");
        ExitProcess(0);
    }

    byte_xor((unsigned char *)fluctuate, FUNC_SIZE, XORKEY);

    if (!VirtualProtect((LPVOID)fluctuate, FUNC_SIZE, encrypt==TRUE? PAGE_NOACCESS:PAGE_EXECUTE_READ, &oldp)) {
        eprint("VirtualProtect");
        ExitProcess(0);
    }
}
```

This simple function takes one parameter, `encrypt` which dictates whether the function would encrypt the target memory or decrypt it. Either ways, the function first marks the page containing the `fluctuate()` as writeable, xor the bytes of the memory (since XOR is symmetric, we need to do this irrespective of encryption or decryption. In an ideal world, stronger encryption/decryption methods would be used and handled separately). Finally, we call `VirtualProtect()` one last time, and if the `encrypt` flag is set to true, we change the memory permissions to `PAGE_NOACCESS` else we mark the page as RX to allow code execution.

Now coming to the `encryptor_wrapper()` function. It is just a wrapper function which calls `protect()` with `encrypt` set to `TRUE`:

```
VOID CALLBACK encryptor_wrapper(IN PVOID lpParameter, IN BOOLEAN TimerOrWaitFired) {
    protect(TRUE);
}
```

So, when we set the timer to call this function, it essentially encrypts the function and changes the page memory protection to `PAGE_NOACCESS`. Therefore when we call the `fluctuate()` function after, it causes an `ACCESS VIOLATION` and our VEH is called into action. Time to look into `fluctuator_veh()` function:

```
LONG WINAPI fluctuator_veh(PEXCEPTION_POINTERS pExceptionInfo) {
    // Check if Exception if within our boundary
    PVOID p_exec_addr = pExceptionInfo->ExceptionRecord->ExceptionAddress;

    if ((p_exec_addr > (PVOID)__boundary_func) || (p_exec_addr < (PVOID)fluctuate)) {
        printf("[-] Unhandled Exception occurred at: 0x%p as 0x%lx\n", p_exec_addr, pExceptionInfo->ExceptionRecord->ExceptionCode);
        ExitProcess(0);
        return EXCEPTION_CONTINUE_SEARCH;
	}

	if (pExceptionInfo->ExceptionRecord->ExceptionCode != EXCEPTION_ACCESS_VIOLATION) {
		printf("[-] Invalid Exception code found: 0x%lx\n", pExceptionInfo->ExceptionRecord->ExceptionCode);
		return EXCEPTION_CONTINUE_SEARCH;
	}

    if ((g_htimer == NULL)  || (g_htimer_queue == NULL)) {
        printf("[-] Globals aren't initialized\n");
        ExitProcess(0);
    }

    Sleep(2000);

    // Decrypt the function
    protect(FALSE);

    if (!CreateTimerQueueTimer(&g_htimer, g_htimer_queue, (WAITORTIMERCALLBACK)encryptor_wrapper, NULL, FLUCT_DURATION, 0x00, 0x00)) {
        eprint("CreateTimerQueue");
        ExitProcess(0);
    }

    return EXCEPTION_CONTINUE_EXECUTION;
}
```

The VEH does the usual checks about the origin of the exception and the code, just like before, and if all checks pass, we proceed. We make sure that the globals are properly initialized and then sleep for 2s to delay execution while the function remains encrypted. We then call the `protect()` function again, but this time `encrypt` set to `FALSE`. This decrypts the function and marks the function as RX making it suitable for execution.

Before passing the execution to the function again, we call `CreateTimerQueueTimer()` again to set a timer which again calls the `encryptor_wrapper` function but this time after a delay of `FLUCT_DURATION` milliseconds. Once the timer is registered, we pass the program flow back to the `fluctuate()` function. With the timer registered, it means that `fluctuate()` only has a time period of `FLUCT_DURATION` milliseconds before it is encrypted again and marked as `PAGE_NOACCESS`, therefore continuing the cycle.

Therefore, if our calculations are correct, the intervals in the `fluctuate()` function should go from 1s to roughly 3s (2s of sleep and the original 1s). Compiling and running our code gives us the following output:

[![](https://github.com/whokilleddb/funcshenanigans/raw/main/imgs/fluctuate.png)](https://github.com/whokilleddb/funcshenanigans/blob/main/imgs/fluctuate.png)

We can clearly see that the time difference went up by 3s (ignore the first one). Note that during for 2 out of those 3s, the function remains encrypted and any memory scanners wont be picking up on it. Also, any functions called after `fluctuate()` will be called normally and while `fluctuate()` can stay encrypted in memory with `PAGE_NOACCESS` unless it is accessed again.

## Conclusion

[Permalink: Conclusion](https://github.com/whokilleddb/funcshenanigans#conclusion)

Even though _fluctation_ as a concept isnt new, this technique can be a good-to-have tool in your arsenal. You can even create code caves and switch out the function with valid benign instructions when the function is not in use(something worth looking into: like [enclaves](https://learn.microsoft.com/en-us/windows/win32/trusted-execution/enclaves)?). Either ways, this was a fun PoC to experiment with.

For comments/discussions feel free to reach out to me at [@whokilleddb](https://x.com/whokilleddb) or open PRs!

Happy Hacking.

Praise the sun!

[![](https://camo.githubusercontent.com/bb0bb284fcc6700c78ff0af794be0eb999250924139f4c5c0e93898d27e1e748/68747470733a2f2f692e7974696d672e636f6d2f76692f7637704163422d4d585f632f6d617872657364656661756c742e6a7067)](https://camo.githubusercontent.com/bb0bb284fcc6700c78ff0af794be0eb999250924139f4c5c0e93898d27e1e748/68747470733a2f2f692e7974696d672e636f6d2f76692f7637704163422d4d585f632f6d617872657364656661756c742e6a7067)

## About

A bunch of shenanigans using functions, VEH and more


### Resources

[Readme](https://github.com/whokilleddb/funcshenanigans#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/whokilleddb/funcshenanigans).

[Activity](https://github.com/whokilleddb/funcshenanigans/activity)

### Stars

[**37**\\
stars](https://github.com/whokilleddb/funcshenanigans/stargazers)

### Watchers

[**0**\\
watching](https://github.com/whokilleddb/funcshenanigans/watchers)

### Forks

[**3**\\
forks](https://github.com/whokilleddb/funcshenanigans/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fwhokilleddb%2Ffuncshenanigans&report=whokilleddb+%28user%29)

## [Releases](https://github.com/whokilleddb/funcshenanigans/releases)

No releases published

## [Packages\  0](https://github.com/users/whokilleddb/packages?repo_name=funcshenanigans)

No packages published

## Languages

- [C98.2%](https://github.com/whokilleddb/funcshenanigans/search?l=c)
- [Makefile1.8%](https://github.com/whokilleddb/funcshenanigans/search?l=makefile)

You can’t perform that action at this time.