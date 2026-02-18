# https://trickster0.github.io/posts/Custom-ReadMemory-API/

[Home](https://trickster0.github.io/)Custom ReadMemory API

Post

Cancel

# Custom ReadMemory API

trickster0  on Feb 13, 2022 _2022-02-13T00:00:00+08:00_

Updated Feb 13, 2022 _2022-02-13T20:32:43+08:00_1 min read

After the great job and inspiration by [x86matthew](https://twitter.com/x86matthew) and his [blogpost](https://www.x86matthew.com/view_post?id=read_write_proc_memory) I decided to play with it as well for x64 bit.

The NTAPI function in this method is RtlFirstEntrySList from ntdll.dll. Its definition like Matthew mentioned in his blog is similar like this:

`DWORD RtlFirstEntrySList(DWORD* Address)

`

In his blog, only the x86 version is referenced and used, so I was curious and took a look myself.

Unfortunately, in x64 bit the actual function looks like this:

[![](https://github.com/trickster0/trickster0.github.io/raw/master/assets/img/favicons/pre-mod.png)](https://github.com/trickster0/trickster0.github.io/raw/master/assets/img/favicons/pre-mod.png)

We can see that there are 2 minor issues in the x64 bit version of this function, first one is that the argument of RtlFirstEntrySList will be +8, `mov rax, qword ptr(rcx+8)` which is easy to solve by just adding -8 in the passed address argument.

FYI, for my POC, I am just reading the address of RtlFirstEntrySList but using reference of its address.

You can alter it be removing the reference(&) to just read the contents of that address.

First issue bypassed! Second one is not possible to evade that easy since it will perform `and al, 0F0h` in the byte we want to fetch, hence losing the accuracy of the byte and obtaing a completely wrong address.

The only way around this would be to patch the 2 bytes that perform the logical AND instruction like I do so, in the POC with WriteProcessMemory.

After patching the 2 bytes our function will look like this and it will be executed via NTDLL as normal.

[![](https://github.com/trickster0/trickster0.github.io/raw/master/assets/img/favicons/after-mod.png)](https://github.com/trickster0/trickster0.github.io/raw/master/assets/img/favicons/after-mod.png)

Obviously the result will come back as little endian, but you can always allocate the bytes in a buffer and print or use them in a proper manner.

[![](https://github.com/trickster0/trickster0.github.io/raw/master/assets/img/favicons/output-mod.png)](https://github.com/trickster0/trickster0.github.io/raw/master/assets/img/favicons/output-mod.png)

POC: [https://github.com/trickster0/CReadMemory](https://github.com/trickster0/CReadMemory)

Make sure you read the blog posts and research of Matthew, there are some great stuff on his blog.

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

[Nov 27, 2021 _2021-11-27T00:00:00+08:00_ **Halo's Gate Evolves -> Tartarus' Gate**\\
\\
A while ago in my twitter, I have mentioned what a huge fan I am of Hell’s Gate and Halo’s Gate. Hell’s Gate originally is a very creative way to fetch the syscall numbers by parsing the InMemoryOr...](https://trickster0.github.io/posts/Halo's-Gate-Evolves-to-Tartarus-Gate/)

[Nov 5, 2021 _2021-11-05T00:00:00+08:00_ **Solving the BFS Ekoparty 2019 Exploitation Challenge**\\
\\
This is a quick write up about how one of our team members, Thanasis, solved the challenge for EkoParty 2019. This was a fun challenge and thanks to Lukas and Nico from Blue Frost Security for maki...](https://trickster0.github.io/posts/Solving-the-BFS-EkoParty/)

[Halo's Gate Evolves -> Tartarus' Gate](https://trickster0.github.io/posts/Halo's-Gate-Evolves-to-Tartarus-Gate/) [Primitive Injection - Breaking the Status Quo](https://trickster0.github.io/posts/Primitive-Injection/)

#### Trending Tags

[hacking](https://trickster0.github.io/tags/hacking/) [vulnhub](https://trickster0.github.io/tags/vulnhub/) [vm](https://trickster0.github.io/tags/vm/) [challenge](https://trickster0.github.io/tags/challenge/) [challenges](https://trickster0.github.io/tags/challenges/) [hack](https://trickster0.github.io/tags/hack/) [%0](https://trickster0.github.io/tags/0/) [asa](https://trickster0.github.io/tags/asa/) [certificate](https://trickster0.github.io/tags/certificate/) [cisco](https://trickster0.github.io/tags/cisco/)

 [back-to-top](https://trickster0.github.io/posts/Custom-ReadMemory-API/#)