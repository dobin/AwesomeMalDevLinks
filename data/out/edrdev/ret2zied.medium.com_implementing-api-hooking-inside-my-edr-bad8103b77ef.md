# https://ret2zied.medium.com/implementing-api-hooking-inside-my-edr-bad8103b77ef

[Sitemap](https://ret2zied.medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fret2zied.medium.com%2Fimplementing-api-hooking-inside-my-edr-bad8103b77ef&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=---top_nav_layout_nav-----------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fret2zied.medium.com%2Fimplementing-api-hooking-inside-my-edr-bad8103b77ef&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page---header_tags--bad8103b77ef---------------------------------------)

[Cpp](https://medium.com/tag/cpp?source=post_page---header_tags--bad8103b77ef---------------------------------------)

[Edr](https://medium.com/tag/edr?source=post_page---header_tags--bad8103b77ef---------------------------------------)

[Api Hooking](https://medium.com/tag/api-hooking?source=post_page---header_tags--bad8103b77ef---------------------------------------)

[Reverse Engineering](https://medium.com/tag/reverse-engineering?source=post_page---header_tags--bad8103b77ef---------------------------------------)

# Implementing API Hooking Inside My EDR

## From injection timing and loader locks to intercepting `LdrLoadDll`

[![Zied Sayari](https://miro.medium.com/v2/resize:fill:32:32/1*ebqCw76ljoCrLdWQV757QQ.jpeg)](https://ret2zied.medium.com/?source=post_page---byline--bad8103b77ef---------------------------------------)

[Zied Sayari](https://ret2zied.medium.com/?source=post_page---byline--bad8103b77ef---------------------------------------)

Follow

9 min read

·

5 days ago

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dbad8103b77ef&operation=register&redirect=https%3A%2F%2Fret2zied.medium.com%2Fimplementing-api-hooking-inside-my-edr-bad8103b77ef&source=---header_actions--bad8103b77ef---------------------post_audio_button------------------)

Share

> In this post, I will be sharing my journey thru implementing API hooking inside my custom EDR which started simple since I already had experience with hooking as a concept from game hacking such as hooking `SwapBuffers` function from openGL library to create and ESP. So I thought this will be easy! But then started going deeper in the windows internals rabbit hole to find myself racing with the spawned program to hook the API function before the spawned program calls it.

## Hook Definition

It is the process of patching a specific place in the target function with a jump instruction to a custom function.

This custom function can do anything such as logging function parameters.

Then pass the flow back to the original function.

## When to use

It is like rewriting the function but dynamically during runtime since you do not have access to the source code. You can modify function behavior by performing a jump somewhere in memory that you control such a `DLL` perform your actions then continue the original function flow.

Example: lets you this function `BYTE * encrypt(BYTE *KEY, char * DATA);`

What you want to do is dump the key during runtime since on every run the key changes.

Here you can create a hooked function to jump to your custom code that can look like this:

```
BYTE *encrypt(BYTE *KEY, char * DATA){
  // jmp to hooked_encrypt()
  // trampoline address
  // ....
}

BYTE *hooked_encrypt(BYTE *KEY, char * DATA){
	printf("Data before encryption %s", DATA);
	return (func_ptr_encrypt)trampoline_address(BYTE *KEY, char * DATA);
}
// Its not that simple but this is a high level view
```

## Implementation in my EDR

There is a couple of things I need to do:

- get the RVA of the function I want to hook
- Hook the Function
- Implement the hooked function

## Getting the RVA

Using a two stage `ReadProcessMemory` to avoid errors

when I tried to read the whole dll from remote process it failed with error `ERROR_PARTIAL_COPY` After I researched this error, I came up with the conclusion that the DLL is not in one page and the function is reading into the next committed page.

So I came up with a work around to split it to two calls to `ReadProcessMemory` instead:

- read header to get to the `IMAGE_DIRECTORY_ENTRY_EXPORT`
- read `export_directory` starting from `base_addr + export_rva`
- accessing everything relative from the `export_region_buffer` by calculating the raw RVA using formula `export_region_buffer + (target_rva - export_rva)`.

verify we got the correct RVA via debugger

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*6IL37BzZKhrwYJiiPU7T0w.png)

take address of `messageBoxA` sub the base address from it

![](https://miro.medium.com/v2/resize:fit:338/1*MwsRoudhn9Uxfp7rHS1NpQ.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:381/1*QzfYY5doVc5BbuekNXaUmQ.png)

Done.

Reading instruction from the function

![](https://miro.medium.com/v2/resize:fit:420/1*Bbpvzaq8o64IB-KaIDxUIg.png)

Now we can start hooking.

## My thoughts

After I implemented the EAT parser I had problem which is I need my hooked function to be inside the program that my EDR spawns.

I had two solutions:

- write my hooked function as shellcode then remotely allocate it inside the target process
- create a DLL that hold all my hooking functions

I went with creating a DLL agent because this will allow my edr to be more expandable and flexible and easier to write; I wont be hooking one function as malware use multiple APIs to perform multiple actions so the first approach will be un logical to go with unless this edr is created as a big POC which is not.

## Setting up the DLL in my enviroment

First I added a new project and selected the template to be DLL now my solution pane looks like this:

![](https://miro.medium.com/v2/resize:fit:339/1*9lkXVwjDaFp56js1X0OB7g.png)

Now I will setup build dependency

![](https://miro.medium.com/v2/resize:fit:571/1*6kcA2b3a0b7toPC0Y6BumQ.png)

Making my EDR depend on the agent

![](https://miro.medium.com/v2/resize:fit:506/1*v_7SwjwnsEu8VLdWGqGElQ.png)

Adding a post build event to copy dll to the public dir where it is can be reached by the spawned process.

![](https://miro.medium.com/v2/resize:fit:697/1*PFRLZrhJzgTobWM8wF9B1w.png)

## Communication between the Process and DLL

I used one-way pipes too send Logs from the Agent DLL to the EDR because I needed a way to send info such as function parameters to my EDR.

## x64 trampoline

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*QAcNGTP93jQlGGufH0Y76g.png)

## How The Hook Works

Lets look first on the `MessageBoxA` assembly

## Before Hooking

we can overwrite 7 bytes only since the next instruction is a relative one which need special modifying to be executed correctly inside our trampoline (will touch on this later in this post).

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*jyNN5h1g9UNkx9N-6uPHmw.png)

For now I will keep it simple. Someone will ask how can you use 7 bytes only to jump to your relay function in x64 arch since absolute jumps must be at least 13 bytes. The trick is to look for a free memory region that is close enough to our target function to allocate and then use a relative jump `0xE9` to jump to it.

## Steps

My `setup_hook` actions:

- Build the trampoline
- Setup the relay address
- From `relay_function` jump to the `hook_payload`
- `hook_payload` execute then jump to trampoline
- Trampoline execute stolen bytes then jump back to original function after the relative jump instruction
- Patch the function to do a relative jump to the `relay_function` relative address

## building the trampoline

Function `setup_trampoline` actions:

- Copy the stolen bytes from the original function and that `stolen_bytes_regoin`
- Write an absolute jump to the `trampoline_jmp_back_regoin` that jumps to instruction after the stolen bytes (inside the original function)
- Calculate the size of the trampoline using `absolute_table_regoin - start_of_trampoline_address` and return it as `UINT32`

## Relay Address

This is where the original function jump:

- Perform an absolute jump to `hook_payload`

## Hook Payload

This where our custom logic is written:

- Execute your the code you want
- Return to trampoline

## Trampoline

This is our safe net to ensure the program does not crash:

- By first executing the overwritten bytes
- Perform an absolute jump to `original_function_address + stolen_bytes_size`

## Patch the original function

Now Since everything is ready we can overwrite the first bytes of the original function with our `relay_address`

## Get Zied Sayari’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

Note: always be sure that the bytes you steal them fully do not half steal bytes because that will corrupt the function and crash. Even if you need 5 bytes only you need to look at the assembly and take the whole instruction.

Also be carful from relative instructions these type of instructions cant be copied directly they need to be modified.

## After My Hook

Our original function will look like this after we write the relative jump patch.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*r-XM31kaGex6qWx_t7gk5g.png)

## Problem 1

When I got my hook working code worked. I face a problem which is how do I integrate it into my EDR.

First I created a function called `inject_agent_dll`. This was not the problem. The problem was, when should I inject my agent inside my monitor loop.

I had 3 places:

- on the `CREATE_PROCESS_DEBUG_EVENT`
- on the `LOAD_DLL_DEBUG_EVENT` when the `user32.dll` is loaded

## on the `CREATE_PROCESS_DEBUG_EVENT`

My goal was to catch everything so this was my first approach and the logical one. I also added a `CREATE_SUSPENDED` flag.

When this event is caught the system loader did not finish it’s job yet. While `inject_agent_dll` function is waiting for the system loader to finish to call `CreateRemoteThread`. system loader will never finish because the process is suspended. **DEADLOCK**

## on the `LOAD_DLL_DEBUG_EVENT`

I tried another approach where I waited until the `user32.dll` to be loaded before injecting because injecting before it will fail silently since `agent.dll` call:

```
get_win_api_func_addr("user32.dll", "MessageBoxA");
// this call HMODULE hMod = GetModuleHandleA(lib_name);
// which will fail because the library is not loaded yet
```

So I needed to wait for `user32.dll` to be loaded. But I could not wait until it is too late and the call to `MessageBoxA` is already executed by the program then my EDR is USELESS.

When I implemented this there was a coin flip some times the call is hooked sometimes not. I researched this and it turns out there was a **race condition** where if my agent is injected a `ms` early my agent fail silently and if a `ms` late I miss the call. Its a coordination issue since my agent is running on a separate thread.

## My Solution

I realized that I needed a way to know exactly when `user32.dll` is loaded before the spawned program so I can win the race and always hook the function before the program calls it.

After some research I found a function called `LdrLoadDll` inside `ntdll.dll` which is the lowest you can get in the user-land, it is called whenever any high level function that load a DLL is called. Such as `LoadLibraryA`, `LoadLibraryExA` ... etc

So what if I hook this function but this time I will perform my hook payload after the function complete, This is how powerful hooking is!!!

### LdrLoadDll

This is the function signature:

```
LdrLoadDll(
_In_opt_ PCWSTR DllPath,
_In_opt_ PULONG DllCharacteristics,
_In_ PCUNICODE_STRING DllName,
_Out_ PVOID *DllHandle );
```

```
// What we need is the last two parameters
// DllName to when user32.dll is load
// DllHandle to get HMODULE that is needed to find the MessageBoxA address
```

### Steps

- Log loaded library anyway
- Hook `LdrLoadDll`
- call trampoline to fill `DllHandle`
- compare `DllName->buffer` with `User32.dll`
- if match, install hook into `MessageBoxA`

Now I can reliably hook `MessageBoxA` before the spawned program.

### When Do I Inject Agent

Now I can Inject on the first `LOAD_DLL_DEBUG_EVENT` meaning a bigger visibility but of course I want have full visibility such static imports, that is where I will consider making a kernal-mode EDR.

**Note**: The agent DllMain need to be like this:

```
BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    if (ul_reason_for_call == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hModule);
```

```
        // This needs to be syncr
        agent_main();
    }
    return TRUE;
}
```

To execute in the same thread and stop spawned program execution.

## Problem 2

This was a simple problem but hard one to debug my absolute jump was using register `r14` which was fine when hooking `MessageBoxA` but when I hooked `LdrLoadDll` this was not the case at all.

I kept getting ACCESS\_VIOLATION exceptions on this instruction:

```
xchg rcx,qword ptr [r14+rdi*8+139B20h]
// look at the r14 being used
```

from the error you can see `r14` is used to access data in some function in the call stack. Program think this register did not change but our hook changed it. When I saw this instruction I immediately knew the reason of my 3 hours suffering. Using a non-volatile (callee-saved) register is BAD (remember that).

Stick with These registers, `RAX`, `R10`, `R11`. Because `RCX`, `RDX`, `R8`, and `R9` contains function parameters and you do not want to miss with that either.

Why I used `r14`, I was trying to use new registers and get out of my comfort zone but that always cost something.

## Testing

I will use The custom x64 shellcode I developed months ago which dynamically resolve and call `MessageBoxA` on the fly

## This is the normal Behavior

As we can see Just a `MessageBoxA` popup.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*F0KIU1SYDPKzn5oxnj1cSA.png)

## Under My EDR

The EDR agent caught the dynamically loaded DLLs and when `MessageBoxA` is called the original parameters are logged and then changed to custom parameters:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*RvEupuP0PJ6ck3eGqEyBaw.png)

You can think of this as simple POC of how an EDR hook API calls and see what parameters are used not only see them but also modify them to stop compromise.

Ex. if a call to a `CreateRemoteThread` is hooked the EDR can investigate the `lpStartAddress` to see if there is a malicious shellcode in there and fill it with NOPS if it is.

## Resources

My EDR github repo:

[https://github.com/zyv2/My\_Custom\_EDR](https://github.com/zyv2/My_Custom_EDR)

Special thanks to this guy

[https://kylehalladay.com/blog/2020/11/13/Hooking-By-Example.html?source=post\_page-----22d9bc461db8---------------------------------------](https://kylehalladay.com/blog/2020/11/13/Hooking-By-Example.html)

LdrLoadDll

[https://ntdoc.m417z.com/ldrloaddll](https://ntdoc.m417z.com/ldrloaddll)

Register and calling conventions

[https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170)

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page---footer_tags--bad8103b77ef---------------------------------------)

[Cpp](https://medium.com/tag/cpp?source=post_page---footer_tags--bad8103b77ef---------------------------------------)

[Edr](https://medium.com/tag/edr?source=post_page---footer_tags--bad8103b77ef---------------------------------------)

[Api Hooking](https://medium.com/tag/api-hooking?source=post_page---footer_tags--bad8103b77ef---------------------------------------)

[Reverse Engineering](https://medium.com/tag/reverse-engineering?source=post_page---footer_tags--bad8103b77ef---------------------------------------)

[![Zied Sayari](https://miro.medium.com/v2/resize:fill:48:48/1*ebqCw76ljoCrLdWQV757QQ.jpeg)](https://ret2zied.medium.com/?source=post_page---post_author_info--bad8103b77ef---------------------------------------)

[![Zied Sayari](https://miro.medium.com/v2/resize:fill:64:64/1*ebqCw76ljoCrLdWQV757QQ.jpeg)](https://ret2zied.medium.com/?source=post_page---post_author_info--bad8103b77ef---------------------------------------)

Follow

[**Written by Zied Sayari**](https://ret2zied.medium.com/?source=post_page---post_author_info--bad8103b77ef---------------------------------------)

[1 follower](https://ret2zied.medium.com/followers?source=post_page---post_author_info--bad8103b77ef---------------------------------------)

· [0 following](https://ret2zied.medium.com/following?source=post_page---post_author_info--bad8103b77ef---------------------------------------)

Security engineer & offensive dev. I build endpoint detection tools out of pure curiosity and break them for fun. Safe for your enterprise, dangerous in a lab.

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----bad8103b77ef---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----bad8103b77ef---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----bad8103b77ef---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----bad8103b77ef---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----bad8103b77ef---------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----bad8103b77ef---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----bad8103b77ef---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----bad8103b77ef---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----bad8103b77ef---------------------------------------)