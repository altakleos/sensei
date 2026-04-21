"""Atomic file-write helper for irreplaceable learner state.

Uses write-to-temp + fsync + rename(2) to guarantee that a crash or
interrupt cannot leave the target file truncated or half-written.
"""

from __future__ import annotations

import contextlib
import os
from pathlib import Path


def atomic_write_text(path: Path, content: str) -> None:
    """Write *content* to *path* atomically.

    Algorithm:
    1. Write to a sibling .tmp file (same directory → same filesystem).
    2. fsync the file descriptor so bytes reach storage before rename.
    3. os.replace() for an atomic POSIX rename(2); also safe on Windows.
    4. On any exception, remove the tmp file to avoid leaving debris.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        with tmp.open("w", encoding="utf-8") as fh:
            fh.write(content)
            # Flush Python's buffer then sync to storage before we rename.
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        with contextlib.suppress(OSError):
            tmp.unlink(missing_ok=True)
        raise
