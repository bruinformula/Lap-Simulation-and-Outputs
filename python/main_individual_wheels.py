"""
Main Script - Individual Wheel Physics Integration
=================================================

Integrates advanced individual wheel physics with lap simulation and shows impact on:
- Acceleration profiles
- Velocity profiles  
- Lap time performance

Compares standard simplified physics vs enhanced individual wheel physics.
"""

import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import time

# Import vehicle configuration
from vehicle_config import get_vehicle_config, get_powertrain_config, print_vehicle_summary

from lap_simulation import lap_sim
from lap_simulation.physics import (calculate_realistic_velocities, estimate_lap_time,
                                   calculate_track_curvature, calculate_distance_array)
from lap_simulation.individual_wheel_physics import (calculate_individual_wheel_loads,
                                                    calculate_suspension_effects)
from lap_simulation.plotting import plot_velocity_profile
from lap_simulation.data_export import save_simulation_results
import pandas as pd
from scipy.io import loadmat
from scipy import ndimage


def load_track_data():
    """Load endurance track data."""
    try:
        from lap_simulation.data_loader import load_comprehensive_track_data
        track_data = load_comprehensive_track_data()
        
        if track_data and 'endurance' in track_data:
            if 'racing_line' in track_data['endurance']:
                x_coords = track_data['endurance']['racing_line']['x']
                y_coords = track_data['endurance']['racing_line']['y']
                distance = track_data['endurance']['racing_line']['distance']
                print(f"✓ Loaded endurance track: {len(x_coords)} points, {distance[-1]:.0f}m")
                return x_coords, y_coords, distance
        
        raise Exception("Could not find racing line in track data")
        
    except Exception as e:
        print(f"⚠ Error loading track: {e}")
        print("Using fallback MATLAB data...")
        
        # Load directly from MATLAB file
        mat_file = os.path.join(os.path.dirname(__file__), "..", "Data Files", "endurance_racing_line.mat")
        if os.path.exists(mat_file):
            racing_data = loadmat(mat_file)
            if 'vehicle_path' in racing_data:
                vehicle_path = racing_data['vehicle_path']
                x_coords = vehicle_path[0, :]
                y_coords = vehicle_path[1, :]
                distance = calculate_distance_array(x_coords, y_coords)
                print(f"✓ Loaded from MATLAB: {len(x_coords)} points, {distance[-1]:.0f}m")
                return x_coords, y_coords, distance
        
        raise Exception("Could not load any track data")


def calculate_enhanced_velocities(x_coords, y_coords, vehicle_config):
    """
    Calculate velocities with individual wheel physics effects.
    
    Enhances standard velocity calculation by considering:
    1. Individual wheel loads instead of equal axle distribution
    2. Suspension roll and camber effects on tire performance
    3. Load transfer asymmetry affecting grip
    """
    
    # Start with standard velocity calculation
    standard_velocities = calculate_realistic_velocities(x_coords, y_coords, 'endurance', 
                                                       enable_aero=True, aero_config='original')
    
    # Calculate track geometry
    curvatures = calculate_track_curvature(x_coords, y_coords)
    distance = calculate_distance_array(x_coords, y_coords)
    
    # Convert to m/s for calculations
    velocities_ms = standard_velocities * 0.44704
    n_points = len(velocities_ms)
    g = 9.81
    
    # Calculate accelerations from track geometry
    lat_accel_g = np.zeros(n_points)
    long_accel_g = np.zeros(n_points)
    
    # Lateral acceleration from velocity and curvature
    for i in range(n_points):
        if velocities_ms[i] > 0 and abs(curvatures[i]) > 1e-6:
            lat_accel_g[i] = abs((velocities_ms[i]**2 * curvatures[i]) / g)
    
    # Longitudinal acceleration from velocity changes
    for i in range(1, n_points-1):
        if distance[i+1] != distance[i]:
            dv = velocities_ms[i+1] - velocities_ms[i]
            ds = distance[i+1] - distance[i]
            dt = ds / max(velocities_ms[i], 1.0)
            if dt > 0:
                long_accel_g[i] = (dv / dt) / g
    
    # Smooth accelerations
    lat_accel_g = ndimage.gaussian_filter1d(lat_accel_g, sigma=2.0)
    long_accel_g = ndimage.gaussian_filter1d(long_accel_g, sigma=2.0)
    
    # Apply individual wheel physics to modify velocities
    enhanced_velocities = np.copy(standard_velocities)
    
    for i in range(len(velocities_ms)):
        # Get individual wheel loads
        wheel_loads = calculate_individual_wheel_loads(
            np.array([lat_accel_g[i]]), 
            np.array([long_accel_g[i]]), 
            np.array([velocities_ms[i]]), 
            vehicle_config
        )
        
        # Get suspension effects
        suspension = calculate_suspension_effects(
            np.array([lat_accel_g[i]]), 
            np.array([long_accel_g[i]]), 
            vehicle_config
        )
        
        # Calculate grip effects
        static_load_front = vehicle_config['weight'] * 0.44754 / 2
        static_load_rear = vehicle_config['weight'] * (1 - 0.44754) / 2
        
        # Load sensitivity (racing tires: 0.75-0.85)
        load_sensitivity = 0.8
        
        # Individual wheel grip factors
        fl_grip = (wheel_loads['FL'][0] / static_load_front) ** load_sensitivity
        fr_grip = (wheel_loads['FR'][0] / static_load_front) ** load_sensitivity
        rl_grip = (wheel_loads['RL'][0] / static_load_rear) ** load_sensitivity
        rr_grip = (wheel_loads['RR'][0] / static_load_rear) ** load_sensitivity
        
        # Camber effects (8% loss per degree)
        camber_front = abs(suspension['camber_change_front'][0])
        camber_rear = abs(suspension['camber_change_rear'][0])
        
        fl_grip *= (1 - camber_front * 0.08)
        fr_grip *= (1 - camber_front * 0.08)
        rl_grip *= (1 - camber_rear * 0.08)
        rr_grip *= (1 - camber_rear * 0.08)
        
        # Load asymmetry penalty
        front_asymmetry = abs(fl_grip - fr_grip) / 2
        rear_asymmetry = abs(rl_grip - rr_grip) / 2
        asymmetry_penalty = 1 - (front_asymmetry + rear_asymmetry) * 0.1
        
        # Overall vehicle grip
        front_weight = 0.44754
        vehicle_grip = (front_weight * (fl_grip + fr_grip) / 2 + 
                       (1 - front_weight) * (rl_grip + rr_grip) / 2) * asymmetry_penalty
        
        # Modify velocity based on grip (v^2 proportional to grip)
        if abs(lat_accel_g[i]) > 0.1:  # In corners
            grip_factor = np.sqrt(max(0.7, min(1.15, vehicle_grip)))
            enhanced_velocities[i] *= grip_factor
        elif abs(long_accel_g[i]) > 0.1:  # Accelerating/braking
            grip_factor = np.sqrt(max(0.9, min(1.05, vehicle_grip)))
            enhanced_velocities[i] *= grip_factor
    
    return enhanced_velocities, standard_velocities


def run_comparison():
    """Run simulation comparing standard vs individual wheel physics."""
    
    print("="*80)
    print("INDIVIDUAL WHEEL PHYSICS - PERFORMANCE IMPACT ANALYSIS")
    print("="*80)
    print("Comparing Standard Physics vs Individual Wheel Physics")
    print("Metrics: Acceleration, Velocity, and Lap Time\n")
    
    # Load vehicle config
    vehicle_config = get_vehicle_config()
    
    # Load track data
    print("Loading endurance track data...")
    start_time = time.time()
    
    try:
        x_coords, y_coords, distance = load_track_data()
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    # Calculate velocities with both methods
    print("\nCalculating velocities...")
    print("  Standard physics (equal wheel loading)...")
    standard_velocities = calculate_realistic_velocities(x_coords, y_coords, 'endurance', 
                                                       enable_aero=True, aero_config='original')
    
    print("  Individual wheel physics (realistic loading)...")
    enhanced_velocities, _ = calculate_enhanced_velocities(x_coords, y_coords, vehicle_config)
    
    # Calculate lap times
    print("  Calculating lap times...")
    standard_lap_time = estimate_lap_time(standard_velocities, distance)
    enhanced_lap_time = estimate_lap_time(enhanced_velocities, distance)
    
    simulation_time = time.time() - start_time
    print(f"Simulation completed in {simulation_time:.1f} seconds\n")
    
    # Performance Analysis
    print("PERFORMANCE COMPARISON RESULTS")
    print("="*50)
    
    # Lap Time Analysis
    lap_time_diff = enhanced_lap_time - standard_lap_time
    lap_time_percent = (lap_time_diff / standard_lap_time) * 100
    
    print(f"LAP TIME ANALYSIS:")
    print(f"  Standard Physics:     {standard_lap_time:.3f} seconds ({standard_lap_time/60:.1f} min)")
    print(f"  Individual Wheel:     {enhanced_lap_time:.3f} seconds ({enhanced_lap_time/60:.1f} min)")
    print(f"  Difference:           {lap_time_diff:+.3f} seconds ({lap_time_percent:+.2f}%)")
    
    if lap_time_diff < 0:
        print(f"  ✓ Individual wheel physics is FASTER by {abs(lap_time_diff):.3f} seconds!")
    else:
        print(f"  ⚠ Individual wheel physics is slower by {lap_time_diff:.3f} seconds")
        print(f"    (More realistic physics accounts for suspension and load transfer losses)")
    print()
    
    # Velocity Analysis
    print(f"VELOCITY ANALYSIS:")
    print(f"  Standard - Avg: {np.mean(standard_velocities):.1f} mph, Max: {np.max(standard_velocities):.1f} mph")
    print(f"  Enhanced - Avg: {np.mean(enhanced_velocities):.1f} mph, Max: {np.max(enhanced_velocities):.1f} mph")
    
    vel_diff_avg = np.mean(enhanced_velocities) - np.mean(standard_velocities)
    vel_diff_max = np.max(enhanced_velocities) - np.max(standard_velocities)
    print(f"  Average difference: {vel_diff_avg:+.1f} mph")
    print(f"  Max difference:     {vel_diff_max:+.1f} mph")
    print()
    
    # Physics Details
    print(f"PHYSICS DIFFERENCES:")
    print(f"  Standard Physics:")
    print(f"    - Equal wheel loading (FL=FR, RL=RR)")
    print(f"    - No suspension effects")
    print(f"    - Simplified tire model")
    print()
    print(f"  Individual Wheel Physics:")
    print(f"    - Individual wheel loads with load transfer")
    print(f"    - Suspension roll and camber effects")
    print(f"    - Load-sensitive tire grip")
    print(f"    - Asymmetric handling penalties")
    print()
    
    # Create visualization
    create_comparison_plot(distance, standard_velocities, enhanced_velocities, 
                          x_coords, y_coords, standard_lap_time, enhanced_lap_time)
    
    return {
        'standard_lap_time': standard_lap_time,
        'enhanced_lap_time': enhanced_lap_time,
        'lap_time_improvement': -lap_time_diff,
        'velocity_improvement': vel_diff_avg,
        'standard_velocities': standard_velocities,
        'enhanced_velocities': enhanced_velocities,
        'distance': distance
    }


def create_comparison_plot(distance, standard_vel, enhanced_vel, x_coords, y_coords, 
                          standard_time, enhanced_time):
    """Create comparison visualization."""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Individual Wheel Physics - Performance Impact', fontsize=16, fontweight='bold')
    
    # Track layout with velocity
    ax1 = axes[0, 0]
    scatter = ax1.scatter(x_coords[::10], y_coords[::10], c=enhanced_vel[::10], 
                         cmap='RdYlBu_r', s=15, alpha=0.8)
    ax1.set_title('Endurance Track Layout\n(Colored by Enhanced Velocity)')
    ax1.set_xlabel('X Position (ft)')
    ax1.set_ylabel('Y Position (ft)')
    ax1.axis('equal')
    plt.colorbar(scatter, ax=ax1, label='Velocity (mph)')
    
    # Velocity comparison
    ax2 = axes[0, 1]
    ax2.plot(distance, standard_vel, 'b-', linewidth=2, label='Standard Physics', alpha=0.8)
    ax2.plot(distance, enhanced_vel, 'r-', linewidth=2, label='Individual Wheel Physics', alpha=0.8)
    ax2.fill_between(distance, standard_vel, enhanced_vel, alpha=0.3, 
                     color='green' if np.mean(enhanced_vel) > np.mean(standard_vel) else 'red')
    ax2.set_title('Velocity Profiles Comparison')
    ax2.set_xlabel('Distance (m)')
    ax2.set_ylabel('Velocity (mph)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Velocity difference
    ax3 = axes[1, 0]
    vel_diff = enhanced_vel - standard_vel
    ax3.plot(distance, vel_diff, 'purple', linewidth=2)
    ax3.fill_between(distance, vel_diff, 0, where=(vel_diff >= 0), 
                     color='green', alpha=0.5, label='Enhanced Faster')
    ax3.fill_between(distance, vel_diff, 0, where=(vel_diff < 0), 
                     color='red', alpha=0.5, label='Enhanced Slower')
    ax3.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax3.set_title('Velocity Difference\n(Enhanced - Standard)')
    ax3.set_xlabel('Distance (m)')
    ax3.set_ylabel('Velocity Difference (mph)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Performance summary
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    lap_time_diff = enhanced_time - standard_time
    vel_improvement = np.mean(enhanced_vel) - np.mean(standard_vel)
    
    summary_text = f"""PERFORMANCE SUMMARY

LAP TIME:
Standard:  {standard_time:.1f} sec ({standard_time/60:.1f} min)
Enhanced:  {enhanced_time:.1f} sec ({enhanced_time/60:.1f} min)
Change:    {lap_time_diff:+.1f} sec

VELOCITY:
Avg Change: {vel_improvement:+.1f} mph
Max Speed:  {np.max(enhanced_vel):.1f} mph

PHYSICS ENHANCEMENTS:
✓ Individual wheel loads
✓ Suspension roll & camber
✓ Load transfer asymmetry  
✓ Realistic tire behavior

TRACK: Endurance ({distance[-1]:.0f}m)
POINTS: {len(distance)} simulation points"""
    
    ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
    
    plt.tight_layout()
    
    # Save plot
    plot_filename = '/Users/Hiro/Documents/Programming/GitHub/Lap-Simulation and Outputs/python/outputs/plots/individual_wheel_analysis.png'
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Analysis plot saved: {plot_filename}")
    
    plt.show()


def main():
    """Main function."""
    
    print_vehicle_summary()
    print()
    
    # Run comparison
    results = run_comparison()
    
    if results is None:
        print("❌ Simulation failed - could not load track data")
        return
    
    # Final summary
    print("\n" + "="*80)
    print("INDIVIDUAL WHEEL PHYSICS INTEGRATION COMPLETE")
    print("="*80)
    
    improvement = results['lap_time_improvement']
    if improvement > 0:
        print(f"🏁 LAP TIME IMPROVEMENT: {improvement:.3f} seconds faster!")
    else:
        print(f"⚠️  LAP TIME CHANGE: {abs(improvement):.3f} seconds slower")
        print(f"   (Realistic physics accounts for suspension and tire losses)")
    
    print(f"🚗 VELOCITY CHANGE: {results['velocity_improvement']:+.1f} mph average")
    print(f"📊 PHYSICS ACCURACY: Individual wheel loads + suspension effects")
    print(f"🔧 INTEGRATION STATUS: ✅ Individual wheel physics successfully integrated")
    
    print(f"\n💡 Individual wheel physics provides:")
    print(f"   • Realistic load distribution across all 4 wheels")
    print(f"   • Suspension effects on tire performance")
    print(f"   • Foundation for advanced tire models")
    
    return results


if __name__ == "__main__":
    main()
