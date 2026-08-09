# https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/

Standard

Posted by

[douggem](https://douggemhax.wordpress.com/author/douggem/)

Posted on

[May 27, 2015](https://douggemhax.wordpress.com/2015/05/27/ "5:50 am")

Posted under

[Uncategorized](https://douggemhax.wordpress.com/category/uncategorized/)

Comments

[8 Comments](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/#comments)

# ObRegisterCallbacks and countermeasures

Because anti-virus softwares were hardhooking the Windows kernel to intercept WinAPI calls when processes were opening files and stuff, Microsoft implemented official and supported methods for receiving notifications for certain events and acting on them.  For instance, when a user launches an executable file, an anti-virus software can be alerted and can scan the file for malicious signatures before launching it.  Or, as is the case in the context of the research that led to this posting, an anti-cheat software can be alerted when a process is attempting to open a handle to the protected game and deny that handle privileges.

This is achieved by registering a callback function for a given event in the kernel using the function ObRegisterCallbacks.  You can see its MSDN article here https://msdn.microsoft.com/en-us/library/windows/hardware/ff558692%28v=vs.85%29.aspx

The short of it is, if you fill out some information regarding what you want to watch and what function you want called when the kernel needs to alert you and pass it to that function, your callback will be called at the appropriate time and you can take appropriate action.  The function returns a handle that you can later use to unregister the callback using ObUnRegisterCallbacks.  This is necessary if your driver unloads because if you left your callback in place and unloaded your driver the callback would probably cause a nice big bugcheck.

This is very annoying when anti-cheats such as Battleye and EasyAntiCheat leverage the callback system to lock down a process and prevent cheaters from reading or manipulating the process memory.  There already exist numerous ways  of countering the callbacks, such as implementing reading/writing functions in your own driver that don’t rely on the standard Windows method of reading from a file.  I wanted to do something a little cleaner, though, and hopefully enable non-modified software access to the protected process.

# The Undocumented Structures

The callbacks are obviously stored in kernel objects and there MUST exist some way to either manipulate these objects or resolve a handle to pass to ObUnRegisterCallbacks.  Then we can just disable the callbacks and read and write to our heart’s content, right?  Well, sort of.  To begin with, I dug into ObRegisterCallbacks to figure out exactly what was going on.

The function begins by allocating some memory.

![](https://i0.wp.com/i.imgur.com/zlN23c8.png)

The first argument is a pointer to the OB\_CALLBACK\_REGISTRATION structure that describes how the callback is to be installed.  If the structure version starts with 0x100 and the registration count is greater than zero, it allocates a buffer the size of 0x20 + OperationCount \* 64 + the altitude string length.  It’s very easy, at this point, to start getting some information on the object that is going to be used to store the callback information.  There will be a header of size 0x20 and a series of objects of size 64.  So already we can start figuring out our structures.

For the sake of brevity (and since I already put these structures into IDA) I’m going to go ahead and give you the structure definitions here:

```
typedef struct _CALLBACK_ENTRY_ITEM {
LIST_ENTRY EntryItemList;
OB_OPERATION Operations;
CALLBACK_ENTRY* CallbackEntry; // Points to the CALLBACK_ENTRY which we use for ObUnRegisterCallback
POBJECT_TYPE ObjectType;
POB_PRE_OPERATION_CALLBACK PreOperation;
POB_POST_OPERATION_CALLBACK PostOperation;
__int64 unk;
}CALLBACK_ENTRY_ITEM, *PCALLBACK_ENTRY_ITEM;

typedef struct _CALLBACK_ENTRY{
 __int16 Version;
 char buffer1[6];
 POB_OPERATION_REGISTRATION RegistrationContext;
 __int16 AltitudeLength1;
 __int16 AltitudeLength2;
 char buffer2[4];
 WCHAR* AltitudeString;
 CALLBACK_ENTRY_ITEM Items; // Is actually an array of CALLBACK_ENTRY_ITEMs that are also in a doubly linked list
}CALLBACK_ENTRY, *PCALLBACK_ENTRY;

Where the 0x20 length header is the beginning of the CALLBACK_ENTRY and the 64 size structure is the CALLBACK_ENTRY_ITEM.  While the CALLBACK_ENTRY_ITEM in the CALLBACK_ENTRY could be accessed as an array of CALLBACK_ENTRY_ITEMs because they’re right next to each other, the kernel doesn’t do this and walks through the linked list instead, and they are only next to each other out of convenience.

ObRegisterCallback then works on filling out these structs using data from the OB_CALLBACK_REGISTRATION object passed in the first argument.  Curiously, when filling out the CALLBACK_ENTRY_ITEMs, it obtains a pointer to the last QWORD of the entry and sets its members according to negative offsets from that point.

Once a CALLBACK_ENTRY_ITEM has been filled out, it’s passed to ObpInserCallbackByAltitude which is exactly what it sounds like.  If you’re not familiar with the Altitude, it’s just a numeric value indicating the order that callbacks should be called.  Lower numbers are called first, higher numbers are called last.  When you insert a callback, the callback is inserted into the linked list according to its altitude value.  If a callback with the same altitude is already in the list, the new callback is not inserted and instead ObpInsertCallbackByAltitude returns a value of STATUS_FLT_INSTANCE_ALTITUDE_COLLISION indicating a collision.  Given that Microsoft’s supported altitudes go up to 430,000 it is unlikely a collision would occur in the wild by chance.  https://msdn.microsoft.com/en-us/library/windows/hardware/ff549689%28v=vs.85%29.aspx

Finding Registered Callbacks

But where does it put the callback objects?  Well, it’s passed in ObpInsertCallbackByAltitude’s first parameter.  Sort of.  The first parameter is to an OBJECT_TYPE structure which is considered opaque by Microsoft but, unlike our other structures in this post, can be dumped with dt in kd.  Its definition is:

typedef struct _OBJECT_TYPE {
 LIST_ENTRY TypeList;
 UNICODE_STRING Name;
 VOID* DefaultObject;
 UCHAR Index;
 unsigned __int32 TotalNumberOfObjects;
 unsigned __int32 TotalNumberOfHandles;
 unsigned __int32 HighWaterNumberOfObjects;
 unsigned __int32 HighWaterNumberOfHandles;
 OBJECT_TYPE_INITIALIZER TypeInfo;
 EX_PUSH_LOCK TypeLock;
 unsigned __int32 Key;
 LIST_ENTRY CallbackList; // A linked list of CALLBACK_ENTRY_ITEMs, which is what we want!
}OBJECT_TYPE, *POBJECT_TYPE;

These objects are global variables, such as PsProcessType and PsThreadType (the only two object types that allow callbacks on their creation or copying).  Note: Those global variables are OBJECT_TYPE**’s, not just single indirection pointers, so beware.

How did ObRegisterCallbacks know which object to use?  It’s passed in the OB_CALLBACK_REGISTRATION.  Or, at least, one of its substructures.  So it gets that handy LIST_ENTRY of Callback items at the end of the object and inserts into that list.  Super convenient!

After the callbacks are inserted ObRegisterCallbacks does some stuff, fires off an APC, whatever.  It doesn’t matter, we have what we’re interested in: The callback structures and how they’re registered and unregistered.  Speaking of unregistering, you know the handle that ObRegisterCallbacks returns?  It’s just a pointer to the CALLBACK_ENTRY structure, the one that is effectively a 0x20 byte header.  But how do we get to that structure?  After all, the OBJECT_TYPE which we will have to parse to find callbacks only has the CALLBACK_ENTRY_ITEMs in a linked list.  Conveniently, each CALLBACK_ENTRY_ITEM has a pointer to its parent CALLBACK_ENTRY, giving us a ‘handle’ with which to unregister it.

So armed with this information, we can just grab PsProcessType and PsThreadType, parse its Callback List, find each entry item’s parent entry, and unregister them with ObUnRegisterCallbacks by passing the address of the entry as the handle!  Bazinga!

 Unregistering the callbacks using ObUnRegisterCallbacks and reading memory from a protected process

The Problem

Sort of.  This works just fine and unregisters the callback.  Unfortunately, when the driver that actually owns the callback goes to unregister it itself when it unloads or whatever, it passes a now invalid handle to ObUnRegisterCallbacks.  Why is this a problem?

 ObUnRegisterCallbacks

When we unregister the callback, the memory of the entry is freed.  So, when the parent driver goes to unregister the now invalid handle pointer to freed memory, bugchecks happen.  Unless this is an acceptable price to pay for unregistering those callbacks, something must be done.

My short term solution is to just do some good old fashioned DKOM.  On Windows 7, as far as I can tell, those callbacks are not monitored by Patchguard.  Simply put, all one has to do is overwrite the PreCallback and PostCallback function pointers in the CALLBACK_ENTRY_ITEM to dummy functions either located in one’s own driver or elsewhere.  This solution seemed to work fine and could even be reversed.  Your driver could disable the callbacks, load its cheat into the target process, then replace the callbacks through DKOM.  This is not an option when using ObUnRegisterCallbacks because the parent driver of the original callbacks would not have a handle to your newly added callbacks.

Things to consider

An anti-virus or anti-cheat software may occasionally attempt to re-register its callback and see if the return value is success or STATUS_FLT_INSTANCE_ALTITUDE_COLLISION.  A collision would indicate that the callback was still in place, while success would indicate that it had been removed.  While an anti-virus has little recourse if this occurs, an anti-cheat software could see this as a sign of tampering and ban the user or close the game.  The solution to this could be to register your own callback at the same altitude as the callback you’re replacing, meaning the anti-cheat will get the collision value and assume its callback is still in place.

An anti-virus or anti-cheat software could check the integrity of its callback items by walking the list itself.  While this is obviously a bad idea in general, if their objects are being manipulated directly it seems like the most direct countermeasure.  Of course, this would spell disaster if a service pack update came out and suddenly anti-viruses and anti-cheats started bugchecking people’s computers because an opaque structure definition changed.

I feel like this is one of the ‘cleanest’ ways to deal with modern anti-cheats kernel modules.  This allows Ring 3 cheat delivery systems to work again without modification and should be relatively stable.  I have no doubt that a similar solution could be used for PsSetLoadImageNotifyRoutine, which I intend on researching next.  I’m sure that the anti-cheat developers will come up with new, exciting, and clever countermeasures to our countermeasures, and the cat and mouse game will rage on 🙂

Doug “Douggem” Confere



Share this:

				Share on X (Opens in new window)
				X


				Share on Facebook (Opens in new window)
				Facebook


Like Loading...

	Related

HiRez anti-cheat analysis part 1January 8, 2014In "Anti-Cheat"
How to get caught by Fallout’s anti-cheatJune 13, 2019With 7 comments
Doug’s ProjectsSeptember 11, 2014With 3 comments


```

## 8 thoughts on “ObRegisterCallbacks and countermeasures”

1. Pingback: [Doug’s Projects \| Douggem's game hacking and reversing notes](https://douggemhax.wordpress.com/2014/09/11/dougs-projects/)
2. Great article, this is definitely going to help me out!





[Reply](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/?replytocom=39#respond)

3. it’s safe to say battleye won against cheaters and exploiters.





[Reply](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/?replytocom=40#respond)

4. hey Doug, but do you think that anti-cheat proggy can just try to access protected process in r3 and saw, that no reply on callback is happen. sorry if its outdated, cant see date of publication





[Reply](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/?replytocom=41#respond)

5. Bastian copied this code or what?





[Reply](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/?replytocom=329#respond)

6. Do you have a more complete source to learn from?





[Reply](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/?replytocom=353#respond)

7. Good write up! I’m currently doing research for a Windows 10 driver to help user mode applications bypass a lot of these anti-cheat systems.





[Reply](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/?replytocom=409#respond)

8. Pingback: [Kernel Karnage – Part 6 (Last Call) – NVISO Labs](https://blog.nviso.eu/2021/12/09/kernel-karnage-part-6-last-call/)

### Leave a comment [Cancel reply](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/\#respond)

Δ

- [Comment](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/#comments)
- [Reblog](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/)
- [Subscribe](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/) [Subscribed](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/)








  - [![](https://s0.wp.com/i/logo/wpcom-gray-white.png?m=1479929237i) Douggem's game hacking and reversing notes](https://douggemhax.wordpress.com/)

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fdouggemhax.wordpress.com%2F2015%2F05%2F27%2Fobregistercallbacks-and-countermeasures%2F&signup_flow=account)


- - [![](https://s0.wp.com/i/logo/wpcom-gray-white.png?m=1479929237i) Douggem's game hacking and reversing notes](https://douggemhax.wordpress.com/)
  - [Subscribe](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/) [Subscribed](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fdouggemhax.wordpress.com%2F2015%2F05%2F27%2Fobregistercallbacks-and-countermeasures%2F&signup_flow=account)
  - [Copy shortlink](https://wp.me/p47hp8-3y)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/)
  - [View post in Reader](https://wordpress.com/reader/blogs/60840546/posts/220)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://douggemhax.wordpress.com/2015/05/27/obregistercallbacks-and-countermeasures/)

%d

Design a site like this with WordPress.com

[Get started](https://wordpress.com/start/?ref=marketing_bar) [Create your website at WordPress.com](https://wordpress.com/start/?ref=marketing_bar)

![](https://pixel.wp.com/g.gif?blog=60840546&v=wpcom&tz=0&user_id=0&post=220&subd=douggemhax&host=douggemhax.wordpress.com&ref=https%3A%2F%2Fwww.google.com%2F&rand=0.28078754153855956)