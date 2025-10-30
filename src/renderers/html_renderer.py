# src/renderers/html_renderer.py
import html
import re
from typing import Dict, Any
from .base_renderer import ReportRenderer

class HtmlRenderer(ReportRenderer):
    """Génère le rapport au format HTML."""
    def get_extension(self) -> str:
        return "html"

    def render(self, data: Dict[str, Any]) -> str:
        header = data['header']
        stats = header['stats']
        projects_html = ""
        if header['projects']: projects_html += f"<b>Projets/Dossiers:</b> {', '.join(header['projects'])}<br>"
        if header['direct_files']: projects_html += f"<b>Fichiers directs:</b> {', '.join(header['direct_files'])}<br>"
        
        html_content = [
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Codebase Extraction Report</title>",
            "<style>body{font-family:sans-serif;line-height:1.6;} pre{background-color:#f4f4f4;padding:1em;border-radius:5px;white-space:pre-wrap;word-wrap:break-word;} h3{border-bottom: 1px solid #ccc; padding-bottom: 5px;}</style>",
            "</head><body>",
            "<h1>Codebase Extraction Report</h1>",
            f"<p><b>Date d'extraction:</b> {header['date']}<br><b>Système:</b> {header['system']}<br>{projects_html}<b>Chemins analysés:</b> {', '.join(header['paths'])}</p>",
            f"<h2>Statistiques</h2><ul><li>Total dossiers: {stats['total_dirs']}</li><li>Total fichiers: {stats['total_files']}</li><li>Fichiers de code: {stats['code_files']}</li></ul>",
            "<h2>Structure du projet</h2>",
            f"<pre>{html.escape(data['structure_string'])}</pre>",
            "<h2>Contenu des fichiers de code</h2>"
        ]
        
        for block in data['file_blocks']:
            match = re.match(r"'(.*?)':", block)
            filename = match.group(1) if match else "file"
            content_match = re.search(r"': \[\n-+\n(.*?)\n-+\n\]", block, re.DOTALL)
            content = content_match.group(1).strip() if content_match else block
            html_content.append(f"<h3>Fichier: <code>{html.escape(filename)}</code></h3>")
            html_content.append(f"<pre><code>{html.escape(content)}</code></pre>")
            
        html_content.append(f"<p>✅ {data['extracted_count']} fichiers extraits avec succès<br>Extraction terminée le {header['date']}</p>")
        html_content.append("</body></html>")
        return "\n".join(html_content)