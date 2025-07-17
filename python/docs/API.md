# API Documentation

## Core Classes and Functions

### DataManager (data_loader.py)
Handles loading and processing of MATLAB .mat files and Excel data.

```python
from lap_simulation.data_loader import DataManager

# Initialize data manager
data_manager = DataManager()

# Load racing line data
racing_line = data_manager.load_racing_line_data('endurance')
```

### TireModel (tire_model.py)
Implements Magic Formula 5.2 tire model for lateral force calculations.

```python
from lap_simulation.tire_model import TireModel

# Initialize tire model
tire = TireModel()

# Calculate lateral force
Fy = tire.calculate_lateral_force(slip_angle, normal_load)
```

### PowertrainModel (powertrain.py)
Engine and transmission modeling with gear selection and torque calculations.

```python
from lap_simulation.powertrain import PowertrainModel

# Initialize powertrain
powertrain = PowertrainModel()

# Calculate wheel force for given velocity
force, gear = powertrain.calculate_wheel_force(velocity_ms)
```

### LapSimulator (lap_sim.py)
Main simulation class that integrates all vehicle dynamics.

```python
from lap_simulation.lap_sim import LapSimulator

# Initialize simulator
simulator = LapSimulator()

# Run lap simulation
results = simulator.simulate_lap('endurance')
```

## Function Reference

### lap_information()
Core physics calculation function that processes track coordinates and calculates vehicle dynamics.

**Parameters:**
- `x_coords`: Array of x coordinates [m]
- `y_coords`: Array of y coordinates [m]
- `velocity`: Vehicle velocity [m/s]

**Returns:**
- `A_long_g`: Longitudinal acceleration [g]
- `A_lat_g`: Lateral acceleration [g]
- `distance`: Cumulative distance [m]

### MF52_Fy_fcn()
Magic Formula 5.2 lateral force calculation.

**Parameters:**
- `alpha`: Slip angle [rad]
- `Fz`: Normal load [N]
- `params`: Tire parameters dictionary

**Returns:**
- `Fy`: Lateral force [N]

### powertrain_lapsim()
Simplified powertrain calculation function.

**Parameters:**
- `velocity_ms`: Vehicle velocity [m/s]
- `config`: Optional powertrain configuration

**Returns:**
- `force_N`: Drive force [N]
- `gear`: Selected gear

## Data Structures

### Vehicle Configuration
```python
vehicle_config = {
    'mass': 280,  # kg
    'wheelbase': 1.55,  # m
    'track_width': 1.22,  # m
    'cg_height': 0.267,  # m
    'cg_position': 0.856,  # m from front axle
    'frontal_area': 1.2,  # m²
    'drag_coefficient': 1.1,
    'downforce_coefficient': 2.5
}
```

### Tire Parameters
```python
tire_params = {
    'Fz0': 500,  # Reference load [N]
    'mu': 1.8,   # Peak friction coefficient
    'B': 12.0,   # Stiffness factor
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
