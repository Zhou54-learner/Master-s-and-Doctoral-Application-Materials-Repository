from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy

from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor


ROOT = Path.cwd()
OUT = ROOT / "2022112550_ZhouZijing_Thesis_Defense_PPT.pptx"
ASSET_DIR = ROOT / "_ppt_assets_resistive_film"
TPL_MEDIA = ASSET_DIR / "template_media"

TEMPLATE = next(ROOT.glob("*Template_2.pptx"))
THESIS = next(f for f in ROOT.glob("*.docx") if "2022112550" in f.name and not f.name.startswith("~$"))

BG_COVER = TPL_MEDIA / "image1.jpeg"
BG_CONTENT = TPL_MEDIA / "image2.jpeg"
LOGO_HIT = TPL_MEDIA / "image4.png"

FIGS = {
    "fig2_1": ASSET_DIR / "fig2_1_power_flow.png",
    "fig2_3": ASSET_DIR / "fig2_3_effective_bandwidth.png",
    "fig3_1": ASSET_DIR / "fig3_1_design_concept.png",
    "fig3_2": ASSET_DIR / "fig3_2_cst_model.png",
    "fig3_4": ASSET_DIR / "fig3_4_model_curve_comparison.png",
    "fig3_5": ASSET_DIR / "fig3_5_resistive_film_cross_section.png",
    "fig4_1": ASSET_DIR / "fig4_1_cst_python_workflow.png",
    "fig4_2": ASSET_DIR / "fig4_2_ga_encoding.png",
    "fig4_3": ASSET_DIR / "fig4_3_resolution_expansion.png",
    "fig5_7": ASSET_DIR / "fig5_7_final_topology.png",
    "fig5_9": ASSET_DIR / "fig5_9_final_rl_curve.png",
    "fig5_10": ASSET_DIR / "fig5_10_stage_curves.png",
    "fig5_11": ASSET_DIR / "fig5_11_bandwidth_comparison.png",
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
LIGHT = RGBColor(245, 247, 248)
LINE = RGBColor(198, 205, 209)
WHITE = RGBColor(255, 255, 255)

FONT = "Aptos"
FONT_SERIF = "Times New Roman"


def ensure_assets():
    ASSET_DIR.mkdir(exist_ok=True)
    TPL_MEDIA.mkdir(exist_ok=True)
    fig_map = {
        "fig2_1_power_flow.png": "word/media/image1.png",
        "fig2_3_effective_bandwidth.png": "word/media/image3.png",
        "fig3_1_design_concept.png": "word/media/image7.png",
        "fig3_2_cst_model.png": "word/media/image8.png",
        "fig3_4_model_curve_comparison.png": "word/media/image10.png",
        "fig3_5_resistive_film_cross_section.png": "word/media/image11.png",
        "fig4_1_cst_python_workflow.png": "word/media/image12.png",
        "fig4_2_ga_encoding.png": "word/media/image13.png",
        "fig4_3_resolution_expansion.png": "word/media/image14.png",
        "fig5_7_final_topology.png": "word/media/image21.png",
        "fig5_9_final_rl_curve.png": "word/media/image23.png",
        "fig5_10_stage_curves.png": "word/media/image24.png",
        "fig5_11_bandwidth_comparison.png": "word/media/image25.png",
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


def add_bullets(slide, x, y, w, h, items, size=17, color=DARK, bullet_color=None,
                line_spacing=1.05):
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
        p.text = "\u2022 " + item
        p.font.name = FONT
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.space_after = Pt(5)
        p.line_spacing = line_spacing
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
    title_size = 24
    if len(title) > 66:
        title_size = 21
    elif len(title) > 52:
        title_size = 22
    add_text(slide, 3.20, 0.16, 6.45, 0.55, title, size=title_size, color=DARK, bold=True)
    add_text(slide, 0.42, 5.08, 4.40, 0.25, "Zhou Zijing | Undergraduate Thesis Defense | 2026",
             size=8.5, color=WHITE, bold=False)
    add_text(slide, 8.92, 5.08, 0.68, 0.25, f"{slide_no:02d}/12",
             size=9, color=WHITE, bold=True, align=PP_ALIGN.RIGHT)


def add_picture_contain(slide, path, x, y, w, h, border=True, caption=None, caption_size=8.5,
                        fill_bg=True):
    if border:
        add_card(slide, x, y, w, h, fill=WHITE if fill_bg else LIGHT, line=LINE, transparency=0)
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
        add_text(slide, x, y + h + 0.02, w, 0.20, caption, size=caption_size, color=GREY,
                 align=PP_ALIGN.CENTER)


def add_table(slide, x, y, w, h, data, col_widths=None, font_size=10.5):
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
            fill = cell.fill
            fill.solid()
            fill.fore_color.rgb = RED if r == 0 else (RGBColor(250, 251, 252) if r % 2 else WHITE)
            para = cell.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.CENTER if r == 0 or c != 1 else PP_ALIGN.LEFT
            para.font.name = FONT
            para.font.size = Pt(font_size if r else font_size + 0.5)
            para.font.bold = r == 0
            para.font.color.rgb = WHITE if r == 0 else DARK
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    return shape


def add_arrow_between(slide, x1, y1, x2, y2, color=GREY):
    line = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    line.line.color.rgb = color
    line.line.width = Pt(1.6)
    try:
        line.line.end_arrowhead = True
    except Exception:
        pass
    return line


def add_flow_box(slide, x, y, w, h, title, subtitle="", fill=LIGHT, line=BLUE, title_size=13):
    box = add_card(slide, x, y, w, h, fill=fill, line=line)
    set_text(box, title + ("\n" + subtitle if subtitle else ""), size=title_size, color=DARK,
             bold=True, align=PP_ALIGN.CENTER)
    box.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    # Make only title-like diagrams concise; all text is editable.
    return box


def make_deck():
    ensure_assets()
    prs = Presentation(str(TEMPLATE))
    remove_all_slides(prs)
    blank_layout = prs.slide_layouts[4]

    # Slide 1
    s = prs.slides.add_slide(blank_layout)
    clear_slide(s)
    add_background(s, BG_COVER)
    add_card(s, 0.60, 1.18, 4.35, 2.45, fill=WHITE, line=RGBColor(230, 233, 235), transparency=6)
    add_text(s, 0.78, 1.32, 4.02, 1.25,
             "Resistive Film-Based Metamaterial\nStructure Design for Enhanced\nBroadband Microwave Absorption",
             size=24, color=DARK, bold=True)
    add_text(s, 0.80, 2.82, 4.00, 0.58, "Undergraduate Thesis Defense", size=18, color=RED, bold=True)
    add_text(s, 0.82, 3.35, 3.95, 0.88,
             "Zhou Zijing\nSchool of Physics, Harbin Institute of Technology\nAdvisor: Prof. Meng Qingxin | May 2026",
             size=13.5, color=DARK)
    add_picture_contain(s, FIGS["fig6_2"], 5.30, 1.18, 4.20, 2.72,
                        caption="Final 12x12 CST model", caption_size=9)
    add_label(s, 5.80, 4.12, 3.12, 0.42, "Final continuous bandwidth: 13.20 GHz", fill=RED, size=13.5)
    add_text(s, 0.80, 5.04, 6.40, 0.28,
             "Metal-backed dual-orthogonal Ohmic Sheet absorber | 2-18 GHz target band",
             size=12, color=WHITE, bold=True)

    # Slide 2
    s = prs.slides.add_slide(blank_layout)
    clear_slide(s)
    add_background(s, BG_CONTENT)
    add_header(s, "Broadband Microwave Absorption Requires Low Reflection and Wide Bandwidth", 2)
    cards = [
        ("Complex EM environment", "Radar, wireless communication,\nremote sensing, and electronic systems"),
        ("Broadband requirement", "Absorption should remain stable\nacross the 2-18 GHz band"),
        ("Low reflection target", "Continuous RL < -10 dB is used\nas the main design criterion"),
    ]
    y = 1.06
    colors = [BLUE, TEAL, GREEN]
    for i, (head, body) in enumerate(cards):
        add_card(s, 0.48, y + i * 1.10, 3.48, 0.88, fill=WHITE, line=colors[i])
        add_label(s, 0.64, y + i * 1.10 + 0.15, 0.32, 0.32, str(i + 1), fill=colors[i], size=12)
        add_text(s, 1.05, y + i * 1.10 + 0.10, 2.68, 0.24, head, size=15.5, color=colors[i], bold=True)
        add_text(s, 1.05, y + i * 1.10 + 0.39, 2.75, 0.36, body, size=10.8, color=DARK)
    add_picture_contain(s, FIGS["fig2_1"], 4.55, 1.02, 4.88, 3.28,
                        caption="Thesis Fig. 2-1: incident, reflected, transmitted, and absorbed power")
    add_label(s, 4.95, 4.43, 4.05, 0.36,
              "Goal: continuous broadband low reflection, not single-frequency absorption",
              fill=GREEN, size=11.5)

    # Slide 3
    s = prs.slides.add_slide(blank_layout)
    clear_slide(s)
    add_background(s, BG_CONTENT)
    add_header(s, "This Thesis Builds a Complete Design-to-Optimization Workflow", 3)
    steps = [
        ("Theory", "RL / impedance"),
        ("Structure", "orthogonal films"),
        ("Simulation", "Ohmic Sheet CST model"),
        ("Optimization", "GA: 6x6 to 12x12"),
        ("Mechanism", "field and loss analysis"),
    ]
    x0, y0, bw, gap = 0.48, 1.00, 1.62, 0.27
    for i, (t, sub) in enumerate(steps):
        x = x0 + i * (bw + gap)
        fill = RGBColor(247, 249, 250) if i % 2 == 0 else WHITE
        add_flow_box(s, x, y0, bw, 0.78, t, sub, fill=fill, line=[BLUE, TEAL, GREY, ORANGE, GREEN][i], title_size=12.2)
        if i < len(steps) - 1:
            add_arrow_between(s, x + bw + 0.04, y0 + 0.39, x + bw + gap - 0.04, y0 + 0.39, color=GREY)
    add_picture_contain(s, FIGS["fig4_1"], 0.74, 2.02, 8.52, 2.40,
                        caption="Thesis Fig. 4-1: CST-Python co-simulation and staged GA optimization workflow")
    add_text(s, 0.82, 4.55, 8.40, 0.22,
             "The defense focus is the completed research chain: model selection, automated simulation, staged topology optimization, and mechanism verification.",
             size=11.5, color=GREY, align=PP_ALIGN.CENTER)

    # Slide 4
    s = prs.slides.add_slide(blank_layout)
    clear_slide(s)
    add_background(s, BG_CONTENT)
    add_header(s, "Reflection Loss and Effective Bandwidth Define the Optimization Target", 4)
    add_card(s, 0.50, 1.05, 3.28, 3.22, fill=WHITE, line=BLUE)
    add_text(s, 0.72, 1.20, 2.82, 0.36, "Evaluation criterion", size=17, color=BLUE, bold=True)
    add_text(s, 0.75, 1.74, 2.70, 0.48, "RL = 20 log10 |S11|", size=22, color=DARK, bold=True, align=PP_ALIGN.CENTER, font=FONT_SERIF)
    add_bullets(s, 0.72, 2.42, 2.82, 1.42, [
        "Metal backplane makes transmission approximately zero.",
        "RL < -10 dB means less than 10% reflected power.",
        "The longest continuous RL < -10 dB band is optimized."
    ], size=11.5)
    add_label(s, 0.90, 3.83, 2.35, 0.34, "Coverage = bandwidth / 16 GHz", fill=GREEN, size=11)
    add_picture_contain(s, FIGS["fig2_3"], 4.18, 1.00, 5.12, 3.32,
                        caption="Thesis Fig. 2-3: effective bandwidth and coverage ratio definition")
    add_text(s, 4.22, 4.50, 5.03, 0.24,
             "This avoids optimizing only a deep but narrow single-frequency absorption valley.",
             size=11.5, color=GREY, align=PP_ALIGN.CENTER)

    # Slide 5
    s = prs.slides.add_slide(blank_layout)
    clear_slide(s)
    add_background(s, BG_CONTENT)
    add_header(s, "A Dual-Orthogonal Resistive-Film Unit Provides More Design Freedom", 5)
    add_picture_contain(s, FIGS["fig3_1"], 4.02, 1.00, 5.25, 3.46,
                        caption="Thesis Fig. 3-1: design concept of the orthogonal resistive-film absorbing unit")
    labels = [
        ("Metal backplane", "Suppresses transmission", BLUE),
        ("PET substrates", "Support orthogonal film planes", TEAL),
        ("X-oriented film", "Impedance regulation / compensation", ORANGE),
        ("Y-oriented film", "Main current path and ohmic loss", GREEN),
    ]
    for i, (head, body, color) in enumerate(labels):
        y = 1.05 + i * 0.82
        add_card(s, 0.55, y, 3.05, 0.60, fill=WHITE, line=color)
        add_text(s, 0.72, y + 0.08, 2.60, 0.18, head, size=13.4, color=color, bold=True)
        add_text(s, 0.72, y + 0.33, 2.65, 0.18, body, size=10.4, color=DARK)
    add_label(s, 0.66, 4.40, 2.82, 0.34,
              "Independent X/Y topologies increase design freedom",
              fill=RED, size=10.5)

    # Slide 6
    s = prs.slides.add_slide(blank_layout)
    clear_slide(s)
    add_background(s, BG_CONTENT)
    add_header(s, "The Ohmic Sheet Model Was Selected for Engineering-Oriented Optimization", 6)
    add_card(s, 0.50, 1.00, 4.10, 1.25, fill=WHITE, line=BLUE)
    add_text(s, 0.72, 1.14, 1.60, 0.28, "Thin solid film", size=15.5, color=BLUE, bold=True)
    add_text(s, 0.72, 1.49, 1.82, 0.44, "Uses thickness and\nvolume conductivity", size=11.2, color=DARK)
    add_label(s, 2.58, 1.43, 1.28, 0.34, "Compared", fill=GREY, size=10.5)
    add_text(s, 3.25, 1.14, 1.10, 0.28, "Ohmic Sheet", size=15.5, color=GREEN, bold=True)
    add_text(s, 3.12, 1.49, 1.18, 0.44, "Uses sheet\nresistance", size=11.2, color=DARK)
    add_picture_contain(s, FIGS["fig3_4"], 5.00, 1.00, 4.26, 2.05,
                        caption="Thesis Fig. 3-4: RL curve comparison")
    table_data = [
        ["Model", "Input parameter", "Effective band", "Role in thesis"],
        ["Thin solid", "Thickness + conductivity", "5.12-18.00 GHz", "Feasibility check"],
        ["Ohmic Sheet", "Sheet resistance", "6.88-18.00 GHz", "Selected for optimization"],
    ]
    add_table(s, 0.55, 2.55, 4.30, 1.52, table_data, col_widths=[1.0, 1.3, 1.1, 0.9], font_size=8.8)
    add_picture_contain(s, FIGS["fig3_5"], 5.00, 3.27, 4.26, 0.92,
                        caption="Thesis Fig. 3-5: engineering sheet-resistance film cross-section", caption_size=8)
    add_label(s, 5.42, 4.38, 3.38, 0.34,
              "Final choice: Ohmic Sheet model for 6x6, 9x9, and 12x12 stages",
              fill=GREEN, size=10.2)

    # Slide 7
    s = prs.slides.add_slide(blank_layout)
    clear_slide(s)
    add_background(s, BG_CONTENT)
    add_header(s, "CST-Python Co-Simulation Automates Modeling, Solving, and Evaluation", 7)
    loop = [
        ("Generate\nparameters", BLUE),
        ("Build CST\nunit model", TEAL),
        ("Frequency-domain\nsolving", GREY),
        ("Export S11", ORANGE),
        ("Calculate RL\nand bandwidth", GREEN),
        ("Update GA\npopulation", RED),
    ]
    coords = [(0.68, 1.15), (2.36, 1.15), (4.04, 1.15), (5.72, 1.15), (7.40, 1.15), (3.18, 2.35)]
    for i, ((txt, color), (x, y)) in enumerate(zip(loop, coords)):
        add_flow_box(s, x, y, 1.34, 0.62, txt, fill=WHITE, line=color, title_size=10.6)
    arrow_pairs = [(1.98, 1.46, 2.34, 1.46), (3.66, 1.46, 4.02, 1.46),
                   (5.34, 1.46, 5.70, 1.46), (7.02, 1.46, 7.38, 1.46),
                   (8.05, 1.80, 4.52, 2.34), (3.80, 2.35, 1.35, 1.80)]
    for x1, y1, x2, y2 in arrow_pairs:
        add_arrow_between(s, x1, y1, x2, y2, color=GREY)
    add_picture_contain(s, FIGS["fig4_1"], 0.65, 3.05, 8.76, 1.42,
                        caption="Thesis Fig. 4-1: original workflow diagram")
    add_text(s, 0.80, 4.58, 8.46, 0.20,
             "Workload evidence: automatic modeling, full-wave solving, S11 export, RL calculation, and generation-by-generation optimization.",
             size=11.2, color=GREY, align=PP_ALIGN.CENTER)

    # Slide 8
    s = prs.slides.add_slide(blank_layout)
    clear_slide(s)
    add_background(s, BG_CONTENT)
    add_header(s, "The Optimization Combines Continuous Parameters and Pixelated Topology", 8)
    add_flow_box(s, 0.62, 1.00, 2.70, 0.46, "Optimization variables", fill=WHITE, line=RED, title_size=13.5)
    add_flow_box(s, 0.70, 1.86, 2.42, 0.54, "Continuous variables", "p, h, Rs,x, Rs,y", fill=WHITE, line=BLUE, title_size=11.8)
    add_flow_box(s, 0.70, 2.82, 2.42, 0.64, "Discrete variables", "X pattern matrix\nY pattern matrix", fill=WHITE, line=GREEN, title_size=11.8)
    add_arrow_between(s, 1.97, 1.46, 1.97, 1.85, color=GREY)
    add_arrow_between(s, 1.97, 1.46, 1.97, 2.81, color=GREY)
    add_label(s, 0.82, 3.86, 2.22, 0.36, "12x12 x 2 layers = 288 binary variables", fill=ORANGE, size=10.6)
    add_picture_contain(s, FIGS["fig4_2"], 3.78, 1.02, 5.48, 3.30,
                        caption="Thesis Fig. 4-2: chromosome encoding and genetic updating mechanism")
    add_text(s, 3.94, 4.52, 5.12, 0.23,
             "The search therefore covers both material/geometric parameters and high-dimensional topology variables.",
             size=11, color=GREY, align=PP_ALIGN.CENTER)

    # Slide 9
    s = prs.slides.add_slide(blank_layout)
    clear_slide(s)
    add_background(s, BG_CONTENT)
    add_header(s, "Six Staged Optimization Tasks Were Completed Instead of a One-Step Search", 9)
    stages = [
        ("1", "6x6\nthin-film\nbaseline", "Verify structure\nand workflow"),
        ("2", "6x6\nOhmic\nverification", "Compare model\ntransfer"),
        ("3", "6x6\nOhmic\nre-optimization", "Restart under\nsheet resistance"),
        ("4", "9x9\ntopology", "Increase pattern\nresolution"),
        ("5", "9x9\np/h\nperturbation", "Fine-tune\ngeometry"),
        ("6", "12x12\nmulti-template", "Final refined\noptimization"),
    ]
    xs = [0.48, 2.02, 3.56, 5.10, 6.64, 8.18]
    for i, (num, title, desc) in enumerate(stages):
        x = xs[i]
        add_label(s, x + 0.42, 1.15, 0.38, 0.38, num, fill=ORANGE if i < 5 else RED, size=12.5)
        add_card(s, x, 1.66, 1.22, 1.08, fill=WHITE, line=ORANGE if i < 5 else RED)
        add_text(s, x + 0.08, 1.76, 1.06, 0.44, title, size=10.8, color=DARK, bold=True, align=PP_ALIGN.CENTER)
        add_text(s, x + 0.08, 2.28, 1.06, 0.34, desc, size=8.7, color=GREY, align=PP_ALIGN.CENTER)
        if i < 5:
            add_arrow_between(s, x + 1.21, 2.19, xs[i + 1] - 0.02, 2.19, color=GREY)
    add_picture_contain(s, FIGS["fig4_3"], 1.05, 3.05, 7.92, 1.34,
                        caption="Thesis Fig. 4-3: hierarchical expansion from 6x6 to 9x9 to 12x12")
    add_text(s, 1.10, 4.55, 7.80, 0.20,
             "The strategy controls search complexity while preserving the physical meaning of each improvement stage.",
             size=11, color=GREY, align=PP_ALIGN.CENTER)

    # Slide 10
    s = prs.slides.add_slide(blank_layout)
    clear_slide(s)
    add_background(s, BG_CONTENT)
    add_header(s, "Bandwidth Increased as the Topology Resolution Improved", 10)
    add_picture_contain(s, FIGS["fig5_10"], 0.50, 1.02, 5.95, 3.38,
                        caption="Thesis Fig. 5-10: RL curves at different optimization stages")
    metrics = [
        ("6x6 Ohmic", 11.20, "70.0%"),
        ("9x9 p/h", 12.32, "77.0%"),
        ("12x12 HF comp.", 13.12, "82.0%"),
        ("Final 12x12", 13.20, "82.5%"),
    ]
    add_text(s, 6.78, 1.02, 2.34, 0.32, "Continuous effective bandwidth", size=14.5, color=BLUE, bold=True)
    maxv = 13.20
    for i, (name, val, cov) in enumerate(metrics):
        y = 1.55 + i * 0.70
        add_text(s, 6.78, y - 0.07, 1.34, 0.22, name, size=10.4, color=DARK, bold=True)
        add_card(s, 6.78, y + 0.19, 1.86, 0.15, fill=RGBColor(229, 235, 239), line=RGBColor(229, 235, 239))
        add_card(s, 6.78, y + 0.19, 1.86 * val / maxv, 0.15, fill=GREEN if i == 3 else BLUE, line=GREEN if i == 3 else BLUE)
        add_text(s, 8.68, y + 0.04, 0.68, 0.28, f"{val:.2f} GHz", size=10.5, color=GREEN if i == 3 else DARK, bold=i == 3, align=PP_ALIGN.RIGHT)
        add_text(s, 8.10, y - 0.07, 0.50, 0.22, cov, size=9.8, color=GREY, align=PP_ALIGN.RIGHT)
    add_label(s, 6.82, 4.37, 2.36, 0.36, "Low-frequency boundary: 4.80 GHz", fill=RED, size=11.2)
    add_text(s, 0.82, 4.62, 8.05, 0.20,
             "The improvement is mainly reflected by wider continuous bandwidth and lower absorption starting frequency.",
             size=11, color=GREY, align=PP_ALIGN.CENTER)

    # Slide 11
    s = prs.slides.add_slide(blank_layout)
    clear_slide(s)
    add_background(s, BG_CONTENT)
    add_header(s, "The Final 12x12 Structure Achieves Broadband Absorption from 4.80 to 18.00 GHz", 11)
    add_picture_contain(s, FIGS["fig5_7"], 0.55, 1.00, 3.58, 2.08,
                        caption="Thesis Fig. 5-7: final 12x12 topology")
    add_picture_contain(s, FIGS["fig5_9"], 4.38, 1.00, 4.78, 2.08,
                        caption="Thesis Fig. 5-9: final reflection-loss curve")
    add_label(s, 0.72, 3.33, 2.65, 0.48, "4.80-18.00 GHz", fill=RED, size=17)
    add_label(s, 3.58, 3.33, 2.30, 0.48, "13.20 GHz bandwidth", fill=GREEN, size=15)
    add_label(s, 6.10, 3.33, 2.10, 0.48, "82.5% coverage", fill=BLUE, size=15)
    add_label(s, 8.38, 3.33, 0.88, 0.48, "-23.485 dB", fill=ORANGE, size=11.5)
    param_data = [
        ["Parameter", "p", "h", "Rs,x", "Rs,y"],
        ["Final value", "13.1409 mm", "10.0731 mm", "140.79 \u03a9/sq", "35.461 \u03a9/sq"],
    ]
    add_table(s, 1.05, 4.08, 7.90, 0.62, param_data,
              col_widths=[1.35, 1.55, 1.55, 1.70, 1.75], font_size=9.0)

    # Slide 12
    s = prs.slides.add_slide(blank_layout)
    clear_slide(s)
    add_background(s, BG_CONTENT)
    add_header(s, "Broadband Absorption Comes from X/Y Coupling, Multimode Response, and Ohmic Loss", 12)
    mech = [
        ("Metal backplane", "Transmission suppression", BLUE),
        ("X/Y orthogonal films", "Spatial coupling", TEAL),
        ("Patterned Ohmic Sheet", "Surface ohmic loss", GREEN),
        ("12x12 topology", "Multimode broadband response", ORANGE),
    ]
    x = 0.48
    for i, (t, sub, color) in enumerate(mech):
        add_flow_box(s, x + i * 2.33, 1.02, 1.82, 0.62, t, sub, fill=WHITE, line=color, title_size=10.2)
        if i < 3:
            add_arrow_between(s, x + i * 2.33 + 1.84, 1.33, x + (i + 1) * 2.33 - 0.08, 1.33, color=GREY)
    frames = [
        (FIGS["fig6_3"], "Electric field at 8.8 GHz\ncurrent-path coupling"),
        (FIGS["fig6_7"], "Magnetic field at 12.0 GHz\nspatial response"),
        (FIGS["fig6_11"], "Power loss at 15.5 GHz\nohmic-loss region"),
    ]
    for i, (path, cap) in enumerate(frames):
        add_picture_contain(s, path, 0.58 + i * 3.05, 1.95, 2.78, 1.58, caption=cap, caption_size=8.3)
    add_card(s, 0.80, 3.96, 8.42, 0.60, fill=WHITE, line=RED)
    add_text(s, 1.00, 4.06, 8.02, 0.32,
             "Conclusion: a broadband absorber was obtained through structure design, automated optimization, and mechanism verification.",
             size=13.2, color=DARK, bold=True, align=PP_ALIGN.CENTER)
    # Closing text on the template footer.
    add_text(s, 3.86, 5.05, 2.28, 0.28, "Thank you for your attention",
             size=12, color=WHITE, bold=True, align=PP_ALIGN.CENTER)

    prs.save(str(OUT))
    return OUT


if __name__ == "__main__":
    path = make_deck()
    print(path)
