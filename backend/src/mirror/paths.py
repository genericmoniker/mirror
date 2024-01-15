"""Path constants for the Mirror application."""
from pathlib import Path

# When running in Docker container:
ROOT_DIR = Path("/home/appuser")
if not ROOT_DIR.exists():
    # When running from source:
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

INSTANCE_DIR = ROOT_DIR / "instance"
