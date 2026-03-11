"""Pytest configuration to add root directory to Python path."""

import sys
from pathlib import Path

# Add the root directory to Python path so imports from root modules work
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
