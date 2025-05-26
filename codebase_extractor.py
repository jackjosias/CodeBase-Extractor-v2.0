#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODEBASE EXTRACTOR v2.0
Agent intelligent pour l'extraction automatique de codebase
Créé pour automatiser la récupération de code pour collaboration IA/LLM
"""

import os
import sys
import platform
import pathlib
import mimetypes
import argparse
from datetime import datetime
from typing import List, Dict, Set, Optional
import fnmatch

class CodebaseExtractor:
    """Agent intelligent pour extraire et formatter une codebase complète"""
    
    def __init__(self):
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
        }
    
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
    
    def _create_tree_structure(self, root_path: str) -> Dict:
        """Crée une structure arborescente du projet"""
        tree = {'files': [], 'dirs': {}, 'stats': {'total_files': 0, 'total_dirs': 0, 'code_files': 0}}
        
        try:
            for item in sorted(os.listdir(root_path)):
                if self._is_ignored(root_path, item):
                    continue
                
                item_path = os.path.join(root_path, item)
                
                if os.path.isfile(item_path):
                    tree['files'].append(item)
                    tree['stats']['total_files'] += 1
                    if self._is_code_file(item_path):
                        tree['stats']['code_files'] += 1
                
                elif os.path.isdir(item_path):
                    tree['dirs'][item] = self._create_tree_structure(item_path)
                    tree['stats']['total_dirs'] += 1
                    # Agrégation des stats
                    for key in tree['stats']:
                        tree['stats'][key] += tree['dirs'][item]['stats'][key]
        
        except PermissionError:
            tree['error'] = "Permission refusée"
        
        return tree
    
    def _format_tree_display(self, tree: Dict, prefix: str = "", is_last: bool = True) -> str:
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
                result.append(self._format_tree_display(tree['dirs'][item], next_prefix, is_last_item))
            else:
                result.append(f"{prefix}{current_prefix}{item}")
        
        return "\n".join(filter(None, result))
    
    def extract_codebase(self, target_path: str, output_file: str = None) -> str:
        """Fonction principale d'extraction de codebase"""
        print(f"🤖 CODEBASE EXTRACTOR v2.0")
        print(f"📍 Système détecté: {self.system_info['os']} {self.system_info['architecture']}")
        print(f"🎯 Analyse du répertoire: {os.path.abspath(target_path)}")
        
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Le chemin spécifié n'existe pas: {target_path}")
        
        if not os.path.isdir(target_path):
            raise NotADirectoryError(f"Le chemin n'est pas un répertoire: {target_path}")
        
        # Création de la structure arborescente
        print("🌳 Analyse de l'arborescence...")
        tree = self._create_tree_structure(target_path)
        
        # Préparation du fichier de sortie
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = os.path.basename(os.path.abspath(target_path))
            output_file = f"codebase_{project_name}_{timestamp}.txt"
        
        print(f"📝 Génération du fichier: {output_file}")
        
        # Génération du contenu
        content_parts = []
        
        # En-tête
        content_parts.append("=" * 80)
        content_parts.append("CODEBASE EXTRACTION REPORT")
        content_parts.append("=" * 80)
        content_parts.append(f"Projet: {os.path.basename(os.path.abspath(target_path))}")
        content_parts.append(f"Chemin: {os.path.abspath(target_path)}")
        content_parts.append(f"Date d'extraction: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content_parts.append(f"Système: {self.system_info['os']} {self.system_info['architecture']}")
        content_parts.append("")
        
        # Statistiques
        content_parts.append("STATISTIQUES DU PROJET:")
        content_parts.append("-" * 30)
        content_parts.append(f"📁 Total dossiers: {tree['stats']['total_dirs']}")
        content_parts.append(f"📄 Total fichiers: {tree['stats']['total_files']}")
        content_parts.append(f"💻 Fichiers de code: {tree['stats']['code_files']}")
        content_parts.append("")
        
        # Arborescence
        content_parts.append("STRUCTURE DU PROJET:")
        content_parts.append("-" * 30)
        content_parts.append(f"{os.path.basename(os.path.abspath(target_path))}/")
        content_parts.append(self._format_tree_display(tree))
        content_parts.append("")
        content_parts.append("=" * 80)
        content_parts.append("CONTENU DES FICHIERS DE CODE")
        content_parts.append("=" * 80)
        content_parts.append("")
        
        # Extraction des fichiers
        extracted_count = 0
        
        def extract_files_recursive(current_path: str, relative_path: str = ""):
            nonlocal extracted_count
            
            try:
                for item in sorted(os.listdir(current_path)):
                    if self._is_ignored(current_path, item):
                        continue
                    
                    item_path = os.path.join(current_path, item)
                    item_relative = os.path.join(relative_path, item) if relative_path else item
                    
                    if os.path.isfile(item_path) and self._is_code_file(item_path):
                        print(f"📖 Extraction: {item_relative}")
                        
                        # Format demandé: ['chemin_relatif':[contenu]]
                        content_parts.append(f"['{item_relative}': [")
                        content_parts.append("-" * 50)
                        
                        file_content = self._safe_read_file(item_path)
                        content_parts.append(file_content)
                        
                        content_parts.append("-" * 50)
                        content_parts.append("]]")
                        content_parts.append("")
                        extracted_count += 1
                    
                    elif os.path.isdir(item_path):
                        extract_files_recursive(item_path, item_relative)
            
            except PermissionError as e:
                content_parts.append(f"[ERREUR PERMISSION: {current_path} - {str(e)}]")
        
        # Lancement de l'extraction
        extract_files_recursive(target_path)
        
        # Pied de page
        content_parts.append("=" * 80)
        content_parts.append("FIN DE L'EXTRACTION")
        content_parts.append("=" * 80)
        content_parts.append(f"✅ {extracted_count} fichiers extraits avec succès")
        content_parts.append(f"📅 Extraction terminée le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Écriture du fichier
        final_content = "\n".join(content_parts)
        
        try:
            with open(output_file, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(final_content)
        except PermissionError:
            # Fallback vers le répertoire home si permission refusée
            home_output = os.path.join(os.path.expanduser("~"), output_file)
            with open(home_output, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(final_content)
            output_file = home_output
        
        print(f"✅ Extraction terminée!")
        print(f"📁 Fichier généré: {os.path.abspath(output_file)}")
        print(f"📊 {extracted_count} fichiers de code extraits")
        
        return output_file

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
    
    parser.add_argument('path', 
                       help='Chemin vers le répertoire du projet à analyser')
    parser.add_argument('-o', '--output', 
                       help='Nom du fichier de sortie (optionnel)')
    
    args = parser.parse_args()
    
    try:
        extractor = CodebaseExtractor()
        output_file = extractor.extract_codebase(args.path, args.output)
        print(f"\n🎉 Mission accomplie! Votre codebase est prête dans: {output_file}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()