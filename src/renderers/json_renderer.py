# src/renderers/json_renderer.py
import json
import re
from typing import Dict, Any
from .base_renderer import ReportRenderer

class JsonRenderer(ReportRenderer):
    """Génère le rapport au format JSON."""
    def get_extension(self) -> str:
        return "json"

    def render(self, data: Dict[str, Any]) -> str:
        files_content = []
        for block in data['file_blocks']:
            match = re.match(r"'(.*?)': \[\n-+\n(.*?)\n-+\n\]", block, re.DOTALL)
            if match:
                path, content = match.groups()
                files_content.append({'path': path, 'content': content.strip()})
            else:
                files_content.append({'path': 'unknown', 'content': block})
        
        json_report = {
            'header': data['header'],
            'structure_tree': data['structure_tree'],
            'files': files_content
        }
        return json.dumps(json_report, ensure_ascii=False, indent=2)