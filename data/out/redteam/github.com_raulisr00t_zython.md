# https://github.com/Raulisr00t/Zython

[Skip to content](https://github.com/Raulisr00t/Zython#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Raulisr00t/Zython) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Raulisr00t/Zython) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Raulisr00t/Zython) to refresh your session.Dismiss alert

{{ message }}

main

[**1** Branch](https://github.com/Raulisr00t/Zython/branches) [**0** Tags](https://github.com/Raulisr00t/Zython/tags)

[Go to Branches page](https://github.com/Raulisr00t/Zython/branches)[Go to Tags page](https://github.com/Raulisr00t/Zython/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![Raulisr00t](https://avatars.githubusercontent.com/u/168528192?v=4&size=40)](https://github.com/Raulisr00t)[Raulisr00t](https://github.com/Raulisr00t/Zython/commits?author=Raulisr00t)

[Update lexer.zig](https://github.com/Raulisr00t/Zython/commit/9bdd32f92b9ed1c8af3eeb26a99fbac42bcb9a16)

3 months agoAug 1, 2026

[9bdd32f](https://github.com/Raulisr00t/Zython/commit/9bdd32f92b9ed1c8af3eeb26a99fbac42bcb9a16) · 3 months agoAug 1, 2026

## History

[33 Commits](https://github.com/Raulisr00t/Zython/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/Raulisr00t/Zython/commits/main/) 33 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [src](https://github.com/Raulisr00t/Zython/tree/main/src "src") | [src](https://github.com/Raulisr00t/Zython/tree/main/src "src") | [Update lexer.zig](https://github.com/Raulisr00t/Zython/commit/9bdd32f92b9ed1c8af3eeb26a99fbac42bcb9a16 "Update lexer.zig") | 3 months agoAug 1, 2026 |
| [README.md](https://github.com/Raulisr00t/Zython/blob/main/README.md "README.md") | [README.md](https://github.com/Raulisr00t/Zython/blob/main/README.md "README.md") | [Update README.md](https://github.com/Raulisr00t/Zython/commit/6b4538077dced5c9413c36458a388c174d14437b "Update README.md") | 3 months agoJul 30, 2026 |
| [build.zig](https://github.com/Raulisr00t/Zython/blob/main/build.zig "build.zig") | [build.zig](https://github.com/Raulisr00t/Zython/blob/main/build.zig "build.zig") | [Add files via upload](https://github.com/Raulisr00t/Zython/commit/fefa5ba4e91ffa5c9c3503d781c6d16d4a99fa28 "Add files via upload") | 3 months agoJul 31, 2026 |
| [fib.py](https://github.com/Raulisr00t/Zython/blob/main/fib.py "fib.py") | [fib.py](https://github.com/Raulisr00t/Zython/blob/main/fib.py "fib.py") | [Add files via upload](https://github.com/Raulisr00t/Zython/commit/7ccaf59d926cab39b0e266834280f791b453efb0 "Add files via upload") | 3 months agoJul 30, 2026 |
| [hello.py](https://github.com/Raulisr00t/Zython/blob/main/hello.py "hello.py") | [hello.py](https://github.com/Raulisr00t/Zython/blob/main/hello.py "hello.py") | [Update hello.py](https://github.com/Raulisr00t/Zython/commit/4261a06a80299d2ba2d61aee745bb148637acd9c "Update hello.py") | 3 months agoJul 30, 2026 |
| View all files |

## Repository files navigation

# Zython

[Permalink: Zython](https://github.com/Raulisr00t/Zython#zython)

A Python 3 subset — tokenizer, parser, bytecode compiler, and virtual machine — written from
scratch in Zig, with real multithreaded execution.

## Highlights

[Permalink: Highlights](https://github.com/Raulisr00t/Zython#highlights)

- **Full pipeline**: source text → tokens → AST → bytecode → VM, with `--dump-tokens` /
`--dump-ast` / `--dump-bytecode` flags to inspect every stage.
- **True parallelism, no GIL.**`spawn()`-ed workers run as real OS threads, each with its own
isolated heap — no shared mutable object graph, so there's no per-object locking anywhere.
`send()`/`recv()`/`join()` move data between workers by message passing. The same CPU-bound
workload takes ~3.7s run sequentially and ~2.0s split across two workers — measured, not
assumed.
- **`--verbose` live execution tracing**: every instruction prints as it executes — worker id,
program counter, opcode, operand, live stack contents — flushed per instruction, so you can
watch the VM work in real time, including two workers' traces genuinely interleaving.
- **A real language subset**: variables, arithmetic/comparison/boolean expressions, `if`/`elif`/
`else`, `while`/`for`, functions with recursion, and lists with indexing.

## Quick start

[Permalink: Quick start](https://github.com/Raulisr00t/Zython#quick-start)

```
zig.exe build --build-file build.zig
zython.exe fib.zpy
zython.exe --verbose small.zpy
zig.exe build test --build-file build.zig
```

## About

Zig based Python Interpreter

### Resources

[Readme](https://github.com/Raulisr00t/Zython#readme-ov-file)

[Activity](https://github.com/Raulisr00t/Zython/activity)

### Stars

**5** stars

### Watchers

**0** watching

### Forks

[**0** forks](https://github.com/Raulisr00t/Zython/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FRaulisr00t%2FZython&report=Raulisr00t+%28user%29)

## [Releases](https://github.com/Raulisr00t/Zython/releases)

No releases published

## [Contributors](https://github.com/Raulisr00t/Zython/graphs/contributors) 1 (1)

- [![@Raulisr00t](https://avatars.githubusercontent.com/u/168528192?s=64&v=4)](https://github.com/Raulisr00t) [**Raulisr00t** Raul](https://github.com/Raulisr00t)

## Languages

- [Zig99.9%](https://github.com/Raulisr00t/Zython/search?l=zig)
- [Python0.1%](https://github.com/Raulisr00t/Zython/search?l=python)

You can’t perform that action at this time.