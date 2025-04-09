"""
Initialize package modules for the Open Source Manus AI project.
"""

# Make the modules importable
from pathlib import Path
import sys

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
