
# KTU MOOC Approval Report Generator

## Quick Start

To generate MOOC approval reports, run:
```
python generate_mooc_reports.py
```

This will create individual PDF reports in the `MOOC_Reports` folder.

---

## Add New Mapping

To add a new KTU-NPTEL mapping, edit `generate_mooc_reports.py` and add an entry to the `MAPPINGS` list:

```python
{
    "ktu_code": "PECST745",           # KTU course code
    "ktu_name": "Computer Vision",     # KTU course name
    "ktu_source": "Computer Science and Engineering.pdf",  # Source PDF
    "ktu_pages": [329, 330, 331, 332], # 0-indexed page numbers
    "nptel_pdf": "108103174.pdf",      # NPTEL course PDF
    "nptel_name": "Computer Vision and Image Processing",
    "nptel_instructor": "Prof. M.K. Bhuyan",
    "nptel_institute": "IIT Guwahati",
    "nptel_duration": "12 Weeks",
    "nptel_id": "noc26-ee31"
}
```

Then run the generator again.

---

## Current Mappings (Jan-Apr 2026)

| KTU Code | KTU Course | NPTEL Course | Institution |
|----------|------------|--------------|-------------|
| PECST745 | Computer Vision | Computer Vision and Image Processing | IIT Guwahati |
| PECST747 | Blockchain and Cryptocurrencies | Blockchain and its Applications | IIT Kharagpur |
| PECST862 | Natural Language Processing | Natural Language Processing | IIT Kharagpur |
| PECST785 | Algorithms for Data Science | Data Science for Engineers | IIT Madras |
| HNCST509 | Object Oriented Design Using UML | OO System Development using UML | IIT Kharagpur |
| HNCST609 | Advanced Algorithms | Design and Analysis of Algorithms | CMI |
| HNCS709 | Advanced Cryptography | Cryptography and Network Security | IIT Kharagpur |
| OEMET722 | Robotics | Robotics and Control | IIT Roorkee |
| OEECT723 | Optimization Techniques | Optimization from Fundamentals | IIT Bombay |
| PEECT752 | Internet of Things | Introduction to Internet of Things | IIT Kharagpur |
| OEEET832 | PLC and Automation | Industrial Automation and Control | IIT Kharagpur |
| HMCET502 | Project Management | Project Management | IIT Roorkee |

---

## Output Files

After running the generator, you will find in `MOOC_Reports/`:

1. **Individual Reports** (one per mapping):
   - `MOOC_PECST745_Report.pdf`
   - `MOOC_PECST747_Report.pdf`
   - etc.

2. **Principal's Proposal**:
   - `MOOC_Principal_Proposal.pdf`

Each individual report contains:
- Cover Page
- Complete KTU Syllabus (3-4 pages)
- NPTEL Course Details
- Syllabus Comparison Table
- Recommendation/Signature Page

---

## Reference Documents

- `MOOC_CONTEXT.md` - Full guide on KTU MOOC regulations
- `B. Tech Regulations_ 2024.pdf` - Official KTU regulations (Section 17)
