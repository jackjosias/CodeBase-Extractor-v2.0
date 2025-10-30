# CodeBase Extractor v3.5 (Architecture Modulaire)

### Créé et maintenu par Jack-Josias

## Présentation

**CodeBase Extractor v3.5** est un agent Python intelligent et ultra-performant, conçu pour extraire, analyser et préparer une codebase pour l'audit, la documentation, l'archivage ou l'ingestion par une IA/LLM.

Cette version marque une refactorisation architecturale majeure, passant d'un script monolithique à une **structure modulaire** pour garantir la maintenabilité, la testabilité et l'évolutivité à long terme. Il fonctionne sur Windows, Linux et macOS, sans aucune dépendance externe.

## Fonctionnalités principales

*   **Architecture Modulaire (Nouveau) :** La logique est désormais séparée en modules distincts (CLI, moteur principal, renderers, utilitaires), appliquant le Principe de Responsabilité Unique pour une robustesse accrue.
*   **Intelligence `.gitignore` :** Lit et applique automatiquement les règles du fichier `.gitignore` trouvé à la racine de votre projet.
*   **Extraction Parallèle Haute Performance :** Utilise tous les cœurs de votre processeur pour lire les fichiers en parallèle, réduisant drastiquement le temps d'extraction.
*   **Rapports Multi-format :** Génération de rapports clairs et exploitables en **TXT, JSON, Markdown, et HTML** (option `--format`).
*   **Export ZIP (Non implémenté) :** La fonctionnalité d'archivage est prévue pour une version future.
*   **Analyse de Sécurité Intégrée :** Détecte les secrets/credentials potentiels et avertit l'utilisateur avant l'export.
*   **Découpage pour LLM :** Découpe automatiquement les fichiers en "chunks" de taille configurable (`--chunk-size`).
*   **Interface CLI Complète :** Options pour personnaliser la sortie, ignorer des motifs, forcer l'export et contrôler le mode interactif.

## Installation

Ce script fonctionne avec **Python 3.6+** et n'a besoin d'aucune bibliothèque externe.

1.  **Vérifiez votre version de Python :**

    ```bash
    python --version # ou sur certains systèmes python3 --version
    ```

2.  **Si Python n'est pas installé ou est une version antérieure à 3.6 :**
    *   **Windows :** Télécharger depuis [python.org](https://python.org) ou via le Microsoft Store.
    *   **macOS :** Utiliser Homebrew (`brew install python3`) ou télécharger depuis [python.org](https://python.org).
    *   **Linux (Ubuntu/Debian) :** `sudo apt update && sudo apt install python3`

**Aucune commande `pip install` n'est requise !**

## Structure du Projet

Le projet suit désormais une structure modulaire claire :

```python
CodeBase-Extractor/
├── codebase_extractor.py       # Point d'entrée principal (CLI)
├── src/
│   ├── __init__.py
│   ├── core.py                 # Moteur principal (parcours, lecture, .gitignore)
│   ├── renderers/              # Module pour les formats de sortie
│   │   ├── base_renderer.py    # Classe de base abstraite pour les renderers
│   │   ├── html_renderer.py    # Renderer pour le format HTML
│   │   ├── json_renderer.py    # Renderer pour le format JSON
│   │   ├── md_renderer.py      # Renderer pour le format Markdown
│   │   └── txt_renderer.py     # Renderer pour le format TXT
│   └── utils.py                # Fonctions utilitaires (sécurité, chunking)
└── README.md
```

## Guide d'utilisation complet

Ce guide couvre tous les cas d'usage avec des exemples concrets, en tenant compte des dernières fonctionnalités.

### Préparation

1.  **Télécharger le projet** et conserver sa structure de dossiers.
2.  **Ouvrir un terminal/console**.
3.  **Naviguer vers le dossier du projet** : `cd /chemin/vers/CodeBase-Extractor`

---
### CAS D'USAGE FONDAMENTAUX

#### #1 : Analyser un projet
Vous voulez extraire tout le code d'un projet.
```bash
# Analyser un projet qui se trouve ailleurs
python3 codebase_extractor.py /chemin/vers/mon/projet

# Analyser le projet courant (si vous êtes dans le dossier de votre projet)
# Note: vous devez fournir le chemin complet vers le script
python3 /chemin/vers/CodeBase-Extractor/codebase_extractor.py .
```
**Résultat :** Un fichier `.txt` est généré avec un nom automatique.

#### #2 : Nom de fichier et format personnalisés
Vous voulez contrôler la sortie.
```bash
# Nom personnalisé et format Markdown
python3 codebase_extractor.py . -o rapport_projet --format md

# Plusieurs formats en une seule fois
python3 codebase_extractor.py . -o rapport_projet --format txt,json,html
```
**Résultat :** Fichiers `rapport_projet.md`, `rapport_projet.txt`, `rapport_projet.json`, `rapport_projet.html` générés.

#### #3 : Extraction de plusieurs dossiers simultanément
Vous voulez combiner le contenu de plusieurs parties de votre projet.
```bash
python3 codebase_extractor.py ./frontend ./backend -o rapport_complet.txt
```
**Résultat :** Un seul rapport contenant l'arborescence et le contenu des deux dossiers.

**Exemple avec des chemins absolus génériques et des fichiers spécifiques :**
```bash
python3 codebase_extractor.py '/chemin/vers/mon/projet/bin/' '/chemin/vers/mon/projet/config/' '/chemin/vers/mon/projet/src/main.py' -o rapport_personnalise.txt
```
**Résultat :** Un rapport unique `rapport_personnalise.txt` incluant le contenu des dossiers et fichiers spécifiés par leurs chemins absolus génériques.

---
### CAS D'USAGE AVANCÉS

#### #4 : Préparation pour IA / LLM (Chunking)
Votre projet est volumineux et vous voulez le fournir à une IA qui a une limite de contexte.
```bash
# Découper le projet en morceaux de 4000 caractères
python3 codebase_extractor.py /chemin/vers/projet --chunk-size 4000 -o projet_pour_claude
```
**Résultat :** Une série de fichiers `projet_pour_claude_chunk_1.txt`, `projet_pour_claude_chunk_2.txt`, etc.

#### #5 : Utilisation en Scripting / Intégration Continue (CI/CD)
Vous voulez automatiser l'extraction sans interaction humaine.
```bash
# Le flag --no-interactive empêche toute question
python3 codebase_extractor.py . -o rapport_ci --no-interactive

# Le flag --force outrepasse les avertissements de sécurité
python3 codebase_extractor.py . -o rapport_audit --force --no-interactive
```

#### #6 : Exclusions personnalisées
Vous voulez ignorer des fichiers ou dossiers spécifiques en plus du `.gitignore`.
```bash
# Ignorer les fichiers de backup et les dossiers de test
python3 codebase_extractor.py . --ignore-patterns "*.bak,*.tmp,tests/"
```

#### #7 : Compression pour IA
Vous voulez une version du rapport sur une seule ligne, facile à copier-coller.
```bash
# Option 1: Automatique (si le mode interactif est activé)
python3 codebase_extractor.py . -o rapport.txt
# Le script demandera : "Voulez-vous créer une version compressée... ? (y/n)"

# Option 2: Forcée (pour les scripts)
python3 codebase_extractor.py . -o rapport.txt --oneline
```
**Résultat :** Un fichier supplémentaire `rapport.oneline.txt` sera créé.

---
### WORKFLOWS TYPIQUES

#### Audit de code
1.  `python3 codebase_extractor.py /projet/client -o audit_client --format md,txt --force`
2.  Analyser le `audit_client.md` pour une vue d'ensemble.
3.  Utiliser le `audit_client.txt` pour des analyses textuelles ou avec d'autres outils.

#### Onboarding d'un nouveau développeur
1.  `python3 codebase_extractor.py . -o doc_projet --format html`
2.  Partager le fichier `doc_projet.html` qui offre une vue navigable et facile à lire de toute la codebase.

#### Session de débug à distance
1.  `python3 codebase_extractor.py ./src -o debug_session.txt`
2.  Envoyer le fichier `debug_session.txt` à un collègue pour qu'il ait le contexte complet du code concerné.

---
### RÉSUMÉ DES COMMANDES ESSENTIELLES

```bash
# Basique
python3 codebase_extractor.py <chemin>

# Avec nom et format
python3 codebase_extractor.py <chemin> -o <nom_sortie> --format <formats>

# Pour IA (gros projets)
python3 codebase_extractor.py <chemin> --chunk-size 4000

# Pour scripts automatisés
python3 codebase_extractor.py <chemin> --no-interactive --force
```

Avec cette version modulaire, le script est plus robuste et prêt à évoluer pour de futurs cas d'usage !

## Sécurité & Bonnes pratiques

*   **Avertissement de Secrets :** Le script scanne les fichiers pour détecter des secrets (API keys, mots de passe, etc.). Si des secrets sont trouvés, **l'utilisateur est averti et doit confirmer l'export** (sauf si `--force` est utilisé).
*   **Risque de Déni de Service (DoS) :** Le script lit les fichiers en mémoire avant de les tronquer. Évitez de l'exécuter sur des répertoires contenant des fichiers non fiables de très grande taille (plusieurs Go).
*   **Vérification :** Il est **fortement recommandé** de toujours vérifier le contenu des rapports générés avant de les partager.

## Limitations

*   **Fichiers Volumineux :** Les fichiers de plus de 1Mo sont tronqués pour préserver la mémoire.
*   **Règles `.gitignore` :** La lecture est robuste pour la majorité des cas, mais pourrait ne pas interpréter certaines règles négatives complexes (`!pattern`) de la même manière que Git.
*   **Découpage LLM :** Le découpage est basé sur le nombre de caractères, pas sur une tokenisation sémantique.

## 🤝 Contribuer

Les contributions sont les bienvenues ! Pour assurer la qualité du projet, veuillez suivre ces étapes :

1.  Forkez le projet.
2.  Créez une nouvelle branche (`git checkout -b feature/NomDeLaFeature`).
3.  Faites vos modifications dans les modules appropriés (`src/core.py`, `src/renderers/`, etc.).
4.  **Important :** Si vous ajoutez ou modifiez des fonctionnalités, mettez à jour la documentation correspondante (`README.md`, `Guide complet`, etc.).
5.  Commitez vos changements (`git commit -m 'Ajout de telle fonctionnalité'`).
6.  Ouvrez une Pull Request.

---
© 2025 Jack-Josias – Tous droits réservés
