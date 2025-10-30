# src/core.py
import os
import sys
import platform
import pathlib
import mimetypes
from datetime import datetime
from typing import Dict, Optional, List, Any, Tuple
import fnmatch
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

class CodebaseExtractor:
    """Agent intelligent pour extraire et formatter une codebase complète."""
    def __init__(self, extra_ignore_patterns: Optional[List[str]] = None):
        self.system_info = self._detect_system()
        self.supported_extensions = {
            '.py', '.js','.mjs', '.ts', '.txt', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp', 
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.sh', '.bash', '.html', '.css', 
            '.scss', '.json', '.yaml', '.yml', '.toml', '.ini', '.md', '.sql', 'Dockerfile', 'Makefile'
        }
        self.base_ignore_patterns = {
            '__pycache__', '.git', 'node_modules', 'venv', 'env', '.venv', 
            'build', 'dist', 'target', '*.log', '.DS_Store'
        }
        if extra_ignore_patterns:
            self.base_ignore_patterns.update(extra_ignore_patterns)

    def _detect_system(self) -> Dict[str, str]:
        system = platform.system().lower()
        return {
            'os': system, 'version': platform.version(), 'architecture': platform.architecture()[0],
            'python_version': platform.python_version(), 'encoding': sys.getdefaultencoding(), 'separator': os.sep
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
        if not paths: return []
        dir_paths = [os.path.abspath(p) for p in paths if os.path.isdir(p)]
        if len(dir_paths) <= 1: return dir_paths
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
        if name.startswith('.') and name not in {'.gitignore', '.dockerignore'}:
            return True
        return False

    def _is_code_file(self, filepath: str) -> bool:
        filename = os.path.basename(filepath)
        if filename in self.supported_extensions: return True
        ext = pathlib.Path(filepath).suffix.lower()
        if ext in self.supported_extensions: return True
        if not ext:
            mime_type, _ = mimetypes.guess_type(filepath)
            if mime_type and 'text' in mime_type: return True
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
                if self._is_ignored(item_path, item, dynamic_ignore_patterns): continue
                if os.path.isfile(item_path):
                    tree['files'].append(item)
                    tree['stats']['total_files'] += 1
                    if self._is_code_file(item_path): tree['stats']['code_files'] += 1
                elif os.path.isdir(item_path):
                    sub_tree = self._create_tree_structure(item_path, dynamic_ignore_patterns)
                    tree['dirs'][item] = sub_tree
                    tree['stats']['total_dirs'] += 1
                    for key in tree['stats']: tree['stats'][key] += sub_tree['stats'][key]
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

    def _collect_files_to_extract(self, root_path: str, dynamic_ignore_patterns: set) -> List[Tuple[str, str]]:
        files_to_process = []
        for root, dirs, files in os.walk(root_path, topdown=True):
            dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d), d, dynamic_ignore_patterns)]
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_ignored(file_path, file, dynamic_ignore_patterns): continue
                if self._is_code_file(file_path):
                    relative_path = os.path.relpath(file_path, root_path)
                    files_to_process.append((file_path, relative_path))
        return files_to_process

    def _extract_content_parallel(self, files_to_process: List[Tuple[str, str]]) -> list:
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

    def _collect_and_prepare_files(self, target_paths: List[str]) -> Tuple[List[str], List[str], List[Tuple[str, str]], Dict[str, int]]:
        if not target_paths:
            print("❌ Aucun chemin fourni.")
            return [], [], [], {}
        initial_abs_paths = {os.path.abspath(p) for p in target_paths}
        valid_dirs = sorted([p for p in initial_abs_paths if os.path.isdir(p)])
        valid_files = sorted([p for p in initial_abs_paths if os.path.isfile(p)])
        for p in initial_abs_paths:
            if not os.path.exists(p): print(f"⚠️ Chemin ignoré (inexistant ou permission refusée): {p}")
        clean_dirs = self._normalize_paths(valid_dirs)
        final_files = [f for f in valid_files if not any(f.startswith(d + os.sep) for d in clean_dirs)]
        all_files_to_process: List[Tuple[str, str]] = []
        total_stats = {'total_files': 0, 'total_dirs': 0, 'code_files': 0}
        for path in clean_dirs:
            dynamic_ignores = self._load_gitignore_patterns(path)
            all_files_to_process.extend(self._collect_files_to_extract(path, dynamic_ignores))
        for file_path in final_files:
            if self._is_code_file(file_path):
                relative_path = os.path.basename(file_path)
                all_files_to_process.append((file_path, relative_path))
        return clean_dirs, final_files, all_files_to_process, total_stats

    def extract_codebase(self, target_paths: List[str], output_file: Optional[str], formats: List[str], renderers: Dict) -> dict:
        print(f"🤖 CODEBASE EXTRACTOR v3.5 - Mode Rapport")
        clean_dirs, final_files, all_files_to_process, total_stats = self._collect_and_prepare_files(target_paths)
        if not all_files_to_process:
            print("❌ Aucun fichier valide à traiter. Arrêt de l'extraction.")
            return {}
        
        structure_parts = []
        for path in clean_dirs:
            dynamic_ignores = self._load_gitignore_patterns(path)
            tree = self._create_tree_structure(path, dynamic_ignores)
            project_name = os.path.basename(path)
            structure_parts.append(f"{project_name}/\n{self._format_tree_display(tree)}")
            for key in total_stats: total_stats[key] += tree['stats'][key]
        
        for file_path in final_files:
            structure_parts.append(f"{os.path.basename(file_path)} (fichier direct)")
            total_stats['total_files'] += 1
            total_stats['code_files'] += 1
            
        print(f"\n🚀 Lancement de l'extraction parallèle de {len(all_files_to_process)} fichiers...")
        all_blocks = self._extract_content_parallel(all_files_to_process)
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_data = {
            'header': {
                'projects': [os.path.basename(p) for p in clean_dirs],
                'direct_files': [os.path.basename(f) for f in final_files],
                'paths': sorted(list(os.path.abspath(p) for p in target_paths)),
                'date': now,
                'system': f"{self.system_info['os']} {self.system_info['architecture']}",
                'stats': total_stats
            },
            'structure_string': "\n".join(structure_parts),
            'structure_tree': [], # La logique pour peupler ceci pourrait être ajoutée
            'file_blocks': all_blocks,
            'extracted_count': len(all_blocks)
        }
        
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

    def chunk_code_files(self, target_paths: List[str], chunk_size: int, output_file_prefix: str):
        print(f"🤖 CODEBASE EXTRACTOR v3.5 - Mode Chunking (Taille: {chunk_size} caractères)")
        _clean_dirs, _final_files, all_files_to_process, _stats = self._collect_and_prepare_files(target_paths)
        if not all_files_to_process:
            print("❌ Aucun fichier valide à traiter. Arrêt du chunking.")
            return
        
        chunk_count = 1
        current_chunk_content: List[str] = []
        current_chunk_size = 0
        for file_path, relative_path in sorted(all_files_to_process):
            content = self._safe_read_file(file_path)
            if not content or content.startswith("[Erreur:"): continue
            
            file_header = f"--- START FILE: {relative_path} ---\n"
            file_footer = f"\n--- END FILE: {relative_path} ---\n\n"
            content_to_add = file_header + content + file_footer
            
            if current_chunk_size + len(content_to_add) > chunk_size and current_chunk_size > 0:
                output_filename = f"{output_file_prefix}_chunk_{chunk_count}.txt"
                print(f"📦 Écriture du chunk {chunk_count} ({current_chunk_size} caractères) -> {output_filename}")
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write("".join(current_chunk_content))
                chunk_count += 1
                current_chunk_content = []
                current_chunk_size = 0
            
            current_chunk_content.append(content_to_add)
            current_chunk_size += len(content_to_add)
            
        if current_chunk_content:
            output_filename = f"{output_file_prefix}_chunk_{chunk_count}.txt"
            print(f"📦 Écriture du dernier chunk {chunk_count} ({current_chunk_size} caractères) -> {output_filename}")
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write("".join(current_chunk_content))
        
        print(f"✅ Chunking terminé! {chunk_count} fichiers générés.")