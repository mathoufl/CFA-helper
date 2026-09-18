
"""
extract.py
----------
Extrait le contenu pédagogique d'une page HTML du cours CFA
et produit un JSON structuré prêt à être passé à Claude.
 
Usage :
    python extract.py <input.html> <output.json>
 
    ou en passant le HTML via stdin :
    cat page.html | python extract.py - output.json
"""
 
import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup
 
 
# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------
 
def clean_text(element) -> str:
    """Retourne le texte brut d'un élément BeautifulSoup, nettoyé."""
    if element is None:
        return ""
    # Supprimer les balises script/style internes
    for tag in element.find_all(["script", "style"]):
        tag.decompose()
    text = element.get_text(separator=" ", strip=True)
    # Normaliser les espaces multiples
    text = re.sub(r" +", " ", text)
    return text.strip()
 
 
def extract_mathml(formula_container) -> str:
    """Extrait le MathML brut depuis un conteneur de formule."""
    script = formula_container.find("script", {"type": "math/mml"})
    if script:
        return script.string.strip() if script.string else ""
    return ""
 
 
def get_formula_number(formula_container) -> int | None:
    """Extrait le numéro de formule depuis le span dédié."""
    span = formula_container.find("span", class_="cfa-curriculum-display-formula-number")
    if span:
        try:
            return int(span.get_text(strip=True))
        except ValueError:
            return None
    return None
 
 
# ---------------------------------------------------------------------------
# Extracteurs par type de bloc
# ---------------------------------------------------------------------------
 
def extract_formulas(container) -> list[dict]:
    """Extrait toutes les formules d'un conteneur."""
    formulas = []
    for fc in container.find_all("div", class_="cfa-curriculum-display-formula-container"):
        mathml = extract_mathml(fc)
        if not mathml:
            continue
        formula_id = fc.get("id", "")
        number = get_formula_number(fc)
        formulas.append({
            "id": formula_id,
            "number": number,
            "mathml": mathml
        })
    return formulas
 
 
def extract_exhibits(container) -> list[dict]:
    """Extrait les références aux graphiques/tableaux."""
    exhibits = []
    for fig in container.find_all("div", class_="cfa-curriculum-exhibit-figure"):
        exhibit_id = fig.get("id", "")
        # Titre
        title_tag = fig.find(["h3", "h4"], class_="cfa-curriculum-exhibit-figure-title")
        title = clean_text(title_tag) if title_tag else ""
        # Numéro depuis le titre (ex. "Exhibit 4")
        number = None
        match = re.search(r"Exhibit\s+(\d+)", title)
        if match:
            number = int(match.group(1))
            # Nettoyer le titre pour garder uniquement le sous-titre
            title = re.sub(r"Exhibit\s+\d+\s*", "", title).strip()
        # Description alt (extended description)
        desc_tag = fig.find("p", class_="dp-panel-outside-panel")
        description = clean_text(desc_tag) if desc_tag else ""
        # Fallback sur l'alt de l'image
        if not description:
            img = fig.find("img")
            if img:
                description = img.get("alt", "")
        exhibits.append({
            "id": exhibit_id,
            "number": number,
            "title": title,
            "description": description
        })
    return exhibits
 
 
def extract_summary_boxes(container) -> list[dict]:
    """Extrait les encadrés de synthèse (shaded boxes)."""
    boxes = []
    for box in container.find_all("div", class_="cfa-curriculum-shaded-box"):
        title_tag = box.find(class_="cfa-curriculum-box-title")
        title = clean_text(title_tag) if title_tag else ""
        # Retirer le titre du contenu
        if title_tag:
            title_tag.decompose()
        content = clean_text(box)
        boxes.append({
            "title": title,
            "content": content
        })
    return boxes
 
 
def extract_examples(container) -> list[dict]:
    """Extrait les blocs exemple."""
    examples = []
    for ex in container.find_all("div", class_="cfa-curriculum-example-box"):
        example_id = ex.get("id", "")
        title_tag = ex.find(class_="cfa-curriculum-box-title")
        title = clean_text(title_tag) if title_tag else ""
        if title_tag:
            title_tag.decompose()
        content = clean_text(ex)
        examples.append({
            "id": example_id,
            "title": title,
            "content": content
        })
    return examples
 
 
def extract_section_content(section) -> str:
    """
    Extrait le texte brut d'une section en excluant les blocs
    déjà traités séparément (formules, exhibits, boxes, exemples).
    """
    clone = BeautifulSoup(str(section), "html.parser")
    for cls in [
        "cfa-curriculum-display-formula-container",
        "cfa-curriculum-exhibit-figure",
        "cfa-curriculum-shaded-box",
        "cfa-curriculum-example-box",
        "dp-qc",                          # QCM exclus
        "cfa-curriculum-exercise-box",    # Question sets exclus
    ]:
        for tag in clone.find_all(class_=cls):
            tag.decompose()
    # Supprimer aussi les titres de section (h3/h4) déjà capturés
    for tag in clone.find_all(["h3", "h4"]):
        tag.decompose()
    return clean_text(clone)
 
 
# ---------------------------------------------------------------------------
# Extraction principale
# ---------------------------------------------------------------------------
 
def extract_sections(main_div) -> list[dict]:
    """
    Extrait récursivement les sections h3 et leurs sous-sections h4.
    """
    sections = []
 
    for section in main_div.find_all("section", recursive=False):
        section_id = section.get("id", "")
 
        # Titre h3
        h3 = section.find("h3", class_="dp-heading")
        title = clean_text(h3) if h3 else ""
 
        content = extract_section_content(section)
        formulas = extract_formulas(section)
        exhibits = extract_exhibits(section)
        summary_boxes = extract_summary_boxes(section)
        examples = extract_examples(section)
 
        # Sous-sections h4 (traitées comme sections imbriquées)
        subsections = []
        for subsection in section.find_all("section", recursive=False):
            sub_id = subsection.get("id", "")
            h4 = subsection.find("h4", class_="dp-heading")
            sub_title = clean_text(h4) if h4 else ""
            subsections.append({
                "id": sub_id,
                "title": sub_title,
                "level": 4,
                "content": extract_section_content(subsection),
                "formulas": extract_formulas(subsection),
                "exhibits": extract_exhibits(subsection),
                "summary_boxes": extract_summary_boxes(subsection),
                "examples": extract_examples(subsection),
                "subsections": []
            })
 
        sections.append({
            "id": section_id,
            "title": title,
            "level": 3,
            "content": content,
            "formulas": formulas,
            "exhibits": exhibits,
            "summary_boxes": summary_boxes,
            "examples": examples,
            "subsections": subsections
        })
 
    return sections
 
 
def extract_los(main_div) -> list[str]:
    """Extrait les Learning Outcome Statements."""
    los_box = main_div.find("div", class_="cfa-curriculum-los-box")
    if not los_box:
        return []
    return [
        clean_text(li)
        for li in los_box.find_all("li", class_="cfa-curriculum-los-item")
    ]
 
 
def extract_page_meta(main_div) -> dict:
    """Extrait les métadonnées de la page (id, titre, module)."""
    wrapper = main_div.find("div", class_="dp-wrapper")
    page_id = wrapper.get("id", "") if wrapper else ""
    title_tag = main_div.find("h2", class_="dp-heading")
    title = ""
    module = ""
    if title_tag:
        pre = title_tag.find("span", class_="dp-header-pre")
        if pre:
            module = clean_text(pre)
            pre.decompose()
        title = clean_text(title_tag)
    return {"id": page_id, "title": title, "module": module}
 
 
def extract(html: str) -> dict:
    """Point d'entrée principal : HTML -> dict structuré."""
    soup = BeautifulSoup(html, "html.parser")
    main_div = soup.find(attrs={"role": "main"})
    if not main_div:
        raise ValueError("Impossible de trouver la balise role='main' dans le HTML.")
 
    meta = extract_page_meta(main_div)
    los = extract_los(main_div)
    sections = extract_sections(main_div)
 
    return {
        "module": meta["module"],
        "page": {
            "id": meta["id"],
            "title": meta["title"],
            "los": los,
            "sections": sections
        }
    }
 
 
# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
 
def main():
    if len(sys.argv) < 3:
        print("Usage: python extract.py <input.html> <output.json>")
        print("       cat page.html | python extract.py - output.json")
        sys.exit(1)
 
    input_arg = sys.argv[1]
    output_path = Path(sys.argv[2])
 
    if input_arg == "-":
        html = sys.stdin.read()
    else:
        html = Path(input_arg).read_text(encoding="utf-8")
 
    result = extract(html)
 
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"✓ Extraction terminée → {output_path}")
 
 
if __name__ == "__main__":
    main()