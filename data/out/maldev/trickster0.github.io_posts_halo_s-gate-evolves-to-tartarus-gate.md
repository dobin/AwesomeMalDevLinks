# https://trickster0.github.io/posts/Halo's-Gate-Evolves-to-Tartarus-Gate/

[Home](https://trickster0.github.io/)Halo's Gate Evolves -> Tartarus' Gate

Post

Cancel

# Halo's Gate Evolves -> Tartarus' Gate

trickster0  on Nov 27, 2021 _2021-11-27T00:00:00+08:00_

Updated Nov 27, 2021 _2021-11-28T03:38:13+08:00_3 min read

A while ago in my twitter, I have mentioned what a huge fan I am of Hell’s Gate and Halo’s Gate. [Hell’s Gate](https://github.com/am0nsec/HellsGate) originally is a very creative way to fetch the syscall numbers by parsing the InMemoryOrderModuleLIst from PEB structure. By finding the ntdll.dll address, which is usually the first entry in InMemoryOrderModuleLIst, it is possible to obtain the syscall numbers by parsing its exports for the necessary functions we need.

Even though this is an excellent technique to bypass most of the Antiviruses, unfortunately due to the evolution of EDRs and unhooking, this technique cannot succeed.

Below we can see a normal syscall where Hell’s Gate would absolutely work.

[![](https://github.com/trickster0/trickster0.github.io/raw/master/assets/img/favicons/ntallocate_normal.png)](https://github.com/trickster0/trickster0.github.io/raw/master/assets/img/favicons/ntallocate_normal.png)

As we have mentioned EDRs evolved and a new technique came to light by Reenz0h, called Halo’s Gate. Halo’s Gate is basically a modified version of Hell’s Gate to unhook the WINAPI calls.

For anyone not aware, unhooking is the process where you evade the hooked WINAPI functions by the AVs/EDRs in order for them to check the parameters and the flow of a program.

Halo’s Gate basically check the first bytes of the called WINAPI and if they are as they should “4c8bd1b8”, then the WINAPI is not hooked and everything proceeds normally, but when the first byte is “e9”, then a jmp assembly instructions redirects the execution of the program to the AV/EDR checking engine, hence it is hooked.

In the screenshot you can see what a hooked call looks like by certain EDRs.

[![](https://github.com/trickster0/trickster0.github.io/raw/master/assets/img/favicons/create_thread.png)](https://github.com/trickster0/trickster0.github.io/raw/master/assets/img/favicons/create_thread.png)

Halo’s Gate tackles this problem if the byte is “e9” by going up or down and check the syscall of the next or previous syscall, if it is not hooked then we grab the syscall and add +1 byte since they are all in order.

Since I am very fond of this technique and It was not working in different EDRs, I was curious why and I had to dig more since it was not the detection/prevention of the security product but it was just failing. Soon I realized that not all EDRs hook the same way, so I had to bypass and extend it Halo’s Gate further into Tartarus’ Gate.

Regarding the EDR, that I was against, I am sure it is easy to find out which one it is but apparently it starts with the bytes “4c8bd1e9” as you can see below when the WINAPI call is hooked.

[![](https://github.com/trickster0/trickster0.github.io/raw/master/assets/img/favicons/ntallocatevirtualmemory.png)](https://github.com/trickster0/trickster0.github.io/raw/master/assets/img/favicons/ntallocatevirtualmemory.png)

Basically what I did was to modify the Halo’s Gate code by adding one more check, to check for the 4th byte if it is “e9”, if it is, it will do the same as the explanation on Halo’s Gate to unhook it, so I ended up calling this Tartarus’ Gate.

I am certain there are more EDRs that have their own hooking method so I can see how this could evolve even further depending on the situation.

Source Code can be found [here](https://github.com/trickster0/TartarusGate) You will notice that the custom way to copy the shellcode to the allocated space is removed, for some reason it was not working very well against this EDR so I would avoid depending on the case. Also, this code might fail a few times depending on the EDR, so if it will not work on the first try, try a few times. If you use a different method that works better than CreateRemoteThread, it will work in a very stable manner.

Resources: [https://sektor7.net/#!res/2021/halosgate.md](https://sektor7.net/#!res/2021/halosgate.md) [https://github.com/am0nsec/HellsGate](https://github.com/am0nsec/HellsGate)

Credits to : Reenz0h from Sektor7 for Halo’s Gate and the authors of Hell’s Gate - [Paul Laîné](https://twitter.com/am0nsec) and [smelly\_\_vx](https://twitter.com/smelly__vx)

This post is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) by the author.

Share

Recent Update

- [Primitive Injection - Breaking the Status Quo](https://trickster0.github.io/posts/Primitive-Injection/)
- [Custom ReadMemory API](https://trickster0.github.io/posts/Custom-ReadMemory-API/)
- [Halo's Gate Evolves -> Tartarus' Gate](https://trickster0.github.io/posts/Halo's-Gate-Evolves-to-Tartarus-Gate/)
- [Solving the BFS Ekoparty 2019 Exploitation Challenge](https://trickster0.github.io/posts/Solving-the-BFS-EkoParty/)
- [EarlyBird APC Queue Injection With a ProcessStateChange Twist](https://trickster0.github.io/posts/earlybird-apc-queue-injection-with-processstatechange-a-twist/)

Trending Tags

[hacking](https://trickster0.github.io/tags/hacking/) [vulnhub](https://trickster0.github.io/tags/vulnhub/) [vm](https://trickster0.github.io/tags/vm/) [challenge](https://trickster0.github.io/tags/challenge/) [challenges](https://trickster0.github.io/tags/challenges/) [hack](https://trickster0.github.io/tags/hack/) [%0](https://trickster0.github.io/tags/0/) [asa](https://trickster0.github.io/tags/asa/) [certificate](https://trickster0.github.io/tags/certificate/) [cisco](https://trickster0.github.io/tags/cisco/)

### Further Reading

[Jun 6 _2025-06-06T00:00:00+08:00_ **Primitive Injection - Breaking the Status Quo**\\
\\
It has been a while, this is my research on trying to change the IOCs of a common remote process injection flow and the end result. I presented this in RedTreat in 2024 and I thought it was about t...](https://trickster0.github.io/posts/Primitive-Injection/)

[Feb 13, 2022 _2022-02-13T00:00:00+08:00_ **Custom ReadMemory API**\\
\\
After the great job and inspiration by x86matthew and his blogpost I decided to play with it as well for x64 bit. The NTAPI function in this method is RtlFirstEntrySList from ntdll.dll. Its definit...](https://trickster0.github.io/posts/Custom-ReadMemory-API/)

[Nov 5, 2021 _2021-11-05T00:00:00+08:00_ **Solving the BFS Ekoparty 2019 Exploitation Challenge**\\
\\
This is a quick write up about how one of our team members, Thanasis, solved the challenge for EkoParty 2019. This was a fun challenge and thanks to Lukas and Nico from Blue Frost Security for maki...](https://trickster0.github.io/posts/Solving-the-BFS-EkoParty/)

[Solving the BFS Ekoparty 2019 Exploitation Challenge](https://trickster0.github.io/posts/Solving-the-BFS-EkoParty/) [Custom ReadMemory API](https://trickster0.github.io/posts/Custom-ReadMemory-API/)

#### Trending Tags

[hacking](https://trickster0.github.io/tags/hacking/) [vulnhub](https://trickster0.github.io/tags/vulnhub/) [vm](https://trickster0.github.io/tags/vm/) [challenge](https://trickster0.github.io/tags/challenge/) [challenges](https://trickster0.github.io/tags/challenges/) [hack](https://trickster0.github.io/tags/hack/) [%0](https://trickster0.github.io/tags/0/) [asa](https://trickster0.github.io/tags/asa/) [certificate](https://trickster0.github.io/tags/certificate/) [cisco](https://trickster0.github.io/tags/cisco/)

 [back-to-top](https://trickster0.github.io/posts/Halo's-Gate-Evolves-to-Tartarus-Gate/#)