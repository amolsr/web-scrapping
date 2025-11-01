"""Utility functions for web scrapers."""

import os
from pathlib import Path


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to the project root
    """
    # This file is in scrapers/utils/, so go up two levels
    return Path(__file__).parent.parent.parent


def get_output_path(filename: str) -> str:
    """
    Get the absolute path to the output directory.
    
    Args:
        filename: Name of the output file (e.g., 'data.csv')
        
    Returns:
        Absolute path to the output file
    """
    project_root = get_project_root()
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)
    return str(output_dir / filename)


def get_output_dir() -> str:
    """
    Get the absolute path to the output directory.
    
    Returns:
        Absolute path to the output directory
    """
    project_root = get_project_root()
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)
    return str(output_dir)

