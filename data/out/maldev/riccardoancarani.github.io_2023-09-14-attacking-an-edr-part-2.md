# https://riccardoancarani.github.io/2023-09-14-attacking-an-edr-part-2/

# Introduction - Where we left off

DISCLAMER: This post was done in collaboration with Devid Lana. You can find his blog here: [her0ness - Attacking an EDR Part 2](https://her0ness.github.io/2023-09-14-Attacking-an-EDR-Part-2/)

Continuing from our last research, we pursued the exploration of the attack surface of the EDR solution under our scrutiny, STRANGETRINITY. Last time we focused on identifying exclusions within the EDR’s configuration that allowed us to perform actions that would not be possible otherwise. This time around, our focus will be on the communication channel between the EDR agent and its tenant.

For those who are not familiar with the generic EDR architecture, in most cases the agents that will be deployed on the systems will eventually need to communicate to a centralized tenant. This is usually done because EDR agents needs to:

- Fetch policies from the centralized tenant and apply new policies
- Send telemetry back to the central instance

As you can imagine, this component is particularly crucial and any interference or tampering could potentially have devastating outcomes. As we did last time, we will begin with formulating an hypothesis that will be validated throughout the rest of this blog post.

In this instance, as it was preannounced in this section, our hypothesis was the following:

_Would an attacker, that is in an advantaged network positioning, be able to intercept and tamper with the EDR client-server communication? And if so, what harm could it cause?_

# The Vulnerability

In general, in order to intercept and tamper with networking communications from one host to another, one of the following conditions must be met:

- You are in the same local subnet as the victim host, and you can also exploit vulnerabilities in the TLS communication to intercept encrypted traffic. This was the less-likely scenario, as we rarely - if ever - are in a similar situation.
- You have a foothold on the victim host. This likely requires administrative privileges to either modify the networking configuration or somehow divert traffic of privileged processes (the EDR in this case).

With the second scenario being the most realistic one, we assumed that we obtained administrative access to the host and we somehow want to either:

- Tamper with the solution to execute our malicious instructions.
- Impede the EDR’s functionalities and prevent it from doing what it is supposed to do

Command execution is always interesting, however, we were also aware that the boundary between administrative access to EDR disarm is also quite relevant as vendors seem to be concerned with admin users being able to uninstall their software without approval from the centralized tenant. That objective seemed to us more achievable with the time that we allocated for this research sprint and our past experience with this vendor suggested that a bug in this component could potentially give us a decent payout.

For the readers that are not familiar with these concepts, EDRs at the end of the day are software like many others. This means that they somehow need to be installed, and at some point, uninstalled. In the early days, it was possible to remove EDRs from a host with the same commands that you would use to remove any other type of installed program. A proof that this was possible is the [Atomic Test to uninstall CrowdStrike](https://atomicredteam.io/defense-evasion/T1562.001/#atomic-test-21---uninstall-crowdstrike-falcon-on-windows) that was published a while ago. It did not take too long before attackers started realizing that this was a thing and implemented it in their arsenal. Furthermore, a whole class of attacks that aimed at stopping defensive products’ functionalities emerged and nowadays it is quite common to see multiple strategies being employed to achieve that, from junky BAT scripts to exploitation of vulnerable drivers. On the other side, vendors started to implement a class of features commonly referred as “anti tampering” to prevent any unauthorized program to stop the defensive software from running. MITRE captured some of this knowledge in ATT&CK  project:  [Impair Defenses: Disable or Modify Tools, Sub-technique T1562.001](https://attack.mitre.org/techniques/T1562/001/). This boundary seemed silly for a lot of folks in IT, and multiple times during our time as consultants we have been told: “It is an impossible scenario, we do not give administrative access to our users”. Despite this being a fair statement, evidence is once again more important than beliefs and biases as there are countless threat intelligence reports that documented how attackers might employ valid credentials, exploit internet-facing assets and much more to end up in that position; this, without even counting how it has been trivial within most organizations to elevate privileges by abusing Active Directory functionalities, tends to be a very valid counter-argument that can hardly be contested. This whole paragraph was to, essentially, reiterate on the concept that this boundary is considered important, and rightfully so.

Generically, in order to change the configuration of something, you need to be able to read it first (or in the worst case, empirically determine changes by interacting with a specific component). The rest of this section will describe how the configuration of our EDR was extracted.

# Configuration Extraction

The technical activity began with a thorough reconnaissance of the attack surface exposed by the product, initially analyzing if any COM servers were registered. Fortunately for us, the assumption proved to be true, and the EDR instantiates two COM classes, that we will call `COMTRINITY_A` and `COMTRINITY_B`.

After scrutinizing the classes, the methods exposed by them were analyzed, with the aim of detecting the presence of any functionality that could be exploited to our advantage. Unfortunately, many of the methods turned out to be unusable due to the restrictions applied at the ACL level, allowing their use only by a virtual service account belonging to the `NT SERVICE\\STRANGETRINITYService` solution.

However, we managed to find an exception and a specific method that we will call `StrangeTrinityAgentStatus()` was accessible by every user part of the Administrators group.

Calling the method returns the status of the agent, the enabled security features and the URL of the remote tenant.

The following is a sample of the content:

```
{
 "agent-unique-id": "8fb4b3fc-4576-11ee-be56-0242ac120002",
 "agent-last-checkin": "2020-02-12",
 "tenant-url": "https://tenant-management.strangetrinity.com",
 "anti-tampering": "TRUE",
 "installed-site": "site123456",
 "agent-version": "2.0",
 "some-other-random-params": "foobar"
}
```

As it is possible to see from the snippet above, a field named “anti-tampering” was present. This reinforced our hypothesis that setting was configurable in some way. Moreover, since this was a research effort and not a black box test, the EDR’s cloud tenant was used to verify that.

A very brief exploration of the web-based functionalities of the EDR showed that indeed it was possible to disable anti-tampering features from the cloud console. The next step that we followed was intercepting the communication from the EDR agent to the tenant, trying to reverse engineer the communication protocol and eventually attempt to manually trigger the disarm of the anti-tampering feature.

## Traffic Interception

Luckily for us, the communication from the agent to the tenant was done using the HTTPS protocol, this allowed us to rely on a very well established set of tools for testing. Since the traffic was found to be encrypted with normal HTTPS (this was verified using Wireshark), our idea was to install a `rogue CA` on the host and perform SSL inspection and traffic manipulation. This is a pretty common technique that enterprises use all the time to monitor traffic on their network. Most vendors rely on the installation of a trusted CA on the user’s endpoints to allow SSL interception.
For simplicity, the attack was performed using an intercepting proxy, like BurpSuite or Zed Attack Proxy, clearly, it’s not necessary to emphasise that all of this could easily be weaponized without installing additional software.

The steps we took for the setup were the following:

1. Add a new entry to the hosts file, resolving the DNS record of the management tenant to the localhost address
2. Start a proxy on port 443, enabling invisible proxying
3. Wait for the Agent check-in

A better explanation on how to configure Burp (the software we actually used) this particular scenario can be found here: [Invisible proxying - PortSwigger](https://portswigger.net/burp/documentation/desktop/tools/proxy/invisible). Using the invisible proxying was necessary, as the EDR agent was not proxy-aware.

After a bunch of seconds, the agent checked in and sent a bunch of HTTP requests to the Management Tenant via REST APIs.

The communication mechanism used was a typical client-server poll architecture, with the EDR sensor calling back at regular intervals to ask for updates from the tenant and at the same time send periodic telemetry, unsurprisingly similar to an enterprise-grade Command and Control.

In response, it received another JSON containing a list of additional settings and configurations.

```
"config-data": {
 "sendingData": [\
  "sent.data"\
 ],
 "some": "some",
 "other": "other",
 "params": "params",
 "engineData":{
  "os.data" : "data",
  "status.data" : "data",
  "behavioural.data" : "data",
  "reputation.data" : "data",
  "exploit.data" : "data",
 }
 "agent-unique-id": "8fb4b3fc-4576-11ee-be56-0242ac120002",
 "threat-hash": "hash",
 "scanner-module": "behavioural",
 "anti-tampering": "TRUE",
 "installed-site": "site123456",
 "agent-version": "2.0",
 "agent-logging-event": "true",
 "kernel-protection": "true",
 "some-other-random-params": "foobar"
}
```

Now all that’s left is to tamper with the request and manually modify the parameter settings through the proxy, setting the `anti-tampering` field to `false`.

As mentioned already, the anti-tampering feature typically includes measures to protect the EDR software and its components from unauthorized modifications. This could involve techniques such as code integrity checks, PPL level protection, encryption of sensitive data, and controls to prevent unauthorised changes to configuration settings. The goal of the anti-tampering feature is to ensure that the EDR solution remains operational and resistant to attacks that might attempt to compromise its functionality.

At this point, the configuration of the agent was fetched again to confirm whether our actions had any impact. To our immense surprise, such a small change effectively disabled the anti-tampering feature, and this was even reflected in the configuration retrieved dynamically.

As a final test, we spawned a high-integrity command prompt, successfully managing to halt several components of the product. We also modified registry keys, ensuring that upon the next reboot, the solution would be completely defeated. To do that, we mostly relied on the `sc.exe` binary used to stop services and other utilities used to suspend running processes.

# Proof Of Concept

The following Powershell code was used to retrieve the configuration of the agent:

```
$clsid = New-Object Guid “{GUID}”
$type = [Type]::GetTypeFromCLSID($clsid)

$object = [Activator]::CreateInstance($type)
$object.StrangeTrinityAgentStatus()**
```

The disclosure also included the code for a custom HTTPs proxy, however, considering that the same effect can be obtained with tools such as BurpSuite, publishing that would add no value to this research.

# Outro

As we can infer from the analysis, the communication between the tenant and the agent constitutes a pivotal aspect of any EDR solution. This communication not only allows the collection and transmission of telemetry from endpoints to a centralised cloud for further analysis but also enables swift implementation of configuration changes that need to be cascaded across the entire environment.

From an attacker’s perspective, the ability to intercept and arbitrarily modify such parameters can certainly provide tactical and operational advantages. This allows them to gain a sufficient time window to execute post-exploitation actions without triggering alerts from the solution and, subsequently, quickly restore the communication returning the environment to a normal state. In fact, various bugs can be found by tampering with the communication channel. From what it was possible to infer, the development of that specific component was not appropriately threat modelled and no appropriate testing was performed.

Having said that, similarly as what was done in part 1 of this series, the vendor positively responded to the disclosure and applied the patches so that performing the same attack would not be trivial anymore.

If you are concerned that the products that you use might be affected by a similar issue, it is recommended to repeat the steps outlined in this research and technically validate that. Vendors should implement stronger controls and integrity checks to ensure that the messages received were not modified in transit.

Tags:


[red-teaming](https://riccardoancarani.github.io/tags#red-teaming)

Share: [Twitter](https://twitter.com/intent/tweet?text=Attacking+an+EDR+-+Part+2&url=https%3A%2F%2Friccardoancarani.github.io%2F2023-09-14-attacking-an-edr-part-2%2F "Share on Twitter") [Facebook](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Friccardoancarani.github.io%2F2023-09-14-attacking-an-edr-part-2%2F "Share on Facebook") [LinkedIn](https://www.linkedin.com/shareArticle?mini=true&url=https%3A%2F%2Friccardoancarani.github.io%2F2023-09-14-attacking-an-edr-part-2%2F "Share on LinkedIn")

- [← Previous Post](https://riccardoancarani.github.io/2023-08-03-attacking-an-edr-part-1/ "Attacking an EDR - Part 1")
- [Next Post →](https://riccardoancarani.github.io/2023-11-07-attacking-an-edr-part-3/ "Attacking an EDR - Part 3")