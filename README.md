
# CodeBase Extractor v2.0 🤖

**Agent intelligent pour l'extraction automatique et la présentation de codebases, facilitant la collaboration avec des IA/LLM.**

## 📖 Table des Matières

- [Description](#description-)
- [🌟 Fonctionnalités Clés](#-fonctionnalités-clés)
- [🎯 Objectif Principal](#-objectif-principal)
- [🛠️ Prérequis](#️-prérequis)
- [⚙️ Installation](#️-installation)
- [🚀 Utilisation](#-utilisation)
  - [Options de la Ligne de Commande](#options-de-la-ligne-de-commande)
  - [Exemples d'Utilisation](#exemples-dutilisation)
- [📄 Format de Sortie](#-format-de-sortie)
- [🏗️ Structure du Script](#️-structure-du-script)
- [🤝 Contribuer](#-contribuer)
- [📜 Licence](#-licence)

## Description 📝

`CodeBase Extractor` est un script Python conçu pour automatiser intégralement le processus de récupération du contenu d'une codebase. Il parcourt récursivement un répertoire de projet, identifie intelligemment les fichiers de code pertinents, lit leur contenu, et génère un unique fichier texte consolidé. Ce fichier de sortie inclut des statistiques sur le projet, une représentation de son arborescence, et le contenu complet des fichiers de code, formaté de manière optimale pour être utilisé avec des modèles de langage volumineux (IA/LLM) ou pour d'autres tâches d'analyse et de documentation.

## 🌟 Fonctionnalités Clés

- **Parcours Récursif Complet** : Analyse tous les dossiers et sous-dossiers du projet cible.
- **Extraction Intelligente de Fichiers** :
    - Supporte une vaste gamme d'extensions de fichiers de code, de configuration, de documentation et web (voir la liste dans le script).
    - Reconnaît les noms de fichiers spéciaux (Makefile, Dockerfile, package.json, etc.).
    - Tente une détection par type MIME pour les fichiers sans extension.
- **Ignorance Automatique** : Exclut automatiquement les dossiers et fichiers non pertinents (ex: `node_modules`, `.git`, `__pycache__`, fichiers IDE, logs, etc.) grâce à une liste configurable de motifs d'ignorance.
- **Lecture Sécurisée des Fichiers** :
    - Gère plusieurs encodages (UTF-8, UTF-16, Latin-1, etc.) pour une compatibilité maximale.
    - Ignore les erreurs de décodage pour ne pas interrompre le processus.
    - Limite la taille des fichiers lus (actuellement 1MB) pour éviter les problèmes avec des fichiers excessivement volumineux, en signalant la troncature.
- **Rapport Détaillé en Sortie** :
    - En-tête avec métadonnées de l'extraction (nom du projet, chemin, date, système).
    - Statistiques du projet (nombre total de fichiers/dossiers, nombre de fichiers de code).
    - Affichage de l'arborescence du projet (fichiers de code uniquement).
    - Contenu de chaque fichier de code extrait, clairement délimité et identifié par son chemin relatif.
- **Format de Sortie Optimisé pour IA/LLM** : Le contenu des fichiers est présenté dans un format `['chemin_relatif': [contenu]]` facilement parsable ou directement ingérable par des modèles de langage.
- **Autonome et Portable** : Ne nécessite aucune dépendance externe, uniquement Python 3.6+.
- **Interface Ligne de Commande (CLI)** : Utilisation simple via `argparse`.

## 🎯 Objectif Principal

L'objectif principal de `CodeBase Extractor` est de **faire gagner un temps considérable** aux développeurs et aux analystes en automatisant la tâche souvent fastidieuse et répétitive de collecte manuelle de l'ensemble du code source d'un projet. Cela est particulièrement utile pour :

- Préparer une codebase pour l'analyse par des Intelligences Artificielles (IA) ou des Modèles de Langage Volumineux (LLM) comme ChatGPT, Claude, etc.
- Créer une vue d'ensemble consolidée d'un projet pour des revues de code.
- Archiver l'état d'une codebase à un instant T.
- Faciliter le partage de code avec des collaborateurs.
- Générer une base pour la documentation technique.

## 🛠️ Prérequis

- **Python 3.6 ou supérieur.**

C'est tout ! Le script n'utilise que des bibliothèques Python standard, donc aucune installation de paquet externe n'est nécessaire.

Pour vérifier votre version de Python :
```bash
python --version
# ou
python3 --version
```

## ⚙️ Installation

1.  **Sauvegardez le script** : Enregistrez le code sous le nom `codebase_extractor.py` dans un répertoire de votre choix.
2.  **Rendre exécutable (Optionnel, pour Linux/macOS)** :
    ```bash
    chmod +x codebase_extractor.py
    ```

## 🚀 Utilisation

Le script s'utilise en ligne de commande.

### Options de la Ligne de Commande

```
usage: codebase_extractor.py [-h] [-o OUTPUT] path

🤖 CodeBase Extractor - Agent intelligent d'extraction de codebase

positional arguments:
  path                  Chemin vers le répertoire du projet à analyser

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Nom du fichier de sortie (optionnel)

Exemples d'utilisation:
 python codebase_extractor.py /path/to/project
 python codebase_extractor.py . -o mon_projet.txt
 python codebase_extractor.py ~/Documents/MonProjet --output extraction.txt
```

### Exemples d'Utilisation

1.  **Analyser le projet dans le répertoire courant et générer un fichier de sortie avec un nom automatique** :
    (Si vous êtes dans `/home/user/MonProjet`)
    ```bash
    python codebase_extractor.py .
    ```
    Cela générera un fichier comme `codebase_MonProjet_YYYYMMDD_HHMMSS.txt` dans le répertoire courant.

2.  **Analyser un projet spécifique et spécifier le nom du fichier de sortie** :
    ```bash
    python codebase_extractor.py /chemin/vers/un/autre/projet -o resultat_extraction.txt
    ```

3.  **Analyser le projet courant et sauvegarder la sortie dans un répertoire spécifique avec un nom personnalisé** :
    ```bash
    python codebase_extractor.py . -o /chemin/vers/mes_extractions/mon_projet_special.txt
    ```

Pour plus de cas d'usage (collaboration IA, audit, backup, documentation, etc.), référez-vous au document `Guide complet d'utilisation - Tous les cas d'usage.txt` fourni avec ce script.

## 📄 Format de Sortie

Le fichier `.txt` généré contiendra les sections suivantes :

1.  **En-tête du Rapport** :
    - Titre : `CODEBASE EXTRACTION REPORT`
    - Nom du Projet
    - Chemin Absolu du Projet
    - Date et Heure de l'Extraction
    - Informations Système (OS, architecture)
2.  **Statistiques du Projet** :
    - Total dossiers
    - Total fichiers
    - Fichiers de code
3.  **Structure du Projet** :
    - Nom du dossier racine du projet
    - Arborescence des dossiers et des fichiers de code pertinents.
4.  **Contenu des Fichiers de Code** :
    - Pour chaque fichier de code extrait, le contenu sera présenté comme suit :
      ```
      ['chemin/relatif/vers/le/fichier.ext': [
      --------------------------------------------------
      Contenu du fichier ici...
      Peut être sur plusieurs lignes.
      --------------------------------------------------
      ]]
      ```
5.  **Pied de Page de l'Extraction** :
    - Indication de fin d'extraction.
    - Nombre total de fichiers extraits.
    - Date et heure de fin.

## 🏗️ Structure du Script

Le script `codebase_extractor.py` est organisé autour de la classe `CodebaseExtractor` :

-   `__init__()`: Initialise les informations système, les extensions supportées et les motifs d'ignorance.
-   `_detect_system()`: Détecte les informations du système d'exploitation.
-   `_is_ignored()`: Vérifie si un chemin ou un nom doit être ignoré.
-   `_is_code_file()`: Détermine si un fichier est un fichier de code pertinent.
-   `_safe_read_file()`: Lit le contenu d'un fichier en gérant les erreurs d'encodage et la taille.
-   `_create_tree_structure()`: Construit récursivement une représentation arborescente du projet.
-   `_format_tree_display()`: Formate l'arborescence pour l'affichage.
-   `extract_codebase()`: Méthode principale orchestrant l'ensemble du processus d'extraction.
    -   `extract_files_recursive()` (fonction imbriquée): Extrait récursivement le contenu des fichiers.
-   `main()`: Fonction globale gérant les arguments de la ligne de commande et l'exécution de l'extracteur.

## 🤝 Contribuer

Les contributions sont les bienvenues ! Si vous avez des suggestions d'amélioration, des corrections de bugs, ou de nouvelles fonctionnalités à proposer :

1.  **Forkez le projet** sur GitHub.
2.  **Créez une nouvelle branche** pour votre fonctionnalité (`git checkout -b feature/NomDeLaFeature`).
3.  **Faites vos modifications.**
4.  **Commitez vos changements** (`git commit -m 'Ajout de telle fonctionnalité'`).
5.  **Poussez vers la branche** (`git push origin feature/NomDeLaFeature`).
6.  **Ouvrez une Pull Request.**

Veuillez vous assurer que votre code respecte le style existant et inclut des commentaires pertinents si nécessaire.

*(Note de Jack-Josias : Vous pouvez adapter cette section selon vos préférences pour les contributions.)*

## 📜 Licence

Apache 2.0
