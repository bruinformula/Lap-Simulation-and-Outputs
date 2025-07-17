# User Guide

## Quick Start

### Installation
1. Navigate to the python directory:
   ```bash
   cd python/
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Your First Simulation
```bash
python python_main.py
```

This will:
- Load endurance track data
- Run lap simulation 
- Generate acceleration plots
- Calculate corner loads
- Show roll angle analysis

## Understanding the Output

### Acceleration Plots
The simulation generates plots showing:
- **Longitudinal acceleration**: Braking (negative) and acceleration (positive) forces
- **Lateral acceleration**: Cornering forces (signed: positive = right turn)
- **Distance traveled**: Cumulative distance around track

### Corner Loads
Shows weight transfer effects:
- **Front Left/Right**: Load distribution during cornering and braking
- **Rear Left/Right**: Load changes affect tire grip and handling

### Roll Angles
Vehicle body roll during cornering:
- Calculated from lateral acceleration and suspension stiffness
- Important for aerodynamics and driver comfort

## Track Selection

### Available Tracks
- **Endurance**: Longer track with high-speed sections
- **Autocross**: Tight, technical course with many turns

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
