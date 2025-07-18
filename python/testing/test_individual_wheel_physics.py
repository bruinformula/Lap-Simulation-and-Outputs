"""
Comprehensive Test Suite for Individual Wheel Physics
=====================================================

Tests all functions in the individual wheel physics module to ensure accuracy
and reliability of the enhanced vehicle dynamics calculations.
"""

import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lap_simulation.individual_wheel_physics import (
    calculate_individual_wheel_loads,
    calculate_suspension_effects,
    calculate_slip_angles_and_yaw_moment
)
from vehicle_config import get_vehicle_config

import numpy as np
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lap_simulation.individual_wheel_physics import (
    calculate_individual_wheel_loads,
    calculate_slip_angles_and_yaw_moment,
    calculate_suspension_effects,
    calculate_individual_wheel_forces_simple,
    validate_wheel_loads
)
from vehicle_config import get_vehicle_config


class TestPhase1Physics:
    """Test Phase 1 physics implementations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.vehicle_config = get_vehicle_config()
        
        # Test data based on MATLAB values
        self.n_points = 50
        self.velocities = np.linspace(10, 40, self.n_points)  # m/s
        self.lateral_accel_g = np.linspace(-1.5, 1.5, self.n_points)
        self.longitudinal_accel_g = np.linspace(-0.8, 0.8, self.n_points)
        
        # Expected values from MATLAB
        self.expected_lltd = 0.51  # 51% from MATLAB
        self.expected_weight_dist_front = 0.44754  # 44.754% from MATLAB
        
    def test_vehicle_config_matlab_values(self):
        """Test that vehicle config contains correct MATLAB values."""
        assert self.vehicle_config['LLTD'] == pytest.approx(0.51, abs=0.001)
        assert self.vehicle_config['roll_gradient_front'] == pytest.approx(1.15, abs=0.001)
        assert self.vehicle_config['roll_gradient_rear'] == pytest.approx(1.15, abs=0.001)
        assert self.vehicle_config['pitch_gradient'] == pytest.approx(0.0, abs=0.001)
        assert self.vehicle_config['kingpin_inclination_front'] == pytest.approx(7.18, abs=0.001)
        assert self.vehicle_config['kingpin_inclination_rear'] == pytest.approx(8.49, abs=0.001)
        assert self.vehicle_config['caster_angle_front'] == pytest.approx(4.0, abs=0.001)
        assert self.vehicle_config['caster_angle_rear'] == pytest.approx(4.0, abs=0.001)
        
    def test_individual_wheel_loads_weight_conservation(self):
        """Test that individual wheel loads conserve total weight."""
        wheel_loads = calculate_individual_wheel_loads(
            self.lateral_accel_g, self.longitudinal_accel_g, 
            self.velocities, self.vehicle_config
        )
        
        # Check weight conservation at each point
        for i in range(self.n_points):
            total_load = (wheel_loads['FL'][i] + wheel_loads['FR'][i] + 
                         wheel_loads['RL'][i] + wheel_loads['RR'][i])
            assert total_load == pytest.approx(self.vehicle_config['weight'], rel=0.001)
    
    def test_individual_wheel_loads_static_conditions(self):
        """Test wheel loads under static conditions (no acceleration)."""
        # Zero acceleration case
        lat_accel = np.zeros(10)
        long_accel = np.zeros(10)
        velocities = np.ones(10) * 20.0
        
        wheel_loads = calculate_individual_wheel_loads(
            lat_accel, long_accel, velocities, self.vehicle_config
        )
        
        # Under static conditions, left/right should be equal
        for i in range(10):
            assert wheel_loads['FL'][i] == pytest.approx(wheel_loads['FR'][i], rel=0.001)
            assert wheel_loads['RL'][i] == pytest.approx(wheel_loads['RR'][i], rel=0.001)
        
        # Check front/rear distribution matches MATLAB WDF
        front_total = wheel_loads['FL'][0] + wheel_loads['FR'][0]
        total_weight = self.vehicle_config['weight']
        front_percentage = front_total / total_weight
        assert front_percentage == pytest.approx(self.expected_weight_dist_front, rel=0.01)
    
    def test_individual_wheel_loads_lateral_transfer(self):
        """Test lateral load transfer distribution (LLTD)."""
        # Pure lateral acceleration case
        lat_accel = np.array([1.0])  # 1g lateral
        long_accel = np.array([0.0])
        velocities = np.array([20.0])
        
        wheel_loads = calculate_individual_wheel_loads(
            lat_accel, long_accel, velocities, self.vehicle_config
        )
        
        # Calculate actual load transfer
        left_total = wheel_loads['FL'][0] + wheel_loads['RL'][0]
        right_total = wheel_loads['FR'][0] + wheel_loads['RR'][0]
        
        # Right side should have more load (positive lateral accel = left turn)
        assert right_total > left_total
        
        # The difference should be related to LLTD
        lateral_transfer = right_total - left_total
        expected_transfer = (lat_accel[0] * self.vehicle_config['cg_height'] * 
                           self.vehicle_config['weight'] / 
                           np.mean([self.vehicle_config['track_width_front'], 
                                   self.vehicle_config['track_width_rear']]))
        
        assert lateral_transfer == pytest.approx(expected_transfer, rel=0.05)
    
    def test_individual_wheel_loads_longitudinal_transfer(self):
        """Test longitudinal load transfer."""
        # Pure longitudinal acceleration (braking)
        lat_accel = np.array([0.0])
        long_accel = np.array([-0.5])  # 0.5g braking
        velocities = np.array([20.0])
        
        wheel_loads = calculate_individual_wheel_loads(
            lat_accel, long_accel, velocities, self.vehicle_config
        )
        
        # Front should have more load during braking
        front_total = wheel_loads['FL'][0] + wheel_loads['FR'][0]
        rear_total = wheel_loads['RL'][0] + wheel_loads['RR'][0]
        
        # Calculate static distribution for comparison
        static_front = self.vehicle_config['weight'] * self.expected_weight_dist_front
        assert front_total > static_front  # More than static during braking
    
    def test_slip_angles_zero_curvature(self):
        """Test slip angles with zero curvature (straight line)."""
        result = calculate_slip_angles_and_yaw_moment(
            20.0, 0.0, self.vehicle_config
        )
        
        # Straight line should have zero slip angles
        assert result['slip_angle_front'] == pytest.approx(0.0, abs=1e-6)
        assert result['slip_angle_rear'] == pytest.approx(0.0, abs=1e-6)
        assert result['yaw_rate'] == pytest.approx(0.0, abs=1e-6)
        assert result['lateral_acceleration'] == pytest.approx(0.0, abs=1e-6)
    
    def test_slip_angles_constant_radius(self):
        """Test slip angles for constant radius turn."""
        velocity = 20.0  # m/s
        radius = 50.0    # m
        curvature = 1.0 / radius
        
        result = calculate_slip_angles_and_yaw_moment(
            velocity, curvature, self.vehicle_config
        )
        
        # Check that lateral acceleration matches kinematics
        expected_lat_accel = velocity**2 * curvature
        assert result['lateral_acceleration'] == pytest.approx(expected_lat_accel, rel=0.001)
        
        # Check that yaw rate is consistent
        expected_yaw_rate = velocity * curvature
        assert result['yaw_rate'] == pytest.approx(expected_yaw_rate, rel=0.001)
        
        # Slip angles should be reasonable for this turn
        assert abs(result['slip_angle_front']) < 0.2  # Less than ~11 degrees
        assert abs(result['slip_angle_rear']) < 0.2
    
    def test_slip_angles_ackermann_steering(self):
        """Test Ackermann steering angle calculation."""
        velocity = 15.0
        radius = 30.0
        curvature = 1.0 / radius
        
        result = calculate_slip_angles_and_yaw_moment(
            velocity, curvature, self.vehicle_config
        )
        
        # Ackermann steering angle should be wheelbase/radius
        expected_ackermann = self.vehicle_config['wheelbase'] / radius
        assert result['steering_angle'] == pytest.approx(expected_ackermann, rel=0.001)
    
    def test_suspension_effects_zero_acceleration(self):
        """Test suspension effects with no acceleration."""
        lat_accel = np.zeros(5)
        long_accel = np.zeros(5)
        
        effects = calculate_suspension_effects(
            lat_accel, long_accel, self.vehicle_config
        )
        
        # No acceleration should mean no roll or pitch
        assert np.all(effects['roll_angle_front'] == 0.0)
        assert np.all(effects['roll_angle_rear'] == 0.0)
        assert np.all(effects['pitch_angle'] == 0.0)
        assert np.all(effects['camber_change_front'] == 0.0)
        assert np.all(effects['camber_change_rear'] == 0.0)
    
    def test_suspension_effects_roll_gradients(self):
        """Test roll gradient calculations."""
        lat_accel = np.array([1.0])  # 1g lateral
        long_accel = np.array([0.0])
        
        effects = calculate_suspension_effects(
            lat_accel, long_accel, self.vehicle_config
        )
        
        # Roll angle should match MATLAB roll gradients
        expected_roll_front = 1.0 * 1.15 * np.pi / 180  # 1.15 deg/g
        expected_roll_rear = 1.0 * 1.15 * np.pi / 180   # 1.15 deg/g
        
        assert effects['roll_angle_front'][0] == pytest.approx(expected_roll_front, rel=0.001)
        assert effects['roll_angle_rear'][0] == pytest.approx(expected_roll_rear, rel=0.001)
    
    def test_suspension_effects_pitch_gradient(self):
        """Test pitch gradient calculations."""
        lat_accel = np.array([0.0])
        long_accel = np.array([1.0])  # 1g longitudinal
        
        effects = calculate_suspension_effects(
            lat_accel, long_accel, self.vehicle_config
        )
        
        # MATLAB has pitch gradient = 0, so pitch angle should be 0
        expected_pitch = 1.0 * 0.0 * np.pi / 180  # 0 deg/g from MATLAB
        assert effects['pitch_angle'][0] == pytest.approx(expected_pitch, abs=1e-6)
    
    def test_wheel_force_distribution(self):
        """Test individual wheel force calculations."""
        # Create test wheel loads
        wheel_loads = {
            'FL': np.array([800, 900, 700]),
            'FR': np.array([800, 700, 900]),
            'RL': np.array([600, 650, 550]),
            'RR': np.array([600, 550, 650])
        }
        lat_accel = np.array([0.5, 1.0, 1.5])
        
        wheel_forces = calculate_individual_wheel_forces_simple(
            wheel_loads, lat_accel, self.vehicle_config
        )
        
        # Forces should be proportional to loads
        for i in range(3):
            total_force = sum(wheel_forces[wheel][i] for wheel in wheel_forces)
            total_load = sum(wheel_loads[wheel][i] for wheel in wheel_loads)
            
            # Check that force distribution roughly matches load distribution
            for wheel in wheel_forces:
                expected_fraction = wheel_loads[wheel][i] / total_load
                actual_fraction = wheel_forces[wheel][i] / total_force
                assert actual_fraction == pytest.approx(expected_fraction, rel=0.1)
    
    def test_validation_functions(self):
        """Test validation functions."""
        wheel_loads = calculate_individual_wheel_loads(
            self.lateral_accel_g, self.longitudinal_accel_g,
            self.velocities, self.vehicle_config
        )
        
        validation = validate_wheel_loads(wheel_loads, self.vehicle_config)
        
        # Validation should pass
        assert validation['weight_balance_ok'] == True
        assert validation['max_weight_error'] < 1.0  # Less than 1N error
        assert 40 < validation['front_weight_percentage'] < 50  # Reasonable range
        assert 45 < validation['left_weight_percentage'] < 55   # Should be ~50%
    
    def test_extreme_conditions(self):
        """Test physics under extreme conditions."""
        # High lateral acceleration
        extreme_lat_accel = np.array([3.0])  # 3g lateral
        zero_long_accel = np.array([0.0])
        velocity = np.array([30.0])
        
        wheel_loads = calculate_individual_wheel_loads(
            extreme_lat_accel, zero_long_accel, velocity, self.vehicle_config
        )
        
        # Even under extreme conditions, no wheel should have negative load
        for wheel in wheel_loads:
            assert wheel_loads[wheel][0] >= 0.0
        
        # Weight should still be conserved
        total_load = sum(wheel_loads[wheel][0] for wheel in wheel_loads)
        assert total_load == pytest.approx(self.vehicle_config['weight'], rel=0.001)
    
    def test_matlab_parameter_consistency(self):
        """Test that our implementation uses consistent MATLAB parameters."""
        # Test LLTD value
        assert self.vehicle_config['LLTD'] == 0.51
        
        # Test roll gradients
        assert self.vehicle_config['roll_gradient_front'] == 1.15
        assert self.vehicle_config['roll_gradient_rear'] == 1.15
        
        # Test weight distribution calculation
        wheelbase = self.vehicle_config['wheelbase']
        cg_x = self.vehicle_config['cg_x']
        calculated_wdf = (wheelbase - cg_x) / wheelbase
        assert calculated_wdf == pytest.approx(0.44754, rel=0.001)
        
        # Test vehicle dimensions match MATLAB
        assert wheelbase == pytest.approx(1.55, rel=0.001)  # 61/12 ft
        assert self.vehicle_config['track_width_front'] == pytest.approx(1.168, rel=0.001)  # 46/12 ft
        assert self.vehicle_config['track_width_rear'] == pytest.approx(1.118, rel=0.001)   # 44/12 ft


def run_phase1_tests():
    """Run all Phase 1 tests and report results."""
    print("Individual Wheel Physics Test Suite")
    print("=" * 50)
    
    # Initialize test class
    test_class = TestPhase1Physics()
    test_class.setup_method()
    
    # List of test methods
    test_methods = [
        ('Vehicle Config MATLAB Values', test_class.test_vehicle_config_matlab_values),
        ('Weight Conservation', test_class.test_individual_wheel_loads_weight_conservation),
        ('Static Conditions', test_class.test_individual_wheel_loads_static_conditions),
        ('Lateral Load Transfer', test_class.test_individual_wheel_loads_lateral_transfer),
        ('Longitudinal Load Transfer', test_class.test_individual_wheel_loads_longitudinal_transfer),
        ('Zero Curvature Slip Angles', test_class.test_slip_angles_zero_curvature),
        ('Constant Radius Slip Angles', test_class.test_slip_angles_constant_radius),
        ('Ackermann Steering', test_class.test_slip_angles_ackermann_steering),
        ('Zero Acceleration Suspension', test_class.test_suspension_effects_zero_acceleration),
        ('Roll Gradients', test_class.test_suspension_effects_roll_gradients),
        ('Pitch Gradients', test_class.test_suspension_effects_pitch_gradient),
        ('Wheel Force Distribution', test_class.test_wheel_force_distribution),
        ('Validation Functions', test_class.test_validation_functions),
        ('Extreme Conditions', test_class.test_extreme_conditions),
        ('MATLAB Parameter Consistency', test_class.test_matlab_parameter_consistency)
    ]
    
    # Run tests and track results
    passed = 0
    failed = 0
    
    for test_name, test_method in test_methods:
        try:
            test_method()
            print(f"✓ {test_name}")
            passed += 1
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    print(f"Success Rate: {passed / (passed + failed) * 100:.1f}%")
    
    if failed == 0:
        print("All individual wheel physics tests passed! ✓")
    else:
        print(f"Phase 1 implementation needs attention ({failed} failures)")
    
    return passed, failed


if __name__ == "__main__":
    run_phase1_tests()
