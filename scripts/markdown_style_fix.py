#!/usr/bin/env python3
"""
Simple markdown style fixer for this repo.

Fixes (safe, idempotent):
- Ensure fenced code blocks (```...) are surrounded by blank lines
- Ensure headings have a blank line before them
- Ensure lists have a blank line before the first list item

Run with --fix to apply changes. It will back up files with .bak extension.
"""

import re
import sys
from pathlib import Path


def process_text(text: str) -> (str, list):
    lines = text.splitlines()
    changed = []
    out = []
    i = 0
    in_fence = False
    while i < len(lines):
        line = lines[i]
        # detect fence
        m_fence = re.match(r"^(```+)", line)
        if m_fence:
            # opening or closing
            if not in_fence:
                # ensure blank line before opening fence
                if len(out) > 0 and out[-1].strip() != "":
                    out.append("")
                    changed.append((i, "blank-before-opening-fence"))
                out.append(line)
                in_fence = True
            else:
                # closing fence
                out.append(line)
                in_fence = False
                # if next original line is not blank, ensure a blank after closing fence
                if i + 1 < len(lines) and lines[i + 1].strip() != "":
                    out.append("")
                    changed.append((i, "blank-after-closing-fence"))
            i += 1
            continue

        # headings: ensure blank line before
        if re.match(r"^#{1,6}\s", line):
            if len(out) > 0 and out[-1].strip() != "":
                out.append("")
                changed.append((i, "blank-before-heading"))
            out.append(line)
            i += 1
            continue

        # lists: unordered (- or *) or ordered (1.) ensure blank line before start
        if re.match(r"^[\-\*\+]\s+|^\d+\.\s+", line):
            if len(out) > 0 and out[-1].strip() != "":
                out.append("")
                changed.append((i, "blank-before-list"))
            out.append(line)
            i += 1
            continue

        out.append(line)
        i += 1

    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), changed


def find_md_files(root: Path):
    for p in root.rglob("*.md"):
        # skip .git directory
        if ".git" in p.parts:
            continue
        yield p


def main():
    fix = "--fix" in sys.argv
    repo = Path(__file__).resolve().parents[1]
    changed_files = []
    for p in find_md_files(repo):
        text = p.read_text(encoding="utf8")
        new_text, changes = process_text(text)
        if changes and new_text != text:
            print(f"Would fix {p.relative_to(repo)}: {len(changes)} changes")
            for c in changes[:5]:
                print("  -", c[1], "at line", c[0])
            if fix:
                bak = p.with_suffix(p.suffix + ".bak")
                bak.write_text(text, encoding="utf8")
                p.write_text(new_text, encoding="utf8")
                print("  Applied fixes and wrote backup to", bak.relative_to(repo))
            changed_files.append(p)

    if not changed_files:
        print("No markdown style issues found.")
    else:
        print("\nTotal files with changes:", len(changed_files))


if __name__ == "__main__":
    main()
