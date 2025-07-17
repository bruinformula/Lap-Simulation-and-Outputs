"""
Powertrain Module
=================

Engine and transmission modeling for lap simulation.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional


class PowertrainModel:
    """
    Powertrain model including engine, transmission, and drivetrain.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize powertrain model.
        
        Parameters:
        -----------
        config : Dict[str, Any], optional
            Powertrain configuration parameters
        """
        if config is None:
            config = self._default_config()
            
        self.engine_speed = np.array(config['engine_speed'])  # RPM
        self.engine_torque = np.array(config['engine_torque'])  # N-m
        self.primary_reduction = config['primary_reduction']
        self.gear_ratios = np.array(config['gear_ratios'])
        self.final_drive = config['final_drive']
        self.shift_point = config['shift_point']  # RPM
        self.drivetrain_losses = config['drivetrain_losses']  # efficiency
        self.shift_time = config['shift_time']  # seconds
        self.tire_radius = config['tire_radius']  # meters
        
    def _default_config(self) -> Dict[str, Any]:
        """Default powertrain configuration matching MATLAB version."""
        return {
            'engine_speed': list(range(6200, 14200, 100)),  # RPM
            'engine_torque': [41.57, 42.98, 44.43, 45.65, 46.44, 47.09, 47.52, 48.58, 49.57, 50.41, 
                             51.43, 51.48, 51, 49.311, 48.94, 48.66, 49.62, 49.60, 47.89, 47.91, 
                             48.09, 48.57, 49.07, 49.31, 49.58, 49.56, 49.84, 50.10, 50.00, 50.00, 
                             50.75, 51.25, 52.01, 52.44, 52.59, 52.73, 53.34, 53.72, 52.11, 52.25, 
                             51.66, 50.5, 50.34, 50.50, 50.50, 50.55, 50.63, 50.17, 50.80, 49.73, 
                             49.35, 49.11, 48.65, 48.28, 48.28, 47.99, 47.68, 47.43, 47.07, 46.67, 
                             45.49, 45.37, 44.67, 43.8, 43.0, 42.3, 42.00, 41.96, 41.70, 40.43, 
                             39.83, 38.60, 38.46, 37.56, 36.34, 35.35, 33.75, 33.54, 32.63, 31.63],  # N-m
            'primary_reduction': 76/36,
            'gear_ratios': [33/12, 32/16, 30/18, 26/18, 30/23, 29/24],
            'final_drive': 40/12,
            'shift_point': 14000,  # RPM
            'drivetrain_losses': 0.85,  # 85% efficiency
            'shift_time': 0.25,  # seconds
            'tire_radius': 9.05/12/3.28,  # converted to meters
        }
    
    def calculate_gear_selection(self, velocity_ms: float) -> int:
        """
        Calculate optimal gear selection for given velocity.
        
        Parameters:
        -----------
        velocity_ms : float
            Vehicle velocity [m/s]
            
        Returns:
        --------
        int
            Selected gear (1-indexed)
        """
        gear = 1
        rpm = 15000  # Start with high RPM
        
        while rpm > self.shift_point and gear <= len(self.gear_ratios):
            total_gear_ratio = (self.gear_ratios[gear-1] * 
                               self.final_drive * 
                               self.primary_reduction)
            rpm = velocity_ms * total_gear_ratio / self.tire_radius * 60 / (2 * np.pi)
            
            if rpm <= self.shift_point:
                break
            gear += 1
            
        return min(gear, len(self.gear_ratios))
    
    def calculate_engine_torque(self, rpm: float) -> float:
        """
        Calculate engine torque at given RPM using interpolation.
        
        Parameters:
        -----------
        rpm : float
            Engine speed [RPM]
            
        Returns:
        --------
        float
            Engine torque [N-m]
        """
        # Bound RPM to engine speed range
        rpm = np.clip(rpm, self.engine_speed[0], self.engine_speed[-1])
        
        # Linear interpolation
        torque = np.interp(rpm, self.engine_speed, self.engine_torque)
        
        return torque
    
    def calculate_wheel_force(self, velocity_ms: float, launch_boost: bool = False) -> Tuple[float, int]:
        """
        Calculate force at wheels for given velocity.
        
        Parameters:
        -----------
        velocity_ms : float
            Vehicle velocity [m/s]
        launch_boost : bool
            Whether to apply launch control boost
            
        Returns:
        --------
        Tuple[float, int]
            (wheel_force_N, selected_gear)
        """
        # Minimum velocity for calculation
        min_velocity = 7.5 if not launch_boost else 10.0
        effective_velocity = max(min_velocity, velocity_ms)
        
        # Calculate gear selection
        gear = self.calculate_gear_selection(effective_velocity)
        
        # Calculate total gear ratio
        total_gear_ratio = (self.gear_ratios[gear-1] * 
                           self.final_drive * 
                           self.primary_reduction)
        
        # Calculate engine RPM
        rpm = effective_velocity * total_gear_ratio / self.tire_radius * 60 / (2 * np.pi)
        
        # Calculate engine torque
        engine_torque = self.calculate_engine_torque(rpm)
        
        # Calculate wheel torque
        wheel_torque = engine_torque * total_gear_ratio * self.drivetrain_losses
        
        # Calculate wheel force
        wheel_force = wheel_torque / self.tire_radius
        
        return wheel_force, gear


def powertrain_lapsim(initial_velocity_ms: float, powertrain_config: Optional[Dict[str, Any]] = None) -> Tuple[float, int]:
    """
    Lap simulation powertrain function (Python equivalent of Powertrainlapsim.m).
    
    Parameters:
    -----------
    initial_velocity_ms : float
        Initial velocity [m/s]
    powertrain_config : Dict[str, Any], optional
        Powertrain configuration
        
    Returns:
    --------
    Tuple[float, int]
        (force_N, selected_gear)
    """
    # Create powertrain model
    powertrain = PowertrainModel(powertrain_config)
    
    # Calculate wheel force and gear
    force_N, gear = powertrain.calculate_wheel_force(initial_velocity_ms)
    
    return force_N, gear


class TransmissionModel:
    """
    Detailed transmission model with shift logic.
    """
    
    def __init__(self, gear_ratios: List[float], shift_points: List[float], 
                 shift_time: float = 0.25):
        """
        Initialize transmission model.
        
        Parameters:
        -----------
        gear_ratios : List[float]
            Transmission gear ratios
        shift_points : List[float]
            Shift points [RPM] for each gear
        shift_time : float
            Time required for gear shift [seconds]
        """
        self.gear_ratios = np.array(gear_ratios)
        self.shift_points = np.array(shift_points)
        self.shift_time = shift_time
        self.current_gear = 1
        self.shift_in_progress = False
        self.shift_start_time = 0.0
        
    def update(self, current_time: float, engine_rpm: float) -> Tuple[int, bool]:
        """
        Update transmission state and determine gear selection.
        
        Parameters:
        -----------
        current_time : float
            Current simulation time [seconds]
        engine_rpm : float
            Current engine RPM
            
        Returns:
        --------
        Tuple[int, bool]
            (current_gear, shift_in_progress)
        """
        # Check if shift is in progress
        if self.shift_in_progress:
            if current_time - self.shift_start_time >= self.shift_time:
                self.shift_in_progress = False
            else:
                return self.current_gear, True
                
        # Check for upshift
        if (self.current_gear < len(self.gear_ratios) and 
            engine_rpm >= self.shift_points[self.current_gear - 1]):
            self._initiate_shift(current_time, self.current_gear + 1)
            
        # Check for downshift (simplified logic)
        elif (self.current_gear > 1 and 
              engine_rpm < self.shift_points[self.current_gear - 2] * 0.8):
            self._initiate_shift(current_time, self.current_gear - 1)
            
        return self.current_gear, self.shift_in_progress
    
    def _initiate_shift(self, current_time: float, target_gear: int):
        """Initiate gear shift."""
        self.shift_in_progress = True
        self.shift_start_time = current_time
        self.current_gear = target_gear
    
    def get_current_ratio(self) -> float:
        """Get current gear ratio."""
        return self.gear_ratios[self.current_gear - 1]
