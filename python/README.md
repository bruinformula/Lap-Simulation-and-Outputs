# Python Lap Simulation

This directory contains all Python implementations of the MATLAB lap simulation code.

## Directory Structure

```
python/
├── README.md                    # This file
├── CONVERSION_SUMMARY.md        # Detailed conversion notes
├── requirements.txt            # Python dependencies
├── simulation_results.csv      # Simulation output data
├── python_main.py              # Main execution script (equivalent to main.m)
├── enhanced_lap_sim.py         # Enhanced simulation with improved physics
├── lap_simulation/             # Core simulation package
│   ├── __init__.py            # Package initialization
│   ├── data_loader.py         # Data loading utilities
│   ├── tire_model.py          # Tire modeling (Magic Formula 5.2)
│   ├── powertrain.py          # Engine and transmission models
│   └── lap_sim.py             # Main lap simulation logic
├── demos/                      # Demonstration scripts
│   ├── complete_conversion_demo.py  # Complete conversion demonstration
│   └── demo_python_conversion.py   # Basic conversion demo
├── visualization/              # Plotting and visualization utilities
│   ├── plot_racing_track.py    # Track plotting utilities
│   ├── quick_track_plot.py     # Quick track visualization
│   ├── simple_track_plot.py    # Simple plotting functions
│   └── ultra_smooth_track.py   # High-resolution track plotting
├── testing/                    # Testing and validation
│   └── test_python_conversion.py   # Testing utilities
└── plots/                      # Generated visualization files
    ├── acceleration_plots.png  # Acceleration vs distance/time plots
    ├── racing_track.png        # Track layout visualizations
    ├── tire_demo.png           # Tire model demonstrations
    ├── ggv_demo.png           # G-G-V diagram plots
    └── ... (other plot files)
```

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
   python enhanced_lap_sim.py
   ```

4. Run demonstrations:
   ```bash
   python demos/complete_conversion_demo.py
   python demos/demo_python_conversion.py
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
