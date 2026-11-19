# Calibration

How raw servo readings become joint angles, how the real arm compares with the URDF, and every
change made because of it. These values carry into `so101_bringup/config/hardware.yaml` for the
C++ hardware interface.

## Tick → radian conversion

```
angle_rad = sign × (Present_Position − 2047) / 4096 × 2π − offset
```

- **4096**: the STS3215 encoder is 12-bit, so it reports positions 0–4095 per revolution.
- **2047**: the half turn, `(4096 − 1) // 2`, the same value LeRobot uses.
- **sign**: +1 if the servo's positive direction matches the URDF joint axis, −1 if not.
- **offset**: any remaining difference between the real arm's zero and the URDF's zero pose.

### Why subtracting 2047 is enough: the homing offset

LeRobot's calibration (robot ID `lil_follower_boi`) had the arm placed at the middle of its range,
then wrote a `Homing_Offset` (register 31, EEPROM) into each servo so that the pose reads 2047. The
servo applies it internally:

```
Present_Position = raw_encoder − Homing_Offset
```

So the positions read from register 56 are already centered. **The homing offsets must not be applied
again in code**, and register 31 must not be written unless the arm is recalibrated. The values
LeRobot wrote are kept for reference in `so101_description/calibration/calibration_copy.json`.

## Per-joint results

Ranges from LeRobot calibration (`range_min` / `range_max`) converted with the formula above, unless
noted as measured with the mirror node.

| Joint | ID | Sign | Offset | Real range (rad) | URDF limits (rad) | Status |
|---|---|---|---|---|---|---|
| shoulder_pan | 1 | +1 | 0 (not yet checked) | −1.980 … +2.143 | −1.920 … +1.920 | URDF inside real range, kept. Lopsided range: verify stops with mirror node |
| shoulder_lift | 2 | +1 | 0 (not yet checked) | −1.792 … +1.807 | −1.745 … +1.745 | URDF inside real range, kept |
| elbow_flex | 3 | +1 | 0 (pending zero-pose check) | **−1.78 … +1.577 (measured)** | −1.69 … **+1.50** | Upper limit tightened from 1.69 |
| wrist_flex | 4 | +1 | 0 (not yet checked) | −1.859 … +1.721 | −1.658 … +1.658 | URDF inside real range, kept. Lopsided range: verify stops with mirror node |
| wrist_roll | 5 | +1 | 0 (not yet checked) | full rotation (0–4095 ticks, ±π) | −2.744 … +2.841 | No hard stop to compare, kept |
| gripper | 6 | +1 | 0 (not yet checked) | −0.091 … +2.131 | **−0.05** … +1.745 | Lower limit tightened from −0.175 |

### Sign

All six joints move in the same direction in RViz as on the real arm when moved by hand, so every
sign is +1, and every `drive_mode` in the LeRobot calibration is 0 (not reversed). This is expected:
`so101_new_calib.urdf` was made to match LeRobot's conventions. The sign is still kept as a
parameter in the hardware interface in case a servo is remounted or the URDF changes.

## Changes to the URDF

Rule used: if the URDF allows motion past a real hard stop, tighten it to a few degrees inside the
stop, so no controller or planner commands a servo into a stop (it stalls at high current and heats
up). If the URDF is more conservative than the real arm, leave it.

### elbow_flex upper: 1.69 → 1.50

- The calibration range suggested the real elbow stopped around +1.563, short of the URDF's 1.69,
  with the whole range shifted about 7° negative.
- **Hypothesis tried:** the table blocked the elbow during calibration, so one end was cut short.
  **Wrong:** measuring with the mirror node (arm lifted clear of the table) gave full extension at
  −1.78, matching calibration. The short end is the folded direction, not extension.
- Measured folded stop: **+1.577**. The URDF let the elbow fold about 6° past it, which is the
  self-collision seen in RViz near +1.69 during issue #1.
- New limit 1.50 leaves about 4.4° of margin. The 7° "shift" is the stops being asymmetric, not a
  zero offset.

### gripper lower: −0.175 → −0.05

- Real closed position is −0.091 (about −5.2°); the URDF allowed −10°.
- New limit −0.05 leaves about 2.3° of margin. This also explains why the gripper looked not fully
  closed at 0 rad in issue #1: closed is slightly below 0.

## Joint limits vs. obstacles

The table limits how far some joints can move, but only depending on where other joints are (for
example the elbow can extend fully only when shoulder_lift raises the arm). That's not a joint
limit. Joint limits describe each joint's own hard stops. Obstacles like the table belong in
MoveIt's collision scene (Milestone 3).

## To do

- [ ] Zero-pose check on each joint: put the real joint at RViz's 0 pose, confirm the mirror node
      reads about 0. Any consistent difference becomes that joint's `offset`.
- [ ] Measure the real stops of shoulder_pan and wrist_flex with the mirror node (their calibration
      ranges are lopsided).
- [ ] Copy final sign/offset values into `so101_bringup/config/hardware.yaml` (step 4).
