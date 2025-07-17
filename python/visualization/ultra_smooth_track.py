"""
Ultra-Smooth Track Plotting
===========================

Advanced track plotting with maximum smoothness to match MATLAB quality.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev, interp1d
from scipy.ndimage import gaussian_filter1d
import pandas as pd
import os
import sys

# Add the python directory to the path
current_dir = os.path.dirname(__file__)
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

from lap_simulation.data_loader import load_track_coordinates


def ultra_smooth_track_plot():
    """Create an ultra-smooth track plot that matches MATLAB quality."""
    print("Creating ultra-smooth track plot...")
    
    try:
        # Load track data from the Scaled sheet
        base_dir = os.path.dirname(__file__)
        endurance_coords = "Endurance_Coordinates_1.xlsx"
        filepath = os.path.join(base_dir, endurance_coords)
        track_data = load_track_coordinates(filepath)
        
        outside_track = track_data['outside_track']
        inside_track = track_data['inside_track']
        
        print(f"Loaded {len(outside_track)} outside and {len(inside_track)} inside track points")
        
        # Create ultra-smooth interpolated tracks
        outside_smooth, inside_smooth, racing_line_smooth = create_ultra_smooth_tracks(
            outside_track, inside_track
        )
        
        # Create the plot with MATLAB-style formatting
        plt.figure(figsize=(16, 12))
        
        # Plot ultra-smooth track boundaries
        plt.plot(outside_smooth[:, 0], outside_smooth[:, 1], 'k-', linewidth=2.5, 
                label='Outside Track Boundary', alpha=0.9)
        plt.plot(inside_smooth[:, 0], inside_smooth[:, 1], 'k-', linewidth=2.5, 
                label='Inside Track Boundary', alpha=0.9)
        
        # Plot ultra-smooth racing line
        plt.plot(racing_line_smooth[:, 0], racing_line_smooth[:, 1], 'r-', linewidth=4, 
                label='Optimized Racing Line', alpha=0.9)
        
        # Add start/finish line
        start_out = outside_smooth[0]
        start_in = inside_smooth[0]
        plt.plot([start_out[0], start_in[0]], [start_out[1], start_in[1]], 
                'g-', linewidth=6, label='Start/Finish', alpha=0.8)
        
        # MATLAB-style formatting
        plt.title('2019 Michigan Endurance - Optimized Racing Track', 
                 fontweight='bold', fontsize=18, pad=20)
        plt.xlabel('X Position [ft]', fontsize=14, labelpad=10)
        plt.ylabel('Y Position [ft]', fontsize=14, labelpad=10)
        
        # Legend with better positioning
        plt.legend(loc='upper right', fontsize=12, frameon=True, 
                  fancybox=True, shadow=True, framealpha=0.9)
        
        # Grid and styling
        plt.grid(True, alpha=0.4, linewidth=0.5, linestyle='-')
        plt.gca().set_axisbelow(True)
        plt.gca().set_facecolor('white')
        
        # Equal aspect ratio and better margins
        plt.axis('equal')
        plt.tight_layout(pad=2.0)
        
        # Add some padding around the track
        all_x = np.concatenate([outside_smooth[:, 0], inside_smooth[:, 0]])
        all_y = np.concatenate([outside_smooth[:, 1], inside_smooth[:, 1]])
        margin = 0.1 * np.max([np.ptp(all_x), np.ptp(all_y)])
        plt.xlim(np.min(all_x) - margin, np.max(all_x) + margin)
        plt.ylim(np.min(all_y) - margin, np.max(all_y) + margin)
        
        # Save with high quality
        plt.savefig('ultra_smooth_racing_track.png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.show()
        
        print("Ultra-smooth track plot saved as 'ultra_smooth_racing_track.png'")
        
        return outside_smooth, inside_smooth, racing_line_smooth
        
    except Exception as e:
        print(f"Error creating ultra-smooth track plot: {e}")
        return None, None, None


def create_ultra_smooth_tracks(outside_track, inside_track):
    """Create ultra-smooth track boundaries and racing line."""
    
    # Step 1: Pre-smooth the raw data
    def pre_smooth_track(track, sigma=3):
        """Apply initial smoothing to raw track data."""
        smoothed = np.copy(track)
        smoothed[:, 0] = gaussian_filter1d(track[:, 0], sigma=sigma, mode='wrap')
        smoothed[:, 1] = gaussian_filter1d(track[:, 1], sigma=sigma, mode='wrap')
        return smoothed
    
    outside_pre = pre_smooth_track(outside_track)
    inside_pre = pre_smooth_track(inside_track)
    
    # Step 2: Ultra-high resolution spline interpolation
    n_points_ultra = len(outside_track) * 10  # 10x resolution for maximum smoothness
    
    # Outside track spline with high smoothing
    tck_out, u_out = splprep([outside_pre[:, 0], outside_pre[:, 1]], 
                             s=len(outside_track)*0.1, per=True, k=3)
    u_new = np.linspace(0, 1, n_points_ultra)
    out_x_ultra, out_y_ultra = splev(u_new, tck_out)
    
    # Inside track spline with high smoothing
    tck_in, u_in = splprep([inside_pre[:, 0], inside_pre[:, 1]], 
                          s=len(inside_track)*0.1, per=True, k=3)
    in_x_ultra, in_y_ultra = splev(u_new, tck_in)
    
    # Convert to arrays
    out_x_ultra = np.array(out_x_ultra)
    out_y_ultra = np.array(out_y_ultra)
    in_x_ultra = np.array(in_x_ultra)
    in_y_ultra = np.array(in_y_ultra)
    
    # Step 3: Create optimized racing line
    racing_line_x, racing_line_y = create_optimized_racing_line(
        out_x_ultra, out_y_ultra, in_x_ultra, in_y_ultra
    )
    
    # Step 4: Final smoothing pass
    # Apply one more round of gentle smoothing for perfection
    out_x_final = gaussian_filter1d(out_x_ultra, sigma=5, mode='wrap')
    out_y_final = gaussian_filter1d(out_y_ultra, sigma=5, mode='wrap')
    in_x_final = gaussian_filter1d(in_x_ultra, sigma=5, mode='wrap')
    in_y_final = gaussian_filter1d(in_y_ultra, sigma=5, mode='wrap')
    racing_x_final = gaussian_filter1d(racing_line_x, sigma=8, mode='wrap')
    racing_y_final = gaussian_filter1d(racing_line_y, sigma=8, mode='wrap')
    
    # Package into arrays
    outside_smooth = np.column_stack([out_x_final, out_y_final])
    inside_smooth = np.column_stack([in_x_final, in_y_final])
    racing_line_smooth = np.column_stack([racing_x_final, racing_y_final])
    
    return outside_smooth, inside_smooth, racing_line_smooth


def create_optimized_racing_line(out_x, out_y, in_x, in_y):
    """Create an optimized racing line using racing principles."""
    
    # Start with geometric center
    center_x = (out_x + in_x) / 2
    center_y = (out_y + in_y) / 2
    
    # Calculate track curvature for racing line optimization
    def calculate_curvature(x, y):
        """Calculate curvature of a parametric curve."""
        dx = np.gradient(x)
        dy = np.gradient(y)
        ddx = np.gradient(dx)
        ddy = np.gradient(dy)
        
        # Avoid division by zero
        denominator = (dx**2 + dy**2)**1.5
        denominator[denominator < 1e-10] = 1e-10
        
        curvature = np.abs(dx * ddy - dy * ddx) / denominator
        return curvature
    
    curvature = calculate_curvature(center_x, center_y)
    curvature = np.nan_to_num(curvature)
    
    # Smooth curvature extensively
    curvature_smooth = gaussian_filter1d(curvature, sigma=30, mode='wrap')
    
    # Racing line strategy: late apex for tight corners
    # Normalize curvature
    max_curvature = np.percentile(curvature_smooth, 98)
    if max_curvature > 0:
        normalized_curvature = curvature_smooth / max_curvature
    else:
        normalized_curvature = curvature_smooth
    
    # Calculate track width at each point
    track_width = np.sqrt((out_x - in_x)**2 + (out_y - in_y)**2)
    
    # Racing line offset: move toward outside on corners for late apex
    # Use a smooth function that gradually increases offset with curvature
    offset_factor = 0.25 * np.tanh(3 * normalized_curvature)  # Smooth transition
    
    # Calculate perpendicular direction for offset
    dx = np.gradient(center_x)
    dy = np.gradient(center_y)
    length = np.sqrt(dx**2 + dy**2)
    length[length < 1e-10] = 1e-10  # Avoid division by zero
    
    # Unit perpendicular vector (toward outside of track)
    perp_x = -dy / length
    perp_y = dx / length
    
    # Apply racing line offset
    racing_line_x = center_x + offset_factor * perp_x * track_width / 2
    racing_line_y = center_y + offset_factor * perp_y * track_width / 2
    
    return racing_line_x, racing_line_y


if __name__ == "__main__":
    # Run the ultra-smooth track plotting
    outside_smooth, inside_smooth, racing_line_smooth = ultra_smooth_track_plot()
    
    if outside_smooth is not None:
        print("\nUltra-smooth track generation complete!")
        print(f"Generated {len(outside_smooth)} ultra-smooth points per boundary")
        print("The track should now look as smooth as the MATLAB version!")
    else:
        print("Track generation failed - check the input data.")
