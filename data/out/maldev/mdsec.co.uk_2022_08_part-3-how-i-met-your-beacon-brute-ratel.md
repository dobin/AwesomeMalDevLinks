# https://www.mdsec.co.uk/2022/08/part-3-how-i-met-your-beacon-brute-ratel/

- [![Adversary](https://www.mdsec.co.uk/wp-content/themes/mdsec/img/icons/icon-adversary.svg)\\
**Adversary Simulation**\\
Our best in class red team can deliver a holistic cyber attack simulation to provide a true evaluation of your organisation’s cyber resilience.](https://www.mdsec.co.uk/our-services/adversary-simulation/)
- [![Application Security](https://www.mdsec.co.uk/wp-content/themes/mdsec/img/icons/icon-application-security.svg)\\
**Application   Security**\\
Leverage the team behind the industry-leading Web Application and Mobile Hacker’s Handbook series.](https://www.mdsec.co.uk/our-services/applicaton-security/)
- [![Penetration Testing](https://www.mdsec.co.uk/wp-content/themes/mdsec/img/icons/icon-penetration-testing.svg)\\
**Penetration   Testing**\\
MDSec’s penetration testing team is trusted by companies from the world’s leading technology firms to global financial institutions.](https://www.mdsec.co.uk/our-services/penetration-testing/)
- [![Response](https://www.mdsec.co.uk/wp-content/themes/mdsec/img/icons/icon-response.svg)\\
**Response**\\
Our certified team work with customers at all stages of the Incident Response lifecycle through our range of proactive and reactive services.](https://www.mdsec.co.uk/our-services/response/)

- [**Research**\\
MDSec’s dedicated research team periodically releases white papers, blog posts, and tooling.](https://www.mdsec.co.uk/knowledge-centre/research/)
- [**Training**\\
MDSec’s training courses are informed by our security consultancy and research functions, ensuring you benefit from the latest and most applicable trends in the field.](https://www.mdsec.co.uk/knowledge-centre/training/)
- [**Insights**\\
View insights from MDSec’s consultancy and research teams.](https://www.mdsec.co.uk/knowledge-centre/insights/)

ActiveBreach

# PART 3: How I Met Your Beacon – Brute Ratel

## Introduction

In [part one](https://www.mdsec.co.uk/2022/07/part-1-how-i-met-your-beacon-overview/), we introduced generic approaches to performing threat hunting of C2 frameworks and then followed it up with practical examples against Cobalt Strike in [part two](https://www.mdsec.co.uk/2022/07/part-2-how-i-met-your-beacon-cobalt-strike/).

In part three of this series, we will analyse Brute Ratel, a command and control framework developed by [Dark Vortex](https://bruteratel.com/). As the C2 is lesser known, we can see it describes itself as follows:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-960x114.png)

The framework has come under close scrutiny in the past few months, having been allegedly abused by [APT29](https://unit42.paloaltonetworks.com/brute-ratel-c4-tool/) and the ransomware group [BlackCat](https://www.sophos.com/en-us/press-office/press-releases/2022/07/blackcat-adds-brute-ratel-to-attack-tools) in recent times. Having an understanding of how we can generically detect this emerging C2 in our infrastructure is therefore useful intelligence for defenders.

Originally, all analysis was performed on Brute Ratel v1.0.7; the latest at the time of original review. However, a cursory update (contained at the end of this article) was performed discussing findings pertinent to v1.1 which was released shortly after our initial x33fcon presentation. One thing that should be noted with Brute Ratel is that the badger has only limited malleability and primarily from the perspective of the c2 channels; with the exception of v1.1 which added malleability for the sleep obfuscation techniques. As such it makes it possible to create very specific detections for the tool.

## **Brute Ratel’s Loader**

Brute Ratel’s badger comes in a number of forms, including exe, DLL and shellcode. When the badger is injected, its reflective loader will instantly load all dependencies required for the badger. As the badger bundles a large amount of post-exploitation features, this leads to a significant number of DLLs being loaded on initialisation:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-1-960x646.png)

As we can see, the DLLs highlighted are all the DLLs that are loaded when the badger is injected. This list includes the loading of winhttp.dll and wininet.dll, which are not necessarily nefarious but are traditional loads for an egress beacon. There are however a number of less common DLLs loaded, such as dbghelp.dll, credui.dll samcli.dll and logoncli.dll amongst others.

This behaviour allows us to create a signature for the image loads and leads to a high signal indicator that can be hunted for through image load telemetry.

For example, using Elastic Query Language, we can search for the sequence of credui.dll, dbghelp.dll and winhttp.dll load events occurring in a process within 60 seconds of each other:

```
sequence by Image with maxspan=1m
	[any where ImageLoaded == 'C:\\Windows\\System32\\credui.dll']
	[any where ImageLoaded == 'C:\\Windows\\System32\\dbghelp.dll']
	[any where ImageLoaded == 'C:\\Windows\\System32\\winhttp.dll']
```

Using the EQL tool, or Elastic’s cloud, we can search our event data, such as the following which was extracted from sysmon logs. Note, we’re explicitly excluding the badger executable itself so we can only identify the injected badgers:

```
eql query -f sysmon-data.json "sequence by Image with maxspan=2m [any where ImageLoaded == 'C:\\Windows\\System32\\credui.dll' and Image != 'C:\\Users\\bob\\Desktop\\badger_x64_aws.exe'] [any where ImageLoaded == 'C:\\Windows\\System32\\dbghelp.dll' and Image != 'C:\\Users\\bob\\Desktop\\badger_x64_aws.exe'] [any where ImageLoaded == 'C:\\Windows\\System32\\winhttp.dll' and Image != 'C:\\Users\\bob\\Desktop\\badger_x64_aws.exe']"
```

This leads to the following which shows the detection of the badger being injected in to notepad.exe:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-2-960x243.png)

This query is particularly powerful as it allows us to retrospectively hunt for indicators of Brute Ratel badgers in the network, without directly running code on the endpoints.

## **Brute Ratel In Memory**

As most beacons remain memory resident, it is important to understand the footprint that is left behind in order to hunt for them. Reviewing the Brute Ratel documentation for the 1.0 release, it details its own implementation of obfuscate and sleep:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-3-960x119.png)

According to the release post, BRc4 uses a mixture of “Asynchronous Procedure Calls, Windows Event Creation, Wait Objects and Timers”. However, analysis of the badger was only able to find evidence of APC based execution; more on this later.

In order to analyse the badger in memory, we first inject it to a process using the pcinject command, then put the badger to sleep using the sleep command:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-4-960x473.png)

Once the badger is sleeping, we can recover the strings from the process using Process Hacker. Interestingly, while the badger is sleeping we can see strings such as the following:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-5.png)

Initially this was quite surprising given the aforementioned purported sleep and obfuscate strategies described on the Brute Ratel blog.

Digging deeper, we can find that some interesting design decisions have been made where by many of the strings displayed in the operator’s UI, are populated from the badger itself. For example, we can see the following in the memory of the badger while it is sleeping:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-6-960x492.png)

And these strings are then returned to the UI as we can see below:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-7.png)

Digging deeper in to the badger, it was quickly apparent that only the .text section was being obfuscated on sleep, leaving the badger susceptible to all manner of signatures against strings and data.

To illustrate this, reversing the badger we can see the entry point for the loader as “bruteloader”:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-8-960x221.png)

Searching for this string in memory while the badger is sleeping, we can quickly find it inside our notepad process:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-9-960x128.png)

These strings provide a good point on which to base a Yara rule for memory scanning on. For example, the following rule will search for either the bruteloader or bhttp\_x64.dll strings in memory of a process:

```
rule brc4_badger_strings
{
meta:
    author = "@domchell"
    description = "Identifies strings used in Badger v1.0.x rDLL, even while sleeping"
strings:
    $a = "bruteloader"
    $b = "bhttp_x64.dll"
condition:
    1 of them
}
```

We can test these against our notepad process while the badger is sleeping to evidence its effectiveness:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-10.png)

It is unlikely the strings will exist in other processes, and using a simple one liner we can quickly find all the injected badgers on our test system:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-11-960x479.png)

Plugging this Yara rule in to virus total, we can quickly find [other samples](https://www.virustotal.com/gui/file/c70b1fd133737a21904159ed2a867e0105060ac74937472da5e4d0e1f6fa1645), such as:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-12-960x149.png)

## **Page Permissions**

Analysis of the Brute Ratel obfuscate and sleep strategy observed the badger to shuffle the page permissions for the badger during sleep in an attempt to evade prolonging executable permissions while the badger sleeps.

Below, we can see the badger operating on a sleep 0, the page permissions for the badger are PAGE\_EXECUTE\_READ on an unmapped page; this is necessary in order to perform tasking:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-13-960x279.png)

Putting the badger to sleep, we can see that the obfuscate and sleep strategy obfuscates the .text section and resets the page permissions for the badger to to PAGE\_READWRITE:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-14-960x379.png)

Interestingly, we however note that this behaviour is not replicated while a SMB pivot is being performed, that is when two badgers are linked. Here we can see our two badgers linked and both on a 60 second sleep:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-15-960x110.png)

Analysis of the page permissions while two badgers are linked reveals that both remain PAGE\_EXECUTE\_READ, irrespective of the sleep time:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-16-960x188.png)

The conclusion is that the obfuscate and sleep strategy is only applicable to the .text section, and while no peer-to-peer pivot is present.

Curious to how the obfuscate and sleep functionality worked, we began to reverse engineer it. Walking through the sleep routine in windbg, we can get an initial flavour of what’s happening; the badger is using WaitForSingleObjectEx to delay execution during a series of asynchronous procedure calls (APC), and leveraging an indirect syscall to execute NtTestAlert and force an alert on the thread:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-17-960x398.png)

Diving in to IDA, we can get a better feel for what is happening. First it creates a new thread with the start address spoofed to a fixed location of TpReleaseCleanupGroupMembers+550:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-18-960x990.png)

A series of context structures are then created for a number of function calls, to NtWaitForSingleObject, NtProtectVirtualMemory, , SystemFunction032, NtGetContextThread and SetThreadContext:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-19-960x990.png)

Next, a number of APCs are queued against the NtContinue, with the intention of using it to proxy calls to the aforementioned context structures; this technique acts as a rudimentary form of ROP:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-20-960x710.png)

Having reverse engineered the sleeping technique, we soon realised that it it was very similar to [@ilove2pwn\_](https://twitter.com/ilove2pwn_)’s [Foliage](https://github.com/SecIdiot/FOLIAGE/blob/master/source/sleep.c) project, with the exception of the hardcoded thread start address.

Despite extensive debugging and reverse engineering of the badger, we unable to reveal any evidence of the “Windows Event Creation, Wait Objects and Timers” techniques referenced in the v1.0 blog post; indeed the APIs required for these techniques did not appear to be imported via the badger’s hashed imports.

## **Brute Ratels Threads**

To analyse how Brute Ratel threads look in memory, we injected the badger in to a fresh copy of notepad. Immediately, we can see there are some suspicious indicators in the threads used by the sleeping badger.

Firstly, we note that there is a suspicious looking thread with a 0x0 start address, and a single frame calling WaitForSingleObjectEx in the call stack:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-21.png)

We can speculate that this thread is used for the HTTP comms based on analysis of the thread call stack while the badger is now sleeping:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-22.png)

Based on the information we gained from reverse engineering the obfuscate and sleep strategy, we noted that new threads were created with a hardcoded spoofed start address of ntdll!TpReleaseCleanupGroupMembers+0x550:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-23-960x475.png)

We were unable to find any instances of this occurring as a start address naturally, and as such leads to a trivial indicator for hunting Brute Ratel threads. In practice this looks as follows within our injected notepad process:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-24.png)

The call stack for the thread is also slightly irregular as it not only contains calls to delay execution, but also the first frame points to ntdll.dll!NtTerminateJobObject+0x1f. A deeper look at why NtNerminateJobObject is used highlights that this is simply a ROP gadget for NtTestAlert and is used to execute pending APCs on the thread:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-25-960x398.png)

## **Memory Hooks**

In our first post in this series, we detailed two potential approaches for detecting in-memory beacons based on memory hooks; by looking for signatures of known patches (e.g. ret to ntdll.dll!EtwEventWrite) and by detecting copy on write operations.

Applying these concepts to Brute Ratel, we note that the badger does not apply any memory hooks until its post-exploitation functionality is used by the operator. An example of this, would be the sharpinline command, which runs a .NET assembly in the current process:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-26-960x329.png)

Once the assembly has completed and the beacon gone back to sleep, we can get a better understanding of whats going on by attaching a debugger and disassembling the values of ntdll.dll!EtwEventWrite and amsi.dll!AmsiScanBuffer:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-27-960x340.png)

As shown above, these are simple and persistent patches to disable .NET ETW data and inhibit AMSI. As the patches are persistent, we can detect them by either of the aforementioned techniques, since not only will we receive a high signal detection due to the first instruction of EtwEventWrite being a ret, but also an indicator that the pages where EtwEventWrite resides have been modified due to the clearing of the shared bit.

Using BeaconHunter, we can rapidly detect these hooks based on resolving the exports on the modified pages, providing a strong indicator that malicious tampering has taken place:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-28.png)

## **Brute Ratel C2 Server**

Moving away from the endpoint, as hunters we also have an interest in detecting the command-and-control infrastructure as this may assist in providing us with sufficient intelligence to detect beaconing based on network telemetry.

The C2 server for Brute Ratel is developed in golang, and by default only allows the operator to modify the default landing page for the C2. To fingerprint the C2 server, we discovered it was possible to generate an unhandled exception when sending a POST request containing base64 to any URI. For example, consider the following base64 POST data compared with the the plaintext:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-29-960x465.png)

It is likely this occurs as the expected input for the base64 decoded POST data should conform to the C2 traffic format. A simple Nuclei rule might help us in scanning for this kind of infrastructure:

```
id: brc4-ts

info:
  name: Brute Ratel C2 Server Fingerprint
  author: Dominic Chell
  severity: info
  description: description
  reference:
    - https://
  tags: tags
requests:
  - raw:
      - |-
        POST / HTTP/1.1
        Host: {{Hostname}}
        Content-Length: 8

        Zm9vYmFy
```

Outside of direct interaction with the C2, it is also possible to detect C2 infrastructure where the operator has not manually redefined the default landing page based on a hash of the HTML ( [http.html\_hash=-1957161625](https://www.shodan.io/search?query=http.html_hash%3A-1957161625)).

Using a simple Shodan [query](https://www.shodan.io/search?query=http.html_hash%3A-1957161625), we can quickly find live infrastructure exposed to the Internet:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-30-960x514.png)

Although only around 40 team servers were identified, we can get a better picture of where these are located based on the geographical spread:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-31-960x544.png)

It is quite likely some of these techniques are already known, as based on reports against our test infrastructure, defenders are actively hunting these C2 servers:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-32-960x583.png)![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-33-960x61.png)

## **Brute Ratel Configurations**

Analysis of the Badger revealed that Brute Ratel maintains an encrypted configuration structure in memory which includes details on the C2 endpoints. Being able to extract this from either artifacts or from running processes can prove helpful for defenders. Our analysis revealed that this configuration is held in a base64 and RC4 encrypted blob using a fixed key of “bYXJm/3#M?:XyMBF” in the artifacts for the badger. While the configuration is stored plaintext in memory for the sleeping badger.

We developed the following config extractor that can be used against both on-disk artifacts for BRC4 v1.0.x or injected sleeping badgers with Brute Ratel 1.0.x and 1.1.x:

```
#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>
#include <Windows.h>
#include <string>
#include <vector>

#pragma comment(lib, "Crypt32.lib")

std::string HexDump(void* pBuffer, DWORD cbBuffer)
{
	PBYTE pbBuffer = (PBYTE)pBuffer;
	std::string strHex;

#define FORMAT_APPEND_1(a)	{ char szTmp[256]; sprintf(szTmp, a); strHex += szTmp; }
#define FORMAT_APPEND_2(a,b)	{ char szTmp[256]; sprintf(szTmp, a, b); strHex += szTmp; }

	for (DWORD i = 0; i < cbBuffer;)
	{
		FORMAT_APPEND_2("0x8x  ", i);

		DWORD n = ((cbBuffer - i) < 16) ? (cbBuffer - i) : 16;

		for (DWORD j = 0; j < n; j++)
		{
			FORMAT_APPEND_2("%02X ", pbBuffer[i + j]);
		}

		for (DWORD j = 0; j < (16 - n); j++)
		{
			FORMAT_APPEND_1("   ");
		}

		FORMAT_APPEND_1(" ");

		for (DWORD j = 0; j < n; j++)
		{
			FORMAT_APPEND_2("%c", (pbBuffer[i + j] < 0x20 || pbBuffer[i + j] > 0x7f) ? '.' : pbBuffer[i + j]);
		}

		FORMAT_APPEND_1("\n");

		i += n;
	}

	return strHex;
}

BOOL ReadAllBytes(std::string strFile, PBYTE* ppbBuffer, UINT* puiBufferLength)
{
	BOOL bSuccess = FALSE;
	PBYTE pbBuffer = NULL;

	*ppbBuffer = NULL;
	*puiBufferLength = 0;

	FILE* fp = fopen(strFile.c_str(), "rb");
	if (fp)
	{
		fseek(fp, 0, SEEK_END);
		long lFile = ftell(fp);
		fseek(fp, 0, SEEK_SET);

		if (!(pbBuffer = (PBYTE)malloc(lFile)))
			goto Cleanup;

		if (fread(pbBuffer, 1, lFile, fp) != lFile)
			goto Cleanup;

		*ppbBuffer = pbBuffer;
		*puiBufferLength = (UINT)lFile;

		pbBuffer = NULL;
		bSuccess = TRUE;
	}

Cleanup:
	if (fp) fclose(fp);
	if (pbBuffer) free(pbBuffer);
	return bSuccess;
}

void Brc4DecodeString(BYTE* pszKey, BYTE* pszInput, BYTE* pszOutput, int cchInput)
{
	BYTE szCharmap[0x100];

	for (UINT i = 0; i < sizeof(szCharmap); i++)
	{
		szCharmap[i] = (char)i;
	}

	UINT cchKey = strlen((char*)pszKey);

	BYTE l = 0;

	for (UINT i = 0; i < sizeof(szCharmap); i++)
	{
		BYTE x = szCharmap[i];
		BYTE k = pszKey[i % cchKey];
		BYTE y = x + k + l;
		l = y;
		szCharmap[i] = szCharmap[y];
		szCharmap[y] = x;
	}

	l = 0;

	for (UINT i = 0; i < cchInput; i++)
	{
		BYTE x = szCharmap[i + 1];
		BYTE y = x + l;
		l = y;
		BYTE z = szCharmap[y];
		szCharmap[i + 1] = z;
		szCharmap[y] = x;
		x = x + szCharmap[i + 1];
		x = szCharmap[x];
		x = x ^ pszInput[i];
		pszOutput[i] = x;
	}
}

BOOL MatchPattern(PBYTE pbInput, PBYTE pbSearch, DWORD cbSearch, BYTE byteMask)
{
	BOOL bMatch = TRUE;

	for (DWORD j = 0; j < cbSearch; j++)
	{
		if (pbSearch[j] != byteMask && pbInput[j] != pbSearch[j])
		{
			bMatch = FALSE;
			break;
		}
	}

	return bMatch;
}

PBYTE FindPattern(PBYTE pbInput, UINT cbInput, PBYTE pbSearch, DWORD cbSearch, BYTE byteMask, UINT* pcSkipMatches)
{
	if (cbInput > cbSearch)
	{
		for (UINT i = 0; i < cbInput - cbSearch; i++)
		{
			BOOL bMatch = MatchPattern(pbInput + i, pbSearch, cbSearch, byteMask);

			if (bMatch)
			{
				if (!*pcSkipMatches)
				{
					return &pbInput[i];
				}

				(*pcSkipMatches)--;
			}
		}
	}

	return NULL;
}

BOOL LocateBrc4Config(PBYTE pbInput, UINT cbInput, PBYTE* ppbConfig)
{
#define XOR_RAX_RAX			0x48, 0x31, 0xC0,
#define PUSH_RAX			0x50,
#define MOV_EAX_IMM32		0xB8, 0xab, 0xab, 0xab, 0xab,
#define MOV_RAX_IMM64		0x48, 0xB8, 0xab, 0xab, 0xab, 0xab, 0xab, 0xab, 0xab, 0xab,
#define PUSH_IMM32			0x68, 0xab, 0xab, 0xab, 0xab,
#define MOV_EAX_0			0xB8, 0x00, 0x00, 0x00, 0x00,

	BYTE Pattern1[] =
	{
		XOR_RAX_RAX
		PUSH_RAX
		MOV_EAX_IMM32
		PUSH_RAX
		MOV_RAX_IMM64
		PUSH_RAX
		MOV_RAX_IMM64
		PUSH_RAX
		MOV_RAX_IMM64
		PUSH_RAX
		MOV_RAX_IMM64
		PUSH_RAX
		MOV_RAX_IMM64
		PUSH_RAX
		MOV_RAX_IMM64
	},
	Pattern2[] =
	{
		XOR_RAX_RAX
		PUSH_RAX
		MOV_RAX_IMM64
		PUSH_RAX
		MOV_RAX_IMM64
		PUSH_RAX
		MOV_RAX_IMM64
		PUSH_RAX
		MOV_RAX_IMM64
		PUSH_RAX
		MOV_RAX_IMM64
		PUSH_RAX
		MOV_RAX_IMM64
		PUSH_RAX
		MOV_RAX_IMM64
	};

	UINT cSkipMatches = 0;

	if (cbInput < 100)
	{
		return FALSE;
	}

	PBYTE pbConfigStart = FindPattern(pbInput, cbInput, Pattern1, sizeof(Pattern1), 0xab, &cSkipMatches);

	if (!pbConfigStart)
	{
		cSkipMatches = 0;

		pbConfigStart = FindPattern(pbInput, cbInput, Pattern2, sizeof(Pattern2), 0xab, &cSkipMatches);

		if (!pbConfigStart)
		{
			return FALSE;
		}
	}

	BYTE Pattern3[] = {
		PUSH_IMM32
		MOV_EAX_0
		PUSH_RAX
		MOV_EAX_0
		PUSH_RAX
		MOV_EAX_0
		PUSH_RAX
	};

	cSkipMatches = 0;

	PBYTE pbConfigEnd = FindPattern(pbConfigStart, cbInput - (pbConfigStart - pbInput), Pattern3, sizeof(Pattern3), 0xab, &cSkipMatches);

	if (!pbConfigEnd)
	{
		return FALSE;
	}

	*ppbConfig = (PBYTE)malloc(pbConfigEnd - pbConfigStart);

	if (!*ppbConfig)
	{
		return FALSE;
	}

	memset(*ppbConfig, 0, pbConfigEnd - pbConfigStart);

	pbConfigStart += 4; // skip: XOR_RAX_RAX / PUSH_RAX

	BYTE Pattern4[] = {
		MOV_EAX_IMM32
		PUSH_RAX
	},
	Pattern5[] = {
		MOV_RAX_IMM64
		PUSH_RAX
	};

	for (UINT uiIndex = 0, i = 0; i < pbConfigEnd - pbConfigStart;)
	{
		if (MatchPattern(pbConfigStart + i, Pattern4, sizeof(Pattern4), 0xab))
		{
			(*ppbConfig)[uiIndex++] = pbConfigStart[i + 4];
			(*ppbConfig)[uiIndex++] = pbConfigStart[i + 3];
			(*ppbConfig)[uiIndex++] = pbConfigStart[i + 2];
			(*ppbConfig)[uiIndex++] = pbConfigStart[i + 1];

			i += sizeof(Pattern4);
		}
		else if (MatchPattern(pbConfigStart + i, Pattern5, sizeof(Pattern5), 0xab))
		{
			(*ppbConfig)[uiIndex++] = pbConfigStart[i + 9];
			(*ppbConfig)[uiIndex++] = pbConfigStart[i + 8];
			(*ppbConfig)[uiIndex++] = pbConfigStart[i + 7];
			(*ppbConfig)[uiIndex++] = pbConfigStart[i + 6];
			(*ppbConfig)[uiIndex++] = pbConfigStart[i + 5];
			(*ppbConfig)[uiIndex++] = pbConfigStart[i + 4];
			(*ppbConfig)[uiIndex++] = pbConfigStart[i + 3];
			(*ppbConfig)[uiIndex++] = pbConfigStart[i + 2];

			i += sizeof(Pattern5);
		}
		else if (MatchPattern(pbConfigStart + i, Pattern3, sizeof(Pattern3), 0xab))
		{
			break;
		}
		else
		{
			return FALSE;
		}
	}

	std::string config = (char*)*ppbConfig;
	std::reverse(config.begin(), config.end());

	strcpy((char*)*ppbConfig, config.c_str());

	return TRUE;
}

BOOL FromBase64(char* pszString, PBYTE* ppbBinary, UINT* pcbBinary)
{
	DWORD cbBinary = 0;

	if (FAILED(CryptStringToBinaryA(pszString, 0, CRYPT_STRING_BASE64, NULL, &cbBinary, NULL, NULL)))
	{
		return FALSE;
	}

	*ppbBinary = (PBYTE)malloc(cbBinary + 1);

	if (!*ppbBinary)
	{
		return FALSE;
	}

	if (FAILED(CryptStringToBinaryA(pszString, 0, CRYPT_STRING_BASE64, *ppbBinary, &cbBinary, NULL, NULL)))
	{
		return FALSE;
	}

	*pcbBinary = cbBinary;

	return TRUE;
}

BOOL ScanProcessForBadgerConfig(HANDLE hProcess, std::string& badgerId, std::vector<std::wstring>& configStrings)
{
	SIZE_T nBytesRead;
	PBYTE lpMemoryRegion = NULL, pbBadgerStateStruct = NULL;

	printf("[+] Searching process memory for badger state ...\n");

	while (1)
	{
		MEMORY_BASIC_INFORMATION mbi = { 0 };

		if (!VirtualQueryEx(hProcess, lpMemoryRegion, &mbi, sizeof(mbi)))
		{
			break;
		}

		if ((mbi.State & MEM_COMMIT) && !(mbi.Protect & PAGE_GUARD) &&
			((mbi.Protect & PAGE_READONLY) || (mbi.Protect & PAGE_READWRITE) || (mbi.Protect & PAGE_EXECUTE_READWRITE)))
		{
			//printf("[+] Searching process memory at 0x%p (size 0x%x)\n", lpMemoryRegion, mbi.RegionSize);

			PBYTE pbLocalMemoryCopy = (PBYTE)malloc(mbi.RegionSize);

			if (!ReadProcessMemory(hProcess, lpMemoryRegion, pbLocalMemoryCopy, mbi.RegionSize, &nBytesRead))
			{
				//printf("[!] Unable to read memory at 0x%p\n", lpMemoryRegion);
			}
			else
			{
				for (UINT i = 0; i < mbi.RegionSize - 128 && !pbBadgerStateStruct; i++)
				{
					if (memcmp(pbLocalMemoryCopy + i, "b-", 2) == 0)
					{
						char* pszEndPtr = NULL;
						int badgerId = strtoul((char*)pbLocalMemoryCopy + i + 2, &pszEndPtr, 10);

						if (pszEndPtr != (char*)pbLocalMemoryCopy + i + 2 && pszEndPtr && *pszEndPtr == '\\' && strnlen(pszEndPtr, 100) > 16)
						{
							pbBadgerStateStruct = lpMemoryRegion + i;
							break;
						}
					}
				}
			}

			free(pbLocalMemoryCopy);
			pbLocalMemoryCopy = NULL;
		}

		lpMemoryRegion += mbi.RegionSize;
	}

	if (!pbBadgerStateStruct)
	{
		printf("[!] Failed to find badger state\n");
		return FALSE;
	}

	printf("[+] Found badger state at 0x%p\n", pbBadgerStateStruct);

	BYTE BadgerState[0x1000];

	memset(BadgerState, 0, sizeof(BadgerState));

	if (!ReadProcessMemory(hProcess, pbBadgerStateStruct, BadgerState, 0x1000, &nBytesRead))
	{
		if (GetLastError() != ERROR_PARTIAL_COPY)
		{
			printf("[!] Unable to read badger state at 0x%p\n", pbBadgerStateStruct);
			return FALSE;
		}
	}

	badgerId = (char*)BadgerState;

	BYTE ConfigString[1024];

	memset(ConfigString, 0, sizeof(ConfigString));

	for (UINT i = 0x100 + (0x10 - ((DWORD64)pbBadgerStateStruct & 0xf)); i < sizeof(BadgerState); i += sizeof(DWORD64))
	{
		DWORD64 pMem = *(DWORD64*)(BadgerState + i);

		if (pMem)
		{
			ConfigString[0] = 0;

			if (!ReadProcessMemory(hProcess, (LPVOID)pMem, ConfigString, 1024, &nBytesRead) || nBytesRead != 1024)
			{
				continue;
			}

			BOOL bIsValid = ConfigString[0] != 0;
			std::wstring badgerString;

#define MIN_STRING_LENGTH	5

			if (bIsValid)
			{
				char* pszConfigString = (char*)ConfigString;

				for (UINT j = 0; j < nBytesRead && pszConfigString[j] != 0; j++)
				{
					if (!isprint(pszConfigString[j]) && !(pszConfigString[j] == '\t' || pszConfigString[j] == '\r' || pszConfigString[j] == '\n'))
					{
						break;
					}

					badgerString.push_back(pszConfigString[j]);
				}

				bIsValid = badgerString.size() >= MIN_STRING_LENGTH;
			}

			if (!bIsValid)
			{
				badgerString.clear();
				bIsValid = TRUE;

				WCHAR* pwszConfigString = (WCHAR*)ConfigString;

				for (UINT j = 0; j < nBytesRead / sizeof(WCHAR) && pwszConfigString[j] != 0; j++)
				{
					if (!iswprint(pwszConfigString[j]) && !(pwszConfigString[j] == '\t' || pwszConfigString[j] == '\r' || pwszConfigString[j] == '\n'))
					{
						break;
					}

					badgerString.push_back(pwszConfigString[j]);
				}

				bIsValid = badgerString.size() >= MIN_STRING_LENGTH;
			}

			if (bIsValid)
			{
				configStrings.push_back(badgerString);
			}
		}
	}

	return TRUE;
}

int main(int argc, char *argv[])
{
	PBYTE key = (PBYTE)"bYXJm/3#M?:XyMBF";

	printf("BruteRatel v1.x Config Extractor\n");

	if (argc < 2)
	{
		printf(
			"Usage: Brc4ConfigExtractor.exe <file> [key]\n"
			"    <file|pid> - file to scan for config, or running process ID\n"
			"    [key]  - key if not default\n"
		);

		return 1;
	}

	if (argc > 2)
	{
		key = (PBYTE)argv[2];
	}

	if (atoi(argv[1]) == 0)
	{
		PBYTE pbBadger = NULL;
		UINT cbBadger = 0;

		if (!ReadAllBytes(argv[1], &pbBadger, &cbBadger))
		{
			printf("[!] Input file '%s' not found\n", argv[1]);
			return 1;
		}

		printf("[+] Analysing file '%s' (%u bytes)\n", argv[1], cbBadger);

		PBYTE pbConfigText = NULL;

		if (!LocateBrc4Config(pbBadger, cbBadger, &pbConfigText))
		{
			printf("[!] Failed to locate BRC4 config\n");
			return 1;
		}

		printf("[+] Located BRC4 config: %s\n", pbConfigText);

		PBYTE pbBinaryConfig = NULL;
		UINT cbBinaryConfig = 0;

		if (!FromBase64((char*)pbConfigText, &pbBinaryConfig, &cbBinaryConfig))
		{
			printf("[!] Failed to decode BRC4 config from base64\n");
			return 1;
		}

		Brc4DecodeString(key, pbBinaryConfig, pbBinaryConfig, cbBinaryConfig);

		printf("[+] Decoded config: %.*s\n", cbBinaryConfig, pbBinaryConfig);
	}
	else
	{
		DWORD dwPid = atoi(argv[1]);

		printf("[+] Analysing process with ID %u\n", dwPid);

		HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, dwPid);

		if (!hProcess)
		{
			printf("[!] Failed to open process\n");
			return 1;
		}

		std::string badgerId;
		std::vector<std::wstring> configStrings;

		if (!ScanProcessForBadgerConfig(hProcess, badgerId, configStrings))
		{
			printf("[!] Failed to locate badger configuration in memory\n");
			return 1;
		}

		printf("[+] Badger '%s' found...\n", badgerId.c_str());

		for (auto configString : configStrings)
		{
			printf("    : %S\n", configString.c_str());
		}

		CloseHandle(hProcess);
	}

	return 0;
}
```

Running the extractor tool on either an artifact or a running process (even while sleeping), will extract the Brute Ratel configuration state for the process or artifact:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-34-960x498.png)

# Updated v1.1 Analysis

Shortly after our talk on this subject at x33fcon, Brute Ratel announced a new version of the software. As such, it seemed appropriate to analyse this to ensure defenders have accurate advice given the recent uptake in Brute Ratel by threat actors.

## Analysis of Obfuscate and Sleep Techniques

One of the things that struck us about the v1.1 release, was the declaration that the author had discovered new sleep and obfuscate techniques. As stated in this [YouTube video](https://www.youtube.com/watch?v=nB5QHVtN9_g&t=267s) “ **Brute Ratel C4 v/s Nighthawk and Open Source Sleep Obfuscation Techniques**“, the author says “I didn’t even knew (SIC) about this technique until Austin released the blog post on this. However, Brute Ratel does not use either of these two techniques that we have seen over here.” in reference to the APC technique used in [Foliage](https://github.com/SecIdiot/FOLIAGE) and the Timer based technique as used in MDSec’s Nighthawk and as reverse engineered [here](https://suspicious.actor/2022/05/05/mdsec-nighthawk-study.html) and a proof of concept implementation released [here](https://github.com/Cracked5pider/Ekko/blob/main/Src/Ekko.c). Noting that this video appeared a short time after the Ekko release.

Reverse engineering of the obfuscate in sleep techniques used within Brute Ratel v1.1 reveal that three sleeping strategies are now available. The first, as we have previously documented is an extremely similar implementation to [@ilove2pwn\_](https://twitter.com/ilove2pwn_)’s Foliage, if not an exact copy.

The second implementation, reverse engineering revealed to be an almost identical implementation of [@c5pider](https://twitter.com/c5pider)’s Ekko code (and originally discovered by [Peter Winter-Smith](https://twitter.com/peterwintrsmith) and used in MDSec’s Nighthawk). For example, consider the following taken from [Ekko](https://github.com/Cracked5pider/Ekko/blob/main/Src/Ekko.c#L97):

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-35-960x604.png)

Compare this with the technique implemented inside Brute Ratel:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-36-960x640.png)

As you can see, the code is almost identical; indeed the few changes include replacing the WinApi calls for CreateTimerQueueTimer with the Rtl wrapper RtlCreateTimer, noting that the breakpoints for Rtl wrappers were avoided (likely intentionally) in the aforementioned video demonstration.

This brings us to the third technique used by Brute Ratel which is a variation of timers and is not publicly documented. We can see here that this technique uses a subtle variation on timers and instead proxies the timer through RtlRegisterWait:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-37-960x508.png)

While this technique is not publicly documented, it has been available in Nighthawk for some time, coincidentally with the same values used for many of the constants. Further coincidences arise with other undocumented/unpublished features arising in the Brute Ratel v1.1 release.

So far, we have only discussed the sleeping techniques available in the x64 implementation of Brute Ratel. Analysis of the x86 implementation shows that the obfuscate and sleep strategies are fixed to the aforementioned APC Foliage based implementation (noting the breakpoints never hit):

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-38-960x244.png)

To date there are no public or open source x86 implementations of obfuscate and sleep strategies that use timers, limiting the available opportunities to easily integrate such code without custom development.

## **In Memory Detections**

One of the updates in the v1.1 release implies that the .rdata section is now also obfuscated, in order to hide strings such as “\[+\] AMSI Patched” which were exposed in the memory of the sleeping badger. However, even cursory memory analysis shows there remains many exposed strings within the memory of the sleeping badger. As a result, this means there are many opportunities to pluck out Brute Ratel processes on an endpoint, even while the badger is sleeping. For example, consider the Brute Ratel C2 data which is stored in a JSON format, simply searching for one of its unique parameters in memory such as “chkin” will allow us to spot a badger:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-39-960x364.png)

Or simply searching for the badger identifier (e.g. b-) will find them scattered all over both the heap and the stack. As a bonus, this can act as simple mechanism to spot the thread that Brute Ratel is operating from, for example:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-40-960x40.png)

Here we can see the presence of the “b-4\\” on the stack of thread 4344. We can confirm that is indeed the thread for Brute Ratel from the UI:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-41-960x159.png)

With this in mind, we’re able to build a simple but effective Yara rule to pluck sleeping Brute Ratel processes from memory:

```
rule brc4_badger_strings
{
meta:
    author = "@domchell"
    description = "Identifies strings from Brute Ratel v1.1"
strings:
    $a = "\"chkin\":"
condition:
    $a
}
```

Executing the Yara rule, we can spot the sleeping badger:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-42-960x317.png)

The detections documented in v1.0 for post-exploitation actions such as suspicious copy on write operations remain relevant and still offer an effective means of detection for BRC4 post-exploitation.

## **Thread Stack Spoofing**

In the v1.0 release of Brute Ratel, as we noted the start address of the thread is hardcoded to ntdll!TpReleaseCleanupGroupMembers+0x550. Version 1.1 proclaims to offer “full thread stack masquerading”. Analysis of the stack spoofing for Brute Ratel reveals a simplistic implementation of rewriting the threads call stack. This process occurs just prior to the badger going to sleep, using the aforementioned timer technique. In an attempt to make the thread appear more legitimate, a new thread stack is created with hardcoded addresses for the first two frames. The addresses hardcoded are at offsets 0xa and 0x12 from RtlUserThreadStart and BaseThreadInitThunk respectively:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-43-960x583.png)

We were able to identify any other threads using these hardcoded start addresses, as such it becomes trivial to identify any Brute Ratel threads on a system. To detect these threads, we updated BeaconHunter accordingly to identify threads with the first two frames at RtlUserThreadStart+0xa and BaseThreadInitThunk+0x12:

![](https://www.mdsec.co.uk/wp-content/uploads/2022/08/image-44-960x581.png)

## Updated rDLL Extraction

Shortly after our analysis at x33fcon, Brute Ratel announced an update to the method in which the artifacts hide the reflective DLL. Analysis of these artifacts revealed that this is achieved using RC4 to encrypt the reflective DLL with a random key; the PE header is then stomped. The 8 byte RC4 key is appended to the encrypted reflective DLL, followed by 400 bytes of base64 configuration file.

We developed the following tool targeting Brute Ratel v1.1 to extract the reflective DLL from DLL and EXE artifacts:

```
//
// only works with BRC4 1.1 binaries.
//
#include <algorithm
#include <windows.h>
#include <cstdio>
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <iomanip>

typedef struct _RC4_CTX {
    BYTE       x, y;
    BYTE       s[256];
} RC4_CTX, *PRC4_CTX;

std::vector<BYTE>
ReadData(std::string path) {
    std::ifstream instream(path, std::ios::in | std::ios::binary);
    std::vector<BYTE> input((std::istreambuf_iterator<char>(instream)), std::istreambuf_iterator<char>());
    return input;
}

bool
WriteData(std::string path, std::vector<BYTE> data) {
    std::ofstream outstream(path, std::ios::out | std::ios::binary);
    std::copy(data.begin(), data.end(), std::ostreambuf_iterator<char>(outstream));
    return outstream.good();
}

BYTE
start_sig[]={
#if defined(_WIN64)
    0x55, 0x50, 0x53, 0x51, 0x52, 0x56, 0x57, 0x41, 0x50, 0x41, 0x51, 0x41, 0x52, 0x41, 0x53, 0x41,
    0x54, 0x41, 0x55, 0x41, 0x56, 0x41, 0x57, 0x48, 0x89, 0xE5, 0x48, 0x83, 0xE4, 0xF0, 0x48, 0x31,
    0xC0, 0x50
#else
    0x60, 0x89, 0xE5, 0x83, 0xE4, 0xF8, 0x31, 0xC0, 0x50
#endif
};

BYTE
end_sig[]={
#if defined(_WIN64)
    0x41, 0x5F, 0x41, 0x5E, 0x41, 0x5D, 0x41, 0x5C, 0x41, 0x5B, 0x41, 0x5A, 0x41, 0x59, 0x41, 0x58,
    0x5F, 0x5E, 0x5A, 0x59, 0x5B, 0x58, 0x5D, 0xC3
#else
    0x83, 0xC4, 0x10, 0x61, 0xC3
#endif
};

void
RC4_set_key(
    PRC4_CTX c,
    PVOID    key,
    UINT     keylen)
{
    UINT i;
    UCHAR j;
    PUCHAR k=(PUCHAR)key;

    for (i=0; i<256; i++) {
        c->s[i] = (UCHAR)i;
    }

    c->x = 0; c->y = 0;

    for (i=0, j=0; i<256; i++) {
        j = (j + (c->s[i] + k[i % keylen]));
        UCHAR t = c->s[i];
        c->s[i] = c->s[j];
        c->s[j] = t;
    }
}

void
RC4_crypt(
    PRC4_CTX c,
    PUCHAR   buf,
    UINT     len)
{
    UCHAR x = c->x, y = c->y, j=0, t;

    for (UINT i=0; i<len; i++) {
        x = (x + 1);
        y = (y + c->s[x]);
        t = c->s[x];
        c->s[x] = c->s[y];
        c->s[y] = t;
        j = (c->s[x] + c->s[y]);
        buf[i] ^= c->s[j];
    }
    c->x = x;
    c->y = y;
}

std::vector<BYTE>
extract_encrypted_rdll(PBYTE ptr, DWORD maxlen) {
    std::vector<BYTE> outbuf;
    printf("Searching %ld bytes.\n", maxlen);

    for (DWORD i=0; i<maxlen;) {
        if (!memcmp(&ptr[i], end_sig, sizeof(end_sig))) {
            printf("Reached end of signature...\n");
            break;
        }
    #if defined(_WIN64)
        if ((ptr[i] & 0x40) == 0x40 && (ptr[i+1] & 0xB0) == 0xB0)
        {
            BYTE buf[8];

            buf[0] = ptr[i + 9];
            buf[1] = ptr[i + 8];
            buf[2] = ptr[i + 7];
            buf[3] = ptr[i + 6];
            buf[4] = ptr[i + 5];
            buf[5] = ptr[i + 4];
            buf[6] = ptr[i + 3];
            buf[7] = ptr[i + 2];

            outbuf.insert(outbuf.end(), buf, buf + sizeof(buf));
            i += (ptr[i + 10] == 0x41) ? 12 : 11;
        } else i++;
    #else
        if ((ptr[i] & 0xB0) == 0xB0 && (ptr[i+5] & 0x50) == 0x50) {
            BYTE buf[4];

            buf[0] = ptr[i + 4];
            buf[1] = ptr[i + 3];
            buf[2] = ptr[i + 2];
            buf[3] = ptr[i + 1];

            outbuf.insert(outbuf.end(), buf, buf + sizeof(buf));
            i += 6;
        } else i++;
    #endif
    }
	std::reverse(outbuf.begin(), outbuf.end());
    return outbuf;
}

int
main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("usage: decrypt_brc4 <DLL|EXE>\n");
        return 0;
    }

    std::vector<BYTE> inbuf, infile = ReadData(argv[1]);
    DWORD len=0, ptr=0;

    if (infile.empty()) {
        printf("Nothing to read.\n");
        return 0;
    }

    do {
        auto dos = (PIMAGE_DOS_HEADER)infile.data();
        auto nt = (PIMAGE_NT_HEADERS)(infile.data() + dos->e_lfanew);
        auto s = IMAGE_FIRST_SECTION(nt);

        for (DWORD i=0; i<nt->FileHeader.NumberOfSections; i++) {
            char Name[IMAGE_SIZEOF_SHORT_NAME + 1] = {0};
            memcpy(Name, s[i].Name, IMAGE_SIZEOF_SHORT_NAME);

            if (std::string(Name) == ".data") {
                len = s[i].SizeOfRawData;
                ptr = s[i].PointerToRawData;
                break;
            }
        }

        if (!len) {
            printf("Unable to locate .data section.\n");
            break;
        }

        printf("Searching %ld bytes for loader...\n", len);

        for (DWORD idx=0; idx<len - sizeof(start_sig); idx++) {
            if(!memcmp(infile.data() + ptr + idx, start_sig, sizeof(start_sig))) {
                printf("Found signature : %08lX\n", ptr + idx);
                inbuf = extract_encrypted_rdll(infile.data() + ptr + idx, len - idx);
                break;
            }
        }

        if (inbuf.size()) {
            printf("size : %zd\n", inbuf.size());
            RC4_CTX c;
            BYTE key[8+1] = {0};
            memcpy((char*)key, inbuf.data() + inbuf.size() - 400 - 8, 8);

            //
            // Decrypt RDLL. The additional 400 bytes are base64 configuration.
            //
            RC4_set_key(&c, key, 8);
            RC4_crypt(&c, inbuf.data(), inbuf.size() - 400);

            //
            // Fix DOS header.
            //
            inbuf[0] = 'M';
            inbuf[1] = 'Z';
            WriteData(std::string(argv[1]) + ".dll", inbuf);
        }
    } while (FALSE);

    return 0;
}
```

## Conclusion

In summary, we’ve highlighted a number of techniques to detect Brute Ratel both in its artifacts, in-memory, through threat hunting and across the network. As this framework grows in popularity with threat actors, it is important to understand the many ways in which it can be detected. As a side note, we have also illustrated how the framework takes close inspiration from the many available open source community tools; knowledge of these can assist in reverse engineering the framework and provide a better understanding of its capabilities (and by virtue its detection points).

This blog post was written [Dominic Chell](https://twitter.com/domchell).

![](https://secure.gravatar.com/avatar/9cb7b62409a4b5ef00769dca4ba852fc49229c9729d600fc2637daf77068c31c?s=96&d=wp_user_avatar&r=g)

written by

#### MDSec Research

## Ready to engage  with MDSec?

[Get in touch](https://www.mdsec.co.uk/contact)

Stay updated with the latest

news from MDSec.


Newsletter Signup Form

Email


reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

If you are human, leave this field blank.

Submit

Copyright 2026 MDSec