# https://blog.scrt.ch/2020/06/19/engineering-antivirus-evasion/

­

Engineering antivirus evasion – SCRT Team Blog

[Skip to content](https://blog.scrt.ch/2020/06/19/engineering-antivirus-evasion/#content)

**tl;dr:** this blog post documents some aspects of our research on antivirus software and how we managed to automatically refactor Meterpreter to bypass every AV/EDR we were put up against. While the ideas for every technique and the implementation of the string obfuscation pass are detailed below, we decided to publish details on API imports hiding / syscalls rewriting in future blog posts to keep this one as short as possible. The source code is available at [https://github.com/scrt/avcleaner](https://github.com/scrt/avcleaner)

* * *

Among the defensive measures a company can implement to protect its information systems against attacks, security software such as antivirus or EDR often come up as an essential toolset to have. While it used to be rather easy to circumvent any kind of malware detection mechanism in the past years, doing so nowadays certainly involves more effort.

On the other hand, communicating about the risks associated with a vulnerability is really challenging in case the Proof-of-Concept to exploit it is itself blocked by an antivirus. While one can claim that it is always theoretically possible to bypass the detection \[1\] and leave it at that, actually doing it may add some strength to the argument.

In addition, there are vulnerabilities that can only be discovered with an existing foothold on a system. For example, in the case where a pentester is not able to get that initial level of access, the audit’s result would not accurately depict the actual security level of the systems in scope.

In view of that, there is a need to be able to circumvent antivirus software. To complicate things, at SCRT we rely on publicly available, open-source tools whenever possible, to emphasise that our work is reproducible by anyone skilled enough to use them, and does not depend on private, expensive tools.

## Problem statement

The community likes to categorise the detection mechanisms of any antivirus as being “static” or “dynamic”. Generally, if detection is triggered before the malware’s execution, it is seen as a kind of static detection.

However, it is worth knowing that a static detection mechanism such as signatures can be invoked during the malware’s execution in reaction to events such as process creations, in-memory file downloads, and so on.

In any case, if we want to use the good old Meterpreter against any kind of security software, we must modify it in such a way that it fulfills the following requirements:

- Bypass any static signature, whether during a filesystem scan or a memory scan.
- Bypass “behavioural detection” which, more often than not, relates to evading userland API hooking.

However, Meterpreter comprises several modules, and the whole codebase amounts to around 700’000 lines of code. In addition, it is constantly updated, which means running a private fork of the project is sure to scale very poorly.

In short, we need a way to transform the codebase automatically.

## Solutions

After years of experience bypassing antivirus software, if there is any kind of insight that we could share with the community, it would be that a malware detection is almost always trivially based on strings, API hooks, or a combination of both.

Even for the products that implement machine learning classifiers such as Cylance, a malware that does not have strings, API imports and hookable API calls is sure to go through the net like a soccer ball through Sergio Rico’s defence.

Meterpreter has thousands of strings, API imports are not hidden in any way and sensitive APIs such as “WriteProcessMemory” can be intercepted easily with a userland API hook. So, we need to remedy that in an automated fashion, which yields two potential solutions:

- Source-to-source code refactoring
- LLVM passes to obfuscate the code base at compilation time.

The latter would be the preferred approach, and many popular researches reached the same conclusion \[2\]. The main reason is that a transformation pass can be written once and reused independently of the software’s programming language or target architecture.

[![](https://blog.scrt.ch/wp-content/uploads/2020/06/LLVMCompiler1.png)](https://blog.scrt.ch/wp-content/uploads/2020/06/LLVMCompiler1.png) Image from: http://www.aosabook.org/en/llvm.html

However, doing so requires the ability to compile Meterpreter with a compiler other than Visual Studio. While we have published some work to change that in December 2018, adoption in the official codebase is still an ongoing process more than a year later.

In the meantime, we have decided to implement the first approach out of spite. After a thorough review of the state-of-the-art of source code refactoring, _libTooling_ (part of the Clang/LLVM toolchain) appeared to be the only viable candidate to parse C/C++ source code and modify it.

Note: since the codebase is strongly Visual Studio dependent, Clang will fail to parse a large part of Metepreter. However, it was still possible to bypass the target antivirus with that half-success. And here we probably have the only advantage of source-to-source transformation over compile-time transformation: the latter requires the whole project to compile without any errors. The former is resilient to thousands of compilation errors; you just end up with an incomplete Abstract Syntax Tree, which is perfectly fine.

![](https://blog.scrt.ch/wp-content/uploads/2020/06/45n9vu.jpg)LLVM passes vs _libTooling_

### String obfuscation

In C/C++, a string may be located in many different contexts. _libTooling_ is not really pleasurable to toy with, so we have applied Pareto’s Law and limited ourselves to those that cover the most suspicious string occurrences within Meterpreter’s codebase:

- Function arguments
- List initializers

#### Function arguments

For instance, we know for a fact that ESET Nod32 will flag the string “ntdll” as being suspicious in the following context:

```
ntdll = LoadLibrary(TEXT("ntdll"))
```

However, rewriting this code snippet in the following manner successfully bypasses the detection:

```
wchar_t ntdll_str[] = {'n','t','d','l','l',0};
ntdll = LoadLibrary(ntdll_str)
```

Behind the scenes, the first snippet will cause the string “ _ntdll_” to be stored inside the _.rdata_ section of the resulting binary, and can be easily spotted by the antivirus. The second snippet will cause the string to be stored on the stack at runtime, and is statically indistinguishable from code, at least in the general case. _IDA Pro_ or alternatives are often able to recognise the string, but they also run more advanced and computationally intensive analyses on the binary.

#### List initializers

In _Meterpreter’s_ codebase, this kind of construct can be found in several files, for instance in _[c/meterpreter/source/extensions/extapi/extapi.c](https://github.com/rapid7/metasploit-payloads/blob/c8aa435b3c4872c58dba04acf53d157c3de2771c/c/meterpreter/source/extensions/extapi/extapi.c#L23)_:

```
Command customCommands[] =
{
    COMMAND_REQ("extapi_window_enum", request_window_enum),
    COMMAND_REQ("extapi_service_enum", request_service_enum),
    COMMAND_REQ("extapi_service_query", request_service_query),
    COMMAND_REQ("extapi_service_control", request_service_control),
    COMMAND_REQ("extapi_clipboard_get_data", request_clipboard_get_data),
    COMMAND_REQ("extapi_clipboard_set_data", request_clipboard_set_data),
    COMMAND_REQ("extapi_clipboard_monitor_start", request_clipboard_monitor_start),
    COMMAND_REQ("extapi_clipboard_monitor_pause", request_clipboard_monitor_pause),
    COMMAND_REQ("extapi_clipboard_monitor_resume", request_clipboard_monitor_resume),
    COMMAND_REQ("extapi_clipboard_monitor_purge", request_clipboard_monitor_purge),
    COMMAND_REQ("extapi_clipboard_monitor_stop", request_clipboard_monitor_stop),
    COMMAND_REQ("extapi_clipboard_monitor_dump", request_clipboard_monitor_dump),
    COMMAND_REQ("extapi_adsi_domain_query", request_adsi_domain_query),
    COMMAND_REQ("extapi_ntds_parse", ntds_parse),
    COMMAND_REQ("extapi_wmi_query", request_wmi_query),
    COMMAND_REQ("extapi_pageant_send_query", request_pageant_send_query),
    ...
}
```

Those strings will be stored in clear-text in the _.rdata_ section of _ext\_server\_espia.x64.dll_ and picked up by _ESET Nod32_ for instance.

To make things worse, those strings are parameters to a macro, located in a list initialiser. This introduces a bunch of tricky corner cases that are not obvious to overcome. The goal is to rewrite this snippet automatically as follows:

```
char hid_extapi_UQOoNXigAPq4[] = {'e','x','t','a','p','i','_','w','i','n','d','o','w','_','e','n','u','m',0};
char hid_extapi_vhFHmZ8u2hfz[] = {'e','x','t','a','p','i','_','s','e','r','v','i','c','e','_','e','n','u','m',0};
char hid_extapi_pW25eeIGBeru[] = {'e','x','t','a','p','i','_','s','e','r','v','i','c','e','_','q','u','e','r','y'
0};
char hid_extapi_S4Ws57MYBjib[] = {'e','x','t','a','p','i','_','s','e','r','v','i','c','e','_','c','o','n','t','r'
'o','l',0};
char hid_extapi_HJ0lD9Dl56A4[] = {'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','g','e','t'
'_','d','a','t','a',0};
char hid_extapi_IiEzXils3UsR[] = {'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','s','e','t'
'_','d','a','t','a',0};
char hid_extapi_czLOBo0HcqCP[] = {'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','m','o','n'
'i','t','o','r','_','s','t','a','r','t',0};
char hid_extapi_WcWbTrsQujiT[] = {'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','m','o','n'
'i','t','o','r','_','p','a','u','s','e',0};
char hid_extapi_rPiFTZW4ShwA[] = {'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','m','o','n'
'i','t','o','r','_','r','e','s','u','m','e',0};
char hid_extapi_05fAoaZLqOoy[] = {'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','m','o','n'
'i','t','o','r','_','p','u','r','g','e',0};
char hid_extapi_cOOyHTPTvZGK[] = {'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','m','o','n','i','t','o','r','_','s','t','o','p',0};
char hid_extapi_smtmvW05cI9y[] = {'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','m','o','n','i','t','o','r','_','d','u','m','p',0};
char hid_extapi_01kuYCM8z49k[] = {'e','x','t','a','p','i','_','a','d','s','i','_','d','o','m','a','i','n','_','q','u','e','r','y',0};
char hid_extapi_SMK9uFj6nThk[] = {'e','x','t','a','p','i','_','n','t','d','s','_','p','a','r','s','e',0};
char hid_extapi_PHxnGM7M0609[] = {'e','x','t','a','p','i','_','w','m','i','_','q','u','e','r','y',0};
char hid_extapi_J7EGS6FRHwkV[] = {'e','x','t','a','p','i','_','p','a','g','e','a','n','t','_','s','e','n','d','_','q','u','e','r','y',0};

Command customCommands[] =
{

    COMMAND_REQ(hid_extapi_UQOoNXigAPq4, request_window_enum),
    COMMAND_REQ(hid_extapi_vhFHmZ8u2hfz, request_service_enum),
    COMMAND_REQ(hid_extapi_pW25eeIGBeru, request_service_query),
    COMMAND_REQ(hid_extapi_S4Ws57MYBjib, request_service_control),
    COMMAND_REQ(hid_extapi_HJ0lD9Dl56A4, request_clipboard_get_data),
    COMMAND_REQ(hid_extapi_IiEzXils3UsR, request_clipboard_set_data),
    COMMAND_REQ(hid_extapi_czLOBo0HcqCP, request_clipboard_monitor_start),
    COMMAND_REQ(hid_extapi_WcWbTrsQujiT, request_clipboard_monitor_pause),
    COMMAND_REQ(hid_extapi_rPiFTZW4ShwA, request_clipboard_monitor_resume),
    COMMAND_REQ(hid_extapi_05fAoaZLqOoy, request_clipboard_monitor_purge),
    COMMAND_REQ(hid_extapi_cOOyHTPTvZGK, request_clipboard_monitor_stop),
    COMMAND_REQ(hid_extapi_smtmvW05cI9y, request_clipboard_monitor_dump),
    COMMAND_REQ(hid_extapi_01kuYCM8z49k, request_adsi_domain_query),
    COMMAND_REQ(hid_extapi_SMK9uFj6nThk, ntds_parse),
    COMMAND_REQ(hid_extapi_PHxnGM7M0609, request_wmi_query),
    COMMAND_REQ(hid_extapi_J7EGS6FRHwkV, request_pageant_send_query),
    COMMAND_TERMINATOR
};
```

### Hiding API Imports

Calling functions exported by external libraries causes the linker to write an entry into the _Import Address Table_ (IAT). As a result, the function name will appear as clear-text within the binary, and thus can be recovered statically without even executing the malware. Of course, there are function names that are more suspicious than others. It would be wise to hide all the suspicious ones and keep the ones that are present in the majority of legitimate binaries.

For instance, in the _kiwi_ extension of Metepreter, one can find the following line:

```
enumStatus = SamEnumerateUsersInDomain(hDomain, &EnumerationContext, 0, &pEnumBuffer, 100, &CountRetourned);
```

This function is exported by _samlib.dll_, so the linker will cause the strings “ _samlib.dll_” and “ _SamEnumerateUsersInDomain_” to appear in the compiled binary.

To solve this issue, it is possible to import the API at runtime using _LoadLibrary / GetProcAddresss_. Of course, both these functions work with strings, so they must be obfuscated as well. Thus, we would like to automatically rewrite the above snippet as follows:

```
typedef NTSTATUS(__stdcall* _SamEnumerateUsersInDomain)(
    SAMPR_HANDLE DomainHandle,
    PDWORD EnumerationContext,
    DWORD UserAccountControl,
    PSAMPR_RID_ENUMERATION* Buffer,
    DWORD PreferedMaximumLength,
    PDWORD CountReturned
);
char hid_SAMLIB_01zmejmkLCHt[] = {'S','A','M','L','I','B','.','D','L','L',0};
char hid_SamEnu_BZxlW5ZBUAAe[] = {'S','a','m','E','n','u','m','e','r','a','t','e','U','s','e','r','s','I','n','D','o','m','a','i','n',0};
HANDLE hhid_SAMLIB_BZUriyLrlgrJ = LoadLibrary(hid_SAMLIB_01zmejmkLCHt);
_SamEnumerateUsersInDomain ffSamEnumerateUsersInDoma =(_SamEnumerateUsersInDomain)GetProcAddress(hhid_SAMLIB_BZUriyLrlgrJ, hid_SamEnu_BZxlW5ZBUAAe);
enumStatus = ffSamEnumerateUsersInDoma(hDomain, &EnumerationContext, 0, &pEnumBuffer, 100, &CountRetourned);
```

### Rewriting syscalls

By default, using the _migrate_ command of Meterpreter on a machine where Cylance is running triggers the antivirus detection (for now, just take our word for it). Cylance detects the process injection with a userland hook. To get around the detection, one can remove the hook, which seems to be the trending approach nowadays, or simply avoid it altogether. We found it simpler to read _ntdll_, recover the syscall number and insert it in a ready-to-call shellcode, which effectively gets around any antivirus’ userland’s hooks. To date, we have yet to find a Blue-Team that identifies _NTDLL.DLL_ being read from disk as being “suspicious”.

## Implementation

All the aforementioned ideas can be implemented in a source code refactoring tool based on _libTooling_. This section documents the way we did it, which is a compromise between time available and patience with the lack of _libTooling_ documentation. So, there is room for improvements, and in case something looks off to you, it probably is and we would love to hear about it.

### Abstract Syntax Tree 101

A compiler typically comprises several components, the most common ones being a _Parser_ and a _Lexer_. When source code is fed to the compiler, it first generates a _Parse Tree_ out of the original source code (what the programmer wrote), and then adds semantic information to the nodes (what the compiler truly needs). The result of this step is called an _Abstract Syntax Tree_. Wikipedia showcases the following example:

```
while b ≠ 0
  if a > b
    a := a − b
  else
    b := b − a
return a
```

A typical AST for this small program would look like this:

![](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Abstract_syntax_tree_for_Euclidean_algorithm.svg/1920px-Abstract_syntax_tree_for_Euclidean_algorithm.svg.png)Example of an Abstract Syntax Tree ( [https://en.wikipedia.org/wiki/Abstract\_syntax\_tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree))

This data structure allows for more precise algorithms when it comes to writing programs that understand properties of other programs, so it seems like a good choice to perform large scale code refactoring.

#### Clang’s Abstract Syntax Tree

Since we need to modify source code The Right WayTM, we will need to get acquainted with _Clang_‘s AST. The good news is that _Clang_ exposes a command-line switch to dump the AST with pretty colours. The bad news is that for everything but toy projects, setting the correct compiler flags is… tricky.

For now, let us have a realistic yet simple enough test translation unit:

```
#include <windows.h>

typedef NTSTATUS (NTAPI *f_NtMapViewOfSection)(HANDLE, HANDLE, PVOID *, ULONG, ULONG,
PLARGE_INTEGER, PULONG, ULONG, ULONG, ULONG);

int main(void)
{
    f_NtMapViewOfSection lNtMapViewOfSection;
    HMODULE ntdll;

    if (!(ntdll = LoadLibrary(TEXT("ntdll"))))
    {
        return -1;
    }

    lNtMapViewOfSection = (f_NtMapViewOfSection)GetProcAddress(ntdll, "NtMapViewOfSection");
    lNtMapViewOfSection(0,0,0,0,0,0,0,0,0,0);
    return 0;
}
```

Then, punch-in the following script into a _.sh_ file (don’t ask how we came up with all those compiler flags, you will bring back painful memories):

```
WIN_INCLUDE="/Users/vladimir/headers/winsdk"
CLANG_PATH="/usr/local/Cellar/llvm/9.0.1"#"/usr/lib/clang/8.0.1/"

clang -cc1 -ast-dump "$1" -D "_WIN64" -D "_UNICODE" -D "UNICODE" -D "_WINSOCK_DEPRECATED_NO_WARNINGS"\
  "-I" "$CLANG_PATH/include" \
  "-I" "$CLANG_PATH" \
  "-I" "$WIN_INCLUDE/Include/msvc-14.15.26726-include"\
  "-I" "$WIN_INCLUDE/Include/10.0.17134.0/ucrt" \
  "-I" "$WIN_INCLUDE/Include/10.0.17134.0/shared" \
  "-I" "$WIN_INCLUDE/Include/10.0.17134.0/um" \
  "-I" "$WIN_INCLUDE/Include/10.0.17134.0/winrt" \
  "-fdeprecated-macro" \
  "-w" \
  "-fdebug-compilation-dir"\
  "-fno-use-cxa-atexit" "-fms-extensions" "-fms-compatibility" \
  "-fms-compatibility-version=19.15.26726" "-std=c++14" "-fdelayed-template-parsing" "-fobjc-runtime=gcc" "-fcxx-exceptions" "-fexceptions" "-fseh-exceptions" "-fdiagnostics-show-option" "-fcolor-diagnostics" "-x" "c++"
```

Notice that _WIN\_INCLUDE_ points to a folder containing all the required headers to interact with the Win32 API. These were taken as-is from a standard Windows 10 install, and to save you some headaches, we recommend that you do the same instead of opting for MinGW’s ones. Then, call the script with the test C file as argument. While this produces a 18MB file, it is easy enough to navigate to the interesting part of the AST by searching for one of the string literals we defined, for instance “ _NtMapViewOfSection_“:

[![](https://blog.scrt.ch/wp-content/uploads/2020/06/output-1024x503.png)](https://blog.scrt.ch/wp-content/uploads/2020/06/output.png)

Now that we have a way to visualise the AST, it is much simpler to understand how we will have to update the nodes to achieve our result, without introducing any syntax errors in the resulting source code. The subsequent sections contain the implementation details related to AST manipulation with _libTooling_.

#### ClangTool boilerplate

Unsurprisingly, there is some required boilerplate code before getting into the interesting stuff, so punch-in the following code into _main.cpp_:

```
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/ASTContext.h"
#include "clang/AST/Decl.h"
#include "clang/AST/Type.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/Basic/SourceManager.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendAction.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Rewrite/Core/Rewriter.h"

// LLVM includes
#include "llvm/ADT/ArrayRef.h"
#include "llvm/ADT/StringRef.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/raw_ostream.h"

#include "Consumer.h"
#include "MatchHandler.h"

#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <fstream>
#include <clang/Tooling/Inclusions/IncludeStyle.h>
#include <clang/Tooling/Inclusions/HeaderIncludes.h>
#include <sstream>

namespace ClSetup {
    llvm::cl::OptionCategory ToolCategory("StringEncryptor");
}

namespace StringEncryptor {

    clang::Rewriter ASTRewriter;
    class Action : public clang::ASTFrontendAction {

    public:
        using ASTConsumerPointer = std::unique_ptr<clang::ASTConsumer>;

        ASTConsumerPointer CreateASTConsumer(clang::CompilerInstance &Compiler,
                                             llvm::StringRef Filename) override {

            ASTRewriter.setSourceMgr(Compiler.getSourceManager(), Compiler.getLangOpts());
            std::vector<ASTConsumer*> consumers;

            consumers.push_back(&StringConsumer);

            // several passes can be combined together by adding them to `consumers`
            auto TheConsumer = llvm::make_unique<Consumer>();
            TheConsumer->consumers = consumers;
            return TheConsumer;
        }

        bool BeginSourceFileAction(clang::CompilerInstance &Compiler) override {
            llvm::outs() << "Processing file " << '\n';
            return true;
        }

        void EndSourceFileAction() override {

            clang::SourceManager &SM = ASTRewriter.getSourceMgr();

            std::string FileName = SM.getFileEntryForID(SM.getMainFileID())->getName();
            llvm::errs() << "** EndSourceFileAction for: " << FileName << "\n";

            // Now emit the rewritten buffer.
            llvm::errs() << "Here is the edited source file :\n\n";
            std::string TypeS;
            llvm::raw_string_ostream s(TypeS);
            auto FileID = SM.getMainFileID();
            auto ReWriteBuffer = ASTRewriter.getRewriteBufferFor(FileID);

            if(ReWriteBuffer != nullptr)
                ReWriteBuffer->write((s));
            else{
                llvm::errs() << "File was not modified\n";
                return;
            }

            std::string result = s.str();
            std::ofstream fo(FileName);

            if(fo.is_open())
                fo << result;
            else
                llvm::errs() << "[!] Error saving result to " << FileName << "\n";
        }
    };
}

auto main(int argc, const char *argv[]) -> int {

    using namespace clang::tooling;
    using namespace ClSetup;

    CommonOptionsParser OptionsParser(argc, argv, ToolCategory);
    ClangTool Tool(OptionsParser.getCompilations(),
                   OptionsParser.getSourcePathList());

    auto Action = newFrontendActionFactory<StringEncryptor::Action>();
    return Tool.run(Action.get());
}
```

Since that boilerplate code is taken from examples in the official documentation, there is no need to describe it further. In fact, the only modification worth mentioning is inside _CreateASTConsumer_. Our end game is to run several tranformation passes on the same translation unit. It can be done by adding items to the _consumers_ collection (the essential line is `consumers.push_back(&...);`).

### String obfuscation

This section describes the most important implementation details regarding the string obfuscation pass, which comprises three steps:

- Locate string literals in the source code.
- Replace them with variables
- Insert a variable definition / assignment at the appropriate location (enclosing function or global context).

#### Locating string literals in source code

_StringConsumer_ can be defined as follows (at the beginning of the _StringEncryptor_ namespace):

```
class StringEncryptionConsumer : public clang::ASTConsumer {
public:

    void HandleTranslationUnit(clang::ASTContext &Context) override {
        using namespace clang::ast_matchers;
        using namespace StringEncryptor;

        llvm::outs() << "[StringEncryption] Registering ASTMatcher...\n";
        MatchFinder Finder;
        MatchHandler Handler(&ASTRewriter);

        const auto Matcher = stringLiteral().bind("decl");

        Finder.addMatcher(Matcher, &Handler);
        Finder.matchAST(Context);
    }
};

StringEncryptionConsumer StringConsumer = StringEncryptionConsumer();
```

Given a translation unit, we can tell _Clang_ to find a pattern inside the AST, as well as register a “handler” to be called whenever a match is found. The pattern matching exposed by _Clang’s_ _[ASTMatcher](https://clang.llvm.org/docs/LibASTMatchersReference.html)_ is quite powerful, and yet underused here, since we only resort to it to locate string literals.

Then, we can get to the heart of the matter by implementing a _MatchHandler_, which will provide us with a _[MatchResult](https://clang.llvm.org/doxygen/structclang_1_1ast__matchers_1_1MatchFinder_1_1MatchResult.html#ab06481084c7027e5779a5a427596f66c)_ instance. A _[MatchResult](https://clang.llvm.org/doxygen/structclang_1_1ast__matchers_1_1MatchFinder_1_1MatchResult.html#ab06481084c7027e5779a5a427596f66c)_ contains a reference to the AST node identified, as well as priceless context information.

Let us implement the class definition and inherit some good stuff from _[clang::ast\_matchers::MatchFinder::MatchCallback](https://clang.llvm.org/doxygen/classclang_1_1ast__matchers_1_1MatchFinder_1_1MatchCallback.html)_:

```
#ifndef AVCLEANER_MATCHHANDLER_H
#define AVCLEANER_MATCHHANDLER_H

#include <vector>
#include <string>
#include <memory>
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/ADT/StringRef.h"
#include "llvm/ADT/ArrayRef.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Frontend/FrontendAction.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Basic/SourceManager.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/AST/Type.h"
#include "clang/AST/Decl.h"
#include "clang/AST/ASTContext.h"
#include "clang/AST/ASTConsumer.h"
#include "MatchHandler.h"

class MatchHandler : public clang::ast_matchers::MatchFinder::MatchCallback {

public:
    using MatchResult = clang::ast_matchers::MatchFinder::MatchResult;

    MatchHandler(clang::Rewriter *rewriter);
    void run(const MatchResult &Result) override; // callback function that runs whenever a Match is found.

};

#endif //AVCLEANER_MATCHHANDLER_H
```

In _MatchHandler.cpp_, we will have to implement MatchHandler’s constructor and the _run_ callback function. The constructor is pretty simple, since it is only needed to store the _[clang::Rewriter](https://clang.llvm.org/doxygen/classclang_1_1Rewriter.html)_‘s instance for later use:

```
using namespace clang;

MatchHandler::MatchHandler(clang::Rewriter *rewriter) {
    this->ASTRewriter = rewriter;
}
```

_run_ is implemented as follows:

```
void MatchHandler::run(const MatchResult &Result) {
    const auto *Decl = Result.Nodes.getNodeAs<clang::StringLiteral>("decl");
    clang::SourceManager &SM = ASTRewriter->getSourceMgr();

    // skip strings in included headers
    if (!SM.isInMainFile(Decl->getBeginLoc()))
        return;

    // strings that comprise less than 5 characters are not worth the effort
    if (!Decl->getBytes().str().size() > 4) {
        return;
    }

    climbParentsIgnoreCast(*Decl, clang::ast_type_traits::DynTypedNode(), Result.Context, 0);
}
```

From the excerpt shown above, there are three elements worth mentioning:

- We extract the AST node that was matched by the pattern defined in _StringEncryptionConsumer_. To do that, one can call the function _[getNodeAs](https://clang.llvm.org/doxygen/classclang_1_1ast__matchers_1_1BoundNodes.html)_, which expects a string as argument that relates to the identifier the pattern was bound to (see the line `const auto Matcher = stringLiteral().bind("decl")`)
- We skip strings that are not defined in the translation unit under analysis. Indeed, our pass intervenes after _Clang_‘s preprocessor, which will actually copy-paste included system headers into the translation unit.
- Then, we are ready to process the string literal. Since we need to know about the context where this string literal was found, we pass the extracted node to a user-defined function, ( _climbParentsIgnoreCast_ in this case, for the lack of a better name), along _[Result.Context](https://clang.llvm.org/doxygen/structclang_1_1ast__matchers_1_1MatchFinder_1_1MatchResult.html#ab06481084c7027e5779a5a427596f66c)_, which contains a reference to the enclosing AST. The goal is to visit the tree upwards until an interesting node is found. In this case, we are interested in a node of type _[CallExpr](https://clang.llvm.org/doxygen/classclang_1_1CallExpr.html)_.

```
bool
MatchHandler::climbParentsIgnoreCast(const StringLiteral &NodeString, clang::ast_type_traits::DynTypedNode node,
                                     clang::ASTContext *const pContext, uint64_t iterations) {

    ASTContext::DynTypedNodeList parents = pContext->getParents(NodeString);

    if (iterations > 0) {
        parents = pContext->getParents(node);
    }

    for (const auto &parent : parents) {

        StringRef ParentNodeKind = parent.getNodeKind().asStringRef();

        if (ParentNodeKind.find("Cast") != std::string::npos) {

            return climbParentsIgnoreCast(NodeString, parent, pContext, ++iterations);
        }

        handleStringInContext(&NodeString, pContext, parent);
    }

    return false;
}
```

In a nutshell, this function recursively looks up the parent nodes of a _StringLiteral_ node, until it finds one that should be interesting (i.e. not a “cast”). _handleStringInContext_ is also straight-forward:

```
void MatchHandler::handleStringInContext(const clang::StringLiteral *pLiteral, clang::ASTContext *const pContext,
                                         const clang::ast_type_traits::DynTypedNode node) {

    StringRef ParentNodeKind = node.getNodeKind().asStringRef();

    if (ParentNodeKind.compare("CallExpr") == 0) {
        handleCallExpr(pLiteral, pContext, node);
    } else if (ParentNodeKind.compare("InitListExpr") == 0) {
        handleInitListExpr(pLiteral, pContext, node);
    } else {
        llvm::outs() << "Unhandled context " << ParentNodeKind << " for string " << pLiteral->getBytes() << "\n";
    }
}
```

As evident from the snippet above, only two kind of nodes are actually handled. It should also be quite easy to add more if needed. Indeed, both cases are already handled in a similar fashion.

```
void MatchHandler::handleCallExpr(const clang::StringLiteral *pLiteral, clang::ASTContext *const pContext,
                                  const clang::ast_type_traits::DynTypedNode node) {

    const auto *FunctionCall = node.get<clang::CallExpr>();

    if (isBlacklistedFunction(FunctionCall)) {
        return; // exclude printf-like functions when the replacement is not constant anymore (C89 standard...).
    }

    handleExpr(pLiteral, pContext, node);
}

void MatchHandler::handleInitListExpr(const clang::StringLiteral *pLiteral, clang::ASTContext *const pContext,
                                      const clang::ast_type_traits::DynTypedNode node) {

    handleExpr(pLiteral, pContext, node);
}
```

#### Replacing string literals

Since both _[CallExpr](https://clang.llvm.org/doxygen/classclang_1_1CallExpr.html)_ and _[InitListExpr](https://clang.llvm.org/doxygen/classclang_1_1InitListExpr.html)_ can be handled in a similar fashion, we define a common function usable by both.

```
bool MatchHandler::handleExpr(const clang::StringLiteral *pLiteral, clang::ASTContext *const pContext,
                                  const clang::ast_type_traits::DynTypedNode node) {

    clang::SourceRange LiteralRange = clang::SourceRange(
            ASTRewriter->getSourceMgr().getFileLoc(pLiteral->getBeginLoc()),
            ASTRewriter->getSourceMgr().getFileLoc(pLiteral->getEndLoc())
    );

    if(shouldAbort(pLiteral, pContext, LiteralRange))
        return false;

    std::string Replacement = translateStringToIdentifier(pLiteral->getBytes().str());

    if(!insertVariableDeclaration(pLiteral, pContext, LiteralRange, Replacement))
        return false ;

    Globs::PatchedSourceLocation.push_back(LiteralRange);

    return replaceStringLiteral(pLiteral, pContext, LiteralRange, Replacement);
}
```

- We randomly generate a variable name.
- Find some empty space at the nearest location and insert the variable declaration. This is basically a wrapper around `ASTRewriter->InsertText()`.
- Replace the string with the identifier generated in step 1.
- Add the string literal location to a collection. This is useful because when visiting _InitListExpr_, the same string literal will appear twice (no idea why).

The last step is the only one that is tricky to implement really, so let us focus on that first:

```
bool MatchHandler::replaceStringLiteral(const clang::StringLiteral *pLiteral, clang::ASTContext *const pContext,
                                        clang::SourceRange LiteralRange,
                                        const std::string& Replacement) {

    // handle "TEXT" macro argument, for instance LoadLibrary(TEXT("ntdll"));
    bool isMacro = ASTRewriter->getSourceMgr().isMacroBodyExpansion(pLiteral->getBeginLoc());

    if (isMacro) {
        StringRef OrigText = clang::Lexer::getSourceText(CharSourceRange(pLiteral->getSourceRange(), true),
                                                         pContext->getSourceManager(), pContext->getLangOpts());

        // weird bug with TEXT Macro / other macros...there must be a proper way to do this.
        if (OrigText.find("TEXT") != std::string::npos) {

            ASTRewriter->RemoveText(LiteralRange);
            LiteralRange.setEnd(ASTRewriter->getSourceMgr().getFileLoc(pLiteral->getEndLoc().getLocWithOffset(-1)));
        }
    }

    return ASTRewriter->ReplaceText(LiteralRange, Replacement);
}
```

Normally, replacing text should be realised with the _[ReplaceText](https://clang.llvm.org/doxygen/classclang_1_1Rewriter.html#afe00ce2338ce67ba76832678f21956ed)_ API, but in practice too many bugs were encountered with it. When it comes to macros, things tend to get very complicated because _Clang’s_ API behaves inconsistently. For instance, if you remove the check `isMacroBodyExpansion()`, you will end up replacing “`TEXT`” instead of its argument.

For instance in `LoadLibrary(TEXT("ntdll"))`, the actual result would be `LoadLibrary(your_variable("ntdll"))`, which is incorrect.

The reason for this is that _TEXT_ is a macro that, when handled by the _Clang’s_ preprocessor, is replaced with `L"ntdll"`. Our transformation pass happens after the preprocessor has done its job, so querying the start and end locations of the token “ _ntdll_” will yield values that are off by a few characters, and are not useful to us. Unfortunately, querying the actual locations in the original translation unit is a kind of black magic with _Clang’s_ API, and the working solution was found with trial-and-error, sorry.

#### Inserting a variable declaration at the nearest empty location

Now that we are able to replace string literals with variable identifiers, the goal is to define that variable and assign it with the value of the original string. In short, we want the patched source code to contain `char your_variable[] = "ntdll"`, without overwriting anything.

There can be two scenarios:

- The string literal is located within a function body.
- The string literal is located outside a function body.

The latter is the most straightforward, since it is only needed to find the start of the expression where the string literal is used.

For the former, we need to find the enclosing function. Then, _Clang_ exposes an API to query the start location of the function body (after the first bracket). This is an ideal place to insert a variable declaration because the variable will be visible in the entire function, and the tokens that we insert will not overwrite stuff.

In any case, both situations are solved by visiting every parent node until a node of type _[FunctionDecl](https://clang.llvm.org/doxygen/classclang_1_1FunctionDecl.html)_ or _[VarDecl](https://clang.llvm.org/doxygen/classclang_1_1VarDecl.html)_ is found:

```
MatchHandler::findInjectionSpot(clang::ASTContext *const Context, clang::ast_type_traits::DynTypedNode Parent,
                                const clang::StringLiteral &Literal, bool IsGlobal, uint64_t Iterations) {

    if (Iterations > CLIMB_PARENTS_MAX_ITER)
        throw std::runtime_error("Reached max iterations when trying to find a function declaration");

    ASTContext::DynTypedNodeList parents = Context->getParents(Literal);;

    if (Iterations > 0) {
        parents = Context->getParents(Parent);
    }

    for (const auto &parent : parents) {

        StringRef ParentNodeKind = parent.getNodeKind().asStringRef();

        if (ParentNodeKind.find("FunctionDecl") != std::string::npos) {
            auto FunDecl = parent.get<clang::FunctionDecl>();
            auto *Statement = FunDecl->getBody();
            auto *FirstChild = *Statement->child_begin();
            return {FirstChild->getBeginLoc(), FunDecl->getEndLoc()};

        } else if (ParentNodeKind.find("VarDecl") != std::string::npos) {

            if (IsGlobal) {
                return parent.get<clang::VarDecl>()->getSourceRange();
            }
        }

        return findInjectionSpot(Context, parent, Literal, IsGlobal, ++Iterations);
    }
}
```

### Test

```
git clone https://github.com/SCRT/avcleaner
mkdir avcleaner/CMakeBuild && cd avcleaner/CMakeBuild
cmake ..
make
cd ..
bash run_example.sh test/string_simplest.c
```

[![](https://blog.scrt.ch/wp-content/uploads/2020/06/Screenshot-2020-06-18-at-17.50.54-1-1024x506.png)](https://blog.scrt.ch/wp-content/uploads/2020/06/Screenshot-2020-06-18-at-17.50.54-1.png)

As you can see, this works pretty well. Now, this example was simple enough that it could have been solved with regexes and way fewer lines of codes. However, even though we are delighted to count the king of regexes (

[@1mm0rt411](https://twitter.com/1mm0rt411) himself) among our ranks, it would have been unfair to challenge him with a task as pesky as string obfuscation in Meterpreter.

#### Going further

For now, strings are not actually encrypted, in spite of the obfuscation pass being named “StringEncryptor”. How much effort is really needed to actually encrypt the strings? Spoiler: a few more hours, but it is a tradition to leave some exercices for the reader 😉

In addition, [@TheColonial](https://twitter.com/TheColonial) recently (April 2020) updated Meterpreter so that it can be compiled with more recent versions of Visual Studio. It means that it should be possible to move on from the C89 standard and handle more corner cases, such as obfuscating the first argument to format string functions.

## To be continued…

As this post is already kind of lengthy, it was decided to split it into several parts. In fact, obfuscating strings was the easy part implementation-wise, although you need to be extremely familiar with _Clang_‘s API. Its documentation being the source code, we recommend allocating a week or two to ingest it as a whole 😛 (and then don’t hesitate to reach out to a specialist for mental health recovery).

The next blog post will be about hiding API Imports automatically.

## References

- \[1\] Rice’s theorem: [https://mathworld.wolfram.com/RicesTheorem.html](https://mathworld.wolfram.com/RicesTheorem.html)
- \[2\] Obfuscator-LLVM – Software Protection for the Masses

_Vladimir Meier_

…

…

…