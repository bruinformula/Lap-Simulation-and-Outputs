"""
Plotting Test Suite with Dummy Tracks
=====================================

This test suite validates all plotting functions using procedurally generated dummy tracks.
Tests various track configurations and plotting scenarios to ensure robust visualization.

Test Categories:
1. Dummy Track Generation
2. Basic Plotting Function Tests
3. Track Layout Plotting Tests
4. Velocity Profile Plotting Tests
5. Acceleration Plotting Tests
6. Load Transfer Plotting Tests
7. Edge Cases and Error Handling
"""

import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vehicle_config import get_vehicle_config
from lap_simulation.plotting import (
    plot_accelerations, plot_corner_loads, plot_accelerations_by_sample,
    plot_roll_angles, plot_track_only, plot_velocity_profile
)
from lap_simulation.physics import (
    calculate_cumulative_distance, calculate_track_curvature,
    calculate_realistic_velocities,
    calculate_longitudinal_acceleration, calculate_lateral_acceleration_from_velocity
)
from lap_simulation.individual_wheel_physics import calculate_individual_wheel_loads


class DummyTrackGenerator:
    """Generate various types of dummy tracks for testing plotting functions."""
    
    @staticmethod
    def create_straight_track(length=1000, n_points=100):
        """Create a simple straight track."""
        x_coords = np.linspace(0, length, n_points)
        y_coords = np.zeros(n_points)
        return x_coords, y_coords
    
    @staticmethod
    def create_oval_track(width=400, height=200, n_points=200):
        """Create an oval/elliptical track."""
        t = np.linspace(0, 2*np.pi, n_points)
        x_coords = width * np.cos(t)
        y_coords = height * np.sin(t)
        return x_coords, y_coords
    
    @staticmethod
    def create_s_curve_track(length=800, amplitude=100, frequency=2, n_points=150):
        """Create an S-curve track."""
        x_coords = np.linspace(0, length, n_points)
        y_coords = amplitude * np.sin(frequency * np.pi * x_coords / length)
        return x_coords, y_coords
    
    @staticmethod
    def create_complex_track(n_points=300):
        """Create a complex track with multiple turns and elevation changes."""
        t = np.linspace(0, 4*np.pi, n_points)
        # Complex parametric equations for varied track
        x_coords = 500 * np.cos(t) + 200 * np.cos(3*t) + 100 * np.sin(5*t)
        y_coords = 300 * np.sin(t) + 150 * np.sin(2*t) + 75 * np.cos(4*t)
        return x_coords, y_coords
    
    @staticmethod
    def create_figure_eight_track(radius=200, n_points=200):
        """Create a figure-eight track."""
        t = np.linspace(0, 2*np.pi, n_points)
        x_coords = radius * np.sin(t)
        y_coords = radius * np.sin(t) * np.cos(t)
        return x_coords, y_coords
    
    @staticmethod
    def create_autocross_style_track(n_points=250):
        """Create an autocross-style track with tight turns and chicanes."""
        # Create a track that resembles an autocross course
        segments = []
        
        # Start straight
        x_start = np.linspace(0, 100, 25)
        y_start = np.zeros(25)
        segments.append((x_start, y_start))
        
        # First turn (90 degrees)
        t1 = np.linspace(0, np.pi/2, 20)
        x_turn1 = 100 + 50 * np.sin(t1)
        y_turn1 = 50 * (1 - np.cos(t1))
        segments.append((x_turn1, y_turn1))
        
        # Slalom section
        x_slalom = np.linspace(150, 350, 50)
        y_slalom = 50 + 30 * np.sin(4 * np.pi * (x_slalom - 150) / 200)
        segments.append((x_slalom, y_slalom))
        
        # Hairpin turn
        t2 = np.linspace(0, np.pi, 30)
        x_hairpin = 350 + 40 * np.cos(t2)
        y_hairpin = 80 + 40 * np.sin(t2)
        segments.append((x_hairpin, y_hairpin))
        
        # Return straight
        x_return = np.linspace(310, 50, 40)
        y_return = np.full(40, 120)
        segments.append((x_return, y_return))
        
        # Final turns back to start
        t3 = np.linspace(np.pi/2, 2*np.pi, 35)
        x_final = 50 + 50 * np.cos(t3)
        y_final = 70 + 50 * np.sin(t3)
        segments.append((x_final[:-10], y_final[:-10]))  # Remove overlap
        
        # Combine all segments
        x_coords = np.concatenate([seg[0] for seg in segments])
        y_coords = np.concatenate([seg[1] for seg in segments])
        
        return x_coords, y_coords
    
    @staticmethod
    def create_track_data_dict(x_coords, y_coords, track_type='endurance'):
        """Convert track coordinates to track data dictionary format."""
        n_points = len(x_coords)
        
        # Create track boundaries (outside and inside)
        track_width = 20.0  # feet
        
        # Calculate track normals for boundary generation
        dx = np.gradient(x_coords)
        dy = np.gradient(y_coords)
        
        # Normalize and rotate 90 degrees for normal vectors
        lengths = np.sqrt(dx**2 + dy**2)
        lengths[lengths == 0] = 1e-6  # Avoid division by zero
        
        normal_x = -dy / lengths
        normal_y = dx / lengths
        
        # Create inside and outside boundaries
        outside_x = x_coords + normal_x * track_width/2
        outside_y = y_coords + normal_y * track_width/2
        inside_x = x_coords - normal_x * track_width/2
        inside_y = y_coords - normal_y * track_width/2
        
        # Calculate distances and velocities
        distances = calculate_cumulative_distance(x_coords, y_coords)
        velocities = calculate_realistic_velocities(x_coords, y_coords, track_type)
        
        # Create track data dictionary
        track_data = {
            'outside_track': np.column_stack([outside_x, outside_y]),
            'inside_track': np.column_stack([inside_x, inside_y]),
            'racing_line': {
                'x': x_coords,
                'y': y_coords,
                'distance': distances,
                'velocity': velocities
            },
            'track_type': track_type,
            'track_length': distances[-1]
        }
        
        return track_data


class TestDummyTrackGeneration:
    """Test the dummy track generation functions."""
    
    def test_straight_track_generation(self):
        """Test straight track generation."""
        x_coords, y_coords = DummyTrackGenerator.create_straight_track(1000, 100)
        
        assert len(x_coords) == 100, "Should have correct number of points"
        assert len(y_coords) == 100, "Should have correct number of points"
        assert x_coords[0] == 0, "Should start at x=0"
        assert x_coords[-1] == 1000, "Should end at x=1000"
        assert np.allclose(y_coords, 0), "Y coordinates should be zero for straight track"
    
    def test_oval_track_generation(self):
        """Test oval track generation."""
        x_coords, y_coords = DummyTrackGenerator.create_oval_track(400, 200, 200)
        
        assert len(x_coords) == 200, "Should have correct number of points"
        assert len(y_coords) == 200, "Should have correct number of points"
        
        # Check that track forms a closed loop (approximately)
        assert abs(x_coords[0] - x_coords[-1]) < 50, "Track should be approximately closed"
        assert abs(y_coords[0] - y_coords[-1]) < 50, "Track should be approximately closed"
        
        # Check that track stays within expected bounds
        assert np.max(x_coords) <= 400 * 1.1, "X coordinates within bounds"
        assert np.max(y_coords) <= 200 * 1.1, "Y coordinates within bounds"
    
    def test_complex_track_generation(self):
        """Test complex track generation."""
        x_coords, y_coords = DummyTrackGenerator.create_complex_track(300)
        
        assert len(x_coords) == 300, "Should have correct number of points"
        assert len(y_coords) == 300, "Should have correct number of points"
        
        # Check for variety in the track (not constant)
        assert np.std(x_coords) > 50, "Track should have variety in X direction"
        assert np.std(y_coords) > 50, "Track should have variety in Y direction"
    
    def test_autocross_track_generation(self):
        """Test autocross-style track generation."""
        x_coords, y_coords = DummyTrackGenerator.create_autocross_style_track()
        
        assert len(x_coords) > 100, "Should have reasonable number of points"
        assert len(y_coords) == len(x_coords), "X and Y should have same length"
        
        # Check that track has varied curvature (typical of autocross)
        curvatures = calculate_track_curvature(x_coords, y_coords)
        assert np.max(np.abs(curvatures)) > 0.01, "Should have significant curvature"
    
    def test_track_data_dict_creation(self):
        """Test conversion to track data dictionary format."""
        x_coords, y_coords = DummyTrackGenerator.create_straight_track(500, 50)
        track_data = DummyTrackGenerator.create_track_data_dict(x_coords, y_coords)
        
        # Check required keys
        required_keys = ['outside_track', 'inside_track', 'racing_line', 'track_type', 'track_length']
        for key in required_keys:
            assert key in track_data, f"Track data should contain {key}"
        
        # Check racing line data
        racing_line = track_data['racing_line']
        assert 'x' in racing_line, "Racing line should have x coordinates"
        assert 'y' in racing_line, "Racing line should have y coordinates"
        assert 'distance' in racing_line, "Racing line should have distances"
        assert 'velocity' in racing_line, "Racing line should have velocities"
        
        # Check that boundaries are reasonable
        assert track_data['outside_track'].shape[1] == 2, "Outside track should have 2 columns"
        assert track_data['inside_track'].shape[1] == 2, "Inside track should have 2 columns"


class TestBasicPlottingFunctions:
    """Test basic plotting function calls and error handling."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        # Create temporary directory for plot outputs
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the get_plot_path function to use temp directory
        self.original_get_plot_path = None
        
    def teardown_method(self):
        """Clean up after each test."""
        # Clean up matplotlib figures
        plt.close('all')
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_plot_accelerations_basic(self, mock_get_plot_path):
        """Test basic acceleration plotting."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'test_accel.png')
        
        # Create test data
        distance = np.linspace(0, 1000, 100)
        A_long_g = 0.5 * np.sin(distance / 100) + 0.1 * np.random.randn(100)
        A_lat_g = 0.8 * np.cos(distance / 150) + 0.1 * np.random.randn(100)
        
        # Should not raise an exception
        plot_accelerations(distance, A_long_g, A_lat_g)
        
        # Check that get_plot_path was called
        mock_get_plot_path.assert_called_once()
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_plot_corner_loads_basic(self, mock_get_plot_path):
        """Test basic corner loads plotting."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'test_loads.png')
        
        # Create test load data
        n_points = 100
        loads = {
            'FL': 300 + 50 * np.sin(np.linspace(0, 4*np.pi, n_points)),
            'FR': 320 + 40 * np.cos(np.linspace(0, 4*np.pi, n_points)),
            'RL': 280 + 60 * np.sin(np.linspace(0, 3*np.pi, n_points)),
            'RR': 290 + 45 * np.cos(np.linspace(0, 3*np.pi, n_points))
        }
        
        # Should not raise an exception
        plot_corner_loads(loads)
        
        # Check that get_plot_path was called
        mock_get_plot_path.assert_called_once()
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_plot_accelerations_by_sample(self, mock_get_plot_path):
        """Test acceleration by sample plotting."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'test_accel_sample.png')
        
        # Create test data
        n_points = 150
        A_long_g = np.random.randn(n_points) * 0.3 + 0.2
        A_lat_g = np.random.randn(n_points) * 0.5
        
        # Should not raise an exception
        plot_accelerations_by_sample(A_long_g, A_lat_g)
        
        # Check that get_plot_path was called
        mock_get_plot_path.assert_called_once()
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_plot_roll_angles(self, mock_get_plot_path):
        """Test roll angle plotting."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'test_roll.png')
        
        # Create test data
        distance = np.linspace(0, 800, 120)
        roll_angle = 5 * np.sin(distance / 100) + 2 * np.cos(distance / 200)
        
        # Should not raise an exception
        plot_roll_angles(distance, roll_angle)
        
        # Check that get_plot_path was called
        mock_get_plot_path.assert_called_once()


class TestTrackLayoutPlotting:
    """Test track layout plotting with various dummy tracks."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test."""
        plt.close('all')
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_plot_straight_track(self, mock_get_plot_path):
        """Test plotting a straight track."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'straight_track.png')
        
        x_coords, y_coords = DummyTrackGenerator.create_straight_track(1000, 100)
        track_data = DummyTrackGenerator.create_track_data_dict(x_coords, y_coords)
        
        # Should not raise an exception
        plot_track_only(track_data, track_type='endurance')
        
        mock_get_plot_path.assert_called_once()
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_plot_oval_track(self, mock_get_plot_path):
        """Test plotting an oval track."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'oval_track.png')
        
        x_coords, y_coords = DummyTrackGenerator.create_oval_track(400, 200, 200)
        track_data = DummyTrackGenerator.create_track_data_dict(x_coords, y_coords, 'endurance')
        
        # Should not raise an exception
        plot_track_only(track_data, track_type='endurance')
        
        mock_get_plot_path.assert_called_once()
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_plot_complex_track(self, mock_get_plot_path):
        """Test plotting a complex track."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'complex_track.png')
        
        x_coords, y_coords = DummyTrackGenerator.create_complex_track(300)
        track_data = DummyTrackGenerator.create_track_data_dict(x_coords, y_coords, 'autocross')
        
        # Should not raise an exception
        plot_track_only(track_data, track_type='autocross')
        
        mock_get_plot_path.assert_called_once()
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_plot_autocross_track(self, mock_get_plot_path):
        """Test plotting an autocross-style track."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'autocross_track.png')
        
        x_coords, y_coords = DummyTrackGenerator.create_autocross_style_track()
        track_data = DummyTrackGenerator.create_track_data_dict(x_coords, y_coords, 'autocross')
        
        # Should not raise an exception
        plot_track_only(track_data, track_type='autocross', save_name='test_autocross.png')
        
        mock_get_plot_path.assert_called_once()
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_plot_figure_eight_track(self, mock_get_plot_path):
        """Test plotting a figure-eight track."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'figure_eight.png')
        
        x_coords, y_coords = DummyTrackGenerator.create_figure_eight_track(200, 200)
        track_data = DummyTrackGenerator.create_track_data_dict(x_coords, y_coords)
        
        # Should not raise an exception
        plot_track_only(track_data, track_type='endurance')
        
        mock_get_plot_path.assert_called_once()


class TestVelocityProfilePlotting:
    """Test velocity profile plotting with various scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test."""
        plt.close('all')
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_velocity_profile_straight_track(self, mock_get_plot_path):
        """Test velocity profile for straight track."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'velocity_straight.png')
        
        x_coords, y_coords = DummyTrackGenerator.create_straight_track(1200, 120)
        track_data = DummyTrackGenerator.create_track_data_dict(x_coords, y_coords)
        
        # Should not raise an exception
        plot_velocity_profile(track_data, track_type='endurance')
        
        mock_get_plot_path.assert_called_once()
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_velocity_profile_s_curve(self, mock_get_plot_path):
        """Test velocity profile for S-curve track."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'velocity_scurve.png')
        
        x_coords, y_coords = DummyTrackGenerator.create_s_curve_track(800, 100, 2, 150)
        track_data = DummyTrackGenerator.create_track_data_dict(x_coords, y_coords, 'autocross')
        
        # Should not raise an exception
        plot_velocity_profile(track_data, track_type='autocross')
        
        mock_get_plot_path.assert_called_once()
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_velocity_profile_with_custom_name(self, mock_get_plot_path):
        """Test velocity profile with custom save name."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'custom_velocity.png')
        
        x_coords, y_coords = DummyTrackGenerator.create_oval_track(300, 150, 180)
        track_data = DummyTrackGenerator.create_track_data_dict(x_coords, y_coords)
        
        # Should not raise an exception
        plot_velocity_profile(track_data, track_type='endurance', save_name='custom_velocity.png')
        
        mock_get_plot_path.assert_called_once()


class TestCompletePhysicsPlotting:
    """Test plotting with complete physics calculations."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = get_vehicle_config()
    
    def teardown_method(self):
        """Clean up after each test."""
        plt.close('all')
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_complete_physics_plotting_pipeline(self, mock_get_plot_path):
        """Test complete physics calculation and plotting pipeline."""
        # Use different filenames for each plot
        def side_effect(filename):
            return os.path.join(self.temp_dir, filename)
        mock_get_plot_path.side_effect = side_effect
        
        # Create test track
        x_coords, y_coords = DummyTrackGenerator.create_autocross_style_track()
        
        # Calculate physics
        distances = calculate_cumulative_distance(x_coords, y_coords)
        velocities = calculate_realistic_velocities(x_coords, y_coords, 'autocross')
        curvatures = calculate_track_curvature(x_coords, y_coords)
        
        # Calculate accelerations
        A_long_g = calculate_longitudinal_acceleration(velocities, distances, self.config)
        A_lat_g = calculate_lateral_acceleration_from_velocity(velocities, curvatures, self.config)
        
        # Calculate load transfer using individual wheel physics
        # Convert velocities from mph to m/s for the new function
        velocities_ms = velocities * 0.44704
        loads = calculate_individual_wheel_loads(A_lat_g, A_long_g, velocities_ms, self.config)
        
        # Calculate roll angles (simplified)
        roll_angle = A_lat_g * 2.0  # Simplified roll calculation
        
        # Test all plotting functions
        plot_accelerations(distances, A_long_g, A_lat_g)
        plot_accelerations_by_sample(A_long_g, A_lat_g)
        plot_corner_loads(loads)
        plot_roll_angles(distances, roll_angle)
        
        # Verify all functions were called
        assert mock_get_plot_path.call_count == 4, "Should have called get_plot_path 4 times"
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_edge_case_minimal_data(self, mock_get_plot_path):
        """Test plotting with minimal data points."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'minimal_data.png')
        
        # Minimal test data (just 3 points)
        distance = np.array([0, 100, 200])
        A_long_g = np.array([0.1, 0.2, 0.1])
        A_lat_g = np.array([0.0, 0.5, 0.0])
        
        # Should handle minimal data gracefully
        plot_accelerations(distance, A_long_g, A_lat_g)
        
        mock_get_plot_path.assert_called_once()
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_edge_case_large_dataset(self, mock_get_plot_path):
        """Test plotting with large dataset."""
        mock_get_plot_path.return_value = os.path.join(self.temp_dir, 'large_data.png')
        
        # Large test data (10000 points)
        n_large = 10000
        distance = np.linspace(0, 5000, n_large)
        A_long_g = np.random.randn(n_large) * 0.2 + 0.1
        A_lat_g = np.random.randn(n_large) * 0.3
        
        # Should handle large datasets
        plot_accelerations(distance, A_long_g, A_lat_g)
        
        mock_get_plot_path.assert_called_once()


class TestPlottingErrorHandling:
    """Test error handling and edge cases in plotting functions."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test."""
        plt.close('all')
    
    def test_mismatched_array_lengths(self):
        """Test handling of mismatched array lengths."""
        distance = np.array([0, 100, 200])
        A_long_g = np.array([0.1, 0.2])  # Different length
        A_lat_g = np.array([0.0, 0.5, 0.0])
        
        # Should raise an error or handle gracefully
        with pytest.raises((ValueError, IndexError)):
            with patch('lap_simulation.plotting.get_plot_path') as mock_path:
                mock_path.return_value = os.path.join(self.temp_dir, 'error_test.png')
                plot_accelerations(distance, A_long_g, A_lat_g)
    
    def test_empty_arrays(self):
        """Test handling of empty arrays."""
        empty_array = np.array([])
        
        # Should handle empty arrays gracefully (matplotlib handles empty arrays without error)
        with patch('lap_simulation.plotting.get_plot_path') as mock_path:
            mock_path.return_value = os.path.join(self.temp_dir, 'empty_test.png')
            # This should not raise an exception - matplotlib handles empty arrays
            plot_accelerations(empty_array, empty_array, empty_array)
    
    def test_nan_values_in_data(self):
        """Test handling of NaN values in data."""
        distance = np.array([0, 100, 200, 300])
        A_long_g = np.array([0.1, np.nan, 0.2, 0.1])
        A_lat_g = np.array([0.0, 0.5, np.nan, 0.0])
        
        # Should handle NaN values without crashing
        with patch('lap_simulation.plotting.get_plot_path') as mock_path:
            mock_path.return_value = os.path.join(self.temp_dir, 'nan_test.png')
            # This should not raise an exception
            plot_accelerations(distance, A_long_g, A_lat_g)
    
    def test_infinite_values_in_data(self):
        """Test handling of infinite values in data."""
        distance = np.array([0, 100, 200, 300])
        A_long_g = np.array([0.1, np.inf, 0.2, 0.1])
        A_lat_g = np.array([0.0, 0.5, -np.inf, 0.0])
        
        # Should handle infinite values without crashing
        with patch('lap_simulation.plotting.get_plot_path') as mock_path:
            mock_path.return_value = os.path.join(self.temp_dir, 'inf_test.png')
            # This should not raise an exception
            plot_accelerations(distance, A_long_g, A_lat_g)


class TestPlottingIntegration:
    """Test integration of plotting with complete lap simulation workflow."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test."""
        plt.close('all')
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_multiple_track_comparison_plotting(self, mock_get_plot_path):
        """Test plotting multiple tracks for comparison."""
        
        def side_effect(filename):
            return os.path.join(self.temp_dir, filename)
        mock_get_plot_path.side_effect = side_effect
        
        # Create different track types
        tracks = {
            'straight': DummyTrackGenerator.create_straight_track(1000, 100),
            'oval': DummyTrackGenerator.create_oval_track(400, 200, 200),
            'complex': DummyTrackGenerator.create_complex_track(250)
        }
        
        # Test each track type
        for track_name, (x_coords, y_coords) in tracks.items():
            track_data = DummyTrackGenerator.create_track_data_dict(x_coords, y_coords)
            
            # Should plot successfully for each track
            plot_track_only(track_data, track_type='endurance', save_name=f'{track_name}_layout.png')
            plot_velocity_profile(track_data, track_type='endurance', save_name=f'{track_name}_velocity.png')
        
        # Should have called get_plot_path for each plot
        assert mock_get_plot_path.call_count == 6, "Should have made 6 plot calls"
    
    @patch('lap_simulation.plotting.get_plot_path')
    def test_track_type_specific_plotting(self, mock_get_plot_path):
        """Test plotting with different track types (endurance vs autocross)."""
        
        def side_effect(filename):
            return os.path.join(self.temp_dir, filename)
        mock_get_plot_path.side_effect = side_effect
        
        # Same track, different types
        x_coords, y_coords = DummyTrackGenerator.create_s_curve_track(600, 80, 3, 120)
        
        for track_type in ['endurance', 'autocross']:
            track_data = DummyTrackGenerator.create_track_data_dict(x_coords, y_coords, track_type)
            
            # Should handle both track types
            plot_track_only(track_data, track_type=track_type)
            plot_velocity_profile(track_data, track_type=track_type)
        
        assert mock_get_plot_path.call_count == 4, "Should have made 4 plot calls"


# Utility function for running specific test groups
def run_plotting_tests(test_group=None):
    """
    Run specific groups of plotting tests.
    
    Parameters:
    -----------
    test_group : str, optional
        Specific test group to run ('dummy', 'basic', 'layout', 'velocity', 'physics', 'error', 'integration', 'all')
    """
    if test_group is None or test_group == 'all':
        pytest.main([__file__, "-v"])
    else:
        test_class_map = {
            'dummy': 'TestDummyTrackGeneration',
            'basic': 'TestBasicPlottingFunctions', 
            'layout': 'TestTrackLayoutPlotting',
            'velocity': 'TestVelocityProfilePlotting',
            'physics': 'TestCompletePhysicsPlotting',
            'error': 'TestPlottingErrorHandling',
            'integration': 'TestPlottingIntegration'
        }
        
        if test_group in test_class_map:
            pytest.main([f"{__file__}::{test_class_map[test_group]}", "-v"])
        else:
            print(f"Unknown test group: {test_group}")
            print(f"Available groups: {list(test_class_map.keys()) + ['all']}")


if __name__ == "__main__":
    # Run all plotting tests by default
    run_plotting_tests('all')
