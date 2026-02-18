# https://learn.microsoft.com/en-us/windows/win32/learnwin32/initializing-the-com-library

Table of contents Exit editor mode

Ask LearnAsk LearnFocus mode

Table of contents[Read in English](https://learn.microsoft.com/en-us/windows/win32/learnwin32/initializing-the-com-library)Add to CollectionsAdd to plan[Edit](https://github.com/MicrosoftDocs/win32/blob/docs/desktop-src/LearnWin32/initializing-the-com-library.md)

* * *

#### Share via

[Facebook](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Flearnwin32%2Finitializing-the-com-library%3FWT.mc_id%3Dfacebook) [x.com](https://twitter.com/intent/tweet?original_referer=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Flearnwin32%2Finitializing-the-com-library%3FWT.mc_id%3Dtwitter&tw_p=tweetbutton&url=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Flearnwin32%2Finitializing-the-com-library%3FWT.mc_id%3Dtwitter) [LinkedIn](https://www.linkedin.com/feed/?shareActive=true&text=%0A%0D%0Ahttps%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Flearnwin32%2Finitializing-the-com-library%3FWT.mc_id%3Dlinkedin) [Email](mailto:?subject=%5BShared%20Article%5D%20Initializing%20the%20COM%20Library%20-%20Win32%20apps%20%7C%20Microsoft%20Learn&body=%0A%0D%0Ahttps%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Flearnwin32%2Finitializing-the-com-library%3FWT.mc_id%3Demail)

* * *

Copy MarkdownPrint

* * *

Note

Access to this page requires authorization. You can try [signing in](https://learn.microsoft.com/en-us/windows/win32/learnwin32/initializing-the-com-library#) or changing directories.


Access to this page requires authorization. You can try changing directories.


# Initializing the COM Library

Feedback

Summarize this article for me


Any Windows program that uses COM must initialize the COM library by calling the [**CoInitializeEx**](https://learn.microsoft.com/en-us/windows/desktop/api/combaseapi/nf-combaseapi-coinitializeex) function. Each thread that uses a COM interface must make a separate call to this function. **CoInitializeEx** has the following signature:

C++Copy

```c++
HRESULT CoInitializeEx(LPVOID pvReserved, DWORD dwCoInit);
```

The first parameter is reserved and must be **NULL**. The second parameter specifies the threading model that your program will use. COM supports two different threading models, _apartment threaded_ and _multithreaded_. If you specify apartment threading, you are making the following guarantees:

- You will access each COM object from a single thread; you will not share COM interface pointers between multiple threads.
- The thread will have a message loop. (See [Window Messages](https://learn.microsoft.com/en-us/windows/win32/learnwin32/window-messages) in Module 1.)

If either of these constraints is not true, use the multithreaded model. To specify the threading model, set one of the following flags in the _dwCoInit_ parameter.

Expand table

| Flag | Description |
| --- | --- |
| **COINIT\_APARTMENTTHREADED** | Apartment threaded. |
| **COINIT\_MULTITHREADED** | Multithreaded. |

You must set exactly one of these flags. Generally, a thread that creates a window should use the **COINIT\_APARTMENTTHREADED** flag, and other threads should use **COINIT\_MULTITHREADED**. However, some COM components require a particular threading model.

Note

Actually, even if you specify apartment threading, it is still possible to share interfaces between threads, by using a technique called _marshaling_. Marshaling is beyond the scope of this module. The important point is that with apartment threading, you must never simply copy an interface pointer to another thread. For more information about the COM threading models, see [Processes, Threads, and Apartments](https://learn.microsoft.com/en-us/windows/desktop/com/processes--threads--and-apartments).

In addition to the flags already mentioned, it is a good idea to set the **COINIT\_DISABLE\_OLE1DDE** flag in the _dwCoInit_ parameter. Setting this flag avoids some overhead associated with Object Linking and Embedding (OLE) 1.0, an obsolete technology.

Here is how you would initialize COM for apartment threading:

C++Copy

```c++
HRESULT hr = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED | COINIT_DISABLE_OLE1DDE);
```

The **HRESULT** return type contains an error or success code. We'll look at COM error handling in the next section.

[Section titled: Uninitializing the COM Library](https://learn.microsoft.com/en-us/windows/win32/learnwin32/initializing-the-com-library#uninitializing-the-com-library)

## Uninitializing the COM Library

For every successful call to [**CoInitializeEx**](https://learn.microsoft.com/en-us/windows/desktop/api/combaseapi/nf-combaseapi-coinitializeex), you must call [**CoUninitialize**](https://learn.microsoft.com/en-us/windows/desktop/api/combaseapi/nf-combaseapi-couninitialize) before the thread exits. This function takes no parameters and has no return value.

C++Copy

```c++
CoUninitialize();
```

[Section titled: Next](https://learn.microsoft.com/en-us/windows/win32/learnwin32/initializing-the-com-library#next)

## Next

[Error Codes in COM](https://learn.microsoft.com/en-us/windows/win32/learnwin32/error-codes-in-com)

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


[Initialize data during extension installation in Dynamics 365 Business Central - Training](https://learn.microsoft.com/en-us/training/modules/initialize-data-extension-installation/?source=recommendations)

Do you want to know how to initialize data during extension installation for Microsoft Dynamics 365 Business Central? Initializing data when you're installing an extension automate many steps that you must otherwise perform manually. By automating this process, you can quickly set up an extension and it becomes more user-friendly.


* * *

- Last updated on 07/09/2024

Ask Learn is an AI assistant that can answer questions, clarify concepts, and define terms using trusted Microsoft documentation.

Please sign in to use Ask Learn.

[Sign in](https://learn.microsoft.com/en-us/windows/win32/learnwin32/initializing-the-com-library#)