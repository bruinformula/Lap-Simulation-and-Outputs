import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator, interp1d
import matplotlib.pyplot as plt
import warnings

# ==============================================================================
# 1. UTILITY AND HELPER FUNCTIONS
# ==============================================================================

def curvature(x, y):
    """
    Calculate the radius of curvature for a path defined by x and y coordinates.
    """
    dx = np.gradient(x)
    dy = np.gradient(y)
    d2x = np.gradient(dx)
    d2y = np.gradient(dy)
    
    curve = np.abs(d2x * dy - dx * d2y) / (dx**2 + dy**2)**1.5
    
    radius = np.full_like(curve, float('inf'))
    mask = curve > 1e-9
    radius[mask] = 1 / curve[mask]
    
    return radius

def powertrain_lapsim(initial_v, powertrain_package, tire_radius):
    """
    Calculates the powertrain's maximum tractive force for a given velocity.
    """
    engine_speed_rpm = powertrain_package['engine_speed_rpm']
    engine_tq_ft_lbs = powertrain_package['engine_tq_ft_lbs']
    primary_reduction = powertrain_package['primary_reduction']
    gear_ratios = powertrain_package['gear_ratios']
    final_drive = powertrain_package['final_drive']
    shift_point_rpm = powertrain_package['shift_point_rpm']
    drivetrain_losses = powertrain_package['drivetrain_losses']

    gear_select = 0
    rpm = shift_point_rpm + 1

    while rpm > shift_point_rpm and gear_select < len(gear_ratios):
        gear_select += 1
        gear_tot = gear_ratios[gear_select - 1] * final_drive * primary_reduction
        rpm = (initial_v / tire_radius) * gear_tot * (60 / (2 * np.pi))

    torque_interp = interp1d(engine_speed_rpm, engine_tq_ft_lbs, bounds_error=False, fill_value=0)
    torque_at_rpm = torque_interp(rpm)

    torque_at_wheels = torque_at_rpm * gear_tot * drivetrain_losses
    fx_lbs = torque_at_wheels / tire_radius

    return fx_lbs, gear_select

# ==============================================================================
# 2. MAIN SIMULATION LOGIC
# ==============================================================================

def run_lap_simulation(track_excel_file, sheet_name):
    """
    Orchestrates the entire lap simulation process.
    """
    print("Starting lap simulation...")

    # --- Section 1: Vehicle & Powertrain Definition ---
    powertrain_package = {
        'engine_speed_rpm': np.arange(6200, 14101, 100),
        'engine_tq_ft_lbs': np.array([41.57, 42.98, 44.43, 45.65, 46.44, 47.09, 47.52, 48.58, 49.57, 50.41, 51.43, 51.48, 51, 49.311, 48.94, 48.66, 49.62, 49.60, 47.89, 47.91, 48.09, 48.57, 49.07, 49.31, 49.58, 49.56, 49.84, 50.10, 50.00, 50.00, 50.75, 51.25, 52.01, 52.44, 52.59, 52.73, 53.34, 53.72, 52.11, 52.25, 51.66, 50.5, 50.34, 50.50, 50.50, 50.55, 50.63, 50.17, 50.80, 49.73, 49.35, 49.11, 48.65, 48.28, 48.28, 47.99, 47.68, 47.43, 47.07, 46.67, 45.49, 45.37, 44.67, 43.8, 43.0, 42.3, 42.00, 41.96, 41.70, 40.43, 39.83, 38.60, 38.46, 37.56, 36.34, 35.35, 33.75, 33.54, 32.63, 31.63]),
        'primary_reduction': 76 / 36,
        'gear_ratios': np.array([33/12, 32/16, 30/18, 26/18, 30/23, 29/24]),
        'final_drive': 40 / 12,
        'shift_point_rpm': 14000,
        'drivetrain_losses': 0.85
    }
    W_lbs = 660
    tire_radius_ft = 9.05 / 12
    g = 32.2
    max_lateral_g = 1.8 
    max_braking_g = -2.0

    # --- Section 2: Generate GGV Performance Curves ---
    velocity_range_fps = np.arange(1, 151, 1)
    ax_g_values = [powertrain_lapsim(v, powertrain_package, tire_radius_ft)[0] / W_lbs for v in velocity_range_fps]
    accel_g_curve = PchipInterpolator(velocity_range_fps, ax_g_values)
    print("Generated GGV curves.")

    # --- Section 3: Load and Process Track Data ---
    print(f"Reading sheet '{sheet_name}' from '{track_excel_file}'...")
    track_data = pd.read_excel(track_excel_file, sheet_name=sheet_name, header=0)
    
    # *** THIS IS THE NEW, ROBUST DATA CONVERSION BLOCK ***
    try:
        # Identify coordinate columns by their integer position (B, C, D, E)
        coord_cols = track_data.columns[1:5] 
        # Convert these columns to numeric types, errors will stop execution
        track_data[coord_cols] = track_data[coord_cols].apply(pd.to_numeric, errors='raise')
    except (ValueError, TypeError) as e:
        print("\n❌ DATA ERROR: Could not convert track coordinates to numbers.")
        print("Please check your Excel file for non-numeric data in the coordinate columns (B, C, D, E).")
        print(f"Error details: {e}")
        return # Stop the simulation
    
    outside_x = track_data.iloc[:, 1].values
    outside_y = track_data.iloc[:, 2].values
    inside_x = track_data.iloc[:, 3].values
    inside_y = track_data.iloc[:, 4].values
    
    path_x = (outside_x + inside_x) / 2
    path_y = (outside_y + inside_y) / 2
    
    path_radii = curvature(path_x, path_y)
    segment_distances = np.sqrt(np.diff(path_x, append=path_x[0])**2 + np.diff(path_y, append=path_y[0])**2)
    cumulative_distance = np.cumsum(segment_distances)
    print(f"Loaded track data: {len(path_x)} points, total distance: {cumulative_distance[-1]:.2f} ft.")

    # --- Section 4: Simulate the Lap ---
    v_max_cornering = np.sqrt(max_lateral_g * g * path_radii)

    velocity_fwd = np.zeros_like(v_max_cornering)
    for i in range(1, len(velocity_fwd)):
        v_prev = velocity_fwd[i-1]
        ax_g = accel_g_curve(v_prev)
        v_new_squared = v_prev**2 + 2 * ax_g * g * segment_distances[i-1]
        v_new = np.sqrt(max(0, v_new_squared))
        velocity_fwd[i] = min(v_new, v_max_cornering[i])

    velocity_bwd = np.zeros_like(v_max_cornering)
    velocity_bwd[-1] = velocity_fwd[-1]
    for i in range(len(velocity_bwd) - 2, -1, -1):
        v_next = velocity_bwd[i+1]
        v_new_squared = v_next**2 - 2 * max_braking_g * g * segment_distances[i]
        v_new = np.sqrt(max(0, v_new_squared))
        velocity_bwd[i] = min(v_new, v_max_cornering[i], velocity_fwd[i])

    final_velocity_fps = np.minimum(velocity_fwd, velocity_bwd)
    final_velocity_fps[final_velocity_fps < 1e-6] = 1e-6
    segment_times = segment_distances / final_velocity_fps
    total_lap_time = np.sum(segment_times)
    print(f"Simulation complete. Estimated Lap Time: {total_lap_time:.3f} seconds.")

    # --- Section 5: Calculate Final Metrics ---
    final_velocity_mph = final_velocity_fps * (3600 / 5280)
    lat_accel_g = final_velocity_fps**2 / (path_radii * g)
    long_accel_g = np.gradient(final_velocity_fps, segment_distances) * final_velocity_fps / g
    
    return total_lap_time, cumulative_distance, final_velocity_mph, lat_accel_g, long_accel_g

# ==============================================================================
# 3. EXECUTION AND PLOTTING
# ==============================================================================

if __name__ == '__main__':
    track_file = 'Endurance_Coordinates_1.xlsx'
    sheet_to_read = 'Scaled'
    
    try:
        # The run_lap_simulation function will now return None if there's a data error
        results = run_lap_simulation(track_file, sheet_name=sheet_to_read)

        # Only proceed to plotting if the simulation ran successfully
        if results:
            lap_time, dist, vel, lat_g, long_g = results
            
            # --- Plotting Results ---
            plt.figure(figsize=(12, 6))
            plt.plot(dist, vel, label='Velocity')
            plt.xlabel('Distance Along Track (ft)')
            plt.ylabel('Velocity (mph)')
            plt.title(f'Velocity Profile | Lap Time: {lap_time:.3f} s')
            plt.grid(True)
            plt.legend()
            
            plt.figure(figsize=(8, 8))
            plt.scatter(lat_g, long_g, s=5, alpha=0.5)
            plt.xlabel('Lateral Acceleration (G)')
            plt.ylabel('Longitudinal Acceleration (G)')
            plt.title('G-G Diagram')
            plt.grid(True)
            plt.axis('equal')
            plt.xlim(-2.5, 2.5)
            plt.ylim(-2.5, 2.5)

            plt.show()

    except FileNotFoundError:
        print(f"\n❌ ERROR: The file '{track_file}' was not found.")
        print("Please make sure the Excel file is in the same directory as this script.")
    except ValueError as e:
         if "Worksheet named" in str(e):
              print(f"\n❌ ERROR: Could not find the sheet named '{sheet_to_read}' in '{track_file}'.")
              print("Please check the sheet name for typos.")
         else:
              print(f"\nAn unexpected error occurred: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")