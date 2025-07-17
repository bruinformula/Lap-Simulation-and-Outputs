"""
Vehicle Configuration File
==========================

This file contains all vehicle parameters that can be easily modified
for different vehicle configurations or design studies.

All parameters use metric units (kg, m, N, etc.) unless otherwise specified.
"""

# =============================================================================
# VEHICLE MASS PROPERTIES
# =============================================================================

# Total vehicle mass including driver [kg] (from MATLAB: 660 lbs)
VEHICLE_MASS = 299.37  # 660 lbs converted to kg

# Center of gravity position from front axle [m] (calculated from MATLAB WDF = 44.754%)
CG_X_POSITION = 0.856  # This gives 44.754% front weight distribution with 1.55m wheelbase

# Center of gravity height above ground [m] (from MATLAB: 10.5/12 ft)  
CG_HEIGHT = 0.267  # 10.5/12 ft = 0.875 ft = 0.267 m

# Vehicle weight [N] (calculated from mass)
VEHICLE_WEIGHT = VEHICLE_MASS * 9.81


# =============================================================================
# VEHICLE DIMENSIONS
# =============================================================================

# Wheelbase - distance between front and rear axles [m] (from MATLAB: 61/12 ft)
WHEELBASE = 1.55  # 61/12 ft = 5.083 ft = 1.55 m

# Track width - distance between left and right wheels [m] (average of front/rear)
TRACK_WIDTH = 1.143  # Average of front (1.168m) and rear (1.118m)

# Front track width [m] (from MATLAB: 46/12 ft)
TRACK_WIDTH_FRONT = 1.168  # 46/12 ft = 3.833 ft = 1.168 m

# Rear track width [m] (from MATLAB: 44/12 ft)
TRACK_WIDTH_REAR = 1.118  # 44/12 ft = 3.667 ft = 1.118 m


# =============================================================================
# AERODYNAMICS
# =============================================================================

# Frontal area [m²] (estimated from MATLAB aerodynamic coefficients)
FRONTAL_AREA = 1.2

# Drag coefficient [-] (from MATLAB: Cd = 0.0184)
DRAG_COEFFICIENT = 0.0184

# Downforce coefficient [-] (from MATLAB: Cl = 0.0418)
DOWNFORCE_COEFFICIENT = 0.0418

# Air density [kg/m³]
AIR_DENSITY = 1.225


# =============================================================================
# SUSPENSION AND HANDLING
# =============================================================================

# Roll center heights [inches] (converted to meters in calculations)
ROLL_CENTER_FRONT = 2.0  # inches
ROLL_CENTER_REAR = 1.832  # inches

# Roll stiffness - springs [ft-lb/rad]
ROLL_STIFFNESS_FRONT_SPRINGS = 11317
ROLL_STIFFNESS_REAR_SPRINGS = 10202

# Roll stiffness - anti-roll bars [ft-lb/rad]
ROLL_STIFFNESS_FRONT_ARB = 959.770
ROLL_STIFFNESS_REAR_ARB = 1174.436

# Total roll stiffness [ft-lb/rad]
ROLL_STIFFNESS_FRONT_TOTAL = ROLL_STIFFNESS_FRONT_SPRINGS + ROLL_STIFFNESS_FRONT_ARB
ROLL_STIFFNESS_REAR_TOTAL = ROLL_STIFFNESS_REAR_SPRINGS + ROLL_STIFFNESS_REAR_ARB


# =============================================================================
# TIRE PARAMETERS
# =============================================================================

# Tire radius [m] (from MATLAB: 9.05/12 ft)
TIRE_RADIUS = 0.230  # 9.05/12 ft = 0.754 ft = 0.230 m

# Tire width [m]
TIRE_WIDTH = 0.18

# Static tire loads [N] (calculated from weight distribution)
STATIC_LOAD_FRONT = VEHICLE_WEIGHT * (WHEELBASE - CG_X_POSITION) / WHEELBASE / 2
STATIC_LOAD_REAR = VEHICLE_WEIGHT * CG_X_POSITION / WHEELBASE / 2

# Magic Formula 5.2 Parameters
TIRE_MF52_PARAMS = {
    'Fz0': 500.0,      # Reference normal load [N]
    'mu': 1.8,         # Peak friction coefficient [-]
    'B': 12.0,         # Stiffness factor [-]
    'C': 1.4,          # Shape factor [-]
    'D': 1.0,          # Peak factor [-]
    'E': -0.5,         # Curvature factor [-]
    'Sh': 0.0,         # Horizontal shift [-]
    'Sv': 0.0          # Vertical shift [-]
}

# Tire scaling factors (from MATLAB: sf_x = 0.6, sf_y = 0.47)
TIRE_SCALING_LONGITUDINAL = 0.6   # sf_x - longitudinal friction scaling
TIRE_SCALING_LATERAL = 0.47       # sf_y - lateral friction scaling


# =============================================================================
# POWERTRAIN CONFIGURATION
# =============================================================================

# Engine speed range [RPM] (from MATLAB: 6200:100:14100)
ENGINE_SPEED_RANGE = list(range(6200, 14200, 100))

# Engine torque curve [N-m] corresponding to speed range (from MATLAB)
ENGINE_TORQUE_CURVE = [
    41.57, 42.98, 44.43, 45.65, 46.44, 47.09, 47.52, 48.58, 49.57, 50.41, 
    51.43, 51.48, 51, 49.311, 48.94, 48.66, 49.62, 49.60, 47.89, 47.91, 
    48.09, 48.57, 49.07, 49.31, 49.58, 49.56, 49.84, 50.10, 50.00, 50.00, 
    50.75, 51.25, 52.01, 52.44, 52.59, 52.73, 53.34, 53.72, 52.11, 52.25, 
    51.66, 50.5, 50.34, 50.50, 50.50, 50.55, 50.63, 50.17, 50.80, 49.73, 
    49.35, 49.11, 48.65, 48.28, 48.28, 47.99, 47.68, 47.43, 47.07, 46.67, 
    45.49, 45.37, 44.67, 43.8, 43.0, 42.3, 42.00, 41.96, 41.70, 40.43, 
    39.83, 38.60, 38.46, 37.56, 36.34, 35.35, 33.75, 33.54, 32.63, 31.63
]

# Primary reduction ratio [-] (from MATLAB: 76/36)
PRIMARY_REDUCTION = 76/36  # = 2.111

# Transmission gear ratios [-] (from MATLAB)
GEAR_RATIOS = [33/12, 32/16, 30/18, 26/18, 30/23, 29/24]

# Final drive ratio [-] (from MATLAB: 40/12)
FINAL_DRIVE_RATIO = 40/12  # = 3.333

# Shift point [RPM] (from MATLAB: 14000)
SHIFT_POINT = 14000

# Drivetrain efficiency [-] (from MATLAB: 0.85)
DRIVETRAIN_EFFICIENCY = 0.85

# Shift time [seconds] (from MATLAB: 0.25)
SHIFT_TIME = 0.25


# =============================================================================
# SIMULATION PARAMETERS
# =============================================================================

# Maximum velocity for simulation [m/s]
MAX_VELOCITY = 50.0

# Minimum velocity for powertrain calculations [m/s]
MIN_VELOCITY = 7.5

# Launch boost minimum velocity [m/s]
LAUNCH_BOOST_VELOCITY = 10.0

# Gravity acceleration [m/s²]
GRAVITY = 9.81


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_vehicle_config():
    """
    Get complete vehicle configuration dictionary.
    
    Returns:
    --------
    dict
        Complete vehicle configuration
    """
    return {
        # Mass properties
        'mass': VEHICLE_MASS,
        'weight': VEHICLE_WEIGHT,
        'cg_x': CG_X_POSITION,
        'cg_height': CG_HEIGHT,
        
        # Dimensions
        'wheelbase': WHEELBASE,
        'track_width': TRACK_WIDTH,
        'track_width_front': TRACK_WIDTH_FRONT,
        'track_width_rear': TRACK_WIDTH_REAR,
        
        # Aerodynamics
        'frontal_area': FRONTAL_AREA,
        'drag_coefficient': DRAG_COEFFICIENT,
        'downforce_coefficient': DOWNFORCE_COEFFICIENT,
        'air_density': AIR_DENSITY,
        
        # Suspension
        'roll_center_front': ROLL_CENTER_FRONT,
        'roll_center_rear': ROLL_CENTER_REAR,
        'roll_stiffness_front': ROLL_STIFFNESS_FRONT_TOTAL,
        'roll_stiffness_rear': ROLL_STIFFNESS_REAR_TOTAL,
        
        # Tires
        'tire_radius': TIRE_RADIUS,
        'tire_width': TIRE_WIDTH,
        'static_load_front': STATIC_LOAD_FRONT,
        'static_load_rear': STATIC_LOAD_REAR,
        'tire_params': TIRE_MF52_PARAMS,
        
        # Simulation
        'max_velocity': MAX_VELOCITY,
        'min_velocity': MIN_VELOCITY,
        'gravity': GRAVITY
    }


def get_powertrain_config():
    """
    Get complete powertrain configuration dictionary.
    
    Returns:
    --------
    dict
        Complete powertrain configuration
    """
    return {
        'engine_speed': ENGINE_SPEED_RANGE,
        'engine_torque': ENGINE_TORQUE_CURVE,
        'primary_reduction': PRIMARY_REDUCTION,
        'gear_ratios': GEAR_RATIOS,
        'final_drive': FINAL_DRIVE_RATIO,
        'shift_point': SHIFT_POINT,
        'drivetrain_losses': DRIVETRAIN_EFFICIENCY,
        'shift_time': SHIFT_TIME,
        'tire_radius': TIRE_RADIUS
    }


def print_vehicle_summary():
    """Print a summary of key vehicle parameters."""
    print("=" * 50)
    print("VEHICLE CONFIGURATION SUMMARY")
    print("=" * 50)
    print(f"Mass: {VEHICLE_MASS} kg ({VEHICLE_MASS * 2.205:.1f} lbs)")
    print(f"Wheelbase: {WHEELBASE:.3f} m ({WHEELBASE * 39.37:.1f} in)")
    print(f"Track Width: {TRACK_WIDTH:.3f} m ({TRACK_WIDTH * 39.37:.1f} in)")
    print(f"CG Height: {CG_HEIGHT:.3f} m ({CG_HEIGHT * 39.37:.1f} in)")
    print(f"CG Position: {CG_X_POSITION:.3f} m from front axle")
    print(f"Weight Distribution: {(WHEELBASE - CG_X_POSITION)/WHEELBASE*100:.1f}% front")
    print(f"Frontal Area: {FRONTAL_AREA:.2f} m²")
    print(f"Drag Coefficient: {DRAG_COEFFICIENT:.2f}")
    print(f"Downforce Coefficient: {DOWNFORCE_COEFFICIENT:.2f}")
    print(f"Peak Friction: {TIRE_MF52_PARAMS['mu']:.2f}")
    print(f"Shift Point: {SHIFT_POINT} RPM")
    print("=" * 50)


# =============================================================================
# EXAMPLE ALTERNATIVE CONFIGURATIONS
# =============================================================================

# Example: Lighter vehicle configuration
LIGHTWEIGHT_CONFIG = {
    'mass': 250.0,  # 30 kg lighter
    'cg_height': 0.250,  # 17mm lower CG
    'drag_coefficient': 1.05,  # Slightly better aero
}

# Example: High-downforce configuration  
HIGH_DOWNFORCE_CONFIG = {
    'downforce_coefficient': 3.2,  # More downforce
    'drag_coefficient': 1.25,  # Higher drag penalty
    'frontal_area': 1.25,  # Larger frontal area
}

# Example: Autocross configuration
AUTOCROSS_CONFIG = {
    'tire_params': {
        'mu': 2.0,  # Stickier tires
        'B': 15.0,  # Stiffer tire response
    },
    'gear_ratios': [3.0, 2.2, 1.8, 1.5, 1.3, 1.15],  # Shorter gearing
}


if __name__ == "__main__":
    # Print vehicle summary when run directly
    print_vehicle_summary()
    
    # Example of getting configurations
    vehicle_config = get_vehicle_config()
    powertrain_config = get_powertrain_config()
    
    print(f"\nTotal configuration parameters: {len(vehicle_config) + len(powertrain_config)}")
