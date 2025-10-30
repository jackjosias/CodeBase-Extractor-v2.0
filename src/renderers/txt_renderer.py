# src/renderers/txt_renderer.py
from typing import Dict, Any
from .base_renderer import ReportRenderer

class TxtRenderer(ReportRenderer):
    """Génère le rapport au format texte brut."""
    def get_extension(self) -> str:
        return "txt"

    def render(self, data: Dict[str, Any]) -> str:
        parts = []
        header = data['header']
        stats = header['stats']
        parts.append("=" * 80)
        parts.append("CODEBASE EXTRACTION REPORT")
        parts.append("=" * 80)
        if header['projects']: parts.append(f"Projets/Dossiers: {', '.join(header['projects'])}")
        if header['direct_files']: parts.append(f"Fichiers directs: {', '.join(header['direct_files'])}")
        parts.append(f"Chemins analysés: {', '.join(header['paths'])}")
        parts.append(f"Date d'extraction: {header['date']}")
        parts.append(f"Système: {header['system']}")
        parts.append("\nSTATISTIQUES DU PROJET:\n" + "-" * 30)
        parts.append(f"📁 Total dossiers: {stats['total_dirs']}")
        parts.append(f"📄 Total fichiers: {stats['total_files']}")
        parts.append(f"💻 Fichiers de code: {stats['code_files']}")
        parts.append("\nSTRUCTURE DU PROJET:\n" + "-" * 30)
        parts.append(data['structure_string'])
        parts.append("\n" + "=" * 80)
        parts.append("CONTENU DES FICHIERS DE CODE")
        parts.append("=" * 80)
        
        final_content = "\n".join(parts)
        if data['file_blocks']:
            final_content += "\n\n" + " &&& ".join(data['file_blocks'])
        
        footer = [
            "\n\n" + "=" * 80, "FIN DE L'EXTRACTION", "=" * 80,
            f"✅ {data['extracted_count']} fichiers extraits avec succès",
            f"📅 Extraction terminée le {header['date']}"
        ]
        return final_content + "\n".join(footer)