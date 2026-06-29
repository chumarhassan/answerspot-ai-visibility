"""Make `backend/` importable so tests can `import diff`, `import gemini`, etc."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
