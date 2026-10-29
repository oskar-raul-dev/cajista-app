from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG: dict[str, Any] = {
    "project": {
        "output_dir": "./output",
        "build_dir": "./.build",
        "cache_dir": "./.cache/highlight",
        "overwrite": False,
        "keep_html": False,
    },
    "formats": {"docx": True, "pdf": True, "html": False, "zip": False},
    "styles": {
        "css": "./styles/default.css",
        "docx_from_css": True,
        "reference_docx": None,
    },
    "highlight": {
        "executable": "highlight",
        "theme": "",
        "inline_css": True,
        "fragment": True,
        "cache": True,
        "fallback": "plain",
        "aliases": {
            "js": "javascript",
            "jsx": "javascript",
            "ts": "typescript",
            "tsx": "typescript",
            "py": "python",
            "sh": "bash",
            "shell": "bash",
            "ps1": "powershell",
            "yml": "yaml",
            "c++": "cpp",
            "c#": "csharp",
            "cs": "csharp",
            "md": "markdown",
            "html5": "html",
        },
    },
    "pdf": {"engine": "weasyprint", "presentational_hints": False},
    "word": {
        "split_code_by_line": True,
        "repeat_table_header": True,
        "disable_spellcheck_in_code": True,
        "keep_headings_with_next": True,
    },
    "qa": {
        "enabled": False,
        "render_docx": True,
        "render_pdf": True,
        "libreoffice_executable": None,
        "pdftoppm_executable": None,
    },
    "batch": {
        "recursive": False,
        "pattern": "*.md",
        "preserve_directories": False,
    },
}


# Recursively merges `override` into a copy of `base`; nested dicts merge, other values replace.
def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# Turns a possibly relative path into an absolute one, relative to `base_dir`.
def _resolve_path(value: str | None, base_dir: Path) -> str | None:
    if not value:
        return value
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return str(path.resolve())


# Builds the config from the defaults plus the optional YAML, resolving paths
# against the YAML's folder (or the CWD, with the repo's default CSS).
def load_config(config_path: Path | None = None) -> dict[str, Any]:
    config = copy.deepcopy(DEFAULT_CONFIG)
    base_dir = Path.cwd()

    if config_path:
        config_path = config_path.expanduser().resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"No existe el archivo YAML: {config_path}")
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            raise ValueError("La raíz del YAML debe ser un objeto/mapa.")
        config = deep_merge(config, loaded)
        base_dir = config_path.parent
    else:
        project_root = Path(__file__).resolve().parent.parent
        default_css = project_root / "styles" / "default.css"
        config["styles"]["css"] = str(default_css)

    for section, key in [
        ("project", "output_dir"),
        ("project", "build_dir"),
        ("project", "cache_dir"),
        ("styles", "css"),
        ("styles", "reference_docx"),
        ("qa", "libreoffice_executable"),
        ("qa", "pdftoppm_executable"),
    ]:
        value = config.get(section, {}).get(key)
        if value:
            config[section][key] = _resolve_path(str(value), base_dir)

    return config


# Returns a copy of the config with the non-None CLI options written into it.
def apply_cli_overrides(config: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    result = copy.deepcopy(config)

    mapping: dict[str, tuple[str, str]] = {
        "css": ("styles", "css"),
        "output_dir": ("project", "output_dir"),
        "highlight_exe": ("highlight", "executable"),
        "highlight_theme": ("highlight", "theme"),
        "overwrite": ("project", "overwrite"),
        "keep_html": ("project", "keep_html"),
        "cache": ("highlight", "cache"),
        "qa": ("qa", "enabled"),
    }

    for name, value in overrides.items():
        if value is None or name not in mapping:
            continue
        section, key = mapping[name]
        if name in {"css", "output_dir"}:
            value = str(Path(value).expanduser().resolve())
        result[section][key] = value

    return result


# Returns the deduplicated output formats, from the CLI or else the config; rejects unknown ones.
def resolve_formats(config: dict[str, Any], requested: list[str] | None) -> list[str]:
    valid = {"docx", "pdf", "html"}
    if requested:
        formats = [item.lower() for item in requested]
    else:
        formats = [name for name, enabled in config["formats"].items() if enabled and name in valid]

    unknown = sorted(set(formats) - valid)
    if unknown:
        raise ValueError(f"Formatos no válidos: {', '.join(unknown)}")
    if not formats:
        raise ValueError("Debe habilitar al menos un formato: docx, pdf o html.")
    return list(dict.fromkeys(formats))
