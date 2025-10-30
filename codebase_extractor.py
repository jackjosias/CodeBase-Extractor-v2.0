#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODEBASE EXTRACTOR v3.5 (Refactored)
Point d'entrée principal et orchestrateur de l'extraction.
"""
# ==============================================================================
# CodeBase Extractor - Créé et maintenu par Jack-Josias (2025)
# Architecture refactorisée par Linus-Torvalds_ULTIMATE_AGENT_066.0_Kratos
# ==============================================================================
import sys
import argparse

# Import des composants depuis la nouvelle structure modulaire
from src.core import CodebaseExtractor
from src.utils import compress_to_oneline, handle_interactive_compression
from src.renderers.txt_renderer import TxtRenderer
from src.renderers.json_renderer import JsonRenderer
from src.renderers.md_renderer import MdRenderer
from src.renderers.html_renderer import HtmlRenderer

def main():
    """Fonction principale pour parser les arguments et lancer l'extraction."""
    parser = argparse.ArgumentParser(
        description="🤖 CodeBase Extractor v3.5 (Refactored)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('paths', help='Un ou plusieurs chemins vers les répertoires ET/OU fichiers à analyser', nargs='+')
    parser.add_argument('-o', '--output', help='Nom de base du fichier de sortie (sans extension)')
    parser.add_argument('--format', type=str, default='txt', help='Formats: txt,json,md,html (séparés par virgule)')
    parser.add_argument('--zip', action='store_true', help='Archiver les sorties dans un ZIP (non implémenté)')
    parser.add_argument('--chunk-size', type=int, help='Activer le mode chunking et définir la taille max en caractères')
    parser.add_argument('--force', action='store_true', help='Forcer l\'export malgré la détection de secrets')
    parser.add_argument('--ignore-patterns', type=str, help='Patterns d\'exclusion personnalisés (séparés par virgule)')
    parser.add_argument('--oneline', action='store_true', help='Crée une version compressée sur une ligne du rapport texte pour les LLMs')
    parser.add_argument('--no-interactive', action='store_true', help='Désactive toute invite interactive à la fin de l\'exécution')
    
    args = parser.parse_args()

    try:
        extra_ignores = args.ignore_patterns.split(',') if args.ignore_patterns else None
        
        # Initialisation du moteur principal
        extractor = CodebaseExtractor(extra_ignore_patterns=extra_ignores)

        if args.chunk_size:
            output_prefix = args.output if args.output else "codebase_output"
            extractor.chunk_code_files(args.paths, args.chunk_size, output_prefix)
        else:
            # Dictionnaire des renderers disponibles
            available_renderers = {
                'txt': TxtRenderer(),
                'json': JsonRenderer(),
                'md': MdRenderer(),
                'html': HtmlRenderer()
            }
            
            formats = [f.strip() for f in (args.format or 'txt').split(',')]
            
            # Exécution de l'extraction
            output_files = extractor.extract_codebase(args.paths, args.output, formats, available_renderers)
            
            if not output_files:
                sys.exit(1)

            # Gestion de la compression post-traitement
            if args.oneline:
                file_to_compress = None
                if 'txt' in output_files:
                    file_to_compress = output_files['txt']
                elif 'md' in output_files:
                    file_to_compress = output_files['md']
                
                if file_to_compress:
                    compress_to_oneline(file_to_compress)
                else:
                    print("⚠️ L'option --oneline fonctionne mieux avec les formats .txt ou .md, qui n'ont pas été générés.")
            elif not args.no_interactive:
                handle_interactive_compression(output_files)

        if args.zip:
            print("📦 Fonctionnalité ZIP non implémentée.")

    except Exception as e:
        print(f"❌ Erreur critique: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()