"""
Output Utilities
================

Utilities for managing output files and directories.
"""

import os
from pathlib import Path


def get_output_dir(output_type: str = "plots") -> str:
    """
    Get the path to the outputs directory.
    
    Parameters:
    -----------
    output_type : str
        Type of output ('plots', 'data', etc.)
        
    Returns:
    --------
    str
        Absolute path to the output directory
    """
    # Get the python directory (parent of lap_simulation)
    python_dir = Path(__file__).parent.parent
    
    # Create outputs directory structure
    outputs_dir = python_dir / "outputs" 
    specific_dir = outputs_dir / output_type
    
    # Create directory if it doesn't exist
    specific_dir.mkdir(parents=True, exist_ok=True)
    
    return str(specific_dir)


def get_plot_path(filename: str) -> str:
    """
    Get the full path for saving a plot file.
    
    Parameters:
    -----------
    filename : str
        The filename for the plot (with .png extension)
        
    Returns:
    --------
    str
        Full path where the plot should be saved
    """
    return os.path.join(get_output_dir("plots"), filename)


def get_data_path(filename: str) -> str:
    """
    Get the full path for saving a data file.
    
    Parameters:
    -----------
    filename : str
        The filename for the data file
        
    Returns:
    --------
    str
        Full path where the data file should be saved
    """
    return os.path.join(get_output_dir("data"), filename)


def print_save_message(filepath: str, file_type: str = "file") -> None:
    """
    Print a standardized save message.
    
    Parameters:
    -----------
    filepath : str
        The full path where the file was saved
    file_type : str
        Type of file (e.g., 'plot', 'data', 'file')
    """
    filename = os.path.basename(filepath)
    print(f"✓ Saved {file_type} as outputs/{os.path.basename(os.path.dirname(filepath))}/{filename}")
