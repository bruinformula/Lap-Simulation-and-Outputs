# Python Lap Simulation

This directory contains all Python implementations of the MATLAB lap simulation code.

## Directory Structure

```
python/
├── README.md                    # This file
├── CONVERSION_SUMMARY.md        # Detailed conversion notes
├── requirements.txt            # Python dependencies
├── vehicle_config.py           # Vehicle parameter configuration
├── python_main.py              # Main execution script (equivalent to main.m)
├── lap_simulation/             # Core simulation package
│   ├── __init__.py            # Package initialization
│   ├── data_loader.py         # Data loading utilities
│   ├── tire_model.py          # Tire modeling (Magic Formula 5.2)
│   ├── powertrain.py          # Engine and transmission models
│   ├── lap_sim.py             # Main lap simulation logic
│   └── output_utils.py        # Output file management utilities
├── demos/                      # Demonstration scripts
│   ├── complete_conversion_demo.py  # Complete conversion demonstration
│   ├── demo_python_conversion.py   # Basic conversion demo
│   ├── enhanced_lap_sim.py    # Enhanced simulation with improved physics
│   └── vehicle_config_demo.py # Configuration examples and comparisons
├── visualization/              # Plotting and visualization utilities
│   ├── plot_racing_track.py    # Track plotting utilities
│   ├── quick_track_plot.py     # Quick track visualization
│   ├── simple_track_plot.py    # Simple plotting functions
│   └── ultra_smooth_track.py   # High-resolution track plotting
├── testing/                    # Testing and validation
│   └── test_python_conversion.py   # Testing utilities
├── docs/                       # Documentation
│   ├── README.md              # Documentation index
│   ├── USER_GUIDE.md          # User documentation
│   ├── DEVELOPMENT.md         # Developer guidelines
│   └── API.md                 # Technical reference
└── outputs/                    # Generated output files
    ├── plots/                  # All PNG visualizations
    │   ├── acceleration_plots.png  # Acceleration vs distance/time plots
    │   ├── racing_track.png        # Track layout visualizations
    │   ├── tire_demo.png           # Tire model demonstrations
    │   ├── ggv_demo.png           # G-G-V diagram plots
    │   └── ... (other plot files)
    └── data/                   # CSV and other data files
        └── simulation_results.csv  # Simulation output data
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **📖 [User Guide](docs/USER_GUIDE.md)** - Start here for basic usage
- **🔧 [Development Guide](docs/DEVELOPMENT.md)** - For developers and contributors  
- **📚 [API Reference](docs/API.md)** - Complete function documentation
- **📋 [Documentation Index](docs/README.md)** - Full documentation overview

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

## Features

- **Complete MATLAB Conversion**: All MATLAB functionality translated to Python
- **High-Resolution Data**: 1000-point racing line vs original 151 points
- **Realistic Physics**: Proper signed lateral acceleration and realistic longitudinal acceleration
- **Modular Design**: Object-oriented structure for easy maintenance and extension
- **Data Compatibility**: Direct loading of MATLAB .mat files and Excel data
- **Comprehensive Plotting**: Track visualization matching MATLAB output quality

## Key Components

- **Data Loader**: Handles .mat files, Excel sheets, and tire data
- **Tire Model**: Magic Formula 5.2 implementation with lateral force calculations
- **Powertrain**: Engine torque curves, transmission, and drivetrain modeling
- **Lap Simulator**: Main physics integration and vehicle dynamics
- **Plotting**: High-quality track and data visualization

## Performance

The Python implementation achieves the same results as MATLAB with:
- 3x fewer lines of code (367 vs 1115 lines)
- Vectorized operations for better performance
- Modern object-oriented design
- Simplified physics models while maintaining accuracy
