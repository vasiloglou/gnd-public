"""Render the three DC2 drafts, verbatim from the checked pages, into one checkpoint page."""
import re, sys
from pathlib import Path
import markdown
here = Path(__file__).parent
GH = "https://github.com/vasiloglou/gnd-public/blob/main/docs/"
LINKS = [
    (r'href="(?:\.\./reference/)?disclosure\.md#([^"]+)"', r'href="#\1"'),
    (r'href="(?:\.\./reference/|reference/)?disclosure\.md"', 'href="#part-reference"'),
    (r'href="(?:\.\./how-to/)?disclosure-mode\.md#([^"]+)"', r'href="#\1"'),
    (r'href="(?:\.\./how-to/)?disclosure-mode\.md"', 'href="#part-howto"'),
    (r'href="why-not\.md(#[^"]*)?"', lambda m: f'href="{GH}reference/why-not.md{m.group(1) or ""}"'),
    (r'href="repair-a-missing-claim\.md"', f'href="{GH}how-to/repair-a-missing-claim.md"'),
    (r'href="\.\./guides/exports\.md"', f'href="{GH}guides/exports.md"'),
]
def render(name):
    src = re.sub(r"<!--.*?-->\n?", "", (here / name).read_text(), flags=re.S)
    body = markdown.markdown(src, extensions=["fenced_code", "tables", "admonition", "toc"])
    for pattern, repl in LINKS:
        body = re.sub(pattern, repl, body)
    return re.sub(r'(</code></pre>\s*)<pre><code class="language-text">', r'\1<pre class="out"><code class="language-text">', body)
page = (here / "shell.html").read_text()
for key, name in (("REFERENCE", "docs/reference/disclosure.md"), ("HOWTO", "docs/how-to/disclosure-mode.md"), ("CHANGES", "changes.md")):
    page = page.replace(f"@@{key}@@", render(name))
(here / "dc2.html").write_text(page)
print(len(page), "bytes;", len(re.findall(r'href="[^"#h][^"]*\.md', page)), "unresolved relative .md links")
