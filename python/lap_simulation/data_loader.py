"""
Data Loader Module
==================

Utilities for loading MATLAB data files (.mat) and Excel files used in the lap simulation.
"""

import numpy as np
import pandas as pd
from scipy.io import loadmat
from typing import Dict, Any, Tuple, Optional
import os


def load_mat_data(filepath: str) -> Dict[str, Any]:
    """
    Load MATLAB .mat file and return data dictionary.
    
    Parameters:
    -----------
    filepath : str
        Path to the .mat file
        
    Returns:
    --------
    Dict[str, Any]
        Dictionary containing the loaded data
    """
    try:
        data = loadmat(filepath)
        # Remove MATLAB metadata keys
        cleaned_data = {k: v for k, v in data.items() if not k.startswith('__')}
        return cleaned_data
    except Exception as e:
        raise FileNotFoundError(f"Could not load {filepath}: {str(e)}")


def load_tire_data(data_dir: str) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Load all tire-related data files.
    
    Parameters:
    -----------
    data_dir : str
        Path to the data files directory
        
    Returns:
    --------
    Tuple[Dict, Dict, Dict]
        (lateral_force_model, lateral_coefficients, longitudinal_force_data)
    """
    # Load lateral tire force model
    lateral_model_path = os.path.join(data_dir, "A1654run21_MF52_Fy_GV12.mat")
    lateral_model = load_mat_data(lateral_model_path)
    
    # Load Magic Formula coefficients
    lateral_coeff_path = os.path.join(data_dir, "A1654run21_MF52_Fy_12.mat")
    lateral_coefficients = load_mat_data(lateral_coeff_path)
    
    # Load longitudinal tire data
    longitudinal_path = os.path.join(data_dir, "Hoosier_R25B_18.0x7.5-10_FX_12psi.mat")
    longitudinal_data = load_mat_data(longitudinal_path)
    
    return lateral_model, lateral_coefficients, longitudinal_data


def load_track_coordinates(filepath: str) -> Dict[str, np.ndarray]:
    """
    Load track coordinates from Excel file, specifically from the 'Scaled' sheet.
    
    Parameters:
    -----------
    filepath : str
        Path to the Excel file containing track coordinates
        
    Returns:
    --------
    Dict[str, np.ndarray]
        Dictionary containing 'outside_track' and 'inside_track' coordinates
    """
    try:
        # Read from the 'Scaled' sheet specifically
        df = pd.read_excel(filepath, sheet_name='Scaled')
        
        # The structure is:
        # Row 0: NaN, "Outside Track", NaN, "Inside Track", NaN
        # Row 1: NaN, "x", "y", "x", "y"  
        # Row 2+: Point labels, outside_x, outside_y, inside_x, inside_y
        
        # Skip the header rows and extract data
        data_rows = df.iloc[2:].copy()  # Start from row 2 (0-indexed)
        
        # Extract coordinates, handling potential NaN values
        outside_x = pd.to_numeric(data_rows.iloc[:, 1], errors='coerce')
        outside_y = pd.to_numeric(data_rows.iloc[:, 2], errors='coerce')
        inside_x = pd.to_numeric(data_rows.iloc[:, 3], errors='coerce')
        inside_y = pd.to_numeric(data_rows.iloc[:, 4], errors='coerce')
        
        # Remove rows with NaN values
        valid_outside = ~(outside_x.isna() | outside_y.isna())
        valid_inside = ~(inside_x.isna() | inside_y.isna())
        
        outside_track = np.column_stack((
            np.array(outside_x[valid_outside].values),
            np.array(outside_y[valid_outside].values)
        ))
        
        inside_track = np.column_stack((
            np.array(inside_x[valid_inside].values),
            np.array(inside_y[valid_inside].values)
        ))
        
        print(f"Loaded {len(outside_track)} outside track points and {len(inside_track)} inside track points")
        
        return {
            'outside_track': outside_track,
            'inside_track': inside_track
        }
        
    except Exception as e:
        raise FileNotFoundError(f"Could not load track coordinates from {filepath}: {str(e)}")


def load_racing_line_data(data_dir: str, track_type: str = "endurance") -> Dict[str, Any]:
    """
    Load racing line data for specified track type.
    
    Parameters:
    -----------
    data_dir : str
        Path to the data files directory
    track_type : str
        Type of track ("endurance" or "autocross")
        
    Returns:
    --------
    Dict[str, Any]
        Racing line data
    """
    filename = f"{track_type}_racing_line.mat"
    filepath = os.path.join(data_dir, filename)
    return load_mat_data(filepath)


class DataManager:
    """
    Centralized data management for lap simulation.
    """
    
    def __init__(self, base_dir: str):
        """
        Initialize data manager.
        
        Parameters:
        -----------
        base_dir : str
            Base directory containing data files
        """
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, "Data Files")
        
        # Cached data
        self._tire_data = None
        self._track_data = {}
        
    def get_tire_data(self) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """Get tire data, loading if necessary."""
        if self._tire_data is None:
            self._tire_data = load_tire_data(self.data_dir)
        return self._tire_data
    
    def get_track_coordinates(self, track_name: str) -> Dict[str, np.ndarray]:
        """
        Get track coordinates for specified track.
        
        Parameters:
        -----------
        track_name : str
            Name of track file (e.g., "Endurance_Coordinates_1.xlsx")
            
        Returns:
        --------
        Dict[str, np.ndarray]
            Dictionary containing 'outside_track' and 'inside_track' coordinates
        """
        if track_name not in self._track_data:
            filepath = os.path.join(self.base_dir, track_name)
            self._track_data[track_name] = load_track_coordinates(filepath)
        return self._track_data[track_name]
    
    def get_racing_line(self, track_type: str = "endurance") -> Dict[str, Any]:
        """Get racing line data for specified track type."""
        return load_racing_line_data(self.data_dir, track_type)
