# User Guide - Vehicle Dynamics and Physics

## Quick Start with Physics Understanding

### Installation and First Simulation
```bash
cd python/
pip install -r requirements.txt
python main.py
```

### Understanding What Happens Physically

When you run the simulation, the system performs these physics calculations:

1. **Track Geometry Analysis**: Converts track coordinates into curvature values
2. **Vehicle Kinematics**: Calculates required lateral acceleration for each track segment
3. **Tire Force Modeling**: Uses Magic Formula to determine available grip
4. **Load Transfer Calculation**: Computes dynamic weight distribution
5. **Vehicle Dynamics Integration**: Simulates realistic vehicle motion

## Physics Behind the Outputs

### Acceleration Plots - What They Mean

#### Longitudinal Acceleration
- **Positive Values**: Vehicle accelerating (engine torque > resistance)
- **Negative Values**: Vehicle braking (brake force or drag > drive force)
- **Magnitude Limits**: Typically ±1.2g for Formula SAE vehicles
- **Physics Source**: Tire friction circle and powertrain limits

#### Lateral Acceleration  
- **Sign Convention**: Positive = right turn, negative = left turn
- **Magnitude Source**: Track curvature × velocity²
- **Limits**: Tire lateral force capacity (typically 1.5-2.0g for racing tires)
- **Realism**: Values match actual vehicle testing data

### Corner Load Analysis - Load Transfer Physics

#### Physical Mechanisms
During cornering and braking, vehicle weight shifts due to:
- **Lateral Forces**: Centrifugal force creates left/right weight transfer
- **Longitudinal Forces**: Inertial forces create front/rear weight transfer
- **CG Height Effects**: Higher center of gravity amplifies load transfer
- **Track Width/Wheelbase**: Wider stance reduces load transfer percentage

#### Individual Wheel Loads
- **Front Left (FL)**: Increases during right turns and braking
- **Front Right (FR)**: Increases during left turns and braking  
- **Rear Left (RL)**: Increases during right turns and acceleration
- **Rear Right (RR)**: Increases during left turns and acceleration

### Roll Angle Physics

#### Suspension Dynamics
Vehicle roll results from:
- **Lateral Force Moment**: Centrifugal force × CG height
- **Roll Stiffness Resistance**: Spring and anti-roll bar forces
- **Roll Center Geometry**: Suspension kinematics affect roll characteristics

#### Engineering Significance
- **Aerodynamics**: Roll affects wing and undertray ground clearance
- **Tire Contact**: Roll changes tire contact patch and camber angles
- **Driver Comfort**: Excessive roll affects driver ability and confidence

## Track Physics and Racing Lines

### Curvature and Speed Relationship

The fundamental relationship governing vehicle speed through corners:
```
v_max = √(μ × g / κ)
```

Where:
- **v_max**: Maximum cornering speed
- **μ**: Tire-road friction coefficient  
- **g**: Gravitational acceleration
- **κ**: Track curvature (1/radius)

### Racing Line Optimization

The simulation uses physics principles to determine optimal paths:
- **Geometric Line**: Largest radius through corner
- **Late Apex**: Maximizes straight-line acceleration zones
- **Early Apex**: Maximizes corner exit speed
- **Physics Constraints**: Tire grip limits and vehicle dynamics

## Vehicle Configuration Physics

### Mass Properties Impact

#### Center of Gravity Height
- **Lower CG**: Reduces load transfer, improves handling
- **Higher CG**: Increases load transfer, affects stability
- **Optimal Range**: 250-300mm for Formula SAE vehicles

#### Weight Distribution
- **Front-Heavy**: Promotes understeer, improves braking
- **Rear-Heavy**: Promotes oversteer, can improve acceleration traction
- **Balanced**: Neutral handling characteristics

### Suspension Tuning Physics

#### Roll Stiffness Distribution
- **Front Stiff**: Increases understeer tendency
- **Rear Stiff**: Increases oversteer tendency
- **Total Stiffness**: Affects overall roll angle magnitude

#### Spring Rate Effects
- **Higher Rates**: Reduce body motion, improve aerodynamic consistency
- **Lower Rates**: Improve tire contact, better over rough surfaces
- **Balance**: Compromise between handling and ride quality

### Aerodynamic Physics

#### Downforce Benefits
- **Increased Normal Load**: Higher tire grip capability
- **Speed Sensitivity**: Effect increases with speed squared
- **Load Transfer Reduction**: Downforce reduces relative load transfer percentage

#### Drag Penalties
- **Speed Resistance**: Opposes acceleration and limits top speed
- **Power Requirement**: Increases power needed to maintain speed
- **Efficiency Trade-off**: Balance between cornering and straight-line performance

## Advanced Physics Concepts

### Friction Circle Theory

The tire friction circle represents the maximum combined force capability:
- **Pure Lateral**: Maximum cornering force
- **Pure Longitudinal**: Maximum acceleration/braking force
- **Combined**: Total force magnitude limited by circle radius
- **Optimization**: Best lap times use full friction circle

### Load Sensitivity Effects

Tire performance varies with normal load:
- **Peak Force**: Increases with load but not proportionally
- **Load Sensitivity**: Typically Fmax ∝ Fz^0.9
- **Optimization**: Equal tire loading maximizes total grip

### Vehicle Dynamics Stability

#### Understeer/Oversteer Tendencies
- **Understeer**: Front tires lose grip first, vehicle pushes wide
- **Oversteer**: Rear tires lose grip first, vehicle rotates more than desired
- **Neutral**: Balanced front/rear grip, vehicle follows driver input

#### Stability Factors
- **Static Margin**: CG location relative to aerodynamic center
- **Weight Distribution**: Front/rear load distribution effects
- **Roll Stiffness**: Suspension tuning influence on balance

## Validation and Accuracy

### Physics Model Validation
- **Tire Data**: Based on actual tire testing results
- **Vehicle Parameters**: Realistic Formula SAE specifications
- **Force Limits**: Consistent with vehicle testing experience
- **Energy Balance**: Kinetic energy changes match work performed

### Typical Performance Values
- **Lateral Acceleration**: 1.2-1.8g sustained cornering
- **Longitudinal Acceleration**: 1.0g acceleration, 1.3g braking
- **Top Speed**: 80-100 mph depending on gearing and aerodynamics
- **Lap Times**: Competitive with actual Formula SAE performance

This physics-focused approach ensures the simulation provides meaningful engineering insights for vehicle development and driver training applications.

### Changing Tracks
Edit the track selection in `python_main.py`:
```python
# For autocross instead of endurance
track_coords = "Autocross_Coordinates_2.xlsx"
```

## Customizing Simulations

### Vehicle Configuration File
The easiest way to modify vehicle parameters is through the dedicated `vehicle_config.py` file:

```python
# Open vehicle_config.py and modify parameters directly
VEHICLE_MASS = 260.0  # Change from 280 to 260 kg
CG_HEIGHT = 0.250     # Lower center of gravity
TIRE_MF52_PARAMS = {
    'mu': 2.0,        # Increase tire grip
    'B': 15.0,        # Stiffer tire response
    # ... other parameters
}
```

### Quick Configuration Changes
```python
from vehicle_config import get_vehicle_config, get_powertrain_config

# Get base configuration
config = get_vehicle_config()

# Modify specific parameters
config['mass'] = 260  # kg
config['cg_height'] = 0.250  # m
config['tire_params']['mu'] = 2.0  # better grip

# Use modified config in simulation
```

### Pre-defined Configurations
The vehicle_config.py file includes several example configurations:

```python
# Lightweight configuration
LIGHTWEIGHT_CONFIG = {
    'mass': 250.0,
    'cg_height': 0.250,
    'drag_coefficient': 1.05
}

# High-downforce configuration  
HIGH_DOWNFORCE_CONFIG = {
    'downforce_coefficient': 3.2,
    'drag_coefficient': 1.25
}

# Autocross-optimized configuration
AUTOCROSS_CONFIG = {
    'tire_params': {'mu': 2.0, 'B': 15.0},
    'gear_ratios': [3.0, 2.2, 1.8, 1.5, 1.3, 1.15]
}
```

### Vehicle Parameters
Modify vehicle configuration in `vehicle_config.py`:

```python
vehicle_config = {
    'mass': 280,  # kg - total vehicle mass
    'wheelbase': 1.55,  # m - distance between axles
    'track_width': 1.22,  # m - distance between wheels
    'cg_height': 0.267,  # m - center of gravity height
    'cg_position': 0.856,  # m - CG distance from front axle
}
```

### Configuration Testing
Test different configurations:
```bash
python vehicle_config_demo.py  # Compare multiple configurations
python vehicle_config.py       # Print current configuration summary
```

### Advanced Parameter Studies
Run parameter sensitivity analyses:
```python
# Test different vehicle masses
masses = [250, 260, 270, 280, 290, 300]  # kg
for mass in masses:
    config = get_vehicle_config()
    config['mass'] = mass
    results = run_simulation(config)
    analyze_results(results)
```

### Aerodynamics
Adjust aerodynamic properties in `vehicle_config.py`:
```python
aero_config = {
    'frontal_area': 1.2,  # m² - frontal area
    'drag_coefficient': 1.1,  # Cd
    'downforce_coefficient': 2.5,  # Cl
}
```

### Engine/Powertrain
Modify engine characteristics in `vehicle_config.py`:
```python
engine_config = {
    'max_power': 75000,  # W - maximum power
    'shift_point': 14000,  # RPM - shift point
    'gear_ratios': [2.75, 2.0, 1.67, 1.44, 1.3, 1.21],
}
```

## Advanced Features

### High-Resolution Simulation
For more detailed results, use the enhanced simulator:
```bash
python enhanced_lap_sim.py
```

Benefits:
- 1000-point racing line vs 151 points
- More accurate curvature calculations
- Realistic acceleration magnitudes

### Custom Visualizations
Create specialized plots:
```bash
python visualization/plot_racing_track.py  # Track layout only
python visualization/quick_track_plot.py   # Fast overview
```

### Batch Processing
Run multiple configurations:
```python
from demos.complete_conversion_demo import run_parameter_sweep

# Test different vehicle masses
masses = [260, 280, 300]  # kg
results = run_parameter_sweep('mass', masses)
```

## Interpreting Results

### Realistic Values
- **Lateral acceleration**: ±1.5g to ±2.0g (race car typical)
- **Longitudinal acceleration**: -1.5g to +1.0g (braking vs acceleration)
- **Corner loads**: 50-150% of static load per wheel
- **Roll angles**: 1-3 degrees typical

### Performance Metrics
Key indicators of vehicle performance:
- **Peak lateral g**: Maximum cornering capability
- **Minimum lap time**: Overall performance measure  
- **Load variation**: Tire utilization efficiency
- **Roll angle**: Handling characteristics

## Troubleshooting

### Common Issues

1. **ImportError**: Missing dependencies
   ```bash
   pip install -r requirements.txt
   ```

2. **FileNotFoundError**: Data files not found
   - Ensure you're running from the python/ directory
   - Check that Data Files/ directory exists in parent folder

3. **Plotting errors**: Display issues
   ```bash
   pip install matplotlib --upgrade
   ```

4. **Performance issues**: Large datasets
   - Use enhanced_lap_sim.py for optimized calculations
   - Consider reducing data resolution for testing

### Getting Help
- Check `docs/API.md` for function details
- See `docs/DEVELOPMENT.md` for advanced topics
- Review example scripts in `demos/` directory

## Output Files

### Generated Data
- `simulation_results.csv`: Numerical results for further analysis
- `plots/*.png`: Visualization files

### Data Format
CSV contains columns:
- Distance [m]
- Velocity [m/s] 
- Lateral acceleration [g]
- Longitudinal acceleration [g]
- Corner loads [N]
- Roll angle [degrees]

## Next Steps

1. **Experiment with parameters**: Try different vehicle configurations
2. **Custom tracks**: Create your own track coordinate files
3. **Advanced analysis**: Use the data for optimization studies
4. **Integration**: Incorporate into larger vehicle design workflows
