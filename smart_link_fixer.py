import os
import re
from urllib.parse import unquote
import difflib

def get_vault_map(root_dir):
    # Maps filename (no ext) -> actual relative path
    vault_map = {}
    all_files = []
    for root, dirs, files in os.walk(root_dir):
        if any(d in root for d in [".obsidian", ".smart-env", ".agent"]):
            continue
        for file in files:
            if file.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(root, file), root_dir)
                name_no_ext = os.path.splitext(file)[0]
                vault_map[name_no_ext.lower()] = rel_path
                all_files.append(rel_path)
    return vault_map, all_files

def find_best_match(broken_link, vault_map):
    # Clean the link
    link_name = unquote(broken_link).split('/')[-1].split('#')[0].split('?')[0]
    if link_name.endswith('.md'):
        link_name = link_name[:-3]
    
    link_lower = link_name.lower().strip()
    
    # Direct match
    if link_lower in vault_map:
        return os.path.splitext(os.path.basename(vault_map[link_lower]))[0]
    
    # Truncated match (prefix match)
    for name in vault_map:
        if name.startswith(link_lower) or link_lower.startswith(name):
            return os.path.splitext(os.path.basename(vault_map[name]))[0]
            
    # Fuzzy match
    matches = difflib.get_close_matches(link_lower, vault_map.keys(), n=1, cutoff=0.6)
    if matches:
        return os.path.splitext(os.path.basename(vault_map[matches[0]]))[0]
        
    return None

def fix_content(content, vault_map):
    # 1. Fix Wikilinks
    def wikilink_sub(match):
        link = match.group(1).strip()
        label = match.group(2) if match.group(2) else ""
        match_name = find_best_match(link, vault_map)
        if match_name:
            if label:
                return f"[[{match_name}{label}]]"
            else:
                return f"[[{match_name}]]"
        return match.group(0) # Keep as is if no match

    # Regex for wikilinks: [[Link|Label]] or [[Link]]
    content = re.sub(r'\[\[([^\]|]+)(\|[^\]]+)?\]\]', wikilink_sub, content)
    
    # 2. Fix Markdown links
    def mdlink_sub(match):
        label = match.group(1)
        link = match.group(2)
        
        # Skip external
        if link.startswith('http') or link.startswith('mailto:'):
            return match.group(0)
            
        match_name = find_best_match(link, vault_map)
        if match_name:
            # Convert to wikilink because it's safer for Obsidian
            return f"[[{match_name}|{label}]]"
            
        return match.group(0)

    # Regex for markdown links: [Label](Link)
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', mdlink_sub, content)
    
    return content

def cleanup_vault(root_dir):
    vault_map, all_files = get_vault_map(root_dir)
    
    for rel_path in all_files:
        path = os.path.join(root_dir, rel_path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = fix_content(content, vault_map)
            
            # Additional cleanup: remove Notion specific artifacts if possible
            # (e.g. empty lines with just a dot, or excessive whitespace)
            
            if content != new_content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed links in: {rel_path}")
        except Exception as e:
            print(f"Error processing {rel_path}: {e}")

if __name__ == "__main__":
    cleanup_vault('.')
