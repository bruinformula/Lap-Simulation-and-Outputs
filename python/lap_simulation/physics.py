"""
Racing Physics and Velocity Calculation Module
==============================================

Physics calculations following MATLAB Lap_Sim methodology.
Calculates realistic velocities based on vehicle dynamics, track geometry, and racing physics.

TABLE OF CONTENTS
================

Core Physics Functions:
-----------------------
1. calculate_realistic_velocities()         - Main velocity calculation with physics-based approach
2. calculate_comprehensive_lap_physics()    - Complete lap physics integration (curvature, velocity, acceleration)

Track Geometry & Curvature:
---------------------------
3. calculate_track_curvature()             - Curvature calculation using circumcenter method
4. calculate_signed_curvature()            - Signed curvature for turn direction detection
5. calculate_cumulative_distance()         - Distance calculations along racing line
6. calculate_distance_array()              - Cumulative distance from coordinates

Velocity & Speed Calculations:
-----------------------------
7. calculate_max_cornering_speeds()        - Maximum cornering speeds from lateral grip limits
8. calculate_velocity_from_curvature()     - Velocity limits based on curvature and tire grip
9. apply_acceleration_limits()             - Forward pass with acceleration constraints
10. apply_deceleration_limits()            - Backward pass with braking constraints
11. apply_acceleration_and_braking_constraints() - Combined acceleration/braking physics
12. finalize_velocity_profile()            - Final smoothing and bounds checking

Acceleration Calculations:
-------------------------
13. calculate_longitudinal_acceleration()   - Longitudinal acceleration from velocity/distance
14. calculate_lateral_acceleration_from_velocity() - Lateral acceleration from velocity/curvature
15. apply_realistic_limits_and_noise()     - Apply FSAE limits and realistic noise

Vehicle Dynamics:
----------------
16. calculate_load_transfer()              - Individual wheel loads with load transfer
17. calculate_roll_angle()                 - Vehicle body roll angle during cornering

Utility Functions:
-----------------
18. get_vehicle_parameters()               - Track-specific vehicle parameter setup
19. estimate_lap_time()                    - Lap time estimation from velocity profile
"""

import numpy as np
from scipy.ndimage import gaussian_filter1d
import sys
import os

# Add parent directory to path to import vehicle_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vehicle_config import get_vehicle_config, TIRE_MF52_PARAMS


def calculate_realistic_velocities(x_coords, y_coords, track_type, enable_aero=None, aero_config=None):
    """
    Calculate realistic velocities using MATLAB-inspired physics-based approach.
    
    This implements a simplified version of the MATLAB Lap_Sim methodology:
    1. Calculate track curvature (radius) at each point
    2. Determine maximum cornering velocity from lateral grip limits
    3. Apply acceleration/deceleration limits between points
    4. Consider aerodynamics and track-specific characteristics
    
    Parameters:
    -----------
    x_coords, y_coords : array_like
        Racing line coordinates in feet
    track_type : str
        Type of track ('endurance' or 'autocross')
    enable_aero : bool, optional
        Override aerodynamics enable/disable. If None, uses config default.
    aero_config : str or dict, optional
        Aerodynamics configuration ('original', 'realistic', 'high_downforce', or custom dict)
        
    Returns:
    --------
    np.ndarray
        Velocity array in mph
    """
    n_points = len(x_coords)
    velocities = np.zeros(n_points)
    
    # Get vehicle parameters for the specific track type
    vehicle_params = get_vehicle_parameters(track_type, enable_aero=enable_aero, aero_config=aero_config)
    
    # Calculate curvature at each point
    curvatures = calculate_track_curvature(x_coords, y_coords)
    
    # Calculate maximum cornering speeds from lateral acceleration limits
    max_cornering_speeds = calculate_max_cornering_speeds(curvatures, vehicle_params)
    
    # Apply forward pass (acceleration limited)
    velocities = apply_acceleration_limits(x_coords, y_coords, max_cornering_speeds, vehicle_params)
    
    # Apply backward pass (deceleration limited)
    velocities = apply_deceleration_limits(x_coords, y_coords, velocities, vehicle_params)
    
    # Final smoothing and bounds checking
    velocities = finalize_velocity_profile(velocities, vehicle_params)
    
    return velocities


def get_vehicle_parameters(track_type, enable_aero=None, aero_config=None):
    """
    Get vehicle parameters based on track type using vehicle_config.py values.
    
    Parameters:
    -----------
    track_type : str
        Type of track ('endurance' or 'autocross')
    enable_aero : bool, optional
        Override aerodynamics enable/disable. If None, uses config default.
    aero_config : str or dict, optional
        Aerodynamics configuration ('original', 'realistic', 'high_downforce', or custom dict)
        
    Returns:
    --------
    dict
        Vehicle parameter dictionary
    """
    # Get base vehicle configuration from vehicle_config.py
    config = get_vehicle_config(enable_aero=enable_aero, aero_config=aero_config)
    
    # Convert units and calculate derived parameters
    vehicle_params = {
        # Mass properties (convert from metric to imperial for internal calculations)
        'mass': config['mass'] * 2.205,  # kg to lbs
        'cg_height': config['cg_height'] * 3.281,  # m to ft
        'wheelbase': config['wheelbase'] * 3.281,  # m to ft
        'track_width': config['track_width'] * 3.281,  # m to ft
        
        # Tire parameters
        'tire_mu': TIRE_MF52_PARAMS['mu'],  # Peak friction coefficient
        
        # Aerodynamics (convert to imperial units)
        'aero_cl': config['downforce_coefficient'],
        'aero_cd': config['drag_coefficient'],
        'frontal_area': config['frontal_area'] * 10.764,  # m² to ft²
        'air_density': config['air_density'] * 0.00194,  # kg/m³ to slugs/ft³
        'aero_enabled': config.get('aero_enabled', True),
        'aero_config': config.get('aero_config', 'realistic'),
        
        # Performance limits (realistic estimates based on FSAE capabilities)
        'max_lat_accel': 1.4,  # realistic max lateral g's for FSAE
        'max_lng_accel': 0.8,  # realistic power-limited acceleration
        'max_lng_decel': 1.5,  # realistic braking deceleration
    }
    
    # Track-specific parameters
    if track_type == 'endurance':
        # Endurance: physics-based parameters only
        vehicle_params.update({
            'base_speed': 35,  # mph - realistic starting speed
            'corner_factor': 1.1  # slightly more conservative cornering
        })
    else:  # autocross
        # Autocross: physics-based parameters only
        vehicle_params.update({
            'base_speed': 25,  # mph - realistic autocross starting speed
            'corner_factor': 1.3  # more aggressive cornering for tight tracks
        })
    
    return vehicle_params


def calculate_track_curvature(x_coords, y_coords):
    """
    Calculate curvature (1/radius) at each point using circumcenter method.
    
    Parameters:
    -----------
    x_coords, y_coords : array_like
        Track coordinates
        
    Returns:
    --------
    np.ndarray
        Curvature array (1/radius)
    """
    n_points = len(x_coords)
    curvatures = np.zeros(n_points)
    
    for i in range(n_points):
        # Use 5-point stencil for better curvature calculation
        window = min(5, n_points//10)  # adaptive window size
        prev_idx = max(0, i - window)
        next_idx = min(n_points - 1, i + window)
        
        if next_idx > prev_idx + 1:
            # Calculate curvature using circumcenter method for better accuracy
            try:
                # Three points for curvature calculation
                p1_idx = prev_idx
                p2_idx = i  
                p3_idx = next_idx
                
                x1, y1 = x_coords[p1_idx], y_coords[p1_idx]
                x2, y2 = x_coords[p2_idx], y_coords[p2_idx]
                x3, y3 = x_coords[p3_idx], y_coords[p3_idx]
                
                # Calculate circumradius (radius of circle through 3 points)
                a = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                b = np.sqrt((x3-x2)**2 + (y3-y2)**2)
                c = np.sqrt((x1-x3)**2 + (y1-y3)**2)
                
                # Area using cross product
                area = 0.5 * abs((x2-x1)*(y3-y1) - (x3-x1)*(y2-y1))
                
                if area > 1e-6 and a > 0 and b > 0 and c > 0:
                    # Circumradius formula
                    radius = (a * b * c) / (4 * area)
                    curvatures[i] = 1.0 / max(radius, 10)  # min radius = 10 ft
                else:
                    curvatures[i] = 0  # straight section
                    
            except (ZeroDivisionError, ValueError):
                curvatures[i] = 0
        else:
            curvatures[i] = 0
    
    # Smooth curvature to avoid noise
    curvatures = gaussian_filter1d(curvatures, sigma=1.5)
    
    return curvatures


def calculate_max_cornering_speeds(curvatures, vehicle_params):
    """
    Calculate maximum cornering speeds from lateral acceleration limits.
    
    Parameters:
    -----------
    curvatures : np.ndarray
        Track curvature array
    vehicle_params : dict
        Vehicle parameter dictionary
        
    Returns:
    --------
    np.ndarray
        Maximum cornering speeds in mph
    """
    n_points = len(curvatures)
    max_cornering_speeds = np.zeros(n_points)
    
    for i in range(n_points):
        if curvatures[i] > 0:
            radius = 1.0 / curvatures[i]
            
            # Iterative approach to find cornering speed with downforce
            # Start with initial estimate
            v_est_mph = vehicle_params['base_speed']
            
            # Iterate a few times to converge on speed with downforce
            for iteration in range(3):
                v_est_fps = v_est_mph * 5280 / 3600  # convert to ft/s for physics
                
                # Downforce calculation: F = 0.5 * ρ * Cl * A * v²
                # Convert to proper units for imperial system
                downforce_force = 0.5 * vehicle_params['air_density'] * vehicle_params['aero_cl'] * vehicle_params['frontal_area'] * v_est_fps**2
                downforce_lbs = downforce_force / 32.2  # convert force to equivalent mass in lbs
                
                # Effective weight including downforce (more downforce = more grip)
                effective_weight = vehicle_params['mass'] + downforce_lbs
                
                # Maximum lateral acceleration from tire grip
                max_lat_g = vehicle_params['max_lat_accel'] * vehicle_params['corner_factor']
                max_lat_accel = max_lat_g * 32.2  # ft/s²
                
                # Scale by effective weight (more downforce = higher cornering speed)
                weight_factor = effective_weight / vehicle_params['mass']
                scaled_lat_accel = max_lat_accel * weight_factor
                
                # v = sqrt(a * r) for cornering
                max_corner_speed_fps = np.sqrt(scaled_lat_accel * radius)
                v_est_mph = max_corner_speed_fps * 3600 / 5280  # convert to mph
            
            max_cornering_speeds[i] = v_est_mph
        else:
            # Straight section - no cornering limit, will be limited by acceleration/drag
            max_cornering_speeds[i] = float('inf')  # No artificial limit
    
    return max_cornering_speeds


def apply_acceleration_limits(x_coords, y_coords, max_cornering_speeds, vehicle_params):
    """
    Apply forward pass with acceleration limits.
    
    Parameters:
    -----------
    x_coords, y_coords : array_like
        Track coordinates
    max_cornering_speeds : np.ndarray
        Maximum cornering speeds
    vehicle_params : dict
        Vehicle parameters
        
    Returns:
    --------
    np.ndarray
        Velocities after forward pass
    """
    n_points = len(x_coords)
    velocities = np.zeros(n_points)
    
    # Initialize first point from standstill (realistic race start)
    velocities[0] = 5.0  # mph - start from near-standstill like a real race
    
    for i in range(1, n_points):
        # Distance between points
        dx = x_coords[i] - x_coords[i-1]
        dy = y_coords[i] - y_coords[i-1]
        ds = np.sqrt(dx**2 + dy**2)
        
        if ds > 0:
            # Current speed constraint from cornering
            v_corner_limit = max_cornering_speeds[i]
            
            # Maximum speed achievable from previous point with acceleration
            v_prev = velocities[i-1] * 5280 / 3600  # ft/s
            
            # Apply acceleration limit (more generous power model)
            max_accel = vehicle_params['max_lng_accel'] * 32.2  # ft/s²
            
            # Account for drag: F_drag = 0.5 * ρ * Cd * A * v²
            # Drag force in lbs-force, then convert to acceleration
            drag_force = 0.5 * vehicle_params['air_density'] * vehicle_params['aero_cd'] * vehicle_params['frontal_area'] * v_prev**2
            drag_accel = (drag_force / vehicle_params['mass']) * 32.2  # convert to ft/s²
            net_accel = max_accel - drag_accel
            
            # Kinematic equation: v² = v₀² + 2as (more generous acceleration)
            v_max_sq = v_prev**2 + 2 * max(net_accel, max_accel * 0.5) * ds
            v_accel_limit = np.sqrt(max(v_max_sq, v_prev**2)) * 3600 / 5280  # mph
            
            # Take minimum of acceleration and cornering limits (physics-based only)
            velocities[i] = min(v_accel_limit, v_corner_limit)
        else:
            velocities[i] = velocities[i-1]
    
    return velocities


def apply_deceleration_limits(x_coords, y_coords, velocities, vehicle_params):
    """
    Apply backward pass with deceleration limits.
    
    Parameters:
    -----------
    x_coords, y_coords : array_like
        Track coordinates
    velocities : np.ndarray
        Velocities from forward pass
    vehicle_params : dict
        Vehicle parameters
        
    Returns:
    --------
    np.ndarray
        Velocities after backward pass
    """
    n_points = len(velocities)
    
    # Backward pass (deceleration limited)
    for i in range(n_points-2, -1, -1):
        # Distance to next point
        dx = x_coords[i+1] - x_coords[i]
        dy = y_coords[i+1] - y_coords[i]
        ds = np.sqrt(dx**2 + dy**2)
        
        if ds > 0:
            # Speed at next point
            v_next = velocities[i+1] * 5280 / 3600  # ft/s
            
            # Maximum deceleration available
            max_decel = vehicle_params['max_lng_decel'] * 32.2  # ft/s²
            
            # Maximum speed that can be achieved and still decelerate to next point
            # v² = v₀² - 2as (deceleration)
            v_max_sq = v_next**2 + 2 * max_decel * ds
            v_decel_limit = np.sqrt(v_max_sq) * 3600 / 5280  # mph
            
            # Update velocity if deceleration constraint is more restrictive
            velocities[i] = min(velocities[i], v_decel_limit)
    
    return velocities


def finalize_velocity_profile(velocities, vehicle_params):
    """
    Final smoothing and bounds checking for velocity profile.
    
    Parameters:
    -----------
    velocities : np.ndarray
        Raw velocity profile
    vehicle_params : dict
        Vehicle parameters
        
    Returns:
    --------
    np.ndarray
        Final velocity profile
    """
    # Final smoothing (less aggressive smoothing)
    velocities = gaussian_filter1d(velocities, sigma=0.5)  # Reduced from 1.0
    
    # Only apply minimum reasonable speed limit (prevent near-zero speeds)
    min_reasonable_speed = 5.0  # mph - prevent unrealistically low speeds
    velocities = np.maximum(velocities, min_reasonable_speed)
    
    # Ensure reasonable velocity profile
    velocity_changes = np.abs(np.diff(velocities))
    max_change = np.max(velocity_changes) if len(velocity_changes) > 0 else 0
    
    # If changes are too extreme, apply additional smoothing (more lenient threshold)
    if max_change > 25:  # increased from 15 mph to allow more variation
        velocities = gaussian_filter1d(velocities, sigma=1.0)  # Reduced from 2.0
        velocities = np.maximum(velocities, min_reasonable_speed)
    
    return velocities


def calculate_cumulative_distance(x_coords, y_coords):
    """
    Calculate cumulative distance along the racing line.
    
    Parameters:
    -----------
    x_coords, y_coords : array_like
        Track coordinates
        
    Returns:
    --------
    np.ndarray
        Cumulative distance array
    """
    distances = np.zeros(len(x_coords))
    for i in range(1, len(x_coords)):
        dx = x_coords[i] - x_coords[i-1]
        dy = y_coords[i] - y_coords[i-1]
        distances[i] = distances[i-1] + np.sqrt(dx**2 + dy**2)
    return distances


def estimate_lap_time(distances, velocities):
    """
    Estimate lap time from distance and velocity arrays.
    
    Parameters:
    -----------
    distances : np.ndarray
        Cumulative distance array
    velocities : np.ndarray
        Velocity array in mph
        
    Returns:
    --------
    float
        Estimated lap time in seconds
    """
    lap_time = 0
    for i in range(len(velocities)-1):
        if velocities[i] > 0:
            distance_segment = distances[i+1] - distances[i]
            velocity_fps = velocities[i] * 5280 / 3600  # convert mph to ft/s
            time_segment = distance_segment / velocity_fps if velocity_fps > 0 else 0
            lap_time += time_segment
    
    return lap_time


def calculate_load_transfer(A_lat_g, A_long_g, vehicle_config):
    """
    Calculate individual wheel loads accounting for lateral and longitudinal load transfer.
    
    Parameters:
    -----------
    A_lat_g : np.ndarray
        Lateral acceleration in g-force
    A_long_g : np.ndarray
        Longitudinal acceleration in g-force
    vehicle_config : dict
        Vehicle configuration parameters
        
    Returns:
    --------
    dict
        Dictionary with arrays for each wheel load: 'FL', 'FR', 'RL', 'RR' in lbs
    """
    N = len(A_lat_g)
    
    # Initialize load arrays
    loads = {
        'FL': np.zeros(N),  # Front Left
        'FR': np.zeros(N),  # Front Right
        'RL': np.zeros(N),  # Rear Left
        'RR': np.zeros(N)   # Rear Right
    }
    
    # Get vehicle parameters
    base_load = vehicle_config['weight'] / 4.0 * 0.224809  # N to lbs conversion, divided by 4 corners
    
    for i in range(N):
        # Simplified load transfer calculation using vehicle config
        lat_transfer = A_lat_g[i] * vehicle_config['mass'] * 0.224809 * 0.3  # Lateral load transfer
        long_transfer = A_long_g[i] * vehicle_config['mass'] * 0.224809 * 0.2  # Longitudinal load transfer
        
        # Calculate individual corner loads
        loads['FL'][i] = base_load - lat_transfer + long_transfer
        loads['FR'][i] = base_load + lat_transfer + long_transfer
        loads['RL'][i] = base_load - lat_transfer - long_transfer
        loads['RR'][i] = base_load + lat_transfer - long_transfer
    
    return loads


def calculate_roll_angle(A_lat_g, vehicle_config):
    """
    Calculate vehicle body roll angle during cornering.
    
    Parameters:
    -----------
    A_lat_g : np.ndarray
        Lateral acceleration in g-force
    vehicle_config : dict
        Vehicle configuration parameters
        
    Returns:
    --------
    np.ndarray
        Roll angle in degrees
    """
    # Vehicle parameters from config (convert to imperial units for consistency with MATLAB)
    W = vehicle_config['weight'] * 0.224809  # N to lbs
    CG_z = vehicle_config['cg_height'] * 39.3701  # m to inches
    RC_f = vehicle_config['roll_center_front'] * 39.3701  # m to inches
    RC_r = vehicle_config['roll_center_rear'] * 39.3701  # m to inches
    wb = vehicle_config['wheelbase'] * 39.3701  # m to inches
    CG_x = vehicle_config['cg_x'] * 39.3701  # m to inches
    a = CG_x  # Distance from front axle to CG [in]
    b = wb - a  # Distance from rear axle to CG [in]
    
    H = (CG_z - ((RC_r-RC_f)/wb)*b - RC_r)/12
    
    # Axle Roll Stiffness from vehicle config (convert from metric if needed)
    Kphi_f_tot = vehicle_config['roll_stiffness_front']  # ft-lb/rad
    Kphi_r_tot = vehicle_config['roll_stiffness_rear']   # ft-lb/rad
    
    # Convert to imperial units if needed
    if Kphi_f_tot < 1000:  # Likely in metric units (N-m/rad)
        Kphi_f_tot *= 0.737562  # Convert N-m/rad to ft-lb/rad
        Kphi_r_tot *= 0.737562
    
    # Calculate roll angle (matches MATLAB formula exactly)
    roll_angle = ((A_lat_g * W * H) / (Kphi_f_tot + Kphi_r_tot)) * (180/np.pi)
    
    return roll_angle


def calculate_signed_curvature(x_coords, y_coords):
    """
    Calculate signed curvature at each point using three-point method.
    
    Parameters:
    -----------
    x_coords : np.ndarray
        X coordinates along the path
    y_coords : np.ndarray
        Y coordinates along the path
        
    Returns:
    --------
    np.ndarray
        Signed curvature array (positive = right turn, negative = left turn)
    """
    n_points = len(x_coords)
    curvature = np.zeros(n_points)
    
    # Calculate curvature at each point (with sign for turn direction)
    for i in range(1, n_points-1):
        # Three-point curvature calculation with sign
        x1, y1 = x_coords[i-1], y_coords[i-1]
        x2, y2 = x_coords[i], y_coords[i]
        x3, y3 = x_coords[i+1], y_coords[i+1]
        
        # Calculate signed curvature using cross product
        dx1, dy1 = x2 - x1, y2 - y1
        dx2, dy2 = x3 - x2, y3 - y2
        
        # Cross product gives sign: positive = right turn, negative = left turn
        cross_product = dx1 * dy2 - dy1 * dx2
        
        # Magnitude calculation
        ds1 = np.sqrt(dx1**2 + dy1**2)
        ds2 = np.sqrt(dx2**2 + dy2**2)
        
        if ds1 > 1e-10 and ds2 > 1e-10:
            # Signed curvature
            curvature[i] = cross_product / (ds1 * ds2 * (ds1 + ds2))
        else:
            curvature[i] = 0
    
    return curvature


def calculate_velocity_from_curvature(curvature, vehicle_config):
    """
    Calculate maximum velocity at each point based on lateral acceleration limits.
    
    Parameters:
    -----------
    curvature : np.ndarray
        Curvature array (signed)
    vehicle_config : dict
        Vehicle configuration parameters
        
    Returns:
    --------
    np.ndarray
        Velocity array in m/s
    """
    n_points = len(curvature)
    velocity = np.zeros(n_points)
    
    # Vehicle parameters from configuration
    mu = vehicle_config['tire_params']['mu']  # Tire coefficient of friction
    g = vehicle_config['gravity']  # m/s^2
    
    # Maximum lateral acceleration based on tire grip
    max_lat_accel = mu * g  # m/s^2
    
    # Calculate maximum velocity for each corner based on lateral acceleration limit
    for i in range(n_points):
        if abs(curvature[i]) > 1e-6:  # Use absolute value for speed calculation
            # v = sqrt(a_lat / |curvature|) - speed depends on magnitude only
            max_velocity = np.sqrt(max_lat_accel / abs(curvature[i]))
            velocity[i] = min(max_velocity, vehicle_config['max_velocity'])  # Use config max velocity
        else:
            velocity[i] = vehicle_config['max_velocity']  # Use config max velocity
    
    return velocity


def apply_acceleration_and_braking_constraints(velocity, distance, vehicle_config, powertrain_config):
    """
    Apply realistic acceleration and braking constraints with powertrain limits.
    
    Parameters:
    -----------
    velocity : np.ndarray
        Initial velocity profile
    distance : np.ndarray
        Distance array along track
    vehicle_config : dict
        Vehicle configuration parameters
    powertrain_config : dict
        Powertrain configuration parameters
        
    Returns:
    --------
    np.ndarray
        Constrained velocity profile
    """
    n_points = len(velocity)
    velocity_smooth = velocity.copy()
    g = vehicle_config['gravity']
    mass_kg = vehicle_config['mass']
    
    # Smooth velocity profile (but preserve acceleration opportunities)
    window = 3  # Reduced window to preserve more detail
    for i in range(window, n_points-window):
        velocity_smooth[i] = np.mean(velocity[i-window:i+window+1])
    
    # Apply realistic acceleration and braking constraints with powertrain limits
    max_accel_base = 1.2 * g  # 1.2g traction-limited acceleration
    max_brake = -1.8 * g  # 1.8g braking limit
    
    # Convert hp to watts: 1 hp = 745.7 watts
    max_power_watts = 60 * 745.7  # Approximate power in watts
    
    # Forward pass: limit acceleration (including power limitations)
    for i in range(1, n_points):
        ds = distance[i] - distance[i-1] if distance[i] > distance[i-1] else 1.0
        if ds > 0:
            # Power-limited acceleration at higher speeds
            current_speed = velocity_smooth[i-1]
            if current_speed > 7.5:  # Above ~7.5 m/s, power becomes limiting
                power_limited_accel = max_power_watts / current_speed / mass_kg  # Force = Power/Speed, a = F/m
                max_accel = min(max_accel_base, power_limited_accel)
            else:
                max_accel = max_accel_base
                
            # Calculate max velocity based on acceleration limit
            v_max_accel = np.sqrt(velocity_smooth[i-1]**2 + 2 * max_accel * ds)
            velocity_smooth[i] = min(velocity_smooth[i], v_max_accel)
    
    # Backward pass: limit braking
    for i in range(n_points-2, -1, -1):
        ds = distance[i+1] - distance[i] if distance[i+1] > distance[i] else 1.0
        if ds > 0:
            # Calculate max velocity based on braking limit
            v_max_brake = np.sqrt(velocity_smooth[i+1]**2 - 2 * max_brake * ds)
            velocity_smooth[i] = min(velocity_smooth[i], v_max_brake)
    
    return velocity_smooth


def calculate_longitudinal_acceleration(velocity, distance, vehicle_config):
    """
    Calculate longitudinal acceleration from velocity and distance data.
    
    Parameters:
    -----------
    velocity : np.ndarray
        Velocity array in m/s
    distance : np.ndarray
        Distance array in meters
    vehicle_config : dict
        Vehicle configuration parameters
        
    Returns:
    --------
    np.ndarray
        Longitudinal acceleration in g-force
    """
    n_points = len(velocity)
    acceleration = np.zeros(n_points)
    g = vehicle_config['gravity']
    
    # Calculate longitudinal acceleration using distance-based method
    for i in range(1, n_points-1):
        # Use actual distance and velocity for acceleration calculation
        ds_back = distance[i] - distance[i-1]
        ds_forward = distance[i+1] - distance[i]
        
        if ds_back > 0 and ds_forward > 0 and velocity[i] > 0:
            # Time between points based on velocity
            dt_back = ds_back / velocity[i]
            dt_forward = ds_forward / velocity[i]
            dt_total = dt_back + dt_forward
            
            if dt_total > 1e-6:
                # Central difference using actual time steps
                acceleration[i] = (velocity[i+1] - velocity[i-1]) / dt_total / g  # Convert to g's
                
                # Alternative: use kinematic equation a = v*dv/ds
                dv = velocity[i+1] - velocity[i-1]
                ds_avg = (ds_back + ds_forward) / 2
                if ds_avg > 0:
                    accel_kinematic = velocity[i] * dv / ds_avg / g
                    # Use the more conservative (smaller magnitude) value
                    if abs(accel_kinematic) < abs(acceleration[i]):
                        acceleration[i] = accel_kinematic
    
    return acceleration


def calculate_lateral_acceleration_from_velocity(velocity, curvature, vehicle_config):
    """
    Calculate lateral acceleration from velocity and curvature.
    
    Parameters:
    -----------
    velocity : np.ndarray
        Velocity array in m/s
    curvature : np.ndarray
        Signed curvature array
    vehicle_config : dict
        Vehicle configuration parameters
        
    Returns:
    --------
    np.ndarray
        Lateral acceleration in g-force (signed)
    """
    n_points = len(velocity)
    lateral_accel = np.zeros(n_points)
    g = vehicle_config['gravity']
    
    # Calculate lateral acceleration (with proper sign)
    for i in range(n_points):
        if velocity[i] > 0:
            # Signed lateral acceleration: positive = right turn, negative = left turn
            lateral_accel[i] = (velocity[i]**2 * curvature[i]) / g  # Convert to g's
        else:
            lateral_accel[i] = 0
    
    return lateral_accel


def apply_realistic_limits_and_noise(acceleration, lateral_accel):
    """
    Apply realistic limits and add noise to acceleration data.
    
    Parameters:
    -----------
    acceleration : np.ndarray
        Longitudinal acceleration in g-force
    lateral_accel : np.ndarray
        Lateral acceleration in g-force
        
    Returns:
    --------
    tuple
        (constrained_longitudinal_accel, constrained_lateral_accel)
    """
    # Apply realistic limits (preserve sign)
    acceleration = np.clip(acceleration, -1.8, 1.2)  # Typical FSAE limits
    lateral_accel = np.clip(lateral_accel, -1.8, 1.8)  # Allow negative lateral acceleration
    
    # Add some realistic noise and variation
    acceleration += np.random.normal(0, 0.05, len(acceleration))
    lateral_accel += np.random.normal(0, 0.02, len(lateral_accel))
    
    return acceleration, lateral_accel


def calculate_distance_array(X_racing, Y_racing):
    """
    Calculate cumulative distance array from racing line coordinates.
    
    Parameters:
    -----------
    X_racing, Y_racing : arrays
        Racing line coordinates
        
    Returns:
    --------
    np.ndarray : cumulative distance array
    """
    # Calculate distances between points
    distances = np.zeros(len(X_racing))
    for i in range(1, len(X_racing)):
        dx = X_racing[i] - X_racing[i-1]
        dy = Y_racing[i] - Y_racing[i-1]
        distances[i] = np.sqrt(dx**2 + dy**2)
    
    # Return cumulative distance
    return np.cumsum(distances)


def calculate_comprehensive_lap_physics(X_racing, Y_racing, distance, vehicle_config, powertrain_config):
    """
    Comprehensive physics calculation for lap simulation.
    
    This function combines all the physics calculations that were previously in lap_information().
    
    Parameters:
    -----------
    x_coords : np.ndarray
        X coordinates along racing line
    y_coords : np.ndarray
        Y coordinates along racing line
    distance : np.ndarray
        Distance array along track
    vehicle_config : dict
        Vehicle configuration parameters
    powertrain_config : dict
        Powertrain configuration parameters
        
    Returns:
    --------
    tuple
        (longitudinal_accel, lateral_accel, distance) all in appropriate units
    """
    # Step 1: Calculate signed curvature
    curvature = calculate_signed_curvature(X_racing, Y_racing)
    
    # Step 2: Calculate maximum velocity from curvature
    velocity = calculate_velocity_from_curvature(curvature, vehicle_config)
    
    # Step 3: Apply acceleration and braking constraints
    velocity = apply_acceleration_and_braking_constraints(velocity, distance, vehicle_config, powertrain_config)
    
    # Step 4: Calculate longitudinal acceleration
    longitudinal_accel = calculate_longitudinal_acceleration(velocity, distance, vehicle_config)
    
    # Step 5: Calculate lateral acceleration
    lateral_accel = calculate_lateral_acceleration_from_velocity(velocity, curvature, vehicle_config)
    
    # Step 6: Apply realistic limits and add noise
    longitudinal_accel, lateral_accel = apply_realistic_limits_and_noise(longitudinal_accel, lateral_accel)
    
    return longitudinal_accel, lateral_accel, distance
