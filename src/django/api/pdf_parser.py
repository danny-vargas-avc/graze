"""Parse nutrition PDFs using pdfplumber for text extraction and Claude API for structured data."""
import json
import pdfplumber
import anthropic


def extract_pdf_text(pdf_file):
    """Extract all text from a PDF file."""
    text_parts = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

            # Also extract tables if present
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row:
                        text_parts.append('\t'.join(str(cell or '') for cell in row))

    return '\n'.join(text_parts)


def parse_with_claude(text, api_key):
    """Send extracted PDF text to Claude for structured nutrition parsing."""
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        messages=[{
            "role": "user",
            "content": f"""Parse this restaurant nutrition information into structured JSON.

You must classify each item as either a "menu_item" or a "byo_component":

- **menu_item**: A complete dish you'd order (e.g. "Chicken Burrito Bowl", "Caesar Salad", "Lemonade")
- **byo_component**: An individual ingredient for a build-your-own meal (e.g. "White Rice", "Chicken", "Sour Cream", "Guacamole"). These are typically listed per-ingredient with small serving sizes, grouped under categories like Base, Protein, Toppings, Dressings/Sauces.

Return a JSON object with two arrays:

{{
  "menu_items": [
    {{
      "name": "string (required)",
      "category": "string (e.g. Entrees, Sides, Beverages)",
      "serving_size": "string (e.g. 1 bowl, 12 oz)",
      "calories": "integer (required)",
      "protein": "number in grams (required)",
      "carbs": "number in grams (required)",
      "fat": "number in grams (required)",
      "fiber": "number in grams or null",
      "sodium": "integer in mg or null",
      "sugar": "number in grams or null",
      "saturated_fat": "number in grams or null"
    }}
  ],
  "byo_components": [
    {{
      "name": "string (required)",
      "category": "string: one of base, protein, topping, dressing, extra (required)",
      "calories": "integer (required)",
      "protein": "number in grams (required)",
      "carbs": "number in grams (required)",
      "fat": "number in grams (required)",
      "fiber": "number in grams or null",
      "sodium": "integer in mg or null",
      "sugar": "number in grams or null",
      "saturated_fat": "number in grams or null"
    }}
  ]
}}

For byo_components category, map to one of: base, protein, topping, dressing, extra.
If the PDF has no BYO ingredients, return an empty byo_components array.

Return ONLY the JSON object. No markdown, no explanation.

Nutrition data:
{text}"""
        }]
    )

    response_text = message.content[0].text.strip()

    # Handle potential markdown code blocks in response
    if response_text.startswith('```'):
        lines = response_text.split('\n')
        response_text = '\n'.join(lines[1:-1])

    return json.loads(response_text)


def parse_nutrition_pdf(pdf_file, api_key):
    """Full pipeline: extract text from PDF, parse with Claude.

    Returns dict with 'menu_items' and 'byo_components' arrays.
    """
    text = extract_pdf_text(pdf_file)
    if not text.strip():
        raise ValueError("No text could be extracted from the PDF.")
    return parse_with_claude(text, api_key)
