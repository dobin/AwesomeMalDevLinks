# https://medium.com/threat-hunters-forge/threat-hunting-with-etw-events-and-helk-part-1-installing-silketw-6eb74815e4a0

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2Fthreat-hunters-forge%2Fthreat-hunting-with-etw-events-and-helk-part-1-installing-silketw-6eb74815e4a0&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2Fthreat-hunters-forge%2Fthreat-hunting-with-etw-events-and-helk-part-1-installing-silketw-6eb74815e4a0&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

[**Open Threat Research**](https://medium.com/threat-hunters-forge?source=post_page---publication_nav-45ee330cc033-6eb74815e4a0---------------------------------------)

·

Follow publication

[![Open Threat Research](https://miro.medium.com/v2/resize:fill:38:38/1*_3dB08B46iv4OXRQ8ZZLnw.jpeg)](https://medium.com/threat-hunters-forge?source=post_page---post_publication_sidebar-45ee330cc033-6eb74815e4a0---------------------------------------)

Threat Hunting, Data Science & Open Source Projects

Follow publication

# Threat Hunting with ETW events and HELK — Part 1: Installing SilkETW 🏄‍♀🏄

[![Roberto Rodriguez](https://miro.medium.com/v2/resize:fill:32:32/1*9WbXEpOxOhaMq99CwG1ESQ.png)](https://medium.com/@cyb3rward0g?source=post_page---byline--6eb74815e4a0---------------------------------------)

[Roberto Rodriguez](https://medium.com/@cyb3rward0g?source=post_page---byline--6eb74815e4a0---------------------------------------)

Follow

14 min read

·

Sep 19, 2019

154

3

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D6eb74815e4a0&operation=register&redirect=https%3A%2F%2Fmedium.com%2Fthreat-hunters-forge%2Fthreat-hunting-with-etw-events-and-helk-part-1-installing-silketw-6eb74815e4a0&source=---header_actions--6eb74815e4a0---------------------post_audio_button------------------)

Share

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*G9aLuMWPHHEWSahQ.jpg)

One of my favorite things to do besides playing with Jupyter Notebooks 😆 is to identify new data sources that could provide additional context to the analytics that I develop while performing research. From a Windows environment perspective, most of the time, the event logs generated after simulating an adversarial technique, come from sources that are simply enabled by pushing an audit policy or by running `auditpol.exe` . Even though Windows audit policies allow you to enable several useful events, remember that those are only a subset of all the telemetry available in Windows systems.

There are several other sources of data that are available, but they cannot be easily enabled via an audit policy. However, they are easy to explore interactively with the right tooling and a little bit of knowledge about the Event Tracing for Windows (ETW) concepts.

This post is part of a four-part series which will go over the basics of the ETW model, how to install SilkETW, consume and aggregate ETW events, and at the same time show you how you can leverage the additional telemetry for a few detection use cases with the [Hunting ELK (HELK)](https://github.com/Cyb3rWard0g/HELK).

In this first post, I will go over the basics of ETW and the installation of an amazing project by [Ruben Boonen (@FuzzySec)](https://twitter.com/FuzzySec) 🍻 named [SilkETW](https://github.com/fireeye/SilkETW) ⚔️

The other three parts can be found in the following links:

- [Threat Hunting with ETW events and HELK — Part 2: Shipping ETW events to HELK ⚒](https://medium.com/threat-hunters-forge/threat-hunting-with-etw-events-and-helk-part-2-shipping-etw-events-to-helk-16837116d2f5)
- Threat Hunting with ETW events and HELK — Part 3: Hunt use cases ⚔️
- Threat Hunting with ETW events and HELK — Part 4: ETW event and Jupyter Notebooks 🚀

Before we even start talking about SilkETW, I believe it is important to start from the basics, and refresh some of the key concepts of the ETW model. I also believe it is important to understand how you could manually enable event tracing for specific ETW providers to learn about the mechanics of it.

## What is ETW?

> Event Tracing for Windows (ETW) is an efficient kernel-level tracing facility that lets you log kernel or application-defined events to a log file. You can consume the events in real time or from a log file and use them to debug an application or to determine where performance issues are occurring in the application. ETW lets you enable or disable event tracing dynamically, allowing you to perform detailed tracing in a production environment without requiring computer or application restarts.

According to [MS docs](https://docs.microsoft.com/en-us/windows/win32/etw/about-event-tracing), the Event Tracing API is broken into three distinct components:

- [Controllers](https://docs.microsoft.com/en-us/windows/win32/etw/about-event-tracing#controllers), which start and stop an event tracing session and enable providers
- [Providers](https://docs.microsoft.com/en-us/windows/win32/etw/about-event-tracing#providers), which provide the events
- [Consumers](https://docs.microsoft.com/en-us/windows/win32/etw/about-event-tracing#consumers), which consume the events

The following diagram from the Microsoft [Ntdebugging Blog](https://blogs.msdn.microsoft.com/ntdebugging/2009/08/27/part-1-etw-introduction-and-overview/) helped me to understand how each component relates to each other.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*4BO6zVzld3Dyd4wTvPVw-Q.png)

## Exploring ETW Components

### Controllers

Tools such as [Logman](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/logman) are good examples of a **Controller** in the ETW model since it creates and manages **Event Trace Sessions** and **Performance logs**. In addition, you can use it to query metadata of each component (i.e. Providers).

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Gu4Tv-Iw0DYbtp3lMgrXEQ.png)

[https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/logman](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/logman)

Another way to create new event trace sessions and enable ETW providers is via the built-in **Windows Performance System Tool** located at **Computer Management> System Tools > Performance**. I’ll go over an example later.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*R1s-QtNnp4LlgoIpOnyuQg.png)

### List Event Trace Sessions

You can use logman to list running event trace sessions in your system

```
logman query -ets
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Ri3L7b9v7NgKIQ42rMwSXg.png)

You can also use the **Windows Performance System Tool** to see what **Event Trace Sessions** are enabled and the providers providing events to them.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*t3gqRJ-iWmqxjd_unqgHgA.png)

If you also wanted to know what event providers a specific event trace session is subscribed to via logman, you can run the following command:

```
logman query "EventLog-System" -ets
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*TJNzINANmBVnhYl5Du0olQ.png)

### List ETW Providers

Next, you can list all the available providers in your system with logman:

```
logman query providers
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*rg5lxywttrlPwl1shAYFzw.png)

### Query Specific ETW Providers

What if I wanted to look for specific **ETW Providers** ? You can filter the `logman query providers` results and look for specific strings. For example, we can look for providers with the word **Security** in their name as shown below:

```
$ETWProviders = logman query providers
$ETWProviders | Where-Object { $_ -Like "*Security*" }
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*z4Xk4P-9OS8aUEJg6UgAOQ.png)

We can select the **Microsoft-Windows-Security-Auditing**,and query its metadata to get more information about it.

```
logman query providers Microsoft-Windows-Security-Auditing
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*HfHcaHDAEFerryt-PhIjSA.png)

You could also get information about specific ETW providers via a tool named [Windows Events Providers Explorer (WEPExplorer)](https://github.com/lallousx86/WinTools/tree/master/WEPExplorer)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*rKoKCPKVKAXNiakIoVEgOA.png)

You could also use [**wevtutil.exe**](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil) to retrieve information about event logs and publishers ( Thank you [Marc Sherman](https://twitter.com/msherman1970))

```
> wevtutil.exe get-publisher Microsoft-Windows-Security-Auditing /getevents:true /getmessage:true
```

### Windows Security Auditing ETW Provider Events 💥

We now know that there is an event tracing session subscribed to the **Microsoft-Windows-Security-Auditing** provider which uses the channel **Security** to allow ingestion of Security events via the event log.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*PN1HQNj-XxbriyZbJogkyA.png)

## Can I Consume Any ETW Event via the Event Log?

According to [Matt Graeber’s](https://twitter.com/mattifestation) research, **ONLY** ETW provider events that have a **Channel** property applied to them can be consumed by the event log.

For example, this [post](https://blogs.msdn.microsoft.com/ntdebugging/2009/09/08/part-2-exploring-and-decoding-etw-providers-using-event-log-channels/) from the [Microsoft Ntdebugging blog](https://blogs.msdn.microsoft.com/ntdebugging/) has a great step-by-step tutorial on how to enable event tracing for the **Microsoft-Windows-WinINet** provider via the **Analytic** channel.

We can start by using the [WEPExplorer](https://github.com/lallousx86/WinTools/tree/master/WEPExplorer) tool to get more detailed information about the specific **Channels** applied to each ETW event. As you can see below, we can see the **Microsoft-Windows-WinINet/Analytic** channel applied to most of the events from the **Microsoft-Windows-WinINet** provider. Therefore, they are meant to be consumed by the event log in **real-time**.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*9dkHrj7ucKNpADd5jP9fsA.png)

### Consume **WinINet Events**

Now that we know that we can consume events from the Microsoft-Windows-WinINet provider in real-time via the event log, we can start the process by enabling the **Analytic and Debug Logs** view.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*bWuBOQm8ZGkAnPpGl7pdjw.png)

You might have to restart the event viewer console. You will see a new event log folder named **WinINet (Microsoft-Windows-WinINet)** under Application and Service Logs > Microsoft > Windows. Click on it and you will see 3 channels. Right-click on the **Analytic** channel and select **Enable Log**.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*RqWsPHZi4eYxtmT1LM0stA.png)

Click **Ok.**

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*FE38sJbIR4_RS0DgFaP2-g.png)

If you go to a website via Microsoft Edge, you will start seeing events populating the **Analytic Channel** as shown below:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*_nm6AjfTxoDrvpUnIxLN5A.png)

You can validate that an event trace session for the **WinINet** provider was enabled by going to Computer Management > System Tools > Performance > Data Collector Sets > Startup Event Trace Sessions as shown below:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*DRD_rBsKNr-P1Jy52nQiKg.png)

## What about ETW Events Without a Property Channel?

What if I wanted to enable an event trace session for providers which events do not have a property **Channel** applied to them? For example, with adversaries dynamically loading custom .NET code for execution, I would like to enable event tracing for the **Microsoft-Windows-DotNETRuntime** {E13C0D23-CCBC-4E12–931B-D9CC2EEE27E4} and explore the data.

## Get Roberto Rodriguez’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

We can use the [Windows Events Providers Explorer (WEPExplorer)](https://github.com/lallousx86/WinTools/tree/master/WEPExplorer) tool again and verify if we can consume those ETW events in real-time via the event log. Unfortunately, there are not **Channel** properties applied to the events.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*oS4nWfYBAY9cf6ojZZ1rtA.png)

### So What Now?

You can still do it, but not in real-time to the event log. You will have to:

- Create an event trace session (manually)
- Subscribe to the ETW provider
- Set location of the **.etl** file that will be created
- Start the event trace session
- **.etl** file is generated
- Open **.etl** log via the event log as a saved log file

You can start by creating the event trace session via the **Performance System Tool** located at Computer Management > System Tools > Performance. You just have to create a new **Data Collector Set** as shown in the image below:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ZzZvC5E765-KltTxaQpLhg.png)

Give it a name and select **Create Manually (Advanced)**

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*DTcO5kxj6_f6QDWCIJDpOQ.png)

Next, select the event trace provider **Microsoft-Windows-DotNETRuntime**

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*s_o5N0Ct9lJghUuawX5Jew.png)

You are almost done! You can use the view below and modify the properties of the data collector set. For example, select **Keywords** and then **Edit**.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*WlQoNZM_kFR4FFuiy7CeSQ.png)

For example, you can collect a subset of events related to **JitKeyword, InteropKeyword, LoaderKeyword and NGenKeyword** for .NET activity. If you want to learn why I am interested in those events, you can read [this blog post](https://www.countercept.com/blog/detecting-malicious-use-of-net-part-2/) from the [Countercept team](https://www.countercept.com/). After selecting those values, you will get a bitmask: **0x2038** (Remember this! 😉). Next, click **Ok** and **Next**.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*PgdHepALBXzfnBbkvPRUww.png)

Select the location of the **.etl** file. Keep the default location and click **Next.**

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*fH-4Wj8QFjay5koJokMzzw.png)

Keep the defaults and click **Finish!**

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*26VLji8KObXGmvnqghwltw.png)

You can see the new event trace session available but with status **Stopped**. You can also double-click on it and check the location and name of the **.etl** file that will be created once the event trace session gets started.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*stbrpP0myYxdUbhKRkDQug.png)

Right-click on the new event trace session and select **Start.**

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*hYLfJhLe_QH05cgl5JpHyg.png)

The event trace session is now running, but you wont see it in the event logs unless you grab a copy of the **.etl** file and open it as a saved log. You wont be able to have a continuous ingestion to the event log. To open the . **etl** file as a saved log, go to Event Viewer console and click on Action > Open Saved Log.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*0E9nRCrjfgoGewqbqzSBwg.png)

Select the **.etl** file associated with your event trace session, and click **Open.**

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*oHHo-ba4v0HRW5PEsq61YA.png)

Click **Yes** after getting the prompt to create a copy of it

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*cpfkFzOt04RJ1DiH6_8iaw.png)

You can keep the default location to display the external log. Click **Ok.**

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*5NfTBbIAzKDRwLs35nB1eg.png)

💥Thats it! That was easy right?

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*H624rrShkq3hB2LDI-GWww.png)

Even though I was able to get events from the **Microsoft-Windows-DotNETRuntime** provider, it is not a continuous real-time ingestion to the event log. By default those ETW events don’t have a **Channel** applied to them.One way to accomplish the real-time ingestion to the event log would be by writing an applications leveraging ETW apis and enable that capability.

## Enter SilkETW

Fortunately! The amazing [Ruben Boonen](https://twitter.com/FuzzySec) figured out a way to do that and more via C# wrappers and developed a tool named [**SilkETW**](https://github.com/fireeye/SilkETW) to provide a straightforward interface for ETW events collection, filtering and ingestion. The project provides 2 ways to interact with ETW components. One is via the command line, and the other one by running **SilkETW** headless as a service.

[https://twitter.com/FuzzySec/status/1108398013960065024](https://twitter.com/FuzzySec/status/1108398013960065024)

My brother

[Jose Luis Rodriguez](https://medium.com/u/b8f2906f3de3?source=post_page---user_mention--6eb74815e4a0---------------------------------------)

and I were so excited about this release that..

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/0*BLKeRWEBSIjw0MH-.jpg)

We decided to test it in our lab environment and used it to consume events from the **Microsoft-Windows-LDAP-Client** provider while executing some LDAP filters via [Powerview](https://github.com/PowerShellMafia/PowerSploit/tree/dev/Recon) by

[Will](https://medium.com/u/74ad66811b78?source=post_page---user_mention--6eb74815e4a0---------------------------------------)

. I will walk through some examples in the next parts of this series. For now, I can show you how to install SilkETW ⚔️

[https://twitter.com/Cyb3rWard0g/status/1108592833349464064](https://twitter.com/Cyb3rWard0g/status/1108592833349464064)

## Installation

Download the latest release package from [https://github.com/fireeye/SilkETW/releases](https://github.com/fireeye/SilkETW/releases) and unblock the compressed file (Version 0.8 was the latest when writing this post)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*-vRj4zzG6dRf1UIZrUrNzQ.png)

You will see two folders: **SilkETW** and **SilkService**. Thats how you differentiate how you will go about running SilkETW.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*4ZtAkWq2qF2dU1WbwEAO_g.png)

Also, in the **Dependencies** folder, you will find binaries that you need to run as pre-requirements ( Do **NOT** skip this step!)

- Install the VC++ 2015 x86 redistributable package

Dependencies\\vc2015\_redist.x86.exe or download it from [https://www.microsoft.com/en-ie/download/details.aspx?id=48145](https://www.microsoft.com/en-ie/download/details.aspx?id=48145)
- Install at least v4.5 of the .NET framework

Dependencies\\dotNetFx45\_Full\_setup.exe or download it from [https://www.microsoft.com/en-ie/download/details.aspx?id=30653](https://www.microsoft.com/en-ie/download/details.aspx?id=30653)

## SilkETW CLI

You do not need to do anything else to start working with the CLI version of it and the basic options. Open a a terminal as **Administrator** and just run the binary inside of the SilkETW folder to learn about the available options with the tool. (Downloads>SilkETW\_SilkService\_v8>v8>SilkETW)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*muBU-6x4Ru5Q9YSGs2wj6g.png)

### Event Tracing for **Microsoft-Windows-DotNETRuntime**

Remember all the things that we needed to do to interact with ETW providers that did not have a property **Channel** applied to them? These are the arguments to consume ETW events from the **Microsoft-Windows-DotNETRuntime** provider with the same keyword filters via the event log:

- -pn Microsoft-Windows-DotNETRuntime
- -ot eventlog
- -uk 0x2038

```
> SilkETW.exe -t user -pn Microsoft-Windows-DotNETRuntime -uk 0x2038 -ot eventlog
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*yhktdRrnmGm5xFCMqC_DJw.png)

Something important to point out in here is that the collection of events is continuous and pushed to the **SilkETW-Log** event log directly. However, as you can see in your cmd terminal, it is not a collection that will run headless in the background. This is perfect for debugging and analysis of ETW events generated by any execution of code during research. CTRL-C to stop collector!

## SilkETW in Headless Mode = SilkService 🔥

According to the [setup instructions in the GitHub README](https://github.com/fireeye/SilkETW#silkservice), you can install the service by issuing the following command from an elevated prompt:

```
sc create SillkService binPath= "C:\Path\To\SilkService.exe" start= demand
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*uxXa0wRJcVk0oURylJdsJg.png)

### Build Your SilkService XML Config

Before you even start the **SilkService**, you have to make your own SilkServiceConfig.xml file and place it in the same directory as the service binary (i.e. Downloads>SilkETW\_Service\_v8\\v8\\SilkService). This is a template that Ruben provided with several options:

ruben-silkserviceconfig-template.xml – Medium

Following our example for **Microsoft-Windows-DotNETRuntime** events consumed via the event log, you can use this basic config:

dotnetruntime-silkservice-config.xml – Medium

Remember that the <Guid> field is a random GUID that you generate. When I started to work with these configs, I thought it was the provider GUID 😆. Next, copy the **DotNETRuntime** config, rename it **SilkServiceConfig.xml**, and place it in the same directory as the service binary.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*c4uJf3dR6QV_03DUglQA-A.png)

### Start SilkService 🤞

Open Services> Right-Click on **SilkService** \> Start . A new folder named **Logs** will be created under the SilkService folder. There you will find a log file that will tell you more about the collector status and if the parameters you provided via the SilkServiceConfig.xml were validated successfully.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*c0fCRiSb-q1Xr7gxgGG0QQ.png)

If you open Event Viewer again (restart it), you will see that there is a new event log named **SilkService-Log**. There you will be able to see a continuous real-time ingestion of ETW events from the **Microsoft-Windows-DotNETRuntime** provider 🔥 🚒

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*BeIonS653zAn8F6uXa26yA.png)

### SilkService XML Config Elements

If you want to modify your SilkService config and add other XML elements, this is the list of options that you can play with on your configs. Ruben has a lot of examples in his repo and also several demos from [BH Arsenal 2019](https://github.com/FuzzySecurity/BH-Arsenal-2019)

[**fireeye/SilkETW** \\
\\
**You can’t perform that action at this time. You signed in with another tab or window. You signed out in another tab or…**\\
\\
github.com](https://github.com/fireeye/SilkETW/blob/74246ba6601e996b5e8b6016a5d5c7fd08e264fb/SilkService/h_SilkParameters.cs?source=post_page-----6eb74815e4a0---------------------------------------#L27-L40)

```
// Define XML elements
XName CI = XName.Get("ETWCollector");
XName CG = XName.Get("Guid");
XName CT = XName.Get("CollectorType");
XName KK = XName.Get("KernelKeywords");
XName OT = XName.Get("OutputType");
XName P = XName.Get("Path");
XName PN = XName.Get("ProviderName");
XName UTEL = XName.Get("UserTraceEventLevel");
XName UK = XName.Get("UserKeywords");
XName FO = XName.Get("FilterOption");
XName FV = XName.Get("FilterValue");
XName YS = XName.Get("YaraScan");
XName YO = XName.Get("YaraOptions");
```

Also, check how others are playing with SilkETW for some ideas. This [blog post](https://blog.iisreset.me/tracing-as-a-service-with-silketw-pt/) by [Mathias Jessen](https://twitter.com/IISResetMe), shows you how to write events to a file (JSON).

### SilkETW Event Types

It is important to also know what events are provided by SilkETW when looking at the event log. This is totally different from the events provided by each provider. According to [Issue 1](https://github.com/fireeye/SilkETW/issues/1), the log has four event id types:

Event ID = 0 -> Collector start

```
{
  "Collector": "Start",
  "Data": {
    "Type": "User",
    "Provider": "Microsoft-Windows-DotNETRuntime",
    "Keywords": "0x2038",
    "FilterOption": "None",
    "FilterValue": "",
    "YaraPath": "",
    "YaraOption": "None"
  }
}
```

Event ID = 1 -> Collector terminated by user

```
{
  "Collector": "Stop",
  "Error": false
}
```

Event ID = 2 -> Collector terminated by error

```
{
  "Collector": "Stop",
  "Error": true,
  "ErrorCode": 3
}
```

Event ID = 3 -> Event recorded

This is just the raw JSON for the event that was recorded by the collector.

This is it for the first post of this series. I hope this was helpful to anyone that wanted to play with SilkETW and consume events in real-time via the event log! . In the next post, I will show you how you can ship the ETW events from the event log to your [HELK stack](https://github.com/Cyb3rWard0g/HELK)!

Thank you for reading! and feedback is always welcome!

Thank you Ruben for all your help and patience! ⚔️

**Updates:**

- 19/09/2019 [Marc Sherman Suggestion](https://twitter.com/msherman1970/status/1174803636955820033)

## References

[https://docs.microsoft.com/en-us/windows/win32/etw/about-event-tracing](https://docs.microsoft.com/en-us/windows/win32/etw/about-event-tracing)

[https://blogs.msdn.microsoft.com/ntdebugging/2009/08/27/part-1-etw-introduction-and-overview/](https://blogs.msdn.microsoft.com/ntdebugging/2009/08/27/part-1-etw-introduction-and-overview/)

[https://github.com/fireeye/SilkETW](https://github.com/fireeye/SilkETW)

[https://github.com/FuzzySecurity/BH-Arsenal-2019](https://github.com/FuzzySecurity/BH-Arsenal-2019)

[https://github.com/fireeye/SilkETW/issues/1](https://github.com/fireeye/SilkETW/issues/1)

[https://github.com/FuzzySecurity/BH-Arsenal-2019/blob/master/Ruben%20Boonen%20-%20BHArsenal\_SilkETW\_v0.2.pdf](https://github.com/FuzzySecurity/BH-Arsenal-2019/blob/master/Ruben%20Boonen%20-%20BHArsenal_SilkETW_v0.2.pdf)

[https://medium.com/palantir/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63](https://medium.com/palantir/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63)

[https://medium.com/palantir/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63](https://medium.com/palantir/tampering-with-windows-event-tracing-background-offense-and-defense-4be7ac62ac63)

[https://blogs.msdn.microsoft.com/ntdebugging/2009/09/08/part-2-exploring-and-decoding-etw-providers-using-event-log-channels/](https://blogs.msdn.microsoft.com/ntdebugging/2009/09/08/part-2-exploring-and-decoding-etw-providers-using-event-log-channels/)

[https://docs.microsoft.com/en-us/windows/win32/wes/defining-channels](https://docs.microsoft.com/en-us/windows/win32/wes/defining-channels)

[https://www.countercept.com/blog/detecting-malicious-use-of-net-part-1/](https://www.countercept.com/blog/detecting-malicious-use-of-net-part-1/)

[https://www.countercept.com/blog/detecting-malicious-use-of-net-part-2/](https://www.countercept.com/blog/detecting-malicious-use-of-net-part-2/)

[https://blogs.technet.microsoft.com/office365security/hidden-treasure-intrusion-detection-with-etw-part-2/](https://blogs.technet.microsoft.com/office365security/hidden-treasure-intrusion-detection-with-etw-part-2/)

[Microsoft](https://medium.com/tag/microsoft?source=post_page-----6eb74815e4a0---------------------------------------)

[Threat Hunting](https://medium.com/tag/threat-hunting?source=post_page-----6eb74815e4a0---------------------------------------)

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page-----6eb74815e4a0---------------------------------------)

[Security Engineering](https://medium.com/tag/security-engineering?source=post_page-----6eb74815e4a0---------------------------------------)

[Network Security](https://medium.com/tag/network-security?source=post_page-----6eb74815e4a0---------------------------------------)

[![Open Threat Research](https://miro.medium.com/v2/resize:fill:48:48/1*_3dB08B46iv4OXRQ8ZZLnw.jpeg)](https://medium.com/threat-hunters-forge?source=post_page---post_publication_info--6eb74815e4a0---------------------------------------)

[![Open Threat Research](https://miro.medium.com/v2/resize:fill:64:64/1*_3dB08B46iv4OXRQ8ZZLnw.jpeg)](https://medium.com/threat-hunters-forge?source=post_page---post_publication_info--6eb74815e4a0---------------------------------------)

Follow

[**Published in Open Threat Research**](https://medium.com/threat-hunters-forge?source=post_page---post_publication_info--6eb74815e4a0---------------------------------------)

[1K followers](https://medium.com/threat-hunters-forge/followers?source=post_page---post_publication_info--6eb74815e4a0---------------------------------------)

· [Last published Oct 28, 2020](https://medium.com/threat-hunters-forge/mapping-att-ck-data-sources-to-security-events-via-ossem-%EF%B8%8F-b606d99e738c?source=post_page---post_publication_info--6eb74815e4a0---------------------------------------)

Threat Hunting, Data Science & Open Source Projects

Follow

[![Roberto Rodriguez](https://miro.medium.com/v2/resize:fill:48:48/1*9WbXEpOxOhaMq99CwG1ESQ.png)](https://medium.com/@cyb3rward0g?source=post_page---post_author_info--6eb74815e4a0---------------------------------------)

[![Roberto Rodriguez](https://miro.medium.com/v2/resize:fill:64:64/1*9WbXEpOxOhaMq99CwG1ESQ.png)](https://medium.com/@cyb3rward0g?source=post_page---post_author_info--6eb74815e4a0---------------------------------------)

Follow

[**Written by Roberto Rodriguez**](https://medium.com/@cyb3rward0g?source=post_page---post_author_info--6eb74815e4a0---------------------------------------)

[1.7K followers](https://medium.com/@cyb3rward0g/followers?source=post_page---post_author_info--6eb74815e4a0---------------------------------------)

· [5 following](https://medium.com/@cyb3rward0g/following?source=post_page---post_author_info--6eb74815e4a0---------------------------------------)

Follow

## Responses (3)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fthreat-hunters-forge%2Fthreat-hunting-with-etw-events-and-helk-part-1-installing-silketw-6eb74815e4a0&source=---post_responses--6eb74815e4a0---------------------respond_sidebar------------------)

Cancel

Respond

[![Ayeshar](https://miro.medium.com/v2/resize:fill:32:32/0*oV2lD3VfYfVLPbpq)](https://medium.com/@ayeshar4940?source=post_page---post_responses--6eb74815e4a0----0-----------------------------------)

[Ayeshar](https://medium.com/@ayeshar4940?source=post_page---post_responses--6eb74815e4a0----0-----------------------------------)

[Mar 19, 2025](https://medium.com/@ayeshar4940/hi-great-blog-c790dbe70bba?source=post_page---post_responses--6eb74815e4a0----0-----------------------------------)

```
Hi, great blog.

I was replicating everything in here but i fail to ingest silkETW logs in event viewer.

i inatalled silkSerivce.exe using .NET installUtil installer but when i try to start this service from services.msc it exits with error: the…more
```

--

Reply

[![Lukas Lesky](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)](https://medium.com/@d0xy?source=post_page---post_responses--6eb74815e4a0----1-----------------------------------)

[Lukas Lesky](https://medium.com/@d0xy?source=post_page---post_responses--6eb74815e4a0----1-----------------------------------)

[May 8, 2021](https://medium.com/@d0xy/so-where-is-part-3-and-4-then-b74f9cc7bcd5?source=post_page---post_responses--6eb74815e4a0----1-----------------------------------)

```
So - where is Part 3 and 4 then?
```

--

Reply

[![Fred Frey](https://miro.medium.com/v2/resize:fill:32:32/1*Ph9UTw-00pk892-iazRljA.jpeg)](https://medium.com/@FredFrey?source=post_page---post_responses--6eb74815e4a0----2-----------------------------------)

[Fred Frey](https://medium.com/@FredFrey?source=post_page---post_responses--6eb74815e4a0----2-----------------------------------)

[Sep 30, 2019](https://medium.com/@FredFrey/absolutely-amazing-blog-4352399148fb?source=post_page---post_responses--6eb74815e4a0----2-----------------------------------)

```
Absolutely amazing blog! I’ve only started scratching the surface of ETW when i stumbled upon this … Well don Sir!
```

--

Reply

## More from Roberto Rodriguez and Open Threat Research

[See all from Roberto Rodriguez](https://medium.com/@cyb3rward0g?source=post_page---author_recirc--6eb74815e4a0---------------------------------------)

[See all from Open Threat Research](https://medium.com/threat-hunters-forge?source=post_page---author_recirc--6eb74815e4a0---------------------------------------)

## Recommended from Medium

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--6eb74815e4a0---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----6eb74815e4a0---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----6eb74815e4a0---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----6eb74815e4a0---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----6eb74815e4a0---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----6eb74815e4a0---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----6eb74815e4a0---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----6eb74815e4a0---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----6eb74815e4a0---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----6eb74815e4a0---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)