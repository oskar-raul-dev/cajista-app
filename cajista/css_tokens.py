from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import tinycss2
from docx.shared import Cm, Inches, Mm, Pt


ROOT_PATTERN = re.compile(r":root\s*\{(?P<body>.*?)\}", re.DOTALL | re.IGNORECASE)
VAR_PATTERN = re.compile(r"(--[\w-]+)\s*:\s*([^;]+);")
HEX_PATTERN = re.compile(r"#([0-9a-fA-F]{6})")


DEFAULT_TOKENS = {
    "--page-size": "A4",
    "--page-margin-top": "2.5cm",
    "--page-margin-right": "2.5cm",
    "--page-margin-bottom": "2.5cm",
    "--page-margin-left": "2.5cm",
    "--font-body": 'Arial, "Liberation Sans", sans-serif',
    "--font-mono": 'Consolas, "Liberation Mono", monospace',
    "--font-size-body": "11pt",
    "--font-size-code": "9.2pt",
    "--line-height-body": "1.5",
    "--line-height-code": "1.4",
    "--color-primary": "#2c3e50",
    "--color-accent": "#64748b",
    "--color-text": "#1f2937",
    "--color-text-alt": "#374151",
    "--color-border": "#d1d5db",
    "--color-surface": "#f3f4f6",
    "--color-surface-alt": "#f9fafb",
    "--color-link": "#2c3e50",
    "--h1-size": "24pt",
    "--h2-size": "20pt",
    "--h3-size": "16pt",
    "--h4-size": "14pt",
    "--h5-size": "12pt",
    "--h6-size": "11pt",
    "--table-font-size": "9.5pt",
}


@dataclass(frozen=True)
class StyleTokens:
    values: dict[str, str]

    # Returns a token's raw value, falling back to the built-in default.
    def get(self, name: str, default: str | None = None) -> str:
        if default is None:
            default = DEFAULT_TOKENS.get(name, "")
        return self.values.get(name, default)

    # Returns a token's hex color as uppercase RRGGBB (no `#`), as Word expects.
    def color(self, name: str, default: str) -> str:
        value = self.get(name, default)
        match = HEX_PATTERN.search(value)
        return match.group(1).upper() if match else default.replace("#", "").upper()

    # Returns the first family of a CSS font stack.
    def font(self, name: str, default: str) -> str:
        value = self.get(name, default)
        first = value.split(",", 1)[0].strip().strip('"\'')
        return first or default

    # Returns a token's length converted to points.
    def points(self, name: str, default: float) -> float:
        return length_to_points(self.get(name, f"{default}pt"), default)


# Reads and validates the CSS file, and extracts the `--*` tokens from its first `:root` block.
def load_css(css_path: Path) -> tuple[str, StyleTokens]:
    if not css_path.exists():
        raise FileNotFoundError(f"No existe el CSS: {css_path}")
    css = css_path.read_text(encoding="utf-8")
    errors = [token for token in tinycss2.parse_stylesheet(css) if token.type == "error"]
    if errors:
        raise ValueError(f"CSS inválido: {errors[0].message}")

    values = dict(DEFAULT_TOKENS)
    match = ROOT_PATTERN.search(css)
    if match:
        for name, value in VAR_PATTERN.findall(match.group("body")):
            values[name.strip()] = value.strip()
    return css, StyleTokens(values)


# Converts a CSS length (pt, px, cm, mm, in) to points; returns `default` if unparsable.
def length_to_points(value: str, default: float = 0.0) -> float:
    text = value.strip().lower()
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*(pt|px|cm|mm|in)?", text)
    if not match:
        return default
    number = float(match.group(1))
    unit = match.group(2) or "pt"
    return {
        "pt": number,
        "px": number * 0.75,
        "cm": number * 72 / 2.54,
        "mm": number * 72 / 25.4,
        "in": number * 72,
    }[unit]


# Converts a CSS length to a python-docx Length object.
def docx_length(value: str):
    text = value.strip().lower()
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*(pt|px|cm|mm|in)?", text)
    if not match:
        return Pt(0)
    number = float(match.group(1))
    unit = match.group(2) or "pt"
    if unit == "cm":
        return Cm(number)
    if unit == "mm":
        return Mm(number)
    if unit == "in":
        return Inches(number)
    if unit == "px":
        return Pt(number * 0.75)
    return Pt(number)
