from __future__ import annotations

import importlib.metadata
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from .css_tokens import load_css


# Runs a `--version`-style command and returns (success, first output line).
def _command_version(command: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        text = (result.stdout or result.stderr).strip().splitlines()
        return result.returncode == 0, text[0] if text else "encontrado"
    except Exception as exc:
        return False, str(exc)


# Checks Python, packages, highlight, the CSS and the optional QA tools.
# Returns the report rows and whether every required one is OK.
def doctor(config: dict) -> tuple[list[tuple[str, str, bool, bool]], bool]:
    rows: list[tuple[str, str, bool, bool]] = []
    rows.append(("Python", platform.python_version(), sys.version_info >= (3, 10), True))

    for package in ("weasyprint", "python-docx", "markdown-it-py", "beautifulsoup4", "lxml", "PyYAML", "tinycss2", "typer"):
        try:
            version = importlib.metadata.version(package)
            rows.append((package, version, True, True))
        except importlib.metadata.PackageNotFoundError:
            rows.append((package, "no instalado", False, True))

    highlight_exe = str(config["highlight"].get("executable", "highlight"))
    ok, version = _command_version([highlight_exe, "--version"])
    rows.append(("highlight", version, ok, True))

    css_path = Path(config["styles"]["css"])
    try:
        load_css(css_path)
        rows.append(("CSS", str(css_path), True, True))
    except Exception as exc:
        rows.append(("CSS", str(exc), False, True))

    libreoffice = config.get("qa", {}).get("libreoffice_executable") or shutil.which("soffice")
    if libreoffice:
        ok, version = _command_version([str(libreoffice), "--version"])
        rows.append(("LibreOffice", version, ok, False))
    else:
        rows.append(("LibreOffice", "no encontrado", False, False))

    pdftoppm = config.get("qa", {}).get("pdftoppm_executable") or shutil.which("pdftoppm")
    if pdftoppm:
        ok, version = _command_version([str(pdftoppm), "-v"])
        rows.append(("pdftoppm", version, ok, False))
    else:
        rows.append(("pdftoppm", "no encontrado", False, False))

    required_ok = all(ok for _, _, ok, required in rows if required)
    return rows, required_ok
