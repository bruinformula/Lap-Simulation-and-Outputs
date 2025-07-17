"""
Data Export and Results Management Module
========================================

Handles saving simulation results and data export functionality.
"""

import numpy as np
from .output_utils import get_data_path


def save_simulation_results(distance, A_long_g, A_lat_g, roll_angle, loads=None):
    """
    Save simulation results to CSV file.
    
    Parameters:
    -----------
    distance : np.ndarray
        Distance array in feet
    A_long_g : np.ndarray
        Longitudinal acceleration in g-force
    A_lat_g : np.ndarray
        Lateral acceleration in g-force
    roll_angle : np.ndarray
        Roll angle in degrees
    loads : dict, optional
        Dictionary with wheel load arrays
    """
    # Create the main results data
    results_data = np.column_stack([distance, A_long_g, A_lat_g, roll_angle])
    
    # Header for main results
    header = 'Distance_ft,Longitudinal_Accel_g,Lateral_Accel_g,Roll_Angle_deg'
    
    # If loads are provided, add them to the results
    if loads is not None:
        loads_data = np.column_stack([loads['FL'], loads['FR'], loads['RL'], loads['RR']])
        results_data = np.column_stack([results_data, loads_data])
        header += ',Load_FL_lbs,Load_FR_lbs,Load_RL_lbs,Load_RR_lbs'
    
    # Save results to file
    results_file = get_data_path('simulation_results.csv')
    np.savetxt(results_file, results_data, 
               delimiter=',', 
               header=header,
               comments='')
    
    return results_file


def create_summary_report(distance, A_long_g, A_lat_g, roll_angle, loads=None):
    """
    Create a summary report of simulation results.
    
    Parameters:
    -----------
    distance : np.ndarray
        Distance array in feet
    A_long_g : np.ndarray
        Longitudinal acceleration in g-force
    A_lat_g : np.ndarray
        Lateral acceleration in g-force
    roll_angle : np.ndarray
        Roll angle in degrees
    loads : dict, optional
        Dictionary with wheel load arrays
        
    Returns:
    --------
    dict
        Summary statistics
    """
    summary = {
        'total_distance': distance[-1] if len(distance) > 0 else 0,
        'max_lateral_accel': np.max(np.abs(A_lat_g)),
        'max_longitudinal_accel': np.max(A_long_g),
        'max_deceleration': np.min(A_long_g),
        'max_roll_angle': np.max(np.abs(roll_angle)),
        'avg_lateral_accel': np.mean(np.abs(A_lat_g)),
        'avg_longitudinal_accel': np.mean(A_long_g)
    }
    
    if loads is not None:
        summary['max_wheel_load'] = max(np.max(loads['FL']), np.max(loads['FR']), 
                                       np.max(loads['RL']), np.max(loads['RR']))
        summary['min_wheel_load'] = min(np.min(loads['FL']), np.min(loads['FR']), 
                                       np.min(loads['RL']), np.min(loads['RR']))
    
    return summary


def print_summary_report(summary):
    """
    Print a formatted summary report.
    
    Parameters:
    -----------
    summary : dict
        Summary statistics from create_summary_report()
    """
    print("\n" + "="*50)
    print("LAP SIMULATION SUMMARY REPORT")
    print("="*50)
    print(f"Total Distance: {summary['total_distance']:.1f} ft")
    print(f"Max Lateral Acceleration: {summary['max_lateral_accel']:.2f} g")
    print(f"Max Longitudinal Acceleration: {summary['max_longitudinal_accel']:.2f} g")
    print(f"Max Deceleration: {summary['max_deceleration']:.2f} g")
    print(f"Max Roll Angle: {summary['max_roll_angle']:.2f} degrees")
    print(f"Average Lateral Acceleration: {summary['avg_lateral_accel']:.2f} g")
    print(f"Average Longitudinal Acceleration: {summary['avg_longitudinal_accel']:.2f} g")
    
    if 'max_wheel_load' in summary:
        print(f"Max Wheel Load: {summary['max_wheel_load']:.1f} lbs")
        print(f"Min Wheel Load: {summary['min_wheel_load']:.1f} lbs")
    
    print("="*50)
