# https://github.com/mockdr/mockdr

[Skip to content](https://github.com/mockdr/mockdr#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/mockdr/mockdr) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/mockdr/mockdr) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/mockdr/mockdr) to refresh your session.Dismiss alert

{{ message }}

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/mockdr/mockdr).

[mockdr](https://github.com/mockdr)/ **[mockdr](https://github.com/mockdr/mockdr)** Public

- [Notifications](https://github.com/login?return_to=%2Fmockdr%2Fmockdr) You must be signed in to change notification settings
- [Fork\\
3](https://github.com/login?return_to=%2Fmockdr%2Fmockdr)
- [Star\\
52](https://github.com/login?return_to=%2Fmockdr%2Fmockdr)


Use this GitHub action with your project

Add this Action to an existing workflow or create a new one

[View on Marketplace](https://github.com/marketplace/actions/mockdr-multi-edr-mock-server)

main

[**10** Branches](https://github.com/mockdr/mockdr/branches) [**10** Tags](https://github.com/mockdr/mockdr/tags)

[Go to Branches page](https://github.com/mockdr/mockdr/branches)[Go to Tags page](https://github.com/mockdr/mockdr/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![gweber](https://avatars.githubusercontent.com/u/516202?v=4&size=40)](https://github.com/gweber)[gweber](https://github.com/mockdr/mockdr/commits?author=gweber)

[fix(kibana): three routes answered a dialect no client parses](https://github.com/mockdr/mockdr/commit/9a0c452fc48845c728416666d80daf17fb3b332c)

Open commit detailssuccess

30 minutes agoAug 29, 2026

[9a0c452](https://github.com/mockdr/mockdr/commit/9a0c452fc48845c728416666d80daf17fb3b332c) · 30 minutes agoAug 29, 2026

## History

[224 Commits](https://github.com/mockdr/mockdr/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/mockdr/mockdr/commits/main/) 224 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [.github](https://github.com/mockdr/mockdr/tree/main/.github ".github") | [.github](https://github.com/mockdr/mockdr/tree/main/.github ".github") | [fix(splunk): answer a wrong verb by the verb, not by the path](https://github.com/mockdr/mockdr/commit/1062ae29ffa7877e7f379f38d7ad810c0c1ba7cc "fix(splunk): answer a wrong verb by the verb, not by the path  mockdr had it the other way round — one answer for the search endpoints, another for the KV store's batch paths, and the 400 splunkd keeps for a `POST` with no name to act on for everything else, so `PUT` and `PATCH` on any EAI collection came back as that 400. Measured across fifteen paths: `PATCH` is 405 `Method Not Allowed` everywhere and carries no `Allow`; `PUT` is 404 `Requested invalid action 'PUT'.` except under `/services/search/`, where it is that same 405.  The search endpoints keep an answer of their own, and it is not one answer: a wrong verb is FATAL *with* an `Allow`, worded `Method Not Allowed` on the job collections and `The method is not allowed.` everywhere else, while `typeahead` sits outside all of it. Encoded path by path, because no rule accounts for the split — and this repo's own tests caught the first attempt, which had generalised from too few paths and broke `GET` on the export and parser endpoints.  The batch paths take `PUT` as well as `POST`: splunkd's refusal there names `Allow: POST,PUT`, and mockdr served one of the two. Deleting a job is *cancelling* it, in a line that does not name the sid. `typeahead` requires a `count` and says so, where mockdr defaulted to fifty and answered an empty list — \"there is nothing to complete\" rather than \"you did not say how many\". And `timeparser` with no `time` answers 204 with no body and no content type, rather than assuming `now`.  CI's new audit job fetches the SentinelOne spec, as the field-drift job does: without it `enum_drift` cannot run, and a check that does not run is worse than one that fails.") | 13 hours agoAug 28, 2026 |
| [backend](https://github.com/mockdr/mockdr/tree/main/backend "backend") | [backend](https://github.com/mockdr/mockdr/tree/main/backend "backend") | [fix(kibana): three routes answered a dialect no client parses](https://github.com/mockdr/mockdr/commit/9a0c452fc48845c728416666d80daf17fb3b332c "fix(kibana): three routes answered a dialect no client parses  `rules/_bulk_create` let FastAPI answer pydantic's `Input should be a valid list`; `rules/preview` asked for a `name` alone, in the io-ts wording a different family of routes uses; `signals/assignees` answered one hand-written `ids is required` for every malformed body. 8.15 words all three with zod: it names what it got, lists five failures and counts the rest — the same rule the bulk-action route already answers with — and names each member of each block in declaration order.  Two more findings came out of the last of them, and both are the kind that answers success to a request that did nothing. The members are `add` and `remove`, where mockdr read `assignees_to_add` and `assignees_to_remove`, so an assignment written the way the product takes it was read as no assignment at all. And an assignee is a user id as a plain string, where mockdr read the `{\"uid\": …}` object it stores internally — so the same request raised out of the handler instead.  These three were among the two dozen vendor routes `audit_coverage.py` reports as watched by this repo's own tests alone. They have probes now.") | 30 minutes agoAug 29, 2026 |
| [bruno/mockdr](https://github.com/mockdr/mockdr/tree/main/bruno/mockdr "This path skips through empty directories") | [bruno/mockdr](https://github.com/mockdr/mockdr/tree/main/bruno/mockdr "This path skips through empty directories") | [fix: what the TEAMS.md review of 2.1.0 converged on](https://github.com/mockdr/mockdr/commit/d7c972b338f5325a5f632f47c96406dfb3996fe8 "fix: what the TEAMS.md review of 2.1.0 converged on  Three convergent findings from 86 perspectives over the code, done:  1. Bridge events dated by their records. Splunk bridge and Sentinel seeders    stamped every event 2023-11-14 (_SEED_EPOCH) while the records said    2026; earliest=-24h and the seeded ES saved searches found nothing.    utils/event_time.py reads the record's own timestamp. The seeder's    duplicate activity pass is gone (the repository bridges them live).  2. Growth capped. Per-request collections evict oldest-first (store.CAPS:    events, notables, jobs, sessions, ES documents, uploads, OAuth tokens);    request bodies have a 413 ceiling (MOCKDR_MAX_BODY_BYTES, read-free);    fault-injection delay bounded; /metrics labels by route template so    unknown paths cannot add series. Webhook delivery: 5xx retried, 4xx a    rejection, only 2xx/3xx a success (a 500 used to count as delivered);    the public webhook sink redacts credential headers.  3. Map = territory. ADR-001 lock claim, SECURITY.md XSS header, ADR-009    title, FastAPI title and console branding (\"Mock S1\", \"Hypervisor\",    \"7 platforms\"), one coverage gate (85 %, measured 89 %), CORS default on    ports that exist, README env table complete, Vite proxy for every vendor    root, dead Bruno/Postman requests, a CloudFront error page committed as    crowdstrike_swagger.json, get_threat on the shared serializer.    NOTICE.md lists every vendored reference with its licence. CI runs    fuzz_parsers.py and hostile_probe.py on every push.") | last weekAug 23, 2026 |
| [conformance](https://github.com/mockdr/mockdr/tree/main/conformance "conformance") | [conformance](https://github.com/mockdr/mockdr/tree/main/conformance "conformance") | [fix(kibana): three routes answered a dialect no client parses](https://github.com/mockdr/mockdr/commit/9a0c452fc48845c728416666d80daf17fb3b332c "fix(kibana): three routes answered a dialect no client parses  `rules/_bulk_create` let FastAPI answer pydantic's `Input should be a valid list`; `rules/preview` asked for a `name` alone, in the io-ts wording a different family of routes uses; `signals/assignees` answered one hand-written `ids is required` for every malformed body. 8.15 words all three with zod: it names what it got, lists five failures and counts the rest — the same rule the bulk-action route already answers with — and names each member of each block in declaration order.  Two more findings came out of the last of them, and both are the kind that answers success to a request that did nothing. The members are `add` and `remove`, where mockdr read `assignees_to_add` and `assignees_to_remove`, so an assignment written the way the product takes it was read as no assignment at all. And an assignee is a user id as a plain string, where mockdr read the `{\"uid\": …}` object it stores internally — so the same request raised out of the handler instead.  These three were among the two dozen vendor routes `audit_coverage.py` reports as watched by this repo's own tests alone. They have probes now.") | 30 minutes agoAug 29, 2026 |
| [data/vendor-specs](https://github.com/mockdr/mockdr/tree/main/data/vendor-specs "This path skips through empty directories") | [data/vendor-specs](https://github.com/mockdr/mockdr/tree/main/data/vendor-specs "This path skips through empty directories") | [fix(falcon,cortex): refuse a write body that carries nothing the rout…](https://github.com/mockdr/mockdr/commit/3f146fa26c9dac2ed872cb5f686cf7613b12a34c "fix(falcon,cortex): refuse a write body that carries nothing the route knows  The same question the SentinelOne mount now answers, asked of the two other platforms whose references state what a write body is made of.  Six Falcon routes answered 200 to {} — a host action addressed to no host, an indicator create with no indicators, a case tagged with nothing, each coming back as a success with an empty resources list, which reads exactly like a request that matched nothing. gofalcon's request_required says what those bodies carry.  Two more were Cortex XDR's. Its reference states a requirement for 68 of its routes and none for most of the rest — xql/get_quota gives {\"request_data\": null} as its own example — so the nine routes it is silent about go on answering, because refusing a body a product may well accept is the same defect facing the other way. cortex_openapi_spec.py keeps the request side of the transcription now.  And the sweep that found all this was reseeding the world under itself: it probed mockdr's own _dev surface, and posting to _dev/scenario invalidated the tokens every later mount was being probed with, turning three platforms' worth of routes into 401s it read as 'never reached'. It sees 23 more routes now, and the ones no reference speaks for are listed with the reason, so a non-zero exit means something new.  17 tests; 4154 backend tests.") | 3 days agoAug 26, 2026 |
| [docs](https://github.com/mockdr/mockdr/tree/main/docs "docs") | [docs](https://github.com/mockdr/mockdr/tree/main/docs "docs") | [fix(sentinel): let the tables the connectors advertise hold something](https://github.com/mockdr/mockdr/commit/0370e6638de166ee9ebe1b598b80ccf7e63113c1 "fix(sentinel): let the tables the connectors advertise hold something  This workspace's dataConnectors advertise SentinelOne_CL, CrowdStrikeFalcon_CL, ElasticSecurity_CL and PaloAltoCortexXDR_CL — and hand the client the query to ask each one when data last arrived, '<Table> | summarize max(TimeGenerated)'. All four answered an empty result with no columns, and the summarize went unparsed so the connector's own query returned the whole table. A client that read the connector list and ran what it was given learned that a connector this install says is ingesting had ingested nothing.  The events were there the whole time: the same install's Splunk store holds them, from the same four products, and the code said so — 'these are populated by the Splunk event store' — beside a return []. Each table now answers its own connector's events, with the TimeGenerated a workspace orders custom logs by, and summarize max/min answer one row named the way Log Analytics names it.  4 tests; 4300 backend tests; all audits clean.") | 3 days agoAug 26, 2026 |
| [frontend](https://github.com/mockdr/mockdr/tree/main/frontend "frontend") | [frontend](https://github.com/mockdr/mockdr/tree/main/frontend "frontend") | [chore(release): cut 2.3.0](https://github.com/mockdr/mockdr/commit/a10d5bce1ab601f165e3f5e3a88f152884f18e13 "chore(release): cut 2.3.0  The round that stopped comparing shapes and started comparing answers. Every probe until now measured the *shape* of a reply against an empty real install, which cannot see a wrong answer: a search that matches nothing agrees with every other search that matches nothing. Seeding both sides with the same data found what that blind spot had been holding — every Elasticsearch time filter matching nothing, Splunk snapping its windows on a multiple of seconds, a date_histogram leaving out the quiet days, an ordinary parenthesised SPL search answering 500, an index you created not existing, and Kibana reading four dialects of query past without a word.  `--seeded` is now part of the harness and of CI: the same five events into both Splunk targets, the same six documents into both Elasticsearch targets, and 56 probes comparing rows rather than skeletons.  Release tools before the tag: 119 Splunk and 153 Elasticsearch/Kibana conformance probes with 0 findings against the real products, schema_drift 0/0 on all six spec-judged platforms (199 routes), field_drift 12/12 clean, fuzz 10 694 inputs and hostile probe 16 348 requests with no findings, load test all scenarios passing (read p99 62.8 ms), 3 457 backend tests, 2 103 frontend tests.") | 5 days agoAug 24, 2026 |
| [node\_modules/.vite/vitest/da39a3ee5e6b4b0d3255bfef95601890afd80709](https://github.com/mockdr/mockdr/tree/main/node_modules/.vite/vitest/da39a3ee5e6b4b0d3255bfef95601890afd80709 "This path skips through empty directories") | [node\_modules/.vite/vitest/da39a3ee5e6b4b0d3255bfef95601890afd80709](https://github.com/mockdr/mockdr/tree/main/node_modules/.vite/vitest/da39a3ee5e6b4b0d3255bfef95601890afd80709 "This path skips through empty directories") | [fix(fidelity): no evidence, no route - drop the unevidenced XDR and r…](https://github.com/mockdr/mockdr/commit/1d9c43eae53a2808c7db681b152b0c0600ac70b1 "fix(fidelity): no evidence, no route - drop the unevidenced XDR and retired CrowdStrike routes  A mock that serves a path nobody can document invents the product. Removed, with the UI that leaned on them:  - Cortex XDR: alerts/update_alerts, hash_exceptions/allowlist|blocklist/get,   indicators/enable_iocs|disable_iocs - no public evidence of their reply   shape exists. The hash-exceptions view goes with them (add/remove stay). - CrowdStrike: the sixteen routes the current API no longer has - the legacy   Incidents API (/incidents/*), the legacy IOC API (/indicators/*/iocs/v1),   the cases shape under /alerts/*/cases and the GET variants of .../GET/v1   POSTs. The incidents and cases views and the dashboard's incident widget   go with them; cases keep the documented /cases/queries/cases/v1 and   /cases/entities/case-tags/v1.  Every mounted CrowdStrike and Cortex XDR route now has a reference: 23 and 33 compared, 0 drift, 0 unjudged. Tests moved to the documented routes; the single-entity UI wrappers no longer reject on an empty list.  Also: the previous commit's frontend CI failure (four unhandled rejections from those wrappers under a mocked client) is fixed here.") | last weekAug 22, 2026 |
| [postman](https://github.com/mockdr/mockdr/tree/main/postman "postman") | [postman](https://github.com/mockdr/mockdr/tree/main/postman "postman") | [fix: what the TEAMS.md review of 2.1.0 converged on](https://github.com/mockdr/mockdr/commit/d7c972b338f5325a5f632f47c96406dfb3996fe8 "fix: what the TEAMS.md review of 2.1.0 converged on  Three convergent findings from 86 perspectives over the code, done:  1. Bridge events dated by their records. Splunk bridge and Sentinel seeders    stamped every event 2023-11-14 (_SEED_EPOCH) while the records said    2026; earliest=-24h and the seeded ES saved searches found nothing.    utils/event_time.py reads the record's own timestamp. The seeder's    duplicate activity pass is gone (the repository bridges them live).  2. Growth capped. Per-request collections evict oldest-first (store.CAPS:    events, notables, jobs, sessions, ES documents, uploads, OAuth tokens);    request bodies have a 413 ceiling (MOCKDR_MAX_BODY_BYTES, read-free);    fault-injection delay bounded; /metrics labels by route template so    unknown paths cannot add series. Webhook delivery: 5xx retried, 4xx a    rejection, only 2xx/3xx a success (a 500 used to count as delivered);    the public webhook sink redacts credential headers.  3. Map = territory. ADR-001 lock claim, SECURITY.md XSS header, ADR-009    title, FastAPI title and console branding (\"Mock S1\", \"Hypervisor\",    \"7 platforms\"), one coverage gate (85 %, measured 89 %), CORS default on    ports that exist, README env table complete, Vite proxy for every vendor    root, dead Bruno/Postman requests, a CloudFront error page committed as    crowdstrike_swagger.json, get_threat on the shared serializer.    NOTICE.md lists every vendored reference with its licence. CI runs    fuzz_parsers.py and hostile_probe.py on every push.") | last weekAug 23, 2026 |
| [scripts](https://github.com/mockdr/mockdr/tree/main/scripts "scripts") | [scripts](https://github.com/mockdr/mockdr/tree/main/scripts "scripts") | [fix(splunk): one KV Store collection, read back by name](https://github.com/mockdr/mockdr/commit/5b7abfee58f01de5848477496d5e8868db5ea95e "fix(splunk): one KV Store collection, read back by name  splunkd serves a collection's configuration under its own path as well as in the listing, and mockdr had only the listing — so a client reading back the collection it had just created met the catch-all's complaint about a missing target name, where splunkd answers the entry or a 404 naming it. The single read carries the `fields` block naming what the collection accepts, with the first non-empty `wildcard` in this mock: the two families a schema is written in.  scripts/unreadable_entries.py asks under `servicesNS/nobody` for it. The bare path is a refusal rather than a listing there, so asking at the top skipped the one collection the audit exists to check.") | 46 minutes agoAug 29, 2026 |
| [team](https://github.com/mockdr/mockdr/tree/main/team "team") | [team](https://github.com/mockdr/mockdr/tree/main/team "team") | [chore(release): cut 2.3.0](https://github.com/mockdr/mockdr/commit/a10d5bce1ab601f165e3f5e3a88f152884f18e13 "chore(release): cut 2.3.0  The round that stopped comparing shapes and started comparing answers. Every probe until now measured the *shape* of a reply against an empty real install, which cannot see a wrong answer: a search that matches nothing agrees with every other search that matches nothing. Seeding both sides with the same data found what that blind spot had been holding — every Elasticsearch time filter matching nothing, Splunk snapping its windows on a multiple of seconds, a date_histogram leaving out the quiet days, an ordinary parenthesised SPL search answering 500, an index you created not existing, and Kibana reading four dialects of query past without a word.  `--seeded` is now part of the harness and of CI: the same five events into both Splunk targets, the same six documents into both Elasticsearch targets, and 56 probes comparing rows rather than skeletons.  Release tools before the tag: 119 Splunk and 153 Elasticsearch/Kibana conformance probes with 0 findings against the real products, schema_drift 0/0 on all six spec-judged platforms (199 routes), field_drift 12/12 clean, fuzz 10 694 inputs and hostile probe 16 348 requests with no findings, load test all scenarios passing (read p99 62.8 ms), 3 457 backend tests, 2 103 frontend tests.") | 5 days agoAug 24, 2026 |
| [toolkit](https://github.com/mockdr/mockdr/tree/main/toolkit "toolkit") | [toolkit](https://github.com/mockdr/mockdr/tree/main/toolkit "toolkit") | [Initial commit](https://github.com/mockdr/mockdr/commit/8dbed909dcdc94e75016ada65c40ff12db8872d6 "Initial commit") | 5 months agoMar 19, 2026 |
| [.dockerignore](https://github.com/mockdr/mockdr/blob/main/.dockerignore ".dockerignore") | [.dockerignore](https://github.com/mockdr/mockdr/blob/main/.dockerignore ".dockerignore") | [Initial commit](https://github.com/mockdr/mockdr/commit/8dbed909dcdc94e75016ada65c40ff12db8872d6 "Initial commit") | 5 months agoMar 19, 2026 |
| [.gitignore](https://github.com/mockdr/mockdr/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/mockdr/mockdr/blob/main/.gitignore ".gitignore") | [fix(fidelity): measure every response shape against the real product …](https://github.com/mockdr/mockdr/commit/16b4f8558ede4fe9fce78509f33f2b24dafcbe9e "fix(fidelity): measure every response shape against the real product or its spec  Response shapes were typed from memory; now they are measured. Splunk, Elasticsearch and Kibana entries are compared key-for-key against the real containers in the conformance harness, Sentinel and Graph resources against the vendor's published specs fetched from the internet (Azure REST API specs 2024-03-01 stable + 2025-10-01 preview for GenericUI connectors; Microsoft Graph v1.0 OpenAPI metadata).  Before -> after: Splunk 897 missing keys -> 0 (72 probes); Sentinel 276 drift findings -> 0 (19 routes); Graph 35 -> 0 (49 routes); Elastic/Kibana 0 (57).  Splunk: every collection completed from fixtures captured on 10.4.2 (a saved search has 217 keys, not 11; a finished job 67 with its telemetry, anchored on the job's own start time); per-collection links, ACL members, published, paging/messages/top links; server/status is a seven-entry collection; KV config uses splunkd's flat keys and lists under /services; the parser names dc(host)'s field and timechart's seriesfilter; wrong password carries its code, a missing one does not. Kibana serves all 33 features.  Sentinel: spec-generated fixtures (scripts/gen_arm_fixtures.py) deep-merged under the mock's values; systemData everywhere; kind top-level; three real alert-rule templates; IncidentLabel objects; connectors shaped per kind; undeclared watchlistItemsCount/techniques removed; etag on watchlist items; TI indicators carry kind=indicator.  Graph: alert_ids, isActive, publisherName, deploymentProfileAssignmentStatus and result (none declared in v1.0) removed; member collections return typed users with @odata.type.  Tooling: scripts/schema_drift.py resolves cross-file $refs, scopes kind to the route's base type, resolves @odata.type, loads preview-only definitions, treats free-form objects and empty arrays as not-drift, and walks parents for empty nested collections. data/vendor-specs is versioned. Two probes declare data-dependent paths with the reason on the line.  Known limits: CrowdStrike's swagger is not publicly downloadable; MDE and Cortex XDR publish docs only; Graph /beta/ routes cannot be judged by v1.0.") | last weekAug 22, 2026 |
| [.gitleaks.toml](https://github.com/mockdr/mockdr/blob/main/.gitleaks.toml ".gitleaks.toml") | [.gitleaks.toml](https://github.com/mockdr/mockdr/blob/main/.gitleaks.toml ".gitleaks.toml") | [Initial commit](https://github.com/mockdr/mockdr/commit/8dbed909dcdc94e75016ada65c40ff12db8872d6 "Initial commit") | 5 months agoMar 19, 2026 |
| [.pre-commit-config.yaml](https://github.com/mockdr/mockdr/blob/main/.pre-commit-config.yaml ".pre-commit-config.yaml") | [.pre-commit-config.yaml](https://github.com/mockdr/mockdr/blob/main/.pre-commit-config.yaml ".pre-commit-config.yaml") | [Initial commit](https://github.com/mockdr/mockdr/commit/8dbed909dcdc94e75016ada65c40ff12db8872d6 "Initial commit") | 5 months agoMar 19, 2026 |
| [ARCHITECTURE.md](https://github.com/mockdr/mockdr/blob/main/ARCHITECTURE.md "ARCHITECTURE.md") | [ARCHITECTURE.md](https://github.com/mockdr/mockdr/blob/main/ARCHITECTURE.md "ARCHITECTURE.md") | [fix: the review's remaining debts on the backend side](https://github.com/mockdr/mockdr/commit/0ffa61a65309f00f5a8c179896890214c4c2396c "fix: the review's remaining debts on the backend side  - Seed data names nobody real: documentation IP ranges (RFC 5737) and   reserved domains (.example/.test) replace Faker's routable public IPs and   surname domains; the mail-rule seeds no longer forward to gmail.com. - Cortex XDR exclusions, violations and agent reports carried a fixed   2023 timestamp; they are dated within the last day. - The persistence snapshot records the version that wrote it; loading one   from another release says so in the log. - Webhook deliveries run on a bounded pool of eight daemon workers instead   of a sleeping thread per subscription per event; tests wait on   wait_for_deliveries() rather than on thread names. - The Docker image chowns /app to appuser (it was created after the COPYs);   compose notes that read_only and MOCKDR_PERSIST need a volume. - ARCHITECTURE.md describes eight platforms, the measured-fidelity method,   the bridge and the verification tooling (it had stood still since March). - scripts/README.md maps all seventeen scripts to when they run and holds   the release checklist; TESTING.md lists the CI jobs that actually exist. - The three parsers the review flagged for missing depth guards are not   recursive (Graph delegates to the guarded OData engine); no change.") | last weekAug 23, 2026 |
| [CHANGELOG.md](https://github.com/mockdr/mockdr/blob/main/CHANGELOG.md "CHANGELOG.md") | [CHANGELOG.md](https://github.com/mockdr/mockdr/blob/main/CHANGELOG.md "CHANGELOG.md") | [fix(kibana): three routes answered a dialect no client parses](https://github.com/mockdr/mockdr/commit/9a0c452fc48845c728416666d80daf17fb3b332c "fix(kibana): three routes answered a dialect no client parses  `rules/_bulk_create` let FastAPI answer pydantic's `Input should be a valid list`; `rules/preview` asked for a `name` alone, in the io-ts wording a different family of routes uses; `signals/assignees` answered one hand-written `ids is required` for every malformed body. 8.15 words all three with zod: it names what it got, lists five failures and counts the rest — the same rule the bulk-action route already answers with — and names each member of each block in declaration order.  Two more findings came out of the last of them, and both are the kind that answers success to a request that did nothing. The members are `add` and `remove`, where mockdr read `assignees_to_add` and `assignees_to_remove`, so an assignment written the way the product takes it was read as no assignment at all. And an assignee is a user id as a plain string, where mockdr read the `{\"uid\": …}` object it stores internally — so the same request raised out of the handler instead.  These three were among the two dozen vendor routes `audit_coverage.py` reports as watched by this repo's own tests alone. They have probes now.") | 30 minutes agoAug 29, 2026 |
| [CLA.md](https://github.com/mockdr/mockdr/blob/main/CLA.md "CLA.md") | [CLA.md](https://github.com/mockdr/mockdr/blob/main/CLA.md "CLA.md") | [Initial commit](https://github.com/mockdr/mockdr/commit/8dbed909dcdc94e75016ada65c40ff12db8872d6 "Initial commit") | 5 months agoMar 19, 2026 |
| [CODE\_OF\_CONDUCT.md](https://github.com/mockdr/mockdr/blob/main/CODE_OF_CONDUCT.md "CODE_OF_CONDUCT.md") | [CODE\_OF\_CONDUCT.md](https://github.com/mockdr/mockdr/blob/main/CODE_OF_CONDUCT.md "CODE_OF_CONDUCT.md") | [Initial commit](https://github.com/mockdr/mockdr/commit/8dbed909dcdc94e75016ada65c40ff12db8872d6 "Initial commit") | 5 months agoMar 19, 2026 |
| [COMMERCIAL\_LICENSE.md](https://github.com/mockdr/mockdr/blob/main/COMMERCIAL_LICENSE.md "COMMERCIAL_LICENSE.md") | [COMMERCIAL\_LICENSE.md](https://github.com/mockdr/mockdr/blob/main/COMMERCIAL_LICENSE.md "COMMERCIAL_LICENSE.md") | [Initial commit](https://github.com/mockdr/mockdr/commit/8dbed909dcdc94e75016ada65c40ff12db8872d6 "Initial commit") | 5 months agoMar 19, 2026 |
| [CONTRIBUTING.md](https://github.com/mockdr/mockdr/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [CONTRIBUTING.md](https://github.com/mockdr/mockdr/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [Initial commit](https://github.com/mockdr/mockdr/commit/8dbed909dcdc94e75016ada65c40ff12db8872d6 "Initial commit") | 5 months agoMar 19, 2026 |
| [Dockerfile](https://github.com/mockdr/mockdr/blob/main/Dockerfile "Dockerfile") | [Dockerfile](https://github.com/mockdr/mockdr/blob/main/Dockerfile "Dockerfile") | [fix(splunk,elastic): answer with the headers the products answer with](https://github.com/mockdr/mockdr/commit/ce05124b2bdb496afb08c83926fb6f36fda1f7bb "fix(splunk,elastic): answer with the headers the products answer with  Server: uvicorn was on every answer, which is the plainest way there is to tell a mock from the thing it mocks. Under it, measured on 10.4.2 header by header: splunkd says what each answer depends on (Vary: Cookie, Authorization — or Authorization alone for a session token it cannot resolve, refused before its cookie handler, and nothing at all for a collector token read from the query string); it says how each answer may be kept (no-store with its own already-expired Expires of October 1978, private for a credential it refused and for a mode it could not read); and for the one family it serves as cacheable — data/indexes, on a successful read only — it publishes a weak ETag and answers a matching If-None-Match with 304. mockdr answered the whole collection every time.  And none of the three runnable products' compression: all three compress when a client offers gzip, they disagree about the details, and one compressor for all of them gets two wrong. Each mount follows its own product now; the six with no runnable product stay uncompressed rather than guessed at.  The harness compares vary as the unordered list it is, and without accept-encoding: whether this answer was compressed depends on how much data each install holds.  25 tests; 4241 backend tests; both conformance suites clean, seeded and not.") | 3 days agoAug 26, 2026 |
| [LICENSE.md](https://github.com/mockdr/mockdr/blob/main/LICENSE.md "LICENSE.md") | [LICENSE.md](https://github.com/mockdr/mockdr/blob/main/LICENSE.md "LICENSE.md") | [Initial commit](https://github.com/mockdr/mockdr/commit/8dbed909dcdc94e75016ada65c40ff12db8872d6 "Initial commit") | 5 months agoMar 19, 2026 |
| [README.md](https://github.com/mockdr/mockdr/blob/main/README.md "README.md") | [README.md](https://github.com/mockdr/mockdr/blob/main/README.md "README.md") | [fix(splunk,elastic): answer with the headers the products answer with](https://github.com/mockdr/mockdr/commit/ce05124b2bdb496afb08c83926fb6f36fda1f7bb "fix(splunk,elastic): answer with the headers the products answer with  Server: uvicorn was on every answer, which is the plainest way there is to tell a mock from the thing it mocks. Under it, measured on 10.4.2 header by header: splunkd says what each answer depends on (Vary: Cookie, Authorization — or Authorization alone for a session token it cannot resolve, refused before its cookie handler, and nothing at all for a collector token read from the query string); it says how each answer may be kept (no-store with its own already-expired Expires of October 1978, private for a credential it refused and for a mode it could not read); and for the one family it serves as cacheable — data/indexes, on a successful read only — it publishes a weak ETag and answers a matching If-None-Match with 304. mockdr answered the whole collection every time.  And none of the three runnable products' compression: all three compress when a client offers gzip, they disagree about the details, and one compressor for all of them gets two wrong. Each mount follows its own product now; the six with no runnable product stay uncompressed rather than guessed at.  The harness compares vary as the unordered list it is, and without accept-encoding: whether this answer was compressed depends on how much data each install holds.  25 tests; 4241 backend tests; both conformance suites clean, seeded and not.") | 3 days agoAug 26, 2026 |
| [SECURITY.md](https://github.com/mockdr/mockdr/blob/main/SECURITY.md "SECURITY.md") | [SECURITY.md](https://github.com/mockdr/mockdr/blob/main/SECURITY.md "SECURITY.md") | [fix: what the TEAMS.md review of 2.1.0 converged on](https://github.com/mockdr/mockdr/commit/d7c972b338f5325a5f632f47c96406dfb3996fe8 "fix: what the TEAMS.md review of 2.1.0 converged on  Three convergent findings from 86 perspectives over the code, done:  1. Bridge events dated by their records. Splunk bridge and Sentinel seeders    stamped every event 2023-11-14 (_SEED_EPOCH) while the records said    2026; earliest=-24h and the seeded ES saved searches found nothing.    utils/event_time.py reads the record's own timestamp. The seeder's    duplicate activity pass is gone (the repository bridges them live).  2. Growth capped. Per-request collections evict oldest-first (store.CAPS:    events, notables, jobs, sessions, ES documents, uploads, OAuth tokens);    request bodies have a 413 ceiling (MOCKDR_MAX_BODY_BYTES, read-free);    fault-injection delay bounded; /metrics labels by route template so    unknown paths cannot add series. Webhook delivery: 5xx retried, 4xx a    rejection, only 2xx/3xx a success (a 500 used to count as delivered);    the public webhook sink redacts credential headers.  3. Map = territory. ADR-001 lock claim, SECURITY.md XSS header, ADR-009    title, FastAPI title and console branding (\"Mock S1\", \"Hypervisor\",    \"7 platforms\"), one coverage gate (85 %, measured 89 %), CORS default on    ports that exist, README env table complete, Vite proxy for every vendor    root, dead Bruno/Postman requests, a CloudFront error page committed as    crowdstrike_swagger.json, get_threat on the shared serializer.    NOTICE.md lists every vendored reference with its licence. CI runs    fuzz_parsers.py and hostile_probe.py on every push.") | last weekAug 23, 2026 |
| [TESTING.md](https://github.com/mockdr/mockdr/blob/main/TESTING.md "TESTING.md") | [TESTING.md](https://github.com/mockdr/mockdr/blob/main/TESTING.md "TESTING.md") | [fix: the review's remaining debts on the backend side](https://github.com/mockdr/mockdr/commit/0ffa61a65309f00f5a8c179896890214c4c2396c "fix: the review's remaining debts on the backend side  - Seed data names nobody real: documentation IP ranges (RFC 5737) and   reserved domains (.example/.test) replace Faker's routable public IPs and   surname domains; the mail-rule seeds no longer forward to gmail.com. - Cortex XDR exclusions, violations and agent reports carried a fixed   2023 timestamp; they are dated within the last day. - The persistence snapshot records the version that wrote it; loading one   from another release says so in the log. - Webhook deliveries run on a bounded pool of eight daemon workers instead   of a sleeping thread per subscription per event; tests wait on   wait_for_deliveries() rather than on thread names. - The Docker image chowns /app to appuser (it was created after the COPYs);   compose notes that read_only and MOCKDR_PERSIST need a volume. - ARCHITECTURE.md describes eight platforms, the measured-fidelity method,   the bridge and the verification tooling (it had stood still since March). - scripts/README.md maps all seventeen scripts to when they run and holds   the release checklist; TESTING.md lists the CI jobs that actually exist. - The three parsers the review flagged for missing depth guards are not   recursive (Graph delegates to the guarded OData engine); no change.") | last weekAug 23, 2026 |
| [action.yml](https://github.com/mockdr/mockdr/blob/main/action.yml "action.yml") | [action.yml](https://github.com/mockdr/mockdr/blob/main/action.yml "action.yml") | [fix(splunk,elastic): answer with the headers the products answer with](https://github.com/mockdr/mockdr/commit/ce05124b2bdb496afb08c83926fb6f36fda1f7bb "fix(splunk,elastic): answer with the headers the products answer with  Server: uvicorn was on every answer, which is the plainest way there is to tell a mock from the thing it mocks. Under it, measured on 10.4.2 header by header: splunkd says what each answer depends on (Vary: Cookie, Authorization — or Authorization alone for a session token it cannot resolve, refused before its cookie handler, and nothing at all for a collector token read from the query string); it says how each answer may be kept (no-store with its own already-expired Expires of October 1978, private for a credential it refused and for a mode it could not read); and for the one family it serves as cacheable — data/indexes, on a successful read only — it publishes a weak ETag and answers a matching If-None-Match with 304. mockdr answered the whole collection every time.  And none of the three runnable products' compression: all three compress when a client offers gzip, they disagree about the details, and one compressor for all of them gets two wrong. Each mount follows its own product now; the six with no runnable product stay uncompressed rather than guessed at.  The harness compares vary as the unordered list it is, and without accept-encoding: whether this answer was compressed depends on how much data each install holds.  25 tests; 4241 backend tests; both conformance suites clean, seeded and not.") | 3 days agoAug 26, 2026 |
| [ci.sh](https://github.com/mockdr/mockdr/blob/main/ci.sh "ci.sh") | [ci.sh](https://github.com/mockdr/mockdr/blob/main/ci.sh "ci.sh") | [perf: serialisation no longer dominates the request; scripts are linted](https://github.com/mockdr/mockdr/commit/a162cf717ef46f08511ecd7f53b15579673f8f74 "perf: serialisation no longer dominates the request; scripts are linted  The weekly load test (new in CI) failed on the runner at read p99 812 ms. Three causes in the path every response takes:  - dataclasses.asdict deep-copies every leaf: 11 700 _asdict_inner calls   per GET /threats. utils/serde.record_dict rebuilds mutable containers   and shares scalars — same isolation from the store, same output. - deep_complete built defaults for keys the record then overwrote. - SecurityHeadersMiddleware ran as BaseHTTPMiddleware (an anyio task group   per request, on all 561 routes); it is pure ASGI now.  GET /threats 7.1 -> 3.4 ms; load test passes (read p99 449 ms pinned to two cores). 199 routes compared across six platforms, 0 drift, 2806 tests.  Also: scripts/ gets its own ruff config and is linted by CI and ci.sh — 34 accumulated findings fixed, among them field_drift binding 0.0.0.0 to reach its own process. load_test.py takes --concurrency so the CI job can scale to a 2-vCPU runner without weakening the gate elsewhere.") | 5 days agoAug 24, 2026 |
| [docker-compose.yml](https://github.com/mockdr/mockdr/blob/main/docker-compose.yml "docker-compose.yml") | [docker-compose.yml](https://github.com/mockdr/mockdr/blob/main/docker-compose.yml "docker-compose.yml") | [fix: the review's remaining debts on the backend side](https://github.com/mockdr/mockdr/commit/0ffa61a65309f00f5a8c179896890214c4c2396c "fix: the review's remaining debts on the backend side  - Seed data names nobody real: documentation IP ranges (RFC 5737) and   reserved domains (.example/.test) replace Faker's routable public IPs and   surname domains; the mail-rule seeds no longer forward to gmail.com. - Cortex XDR exclusions, violations and agent reports carried a fixed   2023 timestamp; they are dated within the last day. - The persistence snapshot records the version that wrote it; loading one   from another release says so in the log. - Webhook deliveries run on a bounded pool of eight daemon workers instead   of a sleeping thread per subscription per event; tests wait on   wait_for_deliveries() rather than on thread names. - The Docker image chowns /app to appuser (it was created after the COPYs);   compose notes that read_only and MOCKDR_PERSIST need a volume. - ARCHITECTURE.md describes eight platforms, the measured-fidelity method,   the bridge and the verification tooling (it had stood still since March). - scripts/README.md maps all seventeen scripts to when they run and holds   the release checklist; TESTING.md lists the CI jobs that actually exist. - The three parsers the review flagged for missing depth guards are not   recursive (Graph delegates to the guarded OData engine); no change.") | last weekAug 23, 2026 |
| [render.yaml](https://github.com/mockdr/mockdr/blob/main/render.yaml "render.yaml") | [render.yaml](https://github.com/mockdr/mockdr/blob/main/render.yaml "render.yaml") | [Initial commit](https://github.com/mockdr/mockdr/commit/8dbed909dcdc94e75016ada65c40ff12db8872d6 "Initial commit") | 5 months agoMar 19, 2026 |
| [start.sh](https://github.com/mockdr/mockdr/blob/main/start.sh "start.sh") | [start.sh](https://github.com/mockdr/mockdr/blob/main/start.sh "start.sh") | [fix: close the remaining review findings across backend and UI](https://github.com/mockdr/mockdr/commit/950512bffc8b0389cbf472bd1b92c75aed621023 "fix: close the remaining review findings across backend and UI  Follow-up to the vendor audit, working through what the reviews turned up but the earlier passes left open.  Splunk had a role model that looked like it protected something and did not: require_splunk_admin was defined and never applied, so the seeded viewer could create indexes, mint HEC tokens and drop KV Store collections. It now guards those endpoints, with sc_admin counting as an administrator the way Splunk Cloud treats it.  The state snapshot registry had fallen behind by three whole vendors — Graph, Sentinel and Splunk, plus hash exceptions. Since loading a snapshot skips seeding, restarting with MOCKDR_PERSIST left those vendors permanently empty. All 65 collections are registered, membership lists that carry no record identifier get a mapping category of their own, and a coverage test now fails the moment a new collection is added without being registered, which is how this gap opened in the first place.  The EDR→SIEM bridge described by ADR-009 was unreachable: neither register function had a call site and nothing ever published to the bus. Both bridges are registered at import — so a test client sees them too — and the mutations that exist publish, so a Defender alert or a triggered scenario now reaches Splunk and Sentinel. subscribe() became idempotent so import- and startup-time wiring cannot double-deliver.  Sentinel crashed with an unhandled ValueError on any $skipToken it had not issued, and returned a bare \"?$skipToken=N\" where ARM returns an absolute URL. Both fixed in a shared helper.  The Webhooks page threw while rendering because it read snake_case field names the API never returns; the tests missed it by mocking the same wrong shape, so they were corrected to the real response. The UI also shipped without a .env, and Vite inlines VITE_* at build time, so every vendor client authenticated as \"undefined\" — start.sh and the Docker build now seed it from .env.example.  Also: the Entra token endpoints answer with flat OAuth 2.0 errors rather than the OData envelope of the API behind them, /graph/v1.0/me refuses app-only auth as real Graph does, MDE supports $count, Graph 404s use each sub-API's own code, /iocs/bulk no longer discards a single-object payload, evicted activities are deleted rather than orphaned, and the XDR key lookup is the O(1) it always claimed to be.") | 2 weeks agoAug 14, 2026 |
| View all files |

## Repository files navigation

# mockdr — Multi-EDR Mock Server

[Permalink: mockdr — Multi-EDR Mock Server](https://github.com/mockdr/mockdr#mockdr--multi-edr-mock-server)

[![CI](https://github.com/mockdr/mockdr/actions/workflows/ci.yml/badge.svg)](https://github.com/mockdr/mockdr/actions/workflows/ci.yml)[![License: BSL 1.1](https://camo.githubusercontent.com/16f9fce765317048cc23bbaef0946b47eacb416dcd659db5b5caf1fdbad62a24/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4c6963656e73652d42534c5f312e312d6f72616e67652e737667)](https://github.com/mockdr/mockdr/blob/main/LICENSE.md)[![Python 3.12](https://camo.githubusercontent.com/9136f14280f09ef3ccc2598b89ae6c61add5c637ce54d78434ef23a8ad7f1432/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f707974686f6e2d332e31322d3337373661622e737667)](https://www.python.org/)[![TypeScript](https://camo.githubusercontent.com/f35f457b0fa683957541e8f38f4398a86057eb8ac1814bda742acc57d7d7dd23/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f747970657363726970742d352d3331373863362e737667)](https://www.typescriptlang.org/)[![Vue 3](https://camo.githubusercontent.com/c5b45f010037f2ced69cdae2e2b566a024d3d8af0214830afece50c8a3d23c51/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f7675652d332d3432623838332e737667)](https://vuejs.org/)[![Docker](https://camo.githubusercontent.com/8aebaef0e768a0e7c6e97cbb2ef3d9ac2309ed9f82cec2a28cc48498d172fd5e/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646f636b65722d72656164792d3234393665642e737667)](https://www.docker.com/)[![mypy: strict](https://camo.githubusercontent.com/de0ac0a7088fdf701fdfd0331026836509d47928f9c9488f7e22d02fc8096ee7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6d7970792d7374726963742d737563636573732e737667)](https://mypy.readthedocs.io/)[![ruff](https://camo.githubusercontent.com/d6c7524504b7d886a9d34c11f44b9d31b2de1a579325b42e932744c4575a063b/68747470733a2f2f696d672e736869656c64732e696f2f656e64706f696e743f75726c3d68747470733a2f2f7261772e67697468756275736572636f6e74656e742e636f6d2f61737472616c2d73682f727566662f6d61696e2f6173736574732f62616467652f76322e6a736f6e)](https://github.com/astral-sh/ruff)

[![Deploy to Render](https://camo.githubusercontent.com/c3053e93bc9f0a2cd84050a5ff9f07cc5e639621a72e50dce48781f4a38f10e2/68747470733a2f2f72656e6465722e636f6d2f696d616765732f6465706c6f792d746f2d72656e6465722d627574746f6e2e737667)](https://render.com/deploy?repo=https://github.com/mockdr/mockdr)

A self-contained mock server for **SentinelOne**, **CrowdStrike Falcon**, **Microsoft Defender for Endpoint**, **Elastic Security**, **Cortex XDR**, **Splunk SIEM**, **Microsoft Sentinel**, and **Microsoft Graph API** (Entra ID, Intune, M365, Security) -- eight security platforms in a single process with realistic seed data, real API paths, and real response envelopes.

SOAR playbooks, SIEM connectors, and automation scripts point at mockdr without modification -- endpoint paths, request/response formats, query parameters, and field names match each vendor's real API.

## Use Cases

[Permalink: Use Cases](https://github.com/mockdr/mockdr#use-cases)

| Who | What they test against mockdr |
| --- | --- |
| **SOAR engineers** | Playbooks for alert triage, threat remediation, agent quarantine -- across all eight vendors without burning lab licences |
| **SIEM integrators** | EDR log ingestion, field mapping, and parser validation with deterministic, repeatable data |
| **Security automation devs** | Python/Go/PowerShell scripts using vendor SDKs -- offline, no VPN, no rate limits |
| **Pentesters / red teamers** | Validate EDR response tooling against realistic agent/threat/alert states before engaging a live tenant |
| **QA engineers** | Regression tests for EDR-integrated products -- seed data resets to a known state on every run |

## Supported Platforms

[Permalink: Supported Platforms](https://github.com/mockdr/mockdr#supported-platforms)

| Platform | Prefix | Auth Method | Response Format |
| --- | --- | --- | --- |
| SentinelOne Singularity API v2.1 | `/web/api/v2.1` | `ApiToken` header | `{"data": [...], "pagination": {...}}` |
| CrowdStrike Falcon | `/cs` | OAuth2 client credentials | `{"resources": [...], "meta": {...}}` |
| Microsoft Defender for Endpoint | `/mde` | OAuth2 client credentials | `{"value": [...]}` (OData) |
| Elastic Security | `/elastic` \+ `/kibana` | Basic Auth or API Key | Elasticsearch / Kibana JSON |
| Cortex XDR | `/xdr/public_api/v1` | API key or SHA-256 digest (`x-xdr-auth-id`) | `{"reply": {...}}` |
| Splunk SIEM | `/splunk` | Basic Auth, Bearer, or HEC token | Splunk REST JSON |
| Microsoft Sentinel | `/sentinel` | OAuth2 client credentials | Azure ARM JSON |
| Microsoft Graph API (Entra ID, Intune, M365, Security) | `/graph` | OAuth2 client credentials (plan-gated) | `{"value": [...]}` (OData) |

## Quick Start

[Permalink: Quick Start](https://github.com/mockdr/mockdr#quick-start)

### One command (no Docker)

[Permalink: One command (no Docker)](https://github.com/mockdr/mockdr#one-command-no-docker)

```
./start.sh
```

- Frontend: [http://localhost:3000](http://localhost:3000/)
- API: [http://localhost:8001](http://localhost:8001/)
- Swagger: [http://localhost:8001/web/api/v2.1/doc](http://localhost:8001/web/api/v2.1/doc)

### Docker

[Permalink: Docker](https://github.com/mockdr/mockdr#docker)

```
docker-compose up --build
```

Everything on a single port -- FastAPI serves both the API and the built frontend:

- App: [http://localhost:5001](http://localhost:5001/)
- API: [http://localhost:5001/web/api/v2.1](http://localhost:5001/web/api/v2.1)

### One-click cloud deploy

[Permalink: One-click cloud deploy](https://github.com/mockdr/mockdr#one-click-cloud-deploy)

[![Deploy to Render](https://camo.githubusercontent.com/c3053e93bc9f0a2cd84050a5ff9f07cc5e639621a72e50dce48781f4a38f10e2/68747470733a2f2f72656e6465722e636f6d2f696d616765732f6465706c6f792d746f2d72656e6465722d627574746f6e2e737667)](https://render.com/deploy?repo=https://github.com/mockdr/mockdr)

Free tier -- no credit card required. Deploys the Docker image with default seed data.

### Manual

[Permalink: Manual](https://github.com/mockdr/mockdr#manual)

```
# Backend
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
PYTHONPATH=. .venv/bin/uvicorn main:app --port 8001 --reload --no-server-header

# Frontend (separate terminal)
cd frontend
cp .env.example .env   # VITE_* mock credentials, inlined at build time
npm install && npm run dev
```

`./start.sh` and the Docker build create `frontend/.env` from `.env.example`
automatically; only the manual path above needs the copy. Without it every
vendor client in the UI authenticates as `undefined`.

## Authentication

[Permalink: Authentication](https://github.com/mockdr/mockdr#authentication)

### SentinelOne

[Permalink: SentinelOne](https://github.com/mockdr/mockdr#sentinelone)

All S1 endpoints require `Authorization: ApiToken <token>`.

| Role | Token |
| --- | --- |
| Admin | `admin-token-0000-0000-000000000001` |
| Viewer | `viewer-token-0000-0000-000000000002` |
| SOC Analyst | `soc-analyst-token-000-000000000003` |

```
curl -H "Authorization: ApiToken admin-token-0000-0000-000000000001" \
  http://localhost:8001/web/api/v2.1/agents
```

### CrowdStrike Falcon

[Permalink: CrowdStrike Falcon](https://github.com/mockdr/mockdr#crowdstrike-falcon)

OAuth2 client credentials flow. POST to `/cs/oauth2/token` with `client_id` \+ `client_secret` to receive a Bearer token.

| Role | Client ID | Client Secret |
| --- | --- | --- |
| Admin | `cs-mock-admin-client` | `cs-mock-admin-secret` |
| Analyst | `cs-mock-analyst-client` | `cs-mock-analyst-secret` |
| Viewer | `cs-mock-viewer-client` | `cs-mock-viewer-secret` |

```
# Get token
TOKEN=$(curl -s -X POST http://localhost:8001/cs/oauth2/token \
  -d "client_id=cs-mock-admin-client&client_secret=cs-mock-admin-secret" | jq -r .access_token)

# Use token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/cs/devices/queries/devices/v1
```

### Microsoft Defender for Endpoint

[Permalink: Microsoft Defender for Endpoint](https://github.com/mockdr/mockdr#microsoft-defender-for-endpoint)

OAuth2 client credentials flow. POST to `/mde/oauth2/v2.0/token` with `client_id`, `client_secret`, and `grant_type=client_credentials`. The tenant-scoped URL real Entra uses — `/mde/{tenant}/oauth2/v2.0/token`, with tenant `a1b2c3d4-e5f6-7890-abcd-ef1234567890` or the verified domain `acmecorp.onmicrosoft.com` — is accepted too, so MSAL-shaped clients work unchanged. The same applies to `/graph` and `/sentinel`; see the [Graph integration guide](https://github.com/mockdr/mockdr/blob/main/docs/graph-integration-guide.md) for tenant validation and `MOCKDR_STRICT_TENANT`.

| Role | Client ID | Client Secret |
| --- | --- | --- |
| Admin | `mde-mock-admin-client` | `mde-mock-admin-secret` |
| Analyst | `mde-mock-analyst-client` | `mde-mock-analyst-secret` |
| Viewer | `mde-mock-viewer-client` | `mde-mock-viewer-secret` |

```
TOKEN=$(curl -s -X POST http://localhost:8001/mde/oauth2/v2.0/token \
  -d "client_id=mde-mock-admin-client&client_secret=mde-mock-admin-secret&grant_type=client_credentials" \
  | jq -r .access_token)

curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/mde/api/machines
```

### Elastic Security

[Permalink: Elastic Security](https://github.com/mockdr/mockdr#elastic-security)

Supports two auth methods: **Basic Auth** and **API Key Auth**. Kibana mutation endpoints also require a `kbn-xsrf` header.

**Basic Auth users:**

| Role | Username | Password |
| --- | --- | --- |
| Admin | `elastic` | `mock-elastic-password` |
| Analyst | `analyst` | `mock-analyst-password` |
| Viewer | `viewer` | `mock-viewer-password` |

**API Keys** (use as `Authorization: ApiKey base64(id:key)`):

| Role | Key ID | API Key |
| --- | --- | --- |
| Admin | `es-admin-key-001` | `mock-es-admin-api-key` |
| Analyst | `es-analyst-key-001` | `mock-es-analyst-api-key` |
| Viewer | `es-viewer-key-001` | `mock-es-viewer-api-key` |

```
# Basic Auth
curl -u elastic:mock-elastic-password http://localhost:8001/elastic/_search

# API Key Auth (base64 of "es-admin-key-001:mock-es-admin-api-key")
curl -H "Authorization: ApiKey ZXMtYWRtaW4ta2V5LTAwMTptb2NrLWVzLWFkbWluLWFwaS1rZXk=" \
  http://localhost:8001/kibana/api/detection_engine/rules/_find
```

### Cortex XDR

[Permalink: Cortex XDR](https://github.com/mockdr/mockdr#cortex-xdr)

Both Cortex XDR authentication levels are supported.

**Standard** — send the key itself: `x-xdr-auth-id` and `Authorization: <secret>`.

**Advanced** — the key never leaves the client; send `x-xdr-auth-id`, `x-xdr-nonce`, `x-xdr-timestamp` and `Authorization`, the latter being `SHA256(key + nonce + timestamp)` over the plain concatenation (no delimiter).

| Role | API Key ID | Secret |
| --- | --- | --- |
| Admin | `1` | `xdr-admin-secret` |
| Analyst | `2` | `xdr-analyst-secret` |
| Viewer | `3` | `xdr-viewer-secret` |

```
# Standard auth — the key goes in the Authorization header
curl -X POST http://localhost:8001/xdr/public_api/v1/incidents/get_incidents/ \
  -H "x-xdr-auth-id: 1" \
  -H "Authorization: xdr-admin-secret" \
  -H "Content-Type: application/json" \
  -d '{"request_data": {}}'

# Advanced auth — hash key + nonce + timestamp instead
NONCE=$(python3 -c "import secrets; print(secrets.token_hex(32))")
TIMESTAMP=$(date +%s%3N)
AUTH=$(python3 -c "import hashlib,sys; print(hashlib.sha256(''.join(sys.argv[1:]).encode()).hexdigest())" \
  "xdr-admin-secret" "$NONCE" "$TIMESTAMP")

curl -X POST http://localhost:8001/xdr/public_api/v1/incidents/get_incidents/ \
  -H "x-xdr-auth-id: 1" \
  -H "x-xdr-nonce: $NONCE" \
  -H "x-xdr-timestamp: $TIMESTAMP" \
  -H "Authorization: $AUTH" \
  -H "Content-Type: application/json" \
  -d '{"request_data": {}}'
```

### Splunk SIEM

[Permalink: Splunk SIEM](https://github.com/mockdr/mockdr#splunk-siem)

Supports **Basic Auth**, a **session key** from login (`Authorization: Splunk <key>`, or `Bearer <key>` in the JWT scheme), and **HEC Tokens** (`Authorization: Splunk <token>`) for HTTP Event Collector endpoints.

Like splunkd, responses are Atom XML unless you ask for JSON with `output_mode=json` — the Splunk SDKs always do. HEC is exempt and always answers JSON.

**Basic Auth users:**

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `mockdr-admin` |
| Analyst | `analyst` | `mockdr-analyst` |
| Viewer | `viewer` | `mockdr-viewer` |

```
# Get session key (output_mode=json — the bare call returns XML, as splunkd does)
SESSION=$(curl -s -X POST "http://localhost:8001/splunk/services/auth/login?output_mode=json" \
  -d "username=admin&password=mockdr-admin" | jq -r .sessionKey)

# Use session key
curl -H "Authorization: Splunk $SESSION" \
  "http://localhost:8001/splunk/services/server/info?output_mode=json"
```

**HEC Tokens** (use as `Authorization: Splunk <token>`):

| Name | Token | Default Index |
| --- | --- | --- |
| mockdr-edr-sentinelone | `11111111-1111-1111-1111-111111111111` | `sentinelone` |
| mockdr-edr-crowdstrike | `22222222-2222-2222-2222-222222222222` | `crowdstrike` |
| mockdr-edr-general | `33333333-3333-3333-3333-333333333333` | `main` |

### Microsoft Sentinel

[Permalink: Microsoft Sentinel](https://github.com/mockdr/mockdr#microsoft-sentinel)

OAuth2 client credentials flow. POST to `/sentinel/oauth2/v2.0/token` with `client_id` \+ `client_secret` to receive a Bearer token.

| Client ID | Client Secret |
| --- | --- |
| `sentinel-mock-client-id` | `sentinel-mock-client-secret` |

Management-plane requests require `?api-version=`, exactly as Azure Resource Manager does — a request without it is answered with `400 MissingApiVersionParameter`. The Log Analytics query endpoint (`/sentinel/v1/workspaces/...`) is not ARM and takes no api-version.

```
TOKEN=$(curl -s -X POST http://localhost:8001/sentinel/oauth2/v2.0/token \
  -d "client_id=sentinel-mock-client-id&client_secret=sentinel-mock-client-secret" \
  | jq -r .access_token)

WS=/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mockdr-rg
WS=$WS/providers/Microsoft.OperationalInsights/workspaces/mockdr-workspace
WS=$WS/providers/Microsoft.SecurityInsights

curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/sentinel$WS/incidents?api-version=2024-03-01"
```

### Microsoft Graph API

[Permalink: Microsoft Graph API](https://github.com/mockdr/mockdr#microsoft-graph-api)

OAuth2 client credentials flow with **plan-based feature gating**. POST to `/graph/oauth2/v2.0/token` with `client_id`, `client_secret`, and `grant_type=client_credentials`.

| Role | Client ID | Client Secret | Plan |
| --- | --- | --- | --- |
| Global Admin | `graph-mock-admin-client` | `graph-mock-admin-secret` | Plan 2 (E5) |
| Security Admin | `graph-mock-security-client` | `graph-mock-security-secret` | Plan 2 (E5) |
| SMB Admin | `graph-mock-smb-client` | `graph-mock-smb-secret` | Defender for Business |
| Plan 1 User | `graph-mock-p1-client` | `graph-mock-p1-secret` | Plan 1 (E3) |
| Intune Admin | `graph-mock-intune-client` | `graph-mock-intune-secret` | Plan 2 (Intune) |
| Mail Only | `graph-mock-mail-client` | `graph-mock-mail-secret` | None (E3) |

```
TOKEN=$(curl -s -X POST http://localhost:8001/graph/oauth2/v2.0/token \
  -d "client_id=graph-mock-admin-client&client_secret=graph-mock-admin-secret&grant_type=client_credentials&scope=https://graph.microsoft.com/.default" \
  | jq -r .access_token)

# Entra ID users
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/graph/v1.0/users?\$select=displayName,userPrincipalName,department"

# Intune managed devices
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/graph/v1.0/deviceManagement/managedDevices

# Plan gating: Plan 1 gets 403 on advanced hunting
P1_TOKEN=$(curl -s -X POST http://localhost:8001/graph/oauth2/v2.0/token \
  -d "client_id=graph-mock-p1-client&client_secret=graph-mock-p1-secret&grant_type=client_credentials" \
  | jq -r .access_token)
curl -X POST -H "Authorization: Bearer $P1_TOKEN" -H "Content-Type: application/json" \
  -d '{"Query":"DeviceProcessEvents | take 5"}' \
  http://localhost:8001/graph/v1.0/security/runHuntingQuery
# → 403 Forbidden
```

**Plan Comparison:**

| Feature | Plan 1 | Plan 2 | Defender for Business |
| --- | --- | --- | --- |
| Users, Groups, CA Policies | ✅ | ✅ | ✅ |
| Mail, Files, Teams | ✅ | ✅ | ✅ |
| Security Alerts & Incidents | ❌ | ✅ | ✅ |
| Advanced Hunting | ❌ | ✅ | ❌ |
| Identity Protection (Risky Users) | ❌ | ✅ | ❌ |
| Intune Device Management | ❌ | ✅ | ✅ |
| Attack Simulation | ❌ | ✅ | ❌ |

## API Coverage

[Permalink: API Coverage](https://github.com/mockdr/mockdr#api-coverage)

### SentinelOne (prefix: `/web/api/v2.1`)

[Permalink: SentinelOne (prefix: /web/api/v2.1)](https://github.com/mockdr/mockdr#sentinelone-prefix-webapiv21)

| Domain | Endpoints |
| --- | --- |
| Agents | List, get, count, passphrases, tags, processes, applications, 20+ agent actions, fetch-files, file download |
| Threats | List, get, timeline, notes (single + bulk), analyst-verdict, incident, mitigate (kill/quarantine/remediate/rollback), mark-as-threat/resolved |
| Alerts | List, get, analyst-verdict, incident |
| Deep Visibility | init-query, query-status, events, events by type, cancel-query |
| Accounts | List, get, create, update |
| Sites | List, get, create, update, delete, reactivate, expire-now |
| Groups | List, get, create, update, delete, move-agents |
| Policies | Get, update (scoped by siteId or groupId) |
| Exclusions | List, create, delete (single + bulk) |
| Blocklist | List, create, delete (single + bulk) |
| Firewall Rules | List, create, update, delete |
| Device Control | List, create, update, delete |
| IOCs | List, create, bulk-create, delete |
| Tags | List, get, create, update, delete, assign/unassign to agents |
| Users | List, get, create, update, delete (single + bulk), generate-api-token, token-details, login-by-token |
| Hashes | Verdict lookup (checks blocklist) |
| Activities | List, types |
| Webhooks | List, get, create, delete, test fire |
| System | Status (public), info, configuration |

### CrowdStrike Falcon (prefix: `/cs`)

[Permalink: CrowdStrike Falcon (prefix: /cs)](https://github.com/mockdr/mockdr#crowdstrike-falcon-prefix-cs)

| Domain | Endpoints |
| --- | --- |
| Auth | `POST /oauth2/token` (client credentials flow) |
| Hosts | List, get, actions (contain, lift\_containment, hide, unhide) |
| Detections | List, get, update status |
| IOCs | CRUD (custom indicators) |
| Host Groups | CRUD + member management |
| Users | Query ids, get by ids (`POST …/users/GET/v1`) |
| Processes | Process detail lookup |
| Quarantine | Query ids, get by ids (`POST …/GET/v1`), actions |
| Cases | Query ids, add/remove tags (the documented routes) |

### Microsoft Defender for Endpoint (prefix: `/mde`)

[Permalink: Microsoft Defender for Endpoint (prefix: /mde)](https://github.com/mockdr/mockdr#microsoft-defender-for-endpoint-prefix-mde)

| Domain | Endpoints |
| --- | --- |
| Auth | `POST /oauth2/v2.0/token` (client credentials flow) |
| Machines | List, get, actions (isolate, unisolate, scan, more) |
| Alerts | List, get, update, create |
| Indicators | List, create, delete, batch delete |
| Machine Actions | List, get, submit actions |
| Investigations | List, get, start |
| Advanced Hunting | Run KQL queries — evaluated, not canned |
| Software | List, get (TVM) |
| Vulnerabilities | List, get (TVM CVEs) |
| File Info | File information lookup |
| Users | List, get |

### Elastic Security (prefixes: `/elastic` \+ `/kibana`)

[Permalink: Elastic Security (prefixes: /elastic + /kibana)](https://github.com/mockdr/mockdr#elastic-security-prefixes-elastic--kibana)

| Domain | Endpoints |
| --- | --- |
| Auth | API key validation, basic auth |
| Search | `POST /_search` (Elasticsearch query DSL) |
| Endpoints | List, get endpoint metadata |
| Detection Rules | CRUD + enable/disable |
| Alerts | List, get, update status |
| Cases | CRUD + comments |
| Exception Lists | CRUD (lists + items) |

### Cortex XDR (prefix: `/xdr/public_api/v1`)

[Permalink: Cortex XDR (prefix: /xdr/public_api/v1)](https://github.com/mockdr/mockdr#cortex-xdr-prefix-xdrpublic_apiv1)

| Domain | Endpoints |
| --- | --- |
| Auth | Standard API key or advanced SHA-256 digest (`x-xdr-auth-id`) |
| Incidents | List, get, update, extra data |
| Alerts | List by filter, list with events (`get_alerts_multi_events`), original alerts, insert (parsed, CEF) |
| Endpoints | List, get, isolate, unisolate, scan, policy |
| Scripts | List, get, execute, execution status/results |
| IOCs | Insert (`tim_insert_jsons`) |
| Actions | Action center — list, get, status |
| Hash Exceptions | Allowlist/blocklist add, remove |
| Audit | Management + agent audit logs |
| Distributions | Distribution list |
| XQL | Start query, get results, quota |
| System | Server info, health check |

### Splunk SIEM (prefix: `/splunk`)

[Permalink: Splunk SIEM (prefix: /splunk)](https://github.com/mockdr/mockdr#splunk-siem-prefix-splunk)

| Domain | Endpoints |
| --- | --- |
| Auth | `POST /services/auth/login` (session key flow) |
| Search | Create, manage, and retrieve search jobs (full SPL) |
| Notable Events | List, get, update notable events (ES workflow) |
| Saved Searches | CRUD + dispatch + history |
| Indexes | List, get, create index metadata |
| Inputs | List data inputs |
| HEC | Event, raw, health, ack (`/services/collector`) |
| KV Store | Full CRUD on collections + batch save |
| Alerts | List, get, delete fired alerts |
| Server | Server info |
| Users | List, get users, roles, capabilities |

#### SPL Search Engine

[Permalink: SPL Search Engine](https://github.com/mockdr/mockdr#spl-search-engine)

mockdr includes a **real SPL parser and execution engine** that runs queries against the in-memory event store. Supported pipeline commands:

Commands run in the order you write them, so `| head 1 | sort _time` and `| sort _time | head 1` differ as they do in Splunk.

| Command | Example | Description |
| --- | --- | --- |
| `search` | `search index=sentinelone NOT sourcetype=stash` | Filter by index, sourcetype, host, field=value; supports `AND`/`OR`/`NOT`, parentheses and `*` wildcards |
| `where` | `where severity="critical" AND count > 5` | Real comparison operators, not just equality |
| `eval` | `eval risk=severity*10, tier=if(risk>50,"high","low")` | Arithmetic, `.` concatenation, `if`/`case`/`coalesce`/`upper` and friends |
| `stats` | `stats count, avg(risk) as mean by classification` | `count`/`sum`/`avg`/`min`/`max`/`dc`/`values`/`list`/`median`, with aliases |
| `timechart` | `timechart span=1h count by sourcetype` | Bucket over time |
| `top` / `rare` | `top 5 sourcetype` | Ranked tables with `count` and `percent` |
| `dedup` | `dedup host sourcetype` | First row per distinct key |
| `table` | `table _time host classification` | Project specific fields |
| `fields` | `fields - _raw` | Include or exclude fields |
| `rex` | `rex field=host "(?<site>^[a-z]+)"` | Extract named capture groups |
| `regex` | `regex host="^wkstn"` | Filter by regular expression |
| `sort` | `sort sourcetype, -count` | Several keys; numeric where the values are numbers |
| `head` / `tail` | `head 20` | First or last N results |
| `rename` | `rename computerName as hostname` | Rename fields |
| `fillnull` | `fillnull value=0 count` | Replace empty values |

Time modifiers (`earliest=-24h@h latest=now`) and the ```notable``` macro are also supported. A command the engine does not implement is reported in the job's `messages` rather than silently ignored, so a query that cannot run does not look like one that returned nothing.

```
# Run a one-shot search
curl -u admin:mockdr-admin -X POST \
  "http://localhost:8001/splunk/services/search/jobs/export" \
  -d 'search=search index=sentinelone sourcetype=sentinelone:channel:threats | stats count by classification | sort -count' \
  -d 'output_mode=json'
```

#### Advanced Hunting (KQL)

[Permalink: Advanced Hunting (KQL)](https://github.com/mockdr/mockdr#advanced-hunting-kql)

`POST /mde/api/advancedqueries/run` evaluates the query against tables projected from the same seeded data the REST endpoints serve, so a hunting result cannot contradict `/api/machines` or `/api/alerts`.

Tables: `DeviceInfo`, `AlertInfo`, `AlertEvidence`, `DeviceTvmSoftwareInventory`, `DeviceTvmSoftwareVulnerabilities`.

Operators: `where`, `project`, `project-away`, `extend`, `summarize ... by`, `order by`, `take`/`limit`, `top`, `distinct`, `count` — with `==`, `!=`, `<`, `>`, `contains`, `startswith`, `endswith`, `has`, `in`, `matches regex`, combined with `and`/`or`/`not`.

```
curl -H "Authorization: Bearer $TOKEN" -X POST \
  "http://localhost:8001/mde/api/advancedqueries/run" \
  -d '{"Query":"DeviceInfo | where OSPlatform == \"Windows10\" | summarize Devices=count() by HealthStatus | order by Devices desc"}'
```

A query naming a table that does not exist, or an operator the engine does not implement, is answered with `400` rather than rows that were never asked for.

### Microsoft Sentinel (prefix: `/sentinel`)

[Permalink: Microsoft Sentinel (prefix: /sentinel)](https://github.com/mockdr/mockdr#microsoft-sentinel-prefix-sentinel)

| Domain | Endpoints |
| --- | --- |
| Auth | `POST /oauth2/v2.0/token` (Azure AD client creds) |
| Incidents | List, get, create, update, delete + comments |
| Alert Rules | List, get, create, update, delete (analytics rules) |
| Data Connectors | List, get, create, delete |
| Watchlists | List, get, create, update, delete + items |
| Threat Intelligence | List, get, create, delete indicators |
| Bookmarks | List, get, create, update, delete |
| Log Analytics | Run KQL queries |
| Operations | Get long-running operation status |

### Microsoft Graph API (prefix: `/graph`)

[Permalink: Microsoft Graph API (prefix: /graph)](https://github.com/mockdr/mockdr#microsoft-graph-api-prefix-graph)

| Domain | Endpoints |
| --- | --- |
| Auth | `POST /oauth2/v2.0/token` (Azure AD, plan-gated) |
| Organization | Get tenant info |
| Users | List, get, memberOf, mail rules (v1.0 + beta) |
| Groups | List, get, members |
| Directory Roles | List, get members |
| Auth Methods | User registration details (MFA status) |
| Service Principals | List with OData |
| Applications | List with OData |
| Conditional Access | Policies, named locations, admin units |
| Licenses | subscribedSkus |
| Sign-In Logs | List with $filter |
| Audit Logs | List with $filter |
| Identity Protection | Risky users, risk detections (plan-gated) |
| Managed Devices | List, get, $count, device actions (wipe, retire, sync, scan ...) |
| Detected Apps | List, get devices per app |
| Compliance | Policies, device configurations |
| Autopilot | Devices, deployment profiles |
| App Management | MAM policies, mobile apps |
| Update Rings | Windows Update for Business configurations |
| Enrollment | Restrictions, device categories |
| Security Alerts v2 | List, get, patch |
| Incidents | List, get with $expand=alerts |
| Advanced Hunting | Run KQL queries (plan-gated) |
| Secure Scores | List daily snapshots |
| TI Indicators | List, create, delete |
| Mail | Messages, folders, send mail |
| Files | OneDrive drives/items, SharePoint sites |
| Teams | Teams, channels, messages |
| Attack Simulation | List simulations (plan-gated) |
| Threat Assessment | List, create |
| Service Health | Health overviews |

## Seed Data

[Permalink: Seed Data](https://github.com/mockdr/mockdr#seed-data)

Deterministic seed (`random.seed(42)` \+ `Faker.seed(42)`) \-\- same data every cold start. Reset at any time via the DEV panel or `POST /_dev/reset`.

### SentinelOne

[Permalink: SentinelOne](https://github.com/mockdr/mockdr#sentinelone-1)

- 1 account, 3 sites, 9 groups
- **60 agents** \-\- Windows/macOS/Linux; desktop/laptop/server; online/offline; tagged; ~18% running EOL operating systems (Windows 8.1, Windows 10 1809, macOS Big Sur, CentOS 7)
- **30 threats** \-\- Emotet, TrickBot, Ryuk, WannaCry, LockBit, etc.
- **20 alerts** \-\- STAR/UAM alerts with all severity/verdict/status combinations
- 15 exclusions, 10 blocklist entries, 8 firewall rules, 6 device control rules, 20 IOCs
- 120 activity log entries spanning 90 days

### CrowdStrike Falcon

[Permalink: CrowdStrike Falcon](https://github.com/mockdr/mockdr#crowdstrike-falcon-1)

- **60 hosts** (mirrored from S1 agent fleet)
- **30 detections** with 1-3 behaviors each
- **15 incidents** grouping hosts and detections
- 5 host groups (3 dynamic, 2 static), 20 IOCs, 8 users, 15 quarantined files, 8 cases

### Microsoft Defender for Endpoint

[Permalink: Microsoft Defender for Endpoint](https://github.com/mockdr/mockdr#microsoft-defender-for-endpoint-1)

- **60 machines** (mirrored from S1 agent fleet)
- **40 alerts** with evidence items and comments
- 20 indicators (FileSha256, IpAddress, DomainName)
- 15 machine actions, 10 automated investigations
- ~52 TVM software entries (corporate, EDR agents + outdated versions, EOL, torrent clients, dual-use tools)
- ~15 TVM vulnerability (CVE) records

### Elastic Security

[Permalink: Elastic Security](https://github.com/mockdr/mockdr#elastic-security-1)

- **60 endpoints** (mirrored from S1 agent fleet)
- **45 alerts** linked to rules and endpoints
- 25 detection rules (KQL, EQL, threshold)
- 8 cases with 2-5 comments each
- 5 exception lists with exception items

### Cortex XDR

[Permalink: Cortex XDR](https://github.com/mockdr/mockdr#cortex-xdr-1)

- **60 endpoints** (mirrored from S1 agent fleet)
- **20 incidents** with linked alerts and endpoints
- **40 alerts** across multiple severity levels
- ~20 IOCs (hash, IP, domain), 10 hash exceptions (6 blocklist + 4 allowlist)
- 10 scripts with execution history, 15 action center entries
- 30 audit log entries, 5 distribution packages

### Splunk SIEM

[Permalink: Splunk SIEM](https://github.com/mockdr/mockdr#splunk-siem-1)

All five EDR vendor data sets are **replayed into Splunk indexes** with realistic sourcetypes and field extractions -- the same data, indexed for SIEM analysis.

**Indexes (9):**

| Index | Content | Sourcetypes |
| --- | --- | --- |
| `sentinelone` | S1 threats, agents, activities | `sentinelone:channel:threats`, `sentinelone:channel:agents`, `sentinelone:channel:activities` |
| `crowdstrike` | CS detections, incidents | `CrowdStrike:Event:Streams:JSON` |
| `msdefender` | MDE alerts, machines | `ms:defender:atp:alerts`, `ms:defender:machines` |
| `elastic_security` | Elastic alerts, endpoints | `elastic:security:alerts`, `elastic:security:endpoints` |
| `cortex_xdr` | XDR incidents, alerts, endpoints | `pan:xdr:incident`, `pan:xdr:alert`, `pan:xdr:endpoint` |
| `notable` | ES notable events from all 5 vendors | `stash` |
| `main` | Default index | — |
| `_internal` | Splunk internal logs | — |
| `_audit` | Audit logs | — |

**Notable events** are auto-generated from EDR threat/detection/alert data with severity mapping, drilldown SPL queries, and status workflow (New → In Progress → Resolved → Closed).

**Saved searches (5):** One per EDR vendor -- "SentinelOne Threats - Last 24h", "CrowdStrike High Severity Detections", "All EDR Notable Events", "Microsoft Defender Alerts", "Cortex XDR Incidents".

**HEC tokens (3):** SentinelOne (`11111111-...`), CrowdStrike (`22222222-...`), General (`33333333-...`).

**KV Store collections (2):**`splunk_xsoar_users` (XSOAR↔Splunk user mapping), `incident_review_lookup` (notable event triage state).

**Users (3):** admin, analyst, viewer -- matching the auth table above.

**UI (6 views):** SPL search editor, SIEM dashboard with charts, notable event triage, notable detail with drilldown, index browser, HEC token management.

#### Training Examples

[Permalink: Training Examples](https://github.com/mockdr/mockdr#training-examples)

```
# List all SentinelOne threats by classification
search index=sentinelone sourcetype=sentinelone:channel:threats
  | stats count by classification | sort -count

# Find high-severity CrowdStrike detections
search index=crowdstrike sourcetype="CrowdStrike:Event:Streams:JSON"
  | where Severity>=4 | table _time ComputerName DetectName Severity

# Triage open notable events across all EDR vendors
search `notable` | where status="New"
  | table _time rule_name severity src dest owner

# Cross-vendor threat overview
search index=sentinelone OR index=crowdstrike OR index=msdefender
  | stats count by index | sort -count
```

### Microsoft Sentinel

[Permalink: Microsoft Sentinel](https://github.com/mockdr/mockdr#microsoft-sentinel-1)

- Incidents replayed from all 5 EDR vendor data (MDE, S1, CS, Elastic, XDR)
- 5 analytics rules (one per EDR vendor)
- 5 data connectors, 3 watchlists, 3 threat intelligence indicators
- Investigation bookmarks (first 3 incidents) and comments (first 5 incidents)

### Microsoft Graph API

[Permalink: Microsoft Graph API](https://github.com/mockdr/mockdr#microsoft-graph-api-1)

- **28 Entra users** — 25 employees (mapped from MDE machine loggedOnUsers + Faker), 3 external guests (B2B contractors/partners); ~72% active, ~8% stale (enabled but no sign-in for 90+ days), ~20% disabled (former employees)
- **10 groups** (6 department, 1 M365, 1 Security, 2 dynamic)
- **8 directory roles** with real roleTemplateIds — 5 Global Admins (CIS violation: max 4), disabled users in privileged roles
- **25 MFA registration details** (~80% MFA registered); Security Administrator without MFA
- **4 mail forwarding rules** — former employee forwarding to `competitor.com` and `external-consulting.com`; active employee forwarding invoices to personal `gmail.com`
- **8 service principals** — 2 unverified apps with `Files.ReadWrite.All` scope
- **6 conditional access policies** (1 in report-only mode), 3 named locations, 2 admin units
- **5 license SKUs** — Intune P1 at 96% consumed (near-exhaustion warning)
- **200 sign-in logs** (30 days: ~70% success, ~15% MFA, ~10% failed, ~5% blocked by CA)
- **100 audit logs** (user/group/policy management activities)
- **5 risky users** (2 high, 2 medium, 1 dismissed) + **15 risk detections** (6 event types)
- **66 managed devices** — 60 mirrored from S1 fleet (same EOL OS visible across all vendors) + 6 mobile devices (3 company iOS/Android, 3 personal BYOD noncompliant)
- **30 detected apps** with device mappings
- **5 compliance policies**, 4 device configurations, 20 Autopilot devices, 3 profiles
- **4 MAM policies**, 12 mobile apps, 3 update rings
- **40 security alerts** (mapped from MDE), **15 incidents** (grouped), **30 secure scores**, **20 TI indicators**
- **75 mail messages**, 25 folders, 5 OneDrive drives, 40 drive items, 2 SharePoint sites
- **4 teams**, 10 channels, 25 channel messages
- **3 attack simulations**, 5 threat assessments, 6 service health entries

**Compliance violations baked into seed data:** former employees with admin roles and external mail forwarding, app tokens not revoked after offboarding, too many Global Admins, admin without MFA, stale accounts, unverified apps with broad permissions, EOL operating systems, BYOD devices, CA policies in report-only mode, license near-exhaustion. See [Graph Integration Guide](https://github.com/mockdr/mockdr/blob/main/docs/graph-integration-guide.md) for the full findings table.

All data is **in-memory** by default -- mutations survive until server restart or `/_dev/reset`.

**Optional persistence:** set `MOCKDR_PERSIST=/path/to/state.json` to save state across restarts. The server debounces writes (2 s) and uses atomic file replacement to prevent corruption. The snapshot records the version that wrote it; loading one from another release logs which, and a snapshot whose records no longer parse is moved to `state.json.corrupt` and the server seeds fresh rather than serve a hollowed-out store. In Docker the path must be on a writable volume — the compose file runs the container `read_only`.

## Configuration

[Permalink: Configuration](https://github.com/mockdr/mockdr#configuration)

| Variable | Default | Description |
| --- | --- | --- |
| `SEED_COUNT_AGENTS` | 60 | S1 agents to seed (CS/MDE/Elastic/XDR/Graph mirror this count; Splunk/Sentinel replay from all EDR data) |
| `SEED_COUNT_THREATS` | 30 | S1 threats to seed |
| `SEED_COUNT_ALERTS` | 20 | S1 alerts to seed |
| `MOCKDR_PERSIST` | (none) | File path for JSON state persistence across restarts |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:8001,http://localhost:5001` | Comma-separated allowed CORS origins |
| `MOCKDR_STRICT_TENANT` | `true` | Require the tenant in an Entra token URL (`/{tenant}/oauth2/v2.0/token`) to match the mock tenant; set `false` to accept any tenant |
| `MOCKDR_SPLUNK_DISPATCH_SECONDS` | `0` | How long a Splunk search job takes to reach `DONE`. `0` completes immediately and keeps responses deterministic; set e.g. `5` to make `QUEUED` → `PARSING` → `RUNNING` → `FINALIZING` observable, so a client's `isDone` polling loop is actually exercised |
| `MOCKDR_SPLUNK_HEC_QUERY_STRING_AUTH` | `false` | Whether HEC honours its token as `?token=`, mirroring `inputs.conf`'s `allowQueryStringAuth`. Off by default because that is splunkd's default: a valid token sent this way is refused with `400 {"code": 16}` until the setting is on |
| `MOCKDR_MAX_BODY_BYTES` | `16777216` (16 MiB) | Largest request body accepted; a larger one answers `413` before any byte is read, as a reverse proxy in front of the real products would |
| `SPLUNK_SESSION_TTL_SECONDS` | `28800` | Lifetime of a Splunk session key from `/services/auth/login` |
| `ES_ADMIN_PASSWORD`, `ES_ANALYST_PASSWORD`, `ES_VIEWER_PASSWORD` | `mock-elastic-password`, `mock-analyst-password`, `mock-viewer-password` | Passwords of the three Elasticsearch users; the only credentials that can be changed without editing a seeder |

## Middleware Stack

[Permalink: Middleware Stack](https://github.com/mockdr/mockdr#middleware-stack)

Eight ASGI middleware layers run on every request (outermost first):

| Middleware | Purpose |
| --- | --- |
| Metrics | Request timing, status code counters (`GET /metrics`) |
| Request Logging | Structured JSON logs for every request |
| Rate Limit | Configurable per-minute rate limiting (`/_dev/rate-limit`) |
| Security Headers | HSTS, X-Content-Type-Options, CSP, etc. |
| Request Audit | Append to queryable audit log (`/_dev/requests`) |
| Tenant Scope | Non-admin tokens auto-scoped to their account |
| Fault Injection | Artificial latency + random errors (`/_dev/fault-injection`) |
| Recording Proxy | Record/replay real vendor API calls (all 8 vendors) |

## DEV Mock Controls

[Permalink: DEV Mock Controls](https://github.com/mockdr/mockdr#dev-mock-controls)

Floating bug icon (bottom-right corner of the UI):

| Control | Description |
| --- | --- |
| Live stats | Agent / threat / alert counts |
| Role switcher | Switch between the three preset tokens |
| Mass Infection | Infect 20 random agents |
| APT Campaign | Targeted attack on 10 agents |
| Agents Offline | Take 30% of agents offline |
| Quiet Day | Resolve all threats, heal all agents |
| Compliance Drift | Mark ~30% of Graph managed devices non-compliant |
| MFA Gap | Disable MFA for ~40% of Graph users |
| Risky Sign-In Wave | Generate 20 risky sign-in log entries in Graph |
| License Exhaustion | Exhaust all Graph license SKUs |
| Reset to Seed Data | Wipe mutations, restore original seed |
| API Tokens | Copy any preset token to clipboard |

## DEV Endpoints

[Permalink: DEV Endpoints](https://github.com/mockdr/mockdr#dev-endpoints)

Non-standard endpoints for tooling, test automation, and mock control:

| Endpoint | Description |
| --- | --- |
| `POST /_dev/reset` | Re-seed all data (all eight vendors) |
| `POST /_dev/scenario` | Trigger a scenario (see [Scenarios](https://github.com/mockdr/mockdr#scenarios) below) |
| `GET /_dev/stats` | Collection counts |
| `GET /_dev/tokens` | All valid API tokens |
| `GET /_dev/requests` | Request audit log |
| `DELETE /_dev/requests` | Clear request audit log |
| `GET /_dev/export` | Export full store snapshot (JSON) |
| `POST /_dev/import` | Import store snapshot |
| `GET /_dev/rate-limit` | Get rate-limit configuration |
| `POST /_dev/rate-limit` | Update rate-limit configuration |
| `GET /_dev/playbooks` | List playbooks (built-in + custom) |
| `GET /_dev/playbooks/status` | Current playbook execution status |
| `GET /_dev/playbooks/{id}` | Playbook detail with all steps |
| `POST /_dev/playbooks/{id}/run` | Execute a playbook against an agent |
| `POST /_dev/playbooks` | Create custom playbook |
| `PUT /_dev/playbooks/{id}` | Update existing playbook |
| `DELETE /_dev/playbooks/{id}` | Delete playbook |
| `DELETE /_dev/playbooks/cancel` | Cancel active playbook execution |
| `GET /_dev/webhooks/deliveries` | Webhook delivery log (newest first) |
| `POST /_dev/webhook-sink` | Capture incoming webhook (unauthenticated) |
| `GET /_dev/webhook-sink` | List captured webhooks |
| `DELETE /_dev/webhook-sink` | Clear all captured webhooks |
| `GET /_dev/fault-injection` | Get fault injection config |
| `POST /_dev/fault-injection` | Update fault injection (delay, error rate) |
| `DELETE /_dev/fault-injection` | Reset fault injection to defaults |
| `GET /_dev/export/logs` | Unified structured log export (SIEM-ready) |
| `GET /_dev/proxy/config` | Get recording proxy mode and per-vendor settings (secrets masked) |
| `POST /_dev/proxy/config` | Set proxy mode and per-vendor upstream connections |
| `GET /_dev/proxy/recordings` | List all recorded exchanges (newest first) |
| `DELETE /_dev/proxy/recordings` | Clear all recordings |
| `GET /_dev/proxy/vendors` | List supported vendor keys, labels, and default auth types |

### Scenarios

[Permalink: Scenarios](https://github.com/mockdr/mockdr#scenarios)

`POST /_dev/scenario` with `{"scenario": "<name>"}`:

| Scenario | Vendor | Description |
| --- | --- | --- |
| `mass_infection` | SentinelOne | Infect 20 random agents with threats |
| `apt_campaign` | SentinelOne | Targeted attack: compromise 10 agents |
| `agent_offline` | SentinelOne | Disconnect ~33% of agents |
| `quiet_day` | SentinelOne | Resolve all threats, heal all agents |
| `compliance_drift` | Microsoft Graph | Mark ~30% of managed devices non-compliant |
| `mfa_gap` | Microsoft Graph | Disable MFA for ~40% of users |
| `risky_signin_wave` | Microsoft Graph | Generate 20 risky sign-in log entries |
| `license_exhaustion` | Microsoft Graph | Exhaust all license SKUs |

## Recording Proxy

[Permalink: Recording Proxy](https://github.com/mockdr/mockdr#recording-proxy)

mockdr includes a built-in **recording proxy** that can forward requests to real vendor APIs, record the exchanges, and replay them later. This is useful for:

- Capturing real API responses to validate mock fidelity
- Building deterministic regression test fixtures from real data
- Offline testing against recorded real-world responses

### Supported Vendors

[Permalink: Supported Vendors](https://github.com/mockdr/mockdr#supported-vendors)

The proxy supports **all eight vendors** with vendor-appropriate authentication:

| Vendor | Auth Method | Example Base URL |
| --- | --- | --- |
| SentinelOne | `ApiToken` header | `https://tenant.sentinelone.net` |
| CrowdStrike Falcon | OAuth2 client credentials | `https://api.crowdstrike.com` |
| Microsoft Defender | OAuth2 client credentials | `https://api.securitycenter.microsoft.com` |
| Elastic Security | Basic Auth / API Key | `https://elastic.example.com:9200` |
| Cortex XDR | API key (key ID + secret) | `https://api-tenant.xdr.paloaltonetworks.com` |
| Splunk SIEM | Basic Auth / Bearer | `https://splunk.example.com:8089` |
| Microsoft Sentinel | OAuth2 client credentials | `https://management.azure.com` |
| Microsoft Graph | OAuth2 client credentials | `https://graph.microsoft.com` |

### Three Modes

[Permalink: Three Modes](https://github.com/mockdr/mockdr#three-modes)

| Mode | Behavior |
| --- | --- |
| `off` (default) | No-op -- all requests served by mock |
| `record` | Forward to real vendor API, save the exchange, return the real response |
| `replay` | Serve from saved recordings (matched by vendor + method + path); fall back to mock if no match |

Dev paths (`/_dev/*`) always bypass the proxy.

### Configuration

[Permalink: Configuration](https://github.com/mockdr/mockdr#configuration-1)

Configure via the UI (Recording Proxy page) or the API:

```
# Configure CrowdStrike proxy
curl -X POST http://localhost:8001/web/api/v2.1/_dev/proxy/config \
  -H "Authorization: ApiToken admin-token-0000-0000-000000000001" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "record",
    "vendors": [\
      {\
        "vendor": "crowdstrike",\
        "base_url": "https://api.crowdstrike.com",\
        "auth": {\
          "type": "oauth2",\
          "client_id": "YOUR_CLIENT_ID",\
          "client_secret": "YOUR_CLIENT_SECRET",\
          "token_url": "https://api.crowdstrike.com/oauth2/token"\
        }\
      },\
      {\
        "vendor": "s1",\
        "base_url": "https://tenant.sentinelone.net",\
        "auth": {\
          "type": "api_token",\
          "token": "YOUR_S1_TOKEN"\
        }\
      }\
    ]
  }'

# Switch to replay mode
curl -X POST http://localhost:8001/web/api/v2.1/_dev/proxy/config \
  -H "Authorization: ApiToken admin-token-0000-0000-000000000001" \
  -H "Content-Type: application/json" \
  -d '{"mode": "replay"}'
```

Multiple vendors can be configured simultaneously -- each vendor's requests are routed independently based on URL prefix. Vendors without a configured `base_url` fall through to the mock.

### Persistence

[Permalink: Persistence](https://github.com/mockdr/mockdr#persistence)

- **Proxy config** (vendor connections) is included in the `MOCKDR_PERSIST` snapshot and survives restarts.
- **Proxy config** survives `/_dev/reset` (only mock data is re-seeded, not proxy settings).
- **Recordings** are in-memory only (max 1,000, circular buffer). Export via `GET /_dev/proxy/recordings` to persist externally.
- **OAuth2 token cache** is in-memory only -- tokens are short-lived and re-fetched as needed.

## Architecture

[Permalink: Architecture](https://github.com/mockdr/mockdr#architecture)

```
backend/
├── domain/                    # Pure dataclasses — field names match each vendor's API
│   ├── cs_*.py                # CrowdStrike domain models (host, detection, incident, ...)
│   ├── mde_*.py               # MDE domain models (machine, alert, indicator, ...)
│   ├── es_*.py                # Elastic domain models (endpoint, rule, alert, ...)
│   ├── xdr_*.py               # Cortex XDR domain models (incident, alert, endpoint, ...)
│   ├── graph/                 # Microsoft Graph models (30 files: user, device, alert, ...)
│   ├── sentinel/              # Microsoft Sentinel domain models
│   └── splunk/                # Splunk SIEM domain models
├── repository/                # Generic Repository[T] + thread-safe InMemoryStore
│   ├── store.py               # Thread-safe in-memory store (RLock, named collections)
│   ├── base.py                # Repository[T] generic base class
│   ├── *_repo.py              # S1, CS, MDE, Elastic, XDR per-domain repos
│   ├── graph/                 # Graph repositories (30 files)
│   ├── sentinel/              # Sentinel repositories
│   └── splunk/                # Splunk repositories
├── application/               # CQRS layer — one module per domain
│   ├── agents/                # S1 agents: queries.py + commands.py
│   ├── threats/               # S1 threats: queries.py + commands.py
│   ├── cs_*/                  # CrowdStrike modules (hosts, detections, incidents, ...)
│   ├── mde_*/                 # MDE modules (machines, alerts, indicators, hunting, ...)
│   ├── es_*/                  # Elastic modules (search, rules, alerts, cases, ...)
│   ├── xdr_*/                 # Cortex XDR modules (incidents, alerts, endpoints, xql, ...)
│   ├── graph/                 # Graph modules (20 submodules: users, devices, security, ...)
│   │   ├── users/             #   queries.py — Entra ID user queries
│   │   ├── device_management/ #   queries.py — Intune device queries
│   │   ├── security/          #   queries.py — alerts, incidents, hunting, scores, TI
│   │   ├── mail/              #   queries.py — messages, folders, send
│   │   └── ...                #   + groups, identity, files, teams, etc.
│   ├── sentinel/              # Sentinel application logic
│   ├── splunk/                # Splunk application logic
│   └── playbook/              # SOAR-like playbook engine
├── api/
│   ├── auth.py                # S1 ApiToken auth
│   ├── cs_auth.py             # CrowdStrike OAuth2 Bearer auth
│   ├── mde_auth.py            # MDE OAuth2 Bearer auth
│   ├── es_auth.py             # Elastic Basic Auth + API Key auth
│   ├── xdr_auth.py            # Cortex XDR API key auth
│   ├── splunk_auth.py         # Splunk Basic Auth + Bearer + HEC auth
│   ├── sentinel_auth.py       # Sentinel Azure AD OAuth2 auth
│   ├── graph_auth.py          # Graph Azure AD OAuth2 auth (plan-gated)
│   ├── dto/                   # Pydantic request models (HTTP boundary only)
│   ├── middleware/             # 8 ASGI middleware classes
│   └── routers/               # Thin FastAPI routers — one file per domain per vendor
│       ├── cs_*.py            # CrowdStrike routers (13 modules)
│       ├── mde_*.py           # MDE routers (11 modules)
│       ├── es_*.py            # Elastic routers (7 modules)
│       ├── xdr_*.py           # Cortex XDR routers (11 modules)
│       ├── graph/             # Microsoft Graph routers (24 modules)
│       ├── splunk/            # Splunk SIEM routers (10 modules)
│       └── sentinel/          # Microsoft Sentinel routers (9 modules)
├── utils/
│   ├── mde_odata.py           # OData v4 $filter parser (MDE)
│   ├── graph_odata.py         # Graph OData extensions ($count, $search, lambda)
│   ├── cs_fql.py              # CrowdStrike FQL parser
│   ├── graph_response.py      # Graph OData response envelope builder
│   └── ...                    # pagination, filtering, field stripping, etc.
└── infrastructure/
    ├── seed.py                # Orchestrator — calls per-domain seeders for all 8 vendors
    └── seeders/               # Per-domain Faker-based deterministic data generators (seed 42)
        ├── agents.py          # S1 agent seeder (base fleet: 60 agents)
        ├── cs_*.py            # CrowdStrike seeders (hosts mirrored from S1 fleet)
        ├── mde_*.py           # MDE seeders (machines mirrored from S1 fleet)
        ├── graph/             # Graph seeders (28 files: users, devices, security, mail, ...)
        ├── splunk/            # Splunk infrastructure + EDR event replay seeders
        └── sentinel/          # Sentinel infrastructure + incident correlation seeders

frontend/                      # Vue 3 + TypeScript — vue-tsc strict, ESLint zero-warnings
└── src/
    ├── api/                   # Axios client + typed domain API modules (14 modules)
    │   ├── crowdstrike.ts     # CrowdStrike API client
    │   ├── defender.ts        # MDE API client
    │   ├── elastic.ts         # Elastic Security API client
    │   ├── graph.ts           # Microsoft Graph API client (plan-aware, 10 namespaces)
    │   ├── sentinel.ts        # Sentinel API client
    │   ├── splunk.ts          # Splunk API client
    │   └── ...                # + S1, cortex, dev, system, agents, threats, alerts, tags
    ├── stores/                # Pinia stores
    ├── types/                 # Shared interfaces mirroring each vendor API
    │   ├── index.ts           # S1 + shared types
    │   └── graph.ts           # Microsoft Graph types (25+ interfaces)
    ├── components/            # Shared UI + DevMockPanel (scenarios, role switcher)
    └── views/                 # One view per UI page
        ├── cs/                # CrowdStrike views (5)
        ├── elastic/           # Elastic Security views (6)
        ├── graph/             # Microsoft Graph views (9: dashboard, users, devices, ...)
        ├── mde/               # Microsoft Defender views (6)
        ├── xdr/               # Cortex XDR views (6)
        ├── splunk/            # Splunk SIEM views (6)
        └── sentinel/          # Microsoft Sentinel views (6)
```

## Testing

[Permalink: Testing](https://github.com/mockdr/mockdr#testing)

See [TESTING.md](https://github.com/mockdr/mockdr/blob/main/TESTING.md) for the full test standard.

## GitHub Action

[Permalink: GitHub Action](https://github.com/mockdr/mockdr#github-action)

Use mockdr as a service in your CI pipeline:

```
- uses: mockdr/mockdr@main
  with:
    port: 5001
    api-token: admin-token-0000-0000-000000000001

- run: pytest --base-url http://localhost:5001
```

The action starts the server, waits for it to be healthy, and exposes `base-url` and `api-token` outputs. All eight vendor mocks are available on the same port.

## Docker

[Permalink: Docker](https://github.com/mockdr/mockdr#docker-1)

```
# Build and run
docker build -t mockdr .
docker run -p 5001:5001 mockdr

# With persistence
docker run -p 5001:5001 -e MOCKDR_PERSIST=/data/state.json -v mockdr-data:/data mockdr
```

The image uses a multi-stage build (Node 20 for frontend, Python 3.12-slim for runtime) with a built-in healthcheck.

## Contributing

[Permalink: Contributing](https://github.com/mockdr/mockdr#contributing)

See [CONTRIBUTING.md](https://github.com/mockdr/mockdr/blob/main/CONTRIBUTING.md) for development setup, code standards, and PR guidelines.

## License

[Permalink: License](https://github.com/mockdr/mockdr#license)

mockdr is source-available under the **[Business Source License 1.1](https://github.com/mockdr/mockdr/blob/main/LICENSE.md)**.

| Use case | License required? |
| --- | --- |
| Personal use, learning, hobby projects | ✅ Free |
| Evaluation / proof of concept (30 days) | ✅ Free |
| Open-source projects (OSI-approved license) | ✅ Free |
| Non-profit / educational internal use | ✅ Free |
| **Commercial use by for-profit companies** | **💼 Commercial license** |
| **Embedding in commercial products** | **💼 Commercial license** |
| **Offering as a hosted / managed service** | **💼 Commercial license** |

Each release converts to **Apache 2.0** four years after publication.

See [COMMERCIAL\_LICENSE.md](https://github.com/mockdr/mockdr/blob/main/COMMERCIAL_LICENSE.md) for plans, pricing,
and FAQ — or contact **[licensing@mockdr.io](mailto:licensing@mockdr.io)**.

Copyright (c) 2026 Guenter Weber. All rights reserved.

## About

Multi-EDR & SIEM mock server. SentinelOne, CrowdStrike, Defender, Elastic, Cortex XDR, Splunk, M365 and Sentinel — 8 platforms in one process. Real API paths, real auth, deterministic seed data, fault injection, scenario engine, SPL parser. GitHub Action + one-click Render deploy. BSL-1.1

[mockdr.io](https://mockdr.io/)

### Topics

[api-mock](https://github.com/topics/api-mock) [cortex-xdr](https://github.com/topics/cortex-xdr) [crowdstrike](https://github.com/topics/crowdstrike) [edr](https://github.com/topics/edr) [elastics-security](https://github.com/topics/elastics-security) [github-actions](https://github.com/topics/github-actions) [m365](https://github.com/topics/m365) [microsoft-sentinel](https://github.com/topics/microsoft-sentinel) [mock-server](https://github.com/topics/mock-server) [mocrosoft-defender](https://github.com/topics/mocrosoft-defender) [security-automation](https://github.com/topics/security-automation) [sentinelone](https://github.com/topics/sentinelone) [siem](https://github.com/topics/siem) [soar](https://github.com/topics/soar) [splunk](https://github.com/topics/splunk) [testing](https://github.com/topics/testing)

### Resources

[Readme](https://github.com/mockdr/mockdr#readme-ov-file)

[License](https://github.com/mockdr/mockdr#License-1-ov-file)

### Code of conduct

[Code of conduct](https://github.com/mockdr/mockdr#coc-ov-file)

### Contributing

[Contributing](https://github.com/mockdr/mockdr#contributing-ov-file)

### Security policy

[Security policy](https://github.com/mockdr/mockdr#security-ov-file)

[Activity](https://github.com/mockdr/mockdr/activity)

[Custom properties](https://github.com/mockdr/mockdr/custom-properties)

### Stars

**52** stars

### Watchers

**0** watching

### Forks

[**3** forks](https://github.com/mockdr/mockdr/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fmockdr%2Fmockdr&report=mockdr+%28user%29)

## [Releases](https://github.com/mockdr/mockdr/releases) 10 (10)

[mockdr v2.3.0Latest\\
\\
5 days agoAug 24, 2026](https://github.com/mockdr/mockdr/releases/tag/v2.3.0)

[\+ 9 releases](https://github.com/mockdr/mockdr/releases)

## [Contributors](https://github.com/mockdr/mockdr/graphs/contributors) 2 (2)

- [![@gweber](https://avatars.githubusercontent.com/u/516202?s=64&v=4)](https://github.com/gweber) [**gweber** Günter Weber](https://github.com/gweber)
- [![@dependabot[bot]](https://avatars.githubusercontent.com/in/29110?s=64&v=4)](https://github.com/dependabot[bot]) [**dependabot\[bot\]**](https://github.com/dependabot[bot])

## Languages

- [Python74%](https://github.com/mockdr/mockdr/search?l=python)
- [TypeScript14.6%](https://github.com/mockdr/mockdr/search?l=typescript)
- [Vue9.9%](https://github.com/mockdr/mockdr/search?l=vue)
- [Bru1.1%](https://github.com/mockdr/mockdr/search?l=bru)
- [Shell0.3%](https://github.com/mockdr/mockdr/search?l=shell)
- [CSS0.1%](https://github.com/mockdr/mockdr/search?l=css)

You can’t perform that action at this time.