# https://github.com/racoten/ReflectivePluginLoader

[Skip to content](https://github.com/racoten/ReflectivePluginLoader#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/racoten/ReflectivePluginLoader) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/racoten/ReflectivePluginLoader) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/racoten/ReflectivePluginLoader) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/racoten/ReflectivePluginLoader/branches) [**0** Tags](https://github.com/racoten/ReflectivePluginLoader/tags)

[Go to Branches page](https://github.com/racoten/ReflectivePluginLoader/branches)[Go to Tags page](https://github.com/racoten/ReflectivePluginLoader/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![racoten](https://avatars.githubusercontent.com/u/40224197?v=4&size=40)](https://github.com/racoten)[racoten](https://github.com/racoten/ReflectivePluginLoader/commits?author=racoten)

[Update README.md](https://github.com/racoten/ReflectivePluginLoader/commit/59cc836276c5c371cf02cbbbdaf739ecb9a74fe8)

last monthSep 15, 2026

[59cc836](https://github.com/racoten/ReflectivePluginLoader/commit/59cc836276c5c371cf02cbbbdaf739ecb9a74fe8) · last monthSep 15, 2026

## History

[4 Commits](https://github.com/racoten/ReflectivePluginLoader/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/racoten/ReflectivePluginLoader/commits/main/) 4 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [Include](https://github.com/racoten/ReflectivePluginLoader/tree/main/Include "Include") | [Include](https://github.com/racoten/ReflectivePluginLoader/tree/main/Include "Include") | [Add files via upload](https://github.com/racoten/ReflectivePluginLoader/commit/792d95e62a0f39ddcf5adea937542b4b24441bab "Add files via upload") | last monthSep 15, 2026 |
| [Modules/CmdPlugin](https://github.com/racoten/ReflectivePluginLoader/tree/main/Modules/CmdPlugin "This path skips through empty directories") | [Modules/CmdPlugin](https://github.com/racoten/ReflectivePluginLoader/tree/main/Modules/CmdPlugin "This path skips through empty directories") | [Add files via upload](https://github.com/racoten/ReflectivePluginLoader/commit/792d95e62a0f39ddcf5adea937542b4b24441bab "Add files via upload") | last monthSep 15, 2026 |
| [Testing](https://github.com/racoten/ReflectivePluginLoader/tree/main/Testing "Testing") | [Testing](https://github.com/racoten/ReflectivePluginLoader/tree/main/Testing "Testing") | [Add files via upload](https://github.com/racoten/ReflectivePluginLoader/commit/792d95e62a0f39ddcf5adea937542b4b24441bab "Add files via upload") | last monthSep 15, 2026 |
| [Tools](https://github.com/racoten/ReflectivePluginLoader/tree/main/Tools "Tools") | [Tools](https://github.com/racoten/ReflectivePluginLoader/tree/main/Tools "Tools") | [Add files via upload](https://github.com/racoten/ReflectivePluginLoader/commit/792d95e62a0f39ddcf5adea937542b4b24441bab "Add files via upload") | last monthSep 15, 2026 |
| [CMakeLists.txt](https://github.com/racoten/ReflectivePluginLoader/blob/main/CMakeLists.txt "CMakeLists.txt") | [CMakeLists.txt](https://github.com/racoten/ReflectivePluginLoader/blob/main/CMakeLists.txt "CMakeLists.txt") | [Add files via upload](https://github.com/racoten/ReflectivePluginLoader/commit/792d95e62a0f39ddcf5adea937542b4b24441bab "Add files via upload") | last monthSep 15, 2026 |
| [LICENSE](https://github.com/racoten/ReflectivePluginLoader/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/racoten/ReflectivePluginLoader/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/racoten/ReflectivePluginLoader/commit/7f66a84e65322061be83cca923d27940b4009770 "Initial commit") | last monthSep 14, 2026 |
| [README.md](https://github.com/racoten/ReflectivePluginLoader/blob/main/README.md "README.md") | [README.md](https://github.com/racoten/ReflectivePluginLoader/blob/main/README.md "README.md") | [Update README.md](https://github.com/racoten/ReflectivePluginLoader/commit/59cc836276c5c371cf02cbbbdaf739ecb9a74fe8 "Update README.md") | last monthSep 15, 2026 |
| View all files |

## Repository files navigation

# ReflectivePluginLoader

[Permalink: ReflectivePluginLoader](https://github.com/racoten/ReflectivePluginLoader#reflectivepluginloader)

[![License: MIT](https://camo.githubusercontent.com/08cef40a9105b6526ca22088bc514fbfdbc9aac1ddbf8d4e6c750e3a88a44dca/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d4d49542d626c75652e737667)](https://github.com/racoten/ReflectivePluginLoader/blob/main/LICENSE)

A minimal reflective PE mapper with a hot-swappable plugin interface for Windows x64. Maps a DLL straight from a byte buffer in memory, resolves its exports, and calls into a clean `IPlugin` ABI without touching `LoadLibrary`. Companion code for the blog post on reflective loaders and modular plugin architectures.

## Blog Post

[Permalink: Blog Post](https://github.com/racoten/ReflectivePluginLoader#blog-post)

> See the full writeup: [Using Reflective Loaders to Replace LoadLibrary for Hot-Swappable Modules in C++](https://racoten.gitbook.io/red-team-developments-and-operations#using-reflective-loaders-to-replace-loadlibrary-for-hot-swappable-modules-in-c)

## Quick Start

[Permalink: Quick Start](https://github.com/racoten/ReflectivePluginLoader#quick-start)

```
# Configure
cmake -B build

# Build
cmake --build build --config Release

# The build produces:
#   build/Release/cmdplugin.dll   (example plugin)
#   build/Release/harness.exe     (test harness)
```

## Usage

[Permalink: Usage](https://github.com/racoten/ReflectivePluginLoader#usage)

```
# Map cmdplugin.dll from disk, run "dir C:\"
harness.exe cmdplugin.dll "dir C:\"

# Default: loads cmdplugin.dll, runs "whoami"
harness.exe
```

The harness reads the DLL into a byte buffer, maps it with the reflective loader, resolves the plugin exports, and dispatches the command through the `IPlugin` interface.

## Project Structure

[Permalink: Project Structure](https://github.com/racoten/ReflectivePluginLoader#project-structure)

```
ReflectivePluginLoader/
├── CMakeLists.txt              # Root build
├── Include/
│   ├── IPlugin.h               # Plugin ABI (TaskApi, IPlugin, helpers)
│   └── ReflectiveLoaderEngine.h # PE mapper + export resolver
├── Modules/
│   └── CmdPlugin/
│       ├── cmdplugin.cpp        # Example: command execution plugin
│       └── CMakeLists.txt
├── Testing/
│   ├── main.cpp                 # Test harness (loads DLL from file)
│   └── CMakeLists.txt
└── Tools/
    └── file2hex.py              # Convert a DLL to a C byte array
```

## Writing Your Own Module

[Permalink: Writing Your Own Module](https://github.com/racoten/ReflectivePluginLoader#writing-your-own-module)

1. Create a new directory under `Modules/`.
2. Include `IPlugin.h` and implement the `IPlugin` interface:

```
#include "IPlugin.h"

class MyPlugin : public IPlugin {
public:
    void init() const override { /* setup */ }
    void execute(TaskApi* task) const override { /* do work */ }
    void cleanup() const override { /* teardown */ }
};
```

3. Implement the five exported functions (`create_plugin`, `destroy_plugin`, `plugin_init`, `plugin_exec`, `plugin_cleanup`) using `HeapAlloc`/placement `new` for CRT-safe cross-module allocation.

4. Add a `CMakeLists.txt` and register it in the root `CMakeLists.txt` with `add_subdirectory()`.


The host doesn't need to know what your module does internally. It maps, resolves, calls `init -> execute -> cleanup`, and moves on.

## Known Limitations

[Permalink: Known Limitations](https://github.com/racoten/ReflectivePluginLoader#known-limitations)

The mapper handles the basics and deliberately stops there:

- **Supported:** Base relocations, import resolution, per-section memory protections
- **Not supported:** TLS callbacks, delay-load imports, forwarded exports, CFG metadata, SEH table registration

If a module needs any of those, either extend the mapper or reject the module early with a clear error. Silent half-support is the worst failure mode.

## References

[Permalink: References](https://github.com/racoten/ReflectivePluginLoader#references)

- [stephenfewer/ReflectiveDLLInjection](https://github.com/stephenfewer/ReflectiveDLLInjection) \- The original reflective loader
- [ired.team - Reflective DLL Injection](https://www.ired.team/offensive-security/code-injection-process-injection/reflective-dll-injection) \- Walkthrough and PoC
- [fancycode/MemoryModule](https://github.com/fancycode/MemoryModule) \- Full-featured "load DLL from memory" library
- [PE Format (Microsoft)](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format) \- PE/COFF specification

## License

[Permalink: License](https://github.com/racoten/ReflectivePluginLoader#license)

[MIT](https://github.com/racoten/ReflectivePluginLoader/blob/main/LICENSE)

## About

A minimal PE mapper that loads DLLs straight from memory and calls into a clean plugin interface, no LoadLibrary needed.

### Resources

[Readme](https://github.com/racoten/ReflectivePluginLoader#readme-ov-file)

[Unlicense](https://github.com/racoten/ReflectivePluginLoader#Unlicense-1-ov-file)

[Activity](https://github.com/racoten/ReflectivePluginLoader/activity)

### Stars

**49** stars

### Watchers

**0** watching

### Forks

[**5** forks](https://github.com/racoten/ReflectivePluginLoader/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fracoten%2FReflectivePluginLoader&report=racoten+%28user%29)

## [Releases](https://github.com/racoten/ReflectivePluginLoader/releases)

No releases published

## [Contributors](https://github.com/racoten/ReflectivePluginLoader/graphs/contributors) 1 (1)

- [![@racoten](https://avatars.githubusercontent.com/u/40224197?s=64&v=4)](https://github.com/racoten) [**racoten**](https://github.com/racoten)

## Languages

- [C++89.1%](https://github.com/racoten/ReflectivePluginLoader/search?l=c%2B%2B)
- [Python6.4%](https://github.com/racoten/ReflectivePluginLoader/search?l=python)
- [CMake4.5%](https://github.com/racoten/ReflectivePluginLoader/search?l=cmake)

You can’t perform that action at this time.