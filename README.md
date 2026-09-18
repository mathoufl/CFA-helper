# CFA Study Pipeline
 
Système personnel d'étude du CFA, conçu pour transformer les cours verbeux en synthèses denses et structurées, adaptées à un profil ingénieur.
 
## Principe
 
Le cours CFA est extrait depuis l'interface web (HTML) ou le PDF, prétraité par un script Python, puis passé page par page à Claude qui produit une synthèse au format "cours de maths" :
 
**Définition → Raisonnement → Proposition → Corollaires**
 
## Structure du repo
 
```
cfa-study-pipeline/
├── classes/
│   ├── raw/                    # HTML brut extrait, organisé par module
│   │   └── <nom-chapitre>/
│   └── parsed/                 # JSON prétraité prêt à passer à Claude
│       └── <nom-chapitre>/
├── source-pdf/                 # PDFs officiels CFA Level 1 2026
├── prompt/
│   └── system_prompt.txt       # Prompt de synthèse validé
├── scripts/
│   └── extract.py              # Extraction et prétraitement HTML → JSON
├── CLAUDE.md                   # Contexte projet pour Claude
├── TODO.md                     # État d'avancement
└── README.md
```
 
## Workflow
 
1. Ouvrir une session par cours dans Claude
2. Passer le prompt (`prompt/system_prompt.txt`) + les LOS du module en début de session
3. Extraire le HTML de chaque page via `scripts/extract.py`
4. Passer le JSON extrait page par page à Claude
5. Copier la synthèse dans `classes/parsed/<module>/`
 
## Stack
 
- Python 3 (extraction et prétraitement HTML)
- Claude (Anthropic) — modèle : claude-sonnet-4-6
- Format d'échange : JSON
