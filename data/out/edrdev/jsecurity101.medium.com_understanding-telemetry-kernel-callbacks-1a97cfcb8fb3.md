# https://jsecurity101.medium.com/understanding-telemetry-kernel-callbacks-1a97cfcb8fb3

[Sitemap](https://jonny-johnson.medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Funderstanding-telemetry-kernel-callbacks-1a97cfcb8fb3&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Funderstanding-telemetry-kernel-callbacks-1a97cfcb8fb3&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Understanding Telemetry: Kernel Callbacks

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:32:32/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---byline--1a97cfcb8fb3---------------------------------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---byline--1a97cfcb8fb3---------------------------------------)

Follow

9 min read

·

Jun 12, 2023

7

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D1a97cfcb8fb3&operation=register&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Funderstanding-telemetry-kernel-callbacks-1a97cfcb8fb3&source=---header_actions--1a97cfcb8fb3---------------------post_audio_button------------------)

Share

## Introduction

I’ve published blogs around telemetry mechanisms like Event Tracing for Windows (ETW) in the [Uncovering Windows Events](https://medium.com/specter-ops-posts/uncovering-windows-events-b4b9db7eac54) series, but one mechanism I haven’t discussed yet are kernel callback functions. This was mentioned in one of the [DCP Live episodes](https://www.youtube.com/live/PPCaZRuzQDM?feature=share) that Jared Atkinson and I host on Mondays so I figured a write-up would help listeners (or people in general) better understand what kernel callback functions are and how vendors leverage them to get insight into activity.

In my opinion, not only is this topic super cool but it’s also practical for anyone that wants to know how to bypass EDR, understand how EDR/AV are exposing telemetry, and also know where your EDRs can obtain telemetry you might want in the future.

## Kernel Callback Functions

In simple terms, a callback routine is just a function that isn’t directly called by the developer. Rather, some other component invokes the function whenever a specific event occurs. In the case of kernel callback routines, these events may be process creation, obtaining a handle to a process/thread, creating a thread, setting a registry key, or other activities defined by Microsoft, and the kernel itself calls the registered callback functions inside of the loaded driver(s).

After implementing their callback routine in their driver, the developer has to register the function with the operating system. Microsoft provides a variety of functions that allow for callback to be registered that are commonly seen in AVs and EDRs:

- [PsSetCreateProcessNotifyRoutine](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutine)/ [PsSetCreateProcessNotifyRoutineEx](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex)/ [PsSetCreateProcessNotifyRoutineEx2](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreateprocessnotifyroutineex2): Registers a callback that collects process creation/deletion events
- [PsSetCreateThreadNotifyRoutine](http://pssetcreatethreadnotifyroutine/)/ [PsSetCreateThreadNotifyRoutineEx](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetcreatethreadnotifyroutineex): Registers a callback that collects thread creation/deletion events
- [PsSetLoadImageNotifyRoutine](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetloadimagenotifyroutine)/ [PsSetLoadImageNotifyRoutineEx](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-pssetloadimagenotifyroutineex): Registers a callback that collects when an image is loaded/mapped into memory
- [ObRegisterCallbacks](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-obregistercallbacks): Registers a pre/post-operation callback that information when a process, thread, or desktop handle is opened or duplicated.
- [CmRegisterCallback](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-cmregistercallback)/ [CmRegisterCallbackEx](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-cmregistercallbackex): Registers a callback that receives pre/post operation information about registry actions. The full list of events can be found [here](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ne-wdm-_reg_notify_class).

Let’s walk through one of these routines and watch how it works from registration of the callback to triggering the callback. For this post, we will look at a process creation callback that is registered via the ObRegisterCallbacks function.

## Process Handle Requests

### Registration

When a driver wants to leverage a callback to obtain information about process, thread, or desktop object handle requests, whether they be handle duplication or creation events, they register that callback through [ObRegisterCallbacks](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-obregistercallbacks).The first parameter that is passed into ObRegisterCallbacks is a pointer to the [OB\_CALLBACK\_REGISTRATION](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_ob_callback_registration) structure:

```
typedef struct _OB_CALLBACK_REGISTRATION {
  USHORT                    Version;
  USHORT                    OperationRegistrationCount;
  UNICODE_STRING            Altitude;
  PVOID                     RegistrationContext;
  OB_OPERATION_REGISTRATION *OperationRegistration;
} OB_CALLBACK_REGISTRATION, *POB_CALLBACK_REGISTRATION;
```

This structure holds information about the object callback version, the callback’s altitude value, and, most importantly, a pointer to another structure — [OB\_OPERATION\_REGISTRATION](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_ob_operation_registration):

```
typedef struct _OB_OPERATION_REGISTRATION {
  POBJECT_TYPE                *ObjectType;
  OB_OPERATION                Operations;
  POB_PRE_OPERATION_CALLBACK  PreOperation;
  POB_POST_OPERATION_CALLBACK PostOperation;
} OB_OPERATION_REGISTRATION, *POB_OPERATION_REGISTRATION;
```

This structure holds information about the object type (i.e., process, threads, and desktop) the callback is registered for, what type of operation the callbacks will trigger on (handle create or duplicate), and the pre/post operation callback routines. When registering callbacks, these members are filled out and passed into ObRegisterCallbacks to register with the system. At face value it’s as easy as that. However; there is more being done behind the scenes. Every object is backed by an OBJECT\_TYPE structure and the last member of that structure is called the CallbackList, which is a LIST\_ENTRY (linked list) of CALLBACK\_ENTRY\_ITEM structures, more on this later. ObRegisterCallbacks is going to make a call to ObpInsertCallbackByAltitude which will iterate through the OBJECT\_TYPE’s CallbackList member (a linked list) to see if there are any other callbacks that are registered under the same altitude. Per this [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/load-order-groups-and-altitudes-for-minifilter-drivers) 2 drivers can not have the same altitude.

If there isn’t a callback already registered with that altitude specified, it will insert that callback into the OBJECT\_TYPE’s Callback list.

### Notification

First, let’s take a look into the pre-post operation callbacks:

```
IRQL_requires_max_(APC_LEVEL)
OB_PREOP_CALLBACK_STATUS PreProcessHandleCallback(PVOID RegistrationContext, POB_PRE_OPERATION_INFORMATION OperationInformation) {
 PAGED_CODE();
 UNREFERENCED_PARAMETER(RegistrationContext);
 UNREFERENCED_PARAMETER(OperationInformation);

 if (OperationInformation->Operation == OB_OPERATION_HANDLE_CREATE) {
  PEPROCESS openedProcess = (PEPROCESS)OperationInformation->Object;
  HANDLE targetPID = PsGetProcessId(openedProcess);
  HANDLE sourcePID = PsGetCurrentProcessId();

  if (targetPID == (HANDLE)2972 && sourcePID  == (HANDLE)9084)  {
   if (OperationInformation->Parameters->CreateHandleInformation.OriginalDesiredAccess == PROCESS_ALL_ACCESS) {
    OperationInformation->Parameters->CreateHandleInformation.DesiredAccess = 0x1000;
    DbgPrint("Changed rights from PROCESS_ALL_ACCESS to PROCESS_QUERY_LIMITED_ACCESS\n");
   }

  }
 }

 return OB_PREOP_SUCCESS;
}

_IRQL_requires_max_(APC_LEVEL)
void PostProcessHandleCallback(PVOID RegistrationContext, POB_POST_OPERATION_INFORMATION OperationInformation) {
 PAGED_CODE();
 UNREFERENCED_PARAMETER(RegistrationContext);
 UNREFERENCED_PARAMETER(OperationInformation);

 ACCESS_MASK AccessRights = OperationInformation->Parameters->CreateHandleInformation.GrantedAccess;

 if (AccessRights != 0x0) {
  if (OperationInformation->Operation == OB_OPERATION_HANDLE_CREATE) {

   PEPROCESS openedProcess = (PEPROCESS)OperationInformation->Object;
   HANDLE targetPID = PsGetProcessId(openedProcess);
   HANDLE sourcePID = PsGetCurrentProcessId();

   if (targetPID == sourcePID) {
    DbgPrint("Process %d created a handle to itself with access rights %d\n", sourcePID, AccessRights);
   }
   else {
    DbgPrint("Process %d created a handle to process %d with access rights %d\n", sourcePID, targetPID, AccessRights);
   }

  }
 }
}
```

As you can see, these are very simple functions. PreProcessHandleCallback will get information about the request and if ProcessId 9084 requests an ALL\_ACCESS handle to 2972, it will modify that request to PROCESS\_QUERY\_LIMITED\_ACCESS:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*xi5rSD9TBGupTx7BSeQclA.png)

It is important to note, PreProcessHandleCallback isn’t performing the operation access check, this is handled by the security reference monitor (SRM) via checks from [SeAccessCheck](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-seaccesscheck) and [SePrivilegeCheck](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-seprivilegecheck). The pre-operation callback is modifying the request after it has gone to the SRM. So say that a request was made to obtain a handle and its access was denied, the pre/post callbacks would never be called. Pre-operation callbacks can not outright deny a handle, but they can modify the access the callee has or strip the handle completely of all rights. Theoretically say if you didn’t want a callee to have [DUPLICATE\_HANDLE rights to LSASS](https://medium.com/@jsecurity101/bypassing-access-mask-auditing-strategies-480fb641c158), then when the request is made those rights could be stripped from the handle through the pre-callback.

The post-callback in this POC is very simple, as it will just print the handle requests out:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ikyAV9DzN83x00SzWE-Dgw.png)

This is, in my opinion, really cool to monitor because you can see that a lot of processes obtain handles to themselves, which from a security perspective is how useful to an analyst? You also see common rights that are requested by certain processes, which is useful whether you’re trying to get a better understanding of internals as a whole or just a baseline process handle requests.

Now that we have seen how callbacks for process handle creation events can be registered and we have looked at the actual callbacks themselves you might be asking the question how/when do these callbacks trigger.

Let’s say we have two processes — ProcessA and ProcessB. ProcessA wants to get a handle to ProcessB. ProcessA calls OpenProcess, which internally calls ntdll!NtOpenProcess, that in turn executes a syscall, transitioninging control into the kernel to execute nt!NtOpenProcess. In kernel mode, nt!NtOpenProcess calls nt!ObpCreateHandle by way of nt!ObOpenObjectByPointer. Inside of ObpCreateHandle are two functions that relate to the pre/post-operation callbacks — ObpPreInterceptHandleCreate and ObpPostInterceptHandleCreate.

ObpPreInterceptHandleCreate is executed to check for any preoperation callbacks whereas ObpPostInterceptHandleCreate is for preoperation callbacks. They work similarly but not exactly the same. ObpPreInterceptHandleCreate calls ObpCallPreOperationCallbacks checks to see if there are any pre-operation callbacks for the handle create action, allows the preoperation callback to modify the rights returned by the handle and then moves on. Which later, right before the handle is returned to ProcessA, ObpPostInterceptHandleCreate calls ObpCallPostOperationCallbacks to allow a callback to log this action.

## Get Jonathan Johnson’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Here is a diagram that I made to help me understand this process:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*cUFOmBfIEhnF5kexH8LMjQ.png)

### Identifying Callbacks

There are a couple ways you could go and identify different callbacks running on the system:

1. Winobjex by hfiref0x

Under Extras -> System Callbacks, Winobjex will showcase what callbacks are registered and the driver that registered them:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*NGjVjGvS2raTKgoomPLVlg.png)

You also get the function address for the callback, so you could go into WinDbg and set a breakpoint if you want to perform further analysis:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*MFmTyZbxyti3PovLH0EtjQ.png)

[2\. TelemetrySourcer](https://github.com/jthuraisamy/TelemetrySourcerer) by [Jackson\_T](https://twitter.com/Jackson_T)

This tool is cool because it will find callbacks that are registered and then leverage a driver to unregister those callbacks. I was going to explain how it does this but it seems the code is very similar to mimikatz, which Matt Hand already breaks down well [here](https://posts.specterops.io/mimidrv-in-depth-4d273d19e148#:~:text=operation%20has%20completed.-,Mimidrv,-first%20searches%20for)

3\. WinDbg (Looking only for ProcessType callbacks)

Pull the address to the ProcessType:

```
dx @$ProcObj = *(nt!_OBJECT_TYPE **)&nt!PsProcessType
```

This will give us a variable called ProcObj which stored the process OBJECT\_TYPE structure, which looks like this:

```
@$ProcObj                 : 0xffff8088a14b1640 [Type: _OBJECT_TYPE *]
    [+0x000] TypeList         [Type: _LIST_ENTRY]
    [+0x010] Name             : "Process" [Type: _UNICODE_STRING]
    [+0x020] DefaultObject    : 0x0 [Type: void *]
    [+0x028] Index            : 0x7 [Type: unsigned char]
    [+0x02c] TotalNumberOfObjects : 0xb3 [Type: unsigned long]
    [+0x030] TotalNumberOfHandles : 0x884 [Type: unsigned long]
    [+0x034] HighWaterNumberOfObjects : 0xca [Type: unsigned long]
    [+0x038] HighWaterNumberOfHandles : 0x8d4 [Type: unsigned long]
    [+0x040] TypeInfo         [Type: _OBJECT_TYPE_INITIALIZER]
    [+0x0b8] TypeLock         [Type: _EX_PUSH_LOCK]
    [+0x0c0] Key              : 0x636f7250 [Type: unsigned long]
    [+0x0c8] CallbackList     [Type: _LIST_ENTRY]
```

Like mentioned before, handle callbacks are stored within the CallbackList which is a linked list full of addresses which point to an undocumented structure CALLBACK\_ENTRY\_ITEM:

```
struct _CALLBACK_ENTRY_ITEM
{
LIST_ENTRY EntryItemList;
OB_OPERATION Operations1;
OB_OPERATION Operations2;
PCALLBACK_ENTRY CallbackEntry;
POBJECT_TYPE ObjectType;
POB_PRE_OPERATION_CALLBACK PreOperation;
POB_POST_OPERATION_CALLBACK PostOperation;
};
```

We can pull the first and last in this list address via dx @$ProcObj->CallbackList

```
dx @$ProcObj->CallbackList
@$ProcObj->CallbackList                 [Type: _LIST_ENTRY]
    [+0x000] Flink            : 0xffffbd8706ff9230 [Type: _LIST_ENTRY *]
    [+0x008] Blink            : 0xffffbd8706c54140 [Type: _LIST_ENTRY *]
```

This gives us the first and last address of the linked list. I wrote a little JavaScript that will iterate through this list and print out callbacks:

```
"use strict";
function iterateList(firstAddress) {
    let listEntry = host.getModuleType("nt", "_LIST_ENTRY");
    let currentEntry = firstAddress

    const preoffset = 0x028;
    const postoffset = 0x030;
    let blink = host.createTypedObject(firstAddress, listEntry).Blink;
    host.diagnostics.debugLog(`Blink address: ${blink.address.toString(16)}\n`);
    while (currentEntry.toString(16) !== blink.address.toString(16)){
        let precallback = currentEntry.add(preoffset);
        let postcallback = currentEntry.add(postoffset);
        host.diagnostics.debugLog(`Address: ${currentEntry.toString(16)} has Precallback address: ${precallback.toString(16)} PostCallback address: ${postcallback.toString(16)}\n`);

        let nextEntry = host.createTypedObject(currentEntry, listEntry);
        currentEntry = nextEntry.Flink.address;


    }
    let precallback = blink.address.add(preoffset);
    let postcallback = blink.address.add(postoffset);
    host.diagnostics.debugLog(`Address: ${blink.address.toString(16)} has Precallback address: ${precallback.toString(16)} PostCallback address: ${postcallback.toString(16)}\n`);

    return 0;
}
```

This will return the proper callback address, which you can see function names if symbols are resolved via dps:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*SfMRDPmKyhFTz_3QcJm_og.png)

This script takes in 2 parameters, the first is the starting address of the LIST\_ENTRY (@$ProcObj->CallbackList.Flink) and the second is the last address of the LIST\_ENTRY (@$ProcObj->CallbackList.Blink). The script will then iterate through the LIST\_ENTRY and pull out the offsets of the pre & post operation callbacks. These offsets are from the CALLBACK\_ENTRY\_ITEM structure. DPS can be used to display a pointer value and if symbols are loaded then they will resolve to the Driver!FunctionName of the callback.

## Conclusion

Figuring out how telemetry is generated and leveraged is my passion. Understanding these concepts are important for anyone that wants to understand how their AV/EDRs are preventing certain adversary actions, but also the data exposed to them as defenders. While this post doesn’t cover all the different types of callbacks a driver developer can implement and how they work, I hope this methodology helps others if they do want to find them. In general, I haven’t seen a lot of handle operations leveraged to add additional context to detections. I think understanding where these events come from, why they are triggering, and why there is such a high volume of them will help analysts feel more comfortable with those events. Related to this idea, I did a talk with Olaf Hartong at [ATT&CKCon 3.0](https://www.youtube.com/watch?v=ba2e9pWxboU&t=864s) that could be helpful to some as well.

If you are interested in playing with the pre/post callbacks (which I highly suggest) the code can be found here: [https://github.com/jsecurity101/ProcCallback/tree/main](https://github.com/jsecurity101/ProcCallback/tree/main)

A thank you to [Matt Hand](https://twitter.com/matterpreter) for reviewing this blog. Again, I didn’t go into depth on every aspect of these handle operation callbacks. However; Matt is coming out with a book ( [Evading EDR](https://nostarch.com/book-edr)) which goes into deeper depth about handle operation callbacks, as well as all of these others (process creation, registry, etc). So be on the lookout for that!

Another thank you to [Yarden Shafir](https://twitter.com/yarden_shafir) for pushing me to become more comfortable with JS in WinDbg, this really helped me efficiently find what I was looking for. She has some great examples in her GitHub repo: [WinDbg\_Scripts](https://github.com/yardenshafir/WinDbg_Scripts).

## Resources

- [Mimidrv In Depth: Exploring Mimikatz’s Kernel Driver](https://posts.specterops.io/mimidrv-in-depth-4d273d19e148)
- [TelemetrySourcer](https://github.com/jthuraisamy/TelemetrySourcerer)
- [WinObjEx](https://github.com/hfiref0x/WinObjEx64)
- [Callback Objects](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/callback-objects)

[Research](https://medium.com/tag/research?source=post_page-----1a97cfcb8fb3---------------------------------------)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:48:48/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---post_author_info--1a97cfcb8fb3---------------------------------------)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:64:64/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---post_author_info--1a97cfcb8fb3---------------------------------------)

Follow

[**Written by Jonathan Johnson**](https://jonny-johnson.medium.com/?source=post_page---post_author_info--1a97cfcb8fb3---------------------------------------)

[1.1K followers](https://jonny-johnson.medium.com/followers?source=post_page---post_author_info--1a97cfcb8fb3---------------------------------------)

· [30 following](https://jonny-johnson.medium.com/following?source=post_page---post_author_info--1a97cfcb8fb3---------------------------------------)

Principal Windows EDR Product Researcher @Huntress \| Windows Internals

Follow

## No responses yet

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fjonny-johnson.medium.com%2Funderstanding-telemetry-kernel-callbacks-1a97cfcb8fb3&source=---post_responses--1a97cfcb8fb3---------------------respond_sidebar------------------)

Cancel

Respond

## More from Jonathan Johnson

![Understanding ETW Patching](https://miro.medium.com/v2/resize:fit:679/format:webp/0*Bz0rLE2iCu65PdiK)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:20:20/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---author_recirc--1a97cfcb8fb3----0---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--1a97cfcb8fb3----0---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

[**Understanding ETW Patching**](https://jonny-johnson.medium.com/understanding-etw-patching-9f5af87f9d7b?source=post_page---author_recirc--1a97cfcb8fb3----0---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

Apr 12, 2024

[A clap icon110](https://jonny-johnson.medium.com/understanding-etw-patching-9f5af87f9d7b?source=post_page---author_recirc--1a97cfcb8fb3----0---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

![WMI Internals Part 1](https://miro.medium.com/v2/resize:fit:679/format:webp/0*4yL5BkWjyOpksUzx)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:20:20/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---author_recirc--1a97cfcb8fb3----1---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--1a97cfcb8fb3----1---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

[**WMI Internals Part 1**](https://jonny-johnson.medium.com/wmi-internals-part-1-41bb97e7f5eb?source=post_page---author_recirc--1a97cfcb8fb3----1---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

Jul 5, 2022

[A clap icon55\\
\\
A response icon1](https://jonny-johnson.medium.com/wmi-internals-part-1-41bb97e7f5eb?source=post_page---author_recirc--1a97cfcb8fb3----1---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

![Uncovering Windows Events](https://miro.medium.com/v2/resize:fit:679/format:webp/0*1WyzENPfD3ip59cm)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:20:20/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---author_recirc--1a97cfcb8fb3----2---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--1a97cfcb8fb3----2---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

[**Uncovering Windows Events**](https://jonny-johnson.medium.com/uncovering-windows-events-b4b9db7eac54?source=post_page---author_recirc--1a97cfcb8fb3----2---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

Mar 15, 2023

[A clap icon34\\
\\
A response icon1](https://jonny-johnson.medium.com/uncovering-windows-events-b4b9db7eac54?source=post_page---author_recirc--1a97cfcb8fb3----2---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

![Mastering Windows Access Control: Understanding SeDebugPrivilege](https://miro.medium.com/v2/resize:fit:679/format:webp/0*5q52eLOsmpRC4I55.png)

[![Jonathan Johnson](https://miro.medium.com/v2/resize:fill:20:20/1*ro6iOomAZwYlmMgljL7EfA.png)](https://jonny-johnson.medium.com/?source=post_page---author_recirc--1a97cfcb8fb3----3---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

[Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--1a97cfcb8fb3----3---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

[**Mastering Windows Access Control: Understanding SeDebugPrivilege**](https://jonny-johnson.medium.com/mastering-windows-access-control-understanding-sedebugprivilege-28a58c2e5314?source=post_page---author_recirc--1a97cfcb8fb3----3---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

Dec 18, 2023

[A clap icon62\\
\\
A response icon1](https://jonny-johnson.medium.com/mastering-windows-access-control-understanding-sedebugprivilege-28a58c2e5314?source=post_page---author_recirc--1a97cfcb8fb3----3---------------------d884533e_d5b1_4ca1_b240_932ce687fbe1--------------)

[See all from Jonathan Johnson](https://jonny-johnson.medium.com/?source=post_page---author_recirc--1a97cfcb8fb3---------------------------------------)

## Recommended from Medium

![Stanford Just Killed Prompt Engineering With 8 Words (And I Can’t Believe It Worked)](https://miro.medium.com/v2/resize:fit:679/format:webp/1*va3sFwIm26snbj5ly9ZsgA.jpeg)

[![Generative AI](https://miro.medium.com/v2/resize:fill:20:20/1*M4RBhIRaSSZB7lXfrGlatA.png)](https://generativeai.pub/?source=post_page---read_next_recirc--1a97cfcb8fb3----0---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

In

[Generative AI](https://generativeai.pub/?source=post_page---read_next_recirc--1a97cfcb8fb3----0---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

by

[Adham Khaled](https://medium.com/@adham__khaled__?source=post_page---read_next_recirc--1a97cfcb8fb3----0---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

[**Stanford Just Killed Prompt Engineering With 8 Words (And I Can’t Believe It Worked)**](https://medium.com/@adham__khaled__/stanford-just-killed-prompt-engineering-with-8-words-and-i-cant-believe-it-worked-8349d6524d2b?source=post_page---read_next_recirc--1a97cfcb8fb3----0---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

Oct 19, 2025

[A clap icon23K\\
\\
A response icon618](https://medium.com/@adham__khaled__/stanford-just-killed-prompt-engineering-with-8-words-and-i-cant-believe-it-worked-8349d6524d2b?source=post_page---read_next_recirc--1a97cfcb8fb3----0---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

![Modifying GodPotato to Evade Antivirus](https://miro.medium.com/v2/resize:fit:679/format:webp/1*ZBfU29N4K48f1_FpL9HHCA.png)

[![lainkusanagi](https://miro.medium.com/v2/resize:fill:20:20/1*VzJHRBQO-U0LwAINk4bE1A.png)](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--1a97cfcb8fb3----1---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

[lainkusanagi](https://medium.com/@luisgerardomoret_69654?source=post_page---read_next_recirc--1a97cfcb8fb3----1---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

[**Modifying GodPotato to Evade Antivirus**](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--1a97cfcb8fb3----1---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

Nov 7, 2025

[A clap icon114](https://medium.com/@luisgerardomoret_69654/modifying-godpotato-to-evade-antivirus-f066aa779cf9?source=post_page---read_next_recirc--1a97cfcb8fb3----1---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

![I Stopped Using ChatGPT for 30 Days. What Happened to My Brain Was Terrifying.](https://miro.medium.com/v2/resize:fit:679/format:webp/1*z4UOJs0b33M4UJXq5MXkww.png)

[![Level Up Coding](https://miro.medium.com/v2/resize:fill:20:20/1*5D9oYBd58pyjMkV_5-zXXQ.jpeg)](https://levelup.gitconnected.com/?source=post_page---read_next_recirc--1a97cfcb8fb3----0---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

In

[Level Up Coding](https://levelup.gitconnected.com/?source=post_page---read_next_recirc--1a97cfcb8fb3----0---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

by

[Teja Kusireddy](https://medium.com/@teja.kusireddy23?source=post_page---read_next_recirc--1a97cfcb8fb3----0---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

[**I Stopped Using ChatGPT for 30 Days. What Happened to My Brain Was Terrifying.**](https://medium.com/@teja.kusireddy23/i-stopped-using-chatgpt-for-30-days-what-happened-to-my-brain-was-terrifying-70d2a62246c0?source=post_page---read_next_recirc--1a97cfcb8fb3----0---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

Dec 28, 2025

[A clap icon5.3K\\
\\
A response icon216](https://medium.com/@teja.kusireddy23/i-stopped-using-chatgpt-for-30-days-what-happened-to-my-brain-was-terrifying-70d2a62246c0?source=post_page---read_next_recirc--1a97cfcb8fb3----0---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

![Windows Privilege Escalation Cheat Sheet](https://miro.medium.com/v2/resize:fit:679/format:webp/1*-hxUdBJxohk0BTKePV2Ecg.png)

[![MEGAZORD](https://miro.medium.com/v2/resize:fill:20:20/1*1VxFV17lhzPLxendL-7IbQ.jpeg)](https://medium.com/@MEGAZORDI?source=post_page---read_next_recirc--1a97cfcb8fb3----1---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

[MEGAZORD](https://medium.com/@MEGAZORDI?source=post_page---read_next_recirc--1a97cfcb8fb3----1---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

[**Windows Privilege Escalation Cheat Sheet**](https://medium.com/@MEGAZORDI/windows-privilege-escalation-cheat-sheet-e6272b6c9dfc?source=post_page---read_next_recirc--1a97cfcb8fb3----1---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

Oct 15, 2025

[A clap icon6](https://medium.com/@MEGAZORDI/windows-privilege-escalation-cheat-sheet-e6272b6c9dfc?source=post_page---read_next_recirc--1a97cfcb8fb3----1---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

![Media— HTB Writeup](https://miro.medium.com/v2/resize:fit:679/format:webp/1*MwN1rrut153sqEpqqKgGwg.jpeg)

[![Alts](https://miro.medium.com/v2/resize:fill:20:20/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@alt123?source=post_page---read_next_recirc--1a97cfcb8fb3----2---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

[Alts](https://medium.com/@alt123?source=post_page---read_next_recirc--1a97cfcb8fb3----2---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

[**Media— HTB Writeup**](https://medium.com/@alt123/media-htb-writeup-5bdb199599e4?source=post_page---read_next_recirc--1a97cfcb8fb3----2---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

Nov 26, 2025

![Subnet Mask](https://miro.medium.com/v2/resize:fit:679/format:webp/0*CURlUwLy4tPhG2fk)

[![mohandika](https://miro.medium.com/v2/resize:fill:20:20/1*Gv_3PHgC2rrQpWsXUvnr0g.png)](https://medium.com/@theceosmind?source=post_page---read_next_recirc--1a97cfcb8fb3----3---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

[mohandika](https://medium.com/@theceosmind?source=post_page---read_next_recirc--1a97cfcb8fb3----3---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

[**Subnet Mask**](https://medium.com/@theceosmind/subnet-mask-e661df6ec4c2?source=post_page---read_next_recirc--1a97cfcb8fb3----3---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

Dec 20, 2025

[A clap icon10](https://medium.com/@theceosmind/subnet-mask-e661df6ec4c2?source=post_page---read_next_recirc--1a97cfcb8fb3----3---------------------fe474499_cc86_4112_a90f_16da85630038--------------)

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--1a97cfcb8fb3---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----1a97cfcb8fb3---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----1a97cfcb8fb3---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----1a97cfcb8fb3---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----1a97cfcb8fb3---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----1a97cfcb8fb3---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----1a97cfcb8fb3---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----1a97cfcb8fb3---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----1a97cfcb8fb3---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----1a97cfcb8fb3---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)