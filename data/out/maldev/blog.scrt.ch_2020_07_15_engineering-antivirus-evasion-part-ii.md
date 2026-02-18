# https://blog.scrt.ch/2020/07/15/engineering-antivirus-evasion-part-ii/

­

Engineering antivirus evasion (Part II) – SCRT Team Blog

[Skip to content](https://blog.scrt.ch/2020/07/15/engineering-antivirus-evasion-part-ii/#content)

**tl;dr** To interact with the Windows operating system, software often import functions from _Dynamic Link Libraries_ (DLL). These functions are listed in clear-text in a table called _Import Address Table_ and antivirus software tend to capitalise on that to infer malicious behavioural detection. We show ideas and implementation of an obfuscator that allows to refactor any C/C++ software to remove this footprint, with a focus on _Meterpreter_. The source code is available at [https://github.com/scrt/avcleaner](https://github.com/scrt/avcleaner).

# Introduction

In a [previous blog post](https://blog.scrt.ch/2020/06/19/engineering-antivirus-evasion/), we showed how to replace string literals in source code accurately without using regexes. The goal is to reduce the footprint of a binary and blind security software that relies on static signatures.

However, apart from string literals in the source code itself, there are plenty of other fingerprints that can be collected and analysed statically. In this blog post, we will show how one can hide API imports manually from a binary, and then automate the process for every software written in C/C++.

## The problem with API imports

Let us write and build a simple C program that pops up an alert box:

```
#include <Windows.h>
int main(int argc, char** argv) {
    MessageBox(NULL, "Test", "Something", MB_OK);
    return 0;
}
```

Then, build with your favorite compiler. Here, _MinGW_ is used to cross-build from _macOS_ to _Windows_:

```
x86_64-w64-mingw32-gcc test.c -o /tmp/toto.exe
```

Afterwards, one can list the strings using _rabin2_ (included in _radare2_), or even the GNU _strings_ utility:

`rabin2 -zz /tmp/toto.exe | bat`

```
 205   │ 201  0x00003c92 0x00408692 7   8    .idata        ascii   strncmp
 206   │ 202  0x00003c9c 0x0040869c 8   9    .idata        ascii   vfprintf
 207   │ 203  0x00003ca8 0x004086a8 11  12   .idata        ascii   MessageBoxA
 208   │ 204  0x00003d10 0x00408710 12  13   .idata        ascii   KERNEL32.dll
 209   │ 205  0x00003d84 0x00408784 10  11   .idata        ascii   msvcrt.dll
 210   │ 206  0x00003d94 0x00408794 10  11   .idata        ascii   USER32.dll
...

9557   │ 9553 0x0004f481 0x00458e81 30  31                 ascii   .refptr.__native_startup_state
9558   │ 9554 0x0004f4a0 0x00458ea0 11  12                 ascii   __ImageBase
9559   │ 9555 0x0004f4ac 0x00458eac 11  12                 ascii   MessageBoxA
9560   │ 9556 0x0004f4b8 0x00458eb8 12  13                 ascii   GetLastError
9561   │ 9557 0x0004f4c5 0x00458ec5 17  18                 ascii   __imp_MessageBoxA
9562   │ 9558 0x0004f4d7 0x00458ed7 23  24                 ascii   GetSystemTimeAsFileTime
9563   │ 9559 0x0004f4ef 0x00458eef 22  23                 ascii   mingw_initltssuo_force
9564   │ 9560 0x0004f506 0x00458f06 19  20                 ascii   __rt_psrelocs_start
```

As evident from the console output shown above, the string `MessageBoxA` appears three times. This is due to the fact that this function must be imported from the library _User32.dll_ (more on this later).

Of course, this string in particular is not susceptible to raise an antivirus’ eyebrows, but that would definitely be the case for APIs such as:

- InternetReadFile
- ShellExecute
- CreateRemoteThread
- OpenProcess
- ReadProcessMemory
- WriteProcessMemory
- …

## Hiding API imports

Before going further, let us recapitulate the different ways available to developers to call functions in external libraries on Windows systems \[1\]:

- Load-time dynamic linking.
- Run-time dynamic linking.

### Load-time dynamic linking

This is the default approach to resolve function in external libraries and is actually taken care of automatically by the linker. During the build cycle, the application is linked against the _import library_ (.lib) of each Dynamic Link Library (DLL) it depends on. For each imported function, the linker writes an entry into the IAT for the associated DLL.

When the application is started, the operating system scans the IAT and maps all the libraries listed there in the process’ address space, and the addresses of each imported function is updated to point to the corresponding entry in the DLL’s Export Address Table.

[![](https://blog.scrt.ch/wp-content/uploads/2020/07/peformat_iat2-1-1024x567.png)](https://blog.scrt.ch/wp-content/uploads/2020/07/peformat_iat2-1.png) Import Address Table (IAT)

### Run-time dynamic linking

An alternative is to do it manually by first loading the corresponding library with [LoadLibrary](https://docs.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibrarya), and then resolving the function’s address with [GetProcAddress](https://docs.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getprocaddress). For instance, the previous example can be adapted in order to rely on run-time dynamic linking.

First, it is necessary to define a function pointer for the API `MessageBoxA`. Before jumping into that, let us share a small trick to remember the syntax of function pointers in C for those of us that find it unintuitive:

```
<return type> (*<your pointer name>)(arg1, arg2, ...);
```

As you can see, it is the same syntax used to define functions, apart from the star operator (because it is a function _pointer_) and the parenthesis.

Now, we need the prototype of `MessageBox`, which can be copy-pasted from `winuser.h` from the Windows SDK or straight from [MSDN](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox):

```
int MessageBox(
  HWND    hWnd,
  LPCTSTR lpText,
  LPCTSTR lpCaption,
  UINT    uType
);
```

Now, the aforementioned function pointer syntax can be updated with the correct information:

```
int (*_MessageBoxA)(
    HWND hWnd,
    LPCTSTR lpText,
    LPCTSTR lpCaption,
    UINT uType
);
```

MSDN tells us that this function is exported by _User32.dll_:

[![](https://blog.scrt.ch/wp-content/uploads/2020/07/messagebox-1024x473.png)](https://blog.scrt.ch/wp-content/uploads/2020/07/messagebox.png) The API MessageBoxA is exported by User32.dll.

So, the application must first load this library:

```
HANDLE hUser32 = LoadLibrary("User32.dll");
```

Then, `GetProcAddress` can finally be used to assign the correct address to the function pointer defined above:

```
_MessageBoxA fMessageBoxA = (_MessageBoxA) GetProcAddress(hUser32, "MessageBoxA");
```

From there, the original example must be adapted to call `fMessageBoxA` instead of `MessageBoxA`, which gives:

```
#include <Windows.h>

typedef int (*_MessageBoxA)(
  HWND    hWnd,
  LPCTSTR lpText,
  LPCTSTR lpCaption,
  UINT    uType
);

int main(int argc, char** argv) {

    HANDLE hUser32 = LoadLibraryA("User32.dll");
    _MessageBoxA fMessageBoxA = (_MessageBoxA) GetProcAddress(hUser32, "MessageBoxA");
    fMessageBoxA(NULL, "Test", "Something", MB_OK);
    return 0;
}
```

The `Windows.h` include is only required for the data types `HWND`, `LPCTSTR` and `UINT`. Building and running this simple example spawns an alert box, as expected:

[![](https://blog.scrt.ch/wp-content/uploads/2020/07/messageboxa_result.png)](https://blog.scrt.ch/wp-content/uploads/2020/07/messageboxa_result.png) Simplest example of using LoadLibrary and GetProcAddress for run-time dynamic linking.

### Final adaptation

Of course, running `strings` on `toto.exe` will still yield the strings “User32.dll” and “MessageBoxA”. So, those strings should ideally be encrypted, but the simple obfuscation trick shown in the previous blog post suffices to bypass antivirus detection. The end result would be:

```
#include <Windows.h>

typedef int (*_MessageBoxA)(
  HWND    hWnd,
  LPCTSTR lpText,
  LPCTSTR lpCaption,
  UINT    uType
);

int main(int argc, char** argv) {

    char user32[] = {'U','s','e','r','3','2','.','d','l','l',0};
    HANDLE hUser32 = LoadLibraryA(user32);

    char messabox[] = {'M','e','s','s','a','g','e','B','o','x','A',0};
    _MessageBoxA fMessageBoxA = (_MessageBoxA) GetProcAddress(hUser32, messabox);
    fMessageBoxA(NULL, "Test", "Something", MB_OK);
    return 0;
}
```

This time, neither `strings` nor `rabin2` are able to find the string (although a reverse-engineer sure will):

```
➜  x86_64-w64-mingw32-gcc test.c -o /tmp/toto.exe
➜  strings /tmp/toto.exe | grep MessageBox
➜  rabin2 -zz /tmp/toto.exe | grep MessageBox
➜
```

## Automated source code refactoring

The same approach lengthily described in the previous blog post can be used to refactor an existing code-base, so that suspicious API are loaded at runtime and removed from the _Import Address Table_. To do that, we will build upon the existing work realised with `libTooling`.

Let us break down this task as follows:

- Generate the _Abstract Syntax Tree_ for the previous, original example. This is required to understand how to manipulate the nodes to replace a function call.
- Locate all the function calls in a code-base for a given API with an [ASTMatcher](https://clang.llvm.org/docs/LibASTMatchersReference.html).
- Replace all the calls with another function identifier.
- Insert `LoadLibrary` / `GetprocAddress` calls just before each function call.
- Check that it works.
- Generalise and obfuscate all the suspicious API.

### The MessageBox application’s Abstract Syntax Tree

To view Clang’s Abstract Syntax Tree for the original _MessageBox_ application, let us use that script (adapt the path to your Windows SDK):

```
WIN_INCLUDE="/Users/vladimir/dev/avcleaner"
CLANG_PATH="/usr/local/Cellar/llvm/9.0.1"

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

And run it:

```
bash clang-astdump.sh test/messagebox_simple.c > test/messagebox_simple.c.ast
```

[![](https://blog.scrt.ch/wp-content/uploads/2020/07/messagebox_ast-1024x228.jpg)](https://blog.scrt.ch/wp-content/uploads/2020/07/messagebox_ast.jpg) Clang Abstract Syntax Tree for a simple application that calls the API MessageBoxA.

Locating function calls in source code basically amounts to finding AST nodes of type [CallExpr](https://clang.llvm.org/doxygen/classclang_1_1CallExpr.html). As pictured on the screenshot above, the function name that is actually called is specified in one of its child nodes, so it should be possible to access it later on.

### Locate function calls for a given API

[ASTMatcher](https://clang.llvm.org/docs/LibASTMatchersReference.html) is just what we need in order to enumerate every function call to a given function. First, it is important to get the syntax right for this matcher, since it is a bit more complicated that the one used in the previous blog post. To get it right, I relied on `clang-query`, which is an invaluable interactive tool that allows to run custom queries on source code. Interestingly, it is also based on `libTooling` and is much more powerful than what is showcased in this blog post (see \[ [2](https://devblogs.microsoft.com/cppblog/exploring-clang-tooling-part-2-examining-the-clang-ast-with-clang-query/)\]).

```
clang-query> match callExpr(callee(functionDecl(hasName("MessageBoxA"))))

Match #1:

/Users/vladimir/dev/scrt/avcleaner/test/messagebox_simple.c:6:5: note: "root" binds here
    MessageBoxA(NULL, "Test", "Something", MB_OK);
    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1 match.
clang-query>
```

Trial-and-error and tab completion suffice to converge quickly to a working solution. Now that the matcher is proven to work well, we can create a new [ASTConsumer](https://clang.llvm.org/doxygen/classclang_1_1ASTConsumer.html) just like we did in the previous blog post. Basically, its job is to reproduce what we did with _clang-query_, but in C++:

```
class ApiCallConsumer : public clang::ASTConsumer {
public:

    ApiCallConsumer(std::string ApiName, std::string TypeDef, std::string Library)
            : _ApiName(std::move(ApiName)), _TypeDef(std::move(TypeDef)), _Library(std::move(Library)) {}

    void HandleTranslationUnit(clang::ASTContext &Context) override {

        using namespace clang::ast_matchers;
        using namespace AVObfuscator;

        llvm::outs() << "[ApiCallObfuscation] Registering ASTMatcher for " << _ApiName << "\n";
        MatchFinder Finder;
        ApiMatchHandler Handler(&ASTRewriter, _ApiName, _TypeDef, _Library);

        const auto Matcher = callExpr(callee(functionDecl(hasName(_ApiName)))).bind("callExpr");

        Finder.addMatcher(Matcher, &Handler);
        Finder.matchAST(Context);
    }

private:
    std::string _ApiName;
    std::string _TypeDef;
    std::string _Library;
};
```

An implementation detail that we found important was to offer the possibility to match many different functions, and since the end game is to insert `LoadLibrary` / `GetProcAddress` for each replaced API function, we need to be able to supply the DLL name along the function prototype.

Doing so allows to elegantly register as many [ASTConsumers](https://clang.llvm.org/doxygen/classclang_1_1ASTConsumer.html) as there are API to replace. Instantiation of this [ASTConsumer](https://clang.llvm.org/doxygen/classclang_1_1ASTConsumer.html) must be done in the `ASTFrontendAction`:

[![](https://blog.scrt.ch/wp-content/uploads/2020/07/diff_frontend-1024x257.png)](https://blog.scrt.ch/wp-content/uploads/2020/07/diff_frontend.png) Minor modifications of main.cpp.

This is the only modification required on the existing code that we did in the previous blog post. From there, everything else can be realised as a bunch of code that we will add, starting with the creation of `ApiMatchHandler.cpp`.

The matcher must be provided with a callback function, so let us give it one:

```
void ApiMatchHandler::run(const MatchResult &Result) {

    llvm::outs() << "Found " << _ApiName << "\n";

    const auto *CallExpression = Result.Nodes.getNodeAs<clang::CallExpr>("callExpr");
    handleCallExpr(CallExpression, Result.Context);
}
```

The task broken down as a list of steps in the beginning of the section can be transposed in code, for instance with the following methods:

```
bool handleCallExpr(const clang::CallExpr *CallExpression, clang::ASTContext *const pContext);

bool replaceIdentifier(const clang::CallExpr *CallExpression, const std::string &ApiName,
                        const std::string &NewIdentifier);
bool
addGetProcAddress(const clang::CallExpr *pCallExpression, clang::ASTContext *const pContext,
                    const std::string &NewIdentifier, std::string &ApiName);

clang::SourceRange findInjectionSpot(clang::ASTContext *const Context, clang::ast_type_traits::DynTypedNode Parent,
                                        const clang::CallExpr &Literal, uint64_t Iterations);
```

### Replace function calls

This is the most trivial part. The goal is to replace “MessageBoxA” in the AST with a random identifier. Initialisation of this random variable is done in the subsequent section.

```
bool ApiMatchHandler::handleCallExpr(const CallExpr *CallExpression, clang::ASTContext *const pContext) {

    // generate a random variable name
    std::string Replacement = Utils::translateStringToIdentifier(_ApiName);

    // inject Run-time dynamic linking
    if (!addGetProcAddress(CallExpression, pContext, Replacement, _ApiName))
        return false;

    // MessageBoxA -> random identifier generated above
    return replaceIdentifier(CallExpression, _ApiName, Replacement);
}
```

The [ReplaceText](https://clang.llvm.org/doxygen/Rewriter_8h_source.html#l00164) Clang AP is used to rename the function identifier:

```
bool ApiMatchHandler::replaceIdentifier(const CallExpr *CallExpression, const std::string &ApiName,
                                        const std::string &NewIdentifier) {
    return this->ASTRewriter->ReplaceText(CallExpression->getBeginLoc(), ApiName.length(), NewIdentifier);
}
```

### **Insert LoadLibrary / GetProcAddress**

Injecting Run-time dynamic linking for the API that we would like to add is a multi-step process:

- Insert the API prototype, either at the top of the translation unit or in the enclosing function. To keep it simple, we opt for the latter, but we need to ensure that it was not already added in case the API is called several times in the same function, which would happen if there are subsequent calls to the same API.
- Insert the line `HANDLE <random identifier> LoadLibrary(<library name>);`
- Insert the call to `GetProcAddress`.

Of course, to avoid inserting obvious string literals while doing this, each string must be written as a stack string instead. This makes the code a bit tedious to read but nothing too complex:

```
bool ApiMatchHandler::addGetProcAddress(const clang::CallExpr *pCallExpression, clang::ASTContext *const pContext,
                                        const std::string &NewIdentifier, std::string &ApiName) {

    SourceRange EnclosingFunctionRange = findInjectionSpot(pContext, clang::ast_type_traits::DynTypedNode(),
                                                           *pCallExpression, 0);

    std::stringstream Result;

    // add function prototype if not already added
    if(std::find(TypedefAdded.begin(), TypedefAdded.end(), pCallExpression->getDirectCallee()) == TypedefAdded.end()) {

        Result << "\t" << _TypeDef << "\n";
    }

    // add LoadLibrary with obfuscated strings
    std::string LoadLibraryVariable = Utils::translateStringToIdentifier(_Library);
    std::string LoadLibraryString = Utils::generateVariableDeclaration(LoadLibraryVariable, _Library);
    std::string LoadLibraryHandleIdentifier = Utils::translateStringToIdentifier("hHandle_"+_Library);
    Result << "\t" << LoadLibraryString << std::endl;
    Result << "\tHANDLE " << LoadLibraryHandleIdentifier << " = LoadLibrary(" << LoadLibraryVariable << ");\n";

    // add GetProcAddress with obfuscated string: TypeDef NewIdentifier = (TypeDef) GetProcAddress(handleIdentifier, ApiName)
    std::string ApiNameIdentifier = Utils::translateStringToIdentifier(ApiName);
    std::string ApiNameDecl = Utils::generateVariableDeclaration(ApiNameIdentifier, ApiName);
    Result << "\t" << ApiNameDecl << "\n";
    Result << "\t_ "<< ApiName << " " << NewIdentifier << " = (_" << ApiName << ") GetProcAddress("
           << LoadLibraryHandleIdentifier << ", " << ApiNameIdentifier << ");\n";

    TypedefAdded.push_back(pCallExpression->getDirectCallee());

    // add everything at the beginning of the function.
    return !(ASTRewriter->InsertText(EnclosingFunctionRange.getBegin(), Result.str()));
}
```

### Test

```
git clone https://github.com/scrt/avcleaner
mkdir avcleaner/CMakeBuild && cd avcleaner/CMakeBuild
cmake ..
make
cd ..
```

To test that everything works as expected, the following test file is used:

```
#include <Windows.h>

int main(int argc, char** argv) {

    MessageBoxA(NULL, "Test", "Something", MB_OK);
    MessageBoxA(NULL, "Another test", "Another something", MB_OK);
    return 0;
}
```

Run the obfuscator:

```
./CMakeBuild/avcleaner.bin test/messagebox_simple.c --strings=true --api=true -- -D _WIN64 -D _UNICODE -D UNICODE -D _WINSOCK_DEPRECATED_NO_WARNINGS\
 -I /usr/local/Cellar/llvm/9.0.1\
 -I /Users/vladimir/dev/scrt/avcleaner/Include/msvc-14.15.26726-include\
 -I /Users/vladimir/dev/scrt/avcleaner/Include/10.0.17134.0/ucrt\
 -I /Users/vladimir/dev/scrt/avcleaner/Include/10.0.17134.0/shared\
 -I /Users/vladimir/dev/scrt/avcleaner/Include/10.0.17134.0/um\
 -I /Users/vladimir/dev/scrt/avcleaner/Include/10.0.17134.0/winrt -w -fdebug-compilation-dir -fno-use-cxa-atexit -fms-extensions -fms-compatibility -fms-compatibility-version=19.15.26726 -std=c++14 -fdelayed-template-parsing -fobjc-runtime=gcc -fcxx-exceptions -fexceptions -fdiagnostics-show-option -fcolor-diagnostics -x c++ -ferror-limit=1900 -target x86_64-pc-windows-msvc19.15.26726 -fsyntax-only -disable-free -disable-llvm-verifier -discard-value-names -dwarf-column-info -debugger-tuning=gdb -momit-leaf-frame-pointer -v
```

Inspect the result:

```
#include <Windows.h>

int main(int argc, char** argv) {

	const char  hid_Someth_lNGj92poubUG[] = {'\x53','\x6f','\x6d','\x65','\x74','\x68','\x69','\x6e','\x67',0};

	const char  hid_Anothe_UP7KUo4Sa8LC[] = {'\x41','\x6e','\x6f','\x74','\x68','\x65','\x72','\x20','\x74','\x65','\x73','\x74',0};

	const char  hid_Anothe_ACsNhmIcS1tA[] = {'\x41','\x6e','\x6f','\x74','\x68','\x65','\x72','\x20','\x73','\x6f','\x6d','\x65','\x74','\x68','\x69','\x6e','\x67',0};
	typedef int (*_MessageBoxA)(HWND hWnd, LPCTSTR lpText, LPCTSTR lpCaption, UINT uType);
	TCHAR hid_User___Bhk5rL2239Kc[] = {'\x55','\x73','\x65','\x72','\x33','\x32','\x2e','\x64','\x6c','\x6c',0};

	HANDLE hid_hHandl_PFP2JD4HjR8w = LoadLibrary(hid_User___Bhk5rL2239Kc);
	TCHAR hid_Messag_drqxgJLSrxfT[] = {'\x4d','\x65','\x73','\x73','\x61','\x67','\x65','\x42','\x6f','\x78','\x41',0};

	_MessageBoxA hid_Messag_1W70P1kc8OJv = (_MessageBoxA) GetProcAddress(hid_hHandl_PFP2JD4HjR8w, hid_Messag_drqxgJLSrxfT);
	TCHAR hid_User___EMmJBb201EuJ[] = {'\x55','\x73','\x65','\x72','\x33','\x32','\x2e','\x64','\x6c','\x6c',0};

	HANDLE hid_hHandl_vU1riOrVWM8g = LoadLibrary(hid_User___EMmJBb201EuJ);
	TCHAR hid_Messag_GoaJMFscXsdw[] = {'\x4d','\x65','\x73','\x73','\x61','\x67','\x65','\x42','\x6f','\x78','\x41',0};

	_MessageBoxA hid_Messag_6nzSLR0dttUn = (_MessageBoxA) GetProcAddress(hid_hHandl_vU1riOrVWM8g, hid_Messag_GoaJMFscXsdw);
hid_Messag_1W70P1kc8OJv(NULL, "Test", hid_Someth_lNGj92poubUG, MB_OK);
    hid_Messag_6nzSLR0dttUn(NULL, hid_Anothe_UP7KUo4Sa8LC, hid_Anothe_ACsNhmIcS1tA, MB_OK);
    return 0;
}
```

As you can see, the combination of both the string obfuscation and API obfuscation passes are quite powerful. The string “Test” was left out because we decided to ignore small strings. Then, the obfuscated source code can be built:

```
$ cp test/messagebox_simple.c.patch /tmp/test.c
$ x86_64-w64-mingw32-gcc /tmp/test.c -o /tmp/toto.exe
```

Testing on a Windows 10 virtual machine showed that the original features were kept functional. More importantly, there are no “MessageBox” strings in the obfuscated binary:

```
$ rabin2 -zz /tmp/toto.exe | grep MessageBox | wc -l
  0
```

### Generalisation

With regard to the antivirus ESET Nod32, we discovered that it was important to hide API imports related to _samlib.dll_, especially the APIs in the list below:

- SamConnect
- SamConnectWithCreds
- SamEnumerateDomainsInSamServer
- SamLookupDomainInSamServer
- SamOpenDomain
- SamOpenUser
- SamOpenGroup
- SamOpenAlias
- SamQueryInformationUser
- SamSetInformationUser
- SamiChangePasswordUser
- SamGetGroupsForUser
- SamGetAliasMembership
- SamGetMembersInGroup
- SamGetMembersInAlias
- SamEnumerateUsersInDomain
- SamEnumerateGroupsInDomain
- SamEnumerateAliasesInDomain
- SamLookupNamesInDomain
- SamLookupIdsInDomain
- SamRidToSid
- SamCloseHandle
- SamFreeMemory

These functions are not black-listed anywhere in the AV engine as far as we could tell, but they do somehow increase the internal detection confidence score. So, we must register an `ApiCallConsumer` for each of these functions, which means that we need their names and their function prototypes:

```
static std::map<std::string, std::string> ApiToHide_samlib = {
    {"SamConnect",                     "typedef NTSTATUS (__stdcall* _SamEnumerateDomainsInSamServer)(SAMPR_HANDLE ServerHandle, DWORD * EnumerationContext, PSAMPR_RID_ENUMERATION* Buffer, DWORD PreferedMaximumLength,DWORD * CountReturned);"},
    {"SamConnectWithCreds",            "typedef NTSTATUS(__stdcall* _SamConnect)(PUNICODE_STRING ServerName, SAMPR_HANDLE * ServerHandle, ACCESS_MASK DesiredAccess, BOOLEAN Trusted);"},
    {"SamEnumerateDomainsInSamServer", "typedef NTSTATUS(__stdcall* _SamConnectWithCreds)(PUNICODE_STRING ServerName, SAMPR_HANDLE * ServerHandle, ACCESS_MASK DesiredAccess, LSA_OBJECT_ATTRIBUTES * ObjectAttributes, RPC_AUTH_IDENTITY_HANDLE AuthIdentity, PWSTR ServerPrincName, ULONG * unk0);"},
    ...
}
```

And then, we update _main.cpp_ to iterate over this collection and handle each one:

```
for(auto const& el: ApiToHide_samlib){

    auto Cons = std::make_unique<ApiCallConsumer*>(new ApiCallConsumer(el.first, el.second,
                                                                        "samlib.dll"));
    consumers.push_back(*Cons);
}
```

Here, `std::make_unique` is invaluable because it allows us to instantiate objects on the heap in this loop, while sparing us the effort to manually free those objects later on. They will be freed automatically when they are no longer used.

Finally, we can battle test the obfuscator against `mimikatz`, especially [kuhl\_m\_lsadump.c](https://github.com/rapid7/mimikatz/blob/bc5d9947f58838a3d3446d1c8d42031c1d386ee1/mimikatz/modules/kuhl_m_lsadump.c):

```
bash run_example_mimikatz.sh test/kuhl_m_lsadump.c
```

This produce an interesting result:

[![](https://blog.scrt.ch/wp-content/uploads/2020/07/lsadump2-1024x617.jpg)](https://blog.scrt.ch/wp-content/uploads/2020/07/lsadump2.jpg) Run-time dynamic linking for API imported from samlib.dll

Actual function calls are correctly replaced:

[![](https://blog.scrt.ch/wp-content/uploads/2020/07/lsadump1-1024x617.jpg)](https://blog.scrt.ch/wp-content/uploads/2020/07/lsadump1.jpg) Function calls imported from samlib.dll are correctly replaced.

The strings inside the macro “PRINT\_ERROR” were left out because we noped out this macro with a `do{}while(0)`. As a side note, we did not find a better project to find bugs in the obfuscator than `mimikatz`. The code style is indeed quite exotic 🙂 .

# Improvements

Here are some exercices left to the reader 🙂

## More stealth

You don’t actually need the API `LoadLibrary` / `GetProcAddress` to perform run-time dynamic linking.

It is best to reimplement these functions to avoid hooks, and there already are open-source projects that allow you to do that ( [ReflectiveDLLInjection](https://github.com/rapid7/ReflectiveDLLInjection/)).

If you managed to read this far, you know that you only have to inject an implementation for these functions at the top of the translation unit (with `findInjectionSpot`) and update the method `addGetProcAddress` to use your implementation instead of the `WinAPI`.

## Error handling

- `LoadLibrary` returns `NULL` in case it was not successful, so it is possible to add a check for this and gracefully recover from this error. In the current situation, the application may very well crash.
- `GetProcAddress` also returns `NULL` in case of errors and it is important to check for this as well.

# Conclusion

In this blog post, we showed how it is possible to accurately replace function calls in C/C++ code-bases without using regexes. All of that was realised to prevent antivirus software to statically collect behaviour information about Meterpreter or other software that we use during our pentesting engagements.

Applied to ESET Nod32, this was a key step to allow every Meterpreter modules to go through its net undetected, and was definitely helpful for the more advanced products.

Hiding API imports is one thing, but once the malware executes, there are ways for a security software to gather behavioural information by monitoring API calls.

In view of that, the next blog post will be about automated refactoring of suspicious Win32 APIs to direct syscalls. This is another key step to circumvent run-time detection realised with userland hooks for AV such as Cylance, Traps and Kaspersky.

# References

\[1\] The Rootkit Arsenal, Chapter 11, p.480.

\[2\] [https://devblogs.microsoft.com/cppblog/exploring-clang-tooling-part-2-examining-the-clang-ast-with-clang-query/](https://devblogs.microsoft.com/cppblog/exploring-clang-tooling-part-2-examining-the-clang-ast-with-clang-query/)

_Vladimir Meier_

…

…

…

…

…

…

…