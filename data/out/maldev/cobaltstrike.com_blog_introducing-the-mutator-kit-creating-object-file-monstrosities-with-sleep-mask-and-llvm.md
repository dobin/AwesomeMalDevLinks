# https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm

This website uses cookies. You may change your settings at any time.

AcceptReject AllManage Cookies

Cookie Preferences

[Home](https://www.cobaltstrike.com/) » [Blog](https://www.cobaltstrike.com/blog/) » Introducing the Mutator Kit: Creating Object File Monstrosities with Sleep Mask and LLVM

# Introducing the Mutator Kit: Creating Object File Monstrosities with Sleep Mask and LLVM

_This is a joint blog written by William Burgess ( [@joehowwolf](https://x.com/joehowwolf)) and Henri Nurmi ( [@HenriNurmi](https://twitter.com/HenriNurmi))._

In our [‘Cobalt Strike and YARA: Can I Have Your Signature?’ blog post](https://www.cobaltstrike.com/blog/cobalt-strike-and-yara-can-i-have-your-signature), we highlighted that the sleep mask is a common target for in-memory YARA signatures. In that post we recommended using the evasive sleep mask option to scramble the sleep mask at run time and break any static signatures. However, this solves the problem at the cost of introducing further forensic artefacts onto a host and increasing our footprint. A much simpler solution is to mutate the sleep mask each time we compile it to make static signatures redundant.

This blog introduces the mutator kit, which uses an LLVM obfuscator to break in-memory YARA scanning of the sleep mask. In the following sections, we will give a quick background to the mutator kit and then show you how to apply it so that a uniquely mutated sleep mask can be applied every time a payload is exported.

The mutator kit is available in the Arsenal Kit now.

Demo: Cobalt Strike MutatorKit

![Video Thumbnail](https://fast.wistia.net/embed/medias/ncw3ov93bg/swatch)

![Video Thumbnail](https://embed-ssl.wistia.com/deliveries/0fa094ec15555fe1fcda7ac70f277d84.webp?image_crop_resized=640x340)

Click for sound

3:24

●●●●

Install Requirements on Ubuntu 22.04

Load Sleepmask Mutator script into the Script Manager

Export a Beacon Payload

Export a Mutated Beacon Payload

_This short video provides a high level overview on how to install and use the Cobalt Strike Mutator Kit, which uses an LLVM obfuscator to break in-memory YARA scanning of the sleep mask._

## Mutator Kit

Typically, given the same source code, compilers will generate the same machine code (I.e. they can be considered, with some caveats, deterministic). As an example, we can build the sleep mask with MinGW and compare the .text sections between different builds. Closer analysis reveals the .text sections are the same:

[view source](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#printSource "print") [?](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#about "?")

|     |
| --- |
| `// [1] Build the sleepmask.` |

|     |
| --- |
| `$ ./build.sh 49 WaitForSingleObject``true``none /tmp/dist` |

|     |
| --- |
| `[ ... ]` |

|     |
| --- |
| `[Sleepmask kit] [*] Compile sleepmask.x64.o` |

|     |
| --- |
| `[ ... ]` |

|     |
| --- |
|  |

|     |
| --- |
| `// [2] Use objdump to find the text section size.` |

|     |
| --- |
| `$ objdump -h sleepmask.x64.o` |

|     |
| --- |
|  |

|     |
| --- |
| ```sleepmask.x64.o:     file format pe-x86-64` |

|     |
| --- |
|  |

|     |
| --- |
| `Sections:` |

|     |
| --- |
| `Idx Name          Size      VMA               LMA               File off  Algn` |

|     |
| --- |
| ```0 .text         00000200  0000000000000000  0000000000000000  00000104  2**4` |

|     |
| --- |
| ```CONTENTS, ALLOC, LOAD, RELOC, READONLY, CODE` |

|     |
| --- |
|  |

|     |
| --- |
| `// [3] Extract the .text section.` |

|     |
| --- |
| `// NB skip is the offset('File off') of the .text section` |

|     |
| --- |
| `// from objdmp and count is the size of the section` |

|     |
| --- |
| `// e.g. python -c 'print(int("104", 16))' == 260.` |

|     |
| --- |
| `$ dd``if``=sleepmask.x64.o of=sleepmask1.bin skip=260 count=512 bs=1` |

|     |
| --- |
|  |

|     |
| --- |
| `// [4] Calculate shasum.` |

|     |
| --- |
| `$ shasum sleepmask1.bin` |

|     |
| --- |
| `4f7813a6aae018a4cf6a78040d9c20024b5a83da  sleepmask1.bin` |

|     |
| --- |
|  |

|     |
| --- |
| `// [5] Repeat the steps again to build another sleep` |

|     |
| --- |
| `// mask and extract/hash the .text section - the hash is identical!` |

|     |
| --- |
| `$ shasum sleepmask2.bin` |

|     |
| --- |
| `4f7813a6aae018a4cf6a78040d9c20024b5a83da  sleepmask2.bin` |

This is clearly a problem when attempting to hide from YARA signatures which look for specific op code patterns. An example of this can be found in the [following YARA signature](https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows_Trojan_CobaltStrike.yar#L849), which looks for the following op code pattern in the default sleep mask (`0x4C 0x8B 0x53 0x08` etc.):

[view source](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#printSource "print") [?](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#about "?")

|     |
| --- |
| `mov r10, [rbx+0x08]` |

|     |
| --- |
| `mov r9d, [r10]` |

|     |
| --- |
| `mov r11d, [r10+0x04]` |

|     |
| --- |
| `lea r10, [r10+0x08]` |

|     |
| --- |
| `test r9d, r9d` |

|     |
| --- |
| `jnz 0x0000000000000007` |

|     |
| --- |
| `test r11d, r11d` |

|     |
| --- |
| `jz 0x0000000000000035` |

|     |
| --- |
| `cmp r9d, r11d` |

|     |
| --- |
| `jnb 0xFFFFFFFFFFFFFFE8` |

|     |
| --- |
| `mov rdi, r9` |

|     |
| --- |
| `mov r8, [rbx]` |

As the sleep mask is visible in memory when Beacon is sleeping, this can be a [trivial detection opportunity](https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows_Trojan_CobaltStrike.yar#L865), as demonstrated below:

![](https://www.cobaltstrike.com/app/uploads/2024/01/defaultsleepmaskyarahit-1024x217.png)Fig 1. The results of scanning Elastic’s Cobalt Strike YARA rules against a process running Beacon with the default sleep mask enabled. The single hit is for the rule `Windows_Trojan_CobaltStrike_b54b94ac`, which as explained above, looks for code belonging to the default sleep mask.

Ideally, we would like to compile the sleep mask and get a unique build each time, in order to make it impossible to produce high fidelity YARA signatures at scale. A common technique for mutating code is using [LLVM](https://llvm.org/docs/tutorial/), of which there are numerous well documented open-source projects (for example, see [0xpat’s blog](https://0xpat.github.io/Malware_development_part_6/)).  Typically, these make use of LLVM Intermediate Representation (IR) code to apply a number of transformation passes to produce obfuscated / mutated machine code.

[Our mutator kit](https://github.com/Cobalt-Strike/obfuscator-llvm) adopts a similar approach and contains four obfuscation passes which are based on eShard’s [obfuscator-llvm plugin](https://github.com/eshard/obfuscator-llvm).  This in turn is based on mutations introduced in the [research by Pascal J., et al](https://crypto.junod.info/spro15.pdf).  These passes include:

- **Substitution-** Replace binary operators with functionally equivalent ones
- **Bogus-** Insert fake control flow blocks
- **Code** **Flattening-** Aims to break higher level code/control flow structure
- **Basic-block Splitting-** Aims to break higher level code/control flow structure

More information on these can be found in the research paper referenced above. Note that we are not overly concerned with making the sleep mask hard to reverse engineer; we are primarily interested in breaking static signatures. Hence, we will not go into any more detail into creating obfuscation passes for LLVM. However, the mutator kit `README.md` contains a number of references should you wish to fork [our obfuscator-llvm repo](https://github.com/Cobalt-Strike/obfuscator-llvm) and create your own passes.

## Usage

We have provided two methods to install the mutator kit:

1. Installing the requirements directly (referred to as ‘native’)
2. Docker

As LLVM plugins require a specific LLVM version and environment, docker makes it easy to handle the required setup and obfuscation plugin compilation. However, if you do not wish to use docker, scripts are provided to bootstrap this process for you (I.e. method 1/native). Additionally, both docker and LLVM can be complicated to use on Windows, so the native method has the advantage of being simple to run on Windows via the Windows Subsystem for Linux (WSL). This blog will assume installation via the native method but see the `README.md` in the mutator kit repo for more guidance on using the provided docker container.

After installing the requirements, the primary workflow is to load the `sleepmask_mutator.cna` script into Cobalt Strike. This will automatically apply a mutated sleep mask to your exported Beacon payloads (see the `Cobalt Strike Client` section below). This script abstracts away the low level details of the mutator kit and makes it very easy to get up and running. However, in order to demonstrate some of the functionality of the mutator kit we will use the command line in this section.

The mutator kit can be manually invoked from the command line via the `mutator.sh` script. The script takes the following arguments:

[view source](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#printSource "print") [?](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#about "?")

|     |
| --- |
| `mutator.sh <target architecture> <clang args>` |

To demonstrate the obfuscation passes in action we can take the following simple C program (`example.c`):

[view source](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#printSource "print") [?](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#about "?")

|     |
| --- |
| `void``go() {` |

|     |
| --- |
| ```int``a = 5;` |

|     |
| --- |
| ```int``b = a + 6;` |

|     |
| --- |
| `}` |

We can compile this with only the substitution pass enabled with the following command:

[view source](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#printSource "print") [?](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#about "?")

|     |
| --- |
| `$ OBFUSCATIONS=substitution mutator.sh x64 –c example.c -o example.o` |

One helpful way of demonstrating the effect of specific obfuscation passes is by generating LLVM IR code and comparing it to the original (unmutated) code. This is demonstrated in the example below:

[view source](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#printSource "print") [?](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#about "?")

|     |
| --- |
| `// Build example.c with only the substitution pass enabled` |

|     |
| --- |
| `$ OBFUSCATIONS=substitution mutator.sh x64 -emit-llvm -S example.c -o example_with_substitutions.ll` |

|     |
| --- |
|  |

|     |
| --- |
| `// Compare the original LLVM IR code with the mutated version` |

|     |
| --- |
| `$ diff --color example.ll example_with_substitutions.ll` |

|     |
| --- |
|  |

|     |
| --- |
| `12,13c12,16` |

|     |
| --- |
|  |

|     |
| --- |
| `// example.ll` |

|     |
| --- |
|  |

|     |
| --- |
| `<   %4 = add nsw i32 %3, 6` |

|     |
| --- |
| `<   store i32 %4, i32* %2, align 4` |

|     |
| --- |
|  |

|     |
| --- |
| `// example_with_substitutions.ll` |

|     |
| --- |
|  |

|     |
| --- |
| `>   %4 = sub i32 %3, 1041996456` |

|     |
| --- |
| `>   %5 = add i32 %4, 6` |

|     |
| --- |
| `>   %6 = add i32 %5, 1041996456` |

|     |
| --- |
| `>   %7 = add nsw i32 %3, 6` |

|     |
| --- |
| `>   store i32 %6, i32* %2, align 4` |

This trivial example demonstrates the impact of only including the substitution pass on the generated code.

More [detailed documentation on LLVM IR](https://mapping-high-level-constructs-to-llvm-ir.readthedocs.io/en/latest/a-quick-primer/index.html) is available, but with a basic understanding this can help debug any problems and to sanity check that specific obfuscation passes have been applied correctly. This makes for a quicker feedback loop, rather than opening the generated object file in IDA.

Having demonstrated the basic usage of the mutator kit, we can now apply it to the sleep mask with the following command:

[view source](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#printSource "print") [?](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm#about "?")

|     |     |
| --- | --- |
| `1` | `$ mutator.sh x64 -c -DIMPL_CHKSTK_MS=1 -DMASK_TEXT_SECTION=1 -o sleepmask.x64.o src49/sleepmask.c` |

|     |     |
| --- | --- |
| `2` | `Obfuscation flattening enabled` |

|     |     |
| --- | --- |
| `3` | `Obfuscation substitution enabled` |

|     |     |
| --- | --- |
| `4` | `Obfuscation split-basic-blocks enabled` |

Note that the `-D*` arguments are used to add an implicit `#define` to the sleep mask which are consistent with the options provided in the `build.sh` script within the sleep mask kit. For more information on clang command line arguments see the [Clang documentation](https://clang.llvm.org/docs/ClangCommandLineReference.html). Additionally, the `–DIMPL_CHKSTK_MS=1` flag is needed to avoid any issues when loading the sleep mask into Cobalt Strike.

By default, only three passes are applied (flattening, substitution, and split-basic-blocks) as bogus can increase the code size. However, you can override the default behaviour by passing in the `OBFUSCATIONS` environment variable (`OBFUSCATIONS=flattening,substitution,split-basic-blocks,bogus mutator.sh x64..` etc.). See the `README.md` included in the mutator kit for more guidance.

At this stage, we can compare the default sleep mask to an LLVM mutated sleep mask. The screenshot below shows the call graph for the _same_ function in the default sleep mask (left) and a mutated one (right):

![Fig 2. A comparison of the same function for the default sleep mask (left) and a LLVM mutated sleep mask (right). ](https://www.cobaltstrike.com/app/uploads/2024/01/functioncallgraphcomparison-812x1024.png)Fig 2. A comparison of the _same_ function for the default sleep mask (left) and a LLVM mutated sleep mask (right).

## Cobalt Strike Client

The example above has demonstrated basic use of the mutator kit and the impact it has on compiled code. However, to make experimenting with the mutator kit and sleep mask as simple as possible we have included a cna script (`sleepmask_mutator.cna`) which adds a menu item allowing you to configure the mutator kit through the Cobalt Strike client. This option is demonstrated in the screenshot below:

![](https://www.cobaltstrike.com/app/uploads/2024/01/sleepmask_mutator_ui.png)Fig 3. Screenshot showing the use of the `sleepmask_mutator.cna` script. This allows you to configure the sleep mask and desired obfuscation passes from the Cobalt Strike GUI.

This menu allows you to:

- Select what obfuscation passes to apply
- Select whether you want to rebuild the sleep mask for _every_ payload export

The script will then automatically apply a mutated sleep mask based on these options to your exported Beacon payloads. Therefore, if desired, it is possible to ensure that every time you export a payload, a different LLVM mutated sleep mask will automatically be applied. The script will also ensure that an error is thrown if any problems are encountered to guarantee a default sleep mask is not accidentally applied (and which could subsequently endanger OPSEC).

The output of the `sleepmask_mutator.cna` script can be seen in the screenshot of the Script Console below when generating a raw HTTP Beacon DLL:

![](https://www.cobaltstrike.com/app/uploads/2024/01/mutator_plugin_export-1024x409.png)Fig 4: The Script Console showing the `sleepmask_mutator.cna` script in action. As part of payload generation, a new LLVM mutated sleep mask is built and automatically applied to a raw Beacon DLL.

With our mutated sleep mask, we can re-run the YARA scan against a process hosting beacon and reveal that no hits are found:

![](https://www.cobaltstrike.com/app/uploads/2024/01/yara_after_llvm-1024x222.png)Fig 5:  The results of scanning Elastic’s Cobalt Strike YARA rules against a process running Beacon with a LLVM mutated sleep mask. As we have mutated the sleep mask there are now no YARA hits for the sleep mask when Beacon is sleeping.

We can also use the mutator kit to compile other BOFs. You may want to consider doing this for a higher level of OPSEC. As a note, most open source BOFs are intended to be compiled with MinGW. Hence, when compiling BOFs with the mutator kit it is highly likely you will encounter compiler issues which you will need to resolve on your own.

## Conclusion

This blog has introduced the mutator kit which is available in the Arsenal Kit now. This kit is designed with the intention of making the creation of high fidelity YARA signatures targeting the sleep mask in-memory impracticable. With this release you can now generate mutated sleep masks on every payload export, which will fundamentally break pre-canned YARA signatures and provide enhanced OPSEC against in-memory signatures.

![](https://www.cobaltstrike.com/app/uploads/2023/07/William-Burgess.png)

#### [William Burgess](https://www.cobaltstrike.com/profile/william-burgess)

Principal Research Lead

[View Profile](https://www.cobaltstrike.com/profile/william-burgess)

TOPICS


- [Development](https://www.cobaltstrike.com/blog?_sft_cornerstone=development "Development")
- [Red Team](https://www.cobaltstrike.com/blog?_sft_cornerstone=red-team "Red Team")