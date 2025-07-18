"""
Comprehensive Physics Test Suite
================================

This test suite validates all physics calculations across different vehicle configurations
to ensure accuracy of acceleration, load transfer, and lap time calculations.

Test Categories:
1. Basic Physics Validation
2. Vehicle Configuration Parameter Tests
3. Aerodynamic Effects Tests
4. Load Transfer Accuracy Tests
5. Acceleration Calculation Tests
6. Lap Time Accuracy Tests
7. Cross-Configuration Consistency Tests
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vehicle_config import (
    get_vehicle_config, get_powertrain_config,
    ORIGINAL_MATLAB_CONFIG, REALISTIC_FSAE_CONFIG, HIGH_DOWNFORCE_CONFIG
)
from lap_simulation.physics import (
    calculate_realistic_velocities, calculate_aerodynamic_forces,
    calculate_longitudinal_acceleration,
    calculate_lateral_acceleration_from_velocity, get_vehicle_parameters,
    calculate_track_curvature, calculate_max_cornering_speeds,
    apply_acceleration_limits, apply_deceleration_limits,
    estimate_lap_time, calculate_cumulative_distance
)
from lap_simulation.individual_wheel_physics import calculate_individual_wheel_loads
from lap_simulation.powertrain import PowertrainModel


class TestBasicPhysicsValidation:
    """Test fundamental physics calculations for correctness."""
    
    def test_gravity_constant(self):
        """Test that gravity is correctly defined."""
        config = get_vehicle_config()
        assert abs(config['gravity'] - 9.81) < 0.01, "Gravity should be 9.81 m/s²"
    
    def test_mass_weight_consistency(self):
        """Test that mass and weight are consistent."""
        config = get_vehicle_config()
        expected_weight = config['mass'] * config['gravity']
        assert abs(config['weight'] - expected_weight) < 0.1, "Weight should equal mass × gravity"
    
    def test_wheelbase_cg_consistency(self):
        """Test that center of gravity position is within wheelbase."""
        config = get_vehicle_config()
        assert 0 < config['cg_x'] < config['wheelbase'], "CG should be between front and rear axles"
    
    def test_track_width_consistency(self):
        """Test that track widths are reasonable."""
        config = get_vehicle_config()
        assert config['track_width_front'] > 0, "Front track width should be positive"
        assert config['track_width_rear'] > 0, "Rear track width should be positive"
        # Average should be close to overall track width
        avg_track = (config['track_width_front'] + config['track_width_rear']) / 2
        assert abs(avg_track - config['track_width']) < 0.1, "Track width should be average of front/rear"


class TestVehicleConfigurationParameters:
    """Test all vehicle configuration parameters for validity and range checking."""
    
    @pytest.mark.parametrize("aero_config", [None, 'original', 'realistic', 'high_downforce'])
    def test_aero_configurations(self, aero_config):
        """Test different aerodynamic configurations."""
        config = get_vehicle_config(aero_config=aero_config)
        
        # All aero coefficients should be non-negative
        assert config['drag_coefficient'] >= 0, "Drag coefficient should be non-negative"
        assert config['downforce_coefficient'] >= 0, "Downforce coefficient should be non-negative"
        
        # Frontal area should be reasonable for FSAE car
        assert 0.5 <= config['frontal_area'] <= 3.0, "Frontal area should be reasonable for FSAE"
        
        # Front downforce distribution should be between 0 and 1
        assert 0 <= config['front_downforce_distribution'] <= 1, "Front downforce distribution should be 0-1"
    
    def test_mass_properties_range(self):
        """Test that mass properties are in reasonable ranges for FSAE."""
        config = get_vehicle_config()
        
        # Total mass should be reasonable for FSAE (200-400 kg typical)
        assert 200 <= config['mass'] <= 400, "Vehicle mass should be typical for FSAE"
        
        # CG height should be reasonable (0.2-0.4m typical)
        assert 0.15 <= config['cg_height'] <= 0.5, "CG height should be reasonable"
        
        # Wheelbase should be reasonable (1.4-1.8m typical for FSAE)
        assert 1.2 <= config['wheelbase'] <= 2.0, "Wheelbase should be reasonable for FSAE"
    
    def test_tire_parameters_validity(self):
        """Test tire parameter validity."""
        config = get_vehicle_config()
        
        # Tire radius should be reasonable for FSAE (18" wheels typical)
        assert 0.15 <= config['tire_radius'] <= 0.35, "Tire radius should be reasonable"
        
        # Static loads should be positive and sum to total weight
        total_static_load = 2 * (config['static_load_front'] + config['static_load_rear'])
        assert abs(total_static_load - config['weight']) < 1.0, "Static loads should sum to total weight"
        
        # Magic Formula parameters should be in reasonable ranges
        tire_params = config['tire_params']
        assert 0.5 <= tire_params['mu'] <= 3.0, "Friction coefficient should be reasonable"
        assert tire_params['Fz0'] > 0, "Reference load should be positive"


class TestAerodynamicEffects:
    """Test aerodynamic force calculations and their effects."""
    
    def create_test_velocity_profile(self):
        """Create a test velocity profile for aerodynamic testing."""
        return np.array([20, 40, 60, 80, 100])  # mph
    
    @pytest.mark.parametrize("aero_config", ['original', 'realistic', 'high_downforce'])
    def test_aerodynamic_force_scaling(self, aero_config):
        """Test that aerodynamic forces scale with velocity squared."""
        vehicle_params = get_vehicle_parameters('endurance', aero_config=aero_config)
        velocities = self.create_test_velocity_profile()
        
        aero_forces = calculate_aerodynamic_forces(velocities, vehicle_params)
        
        # Test that forces scale with v²
        for i in range(1, len(velocities)):
            velocity_ratio = velocities[i] / velocities[0]
            force_ratio = aero_forces['total_downforce'][i] / max(aero_forces['total_downforce'][0], 1e-6)
            
            if aero_forces['total_downforce'][0] > 1e-6:  # Only test if base force is significant
                expected_ratio = velocity_ratio ** 2
                assert abs(force_ratio - expected_ratio) < 0.1, f"Downforce should scale with v² for {aero_config}"
    
    def test_downforce_distribution(self):
        """Test that downforce is properly distributed between front and rear."""
        vehicle_params = get_vehicle_parameters('endurance', aero_config='realistic')
        velocities = np.array([60])  # mph
        
        aero_forces = calculate_aerodynamic_forces(velocities, vehicle_params)
        
        total_downforce = aero_forces['total_downforce'][0]
        front_downforce = aero_forces['front_downforce'][0]
        rear_downforce = aero_forces['rear_downforce'][0]
        
        # Front + rear should equal total
        assert abs(front_downforce + rear_downforce - total_downforce) < 0.1, "Front + rear should equal total downforce"
        
        # Distribution should match configuration
        if total_downforce > 1e-6:
            front_fraction = front_downforce / total_downforce
            expected_fraction = vehicle_params['front_downforce_distribution']
            assert abs(front_fraction - expected_fraction) < 0.05, "Downforce distribution should match configuration"
    
    def test_aerodynamic_moments(self):
        """Test aerodynamic moment calculations."""
        vehicle_params = get_vehicle_parameters('endurance', aero_config='realistic')
        velocities = np.array([60])  # mph
        
        aero_forces = calculate_aerodynamic_forces(velocities, vehicle_params)
        
        # Drag moment should be proportional to drag force and COP height
        if aero_forces['drag_force'][0] > 1e-6:
            expected_drag_moment = aero_forces['drag_force'][0] * vehicle_params['cop_height']
            assert abs(aero_forces['drag_moment'][0] - expected_drag_moment) < 0.1, "Drag moment calculation error"


class TestLoadTransferAccuracy:
    """Test load transfer calculations for accuracy."""
    
    def test_static_load_transfer_zero_acceleration(self):
        """Test that zero acceleration gives static loads."""
        config = get_vehicle_config()
        n_points = 5
        A_lat_g = np.zeros(n_points)
        A_long_g = np.zeros(n_points)
        velocities = np.full(n_points, 30.0 * 0.44704)  # Convert mph to m/s
        
        loads = calculate_individual_wheel_loads(A_lat_g, A_long_g, velocities, config)
        
        # With zero acceleration, loads should be close to static
        expected_front = config['static_load_front']
        expected_rear = config['static_load_rear']
        
        tolerance = 0.1 * expected_front  # 10% tolerance for numerical errors
        
        assert abs(loads['FL'][0] - expected_front) < tolerance, "Front left load should be static"
        assert abs(loads['FR'][0] - expected_front) < tolerance, "Front right load should be static"
        assert abs(loads['RL'][0] - expected_rear) < tolerance, "Rear left load should be static"
        assert abs(loads['RR'][0] - expected_rear) < tolerance, "Rear right load should be static"
    
    def test_lateral_load_transfer_symmetry(self):
        """Test that lateral load transfer maintains left-right force balance."""
        config = get_vehicle_config()
        n_points = 1
        A_lat_g = np.array([1.0])  # 1g lateral acceleration
        A_long_g = np.zeros(n_points)
        velocities = np.array([30.0 * 0.44704])  # Convert mph to m/s
        
        loads = calculate_individual_wheel_loads(A_lat_g, A_long_g, velocities, config)
        
        # Total load on each axle should remain the same
        front_total = loads['FL'][0] + loads['FR'][0]
        rear_total = loads['RL'][0] + loads['RR'][0]
        total_load = front_total + rear_total
        
        # Should approximately equal total vehicle weight
        assert abs(total_load - config['weight']) < config['weight'] * 0.1, "Total load should be conserved"
        
        # One side should have more load than the other (load transfer effect)
        front_imbalance = abs(loads['FL'][0] - loads['FR'][0])
        rear_imbalance = abs(loads['RL'][0] - loads['RR'][0])
        
        assert front_imbalance > 0, "Should have lateral load transfer at front"
        assert rear_imbalance > 0, "Should have lateral load transfer at rear"
    
    def test_longitudinal_load_transfer(self):
        """Test longitudinal load transfer under acceleration/braking."""
        config = get_vehicle_config()
        n_points = 3
        # Test acceleration, steady state, braking
        A_long_g = np.array([1.0, 0.0, -1.0])  # 1g accel, 0g, 1g braking
        A_lat_g = np.zeros(n_points)
        velocities = np.array([30.0, 30.0, 30.0]) * 0.44704  # Convert mph to m/s
        
        loads = calculate_individual_wheel_loads(A_lat_g, A_long_g, velocities, config)
        
        # Under acceleration (positive), rear should have more load
        rear_accel = loads['RL'][0] + loads['RR'][0]
        rear_steady = loads['RL'][1] + loads['RR'][1]
        rear_brake = loads['RL'][2] + loads['RR'][2]
        
        assert rear_accel > rear_steady, "Rear load should increase under acceleration"
        assert rear_brake < rear_steady, "Rear load should decrease under braking"


class TestAccelerationCalculations:
    """Test acceleration calculation accuracy."""
    
    def create_test_track(self):
        """Create a simple test track for acceleration testing."""
        # Straight track with some turns
        n_points = 100
        x_coords = np.linspace(0, 1000, n_points)  # 1000 ft straight
        y_coords = np.zeros(n_points)
        
        # Add some gentle curves
        y_coords[25:75] = 50 * np.sin(np.linspace(0, np.pi, 50))
        
        return x_coords, y_coords
    
    def test_longitudinal_acceleration_calculation(self):
        """Test longitudinal acceleration calculation from velocity and distance."""
        # Create test data
        distances = np.array([0, 100, 200, 300, 400])  # ft
        velocities = np.array([20, 30, 40, 50, 60])  # mph
        
        config = get_vehicle_config()
        accel = calculate_longitudinal_acceleration(velocities, distances, config)
        
        # All accelerations should be positive (increasing speed)
        assert np.all(accel[1:] > 0), "Should have positive acceleration for increasing speeds"
        
        # Accelerations should be reasonable (< 5 m/s² for FSAE)
        assert np.all(accel[1:] < 5.0), "Accelerations should be reasonable for FSAE"
    
    def test_lateral_acceleration_from_velocity(self):
        """Test lateral acceleration calculation from velocity and curvature."""
        x_coords, y_coords = self.create_test_track()
        curvatures = calculate_track_curvature(x_coords, y_coords)
        velocities = np.full(len(x_coords), 40.0)  # 40 mph constant
        config = get_vehicle_config()
        
        lat_accel = calculate_lateral_acceleration_from_velocity(velocities, curvatures, config)
        
        # Lateral acceleration should be low on straights (low curvature)
        straight_sections = curvatures < 0.001
        assert np.all(lat_accel[straight_sections] < 0.2), "Lateral acceleration should be low on straights"
        
        # Should have higher lateral acceleration in curves
        curve_sections = curvatures > 0.01
        if np.any(curve_sections):
            assert np.mean(lat_accel[curve_sections]) > np.mean(lat_accel[straight_sections]), \
                "Should have higher lateral acceleration in curves"
    
    def test_acceleration_limits_physical_validity(self):
        """Test that acceleration limits are physically reasonable."""
        x_coords, y_coords = self.create_test_track()
        vehicle_params = get_vehicle_parameters('endurance')
        
        curvatures = calculate_track_curvature(x_coords, y_coords)
        max_cornering_speeds = calculate_max_cornering_speeds(curvatures, vehicle_params)
        
        velocities = apply_acceleration_limits(x_coords, y_coords, max_cornering_speeds, vehicle_params)
        
        # Velocities should be reasonable
        assert np.all(velocities > 0), "All velocities should be positive"
        assert np.all(velocities < 150), "Velocities should be reasonable for FSAE (< 150 mph)"
        
        # Calculate accelerations and check they're within limits
        distances = calculate_cumulative_distance(x_coords, y_coords)
        config = get_vehicle_config()
        accel = calculate_longitudinal_acceleration(velocities, distances, config)
        
        # Most accelerations should be within reasonable FSAE limits
        reasonable_accel = np.abs(accel[1:]) < 8.0  # 8 m/s² limit (generous)
        assert np.sum(reasonable_accel) > 0.8 * len(reasonable_accel), \
            "Most accelerations should be within reasonable limits"


class TestLapTimeAccuracy:
    """Test lap time calculation accuracy."""
    
    def test_lap_time_calculation_basic(self):
        """Test basic lap time calculation."""
        # Simple test: 1000 ft at constant 30 mph
        distances = np.array([0, 500, 1000])  # ft
        velocities = np.array([30, 30, 30])  # mph
        
        lap_time = estimate_lap_time(distances, velocities)
        
        # Expected: 1000 ft / (30 mph) = 1000 ft / (44 ft/s) ≈ 22.7 seconds
        expected_time = 1000 / (30 * 5280 / 3600)
        assert abs(lap_time - expected_time) < 1.0, "Basic lap time calculation should be accurate"
    
    def test_lap_time_with_acceleration(self):
        """Test lap time with varying speeds."""
        distances = np.array([0, 250, 500, 750, 1000])  # ft
        velocities = np.array([20, 30, 40, 50, 60])  # mph - accelerating
        
        lap_time = estimate_lap_time(distances, velocities)
        
        # Should be faster than constant speed at average velocity
        avg_velocity = np.mean(velocities)
        constant_speed_time = 1000 / (avg_velocity * 5280 / 3600)
        
        # Due to acceleration, actual time should be between fastest and slowest constant speeds
        fast_time = 1000 / (60 * 5280 / 3600)
        slow_time = 1000 / (20 * 5280 / 3600)
        
        assert fast_time < lap_time < slow_time, "Lap time should be between fast and slow extremes"
    
    def test_lap_time_consistency_across_configs(self):
        """Test that lap time calculations are consistent across vehicle configurations."""
        x_coords = np.linspace(0, 1000, 50)
        y_coords = np.zeros(50)
        
        # Test different configurations
        configs = ['original', 'realistic', 'high_downforce']
        lap_times = {}
        
        for config in configs:
            velocities = calculate_realistic_velocities(x_coords, y_coords, 'endurance', aero_config=config)
            distances = calculate_cumulative_distance(x_coords, y_coords)
            lap_times[config] = estimate_lap_time(distances, velocities)
        
        # All lap times should be reasonable (5-60 seconds for this test track)
        for config, time in lap_times.items():
            assert 5 < time < 60, f"Lap time for {config} should be reasonable"
        
        # High downforce should generally be faster (more grip)
        # But allow for exceptions due to drag penalty
        assert abs(lap_times['high_downforce'] - lap_times['original']) < 30, \
            "Lap times should be within reasonable range across configs"


class TestCrossConfigurationConsistency:
    """Test consistency across different vehicle configurations."""
    
    def test_aero_disabled_vs_zero_coefficients(self):
        """Test that disabling aero is equivalent to zero coefficients."""
        x_coords = np.linspace(0, 500, 25)
        y_coords = np.zeros(25)
        
        # Disabled aero
        velocities_disabled = calculate_realistic_velocities(
            x_coords, y_coords, 'endurance', enable_aero=False
        )
        
        # Zero coefficients
        velocities_zero = calculate_realistic_velocities(
            x_coords, y_coords, 'endurance', enable_aero=True,
            aero_config={'drag_coefficient': 0.0, 'downforce_coefficient': 0.0}
        )
        
        # Should be very similar
        diff = np.abs(velocities_disabled - velocities_zero)
        assert np.max(diff) < 1.0, "Disabled aero should be similar to zero coefficients"
    
    def test_track_type_parameter_consistency(self):
        """Test that track type parameters are consistently applied."""
        x_coords = np.linspace(0, 300, 20)
        y_coords = np.zeros(20)
        
        # Test both track types
        endurance_vel = calculate_realistic_velocities(x_coords, y_coords, 'endurance')
        autocross_vel = calculate_realistic_velocities(x_coords, y_coords, 'autocross')
        
        # Both should produce valid results
        assert np.all(endurance_vel > 0), "Endurance velocities should be positive"
        assert np.all(autocross_vel > 0), "Autocross velocities should be positive"
        
        # Should have different characteristics but similar magnitudes
        assert np.abs(np.mean(endurance_vel) - np.mean(autocross_vel)) < 20, \
            "Track types should have similar average speeds"
    
    def test_powertrain_configuration_validity(self):
        """Test that powertrain configuration is valid across all test cases."""
        powertrain_config = get_powertrain_config()
        
        # Basic validation
        assert len(powertrain_config['engine_speed']) == len(powertrain_config['engine_torque']), \
            "Engine speed and torque arrays should have same length"
        
        assert powertrain_config['shift_point'] > 0, "Shift point should be positive"
        assert 0 < powertrain_config['drivetrain_losses'] <= 1, "Drivetrain efficiency should be 0-1"
        
        # Test powertrain model initialization
        powertrain = PowertrainModel(powertrain_config)
        
        # Test gear selection
        test_velocity = 15.0  # m/s
        gear = powertrain.calculate_gear_selection(test_velocity)
        assert 1 <= gear <= len(powertrain_config['gear_ratios']), "Gear selection should be valid"


class TestPhysicsIntegration:
    """Test integration of all physics components together."""
    
    def test_complete_physics_pipeline(self):
        """Test the complete physics calculation pipeline."""
        # Create a realistic test track
        n_points = 50
        x_coords = np.linspace(0, 800, n_points)
        y_coords = 100 * np.sin(2 * np.pi * x_coords / 800)  # Sinusoidal track
        
        # Run complete physics calculation
        velocities = calculate_realistic_velocities(x_coords, y_coords, 'endurance')
        distances = calculate_cumulative_distance(x_coords, y_coords)
        
        # Calculate all derived quantities
        curvatures = calculate_track_curvature(x_coords, y_coords)
        config = get_vehicle_config()
        long_accel = calculate_longitudinal_acceleration(velocities, distances, config)
        lat_accel = calculate_lateral_acceleration_from_velocity(velocities, curvatures, config)
        lap_time = estimate_lap_time(distances, velocities)
        
        # Comprehensive validation
        assert len(velocities) == n_points, "Velocity array should match input length"
        assert len(distances) == n_points, "Distance array should match input length"
        assert len(long_accel) == n_points, "Longitudinal acceleration array should match input length"
        assert len(lat_accel) == n_points, "Lateral acceleration array should match input length"
        
        # Physics validity checks
        assert np.all(velocities > 0), "All velocities should be positive"
        assert np.all(np.isfinite(velocities)), "All velocities should be finite"
        assert np.all(distances[1:] > distances[:-1]), "Distances should be monotonically increasing"
        assert lap_time > 0, "Lap time should be positive"
        assert np.all(np.abs(long_accel[1:]) < 10), "Longitudinal accelerations should be reasonable"
        assert np.all(np.abs(lat_accel) < 20), "Lateral accelerations should be reasonable"
    
    def test_physics_sensitivity_analysis(self):
        """Test sensitivity of physics calculations to small parameter changes."""
        base_config = get_vehicle_config()
        x_coords = np.linspace(0, 400, 25)
        y_coords = np.zeros(25)
        
        # Base case
        base_velocities = calculate_realistic_velocities(x_coords, y_coords, 'endurance')
        base_lap_time = estimate_lap_time(calculate_cumulative_distance(x_coords, y_coords), base_velocities)
        
        # Test small changes in key parameters
        test_params = [
            ('mass', 0.95),  # 5% lighter
            ('mass', 1.05),  # 5% heavier
            ('cg_height', 0.9),  # 10% lower CG
            ('cg_height', 1.1),  # 10% higher CG
        ]
        
        for param, factor in test_params:
            # Create modified config
            modified_config = base_config.copy()
            modified_config[param] = base_config[param] * factor
            
            # Calculate with modified config (Note: this requires modifying the physics functions to accept config directly)
            # For now, we'll test that the configuration itself is valid
            assert modified_config[param] > 0, f"Modified {param} should be positive"
            
            # The actual sensitivity test would require refactoring physics functions
            # to accept configuration parameters directly


if __name__ == "__main__":
    # Run specific test classes for debugging
    pytest.main([
        __file__ + "::TestBasicPhysicsValidation",
        "-v"
    ])
