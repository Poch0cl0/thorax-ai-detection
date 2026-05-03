from pathlib import Path


def ensure_parent_dir(path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)


def safe_suffix(filename: str) -> str:
    return Path(filename).suffix.lower()
