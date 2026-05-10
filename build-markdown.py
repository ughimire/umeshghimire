#!/usr/bin/env python3
"""Auto-generate Markdown files for the AI/LLM "View as Markdown" feature.

Run after editing any page's HTML:

    python3 build-markdown.py

It walks each public page, extracts the <main> content, and writes a
clean Markdown version at the matching root-level .md path. The HTML
"View as Markdown" banner already links to these files.

No external dependencies — uses Python's standard library only.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent

# (HTML source path, output Markdown path, optional override H1)
PAGES = [
    ("index.html",            "index.md"),
    ("about/index.html",      "about.md"),
    ("services/index.html",   "services.md"),
    ("portfolio/index.html",  "portfolio.md"),
    ("experience/index.html", "experience.md"),
    ("cv/index.html",         "cv.md"),
    ("contact/index.html",    "contact.md"),
]


# ----- inline → markdown ------------------------------------------------

def inline_to_md(s: str) -> str:
    """Convert an inline HTML fragment to plain text + light Markdown."""
    # Replace <br> with newline
    s = re.sub(r"<\s*br\s*/?\s*>", "\n", s, flags=re.I)
    # Insert spaces between adjacent inline blocks so e.g. <strong>12+</strong><span>Years</span> becomes "**12+** Years"
    s = re.sub(r"</(strong|b|em|i|span|small|code)>(?=<)", r"</\1> ", s, flags=re.I)
    # bold
    s = re.sub(r"</?\s*(strong|b)\s*>", "**", s, flags=re.I)
    # italic
    s = re.sub(r"</?\s*(em|i)\s*>", "*", s, flags=re.I)
    # code
    s = re.sub(r"</?\s*code\s*>", "`", s, flags=re.I)

    # links: <a href="X">Y</a>  →  [Y](X)  — drop links with no visible text
    def link_repl(m: re.Match) -> str:
        href = m.group(1)
        inner = inline_to_md(m.group(2))
        if not inner.strip():
            return ""
        return f"[{inner.strip()}]({href})"

    s = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
               link_repl, s, flags=re.I | re.S)

    # strip remaining tags
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    # normalize whitespace within a line
    s = re.sub(r"[ \t]+", " ", s)
    # trim each line and drop empty trailing
    lines = [ln.rstrip() for ln in s.splitlines()]
    return "\n".join(lines).strip()


# ----- structural helpers ----------------------------------------------

def remove_block(s: str, tag: str) -> str:
    return re.sub(rf"<{tag}\b[^>]*>.*?</{tag}>", "", s, flags=re.S | re.I)


def remove_class_block(s: str, cls: str) -> str:
    """Remove any element whose class contains `cls` (assumes well-formed open/close on same tag name)."""
    pattern = re.compile(
        rf'<(?P<tag>[a-zA-Z0-9]+)([^>]*\bclass="[^"]*\b{re.escape(cls)}\b[^"]*"[^>]*)>(.*?)</(?P=tag)>',
        re.S | re.I,
    )
    prev = None
    while prev != s:
        prev = s
        s = pattern.sub("", s)
    return s


def extract_main(html_text: str) -> str:
    m = re.search(r"<main[^>]*>(.*?)</main>", html_text, re.S | re.I)
    return m.group(1) if m else html_text


# ----- block-level walker ----------------------------------------------

BLOCK_SPLIT = re.compile(
    r"(<h[1-6][^>]*>.*?</h[1-6]>"
    r"|<p\b[^>]*>.*?</p>"
    r"|<ul\b[^>]*>.*?</ul>"
    r"|<ol\b[^>]*>.*?</ol>"
    r"|<dl\b[^>]*>.*?</dl>"
    r"|<details\b[^>]*>.*?</details>"
    r"|<blockquote\b[^>]*>.*?</blockquote>"
    r"|<pre\b[^>]*>.*?</pre>"
    r"|<article\b[^>]*>.*?</article>"
    r"|<section\b[^>]*>.*?</section>"
    r"|<aside\b[^>]*>.*?</aside>"
    r"|<header\b[^>]*>.*?</header>"
    r"|<footer\b[^>]*>.*?</footer>"
    r"|<div\b[^>]*>.*?</div>"
    r"|<hr\s*/?>)",
    re.S | re.I,
)


def render_blocks(s: str, out: list[str], heading_offset: int = 0,
                  drop_first_h1: bool = False) -> None:
    """Walk the HTML and append Markdown lines to `out`."""
    pieces = BLOCK_SPLIT.split(s)
    state = {"dropped_first_h1": not drop_first_h1}

    for piece in pieces:
        if not piece or not piece.strip():
            continue
        p = piece.strip()

        # Heading
        m = re.match(r"<(h[1-6])\b[^>]*>(.*?)</\1>", p, re.S | re.I)
        if m:
            level = int(m.group(1)[1]) + heading_offset
            level = max(1, min(6, level))
            text = inline_to_md(m.group(2))
            if not text:
                continue
            if level == 1 and not state["dropped_first_h1"]:
                state["dropped_first_h1"] = True
                continue
            out.append("")
            out.append("#" * level + " " + text)
            out.append("")
            continue

        # Paragraph
        if re.match(r"<p\b", p, re.I):
            # Skip breadcrumbs, ledes that duplicate the page hero, banner content.
            if re.search(r'class="[^"]*\bbreadcrumbs\b', p, re.I):
                continue
            text = inline_to_md(p)
            if text:
                out.append(text)
                out.append("")
            continue

        # Lists
        if re.match(r"<(ul|ol)\b", p, re.I):
            ordered = bool(re.match(r"<ol\b", p, re.I))
            items = re.findall(r"<li\b[^>]*>(.*?)</li>", p, flags=re.S | re.I)
            for i, item in enumerate(items, 1):
                bullet = f"{i}." if ordered else "-"
                # If a list item itself contains nested headings/sublists, render fully
                inner = item.strip()
                if re.search(r"<(h[1-6]|ul|ol|p)\b", inner, re.I):
                    sub: list[str] = []
                    render_blocks(inner, sub, heading_offset=heading_offset + 1, drop_first_h1=False)
                    body = "\n".join(line for line in sub if line.strip())
                    indented = "\n".join(("  " + ln if ln else "") for ln in body.splitlines())
                    leading = inline_to_md(re.sub(r"<(h[1-6]|ul|ol|p|div)\b.*?</\1>", "", inner, flags=re.S|re.I))
                    head = leading.strip()
                    if head:
                        out.append(f"{bullet} {head}")
                    if indented.strip():
                        out.append(indented.lstrip())
                else:
                    line = inline_to_md(inner)
                    if line:
                        out.append(f"{bullet} {line}")
            out.append("")
            continue

        # Description list (Quick facts on About page, CV skills)
        if re.match(r"<dl\b", p, re.I):
            pairs = re.findall(r"<dt\b[^>]*>(.*?)</dt>\s*<dd\b[^>]*>(.*?)</dd>", p, flags=re.S | re.I)
            for dt, dd in pairs:
                key = inline_to_md(dt)
                val = inline_to_md(dd)
                if key or val:
                    out.append(f"- **{key}:** {val}".rstrip())
            out.append("")
            continue

        # FAQ <details><summary>Q</summary><p>A</p></details>
        if re.match(r"<details\b", p, re.I):
            sm = re.search(r"<summary\b[^>]*>(.*?)</summary>", p, re.S | re.I)
            rest = re.sub(r"<summary\b[^>]*>.*?</summary>", "", p, flags=re.S | re.I)
            rest = re.sub(r"</?details[^>]*>", "", rest, flags=re.I)
            q = inline_to_md(sm.group(1)) if sm else ""
            if q:
                out.append("")
                out.append(f"**{q}**")
            sub: list[str] = []
            render_blocks(rest, sub, heading_offset=heading_offset, drop_first_h1=False)
            out.extend(sub)
            continue

        # Blockquote
        if re.match(r"<blockquote\b", p, re.I):
            inner = re.sub(r"</?blockquote[^>]*>", "", p, flags=re.I)
            for line in inline_to_md(inner).splitlines():
                if line.strip():
                    out.append("> " + line.strip())
            out.append("")
            continue

        # Pre
        if re.match(r"<pre\b", p, re.I):
            inner = re.sub(r"</?pre[^>]*>|</?code[^>]*>", "", p, flags=re.I)
            inner = html.unescape(inner)
            out.append("```")
            out.extend(inner.strip("\n").splitlines() or [""])
            out.append("```")
            out.append("")
            continue

        # HR
        if re.match(r"<hr\b", p, re.I):
            out.append("---")
            out.append("")
            continue

        # Container blocks (article, section, div, etc.)
        m = re.match(r"<([a-zA-Z0-9]+)\b[^>]*>(.*)</\1>$", p, re.S | re.I)
        if m:
            inner = m.group(2)
            # If the container has no block-level children, render its inline text as a paragraph
            if not re.search(r"<(h[1-6]|p|ul|ol|dl|details|blockquote|pre|article|section|aside|header|footer|div)\b",
                              inner, re.I):
                text = inline_to_md(inner)
                if text:
                    out.append(text)
                    out.append("")
            else:
                render_blocks(inner, out, heading_offset=heading_offset, drop_first_h1=False)


# ----- top-level driver ------------------------------------------------

def build_one(src: str, dst: str) -> None:
    html_text = (ROOT / src).read_text(encoding="utf-8")
    body = extract_main(html_text)

    # Strip noise we don't want in the markdown view
    body = re.sub(r"<script\b.*?</script>", "", body, flags=re.S | re.I)
    body = re.sub(r"<style\b.*?</style>", "", body, flags=re.S | re.I)
    body = re.sub(r"<form\b.*?</form>", "", body, flags=re.S | re.I)
    body = re.sub(r"<svg\b.*?</svg>", "", body, flags=re.S | re.I)
    body = remove_class_block(body, "md-banner")
    body = remove_class_block(body, "cta-banner")
    body = remove_class_block(body, "breadcrumbs")
    body = remove_class_block(body, "logos")
    body = remove_class_block(body, "hero__trust")
    body = remove_class_block(body, "socials")
    body = remove_class_block(body, "profile-card")
    body = remove_class_block(body, "hero__bg")
    body = remove_class_block(body, "cv__actions")
    body = remove_class_block(body, "section--cta")
    body = remove_class_block(body, "service__icon")
    body = remove_class_block(body, "project__media")
    # Decorative inline labels — drop entire span
    body = remove_class_block(body, "kicker")
    body = remove_class_block(body, "eyebrow")
    body = remove_class_block(body, "chips")
    body = remove_class_block(body, "hp")
    # Drop the section/wrapper for the markdown banner aside on every page
    body = re.sub(r'<aside\b[^>]*class="[^"]*\bmd-banner\b[^"]*"[^>]*>.*?</aside>', "", body, flags=re.S | re.I)

    out: list[str] = []
    render_blocks(body, out, heading_offset=0, drop_first_h1=False)

    # Final clean-up
    md = "\n".join(out).strip() + "\n"
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"^[ \t]+\Z", "", md, flags=re.M)
    md = re.sub(r" +\n", "\n", md)
    # Drop empty headings (heading immediately followed by another heading or end)
    md = re.sub(r"^(#+ [^\n]+)\n+(?=#+ |\Z)", "", md, flags=re.M)
    # Collapse leading-space wraps inside paragraphs (<p> with newlines in source)
    md = re.sub(r"\n +(?=\S)", " ", md)

    (ROOT / dst).write_text(md, encoding="utf-8")
    print(f"  {src:30s}  →  {dst}  ({len(md):,} chars)")


def main() -> int:
    print("Building markdown views from HTML…")
    for entry in PAGES:
        src, dst = entry[0], entry[1]
        if not (ROOT / src).exists():
            print(f"  ! missing source: {src}", file=sys.stderr)
            continue
        build_one(src, dst)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
