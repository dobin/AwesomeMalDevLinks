# https://learn.microsoft.com/en-us/windows/win32/midl/com-dcom-and-type-libraries

Table of contents Exit editor mode

Ask LearnAsk LearnFocus mode

Table of contents[Read in English](https://learn.microsoft.com/en-us/windows/win32/midl/com-dcom-and-type-libraries)Add to CollectionsAdd to plan[Edit](https://github.com/MicrosoftDocs/win32/blob/docs/desktop-src/Midl/com-dcom-and-type-libraries.md)

* * *

#### Share via

[Facebook](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Fmidl%2Fcom-dcom-and-type-libraries%3FWT.mc_id%3Dfacebook) [x.com](https://twitter.com/intent/tweet?original_referer=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Fmidl%2Fcom-dcom-and-type-libraries%3FWT.mc_id%3Dtwitter&tw_p=tweetbutton&url=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Fmidl%2Fcom-dcom-and-type-libraries%3FWT.mc_id%3Dtwitter) [LinkedIn](https://www.linkedin.com/feed/?shareActive=true&text=%0A%0D%0Ahttps%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Fmidl%2Fcom-dcom-and-type-libraries%3FWT.mc_id%3Dlinkedin) [Email](mailto:?subject=%5BShared%20Article%5D%20COM%2C%20DCOM%2C%20and%20Type%20Libraries%20-%20Win32%20apps%20%7C%20Microsoft%20Learn&body=%0A%0D%0Ahttps%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Fmidl%2Fcom-dcom-and-type-libraries%3FWT.mc_id%3Demail)

* * *

Copy MarkdownPrint

* * *

Note

Access to this page requires authorization. You can try [signing in](https://learn.microsoft.com/en-us/windows/win32/midl/com-dcom-and-type-libraries#) or changing directories.


Access to this page requires authorization. You can try changing directories.


# COM, DCOM, and Type Libraries

Feedback

Summarize this article for me


Component Object Model (COM) and Distributed Component Object Model (DCOM) use Remote Procedure Calls (RPC) to enable distributed component objects to communicate with each other. Thus, a COM or DCOM interface defines the identity and external characteristics of a COM object. It forms the means by which clients can gain access to an object's methods and data. With DCOM, this access is possible regardless of whether the objects exist in the same process, different processes on the same machine, or on different machines. As with RPC client/server interfaces, a COM or DCOM object can expose its functionality in a number of different ways and through multiple interfaces.

[Section titled: Type Library](https://learn.microsoft.com/en-us/windows/win32/midl/com-dcom-and-type-libraries#type-library)

## Type Library

A type library (.tlb) is a binary file that stores information about a COM or DCOM object's properties and methods in a form that is accessible to other applications at runtime. Using a type library, an application or browser can determine which interfaces an object supports, and invoke an object's interface methods. This can occur even if the object and client applications were written in different programming languages. The COM/DCOM run-time environment can also use a type library to provide automatic cross-apartment, cross-process, and cross-machine marshaling for interfaces described in type libraries.

[Section titled: Characteristics of an Interface](https://learn.microsoft.com/en-us/windows/win32/midl/com-dcom-and-type-libraries#characteristics-of-an-interface)

## Characteristics of an Interface

You define the characteristics of an interface in an interface definition (IDL) file and an optional application configuration file (ACF):

- The IDL file specifies the characteristics of the application's interfaces on the wire — that is, how data is to be transmitted between client and server, or between COM objects.
- The ACF file specifies interface characteristics, such as binding handles, that pertain only to the local operating environment. The ACF file can also specify how to marshal and transmit a complex data structure in a machine-independent form.

For more information on IDL and ACF files, see [The IDL and ACF Files](https://learn.microsoft.com/en-us/windows/desktop/Rpc/the-idl-and-acf-files).

The IDL and ACF files are scripts written in Microsoft Interface Definition Language (MIDL), which is the Microsoft implementation and extension of the OSF-DCE interface definition language (IDL). The Microsoft extensions to the IDL language enable you to create COM interfaces and type libraries. The compiler, Midl.exe, uses these scripts to generate C-language stubs and header files as well as type library files.

[Section titled: The MIDL Compiler](https://learn.microsoft.com/en-us/windows/win32/midl/com-dcom-and-type-libraries#the-midl-compiler)

## The MIDL Compiler

Depending on the contents of your IDL file, the MIDL compiler will generate any of the following files.

A C-language proxy/stub file, an interface identifier file, a DLL data file, and a related header file for a custom COM interface. The MIDL compiler generates these files when it encounters the object attribute in an interface attribute list. For more detailed information on these files, see [Files Generated for a COM Interface](https://learn.microsoft.com/en-us/windows/win32/midl/files-generated-for-a-com-interface).

A compiled type library (.tlb) file and related header file. MIDL generates these files when it encounters a [**library**](https://learn.microsoft.com/en-us/windows/win32/midl/library) statement in the IDL file. For general information about type libraries, see [Contents of a Type Library](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/automat/contents-of-a-type-library), in the Automation Programmer's Reference.

C/C++-language client and server stub files and related header file for an RPC interface. These files are generated when there are interfaces in the IDL file that do not have the [**object**](https://learn.microsoft.com/en-us/windows/win32/midl/object) attribute. For an overview of the stub and header files, see [General Build Procedure](https://learn.microsoft.com/en-us/windows/desktop/Rpc/general-build-procedure). For more detailed information, see [Files Generated for an RPC Interface](https://learn.microsoft.com/en-us/windows/win32/midl/files-generated-for-an-rpc-interface).

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

Training


Module


[Implement interfaces in Dynamics 365 Business Central - Training](https://learn.microsoft.com/en-us/training/modules/business-central-interfaces/?source=recommendations)

Do you want to know how to implement interfaces in AL? If so, this module will explain how to implement interfaces in AL for use with Microsoft Dynamics 365 Business Central.


* * *

- Last updated on 08/19/2020

Ask Learn is an AI assistant that can answer questions, clarify concepts, and define terms using trusted Microsoft documentation.

Please sign in to use Ask Learn.

[Sign in](https://learn.microsoft.com/en-us/windows/win32/midl/com-dcom-and-type-libraries#)