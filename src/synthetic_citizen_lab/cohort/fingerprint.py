"""Source fingerprint helpers for cohort reproducibility."""

from hashlib import sha256
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Return SHA-256 for a source file using bounded chunks."""
    digest = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
