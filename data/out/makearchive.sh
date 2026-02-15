#!/bin/bash

# Create a .zip file for each subdirectory in the current directory

for dir in */; do
    # Remove trailing slash from directory name
    dirname="${dir%/}"
    
    # Skip if not a directory
    [ -d "$dirname" ] || continue
    
    # Create zip file for the directory (only .md files)
    echo "Creating ${dirname}.zip..."
    zip -r "${dirname}.zip" "$dirname" -i '*.md'
done

echo "Done! Created zip files for all subdirectories."
