"""
Parse MOD Pizza nutrition HTML and generate a CSV of menu items.
"""

import csv
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

# Paths
HTML_PATH = Path(__file__).parent.parent / "data" / "nutrition_pdfs" / "MOD.html"
CSV_PATH = Path(__file__).parent.parent / "data" / "mod_pizza_menu_items.csv"

# CSV header columns
CSV_HEADER = [
    "restaurant_slug", "name", "category", "serving_size", "calories",
    "protein", "carbs", "fat", "fiber", "sodium", "sugar", "saturated_fat",
    "is_vegetarian", "is_vegan", "is_gluten_free", "allergens", "tags",
    "source_url",
]

# Sections to parse and their category mapping
SECTIONS = {
    "collapsepizza1": "pizza",
    "collapsesalad1": "salad",
    "collapsemore-stuff1": "side",
    "collapsedesserts1": "dessert",
}

# Nutrition metric keywords used to identify value elements
METRIC_KEYWORDS = [
    "CALORIES", "FAT", "CHOLESTEROL", "SODIUM",
    "CARBOHYDRATE", "FIBER", "SUGARS", "PROTEIN", "TRANSFAT",
]


def clean_value(text):
    """Convert a nutrition value string to a numeric string. En-dash means 0."""
    text = text.strip()
    if text in ("\u2013", "-", ""):
        return ""
    # Some values have prefixes like "Bread: 1340" — extract the number
    match = re.search(r"([\d.]+)\s*$", text)
    if match:
        return match.group(1)
    return ""


def title_case_name(name):
    """Convert lowercase item names to title case, preserving parentheticals."""
    # Items like "cheesy garlic bread" → "Cheesy Garlic Bread"
    # Items like "dipping sauce - bbq sauce (per 3 tbsp)" → "Dipping Sauce - BBQ Sauce (Per 3 Tbsp)"
    # But preserve names that are already properly cased (e.g., "Caspian")
    words = name.split()
    result = []
    for word in words:
        if word.startswith("("):
            result.append("(" + word[1:].capitalize())
        elif word == "-":
            result.append("-")
        elif word.lower() in ("bbq", "pc"):
            result.append(word.upper())
        else:
            result.append(word.capitalize())
    return " ".join(result)


def parse_section(section_el, category):
    """Parse a section element and return a list of menu item dicts."""
    items = []
    aria_els = section_el.find_all(attrs={"aria-label": True})

    i = 0
    while i < len(aria_els):
        el = aria_els[i]
        label = el.get("aria-label", "").strip()
        text = el.get_text(strip=True)
        classes = el.get("class", [])

        is_metric = any(kw in label for kw in METRIC_KEYWORDS)

        if is_metric:
            # Skip stray metric elements
            i += 1
            continue

        is_title = "nutrition__title" in classes

        if is_title:
            # This is a named item with size variants (pizza, salad)
            item_name = text.strip()
            i += 1
            # Parse size variants
            while i < len(aria_els):
                el2 = aria_els[i]
                label2 = el2.get("aria-label", "").strip()
                text2 = el2.get_text(strip=True)
                classes2 = el2.get("class", [])
                is_metric2 = any(kw in label2 for kw in METRIC_KEYWORDS)
                is_title2 = "nutrition__title" in classes2

                if is_title2:
                    # Next item starts
                    break

                if is_metric2:
                    # Stray metric, skip
                    i += 1
                    continue

                # This is a size variant label (e.g., "Mini", "MOD", "Mega Dough")
                size_text = text2.strip()
                # Normalize size names
                size_display = size_text
                if size_text.lower() in ("mega dough", "mega"):
                    size_display = "Mega"
                elif size_text.lower() == "mod":
                    size_display = "MOD"
                elif size_text.lower() == "mini":
                    size_display = "Mini"
                elif size_text.lower() == "mini/side":
                    size_display = "Mini"

                full_name = f"{item_name} ({size_display})"
                i += 1

                # Now read 11 nutrition values
                nutrition = read_nutrition_values(aria_els, i)
                if nutrition:
                    items.append(build_row(full_name, category, nutrition))
                    i += 11
                else:
                    break

        else:
            # This is a standalone item (More Stuff, Desserts) — no size variants
            item_name = title_case_name(text.strip())
            i += 1

            # Read 11 nutrition values
            nutrition = read_nutrition_values(aria_els, i)
            if nutrition:
                items.append(build_row(item_name, category, nutrition))
                i += 11
            # else: skip

    return items


def read_nutrition_values(aria_els, start_idx):
    """Read 11 consecutive nutrition values starting at start_idx.

    Expected order:
        Calories, Calories from Fat, Total Fat, Saturated Fat, Trans Fat,
        Cholesterol, Sodium, Carbohydrate, Dietary Fiber, Sugars, Protein
    """
    if start_idx + 11 > len(aria_els):
        return None

    values = []
    for j in range(11):
        el = aria_els[start_idx + j]
        label = el.get("aria-label", "")
        if not any(kw in label for kw in METRIC_KEYWORDS):
            return None
        values.append(clean_value(el.get_text(strip=True)))

    return {
        "calories": values[0],
        "calories_from_fat": values[1],
        "total_fat": values[2],
        "saturated_fat": values[3],
        "trans_fat": values[4],
        "cholesterol": values[5],
        "sodium": values[6],
        "carbohydrate": values[7],
        "dietary_fiber": values[8],
        "sugars": values[9],
        "protein": values[10],
    }


def build_row(name, category, nutrition):
    """Build a CSV row dict from name, category, and nutrition values."""
    return {
        "restaurant_slug": "mod-pizza",
        "name": name,
        "category": category,
        "serving_size": "",
        "calories": nutrition["calories"],
        "protein": nutrition["protein"],
        "carbs": nutrition["carbohydrate"],
        "fat": nutrition["total_fat"],
        "fiber": nutrition["dietary_fiber"],
        "sodium": nutrition["sodium"],
        "sugar": nutrition["sugars"],
        "saturated_fat": nutrition["saturated_fat"],
        "is_vegetarian": "false",
        "is_vegan": "false",
        "is_gluten_free": "false",
        "allergens": "",
        "tags": "",
        "source_url": "",
    }


def main():
    if not HTML_PATH.exists():
        print(f"Error: HTML file not found at {HTML_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    all_items = []
    for section_id, category in SECTIONS.items():
        section_el = soup.find(id=section_id)
        if not section_el:
            print(f"Warning: section '{section_id}' not found", file=sys.stderr)
            continue
        items = parse_section(section_el, category)
        print(f"  {category}: {len(items)} items")
        all_items.extend(items)

    # Write CSV
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        writer.writerows(all_items)

    print(f"\nWrote {len(all_items)} items to {CSV_PATH}")


if __name__ == "__main__":
    main()
