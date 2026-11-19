import json
import math
from pathlib import Path

CALIBRATION_FILE = Path(__file__).parent / 'calibration_copy.json'

CALIBRATION_DATA = json.load(open(CALIBRATION_FILE))

URDF_RANGES = {
    'shoulder_pan': [-1.91986, 1.91986],
    'shoulder_lift': [-1.74533, 1.74533],
    'elbow_flex': [-1.69, 1.69],
    'wrist_flex': [-1.65806, 1.65806],
    'wrist_roll': [-2.74385, 2.84121],
    'gripper': [-0.174533, 1.74533]
}

for joint, data in CALIBRATION_DATA.items():
    print("--------------------------------")
    
    print(f"Joint: {joint}")
    print(f"ID: {data['id']}")

    # Convert min and max range to radians
    range_min_rad = (data['range_min'] - 2047) * (2 * math.pi) / 4096
    range_max_rad = (data['range_max'] - 2047) * (2 * math.pi) / 4096
    
    
    print(f"Calculated Range Min Rad: {range_min_rad} URDF Range: {URDF_RANGES[joint][0]}")
    print(f"Calculated Range Max Rad: {range_max_rad} URDF Range: {URDF_RANGES[joint][1]}")
    
    print("--------------------------------")