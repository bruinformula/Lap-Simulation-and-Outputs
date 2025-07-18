"""
Phase 1 Integration Demo
=======================

Demonstrates integration of Phase 1 physics (individual wheel loads, slip angles,
and suspension kinematics) with the existing lap simulation framework.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lap_simulation.phase1_physics import (
    calculate_individual_wheel_loads,
    calculate_slip_angles_and_yaw_moment,
    calculate_suspension_effects,
    validate_wheel_loads
)
from lap_simulation.physics import (
    calculate_realistic_velocities,
    calculate_track_curvature,
    calculate_cumulative_distance,
    calculate_signed_curvature
)
from lap_simulation.data_loader import load_track_coordinates
from vehicle_config import get_vehicle_config


def run_phase1_enhanced_simulation(track_file='autocross_racing_line.mat'):
    """
    Run lap simulation with Phase 1 enhanced physics.
    
    Parameters:
    -----------
    track_file : str
        Track data file to load
    """
    print("Phase 1 Enhanced Lap Simulation")
    print("=" * 50)
    
    # Load vehicle configuration
    vehicle_config = get_vehicle_config()
    
    # Load track data or create dummy data
    try:
        track_path = f"/Users/Hiro/Documents/Programming/GitHub/Lap-Simulation and Outputs/Data Files/{track_file}"
        track_data = load_track_coordinates(track_path)
        x_coords = track_data['x']
        y_coords = track_data['y']
        print(f"Loaded track: {track_file}")
        print(f"Track length: {len(x_coords)} points")
    except Exception as e:
        print(f"Could not load track data: {e}")
        print("Using dummy track data for demo...")
        
        # Create dummy track (simple oval with varying curvature)
        t = np.linspace(0, 2*np.pi, 200)
        x_coords = 100 * (1 + 0.3*np.cos(2*t)) * np.cos(t)
        y_coords = 60 * (1 + 0.2*np.sin(3*t)) * np.sin(t)
    
    # Calculate basic track properties
    print("\n1. Calculating track properties...")
    distances = calculate_cumulative_distance(x_coords, y_coords)
    curvatures = calculate_signed_curvature(x_coords, y_coords)
    
    # Calculate velocity profile
    print("2. Calculating velocity profile...")
    velocities = calculate_realistic_velocities(x_coords, y_coords, 'autocross')
    
    # Calculate accelerations from velocity and curvature
    lateral_accel_g = np.zeros_like(velocities)
    longitudinal_accel_g = np.zeros_like(velocities)
    
    for i in range(len(velocities)):
        if i > 0:
            # Calculate longitudinal acceleration from velocity change
            dt = 0.1  # Approximate time step
            dv = velocities[i] - velocities[i-1]
            longitudinal_accel_g[i] = (dv / dt) / 9.81
            
        # Calculate lateral acceleration from velocity and curvature
        if abs(curvatures[i]) > 1e-6:
            lateral_accel_g[i] = (velocities[i]**2 * abs(curvatures[i])) / 9.81
    
    # Create standard results dictionary
    standard_results = {
        'velocities': velocities,
        'lateral_accel_g': lateral_accel_g,
        'longitudinal_accel_g': longitudinal_accel_g,
        'distances': distances,
        'curvatures': curvatures,
        'x_coords': x_coords,
        'y_coords': y_coords
    }
    
    print(f"   Calculated {len(velocities)} points")
    print(f"   Max velocity: {np.max(velocities):.1f} m/s")
    print(f"   Max lateral accel: {np.max(np.abs(lateral_accel_g)):.2f} g")
    
    # Run Phase 1 enhanced calculations
    print("\n2. Running Phase 1 enhanced calculations...")
    
    # Calculate individual wheel loads
    wheel_loads = calculate_individual_wheel_loads(
        lateral_accel_g, longitudinal_accel_g, velocities, vehicle_config
    )
    
    # Validate wheel loads
    validation = validate_wheel_loads(wheel_loads, vehicle_config)
    print(f"   Wheel load validation: {'PASS' if validation['weight_balance_ok'] else 'FAIL'}")
    print(f"   Max weight error: {validation['max_weight_error']:.2f} N")
    print(f"   Front weight distribution: {validation['front_weight_percentage']:.1f}%")
    
    # Calculate suspension effects
    suspension_effects = calculate_suspension_effects(
        lateral_accel_g, longitudinal_accel_g, vehicle_config
    )
    
    print(f"   Max front roll angle: {np.rad2deg(np.max(np.abs(suspension_effects['roll_angle_front']))):.2f} deg")
    print(f"   Max rear roll angle: {np.rad2deg(np.max(np.abs(suspension_effects['roll_angle_rear']))):.2f} deg")
    
    # Calculate slip angles and yaw moments for selected points
    print("\n3. Calculating vehicle dynamics at key points...")
    dynamics_results = []
    
    # Select points with high lateral acceleration
    high_lat_indices = np.where(np.abs(lateral_accel_g) > 0.5)[0]
    sample_indices = high_lat_indices[::len(high_lat_indices)//5] if len(high_lat_indices) > 5 else high_lat_indices
    
    for i in sample_indices:
        dynamics = calculate_slip_angles_and_yaw_moment(
            float(velocities[i]), float(curvatures[i]), vehicle_config
        )
        dynamics['index'] = i
        dynamics['velocity'] = velocities[i]
        dynamics['lateral_accel'] = lateral_accel_g[i]
        dynamics_results.append(dynamics)
    
    print(f"   Analyzed {len(dynamics_results)} high-cornering points")
    
    if dynamics_results:
        max_slip_front = max(abs(d['slip_angle_front']) for d in dynamics_results)
        max_slip_rear = max(abs(d['slip_angle_rear']) for d in dynamics_results)
        print(f"   Max front slip angle: {np.rad2deg(max_slip_front):.2f} deg")
        print(f"   Max rear slip angle: {np.rad2deg(max_slip_rear):.2f} deg")
    
    # Create comprehensive results dictionary
    enhanced_results = {
        'standard_results': standard_results,
        'wheel_loads': wheel_loads,
        'suspension_effects': suspension_effects,
        'dynamics_results': dynamics_results,
        'validation': validation,
        'vehicle_config': vehicle_config
    }
    
    return enhanced_results


def plot_phase1_results(results):
    """
    Create comprehensive plots showing Phase 1 physics results.
    
    Parameters:
    -----------
    results : dict
        Results from run_phase1_enhanced_simulation
    """
    print("\n4. Creating Phase 1 physics plots...")
    
    # Extract data
    standard = results['standard_results']
    wheel_loads = results['wheel_loads']
    suspension = results['suspension_effects']
    
    distances = standard['distances']
    velocities = standard['velocities']
    lateral_accel_g = standard['lateral_accel_g']
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle('Phase 1 Enhanced Lap Simulation Results', fontsize=16)
    
    # Plot 1: Individual wheel loads
    ax1 = axes[0, 0]
    ax1.plot(distances, wheel_loads['FL'], label='Front Left', color='blue')
    ax1.plot(distances, wheel_loads['FR'], label='Front Right', color='cyan')
    ax1.plot(distances, wheel_loads['RL'], label='Rear Left', color='red')
    ax1.plot(distances, wheel_loads['RR'], label='Rear Right', color='orange')
    ax1.set_title('Individual Wheel Loads')
    ax1.set_xlabel('Distance (m)')
    ax1.set_ylabel('Load (N)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Load transfer analysis
    ax2 = axes[0, 1]
    front_total = wheel_loads['FL'] + wheel_loads['FR']
    rear_total = wheel_loads['RL'] + wheel_loads['RR']
    left_total = wheel_loads['FL'] + wheel_loads['RL']
    right_total = wheel_loads['FR'] + wheel_loads['RR']
    
    ax2.plot(distances, front_total, label='Front Axle', color='blue')
    ax2.plot(distances, rear_total, label='Rear Axle', color='red')
    ax2.plot(distances, left_total, '--', label='Left Side', color='green')
    ax2.plot(distances, right_total, '--', label='Right Side', color='purple')
    ax2.set_title('Load Distribution by Axle/Side')
    ax2.set_xlabel('Distance (m)')
    ax2.set_ylabel('Load (N)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Suspension roll angles
    ax3 = axes[1, 0]
    ax3.plot(distances, np.rad2deg(suspension['roll_angle_front']), 
             label='Front Roll', color='blue')
    ax3.plot(distances, np.rad2deg(suspension['roll_angle_rear']), 
             label='Rear Roll', color='red')
    ax3.plot(distances, np.rad2deg(suspension['pitch_angle']), 
             label='Pitch', color='green')
    ax3.set_title('Suspension Roll and Pitch Angles')
    ax3.set_xlabel('Distance (m)')
    ax3.set_ylabel('Angle (deg)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Camber changes
    ax4 = axes[1, 1]
    ax4.plot(distances, np.rad2deg(suspension['camber_change_front']), 
             label='Front Camber Change', color='blue')
    ax4.plot(distances, np.rad2deg(suspension['camber_change_rear']), 
             label='Rear Camber Change', color='red')
    ax4.set_title('Dynamic Camber Changes')
    ax4.set_xlabel('Distance (m)')
    ax4.set_ylabel('Camber Change (deg)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Velocity and lateral acceleration
    ax5 = axes[2, 0]
    ax5_twin = ax5.twinx()
    
    line1 = ax5.plot(distances, velocities, color='blue', label='Velocity')
    line2 = ax5_twin.plot(distances, lateral_accel_g, color='red', label='Lateral Accel')
    
    ax5.set_xlabel('Distance (m)')
    ax5.set_ylabel('Velocity (m/s)', color='blue')
    ax5_twin.set_ylabel('Lateral Acceleration (g)', color='red')
    ax5.set_title('Velocity Profile and Lateral Acceleration')
    
    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax5.legend(lines, labels, loc='upper right')
    ax5.grid(True, alpha=0.3)
    
    # Plot 6: Weight distribution analysis
    ax6 = axes[2, 1]
    front_percentage = front_total / (front_total + rear_total) * 100
    left_percentage = left_total / (left_total + right_total) * 100
    
    ax6.plot(distances, front_percentage, label='Front Weight %', color='blue')
    ax6.plot(distances, left_percentage, label='Left Weight %', color='green')
    ax6.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50% Reference')
    ax6.set_title('Dynamic Weight Distribution')
    ax6.set_xlabel('Distance (m)')
    ax6.set_ylabel('Weight Percentage (%)')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    plot_filename = '/Users/Hiro/Documents/Programming/GitHub/Lap-Simulation and Outputs/python/outputs/plots/phase1_enhanced_physics.png'
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"   Saved plot: {plot_filename}")
    
    plt.show()


def compare_with_standard_physics(results):
    """
    Compare Phase 1 enhanced results with standard physics.
    
    Parameters:
    -----------
    results : dict
        Results from run_phase1_enhanced_simulation
    """
    print("\n5. Comparing with standard physics...")
    
    standard = results['standard_results']
    wheel_loads = results['wheel_loads']
    
    # Compare total loads with standard load transfer
    if 'loads' in standard:
        standard_loads = standard['loads']
        
        # Calculate totals from individual wheels
        phase1_front_total = wheel_loads['FL'] + wheel_loads['FR']
        phase1_rear_total = wheel_loads['RL'] + wheel_loads['RR']
        
        # Compare with standard
        if 'front' in standard_loads and 'rear' in standard_loads:
            standard_front_total = standard_loads['front']
            standard_rear_total = standard_loads['rear']
            
            front_diff = np.mean(np.abs(phase1_front_total - standard_front_total))
            rear_diff = np.mean(np.abs(phase1_rear_total - standard_rear_total))
            
            print(f"   Average difference in front loads: {front_diff:.1f} N")
            print(f"   Average difference in rear loads: {rear_diff:.1f} N")
            
            if front_diff < 50 and rear_diff < 50:
                print("   ✓ Phase 1 loads consistent with standard physics")
            else:
                print("   ⚠ Significant differences found - review calculations")
    
    # Performance impact analysis
    total_points = len(standard['velocities'])
    print(f"   Processed {total_points} track points")
    print(f"   Phase 1 adds individual wheel resolution")
    print(f"   Phase 1 adds suspension kinematics")
    print(f"   Phase 1 adds vehicle dynamics analysis")


def create_phase1_summary_report(results):
    """
    Create a summary report of Phase 1 implementation.
    
    Parameters:
    -----------
    results : dict
        Results from run_phase1_enhanced_simulation
    """
    print("\n6. Phase 1 Implementation Summary")
    print("=" * 50)
    
    validation = results['validation']
    suspension = results['suspension_effects']
    dynamics = results['dynamics_results']
    
    print("MATLAB Parameter Verification:")
    config = results['vehicle_config']
    print(f"   LLTD: {config['LLTD']:.2f} (MATLAB: 0.51)")
    print(f"   Front roll gradient: {config['roll_gradient_front']:.2f} deg/g (MATLAB: 1.15)")
    print(f"   Rear roll gradient: {config['roll_gradient_rear']:.2f} deg/g (MATLAB: 1.15)")
    print(f"   Pitch gradient: {config['pitch_gradient']:.2f} deg/g (MATLAB: 0.0)")
    
    print("\nImplemented Features:")
    print("   ✓ Individual wheel load calculations with LLTD")
    print("   ✓ Lateral and longitudinal load transfer")
    print("   ✓ Suspension roll and pitch angles")
    print("   ✓ Dynamic camber changes")
    print("   ✓ Slip angle calculations")
    print("   ✓ Yaw moment balance")
    print("   ✓ Ackermann steering geometry")
    
    print("\nValidation Results:")
    print(f"   Weight conservation: {'PASS' if validation['weight_balance_ok'] else 'FAIL'}")
    print(f"   Max weight error: {validation['max_weight_error']:.3f} N")
    print(f"   Front weight distribution: {validation['front_weight_percentage']:.1f}%")
    
    print("\nSuspension Analysis:")
    max_roll_front = np.rad2deg(np.max(np.abs(suspension['roll_angle_front'])))
    max_roll_rear = np.rad2deg(np.max(np.abs(suspension['roll_angle_rear'])))
    print(f"   Max front roll angle: {max_roll_front:.2f} deg")
    print(f"   Max rear roll angle: {max_roll_rear:.2f} deg")
    
    if dynamics:
        max_slip = max(np.rad2deg(abs(d['slip_angle_front'])) for d in dynamics)
        print(f"   Max slip angle: {max_slip:.2f} deg")
    
    print("\nNext Steps (Phase 2):")
    print("   - Implement full Magic Formula 5.2 tire model")
    print("   - Add individual wheel force calculations")
    print("   - Integrate with combined slip conditions")
    print("   - Add tire temperature effects")
    
    print("\nPhase 1 implementation completed successfully! ✓")


def main():
    """Main demo function."""
    print("Starting Phase 1 Enhanced Lap Simulation Demo")
    print("=" * 60)
    
    # Run enhanced simulation
    results = run_phase1_enhanced_simulation()
    
    # Create plots
    plot_phase1_results(results)
    
    # Compare with standard
    compare_with_standard_physics(results)
    
    # Create summary report
    create_phase1_summary_report(results)


if __name__ == "__main__":
    main()
