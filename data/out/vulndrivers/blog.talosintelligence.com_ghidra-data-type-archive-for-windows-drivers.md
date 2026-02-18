# https://blog.talosintelligence.com/ghidra-data-type-archive-for-windows-drivers/

[Blog](https://blog.talosintelligence.com/)

![](https://blog.talosintelligence.com/content/images/2024/10/GenericCiscoTalos-Header.jpg)

# Ghidra data type archive for Windows driver functions

By [Chris Neal](https://blog.talosintelligence.com/author/chris-neal/)

Thursday, October 10, 2024 06:00


While reverse-engineering Windows drivers with Ghidra, it is common to encounter a function or data type that is not recognized during disassembly.

This is because Ghidra does not natively include the majority of the definitions for data types and functions used by Windows drivers.

Thankfully, these problems can usually be solved by importing Ghidra data type archive files (.gdt) that contain the relevant definitions.

However, it is not uncommon that the definitions in question aren’t available in a preexisting .gdt file, meaning a new definition must be created manually. Additionally, in some cases, the function or data type may be undocumented by Microsoft, making the process of creating a new definition a more tedious process.

To aid analysts in reverse engineering Windows drivers, Cisco Talos is releasing a GDT file on GitHub that contains various definitions for functions and data types that have been created as needed during our analysis of malicious drivers, as they were not present in the commonly used data type archives.

It is important to note that this archive is not intended to contain all undocumented Windows functions or serve as a replacement for other available data type archives, but as a supplement to them. This is a long-term project that will continue to grow when new definitions are created by our analysts and added to the public release.

The archive can be found [here](https://github.com/Cisco-Talos/Windows-drivers-GDT-file) on our GitHub repository.

##### Share this post

- [Share this on Facebook](https://www.facebook.com/sharer.php?u=https://blog.talosintelligence.com/ghidra-data-type-archive-for-windows-drivers/ "Share this on Facebook")
- [Post This](https://x.com/share?url=https://blog.talosintelligence.com/ghidra-data-type-archive-for-windows-drivers/ "Post This")
- [Share this on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://blog.talosintelligence.com/ghidra-data-type-archive-for-windows-drivers/ "Share this on LinkedIn")
- [Reddit This](https://www.reddit/submit?url=https://blog.talosintelligence.com/ghidra-data-type-archive-for-windows-drivers/ "Reddit This")
- [Email This](mailto:?body=Ghidra%20data%20type%20archive%20for%20Windows%20driver%20functionshttps://blog.talosintelligence.com/ghidra-data-type-archive-for-windows-drivers/ "Email This")