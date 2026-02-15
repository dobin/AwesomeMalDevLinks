# https://www.okiok.com/achieving-dll-side-loading-in-the-original-process/

By [Guillaume Caillé](https://www.okiok.com/author/gcaille/ "Posts by Guillaume Caillé")

Posted [March 19, 2024](https://www.okiok.com/2024/03/)

In [Blog](https://www.okiok.com/category/blog/)

Achieving DLL Side-Loading in the Original Process2024-03-192024-03-19/wp-content/uploads/2016/09/stick-logo2.pngOkiok/wp-content/uploads/2016/09/stick-logo2.png200px200px

[0](https://www.okiok.com/achieving-dll-side-loading-in-the-original-process/#comments) [Print](https://www.okiok.com/achieving-dll-side-loading-in-the-original-process/# "Print")

### Introduction

DLL side loading has been used for quite some time now to achieve code execution in a trusted signed process. It has been extensively discussed in other blogs, so I invite you to read them first as I won’t repeat that here. The easy and most popular way to do it is by placing code into DllMain to do remote shellcode injection once the DLL gets loaded into a process.

Remote injection has been less and less easy to do in the recent time against good EDRs, but it is still doable using recent techniques, for example, how “Pool Party” is doing it at this time.

Local execution of the shellcode in the original process by jumping to its beginning remains a more stable and OPSEC approach in most scenarios, but it comes with a limitation when doing DLL side-loading, namely the “Loader Lock”. In essence, being inside the loader lock means being significantly restricted as per which functions that can be called in that state.

![](https://www.okiok.com/wp-content/uploads/2024/03/dll_order.png)

Figure 1 source: https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-best-practices

This is because most C2 shellcodes, like Cobalt Strike’s, will attempt to load other DLLs during initialization, which is not permitted nor recommended inside the loader lock. This will result, most of the time, in a blocked process and no shell.

So, what are our options? Some people are creating a separate thread and executing from there with success, but it is not a [recommended solution](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-best-practices#:~:text=You%20should%20never%20perform%20the%20following%20tasks%20from%20within%20DllMain%3A) as per Microsoft because, depending on what is done in that thread, it can create a deadlock or a crash. I personally never use DllMain to do side-loading and prefer to reimplement and export the first method that is exported by the legitimate DLL and called by the side-loaded process. This is notably useful in scenarios where you don’t want to have the original program display any visual indicator to the potentially currently logged-in user and where completely hijacking the program functionality is what is desired.

This blog post will present the methodology I use to find good candidates and how to circumvent problems that might arise when compiling.

### Finding Side-Loadable Candidates

First, I fire up Process Monitor with the usual parameters to find DLLs which are first searched in the current directory but not found.

![](https://www.okiok.com/wp-content/uploads/2024/03/procmon_filter.png)

Then, I start executing arbitrary signed binaries on my test system until I see a missing DLL that is attempted to be loaded from the testing folder:

![](https://www.okiok.com/wp-content/uploads/2024/03/procmon.png)

The ideal candidates are signed binaries that can be launched without requiring dozens of other files in the same folder architecture to make them more portable.

In this example, I found an HP related binary that seemed to be vulnerable to side-loading when placing a custom VERSION.dll in the same folder. OPSEC wise, however, version.dll is a common target for detections and should be avoided for real life scenarios, if possible.

### Finding Hijackable Exported Functions

Then, using API Monitor (some people prefer to use Frida here, but in this case, I find it’s easier to just use this tool), it is possible to see what functions are called by the original signed process from the target DLL by filtering on GetProcAddress and LoadLibrary function calls. Here, there were three functions looked up in the target DLL.

![](https://www.okiok.com/wp-content/uploads/2024/03/sideloading-apimonitor.png)

In the use cases I described at the beginning of this post, its ideal to hijack the first function that gets called and jump directly to the shellcode to eliminate the need to reimplement anything from the original DLL.

In this case, with Microsoft’s documentation for [VerQueryValueW](https://learn.microsoft.com/en-us/windows/win32/api/winver/nf-winver-verqueryvaluew), It is possible to confirm which one is called first: “ _Retrieves specified version information from the specified version-information resource. To retrieve the appropriate resource, **before you call VerQueryValue, you must first call the**_ [**_GetFileVersionInfoSize_**](https://learn.microsoft.com/en-us/windows/desktop/api/winver/nf-winver-getfileversioninfosizea) **_function, and then the_** [**_GetFileVersionInfo_**](https://learn.microsoft.com/en-us/windows/desktop/api/winver/nf-winver-getfileversioninfoa) **_function._**” This also matches what can be seen from API Monitor.

### Writing the Payload

At this point I now know what name I should give my DLL, and which exported function name to use. It is time to write the malicious code and compile it.

For that, it is only important to mimic the original function signature. In this case, since it comes from a system DLL, the function signature can be found on MSDN.

![](https://www.okiok.com/wp-content/uploads/2024/03/msdn.png)

Due to personal preferences, the current example will be using the Nim-Lang equivalent. Here is the final code:

![](https://www.okiok.com/wp-content/uploads/2024/03/nim-code-final.png)

In this version, nothing is being done in DllMain at initialization, but the local injection code would be executed shortly after “GetFileVersionInfoSizeW” is called.

After compilation, it is a good idea to make sure the DLL correctly exports the desired function:

![](https://www.okiok.com/wp-content/uploads/2024/03/show_export_filtered.png)

### Tricking the compiler

Sometimes, and as it is the case in this example, the compiler will prevent compilation since the target function name being exported is already defined in one of its files:

![](https://www.okiok.com/wp-content/uploads/2024/03/compiler-idiot-filtered.png)

The easy way to circumvent this problem is to temporarily comment that function in the compiler’s file and try again. If cross compiling from Linux, the following file needs to be modified: _/usr/share/mingw-w64/include/winver.h_

![](https://www.okiok.com/wp-content/uploads/2024/03/compiler-tricked-filtered-1.png)

The resulting files:

![](https://www.okiok.com/wp-content/uploads/2024/03/compiled_files.png)

### Conclusion

Using this method, I find it is trivial to successfully implement DLL side-loading in the original process while always avoiding DllMain and its deadlock limitation.

If you have been struggling with this, or just starting out playing with DLL side-loading, I hope this saves you time. Enjoy your shells!

![](https://www.okiok.com/wp-content/uploads/2024/03/beacon.png)

[dll](https://www.okiok.com/tag/dll/), [implant](https://www.okiok.com/tag/implant/), [injection](https://www.okiok.com/tag/injection/), [payload](https://www.okiok.com/tag/payload/), [red team](https://www.okiok.com/tag/red-team/), [red teaming](https://www.okiok.com/tag/red-teaming/), [sideloading](https://www.okiok.com/tag/sideloading/)

![Guillaume Caillé](https://www.okiok.com/wp-content/litespeed/avatar/05c911273f8738d2141d8876ff7ddc4e.jpg?ver=1770953738)

[Guillaume Caillé](https://www.okiok.com/author/gcaille/)

- [Get in touch with me via email](mailto:gcaille@okiok.com "Get in touch with me via email")

### Leave a Comment  [Cancel reply](https://www.okiok.com/achieving-dll-side-loading-in-the-original-process/\#respond)

Save my name, email, and website in this browser for the next time I comment.

Alternative:

WPA

- [![](https://www.okiok.com/wp-content/uploads/2016/08/performe_signature_entreprises_renv.png)](https://www.economie.gouv.qc.ca/accueil/?no_cache=1)
- [![](https://www.okiok.com/wp-content/uploads/2019/03/intertek-iso-9001-2015.png)](http://www.intertek.com/auditing/iso-9001/)
- [![](https://www.okiok.com/wp-content/uploads/2025/06/aicpa-soc.png)](https://www.aicpa.org/soc4so)
- [![](https://www.okiok.com/wp-content/uploads/2016/08/bureau-securite-publique.png)](http://www.bureausecuriteprivee.qc.ca/)
- [![](https://www.okiok.com/wp-content/uploads/2016/08/rss-1.png)](https://www.okiok.com/feed/rss/)

RAC/M, RAC/M Identity, S-Filer, S-Filer Portal, S-Filer Cloud and Okiok MDR are registered trademarks of OKIOK Data ltd.
All other trademarks are the property of their respective owners.
© 2026 OKIOK.

Start typing and press Enter to search