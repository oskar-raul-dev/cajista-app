from __future__ import annotations

from html import escape

from markdown_it import MarkdownIt

from .highlight_runner import HighlightRunner

# Value of the `lang` attribute on the generated <html> element.
HTML_LANG = "en"


# Creates the MarkdownIt parser with custom rules for fenced and indented code blocks.
def build_parser(highlighter: HighlightRunner) -> MarkdownIt:
    parser = MarkdownIt(
        "commonmark",
        {"html": True, "breaks": False, "linkify": True, "typographer": False},
    ).enable("table")

    # Renders a fenced block as a `code-container` figure wrapping highlight's output.
    def fence(tokens, index, options, env):
        token = tokens[index]
        language = token.info.strip().split()[0] if token.info else ""
        fragment = highlighter.render(token.content.rstrip("\n"), language)
        return (
            f'<figure class="code-container" data-language="{escape(language, quote=True)}">\n'
            f"{fragment}\n"
            "</figure>\n"
        )

    # Renders an indented code block as a plain `verbatim-block`.
    def code_block(tokens, index, options, env):
        content = escape(tokens[index].content.rstrip("\n"))
        return f'<pre class="verbatim-block"><code>{content}</code></pre>\n'

    parser.renderer.rules["fence"] = fence
    parser.renderer.rules["code_block"] = code_block
    return parser


# Renders the Markdown into a self-contained HTML page with the CSS embedded.
def build_html(markdown_text: str, title: str, css: str, highlighter: HighlightRunner) -> str:
    body = build_parser(highlighter).render(markdown_text)
    return f"""<!doctype html>
<html lang="{HTML_LANG}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>
{css}
</style>
</head>
<body>
<main class="document">
{body}
</main>
</body>
</html>
"""
