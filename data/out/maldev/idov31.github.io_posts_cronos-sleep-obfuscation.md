# https://idov31.github.io/posts/cronos-sleep-obfuscation

06.11.2022

# timeout /t 31 && start evil.exe

Ido Veltzman

[![star](https://idov31.github.io/post-images/GithubStar.svg)](https://github.com/Idov31/Cronos)[![fork](https://idov31.github.io/post-images/GithubFork.svg)](https://github.com/Idov31/Cronos/fork)[![follow](https://idov31.github.io/post-images/GithubFollow.svg)](https://github.com/Idov31)

Table Of Contents

* * *

## Prologue

Cronos is a new sleep obfuscation technique co-authored by [idov31](https://github.com/idov31) and [yxel](https://github.com/janoglezcampos). It is based on [5pider's](https://github.com/Cracked5pider) [Ekko](https://github.com/Cracked5pider/Ekko) and like it, it encrypts the process image with RC4 encryption and evades memory scanners by also changing memory regions permissions from RWX to RW back and forth. In this blog post, we will cover Cronos specifically and sleep obfuscation techniques in general and explain why we need them and the common ground of any sleep obfuscation technique. As always, the full code is available on [GitHub](https://github.com/idov31/Cronos) and for any questions feel free to reach out on [X (Twitter)](https://twitter.com/idov31).

* * *

## Sleep Obfuscation In General

To understand why sleep obfuscations are a need, we need to understand what problem they attempt to solve. Detection capabilities have evolved over the years, we can see that more and more companies going from using AV to EDRs as they provide more advanced detection capabilities and attempt to find the hardest attackers to find. Besides that, also investigators have better tools like [pe-sieve](https://github.com/hasherezade/pe-sieve) that finds injected DLLs, hollowed processes and shellcodes and that is a major problem for any attacker that attempts to hide their malware.

To solve this issue, people came up with sleep obfuscation techniques and all of them have a basic idea: As long as the current piece of malware (whether it is DLL, EXE or shellcode) isn't doing any important "work" (for example, when an agent don't have any task from the C2 or backdoor that just checks in once in a while) it should be encrypted, when people start realizing that they came up with a technique that will encrypt the process image and decrypt it when it needs to be activated.

One of the very first techniques I got to know is [Gargoyle](https://github.com/JLospinoso/gargoyle) which is an amazing technique for marking a process as non-executable and using the ROP chain to make it executable again. This worked great until scanners began to adapt and began looking also for non-executable memory regions, but in this game of cops and thieves, the attackers adapted again and started using a single byte XOR to encrypt the malicious part or the whole image an example for it is [SleepyCrypt](https://github.com/SolomonSklash/SleepyCrypt). SleepyCrypt not only adds encryption but also supports x64 binaries (the original Gargoyle supports only x86 but Waldo-IRC created an [x64 version of Gargoyle](https://github.com/waldo-irc/YouMayPasser) but, you guessed it, memory scanners found a solution to that as well by doing single XOR brute force on memory regions.

Now that we have the background and understand **WHY** sleep obfuscations exist let's understand what has changed and what sleep obfuscation techniques we have nowadays.

* * *

## Modern Sleep Obfuscations

Today (speaking in 2022) we have memory scanners that can brute force single-byte XOR encryption and detect malicious programs even when they do not have any executable rights, what can be done next?

The answer starts to become clearer in [Foliage](https://github.com/SecIdiot/FOLIAGE), which uses not only heavier obfuscation than single-byte XOR but also a neat trick to trigger the ROP chain to change the memory regions' permission using `NtContinue` and context.

Later on, [Ekko](https://github.com/Cracked5pider/Ekko) came out and added 2 important features: One of them is to RC4 encrypt the process image using an undocumented function` SystemFunction032`, and the other one is to address and fix the soft spot of every sleep technique so far: Stabilize the ROP using a small and very meaningful change to the RSP register.

To conclude the modern sleep obfuscation section we will also talk about [DeathSleep](https://github.com/janoglezcampos/DeathSleep) a technique that kills the current thread after saving its CPU state and stack and then restores them. DeathSleep also helped a lot during the creation of Cronos.

Now, it is understandable where we are heading with this and combine all the knowledge we have accumulated so far to create Cronos.

* * *

## Cronos

The main logic of Cronos is pretty simple:

1. 1.
Changing the image's protection to RW.

2. 2.
Encrypt the image.

3. 3.
Decrypt the image.

4. 4.
Add execution privileges to the image.


To achieve this we need to do several things like encrypting somehow the image with a function, choosing which kind of timer to use and most importantly finding a way to execute code when the image is decrypted.

Finding an encryption function was easy, choosing `SystemFunction032` was an obvious choice since it is well used (also in Ekko) and also documented by Benjamin Delpy in [his article](https://blog.gentilkiwi.com/cryptographie/api-systemfunction-windows) and many other places.

One may ask "Why to use a function that can be used as a strong IoC when you can do custom or XOR encryption?" the honest answer is that it will be much easier to use it in the ROP later on (spoiler alert) than implementing strong and good encryption.

Now, that we have an encryption function we need to have timers that can execute an APC function of our choosing. For that, I chose waitable timers because they are well-documented , easy and stable to use and easy to trigger - all that needs to be done is to call any alertable sleep function (e.g. `SleepEx`).

All we have left to do is to find a way to execute an APC that will trigger the sleeping function, the problem is that the code has to run regardless of the image's state (whether has executable rights, is encrypted, etc.) and the obvious solution is to use an ROP chain that will execute the sleep to trigger the APC.

For the final stage, we used the NtContinue trick from Foliage to execute the different stages of sleep obfuscation `(RW -> Encrypt -> Decrypt -> RWX)`.

* * *

## Conclusion

This was a fun project to make, and we were able to make it thanks to the amazing projects mentioned here every single one of them created another piece to get us where we are here.

I hope that you enjoyed the blog and would love to hear what you think about it!