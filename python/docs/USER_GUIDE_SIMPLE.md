# User Guide - Understanding the Physics Behind Lap Simulation

This guide explains what the simulation does and how to interpret the results from a physics perspective.

## What the Simulation Does

The lap simulation takes a racing track (defined by X,Y coordinates) and calculates:
1. How much sideways acceleration (lateral g-force) is needed at each point
2. How much forward/backward acceleration (longitudinal g-force) occurs
3. How weight shifts between the four wheels
4. How much the car body rolls during cornering

## Understanding the Physics

### 1. Why Cars Need Lateral Acceleration in Turns

When you drive in a straight line, you don't need any sideways force. But when you turn, you need centripetal force to follow the curved path.

**The Physics**: `a_lateral = v² / r`
- `v` = your speed
- `r` = radius of the turn (sharper turns have smaller radius)
- `a_lateral` = sideways acceleration needed

**What this means**: 
- Go twice as fast → need 4x the sideways force
- Take a turn twice as sharp → need 2x the sideways force

### 2. Where Lateral Acceleration Comes From

The sideways force comes from your tires. When you turn the steering wheel, the front tires point sideways relative to where the car is moving. This creates a "slip angle" that generates lateral force.

**The Physics**: Tires work like springs up to a point, then they slip
- Small slip angle → tire force builds up
- Medium slip angle → maximum tire force
- Large slip angle → tire force drops (you're sliding)

### 3. Why Weight Shifts During Turns

When you turn, your body gets pushed to the outside of the turn. The same thing happens to the car's weight.

**The Physics**: `Weight_transfer = (lateral_acceleration × mass × CG_height) / track_width`

**What this means**:
- Higher center of gravity → more weight transfer
- Harder cornering → more weight transfer
- Wider car → less weight transfer for same cornering

### 4. Why the Car Body Rolls

The car "leans" into turns because the springs and anti-roll bars resist the rolling motion but don't eliminate it completely.

**The Physics**: `Roll_angle = (lateral_force × CG_height) / (front_stiffness + rear_stiffness)`

**What this means**:
- Stiffer anti-roll bars → less body roll
- Higher center of gravity → more body roll
- Harder cornering → more body roll

## Running the Simulation

### Basic Usage
```bash
cd python
python main.py
```

This will:
1. Load the endurance track coordinates
2. Calculate accelerations for the entire lap
3. Calculate wheel loads and roll angles
4. Create plots showing the results

### What Files Are Created

The simulation creates several plots in the `outputs/plots/` folder:

**`acceleration_plots.png`**: Shows lateral and longitudinal accelerations vs. distance around the track
**`corner_loads.png`**: Shows the load on each wheel throughout the lap
**`roll_angles.png`**: Shows how much the car leans during different parts of the track

## Interpreting the Results

### Acceleration Plots

**Longitudinal Acceleration (Blue Line)**:
- **Positive values**: Car is accelerating (throttle on)
- **Negative values**: Car is braking
- **Zero values**: Car is coasting at constant speed

**Lateral Acceleration (Red Line)**:
- **High values**: Car is in a tight turn
- **Low values**: Car is on a straight section or gentle curve
- **Typical range**: 0.8g to 1.5g for a racing car

### Corner Load Plots

These show how much weight each wheel is supporting:

**Front Left (FL)**: 
- **Higher loads**: When turning right (weight shifts left) or braking (weight shifts forward)
- **Lower loads**: When turning left or accelerating

**Front Right (FR)**:
- **Higher loads**: When turning left or braking
- **Lower loads**: When turning right or accelerating

**Rear Left (RL)**:
- **Higher loads**: When turning right or accelerating (weight shifts back)
- **Lower loads**: When turning left or braking

**Rear Right (RR)**:
- **Higher loads**: When turning left or accelerating
- **Lower loads**: When turning right or braking

### Roll Angle Plots

**Positive angles**: Car is leaning to the right
**Negative angles**: Car is leaning to the left
**Typical values**: 1-3 degrees for a racing car with stiff suspension

## Understanding the Vehicle Parameters

You can modify the car's characteristics in `vehicle_config.py`:

### Mass Properties
- **`mass`**: Heavier cars need more force to accelerate but have more grip
- **`cg_height`**: Lower center of gravity reduces weight transfer and body roll

### Suspension
- **`roll_stiffness_front/rear`**: Stiffer settings reduce body roll but may reduce grip on bumpy tracks

### Geometry
- **`wheelbase`**: Longer wheelbase generally improves stability
- **`track_width`**: Wider track reduces weight transfer for same lateral acceleration

## Common Physics Insights

### Why Racing Cars Are Low and Wide
- **Low**: Reduces center of gravity height, minimizing weight transfer and body roll
- **Wide**: Reduces weight transfer for a given lateral acceleration

### Why Soft vs. Stiff Suspension
- **Soft**: Better for bumpy tracks, keeps tires in contact with ground
- **Stiff**: Better for smooth tracks, reduces body movement and weight transfer

### Why Weight Transfer Matters
- Tires generate maximum force at an optimal load
- Too little load: tire can't generate much force
- Too much load: tire becomes overloaded and loses efficiency
- Even loading gives maximum total grip

## Troubleshooting Unrealistic Results

### If Accelerations Look Too High
- Check vehicle mass (should be 200-300 kg for Formula SAE)
- Check track curvature calculation (very sharp turns may have calculation errors)
- Verify units (acceleration should be in g-force, typically < 2.0g)

### If Load Transfer Looks Wrong
- Check center of gravity height (should be 0.25-0.4m for racing car)
- Verify track width (should be 1.0-1.4m typically)
- Check that loads sum to total vehicle weight

### If Roll Angles Look Unrealistic
- Check roll stiffness values (should be 500-2000 Nm/rad for racing car)
- Verify center of gravity height above roll center
- Racing cars typically have < 3 degrees roll angle

## Next Steps

Once you understand the basic physics, you can:
1. Modify vehicle parameters to see how they affect performance
2. Try different track layouts
3. Analyze specific sections of the track in detail
4. Compare different vehicle setups

The key is understanding that everything is connected: the track shape determines required accelerations, which cause load transfer, which affects tire grip, which limits how fast you can go.
