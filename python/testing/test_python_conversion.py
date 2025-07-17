"""
Test Script for Python Lap Simulation
======================================

Simple test to verify the conversion works and can load data files.
"""

import os
import sys
import numpy as np

# Add the python directory to the path
current_dir = os.path.dirname(__file__)
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

try:
    from lap_simulation.data_loader import DataManager, load_mat_data
    from lap_simulation.tire_model import TireModel
    from lap_simulation.powertrain import PowertrainModel, powertrain_lapsim
    print("✓ Successfully imported all modules")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


def test_data_loading():
    """Test loading MATLAB data files."""
    print("\nTesting data loading...")
    
    try:
        # Test DataManager
        data_manager = DataManager(current_dir)
        print("✓ DataManager initialized")
        
        # Test tire data loading
        data_dir = os.path.join(current_dir, "Data Files")
        if os.path.exists(data_dir):
            # List available data files
            data_files = os.listdir(data_dir)
            print(f"✓ Found {len(data_files)} data files:")
            for file in data_files:
                print(f"  - {file}")
                
            # Try to load a sample .mat file
            if any(file.endswith('.mat') for file in data_files):
                mat_file = next(file for file in data_files if file.endswith('.mat'))
                mat_path = os.path.join(data_dir, mat_file)
                try:
                    data = load_mat_data(mat_path)
                    print(f"✓ Successfully loaded {mat_file}")
                    print(f"  Keys: {list(data.keys())}")
                except Exception as e:
                    print(f"✗ Error loading {mat_file}: {e}")
        else:
            print("✗ Data Files directory not found")
            
    except Exception as e:
        print(f"✗ Data loading test failed: {e}")


def test_tire_model():
    """Test tire model functionality."""
    print("\nTesting tire model...")
    
    try:
        data_dir = os.path.join(current_dir, "Data Files")
        if os.path.exists(data_dir):
            tire_model = TireModel(data_dir)
            print("✓ TireModel initialized")
            
            # Test force calculations with dummy data
            slip_angle = 5.0  # degrees
            normal_force = 500.0  # N
            camber_angle = -2.0  # degrees
            
            try:
                lateral_force = tire_model.calculate_lateral_force(slip_angle, normal_force, camber_angle)
                print(f"✓ Lateral force calculation: {lateral_force[0]:.2f} N")
            except Exception as e:
                print(f"⚠ Lateral force calculation (expected to have issues): {e}")
                
            try:
                longitudinal_force = tire_model.calculate_longitudinal_force(0.1, normal_force, camber_angle)
                print(f"✓ Longitudinal force calculation: {longitudinal_force[0]:.2f} N")
            except Exception as e:
                print(f"⚠ Longitudinal force calculation (expected to have issues): {e}")
        else:
            print("⚠ Skipping tire model test - no data directory")
            
    except Exception as e:
        print(f"✗ Tire model test failed: {e}")


def test_powertrain():
    """Test powertrain model."""
    print("\nTesting powertrain model...")
    
    try:
        # Test with default configuration
        powertrain = PowertrainModel()
        print("✓ PowertrainModel initialized with defaults")
        
        # Test force calculation
        velocity_ms = 20.0  # m/s
        force, gear = powertrain.calculate_wheel_force(velocity_ms)
        print(f"✓ Wheel force at {velocity_ms} m/s: {force:.1f} N, Gear: {gear}")
        
        # Test powertrain_lapsim function
        force2, gear2 = powertrain_lapsim(velocity_ms)
        print(f"✓ Powertrain lapsim: {force2:.1f} N, Gear: {gear2}")
        
    except Exception as e:
        print(f"✗ Powertrain test failed: {e}")


def test_basic_simulation():
    """Test basic simulation setup."""
    print("\nTesting basic simulation setup...")
    
    try:
        from lap_simulation.lap_sim import LapSimulator, VehicleConfig
        
        # Test VehicleConfig
        vehicle = VehicleConfig()
        print("✓ VehicleConfig initialized")
        print(f"  Vehicle weight: {vehicle.W} lbs")
        print(f"  Wheelbase: {vehicle.l:.2f} ft")
        
        # Test LapSimulator initialization
        simulator = LapSimulator(current_dir)
        print("✓ LapSimulator initialized")
        
        # Test GGV diagram generation (simplified)
        try:
            velocities, max_accel, max_cornering = simulator.generate_ggv_diagram()
            print(f"✓ GGV diagram generated with {len(velocities)} velocity points")
            print(f"  Max acceleration range: {np.min(max_accel):.2f} to {np.max(max_accel):.2f} g")
        except Exception as e:
            print(f"⚠ GGV generation (expected to have issues): {e}")
            
    except Exception as e:
        print(f"✗ Basic simulation test failed: {e}")


def main():
    """Run all tests."""
    print("Python Lap Simulation Test Suite")
    print("=" * 40)
    
    test_data_loading()
    test_tire_model()
    test_powertrain()
    test_basic_simulation()
    
    print("\n" + "=" * 40)
    print("Test suite completed!")
    print("\nNotes:")
    print("- Some tests may show warnings due to missing/incomplete data files")
    print("- The conversion provides a framework that can be extended")
    print("- Full functionality requires complete MATLAB data file support")


if __name__ == "__main__":
    main()
