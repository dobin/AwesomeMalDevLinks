# https://projectblack.io/blog/bypassing-edr-with-local-ai/

Just about every enterprise environment in Australia (and likely globally) makes use of a Endpoint Detection and Response (EDR) solution as a part of their security strategy now.

As [penetration testers](https://projectblack.io/penetration-testing/), this is very annoying (I'm sure it's annoying for criminals as well). Long gone are the days of simply deleting Windows Defender AV definitions and running whatever you want. Today, privilege escalation and lateral movement in Active Directory environments often involves some sort of EDR dance.

## The Benchmark/Goal

To understand how AI can help us (and criminals) evade EDR, I set a target.

Can AI write an executable which helps us dump the LSASS (Local Security Authority Subsystem Service) process without being detected by modern EDR **with limited input from me**?

💡

As an attacker, after gaining administrative access to a Windows host, a common post exploitation step involves dumping the LSASS process. Depending on the Windows configuration, LSASS can hold plaintext passwords or password hashes.

We can then use these passwords or hashes to log into other systems thereby achieving lateral movement.

## Using Claude

Starting with Claude, trying to use it to write our LSASS dumper results in immediate refusals. This goes for Opus 5, Opus 4.8 and Sonnet 5.

![](https://projectblack.io/blog/content/images/2026/09/image-4.png)

Although the message mentions the Cyber Verification Program, my account/org is already approved into the program.

![](https://projectblack.io/blog/content/images/2026/09/image-5.png)

I gave them my ID to go through the CVP just to see that refusal. How do I unsend my ID? /s

## Turning to DeepSeek (v4 Flash 0731)

We're off to the races!

Trying the same prompt with an open weight model works immediately.

![](https://projectblack.io/blog/content/images/2026/09/image-6.png)

After a few more back and forth prompts, we have a working executable that:

- Takes a PID as input
- Uses reflection to create a suspended clone process of the target PID
- Creates an in-memory minidump of the process and XOR encrypts it
- Writes the encrypted file to disk

![](https://projectblack.io/blog/content/images/2026/09/image-8.png)

Running `pypykatz lsa minidump` we can also validate that the created dump is valid.

![](https://projectblack.io/blog/content/images/2026/09/image-10.png)

Unfortunately it currently gets detected by EDR...

Asking for extra stealth results in a guardrail being hit.

![](https://projectblack.io/blog/content/images/2026/09/image-7.png)

Rather than trying to reframe my way through this, I figured I'd try an uncensored model to see what all the fuss is about.

## Uncensored Qwen 3.8 27B

With access to some hardware (owned or rented) it's possible to run AI models that have been tweaked by the community to remove all guardrails.

This particular [version](https://huggingface.co/HauhauCS/Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-MTP-GGUF) of Qwen 3.8 27b seems very willing to do anything you ask. We're currently able to run this on our hashcat rig (2 x RTX 4090).

![](https://projectblack.io/blog/content/images/2026/09/image-9.png)The possibilities are endless.

Back on track with our project...

I then asked if it can just make our executable more stealthy without any other instructions.

![](https://projectblack.io/blog/content/images/2026/09/image-11.png)

After a lengthy wait, our new executable runs without any detections!

That was trivial.

![](https://projectblack.io/blog/content/images/2026/09/image-12.png)

There were no detections for both (2) of the EDR solutions I have access to in our lab.

![](https://projectblack.io/blog/content/images/2026/09/image.png)All green on host 1!![](https://projectblack.io/blog/content/images/2026/09/image-13.png)Only a test alert from earlier in the console on host 2.

Reviewing what changes it made, without any other input from me the uncensored model decided to apply all of the following to our executable:

- Modified process spawning to be less suspicious
- Reduced access masks on the target process
- Added some random sleeps for building the minidump
- Changed output naming/path
- Scrubbed embedded strings in the executable

## Conclusion

If you're on the [red team side](https://projectblack.io/penetration-testing/), I'd recommend that you experiment with some of these uncensored LLMs to help with custom tool development.

For defenders, core security hygiene matters more than ever: reduce your attack surface, enforce least privilege, and audit credential hygiene. If an attacker manages to gain a foothold, EDR solutions are less dependable if $5 of rented compute is all that's required to plough ahead undetected.