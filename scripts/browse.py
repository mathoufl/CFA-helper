"""
browse.py
---------
Ouvre un Chromium interactif avec session persistante.
Détecte automatiquement le module et la page depuis le titre de la page courante.
Lance extract.py après chaque extraction.

Usage :
    python browse.py --course <nom-cours>

Exemple :
    python browse.py --course corporate-issuers

Structure de sortie :
    classes/raw/<course>/<course>_module<N>_page<N>.html
    classes/parsed/<course>/<course>_module<N>_page<N>.json

Raccourcis terminal :
    Entrée        → extraire la page courante (module/page détectés automatiquement)
    q + Entrée    → quitter
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent  # scripts/ -> repo root
RAW_DIR = REPO_ROOT / "classes" / "raw"
PARSED_DIR = REPO_ROOT / "classes" / "parsed"
EXTRACT_SCRIPT = Path(__file__).parent / "extract.py"
USER_DATA_DIR = REPO_ROOT / ".chromium-profile"

# ---------------------------------------------------------------------------
# Détection automatique module/page depuis le DOM
# ---------------------------------------------------------------------------

def detect_coordinates(page_playwright) -> tuple[int, int] | None:
    """
    Lit le titre de la page dans le DOM et en extrait module et page.
    Le titre attendu est de la forme : "6.04 | Modigliani–Miller..."
    Retourne (module, page) ou None si la détection échoue.
    """
    try:
        # Cherche le h2 avec la classe dp-heading qui contient "X.YY | ..."
        title = page_playwright.locator("h2.dp-heading").first.inner_text(timeout=3000)
        # Extrait le pattern X.YY en début de titre
        match = re.search(r"(\d+)\.(\d+)", title)
        if match:
            module = int(match.group(1))
            page_num = int(match.group(2))
            return module, page_num
    except Exception:
        pass

    # Fallback : cherche dans le titre de l'onglet
    try:
        title = page_playwright.title()
        match = re.search(r"(\d+)\.(\d+)", title)
        if match:
            module = int(match.group(1))
            page_num = int(match.group(2))
            return module, page_num
    except Exception:
        pass

    return None

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_filename(course: str, module: int, page: int) -> str:
    return f"{course}_module{module}_page{page}"


def extract_page(page_playwright, course: str) -> bool:
    """
    Détecte les coordonnées, extrait le HTML de la page courante,
    le sauvegarde dans raw/ et lance extract.py vers parsed/.
    Retourne True si succès.
    """
    # Détection automatique
    coords = detect_coordinates(page_playwright)
    if coords is None:
        print("  ✗ Impossible de détecter le module/page depuis cette page.")
        print("    Assure-toi d'être sur une page de cours CFA.")
        return False

    module, page_num = coords
    filename = build_filename(course, module, page_num)
    print(f"  → Détecté : {filename}")

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

    # Sauvegarde HTML
    html = page_playwright.content()
    raw_path.write_text(html, encoding="utf-8")
    print(f"  ✓ HTML sauvegardé → {raw_path}")

    # Vérification JSON existant
    if parsed_path.exists():
        confirm = input(f"  ⚠ {parsed_path.name} existe déjà. Écraser ? (o/N) : ").strip().lower()
        if confirm != "o":
            print("  → Parsing ignoré, HTML sauvegardé uniquement.")
            return True

    # Lancement extract.py
    print("  → Parsing en cours...")
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="CFA page extractor — browser interactif")
    parser.add_argument("--course", required=True, help="Nom du cours (ex: corporate-issuers)")
    args = parser.parse_args()

    course = args.course

    print(f"""
╔══════════════════════════════════════════════╗
║         CFA Study Pipeline — Browser         ║
╠══════════════════════════════════════════════╣
║  Cours : {course:<36}║
╠══════════════════════════════════════════════╣
║  Entrée      → extraire la page courante     ║
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

        if not browser.pages:
            page = browser.new_page()
        else:
            page = browser.pages[0]

        print("  Chromium ouvert. Navigue vers la page voulue puis appuie sur Entrée.\n")

        try:
            while True:
                cmd = input("  > ").strip().lower()

                if cmd == "q":
                    print("  Au revoir.")
                    break
                else:
                    extract_page(page, course)
                    print()

        except KeyboardInterrupt:
            print("\n  Interruption clavier. Fermeture.")

        finally:
            browser.close()


if __name__ == "__main__":
    main()