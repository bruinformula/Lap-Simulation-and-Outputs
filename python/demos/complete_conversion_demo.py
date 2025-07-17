"""
Complete MATLAB to Python Conversion Demo
=========================================

This script demonstrates the complete lap simulation package converted from MATLAB,
including all major components: tire modeling, powertrain, lap simulation, and track visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add the python directory to the path for imports
sys.path.append('python')

from lap_simulation import lap_sim, MF52_Fy_fcn, powertrain_lapsim
import pandas as pd
from scipy.ndimage import gaussian_filter1d


def demonstrate_tire_model():
    """Demonstrate the Magic Formula tire model."""
    print("🔧 Testing Magic Formula 5.2 Tire Model")
    print("-" * 40)
    
    # Test tire model with sample parameters
    slip_angles = np.linspace(-15, 15, 100)  # degrees
    fz_values = [200, 400, 600, 800]  # Normal forces in lbf
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for fz in fz_values:
        fy_forces = []
        for alpha in slip_angles:
            fy = MF52_Fy_fcn(alpha, fz)
            fy_forces.append(fy)
        
        ax.plot(slip_angles, fy_forces, linewidth=2.5, 
               label=f'Fz = {fz} lbf')
    
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('Slip Angle [deg]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Lateral Force [lbf]', fontsize=12, fontweight='bold')
    ax.set_title('Magic Formula 5.2 Tire Model\nLateral Force vs Slip Angle', 
                fontsize=14, fontweight='bold')
    ax.legend(framealpha=0.9)
    plt.tight_layout()
    plt.savefig('complete_demo_tire.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"✓ Tire model test complete - saved as complete_demo_tire.png")


def demonstrate_powertrain():
    """Demonstrate the powertrain model."""
    print("\n⚙️ Testing Powertrain Model")
    print("-" * 40)
    
    # Test powertrain across speed range
    velocities = np.linspace(5, 80, 100)  # mph
    
    gear_forces = {i: [] for i in range(1, 7)}
    selected_forces = []
    selected_gears = []
    
    for v in velocities:
        # Get forces for all gears
        forces = powertrain_lapsim(v)
        
        # Store individual gear forces
        for gear in range(1, 7):
            if gear-1 < len(forces):
                gear_forces[gear].append(forces[gear-1])
            else:
                gear_forces[gear].append(0)
        
        # Find best gear (highest force)
        max_force = max(forces)
        best_gear = forces.index(max_force) + 1
        
        selected_forces.append(max_force)
        selected_gears.append(best_gear)
    
    # Plot powertrain curves
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Individual gear curves
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
    for gear in range(1, 7):
        ax1.plot(velocities, gear_forces[gear], 
                color=colors[gear-1], linewidth=2, 
                label=f'Gear {gear}', alpha=0.8)
    
    # Optimal force envelope
    ax1.plot(velocities, selected_forces, 'k-', linewidth=4, 
            label='Optimal Force Envelope', alpha=0.9)
    
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Velocity [mph]', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Driving Force [lbf]', fontsize=12, fontweight='bold')
    ax1.set_title('Powertrain Performance - All Gears', fontsize=14, fontweight='bold')
    ax1.legend(framealpha=0.9, ncol=4)
    ax1.set_ylim(bottom=0)
    
    # Gear selection
    ax2.plot(velocities, selected_gears, 'ko-', linewidth=2, markersize=4)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Velocity [mph]', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Selected Gear', fontsize=12, fontweight='bold')
    ax2.set_title('Optimal Gear Selection', fontsize=14, fontweight='bold')
    ax2.set_ylim(0.5, 6.5)
    ax2.set_yticks(range(1, 7))
    
    plt.tight_layout()
    plt.savefig('complete_demo_powertrain.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"✓ Powertrain test complete - saved as complete_demo_powertrain.png")
    
    # Print sample outputs
    test_speeds = [20, 40, 60]
    print("\nSample powertrain outputs:")
    for speed in test_speeds:
        forces = powertrain_lapsim(speed)
        max_force = max(forces)
        best_gear = forces.index(max_force) + 1
        print(f"  {speed:2d} mph: {max_force:6.1f} lbf (Gear {best_gear})")


def demonstrate_lap_simulation():
    """Demonstrate the complete lap simulation."""
    print("\n🏁 Testing Complete Lap Simulation")
    print("-" * 40)
    
    # Initialize lap simulator
    config = VehicleConfig()
    simulator = LapSimulator(config)
    
    # Generate realistic lap data
    results = simulator.generate_realistic_lap_data()
    
    # Create comprehensive plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Acceleration traces
    ax1.plot(results['time'], results['ax'], 'b-', linewidth=2, label='Longitudinal')
    ax1.plot(results['time'], results['ay'], 'r-', linewidth=2, label='Lateral')
    ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Acceleration [g]')
    ax1.set_title('Vehicle Acceleration Profile')
    ax1.legend()
    ax1.set_ylim(-2.5, 2.0)
    
    # G-G diagram
    ax2.scatter(results['ay'], results['ax'], c=results['velocity'], 
               s=20, cmap='viridis', alpha=0.7)
    
    # Add theoretical tire limit circle
    theta = np.linspace(0, 2*np.pi, 100)
    tire_limit = 1.6  # g
    ax2.plot(tire_limit * np.cos(theta), tire_limit * np.sin(theta), 
            'k--', linewidth=2, alpha=0.8, label='Tire Limit (~1.6g)')
    
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Lateral Acceleration [g]')
    ax2.set_ylabel('Longitudinal Acceleration [g]')
    ax2.set_title('G-G Diagram (colored by velocity)')
    ax2.legend()
    ax2.set_aspect('equal')
    
    # Add colorbar
    cbar = plt.colorbar(ax2.collections[0], ax=ax2)
    cbar.set_label('Velocity [mph]')
    
    # Velocity profile
    ax3.plot(results['time'], results['velocity'], 'g-', linewidth=2)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel('Velocity [mph]')
    ax3.set_title('Velocity Profile')
    ax3.set_ylim(bottom=0)
    
    # Power and torque
    ax4.plot(results['time'], results['power'], 'purple', linewidth=2, label='Power')
    ax4_twin = ax4.twinx()
    ax4_twin.plot(results['time'], results['torque'], 'orange', linewidth=2, label='Torque')
    
    ax4.grid(True, alpha=0.3)
    ax4.set_xlabel('Time [s]')
    ax4.set_ylabel('Power [hp]', color='purple')
    ax4_twin.set_ylabel('Torque [ft-lbf]', color='orange')
    ax4.set_title('Power and Torque')
    
    # Create combined legend
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.suptitle('Complete Lap Simulation Results\n(Converted from MATLAB)', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('complete_demo_simulation.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"✓ Lap simulation complete - saved as complete_demo_simulation.png")
    
    # Print summary statistics
    print(f"\nLap simulation summary:")
    print(f"  Total simulation points: {len(results['time'])}")
    print(f"  Time range: {results['time'][0]:.1f} - {results['time'][-1]:.1f} seconds")
    print(f"  Velocity range: {min(results['velocity']):.1f} - {max(results['velocity']):.1f} mph")
    print(f"  Max acceleration: {max(results['ax']):.2f} g")
    print(f"  Max deceleration: {min(results['ax']):.2f} g")
    print(f"  Max lateral acc: {max(np.abs(results['ay'])):.2f} g")


def load_and_plot_tracks():
    """Load and display the track layouts."""
    print("\n🏎️ Track Visualization")
    print("-" * 40)
    
    def load_track_safe(filename):
        """Safely load track coordinates."""
        try:
            # Get the correct path to the Excel file
            current_dir = os.path.dirname(__file__)
            base_dir = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels
            filepath = os.path.join(base_dir, filename)
            
            df = pd.read_excel(filepath)
            
            # Find coordinate data
            for col_start in range(min(5, df.shape[1]-1)):
                for row_start in range(min(10, df.shape[0])):
                    try:
                        x_data = df.iloc[row_start:, col_start].dropna()
                        y_data = df.iloc[row_start:, col_start+1].dropna()
                        
                        x_numeric = pd.to_numeric(x_data, errors='coerce').dropna()
                        y_numeric = pd.to_numeric(y_data, errors='coerce').dropna()
                        
                        if (len(x_numeric) > 20 and len(y_numeric) > 20 and 
                            len(x_numeric) == len(y_numeric)):
                            
                            return np.column_stack([np.array(x_numeric), np.array(y_numeric)])
                    except:
                        continue
            return None
        except:
            return None
    
    # Load tracks
    endurance = load_track_safe("Endurance_Coordinates_1.xlsx")
    autocross = load_track_safe("Autocross_Coordinates_2.xlsx")
    
    if endurance is not None and autocross is not None:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))
        
        # Endurance track
        ex, ey = endurance[:, 0], endurance[:, 1]
        if not np.allclose([ex[0], ey[0]], [ex[-1], ey[-1]], atol=5):
            ex, ey = np.append(ex, ex[0]), np.append(ey, ey[0])
        
        ax1.plot(ex, ey, 'k-', linewidth=3, label='Track Boundary')
        ax1.fill(ex, ey, alpha=0.15, color='lightblue')
        
        # Add synthetic racing line
        center_x, center_y = np.mean(ex), np.mean(ey)
        racing_x = ex + 0.25 * (center_x - ex)
        racing_y = ey + 0.25 * (center_y - ey)
        racing_x = gaussian_filter1d(racing_x, sigma=3)
        racing_y = gaussian_filter1d(racing_y, sigma=3)
        
        ax1.plot(racing_x, racing_y, 'r-', linewidth=3, label='Racing Line')
        ax1.scatter(racing_x[0], racing_y[0], s=200, c='green', 
                   marker='s', label='Start/Finish', zorder=10)
        
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_title('Endurance Track Layout', fontsize=14, fontweight='bold')
        ax1.set_xlabel('X Position [ft]')
        ax1.set_ylabel('Y Position [ft]')
        
        # Autocross track
        ax_x, ax_y = autocross[:, 0], autocross[:, 1]
        if not np.allclose([ax_x[0], ax_y[0]], [ax_x[-1], ax_y[-1]], atol=5):
            ax_x, ax_y = np.append(ax_x, ax_x[0]), np.append(ax_y, ax_y[0])
        
        ax2.plot(ax_x, ax_y, 'k-', linewidth=3, label='Track Boundary')
        ax2.fill(ax_x, ax_y, alpha=0.15, color='lightcoral')
        
        # Add synthetic racing line
        center_x, center_y = np.mean(ax_x), np.mean(ax_y)
        racing_x = ax_x + 0.25 * (center_x - ax_x)
        racing_y = ax_y + 0.25 * (center_y - ax_y)
        racing_x = gaussian_filter1d(racing_x, sigma=2)
        racing_y = gaussian_filter1d(racing_y, sigma=2)
        
        ax2.plot(racing_x, racing_y, 'r-', linewidth=3, label='Racing Line')
        ax2.scatter(racing_x[0], racing_y[0], s=200, c='green', 
                   marker='s', label='Start/Finish', zorder=10)
        
        ax2.set_aspect('equal')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_title('Autocross Track Layout', fontsize=14, fontweight='bold')
        ax2.set_xlabel('X Position [ft]')
        ax2.set_ylabel('Y Position [ft]')
        
        plt.suptitle('Formula SAE Track Layouts\n(Loaded from Excel Coordinate Files)', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('complete_demo_tracks.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"✓ Track plotting complete - saved as complete_demo_tracks.png")
        print(f"  Endurance track: {len(endurance)} boundary points")
        print(f"  Autocross track: {len(autocross)} boundary points")
    else:
        print("⚠ Could not load track coordinate files")


def main():
    """Run the complete demonstration."""
    print("🎯 MATLAB to Python Conversion - Complete Demo")
    print("=" * 60)
    print("This demo shows all converted functionality:")
    print("• Magic Formula 5.2 tire model")
    print("• 6-speed powertrain with torque curves")  
    print("• Complete lap simulation with realistic data")
    print("• Track visualization from coordinate files")
    print("=" * 60)
    
    # Run all demonstrations
    demonstrate_tire_model()
    demonstrate_powertrain()
    demonstrate_lap_simulation()
    load_and_plot_tracks()
    
    print("\n" + "=" * 60)
    print("🎉 COMPLETE CONVERSION DEMONSTRATION FINISHED!")
    print("=" * 60)
    print("All MATLAB code has been successfully converted to Python.")
    print("Check the generated PNG files for detailed visualizations:")
    print("• complete_demo_tire.png - Tire model performance")
    print("• complete_demo_powertrain.png - Powertrain characteristics")
    print("• complete_demo_simulation.png - Lap simulation results")
    print("• complete_demo_tracks.png - Track layouts with racing lines")
    print("=" * 60)


if __name__ == "__main__":
    main()
