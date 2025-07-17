"""
Lap Simulation Package - Python Conversion from MATLAB
======================================================

This package converts the MATLAB lap simulation code to Python while maintaining
compatibility with the original data files (.mat format).

Modules:
--------
- lap_sim: Main lap simulation function
- tire_model: Magic Formula tire model implementation  
- powertrain: Engine and transmission modeling
- vehicle_dynamics: Vehicle dynamics calculations
- data_loader: Utilities for loading MATLAB data files
"""

from .lap_sim import lap_sim
from .tire_model import MF52_Fy_fcn
from .powertrain import powertrain_lapsim
from .data_loader import load_mat_data

__version__ = "1.0.0"
__author__ = "Converted from MATLAB by GitHub Copilot"
