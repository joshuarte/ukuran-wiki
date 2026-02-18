import os
import re
from urllib.parse import unquote

def get_all_md_files(root_dir):
    md_files = {}
    for root, dirs, files in os.walk(root_dir):
        if ".obsidian" in root or ".smart-env" in root or ".agent" in root:
            continue
        for file in files:
            if file.endswith('.md'):
                name_no_ext = os.path.splitext(file)[0]
                full_path = os.path.relpath(os.path.join(root, file), root_dir)
                # Map both full path and filename for fuzzy resolution
                md_files[full_path] = True
                md_files[file] = True
                md_files[name_no_ext] = True
    return md_files

def find_links(content):
    # Wikilinks: [[Link]] or [[Link|Label]]
    wikilinks = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
    # Markdown links: [Label](Path)
    md_links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', content)
    return wikilinks, md_links

def check_vault(root_dir):
    md_files = get_all_md_files(root_dir)
    broken_links = []
    
    for root, dirs, files in os.walk(root_dir):
        if ".obsidian" in root or ".smart-env" in root or ".agent" in root:
            continue
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, root_dir)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    wikilinks, md_links = find_links(content)
                    
                    for link in wikilinks:
                        link_clean = link.strip()
                        # Obsidian allows links without .md
                        if link_clean not in md_files and (link_clean + ".md") not in md_files:
                            broken_links.append({"file": rel_path, "link": link, "type": "wikilink"})
                            
                    for link in md_links:
                        # Ignore external links
                        if link.startswith('http') or link.startswith('mailto:'):
                            continue
                        
                        # Unquote URL encoding
                        link_unquoted = unquote(link)
                        # Remove anchors or queries
                        link_clean = link_unquoted.split('#')[0].split('?')[0]
                        
                        if not link_clean:
                            continue
                            
                        # Check relative to current file or absolute from vault root
                        link_path_rel = os.path.normpath(os.path.join(os.path.dirname(rel_path), link_clean))
                        link_path_abs = os.path.normpath(link_clean)
                        
                        if link_path_rel not in md_files and link_path_abs not in md_files and link_clean not in md_files:
                             # Some links might be to folders or non-md files
                             if not os.path.exists(os.path.join(root_dir, link_clean)):
                                broken_links.append({"file": rel_path, "link": link, "type": "markdown"})
                
                except Exception as e:
                    print(f"Error reading {path}: {e}")
                    
    return broken_links

if __name__ == "__main__":
    broken = check_vault('.')
    for b in broken:
        print(f"BROKEN [{b['type']}] in {b['file']}: {b['link']}")
