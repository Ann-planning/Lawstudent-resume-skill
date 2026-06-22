#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def check_docx_structure(docx_path: Path, *, expected_cn_font: str) -> list[str]:
    issues = []
    if not docx_path.exists():
        return [f"Missing file: {docx_path}"]
    try:
        with zipfile.ZipFile(docx_path) as zf:
            names = set(zf.namelist())
            required = {
                "[Content_Types].xml",
                "_rels/.rels",
                "word/document.xml",
                "word/styles.xml",
                "word/fontTable.xml",
            }
            missing = required - names
            if missing:
                issues.append(f"Missing OOXML parts: {sorted(missing)}")
            font_xml = zf.read("word/fontTable.xml").decode("utf-8")
            if expected_cn_font not in font_xml:
                issues.append(f"fontTable.xml does not contain expected Chinese font: {expected_cn_font}")
    except zipfile.BadZipFile:
        issues.append("Invalid DOCX zip structure")
    return issues


def try_render_pdf(docx_path: Path) -> tuple[bool, str]:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return False, "Skipped render QA: soffice/libreoffice not available"

    with tempfile.TemporaryDirectory() as tmpdir:
        outdir = Path(tmpdir)
        cmd = [
            soffice,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(outdir),
            str(docx_path),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        pdf_path = outdir / (docx_path.stem + ".pdf")
        if proc.returncode != 0 or not pdf_path.exists():
            stderr = proc.stderr.strip() or proc.stdout.strip() or "unknown error"
            return False, f"Render QA failed: {stderr}"
        return True, f"Render QA passed: {pdf_path.name} generated"


def try_text_extract(docx_path: Path) -> tuple[bool, str]:
    textutil = shutil.which("textutil")
    if not textutil:
        return False, "Skipped text extraction QA: textutil not available"
    proc = subprocess.run(
        [textutil, "-convert", "txt", "-stdout", str(docx_path)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip() or "unknown error"
        return False, f"Text extraction QA failed: {err}"
    if not proc.stdout.strip():
        return False, "Text extraction QA failed: extracted text is empty"
    return True, "Text extraction QA passed"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify bundled resume DOCX structure and optional renderability.")
    parser.add_argument("docx", help="Path to the .docx file to verify.")
    parser.add_argument("--expected-cn-font", default="STKaiti", help="Expected Chinese font family in fontTable.xml.")
    args = parser.parse_args()

    docx_path = Path(args.docx)
    issues = check_docx_structure(docx_path, expected_cn_font=args.expected_cn_font)
    if issues:
        for issue in issues:
            print(issue)
        sys.exit(1)

    ok_text, message_text = try_text_extract(docx_path)
    print("OOXML structure OK")
    print(message_text)
    if not ok_text and "Skipped text extraction QA" not in message_text:
        sys.exit(1)

    ok, message = try_render_pdf(docx_path)
    print(message)
    if not ok and "Skipped render QA" not in message:
        sys.exit(1)


if __name__ == "__main__":
    main()
