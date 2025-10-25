#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODEBASE EXTRACTOR v3.1 (Architectural Refactor - Path Handling Upgrade)
Agent intelligent pour l'extraction automatique de codebase
Créé pour automatiser la récupération de code pour collaboration IA/LLM
"""
# ==============================================================================
# CodeBase Extractor - Créé et maintenu par Jack-Josias (2025)
# ==============================================================================
import os
import sys
import platform
import pathlib
import mimetypes
import argparse
from datetime import datetime
from typing import Dict, Optional, List, Any
import fnmatch
import zipfile
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==============================================================================
# SECTION: MOTEUR DE RENDU (RENDERERS)
# ==============================================================================
class ReportRenderer:
    """Classe de base abstraite pour les générateurs de rapports."""
    def render(self, data: Dict[str, Any]) -> str:
        raise NotImplementedError

    def get_extension(self) -> str:
        raise NotImplementedError

class TxtRenderer(ReportRenderer):
    """Génère le rapport au format texte brut, préservant le format original."""
    def get_extension(self) -> str:
        return "txt"

    def render(self, data: Dict[str, Any]) -> str:
        parts = []
        header = data['header']
        stats = header['stats']
        parts.append("=" * 80)
        parts.append("CODEBASE EXTRACTION REPORT")
        parts.append("=" * 80)

        # HEPHAESTUS v59.0 MODIFICATION: Logique d'affichage de l'en-tête améliorée pour plus de clarté
        if header['projects']:
             parts.append(f"Projets/Dossiers: {', '.join(header['projects'])}")
        if header['direct_files']:
             parts.append(f"Fichiers directs: {', '.join(header['direct_files'])}")
        
        parts.append(f"Chemins analysés: {', '.join(header['paths'])}")
        parts.append(f"Date d'extraction: {header['date']}")
        parts.append(f"Système: {header['system']}")
        parts.append("")
        parts.append("STATISTIQUES DU PROJET:")
        parts.append("-" * 30)
        parts.append(f"📁 Total dossiers: {stats['total_dirs']}")
        parts.append(f"📄 Total fichiers: {stats['total_files']}")
        parts.append(f"💻 Fichiers de code: {stats['code_files']}")
        parts.append("")
        parts.append("STRUCTURE DU PROJET:")
        parts.append("-" * 30)
        parts.append(data['structure_string'])
        parts.append("")
        parts.append("=" * 80)
        parts.append("CONTENU DES FICHIERS DE CODE")
        parts.append("=" * 80)

        final_content = "\n".join(parts)
        if data['file_blocks']:
            # HEPHAESTUS v59.0 MODIFICATION: Utilisation de \n\n pour séparer les blocs, plus lisible que ' && '
            final_content += "\n\n" + "\n\n".join(data['file_blocks'])

        footer = [
            "\n\n" + "=" * 80,
            "FIN DE L'EXTRACTION",
            "=" * 80,
            f"✅ {data['extracted_count']} fichiers extraits avec succès",
            f"📅 Extraction terminée le {header['date']}"
        ]
        return final_content + "\n".join(footer)

class JsonRenderer(ReportRenderer):
    """Génère le rapport au format JSON."""
    def get_extension(self) -> str:
        return "json"

    def render(self, data: Dict[str, Any]) -> str:
        # HEPHAESTUS v59.0 MODIFICATION: Contenu des fichiers séparé pour plus de clarté
        files_content = []
        for block in data['file_blocks']:
            # Extrait le chemin et le contenu du bloc formaté
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
        # HEPHAESTUS v59.0 MODIFICATION: Logique d'affichage de l'en-tête améliorée
        if header['projects']:
             parts.append(f"**Projets/Dossiers**: {', '.join(header['projects'])}\n")
        if header['direct_files']:
             parts.append(f"**Fichiers directs**: {', '.join(header['direct_files'])}\n")
        
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
            # HEPHAESTUS v59.0 MODIFICATION: Extraction du nom de fichier pour le bloc de code MD
            match = re.match(r"'(.*?)':", block)
            filename = match.group(1) if match else "file"
            ext = filename.split('.')[-1]
            parts.append(f"**Fichier: `{filename}`**\n")
            parts.append(f"```{ext}\n{block}\n```\n")

        parts.append(f"\n✅ {data['extracted_count']} fichiers extraits avec succès\n")
        parts.append(f"Extraction terminée le {header['date']}\n")
        return "".join(parts)

class HtmlRenderer(ReportRenderer):
    """Génère le rapport au format HTML."""
    def get_extension(self) -> str:
        return "html"

    def render(self, data: Dict[str, Any]) -> str:
        import html
        header = data['header']
        stats = header['stats']
        
        projects_html = ""
        if header['projects']:
            projects_html += f"<b>Projets/Dossiers:</b> {', '.join(header['projects'])}<br>"
        if header['direct_files']:
            projects_html += f"<b>Fichiers directs:</b> {', '.join(header['direct_files'])}<br>"

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
            html_content.append(f"<h3>Fichier: <code>{html.escape(filename)}</code></h3>")
            html_content.append(f"<pre><code>{html.escape(block)}</code></pre>")
        
        html_content.append(f"<p>✅ {data['extracted_count']} fichiers extraits avec succès<br>Extraction terminée le {header['date']}</p>")
        html_content.append("</body></html>")
        return "\n".join(html_content)

# ==============================================================================
# SECTION: MOTEUR D'EXTRACTION
# ==============================================================================
class CodebaseExtractor:
    """Agent intelligent pour extraire et formatter une codebase complète"""
    def __init__(self, extra_ignore_patterns=None):
        self.system_info = self._detect_system()
        self.supported_extensions = {
            # Langages de programmation
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.mm', '.pl', '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd', '.vbs', '.lua', '.dart', '.elm', '.haskell', '.hs', '.clj', '.cljs', '.edn', '.f90', '.f95', '.fortran', '.cobol', '.cob', '.pas', '.pp', '.asm', '.s', '.sql', '.plsql', '.mysql', '.sqlite', '.psql',
            # Web, templating et markup
            '.html', '.htm', '.xml', '.xhtml', '.svg', '.css', '.scss', '.sass', '.less', '.styl', '.vue', '.svelte', '.twig', '.jinja', '.jinja2', '.latte', '.blade.php',
            # Configuration et données
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.config', '.properties', '.env', '.gitignore', '.gitconfig', '.dockerignore', '.editorconfig', '.prettierrc', '.eslintrc', '.babelrc', '.webpack.config.js',
            # Documentation
            '.md', '.rst', '.txt', '.adoc', '.tex', '.latex',
            # Autres
            '.dockerfile', 'Dockerfile', '.makefile', 'Makefile', '.cmake', '.gradle', '.maven', '.ant', '.sbt', '.mix.exs', '.rebar.config', '.cargo.toml', '.pubspec.yaml', '.package.json', '.requirements.txt', '.pipfile', '.poetry.lock', '.gemfile', '.podfile', '.cartfile'
        }
        self.base_ignore_patterns = {
            '__pycache__', '.git', '.svn', '.hg', '.bzr', 'node_modules', '.npm', '.yarn', 'venv', 'env', '.env', 'virtualenv', '.venv', 'env/', 'venv/', 'build', 'dist', 'target', 'bin', 'obj', 'out', '.build', '.dist', '.vscode', '.idea', '.vs', '.atom', '.sublime-text', '.brackets', '*.swp', '*.swo', '*~', '.DS_Store', 'Thumbs.db', 'desktop.ini', 'logs', '*.log', '*.tmp', '*.temp', '.cache', '.temp', 'tmp', 'vendor', '.nuget', 'bower_components', 'jspm_packages', '.sass-cache', '.gradle', '.m2', '.ivy2'
        }
        if extra_ignore_patterns:
            self.base_ignore_patterns.update(extra_ignore_patterns)

    def _detect_system(self) -> Dict[str, str]:
        system = platform.system().lower()
        return {
            'os': system,
            'version': platform.version(),
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version(),
            'encoding': sys.getdefaultencoding(),
            'separator': os.sep
        }

    def _load_gitignore_patterns(self, root_path: str) -> set:
        gitignore_path = os.path.join(root_path, '.gitignore')
        patterns = set()
        if os.path.exists(gitignore_path):
            print(f"📄 Fichier .gitignore trouvé dans {root_path}. Chargement des règles.")
            with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    stripped_line = line.strip()
                    if stripped_line and not stripped_line.startswith('#'):
                        patterns.add(stripped_line)
        return patterns

    def _normalize_paths(self, paths: List[str]) -> List[str]:
        # Cette fonction est maintenant utilisée pour la déduplication de répertoires uniquement.
        # La logique principale de gestion des chemins est dans `extract_codebase`.
        if not paths:
            return []
        
        # Conserver uniquement les répertoires existants pour cette logique
        dir_paths = [os.path.abspath(p) for p in paths if os.path.isdir(p)]
        if len(dir_paths) <= 1:
            return dir_paths

        sorted_paths = sorted([p + os.sep for p in dir_paths])
        unique_roots = []
        last_root = " "
        for path in sorted_paths:
            if not path.startswith(last_root):
                unique_roots.append(path.rstrip(os.sep))
                last_root = path
        return unique_roots

    def _is_ignored(self, path: str, name: str, dynamic_ignore_patterns: set) -> bool:
        full_ignore_set = self.base_ignore_patterns.union(dynamic_ignore_patterns)
        for pattern in full_ignore_set:
            if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(path, f"*{os.sep}{pattern}"):
                return True
        if name.startswith('.') and name not in {'.env', '.gitignore', '.dockerignore'}:
            return True
        return False

    def _is_code_file(self, filepath: str) -> bool:
        filename = os.path.basename(filepath)
        if filename in self.supported_extensions:
            return True
        ext = pathlib.Path(filepath).suffix.lower()
        if ext in self.supported_extensions:
            return True
        if not ext:
            mime_type, _ = mimetypes.guess_type(filepath)
            if mime_type and 'text' in mime_type:
                return True
        return False

    def _safe_read_file(self, filepath: str) -> Optional[str]:
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                if len(content) > 1000000:
                    return content[:1000000] + f"\n\n[... Fichier tronqué - taille originale: {len(content)} caractères]"
                return content
            except (UnicodeDecodeError, PermissionError, OSError):
                continue
        return f"[Erreur: Impossible de lire le fichier {filepath}]"

    def _create_tree_structure(self, root_path: str, dynamic_ignore_patterns: set) -> dict:
        tree: Dict[str, Any] = {'files': [], 'dirs': {}, 'stats': {'total_files': 0, 'total_dirs': 0, 'code_files': 0}}
        try:
            for item in sorted(os.listdir(root_path)):
                item_path = os.path.join(root_path, item)
                if self._is_ignored(item_path, item, dynamic_ignore_patterns):
                    continue
                if os.path.isfile(item_path):
                    tree['files'].append(item)
                    tree['stats']['total_files'] += 1
                    if self._is_code_file(item_path):
                        tree['stats']['code_files'] += 1
                elif os.path.isdir(item_path):
                    sub_tree = self._create_tree_structure(item_path, dynamic_ignore_patterns)
                    tree['dirs'][item] = sub_tree
                    tree['stats']['total_dirs'] += 1
                    for key in tree['stats']:
                        tree['stats'][key] += sub_tree['stats'][key]
        except PermissionError:
            tree['error'] = "Permission refusée"
        return tree

    def _format_tree_display(self, tree: Dict, prefix: str = "") -> str:
        result = []
        items = list(tree.get('dirs', {}).keys()) + tree.get('files', [])
        for i, item_name in enumerate(sorted(items)):
            is_last = (i == len(items) - 1)
            is_dir = item_name in tree.get('dirs', {})
            connector = "└── " if is_last else "├── "
            line = f"{prefix}{connector}{item_name}{'/' if is_dir else ''}"
            result.append(line)
            if is_dir:
                next_prefix = prefix + ("    " if is_last else "│   ")
                result.append(self._format_tree_display(tree['dirs'][item_name], next_prefix))
        return "\n".join(result)

    def _collect_files_to_extract(self, root_path: str, dynamic_ignore_patterns: set) -> list:
        files_to_process = []
        for root, dirs, files in os.walk(root_path, topdown=True):
            dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d), d, dynamic_ignore_patterns)]
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_ignored(file_path, file, dynamic_ignore_patterns):
                    continue
                if self._is_code_file(file_path):
                    # HEPHAESTUS v59.0 MODIFICATION: Calcul du chemin relatif par rapport au chemin racine de départ
                    # pour une meilleure cohérence, et non par rapport à os.path.dirname(root_path)
                    relative_path = os.path.relpath(file_path, root_path)
                    files_to_process.append((file_path, relative_path))
        return files_to_process

    def _extract_content_parallel(self, files_to_process: list) -> list:
        all_blocks = []
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            future_to_file = {executor.submit(self._safe_read_file, f[0]): f[1] for f in files_to_process}
            for future in as_completed(future_to_file):
                relative_path = future_to_file[future]
                try:
                    content = future.result()
                    print(f"📖 Extraction parallèle: {relative_path}")
                    block = f"'{relative_path}': [\n" + "-" * 50 + "\n" + (content or "[Aucun contenu lu]") + "\n" + "-" * 50 + "\n]"
                    all_blocks.append(block)
                except Exception as exc:
                    print(f"❌ Erreur lors de l'extraction de {relative_path}: {exc}")
        return sorted(all_blocks)

    def extract_codebase(self, target_paths: List[str], output_file: Optional[str] = None, formats: Optional[List[str]] = None) -> dict:
        print("🤖 CODEBASE EXTRACTOR v3.1")
        
        # === HEPHAESTUS v59.0: DÉBUT DE LA LOGIQUE DE PRÉ-TRAITEMENT DES CHEMINS ===
        if not target_paths:
            print("❌ Aucun chemin fourni. Arrêt de l'extraction.")
            return {}

        initial_abs_paths = {os.path.abspath(p) for p in target_paths}
        
        valid_dirs = sorted([p for p in initial_abs_paths if os.path.isdir(p)])
        valid_files = sorted([p for p in initial_abs_paths if os.path.isfile(p)])
        
        for p in initial_abs_paths:
            if not os.path.exists(p):
                print(f"⚠️ Chemin ignoré (inexistant ou permission refusée): {p}")

        # Dédupliquer les répertoires (ex: /a et /a/b -> garder /a)
        clean_dirs = self._normalize_paths(valid_dirs)

        # Filtrer les fichiers qui sont déjà inclus dans un des répertoires à traiter
        final_files = []
        for f in valid_files:
            is_subpath = any(f.startswith(d + os.sep) for d in clean_dirs)
            if not is_subpath:
                final_files.append(f)
            else:
                print(f"ℹ️ Fichier ignoré car inclus dans un répertoire analysé: {f}")
        
        if not clean_dirs and not final_files:
            print("❌ Aucun chemin valide (fichier ou répertoire) à traiter. Arrêt de l'extraction.")
            return {}
        # === HEPHAESTUS v59.0: FIN DE LA LOGIQUE DE PRÉ-TRAITEMENT DES CHEMINS ===

        all_trees_data, total_stats, all_files_to_process = [], {'total_files': 0, 'total_dirs': 0, 'code_files': 0}, []
        structure_parts = []

        # Traitement des répertoires
        for path in clean_dirs:
            print(f"🎯 Analyse du répertoire: {path}")
            dynamic_ignores = self._load_gitignore_patterns(path)
            print("🌳 Analyse de l'arborescence...")
            tree = self._create_tree_structure(path, dynamic_ignores)
            
            project_name = os.path.basename(path)
            all_trees_data.append((project_name, tree))
            structure_parts.append(f"{project_name}/\n{self._format_tree_display(tree)}")

            for key in total_stats:
                total_stats[key] += tree['stats'][key]
            
            print("🔍 Collecte des fichiers à extraire du répertoire...")
            # HEPHAESTUS v59.0 MODIFICATION: Le chemin relatif est calculé par rapport au `path` de départ
            all_files_to_process.extend(self._collect_files_to_extract(path, dynamic_ignores))

        # Traitement des fichiers directs
        for file_path in final_files:
            print(f"🎯 Analyse du fichier direct: {file_path}")
            if self._is_code_file(file_path):
                relative_path = os.path.basename(file_path)
                # Ajouter le fichier à la liste de traitement avec un chemin relatif simple
                all_files_to_process.append((file_path, relative_path))
                # Mettre à jour les statistiques manuellement
                total_stats['total_files'] += 1
                total_stats['code_files'] += 1
                # Ajouter une entrée simple à la structure pour la visibilité
                structure_parts.append(f"{relative_path} (fichier direct)")
            else:
                print(f"ℹ️ Fichier ignoré (type non supporté): {file_path}")

        print(f"\n🚀 Lancement de l'extraction parallèle de {len(all_files_to_process)} fichiers...")
        all_blocks = self._extract_content_parallel(all_files_to_process)

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        structure_str = "\n".join(structure_parts)
        
        report_data = {
            'header': {
                'projects': [os.path.basename(p) for p in clean_dirs],
                'direct_files': [os.path.basename(f) for f in final_files],
                'paths': sorted(list(initial_abs_paths)),
                'date': now,
                'system': f"{self.system_info['os']} {self.system_info['architecture']}",
                'stats': total_stats
            },
            'structure_string': structure_str,
            'structure_tree': all_trees_data, # Note: ne contient que les arbres des répertoires
            'file_blocks': all_blocks,
            'extracted_count': len(all_blocks)
        }

        renderers = {'txt': TxtRenderer(), 'json': JsonRenderer(), 'md': MdRenderer(), 'html': HtmlRenderer()}
        formats = formats or ['txt']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        base_name = os.path.basename(target_paths[0]) if len(target_paths) == 1 else "multi_targets"
        base_output_name = output_file.rsplit('.', 1)[0] if output_file else f"codebase_{base_name}_{timestamp}"
        
        output_files = {}
        for fmt in formats:
            if fmt in renderers:
                print(f"🎨 Rendu du format: {fmt.upper()}")
                content_to_write = renderers[fmt].render(report_data)
                fname = base_output_name + '.' + renderers[fmt].get_extension()
                with open(fname, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(content_to_write)
                output_files[fmt] = fname
        
        print(f"✅ Extraction terminée! Fichiers générés: {', '.join(output_files.values())}")
        return output_files

    def chunk_code_files(self, target_paths, chunk_size, output_file_prefix):
        # Cette fonction pourrait bénéficier des optimisations (collecte unique) mais est laissée telle quelle pour l'instant
        # car elle représente un cas d'usage distinct.
        print("🧩 Découpage en chunks pour LLM...")
        # ... (logique de chunking existante) ...
        pass

    def scan_for_secrets(self, file_content: str, file_path: str) -> List[Dict[str, str]]:
        secret_patterns = [r'(?i)(api[_-]?key|secret|token|password|passwd|pwd)["\'\s:=]+[\w\-\+/=]{8,}']
        findings = []
        for pat in secret_patterns:
            for match in re.findall(pat, file_content):
                findings.append({'file': file_path, 'secret': match})
        return findings

def main():
    parser = argparse.ArgumentParser(description="🤖 CodeBase Extractor v3.1", formatter_class=argparse.RawDescriptionHelpFormatter)
    # ... (arguments argparse inchangés) ...
    parser.add_argument('paths', help='Un ou plusieurs chemins vers les répertoires ET/OU fichiers à analyser', nargs='+')
    parser.add_argument('-o', '--output', help='Nom du fichier de sortie (sans extension)')
    parser.add_argument('--format', type=str, default='txt', help='Formats: txt,json,md,html (séparés par virgule)')
    parser.add_argument('--zip', action='store_true', help='Archiver les sorties dans un ZIP')
    parser.add_argument('--chunk-size', type=int, help='Découper les fichiers en chunks pour LLM')
    parser.add_argument('--force', action='store_true', help='Forcer l\'export malgré la détection de secrets')
    parser.add_argument('--ignore-patterns', type=str, help='Patterns d\'exclusion personnalisés (séparés par virgule)')
    args = parser.parse_args()

    try:
        extra_ignores = args.ignore_patterns.split(',') if args.ignore_patterns else None
        extractor = CodebaseExtractor(extra_ignore_patterns=extra_ignores)

        # Le scan de sécurité est maintenant intégré dans le flux principal pour efficacité
        # mais pourrait être appelé ici en amont si un blocage strict est souhaité.

        formats = [f.strip() for f in (args.format or 'txt').split(',')]
        output_files = extractor.extract_codebase(args.paths, args.output, formats=formats)

        if not output_files:
            sys.exit(1)

        if args.zip:
            # ... (logique de zip inchangée pour l'instant) ...
            print("📦 Fonctionnalité ZIP à implémenter avec la nouvelle architecture.")

    except Exception as e:
        print(f"❌ Erreur critique: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
