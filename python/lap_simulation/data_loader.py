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


def load_comprehensive_track_data(base_dir=None):
    """
    Load all track-related data including coordinates, racing lines, and simulation results.
    
    Parameters:
    -----------
    base_dir : str, optional
        Base directory containing track files (defaults to parent directory)
        
    Returns:
    --------
    dict
        Dictionary containing comprehensive track data with velocity information
    """
    from scipy.ndimage import gaussian_filter1d
    from .physics import calculate_realistic_velocities, calculate_cumulative_distance
    
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    track_data = {}
    
    # Load track coordinate data
    try:
        # Load endurance track data
        endurance_file = os.path.join(base_dir, 'Endurance_Coordinates_1.xlsx')
        endurance_data = load_track_coordinates(endurance_file)
        if endurance_data:
            track_data['endurance'] = endurance_data
            outside_points = len(endurance_data['outside_track'])
            inside_points = len(endurance_data['inside_track'])
            print(f"✓ Endurance: {outside_points} outside, {inside_points} inside boundary points")
        
        # Load autocross track  
        autocross_file = os.path.join(base_dir, "Autocross_Coordinates_2.xlsx")
        autocross_data = load_track_coordinates(autocross_file)
        if autocross_data:
            track_data['autocross'] = autocross_data
            outside_points = len(autocross_data['outside_track'])
            inside_points = len(autocross_data['inside_track'])
            print(f"✓ Autocross: {outside_points} outside, {inside_points} inside boundary points")
            
    except Exception as e:
        print(f"⚠ Error loading track coordinates: {e}")
    
    # Load racing line and simulation data for velocity information
    try:
        print("🏎️ Loading racing line and velocity data...")
        data_dir = os.path.join(base_dir, "Data Files")
        
        # Try to load racing line data files
        racing_files = {
            'endurance': "endurance_racing_line.mat",
            'autocross': "autocross_racing_line.mat"
        }
        
        for track_type, filename in racing_files.items():
            filepath = os.path.join(data_dir, filename)
            if os.path.exists(filepath):
                try:
                    racing_data = load_mat_data(filepath)
                    if track_type in track_data:
                        track_data[track_type]['racing_line'] = racing_data
                        print(f"✓ {track_type.capitalize()} racing line loaded")
                        print(f"  Available keys: {list(racing_data.keys())}")
                except Exception as e:
                    print(f"⚠ Could not load {track_type} racing line: {e}")
        
    except Exception as e:
        print(f"⚠ Error loading racing line data: {e}")
    
    # Generate synthetic velocity data based on track curvature
    for track_type in ['endurance', 'autocross']:
        if track_type in track_data:
            track_data[track_type] = _add_velocity_data(track_data[track_type], track_type)
    
    return track_data


def _add_velocity_data(track_data, track_type):
    """
    Add realistic velocity data based on track geometry and racing dynamics.
    
    Parameters:
    -----------
    track_data : dict
        Track data for a specific track
    track_type : str
        Type of track ('endurance' or 'autocross')
        
    Returns:
    --------
    dict
        Track data with added velocity information
    """
    from scipy.ndimage import gaussian_filter1d
    from .physics import calculate_realistic_velocities, calculate_cumulative_distance
    
    # Create racing line from track boundaries if not available
    if 'racing_line' not in track_data:
        outside = track_data['outside_track']
        inside = track_data['inside_track']
        
        # Create center line between boundaries
        min_points = min(len(outside), len(inside))
        outside = outside[:min_points]
        inside = inside[:min_points]
        
        racing_x = (outside[:, 0] + inside[:, 0]) / 2
        racing_y = (outside[:, 1] + inside[:, 1]) / 2
        
        # Smooth the racing line
        racing_x = gaussian_filter1d(racing_x, sigma=3)
        racing_y = gaussian_filter1d(racing_y, sigma=3)
        
        track_data['racing_line'] = {
            'x': racing_x,
            'y': racing_y
        }
        print(f"✓ Generated synthetic racing line for {track_type}: {len(racing_x)} points")
    else:
        # Extract coordinates from loaded racing line data
        racing_data = track_data['racing_line']
        x_coords, y_coords = _extract_racing_line_coordinates(racing_data)
        track_data['racing_line'] = {
            'x': x_coords,
            'y': y_coords
        }
    
    # Calculate velocity using physics module
    x_coords = track_data['racing_line']['x']
    y_coords = track_data['racing_line']['y']
    
    # Use physics module for velocity calculation
    velocities = calculate_realistic_velocities(x_coords, y_coords, track_type)
    
    track_data['racing_line']['velocity'] = velocities
    track_data['racing_line']['distance'] = calculate_cumulative_distance(x_coords, y_coords)
    
    avg_speed = np.mean(velocities)
    max_speed = np.max(velocities)
    min_speed = np.min(velocities)
    
    print(f"✓ Velocity profile generated for {track_type}:")
    print(f"  Average: {avg_speed:.1f} mph, Max: {max_speed:.1f} mph, Min: {min_speed:.1f} mph")
    
    return track_data


def _extract_racing_line_coordinates(racing_data):
    """
    Extract x, y coordinates from various racing line data formats.
    
    Parameters:
    -----------
    racing_data : dict
        Racing line data from .mat file or other source
        
    Returns:
    --------
    tuple
        (x_coords, y_coords) arrays
    """
    # Handle different possible data structures
    if isinstance(racing_data, dict):
        # First check for vehicle_path (most common format in our data)
        if 'vehicle_path' in racing_data:
            vehicle_path = racing_data['vehicle_path']
            if isinstance(vehicle_path, np.ndarray) and vehicle_path.shape[0] == 2:
                x_coords = vehicle_path[0, :]
                y_coords = vehicle_path[1, :]
                print(f"✓ Extracted racing line from vehicle_path: {len(x_coords)} points")
                print(f"  X range: {np.min(x_coords):.1f} to {np.max(x_coords):.1f}")
                print(f"  Y range: {np.min(y_coords):.1f} to {np.max(y_coords):.1f}")
                return x_coords, y_coords
        
        # Try common coordinate key pairs
        coord_pairs = [
            ('x', 'y'), ('X', 'Y'), ('x_coords', 'y_coords'), 
            ('racing_x', 'racing_y'), ('path_x', 'path_y')
        ]
        
        for x_key, y_key in coord_pairs:
            if x_key in racing_data and y_key in racing_data:
                x_data = np.array(racing_data[x_key]).flatten()
                y_data = np.array(racing_data[y_key]).flatten()
                
                # Skip normalized coordinates (0-1 range) if we have real coordinates available
                if not (np.min(x_data) >= 0 and np.max(x_data) <= 1 and len(x_data) > 10):
                    print(f"✓ Extracted racing line from {x_key}/{y_key}: {len(x_data)} points")
                    return x_data, y_data
            
        # Try to extract from coordinate matrices
        for key in racing_data.keys():
            data = racing_data[key]
            if isinstance(data, np.ndarray) and data.ndim == 2:
                if data.shape[1] >= 2 and data.shape[0] > 10:
                    x_coords = data[:, 0]
                    y_coords = data[:, 1]
                    # Check if these look like real coordinates (not normalized)
                    if not (np.min(x_coords) >= 0 and np.max(x_coords) <= 1):
                        print(f"✓ Extracted racing line from matrix {key}: {len(x_coords)} points")
                        return x_coords, y_coords
                elif data.shape[0] >= 2 and data.shape[1] > 10:
                    x_coords = data[0, :]
                    y_coords = data[1, :]
                    # Check if these look like real coordinates (not normalized)
                    if not (np.min(x_coords) >= 0 and np.max(x_coords) <= 1):
                        print(f"✓ Extracted racing line from transposed matrix {key}: {len(x_coords)} points")
                        return x_coords, y_coords
    
    print("⚠ Could not extract racing line coordinates from data")
    return None, None
