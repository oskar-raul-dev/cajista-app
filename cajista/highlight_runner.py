from __future__ import annotations

import hashlib
import html
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Mapping


LANGUAGE_EXTENSIONS = {
    "bash": ".sh", "c": ".c", "cpp": ".cpp", "csharp": ".cs",
    "css": ".css", "dart": ".dart", "dockerfile": ".dockerfile",
    "elixir": ".ex", "go": ".go", "graphql": ".graphql",
    "groovy": ".groovy", "haskell": ".hs", "html": ".html",
    "java": ".java", "javascript": ".js", "json": ".json",
    "julia": ".jl", "kotlin": ".kt", "lua": ".lua",
    "makefile": ".mk", "markdown": ".md", "matlab": ".m",
    "objective-c": ".m", "perl": ".pl", "php": ".php",
    "powershell": ".ps1", "python": ".py", "r": ".r",
    "ruby": ".rb", "rust": ".rs", "scala": ".scala", "scss": ".scss",
    "sql": ".sql", "swift": ".swift", "toml": ".toml",
    "typescript": ".ts", "vue": ".vue", "xml": ".xml", "yaml": ".yaml",
}


class HighlightRunner:
    # Stores settings, normalizes aliases, creates the cache dir and records the highlight version.
    def __init__(
        self,
        executable: str,
        theme: str,
        cache_dir: Path,
        use_cache: bool,
        aliases: Mapping[str, str] | None = None,
    ) -> None:
        self.executable = executable
        self.theme = theme.strip()
        self.cache_dir = cache_dir
        self.use_cache = use_cache
        self.aliases = {str(k).lower(): str(v).lower() for k, v in (aliases or {}).items()}
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.version = self._version_or_unknown()

    # Tells whether the highlight executable can be found.
    def available(self) -> bool:
        return bool(shutil.which(self.executable) or Path(self.executable).exists())

    # Returns highlighted HTML for a code block, using the cache when possible.
    # Falls back to plain HTML when there is no language, no highlight, or it fails.
    def render(self, code: str, language: str | None) -> str:
        normalized = self.normalize_language(language)
        if not normalized or not self.available():
            return self.plain_fragment(code)

        cache_file = self.cache_dir / f"{self._cache_key(code, normalized)}.html"
        if self.use_cache and cache_file.exists():
            return self._normalize_fragment(cache_file.read_text(encoding="utf-8"))

        try:
            fragment = self._invoke(code, normalized)
        except Exception:
            fragment = self.plain_fragment(code)

        if self.use_cache:
            cache_file.write_text(fragment, encoding="utf-8")
        return fragment

    # Maps a fence info string to a highlight language name via the aliases.
    def normalize_language(self, language: str | None) -> str:
        if not language:
            return ""
        name = language.strip().split()[0].lower()
        return self.aliases.get(name, name)

    # Returns the highlight version string, or "unavailable"; part of the cache key.
    def _version_or_unknown(self) -> str:
        try:
            result = subprocess.run(
                [self.executable, "--version"], capture_output=True, text=True,
                check=True, timeout=10,
            )
            return (result.stdout or result.stderr).strip()
        except Exception:
            return "unavailable"

    # Runs highlight on a temp file and returns the normalized HTML fragment.
    def _invoke(self, code: str, language: str) -> str:
        extension = LANGUAGE_EXTENSIONS.get(language, f".{language}" if language else ".txt")
        with tempfile.TemporaryDirectory(prefix="cajista-highlight-") as temp:
            temp_dir = Path(temp)
            source = temp_dir / f"source{extension}"
            output = temp_dir / "fragment.html"
            source.write_text(code, encoding="utf-8")

            command = [
                self.executable,
                "--out-format=html",
                "--fragment",
                "--inline-css",
                f"--syntax={language}",
                f"--input={source}",
                f"--output={output}",
            ]
            if self.theme:
                command.append(f"--style={self.theme}")

            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            if result.returncode != 0 or not output.exists():
                error = (result.stderr or result.stdout).strip()
                raise RuntimeError(f"highlight falló ({language}): {error}")
            fragment = output.read_text(encoding="utf-8")
            return self._normalize_fragment(fragment)

    # Strips the XML prolog and ensures the fragment is wrapped in <pre><code>.
    @staticmethod
    def _normalize_fragment(fragment: str) -> str:
        # With --fragment, highlight 4.x returns only the <span>s, without <pre>.
        # Without <pre>, HTML/PDF lose whitespace and the DOCX drops the block,
        # so it is wrapped here. Idempotent for cached results.
        fragment = fragment.replace('<?xml version="1.0" encoding="UTF-8"?>', "").strip()
        if not fragment.lstrip().lower().startswith("<pre"):
            fragment = f"<pre><code>{fragment}</code></pre>"
        return fragment

    # Hashes version, theme, language, code and options into the cache file name.
    def _cache_key(self, code: str, language: str) -> str:
        payload = json.dumps(
            {
                "version": self.version,
                "theme": self.theme,
                "language": language,
                "code": code,
                "inline_css": True,
                "fragment": True,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # Returns the code escaped in a plain `verbatim-block`, with no highlighting.
    @staticmethod
    def plain_fragment(code: str) -> str:
        return f'<pre class="verbatim-block"><code>{html.escape(code)}</code></pre>'
