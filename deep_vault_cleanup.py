import os
import re
from urllib.parse import unquote
import difflib

def get_vault_map(root_dir):
    vault_map = {}
    all_files = []
    for root, dirs, files in os.walk(root_dir):
        if any(d in root for d in [".obsidian", ".smart-env", ".agent"]):
            continue
        for file in files:
            if file.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(root, file), root_dir)
                name_no_ext = os.path.splitext(file)[0]
                vault_map[name_no_ext.lower().strip()] = rel_path
                all_files.append(rel_path)
    return vault_map, all_files

def find_best_match(link_text, vault_map):
    # Clean link text
    # Remove path, extension, anchor, hash residues
    name = unquote(link_text).split('/')[-1].split('#')[0].split('?')[0]
    name = re.sub(r' [0-9a-f]{32}$', '', name) # Remove hash if present
    if name.endswith('.md'): name = name[:-3]
    
    name_lower = name.lower().strip()
    
    if not name_lower: return None
    
    # Direct match
    if name_lower in vault_map:
        return os.path.splitext(os.path.basename(vault_map[name_lower]))[0]
        
    # Partial match
    for vn in vault_map:
        if vn.startswith(name_lower) or name_lower.startswith(vn):
             return os.path.splitext(os.path.basename(vault_map[vn]))[0]
             
    # Fuzzy match
    matches = difflib.get_close_matches(name_lower, vault_map.keys(), n=1, cutoff=0.7)
    if matches:
        return os.path.splitext(os.path.basename(vault_map[matches[0]]))[0]
    
    return None

def deep_cleanup(content, vault_map):
    # 1. Remove trailing Notion IDs and junk after Wikilinks
    # Example: [[Link|Label]]%202ec48bad...md)
    content = re.sub(r'(\[\[[^\]]+\]\])(%20| )[0-9a-f]{32}\.md\)?', r'\1', content)
    
    # 2. Fix Wikilinks
    def wikilink_sub(match):
        link = match.group(1).strip()
        label = match.group(2) if match.group(2) else ""
        match_name = find_best_match(link, vault_map)
        if match_name:
            if label:
                return f"[[{match_name}{label}]]"
            else:
                return f"[[{match_name}]]"
        return f"[[{link}{label}]]" # Return original text if no match found but keep wikilink format

    content = re.sub(r'\[\[([^\]|]+)(\|[^\]]+)?\]\]', wikilink_sub, content)
    
    # 3. Convert Markdown links to Wikilinks and fix them
    def mdlink_sub(match):
        label = match.group(1)
        link = match.group(2)
        if link.startswith('http'): return match.group(0)
        
        match_name = find_best_match(link, vault_map)
        if match_name:
            if label.lower() == match_name.lower():
                return f"[[{match_name}]]"
            return f"[[{match_name}|{label}]]"
        return f"[[{link}|{label}]]"

    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', mdlink_sub, content)
    
    # 4. Remove empty or redundant Notion blocks (like <aside> 💡 </aside> if empty)
    # Keeping them for now as they might have content.
    
    return content

def process_vault(root_dir):
    vault_map, all_files = get_vault_map(root_dir)
    for rel_path in all_files:
        path = os.path.join(root_dir, rel_path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = deep_cleanup(content, vault_map)
            
            if content != new_content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Deep cleaned: {rel_path}")
        except Exception as e:
            print(f"Error: {e} in {rel_path}")

if __name__ == "__main__":
    process_vault('.')
