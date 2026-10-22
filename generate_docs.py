"""
Script to generate the comprehensive Word specification document for the Cheat Detection System (CDS).
Reflects the 2-Stage Strategic Roadmap and the 4-Stage Processing Architecture:
  - Stage 1: Passive NLP Detector (Historical Game DB + Cold Start Training Mode)
  - Stage 2: Active Anomaly Detector (Live Telemetry: speed, height, DPM, micro-aim)
  - Stage 3: Agentic Profile Inspector (Cheat seller detection on Discord/Telegram)
  - Stage 4: Central Pipeline Orchestrator (Cross-model Gray routing, 3-Gray -> Red promotion rule)
  - Developer Handover: Free / Monitor / Ban
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_document(output_path):
    doc = docx.Document()
    
    # Page setup - 1 inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
    
    navy_color = RGBColor(15, 41, 66)
    teal_color = RGBColor(2, 132, 199)
    slate_color = RGBColor(30, 41, 59)
    
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = slate_color
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # ------------------ COVER / TITLE SECTION ------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(36)
    title_p.paragraph_format.space_after = Pt(6)
    title_run = title_p.add_run("CHEAT DETECTION SYSTEM (CDS)")
    title_run.font.name = 'Arial'
    title_run.font.size = Pt(26)
    title_run.font.bold = True
    title_run.font.color.rgb = navy_color

    subtitle_p = doc.add_paragraph()
    subtitle_p.paragraph_format.space_after = Pt(24)
    subtitle_run = subtitle_p.add_run("Technical Architecture, Battleground Implementation & Developer Handover")
    subtitle_run.font.name = 'Arial'
    subtitle_run.font.size = Pt(13)
    subtitle_run.font.color.rgb = teal_color

    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.LEFT
    meta_table.autofit = False
    
    meta_data = [
        ("Project:", "Cheat Detection System (CDS)"),
        ("Strategic Roadmap:", "Stage 1 (Core Analogy Engine) & Stage 2 (Battleground Games)"),
        ("Internal Architecture:", "4-Stage Triangulation (Passive NLP + Active Telemetry + Profile Agent + Orchestrator)"),
        ("Consensus Engine:", "3-GRAY Promotion Rule (3x GRAY ===> RED) & 2-GRAY Retention"),
        ("Classification Tiers:", "GREEN (Free) | GRAY (Monitor) | RED (Ban / Quarantine)"),
        ("Document Version:", "2.0.0-PRODUCTION SPECIFICATION (October 2026)")
    ]
    
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c1, c2 = row.cells[0], row.cells[1]
        c1.width = Inches(2.2)
        c2.width = Inches(4.3)
        set_cell_background(c1, "F1F5F9")
        set_cell_background(c2, "F8FAFC")
        set_cell_margins(c1, 80, 80, 100, 100)
        set_cell_margins(c2, 80, 80, 100, 100)
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(k)
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = navy_color
        
        p2 = c2.paragraphs[0]
        r2 = p2.add_run(v)
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = slate_color

    doc.add_page_break()

    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(8)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = navy_color
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = teal_color
        return h

    # ------------------ 1. STRATEGIC ROADMAP ------------------
    add_h1("1. Strategic Product Roadmap")
    p = doc.add_paragraph()
    p.add_run(
        "The Cheat Detection System (CDS) is engineered across two overarching product stages:\n"
        "• Stage 1 (Core Analogy Engine — Current Development): The core framework, mathematical models, feature scaling pipelines, NLP tokenization engine, and multi-model consensus logic.\n"
        "• Stage 2 (Modern Battleground Implementation — Next Step): Tailored integration for 100-player Battle Royale / Battleground games (e.g. PUBG, Warzone, Apex, Free Fire) addressing parachuting, open-world terrain elevation, vehicle dynamics, and long-range ballistic gunplay."
    )

    # ------------------ 2. DEVELOPER INTEGRATION WORKFLOW ------------------
    add_h1("2. Developer End: Integration & Onboarding Flow")
    p = doc.add_paragraph()
    p.add_run(
        "Game developers integrate CDS into their production infrastructure through a standardized sequence:\n"
        "1. Fork Repository & Read Documentation: Developer forks the repository and reviews battleground-implementation.md.\n"
        "2. Stage 1 Hookup & Cold-Start Training: Developer attaches their game database (Win rate, K/D, Headshot %, DPM), runs feature scaling, and executes training mode with a binary GREEN/RED Answer Key.\n"
        "3. Stage 2 Hookup: Connects live dedicated server telemetry (speed, height, DPM, live headshots, micro-aim adjustments). Clean players are discarded, reporting only GRAY and RED.\n"
        "4. Stage 3 Hookup: Connects player profiles and social metadata to the Agentic Profile Inspector to catch cheat sellers advertising on Discord/Telegram. Outputs GREEN/GRAY only.\n"
        "5. Stage 4 Orchestrator: Balances all models simultaneously, aggregates cross-model GRAY lists, applies the 3-GRAY to RED promotion rule, and delivers final rosters.\n"
        "6. Developer Handover: Developer frees GREEN players, monitors GRAY players, and bans RED players according to studio policy. CDS holds no responsibility for subsequent moderation decisions."
    )

    # ------------------ 3. THE 4 INTERNAL PROCESSING STAGES ------------------
    add_h1("3. The 4 Internal Processing Stages of CDS")

    add_h2("3.1 Stage 1: Passive Detector (NLP Method on Game Database)")
    p = doc.add_paragraph()
    p.add_run(
        "The Passive Detector attaches to historical player databases. Numerical features (Win rate, K/D, Total matches, Headshot rate, DPM) are scaled and serialized into NLP feature tokens.\n"
        "Cold-Start Training Mode: When initialized for the first time, the developer supplies an Answer Key of known GREEN and RED accounts. Ground truth has no intermediate GRAY—this establishes clean decision boundaries, allowing the model to accurately infer suspicious intermediate GRAY players during live operation.\n"
        "Output: Tri-state roster of GREEN, GRAY, and RED."
    )

    add_h2("3.2 Stage 2: Active Detector (Real-Time In-Game Anomaly)")
    p = doc.add_paragraph()
    p.add_run(
        "Running concurrently and independently during live matches, Stage 2 processes streaming telemetry:\n"
        "• Movement Speed: Detects speed hacks exceeding natural sprint thresholds.\n"
        "• Player Height / Elevation: Detects fly hacks and vertical teleportation.\n"
        "• Damage Per Minute (DPM) & Live K/D: Flags impossible single-match burst combat.\n"
        "• Micro-Aim Snapping: Detects non-biological aimbot micro-adjustments.\n"
        "Resource Optimization: Clean players (GREEN) are immediately discarded from alerting to reduce server tick overhead. Only GRAY and RED are reported."
    )

    add_h2("3.3 Stage 3: External Verification (Agentic Profile Inspector)")
    p = doc.add_paragraph()
    p.add_run(
        "Many aggressive cheaters monetize their hacks by placing contact details in their profile bio, nickname, or clan tag (e.g. 'DM for undetected VIP hack DC: seller#123', 'Telegram: t.me/ez_cheats').\n"
        "Stage 3 extracts profile metadata and uses LLM agentic heuristics to detect cheat-seller language and external communication handles.\n"
        "Safety Invariant: Because profile text alone cannot prove active in-game cheating, Stage 3 outputs ONLY GREEN or GRAY (never RED directly)."
    )

    add_h2("3.4 Stage 4: Central Pipeline Orchestrator & Consensus Engine")
    p = doc.add_paragraph()
    p.add_run(
        "Stage 4 manages simultaneous model execution, routes data streams, and enforces the cross-model consensus rules:\n"
        "• Direct RED Rule: Any direct RED from Stage 1 or Stage 2 results in immediate RED classification.\n"
        "• The 3-GRAY Promotion Rule: If a player is flagged as GRAY across ALL THREE models (Stage 1 Passive, Stage 2 Active, AND Stage 3 Profile), Stage 4 automatically promotes them to RED.\n"
        "• The 2-GRAY Retention Rule: If a player is flagged as GRAY in only 1 or 2 models, they are kept in GRAY for elevated monitoring.\n"
        "• Nominal Rule: Players clean across models remain GREEN."
    )

    # ------------------ 4. CONSENSUS MATRIX TABLE ------------------
    add_h1("4. Stage 4 Consensus Matrix")
    
    matrix_table = doc.add_table(rows=6, cols=4)
    matrix_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    matrix_table.autofit = False

    headers = ["Stage 1 (Passive DB)", "Stage 2 (Active Telemetry)", "Stage 3 (Profile Bio)", "Final Resolution"]
    for j, h_text in enumerate(headers):
        cell = matrix_table.rows[0].cells[j]
        set_cell_background(cell, "0F2942")
        p_cell = cell.paragraphs[0]
        r = p_cell.add_run(h_text)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9.5)

    matrix_data = [
        ("RED", "Any", "Any", "RED (Instant Flag from DB)"),
        ("Any", "RED", "Any", "RED (Instant Flag from Telemetry)"),
        ("GRAY", "GRAY", "GRAY", "RED (Promoted: 3-Gray Consensus)"),
        ("GRAY", "GRAY", "GREEN", "GRAY (Retained: 2-Gray Flag)"),
        ("GREEN", "GREEN", "GREEN", "GREEN (Clean Baseline)")
    ]

    widths = [Inches(1.6), Inches(1.8), Inches(1.6), Inches(1.8)]
    for i, row in enumerate(matrix_data, start=1):
        for j, val in enumerate(row):
            cell = matrix_table.rows[i].cells[j]
            cell.width = widths[j]
            set_cell_background(cell, "FFFFFF" if i % 2 == 1 else "F8FAFC")
            set_cell_margins(cell, 80, 80, 100, 100)
            p_cell = cell.paragraphs[0]
            r = p_cell.add_run(val)
            r.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_before = Pt(12)

    # ------------------ 5. DEVELOPER RESPONSIBILITY HANDOVER ------------------
    add_h1("5. Developer Responsibility & Enforcement Handover")
    p = doc.add_paragraph()
    p.add_run(
        "CDS delivers intelligence and classification. Policy enforcement is strictly executed by the game studio:\n"
        "• GREEN: Free players to engage in normal matchmaking. Standard low-frequency telemetry.\n"
        "• GRAY: Apply game-specific monitoring: increase server tickrate to 128Hz, record full demo replay, or place in soft trust-factor matchmaking.\n"
        "• RED: Execute disciplinary actions: instant match disconnect, account/HWID ban, damage nullification, or routing to shadow-lobbies (cheaters vs. cheaters).\n\n"
        "CDS accepts no liability or responsibility for developer enforcement penalties or ban disputes."
    )

    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    target = os.path.join(r"D:\Project\CDS", "Cheat_Detection_System_Specification.docx")
    create_document(target)
