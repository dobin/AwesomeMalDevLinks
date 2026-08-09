# https://blog.calif.io/p/dark-elevator-windows-install-service

# [Calif](https://blog.calif.io/)

SubscribeSign in

![User's avatar](https://substackcdn.com/image/fetch/$s_!UZ0_!,w_64,h_64,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F489bcdd2-8e9f-4bd1-92c4-09754a4aedd1_144x144.png)

Discover more from Calif

Over 3,000 subscribers

Subscribe

By subscribing, you agree Substack's [Terms of Use](https://substack.com/tos), and acknowledge its [Information Collection Notice](https://substack.com/ccpa#personal-data-collected) and [Privacy Policy](https://substack.com/privacy).

Already have an account? Sign in

# Dark Elevator: Windows Install Service Local Privilege Escalation (CVE-2026-50343)

### A pure-logic, 100% reliable path from a normal user to SYSTEM

[![r0keb's avatar](https://substackcdn.com/image/fetch/$s_!-eE0!,w_36,h_36,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F64485386-3a12-4e15-b893-7cdf4899df76_407x407.jpeg)](https://substack.com/@r0keb)

[r0keb](https://substack.com/@r0keb)

Jul 22, 2026

10

Share

[![Dark Elevator"](https://substackcdn.com/image/fetch/$s_!l9I0!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fc5c62a24-012b-4bb9-8ee0-c7a71990025b_1696x2502.jpeg)](https://substackcdn.com/image/fetch/$s_!l9I0!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fc5c62a24-012b-4bb9-8ee0-c7a71990025b_1696x2502.jpeg)

Today we walk through Dark Elevator, a LPE in Windows 11. We reported it to Microsoft on May 20, 2026, and it is now fixed as CVE-2026-50343.

A normal user can cause `InstallService`, the SYSTEM service behind the Windows app install pipeline, to load an attacker-controlled DLL into the SYSTEM `svchost.exe` process and obtain an interactive `NT AUTHORITY\SYSTEM` shell.

The exploit chains two logic flaws: a writable plugin map in `InstallService`, and a Windows-shipped COM class whose backing DLL a normal user can plant. Because the exploit corrupts no kernel memory, it works deterministically every time. It also needs none of the usual preconditions: no administrator rights, no UAC consent, no reboot, and no service-control permissions over `InstallService`.

The impact is high because code execution lands inside a Microsoft-signed SYSTEM service process. From that position an attacker can install services, create privileged accounts, tamper with protected machine-wide state, access other users' data, disable or bypass local security controls, and establish persistence with SYSTEM privileges.

Tested target:

```
Microsoft Windows 11
Build: 10.0.26200.8457
```

Here is a demo of the exploit on Windows 11 25H2:

[![](https://substackcdn.com/image/fetch/$s_!vECQ!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd8670524-8d99-432b-9fb9-772e14b650ee_800x449.gif)](https://substackcdn.com/image/fetch/$s_!vECQ!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd8670524-8d99-432b-9fb9-772e14b650ee_800x449.gif)

The exploit takes three steps:

1. Add a map entry that points a plugin at an existing COM class whose DLL sits under `C:\ProgramData`.

2. Drop a malicious DLL at that path, a folder any normal user can write to.

3. Ask `InstallService` to activate the plugin.


`InstallService` then loads the attacker's DLL into its own SYSTEM process.

[![Exploit chain: a standard user writes a StaticPluginMap entry, plants a DLL, and triggers InstallService, which loads the DLL as SYSTEM](https://substackcdn.com/image/fetch/$s_!b_5Z!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fc0687f85-9ad3-40f3-bdb0-03467610b3e8_1000x912.png)](https://substackcdn.com/image/fetch/$s_!b_5Z!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fc0687f85-9ad3-40f3-bdb0-03467610b3e8_1000x912.png)

## The Bugs

The exploit chains two separate weaknesses:

1. **A writable plugin map.**`InstallService` runs as SYSTEM and decides which COM class to load by reading `StaticPluginMap`, a registry key that any normal user can write. This lets an unprivileged user point the SYSTEM service at any CLSID.

2. **A user-plantable COM server.** A COM class Windows ships, CrossDevice (`{E9F83CF2-E0C0-4CA7-AF01-E90C70BEF496}`), registers its in-process DLL at a path under `%PROGRAMDATA%` that any normal user can write, and the DLL need not already exist. This lets an unprivileged user supply the DLL that class loads.


The rest of this section walks through each bug in turn.

`InstallService` handles app package installation and runs as `LocalSystem`, so any code loaded into its process runs as SYSTEM. It does the actual install work through fulfillment plugins, and it picks which plugin to load by consulting a static plugin map at runtime.

That map, `StaticPluginMap`, is a set of registry values pairing a plugin id (like `VRStaticMap`) with a COM class id (a CLSID). Whoever can write the map decides which class the service loads. On the tested system, `StaticPluginMap` lives at `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\InstallService\State`, which any normal user can write to. This is the first bug.

[![Trust boundary: a standard user writes StaticPluginMap under HKLM, and the SYSTEM InstallService reads and honors that entry](https://substackcdn.com/image/fetch/$s_!L51R!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe45cacf8-a40a-42e9-aa06-f5f9e0da6893_1000x600.png)](https://substackcdn.com/image/fetch/$s_!L51R!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe45cacf8-a40a-42e9-aa06-f5f9e0da6893_1000x600.png)

Reverse engineering and live debugging of `InstallService` showed that plugin activation works as follows:

```
InstallServiceControl::CreateInstallServiceWork
  -> InstallQueue2::CreateWork
    -> CreateInstallServiceWorkByPlugin
      -> PluginHelpers::IsPluginAvailable
        -> PluginHelpers::GetPluginFromStaticMap
      -> PluginHelpers::ActivatePlugin
        -> PluginHelpers::GetPluginFromStaticMap
        -> CoCreateInstance(mapped CLSID, CLSCTX_INPROC_SERVER, IInstallServicePlugin)
```

Built-in plugin IDs such as `WU`, `XVC`, and `ChainedWork` are handled internally. Any other plugin ID can be made "available" by creating a matching value under `StaticPluginMap`.

Here is the relevant part of `PluginHelpers::ActivatePlugin`, decompiled:

```
IInstallServicePlugin ActivatePlugin(hstring callerOrUserContext,
                                     hstring pluginId)
{
    if (pluginId == L"Microsoft.GamingServices_8wekyb3d8bbwe" ||
        pluginId == L"ChainedWork") {
        ...
    }
    ...
    mapped = PluginHelpers::GetPluginFromStaticMap(pluginId);
    if (mapped) {
        GUID clsid = {};

        if (IIDFromString(mapped.c_str(), &clsid) >= 0) {
            return CoCreateInstance(
                clsid,
                NULL,
                CLSCTX_INPROC_SERVER,
                IID_IInstallServicePlugin);
        }

        factory = get_activation_factory<IActivationFactory>(mapped);
        return factory.ActivateInstance<IInstallServicePlugin>();
    }
    ...
}
```

The exploit takes the static-map branch, where `ActivatePlugin` calls [`CoCreateInstance`](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cocreateinstance)`(clsid, NULL, CLSCTX_INPROC_SERVER, IID_IInstallServicePlugin)`. [`CLSCTX_INPROC_SERVER`](https://learn.microsoft.com/en-us/windows/win32/api/wtypesbase/ne-wtypesbase-clsctx) makes COM load the plugin's DLL into the `InstallService` process, and the final argument, `IID_IInstallServicePlugin` (`{42DFA3DD-F369-478E-B764-0079881E8D8D}`), is just the COM interface the service expects a plugin to implement.

That `clsid` is the one value the exploit gets to choose, and it needs a class whose in-process DLL sits at a path it can write. Registering a new class would need admin, so the exploit reuses one Windows already ships: `{E9F83CF2-E0C0-4CA7-AF01-E90C70BEF496}`, a CrossDevice streaming component. Its [`InprocServer32`](https://learn.microsoft.com/en-us/windows/win32/com/inprocserver32) DLL path already sits under `%PROGRAMDATA%`, which standard users can write:

```
HKLM\SOFTWARE\Classes\CLSID\{E9F83CF2-E0C0-4CA7-AF01-E90C70BEF496}\InprocServer32

(Default)      REG_EXPAND_SZ    %PROGRAMDATA%\CrossDevice\CrossDevice.Streaming.Source.dll
```

`%PROGRAMDATA%` is `C:\ProgramData`, a tree where standard users can create folders and files, and the DLL does not have to exist yet. Even though the attacker cannot touch the HKLM registration, they control what it points to: they just create `C:\ProgramData\CrossDevice\CrossDevice.Streaming.Source.dll` themselves. This is the second bug.

## PoC

Everything needed to build the PoC is in [this folder](https://github.com/califio/publications/tree/main/MADBugs/windows-CVE-2026-50343).

## Disclosure Timeline

- 2026-05-20: Reported to Microsoft.

- 2026-07-14: Fixed by Microsoft as CVE-2026-50343.


Kudos to all the other researchers who independently discovered and reported CVE-2026-50343.

* * *

#### Subscribe to Calif

By Khanh · Launched 3 years ago

Subscribe

By subscribing, you agree Substack's [Terms of Use](https://substack.com/tos), and acknowledge its [Information Collection Notice](https://substack.com/ccpa#personal-data-collected) and [Privacy Policy](https://substack.com/privacy).

[![B.T Channel's avatar](https://substackcdn.com/image/fetch/$s_!I1Bs!,w_32,h_32,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4b4c1622-7134-4569-9f99-a2ed3c64494f_96x96.jpeg)](https://substack.com/profile/510808898-bt-channel)[![Thomas717's avatar](https://substackcdn.com/image/fetch/$s_!JLb9!,w_32,h_32,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F63c822ef-3f59-4091-9a0b-2b1137c5f0ee_366x366.jpeg)](https://substack.com/profile/158382663-thomas717)[![Gia Bui's avatar](https://substackcdn.com/image/fetch/$s_!vWm_!,w_32,h_32,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fb0b1c2bd-6989-4be3-b017-dd0fcb10ccde_144x144.png)](https://substack.com/profile/125418931-gia-bui)[![nop's avatar](https://substackcdn.com/image/fetch/$s_!zsde!,w_32,h_32,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F1e8e1bfe-0a81-49a5-bf6b-2bf8a4db4acd_574x574.jpeg)](https://substack.com/profile/230614358-nop)[![Duc's avatar](https://substackcdn.com/image/fetch/$s_!yqAp!,w_32,h_32,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6b156d17-5fd7-41e3-ac70-aec19b113db0_144x144.png)](https://substack.com/profile/323374404-duc)

10 Likes

10

Share

|     |     |
| --- | --- |
| [![r0keb's avatar](https://substackcdn.com/image/fetch/$s_!-eE0!,w_52,h_52,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F64485386-3a12-4e15-b893-7cdf4899df76_407x407.jpeg)](https://substack.com/@r0keb?utm_source=byline) | A guest post by

|     |     |
| --- | --- |
| [r0keb](https://substack.com/@r0keb?utm_campaign=guest_post_bio&utm_medium=web)<br>low-level enthusiast | [Subscribe to r0keb](https://r0keb.substack.com/subscribe?) | |

#### Discussion about this post

CommentsRestacks

![User's avatar](https://substackcdn.com/image/fetch/$s_!TnFC!,w_32,h_32,c_fill,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack.com%2Fimg%2Favatars%2Fdefault-light.png)

TopLatestDiscussions

[First public macOS kernel memory corruption exploit on Apple M5](https://blog.calif.io/p/first-public-kernel-memory-corruption)

[Apple spent five years building hardware and software to make memory corruption exploits dramatically harder. Our engineers, working together with…](https://blog.calif.io/p/first-public-kernel-memory-corruption)

May 14

104

1

9

![](https://substackcdn.com/image/fetch/$s_!TJW7!,w_320,h_213,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_center/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2c731d5e-68ca-4054-894f-659601de6a66_2048x1536.jpeg)

[Codex Discovered a Hidden HTTP/2 Bomb](https://blog.calif.io/p/codex-discovered-a-hidden-http2-bomb)

[14 years ago, I helped break HTTP header compression, then was asked to review the fix, which became part of HTTP/2. Life has come full circle: today…](https://blog.calif.io/p/codex-discovered-a-hidden-http2-bomb)

Jun 2

35

13

6

![](https://substackcdn.com/image/fetch/$s_!oj_T!,w_320,h_213,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_center/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4bedabfd-d72a-4e69-9121-5abe45efeab0_1200x630.png)

[MAD Bugs: vim vs emacs vs Claude](https://blog.calif.io/p/mad-bugs-vim-vs-emacs-vs-claude)

[We asked Claude to find a bug in Vim. It found an RCE. Just open a file, and you’re owned. We joked: fine, we’ll switch to Emacs. Then Claude found an…](https://blog.calif.io/p/mad-bugs-vim-vs-emacs-vs-claude)

Mar 30•[Calif](https://substack.com/@calif)

37

12

4

![](https://substackcdn.com/image/fetch/$s_!IDy_!,w_320,h_213,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_center/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa219122f-e67e-46e4-b598-c7c6967fedce_798x1314.png)

See all

### Ready for more?

Subscribe