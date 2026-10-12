# ClaudeBot: Outdoor Patrol and Security Robot

Revision 5 (2026-10-12). Supersedes earlier revisions. Changes since revision 1 are folded in: everything structural is printed, PETG for the first build, two rear drive wheels plus two zero-turn-mower-size front casters, the mower-style raised front boom that those casters require, and the corrections that came out of the virtual build audit (phase 1 is complete: 68 parts modelled, exported, interference-checked and assembly-audited).

## Context
Andrew wants to design, 3D print, and assemble his own AI robot that solves a real problem for a person. The chosen problem: **a mobile outdoor property helper that patrols a yard (under 1 acre: lawn, paths, gentle slopes) and reports on security**. It should notice gates left open, packages, animals, people, and damage, then alert him with photos. He prints on a **Bambu Lab H2C**, uses a **Raspberry Pi 5 + Claude API** as the brain, and wants **CadQuery (Python) CAD with STEP + STL output**. Budget isn't a constraint, and he has some electronics experience (soldering, Pi).

Outcome: a repo with parametric CAD for every printed part, a full BOM, a wiring diagram, print and assembly guides, and the robot software (drive, navigation, Claude-powered patrol reports, alerts, docking).

## Hard requirements (set by Andrew)
1. **Every structural part is 3D printed:** chassis, boom, wheels, tires, casters, axle housings, enclosure, shell, mast, and dock. Only electronics, gearmotors, ball bearings, shafts, and fasteners are bought.
2. **Drivetrain:** two large rear drive wheels (300 x 80 mm), each with its own motor, plus two front swivel casters. Differential drive turns without dragging tires sideways, so it is gentle on grass.
3. **Casters are zero-turn mower size** (11x4.00-5 class: 280 mm tire, 100 mm wide) so they roll over ruts and divots instead of dropping into them.
4. **PETG** for all rigid parts in the first build, **TPU 95A** for treads, tires, gaskets, and the bumper skin.

## Layout (follows a zero-turn mower)
A 280 mm caster sweeps a 190 mm circle around its spindle when it swings. Anything at tire height inside that circle gets hit, so the body is split into two levels, the way a mower frame is:

- **Low chassis (rear):** x = -280 to +70, 300 wide, 90 tall, bottom at 90 mm ground clearance. Holds the two drive motors. It stops behind the caster swing circle.
- **Battery:** lies flat on the chassis lid (under the deck, between the deck legs and the riser feet), centred at x = -100. The chassis cells are split by the module seam walls, so the pack cannot go inside them.
- **Raised front boom:** underside at 315 mm, above the 280 mm tire tops. Two longitudinal arms at y = +/-200 mm and two cross members (x = 30 and 280) carry the caster spindle towers on pads at the arms' front ends. The tires and yoke crowns swing a full circle underneath; the canopy's bottom band is cut away ahead of x = 165 for the crowns.
- **Upper deck:** sits on the boom top (355 to 361 mm). Carries the electronics enclosure and the mast standoff; the body canopy sits over it.
- **Drive axle:** x = -160, track 404 mm. Wheelbase (axle to spindle) 440 mm.

Overall: about 700 mm long (body plus bumper), 570 mm wide over the caster towers, 1020 mm tall to the camera head. The caster tires reach 470 mm ahead of the axle when they flip forward in reverse. Estimated mass 17 kg.

3D preview: `docs/render-preview.html`. Illustrated build guide: `docs/guide/index.html` (both published as Claude artifacts).

## Key design decisions
- **Fully printed modular chassis:** four open-top ribbed tray modules (175 x 150 x 90 each, 5 mm walls) bolted together through their shared walls with M5 bolts and located by 6 mm printed dowels. Two lid plates bolt across all four modules and lock the chassis stiff. Rear modules carry the axle housing flange on their outer walls.
- **PETG allowances:** 5 walls or more on load-bearing parts, ribs on every flat panel, and no part relies on a thin unsupported post in the layer direction. PET-CF or ASA can replace PETG later with no CAD change.
- **Drive wheels:** 284 mm printed rim and spoked hub in one piece, with a separate 300 x 80 mm TPU tread that stretches over three retention ribs. The tread profile is low and smooth like a turf tire.
- **Wheel bearings take the load, not the gearbox:** each wheel rides on two 6808 bearings (40 x 52 x 7) on a printed axle housing (40 mm OD) that bolts through the chassis wall to a motor mount bracket inside; the bolt heads are counterbored into the housing flange so they clear the hub. The motor bolts to the bracket's 10 mm standoff; its clamping coupler sits in the housing's 20 mm bore, and an 8 mm REX extension shaft runs through the 12 mm bore to a goBILDA REX hub bolted on the wheel's outer web. The motor only supplies torque. The two motors point at each other on the axle line with 30 mm between their tails.
- **Motors:** 2x goBILDA 5203 Yellow Jacket 71.2:1 with encoders (84 rpm, 93.6 kg.cm stall, 8 mm REX shaft). About 1.3 m/s top speed, capped at 1.0 m/s in software. `docs/drivetrain-sizing.md` checks torque margin at 17 kg on a 15 percent grass slope.
- **Motor controller:** one RoboClaw 2x15A, one channel per wheel.
- **Casters:** printed 258 mm rim with a 280 x 100 mm TPU tire. Wheel on two 608 bearings on an M8 axle bolt. The fork is a yoke with 50 mm trail; a separate 20 mm spindle sleeve (hex boss into the crown) on an M12 x 180 bolt core passes up through the arm pad into the tower, where it runs in two 6004 bearings. A 51104 thrust bearing between the yoke crown and the pad underside carries the weight. Towers sit on the arm pads and bolt down with 4x M6 x 20. The M12 bolt goes into the crown before the wheel, because the tire blocks it afterwards.
- **Power:** 12.8 V 20 Ah LiFePO4 (pack must fit 180 x 150 x 75 mm, lying flat in the chassis just ahead of the axle; about 3 hours of patrol). 5 V 5 A buck for the Pi 5, inline fuse, mushroom E-stop cutting motor power through a relay, printed charging dock with spring contacts.
- **Sensing:** u-blox ZED-F9P RTK GPS (2 cm with NTRIP corrections), BNO085 IMU, Luxonis OAK-D Pro W on the canopy nose (depth, night IR, on-device person/animal detection), a 400 mm mast with a pan-tilt Pi Camera Module 3 and IR illuminator, bumper microswitches, LED light bar and buzzer.
- **Software:** Python asyncio on Raspberry Pi OS 64-bit. No ROS 2 to start; clean module interfaces so ROS 2/Nav2 can be swapped in later. Differential-drive kinematics, pure-pursuit path following with a 0.4 m minimum radius on grass, spin-in-place only on hard surfaces or when stuck.
- **AI split:** OAK-D runs fast local detection to trigger checks. At each checkpoint the Pi sends the photo, the baseline photo, and context to Claude (`claude-sonnet-5-5` for routine checks, `claude-opus-5-5` for the daily summary). Claude returns structured findings through tool use. Alerts go out by ntfy or Telegram with the photo attached. Load the `claude-api` skill during implementation to confirm SDK details.
- **Safety and privacy:** speed cap, GPS geofence, bumper stop, heartbeat watchdog, camera no-look zones.

## Repo layout
```
ClaudeBot/
  PLAN.md
  .venv/                   # CadQuery 2.8 (system CadQuery is broken with NumPy 2)
  cad/
    params.py              # every shared dimension, fits, H2C volume, bearing + fastener sizes
    lib/features.py        # insert holes, clearance holes, nut pockets, bearing seats, tubes, ribs
    parts/                 # one module per subsystem; each exposes parts() -> list of Part
      chassis.py drivetrain.py casters.py boom.py enclosure.py shell.py mast.py rear.py dock.py
    export.py              # writes out/step/*.step, out/stl/*.stl (fine) and docs/guide/models/*.stl (web); checks print volume
    assembly.py            # places all 68 parts, exports out/assembly.step/.stl and assembly.json, reports interferences
    audit.py               # virtual build: insertion sweeps, bolt alignment, driver access; writes docs/assembly-audit.md
    print_guide.py         # writes docs/print-guide.md from the manifest
    out/                   # generated (step/, stl/, manifest.csv, assembly.*)
  electronics/
    BOM.csv                # every purchased part with qty and notes
    wiring.md              # power + signal diagram and pinouts (later phase)
  software/                # later phases (see build phases)
  docs/
    render-preview.html    # interactive 3D preview (concept proportions)
    guide/index.html       # illustrated step-by-step build guide with 3D views of every part (+ models/, assembly.json)
    drivetrain-sizing.md   # torque, speed, traction, runtime
    print-guide.md         # generated: per-part material, orientation, walls, supports, mass
    assembly-audit.md      # generated: results of the virtual build
    field-setup.md         # later phase
```

After any CAD change, run in order: `export.py`, `assembly.py`, `audit.py`, `print_guide.py`. All four must finish clean before printing.

## Printed parts
The authoritative list is `docs/print-guide.md` (generated, 68 designs, 112 pieces, about 22 kg of filament). Summary by subsystem:

| Subsystem | Parts |
|---|---|
| Chassis | 4 tray modules (rear L/R, front L/R), 2 lid plates, battery tray, 16 alignment dowels |
| Drive | 2 axle housings, 2 motor mount brackets, 2 wheels (284 mm rim + hub), 2 bearing spacers, 2 TPU treads |
| Boom | 2 arms (L/R, with tower pads), 4 cross member halves, 2 risers, 2 braces, 2 deck legs, 4 deck quadrants |
| Casters | 2 spindle towers, 2 spindle sleeves, 2 yokes, 2 rims, 2 TPU tires, 2 inner + 4 outer axle spacers |
| Enclosure | tub, lid, TPU gasket |
| Shell | rear, front and 4 side skirt panels, 4 canopy quadrants, 7 canopy splice strips, 2 fenders, bumper carrier, TPU bumper skin, depth camera mount and hood |
| Mast | standoff, base, 2 segments, pan base, tilt bracket, camera housing, camera cover, clear window, GPS mount |
| Rear fittings | E-stop housing, charge port housing, light bar housing, contact pad carrier |
| Dock | 4 tiles, 4 rail halves, contact block, rain cover, AprilTag frame |

## Build order (from the audit)
1. Chassis modules, dowels, seam bolts.
2. Motor brackets (motors already bolted on) and axle housings, **then** the lids, then wheels and treads.
3. Deck legs, battery tray and battery, all six skirt panels (they cannot pass the cross members or wheels later).
4. Rear cross member + risers as a unit, braces, arms, front cross member.
5. Casters: towers, then yoke with the M12 bolt already in, wheel, thrust bearing, up through the pad.
6. Deck quadrants (rear right, rear left, front right, front left), enclosure, mast standoff.
7. Canopy quadrants with splice strips, fenders, bumper, depth camera, rear fittings.
8. Mast, pan-tilt head, GPS.
9. Dock.

## Build phases (each ends with something testable)
1. **CAD and sizing (done):** `params.py`, feature library, every printed part, STEP + STL export with a print-volume check, assembly interference check, virtual build audit, BOM, print guide, drivetrain sizing, illustrated build guide. Next: print bearing-seat test coupons, then the drive wheel and axle housing.
2. **Drive base:** chassis, boom, casters, motors, RoboClaw, battery, E-stop. Bench test, then gamepad drive on the lawn.
3. **Enclosure and body:** sealed electronics box, skirts, canopy, fenders, bumper. Hose test.
4. **Navigation:** GPS + IMU + odometry fusion, record the boundary and route, pure pursuit, obstacle stop, geofence.
5. **Patrol intelligence:** mast and pan-tilt, checkpoint photos, baselines, Claude findings, alerts, daily report.
6. **Autonomy:** dock (GPS approach, AprilTag final alignment), scheduled patrols, night mode.

## Verification
- **CAD:** `.venv/bin/python cad/export.py` builds every part, writes STEP and STL, and fails if any part exceeds the print volume. `cad/assembly.py` writes an assembly STEP and reports any part-to-part interference. `cad/audit.py` assembles the robot in build order and fails if a part cannot reach its position, a bolt hole does not line up through every joined part, or a driver cannot reach a bolt head at that point in the build (current result: 68 of 68 parts, 160 of 160 fasteners clear). Spot-check STEPs in Fusion/Onshape, slice STLs in Bambu Studio.
- **Mechanical:** print bearing seat and insert boss coupons first. Load test the chassis at 20 kg. Casters must self-align at 1 m/s without shimmy.
- **Software:** `pytest software/tests` against mock hardware (later phases).
- **Field:** route tracking within 10 cm at 0.5 m/s, no ruts on the lawn, bumper and geofence stops, a staged open-gate alert with a photo.
