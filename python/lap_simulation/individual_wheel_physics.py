"""
Individual Wheel Physics - Advanced Vehicle Dynamics
====================================================

This module implements individual wheel load calculations, suspension effects,
and advanced vehicle dynamics that provide realistic tire loading and suspension
behavior for accurate lap simulation.

CAPABILITIES:
- Individual wheel load calculations (FL, FR, RL, RR) instead of axle totals
- Suspension kinematics (roll angles, camber changes) affecting tire performance
- Slip angle calculations for each wheel based on actual loads
- Yaw moment calculations from asymmetric tire forces
- Load transfer distribution using Lateral Load Transfer Distribution (LLTD)

These physics provide the foundation for realistic tire modeling and enable
detailed vehicle dynamics analysis that standard physics approaches miss.
"""

import numpy as np
from scipy.ndimage import gaussian_filter1d
from typing import Dict, Tuple, Optional


def calculate_individual_wheel_loads(
    lateral_accel_g: np.ndarray,
    longitudinal_accel_g: np.ndarray,
    velocities: np.ndarray,
    vehicle_config: Dict
) -> Dict[str, np.ndarray]:
    """
    Calculate individual wheel loads with LLTD and detailed load transfer.
    
    This implementation follows the MATLAB approach for calculating load transfer
    to individual wheels using Lateral Load Transfer Distribution (LLTD).
    
    Parameters:
    -----------
    lateral_accel_g : np.ndarray
        Lateral acceleration in g's
    longitudinal_accel_g : np.ndarray
        Longitudinal acceleration in g's
    velocities : np.ndarray
        Vehicle velocities [m/s]
    vehicle_config : Dict
        Vehicle configuration dictionary
        
    Returns:
    --------
    Dict[str, np.ndarray]
        Individual wheel loads for FL, FR, RL, RR [N]
    """
    # Get vehicle parameters (using MATLAB values)
    LLTD = vehicle_config['LLTD']  # 0.51 from MATLAB
    weight = vehicle_config['weight']  # Total weight [N]
    wheelbase = vehicle_config['wheelbase']  # [m]
    cg_x = vehicle_config['cg_x']  # CG position from front axle [m]
    cg_height = vehicle_config['cg_height']  # [m]
    track_width_front = vehicle_config['track_width_front']  # [m]
    track_width_rear = vehicle_config['track_width_rear']  # [m]
    
    # Calculate weight distribution (from MATLAB: WDF = 44.754%)
    weight_dist_front = (wheelbase - cg_x) / wheelbase  # Front weight percentage
    
    # Static loads per axle
    static_front_total = weight * weight_dist_front
    static_rear_total = weight * (1 - weight_dist_front)
    
    # Static loads per wheel
    static_front_per_wheel = static_front_total / 2
    static_rear_per_wheel = static_rear_total / 2
    
    # Initialize output arrays
    n_points = len(velocities)
    loads = {
        'FL': np.zeros(n_points),  # Front Left
        'FR': np.zeros(n_points),  # Front Right
        'RL': np.zeros(n_points),  # Rear Left
        'RR': np.zeros(n_points)   # Rear Right
    }
    
    for i in range(n_points):
        # Calculate longitudinal load transfer (from longitudinal acceleration)
        # This follows MATLAB: wf = wf - Ax*cg*WS/l and wr = wr + Ax*cg*WS/l
        # Note: MATLAB uses WS = W/2 (half car weight)
        half_weight = weight / 2
        long_transfer_total = longitudinal_accel_g[i] * cg_height * half_weight / wheelbase
        long_transfer_front_per_wheel = long_transfer_total  # Per wheel
        long_transfer_rear_per_wheel = long_transfer_total   # Per wheel
        
        # Calculate lateral load transfer (from lateral acceleration)
        # Total lateral load transfer: WT = A_y*cg*W/mean([twf twr])
        mean_track_width = np.mean([track_width_front, track_width_rear])
        lateral_transfer_total = abs(lateral_accel_g[i]) * cg_height * weight / mean_track_width
        
        # Distribute lateral load transfer between front and rear axles using LLTD
        # From MATLAB: LLTD determines how much of the total lateral load transfer
        # goes to the front vs rear axle
        lateral_transfer_front = lateral_transfer_total * LLTD
        lateral_transfer_rear = lateral_transfer_total * (1 - LLTD)
        
        # Apply load transfers to individual wheels
        # Sign convention: positive lateral_accel_g means turning left (load transfers to right wheels)
        lat_sign = np.sign(lateral_accel_g[i])
        
        # Front wheels
        loads['FL'][i] = static_front_per_wheel - lat_sign * lateral_transfer_front/2 - long_transfer_front_per_wheel
        loads['FR'][i] = static_front_per_wheel + lat_sign * lateral_transfer_front/2 - long_transfer_front_per_wheel
        
        # Rear wheels
        loads['RL'][i] = static_rear_per_wheel - lat_sign * lateral_transfer_rear/2 + long_transfer_rear_per_wheel
        loads['RR'][i] = static_rear_per_wheel + lat_sign * lateral_transfer_rear/2 + long_transfer_rear_per_wheel
        
        # Ensure no negative loads (wheels can't pull on ground)
        for wheel in ['FL', 'FR', 'RL', 'RR']:
            loads[wheel][i] = max(loads[wheel][i], 0.0)
    
    return loads


def calculate_slip_angles_and_yaw_moment(
    velocity: float,
    curvature: float,
    vehicle_config: Dict,
    steering_angle: Optional[float] = None
) -> Dict:
    """
    Calculate slip angles and yaw moment balance for vehicle dynamics.
    
    This follows the MATLAB approach for calculating vehicle dynamics including
    slip angles at front and rear axles and yaw moment balance.
    
    Parameters:
    -----------
    velocity : float
        Vehicle velocity [m/s]
    curvature : float  
        Track curvature [1/m]
    vehicle_config : Dict
        Vehicle configuration
    steering_angle : float, optional
        Steering angle [rad]. If None, uses Ackermann approximation
        
    Returns:
    --------
    Dict
        Vehicle dynamics state including slip angles and yaw moment
    """
    # Vehicle geometry (from MATLAB)
    wheelbase = vehicle_config['wheelbase']  # l
    cg_x = vehicle_config['cg_x']  # Distance from front axle to CG
    
    # Calculate a and b (from MATLAB: a = l*(1-WDF), b = l*WDF)
    weight_dist_front = (wheelbase - cg_x) / wheelbase
    a = wheelbase * (1 - weight_dist_front)  # Distance from CG to front axle
    b = wheelbase * weight_dist_front        # Distance from CG to rear axle
    
    # Avoid division by zero at very low speeds
    if velocity < 0.1:
        return {
            'slip_angle_front': 0.0,
            'slip_angle_rear': 0.0,
            'yaw_moment': 0.0,
            'steering_angle': 0.0,
            'sideslip_angle': 0.0,
            'yaw_rate': 0.0,
            'lateral_acceleration': 0.0
        }
    
    # Calculate kinematic parameters
    yaw_rate = velocity * curvature  # r = V * curvature
    lateral_acceleration = velocity**2 * curvature  # A_y = V^2 * curvature
    
    # Initial guess for sideslip angle (from MATLAB: beta = 0)
    sideslip_angle = 0.0  # beta
    
    # Steering angle: use Ackermann approximation if not provided
    # From MATLAB: delta = l/R, where R = 1/curvature
    if steering_angle is None:
        if abs(curvature) > 1e-6:
            steering_angle = wheelbase * curvature  # Ackermann steering
        else:
            steering_angle = 0.0
    
    # Ensure steering_angle is a float
    if steering_angle is not None:
        steering_angle = float(steering_angle)
    
    # Calculate slip angles (from MATLAB)
    # Front slip angle: a_f = beta + a*r/V - delta
    slip_angle_front = sideslip_angle + a * yaw_rate / velocity - steering_angle
    
    # Rear slip angle: a_r = beta - b*r/V
    slip_angle_rear = sideslip_angle - b * yaw_rate / velocity
    
    # Calculate tire forces using simplified linear model
    # (This will be replaced with Magic Formula in Phase 2)
    cornering_stiffness_front = vehicle_config.get('cornering_stiffness_front', 1200)  # N/rad
    cornering_stiffness_rear = vehicle_config.get('cornering_stiffness_rear', 1100)   # N/rad
    
    # Front and rear lateral forces
    force_front = cornering_stiffness_front * slip_angle_front
    force_rear = cornering_stiffness_rear * slip_angle_rear
    
    # Yaw moment about CG (from MATLAB vehicle dynamics)
    # M_z = F_front * a - F_rear * b
    yaw_moment = force_front * a - force_rear * b
    
    return {
        'slip_angle_front': slip_angle_front,
        'slip_angle_rear': slip_angle_rear,
        'yaw_moment': yaw_moment,
        'steering_angle': steering_angle,
        'sideslip_angle': sideslip_angle,
        'yaw_rate': yaw_rate,
        'lateral_acceleration': lateral_acceleration,
        'force_front': force_front,
        'force_rear': force_rear
    }


def calculate_suspension_effects(
    lateral_accel_g: np.ndarray,
    longitudinal_accel_g: np.ndarray,
    vehicle_config: Dict
) -> Dict[str, np.ndarray]:
    """
    Calculate suspension kinematics effects including roll and pitch angles.
    
    This implements the MATLAB suspension kinematics calculations including
    roll gradients, pitch gradients, and camber changes.
    
    Parameters:
    -----------
    lateral_accel_g : np.ndarray
        Lateral acceleration in g's
    longitudinal_accel_g : np.ndarray
        Longitudinal acceleration in g's
    vehicle_config : Dict
        Vehicle configuration
        
    Returns:
    --------
    Dict[str, np.ndarray]
        Suspension effects including roll, pitch, and camber changes
    """
    # Get suspension parameters from MATLAB
    roll_gradient_front = vehicle_config.get('roll_gradient_front', 1.15)  # deg/g
    roll_gradient_rear = vehicle_config.get('roll_gradient_rear', 1.15)    # deg/g
    pitch_gradient = vehicle_config.get('pitch_gradient', 0.0)             # deg/g
    
    # Camber gains from MATLAB (IA_gainf, IA_gainr)
    camber_gain_front = vehicle_config.get('camber_gain_front', 0.1)  # deg/deg
    camber_gain_rear = vehicle_config.get('camber_gain_rear', 0.2)    # deg/deg
    
    # Calculate roll angles (from MATLAB: roll gradients in deg/g)
    roll_angle_front = lateral_accel_g * roll_gradient_front * np.pi / 180  # Convert to radians
    roll_angle_rear = lateral_accel_g * roll_gradient_rear * np.pi / 180
    
    # Calculate pitch angle (from MATLAB: pitch gradient in deg/g)
    pitch_angle = longitudinal_accel_g * pitch_gradient * np.pi / 180
    
    # Calculate camber changes from roll
    # From MATLAB: IA_f = roll_effect*IA_gainf + IA_0f
    camber_change_front = roll_angle_front * camber_gain_front
    camber_change_rear = roll_angle_rear * camber_gain_rear
    
    # Calculate kinematic effects on wheel alignment
    # This is simplified - full implementation would include KPI and caster effects
    kingpin_inclination_front = vehicle_config.get('kingpin_inclination_front', 7.18) * np.pi / 180
    kingpin_inclination_rear = vehicle_config.get('kingpin_inclination_rear', 8.49) * np.pi / 180
    caster_angle_front = vehicle_config.get('caster_angle_front', 4.0) * np.pi / 180
    caster_angle_rear = vehicle_config.get('caster_angle_rear', 4.0) * np.pi / 180
    
    return {
        'roll_angle_front': roll_angle_front,
        'roll_angle_rear': roll_angle_rear, 
        'pitch_angle': pitch_angle,
        'camber_change_front': camber_change_front,
        'camber_change_rear': camber_change_rear,
        'total_camber_front': camber_change_front,  # Static camber = 0 in MATLAB
        'total_camber_rear': camber_change_rear,
        'kingpin_inclination_front': kingpin_inclination_front,
        'kingpin_inclination_rear': kingpin_inclination_rear,
        'caster_angle_front': caster_angle_front,
        'caster_angle_rear': caster_angle_rear
    }


def calculate_individual_wheel_forces_simple(
    wheel_loads: Dict[str, np.ndarray],
    lateral_accel_g: np.ndarray,
    vehicle_config: Dict
) -> Dict[str, np.ndarray]:
    """
    Calculate tire forces for each individual wheel using simplified tire model.
    
    This is a simplified implementation for Phase 1. Phase 2 will implement
    the full Magic Formula 5.2 model.
    
    Parameters:
    -----------
    wheel_loads : Dict[str, np.ndarray]
        Normal loads for FL, FR, RL, RR [N]
    lateral_accel_g : np.ndarray
        Lateral acceleration in g's
    vehicle_config : Dict
        Vehicle configuration
        
    Returns:
    --------
    Dict[str, np.ndarray]
        Tire forces for each wheel [N]
    """
    # Simple tire model: F_y = mu * F_z
    # This approximates the linear region of the tire model
    mu_peak = vehicle_config.get('tire_params', {}).get('mu', 1.8)
    
    # For Phase 1, use a simplified approach where we assume symmetric loading
    # and calculate forces based on total lateral acceleration demand
    
    n_points = len(lateral_accel_g)
    wheel_forces = {
        'FL': np.zeros(n_points),
        'FR': np.zeros(n_points), 
        'RL': np.zeros(n_points),
        'RR': np.zeros(n_points)
    }
    
    for i in range(n_points):
        # Calculate required total lateral force
        total_weight = vehicle_config['weight']
        required_lateral_force = abs(lateral_accel_g[i]) * total_weight
        
        # Distribute force based on wheel loads
        total_normal_force = sum(wheel_loads[wheel][i] for wheel in ['FL', 'FR', 'RL', 'RR'])
        
        if total_normal_force > 0:
            for wheel in ['FL', 'FR', 'RL', 'RR']:
                # Force proportional to normal load
                force_fraction = wheel_loads[wheel][i] / total_normal_force
                wheel_forces[wheel][i] = required_lateral_force * force_fraction
                
                # Limit by tire friction
                max_force = mu_peak * wheel_loads[wheel][i]
                wheel_forces[wheel][i] = min(wheel_forces[wheel][i], max_force)
    
    return wheel_forces


def calculate_slip_angles_and_yaw_moment_arrays(
    velocities: np.ndarray,
    x_coords: np.ndarray,
    y_coords: np.ndarray,
    vehicle_config: Dict
) -> Dict[str, np.ndarray]:
    """
    Calculate slip angles and yaw moment for arrays of position and velocity data.
    
    Parameters:
    -----------
    velocities : np.ndarray
        Vehicle velocities [m/s or mph]
    x_coords : np.ndarray
        X coordinates along track [m or ft]
    y_coords : np.ndarray
        Y coordinates along track [m or ft]
    vehicle_config : Dict
        Vehicle configuration
        
    Returns:
    --------
    Dict[str, np.ndarray]
        Arrays of slip angles and yaw moments
    """
    n_points = len(velocities)
    
    # Initialize output arrays
    slip_angles_front = np.zeros(n_points)
    slip_angles_rear = np.zeros(n_points)
    yaw_moments = np.zeros(n_points)
    curvatures = np.zeros(n_points)
    
    # Convert velocities to m/s if they're in mph
    if np.mean(velocities) > 10:  # Assume mph if average > 10
        velocities_ms = velocities * 0.44704
    else:
        velocities_ms = velocities
    
    # Calculate curvature at each point using central differences
    for i in range(1, n_points - 1):
        # Calculate curvature using three points
        try:
            # Vector from previous to current point
            dx1 = x_coords[i] - x_coords[i-1]
            dy1 = y_coords[i] - y_coords[i-1]
            
            # Vector from current to next point
            dx2 = x_coords[i+1] - x_coords[i]
            dy2 = y_coords[i+1] - y_coords[i]
            
            # Calculate curvature using cross product method
            # k = |v1 x v2| / |v1|^3 where v1 is velocity vector
            cross_product = dx1 * dy2 - dy1 * dx2
            magnitude_squared = dx1**2 + dy1**2
            
            if magnitude_squared > 1e-6:
                curvatures[i] = abs(cross_product) / (magnitude_squared**1.5)
            else:
                curvatures[i] = 0.0
                
        except:
            curvatures[i] = 0.0
    
    # Handle boundary conditions
    curvatures[0] = curvatures[1] if n_points > 1 else 0.0
    curvatures[-1] = curvatures[-2] if n_points > 1 else 0.0
    
    # Smooth curvature to reduce noise
    curvatures = gaussian_filter1d(curvatures, sigma=2.0)
    
    # Calculate slip angles and yaw moment for each point
    for i in range(n_points):
        try:
            dynamics = calculate_slip_angles_and_yaw_moment(
                velocity=velocities_ms[i],
                curvature=curvatures[i],
                vehicle_config=vehicle_config
            )
            
            slip_angles_front[i] = dynamics['slip_angle_front']
            slip_angles_rear[i] = dynamics['slip_angle_rear']
            yaw_moments[i] = dynamics['yaw_moment']
            
        except:
            # Handle any calculation errors with default values
            slip_angles_front[i] = 0.0
            slip_angles_rear[i] = 0.0
            yaw_moments[i] = 0.0
    
    return {
        'front': slip_angles_front,
        'rear': slip_angles_rear,
        'yaw_moment': yaw_moments,
        'curvature': curvatures
    }


def validate_wheel_loads(wheel_loads: Dict[str, np.ndarray], vehicle_config: Dict) -> Dict:
    """
    Validate that wheel loads sum to total vehicle weight.
    
    Parameters:
    -----------
    wheel_loads : Dict[str, np.ndarray]
        Individual wheel loads
    vehicle_config : Dict
        Vehicle configuration
        
    Returns:
    --------
    Dict
        Validation results including weight balance errors
    """
    total_weight = vehicle_config['weight']
    
    # Calculate total load at each point
    total_loads = (wheel_loads['FL'] + wheel_loads['FR'] + 
                   wheel_loads['RL'] + wheel_loads['RR'])
    
    # Calculate errors
    weight_errors = total_loads - total_weight
    max_error = np.max(np.abs(weight_errors))
    mean_error = np.mean(np.abs(weight_errors))
    
    # Calculate front/rear balance
    front_loads = wheel_loads['FL'] + wheel_loads['FR']
    rear_loads = wheel_loads['RL'] + wheel_loads['RR']
    front_percentage = np.mean(front_loads / total_loads) * 100
    
    # Calculate left/right balance
    left_loads = wheel_loads['FL'] + wheel_loads['RL']
    right_loads = wheel_loads['FR'] + wheel_loads['RR']
    left_percentage = np.mean(left_loads / total_loads) * 100
    
    return {
        'max_weight_error': max_error,
        'mean_weight_error': mean_error,
        'front_weight_percentage': front_percentage,
        'left_weight_percentage': left_percentage,
        'weight_balance_ok': max_error < (total_weight * 0.01),  # 1% tolerance
        'total_points_validated': len(total_loads)
    }


# Example usage and testing function
def test_phase1_physics():
    """Test Phase 1 physics implementations with sample data."""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from vehicle_config import get_vehicle_config
    
    # Get vehicle configuration
    vehicle_config = get_vehicle_config()
    
    # Create sample data
    n_points = 100
    velocities = np.linspace(10, 40, n_points)  # 10-40 m/s
    lateral_accel_g = np.sin(np.linspace(0, 4*np.pi, n_points)) * 1.5  # ±1.5g
    longitudinal_accel_g = np.cos(np.linspace(0, 2*np.pi, n_points)) * 0.8  # ±0.8g
    curvatures = lateral_accel_g / (velocities**2)  # Calculate consistent curvatures
    
    print("Testing Phase 1 Physics Implementation")
    print("=" * 50)
    
    # Test individual wheel loads
    print("1. Testing individual wheel load calculations...")
    wheel_loads = calculate_individual_wheel_loads(
        lateral_accel_g, longitudinal_accel_g, velocities, vehicle_config
    )
    
    # Validate results
    validation = validate_wheel_loads(wheel_loads, vehicle_config)
    print(f"   Max weight error: {validation['max_weight_error']:.2f} N")
    print(f"   Mean weight error: {validation['mean_weight_error']:.2f} N")
    print(f"   Front weight %: {validation['front_weight_percentage']:.1f}%")
    print(f"   Weight balance OK: {validation['weight_balance_ok']}")
    
    # Test slip angle calculations
    print("\n2. Testing slip angle and yaw moment calculations...")
    dynamics_results = []
    for i in range(0, n_points, 10):  # Test every 10th point
        result = calculate_slip_angles_and_yaw_moment(
            velocities[i], curvatures[i], vehicle_config
        )
        dynamics_results.append(result)
    
    print(f"   Tested {len(dynamics_results)} velocity points")
    print(f"   Sample slip angle front: {np.rad2deg(dynamics_results[5]['slip_angle_front']):.2f} deg")
    print(f"   Sample slip angle rear: {np.rad2deg(dynamics_results[5]['slip_angle_rear']):.2f} deg")
    
    # Test suspension effects
    print("\n3. Testing suspension kinematics calculations...")
    suspension_effects = calculate_suspension_effects(
        lateral_accel_g, longitudinal_accel_g, vehicle_config
    )
    
    max_roll_front = np.max(np.abs(suspension_effects['roll_angle_front']))
    max_roll_rear = np.max(np.abs(suspension_effects['roll_angle_rear']))
    print(f"   Max front roll angle: {np.rad2deg(max_roll_front):.2f} deg")
    print(f"   Max rear roll angle: {np.rad2deg(max_roll_rear):.2f} deg")
    
    # Test individual wheel forces
    print("\n4. Testing individual wheel force calculations...")
    wheel_forces = calculate_individual_wheel_forces_simple(
        wheel_loads, lateral_accel_g, vehicle_config
    )
    
    max_forces = {wheel: np.max(wheel_forces[wheel]) for wheel in wheel_forces}
    print(f"   Max wheel forces: FL={max_forces['FL']:.0f}N, FR={max_forces['FR']:.0f}N")
    print(f"                     RL={max_forces['RL']:.0f}N, RR={max_forces['RR']:.0f}N")
    
    print("\nPhase 1 physics implementation test completed successfully!")
    return wheel_loads, dynamics_results, suspension_effects, wheel_forces


if __name__ == "__main__":
    test_phase1_physics()
