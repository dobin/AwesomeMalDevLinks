# https://fluxsec.red/rust-dll-windows-api

# Building a DLL in Rust

Building a simple DLL in Rust with the Windows API

* * *

## Intro

As ever, the project can be found here on my [GitHub](https://github.com/0xflux/Simple-Rust-DLL).

There is an update to the below source code making your DLL much more reliable if you are relying on DLL\_PROCESS\_ATTACH - if you want to see that, check out the bottom of my [blog post here](https://fluxsec.red/remote-process-dll-injection#a-dll-update-automatic-unloading).

DLLs, short for Dynamic Link Libraries, are like the Swiss Army knives for Windows apps. They are akin to little helper libraries packed with code and functions that other apps or DLLs can borrow. In my mind, there are two types of DLL (well, not really, but bear with..), the first is those which are shipped alongside software (literally go look at any software folder on your PC and you will find plenty of DLLs I’m sure), and secondly, there are those DLLs provided by Microsoft which are used by the Windows API when programming in Windows. These DLLs such as `user32.dll`, `kernel32.dll` and `netapi32.dll` are all provided by Microsoft which essentially allow you as a programmer to call on the Kernel to do something for you. If you want to take a look at how you can abuse this mechanism for some advanced EDR / Antivirus evasion, check my [blog post](https://fluxsec.red/dll-injection-edr-evasion-1).

Why are DLL’s so useful to offensive cyber operations and malware developers? Well, there are three main reasons in my opinion:

1. DLLs can be used in PE injection: [T1055.001 DLL Injection](https://attack.mitre.org/techniques/T1055/001/) & [T1620 Reflective Code Loading](https://attack.mitre.org/techniques/T1620/)
2. DLLs can be used in Search Order Hijacking & DLL Side-Loading techniques: [T1574.002 DLL Side-Loading](https://attack.mitre.org/techniques/T1574/002/) & [T1574.001 DLL Search Order Hijacking](https://attack.mitre.org/techniques/T1574/001/)
3. DLLs may be subject to less scrutiny by EDR (at least when making Syscalls (for more info on syscalls see my [blog post](https://fluxsec.red/dll-injection-edr-evasion-1))). I don’t have a link to the video sadly, but there is a talk somewhere out there on YouTube where researchers compared using an EXE vs DLL for an implant / loader, and whilst they did the same thing, the DLL had less of a detectable footprint.

Legal disclaimer applies, by reading on you acknowledge that, see the legal disclaimer [here](https://fluxsec.red/#legal-disclaimer). In short, you must not use the below information for any criminal or unethical purposes, and it should only be used by security professionals, or for those interested in cyber security to deepen your knowledge. I firmly believe taking a proactive approach to security through penetration testing, ethical hacking and red teaming is one of the best ways we can improve cyber security as a whole in society.

## DLLMain

In C your program you may wish to use the **main** function as your entry point:

```c
void main() {
    // your code
}
```

And in Rust:

```rust
fn main() {
    // your code
}
```

A DLL has some important structures we first need to know about. Firstly; a DLL doesn’t require a **main** function to run, you can simply have a DLL which is just function after function after function. That said, there is a function called DllMain, which will act as the entry point when the DLL is loaded into a process, unloaded, a new thread is created, or when a thread exits cleanly.

According to the Win32 API for [DllMain](https://learn.microsoft.com/en-us/windows/win32/dlls/dllmain) (Windows API documentation), the function takes in 3 parameters:

```c
BOOL WINAPI DllMain(
    HINSTANCE hinstDLL,  // handle to DLL module
    DWORD fdwReason,     // reason for calling function
    LPVOID lpvReserved )  // reserved
```

The first and last parameter we will ignore for the purposes of this; but the middle argument, **fdwReason**, is a **DWORD**. The Win32 API tells us “The reason code that indicates why the DLL entry-point function is being called”, and gives the following table of constants to use in our program:

![DLL fdwReason constants](https://fluxsec.red/static/images/dll-process-attach.png)

We are mostly interested in the case of **DLL\_PROCESS\_ATTACH** when developing implants and modules.

## Exported Functions

The other important structural thing to know about DLLs is exported functions. As a DLL is literally, a library, we need to tell other programs what functions they can call from our library. In the same way you don’t want all your functions in a program to be public, DLLs have an additional concept of visibility from outside of the DLL. When making a DLL in Rust, you can make a function exportable like so:

```rust
#[no_mangle]
pub extern fn my_function() {
    // yoru code
}
```

The **#\[no\_mangle\]** attribute is used to tell the Rust compiler not to mangle the name of the function. Name mangling happens where the compiler generates unique names for each function and variable in your code to avoid naming conflicts, which is especially important when linking code with other libraries. The **#\[no\_mangle\]** attribute tells the Rust compiler **NOT** to mangle the names (i.e. to keep them as you have written). We do this because the external programs calling our DLL will need to know exactly which function name to call.

Using **pub extern** goes hand-in-hand with **#\[no\_mangle\]** to make the function accessible outside of the DLL. **Pub** is a visibility modifier, and **extern** indicates that the function should use the “C” calling convention, which is a standard way that functions expect arguments to be passed to them. Doing this makes the function universally callable, ensuring callers from other languages can correctly interact with the function. If you want to read more about this, Microsoft have written a nice post on [calling conventions for x64](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170).

## The code

Now we have a basic understanding of what a DLL is and its structure, lets get to work.

In order to use **DllMain** in our code, we need to firstly import the [Windows crate](https://crates.io/crates/windows), then add a dependency into our cargo.toml. Make sure you add –lib to the cargo new command to tell cargo we are building a library.

```shell
cargo new rust_dll --lib
cd rust_dll
cargo add windows
```

There’s a very important step that must be done when building a DLL, in the **cargo.toml** file, add this (which tells Rust we are building a DLL):

```shell
[lib]
crate-type = ["cdylib"]
```

Open up the **cargo.toml** file and update the dependencies as below. At this stage, we are adding in **Win32\_UI\_WindowsAndMessaging** because we will be making a popup box (MessageBox) as part of the DLL. In order to use [DLL\_PROCESS\_ATTACH](https://microsoft.github.io/windows-docs-rs/doc/windows/Win32/System/SystemServices/constant.DLL_PROCESS_ATTACH.html) we need to also import **Win32\_System\_SystemServices**.

```rust
[dependencies]
windows = { version = "0.54.0", features = [\
    "Win32_UI_WindowsAndMessaging",\
    "Win32_System_SystemServices",\
] }
```

Next, knowing what we know about the structure of the DLL we can start with building out **DLLMain**. Very simply this will be called when the DLL is attached to a process, and we are matching on the middle argument, **dw\_reason**, looking for the constant **DLL\_PROCESS\_ATTACH** (AKA a value of 1 if you recall the above table provided by the Win32 API). We exit with 1, which tells the process calling the DLL that it completed successfully.

```rust
use windows::Win32::System::SystemServices::*;

#[no_mangle]
#[allow(non_snake_case)]
fn DllMain(_: usize, dw_reason: u32, _: usize) -> i32 {
    match dw_reason {
        DLL_PROCESS_ATTACH => (),
        DLL_PROCESS_DETACH => (),
        _ => (),
    }

    1
}
```

Now, we can bring into scope MessageBoxA (also MB\_OK, and the s macro for building an easy ANSI string, check the previous tutorial if that doesn’t make sense to you) with:

```rust
use windows::Win32::UI::WindowsAndMessaging::{MessageBoxA, MB_OK};
```

Remember to check the [Windows crate](https://microsoft.github.io/windows-docs-rs/doc/windows/Win32/UI/WindowsAndMessaging/fn.MessageBoxA.html) as well as the [Win32 API](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messageboxa) for this function.

We will define a new function which will be called in **DLL\_PROCESS\_ATTACHED** that calls **MessageBoxA** as follows (note, we don’t need to be concerned with mangling here):

```rust
fn attach() {
    unsafe {
        MessageBoxA(None, s!("Hello from Rust DLL"), s!("Hello from Rust DLL"), MB_OK);
    }
}
```

## Final code

Now all we have to do is call our new function from **DLLMain**, and our final code is as follows:

```rust
use windows::{Win32::UI::WindowsAndMessaging::{MessageBoxA, MB_OK}, Win32::System::SystemServices::*,};
use windows::core::s;

#[no_mangle]
#[allow(non_snake_case)]
fn DllMain(_: usize, dw_reason: u32, _: usize) -> i32 {
    match dw_reason {
        DLL_PROCESS_ATTACH => attach(),
        _ => (),
    }

    1
}

fn attach() {
    unsafe {
        MessageBoxA(None, s!("Hello from Rust DLL"), s!("Hello from Rust DLL"), MB_OK);
    }
}
```

Catch you next time! :)