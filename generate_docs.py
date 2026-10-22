"""
Script to generate the comprehensive Word specification document for the Cheat Detection System (CDS).
Uses python-docx with professional typography, table formatting, and color palettes.
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_document(output_path):
    doc = docx.Document()
    
    # Page setup - 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
    
    # Styles & Colors
    # Primary: Deep Navy (#0F2942), Secondary: Teal Accent (#0284C7), Dark Slate (#1E293B)
    navy_color = RGBColor(15, 41, 66)
    teal_color = RGBColor(2, 132, 199)
    slate_color = RGBColor(30, 41, 59)
    gray_color = RGBColor(100, 116, 139)
    
    # Set default style font
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
    title_run.font.size = Pt(28)
    title_run.font.bold = True
    title_run.font.color.rgb = navy_color

    subtitle_p = doc.add_paragraph()
    subtitle_p.paragraph_format.space_after = Pt(24)
    subtitle_run = subtitle_p.add_run("Next-Generation Multi-Modal Anti-Cheat Architecture & Specification")
    subtitle_run.font.name = 'Arial'
    subtitle_run.font.size = Pt(14)
    subtitle_run.font.color.rgb = teal_color

    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.LEFT
    meta_table.autofit = False
    
    meta_data = [
        ("Document Version:", "1.0.0-PROPOSAL (Engineering Specification)"),
        ("Classification:", "Proprietary & Confidential - Source-Available View-Only"),
        ("Core Architecture:", "3-Tier Hybrid (Passive NLP + Active Anomaly + Agentic Verification)"),
        ("Target Environments:", "Competitive Multiplayer, Real-Time FPS, MOBA, & Battle Royale"),
        ("Date of Publication:", "October 2026")
    ]
    
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c1, c2 = row.cells[0], row.cells[1]
        c1.width = Inches(2.2)
        c2.width = Inches(4.3)
        set_cell_background(c1, "F1F5F9")
        set_cell_background(c2, "F8FAFC")
        set_cell_margins(c1, 80, 80, 120, 120)
        set_cell_margins(c2, 80, 80, 120, 120)
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(k)
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = navy_color
        
        p2 = c2.paragraphs[0]
        r2 = p2.add_run(v)
        r2.font.size = Pt(10)
        r2.font.color.rgb = slate_color

    doc.add_page_break()

    # Helper function for Section Headings
    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(8)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(18)
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
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = teal_color
        return h

    def add_h3(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = slate_color
        return h

    # ------------------ 1. EXECUTIVE SUMMARY ------------------
    add_h1("1. Executive Summary")
    p = doc.add_paragraph()
    p.add_run(
        "The competitive gaming ecosystem is experiencing unprecedented growth, with e-sports viewership and real-money tournament prize pools reaching all-time highs. "
        "However, this exponential expansion is critically undermined by the proliferation of sophisticated cheats—including kernel-level direct memory access (DMA) devices, "
        "AI-assisted computer vision aimbots running on secondary PCs, and stealth memory injection tools. Traditional signature-based anti-cheat mechanisms fail against polymorphic binaries and external hardware cheats.\n\n"
        "The Cheat Detection System (CDS) introduces a revolutionary multi-modal behavioral anti-cheat framework that evaluates player actions and performance telemetry rather than relying solely on invasive client-side scans. "
        "By fusing three decoupled, fault-tolerant analytical layers—Passive NLP Detection, Active Kinematic Anomaly Detection, and External Agentic Multi-Perspective Verification—CDS detects both conventional hacks and undetectable modern hardware cheats with industry-leading precision and near-zero false positive rates."
    )

    # ------------------ 2. PROBLEM STATEMENT & THREAT LANDSCAPE ------------------
    add_h1("2. Problem Statement & Modern Threat Landscape")
    p = doc.add_paragraph()
    p.add_run(
        "Modern cheating technology has evolved far beyond traditional DLL injection or simple Cheat Engine memory modifications. "
        "Today's commercial cheat vendors exploit sophisticated loopholes in operating systems and game engines:"
    )

    threat_table = doc.add_table(rows=5, cols=3)
    threat_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    threat_table.autofit = False

    headers = ["Cheat Attack Vector", "Mechanism of Operation", "Traditional Anti-Cheat Blindspot"]
    for j, h_text in enumerate(headers):
        cell = threat_table.rows[0].cells[j]
        set_cell_background(cell, "0F2942")
        p_cell = cell.paragraphs[0]
        r = p_cell.add_run(h_text)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(10)

    threat_data = [
        ("DMA Hardware Cheats", "PCIe FPGA cards read physical RAM from a secondary PC, bypassing Windows kernel hooks.", "Client kernel drivers see zero suspicious processes or thread hooks on the gaming machine."),
        ("Computer Vision Aimbots", "HDMI capture cards stream display feed to an external machine running YOLO/TensorRT object detection, sending HID mouse inputs.", "Runs completely off-box without modifying game process memory or game executable binaries."),
        ("Micro-Smoothing & Humanized Aim", "Aimbots emulate human hand jitter, Bezier curves, and reaction time distributions.", "Simple threshold filters and standard deviation checks fail to catch smoothed aim corrections."),
        ("Chams & Occlusion ESP", "Network packet sniffing on local proxy or encrypted memory decryption.", "Completely passive reading of unencrypted server updates with no local memory writes.")
    ]

    col_widths = [Inches(1.8), Inches(2.5), Inches(2.2)]
    for i, row in enumerate(threat_data, start=1):
        for j, val in enumerate(row):
            cell = threat_table.rows[i].cells[j]
            cell.width = col_widths[j]
            set_cell_background(cell, "FFFFFF" if i % 2 == 1 else "F8FAFC")
            set_cell_margins(cell, 80, 80, 100, 100)
            p_cell = cell.paragraphs[0]
            r = p_cell.add_run(val)
            r.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_before = Pt(8)

    # ------------------ 3. THE THREE LAYERS OF CDS ARCHITECTURE ------------------
    add_h1("3. The Three Layers of CDS Architecture")
    p = doc.add_paragraph()
    p.add_run(
        "CDS abandons purely reactive client-side memory scanning in favor of a layered behavioral defense. "
        "The three layers operate independently, providing cross-validating evidence before any disciplinary action is taken."
    )

    add_h2("3.1 Layer 1: Passive Detector (NLP & Behavioral Semantics)")
    p = doc.add_paragraph()
    p.add_run(
        "The Passive Detector operates asynchronously and non-intrusively by analyzing unstructured text, user metadata, match chat, and player reporting signals.\n"
        "Key functions include:\n"
    )
    
    doc.add_paragraph(
        "• Natural Language Processing of In-Game Reports: Standard reporting tools suffer from report bombing and tilt-induced false reports. "
        "Layer 1 utilizes fine-tuned BERT/RoBERTa transformers to evaluate report semantics, extracting specific claims (e.g., 'tracking through walls at B site', 'snapped to head 180 degrees') and weighting them against historical reporter credibility scores.",
        style='List Bullet'
    )
    doc.add_paragraph(
        "• In-Game Chat & Intent Mining: Detects admission of cheat usage ('toggled on', 'selling config', 'radar link in bio'), toxic deflection behaviors, and pattern clustering typical of burner/cheater accounts.",
        style='List Bullet'
    )
    doc.add_paragraph(
        "• Sequence-as-Language Tokenization: Translates discrete game events (kill sequences, weapon swaps, target locks, sightline acquirement) into semantic tokens. "
        "Using autoregressive sequence models, Layer 1 computes the perplexity of player action sequences; unnatural bursts of high-improbability decisions generate passive anomaly triggers.",
        style='List Bullet'
    )

    add_h2("3.2 Layer 2: Active Detector (Kinematic Anomaly & Biomechanical Metrics)")
    p = doc.add_paragraph()
    p.add_run(
        "The Active Detector runs on the game server and edge streaming pipelines, processing raw user input telemetry (mouse delta X/Y, tick-rate packet streams, camera angles, FOV vectors) in real-time.\n"
        "Its core algorithms examine the physical and biomechanical feasibility of user movement:"
    )

    doc.add_paragraph(
        "• Angular Jerk & Minimum Jerk Trajectory Validation: Human biological motor control follows Flash & Hogan's Minimum Jerk Principle. "
        "When a human snaps to a target, acceleration and deceleration curves are smooth and bell-shaped. CDS calculates the third derivative of angular position (Jerk). "
        "Synthetic aimbots exhibit instantaneous acceleration, unnatural step functions, or algorithmic micro-corrections lacking muscular inertia.",
        style='List Bullet'
    )
    doc.add_paragraph(
        "• Reaction Time & Visual Latency Bounds: Measures latency between when an enemy hitbox becomes visually rendered/occlusion-cleared and the player's initial angular redirection. "
        "Human visual reaction time rarely drops below 140ms in dynamic scenarios. Sustained sub-100ms or predictive alignment through opaque geometry directly triggers active anomaly alerts.",
        style='List Bullet'
    )
    doc.add_paragraph(
        "• Spatial Occlusion Crosshair Mutual Information: Calculates the statistical correlation between crosshair coordinates and occluded enemy centers-of-mass across walls. "
        "Even when cheaters attempt to hide wallhacks, unconscious crosshair tracking of unseen targets produces high mutual information values over extended rounds.",
        style='List Bullet'
    )

    add_h2("3.3 Layer 3: External Verification (Agentic Autonomous AI Review)")
    p = doc.add_paragraph()
    p.add_run(
        "When Layer 1 and/or Layer 2 flag an anomaly score exceeding predefined risk thresholds (e.g., Risk > 0.70), "
        "the match replay segment is extracted and routed to Layer 3: the External Agentic Verification System. "
        "Inspired by multi-agent reasoning, Layer 3 utilizes specialized AI evaluation agents that analyze the match from multiple perspectives:"
    )

    agent_table = doc.add_table(rows=4, cols=2)
    agent_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    agent_table.autofit = False

    agent_headers = ["Specialized AI Agent", "Responsibilities & Verification Scope"]
    for j, h_text in enumerate(agent_headers):
        cell = agent_table.rows[0].cells[j]
        set_cell_background(cell, "0284C7")
        p_cell = cell.paragraphs[0]
        r = p_cell.add_run(h_text)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(10)

    agent_data = [
        ("Kinematic Inspector Agent", "Re-simulates the mouse vectors in an isolated physics engine sandbox. Detects input spoofing, mouse event injection flags, and synthetic hardware emulation artifacts."),
        ("Spatial & Audio Context Agent", "Checks whether the suspect player had valid game sensory inputs: teammate voice callouts, radar pings, audio footsteps, bullet tracer origin, or grenade bounces that explain the engagement."),
        ("Verdict Arbiter Agent (Consensus)", "Weighs evidence from all agents, computes a Final Confidence Index (0% to 100%), generates an explainable natural-language dossier, and triggers automated quarantine or human moderator escalation.")
    ]

    for i, row in enumerate(agent_data, start=1):
        for j, val in enumerate(row):
            cell = agent_table.rows[i].cells[j]
            cell.width = Inches(2.2) if j == 0 else Inches(4.3)
            set_cell_background(cell, "FFFFFF" if i % 2 == 1 else "F8FAFC")
            set_cell_margins(cell, 80, 80, 100, 100)
            p_cell = cell.paragraphs[0]
            r = p_cell.add_run(val)
            r.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_before = Pt(8)

    # ------------------ 4. SYSTEM WORKFLOW & ACTION MATRIX ------------------
    add_h1("4. Decision Matrix & Action Workflow")
    p = doc.add_paragraph()
    p.add_run(
        "To ensure that legitimate skilled players (e.g., esports professionals, smurf accounts) are never falsely penalized, "
        "CDS employs a tiered confidence resolution framework:"
    )

    action_table = doc.add_table(rows=5, cols=4)
    action_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    action_table.autofit = False

    act_headers = ["Confidence Score", "Risk Tier", "Automated Action", "Human Review Trigger"]
    for j, h_text in enumerate(act_headers):
        cell = action_table.rows[0].cells[j]
        set_cell_background(cell, "0F2942")
        p_cell = cell.paragraphs[0]
        r = p_cell.add_run(h_text)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9.5)

    act_data = [
        ("0% - 49%", "Nominal / Normal", "No action. Telemetry archived for periodic model baseline training.", "None."),
        ("50% - 74%", "Elevated Suspicion", "Increase server tick telemetry sampling rate (from 20Hz to 128Hz); initiate passive replay buffer recording.", "Automated logging in watch-list."),
        ("75% - 89%", "High Anomaly", "Silent shadow-matchmaking (suspect placed in cheater pool); route incident dossier to moderation dashboard.", "Dispatched to human anti-cheat team with auto-compiled video & telemetry clips."),
        ("90% - 100%", "Definite Exploit", "Instant match termination or in-game neutralization (damage nullification); hardware / account ban enforced.", "Automated post-ban audit trail generated with 99.99% certainty proof.")
    ]

    act_widths = [Inches(1.2), Inches(1.4), Inches(2.3), Inches(1.6)]
    for i, row in enumerate(act_data, start=1):
        for j, val in enumerate(row):
            cell = action_table.rows[i].cells[j]
            cell.width = act_widths[j]
            set_cell_background(cell, "FFFFFF" if i % 2 == 1 else "F8FAFC")
            set_cell_margins(cell, 80, 80, 90, 90)
            p_cell = cell.paragraphs[0]
            r = p_cell.add_run(val)
            r.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_before = Pt(12)

    # ------------------ 5. ARCHITECTURAL CRITIQUE & IMPROVEMENT ROADMAP ------------------
    add_h1("5. Architecture Analysis, Critique & Recommended Improvements")
    p = doc.add_paragraph()
    p.add_run(
        "A rigorous review of the original concept outlined in the preliminary notes highlights several vital technical areas "
        "that must be engineered to make CDS production-ready in commercial deployments:"
    )

    add_h2("5.1 Addressing Smurfing vs. Cheating Ambiguity")
    p = doc.add_paragraph()
    p.add_run(
        "Critical Flaw in Simple Anomaly Models: Highly skilled veteran players playing on new accounts (smurfs) consistently beat average player metrics by wide margins. "
        "Standard statistical anomaly models often misidentify high headshot ratios and rapid flick shots as aimbots.\n"
        "CDS Resolution: Differentiate skill from automation by analyzing human imperfection metrics. Skilled humans exhibit micro-overshoots followed by corrective saccades, "
        "whereas aimbots—even smoothed ones—exhibit non-biological linear damping. CDS incorporates a dedicated Smurf Disambiguation Classifier."
    )

    add_h2("5.2 Privacy & Chat Telemetry Compliance (GDPR / CCPA)")
    p = doc.add_paragraph()
    p.add_run(
        "Handling raw player chat text raises compliance obligations under GDPR, CCPA, and COPPA. "
        "CDS resolves this by applying Client-Side Token Anonymization and Differential Privacy. Chat messages are pseudonymized, stripped of Personally Identifiable Information (PII), "
        "and converted into semantic embedding vectors before being transmitted to the central intelligence cloud."
    )

    add_h2("5.3 Adversarial Machine Learning & Evasion Resistance")
    p = doc.add_paragraph()
    p.add_run(
        "Cheat authors actively attempt to train adversarial neural networks to find blindspots in machine learning detectors (e.g., adding Perlin noise to aimbot vectors). "
        "To counter this, CDS employs Adversarial Training loops where simulated synthetic cheats continually stress-test the active detection models during continuous integration (CI) builds."
    )

    add_h2("5.4 Edge vs. Cloud Latency Partitioning")
    p = doc.add_paragraph()
    p.add_run(
        "Running heavy transformer models synchronously during 128-tick server frames causes intolerable tick lag. "
        "CDS partitions compute into three decoupled tiers:\n"
        "1. In-Engine Lightweight Ring Buffer (<1ms overhead): Computes instant Jerk and angular velocity metrics directly in the game server loop.\n"
        "2. Stream Processing Pipeline (10-50ms latency): Kafka + Flink pipeline that processes sliding time-series telemetry windows.\n"
        "3. Cloud Agentic Evaluation (Asynchronous, 5-30s turnaround): Multi-agent replay analysis triggered on demand without impacting server performance."
    )

    # ------------------ 6. TECHNOLOGY STACK & DEPLOYMENT ------------------
    add_h1("6. Recommended Technology Stack")
    p = doc.add_paragraph()
    p.add_run("The CDS platform is architected with modern, high-performance distributed technologies:")

    stack_table = doc.add_table(rows=6, cols=3)
    stack_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    stack_table.autofit = False

    stack_headers = ["Subsystem Component", "Recommended Technology", "Architectural Rationale"]
    for j, h_text in enumerate(stack_headers):
        cell = stack_table.rows[0].cells[j]
        set_cell_background(cell, "0F2942")
        p_cell = cell.paragraphs[0]
        r = p_cell.add_run(h_text)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9.5)

    stack_data = [
        ("Server Telemetry Agent", "Rust / C++ SDK", "Ultra-low memory footprint, zero garbage collection pauses, SIMD vectorization for real-time kinematics."),
        ("Event Ingestion Pipeline", "Apache Kafka + Apache Flink", "Processes millions of concurrent player ticks per second with sub-5ms streaming window calculations."),
        ("Anomaly Inference Engine", "ONNX Runtime / TensorRT", "Hardware-accelerated model serving enabling microsecond inference for high-frequency player kinematic states."),
        ("Agentic Verification Engine", "Python / LangGraph / vLLM", "Orchestrates multi-agent reflection loops, spatial game state reasoning, and automated dossier synthesis."),
        ("Data Lake & Feature Store", "ClickHouse + Feast", "ClickHouse columnar storage delivers lightning-fast SQL queries across billions of historical match ticks.")
    ]

    for i, row in enumerate(stack_data, start=1):
        for j, val in enumerate(row):
            cell = stack_table.rows[i].cells[j]
            cell.width = [Inches(1.8), Inches(2.2), Inches(2.5)][j]
            set_cell_background(cell, "FFFFFF" if i % 2 == 1 else "F8FAFC")
            set_cell_margins(cell, 80, 80, 100, 100)
            p_cell = cell.paragraphs[0]
            r = p_cell.add_run(val)
            r.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_before = Pt(14)

    # ------------------ 7. CONCLUSION & NEXT STEPS ------------------
    add_h1("7. Conclusion & Phased Implementation Plan")
    p = doc.add_paragraph()
    p.add_run(
        "The Cheat Detection System (CDS) represents a paradigm shift in game security. By shifting the defensive perimeter from vulnerable client-side memory scanning "
        "to intelligent, behavioral multi-modal verification, CDS permanently solves the existential threat posed by external hardware and computer-vision cheats.\n\n"
        "Phase 1 (Month 1-3): Telemetry Ingestion Prototype & Rust Server SDK development.\n"
        "Phase 2 (Month 4-6): Active Kinematic Model Training (Minimum Jerk & Angular Variance).\n"
        "Phase 3 (Month 7-9): Passive NLP Pipeline & Match Report Sentiment Analyzer.\n"
        "Phase 4 (Month 10-12): Agentic Verification Multi-Agent Arbiter & Pilot Matchmaking Integration."
    )

    # Save document
    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    target = os.path.join(r"D:\Project\CDS", "Cheat_Detection_System_Specification.docx")
    create_document(target)
