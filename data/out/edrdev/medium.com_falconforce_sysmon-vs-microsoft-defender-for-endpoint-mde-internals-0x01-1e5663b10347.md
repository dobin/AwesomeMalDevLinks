# https://medium.com/falconforce/sysmon-vs-microsoft-defender-for-endpoint-mde-internals-0x01-1e5663b10347

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2Ffalconforce%2Fsysmon-vs-microsoft-defender-for-endpoint-mde-internals-0x01-1e5663b10347&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2Ffalconforce%2Fsysmon-vs-microsoft-defender-for-endpoint-mde-internals-0x01-1e5663b10347&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

[**FalconForce**](https://medium.com/falconforce?source=post_page---publication_nav-a249c8f00490-1e5663b10347---------------------------------------)

·

Follow publication

[![FalconForce](https://miro.medium.com/v2/resize:fill:38:38/1*Uf-Lb331GOxOfVzZeyg7TA.png)](https://medium.com/falconforce?source=post_page---post_publication_sidebar-a249c8f00490-1e5663b10347---------------------------------------)

A team of highly specialized security professionals

Follow publication

# Sysmon vs Microsoft Defender for Endpoint, MDE Internals 0x01

[![Olaf Hartong](https://miro.medium.com/v2/resize:fill:32:32/1*NrDNsO-K9DO3r-Ry-Aj3Dw.jpeg)](https://medium.com/@olafhartong?source=post_page---byline--1e5663b10347---------------------------------------)

[Olaf Hartong](https://medium.com/@olafhartong?source=post_page---byline--1e5663b10347---------------------------------------)

Follow

13 min read

·

Oct 15, 2021

284

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D1e5663b10347&operation=register&redirect=https%3A%2F%2Fmedium.com%2Ffalconforce%2Fsysmon-vs-microsoft-defender-for-endpoint-mde-internals-0x01-1e5663b10347&source=---header_actions--1e5663b10347---------------------post_audio_button------------------)

Share

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*CRPrGqvUD759IHy5L0A_Hw.jpeg)

It is not a big secret that we at FalconForce work a lot with, and are big fans of, both [Microsoft Defender for Endpoint](https://docs.microsoft.com/en-us/microsoft-365/security/defender-endpoint/microsoft-defender-endpoint?view=o365-worldwide) (MDE) and [Sysinternals Sysmon](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon). I still use and maintain my [Sysmon-modular configuration](https://github.com/olafhartong/sysmon-modular) project quite frequently.

One of the questions we quite often get is whether one can replace the other, or whether implementing either of the products is enough. Honestly, like almost everything in in this industry, there is not a conclusive answer to this question.

Clearly both are products with different intentions. MDE is a commercial solution which has the ability to detect and act, besides generating telemetry. On top of that it also comes with an antivirus engine. Sysmon is available for free and purposely built for telemetry generation, detections and response actions need to be built by the operators.

> This blog will primarily focus on the telemetry and detection engineering aspects of both tools.

## Deciding what to use

When it comes to dealing with these two detection sources and choosing between them there are a couple of important things you’ll need to take into account.

**Team maturity;** First of all, the maturity of your team will drive this direction significantly. In order to have a deep understanding and ability to research most modern attacks, an inquisitive mindset as well as some higher grade of experience is mandatory. Doing an honest assessment of the current state and ambition of your team will support the decision making process on which of the two products to focus your efforts on.

**Risk appetite;** Next is the focus of the team, as well as the risk appetite of the organisation. If you are part of an already stretched team or you work for an organisation that has a high degree of risk acceptance it might not be a feasible to spend your time to duplicate efforts or a lot of time on research and development.

**Budget;** As with a lot of things in the world, money plays a big role here too. Working with either (or both) solutions comes at a price. MDE has a per machine/user license fee which includes storage and a mature team will also spend time on developing custom detections on top of the out of the box content. Sysmon is free to use, but requires maintenance of the configuration, shipping and storing the logs and all rules need to developed and maintained by your team.

### Single solution

This is most likely a difficult call to make. Whichever of the two products you (or your management) decides to use, you’ll have to fully commit to its great and weak points; and use is to the best of your abilities. There might be all kinds of internal reasons for the decision, whether it’s budget, staffing availability, or risk appetite. In the end it will come down to knowing your tool intimately and building the best possible detection capability with it. Should you go for this path, you should full commit to utilizing the solution to the best of its capabilities before even considering an additional solution.

We regularly talk to people that want to add Sysmon alongside MDE for additional visibility on a very specific subject without, for instance, utilizing the custom detection capabilities of MDE. Often there is also an acceptable way of doing the same or something similar with what you have already in place.

### Augmentation implementation

Due to the nature of both products, there is quite a bit of overlap in the telemetry generation capability. To save some time in developing duplicate detections on both sets of telemetry, it might be an idea to augment MDE with Sysmon telemetry on the points where it has limited or no capability (yet). Since you are ideally already evaluating your tools on a periodic basis, this direction allows you to cover the blind spots of the other one. Doing so should provide you with a higher detection rate.

Obviously, this entails some overhead since you’re working with two telemetry sets and will also have to ingest and store both of them, which evidently is more expensive. On top of that, the most important thing is to also utilize both products well; so building detections on both of these sources, or combine them into correlated events, to gain the best benefit. This also allows you to better monitor for tampering with each of the solutions.

### Full capability / fallback implementation

From our experience, a lot of actors make an effort to disable AV or bypass EDRs, but Sysmon is often overlooked; which makes it a great addition to the defensive tool set. Therefore, if you have the time, capabilities and resources and the type of organisation where the risk acceptance is on the lower end of the spectrum, it might be a good idea to invest time into developing a configuration and detection repository that overlaps with the EDR and augments its blind spots at the same time. This way you have a fallback mechanism and a second pair of eyes concurrently. Should the attacker become aware of both solutions you’ll have at least some brief additional visibility into their attempts to circumvent or disable it.

In any case, going this route will imply quite some additional work. Not only does it require maintaining two tools, configurations and data streams; also the resulting alerts need to be tended to. There are a lot of possible ways to aggregate the duplicate solutions without adding an additional load to the analyst. The cool part about it is that having this duplicate stream is that also this can tell you something. For example, when there is only one solution firing where you know you have detections on both ends. This might be due to one of the tools failing or being tampered with, or that there is an attack variant that one of the solutions was incapable of spotting.

## Knowing your tools, the strengths and weaknesses

At a first level glance it’s already clear that there is a big overlap between MDE and Sysmon, but both tools also have several unique abilities. One very clear distinction is the ability to load a custom configuration file to Sysmon.

MDE has a huge set of configuration options for telemetry generation, which is updated and downloaded from the cloud frequently and stored somewhere on the operating system. Sadly, at the time of writing, this is not something that is modifiable by customers.

### Theoretical telemetry mapping

The easiest way to compare capabilities can be achieved in several ways through MITRE ATT&CK. One of them is to map the data sources mentioned in all technniques to the telemetry events a tool can produce. Keep in mind this is at best an indicative exercise since not everything can _or will be_ logged.

What we’ve done for the screenshots below is plot the ATT&CK data sources per technique against the [OSSEM Detection Model](https://github.com/OTRF/OSSEM-DM) to show the number of data sources covered by our tool(s), in this case MDE and Sysmon. The darker the color, the more of the per technique mentioned data sources will be theoretically covered by telemetry.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*xylCjm1XtlH9aYgYtajYgw.png)

Sysmon telemetry potential mapping to MITRE ATT&CK.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*YW9f6uVACETWCYiHQ4MjCg.png)

MDE telemetry potential mapping to MITRE ATT&CK.

Close up you can see the mappings in more detail. All ATT&CK data sources are mapped to the proper MDE table and to add detail also the proper ActionType. The score is based on the percentage of data sources having a mapping to a telemetry source.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*cQCuyV3VDKA7Ydrp6jApwg.png)

Zoomed example of MDE potential mapping to show the data source mapping.

As you can see, and might have expected, there is quite some overlap in the potential telemetry available so it might make sense to dig a little bit deeper.

### Telemetry head to head

To be able to properly compare the quality and verbosity of the telemetry of both products, we’ll need to look at the data actually generated. This can, for instance, be achieved by utilizing a set of attack simulation scripts, like the [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) project. Ideally, you’ll do a lot more custom research, but for this exercise in telemetry comparison Atomic Red Team is already quite adequate.

Digging through the generated data in both MDE and Sysmon, and augmented with my experience from a lot of time spent engineering detections on both telemetry sources, we end up with the following comparison overview. This overview is based on what Sysmon has and what MDE offers in comparison.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Vr1__5i73_2c-tBNtuzjuQ.png)

Telemetry completeness comparison between Sysmon and MDE.

Please note that besides the events generated by MDE above there is a wealth of (frequently updated) events it provides telemetry for. An overview of the events available at the time of writing this blog is visible in the screenshot below.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*kOi-A1TuYM761JXOXHAtxg.png)

Current unique capabilities for Sysmon and MDE.

**Telemetry configuration**

To be able to rely on a tool, I always want to know 1) how it gathers its telemetry, and 2) what filters are applied before it ends up in my data analytics platform.

As mentioned before, Sysmon requires you to provide it with a configuration that allows you full control to tell it what to write to the EventLog and what not to log. [Sysmon-modular](https://github.com/olafhartong/sysmon-modular) was built exactly for this and makes it easy to maintain it also for different environments.

## Get Olaf Hartong’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

The same is true up to a certain degree for MDE, the big distinction is that Microsoft 100% determines and maintains this configuration without easy access for the user. This is not a huge problem for most people, but if you want to know what its blind spots are and how it filters or samples this is a different story. As you might expect with a configuration for a complex product as an EDR, there are all kinds of filters applied to keep it performing well and also to keep the data volume sent to the cloud manageable for the vendor. Besides per-event filters MDE has a set of global limits.

![](https://miro.medium.com/v2/resize:fit:438/1*tm-O5dVTppNkGsGGqMnifA.png)

Global settings for MDE.

In most cases all these limits should not be the cause of blind spots, but on some systems this might cause you to miss certain events.

### Telemetry acquisition

In different capacities Sysmon and MDE rely on several [Event Tracing for Windows (ETW)](https://docs.microsoft.com/en-us/windows/win32/etw/about-event-tracing) providers. In short, ETW is a kernel-level tracing facility embedded in Windows that lets you log kernel or application-defined events. ETW is at the core of all Event Logs and a lot more monitoring implementations.

Sysmon only gathers DNS data from ETW and writes to its own ETW provider in order to get all data into the EventLog. Moreover, Sysmon collects all of its other information through kernel callbacks via its own kernel driver.

MDE consists of many building blocks and as one of the sources for its telemetry it uses a large set of (sometimes protected) ETW providers.

ETW is an extremely rich data source that also contains a lot of information that is not required for security purposes. There is a set of filters applied per provider in MDE to not get a firehose of data that will not be utilized.

These filters consist of the Event IDs per provider MDE is interested in, but they also contain some metadata. And more importantly: caps to limit the amount of generated and therefore ingested telemetry.

As an example, the screenshot below shows a part the Microsoft-Windows-TCPIP ETW provider manifest, which can be easily visualized with [ETW Explorer by Pavel Yosifovch.](https://github.com/zodiacon/EtwExplorer) As you can deduce from the very long scrollbar, there are several hundreds of events to subscribe to.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*dKE5hd3UHLrGOjK3nCQY8Q.png)

ETW Explorer example of the Microsoft-Windows-TCPIP provider.

**Kernel Callbacks**

Sysmon relies almost completely on kernel callbacks to get all the information it is able to log. MDE also makes quite some use of this besides the ETW subscriptions. Windows Defender, part of MDE, even has its own callbacks and can work independently from the EDR component.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*P_77HJmTK8HRSAnp2mB0qA.png)

Process, registry, DLL load and thread kernel callbacks set by the respective drivers.

This is also where we are able to see why Sysmon has process termination logging and MDE does not, simply because they don’t have that callback set for the PostOperation of a process, only the PreOperation.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*T0v2sHzufq08cnLjb8ibiQ.png)

Process event callbacks Sysmon, Windows Defender and MDE.

Both engines also do some additional magic on the background to enrich these events. For instance, network callback events do not have the same rich information that gets logged by both engines; this is enriched by caching the process information and adding that to the trace information.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*becOmZGSC43OY4XVXum-IA.png)

A trace of a network callback session, showing limited information compared to a Sysmon or MDE event.

**Sysmon** **telemetry considerations**

As mentioned earlier in this post, the quality of your Sysmon datastream heavily relies on your configuration. Maintaining this configuration requires a certain degree of research and frequent updates to not have blind spots in your telemetry. This argument is obviously equally valid for the detection aspect, where MDE might have an out of the box detection already implemented. With Sysmon there is no option to sample your telemetry, once you configure something to be logged you can expect it to store all of the occurrences.

The upside of this obviously is that you know what you should see and what you have filtered from being logged.

**MDE telemetry considerations**

As we have seen earlier in this blog post, MDE has a wealth of additional information over Sysmon. Not all of the overlapping events are equally matched in verbosity. Keep in mind that Microsoft is running a balancing act between cost, maintainability and performance on the endpoint and bandwidth. They do their best to provide most customers with a good solution, which might be too much for some and falling a bit short in some areas for some others.This is not a criticism, it’s a totally fair business case. Knowing about this is where you can decide what to do about this.

A snippet of the MDE configuration below where it specifies one of the events from the Microsoft-Windows-TCPIP provider us quite a couple of things for this single event.

![](https://miro.medium.com/v2/resize:fit:556/1*OS33A2x4TEibx9G99aPZFA.png)

Partial Microsoft Defender for Endpoint ETW configuration.

Obviously it involves a completed TCP/IP connection event. Some of the fields from the provider are extracted and enriched with the InitiatingProcess information that is derived from the information tied to the [ProcessStartKey](https://docs.microsoft.com/en-us/windows/desktop/ETW/enable-trace-parameters) field. [ProcessStartKeys](https://docs.microsoft.com/en-us/windows/desktop/ETW/enable-trace-parameters) were introduced in [Windows 10 build 1507](https://docs.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-enable_trace_parameters) and are intended to serve as a locally unique identifier for a process.

But this is not all, there are two caps visible there, the ‘globalcap’ of \[undisclosed\] which limits the total number of this event per 24 hours for this machine to that number of events in total. Next, there is also a ‘localcap’, which in this example is named ConnectCompleteFirstSeen. This event also has its own expiration, which in this example is also 24 hours and a localcap for this event specifically. This means that for every event that has the fields names in the fields array only x event(s) per day will be logged.

A simple example will make it more clear to understand the impact of the above configuration to the telemetry and custom detection implications. Let’s say we’re looking at a piece of malware that is executed on a machine and sets up a command and control channel to a server on the internet and keeps checking in approximately every 10 minutes for instructions. With the configuration above, the number of log events of this network activity will be just a limited number of connections to the command and control server; the rest of the beaconing behavior is not stored, since the process and network information is not changing. **Keep this in mind when you’re writing detections or when you are investigating an incident.**

> All ETW-based event types have a configuration like this. Obviously, the parameters and caps differ per event. Make sure to investigate the events important to you.

However, there is a big caveat here. **This is the default behavior of the telemetry engine.** As mentioned before, MDE consists of many components locally installed on the endpoint as well as in the cloud. One of its components is the NetworkProtection module which logs all network traffic to its own ETW provider. Should one of the MDE engines classify the binary or the traffic as suspicious, it can decide to send more telemetry to the cloud. In most of our test cases this still does not store all events, but will provide more information to investigate. So far, we have not been able to determine how and when it decides to change the default behavior, nor can we fully reproduce this behavior. These telemetry sources, when important to you in your detection requirements, would be a great example for the augmentation implementation of Sysmon to make sure the traffic patterns you are interested in are always logged.

## Conclusion

Both tools have their strong and potential weaker points. Depending on the maturity of your team, its budget and the risk appetite of the organization there are no bad choices when either is, or both are, applied thoroughly. To an extend it comes down to flexibility, easy of use, maintenance comfort, etc. which might also help sell either one internally.

Regardless, both are great to work with and provide a wealth of detection opportunities. Even some of the less ideal parts of each product can be acceptable for your use, so it doesn’t have to be a problem directly. Knowing what it can and cannot do is key though…

Regardless of what tool you decide to use, if you rely on any tool for your detection capability, make an effort to understand how it works. Get a deeper understanding of its inner workings, its configuration and limitations. Don’t rely on the marketing promises and fancy dashboards. This allows you to make decisions on how to deal with them, augment them or accept a blind spot when you have a good reason to do so.

Ultimately it is a time and effort (cost) versus risk acceptance discussion. Applying one solution really well still has preference over implementing both in a mediocre way.

## More

This article is part of a series, the other editions are listed below:

- [Microsoft Defender for Endpoint Internals 0x02 — Audit Settings and Telemetry](https://medium.com/falconforce/microsoft-defender-for-endpoint-internals-0x02-audit-settings-and-telemetry-1d0af3ebfb27?sk=3e9535b02aa9a18de324298609fb1753)
- [Microsoft Defender for Endpoint Internals 0x03 — MDE telemetry unreliability and log augmentation](https://medium.com/falconforce/microsoft-defender-for-endpoint-internals-0x03-mde-telemetry-unreliability-and-log-augmentation-ec6e7e5f406f?sk=568408658cb80770d2ed7ca8a415351c)
- [Microsoft Defender for Endpoint Internals 0x04 — Timeline](https://medium.com/falconforce/microsoft-defender-for-endpoint-internals-0x04-timeline-3f01282839e4?sk=78b7f120f56b38535c5115817e329f34)
- [Microsoft Defender for Endpoint Internals 0x05 — Telemetry for sensitive actions](https://medium.com/falconforce/microsoft-defender-for-endpoint-internals-0x05-telemetry-for-sensitive-actions-1b90439f5c25?sk=8ac2d4a290f085f3edc870d235798af6)

[Defender For Endpoint](https://medium.com/tag/defender-for-endpoint?source=post_page-----1e5663b10347---------------------------------------)

[Mdes](https://medium.com/tag/mdes?source=post_page-----1e5663b10347---------------------------------------)

[Sysmon](https://medium.com/tag/sysmon?source=post_page-----1e5663b10347---------------------------------------)

[Falconfriday](https://medium.com/tag/falconfriday?source=post_page-----1e5663b10347---------------------------------------)

[Detection Engineering](https://medium.com/tag/detection-engineering?source=post_page-----1e5663b10347---------------------------------------)

[![FalconForce](https://miro.medium.com/v2/resize:fill:48:48/1*Uf-Lb331GOxOfVzZeyg7TA.png)](https://medium.com/falconforce?source=post_page---post_publication_info--1e5663b10347---------------------------------------)

[![FalconForce](https://miro.medium.com/v2/resize:fill:64:64/1*Uf-Lb331GOxOfVzZeyg7TA.png)](https://medium.com/falconforce?source=post_page---post_publication_info--1e5663b10347---------------------------------------)

Follow

[**Published in FalconForce**](https://medium.com/falconforce?source=post_page---post_publication_info--1e5663b10347---------------------------------------)

[845 followers](https://medium.com/falconforce/followers?source=post_page---post_publication_info--1e5663b10347---------------------------------------)

· [Last published Feb 6, 2026](https://medium.com/falconforce/falconfriday-need-for-speed-going-underground-with-near-real-time-nrt-rules-0xff26-0972aecf894d?source=post_page---post_publication_info--1e5663b10347---------------------------------------)

A team of highly specialized security professionals

Follow

[![Olaf Hartong](https://miro.medium.com/v2/resize:fill:48:48/1*NrDNsO-K9DO3r-Ry-Aj3Dw.jpeg)](https://medium.com/@olafhartong?source=post_page---post_author_info--1e5663b10347---------------------------------------)

[![Olaf Hartong](https://miro.medium.com/v2/resize:fill:64:64/1*NrDNsO-K9DO3r-Ry-Aj3Dw.jpeg)](https://medium.com/@olafhartong?source=post_page---post_author_info--1e5663b10347---------------------------------------)

Follow

[**Written by Olaf Hartong**](https://medium.com/@olafhartong?source=post_page---post_author_info--1e5663b10347---------------------------------------)

[2.2K followers](https://medium.com/@olafhartong/followers?source=post_page---post_author_info--1e5663b10347---------------------------------------)

· [41 following](https://medium.com/@olafhartong/following?source=post_page---post_author_info--1e5663b10347---------------------------------------)

FalconForce \| Data Dweller \| Microsoft MVP

Follow

## No responses yet

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Ffalconforce%2Fsysmon-vs-microsoft-defender-for-endpoint-mde-internals-0x01-1e5663b10347&source=---post_responses--1e5663b10347---------------------respond_sidebar------------------)

Cancel

Respond

## More from Olaf Hartong and FalconForce

![Microsoft Defender for Endpoint Internals 0x02 — Audit Settings and Telemetry](https://miro.medium.com/v2/resize:fit:679/format:webp/1*XkFUpiIjdr500kANOFFsQA.png)

[![FalconForce](https://miro.medium.com/v2/resize:fill:20:20/1*Uf-Lb331GOxOfVzZeyg7TA.png)](https://medium.com/falconforce?source=post_page---author_recirc--1e5663b10347----0---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

In

[FalconForce](https://medium.com/falconforce?source=post_page---author_recirc--1e5663b10347----0---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

by

[Olaf Hartong](https://medium.com/@olafhartong?source=post_page---author_recirc--1e5663b10347----0---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

Jul 1, 2022

[A clap icon89\\
\\
A response icon2](https://medium.com/falconforce/microsoft-defender-for-endpoint-internals-0x02-audit-settings-and-telemetry-1d0af3ebfb27?source=post_page---author_recirc--1e5663b10347----0---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

![Microsoft Defender for Endpoint Internal 0x06 — Custom Collection](https://miro.medium.com/v2/resize:fit:679/format:webp/1*g0iuXzGWdLnZRwLjdnf5OA.jpeg)

[![FalconForce](https://miro.medium.com/v2/resize:fill:20:20/1*Uf-Lb331GOxOfVzZeyg7TA.png)](https://medium.com/falconforce?source=post_page---author_recirc--1e5663b10347----1---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

In

[FalconForce](https://medium.com/falconforce?source=post_page---author_recirc--1e5663b10347----1---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

by

[Olaf Hartong](https://medium.com/@olafhartong?source=post_page---author_recirc--1e5663b10347----1---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

Nov 20, 2025

[A clap icon7](https://medium.com/falconforce/microsoft-defender-for-endpoint-internal-0x06-custom-collection-81fc1042b87c?source=post_page---author_recirc--1e5663b10347----1---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

![Microsoft Defender for Endpoint Internals 0x05 — Telemetry for sensitive actions](https://miro.medium.com/v2/resize:fit:679/format:webp/1*Qf9pMnWhe0pkFBox8oefjg.png)

[![FalconForce](https://miro.medium.com/v2/resize:fill:20:20/1*Uf-Lb331GOxOfVzZeyg7TA.png)](https://medium.com/falconforce?source=post_page---author_recirc--1e5663b10347----2---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

In

[FalconForce](https://medium.com/falconforce?source=post_page---author_recirc--1e5663b10347----2---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

by

[Olaf Hartong](https://medium.com/@olafhartong?source=post_page---author_recirc--1e5663b10347----2---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

Oct 13, 2023

[A clap icon75](https://medium.com/falconforce/microsoft-defender-for-endpoint-internals-0x05-telemetry-for-sensitive-actions-1b90439f5c25?source=post_page---author_recirc--1e5663b10347----2---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

![Microsoft Defender for Endpoint Internals 0x03 — MDE telemetry unreliability and log augmentation](https://miro.medium.com/v2/resize:fit:679/format:webp/1*OEaiSz03zPWzbyiVL6s6Pw.png)

[![FalconForce](https://miro.medium.com/v2/resize:fill:20:20/1*Uf-Lb331GOxOfVzZeyg7TA.png)](https://medium.com/falconforce?source=post_page---author_recirc--1e5663b10347----3---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

In

[FalconForce](https://medium.com/falconforce?source=post_page---author_recirc--1e5663b10347----3---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

by

[Olaf Hartong](https://medium.com/@olafhartong?source=post_page---author_recirc--1e5663b10347----3---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

Jul 8, 2022

[A clap icon66\\
\\
A response icon1](https://medium.com/falconforce/microsoft-defender-for-endpoint-internals-0x03-mde-telemetry-unreliability-and-log-augmentation-ec6e7e5f406f?source=post_page---author_recirc--1e5663b10347----3---------------------14201f0a_07e9_499e_83e5_342f668a6227--------------)

[See all from Olaf Hartong](https://medium.com/@olafhartong?source=post_page---author_recirc--1e5663b10347---------------------------------------)

[See all from FalconForce](https://medium.com/falconforce?source=post_page---author_recirc--1e5663b10347---------------------------------------)

## Recommended from Medium

![Active Directory Lab for PenTest. Manual Deployment Guide](https://miro.medium.com/v2/resize:fit:679/format:webp/1*x0k_83ZQ3gz3KTVqHE3BGQ.png)

[![InfoSec Write-ups](https://miro.medium.com/v2/resize:fill:20:20/1*SWJxYWGZzgmBP1D0Qg_3zQ.png)](https://medium.com/bugbountywriteup?source=post_page---read_next_recirc--1e5663b10347----0---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

In

[InfoSec Write-ups](https://medium.com/bugbountywriteup?source=post_page---read_next_recirc--1e5663b10347----0---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

by

[Andrey Pautov](https://medium.com/@1200km?source=post_page---read_next_recirc--1e5663b10347----0---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

Jan 24

[A clap icon11\\
\\
A response icon2](https://medium.com/bugbountywriteup/active-directory-lab-for-pentest-manual-deployment-guide-cab28cd4ad8d?source=post_page---read_next_recirc--1e5663b10347----0---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

![Stop Watching OpenClaw Install Tutorials — This Is How You Actually Tame It](https://miro.medium.com/v2/resize:fit:679/format:webp/1*cKognCK0VNSBN79Awlwl8g.png)

[![Activated Thinker](https://miro.medium.com/v2/resize:fill:20:20/1*I0dmd2-TIrUdjo5eUTjtvw.png)](https://medium.com/activated-thinker?source=post_page---read_next_recirc--1e5663b10347----1---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

In

[Activated Thinker](https://medium.com/activated-thinker?source=post_page---read_next_recirc--1e5663b10347----1---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

by

[Shane Collins](https://medium.com/@intellizab?source=post_page---read_next_recirc--1e5663b10347----1---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

Feb 1

[A clap icon328\\
\\
A response icon4](https://medium.com/activated-thinker/stop-watching-openclaw-install-tutorials-this-is-how-you-actually-tame-it-f3416f5d80bc?source=post_page---read_next_recirc--1e5663b10347----1---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

![Wazuh for DevSecOps: A Comprehensive Guide](https://miro.medium.com/v2/resize:fit:679/format:webp/0*zrhxcT4FEj7CTjG7)

[![Ismael Barrantes](https://miro.medium.com/v2/resize:fill:20:20/1*G8tZd7qraRS2a4Pu3j_zHg.jpeg)](https://medium.com/@ismapersonal97?source=post_page---read_next_recirc--1e5663b10347----0---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

[Ismael Barrantes](https://medium.com/@ismapersonal97?source=post_page---read_next_recirc--1e5663b10347----0---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

Oct 4, 2025

![Introducing the DRAPE Index: How to measure (in)success in a Threat Detection practice?](https://miro.medium.com/v2/resize:fit:679/format:webp/1*V1hY17APqUmKtT6fyxK0Cg.png)

[![Detect FYI](https://miro.medium.com/v2/resize:fill:20:20/1*ayMhoNccbO0IxQ1UPFv0SA.png)](https://medium.com/detect-fyi?source=post_page---read_next_recirc--1e5663b10347----1---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

In

[Detect FYI](https://medium.com/detect-fyi?source=post_page---read_next_recirc--1e5663b10347----1---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

by

[Alex Teixeira](https://medium.com/@ateixei?source=post_page---read_next_recirc--1e5663b10347----1---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

Nov 17, 2025

[A clap icon260\\
\\
A response icon4](https://medium.com/detect-fyi/introducing-the-drape-index-how-to-measure-in-success-in-a-threat-detection-practice-154fd977f731?source=post_page---read_next_recirc--1e5663b10347----1---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

![SOC Analyst ROADMAP [2026 ]](https://miro.medium.com/v2/resize:fit:679/format:webp/1*iZXEf1KME_h-QCHSA4ppdA.png)

[![Mr Horbio](https://miro.medium.com/v2/resize:fill:20:20/1*uney5OKbxxfykdlwmeosyg.jpeg)](https://medium.com/@hrofficial62?source=post_page---read_next_recirc--1e5663b10347----2---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

[Mr Horbio](https://medium.com/@hrofficial62?source=post_page---read_next_recirc--1e5663b10347----2---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

Jan 1

[A clap icon102\\
\\
A response icon2](https://medium.com/@hrofficial62/soc-analyst-roadmap-2026-13006d3d3cdd?source=post_page---read_next_recirc--1e5663b10347----2---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

![What is YARA Rule Agent Skills?](https://miro.medium.com/v2/resize:fit:679/format:webp/1*4m2EbsvGzli9Vz10vQz0uA.png)

[![Tahir](https://miro.medium.com/v2/resize:fill:20:20/1*-ggDcHgIQSbhwkpWwqLaEw.png)](https://medium.com/@tahirbalarabe2?source=post_page---read_next_recirc--1e5663b10347----3---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

[Tahir](https://medium.com/@tahirbalarabe2?source=post_page---read_next_recirc--1e5663b10347----3---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

Feb 4

[A clap icon4](https://medium.com/@tahirbalarabe2/what-is-yara-rule-agent-skills-ab021ab42414?source=post_page---read_next_recirc--1e5663b10347----3---------------------c740d7fa_449f_4f79_8d42_018230849afb--------------)

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--1e5663b10347---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----1e5663b10347---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----1e5663b10347---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----1e5663b10347---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----1e5663b10347---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----1e5663b10347---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----1e5663b10347---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----1e5663b10347---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----1e5663b10347---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----1e5663b10347---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)