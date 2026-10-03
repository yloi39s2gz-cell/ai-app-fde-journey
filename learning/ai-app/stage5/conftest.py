"""让 pytest 从 stage5 目录运行时也能 import stage3 的 chunker 等模块。"""

from __future__ import annotations

import sys
from pathlib import Path

STAGE3 = Path(__file__).resolve().parent.parent / "stage3"
if str(STAGE3) not in sys.path:
    sys.path.insert(0, str(STAGE3))
