"""
Plotting and Visualization Module
=================================

Contains all plotting functions for lap simulation results.
Separates visualization logic from main simulation logic.
"""

import numpy as np
import matplotlib.pyplot as plt
from .output_utils import get_plot_path


def plot_accelerations(distance, A_long_g, A_lat_g):
    """
    Plot longitudinal and lateral accelerations vs distance.
    
    Parameters:
    -----------
    distance : np.ndarray
        Distance array in feet
    A_long_g : np.ndarray
        Longitudinal acceleration in g-force
    A_lat_g : np.ndarray
        Lateral acceleration in g-force
    """
    # Create figure with MATLAB styling
    fig = plt.figure(figsize=(12, 8))
    try:
        fig.canvas.manager.set_window_title('Accelerations')
    except:
        pass  # Window title setting may not work in all environments
    
    # Main plot - matches MATLAB: plot(distance,A_long_g,distance,A_lat_g)
    plt.plot(distance, A_long_g, 'b-', linewidth=1.5, label='Longitudinal')
    plt.plot(distance, A_lat_g, 'r-', linewidth=1.5, label='Lateral')
    
    plt.title('Endurance Simulation Acceleration Traces', fontweight='bold')
    plt.xlabel('Distance Travelled (d) [ft]')
    plt.ylabel('Acceleration [g]')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = get_plot_path('acceleration_plots.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_corner_loads(loads):
    """
    Plot individual wheel loads.
    
    Parameters:
    -----------
    loads : dict
        Dictionary with wheel load arrays: 'FL', 'FR', 'RL', 'RR'
    """
    N = len(loads['FL'])
    samples = np.arange(1, N+1)
    
    # Create the corner loads plot (matches MATLAB subplot structure)
    fig2 = plt.figure(figsize=(12, 10))
    try:
        fig2.canvas.manager.set_window_title('Corner Loads')
    except:
        pass
    
    # Front Left (matches MATLAB subplot(2,2,1))
    plt.subplot(2, 2, 1)
    plt.plot(samples, loads['FL'], 'b-', linewidth=1.5)
    plt.title('Front Left', fontweight='bold')
    plt.xlabel('Sample #')
    plt.ylabel('Load (lbs)')
    plt.grid(True, alpha=0.3)
    
    # Front Right (matches MATLAB subplot(2,2,2))
    plt.subplot(2, 2, 2)
    plt.plot(samples, loads['FR'], 'b-', linewidth=1.5)
    plt.title('Front Right', fontweight='bold')
    plt.xlabel('Sample #')
    plt.ylabel('Load (lbs)')
    plt.grid(True, alpha=0.3)
    
    # Rear Left (matches MATLAB subplot(2,2,3))
    plt.subplot(2, 2, 3)
    plt.plot(samples, loads['RL'], 'b-', linewidth=1.5)
    plt.title('Rear Left', fontweight='bold')
    plt.xlabel('Sample #')
    plt.ylabel('Load (lbs)')
    plt.grid(True, alpha=0.3)
    
    # Rear Right (matches MATLAB subplot(2,2,4))
    plt.subplot(2, 2, 4)
    plt.plot(samples, loads['RR'], 'b-', linewidth=1.5)
    plt.title('Rear Right', fontweight='bold')
    plt.xlabel('Sample #')
    plt.ylabel('Load (lbs)')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = get_plot_path('corner_loads.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_accelerations_by_sample(A_long_g, A_lat_g):
    """
    Plot accelerations vs sample number.
    
    Parameters:
    -----------
    A_long_g : np.ndarray
        Longitudinal acceleration in g-force
    A_lat_g : np.ndarray
        Lateral acceleration in g-force
    """
    N = len(A_lat_g)
    samples = np.arange(1, N+1)
    
    # Additional acceleration plots (matches the second MATLAB figure)
    fig3 = plt.figure(figsize=(12, 8))
    try:
        fig3.canvas.manager.set_window_title('Accelerations')
    except:
        pass
    
    # Longitudinal acceleration vs. sample # (matches MATLAB subplot(2,1,1))
    plt.subplot(2, 1, 1)
    plt.plot(samples, A_long_g, 'b-', linewidth=1.5)
    plt.xlabel('Sample #')
    plt.ylabel('Longitudinal accel (G)')
    plt.title('Longitudinal Acceleration')
    plt.grid(True, alpha=0.3)
    
    # Lateral acceleration vs. sample # (matches MATLAB subplot(2,1,2))
    plt.subplot(2, 1, 2)
    plt.plot(samples, A_lat_g, 'r-', linewidth=1.5)
    plt.xlabel('Sample #')
    plt.ylabel('Lateral accel (G)')
    plt.title('Lateral Acceleration')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = get_plot_path('acceleration_by_sample.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_roll_angles(distance, roll_angle):
    """
    Plot vehicle roll angles vs distance.
    
    Parameters:
    -----------
    distance : np.ndarray
        Distance array in feet
    roll_angle : np.ndarray
        Roll angle in degrees
    """
    # Plot roll angles
    plt.figure(figsize=(12, 6))
    plt.plot(distance, roll_angle, 'g-', linewidth=1.5)
    plt.title('Vehicle Roll Angle', fontweight='bold')
    plt.xlabel('Distance Travelled (d) [ft]')
    plt.ylabel('Roll Angle [degrees]')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot_path = get_plot_path('roll_angles.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_track_only(track_data, track_type='endurance', save_name=None):
    """
    Plot only the track layout with racing line (no velocity subplot).
    
    Parameters:
    -----------
    track_data : dict
        Track data dictionary for specific track
    track_type : str
        'endurance' or 'autocross'
    save_name : str, optional
        Filename to save the plot
    """
    from matplotlib.patches import Polygon
    from matplotlib.collections import LineCollection
    from matplotlib.colors import Normalize
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Colors for different elements
    colors = {
        'outside_boundary': '#2C3E50',
        'inside_boundary': '#34495E', 
        'track_fill': '#ECF0F1',
        'start_finish': '#27AE60',
        'background': '#FFFFFF'
    }
    
    # Main track plot
    ax.set_facecolor(colors['background'])
    
    # Plot track boundaries
    outside = track_data['outside_track']
    inside = track_data['inside_track']
    
    ax.plot(outside[:, 0], outside[:, 1], color=colors['outside_boundary'], 
            linewidth=4, label='Outside Boundary', alpha=0.9)
    ax.plot(inside[:, 0], inside[:, 1], color=colors['inside_boundary'], 
            linewidth=4, label='Inside Boundary', alpha=0.9)
    
    # Fill track area between boundaries
    track_polygon = np.vstack([outside, inside[::-1]])
    track_patch = Polygon(track_polygon, alpha=0.3, facecolor=colors['track_fill'], 
                         edgecolor='none', label='Track Surface')
    ax.add_patch(track_patch)
    
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
    line_collection = ax.add_collection(lc)
    
    # Add colorbar for velocity
    cbar = plt.colorbar(line_collection, ax=ax, shrink=0.8, aspect=20)
    cbar.set_label('Velocity [mph]', fontsize=12, fontweight='bold')
    cbar.ax.tick_params(labelsize=10)
    
    # Add start/finish marker
    ax.scatter(x_coords[0], y_coords[0], s=300, c=colors['start_finish'], 
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
                ax.arrow(x_coords[i], y_coords[i], 
                         dx/arrow_length * scale, dy/arrow_length * scale,
                         head_width=scale*0.8, head_length=scale*0.6, 
                         fc='white', ec='black', alpha=0.9, zorder=12,
                         linewidth=1.5)
    
    # Styling for main plot
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', framealpha=0.95, fontsize=11)
    
    track_name = track_type.capitalize()
    ax.set_title(f'{track_name} Track with Velocity-Optimized Racing Line', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('X Position [ft]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y Position [ft]', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    # Save the plot
    if save_name is None:
        save_name = f'{track_type}_track_layout.png'
    plot_path = get_plot_path(save_name)
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_velocity_profile(track_data, track_type='endurance', save_name=None):
    """
    Plot velocity profile along the track distance.
    
    Parameters:
    -----------
    track_data : dict
        Track data dictionary for specific track
    track_type : str
        'endurance' or 'autocross' 
    save_name : str, optional
        Filename to save the plot
    """
    racing_line = track_data['racing_line']
    distances = racing_line['distance']
    velocities = racing_line['velocity']
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    # Plot velocity profile
    ax.plot(distances, velocities, 'b-', linewidth=2.5, alpha=0.8)
    ax.fill_between(distances, velocities, alpha=0.3, color='blue')
    
    # Styling
    track_name = track_type.capitalize()
    ax.set_title(f'{track_name} Track - Velocity Profile', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Distance Along Track [ft]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Velocity [mph]', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add statistics
    avg_velocity = np.mean(velocities)
    max_velocity = np.max(velocities)
    min_velocity = np.min(velocities)
    
    info_text = f'Avg: {avg_velocity:.1f} mph\nMax: {max_velocity:.1f} mph\nMin: {min_velocity:.1f} mph'
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    
    # Save the plot
    if save_name is None:
        save_name = f'{track_type}_velocity_profile.png'
    plot_path = get_plot_path(save_name)
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
