# https://github.com/symgraph/IDAssist

[Skip to content](https://github.com/symgraph/IDAssist#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/symgraph/IDAssist) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/symgraph/IDAssist) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/symgraph/IDAssist) to refresh your session.Dismiss alert

{{ message }}

[symgraph](https://github.com/symgraph)/ **[IDAssist](https://github.com/symgraph/IDAssist)** Public

- [Notifications](https://github.com/login?return_to=%2Fsymgraph%2FIDAssist) You must be signed in to change notification settings
- [Fork\\
73](https://github.com/login?return_to=%2Fsymgraph%2FIDAssist)
- [Star\\
706](https://github.com/login?return_to=%2Fsymgraph%2FIDAssist)


master

[**2** Branches](https://github.com/symgraph/IDAssist/branches) [**17** Tags](https://github.com/symgraph/IDAssist/tags)

[Go to Branches page](https://github.com/symgraph/IDAssist/branches)[Go to Tags page](https://github.com/symgraph/IDAssist/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![jtang613](https://avatars.githubusercontent.com/u/11688468?v=4&size=40)](https://github.com/jtang613)[jtang613](https://github.com/symgraph/IDAssist/commits?author=jtang613)<br>[Add OpenWebUI API path provider](https://github.com/symgraph/IDAssist/commit/7b9e2dea6229a91ec79994a8178ba0eebf4fa0ee)<br>2 months agoJun 28, 2026<br>[7b9e2de](https://github.com/symgraph/IDAssist/commit/7b9e2dea6229a91ec79994a8178ba0eebf4fa0ee) · 2 months agoJun 28, 2026<br>## History<br>[72 Commits](https://github.com/symgraph/IDAssist/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/symgraph/IDAssist/commits/master/) 72 Commits |
| [docs](https://github.com/symgraph/IDAssist/tree/master/docs "docs") | [docs](https://github.com/symgraph/IDAssist/tree/master/docs "docs") | [feat(bedrock): add native AWS Bedrock provider via Converse API](https://github.com/symgraph/IDAssist/commit/574fc78ad445436aaa0fd3de77806660aee862dc "feat(bedrock): add native AWS Bedrock provider via Converse API  Implements a first-class Bedrock provider using boto3 bedrock-runtime Converse/ConverseStream API, independent of the LiteLLM proxy path.  - New ProviderType.BEDROCK enum with proper capabilities - BedrockProvider class with chat, streaming, tool use, error handling - BedrockProviderFactory registered with graceful fallback - Migration adds aws_region, aws_profile, aws_access_key_id,   aws_secret_access_key columns to llm_providers table - Settings UI with AWS credential fields (hidden unless bedrock type) - boto3 dependency - 40 unit tests (enum, factory, migration, provider, settings) - Documentation updated with setup guide and pricing/quotas notice  Closes #13") | 3 months agoMay 16, 2026 |
| [src](https://github.com/symgraph/IDAssist/tree/master/src "src") | [src](https://github.com/symgraph/IDAssist/tree/master/src "src") | [Add OpenWebUI API path provider](https://github.com/symgraph/IDAssist/commit/7b9e2dea6229a91ec79994a8178ba0eebf4fa0ee "Add OpenWebUI API path provider") | 2 months agoJun 28, 2026 |
| [tests](https://github.com/symgraph/IDAssist/tree/master/tests "tests") | [tests](https://github.com/symgraph/IDAssist/tree/master/tests "tests") | [Add OpenWebUI API path provider](https://github.com/symgraph/IDAssist/commit/7b9e2dea6229a91ec79994a8178ba0eebf4fa0ee "Add OpenWebUI API path provider") | 2 months agoJun 28, 2026 |
| [.gitignore](https://github.com/symgraph/IDAssist/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/symgraph/IDAssist/blob/master/.gitignore ".gitignore") | [Initial commit.](https://github.com/symgraph/IDAssist/commit/6ae6172c37f6e1b14cd2410cab9d95b65e68ef33 "Initial commit.") | 6 months agoFeb 26, 2026 |
| [LICENSE](https://github.com/symgraph/IDAssist/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/symgraph/IDAssist/blob/master/LICENSE "LICENSE") | [Add MIT License.](https://github.com/symgraph/IDAssist/commit/63925699582eefd3c1a20d818115dc21d581f68d "Add MIT License.") | 6 months agoFeb 26, 2026 |
| [README.md](https://github.com/symgraph/IDAssist/blob/master/README.md "README.md") | [README.md](https://github.com/symgraph/IDAssist/blob/master/README.md "README.md") | [feat(bedrock): add native AWS Bedrock provider via Converse API](https://github.com/symgraph/IDAssist/commit/574fc78ad445436aaa0fd3de77806660aee862dc "feat(bedrock): add native AWS Bedrock provider via Converse API  Implements a first-class Bedrock provider using boto3 bedrock-runtime Converse/ConverseStream API, independent of the LiteLLM proxy path.  - New ProviderType.BEDROCK enum with proper capabilities - BedrockProvider class with chat, streaming, tool use, error handling - BedrockProviderFactory registered with graceful fallback - Migration adds aws_region, aws_profile, aws_access_key_id,   aws_secret_access_key columns to llm_providers table - Settings UI with AWS credential fields (hidden unless bedrock type) - boto3 dependency - 40 unit tests (enum, factory, migration, provider, settings) - Documentation updated with setup guide and pricing/quotas notice  Closes #13") | 3 months agoMay 16, 2026 |
| [ida-plugin.json](https://github.com/symgraph/IDAssist/blob/master/ida-plugin.json "ida-plugin.json") | [ida-plugin.json](https://github.com/symgraph/IDAssist/blob/master/ida-plugin.json "ida-plugin.json") | [Add ReAct plan approval step.](https://github.com/symgraph/IDAssist/commit/44c0c16fdb22cb21d61c363f12c22c03022061c1 "Add ReAct plan approval step.") | 3 months agoMay 25, 2026 |
| [idassist\_plugin.py](https://github.com/symgraph/IDAssist/blob/master/idassist_plugin.py "idassist_plugin.py") | [idassist\_plugin.py](https://github.com/symgraph/IDAssist/blob/master/idassist_plugin.py "idassist_plugin.py") | [Version fix.](https://github.com/symgraph/IDAssist/commit/eda5f78c7e316f0f9f84a4fb2df3e73889124ce2 "Version fix.") | 5 months agoMar 14, 2026 |
| [requirements.txt](https://github.com/symgraph/IDAssist/blob/master/requirements.txt "requirements.txt") | [requirements.txt](https://github.com/symgraph/IDAssist/blob/master/requirements.txt "requirements.txt") | [feat(bedrock): add native AWS Bedrock provider via Converse API](https://github.com/symgraph/IDAssist/commit/574fc78ad445436aaa0fd3de77806660aee862dc "feat(bedrock): add native AWS Bedrock provider via Converse API  Implements a first-class Bedrock provider using boto3 bedrock-runtime Converse/ConverseStream API, independent of the LiteLLM proxy path.  - New ProviderType.BEDROCK enum with proper capabilities - BedrockProvider class with chat, streaming, tool use, error handling - BedrockProviderFactory registered with graceful fallback - Migration adds aws_region, aws_profile, aws_access_key_id,   aws_secret_access_key columns to llm_providers table - Settings UI with AWS credential fields (hidden unless bedrock type) - boto3 dependency - 40 unit tests (enum, factory, migration, provider, settings) - Documentation updated with setup guide and pricing/quotas notice  Closes #13") | 3 months agoMay 16, 2026 |
| View all files |

## Repository files navigation

# IDAssist

[Permalink: IDAssist](https://github.com/symgraph/IDAssist#idassist)

_AI-Powered Reverse Engineering Plugin for IDA Pro_

**Author:** Jason Tang

## Description

[Permalink: Description](https://github.com/symgraph/IDAssist#description)

IDAssist is an IDA Pro plugin that integrates LLM-powered analysis directly into IDA's interface, providing AI-assisted binary reverse engineering through configurable LLM providers, semantic knowledge graphs, RAG document search, and supports a wide diversity of LLM providers.

Built with Python and PySide6, IDAssist runs as a dockable panel inside IDA Pro 9.0+ and communicates with LLM providers (OpenAI, Anthropic, Ollama, LiteLLM, and more) to analyze functions, suggest renames, answer questions about code, and build a searchable knowledge graph of an entire binary.

[![Screenshot](https://github.com/symgraph/IDAssist/raw/master/docs/screenshots/slideshow.gif)](https://github.com/symgraph/IDAssist/blob/master/docs/screenshots/slideshow.gif)[![Screenshot](https://github.com/symgraph/IDAssist/raw/master/docs/screenshots/slideshow.gif)](https://github.com/symgraph/IDAssist/blob/master/docs/screenshots/slideshow.gif)[Open Screenshot in new window](https://github.com/symgraph/IDAssist/blob/master/docs/screenshots/slideshow.gif)

## Core Features

[Permalink: Core Features](https://github.com/symgraph/IDAssist#core-features)

**Function Explanation** — Generate detailed natural-language explanations of decompiled functions with automatic security analysis including risk level, activity profile, security flags, and API detection.

**Interactive Query Chat** — Ask questions about the binary with persistent chat history. Use context macros (`#func`, `#addr`, `#line`, `#range`) to inject function code, addresses, or disassembly ranges into queries.

**Automated Actions** — AI-powered rename suggestions for functions, variables, and types. Review proposed changes in a table with confidence scores, then apply selected actions back to the IDB.

**Semantic Knowledge Graph** — Build and explore a knowledge graph of the binary's functions, call relationships, data flows, and security characteristics. Includes visual graph rendering, semantic search, and community detection.

**RAG Document Search** — Upload reference documents (`.txt`, `.md`, `.rst`, `.pdf`) and use them as context during LLM queries. Supports hybrid text+vector search via Whoosh indexing.

**SymGraph Integration** — Push and pull function names, variable names, types, and graph data to the SymGraph collaborative platform. Includes a multi-step wizard with conflict resolution for pulls.

**Settings Management** — Configure multiple LLM and MCP providers, manage SymGraph API credentials, customize the system prompt, and set database paths.

## Advanced Capabilities

[Permalink: Advanced Capabilities](https://github.com/symgraph/IDAssist#advanced-capabilities)

### ReAct Agent

[Permalink: ReAct Agent](https://github.com/symgraph/IDAssist#react-agent)

The Query tab supports an autonomous ReAct (Reasoning + Acting) agent mode. When enabled, the LLM plans an investigation strategy, executes tools to gather information, reflects on findings, and synthesizes a comprehensive answer — all automatically across multiple reasoning rounds.

### Extended Thinking

[Permalink: Extended Thinking](https://github.com/symgraph/IDAssist#extended-thinking)

Configure reasoning effort levels to control how much the LLM "thinks" before responding:

| Level | Thinking Budget | Best For |
| --- | --- | --- |
| None | Disabled | Fast, simple queries |
| Low | ~2K tokens | Straightforward analysis |
| Medium | ~10K tokens | Moderate complexity |
| High | ~25K tokens | Deep analysis, complex code |

### MCP Integration

[Permalink: MCP Integration](https://github.com/symgraph/IDAssist#mcp-integration)

IDAssist can connect to external MCP servers for tool-augmented LLM interactions where the model can programmatically inspect functions, read disassembly, query cross-references, and modify the IDB during reasoning. Both URL-based MCP servers (`SSE` or `Streamable HTTP`) and stdio-based MCP servers started from a local CLI command are supported. IDAssist also provides built-in internal tools for function calling without requiring an external MCP server.

### Function Calling

[Permalink: Function Calling](https://github.com/symgraph/IDAssist#function-calling)

LLM providers with tool-calling support can invoke IDA analysis functions mid-conversation, enabling iterative investigation without manual intervention.

### RLHF Feedback

[Permalink: RLHF Feedback](https://github.com/symgraph/IDAssist#rlhf-feedback)

Provide thumbs-up/thumbs-down feedback on explanations and query responses. Feedback is stored locally and can be used to improve prompt engineering and model selection.

## Architecture

[Permalink: Architecture](https://github.com/symgraph/IDAssist#architecture)

IDAssist follows an MVC (Model-View-Controller) pattern:

- **Views** (`src/views/`) — PySide6 tab widgets that emit signals on user interaction
- **Controllers** (`src/controllers/`) — Connect view signals to service calls, manage state
- **Services** (`src/services/`) — Business logic, LLM providers, database access, graph analysis
- **Internal Tools** (`src/services/internal_tools.py`) — IDA-specific tool definitions for LLM function calling
- **Graph Tools** (`src/services/graphrag/graphrag_tools.py`) — Semantic graph read/write tools for LLM interaction

Key design principles:

- All IDA API calls execute on the main thread via `execute_on_main_thread()`
- LLM responses stream incrementally to the UI
- Local SQLite databases for persistence (no external database required)
- Singleton service registry with thread-safe initialization

## Quick Start

[Permalink: Quick Start](https://github.com/symgraph/IDAssist#quick-start)

1. **Install the plugin** (recommended — IDA Plugin Manager):



```
hcli plugin install idassist
```







This automatically installs the plugin and its Python dependencies into IDA's environment.

2. **Or install manually** (from release tarball):

Download the latest release zip from [GitHub Releases](https://github.com/jtang613/IDAssist/releases) and extract it into your IDA plugins directory:

**Linux / macOS:**



```
unzip IDAssist-*.zip -d ~/.idapro/plugins/
```







**Windows:**
Extract the zip into `%APPDATA%\Hex-Rays\IDA Pro\plugins\`.

Then install dependencies using **IDA's bundled Python** (not your system Python):

**Linux / macOS:**



```
<IDA_INSTALL_DIR>/python3/bin/pip3 install -r ~/.idapro/plugins/IDAssist/requirements.txt
```







**Windows:**



```
"<IDA_INSTALL_DIR>\python3\python.exe" -m pip install -r "%APPDATA%\Hex-Rays\IDA Pro\plugins\IDAssist\requirements.txt"
```








> Replace `<IDA_INSTALL_DIR>` with your IDA Pro installation path (e.g., `/opt/idapro-9.0` or `C:\Program Files\IDA Pro 9.0`).
>
> **Tip:** You can also set the `IDAUSR` environment variable to a custom directory containing a `plugins/` subdirectory.

3. **Open IDAssist:** Launch IDA Pro, open a binary, and press `Ctrl+Shift+A` (or Edit > Plugins > IDAssist).

4. **Configure a provider:** Go to the Settings tab, click **Add** under LLM Providers, and configure your preferred provider.

5. **Analyze a function:** Navigate to any function, click the **Explain** tab, and press **Explain Function**.


For detailed setup instructions, see [Getting Started](https://github.com/symgraph/IDAssist/blob/master/docs/getting-started.md).

## LLM Provider Setup

[Permalink: LLM Provider Setup](https://github.com/symgraph/IDAssist#llm-provider-setup)

IDAssist supports the following provider types:

| Type | Auth Method | Notes |
| --- | --- | --- |
| `anthropic_platform` | API Key | Anthropic API direct |
| `anthropic_oauth` | OAuth (browser) | Browser-based authentication |
| `anthropic_claude_cli` | Local CLI | Uses the `claude` CLI binary |
| `bedrock` | AWS Credentials | Direct AWS Bedrock Converse API |
| `openai_platform` | API Key | OpenAI API direct |
| `openai_oauth` | OAuth (browser) | Browser-based authentication |
| `ollama` | None (local) | Self-hosted models |
| `litellm` | Proxy URL | Multi-provider proxy |

### Recommended Models

[Permalink: Recommended Models](https://github.com/symgraph/IDAssist#recommended-models)

| Provider | Model | Strengths |
| --- | --- | --- |
| Anthropic | `claude-sonnet-4-6` | Strong code analysis, extended thinking |
| OpenAI | `gpt-5.3-codex` | Fast, good general analysis |
| Ollama | `qwen2.5-coder:32b` | Local, no API key needed |

## Using the Semantic Graph

[Permalink: Using the Semantic Graph](https://github.com/symgraph/IDAssist#using-the-semantic-graph)

The Semantic Graph tab provides a knowledge graph of the binary:

1. **ReIndex Binary** — Extracts function structure, call graph, and cross-references
2. **Semantic Analysis** — Generates LLM summaries for each function
3. **Security Analysis** — Detects vulnerability patterns and security-relevant APIs
4. **Network Flow** — Tracks network operations across the call graph
5. **Community Detection** — Groups related functions into modules

Explore the graph via the **List View** (callers, callees, edges, flags), **Visual Graph** (interactive node diagram with N-hop expansion), or **Search** (7 query types including semantic search, similar functions, and call context).

## Context Menu Actions

[Permalink: Context Menu Actions](https://github.com/symgraph/IDAssist#context-menu-actions)

Right-click in any Disassembly or Pseudocode view to access:

| Action | Hotkey | Effect |
| --- | --- | --- |
| Explain Function | `Ctrl+Shift+E` | Opens Explain tab and generates explanation |
| Ask About Selection | `Ctrl+Shift+Q` | Opens Query tab with `#func` context |
| Rename Suggestions | — | Opens Actions tab and generates suggestions |

## Requirements

[Permalink: Requirements](https://github.com/symgraph/IDAssist#requirements)

- **IDA Pro 9.0+** with Python 3 and PySide6
- **Hex-Rays Decompiler** (recommended for pseudocode features)
- Python packages listed in `requirements.txt`

## Documentation

[Permalink: Documentation](https://github.com/symgraph/IDAssist#documentation)

- [Documentation Index](https://github.com/symgraph/IDAssist/blob/master/docs/index.md)
- [Getting Started](https://github.com/symgraph/IDAssist/blob/master/docs/getting-started.md)
- Tab References: [Explain](https://github.com/symgraph/IDAssist/blob/master/docs/tabs/explain-tab.md) \| [Query](https://github.com/symgraph/IDAssist/blob/master/docs/tabs/query-tab.md) \| [Actions](https://github.com/symgraph/IDAssist/blob/master/docs/tabs/actions-tab.md) \| [Semantic Graph](https://github.com/symgraph/IDAssist/blob/master/docs/tabs/semantic-graph-tab.md) \| [RAG](https://github.com/symgraph/IDAssist/blob/master/docs/tabs/rag-tab.md) \| [Settings](https://github.com/symgraph/IDAssist/blob/master/docs/tabs/settings-tab.md)
- Workflows: [Explain](https://github.com/symgraph/IDAssist/blob/master/docs/workflows/explain-workflow.md) \| [Query](https://github.com/symgraph/IDAssist/blob/master/docs/workflows/query-workflow.md) \| [Semantic Graph](https://github.com/symgraph/IDAssist/blob/master/docs/workflows/semantic-graph-workflow.md)

## Homepage

[Permalink: Homepage](https://github.com/symgraph/IDAssist#homepage)

[https://symgraph.ai](https://symgraph.ai/)

## License

[Permalink: License](https://github.com/symgraph/IDAssist#license)

See LICENSE file for details.

## About

AI-Powered Reverse Engineering Plugin for IDA Pro

### Topics

[ida-plugin](https://github.com/topics/ida-plugin) [ida-plugins](https://github.com/topics/ida-plugins) [idapro](https://github.com/topics/idapro) [llm](https://github.com/topics/llm)

### Resources

[Readme](https://github.com/symgraph/IDAssist#readme-ov-file)

[MIT license](https://github.com/symgraph/IDAssist#MIT-1-ov-file)

[Activity](https://github.com/symgraph/IDAssist/activity)

### Stars

**706** stars

### Watchers

**6** watching

### Forks

[**73** forks](https://github.com/symgraph/IDAssist/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fsymgraph%2FIDAssist&report=symgraph+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.