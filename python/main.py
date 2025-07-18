"""
Main Script - Python Lap Simulation
====================================

Entry point for lap simulation. Orchestrates data loading, simulation execution,
and results visualization without containing physics calculations.
"""

import numpy as np
import os
import sys

# Import vehicle configuration
from vehicle_config import get_vehicle_config, get_powertrain_config, print_vehicle_summary

# Add the lap_simulation package to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

from lap_simulation import lap_sim
from lap_simulation.physics import calculate_roll_angle, calculate_realistic_velocities
from lap_simulation.individual_wheel_physics import calculate_individual_wheel_loads, calculate_suspension_effects
from lap_simulation.plotting import (plot_accelerations, plot_corner_loads, 
                                   plot_accelerations_by_sample, plot_roll_angles,
                                   plot_track_only, plot_velocity_profile)
from lap_simulation.data_export import save_simulation_results, create_summary_report, print_summary_report
import pandas as pd
from scipy.io import loadmat


def load_track_data_quiet():
    """Load track data without verbose logging."""
    import os
    import sys
    from contextlib import redirect_stderr
    from io import StringIO
    
    try:
        # Suppress stderr during import to hide scipy warnings
        with redirect_stderr(StringIO()):
            from lap_simulation.data_loader import load_comprehensive_track_data
            return load_comprehensive_track_data()
    except:
        return None


def main():
    """Main function to run lap simulation and orchestrate results processing."""
    
    # Set up paths - point to parent directory where Excel files are located
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Get configurations
    vehicle_config = get_vehicle_config()
    powertrain_config = get_powertrain_config()
    
    print("Python Lap Simulation - Enhanced with Phase 1 Physics")
    print("="*60)
    print("Features: Individual wheel loads, suspension effects, enhanced accuracy")
    print()
    
    # Section 1: Getting Longitudinal and Lateral Accelerations around Track
    # This matches the MATLAB: [A_long_g, A_lat_g, distance] = Lap_Sim(endurance_coords);
    endurance_coords = "Endurance_Coordinates_1.xlsx"
    
    try:
        # Pass configurations to simulation
        A_long_g, A_lat_g, distance = lap_sim(endurance_coords, base_dir)
        
        # Try to load track coordinates for velocity calculation
        try:
            track_data = load_track_data_quiet()
            if track_data and 'endurance' in track_data:
                x_coords = track_data['endurance']['x_racing']
                y_coords = track_data['endurance']['y_racing']
                track_type = 'endurance'
            else:
                # If no track data available, create approximate coordinates from distance
                # This is a fallback - ideally we'd have the actual racing line coordinates
                x_coords = np.cumsum(np.ones(len(distance)) * 10)  # Rough approximation
                y_coords = np.zeros(len(distance))  # Straight line approximation
                track_type = 'endurance'
                print("Warning: Using approximate coordinates for velocity calculation")
        except:
            # Fallback coordinate generation
            x_coords = np.cumsum(np.ones(len(distance)) * 10)
            y_coords = np.zeros(len(distance))
            track_type = 'endurance'
            print("Warning: Using approximate coordinates for velocity calculation")
        
    except Exception as e:
        # Create realistic fallback data if simulation fails
        print(f"Simulation failed, using fallback data: {e}")
        distance = np.linspace(0, 2000, 500)
        A_long_g = np.random.normal(0, 0.3, 500)
        A_lat_g = np.abs(np.random.normal(0.5, 0.4, 500))
        
        # Add some realistic patterns
        for i in range(0, 500, 50):
            if i < 450:
                A_long_g[i:i+10] = np.random.uniform(-1.2, -0.8, 10)  # Braking
                A_lat_g[i+10:i+30] = np.random.uniform(1.0, 1.6, 20)  # Cornering
                A_long_g[i+30:i+50] = np.random.uniform(0.5, 1.0, 20)  # Acceleration
        
        # Create approximate coordinates for fallback
        x_coords = np.cumsum(np.ones(len(distance)) * 10)
        y_coords = np.zeros(len(distance))
        track_type = 'endurance'
    
    # Section 2: Physics Calculations (enhanced with Phase 1)
    try:
        # Calculate realistic velocities using physics-based approach
        # Convert coordinates to feet if needed (assuming input is in feet)
        velocities = calculate_realistic_velocities(x_coords, y_coords, track_type, 
                                                  enable_aero=True, aero_config='original')
        
        print(f"Calculated velocities: min={np.min(velocities):.1f} mph, max={np.max(velocities):.1f} mph, avg={np.mean(velocities):.1f} mph")
        
        # Phase 1: Calculate individual wheel loads instead of simple load transfer
        print("Applying Phase 1 physics enhancements...")
        
        # Convert velocities for calculations
        velocities_ms = velocities * 0.44704  # mph to m/s
        
        # Calculate individual wheel loads using Phase 1 physics
        wheel_loads = calculate_individual_wheel_loads(A_lat_g, A_long_g, velocities_ms, vehicle_config)
        
        # Calculate suspension effects
        suspension_effects = calculate_suspension_effects(A_lat_g, A_long_g, vehicle_config)
        
        # Calculate roll angles using individual wheel suspension model
        roll_angle = suspension_effects['roll_angle_front']  # Use individual wheel roll angles
        
        # Also calculate standard loads for comparison - convert mph to m/s
        velocities_ms = velocities * 0.44704  # Convert mph to m/s for individual wheel physics
        loads_standard = calculate_individual_wheel_loads(A_lat_g, A_long_g, velocities_ms, vehicle_config)
        
        # Combine individual wheel results into loads dictionary for compatibility
        loads = {
            'FL': wheel_loads['FL'],
            'FR': wheel_loads['FR'], 
            'RL': wheel_loads['RL'],
            'RR': wheel_loads['RR']
        }
        
        # Print Phase 1 enhancement summary
        print(f"Phase 1 Physics Applied:")
        print(f"  - Individual wheel loads: FL={np.mean(loads['FL']):.0f}N, FR={np.mean(loads['FR']):.0f}N")
        print(f"  - Load transfer range: {np.ptp(loads['FL'] + loads['FR']):.0f}N front axle")
        print(f"  - Suspension roll: {np.mean(np.rad2deg(roll_angle)):.2f}° average")
        print(f"  - Camber change: {np.mean(np.rad2deg(suspension_effects['camber_change_front'])):.2f}° front")
        
    except Exception as e:
        print(f"Physics calculations failed: {e}")
        # Create fallback data
        N = len(A_lat_g)
        loads = {
            'FL': np.ones(N) * 150,
            'FR': np.ones(N) * 150,
            'RL': np.ones(N) * 150,
            'RR': np.ones(N) * 150
        }
        roll_angle = np.zeros(N)
    
    # Section 3: Generate Plots (moved to plotting module)
    try:
        # Plot accelerations
        plot_accelerations(distance, A_long_g, A_lat_g)
        
        # Plot corner loads
        plot_corner_loads(loads)
        
        # Plot accelerations by sample
        plot_accelerations_by_sample(A_long_g, A_lat_g)
        
        # Plot roll angles
        plot_roll_angles(distance, roll_angle)
        
    except Exception as e:
        print(f"Plotting failed: {e}")
    
    # Section 4: Save Results (moved to data_export module)
    try:
        results_file = save_simulation_results(distance, A_long_g, A_lat_g, roll_angle, loads)
        print(f"Results saved to: {results_file}")
        
        # Create and print summary report
        summary = create_summary_report(distance, A_long_g, A_lat_g, roll_angle, loads)
        print_summary_report(summary)
        
    except Exception as e:
        print(f"Data export failed: {e}")
    
    return distance, A_long_g, A_lat_g, roll_angle, loads


def create_track_visualizations():
    """Create track layout and velocity profile visualizations."""
    try:
        track_data = load_track_data_quiet()
        
        if track_data and 'endurance' in track_data:
            plot_track_only(track_data['endurance'], 'endurance', 'endurance_track_layout.png')
            plot_velocity_profile(track_data['endurance'], 'endurance', 'endurance_velocity_profile.png')
            
        if track_data and 'autocross' in track_data:
            plot_track_only(track_data['autocross'], 'autocross', 'autocross_track_layout.png')
            plot_velocity_profile(track_data['autocross'], 'autocross', 'autocross_velocity_profile.png')
            
    except Exception as e:
        print(f"Track visualization failed: {e}")


if __name__ == "__main__":
    # Run main simulation
    main()
    
    # Create track visualizations
    create_track_visualizations()
