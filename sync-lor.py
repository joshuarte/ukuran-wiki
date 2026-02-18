import os
import shutil
from pathlib import Path

# --- CONFIGURAZIONE ---
VAULT_PATH = Path("/")
DRIVE_TXT_PATH = Path("/txt")
# ----------------------

def sync_vault():
    print("🚀 Avvio sincronizzazione...")
    for md_file in VAULT_PATH.rglob("*.md"):
        # Salta cartelle di sistema
        if any(part.startswith('.') for part in md_file.parts):
            continue
            
        # Calcola path relativo
        rel_path = md_file.relative_to(VAULT_PATH)
        target_file = DRIVE_TXT_PATH / rel_path.with_suffix(".txt")
        
        # Crea directory e copia
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(md_file, target_file)
        
    print(f"✅ Sincronizzazione completata in: {DRIVE_TXT_PATH}")

if __name__ == "__main__":
    sync_vault()