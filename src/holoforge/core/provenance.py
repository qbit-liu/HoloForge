"""Runtime provenance helpers."""

from __future__ import annotations

from contextlib import redirect_stdout
from functools import lru_cache
import hashlib
import io
import platform
import sys
from typing import Dict
import warnings

import numpy as np
import scipy

from holoforge import __version__


def runtime_versions() -> Dict[str, str]:
    """Return privacy-safe runtime and numerical-build provenance."""

    return {
        "holoforge": __version__,
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "byteorder": sys.byteorder,
        "platform_system": platform.system() or "unknown",
        "platform_machine": platform.machine() or "unknown",
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "numerical_build_sha256": _numerical_build_digest(),
    }


@lru_cache(maxsize=1)
def _numerical_build_digest() -> str:
    """Hash NumPy/SciPy build reports without exposing their local paths."""

    sections = []
    for label, show in (
        ("numpy", np.__config__.show),
        ("scipy", scipy.__config__.show),
    ):
        buffer = io.StringIO()
        with warnings.catch_warnings(), redirect_stdout(buffer):
            warnings.simplefilter("ignore")
            show()
        sections.append(f"[{label}]\n{buffer.getvalue().strip()}\n")
    return hashlib.sha256("".join(sections).encode("utf-8")).hexdigest()
