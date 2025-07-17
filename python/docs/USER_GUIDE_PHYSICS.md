# User Guide - Vehicle Dynamics and Physics

## Overview

This user guide explains the physics models and vehicle dynamics principles implemented in the lap simulation system. The focus is on understanding the underlying motorsports engineering concepts and how they translate to realistic vehicle behavior simulation.

## Physics Fundamentals

### Vehicle Dynamics Coordinate System

The simulation follows SAE J670 vehicle dynamics coordinate system:
- **X-axis**: Forward direction (longitudinal)
- **Y-axis**: Lateral direction (left positive)
- **Z-axis**: Vertical direction (up positive)
- **Origin**: At vehicle center of gravity

### Force and Moment Conventions
- **Longitudinal Forces**: Positive for acceleration, negative for braking
- **Lateral Forces**: Positive for left turn (right-hand coordinate system)
- **Normal Forces**: Always positive (upward)
- **Moments**: Follow right-hand rule convention

## Core Physics Models

### 1. Track Geometry and Kinematics

#### Track Curvature Calculation
The simulation processes track coordinates to determine local curvature:

```
Curvature (κ) = |x'y'' - y'x''| / (x'² + y'²)^(3/2)
```

Where x', y' are first derivatives and x'', y'' are second derivatives with respect to distance.

**Physical Significance:**
- Higher curvature requires greater lateral acceleration
- Curvature sign determines turn direction
- Smooth curvature transitions prevent unrealistic acceleration spikes

#### Required Lateral Acceleration
For a given curvature and speed, the required lateral acceleration is:

```
a_lateral = v² × κ
```

**Physical Constraints:**
- Limited by tire friction circle
- Affects vehicle speed through corners
- Determines racing line optimization

### 2. Tire Physics - Magic Formula 5.2

#### Lateral Force Generation
The Magic Formula 5.2 model calculates tire lateral force:

```
Fy = D × sin(C × arctan(B × α - E × (B × α - arctan(B × α))))
```

Where:
- **D**: Peak force factor (load dependent)
- **C**: Shape factor (typically ~1.3 for racing tires)
- **B**: Stiffness factor (determines initial slope)
- **E**: Curvature factor (affects peak shape)
- **α**: Slip angle [radians]

**Physical Behavior:**
- **Linear Region**: Small slip angles, high stiffness
- **Peak Force**: Maximum lateral force generation
- **Saturation Region**: Decreasing force with increasing slip angle

#### Load Sensitivity
Peak force varies with normal load:

```
D = D₀ × (Fz/Fz₀)^n
```

Where:
- **D₀**: Peak force at reference load
- **Fz₀**: Reference normal load
- **n**: Load sensitivity exponent (typically 0.8-1.2)

**Engineering Significance:**
- Load transfer affects individual tire performance
- Optimal load distribution maximizes total grip
- Aerodynamic downforce increases tire capability

### 3. Vehicle Load Transfer

#### Lateral Load Transfer
During cornering, load transfers from inside to outside wheels:

```
ΔFz_lateral = (ay × m × h) / t
```

Where:
- **ay**: Lateral acceleration [m/s²]
- **m**: Vehicle mass [kg]
- **h**: CG height [m]
- **t**: Track width [m]

**Individual Wheel Loads:**
```
Fz_left = (m×g)/2 - ΔFz_lateral
Fz_right = (m×g)/2 + ΔFz_lateral
```

#### Longitudinal Load Transfer
During acceleration/braking, load transfers between front and rear:

```
ΔFz_longitudinal = (ax × m × h) / L
```

Where:
- **ax**: Longitudinal acceleration [m/s²]
- **L**: Wheelbase [m]

**Axle Load Distribution:**
```
Fz_front = Fz_static_front ± ΔFz_longitudinal
Fz_rear = Fz_static_rear ∓ ΔFz_longitudinal
```

### 4. Suspension and Roll Dynamics

#### Roll Angle Calculation
Vehicle roll angle depends on lateral acceleration and suspension properties:

```
φ = (ay × m × H) / (Kφ_front + Kφ_rear)
```

Where:
- **H**: Roll moment arm height [m]
- **Kφ**: Roll stiffness [Nm/rad]

**Roll Moment Arm:**
```
H = h_cg - h_rc
```

Where:
- **h_cg**: Center of gravity height
- **h_rc**: Roll center height

**Physical Effects:**
- Higher CG increases roll angle
- Stiffer suspension reduces roll angle
- Roll affects tire camber and contact patch

#### Roll Stiffness Distribution
Total roll stiffness is distributed between front and rear:

```
Roll_distribution = Kφ_front / (Kφ_front + Kφ_rear)
```

**Handling Effects:**
- Front-biased stiffness increases understeer tendency
- Rear-biased stiffness increases oversteer tendency
- Optimal distribution depends on vehicle balance goals

### 5. Aerodynamic Forces

#### Downforce Generation
Aerodynamic downforce follows speed-squared relationship:

```
Fz_aero = 0.5 × ρ × v² × CL × A
```

Where:
- **ρ**: Air density [kg/m³]
- **v**: Vehicle speed [m/s]
- **CL**: Lift coefficient (negative for downforce)
- **A**: Reference area [m²]

#### Drag Force
Aerodynamic drag opposes motion:

```
Fx_drag = 0.5 × ρ × v² × CD × A
```

**Performance Trade-offs:**
- Higher downforce improves cornering but increases drag
- Aerodynamic balance affects front/rear grip distribution
- Speed sensitivity requires different setups for different tracks

### 6. Powertrain Physics

#### Engine Torque Curve
Realistic engine torque varies with RPM:

```
T(rpm) = T_max × f(rpm/rpm_peak)
```

Typical Formula SAE engine characteristics:
- **Peak Torque**: ~80-100 Nm at 6000-7000 RPM
- **Redline**: 10,000-12,000 RPM
- **Power**: 60-85 HP peak

#### Wheel Force Calculation
Drive force at wheels depends on gear selection:

```
Fx_drive = T_engine × gear_ratio × final_drive × efficiency / R_wheel
```

**Traction Limits:**
```
Fx_max = μ × Fz_driven_wheels
```

Where **μ** is the tire-road friction coefficient.

## Simulation Workflow

### 1. Track Processing
1. **Coordinate Import**: Load X,Y coordinates from Excel file
2. **Interpolation**: Create high-resolution racing line (1000+ points)
3. **Curvature Calculation**: Compute local track curvature
4. **Distance Integration**: Calculate cumulative distance along track

### 2. Vehicle State Calculation
1. **Speed Profile**: Determine maximum cornering speeds
2. **Acceleration Limits**: Apply tire friction circle constraints
3. **Load Transfer**: Calculate dynamic wheel loads
4. **Roll Dynamics**: Compute vehicle roll angles

### 3. Force Integration
1. **Tire Forces**: Calculate lateral and longitudinal forces
2. **Aerodynamic Forces**: Compute downforce and drag
3. **Powertrain Forces**: Determine drive/brake forces
4. **Force Balance**: Ensure physical consistency

### 4. Results Generation
1. **Acceleration Profiles**: Output longitudinal and lateral accelerations
2. **Load Analysis**: Individual wheel loads throughout lap
3. **Performance Metrics**: Lap time, sector times, peak accelerations
4. **Visualization**: Track layouts and data plots

## Physics Validation

### Validation Checks
- **Force Balance**: Sum of forces equals mass × acceleration
- **Energy Conservation**: Kinetic + potential energy changes match work done
- **Friction Circle**: Combined forces stay within tire limits
- **Physical Limits**: Accelerations within realistic ranges

### Typical Results
- **Lateral Acceleration**: 1.0-2.0g in steady-state cornering
- **Longitudinal Acceleration**: 0.8-1.2g acceleration, 1.0-1.5g braking
- **Roll Angles**: 0.5-2.0 degrees typical for formula car
- **Load Transfer**: 15-30% of static load during maneuvers

## Engineering Applications

### Vehicle Setup Optimization
- **Weight Distribution**: Front/rear balance for desired handling
- **Suspension Tuning**: Roll stiffness distribution and spring rates
- **Aerodynamic Balance**: Front/rear downforce distribution
- **Tire Pressure**: Optimization for load transfer conditions

### Performance Analysis
- **Sector Timing**: Identify lap time improvement opportunities
- **Acceleration Analysis**: Evaluate powertrain and aerodynamic performance
- **Tire Loading**: Assess tire utilization and degradation
- **Setup Sensitivity**: Parameter sweep studies for optimization

### Design Trade-offs
- **Aerodynamics vs Weight**: Downforce benefits vs added mass
- **CG Height**: Handling vs roll dynamics
- **Wheelbase**: Stability vs agility
- **Track Width**: Load transfer vs packaging constraints

This physics-based approach provides accurate vehicle behavior modeling suitable for engineering analysis and vehicle development applications.
