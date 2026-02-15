#!/usr/bin/env python3
"""
Script to scrape URLs from text files and save as markdown using Firecrawl.
"""
import os
import re
import json
from pathlib import Path
from firecrawl import FirecrawlApp

# Configuration
INPUT_DIR = Path("data/in")
OUTPUT_DIR = Path("data/out")
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")

DRY_RUN = False  # Set to True to skip actual API calls and use mock data

def url_to_filename(url):
    """
    Convert a URL to a safe filename.
    """
    # Remove protocol
    filename = re.sub(r'^https?://', '', url)
    # Remove www.
    filename = re.sub(r'^www\.', '', filename)
    # Replace invalid filename characters with underscores
    filename = re.sub(r'[^\w\-.]', '_', filename)
    # Remove multiple consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    # Limit length to avoid filesystem issues
    if len(filename) > 200:
        filename = filename[:200]
    # Add .md extension
    return filename


def process_url(app, url, output_topic_dir, idx, total):
    """
    Process a single URL and write scraped output files.
    """
    print(f"  [{idx}/{total}] Processing: {url}")
    filename = url_to_filename(url)

    output_md_file = output_topic_dir / f"{filename}.md"
    if output_md_file.exists():
        print(f"    Skipping (already scraped): {output_md_file}")
        return False

    if DRY_RUN:
        print(f"    DRY RUN: Skipping actual API call for {url}")
        return False

    try:
        # Scrape the URL using Firecrawl
        result = app.scrape(url, formats=['markdown', 'html'])

        # Extract markdown content
        markdown_content = result.markdown
        if not markdown_content:
            print(f"    Warning: No markdown content returned for {url}")
            return False
        output_name = filename + ".md"
        output_file = output_topic_dir / output_name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {url}\n\n")
            f.write(markdown_content)
        print(f"    Saved to: {output_file}")

        # Extract html content
        html_content = result.html
        if not html_content:
            print(f"    Warning: No HTML content returned for {url}")
            return False
        output_name = filename + ".html"
        output_file = output_topic_dir / output_name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {url}\n\n")
            f.write(html_content)
        print(f"    Saved to: {output_file}")

        # Extract metadata content
        metadata_content = result.metadata
        if not metadata_content:
            print(f"    Warning: No metadata content returned for {url}")
            return False
        output_name = filename + ".json"
        output_file = output_topic_dir / output_name
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_content, f, ensure_ascii=False, indent=2, default=str)
        print(f"    Saved to: {output_file}")

        return True

    except Exception as e:
        print(f"    Error processing {url}: {e}")
        return False


def process_file(input_file):
    """
    Process a single input file containing URLs.
    """
    # Extract topic from filename (e.g., "maldev.txt" -> "maldev")
    topic = input_file.stem
    print(f"\nProcessing topic: {topic}")
    
    # Create output directory for this topic
    output_topic_dir = OUTPUT_DIR / topic
    output_topic_dir.mkdir(parents=True, exist_ok=True)

    if FIRECRAWL_API_KEY is None:
        raise RuntimeError("FIRECRAWL_API_KEY is not set")
    
    # Initialize Firecrawl
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    
    # Read URLs from file
    with open(input_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(urls)} URLs")
    
    # Process each URL
    for idx, url in enumerate(urls, 1):
        process_url(app, url, output_topic_dir, idx, len(urls))


def main():
    """
    Main function to process all input files.
    """
    # Check if API key is set
    if not FIRECRAWL_API_KEY:
        print("Error: FIRECRAWL_API_KEY environment variable not set")
        print("Please set it with: export FIRECRAWL_API_KEY='your-api-key'")
        return
    
    # Check if input directory exists
    if not INPUT_DIR.exists():
        print(f"Error: Input directory {INPUT_DIR} does not exist")
        return
    
    # Get all .txt files in input directory
    input_files = sorted(INPUT_DIR.glob("*.txt"))
    
    if not input_files:
        print(f"No .txt files found in {INPUT_DIR}")
        return
    
    print(f"Found {len(input_files)} input files")
    
    # Process each file
    for input_file in input_files:
        process_file(input_file)
    
    print("\nDone!")

if __name__ == "__main__":
    main()
