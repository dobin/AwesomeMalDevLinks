# https://www.cobaltstrike.com/blog/sleep-mask-update-in-cobalt-strike-4-5

This website uses cookies. You may change your settings at any time.

AcceptReject AllManage Cookies

Cookie Preferences

[Home](https://www.cobaltstrike.com/) » [Blog](https://www.cobaltstrike.com/blog/) » Sleep Mask Update in Cobalt Strike 4.5

# Sleep Mask Update in Cobalt Strike 4.5

Friday 17 December, 2021

The Sleep Mask Kit was first introduced in [Cobalt Strike 4.4](https://www.cobaltstrike.com/blog/cobalt-strike-4-4-the-one-with-the-reconnect-button/) to allow users to modify how the sleep mask function looks in memory in order to defeat static signatures that identified Beacon. This quickly took off in the community and its limits were pushed. Updates were [made in 4.5](https://www.cobaltstrike.com/blog/cobalt-strike-4-5-fork-run-youre-history/) to help address some of these limits.

Licensed users can download the updated kit from [https://www.cobaltstrike.com/scripts](https://www.cobaltstrike.com/scripts)

### What’s New?

#### Increased size

The size of the sleep mask executable code has been increased to 769 bytes from 289 bytes.

#### Heap Memory

A list of heap memory addresses has been added to the input to the sleep mask function. This allows for the ability to mask and unmask Beacon’s heap memory, which could be used to identify Beacon.

### Compatibility

Any sleep mask modifications for Cobalt Strike 4.4 will not be compatible with 4.5 because of the changes to the functions input. This also means the sleep mask modifications are also not backwards compatible.  Users will need to have separate sleep mask versions for 4.4 and 4.5. An updated sleep mask kit is available through the Cobalt Strike UI Help -> Arsenal page.

### Changes

- Added a new **HEAP\_RECORDS** data structure
- Added a pointer to the **HEAP\_RECORDS** data structure to the existing **SLEEPMASKP** structure
- Added new loops to mask and unmask the heap memory identified by the **HEAP\_RECORDS** structure.

### Limitations

These are the current limitations to the sleep mask kit for Cobalt Strike 4.5:

- The executable code size cannot exceed 769 bytes. If this occurs the default sleep mask function will be used.
- Only one function can be defined in the source code file.
- Use of external functions are not supported

### Example

For this example, the Sleep Mask Kit for Cobalt Strike version 4.5 with a modification to the code to only mask and unmask when the sleep is larger than two seconds will be used. This allows for the ability to control the masking and unmasking of Beacon based on the current sleep time.

Generate a Beacon using the modified sleep mask and deploy it on your target system. The Beacon is now running and has a PID value of 5400 for this example.

Using a Yara rule based on the [BeaconEye](https://github.com/CCob/BeaconEye) project, beacon will be detected. The rule shows the memory address that triggered the detection as the current sleep time is set 1 second.

![](https://www.cobaltstrike.com/app/uploads/2023/01/sleep-mask-beacon-eye-rule.png)Detected at 0x7c7290

Using Process Hacker, open the process (5400) and look at the contents of memory at the found location of 0x7c7290. This is determined by finding the base address 0x7b0000 and subtracting from 0x7c7290 to determine the offset within this block of heap memory.

![](https://www.cobaltstrike.com/app/uploads/2023/01/sleep-mask-heap-unmasked.png)Beacon’s configuration unmasked

The highlighted portion shows the signature that was used to identify Beacon, which represents Beacon’s configuration in the heap memory.

With the Cobalt Strike version 4.5 sleep mask this location in memory is provided as one of heap memory addresses in the **HEAP\_RECORDS** list. Now, update the sleep time for this beacon to three seconds so it will mask itself while sleeping and then inspect this memory location again.

![](https://www.cobaltstrike.com/app/uploads/2023/01/sleep-mask-heap-masked.png)Beacon’s Configuration masked

Comparing this to the previous screenshot shows the heap memory is now masked. Running the Yara rule again shows that it does not detect the signature for Beacon’s configuration.

![](https://www.cobaltstrike.com/app/uploads/2023/01/sleep-mask-beacon-eye-rule-2.png)

This is just one simple example of using the sleep mask to obfuscate Beacon in memory.

Enjoy!

### References

- BeaconEye [https://github.com/CCob/BeaconEye](https://github.com/CCob/BeaconEye)

![](https://www.cobaltstrike.com/app/uploads/2023/07/joe-vest-circle-outline.png)

#### [Joe Vest](https://www.cobaltstrike.com/profile/joe-vest)

[View Profile](https://www.cobaltstrike.com/profile/joe-vest)

TOPICS


- [Releases](https://www.cobaltstrike.com/blog?_sft_cornerstone=releases "Releases")