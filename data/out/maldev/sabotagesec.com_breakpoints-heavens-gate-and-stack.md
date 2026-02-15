# https://sabotagesec.com/breakpoints-heavens-gate-and-stack/

[Skip to content](https://sabotagesec.com/breakpoints-heavens-gate-and-stack/#wp--skip-link--target)

## Breakpoints, Heavens Gate and Stack

## Recap

In previous [post](https://sabotagesec.com/stack-manipulation-via-hardware-breakpoint-direct-syscall-execution/) we implemented return address spoofing with the help of H/W breakpoints by manipulating ESP, as our program resumes following the execution of the exception handler, ntdll function call stub is executed.

In this post we will be taking a more covert route of executing an nt function via Heaven gate.

## Windows On Windows (WoW64)

Lets take a look at the syscall stub of NtAllocateVirtualMemory in x64 application. As shown in the image below we can clearly see the syscall instruction.

![](https://sabotagesec.com/wp-content/uploads/2023/09/image.png)

Examining same function stub in a 32 bit application running on x64 OS, surprisingly syscall is not be seen anywhere! Instead we see there is a call to ntdll.77668F00.

![](https://sabotagesec.com/wp-content/uploads/2023/09/image-1.png)

The function at 77668F00 simply executes a jump to WoW64Transition. Interesting eh?!

![](https://sabotagesec.com/wp-content/uploads/2023/09/image-2.png)

Following the previous jump we arrive at another jump as shown below. So folks this special kind of jump is famous Heavens Gate. This is a segment selector, 0x33 means transition from 32bit to 64bit environment. \[0x23 performs the reverse action\]. This instruction is WoW64 version of KiSystemCall in x64 environment.

![](https://sabotagesec.com/wp-content/uploads/2023/09/image-3.png)

On userland we cannot go beyond this point in a debugger. The control flow will eventually reach the same function in x64 version of the ntdll.dll, system will execute it and then again comes back to the 32bit environment. This is how 32 bit application are executed on 64bit OS, and this is Windows On Windows (WoW64). I am not going to dive into technical depths of this matter as there are number of articles on the Internet you can read.

The point is x86 stubs in WoW64 ntdll are executed via Heavens Gate, does it mean we can call it directly? Lets find out!

### State of CPU registers at the time of Heavens Gate call

once we are inside the WoW64 ntdll, we need to make a note of all the instructions that change the state of the stack starting with “call edx” as shown below. (FYI below stub is of NtAllocateVirtualMemory as shown before).

![](https://sabotagesec.com/wp-content/uploads/2023/09/image-4.png)

Lets step into the “call edx” and examine the state of the stack and CPU registers.

As expected the syscall number is moved to EAX as shown below.

![](https://sabotagesec.com/wp-content/uploads/2023/09/23.png)

Lets check the stack, we can see all the arguments pushed on to the stack, following the arguments we can see the return address for the NtAllocateVirtualMemory, and finally the ESP ie top of stack has the return address for our “call edx”. Nevermind, this stack is a random one used for explanation.

![](https://sabotagesec.com/wp-content/uploads/2023/09/2.png)

The “call edx” executed two jumps and the second jump will take us to x64 land in a nutshell, which is our Heavens Gate as shown below. Therefore following the instruction “call edx” there are no instructions that change the state of the stack, only two consecutive jumps.

![](https://sabotagesec.com/wp-content/uploads/2023/09/image-6.png)

Examining the state of the stack at the time of Heavens Gate execution is very important because to directly call the gate we will need to recreate this exact state to prevent the program from crashing and make the function call a success.

Whatever the state we are in \[in terms of stack and registers\] before the “call edx” instruction in function call stub in WoW64 ntdll, because of “call edx” we will need to push a return address thus changing the previous state of the stack. This state change is very important for the Heavens Gate transition.

## Direct Heavens Gate Invocation

### Fetching KiFastSystemCall(Heavens Gate)Address on WoW64

There is a neat trick to fetch the address of the Heavens Gate instruction dynamically via Thread Information Block ie we can simply refer FS:0xC0 or TIB + 0xC0 to retrieve the address of the gate.

### Manipulating CPU context and Stack

We need to follow below steps to successfully call the gate(with a spoofed return address):

- I am not going to explain about return address spoofing and H/W breakpoints again, read Recap section.
- When the breakpoint hits, we will be in WoW64 ntdll stub, thus we know exactly what state of the stack would be.
- In our exception handler, as seen in the previous post (go read Recap!), we will manipulate the stack accordingly but this time we will push one more return address (same gadget) to mimic the “call edx” explained in the prior section.
- Because of this extra push we need to allocate 4 extra bytes when creating a new stack.
- After doing all stack stuff, we need to place our syscall number in EAX.
- Finally place the Heavens Gate address in EIP. Thats it, we have made a successful call to gate. This is a prime ingredient in the WoW64 direct system call invocation.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>57<br>58<br>59<br>60<br>61<br>62<br>63<br>64<br>65<br>66<br>67 | `#define STACK_ARGS_LENGTH 5 //total number of args - 1`<br>`LONG``HWSpoofHandler(EXCEPTION_POINTERS* ExceptionInfo)`<br>`{`<br>``<br>``<br>```if``(ExceptionInfo->ExceptionRecord->ExceptionCode == EXCEPTION_SINGLE_STEP)`<br>```{`<br>```if``(ExceptionInfo->ContextRecord->Eip == (``DWORD64``)&BreakOnSyscall)`<br>```{`<br>``<br>``<br>```ntSyscallStub = CustomGetProc((``UINT64``)hNtdll, (``char``*)*(``DWORD``*)(ExceptionInfo->ContextRecord->Esp + 4));`<br>```// Move breakpoint to the NTAPI function;`<br>```ExceptionInfo->ContextRecord->Dr0 = ntSyscallStub ;`<br>``<br>```}`<br>```else``if``(ExceptionInfo->ContextRecord->Eip == (``DWORD64``)ntSyscallStub )`<br>```{`<br>``<br>``<br>```ExceptionInfo->ContextRecord->Esp -= 0x54;`<br>``<br>``<br>``<br>```// Copy the stack arguments from the original stack`<br>```for``(``size_t``i = 0; i < STACK_ARGS_LENGTH; i++)`<br>```{`<br>```const``size_t``offset = i * STACK_ARGS_LENGTH;`<br>```*(``DWORD64``*)(ExceptionInfo->ContextRecord->Esp + offset) = *(``DWORD64``*)(ExceptionInfo->ContextRecord->Esp + offset + 0x54);`<br>``<br>```}`<br>`//Pushing Original return address after last argument`<br>```*(``DWORD``*)(ExceptionInfo->ContextRecord->Esp + (4 * STACK_ARGS_LENGTH + 8)) = *(``DWORD``*)(ExceptionInfo->ContextRecord->Esp);`<br>```//Pushing Gadget address on top`<br>```*(``DWORD``*)(ExceptionInfo->ContextRecord->Esp) = retGadgetAddress;`<br>`//Simulating call edx by pushing gadget once more and updating the ESP`<br>`*(``DWORD``*)(ExceptionInfo->ContextRecord->Esp - 4) = retGadgetAddress;`<br>```ExceptionInfo->ContextRecord->Esp = ExceptionInfo->ContextRecord->Esp - 4;`<br>``<br>```DWORD_PTR``gate = NULL;`<br>```__asm`<br>```{`<br>```mov eax, dword ptr fs : [0xBB + 0x5]`<br>```mov gate, eax`<br>``<br>```}``//assembly to retrieve Heavens Gate`<br>```//SSN of NtAllocateVirtualMemory on my Windows`<br>```ExceptionInfo->ContextRecord->Eax = 0x18;`<br>```//Direct call to gate`<br>```ExceptionInfo->ContextRecord->Eip = gate;`<br>``<br>```ExceptionInfo->ContextRecord->Dr0 = (``UINT64``)&BreakOnSyscall;`<br>```}`<br>```return``EXCEPTION_CONTINUE_EXECUTION;`<br>``<br>```}`<br>``<br>```return``EXCEPTION_CONTINUE_SEARCH;`<br>``<br>`}` |

[Offensive Coding](https://sabotagesec.com/category/offensive-coding/)

[cyber security](https://sabotagesec.com/tag/cyber-security/), [Malware](https://sabotagesec.com/tag/malware/), [redteam](https://sabotagesec.com/tag/redteam/), [spoofing](https://sabotagesec.com/tag/spoofing/), [stack](https://sabotagesec.com/tag/stack/), [Windows](https://sabotagesec.com/tag/windows/)

### Leave a Reply [Cancel reply](https://sabotagesec.com/breakpoints-heavens-gate-and-stack/\#respond)

Your email address will not be published.Required fields are marked \*

Comment \*

Name \*

Email \*

Website

Save my name, email, and website in this browser for the next time I comment.