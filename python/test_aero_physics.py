#!/usr/bin/env python3
"""
Test Aerodynamics Physics Implementation
=======================================

This script tests the aerodynamics calculations to ensure they're working correctly
and having a meaningful impact on the simulation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from lap_simulation.physics import get_vehicle_parameters
from vehicle_config import get_vehicle_config

def test_aerodynamics_physics():
    """Test that aerodynamics calculations are working correctly."""
    
    print("TESTING AERODYNAMICS PHYSICS")
    print("=" * 50)
    
    # Get vehicle parameters with and without aero
    params_with = get_vehicle_parameters('endurance', enable_aero=True)
    params_without = get_vehicle_parameters('endurance', enable_aero=False)
    
    print("\n1. Vehicle Parameters Check:")
    print(f"   With Aero - Cl: {params_with['aero_cl']:.4f}, Cd: {params_with['aero_cd']:.4f}")
    print(f"   Without Aero - Cl: {params_without['aero_cl']:.4f}, Cd: {params_without['aero_cd']:.4f}")
    
    # Test at various speeds
    speeds_mph = [20, 40, 60, 80]
    
    print("\n2. Force Calculations at Different Speeds:")
    print("   Speed (mph) | Downforce (lbf) | Drag (lbf) | Downforce (equiv lbs)")
    print("   " + "-" * 60)
    
    for speed_mph in speeds_mph:
        speed_fps = speed_mph * 5280 / 3600
        
        # With aero
        downforce = 0.5 * params_with['air_density'] * params_with['aero_cl'] * params_with['frontal_area'] * speed_fps**2
        drag = 0.5 * params_with['air_density'] * params_with['aero_cd'] * params_with['frontal_area'] * speed_fps**2
        downforce_equiv_lbs = downforce / 32.2  # Convert force to equivalent mass
        
        print(f"   {speed_mph:8.0f}    | {downforce:11.2f}  | {drag:8.2f}  | {downforce_equiv_lbs:15.2f}")
    
    # Test cornering speed impact
    print("\n3. Cornering Speed Impact:")
    test_radius = 100  # feet
    base_lat_accel = 1.4 * 32.2  # 1.4g in ft/s²
    vehicle_mass = params_with['mass']
    
    print(f"   Test corner radius: {test_radius} ft")
    print(f"   Base lateral acceleration: {1.4} g")
    print(f"   Vehicle mass: {vehicle_mass:.1f} lbs")
    
    for speed_mph in [40, 60]:
        speed_fps = speed_mph * 5280 / 3600
        
        # Calculate downforce at this speed
        downforce = 0.5 * params_with['air_density'] * params_with['aero_cl'] * params_with['frontal_area'] * speed_fps**2
        downforce_equiv_lbs = downforce / 32.2
        
        # Effective weight and cornering speed
        effective_weight = vehicle_mass + downforce_equiv_lbs
        weight_factor = effective_weight / vehicle_mass
        scaled_lat_accel = base_lat_accel * weight_factor
        max_corner_speed_fps = np.sqrt(scaled_lat_accel * test_radius)
        max_corner_speed_mph = max_corner_speed_fps * 3600 / 5280
        
        # Without aero
        max_corner_speed_no_aero_fps = np.sqrt(base_lat_accel * test_radius)
        max_corner_speed_no_aero_mph = max_corner_speed_no_aero_fps * 3600 / 5280
        
        improvement = max_corner_speed_mph - max_corner_speed_no_aero_mph
        improvement_pct = (improvement / max_corner_speed_no_aero_mph) * 100
        
        print(f"\n   At {speed_mph} mph estimate:")
        print(f"     Downforce: {downforce:.2f} lbf ({downforce_equiv_lbs:.2f} equiv lbs)")
        print(f"     Weight factor: {weight_factor:.3f}")
        print(f"     Max corner speed (with aero): {max_corner_speed_mph:.1f} mph")
        print(f"     Max corner speed (no aero): {max_corner_speed_no_aero_mph:.1f} mph")
        print(f"     Improvement: {improvement:.1f} mph ({improvement_pct:.1f}%)")
    
    # Test drag impact on acceleration
    print("\n4. Drag Impact on Acceleration:")
    max_accel = 0.8 * 32.2  # 0.8g in ft/s²
    
    for speed_mph in speeds_mph:
        speed_fps = speed_mph * 5280 / 3600
        
        # Calculate drag deceleration
        drag = 0.5 * params_with['air_density'] * params_with['aero_cd'] * params_with['frontal_area'] * speed_fps**2
        drag_accel = (drag / vehicle_mass) * 32.2
        net_accel = max_accel - drag_accel
        net_accel_g = net_accel / 32.2
        
        drag_reduction_pct = (drag_accel / max_accel) * 100
        
        print(f"   {speed_mph} mph: Drag = {drag:.2f} lbf, Drag accel = {drag_accel:.3f} ft/s² ({drag_reduction_pct:.1f}% reduction)")
        print(f"           Net acceleration: {net_accel_g:.2f} g")
    
    # Test if coefficients are realistic for FSAE
    print("\n5. Aerodynamic Coefficient Assessment:")
    config = get_vehicle_config(enable_aero=True)
    
    print(f"   Frontal Area: {config['frontal_area']:.2f} m² ({config['frontal_area'] * 10.764:.1f} ft²)")
    print(f"   Drag Coefficient: {config['drag_coefficient']:.4f}")
    print(f"   Downforce Coefficient: {config['downforce_coefficient']:.4f}")
    print(f"   Downforce/Drag Ratio: {config['downforce_coefficient']/config['drag_coefficient']:.2f}")
    
    # Typical FSAE values for reference
    print("\n   FSAE Reference Values:")
    print("   - Frontal Area: 1.0-1.5 m² (typical)")
    print("   - Drag Coefficient: 0.3-1.2 (without wings), 0.7-1.5 (with wings)")
    print("   - Downforce Coefficient: 0.0-3.5 (with wings)")
    print("   - Current values appear to be very optimistic/unrealistic")
    
    if config['drag_coefficient'] < 0.5:
        print("   ⚠️  WARNING: Drag coefficient is unusually low for FSAE")
    if config['downforce_coefficient'] < 1.0:
        print("   ⚠️  WARNING: Downforce coefficient is low for a car with aerodynamic package")
        
    print("\n" + "=" * 50)


if __name__ == "__main__":
    test_aerodynamics_physics()
