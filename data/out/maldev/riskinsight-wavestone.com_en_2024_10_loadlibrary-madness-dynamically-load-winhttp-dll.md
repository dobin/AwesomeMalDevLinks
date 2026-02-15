# https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/

[Skip to content](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#content)

Search for:

- [Deep-dive](https://www.riskinsight-wavestone.com/en/category/formats-en/deep-dive-en/)
- [Ethical Hacking & Incident Response](https://www.riskinsight-wavestone.com/en/category/sections/cybersecurity-digital-trust/ethical-hacking-indicent-response-en/)

# LoadLibrary madness: dynamically load WinHTTP.dll

- 1 year ago
- Read Time: 11 minutes
- by [Yoann DEQUEKER](https://www.riskinsight-wavestone.com/en/author/yoann-dequeker/ "Posts by Yoann DEQUEKER")
- [Leave a comment](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/)

For the last few weeks, I have been developing a full custom _Command and Control_ ( _C2_). This _C2_ uses several _Windows DLL_ for network communication and specially the _WINHTTP.DLL_ one to handle _HTTP_requests used for the _HTTP_ and _HTTPS_ listener.

As everyone knows, when developing a _C2_ and the corresponding agent, _OPSEC_ must be the priority, so the agent code must rise as few events (_ETW_) as possible.

The most common way to increase _OPSEC_when using external _DLL_is to perform dynamic loading to avoid getting the loaded _DLL_name in the source code. This can be done using the _LoadLibrary Win32 API_.

This _API_allows a program to load a specific _DLL_ from the disk. However, the drawback is that _LoadLibrary_ raises several events and telemetry an _EDR_can analyze to detect the malicious _C2_agent.

In order to avoid this kind of event, I chose to implement a custom _LoadLibrary_that will not raise such events.

## State of the art – LoadLibrary

I will not go too much deeper in the implementation details, as this has already been documented several times in _blogposts_ [\[1\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftn1) or _books_ ( _Windows Internals Part 1_).

The goal here is to create a function that takes as an input a _DLL_path and loads the _DLL_ in memory. Doing it manually has a lot of advantages:

- Limits _ETW_and _Microsoft_telemetry
- More choices in the way sections are allocated and written.
- Possibility to hide malicious loaded _DLL_ when not used.

However, there are a lot of edge cases that could make the custom loader unreliable as it was mentioned in the _SpecterOps_blogpost _PerfectLoader[\[2\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftn2)_:

`The quality of these reimplementations may be judged by comparing the feature set of these custom loaders against what the OS’s native loader supports. As such, the native OS loader may be considered a “perfect loader,” but it should not be considered the only perfect loader.`

### Basic implementation

The basic implementation consists in just copying the _DLL_ image in memory, performing relocation, importing imported modules and resolving the _IAT_ entries.

The different steps can be found in the _Windows Internal Part 1_ book ( _page 178_) and a more described implementation can be found here [\[3\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftn3).

This is the most common way to load a _DLL_. Once the _DLL_ is loaded as-is in memory, it can be used for basic usages. However, any use of standard _Win32API_ against this _DLL_ such as _GetModuleHandle_ or _GetProcAddress_will fail.

This implementation does not implement any additional feature provided by the _Windows DLL_ loader: it just performs a textbook _DLL_ loading.

### Fixing compatibility with Microsoft WIN32API

The previous implementation has the merit of working and it helped me out more times I can count. However, it is not reliable; the most important edge case being the _DLL_ cannot be searched using _GetModuleHandle_or _LoadLibrary_.

Therefore, if the others _DLL_need access to the loaded _DLL_, they will not find it with the standard _Win32API_and will load it again using _LoadLibrary_leading to a nice _ETW_event: all we wanted to avoid in the first place.

_Batsec_[\[4\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftn4) wrote an _article_ [\[5\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftn5) on how the _DLL_ can be loaded in memory and still be compatible with the _Microsoft_ _Win32 API_ (at least _GetProcAddress_, _LoadLibrary_and _GetModuleHandle_) without raising a bunch of events.

His research shows that when a _DLL_is loaded by the standard _Windows DLL_ loader, it does not just load the image in memory and the loader will perform at least two additional actions:

- Add the _DLL_in the _PEB_linked list that contains all the _DLL_loaded by a process.
- Create a hash identifying the _DLL_and adding it to another structure called _LdrpHashTable_

During the loading process, the _DLL_loader, calls the _LdrpInsertDataTableEntry_function. This function creates a hash identifying the _DLL_and adds it to the _LdrpHashTable_structure as shown in the following figure:

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/01-Use-of-LdrpHashTable.png)

_Figure 1: use of LdrpHashTable during DLL loading_

This mechanism has been implemented by _Microsoft_to ease and speedup _DLL_search through a read and black binary tree. This structure allows the search of a _DLL_in _O(log(n))_ instead of _O(n)_ with the previous linked list. This mechanism will not be explained here but can be seen in the _DarkLoadLibrary_project in the _FindModuleBaseAddressIndex_function.

Adding the _DLL_in the _PEB_linked list **AND** in the _LdrpHashTable_can be seen as fully registering the _DLL_and makes it known to the process.

Once this link has been established, the _DLL_can be searched, freed, or copied through the _Win32API_.

### Problems with this implementation

When I saw this implementation, I thought that all my problems were solved and started reimplementing it on my side to understand and customize the process.

For a moment it worked well. All the _DLL_ I loaded with worked out of the box and no specific event regarding the loading of an additional _DLL_ were raised by the agent.

The troubles begin when I tried to dynamically load a specific _DLL_: _WinHTTP.dll._

The _DLL_is successfully loaded, and the majority of functions worked well, but one function did not want to work: _WinHTTPOpen_.

This function is used to initialize the environment and prepare the structures that will be used by the other network _API_used to perform an _HTTP_connection. So, without this function, it was not possible to perform any _HTTP_communication through the _WinHTTP API_.

When I called the _WinHTTPOpen_ function, the call failed with the error code _126_. This error code is related to a missing _DLL_which does not make any sense as all the _DLL_were successfully loaded.

## Dive into WinHTTP.DLL madness

### Macroscopic investigation

The error code hinted a problem with a _DLL_that has not been loaded, so my first reflex was to monitor the process using _Procmon_, looking for an imported _DLL_that could have failed to be loaded.

However, even when comparing the _DLL_ loaded with the standard _LoadLibrary_and the ones loaded through the custom loader, no differences could explain the error code _126_.

### Microscopic investigation

For a moment I let this problem aside and continue the development of the agent, but it still bothered me, and I had no idea how I could debug it. Until one day, I took my sanity away, and decided to just decompile the _WinHTTP.DLL_ and debug it step by step until I saw the error code _126_ popping in one of the registers.

#### Finding the initial problem

With the step by step debug, I quickly found that the problem occurred in the _INTERNET\_SESSION\_HANDLE\_OBJECT::SetProxySettings_ function in the _WINHTTP.DLL_ file.

Following the call stack leads me to the following functions:

- _INTERNET\_HANDLE\_BASE::SetProxySettingsWithInterfaceIndex_
- _WxReferenceDll_
- _TakeSingleDllRef_

In the _TakeSingleDllRef_I found the following piece of code:

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/02-Code-TakeSingleDllRef.png)

_Figure 2: TakeSingleDllRef code_

The _126_error code I got when running the _WinHTTPOpen_function is generated by the _GetModuleHandleExA_function.

This function is usually used to retrieve the base address of an already loaded _DLL_by its _DLL_name. However, here, two unusual parameters are given to this API:

- _dwFlags_: _4_instead of _2_
- _dllName_: the address of the current function instead of the name of the _DLL_to search for.

Looking at the _Microsoft_documentation shows that _dwFlags 4_ is named _GET\_MODULE\_HANDLE\_EX\_FLAG\_FROM\_ADDRESS_and thus explains why an address is given instead of a _DLL_name.

Indeed, when this flag is passed to the _GetModuleHandleExA_, the function will not search for the _DLL_base address by its name but will find the _DLL_that contains the given function.

#### Narrow down the problem

The problem comes from the _GetModuleHandleExA_function. This is interesting because during my tests the custom loader worked fine with _GetModuleHandle_(that call _GetModuleHandleEx_under the hood with _dwFlags 2_ instead of _4_).

So, I decompiled the _KERNELBASE.DLL_ to find the difference of implementation when _dwFlags 4_ is passed to _GetModuleHandleEx_.

The callstack shows that _GetModuleHandleEx_called the _BasepGetModuleHandleExW_function.

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/03-BasepGetModuleHandleExW.png)

_Figure 3: BasepGetModuleHandleExW code_

The first part of the _BasepGetModuleHandleExW_function explains the difference of behavior between _GetModuleHandle_and _GetModuleHandleEx_with _dwFlags_ set to _4_.

When the _dwFlags_ is set to _4_, the function uses the _RtlPcToFileHeader_to find the base address of the module related to the function passed as parameters.

A step-by-step debug shows that this function returns the right value for a _DLL_loaded with _LoadLibrary_but always return _0_for a _DLL_loaded with the custom _DLL Loader_.

#### Analysis of RtlPcToFileHeader

If I had to implement a function that, given a specific address, returns the base address of the image containing the function, I would naturally use the _Win32Api VirtualQuery_. So, I did not see why this function could fail.

The _RtlPcToFileHeader_indeed use _VirtualQuery_to get the base address:

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/04-VirtualQuery-in-RtlPcToFileHeader.png)

_Figure 4: use of VirtualQuery inRtlPcToFileHeader_

However, before getting in this execution branch it performs some additional tests :

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/05-Tests-in-RtlPcToFileHeader.png)

_Figure 5: Tests performed in RtlPcToFileHeader_

If the execution flow goes into the _if(!v10)_, the function will return _0_, otherwise, it has a chance to go through the _VirtualQuery_and returns the right base address.

When this function is used on a _DLL_loaded by the custom loader, it always falls in the wrong code path returning _0_.

#### LdrpInvertedFunctionTable

The test performed by the _RtlPcToFileHeader_function is based on an analysis of the _LdrpInvertedFunctionTable_.

This table that can be parsed using the two following structures,

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/06-Parse-inverted-table.png)

_Figure 6: Structure used to parse the inverted table_

seems to be used to handle _SEH_exceptions.

So, it seems that the custom loader fails to register these exceptions. Indeed, using _WinDBG_with the _DLL_ loaded through _LoadLibrary_, it is possible to see that an entry corresponding to the _WINHTTP.DLL_ file has been registered:

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/07-WinDBG-analysis.png)

_Figure 7: Analysis of the inverted table with WinDBG_

The same test with the custom loaded _DLL_shows that no new entry were added to the _LdrpInvertedFunctionTable_.

## Solutions

### The messy one

The root cause of the problem is that when loading the _DLL_, no additional entries are added to the _LdrpInvertedFunctionTable_leading to a hard failure on the _RtlPcToFileHeader_function.

However, the main cause of the problem is that _GetModuleHandleEx_uses _RtlPcToFileHeader_.

While adding a new entry to the _LdrpInvertedFunctionTable_can be a hard problem, hijacking the _GetModuleHandleEx_function when loading the _DLL_is an easy one.

Indeed, during the _DLL_loading process, we have to manually resolve the exported function address, so it is possible to hijack the entry related to _GetModuleHandleExA_.

The following code can be used instead of _GetModuleHandleExA_:

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/08-Custom-GetModuleHandleExA.png)

_Figure 8: custom GetModuleHandleExA code_

This code iterates over the _DLL_registered in the _PEB_linked list, check if the given function is located in the _DLL_and returns the base address of the related _DLL_.

This solution worked for the _WinHTTP.DLL_ but what about other use cases or other functions based on _RtlPcToFileHeader_? We would have to remap them explicitly every time which is not the best way to operate.

### The elegant one

When two things have to work well together, we have to comply with the rules of the part we are integrating to. In this case, the custom loader should implement the feature that adds the different entries in the _LdrpInvertedFunctionTable_.

#### Locate the use of RtlInsertInvertedFunctionTable

The function _RtlInsertInvertedFunctionTable_can be used to add an entry in the _LdrpInvertedFunctionTable_. So, if this is performed by the _Windows DLL_ loader, it should be possible to find a reference of this function in the _LoadLibrary_ callstack.

Indeed, the call to the _RtlInsertInvertedFunctionTable_is found in the _LdrpProcessMappedModule_function:

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/09-RtlInsertInvertedFunctionTable.png)

_Figure 9: use of RtlInsertInvertedFunctionTable during DLL loading_

This function is called with a security cookie generated using the _LdrInitSecurityCookie_function:

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/10-LdrInitSecurityCookie.png)

_Figure 10: Use of LdrInitSecurityCookie_

While the _LdrInitSecurityCookie_is an exported function, the _RtlInsertInvertedFunctionTable_ is not. So, if we want to use this function, there are two choices:

- Using a pattern recognition algorithm to find the function in the NTDLL knowing that the pattern can change between each Windows build version (this technique has been implemented _here_ [\[6\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftn6))
- Redeveloping the function

I’m not a fan of pattern recognition because it is an unreliable technique that must be maintained over each Windows build version.

#### Analysis of the RtlInsertInvertedFunctionTable function

Decompiling the _RtlInsertInvertedFunctionTable_ shows the following code :

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/11-RtlInsertInvertedFunctionTable.png)

_Figure 11: RtlInsertInvertedFunctionTable function_

Among these functions, the only ones exported are the _RtlAcquireSRWLockExclusive_and _RtlReleaseSrwLockExclusive_. However, the other ones are quite simple to implement:

- _RtlCaptureImageExceptionValues_retrieves the image _ExportDirectory_
- _LdrProtectMrData_performs a _VirtualProtect_ on the _.mrdata_ section
- _RtlpInsertInvertedFunctionTableEntry_populates the _RTL\_INVERTED\_FUNCTION\_TABLE\_ENTRY_ and adds the new element to the _RTL\_INVERTED\_FUNCTION\_TABLE LdrpInvertedFunctionTable_.

The only problem now is there is not any exported function that allows the retrieval of the _LdrpInvertedFunctionTable_object.

#### Locate the RtlInsertInvertedFunctionTable

So, against all my principle, some pattern recognition algorithms need to be coded in order to locate the _LdrpInvertedFunctionTable_structure. However, finding this structure will be easier and more reliable than finding some instructions sequences in the whole _NTDLL .text_ section.

Indeed, there are some inputs that can be used to narrow down the lookup and avoid false positive:

- The structure is located in the _.mrdata_
- The _MaxCount_field must be less than _512_
- The _Count_field must be less than max count and more than _0_

`The LdrpInvertedFunctionTable is located in the NTDLL .mrdata. This section is a specific section that is configured with ReadOnly protection as the .rdata. However, this section protection is often changed from ReadOnly to ReadWrite.`

`This section is used to store sensitive structure that can be modified by the OS under specific circumstances (enhance the ReadWrite protection) but must be protected against programmatic error that could write arbitrary data in it (enhance the ReadOnly protection at runtime).`

Then, some conditions on the different entries can be verified to ensure that the address tested represents the _LdrpInvertedFunctionTable_and is not a false positive. For each entry:

- The exception directory address must be contained in the _DLL_image
- The exception directory address must match with the one computed from the _DLL_base image
- The exception directory size must match with the one computed from the _DLL_base image

These conditions do not ensure the unicity of the solution, but I don’t think random garbage in memory could verify all these conditions, especially the last three.

The following function can be used to locate the _LdrpInvertedFunctionTable_:

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/12-LdrpInvertedFunctionTable-Search.png)

_Figure 12: Code looking for LdrpInvertedFunctionTable_

We now have everything we need to implement the _RtlInsertInvertedFunctionTable_.

#### Implement the RtlInsertInvertedFunctionTable

The _RtlInsertInvertedFunctionTable_can be implemented as the following:

- Locate the _LdrpInvertedFunctionTable_as explained before
- Unprotect the _.mrdata_ section from _ReadOnly_to _ReadWrite_using _VirtualProtect_
- Locate the index where the new _DLL_entry must be stored (these entries are sorted by image base address)
- Write the _RTL\_INVERTED\_FUNCTION\_TABLE\_ENTRY_element in the _LdrpInvertedFunctionTable_

![](https://www.riskinsight-wavestone.com/wp-content/uploads/2024/10/13-RtlpInsertInvertedFunctionTableEntry-Implementation.png)

_Figure 13:  RtlpInsertInvertedFunctionTableEntry implementation_

This code can be added to the _DarkLoadLibrary_ [\[7\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftn7) project to get a fully functional _DLL_ Loader.

## Conclusion

When developing a custom _C2_, the most difficult part is not getting something functional. This is mainly basic development. The most difficult and interesting part is to get something _OPSEC_.

This part implies a deep understanding of Windows internals in order to understand what _IOC_ will be raised, how it can be bypassed and how this custom part can be adapted to be fully integrated with the native _Windows_ecosystem.

This blogpost does not only show how a specific part of the _Windows DLL_ loader can be reimplemented, but how _IOC_can be hunted, and how the _Windows_internals can be reversed to adapt our work to the ecosystem.

[\[1\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftnref1) [https://otterhacker.github.io/Malware/Reflective DLL injection.html](https://otterhacker.github.io/Malware/Reflective%20DLL%20injection.html)

[\[2\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftnref2) [https://posts.specterops.io/perfect-loader-implementations-7d785f4e1fa](https://posts.specterops.io/perfect-loader-implementations-7d785f4e1fa)

[\[3\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftnref3) [https://otterhacker.github.io/Malware/Reflective DLL injection.html](https://otterhacker.github.io/Malware/Reflective%20DLL%20injection.html)

[\[4\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftnref4) [https://twitter.com/\_batsec\_](https://twitter.com/_batsec_)

[\[5\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftnref5) [https://www.mdsec.co.uk/2021/06/bypassing-image-load-kernel-callbacks/](https://www.mdsec.co.uk/2021/06/bypassing-image-load-kernel-callbacks/)

[\[6\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftnref6) [https://github.com/strivexjun/MemoryModulePP/blob/master/MemoryModulePP.c](https://github.com/strivexjun/MemoryModulePP/blob/master/MemoryModulePP.c)

[\[7\]](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#_ftnref7) [https://github.com/bats3c/DarkLoadLibrary](https://github.com/bats3c/DarkLoadLibrary)

[C2](https://www.riskinsight-wavestone.com/en/tag/c2-en/) [Command and Control](https://www.riskinsight-wavestone.com/en/tag/command-and-control/) [Dll](https://www.riskinsight-wavestone.com/en/tag/dll-en/) [Ethical Hacking](https://www.riskinsight-wavestone.com/en/tag/ethical-hacking-en/) [WinHTTP](https://www.riskinsight-wavestone.com/en/tag/winhttp/)

Prev post [Adopting MLSecOps: the key to reliable and secure AI models](https://www.riskinsight-wavestone.com/en/2024/10/adopting-mlsecops-the-key-to-reliable-and-secure-ai-models/)

Next post [Generative AI applications: risks and mitigations](https://www.riskinsight-wavestone.com/en/2024/11/generative-ai-applications-risks-and-mitigations/)

### On the same topic

[![GenAI Guardrails – Why do you need them & Which one should you use?](https://www.riskinsight-wavestone.com/wp-content/uploads/2025/11/COVER2-300x300.png)](https://www.riskinsight-wavestone.com/en/2026/02/genai-guardrails-why-do-you-need-them-which-one-should-you-use/)

#### [GenAI Guardrails – Why do you need them & Which one should you use?](https://www.riskinsight-wavestone.com/en/2026/02/genai-guardrails-why-do-you-need-them-which-one-should-you-use/)

- 3 minutes ago

[![Cloud Security: Adapting to a new reality](https://www.riskinsight-wavestone.com/wp-content/uploads/2026/01/Cover-300x300.png)](https://www.riskinsight-wavestone.com/en/2026/01/cloud-security-adapting-to-a-new-reality/)

#### [Cloud Security: Adapting to a new reality](https://www.riskinsight-wavestone.com/en/2026/01/cloud-security-adapting-to-a-new-reality/)

- 2 weeks ago

### Leave a Reply [Cancel reply](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/\#respond)

Your email address will not be published.Required fields are marked \*

Comment \*

Name \*

Email \*

Website

Δ

[Back to top](https://www.riskinsight-wavestone.com/en/2024/10/loadlibrary-madness-dynamically-load-winhttp-dll/#)