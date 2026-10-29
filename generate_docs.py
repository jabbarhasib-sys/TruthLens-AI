import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def create_truthlens_interview_doc():
    doc = Document()

    # Set page margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Style definitions
    # Primary Palette: Deep Forest Emerald #064E3B, Teal #0D9488, Slate Charcoal #1F2937, Accent #10B981
    CLR_PRIMARY = RGBColor(0x06, 0x4E, 0x3B)
    CLR_SECONDARY = RGBColor(0x0F, 0x76, 0x6E)
    CLR_BODY = RGBColor(0x37, 0x41, 0x51)
    CLR_DARK = RGBColor(0x11, 0x18, 0x27)
    CLR_MUTED = RGBColor(0x6B, 0x72, 0x80)

    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def add_callout(title, text, border_color="0D9488", bg_color="F0FDF4"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.9)
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'  <w:left w:val="single" w:sz="36" w:space="0" w:color="{border_color}"/>'
            f'  <w:top w:val="none"/>'
            f'  <w:right w:val="none"/>'
            f'  <w:bottom w:val="none"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        r_title = p.add_run(f"📌 {title}\n")
        r_title.bold = True
        r_title.font.name = "Arial"
        r_title.font.size = Pt(10.5)
        r_title.font.color.rgb = CLR_SECONDARY
        
        r_text = p.add_run(text)
        r_text.font.name = "Calibri"
        r_text.font.size = Pt(10)
        r_text.font.color.rgb = CLR_BODY

    def add_interview_qa(q_num, question, answer_in_my_words, technical_deep_dive, follow_up_tip=None):
        # Container table for clear visual Q&A card
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.9)
        set_cell_background(cell, "FAFAFA")
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="0F766E"/>'
            f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="E5E7EB"/>'
            f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="E5E7EB"/>'
            f'  <w:bottom w:val="single" w:sz="12" w:space="0" w:color="D1D5DB"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        
        # Question Header
        r_q_tag = p.add_run(f"Q{q_num}: ")
        r_q_tag.bold = True
        r_q_tag.font.name = "Arial"
        r_q_tag.font.size = Pt(11)
        r_q_tag.font.color.rgb = CLR_SECONDARY
        
        r_q = p.add_run(f"{question}\n\n")
        r_q.bold = True
        r_q.font.name = "Arial"
        r_q.font.size = Pt(11)
        r_q.font.color.rgb = CLR_DARK
        
        # In My Words section
        r_ans_tag = p.add_run("🗣️ How to Answer in Your Own Words (Natural Interview Response):\n")
        r_ans_tag.bold = True
        r_ans_tag.font.name = "Calibri"
        r_ans_tag.font.size = Pt(10.5)
        r_ans_tag.font.color.rgb = RGBColor(0x06, 0x5F, 0x46)
        
        r_ans = p.add_run(f"\"{answer_in_my_words}\"\n\n")
        r_ans.italic = True
        r_ans.font.name = "Calibri"
        r_ans.font.size = Pt(10)
        r_ans.font.color.rgb = CLR_DARK
        
        # Technical Deep-Dive
        r_tech_tag = p.add_run("⚙️ Under-The-Hood Technical Details (To Impress Senior Interviewers):\n")
        r_tech_tag.bold = True
        r_tech_tag.font.name = "Calibri"
        r_tech_tag.font.size = Pt(10)
        r_tech_tag.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
        
        r_tech = p.add_run(f"{technical_deep_dive}\n")
        r_tech.font.name = "Calibri"
        r_tech.font.size = Pt(9.5)
        r_tech.font.color.rgb = CLR_BODY
        
        if follow_up_tip:
            r_tip_tag = p.add_run("\n🎯 Pro-Tip / Trap to Avoid: ")
            r_tip_tag.bold = True
            r_tip_tag.font.name = "Calibri"
            r_tip_tag.font.size = Pt(9.5)
            r_tip_tag.font.color.rgb = RGBColor(0x99, 0x1B, 0x1B)
            
            r_tip = p.add_run(follow_up_tip)
            r_tip.font.name = "Calibri"
            r_tip.font.size = Pt(9.5)
            r_tip.font.color.rgb = CLR_DARK
            
        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_before = Pt(0)
        p_space.paragraph_format.space_after = Pt(4)

    def format_row(row, bg_hex, text_color_rgb, is_header=False):
        for cell in row.cells:
            set_cell_background(cell, bg_hex)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                for r in p.runs:
                    r.font.name = "Arial" if is_header else "Calibri"
                    r.font.size = Pt(9.5) if is_header else Pt(9.5)
                    r.bold = is_header
                    r.font.color.rgb = text_color_rgb

    def style_table(table, col_widths, header_bg="047857"):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        format_row(table.rows[0], header_bg, RGBColor(0xFF, 0xFF, 0xFF), is_header=True)
        for i, row in enumerate(table.rows[1:]):
            bg = "F9FAFB" if i % 2 == 0 else "FFFFFF"
            format_row(row, bg, CLR_DARK, is_header=False)
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = width

    def add_h1(text):
        h = doc.add_heading(level=1)
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(15)
        r.bold = True
        r.font.color.rgb = CLR_PRIMARY
        return h

    def add_h2(text):
        h = doc.add_heading(level=2)
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(12.5)
        r.bold = True
        r.font.color.rgb = CLR_SECONDARY
        return h

    def add_h3(text):
        h = doc.add_heading(level=3)
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(3)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.bold = True
        r.font.color.rgb = CLR_DARK
        return h

    def add_body(text, bold_prefix=None, space_after=4):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10.5)
            r_pre.bold = True
            r_pre.font.color.rgb = CLR_DARK
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.color.rgb = CLR_BODY
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10.5)
            r_pre.bold = True
            r_pre.font.color.rgb = CLR_DARK
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.color.rgb = CLR_BODY
        return p

    # ══════════════════════════════════════════════════════════════════════════
    # COVER / HEADER
    # ══════════════════════════════════════════════════════════════════════════
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(4)
    r_main = p_title.add_run("🔍 TruthLens AI — Complete Project & Interview Master Guide")
    r_main.font.name = "Arial"
    r_main.font.size = Pt(22)
    r_main.bold = True
    r_main.font.color.rgb = CLR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run("Full Architecture Breakdown · Multi-Modal Content Authentication Pipeline · 360° Interview Q&A Cheatsheet")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = CLR_SECONDARY

    add_callout(
        "Candidate Quick-Start Briefing (Read This 10 Minutes Before Interview)",
        "TruthLens AI is an end-to-end, multi-modal content authentication and fact-checking platform. "
        "It solves the problem of online fake news and deepfakes by aggregating multi-source signals (Google Fact Check, "
        "NewsAPI, GDELT, Hive Moderation AI, Google Cloud Vision, EXIF forensics, and Perceptual dHash) into a "
        "deterministic Trust Engine v3 that calculates a transparent 0-100 Trust Score with confidence margins, supplemented "
        "by Groq Llama-3.1-70B for explainable markdown audits. If asked what you built, summarize it as: "
        "'A real-time multi-modal misinformation detection system combining heuristic forensic engines with GenAI reasoning.'"
    )

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1: WHAT YOU HAVE BUILT (THE 30,000-FT OVERVIEW)
    # ══════════════════════════════════════════════════════════════════════════
    add_h1("1. Executive Summary: What You Built & The Core Problem Solved")
    add_body(
        "TruthLens AI is an enterprise-grade web platform and verification API designed to detect misinformation, "
        "synthetic media (deepfakes), and unverified claims circulating on social networks and news websites. "
        "In modern media environments, manual fact-checking takes hours or days, by which time viral hoaxes and "
        "AI-generated imagery have already caused social panic, reputational damage, or election interference."
    )
    add_body(
        "To solve this latency and accuracy dilemma, TruthLens AI introduces a hybrid verification pipeline: "
        "it pairs fast, deterministic heuristics and multi-vendor API signals with high-order generative AI reasoning. "
        "Users can submit either a textual claim (or news URL) or upload an image. Within 1.5 to 3 seconds, the system "
        "computes a multi-dimensional Trust Score (0–100), categorizes risk (LOW, MEDIUM, HIGH, CRITICAL), outputs confidence "
        "intervals, and delivers a comprehensive forensic audit report with verified citations."
    )

    add_h2("High-Level System Pillars")
    add_bullet(" Accepts raw statements, sensational headlines, or article URLs (via BeautifulSoup scraper), decomposes them into atomic claims, and cross-references Google Fact Check Tools API, NewsAPI, MediaStack, and GDELT Global Event Database.", "1. Real-Time News Claim Verification:")
    add_bullet(" Runs a multi-stage forensic pipeline on uploaded images (EXIF metadata inspection, software fingerprinting, Google Cloud Vision Spoof detection, Hive Moderation AI deepfake analysis, and Difference Hashing/dHash for viral deduplication).", "2. Deepfake & Image Authenticity Forensics:")
    add_bullet(" A proprietary 20+ signal weighted mathematical model that synthesizes API consensus, emotional tone (fear/outrage markers), source reputation, and forensic penalties into a defensible Trust Score.", "3. Trust Engine v3 (Scoring Algorithm):")
    add_bullet(" Integrated Groq Llama 3.1 70B Versatile model to generate natural-language investigative reports breaking down discrepancies, source citations, and recommendations.", "4. Generative AI Reasoning & Audit Trail:")
    add_bullet(" Next.js 15 App Router frontend featuring dark glassmorphism, glowing risk badges, interactive radar breakdowns, and permalink reports backed by FastAPI, SQLite/PostgreSQL, and Redis caching.", "5. Full-Stack Modern Architecture:")

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2: END-TO-END SYSTEM ARCHITECTURE & TECH STACK
    # ══════════════════════════════════════════════════════════════════════════
    add_h1("2. Full-Stack System Architecture & Technology Stack")
    add_body(
        "TruthLens AI is structured as a decoupled client-server micro-architecture. "
        "The frontend communicates asynchronously with the FastAPI backend through JSON REST endpoints, "
        "utilizing persistent connection pools and resilient fallback states."
    )

    add_h2("Technology Stack Breakdown")
    tech_table = doc.add_table(rows=12, cols=3)
    tech_widths = [Inches(1.8), Inches(2.2), Inches(2.9)]
    
    tech_data = [
        ["Layer / Component", "Technology / Library", "Role & Engineering Justification"],
        ["Frontend Framework", "Next.js 15 (React 19, App Router)", "Server-side rendering, dynamic routing (/report/[id]), modern reactive state."],
        ["Frontend Styling", "Tailwind CSS + shadcn/ui", "Dark glassmorphism design system, responsive HUD, neon accents."],
        ["Backend Framework", "FastAPI (Python 3.11+)", "High throughput async I/O, automatic OpenAPI /docs, Pydantic validation."],
        ["Database & ORM", "SQLAlchemy 2.0 + SQLite / PostgreSQL", "Relational persistence for user accounts and audit reports with JSON payloads."],
        ["Caching & Deduplication", "Redis + In-Memory LRU (500 entries)", "Prevents redundant third-party API costs and speeds up viral claims/images."],
        ["Async HTTP Client", "httpx (AsyncClient)", "Persistent HTTP/2 connection pooling with exponential back-off retries."],
        ["LLM Reasoning", "Groq API (Llama 3.1 70B Versatile)", "Ultra-low latency inference (300+ tok/s) for structured investigative audits."],
        ["Image Forensics", "Pillow (PIL) + custom EXIF parser", "Extraction of camera make, model, shutter, GPS coordinates, editing tags."],
        ["Deepfake AI", "Hive Moderation AI REST API", "Computer vision model scoring AI-generation, manipulation, and facial spoofing."],
        ["Computer Vision", "Google Cloud Vision API", "SafeSearch spoof detection and Web Detection (reverse image search)."],
        ["User Security", "PyJWT + bcrypt (12 rounds)", "Stateless bearer token authentication, OAuth2 password flow, RBAC (user/admin)."],
    ]
    for r_idx, row in enumerate(tech_table.rows):
        for c_idx, val in enumerate(tech_data[r_idx]):
            row.cells[c_idx].paragraphs[0].text = val
    style_table(tech_table, tech_widths, header_bg="064E3B")

    add_h2("System Data Flow Architecture")
    add_body("Below is the chronological sequence of operations during an end-to-end verification request:")
    add_bullet(" Client issues a POST request to /api/verify/news or /api/verify/image.", "Step 1 (Ingestion):")
    add_bullet(" Checks Redis / local memory cache via query hash or image dHash. If a match exists, results return in <10ms.", "Step 2 (Cache Check):")
    add_bullet(" Concurrently dispatches requests via httpx.AsyncClient to Google Fact Check, NewsAPI, MediaStack, and GDELT. For images, launches EXIF parser, Hive API, and Google Vision.", "Step 3 (Concurrent Gathering):")
    add_bullet(" Raw API outputs feed into Trust Engine v3. Linguistic red flags, source variety, and forensic signals modify the base score (+/- points).", "Step 4 (Trust Scoring):")
    add_bullet(" Extracted evidence and scores are formatted into a prompt sent to Groq Llama 3.1 70B, which returns an objective audit report in Markdown.", "Step 5 (LLM Synthesis):")
    add_bullet(" Complete analysis saved to database with unique UUID. JSON response sent to client to render rich dashboard.", "Step 6 (Persistence & Delivery):")

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3: IN-DEPTH CONTENT AUTHENTICATION METHODOLOGIES
    # ══════════════════════════════════════════════════════════════════════════
    add_h1("3. Comprehensive Content Authentication: What & How It's Done")
    add_body(
        "Content authentication in TruthLens AI is divided into two distinct forensic domains: "
        "(A) Textual & News Claim Authentication, and (B) Visual & Image Forensics."
    )

    add_h2("A. Textual Claim & News Authentication Pipeline")
    add_bullet(" Accepts live web links (e.g. from BBC, Twitter/X, CNN, or blogs). The url_scraper.py module validates URLs, extracts the core body while stripping HTML/script boilerplate, and isolates key claims.", "1. Web Article Extraction & URL Scraper:")
    add_bullet(" Complex compound sentences are broken down into atomic assertions using the Groq Llama service, allowing the engine to fact-check individual claims independently rather than muddling multi-part assertions.", "2. Claim Decomposition:")
    add_bullet(" Queries Google Fact Check Tools API to find previous reviews by accredited IFCN (International Fact-Checking Network) signatories like PolitiFact, Snopes, FactCheck.org, and AFP. If a false rating is found, the system immediately applies a heavy -45 pt penalty.", "3. Authoritative Fact-Check Cross-Referencing:")
    add_bullet(" Concurrently queries NewsAPI, MediaStack, and GDELT (Global Database of Events, Language, and Tone). Verifies whether mainstream news outlets corroborate the story. Coverage in 5+ independent reputable outlets yields a +20 pt bonus, while zero coverage for an extraordinary claim penalizes -20 pts.", "4. Multi-Source News Corroboration:")
    add_bullet(" Scans claim text for known medical hoaxes (e.g., 'cures cancer', 'bleach cure', 'vaccine microchip') and political conspiracy markers (e.g., 'stolen election', 'deep state', 'plandemic').", "5. Misinformation Pattern Matching:")
    add_bullet(" Parses sensationalist clickbait markers ('you won't believe', 'hidden truth', 'they don't want you to know') and absolute unverifiable statements ('100% proven', 'miracle remedy').", "6. Linguistic Red Flags & Clickbait Heuristics:")
    add_bullet(" Uses entity_service.py to extract named organizations (WHO, CDC, NASA, Reuters), dates, and percentages. Checks if a quote has valid attribution or if prestigious institutions are being falsely cited.", "7. Named Entity & Citation Extraction:")
    add_bullet(" Analyzes emotional manipulation through regex libraries detecting fear-mongering, outrage bait, aggressive ALL-CAPS usage, and multiple exclamation marks.", "8. Emotional Tone Analysis:")

    add_h2("B. Visual & Image Authenticity Forensics Pipeline")
    add_bullet(" Extracts Exchangeable Image File Format (EXIF) tags from file headers. Checks for Camera Make, Model, Lens, Focal Length, Exposure, and capture timestamp. Legitimate camera metadata adds +15 pts. Geolocation coordinates (GPS Latitude/Longitude) yield +8 pts.", "1. EXIF Metadata Forensics:")
    add_bullet(" Scans the 'Software' tag inside image metadata. If tools like Adobe Photoshop, GIMP, or Canva are detected, a -20 pt penalty is applied. If EXIF data has been completely stripped (common when reposting or concealing origin), a -12 pt penalty is applied.", "2. Software Fingerprinting & Stripping Detection:")
    add_bullet(" Connects to Hive Moderation AI's computer vision neural networks. Generates precise percentage confidence across three classes: ai_generated, manipulated (spliced/faceswapped), and original. Scores above 30% AI trigger heavy deductions (-55 × probability).", "3. Deepfake & Synthetic Generation Detection (Hive AI):")
    add_bullet(" Uses Google Cloud Vision SafeSearch to detect spoofed/satirical imagery and Web Detection to trace identical or visually similar images across the web, identifying original publish dates and debunk articles.", "4. Reverse Image & Spoof Detection (Google Cloud Vision):")
    add_bullet(" Converts uploaded images to grayscale, resizes them to 9x8 pixels, and computes adjacent horizontal pixel gradient gradients into a 64-bit hex hash. If an identical or slightly recompressed viral image is uploaded again, hamming distance matching allows instant cache retrieval without paying for external APIs.", "5. Perceptual Hashing (dHash) & Viral Deduplication:")

    add_h2("Scoring Signal Matrix (Trust Engine v3)")
    engine_table = doc.add_table(rows=14, cols=4)
    engine_widths = [Inches(2.0), Inches(1.3), Inches(1.2), Inches(2.4)]
    
    engine_data = [
        ["Signal Name", "Domain", "Impact / Weight", "Forensic Rationale"],
        ["False Fact-Check Rating", "News", "-45 pts", "Official debunk by IFCN verified fact-checker (Snopes, PolitiFact)."],
        ["True Fact-Check Rating", "News", "+25 pts", "Verified true by accredited investigative body."],
        ["Medical Misinformation Pattern", "News", "-20 pts per match", "Dangerous unverified health cure claim (COVID/Cancer)."],
        ["Sensational / Clickbait Phrasing", "News", "-6 pts (cap -24)", "Urgent, alarmist phrasing designed to drive viral clicks."],
        ["Zero Mainstream News Coverage", "News", "-20 pts", "Claim has no corroboration across global news wire services."],
        ["5+ Corroborating News Outlets", "News", "+20 pts", "Broad journalistic consensus and reporting."],
        ["Authoritative Source Citation", "News", "+8 pts", "Explicit attribution to NASA, WHO, CDC, Reuters, BBC."],
        ["Hive AI: AI-Generated (>30%)", "Image", "-55 × prob", "Deep neural net classifies image as synthetic (Midjourney/Flux)."],
        ["Hive AI: Manipulated (>30%)", "Image", "-45 × prob", "Image splicing, cloning, or face-swap tampering detected."],
        ["Full Camera EXIF (Make/Model)", "Image", "+15 pts", "Presence of physical optical hardware capture signature."],
        ["Editing Software in Metadata", "Image", "-20 pts", "Photoshop/GIMP detected in software metadata headers."],
        ["Missing / Stripped EXIF Data", "Image", "-12 pts", "Metadata removed, typical of web recompression or obfuscation."],
        ["Google Vision Spoof Rating", "Image", "-25 pts", "Google SafeSearch model flagged image as visual spoof."],
    ]
    for r_idx, row in enumerate(engine_table.rows):
        for c_idx, val in enumerate(engine_data[r_idx]):
            row.cells[c_idx].paragraphs[0].text = val
    style_table(engine_table, engine_widths, header_bg="0F766E")

    add_body(
        "Risk Classification Thresholds: Scores 75-100 are marked LOW RISK (Credible); "
        "50-74 are MEDIUM RISK (Uncertain); 25-49 are HIGH RISK (Suspicious); and 0-24 are CRITICAL RISK (Likely Misinformation)."
    )

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4: USER AUTHENTICATION & SECURITY ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════════════
    add_h1("4. User Authentication, Authorization & Security Architecture")
    add_body(
        "TruthLens AI implements a robust, stateless security subsystem compliant with modern OAuth2 and JWT standards. "
        "This protects user verification histories and administrative controls."
    )
    add_bullet(" Passwords are never stored in plaintext. They are salted and hashed using bcrypt with a configurable work factor (default 12 rounds in app/core/security.py), protecting against rainbow table attacks.", "1. Password Hashing (bcrypt):")
    add_bullet(" Upon successful login, the server issues a JSON Web Token signed with HMAC-SHA256 (HS256) and a secret key. Tokens carry expiration timestamps (exp) and subject emails (sub).", "2. Stateless JWT Tokens:")
    add_bullet(" The FastAPI backend provides standard JSON login (/api/auth/login) as well as OAuth2PasswordRequestForm compatibility (/api/auth/login-oauth) for interactive API documentation exploration.", "3. Dual Authentication Flow:")
    add_bullet(" FastAPI dependency injection (get_current_user) intercepts incoming bearer tokens in HTTP Authorization headers, validates signatures, checks expiration, and retrieves user records.", "4. Request Authentication Dependency:")
    add_bullet(" User models include role fields ('user' vs 'admin'). Privileged routes (/api/admin/users) enforce role checks via _require_admin helper, preventing unauthorized elevation of privilege.", "5. Role-Based Access Control (RBAC):")
    add_bullet(" Public users can verify news claims anonymously without logging in. However, logged-in users have analyses automatically linked to their profile (user_id foreign key) for historical tracking.", "6. Anonymous vs. Authenticated Dual Modes:")

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5: MASTER INTERVIEW Q&A PREPARATION
    # ══════════════════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_h1("5. Master Interview Q&A Cheatsheet (With 'In My Own Words' Scripts)")
    add_body(
        "This section prepares you for any interview scenario—from casual HR screens to grilling by Principal Engineers. "
        "Each question includes a conversational, authentic script you can say in your own words, backed by the deep technical explanation."
    )

    # Question 1
    add_interview_qa(
        q_num=1,
        question="Can you tell me about your TruthLens AI project? What inspired you to build it?",
        answer_in_my_words=(
            "I built TruthLens AI to solve the growing problem of online misinformation and deepfakes. "
            "Right now, fact-checking is either too slow—taking days for manual journalism—or completely black-box. "
            "I wanted to build a platform where someone can paste a news link or upload an image and get an instant, "
            "transparent Trust Score from 0 to 100 with clear evidence. "
            "I engineered a multi-stage backend using FastAPI that combines external fact-checking APIs, computer vision "
            "forensics, and Groq's Llama 3.1 LLM to give both a mathematical score and an explainable audit report."
        ),
        technical_deep_dive=(
            "Highlight the multi-modal nature of the platform (text claims, URLs, and image forensics). "
            "Mention the tech stack: FastAPI, Next.js 15, SQLAlchemy, Redis, and Groq Llama 3.1. "
            "Explain that you implemented Trust Engine v3, which combines over 20 heuristic and API signals."
        ),
        follow_up_tip="Don't just say 'it uses AI'. Emphasize that the AI is only one part—the deterministic forensic scoring engine prevents LLM hallucinations."
    )

    # Question 2
    add_interview_qa(
        q_num=2,
        question="How does your Trust Score algorithm work? How do you prevent biased or arbitrary numbers?",
        answer_in_my_words=(
            "Our Trust Engine v3 doesn't just guess or rely on an LLM to spit out a number—it uses a deterministic, "
            "weighted scoring model. For news claims, we start at a neutral baseline of 50. Then we add or subtract "
            "points based on concrete evidence: if an accredited IFCN fact-checker like Snopes or PolitiFact already debunked it, "
            "that's an immediate -45 point penalty. If five or more reputable news outlets corroborate the story, we add +20 points. "
            "We also penalize sensationalist clickbait language and medical misinformation patterns. "
            "For images, we inspect EXIF metadata, camera hardware tags, editing software signatures, and run Hive AI deepfake detection. "
            "Every score also produces a confidence interval based on how many APIs agreed."
        ),
        technical_deep_dive=(
            "Point to `app/services/trust_engine.py`. News base = 50.0, Image base = 60.0. "
            "Show how deductions (e.g. `_W_FALSE_FACTCHECK = 45.0`, `_W_MEDICAL_MISINFO = -20.0`) and bonuses "
            "(e.g. `_W_SOURCE_VARIETY_5 = 8.0`, `_W_FULL_EXIF = 15.0`) are tracked in an audit ledger. "
            "The final score is clamped between 0 and 100."
        ),
        follow_up_tip="If they ask why you start at 50, explain that an unverified claim is neutral until corroborating or debunking evidence is discovered."
    )

    # Question 3
    add_interview_qa(
        q_num=3,
        question="How do you verify images and detect AI deepfakes?",
        answer_in_my_words=(
            "We use a defense-in-depth visual pipeline that analyzes an image on three distinct levels: "
            "metadata forensics, computer vision AI, and perceptual hashing. "
            "First, we parse the raw EXIF headers to check if the image has genuine camera hardware attributes like lens type "
            "and GPS coordinates, or if the metadata flags software like Photoshop or Midjourney. "
            "Second, we send the image to Hive Moderation AI, which analyzes pixel patterns and produces probability scores "
            "for whether the image is AI-generated, manipulated, or original. "
            "Third, we use Difference Hashing (dHash). When an image is uploaded, we calculate its 64-bit perceptual hash. "
            "If that exact fake image goes viral and hundreds of users upload it, we can instantly retrieve the cached verdict "
            "in milliseconds using Hamming distance without re-calling expensive external APIs."
        ),
        technical_deep_dive=(
            "Reference `image_service.py` and `calculate_dhash`. dHash scales image to 9x8 grayscale, computes relative pixel differences, "
            "and generates hex string. Mention Hive AI (`https://api.thehive.ai/api/v2/task/sync`) and Google Cloud Vision SafeSearch spoof detection."
        ),
        follow_up_tip="Mention that social media platforms often strip EXIF data; explain that's why TruthLens applies a moderate penalty for missing EXIF but relies on Hive AI for the actual pixel-level deepfake verdict."
    )

    # Question 4
    add_interview_qa(
        q_num=4,
        question="What is the role of the LLM (Groq Llama 3.1) in this project? Why not use it for everything?",
        answer_in_my_words=(
            "That was an intentional architectural decision. If you ask an LLM 'is this claim true?', it can hallucinate, "
            "suffer from knowledge cutoff, or introduce bias. "
            "In TruthLens AI, the LLM is NOT the primary judge; it is an investigative synthesiser and explainer. "
            "Our Python backend gathers real-time facts from Google Fact Check, NewsAPI, and GDELT, and computes the mathematical Trust Score. "
            "We then pass those concrete findings into Groq running Llama 3.1 70B with a strict prompt: synthesize these verified "
            "data points into a clean, human-readable markdown audit with executive summaries, discrepancies, and citations. "
            "We also use Groq's high speed for claim decomposition—breaking complex compound sentences into testable sub-claims."
        ),
        technical_deep_dive=(
            "Groq's LPU hardware delivers over 300 tokens/second, keeping overall latency under 2 seconds. "
            "In `groq_service.py`, httpx.AsyncClient is kept as a persistent singleton with exponential back-off retries on HTTP 429/500."
        ),
        follow_up_tip="Interviewers love this answer because it proves you understand the limitations of LLMs and how to build reliable hybrid AI systems."
    )

    # Question 5
    add_interview_qa(
        q_num=5,
        question="How does authentication and user management work in TruthLens AI?",
        answer_in_my_words=(
            "We implemented a stateless JWT authentication system following OAuth2 standards. "
            "When a user signs up, their password is encrypted using bcrypt with 12 rounds of salt before saving to SQLite or PostgreSQL. "
            "On login, the server verifies the password and issues a signed JSON Web Token with a configurable expiration time. "
            "Our FastAPI endpoints use dependency injection to protect routes like user profile updates and report history. "
            "We also built role-based access control (RBAC): regular users can view and manage their own past verifications, "
            "while admin users have access to admin endpoints to manage users and view system metrics. "
            "Furthermore, analyses can be run anonymously, but if an authenticated user runs an analysis, it's automatically linked to their profile."
        ),
        technical_deep_dive=(
            "Mention `app/core/security.py`, `pyjwt`, `bcrypt.hashpw(..., gensalt(12))`. "
            "The `get_current_user` dependency parses `Authorization: Bearer <token>`, decodes `sub` (email), "
            "and queries the database. `_require_admin` ensures `current_user.role == 'admin'`."
        ),
        follow_up_tip="If asked why JWT over server-side sessions, answer: JWT is stateless, allowing horizontal scaling across multiple backend instances without sticky sessions or shared session stores."
    )

    # Question 6
    add_interview_qa(
        q_num=6,
        question="What happens if external APIs (like NewsAPI, Google, or Groq) are down or rate-limited?",
        answer_in_my_words=(
            "Resilience was one of our main engineering priorities. We implemented three defensive layers: "
            "First, all external network requests use an asynchronous HTTP pool with timeouts (typically 8 to 20 seconds) "
            "and exponential back-off retries for transient errors like 429 rate limits or 503 service drops. "
            "Second, we have a dual-layer caching system: Redis with an automatic in-memory LRU fallback. "
            "Third, we built intelligent content-aware sandbox mocks. If an API key is missing or a service fails, "
            "the system doesn't crash—it gracefully falls back to deterministic mock evaluation, flags that in the health probe (/api/health), "
            "and still returns a realistic verdict."
        ),
        technical_deep_dive=(
            "Review `app/utils/helpers.py` (`CacheService` with `InMemoryCache` fallback) and `_post_with_retry` in `groq_service.py`. "
            "`health.py` exposes integration connectivity status."
        ),
        follow_up_tip="This shows production readiness and high-availability design thinking."
    )

    # Question 7
    add_interview_qa(
        q_num=7,
        question="What database are you using, and how is the data structured?",
        answer_in_my_words=(
            "We use SQLAlchemy 2.0 ORM with SQLite for local development and seamless compatibility with PostgreSQL for production. "
            "The schema consists of two primary models: User and Analysis. "
            "The User model tracks authentication details (email, hashed_password, role, is_active, last_login). "
            "The Analysis table stores every verification run with a UUID primary key, which enables shareable public permalinks "
            "like `/report/[uuid]`. It tracks the analysis_type ('news' or 'image'), query text or image URL, calculated trust_score, "
            "risk_level enum (LOW, MEDIUM, HIGH, CRITICAL), perceptual image_hash, and a flexible JSON column that stores all "
            "raw API outputs, linguistic breakdowns, and LLM reasoning."
        ),
        technical_deep_dive=(
            "Mention `app/models/analysis.py` and `app/models/user.py`. "
            "Explain that storing the full audit trail in a JSON/JSONB column provides schema flexibility as new API providers are added."
        ),
        follow_up_tip="Explain why UUID was chosen instead of auto-incrementing integers: it prevents enumeration attacks where competitors or scrapers increment report IDs."
    )

    # Question 8
    add_interview_qa(
        q_num=8,
        question="What were the biggest technical challenges you faced while building this project?",
        answer_in_my_words=(
            "The biggest challenge was orchestrating multiple disparate APIs without blowing up request latency. "
            "When verifying a single claim, we query Google Fact Check, NewsAPI, MediaStack, and GDELT simultaneously. "
            "Initially, sequential requests took over 8 seconds. I re-architected the pipeline to run concurrently using "
            "Python's `asyncio` and `httpx.AsyncClient` connection pools, cutting response times down to under 2.5 seconds. "
            "Another challenge was handling viral images: running deepfake neural nets on the same viral image over and over "
            "is expensive and slow. Implementing perceptual dHash caching completely eliminated redundant processing."
        ),
        technical_deep_dive=(
            "Explain how `asyncio.gather()` or concurrent task scheduling in FastAPI prevents blocking the main event loop. "
            "Mention connection keep-alive headers."
        ),
        follow_up_tip="Interviewers love hearing about performance optimizations and trade-offs. Concrete latency numbers (8s -> 2.5s) make you sound credible."
    )

    # Question 9
    add_interview_qa(
        q_num=9,
        question="How would you scale TruthLens AI to handle 100,000 active users per day in production?",
        answer_in_my_words=(
            "To scale TruthLens AI to enterprise traffic, I would implement four key architectural upgrades: "
            "1. Infrastructure: Containerize the FastAPI backend with Docker and deploy across Kubernetes or AWS ECS with an Application Load Balancer. "
            "2. Database: Transition from SQLite to managed PostgreSQL (such as Amazon RDS or GCP Cloud SQL) with read replicas and connection pooling via PgBouncer. "
            "3. Caching & Message Queue: Deploy a distributed Redis cluster for caching viral claims. For heavy media analysis, decouple the web request by using Celery or RabbitMQ to process image and video forensics asynchronously with WebSockets notifying the frontend. "
            "4. Edge Delivery: Deploy the Next.js frontend to Vercel or AWS CloudFront to serve static assets and cached public reports directly from CDN edge nodes."
        ),
        technical_deep_dive=(
            "Discuss Celery / Redis background worker architecture. "
            "Explain how long image/video processing can be converted to 202 Accepted status with webhook/WebSocket push."
        ),
        follow_up_tip="This proves you have senior-level systems design intuition beyond just building localhost applications."
    )

    # Question 10
    add_interview_qa(
        q_num=10,
        question="If you had more time or a bigger budget, what features would you build next?",
        answer_in_my_words=(
            "I have three roadmap features planned: "
            "First, Video Deepfake Analysis: extracting frames and audio tracks to run spatial-temporal CNNs and voice clone detection. "
            "Second, a Chrome Browser Extension: allowing users to highlight any text or right-click any image on Twitter, Reddit, or YouTube "
            "and see the TruthLens Trust Score in a floating tooltip without leaving the page. "
            "Third, Social Network Graph Analysis: tracking which bot accounts or coordinated networks are spreading a specific claim."
        ),
        technical_deep_dive=(
            "Mention OpenCV and FFmpeg for video frame sampling. "
            "Mention Manifest V3 for modern Chrome extensions."
        ),
        follow_up_tip="Shows passion, vision, and forward-looking product orientation."
    )

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6: ELEVATOR PITCH & CLOSING ADVICE
    # ══════════════════════════════════════════════════════════════════════════
    doc.add_page_break()
    add_h1("6. The 60-Second Elevator Pitch & Final Interview Strategy")
    
    add_callout(
        "Memorize This 60-Second Pitch (Your Opening Statement)",
        "\"TruthLens AI is a real-time misinformation detection and content authentication platform that I built using "
        "FastAPI, Next.js 15, and Groq's Llama 3.1. It solves the delay and opacity of manual fact-checking by combining "
        "deterministic forensic algorithms with multi-source verification. For text, it aggregates Google Fact Check, NewsAPI, "
        "and GDELT while scanning for sensationalist and health misinformation patterns. For images, it inspects EXIF metadata "
        "and runs Hive AI deepfake detection, using perceptual dHash caching for viral content. Everything feeds into our "
        "proprietary Trust Engine v3, which computes an objective 0 to 100 Trust Score backed by an explainable audit report. "
        "I focused heavily on production resilience, asynchronous concurrency, and clean JWT security.\"",
        border_color="047857",
        bg_color="ECFDF5"
    )

    add_h2("Golden Rules for Your Interview")
    add_bullet(" Always refer to the components as 'we built' or 'I engineered' (e.g. 'I implemented the Trust Engine with 20+ weighted signals'). Never say 'I found this code online' or 'someone helped me'.", "Rule 1: Own Every Line of Architecture:")
    add_bullet(" Remember: Groq Llama 3.1 70B Versatile is the LLM; Hive Moderation AI is the deepfake detector; Google Cloud Vision is for spoofing; NewsAPI/GDELT is for news corroboration; SQLite/PostgreSQL is the database; FastAPI is the server.", "Rule 2: Know the Core Names:")
    add_bullet(" You built a deterministic scoring engine specifically because LLMs hallucinate. You use the LLM to explain and summarize the hard forensic evidence, not to invent the score.", "Rule 3: Understand the LLM's Role:")
    add_bullet(" If they ask 'Why not Python Django?', answer: 'FastAPI has native async support and automatic Pydantic data validation, which was essential for firing multiple external verification APIs concurrently.'", "Rule 4: Have Technical Justifications:")

    # Save document
    output_path = r"c:\TruthLens AI\TruthLens_AI_Project_and_Interview_Master_Guide.docx"
    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    create_truthlens_interview_doc()
