# scripts/

Tools for finding, validating, and mirroring GitHub repositories linked in the
Markdown files of this repo.

---

## `mirror_github_links.py`

Single script with two subcommands: **scrape** and **mirror**.

### Subcommand: `scrape`

Recursively scans Markdown files for GitHub URLs, adds new ones to the
database, then validates every unchecked entry by probing the Git smart-HTTP
endpoint.

```
python scripts/mirror_github_links.py scrape <directory> [--db PATH] [--delay SECONDS]
```

| Argument | Default | Description |
|---|---|---|
| `directory` | `.` | Root directory to scan recursively |
| `--db` | `scripts/githublinks.csv` | Path to the CSV database |
| `--delay` | `0.5` | Seconds between validation requests |

**Example – scan the whole repo and validate new entries:**
```
python scripts/mirror_github_links.py scrape . --db scripts/githublinks.csv
```

### Subcommand: `mirror`

Reads the database and sends every `valid` + not-yet-mirrored repo to the
mirroring service via HTTP POST.

```
python scripts/mirror_github_links.py mirror --password SECRET [--db PATH] [--delay SECONDS]
```

| Argument | Default | Description |
|---|---|---|
| `--password` | *(required)* | Access password for the mirroring service |
| `--db` | `scripts/githublinks.csv` | Path to the CSV database |
| `--delay` | `20` | Seconds between mirror requests |

**Example:**
```
python scripts/mirror_github_links.py mirror --password SECRET --db scripts/githublinks.csv
```

---

## Database (`githublinks.csv`)

Semicolon-delimited CSV, one repo per line.

```
url;status;mirrored
https://github.com/owner/repo;valid;yes
```

### Columns

| Column | Values | Description |
|---|---|---|
| `url` | `https://github.com/owner/repo` | Canonical GitHub repo URL |
| `status` | `unchecked` / `valid` / `invalid` | Result of the git-refs probe |
| `mirrored` | `no` / `yes` / `failed` | Result of the mirror attempt |

### Typical workflow

```
# 1. Scrape new links and validate them
python scripts/mirror_github_links.py scrape .

# 2. Review the CSV manually (e.g. flip status or mirrored as needed)

# 3. Mirror everything that is valid but not yet mirrored
python scripts/mirror_github_links.py mirror --password SECRET
```

**Rules:**
- New URLs are added with `status=unchecked, mirrored=no`.
- Already `valid` or `invalid` entries are **never re-validated** automatically.
- The mirror step only processes `status=valid` and `mirrored≠yes`.
- The CSV is written to disk after each individual check/mirror request so
  progress is never lost on interruption.
