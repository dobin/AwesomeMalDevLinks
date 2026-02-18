# https://github.com/safedv/RustVEHSyscalls

[Skip to content](https://github.com/safedv/RustVEHSyscalls#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/safedv/RustVEHSyscalls) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/safedv/RustVEHSyscalls) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/safedv/RustVEHSyscalls) to refresh your session.Dismiss alert

{{ message }}

[safedv](https://github.com/safedv)/ **[RustVEHSyscalls](https://github.com/safedv/RustVEHSyscalls)** Public

- [Notifications](https://github.com/login?return_to=%2Fsafedv%2FRustVEHSyscalls) You must be signed in to change notification settings
- [Fork\\
18](https://github.com/login?return_to=%2Fsafedv%2FRustVEHSyscalls)
- [Star\\
161](https://github.com/login?return_to=%2Fsafedv%2FRustVEHSyscalls)


A Rust port of LayeredSyscall — performs indirect syscalls while generating legitimate API call stack frames by abusing VEH.


[161\\
stars](https://github.com/safedv/RustVEHSyscalls/stargazers) [18\\
forks](https://github.com/safedv/RustVEHSyscalls/forks) [Branches](https://github.com/safedv/RustVEHSyscalls/branches) [Tags](https://github.com/safedv/RustVEHSyscalls/tags) [Activity](https://github.com/safedv/RustVEHSyscalls/activity)

[Star](https://github.com/login?return_to=%2Fsafedv%2FRustVEHSyscalls)

[Notifications](https://github.com/login?return_to=%2Fsafedv%2FRustVEHSyscalls) You must be signed in to change notification settings

# safedv/RustVEHSyscalls

master

[**1** Branch](https://github.com/safedv/RustVEHSyscalls/branches) [**0** Tags](https://github.com/safedv/RustVEHSyscalls/tags)

[Go to Branches page](https://github.com/safedv/RustVEHSyscalls/branches)[Go to Tags page](https://github.com/safedv/RustVEHSyscalls/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![safedv](https://avatars.githubusercontent.com/u/48970151?v=4&size=40)](https://github.com/safedv)[safedv](https://github.com/safedv/RustVEHSyscalls/commits?author=safedv)<br>[initial commit](https://github.com/safedv/RustVEHSyscalls/commit/c5ee1dc05d819d6e49cbc810b54607ff9f19bb59)<br>2 years agoOct 31, 2024<br>[c5ee1dc](https://github.com/safedv/RustVEHSyscalls/commit/c5ee1dc05d819d6e49cbc810b54607ff9f19bb59) · 2 years agoOct 31, 2024<br>## History<br>[1 Commit](https://github.com/safedv/RustVEHSyscalls/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/safedv/RustVEHSyscalls/commits/master/) 1 Commit |
| [src](https://github.com/safedv/RustVEHSyscalls/tree/master/src "src") | [src](https://github.com/safedv/RustVEHSyscalls/tree/master/src "src") | [initial commit](https://github.com/safedv/RustVEHSyscalls/commit/c5ee1dc05d819d6e49cbc810b54607ff9f19bb59 "initial commit") | 2 years agoOct 31, 2024 |
| [.gitignore](https://github.com/safedv/RustVEHSyscalls/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/safedv/RustVEHSyscalls/blob/master/.gitignore ".gitignore") | [initial commit](https://github.com/safedv/RustVEHSyscalls/commit/c5ee1dc05d819d6e49cbc810b54607ff9f19bb59 "initial commit") | 2 years agoOct 31, 2024 |
| [Cargo.lock](https://github.com/safedv/RustVEHSyscalls/blob/master/Cargo.lock "Cargo.lock") | [Cargo.lock](https://github.com/safedv/RustVEHSyscalls/blob/master/Cargo.lock "Cargo.lock") | [initial commit](https://github.com/safedv/RustVEHSyscalls/commit/c5ee1dc05d819d6e49cbc810b54607ff9f19bb59 "initial commit") | 2 years agoOct 31, 2024 |
| [Cargo.toml](https://github.com/safedv/RustVEHSyscalls/blob/master/Cargo.toml "Cargo.toml") | [Cargo.toml](https://github.com/safedv/RustVEHSyscalls/blob/master/Cargo.toml "Cargo.toml") | [initial commit](https://github.com/safedv/RustVEHSyscalls/commit/c5ee1dc05d819d6e49cbc810b54607ff9f19bb59 "initial commit") | 2 years agoOct 31, 2024 |
| [README.md](https://github.com/safedv/RustVEHSyscalls/blob/master/README.md "README.md") | [README.md](https://github.com/safedv/RustVEHSyscalls/blob/master/README.md "README.md") | [initial commit](https://github.com/safedv/RustVEHSyscalls/commit/c5ee1dc05d819d6e49cbc810b54607ff9f19bb59 "initial commit") | 2 years agoOct 31, 2024 |
| View all files |

## Repository files navigation

# RustVEHSyscalls

[Permalink: RustVEHSyscalls](https://github.com/safedv/RustVEHSyscalls#rustvehsyscalls)

**RustVEHSyscalls** is a Rust-based port of the [LayeredSyscall](https://github.com/WKL-Sec/LayeredSyscall) project. This tool performs indirect syscalls while generating legitimate API call stack frames by abusing Vectored Exception Handling (VEH) to bypass user-land EDR hooks in Windows.

## How It Works

[Permalink: How It Works](https://github.com/safedv/RustVEHSyscalls#how-it-works)

**RustVEHSyscalls** performs indirect syscalls by abusing Vectored Exception Handling (VEH) to generate legitimate API call stack frames. By calling a standard Windows API function and setting a hardware breakpoint within it, the function's call stack is captured. This breakpoint then lets VEH redirect the process to a syscall wrapper in `ntdll.dll`, preserving the original API's call stack structure. This approach enables syscalls to appear as if they originate from legitimate Windows API calls.

### Setup and Cleanup Functions

[Permalink: Setup and Cleanup Functions](https://github.com/safedv/RustVEHSyscalls#setup-and-cleanup-functions)

**RustVEHSyscalls** provides functions to initialize and clean up the Vectored Exception Handling environment necessary for syscall interception. These functions establish the hooks needed to capture and handle indirect syscalls, ensuring clean operation and teardown.

1. **`initialize_hooks()`**:

   - Sets up two vectored exception handlers for adding and managing hardware breakpoints in the system call path. This function allocates memory for the CPU context and retrieves `ntdll.dll`'s base and end addresses for tracing purposes.
2. **`destroy_hooks()`**:

   - Cleans up by removing the added vectored exception handlers.

### Syscall Wrapper

[Permalink: Syscall Wrapper](https://github.com/safedv/RustVEHSyscalls#syscall-wrapper)

**RustVEHSyscalls** provides a `syscall!` macro that wraps several key steps:

1. **Resolving the Syscall Address and SSN**: The macro uses the **PEB** to locate `ntdll.dll` and parses its **Exception Directory** and **Export Address Table** to retrieve both the syscall’s address and System Service Number (SSN).
2. **Setting Hardware Breakpoint**: Once the syscall address and SSN are resolved, the macro sets a hardware breakpoint, allowing RustVEHSyscalls to intercept the syscall execution.
3. **Invoking the Syscall**: Finally, the macro invokes the syscall with the specified parameters, completing the indirect syscall path.

## Usage

[Permalink: Usage](https://github.com/safedv/RustVEHSyscalls#usage)

To initialize syscall interception, call `initialize_hooks()` at the start of your `main` function and `destroy_hooks()` to clean up once you're done. You can also adjust the legitimate call stack by modifying the `demofunction()` in the `hooks.rs` module.

```
/// Example function designed to maintain a clean call stack.
/// This function can be modified to call different legitimate Windows APIs.
pub unsafe extern "C" fn demofunction() {
    MessageBoxA(null_mut(), null_mut(), null_mut(), 0);
}
```

### Example: Calling `NtCreateUserProcess`

[Permalink: Example: Calling NtCreateUserProcess](https://github.com/safedv/RustVEHSyscalls#example-calling-ntcreateuserprocess)

The following example demonstrates how to invoke the `NtCreateUserProcess` syscall. Full test code is available in `lib.rs`.

```
fn main() {
    initialize_hooks(); // Set up necessary hooks

    // Initialize all necessary parameters here...

    // Call NtCreateUserProcess syscall
    let status = syscall!(
        "NtCreateUserProcess",
        OrgNtCreateUserProcess,
        &mut process_handle,
        &mut thread_handle,
        desired_access,
        desired_access,
        null_mut(),
        null_mut(),
        0,
        0,
        process_parameters,
        &mut create_info,
        attribute_list
    );

    destroy_hooks(); // Clean up hooks when done
}
```

## Disclaimer

[Permalink: Disclaimer](https://github.com/safedv/RustVEHSyscalls#disclaimer)

This project is intended **for educational and research purposes only**. Use it responsibly, as any misuse is solely your responsibility—not mine! Always follow ethical guidelines and legal frameworks when doing security research (and, you know, just in general).

## Credits

[Permalink: Credits](https://github.com/safedv/RustVEHSyscalls#credits)

Special thanks to:

- [LayeredSyscall by White Knight Labs](https://github.com/WKL-Sec/LayeredSyscall) for their work.
- [Resolving System Service Numbers Using The Exception Directory by MDsec](https://www.mdsec.co.uk/2022/04/resolving-system-service-numbers-using-the-exception-directory/) for their insights on resolving SSNs.

## Contributing

[Permalink: Contributing](https://github.com/safedv/RustVEHSyscalls#contributing)

Contributions are welcome! If you want to help improve `RustVEHSyscalls` or report bugs, feel free to open an issue or a pull request in the repository.

* * *

## About

A Rust port of LayeredSyscall — performs indirect syscalls while generating legitimate API call stack frames by abusing VEH.


### Topics

[rust-lang](https://github.com/topics/rust-lang "Topic: rust-lang") [red-team](https://github.com/topics/red-team "Topic: red-team") [indirect-syscall](https://github.com/topics/indirect-syscall "Topic: indirect-syscall") [hardware-breakpoint](https://github.com/topics/hardware-breakpoint "Topic: hardware-breakpoint")

### Resources

[Readme](https://github.com/safedv/RustVEHSyscalls#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/safedv/RustVEHSyscalls).

[Activity](https://github.com/safedv/RustVEHSyscalls/activity)

### Stars

[**161**\\
stars](https://github.com/safedv/RustVEHSyscalls/stargazers)

### Watchers

[**1**\\
watching](https://github.com/safedv/RustVEHSyscalls/watchers)

### Forks

[**18**\\
forks](https://github.com/safedv/RustVEHSyscalls/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fsafedv%2FRustVEHSyscalls&report=safedv+%28user%29)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/safedv/RustVEHSyscalls).

## Languages

- [Rust100.0%](https://github.com/safedv/RustVEHSyscalls/search?l=rust)

You can’t perform that action at this time.