from pathlib import Path

# When running in Docker container:
ROOTDIR = Path("/home/appuser")
if not ROOTDIR.exists():
    # When running from source:
    ROOTDIR = Path(__file__).resolve().parent.parent.parent.parent
