# https://knifecoat.com/Posts/Arbitrary+Kernel+RW+using+IORING's

[![](https://publish-01.obsidian.md/access/a392b8cd24cdb828b4d4118fa8fc87d0/attachments/profile.png)](https://knifecoat.com/Home)[KnifeCoat](https://knifecoat.com/Home)

Posts

[Arbitrary Kernel RW using IORING's](https://knifecoat.com/Posts/Arbitrary+Kernel+RW+using+IORING's)

[ASAR Format Spec](https://knifecoat.com/Posts/ASAR+Format+Spec)

[Boyer-Moore Search Optimization ft. ChatGPT](https://knifecoat.com/Posts/Boyer-Moore+Search+Optimization+ft.+ChatGPT)

[Coverage guided fuzzing for native Android libraries (Frida & Radamsa)](https://knifecoat.com/Posts/Coverage+guided+fuzzing+for+native+Android+libraries+(Frida+%26+Radamsa))

[CVE-2022-21882, Paint By Numbers](https://knifecoat.com/Posts/CVE-2022-21882%2C+Paint+By+Numbers)

[Direct Kernel Object Manipulation (DKOM) attacks on ETW Providers](https://knifecoat.com/Posts/Direct+Kernel+Object+Manipulation+(DKOM)+attacks+on+ETW+Providers)

[Feeling Unsafe, going past managed .NET](https://knifecoat.com/Posts/Feeling+Unsafe%2C+going+past+managed+.NET)

[Fuzzing Redux, leveraging AFL++ Frida-Mode on Android native libraries](https://knifecoat.com/Posts/Fuzzing+Redux%2C+leveraging+AFL%2B%2B+Frida-Mode+on+Android+native+libraries)

[Installing Burp Suite CA on Android 14](https://knifecoat.com/Posts/Installing+Burp+Suite+CA+on+Android+14)

[KDNET on Windows 11 over Hyper-V](https://knifecoat.com/Posts/KDNET+on+Windows+11+over+Hyper-V)

[Mo Money Mo Madness, with Frida](https://knifecoat.com/Posts/Mo+Money+Mo+Madness%2C+with+Frida)

[ObjectDataProvider Deserialization using a Xaml Formatter](https://knifecoat.com/Posts/ObjectDataProvider+Deserialization+using+a+Xaml+Formatter)

[OWASP Mobile Application Security (MAS) p0wn](https://knifecoat.com/Posts/OWASP+Mobile+Application+Security+(MAS)+p0wn)

[Reproducing WhatsApp CVE-2019-11932 with AFL & Frida](https://knifecoat.com/Posts/Reproducing+WhatsApp+CVE-2019-11932+with+AFL+%26+Frida)

[Runtime Android Object Instrumentation](https://knifecoat.com/Posts/Runtime+Android+Object+Instrumentation)

[Scalable research tooling for agent systems](https://knifecoat.com/Posts/Scalable+research+tooling+for+agent+systems)

[Solid Block, adventures with Tensorflow and Reinforcement Learning (RL)](https://knifecoat.com/Posts/Solid+Block%2C+adventures+with+Tensorflow+and+Reinforcement+Learning+(RL))

[Speec No Evil](https://knifecoat.com/Posts/Speec+No+Evil)

[Tell you phone to link me at the coffee shop](https://knifecoat.com/Posts/Tell+you+phone+to+link+me+at+the+coffee+shop)

[Writing Small .NET PE's](https://knifecoat.com/Posts/Writing+Small+.NET+PE's)

Resources

Tools

[Home](https://knifecoat.com/Home)

[![](https://publish-01.obsidian.md/access/a392b8cd24cdb828b4d4118fa8fc87d0/attachments/profile.png)](https://knifecoat.com/Home)[KnifeCoat](https://knifecoat.com/Home)

```yaml
tags:
  - Post
  - Windows
  - Exploit-Dev
```

# Intro

Starting from Windows 22H2 (including 23H2 on insider) it is possible to use `IORING's` to create an arbitrary RW primitive. This assumes that you have a vulnerability that grants you an arbitrary write or some kind or increment. I will explain that in more detail below. This is all based on the excellent research done by [Yarden Shafir](https://twitter.com/yarden_shafir), I have linked her posts about `IORING` below. My write-up skips a lot of details, it's more to have some colourful ex post facto notes. For more details about `IORING's` definitely consult the resources below.

- _I/O Rings – When One I/O Operation is Not Enough_ \- [here](https://windows-internals.com/i-o-rings-when-one-i-o-operation-is-not-enough/)
- _IoRing vs. io\_uring: a comparison of Windows and Linux implementations_ \- [here](https://windows-internals.com/ioring-vs-io_uring-a-comparison-of-windows-and-linux-implementations/)
- _One Year to I/O Ring: What Changed?_ \- [here](https://windows-internals.com/one-year-to-i-o-ring-what-changed/)
- _One I/O Ring to Rule Them All: A Full Read/Write Exploit Primitive on Windows 11_ \- [here](https://windows-internals.com/one-i-o-ring-to-rule-them-all-a-full-read-write-exploit-primitive-on-windows-11/)

# Setup

You can create `IORING` objects with the following API.

```cs
[DllImport("kernelbase.dll")]
internal static extern UInt32 CreateIoRing(
    IORING_VERSION ioringVersion,
    IORING_CREATE_FLAGS flags,
    UInt32 submissionQueueSize,
    UInt32 completionQueueSize,
    ref IntPtr hRing);
```

The most salient detail here is that the `IORING_VERSION` is important. The version of the `IORING` dictates what capabilities it has.

```cs
internal enum IORING_VERSION
{
    IORING_VERSION_INVALID = 0,
    IORING_VERSION_1, // Read (21H2)
    IORING_VERSION_2, // Has a bugfix, I think, for v1 (21H2)
    IORING_VERSION_3 = 300 // Read, Write, Flush, Drain (22H2)
}
```

This primitive can technically be used, in part, from `21H2`. Counterintuitively, having `READ` permissions actually grants you `KM Write` and vice versa.

When you create an `IORING` you get back a handle to interact with the object. This is not a _real handle_ it is a pointer to a UM object for your `IORING`.

```cs
[StructLayout(LayoutKind.Sequential)]
internal struct HIORING
{
    public IntPtr handle;
    public NT_IORING_INFO Info;
    public UInt32 IoRingKernelAcceptedVersion;
    public IntPtr RegBufferArray;   // Pointer to array of IORING opperations
    public UInt32 BufferArraySize;  // Size of array of opperation pointers
    public IntPtr Unknown;
    public UInt32 FileHandlesCount;
    public UInt32 SubQueueHead;
    public UInt32 SubQueueTail;
}
```

At the same time a kernel object is also created.

```c
1: kd> dt *!*IORING*
.....
1: kd> dt ntkrnlmp!_IORING_OBJECT
   +0x000 Type             : Int2B
   +0x002 Size             : Int2B
   +0x008 UserInfo         : _NT_IORING_INFO
   +0x038 Section          : Ptr64 Void
   +0x040 SubmissionQueue  : Ptr64 _NT_IORING_SUBMISSION_QUEUE
   +0x048 CompletionQueueMdl : Ptr64 _MDL
   +0x050 CompletionQueue  : Ptr64 _NT_IORING_COMPLETION_QUEUE
   +0x058 ViewSize         : Uint8B
   +0x060 InSubmit         : Int4B
   +0x068 CompletionLock   : Uint8B
   +0x070 SubmitCount      : Uint8B
   +0x078 CompletionCount  : Uint8B
   +0x080 CompletionWaitUntil : Uint8B
   +0x088 CompletionEvent  : _KEVENT
   +0x0a0 SignalCompletionEvent : UChar
   +0x0a8 CompletionUserEvent : Ptr64 _KEVENT
   +0x0b0 RegBuffersCount  : Uint4B // Size of array of opperation pointers
   +0x0b8 RegBuffers       : Ptr64 Ptr64 _IOP_MC_BUFFER_ENTRY // Pointer to array of opperations
   +0x0c0 RegFilesCount    : Uint4B
   +0x0c8 RegFiles         : Ptr64 Ptr64 Void
```

You can then queue read and write operations for your `IORING`.

```cs
// Read data from a "file", can be used to overwrite data from the file at an arbitrary KM address

[DllImport("kernelbase.dll")]
internal static extern UInt32 BuildIoRingReadFile(
    IntPtr ioRing,
    ref IORING_HANDLE_REF fileRef,
    ref IORING_BUFFER_REF dataRef,
    UInt32 numberOfBytesToRead,
    UInt64 fileOffset,
    IntPtr userData,
    UInt32 sqeFlags);

// Write data to a "file", can be used to write KM Memory to a file

[DllImport("kernelbase.dll")]
internal static extern UInt32 BuildIoRingWriteFile(
    IntPtr ioRing,
    ref IORING_HANDLE_REF fileRef,
    ref IORING_BUFFER_REF bufferRef,
    UInt32 numberOfBytesToWrite,
    UInt64 fileOffset,
    FILE_WRITE_FLAGS writeFlags,
    IntPtr userData,
    UInt32 sqeFlags);
```

Remember there is an array of max possible IO operations. For example if the number of operations is `0x5` then `RegBuffersCount` would be `0x5` and the buffer itself will be `0x5 * IntPtr.Size` in length.

Finally you can submit your IO operations to trigger their use.

```cs
[DllImport("kernelbase.dll")]
internal static extern UInt32 SubmitIoRing(
    IntPtr ioRing,
    UInt32 waitOperations,
    UInt32 milliseconds,
    ref UInt32 submittedEntries);
```

# How about pwn?

So what is the idea here? Well, when you initialize your `IORING`, at that point the Kernel mode object will have empty placeholders for `RegBuffers` and `RegBuffersCount` (provided you don't pre-register a buffer).

If you have a Kernel bug which gives you an arbitrary write or an increment then you can set values for those properties on the KM object (`_IORING_OBJECT`). The only thing you have to keep in mind is that you must be able to alloc data at the pointer that you specify in `RegBuffers`. Typically this will be a UM address you actually allocate (like with `NtAllocateVirtualMemory`). Keep in mind that you can provide a preferred base address to your allocator, you will need to do that if your bug is an arbitrary increment. As for the length, you only really need `0x8` bytes as you don't need to queue many operations (just one at a time). In my POC I continuously update the first array entry to read or write.

What then are you allocating? It's not too complicated, the IO operations structs look like so:

```cs
[StructLayout(LayoutKind.Sequential)]
internal struct IOP_MC_BUFFER_ENTRY
{
    public UInt16 Type;
    public UInt16 Reserved;
    public UInt32 Size;
    public UInt32 ReferenceCount;
    public UInt32 Flags;
    public LIST_ENTRY GlobalDataLink;
    public IntPtr Address; // Address to Read or Write
    public UInt32 Length;  // Amount of data to Read or Write
    public Byte AccessMode;
    public UInt32 MdlRef;
    public IntPtr Mdl;
    [MarshalAs(UnmanagedType.ByValArray, SizeConst = 0x18)]
    public Byte[] MdlRundownEvent; // _KEVENT
    public IntPtr PfnArray;
    [MarshalAs(UnmanagedType.ByValArray, SizeConst = 0x20)]
    public Byte[] PageNodes;
}
```

Finally, once you have overwritten the KM `_IORING_OBJECT`, don't forget to set the same properties on the UM object (`HIORING.RegBufferArray` and `HIORING.BufferArraySize`). You should be able to do this because you created the `IORING` object and got the handle back which points at that UM structure.

Then the idea becomes more clear:

- _BuildIoRingReadFile_ : Read data from a file handle, write that data at `IOP_MC_BUFFER_ENTRY.Address` for a length of `IOP_MC_BUFFER_ENTRY.Length`. This gives you arbitrary KM write.
- _BuildIoRingWriteFile_: Read data at `IOP_MC_BUFFER_ENTRY.Address` for a length of `IOP_MC_BUFFER_ENTRY.Length`, write that data to a file handle. This gives you arbitrary KM Read.
- As the "file" target you can create an actual file but the really elegant thing that Yarden does is use named pipes. This is possible because these pipes are technically just file objects. You can then read Kernel data from the pipe or write Kernel data to the pipe.

![giphy.gif](https://publish-01.obsidian.md/access/a392b8cd24cdb828b4d4118fa8fc87d0/Posts/attachments/giphy.gif)

# A guided tour in KD

I just want to show some of these things in KD because it will make more sense. Here is the KM object for the `IORING` at creation time.

![Pasted image 20221120235232.png](https://publish-01.obsidian.md/access/a392b8cd24cdb828b4d4118fa8fc87d0/Posts/attachments/Pasted%20image%2020221120235232.png)

Note that the `RegBuffers` and `RegBuffersCount` fields are empty.

Then I trigger an arbitrary KM write bug to update those fields and set the count (`0x100`) and UM buffer (`0x000001f600310000`).

![Pasted image 20221120235644.png](https://publish-01.obsidian.md/access/a392b8cd24cdb828b4d4118fa8fc87d0/Posts/attachments/Pasted%20image%2020221120235644.png)

Remember here that the buffer points at an array of structures. In this case the buffer has a length of `0x100 * IntPtr.Size` but remember that I said you only need a single entry. Note that here I have a friendly arbitrary write bug but if you have an increment you should have the allocator give you a more beautiful address, like `0x0000000001000000` 😉.

Then later we queue an IO operation by writing the structure pointer to our UM buffer. Lets have a look at what the KM object looks like now. (Ignore the updated address, this is a different runtime of the POC).

![Pasted image 20221121000813.png](https://publish-01.obsidian.md/access/a392b8cd24cdb828b4d4118fa8fc87d0/Posts/attachments/Pasted%20image%2020221121000813.png)

Notice that `RegBuffers` now no longer points at an empty buffer but that there is indeed a single IO operation structure (`_IOP_MC_BUFFER_ENTRY`) that was queued.

![Pasted image 20221121001018.png](https://publish-01.obsidian.md/access/a392b8cd24cdb828b4d4118fa8fc87d0/Posts/attachments/Pasted%20image%2020221121001018.png)

We manually build this `struct` in our POC and write the pointer to the UM buffer (index 0 of the `RegBuffers` array). By just looking at the struct we can't tell if this is a read or a write operation but we can see that the target of the operation is at a Kernel address (`0xfffff8055a11da20`) and that the size of the operation is `0x8`. We are either reading 8 bytes at the address or overwriting 8 bytes at the address, depending on which function we called.

### Clean-up

When your process terminates you will bluescreen, this is because the `RegBuffers` pointer is not null and the kernel will try to free that address on exit. To avoid this you can use the `IORING` write primitive to set the `RegBuffers` pointer back to null before exiting.

# POC

Here is a short video of the POC in action.

Arbitrary Kernel RW using IORING's

Not found

This page does not exist

Interactive graph

On this page

Intro

Setup

How about pwn?

A guided tour in KD

Clean-up

POC

[Powered by Obsidian Publish](https://publish.obsidian.md/)