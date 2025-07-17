"""
Vehicle Configuration Example
=============================

This script demonstrates how to use the vehicle_config.py file
to modify vehicle parameters and run simulations with different configurations.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add the python directory to the path to import vehicle_config
current_dir = os.path.dirname(__file__)
python_dir = os.path.dirname(current_dir)  # Go up one level to python/
sys.path.insert(0, python_dir)

# Import vehicle configuration
from vehicle_config import (
    get_vehicle_config, 
    get_powertrain_config,
    print_vehicle_summary,
    LIGHTWEIGHT_CONFIG,
    HIGH_DOWNFORCE_CONFIG,
    AUTOCROSS_CONFIG
)

# Import output utilities
from lap_simulation.output_utils import get_plot_path, print_save_message

# Import simulation modules
from lap_simulation.lap_sim import LapSimulator
from lap_simulation.data_loader import DataManager


def run_simulation_with_config(config_name, vehicle_modifications=None, powertrain_modifications=None):
    """
    Run simulation with modified vehicle configuration.
    
    Parameters:
    -----------
    config_name : str
        Name of the configuration for display
    vehicle_modifications : dict, optional
        Vehicle parameter modifications
    powertrain_modifications : dict, optional
        Powertrain parameter modifications
    """
    print(f"\n{'='*20} {config_name} {'='*20}")
    
    # Get base configurations
    vehicle_config = get_vehicle_config()
    powertrain_config = get_powertrain_config()
    
    # Apply modifications
    if vehicle_modifications:
        vehicle_config.update(vehicle_modifications)
        print("Vehicle modifications applied:")
        for key, value in vehicle_modifications.items():
            print(f"  {key}: {value}")
    
    if powertrain_modifications:
        powertrain_config.update(powertrain_modifications)
        print("Powertrain modifications applied:")
        for key, value in powertrain_modifications.items():
            print(f"  {key}: {value}")
    
    # Initialize simulator with custom config
    simulator = LapSimulator(vehicle_config, powertrain_config)
    
    # Load track data
    data_manager = DataManager()
    try:
        track_data = data_manager.load_track_coordinates("endurance")
        print(f"Loaded track with {len(track_data['x'])} points")
        
        # Run simulation
        results = simulator.simulate_full_lap(track_data)
        
        # Calculate performance metrics
        max_lat_g = np.max(np.abs(results['lateral_g']))
        max_long_g_accel = np.max(results['longitudinal_g'])
        max_long_g_brake = np.min(results['longitudinal_g'])
        total_time = results['lap_time']
        
        print(f"Performance Summary:")
        print(f"  Lap Time: {total_time:.2f} seconds")
        print(f"  Max Lateral G: ±{max_lat_g:.2f}g")
        print(f"  Max Acceleration: {max_long_g_accel:.2f}g")
        print(f"  Max Braking: {max_long_g_brake:.2f}g")
        
        return results
        
    except Exception as e:
        print(f"Simulation failed: {e}")
        return None


def compare_configurations():
    """Compare different vehicle configurations."""
    print("VEHICLE CONFIGURATION COMPARISON")
    print("="*60)
    
    # Baseline configuration
    baseline = run_simulation_with_config("BASELINE")
    
    # Lightweight configuration
    lightweight = run_simulation_with_config("LIGHTWEIGHT", LIGHTWEIGHT_CONFIG)
    
    # High downforce configuration
    high_df = run_simulation_with_config("HIGH DOWNFORCE", HIGH_DOWNFORCE_CONFIG)
    
    # Autocross configuration
    autocross = run_simulation_with_config("AUTOCROSS", AUTOCROSS_CONFIG)
    
    # Plot comparison if all simulations succeeded
    if all([baseline, lightweight, high_df, autocross]):
        plot_comparison(baseline, lightweight, high_df, autocross)


def plot_comparison(baseline, lightweight, high_df, autocross):
    """Plot comparison of different configurations."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    configs = {
        'Baseline': baseline,
        'Lightweight': lightweight,
        'High Downforce': high_df,
        'Autocross': autocross
    }
    
    colors = ['blue', 'green', 'red', 'orange']
    
    # Lateral acceleration comparison
    for i, (name, data) in enumerate(configs.items()):
        ax1.plot(data['distance'], data['lateral_g'], 
                color=colors[i], label=name, alpha=0.7)
    ax1.set_title('Lateral Acceleration Comparison')
    ax1.set_xlabel('Distance [m]')
    ax1.set_ylabel('Lateral Acceleration [g]')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Longitudinal acceleration comparison
    for i, (name, data) in enumerate(configs.items()):
        ax2.plot(data['distance'], data['longitudinal_g'], 
                color=colors[i], label=name, alpha=0.7)
    ax2.set_title('Longitudinal Acceleration Comparison')
    ax2.set_xlabel('Distance [m]')
    ax2.set_ylabel('Longitudinal Acceleration [g]')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Velocity comparison
    for i, (name, data) in enumerate(configs.items()):
        ax3.plot(data['distance'], data['velocity'], 
                color=colors[i], label=name, alpha=0.7)
    ax3.set_title('Velocity Comparison')
    ax3.set_xlabel('Distance [m]')
    ax3.set_ylabel('Velocity [m/s]')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Lap time comparison (bar chart)
    lap_times = [data['lap_time'] for data in configs.values()]
    ax4.bar(configs.keys(), lap_times, color=colors, alpha=0.7)
    ax4.set_title('Lap Time Comparison')
    ax4.set_ylabel('Lap Time [s]')
    ax4.grid(True, alpha=0.3)
    
    # Add percentage improvement labels
    baseline_time = lap_times[0]
    for i, (name, time) in enumerate(zip(configs.keys(), lap_times)):
        if i > 0:  # Skip baseline
            improvement = (baseline_time - time) / baseline_time * 100
            ax4.text(i, time + 0.5, f'{improvement:+.1f}%', 
                    ha='center', va='bottom')
    
    plt.tight_layout()
    plot_path = get_plot_path('configuration_comparison.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print_save_message(plot_path, 'plot')
    plt.show()


def create_custom_config_example():
    """Example of creating a custom vehicle configuration."""
    print("\nCUSTOM CONFIGURATION EXAMPLE")
    print("="*40)
    
    # Create a custom high-performance configuration
    custom_config = {
        'mass': 260,  # Lighter vehicle
        'cg_height': 0.240,  # Lower center of gravity
        'downforce_coefficient': 2.8,  # More downforce
        'drag_coefficient': 1.15,  # Slightly more drag
        'tire_params': {
            'mu': 1.9,  # Better tires
            'B': 13.0,  # Stiffer response
            'C': 1.4,
            'D': 1.0,
            'E': -0.5
        }
    }
    
    custom_powertrain = {
        'shift_point': 13500,  # Earlier shift for reliability
        'drivetrain_losses': 0.88,  # Better drivetrain efficiency
    }
    
    results = run_simulation_with_config(
        "CUSTOM HIGH-PERFORMANCE", 
        custom_config, 
        custom_powertrain
    )
    
    return results


def parameter_sensitivity_study():
    """Study sensitivity to mass changes."""
    print("\nPARAMETER SENSITIVITY STUDY - VEHICLE MASS")
    print("="*50)
    
    masses = [250, 260, 270, 280, 290, 300]  # kg
    lap_times = []
    max_lat_gs = []
    
    for mass in masses:
        print(f"\nTesting mass: {mass} kg")
        results = run_simulation_with_config(
            f"MASS_{mass}KG", 
            {'mass': mass}
        )
        
        if results:
            lap_times.append(results['lap_time'])
            max_lat_gs.append(np.max(np.abs(results['lateral_g'])))
        else:
            lap_times.append(None)
            max_lat_gs.append(None)
    
    # Plot sensitivity
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    valid_masses = [m for m, t in zip(masses, lap_times) if t is not None]
    valid_times = [t for t in lap_times if t is not None]
    valid_lat_gs = [g for g in max_lat_gs if g is not None]
    
    ax1.plot(valid_masses, valid_times, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Vehicle Mass [kg]')
    ax1.set_ylabel('Lap Time [s]')
    ax1.set_title('Lap Time vs Vehicle Mass')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(valid_masses, valid_lat_gs, 'ro-', linewidth=2, markersize=8)
    ax2.set_xlabel('Vehicle Mass [kg]')
    ax2.set_ylabel('Max Lateral Acceleration [g]')
    ax2.set_title('Max Lateral G vs Vehicle Mass')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = get_plot_path('mass_sensitivity.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print_save_message(plot_path, 'plot')
    plt.show()


def main():
    """Main function to demonstrate vehicle configuration usage."""
    print("VEHICLE CONFIGURATION DEMONSTRATION")
    print("="*60)
    
    # Show current vehicle configuration
    print_vehicle_summary()
    
    # Run different configuration comparisons
    try:
        # Compare predefined configurations
        compare_configurations()
        
        # Create and test custom configuration
        create_custom_config_example()
        
        # Parameter sensitivity study
        parameter_sensitivity_study()
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETE")
        print("Check the plots/ directory for generated visualizations")
        print("="*60)
        
    except Exception as e:
        print(f"Demonstration failed: {e}")
        print("This may be due to missing data files or simulation dependencies")


if __name__ == "__main__":
    main()
