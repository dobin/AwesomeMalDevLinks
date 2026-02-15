# https://www.thedfirspot.com/post/windows-defender-mp-logs-a-story-of-artifacts

top of page

![](https://static.wixstatic.com/media/5cad07_649bbe7f590f4b0099aa92af3ccd3255~mv2.png/v1/fill/w_1024,h_640,al_c,q_90,enc_avif,quality_auto/5cad07_649bbe7f590f4b0099aa92af3ccd3255~mv2.png)

Search

Catchy title, eh? Well, I promise its not “clickbait”. When it comes to DFIR, there are obviously many artifacts to look at. You may even find an item of interest or “pivot point” in multiple artifacts. For example, identifying that a program was executed from both Prefetch and UserAssist or presence of a binary within the MFT (Master File Table) and Shimcache; but is there an artifact or log that will have observed files, hashes, timestamps, full paths, and potentially even signatures? Enter Windows Defender MP (Microsoft Protection) logs.

**The Rundown:**

- MP Logs can store information regarding observed files

- Found within ‘C:\\ProgramData\\Microsoft\\Windows Defender\\Support’

  - Note that ProgramData is a hidden directory, ensure “Hidden files” are enabled in order to see this folder or browse to the UNC path directly
- There are multiple log files within the ‘Support’ directory

- Can record command line arguments

- Can be used to determine if a file existed on the system and may contain additional context surrounding the file

- Can potentially have file hashes

- If a signature is matched, these logs may contain information regarding the identified file

- Even if a file is not identified as “suspicious”, it may still have an entry within this log, as Defender likely scanned it

- May or may not contain log entries, depending on Defenders configuration and presence on the system

- Timestamps are recorded when a file is scanned by Defender. Note that these timestamps are in the local time of the system

- Entries may have full system paths

- Binaries may still have presence in this log if Defender is disabled. This may vary on how Defender was disabled and if other features are still enabled. You’d be surprised on how many incidents you’ll hop into where the client states that Defender is disabled, yet this log contains invaluable information regarding observed files and scanned directories


As mentioned above, Windows Defender MP logs contain information about files scanned by the Microsoft Defender endpoint solution. Think about it; if a file is created, executed, modified, etc. Defender needs to scan the file to determine if its “safe” or not, right? So, it would make sense that there would be a log of this showing what file was scanned, what time it was scanned at, its path, and the result of the scan, right? Well... when we say “story” of artifacts, what exactly do we mean? Essentially, these log files can be a goldmine for evidence of file existence, program execution, results of a scan, signature matches, full path, timestamps, and potentially other files interacted with by the file in question. A big win too, is the fact that these logs can also record the command line parameters supplied with the program execution! Think of this as being a great source that has information you’d often find in artifacts such as prefetch, amcache, Sysmon, and more, in a single log!

Now, of course there may be situations where the data you’re looking for wasn’t recorded in this log or scanned by Defender, but it’s a great artifact to add to your collection and something you should be reviewing for any Windows based incident, regardless if they used Defender as their primary endpoint solution or not! With Windows being Windows, Defender may be recording information on the backend for telemetry and may record data surrounding your incident that you might not find elsewhere!

Now, you may be saying “Great, now I’ll need another tool to parse this data”. NOPE! The MP logs within the ‘Support’ directory are all standard text-based logs! So, if you like to live dangerously, you can open the text files within your favorite text editor and view the content or you can ‘grep’ through the data, focusing on the filename, directory, timestamp or whatever your pivot point may be.

So, let’s take a look at these log files. As mentioned, these can be found within ‘C:\\ProgramData\\Microsoft\\Windows Defender\\Support’.

![](https://static.wixstatic.com/media/5cad07_184d55ad9f4f461bbc5ecfb476c7299d~mv2.png/v1/fill/w_740,h_152,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/5cad07_184d55ad9f4f461bbc5ecfb476c7299d~mv2.png)

Here, you may find various log files, varying on what features of Defender are enabled and what has been observed by Defender.

Common log files you may see are

- MPDetection

- MPLog

-  MPDeviceControl

- MPWppTracing


However, we’re primarily interested in MPDetection and MPLog. As you can imagine, ‘MPDetection’ contains information regarding a detected threat; however, ‘MPlog’ contains a log with details events surrounding scanned files, directories and more. Regardless if the file was detected as “suspicious”, if the file was scanned, it’ll likely have an entry here.

Let’s start off easy by looking in the ‘MPDetection’ log file and check if there’s any information regarding detected files. Again, this is an easy one but bear with me here.

Okay, so we have a detected webshell here but not much information regarding context surrounding the execution and the file itself. Enter, the ‘MPLog’! Let’s open this up and search for the name of the webshell using either grep or “find”, within your text editor.

Awesome, we have a hit here. As we can see below, the first hit in my case regarding this file name references ‘SDN’ or Software Defined Networking. This is typically related to Defender using cloud telemetry. Here, we’ll get information regarding the query, results, timestamps, full path, and more.

![](https://static.wixstatic.com/media/5cad07_2ee81cbe560a4e8aad8a71f7ef817b80~mv2.png/v1/fill/w_49,h_8,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/5cad07_2ee81cbe560a4e8aad8a71f7ef817b80~mv2.png)

![](https://static.wixstatic.com/media/5cad07_09635ddd658b41bc98acb170d8e64eec~mv2.png/v1/fill/w_49,h_4,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/5cad07_09635ddd658b41bc98acb170d8e64eec~mv2.png)

As we continue scrolling through this log, we can see information regarding the detected file, such as the SHA1 hash, file owner, actions taken, and the results.

![](https://static.wixstatic.com/media/5cad07_e5f5e03b1eb940b59ca148997635fde5~mv2.png/v1/fill/w_49,h_10,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/5cad07_e5f5e03b1eb940b59ca148997635fde5~mv2.png)

Additionally, further down, we can see information regarding telemetry of the detection, which also grabbed a potential related process; in our instance, ‘w3wp.exe’ was scanned as part of this detection, which is the IIS worker process. With this being a webshell, ‘w3wp.exe’ was likely used to execute or process the aforementioned shell. This is labeled as “BM Telemetry”, which stands for “Behavioral Monitoring” and is a great keyword to search for when parsing these logs.

![](https://static.wixstatic.com/media/5cad07_71a8db05acd14138874ae32f88840991~mv2.png/v1/fill/w_49,h_14,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/5cad07_71a8db05acd14138874ae32f88840991~mv2.png)

Boom! Now we have a great idea of what was observed, when it was scanned and identified by Defender, and metadata surrounding the file! With this, we can add these events to our timeline or use these as further pivot points! Did the Threat Actor delete the file? Well… since we have the hash, we could utilize OSINT or Open-Source Intelligence and determine if the file has had presence in public scanning solutions, such as VirusTotal. If you get a hit, download the file from there and analyze it further!

![](https://static.wixstatic.com/media/5cad07_362abd0458c54d04a974b2ddb205fa28~mv2.png/v1/fill/w_49,h_16,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/5cad07_362abd0458c54d04a974b2ddb205fa28~mv2.png)

![](https://static.wixstatic.com/media/5cad07_7c469dae331f445d81333ee7fdfb2fa3~mv2.png/v1/fill/w_49,h_16,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_avif,quality_auto/5cad07_7c469dae331f445d81333ee7fdfb2fa3~mv2.png)

So, why is this important? There may be many instances where you take a case and find very limited logging in place. For example, no command line auditing, no process creation auditing, various other artifacts were deleted by a threat actor, including the file itself, Sysmon is not installed, etc. This can be a great log to look at that may take various bits of information you’d find in other artifacts and combine it into a single log source!

[Windows Artifacts For Intrusion Analysis: A Treasure Trove of Evidence](https://www.thedfirspot.com/post/windows-artifacts-for-intrusion-analysis-a-treasure-trove-of-evidence)

bottom of page