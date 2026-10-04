"""Kit de diapositivas — replica el sistema de diseño de Teoria-Labs-6-9-Capas-Red.pptx
para que las presentaciones de la Unidad III se vean igual que las de la Unidad II.

Tokens: 16:9 (13.333 x 7.5 in) · navy 1F3864 + naranja E87C1E · Calibri + Consolas.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ---------------------------------------------------------------- tokens
NAVY   = RGBColor(0x1F, 0x38, 0x64)
BLUE   = RGBColor(0x2E, 0x5C, 0x9A)
ORANGE = RGBColor(0xE8, 0x7C, 0x1E)
TEAL   = RGBColor(0x17, 0x8C, 0x8C)
GREEN  = RGBColor(0x1E, 0x88, 0x49)
RED    = RGBColor(0xC0, 0x39, 0x2B)
LIGHT  = RGBColor(0xF2, 0xF5, 0xFA)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
TEXT   = RGBColor(0x44, 0x44, 0x44)
SUB    = RGBColor(0xC9, 0xD6, 0xEC)
GRAY   = RGBColor(0x8A, 0x8A, 0x8A)
CODEBG = RGBColor(0x14, 0x25, 0x40)

W, H = 13.333, 7.5
FOOT = "Redes de Computadoras · 8410 · Unidad III"


def new_deck():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    return prs


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


# ---------------------------------------------------------------- primitivas
def rect(slide, x, y, w, h, fill):
    s = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def _split_bold(txt):
    """Divide 'a **b** c' en [('a ',False), ('b',True), (' c',False)]."""
    out, buf, i = [], "", 0
    while i < len(txt):
        if txt.startswith("**", i):
            j = txt.find("**", i + 2)
            if j > 0:
                if buf:
                    out.append((buf, False)); buf = ""
                out.append((txt[i + 2:j], True))
                i = j + 2
                continue
        buf += txt[i]
        i += 1
    if buf:
        out.append((buf, False))
    return out or [("", False)]


def text(slide, x, y, w, h, runs, size=14, color=TEXT, bold=False,
         align=PP_ALIGN.LEFT, font="Calibri", space=4, anchor=MSO_ANCHOR.TOP):
    """runs: str, o lista de párrafos; cada párrafo str o lista de (texto, dict).
    Dentro de un texto plano, **así** marca negrita."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space)
        chunks = para if isinstance(para, list) else [(para, {})]
        for txt, opt in chunks:
            for seg, is_bold in _split_bold(txt):
                if not seg:
                    continue
                r = p.add_run()
                r.text = seg
                f = r.font
                f.name = opt.get("font", font)
                f.size = Pt(opt.get("size", size))
                f.bold = True if is_bold else opt.get("bold", bold)
                f.italic = opt.get("italic", False)
                f.color.rgb = opt.get("color", color)
    return box


def header(slide, title, subtitle=None):
    """Barra superior de las diapositivas de contenido."""
    rect(slide, 0, 0, W, 1.05, NAVY)
    rect(slide, 0, 1.05, W, 0.06, ORANGE)
    text(slide, 0.45, 0.13, 12.4, 0.45, title, size=26, color=WHITE, bold=True)
    if subtitle:
        text(slide, 0.45, 0.60, 12.4, 0.35, subtitle, size=13, color=SUB)


def footer(slide, n, part=""):
    label = f"{FOOT}" + (f" · {part}" if part else "")
    text(slide, 0.45, 7.08, 9.0, 0.3, label, size=10, color=GRAY)
    text(slide, 12.13, 7.08, 0.8, 0.3, str(n), size=10, color=GRAY, align=PP_ALIGN.RIGHT)


def notes(slide, body):
    slide.notes_slide.notes_text_frame.text = body


# ---------------------------------------------------------------- bloques
def bullets(slide, items, x, y, w, size=15, gap=7, color=TEXT, h=None):
    """items: lista de str o (str, nivel)."""
    out = []
    for it in items:
        lvl = 0
        if isinstance(it, tuple):
            it, lvl = it
        mark = "▸ " if lvl == 0 else "– "
        sz = size if lvl == 0 else size - 1.5
        col = color if lvl == 0 else GRAY
        out.append([(mark, {"color": ORANGE, "bold": True, "size": sz}),
                    (it, {"color": col, "size": sz})])
    return text(slide, x, y, w, h or 0.5, out, size=size, space=gap)


def callout(slide, x, y, w, h, title, lines, accent=ORANGE, size=12):
    rect(slide, x, y, w, h, LIGHT)
    rect(slide, x, y, 0.08, h, accent)
    text(slide, x + 0.22, y + 0.08, w - 0.4, 0.3, title, size=13, color=NAVY, bold=True)
    body = []
    for ln in lines:
        # un párrafo ya armado es una lista de tuplas (texto, opts) o una tupla suelta
        if isinstance(ln, (tuple, list)):
            body.append(list(ln))
        else:
            body.append([("▸ ", {"color": accent, "bold": True, "size": size}),
                         (ln, {"color": TEXT, "size": size})])
    text(slide, x + 0.22, y + 0.42, w - 0.42, h - 0.5, body, size=size, space=4)


def code(slide, x, y, w, h, lines, size=12):
    rect(slide, x, y, w, h, CODEBG)
    if isinstance(lines, str):
        lines = lines.split("\n")
    body = []
    for ln in lines:
        if isinstance(ln, tuple):
            body.append([(ln[0], {"font": "Consolas", "size": size,
                                  "color": ln[1] if len(ln) > 1 else WHITE})])
        else:
            body.append([(ln, {"font": "Consolas", "size": size, "color": SUB})])
    text(slide, x + 0.2, y + 0.12, w - 0.35, h - 0.2, body, size=size, space=2)


def table(slide, data, x, y, w, col_w=None, size=12, row_h=0.34, header_h=0.38):
    rows, cols = len(data), len(data[0])
    shp = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(0.3))
    tbl = shp.table
    tbl.first_row = True
    tbl.horz_banding = False
    if col_w:
        for i, cw in enumerate(col_w):
            tbl.columns[i].width = Inches(cw)
    tbl.rows[0].height = Inches(header_h)
    for r in range(1, rows):
        tbl.rows[r].height = Inches(row_h)
    for r in range(rows):
        for c in range(cols):
            cell = tbl.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY if r == 0 else (LIGHT if r % 2 else WHITE)
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.05)
            cell.margin_top = Inches(0.02)
            cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            base_bold = (r == 0) or (c == 0 and rows > 2)
            for seg, is_bold in _split_bold(str(data[r][c])):
                if not seg:
                    continue
                run = p.add_run()
                run.text = seg
                f = run.font
                f.name = "Calibri"
                f.size = Pt(size if r else size - 0.5)
                f.bold = True if is_bold else base_bold
                f.color.rgb = WHITE if r == 0 else TEXT
    return tbl


def flow(slide, steps, x, y, w, h=0.85, gap=0.30, colors=None, size=12):
    """steps: lista de (titulo, descripcion)."""
    n = len(steps)
    bw = (w - gap * (n - 1)) / n
    colors = colors or [BLUE, TEAL, GREEN, ORANGE, NAVY, RED]
    for i, (t, d) in enumerate(steps):
        bx = x + i * (bw + gap)
        rect(slide, bx, y, bw, h, colors[i % len(colors)])
        text(slide, bx + 0.08, y + 0.07, bw - 0.16, 0.32, t, size=size + 1,
             color=WHITE, bold=True, align=PP_ALIGN.CENTER)
        text(slide, bx + 0.08, y + 0.40, bw - 0.16, h - 0.45, d, size=size - 1.5,
             color=SUB, align=PP_ALIGN.CENTER)
        if i < n - 1:
            text(slide, bx + bw, y + h / 2 - 0.22, gap, 0.4, "→", size=20,
                 color=NAVY, bold=True, align=PP_ALIGN.CENTER)


def kpi(slide, items, x, y, w, h=1.05, gap=0.22):
    """items: lista de (valor, etiqueta)."""
    n = len(items)
    bw = (w - gap * (n - 1)) / n
    for i, (val, lab) in enumerate(items):
        bx = x + i * (bw + gap)
        rect(slide, bx, y, bw, h, LIGHT)
        rect(slide, bx, y, bw, 0.06, ORANGE)
        text(slide, bx + 0.1, y + 0.14, bw - 0.2, 0.4, val, size=19, color=NAVY,
             bold=True, align=PP_ALIGN.CENTER)
        text(slide, bx + 0.1, y + 0.58, bw - 0.2, 0.4, lab, size=11, color=TEXT,
             align=PP_ALIGN.CENTER)


# ---------------------------------------------------------------- páginas tipo
def cover(prs, kicker, title, subtitle, topics, part_label, duration):
    s = blank(prs)
    rect(s, 0, 0, W, H, NAVY)
    rect(s, 0, 4.55, W, 0.08, ORANGE)
    text(s, 0.9, 1.30, 11.5, 0.5, kicker, size=14, color=ORANGE, bold=True)
    text(s, 0.9, 1.95, 11.5, 1.7, title, size=40, color=WHITE, bold=True)
    text(s, 0.9, 4.85, 11.5, 1.3, subtitle, size=20, color=SUB)
    body = [[("▸ ", {"color": ORANGE, "bold": True, "size": 13}),
             (t, {"color": SUB, "size": 13})] for t in topics]
    text(s, 0.9, 6.15, 11.0, 0.8, body, size=13, space=2)
    text(s, 0.45, 7.08, 11.0, 0.3, f"{FOOT} · {part_label} · {duration}",
         size=10, color=GRAY)
    return s


def divider(prs, badge, title, subtitle, items, minutes):
    s = blank(prs)
    rect(s, 0, 0, W, H, NAVY)
    rect(s, 0, 2.90, W, 0.06, ORANGE)
    rect(s, 0.9, 1.15, 2.2, 0.75, ORANGE)
    text(s, 0.9, 1.27, 2.2, 0.6, badge, size=26, color=WHITE, bold=True,
         align=PP_ALIGN.CENTER)
    text(s, 0.9, 2.0, 11.5, 0.85, title, size=40, color=WHITE, bold=True)
    text(s, 0.9, 3.15, 11.5, 0.5, subtitle, size=18, color=SUB)
    body = [[("▸ ", {"color": ORANGE, "bold": True, "size": 16}),
             (t, {"color": WHITE, "size": 16})] for t in items]
    text(s, 0.9, 3.95, 11.2, 1.8, body, size=16, space=6)
    text(s, 0.45, 7.08, 9.0, 0.3, FOOT, size=10, color=GRAY)
    text(s, 11.0, 7.08, 1.9, 0.3, minutes, size=10, color=ORANGE, align=PP_ALIGN.RIGHT)
    return s


def content(prs, title, subtitle, part, n):
    s = blank(prs)
    header(s, title, subtitle)
    footer(s, n, part)
    return s
