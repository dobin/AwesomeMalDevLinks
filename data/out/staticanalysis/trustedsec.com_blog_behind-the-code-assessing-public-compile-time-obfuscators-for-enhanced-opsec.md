# https://trustedsec.com/blog/behind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec

- [Blog](https://trustedsec.com/blog)
- [Behind the Code: Assessing Public Compile-Time Obfuscators for Enhanced OPSEC](https://trustedsec.com/blog/behind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec)

March 05, 2024

# Behind the Code: Assessing Public Compile-Time Obfuscators for Enhanced OPSEC

Written by
Christopher Paschen


Research

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-Covers/BehindTheCode_WebHero.jpg?w=320&h=320&q=90&auto=format&fit=crop&dm=1767064616&s=336fe63dd3a9b64214fe55c8c7bd3855)

Share

- [Share URL](https://trustedsec.com/blog/behind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec "Share URL")
- [Share via Email](mailto:?subject=Check%20out%20this%20article%20from%20TrustedSec%21&body=Behind%20the%20Code%3A%20Assessing%20Public%20Compile-Time%20Obfuscators%20for%20Enhanced%20OPSEC%3A%20https%3A%2F%2Ftrustedsec.com%2Fblog%2Fbehind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec "Share via Email")
- [Share on Facebook](http://www.facebook.com/sharer.php?u=https%3A%2F%2Ftrustedsec.com%2Fblog%2Fbehind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec "Share on Facebook")
- [Share on X](http://twitter.com/share?text=Behind%20the%20Code%3A%20Assessing%20Public%20Compile-Time%20Obfuscators%20for%20Enhanced%20OPSEC%3A%20https%3A%2F%2Ftrustedsec.com%2Fblog%2Fbehind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec "Share on X")
- [Share on LinkedIn](https://www.linkedin.com/shareArticle?url=https%3A%2F%2Ftrustedsec.com%2Fblog%2Fbehind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec&mini=true "Share on LinkedIn")

Recently, I’ve seen an uptick in interest in compile-time obfuscation of native code through the use of [LLVM](https://llvm.org/). Many of the base primitives used to perform these obfuscation methods are themselves over a year old, and some of the initial research that I’m aware of is over a decade old at this point.

Given the prevalence of heuristics-based detections in a variety of AV engines, I wanted to attempt to find and perform a basic pass on whether compile-time obfuscation for native code yielded decreased or increased detection rates. I wanted to approach this from a naive point of view to see if large changes in detection rates could be observed with minimal input effort. This means that I will not be diving into how to interpret and understand LLVM IR/MIR formats (intermediate formats that optimization passes are performed on) nor how to write your own obfuscator.

Throughout this post, we will also be touching on creating an LLVM-based toolchain that compiles against the Microsoft SDK similar to cl.exe. This included compiling and statically linking against the C runtime used using the _/MT_ option instead of always depending on dynamically linking to msvcrt.dll.

If you want to skip ahead, links to the various test results are available in the appendix at the end of this post.

## Environment Setup

The primary obfuscation tool for native code that I am aware of is via obfuscation passes introduced into LLVM. We will examine public passes and their effects on the detection rates of native executables.

I must convey how the environment for these compilations are created such that you, as a reader, can recreate these experiments or potentially introduce compile-time obfuscation into your workflow.

### Native Code Obfuscation Setup

To set up our obfuscation toolchain, we need to complete five (5) steps:

1. Install LLVM/Clang from the system repository
2. Use xwin to download and set up the Windows SDK
3. Validate that we can produce a functional Windows binary
4. Download and modify a set of public LLVM obfuscation passes
5. Compile these passes and create a template makefile for future use
6. Validate that we can produce an obfuscated, functional binary

For this blog post's purposes, the environment being used will consist of a Fedora 39 machine, using a LLVM-17-based toolchain with out-of-tree plugin passes. This toolchain will be configured to utilize the Visual Studio SDK and headers directly. Acquisition and layout of the visual studio environment is performed by [xwin](https://github.com/Jake-Shadle/xwin).

To install LLVM and the clang-cl front-end, open a command terminal on a Fedora-based Linux machine and execute:

```
dnf install clang clang-libs clang-resource-filesystem llvm llvm-libs llvm-devel
```

This will install LLVM and our clang-cl front-end, which will drive the compilation process. If you have not heard of clang-cl before, it is the MSVC (Microsoft Visual C++) compatible front-end for clang. When we intermix this with the SDK/headers we will download using xwin, it gives us an environment that creates executables as though you compiled it with Visual Studio on a Windows machine using clang. Note that the produced executable is different from when produced using cl.exe proper (e.g., the rich header is missing), but it will get us close enough and follows the format of what is now a drop-down option available in the foremost Windows native executable IDE.

With clang installed, we need to acquire and set up our Windows SDK. Copying the Windows SDK from a Visual Studio install and creating symlinks to deal with common differences such as file case sensitivity is possible but time consuming. Fortunately for us, xwin exists and will ease us through this process. [Download the latest xwin release from GitHub.](https://github.com/Jake-Shadle/xwin/releases/tag/0.5.0) If you are using an x86-based Fedora Linux machine, you will want xwin-\*-x86\_64-unknown-linux-musl.tar.gz. Otherwise, you need to match the format for the host you will be running the xwin tool on.

After the download is complete, open a terminal in the directory of the extracted folder and execute the following commands to download the Microsoft SDK:

```
mv xwin-* /<final_home_partition>
cd <where you moved xwin to>
./xwin --arch x86,x86_64 --accept-license splat --output <final_home> --preserve-ms-arch-notation
```

In my case, < final\_home > is /opt/winsdk.

Finally, we can test that we have created a working toolchain by making a basic message box program. The source code for this basic program, along with links to the rest of our code, is available [here](https://github.com/trustedsec/LLVM-Obfuscation-Experiments/tree/main/goodware/MessageBox_Only).

The message box code can be compiled against our clang setup using the following command:

```
 clang-cl /winsdkdir /opt/winsdk/sdk /vctoolsdir /opt/winsdk/crt /MT -fuse-ld=lld-link test.cpp user32.lib
```

This executable can be transferred and tested on a Windows machine. As of this writing, the executable successfully executed on a Windows 10 system. With our working compiler, it is now possible to locate and configure some out-of-tree passes to use in our obfuscation testing.

For this experiment, the obfuscation passes will be a lightly modified fork of [https://github.com/AimiP02/BronyaObfus](https://github.com/AimiP02/BronyaObfus). This repository was selected because the passes are already compatible with LLVM’s new pass manager. It is also relatively easy to split up the passes such that each can be fed individually into our compilation process. The modified fork used in the tests associated with this post is available [here](https://github.com/freefirex/BronyaObfus).

To compile the obfuscation passes, we will use cmake and a Unix makefile by running the following commands:

```
git clone https://github.com/freefirex/BronyaObfus
cd BronyaObfus
mkdir build
cd build
cmake ..
make
```

If you list the directory now, you should see a collection of .so files, namely libBogusControlFlow.so, libFlattening.so, libIndirectCall.so, libMBAObfuscation.so, and libStringObfuscation.so. With these shared object files, we can now introduce obfuscation passes to compilation.

Our last step is to validate that the passes we have just created can be used. First, let's create a template makefile that will assist with any future compilation work, as we’re about to have many different compilation flags. The template I created is available [here](https://github.com/trustedsec/LLVM-Obfuscation-Experiments/blob/main/makefile.template). At its core, it will compile all the files in src and optionally add obfuscation passes if obf(bogus\|flat\|indirect\|mba\|str) are added to the make command line. General usage might look like:

```
 make all obfbogus obfflat
```

This will make all the files under src, adding bogus control flow and flattening.

## Test Setup

All code being tested for this experiment will be housed under a GitHub repository [here.](https://github.com/trustedsec/LLVM-Obfuscation-Experiments)

The procedure is simple: create or find a code repository, compile it, and then upload the various iterations to VirusTotal to see how detection rates compare. This is not super scientific, and as the obfuscators have some degree of randomness in how they perform, it may not even be repeatable to the exact specification. For my part, though, I feel that this will give a good idea on the relationship between LLVM obfuscation passes and anti-virus detection rates.

I’ve split my tests into two (2) primary passes under the names Goodware and Malware. The Goodware pass focuses on how an obfuscation pass affects the detection of known “good” software. The presence of detections in this category represents false positives, either with the original source or introduced due to the use of obfuscation passes.

The second category, Malware, includes known open-source tools used by bad actors. Here, we’re looking more closely at the change in detection rates from the original compilation of the source. One item to note is that simply changing the compiler from what is normally used (mingw -> clang-cl, msvc -> clang-cl, etc.) already affects the detection ratio.

In all of these tests, if N/A or failed is present in a category, that means either the obfuscation pass outright failed (i.e., caused a segfault while running) or caused errors later in the linking pass.

Reasoning for each tested program was as follows:

Goodware:

- MessageBox -> Exceedingly basic test to baseline from
- SHA-256 -> A legitimate but cryptographic operation
- AES-256 -> A legitimate but cryptographic operation
- PuTTY -> Well-known program that is capable of network communications
- Capstone -> Well-known library that would perform “odd” examination of machine code

Malware:

- Arsenal Kit (Cobalt Strike) -> Specifically was a test of the artifact kit portion, which in its base form should be well detected
- Mimikatz -> “We detect Mimikatz” is a phrase used by legitimate defenders
- Throwback -> One of the first C-based open-source implants I encountered
- TrevorC2 -> Another simple, open-source, C-based agent
- COFFLoader -> While not normally run standalone from disk, the technique used has been incorporated into multiple projects

## Test Results

Below are the results of the tests performed. I was honestly surprised at the lack of meaningful changes in detection rates both for Goodware and Malware. The only case where a meaningful reduction occurred was with Mimikatz, where at most eight (8) detections were dropped. In most other cases, detections were +- 2.For the malware samples specifically, detections were normally reduced, although we can see an increase of detections in the TrevorC2 agent.

I find it notable that PuTTY went from a standard compilation having zero (0) detections to causing false positives when obfuscation was used. In most other Goodware samples, existing false positives were either increased or decreased seemingly randomly by the use of obfuscation.

I also want to point out that the use of obfuscation passes caused the AES test suite to fail (image in appendix). I did not debug why these failures occurred, but it is a strong reminder that modifying code at compile time can introduce errors or conditions that would not normally be present. The possibility of such modifications should be strongly considered by teams looking to leverage this technology.

If you would like to see more information about the actual executables uploaded and discover if the detection rates of these samples have changed over time, I’ve included links to all of my VirusTotal uploads in the appendix.

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BehindCode_Paschen/Fig1_Paschen.png?w=320&q=90&auto=format&fit=max&dm=1709217220&s=7fce82b2a7e0ca2e4c46ba4a1c750870)Figure 1 - Malware Detections

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BehindCode_Paschen/Fig2_Paschen.png?w=320&q=90&auto=format&fit=max&dm=1709217221&s=34666650499022d74e8bf28254196ff4)Figure 2 - Goodware Detections

## Conclusion

I do not feel that adding LLVM obfuscation passes meaningfully impacts the detection ratio of native executables when considering disk scanning. It is entirely possible that when attempting to avoid a known signature use of LLVM obfuscation, passes could be effectively deployed to modify the machine code in such a way that either disk or memory-based scans would be defeated. I’m now of the opinion that if you want/need to use a technique and you know there are specific detections in place, then modifying the bad code manually is largely effective. In a world where ML/heuristic detections are seemingly more prevalent than static signatures, I do not believe LLVM-based obfuscation can be effectively leveraged without putting in a large initial effort to develop custom passes that are not designed to simply bypass static detections but rather target the nature of heuristic detections. Given that most of those algorithms are proprietary, developing such a pass is likely more time-consuming than it is worth for most organizations.

## Appendix:

### VT Scan Links:

#### Messagebox\_Only:

- [none & mba](https://www.virustotal.com/gui/file/fb789c1d51baea4c3a9529dfc8498f5ec2ee4c0e3b31a98f15149090351681b4?nocache=1)
- [str](https://www.virustotal.com/gui/file/92ec228e6bd3cb0cdb259b7340ddaf44e4351cfebc3242e1e9ff367a2a1611b9?nocache=1)
- [indirect](https://www.virustotal.com/gui/file/2f68e0f7ffb083d0c0c79667a06552c19589a79c9156beff2c9474c9b7596706?nocache=1)
- [flat & bogus](https://www.virustotal.com/gui/file/bc5fb951e2e05620e0276879c5d61fa10578d555ef3fd660ffe3c5591c28bd1d?nocache=1)
- [all](https://www.virustotal.com/gui/file/2839679b0212c38135123cd937db0a7a5f7cee0551d7139114a047c53d96ff37?nocache=1)

#### SHA-256:

- [none](https://www.virustotal.com/gui/file/1654a75d7575117bf58d46a75385708100778c1a6128357cf4da3502f058c4e5/detection)
- [mba](https://www.virustotal.com/gui/file/650ad0bcd7300bfe5f85126fa9181e7be4612d89ee0a2cb4bc438bf762ead9f2?nocache=1)
- [str](https://www.virustotal.com/gui/file/94a8402cbb0a97f2f670059e44fe6198a1624aea11568ebe80a1424efaba3398?nocache=1)
- [indirect](https://www.virustotal.com/gui/file/9bc5d501173ab289d3159f92a6357cfc090676b7446031a94a5af4f1167474c0?nocache=1)
- [flat](https://www.virustotal.com/gui/file/b04c9fff7ca2278821e28db8c840bbe59599549464bdda007311721af829eb33?nocache=1)
- [bogus](https://www.virustotal.com/gui/file/7c3006c7fc766279b714e6b5f79488d7f5a8894d51904802e46f499e78f2548c?nocache=1)
- [all](https://www.virustotal.com/gui/file/a07069ab3b18d5af9e3a7dd8f964540a5cbb6532d13c817e3d938d1126465d14?nocache=1)

#### PuTTY:

- [none](https://www.virustotal.com/gui/file/890f715532b5ce6960e56f5743927afe6634fd8478a619669a403347da153e4f?nocache=1)
- [mba](https://www.virustotal.com/gui/file/1f776af50d0616843a3f41e59f901a234c23a3af8c4321b9e3ebef389afbdcd7?nocache=1)
- str - failed
- [indirect](https://www.virustotal.com/gui/file/81a608e8f0b59afd00d4a6309a0b115fa59043a4ee75f1edcbdd521196fc428e?nocache=1)
- [flat](https://www.virustotal.com/gui/file/5f4af2a6f9e33204c132ba5468af4e301da93098662b27336438a09806e2b0bf?nocache=1)
- [bogus](https://www.virustotal.com/gui/file/ec21b0933a6c9ea4922abbbb4aeeec154e042bbe2dee425f9621882545223433)
- [all](https://www.virustotal.com/gui/file/db7ec5b451af694ad5b4f9f29c2d9256c92fdadb2d0d306d13c45db148b5acfd?nocache=1)

#### Capstone:

- [none](https://www.virustotal.com/gui/file/88f265a416f21d92c5b79e1fadfe7ba290f3a2dcb6b25ffd606266708035989e?nocache=1)
- [mba](https://www.virustotal.com/gui/file/f65c7192fb1724c967ca2e9a808fa0fff85ef92fb8bb78d568536daff5a3d6f9?nocache=1)
- str - failed
- [indirect](https://www.virustotal.com/gui/file/1d9686e5783300bea17ca2eea2c7ebee51ebe2c0a0107fb78123e4c55de6bc92?nocache=1)
- [flat](https://www.virustotal.com/gui/file/ef3f48af7a5c778d0fdaec438a81973d6e9fe9306fcd68a4fc74497edc7e7f46?nocache=1)
- [bogus](https://www.virustotal.com/gui/file-analysis/NTQ5MDFjYTlmZmUzMzI4YzMxNmJiYTFkZGQ0NmFhOWQ6MTcwNzQ5Mjc5NA==)
- [all](https://www.virustotal.com/gui/file/3598590510e86700f5df3e78f4f8b73ebdb1ded0a9aebbd05e7fb26a897e1eb9)

#### AES-256:

- [none](https://www.virustotal.com/gui/file/5a2ddc1de7cca18c4bf48c667fbb1e300ac4562d1de6bca4c00e8e373f932ad3?nocache=1)
- [mba](https://www.virustotal.com/gui/file/a406d1924e5ddc3eb1aab78d56e78ea901c8072f204acb88d9f30e9dcf3797fc?nocache=1)
- str - failed
- [indirect](https://www.virustotal.com/gui/file/c0d42f57fa750a86aa32b6e4c915c53e1d6bfe6f1af9d9521b07814d4d61d13c?nocache=1)
- [flat](https://www.virustotal.com/gui/file/64012f8a73059277a42f45f4b88e4f07f22672573e8823073596b664e8b3fea1?nocache=1)
- [bogus](https://www.virustotal.com/gui/file/cd4907acce0a108ec2277350478dac34c734d76e992ddba11530b8957b1bc4d6?nocache=1)
- [all](https://www.virustotal.com/gui/file/145d58f258c9a6c9ef4c5aff16896af7d62ce6366ceb2f218de9928ed87cac1b?nocache=1)

#### Arsenal Kit:

- [none](https://www.virustotal.com/gui/file/45f4f1b77b163015de5c7c9db5b2ea40ac8c0ba303d4b695c6478598eafd7d22)
- [mba](https://www.virustotal.com/gui/file/19687e3e08616c34d0ba53bec0b71d429beb8c3f77cadc2e413ae3f1455bbb62?nocache=1)
- str - failed
- [indirect](https://www.virustotal.com/gui/file/a9e83476a151ac5615ccd72104e463fdc5e32886aa079170e6d6ecc54accb509?nocache=1)
- [flat](https://www.virustotal.com/gui/file/7ff193c4e523722654362b7fcf0638c88978991bad709280224e494b61a0f505?nocache=1)
- [bogus](https://www.virustotal.com/gui/file/78aaaa7d142a4175e5af288cb892f9c14955b269d6e17182b416193f1817516f?nocache=1)
- [all](https://www.virustotal.com/gui/file/7a44b67d7dc78da8ab4cf72b8684b71c7729a94106b53e480e52cde2fc47ec88)
- [mingw compile](https://www.virustotal.com/gui/file/ab28f977a4fee368eab15970a0135bf4df88c1b267bebd66bda3dbf02698b396?nocache=1)

#### Mimikatz:

- [none](https://www.virustotal.com/gui/file/1514ac9beb2abc42a6edd78843507576d0d9047461d3a73cc30d2057d7292d97)
- bogus - failed segfault
- str - failed
- indirect - failed
- [mba](https://www.virustotal.com/gui/file/d75bfaec3b4a373bf25614579f29802aee9d35d73b956ac5b7d061c5997bc36a?nocache=1)
- [flattening](https://www.virustotal.com/gui/file/cb029be4b728c69ab32ecc04d45dfb394a5243f0f6d22710a32c60a4271d7f85?nocache=1)
- [all](https://www.virustotal.com/gui/file/69c63840787d75e471fc92a756543d0d502307150f4fad2ca29950f6e5d2bfcc?nocache=1)

#### TrevorC2:

- [none](https://www.virustotal.com/gui/file/b21dee59cc3236c228c2e2592c5b77a35f4b4ea074eeb94de469795f6861dcfa?nocache=1)
- [bogus](https://www.virustotal.com/gui/file/2c4b232605851053ecaa886dc6842a2cdeeb0982945f4f167b91b8c84d3e4449?nocache=1)
- [str](https://www.virustotal.com/gui/file/8a92ca149f1229855706943309f24e92c1f34ac3f4d0bb89a86f3e22ae2a6d30?nocache=1)
- [indirect](https://www.virustotal.com/gui/file/a7f6181008d48917773a3e9c01f4d235b7283b06225e5bdaa0a969ad0a381957?nocache=1)
- [mba](https://www.virustotal.com/gui/file/e67efcf157af3c6a6363c9f2976b63ca2d68eeca6aea606c9ff6dd6caf6ffffe?nocache=1)
- [flat](https://www.virustotal.com/gui/file/8e4dafbc0abf2ca2c20a529c262140911d630ffabcfb79d0517cd1512342cebf?nocache=1)
- [all](https://www.virustotal.com/gui/file/38805a6a44bae437bf8c8b868fe19282a00b42630c84fcd50f319c212c81c4a9?nocache=1)

#### COFFLoader:

- [none](https://www.virustotal.com/gui/file/5e7ef4503891932ea4e6f112b3cbf80f63dd2246ed7937af3a821278461b5dcd?nocache=1)
- [bogus](https://www.virustotal.com/gui/file/e6cf5058f4190cd23071abbedebbf20072fb931ec82e38f40442c644752c746b?nocache=1)
- [str](https://www.virustotal.com/gui/file/9214bb80fee16143078c3509e078d18612e3d9c808bde5488ddb8074770fd752?nocache=1)
- [indirect](https://www.virustotal.com/gui/file/c4116de73e3f73b796e6a3f7d94f6b996c0173c35bef44d47f7f34303da3c230?nocache=1)
- [mba](https://www.virustotal.com/gui/file/6a180aec38a076b44329a17b70f0060400595adcfbaa1c77ff2faf6e2f179b2e?nocache=1)
- [flat](https://www.virustotal.com/gui/file/49e48ada2326d387503f8b98390b7d0879c944437b5bc836ecd07c79b1d6f045?nocache=1)
- [all](https://www.virustotal.com/gui/file/496cc26a5eb7844c37e42d9b5f8bbe16d2888341a0793766e2a38ae82b5c65a6?nocache=1)

#### Throwback:

- [none](https://www.virustotal.com/gui/file/843a263ae0593e98fa9481a19b86d966f08f0ffd7dcffc88927563b91e6a8a5b?nocache=1)
- bogus - failed
- str [\[BS1\]](https://trustedsec.com/blog/behind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec#_msocom_1) \- failed
- [indirect](https://www.virustotal.com/gui/file/049afb36f3e633ed0f831b098c9142802f4ace0edb080ac8965bc8cdbdcfe312?nocache=1)
- [mba](https://www.virustotal.com/gui/file/d44e57388d7a8758665cabfeae7ab2fddfce9330a04f3099e8d6cd756f4b51ab?nocache=1)
- [flat](https://www.virustotal.com/gui/file/a97fb9b93d85466d4a9aa2d1ae9a5178b70e7fbc426a25715d94325dd6ed35d0?nocache=1)
- [all](https://www.virustotal.com/gui/file/7911517078addcb82c786ee30dfd917ac70ff8ee8abc566a67915bfab62f592d?nocache=1)

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BehindCode_Paschen/Fig3_Paschen.png?w=320&q=90&auto=format&fit=max&dm=1709217223&s=caa1e79313f79db0da201effe0ff2fc9)Figure 3 - AES Test Suite Failing

### References:

[https://github.com/B-Con/crypto-algorithms/tree/master](https://github.com/B-Con/crypto-algorithms/tree/master)

[https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)

[https://github.com/capstone-engine/capstone/archive/5.0.tar.gz](https://github.com/capstone-engine/capstone/archive/5.0.tar.gz)

[https://download.cobaltstrike.com/scripts](https://download.cobaltstrike.com/scripts)

[https://github.com/gentilkiwi/mimikatz](https://github.com/gentilkiwi/mimikatz)

[https://github.com/trustedsec/COFFLoader](https://github.com/trustedsec/COFFLoader)

[https://github.com/trustedsec/trevorc2](https://github.com/trustedsec/trevorc2)

[https://github.com/silentbreaksec/Throwback](https://github.com/silentbreaksec/Throwback%EF%BF%BChttps://github.com/pavelliavonau/cmakeconverter)

[https://github.com/pavelliavonau/cmakeconverter](https://github.com/silentbreaksec/Throwback%EF%BF%BChttps://github.com/pavelliavonau/cmakeconverter)

Share

- [Share URL](https://trustedsec.com/blog/behind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec "Share URL")
- [Share via Email](mailto:?subject=Check%20out%20this%20article%20from%20TrustedSec%21&body=Behind%20the%20Code%3A%20Assessing%20Public%20Compile-Time%20Obfuscators%20for%20Enhanced%20OPSEC%3A%20https%3A%2F%2Ftrustedsec.com%2Fblog%2Fbehind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec "Share via Email")
- [Share on Facebook](http://www.facebook.com/sharer.php?u=https%3A%2F%2Ftrustedsec.com%2Fblog%2Fbehind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec "Share on Facebook")
- [Share on X](http://twitter.com/share?text=Behind%20the%20Code%3A%20Assessing%20Public%20Compile-Time%20Obfuscators%20for%20Enhanced%20OPSEC%3A%20https%3A%2F%2Ftrustedsec.com%2Fblog%2Fbehind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec "Share on X")
- [Share on LinkedIn](https://www.linkedin.com/shareArticle?url=https%3A%2F%2Ftrustedsec.com%2Fblog%2Fbehind-the-code-assessing-public-compile-time-obfuscators-for-enhanced-opsec&mini=true "Share on LinkedIn")

CloseShow Transcript