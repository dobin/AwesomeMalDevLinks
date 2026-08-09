# https://github.com/sums001/Windows-Copilot-API

[Skip to content](https://github.com/sums001/Windows-Copilot-API#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/sums001/Windows-Copilot-API) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/sums001/Windows-Copilot-API) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/sums001/Windows-Copilot-API) to refresh your session.Dismiss alert

{{ message }}

[sums001](https://github.com/sums001)/ **[Windows-Copilot-API](https://github.com/sums001/Windows-Copilot-API)** Public

- [Notifications](https://github.com/login?return_to=%2Fsums001%2FWindows-Copilot-API) You must be signed in to change notification settings
- [Fork\\
391](https://github.com/login?return_to=%2Fsums001%2FWindows-Copilot-API)
- [Star\\
1.2k](https://github.com/login?return_to=%2Fsums001%2FWindows-Copilot-API)


master

[**2** Branches](https://github.com/sums001/Windows-Copilot-API/branches) [**0** Tags](https://github.com/sums001/Windows-Copilot-API/tags)

[Go to Branches page](https://github.com/sums001/Windows-Copilot-API/branches)[Go to Tags page](https://github.com/sums001/Windows-Copilot-API/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![sums001](https://avatars.githubusercontent.com/u/44167398?v=4&size=40)](https://github.com/sums001)[sums001](https://github.com/sums001/Windows-Copilot-API/commits?author=sums001)<br>[Merge branch 'dev'](https://github.com/sums001/Windows-Copilot-API/commit/84389bf841113ccce9178a24685fedb27f02fad5)<br>2 months agoJun 27, 2026<br>[84389bf](https://github.com/sums001/Windows-Copilot-API/commit/84389bf841113ccce9178a24685fedb27f02fad5) · 2 months agoJun 27, 2026<br>## History<br>[31 Commits](https://github.com/sums001/Windows-Copilot-API/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/sums001/Windows-Copilot-API/commits/master/) 31 Commits |
| [assets](https://github.com/sums001/Windows-Copilot-API/tree/master/assets "assets") | [assets](https://github.com/sums001/Windows-Copilot-API/tree/master/assets "assets") | [Readme update](https://github.com/sums001/Windows-Copilot-API/commit/45d0da73c2ea9e06478572459542753d662bad40 "Readme update") | 2 months agoJun 22, 2026 |
| [copilot](https://github.com/sums001/Windows-Copilot-API/tree/master/copilot "copilot") | [copilot](https://github.com/sums001/Windows-Copilot-API/tree/master/copilot "copilot") | [Unify User-Agent across driver + browser to stabilize cf\_clearance](https://github.com/sums001/Windows-Copilot-API/commit/783c571b20cdf93c0e1c57b332c549e5681d2ca3 "Unify User-Agent across driver + browser to stabilize cf_clearance  cf_clearance is bound to the exact UA that earns it, but three surfaces touched one cookie with three different UAs: the curl_cffi driver (impersonate=chrome -> macOS Chrome/146), the headless refresh (Windows Chrome/131), and the interactive login (Playwright native, Windows Chrome/148). The driver always replayed clearance under a UA no browser had earned it with, so Cloudflare distrusted it and gated every turn behind a Turnstile -- surfacing as hourly clearance-expired churn once that gate became fatal.  Collapse all three onto one string (copilot/useragent.py): - driver pins a stable curl_cffi TLS profile (chrome146) and overrides   the UA + client hints to Windows Chrome/148. - both browser launches (headless and visible) advertise the same UA,   so clearance earned by either is reusable by the driver.  Standardize on 148 (Playwright's bundled Chromium) so the browser UA override does not contradict its native Sec-CH-UA hint. Re-auth path is unchanged -- it now refreshes without degrading clearance.") | 2 months agoJun 27, 2026 |
| [examples](https://github.com/sums001/Windows-Copilot-API/tree/master/examples "examples") | [examples](https://github.com/sums001/Windows-Copilot-API/tree/master/examples "examples") | [Stable Client + OpenAI API](https://github.com/sums001/Windows-Copilot-API/commit/f790ccbe047152791e1ed1779cd8b76f1b0a4699 "Stable Client + OpenAI API") | 2 months agoJun 19, 2026 |
| [server](https://github.com/sums001/Windows-Copilot-API/tree/master/server "server") | [server](https://github.com/sums001/Windows-Copilot-API/tree/master/server "server") | [Automatic CF clearance](https://github.com/sums001/Windows-Copilot-API/commit/878a2ff1ec5607b5c417a57a9ff0a7daa6e5b48e "Automatic CF clearance") | 2 months agoJun 24, 2026 |
| [tests](https://github.com/sums001/Windows-Copilot-API/tree/master/tests "tests") | [tests](https://github.com/sums001/Windows-Copilot-API/tree/master/tests "tests") | [Patch + diagnostic](https://github.com/sums001/Windows-Copilot-API/commit/4094d9811065de862c740f475913f099a1eb9515 "Patch + diagnostic") | 2 months agoJun 23, 2026 |
| [.dockerignore](https://github.com/sums001/Windows-Copilot-API/blob/master/.dockerignore ".dockerignore") | [.dockerignore](https://github.com/sums001/Windows-Copilot-API/blob/master/.dockerignore ".dockerignore") | [Add Docker deployment support](https://github.com/sums001/Windows-Copilot-API/commit/27f251ac513e9fb79a173e095373501fb5964e28 "Add Docker deployment support") | 2 months agoJun 22, 2026 |
| [.gitignore](https://github.com/sums001/Windows-Copilot-API/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/sums001/Windows-Copilot-API/blob/master/.gitignore ".gitignore") | [Merge branch 'dev'](https://github.com/sums001/Windows-Copilot-API/commit/5f9c40919d638518af88b9df0a1041e4d311e618 "Merge branch 'dev'") | 2 months agoJun 24, 2026 |
| [Dockerfile](https://github.com/sums001/Windows-Copilot-API/blob/master/Dockerfile "Dockerfile") | [Dockerfile](https://github.com/sums001/Windows-Copilot-API/blob/master/Dockerfile "Dockerfile") | [Add Docker deployment support](https://github.com/sums001/Windows-Copilot-API/commit/27f251ac513e9fb79a173e095373501fb5964e28 "Add Docker deployment support") | 2 months agoJun 22, 2026 |
| [LICENSE](https://github.com/sums001/Windows-Copilot-API/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/sums001/Windows-Copilot-API/blob/master/LICENSE "LICENSE") | [Add MIT License to the project](https://github.com/sums001/Windows-Copilot-API/commit/54fe14c25c000a3659e8d9a5860755eed61ecadb "Add MIT License to the project") | 2 months agoJun 21, 2026 |
| [README.md](https://github.com/sums001/Windows-Copilot-API/blob/master/README.md "README.md") | [README.md](https://github.com/sums001/Windows-Copilot-API/blob/master/README.md "README.md") | [Readme update](https://github.com/sums001/Windows-Copilot-API/commit/87baede9df652c07e133df29fd4d64979154ee7b "Readme update") | 2 months agoJun 24, 2026 |
| [app.py](https://github.com/sums001/Windows-Copilot-API/blob/master/app.py "app.py") | [app.py](https://github.com/sums001/Windows-Copilot-API/blob/master/app.py "app.py") | [Stable Client + OpenAI API](https://github.com/sums001/Windows-Copilot-API/commit/f790ccbe047152791e1ed1779cd8b76f1b0a4699 "Stable Client + OpenAI API") | 2 months agoJun 19, 2026 |
| [docker-compose.yml](https://github.com/sums001/Windows-Copilot-API/blob/master/docker-compose.yml "docker-compose.yml") | [docker-compose.yml](https://github.com/sums001/Windows-Copilot-API/blob/master/docker-compose.yml "docker-compose.yml") | [Add Docker deployment support](https://github.com/sums001/Windows-Copilot-API/commit/27f251ac513e9fb79a173e095373501fb5964e28 "Add Docker deployment support") | 2 months agoJun 22, 2026 |
| [requirements.txt](https://github.com/sums001/Windows-Copilot-API/blob/master/requirements.txt "requirements.txt") | [requirements.txt](https://github.com/sums001/Windows-Copilot-API/blob/master/requirements.txt "requirements.txt") | [Stable Client + OpenAI API](https://github.com/sums001/Windows-Copilot-API/commit/f790ccbe047152791e1ed1779cd8b76f1b0a4699 "Stable Client + OpenAI API") | 2 months agoJun 19, 2026 |
| View all files |

## Repository files navigation

# Windows Copilot API: a free LLM API powered by Microsoft Copilot

[Permalink: Windows Copilot API: a free LLM API powered by Microsoft Copilot](https://github.com/sums001/Windows-Copilot-API#windows-copilot-api-a-free-llm-api-powered-by-microsoft-copilot)

[![Windows Copilot API — a free, OpenAI-compatible API for your Microsoft Copilot account](https://github.com/sums001/Windows-Copilot-API/raw/master/assets/windows-copilot-api-banner.png)](https://github.com/sums001/Windows-Copilot-API/blob/master/assets/windows-copilot-api-banner.png)

**Using your own Microsoft Copilot account.** No API key, no credits, no paid plan: it turns the free chat at [copilot.microsoft.com](https://copilot.microsoft.com/) into an API you can call from code.

You can use it in two ways:

- 🐍 **As a Python library:** just call `client.chat("Hi")`. Supports streaming and multi-turn conversations.
- 🔌 **As a local OpenAI-compatible API:** runs a server at `http://localhost:8000/v1` that speaks the OpenAI format, so the official `openai` SDK (and any OpenAI-compatible app) works as a drop-in, with `localhost` in place of OpenAI.

You sign in once in a browser with your Microsoft **or Google** account; your session is saved and refreshed automatically after that.

> **Unofficial project.** Not affiliated with or endorsed by Microsoft. It automates the consumer Copilot web experience for personal use, so use it responsibly and within Microsoft's terms.

* * *

## Table of contents

[Permalink: Table of contents](https://github.com/sums001/Windows-Copilot-API#table-of-contents)

- [Why use this?](https://github.com/sums001/Windows-Copilot-API#why-use-this)
- [Requirements](https://github.com/sums001/Windows-Copilot-API#requirements)
- [Setup (2 minutes)](https://github.com/sums001/Windows-Copilot-API#setup-2-minutes)
- [Run with Docker (optional)](https://github.com/sums001/Windows-Copilot-API#run-with-docker-optional)
- [Usage 1: In Python (no server)](https://github.com/sums001/Windows-Copilot-API#usage-1-in-python-no-server)
- [Usage 2: As an OpenAI-compatible server](https://github.com/sums001/Windows-Copilot-API#usage-2-as-an-openai-compatible-server)
- [Command line](https://github.com/sums001/Windows-Copilot-API#command-line)
- [Concurrency & stress test](https://github.com/sums001/Windows-Copilot-API#concurrency--stress-test)
- [Rate limiting](https://github.com/sums001/Windows-Copilot-API#rate-limiting)
- [Project layout](https://github.com/sums001/Windows-Copilot-API#project-layout)
- [Notes & limitations](https://github.com/sums001/Windows-Copilot-API#notes--limitations)
- [Troubleshooting](https://github.com/sums001/Windows-Copilot-API#troubleshooting)
- [Collaboration & support](https://github.com/sums001/Windows-Copilot-API#collaboration--support)
- [License](https://github.com/sums001/Windows-Copilot-API#license)
- [Star History](https://github.com/sums001/Windows-Copilot-API#star-history)

* * *

## Why use this?

[Permalink: Why use this?](https://github.com/sums001/Windows-Copilot-API#why-use-this)

- **Free:** uses your normal signed-in Copilot, no API billing.
- **Drop-in OpenAI replacement:** point any OpenAI client at `localhost` and it just works.
- **Works everywhere you're signed in:** the signed-in path works even in regions where _anonymous_ Copilot is blocked (e.g. India).
- **Streaming + conversations:** token-by-token output and multi-turn threads addressed by `conversation_id`.

* * *

## Requirements

[Permalink: Requirements](https://github.com/sums001/Windows-Copilot-API#requirements)

- **Python 3.9+**
- A **Microsoft account** (the free one you use for Copilot is fine)
- Works on Windows, macOS, and Linux

* * *

## Setup (2 minutes)

[Permalink: Setup (2 minutes)](https://github.com/sums001/Windows-Copilot-API#setup-2-minutes)

```
# 1. Clone the project
git clone <your-repo-url>
cd Windows-Copilot-API
```

**2\. Create and activate a virtual environment**

On **macOS / Linux**:

```
python3 -m venv venv
source venv/bin/activate
```

On **Windows** (PowerShell):

```
python -m venv venv
venv\Scripts\Activate.ps1
```

> On Windows you may need to allow script execution once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. In `cmd.exe` activate with `venv\Scripts\activate.bat` instead.

**3\. Install dependencies and sign in**

```
# Install dependencies
pip install -r requirements.txt

# Install the browser Playwright needs (one-time)
playwright install chromium

# Sign in once: a browser opens, log into your Microsoft or Google account
python -m copilot login
```

The browser **closes by itself** once sign-in is detected — you don't need to press Enter or close it manually. After sign-in it sends one short warm-up message that mints the chat token **and** passes Cloudflare's "verify you're human" check in the same step (a brief "finishing setup…" appears, and a tiny throwaway chat lands in your history). If a checkbox shows up, click it in that login window. The steps are logged to `session/login.log` if anything goes wrong. That's it: your session is saved under `session/` (git-ignored, never shared) and reused on every run — so your first request works right away.

> 🛠️ **Run into trouble during setup or your first run?** Head to the [Troubleshooting](https://github.com/sums001/Windows-Copilot-API#troubleshooting) section, the bundled diagnostic both _fixes_ common issues (captcha/clearance) and _logs_ a shareable report.

* * *

## Run with Docker (optional)

[Permalink: Run with Docker (optional)](https://github.com/sums001/Windows-Copilot-API#run-with-docker-optional)

Prefer a container? You can run the OpenAI-compatible server in Docker once you've signed in.

> **Sign in on the host first.** The login step above opens a _visible_ browser, which can't run inside the headless container — so run `python -m copilot login` on your host to populate `session/`. The container mounts that folder and reuses the Cloudflare clearance earned on the host. It refreshes the chat token headlessly, but it can't earn _fresh_ clearance without a visible browser, so when clearance expires (~30 min) it returns a `503` — re-run `python -m copilot login` on the host to refresh `session/`.

```
docker compose up --build
# -> Copilot OpenAI-compatible API on http://localhost:8000
```

The [docker-compose.yml](https://github.com/sums001/Windows-Copilot-API/blob/master/docker-compose.yml) maps port `8000` and bind-mounts your `session/` so the login persists across restarts. Tune `RATE_LIMIT_RPM` / `RATE_LIMIT_BURST` there. To run without Compose, build and pass the same bindings by hand:

```
docker build -t windows-copilot-api .
docker run --rm -p 8000:8000 -v "$(pwd)/session:/app/session" windows-copilot-api
```

* * *

## Usage 1: In Python (no server)

[Permalink: Usage 1: In Python (no server)](https://github.com/sums001/Windows-Copilot-API#usage-1-in-python-no-server)

The simplest way if your code is already Python.

```
from copilot import CopilotClient

client = CopilotClient()                 # loads your signed-in session

# Get a full reply
reply = client.chat("Say hello in one short sentence.")
print(reply.text)

# Continue the SAME conversation — pass the id back
reply2 = client.chat("And now in French?", reply.conversation_id)
print(reply2.text)

# Stream the answer as it's typed
for chunk in client.stream("Tell me a short joke"):
    print(chunk, end="", flush=True)
```

`chat()` returns the full text plus a `conversation_id`; pass that id back to keep the thread going, or omit it to start fresh. `stream()` yields the reply piece by piece.

👉 More: [examples/01\_direct\_chat.py](https://github.com/sums001/Windows-Copilot-API/blob/master/examples/01_direct_chat.py), [02\_direct\_conversation.py](https://github.com/sums001/Windows-Copilot-API/blob/master/examples/02_direct_conversation.py), [03\_direct\_stream.py](https://github.com/sums001/Windows-Copilot-API/blob/master/examples/03_direct_stream.py)

* * *

## Usage 2: As an OpenAI-compatible server

[Permalink: Usage 2: As an OpenAI-compatible server](https://github.com/sums001/Windows-Copilot-API#usage-2-as-an-openai-compatible-server)

Start a local server that speaks the OpenAI API, so existing OpenAI tools and SDKs work unchanged.

```
python app.py
# -> Copilot OpenAI-compatible API on http://127.0.0.1:8000
```

Then point any OpenAI client at it (the API key is required by the SDK but ignored):

```
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="unused")

resp = client.chat.completions.create(
    model="copilot",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(resp.choices[0].message.content)
```

Or call it with plain HTTP / `curl`:

```
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'
```

**Endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/v1/chat/completions` | Chat (supports `"stream": true` and an optional `"conversation_id"`) |
| `GET` | `/v1/models` | Lists the single `copilot` model |

> Change the address with env vars: `HOST=0.0.0.0 PORT=8080 python app.py`, or run `uvicorn server.api:app --host 0.0.0.0 --port 8080`.

👉 More: [examples/04\_server\_http.py](https://github.com/sums001/Windows-Copilot-API/blob/master/examples/04_server_http.py), [05\_server\_stream.py](https://github.com/sums001/Windows-Copilot-API/blob/master/examples/05_server_stream.py), [06\_server\_openai\_sdk.py](https://github.com/sums001/Windows-Copilot-API/blob/master/examples/06_server_openai_sdk.py)

* * *

## Command line

[Permalink: Command line](https://github.com/sums001/Windows-Copilot-API#command-line)

```
python -m copilot login          # sign in and save the session
python -m copilot ask "Hello!"   # quick one-shot question
```

* * *

## Cloudflare clearance (automatic)

[Permalink: Cloudflare clearance (automatic)](https://github.com/sums001/Windows-Copilot-API#cloudflare-clearance-automatic)

Copilot's chat sits behind Cloudflare. Access needs a `cf_clearance` cookie,
earned by passing a "verify you're human" check in a real browser, and it lasts
about half an hour. The bridge handles this for you:

- **At sign-in:**`python -m copilot login` earns clearance as part of the same
warm-up that mints your token, so your first request works immediately. If
Cloudflare shows a checkbox, click it in the login window.
- **When it expires:** if a later request hits the gate, the bridge opens a
browser, passes the check (the checkbox is clicked automatically, or you click
it if one appears), and retries the request for you. You'll see a short
`[copilot] clearance: …` progress log, then the answer.

On a trusted connection the check often passes invisibly with no window at all. A
datacenter/VPN IP is stricter and more likely to show the checkbox; a residential
connection clears most reliably.

The **server** never opens a window: when clearance expires it returns a `503`
(`type: "clearance_required"`). Re-clear out of band with `python -m copilot login`, then retry.

* * *

## Concurrency & stress test

[Permalink: Concurrency & stress test](https://github.com/sums001/Windows-Copilot-API#concurrency--stress-test)

The server bridges a **single** signed-in Copilot account, and Copilot's chat
socket doesn't tolerate concurrent conversations from one process. So the server
**serializes** upstream calls: parallel HTTP requests queue behind a lock and run
one at a time (see [server/api.py](https://github.com/sums001/Windows-Copilot-API/blob/master/server/api.py)). This is intentional, and it
means throughput is sequential, not parallel.

You can measure where it breaks with the included stress test, which fires a
batch of simultaneous requests and **doubles the batch size every successful**
**round** until the first error:

```
# Start the server in one terminal
python app.py

# Ramp concurrency in another (1 → 2 → 4 → 8 → …)
python tests/stress.py
python tests/stress.py --max 64 --timeout 120 --url http://localhost:8000
```

**Sample run** (one signed-in account):

| Concurrency | Result | Wall time | Latency (min / median / max) |
| --- | --- | --- | --- |
| 1 | ✓ all ok | 3.7s | 3.7 / 3.7 / 3.7s |
| 2 | ✓ all ok | 4.6s | 3.4 / 4.6 / 4.6s |
| 4 | ✓ all ok | 8.3s | 3.7 / 6.7 / 8.3s |
| 8 | ✗ 1 failed (`HTTP 502`) | 13.3s | 3.5 / 9.7 / 13.3s |

**Highest fully-successful concurrency: 4.** Wall time roughly doubles each round
while _minimum_ latency stays flat (~3.5s) — the signature of a serialized queue:
one request runs immediately, the rest wait their turn. The failure at 8 is an
upstream `502` (Copilot rejecting requests under load), not a server crash or
timeout — so the exact break point is flaky and may vary between runs.

> Takeaway: keep concurrent in-flight requests low (≈ 1–4). This is a personal
> bridge, not a high-throughput gateway — and please don't hammer your account.

* * *

## Rate limiting

[Permalink: Rate limiting](https://github.com/sums001/Windows-Copilot-API#rate-limiting)

Concurrency (above) is _how many at once_; the **rate limit** is _how many per_
_minute, sustained_. Microsoft publishes none for consumer Copilot, so the bridge
enforces a self-imposed one with a [token bucket](https://github.com/sums001/Windows-Copilot-API/blob/master/server/ratelimit.py): it caps
accepted requests per minute and returns a standard `429` \+ `Retry-After` when
you exceed it. Two env vars tune it:

| Env var | Default | Meaning |
| --- | --- | --- |
| `RATE_LIMIT_RPM` | `12` | Requests/minute the bridge accepts. `0` disables the limit. |
| `RATE_LIMIT_BURST` | `4` | How many requests may go back-to-back before pacing kicks in. |

```
RATE_LIMIT_RPM=20 RATE_LIMIT_BURST=5 python app.py   # raise it; 0 to disable
```

The default 12 rpm sits safely below the ~15 rpm where a single account starts
seeing upstream `502`s. To find _your_ ceiling, run the server with the limiter
off (`RATE_LIMIT_RPM=0`) and push the probe until failures appear:

```
python tests/ratelimit.py --rpm 20 --minutes 3
```

**On the client side, use exponential backoff.** Both `429` (bridge limit) and
the occasional `502` (Copilot upstream hiccup) are transient — retry with
growing delays (e.g. 1s, 2s, 4s) and they almost always clear. The official
`openai` SDK does this automatically and honours `Retry-After`; with plain HTTP,
add a few retries yourself.

* * *

## Project layout

[Permalink: Project layout](https://github.com/sums001/Windows-Copilot-API#project-layout)

| Path | What it does |
| --- | --- |
| [copilot/](https://github.com/sums001/Windows-Copilot-API/blob/master/copilot) | The core library: `CopilotClient`, auth, browser sign-in, HTTP driver |
| [server/](https://github.com/sums001/Windows-Copilot-API/blob/master/server) | The FastAPI OpenAI-compatible server |
| [examples/](https://github.com/sums001/Windows-Copilot-API/blob/master/examples) | Runnable examples for every feature ( [examples/README.md](https://github.com/sums001/Windows-Copilot-API/blob/master/examples/README.md)) |
| [tests/](https://github.com/sums001/Windows-Copilot-API/blob/master/tests) | Test scripts: the concurrency stress test ( [tests/stress.py](https://github.com/sums001/Windows-Copilot-API/blob/master/tests/stress.py)) and the diagnostic & report tool ( [tests/diagnostic.py](https://github.com/sums001/Windows-Copilot-API/blob/master/tests/diagnostic.py)) |
| [app.py](https://github.com/sums001/Windows-Copilot-API/blob/master/app.py) | Starts the server |

* * *

## Notes & limitations

[Permalink: Notes & limitations](https://github.com/sums001/Windows-Copilot-API#notes--limitations)

- **Sign in once, then reuse.** The cached token refreshes automatically; you only re-sign-in if the session fully expires.
- **No daily limit, but be reasonable.** Microsoft doesn't impose a daily chat cap, but please use it in moderation, and don't spam or hammer it with automated bulk requests.
- **One model.** Copilot has no model picker, so the server advertises a single model named `copilot`.
- **Roughly GPT-4 class.** On GPQA Diamond (198 graduate-level questions, closed-book) it scores **40.9%**, which puts it in the GPT-4 family rather than the reasoning tier (o1/o3). Measured with [tests/gpqa\_bench.py](https://github.com/sums001/Windows-Copilot-API/blob/master/tests/gpqa_bench.py).
- **Your session is private.** Everything in `session/` (cookies + token) stays on your machine and is git-ignored.

* * *

## Troubleshooting

[Permalink: Troubleshooting](https://github.com/sums001/Windows-Copilot-API#troubleshooting)

Cloudflare clearance is handled automatically (see above), so most "verify you're
human" issues clear themselves. If a request still fails, run the diagnostic — it
refreshes the session and writes a shareable report.

```
python tests/diagnostic.py                # browser capture + report
python tests/diagnostic.py --report-only  # headless/VPS: report only, no browser
```

The default run opens your signed-in browser and asks you to send one short
message. That single action:

- **Refreshes clearance:** it drives a _real_ browser on the same
`session/profile/` the bridge uses, so passing any "verify you're human" check
earns a fresh `cf_clearance` cookie, then snapshots the session (cookies +
token) into `session/token.json` for the pure-HTTP driver to adopt.
- **Captures the protocol** to `session/ws_capture.log`. A clean turn goes
`setOptions` → `send` → `appendText…` → `done`; a `{"event":"challenge", "method":"cloudflare",…}` frame means Cloudflare gated the turn.

It also writes `session/diagnostic_report.txt` — environment, the _shape_ of your
session (cookie names + token length, never the values), a live chat probe, and
redacted log tails. **Both files are safe to share:** access tokens, cookies,
OAuth codes, and emails are redacted before anything is written. Attach
`diagnostic_report.txt` to a GitHub issue (skim it first) and the cause is
usually obvious.

> On a headless **server/VPS** you can't open a browser, so clearance can't be
> earned there — pass `--report-only`, and do the clearance step on a machine
> with a display (or route traffic through a residential connection, e.g. a
> home-PC exit node), since datacenter IPs are where Cloudflare is strictest.

* * *

## Collaboration & support

[Permalink: Collaboration & support](https://github.com/sums001/Windows-Copilot-API#collaboration--support)

Need a hand getting this running? Open a [GitHub issue](https://github.com/sums001/Windows-Copilot-API/issues) for bugs (for setup/auth problems, attach the redacted `diagnostic_report.txt` from `python tests/diagnostic.py`), start a [discussion](https://github.com/sums001/Windows-Copilot-API/discussions) to share ideas, or send a pull request.

And if you're working on something interesting, or looking for someone to build it, I'm always open to a chat. Feel free to reach out:

- X: [@sums001](https://x.com/sums001)
- Email: [devsum0101@gmail.com](mailto:devsum0101@gmail.com)
- Discord: `sum_s_s`

* * *

## License

[Permalink: License](https://github.com/sums001/Windows-Copilot-API#license)

Released under the [MIT License](https://github.com/sums001/Windows-Copilot-API/blob/master/LICENSE). As this is an unofficial project, you remain responsible for complying with Microsoft's terms of service.

* * *

## Star History

[Permalink: Star History](https://github.com/sums001/Windows-Copilot-API#star-history)

[![Star History Chart](https://camo.githubusercontent.com/2c6302daf06f6326dbaf0ec00f503077027b6d1ee5cfcb0cd840985f7d37e801/68747470733a2f2f6170692e737461722d686973746f72792e636f6d2f63686172743f7265706f733d73756d733030312f57696e646f77732d436f70696c6f742d41504926747970653d74696d656c696e65266c6567656e643d746f702d6c656674)](https://www.star-history.com/?repos=sums001%2FWindows-Copilot-API&type=timeline&legend=top-left)

## About

Reverse engineered Windows Copilot into an OpenAI-compatible API. Access GPT-4 and GPT-5 models through a simple REST interface without API keys or billing.

### Topics

[ai](https://github.com/topics/ai) [ai-agents](https://github.com/topics/ai-agents) [api](https://github.com/topics/api) [copilot](https://github.com/topics/copilot) [llm](https://github.com/topics/llm) [microsoft-copilot](https://github.com/topics/microsoft-copilot) [openai](https://github.com/topics/openai)

### Resources

[Readme](https://github.com/sums001/Windows-Copilot-API#readme-ov-file)

[MIT license](https://github.com/sums001/Windows-Copilot-API#MIT-1-ov-file)

[Activity](https://github.com/sums001/Windows-Copilot-API/activity)

### Stars

**1.2k** stars

### Watchers

**8** watching

### Forks

[**391** forks](https://github.com/sums001/Windows-Copilot-API/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fsums001%2FWindows-Copilot-API&report=sums001+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.