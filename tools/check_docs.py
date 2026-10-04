"""Check generated site's local links, assets and anchors (no external requests)."""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self, text: str):
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.leaked_fences = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])

    def handle_data(self, data):
        # Runnable metadata belongs in HTML comments; a visible fence means the
        # Markdown renderer treated executable instructions as ordinary text.
        if '```' in data:
            self.leaked_fences = True


def check_site(root: Path) -> int:
    root = root.resolve()
    pages = {p.resolve(): Page(p.read_text()) for p in root.rglob('*.html')}
    if root / 'index.html' not in pages:
        raise AssertionError('site/index.html is missing')
    errors = []
    count = 0
    for path, page in pages.items():
        if page.leaked_fences:
            errors.append(f"{path.relative_to(root)}: unrendered Markdown fence")
        for link in page.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc:
                continue
            # GitHub Pages repository prefix is permitted for root-relative links.
            raw = unquote(parts.path)
            if raw.startswith('/gnd-public/'):
                target = root / raw[len('/gnd-public/'):]
            elif raw.startswith('/'):
                target = root / raw.lstrip('/')
            else:
                target = path.parent / raw if raw else path
            target = target.resolve()
            if target.is_dir():
                target /= 'index.html'
            count += 1
            if not target.is_relative_to(root) or not target.is_file():
                errors.append(f'{path.relative_to(root)}: missing {link}')
            elif parts.fragment and target in pages:
                anchor = unquote(parts.fragment)
                if anchor not in pages[target].ids:
                    errors.append(f'{path.relative_to(root)}: absent anchor {link}')
    if errors:
        raise AssertionError('\n'.join(errors))
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    args = parser.parse_args()
    count = check_site(args.site)
    print(f'{count} local links/assets/anchors checked')


if __name__ == '__main__':
    main()
