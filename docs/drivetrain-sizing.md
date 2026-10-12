# Drivetrain sizing

All figures use the revision 4 geometry: 300 mm drive wheels, two goBILDA 5203 71.2:1 motors, 12.8 V 20 Ah LiFePO4, estimated mass 17 kg with about 65 percent of it on the drive wheels.

## Motor data (goBILDA 5203, 71.2:1)
| | |
|---|---|
| No-load speed | 84 rpm |
| Stall torque | 93.6 kg.cm (9.18 N.m) |
| Stall current | 9.2 A at 12 V |
| Continuous torque (rule of thumb, 25 percent of stall) | about 23 kg.cm |

## Speed
Wheel circumference = pi x 0.300 m = 0.942 m.
Top speed = 84 rpm / 60 x 0.942 m = **1.32 m/s** (no load). Under load expect about 1.1 m/s. Software caps it at **1.0 m/s**, and patrols run at 0.5 to 0.7 m/s.

## Torque needed
Force to move = m g (sin(slope) + Crr cos(slope)). Rolling resistance Crr on lawn is about 0.08.

| Case | Force | Per wheel | Torque per wheel | Fraction of stall |
|---|---|---|---|---|
| Flat lawn, steady | 17 x 9.81 x 0.08 = 13.3 N | 6.7 N | 1.0 N.m = 10 kg.cm | 11 percent |
| 15 percent slope on lawn (8.5 deg) | 166.8 x (0.148 + 0.079) = 37.9 N | 19 N | 2.8 N.m = 29 kg.cm | 31 percent |
| 25 percent slope on lawn (14 deg) | 166.8 x (0.242 + 0.078) = 53.4 N | 26.7 N | 4.0 N.m = 41 kg.cm | 44 percent |

Verdict: comfortable on the flat, fine for intermittent 15 percent climbs (slightly above the continuous rating, well below stall), and the 25 percent case is still under half of stall. If the yard has long steep sections, step up to the 5203 139:1 (43 rpm, 0.68 m/s) for twice the margin.

## Traction
Normal force on the drive wheels = 0.65 x 17 x 9.81 = 108 N. With a tire-on-grass friction coefficient of about 0.5, the wheels can push 54 N before slipping, which covers the 15 percent slope case (38 N) and most of the 25 percent case. Spinning in place twists the tires against the grass, which is why the software prefers arcs.

## Current and runtime
Motor current scales with torque: about 1 A per wheel on the flat, 3 A per wheel on the 15 percent slope.

| Load | Power |
|---|---|
| Pi 5, OAK-D, GPS, IMU, servos, radio | about 15 W |
| Driving on the flat at 0.7 m/s | 2 x 1 A x 12.8 V = 26 W |
| Idle at a checkpoint (camera + AI call) | about 18 W |

A patrol that drives half the time: about 32 W average. The pack holds 256 Wh; using 80 percent of it gives **about 6 hours** of patrol, or about 3.5 hours if the route is mostly slopes. The plan's 3-hour figure is the conservative one to design the schedule around.

## Caster check
Each caster carries about 3 kg static. A 608 bearing is rated for about 3.3 kN dynamic load, so even a 10x impact from a rut is inside its rating. The M8 axle sees at most 150 N of shear, far below its limit. The M12 spindle sees a bending moment of about 150 N x 0.05 m trail = 7.5 N.m at the lower bearing, which an 8.8 bolt handles with a large margin.
