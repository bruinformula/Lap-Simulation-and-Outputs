# Documentation Index

Welcome to the Python Lap Simulation documentation. This directory contains comprehensive guides for using, developing, and understanding the lap simulation software.

## Documentation Structure

### 📖 [User Guide](USER_GUIDE.md)
**Start here if you're new to the software**
- Quick start instructions
- Basic usage examples
- Parameter customization
- Troubleshooting common issues
- Output interpretation

### 🔧 [Development Guide](DEVELOPMENT.md) 
**For developers and contributors**
- Setting up development environment
- Code style guidelines
- Testing procedures
- Contributing workflow
- Performance optimization tips

### 📚 [API Reference](API.md)
**Complete function and class documentation**
- Core classes (DataManager, TireModel, PowertrainModel, LapSimulator)
- Function signatures and parameters
- Data structures and configurations
- Error handling examples
- Performance notes

## Quick Navigation

### Getting Started
1. [Installation](USER_GUIDE.md#installation) - Set up the environment
2. [First Simulation](USER_GUIDE.md#running-your-first-simulation) - Run your first lap
3. [Understanding Output](USER_GUIDE.md#understanding-the-output) - Interpret results

### Common Tasks
- [Change vehicle parameters](USER_GUIDE.md#vehicle-parameters)
- [Switch between tracks](USER_GUIDE.md#track-selection)
- [Create custom plots](USER_GUIDE.md#custom-visualizations)
- [Run batch simulations](USER_GUIDE.md#batch-processing)

### Development
- [Code style](DEVELOPMENT.md#code-style-guidelines)
- [Adding tests](DEVELOPMENT.md#testing-guidelines)
- [Contributing code](DEVELOPMENT.md#contributing)
- [Debugging tips](DEVELOPMENT.md#debugging-tips)

### API Reference
- [Core Functions](API.md#function-reference)
- [Class Methods](API.md#core-classes-and-functions)
- [Data Structures](API.md#data-structures)
- [Error Handling](API.md#error-handling)

## File Organization

```
docs/
├── README.md           # This file - documentation index
├── USER_GUIDE.md       # End-user documentation
├── DEVELOPMENT.md      # Developer guidelines
└── API.md             # Technical API reference
```

## Additional Resources

### Example Scripts
- `../demos/` - Working examples and demonstrations
- `../visualization/` - Plotting and analysis tools
- `../testing/` - Test cases and validation scripts

### Generated Output
- `../plots/` - Visualization files from simulations
- `../simulation_results.csv` - Numerical data output

## Version Information

This documentation corresponds to the Python conversion of the MATLAB lap simulation code, featuring:

- **Complete MATLAB compatibility**: All original functionality preserved
- **Enhanced physics**: Realistic acceleration magnitudes and proper sign conventions
- **High-resolution data**: 1000-point racing lines for improved accuracy
- **Modern architecture**: Object-oriented design with comprehensive error handling

## Getting Help

1. **Start with the User Guide** for basic usage questions
2. **Check the API Reference** for specific function details  
3. **Review example scripts** in the demos directory
4. **Consult the Development Guide** for advanced topics

## Contributing to Documentation

Documentation improvements are welcome! Please:
1. Follow the existing format and structure
2. Include practical examples where helpful
3. Keep language clear and concise
4. Test any code examples before submitting

---

**Last Updated**: July 2025  
**Python Version**: 3.13.5  
**MATLAB Compatibility**: R2023b+
