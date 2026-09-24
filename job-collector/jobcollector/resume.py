from __future__ import annotations

from pathlib import Path


def read_resume(path: str | Path) -> str:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as e:
            raise SystemExit("PDF resume needs `pip install pypdf`") from e
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(p)).pages)
    if suffix == ".docx":
        try:
            import docx
        except ImportError as e:
            raise SystemExit("DOCX resume needs `pip install python-docx`") from e
        return "\n".join(par.text for par in docx.Document(str(p)).paragraphs)
    return p.read_text(encoding="utf-8", errors="ignore")
