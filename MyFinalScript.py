"""MyFinalScript.py

MOOC approval proposal PDF generator.

Reads mappings from `CSVV.csv` and produces a professional PDF report suitable for
submission to a faculty advisor.

For each mapping, the report contains (in order):
1) A front page with required course details (with emphasized fields)
2) The KTU syllabus PDF for the mapped KTU course (embedded directly; no text extraction)
3) The MOOC/NPTEL syllabus PDF from the `nptel/` folder (embedded directly)

IMPORTANT:
- This script only reads PDFs from these two folders:
  - `KTU SYLLABUS/`
  - `nptel/`
- It does NOT copy/paste PDF contents; it appends the PDF pages as-is.

Usage examples:
  python MyFinalScript.py
    python MyFinalScript.py --csv CSVV.csv --output "Final Output\\MOOC_Approval_Proposal.pdf"
  python MyFinalScript.py --mode individual
  python MyFinalScript.py --dry-run

Dependencies:
  pip install -r requirements.txt

"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


KTU_FOLDER_DEFAULT = "KTU SYLLABUS"
MOOC_FOLDER_DEFAULT = "nptel"
DEFAULT_CSV = "CSVV.csv"
DEFAULT_OUTPUT_DIR = "Final Output"


WEB_MAPPING_KEYWORDS = (
    "web programming",
    "web technology",
)


@dataclass(frozen=True)
class MappingRow:
    ktu_course_name: str
    course_category: str
    course_code: str
    mooc_course_name: str
    nptel_subject_id: str
    course_id: str
    course_url: str
    coordinators: str
    discipline: str
    offering_institute: str
    duration: str
    content_type: str
    platform: str


def _clean_cell(value: Optional[str]) -> str:
    if value is None:
        return ""
    # Normalize newlines and whitespace (CSV sometimes contains embedded newlines)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = value.strip()
    # Collapse excessive internal whitespace but keep newlines (later we convert to "; ")
    value = re.sub(r"[\t\f\v ]+", " ", value)
    return value


def _norm_for_match(text: str) -> str:
    text = _clean_cell(text).lower()
    # Replace separators with spaces
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _tokenize(text: str) -> List[str]:
    tokens = [t for t in _norm_for_match(text).split(" ") if len(t) >= 3]
    return tokens


def _best_pdf_match(
    pdf_paths: Sequence[str],
    query_primary: str,
    query_secondary: str = "",
) -> Optional[str]:
    """Return best-matching PDF path by token overlap scoring."""

    if not pdf_paths:
        return None

    primary_tokens = set(_tokenize(query_primary))
    secondary_tokens = set(_tokenize(query_secondary))

    # If nothing to score on, bail
    if not primary_tokens and not secondary_tokens:
        return pdf_paths[0]

    best: Tuple[int, int, int, str] | None = None
    # (score_primary, score_secondary, -len(filename), path)

    for path in pdf_paths:
        fname = os.path.basename(path)
        fname_tokens = set(_tokenize(fname))
        score_primary = len(primary_tokens & fname_tokens)
        score_secondary = len(secondary_tokens & fname_tokens)
        score_len = -len(fname)
        candidate = (score_primary, score_secondary, score_len, path)
        if best is None or candidate > best:
            best = candidate

    assert best is not None
    if best[0] == 0 and best[1] == 0:
        return None
    return best[3]


def _list_pdfs(folder: str) -> List[str]:
    if not os.path.isdir(folder):
        return []
    return [
        os.path.join(folder, name)
        for name in os.listdir(folder)
        if name.lower().endswith(".pdf")
    ]


def _find_ktu_pdf(ktu_folder: str, course_code: str, ktu_course_name: str) -> Optional[str]:
    code = _clean_cell(course_code)
    if not code:
        return None

    # Prefer files that start with the code
    all_pdfs = _list_pdfs(ktu_folder)
    startswith = [p for p in all_pdfs if os.path.basename(p).lower().startswith(code.lower())]
    if len(startswith) == 1:
        return startswith[0]
    if len(startswith) > 1:
        return _best_pdf_match(startswith, query_primary=ktu_course_name, query_secondary=code)

    # Fallback: anywhere contains code
    contains = [p for p in all_pdfs if code.lower() in os.path.basename(p).lower()]
    if len(contains) == 1:
        return contains[0]
    if len(contains) > 1:
        return _best_pdf_match(contains, query_primary=ktu_course_name, query_secondary=code)

    # Last resort: name match only
    return _best_pdf_match(all_pdfs, query_primary=ktu_course_name, query_secondary=code)


def _find_mooc_pdf(
    mooc_folder: str,
    mooc_course_name: str,
    nptel_subject_id: str,
    course_id: str,
    course_url: str,
) -> Optional[str]:
    all_pdfs = _list_pdfs(mooc_folder)

    subj = _clean_cell(nptel_subject_id)
    if subj:
        # Prefer PDFs containing exact subject id digits
        subj_digits = re.sub(r"\D+", "", subj)
        if subj_digits:
            candidates = [p for p in all_pdfs if subj_digits in os.path.basename(p)]
            if len(candidates) == 1:
                return candidates[0]
            if len(candidates) > 1:
                return _best_pdf_match(candidates, query_primary=mooc_course_name, query_secondary=subj_digits)

    # If URL includes a numeric id, try that
    url_digits = re.findall(r"\b\d{6,}\b", _clean_cell(course_url))
    for d in url_digits:
        candidates = [p for p in all_pdfs if d in os.path.basename(p)]
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            return _best_pdf_match(candidates, query_primary=mooc_course_name, query_secondary=d)

    # Otherwise best match on course name; consider course_id as weak secondary
    return _best_pdf_match(all_pdfs, query_primary=mooc_course_name, query_secondary=course_id)


def _read_csv_mappings(csv_path: str) -> List[MappingRow]:
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        expected = [
            "Course Name",
            "Course Category",
            "Course Code",
            "MOOC Course Name",
            "NPTEL Subject ID",
            "Course ID",
            "Course URL",
            "Coordinator(s)",
            "Discipline",
            "Offering Institute",
            "Duration",
            "Content Type",
            "Platform",
        ]
        missing = [c for c in expected if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(
                "CSV headers do not match expected columns. Missing: " + ", ".join(missing)
            )

        rows: List[MappingRow] = []
        for raw in reader:
            rows.append(
                MappingRow(
                    ktu_course_name=_clean_cell(raw.get("Course Name")),
                    course_category=_clean_cell(raw.get("Course Category")),
                    course_code=_clean_cell(raw.get("Course Code")),
                    mooc_course_name=_clean_cell(raw.get("MOOC Course Name")),
                    nptel_subject_id=_clean_cell(raw.get("NPTEL Subject ID")),
                    course_id=_clean_cell(raw.get("Course ID")),
                    course_url=_clean_cell(raw.get("Course URL")),
                    coordinators=_clean_cell(raw.get("Coordinator(s)")),
                    discipline=_clean_cell(raw.get("Discipline")),
                    offering_institute=_clean_cell(raw.get("Offering Institute")),
                    duration=_clean_cell(raw.get("Duration")),
                    content_type=_clean_cell(raw.get("Content Type")),
                    platform=_clean_cell(raw.get("Platform")),
                )
            )

    return rows


def _escape_para(text: str) -> str:
    # Minimal XML escaping for ReportLab Paragraph
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _format_multiline(text: str) -> str:
    text = _clean_cell(text)
    if not text:
        return ""
    # Convert embedded newlines to semicolon-separated values (cleaner on cover page)
    parts = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    return "; ".join(parts)


def _build_cover_page_pdf(row: MappingRow, ktu_pdf_name: str, mooc_pdf_name: str) -> bytes:
    buf = BytesIO()

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        spaceAfter=10,
    )
    normal = ParagraphStyle(
        "Normal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=normal,
        fontName="Helvetica-Bold",
    )

    def kv(label: str, value: str, emphasize_value: bool = False) -> Tuple[Paragraph, Paragraph]:
        safe_label = Paragraph(f"<b>{_escape_para(label)}</b>", label_style)
        safe_value = _escape_para(value) if value else "-"
        if emphasize_value and value:
            safe_value = f"<b>{safe_value}</b>"
        safe_value_p = Paragraph(safe_value, normal)
        return safe_label, safe_value_p

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title=f"MOOC Approval Proposal - {row.course_code}",
    )

    story: List[object] = []
    story.append(Paragraph("MOOC APPROVAL PROPOSAL", title))
    #story.append(Paragraph(f"Generated on: {_escape_para(datetime.now().strftime('%Y-%m-%d'))}", normal))
    story.append(Spacer(1, 10))

    # Required details
    data: List[Tuple[Paragraph, Paragraph]] = []
    data.append(kv("KTU Course Name", row.ktu_course_name))
    data.append(kv("Course Category", row.course_category))
    data.append(kv("Course Code", row.course_code, emphasize_value=True))
    data.append(kv("MOOC Course Name", row.mooc_course_name))

    if row.nptel_subject_id:
        data.append(kv("NPTEL Subject ID", row.nptel_subject_id))

    if row.course_id:
        data.append(kv("Course ID", row.course_id))

    if row.course_url:
        # Show URL as plain text (clickable linking is optional and can break in some PDF viewers)
        data.append(kv("Course URL", row.course_url))

    data.append(kv("COORDINATORS", _format_multiline(row.coordinators), emphasize_value=True))
    data.append(kv("Offering Institute", row.offering_institute, emphasize_value=True))
    data.append(kv("Duration", row.duration, emphasize_value=True))
    data.append(kv("Platform", row.platform))

    # Helpful attachment references (names only)
        # if ktu_pdf_name:
        #    data.append(kv("KTU Syllabus PDF (attached)", ktu_pdf_name))
        # if mooc_pdf_name:
        #    data.append(kv("MOOC/NPTEL Syllabus PDF (attached)", mooc_pdf_name))

    table = Table(
        data,
        colWidths=[5.0 * cm, 11.5 * cm],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white]),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 10))

    doc.build(story)
    return buf.getvalue()


def _build_document_cover_pdf(*, branch_text: str) -> bytes:
    buf = BytesIO()

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=32,
        alignment=1,
        spaceAfter=20,
    )
    sub = ParagraphStyle(
        "DocSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=14,
        leading=18,
        alignment=1,
        spaceAfter=10,
    )
    small = ParagraphStyle(
        "DocSmall",
        parent=sub,
        fontSize=12,
        leading=16,
        textColor=colors.grey,
        spaceAfter=0,
    )

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title="MOOC Courses",
    )

    story: List[object] = []
    story.append(Spacer(1, 8 * cm))
    story.append(Paragraph("MOOC Courses", title))
    story.append(Paragraph(_escape_para(branch_text), sub))
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph(f"Date: {_escape_para(datetime.now().strftime('%d %b %Y'))}", small))
    doc.build(story)
    return buf.getvalue()


def _build_index_pdf(entries: Sequence[Tuple[int, str, str, str, int]]) -> bytes:
    """Build an index page listing mappings and their start page in the combined PDF.

    entries: (sno, course_code, ktu_name, mooc_name, start_page)
    """
    buf = BytesIO()
    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "IndexTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        spaceAfter=10,
    )
    cell = ParagraphStyle(
        "IndexCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=12,
    )
    head = ParagraphStyle(
        "IndexHead",
        parent=cell,
        fontName="Helvetica-Bold",
    )

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.7 * cm,
        rightMargin=1.7 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Index",
    )

    story: List[object] = []
    story.append(Paragraph("INDEX", title))
    story.append(Spacer(1, 6))

    table_data: List[List[Paragraph]] = []
    table_data.append(
        [
            Paragraph("S.No", head),
            Paragraph("KTU Course", head),
            Paragraph("MOOC Course", head),
            Paragraph("Start Page", head),
        ]
    )

    for sno, code, ktu_name, mooc_name, start_page in entries:
        ktu_text = f"{_escape_para(code)} - {_escape_para(ktu_name)}" if code else _escape_para(ktu_name)
        table_data.append(
            [
                Paragraph(str(sno), cell),
                Paragraph(ktu_text or "-", cell),
                Paragraph(_escape_para(mooc_name) or "-", cell),
                Paragraph(str(start_page), cell),
            ]
        )

    table = Table(
        table_data,
        colWidths=[1.3 * cm, 7.2 * cm, 7.0 * cm, 2.0 * cm],
        hAlign="LEFT",
        repeatRows=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    story.append(table)
    doc.build(story)
    return buf.getvalue()


def _pdf_page_count_from_bytes(pdf_bytes: bytes) -> int:
    return len(PdfReader(BytesIO(pdf_bytes)).pages)


def _pdf_page_count_from_path(pdf_path: Optional[str]) -> int:
    if not pdf_path:
        return 0
    try:
        return len(PdfReader(pdf_path).pages)
    except Exception:
        return 0


def _is_web_mapping(row: MappingRow) -> bool:
    hay = f"{row.course_code} {row.ktu_course_name} {row.mooc_course_name}".lower()
    if any(k in hay for k in WEB_MAPPING_KEYWORDS):
        return True
    # Explicitly catch the known KTU code as well.
    if row.course_code.strip().upper() == "PECST742":
        return True
    return False


def _order_rows(rows: Sequence[MappingRow]) -> List[MappingRow]:
    """Preserve CSV order, but push Web Programming/Technology mapping to the end."""
    indexed = list(enumerate(rows))
    indexed.sort(key=lambda t: (1 if _is_web_mapping(t[1]) else 0, t[0]))
    return [r for _, r in indexed]


def _append_pdf(writer: PdfWriter, pdf_path: str) -> None:
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        writer.add_page(page)


def _is_row_incomplete(row: MappingRow) -> bool:
    # Consider row incomplete if it lacks MOOC identification AND URL.
    if not row.course_code:
        return True
    has_mooc_identity = bool(row.mooc_course_name or row.nptel_subject_id or row.course_id or row.course_url)
    return not has_mooc_identity


def generate_report(
    *,
    csv_path: str,
    ktu_folder: str,
    mooc_folder: str,
    output_path: str,
    mode: str,
    include_incomplete: bool,
    dry_run: bool,
) -> int:
    rows = _read_csv_mappings(csv_path)

    # Resolve to absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ktu_folder_abs = os.path.join(base_dir, ktu_folder)
    mooc_folder_abs = os.path.join(base_dir, mooc_folder)

    if not os.path.isdir(ktu_folder_abs):
        raise FileNotFoundError(f"KTU folder not found: {ktu_folder_abs}")
    if not os.path.isdir(mooc_folder_abs):
        raise FileNotFoundError(f"MOOC folder not found: {mooc_folder_abs}")

    output_path_abs = output_path
    if not os.path.isabs(output_path_abs):
        output_path_abs = os.path.join(base_dir, output_path_abs)

    os.makedirs(os.path.dirname(output_path_abs), exist_ok=True)

    usable_rows: List[MappingRow] = []
    skipped = 0
    for r in rows:
        if _is_row_incomplete(r) and not include_incomplete:
            skipped += 1
            continue
        usable_rows.append(r)

    # Ordering requirement: Web Technology/Web Programming mapping must be last.
    usable_rows = _order_rows(usable_rows)

    if not usable_rows:
        raise ValueError("No usable mappings found (CSV rows are empty/incomplete).")

    problems: List[str] = []

    def resolve_paths(r: MappingRow) -> Tuple[Optional[str], Optional[str]]:
        ktu_pdf = _find_ktu_pdf(ktu_folder_abs, r.course_code, r.ktu_course_name)
        mooc_pdf = _find_mooc_pdf(
            mooc_folder_abs,
            r.mooc_course_name,
            r.nptel_subject_id,
            r.course_id,
            r.course_url,
        )
        return ktu_pdf, mooc_pdf

    if mode == "combined":
        # Build combined: (1) document cover (2) index (3) per-mapping sections
        writer = PdfWriter()

        doc_cover_bytes = _build_document_cover_pdf(branch_text="Branch: CSE")
        doc_cover_pages = _pdf_page_count_from_bytes(doc_cover_bytes)

        # Resolve all paths once and compute section sizes (for index start pages)
        resolved: List[Tuple[MappingRow, Optional[str], Optional[str], int]] = []
        for idx, r in enumerate(usable_rows, start=1):
            ktu_pdf, mooc_pdf = resolve_paths(r)
            if not ktu_pdf:
                problems.append(f"[{idx}] KTU PDF not found for {r.course_code} - {r.ktu_course_name}")
            if not mooc_pdf:
                problems.append(
                    f"[{idx}] MOOC PDF not found for {r.course_code} -> {r.mooc_course_name or '(no mooc name)'}"
                )

            cover_bytes = _build_cover_page_pdf(
                r,
                ktu_pdf_name=os.path.basename(ktu_pdf) if ktu_pdf else "",
                mooc_pdf_name=os.path.basename(mooc_pdf) if mooc_pdf else "",
            )
            cover_pages = _pdf_page_count_from_bytes(cover_bytes)
            section_pages = cover_pages + _pdf_page_count_from_path(ktu_pdf) + _pdf_page_count_from_path(mooc_pdf)
            resolved.append((r, ktu_pdf, mooc_pdf, section_pages))

        # Build index with stable page numbers (iterate in case index spills to multiple pages)
        assumed_index_pages = 1
        index_bytes = b""
        for _ in range(3):
            start_page = doc_cover_pages + assumed_index_pages + 1
            entries: List[Tuple[int, str, str, str, int]] = []
            cursor = start_page
            for sno, (r, _ktu, _mooc, sec_pages) in enumerate(resolved, start=1):
                entries.append((sno, r.course_code, r.ktu_course_name, r.mooc_course_name, cursor))
                cursor += sec_pages

            index_bytes = _build_index_pdf(entries)
            actual_index_pages = _pdf_page_count_from_bytes(index_bytes)
            if actual_index_pages == assumed_index_pages:
                break
            assumed_index_pages = actual_index_pages

        # Assemble final combined PDF
        for page in PdfReader(BytesIO(doc_cover_bytes)).pages:
            writer.add_page(page)
        for page in PdfReader(BytesIO(index_bytes)).pages:
            writer.add_page(page)

        for r, ktu_pdf, mooc_pdf, _sec_pages in resolved:
            cover_bytes = _build_cover_page_pdf(
                r,
                ktu_pdf_name=os.path.basename(ktu_pdf) if ktu_pdf else "",
                mooc_pdf_name=os.path.basename(mooc_pdf) if mooc_pdf else "",
            )
            for page in PdfReader(BytesIO(cover_bytes)).pages:
                writer.add_page(page)
            if ktu_pdf:
                _append_pdf(writer, ktu_pdf)
            if mooc_pdf:
                _append_pdf(writer, mooc_pdf)

        if dry_run:
            print(f"DRY RUN: would write combined report to: {output_path_abs}")
        else:
            with open(output_path_abs, "wb") as f:
                writer.write(f)

    elif mode == "individual":
        # output_path is treated as output directory
        out_dir = output_path_abs
        os.makedirs(out_dir, exist_ok=True)

        for idx, r in enumerate(usable_rows, start=1):
            ktu_pdf, mooc_pdf = resolve_paths(r)
            if not ktu_pdf:
                problems.append(f"[{idx}] KTU PDF not found for {r.course_code} - {r.ktu_course_name}")
            if not mooc_pdf:
                problems.append(
                    f"[{idx}] MOOC PDF not found for {r.course_code} -> {r.mooc_course_name or '(no mooc name)'}"
                )

            writer = PdfWriter()
            cover_bytes = _build_cover_page_pdf(
                r,
                ktu_pdf_name=os.path.basename(ktu_pdf) if ktu_pdf else "",
                mooc_pdf_name=os.path.basename(mooc_pdf) if mooc_pdf else "",
            )
            cover_reader = PdfReader(BytesIO(cover_bytes))
            for page in cover_reader.pages:
                writer.add_page(page)

            if ktu_pdf:
                _append_pdf(writer, ktu_pdf)
            if mooc_pdf:
                _append_pdf(writer, mooc_pdf)

            safe_code = re.sub(r"[^A-Za-z0-9_-]+", "_", r.course_code.strip() or f"row_{idx}")
            per_path = os.path.join(out_dir, f"MOOC_{safe_code}_Approval_Proposal.pdf")

            if dry_run:
                print(f"DRY RUN: would write: {per_path}")
            else:
                with open(per_path, "wb") as f:
                    writer.write(f)

    else:
        raise ValueError("Invalid mode. Use 'combined' or 'individual'.")

    if skipped:
        print(f"Skipped {skipped} incomplete CSV rows (use --include-incomplete to include).")

    if problems:
        print("\nWarnings:")
        for p in problems:
            print(" - " + p)
        print("\nTip: check filenames inside 'KTU SYLLABUS' and 'nptel' for mismatches.")

    return 0 if not problems else 2


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate MOOC approval proposal PDF(s) from CSVV.csv")
    parser.add_argument("--csv", default=DEFAULT_CSV, help="CSV mapping file (default: CSVV.csv)")
    parser.add_argument("--ktu-folder", default=KTU_FOLDER_DEFAULT, help="KTU syllabus PDF folder")
    parser.add_argument("--mooc-folder", default=MOOC_FOLDER_DEFAULT, help="MOOC/NPTEL PDF folder")
    parser.add_argument(
        "--mode",
        choices=["combined", "individual"],
        default="combined",
        help="combined = one PDF with all mappings; individual = one PDF per mapping",
    )
    parser.add_argument(
        "--output",
        default="",
        help=(
            "Output path. For combined mode: a PDF filepath. For individual mode: an output directory. "
            "Default: 'Final Output/MOOC_Approval_Proposal_<YYYYMMDD>.pdf' (combined) or 'Final Output/' (individual)."
        ),
    )
    parser.add_argument("--include-incomplete", action="store_true", help="Include incomplete CSV rows")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print actions without writing PDFs")

    args = parser.parse_args(argv)

    if not args.output:
        if args.mode == "combined":
            stamp = datetime.now().strftime("%Y%m%d")
            args.output = os.path.join(DEFAULT_OUTPUT_DIR, f"MOOC_Approval_Proposal_{stamp}.pdf")
        else:
            args.output = DEFAULT_OUTPUT_DIR

    return generate_report(
        csv_path=args.csv,
        ktu_folder=args.ktu_folder,
        mooc_folder=args.mooc_folder,
        output_path=args.output,
        mode=args.mode,
        include_incomplete=args.include_incomplete,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
