# https://github.com/jsecurity101/JonMon/wiki/Event-Mapping

[Skip to content](https://github.com/jonny-jhnson/JonMon/wiki/Event-Mapping#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/jonny-jhnson/JonMon/wiki/Event-Mapping) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/jonny-jhnson/JonMon/wiki/Event-Mapping) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/jonny-jhnson/JonMon/wiki/Event-Mapping) to refresh your session.Dismiss alert

{{ message }}

[jonny-jhnson](https://github.com/jonny-jhnson)/ **[JonMon](https://github.com/jonny-jhnson/JonMon)** Public

- [Notifications](https://github.com/login?return_to=%2Fjonny-jhnson%2FJonMon) You must be signed in to change notification settings
- [Fork\\
32](https://github.com/login?return_to=%2Fjonny-jhnson%2FJonMon)
- [Star\\
251](https://github.com/login?return_to=%2Fjonny-jhnson%2FJonMon)


# Event Mapping

[Jump to bottom](https://github.com/jonny-jhnson/JonMon/wiki/Event-Mapping#wiki-pages-box)

Jonathan Johnson edited this page on Jan 27, 2025Jan 27, 2025
·
[2 revisions](https://github.com/jonny-jhnson/JonMon/wiki/Event-Mapping/_history)

| EventId | EventType | Collection Mechanism | Notes |
| --- | --- | --- | --- |
| 1 | ProcessCreation | PsSetCreateProcessNotifyRoutineEx |  |
| 2 | ProcessTerminate | PsSetCreateProcessNotifyRoutine |  |
| 3 | RemoteThreadCreation | PsSetCreateThreadNotifyRoutine |  |
| 4 | ImageLoad | PsSetLoadImageNotifyRoutine | Driver and UM DLL Loads |
| 5 | ProcessAccess | ObRegisterCallbacks.PostOperation.Operation OB\_OPERATION\_HANDLE\_CREATE & OB\_OPERATION\_HANDLE\_DUPLICATE |  |
| 6 | RegistrySaveKey | CmRegisterCallbackEx |  |
| 8 | RegistrySetValue | CmRegisterCallbackEx |  |
| 9 | RegistryKeyCreate | CmRegisterCallbackEx |  |
| 10 | FileCreate | FltRegisterCallback - IRP\_MJ\_CREATE |  |
| 11 | NamedPipeCreate | FltRegisterCallback - IRP\_MJ\_CREATE\_NAMED\_PIPE |  |
| 12 | NamedPipeConnect/Open | FltRegisterCallback - IRP\_MJ\_CREATE\_NAMED\_PIPE |  |
| 13 | MailslotCreate | FltRegisterCallback - IRP\_MJ\_CREATE\_MAILSLOT |  |
| 14 | MailslotConnect/Open | FltRegisterCallback - IRP\_MJ\_CREATE |  |
| 15 | RemoteFileConnection | FltRegisterCallback - IRP\_MJ\_CREATE |  |
| 16 | DotNetLoad | ETW - Microsoft-Windows-DotNETRuntime |  |
| 17 | WMIPermanantSubscription | Microsoft-Windows-WMI-Activity |  |
| 18 | RPCClientCall | ETW - Microsoft-Windows-RPC | RPC events are collected around the interfaces specified in the [MSRPC-to-ATTACK](https://github.com/jsecurity101/MSRPC-to-ATTACK) project |
| 19 | RPCServerCall | ETW - Microsoft-Windows-RPC | RPC events are collected around the interfaces specified in the [MSRPC-to-ATTACK](https://github.com/jsecurity101/MSRPC-to-ATTACK) project |
| 20 | DPAPI - CryptUnprotectData | ETW - Microsoft-Windows-Crypto-DPAPI |  |
| 21 | NetworkTCPEvent | ETW - Microsoft-Windows-Kernel-Network |  |
| 22 | AMSI | ETW - Microsoft-Antimalware-Scan-Interface |  |
| 23 | RemoteReadProcessMemory | ETW - Microsoft-Windows-Threat-Intelligence |  |
| 24 | RemoteWriteProcessMemory | ETW - Microsoft-Windows-Threat-Intelligence |  |
| 25 | RemoteVirtualAllocation | ETW - Microsoft-Windows-Threat-Intelligence |  |
| 26 | QueueUserAPC | ETW - Microsoft-Windows-Threat-Intelligence |  |
| 27 | TokenImpersonation | UM DLL Extension - Thread Query | Periodically queries the system for threads that are executing as SYSTEM where the process is HIGH IL |

### Clone this wiki locally

You can’t perform that action at this time.