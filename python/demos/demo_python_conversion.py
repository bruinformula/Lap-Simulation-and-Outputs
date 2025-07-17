"""
Demonstration Script - Python Lap Simulation
============================================

This script demonstrates the key features of the Python conversion.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Add the python directory to the path
current_dir = os.path.dirname(__file__)
python_dir = os.path.dirname(current_dir)  # Go up one level to python/
sys.path.insert(0, python_dir)

from lap_simulation.powertrain import PowertrainModel, powertrain_lapsim
from lap_simulation.tire_model import TireModel
from lap_simulation.output_utils import get_plot_path, print_save_message


def demo_powertrain():
    """Demonstrate powertrain model functionality."""
    print("🚗 Powertrain Model Demonstration")
    print("=" * 40)
    
    # Create powertrain model
    powertrain = PowertrainModel()
    
    # Test different velocities
    velocities_ms = np.linspace(5, 40, 20)  # m/s
    forces = []
    gears = []
    
    for v in velocities_ms:
        force, gear = powertrain.calculate_wheel_force(v)
        forces.append(force)
        gears.append(gear)
    
    # Convert to more familiar units
    velocities_mph = velocities_ms * 2.237  # Convert to mph
    forces_lbf = np.array(forces) * 0.2248  # Convert to lbf
    
    # Print some key points
    print(f"At 20 mph: {forces_lbf[5]:.0f} lbf, Gear {gears[5]}")
    print(f"At 40 mph: {forces_lbf[10]:.0f} lbf, Gear {gears[10]}")
    print(f"At 60 mph: {forces_lbf[15]:.0f} lbf, Gear {gears[15]}")
    
    # Plot results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Force vs velocity
    ax1.plot(velocities_mph, forces_lbf, 'b-', linewidth=2, marker='o')
    ax1.set_xlabel('Velocity [mph]')
    ax1.set_ylabel('Wheel Force [lbf]')
    ax1.set_title('Powertrain Force vs Velocity')
    ax1.grid(True, alpha=0.3)
    
    # Gear vs velocity
    ax2.plot(velocities_mph, gears, 'r-', linewidth=2, marker='s')
    ax2.set_xlabel('Velocity [mph]')
    ax2.set_ylabel('Selected Gear')
    ax2.set_title('Gear Selection vs Velocity')
    ax2.set_ylim(0, 7)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = get_plot_path('powertrain_demo.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print_save_message(plot_path, 'plot')
    plt.show()


def demo_tire_model():
    """Demonstrate tire model functionality."""
    print("\n🏎️ Tire Model Demonstration")
    print("=" * 40)
    
    data_dir = os.path.join(current_dir, "Data Files")
    if not os.path.exists(data_dir):
        print("⚠ Data Files directory not found, skipping tire demo")
        return
        
    try:
        tire_model = TireModel(data_dir)
        
        # Test longitudinal forces
        slip_ratios = np.linspace(0, 0.2, 20)
        normal_force = 500  # N
        forces_N = []
        
        for sr in slip_ratios:
            force = tire_model.calculate_longitudinal_force(sr, normal_force)
            forces_N.append(force[0])
        
        forces_lbf = np.array(forces_N) * 0.2248
        
        print(f"Max longitudinal force: {max(forces_lbf):.0f} lbf at {normal_force} N normal load")
        
        # Plot tire characteristics
        plt.figure(figsize=(10, 6))
        plt.plot(slip_ratios * 100, forces_lbf, 'g-', linewidth=2, marker='o')
        plt.xlabel('Slip Ratio [%]')
        plt.ylabel('Longitudinal Force [lbf]')
        plt.title('Tire Force vs Slip Ratio')
        plt.grid(True, alpha=0.3)
        plot_path = get_plot_path('tire_demo.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print_save_message(plot_path, 'plot')
        plt.show()
        
    except Exception as e:
        print(f"⚠ Tire model demo failed: {e}")


def demo_ggv_concept():
    """Demonstrate g-g-V diagram concept."""
    print("\n📊 g-g-V Diagram Demonstration")
    print("=" * 40)
    
    # Create sample g-g-V data
    velocities = np.linspace(20, 100, 30)  # ft/s
    
    # Model tire-limited acceleration (decreases with speed due to aero drag)
    max_accel_tire = 1.5 * np.ones_like(velocities)
    
    # Model power-limited acceleration (decreases with speed)
    max_accel_power = 800 / velocities  # Simplified power/speed relationship
    
    # Take minimum (limiting factor)
    max_accel = np.minimum(max_accel_tire, max_accel_power)
    
    # Model braking (approximately constant)
    max_braking = -1.2 * np.ones_like(velocities)
    
    # Model lateral acceleration (tire limited, approximately constant)
    max_lateral = 1.6 * np.ones_like(velocities)
    
    # Convert velocity to mph for display
    velocities_mph = velocities * 0.681818  # ft/s to mph
    
    print(f"Max acceleration at 30 mph: {max_accel[5]:.2f} g")
    print(f"Max lateral acceleration: {max_lateral[0]:.2f} g")
    print(f"Max braking: {max_braking[0]:.2f} g")
    
    # Create plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Velocity vs acceleration
    ax1.plot(velocities_mph, max_accel, 'b-', linewidth=2, label='Max Acceleration')
    ax1.plot(velocities_mph, max_braking, 'r-', linewidth=2, label='Max Braking')
    ax1.plot(velocities_mph, max_lateral, 'g-', linewidth=2, label='Max Lateral')
    ax1.set_xlabel('Velocity [mph]')
    ax1.set_ylabel('Acceleration [g]')
    ax1.set_title('Performance vs Velocity')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # g-g diagram (friction circle)
    theta = np.linspace(0, 2*np.pi, 100)
    radius = 1.6  # Maximum combined acceleration
    
    # Create friction ellipse
    lat_g = radius * np.cos(theta)
    long_g = radius * np.sin(theta) * 0.8  # Slightly less longitudinal
    
    ax2.plot(lat_g, long_g, 'k-', linewidth=2, label='Friction Limit')
    ax2.fill(lat_g, long_g, alpha=0.2, color='gray')
    
    # Add some sample operating points
    sample_lat = np.array([0, 0.5, 1.0, 0.8, -0.8])
    sample_long = np.array([1.2, 0.3, 0, -0.9, -0.9])
    ax2.scatter(sample_lat, sample_long, c='red', s=50, zorder=5, label='Sample Points')
    
    ax2.set_xlabel('Lateral Acceleration [g]')
    ax2.set_ylabel('Longitudinal Acceleration [g]')
    ax2.set_title('g-g Diagram (Friction Circle)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.axis('equal')
    ax2.set_xlim(-2, 2)
    ax2.set_ylim(-1.5, 1.5)
    
    plt.tight_layout()
    plot_path = get_plot_path('ggv_demo.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print_save_message(plot_path, 'plot')
    plt.show()


def demo_summary():
    """Show summary of conversion capabilities."""
    print("\n🎯 Python Conversion Summary")
    print("=" * 40)
    
    print("✅ Successfully converted components:")
    print("   • Vehicle configuration parameters")
    print("   • Powertrain model with gear selection")
    print("   • Tire model framework (Magic Formula)")
    print("   • Data loading for MATLAB files")
    print("   • Basic simulation structure")
    
    print("\n🔧 Key Python advantages:")
    print("   • Modern scientific computing stack")
    print("   • Better visualization with Matplotlib")
    print("   • Modular, object-oriented design")
    print("   • Easy integration with other tools")
    print("   • Comprehensive testing framework")
    
    print("\n📈 Performance characteristics:")
    print("   • Fast numerical computations with NumPy")
    print("   • Efficient data handling with Pandas")
    print("   • Advanced interpolation with SciPy")
    print("   • Professional plotting capabilities")
    
    print("\n🚀 Ready for:")
    print("   • Vehicle parameter studies")
    print("   • Performance optimization")
    print("   • Data analysis and visualization")
    print("   • Integration with CAD tools")
    print("   • Automated testing and validation")


def main():
    """Run complete demonstration."""
    print("🏁 Python Lap Simulation Demonstration")
    print("🔄 Converting MATLAB to Python")
    print("=" * 50)
    
    # Run demonstrations
    demo_powertrain()
    demo_tire_model()
    demo_ggv_concept()
    demo_summary()
    
    print("\n" + "=" * 50)
    print("🎉 Demonstration complete!")
    print("Check the generated PNG files for plots.")
    print("Run 'python test_python_conversion.py' for detailed testing.")


if __name__ == "__main__":
    main()
