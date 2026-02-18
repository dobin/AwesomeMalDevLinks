# https://0xrick.github.io/win-internals/pe2/

## A dive into the PE file format - PE file structure - Part 1: Overview [Permalink](https://0xrick.github.io/win-internals/pe2/\#a-dive-into-the-pe-file-format---pe-file-structure---part-1-overview "Permalink")

### Introduction [Permalink](https://0xrick.github.io/win-internals/pe2/\#introduction "Permalink")

The aim of this post is to provide a basic introduction to the PE file structure without talking about any details.

* * *

### PE files [Permalink](https://0xrick.github.io/win-internals/pe2/\#pe-files "Permalink")

PE stands for Portable Executable, it’s a file format for executables used in Windows operating systems, it’s based on the `COFF` file format (Common Object File Format).

Not only `.exe` files are PE files, dynamic link libraries (`.dll`), Kernel modules (`.srv`), Control panel applications (`.cpl`) and many others are also PE files.

A PE file is a data structure that holds information necessary for the OS loader to be able to load that executable into memory and execute it.

* * *

### Structure Overview [Permalink](https://0xrick.github.io/win-internals/pe2/\#structure-overview "Permalink")

A typical PE file follows the structure outlined in the following figure:

![](https://0xrick.github.io/images/wininternals/pe2/1.png)

If we open an executable file with `PE-bear` we’ll see the same thing:

![](https://0xrick.github.io/images/wininternals/pe2/2.png)

#### DOS Header [Permalink](https://0xrick.github.io/win-internals/pe2/\#dos-header "Permalink")

Every PE file starts with a 64-bytes-long structure called the DOS header, it’s what makes the PE file an MS-DOS executable.

#### DOS Stub [Permalink](https://0xrick.github.io/win-internals/pe2/\#dos-stub "Permalink")

After the DOS header comes the DOS stub which is a small MS-DOS 2.0 compatible executable that just prints an error message saying “This program cannot be run in DOS mode” when the program is run in DOS mode.

#### NT Headers [Permalink](https://0xrick.github.io/win-internals/pe2/\#nt-headers "Permalink")

The NT Headers part contains three main parts:

- **PE signature:** A 4-byte signature that identifies the file as a PE file.
- **File Header:** A standard `COFF` File Header. It holds some information about the PE file.
- **Optional Header:** The most important header of the NT Headers, its name is the Optional Header because some files like object files don’t have it, however it’s required for image files (files like `.exe` files). This header provides important information to the OS loader.

#### Section Table [Permalink](https://0xrick.github.io/win-internals/pe2/\#section-table "Permalink")

The section table follows the Optional Header immediately, it is an array of Image Section Headers, there’s a section header for every section in the PE file.

Each header contains information about the section it refers to.

#### Sections [Permalink](https://0xrick.github.io/win-internals/pe2/\#sections "Permalink")

Sections are where the actual contents of the file are stored, these include things like data and resources that the program uses, and also the actual code of the program, there are several sections each one with its own purpose.

* * *

### Conclusion [Permalink](https://0xrick.github.io/win-internals/pe2/\#conclusion "Permalink")

In this post we looked at a very basic overview of the PE file structure and talked briefly about the main parts of a PE files.

In the upcoming posts we’ll talk about each one of these parts in much more detail.