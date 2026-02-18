#!/usr/bin/env python3
"""
LLM Summarizer for scraped markdown files.

Processes .md files in data/out/<topic>/ directories and generates
LLM summaries saved as corresponding .llm files using OpenAI's API.
"""

import os
import sys
import random
import argparse
from pathlib import Path
from typing import Optional
from openai import OpenAI


PROMPT = """
You are a senior red team operator and security researcher.

Your task is to analyze the provided link or its extracted content and generate a concise, short, structured summary.

The content may be:
- A GitHub repository for a security tool
- A technical blog post (e.g., Windows internals, EDR bypass, AD abuse)
- A conference talk
- A research paper
- A proof-of-concept exploit
- A detection or defensive write-up

OUTPUT FORMAT (strictly follow this structure):

Title:
<Extracted or inferred title>

Type:
<GitHub Tool / Blog Post / Research Paper / Conference Talk / Documentation / Other>

Short Summary (4–8 sentences max):
- What is this about?
- What problem does it solve?
- What techniques or concepts are discussed?
- Who is it useful for (Red Team, Pentester, Malware Dev, Blue Team, etc.)?
- Why is it interesting or important?

Technical Focus:
<List 3–6 core technical concepts covered>

Use Cases:
- Bullet list of practical applications

Keywords:
<10–20 important keywords, comma-separated>
(Include technologies, protocols, APIs, attack techniques, CVEs, Windows internals components, etc.)

Be concise. Avoid marketing language. Focus on technical value.
Do not repeat generic cybersecurity explanations.
"""

# Directories relative to workspace root
INPUT_DIR = Path("data/out")


class LlmSummarizer:
    def __init__(self, api_key: Optional[str] = None, test_mode: bool = False):
        """
        Initialize the LLM summarizer.

        Args:
            api_key: OpenAI API key (reads from OPENAI_API_KEY env var if not provided)
            test_mode: If True, only process 3 random articles
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass --api-key.")

        self.client = OpenAI(api_key=self.api_key)
        self.test_mode = test_mode

    def find_all_md_files(self):
        """
        Find all .md files in data/out/<topic>/ directories.

        Returns:
            List of Path objects for each .md file found.
        """
        if not INPUT_DIR.exists():
            print(f"Error: Input directory {INPUT_DIR} does not exist")
            return []

        md_files = sorted(INPUT_DIR.rglob('*.md'))
        return md_files

    def read_file(self, file_path: Path) -> Optional[str]:
        """Read file content."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

    def summarize(self, content: str, max_retries: int = 3) -> Optional[str]:
        """
        Use OpenAI ChatGPT to summarize the content.

        Args:
            content: Markdown text content
            max_retries: Maximum number of retry attempts for API calls

        Returns:
            Summary text from ChatGPT
        """
        # Truncate very large content to avoid token limits
        max_chars = 100_000
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n[... content truncated ...]"

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-5.2",
                    messages=[
                        {"role": "user", "content": f"{PROMPT}\n\nContent:\n{content}"}
                    ],
                    temperature=0.2,
                )
                return response.choices[0].message.content.strip() if response.choices[0].message.content else None
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  Warning: API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"  Retrying...")
                else:
                    print(f"  Error: OpenAI API failed after {max_retries} attempts: {e}")
                    return None

        return None

    def process(self):
        """Process all .md files and generate .llm summaries."""
        md_files = self.find_all_md_files()

        if not md_files:
            print("No .md files found in data/out/!")
            return

        print(f"Found {len(md_files)} .md files total.")

        if self.test_mode:
            md_files = random.sample(md_files, min(3, len(md_files)))
            print(f"Test mode: Processing {len(md_files)} random files")

        success_count = 0
        skipped_count = 0
        error_count = 0

        for i, md_path in enumerate(md_files, 1):
            rel_path = md_path.relative_to(INPUT_DIR)
            llm_path = md_path.with_suffix('.llm')

            print(f"\n[{i}/{len(md_files)}] {rel_path}")

            # Skip if .llm file already exists
            if llm_path.exists():
                print(f"  Skipped (.llm already exists)")
                skipped_count += 1
                continue

            content = self.read_file(md_path)
            if not content:
                print(f"  Skipped (could not read file)")
                error_count += 1
                continue

            print(f"  Content length: {len(content)} chars")

            summary = self.summarize(content)

            if summary:
                with open(llm_path, 'w', encoding='utf-8') as f:
                    f.write(summary)
                print(f"  Saved: {llm_path.name}")
                success_count += 1
            else:
                print(f"  Failed to generate summary")
                error_count += 1

        print(f"\n{'='*60}")
        print(f"Done: {success_count} summarized, {skipped_count} skipped, {error_count} errors")
        print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description='Summarize scraped .md files using OpenAI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test mode (3 random files)
  python app/llm_summary.py --test

  # Process all .md files in data/out/
  python app/llm_summary.py

Environment:
  OPENAI_API_KEY must be set with your OpenAI API key
        """
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: only process 3 random files'
    )

    parser.add_argument(
        '--api-key',
        type=str,
        help='OpenAI API key (or set OPENAI_API_KEY env var)'
    )

    args = parser.parse_args()

    try:
        summarizer = LlmSummarizer(
            api_key=args.api_key,
            test_mode=args.test,
        )
        summarizer.process()

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
