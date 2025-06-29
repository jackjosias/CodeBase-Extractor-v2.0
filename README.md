
# CodeBase Extractor v3.0

**Créé et maintenu par Jack-Josias**

## Présentation

**CodeBase Extractor v3.0** est un agent Python intelligent et ultra-performant, conçu pour extraire, analyser et préparer une codebase pour l'audit, la documentation, l'archivage ou l'ingestion par une IA/LLM.

Doté d'une **intelligence contextuelle** et d'un **moteur d'extraction parallèle**, il s'adapte automatiquement à vos projets et traite les codebases volumineux à une vitesse exceptionnelle. Il fonctionne sur Windows, Linux et macOS, sans aucune dépendance externe.

## Fonctionnalités principales

*   **[NOUVEAU] Intelligence `.gitignore` :** Lit et applique automatiquement les règles du fichier `.gitignore` trouvé à la racine de votre projet. L'outil s'adapte à vos exclusions spécifiques sans aucune configuration manuelle.
*   **[AMÉLIORÉ] Extraction Parallèle Haute Performance :** Utilise tous les cœurs de votre processeur pour lire les fichiers en parallèle, réduisant drastiquement le temps d'extraction sur les projets volumineux.
*   **[AMÉLIORÉ] Robustesse des Chemins :** Gestion intelligente des chemins d'entrée multiples, même s'ils sont imbriqués ou redondants, garantissant une arborescence unique et correcte.
*   **[ÉTENDU] Support Technologique :** Prise en charge native des moteurs de template modernes comme **Twig (`.twig`)**, Jinja2, Blade, etc., en plus d'une vaste liste de langages et de formats de configuration.
*   **Rapports Multi-format :** Génération de rapports clairs et exploitables en **TXT, JSON, Markdown, et HTML** (option `--format`).
*   **Export ZIP :** Archive tous les rapports et les fichiers de code extraits dans un unique fichier `.zip` portable (`--zip`).
*   **Analyse de Sécurité Intégrée :** Détecte les secrets/credentials potentiels (API keys, tokens, mots de passe) et avertit l'utilisateur avant l'export pour prévenir les fuites d'informations sensibles.
*   **Découpage pour LLM :** Découpe automatiquement les fichiers en "chunks" de taille configurable, prêts à être ingérés par des modèles de langage (`--chunk-size`).

## Installation

Ce script fonctionne avec **Python 3.6+** et n'a besoin d'aucune bibliothèque externe.

1.  **Vérifiez votre version de Python :**
    ```bash
    python --version
    # ou sur certains systèmes
    python3 --version
    ```
2.  **Si Python n'est pas installé ou est une version antérieure à 3.6 :**
    *   **Windows :** Télécharger depuis [python.org](https://python.org) ou via le Microsoft Store.
    *   **macOS :** Utiliser Homebrew (`brew install python3`) ou télécharger depuis [python.org](https://python.org).
    *   **Linux (Ubuntu/Debian) :** `sudo apt update && sudo apt install python3`
    *   **Linux (CentOS/RHEL) :** `sudo dnf install python3`

**Aucune commande `pip install` n'est requise !**

## Comportement détaillé

1.  **Normalisation des entrées :** Le script analyse les chemins fournis et ne conserve que les répertoires parents uniques pour éviter tout traitement redondant.
2.  **Lecture du `.gitignore` :** Pour chaque répertoire parent, le script recherche un fichier `.gitignore` et charge dynamiquement ses règles d'exclusion.
3.  **Analyse de l'arborescence :** Parcours récursif de tous les dossiers et sous-dossiers, en respectant les règles d'exclusion de base ET celles du `.gitignore`.
4.  **Collecte et Extraction Parallèle :** La liste de tous les fichiers pertinents est établie, puis leur contenu est lu en parallèle pour une vitesse maximale.
5.  **Génération des Rapports :** Les données collectées sont ensuite formatées dans un ou plusieurs formats de sortie (TXT, JSON, Markdown, HTML).
6.  **Analyse de Sécurité :** Avant de finaliser, le contenu extrait est scanné pour des secrets potentiels. Si des secrets sont trouvés, une confirmation est demandée à l'utilisateur (sauf si l'option `--force` est utilisée).

## Exemples de commandes et use cases

*   **Extraction simple du répertoire courant vers un fichier par défaut :**
    ```bash
    python3 codebase_extractor.py .
    ```
*   **Extraction d'un dossier spécifique avec un nom de sortie personnalisé :**
    ```bash
    python3 codebase_extractor.py '/chemin/vers/mon/projet' -o rapport_projet.txt
    ```
*   **Extraction de plusieurs dossiers en un seul rapport :**
    ```bash
    python3 codebase_extractor.py ./backend ./frontend ./docs -o rapport_complet
    ```
*   **Génération de plusieurs formats et archivage ZIP :**
    ```bash
    python3 codebase_extractor.py /path/to/project --format txt,md,json --zip
    ```
*   **Extraction avec découpage pour un LLM (chunks de 4000 caractères) :**
    ```bash
    python3 codebase_extractor.py . --chunk-size 4000
    ```
*   **Forcer l'export même si des secrets sont détectés :**
    ```bash
    python3 codebase_extractor.py . --force
    ```
*   **Ajouter des motifs d'exclusion personnalisés en plus du .gitignore :**
    ```bash
    python3 codebase_extractor.py . --ignore-patterns "*.bak,*.old,temp_data/"
    ```

## Exemple de sortie générée (Format TXT)

Voici un extrait typique du rapport généré, dont le format est préservé à travers les mises à jour.

```
================================================================================
CODEBASE EXTRACTION REPORT
================================================================================
Projet: MonProjet
Chemin: /chemin/vers/MonProjet
Date d'extraction: 2025-07-01 10:30:00
Système: linux 64bit

STATISTIQUES DU PROJET:
------------------------------
📁 Total dossiers: 7
📄 Total fichiers: 12
💻 Fichiers de code: 10

STRUCTURE DU PROJET:
------------------------------
MonProjet/
├── app.py
├── config.json
├── README.md
├── .gitignore
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── components/
│       ├── header.js
│       └── footer.js
└── backend/
    ├── server.py
    └── models/
        ├── user.py
        └── product.py

================================================================================
CONTENU DES FICHIERS DE CODE
================================================================================

'app.py': [
--------------------------------------------------
print("Hello World from Main App!")
--------------------------------------------------
] && 'config.json': [
--------------------------------------------------
{
  "database": "prod_db"
}
--------------------------------------------------
] && ... (autres fichiers) ...

================================================================================
FIN DE L'EXTRACTION
================================================================================
✅ 10 fichiers extraits avec succès
📅 Extraction terminée le 2025-07-01 10:30:00
```

## Options CLI principales

| Option                  | Alias | Description                                                                   |
| ----------------------- | ----- | ----------------------------------------------------------------------------- |
| `--output <nom>`        | `-o`  | Nom du fichier de sortie principal (sans extension).                          |
| `--format <formats>`    |       | Formats de sortie : `txt,json,md,html` (un ou plusieurs, séparés par virgule). |
| `--zip`                 |       | Exporte tous les rapports générés dans une archive ZIP.                       |
| `--chunk-size <N>`      |       | Découpe les fichiers en morceaux de N caractères pour ingestion par un LLM.   |
| `--ignore-patterns <p>` |       | Ajoute des motifs d'exclusion personnalisés (séparés par virgule).            |
| `--force`               |       | Force l'export même si des secrets potentiels sont détectés.                  |

## Sécurité & Bonnes pratiques

Le script scanne les fichiers pour détecter des secrets (API keys, mots de passe, etc.). Si des secrets sont trouvés, **l'utilisateur est averti et doit confirmer l'export** (sauf si `--force` est utilisé).

Il est **fortement recommandé** de retirer ou d'anonymiser les secrets avant de partager tout rapport généré.

## Limitations

*   Les fichiers de plus de 1Mo sont tronqués pour préserver la mémoire.
*   La lecture du `.gitignore` est robuste pour la majorité des cas, mais pourrait ne pas interpréter certaines règles négatives complexes (`!pattern`) de la même manière que l'implémentation native de Git.
*   Le découpage pour LLM est basé sur le nombre de caractères, pas sur une tokenisation sémantique.

## Compatibilité

*   **Systèmes d'exploitation :** Windows, macOS, Linux
*   **Version de Python :** 3.6+
*   **Dépendances :** Aucune

## 🤝 Contribuer

Les contributions sont les bienvenues ! Si vous avez des suggestions d'amélioration, des corrections de bugs, ou de nouvelles fonctionnalités à proposer :

1.  Forkez le projet.
2.  Créez une nouvelle branche (`git checkout -b feature/NomDeLaFeature`).
3.  Faites vos modifications.
4.  Commitez vos changements (`git commit -m 'Ajout de telle fonctionnalité'`).
5.  Poussez vers la branche (`git push origin feature/NomDeLaFeature`).
6.  Ouvrez une Pull Request.

---
© 2025 Jack-Josias – Tous droits réservés
