# https://medium.com/@toneillcodes/the-single-primitive-write-writeprocessmemorys-hidden-page-flip-e5cb952bbfb2

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40toneillcodes%2Fthe-single-primitive-write-writeprocessmemorys-hidden-page-flip-e5cb952bbfb2&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=---top_nav_layout_nav-----------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40toneillcodes%2Fthe-single-primitive-write-writeprocessmemorys-hidden-page-flip-e5cb952bbfb2&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Cybersecurity

Windows Internals

Ethical Hacking

Malware

Windows

# The Single-Primitive Write: WriteProcessMemory’s Hidden Page Flip

## Documenting Undocumented WriteProcessMemory Behavior

[![Tom O'Neill](https://miro.medium.com/v2/resize:fill:32:32/1*csbZCQnf74EEf36Ulms2sw.png)](https://medium.com/@toneillcodes?source=post_page---byline--e5cb952bbfb2---------------------------------------)

[Tom O'Neill](https://medium.com/@toneillcodes?source=post_page---byline--e5cb952bbfb2---------------------------------------)

Follow

4 min read

·

Jun 21, 2026

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3De5cb952bbfb2&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40toneillcodes%2Fthe-single-primitive-write-writeprocessmemorys-hidden-page-flip-e5cb952bbfb2&source=---header_actions--e5cb952bbfb2---------------------post_audio_button------------------)

Share

In offensive Windows tradecraft, we are taught to treat memory protections as absolute boundaries. When developing local loaders or manipulating memory regions, we meticulously track page states. If we need to modify a region that is currently marked as read-only (`PAGE_READONLY`) or execute-read (`PAGE_EXECUTE_READ`), our immediate reflex is to explicitly fluctuate the permissions using `VirtualProtect` or its native equivalent, `NtProtectVirtualMemory`.

We do this because documentation dictates that attempting to write directly to non-writable space will result in an access violation.

But Windows documentation often obscures kernel-mode reality. As it turns out, `WriteProcessMemory` is perfectly capable of handling the permission flip for you. By understanding the implicit behavior of the underlying API, we can avoid the need to explicitly toggle user-mode protection.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*lL5frTt7ntHvGf8BUSWG9Q.png)

## WriteProcessMemory: Under the Hood

### Automated NtProtect Toggling

The MSDN documentation for `WriteProcessMemory` (WPM) states that the function copies data into a specified process's memory space, but it stays quiet about permission management. The standard assumption is that if the page permissions don't explicitly permit writing, the API should fail.

[\[1\] MSDN: WriteProcessMemory API Documentation](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory)

In practice, the heavy lifting is passed down to `NtWriteVirtualMemory`. When the kernel services this request against a non-writable page:

- **The Kernel Intercepts:** Instead of immediately failing the operation with an access violation, the kernel verifies handle rights and checks the target page.
- **The Page Flip:** It temporarily forces the write bit on the target pages, copies the data buffer, and seamlessly restores the original protection state — **all without requiring an explicit**`VirtualProtect` **invocation from user-mode.**

As Microsoft developer Raymond Chen famously noted in _The Old New Thing_, this design choice stems from the API’s primary audience: debuggers. When a debugger needs to patch memory to set an `INT 3` breakpoint or handle edit-and-continue modifications, forcing an operator to juggle page permissions manually adds unnecessary overhead. WPM tried to be helpful by handling that transition transparently behind the scenes.

## Get Tom O'Neill’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

[\[2\] _How is it that WriteProcessMemory succeeds in writing to read-only memory?_ — Raymond Chen (The Old New Thing)](https://devblogs.microsoft.com/oldnewthing/20181206-00/?p=100415)

> _💡_ **_Architectural Note:_** _Under the hood, the kernel is essentially performing an implicit_`NtProtectVirtualMemory` _loop on your behalf. The permission modification still occurs; it is simply abstracted away from the user-mode code._

For example, consider the following test case. Allocating a region straight to `PAGE_EXECUTE_READ` and issuing a write immediately afterward is completely valid and fully functional:

### `wpm-example.cpp`

```
#include <windows.h>
#include <stdio.h>

int main() {
    // Example payload buffer
    unsigned char buf[] = "\x90\x90\x90\x90";
    HANDLE pHandle = GetCurrentProcess();
    // 1. Allocate straight to RX space. No RWX, no explicit RW transition.
    LPVOID bufferAddress = VirtualAlloc(NULL, sizeof buf, (MEM_COMMIT | MEM_RESERVE), PAGE_EXECUTE_READ);
    if (!bufferAddress) {
        printf("[ERROR] Allocation failed. Error: %lu\n", GetLastError());
        return -1;
    }
    printf("[*] Memory allocated as RX at: 0x%p\n", bufferAddress);
    // 2. The documentation implies this should fail. The kernel says otherwise.
    // NOTE: This internal permission flip is still a visible event to kernel telemetry!
    BOOL writeShellcode = WriteProcessMemory(pHandle, bufferAddress, buf, sizeof buf, NULL);
    if (!writeShellcode) {
        printf("[ERROR] Write failed. Error: %lu\n", GetLastError());
        VirtualFree(bufferAddress, 0, MEM_RELEASE);
        return -1;
    }
    printf("[+] Successfully wrote to RX memory without calling VirtualProtect.\n");
    return 0;
}
```

### Executing wpm-example.cpp

```
c:\Users\Administrator\Desktop>cl.exe wpm-example.cpp /nologo
example.cpp

c:\Users\Administrator\Desktop>

c:\Users\Administrator\Desktop>wpm-example.exe
[*] Memory allocated as RX at: 0x00000287BC670000
[+] Successfully wrote to RX memory without calling VirtualProtect.

c:\Users\Administrator\Desktop>
```

## The Operational Caveat

### The Signature Changes, The Signal Remains

To be clear: allocating a raw private memory region straight to `PAGE_EXECUTE_READ` and writing to it this way is poor OPSEC if your goal is evasion.

Leaving an unbacked, private memory region as `RX` creates a glaring memory anomaly that any mature memory scanner will catch during a routine sweep.

The value of this snippet isn’t that you should use it to stage raw payloads into private allocations. The value is what it teaches us about the underlying API’s implicit behavior.

In part two of this series, we will look at how to leverage this quirk to eliminate noise in module-stomping workflows.

## Conclusion

For offensive practitioners, understanding the delta between documented Win32 behavior and actual kernel execution allows us to strip unnecessary assumptions out of our tradecraft. While the documentation implies a rigid boundary that requires manual intervention, the reality is that the OS is designed to be helpful, executing complex, automated operations right beneath our user-mode threads.

Relying on `WriteProcessMemory` to implicitly handle permissions highlights the danger of building detections around assumed user-mode sequences. When a behavioral signature expects an explicit `VirtualProtect` call to precede a cross-process or local write, it creates a blind spot out of a documentation technicality. For defenders, this reinforces the idea that monitoring must decouple from user-mode sequence expectations and anchor itself directly to the kernel choke points where the physical memory transition actually occurs.

Now that we understand the raw mechanics of this implicit page flip, we can begin applying it to practical tradecraft. In part two of this series, we will look at how moving this exact trick away from raw allocations and toward existing file-backed memory allows us to strip the noise from precision module-stomping workflows.

## References

\[1\] MSDN: WriteProcessMemory API Documentation [https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory)

_\[2\] How is it that WriteProcessMemory succeeds in writing to read-only memory?_— Raymond Chen (The Old New Thing)

[https://devblogs.microsoft.com/oldnewthing/20181206-00/?p=100415](https://devblogs.microsoft.com/oldnewthing/20181206-00/?p=100415)

Windows Process Injection Repository

[https://github.com/toneillcodes/windows-process-injection](https://github.com/toneillcodes/windows-process-injection)

wpm-example.cpp

[https://github.com/toneillcodes/windows-process-injection/blob/main/snippets/wpm-example.cpp](https://github.com/toneillcodes/windows-process-injection/blob/main/snippets/wpm-example.cpp)

Cybersecurity

Windows Internals

Ethical Hacking

Malware

Windows

[![Tom O'Neill](https://miro.medium.com/v2/resize:fill:48:48/1*csbZCQnf74EEf36Ulms2sw.png)](https://medium.com/@toneillcodes?source=post_page---post_author_info--e5cb952bbfb2---------------------------------------)

[![Tom O'Neill](https://miro.medium.com/v2/resize:fill:64:64/1*csbZCQnf74EEf36Ulms2sw.png)](https://medium.com/@toneillcodes?source=post_page---post_author_info--e5cb952bbfb2---------------------------------------)

Follow

[**Written by Tom O'Neill**](https://medium.com/@toneillcodes?source=post_page---post_author_info--e5cb952bbfb2---------------------------------------)

[57 followers](https://medium.com/@toneillcodes/followers?source=post_page---post_author_info--e5cb952bbfb2---------------------------------------)

· [30 following](https://medium.com/@toneillcodes/following?source=post_page---post_author_info--e5cb952bbfb2---------------------------------------)

Independent Security Researcher

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----e5cb952bbfb2---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----e5cb952bbfb2---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----e5cb952bbfb2---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----e5cb952bbfb2---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----e5cb952bbfb2---------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----e5cb952bbfb2---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----e5cb952bbfb2---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----e5cb952bbfb2---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----e5cb952bbfb2---------------------------------------)