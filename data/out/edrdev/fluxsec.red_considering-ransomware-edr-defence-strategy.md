# https://fluxsec.red/considering-ransomware-edr-defence-strategy

# Real-time Ransomware Detection Strategy

Theorycrafting about live ransomware detection

* * *

## Intro

You can check this project out on [GitHub](https://github.com/0xflux/Sanctum)!

Moving onto something a little different once more for my EDR, Ransomware! Probably, the most notable word in cybersecurity, and certainly something
a lot of new maldevs strive to achieve.

Ransomware itself is simple. Walk the OS (all drives), and overwrite the bytes in each file with an encrypted version of the bytes. Normally, this would
be asymmetric encryption to make the victims life hard. Ransomware evolved somewhat a few years ago with new strategies for faster encryption,
instead of encrypting each byte, encrypt every other byte, or one out of every three, for example.

This work is going to have to wait until my [Pull Request](https://github.com/microsoft/windows-drivers-rs/pull/337) is merged into the main branch of the [windows-drivers-rs](https://github.com/microsoft/windows-drivers-rs) project by Microsoft, the filesystem APIs are not currently exposed via bindgen in the **wdk**, so my PR brings these in. I'm really excited to fully contribute to the windows-drivers-rs project!

## Approach

I have drawn a diagram below just putting my brain on the page; hopefully this accompanying text helps explain my terrible hand-art skills! Ransomware must
walk the filesystem, encrypting each file that it comes across.

The Sanctum [driver](https://github.com/0xflux/Sanctum/tree/main/driver) can act as a minifilter intercepting filesystem I/O requests; if we notice one process is modifying the bytes of a number of files, and its
extension (though this should not be a core detection strategy, what if the ransomware doesn’t change the extension for example), then we should trigger the
response process. Furthermore, modification of the files header / magic bytes would also be irregular for normal end-user file operations; so should be considered
a red flag.

The response element, we will want to:

1. Freeze the process.
2. Perform a memory dump to allow post-incident forensics to try extract any keys from the process, and to allow reverse engineers to understand the ransomware, trying to identify any weaknesses in its implementation.
3. Terminate the process & signal an alert to the telemetry server.

A fun thought; if ransomware is detected on an endpoint - could the server notify all other connected agents to lock them down somehow? Perhaps sending the signature, filename, or commandline arguments of the ransomware
so that agents can perform an urgent scan of the device for that file and ensure processes starting containing any of that metadata are terminated before they can start.

Fun thoughts! Anyway, here is the diagram in question:

![Ransomware theory EDR defence](https://fluxsec.red/static/images/ransomware_theory.jpg)

## Challenges

Some challenges I see with detecting ransomware:

1. Malware designed to kill the EDR will potentially leave a gap for it to successfully operate, for now this is out of scope.
2. Differentiating ransomware vs on-the-fly encryption / other legitimate encryption software.

## Next steps

Now that I’ve set out my approach for building ransomware detection into the EDR; it’s time to play with some minifilter drivers
and some mock ransomware samples I’ll write to determine how the minifilters interpret file encryption - for example writing a single
entire blob to the file vs file-streams, do these look different?

Once the experiments are done to baseline what data ‘passes through’ the minifilter with different approaches to ransomware, it may be worth
doing the same with an on-the-fly encryption (otfe) program, such as Veracrypt, to see what that looks like.

I suspect that the challenges of differentiating between otfe and ransomware will be fairly simple - although there will be a lot of encrypting
and decrypting going on with the otfe software, it shouldn’t bulk walk the filesystem during normal operation (except for the first pass of encryption).
Therefore, we should be able to say if an I/O walk is in progress by a process, and certainly the file signature is being overwritten, then we should
treat it as ransomware. If a real user wanted to apply full disk encryption, then I suppose they would be doing that before the EDR is in action, or
simply turn it off whilst doing the encryption set up.

The next post will outline the results of testing the minifilter; and hopefully after that, outlining some success with trying to detect
live time ransomware!