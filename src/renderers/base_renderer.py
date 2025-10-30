# src/renderers/base_renderer.py
from typing import Dict, Any

class ReportRenderer:
    """Classe de base abstraite pour les générateurs de rapports."""
    def render(self, data: Dict[str, Any]) -> str:
        raise NotImplementedError

    def get_extension(self) -> str:
        raise NotImplementedError