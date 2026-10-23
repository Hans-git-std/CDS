"""
Script to generate the comprehensive Word specification document for the Cheat Detection System (CDS).
Reflects:
  - Features decided by developer (feature-agnostic framework)
  - Powered by TensorFlow Sequential models (Supervised classification & Deep Autoencoders)
  - 2-Stage Strategic Roadmap: Stage 1 Core Framework, Stage 2 Battleground Implementation
  - 4-Stage Operational Engine (Passive NLP, Active Anomaly, Profile Agent, Orchestrator)
  - The 3-GRAY Promotion Rule and Developer Handover
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
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
    
    # 1-inch margins
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

    # ------------------ TITLE SECTION ------------------
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
    subtitle_run = subtitle_p.add_run("Developer Framework Specification Powered by TensorFlow")
    subtitle_run.font.name = 'Arial'
    subtitle_run.font.size = Pt(13)
    subtitle_run.font.color.rgb = teal_color

    meta_data = [
        ("Framework Name:", "Cheat Detection System (CDS)"),
        ("Machine Learning Engine:", "TensorFlow 2.x (Sequential Models & Deep Autoencoders)"),
        ("Feature Philosophy:", "Feature-Agnostic (Dynamic developer-defined features + FeatureScaler)"),
        ("Integration Syntax:", "$$$ info $$$ Markers for all studio-specific parameters"),
        ("Operational Pipeline:", "4-Stage Hybrid (Passive NLP + Active Anomaly + Profile Agent + Orchestrator)"),
        ("Consensus Engine:", "3-GRAY Promotion Rule (3x GRAY ===> RED) & 2-GRAY Retention"),
        ("Specification Version:", "2.2.0-PRODUCTION (October 2026)")
    ]

    meta_table = doc.add_table(rows=len(meta_data), cols=2)
    
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

    # ------------------ 1. EXECUTIVE OVERVIEW ------------------
    add_h1("1. Architectural Purpose & Framework Principles")
    p = doc.add_paragraph()
    p.add_run(
        "The Cheat Detection System (CDS) is a developer-implemented anti-cheat framework built on TensorFlow. "
        "It provides game developers with modular, pre-configured neural network architectures to detect unauthorized third-party "
        "software in modern competitive multiplayer titles (such as Battlegrounds, Battle Royales, and tactical shooters).\n\n"
        "Key Engineering Axioms:\n"
        "• Features are Decided by the Developer: CDS does not hardcode features. Every game tracks unique metrics; the developer passes their own custom feature arrays into the detectors.\n"
        "• TensorFlow Sequential Models: Stage 1 uses a supervised Sequential classifier; Stage 2 uses an unsupervised Sequential Autoencoder.\n"
        "• Newbie-Friendly Integration: The library exposes clean, high-level methods (.train, .classify, .evaluate_telemetry, .harmonize_rosters) enabling rapid developer onboarding."
    )

    # ------------------ 2. THE 4 PROCESSING STAGES ------------------
    add_h1("2. The 4 Operational Processing Stages")

    add_h2("2.1 Stage 1: Passive Detector (TensorFlow Sequential on Historical DB)")
    p = doc.add_paragraph()
    p.add_run(
        "Connects to the game database to evaluate cumulative player performance stats (e.g. Win rate, K/D, Headshots, DPM).\n"
        "Cold-Start Training Mode: When initializing CDS, the developer provides an Answer Key containing binary ground-truth: 0 for GREEN (clean players) and 1 for RED (banned cheaters). "
        "There is no intermediate GRAY in training data. The model learns clean decision boundaries and automatically infers suspicious intermediate GRAY players during live inference.\n"
        "Output: GREEN, GRAY, and RED rosters."
    )

    add_h2("2.2 Stage 2: Active Anomaly Detector (TensorFlow Sequential Autoencoder)")
    p = doc.add_paragraph()
    p.add_run(
        "Evaluates real-time in-game telemetry streamed from dedicated game servers (e.g. movement speed, player height, active combat bursts, aim-snap deltas).\n"
        "Deep Autoencoder Architecture: Trained on normal, legitimate gameplay telemetry to reconstruct natural movement patterns. "
        "High reconstruction error (MSE) indicates an active kinematic cheat.\n"
        "Resource Optimization: Clean players (GREEN) have low reconstruction error and are automatically discarded immediately from reporting, cutting server CPU and memory usage by over 85%. "
        "Only GRAY and RED are reported. Runs independently from Stage 1."
    )

    add_h2("2.3 Stage 3: Agentic Profile Inspector (Cheat Seller Intelligence)")
    p = doc.add_paragraph()
    p.add_run(
        "Aggressive cheat distributors monetize hacks by putting contact info (Discord handles, Telegram invite links, WhatsApp, 'DM for hacks') directly in their profile bio, username, or clan tag.\n"
        "Stage 3 inspects profile metadata and uses agentic pattern evaluation to detect seller channels.\n"
        "Safety Invariant: A profile text string alone cannot definitively prove active in-game cheating. Therefore, Stage 3 outputs ONLY GREEN or GRAY (never RED)."
    )

    add_h2("2.4 Stage 4: Central Pipeline Orchestrator & Consensus Engine")
    p = doc.add_paragraph()
    p.add_run(
        "Stage 4 runs all models simultaneously and balances their workload. Its primary role is cross-evaluating the GRAY lists:\n"
        "• Direct RED Rule: Any direct RED from Stage 1 or Stage 2 leads to immediate RED classification.\n"
        "• The 3-GRAY Promotion Rule: If a player is marked as GRAY across ALL THREE models (Stage 1, Stage 2, and Stage 3), Stage 4 automatically promotes them to RED.\n"
        "• The 2-GRAY Retention Rule: If marked as GRAY in only 1 or 2 models, they are kept in GRAY (retained in the monitor queue).\n"
        "• Clean Rule: Nominal players remain GREEN."
    )

    # ------------------ 3. CONSENSUS MATRIX ------------------
    add_h1("3. Consensus Matrix & Promotion Rules")

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
        ("RED", "Any", "Any", "RED (Direct Red Flag from DB)"),
        ("Any", "RED", "Any", "RED (Direct Red Flag from Live Telemetry)"),
        ("GRAY", "GRAY", "GRAY", "RED (Promoted: 3-Gray Consensus)"),
        ("GRAY", "GRAY", "GREEN", "GRAY (Retained in Monitor Queue)"),
        ("GREEN", "GREEN", "GREEN", "GREEN (Verified Clean Baseline)")
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

    # ------------------ 4. DEVELOPER HANDOVER ------------------
    add_h1("4. Developer Handover & Enforcement Responsibility")
    p = doc.add_paragraph()
    p.add_run(
        "CDS delivers intelligence and threat categorization. Administrative policy enforcement is executed solely by the game studio:\n"
        "• GREEN: Developer frees the player to continue standard matchmaking.\n"
        "• GRAY: Developer monitors the player (e.g. increase server tickrate to 128Hz, record full demo replay, or place in soft trust-factor matchmaking).\n"
        "• RED: Developer executes disciplinary actions (instant match disconnect, HWID/account ban, or silent quarantine into shadow-lobbies).\n\n"
        "CDS accepts no liability or responsibility for game studio moderation decisions after delivering the classified rosters."
    )

    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    target = os.path.join(r"D:\Project\CDS", "Cheat_Detection_System_Specification.docx")
    create_document(target)
