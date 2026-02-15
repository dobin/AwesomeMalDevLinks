# https://www.huntress.com/blog/silencing-the-edr-silencers

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F6a889f843f1c43a695dc53a813b091e2)

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F9f33356fc04f46a2ac4a68753ba41658)

[Home](https://www.huntress.com/)![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F779e332a141048329fb98c924119138a) [Blog](https://www.huntress.com/blog) ![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F779e332a141048329fb98c924119138a)

Silencing the EDR Silencers

Last Updated:

[November 18, 2024](https://www.huntress.com/)

# Silencing the EDR Silencers

By:

[![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Ffd9313cd495648cebe8b5840aa07d062)\\
Jonathan Johnson](https://www.huntress.com/authors/jonathan-johnson)

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F948a594740d14aeebdbbad48fcac5a15)

![Share icon](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Fe499a4a7ecac4052ab9e5c194b638f16)

![Glitch effect](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Fc2118b00ed614bbf83f96f25de0beaf8)![Glitch effect](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Fc2118b00ed614bbf83f96f25de0beaf8)![Glitch effect](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F0658aac7c84b4f7e9a7c7b2a5b519b28)

As many security practitioners know, tampering with Endpoint Detection and Response (EDR) products is a deep desire for threat actors and red teamers alike. I spoke about this briefly at BlackHat this year in my “EDR Blinded, Now What?” Huntress booth talk.

![__wf_reserved_inherit](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Fb8fe7e11696c499bbe999f67799f3261)

_Speaking at BlackHat. Photo cred to my twin_ [_John Hammond_](https://www.huntress.com/authors/john-hammond) _._

In one of the slides, I talked about how one of the most common ways to “blind” EDRs is to apply firewall rules against the desired EDR applications. This technique is unique in the way that an attacker doesn’t need to directly access an EDR’s application themselves (open a handle to the process or file). Instead, they alter the application’s ability to communicate outbound to their server, as well as alter the server’s ability to communicate inbound to the application. So, although the EDR can collect telemetry of an action, those actions aren't being sent up for detections or investigations. In this blog, I'll touch on this technique and discuss how products can protect themselves from this attack.

## Blocking Mechanisms

While we discuss the various ways one might block application's network communications, two ways really come to mind that are the most prevalent today:

1. Creating Windows Defender Firewall with Advanced Security rules
2. Creating Windows Filtering Platform (WFP) rules

Now, that might sound repetitive because it slightly is. That’s because the built-in Windows Defender Firewall leverages the Windows Filtering Platform to enforce its rules. However, I call it out because, as we’ll see later, we have to adjust the solution because depending on how you interact with each feature, the settings are set in different locations.

**_Note:_** _Before we proceed, it’s important to state that we’ll only be looking at default Windows firewall capabilities, not third-party ones. This blog also only focuses on when firewall rules are set via the Windows Firewall or WFP._

### Windows FirewallI

The [Windows Firewall](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/) has the ability to create custom rules that either allow or disallow an application to speak out through the network. Both inbound and outbound. There are no restrictions on which processes are targeted by these firewall rules, so as long as an attacker has local administrator rights they can successfully add an EDR agent into the firewall rule and block network connections. Most people have probably seen the following page as it relates to the Windows Firewall:

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F410c0153e006427898348809d0b070b9)

_Figure 1: Windows Defender Firewall with Advanced Security Window_

There is also an easy built-in tool to create firewall rules called **netsh**:

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Fe70c793136534ebbac7ec8eff925743e)

_Figure 2:_ **_netsh advfirewall_** _example_

For something more custom, someone could leverage the [INetFwRule](https://learn.microsoft.com/en-us/windows/win32/api/netfw/nn-netfw-inetfwrule) and [INetFwRules](https://learn.microsoft.com/en-us/windows/win32/api/netfw/nf-netfw-inetfwrules-add) COM interfaces. Users can implement this themselves quite easily. A well-known tool that does this is [EDRSandblast](https://github.com/wavestone-cdt/EDRSandblast/blob/0710fad92dbcdf373ed30c536b99012fcd46dbcc/EDRSandblast/Utils/FirewallOps.cpp#L140), which eventually leverages the [Add](https://learn.microsoft.com/en-us/windows/win32/api/netfw/nf-netfw-inetfwrules-add) method in the **INetFwRules** COM interface to create a new firewall rule against a known EDR binary.

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F95bbe3615ff7403b909db330a3110122)

_Figure 3:_ **_EDRSandblast_** _firewall creation example_

Now, it’s good to note that with Windows AV turned on, Defender does block firewall rules being made against **MsMpEng.exe**. However, the key point is that this can be done against any EDR, and if they’re not monitoring, the network communications will be cut off. When these firewall rules are created, they’re actually stored in the registry under:

**HKLM\\System\\CurrentControlSet\\Services\\SharedAccess\\Parameters\\FirewallPolicy\\FirewallRules\\{GUID}**

**{GUID}** represents the firewall rule. This is stored as a **REG\_SZ** value where the data holds the information about the rule:

**`v2.32|Action=Block|Active=TRUE|Dir=In|App={application-path}|Name={firewall-rule-name}|Desc={firewall-rule-name}|`**

Let’s touch on the most important bits of this rule:

- **Action** \- the firewall action to take (allow or block)
- **Active** \- whether or not the firewall rule is currently active or not
- **Dir** \- direction to permit or deny communication between either In(bound) or Out(bound)
- **App** \- the application to block or allow
- **Name** \- firewall rule name
- **Desc** (optional) - description of the firewall

There are other optional flags that can be put into the string as well. The three biggest tags here are **Action**, **Dir**, and **App**.

So before we move forward into the WFP, let’s remember the registry key **HKLM\\System\\CurrentControlSet\\Services\\SharedAccess\\Parameters\\FirewallPolicy\\FirewallRules\\{GUID}**. This will come in handy later when we discuss solutions.

### Windows Filtering Platform (WFP)

The Windows Firewall leverages the [Windows Filtering Platform](https://learn.microsoft.com/en-us/windows/win32/fwp/windows-filtering-platform-start-page) to enforce its rules. Here, we won’t go in-depth about the internals of the WFP simply because we believe that a lot of other great researchers have. In fact, the following are great resources:

- [Understanding Network Access in Windows AppContainers](https://googleprojectzero.blogspot.com/2021/08/understanding-network-access-windows-app.html) by [James Forshaw](https://x.com/tiraniddo)
- [What The Filter (WTF) is Going on With Windows Filtering Platform](https://zeronetworks.com/blog/wtf-is-going-on-with-wfp) by [Sagie Dulce](https://x.com/SagieDulce)

Interacting with the WFP is a lot easier because there are direct APIs that we can take advantage of. A list of WFP APIs can be found [here](https://learn.microsoft.com/en-us/windows/win32/fwp/api-sets). For purposes of creating a WFP filter, the desired API is [FwpmFilterAdd0](https://learn.microsoft.com/en-us/windows/win32/api/fwpmu/nf-fwpmu-fwpmfilteradd0). Many reading this blog have likely heard of [EDRSilencer](https://github.com/netero1010/EDRSilencer). This function is leveraged to [create a WFP filter](https://github.com/netero1010/EDRSilencer/blob/57f6bb6b24f88f781eda2f3ebad8e781a8a61c0c/EDRSilencer.c#L200C26-L200C40) for both IPv4 and IPv6 addresses. When these rules are applied, there are two things that have to exist:

- A provider - policy provider that is used for the management of the filter
- A filter (inbound and outbound) - rule that if the conditions are met, takes the actions specified

There are four types of run-time filters that users can interact with. [**Dynamic**](https://learn.microsoft.com/en-us/windows/win32/fwp/object-management), [**Static**](https://learn.microsoft.com/en-us/windows/win32/fwp/object-management), [**Persistent**](https://learn.microsoft.com/en-us/windows/win32/fwp/object-management), and [**Built-in**](https://learn.microsoft.com/en-us/windows/win32/fwp/object-management). The most valuable are persistent filters to an attacker, as they live until the filter is removed. When filters are set, they’re stored in the registry just like firewall rules, just in a different location:

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Ff54db50abcc34a4898d2d7fe19bd61b7)

_Figure 4: Procmon output of WFP filters and provider being set_

Each provider and filter is stored as a {GUID}value, and the filter data is stored as a byte array ( **REG\_BINARY**).

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Fc2cc7629fb25403f984a32965ab7455a)

_Figure 5: WFP filter byte array example_

This can make parsing this data a little more difficult than the firewall rules above just because it isn’t just a simple string value. However, an easy way to interact with filters is with the **Get-FwFilter** PowerShell cmdlet. For example, you can get the information about a filter via the **Get-FwFilter** cmdlet if you have the **FilterId** or **FilterKey**:

##### **FilterID**

Loading Gist...

##### **FilterKey**

Loading Gist...

This is a great option if you’re curious what a specific filter is doing on your machine. Now, let’s see how to stop this from happening against an EDR application!

## Solution

We’ve identified that firewall rules and WFP filters are both eventually set in the registry. This is great for anyone trying to pick up on this activity because there are multiple ways to monitor the registry. We’d like to propose two avenues that a product could take if they want to stop this tampering technique in its tracks: **Prevention** and **Immediate Removal**.

### Prevention

Products can either prevent it by leveraging a pre-callback routine for **RegSetValue**( [RegNtPreSetValueKey](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ne-wdm-_reg_notify_class)). If a product has access to the kernel via a driver, then they could leverage [RegNtPreSetValueKey](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ne-wdm-_reg_notify_class) to receive notifications when any registry value set operation is performed in the registry. Upon doing so, they could parse out the registry path and the data being set, and if it matched, they could return **STATUS\_ACCESS\_DENIED** to prevent that key from being set. A successful implementation would look something like the following:

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Ffde8210438e4416a983870bbe5f775c9)

_Figure 6:_ **_EDRSandblast_** _failing to create firewall rules_

You can see that the firewall rules aren't successfully created because they're blocked through the registry pre-callback **RegNtPreSetValueKey** notification. This works great from a prevention standpoint, but to be honest, I don’t always think it’s a good idea to parse or process data in the kernel unless it’s really lightweight. And although this works well for the firewall rules, that data is stored as a string value, where the WFP filters are stored as a byte array. Like the firewall rules above, this shouldn’t be processed/parsed in the kernel.

### Immediate Removal

The methodology of “immediate removal” is similar to the method above, except that you’re technically allowing the undesired action to take place before doing anything about it. This can be done by monitoring for these registry value set operations via a post-callback ( [RegNtPostSetValueKey](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ne-wdm-_reg_notify_class)). This callback is notified once the action has already taken place in the registry. Now, someone could still process/parse this data in the kernel and deal with it, but I recommend storing the post-callback data and shipping it down to a user-mode agent so that it can take care of the parsing and processing. Figure 7 shows a very high-level architecture of how this can be done. There are many ways to do this, and this isn’t the only right way, but this is just how I did it when I created the proof-of-concept within [JonMon](https://github.com/jsecurity101/JonMon).

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Fa7a7630d666643f5bf3ef1a04fb0da4e)

_Figure 7: Basic EDR architecture for registry post-callback_

Once the data is successfully shipped down to the user-mode agent and parsed, then the agent can safely get rid of the rules. You can’t just delete the registry keys because the rules/filters aren't immediately reset. Instead, you must remove them in a way so that the filtering engine refreshes after the removal. You could delete the registry key, but then you’d have to reboot the machine. Obviously, this approach isn’t an appropriate option, as products want to do modifications during runtime. There are some effective options to achieve this, however. For firewall rules, I leveraged COM to do this:

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F4016c0b306ef4ede9a77156d386cc09b)

_Figure 8: Code example for_ **_INetFwRules::Remove_**

I validated that the registry value held the undesired firewall policy and used the [INetFwRules Remove Method](https://learn.microsoft.com/en-us/windows/win32/api/netfw/nf-netfw-inetfwrules-remove) to remove the firewall policy. Figure 9 shows how it looks after implementation:

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Fe4d4426d34fa4669acbb9036f2457633)

_Figure 9: Example of malicious firewall rules being removed in real-time_

You can see the rules were successfully created but immediately removed, rendering the tampering technique useless.

For the filters and providers within the WFP, I leveraged the [FwpmFilterDeleteById0](https://learn.microsoft.com/en-us/windows/win32/api/fwpmu/nf-fwpmu-fwpmfilterdeletebyid0) function to delete the filter and the [FwpmProviderDeleteByKey0](https://learn.microsoft.com/en-us/windows/win32/api/fwpmu/nf-fwpmu-fwpmproviderdeletebykey0) function to delete the provider.

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F0f20a60e8071478d8cf9af63cc1ae908)

_Figure 10: Code example of removing malicious WFP filters and providers_

After this is implemented, we can see the filters and providers that are created, with EDRSilencer successfully deleted:

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F79913ee9d78146d0830a7a4abd7fccf5)

_Figure 11: Example of malicious WFP filters being removed in real-time_

While this method might not be "preventing" the rules from being written, it's just as effective. The product doesn’t need to parse and process this data in the kernel, and the removal is almost immediate. Lastly, you don’t have to use the registry callbacks, as the WFP has the [5447](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5447) security event that states when a new rule is created. Someone could monitor for that and perform the same actions as above to remove that rule.

## Conclusion

Tampering with EDRs is a very hot topic, and I see many people talking about leveraging firewall policies and WFP filters to blind EDRs. It’s clear this is very effective. It’s also unique, as the attacker doesn’t have to interface with the EDR’s processes directly. I’ve yet to see anyone go in-depth on how to stop or mitigate this tamper technique, so I wanted to provide some potential solutions. I hope this helps you understand this tampering technique better and how to mitigate it.

Want to dive into even more attacker techniques? [**Join us at Tradecraft Tuesday!** No products, no pitches—just tradecraft.](https://www.huntress.com/tradecraft-tuesday)

![Glitch effect](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F97d1ebf9f67945c9af2c6341e585bc21)

## You Might Also Like

[![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F642541cb00fe4e90a07832fed51581a9)\\
\\
**Looking Through a Pinhole at a Qilin Ransomware Attack** \\
\\
Learn More![right arrow](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F779e332a141048329fb98c924119138a)](https://www.huntress.com/blog/looking-at-qilin-ransomware-attack)

[![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F23d4b0b97a6c44119d5cf9c5ff789138)\\
\\
**The Crown Prince, Nezha: A New Tool Favored by China-Nexus Threat Actors** \\
\\
Learn More![right arrow](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F779e332a141048329fb98c924119138a)](https://www.huntress.com/blog/nezha-china-nexus-threat-actor-tool)

[![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Fc5ca2c6f28994ad1877490baf68255c5)\\
\\
**Gootloader Returns: What Goodies Did They Bring?** \\
\\
Learn More![right arrow](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F779e332a141048329fb98c924119138a)](https://www.huntress.com/blog/gootloader-threat-detection-woff2-obfuscation)

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Fe4c269018ce94700a59e351c5b9edb99)![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F1aa59311842f4ca6bda70300ff181cf9)![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2F9ad6bcb77d1842b98142269ef70c4f47)

## Sign Up for Huntress Updates

Get insider access to Huntress tradecraft, killer events, and the freshest blog updates.

Work Email\*

[Privacy](https://www.cloudflare.com/privacypolicy/) • [Terms](https://www.cloudflare.com/website-terms/)

Submit

By submitting this form, you accept our [Terms of Service](https://www.huntress.com/terms-of-use)& [Privacy Policy](https://www.huntress.com/privacy-policy)

Thank you! Your submission has been received!

Oops! Something went wrong while submitting the form.

![](https://cdn.builder.io/api/v1/image/assets%2F3eb6f92aedf74f109c7b4b0897ec39a8%2Fcb5efa5143804ba59d530a903d29fe5f)

![](https://cdn.builder.io/api/v1/pixel?apiKey=3eb6f92aedf74f109c7b4b0897ec39a8)