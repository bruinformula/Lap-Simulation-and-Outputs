#!/usr/bin/env python3
"""
Debug script for physics velocity calculation
"""

import sys
import os
import numpy as np

# Add the physics module to path
sys.path.append('/Users/Hiro/Documents/Programming/GitHub/Lap-Simulation and Outputs/python')

from lap_simulation.physics import calculate_realistic_velocities, get_vehicle_parameters, calculate_track_curvature, calculate_max_cornering_speeds
from visualization.plot_racing_track import load_comprehensive_track_data

print("Testing physics velocity calculation...")
print("=" * 50)

# Load track data to get coordinates
base_dir = '/Users/Hiro/Documents/Programming/GitHub/Lap-Simulation and Outputs'
track_data = load_comprehensive_track_data(base_dir)

if 'endurance' in track_data:
    racing_line = track_data['endurance']['racing_line']
    x_coords = racing_line['x']
    y_coords = racing_line['y']
    
    print(f"Testing with {len(x_coords)} endurance track points")
    
    # Get vehicle parameters
    vehicle_params = get_vehicle_parameters('endurance')
    print(f"Vehicle params: base_speed={vehicle_params['base_speed']}, max_speed={vehicle_params['max_speed']}")
    
    # Calculate curvature
    curvatures = calculate_track_curvature(x_coords, y_coords)
    print(f"Curvatures - Min: {np.min(curvatures):.6f}, Max: {np.max(curvatures):.6f}, Mean: {np.mean(curvatures):.6f}")
    
    # Calculate max cornering speeds
    max_cornering_speeds = calculate_max_cornering_speeds(curvatures, vehicle_params)
    print(f"Max cornering speeds - Min: {np.min(max_cornering_speeds):.1f}, Max: {np.max(max_cornering_speeds):.1f}, Mean: {np.mean(max_cornering_speeds):.1f}")
    
    # Calculate final velocities
    velocities = calculate_realistic_velocities(x_coords, y_coords, 'endurance')
    print(f"Final velocities - Min: {np.min(velocities):.1f}, Max: {np.max(velocities):.1f}, Mean: {np.mean(velocities):.1f}")
    
    # Check if velocities are all the same
    if np.max(velocities) - np.min(velocities) < 0.1:
        print("❌ PROBLEM: Velocities are essentially constant!")
        print("   This indicates the physics algorithm is not working correctly")
        
        # Check the first few cornering speeds vs final velocities
        print("   First 10 cornering speeds:", max_cornering_speeds[:10])
        print("   First 10 final velocities:", velocities[:10])
    else:
        print("✅ Velocities have variation - physics working correctly")

else:
    print("❌ No endurance track data available for testing")
