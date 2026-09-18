"""
browse.py
---------
Ouvre un Chromium interactif avec session persistante.
Permet d'extraire le HTML de la page courante et de lancer extract.py
en appuyant sur Entrée dans le terminal.

Usage :
    python browse.py --course <nom-cours> --module <num> --page <num>

Exemple :
    python browse.py --course corporate-issuers --module 6 --page 4

Structure de sortie (relative au repo, définie dans config) :
    classes/raw/<course>/corporate-issuers_module6_page4.html
    classes/parsed/<course>/corporate-issuers_module6_page4.json

Raccourcis terminal :
    Entrée        → extraire la page courante
    q + Entrée    → quitter
"""

import argparse
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# ---------------------------------------------------------------------------
# Configuration — adapter au chemin racine du repo
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent  # scripts/ -> repo root
RAW_DIR = REPO_ROOT / "classes" / "raw"
PARSED_DIR = REPO_ROOT / "classes" / "parsed"
EXTRACT_SCRIPT = Path(__file__).parent / "extract.py"

# Profil Chromium persistant (conserve la session de login)
USER_DATA_DIR = REPO_ROOT / ".chromium-profile"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_filename(course: str, module: int, page: int) -> str:
    return f"{course}_module{module}_page{page}"


def extract_page(page_playwright, course: str, module: int, page_num: int) -> bool:
    """
    Extrait le HTML de la page Playwright courante,
    le sauvegarde dans raw/ et lance extract.py vers parsed/.
    Retourne True si succès.
    """
    filename = build_filename(course, module, page_num)

    raw_course_dir = RAW_DIR / course
    parsed_course_dir = PARSED_DIR / course
    raw_course_dir.mkdir(parents=True, exist_ok=True)
    parsed_course_dir.mkdir(parents=True, exist_ok=True)

    raw_path = raw_course_dir / f"{filename}.html"
    parsed_path = parsed_course_dir / f"{filename}.json"

    # Vérification fichier existant
    if raw_path.exists():
        confirm = input(f"  ⚠ {raw_path.name} existe déjà. Écraser ? (o/N) : ").strip().lower()
        if confirm != "o":
            print("  → Extraction annulée.")
            return False

    # Récupération du HTML
    html = page_playwright.content()
    raw_path.write_text(html, encoding="utf-8")
    print(f"  ✓ HTML sauvegardé → {raw_path}")

    # Lancement de extract.py
    if parsed_path.exists():
        confirm = input(f"  ⚠ {parsed_path.name} existe déjà. Écraser ? (o/N) : ").strip().lower()
        if confirm != "o":
            print("  → Parsing ignoré, HTML sauvegardé uniquement.")
            return True

    print(f"  → Parsing en cours...")
    result = subprocess.run(
        [sys.executable, str(EXTRACT_SCRIPT), str(raw_path), str(parsed_path)],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"  ✓ JSON sauvegardé → {parsed_path}")
        return True
    else:
        print(f"  ✗ Erreur extract.py :\n{result.stderr}")
        return False


def prompt_coordinates(course: str, module: int, page: int):
    """
    Permet de modifier course/module/page avant chaque extraction.
    Appuyer sur Entrée conserve la valeur actuelle.
    """
    print(f"\n  Coordonnées actuelles : {build_filename(course, module, page)}")
    new_course = input(f"  Course [{course}] : ").strip() or course
    try:
        new_module = int(input(f"  Module [{module}] : ").strip() or module)
    except ValueError:
        new_module = module
    try:
        new_page = int(input(f"  Page [{page}] : ").strip() or page)
    except ValueError:
        new_page = page
    return new_course, new_module, new_page


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="CFA page extractor — browser interactif")
    parser.add_argument("--course", required=True, help="Nom du cours (ex: corporate-issuers)")
    parser.add_argument("--module", required=True, type=int, help="Numéro du module (ex: 6)")
    parser.add_argument("--page", required=True, type=int, help="Numéro de page (ex: 4)")
    args = parser.parse_args()

    course = args.course
    module = args.module
    page_num = args.page

    print(f"""
╔══════════════════════════════════════════════╗
║         CFA Study Pipeline — Browser         ║
╠══════════════════════════════════════════════╣
║  Entrée      → extraire la page courante     ║
║  m + Entrée  → modifier les coordonnées      ║
║  q + Entrée  → quitter                       ║
╚══════════════════════════════════════════════╝
""")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            args=["--start-maximized"],
            no_viewport=True
        )

        # Ouvrir un onglet si le contexte est vide
        if not browser.pages:
            page = browser.new_page()
        else:
            page = browser.pages[0]

        print(f"  Chromium ouvert. Navigue vers la page voulue puis appuie sur Entrée.\n")
        print(f"  Cible initiale : {build_filename(course, module, page_num)}\n")

        try:
            while True:
                cmd = input("  > ").strip().lower()

                if cmd == "q":
                    print("  Au revoir.")
                    break

                elif cmd == "m":
                    course, module, page_num = prompt_coordinates(course, module, page_num)
                    print(f"  Cible mise à jour : {build_filename(course, module, page_num)}")

                else:
                    # Entrée ou toute autre touche → extraction
                    extract_page(page, course, module, page_num)
                    # Auto-incrément de la page
                    auto = input(f"\n  Passer à la page {page_num + 1} ? (O/n) : ").strip().lower()
                    if auto != "n":
                        page_num += 1
                    print(f"  Cible suivante : {build_filename(course, module, page_num)}\n")

        except KeyboardInterrupt:
            print("\n  Interruption clavier. Fermeture.")

        finally:
            browser.close()


if __name__ == "__main__":
    main()