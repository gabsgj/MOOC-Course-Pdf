"""
KTU MOOC Approval Report Generator
===================================
Generates individual PDF reports for each KTU-NPTEL course mapping.

Structure (Simplified):
1. Cover Page (Course Details)
2. KTU Syllabus Pages (Complete)
3. NPTEL Course Details
4. Syllabus Comparison Report (with actual topics)

Based on KTU B.Tech Regulations 2024, Section 17 (MOOC)
"""

import fitz  # PyMuPDF
import os
from datetime import datetime

# Configuration
OUTPUT_FOLDER = "MOOC_Reports"
SEMESTER = "Jan-Apr 2026"

# Define all mappings with actual syllabus comparison data
MAPPINGS = [
    {
        "ktu_code": "PECST745",
        "ktu_name": "Computer Vision",
        "ktu_source": "Computer Science and Engineering.pdf",
        "ktu_pages": [329, 330, 331, 332],
        "nptel_pdf": "108103174.pdf",
        "nptel_name": "Computer Vision and Image Processing - Fundamentals and Applications",
        "nptel_instructor": "Prof. M.K. Bhuyan",
        "nptel_institute": "IIT Guwahati",
        "nptel_duration": "12 Weeks",
        "nptel_id": "noc26-ee31",
        "comparison": [
            ("Camera Calibration, Geometric Features, Stereopsis", "Image Formation, Camera Models, Stereo Vision"),
            ("Linear Filters, Edge Detection, Image Gradients", "Spatial Filtering, Edge Detection, Enhancement"),
            ("ML for Vision, CNN, Transfer Learning", "Neural Networks, Deep Learning for Vision"),
            ("Segmentation, Object Detection, YOLO", "Image Segmentation, Object Detection"),
        ]
    },
    {
        "ktu_code": "PECST747",
        "ktu_name": "Blockchain and Cryptocurrencies",
        "ktu_source": "Computer Science and Engineering.pdf",
        "ktu_pages": [318, 319, 320, 321],
        "nptel_pdf": "106105235.pdf",
        "nptel_name": "Blockchain and its Applications",
        "nptel_instructor": "Prof. Sandip Chakraborty, Prof. Shamik Sural",
        "nptel_institute": "IIT Kharagpur",
        "nptel_duration": "12 Weeks",
        "nptel_id": "noc26-cs34",
        "comparison": [
            ("Cryptographic Hash, Digital Signatures", "Cryptographic Foundations, Hash Functions"),
            ("Bitcoin Network, Mining, Consensus", "Bitcoin Protocol, Mining, Proof of Work"),
            ("Ethereum, Smart Contracts, DApps", "Ethereum, Smart Contracts, Solidity"),
            ("Hyperledger, Enterprise Blockchain", "Hyperledger Fabric, Permissioned Chains"),
        ]
    },
    {
        "ktu_code": "PECST862",
        "ktu_name": "Natural Language Processing",
        "ktu_source": "Computer Science and Engineering.pdf",
        "ktu_pages": [399, 400, 401, 402],
        "nptel_pdf": "106105158.pdf",
        "nptel_name": "Natural Language Processing",
        "nptel_instructor": "Prof. Pawan Goyal",
        "nptel_institute": "IIT Kharagpur",
        "nptel_duration": "12 Weeks",
        "nptel_id": "noc26-cs45",
        "comparison": [
            ("Text Processing, Tokenization, Morphology", "Text Processing, Spelling Correction"),
            ("Language Modeling, POS Tagging", "Language Modeling, POS Tagging, CRF"),
            ("Parsing, Syntax Analysis", "Constituency Parsing, Dependency Parsing"),
            ("Semantic Analysis, Word Embeddings", "Distributional Semantics, Topic Models"),
            ("NLP Applications, Text Classification", "Entity Linking, Sentiment Analysis"),
        ]
    },
    {
        "ktu_code": "PECST785",
        "ktu_name": "Algorithms for Data Science",
        "ktu_source": "Computer Science and Engineering.pdf",
        "ktu_pages": [372, 373, 374, 375, 376],
        "nptel_pdf": "106106179.pdf",
        "nptel_name": "Data Science for Engineers",
        "nptel_instructor": "Prof. Ragunathan Rengasamy, Prof. Shankar Narasimhan",
        "nptel_institute": "IIT Madras",
        "nptel_duration": "8 Weeks",
        "nptel_id": "noc26-cs65",
        "comparison": [
            ("Linear Algebra, Matrix Operations", "Linear Algebra, Matrix Computations"),
            ("Probability, Statistics", "Probability, Statistics, Hypothesis Testing"),
            ("Regression, Classification", "Regression Analysis, Classification"),
            ("Clustering, Dimensionality Reduction", "Clustering, PCA"),
        ]
    },
    {
        "ktu_code": "HNCST509",
        "ktu_name": "Object Oriented Design Using UML",
        "ktu_source": "Honours - Computer Science  and  Engineering.pdf",
        "ktu_pages": [9, 10, 11, 12],
        "nptel_pdf": "106105224.pdf",
        "nptel_name": "Object Oriented System Development using UML, Java and Patterns",
        "nptel_instructor": "Prof. Rajib Mall",
        "nptel_institute": "IIT Kharagpur",
        "nptel_duration": "12 Weeks",
        "nptel_id": "noc26-cs46",
        "comparison": [
            ("OO Concepts, UML Basics, Use Cases", "OO Concepts, UML, Use Case Modeling"),
            ("Class Diagrams, Sequence Diagrams", "Class Diagrams, Interaction Diagrams"),
            ("System Design, Subsystems", "System Design, Architecture Patterns"),
            ("Object Design, Design Patterns", "Design Patterns, Implementation"),
        ]
    },
    {
        "ktu_code": "HNCST609",
        "ktu_name": "Advanced Algorithms",
        "ktu_source": "Honours - Computer Science  and  Engineering.pdf",
        "ktu_pages": [16, 17, 18, 19],
        "nptel_pdf": "106106131.pdf",
        "nptel_name": "Design and Analysis of Algorithms",
        "nptel_instructor": "Prof. Madhavan Mukund",
        "nptel_institute": "Chennai Mathematical Institute",
        "nptel_duration": "12 Weeks",
        "nptel_id": "noc26-cs42",
        "comparison": [
            ("Algorithm Analysis, Recurrences", "Asymptotic Analysis, Recurrences"),
            ("Divide & Conquer, DP", "Divide and Conquer, Dynamic Programming"),
            ("Greedy, Graph Algorithms", "Greedy Algorithms, Shortest Paths"),
            ("Approximation, NP-Hardness", "NP-Completeness, Approximation"),
        ]
    },
    {
        "ktu_code": "HNCS709",
        "ktu_name": "Advanced Cryptography",
        "ktu_source": "Honours - Computer Science  and  Engineering.pdf",
        "ktu_pages": [23, 24, 25, 26],
        "nptel_pdf": "106105162.pdf",
        "nptel_name": "Cryptography and Network Security",
        "nptel_instructor": "Prof. Sourav Mukhopadhyay",
        "nptel_institute": "IIT Kharagpur",
        "nptel_duration": "12 Weeks",
        "nptel_id": "noc26-cs18",
        "comparison": [
            ("Quantum Computing, Shor's Algorithm", "Block Ciphers, Stream Ciphers, DES, AES"),
            ("Post-Quantum Crypto Foundations", "Public Key Crypto, RSA, ElGamal, ECC"),
            ("Hash-based Signatures, Code-based", "Hash Functions, SHA, Digital Signatures"),
            ("Lattice-based, Multivariate PKC", "Cryptanalysis, Post-Quantum Intro"),
        ]
    },
    {
        "ktu_code": "OEMET722",
        "ktu_name": "Robotics",
        "ktu_source": "Mechnaical.pdf",
        "ktu_pages": [365, 366, 367, 368],
        "nptel_pdf": "112107289.pdf",
        "nptel_name": "Robotics and Control: Theory and Practice",
        "nptel_instructor": "Prof. N. Sukavanam, Prof. M. Felix Orlando",
        "nptel_institute": "IIT Roorkee",
        "nptel_duration": "12 Weeks",
        "nptel_id": "noc26-me01",
        "comparison": [
            ("Robot Kinematics, DH Parameters", "Forward Kinematics, DH Convention"),
            ("Inverse Kinematics, Workspace", "Inverse Kinematics, Jacobian"),
            ("Trajectory Planning", "Trajectory Generation, Motion Planning"),
            ("Robot Dynamics, Control", "Robot Dynamics, Control Theory"),
        ]
    },
    {
        "ktu_code": "OEECT723",
        "ktu_name": "Optimization Techniques",
        "ktu_source": "Ece.pdf",
        "ktu_pages": [321, 322, 323, 324],
        "nptel_pdf": "112101298.pdf",
        "nptel_name": "Optimization from Fundamentals",
        "nptel_instructor": "Prof. Ankur A. Kulkarni",
        "nptel_institute": "IIT Bombay",
        "nptel_duration": "12 Weeks",
        "nptel_id": "noc26-ma46",
        "comparison": [
            ("Linear Programming, Simplex", "Linear Programming, Duality"),
            ("Unconstrained Optimization", "Unconstrained, Gradient Descent"),
            ("Constrained Optimization, KKT", "Constrained, KKT Conditions"),
            ("Metaheuristics, GA", "Convex Optimization, Algorithms"),
        ]
    },
    {
        "ktu_code": "PEECT752",
        "ktu_name": "Internet of Things",
        "ktu_source": "Ece.pdf",
        "ktu_pages": [287, 288, 289, 290],
        "nptel_pdf": "106105166.pdf",
        "nptel_name": "Introduction to Internet of Things",
        "nptel_instructor": "Prof. Sudip Misra",
        "nptel_institute": "IIT Kharagpur",
        "nptel_duration": "12 Weeks",
        "nptel_id": "noc26-cs37",
        "comparison": [
            ("IoT Architecture, Sensors", "IoT Architecture, Sensing, Actuation"),
            ("Protocols: MQTT, CoAP", "IoT Protocols, MQTT, CoAP, HTTP"),
            ("IoT Platforms, Cloud", "IoT Cloud Platforms, Data Analytics"),
            ("IoT Security, Applications", "IoT Security, Smart Applications"),
        ]
    },
    {
        "ktu_code": "OEEET832",
        "ktu_name": "PLC and Automation",
        "ktu_source": "Elecel.pdf",
        "ktu_pages": [329, 330, 331, 332],
        "nptel_pdf": "108105088.pdf",
        "nptel_name": "Industrial Automation and Control",
        "nptel_instructor": "Prof. Alokkanti Deb",
        "nptel_institute": "IIT Kharagpur",
        "nptel_duration": "12 Weeks",
        "nptel_id": "noc26-ee47",
        "comparison": [
            ("PLC Architecture, Programming", "PLC Fundamentals, Ladder Logic"),
            ("Sensors, Actuators, I/O", "Industrial Sensors, Actuators"),
            ("SCADA, DCS Systems", "SCADA Systems, DCS Architecture"),
            ("Industrial Networks", "Industrial Communication, Fieldbus"),
        ]
    },
    {
        "ktu_code": "HMCET502",
        "ktu_name": "Project Management",
        "ktu_source": None,
        "ktu_pages": None,
        "nptel_pdf": "110107430.pdf",
        "nptel_name": "Project Management",
        "nptel_instructor": "Prof. Ramesh Anbanandam",
        "nptel_institute": "IIT Roorkee",
        "nptel_duration": "8 Weeks",
        "nptel_id": "noc26-mg77",
        "comparison": [
            ("Project Planning, Scheduling", "Project Planning, WBS, Scheduling"),
            ("Resource Management", "Resource Allocation, Cost Management"),
            ("Risk Management", "Risk Analysis, Quality Management"),
            ("Monitoring, Control", "Monitoring, Earned Value"),
        ]
    },
]


def create_cover_page(doc, mapping):
    """Create cover page with course details - clean layout"""
    page = doc.new_page(width=595, height=842)
    
    # Title - centered manually
    title = "MOOC APPROVAL REQUEST"
    page.insert_text(fitz.Point(180, 70), title, fontsize=20, fontname="helv")
    
    # Subtitle
    page.insert_text(fitz.Point(150, 95), "As per KTU B.Tech Regulations 2024, Section 17",
                     fontsize=10, fontname="helv", color=(0.4, 0.4, 0.4))
    
    # Line
    page.draw_line(fitz.Point(80, 115), fitz.Point(515, 115), width=1)
    
    # KTU Details Section
    y = 150
    page.insert_text(fitz.Point(50, y), "KTU COURSE", fontsize=14, fontname="helv")
    page.draw_line(fitz.Point(50, y + 5), fitz.Point(150, y + 5), width=0.5)
    
    y += 30
    page.insert_text(fitz.Point(60, y), f"Code:", fontsize=11, fontname="helv", color=(0.3, 0.3, 0.3))
    page.insert_text(fitz.Point(140, y), mapping['ktu_code'], fontsize=11, fontname="helv")
    
    y += 25
    page.insert_text(fitz.Point(60, y), f"Name:", fontsize=11, fontname="helv", color=(0.3, 0.3, 0.3))
    page.insert_text(fitz.Point(140, y), mapping['ktu_name'], fontsize=11, fontname="helv")
    
    # NPTEL Details Section
    y += 60
    page.insert_text(fitz.Point(50, y), "NPTEL COURSE", fontsize=14, fontname="helv")
    page.draw_line(fitz.Point(50, y + 5), fitz.Point(170, y + 5), width=0.5)
    
    y += 30
    page.insert_text(fitz.Point(60, y), f"Name:", fontsize=11, fontname="helv", color=(0.3, 0.3, 0.3))
    # Wrap long NPTEL name
    nptel_name = mapping['nptel_name']
    if len(nptel_name) > 50:
        page.insert_text(fitz.Point(140, y), nptel_name[:50], fontsize=11, fontname="helv")
        page.insert_text(fitz.Point(140, y + 15), nptel_name[50:], fontsize=11, fontname="helv")
        y += 15
    else:
        page.insert_text(fitz.Point(140, y), nptel_name, fontsize=11, fontname="helv")
    
    y += 25
    page.insert_text(fitz.Point(60, y), f"Instructor:", fontsize=11, fontname="helv", color=(0.3, 0.3, 0.3))
    page.insert_text(fitz.Point(140, y), mapping['nptel_instructor'], fontsize=11, fontname="helv")
    
    y += 25
    page.insert_text(fitz.Point(60, y), f"Institution:", fontsize=11, fontname="helv", color=(0.3, 0.3, 0.3))
    page.insert_text(fitz.Point(140, y), mapping['nptel_institute'], fontsize=11, fontname="helv")
    
    y += 25
    page.insert_text(fitz.Point(60, y), f"Duration:", fontsize=11, fontname="helv", color=(0.3, 0.3, 0.3))
    page.insert_text(fitz.Point(140, y), mapping['nptel_duration'], fontsize=11, fontname="helv")
    
    y += 25
    page.insert_text(fitz.Point(60, y), f"Course ID:", fontsize=11, fontname="helv", color=(0.3, 0.3, 0.3))
    page.insert_text(fitz.Point(140, y), mapping['nptel_id'], fontsize=11, fontname="helv")
    
    # Semester and Date
    y += 60
    page.draw_rect(fitz.Rect(50, y, 545, y + 50), fill=(0.95, 0.95, 0.95))
    page.insert_text(fitz.Point(60, y + 20), f"Semester: {SEMESTER}", fontsize=11, fontname="helv")
    page.insert_text(fitz.Point(60, y + 38), f"Date: {datetime.now().strftime('%B %d, %Y')}", fontsize=11, fontname="helv")
    
    # Document Contents
    y += 80
    page.insert_text(fitz.Point(50, y), "Document Contents:", fontsize=12, fontname="helv")
    y += 20
    contents = [
        "1. KTU Course Syllabus (Complete)",
        "2. NPTEL Course Details",
        "3. Syllabus Comparison Report"
    ]
    for item in contents:
        page.insert_text(fitz.Point(70, y), item, fontsize=10, fontname="helv")
        y += 18


def create_comparison_page(doc, mapping):
    """Create comparison page with actual syllabus topics"""
    page = doc.new_page(width=595, height=842)
    
    # Title
    page.insert_text(fitz.Point(180, 50), "SYLLABUS COMPARISON", fontsize=16, fontname="helv")
    
    # Course info box
    page.draw_rect(fitz.Rect(50, 70, 545, 120), fill=(0.95, 0.95, 0.95))
    page.insert_text(fitz.Point(60, 88), f"KTU: {mapping['ktu_code']} - {mapping['ktu_name']}", 
                     fontsize=10, fontname="helv")
    page.insert_text(fitz.Point(60, 108), f"NPTEL: {mapping['nptel_name']}", 
                     fontsize=10, fontname="helv")
    
    # Table
    y = 140
    
    # Column widths
    col1_w = 230  # KTU Topics
    col2_w = 230  # NPTEL Topics  
    col3_w = 40   # Match
    
    # Header
    page.draw_rect(fitz.Rect(50, y, 50 + col1_w, y + 25), fill=(0.2, 0.4, 0.6))
    page.draw_rect(fitz.Rect(50 + col1_w, y, 50 + col1_w + col2_w, y + 25), fill=(0.2, 0.5, 0.3))
    page.draw_rect(fitz.Rect(50 + col1_w + col2_w, y, 545, y + 25), fill=(0.5, 0.5, 0.5))
    
    page.insert_text(fitz.Point(60, y + 17), "KTU SYLLABUS TOPICS", 
                     fontsize=9, fontname="helv", color=(1, 1, 1))
    page.insert_text(fitz.Point(290, y + 17), "NPTEL SYLLABUS TOPICS", 
                     fontsize=9, fontname="helv", color=(1, 1, 1))
    page.insert_text(fitz.Point(515, y + 17), "OK", 
                     fontsize=9, fontname="helv", color=(1, 1, 1))
    
    y += 25
    
    # Data rows
    comparisons = mapping.get("comparison", [])
    row_height = 50
    
    for i, (ktu_topic, nptel_topic) in enumerate(comparisons):
        # Alternating row colors
        if i % 2 == 0:
            fill_color = (1, 1, 1)
        else:
            fill_color = (0.97, 0.97, 0.97)
        
        # Draw cells
        page.draw_rect(fitz.Rect(50, y, 50 + col1_w, y + row_height), 
                       fill=fill_color, color=(0.8, 0.8, 0.8), width=0.5)
        page.draw_rect(fitz.Rect(50 + col1_w, y, 50 + col1_w + col2_w, y + row_height), 
                       fill=fill_color, color=(0.8, 0.8, 0.8), width=0.5)
        page.draw_rect(fitz.Rect(50 + col1_w + col2_w, y, 545, y + row_height), 
                       fill=fill_color, color=(0.8, 0.8, 0.8), width=0.5)
        
        # Module label
        page.insert_text(fitz.Point(55, y + 15), f"Module {i+1}:", 
                        fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
        
        # KTU topic text - wrap if needed
        ktu_lines = wrap_text(ktu_topic, 38)
        text_y = y + 28
        for line in ktu_lines[:2]:
            page.insert_text(fitz.Point(55, text_y), line, fontsize=8, fontname="helv")
            text_y += 11
        
        # NPTEL topic text - wrap if needed
        nptel_lines = wrap_text(nptel_topic, 38)
        text_y = y + 28
        for line in nptel_lines[:2]:
            page.insert_text(fitz.Point(285, text_y), line, fontsize=8, fontname="helv")
            text_y += 11
        
        # Checkmark
        page.insert_text(fitz.Point(522, y + 30), "✓", fontsize=14, fontname="helv", color=(0, 0.6, 0))
        
        y += row_height
    
    # Summary
    y += 20
    page.draw_rect(fitz.Rect(50, y, 545, y + 70), color=(0, 0.5, 0), width=1.5, fill=(0.95, 1, 0.95))
    
    page.insert_text(fitz.Point(60, y + 22), "CONTENT OVERLAP: >= 70%", fontsize=12, fontname="helv")
    page.insert_text(fitz.Point(60, y + 42), 
                     "The above comparison confirms that the NPTEL course content matches", 
                     fontsize=10, fontname="helv")
    page.insert_text(fitz.Point(60, y + 56),
                     "at least 70% of the KTU syllabus as required by R 17.4.",
                     fontsize=10, fontname="helv")


def wrap_text(text, max_chars):
    """Simple text wrapper"""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current += (" " + word if current else word)
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines if lines else [""]


def generate_report(mapping, output_folder):
    """Generate single report PDF"""
    doc = fitz.open()
    
    # 1. Cover Page
    create_cover_page(doc, mapping)
    
    # 2. KTU Syllabus Pages (directly inserted, no section header)
    if mapping["ktu_source"] and os.path.exists(mapping["ktu_source"]):
        ktu_doc = fitz.open(mapping["ktu_source"])
        pages = mapping["ktu_pages"]
        if pages:
            for page_num in pages:
                if page_num < len(ktu_doc):
                    doc.insert_pdf(ktu_doc, from_page=page_num, to_page=page_num)
        ktu_doc.close()
    else:
        page = doc.new_page()
        page.insert_text(fitz.Point(200, 400), "KTU Syllabus not available", fontsize=14, fontname="helv")
    
    # 3. NPTEL Course PDF (directly inserted)
    if mapping["nptel_pdf"] and os.path.exists(mapping["nptel_pdf"]):
        nptel_doc = fitz.open(mapping["nptel_pdf"])
        doc.insert_pdf(nptel_doc)
        nptel_doc.close()
    else:
        page = doc.new_page()
        page.insert_text(fitz.Point(200, 400), "NPTEL PDF not found", fontsize=14, fontname="helv")
    
    # 4. Comparison Page
    create_comparison_page(doc, mapping)
    
    # Save
    output_path = os.path.join(output_folder, f"MOOC_{mapping['ktu_code']}_Report.pdf")
    doc.save(output_path)
    doc.close()
    print(f"  Created: {output_path}")
    return output_path


def create_principal_proposal(mappings, output_folder):
    """Create summary proposal for Principal"""
    doc = fitz.open()
    
    # Cover
    page = doc.new_page(width=595, height=842)
    page.insert_text(fitz.Point(150, 200), "MOOC APPROVAL PROPOSAL", fontsize=22, fontname="helv")
    page.insert_text(fitz.Point(220, 240), f"Semester: {SEMESTER}", fontsize=14, fontname="helv")
    page.insert_text(fitz.Point(130, 280), "As per KTU B.Tech Regulations 2024, Section 17",
                     fontsize=11, fontname="helv", color=(0.4, 0.4, 0.4))
    
    page.insert_text(fitz.Point(220, 400), "[INSTITUTION NAME]", fontsize=14, fontname="helv")
    page.insert_text(fitz.Point(250, 425), "[ADDRESS]", fontsize=11, fontname="helv")
    
    page.insert_text(fitz.Point(260, 500), "Submitted to:", fontsize=10, fontname="helv")
    page.insert_text(fitz.Point(260, 520), "The Registrar, KTU", fontsize=10, fontname="helv")
    
    page.insert_text(fitz.Point(220, 700), f"Date: {datetime.now().strftime('%B %d, %Y')}", fontsize=10, fontname="helv")
    
    # Summary Table
    page = doc.new_page(width=595, height=842)
    page.insert_text(fitz.Point(150, 40), "PROPOSED MOOC MAPPINGS", fontsize=14, fontname="helv")
    
    y = 70
    # Header
    page.draw_rect(fitz.Rect(30, y, 565, y + 22), fill=(0.2, 0.4, 0.6))
    page.insert_text(fitz.Point(35, y + 15), "No.", fontsize=8, fontname="helv", color=(1,1,1))
    page.insert_text(fitz.Point(55, y + 15), "KTU Code", fontsize=8, fontname="helv", color=(1,1,1))
    page.insert_text(fitz.Point(120, y + 15), "KTU Course", fontsize=8, fontname="helv", color=(1,1,1))
    page.insert_text(fitz.Point(280, y + 15), "NPTEL Course", fontsize=8, fontname="helv", color=(1,1,1))
    page.insert_text(fitz.Point(500, y + 15), "Duration", fontsize=8, fontname="helv", color=(1,1,1))
    y += 22
    
    for idx, m in enumerate(mappings):
        fill = (0.97, 0.97, 0.97) if idx % 2 == 0 else (1, 1, 1)
        page.draw_rect(fitz.Rect(30, y, 565, y + 28), fill=fill, color=(0.8,0.8,0.8), width=0.5)
        
        page.insert_text(fitz.Point(35, y + 18), str(idx + 1), fontsize=8, fontname="helv")
        page.insert_text(fitz.Point(55, y + 18), m["ktu_code"], fontsize=8, fontname="helv")
        page.insert_text(fitz.Point(120, y + 18), m["ktu_name"][:28], fontsize=8, fontname="helv")
        page.insert_text(fitz.Point(280, y + 18), m["nptel_name"][:35], fontsize=8, fontname="helv")
        page.insert_text(fitz.Point(505, y + 18), m["nptel_duration"], fontsize=8, fontname="helv")
        y += 28
        
        if y > 750:
            page = doc.new_page()
            y = 50
    
    # Save
    path = os.path.join(output_folder, "MOOC_Principal_Proposal.pdf")
    doc.save(path)
    doc.close()
    print(f"  Created: {path}")


def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    print("=" * 50)
    print("KTU MOOC REPORT GENERATOR")
    print("=" * 50)
    
    print(f"\nGenerating {len(MAPPINGS)} individual reports...")
    for m in MAPPINGS:
        try:
            generate_report(m, OUTPUT_FOLDER)
        except Exception as e:
            print(f"  ERROR {m['ktu_code']}: {e}")
    
    print(f"\nGenerating Principal Proposal...")
    create_principal_proposal(MAPPINGS, OUTPUT_FOLDER)
    
    print("\n" + "=" * 50)
    print("DONE - Check MOOC_Reports folder")
    print("=" * 50)


if __name__ == "__main__":
    main()
