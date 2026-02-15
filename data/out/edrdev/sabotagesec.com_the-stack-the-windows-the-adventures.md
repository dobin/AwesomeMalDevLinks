# https://sabotagesec.com/the-stack-the-windows-the-adventures/

[Skip to content](https://sabotagesec.com/the-stack-the-windows-the-adventures/#wp--skip-link--target)

## The Stack, The Windows & The Adventures

![\"\"](https://sabotagesec.com/wp-content/uploads/2023/03/image-9.png?w=479\%22)

## Introduction

This post is a \\”how-to\\” for writing Win32 code for performing a stackwalk on both x86 and x64 architectures and along the way we will learn the theory behind some of the concepts associated with the stack. In fact this is a quick note created for myself when I started working on designing a runtime anomaly detection using call stack as the telemetry for the data. I hope this will save a lot of googling!

Check out following posts to take a deep dive into stack internals.

- [x64 stack internals](https://sabotagesec.com/%22https://offensivecraft.wordpress.com/2023/02/11/the-stack-series-the-x64-stack//%22)
- [Return Address Spoofing](https://sabotagesec.com/%22https://offensivecraft.wordpress.com/2022/12/08/the-stack-series-return-address-spoofing-on-x64//%22)

## contexts & Wow64

Windows Wow64 API [set](https://sabotagesec.com/%22https://learn.microsoft.com/en-us/windows/win32/api/wow64apiset//%22) provides a lot functionalities to perform various operations on x86 address space from an x64 space. The function _IsWow64Process_ is very useful in identifying 32 bit processes running on x64 system. Process level operations can then be performed with ease and more flexibility, a decision can be made by calling this specific API and use appropriate x86 data structures to do something interesting (whatever that is!) from an x64 process.

![\"\"](https://sabotagesec.com/wp-content/uploads//2023/03/image.png)

Sometimes we need to capture a context of the running thread in events like error handling, state analysis to do something interesting like stack walk or even some of the win32 APIs expect contexts to be passed as input. For starters, a context is a snapshot of the CPU at a given time, context can be seen as a structure whose members are all available registers in the CPU and other architectural elements that make up the \\”state\\” of the system. Following two images show two types of CONTEXT structures supported by Windows, the \_WOW64\_CONTEXT structure reflects x86 system and \_CONTEXT structure reflects x64 one. We can pick one based on the architecture we are targeting in our application. It is evident from the images that both context structures are very much closely tied to its internal architectural details, hence these cannot be used interchangeably.

![\"\"](https://sabotagesec.com/wp-content/uploads/2023/03/image-1.png?w=862\%22)![\"\"](https://sabotagesec.com/wp-content/uploads/2023/03/image-2.png?w=580\%22)

Following APIs will help us to capture the context (not limited to this set):

- GetThreadContext
- Wow64GetThreadContext
- RtlCaptureContext

## stack walking using win32 api

## basic idea

I am not going to reiterate the working of stack and stack walking or tracing and its uses as I have already covered it in my previous posts and it has been a recurring theme in my recent posts.

If we are planning to do a stack trace then we don\\’t have to cook up our own code, Windows provides us with two elegant APIs to do it.

- **_StackWalk64_**
- **_StackWalk_**
- ..and a hidden gem **_RtlWalkFrameChain_** (not going to be covered in this post, explore this on your own 😉 )

Why it is always a good idea to use above APIs is we don\\’t have to worry about any architectural details of stack implementation, the API will take care of everything for us. These APIs **_StackWalk64_** and **_StackWalk_** need to be enclosed in an infinite loop, this functions will fail when they are done walking the last frame on the call stack. The code structure is shown below:

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9 | `do`<br>`{`<br>```if(StackWalkXX(...))`<br>```{`<br>```//Execution comes here after walking the last frame in the chain`<br>```break;`<br>```}`<br>```//do something interesting with the data obtained from stack walk`<br>`}while(1)` |

Note: Each iteration represents a stack frame in the call chain

Interestingly the output from the API is a \\” _stackframe_\\” represented by following structures:

- [STACKFRAME](https://sabotagesec.com/%22https://learn.microsoft.com/en-us/windows/win32/api/dbghelp/ns-dbghelp-stackframe/%22)
- STACKFRAME64

Refer to the documentation to learn more about the members and types.

## Initialization of STACKFRAME/STACKFRAME64

One very important step is initialization of **_STACKFRAME_** structures before calling the APIs. The context information retrieved from API like **_GetThreadContext_** needs to be used to initialize the internal members in **_STACKFRAME/STACKFRAME64_** required for the functioning of **_StackWalk/StackWalk64_** apis. Below images show the initialization step for x32 and x64 respectively.

![\"\"](https://sabotagesec.com/wp-content/uploads/2023/03/image-7.png?w=400\%22)![\"\"](https://sabotagesec.com/wp-content/uploads/2023/03/image-8.png?w=407\%22)

## x32 System

![\"\"](https://sabotagesec.com/wp-content/uploads/2023/03/image-3.png?w=688\%22)

Few things to keep in mind while using it:

- The first parameter should be **_IMAGE\_FILE\_MACHINE\_I386_** (0x014c)
- The input stackframe (4th parameter) must be of the type **_LPSTACKFRAME_**
- The 7th parameter **_FunctionTableAccessRoutine_** should be NULL, this is required for 64 systems only.
- The 8th parameter should be a pointer to the function **_SymGetModuleBase_**

Example

![\"\"](https://sabotagesec.com/wp-content/uploads/2023/03/image-6.png?w=1014\%22)

## x64 system

![\"\"](https://sabotagesec.com/wp-content/uploads/2023/03/image-4.png?w=687\%22)

- The first parameter should be **_IMAGE\_FILE\_MACHINE\_AMD64_** (0x8664)
- The input stackframe (4th parameter) must be of the type **_LPSTACKFRAME64_**
- The 7th parameter **_FunctionTableAccessRoutine_** should be pointer to **_SymFunctionTableAccess64_** function.
- The 8th parameter should be a pointer to the function **_SymGetModuleBase64_**

Example

![\"\"](https://sabotagesec.com/wp-content/uploads/2023/03/image-5.png?w=1024\%22)

## code examples from web

Code Samples

https://cpp.hotexamples.com/examples/-/-/StackWalk64/cpp-stackwalk64-function-examples.html

[Offensive Coding](https://sabotagesec.com/category/offensive-coding/)

[C#](https://sabotagesec.com/tag/c/), [stack](https://sabotagesec.com/tag/stack/), [win32](https://sabotagesec.com/tag/win32/), [Windows](https://sabotagesec.com/tag/windows/), [windows development](https://sabotagesec.com/tag/windows-development/)

### Leave a Reply [Cancel reply](https://sabotagesec.com/the-stack-the-windows-the-adventures/\#respond)

Your email address will not be published.Required fields are marked \*

Comment \*

Name \*

Email \*

Website

Save my name, email, and website in this browser for the next time I comment.