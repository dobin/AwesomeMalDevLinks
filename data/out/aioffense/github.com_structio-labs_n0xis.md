# https://github.com/Structio-labs/N0xis

[Skip to content](https://github.com/Structio-labs/N0xis#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Structio-labs/N0xis) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Structio-labs/N0xis) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Structio-labs/N0xis) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/Structio-labs/N0xis/branches) [**2** Tags](https://github.com/Structio-labs/N0xis/tags)

[Go to Branches page](https://github.com/Structio-labs/N0xis/branches)[Go to Tags page](https://github.com/Structio-labs/N0xis/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![reLargo](https://avatars.githubusercontent.com/u/324685348?v=4&size=40)](https://github.com/reLargo)[reLargo](https://github.com/Structio-labs/N0xis/commits?author=reLargo)

[roadmap: language-aware analysis, the runtime's own tables first](https://github.com/Structio-labs/N0xis/commit/a96d9dc4e0c232af673a4161948b2b6c546fa552)

Open commit detailssuccess

3 days agoOct 6, 2026

[a96d9dc](https://github.com/Structio-labs/N0xis/commit/a96d9dc4e0c232af673a4161948b2b6c546fa552) · 3 days agoOct 6, 2026

## History

[71 Commits](https://github.com/Structio-labs/N0xis/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/Structio-labs/N0xis/commits/main/) 71 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [.github/workflows](https://github.com/Structio-labs/N0xis/tree/main/.github/workflows "This path skips through empty directories") | [.github/workflows](https://github.com/Structio-labs/N0xis/tree/main/.github/workflows "This path skips through empty directories") | [Remove the companion-window crate](https://github.com/Structio-labs/N0xis/commit/fef0cdf7c78ea5317ea058b282cd5e8a32e57e8f "Remove the companion-window crate  The workspace carried a desktop overlay crate built around one game's input mechanic. It is gone, with its docs, and with every mention of it in the concept, the map, the roadmap, CI comments, scripts and crate comments. The shared capabilities it used (address tables, `input probe`, the live process adapter, plugins) stay; Cargo.lock drops the GUI stack only it pulled in (493 to 140 packages, no version changed).  Alongside: the concept-grep core module and its types take the command's name; a test that searched install paths named after a product now reads its roots from N0XIS_IL2CPP_ROOTS and skips, saying so, when that is unset; a ROADMAP line that compared N0xis with other tools is gone; and the last passages describing that game's input mechanic now say what they mean in neutral words.  Gate: 794 tests pass, clippy clean on Linux and the Windows target, the crate-boundary check passes.") | 5 days agoOct 5, 2026 |
| [crates](https://github.com/Structio-labs/N0xis/tree/main/crates "crates") | [crates](https://github.com/Structio-labs/N0xis/tree/main/crates "crates") | [pdb: name and bound a PE's functions from its matching PDB](https://github.com/Structio-labs/N0xis/commit/58f9038134ee2088e57cbebf6a0878792cf622ef "pdb: name and bound a PE's functions from its matching PDB  Gap-closing item 1, M1's local half. A PE whose CodeView record names a PDB is named from a matching one in every command: each function's name, and its length where a procedure record states it. A static function with no export, no public name and no unwind entry is now named and bounded; without the PDB it stays `sub_…`, as before.  Which file: beside the image under the name the linker wrote, the path it wrote, then the project's symbol store (`.n0x/symbols/`, a symbol server's layout). A PDB is used only when its information stream's GUID and its debug-information stream's age equal the image's record; one of another build is reported in `profile` and never used. A function the PDB places outside the image's executable sections, or running past their end, is left out and counted.  `symbols add` keeps a PDB in the store after the same check, through the registry, so `serve` and an agent reach it too. `profile` reports which PDB was used, or where it looked and what it found there.  The name order was spelled out by hand at five places as nested `ChainedSymbols`; it is now one `StaticNames`, so a new source is added once. `stated_functions` takes the PDB's extents where the image's own table states none.  Checked on the fixture built from known source (exact names, addresses and lengths; a copy with one byte of its GUID or its age changed is refused; a raised information-stream age still matches), and on five system DLLs with their vendor's public PDBs against llvm-pdbutil: all 18 927 function addresses listed, each named as llvm-undname reads it but for spelling (59, each inspected). Calibrated: matching on the information stream's age, or on any identity, fails a test.  Also fixes the crate count README and MAP gave, which the previous commit left at 14 and failed CI on.") | 3 days agoOct 6, 2026 |
| [docs](https://github.com/Structio-labs/N0xis/tree/main/docs "docs") | [docs](https://github.com/Structio-labs/N0xis/tree/main/docs "docs") | [pdb: name and bound a PE's functions from its matching PDB](https://github.com/Structio-labs/N0xis/commit/58f9038134ee2088e57cbebf6a0878792cf622ef "pdb: name and bound a PE's functions from its matching PDB  Gap-closing item 1, M1's local half. A PE whose CodeView record names a PDB is named from a matching one in every command: each function's name, and its length where a procedure record states it. A static function with no export, no public name and no unwind entry is now named and bounded; without the PDB it stays `sub_…`, as before.  Which file: beside the image under the name the linker wrote, the path it wrote, then the project's symbol store (`.n0x/symbols/`, a symbol server's layout). A PDB is used only when its information stream's GUID and its debug-information stream's age equal the image's record; one of another build is reported in `profile` and never used. A function the PDB places outside the image's executable sections, or running past their end, is left out and counted.  `symbols add` keeps a PDB in the store after the same check, through the registry, so `serve` and an agent reach it too. `profile` reports which PDB was used, or where it looked and what it found there.  The name order was spelled out by hand at five places as nested `ChainedSymbols`; it is now one `StaticNames`, so a new source is added once. `stated_functions` takes the PDB's extents where the image's own table states none.  Checked on the fixture built from known source (exact names, addresses and lengths; a copy with one byte of its GUID or its age changed is refused; a raised information-stream age still matches), and on five system DLLs with their vendor's public PDBs against llvm-pdbutil: all 18 927 function addresses listed, each named as llvm-undname reads it but for spelling (59, each inspected). Calibrated: matching on the information stream's age, or on any identity, fails a test.  Also fixes the crate count README and MAP gave, which the previous commit left at 14 and failed CI on.") | 3 days agoOct 6, 2026 |
| [examples/config-demo](https://github.com/Structio-labs/N0xis/tree/main/examples/config-demo "This path skips through empty directories") | [examples/config-demo](https://github.com/Structio-labs/N0xis/tree/main/examples/config-demo "This path skips through empty directories") | [docs: a config-decryption demo replaces the hp demo; neutral examples](https://github.com/Structio-labs/N0xis/commit/2b8aaf24362ba108d19101efab843fe30791d9df "docs: a config-decryption demo replaces the hp demo; neutral examples  The animation at the top of the README showed a program losing \"hp\", which framed the tool as a game trainer. The new example is the question a reverse engineer actually asks: a program keeps its settings encrypted and decrypts them into memory; find the plaintext (`scan aob`), put a hardware watchpoint on it (`provenance trace`), and get the code that wrote it. The answer is the decryption loop, with its rolling key: `v1 + (v1 * 2) * 4 + 7`, which is the source's `key * 13 + 7`.  Checked on Linux, gcc -O2 -g: the scan finds the plaintext once, at the address nm gives `config`; the write is the byte store objdump shows at decrypt_config+0x36, inside the function nm names; the loop bound is the plaintext's 47 bytes. The README shows that run's output and says what it does not name yet (the symbols), and the recording is the real script, rerunnable with examples/config-demo/demo.sh.  The quickstart now uses `app.exe` instead of `game.exe`, `profile` reports \"runtime hints\", and the runtime formats (LuaJIT bytecode, Bitsquid, IL2CPP) come last in what names get recovered from.") | 5 days agoOct 5, 2026 |
| [oracle](https://github.com/Structio-labs/N0xis/tree/main/oracle "oracle") | [oracle](https://github.com/Structio-labs/N0xis/tree/main/oracle "oracle") | [oracle: keep Python bytecode out of the tree](https://github.com/Structio-labs/N0xis/commit/9a71c8e813ff6921f892733e0b1790aee3acdec1 "oracle: keep Python bytecode out of the tree  run.sh imports win_check.py to reuse its PE parser, which left a __pycache__ directory in oracle/windows after every run. Run that step with `python3 -B` and ignore __pycache__ for the helper scripts in general.") | 5 days agoOct 4, 2026 |
| [scripts](https://github.com/Structio-labs/N0xis/tree/main/scripts "scripts") | [scripts](https://github.com/Structio-labs/N0xis/tree/main/scripts "scripts") | [pdb: read a program database behind our own types, fuzzed from the start](https://github.com/Structio-labs/N0xis/commit/df4ef295765e86b7f0796bb81f6dba2af87632ef "pdb: read a program database behind our own types, fuzzed from the start  The first slice of gap-closing item 1 (M1): what a PDB says about an image's functions — where each starts, its length when a procedure record states it, and its name — through `n0xis-pdb`, with `pdb2` behind the crate's own types.  Which PDB belongs to an image is the GUID of the PDB's information stream with the age of its debug-information stream. The information stream's own age is not the one: measured on five system DLLs and the public PDBs their vendor serves, every image records age 1, every DBI stream says 1, and the information streams say 2 to 4.  A fixture built here from known source (fixtures/README.md) is read back exactly: the five functions with the addresses and lengths llvm-pdbutil gives, the static found only in its module's stream, and the public table's count of functions.  tests/mutated.rs reads 2 000 corrupted copies under an allocation cap and a deadline. Its first run made the reader panic on 9: it adds the DBI header's substream sizes without checking, and a cleared page overflows the sum. A release build would have wrapped silently and read on from the wrong offset. The reader is now built with overflow checks in release too, every call into it is guarded, and a stop is an error about the file. The cap was calibrated by sizing a buffer from a header field: the test then fails.  The boundary check now keeps the crate and its reader out of the pure crates; calibrated by declaring the crate pure, which fails.") | 3 days agoOct 6, 2026 |
| [signatures](https://github.com/Structio-labs/N0xis/tree/main/signatures "signatures") | [signatures](https://github.com/Structio-labs/N0xis/tree/main/signatures "signatures") | [N0xis — AI-first reverse-engineering toolkit](https://github.com/Structio-labs/N0xis/commit/3d0c5784dcfc8516159207b3796a5ec339f53c50 "N0xis — AI-first reverse-engineering toolkit  Static analysis, an SSA decompiler, live-process memory, and provenance, driven from a CLI and an MCP server that speak the same JSON.  This is a fresh public history. The project's development history is preserved privately; it is not part of this repository.") | last monthSep 11, 2026 |
| [.gitattributes](https://github.com/Structio-labs/N0xis/blob/main/.gitattributes ".gitattributes") | [.gitattributes](https://github.com/Structio-labs/N0xis/blob/main/.gitattributes ".gitattributes") | [N0xis — AI-first reverse-engineering toolkit](https://github.com/Structio-labs/N0xis/commit/3d0c5784dcfc8516159207b3796a5ec339f53c50 "N0xis — AI-first reverse-engineering toolkit  Static analysis, an SSA decompiler, live-process memory, and provenance, driven from a CLI and an MCP server that speak the same JSON.  This is a fresh public history. The project's development history is preserved privately; it is not part of this repository.") | last monthSep 11, 2026 |
| [.gitignore](https://github.com/Structio-labs/N0xis/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/Structio-labs/N0xis/blob/main/.gitignore ".gitignore") | [docs: describe targets by their shape, not as games, across the engin…](https://github.com/Structio-labs/N0xis/commit/6f177a53f3be75da14ad0830dd6bc8078761042b "docs: describe targets by their shape, not as games, across the engine's comments  Code comments, doc comments, manifests and prose outside the CLI and the HUD called targets games, titles and players, and cited the IL2CPP runtime's layouts by a commercial engine's name. They now say what the thing is: a process, an application, a launcher executable, the IL2CPP runtime's own headers, runtimes from 2018.1 on. Nothing else changed: no code, no test expectation, no number (the only new digits are the \"2\" of IL2CPP where it replaced a product name), and Bevy stays where it names the plugin-architecture model.  Left on purpose: identifiers the CLI uses (`gamegrep`), real file and module names code matches on (`GameAssembly.dll`), test fixture data, and real runtime strings.") | 5 days agoOct 5, 2026 |
| [CHANGELOG.md](https://github.com/Structio-labs/N0xis/blob/main/CHANGELOG.md "CHANGELOG.md") | [CHANGELOG.md](https://github.com/Structio-labs/N0xis/blob/main/CHANGELOG.md "CHANGELOG.md") | [pdb: name and bound a PE's functions from its matching PDB](https://github.com/Structio-labs/N0xis/commit/58f9038134ee2088e57cbebf6a0878792cf622ef "pdb: name and bound a PE's functions from its matching PDB  Gap-closing item 1, M1's local half. A PE whose CodeView record names a PDB is named from a matching one in every command: each function's name, and its length where a procedure record states it. A static function with no export, no public name and no unwind entry is now named and bounded; without the PDB it stays `sub_…`, as before.  Which file: beside the image under the name the linker wrote, the path it wrote, then the project's symbol store (`.n0x/symbols/`, a symbol server's layout). A PDB is used only when its information stream's GUID and its debug-information stream's age equal the image's record; one of another build is reported in `profile` and never used. A function the PDB places outside the image's executable sections, or running past their end, is left out and counted.  `symbols add` keeps a PDB in the store after the same check, through the registry, so `serve` and an agent reach it too. `profile` reports which PDB was used, or where it looked and what it found there.  The name order was spelled out by hand at five places as nested `ChainedSymbols`; it is now one `StaticNames`, so a new source is added once. `stated_functions` takes the PDB's extents where the image's own table states none.  Checked on the fixture built from known source (exact names, addresses and lengths; a copy with one byte of its GUID or its age changed is refused; a raised information-stream age still matches), and on five system DLLs with their vendor's public PDBs against llvm-pdbutil: all 18 927 function addresses listed, each named as llvm-undname reads it but for spelling (59, each inspected). Calibrated: matching on the information stream's age, or on any identity, fails a test.  Also fixes the crate count README and MAP gave, which the previous commit left at 14 and failed CI on.") | 3 days agoOct 6, 2026 |
| [COMMERCIAL.md](https://github.com/Structio-labs/N0xis/blob/main/COMMERCIAL.md "COMMERCIAL.md") | [COMMERCIAL.md](https://github.com/Structio-labs/N0xis/blob/main/COMMERCIAL.md "COMMERCIAL.md") | [N0xis — AI-first reverse-engineering toolkit](https://github.com/Structio-labs/N0xis/commit/3d0c5784dcfc8516159207b3796a5ec339f53c50 "N0xis — AI-first reverse-engineering toolkit  Static analysis, an SSA decompiler, live-process memory, and provenance, driven from a CLI and an MCP server that speak the same JSON.  This is a fresh public history. The project's development history is preserved privately; it is not part of this repository.") | last monthSep 11, 2026 |
| [CONCEPT.md](https://github.com/Structio-labs/N0xis/blob/main/CONCEPT.md "CONCEPT.md") | [CONCEPT.md](https://github.com/Structio-labs/N0xis/blob/main/CONCEPT.md "CONCEPT.md") | [Remove the companion-window crate](https://github.com/Structio-labs/N0xis/commit/fef0cdf7c78ea5317ea058b282cd5e8a32e57e8f "Remove the companion-window crate  The workspace carried a desktop overlay crate built around one game's input mechanic. It is gone, with its docs, and with every mention of it in the concept, the map, the roadmap, CI comments, scripts and crate comments. The shared capabilities it used (address tables, `input probe`, the live process adapter, plugins) stay; Cargo.lock drops the GUI stack only it pulled in (493 to 140 packages, no version changed).  Alongside: the concept-grep core module and its types take the command's name; a test that searched install paths named after a product now reads its roots from N0XIS_IL2CPP_ROOTS and skips, saying so, when that is unset; a ROADMAP line that compared N0xis with other tools is gone; and the last passages describing that game's input mechanic now say what they mean in neutral words.  Gate: 794 tests pass, clippy clean on Linux and the Windows target, the crate-boundary check passes.") | 5 days agoOct 5, 2026 |
| [CONTRIBUTING.md](https://github.com/Structio-labs/N0xis/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [CONTRIBUTING.md](https://github.com/Structio-labs/N0xis/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [Remove the companion-window crate](https://github.com/Structio-labs/N0xis/commit/fef0cdf7c78ea5317ea058b282cd5e8a32e57e8f "Remove the companion-window crate  The workspace carried a desktop overlay crate built around one game's input mechanic. It is gone, with its docs, and with every mention of it in the concept, the map, the roadmap, CI comments, scripts and crate comments. The shared capabilities it used (address tables, `input probe`, the live process adapter, plugins) stay; Cargo.lock drops the GUI stack only it pulled in (493 to 140 packages, no version changed).  Alongside: the concept-grep core module and its types take the command's name; a test that searched install paths named after a product now reads its roots from N0XIS_IL2CPP_ROOTS and skips, saying so, when that is unset; a ROADMAP line that compared N0xis with other tools is gone; and the last passages describing that game's input mechanic now say what they mean in neutral words.  Gate: 794 tests pass, clippy clean on Linux and the Windows target, the crate-boundary check passes.") | 5 days agoOct 5, 2026 |
| [Cargo.lock](https://github.com/Structio-labs/N0xis/blob/main/Cargo.lock "Cargo.lock") | [Cargo.lock](https://github.com/Structio-labs/N0xis/blob/main/Cargo.lock "Cargo.lock") | [pdb: name and bound a PE's functions from its matching PDB](https://github.com/Structio-labs/N0xis/commit/58f9038134ee2088e57cbebf6a0878792cf622ef "pdb: name and bound a PE's functions from its matching PDB  Gap-closing item 1, M1's local half. A PE whose CodeView record names a PDB is named from a matching one in every command: each function's name, and its length where a procedure record states it. A static function with no export, no public name and no unwind entry is now named and bounded; without the PDB it stays `sub_…`, as before.  Which file: beside the image under the name the linker wrote, the path it wrote, then the project's symbol store (`.n0x/symbols/`, a symbol server's layout). A PDB is used only when its information stream's GUID and its debug-information stream's age equal the image's record; one of another build is reported in `profile` and never used. A function the PDB places outside the image's executable sections, or running past their end, is left out and counted.  `symbols add` keeps a PDB in the store after the same check, through the registry, so `serve` and an agent reach it too. `profile` reports which PDB was used, or where it looked and what it found there.  The name order was spelled out by hand at five places as nested `ChainedSymbols`; it is now one `StaticNames`, so a new source is added once. `stated_functions` takes the PDB's extents where the image's own table states none.  Checked on the fixture built from known source (exact names, addresses and lengths; a copy with one byte of its GUID or its age changed is refused; a raised information-stream age still matches), and on five system DLLs with their vendor's public PDBs against llvm-pdbutil: all 18 927 function addresses listed, each named as llvm-undname reads it but for spelling (59, each inspected). Calibrated: matching on the information stream's age, or on any identity, fails a test.  Also fixes the crate count README and MAP gave, which the previous commit left at 14 and failed CI on.") | 3 days agoOct 6, 2026 |
| [Cargo.toml](https://github.com/Structio-labs/N0xis/blob/main/Cargo.toml "Cargo.toml") | [Cargo.toml](https://github.com/Structio-labs/N0xis/blob/main/Cargo.toml "Cargo.toml") | [pdb: read a program database behind our own types, fuzzed from the start](https://github.com/Structio-labs/N0xis/commit/df4ef295765e86b7f0796bb81f6dba2af87632ef "pdb: read a program database behind our own types, fuzzed from the start  The first slice of gap-closing item 1 (M1): what a PDB says about an image's functions — where each starts, its length when a procedure record states it, and its name — through `n0xis-pdb`, with `pdb2` behind the crate's own types.  Which PDB belongs to an image is the GUID of the PDB's information stream with the age of its debug-information stream. The information stream's own age is not the one: measured on five system DLLs and the public PDBs their vendor serves, every image records age 1, every DBI stream says 1, and the information streams say 2 to 4.  A fixture built here from known source (fixtures/README.md) is read back exactly: the five functions with the addresses and lengths llvm-pdbutil gives, the static found only in its module's stream, and the public table's count of functions.  tests/mutated.rs reads 2 000 corrupted copies under an allocation cap and a deadline. Its first run made the reader panic on 9: it adds the DBI header's substream sizes without checking, and a cleared page overflows the sum. A release build would have wrapped silently and read on from the wrong offset. The reader is now built with overflow checks in release too, every call into it is guarded, and a stop is an error about the file. The cap was calibrated by sizing a buffer from a header field: the test then fails.  The boundary check now keeps the crate and its reader out of the pure crates; calibrated by declaring the crate pure, which fails.") | 3 days agoOct 6, 2026 |
| [LICENSE](https://github.com/Structio-labs/N0xis/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/Structio-labs/N0xis/blob/main/LICENSE "LICENSE") | [N0xis — AI-first reverse-engineering toolkit](https://github.com/Structio-labs/N0xis/commit/3d0c5784dcfc8516159207b3796a5ec339f53c50 "N0xis — AI-first reverse-engineering toolkit  Static analysis, an SSA decompiler, live-process memory, and provenance, driven from a CLI and an MCP server that speak the same JSON.  This is a fresh public history. The project's development history is preserved privately; it is not part of this repository.") | last monthSep 11, 2026 |
| [MAP.md](https://github.com/Structio-labs/N0xis/blob/main/MAP.md "MAP.md") | [MAP.md](https://github.com/Structio-labs/N0xis/blob/main/MAP.md "MAP.md") | [pdb: name and bound a PE's functions from its matching PDB](https://github.com/Structio-labs/N0xis/commit/58f9038134ee2088e57cbebf6a0878792cf622ef "pdb: name and bound a PE's functions from its matching PDB  Gap-closing item 1, M1's local half. A PE whose CodeView record names a PDB is named from a matching one in every command: each function's name, and its length where a procedure record states it. A static function with no export, no public name and no unwind entry is now named and bounded; without the PDB it stays `sub_…`, as before.  Which file: beside the image under the name the linker wrote, the path it wrote, then the project's symbol store (`.n0x/symbols/`, a symbol server's layout). A PDB is used only when its information stream's GUID and its debug-information stream's age equal the image's record; one of another build is reported in `profile` and never used. A function the PDB places outside the image's executable sections, or running past their end, is left out and counted.  `symbols add` keeps a PDB in the store after the same check, through the registry, so `serve` and an agent reach it too. `profile` reports which PDB was used, or where it looked and what it found there.  The name order was spelled out by hand at five places as nested `ChainedSymbols`; it is now one `StaticNames`, so a new source is added once. `stated_functions` takes the PDB's extents where the image's own table states none.  Checked on the fixture built from known source (exact names, addresses and lengths; a copy with one byte of its GUID or its age changed is refused; a raised information-stream age still matches), and on five system DLLs with their vendor's public PDBs against llvm-pdbutil: all 18 927 function addresses listed, each named as llvm-undname reads it but for spelling (59, each inspected). Calibrated: matching on the information stream's age, or on any identity, fails a test.  Also fixes the crate count README and MAP gave, which the previous commit left at 14 and failed CI on.") | 3 days agoOct 6, 2026 |
| [README.md](https://github.com/Structio-labs/N0xis/blob/main/README.md "README.md") | [README.md](https://github.com/Structio-labs/N0xis/blob/main/README.md "README.md") | [pdb: name and bound a PE's functions from its matching PDB](https://github.com/Structio-labs/N0xis/commit/58f9038134ee2088e57cbebf6a0878792cf622ef "pdb: name and bound a PE's functions from its matching PDB  Gap-closing item 1, M1's local half. A PE whose CodeView record names a PDB is named from a matching one in every command: each function's name, and its length where a procedure record states it. A static function with no export, no public name and no unwind entry is now named and bounded; without the PDB it stays `sub_…`, as before.  Which file: beside the image under the name the linker wrote, the path it wrote, then the project's symbol store (`.n0x/symbols/`, a symbol server's layout). A PDB is used only when its information stream's GUID and its debug-information stream's age equal the image's record; one of another build is reported in `profile` and never used. A function the PDB places outside the image's executable sections, or running past their end, is left out and counted.  `symbols add` keeps a PDB in the store after the same check, through the registry, so `serve` and an agent reach it too. `profile` reports which PDB was used, or where it looked and what it found there.  The name order was spelled out by hand at five places as nested `ChainedSymbols`; it is now one `StaticNames`, so a new source is added once. `stated_functions` takes the PDB's extents where the image's own table states none.  Checked on the fixture built from known source (exact names, addresses and lengths; a copy with one byte of its GUID or its age changed is refused; a raised information-stream age still matches), and on five system DLLs with their vendor's public PDBs against llvm-pdbutil: all 18 927 function addresses listed, each named as llvm-undname reads it but for spelling (59, each inspected). Calibrated: matching on the information stream's age, or on any identity, fails a test.  Also fixes the crate count README and MAP gave, which the previous commit left at 14 and failed CI on.") | 3 days agoOct 6, 2026 |
| [ROADMAP.md](https://github.com/Structio-labs/N0xis/blob/main/ROADMAP.md "ROADMAP.md") | [ROADMAP.md](https://github.com/Structio-labs/N0xis/blob/main/ROADMAP.md "ROADMAP.md") | [roadmap: language-aware analysis, the runtime's own tables first](https://github.com/Structio-labs/N0xis/commit/a96d9dc4e0c232af673a4161948b2b6c546fa552 "roadmap: language-aware analysis, the runtime's own tables first  Gap-closing item 10. A Go program keeps every function's name and start in its own function table even when stripped, and a Rust program's panic locations name its dependencies with their versions; the pipeline reads neither. Measured on stripped binaries here: two Go programs, 5 074 and 43 235 functions found and 3 named in each, where their own tables name 4 934 and 42 939; two Rust programs, none named, one of them naming 18 dependencies and 225 source files in its panic locations.  Recorded by cost, each with what makes it done: the Go function table, a Rust program's inventory, pointer-and-length strings, Go's register calling convention, the Rust standard library by signature, and output in the language's own terms (research-grade, not scheduled). Swift waits on Mach-O.") | 3 days agoOct 6, 2026 |
| [book.toml](https://github.com/Structio-labs/N0xis/blob/main/book.toml "book.toml") | [book.toml](https://github.com/Structio-labs/N0xis/blob/main/book.toml "book.toml") | [docs: describe targets by their shape, not as games, across the engin…](https://github.com/Structio-labs/N0xis/commit/6f177a53f3be75da14ad0830dd6bc8078761042b "docs: describe targets by their shape, not as games, across the engine's comments  Code comments, doc comments, manifests and prose outside the CLI and the HUD called targets games, titles and players, and cited the IL2CPP runtime's layouts by a commercial engine's name. They now say what the thing is: a process, an application, a launcher executable, the IL2CPP runtime's own headers, runtimes from 2018.1 on. Nothing else changed: no code, no test expectation, no number (the only new digits are the \"2\" of IL2CPP where it replaced a product name), and Bevy stays where it names the plugin-architecture model.  Left on purpose: identifiers the CLI uses (`gamegrep`), real file and module names code matches on (`GameAssembly.dll`), test fixture data, and real runtime strings.") | 5 days agoOct 5, 2026 |
| [check\_obsidian\_links.py](https://github.com/Structio-labs/N0xis/blob/main/check_obsidian_links.py "check_obsidian_links.py") | [check\_obsidian\_links.py](https://github.com/Structio-labs/N0xis/blob/main/check_obsidian_links.py "check_obsidian_links.py") | [N0xis — AI-first reverse-engineering toolkit](https://github.com/Structio-labs/N0xis/commit/3d0c5784dcfc8516159207b3796a5ec339f53c50 "N0xis — AI-first reverse-engineering toolkit  Static analysis, an SSA decompiler, live-process memory, and provenance, driven from a CLI and an MCP server that speak the same JSON.  This is a fresh public history. The project's development history is preserved privately; it is not part of this repository.") | last monthSep 11, 2026 |
| [lhm.plugin.json](https://github.com/Structio-labs/N0xis/blob/main/lhm.plugin.json "lhm.plugin.json") | [lhm.plugin.json](https://github.com/Structio-labs/N0xis/blob/main/lhm.plugin.json "lhm.plugin.json") | [docs: describe targets by their shape, not as games, across the engin…](https://github.com/Structio-labs/N0xis/commit/6f177a53f3be75da14ad0830dd6bc8078761042b "docs: describe targets by their shape, not as games, across the engine's comments  Code comments, doc comments, manifests and prose outside the CLI and the HUD called targets games, titles and players, and cited the IL2CPP runtime's layouts by a commercial engine's name. They now say what the thing is: a process, an application, a launcher executable, the IL2CPP runtime's own headers, runtimes from 2018.1 on. Nothing else changed: no code, no test expectation, no number (the only new digits are the \"2\" of IL2CPP where it replaced a product name), and Bevy stays where it names the plugin-architecture model.  Left on purpose: identifiers the CLI uses (`gamegrep`), real file and module names code matches on (`GameAssembly.dll`), test fixture data, and real runtime strings.") | 5 days agoOct 5, 2026 |
| [rust-toolchain.toml](https://github.com/Structio-labs/N0xis/blob/main/rust-toolchain.toml "rust-toolchain.toml") | [rust-toolchain.toml](https://github.com/Structio-labs/N0xis/blob/main/rust-toolchain.toml "rust-toolchain.toml") | [N0xis — AI-first reverse-engineering toolkit](https://github.com/Structio-labs/N0xis/commit/3d0c5784dcfc8516159207b3796a5ec339f53c50 "N0xis — AI-first reverse-engineering toolkit  Static analysis, an SSA decompiler, live-process memory, and provenance, driven from a CLI and an MCP server that speak the same JSON.  This is a fresh public history. The project's development history is preserved privately; it is not part of this repository.") | last monthSep 11, 2026 |
| View all files |

## Repository files navigation

# N0xis

[Permalink: N0xis](https://github.com/Structio-labs/N0xis#n0xis)

**From a hardware watchpoint in a live process to the decompiled statement that wrote the value.**

Memory scanners find the _address_. Decompilers explain the _code_. **N0xis takes you from one to the other in one scriptable loop.**

[![A live run: find a program's decrypted settings in its memory, watch them with a hardware watchpoint, and get the decompiled loop that wrote them](https://github.com/Structio-labs/N0xis/raw/main/docs/assets/live-loop.gif)](https://github.com/Structio-labs/N0xis/blob/main/docs/assets/live-loop.gif)[![A live run: find a program's decrypted settings in its memory, watch them with a hardware watchpoint, and get the decompiled loop that wrote them](https://github.com/Structio-labs/N0xis/raw/main/docs/assets/live-loop.gif)](https://github.com/Structio-labs/N0xis/blob/main/docs/assets/live-loop.gif)[Open A live run: find a program's decrypted settings in its memory, watch them with a hardware watchpoint, and get the decompiled loop that wrote them in new window](https://github.com/Structio-labs/N0xis/blob/main/docs/assets/live-loop.gif)

A real run of [`examples/config-demo`](https://github.com/Structio-labs/N0xis/blob/main/examples/config-demo): a program keeps its settings encrypted and decrypts them into memory; find the plaintext, arm a hardware watchpoint on it, and get the decompiled code that wrote it. Rerun it yourself with `demo.sh`.

```
$ n0x provenance trace --pid 181529 --addr 0x564e32cb7060 --kind write
```

```
"instruction_va": "0x564e32cb4266",   // the byte store that wrote the watched address
"function_va": "0x564e32cb4230",      // the function it sits in, auto-resolved
"decompiled_context": [\
  "rcx.3 = (uint32_t)((uint32_t)(uint32_t)*(uint8_t*)((rsi.1 + v2)) ^ (uint32_t)v1);",\
  "*(uint8_t*)((rdi.1 + v2)) = (uint8_t)rcx.3;",   // ← the write\
  "rcx.4 = (uint32_t)(v1 + (v1 * 0x2));",\
  "v2 = (v2 + 0x1);",\
  "v1 = (uint32_t)((v1 + (rcx.4 * 0x4)) + 0x7);"\
]
```

In the source this is the loop `config[i] = sealed[i] ^ key; key = key * 13 + 7;`: the
decompiled key update, `v1 + (v1 * 2) * 4 + 7`, is the same `key * 13 + 7`. The answer gives
addresses, not the names `config` and `decrypt_config`: names of globals and functions from the
binary's symbols are not carried into it yet. The run above is on Linux; the live loop runs on
Windows too.

The watchpoint hit is resolved through the same SSA pipeline that decompiles the file, so
the answer is the statement that wrote the value and the function it sits in, as JSON a
script can act on. It is meant to sit next to the disassembler and decompiler you already
use, not to replace them.

## Install

[Permalink: Install](https://github.com/Structio-labs/N0xis#install)

Prebuilt binaries for Linux and Windows — **[latest release](https://github.com/Structio-labs/N0xis/releases/latest)**.

```
curl -LO https://github.com/Structio-labs/N0xis/releases/latest/download/n0xis-linux-x86_64
chmod +x n0xis-linux-x86_64 && ./n0xis-linux-x86_64 --version
```

Or build it: `cargo build --workspace --release` (Windows and Linux; no MSVC Build Tools
needed — `rust-toolchain.toml` pins the gnu host).

## Quickstart

[Permalink: Quickstart](https://github.com/Structio-labs/N0xis#quickstart)

Every command prints **one** JSON object — argument errors included: `{"ok":true,"data":…,"meta":…}` or
`{"ok":false,"error":…}`. Add `--pretty` to read it; the exit code is non-zero on failure.

```
n0x doctor                                                    # environment check
n0x profile --file app.exe                                    # triage: sections, exports, runtime hints
n0x function discover --file app.exe --pdata                 # exact .pdata discovery
n0x decomp pseudo --file app.exe --addr 0x140012a00 --style ssa --pretty
n0x provenance trace --pid 4821 --addr 0x1a2b3c40 --kind write --pretty
```

The same commands run on a live `--pid`, a static `--file`, a captured `--snapshot`, or a
remote process over SSH. It is ordinary Unix plumbing —
`n0x function discover --file app.exe --pdata | jq -r '.data.functions[].va'` feeds the next
command. `n0x guide` lists all 117 commands, generated from the binary so it never drifts — and a test
fails the build if this number does.

**From an agent:** point any MCP client at `n0xis-mcp` — 25 tools returning the identical
`{ok,data,meta}` envelope, JSON-RPC over stdio.

```
{ "mcpServers": { "n0xis": { "command": "/path/to/n0xis-mcp" } } }
```

## What it does

[Permalink: What it does](https://github.com/Structio-labs/N0xis#what-it-does)

- **Decompile** — an optimizing SSA decompiler (Memory-SSA, phi-web variable coalescing,
complete SSA destruction, exact branch conditions) whose **optimizer reports every rewrite it**
**made** (`--explain`: which sub-pass changed what, at which address), not a black-box answer.
- **Scan live memory** — value/pointer/AOB scanning with snapshot-backed narrowing, freeze,
code-cave hooks: the full scan → narrow → freeze → patch loop.
- **Watch & explain** — software / hardware / conditional breakpoints and a real cross-process
unwound call stack; the raw material provenance is built on.
- **Recover names** — C++ classes from RTTI on both ABIs (MSVC `.rdata` chains and Itanium
`_ZTV` symbols), .NET NativeAOT `RVA ↔ Namespace.Type.Method`, and a few runtime formats
(LuaJIT bytecode, Bitsquid, IL2CPP), so a stripped image reads as source, not `sub_XXXX`.
- **Persist & diff** — `.n0xt` tables, versioned annotations, content-addressed caching,
function/version diffing.

Windows **and** Linux, PE **and** ELF, one pipeline — static files, live processes, snapshots
and remote targets all flow through the same passes and the same versioned JSON.

There is no ML nondeterminism in the core, ever. A desktop GUI lives in a separate repo:
**[n0xis-gui](https://github.com/Structio-labs/n0xis-gui)**.

## Status

[Permalink: Status](https://github.com/Structio-labs/N0xis#status)

**Alpha.** Every claim below is a measurement against a source outside the tool — the kernel,
the image's own tables, or the target process itself. Where there is no such source, it says so,
because _implemented_ and _verified_ are not the same claim.

**Live memory**, against a disposable target that plants known values:

- **Linux — 29 of 31 commands measured against `/proc/<pid>/mem`, one wrong and fixed.** The
other two are Windows-only and refuse saying so. The one wrong was `scan dissect`, which
chose a field's width before its alignment and so read a struct four bytes out of phase from
its first mistake on: one field of six right against a layout known from its own source, five
of six after.
- **Windows 11 — 21 of 23 checks measured, 0 wrong**, with the target itself as the oracle.
`ui focus` correctly finds no window on a console target; `stack backtrace` is
**Linux-only** — the one place the Linux adapter is ahead.

**The decoder**, against an independent disassembler — the floor everything else stands on,
and until now checked only by the passes built on top of it, which all read the same stream:

- x86: instruction **boundaries** compared with `objdump`. Three purpose-built shapes exact,
**20 000 instructions of a shared library and 20 000 of a 32-bit system DLL, zero**
**disagreements** and zero boundaries either side had alone. Widened to **60 000 instructions**
**of a 334 MB stripped browser binary: 2 disagreements, both inside an ASCII string embedded**
**in `.text`** where the reference itself decodes `(bad)` — not code, and neither reading is
the right one.
- AArch64: **mnemonics** compared with `llvm-objdump` (fixed-width encodings make boundaries
vacuous). See the ARM64 line below.
- AArch64, **the encoding space rather than compiler output**: 600 deterministic words judged
by `llvm-mc --mattr=+all` and by n0xis. 241 both call an instruction, 304 both reject —
and **48 (8.0%) are reserved encodings n0xis reads as instructions**, with 7 (1.2%) real
instructions it rejects (mostly LSE atomics). Three of the 48 were decoded by hand and are
genuinely UNALLOCATED. That gap is **held by a bound that fails if it grows**, and stated
here rather than left out: a reserved word read as an instruction turns data into a
plausible program.

**Function extents**, against the image's own unwind table and the linker's export list:

- every FDE's `start..end` from `objdump --dwarf=frames` equal to the recovered extent —
**3 787 compared on this machine (10 + libc's 3 777), start and end, exact**; separately
measured at 15 467 and 14 355 on two large libraries.
- **0 exported entry points missed** by the function list: 10 of 10 on the oracle shape and
**2 323 of 2 323 inside libc's scanned window**.

**Cross-references and the call graph**, against the disassembly of a source that is not this
tool:

- **4 733 references across the six busiest targets of a system C library — none missed and**
**none invented**, in both directions. `call`, tail-call `jmp` and RIP-relative data
references are each labelled by `kind`, and each was compared against what `objdump` shows.
- **304 call sites across 100 functions — none missed and none invented**, with each
function's extent taken from the unwind table rather than from a symbol boundary, and a
tail call (including a _conditional_ one) counted as the call it is.
- **464 branch targets across 100 functions, every one of them the start of a basic block.**
A target the splitter misses leaves two blocks fused, so an edge that exists in the program
does not exist in the graph — and nothing above it can notice.

**Recovered struct fields**, against the compiler that laid the struct out:

- `gcc -g` states every member's offset; **15 recovered field offsets across 10 functions,**
**every one a real member — none invented.** One-directional on purpose: an optimizer folds
and drops field accesses, so a member that never appears is the compiler's doing, not a miss.

**Static analysis**, against the extents and tables the image declares:

- x64 ELF and PE: function extents exact, 0 CFG-invariant violations over 92 001 edges.
- **ARM64 — decoder and CFG verified, decompiler not.** 2 381 of 2 381 function extents exactly
equal to the symbol table, 0 violations across 46 757 CFG edges. The decoder is now checked
against **LLVM's own AArch64 disassembler** over compiler output built for the purpose
(`oracle/arm64.c` at `-O2`): **147 instructions, 147 shared addresses, 0 failures to decode,**
**and every one of the 28 name differences a documented architecture alias** (`mov`/`orr`,
`cmp`/`subs`, `b.hs`/`b.cs`, …), each listed in the test rather than forgiven in bulk. The
AArch64 lift/SSA is still not built, so `decomp pseudo` reports `quality: 0.0` and falls back
to `asm` nodes. The optimizing decompiler is **x64-only**.
- 32-bit PE: 422 of 422 exported entry points discovered, 0 violations over 34 149 edges.
On a 32-bit image with **no exception table at all**, checked against the 3 889 `.eh_frame`
FDEs an independent parser reads out of it: **0 missed, every extent exact, 0 entries interior**
**to a known function.** The rule was written against x64 exception tables and holds on an
architecture that has none.

**Recovered signatures**, against targets compiled here whose answer is known before the
question is asked (`oracle/`):

- **12 of 12 on both x86-64 ABIs** — parameter count, which register file each parameter
arrives in, and return class, including both orders of a mixed integer/floating signature
(System V and Win64 count their two argument register files by different rules).
- 32-bit `cdecl` states no arity on the way out and passes nothing in a register, so the
parameter list reads `()` — C for _unspecified_ — and not `(void)`, which would be a claim
that there are none. The x87 return this lift does not model reads `/*unknown*/`, not `void`.
Both gaps are recorded in `oracle/expect.json` with their reason, and the test **fails if one**
**quietly closes**, so a recorded limitation cannot rot into folklore.

**Recovered C++ classes**, against the image's own type-descriptor strings:

- **93 vtables on a 32-bit C++ runtime (0 before), 97 and 152 on two 64-bit ones, 269 on an**
**ELF through the Itanium path — and every recovered name present in the image's own**
**strings**, so none is invented. Both MSVC dialects have planted regression fixtures
(`oracle/rtti32.c`, `oracle/rtti64.S`), because no compiler here emits MSVC RTTI.

**Not verified, and not claimed:**`il2cpp import` / `symbols` need an external dumper's index;
`il2cpp obj` / `classes` need a live managed process. The versioned JSON contract has not been
road-tested by outside users — expect shapes to move.

## Docs

[Permalink: Docs](https://github.com/Structio-labs/N0xis#docs)

- **[docs/CLI\_COMMANDS.md](https://github.com/Structio-labs/N0xis/blob/main/docs/CLI_COMMANDS.md)** — every command (the inventory is generated
from the binary), the schema id each emits, and the caveats behind each claim. Arguments live
in `n0x guide` and `--help`, which are generated too.
- **[oracle/README.md](https://github.com/Structio-labs/N0xis/blob/main/oracle/README.md)** — the corpus of targets whose answer is known
before the question is asked, how the ranking of sources works, and how to add a shape.
- **[docs/VERIFICATION.md](https://github.com/Structio-labs/N0xis/blob/main/docs/VERIFICATION.md)** — the verification ledger: every check with
its source rung and case count, and what is proven, open, or not claimed — all in one place.
- **[CONCEPT.md](https://github.com/Structio-labs/N0xis/blob/main/CONCEPT.md)** — architecture: adapters, passes, seams.
- **[ROADMAP.md](https://github.com/Structio-labs/N0xis/blob/main/ROADMAP.md)** — build history and the analysis capabilities still missing.
- **[MAP.md](https://github.com/Structio-labs/N0xis/blob/main/MAP.md)** — the 15-crate workspace layout.
- **[docs/COMMUNITY\_ROADMAP.md](https://github.com/Structio-labs/N0xis/blob/main/docs/COMMUNITY_ROADMAP.md)** ·
**[docs/PRODUCT\_POLICY.md](https://github.com/Structio-labs/N0xis/blob/main/docs/PRODUCT_POLICY.md)** · **[CONTRIBUTING.md](https://github.com/Structio-labs/N0xis/blob/main/CONTRIBUTING.md)**

## License

[Permalink: License](https://github.com/Structio-labs/N0xis#license)

N0xis is **source-available** software, developed under the Structio name.

- **Free for noncommercial use** — personal projects, research, education, CTFs, hobby reverse
engineering, and use by noncommercial organizations, under the
[PolyForm Noncommercial License 1.0.0](https://github.com/Structio-labs/N0xis/blob/main/LICENSE).
- **Commercial use requires a paid license** — see [COMMERCIAL.md](https://github.com/Structio-labs/N0xis/blob/main/COMMERCIAL.md).

Versions up to and including 0.2.1 were released under AGPL-3.0 and remain available under
those terms. This license applies to 0.3.0 and later.

Not sure whether your use case is commercial? Open an issue or email [structio.dev@gmail.com](mailto:structio.dev@gmail.com) —
I'd rather answer a question than chase a violation.

## About

AI-first reverse-engineering toolkit: static analysis, SSA decompiler, live memory, provenance. Source-available (PolyForm Noncommercial).

### Topics

[binary-analysis](https://github.com/topics/binary-analysis) [cli](https://github.com/topics/cli) [decompilation](https://github.com/topics/decompilation) [decompiler](https://github.com/topics/decompiler) [disassembler](https://github.com/topics/disassembler) [elf](https://github.com/topics/elf) [mcp](https://github.com/topics/mcp) [pe](https://github.com/topics/pe) [reverse-engineering](https://github.com/topics/reverse-engineering) [rust](https://github.com/topics/rust) [ssa](https://github.com/topics/ssa) [static-analysis](https://github.com/topics/static-analysis)

### Resources

[Readme](https://github.com/Structio-labs/N0xis#readme-ov-file)

[License](https://github.com/Structio-labs/N0xis#License-1-ov-file)

### Contributing

[Contributing](https://github.com/Structio-labs/N0xis#contributing-ov-file)

[Activity](https://github.com/Structio-labs/N0xis/activity)

[Custom properties](https://github.com/Structio-labs/N0xis/custom-properties)

### Stars

**0** stars

### Watchers

**0** watching

### Forks

[**0** forks](https://github.com/Structio-labs/N0xis/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FStructio-labs%2FN0xis&report=Structio-labs+%28user%29)

## [Releases](https://github.com/Structio-labs/N0xis/releases) 2 (2)

[N0xis 0.3.4Latest\\
\\
3 days agoOct 6, 2026](https://github.com/Structio-labs/N0xis/releases/tag/v0.3.4)

[\+ 1 release](https://github.com/Structio-labs/N0xis/releases)

## [Contributors](https://github.com/Structio-labs/N0xis/graphs/contributors) 1 (1)

- [![@reLargo](https://avatars.githubusercontent.com/u/324685348?s=64&v=4)](https://github.com/reLargo) [**reLargo** Timothy Kosovskyi](https://github.com/reLargo)

## Languages

- [Rust97.2%](https://github.com/Structio-labs/N0xis/search?l=rust)
- [C1.5%](https://github.com/Structio-labs/N0xis/search?l=c)
- [Other1.3%](https://github.com/Structio-labs/N0xis/search?l=Other)

You can’t perform that action at this time.