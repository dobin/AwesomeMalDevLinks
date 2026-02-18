# https://fluxsec.red/monitoring-ntdll-for-memory-patching-etw-hacking-bypass-in-rust-EDR

# Monitoring NTDLL for in memory patching

Naa na na na, cant touch this

* * *

## Intro

The code for this can be found on GitHub: [Sanctum](https://github.com/0xflux/Sanctum). If you like this, please show support by giving it a star, it keeps me motivated!

So, I wanted to do something that turns away from the syscall hooking for my EDR, but still on the same lines. I decided it’s time to check for in-memory patching that
malware likes to do, as one evasion technique.

In fact (future me writing here) - sometime after writing this blog post and code; I came across a C program by Mr-Un1k0d3r in their RedTeamCCode repository,
a file called [unhook\_crowdstrike\_64.c](https://github.com/Mr-Un1k0d3r/RedTeamCCode/blob/main/unhook_crowdstrike_64.c), after
reading through that - this addition to my EDR would detect this alleged CrowdStrike unhooking technique if applied to my EDR :).

An example of this, is Event Tracing for Windows patching - for more info check my blog posts:

- [Writing malware that performs ETW patching](https://fluxsec.red/etw-patching-rust)
- [Subscribing to un-patchable (from usermode) ETW: Threat Intelligence](https://fluxsec.red/event-tracing-for-windows-threat-intelligence-rust-consumer)

Whilst we are using ETW patching as an example; this technique applies to any patching of NTDLL (or any other DLL for that fact!).

What we are looking to do in short is read a given module (in this case, NTDLL), and calculate a hash. We can then periodically check that module for changes by
recomputing the hash. To achieve this, we will put the loop checking the hash in its own OS thread so it doesn’t interfere with the operation of the program.

## Fundamentals

Okay - before we get started I wanted to quickly cover some fundamentals of PE (Portable Executable) headers.

Every executable, and DLL has a particular set of structures at the start of the binary which you may have seen before, commonly you will see things at the start of
a binary like:

- MZ
- This program cannot be run in DOS mode

When opening a binary (exe or DLL) in a hex editor, you can see this as follows:

![Windows PE DOS Header](https://fluxsec.red/static/images/dos_header.png)

What is this? Well, Windows requires certain sections of metadata which essentially describe how the binary file is laid out and pointers to where key things are, such
as the address of the entrypoint function (commonly (but not always) `main()`).

Given we want to hash the module NTDLL to detect changes, we have a few objectives we need to achieve:

1. Find the .text section containing the actual code of NTDLL we want to hash.
2. Find the length of that section, so we know how many bytes we want to read.

The **.text** section of a binary is the executable section where the code lives - ordinarily this section is read only; however malware can edit the **.text** section so that
the code no longer does what the original author intended (such as our [ETW patching](https://fluxsec.red/etw-patching-rust) techniques).

A key concept at this stage is the difference between a Virtual Address and a Relative Virtual Address. To explain this simply: the **virtual address** is the address of ‘something’ (aka
a function, variable) in the memory the process has been allocated - this does not map directly to a physical address in RAM. The virtual address space is for use by the program. The
**relative virtual address** is an offset to ‘something’ from the base address (virtual address) of the module.

## Finding the text section

To tackle the first objective, we can find the .text section through some traversing of the PE headers. The ‘base’ of the **.text** section can be found at the **relative** virtual address
found by looking in the [OptionalHeader](https://learn.microsoft.com/en-gb/windows/win32/api/winnt/ns-winnt-image_optional_header32?redirectedfrom=MSDN) at the field **BaseOfCode**.

Looking at the list of fields, you may want to think the field **SizeOfCode** relates to the size of the .text section in memory. Which is what I thought; however when building this I found that
there was a discrepancy between this and the **.text** section in memory; and what more, it was larger than the size of the DLL on disk - so this can’t be right? The Windows API defines this as:

The size of the code section, in bytes, or the sum of all such sections if there are multiple code sections.

Which, sounds right? However, I found this NOT to be what we want.

So, instead we can use the **VirtualSize** field on a [IMAGE\_SECTION\_HEADER](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_section_header). As we said before,
the **.text** section is where the (or some of) executable code lives. There are any number of other sections; such as for storing read only data and other things. Each of these sections has
a header (as part of the PE headers discussed above). In this header, is a field **VirtualSize** which is defined by microsoft as:

The total size of the section when loaded into memory, in bytes. If this value is greater than the SizeOfRawData member, the section is filled with zeroes.
This field is valid only for executable images and should be set to 0 for object files.

So, armed with this information, we can write some code with a little pointer arithmetic (and relative addressing adjustments) to get what we need! Before we do, let’s have a look at the
output. The image below shows:

- The green box is the calculated base address of the **.text** section
- The blue box & line is the size of the **.text** section (note that the blue box represents the size as an integer, not as hex, I calculated this in hex to do the math in calc)
- The red box & line is the end of the **.text** section, which you can see when you do the math in the calculator, works out to the end of our **.text** section.

![Looking at .text section in a PE Portable Executable](https://fluxsec.red/static/images/size_of_txt.png)

For monitoring NTDLL, we need a struct to hold the data so we can easily compare & hash without having the CPU do all these calculations each iteration. We will hold them in the following:

```rust
/// The core mappings of NTDLL so that it can be monitored for changes via a hash value
struct NtdllIntegrity {
    /// The base address (VA) of the .text segment
    text_base: usize,
    /// The size in memory of the .text segment
    size: usize,
    hash: String,
}
```

And now the code to get the base address & size. The below code does:

1. We get a handle to NTDLL in memory which in turn will give us its base address (Virtual Address).
2. Check the DOS signature is correct so we don’t read corrupted / misaligned / invalid memory.
3. Read the **OptionalHeader** to get the **BaseOfCode** using some pointer arithmetic.
4. Enumerate all section headers, looking for the **.text** section. When found - get its size.
5. Check the size isn’t 0, and return the nwo instantiated struct.

```rust
impl NtdllIntegrity {
    fn new() -> Self {
        // `module` will contain the base address of the DLL
        let module = unsafe { GetModuleHandleA(s!("ntdll.dll")) }.expect("[-] Could not get a handle to NTDLL");

        //
        // Resolve the Virtual Address address & size of the .text section
        //
        let dos_header = unsafe { std::ptr::read(module.0 as *const IMAGE_DOS_HEADER) };
        if dos_header.e_magic != IMAGE_DOS_SIGNATURE {
            panic!("[-] Bytes of NTDLL did not match DOS signature.");
        }

        let mut size_of_text_sec: u32 = 0;
        let headers = unsafe { std::ptr::read(module.0.add(dos_header.e_lfanew as _) as *const IMAGE_NT_HEADERS64) };

        // Get the virtual address of the .text segment
        let base_of_code_offset = headers.OptionalHeader.BaseOfCode as usize;
        let base_of_code = (module.0 as usize + base_of_code_offset) as *const c_void;

        // Look for the .text section to get the size of the section in bytes
        for i in 0..headers.FileHeader.NumberOfSections {
            let section_header = unsafe { std::ptr::read(module.0
                .add(dos_header.e_lfanew as _)
                .add(size_of_val(&headers))
                .add(i as usize * size_of::<IMAGE_SECTION_HEADER>())
            as *const IMAGE_SECTION_HEADER) };

            let name = unsafe { CStr::from_ptr(section_header.Name.as_ptr() as *const _) }.to_str().expect("[-] Could not parse name to str");
            if name == ".text" {
                // SAFETY: Reading union field on documented & MSFT provided field as part of PE structure, should be fine
                size_of_text_sec = unsafe { section_header.Misc.VirtualSize };
                break;
            }
        }

        assert_ne!(size_of_text_sec, 0);

        Self {
            text_base: base_of_code as usize,
            size: size_of_text_sec as _,
            hash: String::new(),
        }
    }
}
```

## Reading the text section

Now we have the addresses in place, we can read the bytes of the **.text** section into a buffer. **Note:** I am reading this into a vector, which is
heap allocated, the size of the **.text** section. This is bad practice for how we want to approach this, but as its a POC I don’t mind this for now,
and I will refactor it later. The reason this is bad is if we were to load the EDR’s DLL into every process at once, we would read:

num of processes \* size in bytes of NTDLL

Into the heap of **each** process, which may (depending on how much RAM you have), crash your system. NTDLL is fairly small, so it would most likely be ok.
But lets say we were reading arbitrary DLLs in, this could be a problem.

The approach below is also somewhat efficient by using [Vec::with\_capacity](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.with_capacity), which
shouldn’t write 0’s to the buffer before it is used.

We simply step through the memory by adding an offset to where we are reading ( **pos**) to the ‘base’ address of the **.text** section for n bytes where n
is the size.

And, before we look at the code, seeing it in action - you can see the last few bytes in the buffer printed on the right, and the representative bytes in the
debugger on the left.

![Read bytes in NTDLL](https://fluxsec.red/static/images/read_end_bytes.png)

```rust
/// Get a hash of NTDLL in its entirety, and save the state of this for future lookups.
fn read_ntdll_bytes(ntdll_info: &NtdllIntegrity) -> Vec<u8> {
    // The position we are indexing into, using the size of the image as a ceiling
    let mut pos = 0;
    // Buffer to store the bytes for hashing
    // todo may want to read into a stack / small heap buffer to preserve system resources if all processes do this
    let mut buf: Vec<u8> = Vec::with_capacity(ntdll_info.size);
    while pos < ntdll_info.size {
        // SAFETY: This read should be safe so long as NTDLL remains mapped in memory. Should NTDLL be remapped or removed
        // then this will lead to UB.
        buf.push(unsafe { std::ptr::read((ntdll_info.text_base as *const c_void).add(pos as _) as *const _) });
        pos += 1;
    }

    assert_eq!(buf.len(), ntdll_info.size as usize);

    buf
}
```

## Hashing

Finally, we can hash the buffer we got (using the **md-5** crate):

```rust
fn hash_ntdll_text_segment(ntdll_info: &NtdllIntegrity) -> String {
    // Read the bytes
    let buf = read_ntdll_bytes(&ntdll_info);

    // Calculate the hash
    let mut hasher = Md5::new();
    hasher.update(buf);
    let hash = hasher.finalize();
    let hash: String = hash.iter().map(|byte| format!("{:02X}", byte)).collect();
    hash
}
```

## Continuous monitoring

The objective of this of course, is to continuously monitor for any malware modifying NTDLL - so as we said above, we want to run this in its own OS thread
so that we do not interfere with the functionality of the main program. We use 1 second as an example, but this can be any arbitrary unit of time you wish.

So, lets spawn a thread and loop, looking for a change in the calculated hash:

```rust
/// The entrypoint to starting the NTDLL integrity checker. This will spawn a new OS thread which will occasionally monitor the
/// integrity of NTDLL to check for changes to the .text segment of NTDLL in memory. Once we have hooked the DLL there should be no
/// reason for this to be further modified.
///
/// This function **must** be called after the EDR DLL has hooked API's and before all threads are resumed.
pub fn start_ntdll_integrity_monitor() {
    let mut ntdll_info = NtdllIntegrity::new();

    let hash = hash_ntdll_text_segment(&ntdll_info);
    ntdll_info.hash = hash;

    let _ = std::thread::spawn(|| {
        periodically_check_ntdll_hash(ntdll_info);
    });
}

fn periodically_check_ntdll_hash(ntdll: NtdllIntegrity) -> ! {
    loop {

        let hash = hash_ntdll_text_segment(&ntdll);
        if hash != ntdll.hash {
            println!("HASH CHANGE DETECTED. Old: {}, New: {}", ntdll.hash, hash);
        }

        std::thread::sleep(Duration::from_secs(1));
    }
}
```

## Making our malware patch ETW

Finally, we need to make our malware patch Event Tracing for Windows as I describe in [my blog post here](https://fluxsec.red/etw-patching-rust).

I have modified the test malware we are using in the EDR project ( [link](https://github.com/0xflux/Sanctum/tree/main/malware)) to patch ETW to try blind
any EDR before it does the bad things. When we run the malware, with the ETW patch, it is detected as follows:

![Read bytes in NTDLL](https://fluxsec.red/static/images/patch_detected.png)

## Next steps

To bring this to life - this detection should:

1. Signal the EDR via a named pipe that memory modification has taken place for it to suspend the process / kill the process, etc.
2. Re-hash NTDLL after the modification was made (in case the user allows it? Or some other logic?).
3. Alert the user (not yet implemented).

Finally; this technique won’t catch really sophisticated threats which could do some runtime hot-patching. If an implant patches memory such that it disables
user-mode ETW when it runs, then reverts it before it sleeps, we would be reliant upon a collision between our in-memory scan vs the malware being ‘awake’ and
using the patched memory for it to be detected.

We could take this further by monitoring `NtWriteVirtualMemory` calls and looking at the address that is being written to - but if memory is altered via the C Runtime
(aka how Rust also implements raw memory writes) we can first look for a change of protection via **VirtualProtect** \- if the **.text** section is being altered to be
writeable, then we can flat out block it and report.

In fact - doing that, may even make this monitoring unnecessary :). I hope you enjoyed this post! Don’t forget to [star my project](https://github.com/0xflux/Sanctum/) if you liked it!