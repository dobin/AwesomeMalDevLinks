# https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking

This website uses cookies. You may change your settings at any time.

AcceptReject AllManage Cookies

Cookie Preferences

[Home](https://www.cobaltstrike.com/) » [Blog](https://www.cobaltstrike.com/blog/) » Revisiting the User-Defined Reflective Loader Part 2: Obfuscation and Masking

# Revisiting the User-Defined Reflective Loader Part 2: Obfuscation and Masking

Monday 11 September, 2023

This is the second installment in a series revisiting the User-Defined Reflective Loader (UDRL). In [part one](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-1-simplifying-development), we aimed to simplify the development and debugging of custom loaders and introduced the User-Defined Reflective Loader Visual Studio (UDRL-VS) template.

In this installment, we’ll build upon the original UDRL-VS loader and explore how to apply our own custom obfuscation and masking to Beacons with UDRLs. The primary intention of this post is to demonstrate the huge amount of flexibility that is available to UDRL developers in Cobalt Strike and provide code examples for users to apply to internal projects.

To accompany this post, we’ve added an “obfuscation-loader” to the UDRL-VS kit and made some changes to the solution itself. UDRL-VS started out as a simple example loader that you could debug in Visual Studio. It is now a library of loader functions that will grow over time. At present, we have a “default-loader” (the original UDRL-VS loader) and an “obfuscation-loader” (the example described in this post). The move to a library simplifies the maintenance of the kit but should also improve the user experience when developing custom loaders.

In addition, we recently published [Cobalt Strike and YARA: Can I have your Signature?](https://www.cobaltstrike.com/blog/cobalt-strike-and-yara-can-i-have-your-signature/) where we discussed the concept of in-memory YARA scanning and the importance of masking, obfuscation and customization with regards to evading static detections. As part of that post, we demonstrated Beacon’s susceptibility to defensive tools such as YARA in its default state, and therefore strongly recommend reading it for some additional background and context.

## UDRL vs Malleable C2

Cobalt Strike allows users to obfuscate Beacon via its [malleable C2](https://www.cobaltstrike.com/product/features/malleable-c2) profile. For example, the [`stage{}`](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2-extend_pe-memory-indicators.htm) block can be used to modify the RAW Beacon payload and define how it is loaded into memory. Whilst this offers flexibility, it does have limitations which can expose Beacon to detection via YARA scanning (as shown in the [Cobalt Strike and YARA post](https://www.cobaltstrike.com/blog/cobalt-strike-and-yara-can-i-have-your-signature/)). Most notably, `stage.obfuscate` which masks several aspects of the RAW Beacon payload but does not mask the default reflective loader, its DOS stub, or the Sleep Mask.

As part of applying a UDRL to Beacon, PE modifications defined in the `stage{}` block are [deliberately ignored](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/malleable-c2-extend_user-defined-rdll.htm). This is because they are tightly coupled to the operation of the default reflective loader. For example, if something is masked in a certain way, the loader will need to know how to unmask it. As a result, a _default Beacon_ is passed to the `BEACON_RDLL_GENERATE*` hooks so that users can customize it. This allows UDRL developers to go way beyond what is possible with just the `stage{}` block and create custom obfuscation and masking routines to transform Beacon.

It is still possible to use Aggressor Script to [query the malleable C2 profile](https://github.com/boku7/BokuLoader/blob/88bbfda41e3f01899b838395addfb831177614fe/dist/BokuLoader.cna#L905) and apply its configuration to Beacon. However, in this post, we will apply our transformations exclusively using Aggressor Script. This helps to maintain a logical separation, but also ensures that our modifications are applied correctly regardless of the malleable C2 profile.

**_Note:_** _This post focuses on the obfuscation and masking of Beacon prior to loading it into memory. However, as part of the loading process we undo all of this to achieve execution. As a result, in part 3 of this series, we will use the Sleep Mask to apply runtime masking to Beacon to complete the coverage outlined in the Cobalt Strike and YARA post. It is also important to highlight that obfuscation and masking is only one aspect of the “evasion-in-depth” approach. The content of these posts (part2/part3) and the example provided in the UDRL-VS kit is solely focused on addressing static signatures and tools such as YARA. It will **not** help to evade all of the various features of PE malware models, different types of behavioural analysis or other more advanced detection techniques, such as those that look for_ [_thread creation trampolines_](https://www.elastic.co/security-labs/get-injectedthreadex-detection-thread-creation-trampolines) _or_ [_inspect kernel call stacks_](https://www.elastic.co/security-labs/upping-the-ante-detecting-in-memory-threats-with-kernel-call-stacks) _, etc_.

## Setting The Stage{}

In the following sections we will expand upon what’s available in the `stage{}` block and use it as a starting point to transform Beacon.

### stage.magic\_mz

There are several options within the `stage{}` block that allow users to modify obvious PE file markers in Beacon’s header. However, whilst these options offer the flexibility to customize Beacon, they are limited to specific aspects of its header. For example, `stage.magic_mz_x**` which allows users to overwrite the first 4 bytes of the RAW Beacon payload (the MZ header).

As part of UDRL development, we are not limited to modifying specific bytes at specific locations. Instead, we can modify any value at any location. This means we can extend the idea behind options like `stage.magic_mz` and use Aggressor Script to completely transform Beacon’s PE header.

To demonstrate this idea, we replaced Beacon’s original PE header with the custom `PE_HEADER_DATA` and `SECTION_INFORMATION` structures shown below. These structures only contain a subset of the information available in a PE header, but still have everything our reflective loader needs to load a DLL. More information on custom executable formats can be found in [Hasherezade’s](https://twitter.com/hasherezade) excellent [From Hidden Bee To](https://research.checkpoint.com/2023/from-hidden-bee-to-rhadamanthys-the-evolution-of-custom-executable-formats/) [Rhadamanthys](https://research.checkpoint.com/2023/from-hidden-bee-to-rhadamanthys-the-evolution-of-custom-executable-formats/) [– The evolution of custom executable formats](https://research.checkpoint.com/2023/from-hidden-bee-to-rhadamanthys-the-evolution-of-custom-executable-formats/).

_**Note:** Due to the significant number of signatures targeting the reflective loader’s DOS stub. We chose to use the “Double Pulsar” approach for the obfuscation-loader. The same techniques described here could be expanded to work with the “Stephen Fewer” style loaders, but this can be left as an exercise for the reader._

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#about "?")

|     |     |
| --- | --- |
| `1` | `typedef``struct``_SECTION_INFORMATION {` |

|     |     |
| --- | --- |
| `2` | ```DWORD``VirtualAddress;` |

|     |     |
| --- | --- |
| `3` | ```DWORD``PointerToRawData;` |

|     |     |
| --- | --- |
| `4` | ```DWORD``SizeOfRawData;` |

|     |     |
| --- | --- |
| `5` | `} SECTION_INFORMATION, *PSECTION_INFORMATION;` |

|     |     |
| --- | --- |
| `6` |  |

|     |     |
| --- | --- |
| `7` | `typedef``struct``_PE_HEADER_DATA {` |

|     |     |
| --- | --- |
| `8` | ```DWORD``SizeOfImage;` |

|     |     |
| --- | --- |
| `9` | ```DWORD``SizeOfHeaders;` |

|     |     |
| --- | --- |
| `10` | ```DWORD``entryPoint;` |

|     |     |
| --- | --- |
| `11` | ```QWORD ImageBase;` |

|     |     |
| --- | --- |
| `12` | ```SECTION_INFORMATION Text;` |

|     |     |
| --- | --- |
| `13` | ```SECTION_INFORMATION Rdata;` |

|     |     |
| --- | --- |
| `14` | ```SECTION_INFORMATION Data;` |

|     |     |
| --- | --- |
| `15` | ```SECTION_INFORMATION Pdata;` |

|     |     |
| --- | --- |
| `16` | ```SECTION_INFORMATION Reloc;` |

|     |     |
| --- | --- |
| `17` | ```DWORD``ExportDirectoryRVA;` |

|     |     |
| --- | --- |
| `18` | ```DWORD``DataDirectoryRVA;` |

|     |     |
| --- | --- |
| `19` | ```DWORD``RelocDirectoryRVA;` |

|     |     |
| --- | --- |
| `20` | ```DWORD``RelocDirectorySize;` |

|     |     |
| --- | --- |
| `21` | `} PE_HEADER_DATA, *PPE_HEADER_DATA;` |

To create the above header structure, we used Aggressor Script’s [`pedump`](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm#pedump) [`()`](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm#pedump) function to generate a map of Beacon’s PE header (`%pe_header_map`). We then “ _packed_” the information we needed into a byte sequence with Sleep’s [`pack()`](http://sleep.dashnine.org/manual/pack.html) function. In the code example below, the first three values of the `PE_HEADER_DATA` structure are queried from `%pe_header_map` and “ _packed_” into a byte sequence called `$pe_header_data`. The format string “I-I-I-“ specifies three 4-byte unsigned integer values (DWORDs) in little endian byte order.

_**Note:** Sleep uses the concept of “ [Scalars](http://sleep.dashnine.org/manual/fundamentals.html#1)” which are universal data containers. Variables in Sleep are Scalars indicated by a `$` and can hold strings, numbers or even references to Java objects. `%pe_header_map` is a “Hash Scaler” indicated by the `%` sign. This is a data type that can hold multiple values associated with a key._

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#about "?")

|     |     |
| --- | --- |
| `1` | `$pe_header_data``=``pack``(` |

|     |     |
| --- | --- |
| `2` | ```"I-I-I-"``,` |

|     |     |
| --- | --- |
| `3` | ```%pe_header_map``[``"SizeOfImage.<value>"``],` |

|     |     |
| --- | --- |
| `4` | ```%pe_header_map``[``"SizeOfHeaders.<value>"``],` |

|     |     |
| --- | --- |
| `5` | ```%pe_header_map``[``"AddressOfEntryPoint.<value>"``]` |

|     |     |
| --- | --- |
| `6` | `);` |

To replace Beacon’s original PE header, we used Sleep’s [`substr("string", start, [end])`](http://sleep.dashnine.org/manual/substr.html) function to extract a byte sequence that contained only Beacon’s PE sections. It was then possible to append it to our newly created `$pe_header_data` structure.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#about "?")

|     |     |
| --- | --- |
| `1` | `# create custom header structure` |

|     |     |
| --- | --- |
| `2` | `$pe_header_data``= create_header_content(``%pe_header_map``);` |

|     |     |
| --- | --- |
| `3` | `` |

|     |     |
| --- | --- |
| `4` | `# determine size of Beacon’s Pe header` |

|     |     |
| --- | --- |
| `5` | `$size_of_pe_headers``=``%pe_header_map``[``"SizeOfHeaders.<value>"``];` |

|     |     |
| --- | --- |
| `6` |  |

|     |     |
| --- | --- |
| `7` | `# remove Beacon's original PE header` |

|     |     |
| --- | --- |
| `8` | `$beacon_pe_sections``=``substr``(``$beacon``,``$size_of_pe_headers``);` |

|     |     |
| --- | --- |
| `9` |  |

|     |     |
| --- | --- |
| `10` | `# append PE sections to newly created header structure` |

|     |     |
| --- | --- |
| `11` | `$modified_beacon``=``$pe_header_data``.``$beacon_pe_sections``;` |

For clarity, the above has been illustrated in the following diagram:

![](https://www.cobaltstrike.com/app/uploads/2023/09/diagram_modified-pe-header.png)Figure 1. The original Beacon vs the modified Beacon.

To support the above change, we had to make several modifications to the loader. Most importantly, we had to remove references to the original PE header and update it to parse the `PE_HEADER_DATA` structure.  Additionally, as we removed a considerable chunk of data from Beacon, we had to ensure that the loader could still copy it correctly.

The `PointerToRawData` value in the `SECTION_INFORMATION` structure shown previously is a “file pointer”. A file pointer is a location within a given PE file as stored on disk (before it has been loaded). Therefore, after removing Beacon’s PE Header, the `PointerToRawData` values were incorrect as they were `SizeOfHeaders` (`0x400`) too large. Put simply, in Beacon’s original PE header, the `.text`section’s `PointerToRawData` value is `0x400`. However, after removing the header, the `.text` section started at `0x0`. As a result, the loader would have to subtract `0x400` (the size of the PE header) from the original value to correctly identify the section. It would have been possible to perform this subtraction for each of these `PointerToRawData` values, but a much simpler approach was to offset the base address of the RAW Beacon itself. For example, if the base address was offset to `-0x400`, then when we can use the original `PointerToRawData` value (`0x400`) to find the start of the `.text` section at `0x0`. This offset can be seen in the following code example.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#about "?")

|     |     |
| --- | --- |
| `1` | `// Identify the start address of Beacon` |

|     |     |
| --- | --- |
| `2` | `PPE_HEADER_DATA peHeaderData = (PPE_HEADER_DATA)bufferBaseAddress;` |

|     |     |
| --- | --- |
| `3` | `char``* rawDllBaseAddress = bufferBaseAddress +``sizeof``(PE_HEADER_DATA);` |

|     |     |
| --- | --- |
| `4` |  |

|     |     |
| --- | --- |
| `5` | `// Offset the start address by SizeOfHeaders` |

|     |     |
| --- | --- |
| `6` | `rawDllBaseAddress -= peHeaderData->SizeOfHeaders;` |

The above modification ensured that the loader was able to successfully identify each section and load them into memory. However, the loaded image still contained a considerable amount of space between its start address and its `.text` section. This was because our loader copied the RAW Beacon DLL into the newly allocated memory at the locations specified by `VirtualAddress` in the `SECTION_INFORMATION` structures. `VirtualAddress` is a Relative Virtual Address (RVA) which means the address of an item after it is loaded into memory. This value is “ _relative_” to the image’s base address which means it accounts for the PE header. Once again, we could have subtracted the virtual size of the PE header (`0x1000`) from each of these values, but a much simpler option was to offset the base address of the loaded image as well. This ensured that the that the memory region containing the loaded Beacon image began with the .text section rather than a PE header or any empty space.

![A high-level diagram to show the layout of the loaded Beacon image in memory.](https://www.cobaltstrike.com/app/uploads/2023/09/diagram_removed-pe-header-loaded-beacon.png)Figure 2. The layout of the loaded Beacon image in memory.

**_Note:_** _The `stage.obfuscate` malleable C2 option instructs the default loader to use a similar approach when copying Beacon into memory._

### stage.transform

By default, Beacon contains some widely known strings that are considered low hanging fruit for static detections. The malleable C2 profile makes it trivial to modify them with its `transform-x**{}` blocks and even allows users to add new strings with its `string`/`stringw` commands.

It is possible to use the [`strrep`](http://sleep.dashnine.org/manual/strrep.html) [`()`](http://sleep.dashnine.org/manual/strrep.html) function in Aggressor Script to replace strings. However, it is native to Sleep, which means it operates slightly differently to the one in the malleable C2 profile. For example, Sleep’s `func_strrep()` uses Java’s `replace()` method, which means it completely replaces the original string with the new one. This can be seen in the following screenshot.

![](https://www.cobaltstrike.com/app/uploads/2023/09/screenshot_w3schools-java-replace.png)Figure 3. Java’s `replace()` method.

This type of modification is problematic when modifying a PE file, as it could change the size of the affected section and cause either the loader or the PE file to crash during execution. To overcome this, we created a simple wrapper around Sleep’s `strrep()` called `strrep_pad()`. This function was used to pad the input string with NULL bytes prior to replacing it (in a similar fashion to the malleable C2’s `strrep` command). We then replaced “ _beacon.x64.dll_” and “ _ReflectiveLoader_” with “ _udrl.x64.dll_” and “ _customLoader_” as shown in CFF Explorer below.

![](https://www.cobaltstrike.com/app/uploads/2023/09/screenshot_cff-explorer-strrep-1-1024x371.png)Figure 4. The modified Beacon strings.

**_Note:_** _It is possible to apply the contents of a malleable C2 profile’s `transform-x**` block in Aggressor Script via `setup_transformations()`. In addition, strings defined in the malleable C2 profile can be applied with `setup_strings()`. However, as described at the start of this post, we opted to apply our transformations solely in Aggressor Script_

### stage.obfuscate

As part of the Cobalt Strike and YARA post, we discussed the `stage.obfuscate` malleable C2 option and highlighted that despite masking some aspects of Beacon, it still left a lot exposed. In the previous sections we implemented some of `stage.obfuscate`’s functionality in the sense that we removed Beacon’s PE header as part of loading it into memory. However, it also masks Beacon’s `.text` section and its Import Address Table (IAT) which is important due to the significant number of YARA rules that target them.

There is an existing Aggressor Script function called [`pe_mask_section`](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm#pe_mask_section) [`()`](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm#pe_mask_section) that makes it trivial to mask a section with a single byte key. In addition, [Bobby Cooke](https://twitter.com/0xBoku) has demonstrated in [BokuLoader](https://github.com/boku7/BokuLoader) that it is possible to use Aggressor Script to [mask each string in the IAT](https://github.com/boku7/BokuLoader/blob/88bbfda41e3f01899b838395addfb831177614fe/dist/BokuLoader.cna#L1017C4-L1017C4).

Whilst masking Beacon’s `.text` section and its IAT would provide feature parity with the malleable C2 profile, we know from Cobalt Strike and YARA that this would still leave parts of Beacon exposed. As a result, we wanted to create a more generic capability that could mask these vulnerable sections (`.text`, `.rdata``.data`) with randomly generated variable length keys.

At a high-level, our approach was to append a buffer of XOR keys to the `PE_HEADER_DATA` structure and dynamically retrieve them at runtime. This allowed us to add variation to each exported artefact without re-compiling the loader. The following diagram provides an illustration of this approach.

![](https://www.cobaltstrike.com/app/uploads/2023/09/diagram_xor-keys-layout-1024x94.png)Figure 5. A high-level overview of the modified artefact.

To ensure that we could retrieve the XOR keys from this buffer, we updated the `PE_HEADER_DATA` structure to include the lengths of each XOR key.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#about "?")

|     |     |
| --- | --- |
| `1` | `typedef``struct``_PE_HEADER_DATA {` |

|     |     |
| --- | --- |
| `2` | ```[…SNIP…]` |

|     |     |
| --- | --- |
| `3` | ```DWORD``TextSectionXORKeyLength;` |

|     |     |
| --- | --- |
| `4` | ```DWORD``RdataSectionXORKeyLength;` |

|     |     |
| --- | --- |
| `5` | ```DWORD``DataSectionXORKeyLength;` |

|     |     |
| --- | --- |
| `6` | `} PE_HEADER_DATA, *PPE_HEADER_DATA;` |

It was then possible to use these values to index the buffer and determine the start address of each key. This also meant that the key length could change dramatically between each exported payload and the loader would still be able to retrieve them.

To simplify using the XOR keys in the loader at runtime, we created a `KEY_INFO` structure to provide an abstract representation of each key and its length. We then added `XOR_KEYS` to do the same for each `KEY_INFO` structure.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#about "?")

|     |     |
| --- | --- |
| `1` | `typedef``struct``_KEY_INFO {` |

|     |     |
| --- | --- |
| `2` | ```size_t``KeyLength;` |

|     |     |
| --- | --- |
| `3` | ```char``* Key;` |

|     |     |
| --- | --- |
| `4` | `} KEY_INFO, *PKEY_INFO;` |

|     |     |
| --- | --- |
| `5` |  |

|     |     |
| --- | --- |
| `6` | `typedef``struct``_XOR_KEYS {` |

|     |     |
| --- | --- |
| `7` | ```KEY_INFO TextSection;` |

|     |     |
| --- | --- |
| `8` | ```KEY_INFO RdataSection;` |

|     |     |
| --- | --- |
| `9` | ```KEY_INFO DataSection;` |

|     |     |
| --- | --- |
| `10` | `} XOR_KEYS, *PXOR_KEYS;` |

The following code example demonstrates the approach described above. Initially, the size of `PE_HEADER_DATA` is used to find the start address of the first XOR key. Then, the XOR key lengths in `peHeaderData` are used to identify the start address of each subsequent key.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#about "?")

|     |     |
| --- | --- |
| `1` | `PPE_HEADER_DATA peHeaderData = (PPE_HEADER_DATA)rawDllBaseAddress;` |

|     |     |
| --- | --- |
| `2` | `XOR_KEYS xorKeys;` |

|     |     |
| --- | --- |
| `3` | `xorKeys.TextSection.key = rawDllBaseAddress +``sizeof``(PE_HEADER_DATA);` |

|     |     |
| --- | --- |
| `4` | `xorKeys.TextSection.keyLength = peHeaderData->TextSectionXORKeyLength;` |

|     |     |
| --- | --- |
| `5` | `xorKeys.RdataSection.key = xorKeys.TextSection.key + peHeaderData->TextSectionXORKeyLength;` |

|     |     |
| --- | --- |
| `6` | `xorKeys.RdataSection.keyLength = peHeaderData->RdataSectionXORKeyLength;` |

|     |     |
| --- | --- |
| `7` | `xorKeys.DataSection.key = xorKeys.RdataSection.key + peHeaderData->RdataSectionXORKeyLength;` |

|     |     |
| --- | --- |
| `8` | `xorKeys.DataSection.keyLength = peHeaderData->DataSectionXORKeyLength;` |

## Obfuscation vs YARA

In the previous sections, we described our approach to obfuscation and masking Beacon. We can now test the modified artefact against [Elastic’s collection of open-source YARA rules for Cobalt Strike](https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows_Trojan_CobaltStrike.yar) (as previously used in the Cobalt Strike and YARA post).

Once again, we’d like to credit Elastic for its comprehensive rule set. In addition, we’d also like to reiterate that this is not intended to be a guide to evade a specific vendor. We are focusing on publicly available static detections, which is undoubtedly only one aspect of the defence-in-depth approach employed by modern EDRs. In the following screenshot, we have scanned the default RAW Beacon payload followed by our modified artefact. We can see that the default payload was trivial to detect, but the obfuscated Beacon did not trigger any of the YARA rules.

![](https://www.cobaltstrike.com/app/uploads/2023/09/screenshot_obfuscation-vs-yara-1024x460.png)Figure 6. YARA scans of both the RAW Beacon payload and the modified artefact.

## The Extra Mile

In the previous sections we built upon the existing malleable C2 options available in Cobalt Strike to create a Beacon payload that was robust against static detections. Whilst the transformations detailed above were found to be effective, there are many examples of modern malware that utilises multiple layers of obfuscation and masking as part of their defence evasion strategy. For example, [the Roshtyak malware strain](https://decoded.avast.io/janvojtesek/raspberry-robins-roshtyak-a-little-lesson-in-trickery/) uses _14 layers_ of obfuscation.

The process of applying 14 layers of obfuscation is understandably outside the scope of this post. However, Elastic’s Security Labs recently published a fantastic walkthrough of the [Blister loader](https://www.elastic.co/security-labs/blister-loader) which uses compression and encryption to add layers of obfuscation. Applying these two felt like a more realistic goal for our example loader.

In the following sections, we will adapt the Blister loader’s approach and demonstrate how to build these layers of obfuscation into the UDRL itself. Therefore, we will apply both compression and encryption to the modified Beacon via Aggressor Script. This helps to simplify the process of embedding Beacon into different stage0 shellcode runners, but also fits nicely into the Cobalt Strike workflow. For example, when spawning or injecting Beacon. Additionally, in Cobalt Strike 4.9 we have made it possible for users to apply UDRLs to postex DLLs which means that they can benefit from the obfuscation and masking as well.

**_Note:_** _This layered approach to obfuscation could also provide an excellent opportunity to apply [Defence](https://attack.mitre.org/tactics/TA0005/)_ [_Evasion_](https://attack.mitre.org/tactics/TA0005/) _techniques. For example,_ [_Execution Guard Rails_](https://attack.mitre.org/techniques/T1480/) _or_ [_Virtualisation/Sandbox Evasion_](https://attack.mitre.org/techniques/T1497/) _._

### Applying Compression

A full description of compression is outside the scope of this blog post. Fundamentally though, [compression is the process of encoding information using fewer bits than the original](https://en.wikipedia.org/wiki/Data_compression).

To demonstrate using compression as part of a reflective loader, we implemented Microsoft’s [LZNT1](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/5655f4a3-6ba4-489b-959f-e1f407c52f15) compression algorithm in Aggressor Script. We primarily chose LZNT1 because it is supported by [`RtlDecompressBuffer`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-rtldecompressbuffer) [`()`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-rtldecompressbuffer). This simplified the loader as we were able to use it to decompress the buffer instead of implementing the decompression logic ourselves. In addition, [Nakatsuru You](https://github.com/you0708) had already ported Jeffrey Bush’s [C implementation of LZNT1](https://github.com/coderforlife/ms-compress) to [Python](https://github.com/you0708/lznt1), which made it trivial to port it once more to Aggressor Script.

**_Note:_** _It would have been possible to [execute the Python](http://sleep.dashnine.org/manual/exec.html) implementation directly from Aggressor Script, but for the sake of simplicity and so that we could provide an example without any other dependencies, we spent some time re-writing it in Sleep. As part of some (very) limited testing that the LZNT1 compression algorithm compressed the default Beacon shellcode (CS 4.8)_ _from roughly ~296kb to ~178kb.  The compression algorithm was not quite as effective on the obfuscated Beacon due to the transformations described in the previous section._

The function prototype for `RtlDecompressBuffer()` has been provided below.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#about "?")

|     |     |
| --- | --- |
| `1` | `NT_RTL_COMPRESS_API NTSTATUS RtlDecompressBuffer(` |

|     |     |
| --- | --- |
| `2` | ```[in]``USHORT``CompressionFormat,` |

|     |     |
| --- | --- |
| `3` | ```[out]``PUCHAR``UncompressedBuffer,` |

|     |     |
| --- | --- |
| `4` | ```[in]``ULONG``UncompressedBufferSize,` |

|     |     |
| --- | --- |
| `5` | ```[in]``PUCHAR``CompressedBuffer,` |

|     |     |
| --- | --- |
| `6` | ```[in]``ULONG``CompressedBufferSize,` |

|     |     |
| --- | --- |
| `7` | ```[out]``PULONG``FinalUncompressedSize` |

|     |     |
| --- | --- |
| `8` | `);` |

As described above, it was possible to decompress the compressed buffer with a single call to `RtlDecompressBuffer()`. However, as shown in its function prototype, it required the size of both the compressed and the decompressed buffer. It was not possible to retrieve these sizes from the existing `PE_HEADER_DATA` structure as we had compressed it. Therefore, to pass this information to the loader, we used the same approach described at the start of this post and created a new custom header structure to hold this information called `UDRL_HEADER_DATA`.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#about "?")

|     |     |
| --- | --- |
| `1` | `typedef``struct``_UDRL_HEADER_DATA {` |

|     |     |
| --- | --- |
| `2` | ```DWORD``CompressedSize;``//the size of the compressed artefact` |

|     |     |
| --- | --- |
| `3` | ```DWORD``RawFileSize;``//the size of the RAW DLL` |

|     |     |
| --- | --- |
| `4` | ```DWORD``LoadedImageSize;``// the size of the loaded image` |

|     |     |
| --- | --- |
| `5` | `} UDRL_HEADER_DATA, * PUDRL_HEADER_DATA;` |

The high-level layout at this stage has been illustrated in the following diagram.

![](https://www.cobaltstrike.com/app/uploads/2023/09/diagram_lznt1-layout-1024x207.png)Figure 7. A high-level overview of the modified artefact after compression.

In the original UDRL-VS example, we allocated a block of memory and copied Beacon into it as part of the loading process. However, to support compression, we were required to allocate another block of temporary memory to store the decompressed Beacon DLL prior to loading it.

The decompression workflow can be seen in the following diagram. The term “loader memory” refers to the original allocation of memory for the UDRL. We have not included the loader itself in this diagram for simplicity.

![](https://www.cobaltstrike.com/app/uploads/2023/09/diagram_lznt1-workflow-1-1024x1012.png)Figure 8. The decompression workflow.

**_Note:_** _Here we are allocating an additional region of memory to handle the decompression. This is obviously a trade-off, as perhaps a large allocation of memory could be considered suspicious. It is therefore up to the UDRL developer to decide if compression is worth the additional allocation of memory. As stated at the start of this post, this is intended as an example._

### Applying Encryption

To demonstrate encryption, we opted for simplicity and used the RC4 encryption algorithm. We considered it simple because an RC4 encryption/decryption routine can be written in very few lines of code. In addition, there are a number of public examples of the algorithm. For example, [@\_EthicalChaos\_](https://twitter.com/_EthicalChaos_) ( [ccob](https://gist.github.com/CCob)) has already shown how to [encrypt a buffer with RC4](https://gist.github.com/CCob/9dd8de00c2c6ad069301a225589223fa) via Java in Sleep and [Austin Hudson](https://twitter.com/ilove2pwn_) used RC4 as part of [Titanldr-ng](https://github.com/realoriginal/titanldr-ng/blob/master/Titan.cna).

In the following example, an encryption key is randomly generated and used to encrypt the previously compressed buffer. The length of the encryption key is then added to the `UDRL_HEADER_DATA` structure and in a similar fashion to the XOR keys, the encryption key is appended to it.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#about "?")

|     |     |
| --- | --- |
| `1` | `$rc4_key_length``= 11;` |

|     |     |
| --- | --- |
| `2` | `$rc4_key``= generate_random_bytes(``$rc4_key_length``);` |

|     |     |
| --- | --- |
| `3` | `[…SNIP…]` |

|     |     |
| --- | --- |
| `4` | `$encrypted_buffer``= rc4_encrypt(``$compressed_buffer``,``$rc4_key``);` |

|     |     |
| --- | --- |
| `5` | `$udrl_header_data``=``pack``(` |

|     |     |
| --- | --- |
| `6` | ```“I-I-I-I-“,` |

|     |     |
| --- | --- |
| `7` | ```$compressed_file_size``,` |

|     |     |
| --- | --- |
| `8` | ```$raw_file_size``,` |

|     |     |
| --- | --- |
| `9` | ```$loaded_image_size``,` |

|     |     |
| --- | --- |
| `10` | ```$rc4_key_length``,` |

|     |     |
| --- | --- |
| `11` | `);` |

|     |     |
| --- | --- |
| `12` | `return``$udrl_header_data``.``$rc4_key``.``$encrypted_buffer``;` |

This approach has been illustrated in the following diagram.

![](https://www.cobaltstrike.com/app/uploads/2023/09/diagram_lznt1-rc4-layout-1024x193.png)Figure 9. A high-level overview of the modified artefact after compression and encryption.

To ensure that the loader was independent of whatever executed it, we had to assume that it would not have the required permissions to decrypt the buffer in place (as it is highly likely the loader would be running in `PAGE_EXECUTE_READ` memory). As a result, we modified the original workflow and decided to use Loaded Image Memory twice (this also helped to avoid allocating another region of memory).

As shown in the following diagram, the compressed and encrypted buffer was first copied into the Loaded Image Memory so that it could be decrypted (in `PAGE_READWRITE`memory). The decrypted buffer was then decompressed and stored in Temporary Memory. Once the buffer had been decrypted/decompressed, it was possible for the loader to continue its original workflow and load Beacon back into Loaded Image Memory (hence the name Loaded Image Memory).

![](https://www.cobaltstrike.com/app/uploads/2023/09/diagram_lznt1-rc4-workflow-1-1024x606.png)Figure 10. The decryption/decompression workflow.

### Entropy

In the previous sections we heavily obfuscated Beacon. However, in doing so, we significantly increased its entropy which can be [problematic when trying to evade PE malware models](https://redsiege.com/blog/2023/04/evading-crowdstrike-falcon-using-entropy/). A full description of all the various features of PE malware models is outside the scope of this post. However, we have experienced modern EDR highlighting even benign files as suspicious if they contain too much randomness. As a result, we thought it would be helpful to (very) briefly demonstrate the effect of the above obfuscation on entropy as it may be something to consider when creating stage0 shellcode runners.

There are some excellent resources online that talk about [Threat Hunting with File Entropy](https://practicalsecurityanalytics.com/file-entropy/) and [Using Entropy in Threat Hunting](https://redcanary.com/blog/threat-hunting-entropy/). In addition, there is a section on Binary Entropy in [Sektor7’s Windows Evasion course](https://institute.sektor7.net/rto-win-evasion). As a result, this post will not delve into it in much detail. Fundamentally though, when people talk about binary entropy, they are typically referring to a measure of randomness.

In the following example, we calculated the entropy of a default RAW Beacon, the obfuscated Beacon and then finally the compressed/encrypted version. We can see that these transformations have significantly increased the entropy. Therefore, any PE malware model that considers high entropy a suspicious feature would likely trigger on it.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#about "?")

|     |     |
| --- | --- |
| `1` | `C:\Tools>sigcheck.exe -a beacon.x64.bin | findstr /I entropy` |

|     |     |
| --- | --- |
| `2` | ```Entropy:        6.188` |

|     |     |
| --- | --- |
| `3` | `C:\Tools>sigcheck.exe -a beacon.x64.obfuscated.bin | findstr /I entropy` |

|     |     |
| --- | --- |
| `4` | ```Entropy:        7.535` |

|     |     |
| --- | --- |
| `5` | `C:\Tools>sigcheck.exe -a beacon.x64.obfuscated.lznt1.rc4.bin | findstr /I entropy` |

|     |     |
| --- | --- |
| `6` | ```Entropy:        7.999` |

[0xPat](https://twitter.com/0xPat) has published an excellent series of posts on [malware development](https://0xpat.github.io/Malware_development_part_1/). We recommend reading all of it, but as part of their fourth post about [anti-static analysis](https://0xpat.github.io/Malware_development_part_4/) they recommend using Base64 encoding to reduce entropy as its 64 character alphabet reduces the randomness.

Aggressor Script provides a built-in [`base64_encode()`](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm#base64_encode) function which makes it easy to test this hypothesis. We can see that Base64 encoding brings the entropy down considerably.

[view source](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#viewSource "view source")

[print](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#printSource "print") [?](https://www.cobaltstrike.com/blog/revisiting-the-udrl-part-2-obfuscation-masking#about "?")

|     |     |
| --- | --- |
| `1` | `C:\Tools>sigcheck.exe -a beacon.x64.obfuscated.lznt1.rc4.b64.bin | findstr /I entropy` |

|     |     |
| --- | --- |
| `2` |  |

|     |     |
| --- | --- |
| `3` | ```Entropy:        6.001` |

**_Note:_** _One drawback to Base64 encoding is that it increases the length of the artefact. However, in our limited testing the obfuscated/compressed/encrypted/encoded buffer was not much larger than the original RAW Beacon payload (~305kb vs ~296kb in CS 4.8)._

![A high-level overview of the modified artefact after compression, encryption and encoding.](https://www.cobaltstrike.com/app/uploads/2023/09/diagram_lznt1-rc4-b64-layout-1024x192.png)Figure 11. A high-level overview of the modified artefact after compression, encryption and encoding.

To handle this transformation in the example loader, we added `Base64Decode()` to Obfuscation.cpp. It was then possible to use the existing approach to decompression/decryption but simply Base64 decode the buffer as part of the copy operation. The updated workflow has been illustrated in the following diagram.

![The decoding/decryption/decompression workflow.](https://www.cobaltstrike.com/app/uploads/2023/09/diagram_lznt1-rc4-b64-workflow-1-1024x606.png)Figure 12. The decoding/decryption/decompression workflow.

**_Note:_** _It is important to note that the artefact we have created will ultimately sit inside a stage0 shellcode runner of some description. As a result, we need to consider the entropy of the shellcode runner as well as the artefact itself. The default Cobalt Strike executable has a relatively high entropy which is even larger when used in combination with our obfuscation-example. This is because the Cobalt Strike client masks the shellcode with a randomly generated 4-byte key prior to stomping it into the default executable. This essentially removes the effect of the Base64 encoding. To overcome this, it is possible to either export the RAW shellcode and create a custom shellcode runner or use the artefact kit to modify the default executable. The Cobalt Strike client will not apply this masking to custom artefacts. We strongly recommend developing custom shellcode runners, the default Cobalt Strike executables are widely signatured and will likely negate any obfuscation you apply to Beacon_

## Closing Thoughts

As part of this post, we have obfuscated, compressed, encrypted and encoded Beacon to evade a set of open-source static detections. Whilst we have demonstrated one approach, we hope this post has shown that the possibilities are endless when developing your own custom obfuscation and masking routines within a UDRL.

Once again, it is important to note that despite all of the obfuscation and masking applied above. Beacon can be trivial to detect in memory in its default state with regards to YARA scanning unless it takes evasive action. The simplest way to mask Beacon at runtime is via the Sleep Mask kit. A full description of the Sleep Mask was outside the scope of this post, however, in part 3 of this series we will demonstrate how to complete the coverage outlined above and mask the obfuscation-loader at runtime.

The code is now available in the udrl-vs kit in the Arsenal Kit. To try it out, simply open the solution and compile the obfuscation-loader Release build. You can then load the` ./bin/examples/obfuscation-loader/prepend-udrl.cna`script into the Cobalt Strike console and export an artefact.

Alternatively, you can start using this functionality in your own custom UDRLs. To create a custom loader, add a project to the UDRL-VS solution, apply the `loader.prop` properties file and add a reference the UDRL-VS library. You can then create your own loader and either use our example loader functions or write your own. More information on all of the above can be found in the kit’s README.

![](https://www.cobaltstrike.com/app/uploads/2023/09/Cobalt-author-photo.png)

#### [Robert Bearsby](https://www.cobaltstrike.com/profile/robert-bearsby)

Senior Cybersecurity Researcher

[View Profile](https://www.cobaltstrike.com/profile/robert-bearsby)

TOPICS


- [Development](https://www.cobaltstrike.com/blog?_sft_cornerstone=development "Development")
- [Red Team](https://www.cobaltstrike.com/blog?_sft_cornerstone=red-team "Red Team")