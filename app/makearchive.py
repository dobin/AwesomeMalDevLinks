import os
import zipfile
from pathlib import Path


def make_archives():
    out_dir = Path("data/out")
    result_dir = Path("data/result")
    result_dir.mkdir(parents=True, exist_ok=True)

    for dirname in out_dir.iterdir():
        if not dirname.is_dir():
            continue

        basename = dirname.name
        zip_path = result_dir / f"{basename}.zip"

        print(f"Creating {basename}.zip...")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for md_file in dirname.rglob("*.md"):
                zf.write(md_file)

    print("Done! Created zip files for all subdirectories.")


if __name__ == "__main__":
    make_archives()
