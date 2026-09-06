"""Offline Markdown path and heading checker. Python 3.10+, standard library only."""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

VERSION = '0.1.0'
LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s()]+))(?:\s+["\'][^\n]*?["\'])?\s*\)')
IGNORED = {'.git', '.venv', 'node_modules', 'venv', '__pycache__'}


def visible_lines(text):
    """Preserve line numbers while ignoring fenced code and HTML comments."""
    text = re.sub(r'<!--.*?(?:-->|\Z)', lambda m: '\n' * m[0].count('\n'), text, flags=re.S)
    fence = None
    for line in text.splitlines():
        match = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
            yield ''
        elif match:
            fence = match[1]
            yield ''
        else:
            yield re.sub(r'(`+).*?\1', '', line)


def headings(text):
    # A documented subset of GitHub heading slugs, including duplicate suffixes.
    used = set()
    lines = list(visible_lines(text))
    for i, line in enumerate(lines):
        match = re.match(r'^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$', line)
        title = match[1] if match else None
        if title is None and i + 1 < len(lines) and line.strip() and re.fullmatch(r' {0,3}(?:=+|-+)\s*', lines[i+1]):
            title = line.strip()
        if title is None:
            continue
        title = re.sub(r'!?\[([^]]*)\]\([^)]*\)', r'\1', title)
        title = re.sub(r'<[^>]*>', '', title)
        base = ''.join(c for c in title.lower() if c.isalnum() or c in ' _-').replace(' ', '-')
        slug, n = base, 0
        while slug in used:
            n += 1
            slug = f'{base}-{n}'
        used.add(slug)
    return used


def check(root):
    root = root.resolve()
    issues, scanned, cache = [], 0, {}
    files = sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() == '.md' and not p.is_symlink() and not any(part in IGNORED for part in p.relative_to(root).parts))
    for source in files:
        scanned += 1
        relative = source.relative_to(root).as_posix()
        try:
            content = source.read_text(encoding='utf-8-sig')
        except (OSError, UnicodeError) as exc:
            issues.append(dict(file=relative, line=1, target='', reason=f'cannot read Markdown: {exc}'))
            continue
        for number, line in enumerate(visible_lines(content), 1):
            for match in LINK.finditer(line):
                target = match[1] or match[2]
                try:
                    url = urlsplit(target)
                    if url.scheme or url.netloc:
                        continue
                    decoded = unquote(url.path)
                    destination = ((root / decoded.lstrip('/')) if decoded.startswith('/') else (source.parent / decoded) if decoded else source).resolve()
                    reason = None
                    if not destination.is_relative_to(root):
                        reason = 'target is outside the project root'
                    elif not destination.exists():
                        reason = 'path does not exist'
                    elif url.fragment and destination.is_file() and destination.suffix.lower() == '.md':
                        if destination not in cache:
                            cache[destination] = headings(destination.read_text(encoding='utf-8-sig'))
                        if unquote(url.fragment) not in cache[destination]:
                            reason = 'heading anchor does not exist'
                except (OSError, UnicodeError, ValueError) as exc:
                    reason = f'cannot inspect target: {exc}'
                if reason:
                    issues.append(dict(file=relative, line=number, target=target, reason=reason))
    return {'files_scanned': scanned, 'issues': issues}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', default='.', help='project root (default: current directory)')
    parser.add_argument('--json', action='store_true', help='print machine-readable results')
    parser.add_argument('--version', action='version', version=VERSION)
    args = parser.parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        parser.error(f'not a directory: {root}')
    report = check(root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for issue in report['issues']:
            print(f"{issue['file']}:{issue['line']}: {issue['reason']} [{issue['target']}]")
        print(f"Checked {report['files_scanned']} Markdown files; {len(report['issues'])} issue(s).")
    return 1 if report['issues'] else 0


if __name__ == '__main__':
    sys.exit(main())
