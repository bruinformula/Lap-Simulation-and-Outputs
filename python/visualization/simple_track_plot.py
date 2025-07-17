"""
Simplified Track Plotting - Quick Fix
=====================================

A simplified version to quickly plot the racing tracks from the available data.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import os
from scipy.io import loadmat


def load_endurance_coordinates():
    """Load endurance track coordinates from Excel file."""
    try:
        df = pd.read_excel('Endurance_Coordinates_1.xlsx')
        
        # The data structure shows x in column 'Unnamed: 1' and y in 'Unnamed: 2'
        # Starting from row 2 (index 2) after headers
        coords_data = df.iloc[2:, 1:3]  # Get x, y columns starting from row 2
        
        # Clean the data - remove non-numeric entries
        coords_clean = []
        for idx, row in coords_data.iterrows():
            try:
                x = float(row.iloc[0])
                y = float(row.iloc[1])
                coords_clean.append([x, y])
            except:
                continue
        
        return np.array(coords_clean)
    except Exception as e:
        print(f"Error loading endurance coordinates: {e}")
        return None


def load_autocross_coordinates():
    """Load autocross track coordinates from Excel file."""
    try:
        df = pd.read_excel('Autocross_Coordinates_2.xlsx')
        
        # Similar structure to endurance
        coords_data = df.iloc[2:, 1:3]  # Get x, y columns starting from row 2
        
        # Clean the data
        coords_clean = []
        for idx, row in coords_data.iterrows():
            try:
                x = float(row.iloc[0])
                y = float(row.iloc[1])
                coords_clean.append([x, y])
            except:
                continue
        
        return np.array(coords_clean)
    except Exception as e:
        print(f"Error loading autocross coordinates: {e}")
        return None


def load_racing_line_from_mat(filename):
    """Load racing line data from .mat file."""
    try:
        data = loadmat(f"Data Files/{filename}")
        
        # Look for the racing line data
        racing_line_key = filename.replace('.mat', '').replace('_', '_')
        
        if racing_line_key in data:
            racing_line = data[racing_line_key]
            if racing_line.ndim == 2 and racing_line.shape[1] >= 2:
                return racing_line[:, 0], racing_line[:, 1]
            elif racing_line.ndim == 2 and racing_line.shape[0] >= 2:
                return racing_line[0, :], racing_line[1, :]
        
        # Try other common keys
        for key in ['vehicle_path', 'path_points', 'racing_line', 'track', 'x', 'y']:
            if key in data:
                path_data = data[key]
                if isinstance(path_data, np.ndarray) and path_data.size > 10:
                    if path_data.ndim == 2 and path_data.shape[1] >= 2:
                        return path_data[:, 0], path_data[:, 1]
                    elif path_data.ndim == 2 and path_data.shape[0] >= 2:
                        return path_data[0, :], path_data[1, :]
        
        # Try x and y separately
        if 'x' in data and 'y' in data:
            x_data = np.array(data['x']).flatten()
            y_data = np.array(data['y']).flatten()
            if len(x_data) == len(y_data) and len(x_data) > 10:
                return x_data, y_data
        
        print(f"Available keys in {filename}: {list(data.keys())}")
        return None, None
        
    except Exception as e:
        print(f"Error loading racing line from {filename}: {e}")
        return None, None


def plot_track_simple(coords, racing_x=None, racing_y=None, title="Race Track", save_name=None):
    """Plot track with optional racing line."""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    if coords is not None and len(coords) > 0:
        # Plot track boundary
        track_x = coords[:, 0]
        track_y = coords[:, 1]
        
        # Close the track if not already closed
        if not (track_x[0] == track_x[-1] and track_y[0] == track_y[-1]):
            track_x = np.append(track_x, track_x[0])
            track_y = np.append(track_y, track_y[0])
        
        # Plot track boundary
        ax.plot(track_x, track_y, 'k-', linewidth=3, label='Track Boundary')
        
        # Fill track area
        ax.fill(track_x, track_y, alpha=0.1, color='lightgray')
        
        print(f"✓ Plotted track boundary: {len(coords)} points")
        
        # Calculate and display track info
        track_length = np.sum(np.sqrt(np.diff(track_x)**2 + np.diff(track_y)**2))
        
        info_text = f'{title} Information:\n'
        info_text += f'• Boundary points: {len(coords)}\n'
        info_text += f'• Track length: {track_length:.0f} ft'
        
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
               verticalalignment='top', bbox=dict(boxstyle='round', 
               facecolor='white', alpha=0.9), fontsize=11)
    
    # Plot racing line if available
    if racing_x is not None and racing_y is not None:
        ax.plot(racing_x, racing_y, 'r-', linewidth=3, 
               label='Optimized Racing Line', alpha=0.8)
        
        # Mark start/finish
        ax.scatter(racing_x[0], racing_y[0], s=200, c='green', 
                  marker='s', label='Start/Finish', zorder=10,
                  edgecolor='white', linewidth=2)
        
        # Add direction arrows
        n_arrows = 12
        arrow_spacing = len(racing_x) // n_arrows
        for i in range(0, len(racing_x) - 5, arrow_spacing):
            dx = racing_x[i+3] - racing_x[i]
            dy = racing_y[i+3] - racing_y[i]
            arrow_length = np.sqrt(dx**2 + dy**2)
            if arrow_length > 0:
                scale = 8  # Arrow size
                ax.arrow(racing_x[i], racing_y[i], 
                        dx/arrow_length * scale, dy/arrow_length * scale,
                        head_width=3, head_length=2, fc='yellow', 
                        ec='red', alpha=0.8, zorder=8)
        
        print(f"✓ Plotted racing line: {len(racing_x)} points")
        
        # Update info text
        if coords is not None:
            racing_length = np.sum(np.sqrt(np.diff(racing_x)**2 + np.diff(racing_y)**2))
            info_text += f'\n• Racing line length: {racing_length:.0f} ft'
            info_text += f'\n• Racing line points: {len(racing_x)}'
            
            # Update the text box
            ax.texts[0].set_text(info_text)
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.set_title(title + ' Layout with Optimized Racing Line', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('X Position [ft]', fontsize=12)
    ax.set_ylabel('Y Position [ft]', fontsize=12)
    
    plt.tight_layout()
    
    if save_name:
        plt.savefig(save_name, dpi=300, bbox_inches='tight')
        print(f"✓ Saved plot as {save_name}")
    
    plt.show()


def main():
    """Main function to load and plot tracks."""
    print("Racing Track Visualization")
    print("=" * 40)
    
    # Load endurance track
    print("\nLoading Endurance Track...")
    endurance_coords = load_endurance_coordinates()
    endurance_racing_x, endurance_racing_y = load_racing_line_from_mat("endurance_racing_line.mat")
    
    if endurance_coords is not None:
        print(f"Loaded endurance track: {len(endurance_coords)} boundary points")
        if endurance_racing_x is not None:
            print(f"Loaded endurance racing line: {len(endurance_racing_x)} points")
        
        plot_track_simple(endurance_coords, endurance_racing_x, endurance_racing_y,
                         "Endurance Track", "endurance_track_plot.png")
    
    # Load autocross track
    print("\nLoading Autocross Track...")
    autocross_coords = load_autocross_coordinates()
    autocross_racing_x, autocross_racing_y = load_racing_line_from_mat("autocross_racing_line.mat")
    
    if autocross_coords is not None:
        print(f"Loaded autocross track: {len(autocross_coords)} boundary points")
        if autocross_racing_x is not None:
            print(f"Loaded autocross racing line: {len(autocross_racing_x)} points")
        
        plot_track_simple(autocross_coords, autocross_racing_x, autocross_racing_y,
                         "Autocross Track", "autocross_track_plot.png")
    
    # Create comparison plot if both tracks loaded
    if endurance_coords is not None and autocross_coords is not None:
        print("\nCreating comparison plot...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        
        # Endurance subplot
        ex, ey = endurance_coords[:, 0], endurance_coords[:, 1]
        if not (ex[0] == ex[-1] and ey[0] == ey[-1]):
            ex, ey = np.append(ex, ex[0]), np.append(ey, ey[0])
        
        ax1.plot(ex, ey, 'k-', linewidth=3, label='Track Boundary')
        ax1.fill(ex, ey, alpha=0.1, color='lightgray')
        
        if endurance_racing_x is not None:
            ax1.plot(endurance_racing_x, endurance_racing_y, 'r-', 
                    linewidth=3, label='Racing Line')
            ax1.scatter(endurance_racing_x[0], endurance_racing_y[0], 
                       s=150, c='green', marker='s', label='Start/Finish')
        
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_title('Endurance Track', fontsize=14, fontweight='bold')
        ax1.set_xlabel('X Position [ft]')
        ax1.set_ylabel('Y Position [ft]')
        
        # Autocross subplot
        ax, ay = autocross_coords[:, 0], autocross_coords[:, 1]
        if not (ax[0] == ax[-1] and ay[0] == ay[-1]):
            ax, ay = np.append(ax, ax[0]), np.append(ay, ay[0])
        
        ax2.plot(ax, ay, 'k-', linewidth=3, label='Track Boundary')
        ax2.fill(ax, ay, alpha=0.1, color='lightgray')
        
        if autocross_racing_x is not None:
            ax2.plot(autocross_racing_x, autocross_racing_y, 'r-', 
                    linewidth=3, label='Racing Line')
            ax2.scatter(autocross_racing_x[0], autocross_racing_y[0], 
                       s=150, c='green', marker='s', label='Start/Finish')
        
        ax2.set_aspect('equal')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_title('Autocross Track', fontsize=14, fontweight='bold')
        ax2.set_xlabel('X Position [ft]')
        ax2.set_ylabel('Y Position [ft]')
        
        plt.tight_layout()
        plt.savefig('track_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✓ Saved comparison plot as track_comparison.png")
    
    print("\n" + "=" * 40)
    print("Track visualization complete!")


if __name__ == "__main__":
    main()
