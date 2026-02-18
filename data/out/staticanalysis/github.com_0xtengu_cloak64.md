# https://github.com/0xtengu/Cloak64

[Skip to content](https://github.com/0xtengu/Cloak64#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/0xtengu/Cloak64) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/0xtengu/Cloak64) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/0xtengu/Cloak64) to refresh your session.Dismiss alert

{{ message }}

[0xtengu](https://github.com/0xtengu)/ **[Cloak64](https://github.com/0xtengu/Cloak64)** Public

- [Notifications](https://github.com/login?return_to=%2F0xtengu%2FCloak64) You must be signed in to change notification settings
- [Fork\\
3](https://github.com/login?return_to=%2F0xtengu%2FCloak64)
- [Star\\
48](https://github.com/login?return_to=%2F0xtengu%2FCloak64)


### License

[MIT license](https://github.com/0xtengu/Cloak64/blob/main/LICENSE)

[48\\
stars](https://github.com/0xtengu/Cloak64/stargazers) [3\\
forks](https://github.com/0xtengu/Cloak64/forks) [Branches](https://github.com/0xtengu/Cloak64/branches) [Tags](https://github.com/0xtengu/Cloak64/tags) [Activity](https://github.com/0xtengu/Cloak64/activity)

[Star](https://github.com/login?return_to=%2F0xtengu%2FCloak64)

[Notifications](https://github.com/login?return_to=%2F0xtengu%2FCloak64) You must be signed in to change notification settings

# 0xtengu/Cloak64

main

[**1** Branch](https://github.com/0xtengu/Cloak64/branches) [**0** Tags](https://github.com/0xtengu/Cloak64/tags)

[Go to Branches page](https://github.com/0xtengu/Cloak64/branches)[Go to Tags page](https://github.com/0xtengu/Cloak64/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![0xtengu](https://avatars.githubusercontent.com/u/184171011?v=4&size=40)](https://github.com/0xtengu)[0xtengu](https://github.com/0xtengu/Cloak64/commits?author=0xtengu)<br>[Update README.md](https://github.com/0xtengu/Cloak64/commit/0f71a6961e9045a42ee9744293431b0a374606dc)<br>2 months agoDec 20, 2025<br>[0f71a69](https://github.com/0xtengu/Cloak64/commit/0f71a6961e9045a42ee9744293431b0a374606dc) · 2 months agoDec 20, 2025<br>## History<br>[13 Commits](https://github.com/0xtengu/Cloak64/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/0xtengu/Cloak64/commits/main/) 13 Commits |
| [LICENSE](https://github.com/0xtengu/Cloak64/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/0xtengu/Cloak64/blob/main/LICENSE "LICENSE") | [Create LICENSE](https://github.com/0xtengu/Cloak64/commit/7194ef1df93d02faa577b500cfb84071b37ec611 "Create LICENSE") | 6 months agoAug 18, 2025 |
| [README.md](https://github.com/0xtengu/Cloak64/blob/main/README.md "README.md") | [README.md](https://github.com/0xtengu/Cloak64/blob/main/README.md "README.md") | [Update README.md](https://github.com/0xtengu/Cloak64/commit/0f71a6961e9045a42ee9744293431b0a374606dc "Update README.md") | 2 months agoDec 20, 2025 |
| [cloak.asm](https://github.com/0xtengu/Cloak64/blob/main/cloak.asm "cloak.asm") | [cloak.asm](https://github.com/0xtengu/Cloak64/blob/main/cloak.asm "cloak.asm") | [Update cloak.asm](https://github.com/0xtengu/Cloak64/commit/9a4b67795df65af1a6bbb071b5b62d383c255eb6 "Update cloak.asm") | 6 months agoAug 19, 2025 |
| View all files |

## Repository files navigation

Warning

Use responsibly.

This project is licensed under the [MIT License](https://github.com/0xtengu/Cloak64/blob/main/LICENSE).

The author takes no liability for misuse, damage, or unintended consequences.

Note

Inspired by [https://github.com/0xf00sec/Vx](https://github.com/0xf00sec/Vx)

```
+-------------------------------------------------------+
|                      CLOAK64                          |
|           Metamorphic Decoder-Stub Generator          |
+-------------------------------------------------------+

>> what is it?

CLOAK64 is a metamorphic code engine for x86_64 Windows that generates
unique decoder stubs with metamorphic characteristics. Each generation
produces functionally identical but different code.

[+] target: Windows 11 24H2 (build 26100), x64

---[ 0x01 ]----------------[ what's in the box ]---------------------

[+] PolymorphicEngine
    decoder generator with metamorphic integration

[+] MetamorphicEngine
    instruction variants (XOR / ADD / SUB / ROL)

[+] Bootstrap
    15–16 byte position-independent loader

[+] GenerateFibonacciKeys
    entropy-seeded fibonacci key derivation

[+] Configure
    register and algorithm selection

[+] MetamorphicPointer
    INC vs ADD pointer advancement variants

[+] GenerateTrash
    multi-pattern junk instruction injection

[+] EmitJnzBackToSaved
    adaptable short / long jump emission

[+] ApplyEncryption
    inverse algorithm payload encryption

[+] ResetGlobalState
    state initialization with RDTSC entropy

---[ 0x02 ]----------------[ what does it do ]----------------------

0x1 generates RDTSC + fibonacci cryptographic keys with entropy mixing
0x2 configures metamorphic parameters (registers, algorithms, profiles)
0x3 encrypts payload using inverse of selected decryption algorithm
0x4 generates bootstrap loader (CALL / POP / LEA | ADD / JMP sequence)
0x5 creates decoder loop with variable features
0x6 applies metamorphic variants to algorithms
0x7 outputs executable blob with cloaked signature patterns

---[ 0x03 ]----------------[ features ]----------------------------

[+] algorithms
    XOR / ADD / SUB / ROL

    sizes
      XOR 2 / 6 / 10
      ADD 2 / 6 / 10
      SUB 2 / 6 / 10
      ROL 2 / 6

    forms
      direct (2)
        OP [RDI], BL

      load-op-store (6)
        MOV AL, [RDI]
        OP  AL, BL
        MOV [RDI], AL

      extended (10)
        LODSB
        OP
        STOSB

    note
      for ROL direct use
        ROL byte [RDI], 1

[+] crypto pairs
    XOR <-> XOR
    ADD -> SUB
    SUB -> ADD
    ROR -> ROL

[+] metamorphism
    same semantics, different instruction sequences

[+] register selection
    RegBase / RegCount / RegKey (auto-resolve)

[+] keys
    RDTSC + fibonacci + transforms

[+] addressing
    CALL / POP (RIP-relative), full PIC

[+] jumps
    adaptive short / long selection

[+] pointer advance
    INC RDI
    ADD RDI, 1

[+] junk injection
    NOPs, reg ops, PUSH / POP (multi-pattern)

[+] bootstrap
    15–16 bytes (validated)

[+] layout
    64-byte key section
    three-layer architecture

[+] entropy output
    masks static signatures

[+] dependencies
    bootstrap has no API calls

[+] errors
    LastErrorCode tracking

[+] size limits
    decoder <= 8 KB
    payload <= 64 KB
    scratch <= 16 KB

---[ 0x04 ]----------------[ execution flow ]----------------------

BUILD-TIME GENERATION
--------------------

0x1 Generate Keys
    RDTSC entropy + fibonacci math
    produces UserKey / PrimaryKey / SecondaryKey
    seeds PRNG for subsequent operations

0x2 Configure Engine
    select RegBase (RBX / RDX / RSI / RDI)
    select RegCount (avoids RegBase)
    select RegKey (avoids both)
    select algorithm index (0-3)
    select metamorphic profile (0-7)

0x3 ApplyEncryption
    XOR -> XOR with rolling key
    ADD -> ADD with rolling key (decrypt via SUB)
    SUB -> SUB with rolling key (decrypt via ADD)
    ROR -> ROR 1 bit per byte (decrypt via ROL)

0x4 Generate Bootstrap
    CALL next / POP RAX (RIP discovery)
    choose LEA or ADD form (randomized)
    set RDI pointer
    JMP RAX -> decoder
    size must be exactly 15–16 bytes

0x5 PolymorphicEngine
    initialize key (MOV r64, imm64)
    RIP calc via CALL / POP
    LEA decoder address
    MOV payload size -> counter
    metamorphic decode loop
    trash code injection
    pointer increment (INC or ADD)
    DEC / JNZ loop
    RET -> decrypted payload

0x6 Assemble Final Layout
    layout:
      [bootstrap 15–16B]
      [key 64B]
      [decoder variable]
      [encrypted payload]

    patch displacements
    validate total size
    return engine size (or 0 on error)

---[ runtime execution flow ]---------------------------------------

0x1 Bootstrap
    CALL / POP RIP
    LEA or ADD adjust
    MOV RDI, RAX
    JMP RAX -> decoder

0x2 Decoder
    MOV RBX, transformed_key
    CALL / POP
    LEA base
    MOV RDI, base
    MOV RCX, payload_size

    loop
      decode op (variant)
      ROL RBX, 1
      insert junk
      INC RDI or ADD RDI, 1
      DEC RCX
      JNZ loop_start

    RET -> payload

0x3 Decrypted Payload
    restored in memory
    obfuscation removed
    original code executes

EOF
```

## About

No description, website, or topics provided.


### Resources

[Readme](https://github.com/0xtengu/Cloak64#readme-ov-file)

### License

[MIT license](https://github.com/0xtengu/Cloak64#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/0xtengu/Cloak64).

[Activity](https://github.com/0xtengu/Cloak64/activity)

### Stars

[**48**\\
stars](https://github.com/0xtengu/Cloak64/stargazers)

### Watchers

[**1**\\
watching](https://github.com/0xtengu/Cloak64/watchers)

### Forks

[**3**\\
forks](https://github.com/0xtengu/Cloak64/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2F0xtengu%2FCloak64&report=0xtengu+%28user%29)

## [Releases](https://github.com/0xtengu/Cloak64/releases)

No releases published

## [Packages\  0](https://github.com/users/0xtengu/packages?repo_name=Cloak64)

No packages published

## Languages

- [Assembly100.0%](https://github.com/0xtengu/Cloak64/search?l=assembly)

You can’t perform that action at this time.