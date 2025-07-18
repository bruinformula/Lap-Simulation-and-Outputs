"""
Individual Wheel Physics Demonstration
=====================================

Clear demonstration of what individual wheel physics adds to lap simulation.
Shows specific differences between standard and advanced physics approaches.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lap_simulation.individual_wheel_physics import (
    calculate_individual_wheel_loads,
    calculate_suspension_effects
)
from vehicle_config import get_vehicle_config


def individual_wheel_demo():
    """Demonstration of individual wheel physics vs standard physics."""
    print("INDIVIDUAL WHEEL PHYSICS DEMONSTRATION")
    print("=" * 50)
    print("This shows EXACTLY what individual wheel physics adds with test cases.\n")
    
    # Get vehicle config
    vehicle_config = get_vehicle_config()
    
    # Test Case 1: Pure lateral acceleration (cornering)
    print("TEST CASE 1: Pure Cornering (1.5g lateral acceleration)")
    print("-" * 50)
    
    # Simple test data
    n_points = 1
    lateral_accel_g = np.array([1.5])  # 1.5g cornering
    longitudinal_accel_g = np.array([0.0])  # No braking/acceleration
    velocities = np.array([20.0])  # 20 m/s constant speed
    
    # Calculate individual wheel loads
    wheel_loads = calculate_individual_wheel_loads(
        lateral_accel_g, longitudinal_accel_g, velocities, vehicle_config
    )
    
    # Standard physics assumption: equal load on left/right wheels
    total_weight = vehicle_config['weight']
    static_front_per_wheel = total_weight * 0.44754 / 2  # MATLAB WDF = 44.754%
    static_rear_per_wheel = total_weight * (1 - 0.44754) / 2
    
    print(f"Vehicle weight: {total_weight:.0f} N")
    print(f"Static load per wheel: FL={static_front_per_wheel:.0f}N, FR={static_front_per_wheel:.0f}N, RL={static_rear_per_wheel:.0f}N, RR={static_rear_per_wheel:.0f}N")
    print()
    
    print("STANDARD PHYSICS ASSUMPTION:")
    print("  - All wheels equally loaded during cornering")
    print("  - No left-right load transfer information")
    print("  - FL = FR, RL = RR always")
    print()
    
    print("INDIVIDUAL WHEEL PHYSICS:")
    FL = wheel_loads['FL'][0]
    FR = wheel_loads['FR'][0]
    RL = wheel_loads['RL'][0]
    RR = wheel_loads['RR'][0]
    
    print(f"  Front Left:  {FL:.0f} N")
    print(f"  Front Right: {FR:.0f} N")
    print(f"  Rear Left:   {RL:.0f} N")
    print(f"  Rear Right:  {RR:.0f} N")
    print()
    
    # Show the differences
    front_diff = abs(FR - FL)
    rear_diff = abs(RR - RL)
    
    print("LOAD TRANSFER ANALYSIS:")
    print(f"  Front axle left-right difference: {front_diff:.0f} N")
    print(f"  Rear axle left-right difference:  {rear_diff:.0f} N")
    print(f"  Right side total: {FR + RR:.0f} N")
    print(f"  Left side total:  {FL + RL:.0f} N")
    print(f"  Total load transfer: {abs((FR + RR) - (FL + RL)):.0f} N")
    print()
    
    print("WHY THIS MATTERS:")
    print("  - Right wheels have more load → more grip available")
    print("  - Left wheels have less load → less grip available")  
    print("  - Standard physics cannot predict this asymmetry")
    print("  - Critical for tire performance and vehicle balance")
    print()
    
    # Test Case 2: Suspension effects
    print("TEST CASE 2: Suspension Kinematics")
    print("-" * 50)
    
    suspension_effects = calculate_suspension_effects(
        lateral_accel_g, longitudinal_accel_g, vehicle_config
    )
    
    roll_angle_deg = np.rad2deg(suspension_effects['roll_angle_front'][0])
    camber_change_deg = np.rad2deg(suspension_effects['camber_change_front'][0])
    
    print("STANDARD PHYSICS:")
    print("  - No suspension effects")
    print("  - Roll angle: 0°")
    print("  - Camber change: 0°")
    print()
    
    print("INDIVIDUAL WHEEL SUSPENSION EFFECTS:")
    print(f"  - Roll angle: {roll_angle_deg:.2f}°")
    print(f"  - Camber change: {camber_change_deg:.2f}°")
    print(f"  - Uses MATLAB roll gradient: {vehicle_config['roll_gradient_front']:.2f} deg/g")
    print()
    
    print("IMPACT ON TIRE PERFORMANCE:")
    print(f"  - Camber reduces tire grip by ~5% per degree")
    print(f"  - Estimated grip loss: {camber_change_deg * 5:.1f}%")
    print(f"  - Standard physics misses this effect completely")
    print()
    
    # Test Case 3: Show weight distribution effects
    print("TEST CASE 3: Weight Distribution Impact")
    print("-" * 50)
    
    # Create a range of lateral accelerations
    lat_accel_range = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
    long_accel_range = np.zeros_like(lat_accel_range)
    vel_range = np.ones_like(lat_accel_range) * 20.0
    
    print("Lateral Acc (g) | FL (N) | FR (N) | RL (N) | RR (N) | L-R Diff (N)")
    print("-" * 65)
    
    for i, lat_g in enumerate(lat_accel_range):
        loads = calculate_individual_wheel_loads(
            np.array([lat_g]), long_accel_range[i:i+1], vel_range[i:i+1], vehicle_config
        )
        
        FL = loads['FL'][0]
        FR = loads['FR'][0] 
        RL = loads['RL'][0]
        RR = loads['RR'][0]
        
        lr_diff = abs((FR + RR) - (FL + RL))
        
        print(f"    {lat_g:4.1f}      | {FL:4.0f}  | {FR:4.0f}  | {RL:4.0f}  | {RR:4.0f}  |    {lr_diff:4.0f}")
    
    print()
    print("OBSERVATIONS:")
    print("  - Higher lateral acceleration → more load transfer")
    print("  - Load transfer affects all wheels differently")
    print("  - LLTD determines front/rear distribution")
    print("  - Standard physics would show 0 N difference for all cases")
    print()
    
    return {
        'wheel_loads': wheel_loads,
        'suspension_effects': suspension_effects,
        'vehicle_config': vehicle_config
    }


def create_visual_comparison():
    """Create a visual comparison of standard vs Phase 1."""
    print("CREATING VISUAL COMPARISON")
    print("-" * 30)
    
    vehicle_config = get_vehicle_config()
    
    # Create a range of cornering scenarios
    lateral_g_range = np.linspace(0, 2.0, 21)  # 0 to 2g
    long_g_range = np.zeros_like(lateral_g_range)
    velocities = np.ones_like(lateral_g_range) * 20.0
    
    # Calculate Phase 1 loads
    wheel_loads = calculate_individual_wheel_loads(
        lateral_g_range, long_g_range, velocities, vehicle_config
    )
    
    # Calculate standard assumption (equal left/right)
    total_weight = vehicle_config['weight']
    weight_dist_front = 0.44754  # MATLAB WDF
    
    static_front_per_wheel = total_weight * weight_dist_front / 2
    static_rear_per_wheel = total_weight * (1 - weight_dist_front) / 2
    
    # Standard physics: wheels stay at static loads (no lateral load transfer)
    standard_FL = np.ones_like(lateral_g_range) * static_front_per_wheel
    standard_FR = np.ones_like(lateral_g_range) * static_front_per_wheel
    standard_RL = np.ones_like(lateral_g_range) * static_rear_per_wheel
    standard_RR = np.ones_like(lateral_g_range) * static_rear_per_wheel
    
    # Create comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Individual Wheel Physics vs Standard Physics', fontsize=16)
    
    # Plot 1: Individual wheel loads
    ax1 = axes[0, 0]
    ax1.plot(lateral_g_range, wheel_loads['FL'], 'b-', linewidth=2, label='Individual FL')
    ax1.plot(lateral_g_range, wheel_loads['FR'], 'c-', linewidth=2, label='Individual FR')
    ax1.plot(lateral_g_range, wheel_loads['RL'], 'r-', linewidth=2, label='Individual RL')
    ax1.plot(lateral_g_range, wheel_loads['RR'], 'orange', linewidth=2, label='Individual RR')
    
    ax1.plot(lateral_g_range, standard_FL, 'b--', alpha=0.7, label='Standard FL=FR')
    ax1.plot(lateral_g_range, standard_RL, 'r--', alpha=0.7, label='Standard RL=RR')
    
    ax1.set_title('Individual Wheel Loads')
    ax1.set_xlabel('Lateral Acceleration (g)')
    ax1.set_ylabel('Wheel Load (N)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Load differences
    ax2 = axes[0, 1]
    front_diff = wheel_loads['FR'] - wheel_loads['FL']
    rear_diff = wheel_loads['RR'] - wheel_loads['RL']
    
    ax2.plot(lateral_g_range, front_diff, 'b-', linewidth=2, label='Front: FR - FL')
    ax2.plot(lateral_g_range, rear_diff, 'r-', linewidth=2, label='Rear: RR - RL')
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='Standard (always 0)')
    
    ax2.fill_between(lateral_g_range, front_diff, 0, alpha=0.3, color='blue')
    ax2.fill_between(lateral_g_range, rear_diff, 0, alpha=0.3, color='red')
    
    ax2.set_title('Left-Right Load Differences\n(Standard Physics = 0)')
    ax2.set_xlabel('Lateral Acceleration (g)')
    ax2.set_ylabel('Load Difference (N)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Suspension effects
    ax3 = axes[1, 0]
    suspension = calculate_suspension_effects(lateral_g_range, long_g_range, vehicle_config)
    
    roll_angle_deg = np.rad2deg(suspension['roll_angle_front'])
    camber_change_deg = np.rad2deg(suspension['camber_change_front'])
    
    ax3.plot(lateral_g_range, roll_angle_deg, 'g-', linewidth=2, label='Roll Angle')
    ax3.plot(lateral_g_range, camber_change_deg, 'm-', linewidth=2, label='Camber Change')
    ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='Standard (always 0°)')
    
    ax3.set_title('Suspension Effects\n(Standard Physics = 0°)')
    ax3.set_xlabel('Lateral Acceleration (g)')
    ax3.set_ylabel('Angle (degrees)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Tire performance impact
    ax4 = axes[1, 1]
    
    # Calculate tire performance impact
    grip_loss_percent = camber_change_deg * 5  # 5% loss per degree of camber
    load_effect_FL = (wheel_loads['FL'] / static_front_per_wheel - 1) * 100  # % change from static
    load_effect_FR = (wheel_loads['FR'] / static_front_per_wheel - 1) * 100
    
    ax4.plot(lateral_g_range, grip_loss_percent, 'purple', linewidth=2, label='Camber Grip Loss (%)')
    ax4.plot(lateral_g_range, load_effect_FL, 'b-', linewidth=2, label='FL Load Effect (%)')
    ax4.plot(lateral_g_range, load_effect_FR, 'c-', linewidth=2, label='FR Load Effect (%)')
    ax4.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='Standard (no effects)')
    
    ax4.set_title('Tire Performance Effects\n(Standard Physics = 0% change)')
    ax4.set_xlabel('Lateral Acceleration (g)')
    ax4.set_ylabel('Performance Change (%)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    plot_filename = '/Users/Hiro/Documents/Programming/GitHub/Lap-Simulation and Outputs/python/outputs/plots/individual_wheel_comparison.png'
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Saved visual comparison: {plot_filename}")
    
    plt.show()


def main():
    """Main function."""
    # Run demonstration
    demo_results = individual_wheel_demo()
    
    # Create visual comparison
    create_visual_comparison()
    
    print("=" * 60)
    print("CONCLUSION: Individual wheel physics adds critical missing capabilities")
    print("=" * 60)
    print("✓ Individual wheel loads instead of axle totals")
    print("✓ Left-right load transfer during cornering")  
    print("✓ Suspension roll and camber effects")
    print("✓ Foundation for advanced tire models")
    print("✓ Realistic vehicle dynamics analysis")
    print("\nThese effects are essential for accurate lap simulation!")


if __name__ == "__main__":
    main()
