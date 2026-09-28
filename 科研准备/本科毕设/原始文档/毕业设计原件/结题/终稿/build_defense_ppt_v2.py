from pathlib import Path
from zipfile import ZipFile

from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor


ROOT = Path.cwd()
OUT = ROOT / "2022112550_ZhouZijing_Thesis_Defense_PPT_v2.pptx"
ASSET_DIR = ROOT / "_ppt_assets_resistive_film"
TPL_MEDIA = ASSET_DIR / "template_media"

TEMPLATE = next(ROOT.glob("*Template_2.pptx"))
THESIS = next(f for f in ROOT.glob("*.docx") if "2022112550" in f.name and not f.name.startswith("~$"))
CODE_FILE = ROOT / "ohmic_sheet_12x12_multitemplate_topology_ga_code.py"

BG_COVER = TPL_MEDIA / "image1.jpeg"
BG_CONTENT = TPL_MEDIA / "image2.jpeg"
LOGO_HIT = TPL_MEDIA / "image4.png"

FIGS = {
    "fig2_1": ASSET_DIR / "fig2_1_power_flow.png",
    "fig2_3": ASSET_DIR / "fig2_3_effective_bandwidth.png",
    "fig3_1": ASSET_DIR / "fig3_1_design_concept.png",
    "fig3_2": ASSET_DIR / "fig3_2_cst_model.png",
    "fig3_3": ASSET_DIR / "fig3_3_geometry_boundary.png",
    "fig3_5": ASSET_DIR / "fig3_5_resistive_film_cross_section.png",
    "fig4_1": ASSET_DIR / "fig4_1_cst_python_workflow.png",
    "fig4_2": ASSET_DIR / "fig4_2_ga_encoding.png",
    "fig4_3": ASSET_DIR / "fig4_3_resolution_expansion.png",
    "fig5_1": ASSET_DIR / "fig5_1_6x6_thin_baseline.png",
    "fig5_2": ASSET_DIR / "fig5_2_6x6_ohmic_verify.png",
    "fig5_3": ASSET_DIR / "fig5_3_6x6_ohmic_reopt.png",
    "fig5_5": ASSET_DIR / "fig5_5_9x9_ph_perturb.png",
    "fig5_7": ASSET_DIR / "fig5_7_final_topology.png",
    "fig5_9": ASSET_DIR / "fig5_9_final_rl_curve.png",
    "fig6_2": ASSET_DIR / "fig6_2_final_3d_model.png",
    "fig6_3": ASSET_DIR / "fig6_3_efield_8p8.png",
    "fig6_7": ASSET_DIR / "fig6_7_hfield_12p0.png",
    "fig6_11": ASSET_DIR / "fig6_11_loss_15p5.png",
}

RED = RGBColor(164, 33, 28)
DARK = RGBColor(36, 48, 56)
BLUE = RGBColor(43, 91, 122)
TEAL = RGBColor(42, 120, 128)
ORANGE = RGBColor(195, 112, 45)
GREEN = RGBColor(51, 119, 87)
GREY = RGBColor(112, 125, 132)
LIGHT = RGBColor(246, 248, 249)
MID = RGBColor(226, 232, 235)
LINE = RGBColor(196, 204, 208)
WHITE = RGBColor(255, 255, 255)
CODE_BG = RGBColor(247, 248, 249)

FONT = "Aptos"
FONT_SERIF = "Times New Roman"
FONT_CODE = "Consolas"


def ensure_assets():
    ASSET_DIR.mkdir(exist_ok=True)
    TPL_MEDIA.mkdir(exist_ok=True)
    fig_map = {
        "fig2_1_power_flow.png": "word/media/image1.png",
        "fig2_3_effective_bandwidth.png": "word/media/image3.png",
        "fig3_1_design_concept.png": "word/media/image7.png",
        "fig3_2_cst_model.png": "word/media/image8.png",
        "fig3_3_geometry_boundary.png": "word/media/image9.png",
        "fig3_5_resistive_film_cross_section.png": "word/media/image11.png",
        "fig4_1_cst_python_workflow.png": "word/media/image12.png",
        "fig4_2_ga_encoding.png": "word/media/image13.png",
        "fig4_3_resolution_expansion.png": "word/media/image14.png",
        "fig5_1_6x6_thin_baseline.png": "word/media/image15.png",
        "fig5_2_6x6_ohmic_verify.png": "word/media/image16.png",
        "fig5_3_6x6_ohmic_reopt.png": "word/media/image17.png",
        "fig5_5_9x9_ph_perturb.png": "word/media/image19.png",
        "fig5_7_final_topology.png": "word/media/image21.png",
        "fig5_9_final_rl_curve.png": "word/media/image23.png",
        "fig6_2_final_3d_model.png": "word/media/image28.png",
        "fig6_3_efield_8p8.png": "word/media/image29.png",
        "fig6_7_hfield_12p0.png": "word/media/image33.png",
        "fig6_11_loss_15p5.png": "word/media/image37.png",
    }
    with ZipFile(THESIS) as z:
        for out_name, src in fig_map.items():
            out = ASSET_DIR / out_name
            if not out.exists():
                out.write_bytes(z.read(src))
    with ZipFile(TEMPLATE) as z:
        for name in z.namelist():
            if name.startswith("ppt/media/") and not name.endswith("/"):
                out = TPL_MEDIA / Path(name).name
                if not out.exists():
                    out.write_bytes(z.read(name))


def remove_all_slides(prs):
    sld_id_lst = prs.slides._sldIdLst
    for idx in range(len(prs.slides) - 1, -1, -1):
        r_id = sld_id_lst[idx].rId
        prs.part.drop_rel(r_id)
        del sld_id_lst[idx]


def clear_slide(slide):
    for shp in list(slide.shapes):
        shp._element.getparent().remove(shp._element)


def add_background(slide, bg_path):
    slide.shapes.add_picture(str(bg_path), 0, 0, width=Inches(10), height=Inches(5.625))


def set_text(shape, text, size=18, color=DARK, bold=False, align=PP_ALIGN.LEFT,
             font=FONT, italic=False):
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.name = font
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.italic = italic
    p.font.color.rgb = color
    return shape


def add_text(slide, x, y, w, h, text, size=18, color=DARK, bold=False,
             align=PP_ALIGN.LEFT, font=FONT, italic=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    box.text_frame.margin_left = Inches(0.04)
    box.text_frame.margin_right = Inches(0.04)
    box.text_frame.margin_top = Inches(0.02)
    box.text_frame.margin_bottom = Inches(0.02)
    return set_text(box, text, size, color, bold, align, font, italic)


def add_bullets(slide, x, y, w, h, items, size=16.5, color=DARK, bullet="•"):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{bullet} {item}"
        p.font.name = FONT
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.space_after = Pt(6)
        p.line_spacing = 1.05
    return box


def add_card(slide, x, y, w, h, fill=WHITE, line=LINE, transparency=0):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.fill.transparency = transparency
    shp.line.color.rgb = line
    shp.line.width = Pt(0.8)
    return shp


def add_label(slide, x, y, w, h, text, fill=BLUE, size=12, color=WHITE):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.color.rgb = fill
    set_text(shp, text, size=size, color=color, bold=True, align=PP_ALIGN.CENTER)
    shp.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    return shp


def add_header(slide, title, slide_no):
    slide.shapes.add_picture(str(LOGO_HIT), Inches(0.35), Inches(0.10), width=Inches(2.72))
    size = 28
    if len(title) > 54:
        size = 23
    elif len(title) > 42:
        size = 25
    add_text(slide, 3.18, 0.12, 6.55, 0.60, title, size=size, color=DARK, bold=True)
    add_text(slide, 0.42, 5.08, 4.55, 0.25, "Zhou Zijing | Undergraduate Thesis Defense | 2026",
             size=8.5, color=WHITE, bold=False)
    add_text(slide, 8.90, 5.08, 0.70, 0.25, f"{slide_no:02d}/16",
             size=9, color=WHITE, bold=True, align=PP_ALIGN.RIGHT)


def add_picture_contain(slide, path, x, y, w, h, border=True, caption=None,
                        caption_size=12, fill_bg=True):
    if border:
        add_card(slide, x, y, w, h, fill=WHITE if fill_bg else LIGHT, line=LINE)
    with Image.open(path) as img:
        iw, ih = img.size
    aspect = iw / ih
    box_aspect = w / h
    if aspect >= box_aspect:
        pw = w - 0.10
        ph = pw / aspect
    else:
        ph = h - 0.10
        pw = ph * aspect
    px = x + (w - pw) / 2
    py = y + (h - ph) / 2
    slide.shapes.add_picture(str(path), Inches(px), Inches(py), width=Inches(pw), height=Inches(ph))
    if caption:
        add_text(slide, x, y + h + 0.03, w, 0.24, caption, size=caption_size,
                 color=GREY, align=PP_ALIGN.CENTER)


def add_table(slide, x, y, w, h, data, col_widths=None, font_size=11.5):
    rows = len(data)
    cols = len(data[0])
    shape = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h))
    table = shape.table
    if col_widths:
        for i, cw in enumerate(col_widths):
            table.columns[i].width = Inches(cw)
    for r in range(rows):
        for c in range(cols):
            cell = table.cell(r, c)
            cell.text = data[r][c]
            cell.margin_left = Inches(0.04)
            cell.margin_right = Inches(0.04)
            cell.margin_top = Inches(0.02)
            cell.margin_bottom = Inches(0.02)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RED if r == 0 else (RGBColor(250, 251, 252) if r % 2 else WHITE)
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.font.name = FONT
            p.font.size = Pt(font_size if r else font_size + 0.5)
            p.font.bold = r == 0
            p.font.color.rgb = WHITE if r == 0 else DARK
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    return shape


def add_flow_box(slide, x, y, w, h, title, subtitle="", fill=WHITE, line=BLUE, size=12):
    box = add_card(slide, x, y, w, h, fill=fill, line=line)
    text = title + ("\n" + subtitle if subtitle else "")
    set_text(box, text, size=size, color=DARK, bold=True, align=PP_ALIGN.CENTER)
    box.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    return box


def add_line(slide, x1, y1, x2, y2, color=GREY, width=1.4):
    line = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    line.line.color.rgb = color
    line.line.width = Pt(width)
    return line


def add_code_block(slide, x, y, w, h, code, source, size=10.5):
    add_card(slide, x, y, w, h, fill=CODE_BG, line=LINE)
    add_text(slide, x + 0.08, y + 0.05, w - 0.16, 0.18, source,
             size=8.6, color=GREY, bold=False)
    box = slide.shapes.add_textbox(Inches(x + 0.08), Inches(y + 0.28), Inches(w - 0.16), Inches(h - 0.36))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = False
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    for i, line in enumerate(code.splitlines()):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = FONT_CODE
        p.font.size = Pt(size)
        p.font.color.rgb = RGBColor(30, 42, 48)
        p.space_after = Pt(0)
    return box


def get_code_lines(start, end):
    lines = CODE_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[start - 1:end])


def make_deck():
    ensure_assets()
    prs = Presentation(str(TEMPLATE))
    remove_all_slides(prs)
    layout = prs.slide_layouts[4]

    # 1 Cover
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_COVER)
    add_card(s, 0.58, 0.98, 4.25, 3.25, fill=WHITE, line=RGBColor(230, 233, 235), transparency=7)
    add_text(s, 0.80, 1.18, 3.82, 1.44,
             "Resistive Film-Based\nMetamaterial Structure Design\nfor Enhanced Broadband\nMicrowave Absorption",
             size=23.5, color=DARK, bold=True)
    add_text(s, 0.82, 2.80, 3.70, 0.34, "Undergraduate Thesis Defense", size=18, color=RED, bold=True)
    add_text(s, 0.82, 3.25, 3.70, 0.70,
             "Zhou Zijing\nSchool of Physics, Harbin Institute of Technology\nAdvisor: Prof. Meng Qingxin | May 2026",
             size=13.2, color=DARK)
    add_picture_contain(s, FIGS["fig6_2"], 5.20, 1.05, 4.25, 2.72,
                        caption="Final 12x12 CST model", caption_size=11)
    add_label(s, 5.72, 4.02, 3.15, 0.40, "Final continuous bandwidth: 13.20 GHz", fill=RED, size=13)
    add_text(s, 0.82, 5.05, 5.60, 0.25, "Metal-backed dual-orthogonal Ohmic Sheet absorber | 2-18 GHz",
             size=11.5, color=WHITE, bold=True)

    # 2 Motivation
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "Motivation and Research Target", 2)
    add_picture_contain(s, FIGS["fig2_1"], 5.02, 1.02, 4.20, 3.20,
                        caption="Thesis Fig. 2-1: incident, reflected, transmitted, and absorbed power")
    add_label(s, 0.58, 1.02, 3.70, 0.42, "Research problem", fill=BLUE, size=15)
    add_bullets(s, 0.68, 1.62, 3.80, 1.25, [
        "Complex electromagnetic environments require low-reflection absorbing structures.",
        "Conventional absorbers face bandwidth, thickness, and tunability limits.",
        "This thesis targets continuous absorption in the 2-18 GHz band."
    ], size=14.5)
    add_label(s, 0.68, 3.36, 3.55, 0.42, "Main target: longest continuous RL < -10 dB band", fill=GREEN, size=13)
    add_text(s, 0.82, 4.16, 3.42, 0.45,
             "The defense focus is the completed modeling and optimization process, not only the final curve.",
             size=13, color=GREY, align=PP_ALIGN.CENTER)

    # 3 Criterion
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "Absorption Criterion and Evaluation Indices", 3)
    add_picture_contain(s, FIGS["fig2_3"], 4.34, 1.00, 4.78, 3.28,
                        caption="Thesis Fig. 2-3: effective bandwidth and coverage ratio")
    add_card(s, 0.58, 1.06, 3.30, 3.15, fill=WHITE, line=BLUE)
    add_text(s, 0.78, 1.25, 2.92, 0.46, "Metal-backed absorber", size=17, color=BLUE, bold=True)
    add_text(s, 0.86, 1.92, 2.70, 0.46, "RL = 20 log10 |S11|", size=22, color=DARK, bold=True,
             align=PP_ALIGN.CENTER, font=FONT_SERIF)
    add_bullets(s, 0.82, 2.65, 2.75, 1.10, [
        "Transmission is suppressed by the metal backplane.",
        "RL < -10 dB corresponds to low reflection.",
        "Coverage ratio uses the 16 GHz target band."
    ], size=12.8)
    add_label(s, 0.94, 3.82, 2.52, 0.34, "Optimize continuity, not only minimum RL", fill=ORANGE, size=11.2)

    # 4 Structure
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "Absorbing Unit Structure", 4)
    add_picture_contain(s, FIGS["fig3_1"], 4.35, 0.98, 4.82, 3.46,
                        caption="Thesis Fig. 3-1: orthogonal resistive-film absorbing unit")
    comp = [
        ("Metal backplane", "Suppresses transmission", BLUE),
        ("PET substrates", "0.188 mm support layers", TEAL),
        ("X-oriented film", "higher Rs; impedance / HF compensation", ORANGE),
        ("Y-oriented film", "lower Rs; main ohmic dissipation path", GREEN),
    ]
    for i, (head, body, col) in enumerate(comp):
        y = 1.02 + i * 0.82
        add_card(s, 0.58, y, 3.42, 0.62, fill=WHITE, line=col)
        add_text(s, 0.78, y + 0.08, 3.02, 0.20, head, size=14.3, color=col, bold=True)
        add_text(s, 0.78, y + 0.35, 3.05, 0.20, body, size=11.2, color=DARK)
    add_label(s, 0.85, 4.42, 2.82, 0.34, "Independent X/Y topology and sheet resistance", fill=RED, size=11.2)

    # 5 CST environment
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "CST Modeling Environment", 5)
    add_picture_contain(s, FIGS["fig3_2"], 0.58, 1.00, 4.10, 2.00,
                        caption="Thesis Fig. 3-2: CST 3D unit model")
    add_picture_contain(s, FIGS["fig3_3"], 5.02, 1.00, 4.10, 2.00,
                        caption="Thesis Fig. 3-3: geometry, coordinate system, and boundary settings")
    sim_data = [
        ["Setting", "Value / role"],
        ["Solver", "Frequency-domain full-wave simulation"],
        ["Boundary", "Periodic in X/Y; open boundary in Z"],
        ["Excitation", "Floquet port / normally incident plane wave"],
        ["Frequency", "2-18 GHz sweep"],
        ["Output", "S11 exported for RL and bandwidth calculation"],
    ]
    add_table(s, 1.18, 3.40, 7.55, 1.08, sim_data, col_widths=[1.65, 5.90], font_size=9.8)

    # 6 Monitor settings
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "Monitor and Output Settings", 6)
    monitor_data = [
        ["Output item", "Frequency", "Purpose"],
        ["S11 / RL curve", "2-18 GHz sweep", "Fitness: bandwidth, coverage, min RL"],
        ["Electric field", "8.8, 12.0, 15.5 GHz", "Field enhancement and edge response"],
        ["Magnetic field", "8.8, 12.0, 15.5 GHz", "Coupling with metal backplane"],
        ["Power-loss density", "8.8, 12.0, 15.5 GHz", "Ohmic-loss locations on sheet film"],
    ]
    add_table(s, 0.62, 1.08, 8.76, 2.65, monitor_data, col_widths=[2.05, 2.20, 4.51], font_size=11.2)
    add_label(s, 0.90, 4.05, 3.65, 0.42, "Optimization stage", fill=BLUE, size=14)
    add_text(s, 1.02, 4.55, 3.42, 0.20, "S11 -> RL -> continuous bandwidth fitness", size=12.8, color=DARK,
             align=PP_ALIGN.CENTER)
    add_label(s, 5.08, 4.05, 3.65, 0.42, "Mechanism stage", fill=GREEN, size=14)
    add_text(s, 5.20, 4.55, 3.42, 0.20, "E/H fields and loss density explain absorption", size=12.8, color=DARK,
             align=PP_ALIGN.CENTER)

    # 7 Model choice
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "Model Choice: Thin Solid Film vs Ohmic Sheet", 7)
    add_picture_contain(s, FIGS["fig3_5"], 0.62, 1.00, 4.55, 2.74,
                        caption="Thesis Fig. 3-5: engineering sheet-resistance film cross-section")
    model_data = [
        ["Item", "Thin solid film", "Ohmic Sheet"],
        ["Input", "Thickness + conductivity", "Sheet resistance Ω/sq"],
        ["Mesh cost", "Higher for thin layers", "Lower surface model"],
        ["Engineering match", "Indirect conversion", "Direct sheet-resistance parameter"],
        ["Use in thesis", "Early feasibility", "6x6 / 9x9 / 12x12 optimization"],
    ]
    add_table(s, 5.45, 1.02, 3.90, 2.15, model_data, col_widths=[1.05, 1.38, 1.47], font_size=8.8)
    add_label(s, 5.62, 3.55, 3.35, 0.42, "Final modeling basis: Ohmic Sheet", fill=GREEN, size=13.5)
    add_text(s, 5.58, 4.15, 3.45, 0.42,
             "Reason: clearer material meaning and better suitability for high-resolution pixel optimization.",
             size=12.2, color=GREY, align=PP_ALIGN.CENTER)

    # 8 Pixel topology
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "Pixelated Topology Construction", 8)
    add_picture_contain(s, FIGS["fig4_2"], 4.40, 1.02, 4.82, 3.22,
                        caption="Thesis Fig. 4-2: chromosome encoding and genetic updating mechanism")
    pix_data = [
        ["Stage", "Pixels / layer", "X/Y binary variables"],
        ["6x6", "36", "72"],
        ["9x9", "81", "162"],
        ["12x12", "144", "288"],
    ]
    add_table(s, 0.68, 1.10, 3.20, 1.38, pix_data, col_widths=[0.95, 1.05, 1.20], font_size=10.5)
    add_bullets(s, 0.74, 2.78, 3.15, 1.08, [
        "1 = retained sheet-resistance region",
        "0 = removed region",
        "X/Y films evolve independently"
    ], size=13.2)
    add_label(s, 0.82, 4.18, 2.82, 0.36, "Binary matrix -> chromosome -> CST model", fill=ORANGE, size=11.3)

    # 9 Closed loop
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "CST-Python Closed Loop", 9)
    add_picture_contain(s, FIGS["fig4_1"], 0.50, 0.92, 7.10, 3.80,
                        caption="Thesis Fig. 4-1: CST-Python co-simulation and staged GA optimization workflow")
    steps = ["Parameter generation", "CST modeling", "S11 export", "Fitness calculation", "GA update"]
    for i, st in enumerate(steps):
        add_label(s, 7.92, 1.02 + i * 0.64, 1.34, 0.36, st, fill=[BLUE, TEAL, GREY, GREEN, ORANGE][i], size=9.8)
    add_text(s, 7.80, 4.38, 1.58, 0.28, "One automated loop replaces repeated manual modeling.", size=10.8,
             color=GREY, align=PP_ALIGN.CENTER)

    # 10 Code variables
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "Code Evidence: Variables and GA Setup", 10)
    code1 = "\n".join([
        'OPTIMIZATION_FILM_MODEL = "ohmic_sheet"',
        "TOPOLOGY_N = 12",
        "TARGET_TOTAL_BAND = 16.0",
        "REFERENCE_9X9_BW = 12.338308457711443",
        "REFERENCE_12X12_BW = 13.120000000000001",
        "TARGET_85_BW = 13.6",
        "P_MIN = 12.85",
        "P_MAX = 13.55",
        "H_MIN = 9.65",
        "H_MAX = 10.45",
        "RS_X_MIN = 80.0",
        "RS_X_MAX = 240.0",
        "RS_Y_MIN = 20.0",
        "RS_Y_MAX = 80.0",
        "BASE_P_12 = 13.1437",
        "BASE_H_12 = 10.0791",
        "BASE_RSX_12 = 142.198",
        "BASE_RSY_12 = 38.599",
        "pop_size = 16",
        "iterations = 8",
        "p_m_start = 0.23",
    ])
    add_code_block(s, 0.55, 0.95, 5.55, 3.90, code1,
                   "Source: ohmic_sheet_12x12_multitemplate_topology_ga_code.py, lines 4291-4321",
                   size=8.8)
    add_label(s, 6.52, 1.05, 2.55, 0.38, "What this code proves", fill=BLUE, size=13.5)
    add_bullets(s, 6.42, 1.66, 2.95, 2.62, [
        "The final stage explicitly uses the Ohmic Sheet model.",
        "p, h, Rs_x and Rs_y are continuous optimization variables.",
        "12x12 topology is optimized under constrained ranges.",
        "The GA uses 16 individuals, 8 iterations and a decaying mutation rate."
    ], size=13.0)

    # 11 Code fitness
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "Code Evidence: Fitness from S11 Results", 11)
    code2 = "\n".join([
        "def extract_metrics(cst_file):",
        "    result = cst.results.ProjectFile(cst_file, allow_interactive=True)",
        '    s11 = result.get_3d().get_result_item(r\"1D Results\\S-Parameters\\SZmax(1),Zmax(1)\")',
        "    data = s11.get_data()",
        "    freqs, rls = [], []",
        "    for row in data:",
        "        freq = float(row[0])",
        "        mag = max(abs(row[1]), 1e-12)",
        "        freqs.append(freq)",
        "        rls.append(float(20 * np.log10(mag)))",
        "    freqs = np.array(freqs, dtype=float)",
        "    rls = np.array(rls, dtype=float)",
        "    intervals = _find_effective_intervals(freqs, rls, -10.0)",
        "    if intervals:",
        "        i0, i1 = max(intervals, key=lambda t: freqs[t[1]] - freqs[t[0]])",
        "        f_low, f_high = float(freqs[i0]), float(freqs[i1])",
        "        bw = max(0.0, f_high - f_low)",
    ])
    add_code_block(s, 0.48, 0.95, 5.95, 3.95, code2,
                   "Source: ohmic_sheet_12x12_multitemplate_topology_ga_code.py, lines 4711-4736",
                   size=8.8)
    add_label(s, 6.78, 1.05, 2.25, 0.38, "Fitness data flow", fill=GREEN, size=13.5)
    flow = [("CST result", BLUE), ("S11 data", TEAL), ("RL curve", ORANGE), ("RL < -10 dB interval", GREEN), ("bandwidth / coverage", RED)]
    for i, (txt, col) in enumerate(flow):
        add_flow_box(s, 6.75, 1.62 + i * 0.58, 2.30, 0.38, txt, fill=WHITE, line=col, size=10.5)
        if i < len(flow) - 1:
            add_line(s, 7.90, 2.00 + i * 0.58, 7.90, 2.18 + i * 0.58, color=GREY, width=1.1)
    add_text(s, 6.58, 4.55, 2.70, 0.22, "The GA objective is generated directly from simulated S11 data.",
             size=10.8, color=GREY, align=PP_ALIGN.CENTER)

    # 12 Staged strategy
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "Staged Optimization Strategy", 12)
    add_picture_contain(s, FIGS["fig4_3"], 0.70, 0.98, 8.55, 2.42,
                        caption="Thesis Fig. 4-3: hierarchical expansion from 6x6 to 9x9 to 12x12")
    stages = [
        ("6x6", "Verify model and workflow", "Problem: low-frequency edge remains high"),
        ("9x9", "Add edges, windows and bridges", "Problem: still room below 5.68 GHz"),
        ("12x12", "Multi-template final refinement", "Target: connect low/mid/high-frequency modes"),
    ]
    for i, (head, goal, issue) in enumerate(stages):
        x = 0.72 + i * 3.05
        add_card(s, x, 3.76, 2.55, 0.72, fill=WHITE, line=[BLUE, ORANGE, GREEN][i])
        add_text(s, x + 0.10, 3.84, 0.58, 0.22, head, size=16, color=[BLUE, ORANGE, GREEN][i], bold=True)
        add_text(s, x + 0.76, 3.83, 1.65, 0.20, goal, size=9.8, color=DARK, bold=True)
        add_text(s, x + 0.76, 4.10, 1.65, 0.18, issue, size=8.4, color=GREY)

    # 13 6x6
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "6x6 Stage: Feasibility and Model Transfer", 13)
    add_picture_contain(s, FIGS["fig5_1"], 0.55, 1.02, 4.15, 1.90,
                        caption="Thesis Fig. 5-1: 6x6 thin solid film baseline")
    add_picture_contain(s, FIGS["fig5_3"], 0.55, 3.18, 4.15, 1.28,
                        caption="Thesis Fig. 5-3: 6x6 Ohmic Sheet re-optimization")
    data = [
        ["Step", "Purpose", "Result"],
        ["Thin solid baseline", "Verify orthogonal structure + workflow", "5.12-18.00 GHz; 12.88 GHz"],
        ["Ohmic verification", "Test same pattern after model transfer", "6.88-18.00 GHz; 11.12 GHz"],
        ["Ohmic re-opt.", "Restart search under sheet resistance", "6.80-18.00 GHz; 11.20 GHz"],
    ]
    add_table(s, 5.00, 1.08, 4.25, 1.62, data, col_widths=[1.20, 1.70, 1.35], font_size=8.8)
    add_label(s, 5.28, 3.18, 3.55, 0.38, "What this stage solved", fill=BLUE, size=13.2)
    add_bullets(s, 5.12, 3.72, 3.98, 0.82, [
        "Confirmed the structural route and automatic optimization workflow.",
        "Showed why the Ohmic Sheet model needed independent re-optimization.",
        "Exposed the next bottleneck: low-frequency boundary near 6.8 GHz."
    ], size=10.8)

    # 14 9x9
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "9x9 Stage: Resolution and p/h Perturbation", 14)
    add_picture_contain(s, FIGS["fig5_5"], 0.55, 1.00, 5.25, 3.10,
                        caption="Thesis Fig. 5-5: reflection loss after 9x9 p and h perturbation")
    add_label(s, 6.15, 1.02, 2.82, 0.38, "Concrete changes from 6x6", fill=ORANGE, size=13.2)
    change_data = [
        ["Item", "6x6", "9x9"],
        ["Pixels / layer", "36", "81"],
        ["Topology details", "coarse blocks", "edges / windows / bridges"],
        ["Variables", "pattern + parameters", "fixed topology + p/h perturbation"],
        ["Bandwidth", "11.20 GHz", "12.32 GHz"],
    ]
    add_table(s, 6.02, 1.58, 3.20, 1.72, change_data, col_widths=[1.05, 1.00, 1.15], font_size=8.8)
    add_bullets(s, 6.08, 3.72, 3.05, 0.74, [
        "Low-frequency edge improved to 5.68 GHz.",
        "Deepest local minimum appeared, but final goal required broader low-frequency coverage."
    ], size=10.8)

    # 15 12x12
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "12x12 Final Stage and Performance", 15)
    add_picture_contain(s, FIGS["fig5_7"], 0.55, 0.98, 3.95, 2.05,
                        caption="Thesis Fig. 5-7: final 12x12 topology")
    add_picture_contain(s, FIGS["fig5_9"], 4.88, 0.98, 4.25, 2.05,
                        caption="Thesis Fig. 5-9: final reflection-loss curve")
    add_label(s, 0.82, 3.28, 2.10, 0.40, "4.80-18.00 GHz", fill=RED, size=14.5)
    add_label(s, 3.12, 3.28, 2.10, 0.40, "13.20 GHz", fill=GREEN, size=15)
    add_label(s, 5.42, 3.28, 1.90, 0.40, "82.5%", fill=BLUE, size=15)
    add_label(s, 7.55, 3.28, 1.20, 0.40, "-23.485 dB", fill=ORANGE, size=11.6)
    perf = [
        ["Stage", "Effective band", "BW", "Coverage"],
        ["6x6 Ohmic re-opt.", "6.80-18.00", "11.20", "70.0%"],
        ["9x9 p/h perturb.", "5.68-18.00", "12.32", "77.0%"],
        ["12x12 HF comp.", "4.88-18.00", "13.12", "82.0%"],
        ["Final 12x12", "4.80-18.00", "13.20", "82.5%"],
    ]
    add_table(s, 0.88, 3.92, 8.00, 0.86, perf, col_widths=[2.40, 2.10, 1.00, 1.20], font_size=8.4)

    # 16 Mechanism
    s = prs.slides.add_slide(layout); clear_slide(s); add_background(s, BG_CONTENT)
    add_header(s, "Mechanism and Conclusions", 16)
    imgs = [
        (FIGS["fig6_3"], "Electric field at 8.8 GHz\nlonger current-path coupling"),
        (FIGS["fig6_7"], "Magnetic field at 12.0 GHz\nspatial coupling with backplane"),
        (FIGS["fig6_11"], "Power loss at 15.5 GHz\nlocalized ohmic loss"),
    ]
    for i, (path, cap) in enumerate(imgs):
        add_picture_contain(s, path, 0.48 + i * 3.12, 1.00, 2.92, 1.70, caption=cap, caption_size=9.2)
    mech = [
        ("Metal backplane", "suppresses transmission"),
        ("Y-oriented film", "main loss + low-frequency skeleton"),
        ("X-oriented film", "impedance tuning + high-frequency compensation"),
        ("12x12 topology", "edges, windows and bridges connect multiple modes"),
    ]
    for i, (head, body) in enumerate(mech):
        x = 0.70 + (i % 2) * 4.40
        y = 3.55 + (i // 2) * 0.54
        add_flow_box(s, x, y, 3.75, 0.38, head, body, fill=WHITE, line=[BLUE, GREEN, ORANGE, RED][i], size=9.6)
    add_text(s, 1.10, 4.75, 7.70, 0.22,
             "Conclusion: the final bandwidth is obtained through model construction, automated optimization, staged refinement, and field-based mechanism verification.",
             size=10.6, color=GREY, align=PP_ALIGN.CENTER)

    prs.save(str(OUT))
    return OUT


if __name__ == "__main__":
    print(make_deck())
