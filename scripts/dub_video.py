import sys
from pathlib import Path

# Allow running from the project root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dubber.cli import main

if __name__ == "__main__":
    main()
