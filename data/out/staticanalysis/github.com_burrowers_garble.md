# https://github.com/burrowers/garble

[Skip to content](https://github.com/burrowers/garble#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/burrowers/garble) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/burrowers/garble) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/burrowers/garble) to refresh your session.Dismiss alert

{{ message }}

[burrowers](https://github.com/burrowers)/ **[garble](https://github.com/burrowers/garble)** Public

- Sponsor







# Sponsor burrowers/garble























##### GitHub Sponsors

[Learn more about Sponsors](https://github.com/sponsors)









[![@mvdan](https://avatars.githubusercontent.com/u/3576549?s=80&v=4)](https://github.com/mvdan)



[mvdan](https://github.com/mvdan)



[mvdan](https://github.com/mvdan)







[Sponsor](https://github.com/sponsors/mvdan)











[![@pagran](https://avatars.githubusercontent.com/u/67878280?s=80&v=4)](https://github.com/pagran)



[pagran](https://github.com/pagran)



[pagran](https://github.com/pagran)







[Sponsor](https://github.com/sponsors/pagran)















[Learn more about funding links in repositories](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository).




[Report abuse](https://github.com/contact/report-abuse?report=burrowers%2Fgarble+%28Repository+Funding+Links%29)

- [Notifications](https://github.com/login?return_to=%2Fburrowers%2Fgarble) You must be signed in to change notification settings
- [Fork\\
340](https://github.com/login?return_to=%2Fburrowers%2Fgarble)
- [Star\\
5.3k](https://github.com/login?return_to=%2Fburrowers%2Fgarble)


Obfuscate Go builds


### License

[BSD-3-Clause license](https://github.com/burrowers/garble/blob/master/LICENSE)

[5.3k\\
stars](https://github.com/burrowers/garble/stargazers) [340\\
forks](https://github.com/burrowers/garble/forks) [Branches](https://github.com/burrowers/garble/branches) [Tags](https://github.com/burrowers/garble/tags) [Activity](https://github.com/burrowers/garble/activity)

[Star](https://github.com/login?return_to=%2Fburrowers%2Fgarble)

[Notifications](https://github.com/login?return_to=%2Fburrowers%2Fgarble) You must be signed in to change notification settings

# burrowers/garble

master

[**8** Branches](https://github.com/burrowers/garble/branches) [**25** Tags](https://github.com/burrowers/garble/tags)

[Go to Branches page](https://github.com/burrowers/garble/branches)[Go to Tags page](https://github.com/burrowers/garble/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>![mvdan](https://avatars.githubusercontent.com/u/3576549?v=4&size=40)![luantak](https://avatars.githubusercontent.com/u/46541492?v=4&size=40)<br>[mvdan](https://github.com/burrowers/garble/commits?author=mvdan)<br>and<br>[luantak](https://github.com/burrowers/garble/commits?author=luantak)<br>[README: note that `-literals` can be reversed](https://github.com/burrowers/garble/commit/0e3374174b1fd9fe8662f5a2a91840db5be6733d)<br>success<br>2 months agoDec 23, 2025<br>[0e33741](https://github.com/burrowers/garble/commit/0e3374174b1fd9fe8662f5a2a91840db5be6733d) · 2 months agoDec 23, 2025<br>## History<br>[770 Commits](https://github.com/burrowers/garble/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/burrowers/garble/commits/master/) 770 Commits |
| [.github](https://github.com/burrowers/garble/tree/master/.github ".github") | [.github](https://github.com/burrowers/garble/tree/master/.github ".github") | [add support for Go 1.25 and drop support for 1.24](https://github.com/burrowers/garble/commit/aed2fd265907f9df99d39f18c97ffe508e8bb985 "add support for Go 1.25 and drop support for 1.24  While strictly speaking it would be okay to leave Go 1.24 support in place for the time being, we are behind on a few tasks at the moment so it's best to keep the setup at master simpler for the next release. Go 1.25 already came out two weeks ago, and it seems to have been a fairly smooth release, so I don't suspect any end users will have trouble upgrading to it.  Note that two changes were necessary for garble to work on Go 1.25.0.  First, we stop deduplicating runtimeAndLinknamed with runtimeAndDeps. Otherwise, for GOOS=windows, internal/runtime/cgroup would be missing as it is a //go:linkname target from runtime on all platforms, but it is not transitively imported from runtime on GOOS=windows.  Second, the testing/synctest package is now part of std, and it is a //go:linkname target from the testing package but not a transitive import from it. Teach appendListedPackages that, when loading all packages for a `go test` run, it should load the new testing/synctest package too.  Fixes #968.") | 6 months agoAug 30, 2025 |
| [docs](https://github.com/burrowers/garble/tree/master/docs "docs") | [docs](https://github.com/burrowers/garble/tree/master/docs "docs") | [add trash block generator docs](https://github.com/burrowers/garble/commit/d76bc2eb47cd74a7f089ab92ba23435a1d69e021 "add trash block generator docs") | 2 years agoFeb 11, 2024 |
| [internal](https://github.com/burrowers/garble/tree/master/internal "internal") | [internal](https://github.com/burrowers/garble/tree/master/internal "internal") | [internal/literals: modernize -fix](https://github.com/burrowers/garble/commit/cb4cb3cfca3f913374839cccbe08af14312719dd "internal/literals: modernize -fix") | 6 months agoAug 31, 2025 |
| [scripts](https://github.com/burrowers/garble/tree/master/scripts "scripts") | [scripts](https://github.com/burrowers/garble/tree/master/scripts "scripts") | [support testing/synctest when a non-test package imports "testing" too](https://github.com/burrowers/garble/commit/36fcc61c4e5d0c1b5f0bd0c0240cf07954a8dc1a "support testing/synctest when a non-test package imports \"testing\" too  As spotted by scripts/check-third-party.sh, it's possible to import the testing package without using `go test`, so our previous solution to only load testing/synctest when running `go test` was not enough.  Add a regression test via stdimporter in gogarble.txtar.") | 6 months agoAug 30, 2025 |
| [testdata](https://github.com/burrowers/garble/tree/master/testdata "testdata") | [testdata](https://github.com/burrowers/garble/tree/master/testdata "testdata") | [stop ignoring GODEBUG when -tiny is used](https://github.com/burrowers/garble/commit/65ffaa0efb591c12a659ad4974b2b7fca20c0154 "stop ignoring GODEBUG when -tiny is used  GODEBUG started being used for configuring the behavior of the Go toolchain and standard library, for the sake of smoother transitions in terms of backwards and forwards compatibility. See: https://go.dev/doc/godebug  As such, it is not right to have `garble build -tiny` ignore all GODEBUG settings, because many GODEBUG keys nowadays do not actually involve debugging what a Go binary is doing.  Moreover, the mechanism we were using broke with Go 1.25.2, which refactored `func parsedebugvars()` into `func parseRuntimeDebugVars(godebug string)`, so our test started breaking as our runtime patching was broken.") | 4 months agoOct 18, 2025 |
| [.gitattributes](https://github.com/burrowers/garble/blob/master/.gitattributes ".gitattributes") | [.gitattributes](https://github.com/burrowers/garble/blob/master/.gitattributes ".gitattributes") | [start testing on GitHub Actions](https://github.com/burrowers/garble/commit/ab560ff007cc857e9f5f012409be5c92d9faf3c0 "start testing on GitHub Actions  No windows yet, because a few portability issues remain.") | 7 years agoDec 9, 2019 |
| [.gitignore](https://github.com/burrowers/garble/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/burrowers/garble/blob/master/.gitignore ".gitignore") | [obfuscate all names used in reflection](https://github.com/burrowers/garble/commit/926f3de60d4353f207104e497a5298bb24ff7c90 "obfuscate all names used in reflection  Go code can retrieve and use field and method names via the `reflect` package. For that reason, historically we did not obfuscate names of fields and methods underneath types that we detected as used for reflection, via e.g. `reflect.TypeOf`.  However, that caused a number of issues. Since we obfuscate and build one package at a time, we could only detect when types were used for reflection in their own package or in upstream packages. Use of reflection in downstream packages would be detected too late, causing one package to obfuscate the names and the other not to, leading to a build failure.  A different approach is implemented here. All names are obfuscated now, but we collect those types used for reflection, and at the end of a build in `package main`, we inject a function into the runtime's `internal/abi` package to reverse the obfuscation for those names which can be used for reflection.  This does mean that the obfuscation for these names is very weak, as the binary contains a one-to-one mapping to their original names, but they cannot be obfuscated without breaking too many Go packages out in the wild. There is also some amount of overhead in `internal/abi` due to this, but we aim to make the overhead insignificant.  Fixes #884, #799, #817, #881, #858, #843, #842  Closes #406") | 2 years agoNov 27, 2024 |
| [AUTHORS](https://github.com/burrowers/garble/blob/master/AUTHORS "AUTHORS") | [AUTHORS](https://github.com/burrowers/garble/blob/master/AUTHORS "AUTHORS") | [obfuscate all names used in reflection](https://github.com/burrowers/garble/commit/926f3de60d4353f207104e497a5298bb24ff7c90 "obfuscate all names used in reflection  Go code can retrieve and use field and method names via the `reflect` package. For that reason, historically we did not obfuscate names of fields and methods underneath types that we detected as used for reflection, via e.g. `reflect.TypeOf`.  However, that caused a number of issues. Since we obfuscate and build one package at a time, we could only detect when types were used for reflection in their own package or in upstream packages. Use of reflection in downstream packages would be detected too late, causing one package to obfuscate the names and the other not to, leading to a build failure.  A different approach is implemented here. All names are obfuscated now, but we collect those types used for reflection, and at the end of a build in `package main`, we inject a function into the runtime's `internal/abi` package to reverse the obfuscation for those names which can be used for reflection.  This does mean that the obfuscation for these names is very weak, as the binary contains a one-to-one mapping to their original names, but they cannot be obfuscated without breaking too many Go packages out in the wild. There is also some amount of overhead in `internal/abi` due to this, but we aim to make the overhead insignificant.  Fixes #884, #799, #817, #881, #858, #843, #842  Closes #406") | 2 years agoNov 27, 2024 |
| [CHANGELOG.md](https://github.com/burrowers/garble/blob/master/CHANGELOG.md "CHANGELOG.md") | [CHANGELOG.md](https://github.com/burrowers/garble/blob/master/CHANGELOG.md "CHANGELOG.md") | [CHANGELOG: add entry for v0.15.0](https://github.com/burrowers/garble/commit/6dab979d1cae7c703aeff286f1c70319c34a6c35 "CHANGELOG: add entry for v0.15.0") | 6 months agoAug 31, 2025 |
| [CONTRIBUTING.md](https://github.com/burrowers/garble/blob/master/CONTRIBUTING.md "CONTRIBUTING.md") | [CONTRIBUTING.md](https://github.com/burrowers/garble/blob/master/CONTRIBUTING.md "CONTRIBUTING.md") | [format testscript files with gofmt](https://github.com/burrowers/garble/commit/87ebebb520af0cc1fbb0978025a416aa8c5a2300 "format testscript files with gofmt") | 8 months agoJun 15, 2025 |
| [LICENSE](https://github.com/burrowers/garble/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/burrowers/garble/blob/master/LICENSE "LICENSE") | [set up an AUTHORS file to attribute copyright](https://github.com/burrowers/garble/commit/805c895d594b1f9ec4ef4eaa79e76d2436063886 "set up an AUTHORS file to attribute copyright  Many files were missing copyright, so also add a short script to add the missing lines with the current year, and run it.  The AUTHORS file is also self-explanatory. Contributors can add themselves there, or we can simply update it from time to time via git-shortlog.  Since we have two scripts now, set up a directory for them.") | 6 years agoSep 6, 2020 |
| [README.md](https://github.com/burrowers/garble/blob/master/README.md "README.md") | [README.md](https://github.com/burrowers/garble/blob/master/README.md "README.md") | [README: note that `-literals` can be reversed](https://github.com/burrowers/garble/commit/0e3374174b1fd9fe8662f5a2a91840db5be6733d "README: note that `-literals` can be reversed") | 2 months agoDec 23, 2025 |
| [bench\_test.go](https://github.com/burrowers/garble/blob/master/bench_test.go "bench_test.go") | [bench\_test.go](https://github.com/burrowers/garble/blob/master/bench_test.go "bench_test.go") | [apply minor cleanups suggested by tools](https://github.com/burrowers/garble/commit/97ae350b0e53415ab9c572e1719aa8a459767373 "apply minor cleanups suggested by tools  GARBLE_PARENT_WORK hasn't been used for a while. A couple of other minor simplifications.") | last yearJan 17, 2025 |
| [bundled\_typeparams.go](https://github.com/burrowers/garble/blob/master/bundled_typeparams.go "bundled_typeparams.go") | [bundled\_typeparams.go](https://github.com/burrowers/garble/blob/master/bundled_typeparams.go "bundled_typeparams.go") | [all: run gopls's modernize -fix](https://github.com/burrowers/garble/commit/cb83c50b13a30f83e3a2348f3cb151e3b20ea2e3 "all: run gopls's modernize -fix  Except on reflect_abi_code.go, as that needs to be compatible with older versions of Go given that we inject its code.") | last yearFeb 22, 2025 |
| [bundled\_typeutil.go](https://github.com/burrowers/garble/blob/master/bundled_typeutil.go "bundled_typeutil.go") | [bundled\_typeutil.go](https://github.com/burrowers/garble/blob/master/bundled_typeutil.go "bundled_typeutil.go") | [all: run gopls's modernize -fix](https://github.com/burrowers/garble/commit/cb83c50b13a30f83e3a2348f3cb151e3b20ea2e3 "all: run gopls's modernize -fix  Except on reflect_abi_code.go, as that needs to be compatible with older versions of Go given that we inject its code.") | last yearFeb 22, 2025 |
| [cache\_pkg.go](https://github.com/burrowers/garble/blob/master/cache_pkg.go "cache_pkg.go") | [cache\_pkg.go](https://github.com/burrowers/garble/blob/master/cache_pkg.go "cache_pkg.go") | [refactor main into pieces](https://github.com/burrowers/garble/commit/28f7a7ffbfbe07c8b3898a891f93fed4b22e5508 "refactor main into pieces  * reflect_abi_patch.go was added into reflect.go * shared.go was renamed into cache_shared.go and package caching was moved to cache_pkg.go * transformer methods in main.go are moved to transformer.go") | 5 months agoSep 8, 2025 |
| [cache\_shared.go](https://github.com/burrowers/garble/blob/master/cache_shared.go "cache_shared.go") | [cache\_shared.go](https://github.com/burrowers/garble/blob/master/cache_shared.go "cache_shared.go") | [parse `go env GOVERSION` with go/version directly](https://github.com/burrowers/garble/commit/9d7c84b0c6b03223b4a44680b5f5f254cf8c6cfd "parse `go env GOVERSION` with go/version directly  We don't need to use a regular expression to find \"goN.M\" anymore, as go/version seems to deal with \"devel\" versions from master just fine. We can then also stop having two separate fields for the version of the Go toolchain currently being used.") | 4 months agoOct 18, 2025 |
| [cmdgo\_quoted.go](https://github.com/burrowers/garble/blob/master/cmdgo_quoted.go "cmdgo_quoted.go") | [cmdgo\_quoted.go](https://github.com/burrowers/garble/blob/master/cmdgo_quoted.go "cmdgo_quoted.go") | [update x/tools version used in go:generate](https://github.com/burrowers/garble/commit/598d5182fbbc0bd65b3b742e4ab424786fb732f1 "update x/tools version used in go:generate  Fixes running this go:generate line with Go tip.") | 3 years agoJan 24, 2023 |
| [go.mod](https://github.com/burrowers/garble/blob/master/go.mod "go.mod") | [go.mod](https://github.com/burrowers/garble/blob/master/go.mod "go.mod") | [update golang.org/x dependencies](https://github.com/burrowers/garble/commit/176426755cf46ec7f98f59d7e3a2c7575697084e "update golang.org/x dependencies") | 6 months agoAug 30, 2025 |
| [go.sum](https://github.com/burrowers/garble/blob/master/go.sum "go.sum") | [go.sum](https://github.com/burrowers/garble/blob/master/go.sum "go.sum") | [update golang.org/x dependencies](https://github.com/burrowers/garble/commit/176426755cf46ec7f98f59d7e3a2c7575697084e "update golang.org/x dependencies") | 6 months agoAug 30, 2025 |
| [go\_std\_tables.go](https://github.com/burrowers/garble/blob/master/go_std_tables.go "go_std_tables.go") | [go\_std\_tables.go](https://github.com/burrowers/garble/blob/master/go_std_tables.go "go_std_tables.go") | [support testing/synctest when a non-test package imports "testing" too](https://github.com/burrowers/garble/commit/36fcc61c4e5d0c1b5f0bd0c0240cf07954a8dc1a "support testing/synctest when a non-test package imports \"testing\" too  As spotted by scripts/check-third-party.sh, it's possible to import the testing package without using `go test`, so our previous solution to only load testing/synctest when running `go test` was not enough.  Add a regression test via stdimporter in gogarble.txtar.") | 6 months agoAug 30, 2025 |
| [hash.go](https://github.com/burrowers/garble/blob/master/hash.go "hash.go") | [hash.go](https://github.com/burrowers/garble/blob/master/hash.go "hash.go") | [Prevent automated plaintext extraction of literals with current tools (](https://github.com/burrowers/garble/commit/d47e0761eb51dedbce86a4f142ab45154f46adb1 "Prevent automated plaintext extraction of literals with current tools (#930)  Some programs which could automatically reverse string literals obfuscated with `-literals` exist.  They currently work by emulating the string literal decryption functions we insert.  We prevent this naive emulation from succeeding by making the decryption functions dependent on global state.  This can still be broken with enough effort, we are curious which approach reverse-engineers come up with next, we certainly still have some ideas to make this harder.  Fixes #926 ---------  Co-authored-by: Paul Scheduikat <lu4p@pm.me>") […](https://github.com/burrowers/garble/pull/930) | 9 months agoJun 2, 2025 |
| [main.go](https://github.com/burrowers/garble/blob/master/main.go "main.go") | [main.go](https://github.com/burrowers/garble/blob/master/main.go "main.go") | [support Go versions with X: suffixes for GOEXPERIMENTs](https://github.com/burrowers/garble/commit/37e582d5813b3cd05bcc6350876441bcbb430abf "support Go versions with X: suffixes for GOEXPERIMENTs  A workaround until https://github.com/golang/go/issues/75953 is fixed.  See #978.") | 4 months agoOct 18, 2025 |
| [main\_test.go](https://github.com/burrowers/garble/blob/master/main_test.go "main_test.go") | [main\_test.go](https://github.com/burrowers/garble/blob/master/main_test.go "main_test.go") | [clarify why TestScript sets GONOSUMDB (](https://github.com/burrowers/garble/commit/59eee83beb8bd7433cb64149efcee4ee95333981 "clarify why TestScript sets GONOSUMDB (#958)  And unset it in gotoolchain.txtar, as that one testscript does fetch modules from the real proxy.golang.org.  Closes #950.") [#958](https://github.com/burrowers/garble/pull/958) [)](https://github.com/burrowers/garble/commit/59eee83beb8bd7433cb64149efcee4ee95333981 "clarify why TestScript sets GONOSUMDB (#958)  And unset it in gotoolchain.txtar, as that one testscript does fetch modules from the real proxy.golang.org.  Closes #950.") | 8 months agoJun 15, 2025 |
| [position.go](https://github.com/burrowers/garble/blob/master/position.go "position.go") | [position.go](https://github.com/burrowers/garble/blob/master/position.go "position.go") | [start using go/ast.Preorder](https://github.com/burrowers/garble/commit/fa2e718bd1ce25d26504903b6dc8aa7f07603c04 "start using go/ast.Preorder  Thanks to being able to use range-over-func, some control flow in our code gets simplified.") | last yearFeb 22, 2025 |
| [reflect.go](https://github.com/burrowers/garble/blob/master/reflect.go "reflect.go") | [reflect.go](https://github.com/burrowers/garble/blob/master/reflect.go "reflect.go") | [refactor main into pieces](https://github.com/burrowers/garble/commit/28f7a7ffbfbe07c8b3898a891f93fed4b22e5508 "refactor main into pieces  * reflect_abi_patch.go was added into reflect.go * shared.go was renamed into cache_shared.go and package caching was moved to cache_pkg.go * transformer methods in main.go are moved to transformer.go") | 5 months agoSep 8, 2025 |
| [reflect\_abi\_code.go](https://github.com/burrowers/garble/blob/master/reflect_abi_code.go "reflect_abi_code.go") | [reflect\_abi\_code.go](https://github.com/burrowers/garble/blob/master/reflect_abi_code.go "reflect_abi_code.go") | [go back to sorting \_originalNamePairs lexicographically](https://github.com/burrowers/garble/commit/30d1d8cbb7296aa88d2baa94fd98e9316e747ccf "go back to sorting _originalNamePairs lexicographically  Now that we only use the list to create a replacer at init time, we no longer need to spend extra effort sorting by length first. The benchmark shows no measurable difference in performance.") | 2 years agoDec 1, 2024 |
| [reverse.go](https://github.com/burrowers/garble/blob/master/reverse.go "reverse.go") | [reverse.go](https://github.com/burrowers/garble/blob/master/reverse.go "reverse.go") | [support reversing asm filenames](https://github.com/burrowers/garble/commit/33e574685bb84850f9e9ef7638f640815af42775 "support reversing asm filenames  Which can be helpful when debugging assembly build errors such as the one from #948. I could not get an obfuscated binary to ever print or show its assembly positions or filenames, so this has no test.") | 5 months agoSep 8, 2025 |
| [runtime\_patch.go](https://github.com/burrowers/garble/blob/master/runtime_patch.go "runtime_patch.go") | [runtime\_patch.go](https://github.com/burrowers/garble/blob/master/runtime_patch.go "runtime_patch.go") | [stop ignoring GODEBUG when -tiny is used](https://github.com/burrowers/garble/commit/65ffaa0efb591c12a659ad4974b2b7fca20c0154 "stop ignoring GODEBUG when -tiny is used  GODEBUG started being used for configuring the behavior of the Go toolchain and standard library, for the sake of smoother transitions in terms of backwards and forwards compatibility. See: https://go.dev/doc/godebug  As such, it is not right to have `garble build -tiny` ignore all GODEBUG settings, because many GODEBUG keys nowadays do not actually involve debugging what a Go binary is doing.  Moreover, the mechanism we were using broke with Go 1.25.2, which refactored `func parsedebugvars()` into `func parseRuntimeDebugVars(godebug string)`, so our test started breaking as our runtime patching was broken.") | 4 months agoOct 18, 2025 |
| [transformer.go](https://github.com/burrowers/garble/blob/master/transformer.go "transformer.go") | [transformer.go](https://github.com/burrowers/garble/blob/master/transformer.go "transformer.go") | [refactor main into pieces](https://github.com/burrowers/garble/commit/28f7a7ffbfbe07c8b3898a891f93fed4b22e5508 "refactor main into pieces  * reflect_abi_patch.go was added into reflect.go * shared.go was renamed into cache_shared.go and package caching was moved to cache_pkg.go * transformer methods in main.go are moved to transformer.go") | 5 months agoSep 8, 2025 |
| View all files |

## Repository files navigation

# garble

[Permalink: garble](https://github.com/burrowers/garble#garble)

```
go install mvdan.cc/garble@latest
```

Obfuscate Go code by wrapping the Go toolchain. Requires Go 1.25 or later.

```
garble build [build flags] [packages]
```

The tool also supports `garble test` to run tests with obfuscated code,
`garble run` to obfuscate and execute simple programs,
and `garble reverse` to de-obfuscate text such as stack traces.
Run `garble -h` to see all available commands and flags.

You can also use `go install mvdan.cc/garble@master` to install the latest development version.

### Purpose

[Permalink: Purpose](https://github.com/burrowers/garble#purpose)

Produce a binary that works as well as a regular build, but that has as little
information about the original source code as possible.

The tool is designed to be:

- Coupled with `cmd/go`, to support modules and build caching
- Deterministic and reproducible, given the same initial source code
- Reversible given the original source, to de-obfuscate panic stack traces

### Mechanism

[Permalink: Mechanism](https://github.com/burrowers/garble#mechanism)

The tool wraps calls to the Go compiler and linker to transform the Go build, in
order to:

- Replace as many useful identifiers as possible with short base64 hashes
- Replace package paths with short base64 hashes
- Replace filenames and position information with short base64 hashes
- Remove all [build](https://go.dev/pkg/runtime/#Version) and [module](https://go.dev/pkg/runtime/debug/#ReadBuildInfo) information
- Strip debugging information and symbol tables via `-ldflags="-w -s"`
- [Obfuscate literals](https://github.com/burrowers/garble#literal-obfuscation), if the `-literals` flag is given
- Remove [extra information](https://github.com/burrowers/garble#tiny-mode), if the `-tiny` flag is given

By default, the tool obfuscates all the packages being built.
You can manually specify which packages to obfuscate via `GOGARBLE`,
a comma-separated list of glob patterns matching package path prefixes.
This format is borrowed from `GOPRIVATE`; see `go help private`.

Note that commands like `garble build` will use the `go` version found in your
`$PATH`. To use different versions of Go, you can
[install them](https://go.dev/doc/manage-install#installing-multiple)
and set up `$PATH` with them. For example, for Go 1.17.1:

```
$ go install golang.org/dl/go1.17.1@latest
$ go1.17.1 download
$ PATH=$(go1.17.1 env GOROOT)/bin:${PATH} garble build
```

### Use cases

[Permalink: Use cases](https://github.com/burrowers/garble#use-cases)

A common question is why a code obfuscator is needed for Go, a compiled language.
Go binaries include a surprising amount of information about the original source;
even with debug information and symbol tables stripped, many names and positions
remain in place for the sake of traces, reflection, and debugging.

Some use cases for Go require sharing a Go binary with the end user.
If the source code for the binary is private or requires a purchase,
its obfuscation can help discourage reverse engineering.

A similar use case is a Go library whose source is private or purchased.
Since Go libraries cannot be imported in binary form, and Go plugins
[have their shortcomings](https://github.com/golang/go/issues/19282),
sharing obfuscated source code becomes an option.
See [#369](https://github.com/burrowers/garble/issues/369).

Obfuscation can also help with aspects entirely unrelated to licensing.
For example, the `-tiny` flag can make binaries 15% smaller,
similar to the [common practice in Android](https://developer.android.com/build/shrink-code#obfuscate) to reduce app sizes.
Obfuscation has also helped some open source developers work around
anti-virus scans incorrectly treating Go binaries as malware.

### Literal obfuscation

[Permalink: Literal obfuscation](https://github.com/burrowers/garble#literal-obfuscation)

Using the `-literals` flag causes literal expressions such as strings to be
replaced with more complex expressions, resolving to the same value at run-time.
String literals injected via `-ldflags=-X` are also replaced by this flag.
This feature is opt-in, as it can cause slow-downs depending on the input code.

Literals used in constant expressions cannot be obfuscated, since they are
resolved at compile time. This includes any expressions part of a `const`
declaration, for example.

Note that this process can be reversed given enough effort;
see [#984](https://github.com/burrowers/garble/issues/984).

### Tiny mode

[Permalink: Tiny mode](https://github.com/burrowers/garble#tiny-mode)

With the `-tiny` flag, even more information is stripped from the Go binary.
Position information is removed entirely, rather than being obfuscated.
Runtime code which prints panics, fatal errors, and trace/debug info is removed.
Many symbol names are also omitted from binary sections at link time.
All in all, this can make binaries about 15% smaller.

With this flag, no panics or fatal runtime errors will ever be printed, but they
can still be handled internally with `recover` as normal.

Note that this flag can make debugging crashes harder, as a panic will simply
exit the entire program without printing a stack trace, and source code
positions and many names are removed.
Similarly, `garble reverse` is generally not useful in this mode.

### Control flow obfuscation

[Permalink: Control flow obfuscation](https://github.com/burrowers/garble#control-flow-obfuscation)

See: [CONTROLFLOW.md](https://github.com/burrowers/garble/blob/master/docs/CONTROLFLOW.md)

### Speed

[Permalink: Speed](https://github.com/burrowers/garble#speed)

`garble build` should take about twice as long as `go build`, as it needs to
complete two builds. The original build, to be able to load and type-check the
input code, and then the obfuscated build.

Garble obfuscates one package at a time, mirroring how Go compiles one package
at a time. This allows Garble to fully support Go's build cache; incremental
`garble build` calls should only re-build and re-obfuscate modified code.

Note that the first call to `garble build` may be comparatively slow,
as it has to obfuscate each package for the first time. This is akin to clearing
`GOCACHE` with `go clean -cache` and running a `go build` from scratch.

Garble also makes use of its own cache to reuse work, akin to Go's `GOCACHE`.
It defaults to a directory under your user's cache directory,
such as `~/.cache/garble`, and can be placed elsewhere by setting `GARBLE_CACHE`.

### Determinism and seeds

[Permalink: Determinism and seeds](https://github.com/burrowers/garble#determinism-and-seeds)

Just like Go, garble builds are deterministic and reproducible in nature.
This has significant benefits, such as caching builds and being able to use
`garble reverse` to de-obfuscate stack traces.

By default, garble will obfuscate each package in a unique way,
which will change if its build input changes: the version of garble, the version
of Go, the package's source code, or any build parameter such as GOOS or -tags.
This is a reasonable default since guessing those inputs is very hard.

You can use the `-seed` flag to provide your own obfuscation randomness seed.
Reusing the same seed can help produce the same code obfuscation,
which can help when debugging or reproducing problems.
Regularly rotating the seed can also help against reverse-engineering in the long run,
as otherwise one can look at changes in how Go's standard library is obfuscated
to guess when the Go or garble versions were changed across a series of builds.

To always use a different seed for each build, use `-seed=random`.
Note that extra care should be taken when using custom seeds:
if a `-seed` value used in a build is lost, `garble reverse` will not work.

### Caveats

[Permalink: Caveats](https://github.com/burrowers/garble#caveats)

Most of these can improve with time and effort. The purpose of this section is
to document the current shortcomings of this tool.

- Exported methods are never obfuscated at the moment, since they could
be required by interfaces. This area is a work in progress; see
[#3](https://github.com/burrowers/garble/issues/3).

- Aside from `GOGARBLE` to select patterns of packages to obfuscate,
there is no supported way to exclude obfuscating a selection of files or packages.
More often than not, a user would want to do this to work around a bug; please file the bug instead.

- Go programs [are initialized](https://go.dev/ref/spec#Program_initialization) one package at a time,
where imported packages are always initialized before their importers,
and otherwise they are initialized in the lexical order of their import paths.
Since garble obfuscates import paths, this lexical order may change arbitrarily.

- Go plugins are not currently supported; see [#87](https://github.com/burrowers/garble/issues/87).

- Garble requires `git` to patch the linker. That can be avoided once go-gitdiff
supports [non-strict patches](https://github.com/bluekeyes/go-gitdiff/issues/30).

- APIs like [`runtime.GOROOT`](https://pkg.go.dev/runtime#GOROOT)
and [`runtime/debug.ReadBuildInfo`](https://pkg.go.dev/runtime/debug#ReadBuildInfo)
will not work in obfuscated binaries. This [can affect loading timezones](https://github.com/golang/go/issues/51473#issuecomment-2490564684), for example.


### Contributing

[Permalink: Contributing](https://github.com/burrowers/garble#contributing)

We welcome new contributors. If you would like to contribute, see
[CONTRIBUTING.md](https://github.com/burrowers/garble/blob/master/CONTRIBUTING.md) as a starting point.

## About

Obfuscate Go builds


### Topics

[golang](https://github.com/topics/golang "Topic: golang") [obfuscation](https://github.com/topics/obfuscation "Topic: obfuscation") [build](https://github.com/topics/build "Topic: build") [binary](https://github.com/topics/binary "Topic: binary") [code-obfuscator](https://github.com/topics/code-obfuscator "Topic: code-obfuscator")

### Resources

[Readme](https://github.com/burrowers/garble#readme-ov-file)

### License

[BSD-3-Clause license](https://github.com/burrowers/garble#BSD-3-Clause-1-ov-file)

### Contributing

[Contributing](https://github.com/burrowers/garble#contributing-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/burrowers/garble).

[Activity](https://github.com/burrowers/garble/activity)

[Custom properties](https://github.com/burrowers/garble/custom-properties)

### Stars

[**5.3k**\\
stars](https://github.com/burrowers/garble/stargazers)

### Watchers

[**41**\\
watching](https://github.com/burrowers/garble/watchers)

### Forks

[**340**\\
forks](https://github.com/burrowers/garble/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fburrowers%2Fgarble&report=burrowers+%28user%29)

## [Releases\  25](https://github.com/burrowers/garble/releases)

[v0.15.0\\
Latest\\
\\
on Aug 31, 2025Aug 31, 2025](https://github.com/burrowers/garble/releases/tag/v0.15.0)

[\+ 24 releases](https://github.com/burrowers/garble/releases)

## Sponsor this project

- [![@mvdan](https://avatars.githubusercontent.com/u/3576549?s=64&v=4)](https://github.com/mvdan)[**mvdan** Daniel Martí](https://github.com/mvdan)[Sponsor @mvdan](https://github.com/sponsors/mvdan)
- [![@pagran](https://avatars.githubusercontent.com/u/67878280?s=64&v=4)](https://github.com/pagran)[**pagran**](https://github.com/pagran)[Sponsor @pagran](https://github.com/sponsors/pagran)

[Learn more about GitHub Sponsors](https://github.com/sponsors)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/burrowers/garble).

## [Contributors\  22](https://github.com/burrowers/garble/graphs/contributors)

- [![@mvdan](https://avatars.githubusercontent.com/u/3576549?s=64&v=4)](https://github.com/mvdan)
- [![@luantak](https://avatars.githubusercontent.com/u/46541492?s=64&v=4)](https://github.com/luantak)
- [![@pagran](https://avatars.githubusercontent.com/u/67878280?s=64&v=4)](https://github.com/pagran)
- [![@capnspacehook](https://avatars.githubusercontent.com/u/23243104?s=64&v=4)](https://github.com/capnspacehook)
- [![@kortschak](https://avatars.githubusercontent.com/u/275221?s=64&v=4)](https://github.com/kortschak)
- [![@sig1nt](https://avatars.githubusercontent.com/u/8923630?s=64&v=4)](https://github.com/sig1nt)
- [![@dlespiau](https://avatars.githubusercontent.com/u/7986?s=64&v=4)](https://github.com/dlespiau)
- [![@nick-jones](https://avatars.githubusercontent.com/u/350792?s=64&v=4)](https://github.com/nick-jones)
- [![@zwass](https://avatars.githubusercontent.com/u/575602?s=64&v=4)](https://github.com/zwass)
- [![@dydysy](https://avatars.githubusercontent.com/u/3320510?s=64&v=4)](https://github.com/dydysy)
- [![@DominicBreuker](https://avatars.githubusercontent.com/u/5805095?s=64&v=4)](https://github.com/DominicBreuker)
- [![@NHAS](https://avatars.githubusercontent.com/u/6820641?s=64&v=4)](https://github.com/NHAS)
- [![@Hritik14](https://avatars.githubusercontent.com/u/7457065?s=64&v=4)](https://github.com/Hritik14)
- [![@fakeboboliu](https://avatars.githubusercontent.com/u/7552030?s=64&v=4)](https://github.com/fakeboboliu)

[\+ 8 contributors](https://github.com/burrowers/garble/graphs/contributors)

## Languages

- [Go98.9%](https://github.com/burrowers/garble/search?l=go)
- [Shell1.1%](https://github.com/burrowers/garble/search?l=shell)

You can’t perform that action at this time.