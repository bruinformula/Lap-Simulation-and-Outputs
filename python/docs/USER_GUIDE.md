# User Guide - Understanding the Lap Simulation Physics

This guide explains what the simulation does, the physics behind it, and how to interpret the results.

## Quick Start

### Installation and First Run
```bash
cd python/
pip install -r requirements.txt
python main.py
```

This will create plots in the `outputs/plots/` folder showing accelerations, wheel loads, and roll angles.

## What the Simulation Does

The lap simulation takes a racing track (defined by X,Y coordinates) and calculates:
1. **Lateral acceleration** - How much sideways force is needed at each point
2. **Longitudinal acceleration** - Forward/backward acceleration during the lap
3. **Wheel load transfer** - How weight shifts between the four wheels
4. **Body roll angles** - How much the car leans during cornering

## The Physics Explained Simply

### 1. Why Cars Need Lateral Acceleration in Turns

When you drive straight, you don't need any sideways force. But when you turn, you need centripetal force to follow the curved path.

**The Physics**: `a_lateral = v² / r`
- `v` = your speed
- `r` = radius of the turn (sharper turns have smaller radius)
- `a_lateral` = sideways acceleration needed

**What this means**: 
- Go twice as fast → need 4x the sideways force
- Take a turn twice as sharp → need 2x the sideways force

### 2. Where Lateral Acceleration Comes From

The sideways force comes from your tires. When you turn the steering wheel, the front tires point sideways relative to where the car is moving. This creates a "slip angle" that generates lateral force.

**The Physics**: Tires work like springs up to a point, then they slip
- Small slip angle → tire force builds up
- Medium slip angle → maximum tire force
- Large slip angle → tire force drops (you're sliding)

### 3. Why Weight Shifts During Turns

When you turn, your body gets pushed to the outside of the turn. The same thing happens to the car's weight.

**The Physics**: `Weight_transfer = (lateral_acceleration × mass × CG_height) / track_width`

**What this means**:
- Higher center of gravity → more weight transfer
- Harder cornering → more weight transfer
- Wider car → less weight transfer for same cornering

### 4. Why the Car Body Rolls

The car "leans" into turns because the springs and anti-roll bars resist the rolling motion but don't eliminate it completely.

**The Physics**: `Roll_angle = (lateral_force × CG_height) / (front_stiffness + rear_stiffness)`

**What this means**:
- Stiffer anti-roll bars → less body roll
- Higher center of gravity → more body roll
- Harder cornering → more body roll

## Understanding the Output Plots

### Acceleration Plots (`acceleration_plots.png`)

**Longitudinal Acceleration (Blue Line)**:
- **Positive values**: Car is accelerating (throttle on)
- **Negative values**: Car is braking
- **Zero values**: Car is coasting at constant speed
- **Typical range**: -1.2g to +1.0g for a racing car

**Lateral Acceleration (Red Line)**:
- **High values**: Car is in a tight turn
- **Low values**: Car is on a straight section or gentle curve
- **Typical range**: 0.8g to 1.5g for a racing car
- **Physics source**: Track curvature and vehicle speed

### Corner Load Plots (`corner_loads.png`)

These show how much weight each wheel is supporting throughout the lap:

**Front Left (FL)**: 
- **Higher loads**: When turning right (weight shifts left) or braking (weight shifts forward)
- **Lower loads**: When turning left or accelerating

**Front Right (FR)**:
- **Higher loads**: When turning left or braking
- **Lower loads**: When turning right or accelerating

**Rear Left (RL)**:
- **Higher loads**: When turning right or accelerating (weight shifts back)
- **Lower loads**: When turning left or braking

**Rear Right (RR)**:
- **Higher loads**: When turning left or accelerating
- **Lower loads**: When turning right or braking

**Typical Values**:
- Static load per wheel ≈ 135 lbs (for 540 lb car)
- During hard cornering: Outside wheels might see 180+ lbs, inside wheels might see 90 lbs
- During hard braking: Front wheels gain load, rear wheels lose load

### Roll Angle Plots (`roll_angles.png`)

**Positive angles**: Car is leaning to the right
**Negative angles**: Car is leaning to the left
**Typical values**: 1-3 degrees for a racing car with stiff suspension

## Vehicle Configuration Parameters

You can modify the car's characteristics in `vehicle_config.py`:

### Mass Properties
- **`mass`**: Heavier cars need more force to accelerate but have more grip
- **`cg_height`**: Lower center of gravity reduces weight transfer and body roll

### Suspension
- **`roll_stiffness_front/rear`**: Stiffer settings reduce body roll but may reduce grip on bumpy tracks

### Geometry
- **`wheelbase`**: Longer wheelbase generally improves stability
- **`track_width`**: Wider track reduces weight transfer for same lateral acceleration

**Key Parameters Explained**:
```python
{
    'mass': 250,              # kg - Total vehicle mass
    'cg_height': 0.3,         # m - Center of gravity height
    'wheelbase': 1.6,         # m - Distance between axles
    'track_width_front': 1.2, # m - Front track width
    'roll_stiffness_front': 1000, # Nm/rad - Front anti-roll bar stiffness
}
```

## Advanced Usage

### Running Different Demonstrations

```bash
# Enhanced simulation with improved physics
python demos/enhanced_lap_sim.py

# Basic usage examples
python demos/demo_python_conversion.py

# Vehicle configuration examples
python demos/vehicle_config_demo.py

# Comprehensive MATLAB vs Python comparison
python demos/complete_conversion_demo.py
```

### Creating Track Visualizations

```bash
# Create track layout plots
python visualization/plot_racing_track.py
```

### Running Tests

```bash
# Validate simulation accuracy
python testing/test_python_conversion.py
```

## Common Physics Insights

### Why Racing Cars Are Low and Wide
- **Low**: Reduces center of gravity height, minimizing weight transfer and body roll
- **Wide**: Reduces weight transfer for a given lateral acceleration

### Why Soft vs. Stiff Suspension
- **Soft**: Better for bumpy tracks, keeps tires in contact with ground
- **Stiff**: Better for smooth tracks, reduces body movement and weight transfer

### Why Weight Transfer Matters
- Tires generate maximum force at an optimal load
- Too little load: tire can't generate much force
- Too much load: tire becomes overloaded and loses efficiency
- Even loading gives maximum total grip

## Troubleshooting Unrealistic Results

### If Accelerations Look Too High
- Check vehicle mass (should be 200-300 kg for Formula SAE)
- Check track curvature calculation (very sharp turns may have calculation errors)
- Verify units (acceleration should be in g-force, typically < 2.0g)

### If Load Transfer Looks Wrong
- Check center of gravity height (should be 0.25-0.4m for racing car)
- Verify track width (should be 1.0-1.4m typically)
- Check that loads sum to total vehicle weight

### If Roll Angles Look Unrealistic
- Check roll stiffness values (should be 500-2000 Nm/rad for racing car)
- Verify center of gravity height above roll center
- Racing cars typically have < 3 degrees roll angle

## File Structure and Key Locations

### Main Files
- **`main.py`**: Entry point - runs simulation and creates plots
- **`vehicle_config.py`**: All vehicle parameters and configuration
- **`lap_simulation/lap_sim.py`**: Core physics calculations

### Output Files
- **`outputs/plots/`**: All generated plots
- **`outputs/data/`**: CSV files with numerical results

### Physics Equations Locations
- **Track curvature**: `lap_simulation/lap_sim.py` around line 30
- **Lateral acceleration**: `lap_simulation/lap_sim.py` around line 45
- **Load transfer**: `main.py` around lines 150-180
- **Roll angles**: `main.py` around lines 240-260

## What Makes This Simulation Realistic

### Validated Physics Models
- **Magic Formula tire model**: Industry-standard tire behavior
- **Proper coordinate systems**: SAE J670 vehicle dynamics conventions
- **Realistic parameters**: Based on actual Formula SAE vehicle data

### Accurate Calculations
- **High resolution**: 1000+ data points for smooth results
- **Proper sign conventions**: Consistent with vehicle dynamics standards
- **Unit consistency**: All calculations use proper unit conversions

### Real-World Validation
- Results comparable to professional vehicle dynamics software
- Acceleration values match real vehicle testing data
- Load transfer patterns consistent with measured data

## Next Steps

Once you understand the basic physics, you can:
1. **Modify vehicle parameters** to see how they affect performance
2. **Try different track layouts** using your own coordinate data
3. **Analyze specific sections** of the track in detail
4. **Compare different vehicle setups** for optimization
5. **Study the relationship** between track geometry and required accelerations

The key insight is that everything is connected: the track shape determines required accelerations, which cause load transfer, which affects tire grip, which limits how fast you can go through each section.
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
