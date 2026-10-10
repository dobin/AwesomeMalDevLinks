# https://github.com/dmdhrumilmistry/security-harness

[Skip to content](https://github.com/dmdhrumilmistry/security-harness#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/dmdhrumilmistry/security-harness) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/dmdhrumilmistry/security-harness) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/dmdhrumilmistry/security-harness) to refresh your session.Dismiss alert

{{ message }}

main

[**2** Branches](https://github.com/dmdhrumilmistry/security-harness/branches) [**1** Tag](https://github.com/dmdhrumilmistry/security-harness/tags)

[Go to Branches page](https://github.com/dmdhrumilmistry/security-harness/branches)[Go to Tags page](https://github.com/dmdhrumilmistry/security-harness/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![dmdhrumilmistry](https://avatars.githubusercontent.com/u/56185972?v=4&size=40)](https://github.com/dmdhrumilmistry)[dmdhrumilmistry](https://github.com/dmdhrumilmistry/security-harness/commits?author=dmdhrumilmistry)

[Merge pull request](https://github.com/dmdhrumilmistry/security-harness/commit/68748d52c99e10d09e7709d62fd78375ad8148fc) [#12](https://github.com/dmdhrumilmistry/security-harness/pull/12) [from dmdhrumilmistry/feat/pr-review-incrementa…](https://github.com/dmdhrumilmistry/security-harness/commit/68748d52c99e10d09e7709d62fd78375ad8148fc)

Open commit details

2 weeks agoSep 27, 2026

[68748d5](https://github.com/dmdhrumilmistry/security-harness/commit/68748d52c99e10d09e7709d62fd78375ad8148fc) · 2 weeks agoSep 27, 2026

## History

[34 Commits](https://github.com/dmdhrumilmistry/security-harness/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/dmdhrumilmistry/security-harness/commits/main/) 34 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [.claude-plugin](https://github.com/dmdhrumilmistry/security-harness/tree/main/.claude-plugin ".claude-plugin") | [.claude-plugin](https://github.com/dmdhrumilmistry/security-harness/tree/main/.claude-plugin ".claude-plugin") | [feat(dist): package for Gemini CLI, opencode and Codex; polish manifests](https://github.com/dmdhrumilmistry/security-harness/commit/7306646b3ed52db3a70dddea48c2ca1c9af57a19 "feat(dist): package for Gemini CLI, opencode and Codex; polish manifests  Makes the harness installable outside Claude Code without forking the skills.  Gemini CLI: gemini-extension.json and GEMINI.md at the repo root. Gemini loads an extension's skills from the extension root, while the Claude Code plugin format fixes them under the plugin directory, so scripts/sync-agent-skills.py generates a root skills/ mirror from the canonical copy. It has a --check mode for CI, so a stale mirror fails loudly instead of shipping.  opencode and other agentskills.io agents: those discover SKILL.md from .agents/skills, ~/.claude/skills and their own directories, so the script's --install flag writes into whichever the user wants. Codex reads AGENTS.md on its own, already added.  Manifest polish for directory submission: LICENSE (MIT was declared in plugin.json but the file was missing), displayName, repository, category and expanded keywords, plus a plugin-level README.md that the official directory expects. Version aligned at 0.2.0 across marketplace.json, plugin.json and gemini-extension.json.  docs/DISTRIBUTION.md records the per-ecosystem layout and the public listing steps. Notably the Gemini gallery needs no submission form: a public repo, the gemini-cli-extension topic, and a release tag matching the manifest version.  README: multi-agent install instructions, and the knowledge-base section rewritten to describe the two-stage pipeline. The old text contradicted itself, claiming both that the PR is auto-merged on approval and that there is no auto-merge.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 26, 2026 |
| [.github](https://github.com/dmdhrumilmistry/security-harness/tree/main/.github ".github") | [.github](https://github.com/dmdhrumilmistry/security-harness/tree/main/.github ".github") | [refactor(pr-review): ship it as a local dev skill, drop this repo's o…](https://github.com/dmdhrumilmistry/security-harness/commit/294ac0b8cc7e9f7b34f6c5d4106115ea004554a3 "refactor(pr-review): ship it as a local dev skill, drop this repo's own CI  sh-pr-review is meant to be run by a developer on their own machine against a PR in whatever repo they are working in. It was also wired into this repository's CI, which was scope I added and nobody asked for. That CI is what produced the red security/pr-review status on the last two PRs, and debugging it had nothing to do with the skill being useful to anyone.    - Remove .github/workflows/security-pr-review.yml. The skill is the     deliverable; running it here proves nothing a local run does not.   - Remove the execution_file output from the ai-agent composite action, added     only to debug that workflow. The github_token input stays: it is a real fix     for using claude-code-action in any pull_request workflow, and the template     below depends on it.   - Turn the CI section of pr-review-mapping.md into a self-contained     copy-paste workflow for the reader's own repo, rather than a pointer at a     file in ours. It carries the github_token fix and a note about the     fail-safe, which are the two things that stop a required check being     deleted a week later.  The skill itself gains the part it was actually missing, which is everything about being run by a human somewhere else:    - Check repo permissions before spending a single subagent. Reviewing     someone else's project now says up front that posting will 403, instead of     discovering it at Phase 7 after ten minutes of analysis.   - Check whether .security-harness/ is ignored in the target repo, and offer     .git/info/exclude so the run tree never dirties someone's PR.   - State plainly that the run directory lands in the target repo, not here.   - Reframe --ci as CI-only, since it removes the confirmation gate, which is     the main safety property when a human is driving.  Docs now lead with \"run it on your own machine, in any repo gh can see\", and treat automating it as a later, separate decision.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 27, 2026 |
| [docs](https://github.com/dmdhrumilmistry/security-harness/tree/main/docs "docs") | [docs](https://github.com/dmdhrumilmistry/security-harness/tree/main/docs "docs") | [fix: make the bundled scripts work on Linux](https://github.com/dmdhrumilmistry/security-harness/commit/d30a52ed598689a72ec9ad204b08048b6c4278f9 "fix: make the bundled scripts work on Linux  Asked \"what about linux\" and found three things, one of them self-inflicted.  1. `python` does not exist on a default Debian or Ubuntu box. Those ship    `python3` only, and `python` is absent unless python-is-python3 is    installed. Every doc and every skill instruction said `python <script>`, so    the cache, the metrics and the posting step would all have failed on the    most common Linux setup. The skill now resolves    PY=\"$(command -v python3 || command -v python)\" once in Phase 0, before    anything needs it, and stops with a clear message if neither exists. Docs    use python3.  2. The scripts carried a #!/usr/bin/env python3 shebang but were committed    mode 100644, so ./scripts/sh-metrics.py was permission denied on Linux and    macOS. Now 100755, which git preserves, so direct execution works.  3. __pycache__/*.pyc from my own test runs had been swept into the repo by    git add -A. Removed, and .gitignore now covers bytecode and the    .security-harness run trees that a review writes into a target repo.  Also fixed while in there: four literal backslash-n sequences left in the skill by an earlier heredoc edit, which would have been copied into a shell verbatim, and $PY being used in Phase 0 while defined in Phase 1.  Linux paths were already correct, XDG_CACHE_HOME and XDG_DATA_HOME with ~/.cache and ~/.local/share fallbacks, but the docs listed them as \"other\" under Windows and macOS. Linux is now a named first row with its defaults spelled out.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 27, 2026 |
| [plugins/security-harness](https://github.com/dmdhrumilmistry/security-harness/tree/main/plugins/security-harness "This path skips through empty directories") | [plugins/security-harness](https://github.com/dmdhrumilmistry/security-harness/tree/main/plugins/security-harness "This path skips through empty directories") | [fix: make the bundled scripts work on Linux](https://github.com/dmdhrumilmistry/security-harness/commit/d30a52ed598689a72ec9ad204b08048b6c4278f9 "fix: make the bundled scripts work on Linux  Asked \"what about linux\" and found three things, one of them self-inflicted.  1. `python` does not exist on a default Debian or Ubuntu box. Those ship    `python3` only, and `python` is absent unless python-is-python3 is    installed. Every doc and every skill instruction said `python <script>`, so    the cache, the metrics and the posting step would all have failed on the    most common Linux setup. The skill now resolves    PY=\"$(command -v python3 || command -v python)\" once in Phase 0, before    anything needs it, and stops with a clear message if neither exists. Docs    use python3.  2. The scripts carried a #!/usr/bin/env python3 shebang but were committed    mode 100644, so ./scripts/sh-metrics.py was permission denied on Linux and    macOS. Now 100755, which git preserves, so direct execution works.  3. __pycache__/*.pyc from my own test runs had been swept into the repo by    git add -A. Removed, and .gitignore now covers bytecode and the    .security-harness run trees that a review writes into a target repo.  Also fixed while in there: four literal backslash-n sequences left in the skill by an earlier heredoc edit, which would have been copied into a shell verbatim, and $PY being used in Phase 0 while defined in Phase 1.  Linux paths were already correct, XDG_CACHE_HOME and XDG_DATA_HOME with ~/.cache and ~/.local/share fallbacks, but the docs listed them as \"other\" under Windows and macOS. Linux is now a named first row with its defaults spelled out.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 27, 2026 |
| [scripts](https://github.com/dmdhrumilmistry/security-harness/tree/main/scripts "scripts") | [scripts](https://github.com/dmdhrumilmistry/security-harness/tree/main/scripts "scripts") | [fix(sync): preserve the exec bit through the generated mirror](https://github.com/dmdhrumilmistry/security-harness/commit/63518cfa698f0c2e5940ad5c33a0a946d174aa88 "fix(sync): preserve the exec bit through the generated mirror  The canonical scripts were marked 100755 but the mirror under skills/ came out 100644, so anyone installing the Gemini extension or copying into ~/.agents/skills got scripts that could not be executed despite carrying a python3 shebang.  Cause: Windows has no exec bit, so a mirror regenerated there is committed 0644 regardless of the source mode. The sync script now sets it explicitly on every bundled .py and .sh after copying, which means the mirror cannot drift depending on which platform regenerated it.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 27, 2026 |
| [skills](https://github.com/dmdhrumilmistry/security-harness/tree/main/skills "skills") | [skills](https://github.com/dmdhrumilmistry/security-harness/tree/main/skills "skills") | [fix(sync): preserve the exec bit through the generated mirror](https://github.com/dmdhrumilmistry/security-harness/commit/63518cfa698f0c2e5940ad5c33a0a946d174aa88 "fix(sync): preserve the exec bit through the generated mirror  The canonical scripts were marked 100755 but the mirror under skills/ came out 100644, so anyone installing the Gemini extension or copying into ~/.agents/skills got scripts that could not be executed despite carrying a python3 shebang.  Cause: Windows has no exec bit, so a mirror regenerated there is committed 0644 regardless of the source mode. The sync script now sets it explicitly on every bundled .py and .sh after copying, which means the mirror cannot drift depending on which platform regenerated it.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 27, 2026 |
| [.gitignore](https://github.com/dmdhrumilmistry/security-harness/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/dmdhrumilmistry/security-harness/blob/main/.gitignore ".gitignore") | [fix: make the bundled scripts work on Linux](https://github.com/dmdhrumilmistry/security-harness/commit/d30a52ed598689a72ec9ad204b08048b6c4278f9 "fix: make the bundled scripts work on Linux  Asked \"what about linux\" and found three things, one of them self-inflicted.  1. `python` does not exist on a default Debian or Ubuntu box. Those ship    `python3` only, and `python` is absent unless python-is-python3 is    installed. Every doc and every skill instruction said `python <script>`, so    the cache, the metrics and the posting step would all have failed on the    most common Linux setup. The skill now resolves    PY=\"$(command -v python3 || command -v python)\" once in Phase 0, before    anything needs it, and stops with a clear message if neither exists. Docs    use python3.  2. The scripts carried a #!/usr/bin/env python3 shebang but were committed    mode 100644, so ./scripts/sh-metrics.py was permission denied on Linux and    macOS. Now 100755, which git preserves, so direct execution works.  3. __pycache__/*.pyc from my own test runs had been swept into the repo by    git add -A. Removed, and .gitignore now covers bytecode and the    .security-harness run trees that a review writes into a target repo.  Also fixed while in there: four literal backslash-n sequences left in the skill by an earlier heredoc edit, which would have been copied into a shell verbatim, and $PY being used in Phase 0 while defined in Phase 1.  Linux paths were already correct, XDG_CACHE_HOME and XDG_DATA_HOME with ~/.cache and ~/.local/share fallbacks, but the docs listed them as \"other\" under Windows and macOS. Linux is now a named first row with its defaults spelled out.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 27, 2026 |
| [AGENTS.md](https://github.com/dmdhrumilmistry/security-harness/blob/main/AGENTS.md "AGENTS.md") | [AGENTS.md](https://github.com/dmdhrumilmistry/security-harness/blob/main/AGENTS.md "AGENTS.md") | [fix: make the bundled scripts work on Linux](https://github.com/dmdhrumilmistry/security-harness/commit/d30a52ed598689a72ec9ad204b08048b6c4278f9 "fix: make the bundled scripts work on Linux  Asked \"what about linux\" and found three things, one of them self-inflicted.  1. `python` does not exist on a default Debian or Ubuntu box. Those ship    `python3` only, and `python` is absent unless python-is-python3 is    installed. Every doc and every skill instruction said `python <script>`, so    the cache, the metrics and the posting step would all have failed on the    most common Linux setup. The skill now resolves    PY=\"$(command -v python3 || command -v python)\" once in Phase 0, before    anything needs it, and stops with a clear message if neither exists. Docs    use python3.  2. The scripts carried a #!/usr/bin/env python3 shebang but were committed    mode 100644, so ./scripts/sh-metrics.py was permission denied on Linux and    macOS. Now 100755, which git preserves, so direct execution works.  3. __pycache__/*.pyc from my own test runs had been swept into the repo by    git add -A. Removed, and .gitignore now covers bytecode and the    .security-harness run trees that a review writes into a target repo.  Also fixed while in there: four literal backslash-n sequences left in the skill by an earlier heredoc edit, which would have been copied into a shell verbatim, and $PY being used in Phase 0 while defined in Phase 1.  Linux paths were already correct, XDG_CACHE_HOME and XDG_DATA_HOME with ~/.cache and ~/.local/share fallbacks, but the docs listed them as \"other\" under Windows and macOS. Linux is now a named first row with its defaults spelled out.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 27, 2026 |
| [CLAUDE.md](https://github.com/dmdhrumilmistry/security-harness/blob/main/CLAUDE.md "CLAUDE.md") | [CLAUDE.md](https://github.com/dmdhrumilmistry/security-harness/blob/main/CLAUDE.md "CLAUDE.md") | [style: replace em dashes with hyphens and document the rule](https://github.com/dmdhrumilmistry/security-harness/commit/e752ceec450cc8b052e8b259bdc31fbe69e8bed0 "style: replace em dashes with hyphens and document the rule  Swept 209 em/en dashes out of the repo and replaced them with plain ASCII hyphens. The character replacement is behaviour-preserving: a spaced em dash becomes a spaced hyphen, an unspaced one becomes a bare hyphen.  Added AGENTS.md as the shared style and layout contract for every agent that works here (Claude Code, Codex, Gemini CLI, opencode), with CLAUDE.md pointing at it so there is one source of truth rather than per-agent copies that drift.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 26, 2026 |
| [GEMINI.md](https://github.com/dmdhrumilmistry/security-harness/blob/main/GEMINI.md "GEMINI.md") | [GEMINI.md](https://github.com/dmdhrumilmistry/security-harness/blob/main/GEMINI.md "GEMINI.md") | [feat(dist): package for Gemini CLI, opencode and Codex; polish manifests](https://github.com/dmdhrumilmistry/security-harness/commit/7306646b3ed52db3a70dddea48c2ca1c9af57a19 "feat(dist): package for Gemini CLI, opencode and Codex; polish manifests  Makes the harness installable outside Claude Code without forking the skills.  Gemini CLI: gemini-extension.json and GEMINI.md at the repo root. Gemini loads an extension's skills from the extension root, while the Claude Code plugin format fixes them under the plugin directory, so scripts/sync-agent-skills.py generates a root skills/ mirror from the canonical copy. It has a --check mode for CI, so a stale mirror fails loudly instead of shipping.  opencode and other agentskills.io agents: those discover SKILL.md from .agents/skills, ~/.claude/skills and their own directories, so the script's --install flag writes into whichever the user wants. Codex reads AGENTS.md on its own, already added.  Manifest polish for directory submission: LICENSE (MIT was declared in plugin.json but the file was missing), displayName, repository, category and expanded keywords, plus a plugin-level README.md that the official directory expects. Version aligned at 0.2.0 across marketplace.json, plugin.json and gemini-extension.json.  docs/DISTRIBUTION.md records the per-ecosystem layout and the public listing steps. Notably the Gemini gallery needs no submission form: a public repo, the gemini-cli-extension topic, and a release tag matching the manifest version.  README: multi-agent install instructions, and the knowledge-base section rewritten to describe the two-stage pipeline. The old text contradicted itself, claiming both that the PR is auto-merged on approval and that there is no auto-merge.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 26, 2026 |
| [LICENSE](https://github.com/dmdhrumilmistry/security-harness/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/dmdhrumilmistry/security-harness/blob/main/LICENSE "LICENSE") | [feat(dist): package for Gemini CLI, opencode and Codex; polish manifests](https://github.com/dmdhrumilmistry/security-harness/commit/7306646b3ed52db3a70dddea48c2ca1c9af57a19 "feat(dist): package for Gemini CLI, opencode and Codex; polish manifests  Makes the harness installable outside Claude Code without forking the skills.  Gemini CLI: gemini-extension.json and GEMINI.md at the repo root. Gemini loads an extension's skills from the extension root, while the Claude Code plugin format fixes them under the plugin directory, so scripts/sync-agent-skills.py generates a root skills/ mirror from the canonical copy. It has a --check mode for CI, so a stale mirror fails loudly instead of shipping.  opencode and other agentskills.io agents: those discover SKILL.md from .agents/skills, ~/.claude/skills and their own directories, so the script's --install flag writes into whichever the user wants. Codex reads AGENTS.md on its own, already added.  Manifest polish for directory submission: LICENSE (MIT was declared in plugin.json but the file was missing), displayName, repository, category and expanded keywords, plus a plugin-level README.md that the official directory expects. Version aligned at 0.2.0 across marketplace.json, plugin.json and gemini-extension.json.  docs/DISTRIBUTION.md records the per-ecosystem layout and the public listing steps. Notably the Gemini gallery needs no submission form: a public repo, the gemini-cli-extension topic, and a release tag matching the manifest version.  README: multi-agent install instructions, and the knowledge-base section rewritten to describe the two-stage pipeline. The old text contradicted itself, claiming both that the PR is auto-merged on approval and that there is no auto-merge.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 26, 2026 |
| [README.md](https://github.com/dmdhrumilmistry/security-harness/blob/main/README.md "README.md") | [README.md](https://github.com/dmdhrumilmistry/security-harness/blob/main/README.md "README.md") | [fix: make the bundled scripts work on Linux](https://github.com/dmdhrumilmistry/security-harness/commit/d30a52ed598689a72ec9ad204b08048b6c4278f9 "fix: make the bundled scripts work on Linux  Asked \"what about linux\" and found three things, one of them self-inflicted.  1. `python` does not exist on a default Debian or Ubuntu box. Those ship    `python3` only, and `python` is absent unless python-is-python3 is    installed. Every doc and every skill instruction said `python <script>`, so    the cache, the metrics and the posting step would all have failed on the    most common Linux setup. The skill now resolves    PY=\"$(command -v python3 || command -v python)\" once in Phase 0, before    anything needs it, and stops with a clear message if neither exists. Docs    use python3.  2. The scripts carried a #!/usr/bin/env python3 shebang but were committed    mode 100644, so ./scripts/sh-metrics.py was permission denied on Linux and    macOS. Now 100755, which git preserves, so direct execution works.  3. __pycache__/*.pyc from my own test runs had been swept into the repo by    git add -A. Removed, and .gitignore now covers bytecode and the    .security-harness run trees that a review writes into a target repo.  Also fixed while in there: four literal backslash-n sequences left in the skill by an earlier heredoc edit, which would have been copied into a shell verbatim, and $PY being used in Phase 0 while defined in Phase 1.  Linux paths were already correct, XDG_CACHE_HOME and XDG_DATA_HOME with ~/.cache and ~/.local/share fallbacks, but the docs listed them as \"other\" under Windows and macOS. Linux is now a named first row with its defaults spelled out.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 27, 2026 |
| [gemini-extension.json](https://github.com/dmdhrumilmistry/security-harness/blob/main/gemini-extension.json "gemini-extension.json") | [gemini-extension.json](https://github.com/dmdhrumilmistry/security-harness/blob/main/gemini-extension.json "gemini-extension.json") | [feat(dist): package for Gemini CLI, opencode and Codex; polish manifests](https://github.com/dmdhrumilmistry/security-harness/commit/7306646b3ed52db3a70dddea48c2ca1c9af57a19 "feat(dist): package for Gemini CLI, opencode and Codex; polish manifests  Makes the harness installable outside Claude Code without forking the skills.  Gemini CLI: gemini-extension.json and GEMINI.md at the repo root. Gemini loads an extension's skills from the extension root, while the Claude Code plugin format fixes them under the plugin directory, so scripts/sync-agent-skills.py generates a root skills/ mirror from the canonical copy. It has a --check mode for CI, so a stale mirror fails loudly instead of shipping.  opencode and other agentskills.io agents: those discover SKILL.md from .agents/skills, ~/.claude/skills and their own directories, so the script's --install flag writes into whichever the user wants. Codex reads AGENTS.md on its own, already added.  Manifest polish for directory submission: LICENSE (MIT was declared in plugin.json but the file was missing), displayName, repository, category and expanded keywords, plus a plugin-level README.md that the official directory expects. Version aligned at 0.2.0 across marketplace.json, plugin.json and gemini-extension.json.  docs/DISTRIBUTION.md records the per-ecosystem layout and the public listing steps. Notably the Gemini gallery needs no submission form: a public repo, the gemini-cli-extension topic, and a release tag matching the manifest version.  README: multi-agent install instructions, and the knowledge-base section rewritten to describe the two-stage pipeline. The old text contradicted itself, claiming both that the PR is auto-merged on approval and that there is no auto-merge.  Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>") | 2 weeks agoSep 26, 2026 |
| View all files |

## Repository files navigation

# Security Harness

[Permalink: Security Harness](https://github.com/dmdhrumilmistry/security-harness#security-harness)

A multi-agent **application-security review harness** for Claude Code (and, later, other AI agents). One
router skill dispatches to a full offensive-security pipeline that **maps** a codebase, **hunts**
vulnerabilities with a per-class knowledge base, **chains** findings into escalations, **verifies** real
impact, and **reports** to README / JSON / SARIF / doc / PDF.

> Scope: this harness performs **static** analysis (source review, data-flow tracing, PoC/payload
> construction) on code you own or are authorized to test. It does not attack live third-party systems.

## What's inside

[Permalink: What's inside](https://github.com/dmdhrumilmistry/security-harness#whats-inside)

```
security-harness/                         # a plugin marketplace
└── plugins/security-harness/
    ├── skills/
    │   ├── sh-router            # single entry point - routes any appsec request
    │   ├── sh-security-review   # the pipeline orchestrator (Stages 0-5)
    │   └── sh-kb-*  (15)        # per-vuln-class knowledge bases
    ├── agents/
    │   ├── sh-recon             # map: Graft graph + stack/SBOM/CVE + attack surface
    │   ├── sh-hunter            # find: source→sink hunting, one per class (parallel)
    │   ├── sh-chainer           # escalate: combine findings into attack chains
    │   ├── sh-verifier          # confirm: offensive + seceng + dev verification + PoC
    │   └── sh-reporter          # deliver: README/JSON/SARIF/HTML/PDF/doc
    └── references/              # shared contracts (finding schema, SARIF map, state files, rubrics)
```

### Vulnerability classes covered (the `sh-kb-*` skills)

[Permalink: Vulnerability classes covered (the sh-kb-* skills)](https://github.com/dmdhrumilmistry/security-harness#vulnerability-classes-covered-the-sh-kb--skills)

access-control (IDOR/BOLA/priv-esc) · sqli · xss · ssrf · injection (cmd/code/SSTI/LDAP) · auth (session/JWT)
· deserialization · path-traversal (LFI/RFI) · secrets · csrf · xxe · open-redirect · crypto · race-conditions
· file-upload. Dependency CVEs/SBOM are handled by the recon stage.

## Install

[Permalink: Install](https://github.com/dmdhrumilmistry/security-harness#install)

The harness ships for several agents. Full packaging details and the release
checklist are in [`docs/DISTRIBUTION.md`](https://github.com/dmdhrumilmistry/security-harness/blob/main/docs/DISTRIBUTION.md).

**Claude Code** \- add this repo as a plugin marketplace and install the plugin:

```
/plugin marketplace add dmdhrumilmistry/security-harness
/plugin install security-harness
```

`/plugin marketplace add` accepts any of: a GitHub `owner/repo` (as above), a full git URL
(`https://github.com/dmdhrumilmistry/security-harness.git`), or a local path to a clone
(e.g. `/plugin marketplace add ./security-harness` from the directory containing your checkout).
Then run `/plugin install security-harness` and reload when prompted.

**Gemini CLI** \- a native extension, manifest at the repo root:

```
gemini extensions install https://github.com/dmdhrumilmistry/security-harness
```

**opencode, Codex, or any [agentskills.io](https://agentskills.io/) agent** \- copy the
skills into a discovery directory. Codex additionally picks up `AGENTS.md` on its own:

```
git clone https://github.com/dmdhrumilmistry/security-harness
cd security-harness
python3 scripts/sync-agent-skills.py --install agents     # ~/.agents/skills
python3 scripts/sync-agent-skills.py --install opencode   # ~/.config/opencode/skills
```

**Graft is installed and set up automatically by the pipeline.** Stage 0 runs `npm install -g @nanonets/graft` if it's missing (requires Node/npm), then `graft init <target> --no-agents --no-global`
to register the Graft MCP server and freshness hooks for the target repo. The graph itself (`<target>/graft/`,
auto-gitignored) is built during recon. To pre-install manually: `npm install -g @nanonets/graft`. Graft's
structural build is free and needs no API key; the optional `--deep` LLM pass uses `GRAFT_API_KEY` /
`GRAFT_PROVIDER` / `GRAFT_MODEL` when set.

**The other tools are also auto-installed by Stage 0 when missing** (via whatever package manager is on the
machine - winget/choco/scoop, brew, apt, npm/pip/go - see `references/tooling-setup.md`). Installs are
announced, prefer no-elevation methods, and never block the run: anything that can't be installed is simply
marked unavailable and the pipeline falls back. Stage 0 installs only what fills a missing capability group:

- SBOM: [`syft`](https://github.com/anchore/syft) · CVEs: one of [`grype`](https://github.com/anchore/grype)
(preferred), [`trivy`](https://github.com/aquasecurity/trivy), or [`osv-scanner`](https://github.com/google/osv-scanner)
- Reports: `wkhtmltopdf` or `pandoc` (for PDF/DOCX); otherwise you get `report.html` (or a headless-Chrome PDF).

All of them are optional - the pipeline degrades gracefully to native search + manifest parsing if none install.

## Usage

[Permalink: Usage](https://github.com/dmdhrumilmistry/security-harness#usage)

Invoke the router with a natural-language request:

```
/sh-router full security review of ./api
/sh-router find SQLi and IDOR in src/
/sh-router just map this codebase        # recon only
```

Or call the pipeline directly:

```
/sh-security-review . classes:sqli,access-control,ssrf depth:deep
/sh-security-review . stage:report       # regenerate reports for the latest run
```

### Model & cost control

[Permalink: Model & cost control](https://github.com/dmdhrumilmistry/security-harness#model--cost-control)

Each stage runs on a model matched to its cognitive load, so tokens are spent where discovery quality
actually depends on them and saved on mechanical work. **This is the default - no arguments needed.**

| Stage | Default model |
| --- | --- |
| recon | `sonnet` |
| hunt (per class) | `haiku` for pattern classes (secrets, crypto, open-redirect, csrf) · `sonnet` for source→sink tracing (sqli, xss, ssrf, injection, path-traversal, xxe, file-upload, auth) · `opus` for deep-logic classes (access-control, race-conditions, deserialization) |
| chain | `opus` |
| verify | `opus` (the precision gate - kept strong) |
| report | `haiku` |

Override with the `models:` argument (passed through the router too):

```
/sh-security-review .                         # default tiered map above
/sh-security-review . models:max              # every stage + hunter on opus (max quality, max cost)
/sh-security-review . models:cheap            # aggressive downshift (trades some verify precision)
/sh-security-review . models:verify=opus,hunt=sonnet          # per-stage overrides
/sh-security-review . models:report=sonnet,hunt.pattern=sonnet  # per-hunter-tier override
```

Stages: `setup, recon, hunt, chain, verify, report`. Models: `opus, sonnet, haiku, inherit`. For `hunt`,
a bare model flattens all hunters to it; `hunt.pattern` / `hunt.trace` / `hunt.logic` target one tier.
Other token savers are built in: recon only spawns hunters for classes with real attack surface, hunters
query the Graft graph instead of reading whole files, and `findings.json`/SARIF are generated by a
deterministic script rather than the model.

### Output

[Permalink: Output](https://github.com/dmdhrumilmistry/security-harness#output)

Everything lands under `<target>/.security-harness/<run-id>/`:

- `recon.md`, `codebase-map.json` \- the map (stack, SBOM, CVEs, attack surface).
- `findings.jsonl` → `chains.md` → `verified.jsonl` \- the working state (see `references/state-files.md`).
- `reports/` \- `README.md`, `findings.json`, `results.sarif`, `report.html`, `report.pdf` (\+ `report.docx`).

Each published finding carries a payload, a PoC, the verification verdict, CWE/OWASP ids, CVSS, and a
code-level mitigation.

## Pull request review

[Permalink: Pull request review](https://github.com/dmdhrumilmistry/security-harness#pull-request-review)

`sh-pr-review` reviews a single pull request rather than a whole codebase, posts the
result as inline comments **on the PR itself**, and sets a `security/pr-review` commit
status that branch protection can enforce.

**Run it from your own machine, on any PR you can read.** Install the plugin and ask:

```
review https://github.com/acme/api/pull/128
review PR 42
security review this PR
```

**Paste a PR link** and it reviews that PR in that repository, cloning it to a temporary
directory first, because the hunters read files and not just the patch. Nothing is
written into the repo you are working in.

**Pass a bare number** and it resolves against **the repo you are currently in**, the one
`git remote` points at. Pass nothing and it takes the open PR for your current branch.

Phase 7 prints the findings and the verdict and **asks before posting anything** \- a
decline is a normal outcome, and the payload stays on disk for you to post later.

Before spending any analysis it checks whether you can actually write to the target repo,
so reviewing someone else's project tells you up front that posting will 403 rather than
discovering it ten minutes in.

Three properties make it usable as a merge gate rather than noise:

- **Only what the PR is responsible for fails it.** Every finding carries a `pr_impact`
of `introduced`, `aggravated`, or `pre_existing`. The first two block; `pre_existing`
is reported and never blocks. Blocking a merge over code the author never wrote is how
a required check gets deleted, so when a hunter is unsure between `aggravated` and
`pre_existing`, it must pick `pre_existing`.
- **Depth follows risk.** Triage runs first, in the orchestrator, with no subagents. It
maps changed paths and added-line sink tokens onto the same class slugs the `sh-kb-*`
bases use, then picks a tier. Tier 0 (no security-relevant change) launches nothing at
all and still sets the status. Tier 3 runs the full pipeline.
- **Re-pushes do not spam.** Each comment carries a hidden fingerprint computed without
line numbers, so a re-review adds only what is new and lists what was fixed as
"Resolved since the last review".

| Verdict | Status | When |
| --- | --- | --- |
| fail | `failure` | introduced or aggravated finding at or above `--fail-on` (default `medium`), confidence >= 80 |
| warn | `success` | nothing introduced or aggravated; pre-existing findings reported |
| pass | `success` | no findings, or triage stopped at Tier 0 |
| error | `error` | the review could not complete |

`warn` reports `success` on purpose: a warning that blocks a merge is a failure with
extra steps, and teams respond by removing the check. `error` is kept distinct from
`failure` so a broken run never looks like a vulnerability it did not find.

The review event is always `COMMENT`, never `REQUEST_CHANGES` or `APPROVE`. The commit
status is the enforcement mechanism, and it is the one branch protection reads.

**Scope:** the skill writes to the pull request and the commit status, and nowhere else.
It opens no issues and creates nothing in any external tracker.

### Re-reviews are incremental

[Permalink: Re-reviews are incremental](https://github.com/dmdhrumilmistry/security-harness#re-reviews-are-incremental)

A PR gets reviewed once per push, so the second review has to be cheaper than the first or
the tool becomes something people turn off.

**Dedup happens before the spending, not before the posting.** The fingerprints already on
the PR are read in Phase 1 and handed to the hunters and the verifier. Finding a duplicate
at the end would mean the most expensive model in the pipeline had already re-confirmed a
conclusion that was written on the PR the whole time. This needs no cache: the state lives
in the PR, so it works on a cold machine and in CI.

**A local cache makes the rest incremental.**`sh-review-cache` stores each run's file
hashes, findings and verdicts under your OS cache directory (never in the repo, since a
cross-repo review runs in a temp clone that gets deleted). The next review re-hunts only
files whose content actually changed, reuses verdicts for findings that are unchanged, and
reuses the recon map if nothing it covers moved.

**A base-branch merge costs nothing.** Merging `main` into a PR branch changes the head
SHA and nothing the author wrote, but a commit status is pinned to a SHA, so the required
check silently disappears from the new head. When the PR's own files are byte-identical
_and_ the base delta touches nothing the findings depend on, the previous verdict is
re-stamped onto the new SHA with no agents launched at all. That last condition is what
makes it safe: a base merge that deletes a sanitizer leaves every PR file unchanged while
turning a safe line into an exploitable one.

Invalidation is deliberately conservative, because a stale entry in a security tool does
not make it slow, it makes it **wrong**. The cache key hashes every `sh-kb-*` knowledge
base, so a KB update invalidates every cached finding - a cached "clean" must never
suppress the finding that update was written to catch. Model identity, skill version, file
content and a 7-day TTL all invalidate too, and an unspecified model is treated as a miss.

`--no-cache` disables it, `--refresh-cache` re-baselines, and `run.md` records per phase
what was launched, reused and skipped, so a cache that quietly stops hitting is visible
rather than assumed.

### Posting, and where things are written

[Permalink: Posting, and where things are written](https://github.com/dmdhrumilmistry/security-harness#posting-and-where-things-are-written)

**The review and the commit status are posted by default.** A review that was computed and
never delivered helped nobody. `--confirm` restores a prompt before posting, `--dry-run`
sends nothing, `--no-status` posts the review but leaves the commit status alone.

Posting goes through `scripts/sh-pr-post.py` rather than hand-built API calls, because it
is a multi-step operation with a mandatory tail: review, then status, then receipts, with
a 422 recovered by moving the comment rather than shifting a line number. The script
**never exits leaving the status at `pending`** \- if the review cannot be posted it still
sets `error`, saying the tooling failed rather than accusing the PR.

Inline comments are reserved for findings at **medium or above** with confidence >= 80.
Low-severity findings go in the collapsed body section, so a low-priority finding showing
up with zero inline comments is the policy working, not a failure.

### Local run metrics

[Permalink: Local run metrics](https://github.com/dmdhrumilmistry/security-harness#local-run-metrics)

Every run records what it cost, so "the cache is working" and "reviews got slower" stop
being matters of opinion.

```
python3 <skill>/scripts/sh-metrics.py path      # where records live
python3 <skill>/scripts/sh-metrics.py report    # aggregate, by model
python3 <skill>/scripts/sh-metrics.py purge --older-than-days 30
```

Two append-only JSONL files - `runs.jsonl` (repo, PR, tier, verdict, totals, the flags you
passed) and `events.jsonl` (one line per phase or agent: model, tokens, duration, outcome,
whether it was reused from cache). JSONL so a crashed run still leaves valid lines above
the crash.

| Platform | Metrics | Cache |
| --- | --- | --- |
| **Linux / BSD** | `$XDG_DATA_HOME/security-harness/metrics`<br>default `~/.local/share/security-harness/metrics` | `$XDG_CACHE_HOME/security-harness`<br>default `~/.cache/security-harness` |
| macOS | `~/Library/Application Support/security-harness/metrics` | `~/Library/Caches/security-harness` |
| Windows | `%LOCALAPPDATA%\security-harness\metrics` | `%LOCALAPPDATA%\security-harness\cache` |

Linux follows the XDG Base Directory spec, so both honour `XDG_DATA_HOME` and
`XDG_CACHE_HOME` when set and fall back to `~/.local/share` and `~/.cache` when they are
not. Override either directly with `SH_METRICS_DIR` and `SH_REVIEW_CACHE_DIR`.

**On `python` vs `python3`:** most Linux distributions ship `python3` and have no `python`
at all, so the examples here use `python3`. The bundled scripts carry a
`#!/usr/bin/env python3` shebang and are executable, so `./scripts/sh-metrics.py report`
works directly on Linux and macOS. The skill resolves
`PY="$(command -v python3 || command -v python)"` once per run, which covers all three
platforms including Git Bash on Windows.

**Strictly local.** Neither script contains any network code or reporting endpoint.
Anything token-shaped is redacted before it is written, because local files get pasted
into issues.

### Running it unattended

[Permalink: Running it unattended](https://github.com/dmdhrumilmistry/security-harness#running-it-unattended)

Optional, and a separate decision from using the skill. Run it by hand on your own PRs
for a while first, so you know what it says about your codebase before it says it in
front of your team.

When you are ready, "Enforcing the check on a repository" in
[`references/pr-review-mapping.md`](https://github.com/dmdhrumilmistry/security-harness/blob/main/plugins/security-harness/references/pr-review-mapping.md)
has a copy-paste workflow for **your** repo, plus the fail-safe that stops a dead job
leaving a required check stuck on `pending`.

The threshold stays at the default `medium`. Pre-existing findings never block a merge,
so an unscanned codebase does not produce a wall of red on day one - only what a PR
actually introduces or aggravates can fail it.

## How it works

[Permalink: How it works](https://github.com/dmdhrumilmistry/security-harness#how-it-works)

1. **Setup** \- probe available tools, define scope, create the run directory.
2. **Recon** (`sh-recon`) \- build the Graft graph; detect stack/versions; SBOM + CVEs; enumerate entry
points, trust boundaries, and dangerous sinks.
3. **Hunt** (`sh-hunter` ×N, parallel) - one hunter per relevant class loads its `sh-kb-*` knowledge base,
traces attacker input from source to sink, and records candidates. A shared **attempts ledger** stops
agents from repeating each other's probes.
4. **Chain** (`sh-chainer`) \- compose findings into higher-severity attack paths.
5. **Verify** (`sh-verifier`) \- refute first, then confirm exploitability from evidence, build PoCs, assign
CVSS, and cut false positives.
6. **Report** (`sh-reporter`) \- produce the deliverables.

Subagents share nothing but files; the contract is in `plugins/security-harness/references/state-files.md`.

## Extending

[Permalink: Extending](https://github.com/dmdhrumilmistry/security-harness#extending)

Add a new vulnerability class by creating `skills/sh-kb-<class>/SKILL.md` following the shared template
(When to hunt · Sources & sinks · Detection recipe · Payloads/PoC · False-positive filters · CWE/OWASP ·
Chaining hints · Mitigation), then add its slug to the `class` enum in `references/finding-schema.json`
and the routing table in `skills/sh-router/SKILL.md`.

## Automated knowledge-base updates

[Permalink: Automated knowledge-base updates](https://github.com/dmdhrumilmistry/security-harness#automated-knowledge-base-updates)

A scheduled GitHub Action (`.github/workflows/update-knowledge-base.yml`) keeps the `sh-kb-*` knowledge
bases fresh. **Every alternate day** (and on manual `workflow_dispatch`), it runs an agent to distill new,
reputable public security research - OWASP, PortSwigger Research, CWE/CAPEC, NIST, MDN, curated GitHub
repos, and public HackerOne disclosures - into small, well-sourced improvements. A **second, adversarial**
**reviewer agent** then scans the resulting diff for malicious/injected content, and the PR is
**auto-merged only if that reviewer approves**.

### Two workflows, three jobs

[Permalink: Two workflows, three jobs](https://github.com/dmdhrumilmistry/security-harness#two-workflows-three-jobs)

PR creation is deliberately separated from review and merge, so the thing that writes
the diff is never the thing that decides to ship it.

**Stage 1 - [`update-knowledge-base.yml`](https://github.com/dmdhrumilmistry/security-harness/blob/main/.github/workflows/update-knowledge-base.yml)**
(scheduled or manual). One job, `create-pr`:

1. **Generate** \- the agent edits the KB from allowlisted sources. No commit, no push.
2. **Open PR** \- a deterministic step opens (or updates) a PR on the `automated/kb-update`
branch, labeled `awaiting-review`.
3. **Hand off** \- on a successful PR creation it dispatches stage 2 with the PR number.

**Stage 2 - [`kb-review-and-merge.yml`](https://github.com/dmdhrumilmistry/security-harness/blob/main/.github/workflows/kb-review-and-merge.yml)**
(dispatched by stage 1, or run by hand against any automated PR). Two jobs:

- **`review`** \- a _separate_ agent run inspects the diff **adversarially** for
prompt-injection artifacts, out-of-scope edits, secrets/exfil, PII, weaponized
exploits, off-allowlist sourcing, or house-style violations. It has **no web and no**
**shell**, and **fails closed**: anything suspicious, any uncertainty, or a missing
verdict file → REJECT. The verdict is posted as a PR comment and drives the label.
- **`merge`** \- runs **only** on `APPROVE`, and merges the PR. A `REJECT` skips it and
the `blocked` job reports why.

> **Why a dispatch rather than a `pull_request` trigger:** a PR opened by `GITHUB_TOKEN`
> does not trigger `pull_request` workflows. `workflow_dispatch` is one of the two events
> exempt from that recursion guard, so stage 1 can hand off reliably.

**Auto-merge means an approving agent lands code in `main`.** The controls on that:

- The merge job refuses any PR that is closed, from a fork, or whose head branch is
outside `automated/*` (`ALLOWED_HEAD_PREFIX` in the workflow).
- It prefers GitHub's own auto-merge, so **branch protection still applies**. With a rule
on `main` requiring an approving review, the PR queues and waits for a human instead of
merging. It falls back to an immediate merge only on repos where auto-merge is off.
- Set the `auto_merge` input to `false` on a manual run to review without merging.
- The reviewer prompt tells the agent its verdict is binding, not advisory.

> Requires the repo setting **"Allow GitHub Actions to create and approve pull requests"** (Settings →
> Actions → General → Workflow permissions) so the workflow can open the PR. If you want a human in the
> loop despite auto-merge, protect `main` with a branch-protection rule requiring a pull request and at
> least one approving review - the auto-merge path honours it.

### Pluggable agents

[Permalink: Pluggable agents](https://github.com/dmdhrumilmistry/security-harness#pluggable-agents)

Both stages run through [`.github/actions/ai-agent`](https://github.com/dmdhrumilmistry/security-harness/blob/main/.github/actions/ai-agent/action.yml),
a composite action that dispatches to whichever agent you configure. Claude Code, OpenAI
Codex, Gemini CLI, and an escape hatch for anything else:

| `agent` | Runs | Credential |
| --- | --- | --- |
| `claude` (default) | `anthropics/claude-code-action@v1` | `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` |
| `codex` | `codex exec --full-auto` | `OPENAI_API_KEY` |
| `gemini` | `gemini --yolo --prompt` | `GEMINI_API_KEY` |
| `custom` | your `KB_AGENT_INSTALL` / `KB_AGENT_COMMAND` | whatever it needs |

Pick per run from the `workflow_dispatch` inputs, or set repo variables to change the
default: `KB_AGENT` and `KB_MODEL` for the generator, `KB_REVIEW_AGENT` and
`KB_REVIEW_MODEL` for the reviewer. Running the generator and the reviewer on **different**
**agents** is a meaningful hardening step: an injection tuned for one model is less likely
to land on a second, independent one.

For `agent: custom`, set `KB_AGENT_COMMAND` to a shell command. The prompt is written to
the file named by `$AGENT_PROMPT_FILE`, and `$AGENT_MODEL` carries the model input.

Prompt-injection defenses, since the generator reads the open web:

- **Domain allowlist.**`WebFetch` is restricted to the trusted domains in
`.github/kb-update/trusted-sources.md` (mirrored in the workflow's `--allowedTools`). `WebSearch` can
discover URLs, but only allowlisted domains can actually be fetched.
- **Content is data, not commands.** The task prompt (`.github/kb-update/prompt.md`) instructs Claude to
treat every fetched byte as untrusted reference material and to ignore any instructions embedded in a
page - HackerOne report bodies (user-generated) are flagged as the highest-risk tier.
- **No shell, no push on the generator; the reviewer is the gate.** The generator can only edit files.
The independent reviewer (`.github/kb-update/review-prompt.md`) is what stands between fetched content
and `main` \- nothing merges without its explicit approval.
- **Different agents for generator and reviewer.** Optional, and the strongest version of the gate: set
`KB_AGENT` and `KB_REVIEW_AGENT` to two different engines.

**Setup:**

- Add the credential for whichever agent you use (Settings → Secrets and variables → Actions):
**`CLAUDE_CODE_OAUTH_TOKEN`** (default), `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `GEMINI_API_KEY`.
The OAuth token authenticates against **your Claude subscription's usage limits** rather than a metered
API key - generate it locally with `claude setup-token` (requires an active Claude Pro/Max subscription)
and paste the result.
- Enable **"Allow GitHub Actions to create and approve pull requests"** (Settings → Actions → General →
Workflow permissions) so the workflow can open its PR. Recommended: add a branch-protection rule on `main`
requiring a PR and an approving review, so no automated change can land without a human even with
auto-merge on.
- To change which sources are allowed, edit the allowlist in `trusted-sources.md` **and** the matching
`WebFetch(domain:...)` entries in the workflow - keep the two in sync.

Each run records what it did in `.github/kb-update/last-run-summary.md`.

## Roadmap

[Permalink: Roadmap](https://github.com/dmdhrumilmistry/security-harness#roadmap)

- ~~Codex / Cursor mirror wiring.~~
✅ Shipped: `AGENTS.md`, a Gemini CLI extension, and `scripts/sync-agent-skills.py`
for `.agents/skills` and opencode. See [`docs/DISTRIBUTION.md`](https://github.com/dmdhrumilmistry/security-harness/blob/main/docs/DISTRIBUTION.md).
- ~~Optional live-fetch augmentation of knowledge bases (PortSwigger/OWASP/CWE) on top of curated references.~~
✅ Shipped as the scheduled knowledge-base updater above.
- Optional DAST bridge for runtime confirmation of `needs-runtime` findings.

## License

[Permalink: License](https://github.com/dmdhrumilmistry/security-harness#license)

MIT

## About

A multi-agent application-security review harness for Claude Code (and, later, other AI agents). One router skill dispatches to a full offensive-security pipeline that maps a codebase, hunts vulnerabilities with a per-class knowledge base, chains findings into escalations, verifies real impact, and reports to README/JSON/SARIF/doc/PDF.

### Topics

[agent-skills](https://github.com/topics/agent-skills) [appsec](https://github.com/topics/appsec) [claude-code-plugin](https://github.com/topics/claude-code-plugin) [gemini-cli-extension](https://github.com/topics/gemini-cli-extension)

### Resources

[Readme](https://github.com/dmdhrumilmistry/security-harness#readme-ov-file)

[MIT license](https://github.com/dmdhrumilmistry/security-harness#MIT-1-ov-file)

[Activity](https://github.com/dmdhrumilmistry/security-harness/activity)

### Stars

**41** stars

### Watchers

**0** watching

### Forks

[**10** forks](https://github.com/dmdhrumilmistry/security-harness/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fdmdhrumilmistry%2Fsecurity-harness&report=dmdhrumilmistry+%28user%29)

## [Releases](https://github.com/dmdhrumilmistry/security-harness/releases) 1 (1)

[v0.2.0Latest\\
\\
2 weeks agoSep 27, 2026](https://github.com/dmdhrumilmistry/security-harness/releases/tag/v0.2.0)

## [Contributors](https://github.com/dmdhrumilmistry/security-harness/graphs/contributors) 3 (3)

- [![@claude](https://avatars.githubusercontent.com/u/81847?s=64&v=4)](https://github.com/claude) [**claude** Claude](https://github.com/claude)
- [![@dmdhrumilmistry](https://avatars.githubusercontent.com/u/56185972?s=64&v=4)](https://github.com/dmdhrumilmistry) [**dmdhrumilmistry** dmdhrumilmistry](https://github.com/dmdhrumilmistry)
- [![@github-actions[bot]](https://avatars.githubusercontent.com/in/15368?s=64&v=4)](https://github.com/github-actions[bot]) [**github-actions\[bot\]**](https://github.com/github-actions[bot])

## Languages

- [Python100%](https://github.com/dmdhrumilmistry/security-harness/search?l=python)

You can’t perform that action at this time.