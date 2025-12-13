"""Generate a compact MOOC mappings summary (CSV + PDF).

Outputs (into Final Output/):
- MOOC_Mappings_List.csv
- MOOC_Mappings_List.pdf

Columns:
- KTU Course Category
- Semester
- KTU Course Name
- KTU Course Code
- NPTEL Course Name
- Offering Institute
"""

import csv
import os
from typing import List

import fitz  # PyMuPDF

from generate_final_reports import MAPPINGS, SEMESTER, OUTPUT_FOLDER, get_file_path


HEADERS: List[str] = [
    "KTU Course Category",
    "KTU Course Name",
    "KTU Course Code",
    "NPTEL Course Name",
    "Offering Institute",
]


def ensure_output_dir() -> str:
    """Ensure the Final Output directory exists and return its absolute path."""
    output_dir = get_file_path(OUTPUT_FOLDER)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def generate_csv(output_dir: str) -> str:
    """Generate a CSV summary suitable for opening in Excel."""
    csv_path = os.path.join(output_dir, "MOOC_Mappings_List.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)

        for mapping in MAPPINGS:
            row = [
                mapping.get("category", ""),
                mapping.get("ktu_name", ""),
                mapping.get("ktu_code", ""),
                mapping.get("nptel_name", ""),
                mapping.get("nptel_institute", ""),
            ]
            writer.writerow(row)

    return csv_path


def generate_pdf(output_dir: str) -> str:
    """Generate a one–two page PDF summary table of all mappings."""
    pdf_path = os.path.join(output_dir, "MOOC_Mappings_List.pdf")

    doc = fitz.open()

    # Basic layout
    page_width, page_height = 595, 842  # A4 in points
    left_margin = 40
    top_margin = 60
    row_height = 18

    def new_page() -> "fitz.Page":
        page = doc.new_page(width=page_width, height=page_height)
        # Title
        title = "KTU – NPTEL MOOC Mappings"
        page.insert_text(
            fitz.Point(left_margin, 40),
            title,
            fontsize=12,
            fontname="helv",
        )
        # Header row background
        header_y = top_margin
        col_x = [
            left_margin,       # Category
            left_margin + 80,  # KTU Code
            left_margin + 150, # KTU Name
            left_margin + 330, # NPTEL Name
            left_margin + 500, # Institute
        ]

        # Draw header labels
        headers = [
            "Category",
            "KTU Code",
            "KTU Course Name",
            "NPTEL Course Name",
            "Institute",
        ]
        for x, text in zip(col_x, headers):
            page.insert_text(
                fitz.Point(x, header_y),
                text,
                fontsize=8,
                fontname="helv",
            )

        # Horizontal line under header
        page.draw_line(
            fitz.Point(left_margin, header_y + 3),
            fitz.Point(page_width - left_margin, header_y + 3),
            width=0.5,
        )

        return page

    page = new_page()
    y = top_margin + row_height

    for mapping in MAPPINGS:
        if y > page_height - 40:
            page = new_page()
            y = top_margin + row_height

        category = str(mapping.get("category", ""))
        ktu_code = str(mapping.get("ktu_code", ""))
        ktu_name = str(mapping.get("ktu_name", ""))
        nptel_name = str(mapping.get("nptel_name", ""))
        institute = str(mapping.get("nptel_institute", ""))

        # Column x-positions must match header
        col_x = [
            left_margin,       # Category
            left_margin + 80,  # KTU Code
            left_margin + 150, # KTU Name
            left_margin + 330, # NPTEL Name
            left_margin + 500, # Institute
        ]

        values = [
            category,
            ktu_code,
            ktu_name,
            nptel_name,
            institute,
        ]

        # Slightly smaller font to fit in 1–2 pages
        for x, text in zip(col_x, values):
            page.insert_text(
                fitz.Point(x, y),
                text[:40],  # simple truncation to keep things narrow
                fontsize=7,
                fontname="helv",
            )

        y += row_height

    doc.save(pdf_path)
    doc.close()

    return pdf_path


def main() -> None:
    output_dir = ensure_output_dir()
    csv_path = generate_csv(output_dir)
    pdf_path = generate_pdf(output_dir)

    print(f"MOOC mappings CSV generated at: {csv_path}")
    print(f"MOOC mappings PDF generated at: {pdf_path}")


if __name__ == "__main__":
    main()
