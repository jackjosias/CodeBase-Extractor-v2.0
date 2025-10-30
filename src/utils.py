# src/utils.py
import os
import re
from typing import List, Dict

def scan_for_secrets(file_content: str, file_path: str) -> List[Dict[str, str]]:
    """Scanne un contenu textuel à la recherche de secrets potentiels."""
    secret_patterns = [r'(?i)(api[_-]?key|secret|token|password|passwd|pwd)["\'\s:=]+[\w\-\+/=]{8,}']
    findings = []
    for pat in secret_patterns:
        for match in re.findall(pat, file_content):
            findings.append({'file': file_path, 'secret': match})
    return findings

def compress_to_oneline(input_filename: str):
    """Lit un fichier, le compresse en une seule ligne et écrit le résultat."""
    try:
        print(f"\n🔄 Compression de {input_filename} en format une ligne...")
        with open(input_filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        oneline_content = ' '.join(content.split())
        base, ext = os.path.splitext(input_filename)
        output_filename = f"{base}.oneline{ext}"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(oneline_content)
        print(f"✅ Fichier compressé généré : {output_filename}")
    except (IOError, OSError) as e:
        print(f"❌ Erreur lors de la compression du fichier {input_filename}: {e}")

def handle_interactive_compression(output_files: Dict[str, str]):
    """Gère la logique de l'invite interactive pour la compression."""
    file_to_compress = None
    if 'txt' in output_files:
        file_to_compress = output_files['txt']
    elif 'md' in output_files:
        file_to_compress = output_files['md']
    
    if not file_to_compress:
        return

    try:
        answer = input(f"\n👉 Voulez-vous créer une version compressée sur une ligne de '{file_to_compress}' pour les LLMs ? (y/n): ")
        if answer.lower().strip().startswith('y'):
            compress_to_oneline(file_to_compress)
    except (EOFError, KeyboardInterrupt):
        print("\nInvite non-interactive détectée ou annulée. Aucune compression effectuée.")