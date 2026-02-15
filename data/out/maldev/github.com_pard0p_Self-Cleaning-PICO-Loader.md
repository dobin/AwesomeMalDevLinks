# https://github.com/pard0p/Self-Cleaning-PICO-Loader

[Skip to content](https://github.com/pard0p/Self-Cleaning-PICO-Loader#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/pard0p/Self-Cleaning-PICO-Loader) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/pard0p/Self-Cleaning-PICO-Loader) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/pard0p/Self-Cleaning-PICO-Loader) to refresh your session.Dismiss alert

{{ message }}

[pard0p](https://github.com/pard0p)/ **[Self-Cleaning-PICO-Loader](https://github.com/pard0p/Self-Cleaning-PICO-Loader)** Public

- [Notifications](https://github.com/login?return_to=%2Fpard0p%2FSelf-Cleaning-PICO-Loader) You must be signed in to change notification settings
- [Fork\\
3](https://github.com/login?return_to=%2Fpard0p%2FSelf-Cleaning-PICO-Loader)
- [Star\\
48](https://github.com/login?return_to=%2Fpard0p%2FSelf-Cleaning-PICO-Loader)


Self-cleaning in-memory PICO loader for Crystal Palace. Automatically erases traces and operates entirely in memory for stealthy payload execution.


### License

[MIT license](https://github.com/pard0p/Self-Cleaning-PICO-Loader/blob/main/LICENSE)

[48\\
stars](https://github.com/pard0p/Self-Cleaning-PICO-Loader/stargazers) [3\\
forks](https://github.com/pard0p/Self-Cleaning-PICO-Loader/forks) [Branches](https://github.com/pard0p/Self-Cleaning-PICO-Loader/branches) [Tags](https://github.com/pard0p/Self-Cleaning-PICO-Loader/tags) [Activity](https://github.com/pard0p/Self-Cleaning-PICO-Loader/activity)

[Star](https://github.com/login?return_to=%2Fpard0p%2FSelf-Cleaning-PICO-Loader)

[Notifications](https://github.com/login?return_to=%2Fpard0p%2FSelf-Cleaning-PICO-Loader) You must be signed in to change notification settings

# pard0p/Self-Cleaning-PICO-Loader

main

[**1** Branch](https://github.com/pard0p/Self-Cleaning-PICO-Loader/branches) [**0** Tags](https://github.com/pard0p/Self-Cleaning-PICO-Loader/tags)

[Go to Branches page](https://github.com/pard0p/Self-Cleaning-PICO-Loader/branches)[Go to Tags page](https://github.com/pard0p/Self-Cleaning-PICO-Loader/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![pard0p](https://avatars.githubusercontent.com/u/79936108?v=4&size=40)](https://github.com/pard0p)[pard0p](https://github.com/pard0p/Self-Cleaning-PICO-Loader/commits?author=pard0p)<br>[Add LICENSE file](https://github.com/pard0p/Self-Cleaning-PICO-Loader/commit/0251f35158787ef19780d98168d15526cdfffcbc)<br>4 months agoNov 2, 2025<br>[0251f35](https://github.com/pard0p/Self-Cleaning-PICO-Loader/commit/0251f35158787ef19780d98168d15526cdfffcbc) · 4 months agoNov 2, 2025<br>## History<br>[9 Commits](https://github.com/pard0p/Self-Cleaning-PICO-Loader/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/pard0p/Self-Cleaning-PICO-Loader/commits/main/) 9 Commits |
| [images](https://github.com/pard0p/Self-Cleaning-PICO-Loader/tree/main/images "images") | [images](https://github.com/pard0p/Self-Cleaning-PICO-Loader/tree/main/images "images") | [Initial commit](https://github.com/pard0p/Self-Cleaning-PICO-Loader/commit/31971d622d1e9247e52f1287d90f4effdb076eb9 "Initial commit") | 4 months agoOct 28, 2025 |
| [simple\_obj\_self\_cleaning](https://github.com/pard0p/Self-Cleaning-PICO-Loader/tree/main/simple_obj_self_cleaning "simple_obj_self_cleaning") | [simple\_obj\_self\_cleaning](https://github.com/pard0p/Self-Cleaning-PICO-Loader/tree/main/simple_obj_self_cleaning "simple_obj_self_cleaning") | [Adding a comment](https://github.com/pard0p/Self-Cleaning-PICO-Loader/commit/b4a7451b4053d515a8f081b1b9001eab4292c5dd "Adding a comment") | 4 months agoNov 1, 2025 |
| [LICENSE](https://github.com/pard0p/Self-Cleaning-PICO-Loader/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/pard0p/Self-Cleaning-PICO-Loader/blob/main/LICENSE "LICENSE") | [Add LICENSE file](https://github.com/pard0p/Self-Cleaning-PICO-Loader/commit/0251f35158787ef19780d98168d15526cdfffcbc "Add LICENSE file") | 4 months agoNov 2, 2025 |
| [README.md](https://github.com/pard0p/Self-Cleaning-PICO-Loader/blob/main/README.md "README.md") | [README.md](https://github.com/pard0p/Self-Cleaning-PICO-Loader/blob/main/README.md "README.md") | [Changing the way we get the start address](https://github.com/pard0p/Self-Cleaning-PICO-Loader/commit/35a514b4b4fb23b1e78446cc721e879bf5781c9f "Changing the way we get the start address") | 4 months agoNov 1, 2025 |
| View all files |

## Repository files navigation

# Self-Cleaning PICO Loader for Crystal Palace

[Permalink: Self-Cleaning PICO Loader for Crystal Palace](https://github.com/pard0p/Self-Cleaning-PICO-Loader#self-cleaning-pico-loader-for-crystal-palace)

This loader demonstrates advanced in-memory self-cleaning techniques for offensive tooling. It dynamically determines its own start and end addresses in memory, enabling complete removal of the loader after execution.

## Dynamic Loader Boundaries

[Permalink: Dynamic Loader Boundaries](https://github.com/pard0p/Self-Cleaning-PICO-Loader#dynamic-loader-boundaries)

To obtain the base and end addresses of the injected PICO loader in memory:

- The loader is built with a small, empty file appended at the end (see `pic_end.o` in the loader spec).
- The base address is determined by using the address of the entry point function (`go`) directly through `getPicStart()`.
- The end address is determined by referencing the appended empty section through `getPicEnd()`.

## Memory Erasure Using Sleep Obfuscation Technique

[Permalink: Memory Erasure Using Sleep Obfuscation Technique](https://github.com/pard0p/Self-Cleaning-PICO-Loader#memory-erasure-using-sleep-obfuscation-technique)

With both addresses, the loader can:

- Erase and free its own memory region after payload execution.
- The sleep obfuscation technique (e.g., Ekko) is adapted here to enable complete removal of the PICO loader from process memory. Instead of obfuscating and sleeping, the technique is modified to zero and release the loader memory entirely.

## Key Steps

[Permalink: Key Steps](https://github.com/pard0p/Self-Cleaning-PICO-Loader#key-steps)

1. **Dynamic Address Discovery:**
   - `getPicStart()` function returns the loader's base address using the entry point function address.
   - `getPicEnd()` function returns the end address via the appended empty section.
2. **Self-Cleaning:**
   - The loader sets its memory to RW, zeroes it, and frees it using timer-based ROP gadgets.
   - No traces remain in the process memory after execution.

## Moneta Analysis: Loader Comparison

[Permalink: Moneta Analysis: Loader Comparison](https://github.com/pard0p/Self-Cleaning-PICO-Loader#moneta-analysis-loader-comparison)

Below are two screenshots from Moneta showing the memory regions after payload execution:

### Default PICO Loader

[Permalink: Default PICO Loader](https://github.com/pard0p/Self-Cleaning-PICO-Loader#default-pico-loader)

[![Default Loader](https://github.com/pard0p/Self-Cleaning-PICO-Loader/raw/main/images/default_loader.png)](https://github.com/pard0p/Self-Cleaning-PICO-Loader/blob/main/images/default_loader.png)_After execution, RWX regions containing the payload remain in the process memory._

### Self-Cleaning PICO Loader

[Permalink: Self-Cleaning PICO Loader](https://github.com/pard0p/Self-Cleaning-PICO-Loader#self-cleaning-pico-loader)

[![Self-Cleaning Loader](https://github.com/pard0p/Self-Cleaning-PICO-Loader/raw/main/images/self_cleaning_loader.png)](https://github.com/pard0p/Self-Cleaning-PICO-Loader/blob/main/images/self_cleaning_loader.png)_After execution, RWX regions with the payload disappear, leaving no traces, and the process continues running normally._

This demonstrates the effectiveness of the self-cleaning technique: the loader fully erases and frees its own memory, unlike the default loader which leaves potentially detectable regions in memory.

* * *

## References

[Permalink: References](https://github.com/pard0p/Self-Cleaning-PICO-Loader#references)

- Sleep obfuscation based in [Ekko technique](https://github.com/Crystallize-Ekko/Ekko)
- [Crystal Palace](https://tradecraftgarden.org/crystalpalace.html)

## Warning: Control Flow Guard (CFG)

[Permalink: Warning: Control Flow Guard (CFG)](https://github.com/pard0p/Self-Cleaning-PICO-Loader#warning-control-flow-guard-cfg)

When injecting into processes with Control Flow Guard (CFG) enabled, a bypass is required for successful execution of self-cleaning or sleep-obfuscation techniques. For details and implementation, see: [https://github.com/Crypt0s/Ekko\_CFG\_Bypass/tree/main](https://github.com/Crypt0s/Ekko_CFG_Bypass/tree/main)

## About

Self-cleaning in-memory PICO loader for Crystal Palace. Automatically erases traces and operates entirely in memory for stealthy payload execution.


### Topics

[shellcode](https://github.com/topics/shellcode "Topic: shellcode") [evasion](https://github.com/topics/evasion "Topic: evasion") [pico](https://github.com/topics/pico "Topic: pico") [crystal-palace](https://github.com/topics/crystal-palace "Topic: crystal-palace")

### Resources

[Readme](https://github.com/pard0p/Self-Cleaning-PICO-Loader#readme-ov-file)

### License

[MIT license](https://github.com/pard0p/Self-Cleaning-PICO-Loader#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/pard0p/Self-Cleaning-PICO-Loader).

[Activity](https://github.com/pard0p/Self-Cleaning-PICO-Loader/activity)

### Stars

[**48**\\
stars](https://github.com/pard0p/Self-Cleaning-PICO-Loader/stargazers)

### Watchers

[**0**\\
watching](https://github.com/pard0p/Self-Cleaning-PICO-Loader/watchers)

### Forks

[**3**\\
forks](https://github.com/pard0p/Self-Cleaning-PICO-Loader/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fpard0p%2FSelf-Cleaning-PICO-Loader&report=pard0p+%28user%29)

## [Releases](https://github.com/pard0p/Self-Cleaning-PICO-Loader/releases)

No releases published

## [Packages\  0](https://github.com/users/pard0p/packages?repo_name=Self-Cleaning-PICO-Loader)

No packages published

## Languages

- [C96.0%](https://github.com/pard0p/Self-Cleaning-PICO-Loader/search?l=c)
- [Makefile3.3%](https://github.com/pard0p/Self-Cleaning-PICO-Loader/search?l=makefile)
- [Ruby0.7%](https://github.com/pard0p/Self-Cleaning-PICO-Loader/search?l=ruby)

You can’t perform that action at this time.