# https://tradecraftgarden.org/docs.html

Tradecraft Garden

## Crystal Palace Documentation

### 1\. Overview

#### 1.1 What is Crystal Palace?

Crystal Palace is a linker and linker script language specialized to the needs of position-independent code tradecraft.

The name is inspired by [The Crystal Palace](https://www.popsci.com/technology/crystal-palace-mystery/), a former cast-iron and glass structure built in London for the Great Exhibition of 1851. At the time, it was the world's largest building. The Crystal Palace adopted a standard size and thread for screws and demonstrated the efficiency gains from building with a standard.

Like The Crystal Palace, this project solves common problems turning tradecraft ideas into position-independent capability code.

Features include:

- Append multiple resources to position-independent code (PIC) and access them as symbols linked to the code
- Run COFFs from position-independent code (Crystal Palace's PICO convention)
- Mask, encrypt, and calculate embeddable checksums for resources
- Assign user-supplied data to global symbols within PICOs and PIC
- Separate .spec files and programs into modules that are callable from other modules
- Ergonomic PIC development options for Win32 API resolution, use of strings, and to handle x86-weirdness
- Shared library model to merge functionality into COFF and PIC programs
- Instrument PIC/PICO programs with powerful self-hooking tools, optimize IAT hooks to specific DLLs
- Transform programs with link-time optimization, block shuffling, and code mutation
- Generate high-fidelity Yara rules for invariant parts of PIC and PICO programs
- Error and condition checking specific to the needs of position-independent code projects

#### 1.2 Goal: Separate Capability from Tradecraft

The goal of Tradecraft Garden and Crystal Palace is to separate evasion tradecraft from capability. This requires:

- Conventions to develop tradecraft, capability, and libraries that are compatible with each other.
- Software design patterns for isolated development and recombination of components
- A development, test, and demonstration model that is use-case agnostic

This project is solving for these needs.

#### 1.3 The Common Convention

[PICOs](https://tradecraftgarden.org/docs.html#picos), which are Cobalt Strike BOFs without the API, are Crystal Palace's standard container for position-independent code, loader-ready COFF, and shared libraries that work in both contexts. [LibTCG](https://tradecraftgarden.org/libtcg.html) is an example of a [shared library](https://tradecraftgarden.org/docs.html#lib). The [Community Pavilion](https://tradecraftgarden.org/references.html) has several other libraries written to these conventions.

#### 1.4 Tradecraft and Capability Pairings

This project provides tools to add tradecraft to capability containerized as DLLs, PIC, PICOs, and BOFs:

Self-bootstrapping memory-injected DLLs are DLL capabilities paired with DLL loaders. These loaders place the DLL capability in memory and use import hooks to change its runtime behavior. Most [Tradecraft Garden](https://tradecraftgarden.org/tradecraft.html) examples are DLL loaders.

Crystal Palace has a pattern to separate [PIC](https://tradecraftgarden.org/docs.html#pic) from boostrap tradecraft to find Win32 APIs and restore global variables. The pattern is to merge a services module with a PICO and use [PIC ergonomic tools](https://vimeo.com/1126841810) to weave them together. [Simple PIC](https://tradecraftgarden.org/simplepic.html) demonstrates this pattern.

PICOs (and PIC written as PICOs) are pairable with runtime tradecraft to change their behaviors and plug-in features. The pattern is to merge the tradecraft and use attach/redirect to [weave](https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/) the tradecraft into the capability. Crystal Palace's [modular .spec files](https://aff-wg.org/2025/12/01/tradecraft-orchestration-in-the-garden/) encourage base projects that use tradecraft specified at time-of-use. [Simple Loader (Hooking)](https://tradecraftgarden.org/simplehook.html) demonstrates this.

[Beacon Object Files](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_main.htm) are pairable with tradecraft too. Create a .spec file to merge tradecraft with a BOF. `make coff` will output a COFF. Use attach and redirect to update the BOF to use the tradecraft. This pattern creates questions about the role of a C2 agent. Should agent's provide tradecraft for everything they may run? Or, is it better to keep an agent light and let BOFs bring their own tradecraft? Daniel Duggan's [BOF Cocktails](https://rastamouse.me/bof-cocktails/) blog post discusses this idea.

#### 1.5 Use-case Agnostic Demonstration

All of the Tradecraft Garden examples are [demonstrated](https://tradecraftgarden.org/docs.html#demo) in a use-case agnostic way with a "Hello World" message box DLL or PICO. This is the tradecraft POC equivalent of "popping calc".

### 2\. Definitions

#### 2.1 DLL loaders

Many Windows offensive security tools and research POCs are compiled as Windows DLLs and rely on bespoke DLL loaders, usually packaged with the capability, to parse the DLL, set it up in memory, and pass execution to it.

The benefit of a bespoke DLL loader is to make the capability less observable to the operating system and security products. For a long time, this common practice did just that. Capabilities loaded this way were virtually invisible.

Post-2016, significant industry effort has gone into detection and mitigation ideas that target this practice. Memory injection with a DLL loader is a [classic example](https://www.youtube.com/watch?v=RoqVunX_sqA) of a former evasion, becoming the source of tells to identify weird on a compromised host AND to flag benign behavior happening from a weird context.

Similarly, much effort has gone into playing with the tells related to memory injection, finding new ways to achieve the same outcomes (without the same visibility), and pushing back on the instrumentation providing the visibility. When this happens in the public, it's a good thing, as it informs better security solutions and ideas, and takes the low hanging fruit "offense wins" off of the table.

#### 2.2 PICO loaders

Crystal Palace also supports loading capability written as PICOs (Crystal Palace COFF) as an alternative to DLLs. The benefits of PICOs over DLLs:

- They're smaller
- You know exactly what's in them
- You have full control over how their code and data live in memory, relative to each other
- And, you can transform PICO capabilities with Crystal Palace's link-time optimization, function order shuffling, and code mutation

Whether a capability is written as a PICO or DLL, the goal of Tradecraft Garden (and Crystal Palace) is to explore building load and run-time memory evasion tradecraft into position-independent loaders that are separate and agnostic to the capability they are applied to.

#### 2.3 Position-independent Code

Capability loaders are often written as position-independent code. That is, a blob of data one can load into memory, start execution from position 0, and the right things will happen.

In the distant past position-independent code was often written as hand-optimized assembly.

Today, it's [more common to write code in C](https://web.archive.org/web/20210305190309/http://www.exploit-monday.com/2013/08/writing-optimized-windows-shellcode-in-c.html), compile it into some form (e.g., a DLL or a COFF), and use a program like objcopy to extract the .text section from the built file. This .text section is where the executable code lives.

Writing code this way requires a lot of special care, because the compiler and linker do not know you intend to sever the executable stuff from the linker and loader-populated function references, data, and other stuff expected by the compiler's output.

When you extract a .text section, what you have is a series of things for the CPU to do. You don't have access to any APIs, C runtime functions, or embedded data (e.g., string constants). You also don't have access to global variables.

Each of the above can be overcome with special care. Later in this document, we'll go over Crystal Palace features that can help with Position Independent Code. This document will also cover some aspects of how to write code without Crystal Palace's "magic".

#### 2.4 Linking

The purpose of a linker is to parse compiler output (object files) and put them together to meet the expected contract of whatever loader will execute the final program. For Windows, this is usually a DLL or executable.

Crystal Palace is different. While it does combine object files and merge them into something to run, the end goal of Crystal Palace is to generate outputs that execute as position-independent code without the aid of the operating system's loader.

The Crystal Palace specification language aims to give precise control over how object files are combined, transformed (aka, used as PIC, executed from COFF), and packaged.

#### 2.5 Specification Files

The Crystal Palace linker is driven by [specification files](https://tradecraftgarden.org/docs.html#specfiles). These files are Crystal Palace's linker script.

There is no default specification file or script. Every Crystal Palace project has a specification to describe how to assemble, transform, and link resources into a ready-to-run position-independent code blob.

The Tradecraft Garden has multiple examples of DLL and Object (COFF) loaders and Crystal Palace specification files. Each of the "Simple Loader" projects demonstrates different Crystal Palace features.

#### 2.6 DLL and COFF Expectations

Crystal Palace is agnostic to any contract between a DLL capability and any specific loader. That said, here are the DLL assumptions of the Tradecraft Garden loaders:

- A standard Windows DLL with an entry point of DllMain
- The Windows DLL is not transformed, mangled, obfuscated or otherwise altered.
- Only `DllMain(hDll, DLL_PROCESS_ATTACH, NULL)` is needed to start the capability
- The capability is single-threaded

A C2 framework may export DLLs that (likely) do not adhere to the above assumptions. Compatibility with any specific C2 is not a goal of the Tradecraft Garden projects.

COFFs passed to Crystal Palace, as capabilities, are expected to adhere to [PICO conventions](https://tradecraftgarden.org/docs.html#picos).

### 3\. Install and Build

#### 3.1 Requirements

Crystal Palace is written in Java and requires a modern-ish [Java runtime environment](https://openjdk.org/). OpenJDK 11 or later is likely OK.

The Tradecraft Garden examples have Makefiles for the [MinGW-w64 compiler environment](https://www.mingw-w64.org/).

The Crystal Palace demonstration programs also build with MinGW-w64.

Crystal Palace's included scripts and the Tradecraft Garden Makefiles assume a Linux environment.

Fortunately, [Windows Subsystem for Linux](https://tradecraftgarden.org/wslsetup.html) is an excellent host for these dependencies and workflows. Follow the [setup guide](https://tradecraftgarden.org/wslsetup.html) to create a Crystal Garden/TCG WSL environment that meets these requirements.

While it's possible these projects are workable with other compilers and environments, no accommodation is made for these other environments. Beware.

#### 3.2 Installation

To install Crystal Palace, extract the Crystal Palace distribution to its preferred home:

tar zxvf cpdistYYYYMMDD.tgz

That's it. There are no other steps.

#### 3.3 Building Crystal Palace

Crystal Palace is built with [Apache Ant](https://ant.apache.org/). To build Crystal Palace, use:

ant clean ; ant

The above will produce a crystalpalace.jar file. The other needed scripts (e.g., link) are included in the source and pre-built distributions of Crystal Palace.

#### 3.4 Building Crystal Palace Demonstration Tools

The `demo/` folder of Crystal Palace includes a few C programs to aid working with the Tradecraft Garden examples.

Change to the `demo/` folder.

cd demo

And, run `make` to build the demonstration programs:

make clean ; make

### 4\. CLI Usage

#### 4.1 Command-line Use

The Crystal Palace linker is usable from the command-line via the `link` command (Linux) and `java -jar crystalpalace.jar`. Run either command with no arguments to see the latest help message:

![](https://tradecraftgarden.org/ss_args.jpg)

The most typical use of Crystal Palace is:

./link \[/path/to/loader.spec\] \[file.dll\|.o\] \[out.bin\]

This use will parse and apply the commands in loader.spec to build a position-independent code package, saved as out.bin, that loads and executes the specified Win32 DLL (or PICO COFF).

Crystal Palace will parse the specified DLL (e.g., file.dll) and use its architecture to determine which target label to call within the specification file. These will come up later. For now, target labels are commands specific to an architecture (e.g., x86, x64, etc.).

If a DLL is passed to ./link, Crystal Palace sets `$DLL` to the contents of the file.

If a COFF is passed to ./link, Crystal Palace sets `$OBJECT` to the contents of the file.

These byte array values are referenced as `$KEY` in specification files.

#### 4.2 Passing byte\[\] arguments

It's possible to pass other `$KEY=[value]` arguments via the command-line too.

The syntax for passing these arguments is:

./link \[/path/to/loader.spec\] \[file.dll\] \[out.bin\] \[KEY=value\] \[KEY2=value\] \[...\]

When you pass variables to Crystal Palace via the command-line, do not prefix `KEY` with `$`. Crystal Palace will do this for you.

Crystal Palace expects that each `$KEY` in its execution environment is a byte\[\] array. Specify this on the command-line as a string of hex digits.

Crystal Palace does not have awareness of the C type of these bytes. If you use the $KEY mechanism to pass a pointer or DWORD, you are responsible for specifying the bytes in the right order for the target architecture. In practice, x86 and x64 targets are little-endian byte order.

As an example:

./link loader.spec file.dll out.bin NUMBER=04030201

The above populates `$NUMBER` with the value of 0x01020304, assuming it's used as a DWORD from your C code.

#### 4.3 Passing variable arguments

Some Crystal Palace specification files expect user-specified %variable strings to provide needed details to a project. There are several ways to pass these strings:

./link \[/path/to/loader.spec\] \[file.dll\] \[out.bin\] \[%var="value"\] \[-r %files="a, b, c"\]

You may specify a %variable value with the `%var="value"` syntax on the CLI. Crystal Palace's next and foreach commands act on %variable arrays. These are just a comma-separated list of values (e.g., a, b, c).

Finally, there is the case of `-r %files="a, b, c"`. This is the resolve flag. It tells Crystal Palace's CLI to walk the values in %files and resolve their paths relative to the current working directory. This is necessary as Crystal Palace always interprets partial file paths relative to the location of the current .spec file. In a modular linking project, with files and resources scattered everywhere, this deliberate path resolution is sometimes necessary.

#### 4.4 Configuration files

Another way to pass `$KEY` and `%var` information is through Crystal Palace configuration files. These are Crystal Palace specification files and have access to all Crystal Palace commands. But, largely, their purpose is to use commands like setg, pack, and resolve to configure values for another project.

To specify a configuration file on the Crystal Palace CLI, prefix the filename with @:

./link \[/path/to/loader.spec\] \[file.dll\] \[out.bin\] \[@config.spec\] \[@config2.spec\]

Here's an example Crystal Palace configuration file:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15 | `x64:`<br>```# set the global variable %key to "Hello World"`<br>```setg``"%key"``"Hello World"`<br>```# pack the 4-byte integer 0x31337 and wchar_t* string into $VAR`<br>```pack $VAR``"iZ"``"0x31337"``"This is a UTF-16LE string"`<br>```# set some partial paths in %files`<br>```setg``"%files"``"content/a.txt, content/b.txt"`<br>```# use resolve (like -r) to resolve %files paths relative to this .spec`<br>```resolve``"%files"`<br>```# use echo to print any of these values`<br>```echo``"Files: "``%files` |

`x64:` is a program label to group commands run for x64 `$DLL` or `$OBJECT` capabilities.

`setg` sets a global variable, visible through this whole linking session, to a string value.

`pack` marshals its arguments into a _$VAR_ using a [template string](https://tradecraftgarden.org/docs.html#pack) to specify their type/interpretation.

`resolve` is the same as the -r CLI option. It walks the specified variable and resolves each of its paths relative to the config.spec file.

Crystal Palace commands that set or update a variable require you to quote the variable name. This is because the literal variable name is the argument and not its value.

#### ⦿ Hooking Crystal Palace commands

One last configuration-specific oddity is `before`. This command hooks a Crystal Palace command and executes another command before it runs. This is a way to get visibility in a project (e.g., coffparse, disassemble, echo), override its configuration (e.g., rule, set, etc.), or include commands (e.g., call, run) without editing its .spec files.

before sets these arguments for its hooks:

- `%_` is the command+arguments of the hooked command.
- %1 .. % _n_ are set to the individual arguments.

Recipe 1: Disassemble code before export

`before "export" : disassemble "code.txt"`

Recipe 2: Turn on evasive options before export. Useful with `-g` for generating Yara rules.

`before "export" : options +regdance +mutate`

#### 4.5 Pack Reference

`pack` is Crystal Palace's command to marshal arguments into a byte array `$VARIABLE`. The syntax is:

`pack $VARIABLE "template" arg1 arg2 arg3`

Each argument is interpreted and formatted as dictated by its corresponding template character.

Numerical and multi-byte ('Z') characters are packed in little-end byte order.

Number arguments are decimal (by default), 0xhex, and 0octal. Positive numbers up to the full unsigned-size of the type are accepted. Negative numbers up to the minimum negative value of the type are accepted.

Here is the pack command reference:

| Template | Argument | Type | Size (b) | Notes |
| --- | --- | --- | --- | --- |
| b | $VAR | byte string | _var_ |  |
| i | number | int | 4 |  |
| l | number | long | 8 |  |
| p | number | pointer | 4, 8 | size is arch dependent |
| s | number | short | 2 |  |
| x | No arg | NULL byte! | 1 |  |
| z | "string" | UTF8 string | _var_ | string is null-terminated |
| Z | "string" | UTF16-LE string | _var_ | string is null-terminated |
| @4, @8, @n | No arg | NULL byte(s) | _var_ | Align packed string to 4, 8, or architecture's natural boundary bytes. |
| # _t_ | _var_ | int | _var_ | Process template _t_ and prepend 4-byte length to it |

#### 4.6 Argument passing examples

The Tradecraft Garden has two examples that highlight the benefit of argument passing:

- [Simple Loader (Pointer Patching)](https://tradecraftgarden.org/simplepatch.html) demonstrates how to avoid Export Address Filtering-like mitigations by passing GetProcAddress and LoadLibraryA pointers to a loader, if they're already known.
- [Simple Loader (Execution Guardrails)](https://tradecraftgarden.org/simpleguard.html) demonstrates encrypting the DLL and follow-on resources with an environment-derived secret key. It also relies on a `%NEXT` variable to specify a follow-on stage 2 specification file.

#### 4.7 Yara Rule Generator

Add `-g "outfile.yar"` to ./link to generate Yara rules alongside the linker output. There's a [Java API](https://tradecraftgarden.org/api/crystalpalace/spec/LinkSpec.html#runAndGenerate(crystalpalace.spec.Capability,java.util.Map)) for this too.

Crystal Palace's rule command gives advice to the Yara rule generator. This command is optional.

`rule "name" [max] [minAgree] [minLen-maxLen] ["funcA, ..."]`

"name" sets the Yara rule's name. If name is empty (e.g., ""), the rule generator will derive a name.

max sets how many signatures Crystal Palace allows within a rule. Crystal Palace scores candidate signatures and selects the best ones. This score favors instructions that are information dense or contain unique constants. The default is 10.

Set max to 0 to disable signature generation for a piece of a project.

minAgree is the number of signatures that must agree for a rule to match a sample. If the number of signatures generated is less than minAgree, Crystal Palace will require all of the signatures to fire.

minLen-maxLen sets the minimum and maximum non-wildcarded bytes in a signature. The default range is 10-16.

"funcA, ..." is a list of functions to generate signatures from. By default, Crystal Palace considers all functions in scope.

The rule generator is scoped to object code (e.g., the .text section) of a program only. It does not generate signatures from .rdata constants (strings) and it does not look at appended shellcode (e.g., linkfunc).

#### 4.8 Other Commands

The Crystal Palace distribution includes a few other utilities.

The `coffparse` command parses a .o file and prints information about it. This is a good way to understand how Crystal Palace sees your program.

The `disassemble` command disassembles the code in a .o file and prints it as plaintext.

`piclink` is like `link` but it doesn't accept a COFF or DLL argument. It assembles a PIC project, based on what's in a specification file.

### 5\. Demonstrating Tradecraft

#### 5.1 Demonstration Programs

Crystal Palace ships with demonstration programs in the `demo/` folder.

The demonstration programs include:

`run.x86.exe` and `run.x64.exe`. These projects inject a position-independent capability loader package into memory and pass execution to it. When either program is run by itself, they will display their arguments, and `KEY=value` output needed by some of the Tradecraft Garden Simple Loaders.

`test.x86.dll` and `test.x64.dll` are simple Windows DLLs that show a "Hello World" message box.

`test.x86.o` and `test.x64.o` are simple PICO COFFs that show a "Hello World" message box.

![](https://tradecraftgarden.org/ss_run_noargs.jpg)

The x86 and x64 variations of the run and test programs denote the architecture each was built for. Do not mix an x86 DLL with an x64 runner.

The run.exe programs are not a test environment for position-independent capability loaders. That's outside the scope of this project. Further, the test DLLs are not a stress test or simulation of things a follow-on DLL might do.

The purpose of these demonstration programs is to quickly show that something can run with a tradecraft applied to it. In this way, these programs are like the vulnerability proof-of-concept convention of "popping calc" to demonstrate successful code execution.

#### 5.2 A demonstration of the demonstration programs

Here's a quick walk-through of using the demonstration programs with a Tradecraft Garden project:

1\. Pair test.x64.dll with a DLL loader

./link /path/to/loader.spec demo/test.x64.dll out.x64.bin

2\. Run out.x64.bin with run.x64.exe

demo/run.x64.exe out.x64.bin

That's it.

![](https://tradecraftgarden.org/ss_demo.jpg)

### 6\. Java API

#### 6.1 Overview

Java applications may embed the Crystal Palace linker via its Java API.

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43 | `import``crystalpalace.spec.Capability;`<br>`import``crystalpalace.spec.LinkSpec;`<br>`import``crystalpalace.spec.SpecLogger;`<br>`import``crystalpalace.spec.SpecMessage;`<br>`import``crystalpalace.spec.SpecProgramException;`<br>`import``crystalpalace.spec.SpecParseException;`<br>`import``java.util.HashMap;`<br>`public``class``Demo``implements``SpecLogger {`<br>```// act on a log message (e.g., echo command) from Crystal Palace`<br>```public``void``logSpecMessage(SpecMessage message) {`<br>```System.out.println(message.toString());`<br>```}`<br>```public``byte``[] process(String specf,``byte``[] coff_or_dll) {`<br>```try``{`<br>```LinkSpec spec = LinkSpec.Parse(specf);`<br>```// register this class as a SpecLogger for LinkSpec`<br>```spec.addLogger(``this``);`<br>```// turn our coff_or_dll argument into a Capability object`<br>```Capability capab = Capability.Parse(coff_or_dll);`<br>```// the second parameter HashMap is an opportunity to pass`<br>```// $KEY=byte[] and %VAR="string" values to the spec program`<br>```return``spec.run(capab,``new``HashMap());`<br>```}`<br>```catch``(SpecParseException parsex) {`<br>```System.out.println(parsex.toString());`<br>```}`<br>```catch``(SpecProgramException progex) {`<br>```System.out.println(progex.toString());`<br>```}`<br>```catch``(java.io.IOException ioex) {`<br>```System.out.println(ioex.getMessage());`<br>```}`<br>```return``new``byte``[``0``];`<br>```}`<br>`}` |

The Java API is the most ergonomic way to use Crystal Palace. A program that embeds this technology can standardize the `$KEY` arguments that are available, document them, and take care to marshal them to well-defined types with the correct byte order.

The API is relatively simple. Use the `Parse` static method of the LinkSpec class to parse a Crystal Palace specification file. If there's an error, this method will throw a `SpecParseException` with detailed information about the parsing errors. The `Parse` method returns a `LinkSpec` object. Use `Capability.Parse` to turn a COFF or DLL byte\[\] argument into a Capability.

Call `run` on the LinkSpec object with your Capability object and a java.util.Map argument, mapping `"$KEY"` to `(byte[])value` and `"%var"` to `(String)value`. If there's an error during the linking process, this method will throw either a `SpecParseException` or a `SpecPorgramException`. Both of these methods have sane `toString` methods that provide a user-friendly representation of the error(s) and their context.

The return value of `run` is your ready-to-go position-independent code blob.

[JavaDoc Generated API documents](https://tradecraftgarden.org/api/crystalpalace/spec/LinkSpec.html) are available for these classes too.

#### 6.2 Limitations

The current Java API has limitations.

When Crystal Palace specifications reference a file (e.g., load, run, etc.)--there's no API accommodation to intercept that reference and resolve it with an application-internal resource.

Also, there is no Crystal Palace API to extend the specification language with new commands specific to the embedding application.

### 7\. Specification Files

#### 7.1 Walk-through

The specification file is interpreted by Crystal Palace to create a ready-to-run position-independent code from one or more COFF and DLL files.

Here's an example specification file:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25 | `# Our specification file. This is a comment`<br>`x86:`<br>```# load our x86 .o file AND turn it into position-independent code`<br>```load``"bin/loader.x86.o"`<br>```make``pic`<br>```# handle any x86 pointer fixes we need, with the help of the _caller function`<br>```fixptrs``"_caller"`<br>```# load our Reflective DLL argument AND link it into our PIC as my_data section`<br>```push $DLL`<br>```link``"my_data"`<br>``<br>```# we're done, export the final blob`<br>```export`<br>`x64:`<br>```load``"bin/loader.x64.o"`<br>```make``pic`<br>```push $DLL`<br>```link``"my_data"`<br>``<br>```export` |

Comments begin with the `#` symbol and go to the end of the line.

Crystal Palace commands ignore whitespace. The indentation is for readability only.

Targets are written as `label:`. Valid targets include x86.o/x64.o (COFF) and x86.dll/x64.dll (DLL). Generic targets (e.g., x86, x64) are used if a more specific target is not defined.

Targets separate build resources and logic for each architecture and capability.

Targets contain commands. Each command works with the program stack, %string variables, and byte\[\] $content variables.

Let's walk-through the x64 target of our example specification file:

![](https://tradecraftgarden.org/stackops.png)

(1) `load "bin/loader.x64.o"` reads the content of bin/loader.x64.o and pushes it onto the stack.

(2) `make pic` pops the loader.x64.o content off the stack and creates an export object configured for position-independent code. This object is not the final position-independent code. It's a malleable COFF-based intermediate form and the configuration details for the program exporter. Many Crystal Palace commands act on these export configuration objects. This object is pushed onto the stack.

(3) `push $DLL` pushes the content of $DLL, a global-scope byte\[\] variable, onto the stack. $DLL was set when we provided a .dll argument to the link CLI or Java API. Both the CLI and Java API allow passing custom $VAR values.

(4) `link "my_data"` pops two values from the stack. The top value is the byte\[\] content. The next value is an export configuration object. The link command updates the export configuration to associate `my_data` with the popped byte\[\] content. Later, when the final program is exported, Crystal Palace will append the content to the program and resolve my\_data relocations with the data's offset. The export configuration object is pushed back onto the stack.

(5) `export` pops the export configuration object and interprets its state to generate our position-independent code. The ready-to-run generated program (byte\[\]) is pushed onto the stack.

After the last command, Crystal Palace pops the generated program from the stack. This is the value written to the CLI output file (or returned by the Java API).

#### 7.2 Command Reference

Below is a full list of Crystal Palace spec file commands and how they impact the Crystal Palace stack. Note that any files paths are resolved relative to the current .spec file.

| Command | Pop | Push | Description |
| --- | --- | --- | --- |
| addhook "MOD$Func" | OBJECT | OBJECT | Register MOD$Func's `attach "MOD$Func" "hook"` chain with \_\_resolve\_hook() intrinsic. |
| addhook "MOD$Func" "hook" | OBJECT | OBJECT | Register MOD$Func hook for use with \_\_resolve\_hook() intrinsic. |
| attach "MOD$Func" "hook" | OBJECT | OBJECT | Rewrite calls and references to MODULE$Function to go through hook(). Preserves MODULE$Function in hook(). |
| before "cmd1": cmd2 %\_ |  |  | Run cmd2 before cmd1 executes. %\_ is set to the command+arguments of cmd1. %1 ... % _n_ are set to the individual arguments |
| call "file.spec" "label" ... |  |  | Calls "label" from another .spec, using the same target, $VARs, and stack as the current script. Accepts positional arguments, passed as %1, %2, etc. |
| coffparse "file.txt" | OBJECT | OBJECT | Parse object on stack and output a string representation to file.txt. The COFF parsing will occur at export, after +options are applied, and before patched values are acted on. |
| dfr "resolver" "method" | OBJECT | OBJECT | **(PIC only)** Sets default dynamic function resolution resolver function. Rewrites MODULE$Function references in PIC to call resolver. ror13 method passes ror13 module and function hashes to resolver. strings method passes module and function stack strings to resolver. |
| dfr "res." "method" "M1, M2" | OBJECT | OBJECT | **(PIC only)** Set dynamic function resolution resolver function for Win32 APIs from MODULE1 and MODULE2. This resolver has priority over the default resolver. |
| disassemble "file.txt" | OBJECT | OBJECT | Disassemble object on stack and write output to file.txt. The disassemble will occur at export, after +options are applied, and before patched values are acted on. |
| echo ... |  |  | print arguments to STDOUT (CLI) or [SpecLogger](https://tradecraftgarden.org/api/crystalpalace/spec/SpecLogger.html) (Java API) |
| export | OBJECT | BYTES | Turn object on stack into bytes |
| exportfunc "fun" "\_\_tag\_fun" | OBJECT | OBJECT | **(PICO only)** Export function from PICO and generate \_\_tag\_function intrinsic (used with PicoGetExport to find func pointer) |
| filterhooks $DLL\|$OBJECT | OBJECT | OBJECT | Walk imports of $DLL or $OBJECT and remove registered hooks for APIs not in import table |
| fixbss "getBSS" | OBJECT | OBJECT | **(PIC only)** Rewrites PIC .bss (uninitialized global variables) references to call `getBSS(size of bss section)` and reference global variables as an offset of the returned pointer. This restores uninitialized global variables in PIC programs. |
| fixptrs "\_caller" | OBJECT | OBJECT | **(x86 PIC only)** Rewrite x86 PIC to turn partial pointers into full pointers with the help of \_caller function. Allows access to strings and linked data without hacks. |
| foreach %var: cmd %\_ |  |  | For each item in %var (comma separated list of strings), run cmd with %\_ set to the current item. |
| generate $VAR ## |  |  | Generate ## random bytes and assign to $VAR |
| import "A, B, C, ..." | OBJECT | OBJECT | Import functions A, B, and C into COFF object.<br>"A, B, C, ..." maps members of IMPORTFUNCS struct passed to `PicoLoader` to function symbols in COFF. First two values are always LoadLibraryA and GetProcAddress. Extend IMPORTFUNCS struct to pass the other pointers |
| load "file" |  | BYTES | Load contents of file onto stack |
| load $VAR "file" |  |  | Load contents of file into $VAR |
| link "section" | BYTES, OBJECT | OBJECT | Link (data) bytes on the stack to section `__attribute__((section("section")))` in object on the stack. |
| linkfunc "symbol" | BYTES, OBJECT | OBJECT | Link (code) bytes on the stack to function symbol in object on stack |
| make coff \[+options\] | BYTES | OBJECT | Turn contents on stack into a COFF-exporter object.<br> <br>Options are +optimize (Link-time optimization), +disco (randomize function order), +mutate (constants mutator), and others |
| make object \[+options\] | BYTES | OBJECT | Turn contents on stack into a PICO-exporter object.<br> <br>Options are +optimize (Link-time optimization), +disco (randomize function order), +mutate (constants mutator), and others |
| make pic \[+options\] | BYTES | OBJECT | Turn contents on stack into PIC-exporter object.<br> <br>Options are +optimize (Link-time optimization), +disco (randomize function order), +mutate (constants mutator), +gofirst (make go the first function), and others |
| merge | BYTES, OBJECT | OBJECT | Merge bytes on stack (COFF content) to object on stack |
| mergelib "lib.x##.zip" | OBJECT | OBJECT | Merges each COFF file within zip archive to object on stack |
| meta "verb" "value" |  |  | Update meta-information for current .spec file.<br>Verbs: author, describe, license, name, and reference. |
| next "%var": cmd %\_ |  |  | Remove first element from %var and run cmd with %\_ set to the removed element. Do nothing if %var is empty. |
| options \[+options\] | OBJECT | OBJECT | Turn on more +options for this export configuration object.<br> <br>Options are +optimize (Link-time optimization), +disco (randomize function order), +mutate (constants mutator), and others |
| optout "target" "h1, h2, ..." | OBJECT | OBJECT | Do not allow redirect or attachs hooks hook1, hook2, etc. (or hooks that call them) in target function |
| pack $VAR "template" ... |  |  | Marshal "string" arguments into $VAR with types specified in template. See [Pack Reference](https://tradecraftgarden.org/docs.html#pack). |
| patch "symbol" $VAR | OBJECT | OBJECT | Patch "symbol" within COFF/PIC with contents of $VAR |
| pop $VAR | BYTES |  | Pop content from stack and store in $VAR |
| preplen | BYTES | BYTES | Prepend length (of content) to the content on the stack<br>Length is a 4-byte integer in arch-native byte order. |
| prepsum | BYTES | BYTES | Calculate and prepend Adler32 checksum to content on the stack<br>Checksum is a 4-byte integer in arch-native byte order. |
| preserve "target" "f1, f2, ..." | OBJECT | OBJECT | Prevent attach and redirect hooks on MODULE$Function or target within func1, func2, etc. |
| protect "func1, func2, etc." | OBJECT | OBJECT | Prevent all attach and redirect hooks within func1, func2, etc. |
| push $VAR |  | BYTES | Push $var onto stack |
| rc4 $VAR | BYTES | BYTES | RC4 encrypt content on stack with $VAR as key |
| redirect "function" "hook" | OBJECT | OBJECT | Rewrite calls and references to function() to go through hook(). Preserves function() in hook(). |
| remap "old" "new" | OBJECT | OBJECT | Rename a symbol in the current COFF. (Use ./coffparse to see symbol names) |
| resolve "%var" |  |  | Resolves and updates comma-separated partial file paths in %var to full-paths relative to current .spec file location |
| rule "name" max ... | OBJECT | OBJECT | Configure Yara rule for object on stack. Full options are: rule "name" \[maxSigs\] \[minAgree\] \[minSigLength-maxSigLength\] \["func1, func2"\]. The last parameter is a list of functions to generate signatures from. |
| run "foo.spec" ... |  |  | Run another .spec, using the same target, $VARs, and stack as the current script. Accepts positional arguments, passed as %1, %2, etc. |
| set "%var" "value" |  |  | Sets %var to value in the local scope (e.g., visible to the current running label context only) |
| setg "%var" "value" |  |  | Sets %var to value in the global scope (e.g., accessible globally through this linking session) |
| xor $VAR | BYTES | BYTES | Mask content on stack using $VAR as key |

#### 7.3 Binary Transformation Options

Crystal Palace's `make coff`, `make pic`, and `make object` commands support several binary transformations. These are features that disassemble your program, transform it in some way, and put it back together into something that (usually) works.

The tools:

`+blockparty` randomizes the blocks in a function.

`+disco` is function disco! This feature randomizes the order of functions in your program. If it's used with `make pic` the first function is not randomized.

`+gofirst` makes sure `go()` function is at position 0 of your PIC.

`+mutate` rewrites some instructions to break up constants and stack strings.

`+optimize` is link-time optimization. This transform walks your program, finds function calls (and other references to the function), and cuts unused functions from your program. This is a great tool if you're reusing a library of headers between projects and want to get rid of the stuff the current program doesn't need.

`+regdance` is a register shuffling tool. This feature shuffles non-volatile registers in functions where it's safe to do so.

`+shatter` supercedes +blockparty. It randomizes blocks across the entire program.

You may specify one or more of these options with the `make` command. The order doesn't matter.

To understand how these transform affect your program, use `disassemble "out.txt"`. This command disassembles a PIC or PICO on the program stack and writes the output to out.txt (or another file you specify).

#### 7.4 Meta-Information

Crystal Palace includes commands to set meta-information about the tradecraft. This information is available to the [Java API](https://tradecraftgarden.org/docs.html#javaapi) and used by the Yara rule generator (rulegen). Place these commands at the top of your files, before the first target label.

`name "Tradecraft Name"` assigns a descriptive short name to the tradecraft in the file.

`describe "This is a description of the tradecraft"` is a longer, about one sentence, description of the tradecraft.

`author "Mr. Big"` sets the author information for this tradecraft implementation.

`reference "URL"` is a URL reference for the tradecraft implementation.

`license "..."` is the software license for the tradecraft implementation (and generated yara rules).

Each of these commands are optional. Their order doesn't matter.

`meta` is used to update meta-information via CLI [@config.spec](https://tradecraftgarden.org/docs.html#config) files when generating targeted Yara rules. Below is a @config.spec to generate a [Yara rule](https://tradecraftgarden.org/libtcg.html?file=rules.yar) from LibTCG's Win32 API resolution functions:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6 | `x64:`<br>```before``"export"``: options +regdance +mutate`<br>```before``"export"``: rule``"LibTCG_ResolveEAT"``10 5 10-18``"findModuleByHash, findFunctionByHash"`<br>```before``"export"``: meta``"name"``"LibTCG"`<br>```before``"export"``: meta``"describe"``"Export Address Table Win32 API resolution"`<br>```before``"export"``: meta``"license"``"BSD"` |

#### 7.5 Build Templates with %variables

Crystal Palace commands may use %variables anywhere a "string" argument is used. These are user-defined strings passed in at the beginning of the program.

For example:

`load %foo`

This command will resolve %foo and load its contents.

The <> is the string concatenation operator:

`load %foo <> â€œ.x64.oâ€`

This will resolve %foo and append .x64.o to it.

The echo command helps make sense of all of this. `echo` prints its arguments to STDOUT (CLI) or to a SpecLogger object (API):

`echo %foo <> ".x64.o"`

The purpose of %variables is to turn Crystal Palace specification files into build templates, reactive to user-specified options.

#### 7.6 Looping %variables

`foreach` loops over items in a comma-separated list and calls the follow-on command with %\_ as the argument.

`foreach "a, b, c": echo "Hello " %_`

You can use a %variable here too:

`set "%list" "a, b, c"
foreach %list: echo "Hello " %_`

`next` removes the first item from a %list, sets %\_ to the removed value, and calls the follow-on command. If the %list is empty, `next` does nothing.

`set "%list" "a, b, c"
next "%list": echo "First " %_
next "%list": echo "Second " %_`

These commands allow link-time composition of one or more user-specified modules.

#### 7.7 Callable Labels

Callable labels are Crystal Palace functions. Use `name.arch:` to define a callable label:

`foo.x64:`

Callable labels are invoked with the .syntax:

`.foo`

Callable labels accept positional arguments too. These are available within the called label's local scope (visible only during that execution) as %1, %2, etc.

`.foo "arg 1" %arg2`

`call` runs a callable label in another specification file:

`call "file.spec" "foo" "arg 1" %arg2`

Callable labels, especially paired with `call`, are Crystal Palace's modularity tool. [Simple Loader - Hooking](https://tradecraftgarden.org/simplehook.html) demonstrates this. The Hooking loader defines a base architecture with user-specified modules in a `%HOOKS` variable. Each tradecraft module defines **setup** and **hooks** callable labels to expose tradecraft-specific setup to the base loader.

#### 7.8 Quoting Strings

Crystal Palace accepts bare word strings in a lot of places. But, I recommend disciplining yourself to "quote strings" with double quotes.

Beyond "quotes", Crystal Palace has a few other quoting tools.

The : operator is a special quoting tool. It takes everything afterwards and gathers it into one argument. It's demonstrated with the `foreach` and `next` commands, but it works anywhere.

Crystal Palace's command language has a syntax to change the quoting character on a command-by-command basis too:

`echo,' 'This is a "string" with a new quote character'`

You can go a little crazier with it:

`echo,Z ZThis is my 'string' with "quoted characters"Z`

### 8\. Position-independent Code

#### 8.1 Overview

The `make pic` command within a .spec file will transform a COFF into position-independent code. And there's more. But, this "there's more" requires some explanation.

A COFF file is not meant as an executable. A COFF is code generated by the compiler, data referenced by that code (e.g., string literals), and a bunch of records--called relocations--that describe the places in the executable code where outside stuff is referenced or called upon, but where in memory that outside stuff lives is currently unknown. It's the job of the linker and the operating system loader to handle these relocations. Some things the linker can handle. Others (e.g., calls to exported functions in other libraries) normally require the help of the operating system loader.

At its simplest, the `make pic` command extracts the .text (your code) and .rdata (string constants) sections from a COFF and appends them together. Crystal Palace will, on its own, attempt to resolve a bunch of those relocations for you and report as errors the relocations it can't resolve.

For x64, the linker can do a lot without knowing anything about the execution environment of the final program. The x64 instruction set allows referencing data relative to the current executing instruction. In practice, this means relocations referencing appended data (e.g., the link command) just work. References to the .rdata section (where your strings live) will just work too. And, small things, like referencing a function pointer within your .text section works as well--because Crystal Palace handles these relocations too.

For x86, things get messy. The x86 instruction set does not allow referencing data relative to the current execution instruction. This means attempts to reference certain symbols (e.g., a pointer for a function) won't work. Crystal Palace has the option to resolve these symbol relocations with partial pointers. But, this means at runtime some sort of special care is needed to turn these partial pointers into full pointers.

Crystal Palace has several PIC development ergonomic features. They're opt-in, but they solve a lot of problems.

#### 8.2 Pointer Fixing (x86)

The `fixptrs` command opts x86 PIC into Crystal Palace's pointer fixing feature. This feature walks your program, finds any data references, and dynamically rewrites the program to create a full pointer. This is made possible by a `_caller` helper function that you provide. The \_caller function is responsible for returning its return address. Every example in the Tradecraft Garden opts into this feature. The fixptrs feature also works with references to .rdata--giving you the use of strings in x86 PIC programs. And, pointers to local functions work too.

`fixptrs "_caller"`

Before fixptrs, it was necessary to caculate the full address for any linked symbols on x86. This involved adding the return address from `caller`, the partial pointer to the data, and an offset to account for the distance between the `caller` return address and the end of the assembly instruction loading the data. This is what that looked like:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27 | `char``__DLLDATA__[0] __attribute__((section(``"my_data"``)));`<br>`#ifdef WIN_X86`<br>`__declspec``(``noinline``)``ULONG_PTR``caller(``VOID``) {``return``(``ULONG_PTR``)WIN_GET_CALLER(); }`<br>`char``* findAppendedDLL() {`<br>```/*`<br>```* 000006E3 <_findAppendedDLL>:`<br>```* 000006E3 55                   push      %ebp`<br>```* 000006E4 89E5                 mov       %esp,%ebp`<br>```* 000006E6 E8F0FFFFFF           call      _caller`<br>```* ; %eax holds the return address of our call which is 0x6EB`<br>```*`<br>```* 000006EB BA00000000           mov       $my_data,%edx`<br>```* ; %edx is $my_data, which is the offset to my_data FROM 0x6F0`<br>```*`<br>```* 000006F0 83C205               add       $5,%edx`<br>```* ; add 5 to %edx (the length of instruction at 0x6EB) and...`<br>```* ; we have... a full pointer in %edx *pHEAR*`<br>```*`<br>```* 000006F3 01D0                 add       %edx,%eax`<br>```* 000006F5 5D                   pop       %ebp`<br>```* 000006F6 C3                   ret`<br>```*/`<br>```return``PTR_OFFSET(caller(), (``ULONG_PTR``)&__DLLDATA__ + 5);`<br>`}`<br>`#endif` |

The above is no longer needed with Crystal Palace PIC programs. fixptrs is the tool to restore linked data and local function pointers in x86 PIC.

#### 8.3 Resolving Win32 APIs

Position-independent code, initially, has no access to or idea about the Win32 API. A common strategy to find the Win32 API is to walk the export address table of modules loaded in memory and compare their exported function string hashes with a list of hashes in the PIC program. This is the method most Tradecraft Garden examples use. And, Crystal Palace has tools to help with this.

Use `dfr "resolver" "ror13"` to enable Dynamic Function Resolution (DFR) with the ror13 method. `ror13` here is the hashing algorithm and call contract for the resolver. When DFR is setup this way, Crystal Palace will walk your PIC program (x86 and x64), find references to `MODULE$Function`, calculate the ror13 hash of MODULE, and the ror13 hash of Function, and insert code to call your resolver with these values as arguments. Most Tradecraft Garden PIC programs use this convention.

The variant of this is `dfr "resolver" "strings"` which inserts code to push MODULE and Function strings onto the stack and call your resolver with pointer arguments to each. This is handy for situations where GetProcAddress and GetModuleHandle are known before your PIC is run. [Simple Loader (Pointer Patching)](https://tradecraftgarden.org/simplepatch.html) demonstrates this variant.

The exception to the `MODULE$Function` convention is `GetProcAddress` and `LoadLibraryA`. Crystal Palace's DFR will handle these without KERNEL32$ prefixed.

Crystal Palace allows multiple resolvers. Use `dfr "resolver" "method" "mod1, mod2, ..."` to set a DFR resolver for specific Win32 modules. This resolver will take priority over the default DFR resolver.

If your PIC may need to load libraries, consider `dfr "resolver" "ror13" "KERNEL32"` to bootstrap needed functions from Kernel32 and use a default resolver `dfr "resolver_ext" "strings"` to handle everything else. The default resolver with strings is an opportunity to load any missing libraries. [Simple PIC](https://tradecraftgarden.org/simplepic.html) demonstrates this.

DFR works fine with function pointers and direct calls.

You can resolve Win32 APIs without DFR. The manual way is to define constants for the function/module hashes you wish to look up, and early-on in your program--populate a struct with the function pointers your program will need. Here's what that looks like:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10 | `#define KERNEL32DLL_HASH    0x6A4ABC5B`<br>`#define LOADLIBRARYA_HASH   0xEC0E4E8E`<br>`#define GETPROCADDRESS_HASH 0x7C0DFCAA`<br>`void``findNeededFunctions(IMPORTFUNCS * funcs) {`<br>```char``* hModule = (``char``*)findModuleByHash(KERNEL32DLL_HASH);`<br>``<br>```funcs->LoadLibraryA   = (__typeof__(LoadLibraryA) *)   findFunctionByHash(hModule, LOADLIBRARYA_HASH);`<br>```funcs->GetProcAddress = (__typeof__(GetProcAddress) *) findFunctionByHash(hModule, GETPROCADDRESS_HASH);`<br>`}` |

Pair this manual resolution with [attach](https://tradecraftgarden.org/docs.html#attach) and you have a way to define one function that resolves and calls a Win32 API across your program. The benefit of this over DFR is that `attach` looks like a normal function call. It doesn't require the same state-preserving instructions as DFR.

Tradecraft Garden's [20250910 release](https://tradecraftgarden.org/download/tcg20250910-bsd.tgz) contains working examples of resolving Win32 APIs, handling x86 partial pointers, etc. Consult this old release if you're interested in these manual techniques.

#### 8.4 Global Variables

Without hacks, global variables are not available in position-independent code. Crystal Palace has a tool to restore some global variables to PIC, if it's needed.

Use `fixbss "getBSS"` to opt into Crystal Palace's .bss restoration feature. .bss is the COFF section for uninitialized global variables.

When fixbss is setup, Crystal Palace will rewrite each .bss instruction reference to call the specified `getBSS` function and use its return value as the base .bss address in memory.

The `getBSS` function accepts one DWORD argument (the length of the .bss section) and returns a pointer to the .bss data. The `getBSS` function must return the same pointer each call. fixbss expects that the .bss space is initialized to zeroes and large enough to accommodate the .bss section.

The [Simple PIC](https://tradecraftgarden.org/simplepic.html) project demonstrates fixbss.

#### 8.5 Avoiding Common PIC-falls

The entry point for your position-independent code is the function at the top of your C program. For compatability with Crystal Palace features (e.g., link-time optimization, function disco, and error checks), name this function `go`.

Don't use switch statements in your programs. These often generate a [jump table](https://www.cs.umd.edu/~waa/311-F09/jumptable.pdf) that lives in read-only constants (.rdata) memory with relocations of their own. Jump tables are not supported by Crystal Palace.

Beware of compiler optimizations. MinGW -O1 compiled programs are supported by Crystal Palace, but know that the optimizations may move functions around, insert jump tables, and make other changes that impact position-independent code negatively.

If you do turn on optimizations, here are some of the GCC flags I found most helpful: `-fno-jump-tables -fno-toplevel-reorder -fno-exceptions -fno-stack-protector`. If needed, decorate troublesome functions with `__attribute__((optimize("O0")))` to disable optimizations for that function.

Crystal Palace does not have transforms for float and double types. If you use these in your program, it may break.

SEHs are not supported by Crystal Palace. Don't use them.

Beware that your compiler may add "sneaky function calls" to your code. For example, with Microsoft's compiler, if you use too much stack space for local variables, the compiler will insert a function call to probe the next pages of the stack. If this happens, identify the compiler feature associated with the unresolved function, and use a command-line switch to turn it off.

If Crystal Palace reports a relocation error, it means your compiler generated code that references data Crystal Palace can't resolve without the aid of the operating system loader. In these situations, your best bet is to revise that code.

### 9\. Crystal Palace PICOs (COFFs)

#### 9.1 Overview

Position-independent Code Objects, aka PICOs, are a Crystal Palace convention to embed and run COFFs in a simple and flexible way. PICOs are similar to [Cobalt Strike's Beacon Object Files](https://youtube.com/watch?v=gfYswA_Ronw) but without the API.

PICOs are an abstraction above position-independent code with a lot of conveniences restored. You regain the ability to use strings and other constants. PICOs support initialized and uninitialized global variables. And, the PICO loader also supports dynamic function resolution for referencing Win32 APIs from the COFF. This is Cobalt Strike's `MODULE$function` convention from Beacon Object Files. Writing PICOs targeting x86 and x64 CPUs is virtually the same.

A resource is designated as a PICO with the `make object` command within a .spec file. This command directs Crystal Palace to parse the object file, pre-resolve various sections for global variables and built-in strings, extract the .text section, and generate "loading directives" which are simple instructions to assist with loading and processing relocations of this amalgamation that started as a COFF.

The entry point of a PICO is the `go` function.

Note that `go` is optional. This is useful to merge multiple PICOs into one and access their functionality via an exported function.

#### 9.2 PICO Example

Here is a simple PICO example that prints "Hello World" via [OutputDebugStringA](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-outputdebugstringa).

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7 | `#include <windows.h>`<br>`WINBASEAPI``VOID``WINAPI KERNEL32$OutputDebugStringA (``LPCSTR``lpOutputString);`<br>`void``go(``char``* arg) {`<br>```KERNEL32$OutputDebugStringA(``"Hello World!"``);`<br>`}` |

#### 9.3 How to run a PICO

To run a Crystal Palace PICO (COFF), include `tcg.h` into your code, and use a function that looks something like this:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20 | `void``run_coff(IMPORTFUNCS * funcs,``char``* srcPico) {`<br>```char``* dstCode;`<br>```char``* dstData;`<br>``<br>```/* allocate memory for our PICO */`<br>```dstData = KERNEL32$VirtualAlloc( NULL, PicoDataSize(srcPico), MEM_RESERVE|MEM_COMMIT|MEM_TOP_DOWN,`<br>```PAGE_READWRITE );`<br>```dstCode = KERNEL32$VirtualAlloc( NULL, PicoCodeSize(srcPico), MEM_RESERVE|MEM_COMMIT|MEM_TOP_DOWN,`<br>```PAGE_EXECUTE_READWRITE );`<br>``<br>```/* load our pico into our destination address, thanks! */`<br>```PicoLoad(funcs, srcPico, dstCode, dstData);`<br>``<br>```/* And, we can call our pico entry point */`<br>```PicoEntryPoint(srcPico, dstCode)(NULL);`<br>``<br>```/* free everything... */`<br>```KERNEL32$VirtualFree(dstData, 0, MEM_RELEASE);`<br>```KERNEL32$VirtualFree(dstCode, 0, MEM_RELEASE);`<br>`}` |

This API gives you control over where your PICO is located in memory and whether or not the code and data are in the same contiguous memory. The default PICO entry point accepts a `char *` argument. But, that's just a definition. You can cast it to something else.

The `IMPORTFUNCS` struct is defined in tcg.h. It's used to pass `GetProcAddress` and `LoadLibraryA` pointers (or your chosen substitutes) to PICO and DLL loaders.

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4 | `typedef``struct``{`<br>```__typeof__(LoadLibraryA)   * LoadLibraryA;`<br>```__typeof__(GetProcAddress) * GetProcAddress;`<br>`} IMPORTFUNCS;` |

The `IMPORTFUNCS` struct provides the function pointers the DLL and PICO loading code use to resolve imported APIs.

#### 9.4 Import Functions into a PICO

The function pointers from `IMPORTFUNCS` are also mapped into COFFs loaded via pico.h as `LoadLibraryA` and `GetProcAddress`. If you pass a struct with extra pointers in it, you can bring those functions into COFFs as well. Use the `import` command to do this. For example, if we pass a populated `WIN32FUNCS` to PicoLoader:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6 | `typedef``struct``{`<br>```__typeof__(LoadLibraryA)   * LoadLibraryA;`<br>```__typeof__(GetProcAddress) * GetProcAddress;`<br>```__typeof__(VirtualAlloc)   * VirtualAlloc;`<br>```__typeof__(VirtualFree)    * VirtualFree;`<br>`} WIN32FUNCS;` |

Then `import "LoadLibraryA, GetProcAddress, VirtualAlloc, VirtualFree"` in the .spec file will map the LoadLibraryA function to the first entry of that struct, GetProcAddress to the second, VirtualAlloc to the third, and VirtualFree to the fourth.

#### 9.5 Export Functions from a PICO

`exportfunc "function" "__tag_function"` exports a function from a PICO and generates a tag intrinsic.

Behind the scenes, exportfunc generates a random integer tag for the function. This tag makes the exported function discoverable via the PICO's loading directives.

We don't know this hidden tag value. That's where `__tag_function()` comes in. This pseudo-function is replaced with the hidden tag at link time. `__tag_function()` is available globally to any PIC/PICO exported after exportfunc is used.

Here's the prototype to declare \_\_tag\_function:

`int __tag_function();`

Use this intrinsic with `PicoGetExport` to get a pointer to the exported function:

`PICOMAIN_FUNC pFunction = PicoGetExport(picoSrc, picoDst, __tag_function());`

#### 9.6 Shared Libraries

Crystal Palace has a concept of shared libraries. A shared library is a .zip archive of x86 or x64 COFF objects. Use `mergelib "path/to/lib.x64.zip"` to merge each of the objects in the library with the current PICO/PIC/COFF on the stack.

Crystal Palace PIC (with fixptrs and dfr opted-into) and PICOs share the same conventions. This means a COFF that uses `MODULE$Function` for Win32 APIs, avoids global variables, etc. is suitable as a shared library for use in PIC or PICO programs.

One downside to share libraries is they may import stuff you don't need. Use the `+optimize` option with the `make` command to enable link-time optimization. This will remove functions that are not called or referenced from your final program.

The [Tradecraft Garden Library](https://tradecraftgarden.org/libtcg.html) (LibTCG) is Tradecraft Garden's default library. It provides functions for DLL loading, PICO running, walking the export address table, and even printf()-style debugging. LibTCG is also a good example of how to build a library. It's API is described in `tcg.h`. All Tradecraft Garden examples use this library.

### 10\. PIC and PICO Instrumentation

#### 10.1 Attach and Redirect

Crystal Palace has tools to attach to Win32 APIs and redirect local function calls to user-provided hook functions. Both commands transform the program instructions to look like the hook was the original function call (or reference). This is a process called weaving. Think of attach and redirect as software composition tools. With these tools, you can layer functionality over a base behavior, outright replace parts of a base capability, or go beyond 1:1 limits of modular programming and chain candidate implementations over a placeholder function in a capability. These tools enable a programming paradigm called [Aspect-Oriented Programming](https://aff-wg.org/2025/11/10/tradecraft-engineering-with-aspect-oriented-programming/).

attach applies a hook to a Win32 API:

`attach "MODULE$Function" "hook"`

attach is context aware. It will not update references to the target function in the context of `hook`. This allows `hook` to call the original function without hacks to preserve its pointer.

attach is stackable too. A follow-on attach will hook MODULE$Function in the first `hook` function. Hooks may call their MODULE$Function to pass execution through the chain of hooks until the original API is reached. Hooks execute in a first-declared first-executed order.

redirect adds a hook to a local function:

`redirect "function" "hook"`

redirect works much like attach and has the same semantics. Redirects are stackable too. Calls to `function` within a hook pass execution through the rest of the function's redirect hook chain.

Beware of redirect when programs are built with compiler optimizations (e.g., -O1). The compiler may inline a redirect-target function, making it unreachable by this feature. Or, if the function is empty, the compiler may remove the call to the function. Here's how to work-around that:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13 | `/*`<br>```* This is an empty function, but we will use redirect to LAYER setupHooks from our modules on top of this.`<br>```*`<br>```* NOTE: gcc with -O1 likes to inline some functions and an empty or minimal function is a prime candidate for`<br>```* inlining. I'm using noinline to prevent that tragedy, because if a function is inlined, we can't redirect it`<br>```*/`<br>`void``__attribute__((``noinline``)) setupHooks(``char``* srchooks,``char``* dsthooks, DLLDATA * data,``char``* dstdll) {`<br>```/*`<br>```* And, in the fighting the optimizer department, -O1 likes to also not call a function it believes has`<br>```* no side-effects. So, we stick this here to say GCC LEAVE MY EMPTY FUNCTION ALONE!`<br>```*/`<br>```__asm__ __volatile__(``""``);`<br>`}` |

#### 10.2 Isolating Functions from Attach and Redirect

attach and redirect have global effect in the exported PIC/PICO. Below are tools to case-by-case isolate functions from attach and redirect hooks.

`protect "function1, function2, etc."`

protect isolates the listed functions from all attach and redirect hooks. `dprintf` is opted into this automatically. Use this tool to protect debugging tools and other sensitive code.

`preserve "target|MODULE$Function" "function1, function2"`

preserve protects a specific target (local function or Win32 API) from attach and redirect hooks in the listed function contexts. Use preserve functions that need direct access to the target function or its pointer.

`optout "function" "hook1, hook2, hook3"`

optout prevents specific hooks from taking effect within a function. Use optout to isolate a tradecraft setup function from its own hooks. This makes it possible for other tradecraft to modify the setup function later.

#### 10.3 IAT Hooks

The addhook command registers a MODULE$Function hook with Crystal Palace:

`addhook "MODULE$Function" "hook"`

`addhook` with no hook function will use the `attach "MODULE$Function" "hook"` chain. This is useful if layering IAT hooks is your goal.

You're welcome to specify as many of these as you like. Crystal Palace won't throw an error if a MODULE$Function hook isn't used.

These registered hooks are used by the \_\_resolve\_hook() linker intrinsic:

`FARPROC __resolve_hook(DWORD functionHash);`

A linker intrinsic is a pseudo-function that expands into linker generated code where it's called. \_\_resolve\_hook() generates code to turn a "Function" ror13 hash into a hook pointer.

Use filterhooks to remove registered hooks that aren't needed by its $DLL or $OBJECT argument. This command walks the capability import table to see what is and isn't needed.

`filterhooks $DLL`

### 11\. C Patterns

#### 11.1 Overview

Below are several patterns to interact with data and results from the Crystal Palace specification commands above. The Tradecraft Garden has full working samples that demonstrate each of the above in context. For simplicity's sake, each of the below patterns is x64 only. The x86-compatibility steps are left out.

#### 11.2 Appending resources

The `link` command creates a section within a COFF or PIC and places a resource within it. This data is then easily reachable from a C program:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5 | `char``__DLLDATA__[0] __attribute__((section(``"my_data"``)));`<br>``<br>`char``* findAppendedDLL() {`<br>```return``(``char``*)&__DLLDATA__;`<br>`}` |

The above is from [Simple Loader](https://tradecraftgarden.org/simple.html). This C code declares a global variable, in this case a character array of some length, and places it in the `my_data` section of the program. The `link "my_data"` command within the .spec file places the resource, at the top of the Crystal Palace stack, into this section.

This pattern works with resources linked to COFF and PIC.

You can create as many of these sections for different resources as you like.

#### 11.3 Mask, Encrypt, and calculate embeddable checksums for resources

Several specification commands are meant to transform or add information to data before you link it.

`preplen` prepends the length of data on the program stack to itself. Here is a C struct to interact with that length value and follow-on data:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4 | `typedef``struct``{`<br>```int``length;`<br>```char``value[];`<br>`} _RESOURCE;` |

The [Simple Loader (Masking)](https://tradecraftgarden.org/simplemask.html) project demonstrates `preplen` used with `xor` to unmask resources and work with an arbitrary (e.g., specified in the .spec file) length XOR mask.

The `prepsum` command calculates the [Adler-32 checksum](https://www.ietf.org/rfc/rfc1950.txt) of the top-level data on the program stack, and prepends this value to it. Here is a C struct to interact with that data:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4 | `typedef``struct``{`<br>```DWORD``checksum;`<br>```char``value[];`<br>`} _VERIFY;` |

And, here is C code to calculate the Adler-32 checksum of a resource:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10 | `DWORD``checksum(unsigned``char``* buffer,``DWORD``length) {`<br>```DWORD``a = 1, b = 0;`<br>```for``(``int``x = 0; x < length; x++) {`<br>```a = (a + buffer[x]) % 65521;`<br>```b = (a + b) % 65521;`<br>```}`<br>``<br>```return``(b << 16) + a;`<br>`}` |

The [Simple Loader (Execution Guardrails)](https://tradecraftgarden.org/simpleguard.html) project demonstrates the use of `prepsum` and `rc4` to encrypt and post-decrypt validate resources.

#### 11.4 Assign user-supplied data to global symbols

The `patch "symbol" $VAR` command patches the contents of `$VAR` into the specified symbol. This works for both PIC and COFF, but with caveats.

For COFF, declare a global variable, and initialize it to some value. Congratulations, this value is now a candidate to get updated with the `patch` command from a .spec file. This works on both x86 and x64. The [Page Streaming Loader](https://tradecraftgarden.org/pagestream.html) uses this to set a XOR key, created from the .spec file's `generate` command, to a random value.

You can use `patch` with x64 position-independent code, BUT you must declare the global variable as existing within the .text section of your code:

[?](https://tradecraftgarden.org/docs.html#)

|     |     |
| --- | --- |
| 1<br>2 | `__typeof__(GetModuleHandle) * pGetModuleHandle __attribute__((section(``".text"``)));`<br>`__typeof__(GetProcAddress)  * pGetProcAddress  __attribute__((section(``".text"``)));` |

The above code declares two pointers, pGetModuleHandle and pGetProcAddress, as global variables. The `__attribute__((section(".text")));` decorator tells the compiler to allocate these globals into the .text section (aka our executable code). The [Simple Loader (Pointer Patching)](https://tradecraftgarden.org/simplepatch.html) example demonstrates using patch from a .spec file to set these globals.

### 12\. Next steps

That's it for the documentation. The next step is to try some things out, modify some code, and have fun with this stuff.

As an easy next step, visit the [The Amphitheater](https://tradecraftgarden.org/videos.html) for videos on how to [setup](https://tradecraftgarden.org/wslsetup.html) your Windows Subsystem for Linux environment and a demonstration of using Crystal Palace and building the Tradecraft Garden files.

I recommend trying to reproduce what's in the videos first. Prove to yourself that you can compile the samples, run the linker, and get the "Hello World" message box via the included demonstration programs.

A good step after this is to try and load a DLL other than the DLL that comes with Crystal Palace. Maybe something custom. Maybe something from a favorite C2.

Do note that some C2s (Cobalt Strike, for example) have a startup convention that differs from just calling `DllMain((HANDLE)hDll, DLL_PROCESS_ATTACH, NULL)`. You will likely need to modify a Tradecraft Garden example to work with that specific convention. Fortunately, if you're interested in [Cobalt Strike](https://www.cobaltstrike.com/)--you're not on your own. Daniel Duggan has written [Harvesting the Tradecraft Garden](https://rastamouse.me/harvesting-the-tradecraft-garden/) parts [1](https://rastamouse.me/harvesting-the-tradecraft-garden/) and [2](https://rastamouse.me/harvesting-the-tradecraft-garden-part-2/). These blog posts demonstrate how to use Crystal Palace with Cobalt Strike's Beacon and post-ex DLLs.

Once you're convinced you can make these examples work with a DLL that interests you--the next fun is in studying the TCG code, modifying it to do new things, and getting familiar with what's possible.

To help with this, there are several "Simple Loaders". I encourage you to study these to get an idea of how to use the Crystal Palace linker features and do cool things you may want in your loaders:

- [Reflective DLL Injection](https://tradecraftgarden.org/rdlli.html) Stephen Fewer's ReflectiveDLLInjection with minimal changes
- [Simple Loader 1](https://tradecraftgarden.org/simple.html) Simple DLL loader
- [Simple Loader 2 (COFF)](https://tradecraftgarden.org/simplefree.html) Simple DLL loader that frees itself with an embedded COFF
- [Simple Loader 3 (Resource Masking)](https://tradecraftgarden.org/simplemask.html) Simple DLL loader that accesses masked resources
- [Simple Loader 4 (Pointer Patching)](https://tradecraftgarden.org/simplepatch.html) Simple DLL loader that bootstraps with patched-in pointers
- [Simple Loader 5 (Execution Guardrails)](https://tradecraftgarden.org/simpleguard.html) Simple loader stage that implements execution guardrails
- [Simple Loader 6 (Hooking)](https://tradecraftgarden.org/simplehook.html) Simple DLL loader that uses IAT hooks to change loaded DLL's behavior
- [Simple Loader 7 (COFF Capability)](https://tradecraftgarden.org/simpleobj.html) Simple OBJ loader
- [Simple Loader 8 (Mixed COFF and DLL)](https://tradecraftgarden.org/simpleobjmix.html) Simple OBJ and DLL loader (supporting both)
- [Simple PIC 9](https://tradecraftgarden.org/simplepic.html) Simple PIC Services Module