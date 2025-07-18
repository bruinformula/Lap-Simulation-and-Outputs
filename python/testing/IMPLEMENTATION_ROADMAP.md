# Implementation Roadmap: Adding Missing Physics Computations

## Overview

This document provides a structured roadmap for implementing the missing physics computations identified in `MISSING_PHYSICS_COMPUTATIONS.md`. The implementations are prioritized by impact on simulation accuracy and ease of implementation.

---

## Phase 1: High Priority - Core Vehicle Dynamics (Estimated: 4-6 weeks)

### 1.1 Individual Wheel Load and Force Calculations

#### Current State:
```python
# Only total axle loads calculated
loads['FL'][i] = front_total_per_wheel - lat_transfer_front - long_transfer_front
```

#### Target Implementation:
```python
def calculate_individual_wheel_loads(A_lat_g, A_long_g, velocities, vehicle_config):
    """
    Calculate individual wheel loads with LLTD and detailed load transfer.
    
    Returns:
    --------
    dict: Individual wheel loads for FL, FR, RL, RR
    """
    # Lateral Load Transfer Distribution (LLTD)
    LLTD = vehicle_config.get('LLTD', 0.58)  # Typical FSAE value
    
    for i in range(len(velocities)):
        # Total lateral load transfer
        WT = A_lat_g[i] * vehicle_config['cg_height'] * vehicle_config['weight'] / \
             np.mean([vehicle_config['track_width_front'], vehicle_config['track_width_rear']])
        
        # Distribute between front and rear based on LLTD
        WTF = WT * LLTD
        WTR = WT * (1 - LLTD)
        
        # Individual wheel loads
        loads['FL'][i] = static_front_per_wheel - WTF - long_transfer_front
        loads['FR'][i] = static_front_per_wheel + WTF - long_transfer_front
        loads['RL'][i] = static_rear_per_wheel - WTR + long_transfer_rear
        loads['RR'][i] = static_rear_per_wheel + WTR + long_transfer_rear
    
    return loads
```

#### Required Vehicle Parameters:
```python
# Add to vehicle_config.py
LATERAL_LOAD_TRANSFER_DISTRIBUTION = 0.58  # LLTD (0-1, typical FSAE: 0.55-0.65)
ROLL_GRADIENT_FRONT = 3.5  # deg/g
ROLL_GRADIENT_REAR = 2.8   # deg/g
PITCH_GRADIENT = 2.0       # deg/g
```

### 1.2 Yaw Moment Balance and Slip Angle Calculations

#### Target Implementation:
```python
def calculate_slip_angles_and_yaw_moment(velocity, curvature, vehicle_config):
    """
    Calculate slip angles and yaw moment balance for vehicle dynamics.
    
    Parameters:
    -----------
    velocity : float
        Vehicle velocity [m/s]
    curvature : float  
        Track curvature [1/m]
    vehicle_config : dict
        Vehicle configuration
        
    Returns:
    --------
    dict: slip_angle_front, slip_angle_rear, yaw_moment, steering_angle
    """
    # Vehicle geometry
    wheelbase = vehicle_config['wheelbase']
    a = vehicle_config['cg_x']  # Distance from front axle to CG
    b = wheelbase - a           # Distance from rear axle to CG
    
    # Yaw rate from kinematics
    yaw_rate = velocity * curvature
    
    # Lateral acceleration
    lateral_accel = velocity**2 * curvature
    
    # Sideslip angle (initial guess)
    beta = 0.0  # Will be iterated
    
    # Steering angle (initial guess) 
    delta = wheelbase * curvature  # Ackermann approximation
    
    # Slip angles
    slip_angle_front = beta + a * yaw_rate / velocity - delta
    slip_angle_rear = beta - b * yaw_rate / velocity
    
    # Calculate tire forces (simplified - will integrate with MF5.2 later)
    cornering_stiffness_front = vehicle_config.get('cornering_stiffness_front', 1200)  # N/rad
    cornering_stiffness_rear = vehicle_config.get('cornering_stiffness_rear', 1100)   # N/rad
    
    F_front = cornering_stiffness_front * slip_angle_front
    F_rear = cornering_stiffness_rear * slip_angle_rear
    
    # Yaw moment about CG
    yaw_moment = F_front * a - F_rear * b
    
    return {
        'slip_angle_front': slip_angle_front,
        'slip_angle_rear': slip_angle_rear,
        'yaw_moment': yaw_moment,
        'steering_angle': delta,
        'sideslip_angle': beta
    }
```

### 1.3 Basic Suspension Kinematics

#### Target Implementation:
```python
def calculate_suspension_effects(A_lat_g, A_long_g, vehicle_config):
    """
    Calculate suspension kinematics effects including roll and pitch angles.
    
    Returns:
    --------
    dict: roll_angle_front, roll_angle_rear, pitch_angle, camber_changes
    """
    # Roll gradients from config
    rg_front = vehicle_config.get('roll_gradient_front', 3.5)  # deg/g
    rg_rear = vehicle_config.get('roll_gradient_rear', 2.8)    # deg/g
    pg = vehicle_config.get('pitch_gradient', 2.0)            # deg/g
    
    # Roll angles
    roll_angle_front = A_lat_g * rg_front * np.pi / 180  # Convert to radians
    roll_angle_rear = A_lat_g * rg_rear * np.pi / 180
    
    # Pitch angle
    pitch_angle = A_long_g * pg * np.pi / 180
    
    # Camber changes from roll (simplified)
    camber_gain_front = vehicle_config.get('camber_gain_front', 1.0)  # deg/deg
    camber_gain_rear = vehicle_config.get('camber_gain_rear', 0.8)    # deg/deg
    
    camber_change_front = roll_angle_front * camber_gain_front
    camber_change_rear = roll_angle_rear * camber_gain_rear
    
    return {
        'roll_angle_front': roll_angle_front,
        'roll_angle_rear': roll_angle_rear, 
        'pitch_angle': pitch_angle,
        'camber_change_front': camber_change_front,
        'camber_change_rear': camber_change_rear
    }
```

---

## Phase 2: Medium Priority - Tire Model Integration (Estimated: 6-8 weeks)

### 2.1 Complete Magic Formula 5.2 Implementation

#### Target Implementation:
```python
class MagicFormula52:
    """Complete Magic Formula 5.2 tire model implementation."""
    
    def __init__(self, tire_params):
        """Initialize with full parameter set."""
        # 18 Magic Formula coefficients
        self.coefficients = {
            'PCy1': tire_params.get('PCy1', 1.0),
            'PDy1': tire_params.get('PDy1', 1.0),
            'PDy2': tire_params.get('PDy2', 0.0),
            'PDy3': tire_params.get('PDy3', 0.0),
            'PEy1': tire_params.get('PEy1', 0.0),
            'PEy2': tire_params.get('PEy2', 0.0),
            'PEy3': tire_params.get('PEy3', 0.0),
            'PEy4': tire_params.get('PEy4', 0.0),
            'PKy1': tire_params.get('PKy1', -15.0),
            'PKy2': tire_params.get('PKy2', 2.0),
            'PKy3': tire_params.get('PKy3', 0.3),
            'PHy1': tire_params.get('PHy1', 0.0),
            'PHy2': tire_params.get('PHy2', 0.0),
            'PHy3': tire_params.get('PHy3', 0.0),
            'PVy1': tire_params.get('PVy1', 0.0),
            'PVy2': tire_params.get('PVy2', 0.0),
            'PVy3': tire_params.get('PVy3', 0.0),
            'PVy4': tire_params.get('PVy4', 0.0)
        }
        
        # Global scaling factors
        self.scaling = {
            'FZ0': tire_params.get('FZ0', 220.0),
            'LFZO': tire_params.get('LFZO', 1.0),
            'LCY': tire_params.get('LCY', 1.0),
            'LMUY': tire_params.get('LMUY', 1.0),
            'LEY': tire_params.get('LEY', 1.0),
            'LKY': tire_params.get('LKY', 1.0),
            'LHY': tire_params.get('LHY', 1.0),
            'LVY': tire_params.get('LVY', 1.0),
            'LGAY': tire_params.get('LGAY', 1.0)
        }
    
    def calculate_lateral_force(self, slip_angle, normal_force, camber_angle):
        """
        Calculate lateral force using full MF5.2 equations.
        
        Parameters:
        -----------
        slip_angle : float
            Slip angle [rad]
        normal_force : float
            Normal force [N]
        camber_angle : float
            Camber angle [rad]
            
        Returns:
        --------
        float: Lateral force [N]
        """
        # Convert inputs
        ALPHA = slip_angle
        Fz = abs(normal_force)
        GAMMA = camber_angle
        
        # Get parameters
        FZ0 = self.scaling['FZ0']
        LFZO = self.scaling['LFZO']
        LCY = self.scaling['LCY']
        LMUY = self.scaling['LMUY']
        LEY = self.scaling['LEY']
        LKY = self.scaling['LKY']
        LHY = self.scaling['LHY']
        LVY = self.scaling['LVY']
        LGAY = self.scaling['LGAY']
        
        # Calculate derived parameters
        GAMMAy = GAMMA * LGAY
        Fz0PR = FZ0 * LFZO
        DFz = (Fz - Fz0PR) / Fz0PR
        
        # Shape factor
        Cy = self.coefficients['PCy1'] * LCY
        
        # Peak factor
        MUy = (self.coefficients['PDy1'] + self.coefficients['PDy2'] * DFz) * \
              (1.0 - self.coefficients['PDy3'] * GAMMAy**2) * LMUY
        Dy = MUy * Fz
        
        # Stiffness factor
        KY = self.coefficients['PKy1'] * FZ0 * \
             np.sin(2.0 * np.arctan(Fz / (self.coefficients['PKy2'] * FZ0 * LFZO))) * \
             (1.0 - self.coefficients['PKy3'] * abs(GAMMAy)) * LFZO * LKY
        By = KY / (Cy * Dy)
        
        # Curvature factor
        Ey = (self.coefficients['PEy1'] + self.coefficients['PEy2'] * DFz) * \
             (1.0 - (self.coefficients['PEy3'] + self.coefficients['PEy4'] * GAMMAy) * np.sign(ALPHA)) * LEY
        
        # Horizontal shift
        SHy = (self.coefficients['PHy1'] + self.coefficients['PHy2'] * DFz) * LHY + \
              self.coefficients['PHy3'] * GAMMAy
        ALPHAy = ALPHA + SHy
        
        # Vertical shift
        SVy = Fz * ((self.coefficients['PVy1'] + self.coefficients['PVy2'] * DFz) * LVY + \
                   (self.coefficients['PVy3'] + self.coefficients['PVy4'] * DFz) * GAMMAy) * LMUY
        
        # Final Magic Formula equation
        Fy0 = Dy * np.sin(Cy * np.arctan(By * ALPHAy - Ey * (By * ALPHAy - np.arctan(By * ALPHAy)))) + SVy
        
        return Fy0
```

### 2.2 Integration with Individual Wheel Calculations

```python
def calculate_individual_wheel_forces(wheel_loads, slip_angles, camber_angles, tire_model):
    """
    Calculate tire forces for each individual wheel using Magic Formula.
    
    Parameters:
    -----------
    wheel_loads : dict
        Normal loads for FL, FR, RL, RR
    slip_angles : dict
        Slip angles for each wheel
    camber_angles : dict
        Camber angles for each wheel
    tire_model : MagicFormula52
        Tire model instance
        
    Returns:
    --------
    dict: Tire forces for each wheel
    """
    wheel_forces = {}
    
    for wheel in ['FL', 'FR', 'RL', 'RR']:
        wheel_forces[wheel] = tire_model.calculate_lateral_force(
            slip_angles[wheel],
            wheel_loads[wheel], 
            camber_angles[wheel]
        )
    
    return wheel_forces
```

---

## Phase 3: Advanced Features - Iterative Solving (Estimated: 4-6 weeks)

### 3.1 Iterative Vehicle Dynamics Solver

```python
class IterativeVehicleDynamicsSolver:
    """Iterative solver for vehicle dynamics with convergence."""
    
    def __init__(self, vehicle_config, tire_model):
        self.vehicle_config = vehicle_config
        self.tire_model = tire_model
        self.max_iterations = 50
        self.tolerance = 1e-4
    
    def solve_vehicle_dynamics(self, velocity, curvature):
        """
        Solve vehicle dynamics with iteration for convergence.
        
        Returns:
        --------
        dict: Converged vehicle state
        """
        # Initial guesses
        beta = 0.0  # Sideslip angle
        delta = self.vehicle_config['wheelbase'] * curvature  # Steering angle
        
        # Iteration loop
        for iteration in range(self.max_iterations):
            # Calculate current state
            current_state = self.calculate_vehicle_state(velocity, curvature, beta, delta)
            
            # Check lateral force balance
            lateral_force_error = self.check_lateral_force_balance(current_state)
            
            # Check yaw moment balance
            yaw_moment_error = self.check_yaw_moment_balance(current_state)
            
            # Check convergence
            if abs(lateral_force_error) < self.tolerance and abs(yaw_moment_error) < self.tolerance:
                current_state['converged'] = True
                current_state['iterations'] = iteration
                return current_state
            
            # Update variables
            beta += lateral_force_error * 0.1  # Step size for stability
            delta -= yaw_moment_error * 0.01   # Step size for stability
        
        # If not converged
        current_state['converged'] = False
        current_state['iterations'] = self.max_iterations
        return current_state
    
    def calculate_vehicle_state(self, velocity, curvature, beta, delta):
        """Calculate complete vehicle state for given inputs."""
        # Implementation details...
        pass
    
    def check_lateral_force_balance(self, state):
        """Check if lateral forces balance with required centripetal force."""
        # Implementation details...
        pass
    
    def check_yaw_moment_balance(self, state):
        """Check if yaw moment is balanced."""
        # Implementation details...
        pass
```

---

## Phase 4: Performance Optimization - GGV Diagrams (Estimated: 3-4 weeks)

### 4.1 GGV Diagram Generation

```python
def generate_ggv_diagram(vehicle_config, tire_model, velocity_range, curvature_range):
    """
    Generate G-G-V performance envelope diagram.
    
    Parameters:
    -----------
    velocity_range : array_like
        Range of velocities to evaluate [m/s]
    curvature_range : array_like
        Range of curvatures to evaluate [1/m]
        
    Returns:
    --------
    dict: GGV lookup table and performance envelope
    """
    ggv_table = {}
    
    for velocity in velocity_range:
        ggv_table[velocity] = {}
        
        for curvature in curvature_range:
            # Calculate maximum lateral acceleration for this velocity and curvature
            max_lat_accel = calculate_max_lateral_acceleration(velocity, curvature, vehicle_config, tire_model)
            
            # Calculate maximum longitudinal acceleration
            max_long_accel = calculate_max_longitudinal_acceleration(velocity, vehicle_config, tire_model)
            
            # Store in lookup table
            ggv_table[velocity][curvature] = {
                'max_lateral_accel': max_lat_accel,
                'max_longitudinal_accel': max_long_accel,
                'max_combined_accel': calculate_combined_acceleration_limit(max_lat_accel, max_long_accel)
            }
    
    return ggv_table

def optimize_velocity_profile_with_ggv(track_coordinates, ggv_table):
    """Use GGV table to optimize velocity profile."""
    # Implementation for GGV-based optimization
    pass
```

---

## Phase 5: Powertrain Integration (Estimated: 3-4 weeks)

### 5.1 Real-time Powertrain Calculations

```python
def integrate_powertrain_with_physics(velocity_profile, distances, vehicle_config, powertrain_config):
    """
    Integrate powertrain calculations into main physics loop.
    
    Returns:
    --------
    dict: Updated velocity profile with powertrain constraints
    """
    powertrain = PowertrainModel(powertrain_config)
    optimized_velocities = velocity_profile.copy()
    
    for i in range(len(velocity_profile)):
        current_velocity = velocity_profile[i] * 0.44704  # mph to m/s
        
        # Get optimal gear
        gear = powertrain.calculate_gear_selection(current_velocity)
        
        # Calculate available torque
        rpm = powertrain.calculate_engine_rpm(current_velocity, gear)
        engine_torque = powertrain.calculate_engine_torque(rpm)
        wheel_torque = engine_torque * powertrain.get_total_gear_ratio(gear) * powertrain_config['drivetrain_losses']
        
        # Convert to wheel force
        wheel_force = wheel_torque / vehicle_config['tire_radius']
        
        # Calculate power-limited acceleration
        power_limited_accel = wheel_force / vehicle_config['mass']
        
        # Apply power limit if it's more restrictive than grip limit
        if i > 0:
            ds = distances[i] - distances[i-1]
            if ds > 0:
                # Calculate maximum achievable velocity with power limit
                v_prev_ms = optimized_velocities[i-1] * 0.44704
                v_max_power_sq = v_prev_ms**2 + 2 * power_limited_accel * ds
                v_max_power = np.sqrt(max(v_max_power_sq, v_prev_ms**2)) / 0.44704  # Convert back to mph
                
                # Take minimum of grip-limited and power-limited
                optimized_velocities[i] = min(optimized_velocities[i], v_max_power)
    
    return optimized_velocities
```

---

## Implementation Guidelines

### Development Workflow:
1. **Test-Driven Development**: Write tests for each new physics function
2. **Incremental Integration**: Add one physics computation at a time
3. **Validation**: Compare results with MATLAB implementation at each phase
4. **Performance Monitoring**: Ensure computational efficiency

### Required Vehicle Parameters to Add:
```python
# Suspension parameters
'LLTD': 0.58,                           # Lateral Load Transfer Distribution
'roll_gradient_front': 3.5,             # deg/g
'roll_gradient_rear': 2.8,              # deg/g  
'pitch_gradient': 2.0,                  # deg/g
'camber_gain_front': 1.0,               # deg/deg
'camber_gain_rear': 0.8,                # deg/deg
'kingpin_inclination_front': 7.0,       # deg
'kingpin_inclination_rear': 0.0,        # deg
'caster_angle_front': 3.0,              # deg
'caster_angle_rear': 0.0,               # deg

# Tire parameters  
'cornering_stiffness_front': 1200,      # N/rad
'cornering_stiffness_rear': 1100,       # N/rad
'tire_scaling_lateral': 0.47,           # sf_y
'tire_scaling_longitudinal': 0.60,      # sf_x

# Magic Formula coefficients (18 parameters)
'tire_mf52_coefficients': {...},

# Performance parameters
'differential_locking_torque': 50,      # N-m
'max_steering_angle': 25.0,             # deg
```

### Testing Strategy:
- **Unit Tests**: Each physics function individually
- **Integration Tests**: Combined physics calculations
- **Validation Tests**: Compare with MATLAB results
- **Performance Tests**: Computational efficiency benchmarks

### Documentation Requirements:
- **Physics Documentation**: Mathematical derivations for each computation
- **API Documentation**: Function interfaces and parameters
- **Validation Reports**: Comparison studies with MATLAB
- **User Guides**: How to tune vehicle parameters

This roadmap provides a structured approach to systematically implement the missing physics computations while maintaining code quality and validation against the MATLAB reference implementation.
