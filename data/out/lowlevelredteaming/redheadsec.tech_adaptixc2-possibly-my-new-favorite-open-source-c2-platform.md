# https://redheadsec.tech/adaptixc2-possibly-my-new-favorite-open-source-c2-platform/

You've successfully subscribed to RedHeadSec

Great! Next, complete checkout for full access to RedHeadSec

Welcome back! You've successfully signed in

Success! Your account is fully activated, you now have access to all content.

Search for Blog

![AdaptixC2 - Possibly My New Favorite Open-Source C2 Platform](https://redheadsec.tech/content/images/2025/05/adapt.png)

12 min read
May 30, 2025

# AdaptixC2 - Possibly My New Favorite Open-Source C2 Platform

[![Evasive Ginger's Picture](https://redheadsec.tech/content/images/2026/01/DDF-1.png)](https://redheadsec.tech/author/evasive_ginger/)

[Evasive Ginger](https://redheadsec.tech/author/evasive_ginger/) in[Tools](https://redheadsec.tech/tag/tools/) [Red-Team](https://redheadsec.tech/tag/red-team/)

As an offensive security consultant, I've had my fair share of experience with command and control frameworks. Everything from commercial products such as Cobalt Strike to open-source frameworks such as [Sliver](https://github.com/BishopFox/sliver?ref=redheadsec.tech) and [Mythic](https://github.com/its-a-feature/Mythic?ref=redheadsec.tech). There are tons of options in the space, each with their own little pros and cons. Hearing about another C2 generally does not make the news for me but AdaptixC2 was the exception. I generally try to avoid the use of any full feature C2 in current operations, preferring to live off the land or used specialized tools such as [Loki](https://github.com/boku7/Loki?ref=redheadsec.tech) that currently fly under the radar with far greater success than Cobalt Strike or Sliver. I am also not really versed in the development department, so building full in house implementations of C2 servers and clients is just outside the available time I have to learn and commit while performing non-stop work and life. Generally, this is where I'd consider the two most popular open source tools like Mythic and Sliver come into play. Due to the very modular nature of Mythic's design, the ease of building an agent to plug n play with the server is far more streamlined that other platforms, allowing operators to build custom loaders that can perform any number of needed evasion techniques to load code. Sadly, I personally am not a huge fan of Mythic's UI setup (It was updated recently which I am more fond of now) and the pain of debugging inside multiple docker containers and services can get cumbersome. While Sliver was my favorite choice in the past due to the Armory and easy setup, its slower development time and lack of a GUI can be a turn off for some situations. Until now, Mythic was really the only open source C2 in play for most adversarial engagements in my opinion but that may be changing! This is where AdaptixC2 comes in, providing the clean interface similar if not better than Cobalt Strike's while allowing for custom agents and modularity. In this post, I will be going over the basics of v0.5 currently released, the features. and creating custom extensions.

# AdaptixC2 - Overview

AdaptixC2 can be found here: [https://github.com/Adaptix-Framework/AdaptixC2/tree/main](https://github.com/Adaptix-Framework/AdaptixC2/tree/main?ref=redheadsec.tech)

"Adaptix is an extensible post-exploitation and adversarial emulation framework made for penetration testers. The Adaptix server is written in Golang and to allow operator flexibility. The GUI Client is written in C++ QT, allowing it to be used on Linux, Windows, and MacOS operating systems."

## Features (v.5)

- Server/Client Architecture for Multiplayer Support
- Cross-platform GUI client
- Fully encrypted communications
- Listener and Agents as Plugin (Extender)
- Client extensibility for adding new tools
- Task and Jobs storage
- Files and Process browsers
- Socks4 / Socks5 / Socks5 Auth support
- Local and Reverse port forwarding support
- BOF support
- Linking Agents and Sessions Graph
- Agents Health Checker
- Agents KillDate and WorkingTime control
- Windows/Linux/MacOs agents support
- Remote Terminal

I am running the server on a Kali instance, with the client being ran on a Mac ARM64 machine. Installation is pretty straight forward and covered well here: [https://adaptix-framework.gitbook.io/adaptix-framework/adaptix-c2/getting-starting/installation](https://adaptix-framework.gitbook.io/adaptix-framework/adaptix-c2/getting-starting/installation?ref=redheadsec.tech)

# Getting Started

Once you have the compiled server and client, you'll want to configure your C2 server profile. This is different than what you normally expect out of profiles such as Cobalt Strike or Nighthawk, which have everything tied together. Here, AdaptixC2 has a server profile which looks like the following:

```bash
┌──(root㉿DEV-kali)-[/opt/AdaptixC2/dist]
└─# cat profile.json
{
  "Teamserver": {
    "port": 4321,
    "endpoint": "/endpoint",
    "password": "pass",
    "cert": "server.rsa.crt",
    "key": "server.rsa.key",
    "extenders": [\
      "extenders/listener_beacon_http/config.json",\
      "extenders/listener_beacon_smb/config.json",\
      "extenders/listener_beacon_tcp/config.json",\
      "extenders/agent_beacon/config.json",\
      "extenders/listener_gopher_tcp/config.json",\
      "extenders/agent_gopher/config.json"\
    ]
  },

  "ServerResponse": {
    "status": 404,
    "headers": {
      "Content-Type": "text/html; charset=UTF-8",
      "Server": "AdaptixC2",
      "Adaptix Version": "v0.3"
    },
    "page": "404page.html"
  }
}
```

This will set the settings for connecting via the client such as the endpoint URI, password, loaded extenders (listeners and agents), and server response traffic. You can set these via the command line as well if desired but I'd always recommend using a configuration JSON file. Multiplayer is supported out of the box as the server uses one password with the client allowing users to join with an alias, similar to Cobalt Strike. Once you have it ready, you can run it using the `--profile <config>` flag.

❗

OPSEC NOTE: Always put your teamsevers behind redirectors and ACLs to ensure it is not being hit by unwanted eyes when using any C2 in production.

```bash
└─# ./adaptixserver --profile profile.json -debug

[===== Adaptix Framework v0.5 =====]

[+] Starting server -> https://0.0.0.0:4321/endpoint [30/05 19:37:56]
[*] Restore data from Database... [30/05 19:37:56]
   [+] Restored 0 agents [30/05 19:37:56]
   [+] Restored 0 pivots [30/05 19:37:56]
   [+] Restored 0 downloads [30/05 19:37:56]
   [+] Restored 0 screens [30/05 19:37:56]
   [+] Restored 0 listeners [30/05 19:37:56]
```

🤷

As of v0.5, the debug flag does not really change the output. Currently not sure if this is a bug or operator error.

Once running you can connect via the client:

![](https://redheadsec.tech/content/images/2025/05/image.png)Client Connection![](https://redheadsec.tech/content/images/2025/05/image-35.png)

You'll be greeted by the very clean UI, with my personal preference of dark mode with 14 font. From here, you'll want to take a look at the tabs on the interface pane.

![](https://redheadsec.tech/content/images/2025/05/image-2.png)

In order of appearance from left to right, you have:

1. **Listeners** \- Here you can create, edit, and delete listeners
2. **Logs** \- Provides server logs
3. **List View** \- View all current agents in list format
4. **Graph View** \- View all current agents in a graph format
5. **Jobs & Tasks** \- View current and completed tasks assigned to agents
6. **Tunnels** \- View current tunnels deployed by agents
7. **Downloads**\- View downloads from agents
8. **Screenshots** \- View captured screenshots via the Extensions-Kit screenshot BOF
9. **Reconnect** \- Used to reconnect to the server if lost or JWT is expired/invalid

The bottom pane is the agent console and acts very similar to other GUI based C2 clients such as Cobalt Strike or Mythic.

First things first, we need to get a listener up and running. Open the listeners tab, right click on the console pane, and select "Create". You'll be greeted by the following window:

![](https://redheadsec.tech/content/images/2025/05/image-3.png)

Here is where I find AdaptixC2 current lacks the greatest in terms of default customization. This window allows to define a listener based on the current loaded extenders on the server. Recall that part of the building process was the `make extenders` command that were compiled and loaded into your /dist directory. The default is the BeaconHTTP listener which allows you to specify callback hosts, a single URI, user-agent, and other aspects such as headers or responses. Ideally we want to be able to dynamically create callback URIs or select from a list that can then dynamically create data to avoid getting fingerprinted by network traffic scanners or an analyst. I plan to look into custom plugin development or a PR to enhance these features but for now we can go with a good ol default testing profile. The other options here are gopher TCP agents which are compatible with all major operating systems and bind agents which are your peer to peer agents which I will go over shortly. If you select `Use SSL (HTTPS)`, it will generate a self-signed certificate if you do not provide one.

![](https://redheadsec.tech/content/images/2025/05/image-4.png)Sample HTTP Profile![](https://redheadsec.tech/content/images/2025/05/image-5.png)Running Listener

Next we need to create an agent for this listener, right click the listener and hit `Generate Agent`. This will bring up the agent build window for that particular listener. Each listener is tied to specific agent plugins which vary in functionality. Be sure to overview these and choose what is best for your current situation.

![](https://redheadsec.tech/content/images/2025/05/image-6.png)

BeaconHTTP are Windows only currently so we will be testing against another lab host on my Ludus network. On the generate agent window, we can set architecture, format (exe, dll, shellcode, service exe), sleep & jitter, along with kill dates and working times. Kill date will terminate the agent once it hits the specified time and date while working times will ensure your beacon is only active during specific time periods. Another great feature here and on the listener windows are the load and save configuration buttons on the top right, allowing you to save and load profiles that you have built. I will keep everything default here and hit generate. Save to the location of your choice, then move to a Windows host for testing.

![](https://redheadsec.tech/content/images/2025/05/image-7.png)

This box has all protections disabled. Be warned that this code is not OPSEC safe out of the box and has no built in evasion features for default agent plugins so don't expect to go own a fortune 500 off the bat with this. Run the program and you should see a callback:

![](https://redheadsec.tech/content/images/2025/05/image-8.png)

Perfect now we have something to work with. Lets right click the new beacon and go into the console. You may notice other awesome features here such as the ability to browse files and processes via the GUI, create tunnels, and view tasks. You can also do some organizational operations such as set tags, change colors, hide beacons, and mark activity.

![](https://redheadsec.tech/content/images/2025/05/image-12.png)File Explorer

![](https://redheadsec.tech/content/images/2025/05/image-13.png)Process Explorer

You can use the `help` command to list currently loaded commands and extensions. By default, you'll only have the following loaded:

![](https://redheadsec.tech/content/images/2025/05/image-9.png)Default Commands for BeaconHTTP

I'd advise loading in the [https://github.com/Adaptix-Framework/Extension-Kit](https://github.com/Adaptix-Framework/Extension-Kit?ref=redheadsec.tech) which contains tons of useful commands and alias. Perform a `git clone` [`https://github.com/Adaptix-Framework/Extension-Kit.git`](https://github.com/Adaptix-Framework/Extension-Kit.git?ref=redheadsec.tech) then run `for d in */ ; do (cd "$d" && make); done` to make all the current extensions ( **assuming you have all the needed dependencies installed!**). Now go to the Extender tab, right click and `Load New`. Once you have everything you want loaded, you'll have more options to utilize for your agents!

![](https://redheadsec.tech/content/images/2025/05/image-10.png)Same of the Extension Kit

Now we can run some commonly used tools such as `ifconfig` which basically an alias to run the ipconfig BOF from [https://github.com/trustedsec/CS-Situational-Awareness-BOF](https://github.com/trustedsec/CS-Situational-Awareness-BOF?ref=redheadsec.tech).

![](https://redheadsec.tech/content/images/2025/05/image-14.png)

If you need help to understand an extension or command, you can use `help <command> <subcommand>` to get some guidance.

![](https://redheadsec.tech/content/images/2025/05/image-15.png)

Lets spin up a SOCKS5 proxy using **`socks start 1080`**

![](https://redheadsec.tech/content/images/2025/05/image-17.png)

Now lets test that we have access via the proxy:

![](https://redheadsec.tech/content/images/2025/05/image-18.png)

Very nice, now we could proxy into the internal network as needed. Lets check out a GopherTCP agent. I will setup the host and callback to the Kali server and leave the rest as default. You can generate mTLS certificates to use with this agent, but it is not done for you by the server. You can use the provided script to generate some test certificates.

![](https://redheadsec.tech/content/images/2025/05/image-19.png)GopherTCP Agent

```bash
# CA cert
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt -subj "/CN=Test CA"

# server cert and key
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=localhost"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256

# client cert and key
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=client"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365 -sha256
```

Once again, you can generate an agent for all major operating systems here. Sadly, shellcode generation is not supported at this time for the Gopher agent:

![](https://redheadsec.tech/content/images/2025/05/image-20.png)

Now run the agent and lets get a callback:

![](https://redheadsec.tech/content/images/2025/05/image-21.png)

The Gopher agent supports a lot of the main default commands such as tunnels, file browsing, and process browsing.

![](https://redheadsec.tech/content/images/2025/05/image-22.png)

Lets see the power of this agent by also running a Mac agent!

![](https://redheadsec.tech/content/images/2025/05/image-31.png)![](https://redheadsec.tech/content/images/2025/05/image-30.png)Running Shell Command

This allows for having access to all the major operating systems that can communicate in one place, a large advantage over some C2s which are limited to Windows environments.

Lets take a look at some pivot agents now. These are used to link together beacons, minimizing the egress traffic out of the network to the C2 sever. Setup a listener and create an agent as usual, run the agent and use `link smb <target> <pipe>` to link them. This agent is running on a Windows 11 host with Defender enabled without issue!

![](https://redheadsec.tech/content/images/2025/05/image-28.png)List View of Current Beacon Agents![](https://redheadsec.tech/content/images/2025/05/image-25.png)Graph View![](https://redheadsec.tech/content/images/2025/05/image-26.png)BeaconSMB Agent![](https://redheadsec.tech/content/images/2025/05/image-33.png)Screenshot Viewer

This provides a general overview of working with AdaptixC2 so far. I encourage you to setup a lab or use a HackTheBox network to continue playing around with it to better familiarize yourself with the framework.

# Creating Custom Extensions

❗

Adaptix v0.7 moved to a new scripting language for extensions and front end integrations called AxScript. You can view the documentation here: [https://adaptix-framework.gitbook.io/adaptix-framework/development/axscript](https://adaptix-framework.gitbook.io/adaptix-framework/development/axscript?ref=redheadsec.tech)

One of the biggest perks is the ease of extending the current agents using BOFs. Adaptix makes it easy by allowing the operator to create ASX files that configure any compatible BOFs to the client. This is the current list of supported BOF APIs:

[Beacon BOFs \| Adaptix Framework\\
\\
![](https://redheadsec.tech/content/images/icon/image-1)Adaptix Framework\\
\\
![](https://redheadsec.tech/content/images/thumbnail/image-1)](https://adaptix-framework.gitbook.io/adaptix-framework/extenders/agents/beacon/beacon-bofs?ref=redheadsec.tech)

Lets take the GetDomainInfo from [https://github.com/rvrsh3ll/BOF\_Collection](https://github.com/rvrsh3ll/BOF_Collection?ref=redheadsec.tech) and create an extension for it in AdaptixC2. Download the GetDomainInfo.c, beacon.h, and Makefile and put in a folder. The extension config files are in the following format:

```js
 var metadata = {
    name: "Extension Name",
    description: "A description shown in the AxScript Manager"
};

var cmd_something = ax.create_command(
    "something", // Command Name
    "Executes Something BOF", // Description in console
    "something arg1 arg2" // Example
);

cmd_something.setPreHook(function (id, cmdline, parsed_json, ...parsed_lines) {
    let bof_path = ax.script_dir() + "_bin/something." + ax.arch(id) + ".o";
    ax.execute_alias(id, cmdline, `execute bof ${bof_path}`, "BOF implementation: something");
});

var group_something = ax.create_commands_group("Something Group", [cmd_something]);
ax.register_commands_group(group_something, ["beacon","gopher"], ["windows"], []); // What agents it will be available to
```

You can review [https://adaptix-framework.gitbook.io/adaptix-framework/adaptix-c2/bof-and-extensions](https://adaptix-framework.gitbook.io/adaptix-framework/adaptix-c2/bof-and-extensions?ref=redheadsec.tech) to go over the details for formatting, parameters, macros, and data types. The name and description fields are what show up in the Extender menu when loaded, with the extensions array containing everything that will be needed or shown via the console. The following showcases a working GetDomainInfo.axs extension:

```js
 var metadata = {
    name: "GetDomainInfo",
    description: "Returns information on the current domain and domain controller."
};

var cmd_getdomaininfo = ax.create_command(
    "getdomaininfo",
    "Executes GetDomainInfo BOF",
    "getdomaininfo"
);

cmd_getdomaininfo.setPreHook(function (id, cmdline, parsed_json, ...parsed_lines) {
    let bof_path = ax.script_dir() + "_bin/getdomaininfo." + ax.arch(id) + ".o";
    ax.execute_alias(id, cmdline, `execute bof ${bof_path}`, "BOF implementation: GetDomainInfo");
});

var group_getdomaininfo = ax.create_commands_group("GetDomainInfo", [cmd_getdomaininfo]);
ax.register_commands_group(group_getdomaininfo, ["beacon","gopher"], ["windows"], []);
```

This enables the use of the `getdomaininfo` command in the console which will run the BOF located at `$EXT_DIR()/_bin/getdomaininfo.$ARCH().o` _._ This essentially calls a compiled BOF file located in a `_bin` directory where the configuration AXS file is loaded from and for which architecture is needed using the `$ARCH()` macro. So your \_bin folder would contain a `getdomaininfo.x64.o` for example. These can be edited as needed to meet your own organization structure if you chose to deviate from the default. Load the new extension like all the others and give it a try.

![](https://redheadsec.tech/content/images/2025/05/image-29.png)

Very nice, a new working command to add to the tool belt. Here is another showcasing inject-amsi using arguments added to the injection group located in the [Extension-Kit](https://github.com/Adaptix-Framework/Extension-Kit?ref=redheadsec.tech):

```js
// STUFF
var cmd_inject_amsi = ax.create_command("inject_amsi", "Injects AMSI Bypass to given PID", "inject-amsi 808");
cmd_inject_amsi.addArgInt("pid", true);
cmd_inject_amsi.setPreHook(function (id, cmdline, parsed_json, ...parsed_lines) {
    let pid = parsed_json["pid"];

    let bof_params = ax.bof_pack("int", [pid]);
    let bof_path = ax.script_dir() + "_bin/inject_amsi." + ax.arch(id) + ".o";
    let message = "Task: Inject  AMSI bypass";

    ax.execute_alias(id, cmdline, `execute bof ${bof_path} ${bof_params}`, message);
});

var group_exec = ax.create_commands_group("Injection-BOF", [cmd_inject_cfg, cmd_inject_amsi]);
ax.register_commands_group(group_exec, ["beacon", "gopher"], ["windows"], []);

/// MENU

let inject_action = menu.create_action("Inject shellcode", function(process_list) {
    let methods = {
        "inject-sec": "Injects desired shellcode into target process using section mapping",
        "inject-cfg": "Inject shellcode into a target process and hijack execution via overwriting combase.dll!__guard_check_icall_fptr",
        "inject-amsi": "Injects AMSI Bypass to given PID"
    };

// STUFFF
```

![](https://redheadsec.tech/content/images/2025/08/image.png)

# Conclusion

Overall, I am liking the direction AdaptixC2 is going and being still early stages, I see a lot of potential. I'll continue to dive into further customizations and any milestone developments made as time goes on. Consider following and supporting the authors if you've enjoyed this quick overview.

Till next time, farewell and happy hacking!

[Share on Facebook](https://www.facebook.com/sharer/sharer.php?u=https://redheadsec.tech/adaptixc2-possibly-my-new-favorite-open-source-c2-platform/ "Share on Facebook")[Share on Twitter](https://twitter.com/share?text=AdaptixC2%20-%20Possibly%20My%20New%20Favorite%20Open-Source%20C2%20Platform&url=https://redheadsec.tech/adaptixc2-possibly-my-new-favorite-open-source-c2-platform/ "Share on Twitter")[Share on Pinterest](https://pinterest.com/pin/create/button/?url=https://redheadsec.tech/adaptixc2-possibly-my-new-favorite-open-source-c2-platform/&media=https://redheadsec.tech/content/images/2025/05/adapt.png&description=AdaptixC2%20-%20Possibly%20My%20New%20Favorite%20Open-Source%20C2%20Platform "Share on Pinterest")

[![](https://redheadsec.tech/content/images/2025/01/DALL-E-2025-01-24-20.38.00---A-highly-detailed-digital-illustration-of-an-iron-eye-centered-in-the-composition--forged-with-intricate-metallic-textures-and-subtle-engravings.-The-.webp)\\
\\
Previous\\
Post\\
\\
**IronEye - Welcome to your Rusty LDAP Swiss Army Knife**](https://redheadsec.tech/ironeye-welcome-to-your-rusty-ldap-swiss-army-knife-2/) [![](https://redheadsec.tech/content/images/2025/06/phantom.png)\\
\\
Next Post \\
\\
**Phantom Persistence - A quick look at Windows Persistence via RegisterApplicationRestart**](https://redheadsec.tech/phantom-boot-a-quick-look-at-windows-persistence-via-registerapplicationrestart/)

### You may also like

[![Phantom Persistence - A quick look at Windows Persistence via RegisterApplicationRestart](https://redheadsec.tech/content/images/2025/06/phantom.png)](https://redheadsec.tech/phantom-boot-a-quick-look-at-windows-persistence-via-registerapplicationrestart/)

3 min read
Jun 25, 2025

## [Phantom Persistence - A quick look at Windows Persistence via RegisterApplicationRestart](https://redheadsec.tech/phantom-boot-a-quick-look-at-windows-persistence-via-registerapplicationrestart/)

A quick look at Windows Persistence via RegisterApplicationRestart


[![Evasive Ginger's Picture](https://redheadsec.tech/content/images/2026/01/DDF-1.png)](https://redheadsec.tech/author/evasive_ginger/)

[Evasive Ginger](https://redheadsec.tech/author/evasive_ginger/) in[Tools](https://redheadsec.tech/tag/tools/) [Red-Team](https://redheadsec.tech/tag/red-team/)

[![IronEye - Welcome to your Rusty LDAP Swiss Army Knife](https://redheadsec.tech/content/images/2025/01/DALL-E-2025-01-24-20.38.00---A-highly-detailed-digital-illustration-of-an-iron-eye-centered-in-the-composition--forged-with-intricate-metallic-textures-and-subtle-engravings.-The-.webp)](https://redheadsec.tech/ironeye-welcome-to-your-rusty-ldap-swiss-army-knife-2/)

5 min read
Jan 24, 2025

## [IronEye - Welcome to your Rusty LDAP Swiss Army Knife](https://redheadsec.tech/ironeye-welcome-to-your-rusty-ldap-swiss-army-knife-2/)

Description: A mullti-purpose LDAP tool written in Rust.
Created By: Evasive\_Ginger


[![Evasive Ginger's Picture](https://redheadsec.tech/content/images/2026/01/DDF-1.png)](https://redheadsec.tech/author/evasive_ginger/)

[Evasive Ginger](https://redheadsec.tech/author/evasive_ginger/) in[Red-Team](https://redheadsec.tech/tag/red-team/) [Cybersecurity](https://redheadsec.tech/tag/cybersecurity/) [Tools](https://redheadsec.tech/tag/tools/)