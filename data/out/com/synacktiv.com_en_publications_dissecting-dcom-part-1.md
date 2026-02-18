# https://www.synacktiv.com/en/publications/dissecting-dcom-part-1

[Skip to main content](https://www.synacktiv.com/en/publications/dissecting-dcom-part-1#main-content)

[Search](https://www.synacktiv.com/search)

Switch Language

EnglishToggle Dropdown

- English
- [French](https://www.synacktiv.com/publications/dissecting-dcom-partie-1)

- [RSS](https://www.synacktiv.com/en/feed/lastblog.xml)
- [Github](https://github.com/Synacktiv)
- [Twitter](https://twitter.com/synacktiv)
- [Linkedin](https://fr.linkedin.com/company/synacktiv)

[![Home](https://www.synacktiv.com/sites/default/files/logo_synacktiv_blanc.webp)](https://www.synacktiv.com/en "Home")

- [RSS](https://www.synacktiv.com/en/feed/lastblog.xml)
- [Github](https://github.com/Synacktiv)
- [Twitter](https://twitter.com/synacktiv)
- [Linkedin](https://fr.linkedin.com/company/synacktiv)

# Dissecting DCOM part 1

Written by
Kevin Tellier \- 15/09/2025 - in
Pentest
\- [Download](https://www.synacktiv.com/en/publications/dissecting-dcom-part-1#)

This is the first article on the "Dissecting DCOM" series. This article aims at giving an introduction to the base principles of COM and DCOM protocols as well as a detailed network analysis of DCOM.

No previous knowledge is required. The following articles will dig into the authorization and enumeration mechanisms on COM/DCOM. This articles series aims to regroup known knowledge about DCOM in order to allow one to have the necessary tools for vulnerability research on DCOM.

## Table of Contents

- [Introduction](https://www.synacktiv.com/en/publications/dissecting-dcom-part-1#introduction)
- [The Origins of DCOM](https://www.synacktiv.com/en/publications/dissecting-dcom-part-1#the-origins-of-dcom)
- [Some definitions](https://www.synacktiv.com/en/publications/dissecting-dcom-part-1#some-definitions)
- [Enumeration](https://www.synacktiv.com/en/publications/dissecting-dcom-part-1#enumeration)
- [Instantiation](https://www.synacktiv.com/en/publications/dissecting-dcom-part-1#instantiation)
- [Interfaces](https://www.synacktiv.com/en/publications/dissecting-dcom-part-1#interfaces)
- [Component types](https://www.synacktiv.com/en/publications/dissecting-dcom-part-1#component-types)
- [Conclusion](https://www.synacktiv.com/en/publications/dissecting-dcom-part-1#conclusion)
- [References](https://www.synacktiv.com/en/publications/dissecting-dcom-part-1#references)

Looking to improve your skills? Discover our **trainings** sessions! [Learn more](https://www.synacktiv.com/en/offers/trainings).


## Introduction

COM and DCOM are concepts that appear in various contexts, ranging from privilege escalation techniques in Windows to industrial protocols like OPC. Although fundamental to Windows, COM remains an obscure and enigmatic technology for many. Deeply embedded in Windows and seamlessly integrated into the system, it regularly plays a role in common operations.

When I began this research, my knowledge of COM and DCOM was fairly minimal. While Microsoft does provide documentation, crucial details—such as the internal workings of object activation—remained unclear or incomplete.

This article aims to provide a solid foundation on COM and DCOM before delving into the subtleties of the activation process. Our goal is to demystify the mechanisms that enable method calls across remote machines.

But before that, let’s take a brief historical step back to understand how this technology has evolved.

## The Origins of DCOM

COM and DCOM trace their origins to the early iterations of Windows, emerging alongside the resizable windows feature in Windows 2.0.

One of the earliest applications of interprocess communication in Windows was the interprocess clipboard, a fundamental yet effective feature enabling interaction between processes from a user experience standpoint. Introduced in 1987, **Dynamic Data Exchange (DDE)** facilitated this process, later partially supplanted by **Object Linking and Embedding (OLE) 1.0** in 1990. Remarkably, OLE remains around decades later.

As software demands grew, more flexible mechanisms were required to support complex features, such as embedding an Excel spreadsheet within a Word document while maintaining editability.

![excel](https://www.synacktiv.com/sites/default/files/inline-images/pasted-image-20250221173431.webp)

The need for reusable, loosely coupled components led to the adoption of the **Component-Based Development (CBD)** model—a concept that, while often associated with modern software engineering, originated with COM.

COM (Component Object Model) introduced a flexible architecture allowing developers to interact with objects solely through their interfaces, abstracting away the complexities of implementation. This approach laid the groundwork for numerous technologies built on top of COM, including OLE 2.0, ActiveX, DirectX, Windows Shell, Browser Helper Objects, COM+, and, eventually, DCOM.

A pivotal feature of COM is **location transparency**— the ability to interact with an object without knowing its physical location. Whether an object resides within the same thread, process, or even on a remote machine, a user can interact with it using only the provided interface.

With the beta release of Windows 95, which introduced native TCP/IP support, Internet Explorer, and the widespread adoption of the World Wide Web, the necessity for distributed software components grew. The core principles of COM were subsequently extended, giving rise to Distributed COM (DCOM), which enabled communication between software components across networks.

However, distributed communication introduced additional challenges that DCOM sought to address:

- **Marshalling** – The serialization and deserialization of method parameters and return values.
- **Garbage Collection** – Efficient management of object references, ensuring proper cleanup when objects are no longer needed or when errors occur.

Keep these concepts in mind, as they will be explored in greater detail later.

Afterwards, multiple protocols were built on top of DCOM such as:

- Windows Client Certificate Enrollment Protocol (MS-WCCE)
- Component Object Model Plus (COM+) Protocol (MS-COM)
- Disk Management Remote Protocol (MS-DMRP)
- Virtual Disk Service (VDS) Protocol (MS-VDS)
- Windows Management Instrumentation Remote Protocol (MS-WMI)
- Open Platform Communications (OPC, formerly OLE for Process Control)

The last element on the list, OPC is still widely used in Industrial technologies, which is why you get a lot of content related to that subject when you look for information on DCOM.

To summarize, DCOM is essentially COM over the network.

## Some definitions

Before delving deeper, let’s define some key identifiers frequently encountered when working with COM and DCOM:

- **CLSID (Class Identifier)**: A globally unique identifier (GUID) that uniquely identifies a COM class.


  - ex: 49B2791A-B1AE-4C90-9B8E-E860BA07F889
- **ProgID (Programmatic Identifier)**: Friendly name for the COM class

  - ex: MMC20.Application
- **AppID (Application Identifier)**: An identifier that groups multiple related COM classes.

  - ex: 49B2791A-B1AE-4C90-9B8E-E860BA07F889

![definitions](https://www.synacktiv.com/sites/default/files/inline-images/definitions.webp)

## Enumeration

### Registry

Since COM objects are registered in the Windows Registry, they can be easily enumerated using the following command:

```
PS C:\Users\user> reg query "HKCR\CLSID\"
HKEY_CLASSES_ROOT\CLSID\CLSID
HKEY_CLASSES_ROOT\CLSID\{0000002F-0000-0000-C000-000000000046}
HKEY_CLASSES_ROOT\CLSID\{00000300-0000-0000-C000-000000000046}
HKEY_CLASSES_ROOT\CLSID\{00000301-A8F2-4877-BA0A-FD2B6645FB94}
HKEY_CLASSES_ROOT\CLSID\{00000303-0000-0000-C000-000000000046}
[...]
```

Then, for each CLSID, you’ll have multiple keys and values needed by the system to instantiate the class. Indeed, two keys give information related to where the class is implemented. From there you have two possibilities:

- **LocalServer32**: The class is implemented in an executable file
- **InProcServer32**: The class is implemented in a shared library (DLL)

In the same manner of the CLSIDs, ProgIDs and AppIDs can be listed using the following commands:

```
PS C:\Users\user> reg query "HKLM\SOFTWARE\Classes\"
[...]
HKEY_LOCAL_MACHINE\SOFTWARE\Classes\AADJ
HKEY_LOCAL_MACHINE\SOFTWARE\Classes\AADJCSP
HKEY_LOCAL_MACHINE\SOFTWARE\Classes\AboveLockAppLaunchCallback
HKEY_LOCAL_MACHINE\SOFTWARE\Classes\AccClientDocMgr.AccClientDocMgr
[...]
PS C:\Users\user> reg query "HKCR\AppID\"
[...]
HKEY_CLASSES_ROOT\AppID\{00021401-0000-0000-C000-000000000046}
HKEY_CLASSES_ROOT\AppID\{000C101C-0000-0000-C000-000000000046}
HKEY_CLASSES_ROOT\AppID\{0010890e-8789-413c-adbc-48f5b511b3af}
[...]
```

Fortunately, James Forshaw, developed a very convenient tool to enumerate all sort of information on COM: [**OleView.NET**](https://github.com/tyranid/oleviewdotnet).

### OleView.net

![oleviewnet](https://www.synacktiv.com/sites/default/files/inline-images/oleview.net_.webp)

This tool allows you to list CLSIDs, ProgIDs, interfaces, scoped permissions, global permissions, type library definitions, etc. In addition to the enumeration features, you can also instantiate classes and perform many more advanced actions.

OleView.net comes with a Powershell Module, which you can install using:

```
Install-Module OleViewDotNet
```

## Instantiation

Now that we know how to enumerate classes information, we can use this information to instantiate classes.

It’s quite easy to do, as Powershell provides the ability to run .NET code directly by providing different types of identifiers:

- **CLSID**

```
$object = [System.Activator]::CreateInstance([type]::GetTypeFromCLSID("49B2791A-B1AE-4C90-9B8E-E860BA07F889"))
```

- **ProgID**

```
$object = new-object -comobject Shell.Application
$object = [System.Activator]::CreateInstance([type]::GetTypeFromProgID("Shell.Application"))
```

Methods and attributes can then be called directly from the **$object** variable:

```
$object.Document.ActiveView.ExecuteShellCommand("cmd",$null,"/c calc.exe","7")
```

Classes can also be instantiated remotely by specifying an IP address as second parameter:

```
$object = [System.Activator]::CreateInstance([type]::GetTypeFromProgID("Shell.Application","192.168.0.2"))
```

We have seen multiples methods to instantiate classes using Powershell but it can also be done using other binaries such as rundll32 with the CLSID:

```
rundll32.exe C:\Windows\System32\shell32.dll,SHCreateLocalServerRunDll {9aa46009-3ce0-458a-a354-715610a075e6}
rundll32.exe -sta {9aa46009-3ce0-458a-a354-715610a075e6}
```

Next, scheduled tasks offers another quite interesting persistence method. Here is the format to use for the scheduled task XML file:

```
<Actions Context="LocalSystem">
   <ComHandler>
     <ClassId>{E4544ABA-62BF-4C54-AAB2-EC246342626C}</ClassId>
   </ComHandler>
</Actions>
```

A regular user can register a new CLSID in the HKCU hive, pointing to an arbitrary executable, and then instantiate this class through a scheduled task later on.

Using the Windows API, the most common functions to create an object are:

- **CoCreateInstance**: creates a single object on the local computer

```
HRESULT CoCreateInstance(
  [in]  REFCLSID  rclsid,
  [in]  LPUNKNOWN pUnkOuter,
  [in]  DWORD     dwClsContext,
  [in]  REFIID    riid,
  [out] LPVOID    *ppv
);
```

- **CoCreateInstanceEx**: creates a single object remotely

```
HRESULT CoCreateInstanceEx(
  [in]      REFCLSID     Clsid,
  [in]      IUnknown     *punkOuter,
  [in]      DWORD        dwClsCtx,
  [in]      COSERVERINFO *pServerInfo,
  [in]      DWORD        dwCount,
  [in, out] MULTI_QI     *pResults
);
```

- **CoGetClassObject**: creates a class factory object (most of the time), that can be used to instantiate multiple objects

```
HRESULT CoGetClassObject(
  [in]           REFCLSID rclsid,
  [in]           DWORD    dwClsContext,
  [in, optional] LPVOID   pvReserved,
  [in]           REFIID   riid,
  [out]          LPVOID   *ppv
);
```

Finally, you can instantiate classes in the explorer using the following syntax:

```
explorer "shell:::{D4480A50-BA28-11d1-8E75-00C04FA31A86}"
```

This trick can help to bypass **AppLocker** in some cases. The full list of explorer shortcuts can be found [here](https://www.elevenforum.com/t/list-of-windows-11-clsid-key-guid-shortcuts.1075/).

Under the hood, this class is instantiated using the `rundll32 C:\Windows\System32\shwebsvc.dll,AddNetPlaceRunDll` command. Some other similar classes might be interesting to investigate.

## Interfaces

According to Component-based software engineering principles, COM classes expose interfaces which are a collection of functions used to communicate with the client. A COM class can expose multiple interfaces where each interface is identified by an IID, which is a unique GUID.

Among all the available interfaces, one is quite special: **IUnknown**. Indeed, every single COM class must implement the **IUnknown** interface and every interface must inherit from **IUnknown**.

The interface **IUnknown** exposes the method **QueryInterface()** which takes an IID as an input and returns an interface pointer after calling **AddRef** (another method from **IUnknown** interface to manage reference counting).

```
HRESULT QueryInterface(
  REFIID riid,
  void   **ppvObject
);
```

Interfaces are described using the **IDL (Interface Definition Language)** format:

```
[object, uuid(673B0E01-4987-11d2-85C0-08001700C57F)]
interface ITest : IUnknown
{
  ULONG Test1();
  ULONG Test2();
}
```

Thereby for each interface, the following information are declared:

- The name of the interface, ex: ITest
- The name of the parent interface, ex: IUnknown
- For each method, the method prototype, ex: Test1()

The IDL file is then used to generate a **type library (TLB)** and other output files using the **MIDL compiler**. The TLB file stores information such as properties and methods of a COM or DCOM class in a binary format. This file is parsed at runtime by other applications to determine interfaces, and interfaces methods that can be called on an object. This way, clients and servers built using different languages can communicate by parsing an object type library. We’ll also see that this file can be very useful while looking for interesting methods.

All TLB files are referenced in the registry under the following key (example for the CLSID 91e132a0-0df1-11d2-86cc-444553540000): **HKEY\_CLASSES\_ROOT\\CLSID\\{91e132a0-0df1-11d2-86cc-444553540000}\\TypeLib**.

## Component types

We have seen a bit earlier that classes can be implemented two different ways:

- **InProcServer32**: The class is implemented in a shared library (DLL, In-process)
- **LocalServer32**: The class is implemented in an executable file (Exe, Out-of-process)

### In-process

As you can imagine, in-process components are running inside the process that instantiated the object. In most cases, they are defined in DLL files (except if they are instantiated from a remote computer, see [DLL Surrogates](https://learn.microsoft.com/en-us/windows/win32/com/dll-surrogates) for details).

You can spot DLLs implementing COM objects by the exported function **DllGetClassObject()** which takes a CLSID as input parameter and returns a class factory:

```
HRESULT DllGetClassObject(
  [in]  REFCLSID rclsid,
  [in]  REFIID   riid,
  [out] LPVOID   *ppv
);
```

Object factories allow creating an instance of an object via the **IClassFactory::CreateInstance()** method:

```
HRESULT CreateInstance(
  [in]  IUnknown *pUnkOuter,
  [in]  REFIID   riid,
  [out] void     **ppvObject
);
```

And finally you can call methods on the instantiated object.

To sum-up this process:

1. You call the exported function **DllGetClassObject(CLSID)** from the DLL referenced in the registry
2. You obtain a **class factory**
3. You call the **IClassFactory::CreateInstance(IID)** method on the class factory by specifying the IID of the desired interface
4. You call the final method on the desired interface of the instantiated object

![inprocess](https://www.synacktiv.com/sites/default/files/inline-images/inprocess.webp)

### Out-of-process

Out-of-process components are different in most aspects. First, they are running in a different process on your computer (or a remote computer via DCOM). They are implemented in executable binaries (.exe files).

Depending on the location of the server (locally or remote), the protocols and the interfaces involved might change but the overall process is similar. In fact, the ALPC (a protocol used for local RPC communications) protocol is replaced by DCE-RPC, interfaces and methods are also similar ( **ISystemActivator** and **IRemoteSCMActivator**)

The activation process of this types of component involves a new component: the DCOM activator which is a component of RPCSS. Thus, RPCSS exposes two RPC interfaces:

- **IActivation**: Legacy activator interface
- **IRemoteSCMActivator (aka ISystemActivator)**: Activator interface for COM version superior to 5.6 Those two interfaces are relatively similar, and they allow to call activation methods through the DCE-RPC protocol on remote hosts.

We will focus here on remote activation since the local activation process was already explained in details by James Forshaw in this [excellent talk](https://www.youtube.com/watch?v=dfMuzAZRGm4).

Although remote and local object activation are conceptually similar, interesting mechanisms are involved in this process.

### IOXIDResolver

The very first step of object activation is contacting the object resolver to get the string and security bindings from the server. This is done by calling the **ServerAlive2()** method the **IOXIDResolver** native RPC interface:

![IActivation](https://www.synacktiv.com/sites/default/files/inline-images/rpcview_iactivation.webp)

This method returns network and security bindings used to contact the object resolver:

![serveralive](https://www.synacktiv.com/sites/default/files/inline-images/2_serveralive_req.webp)

As you can see, the hostname of the machine as well as the IP address of each network interface are included in the response. This behavior was first discovered by Airbus Cybersecurity team and described in their [blog post](https://airbus-cyber-security.com/the-oxid-resolver-part-1-remote-enumeration-of-network-interfaces-without-any-authentication/). It can be very useful while looking for jump machines to access restricted subnetworks for instance.

### IActivation

This native RPC interface exposes only one method used for object activation: **[RemoteActivation](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dcom/cf56f36e-a87e-49b4-9729-ebb8a07054fb)**. This interface is used for older versions of DCOM but is still present.

You can easily identify this interface on **RPCView** from the **RPCSS.exe** process:

![IActivation](https://www.synacktiv.com/sites/default/files/inline-images/rpcview_iactivation_0.webp)

Don’t run, we’ll focus on some parameters:

- **Clsid**: The class identifier we’ve seen earlier
- **pIIDs**: The requested interface identifiers on the object to be created
- **pOxid**: The OXID, an identifier for the object exporter containing this object (we’ll take a deeper look at this component later)
- **pObjectStorage**: May contain a marshalled **OBJREF** (a bit more detail just below)

**ORPCthis** and **ORPCthat** parameters are structures added by the DCOM protocol to carry additional parameters ( [Ref](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dcom/db1d5ce1-a783-4f3d-854c-dc44308e78fb)) like versioning (we’ve seen before that DCOM supports different versions), causality information or application-specific out-of-band data.

The **OBJREF** is a structure containing a marshalled COM object sent to the client, and used to create a proxy object that acts as a stand-in for the remote object, allowing to call methods over the network.

The structure content and layout depends on the type of **OBJREF** used. Four types of **OBJREF** exist:

1. **OBJREF\_STANDARD**: Marshalling by reference
2. **OBJREF\_HANDLER**
3. **OBJREF\_CUSTOM**: Marshalling by value
4. **OBJREF\_EXTENDED**

The **OBJREF** structure then depends on the type of **OBJREF** defined in the flags of the header:

- **OBJREF\_STANDARD** specifies a reference to the object you want to interact with within the IPID field (pointing to the server hosting the object).
- **OBJREF\_CUSTOM** embeds the COM object in a marshalled form along with the CLSID of the class used to then unmarshall the data on the client.

![objref](https://www.synacktiv.com/sites/default/files/inline-images/objref.drawio.webp)

We’ll see after how this **OBJREF** is used to interact with the final **OBJECT** in both cases.

Although the interface **IActivation** exists, and the process being similar, the **IRemoteSCMActivator** interface is preferred for newer versions of DCOM.

### ISystemActivator (or IRemoteSCMActivator)

Unlike the **IActivation** interface, **IRemoteSCMActivator** splits the activation process in two functions:

- **RemoteGetClassObject**: used by the client to create an **OBJREF** for the class factory object

```
HRESULT RemoteGetClassObject(
   [in] handle_t rpc,
   [in] ORPCTHIS* orpcthis,
   [out] ORPCTHAT* orpcthat,
   [in, unique] MInterfacePointer* pActProperties,
   [out] MInterfacePointer** ppActProperties
 );
```

- **RemoteCreateInstance**: used by the client to create an **OBJREF** for the actual object

```
 HRESULT RemoteCreateInstance(
   [in] handle_t rpc,
   [in] ORPCTHIS* orpcthis,
   [out] ORPCTHAT* orpcthat,
   [in, unique] MInterfacePointer* pUnkOuter,
   [in, unique] MInterfacePointer* pActProperties,
   [out] MInterfacePointer** ppActProperties
 );
```

Both functions take activation properties as input and output information to connect back to the object.

The activation properties structure is divided into a header and activation properties. The header contains various information related to the classes you want to instantiate such as the CLSIDs.

The properties structure is as follows:

```
struct InstantiationInfoData {
    CLSID classId; #CLSID to create
    DWORD classCtx;
    DWORD actvflags; #Activation flags
    long fIsSurrogate;
    DWORD cIID;
    DWORD instFlag;
    IID *pIID; #List of interface IDs to query for
    DWORD thisSize;
    COMVERSION clientCOMVersion;
}
```

For instance, while instantiating remotely the **MMC20.Application** class with **RemoteGetClassObject()**, the following **InstantiationInfoData** structure containing the CLSID and the IID of the class factory is passed to the server:

![MMC20.Application](https://www.synacktiv.com/sites/default/files/inline-images/mmc20.application_remotegetclassobject_request.webp)

The server then sends back a response containing an OBJREF\_CUSTOM (always) with the IID 000001a3-0000-0000-c000-000000000046 corresponding to **IID\_IActivationPropertiesOut**, a specific structure containing information regarding the activation of the requested interface.

This was a bit confusing at first, what if I want a standard **OBJREF** ? Well this **OBJREF** is not the one you expected, and the response is deeper.

The response structure is split into two parts, the **CustomHeader** and the **Properties**, itself divided in two parts:

- [ScmReplyInfo](https://learn.microsoft.com/fr-fr/openspecs/windows_protocols/ms-dcom/eab34106-2ea4-4bf5-ae6c-77b57fda5d6c): A structure providing information needed to contact the remote object exporter (IRemUnknown2)

_Remark: From now on, an RPC channel is established between the client and the object resolver on a dynamic RPC port (here 62076/TCP) sent by the server in the String Bindings contained in the **ScmReplyInfo** structure._

![scmreply](https://www.synacktiv.com/sites/default/files/inline-images/scmreplyinfo.webp)

- [PropertiesOutput](https://learn.microsoft.com/fr-fr/openspecs/windows_protocols/ms-dcom/7f35873f-0f4b-47e7-a90c-f2ced71fecd6): A structure containing pointers to the interfaces requested by the client that the object implements as well as an **OBJREF** (standard or custom)

```
struct PropsOutInfo {
    DWORD cIfs;
    IID* piid;
    HRESULT* phresults;
    MInterfacePointer** ppIntfData;
}
```

![propsoutinfo](https://www.synacktiv.com/sites/default/files/inline-images/propsoutinfo.webp)

Next steps are quite similar to the in-process activation. Indeed, we need to contact the object resolver on the remote host in order to access the class factory object. The IPID of the **IRemUnknown2** interface (the object exporter) is the only information needed to contact it.

The **IRemUnknown2** interface is analog to the holy **IUnknown** interface locally, it also the equivalent method to **QueryInterface**():

```
 HRESULT RemQueryInterface2(
   [in] REFIPID ripid,
   [in] unsigned short cIids,
   [in, size_is(cIids)] IID* iids,
   [out, size_is(cIids)] HRESULT* phr,
   [out, size_is(cIids)] PMInterfacePointerInternal* ppMIF
 );
```

As you may have already guessed, this method takes as input the IPID of the interface you want to talk to (here **IClassFactory** we got from the **PropertiesOut** structure). In this example, we do have a Class Factory, however if your class does not implement a factory interface, the object is then contacted directly.

![RemQueryInterface](https://www.synacktiv.com/sites/default/files/inline-images/remqueryinterface.webp)

The **IClassFactory** interface is then queried via DCE-RPC directly to create the object instance with the method **CreateInstance()**:

```
HRESULT CreateInstance(
  [in]  IUnknown *pUnkOuter,
  [in]  REFIID   riid,
  [out] void     **ppvObject
);
```

At this time of the research I was looking for a plain **OBJREF** in Wireshark, then I heard the **OBJREF** meowing to my ear:

![classfactory_response](https://www.synacktiv.com/sites/default/files/inline-images/iclassfactory_response.webp)

This MEOW string is the **OBJREF** signature and by saving this binary data to a file, striping the beginning and parsing it with OLEView.NET (Object > Hex Editor > From File), you can see that this is an **OBJREF** for the **IUnknown** interface:

![objref](https://www.synacktiv.com/sites/default/files/inline-images/objref_parsing.webp)

We are now ready to call the **IUnknown** interface from the final object in order to query further interfaces.

## Conclusion

In this article, we have explored the different types of components involved in COM/DCOM (Classes, Interfaces) and their identifiers (ProgIDs, CLSIDs, AppIDs, IIDs). We also discussed how to enumerate them using native tools (PowerShell, Windows Registry) or external tools such as OleView.NET.

Then, we described the different ways to instantiate a class.

Next time, we will try to understand the mechanics behind method calling or object enumeration and the permission mechanism.

## References

- [James Forshaw - COM in Sixty Seconds! (well minutes more likely) @ Infiltrate 2017](https://www.youtube.com/watch?v=dfMuzAZRGm4)
- [Finding Interactive User COM Objects using PowerShell - Tyranid's Lair](https://www.tiraniddo.dev/2018/09/finding-interactive-user-com-objects_9.html)

Share this article

[Facebook](https://www.synacktiv.com/#facebook) [Twitter](https://www.synacktiv.com/#twitter)

## Other publications

[**Beyond ACLs: Mapping Windows Privilege Escalation Paths with BloodHound**](https://www.synacktiv.com/en/publications/beyond-acls-mapping-windows-privilege-escalation-paths-with-bloodhound)

Windows privileges are special rights that grant processes the ability to perform sensitive operations. Some privileges allow bypassing standard Access Control List (ACL) checks, which can lead to sig

...


Noah Chaslin
\- 02/02/2026 -
Pentest

[**On the clock: Escaping VMware Workstation at Pwn2Own Berlin 2025**](https://www.synacktiv.com/en/publications/on-the-clock-escaping-vmware-workstation-at-pwn2own-berlin-2025)

At Pwn2Own Berlin 2025, we exploited VMware Workstation by abusing a Heap-Overflow in its PVSCSI controller implementation. The vulnerable allocation landed in the LFH allocator of Windows 11, whose e

...


Thomas Bouzerar, Etienne Helluy-Lafont
\- 23/01/2026 -
Exploit, Reverse-engineering

[**Wireless-(in)Fidelity: Pentesting Wi-Fi in 2025**](https://www.synacktiv.com/en/publications/wireless-infidelity-pentesting-wi-fi-in-2025)

Despite the advancements that have been made in Wi-Fi security with the arrival of WPA3, some misconfigurations and legacy protocols still remain. In this blogpost, we share insights into Wi-Fi relate

...


Quentin Vacher
\- 14/01/2026 -
Pentest

✓

Thanks for sharing!

[Facebook](https://www.synacktiv.com/#facebook) [Twitter](https://www.synacktiv.com/#twitter) [Email](https://www.synacktiv.com/#email) [Pinterest](https://www.synacktiv.com/#pinterest) [LinkedIn](https://www.synacktiv.com/#linkedin) [Reddit](https://www.synacktiv.com/#reddit) [WhatsApp](https://www.synacktiv.com/#whatsapp) [Gmail](https://www.synacktiv.com/#google_gmail) [Telegram](https://www.synacktiv.com/#telegram) [Pocket](https://www.synacktiv.com/#pocket) [Mix](https://www.synacktiv.com/#mix) [Tumblr](https://www.synacktiv.com/#tumblr) [Amazon Wish List](https://www.synacktiv.com/#amazon_wish_list) [AOL Mail](https://www.synacktiv.com/#aol_mail) [Balatarin](https://www.synacktiv.com/#balatarin) [BibSonomy](https://www.synacktiv.com/#bibsonomy) [Bitty Browser](https://www.synacktiv.com/#bitty_browser) [Blinklist](https://www.synacktiv.com/#blinklist) [Blogger](https://www.synacktiv.com/#blogger) [BlogMarks](https://www.synacktiv.com/#blogmarks) [Bookmarks.fr](https://www.synacktiv.com/#bookmarks_fr) [Box.net](https://www.synacktiv.com/#box_net) [Buffer](https://www.synacktiv.com/#buffer) [Care2 News](https://www.synacktiv.com/#care2_news) [CiteULike](https://www.synacktiv.com/#citeulike) [Copy Link](https://www.synacktiv.com/#copy_link) [Design Float](https://www.synacktiv.com/#design_float) [Diary.Ru](https://www.synacktiv.com/#diary_ru) [Diaspora](https://www.synacktiv.com/#diaspora) [Digg](https://www.synacktiv.com/#digg) [Diigo](https://www.synacktiv.com/#diigo) [Douban](https://www.synacktiv.com/#douban) [Draugiem](https://www.synacktiv.com/#draugiem) [DZone](https://www.synacktiv.com/#dzone) [Evernote](https://www.synacktiv.com/#evernote) [Facebook Messenger](https://www.synacktiv.com/#facebook_messenger) [Fark](https://www.synacktiv.com/#fark) [Flipboard](https://www.synacktiv.com/#flipboard) [Folkd](https://www.synacktiv.com/#folkd) [Google Bookmarks](https://www.synacktiv.com/#google_bookmarks) [Google Classroom](https://www.synacktiv.com/#google_classroom) [Hacker News](https://www.synacktiv.com/#hacker_news) [Hatena](https://www.synacktiv.com/#hatena) [Houzz](https://www.synacktiv.com/#houzz) [Instapaper](https://www.synacktiv.com/#instapaper) [Kakao](https://www.synacktiv.com/#kakao) [Kik](https://www.synacktiv.com/#kik) [Push to Kindle](https://www.synacktiv.com/#kindle_it) [Known](https://www.synacktiv.com/#known) [Line](https://www.synacktiv.com/#line) [LiveJournal](https://www.synacktiv.com/#livejournal) [Mail.Ru](https://www.synacktiv.com/#mail_ru) [Mastodon](https://www.synacktiv.com/#mastodon) [Mendeley](https://www.synacktiv.com/#mendeley) [Meneame](https://www.synacktiv.com/#meneame) [MeWe](https://www.synacktiv.com/#mewe) [Mixi](https://www.synacktiv.com/#mixi) [MySpace](https://www.synacktiv.com/#myspace) [Netvouz](https://www.synacktiv.com/#netvouz) [Odnoklassniki](https://www.synacktiv.com/#odnoklassniki) [Outlook.com](https://www.synacktiv.com/#outlook_com) [Papaly](https://www.synacktiv.com/#papaly) [Pinboard](https://www.synacktiv.com/#pinboard) [Plurk](https://www.synacktiv.com/#plurk) [Print](https://www.synacktiv.com/#print) [PrintFriendly](https://www.synacktiv.com/#printfriendly) [Protopage Bookmarks](https://www.synacktiv.com/#protopage_bookmarks) [Pusha](https://www.synacktiv.com/#pusha) [Qzone](https://www.synacktiv.com/#qzone) [Rediff MyPage](https://www.synacktiv.com/#rediff) [Refind](https://www.synacktiv.com/#refind) [Renren](https://www.synacktiv.com/#renren) [Sina Weibo](https://www.synacktiv.com/#sina_weibo) [SiteJot](https://www.synacktiv.com/#sitejot) [Skype](https://www.synacktiv.com/#skype) [Slashdot](https://www.synacktiv.com/#slashdot) [SMS](https://www.synacktiv.com/#sms) [StockTwits](https://www.synacktiv.com/#stocktwits) [Svejo](https://www.synacktiv.com/#svejo) [Symbaloo Bookmarks](https://www.synacktiv.com/#symbaloo_bookmarks) [Threema](https://www.synacktiv.com/#threema) [Trello](https://www.synacktiv.com/#trello) [Tuenti](https://www.synacktiv.com/#tuenti) [Twiddla](https://www.synacktiv.com/#twiddla) [TypePad Post](https://www.synacktiv.com/#typepad_post) [Viadeo](https://www.synacktiv.com/#viadeo) [Viber](https://www.synacktiv.com/#viber) [VK](https://www.synacktiv.com/#vk) [Wanelo](https://www.synacktiv.com/#wanelo) [WeChat](https://www.synacktiv.com/#wechat) [WordPress](https://www.synacktiv.com/#wordpress) [Wykop](https://www.synacktiv.com/#wykop) [XING](https://www.synacktiv.com/#xing) [Yahoo Mail](https://www.synacktiv.com/#yahoo_mail) [Yoolink](https://www.synacktiv.com/#yoolink) [Yummly](https://www.synacktiv.com/#yummly)

[AddToAny](https://www.addtoany.com/ "Share Buttons")

[Facebook](https://www.synacktiv.com/#facebook) [Twitter](https://www.synacktiv.com/#twitter) [Email](https://www.synacktiv.com/#email) [Pinterest](https://www.synacktiv.com/#pinterest) [LinkedIn](https://www.synacktiv.com/#linkedin) [Reddit](https://www.synacktiv.com/#reddit) [WhatsApp](https://www.synacktiv.com/#whatsapp) [Gmail](https://www.synacktiv.com/#google_gmail)

[Email](https://www.synacktiv.com/#email) [Gmail](https://www.synacktiv.com/#google_gmail) [AOL Mail](https://www.synacktiv.com/#aol_mail) [Outlook.com](https://www.synacktiv.com/#outlook_com) [Yahoo Mail](https://www.synacktiv.com/#yahoo_mail)

[More…](https://www.synacktiv.com/en/publications/dissecting-dcom-part-1 "Show all")

Back to top