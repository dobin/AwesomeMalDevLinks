# https://github.com/KickedDroid/bof_oxide

[Skip to content](https://github.com/KickedDroid/bof_oxide#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/KickedDroid/bof_oxide) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/KickedDroid/bof_oxide) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/KickedDroid/bof_oxide) to refresh your session.Dismiss alert

{{ message }}

[KickedDroid](https://github.com/KickedDroid)/ **[bof\_oxide](https://github.com/KickedDroid/bof_oxide)** Public

- [Notifications](https://github.com/login?return_to=%2FKickedDroid%2Fbof_oxide) You must be signed in to change notification settings
- [Fork\\
3](https://github.com/login?return_to=%2FKickedDroid%2Fbof_oxide)
- [Star\\
74](https://github.com/login?return_to=%2FKickedDroid%2Fbof_oxide)


A POC for developing BOFs for Sliver, Havoc, Cobalt Strike or most COFFLoaders in Rust.


[74\\
stars](https://github.com/KickedDroid/bof_oxide/stargazers) [3\\
forks](https://github.com/KickedDroid/bof_oxide/forks) [Branches](https://github.com/KickedDroid/bof_oxide/branches) [Tags](https://github.com/KickedDroid/bof_oxide/tags) [Activity](https://github.com/KickedDroid/bof_oxide/activity)

[Star](https://github.com/login?return_to=%2FKickedDroid%2Fbof_oxide)

[Notifications](https://github.com/login?return_to=%2FKickedDroid%2Fbof_oxide) You must be signed in to change notification settings

# KickedDroid/bof\_oxide

main

[**1** Branch](https://github.com/KickedDroid/bof_oxide/branches) [**0** Tags](https://github.com/KickedDroid/bof_oxide/tags)

[Go to Branches page](https://github.com/KickedDroid/bof_oxide/branches)[Go to Tags page](https://github.com/KickedDroid/bof_oxide/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![KickedDroid](https://avatars.githubusercontent.com/u/24928676?v=4&size=40)](https://github.com/KickedDroid)[KickedDroid](https://github.com/KickedDroid/bof_oxide/commits?author=KickedDroid)<br>[Update README.md](https://github.com/KickedDroid/bof_oxide/commit/c44ddbd643d3798df0a338b3ee1ef926b1e1de3d)<br>6 months agoAug 24, 2025<br>[c44ddbd](https://github.com/KickedDroid/bof_oxide/commit/c44ddbd643d3798df0a338b3ee1ef926b1e1de3d) · 6 months agoAug 24, 2025<br>## History<br>[51 Commits](https://github.com/KickedDroid/bof_oxide/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/KickedDroid/bof_oxide/commits/main/) 51 Commits |
| [src](https://github.com/KickedDroid/bof_oxide/tree/main/src "src") | [src](https://github.com/KickedDroid/bof_oxide/tree/main/src "src") | [Working like old version](https://github.com/KickedDroid/bof_oxide/commit/8d0e1524843dd8cd4e92cf2ea55e75826a2ec4f4 "Working like old version") | 6 months agoAug 24, 2025 |
| [.gitignore](https://github.com/KickedDroid/bof_oxide/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/KickedDroid/bof_oxide/blob/main/.gitignore ".gitignore") | [Cargo overhall](https://github.com/KickedDroid/bof_oxide/commit/1f5579e61c803266752cc89b5e28ae8e4ddd2589 "Cargo overhall") | 8 months agoJun 30, 2025 |
| [README.md](https://github.com/KickedDroid/bof_oxide/blob/main/README.md "README.md") | [README.md](https://github.com/KickedDroid/bof_oxide/blob/main/README.md "README.md") | [Update README.md](https://github.com/KickedDroid/bof_oxide/commit/c44ddbd643d3798df0a338b3ee1ef926b1e1de3d "Update README.md") | 6 months agoAug 24, 2025 |
| [justfile](https://github.com/KickedDroid/bof_oxide/blob/main/justfile "justfile") | [justfile](https://github.com/KickedDroid/bof_oxide/blob/main/justfile "justfile") | [Cleanup](https://github.com/KickedDroid/bof_oxide/commit/8662dd2239c5e3dadfd0d49d58a7ae2cdcf3a54b "Cleanup") | 6 months agoAug 20, 2025 |
| View all files |

## Repository files navigation

# bof\_oxide

[Permalink: bof_oxide](https://github.com/KickedDroid/bof_oxide#bof_oxide)

A POC or Template whatever for developing BOFs for Sliver, Havoc, Cobalt Strike or most COFFLoaders.

Goals:

- Less Volitile BOFs
- Make Debugging BOFs less of a pain.
- Better Error Handling

This project was fun but ran into limitations with what I wanted. I learned a lot of lessons of which I will write a post about soon. [Here](https://kickeddroid.github.io/2025/08/22/What-I-Learned-writing-a-bof-in-rust.html) Until then check out my repository [loadstar](https://github.com/KickedDroid/loadstar).

### Build

[Permalink: Build](https://github.com/KickedDroid/bof_oxide#build)

Create objects directory

```
mkdir objects
```

Run justfile

```
just bof
```

# Usage Example

[Permalink: Usage Example](https://github.com/KickedDroid/bof_oxide#usage-example)

```
pub fn rust_bof(mut beacon: Beacon) {
    let str_arg = beacon.get_arg();
    if str_arg.is_null() {
        beacon.output("Please provide a str:\"arg\"");
    } else {
        beacon.printf("Hello %s from rust bof\0", str_arg as *mut c_char);
    }
}
```

Running the bof above with [https://github.com/hakaioffsec/coffee](https://github.com/hakaioffsec/coffee)

```
.\coffee-gnu.exe --bof-path .\test.o -- str:"World"
Hello World from rust-bof

[+] Rust BOF Completed successfully
```

```
# Terminate Gracefully
.\coffee-gnu.exe --bof-path .\test.o --
[!] Str_arg argument is required
```

Running in Sliver

[![image](https://private-user-images.githubusercontent.com/24928676/416829156-b993d6e7-1914-40f8-9d1b-a8ec7f8bc6b9.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI2OTEsIm5iZiI6MTc3MTQxMjM5MSwicGF0aCI6Ii8yNDkyODY3Ni80MTY4MjkxNTYtYjk5M2Q2ZTctMTkxNC00MGY4LTlkMWItYThlYzdmOGJjNmI5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDEwNTk1MVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWNhNzgyZDBiZTU0YjA4MTRlNDE5ZmFmN2FjYjIyOWJjYTNjNTY3OTU5MzA1OGRlNjZjNDE4MzE0MTZjMDJiMDQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.7Sxo3z-ARnIbhaHBqjBQLZYWk3Gi4dyvZfinIZBjVOg)](https://private-user-images.githubusercontent.com/24928676/416829156-b993d6e7-1914-40f8-9d1b-a8ec7f8bc6b9.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzE0MTI2OTEsIm5iZiI6MTc3MTQxMjM5MSwicGF0aCI6Ii8yNDkyODY3Ni80MTY4MjkxNTYtYjk5M2Q2ZTctMTkxNC00MGY4LTlkMWItYThlYzdmOGJjNmI5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAyMTglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMjE4VDEwNTk1MVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWNhNzgyZDBiZTU0YjA4MTRlNDE5ZmFmN2FjYjIyOWJjYTNjNTY3OTU5MzA1OGRlNjZjNDE4MzE0MTZjMDJiMDQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.7Sxo3z-ARnIbhaHBqjBQLZYWk3Gi4dyvZfinIZBjVOg)

### How it works

[Permalink: How it works](https://github.com/KickedDroid/bof_oxide#how-it-works)

This is just a wrapper around the existing Beacon Fns provided. The difference is we pass the function pointers to a Rust wrapper.

```
C -> Rust -> BeaconApi
```

The bof entry point is still `go` and it's still handled in C.

```
// Extern Rust initialize fn
extern void initialize(
    void (*beacon_output)(int, const char*, int),
    void (*beacon_format_alloc)(formatp*, int),
    void (*beacon_format_free)(formatp*),
    void (*beacon_printf)(int, const char * fmt, ...)
);

void go(char* args, int alen) {
    // Pass the fn pointers to the rust wrapper
    initialize(BeaconOutput, BeaconFormatAlloc, BeaconFormatFree, BeaconPrintf);
}
```

The rust intialize fn

```
// This is the Entrypoint for the Rust portion
// Initialize and call rust_bof
#[no_mangle]
pub extern "C" fn initialize(
    beacon_output: BeaconOutputFn,
    beacon_format_alloc: BeaconFormatAllocFn,
    beacon_format_free: BeaconFormatFreeFn,
    beacon_printf: BeaconPrintfFn,
) {
    // Pass the fn pointers to the Beacon wrapper
    let mut beacon = Beacon::new(
        beacon_output,
        beacon_format_alloc,
        beacon_format_free,
        beacon_printf,
    );

    // Call rust_bof
    rust_bof(&mut beacon);
}
```

Structure of BOF

```
➜  rust_bof git:(main) ✗ objdump -t bof_oxide.o

bof_oxide.o:     file format pe-x86-64

SYMBOL TABLE:
[  0](sec  1)(fl 0x00)(ty    0)(scl   3) (nx 1) 0x0000000000000000 .text
AUX scnlen 0x9b nreloc 3 nlnno 0 checksum 0x8f8752ca assoc 1 comdat 0
[  2](sec  5)(fl 0x00)(ty    0)(scl   3) (nx 1) 0x0000000000000000 .xdata
AUX scnlen 0xc nreloc 0 nlnno 0 checksum 0x7f2842f8 assoc 4 comdat 0
[  4](sec  2)(fl 0x00)(ty    0)(scl   3) (nx 1) 0x0000000000000000 .rdata
AUX scnlen 0x7d nreloc 0 nlnno 0 checksum 0x7fd708e1 assoc 5 comdat 0
[  6](sec  4)(fl 0x00)(ty    0)(scl   3) (nx 1) 0x0000000000000000 .pdata
AUX scnlen 0xc nreloc 3 nlnno 0 checksum 0x30cfafda assoc 7 comdat 0
[  8](sec  1)(fl 0x00)(ty   20)(scl   2) (nx 0) 0x0000000000000000 initialize
[  9](sec  1)(fl 0x00)(ty   20)(scl   2) (nx 1) 0x00000000000000a0 go
AUX tagndx 0 ttlsiz 0x0 lnnos 0 next 0
[ 11](sec  1)(fl 0x00)(ty    0)(scl   3) (nx 1) 0x00000000000000a0 .text
AUX scnlen 0x40 nreloc 5 nlnno 0
[ 13](sec  5)(fl 0x00)(ty    0)(scl   3) (nx 1) 0x000000000000000c .xdata
AUX scnlen 0xc nreloc 0 nlnno 0
[ 15](sec  4)(fl 0x00)(ty    0)(scl   3) (nx 1) 0x000000000000000c .pdata
AUX scnlen 0xc nreloc 3 nlnno 0
[ 17](sec  3)(fl 0x00)(ty    0)(scl   3) (nx 1) 0x0000000000000000 .rdata$zzz
AUX scnlen 0x1d nreloc 0 nlnno 0
[ 19](sec  0)(fl 0x00)(ty    0)(scl   2) (nx 0) 0x0000000000000000 __imp_BeaconOutput
[ 20](sec  0)(fl 0x00)(ty    0)(scl   2) (nx 0) 0x0000000000000000 __imp_BeaconFormatFree
[ 21](sec  0)(fl 0x00)(ty    0)(scl   2) (nx 0) 0x0000000000000000 __imp_BeaconPrintf
[ 22](sec  0)(fl 0x00)(ty    0)(scl   2) (nx 0) 0x0000000000000000 __imp_BeaconFormatAlloc
```

* * *

### References

[Permalink: References](https://github.com/KickedDroid/bof_oxide#references)

Header file `beacon.h` from [https://github.com/Cobalt-Strike/bof\_template/blob/main/beacon.h](https://github.com/Cobalt-Strike/bof_template/blob/main/beacon.h)

### FAFO License

[Permalink: FAFO License](https://github.com/KickedDroid/bof_oxide#fafo-license)

This is striclty for educational and research purposes. I'm not responsible for any use of this, by any means. Use at you're own risk and find out. NOTE: This probs will get you picked up immediately so good luck.

## About

A POC for developing BOFs for Sliver, Havoc, Cobalt Strike or most COFFLoaders in Rust.


### Topics

[rust](https://github.com/topics/rust "Topic: rust") [sliver](https://github.com/topics/sliver "Topic: sliver") [bof](https://github.com/topics/bof "Topic: bof") [coff](https://github.com/topics/coff "Topic: coff") [cobaltstrike](https://github.com/topics/cobaltstrike "Topic: cobaltstrike") [havoc2](https://github.com/topics/havoc2 "Topic: havoc2") [coffloader](https://github.com/topics/coffloader "Topic: coffloader")

### Resources

[Readme](https://github.com/KickedDroid/bof_oxide#readme-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/KickedDroid/bof_oxide).

[Activity](https://github.com/KickedDroid/bof_oxide/activity)

### Stars

[**74**\\
stars](https://github.com/KickedDroid/bof_oxide/stargazers)

### Watchers

[**2**\\
watching](https://github.com/KickedDroid/bof_oxide/watchers)

### Forks

[**3**\\
forks](https://github.com/KickedDroid/bof_oxide/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FKickedDroid%2Fbof_oxide&report=KickedDroid+%28user%29)

## [Releases](https://github.com/KickedDroid/bof_oxide/releases)

No releases published

## [Packages\  0](https://github.com/users/KickedDroid/packages?repo_name=bof_oxide)

No packages published

## Languages

- [Rust62.5%](https://github.com/KickedDroid/bof_oxide/search?l=rust)
- [C29.5%](https://github.com/KickedDroid/bof_oxide/search?l=c)
- [Just8.0%](https://github.com/KickedDroid/bof_oxide/search?l=just)

You can’t perform that action at this time.