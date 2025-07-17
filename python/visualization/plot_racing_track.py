"""
Track Visualization Module
==========================

Functions to plot the optimized racing track with racing line and track boundaries.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import LineCollection
import os
import sys
from scipy.io import loadmat

# Add the python directory to the path
current_dir = os.path.dirname(__file__)
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

from lap_simulation.data_loader import load_mat_data, load_track_coordinates


def load_track_data(base_dir: str = "."):
    """
    Load all track-related data including coordinates and racing lines.
    
    Parameters:
    -----------
    base_dir : str
        Base directory containing track files
        
    Returns:
    --------
    dict
        Dictionary containing track data
    """
    track_data = {}
    
    try:
        # Load endurance track coordinates
        endurance_file = os.path.join(base_dir, "Endurance_Coordinates_1.xlsx")
        if os.path.exists(endurance_file):
            endurance_coords = load_track_coordinates(endurance_file)
            track_data['endurance_coordinates'] = endurance_coords
            print(f"✓ Loaded endurance coordinates: {endurance_coords.shape[0]} points")
        
        # Load autocross track coordinates
        autocross_file = os.path.join(base_dir, "Autocross_Coordinates_2.xlsx")
        if os.path.exists(autocross_file):
            autocross_coords = load_track_coordinates(autocross_file)
            track_data['autocross_coordinates'] = autocross_coords
            print(f"✓ Loaded autocross coordinates: {autocross_coords.shape[0]} points")
    except Exception as e:
        print(f"⚠ Error loading track coordinates: {e}")
    
    try:
        # Load racing line data
        data_dir = os.path.join(base_dir, "Data Files")
        
        # Endurance racing line
        endurance_racing_file = os.path.join(data_dir, "endurance_racing_line.mat")
        if os.path.exists(endurance_racing_file):
            endurance_racing = load_mat_data(endurance_racing_file)
            track_data['endurance_racing_line'] = endurance_racing
            print(f"✓ Loaded endurance racing line data")
            print(f"  Keys: {list(endurance_racing.keys())}")
        
        # Autocross racing line
        autocross_racing_file = os.path.join(data_dir, "autocross_racing_line.mat")
        if os.path.exists(autocross_racing_file):
            autocross_racing = load_mat_data(autocross_racing_file)
            track_data['autocross_racing_line'] = autocross_racing
            print(f"✓ Loaded autocross racing line data")
            print(f"  Keys: {list(autocross_racing.keys())}")
            
    except Exception as e:
        print(f"⚠ Error loading racing line data: {e}")
    
    return track_data


def extract_racing_line_points(racing_data):
    """
    Extract x, y coordinates from racing line data structure.
    
    Parameters:
    -----------
    racing_data : dict
        Racing line data from .mat file
        
    Returns:
    --------
    tuple
        (x_coords, y_coords) arrays
    """
    # Try different possible key names for the racing line data
    possible_keys = ['racing_line', 'line', 'path', 'coordinates', 'track', 'xy', 'points']
    
    for key in racing_data.keys():
        data = racing_data[key]
        if isinstance(data, np.ndarray):
            if data.ndim == 2 and data.shape[1] >= 2:
                # Found coordinate data
                print(f"  Using key '{key}' with shape {data.shape}")
                return data[:, 0], data[:, 1]
            elif data.ndim == 2 and data.shape[0] >= 2:
                # Transposed data
                print(f"  Using transposed key '{key}' with shape {data.shape}")
                return data[0, :], data[1, :]
    
    # If no clear coordinate data found, try to extract from nested structures
    for key in racing_data.keys():
        data = racing_data[key]
        if hasattr(data, 'dtype') and data.dtype == 'object':
            # Try to extract from object array
            try:
                if len(data) >= 2:
                    x_data = np.array(data[0]).flatten()
                    y_data = np.array(data[1]).flatten()
                    if len(x_data) == len(y_data) and len(x_data) > 10:
                        print(f"  Extracted from object array '{key}': {len(x_data)} points")
                        return x_data, y_data
            except:
                continue
    
    print(f"⚠ Could not extract coordinate data from racing line")
    return None, None


def plot_track_with_racing_line(track_data, track_type='endurance', save_name=None):
    """
    Plot track boundaries with optimized racing line.
    
    Parameters:
    -----------
    track_data : dict
        Track data dictionary
    track_type : str
        'endurance' or 'autocross'
    save_name : str, optional
        Filename to save the plot
    """
    fig, ax = plt.subplots(figsize=(15, 12))
    
    # Colors for different elements
    colors = {
        'track_boundary': '#404040',
        'racing_line': '#FF4444',
        'track_center': '#888888',
        'background': '#F8F8F8'
    }
    
    ax.set_facecolor(colors['background'])
    
    # Plot track boundaries if available
    coord_key = f'{track_type}_coordinates'
    if coord_key in track_data:
        coords = track_data[coord_key]
        
        # Assume the coordinates define the track boundaries
        # For a closed track, we need to close the loop
        if not np.allclose(coords[0], coords[-1]):
            coords_closed = np.vstack([coords, coords[0]])
        else:
            coords_closed = coords
        
        # Plot track boundary
        ax.plot(coords_closed[:, 0], coords_closed[:, 1], 
               color=colors['track_boundary'], linewidth=3, 
               label='Track Boundary', alpha=0.8)
        
        # Fill track area
        track_polygon = Polygon(coords, alpha=0.1, facecolor='lightgray', 
                               edgecolor='none')
        ax.add_patch(track_polygon)
        
        print(f"✓ Plotted {track_type} track boundary: {len(coords)} points")
    
    # Plot racing line if available
    racing_key = f'{track_type}_racing_line'
    if racing_key in track_data:
        racing_data = track_data[racing_key]
        x_racing, y_racing = extract_racing_line_points(racing_data)
        
        if x_racing is not None and y_racing is not None:
            # Create gradient effect for racing line (speed visualization)
            points = np.array([x_racing, y_racing]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)
            
            # Create color gradient (can represent speed)
            colors_gradient = plt.cm.plasma(np.linspace(0, 1, len(segments)))
            
            lc = LineCollection(segments, colors=colors_gradient, linewidth=4, alpha=0.8)
            ax.add_collection(lc)
            
            # Also plot a simple line for the legend
            ax.plot(x_racing, y_racing, color=colors['racing_line'], 
                   linewidth=4, label='Optimized Racing Line', alpha=0.7)
            
            print(f"✓ Plotted {track_type} racing line: {len(x_racing)} points")
            
            # Add start/finish markers
            if len(x_racing) > 0:
                ax.scatter(x_racing[0], y_racing[0], s=200, c='green', 
                          marker='s', label='Start/Finish', zorder=10, 
                          edgecolor='white', linewidth=2)
                
                # Add direction arrows along the racing line
                arrow_spacing = max(1, len(x_racing) // 15)  # ~15 arrows
                for i in range(0, len(x_racing)-1, arrow_spacing):
                    if i + 5 < len(x_racing):  # Make sure we have enough points for direction
                        dx = x_racing[i+5] - x_racing[i]
                        dy = y_racing[i+5] - y_racing[i]
                        arrow_length = np.sqrt(dx**2 + dy**2)
                        if arrow_length > 0:
                            ax.arrow(x_racing[i], y_racing[i], 
                                   dx/arrow_length * 20, dy/arrow_length * 20,
                                   head_width=15, head_length=10, fc='white', 
                                   ec='black', alpha=0.8, zorder=8)
    
    # Generate synthetic racing line if real data not available
    if coord_key in track_data and racing_key not in track_data:
        print(f"⚠ No racing line data available, generating synthetic racing line")
        coords = track_data[coord_key]
        x_synth, y_synth = generate_synthetic_racing_line(coords)
        
        ax.plot(x_synth, y_synth, color=colors['racing_line'], 
               linewidth=3, label='Synthetic Racing Line', 
               linestyle='--', alpha=0.8)
        
        ax.scatter(x_synth[0], y_synth[0], s=200, c='green', 
                  marker='s', label='Start/Finish', zorder=10,
                  edgecolor='white', linewidth=2)
    
    # Styling
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', framealpha=0.9)
    
    # Title and labels
    track_name = track_type.capitalize()
    ax.set_title(f'{track_name} Track Layout with Optimized Racing Line', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('X Position [ft]', fontsize=12)
    ax.set_ylabel('Y Position [ft]', fontsize=12)
    
    # Add track information text box
    if coord_key in track_data:
        coords = track_data[coord_key]
        track_length = calculate_track_length(coords)
        
        info_text = f'{track_name} Track Information:\n'
        info_text += f'• Track boundary points: {len(coords)}\n'
        info_text += f'• Approximate length: {track_length:.0f} ft\n'
        
        if racing_key in track_data:
            racing_data = track_data[racing_key]
            x_racing, y_racing = extract_racing_line_points(racing_data)
            if x_racing is not None:
                racing_length = calculate_path_length(x_racing, y_racing)
                info_text += f'• Racing line length: {racing_length:.0f} ft\n'
                info_text += f'• Racing line points: {len(x_racing)}'
        
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
               verticalalignment='top', bbox=dict(boxstyle='round', 
               facecolor='white', alpha=0.8), fontsize=10)
    
    plt.tight_layout()
    
    # Save if filename provided
    if save_name:
        plt.savefig(save_name, dpi=300, bbox_inches='tight')
        print(f"✓ Saved track plot as {save_name}")
    
    plt.show()


def generate_synthetic_racing_line(track_coords):
    """
    Generate a synthetic racing line inside the track boundaries.
    
    Parameters:
    -----------
    track_coords : np.ndarray
        Track boundary coordinates
        
    Returns:
    --------
    tuple
        (x_racing, y_racing) synthetic racing line coordinates
    """
    # Simple approach: create a line that's offset inward from the boundary
    # This is a basic approximation - real racing line optimization is much more complex
    
    # Calculate centroid
    centroid_x = np.mean(track_coords[:, 0])
    centroid_y = np.mean(track_coords[:, 1])
    
    # Create racing line by moving each boundary point toward the centroid
    offset_factor = 0.3  # Move 30% toward center
    
    x_racing = track_coords[:, 0] + offset_factor * (centroid_x - track_coords[:, 0])
    y_racing = track_coords[:, 1] + offset_factor * (centroid_y - track_coords[:, 1])
    
    # Smooth the racing line
    from scipy.ndimage import gaussian_filter1d
    x_racing = gaussian_filter1d(x_racing, sigma=2)
    y_racing = gaussian_filter1d(y_racing, sigma=2)
    
    return x_racing, y_racing


def calculate_track_length(coords):
    """Calculate approximate track length from coordinates."""
    if len(coords) < 2:
        return 0
    
    # Calculate distances between consecutive points
    dx = np.diff(coords[:, 0])
    dy = np.diff(coords[:, 1])
    distances = np.sqrt(dx**2 + dy**2)
    
    # Add closing distance for closed track
    closing_distance = np.sqrt((coords[-1, 0] - coords[0, 0])**2 + 
                              (coords[-1, 1] - coords[0, 1])**2)
    
    return np.sum(distances) + closing_distance


def calculate_path_length(x_coords, y_coords):
    """Calculate path length from x, y coordinates."""
    if len(x_coords) < 2:
        return 0
    
    dx = np.diff(x_coords)
    dy = np.diff(y_coords)
    distances = np.sqrt(dx**2 + dy**2)
    
    return np.sum(distances)


def plot_both_tracks(track_data, save_name=None):
    """
    Plot both endurance and autocross tracks side by side.
    
    Parameters:
    -----------
    track_data : dict
        Track data dictionary
    save_name : str, optional
        Filename to save the plot
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    tracks = [
        ('endurance', ax1, 'Endurance Track'),
        ('autocross', ax2, 'Autocross Track')
    ]
    
    for track_type, ax, title in tracks:
        coord_key = f'{track_type}_coordinates'
        racing_key = f'{track_type}_racing_line'
        
        if coord_key in track_data:
            coords = track_data[coord_key]
            
            # Plot track boundary
            if not np.allclose(coords[0], coords[-1]):
                coords_closed = np.vstack([coords, coords[0]])
            else:
                coords_closed = coords
            
            ax.plot(coords_closed[:, 0], coords_closed[:, 1], 
                   'k-', linewidth=3, label='Track Boundary')
            
            # Fill track area
            track_polygon = Polygon(coords, alpha=0.1, facecolor='lightgray')
            ax.add_patch(track_polygon)
            
            # Plot racing line if available
            if racing_key in track_data:
                racing_data = track_data[racing_key]
                x_racing, y_racing = extract_racing_line_points(racing_data)
                
                if x_racing is not None and y_racing is not None:
                    ax.plot(x_racing, y_racing, 'r-', linewidth=3, 
                           label='Racing Line', alpha=0.8)
                    ax.scatter(x_racing[0], y_racing[0], s=150, c='green', 
                              marker='s', label='Start/Finish', zorder=10)
            else:
                # Generate synthetic racing line
                x_synth, y_synth = generate_synthetic_racing_line(coords)
                ax.plot(x_synth, y_synth, 'r--', linewidth=2, 
                       label='Synthetic Racing Line', alpha=0.8)
                ax.scatter(x_synth[0], y_synth[0], s=150, c='green', 
                          marker='s', label='Start/Finish', zorder=10)
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('X Position [ft]')
        ax.set_ylabel('Y Position [ft]')
    
    plt.tight_layout()
    
    if save_name:
        plt.savefig(save_name, dpi=300, bbox_inches='tight')
        print(f"✓ Saved comparison plot as {save_name}")
    
    plt.show()


def main():
    """Main function to load and plot track data."""
    print("Loading and Plotting Optimized Racing Tracks")
    print("=" * 50)
    
    # Load all track data
    track_data = load_track_data()
    
    if not track_data:
        print("⚠ No track data loaded. Check file paths and formats.")
        return
    
    print(f"\nLoaded data for {len(track_data)} track elements")
    
    # Plot endurance track
    if 'endurance_coordinates' in track_data or 'endurance_racing_line' in track_data:
        print("\nPlotting Endurance Track...")
        plot_track_with_racing_line(track_data, 'endurance', 
                                   'endurance_track_with_racing_line.png')
    
    # Plot autocross track
    if 'autocross_coordinates' in track_data or 'autocross_racing_line' in track_data:
        print("\nPlotting Autocross Track...")
        plot_track_with_racing_line(track_data, 'autocross', 
                                   'autocross_track_with_racing_line.png')
    
    # Plot both tracks side by side if both available
    if len([k for k in track_data.keys() if 'coordinates' in k]) >= 2:
        print("\nPlotting Track Comparison...")
        plot_both_tracks(track_data, 'track_comparison.png')
    
    print("\n" + "=" * 50)
    print("Track visualization complete!")


if __name__ == "__main__":
    main()
