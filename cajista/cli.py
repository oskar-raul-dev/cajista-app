from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path
from typing import Annotated

import typer

from .configuration import apply_cli_overrides, load_config, resolve_formats
from .converter import convert_file
from .css_tokens import load_css
from .diagnostics import doctor as run_doctor

app = typer.Typer(help="Convierte Markdown a HTML, DOCX y PDF usando highlight para el código.", no_args_is_help=True)


# Loads the YAML config and applies the CLI flag overrides on top.
def _prepare_config(
    config_path: Path | None,
    css: Path | None,
    output_dir: Path | None,
    highlight_exe: str | None,
    highlight_theme: str | None,
    overwrite: bool | None,
    keep_html: bool | None,
    no_cache: bool,
    qa: bool | None,
):
    config = load_config(config_path)
    return apply_cli_overrides(
        config,
        css=css,
        output_dir=output_dir,
        highlight_exe=highlight_exe,
        highlight_theme=highlight_theme,
        overwrite=overwrite,
        keep_html=keep_html,
        cache=False if no_cache else None,
        qa=qa,
    )


# `convert` command: converts one Markdown file to the requested formats.
@app.command()
def convert(
    source: Annotated[Path, typer.Argument(help="Archivo Markdown de entrada")],
    config: Annotated[Path | None, typer.Option("--config", help="Ruta del YAML")] = None,
    css: Annotated[Path | None, typer.Option("--css", help="Ruta del CSS visual")] = None,
    format: Annotated[list[str] | None, typer.Option("--format", "-f", help="docx, pdf o html; repetible")] = None,
    output_dir: Annotated[Path | None, typer.Option("--output-dir", "-o")] = None,
    output_name: Annotated[str | None, typer.Option("--output-name")] = None,
    highlight_exe: Annotated[str | None, typer.Option("--highlight-exe")] = None,
    highlight_theme: Annotated[str | None, typer.Option("--highlight-theme")] = None,
    keep_html: Annotated[bool | None, typer.Option("--keep-html/--no-keep-html")] = None,
    overwrite: Annotated[bool | None, typer.Option("--overwrite/--no-overwrite")] = None,
    no_cache: Annotated[bool, typer.Option("--no-cache")] = False,
    qa: Annotated[bool | None, typer.Option("--qa/--no-qa")] = None,
):
    """Convierte un archivo Markdown."""
    try:
        resolved = _prepare_config(config, css, output_dir, highlight_exe, highlight_theme, overwrite, keep_html, no_cache, qa)
        formats = resolve_formats(resolved, format)
        result = convert_file(source, resolved, formats, output_name)
        for output in result.outputs:
            typer.echo(str(output))
    except Exception as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(1)


# `batch` command: converts every matching Markdown in a folder, optionally zipping the outputs.
@app.command()
def batch(
    input_dir: Annotated[Path, typer.Argument(help="Directorio con Markdown")],
    config: Annotated[Path | None, typer.Option("--config")] = None,
    css: Annotated[Path | None, typer.Option("--css")] = None,
    format: Annotated[list[str] | None, typer.Option("--format", "-f")] = None,
    output_dir: Annotated[Path | None, typer.Option("--output-dir", "-o")] = None,
    pattern: Annotated[str, typer.Option("--pattern")] = "*.md",
    recursive: Annotated[bool, typer.Option("--recursive")] = False,
    zip_path: Annotated[Path | None, typer.Option("--zip")] = None,
    highlight_exe: Annotated[str | None, typer.Option("--highlight-exe")] = None,
    highlight_theme: Annotated[str | None, typer.Option("--highlight-theme")] = None,
    keep_html: Annotated[bool | None, typer.Option("--keep-html/--no-keep-html")] = None,
    overwrite: Annotated[bool | None, typer.Option("--overwrite/--no-overwrite")] = None,
    no_cache: Annotated[bool, typer.Option("--no-cache")] = False,
):
    """Convierte todos los Markdown de un directorio y puede generar un ZIP."""
    try:
        resolved = _prepare_config(config, css, output_dir, highlight_exe, highlight_theme, overwrite, keep_html, no_cache, None)
        formats = resolve_formats(resolved, format)
        folder = input_dir.expanduser().resolve()
        files = sorted(folder.rglob(pattern) if recursive else folder.glob(pattern))
        if not files:
            raise FileNotFoundError(f"No se encontraron archivos con patrón {pattern} en {folder}")
        outputs: list[Path] = []
        for source in files:
            result = convert_file(source, resolved, formats)
            outputs.extend(result.outputs)
            typer.echo(f"OK {source.name}")
        if zip_path:
            zip_path = zip_path.expanduser().resolve()
            zip_path.parent.mkdir(parents=True, exist_ok=True)
            if zip_path.exists() and not resolved["project"].get("overwrite"):
                raise FileExistsError(f"El ZIP ya existe: {zip_path}")
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                for output in outputs:
                    archive.write(output, arcname=output.name)
            typer.echo(str(zip_path))
    except Exception as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(1)


# `validate` command: checks the Markdown is readable and the YAML/CSS load, without converting.
@app.command()
def validate(
    source: Annotated[Path, typer.Argument(help="Markdown que se desea validar")],
    config: Annotated[Path | None, typer.Option("--config")] = None,
    css: Annotated[Path | None, typer.Option("--css")] = None,
):
    """Valida entrada, YAML y CSS sin convertir."""
    try:
        resolved = _prepare_config(config, css, None, None, None, None, None, False, None)
        source = source.expanduser().resolve()
        if not source.exists():
            raise FileNotFoundError(source)
        source.read_text(encoding="utf-8")
        load_css(Path(resolved["styles"]["css"]))
        typer.echo("OK")
    except Exception as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(1)


# `doctor` command: prints dependency versions; exits 1 if a required one is missing.
@app.command()
def doctor(
    config: Annotated[Path | None, typer.Option("--config")] = None,
    css: Annotated[Path | None, typer.Option("--css")] = None,
):
    """Muestra versiones y disponibilidad de componentes."""
    resolved = _prepare_config(config, css, None, None, None, None, None, False, None)
    rows, required_ok = run_doctor(resolved)
    for name, version, ok, required in rows:
        state = "OK" if ok else ("FALTA" if required else "opcional / no encontrado")
        typer.echo(f"{name:18} {version:45} {state}")
    if not required_ok:
        raise typer.Exit(1)
