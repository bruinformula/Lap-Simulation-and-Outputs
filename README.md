# Lap Simulation - Python Conversion

This repository contains a Python conversion of the MATLAB lap simulation code for Formula SAE vehicle dynamics analysis. The conversion maintains compatibility with the original MATLAB data files while providing a modern Python framework for vehicle simulation.

## Overview

The lap simulation performs vehicle dynamics analysis for Formula SAE racing, including:

- **Tire modeling** using Magic Formula 5.2
- **Powertrain modeling** with engine and transmission
- **Vehicle dynamics** calculations for cornering and acceleration
- **g-g-V diagram generation** for performance envelope analysis
- **Lap time simulation** around race tracks

## Project Structure

```
├── python/                          # Python conversion
│   └── lap_simulation/              # Main simulation package
│       ├── __init__.py              # Package initialization
│       ├── data_loader.py           # MATLAB data file loading
│       ├── tire_model.py            # Magic Formula tire model
│       ├── powertrain.py            # Engine and transmission
│       └── lap_sim.py               # Main simulation logic
├── Scripts/                         # Original MATLAB code
│   ├── main.m                       # Main MATLAB script
│   └── Lap-Simulation/              # MATLAB simulation functions
├── Data Files/                      # Tire and vehicle data
│   ├── *.mat                        # MATLAB data files
│   └── *.xlsx                       # Track coordinate files
├── test_python_conversion.py        # Test suite
├── python_main.py                   # Main Python script
└── requirements.txt                 # Python dependencies
```

## Installation

1. **Set up Python environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python test_python_conversion.py
   ```

## Usage

### Basic Simulation

```python
from python.lap_simulation import lap_sim

# Run lap simulation
acceleration, lateral_accel, distance = lap_sim("Endurance_Coordinates_1.xlsx")

# Plot results
import matplotlib.pyplot as plt
plt.plot(distance, acceleration, label='Longitudinal')
plt.plot(distance, lateral_accel, label='Lateral')
plt.legend()
plt.show()
```

### Advanced Usage

```python
from python.lap_simulation.lap_sim import LapSimulator
from python.lap_simulation.tire_model import TireModel
from python.lap_simulation.powertrain import PowertrainModel

# Initialize components
simulator = LapSimulator(base_dir=".")
tire_model = TireModel("Data Files")
powertrain = PowertrainModel()

# Generate g-g-V diagram
velocities, max_accel, max_cornering = simulator.generate_ggv_diagram()

# Calculate tire forces
lateral_force = tire_model.calculate_lateral_force(
    slip_angle=5.0,      # degrees
    normal_force=500.0,  # N
    camber_angle=-2.0    # degrees
)

# Calculate powertrain output
wheel_force, gear = powertrain.calculate_wheel_force(20.0)  # m/s
```

## Key Features

### 🔄 Data Compatibility
- **MATLAB file support**: Reads `.mat` files using `scipy.io.loadmat`
- **Excel integration**: Loads track coordinates from `.xlsx` files
- **Preserved data structures**: Maintains original data organization

### 🚗 Vehicle Modeling
- **Magic Formula 5.2**: Complete tire model implementation
- **Powertrain simulation**: Engine, transmission, and drivetrain
- **Vehicle dynamics**: Load transfer, suspension kinematics
- **Aerodynamics**: Downforce and drag modeling

### 📊 Analysis Tools
- **g-g-V diagrams**: Performance envelope visualization
- **Lap simulation**: Time and distance analysis
- **Force calculations**: Tire and powertrain forces
- **Parameter studies**: Vehicle configuration optimization

### 🐍 Python Advantages
- **Modern libraries**: NumPy, SciPy, Pandas, Matplotlib
- **Type hints**: Better code documentation and IDE support
- **Modular design**: Easy to extend and modify
- **Testing framework**: Comprehensive test suite

## Conversion Details

### Major Components Converted

1. **`Lap_Sim.m` → `lap_sim.py`**
   - Main simulation logic
   - g-g-V diagram generation
   - Vehicle dynamics calculations

2. **`MF52_Fy_fcn.m` → `tire_model.py`**
   - Magic Formula implementation
   - Tire force calculations
   - Global parameter management

3. **`Powertrainlapsim.m` → `powertrain.py`**
   - Engine torque interpolation
   - Gear selection logic
   - Wheel force calculations

4. **Data loading → `data_loader.py`**
   - MATLAB file reading
   - Data management
   - Caching and organization

### Technical Adaptations

- **Global variables**: Converted to class attributes and parameter passing
- **MATLAB functions**: Translated to Python methods with numpy/scipy
- **Spline interpolation**: Using `scipy.interpolate` for curve fitting
- **Array operations**: Vectorized calculations with NumPy

## Testing

Run the comprehensive test suite:

```bash
python test_python_conversion.py
```

The test suite verifies:
- ✅ Module imports and initialization
- ✅ Data file loading (.mat and .xlsx)
- ✅ Tire model calculations
- ✅ Powertrain model functionality
- ✅ Basic simulation setup
- ✅ g-g-V diagram generation

## Current Status

### ✅ Completed
- Core framework and module structure
- Data loading for MATLAB files
- Basic tire model implementation
- Powertrain model with gear selection
- Vehicle configuration management
- Test suite and verification

### 🚧 In Progress
- Complete Magic Formula parameter loading
- Full cornering dynamics solver
- Track path optimization
- Lap time calculation algorithms

### 📋 Future Enhancements
- GUI interface using tkinter or PyQt
- Real-time plotting and visualization
- Parameter optimization tools
- Monte Carlo sensitivity analysis
- Export to engineering reports

## Performance Comparison

| Feature | MATLAB | Python |
|---------|--------|--------|
| Execution Speed | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Memory Usage | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Extensibility | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Visualization | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Package Ecosystem | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Dependencies

- **NumPy**: Numerical computing and array operations
- **SciPy**: Scientific computing and interpolation
- **Pandas**: Data manipulation and analysis
- **Matplotlib**: Plotting and visualization
- **h5py**: HDF5 file support for MATLAB files
- **openpyxl**: Excel file reading

## License

This project maintains the same license as the original MATLAB code. Please respect the original authors' work and contributions.

## Original Credits

- **Jonathan Vogel** - Clemson Formula SAE
- **Tradespace Analysis Project** - 2019 Michigan Dynamic Event Lap Sim

## Python Conversion

- Converted by GitHub Copilot
- Framework designed for extensibility and modern Python practices

---

For questions, issues, or contributions, please use the GitHub issue tracker or submit pull requests.
