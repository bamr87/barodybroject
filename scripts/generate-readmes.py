# scripts/generate-readmes.py

import os
import sys

TEMPLATE = """
# {dir_name} Directory

## Purpose
[Brief description - please edit]

## Contents
{contents}

## Usage
[Usage instructions - please edit]

## Container Configuration
[Container info - please edit]

## Related Paths
- Incoming: [edit]
- Outgoing: [edit]
"""

def generate_readme(dir_path):
    dir_name = os.path.basename(dir_path)
    contents = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            contents.append(f"- `{item}/`: Subdirectory")
        else:
            contents.append(f"- `{item}`: File")
    
    contents_str = "\n".join(contents)
    
    readme_content = TEMPLATE.format(dir_name=dir_name, contents=contents_str)
    
    readme_path = os.path.join(dir_path, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    print(f"Generated {readme_path}")

def main(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'README.md' not in filenames:
            generate_readme(dirpath)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
