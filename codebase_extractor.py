#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODEBASE EXTRACTOR v2.0
Agent intelligent pour l'extraction automatique de codebase
Créé pour automatiser la récupération de code pour collaboration IA/LLM
"""

# =============================================
# CodeBase Extractor - Créé par Jack-Josias (2025)
# =============================================

import os
import sys
import platform
import pathlib
import mimetypes
import argparse
from datetime import datetime
from typing import Dict, Optional
import fnmatch
import zipfile
import json
import re

class CodebaseExtractor:
    """Agent intelligent pour extraire et formatter une codebase complète"""
    
    def __init__(self, extra_ignore_patterns=None):
        self.system_info = self._detect_system()
        self.supported_extensions = {
            # Langages de programmation
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cc', '.cxx',
            '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.r', '.m', '.mm', '.pl', '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat',
            '.cmd', '.vbs', '.lua', '.dart', '.elm', '.haskell', '.hs', '.clj', '.cljs',
            '.edn', '.f90', '.f95', '.fortran', '.cobol', '.cob', '.pas', '.pp', '.asm',
            '.s', '.sql', '.plsql', '.mysql', '.sqlite', '.psql',
            
            # Web et markup
            '.html', '.htm', '.xml', '.xhtml', '.svg', '.css', '.scss', '.sass', '.less',
            '.styl', '.vue', '.svelte', '.angular', '.react',
            
            # Configuration et données
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.config',
            '.properties', '.env', '.gitignore', '.gitconfig', '.dockerignore',
            '.editorconfig', '.prettierrc', '.eslintrc', '.babelrc', '.webpack.config.js',
            
            # Documentation
            '.md', '.rst', '.txt', '.adoc', '.tex', '.latex',
            
            # Autres
            '.dockerfile', '.docker', '.makefile', '.cmake', '.gradle', '.maven',
            '.ant', '.sbt', '.mix.exs', '.rebar.config', '.cargo.toml', '.pubspec.yaml',
            '.package.json', '.requirements.txt', '.pipfile', '.poetry.lock',
            '.gemfile', '.podfile', '.cartfile'
        }
        
        self.ignore_patterns = {
            # Dossiers système et cache
            '__pycache__', '.git', '.svn', '.hg', '.bzr', 'node_modules', '.npm',
            '.yarn', 'venv', 'env', '.env', 'virtualenv', '.venv', 'env/', 'venv/',
            'build', 'dist', 'target', 'bin', 'obj', 'out', '.build', '.dist',
            
            # IDE et éditeurs
            '.vscode', '.idea', '.vs', '.atom', '.sublime-text', '.brackets',
            '*.swp', '*.swo', '*~', '.DS_Store', 'Thumbs.db', 'desktop.ini',
            
            # Logs et temporaires
            'logs', '*.log', '*.tmp', '*.temp', '.cache', '.temp', 'tmp',
            
            # Packages et dépendances
            'vendor', 'packages', '.nuget', 'bower_components', 'jspm_packages',
            '.sass-cache', '.gradle', '.m2', '.ivy2'
        }.union(set(extra_ignore_patterns or []))
    
    def _detect_system(self) -> Dict[str, str]:
        """Détecte intelligemment le système d'exploitation et ses spécificités"""
        system = platform.system().lower()
        return {
            'os': system,
            'version': platform.version(),
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version(),
            'encoding': sys.getdefaultencoding(),
            'separator': '/' if system != 'windows' else '\\'
        }
    
    def _is_ignored(self, path: str, name: str) -> bool:
        """Vérifie si un fichier/dossier doit être ignoré"""
        # Vérification des patterns d'ignore
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(path, f"*{pattern}*"):
                return True
        
        # Ignore les fichiers cachés (commençant par .)
        if name.startswith('.') and name not in {'.env', '.gitignore', '.dockerignore'}:
            return True
            
        return False
    
    def _is_code_file(self, filepath: str) -> bool:
        """Détermine si un fichier est un fichier de code"""
        ext = pathlib.Path(filepath).suffix.lower()
        
        # Vérification par extension
        if ext in self.supported_extensions:
            return True
        
        # Vérification par nom de fichier spécial
        filename = os.path.basename(filepath).lower()
        special_files = {
            'makefile', 'dockerfile', 'rakefile', 'gemfile', 'pipfile',
            'cmakelists.txt', 'build.gradle', 'pom.xml', 'composer.json',
            'package.json', 'cargo.toml', 'go.mod', 'setup.py', 'requirements.txt'
        }
        
        if filename in special_files:
            return True
        
        # Vérification MIME type pour les fichiers sans extension
        if not ext:
            mime_type, _ = mimetypes.guess_type(filepath)
            if mime_type and 'text' in mime_type:
                return True
        
        return False
    
    def _safe_read_file(self, filepath: str) -> Optional[str]:
        """Lecture sécurisée d'un fichier avec gestion d'encodage"""
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    # Limite la taille pour éviter les très gros fichiers
                    if len(content) > 1000000:  # 1MB max
                        content = content[:1000000] + f"\n\n[... Fichier tronqué - taille originale: {len(content)} caractères]"
                    return content
            except (UnicodeDecodeError, PermissionError, OSError):
                continue
        
        return f"[Erreur: Impossible de lire le fichier {filepath}]"
    
    def _create_tree_structure(self, root_path: str) -> dict:
        """Crée une structure arborescente du projet"""
        tree: dict = {'files': [], 'dirs': {}, 'stats': {'total_files': 0, 'total_dirs': 0, 'code_files': 0}}
        try:
            for item in sorted(os.listdir(root_path)):
                if self._is_ignored(root_path, item):
                    continue
                item_path = os.path.join(root_path, item)
                if os.path.isfile(item_path):
                    files_list = tree['files']
                    if isinstance(files_list, list):
                        files_list.append(item)
                    stats_dict = tree['stats']
                    if isinstance(stats_dict, dict):
                        stats_dict['total_files'] += 1
                    if self._is_code_file(item_path):
                        if isinstance(stats_dict, dict):
                            stats_dict['code_files'] += 1
                elif os.path.isdir(item_path):
                    sub_tree = self._create_tree_structure(item_path)
                    dirs_dict = tree['dirs']
                    if isinstance(dirs_dict, dict):
                        dirs_dict[item] = sub_tree
                    stats_dict = tree['stats']
                    if isinstance(stats_dict, dict):
                        stats_dict['total_dirs'] += 1
                        for key in ['total_files', 'total_dirs', 'code_files']:
                            stats_dict[key] += sub_tree['stats'][key]
        except PermissionError:
            tree['error'] = "Permission refusée"
        return tree
    
    def _format_tree_display(self, tree: Dict, prefix: str = "") -> str:
        """Formate l'affichage de l'arborescence"""
        result = []
        
        # Affichage des dossiers
        dirs = list(tree.get('dirs', {}).keys())
        files = tree.get('files', [])
        
        all_items = [(d, True) for d in dirs] + [(f, False) for f in files if self._is_code_file(os.path.join(".", f))]
        
        for i, (item, is_dir) in enumerate(all_items):
            is_last_item = (i == len(all_items) - 1)
            current_prefix = "└── " if is_last_item else "├── "
            next_prefix = prefix + ("    " if is_last_item else "│   ")
            
            if is_dir:
                result.append(f"{prefix}{current_prefix}{item}/")
                result.append(self._format_tree_display(tree['dirs'][item], next_prefix))
            else:
                result.append(f"{prefix}{current_prefix}{item}")
        
        return "\n".join(filter(None, result))
    
    def extract_codebase(self, target_paths, output_file: Optional[str] = None, formats=None) -> dict:
        """Extraction de codebase pour un ou plusieurs dossiers (liste ou str unique), multi-format"""
        print("🤖 CODEBASE EXTRACTOR v2.0")
        if isinstance(target_paths, str):
            target_paths = [target_paths]
        elif not isinstance(target_paths, list):
            raise ValueError("target_paths doit être un str ou une liste de str")

        all_trees = []
        all_blocks = []
        total_stats = {'total_files': 0, 'total_dirs': 0, 'code_files': 0}
        extracted_count = 0
        content_parts = []
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        system_str = f"{self.system_info['os']} {self.system_info['architecture']}"

        # Extraction de chaque dossier
        for path in target_paths:
            print(f"🎯 Analyse du répertoire: {os.path.abspath(path)}")
            if not os.path.exists(path):
                raise FileNotFoundError(f"Le chemin spécifié n'existe pas: {path}")
            if not os.path.isdir(path):
                raise NotADirectoryError(f"Le chemin n'est pas un répertoire: {path}")
            print("🌳 Analyse de l'arborescence...")
            tree = self._create_tree_structure(path)
            all_trees.append((os.path.basename(os.path.abspath(path)), tree))

        # Préparation du fichier de sortie
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if len(target_paths) == 1:
                project_name = os.path.basename(os.path.abspath(target_paths[0]))
            else:
                project_name = "multi_projects"
            output_file = f"codebase_{project_name}_{timestamp}.txt"
        print(f"📝 Génération du fichier: {output_file}")

        # En-tête
        content_parts.append("=" * 80)
        content_parts.append("CODEBASE EXTRACTION REPORT")
        content_parts.append("=" * 80)
        if len(target_paths) == 1:
            content_parts.append(f"Projet: {os.path.basename(os.path.abspath(target_paths[0]))}")
            content_parts.append(f"Chemin: {os.path.abspath(target_paths[0])}")
        else:
            content_parts.append(f"Projets: {', '.join([os.path.basename(os.path.abspath(p)) for p in target_paths])}")
            content_parts.append(f"Chemins: {', '.join([os.path.abspath(p) for p in target_paths])}")
        content_parts.append(f"Date d'extraction: {now}")
        content_parts.append(f"Système: {system_str}")
        content_parts.append("")

        # Statistiques globales
        for _, tree in all_trees:
            for key in total_stats:
                total_stats[key] += tree['stats'][key]
        content_parts.append("STATISTIQUES DU PROJET:")
        content_parts.append("-" * 30)
        content_parts.append(f"📁 Total dossiers: {total_stats['total_dirs']}")
        content_parts.append(f"📄 Total fichiers: {total_stats['total_files']}")
        content_parts.append(f"💻 Fichiers de code: {total_stats['code_files']}")
        content_parts.append("")

        # Arborescence combinée
        content_parts.append("STRUCTURE DU PROJET:")
        content_parts.append("-" * 30)
        for name, tree in all_trees:
            content_parts.append(f"{name}/")
            content_parts.append(self._format_tree_display(tree))
        content_parts.append("")
        content_parts.append("=" * 80)
        content_parts.append("CONTENU DES FICHIERS DE CODE")
        content_parts.append("=" * 80)
        content_parts.append("")

        # Extraction des fichiers pour chaque dossier
        def extract_files_recursive(current_path: str, relative_path: str = ""):
            nonlocal extracted_count
            blocks = []
            try:
                for item in sorted(os.listdir(current_path)):
                    if self._is_ignored(current_path, item):
                        continue
                    item_path = os.path.join(current_path, item)
                    item_relative = os.path.join(relative_path, item) if relative_path else item
                    if os.path.isfile(item_path) and self._is_code_file(item_path):
                        print(f"📖 Extraction: {item_relative}")
                        file_content = self._safe_read_file(item_path)
                        block = f"'{item_relative}': [\n" + "-" * 50 + "\n" + (file_content if isinstance(file_content, str) else "[Aucun contenu lu]") + "\n" + "-" * 50 + "\n]"
                        blocks.append(block)
                        extracted_count += 1
                    elif os.path.isdir(item_path):
                        blocks.extend(extract_files_recursive(item_path, item_relative))
            except PermissionError as e:
                blocks.append(f"[ERREUR PERMISSION: {current_path} - {str(e)}]")
            return blocks

        for path in target_paths:
            all_blocks.extend(extract_files_recursive(path))

        # Pied de page
        content_parts.append("=" * 80)
        content_parts.append("FIN DE L'EXTRACTION")
        content_parts.append("=" * 80)
        content_parts.append(f"✅ {extracted_count} fichiers extraits avec succès")
        content_parts.append(f"📅 Extraction terminée le {now}")

        # Construction finale du contenu TXT
        final_content = "\n".join(content_parts)
        if all_blocks:
            final_content += " " + " && ".join(all_blocks) + "\n"

        # Construction du contenu JSON
        json_report = {
            'header': {
                'projects': [os.path.basename(os.path.abspath(p)) for p in target_paths],
                'paths': [os.path.abspath(p) for p in target_paths],
                'date': now,
                'system': system_str,
                'stats': total_stats
            },
            'structure': [{name: tree} for name, tree in all_trees],
            'files': all_blocks
        }

        # Construction du contenu Markdown
        md_content = [
            "# Codebase Extraction Report\n",
            f"**Date d'extraction**: {now}",
            f"**Système**: {system_str}",
            f"**Projets**: {', '.join([os.path.basename(os.path.abspath(p)) for p in target_paths])}",
            f"**Chemins**: {', '.join([os.path.abspath(p) for p in target_paths])}\n",
            "## Statistiques",
            f"- Total dossiers: {total_stats['total_dirs']}",
            f"- Total fichiers: {total_stats['total_files']}",
            f"- Fichiers de code: {total_stats['code_files']}\n",
            "## Structure du projet",
        ]
        for name, tree in all_trees:
            md_content.append(f"### {name}/\n")
            md_content.append('```\n' + self._format_tree_display(tree) + '\n```')
        md_content.append("\n## Contenu des fichiers de code\n")
        for block in all_blocks:
            md_content.append('```\n' + block + '\n```')
        md_content.append(f"\n✅ {extracted_count} fichiers extraits avec succès\n")
        md_content.append(f"Extraction terminée le {now}\n")
        md_final = "\n".join(md_content)

        # Construction du contenu HTML
        html_content = [
            "<html><head><meta charset='utf-8'><title>Codebase Extraction Report</title></head><body>",
            "<h1>Codebase Extraction Report</h1>",
            f"<p><b>Date d'extraction:</b> {now}<br><b>Système:</b> {system_str}<br><b>Projets:</b> {', '.join([os.path.basename(os.path.abspath(p)) for p in target_paths])}<br><b>Chemins:</b> {', '.join([os.path.abspath(p) for p in target_paths])}</p>",
            f"<h2>Statistiques</h2><ul><li>Total dossiers: {total_stats['total_dirs']}</li><li>Total fichiers: {total_stats['total_files']}</li><li>Fichiers de code: {total_stats['code_files']}</li></ul>",
            "<h2>Structure du projet</h2>"
        ]
        for name, tree in all_trees:
            html_content.append(f"<h3>{name}/</h3><pre>{self._format_tree_display(tree)}</pre>")
        html_content.append("<h2>Contenu des fichiers de code</h2>")
        for block in all_blocks:
            html_content.append(f"<pre>{block}</pre>")
        html_content.append(f"<p>✅ {extracted_count} fichiers extraits avec succès<br>Extraction terminée le {now}</p>")
        html_content.append("</body></html>")
        html_final = "\n".join(html_content)

        # Gestion des formats demandés
        formats = formats or ['txt']
        base_output = output_file.rsplit('.', 1)[0] if output_file else f"codebase_{now.replace(':','').replace(' ','_')}"
        output_files = {}
        for fmt in formats:
            if fmt == 'txt':
                fname = base_output + '.txt'
                with open(fname, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(final_content)
                output_files['txt'] = fname
            elif fmt == 'json':
                fname = base_output + '.json'
                with open(fname, 'w', encoding='utf-8', errors='ignore') as f:
                    json.dump(json_report, f, ensure_ascii=False, indent=2)
                output_files['json'] = fname
            elif fmt == 'md':
                fname = base_output + '.md'
                with open(fname, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(md_final)
                output_files['md'] = fname
            elif fmt == 'html':
                fname = base_output + '.html'
                with open(fname, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(html_final)
                output_files['html'] = fname
        print(f"✅ Extraction terminée! Fichiers générés: {', '.join(output_files.values())}")
        return output_files

    def chunk_code_files(self, target_paths, chunk_size, output_file_prefix):
        """Découpe les fichiers extraits en chunks de taille chunk_size (en caractères) pour LLM."""
        chunks = []
        for path in target_paths:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not self._is_ignored(root, d)]
                for file in files:
                    file_path = os.path.join(root, file)
                    if self._is_ignored(root, file) or not self._is_code_file(file_path):
                        continue
                    content = self._safe_read_file(file_path)
                    if not content:
                        continue
                    # Découpage en chunks
                    for i in range(0, len(content), chunk_size):
                        chunk = content[i:i+chunk_size]
                        chunks.append({
                            'file': file_path,
                            'chunk_index': i // chunk_size + 1,
                            'chunk': chunk
                        })
        # Génération d'un rapport spécial pour LLM
        llm_report_txt = []
        for c in chunks:
            llm_report_txt.append(f"Fichier: {c['file']} | Chunk {c['chunk_index']}\n" + '-'*40 + f"\n{c['chunk']}\n" + '-'*40 + '\n')
        llm_report_path = f"{output_file_prefix}_llm_chunks.txt"
        with open(llm_report_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.write("\n".join(llm_report_txt))
        print(f"🧩 Rapport LLM (chunks) généré: {llm_report_path}")
        return llm_report_path

    def scan_for_secrets(self, file_content, file_path):
        """Détecte des patterns de secrets/credentials dans le contenu d'un fichier."""
        # Patterns simples pour API keys, tokens, mots de passe (améliorable)
        secret_patterns = [
            r'(?i)(api[_-]?key|secret|token|password|passwd|pwd)["\'\s:=]+[\w\-\+/=]{8,}',
            r'(?i)aws[_-]?secret[_-]?access[_-]?key["\'\s:=]+[\w\-\+/=]{8,}',
            r'(?i)ghp_[0-9a-zA-Z]{36,}', # GitHub token
            r'(?i)sk_live_[0-9a-zA-Z]{24,}', # Stripe key
            r'(?i)AIza[0-9A-Za-z\-_]{35,}', # Google API key
        ]
        findings = []
        for pat in secret_patterns:
            for match in re.findall(pat, file_content):
                findings.append({'file': file_path, 'secret': match})
        return findings

def main():
    """Point d'entrée principal avec interface ligne de commande"""
    parser = argparse.ArgumentParser(
        description="🤖 CodeBase Extractor - Agent intelligent d'extraction de codebase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python codebase_extractor.py /path/to/project
  python codebase_extractor.py . -o mon_projet.txt
  python codebase_extractor.py ~/Documents/MonProjet --output extraction.txt
        """
    )
    
    parser.add_argument('paths', 
                       help='Un ou plusieurs chemins vers les répertoires à analyser (séparés par un espace)', nargs='+')
    parser.add_argument('-o', '--output', help='Nom du fichier de sortie (optionnel)')
    parser.add_argument('--format', type=str, default='txt', help='Format(s) du rapport: txt,json,md,html (séparés par des virgules)')
    parser.add_argument('--zip', action='store_true', help='Exporter le rapport et les fichiers extraits dans une archive ZIP')
    parser.add_argument('--chunk-size', type=int, help='Découper les fichiers extraits en chunks de cette taille (en caractères) pour LLM')
    parser.add_argument('--force', action='store_true', help='Continuer même si des secrets potentiels sont détectés')
    parser.add_argument('--ignore-patterns', type=str, help='Ajouter des motifs d\'exclusion personnalisés (séparés par des virgules)')
    args = parser.parse_args()
    try:
        extra_ignores = args.ignore_patterns.split(',') if args.ignore_patterns else None
        extractor = CodebaseExtractor(extra_ignore_patterns=extra_ignores)
        formats = [f.strip() for f in (args.format or 'txt').split(',')]
        output_files = extractor.extract_codebase(args.paths, args.output, formats=formats)

        # Export ZIP si demandé
        if args.zip:
            zip_name = list(output_files.values())[0].rsplit('.', 1)[0] + '.zip'
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Ajouter les rapports
                for f in output_files.values():
                    zipf.write(f, arcname=os.path.basename(f))
                # Ajouter tous les fichiers extraits (parcours des dossiers)
                def add_extracted_files(current_path, relative_path=""):
                    for item in sorted(os.listdir(current_path)):
                        if extractor._is_ignored(current_path, item):
                            continue
                        item_path = os.path.join(current_path, item)
                        item_relative = os.path.join(relative_path, item) if relative_path else item
                        if os.path.isfile(item_path) and extractor._is_code_file(item_path):
                            zipf.write(item_path, arcname=os.path.join('extracted_files', item_relative))
                        elif os.path.isdir(item_path):
                            add_extracted_files(item_path, item_relative)
                for path in args.paths:
                    add_extracted_files(path)
            print(f"📦 Archive ZIP générée: {os.path.abspath(zip_name)}")

        # Découpage automatique en chunks pour LLM
        if args.chunk_size:
            prefix = args.output.rsplit('.', 1)[0] if args.output else list(output_files.values())[0].rsplit('.', 1)[0]
            extractor.chunk_code_files(args.paths, args.chunk_size, prefix)
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {str(e)}")
        sys.exit(1)

    # Analyse de sécurité : scan des fichiers extraits pour secrets
    all_findings = []
    for path in args.paths:
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not extractor._is_ignored(root, d)]
            for file in files:
                file_path = os.path.join(root, file)
                if extractor._is_ignored(root, file) or not extractor._is_code_file(file_path):
                    continue
                content = extractor._safe_read_file(file_path)
                findings = extractor.scan_for_secrets(content, file_path)
                if findings:
                    all_findings.extend(findings)
    if all_findings and not args.force:
        print("\n⚠️  ATTENTION : Des secrets ou credentials potentiels ont été détectés dans les fichiers suivants :")
        for f in all_findings:
            print(f"- {f['file']} : {f['secret']}")
        print("\nPour votre sécurité, il est recommandé de retirer ces fichiers ou de supprimer les secrets avant de partager le rapport.")
        resp = input("Voulez-vous continuer l'export malgré tout ? (oui/non) : ").strip().lower()
        if resp not in ("oui", "o", "yes", "y"):
            print("❌ Export annulé par l'utilisateur pour raison de sécurité.")
            sys.exit(1)
    elif all_findings:
        print("\n⚠️  Secrets détectés mais export forcé (--force). Soyez prudent !")

if __name__ == "__main__":
    main()

# ---
# Script développé et maintenu par Jack-Josias (2025)