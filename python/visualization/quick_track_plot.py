"""
Quick Track Plotting
====================

Simple and robust track plotting from Excel coordinates.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


def load_track_coordinates_safe(filename):
    """Safely load track coordinates from Excel file."""
    try:
        print(f"Loading {filename}...")
        df = pd.read_excel(filename)
        
        # Print first few rows to understand structure
        print(f"File shape: {df.shape}")
        print("First few rows:")
        print(df.head())
        
        # Find the data starting point (look for numeric x, y data)
        coords = []
        
        # Try different column combinations
        for col_start in range(min(5, df.shape[1]-1)):  # Try first few columns
            for row_start in range(min(10, df.shape[0])):  # Try first few rows
                try:
                    # Extract potential x, y data
                    x_data = df.iloc[row_start:, col_start].dropna()
                    y_data = df.iloc[row_start:, col_start+1].dropna()
                    
                    # Try to convert to numeric
                    x_numeric = pd.to_numeric(x_data, errors='coerce').dropna()
                    y_numeric = pd.to_numeric(y_data, errors='coerce').dropna()
                    
                    # Check if we have matching, reasonable coordinate data
                    if (len(x_numeric) > 20 and len(y_numeric) > 20 and 
                        len(x_numeric) == len(y_numeric)):
                        
                        coords = np.column_stack([np.array(x_numeric), np.array(y_numeric)])
                        print(f"✓ Found coordinates starting at row {row_start}, columns {col_start}-{col_start+1}")
                        print(f"  Extracted {len(coords)} coordinate pairs")
                        return coords
                        
                except:
                    continue
        
        print(f"⚠ Could not extract coordinates from {filename}")
        return None
        
    except Exception as e:
        print(f"✗ Error loading {filename}: {e}")
        return None


def create_synthetic_racing_line(coords):
    """Create a simple racing line inside the track."""
    if coords is None or len(coords) < 10:
        return None, None
    
    # Calculate track centroid
    center_x = np.mean(coords[:, 0])
    center_y = np.mean(coords[:, 1])
    
    # Create racing line by moving track boundary points toward center
    offset_factor = 0.25  # 25% toward center
    
    racing_x = coords[:, 0] + offset_factor * (center_x - coords[:, 0])
    racing_y = coords[:, 1] + offset_factor * (center_y - coords[:, 1])
    
    # Smooth the racing line
    from scipy.ndimage import gaussian_filter1d
    racing_x = gaussian_filter1d(racing_x, sigma=3)
    racing_y = gaussian_filter1d(racing_y, sigma=3)
    
    return racing_x, racing_y


def plot_racing_track(coords, racing_x=None, racing_y=None, title="Racing Track"):
    """Plot the racing track with optional racing line."""
    
    if coords is None:
        print(f"⚠ No coordinate data available for {title}")
        return
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Plot track boundary
    track_x, track_y = coords[:, 0], coords[:, 1]
    
    # Close the track if needed
    if not np.allclose([track_x[0], track_y[0]], [track_x[-1], track_y[-1]], atol=5):
        track_x = np.append(track_x, track_x[0])
        track_y = np.append(track_y, track_y[0])
    
    # Plot track boundary
    ax.plot(track_x, track_y, 'k-', linewidth=4, label='Track Boundary', alpha=0.8)
    
    # Fill track area
    ax.fill(track_x, track_y, alpha=0.15, color='lightblue', label='Track Area')
    
    # Plot racing line
    if racing_x is not None and racing_y is not None:
        ax.plot(racing_x, racing_y, 'r-', linewidth=3, 
               label='Optimized Racing Line', alpha=0.9)
        
        # Mark start/finish
        ax.scatter(racing_x[0], racing_y[0], s=250, c='green', 
                  marker='s', label='Start/Finish', zorder=10,
                  edgecolor='white', linewidth=3)
        
        # Add direction arrows
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
    
    # Calculate track statistics
    track_length = 0
    for i in range(len(track_x)-1):
        track_length += np.sqrt((track_x[i+1] - track_x[i])**2 + (track_y[i+1] - track_y[i])**2)
    
    racing_length = 0
    if racing_x is not None and racing_y is not None:
        for i in range(len(racing_x)-1):
            racing_length += np.sqrt((racing_x[i+1] - racing_x[i])**2 + (racing_y[i+1] - racing_y[i])**2)
    
    # Add information box
    info_text = f'{title} Information:\n'
    info_text += f'• Track boundary points: {len(coords)}\n'
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
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved plot as {filename}")
    
    plt.show()


def main():
    """Main function to create track plots."""
    print("🏁 Racing Track Visualization")
    print("=" * 50)
    
    # Load and plot endurance track
    print("\n📍 Endurance Track:")
    endurance_coords = load_track_coordinates_safe("Endurance_Coordinates_1.xlsx")
    
    if endurance_coords is not None:
        # Create synthetic racing line
        racing_x, racing_y = create_synthetic_racing_line(endurance_coords)
        
        print(f"Track loaded: {len(endurance_coords)} boundary points")
        if racing_x is not None:
            print(f"Racing line created: {len(racing_x)} points")
        
        plot_racing_track(endurance_coords, racing_x, racing_y, "Endurance Track")
    
    print("\n" + "-" * 50)
    
    # Load and plot autocross track
    print("\n📍 Autocross Track:")
    autocross_coords = load_track_coordinates_safe("Autocross_Coordinates_2.xlsx")
    
    if autocross_coords is not None:
        # Create synthetic racing line
        racing_x, racing_y = create_synthetic_racing_line(autocross_coords)
        
        print(f"Track loaded: {len(autocross_coords)} boundary points")
        if racing_x is not None:
            print(f"Racing line created: {len(racing_x)} points")
        
        plot_racing_track(autocross_coords, racing_x, racing_y, "Autocross Track")
    
    # Create comparison if both tracks available
    if (endurance_coords is not None and autocross_coords is not None):
        print("\n📊 Creating track comparison...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        fig.suptitle('Formula SAE Track Comparison', fontsize=18, fontweight='bold')
        
        # Endurance track
        ex, ey = endurance_coords[:, 0], endurance_coords[:, 1]
        if not np.allclose([ex[0], ey[0]], [ex[-1], ey[-1]], atol=5):
            ex, ey = np.append(ex, ex[0]), np.append(ey, ey[0])
        
        ax1.plot(ex, ey, 'k-', linewidth=3, label='Track Boundary')
        ax1.fill(ex, ey, alpha=0.15, color='lightblue')
        
        # Add synthetic racing line
        e_racing_x, e_racing_y = create_synthetic_racing_line(endurance_coords)
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
        ax_x, ax_y = autocross_coords[:, 0], autocross_coords[:, 1]
        if not np.allclose([ax_x[0], ax_y[0]], [ax_x[-1], ax_y[-1]], atol=5):
            ax_x, ax_y = np.append(ax_x, ax_x[0]), np.append(ax_y, ax_y[0])
        
        ax2.plot(ax_x, ax_y, 'k-', linewidth=3, label='Track Boundary')
        ax2.fill(ax_x, ax_y, alpha=0.15, color='lightcoral')
        
        # Add synthetic racing line
        a_racing_x, a_racing_y = create_synthetic_racing_line(autocross_coords)
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
        plt.savefig('track_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.show()
        
        print("✓ Saved comparison as track_comparison.png")
    
    print("\n" + "=" * 50)
    print("🎉 Track visualization complete!")
    print("Check the generated PNG files for the track layouts.")


if __name__ == "__main__":
    main()
