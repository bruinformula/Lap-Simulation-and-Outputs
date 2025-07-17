"""
Quick Track Plotting
====================

Simple and robust track plotting from Excel coordinates.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Add parent directory to path to import from lap_simulation
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from lap_simulation import data_loader
from lap_simulation.output_utils import get_plot_path, print_save_message
from lap_simulation.output_utils import get_plot_path, print_save_message


def load_track_coordinates_safe(filename):
    """Safely load track coordinates using the proper data loader."""
    try:
        # Get the correct path to the Excel file
        current_dir = os.path.dirname(__file__)
        base_dir = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels
        filepath = os.path.join(base_dir, filename)
        
        print(f"Loading {filepath}...")
        
        # Use the proper data loader that handles both inside and outside boundaries
        track_data = data_loader.load_track_coordinates(filepath)
        
        # Extract both boundaries
        outside_track = track_data['outside_track']
        inside_track = track_data['inside_track']
        
        print(f"✓ Loaded {len(outside_track)} outside and {len(inside_track)} inside track points")
        
        return {
            'outside': outside_track,
            'inside': inside_track
        }
        
    except Exception as e:
        print(f"✗ Error loading {filename}: {e}")
        return None


def create_synthetic_racing_line(track_data):
    """Create a synthetic racing line between inside and outside boundaries."""
    if track_data is None:
        return None, None
    
    outside = track_data['outside_track']
    inside = track_data['inside_track']
    
    # Make sure both boundaries have the same number of points
    min_points = min(len(outside), len(inside))
    outside = outside[:min_points]
    inside = inside[:min_points]
    
    # Create racing line as center between boundaries
    racing_x = (outside[:, 0] + inside[:, 0]) / 2
    racing_y = (outside[:, 1] + inside[:, 1]) / 2
    
    # Smooth the racing line for better appearance
    try:
        from scipy.ndimage import gaussian_filter1d
        racing_x = gaussian_filter1d(racing_x, sigma=3)
        racing_y = gaussian_filter1d(racing_y, sigma=3)
    except ImportError:
        # Fall back to simple smoothing if scipy not available
        pass
    
    return racing_x, racing_y


def plot_racing_track(track_data, racing_x=None, racing_y=None, title="Racing Track"):
    """Plot the racing track with optional racing line."""
    
    if track_data is None:
        print(f"⚠ No coordinate data available for {title}")
        return
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Extract outside and inside boundaries
    outside = track_data['outside_track']
    inside = track_data['inside_track']
    
    # Plot track boundaries
    ax.plot(outside[:, 0], outside[:, 1], 'k-', linewidth=3, 
           label='Outside Boundary', alpha=0.8)
    ax.plot(inside[:, 0], inside[:, 1], 'k-', linewidth=3, 
           label='Inside Boundary', alpha=0.8)
    
    # Fill track area between boundaries
    from matplotlib.patches import Polygon
    # Create track polygon by combining outside and reversed inside boundaries
    track_polygon = np.vstack([outside, inside[::-1]])
    track_patch = Polygon(track_polygon, alpha=0.15, color='lightblue', label='Track Area')
    ax.add_patch(track_patch)
    
    # Plot racing line
    if racing_x is not None and racing_y is not None:
        ax.plot(racing_x, racing_y, 'r-', linewidth=3, 
               label='Racing Line', alpha=0.9)
        
        # Mark start/finish
        ax.scatter(racing_x[0], racing_y[0], s=250, c='green', 
                  marker='s', label='Start/Finish', zorder=10,
                  edgecolor='white', linewidth=3)
        
        # Add direction arrows every few points
        if len(racing_x) > 20:
            n_arrows = min(15, len(racing_x) // 8)
            arrow_indices = np.linspace(0, len(racing_x)-6, n_arrows, dtype=int)
            
            for i in arrow_indices:
                if i + 4 < len(racing_x):
                    dx = racing_x[i+4] - racing_x[i]
                    dy = racing_y[i+4] - racing_y[i]
                    arrow_length = np.sqrt(dx**2 + dy**2)
                    
                    if arrow_length > 0:
                        scale = max(5, arrow_length * 0.3)
                        ax.arrow(racing_x[i], racing_y[i], 
                                dx/arrow_length * scale, dy/arrow_length * scale,
                                head_width=scale*0.8, head_length=scale*0.6, 
                                fc='yellow', ec='red', alpha=0.8, zorder=8)
    
    # Calculate track statistics using outside boundary
    outside_x, outside_y = outside[:, 0], outside[:, 1]
    track_length = 0
    for i in range(len(outside_x)-1):
        track_length += np.sqrt((outside_x[i+1] - outside_x[i])**2 + (outside_y[i+1] - outside_y[i])**2)
    
    racing_length = 0
    if racing_x is not None and racing_y is not None:
        for i in range(len(racing_x)-1):
            racing_length += np.sqrt((racing_x[i+1] - racing_x[i])**2 + (racing_y[i+1] - racing_y[i])**2)
    
    # Add information box
    info_text = f'{title} Information:\n'
    info_text += f'• Outside boundary points: {len(outside)}\n'
    info_text += f'• Inside boundary points: {len(inside)}\n'
    info_text += f'• Track perimeter: {track_length:.0f} ft\n'
    if racing_x is not None:
        info_text += f'• Racing line length: {racing_length:.0f} ft\n'
        info_text += f'• Racing line points: {len(racing_x)}'
    
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
           verticalalignment='top', fontsize=11,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9))
    
    # Styling
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', framealpha=0.9, fontsize=11)
    ax.set_title(f'{title} Layout with Optimized Racing Line', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('X Position [ft]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y Position [ft]', fontsize=12, fontweight='bold')
    
    # Improve appearance
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)
    
    plt.tight_layout()
    
    # Save the plot
    filename = f"{title.lower().replace(' ', '_')}_plot.png"
    plot_path = get_plot_path(filename)
    plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
    print_save_message(plot_path, 'plot')
    
    plt.show()


def main():
    """Main function to create track plots."""
    print("🏁 Racing Track Visualization")
    print("=" * 50)
    
    # Set base directory for data files (two levels up from visualization/)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Load and plot endurance track
    print("\n📍 Endurance Track:")
    endurance_file = os.path.join(base_dir, "Endurance_Coordinates_1.xlsx")
    endurance_data = data_loader.load_track_coordinates(endurance_file)
    
    if endurance_data is not None:
        # Create synthetic racing line using center between boundaries
        racing_x, racing_y = create_synthetic_racing_line(endurance_data)
        
        print(f"Track loaded: Outside({len(endurance_data['outside_track'])}) Inside({len(endurance_data['inside_track'])}) points")
        if racing_x is not None:
            print(f"Racing line created: {len(racing_x)} points")
        
        plot_racing_track(endurance_data, racing_x, racing_y, "Endurance Track")
    
    print("\n" + "-" * 50)
    
    # Load and plot autocross track
    print("\n📍 Autocross Track:")
    autocross_file = os.path.join(base_dir, "Autocross_Coordinates_2.xlsx")
    autocross_data = data_loader.load_track_coordinates(autocross_file)
    
    if autocross_data is not None:
        # Create synthetic racing line using center between boundaries
        racing_x, racing_y = create_synthetic_racing_line(autocross_data)
        
        print(f"Track loaded: Outside({len(autocross_data['outside_track'])}) Inside({len(autocross_data['inside_track'])}) points")
        if racing_x is not None:
            print(f"Racing line created: {len(racing_x)} points")
        
        plot_racing_track(autocross_data, racing_x, racing_y, "Autocross Track")
    
    # Create comparison if both tracks available
    if (endurance_data is not None and autocross_data is not None):
        print("\n📊 Creating track comparison...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        fig.suptitle('Formula SAE Track Comparison', fontsize=18, fontweight='bold')
        
        # Endurance track
        e_outside = endurance_data['outside_track']
        e_inside = endurance_data['inside_track']
        
        ax1.plot(e_outside[:, 0], e_outside[:, 1], 'k-', linewidth=3, label='Outside Boundary')
        ax1.plot(e_inside[:, 0], e_inside[:, 1], 'k-', linewidth=3, label='Inside Boundary')
        
        # Fill track area
        from matplotlib.patches import Polygon
        track_polygon = np.vstack([e_outside, e_inside[::-1]])
        track_patch = Polygon(track_polygon, alpha=0.15, color='lightblue')
        ax1.add_patch(track_patch)
        
        # Add racing line
        e_racing_x, e_racing_y = create_synthetic_racing_line(endurance_data)
        if e_racing_x is not None and e_racing_y is not None:
            ax1.plot(e_racing_x, e_racing_y, 'r-', linewidth=3, label='Racing Line')
            ax1.scatter(e_racing_x[0], e_racing_y[0], s=200, c='green', 
                       marker='s', label='Start/Finish', zorder=10)
        
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_title('Endurance Track', fontsize=14, fontweight='bold')
        ax1.set_xlabel('X Position [ft]')
        ax1.set_ylabel('Y Position [ft]')
        
        # Autocross track
        a_outside = autocross_data['outside_track']
        a_inside = autocross_data['inside_track']
        
        ax2.plot(a_outside[:, 0], a_outside[:, 1], 'k-', linewidth=3, label='Outside Boundary')
        ax2.plot(a_inside[:, 0], a_inside[:, 1], 'k-', linewidth=3, label='Inside Boundary')
        
        # Fill track area
        track_polygon = np.vstack([a_outside, a_inside[::-1]])
        track_patch = Polygon(track_polygon, alpha=0.15, color='lightcoral')
        ax2.add_patch(track_patch)
        
        # Add racing line
        a_racing_x, a_racing_y = create_synthetic_racing_line(autocross_data)
        if a_racing_x is not None and a_racing_y is not None:
            ax2.plot(a_racing_x, a_racing_y, 'r-', linewidth=3, label='Racing Line')
            ax2.scatter(a_racing_x[0], a_racing_y[0], s=200, c='green', 
                       marker='s', label='Start/Finish', zorder=10)
        
        ax2.set_aspect('equal')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_title('Autocross Track', fontsize=14, fontweight='bold')
        ax2.set_xlabel('X Position [ft]')
        ax2.set_ylabel('Y Position [ft]')
        
        plt.tight_layout()
        plot_path = get_plot_path('track_comparison.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        print_save_message(plot_path, 'plot')
        plt.show()
        
        print("✓ Saved comparison as track_comparison.png")
    
    print("\n" + "=" * 50)
    print("🎉 Track visualization complete!")
    print("Check the generated PNG files for the track layouts.")


if __name__ == "__main__":
    main()
