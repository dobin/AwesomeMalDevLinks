# https://redops.at/en/blog/the-emulators-gambit-executing-code-from-non-executable-memory

[Previous](https://redops.at/en/knowledge-base)

# The Emulator's Gambit: Executing Code from Non-Executable Memory

When experimenting with virtual memory in Windows, I asked myself: Is there a way to execute shellcode from a PE section like `.data`—which is readable and writable (RW) by default—without calling `VirtualProtect()` to change the memory protection from RW to RX, for example?

This question might sound unusual. After all, why would we want to execute code from a non-executable section? The answer lies in evasion: I was curious to research whether it's possible to execute shellcode without changing memory protection at all—neither through `VirtualProtect()` nor any other function that modifies page permissions. In this blog post, I'll demonstrate how this is possible through a combination of three interesting Windows mechanisms: Hardware Breakpoints (HWBPs), Vectored Exception Handling (VEH), and Instruction Emulation.

### Disclaimer

The purpose of this article is purely academic; the information shared here is for research purposes only and should under no circumstances be used for unethical or illegal activities. I do not claim accuracy or completeness. Just to be clear, I’m not claiming this as a DEP/NX bypass. It’s simply a fun research and learning project that I documented for myself and shared on my homepage — nothing more and nothing less.

Also, to be clear, I’m not claiming to be a programmer or reverse engineer. Most of the code was written or generated with Claude AI — I don’t have the skills to create it entirely from scratch. I’m just learning in small, gradual steps and focusing on understanding what the code is doing.

- [Windows Internals](https://redops.at/en/knowledge-base?filter=Windows%20Internals)
- [EDR-Evasion](https://redops.at/en/knowledge-base?filter=EDR-Evasion)
- [Malware Development](https://redops.at/en/knowledge-base?filter=Malware%20Development)
- [Debugging](https://redops.at/en/knowledge-base?filter=Debugging)

### Introduction

The **Portable Executable (PE)** format in Windows typically includes several default sections: the **.text** section (executable code, RX), the **.data** section (initialized data, RW), the **.rdata** section (read-only data, R), among others. Each section is associated with specific memory protection flags that define whether code within that section can be executed. (Image source: corkami, pe101.svg, [GitHub](https://github.com/corkami/pics/blob/master/binary/pe101/pe101.svg))

![](https://redops.at/assets/images/blog/pe_sections.png)

When executing shellcode through a loader, one option is to embed the shellcode directly into an executable section such as `.text` (RX), allowing it to run without any modification. Alternatively, the shellcode can be placed in a non-executable section like `.data` (RW), which is useful, for example, when using encrypted shellcode that needs to be decrypted in place before execution. In this scenario, the memory protection must first be changed to allow execution—typically by calling the Win32 API `VirtualProtect()` or its native counterpart `NtProtectVirtualMemory()`—before the shellcode can be run.

If we attempt to execute code from a non-executable section without changing its protection, we encounter an access violation. This is due to [Data Execution Prevention](https://learn.microsoft.com/en-us/windows/win32/memory/data-execution-prevention) (DEP), a security feature in modern Windows OS that prevents code execution from non-executable memory locations. DEP is enforced at the hardware level through the [No-eXecute](https://en.wikipedia.org/wiki/NX_bit) (NX) bit on AMD processors or the Execute-Disable (XD) bit on Intel processors.

The traditional solution—calling `VirtualProtect()` to change memory from RW to RX—is straightforward but has a critical weakness: these API calls are heavily monitored by EDRs and endpoint protection systems. Memory protection changes, especially to RWX or from RW to RX in suspicious contexts, are strong indicators of malicious activity.

**This raises an interesting question:** Can we execute shellcode from non-executable memory without ever calling `VirtualProtect()` or any other memory protection API?

The answer is yes, but it depends on which layer you're operating at. At the memory management layer where DEP/NX enforces protection, the answer is no—you cannot execute from non-executable pages. But at the CPU microarchitecture layer where hardware debug features operate, the answer changes. In this blog post, we'll explore an approach that works at the CPU level, before DEP/NX checks occur. By combining Hardware Breakpoints (HWBPs), Vectored Exception Handling (VEH), and instruction emulation, we can execute code (or more precise emulate data) from RW memory without modifying any memory permissions.

This post is organized into practical demonstrations supported by theoretical foundations. All code for this blog post can be [**downloaded from my GitHub**](https://github.com/VirtualAlllocEx/HWBP-DEP-Bypass) repository, allowing you to debug and explore this stuff by yourself. We will cover the following:

- [**Part 1:**](https://redops.at/en/blog/the-emulators-gambit-executing-code-from-non-executable-memory#:~:text=5%3A%20Debugging%20walkthrough-,Part%201%3A%20Understanding%20the%20Problem,-When%20working%20with) Understanding the problem (VirtualProtect-based execution)
- [**Part 2:**](https://redops.at/en/blog/the-emulators-gambit-executing-code-from-non-executable-memory#:~:text=the%20entire%20execution.-,Part%202%3A%20Demonstrating%20Memory%20Protection,-Before%20we%20explore) Demonstrating memory protection (intentional access violation)
- [**Part 3:**](https://redops.at/en/blog/the-emulators-gambit-executing-code-from-non-executable-memory#:~:text=Part%203%3A%20The%20Solution%2C%20Theory%20(HWBP%20%2B%20VEH%20%2B%20Emulation)) The solution, theory (HWBP + VEH +Emulation)
- [**Part 4:**](https://redops.at/en/blog/the-emulators-gambit-executing-code-from-non-executable-memory#:~:text=and%20defensive%20considerations.-,Part%204%3A%20Programmatic%20Implementation,-Now%20that%20we) Programmatic implementation
- [**Part 5:**](https://redops.at/en/blog/the-emulators-gambit-executing-code-from-non-executable-memory#:~:text=from%20emulated%20code%22.-,Part%205%3A%20Debugging%20Walkthrough,-To%20truly%20understand) Debugging walkthrough

### Part 1: **Understanding the Problem**

When working with virtual memory in Windows, it's crucial to understand memory protection constants, which are [officially documented](https://learn.microsoft.com/en-us/windows/win32/memory/memory-protection-constants) by Microsoft. Each section of a Portable Executable (PE) file is assigned specific memory protection attributes at runtime based on its intended purpose.

For example, the `.data` section is typically assigned the memory protection constant `PAGE_READWRITE` (`0x04`), meaning it is readable and writable but not executable. In practice, we can read from this section and write data or code to it, but any attempt to execute code from this section will trigger an access violation due to the missing execute permission.

To demonstrate how `VirtualProtect()` can be used to change these protections, let's examine the Visual Studio project **Win32Data\_Rw\_To\_Rx**, which is available in the [**GitHub repository**](https://github.com/VirtualAlllocEx/HWBP-DEP-Bypass). We'll walk through the code and debug it step-by-step using x64dbg in the following sections.

#### Initial Memory State

When executing our test sample Win32Data\_Rw\_To\_Rx, we first want to verify the **initial memory state** of the .data section, where we have stored a simple shellcode sequence:

```c
0x90, 0x90, 0x90, 0x90, 0x90, 0xC3
```

This sequence represents five **NOP** instructions followed by a **RET** instruction. The shellcode is stored as a static array in the .data section.

![](https://redops.at/assets/images/blog/ShellcodeInDataSection.png)

Upon running the program, the **debug console** confirms that the memory protection for the .data section is set to **RW**(`PAGE_READWRITE`), which is the expected default.

![](https://redops.at/assets/images/blog/DataSectionInitialMemoryState2.png)

To verify the runtime memory protection of the `.data` section, we can use Process Hacker (or similar memory inspection tools) to examine the actual protection attributes assigned by Windows when the PE is loaded. The screenshot below shows the `.data` section with `PAGE_READWRITE` protection—readable and writable, but crucially, not executable.

This protection is enforced by the CPU's MMU (Memory Management Unit). If we attempt to jump to an address in the `.data` section and execute instructions, the CPU will immediately raise an `EXCEPTION_ACCESS_VIOLATION` because the memory page lacks the execute permission. We'll trigger this intentionally in Part 2 to demonstrate the behavior.

![](https://redops.at/assets/images/blog/DataSectionInitialMemoryStateProcessHacker2.png)

#### Change Memory Protection

Now, let’s continue debugging our `Win32Data_Rw_To_Rx.exe` sample and modify the memory protection of the `.data` section from **RW** to **RX** using the `VirtualProtect()` function, as shown in the code snippet below.

```c
DWORD oldProtect = 0;
VirtualProtect(shellcode, sizeof(shellcode), PAGE_EXECUTE_READ, &oldProtect);
```

As shown in the image below, in the debugging console from our executed `Win32Data_Rw_To_Rx.exe` sample we can observe, that the protection has been successfully changed from `PAGE_READWRITE` (RW) to `PAGE_EXECUTE_READ` (RX), allowing our shellcode to execute.

![](https://redops.at/assets/images/blog/DebugConsoleChangeMemoryToRx.png)

To confirm that the memory protection change is real and not just a debugger artifact, we can use Process Hacker to inspect the process memory independently. As shown in the image below, Process Hacker verifies that the `.data` section's protection has been successfully changed to `PAGE_EXECUTE_READ` (`0x20`) by the `VirtualProtect()` function.

![](https://redops.at/assets/images/blog/DebugConsoleChangeMemoryToRxProcessHacker.png)

#### Execute Shellcode

Now we'll verify that execution actually reaches our shellcode and runs correctly. Our test shellcode is simple: `0x90, 0x90, 0x90, 0x90, 0x90, 0xC3`—five NOP (no operation) instructions followed by a RET instruction to return control.

![](https://redops.at/assets/images/blog/ExecuteShellcodeOutputDebugConsolepng.png)

In x64dbg's CPU window, we can set a software breakpoint using the `bp` command followed by the target address. For example, if our shellcode starts at `0x00007FF6A9B04000`, we'd enter:

```plaintext
bp 00007FF6A9B04000
```

As shown in the screenshot below, when this breakpoint is hit during execution, it confirms the CPU is successfully executing instructions from the `.data` section, which now has RX protection after our `VirtualProtect()` call.

![](https://redops.at/assets/images/blog/x64dbg_set_bp_first_NOP_new.png)

To verify the shellcode (`0x90, 0x90, 0x90, 0x90, 0x90, 0xC3`) executes correctly, we can single-step through each instruction using x64dbg's Step Into function (F7). As we step through the code, we should pay close attention to the RIP register in the registers window on the right side of x64dbg. With each press of F7, RIP advances by exactly 1 byte as it moves through each NOP instruction. Since NOP is a single-byte instruction (`0x90`), we can watch RIP increment sequentially through our five NOPs.

![](https://redops.at/assets/images/blog/x64dbg_hit_first_NOP_new.png)

We can now verify execution by single-stepping through the entire shellcode sequence using x64dbg's Step Into (F7) function. Starting with RIP at `0x00007FF624320000` (the first NOP), each press of F7 executes one instruction and advances RIP accordingly. As we step through the five NOP instructions, RIP progresses sequentially: from `...000` to `...001`, then to `...002`, and so on.

Each NOP is a single-byte instruction, so RIP advances by exactly 1 byte with each step. After executing all five NOPs, RIP reaches `0x00007FF624320005`, which points to our final instruction—the RET at offset 5.

![](https://redops.at/assets/images/blog/x64dbg_hit_last_NOP_new.png)

After stepping through the five NOP instructions, RIP now points to the RET instruction (`0xC3`) at address `0x00007FF624320005`. Pressing F7 one final time executes this RET, which performs two key operations: it pops the return address from the stack and sets RIP to that address. As shown in the image below, we can observe RIP jumping back to our main program code, completing the entire execution cycle. The shellcode has run from start to finish—all five NOPs executed sequentially, and the RET successfully returned control to the calling function. The fact that we encountered no access violations during this entire process confirms that the CPU is successfully fetching and executing instructions from the `.data` section, which is only possible because `VirtualProtect()` changed the memory protection from RW to RX.

![](https://redops.at/assets/images/blog/x64dbg_hit_ret_new.png)

Before examining the RET instruction's execution in detail, let's understand what's happening with the stack. Looking at the registers shown in the image below, we see RIP at `0x00007FF624320005` (the RET instruction itself) and RSP at `0x000000998CCFF8A8`. The RSP register points to a location on the stack where the return address is stored. If we examine the Stack panel on the right side of the debugger, we can see the value at that stack address: `0x00007FF624312BA3`. The debugger helpfully labels this as "return to win32data\_rw\_to\_rx.main+63", indicating exactly where execution will resume after the RET completes.

![](https://redops.at/assets/images/blog/x64dbg_at_ret_to_main_new.png)

Now, when we press F7 to step through the RET instruction, the operation executes atomically. The CPU reads the return address from the stack location pointed to by RSP (`0x00007FF624312BA3`), loads it into RIP, and then increments RSP by 8 bytes to pop the value off the stack. As shown in Image 3, after the RET executes, RIP is now `0x00007FF624312BA3`—exactly the value that was stored on the stack. RSP has incremented from `0x000000998CCFF8A8` to `0x000000998CCFF8B0`, reflecting the 8-byte pop operation.

![](https://redops.at/assets/images/blog/x64dbg_after_ret_to_main_new.png)

The x64dbg info bar at the bottom of the screen provides important confirmation of our successful return. Before the RET, we were at `.data:00007FF624320005`—our shellcode in the `.data` section. After the RET, we're now at `.text:00007FF624312BA3`—back in the main program's `.text` section. This section transition proves we successfully executed code from the `.data` section and returned cleanly to normal program flow. The disassembly window now shows the instructions that follow our original shellcode invocation, confirming we've landed at the correct location. Everything worked as intended: our shellcode executed from RW-turned-RX memory in the `.data` section, and the RET instruction successfully returned control to the calling function in the `.text` section.

#### Part 1 - Summary

In this first demonstration, we walked through the traditional method of shellcode execution using the `Win32Data_Rw_To_Rx.exe` sample. This program stores minimal test shellcode—five NOP instructions (`0x90`) followed by a RET instruction (`0xC3`)—in the `.data` section of the PE file.

Using x64dbg, we verified the complete execution flow step by step. First, we confirmed that the `.data` section initially has `PAGE_READWRITE (0x04)` protection, meaning the memory is readable and writable but not executable due to DEP/NX protection. Second, we observed that calling `VirtualProtect()` successfully modifies the page protection from `PAGE_READWRITE (0x04)` to `PAGE_EXECUTE_READ (0x20)`, updating the page table entries to mark the memory as executable. Finally, we confirmed the shellcode executes successfully—the CPU fetches and executes all five NOP instructions followed by the RET, completing without any access violations.

This demonstrates that `VirtualProtect()` is the standard approach for making data memory executable. The API call modifies page table entries at the OS level, allowing the CPU to fetch instructions from previously non-executable pages. Now that we understand how this baseline method works, we can explore what happens when we deliberately break it and then look at an alternative approach.

Part 2 will demonstrate what happens when we skip the `VirtualProtect()` call entirely—intentionally triggering an `EXCEPTION_ACCESS_VIOLATION` to show DEP/NX protection in action. Then in Parts 3 and 4, we'll dive into the core technique of this blog post: executing shellcode from RW memory using Hardware Breakpoints, Vectored Exception Handling, and Instruction Emulation. This approach completely "bypasses" the need for `VirtualProtect()` while keeping memory protection as RW throughout the entire execution.

### Part 2: **Demonstrating Memory Protection**

Before we explore how to execute shellcode from non-executable memory, it's important to understand exactly what problem we're solving. Let's see what happens when we simply remove the `VirtualProtect()` call from our previous example and try to execute code directly from RW memory.

By removing the memory protection change, we intentionally trigger the exact problem that DEP/NX is designed to prevent. As soon as the CPU attempts to fetch the first instruction from our shellcode in the non-executable `.data` section, it raises a memory access violation exception (`0xC0000005`). This crash demonstrates why `VirtualProtect()` is normally required—the CPU's Memory Management Unit (MMU) checks the NX bit before every instruction fetch and blocks execution from non-executable pages.

For this demonstration, I've created a separate test sample called **Win32Data\_Rw\_NoChange**, which you can download from my [**GitHub repository**](https://github.com/VirtualAlllocEx/HWBP-DEP-Bypass). This sample is identical to the previous one, except it omits the `VirtualProtect()` call entirely. This lets us observe the access violation in a controlled debugging environment and see exactly when and how it occurs.

As shown in the screenshot below, when we attempt to execute our shellcode (`0x90, 0x90, 0x90, 0x90, 0x90, 0xC3`) from the `.data` section, the program immediately crashes with a memory access violation. The debugger's status bar shows "First chance exception on `00007FF79B3A1000` (`C0000005`, `EXCEPTION_ACCESS_VIOLATION`)!"—this means the CPU caught the violation before the exception propagated to the application's exception handlers. Looking at the Properties window on the right (from Process Hacker), we can see the root cause: the memory region at address `0x7ff79b3a1000` where our shellcode resides has protection set to "RW" (Read-Write) without execute permission. The CPU detected this during instruction fetch and raised the exception before a single instruction could execute. This is DEP/NX protection working exactly as designed—actively preventing code execution from non-executable memory.

![](https://redops.at/assets/images/blog/x64dbg_memory_error.png)

Now we've seen both sides of the story. In Part 1, shellcode execution succeeded after calling `VirtualProtect()` to make memory executable. In Part 2, without that call, the CPU immediately raised an access violation—execution stopped before the first instruction could run. The `.data` section's RW protection did its job.

This raises an interesting question: is there a way to execute code from RW memory without ever changing the protection? Can we somehow get around the MMU's NX check without modifying page table entries? As we'll see in Parts 3, 4 and 5 the answer is yes—but it requires working at a much lower level of the CPU architecture.

### Part 3: **The Solution, Theory (HWBP + VEH + Emulation)**

The solution comes from understanding the order of operations in the CPU's fetch-decode-execute cycle. Hardware breakpoints trigger before the CPU performs instruction fetch, which means they fire before the MMU checks the NX bit on the page table entry. This timing is crucial—if we can intercept execution at the hardware level using a breakpoint, we catch control before the NX check happens. Then, by handling the resulting exception and emulating the instruction in software, we can achieve code execution without the memory ever being marked as executable. The CPU never actually fetches from the non-executable memory—we read it as data instead.

This is the core insight behind our technique. Now that we understand the problem—DEP/NX preventing execution from RW memory—let's explore how to "bypass" it without calling `VirtualProtect()`. Our solution combines three techniques that work together, and we'll start with the foundation: Hardware Breakpoints.

#### Theory: Hardware Breakpoints

Hardware breakpoints are a debugging feature built directly into the CPU architecture. Unlike software breakpoints, which modify code by inserting an INT3 instruction (`0xCC`) at the target address, hardware breakpoints use dedicated CPU registers to monitor memory addresses without changing any code. This is the key difference that makes our technique possible—we need to intercept execution without modifying the shellcode itself, and hardware breakpoints let us do exactly that.

#### **CPU Debug Registers: The Foundation**

The x86-64 architecture provides eight debug registers (DR0 through DR7) that have been part of the x86 architecture since the [Intel 80386](https://en.wikipedia.org/wiki/I386) processor back in the 1980s. These registers are the foundation of hardware breakpoints and are still used by every modern debugger today.

The registers break down into two groups. DR0, DR1, DR2, and DR3 are address registers—each can hold a single 64-bit memory address for the CPU to monitor. This gives us four simultaneous hardware breakpoints, a limitation that's remained unchanged since the 386 era. The remaining registers (DR4-DR7) control how these breakpoints behave and record status information when they trigger. The image below shows an overview of the debug register structure.

![](https://redops.at/assets/images/blog/debug_register_structure_new.png)

For our technique, we'll use DR0 to track our shellcode execution by setting it to the address where our shellcode begins. In our implementation, we configure this early in the program:

```c
CONTEXT ctx = { 0 };
ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS;
GetThreadContext(GetCurrentThread(), &ctx);

ctx.Dr0 = (DWORD64)g_codeAddress;
ctx.Dr7 = 0x1ull;

SetThreadContext(GetCurrentThread(), &ctx);
```

This code retrieves the current thread's context, sets DR0 to our shellcode's address, and configures DR7 to enable the breakpoint. The value `0x1` in DR7 is critical—it enables DR0 as a local execute breakpoint, which we'll explain shortly.

DR6 is the debug status register that tells us which breakpoint fired. When a hardware breakpoint triggers, DR6 records which specific breakpoint caused the exception. Bits 0 through 3 correspond to DR0 through DR3 respectively—if DR0's breakpoint triggers, bit 0 in DR6 gets set. The operating system typically clears DR6 before resuming execution, but we can read it in our exception handler to determine exactly which breakpoint fired. Our current implementation doesn't explicitly check DR6 since we only use one breakpoint (DR0), but if you were using multiple breakpoints simultaneously, you'd need to examine this register to know which one triggered.

DR7 is where things get interesting. This is the debug control register, and understanding its structure is essential for using hardware breakpoints effectively. This 32-bit register controls whether each breakpoint is enabled, what type of access triggers it (execution, write, or read/write), and how large the monitored region should be. Let's break down how these 32 bits are organized.

For each of the four breakpoints, DR7 contains several control fields. Bits 0 through 7 contain the enable flags, with two bits per breakpoint. Bit 0 enables DR0 locally, meaning the breakpoint is specific to the current thread and will be saved and restored during context switches. Bit 1 enables DR0 globally, meaning it persists across context switches and affects all threads. We typically use local enable by setting bit 0, which is why our code uses `ctx.Dr7 = 0x1ull`—this sets only bit 0, enabling DR0 as a local breakpoint.

Bits 16 through 31 contain the breakpoint conditions. For each breakpoint, there's a 2-bit field specifying the type—00 for execution, 01 for data write, 11 for data read or write—and another 2-bit field specifying the size—00 for 1 byte, 01 for 2 bytes, 11 for 4 bytes, or 10 for 8 bytes. For execution breakpoints, the size field is ignored since execution breakpoints always monitor a single instruction address. Our value of `0x1` uses the default type of 00 (execution) and default size of 00 (1 byte), which is exactly what we need.

Our code includes helper functions to manipulate these debug registers within exception handlers. The `SetHWBPInContext` function encapsulates the logic for configuring a hardware breakpoint:

```c
static __forceinline void SetHWBPInContext(CONTEXT* ctx, void* address) {
    ctx->Dr0 = (DWORD64)address;
    ctx->Dr7 = 0x1ull;
}

void SetHWBP(EXCEPTION_POINTERS* exceptionInfo, void* address) {
    SetHWBPInContext(exceptionInfo->ContextRecord, address);
}

void ClearHWBP(EXCEPTION_POINTERS* exceptionInfo) {
    exceptionInfo->ContextRecord->Dr0 = 0;
    exceptionInfo->ContextRecord->Dr7 = 0;
}
```

The `SetHWBP` function provides a clean interface for our exception handler to set the next hardware breakpoint after emulating an instruction, while `ClearHWBP` removes the breakpoint when we exit the shellcode region.

#### **How Hardware Breakpoints Trigger Before Instruction Fetch**

To understand why hardware breakpoints can "bypass" DEP/NX, we need to look at the timing of events in the CPU's instruction execution pipeline. Modern CPUs use a pipelined architecture where instruction processing flows through several stages: fetch, decode, execute, memory access, and write-back. The key insight is that hardware breakpoint checks happen _before_ memory protection checks—and that timing difference is what makes our technique possible.

![](https://redops.at/assets/images/blog/standard_cpu_pipeline_new.png)

When the CPU prepares to execute an instruction, the normal sequence without any breakpoints looks like this: The instruction pointer (RIP) contains the address of the next instruction to execute. The CPU's fetch unit begins the instruction fetch by requesting the instruction bytes from memory at that address. During this fetch, the Memory Management Unit (MMU) translates the virtual address to a physical address and checks the page table entry for that memory page. The page table entry contains several flags, including the NX (No-eXecute) bit. If the NX bit is set, indicating the page is non-executable, the MMU immediately blocks the fetch and raises an access violation exception (`0xC0000005`). The instruction never enters the CPU pipeline, and execution stops. The image below briefly illustrates the concept of a normal instruction fetch with an NX check.

![](https://redops.at/assets/images/blog/normal_instruction_flow_new.png)

However, when a **hardware breakpoint is set on that address**, the **sequence changes** fundamentally. Before the fetch unit even begins requesting instruction bytes, the CPU's debug logic **checks the current RIP** value **against DR0 through DR3**. This check happens in the microcode before the instruction fetch stage begins—a crucial architectural detail that makes this entire technique possible. The CPU's instruction execution pipeline consists of multiple stages: fetch, decode, execute, memory access, and write-back. Hardware breakpoint checks occur before the fetch stage even initiates, making them a pre-fetch operation rather than a post-fetch validation.

![](https://redops.at/assets/images/blog/hwbp_instruction_flow_new.png)

When the CPU prepares to execute an instruction, the normal sequence follows a predictable pattern. RIP contains the address of the next instruction, and the fetch unit issues a request to memory for the bytes at that address. This request goes through the Memory Management Unit, which translates the virtual address to a physical address and checks the page table entry for that memory page. The page table entry contains various flags including the NX bit that marks the page as non-executable. If the NX bit is set, the MMU immediately blocks the fetch and raises an access violation exception with code `0xC0000005`. The instruction never enters the CPU pipeline, and execution stops.

But hardware breakpoint checks happen earlier. If RIP matches an enabled execution breakpoint in DR0 through DR3, the CPU immediately generates a debug exception—specifically `EXCEPTION_SINGLE_STEP` with code `0x80000004`—and halts before initiating the fetch. The instruction fetch never occurs, which means the MMU never gets involved, never translates the address, never checks the page table entry, and never examines the NX bit. The debug exception fires first, preventing the access violation that would normally occur when attempting to execute from non-executable memory.

This timing difference is the key to our entire technique. The hardware breakpoint check is essentially a pre-fetch check that intercepts execution before memory protection enforcement happens. It's as if we've inserted a gate that closes before the CPU can even attempt to read the instruction from non-executable memory.

#### **Why This Works**

The "bypass" works because of the order of operations at the CPU hardware level. DEP and the NX bit are memory protection mechanisms enforced by the MMU during instruction fetch. They work by marking pages as non-executable in the page table, and the MMU checks these flags when the CPU tries to fetch instructions. But hardware breakpoints operate at an earlier stage—they're checked by the CPU's debug logic before the fetch request even reaches the MMU.

When our hardware breakpoint triggers, the CPU generates `EXCEPTION_SINGLE_STEP` and transfers control to the operating system's exception dispatcher. The exception contains the complete CPU context, including all register values, RIP, RSP, and the debug registers themselves. The Windows exception dispatcher then walks the exception handler chain, and this is where our Vectored Exception Handler comes into play. At this point, we're in our exception handler with full access to the CPU context, and we can read the instruction bytes from memory as data—which is allowed because the page is readable—emulate what that instruction would do, update the CPU context accordingly, and return. The CPU then resumes execution with our modified context, and we've effectively executed an instruction without the CPU ever fetching it from non-executable memory.

![](https://redops.at/assets/images/blog/veh_instruction_flow_new2.png)

The elegance of this technique lies in what never happens. The `.data`section never needs to change protection. Throughout the entire execution of our shellcode, the memory remains RW. If a security tool scans memory looking for executable shellcode, it won't find RWX or RX pages—just normal RW data pages. The **CPU never attempts to execute code** from these pages in the traditional sense. Instead, we're **reading the opcodes as data** and **simulating their effects** in software, and from the CPU's perspective, it's attempting to fetch an instruction, getting interrupted by a debug exception before the fetch completes, and then resuming at a different address.

The **main limitation** is that we only have **four hardware breakpoints available** through DR0 through DR3. Since our shellcode likely contains more than four instructions—even our simple test case has six—we can't set breakpoints on every instruction simultaneously. This means we need to "chain" our breakpoints, setting a new hardware breakpoint after handling each instruction. This chaining happens in our exception handler, and we'll see the implementation shortly. Each time our handler runs, it emulates the current instruction, calculates where RIP should go next, sets a new hardware breakpoint at that address, and returns. This process repeats for every single instruction in our shellcode, making execution significantly slower than native code, but it works reliably and "bypasses" DEP/NX completely.

![](https://redops.at/assets/images/blog/hwbp_chaining.png)

### Theory: Vectored Exception Handling

Now that we understand how hardware breakpoints generate debug exceptions before the CPU checks memory permissions, we need a mechanism to intercept and handle these exceptions. This is where Vectored Exception Handling (VEH) comes into play. VEH provides us with a way to receive first notification of exceptions in our process, giving us the opportunity to examine the exception, modify the CPU state, and decide whether to handle the exception or pass it along to other handlers.

#### **Understanding Windows Exception Handling Architecture**

When an exception occurs in a Windows process, the operating system doesn't immediately terminate the program. Instead, Windows provides multiple layers of exception handling, creating opportunities for code to catch and respond to exceptions. Understanding this hierarchy is crucial because it explains why VEH is the ideal choice for our technique.

The exception handling chain in Windows follows a specific order determined by the operating system. When the CPU raises an exception—whether it's a hardware breakpoint, an access violation, or any other exception—the kernel's exception dispatcher takes control and begins walking through the exception handling chain in a predefined sequence.

![](https://redops.at/assets/images/blog/exception_handler_chain_new.png)

First in line are the Vectored Exception Handlers. These are process-wide handlers registered through the `AddVectoredExceptionHandler` API. If multiple VEH handlers are registered, they're called in the order they were registered if registered with the "first" flag, or in reverse order if registered with the "last" flag. VEH handlers receive the exception first, before any other user-mode exception handling mechanism. This first-chance notification is what makes VEH perfect for our technique—we get to see and handle the hardware breakpoint exception before anything else can interfere. Our code registers the handler early in the program's execution:

```c
PVOID handler = AddVectoredExceptionHandler(1, MyExceptionHandler);
if (!handler) {
    printf("[!] Failed to install VEH\n");
    return 1;
}
printf("[+] VEH installed at %p\n", handler);
```

The first parameter, `1`, indicates we want our handler added to the front of the VEH chain, ensuring it's called before other VEH handlers. The function returns an opaque handle that we save for later cleanup.

If all VEH handlers return `EXCEPTION_CONTINUE_SEARCH`, indicating they didn't handle the exception, Windows moves to the next layer: the debugger. If a debugger is attached to the process, it receives the exception at this point. The debugger can examine the exception, step through code, or continue execution. For our technique, we typically don't have a debugger attached during normal execution, so this step is skipped. However, during development and testing, this can complicate debugging since the debugger might interfere with our exception handling flow.

After the debugger layer, Windows checks Structured Exception Handlers. SEH is the traditional exception handling mechanism in Windows, implemented through `__try` and `__except` blocks in C and C++. SEH handlers are stack-based and frame-based, meaning each function can have its own exception handler that protects that function's scope. Windows walks the stack frames looking for SEH handlers, calling each one until it finds one that handles the exception. SEH handlers are more localized than VEH—they only protect specific code blocks rather than the entire process.

If no SEH handler handles the exception, Windows checks Vectored Continue Handlers, which are similar to VEH but called after SEH rather than before. VCH was added in Windows Vista and is rarely used. For our purposes, we don't need VCH because we handle the exception in our VEH. Finally, if no handler in the chain handles the exception, Windows invokes the Unhandled Exception Filter, which typically displays the familiar "program has stopped working" dialog and terminates the process.

#### **Why Vectored Exception Handling?**

Given this hierarchy, why do we choose VEH over SEH for our technique? The answer lies in several compelling advantages. First and most importantly, VEH is called first. When our hardware breakpoint triggers, our VEH receives the exception before any other user-mode handler. This gives us complete control over the exception handling process. We can examine the exception, decide how to handle it, modify the CPU context, and either handle it completely or pass it along. With SEH, we'd only get the exception after VEH handlers and after the debugger if one is attached, which could interfere with our technique.

Second, VEH is process-wide rather than scope-based. A single VEH registration covers the entire process across all threads. This is particularly useful if our shellcode might be called from different functions or if we want to protect multiple shellcode regions. With SEH, we'd need to wrap each potential execution point in a `__try`/`__except` block, which is more cumbersome and less flexible.

Third, VEH is not stack-based. SEH handlers are stored on the stack as part of the function's stack frame, which makes them vulnerable to stack corruption attacks. VEH handlers are stored in a linked list in the Process Environment Block, separate from the stack, making them more resistant to certain types of attacks. For our legitimate debugging technique, this isn't a security concern per se, but it demonstrates that VEH is a more robust mechanism architecturally.

Fourth, VEH allows us to modify the CPU context and continue execution in a very clean way. When we return `EXCEPTION_CONTINUE_EXECUTION` from our VEH, Windows restores the modified context and resumes execution exactly where we specify. This is perfect for our technique because after emulating an instruction, we need to change RIP to point to the next instruction and potentially modify other registers based on what the instruction did.

#### **The Exception Handler Function**

Our VEH function must follow a specific signature defined by Windows. The function receives a single parameter, a pointer to an `EXCEPTION_POINTERS` structure, and must return a `LONG` value indicating how the exception should be handled. This structure is the gateway to all information about the exception and the CPU state when it occurred:

```c
LONG WINAPI MyExceptionHandler(EXCEPTION_POINTERS* exceptionInfo) {
    DWORD code = exceptionInfo->ExceptionRecord->ExceptionCode;

    if (code == EXCEPTION_SINGLE_STEP) {
        DWORD64 rip = exceptionInfo->ContextRecord->Rip;
        printf("\n[VEH] SINGLE_STEP at RIP=%p\n", (void*)rip);

        // Handler logic continues...
    }

    return EXCEPTION_CONTINUE_SEARCH;
}
```

The `EXCEPTION_POINTERS` structure contains two critical pointers. The first, `ExceptionRecord`, points to an `EXCEPTION_RECORD` structure that describes the exception itself. This structure contains the `ExceptionCode` field, which tells us what type of exception occurred. For our technique, we're primarily interested in `EXCEPTION_SINGLE_STEP` with code `0x80000004`, which is generated by hardware breakpoints. The structure also contains `ExceptionAddress`, which holds the address where the exception occurred, and various other fields providing additional context about the exception.

The second pointer, `ContextRecord`, is even more important for our technique. It points to a `CONTEXT` structure that contains the complete CPU state at the time of the exception. This structure, captures every aspect of the CPU's state. It includes all general-purpose registers—RAX through R15, RSP, RBP, RSI, and RDI—the instruction pointer RIP, the stack pointer RSP, the debug registers DR0 through DR7, the flags register EFLAGS, and even floating-point and vector registers. For our technique, we primarily care about the general-purpose registers, RIP, RSP, and the debug registers.

The critical insight that makes our technique possible is that this `CONTEXT` structure is not just a read-only snapshot—we can modify it. When our exception handler returns `EXCEPTION_CONTINUE_EXECUTION`, Windows restores the CPU state from this modified context. This is how we implement instruction emulation: we read the instruction bytes as data, figure out what they would do, update the context accordingly to simulate those effects, and let Windows restore our modified state. The CPU resumes execution with our changes applied, as if the instruction had executed normally.

#### **Complete Handler Implementation**

Our complete exception handler implements the full logic for intercepting hardware breakpoints, verifying they're in our shellcode region, emulating instructions, and chaining breakpoints:

```c
LONG WINAPI MyExceptionHandler(EXCEPTION_POINTERS* exceptionInfo) {
    DWORD code = exceptionInfo->ExceptionRecord->ExceptionCode;

    if (code == EXCEPTION_SINGLE_STEP) {
        DWORD64 rip = exceptionInfo->ContextRecord->Rip;
        printf("\n[VEH] SINGLE_STEP at RIP=%p\n", (void*)rip);

        if (rip >= (DWORD64)g_codeAddress &&
            rip < (DWORD64)g_codeAddress + g_codeSize) {

            g_instructionCount++;

            if (!EmulateInstruction(exceptionInfo, (unsigned char*)rip)) {
                ClearHWBP(exceptionInfo);
                return EXCEPTION_CONTINUE_SEARCH;
            }

            if (exceptionInfo->ContextRecord->Rip >= (DWORD64)g_codeAddress &&
                exceptionInfo->ContextRecord->Rip < (DWORD64)g_codeAddress + g_codeSize) {

                SetHWBP(exceptionInfo, (void*)exceptionInfo->ContextRecord->Rip);
            }
            else {
                ClearHWBP(exceptionInfo);
            }

            return EXCEPTION_CONTINUE_EXECUTION;
        }
    }

    return EXCEPTION_CONTINUE_SEARCH;
}
```

The handler begins by filtering exceptions. We only care about `EXCEPTION_SINGLE_STEP`, so we check the exception code first. If it's not a single-step exception, we immediately return `EXCEPTION_CONTINUE_SEARCH` to let other handlers deal with it. This is important because our process might generate other exceptions that we shouldn't interfere with.

Once we've confirmed it's a single-step exception, we extract the current RIP value from the context. This tells us where the exception occurred. We then verify that RIP is within our shellcode region by checking if it falls between `g_codeAddress` and `g_codeAddress` plus `g_codeSize`. This verification prevents us from accidentally emulating random code elsewhere in the process. If the exception occurred outside our shellcode region, perhaps because another debugger or tool set a hardware breakpoint, we return `EXCEPTION_CONTINUE_SEARCH` to avoid interfering.

If the exception is within our shellcode region, we increment our instruction counter for statistics, then call `EmulateInstruction` to actually handle the instruction. We'll explore instruction emulation in detail in the next section, but for now, it's sufficient to know that this function reads the instruction bytes, decodes them, and updates the context to reflect what the instruction would have done. If emulation fails because we encounter an unsupported instruction, we clear the hardware breakpoint and return `EXCEPTION_CONTINUE_SEARCH`, allowing the exception to propagate naturally.

After successful emulation, we check if RIP is still within our shellcode region. Emulation will have updated RIP to point to the next instruction. If we're still inside the shellcode, we need to chain our hardware breakpoint by setting DR0 to the new RIP value. This ensures that the next instruction will also trigger our handler. If RIP has moved outside the shellcode region—for example, because we emulated a RET instruction that returned to the caller—we clear the hardware breakpoint since we're done emulating.

Finally, we return `EXCEPTION_CONTINUE_EXECUTION` to tell Windows that we've handled the exception and it should resume execution with our modified context. Windows takes our updated RIP value, updated register values, and updated debug registers, restores them to the CPU, and resumes execution. The CPU then attempts to execute the next instruction, the hardware breakpoint triggers again, and the cycle continues.

#### **Exception Handler Return Values and Cleanup**

The return value from our VEH is critical to how Windows proceeds after the exception. `EXCEPTION_CONTINUE_EXECUTION`, with value `-1` or `0xFFFFFFFF`, tells Windows that we've handled the exception and execution should continue. When we return this value, Windows stops walking the exception handler chain, restores the CPU context from our modified `ContextRecord`, and resumes execution at the RIP we've set. This is what we return after successfully emulating an instruction—we've fixed up the context to reflect what the instruction should have done, and we want execution to continue with our changes.

`EXCEPTION_CONTINUE_SEARCH`, with value `0`, tells Windows that we didn't handle this exception and it should continue walking the exception handler chain. The next handler in line gets a chance to handle it. We return this value for exceptions we don't care about—for example, if our handler receives an `EXCEPTION_ACCESS_VIOLATION` that's not related to our shellcode, or a `EXCEPTION_SINGLE_STEP` that occurred outside our code region, we'd return `EXCEPTION_CONTINUE_SEARCH` to let other handlers or the system deal with it appropriately.

When our program exits or when we're done with the technique, we need to clean up by removing our VEH handler:

```c
RemoveVectoredExceptionHandler(handler);
```

This removes our handler from the exception chain using the handle we saved when we registered it. Proper cleanup is important to avoid leaving stale exception handlers in the process, though in our case, the program exits shortly after we finish demonstrating the technique.

#### **Integration with Hardware Breakpoints: The Complete Flow**

Now we can see how VEH integrates seamlessly with our hardware breakpoint technique. The flow begins in our main function, where we set up all the pieces. First, we install our VEH handler to catch exceptions. Then we configure the hardware breakpoint by setting DR0 to our shellcode's address and DR7 to enable it. Finally, we call our shellcode as if it were a normal function:

```c
printf("\n[*] Calling demo_code at %p ...\n", g_codeAddress);
typedef void (*func_t)(void);
func_t f = (func_t)g_codeAddress;

__try {
    f();
    printf("[+] Returned cleanly from emulated code\n");
}
__except (EXCEPTION_EXECUTE_HANDLER) {
    printf("[!] Exception: 0x%08lx\n", GetExceptionCode());
}
```

When we call the function pointer, the CPU executes a `CALL` instruction that pushes the return address onto the stack and sets RIP to our shellcode's address. At this point, the CPU attempts to fetch the first instruction from our shellcode. But before the fetch completes, before the MMU checks the NX bit, the CPU's debug logic checks RIP against DR0, finds a match, and raises `EXCEPTION_SINGLE_STEP`. Windows receives this exception and begins walking the exception handler chain, calling our VEH first.

Our VEH examines the exception, confirms it's a single-step at an address within our shellcode, and calls `EmulateInstruction`. The emulator reads the first byte—`0x90`, a NOP instruction—and updates the context by incrementing RIP by 1. The VEH then sets DR0 to this new RIP value and returns `EXCEPTION_CONTINUE_EXECUTION`. Windows restores the modified context, and the CPU resumes at the new RIP, which points to the second NOP instruction.

This process repeats five times for the five NOP instructions, with each one incrementing RIP by 1. When we reach the sixth instruction, `0xC3` (RET), the emulator pops the return address from the stack, sets RIP to that address, and adjusts RSP. This RIP value is back in our main function, outside the shellcode region. The VEH detects this, clears the hardware breakpoint, and returns. The CPU resumes execution in main, right after our function call, and the program continues normally.

From the program's perspective, we called a function and it returned cleanly. From the CPU's perspective, it attempted to execute six instructions but got interrupted by debug exceptions each time, never actually fetching instructions from non-executable memory. From DEP/NX's perspective, nothing suspicious happened—no code was ever executed from non-executable pages, and no memory protection was changed. We've successfully "bypassed" the protection by exploiting the timing of hardware breakpoint checks and using software emulation to simulate instruction execution.

### Theory: Instruction Emulation

With hardware breakpoints intercepting execution and VEH providing us with exception handling control, we arrive at the third and most complex component of our technique: instruction emulation. This is where we actually simulate what the CPU would do if it were executing the instructions normally. Emulation is the bridge that allows us to achieve code execution without the CPU ever fetching instructions from non-executable memory.

#### **The Fundamental Concept**

Instruction emulation means reading instruction bytes as data, understanding what those bytes represent, and manually updating the CPU's state to reflect what would have happened if the instruction had executed. The key insight is the distinction between reading memory and executing from memory. DEP/NX prevents the CPU from executing code by blocking instruction fetches from non-executable pages, but it doesn't prevent us from reading those same bytes as ordinary data. A byte containing `0x90` can be read as data from RW memory without any issues—it's only when the CPU tries to interpret that byte as an instruction and execute it that DEP/NX intervenes.

![](https://redops.at/assets/images/blog/reading_data_vs_executing_instrc.png)

Our technique exploits this distinction. When our hardware breakpoint triggers and our VEH receives the exception, we're running in a different context—our exception handler code, which is executing from the `.text` section of our program, which is properly marked as executable. From this privileged position, we can read bytes from the non-executable shellcode region, and these reads are treated as data reads, not instruction fetches. We can then analyze these bytes, figure out what instruction they represent, and manually perform the operations that instruction would have performed by updating the `CONTEXT` structure that Windows will restore when we return from our exception handler.

#### **Understanding x86-64 Instruction Encoding**

To emulate instructions, we first need to understand how instructions are encoded in the x86-64 architecture. Unlike RISC architectures where instructions have a fixed width, x86-64 instructions are variable-length, ranging from a single byte to fifteen bytes. This variable length is a consequence of the architecture's long history and backward compatibility requirements stretching back to the original 8086 processor from 1978.

An x86-64 instruction can contain several components, though not all are present in every instruction. The general structure consists of optional prefixes, an optional REX prefix specific to 64-bit mode, the opcode that identifies the instruction, an optional ModR/M byte that specifies operands, an optional SIB byte for complex addressing, an optional displacement value, and an optional immediate value. The simplest instructions consist of just an opcode byte, while complex instructions can include multiple components.

Let's examine the instructions in our test shellcode to understand this encoding. Our shellcode consists of six bytes: five` 0x90` bytes followed by a `0xC3` byte. These represent five NOP instructions and one RET instruction. The NOP instruction, encoded as `0x90`, is one of the simplest x86 instructions. It consists of a single opcode byte with no operands, no prefixes, and no additional components. The instruction means "no operation"—it does nothing except advance the instruction pointer by one byte. Historically, `0x90` is actually the encoding for "XCHG EAX, EAX" (exchange EAX with itself), which has no effect, making it an ideal no-operation instruction.

The RET instruction, encoded as `0xC3`, is slightly more complex conceptually, though it's still just a single byte. RET means "return from function" and performs several operations atomically. It pops a return address from the stack, sets the instruction pointer to that address, and adjusts the stack pointer. Understanding what RET does requires understanding the x86 calling convention and stack manipulation.

For more complex instructions that we might encounter in real shellcode, the encoding becomes significantly more intricate. Consider a MOV instruction that moves a value from one register to another, such as "MOV RAX, RCX". This instruction might be encoded as `0x48 0x89 0xC8`. The first byte, `0x48`, is a REX prefix indicating a 64-bit operation. The REX prefix is specific to x86-64 and wasn't present in 32-bit x86. It's a single byte with the format 0100WRXB, where W indicates 64-bit operand size, and R, X, B extend the register encoding fields. The second byte, `0x89`, is the opcode for MOV with a specific direction and operand size. The third byte, `0xC8`, is the ModR/M byte that specifies which registers are involved—in this case, RAX as destination and RCX as source.

The ModR/M byte itself has structure. It consists of three fields: a 2-bit Mod field specifying the addressing mode, a 3-bit Reg field specifying a register, and a 3-bit R/M field specifying another register or memory operand. The encoding `0xC8` in binary is `11001000`, which breaks down as Mod=11 (register-direct, no memory), Reg=001 (ECX/RCX), and R/M=000 (EAX/RAX). Combined with the REX.W bit indicating 64-bit operation, this gives us MOV RAX, RCX.

#### **Decoding Instructions**

The decoding process requires reading bytes sequentially and interpreting them according to the x86-64 specification. We start at the instruction pointer and read forward, identifying each component. The process begins by checking for prefixes. Legacy prefixes like `0x66` (operand size override), `0x67` (address size override), `0xF0` (LOCK), and segment overrides can appear at the beginning of an instruction. After any legacy prefixes, we check for a REX prefix, which will be in the range `0x40` through `0x4F`.

Once we've processed prefixes, we read the opcode. Most opcodes are a single byte, but some instructions use two-byte opcodes starting with `0x0F`, and a few use three-byte opcodes starting with `0x0F 0x38` or `0x0F 0x3A`. The opcode tells us what instruction this is and gives us clues about what additional bytes might follow.

After the opcode, we check if the instruction uses a ModR/M byte. Not all instructions have one, but many do. The ModR/M byte's presence depends on the specific opcode. If present, we decode it to understand which registers or memory operands are involved. The Mod field tells us whether we're dealing with register-direct addressing or memory addressing with various displacement sizes. If the ModR/M byte indicates memory addressing and the R/M field is 100 (binary), this signals the presence of a SIB byte for complex addressing involving a base register, an index register, and a scale factor.

Depending on the Mod field and the instruction, there might be a displacement value following the ModR/M or SIB byte. This displacement can be 1, 2, or 4 bytes and represents an offset added to a base address. Finally, some instructions have an immediate value—a constant that's part of the instruction itself. Immediate values can be 1, 2, 4, or 8 bytes depending on the instruction and operand size.

This decoding process is complex and requires careful implementation. A full x86-64 decoder is thousands of lines of code. However, for our demonstration, we only need to handle a tiny subset of instructions—specifically, the ones in our test shellcode.

#### **Emulating NOP Instructions**

Let's examine how we emulate the NOP instruction in our code. The emulation function receives the exception information and a pointer to the current instruction:

```c
BOOL EmulateInstruction(EXCEPTION_POINTERS* exceptionInfo, unsigned char* address) {
    unsigned char opcode = *address;
    printf("  [Emulate] RIP=%p Opcode=0x%02X\n",
        (void*)exceptionInfo->ContextRecord->Rip, opcode);

    switch (opcode) {
    case 0x90:
        exceptionInfo->ContextRecord->Rip += 1;
        return TRUE;
    // ... other cases
    }
}
```

When we encounter opcode `0x90`, we know this is a NOP instruction. The emulation is trivial: we simply increment RIP by 1. This is exactly what the CPU would do if it were executing the NOP normally—it would fetch the byte, decode it as NOP, do nothing for the operation itself, and advance RIP to the next instruction. By incrementing RIP in the context structure, we're simulating this advancement. When our exception handler returns and Windows restores the context, RIP will point to the next byte, and we'll have effectively "executed" the NOP without the CPU ever fetching it from non-executable memory.

The critical detail here is that we're reading the byte at address using a normal memory read operation—the dereference `*address`. **This is a data read, not an instruction fetch**. The page is marked as `PAGE_READWRITE` (`0x04`), which allows reading. The NX bit only prevents instruction fetches, not data reads. From the MMU's perspective, we're just reading a byte of data that happens to contain the value `0x90`. The fact that we interpret this value as an instruction opcode and use it to modify the CPU context is something that happens entirely in software, outside the MMU's purview.

#### **Emulating RET Instructions**

The RET instruction is more complex because it involves stack manipulation and control flow. When the CPU executes a RET instruction normally, it performs three operations atomically: it reads the return address from the memory location pointed to by RSP, sets RIP to that address, and adds 8 to RSP (in 64-bit mode) to pop the return address off the stack. Our emulation must replicate all three operations:

```c
case 0xC3:
{
    DWORD64 ret = *(DWORD64*)(exceptionInfo->ContextRecord->Rsp);
    printf("  [Emulate] RET to %p\n", (void*)ret);

    exceptionInfo->ContextRecord->Rip = ret;
    exceptionInfo->ContextRecord->Rsp += 8;
    return TRUE;
}
```

The emulation begins by reading the return address from the stack. We take the current value of RSP from the context and dereference it as a pointer to a 64-bit value. This reads the 8 bytes at the top of the stack, which contain the return address that was pushed there by the `CALL` instruction that invoked our shellcode. This is another data read from memory—we're reading from the stack, which is also RW memory. The read succeeds because we have read permission.

Next, we update RIP to the return address we just read. This simulates the control flow change that RET performs. Instead of continuing to the next instruction after RET, execution will jump to the return address, which is back in our main function. Finally, we increment RSP by 8 to pop the return address off the stack. This adjustment is important because it maintains the stack's integrity—if we didn't adjust RSP, the return address would still be on the stack, and any subsequent PUSHes would overwrite it or cause stack misalignment.

When our exception handler returns `EXCEPTION_CONTINUE_EXECUTION` with this modified context, Windows restores the new RIP value, which points back to main, and the new RSP value, which has moved up by 8 bytes. The CPU resumes execution at the return address, effectively completing the function return. From main's perspective, the function call completed normally and returned.

#### **The Emulation Challenge**

Our current implementation handles only two instructions: NOP and RET. This is sufficient for our simple demonstration, but real-world shellcode uses dozens or hundreds of different instruction types. A complete emulator would need to handle data movement instructions like MOV, MOVZX, and LEA; arithmetic instructions like ADD, SUB, IMUL, and DIV; logical instructions like AND, OR, XOR, and NOT; shift and rotate instructions; stack operations like PUSH and POP; control flow instructions like CALL, JMP, and conditional jumps; string operations; and many more.

Each instruction type requires careful implementation. Consider PUSH, which decrements RSP by 8 and writes a value to the stack. We'd need to read the value from the source register or memory, adjust RSP, and write the value to the new stack location. POP is the reverse: read from the stack, adjust RSP upward, and write to the destination. MOV requires identifying source and destination operands, which might be registers, memory locations, or immediate values, and transferring data between them.

Conditional jumps present an additional challenge because they require checking the flags register. Instructions like JE (jump if equal) check the Zero Flag, JL (jump if less) checks the Sign Flag and Overflow Flag, and JA (jump if above) checks the Carry Flag and Zero Flag. Our emulator would need to maintain these flags correctly based on the results of arithmetic and logical operations. When we emulate ADD, for example, we'd need to update the Zero Flag if the result is zero, the Sign Flag if the result is negative, the Carry Flag if there's unsigned overflow, and the Overflow Flag if there's signed overflow.

Memory addressing modes add another layer of complexity. An instruction might reference memory using register-direct addressing like `[RAX]`, register-plus-displacement like `[RBP+8]`, SIB-based addressing like `[RBX+RCX*4]`, or RIP-relative addressing like `[RIP+0x1000]`. Each mode requires different calculations to determine the effective address, and our emulator needs to implement all of them correctly.

For our demonstration, we deliberately chose the simplest possible shellcode—five NOPs and a RET—specifically because these instructions are easy to emulate. This allows us to focus on the core technique of using hardware breakpoints and VEH to "bypass" DEP/NX without getting bogged down in the complexities of building a full x86-64 emulator. The principle remains the same regardless of instruction complexity: read the bytes as data, decode them, simulate their effects, and update the context.

#### **Context Manipulation and State Management**

The `CONTEXT` structure we receive in our exception handler is our interface to the CPU's state. Every change we make to this structure will be reflected in the actual CPU registers when Windows restores the context. This makes the `CONTEXT` structure incredibly powerful but also demanding of correctness—if we update it incorrectly, we'll corrupt the program's state and likely cause a crash.

When emulating an instruction, we need to consider all the state it affects. Simple instructions like NOP only affect RIP, making them trivial to emulate. Instructions like RET affect both RIP and RSP. Arithmetic instructions affect multiple registers plus the flags register. Memory operations might affect both registers and memory. We need to ensure that every aspect of the instruction's behavior is replicated in our emulation.

The flags register deserves special attention. The EFLAGS register (or RFLAGS in 64-bit mode) contains individual bits representing various CPU states and conditions. The Zero Flag indicates whether the last operation produced a zero result. The Sign Flag indicates whether the result was negative (most significant bit set). The Carry Flag indicates unsigned arithmetic overflow. The Overflow Flag indicates signed arithmetic overflow. The Direction Flag controls string operation direction. The Trap Flag enables single-step debugging. Our emulation needs to update these flags appropriately when emulating instructions that affect them.

Our current implementation doesn't modify any flags because neither NOP nor RET affects flags. But if we were to emulate an ADD instruction, we'd need to calculate all the flag values based on the addition's result. This requires careful bit manipulation and understanding of how each flag is computed. The x86-64 documentation specifies exactly how each instruction affects each flag, and our emulator must replicate this behavior precisely.

#### **Chaining Hardware Breakpoints**

One of the key techniques that makes our approach work is chaining hardware breakpoints. We only have four hardware breakpoints available through DR0 through DR3, but our shellcode contains six instructions. The solution is to dynamically move the hardware breakpoint as execution progresses. After emulating each instruction, we set the next hardware breakpoint at the new RIP value, creating a chain of breakpoints that follows the execution flow through our shellcode. This chaining happens in our VEH after successful emulation:

```c
if (exceptionInfo->ContextRecord->Rip >= (DWORD64)g_codeAddress &&
    exceptionInfo->ContextRecord->Rip < (DWORD64)g_codeAddress + g_codeSize) {

    SetHWBP(exceptionInfo, (void*)exceptionInfo->ContextRecord->Rip);
}
else {
    ClearHWBP(exceptionInfo);
}
```

After emulation updates RIP, we check if the new RIP is still within our shellcode region. If it is, we call `SetHWBP` to configure DR0 to point to the new RIP value. This means when the CPU resumes and attempts to fetch the next instruction, our hardware breakpoint will trigger again, our VEH will be called again, and we'll emulate the next instruction. This process repeats for each instruction in the shellcode, creating a step-through execution where every single instruction triggers an exception and is emulated.

If the new RIP has moved outside our shellcode region, which happens after the RET instruction returns to main, we clear the hardware breakpoint by zeroing DR0 and DR7. This is important because we don't want to continue intercepting execution once we've left the shellcode. Main's code should execute normally without our intervention.

#### **Performance Implications**

The performance cost of this technique is substantial. Every instruction in our shellcode requires a complete exception handling cycle: the CPU attempts to fetch an instruction, the hardware breakpoint triggers, the CPU generates an exception and switches to kernel mode, the kernel's exception dispatcher runs, Windows walks the exception handler chain, our VEH is called in user mode, we emulate the instruction, we return to kernel mode, the kernel restores the context, and finally the CPU returns to user mode and resumes execution. This entire cycle might involve thousands of CPU cycles, whereas a single NOP instruction normally takes just one cycle.

The ratio of emulated execution time to native execution time can easily exceed 1000:1 or even 10000:1. A shellcode that would normally execute in microseconds might take milliseconds when emulated. This performance penalty is the primary practical limitation of the technique. For short shellcodes or scenarios where execution time doesn't matter, the slowdown is acceptable. But for compute-intensive shellcode or real-time scenarios, the overhead becomes prohibitive.

Additionally, the high frequency of exceptions can itself be a detection vector. Security tools monitoring for unusual patterns might notice a process generating thousands of `EXCEPTION_SINGLE_STEP` exceptions per second and flag this as suspicious behavior. While this is more subtle than monitoring for `VirtualProtect()` calls, it's still detectable by sophisticated defensive systems.

#### **The Complete Picture**

With instruction emulation in place, we now have all three components of our technique working together. Hardware breakpoints intercept execution before memory protection checks occur. Vectored Exception Handling gives us first-chance notification and control over exceptions. Instruction emulation allows us to simulate the behavior of instructions without the CPU actually fetching them from non-executable memory. Together, these mechanisms enable us to execute arbitrary code from the `.data` section without ever calling `VirtualProtect()` or changing memory protection.

![](https://redops.at/assets/images/blog/complete_picture_architecture_new3.png)

The execution flow from start to finish looks like this: Our main function sets up the VEH handler and configures the initial hardware breakpoint at the first byte of our shellcode. We then call the shellcode as if it were a normal function. The CALL instruction pushes the return address and sets RIP to our shellcode address. Immediately, the hardware breakpoint triggers because RIP matches DR0. Windows raises `EXCEPTION_SINGLE_STEP` and calls our VEH. The VEH verifies the exception is in our shellcode region, calls `EmulateInstruction` with the current RIP, and `EmulateInstruction` reads the byte at RIP, recognizes it as NOP, and increments RIP in the context. The VEH sets the next hardware breakpoint at the new RIP and returns `EXCEPTION_CONTINUE_EXECUTION`. Windows restores the modified context, and the CPU resumes.

This cycle repeats five times for the five NOP instructions, with RIP advancing by 1 each time. On the sixth iteration, `EmulateInstruction` encounters the RET instruction. It reads the return address from the stack, sets RIP to that address, and adjusts RSP. The VEH notices that the new RIP is outside the shellcode region and clears the hardware breakpoint. The CPU resumes execution back in `main`, right after the CALL instruction. From main's perspective, we called a function and it returned normally. From the CPU's perspective, it attempted to fetch six instructions but was interrupted by debug exceptions each time, never actually executing code from non-executable memory.

Throughout this entire process, the .data section containing our shellcode remained `PAGE_READWRITE`. We never called `VirtualProtect()`. We never made the memory executable. We never triggered the MMU's NX check because we never attempted instruction fetch from non-executable memory. We "bypassed" DEP/NX entirely by exploiting the timing of hardware breakpoint checks and implementing instruction execution in software rather than hardware.

#### **Practical Considerations**

Implementing this technique in practice requires careful attention to several details. First, error handling is crucial. Our emulation function returns `FALSE` when it encounters an unsupported instruction, and our VEH properly handles this by clearing the hardware breakpoint and returning `EXCEPTION_CONTINUE_SEARCH`. This allows the exception to propagate naturally, resulting in a crash with a meaningful error message rather than undefined behavior.

Second, we need to be careful about the scope of our emulation. We verify that exceptions occur within our shellcode region to avoid accidentally emulating code elsewhere. This is important because other tools or debuggers might set hardware breakpoints for their own purposes, and we shouldn't interfere with them.

Third, we need to consider thread safety if our technique might be used in a multi-threaded program. Debug registers are per-thread, so each thread has its own DR0 through DR7. If multiple threads might execute shellcode simultaneously, we need to manage the debug registers for each thread independently. Our current single-threaded demonstration doesn't require this complexity, but a production implementation would.

Fourth, we should consider cleanup. When our program exits or when we're done with the technique, we should remove the VEH handler and clear any hardware breakpoints we've set. Our code does this at the end of main:

```c
RemoveVectoredExceptionHandler(handler);
```

This ensures we don't leave stale exception handlers or hardware breakpoints that might interfere with normal program operation or debugging.

#### **Summary of the POC/Technique**

We've now explored all three components of our DEP/NX "bypass" technique in depth. Hardware breakpoints provide the interception mechanism, triggering exceptions before the MMU checks memory permissions. Vectored Exception Handling provides the control mechanism, giving us first-chance notification and the ability to modify CPU state. Instruction emulation provides the execution mechanism, allowing us to simulate instruction behavior without actual instruction fetches from non-executable memory.

The technique demonstrates a fundamental principle in computer security: defenses often protect against specific attack vectors, but attackers can find alternative paths that circumvent the defense. DEP/NX is designed to prevent code execution from data pages by blocking instruction fetches. Our technique never performs instruction fetches—instead, we read data, interpret it, and simulate its effects. The defense remains active and functional throughout, yet we achieve our goal of executing code from non-executable memory.

The technique's complexity and performance overhead limit its practical application. It requires implementing a substantial portion of an x86-64 emulator, it's significantly slower than native execution, and it can be detected through monitoring of hardware breakpoint usage and exception patterns.

In the next section,