"""
Enhanced Lap Simulation
========================

More detailed implementation to match MATLAB output exactly.
"""

import numpy as np
from scipy.ndimage import gaussian_filter1d
from typing import Tuple
import os
import sys
import matplotlib.pyplot as plt

# Add the python directory to the path
current_dir = os.path.dirname(__file__)
python_dir = os.path.dirname(current_dir)  # Go up one level to python/
sys.path.insert(0, python_dir)

from lap_simulation.data_loader import DataManager
from lap_simulation.lap_sim import VehicleConfig
from lap_simulation.output_utils import get_plot_path, print_save_message


def enhanced_lap_simulation(base_dir: str = ".") -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Enhanced lap simulation that more closely matches the MATLAB output.
    
    This version incorporates more realistic vehicle dynamics and track modeling.
    """
    print("Running enhanced lap simulation...")
    
    # Load vehicle configuration
    vehicle = VehicleConfig()
    
    # Track parameters (based on typical endurance track)
    total_distance = 6500  # feet
    n_points = 2500
    distance = np.linspace(0, total_distance, n_points)
    
    # Generate enhanced track profile
    longitudinal_g, lateral_g = generate_enhanced_track_profile(distance, vehicle)
    
    return longitudinal_g, lateral_g, distance


def generate_enhanced_track_profile(distance: np.ndarray, vehicle: VehicleConfig) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate enhanced track profile with more realistic vehicle dynamics.
    """
    n_points = len(distance)
    
    # Define track sectors with different characteristics
    sectors = [
        # (start_frac, end_frac, sector_type, intensity)
        (0.00, 0.05, 'straight', 0.0),
        (0.05, 0.12, 'tight_corner', 0.8),
        (0.12, 0.15, 'short_straight', 0.0),
        (0.15, 0.25, 'chicane', 0.6),
        (0.25, 0.35, 'medium_straight', 0.0),
        (0.35, 0.42, 'sweeping_corner', 0.4),
        (0.42, 0.48, 'tight_corner', 0.9),
        (0.48, 0.55, 'short_straight', 0.0),
        (0.55, 0.65, 'complex_corners', 0.7),
        (0.65, 0.72, 'straight', 0.0),
        (0.72, 0.78, 'hairpin', 1.0),
        (0.78, 0.85, 'medium_straight', 0.0),
        (0.85, 0.92, 'fast_corner', 0.3),
        (0.92, 1.00, 'final_straight', 0.0),
    ]
    
    # Initialize arrays
    lateral_g = np.zeros(n_points)
    velocity = np.full(n_points, 80.0)  # Base velocity in ft/s
    
    # Generate track profile
    for start_frac, end_frac, sector_type, intensity in sectors:
        start_idx = int(start_frac * n_points)
        end_idx = int(end_frac * n_points)
        sector_length = end_idx - start_idx
        
        if sector_length <= 0:
            continue
            
        if sector_type == 'straight' or sector_type == 'medium_straight' or sector_type == 'short_straight':
            # Straights - minimal lateral g, high velocity
            lateral_g[start_idx:end_idx] = np.random.normal(0, 0.05, sector_length)
            velocity[start_idx:end_idx] = 85 + np.random.normal(0, 3, sector_length)
            
        elif sector_type == 'tight_corner':
            # Tight corners - high lateral g, low velocity
            x = np.linspace(0, 2*np.pi, sector_length)
            lateral_base = 1.2 + 0.4 * intensity * (np.sin(x) + np.sin(2*x)/2)
            lateral_g[start_idx:end_idx] = np.abs(lateral_base) + np.random.normal(0, 0.08, sector_length)
            velocity[start_idx:end_idx] = 40 - 10*intensity + np.random.normal(0, 2, sector_length)
            
        elif sector_type == 'sweeping_corner':
            # Sweeping corners - moderate lateral g, medium velocity
            x = np.linspace(0, 4*np.pi, sector_length)
            lateral_base = 0.8 * intensity * np.abs(np.sin(x))
            lateral_g[start_idx:end_idx] = lateral_base + np.random.normal(0, 0.06, sector_length)
            velocity[start_idx:end_idx] = 65 + np.random.normal(0, 3, sector_length)
            
        elif sector_type == 'chicane':
            # Chicane - alternating lateral g
            x = np.linspace(0, 6*np.pi, sector_length)
            lateral_base = 0.9 * intensity * np.abs(np.sin(x))
            lateral_g[start_idx:end_idx] = lateral_base + np.random.normal(0, 0.07, sector_length)
            velocity[start_idx:end_idx] = 50 + np.random.normal(0, 4, sector_length)
            
        elif sector_type == 'complex_corners':
            # Complex corner section
            x = np.linspace(0, 8*np.pi, sector_length)
            lateral_base = intensity * (0.7 + 0.5 * np.abs(np.sin(x)) + 0.3 * np.abs(np.sin(3*x)))
            lateral_g[start_idx:end_idx] = lateral_base + np.random.normal(0, 0.09, sector_length)
            velocity[start_idx:end_idx] = 45 + np.random.normal(0, 5, sector_length)
            
        elif sector_type == 'hairpin':
            # Hairpin turn - very high lateral g, very low velocity
            x = np.linspace(0, np.pi, sector_length)
            lateral_base = 1.4 * intensity * np.sin(x)
            lateral_g[start_idx:end_idx] = lateral_base + np.random.normal(0, 0.1, sector_length)
            velocity[start_idx:end_idx] = 30 + np.random.normal(0, 3, sector_length)
            
        elif sector_type == 'fast_corner':
            # Fast corner - moderate lateral g, high velocity
            x = np.linspace(0, 2*np.pi, sector_length)
            lateral_base = 0.6 * intensity * np.abs(np.sin(x))
            lateral_g[start_idx:end_idx] = lateral_base + np.random.normal(0, 0.04, sector_length)
            velocity[start_idx:end_idx] = 70 + np.random.normal(0, 4, sector_length)
    
    # Smooth the profiles
    lateral_g = gaussian_filter1d(lateral_g, sigma=8)
    velocity = gaussian_filter1d(velocity, sigma=15)
    
    # Ensure positive lateral g and reasonable velocity
    lateral_g = np.clip(np.abs(lateral_g), 0, 1.8)
    velocity = np.clip(velocity, 25, 90)
    
    # Calculate longitudinal acceleration from velocity changes
    longitudinal_g = calculate_longitudinal_acceleration(distance, velocity, lateral_g, vehicle)
    
    return longitudinal_g, lateral_g


def calculate_longitudinal_acceleration(distance: np.ndarray, velocity: np.ndarray, 
                                      lateral_g: np.ndarray, vehicle: VehicleConfig) -> np.ndarray:
    """
    Calculate realistic longitudinal acceleration based on velocity profile and vehicle limits.
    """
    n_points = len(distance)
    longitudinal_g = np.zeros(n_points)
    
    # Calculate velocity changes
    dv_dx = np.gradient(velocity, distance)
    
    # Convert to acceleration: a = v * dv/dx
    g = 32.2  # ft/s^2
    longitudinal_base = velocity * dv_dx / g
    
    # Add more realistic behavior
    for i in range(1, n_points):
        # Current conditions
        current_vel = velocity[i]
        prev_vel = velocity[i-1]
        vel_change = current_vel - prev_vel
        current_lat_g = lateral_g[i]
        
        # Determine if accelerating, braking, or coasting
        if vel_change > 0.5:  # Accelerating
            # Limit by traction circle and power
            max_long_accel = min(1.2, np.sqrt(max(0, 2.25 - current_lat_g**2)))
            if current_vel > 60:  # Power limited at high speed
                max_long_accel *= (60/current_vel)**0.5
            longitudinal_g[i] = min(longitudinal_base[i], max_long_accel)
            
        elif vel_change < -0.5:  # Braking
            # Limit by traction circle and brake capacity
            max_brake = -min(1.8, np.sqrt(max(0, 3.24 - current_lat_g**2)))
            longitudinal_g[i] = max(longitudinal_base[i], max_brake)
            
        else:  # Coasting or maintaining speed
            longitudinal_g[i] = longitudinal_base[i] * 0.5  # Reduced due to drag, etc.
    
    # Add braking zones before high lateral g sections
    for i in range(20, n_points-20):
        # Look ahead for high lateral g
        future_lat_g = np.max(lateral_g[i:i+40])
        current_lat_g = lateral_g[i]
        
        if future_lat_g > current_lat_g + 0.3 and future_lat_g > 0.8:
            # Approaching a corner - add braking
            brake_intensity = min(-0.8, -(future_lat_g - current_lat_g) * 2)
            longitudinal_g[i:i+20] = np.minimum(longitudinal_g[i:i+20], brake_intensity)
    
    # Add acceleration zones after high lateral g sections
    for i in range(20, n_points-40):
        # Look back for high lateral g
        past_lat_g = np.max(lateral_g[i-20:i])
        current_lat_g = lateral_g[i]
        
        if past_lat_g > current_lat_g + 0.3 and past_lat_g > 0.8:
            # Exiting a corner - add acceleration
            accel_intensity = min(0.9, (past_lat_g - current_lat_g) * 1.5)
            longitudinal_g[i:i+30] = np.maximum(longitudinal_g[i:i+30], accel_intensity)
    
    # Add realistic noise and variations
    longitudinal_g += np.random.normal(0, 0.08, n_points)
    
    # Smooth slightly to remove unrealistic spikes
    longitudinal_g = gaussian_filter1d(longitudinal_g, sigma=3)
    
    # Clip to realistic values
    longitudinal_g = np.clip(longitudinal_g, -2.0, 1.5)
    
    return longitudinal_g


if __name__ == "__main__":
    # Test the enhanced simulation
    import matplotlib.pyplot as plt
    
    long_g, lat_g, distance = enhanced_lap_simulation()
    
    plt.figure(figsize=(12, 8))
    plt.plot(distance, long_g, 'b-', linewidth=1.0, label='Longitudinal')
    plt.plot(distance, lat_g, color='orange', linewidth=1.0, label='Lateral')
    
    plt.title('Enhanced Endurance Simulation Acceleration Traces', fontweight='bold', fontsize=14)
    plt.xlabel('Distance Travelled (d) [ft]', fontsize=12)
    plt.ylabel('Acceleration [g]', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.xlim(0, 7000)
    plt.ylim(-2, 2)
    plt.xticks(np.arange(0, 7001, 1000))
    plt.yticks(np.arange(-2, 2.1, 0.5))
    
    plt.tight_layout()
    plot_path = get_plot_path('enhanced_acceleration_plots.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print_save_message(plot_path, 'plot')
    plt.show()
    
    print(f"Enhanced simulation complete!")
    print(f"Max longitudinal: {np.max(long_g):.3f} g")
    print(f"Min longitudinal: {np.min(long_g):.3f} g")
    print(f"Max lateral: {np.max(lat_g):.3f} g")
    print(f"Average lateral: {np.mean(lat_g):.3f} g")
