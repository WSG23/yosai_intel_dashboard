#!/usr/bin/env python3
"""Quick fix for upload issues"""

import re
from pathlib import Path


def fix_css_imports():
    """Remove problematic CSS imports"""
    css_files = [
        Path("assets/css/main.css"),
        Path("assets/main.css"),
    ]

    for css_file in css_files:
        if css_file.exists():
            content = css_file.read_text()
            # Comment out @import lines
            new_content = re.sub(r'^@import.*$', r'/* \g<0> */', content, flags=re.MULTILINE)

            if content != new_content:
                backup = css_file.with_suffix('.css.backup')
                css_file.rename(backup)
                css_file.write_text(new_content)
                print(f"✅ Fixed imports in {css_file}")


def fix_style_properties():
    """Fix React style property warnings"""
    files_to_fix = [
        Path("dashboard/layout/navbar.py"),
        Path("components/navbar.py"),
        Path("pages/file_upload.py"),
    ]

    for file_path in files_to_fix:
        if file_path.exists():
            content = file_path.read_text()

            # Fix common style property issues
            fixes = [
                (r'"text-align"', '"textAlign"'),
                (r'"min-height"', '"minHeight"'),
                (r'"text-decoration"', '"textDecoration"'),
            ]

            new_content = content
            for old, new in fixes:
                new_content = re.sub(old, new, new_content)

            if content != new_content:
                file_path.write_text(new_content)
                print(f"✅ Fixed style properties in {file_path}")


if __name__ == "__main__":
    fix_css_imports()
    fix_style_properties()
    print("🚀 All fixes applied! Restart your app.")
