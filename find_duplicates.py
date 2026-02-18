import os
import hashlib
from collections import defaultdict

def get_file_content_hash(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # Ignore whitespace and case for similarity
            normalized = "".join(content.split()).lower()
            return hashlib.md_size(normalized.encode()).hexdigest(), content
    except:
        return None, None

def find_duplicates(root_dir):
    hashes = defaultdict(list)
    for root, dirs, files in os.walk(root_dir):
        if any(d in root for d in [".obsidian", ".smart-env", ".agent"]):
            continue
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                h, content = get_file_content_hash(path)
                if h:
                    hashes[h].append(path)
    
    return {h: paths for h, paths in hashes.items() if len(paths) > 1}

def find_stub_files(root_dir):
    stubs = []
    for root, dirs, files in os.walk(root_dir):
        if any(d in root for d in [".obsidian", ".smart-env", ".agent"]):
            continue
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        lines = [l.strip() for l in f.readlines() if l.strip()]
                    
                    # If file has 0-2 lines and seems like just a title
                    if len(lines) <= 2:
                        stubs.append(path)
                except:
                    pass
    return stubs

if __name__ == "__main__":
    import hashlib
    # Re-implementing hash to avoid md_size error
    def get_hash(content):
        normalized = "".join(content.split()).lower()
        return hashlib.md5(normalized.encode()).hexdigest()

    hashes = defaultdict(list)
    for root, dirs, files in os.walk('.'):
        if any(d in root for d in [".obsidian", ".smart-env", ".agent"]):
            continue
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        c = f.read()
                        h = get_hash(c)
                        hashes[h].append(path)
                except: pass

    print("--- DUPLICATES ---")
    for h, paths in hashes.items():
        if len(paths) > 1:
            print(f"Hash {h}: {paths}")
            
    print("\n--- STUB FILES ---")
    for s in find_stub_files('.'):
        print(s)
