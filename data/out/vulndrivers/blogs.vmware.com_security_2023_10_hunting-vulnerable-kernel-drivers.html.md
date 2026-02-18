# https://blogs.vmware.com/security/2023/10/hunting-vulnerable-kernel-drivers.html

In information security, even seemingly insignificant issues could pose a significant threat. One notable vector of attack is through device drivers used by legitimate software developers. There are numerous available drivers to support legacy hardware in every industry, some of which are from businesses that have long stopped supporting the device. To continue operations, organizations rely upon these deprecated device drivers.

This creates a unique attack vector, as Microsoft Windows allows loading kernel drivers with signatures whose certificates are expired or revoked. This policy facilitates threat actors to [disable](https://www.virusbulletin.com/conference/vb2022/abstracts/lazarus-byovd-evil-windows-core/) security software functions or [install](https://www.welivesecurity.com/2018/09/27/lojax-first-uefi-rootkit-found-wild-courtesy-sednit-group/) bootkits using known vulnerable drivers. Since the Windows 11 2022 update, the vulnerable drivers are [blocked](https://learn.microsoft.com/en-us/windows/security/threat-protection/windows-defender-application-control/microsoft-recommended-driver-block-rules) by default using [Hypervisor-Protected Code Integrity (HVCI)](https://learn.microsoft.com/en-us/windows-hardware/drivers/bringup/device-guard-and-credential-guard). However, this banned-list approach is only effective if the vulnerable driver is known in advance.

The Carbon Black Threat Analysis Unit (TAU) discovered 34 unique vulnerable drivers (237 file hashes) accepting firmware access. Six allow kernel memory access. All give full control of the devices to non-admin users. By exploiting the vulnerable drivers, an attacker without the system privilege may erase/alter firmware, and/or elevate privileges. As of the time of writing in October 2023, the filenames of the vulnerable drivers have not been made public until now.

In this blog post, TAU will describe how to identify unknown vulnerable drivers. This is a long one so here is a quick table of contents if you want to find a specific section:

1. Previous Research
2. Our Approach
3. Implementation
1. Triage Function
2. Analysis Function
4. Hunting Vulnerable Drivers
1. Triage
2. Analysis
3. Result
4. Exploit Development
5. Reporting
6. Wrap-up
7. Tool and PoCs
8. Customer Protection

## 1\. Previous Research

Previous research such as [ScrewedDrivers](https://github.com/eclypsium/Screwed-Drivers) and [POPKORN](https://dl.acm.org/doi/pdf/10.1145/3564625.3564631) utilized symbolic execution for automating the discovery of vulnerable drivers. As far as TAU researched, symbolic execution (or the specific implementations based on [angr](https://github.com/angr/angr)) fails at an unignorable rate by causing path explosions, false negatives and other unknown errors.

Even if symbolic execution works, we need to verify the result on a disassembler manually before reporting the vulnerability. For example, the previous research implementations do not check if the output buffer of the IOCTL request contains the result value in read primitives. In this context, a primitive refers to a basic operation supported by the operating system. Specifically, a read primitive reads data from a driver’s internal buffer, though normally the results would be validated. Another example is that the constraint of the input buffer is sometimes too chaotic to understand. In both cases, there is no way to avoid manual analysis.

Additionally, previous research focused primarily on [Windows Driver Model (WDM)](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-wdm) drivers. [Windows Driver Framework (WDF)](https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/) drivers, whose code and data structures are different by versions and compiler settings, have been unexplored sufficiently. Even if code handling WDF drivers is newly added to the existing implementations, it seemed unlikely to work due to the WDF’s complexity. Therefore, TAU needed to take another approach for discovering both WDM/WDF vulnerable drivers.

## 2\. Our Approach

TAU automated the hunting process of vulnerable WDM/WDF drivers by using an [IDAPython](https://github.com/idapython/src) script. IDAPython is the Python programming language to access APIs of [IDA Pro](https://hex-rays.com/ida-pro/) (hereinafter called IDA), which is a commercial disassembler widely used by reverse engineers. The script implementation is based on the [Hex-Rays Decompiler SDK](https://hex-rays.com/products/decompiler/manual/sdk/index.shtml) and will be detailed in the next section below.

In this research, TAU focuses on drivers that contain firmware access through port I/O and memory mapped I/O for the following reasons.

- Detecting the drivers is almost always the only way for OS-level security software to catch firmware implant installation behavior that modifies SPI flash memory. The SPI flash modification can be done through the low-level APIs and assembly instructions shown in Table 1. It is almost impossible for AV/EDR to detect potential firmware modifications solely on these low-level activities. Once a firmware implant is installed, it can also [disable](https://cfp.recon.cx/2022/talk/RS9CWJ/) firmware scanners used by security vendors.
- The drivers handling such low-level I/O often contain other vulnerabilities like virtual memory access in kernel space (a.k.a. data-only attack). For example, among the discovered vulnerable drivers, the AMD driver [PDFWKRNL.sys](https://www.virustotal.com/gui/file/0cf84400c09582ee2911a5b1582332c992d1cd29fcf811cb1dc00fcd61757db0) allows arbitrary virtual memory access. Another Intel driver [stdcdrvws64.sys](https://www.virustotal.com/gui/file/70afdc0e11db840d5367afe53c35d9642c1cf616c7832ab283781d085988e505) did not provide the read/write primitives directly, but attackers can obtain the same effect by combining memory mapped I/O and the [MmGetPhysicalAddress](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-mmgetphysicaladdress) API through the multiple IOCTL requests.

|     |     |     |
| --- | --- | --- |
|  | **user space** | **kernel space** |
| **APIs** | [DeviceIoControl](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-deviceiocontrol) | **[MmMapIoSpace](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmmapiospace)/ [MmMapIoSpaceEx](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmmapiospaceex) (memory mapped I/O)** |
| **Instructions** | **–** | **IN/OUT (port I/O)** |

_Table 1: Indicators modifying a SPI flash memory_

## 3\. Implementation

The IDAPython script has two functions: triage and analysis. The triage function robustly detects potentially vulnerable drivers from large sets of samples in [IDA batch mode](https://hex-rays.com/blog/igor-tip-of-the-week-08-batch-mode-under-the-hood/) (command-line interface) execution. After the triage, we need to confirm that the detected drivers are truly vulnerable on IDA GUI. The analysis function substantially assists the tedious manual validation.

### 3.1. Triage Function

The triage function identifies IOCTL handlers then finds execution paths from the handlers to the target APIs/instructions. As shown in Table 1 already, the targets are memory-mapped I/O APIs and port I/O assembly instructions. Within the IDA GUI, we can easily find an execution path by using “Add node by name” and “Find path” menus in the [proximity view](https://hex-rays.com/products/ida/support/idadoc/1626.shtml). However, IDA does not provide this functionality through its API. Therefore, TAU implemented the path finder.

The IOCTL handler identification method depends on the driver type. In WDM drivers, the triage function code simply detects an assignment to the MajorFunction array member of the [DRIVER\_OBJECT](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_driver_object) structure then applies the function type. On the other hand, the method for WDF drivers requires a multiple-step procedure.

First, the script detects a call instruction of [WdfVersionBind](https://github.com/microsoft/Windows-Driver-Frameworks/blob/3b9780e847cf68d6199dafe0f87650cf1f9c227f/src/framework/shared/inc/private/common/fxldr.h#L398) API then imports a header file including WDF type information provided by [kmdf\_re](https://github.com/IOActive/kmdf_re) as IDA itself does not support the information. Unlike WDM, WDF APIs are basically called through a function table defined as [WDFFUNCTIONS](https://github.com/microsoft/Windows-Driver-Frameworks/blob/3b9780e847cf68d6199dafe0f87650cf1f9c227f/src/framework/kmdf/inc/private/fxdynamics.h#L484C9-L484C9), that is pointed by the member of the third argument’s structure ( [WDF\_BIND\_INFO](https://github.com/microsoft/Windows-Driver-Frameworks/blob/3b9780e847cf68d6199dafe0f87650cf1f9c227f/src/framework/shared/inc/private/common/fxldr.h#L91).FuncTable). Next, the script tracks cross-references to [WdfIoQueueCreate](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfio/nf-wdfio-wdfioqueuecreate) API in the table. If a function address is assigned to the member of the second argument’s structure ( [WDF\_IO\_QUEUE\_CONFIG](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfio/ns-wdfio-_wdf_io_queue_config).EvtIoDeviceControl), that must be the WDF IOCTL handler.

While this approach is straightforward, the devil is in the details. As shown in the examples of Figure 1 and 2, sometimes WDF\_BIND\_INFO.FuncTable points the pointer to WDFFUNCTIONS (PWDFFUNCTIONS), and sometimes it points WDFFUNCTIONS directly. TAU found that it depends on the WDF version (WDF\_BIND\_INFO.Version). Specifically, version 1.15.0 and later is true of the former. Version 1.13.0 and below is applicable to the latter.

[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/Figure-1.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/Figure-1.png)_Figure 1: FuncTable pointing the pointer to WDFFUNCTIONS (PWDFFUNCTIONS)_

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/Figure-2.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/Figure-2.png) Figure 2: FuncTable directly pointing WDFFUNCTIONS_

Even in the old WDF versions, the script had to consider the variations of how to call WDF APIs. For instance, one driver calls WDFFUNCTIONS.WdfIoQueueCreate directly (Figure 3), and another calculates the offset from WDFFUNCTIONS to call the API (Figure 4). We need to track the cross-references from the head of the table in the latter case.

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/Figure-3.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/Figure-3.png) Figure 3: Direct call of WDFFUNCTIONS.WdfIoQueueCreate_

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-4.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-4.png) Figure 4: Offset calculation for WdfIoQueueCreate_

Moreover, WDF drivers built with debug information, or some older drivers, create function wrappers when calling WDF APIs. In that case, the script detects the wrappers and sets their function types then traces back assignments to the arguments in the parent functions.

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-5.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-5.png) Figure 5: Function type applied to the WdfIoQueueCreate wrapper_

Thus, WDF code and data structures are different by WDF versions and compiler settings.

### 3.2. Analysis Function

The analysis function fixes union fields in IOCTL-related structures and propagates function argument names/types in subroutines recursively to quickly decide if input/output can be controlled. TAU will describe the automation in both WDM/WDF cases.

In one WDM driver example ( [TdkLib64.sys](https://www.virustotal.com/gui/file/aa0c52cebd64a0115c0e7faf4316a52208f738f66a54b4871bd4162eb83dc41a)), TAU had the following code when starting to analyze the IOCTL handler in IDA pseudocode view (sub\_1203C is the handler).

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-6.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-6.png) Figure 6: Typical WDM IOCTL handler code_

If we manually validate that this sample contain vulnerabilities, we need to:

1. Set [PDRIVER\_DISPATCH](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nc-wdm-driver_dispatch) to the function type of sub\_1203C
2. Fix the union field numbers in the structures ( [IO\_STACK\_LOCATION](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_io_stack_location).Parameters and [IRP](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_irp).AssociatedIrp) for [IRP\_MJ\_DEVICE\_CONTROL](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/irp-mj-device-control) requests
3. Rename local variables and change the types according to the assignments
4. Repeat Step 2 and 3 in the called functions recursively until the execution reaches to the targeted APIs and instructions
5. Check if users can control the input for the APIs and instructions then receive the result

The analysis function automates all steps except Step 5. After running the script, IDA displays the improved code.

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-7.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-7.png) Figure 7: Handler code improved by script execution_

Additionally, the script execution tells us that one of the targeted APIs (MmMapIoSpace) is called in the grandchild routine. By the name propagation, we can judge immediately that the API arguments are controllable and the result data is acquirable, as SystemBuffer is utilized for user data input/output and qmemcpy right after MmMapIoSpace plays a role in arbitrary read/write for the mapped memory.

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-8.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-8.png) Figure 8: Code calling MmMapIoSpace_

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-9.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-9.png) Figure 9: Automatically modified code with script execution log_

The script handles WDF drivers in the same way, but it additionally sets argument names and types of the following WDF APIs handling user data I/O since IDA does not support WDF type information by default.

- [WdfRequestRetrieveInputBuffer](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestretrieveinputbuffer)
- [WdfRequestRetrieveOutputBuffer](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestretrieveoutputbuffer)
- [WdfRequestRetrieveInputWdmMdl](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestretrieveinputwdmmdl)
- [WdfRequestRetrieveOutputWdmMdl](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestretrieveoutputwdmmdl)
- [WdfRequestRetrieveInputMemory](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestretrieveinputmemory)
- [WdfRequestRetrieveOutputMemory](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestretrieveoutputmemory)
- [WdfRequestGetParameters](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestgetparameters)

In one WDF example ( [stdcdrv64.sys](https://www.virustotal.com/gui/file/37022838c4327e2a5805e8479330d8ff6f8cd3495079905e867811906c98ea20)) below, the code modified by the script shows that we can gain full control of the MmMapIoSpace’s arguments.

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-10.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-10.png) Figure 10: WDF code before script execution_

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-11.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-11.png) Figure 11: WDF code after script execution_

It should be noted that the name propagation is not perfect. Renaming local variables uncommonly fails due to the following reasons. In these cases, TAU needed to change the names manually.

- The function argument’s item type is cot\_call when traversing the ctree (e.g., 0x11286 in [SysInfoDriverAMD](https://www.virustotal.com/gui/file/fa8db74ce42f813a68242813ac44dd1de71e8f9ea67cdeac496ff0cdf3722fee)).
- Renaming information looks to be lost as the local variable name is changed (e.g., 0x140003657 in [IoAccess.sys](https://www.virustotal.com/gui/file/b9e0c2a569ab02742fa3a37846310a1d4e46ba2bfd4f80e16f00865fc62690cb)).
- Renaming fails multiple times even if a new name is unique in the function (e.g., 0x11ef1 in [cpuz.sys](https://www.virustotal.com/gui/file/9a523854fe84f15efc1635d7f5d3e71812c45d6a4d2c99c29fdc4b4d9c84954c)).

They are rare cases, and any issue is likely caused by internal changes of the ctrees in IDA. Therefore, TAU hasn’t investigated them any further.

## 4\. Hunting Vulnerable Drivers

In this section, TAU will describe how to collect and narrow down the driver samples then identify the vulnerabilities.

**4.1. Triage**

TAU collected about 18K Windows driver samples by [VirusTotal retrohunts](https://support.virustotal.com/hc/en-us/articles/360001293377-Retrohunt). The [YARA rule](https://github.com/TakahiroHaruyama/VDR/blob/main/yara/hardware_io_wdf.yara) is simple.

|     |
| --- |
| ```<br>import "pe"<br>rule hardware_io_wdf {<br>    meta:<br>        description = "Designed to catch x64 kernel drivers importing a memory-mapped I/O API (MmMapIoSpace)"<br>    strings:<br>        $wdf_api_name = "WdfVersionBind"<br>    condition:<br>        filesize < 1MB and<br>        uint16(0) == 0x5a4d and pe.machine == pe.MACHINE_AMD64 and<br>        (pe.imports("ntoskrnl.exe", "MmMapIoSpace") or pe.imports("ntoskrnl.exe", "MmMapIoSpaceEx")) and<br>        $wdf_api_name and // WDF<br>        //not $wdf_api_name and // WDM<br>        for all signature in pe.signatures:<br>        (<br>            not signature.subject contains "WDKTestCert"<br>        )<br>}<br>``` |

Next, TAU de-duplicated the samples based on [imphash](https://www.mandiant.com/resources/blog/tracking-malware-import-hashing) then executed the IDAPython script for the imphash-unique samples in batch mode. The extracted samples were about 300 WDM drivers and 50 WDF. Among them, TAU excluded drivers with the following conditions.

- Already-known vulnerable drivers (source: [CVE List](https://cve.mitre.org/cve/search_cve_list.html), [MS block rules](https://learn.microsoft.com/en-us/windows/security/threat-protection/windows-defender-application-control/microsoft-recommended-driver-block-rules), [loldrivers.io](https://www.loldrivers.io/), [popkorn-artifact](https://github.com/ucsb-seclab/popkorn-artifact/tree/main/evaluation), etc.)
- Drivers whose signature caused verification errors
- Old version of the same drivers validated by [bindiff wrapper](https://github.com/TakahiroHaruyama/ida_haru/tree/master/bindiff)
- Drivers setting their device’s access control
  - In source code: [IoCreateDeviceSecure (WdmlibIoCreateDeviceSecure)](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdmsec/nf-wdmsec-wdmlibiocreatedevicesecure) and [WdfControlDeviceInitAllocate](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfcontrol/nf-wdfcontrol-wdfcontroldeviceinitallocate)
  - In configuration file: [INF AddReg directive](https://github.com/MicrosoftDocs/windows-driver-docs/blob/staging/windows-driver-docs-pr/install/inf-addreg-directive.md)
  - By other minor methods

The device access control is normally set using [Security Descriptor Definition Language (SDDL)](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/sddl-for-device-objects?redirectedfrom=MSDN) strings defined in either source code or configuration file. For instance, the following WDM/WDF drivers set access control by calling APIs in code. The SDDL string “D:P(A;;GA;;;SY)(A;;GA;;;BA)” shows that users except kernel/system/administrator are unable to access the devices.

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-12.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-12.png) Figure 12: Access control using WdmlibIoCreateDeviceSecure_

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-13.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-13.png) Figure 13: Access control using WdfControlDeviceInitAllocate_

TAU also found that some WDF drivers (e.g. [WDTKernel.sys](https://www.virustotal.com/gui/file/98090bbd36594420231959a5df700330147d5870634b59467a135666fe0d2898/detection) and [H2OFFT64.sys](https://www.virustotal.com/gui/file/7c80c7218884e8b5c660c56cf7bfed580c02d0df6b97807097d6cd2f1f9fc9a1/details)) set access control in their INF files like an example below.

|     |
| --- |
| \[WDTInstall.AddReg\]<br>HKR,,DeviceCharacteristics,0x10001,0x0100         ; Use same security checks on relative opens<br>HKR,,Security,,”D:P(A;;GA;;;BA)(A;;GA;;;SY)”      ; Allow generic-all access to Built-in administrators and Local system |

Those drivers are not vulnerable in terms of access control, though privileged attackers can still abuse them as the Bring Your Own Vulnerable Driver (BYOVD) techniques by loading and exploiting the drivers for their purposes like disabling security software.

Other minor methods for device access control are further detailed in the next section.

### 4.2. Analysis

After the triage, TAU analyzed the extracted samples on IDA to verify the vulnerabilities. Thanks to the script’s analysis function explained in the previous section, the validation was basically straightforward, but TAU had to take care of specific issues caused by the drivers. TAU introduces two examples.

[cpuz.sys](https://www.virustotal.com/gui/file/8bbf26cb4d7104031f0633fd2f6a8fda4af99688776fc9a81d6cb5970ed69193) implemented its own device access control method. The driver code checks if processes trying to open the device have the specified privilege (SE\_LOAD\_DRIVER\_PRIVILEGE).If not, the driver returns an error whose status is STATUS\_ACCESS\_DENIED. Even administrators do not have the privilege unless the user-mode process requests it programmatically. Hence, TAU excluded the driver from the list of the discovered vulnerable ones.

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-14.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-14.png) Figure 14: SE\_LOAD\_DRIVER\_PRIVILEGE check by cpuz.sys_

The next unique method was embedded in [TdkLib64.sys](https://www.virustotal.com/gui/file/aa0c52cebd64a0115c0e7faf4316a52208f738f66a54b4871bd4162eb83dc41a). The driver decodes the IOCTL request data using the unique byte map table and validates the header values. After the actual IOCTL handler is executed, the result is also encoded by the table. In this case, non-privileged users can send the IOCTL requests if the data format is correct. Therefore, TAU concluded that this driver was still vulnerable.

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-15.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-15.png) Figure 15: IOCTL data decoding in TdkLib64.sys_

As seen above, we need to confirm manually that the drivers triaged by the batch execution are truly exploitable, so it’s difficult to completely automate the vulnerability discovery. That’s why the script’s analysis function is handy in the manual validation work.

### 4.3. Result

Finally, TAU discovered 34 vulnerable drivers (30 WDM, 4 WDF) with firmware access, including ones made by major chip/BIOS/PC makers. This is the number based on the unique filenames. Practically, there are 237 file hashes in the wild. All discovered drivers give full control of the devices to non-admin users. TAU could load them all on HVCI-enabled Windows 11 except five drivers.

|     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- |
| Filename | Number of Hashes | Type | Signature Status (when discovered) | Other R/W Vulnerabilities | PoC | Note |
| [stdcdrv64.sys](https://www.virustotal.com/gui/file/37022838c4327e2a5805e8479330d8ff6f8cd3495079905e867811906c98ea20) | 1 | WDF | Valid | MSR/CR | Firmware erase | – |
| [IoAccess.sys](https://www.virustotal.com/gui/file/b78eb7f12ba718183313cf336655996756411b7dcc8648157aaa4c891ca9dbee) | [2](https://www.virustotal.com/gui/collection/3439af668dafcbbc9db76e303e8d0ffdea9ad2ae6e4d2a370fff3b6ff154ce71) | WDF | Expired | – | Firmware erase | – |
| [GEDevDrv.SYS](https://www.virustotal.com/gui/file/a369942ce8d4b70ebf664981e12c736ec980dbe5a74585dd826553c4723b1bce) | [4](https://www.virustotal.com/gui/collection/8d8ba3c866157a991585c26135f654c5e6d04770a36f1082f9b2c90490b7a54d) | WDF | Expired | – | – | – |
| [GtcKmdfBs.sys](https://www.virustotal.com/gui/file/edbb23e74562e98b849e5d0eefde3af056ec6e272802a04b61bebd12395754e5) | [5](https://www.virustotal.com/gui/collection/5a5cbe046cfbdc2c1fd16a878149bfd71e3b185b01eb95a55d28436ffa468adb) | WDF | Expired | MSR | – | – |
| [PDFWKRNL.sys](https://www.virustotal.com/gui/file/0cf84400c09582ee2911a5b1582332c992d1cd29fcf811cb1dc00fcd61757db0) | [3](https://www.virustotal.com/gui/collection/2abeb862de297ec3d88a084b7b475a9564e1a740eef9ab1327a880dcfa2b5297) | WDM | Valid | Virtual memory | Firmware erase, EoP | CVE-2023-20598 |
| [TdkLib64.sys](https://www.virustotal.com/gui/file/aa0c52cebd64a0115c0e7faf4316a52208f738f66a54b4871bd4162eb83dc41a) | [18](https://www.virustotal.com/gui/collection/8ea54f140d1780d5f9c8e98bc28b7d8242ed53cbb1056609cba667814291c04c) | WDM | Valid | MSR | Firmware erase | CVE-2023-35841,<br>unique buffer encoding |
| [phymem\_ext64.sys](https://www.virustotal.com/gui/file/fc3e8554602c476e2edfa92ba4f6fb2e5ba0db433b9fbd7d8be1036e454d2584) | [4](https://www.virustotal.com/gui/collection/0f96a8db9e6b23144c507e867a11a178f70db6836667ad10a48115677df778bf) | WDM | Valid | Registry | Firmware erase | Loading failure on HVCI-enabled Win11 |
| [rtif.sys](https://www.virustotal.com/gui/file/9399f35b90f09b41f9eeda55c8e37f6d1cb22de6e224e54567d1f0865a718727) | [7](https://www.virustotal.com/gui/collection/9f46313de9fae7c213015ef0423c5af3ff65bbf79c49b05708daa0fe921a2e85) | WDM | Expired | – | – | KeBugCheckEx |
| [cg6kwin2k.sys](https://www.virustotal.com/gui/file/223f61c3f443c5047d1aeb905b0551005a426f084b7a50384905e7e4ecb761a1) | 1 | WDM | Valid | – | Firmware erase | – |
| [RadHwMgr.sys](https://www.virustotal.com/gui/file/df96d844b967d404e58a12fc57487abc24cd3bd1f8417acfe1ce1ee4a0b0b858) | [6](https://www.virustotal.com/gui/collection/f4f83efbb5e49d9a67fc60c5ea47601b104173956f168501592c16b89606632c) | WDM | Valid | Virtual memory, registry | – | Error in device creation |
| [FPCIE2COM.sys](https://www.virustotal.com/gui/file/ebf0e56a1941e3a6583aab4a735f1b04d4750228c18666925945ed9d7c9007e1) | [5](https://www.virustotal.com/gui/collection/75bb554448d400b060196ca8822b38b6ba0975cca6f8bb3a0eab3e38d7894354) | WDM | Valid | – | – | – |
| [ecsiodriverx64.sys](https://www.virustotal.com/gui/file/7de1ce434f957df7bbdf6578dd0bf06ed1269f3cc182802d5c499f5570a85b3a) | [2](https://www.virustotal.com/gui/collection/edde41338e1c69fd930fd70283bcf5e8fd391b979c3dbcea92186fde3053fa49) | WDM | Expired | MSR | – | – |
| [sysconp.sys](https://www.virustotal.com/gui/file/dba8db472e51edd59f0bbaf4e09df71613d4dd26fd05f14a9bc7e3fc217a78aa) | [2](https://www.virustotal.com/gui/collection/6a7ca92dc0d97566df62e21b43cba4e986020f50528ac80b7497e1de69a1cc30) | WDM | Expired | MSR | – | – |
| [ngiodriver.sys](https://www.virustotal.com/gui/file/42b31b850894bf917372ff50fbe1aff3990331e8bd03840d75e29dcc1026c180) | [12](https://www.virustotal.com/gui/collection/dd7712ccb2dbe4b0daf219c22ea2665d7a2966299e15e8f6c052788e8efba7ca) | WDM | Expired | MSR (read-only) | – | – |
| [avalueio.sys](https://www.virustotal.com/gui/file/a5a4a3c3d3d5a79f3ed703fc56d45011c21f9913001fcbcc43a3f7572cff44ec) | [2](https://www.virustotal.com/gui/collection/69da6641b5b2720ed621f51258a12806dbafa5af76f788d56b8814ad86f7d315) | WDM | Expired | – | – | – |
| [tdeio64.sys](https://www.virustotal.com/gui/file/1076504a145810dfe331324007569b95d0310ac1e08951077ac3baf668b2a486) | [2](https://www.virustotal.com/gui/collection/84f4dc416d466969c8877e7b22acb1778dd1eca590d68031f3876fa136f3069c) | WDM | Expired | – | – | – |
| [WiRwaDrv.sys](https://www.virustotal.com/gui/file/d8fc8e3a1348393c5d7c3a84bcbae383d85a4721a751ad7afac5428e5e579b4e) | 1 | WDM | Expired | – | – | Loading failure on HVCI-enabled Win11 |
| [CP2X72C.SYS](https://www.virustotal.com/gui/file/4b4ea21da21a1167c00b903c05a4e3af6c514ea3dfe0b5f371f6a06305e1d27f) | [5](https://www.virustotal.com/gui/collection/4bd7289bd690d7dc469a07087a372d1395520b2b7bd8f8dc605a64c2ec63c26e) | WDM | Expired | – | – | Loading failure on HVCI-enabled Win11 |
| [SMARTEIO64.SYS](https://www.virustotal.com/gui/file/3c95ebf3f1a87f67d2861dbd1c85dc26c118610af0c9fbf4180428e653ac3e50) | 1 | WDM | Expired | – | – | – |
| [AODDriver.sys](https://www.virustotal.com/gui/file/478bcb750017cb6541f3dd0d08a47370f3c92eec998bc3825b5d8e08ee831b70) | [9](https://www.virustotal.com/gui/collection/9b1f9684f85b4893cd072cf91d12b0eaa524e4b77c45375c71f42440f09154c3) | WDM | Certificate revoked | MSR | – | – |
| [dellbios.sys](https://www.virustotal.com/gui/file/3678ba63d62efd3b706d1b661d631ded801485c08b5eb9a3ef38380c6cff319a) | [11](https://www.virustotal.com/gui/collection/558aaa0ac4f24e4f059cf2a4834d97f825dedeb4d4960034e9feeae51353ab08) | WDM | Certificate revoked | – | – | – |
| [stdcdrvws64.sys](https://www.virustotal.com/gui/file/70afdc0e11db840d5367afe53c35d9642c1cf616c7832ab283781d085988e505) | 1 | WDM | Certificate revoked | Virtual memory, MSR/CR | EoP | Old WDM version of stdcdrv64.sys |
| [sepdrv3\_1.sys](https://www.virustotal.com/gui/file/b2bc7514201727d773c09a1cfcfae793fcdbad98024251ccb510df0c269b04e6) | 1 | WDM | Certificate revoked | – | – | – |
| [kerneld.amd64](https://www.virustotal.com/gui/file/125e4475a5437634cab529da9ea2ef0f4f65f89fb25a06349d731f283c27d9fe) | [36](https://www.virustotal.com/gui/collection/e6351d300e9cead71cf2088f4b49d977f71c1d4170b9430a9695b0b24fc8ed91) | WDM | Certificate revoked | – | – | – |
| [hwdetectng.sys](https://www.virustotal.com/gui/file/2f8b68de1e541093f2d4525a0d02f36d361cd69ee8b1db18e6dd064af3856f4f) | [3](https://www.virustotal.com/gui/collection/b9faa620c3c24b25bd0e2e7d4971b6190ca660c02d6158d2bea94d39dc2d85c2) | WDM | Certificate revoked | MSR | – | – |
| [VdBSv64.sys](https://www.virustotal.com/gui/file/91afa3de4b70ee26a4be68587d58b154c7b32b50b504ff0dc0babc4eb56578f4) | 1 | WDM | Certificate revoked | MSR | – | – |
| [nvoclock.sys](https://www.virustotal.com/gui/file/642857fc8d737e92db8771e46e8638a37d9743928c959ed056c15427c6197a54) | [25](https://www.virustotal.com/gui/collection/e4e0a8caba752db80e436350b23eb49edc02e22d895d41950cbae8b38bfdbd69) | WDM | Certificate revoked | Virtual memory | – | – |
| [rtport.sys](https://www.virustotal.com/gui/file/71423a66165782efb4db7be6ce48ddb463d9f65fd0f266d333a6558791d158e5) | [8](https://www.virustotal.com/gui/collection/94aa1c6bc3d53dc7a05a1e43c50ad7ce3c7fc936eadeec3a4a94cc60ec99d282) | WDM | Certificate revoked | Virtual memory | EoP | – |
| [ComputerZ.Sys](https://www.virustotal.com/gui/file/07d0090c76155318e78a676e2f8af1500c20aaa1e84f047c674d5f990f5a09c8) | [50](https://www.virustotal.com/gui/collection/b8add3e957d1058b0365128fcb932024ee8d3cff9507c3655768772b9f30ba8a) | WDM | Certificate revoked | MSR | – | – |
| [SBIOSIO64.sys](https://www.virustotal.com/gui/file/39336e2ce105901ab65021d6fdc3932d3d6aab665fe4bd55aa1aa66eb0de32f0) | [4](https://www.virustotal.com/gui/collection/2720a1c436df19b4cbbaaae4179e6a8db9b4ae495f7e00732d7d3ea247af9e91) | WDM | Certificate revoked | – | – | – |
| [SysInfoDetectorX64.sys](https://www.virustotal.com/gui/file/45e5977b8d5baec776eb2e62a84981a8e46f6ce17947c9a76fa1f955dc547271) | 1 | WDM | Expired | MSR (read-only) | – | – |
| [nvaudio.sys](https://www.virustotal.com/gui/file/b0dcdbdc62949c981c4fc04ccea64be008676d23506fc05637d9686151a4b77f) | 1 | WDM | Certificate revoked | Virtual memory, MSR/CR | – | Buffer encryption, 72% code similarity with nvoclock.sys |
| [FH-EtherCAT\_DIO.sys](https://www.virustotal.com/gui/file/ae71f40f06edda422efcd16f3a48f5b795b34dd6d9bb19c9c8f2e083f0850eb7) | [2](https://www.virustotal.com/gui/collection/5cb7c8ba095ce384b5e8657623daa989b8b6f0eca35a5dc77a065d7483e43614) | WDM | Expired | MSR | – | Loading failure on HVCI-enabled Win11 |
| [atlAccess.sys](https://www.virustotal.com/gui/file/0b57569aaa0f4789d9642dd2189b0a82466b80ad32ff35f88127210ed105fe57) | 1 | WDM | Expired | – | – | Loading failure on HVCI-enabled Win11 |

_Table 2: Research result_

As shown in Table 2, TAU additionally found other arbitrary read/write vulnerabilities outside of firmware access (arbitrary port I/O and memory mapped I/O). For more details of each vulnerability, check the [previous blog post](https://blogs.vmware.com/security/2023/04/bring-your-own-backdoor-how-vulnerable-drivers-let-hackers-in.html) written by TAU and the [ESET’s write-up](https://www.welivesecurity.com/2022/01/11/signed-kernel-drivers-unguarded-gateway-windows-core/).

- Six drivers allow kernel memory access (arbitrary virtual memory R/W). This can be exploited for elevation of OS privilege (EoP) or defeating security software functions like AV/EDR.
- Twelve drivers accept model-specific register (MSR) access. Attackers can patch system call entry addresses or disable KASLR if the process integrity level is low.
- Three drivers provide control register (CR) access like disabling SMEP/SMAP.
- Two drivers offer registry key/value access.

### 4.4. Exploit Development

TAU developed firmware erasing and EoP PoCs for a subset of the drivers.

The firmware erasing PoC (rwf.py, available on GitHub) targets the Intel Apollo SoC platforms by exploiting the six drivers marked as vulnerable in Table 2. This PoC takes one argument for the target device then erases the first 4KB data of firmware in the SPI flash memory. The PoC behavior is the same as the CHIPSEC framework’s “ [spi erase](https://github.com/chipsec/chipsec/blob/2358adfd514103e48fd3b95d77086752feb4c33e/chipsec/utilcmd/spi_cmd.py#L139)” command as described below, but it exploits port I/O and memory mapped I/O provided by each vulnerable driver with unique IOCTL request data structures, instead of the CHIPSEC driver.

1. Get the SPI Base Address Register (SPIBAR) value through arbitrary port I/O
2. Access SPI registers using the SPIBAR through arbitrary memory mapped I/O
   - Clear FDONE/FCERR/AEL bits in the Hardware Sequencing Flash Status (HSFS) register for initialization
   - Set the address value (0) to the Flash Address (FADDR) register
   - Set FCYCLE and FGO bits in HSFS to start the SPI erase command
   - Check FDONE & SCIP bits in HSFS to make sure that the command execution is finished

As shown in Figure 16, four drivers require to send multiple IOCTL requests for the memory mapped I/O operations above. On the other hand, two drivers (IoAccess.sys and phymem\_ext64.sys) return a user-mode address pointer mapping the SPI registers in the output buffer, so a single IOCTL request is enough to erase firmware.

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-16.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-16.png) Figure 16: Firmware erase by exploiting Intel driver (stdcdrv64.sys)_

It should be noted that the tested platform enabled the SPI flash protection settings like BIOS Lock Enable (BLE) and SMM BIOS Write Protection (SMM\_BWP) described in the [Eclypsium’s blog](https://eclypsium.com/research/protecting-system-firmware-storage/). Normally firmware modification by the SPI write command on modern systems requires another firmware-level [vulnerability](https://www.welivesecurity.com/2022/04/19/when-secure-isnt-secure-uefi-vulnerabilities-lenovo-consumer-laptops/)/ [flaw](https://binarly.io/posts/leaked_msi_source_code_with_intel_oem_keys_how_does_this_affect_industry_wide_software_supply_chain/) defeating the protection settings and Intel Boot Guard.

[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/Hunting_Vulnerable_kernel_Drivers_Fig_17.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/Hunting_Vulnerable_kernel_Drivers_Fig_17.png)

_Figure 17: BIOS write protection settings of the tested hardware_

However, the settings were not effective in preventing the erase command. After erasing, the system became unbootable since the firmware’s header was eliminated as displayed in Figure 18.

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-18.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-18.png) Figure 18: firmware headers before/after erasing_

The EoP PoCs (eop\_\*.py) were implemented for the three drivers included in Table 2. They are classic token stealing exploits that read a token value of the System process in the [\_EPROCESS](https://www.vergiliusproject.com/kernels/x64/Windows%2011/22H2%20(2022%20Update)/_EPROCESS) structure and write the value into the field of the Python exploit process. In Figure 19 below, a non-privileged user could run cmd.exe with system integrity level by the exploit on HVCI-enabled Windows 11.

_[![](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-19.png)](https://blogs.vmware.com/wp-content/uploads/sites/26/2023/10/figure-19.png) Figure 19: EoP exploit for AMD driver (PDFWKRNL.sys) on HVCI-enabled Windows 11_

Two drivers allow arbitrary virtual memory access directly for EoP. Another driver (stdcdrvws64.sys) demands two IOCTL requests per access to translate a virtual address to a physical one by MmGetPhysicalAddress then read/write data at the physical address through arbitrary memory mapped I/O.

## 5\. Reporting

In April and May 2023, TAU reported the vulnerabilities to the vendors whose drivers had valid signatures at the time of discovery. Only two vendors fixed the vulnerabilities and the following CVEs were assigned.

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| Driver Name | Vendor | CVE | JVN (Japan Vulnerability Notes) | Vendor Advisory |
| TdkLib64.sys | Phoenix Technologies Ltd. | [CVE-2023-35841](https://www.cve.org/CVERecord?id=CVE-2023-35841) | [JVNVU#93886750](https://jvn.jp/en/vu/JVNVU93886750/index.html) | N/A |
| PDFWKRNL.sys | Advanced Micro Devices, Inc. | [CVE-2023-20598](https://www.cve.org/CVERecord?id=CVE-2023-20598) | [JVNVU#97149791](https://jvn.jp/en/vu/JVNVU97149791/) | [AMD-SB-6009](https://www.amd.com/en/resources/product-security/bulletin/amd-sb-6009.html) |

_Table 3: Fixed vulnerabilities_

TAU appreciates each vendor’s effort to remediate the vulnerabilities. TAU also thanks JPCERT/CC for coordinating the fixes with the vendors patiently.

## 6\. Wrap-up

By implementing the static analysis automation script, TAU discovered 34 unique vulnerable drivers (237 file hashes) that were not recognized previously. WDM drivers are still widely used, but we can also discover and exploit vulnerable WDF drivers in a similar fashion.

While a lot of vulnerable drivers have been reported by researchers, TAU found not only old vulnerable drivers but also new ones with valid signatures. It seems likely that we need more comprehensive approaches in the future than the current banned-list method used by Microsoft. For example, a simple prevention of loading drivers signed by revoked certificates will block about one-third of the vulnerable drivers disclosed in this research.

Finally, note that the typical vendor’s fixes for vulnerable drivers are to just set the device access control, rejecting non-privileged user’s requests. It can prevent EoP, but leaves the BYOVD techniques unresolved as attackers already have administrator privilege to load kernel drivers. Therefore, TAU expects that threat actors will continue to utilize the techniques by exploiting the “not vulnerable” drivers. TAU will continue to monitor this issue.

## 7\. Tool and PoCs

The IDAPython script and PoCs are available [here](https://github.com/TakahiroHaruyama/VDR). The current scope of the APIs/instructions targeted by the script is narrow and only limited to firmware access. However, it is easy to extend the code to cover other attack vectors (e.g. terminating arbitrary processes). TAU hopes that more people in the cybersecurity industry will recognize the vulnerable driver issue by utilizing this tool and hunting zero-day vulnerabilities.

## 8\. Customer Protection

For protecting our customers, the IOCs (Indicators of Compromise) of vulnerable drivers discovered by this research are available in the “Living Off The Land Drivers” watchlist whose information is created from the website [LOLDrivers](https://www.loldrivers.io/). TAU provided the result with the creator Michael Haag. TAU appreciates his contributions to the security community.

The provided IOCs contain not only the vulnerable drivers but also “not vulnerable” ones that TAU identified during the research (e.g., [WDTKernel.sys,](https://www.virustotal.com/gui/file/98090bbd36594420231959a5df700330147d5870634b59467a135666fe0d2898/detection) [H2OFFT64.sys,](https://www.virustotal.com/gui/file/7c80c7218884e8b5c660c56cf7bfed580c02d0df6b97807097d6cd2f1f9fc9a1/details) [the fixed version of TdkLib64.sys](https://www.virustotal.com/gui/file/cbd4f66ae09797fcd1dc943261a526710acc8dd4b24e6f67ed4a1fce8b0ae31c) and so on) as both can be exploited easily for the BYOVD techniques. The number of added hashes was 272 in total.

## Related Articles

[![An iLUMMAnation on LummaStealer](https://blogs.vmware.com/security/wp-content/uploads/sites/26/2022/03/Malware_Featured.png?w=410&h=222&crop=1)](https://blogs.vmware.com/security/2023/10/an-ilummanation-on-lummastealer.html "An iLUMMAnation on LummaStealer")

[Threat Analysis Unit](https://blogs.vmware.com/security/threat-analysis-unit)

## [An iLUMMAnation on LummaStealer](https://blogs.vmware.com/security/2023/10/an-ilummanation-on-lummastealer.html)

[Fae Carlisle](https://blogs.vmware.com/security/author/fcarlisle1), [Bria Beathley](https://blogs.vmware.com/security/author/bbeathley), [Samantha Saltzman](https://blogs.vmware.com/security/author/ssaltzman), [Ad](https://blogs.vmware.com/security/author/agrema)...
Fae Carlisle, Bria Beathley, Samantha Saltzman, Adelin Grema, Alan NgoOctober 18, 202327 min read

[![VMware Carbon Black Emerges as a Leader in Frost & Sullivan’s 2023 XDR Report](https://blogs.vmware.com/security/wp-content/uploads/sites/26/2023/01/300DPIxGettyImages-13362507991.jpg?w=410&h=222&crop=1)](https://blogs.vmware.com/security/2023/09/vmware-carbon-black-emerges-as-a-leader-in-frost-sullivans-2023-xdr-report.html "VMware Carbon Black Emerges as a Leader in Frost & Sullivan’s 2023 XDR Report")

[Endpoint Security](https://blogs.vmware.com/security/endpoint-security)

## [VMware Carbon Black Emerges as a Leader in Frost & Sullivan’s 2023 XDR Report](https://blogs.vmware.com/security/2023/09/vmware-carbon-black-emerges-as-a-leader-in-frost-sullivans-2023-xdr-report.html)

[Pooja Yarabothu](https://blogs.vmware.com/security/author/pyarabothu)September 12, 20236 min read

[![Detecting Secrets in Container Images](https://blogs.vmware.com/security/wp-content/uploads/sites/26/2022/03/Container-Security_Featured.png?w=410&h=222&crop=1)](https://blogs.vmware.com/security/2023/08/detecting-secrets-in-container-images.html "Detecting Secrets in Container Images")

[Modern Apps Security](https://blogs.vmware.com/security/modern-apps-security)

## [Detecting Secrets in Container Images](https://blogs.vmware.com/security/2023/08/detecting-secrets-in-container-images.html)

[Abby Costin](https://blogs.vmware.com/security/author/acostin)August 18, 20235 min read