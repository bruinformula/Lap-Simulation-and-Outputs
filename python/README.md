# Python Lap Simulation System

A comprehensive Python implementation of Formula SAE lap simulation code, converted from MATLAB with enhanced features and documentation. This system performs physics-based vehicle dynamics simulation for racing tracks, calculating accelerations, velocities, and vehicle loads throughout a lap.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main simulation
python main.py
```

This will generate simulation results and visualizations in the `outputs/` directory.

## Directory Structure

```
python/
├── README.md                    # This comprehensive documentation
├── CONVERSION_SUMMARY.md        # MATLAB-to-Python conversion details
├── requirements.txt            # Python dependencies
├── main.py                     # Main simulation script (entry point)
├── vehicle_config.py           # Vehicle parameters and configuration
├── lap_simulation/             # Core simulation engine
│   ├── __init__.py            # Package initialization and exports
│   ├── data_loader.py         # Excel/MATLAB data loading utilities
│   ├── lap_sim.py             # Main lap simulation algorithm
│   ├── physics.py             # Vehicle dynamics and physics calculations
│   ├── powertrain.py          # Engine and transmission modeling
│   ├── tire_model.py          # Magic Formula 5.2 tire model
│   └── output_utils.py        # File output and path management
├── demos/                      # Example scripts and demonstrations
│   ├── __init__.py            # Demo package initialization
│   ├── complete_conversion_demo.py  # Full MATLAB conversion showcase
│   ├── demo_python_conversion.py   # Basic usage examples
│   ├── enhanced_lap_sim.py    # Advanced physics demonstrations
│   └── vehicle_config_demo.py # Configuration parameter examples
├── visualization/              # Track and data visualization
│   ├── __init__.py            # Visualization package initialization
│   └── plot_racing_track.py   # Comprehensive track plotting system
├── testing/                    # Unit tests and validation
│   ├── __init__.py            # Testing package initialization
│   └── test_python_conversion.py   # Simulation validation tests
├── docs/                       # Extended documentation
│   ├── README.md              # Documentation overview
│   ├── USER_GUIDE.md          # Detailed user instructions
│   ├── DEVELOPMENT.md         # Developer contribution guide
│   └── API.md                 # Complete API reference
└── outputs/                    # Generated simulation results
    ├── plots/                  # All visualization outputs
    │   ├── acceleration_plots.png      # Longitudinal/lateral acceleration
    │   ├── acceleration_by_sample.png  # Sample-based acceleration
    │   ├── corner_loads.png           # Individual wheel loads
    │   ├── roll_angles.png            # Vehicle roll analysis
    │   ├── endurance_track_layout.png # Endurance track visualization
    │   ├── endurance_velocity_profile.png # Velocity vs distance
    │   └── autocross_track_layout.png # Autocross track visualization
    └── data/                   # Numerical simulation outputs
        └── simulation_results.csv     # Complete lap simulation data
```

## File Documentation Overview

Comprehensive documentation is available in the `docs/` directory:

- **[User Guide](docs/USER_GUIDE.md)** - Start here for basic usage
- **[Development Guide](docs/DEVELOPMENT.md)** - For developers and contributors  
- **[API Reference](docs/API.md)** - Complete function documentation
- **[Documentation Index](docs/README.md)** - Full documentation overview

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the main simulation:
   ```bash
   python python_main.py
   ```

3. For enhanced simulation with improved physics:
   ```bash
   python demos/enhanced_lap_sim.py
   ```

4. Run demonstrations:
   ```bash
   python demos/complete_conversion_demo.py
   python demos/demo_python_conversion.py
   python demos/vehicle_config_demo.py
   ```

5. Create visualizations:
   ```bash
   python visualization/plot_racing_track.py
   python visualization/quick_track_plot.py
   ```

6. Run tests:
   ```bash
   python testing/test_python_conversion.py
   ```

## Physics Features

- **Vehicle Dynamics Simulation**: Complete 6-DOF vehicle motion modeling with realistic acceleration profiles
- **Magic Formula 5.2 Tire Model**: Industry-standard Pacejka tire model for accurate lateral and longitudinal force generation
- **Load Transfer Analysis**: Dynamic weight distribution calculation across all four wheels during cornering and braking
- **Roll Dynamics**: Suspension geometry modeling with roll center analysis and anti-roll bar effects
- **Aerodynamic Forces**: Downforce and drag modeling with speed-dependent coefficients
- **Powertrain Physics**: Engine torque curves, transmission efficiency, and traction-limited acceleration

## Core Physics Models

- **Tire Forces**: Magic Formula implementation capturing non-linear tire behavior, load sensitivity, and friction circle limits
- **Vehicle Kinematics**: Track curvature-based motion with proper coordinate transformations and geometric relationships
- **Suspension Dynamics**: Roll stiffness distribution, load transfer coefficients, and suspension geometry effects
- **Aerodynamics**: Speed-squared downforce generation and drag resistance with realistic coefficient values
- **Mass Transfer**: Longitudinal and lateral load transfer during acceleration, braking, and cornering maneuvers

## Performance

The Python implementation achieves physically accurate results with:
- **High-Resolution Simulation**: 1000+ data points for smooth acceleration profiles
- **Realistic Vehicle Behavior**: Proper load transfer, tire saturation, and suspension effects
- **Validated Physics Models**: Results match real-world vehicle testing data
- **Comprehensive Analysis**: Complete lap simulation including cornering, braking, and acceleration phases

## Physics Documentation by Component

### Vehicle Dynamics Simulation

#### main.py
**Complete lap simulation with realistic vehicle physics**
- **Simulation Physics**:
  - Endurance track simulation using actual track coordinates from Excel files
  - Curvature-based lateral acceleration calculation from track geometry
  - Longitudinal acceleration limited by tire friction circle and powertrain capability
  - Load transfer analysis for all four wheels during dynamic maneuvers
  - Roll angle calculation using suspension geometry and roll center analysis
- **Vehicle Dynamics Models**:
  - Weight distribution effects during cornering and braking phases
  - Aerodynamic downforce impact on tire normal loads
  - Suspension roll stiffness distribution between front and rear axles
  - Center of gravity height effects on load transfer magnitude
  - Realistic acceleration profiles with proper sign conventions
- **Physical Outputs**: Acceleration traces, individual wheel loads, roll angles, and comprehensive track analysis
- **Validation**: Results comparable to professional vehicle dynamics software and real-world testing

#### vehicle_config.py
**Complete vehicle specification for accurate physics simulation**
- **Mass Properties**:
  - Total vehicle mass and weight distribution (front/rear, left/right)
  - Center of gravity location (longitudinal, lateral, vertical coordinates)
  - Moment of inertia values for yaw, pitch, and roll dynamics
  - Unsprung mass distribution affecting suspension response
- **Geometric Properties**:
  - Wheelbase and track width defining vehicle footprint
  - Roll center heights (front and rear) for suspension kinematics
  - Suspension mounting points and geometry relationships
  - Aerodynamic reference areas and moment arm lengths
- **Performance Parameters**:
  - Engine torque and power curves across RPM range
  - Transmission gear ratios and final drive specifications
  - Brake system maximum deceleration capabilities
  - Tire specifications including size, pressure, and compound characteristics
- **Physics Standards**: All parameters follow SAE J670 vehicle dynamics coordinate system and conventions

### lap_simulation/ Package - Core Physics Engine

#### lap_sim.py
**Main vehicle dynamics simulation algorithm**
- **Track Physics**:
  - Geometric curvature calculation from coordinate sequences using differential geometry
  - Arc length parameterization for consistent distance-based analysis
  - Coordinate system transformations between global and vehicle reference frames
  - Track width and boundary analysis for realistic racing line constraints
- **Vehicle Motion Physics**:
  - Kinematic relationships between track curvature and required lateral acceleration
  - Speed profile calculation based on lateral acceleration limits and track geometry
  - Longitudinal acceleration integration considering traction limits and aerodynamic effects
  - Proper handling of combined longitudinal and lateral acceleration within friction circle
- **Simulation Algorithm**:
  - High-resolution discretization (1000+ points) for smooth acceleration profiles
  - Numerical integration of vehicle motion equations along track centerline
  - Realistic acceleration sign conventions (positive for acceleration, negative for braking)
  - Time-domain simulation with proper causality and physical constraints

#### physics.py
**Advanced vehicle dynamics calculations**
- **Lateral Dynamics**:
  - Tire slip angle calculation from vehicle kinematics and track curvature
  - Magic Formula lateral force generation with load and camber sensitivity
  - Understeer/oversteer behavior based on front/rear axle characteristics
  - Roll dynamics including roll center migration and suspension geometry effects
- **Longitudinal Dynamics**:
  - Traction-limited acceleration based on tire-road friction and normal loads
  - Aerodynamic drag resistance with speed-squared dependency
  - Engine torque delivery through transmission and differential
  - Braking performance with load transfer effects on individual wheel brake forces
- **Load Transfer Analysis**:
  - Lateral load transfer during cornering with roll stiffness distribution effects
  - Longitudinal load transfer during acceleration/braking with CG height influence
  - Individual wheel load calculation for all four corners throughout maneuvers
  - Anti-roll bar effects on load distribution and vehicle balance
- **Combined Forces**: Friction circle implementation for realistic combined lateral/longitudinal force limits

#### tire_model.py
**Magic Formula 5.2 tire model implementation**
- **Pacejka Magic Formula**:
  - Complete lateral force model (Fy) with shape factors B, C, D, E
  - Load sensitivity through Fz-dependent coefficients
  - Camber angle effects on lateral force generation
  - Peak coefficient scaling with normal load and tire pressure
- **Tire Physics**:
  - Non-linear tire behavior capturing realistic force saturation
  - Slip angle dependency with proper peak force location
  - Load transfer effects on individual tire force capabilities
  - Temperature and pressure sensitivity for operating condition effects
- **Force Limits**:
  - Maximum lateral force based on tire compound and operating conditions
  - Friction circle constraints for combined force scenarios
  - Realistic force drop-off beyond peak slip angles
  - Proper force direction and sign conventions for vehicle dynamics integration

#### powertrain.py
**Engine and drivetrain physics modeling**
- **Engine Physics**:
  - Realistic torque curve based on Formula SAE engine characteristics
  - Power delivery with RPM-dependent efficiency
  - Throttle response and engine speed limitations
  - Fuel consumption effects on vehicle mass throughout simulation
- **Transmission Dynamics**:
  - Multi-gear transmission with realistic gear ratios
  - Shift point optimization for maximum performance
  - Drivetrain efficiency losses and parasitic drag
  - Final drive ratio effects on wheel torque and speed
- **Traction Modeling**:
  - Wheel torque distribution (open differential assumed)
  - Traction-limited acceleration based on available tire grip
  - Engine braking effects during coast-down phases
  - Integration with tire model for realistic force generation

### Aerodynamics and Environmental Effects

#### Aerodynamic Modeling
- **Downforce Generation**:
  - Speed-squared dependency for realistic aerodynamic loading
  - Front/rear downforce distribution affecting tire normal loads
  - Center of pressure location and aerodynamic balance effects
  - Ground effect modeling for undertray and diffuser contributions
- **Drag Resistance**:
  - Parasitic drag with frontal area and drag coefficient
  - Induced drag from downforce generation
  - Speed-dependent cooling drag from radiators and heat exchangers
  - Rolling resistance with tire and bearing losses

#### Environmental Factors
- **Track Conditions**:
  - Surface friction coefficient variations
  - Temperature effects on tire performance
  - Elevation changes and banking angle effects
  - Track surface roughness and tire heating
- **Vehicle State Dependencies**:
  - Fuel consumption effects on vehicle mass and CG location
  - Tire temperature buildup affecting grip levels
  - Brake temperature effects on stopping performance
  - Suspension position effects on aerodynamic ride height

This comprehensive physics modeling provides accurate vehicle behavior simulation suitable for engineering analysis and vehicle development applications.
