# https://zer0condition.github.io/posts/reversing-a-signed-driver/index.html

[Back](https://zer0condition.github.io/index.html#blog)

# Introduction

Recently, I was approached by a discord user who requested that I crack a pay-to-cheat service which I will not name, as he had been banned by them after experiencing some difficulties while attempting to use their services. Although initially hesitant, my boredom got the better of me, and I decided to take a look.

I was not surprised to find that the loader had been packed and virtualized using one of the latest **VMProtect3** versions, which made things a bit more complicated. However, through dynamic analysis, I discovered a binary being dropped to disk on my C:\\Windows\\System32 directory. I expected this to be an executable, but it had a .sys extension and was called **'winhelper.sys'**.

Upon closer inspection, I found the driver's size to be around 2MB, which is unusual for drivers, and its digital certificate had been signed with a revoked/expired EV certificate from a Chinese company called **'Binzhoushi Yongyu Feed Co.,LTd.'**

![Driver Certificate](https://i.imgur.com/J8wchy4.png)

# Investigation

Further investigation revealed that the driver's timestamp was from 2015, which was unusual. I decided to load the driver into IDA and found that it had been packed and virtualized with VMProtect3 once again.

![IDA Analysis](https://i.imgur.com/YNXvkUv.png)

Unfortunately, the entry point was virtualized, so I had to enlist the help of a friend to devirtualize the binary using specialized tools. After obtaining the devirtualized binary, I delved further into the driver's internals and discovered that it used I/Os for communication, which is not out of the ordinary.

Eventually, I found the driver object's reference, followed a sub-function, and located the IRP/Dispatch handler of the driver.

![Driver Object](https://i.imgur.com/9KGoS40.png)![IRP Handler](https://i.imgur.com/KxgaJws.png)

While the functionality wasn't too complicated, the control code passed through the stack location was "encrypted" with some XOR and bitwise operations. The driver controller example program explains how it works.

![Control Code Decryption](https://i.imgur.com/wf64H8f.png)

# IOCTLs and Functionalities

I decided to look into the functionalities of the drivers and their control codes.

#### GetProcessBaseAddress (0x13370400)

This was the first ioctl code I came across, which uses a structure with two variables sent through the IRP SystemBuffer. A buffer is returned to the usermode after the request. It takes a process id integer parameter, which is used for **PsLookupProcessByProcessId()** to get the EPROCESS of the target process and passed into **PsGetProcessSectionBaseAddress()**, which returns the SectionBaseAddress of the EPROCESS. The base address is then accessed from the usermode with the second variable inside the structure.

![GetProcessBaseAddress](https://i.imgur.com/aoIwRT3.png)

#### ReadProcessMemory (0x13370800)

This was the second ioctl code found. It also uses a structure passed from the SystemBuffer but of a different size, containing an int, uintptr\_t, uintptr\_t and size\_t respectively. The first parameter was later found out to be a process id passed from the usermode request, the second is the source address, the third is the buffer, and lastly, the size.

![ReadProcessMemory](https://i.imgur.com/jevpmlw.png)

Further analysis uncovered the purpose of the two function calls. The first function call sets up the functions required for reading/writing process memory:

![Setup Functions](https://i.imgur.com/AUBnFlN.png)![Function Details](https://i.imgur.com/fH2jbOh.png)

The second function call reads the process memory through physical memory. It takes the source address, buffer, size, and a variable that returns a value but is not used further:

![Read Function](https://i.imgur.com/q0O8EwJ.png)

Taking a look inside the function, there is nothing that complicated; it takes the virtual address passed and converts it into a physical address (linear translation) and is used in **MmCopyMemory** for reading the process memory.

![Physical Memory Read](https://i.imgur.com/ozft12C.png)

#### WriteProcessMemory (0x13370C00)

This was the final code found, which is for writing process memory. It takes a structure of the same size as the ReadProcessMemory with the same variables. The same function called before in the read request handler sets up the write function to be used, and the write function itself is called after that.

![WriteProcessMemory](https://i.imgur.com/hcenajT.png)

The write function takes the virtual address passed and converts it into a physical address (linear translation) and is used in **MmMapIoSpaceEx** for writing/mapping values to the process memory.

![Write Function 1](https://i.imgur.com/rYDFhhl.png)![Write Function 2](https://i.imgur.com/sbVJfYw.png)

# Conclusion

Overall, reverse engineering the signed kernel driver was an interesting and challenging task. It involved dynamic analysis, devirtualization, and investigation into the driver's internals to uncover its functionalities and control codes.

**Disclaimer:** It's important to note that reverse engineering and cracking software without permission is illegal and can have severe consequences. As such, it's crucial to always act ethically and with integrity when dealing with software and its security.

After digging deeper, the reason this revoked certificate could be loaded leads to a Chinese tool called **'HookSigntool'**.

Music

Close

Critical Acclaim

Avenged Sevenfold

0:000:00

Critical Acclaim

Carry on Wayward Son

Holy Wars

Ride The Lightning

Cowboys from Hell