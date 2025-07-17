"""
Racing Physics and Velocity Calculation Module
==============================================

Physics calculations following MATLAB Lap_Sim methodology.
Calculates realistic velocities based on vehicle dynamics, track geometry, and racing physics.
"""

import numpy as np
from scipy.ndimage import gaussian_filter1d


def calculate_realistic_velocities(x_coords, y_coords, track_type):
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
        
    Returns:
    --------
    np.ndarray
        Velocity array in mph
    """
    n_points = len(x_coords)
    velocities = np.zeros(n_points)
    
    # Get vehicle parameters for the specific track type
    vehicle_params = get_vehicle_parameters(track_type)
    
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


def get_vehicle_parameters(track_type):
    """
    Get vehicle parameters based on track type.
    
    Parameters:
    -----------
    track_type : str
        Type of track ('endurance' or 'autocross')
        
    Returns:
    --------
    dict
        Vehicle parameter dictionary
    """
    # Base vehicle parameters (realistic FSAE values)
    vehicle_params = {
        'mass': 617.4,  # lbs (280 kg)
        'cg_height': 0.88,  # ft (0.267 m)
        'wheelbase': 5.09,  # ft (1.55 m)
        'track_width': 4.0,  # ft (1.22 m)
        'tire_mu': 1.5,  # realistic peak friction coefficient for FSAE tires
        'aero_cl': 1.5,  # reduced downforce coefficient
        'aero_cd': 1.2,  # realistic drag coefficient
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
            
            # Calculate downforce at estimated speed (iterative)
            v_est = vehicle_params['base_speed'] * 5280 / 3600  # convert to ft/s for physics
            
            # Downforce increases effective grip
            downforce = vehicle_params['aero_cl'] * v_est**2
            effective_weight = vehicle_params['mass'] + downforce
            
            # Maximum lateral acceleration from tire grip
            max_lat_g = vehicle_params['max_lat_accel'] * vehicle_params['corner_factor']
            max_lat_accel = max_lat_g * 32.2  # ft/s²
            
            # Scale by effective weight (more downforce = higher cornering speed)
            weight_factor = effective_weight / vehicle_params['mass']
            scaled_lat_accel = max_lat_accel * weight_factor
            
            # v = sqrt(a * r) for cornering
            max_corner_speed = np.sqrt(scaled_lat_accel * radius)
            max_corner_speed_mph = max_corner_speed * 3600 / 5280  # convert to mph
            
            max_cornering_speeds[i] = max_corner_speed_mph
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
            
            # Account for drag (less aggressive drag effect)
            drag_force = vehicle_params['aero_cd'] * v_prev**2 * 0.5  # Reduce drag impact
            drag_accel = drag_force / vehicle_params['mass'] * 32.2
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
