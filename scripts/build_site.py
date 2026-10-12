"""Build the public site (site/) from the generated build guide in docs/guide.

docs/guide/index.html is written without a document skeleton so it can also be published as a
claude.ai artifact. This script wraps it in a full HTML document, adds a link to the repository,
and copies the model data next to it. Run after cad/export.py when models or the guide change:

    .venv/bin/python scripts/build_site.py
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "docs" / "guide"
SITE = ROOT / "site"
REPO_URL = "https://github.com/MeckMan2025/ClaudeBot"

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="description" content="ClaudeBot: a fully 3D-printed outdoor patrol robot. Every printed part in build order with an interactive 3D view, print settings and the bought-parts list.">
<meta name="theme-color" content="#e0601a">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="12" fill="#e0601a"/>
<rect x="14" y="22" width="36" height="18" rx="4" fill="#ffffff"/>
<circle cx="20" cy="46" r="7" fill="#1d1f21"/><circle cx="44" cy="46" r="7" fill="#1d1f21"/>
<rect x="30" y="12" width="4" height="10" fill="#ffffff"/><circle cx="32" cy="11" r="3" fill="#ffffff"/>
</svg>
"""

LINK_LINE = (
    '    <p class="links"><a href="{repo}">Source, STEP and STL files on GitHub</a> '
    '<span aria-hidden="true">&middot;</span> <a href="{repo}/blob/main/PLAN.md">Design plan</a> '
    '<span aria-hidden="true">&middot;</span> <a href="{repo}/blob/main/docs/print-guide.md">Print guide</a> '
    '<span aria-hidden="true">&middot;</span> <a href="{repo}/blob/main/electronics/BOM.csv">Bill of materials</a></p>\n'
)
LINK_CSS = "  header .links { margin: 0 0 18px; font-size: 13px; } header .links a { color: var(--accent); }\n"


def main():
    src = (GUIDE / "index.html").read_text()
    if "<!DOCTYPE" in src[:200]:
        raise SystemExit("docs/guide/index.html already has a document skeleton; expected the bare artifact form")

    # Add the link line after the intro paragraph and its style before the closing </style>.
    anchor = "</p>\n    <div class=\"summary\">"
    if anchor not in src:
        raise SystemExit("could not find the header intro paragraph to attach the repository links")
    body = src.replace(anchor, "</p>\n" + LINK_LINE.format(repo=REPO_URL) + "    <div class=\"summary\">", 1)
    body = body.replace("</style>", LINK_CSS + "</style>", 1)

    # Split the <title> and <link rel=stylesheet> (head content) from the rest.
    head_end = body.index("<style>")
    head_part, rest = body[:head_end], body[head_end:]
    style_end = rest.index("</style>") + len("</style>")
    style_part, page = rest[:style_end], rest[style_end:]

    html = HEAD + head_part + style_part + "\n</head>\n<body>" + page + "\n</body>\n</html>\n"

    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    (SITE / "index.html").write_text(html)
    (SITE / "favicon.svg").write_text(FAVICON)
    shutil.copy(GUIDE / "assembly.json", SITE / "assembly.json")
    shutil.copytree(GUIDE / "models", SITE / "models", ignore=shutil.ignore_patterns("*.stl"))

    n_models = len(list((SITE / "models").glob("*.b64.json")))
    manifest = json.loads((SITE / "models" / "manifest.json").read_text())
    print(f"site/: index.html + {n_models} models ({len(manifest) if isinstance(manifest, list) else 'ok'} in manifest)")


if __name__ == "__main__":
    main()
