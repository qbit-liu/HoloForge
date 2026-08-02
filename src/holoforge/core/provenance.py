"""Runtime provenance helpers."""

from __future__ import annotations

import platform
from typing import Dict

import numpy as np
import scipy

from holoforge import __version__


def runtime_versions() -> Dict[str, str]:
    """Return versions needed to reproduce a numerical result."""

    return {
        "holoforge": __version__,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
    }
