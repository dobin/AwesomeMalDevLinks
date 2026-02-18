# https://eversinc33.com/posts/anti-anti-rootkit-part-ii.html

(Anti-)Anti-Rootkit Techniques - Part II: Stomped Drivers and Hidden Threads


Published：2024-09-19 \|
Category：

[Windows Kernel](https://eversinc33.com/categories/Windows-Kernel/) [Rootkits](https://eversinc33.com/categories/Windows-Kernel/Rootkits/)

At the end of [Part I](https://eversinc33.com/posts/anti-anti-rootkit-part-i.html) of this Series, we ended up with a small anti-rootkit driver, that was able to detect malicious drivers mapped to unbacked memory if they either run as a standard Windows Driver (that registers a device object for `IRP` communication) or run any thread in unbacked memory at all - unless they employ some other anti-anti-rootkit techniques.

This post will cover some evasions against this specific anti-rootkit and as such build upon [Part I](https://eversinc33.com/posts/anti-anti-rootkit-part-i.html) \- if you have not read it, you might want to do it now. It is a rather short read anyway. Also check out my rootkit [Banshee](https://github.com/eversinc33/Banshee) and the anti-rootkit [unKover](https://github.com/eversinc33/unKover). This post is mainly an aggregation of known anti-rootkit/anti-cheat evasion techniques and me coming up with ways to detect them.

### [Detection 1: Detecting driver “stomping”](https://eversinc33.com/2024/09/19/anti-anti-rootkit-techniques-part-ii-stomped-drivers-and-hidden-threads\#Detection-1-Detecting-driver-%E2%80%9Cstomping%E2%80%9D "Detection 1: Detecting driver “stomping”") Detection 1: Detecting driver “stomping”

The last part was mainly about detecting rootkits that are mapped to memory, using a mapper such as [kdmapper](https://github.com/TheCruZ/kdmapper). Generally, these tools map a driver manually to kernel memory, using an arbitrary write primitive in a vulnerable, signed driver - so the premise of the last blog post was that detecting threads originating from unbacked memory is one way to detect these types of rootkits.

I ended the previous post with a short word on driver “stomping”, i.e. loading the rootkit over an existing driver in memory. As I mentioned, this can easily be detected by simply comparing a driver’s `.text` section on disk to its `.text` section in memory (analogous to detecting module stomping).

The implementation is really straightforward (as usual, error handling ommited for brevity):

First, we iterate over the `\Driver` directory, as known from Part I:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>``` | ```<br>// Get Handle to \Driver directory<br>InitializeObjectAttributes(&attributes, &directoryName, OBJ_CASE_INSENSITIVE, NULL, NULL);<br>status = ZwOpenDirectoryObject(&handle, DIRECTORY_ALL_ACCESS, &attributes);<br>status = ObReferenceObjectByHandle(handle, DIRECTORY_ALL_ACCESS, nullptr, KernelMode, &directory, nullptr);<br>POBJECT_DIRECTORY directoryObject = (POBJECT_DIRECTORY)directory;<br>ULONG_PTR hashBucketLock = directoryObject->Lock;<br>DbgPrint("Scanning DriverObjects...\n");<br>// Lock the hashbucket<br>KeEnterCriticalRegion();<br>ExAcquirePushLockExclusiveEx(&hashBucketLock, 0);<br>for (POBJECT_DIRECTORY_ENTRY entry : directoryObject->HashBuckets)<br>{<br>    while (entry != nullptr && entry->Object)<br>    {<br>        PDRIVER_OBJECT driver = (PDRIVER_OBJECT)entry->Object;<br>``` |

Then, we get the driver service name and look up its path in the registry. (This is flawed, as a rootkit can spoof this as well, by setting this value to point to the actual rootkit driver - but then, the attacker has to drop it to disk (or hook the filesystem driver and spoof it, but that requires some additional effort)):

|     |
| --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` |