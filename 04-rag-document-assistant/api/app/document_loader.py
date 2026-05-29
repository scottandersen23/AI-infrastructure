import hashlib
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_SUFFIXES = {".md", ".markdown", ".txt", ".pdf"}


def load_document(path: str) -> tuple[str, str, str]:
    document_path = Path(path).expanduser().resolve()
    if not document_path.exists():
        raise FileNotFoundError(f"Document not found: {document_path}")
    if document_path.suffix.lower() not in SUPPORTED_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_SUFFIXES))
        raise ValueError(f"Unsupported document type. Supported: {supported}")

    if document_path.suffix.lower() == ".pdf":
        text = _load_pdf(document_path)
    else:
        text = document_path.read_text(encoding="utf-8")

    normalized = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if not normalized:
        raise ValueError(f"Document has no extractable text: {document_path}")

    content_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return str(document_path), normalized, content_hash


def _load_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)
