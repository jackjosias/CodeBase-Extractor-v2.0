# CodeBase Extractor

**Créé et maintenu par Jack-Josias**

---

## Présentation

CodeBase Extractor est un script Python avancé pour extraire, analyser et préparer une codebase pour l'audit, la documentation, l'archivage, ou l'ingestion par une IA/LLM. Il fonctionne sur Windows, Linux et macOS, sans dépendance externe.

## Fonctionnalités principales

- **Extraction multi-dossiers** : combine plusieurs répertoires en un seul rapport.
- **Exclusion automatique** : ignore les fichiers/dossiers générés (node_modules, .venv, dist, etc.) et personnalisables.
- **Rapports multi-format** : TXT, JSON, Markdown, HTML (option `--format`).
- **Export ZIP** : archive tous les rapports et fichiers extraits (`--zip`).
- **Analyse de sécurité** : détecte les secrets/credentials (API keys, tokens, mots de passe) et avertit l'utilisateur avant export.
- **Découpage LLM** : découpe automatique des fichiers en chunks pour ingestion IA (`--chunk-size`).
- **Personnalisation avancée** : motifs d'exclusion, formats, chunk size, etc.

## Installation de Python et Dépendances

Ce script fonctionne avec **Python 3.6+** et n'a besoin d'aucune bibliothèque externe.

- **Windows** :
  - Télécharger depuis [python.org](https://python.org)
  - Ou via Microsoft Store
  - Ou via Chocolatey :
    ```powershell
    choco install python
    ```
- **macOS** :
  - Avec Homebrew :
    ```bash
    brew install python3
    ```
  - Ou télécharger depuis python.org
- **Linux (Ubuntu/Debian)** :
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip
    ```
- **Linux (CentOS/RHEL)** :
    ```bash
    sudo yum install python3 python3-pip
    # ou sur les versions récentes
    sudo dnf install python3 python3-pip
    ```

**Aucune commande pip n'est requise pour ce script !**

Vérifiez simplement votre version :
```bash
python --version
# ou
python3 --version
```

Si Python 3.6+ est installé, le script fonctionnera directement.

## Comportement détaillé

- Scan récursif de tous les dossiers et sous-dossiers.
- Ignore automatiquement les dossiers/fichiers inutiles (`node_modules`, `.git`, etc.).
- Extraction du contenu de tous les fichiers de code pertinents.
- Génération d'un rapport dans un ou plusieurs formats (TXT, JSON, Markdown, HTML).
- Export ZIP possible de tous les rapports et fichiers extraits.
- Analyse de sécurité : détection de secrets/credentials (API keys, mots de passe, etc.), confirmation utilisateur (sauf `--force`).
- Découpage automatique en chunks pour ingestion LLM (`--chunk-size`).
- Utilisation de chemins relatifs dans les rapports.
- Gestion automatique des erreurs d'encodage.

## Format de sortie

- **En-tête global** : infos système, date, chemins analysés.
- **Statistiques cumulées** : nombre de fichiers, dossiers, fichiers de code.
- **Arborescence combinée** : structure des dossiers/fichiers.
- **Contenu des fichiers de code** : tous les fichiers extraits sur une seule ligne, séparés par `&&`.
- **Rapports multi-format** : TXT, JSON, Markdown, HTML.
- **Rapport LLM (optionnel)** : fichiers découpés en chunks pour ingestion IA.

## Exemples de commandes et use cases

### Extraction simple
```bash
python codebase_extractor.py .
```

### Extraction multi-dossiers
```bash
python codebase_extractor.py dossier1 dossier2 dossier3 -o rapport.txt
```

### Extraction multi-format et ZIP
```bash
python codebase_extractor.py src/ lib/ --format txt,md,html --zip
```

### Extraction avec découpage LLM
```bash
python codebase_extractor.py projet/ --chunk-size 2000
```

### Forcer l'export malgré des secrets détectés
```bash
python codebase_extractor.py . --force
```

### Ajouter des motifs d'exclusion personnalisés
```bash
python codebase_extractor.py . --ignore-patterns '*.bak,*.old'
```

## Options CLI principales
- `--format txt,json,md,html` : formats de sortie (un ou plusieurs, séparés par des virgules)
- `--zip` : exporte tout dans une archive ZIP
- `--chunk-size N` : découpe les fichiers en morceaux de N caractères pour LLM
- `--ignore-patterns motif1,motif2` : motifs d'exclusion personnalisés
- `--force` : force l'export même si des secrets sont détectés
- `-o` ou `--output` : nom du fichier de sortie principal

## Sécurité & Bonnes pratiques
- Le script scanne les fichiers pour détecter des secrets (API keys, mots de passe, etc.).
- Si des secrets sont trouvés, l'utilisateur est averti et doit confirmer l'export (sauf `--force`).
- **Il est fortement recommandé de retirer ou d'anonymiser les secrets avant tout partage.**

## Limitations
- Fichiers >1Mo tronqués.
- Encodages exotiques non garantis.
- Découpage LLM basé sur le nombre de caractères (pas de tokens).

## Compatibilité
- Windows, Linux, macOS
- Python 3.6+
- Zéro dépendance externe

## 🤝 Contribuer

Les contributions sont les bienvenues ! Si vous avez des suggestions d'amélioration, des corrections de bugs, ou de nouvelles fonctionnalités à proposer :

1. Forkez le projet sur GitHub.
2. Créez une nouvelle branche pour votre fonctionnalité :
   ```bash
   git checkout -b feature/NomDeLaFeature
   ```
3. Faites vos modifications.
4. Commitez vos changements :
   ```bash
   git commit -m 'Ajout de telle fonctionnalité'
   ```
5. Poussez vers la branche :
   ```bash
   git push origin feature/NomDeLaFeature
   ```
6. Ouvrez une Pull Request.

Veuillez vous assurer que votre code respecte le style existant et inclut des commentaires pertinents si nécessaire.

*Note de Jack-Josias : Vous pouvez adapter cette section selon vos préférences pour les contributions.*

## Licence
Voir le fichier LICENSE

---

**© 2025 Jack-Josias – Tous droits réservés**

## Exemple de sortie générée

Voici un extrait typique du rapport généré :

```
================================================================================
CODEBASE EXTRACTION REPORT
================================================================================
Projet: MonProjet
Chemin: /chemin/vers/MonProjet
Date d'extraction: 2025-05-27 15:00:00
Système: windows 64bit

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
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── components/
│       ├── header.js
│       └── footer.js
├── backend/
│   ├── server.py
│   ├── models/
│   │   ├── user.py
│   │   └── product.py
│   └── utils/
│       └── helpers.py

================================================================================
CONTENU DES FICHIERS DE CODE
================================================================================

'app.py': [
--------------------------------------------------
print("Hello World!")
--------------------------------------------------] && 'frontend/index.html': [
--------------------------------------------------
<!DOCTYPE html>
<html>...</html>
--------------------------------------------------] && ...

================================================================================
FIN DE L'EXTRACTION
================================================================================
✅ 10 fichiers extraits avec succès
📅 Extraction terminée le 2025-05-27 15:00:00
```

Ce format est identique pour tous les formats de sortie (TXT, JSON, Markdown, HTML), avec des adaptations de style.
