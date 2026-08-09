"""
GitHub repository link manager: scrape, validate, and mirror.

Subcommands
-----------
scrape  <directory>  Scan Markdown files for GitHub URLs, add new ones to the
                     CSV as unchecked, then validate each unchecked entry.
mirror               Read the CSV and mirror every valid, not-yet-mirrored repo
                     to the configured mirroring service.

CSV format  (semicolon-delimited)
----------------------------------
url;status;mirrored
https://github.com/owner/repo;valid;yes

Status values  : unchecked | valid | invalid
Mirrored values: no | yes | failed (<reason>)
"""
import argparse
import csv
import os
import re
import sys
import time
import requests


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GITHUB_REPO_REGEX = re.compile(
    r"https?://(?:www\.)?github\.com/([a-zA-Z0-9-_.]+)/([a-zA-Z0-9-_.]+)"
)
DEFAULT_DB_PATH = "scripts/githublinks.csv"
MIRROR_URL = "https://gitadd.r00ted.ch"
VALID_STATUSES = {"valid", "invalid", "unchecked"}


# ---------------------------------------------------------------------------
# CSV abstraction
# ---------------------------------------------------------------------------

class RepoDatabase:
    """In-memory representation of the CSV database with a clear read/write API.

    All mutating methods operate on the in-memory dict; call ``save()`` to
    persist changes to disk.

    Schema (per entry)::

        {
            "status":   "unchecked" | "valid" | "invalid",
            "mirrored": "no" | "yes" | "failed (<reason>)",
        }
    """

    def __init__(self, csv_path: str = DEFAULT_DB_PATH):
        self.csv_path = csv_path
        self._data: dict = {}

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load(self) -> "RepoDatabase":
        """Load the CSV from disk into memory.  Safe to call when file is absent."""
        self._data = {}
        if not os.path.exists(self.csv_path):
            print(f"⚠️  CSV database not found at {os.path.abspath(self.csv_path)}")
            print("   Creating new database on first save.")
            return self

        try:
            with open(self.csv_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f, delimiter=";")
                for row in reader:
                    if not row or row[0].strip().lower() == "url":
                        continue  # skip blank lines and header
                    url = row[0].strip()
                    if not url:
                        continue
                    status = row[1].strip().lower() if len(row) > 1 else "unchecked"
                    if status not in VALID_STATUSES:
                        status = "unchecked"
                    mirrored = row[2].strip() if len(row) > 2 else "no"
                    # Normalize verbose "failed (...)" messages from old runs
                    if mirrored.lower().startswith("failed"):
                        mirrored = "failed"
                    self._data[url] = {"status": status, "mirrored": mirrored}
        except Exception as e:
            print(f"⚠️  Error reading CSV {self.csv_path}: {e}", file=sys.stderr)

        return self

    def save(self) -> None:
        """Write the current in-memory state back to the CSV file (sorted by URL)."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.csv_path)), exist_ok=True)
            with open(self.csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["url", "status", "mirrored"])
                for url in sorted(self._data):
                    entry = self._data[url]
                    status = entry["status"] if entry["status"] in VALID_STATUSES else "unchecked"
                    writer.writerow([url, status, entry.get("mirrored", "no")])
        except Exception as e:
            print(f"⚠️  Error writing CSV {self.csv_path}: {e}", file=sys.stderr)

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def add_if_new(self, url: str) -> bool:
        """Add *url* with default values if it is not already tracked.

        Returns ``True`` if the entry was newly added, ``False`` if it existed.
        """
        if url in self._data:
            return False
        self._data[url] = {"status": "unchecked", "mirrored": "no"}
        return True

    def set_status(self, url: str, status: str) -> None:
        """Update the validation status for *url*."""
        if url not in self._data:
            self._data[url] = {"status": "unchecked", "mirrored": "no"}
        self._data[url]["status"] = status

    def set_mirrored(self, url: str, value: str) -> None:
        """Update the mirrored field for *url*."""
        if url not in self._data:
            self._data[url] = {"status": "unchecked", "mirrored": "no"}
        self._data[url]["mirrored"] = value

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def get_pending_validation(self) -> list:
        """Return URLs whose status is ``unchecked``."""
        return [url for url, entry in self._data.items() if entry["status"] == "unchecked"]

    def get_pending_mirror(self) -> list:
        """Return URLs that are ``valid`` but not yet successfully mirrored."""
        return [
            url for url, entry in self._data.items()
            if entry["status"] == "valid" and entry.get("mirrored", "no").lower() != "yes"
        ]

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, url: str) -> bool:
        return url in self._data


# ---------------------------------------------------------------------------
# Scrape helpers
# ---------------------------------------------------------------------------

def extract_github_repos(directory: str) -> dict:
    """Walk *directory* recursively and return a mapping of repo URL -> list of files."""
    found: dict = {}
    print(f"🔍 Scanning: {os.path.abspath(directory)} ...")

    for root, _, files in os.walk(directory):
        for filename in files:
            if not filename.endswith((".md", ".markdown")):
                continue
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as fh:
                    content = fh.read()
                for owner, repo in GITHUB_REPO_REGEX.findall(content):
                    repo = repo.split(".git")[0].rstrip(").,:`\"'")
                    url = f"https://github.com/{owner}/{repo}"
                    found.setdefault(url, []).append(file_path)
            except Exception as e:
                print(f"⚠️  Error reading {file_path}: {e}", file=sys.stderr)

    return found


def _validate_url(session: requests.Session, url: str):
    """Return ``(status, reason)`` for a single GitHub URL."""
    # Skip non-repository paths immediately
    for prefix in (
        "https://github.com/topics/",
        "https://github.com/users/",
        "https://github.com/orgs/",
        "https://github.com/apps/",
        "https://github.com/sponsors/",
        "https://github.com/stars/",
        "https://github.com/advisories/",
        "https://github.com/contact/",
        "https://github.com/user-attachments/",
    ):
        if url.startswith(prefix):
            return "invalid", "non-repo URL"

    try:
        git_refs_url = f"{url}/info/refs?service=git-upload-pack"
        response = session.get(git_refs_url, allow_redirects=True, timeout=5)
        content_type = response.headers.get("Content-Type", "")
        if response.status_code == 200 and "git-upload-pack" in content_type:
            return "valid", "git repo confirmed"
        return "invalid", f"HTTP {response.status_code}"
    except requests.RequestException as e:
        return "invalid", f"connection error: {e}"


# ---------------------------------------------------------------------------
# Subcommand implementations
# ---------------------------------------------------------------------------

def cmd_scrape(args: argparse.Namespace) -> None:
    """Scrape Markdown files, register new URLs, then validate unchecked ones."""
    db = RepoDatabase(args.db).load()

    # Step 1 – extract URLs from Markdown files
    repo_map = extract_github_repos(args.directory)
    if not repo_map:
        print("No GitHub repository URLs found in any Markdown files.")
        return

    print(f"  Found {len(repo_map)} unique URLs in Markdown files.")

    # Step 2 – add new entries
    newly_added = sum(db.add_if_new(url) for url in repo_map)
    if newly_added:
        print(f"  ➕ {newly_added} new URL(s) added to the database.")
        db.save()

    # Step 3 – validate unchecked entries
    pending = db.get_pending_validation()
    if not pending:
        print("  ✓ All URLs already validated — nothing to check.")
        _print_summary(db)
        return

    cached = len(db) - len(pending)
    print(f"\n📡 Validation:")
    print(f"   ✓ {cached} already validated (cached)")
    print(f"   🔄 {len(pending)} to validate")
    print(f"   ⏱️  Estimated time: ~{len(pending) * args.delay / 60:.1f} min\n")

    valid_count = 0
    invalid_count = 0

    with requests.Session() as session:
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        for url in sorted(pending):
            print(f"  Checking: {url}", end=" ", flush=True)
            status, reason = _validate_url(session, url)
            db.set_status(url, status)
            db.save()
            if status == "valid":
                valid_count += 1
                print("✅ valid")
            else:
                invalid_count += 1
                print(f"❌ {reason}")
            time.sleep(args.delay)

    print(f"\n  Checked {len(pending)}: {valid_count} valid, {invalid_count} invalid")
    _print_summary(db)


def cmd_mirror(args: argparse.Namespace) -> None:
    """Mirror valid, not-yet-mirrored repos to the mirroring service."""
    db = RepoDatabase(args.db).load()

    pending = db.get_pending_mirror()
    if not pending:
        print("✅ No valid repositories pending mirroring.")
        return

    print(f"🔄 Mirroring {len(pending)} repositories ...\n")

    with requests.Session() as session:
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        for url in pending:
            print(f"  Mirroring: {url}", end=" ", flush=True)
            try:
                response = session.post(
                    MIRROR_URL,
                    data={"github_url": url, "access_password": args.password},
                    timeout=30,
                )
                if response.status_code == 200:
                    db.set_mirrored(url, "yes")
                    print("✅ success")
                else:
                    db.set_mirrored(url, "failed")
                    print(f"❌ HTTP {response.status_code}")
            except requests.RequestException as e:
                db.set_mirrored(url, "failed")
                print(f"❌ {e}")

            db.save()
            time.sleep(args.delay)

    mirrored_ok = sum(
        1 for u in pending if db._data[u].get("mirrored") == "yes"
    )
    print(f"\n  Done: {mirrored_ok}/{len(pending)} successfully mirrored.")


# ---------------------------------------------------------------------------
# Summary helper
# ---------------------------------------------------------------------------

def _print_summary(db: RepoDatabase) -> None:
    valid    = sum(1 for e in db._data.values() if e["status"] == "valid")
    invalid  = sum(1 for e in db._data.values() if e["status"] == "invalid")
    unchk    = sum(1 for e in db._data.values() if e["status"] == "unchecked")
    mirrored = sum(1 for e in db._data.values() if e.get("mirrored") == "yes")

    print("\n" + "=" * 50)
    print(" DATABASE SUMMARY")
    print("=" * 50)
    print(f"  Total      : {len(db)}")
    print(f"  Valid      : {valid}")
    print(f"  Invalid    : {invalid}")
    print(f"  Unchecked  : {unchk}")
    print(f"  Mirrored   : {mirrored}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage GitHub repository links: scrape, validate, and mirror.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan current directory, add new URLs, validate unchecked ones:
  python mirror_github_links.py scrape . --db scripts/githublinks.csv

  # Mirror all valid, not-yet-mirrored repos:
  python mirror_github_links.py mirror --password SECRET --db scripts/githublinks.csv
""",
    )
    parser.add_argument("--db", default=DEFAULT_DB_PATH,
                        help=f"Path to the CSV database (default: {DEFAULT_DB_PATH})")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # -- scrape subcommand --
    sp_scrape = subparsers.add_parser(
        "scrape",
        help="Scan Markdown files for GitHub URLs, register new ones, validate unchecked.",
    )
    sp_scrape.add_argument(
        "directory", nargs="?", default=".",
        help="Directory to scan recursively (default: current directory)",
    )
    sp_scrape.add_argument(
        "--delay", type=float, default=0.5,
        help="Seconds between validation requests (default: 0.5)",
    )

    # -- mirror subcommand --
    sp_mirror = subparsers.add_parser(
        "mirror",
        help="Mirror valid, not-yet-mirrored repos to the mirroring service.",
    )
    sp_mirror.add_argument("--password", required=True,
                           help="Access password for the mirroring service")
    sp_mirror.add_argument("--delay", type=int, default=20,
                           help="Seconds between mirror requests (default: 20)")

    args = parser.parse_args()

    if args.command == "scrape":
        cmd_scrape(args)
    elif args.command == "mirror":
        cmd_mirror(args)


if __name__ == "__main__":
    main()