# CLAUDE.md

## Contexte

Ce repo est un pipeline d'étude personnel pour le CFA Level 1.
Les cours sont extraits depuis l'interface web CFA et prétraités en JSON.
Claude Code est utilisé pour produire des synthèses structurées page par page.

## Structure utile pour les sessions de cours

```
classes/
├── raw/<cours>/          # HTML brut (non utilisé en session)
├── parsed/<cours>/       # JSON prétraité — source des synthèses
│   └── <cours>_module<N>_page<N>.json
└── processed/<cours>/    # Synthèses générées en Markdown
    └── <cours>_module<N>_page<N>.md
prompt/
└── system_prompt.txt     # Prompt de synthèse
```

Cours disponibles dans `classes/parsed/` :
- alternative-investments
- corporate-issuers
- derivatives
- economics
- equity-investments
- ethics
- financial-statement-analysis
- fixed-income
- portfolio-management
- quantitative-method

## Protocole de session

### Démarrage
1. L'utilisateur passe le contenu de `prompt/system_prompt.txt`
2. Claude confirme et attend les informations du module
3. L'utilisateur passe : cours, numéro de module, et LOS
4. Claude confirme et attend la première page

### Navigation
- L'utilisateur demande une page : "page 4" ou "module 6 page 4"
- Claude lit le fichier JSON correspondant dans `classes/parsed/<cours>/`
- Claude produit la synthèse selon le format défini dans le system_prompt

### Conventions de nommage des fichiers
`<cours>_module<N>_page<N>.json`
Exemple : `corporate-issuers_module6_page4.json`

### Warnings à émettre
- Fichier JSON introuvable → signaler et demander confirmation avant de continuer
- LOS non fournis pour le module en cours → rappeler à l'utilisateur
- Fichier .md déjà existant dans processed/ → demander confirmation avant d'écraser