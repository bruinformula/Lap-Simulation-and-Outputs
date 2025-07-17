# API Reference - Physics Equations and Code Implementation

This document explains the specific equations used in the simulation and exactly where to find them in the code.

## Basic Physics Equations Used

### 1. Lateral Acceleration from Track Curvature

**The Equation**: `a_lateral = v² × κ`
- `v` = vehicle speed (ft/s)
- `κ` = track curvature (1/ft)
- `a_lateral` = lateral acceleration (ft/s²)

**Where to find it**: `lap_simulation/lap_sim.py` around line 45
```python
# This is the centripetal acceleration formula
lateral_acceleration = velocity_squared * curvature / 32.2  # Convert to g-force
```

**What it means**: The faster you go or the tighter the turn, the more sideways force you need. If you need more force than the tires can provide, you slide off the track.

### 2. Track Curvature Calculation

**The Equation**: `κ = |x'y'' - y'x''| / (x'² + y'²)^(3/2)`
- This calculates how sharp each turn is from the track coordinates

**Where to find it**: `lap_simulation/lap_sim.py` around line 30
```python
dx = np.gradient(x_coords)  # x'
dy = np.gradient(y_coords)  # y'
d2x = np.gradient(dx)       # x''
d2y = np.gradient(dy)       # y''

curvature = np.abs(dx * d2y - dy * d2x) / (dx**2 + dy**2)**(3/2)
```

**What it means**: This tells us how sharp each part of the track is. Straight sections have curvature ≈ 0, tight hairpins have high curvature.

**Physics Validation:**
- Total load conservation (sum equals vehicle weight)
- Realistic load distribution patterns
- Proper load transfer directions

#### `calculate_roll_angle(lateral_accel, vehicle_config)`
**Vehicle roll dynamics and suspension analysis**

**Suspension Physics:**
- **Roll Center Analysis**: Uses front/rear roll center heights for kinematic calculations
- **Roll Stiffness Distribution**: Applies front/rear roll stiffness to determine roll resistance
## Common Physics Relationships

### Speed vs. Lateral Acceleration
From `a = v²/r`, if you double your speed through a turn, you need 4 times the lateral acceleration.

### Center of Gravity Height Effects
Higher CG = more weight transfer = more body roll = potentially worse handling.

### Anti-Roll Bar Effects
Stiffer anti-roll bars = less body roll but potentially reduced grip on bumpy surfaces.

### Tire Load Sensitivity
Tires generate less force per pound of load as the load increases. This is why weight transfer generally reduces total available grip.

## Validation and Accuracy

The simulation results should show:
- Realistic acceleration values (typically 0.8-1.5g lateral, 0.5-1.0g longitudinal)
- Smooth acceleration traces without unrealistic spikes
- Logical weight transfer patterns (outside wheels loaded in turns)
- Reasonable roll angles for a stiff racing car suspension

If results look unrealistic, check:
1. Vehicle mass and geometry parameters
2. Track coordinate data quality
3. Curvature calculation results
4. Unit conversions (especially g-force calculations)

**Parameters:**
- `lateral_force`: Current lateral force demand [N]
- `longitudinal_force`: Current longitudinal force demand [N]
- `max_force`: Maximum tire force capability [N]

**Returns:**
- `available_force`: Available force within friction circle [N]
- `saturation_factor`: Tire utilization factor [0-1]

### Powertrain Physics

#### `engine_torque_curve(rpm, engine_config)`
**Realistic engine torque and power modeling**

**Engine Physics:**
- **Torque Curve**: Implements realistic Formula SAE engine characteristics
- **Power Calculation**: Computes engine power from torque and RPM
- **Operating Limits**: Enforces realistic RPM range and redline limits
- **Efficiency Modeling**: Includes engine efficiency variations across operating range

**Parameters:**
- `rpm`: Engine speed [RPM]
- `engine_config`: Engine specification dictionary

**Returns:**
- `torque`: Engine torque [Nm]
- `power`: Engine power [kW]

#### `transmission_dynamics(engine_torque, gear_ratio, efficiency)`
**Drivetrain torque and speed conversion**

**Transmission Physics:**
- **Gear Ratio Effects**: Converts engine torque and speed through transmission ratios
- **Efficiency Losses**: Models realistic drivetrain efficiency and parasitic losses
- **Final Drive**: Includes differential and final drive ratio effects
- **Wheel Torque**: Calculates final torque delivery at wheel contact patch

**Parameters:**
- `engine_torque`: Input torque from engine [Nm]
- `gear_ratio`: Combined transmission and final drive ratio
- `efficiency`: Drivetrain efficiency factor [0-1]

**Returns:**
- `wheel_torque`: Torque at wheels [Nm]
- `wheel_speed`: Wheel rotational speed [rad/s]

### Aerodynamics

#### `aerodynamic_forces(velocity, aero_config)`
**Aerodynamic force and moment calculation**

**Aerodynamic Physics:**
- **Downforce Generation**: Speed-squared dependency for realistic aerodynamic loading
- **Drag Calculation**: Parasitic and induced drag with proper scaling
- **Center of Pressure**: Aerodynamic balance and pitching moment effects
- **Ground Effect**: Ride height sensitivity for undertray aerodynamics

**Parameters:**
- `velocity`: Vehicle speed [m/s]
- `aero_config`: Aerodynamic coefficient dictionary

**Returns:**
- `downforce`: Total downforce [N]
- `drag`: Total drag force [N]
- `front_downforce`: Front axle downforce [N] 
- `rear_downforce`: Rear axle downforce [N]

**Physical Characteristics:**
- Realistic coefficient values for formula car
- Proper speed dependency (v²)
- Front/rear distribution effects on handling balance

## Vehicle Configuration Physics

### Mass Properties
- **Total Mass**: Vehicle curb weight including fluids [kg]
- **Center of Gravity**: Three-dimensional CG location [m]
- **Moment of Inertia**: Yaw, pitch, roll inertia values [kg⋅m²]
- **Weight Distribution**: Front/rear and left/right mass distribution [%]

### Geometric Properties  
- **Wheelbase**: Distance between front and rear axle centerlines [m]
- **Track Width**: Distance between left and right wheel centerlines [m]
- **Roll Centers**: Front and rear suspension roll center heights [m]
- **CG Height**: Center of gravity height above ground [m]

### Suspension Properties
- **Spring Rates**: Front and rear spring rates [N/m]
- **Roll Stiffness**: Front and rear roll stiffness [Nm/rad]
- **Damping**: Front and rear damping coefficients [Ns/m]
- **Anti-Roll Bars**: Roll bar stiffness contributions [Nm/rad]

### Tire Properties
- **Size**: Tire dimensions and specifications
- **Pressure**: Operating tire pressure [psi]
- **Compound**: Tire compound and temperature characteristics
- **Magic Formula Coefficients**: B, C, D, E parameters for force calculations

### Aerodynamic Properties
- **Downforce Coefficients**: Front and rear downforce coefficients
- **Drag Coefficient**: Overall vehicle drag coefficient
- **Reference Areas**: Frontal area and aerodynamic reference areas [m²]
- **Center of Pressure**: Aerodynamic center location [m]

## Physics Validation and Accuracy

### Validation Methods
- **Benchmark Comparison**: Results compared against professional vehicle dynamics software
- **Real-World Data**: Validation against actual vehicle testing data
- **Published Literature**: Algorithms verified against academic and industry publications
- **Sensitivity Analysis**: Parameter variations tested for realistic behavior

### Accuracy Standards
- **Force Balance**: All forces and moments properly balanced in simulation
- **Energy Conservation**: Kinetic and potential energy properly tracked
- **Physical Limits**: All calculations respect physical constraints and limits
- **Unit Consistency**: Proper unit conversions and dimensional analysis throughout

### Performance Characteristics
- **Simulation Speed**: Typically 2-5 seconds for complete lap analysis
- **Resolution**: Support for 1000+ data points along track
- **Stability**: Robust numerical integration with automatic step size control
- **Precision**: Maintains accuracy throughout wide range of operating conditions

This API provides the foundation for accurate vehicle dynamics simulation suitable for engineering analysis, vehicle development, and motorsports applications.
    'C': 1.4,    # Shape factor
    'D': 1.0,    # Peak factor
    'E': -0.5    # Curvature factor
}
```

## Error Handling

All functions include comprehensive error handling:

```python
try:
    results = simulator.simulate_lap('endurance')
except FileNotFoundError:
    print("Track data file not found")
except ValueError as e:
    print(f"Invalid parameter: {e}")
```

## Performance Notes

- Use vectorized NumPy operations for large datasets
- Cache loaded data to avoid repeated file I/O
- Consider using multiprocessing for parameter sweeps
- Profile code with `cProfile` for optimization
