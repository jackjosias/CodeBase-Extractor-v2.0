# src/renderers/md_renderer.py
import re
from typing import Dict, Any
from .base_renderer import ReportRenderer

class MdRenderer(ReportRenderer):
    """Génère le rapport au format Markdown."""
    def get_extension(self) -> str:
        return "md"

    def render(self, data: Dict[str, Any]) -> str:
        header = data['header']
        stats = header['stats']
        parts = [
            "# Codebase Extraction Report\n",
            f"**Date d'extraction**: {header['date']}\n",
            f"**Système**: {header['system']}\n"
        ]
        if header['projects']: parts.append(f"**Projets/Dossiers**: {', '.join(header['projects'])}\n")
        if header['direct_files']: parts.append(f"**Fichiers directs**: {', '.join(header['direct_files'])}\n")
        parts.extend([
            f"**Chemins analysés**: {', '.join(header['paths'])}\n",
            "## Statistiques",
            f"- Total dossiers: {stats['total_dirs']}",
            f"- Total fichiers: {stats['total_files']}",
            f"- Fichiers de code: {stats['code_files']}\n",
            "## Structure du projet",
            f"```\n{data['structure_string']}\n```\n",
            "\n## Contenu des fichiers de code\n"
        ])
        
        for block in data['file_blocks']:
            match = re.match(r"'(.*?)':", block)
            filename = match.group(1) if match else "file"
            content_match = re.search(r"': \[\n-+\n(.*?)\n-+\n\]", block, re.DOTALL)
            content = content_match.group(1).strip() if content_match else block
            ext = filename.split('.')[-1]
            parts.append(f"**Fichier: `{filename}`**\n")
            parts.append(f"```{ext}\n{content}\n```\n")
            
        parts.append(f"\n✅ {data['extracted_count']} fichiers extraits avec succès\n")
        parts.append(f"Extraction terminée le {header['date']}\n")
        return "".join(parts)