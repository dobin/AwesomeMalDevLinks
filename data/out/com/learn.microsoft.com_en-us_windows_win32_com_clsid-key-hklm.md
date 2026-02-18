# https://learn.microsoft.com/en-us/windows/win32/com/clsid-key-hklm

Table of contents Exit editor mode

Ask LearnAsk LearnFocus mode

Table of contents[Read in English](https://learn.microsoft.com/en-us/windows/win32/com/clsid-key-hklm)Add to CollectionsAdd to plan[Edit](https://github.com/MicrosoftDocs/win32/blob/docs/desktop-src/com/clsid-key-hklm.md)

* * *

#### Share via

[Facebook](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Fcom%2Fclsid-key-hklm%3FWT.mc_id%3Dfacebook) [x.com](https://twitter.com/intent/tweet?original_referer=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Fcom%2Fclsid-key-hklm%3FWT.mc_id%3Dtwitter&tw_p=tweetbutton&url=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Fcom%2Fclsid-key-hklm%3FWT.mc_id%3Dtwitter) [LinkedIn](https://www.linkedin.com/feed/?shareActive=true&text=%0A%0D%0Ahttps%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Fcom%2Fclsid-key-hklm%3FWT.mc_id%3Dlinkedin) [Email](mailto:?subject=%5BShared%20Article%5D%20CLSID%20Key%20-%20Win32%20apps%20%7C%20Microsoft%20Learn&body=%0A%0D%0Ahttps%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Fcom%2Fclsid-key-hklm%3FWT.mc_id%3Demail)

* * *

Copy MarkdownPrint

* * *

Note

Access to this page requires authorization. You can try [signing in](https://learn.microsoft.com/en-us/windows/win32/com/clsid-key-hklm#) or changing directories.


Access to this page requires authorization. You can try changing directories.


# CLSID Key

Feedback

Summarize this article for me


A CLSID is a globally unique identifier that identifies a COM class object. If your server or container allows linking to its embedded objects, you need to register a CLSID for each supported class of objects.

[Section titled: Registry Key](https://learn.microsoft.com/en-us/windows/win32/com/clsid-key-hklm#registry-key)

## Registry Key

**HKEY\_LOCAL\_MACHINE\\SOFTWARE\\Classes\\CLSID**\ _{CLSID}_

Expand table

| Registry key | Description |
| --- | --- |
| [**AppID**](https://learn.microsoft.com/en-us/windows/win32/com/appid) | Associates an AppID with a CLSID. |
| [**AutoConvertTo**](https://learn.microsoft.com/en-us/windows/win32/com/autoconvertto) | Specifies the automatic conversion of a given class of objects to a new class of objects. |
| [**AutoTreatAs**](https://learn.microsoft.com/en-us/windows/win32/com/autotreatas) | Automatically sets the CLSID for the [**TreatAs**](https://learn.microsoft.com/en-us/windows/win32/com/treatas) key to the specified value. |
| [**AuxUserType**](https://learn.microsoft.com/en-us/windows/win32/com/auxusertype) | Specifies an application's short display name and application names. |
| [**Control**](https://learn.microsoft.com/en-us/windows/win32/com/control) | Identifies an object as an ActiveX Control. |
| [**Conversion**](https://learn.microsoft.com/en-us/windows/win32/com/conversion) | Used by the **Convert** dialog box to determine the formats an application can read and write. |
| [**DataFormats**](https://learn.microsoft.com/en-us/windows/win32/com/dataformats) | Specifies the default and main data formats supported by an application. |
| [**DefaultIcon**](https://learn.microsoft.com/en-us/windows/win32/com/defaulticon) | Provides default icon information for iconic presentations of objects. |
| [**InprocHandler**](https://learn.microsoft.com/en-us/windows/win32/com/inprochandler) | Specifies whether an application uses a custom handler. |
| [**InprocHandler32**](https://learn.microsoft.com/en-us/windows/win32/com/inprochandler32) | Specifies whether an application uses a custom handler. |
| [**InprocServer**](https://learn.microsoft.com/en-us/windows/win32/com/inprocserver) | Specifies the path to the in-process server DLL. |
| [**InprocServer32**](https://learn.microsoft.com/en-us/windows/win32/com/inprocserver32) | Registers a 32-bit in-process server and specifies the threading model of the apartment the server can run in. |
| [**Insertable**](https://learn.microsoft.com/en-us/windows/win32/com/insertable) | Indicates that objects of this class should appear in the **Insert Object** dialog box list box when used by COM container applications. |
| [**Interface**](https://learn.microsoft.com/en-us/windows/win32/com/interface) | An optional entry that specifies all interface IDs (IIDs) supported by the associated class. |
| [**LocalServer**](https://learn.microsoft.com/en-us/windows/win32/com/localserver) | Specifies the full path to a 16-bit local server application. |
| [**LocalServer32**](https://learn.microsoft.com/en-us/windows/win32/com/localserver32) | Specifies the full path to a 32-bit local server application. |
| [**MiscStatus**](https://learn.microsoft.com/en-us/windows/win32/com/miscstatus) | Specifies how to create and display an object. |
| [**ProgID**](https://learn.microsoft.com/en-us/windows/win32/com/progid) | Associates a ProgID with a CLSID. |
| [**ToolBoxBitmap32**](https://learn.microsoft.com/en-us/windows/win32/com/toolboxbitmap32) | Identifies the module name and resource ID for a 16 x 16 bitmap to use for the face of a toolbar or toolbox button. |
| [**TreatAs**](https://learn.microsoft.com/en-us/windows/win32/com/treatas) | Specifies the CLSID of a class that can emulate the current class. |
| [**Verb**](https://learn.microsoft.com/en-us/windows/win32/com/verb) | Specifies the verbs to be registered for an application. |
| [**Version**](https://learn.microsoft.com/en-us/windows/win32/com/version) | Specifies the version number of the control. |
| [**VersionIndependentProgID**](https://learn.microsoft.com/en-us/windows/win32/com/versionindependentprogid) | Associates a ProgID with a CLSID. This value is used to determine the latest version of an object application. |

[Section titled: Remarks](https://learn.microsoft.com/en-us/windows/win32/com/clsid-key-hklm#remarks)

## Remarks

The **HKEY\_LOCAL\_MACHINE\\SOFTWARE\\Classes** key corresponds to the **HKEY\_CLASSES\_ROOT** key, which was retained for compatibility with earlier versions of COM.

The CLSID key contains information used by the default COM handler to return information about a class when it is in the running state.

To obtain a CLSID for your application, you can use the Uuidgen.exe, or use the [**CoCreateGuid**](https://learn.microsoft.com/en-us/windows/desktop/api/combaseapi/nf-combaseapi-cocreateguid) function.

The CLSID is a 128-bit number, in hex, within a pair of curly braces.

[Section titled: Related topics](https://learn.microsoft.com/en-us/windows/win32/com/clsid-key-hklm#related-topics)

## Related topics

[**CoCreateGuid**](https://learn.microsoft.com/en-us/windows/desktop/api/combaseapi/nf-combaseapi-cocreateguid)

* * *

## Feedback

Was this page helpful?


YesNoNo

Need help with this topic?


Want to try using Ask Learn to clarify or guide you through this topic?


Ask LearnAsk Learn

Suggest a fix?

* * *

## Additional resources

* * *

- Last updated on 08/23/2019

Ask Learn is an AI assistant that can answer questions, clarify concepts, and define terms using trusted Microsoft documentation.

Please sign in to use Ask Learn.

[Sign in](https://learn.microsoft.com/en-us/windows/win32/com/clsid-key-hklm#)