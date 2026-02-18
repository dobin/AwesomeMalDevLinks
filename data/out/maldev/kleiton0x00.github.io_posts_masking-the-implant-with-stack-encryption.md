# https://kleiton0x00.github.io/posts/Masking-the-Implant-with-Stack-Encryption/

[Posts](https://kleiton0x00.github.io/)Masking the Implant with Stack Encryption

Post

Cancel

# Masking the Implant with Stack Encryption

Posted May 1, 2023 _2023-05-02T00:00:00+02:00_ by  kleiton0x7e

Mirrored from [WKL Security](https://whiteknightlabs.com/2023/05/02/masking-the-implant-with-stack-encryption/)

## Introduction

This article is a demonstration of memory-based detection and evasion techniques. Whenever you build a Command & Control or you perform threat hunting, there will be scenarios when you might need to analyze the memory artifacts of a specific system—something that is really useful during your live forensics or when you’re going to perform an incident response on a host by segregating that host from the network. In such scenarios, it would be required to identify the payload that is currently running in memory. We will be taking a look at some of the examples of how that payload investigation can be performed, and how that investigation can be bypassed as well.

A lot of times during an engagement, an engineer might execute a payload: either Cobalt Strike, Havoc or any other open source C2s that are currently there. There are specific scenarios where the red teamer might want to execute a command on the endpoint, which gathers a lot of strings and sends that to your C2 host. These strings can be username, hostname, or even information related to your command and control server itself and the information might also be encrypted during transit. However, when the payload sleeps on the endpoint, and the red teamer adds sleep and jitter to the beacon, these commands need to be stored in an encrypted way. In this current scenario, this information can be either stored into a heap or on stack.

Regarding heap memory, usually we don’t have to worry about it because you can eventually walk a heap, extract information, and encrypt when you are sleeping. However, things change a bit when we talk about stack encryption.

## The problem with loaders

In a traditional shellcode loader, the shellcode is stored in stack memory since it is stored in a variable inside or outside of a function. When the shellcode is written with `WriteProcessMemory` to a local/remote process, not only is the shellcode stored in that particular memory but also it remains stored in the stack, where the variable lives.

![shellcode_living_in_stack](https://whiteknightlabs.com/wp-content/uploads/2023/04/Pasted-image-20230429021705-1024x342.png)

## Finding the stack

To quickly identify where the stack is located, we need to retrieve the RSP address. This register will contain the address of the top of the stack.

`unsigned char *rsp;
asm("movq %%rsp, %0;" : "=r" (rsp));

`

While the top of the stack is easily identifiable, the bottom is much harder as the stack dynamically increases and/or decreases in size based on the variables that are stored and freed as the code is executed. Luckily `VirtualQuery` makes it so easy for us to retrieve information about the range of pages in the virtual address space of the calling process. So using the RSP address that we found previously allows us to determine the top and the bottom of the stack:

`// Get the address range of the stack
MEMORY_BASIC_INFORMATION mbi;
VirtualQuery(rsp, &mbi, sizeof(mbi));

unsigned char *stackRegion = mbi.BaseAddress - 8192;
unsigned char *stackBase = stackRegion + mbi.RegionSize + 8192;

`

## Suspending the thread to avoid abnormal behavior

It is required to suspend the process before encrypting or decrypting the stack. This is because modifying the stack while the process is still running can cause unpredictable behavior and potential crashes.

To suspend the process, we can use the SuspendThread function from the Windows API, which suspends the execution of a thread until it is resumed with the ResumeThread function.

`hThread = CreateThread(NULL, 0, EncryptThread, rsp, 0, NULL);
ResumeThread(hThread);

DWORD WINAPI EncryptThread(LPVOID lpParameter) {
    //...mask the stack
}

`

## Encrypting what we need to hide

Encrypting from the beginning of the page to the bottom of the stack might look suspicious and is not the most OPSEC-safe approach. Instead, we will encrypt where the stack actually begins (RSP address) and the bottom of the stack (minus 8 bytes).

`int stackSize = stackBase - rsp - 8; //the part that will be encrypted

`

Below is the image of the range that should be encrypted, starting from RSP address (where the plaintext strings and the shellcode is stored) until the end of the stack:

![stack_region_between_rsp_and_base](https://whiteknightlabs.com/wp-content/uploads/2023/04/Pasted-image-20230429023047.png)

The encryption routine is pretty simple; XOR byte per byte until you reach the end of the stack:

`//mask everything between the addresses of RSP and bottom of the stack
unsigned char *p = (unsigned char *)rsp;
int n = 0;
for (int i = 0; i < stackSize; i++) {
    *(p++) ^= 0x55;
}

`

If we analyze the stack of the loader, we can clearly see what the stack will look like after the encryption:

![stack_encrypted_and_decrypted](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-01-16-02-29.png)

## There’s no sleepmask without sleeping

Some modern detection solutions possess countermeasures against a basic `Sleep()`. For example, hooking sleep functions like `Sleep` in C/C++ or `Thread.Sleep` in C# to nullify the sleep, but also fast forwarding.

There is already a nice technique that leverages CPU cycles to perform a custom sleep. I am not going to further describe how it works as it is already well-explained here in this [article](https://shubakki.github.io/posts/2022/12/detecting-and-evading-sandboxing-through-time-based-evasion/).

`unsigned long long __get_timestamp() {
	const size_t UNIX_TIME_START = 0x019DB1DED53E8000; // Start of Unix epoch in ticks.
	const size_t TICKS_PER_MILLISECOND = 10000; // A tick is 100ns.
	LARGE_INTEGER time;
	time.LowPart = *(DWORD*)(0x7FFE0000 + 0x14); // Read LowPart as unsigned long.
	time.HighPart = *(long*)(0x7FFE0000 + 0x1c); // Read High1Part as long.
	return (unsigned long long)((time.QuadPart - UNIX_TIME_START) / TICKS_PER_MILLISECOND);
}

void __alt_sleepms(size_t ms)
{
	volatile size_t x = rand(); // random buffer var
	const unsigned long long end = __get_timestamp() + ms; // calculate when we shall stop sleeping
	while (__get_timestamp() < end) { x += 1; } // increment random var by 1 till we reach our endtime
	if (__get_timestamp() - end > 2000) return; // Fast Forward check, might need some tuning
}

__alt_sleepms(5*1000); //sleep for 5 seconds

`

## Wrapping everything up

In conclusion, understanding memory-based detection and evasion techniques is crucial for effective threat hunting and incident response. Investigating the payloads that are running in memory can provide critical information about a system’s state, but it can also be bypassed through stack encryption techniques.

The code for this PoC can be found in this GitHub [repo](https://github.com/WKL-Sec/StackMask).

## Credits

[https://shubakki.github.io/posts/2022/12/detecting-and-evading-sandboxing-through-time-based-evasion/](https://shubakki.github.io/posts/2022/12/detecting-and-evading-sandboxing-through-time-based-evasion/)

This post is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) by the author.

Share

Contents

### Further Reading

[Jun 25, 2023 _2023-06-26T00:00:00+02:00_ **Navigating Stealthy WMI Lateral Movement**\\
\\
Mirrored from WKL Security Introduction In this article, we’ll look at a Python script that uses Windows Management Instrumentation (WMI) to remotely control a target computer. The script makes u...](https://kleiton0x00.github.io/posts/Navigating-Stealthy-WMI-Lateral-Movement/)

[May 22, 2023 _2023-05-23T00:00:00+02:00_ **Harnessing the Power of Cobalt Strike Profiles for EDR Evasion**\\
\\
Mirrored from WKL Security. This version is an update ahead. Introduction In this blog post, we will go through the importance of each profile’s option, and explore the differences between defaul...](https://kleiton0x00.github.io/posts/Harnessing-the-Power-of-Cobalt-Strike-Profiles-for-EDR-Evasion/)

[Feb 4, 2023 _2023-02-05T00:00:00+01:00_ **Shellcodes are dead, long live Fileless Shellcodes**\\
\\
Recently I was developing a simple Shellcode Loader which uses Callbacks as an alternative of Shellcode execution. While it bypasses every runtime scanning, it failed to bypass the signature detect...](https://kleiton0x00.github.io/posts/Shellcodes-are-dead-long-live-fileless-shellcodes/)

[Shellcodes are dead, long live Fileless Shellcodes](https://kleiton0x00.github.io/posts/Shellcodes-are-dead-long-live-fileless-shellcodes/) [Harnessing the Power of Cobalt Strike Profiles for EDR Evasion](https://kleiton0x00.github.io/posts/Harnessing-the-Power-of-Cobalt-Strike-Profiles-for-EDR-Evasion/)

#### Trending Tags

 [back-to-top](https://kleiton0x00.github.io/posts/Masking-the-Implant-with-Stack-Encryption/#)