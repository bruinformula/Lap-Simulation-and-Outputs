# Development Guide

## Getting Started

### Environment Setup
1. Create virtual environment:
   ```bash
   python -m venv lap_simulation_env
   source lap_simulation_env/bin/activate  # On Windows: lap_simulation_env\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Project Structure
- `lap_simulation/` - Core simulation package
- `demos/` - Example scripts and demonstrations  
- `visualization/` - Plotting and visualization tools
- `testing/` - Unit tests and validation scripts
- `plots/` - Generated output files
- `docs/` - Documentation

## Code Style Guidelines

### Python Standards
- Follow PEP 8 style guide
- Use type hints for function parameters and returns
- Include comprehensive docstrings
- Maximum line length: 100 characters

### Documentation Format
```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief description of function.
    
    Parameters:
    -----------
    param1 : type
        Description of parameter 1
    param2 : type  
        Description of parameter 2
        
    Returns:
    --------
    return_type
        Description of return value
        
    Examples:
    ---------
    >>> result = function_name(value1, value2)
    >>> print(result)
    expected_output
    """
```

### Variable Naming
- Use descriptive names: `lateral_acceleration` not `lat_acc`
- Constants in UPPER_CASE: `GRAVITY = 9.81`
- Private methods with underscore: `_internal_method()`
- Units in variable names when unclear: `velocity_ms`, `force_N`

## Testing Guidelines

### Unit Tests
Create tests in `testing/` directory:

```python
import unittest
from lap_simulation.tire_model import TireModel

class TestTireModel(unittest.TestCase):
    def setUp(self):
        self.tire = TireModel()
    
    def test_lateral_force_calculation(self):
        # Test with known values
        Fy = self.tire.calculate_lateral_force(0.1, 1000)
        self.assertAlmostEqual(Fy, expected_value, places=2)
```

### Validation Tests
Compare Python results with MATLAB:

```python
def test_matlab_compatibility():
    # Load MATLAB reference data
    matlab_results = load_matlab_data('reference_results.mat')
    
    # Run Python simulation
    python_results = run_simulation()
    
    # Compare within tolerance
    np.testing.assert_allclose(python_results, matlab_results, rtol=1e-3)
```

## Contributing

### Before Submitting
1. Run all tests: `python -m pytest testing/`
2. Check code style: `flake8 lap_simulation/`
3. Update documentation if needed
4. Add/update tests for new features

### Git Workflow
1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes with clear commit messages
3. Test thoroughly
4. Submit pull request with description

### Performance Optimization
- Profile with `cProfile` before optimizing
- Use NumPy vectorization over loops
- Cache expensive calculations
- Consider numba for critical paths

## Common Issues

### Data Loading Problems
- Ensure .mat files are in correct format
- Check file paths are relative to script location
- Verify Excel sheet names match expected values

### Physics Calculations
- Check unit conversions (metric vs imperial)
- Validate sign conventions for coordinates
- Ensure realistic parameter ranges

### Plotting Issues
- Install matplotlib with appropriate backend
- Check data array shapes before plotting
- Handle NaN/inf values in datasets

## Debugging Tips

### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Interactive Debugging
```python
import pdb; pdb.set_trace()  # Insert breakpoint
```

### Data Inspection
```python
import numpy as np
print(f"Array shape: {data.shape}")
print(f"Min/Max: {np.min(data):.3f}/{np.max(data):.3f}")
print(f"Has NaN: {np.any(np.isnan(data))}")
```
