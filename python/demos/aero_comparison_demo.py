#!/usr/bin/env python3
"""
Aerodynamics Comparison Demo
===========================

This demo runs lap simulations with and without aerodynamics to show the impact
of aerodynamic forces on lap performance.

Compares:
- Velocity profiles with/without aero
- Lap times with/without aero
- Corner speeds with/without aero
- Straight-line speeds with/without aero

Usage:
    python aero_comparison_demo.py
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lap_simulation.data_loader import load_racing_line_data
from lap_simulation.physics import calculate_realistic_velocities, estimate_lap_time, calculate_cumulative_distance
from vehicle_config import get_vehicle_config
import matplotlib.patches as patches


def load_track_data(track_type):
    """
    Load track data for the specified track type.
    
    Parameters:
    -----------
    track_type : str
        'autocross' or 'endurance'
        
    Returns:
    --------
    dict
        Track data with coordinates
    """
    # Get the correct path to Data Files directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))  # Go up to project root
    data_dir = os.path.join(base_dir, "Data Files")
    
    print(f"Looking for data in: {data_dir}")
    
    # Load racing line data
    racing_data = load_racing_line_data(data_dir, track_type)
    
    # Extract coordinates from the racing line data
    # Look for vehicle_path which seems to contain the actual track coordinates
    if 'vehicle_path' in racing_data:
        coords = racing_data['vehicle_path']
        if coords.shape[0] == 2:  # 2 rows, many columns
            x_coords = coords[0, :]  # First row is X
            y_coords = coords[1, :]  # Second row is Y
        else:
            x_coords = coords[:, 0]  # First column is X
            y_coords = coords[:, 1]  # Second column is Y
        print(f"Using 'vehicle_path' for coordinates, shape: {coords.shape}")
    else:
        # Fallback to other possible coordinate arrays
        coord_keys = ['path_points', 'pp_in', 'pp_out']
        for key in coord_keys:
            if key in racing_data and isinstance(racing_data[key], np.ndarray):
                if key == 'path_points':
                    coords = racing_data[key]
                    x_coords = coords[:, 0]
                    y_coords = coords[:, 1]
                    print(f"Using '{key}' for coordinates, shape: {coords.shape}")
                    break
        else:
            raise ValueError(f"Could not find suitable racing line coordinates in {track_type} data")
    
    print(f"Loaded {len(x_coords)} coordinate points for {track_type}")
    print(f"X range: [{np.min(x_coords):.1f}, {np.max(x_coords):.1f}]")
    print(f"Y range: [{np.min(y_coords):.1f}, {np.max(y_coords):.1f}]")
    
    return {
        'track_type': track_type,
        'x_coords': x_coords,
        'y_coords': y_coords
    }


def run_simple_simulation(track_type, enable_aero=True, aero_config=None):
    """
    Run a simplified lap simulation for aerodynamics comparison.
    
    Parameters:
    -----------
    track_type : str
        'autocross' or 'endurance'
    enable_aero : bool
        Whether to enable aerodynamics
    aero_config : str, optional
        Aerodynamics configuration ('original', 'realistic', 'high_downforce')
        
    Returns:
    --------
    dict
        Simulation results
    """
    # Load track data
    track_data = load_track_data(track_type)
    x_coords = track_data['x_coords']
    y_coords = track_data['y_coords']
    
    # Calculate velocities with/without aero
    velocities = calculate_realistic_velocities(x_coords, y_coords, track_type, 
                                               enable_aero=enable_aero, aero_config=aero_config)
    
    # Calculate distances
    distances = calculate_cumulative_distance(x_coords, y_coords)
    
    return {
        'track_type': track_type,
        'x_coords': x_coords,
        'y_coords': y_coords,
        'velocities': velocities,
        'distances': distances,
        'aero_enabled': enable_aero,
        'aero_config': aero_config
    }


def run_aero_comparison(track_type='autocross', save_plots=True, aero_config=None):
    """
    Run lap simulation comparison with and without aerodynamics.
    
    Parameters:
    -----------
    track_type : str
        'autocross' or 'endurance'
    save_plots : bool
        Whether to save plots to outputs/plots/
    aero_config : str, optional
        Aerodynamics configuration ('original', 'realistic', 'high_downforce')
        
    Returns:
    --------
    dict
        Comparison results and statistics
    """
    print(f"\n{'='*60}")
    config_name = aero_config if aero_config else "default"
    print(f"AERODYNAMICS IMPACT ANALYSIS - {track_type.upper()} ({config_name.upper()})")
    print(f"{'='*60}")
    
    # Run simulation with aerodynamics
    print("\n1. Running simulation WITH aerodynamics...")
    results_with_aero = run_simple_simulation(track_type, enable_aero=True, aero_config=aero_config)
    
    # Run simulation without aerodynamics
    print("2. Running simulation WITHOUT aerodynamics...")
    results_without_aero = run_simple_simulation(track_type, enable_aero=False, aero_config=aero_config)
    
    # Calculate performance differences
    comparison = analyze_performance_difference(
        results_with_aero, results_without_aero, track_type
    )
    comparison['aero_config'] = aero_config
    
    # Create comparison plots
    if save_plots:
        create_comparison_plots(
            results_with_aero, results_without_aero, comparison, track_type
        )
    
    # Print summary
    print_comparison_summary(comparison)
    
    return comparison


def analyze_performance_difference(results_with, results_without, track_type):
    """
    Analyze the performance differences between aero and no-aero simulations.
    
    Parameters:
    -----------
    results_with, results_without : dict
        Simulation results with and without aerodynamics
    track_type : str
        Track type for analysis
        
    Returns:
    --------
    dict
        Detailed comparison analysis
    """
    # Extract data
    vel_with = results_with['velocities']
    vel_without = results_without['velocities']
    
    # Calculate lap times
    time_with = estimate_lap_time(
        results_with['distances'], vel_with
    )
    time_without = estimate_lap_time(
        results_without['distances'], vel_without
    )
    
    # Find corners (low speed sections) and straights (high speed sections)
    speed_threshold = np.percentile(vel_with, 70)  # Top 30% of speeds = straights
    corner_mask = vel_with < speed_threshold
    straight_mask = vel_with >= speed_threshold
    
    # Calculate statistics
    comparison = {
        'track_type': track_type,
        
        # Lap times
        'lap_time_with_aero': time_with,
        'lap_time_without_aero': time_without,
        'lap_time_difference': time_without - time_with,
        'lap_time_improvement_pct': ((time_without - time_with) / time_without) * 100,
        
        # Overall speeds
        'avg_speed_with_aero': np.mean(vel_with),
        'avg_speed_without_aero': np.mean(vel_without),
        'max_speed_with_aero': np.max(vel_with),
        'max_speed_without_aero': np.max(vel_without),
        
        # Corner performance
        'avg_corner_speed_with_aero': np.mean(vel_with[corner_mask]) if np.any(corner_mask) else 0,
        'avg_corner_speed_without_aero': np.mean(vel_without[corner_mask]) if np.any(corner_mask) else 0,
        
        # Straight performance
        'avg_straight_speed_with_aero': np.mean(vel_with[straight_mask]) if np.any(straight_mask) else 0,
        'avg_straight_speed_without_aero': np.mean(vel_without[straight_mask]) if np.any(straight_mask) else 0,
        
        # Speed differences
        'velocity_differences': vel_with - vel_without,
        'max_speed_gain': np.max(vel_with - vel_without),
        'max_speed_loss': np.min(vel_with - vel_without),
        
        # Raw data for plotting
        'velocities_with': vel_with,
        'velocities_without': vel_without,
        'x_coords': results_with['x_coords'],
        'y_coords': results_with['y_coords'],
        'corner_mask': corner_mask,
        'straight_mask': straight_mask
    }
    
    return comparison


def create_comparison_plots(results_with, results_without, comparison, track_type):
    """
    Create comprehensive comparison plots.
    
    Parameters:
    -----------
    results_with, results_without : dict
        Simulation results
    comparison : dict
        Comparison analysis
    track_type : str
        Track type
    """
    # Set up the figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Track layout with velocity comparison
    ax1 = plt.subplot(2, 3, 1)
    create_track_velocity_plot(ax1, comparison, track_type)
    
    # 2. Velocity profile comparison
    ax2 = plt.subplot(2, 3, 2)
    create_velocity_profile_plot(ax2, comparison)
    
    # 3. Speed difference along track
    ax3 = plt.subplot(2, 3, 3)
    create_speed_difference_plot(ax3, comparison)
    
    # 4. Corner vs straight performance
    ax4 = plt.subplot(2, 3, 4)
    create_corner_straight_comparison(ax4, comparison)
    
    # 5. Speed distribution histograms
    ax5 = plt.subplot(2, 3, 5)
    create_speed_distribution_plot(ax5, comparison)
    
    # 6. Performance summary
    ax6 = plt.subplot(2, 3, 6)
    create_performance_summary_plot(ax6, comparison)
    
    plt.tight_layout()
    
    # Save the plot
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f'{track_type}_aero_comparison.png'
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\nComparison plots saved to: {filepath}")
    
    plt.show()


def create_track_velocity_plot(ax, comparison, track_type):
    """Create track layout colored by velocity difference."""
    x_coords = comparison['x_coords']
    y_coords = comparison['y_coords']
    vel_diff = comparison['velocity_differences']
    
    # Create scatter plot colored by velocity difference
    scatter = ax.scatter(x_coords, y_coords, c=vel_diff, cmap='RdYlBu', 
                        s=20, alpha=0.8)
    
    ax.set_aspect('equal')
    ax.set_title(f'{track_type.title()} Track - Velocity Difference\n(Red = Aero Faster, Blue = No-Aero Faster)')
    ax.set_xlabel('X Position (ft)')
    ax.set_ylabel('Y Position (ft)')
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)
    cbar.set_label('Velocity Difference (mph)\n(With Aero - Without Aero)')


def create_velocity_profile_plot(ax, comparison):
    """Create velocity profile comparison."""
    n_points = len(comparison['velocities_with'])
    distance = np.linspace(0, 100, n_points)  # Normalize to 0-100% of lap
    
    ax.plot(distance, comparison['velocities_with'], 'b-', linewidth=2, 
            label='With Aerodynamics', alpha=0.8)
    ax.plot(distance, comparison['velocities_without'], 'r--', linewidth=2, 
            label='Without Aerodynamics', alpha=0.8)
    
    ax.set_title('Velocity Profile Comparison')
    ax.set_xlabel('Track Progress (%)')
    ax.set_ylabel('Velocity (mph)')
    ax.legend()
    ax.grid(True, alpha=0.3)


def create_speed_difference_plot(ax, comparison):
    """Create speed difference plot along the track."""
    n_points = len(comparison['velocity_differences'])
    distance = np.linspace(0, 100, n_points)
    
    vel_diff = comparison['velocity_differences']
    colors = ['red' if diff < 0 else 'blue' for diff in vel_diff]
    
    ax.bar(distance, vel_diff, width=100/n_points, color=colors, alpha=0.7)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    
    ax.set_title('Speed Difference Along Track')
    ax.set_xlabel('Track Progress (%)')
    ax.set_ylabel('Speed Difference (mph)\n(Positive = Aero Faster)')
    ax.grid(True, alpha=0.3)


def create_corner_straight_comparison(ax, comparison):
    """Create corner vs straight performance comparison."""
    categories = ['Corners', 'Straights']
    
    with_aero = [
        comparison['avg_corner_speed_with_aero'],
        comparison['avg_straight_speed_with_aero']
    ]
    without_aero = [
        comparison['avg_corner_speed_without_aero'],
        comparison['avg_straight_speed_without_aero']
    ]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, with_aero, width, label='With Aero', color='blue', alpha=0.7)
    bars2 = ax.bar(x + width/2, without_aero, width, label='Without Aero', color='red', alpha=0.7)
    
    ax.set_title('Corner vs Straight Performance')
    ax.set_xlabel('Track Section')
    ax.set_ylabel('Average Speed (mph)')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=10)


def create_speed_distribution_plot(ax, comparison):
    """Create speed distribution histograms."""
    ax.hist(comparison['velocities_with'], bins=20, alpha=0.7, color='blue', 
            label='With Aero', density=True)
    ax.hist(comparison['velocities_without'], bins=20, alpha=0.7, color='red', 
            label='Without Aero', density=True)
    
    ax.set_title('Speed Distribution')
    ax.set_xlabel('Velocity (mph)')
    ax.set_ylabel('Probability Density')
    ax.legend()
    ax.grid(True, alpha=0.3)


def create_performance_summary_plot(ax, comparison):
    """Create performance summary with key metrics."""
    ax.axis('off')
    
    # Key metrics
    metrics = [
        f"Lap Time Improvement: {comparison['lap_time_improvement_pct']:.2f}%",
        f"Time Difference: {comparison['lap_time_difference']:.2f} sec",
        f"Max Speed Gain: {comparison['max_speed_gain']:.1f} mph",
        f"Max Speed Loss: {abs(comparison['max_speed_loss']):.1f} mph",
        f"Avg Speed Difference: {comparison['avg_speed_with_aero'] - comparison['avg_speed_without_aero']:.1f} mph"
    ]
    
    # Vehicle config info
    config = get_vehicle_config(enable_aero=True, aero_config=comparison.get('aero_config'))
    aero_info = [
        f"Configuration: {comparison.get('aero_config', 'default').title()}",
        f"Drag Coefficient: {config['drag_coefficient']:.4f}",
        f"Downforce Coefficient: {config['downforce_coefficient']:.4f}",
        f"Frontal Area: {config['frontal_area']:.1f} m²"
    ]
    
    # Display metrics
    y_pos = 0.9
    ax.text(0.05, y_pos, "PERFORMANCE IMPACT:", fontsize=14, fontweight='bold')
    y_pos -= 0.1
    
    for metric in metrics:
        ax.text(0.05, y_pos, metric, fontsize=11)
        y_pos -= 0.1
    
    y_pos -= 0.1
    ax.text(0.05, y_pos, "AERODYNAMIC PARAMETERS:", fontsize=14, fontweight='bold')
    y_pos -= 0.1
    
    for info in aero_info:
        ax.text(0.05, y_pos, info, fontsize=11)
        y_pos -= 0.1
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def print_comparison_summary(comparison):
    """Print detailed comparison summary to console."""
    print(f"\n{'='*60}")
    print("AERODYNAMICS IMPACT SUMMARY")
    print(f"{'='*60}")
    
    print(f"\nLAP TIME COMPARISON:")
    print(f"  With Aerodynamics:    {comparison['lap_time_with_aero']:.3f} seconds")
    print(f"  Without Aerodynamics: {comparison['lap_time_without_aero']:.3f} seconds")
    print(f"  Time Difference:      {comparison['lap_time_difference']:.3f} seconds")
    print(f"  Improvement:          {comparison['lap_time_improvement_pct']:.2f}%")
    
    print(f"\nSPEED ANALYSIS:")
    print(f"  Average Speed (with aero):    {comparison['avg_speed_with_aero']:.1f} mph")
    print(f"  Average Speed (without aero): {comparison['avg_speed_without_aero']:.1f} mph")
    print(f"  Maximum Speed (with aero):    {comparison['max_speed_with_aero']:.1f} mph")
    print(f"  Maximum Speed (without aero): {comparison['max_speed_without_aero']:.1f} mph")
    
    print(f"\nCORNER vs STRAIGHT PERFORMANCE:")
    print(f"  Corner Speed (with aero):     {comparison['avg_corner_speed_with_aero']:.1f} mph")
    print(f"  Corner Speed (without aero):  {comparison['avg_corner_speed_without_aero']:.1f} mph")
    print(f"  Straight Speed (with aero):   {comparison['avg_straight_speed_with_aero']:.1f} mph")
    print(f"  Straight Speed (without aero):{comparison['avg_straight_speed_without_aero']:.1f} mph")
    
    print(f"\nMAXIMUM DIFFERENCES:")
    print(f"  Biggest Speed Gain:  {comparison['max_speed_gain']:.1f} mph (aero helps)")
    print(f"  Biggest Speed Loss:  {abs(comparison['max_speed_loss']):.1f} mph (aero hurts)")
    
    # Analyze where aero helps most
    if comparison['max_speed_gain'] > abs(comparison['max_speed_loss']):
        print(f"\n  → Aerodynamics provides NET BENEFIT on this track")
    else:
        print(f"\n  → Aerodynamics provides NET COST on this track")
    
    print(f"\n{'='*60}")


def main():
    """Main function to run aerodynamics comparison."""
    print("Aerodynamics Impact Analysis")
    print("=" * 40)
    
    # Get user choice for aerodynamic configuration
    print("\nSelect aerodynamic configuration:")
    print("1. Original MATLAB values (Cd=0.0184, Cl=0.0418)")
    print("2. Realistic FSAE values (Cd=1.0, Cl=2.5)")
    print("3. High downforce setup (Cd=1.3, Cl=3.2)")
    
    aero_choice = input("Enter choice (1-3): ").strip()
    
    if aero_choice == '1':
        aero_config = 'original'
    elif aero_choice == '2':
        aero_config = 'realistic'
    elif aero_choice == '3':
        aero_config = 'high_downforce'
    else:
        print("Invalid choice. Using original MATLAB values...")
        aero_config = 'original'
    
    # Get user choice for track type
    print("\nSelect track type:")
    print("1. Autocross")
    print("2. Endurance")
    print("3. Both")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        run_aero_comparison('autocross', aero_config=aero_config)
    elif choice == '2':
        run_aero_comparison('endurance', aero_config=aero_config)
    elif choice == '3':
        print("\nRunning comparison for both tracks...\n")
        run_aero_comparison('autocross', aero_config=aero_config)
        run_aero_comparison('endurance', aero_config=aero_config)
    else:
        print("Invalid choice. Running autocross comparison...")
        run_aero_comparison('autocross', aero_config=aero_config)


if __name__ == "__main__":
    main()
