# https://www.hexacorn.com/blog/2025/08/19/dll-forwardsideloading/

[Skip to primary content](https://www.hexacorn.com/blog/2025/08/19/dll-forwardsideloading/#content)

Some DLLs export functions (via export table) that are just forwarding execution to functions implemented in other libraries. It’s a very common practice and one of the most known forwards are:

```
kernel32.dll HeapAlloc -> NTDLL.RtlAllocateHeap
kernel32.dll HeapReAlloc -> NTDLL.RtlReAllocateHeap
kernel32.dll HeapSize -> NTDLL.RtlSizeHeap
```

Now, most of us assume that lots of forwards redirect the execution to most popular Windows DLLs, and these are typically just your regular KnownDLLs: ntdll, kernelbase, ole32, etc. — ones that are on the KnownDLLs list + very often already loaded into memory.

I decided to check what forwards we can find on the Win 11 OS, because I had a cunning plan: If I can find a forward that does not redirect to KnownDlls, then I can execute an indirect DLL sideloading, one that is on par with traditional EXE sideloading technique.

Meaning?

Use a signed rundll32.exe to load a signed DLL that will then load the payload DLL of our choice… by using that exported function.

This is a [list of forwards](https://hexacorn.com/d/apis_fwd.txt) I have generated.

We can quickly identify a non-KnownDlls pair, where:

```
keyiso.dll KeyIsoSetAuditingInterface -> NCRYPTPROV.SetAuditingInterface
```

So, copying _keyiso.dll_ to c:\\test, and then placing a payload in _NCRYPTPROV.dll_ in the same folder, and then finally executing:

```
rundll32.exe c:\test\keyiso.dll, KeyIsoSetAuditingInterface
```

will load a copy of the _keyiso.dll_ first, then the function resolution of _KeyIsoSetAuditingInterface_ will resolve it first to _NCRYPTPROV.SetAuditingInterface_ forward, and then automatically load the _NCRYPTPROV.dll_, and only then execute the function’s code. In the example below, I didn’t bother to implement _SetAuditingInterface_ in the test DLL, just to showcase the execution flow leading to (actually misleading, since it refers to the outer DLL/API name combo) ‘missing API’ message box.

[![](https://www.hexacorn.com/blog/wp-content/uploads/2025/08/keyiso.png)](https://www.hexacorn.com/blog/wp-content/uploads/2025/08/keyiso.png)

The _DLLMain\_64\_DLL\_PROCESS\_ATTACH.txt_ file is created by the test payload, indicating its DllMain function has been executed.

Obviously, this technique does not need to rely on OS libraries. I am pretty sure that a bigger study of exported functions from a larger corpora of signed DLLs will yield a set of combos that can be used to implement this technique.