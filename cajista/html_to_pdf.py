from __future__ import annotations

from pathlib import Path

from weasyprint import HTML


# Renders the HTML file on disk to PDF with WeasyPrint.
def html_to_pdf(html_path: Path, output_path: Path, base_dir: Path | None = None) -> None:
    # base_dir is the Markdown's folder: relative paths (images) are written
    # relative to it, not to .build/ or output/.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    base_url = str(base_dir or html_path.parent)
    HTML(filename=str(html_path), base_url=base_url).write_pdf(str(output_path))
