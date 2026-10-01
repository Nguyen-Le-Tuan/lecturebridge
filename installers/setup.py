"""Entry point that works with managed Python before project dependencies exist."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lecturebridge.installation import main

if __name__ == "__main__":
    raise SystemExit(main())
