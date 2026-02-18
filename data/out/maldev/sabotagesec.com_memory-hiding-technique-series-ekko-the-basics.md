# https://sabotagesec.com/memory-hiding-technique-series-ekko-the-basics/

[Skip to content](https://sabotagesec.com/memory-hiding-technique-series-ekko-the-basics/#wp--skip-link--target)

## Memory Hiding Technique Series: Ekko – The basics

![\"Spot](https://www.rd.com/wp-content/uploads/2018/06/shutterstock_7400092.jpg?resize=700,466\%22)

## **Introduction**

In previous [post](https://sabotagesec.com/%22https://offensivecraft.wordpress.com/2022/11/28/memory-hiding-technique-series-part-0x1//%22), we covered Gargoyle memory hiding technique, this time we will look at another technique called [Ekko](https://github.com/Cracked5pider/Ekko/%22), a POC created by [C5pider](https://sabotagesec.com/%22https://twitter.com/C5pider?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor\%22) which is actually based on [Austin Hudson](https://sabotagesec.com/%22https://twitter.com/ilove2pwn_/%22)\\’s [findings](https://sabotagesec.com/%22https://web.archive.org/web/20220505170100/https://suspicious.actor/2022/05/05/mdsec-nighthawk-study.html/%22) from reversing MDSec NightHawk payload.

The implementation of the Ekko is very straightforward.

- There is a timer for synchronization.
- The **_Asynchronous Procedure Call_** is utilized to invoke **_NtContinue_** to call rest of the APIs used via context switching.
- Call to VirtualProtect alters the memory protections.
- Target memory is encrypted/decrypted using **_SysFunc032_** api.
- Then sleeps for sometime.
- WaitForSingleObject waits on an Event object to finally make an exit

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/up-12.png)

Before we jump right into internals of Ekko, we need to understand core concept used in its development – the \\” **_contexts_**\\” and **_NtContinue_** API. Next section will give you a very clear idea about \\”Context Oriented Programming\\”.

## **context oriented programming**

To be honest, there is no such thing as \\” **_Context Oriented Programming_**\\”, it is something I personally call a code that looks similar to one below. Using **_NtContinue_** and a **_CONTEXT_** structure we can control the flow of execution and this style reminds me of the Return Oriented Programming hence the name Context Oriented Programming. Below code pops up a message box with a text \\”Hi from Oscar\\”. Boring isn\\’t? There is more to this code than meets the eye! LETS DIVE IN!

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-17.png?w=796\%22)

## **The context**

At the hardware level, every running program can be represented by contents residing in the registers and segments. For a processor this forms a context and besides register and segment values, it can also contain some additional data required by the OS for various internal operations. Windows has a special structure called [CONTEXT](https://sabotagesec.com/%22https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-context/%22) structure to keep track of all the values in processor specific registers and segments, as mentioned before it can store additional data like debug control, exception handling etc. Using CONTEXT structure it is very easy to manipulate the values in the processor registers thereby controlling the flow of execution. We are interested only in four members in the CONTEXT:

- Rip
- Rcx
- Rdx
- R8
- R9
- Rsp

Our program is x64 that is why we chose above registers especially RCX/RDX/R8/R9 \[x64 calling convention\]. We need RIP to achieve code execution, RSP for stack setting and the rest for argument passing.

What is the deal with NtContinue in the code?

The [NtContinue](https://sabotagesec.com/%22http://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented%20Functions%2FNT%20Objects%2FThread%2FNtContinue.html\%22) api is an undocumented function in ntdll.dll. This function takes a pointer to CONTEXT structure as the input argument. As the name suggests, if we provide a valid CONTEXT to the function, it will set the processor context with respective values present in the structure. In other words we can execute any code \[RIP\] and pass data to the code through RCX/RDX/R8/R9 . We can call any api that takes arguments not more than four. Since we don\\’t have much control over the stack , APIs that need more than 4 parameters cannot be used in this scenario.\[Thats what I believe! Correct me if I am wrong\].

What is the plan?

Our objective is to call **_MessageBox_** api and pass \\”Hi form Oscar\\” as _lpText_, this can be done by following steps mentioned below:

- Declare CONTEXT structure called **_MsgBox_**
- Retrieve the current context via RtlCaptureContext in **_CtxThread_**.
- Copy the captured context in **_CtxThread_** to _**MsgBox**_ CONTEXT.
- Replace the RIP with address of **_MessageBox()_**
- Replace the RDX with address of lpText
- Replace RCX/R8/R9 with NULL
- Finally call NtContinue by passing **_MsgBox_** CONTEXT to execute _**MessageBox**_ function.

## **devil is in the details** : Debugging

The instruction **MsgBox.Rsp -= 8** plays a crucial role in this program. Why is that so? To answer that we need to have a basic understanding of x64 stack. Lets not get lost in the x64 stack implementation details but point to take home is that both RSP and RBP are static in x64 stack implementation. During the execution of a function, the RSP will remain fixed, when another function is called then stack grows with 8byte increment ie \[RSP -8\]. Below image shows the RSP and RBP value of main function of our program. So during the entire execution of main, RSP will be restored to this value when nested functions finally return to the main.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/screenshot-2022-11-29-024905.png?w=186\%22)

So why does our code have this statement **MsgBox.Rsp -= 8** ?

The answer lies in the implementation of RtlCaptureContext as shown in the image below. The RCX holds our CtxThread CONTEXT structure, below code is saving register values into CtxThread structure. The highlighted code is responsible for capturing the RSP value. Interestingly like the rest of the code that simply moves the value from respective registers to the context structure, RSP is not captured in similar manner, instead value RSP+10 is moved to RAX then to our CtxThread. This is because RtlCapture is smart enough to offset the change made to stack when it is called by the main. So CtxThread.Rsp will be pointing to 14E8C0 as shown in the previous image.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/screenshot-2022-11-29-025141.png?w=784\%22)

If we call our MessageBox api with Rsp == 14E8C0, we will get an exception as shown below. Because the stack is messed up and MessageBox api will try to access some arbitrary address on stack. We need to perform \[MsgBox.Rsp -=8\] to make room for MessageBox call on stack as mentioned before.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-19.png?w=535\%22)

Once our stack is all set, our program pops a message box as shown in the image below.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/11/image-18.png?w=125\%22)

## Conclusion

In the next post, we will see how Ekko utilizes APCs along with NtContinue and contexts to invoke various functions needed to perform memory hiding. Also we will discuss about detection engineering to identify Ekko like malware active in the memory.

[Offensive Coding](https://sabotagesec.com/category/offensive-coding/)

[C#](https://sabotagesec.com/tag/c/), [Malware](https://sabotagesec.com/tag/malware/), [NightHawk](https://sabotagesec.com/tag/nighthawk/), [redteam](https://sabotagesec.com/tag/redteam/)

### Leave a Reply [Cancel reply](https://sabotagesec.com/memory-hiding-technique-series-ekko-the-basics/\#respond)

Your email address will not be published.Required fields are marked \*

Comment \*

Name \*

Email \*

Website

Save my name, email, and website in this browser for the next time I comment.