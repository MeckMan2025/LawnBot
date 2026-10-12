# Print guide

Generated from `cad/out/manifest.csv` by `cad/print_guide.py`. Re-run it after any CAD change.

## Printer settings (Bambu Lab H2C)
- **PETG parts:** 0.4 mm hardened nozzle, 0.2 mm layers, 255 C nozzle, 70 C bed, textured PEI. Walls and infill per the table (gyroid). Dry the spool first.
- **TPU 95A parts:** 0.4 mm nozzle, 0.2 mm layers, 230 C, 40 C bed, 30 mm/s, retraction short, no AMS (direct feed). Dry 8 hours at 65 C first.
- **Clear PETG window:** 0.4 mm nozzle, 100 percent infill, print slowly for clarity.
- **Supports:** only the parts marked `yes`. Use tree supports, 0.2 mm Z gap, and pull them before fitting bearings.
- **Heat-set inserts:** M2.5 (3.4 mm hole), M3 (4.0), M4 (5.6), M5 (6.4), M6 (8.0). Set them with a soldering iron at 230 C, keep them square.
- **Bearing seats:** modelled with 0.25 mm of interference. Test the first seat on a coupon; ream lightly if it needs more than thumb pressure plus a tap.

## Print order
1. **Coupons first:** print one `caster_axle_spacer_outer` and one `bearing_spacer` to check your TPU and PETG dimensions, then a 20 mm slice of `drive_axle_housing` to check the 6808 fit.
2. **Drive first:** `drive_wheel`, `drive_tread`, `drive_axle_housing`, `motor_mount_bracket`, `bearing_spacer`. You can test the motors with these alone.
3. **Chassis:** modules, lids, dowels, battery tray.
4. **Boom and casters:** arms, cross halves, risers, braces, legs, towers, forks, sleeves, rims, tires, spacers, deck quadrants.
5. **Enclosure and shell:** tub, lid, gasket, skirts, canopy quadrants, splices, fenders, bumper, camera mount and hood.
6. **Mast, rear fittings, dock.**

Mass is estimated from the solid volume, the wall count and the infill, so treat it as plus or minus 20 percent.

## Parts

| Part | Qty | Material | Size (mm) | Walls | Infill | Supports | Orientation | Est. mass each | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `chassis_module_rear_left` | 1 | PETG | 175.0 x 150.0 x 90.0 | 5 | 30% | no | open top up | 518 g | Open tray. Seam walls bolt to the neighbour with M5 x 20 and nuts; 6 mm dowels locate them. |
| `chassis_module_rear_right` | 1 | PETG | 175.0 x 150.0 x 90.0 | 5 | 30% | no | open top up | 518 g | Open tray. Seam walls bolt to the neighbour with M5 x 20 and nuts; 6 mm dowels locate them. |
| `chassis_module_front_left` | 1 | PETG | 175.0 x 150.0 x 90.0 | 5 | 30% | no | open top up | 511 g | Open tray. Seam walls bolt to the neighbour with M5 x 20 and nuts; 6 mm dowels locate them. |
| `chassis_module_front_right` | 1 | PETG | 175.0 x 150.0 x 90.0 | 5 | 30% | no | open top up | 511 g | Open tray. Seam walls bolt to the neighbour with M5 x 20 and nuts; 6 mm dowels locate them. |
| `chassis_lid_rear` | 1 | PETG | 175.0 x 300.0 x 14.0 | 4 | 30% | no | flat, ribs up | 287 g | Bolts to the rear modules with M4 x 12. Legs bolt into the M5 inserts. |
| `chassis_lid_front` | 1 | PETG | 175.0 x 300.0 x 14.0 | 4 | 30% | no | flat, ribs up | 289 g | Bolts to the front modules with M4 x 12. Risers and braces bolt into the M5 inserts. |
| `battery_tray` | 1 | PETG | 192.0 x 182.0 x 20.0 | 3 | 20% | no | as modelled (Z up) | 127 g | Sits on the chassis lid under the deck, just ahead of the axle. 2x M4 into the lid inserts, two 25 mm straps. |
| `alignment_dowel` | 16 | PETG | 6.0 x 6.0 x 16.0 | 3 | 100% | no | as modelled (Z up) | 1 g | 6 x 16 mm. Print standing up. |
| `drive_axle_housing` | 2 | PETG | 70.0 x 60.0 x 85.0 | 6 | 60% | no | flange down | 142 g | Flange bolts to the rear module outer wall with 4x M5 x 35 (heads in the counterbores, nuts on the motor mount inside). Fit before the wheel. Tube carries both 6808 bearings. |
| `motor_mount_bracket` | 2 | PETG | 70.0 x 60.0 x 16.0 | 5 | 40% | no | plate down | 38 g | Inside the chassis. Shares the M5 bolts with the axle housing. 4x M4 x 16 bolt the motor face through the standoff; the clamping coupler sits inside the housing's 20 mm bore. |
| `drive_wheel` | 2 | PETG | 290.0 x 290.0 x 80.0 | 4 | 25% | no | inner face down | 1097 g | 284 mm rim and hub in one piece. Press both 6808 bearings in from the inner (flat) face with the spacer between them. goBILDA REX hub bolts to the outer web. |
| `bearing_spacer` | 2 | PETG | 51.5 x 51.5 x 59.4 | 4 | 100% | no | as modelled (Z up) | 48 g | Sits between the two 6808 bearings inside the hub. |
| `drive_tread` | 2 | TPU 95A | 300.0 x 300.0 x 80.0 | 3 | 20% | no | flat | 376 g | Stretch over the rim; the three grooves snap onto the rim ribs. Print with 3 walls and 20 percent gyroid. |
| `caster_spindle_tower` | 2 | PETG | 100.0 x 100.0 x 110.0 | 6 | 50% | no | flange down | 345 g | Sits on the boom arm pad, 4x M6 x 50 down into the pad inserts. Press a 6004 bearing into each end. |
| `caster_spindle_sleeve` | 2 | PETG | 34.6 x 30.0 x 160.0 | 8 | 100% | no | standing, hex down | 42 g | Hex boss drops into the yoke crown. M12 x 180 bolt runs up through it; nylock nut and washer on top of the tower. |
| `caster_fork` | 2 | PETG | 130.0 x 156.0 x 187.0 | 6 | 50% | yes | on its side | 587 g | Yoke with 50 mm trail. Print on its side (one leg on the bed) with supports so layers run along the legs. M8 x 140 axle bolt. |
| `caster_rim` | 2 | PETG | 264.0 x 264.0 x 100.0 | 4 | 25% | no | flat | 1201 g | 258 mm rim. Press a 608 bearing into each end with the inner spacer between them. |
| `caster_tire` | 2 | TPU 95A | 280.0 x 280.0 x 100.0 | 3 | 15% | no | flat | 598 g | 280 x 100 mm. Stretch over the rim ribs. 3 walls, 15 percent gyroid for cushion. |
| `caster_axle_spacer_inner` | 2 | PETG | 13.5 x 13.5 x 85.4 | 4 | 100% | no | as modelled (Z up) | 9 g | Between the two 608 inner races. |
| `caster_axle_spacer_outer` | 4 | PETG | 16.0 x 16.0 x 9.5 | 4 | 100% | no | as modelled (Z up) | 2 g | Between each 608 and the fork leg. |
| `boom_arm_left` | 1 | PETG | 310.0 x 100.0 x 40.0 | 5 | 40% | no | flat | 329 g | 310 mm box section with the tower pad. Print flat, pad up. M6 x 50 tower bolts, M5 x 45 cross member bolts. |
| `boom_arm_right` | 1 | PETG | 310.0 x 100.0 x 40.0 | 5 | 40% | no | flat | 329 g | Mirror of the left arm. |
| `boom_cross_front_half` | 2 | PETG | 185.0 x 40.0 x 40.0 | 5 | 40% | no | flat | 144 g | Two halves lap at the center (turn one 180 degrees) with 2x M5 x 45 and nuts across the joint; the end plate bolts to the arm pad with 2x M5 x 16 through the pad wall. |
| `boom_cross_rear_half` | 2 | PETG | 210.0 x 40.0 x 40.0 | 5 | 40% | no | flat | 167 g | Same as the front halves, plus riser inserts underneath. |
| `riser_column` | 2 | PETG | 64.0 x 64.0 x 129.0 | 5 | 40% | no | foot down | 95 g | Bolt the risers to the rear cross member first (2x M5 x 20 up through the top plate, from inside the open column), then stand that subassembly on the lid and bolt the feet (4x M5 x 16). |
| `riser_brace` | 2 | PETG | 95.0 x 30.0 x 110.0 | 4 | 30% | no | flat | 49 g | Gusset from the lid to the riser rear face. Print flat on its side. |
| `rear_deck_leg` | 2 | PETG | 64.0 x 54.0 x 169.0 | 5 | 40% | no | foot down | 101 g | Chassis lid to upper deck. Foot: 4x M5 x 16. Deck bolts into the top inserts. |
| `deck_front_left` | 1 | PETG | 315.0 x 175.0 x 24.0 | 4 | 30% | no | ribs up (flipped) | 293 g | Ribbed plate. Print ribs up (flip the model). M4 insert grid on 40 mm for mounting. |
| `deck_front_right` | 1 | PETG | 315.0 x 145.0 x 24.0 | 4 | 30% | no | ribs up (flipped) | 259 g | Ribbed plate. Print ribs up (flip the model). M4 insert grid on 40 mm for mounting. |
| `deck_rear_left` | 1 | PETG | 285.0 x 175.0 x 24.0 | 4 | 30% | no | ribs up (flipped) | 287 g | Ribbed plate. Print ribs up (flip the model). M4 insert grid on 40 mm for mounting. |
| `deck_rear_right` | 1 | PETG | 285.0 x 145.0 x 24.0 | 4 | 30% | no | ribs up (flipped) | 253 g | Ribbed plate. Print ribs up (flip the model). M4 insert grid on 40 mm for mounting. |
| `enclosure_tub` | 1 | PETG | 266.0 x 226.0 x 80.0 | 4 | 25% | no | open top up | 446 g | 4x M4 x 12 feet bolts into the deck grid. Pi 5 on M2.5 inserts, other boards on the M3 grid via adapter plates. Fit PG9 glands. |
| `enclosure_lid` | 1 | PETG | 258.0 x 198.0 x 13.0 | 4 | 25% | no | flat, ribs up | 349 g | 8x M4 x 16 into the tub bosses. Gasket sits in the groove. |
| `enclosure_gasket` | 1 | TPU 95A | 249.6 x 189.6 x 2.6 | 2 | 100% | no | flat | 10 g | Press into the lid groove. 2 walls, 100 percent. |
| `skirt_rear` | 1 | PETG | 300.0 x 16.5 x 127.0 | 3 | 20% | no | flat on its back | 108 g | Bolts to the rear lid edge inserts (3x M4). Canopy screws into the top tabs. |
| `skirt_front` | 1 | PETG | 300.0 x 16.5 x 127.0 | 3 | 20% | no | flat on its back | 101 g | Between the risers; the bottom flange is gapped around the riser feet. Wire hole for the bumper loom. |
| `skirt_side_rear` | 2 | PETG | 172.0 x 13.0 x 127.0 | 3 | 20% | no | flat on its back | 61 g | One per side; mirror for the right side in the slicer. Fender bolts pass through the canopy into the bosses. |
| `skirt_side_front` | 2 | PETG | 172.0 x 16.5 x 127.0 | 3 | 20% | no | flat on its back | 60 g | One per side; mirror for the right side in the slicer. Fender bolts pass through the canopy into the bosses. |
| `fender` | 2 | PETG | 304.5 x 104.0 x 101.2 | 3 | 20% | no | on its side | 134 g | Half round over each drive wheel. 3x M4 into the skirt bosses. Print on its side (flange down). |
| `canopy_front_left` | 1 | PETG | 310.0 x 153.5 x 170.0 | 3 | 15% | no | upside down | 235 g | Print upside down (roof on the bed). Join with M3 x 10 screws through the seam tabs. |
| `canopy_front_right` | 1 | PETG | 310.0 x 153.5 x 170.0 | 3 | 15% | no | upside down | 235 g | Print upside down (roof on the bed). Join with M3 x 10 screws through the seam tabs. |
| `canopy_rear_left` | 1 | PETG | 310.0 x 153.5 x 170.0 | 3 | 15% | no | upside down | 258 g | Print upside down (roof on the bed). Join with M3 x 10 screws through the seam tabs. |
| `canopy_rear_right` | 1 | PETG | 310.0 x 153.5 x 170.0 | 3 | 15% | no | upside down | 256 g | Print upside down (roof on the bed). Join with M3 x 10 screws through the seam tabs. |
| `canopy_splice_wall` | 4 | PETG | 120.0 x 30.0 x 7.0 | 3 | 100% | no | flat | 19 g | Inside the canopy across each wall seam, M3 x 8 screws from outside. |
| `canopy_splice_roof_x` | 1 | PETG | 180.0 x 30.0 x 7.0 | 3 | 100% | no | flat | 28 g | Inside the roof across the front/rear seam. |
| `canopy_splice_roof_y` | 2 | PETG | 250.0 x 30.0 x 7.0 | 3 | 100% | no | flat | 39 g | Inside the roof along the left/right seam; one behind the mast, one ahead. |
| `bumper_carrier` | 1 | PETG | 300.0 x 44.0 x 60.0 | 4 | 30% | no | as modelled (Z up) | 402 g | Slides on two M5 x 30 shoulder bolts in the canopy nose with 10 mm springs. Two subminiature microswitches. |
| `bumper_skin` | 1 | TPU 95A | 304.0 x 13.7 x 70.0 | 3 | 20% | no | on its back | 105 g | Clips over the carrier's front lips. |
| `oak_mount` | 1 | PETG | 120.0 x 28.6 x 60.0 | 4 | 40% | no | as modelled (Z up) | 112 g | 10 degree down wedge. Camera on the 1/4-20 and M4 slots; 2x M4 into the canopy nose. |
| `oak_hood` | 1 | PETG | 136.0 x 50.0 x 36.0 | 3 | 20% | no | upside down | 44 g | Rain hood over the depth camera, 2x M4. |
| `mast_standoff` | 1 | PETG | 100.0 x 80.0 x 96.0 | 5 | 40% | no | as modelled (Z up) | 133 g | Deck grid to canopy roof. 4x M4 x 12 down into the deck, 4x M5 inserts on top for the mast base through the roof. |
| `mast_base` | 1 | PETG | 90.0 x 90.0 x 38.0 | 5 | 50% | no | as modelled (Z up) | 65 g | Sits on the canopy roof over the standoff. 4x M5 x 25. First tube slides over the spigot, M4 cross bolt. |
| `mast_segment` | 2 | PETG | 40.0 x 40.0 x 230.0 | 4 | 30% | no | standing | 94 g | 200 mm tube with a 30 mm spigot. Print standing. M4 x 45 cross bolts. |
| `pan_base` | 1 | PETG | 56.0 x 56.0 x 70.0 | 4 | 30% | no | as modelled (Z up) | 136 g | Top of the mast. Standard-size pan servo drops in from the top. |
| `tilt_bracket` | 1 | PETG | 70.0 x 60.0 x 64.0 | 4 | 30% | yes | as modelled (Z up) | 32 g | Bolts to the pan servo horn (25 mm pattern). Tilt servo in one arm, 6 mm pin on the other. |
| `camera_housing` | 1 | PETG | 60.0 x 57.0 x 64.0 | 3 | 20% | yes | open back down | 53 g | Pi Camera Module 3 on M2 screws, IR LED in the side hole. Rear cover on 2x M3. |
| `camera_cover` | 1 | PETG | 3.0 x 50.0 x 64.0 | 3 | 20% | no | flat | 7 g | Rear cover for the camera housing. |
| `camera_window` | 1 | clear PETG | 2.6 x 41.4 x 31.4 | 2 | 100% | no | flat | 4 g | Press into the housing recess; seal with a bead of silicone. |
| `gps_mount` | 1 | PETG | 89.5 x 71.0 x 68.0 | 4 | 30% | yes | as modelled (Z up) | 41 g | L bracket off the pan base rear face holding a 60 mm GPS puck. 2x M4. |
| `estop_housing` | 1 | PETG | 76.0 x 76.0 x 45.0 | 3 | 20% | no | as modelled (Z up) | 42 g | 22 mm mushroom E-stop. 4x M3 through the canopy roof. |
| `charge_port_housing` | 1 | PETG | 26.0 x 80.0 x 60.0 | 4 | 30% | yes | as modelled (Z up) | 65 g | Rear face of the canopy. Two 10 x 30 mm spring pads face the dock. |
| `light_bar_housing` | 1 | PETG | 180.0 x 16.0 x 14.0 | 3 | 20% | no | as modelled (Z up) | 14 g | 12 mm LED strip plus a 12 mm buzzer. 2x M3 into the canopy rear face. |
| `contact_pad_carrier` | 1 | PETG | 8.0 x 120.0 x 30.0 | 3 | 30% | no | as modelled (Z up) | 22 g | Rear of the chassis, carries the two copper charge pads. 2x M4. |
| `dock_tile` | 4 | PETG | 275.0 x 310.0 x 14.0 | 3 | 15% | no | as modelled (Z up) | 730 g | 275 x 310 floor tile with the lap tabs. Four tiles lap together with M5 x 20; 10 mm ground stakes at the corners. |
| `dock_rail_half` | 4 | PETG | 240.0 x 40.0 x 40.0 | 3 | 20% | no | as modelled (Z up) | 121 g | Two halves per rail. Bolt to the tile inserts to funnel the caster tires. |
| `dock_contact_block` | 1 | PETG | 80.0 x 160.0 x 150.0 | 4 | 25% | no | as modelled (Z up) | 220 g | Holds two spring contacts facing the robot's rear pads. Bolt to the tiles. |
| `dock_rain_cover` | 1 | PETG | 100.0 x 220.0 x 65.0 | 3 | 20% | no | upside down | 95 g | Over the contact block. Print upside down. |
| `dock_tag_frame` | 1 | PETG | 140.0 x 140.0 x 36.0 | 3 | 20% | no | as modelled (Z up) | 58 g | Holds a 120 mm printed AprilTag for final docking alignment. Bolts to the rain cover posts. |

## Filament estimate
- PETG: about 20.5 kg
- TPU 95A: about 2.1 kg
- clear PETG: about 0.0 kg
- **Total: about 22.5 kg**
