# CFA Study Pipeline

Système personnel d'étude du CFA, conçu pour transformer les cours verbeux en synthèses denses et structurées, adaptées à un profil ingénieur.

## Principe

Le cours CFA est extrait depuis l'interface web (HTML), prétraité par un script Python, puis passé page par page à Claude qui produit une synthèse au format "cours de maths" :

**Définition → Raisonnement → Proposition → Corollaires**

## Structure du repo

```
cfa-study-pipeline/
├── classes/
│   ├── raw/                        # HTML brut extrait, organisé par cours
│   │   └── <nom-cours>/
│   │       └── <nom-cours>_module<N>_page<N>.html
│   └── parsed/                     # JSON prétraité prêt à passer à Claude
│       └── <nom-cours>/
│           └── <nom-cours>_module<N>_page<N>.json
├── source-pdf/                     # PDFs officiels CFA Level 1 2026
├── prompt/
│   └── system_prompt.txt           # Prompt de synthèse validé
├── scripts/
│   ├── browse.py                   # Browser interactif — extraction HTML + parsing
│   └── extract.py                  # Extraction et prétraitement HTML → JSON
├── .chromium-profile/              # Profil Chromium persistant (session login)
├── .venv/                          # Environnement virtuel Python (non versionné)
├── requirements.txt                # Dépendances Python
├── CLAUDE.md                       # Contexte projet pour Claude
├── TODO.md                         # État d'avancement
└── README.md
```

Les cours disponibles dans `classes/` :

```
alternative-investments      ethics
corporate-issuers            financial-statement-analysis
derivatives                  fixed-income
economics                    portfolio-management
equity-investments           quantitative-method
```

## Workflow

### 1. Installation

```bash
# Créer et activer le venv
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
# .venv\Scripts\activate       # Windows

# Installer les dépendances
pip install -r requirements.txt

# Installer les navigateurs Playwright
python -m playwright install chromium
```

### 2. Extraction des pages

```bash
# Ouvrir le browser interactif
python scripts/browse.py --course <nom-cours> --module <N> --page <N>

# Exemple :
python scripts/browse.py --course corporate-issuers --module 6 --page 4
```

Au premier lancement, Chromium s'ouvre sur une page vierge — navigue vers le cours et connecte-toi. La session est sauvegardée dans `.chromium-profile/` et persistera aux lancements suivants.

**Raccourcis dans le terminal :**

| Commande      | Action                                      |
|---------------|---------------------------------------------|
| `Entrée`      | Extraire la page courante (HTML + JSON)     |
| `m + Entrée`  | Modifier les coordonnées (cours/module/page)|
| `q + Entrée`  | Quitter                                     |

Le script sauvegarde automatiquement :
- Le HTML brut dans `classes/raw/<cours>/`
- Le JSON parsé dans `classes/parsed/<cours>/`

Et propose l'auto-incrément de page après chaque extraction.

### 3. Session de synthèse avec Claude

1. Ouvrir un nouveau chat Claude (1 chat = 1 cours)
2. Coller le contenu de `prompt/system_prompt.txt` en début de session
3. Passer les LOS du module en cours
4. Coller le contenu du JSON page par page

## Stack

- Python 3
- [Playwright](https://playwright.dev/python/) — browser automation
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — parsing HTML
- Claude Sonnet 4.6 — synthèse
- Format d'échange : JSON