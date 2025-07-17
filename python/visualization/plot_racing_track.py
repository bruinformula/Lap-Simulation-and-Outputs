"""
Comprehensive Track Visualization Module
========================================

Complete track visualization with racing line, boundaries, and velocity data.
Consolidated from multiple visualization files for maximum detail and functionality.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
import matplotlib.colors as mcolors
from matplotlib.colorbar import ColorbarBase
import os
import sys
from scipy.io import loadmat
from scipy.ndimage import gaussian_filter1d

# Add the python directory to the path
current_dir = os.path.dirname(__file__)
python_dir = os.path.dirname(current_dir)  # Go up one level to python/
sys.path.insert(0, python_dir)

from lap_simulation import data_loader
from lap_simulation.output_utils import get_plot_path, print_save_message
from lap_simulation.physics import calculate_realistic_velocities, calculate_cumulative_distance, estimate_lap_time


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
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    track_data = {}
    
        # Load track coordinate data
    try:
        # Load endurance track data
        endurance_data = data_loader.load_track_coordinates('Endurance_Coordinates_1.xlsx', base_dir)
        
        # Load autocross track  
        autocross_file = os.path.join(base_dir, "Autocross_Coordinates_2.xlsx")
        autocross_data = data_loader.load_track_coordinates(autocross_file)
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
                    racing_data = data_loader.load_mat_data(filepath)
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
            track_data[track_type] = add_velocity_data(track_data[track_type], track_type)
    
    return track_data


def add_velocity_data(track_data, track_type):
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
        x_coords, y_coords = extract_racing_line_coordinates(racing_data)
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


def extract_racing_line_coordinates(racing_data):
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


def plot_comprehensive_track(track_data, track_type='endurance', save_name=None):
    """
    Plot comprehensive track visualization with velocity-colored racing line.
    
    Parameters:
    -----------
    track_data : dict
        Track data dictionary for specific track
    track_type : str
        'endurance' or 'autocross'
    save_name : str, optional
        Filename to save the plot
    """
    fig, (ax_main, ax_velocity) = plt.subplots(1, 2, figsize=(20, 10))
    
    # Colors for different elements
    colors = {
        'outside_boundary': '#2C3E50',
        'inside_boundary': '#34495E', 
        'track_fill': '#ECF0F1',
        'start_finish': '#27AE60',
        'background': '#FFFFFF'
    }
    
    # Main track plot
    ax_main.set_facecolor(colors['background'])
    
    # Plot track boundaries
    outside = track_data['outside_track']
    inside = track_data['inside_track']
    
    ax_main.plot(outside[:, 0], outside[:, 1], color=colors['outside_boundary'], 
                linewidth=4, label='Outside Boundary', alpha=0.9)
    ax_main.plot(inside[:, 0], inside[:, 1], color=colors['inside_boundary'], 
                linewidth=4, label='Inside Boundary', alpha=0.9)
    
    # Fill track area between boundaries
    track_polygon = np.vstack([outside, inside[::-1]])
    track_patch = Polygon(track_polygon, alpha=0.3, facecolor=colors['track_fill'], 
                         edgecolor='none', label='Track Surface')
    ax_main.add_patch(track_patch)
    
    # Plot racing line with velocity color coding
    racing_line = track_data['racing_line']
    x_coords = racing_line['x']
    y_coords = racing_line['y']
    velocities = racing_line['velocity']
    
    # Create segments for velocity-colored line
    points = np.array([x_coords, y_coords]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    # Create velocity-based colormap
    norm = Normalize(vmin=np.min(velocities), vmax=np.max(velocities))
    lc = LineCollection(segments.tolist(), cmap='viridis', norm=norm, linewidth=5, alpha=0.9)
    lc.set_array(velocities[:-1])  # Use velocity for coloring
    line_collection = ax_main.add_collection(lc)
    
    # Add colorbar for velocity
    cbar = plt.colorbar(line_collection, ax=ax_main, shrink=0.8, aspect=20)
    cbar.set_label('Velocity [mph]', fontsize=12, fontweight='bold')
    cbar.ax.tick_params(labelsize=10)
    
    # Add start/finish marker
    ax_main.scatter(x_coords[0], y_coords[0], s=300, c=colors['start_finish'], 
                   marker='s', label='Start/Finish', zorder=15, 
                   edgecolor='white', linewidth=3)
    
    # Add direction arrows
    n_arrows = 12
    arrow_indices = np.linspace(0, len(x_coords)-6, n_arrows, dtype=int)
    
    for i in arrow_indices:
        if i + 4 < len(x_coords):
            dx = x_coords[i+4] - x_coords[i]
            dy = y_coords[i+4] - y_coords[i]
            arrow_length = np.sqrt(dx**2 + dy**2)
            
            if arrow_length > 0:
                scale = max(8, arrow_length * 0.4)
                ax_main.arrow(x_coords[i], y_coords[i], 
                             dx/arrow_length * scale, dy/arrow_length * scale,
                             head_width=scale*0.8, head_length=scale*0.6, 
                             fc='white', ec='black', alpha=0.9, zorder=12,
                             linewidth=1.5)
    
    # Styling for main plot
    ax_main.set_aspect('equal')
    ax_main.grid(True, alpha=0.3, linestyle='--')
    ax_main.legend(loc='upper right', framealpha=0.95, fontsize=11)
    
    track_name = track_type.capitalize()
    ax_main.set_title(f'{track_name} Track with Velocity-Optimized Racing Line', 
                     fontsize=16, fontweight='bold', pad=20)
    ax_main.set_xlabel('X Position [ft]', fontsize=12, fontweight='bold')
    ax_main.set_ylabel('Y Position [ft]', fontsize=12, fontweight='bold')
    
    # Add track statistics
    track_length = calculate_path_length(x_coords, y_coords)
    avg_velocity = np.mean(velocities)
    max_velocity = np.max(velocities)
    min_velocity = np.min(velocities)
    
    # Estimate lap time using physics module
    distances = racing_line['distance']
    lap_time = estimate_lap_time(distances, velocities)
    
    info_text = f'{track_name} Performance Data:\n'
    info_text += f'• Racing line length: {track_length:.0f} ft\n'
    info_text += f'• Average velocity: {avg_velocity:.1f} mph\n'
    info_text += f'• Max velocity: {max_velocity:.1f} mph\n'
    info_text += f'• Min velocity: {min_velocity:.1f} mph\n'
    info_text += f'• Estimated lap time: {lap_time:.1f} seconds\n'
    info_text += f'• Racing line points: {len(x_coords)}'
    
    ax_main.text(0.02, 0.98, info_text, transform=ax_main.transAxes, 
                verticalalignment='top', fontsize=10,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.95))
    
    # Velocity profile plot
    ax_velocity.plot(distances, velocities, 'b-', linewidth=3, alpha=0.8)
    ax_velocity.fill_between(distances, velocities, alpha=0.3, color='skyblue')
    
    # Highlight high and low speed sections
    high_speed_mask = velocities > np.percentile(velocities, 75)
    low_speed_mask = velocities < np.percentile(velocities, 25)
    
    ax_velocity.scatter(distances[high_speed_mask], velocities[high_speed_mask], 
                       c='red', s=20, alpha=0.7, label='High Speed Sections')
    ax_velocity.scatter(distances[low_speed_mask], velocities[low_speed_mask], 
                       c='orange', s=20, alpha=0.7, label='Low Speed Sections')
    
    ax_velocity.set_xlabel('Distance Along Racing Line [ft]', fontsize=12, fontweight='bold')
    ax_velocity.set_ylabel('Velocity [mph]', fontsize=12, fontweight='bold')
    ax_velocity.set_title(f'{track_name} Velocity Profile', fontsize=14, fontweight='bold')
    ax_velocity.grid(True, alpha=0.3)
    ax_velocity.legend(fontsize=10)
    
    # Add velocity statistics to velocity plot
    vel_stats = f'Velocity Statistics:\n'
    vel_stats += f'Mean: {avg_velocity:.1f} mph\n'
    vel_stats += f'Std Dev: {np.std(velocities):.1f} mph\n'
    vel_stats += f'Range: {max_velocity - min_velocity:.1f} mph'
    
    ax_velocity.text(0.02, 0.98, vel_stats, transform=ax_velocity.transAxes,
                    verticalalignment='top', fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    
    # Save if filename provided
    if save_name:
        plot_path = get_plot_path(save_name)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        print_save_message(plot_path, 'comprehensive track plot')
    
    plt.show()
    
    return fig


def plot_track_comparison(track_data, save_name=None):
    """
    Plot side-by-side comparison of both tracks with velocity information.
    
    Parameters:
    -----------
    track_data : dict
        Complete track data dictionary
    save_name : str, optional
        Filename to save the plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    
    tracks = ['endurance', 'autocross']
    track_names = ['Endurance Track', 'Autocross Track']
    
    for idx, (track_type, track_name) in enumerate(zip(tracks, track_names)):
        if track_type not in track_data:
            continue
            
        data = track_data[track_type]
        
        # Track layout (top row)
        ax_track = axes[0, idx]
        ax_track.set_facecolor('#FFFFFF')
        
        # Plot boundaries
        outside = data['outside_track']
        inside = data['inside_track']
        
        ax_track.plot(outside[:, 0], outside[:, 1], 'k-', linewidth=3, 
                     label='Outside', alpha=0.8)
        ax_track.plot(inside[:, 0], inside[:, 1], 'k-', linewidth=3, 
                     label='Inside', alpha=0.8)
        
        # Fill track
        track_polygon = np.vstack([outside, inside[::-1]])
        track_patch = Polygon(track_polygon, alpha=0.2, facecolor='lightgray')
        ax_track.add_patch(track_patch)
        
        # Velocity-colored racing line
        racing_line = data['racing_line']
        x_coords = racing_line['x']
        y_coords = racing_line['y']
        velocities = racing_line['velocity']
        
        points = np.array([x_coords, y_coords]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        norm = Normalize(vmin=np.min(velocities), vmax=np.max(velocities))
        lc = LineCollection(segments.tolist(), cmap='viridis', norm=norm, linewidth=4)
        lc.set_array(velocities[:-1])
        line_collection = ax_track.add_collection(lc)
        
        # Start/finish
        ax_track.scatter(x_coords[0], y_coords[0], s=200, c='green', 
                        marker='s', zorder=10, edgecolor='white', linewidth=2)
        
        ax_track.set_aspect('equal')
        ax_track.grid(True, alpha=0.3)
        ax_track.set_title(track_name, fontsize=14, fontweight='bold')
        ax_track.set_xlabel('X Position [ft]')
        ax_track.set_ylabel('Y Position [ft]')
        
        # Velocity profile (bottom row)
        ax_vel = axes[1, idx]
        distances = racing_line['distance']
        
        ax_vel.plot(distances, velocities, linewidth=3, color='blue', alpha=0.8)
        ax_vel.fill_between(distances, velocities, alpha=0.3, color='lightblue')
        
        # Mark high/low speed sections
        high_speed = velocities > np.percentile(velocities, 80)
        low_speed = velocities < np.percentile(velocities, 20)
        
        ax_vel.scatter(distances[high_speed], velocities[high_speed], 
                      c='red', s=15, alpha=0.8, label='High Speed')
        ax_vel.scatter(distances[low_speed], velocities[low_speed], 
                      c='orange', s=15, alpha=0.8, label='Low Speed')
        
        ax_vel.set_xlabel('Distance [ft]')
        ax_vel.set_ylabel('Velocity [mph]')
        ax_vel.set_title(f'{track_name} Velocity Profile')
        ax_vel.grid(True, alpha=0.3)
        ax_vel.legend(fontsize=9)
        
        # Add statistics
        avg_vel = np.mean(velocities)
        max_vel = np.max(velocities)
        track_length = distances[-1]
        
        stats_text = f'Avg: {avg_vel:.1f} mph\nMax: {max_vel:.1f} mph\nLength: {track_length:.0f} ft'
        ax_vel.text(0.98, 0.98, stats_text, transform=ax_vel.transAxes,
                   verticalalignment='top', horizontalalignment='right',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                   fontsize=9)
    
    plt.tight_layout()
    
    if save_name:
        plot_path = get_plot_path(save_name)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        print_save_message(plot_path, 'track comparison plot')
    
    plt.show()
    
    return fig


def calculate_path_length(x_coords, y_coords):
    """Calculate total path length from coordinates."""
    if len(x_coords) < 2:
        return 0
    
    dx = np.diff(x_coords)
    dy = np.diff(y_coords)
    distances = np.sqrt(dx**2 + dy**2)
    
    return np.sum(distances)


def main():
    """
    Main function to demonstrate comprehensive track visualization.
    """
    print("🏁 Loading comprehensive track data...")
    track_data = load_comprehensive_track_data()
    
    print("\n📊 Available tracks:", list(track_data.keys()))
    
    # Plot individual tracks with velocity data
    if 'endurance' in track_data:
        print("\n🏁 Plotting Endurance track with velocity data...")
        plot_comprehensive_track(track_data['endurance'], 'endurance',
                                'comprehensive_endurance_track.png')
    
    if 'autocross' in track_data:
        print("\n🏁 Plotting Autocross track with velocity data...")
        plot_comprehensive_track(track_data['autocross'], 'autocross',
                                'comprehensive_autocross_track.png')
    
    # Plot track comparison
    if len(track_data) >= 2:
        print("\n📊 Creating track comparison...")
        plot_track_comparison(track_data, 'comprehensive_track_comparison.png')
    
    print("\n✅ All comprehensive visualizations complete!")


if __name__ == "__main__":
    main()
