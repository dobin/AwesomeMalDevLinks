# https://sabotagesec.com/analysing-a-multi-stager-a-case-study-of-qbot/

[Skip to content](https://sabotagesec.com/analysing-a-multi-stager-a-case-study-of-qbot/#wp--skip-link--target)

## Analysing a Multi Stager : A case study of QBOT

## motivation

This is not going to be about QBOT analysis rather a quick \\”how-to\\” for analysing malwares that employ multiple stages in the infection chain. Recently, in my work, I got a sample (a mal pdf) for analysis, at the time I had no prior information and task was identification. Interestingly initial vector used to execute the sample involved iso images, JScript and VBS, finally I retrieved a DLL file that was saved on the disk as a txt file. After performing an in-depth analysis, I figured out that it was loading some other DLL and giving control to the _DllEntry_ of the new DLL! hmmm interesting. I retrieved the new DLL and started working on it. I saw two interesting(unusual) strings \\” _C:\\\INTERNAL\\\\_\_empty_\\” and \\” _SELF\_TEST\_1_\\”. I went ahead and googled the strings and found two reports one from [Uptycs](https://sabotagesec.com/%22https://www.uptycs.com/blog/qbot-reappears-now-leveraging-dll-side-loading-technique-to-bypass-detection-mechanisms/%22) and other from [Elastic](https://sabotagesec.com/%22https://www.elastic.co/security-labs/qbot-malware-analysis/%22) about Qbot analysis. Both of these reports were telling the same story and I had the same findings only difference was I had no idea it was QBOT (first time seeing one lol)

Now that is the backstory, the motivation for this post is something else, QBot is just another malware in the wild that has multiple stages in its infection chain. Analysing Qbot made me think – _How would one approach the issue of analysing a staging mechanism especially when the next stage happens inside a remote process which you are not debugging currently and resume the analysis process in the target process?_ Hence this post!

## QBot infection : An overview

- Qbot has three stages, first stage is initialisation, second stage is installation and final stage is for communication.
- In the initial phase, it tries to inject itself into remote process through process hollowing vector. The malware will initiate its second stage from the remote process. The entry point function in the target process will be changed to second stage code in the malware.
- Following are the binaries it uses to create the process to perform process hollowing.
  - _C:\\\Windows\\\SysWOW64\\\wermgr.exe_
  - _C:\\\Windows\\\SysWOW64\\\msra.exe_
  - _C:\\\Program Files (x86)\\\Internet Explorer\\\iexplore.exe_
- The first thing that second stage does is to corrupt the malware binary on the disk used in first stage.

This information is enough for us to perform analysis of the second stage.

## fun in jumping between procesesses

Before getting our hands dirty, I have to set some things straight.

- Debugger A : Its the debugger that has the unpacked Qbot dll and this is stage-I
- Debugger B : When stage-I creates target process in suspended state, we will attach a debugger to it for analysing stage-II.

I will go back and forth with these terms so don\\’t get confused! Without further ado lets dive in !

## **get that context**

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/1.png?w=665\%22)

- Since we already have a clear picture of what we are up against (Process hollowing), first thing comes to my mind is the **_GetThreadContext_** and its role in process hollowing. The reasoning behind that is quite simple, malware needs to redirect the execution in the new process to its code hence the _**CONTEXT**_!
- Our objective is very simple, find out about the new entry point in the process, so I know the way-out should be somewhere in the lines of code between **_GetThreadContext_** and _**ResumeThread**_.
- Put a breakpoint on **_GetThreadContext_** function in debugger A. As shown in the image above, QBot calls the api to make the EIP of the thread in target process to point to malware code. The malware creates the target process in suspended state before breakpoint hits, this is shown in the image below, in our case the target process is \\”wermgr.exe\\”. (NO BRAINER 😉 )

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/2.png?w=358\%22)

## **let the malware write**

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/3.png?w=675\%22)

- Further debugging the code line by line in debugger A, one interesting api call is **_ZwWriteVirtualMemory_** as shown in the image above. There is one call prior to this one which is _**NtProtextVirtualMemory**_ with memory protection constant of value **_0x04_** and target memory region is a memory location in target process OFCOURSE!
- Arguments passed to **_ZwWriteVirtualMemory_** api are shown below. the second argument is _BaseAddress_ where data in the buffer (third argument) is going to get written in.
- This is where things get interesting and fun! Since this memory location is in completely different process, we need to fire up a new debug session.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/zwwritevirtualmemory_args.png?w=337\%22)

## **new debug target**

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/4.png?w=617\%22)

- Start a new debugger session by attaching it to our target process (wermgr.exe), Now we have two active debuggers, one (A) is our initial loader and second one (B) is the target process used by the malware to initiate second stage.
- In the debugger B, go to the _BaseAddress_ used in **_ZwWriteVirtualMemory_** (loader process) seen in debugger A, in my case it is _**B954A0**_. As shown in the above image, the address points to _EntryPoint_ of _wermgr.exe_.
- Now this makes sense right? Ands we kind of know what it is trying to achieve here. Image below shows the legitimate _EntryPoint_ of the _wermgr.exe_ in debugger B.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/5.png?w=844\%22)

- After stepping over the **_ZwWriteVirtualMemory_** in debugger A, check the previous address ( _**B954A0**_) in debugger B. The change made to the code by the malware is highlighted in the image below. call **_wemgr.B95995_** is changed to **_jmp A16767_**.
- This is the key to analyse the second stage of QBOT initiated from within hollowed _wermgr.exe_.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/6.png?w=816\%22)

- In debugger B, lets check our new _EntryPoint_( _A16767_);image shown below. We are inside the QBOT code used in second stage operation.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/7.png?w=792\%22)

- Doing a quick memorymap lookup in debugger B for the above address would not hurt! Ofcourse the RWX is good indicator of maliciousness and gives hope to the researcher lol.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/8.png?w=890\%22)

- The process hacker output for the same(wermgr.exe). So this where the QBOT initially injected itself and made the necessary changes in _wermgr.exe_ to divert the execution to this RWX memory region. NICE!

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/9.png?w=750\%22)

- Go back to debugger A, continue debugging the code, you will end up seeing a call to _ResumeThread_ as shown below, step over it and go back to debugger B.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/image-6.png?w=847\%22)

Now you can analyse the second stage of the QBOT, you are inside _wermgr.exe_ and you have an active debug session. Make sure to take a snapshot of your VM, so you don\\’t have to go through all this all over again when you mess up something. 🙂

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/12/11.png?w=975\%22)

## ending note

- We started analysing one process, which is our DllEntry of QBOT (Stage-I)
- By understanding the malware code and vector used we retrieved new entrypoint.
- Using new address of entry we pivoted to the new process. Now we can go forward and analyse the second stage.
- This thinking and problem solving is not limited to QBOT but can be applied to any malware that employs multiple stages. Always get a complete picture of what you are up against in terms of code logic and vector.

[Offensive Coding](https://sabotagesec.com/category/offensive-coding/)

[c2](https://sabotagesec.com/tag/c2/), [CnC](https://sabotagesec.com/tag/cnc/), [cyber security](https://sabotagesec.com/tag/cyber-security/), [debugging](https://sabotagesec.com/tag/debugging/), [elastic](https://sabotagesec.com/tag/elastic/), [Malware](https://sabotagesec.com/tag/malware/), [malware analysis](https://sabotagesec.com/tag/malware-analysis/), [Qbot](https://sabotagesec.com/tag/qbot/), [reverse engineering](https://sabotagesec.com/tag/reverse-engineering/), [staging](https://sabotagesec.com/tag/staging/), [threat research](https://sabotagesec.com/tag/threat-research/), [uptycs](https://sabotagesec.com/tag/uptycs/), [Windows](https://sabotagesec.com/tag/windows/)

### Leave a Reply [Cancel reply](https://sabotagesec.com/analysing-a-multi-stager-a-case-study-of-qbot/\#respond)

Your email address will not be published.Required fields are marked \*

Comment \*

Name \*

Email \*

Website

Save my name, email, and website in this browser for the next time I comment.