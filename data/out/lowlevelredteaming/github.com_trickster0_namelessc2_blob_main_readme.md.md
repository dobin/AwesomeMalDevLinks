# https://github.com/trickster0/NamelessC2/blob/main/README.MD

[Skip to content](https://github.com/trickster0/NamelessC2/blob/main/README.MD#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/trickster0/NamelessC2/blob/main/README.MD) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/trickster0/NamelessC2/blob/main/README.MD) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/trickster0/NamelessC2/blob/main/README.MD) to refresh your session.Dismiss alert

{{ message }}

[trickster0](https://github.com/trickster0)/ **[NamelessC2](https://github.com/trickster0/NamelessC2)** Public

- [Notifications](https://github.com/login?return_to=%2Ftrickster0%2FNamelessC2) You must be signed in to change notification settings
- [Fork\\
34](https://github.com/login?return_to=%2Ftrickster0%2FNamelessC2)
- [Star\\
282](https://github.com/login?return_to=%2Ftrickster0%2FNamelessC2)


## Collapse file tree

## Files

main

Search this repository

/

# README.MD

Copy path

BlameMore file actions

BlameMore file actions

## Latest commit

[![trickster0](https://avatars.githubusercontent.com/u/20028117?v=4&size=40)](https://github.com/trickster0)[trickster0](https://github.com/trickster0/NamelessC2/commits?author=trickster0)

[Update README.MD](https://github.com/trickster0/NamelessC2/commit/d075534d4be70fed2e0d3f85c8e90ccc7ac5bc85)

2 years agoSep 26, 2024

[d075534](https://github.com/trickster0/NamelessC2/commit/d075534d4be70fed2e0d3f85c8e90ccc7ac5bc85) · 2 years agoSep 26, 2024

## History

[History](https://github.com/trickster0/NamelessC2/commits/main/README.MD)

Open commit details

[View commit history for this file.](https://github.com/trickster0/NamelessC2/commits/main/README.MD) History

32 lines (27 loc) · 2.42 KB

/

# README.MD

Top

## File metadata and controls

- Preview

- Code

- Blame


32 lines (27 loc) · 2.42 KB

[Raw](https://github.com/trickster0/NamelessC2/raw/refs/heads/main/README.MD)

Copy raw file

Download raw file

Outline

Edit and raw actions

# Nameless C2 - A C2 with all its components written in Rust.

[Permalink: Nameless C2 - A C2 with all its components written in Rust.](https://github.com/trickster0/NamelessC2/blob/main/README.MD#nameless-c2---a-c2-with-all-its-components-written-in-rust)

Nameless C2 is a small project I started for fun to get a bit familiar with Rust but I do not have any time to continue working on it,

hence I am publishing it in hope that some might find it useful to build on top of it since it needs a LOT of work.

## Another damn C2? WHY?!

[Permalink: Another damn C2? WHY?!](https://github.com/trickster0/NamelessC2/blob/main/README.MD#another-damn-c2-why)

That is totally fair to think that and I agree, I am mostly publishing it due to the fact that I have not seen another Windows Rust implant as small as 256kb (if my memory serves me right) and also has a working sleeping obfuscation method of EkkoEx. Is this the best C2 or super OPSEC? Definitely not! Is it worth playing around with it? I will leave that up to you.

## Installation Process

[Permalink: Installation Process](https://github.com/trickster0/NamelessC2/blob/main/README.MD#installation-process)

I highly recommend that you build the terminal and the implant in Windows boxes while the server should be built ideally on debian.

1. Dependencies on debian for the NamelessServer:

- sudo apt install libssl-dev libsqlite3-dev.
- goes without saying... install rust

2. Compile terminal and agent ideally with the below command.

- cargo build --release --target x86\_64-pc-windows-gnu.

## Notes

[Permalink: Notes](https://github.com/trickster0/NamelessC2/blob/main/README.MD#notes)

There are some stuff left around to take a look and discover, I am not gonna go into how to build things, don't bother opening issues, I am not gonna fix them.

- The terminal application works better in Windows than Linux.
- The implant generates a DLL with an export called DiagnosisCheck, to generate shellcode I have provided a modified sRDI which you can simply use by running


python3 ConvertToShellcode.py -c -f DiagnosisCheck NamelessImplant.dll
- Make sure you check in the implant the kill date, change the hardcoded IPs/Domains.
- Coming form PoshC2, this C2 has a similar way of obtaining the output. When the server will start,


it will generate a NamelessLog.txt which you can tail command to obtain and keep up with everything


tail -f NamelessLog.txt
- For the Rust gurus, you will notice stupid choices in the code that make absolutely no sense and I agree but I suck at Rust ¯\_(ツ)\_/¯

## Credits

[Permalink: Credits](https://github.com/trickster0/NamelessC2/blob/main/README.MD#credits)

- thanks to [https://x.com/\_yamakadi](https://x.com/_yamakadi) for his amazing work on the Clroxide that executes assemblies.
- thanks to [https://x.com/\_Kudaes](https://x.com/_Kudaes)\_ for providing his sRDI, you are a lifesaver dude.
- Thanks to [https://x.com/memN0ps](https://x.com/memN0ps) for his weird(you know what I am talking about) indirect syscall.
- Thanks to [https://x.com/lefterispan](https://x.com/lefterispan) & [https://x.com/eks\_perience](https://x.com/eks_perience) because I would not be who I am today.

You can’t perform that action at this time.