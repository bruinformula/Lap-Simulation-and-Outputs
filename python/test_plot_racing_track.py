#!/usr/bin/env python3
"""
Test script for plot_racing_track module
"""

import sys
import os
import numpy as np

# Add the visualization module to path
sys.path.append('/Users/Hiro/Documents/Programming/GitHub/Lap-Simulation and Outputs/python')

try:
    print("Testing plot_racing_track module...")
    print("=" * 50)
    
    # Import the module
    from visualization.plot_racing_track import load_comprehensive_track_data, plot_comprehensive_track
    
    print("✅ Successfully imported plot_racing_track functions")
    
    # Set base directory
    base_dir = '/Users/Hiro/Documents/Programming/GitHub/Lap-Simulation and Outputs'
    print(f"Using base directory: {base_dir}")
    
    # Test loading track data
    print("\n🔄 Loading comprehensive track data...")
    track_data = load_comprehensive_track_data(base_dir)
    
    if track_data:
        print(f"✅ Successfully loaded track data for: {list(track_data.keys())}")
        
        # Test plotting for each track type
        for track_type, data in track_data.items():
            print(f"\n🎨 Testing plot for {track_type}...")
            try:
                plot_path = plot_comprehensive_track(data, track_type)
                print(f"✅ Successfully created plot for {track_type}")
                print(f"   Plot saved to: {plot_path}")
                
                # Show some data statistics
                if 'racing_line' in data and 'velocity' in data['racing_line']:
                    velocities = data['racing_line']['velocity']
                    distances = data['racing_line']['distance']
                    
                    print(f"   Track statistics:")
                    print(f"     Length: {distances[-1]:.0f} ft")
                    print(f"     Avg velocity: {np.mean(velocities):.1f} mph")
                    print(f"     Max velocity: {np.max(velocities):.1f} mph")
                    print(f"     Min velocity: {np.min(velocities):.1f} mph")
                    
            except Exception as e:
                print(f"❌ Error plotting {track_type}: {e}")
                import traceback
                traceback.print_exc()
    else:
        print("❌ No track data could be loaded")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure the visualization module is properly set up")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Test completed!")
