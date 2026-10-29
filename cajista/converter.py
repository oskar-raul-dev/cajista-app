from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .css_tokens import load_css
from .highlight_runner import HighlightRunner
from .html_builder import build_html
from .html_to_docx import html_to_docx
from .html_to_pdf import html_to_pdf


@dataclass
class ConversionResult:
    source: Path
    outputs: list[Path]


# Runs the full pipeline for one file: Markdown → HTML → PDF/DOCX outputs.
# Refuses to overwrite existing outputs unless `overwrite` is set.
def convert_file(
    source: Path,
    config: dict,
    formats: list[str],
    output_name: str | None = None,
) -> ConversionResult:
    source = source.expanduser().resolve()
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"No existe el Markdown: {source}")

    output_dir = Path(config["project"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    name = output_name or source.stem
    overwrite = bool(config["project"].get("overwrite", False))

    css_path = Path(config["styles"]["css"])
    css, tokens = load_css(css_path)
    highlighter = HighlightRunner(
        executable=str(config["highlight"].get("executable", "highlight")),
        theme=str(config["highlight"].get("theme", "")),
        cache_dir=Path(config["project"]["cache_dir"]),
        use_cache=bool(config["highlight"].get("cache", True)),
        aliases=config["highlight"].get("aliases", {}),
    )

    markdown_text = source.read_text(encoding="utf-8")
    html_text = build_html(markdown_text, name, css, highlighter)
    outputs: list[Path] = []

    build_dir = Path(config["project"]["build_dir"])
    build_dir.mkdir(parents=True, exist_ok=True)
    html_output = output_dir / f"{name}.html"
    html_needed = "html" in formats or "pdf" in formats or bool(config["project"].get("keep_html"))
    html_path = html_output if ("html" in formats or bool(config["project"].get("keep_html"))) else build_dir / f"{name}.html"

    expected = [output_dir / f"{name}.{fmt}" for fmt in formats]
    for path in expected:
        if path.exists() and not overwrite:
            raise FileExistsError(f"La salida ya existe: {path}. Use --overwrite.")

    if html_needed:
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html_text, encoding="utf-8")

    if "html" in formats:
        outputs.append(html_output)
    if "pdf" in formats:
        pdf_path = output_dir / f"{name}.pdf"
        html_to_pdf(html_path, pdf_path, source.parent)
        outputs.append(pdf_path)
    if "docx" in formats:
        docx_path = output_dir / f"{name}.docx"
        reference = config["styles"].get("reference_docx")
        html_to_docx(
            html_text,
            docx_path,
            tokens,
            config.get("word", {}),
            Path(reference) if reference else None,
        )
        outputs.append(docx_path)

    if html_path != html_output and html_path.exists():
        html_path.unlink()
    return ConversionResult(source=source, outputs=outputs)
