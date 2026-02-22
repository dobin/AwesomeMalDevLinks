# https://blog.slowerzs.net/posts/thievingfox/

# ThievingFox - Remotely retrieving credentials from password managers and Windows utilities

###### January 21, 2024

ThievingFox is a collection of post-exploitation tools, used to gather credentials from workstations and servers in the context of penetration tests and similar engagements. It works by making the target application load a malicious library, which performs in-memory hooking to gather credentials.

During pentests, I’ve had great successes using [KeeThief](https://github.com/GhostPack/KeeThief) and mimikatz’s `ts::mstsc` [module](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_ts.c#L335) to gather additional credentials from KeePass and the default RDP client on Windows, on compromised admin workstations.

Using these tools, I found some shortcomings, which `ThievingFox` aims to address, namely:

- Not all administrators are necessarily using these specific applications, which requires identifying potential victims
- Administrators are probably not running with KeePass or the default RDP client at all time, which requires actively waiting for them to open them

While doing so, I added other targets than KeePass and the default RDP client.

The tool can be found on [Github](https://github.com/Slowerzs/ThievingFox).

## Design Considerations

At a high level, ThievingFox works by injecting code inside the targeted application, which then hooks sensitives functionalities, enabling the capture of credentials.
When designing ThievingFox, a few goals were defined.

Firstly, the hooking process should be transparent to the end user - since the goal of ThievingFox is to assist in pentests, it should not impact the use of the application.

Furthermore, the hooking process should be somewhat stable for a given target application. Unlike other tools and proof of concepts that have a similar goal, ThievingFox does _not_ use byte-pattern signatures to identify target functions, because these signatures can be very fragile between environments and versions. This make the finding interesting places to hook more challenging.
Without signatures, we can’t directly hook the functions responsible for processing the credentials, so instead I tried to find libraries with exported symbols, that are somehow used in processing the credentials, to hook them. This makes the hooking more robust, because the external functions from other libraries used are less likely to change across versions and environments.

Finally, many sanity checks are performed to lower the risk of breaking any functionality of the legitimate application.

As a prerequisite to using `ThievingFox`, local administrator privileges must be obtained, and SMB access must not be filtered.

### Active vs Passive injections

Regardless of the targeted application, in order to capture credentials, the application must be hooked.
To be able to hook any function, we must be able to run some code within the targeted process. And, for that, some form of process injection must be performed.

A first option would be to perform some form of “active” injection - a combination of some sort of the `OpenProcess`/`WriteProcessMemory`/`CreateRemoteThread` API calls.

This has several downsides :

- These Windows API and the associated syscalls are heavily monitored by EDR/AV.
- This would require some form of polling to determine whether a victim process is running, which is not ideal for performance reasons.
- To actually perform the polling, the most the common options would be to either use WMI or create a remote process, both of which could be detected and blocked as a form of lateral movement.

All these reasons made “passive” injections preferable. Instead of actively injecting code inside the victim process whenever it is detected, we trick the victim application to load our additional code whenever it is started.
This resolves all main issues: no polling, no lateral movement to actively create a process on a remote host, and “passive” injections do not need to call monitored Windows API.

Different techniques are used to perform these “passive” injections, detailed in later sections.

### Crypto

When any credentials are captured from any application, they must be retrieved by the pentester’s machine before being usable.
At first, an approach of exfiltrating over HTTP was considered, but this requires a permanent listener, and can also be impractical due to firewalling.
The chosen solution ended up being the storage of captured credentials on the target victim filesystem, and waiting for a later point when the credentials are collected from disk, over SMB.

To safely store the credentials on disk, asymmetric cryptography is used - each DLL on the target host embeds a public key, while the private key remains on the machine where `ThievingFox` is ran.

I opted to use [libsodium](https://doc.libsodium.org/) due to its simplicity of use, as well as the presence of bindings in multiple languages (Python, Rust, .NET) - with [Sealed Boxes](https://doc.libsodium.org/public-key_cryptography/sealed_boxes).

## Native Applications

### DLL Proxying

DLL Sideloading is probably the most well-known technique to inject additional code inside a targeted application.
The main idea is to hijack one of the imported DLL by the main executable, by abusing the default configuration of the Windows library loader, which searches the corresponding library name in the folder where the executable is located.

In the case of our targeted applications, DLL sideloading is impractical for Windows binaries - we don’t want to overwrite a DLL inside `C:\Windows\System32` that is used by many other applications, which would risk our malicious DLL being loaded in an unexpected process.

Consequently, DLL sideloading is only used for one application: `KeePassXC`, which ships with multiple DLL, that are nice targets for sideloading. One of the crypto library used by KeePassXC is targeted, `argon2.dll`, and is replaced by our hooking DLL:

![hijacked argon2.dll](https://blog.slowerzs.net/images/ThievingFox/dll_hijacking.png)

To ensure that the original functionalities offered by the DLL we are replacing still work, we re-export the symbols and forward them to the original DLL.
To automate this process, this is done during compilation, using Rust build scripts (an example can be found [here](https://github.com/Slowerzs/ThievingFox/blob/main/consentfox/build.rs)).

This results in the hooking DLL exporting the following symbols :

![argon2.dll exports](https://blog.slowerzs.net/images/ThievingFox/exports_forwarded_to_argon2_bak.png)

As of the first version of `ThievingFox`, `KeePassXC` is the only application where DLL proxying is used.

#### Hooking KeePassXC

To retrieve the masterkey used to unlock a database, we have to hook some external function to which is handed a reference to the masterkey. In `KeePassXC`, the masterkey is very short-lived, and zeroed out as soon as possible.

The only function matching this criteria that I could find is `Botan::Buffered_Computation::update`, which is the method use to update the internal representation to compute a hash of the masterkey. This can also be seen in the source code [here](https://github.com/keepassxreboot/keepassxc/blob/develop/src/crypto/CryptoHash.cpp#L74).

This method is called multiple times, with the masterkey, but also with data we’re not interested in. But with a simple heuristic (ensuring that the character sequence is valid UTF-8, and ensuring that all characters are not null-bytes and other non-printable characters), it is possible to filter out masterkeys from the other type of data.

Now that we know what function we want to target, we have to perform the actual hooking. I chose to perform simple in-memory byte-patching. To do so I used the [minhook](https://github.com/TsudaKageyu/minhook) library, due to its simplicity, its robustness, as well as being easily cross-compilable with Rust (using the [minhook-sys crate](https://crates.io/crates/minhook-sys/)).

All of this makes the retrieval of the maskerkey (and potential keyfile) possible whenever a KeePassXC application unlocks a database :

![KeePassXC masterkey and keyfile retreived with ThievingFox](https://blog.slowerzs.net/images/ThievingFox/keepassxc_poisoning.png)

A similar approach was used to hook other native applications. To identify what exported symbols to use, a combinaison of [API Monitor](http://www.rohitab.com/apimonitor) and manual reverse engineering was used.

### COM Hijacking

What about other native applications ? As we discussed previously, replacing a DLL in `C:\Windows\System32` would not be ideal. Luckily, all Microsoft applications that we are interested in use COM in some form.

COM hijacking enables an attacker to load its own library within a process by simply modifying a registry value. The registry value describes the DLL that is loaded when the application tries to instantiate the corresponding COM class. This is perfect for our scenario !

Not all classes can be hijacked, the executable that implements the functionalities of the class must be implemented in-process. To determine whether a class is suitable, the necessary information is stored is the registry keys associated with the Class ID (CLSID).

Identifying potential COM classes that can be hijacked for a target process can be easily done using [ProcMon](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon) :

![Using Procmon to identify classes that can be hijacked](https://blog.slowerzs.net/images/ThievingFox/com_hijacking_procmon.png)

This process has been repeated for all targeted applications. For each one, a CLSID that was rarely used by other application has been selected.

#### Hooking RDCMan

RDCMan uses CLSID `4EB89FF4-7F78-4A0F-8B8D-2BF02E94E4B2`, which is associated with the MsRdpClient5 class, which contains the interface [IMsRdpClient5](https://learn.microsoft.com/en-us/windows/win32/termserv/imsrdpclient5). This interface implements all the necessary functionalities to create a RDP client, including authentication.
All these functions are implemented inside the `mstscax.dll` DLL. In particular, the function used to hand over the password of the account used for authentication is [`put_ClearTextPassword`](https://learn.microsoft.com/en-us/windows/win32/termserv/imsrdpclientadvancedsettings-cleartextpassword)

Unfortunately, the symbols for these functions are not exported directly :

![Exports of mstscax which do not contain the targeted method](https://blog.slowerzs.net/images/ThievingFox/mstscax_no_exports.png)

But, since the `mstscax.dll` DLL which implements COM method is an in-process server, there is no marshalling to invoke COM methods. This means that we can instantiate our own object, look inside its `vtable` to find directly the address in memory of the functions we’re interested in (the ones related to authentication), and hook them, as we’ve done before for KeePassXC !

This is the approach that is used for both `RDCMan` and `MobaXTerm`, which both use a different version of the `IMsRdpClient` interface.

#### Hooking LogonUI

Hooking `LogonUI.exe` isn’t any different to hooking other native application (in ThievingFox, a combination of COM hijacking and library hooking is used for `LogonUI.exe`). However I wanted to highlight the impact.

`LogonUI.exe` is the process responsible for handling credentials when a user who is physically present on the computer unlocks his session. In addition, `LogonUI.exe` also handles credentials used for RDP connections (at least, when Restricted Admin is not used).

This means that if a server is poisoned, and an administrator uses RDP to connect to this server, its credentials are captured:

![Poisoning of LogonUI.exe](https://blog.slowerzs.net/images/ThievingFox/logonui_poisoning.png)

While not all credentials that end up in `lsass.exe` go through `LogonUI.exe`, but a significant proportion of them do, which is a different way of gathering credentials without touching the actual `lsass.exe` process.

## .NET Framework applications

### AppDomainManager Injection

Applications that are built using the .NET Framework can use a feature named `AppDomainManagers`.
An `AppDomain` is an instance of the .NET virtual machine within a process. As such, a process can contain multiple `AppDomains`, to host different applications withing the same process.
An `AppDomainManager` is a managed library that controls how `AppDomains` are created, destroyed, etc. within a process.

What’s interesting about `AppDomainManagers` is that they can be specified in the config file that is shipped with .NET Framework application, as stated in the [documentation](https://learn.microsoft.com/en-us/dotnet/framework/configure-apps/file-schema/runtime/appdomainmanagerassembly-element).

The only target application (for now) written in .NET Framework is KeePass.

ThievingFox edits the configuration file to add an `AppDomainManager`, which points to our hooking library:

![Edited KeePass.exe.config](https://blog.slowerzs.net/images/ThievingFox/appdomainmanager_injection.png)

#### Hooking KeePass

Unlike native application, hooking the main binary itself is possible : reflection enables us to find functions inside the main assembly that receives the credentials, without any byte-pattern to identify functions.

The actual hooking is also different: the function that we will be hooking is a function written in .NET, so it will be much easier to manipulate its arguments if our hook is also in managed code.

![Image of KeePass masterkey and keyfile retreived with ThievingFox](https://blog.slowerzs.net/images/ThievingFox/keepass_poisoning.png)

To perform the patch we retrieve the native function pointer associated with the `Method` objects associated with the hook and the target function, and simply switch the pointers.

Before switching pointers, we ask the CLR to JIT-compile the hook and the target function, to ensure they are implemented in native code and are not emulated by the CLR VM, and do not move in memory. I also ensure that both the hook and the original function have the same prototype, to be able to manipulate the arguments.

This has a downside : previous versions of the CLR runtime would not necessarily work the same way and as such, switching functions pointers like this might not work. Luckily, most recent versions of .NET frameworks behave this way. Sanity checks have been added to ensure that if we cannot retrieve a correct function pointer, nothing happens.

## Hardening

So what can be done about it ?

The general stance, at least for [KeePass](https://keepass.info/help/base/security.html) and [KeePassXC](https://keepassxc.org/blog/2019-02-21-memory-security/), is that if a malicious application is running on the computer, there is nothing that can be done about it.

KeePassXC takes a measure against “active” injections: it modifies the ACL of its own process handle, to deny access to everyone, including the current user - [relevant source code](https://github.com/keepassxreboot/keepassxc/blob/884386c924192902dc9500a58f9cbdfe22a0a4fd/src/core/Bootstrap.cpp#L121).

While this does not prevent privileged users from getting a handle the KeePassXC by using the `SeDebugPrivilege`, it is a good measure if a low-privileged user is using KeePassXC and this same user is also running a malicious application.

KeePass has the same feature, although the configuration option `Configuration/Security/ProtectProcessWithDacl` must be configured manually, as stated in the [documentation](https://keepass.info/help/v2_dev/customize.html#opt).

Some applications, like Chrome, prevent passive injections by enforcing that all DLL are Microsoft-signed, using [`PROCESS_MITIGATION_BINARY_SIGNATURE_POLICY`](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-process_mitigation_binary_signature_policy). This would require that all dependencies used by the applications are signed, and would prevent the use of third-party plugins.
However, several [other](https://gist.github.com/mgeeky/6ce72a464a691f5c105fffa1bddab301) [techniques](https://blog.quarkslab.com/post-exploitation-abusing-the-keepass-plugin-cache.html) exist to force KeePass to export unencrypted database, without injection.

Unfortunately Windows does not offer any mechanism other than PPL for Anti-Malware (that I know of) to protect sensitives third-party user-mode applications. As such, credentials manager, cannot benefit from this. VirtualBox tries to emulate this protection mechanism, but this requires a device driver and complex user mode [code](https://www.virtualbox.org/browser/vbox/trunk/src/VBox/HostDrivers/Support/SUPR3HardenedMain.cpp#L168).

### What’s next

As of the publication of this article, the following applications are targeted by `ThievingFox` :

| Application | Injection Method |
| --- | --- |
| KeePass.exe | AppDomainManager Injection |
| KeePassXC.exe | DLL Proxying |
| LogonUI.exe (Windows Login Screen) | COM Hijacking |
| consent.exe (Windows UAC Popup) | COM Hijacking |
| mstsc.exe (Windows default RDP client) | COM Hijacking |
| RDCMan.exe (Sysinternals’ RDP client) | COM Hijacking |
| MobaXTerm.exe (3rd party RDP client) | COM Hijacking |

For future versions of `ThievingFox`, I intend to target other applications. In particular, credential managers that use the Electron Framework ;)

## Related work

- [KeeThief](https://github.com/GhostPack/KeeThief) on retrieving credentials from running KeePass processes - by [Lee Chagolla-Christensen](https://twitter.com/tifkin_) and [Will Schroeder](https://twitter.com/harmj0y)
- Mimikatz’s `ts::mstsc` [module](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_ts.c#L335) on retrieving credentials from running mstsc processes - by [Benjamin Delpy](https://twitter.com/gentilkiwi)
- [RDPThief](https://www.mdsec.co.uk/2019/11/rdpthief-extracting-clear-text-credentials-from-remote-desktop-clients/) on hooking mstsc.exe to capture credentials - by [Rio Sherri](https://twitter.com/0x09al)
- [KeePassHax](https://github.com/holly-hacker/KeePassHax) on retrieving KeePass masterkeys in memory - by [holly-hacker](https://github.com/holly-hacker)