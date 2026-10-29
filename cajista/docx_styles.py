from __future__ import annotations

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

from .css_tokens import StyleTokens, docx_length
from .docx_ooxml import ensure_character_style, set_paragraph_borders, set_paragraph_shading


# Applies font family, size, color and weight to a Word style, for every script type.
def _set_style_font(style, name: str, size: float, color: str, bold: bool | None = None, italic: bool | None = None):
    style.font.name = name
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        style.font.bold = bold
    if italic is not None:
        style.font.italic = italic
    r_pr = style.element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        r_fonts.set(qn(f"w:{attr}"), name)


# Sets page size/margins and the Word styles (Normal, Headings, code, quote) from the CSS tokens.
def configure_document(document: Document, tokens: StyleTokens, keep_headings_with_next: bool = True) -> None:
    section = document.sections[0]
    page_size = tokens.get("--page-size", "A4").strip().upper()
    if page_size == "LETTER":
        section.page_width = docx_length("8.5in")
        section.page_height = docx_length("11in")
    else:
        section.page_width = docx_length("21cm")
        section.page_height = docx_length("29.7cm")
    section.top_margin = docx_length(tokens.get("--page-margin-top", "2.5cm"))
    section.right_margin = docx_length(tokens.get("--page-margin-right", "2.5cm"))
    section.bottom_margin = docx_length(tokens.get("--page-margin-bottom", "2.5cm"))
    section.left_margin = docx_length(tokens.get("--page-margin-left", "2.5cm"))

    styles = document.styles
    body_font = tokens.font("--font-body", "Arial")
    mono_font = tokens.font("--font-mono", "Consolas")
    text_color = tokens.color("--color-text", "1F2937")
    primary = tokens.color("--color-primary", "2C3E50")
    accent = tokens.color("--color-accent", "64748B")
    surface = tokens.color("--color-surface", "F3F4F6")
    surface_alt = tokens.color("--color-surface-alt", "F9FAFB")
    border = tokens.color("--color-border", "D1D5DB")

    normal = styles["Normal"]
    _set_style_font(normal, body_font, tokens.points("--font-size-body", 11), text_color)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.25

    for level in range(1, 7):
        style = styles[f"Heading {level}"]
        _set_style_font(style, body_font, tokens.points(f"--h{level}-size", 11), primary, bold=True)
        style.paragraph_format.space_before = Pt(12)
        style.paragraph_format.space_after = Pt(5)
        style.paragraph_format.keep_with_next = keep_headings_with_next

    code_inline = ensure_character_style(styles, "Code Inline")
    _set_style_font(code_inline, mono_font, tokens.points("--font-size-body", 11) - 0.5, text_color)

    for style_name, fill in (("Code Block", surface), ("Verbatim Block", surface_alt), ("Quote", surface_alt)):
        try:
            style = styles[style_name]
        except KeyError:
            style = styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
        if style_name == "Quote":
            _set_style_font(style, body_font, tokens.points("--font-size-body", 11), tokens.color("--color-text-alt", "374151"))
        else:
            _set_style_font(style, mono_font, tokens.points("--font-size-code", 9.2), text_color)
        style.paragraph_format.space_before = Pt(0)
        style.paragraph_format.space_after = Pt(0)
        style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
