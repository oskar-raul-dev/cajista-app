from __future__ import annotations

from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import RGBColor


# Sets a table cell's background fill color.
def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


# Sets a paragraph's background fill color.
def set_paragraph_shading(paragraph, fill: str) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    shd = p_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        p_pr.append(shd)
    shd.set(qn("w:fill"), fill)


# Sets single-line paragraph borders; each side is (color, size, space) or None to skip it.
def set_paragraph_borders(paragraph, *, left=None, top=None, right=None, bottom=None) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    borders = p_pr.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        p_pr.append(borders)
    for side_name, spec in (("left", left), ("top", top), ("right", right), ("bottom", bottom)):
        if not spec:
            continue
        color, size, space = spec
        element = borders.find(qn(f"w:{side_name}"))
        if element is None:
            element = OxmlElement(f"w:{side_name}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), str(size))
        element.set(qn("w:space"), str(space))
        element.set(qn("w:color"), color)


# Sets single-line borders on every edge of a table cell.
def set_cell_borders(cell, color: str = "D1D5DB", size: int = 4) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.find(qn("w:tcBorders"))
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), str(size))
        element.set(qn("w:color"), color)


# Marks a row as a header row that Word repeats on every page.
def repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    marker = OxmlElement("w:tblHeader")
    marker.set(qn("w:val"), "true")
    tr_pr.append(marker)


# Excludes a run from spelling and grammar checks.
def disable_spellcheck(run) -> None:
    r_pr = run._r.get_or_add_rPr()
    no_proof = OxmlElement("w:noProof")
    r_pr.append(no_proof)


# Appends an external hyperlink run to a paragraph (python-docx has no API for it).
def add_hyperlink(paragraph, text: str, url: str, color: str, underline: bool = True):
    part = paragraph.part
    relationship_id = part.relate_to(url, RT.HYPERLINK, is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), relationship_id)
    new_run = OxmlElement("w:r")
    run_props = OxmlElement("w:rPr")
    color_element = OxmlElement("w:color")
    color_element.set(qn("w:val"), color)
    run_props.append(color_element)
    if underline:
        underline_element = OxmlElement("w:u")
        underline_element.set(qn("w:val"), "single")
        run_props.append(underline_element)
    new_run.append(run_props)
    text_element = OxmlElement("w:t")
    text_element.text = text
    new_run.append(text_element)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink


# Returns the named character style, creating it if missing.
def ensure_character_style(styles, name: str):
    try:
        return styles[name]
    except KeyError:
        return styles.add_style(name, WD_STYLE_TYPE.CHARACTER)


# Sets a run's font color from an RRGGBB hex string.
def set_run_color(run, color: str) -> None:
    run.font.color.rgb = RGBColor.from_string(color)
