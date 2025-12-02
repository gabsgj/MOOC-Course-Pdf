# KTU MOOC Approval Document Generation Guide

## Purpose
This guide helps generate official MOOC (Massive Open Online Course) approval documents for KTU (APJ Abdul Kalam Technological University) students seeking to complete NPTEL courses as part of their Honours/Minor/Major programme.

---

## KTU MOOC Regulations (From B.Tech Regulations 2024)

### Key Rules:
1. **R 17.1**: MOOC must be from approved agencies: AICTE, NPTEL, SWAYAM, NITTTR, or university-approved agencies
2. **R 17.2**: Minimum duration of **8 weeks**
3. **R 17.3**: Must be online mode with **proctored/offline End Semester examination**
4. **R 17.4**: At least **70% of course content must match** the Honours/Minor/Major course
5. **R 17.5**: College must submit proposals **one month before semester commencement**
6. **R 17.6**: No more than 30% overlap with other Major/Minor/Honours courses

### What the Principal Must Submit (R 17.5):
1. **MOOC Agency Details** - Name, platform, conducting institution
2. **Course Duration** - Number of weeks
3. **Benefits of the MOOC** - Why this course is beneficial
4. **Syllabus Comparison Report** - Comparing KTU course syllabus with NPTEL course, showing % similarity
5. **IQAC and College Council Recommendations**

---

## Document Structure for Each Mapping

### Individual Mapping Report (One PDF per mapping)

**Page 1: Cover Sheet**
```
MOOC APPROVAL REQUEST
=====================
KTU Course: [CODE] - [NAME]
NPTEL Course: [NAME]
Instructor: [NAME], [INSTITUTION]
Duration: [X] Weeks
Semester: Jan-Apr 2026
```

**Pages 2-5: KTU Course Syllabus (Complete)**
- Full syllabus pages extracted from KTU curriculum
- Includes: Code, Name, Credits, L-T-P-R, Objectives, Modules 1-5, Textbooks, References

**Pages 6-7: NPTEL Course Details**
- NPTEL course PDF content
- Instructor bio, course outline, week-wise plan

**Page 8: Syllabus Comparison Table**
| KTU Module | Topic | NPTEL Week | Topic | Match |
|------------|-------|------------|-------|-------|
| 1 | ... | 1-2 | ... | ✓ |
| 2 | ... | 3-4 | ... | ✓ |

**Page 9: Similarity Declaration**
- Content overlap percentage (must be ≥70%)
- Recommendation statement

---

### Final Principal Proposal (Single consolidated document)

**Page 1: Cover Letter**
- From: Principal
- To: Registrar, KTU
- Subject: MOOC Approval Request for Jan-Apr 2026 Semester
- List of proposed mappings

**Page 2: Summary Table**
| S.No | KTU Course | NPTEL Course | Institution | Duration | Match % |
|------|------------|--------------|-------------|----------|---------|

**Page 3: IQAC Recommendation**

**Attachments: Individual Mapping Reports**

---

## File Naming Convention

Individual Reports:
```
MOOC_[KTU_CODE]_Report.pdf
Example: MOOC_PECST405_Report.pdf
```

Final Proposal:
```
MOOC_Principal_Proposal_[Semester].pdf
Example: MOOC_Principal_Proposal_Jan2026.pdf
```

---

## Workspace Files Reference

### KTU Syllabus Sources:
| File | Contains |
|------|----------|
| `Computer Science and Engineering.pdf` | CSE PE4, PE5, PE6 courses |
| `Honours - Computer Science and Engineering.pdf` | CSE Honours courses |
| `Ece.pdf` | ECE Open/Programme Electives |
| `Mechnaical.pdf` | Mechanical Open Electives |
| `Elecel.pdf` | Electrical & Electronics Open Electives |
| `GroupB *.pdf` | Group B electives |
| `GroupC *.pdf` | Group C electives |

### NPTEL Course PDFs:
Numeric filenames (e.g., `106105158.pdf`) - one-page NPTEL course summaries

### NPTEL Course List:
`Final Course List (Jan - Apr 2026)(1).xlsx` - Master list with Course IDs, Names, Institutions, Duration

---

## How to Request New Mappings

Add to README.md:
```
Create MOOC approval report for:
KTU: [CODE] - [NAME]
NPTEL: [COURSE_NAME]
NPTEL PDF: [filename.pdf]
```

Or provide in prompt:
```
New MOOC mapping needed:
KTU Course: PECST405 - Computer Vision
NPTEL Course: Computer Vision and Image Processing
NPTEL PDF: 106105158.pdf
```

---

## Output Requirements

1. **Print-Ready PDFs** - A4, proper margins, no overlapping text
2. **Separate Files** - Each mapping = separate PDF
3. **Professional Format** - Suitable for official submission
4. **Complete Information** - All required fields filled or marked "NOT AVAILABLE"

---

## Data Integrity Rules

1. **NEVER fabricate** syllabus topics, credits, instructor names, or durations
2. **Extract exactly** from source files - no paraphrasing
3. **Mark missing data** as: "NOT AVAILABLE IN SOURCE FILE"
4. **Verify 70% match** before generating report
5. **Use actual page numbers** from source PDFs
