# docpath-check

Catch broken local Markdown links before they reach your readers.

A small offline command-line tool for repository maintainers. Checks inline
links, image paths, and common Markdown heading anchors. No network requests,
API keys, accounts, or runtime dependencies. Requires Python 3.10 or later.

[中文说明](README.zh-CN.md) · [Contributing](CONTRIBUTING.md) · [License](LICENSE)

## Quick start

Download or clone this repository, then run:

```sh
python docpath.py /path/to/your/project
```

Or install from this source checkout:

```sh
python -m pip install .
docpath-check /path/to/your/project
docpath-check /path/to/your/project --json
```

Example output when a document links to a missing file:

```text
README.md:8: path does not exist [docs/install.md]
Checked 4 Markdown files; 1 issue(s).
```

Exit codes: 0 = no detected issues; 1 = issues found; 2 = invalid CLI arguments.
An empty project reports zero files. A passing check only covers supported syntax.

## Supported checks

- Inline Markdown links and images, including angle-bracket destinations.
- Relative paths, percent-encoded filenames, and repository-root paths.
- Common ATX and Setext headings, Unicode letters, duplicate heading suffixes.
- Current-document anchors and cross-document Markdown heading anchors.
- Ignores fenced code, simple inline code, HTML comments, and remote URLs.
- Skips `.git`, `.venv`, `venv`, `node_modules`, and `__pycache__` directories.
- Rejects destinations resolving outside the selected project root.

## Scope and limitations

This is a lightweight syntax subset, not a CommonMark parser or full GitHub
renderer. Reference-style links, HTML links and custom HTML anchors, nested
parentheses in destinations, multiline links, escaped brackets, and headings
with inline code are not fully supported. Such syntax may be skipped or cause
anchor mismatches. Remote URL availability is not checked. Anchor checks apply
only to `.md` files; non-Markdown targets are checked for existence.

Filesystem case sensitivity follows the operating system. Use Linux CI to detect
case mismatches that Windows may accept. Symlink Markdown source files are
skipped; link targets are resolved and checked against the project root.

## GitHub Actions

This repository includes a Windows/Linux test matrix template in
[the workflow template](ci/github-actions.yml). To enable CI, copy it to `.github/workflows/check.yml` and commit using a GitHub session with workflow write permission. CI is not enabled in this initial upload. To check another repository,
install this tool from a reviewed source checkout and run `docpath-check .`
in that repository. No write permissions or secrets are required.

## Development

```sh
python -m unittest discover -s tests -v
python docpath.py .
```

## Roadmap

- Reference-style link support with regression fixtures.
- More complete Markdown parsing and heading compatibility.
- Configurable exclusions and editor-friendly diagnostics.

Version 0.1.0 is an initial release. Contributions and real-world bug reports
are welcome; see [contribution guidance](CONTRIBUTING.md).
