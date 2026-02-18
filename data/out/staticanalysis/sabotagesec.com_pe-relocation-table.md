# https://sabotagesec.com/pe-relocation-table/

## PE Relocation Table

## **Introduction**

One interesting section in a PE file is \\”.reloc\\” section that houses a special table called Relocation Table which is an important piece of information needed for Windows loader to load the program into the memory for running the program. When developing advanced malware artifacts, we need to implement functionalities found in Windows loader from scratch to achieve desired results \[ahem evasion\]. For that, we need to have a thorough understanding of PE relocations. Hence this post!!

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/04/screenshot-2022-04-19-021233.png?w=215\%22)

## **Need for relocation**

Consider below sample code, after compilation and linking both data and instruction will be accessed by the CPU from memory using some offset from a base address assigned to the compiled binary. The linker links all of the code libraries and everything and put pieces together into a cohesive entity that we see as an executable. The entire executable\\’s data and code will be organized based on a \\”base address\\” set by the linker.

```
void main()
{
  //some code
  func();
  //some code
}
int func(int a,int b)
{
  int result,c=20;
  result = c*(a+b);
  return result;
}
```

The base address can be found in **NTHeaders->OptionalHeader->ImageBase** of PE. Ideally the compiled and linked binary expects the Windows loader to load the program at the address specified in **ImageBase**. But in reality the loader will load the program at an arbitrary address based on the memory availability and all. Now this is a real problem! Because linker linked code and data with respect to the **ImageBase** address. With different base address, the offsets assigned to both code and data will be pointing to invalid addresses in the memory. **_Relocation Table comes to the rescue!!_**

The information stored in the Relocation Table will be used by the Windows Loader to apply memory recalculation to offset the effect of a different base address. Table contains addresses that point to addresses in the program that require recalculation or relocation for functioning properly.

## **Relocation Table**

Memory layout of the Relocation Table is shown below. Each block represents a single page of memory, usually 4kb. The **IMAGE\_BASE\_RELOCATION**\[8 byte long\]structure specifies the page RVA, and the size of the relocation block.

```
typedef struct _IMAGE_BASE_RELOCATION {
    DWORD   VirtualAddress;
    DWORD   SizeOfBlock;
} IMAGE_BASE_RELOCATION;
typedef IMAGE_BASE_RELOCATION UNALIGNED * PIMAGE_BASE_RELOCATION;
```

Each block begins with RVA to the page and Blocksize which is followed by \[2 bytes\]offsets that point to addresses in the program that need relocation or address recalculation. The 2 byte offsets whose first 4 MSB bits represent relocation type and the rest of the bits represents offset. Two most common types are 0x3 for 32 bit systems and 0xA for 64 bit systems.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/04/image.png?w=377\%22)![\"\"](https://sabotagesec.com/wp-content/uploads/2022/04/up-3.png?w=1024\%22)

One important thing to understand is these offsets in the table are simply pointers to virtual addresses used in the program that needs relocations. The addresses pointed by offsets are addresses computed based on the **ImageBase** value thus need to be recalculated for relocation of code and data. Lets call offsets present in each blocks in the relocation table as \\”reloc RVA\\” and these points to RVAs that need recalculation. So when loader does the recalculation, it is the RVA stored in \\”reloc RVA\\” in a page block that gets modified and not the \\”reloc RVA\\”! Just imagine \\”reloc RVAs\\” as table indices that point to RVA that need recalculation!

## In Action-Analysing notepad

Analyzing the notepad.exe on disk in PE-Bear shows its ImageBase address set by the linker. When we run notepad, there is no assurance that it will get exact same address as base address for the binary in the memory.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/04/screenshot-2022-04-19-032735.png?w=584\%22)

Lets see notepad\\’s Relocation Table! We can see the table contains 4 blocks. The page RVA and BlockSize are structure members of **IMAGE\_BASE\_RELOCATION**. We can clearly see RVA for each page blocks and corresponding size.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/04/image-2.png?w=417\%22)

Lets looks at the contents of first block with an offset 0x31000. We can see Reloc RVAs which point to addresses that need relocation in the memory. This can be verified by checking the data stored at 0x26000 reloc RVA.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/04/image-3.png?w=463\%22)

The RVA stored at reloc RVA 0x0x26000 is 0x140030c90. Its pretty clear by now, the stored RVA is based on ImageBase value 0x140000000. Hence 0x140030c90 needs to be calculated by the loader if program gets loaded at a different ImageBase address.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/04/screenshot-2022-04-19-033726.png?w=487\%22)

## Relocation

A variable called DELTA is calculated to perform relocation by Windows Loader

```
DELTA = Loaded base address [runtime]- real base address [PE imagebase value]
```

The delta is a simple difference of address at which the program is loaded by the loader and the base address hardcoded in PE. This difference is then added to each RVAs pointed by reloc RVAs in the relocation table.

While executing the program, the CPU can thus easily access relocated address by simply adding the \\”reloc RVA\\” in the relocation table to \\”loaded base address\\” of the binary in the memory.

## testing the theory

We can attach a debugger to a notepad instance, we can see the loaded address from below image.

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/04/image-4.png?w=678\%22)

Lets do the math!

Loaded base address : 0x7ff7ff850000

ImageBase in PE: 0x140000000

Delta calculated:0x7FF6BF850000

Lets relocate the RVA 0x140030c90 at reloc RVA 0x0x26000

```
0x7FF6BF850000 [delta] + 0x140030c90 [RVA] = 7FF7 FF88 0C90
```

Lets validate our theory by going to one of the reloc table entry at

0x7ff7ff850000 \[loaded addr\] + 0x26000\[reloc RVA\], as we can see the table entry points to 0x7FF7 FF88 0C90 just like we calculated above! This is how relocation is calculated. The RVA which was initially 0x140030c90 \[based on ImageBase value in PE\] is now recalculated to 0x7FF7 FF880C90 \[based on loaded address\]

![\"\"](https://sabotagesec.com/wp-content/uploads/2022/04/screenshot-2022-04-19-035855.png?w=599\%22)

This can be programmatically done to perform relocation to aid in scenarios like Process Hollowing, DLL Unhooking and reflective loading etc :

[Offensive Coding](https://sabotagesec.com/category/offensive-coding/)

### Leave a Reply [Cancel reply](https://sabotagesec.com/pe-relocation-table/\#respond)

Your email address will not be published.Required fields are marked \*

Comment \*

Name \*

Email \*

Website

Save my name, email, and website in this browser for the next time I comment.