"""Every shared dimension for LawnBot, in millimetres.

Coordinate frame for the whole robot: X forward, Y left, Z up, Z = 0 at the ground.
Change a number here and every part that depends on it follows.
"""

# ---- Printer -------------------------------------------------------------
# Bambu Lab H2C. Single-nozzle volume is 325 x 320 x 320; dual-nozzle is 300 x 320 x 320.
# We keep a margin so parts never touch the bed edge or the purge area.
BUILD_SINGLE = (318.0, 315.0, 315.0)
BUILD_DUAL = (295.0, 315.0, 315.0)

# ---- Fasteners and fits ----------------------------------------------------
# Heat-set inserts: (hole diameter, hole depth). Sized for common brass inserts in PETG.
INSERT = {"M2.5": (3.4, 4.5), "M3": (4.0, 6.0), "M4": (5.6, 7.0), "M5": (6.4, 9.0), "M6": (8.0, 11.0)}
# Clearance holes for bolts.
CLEAR = {"M2.5": 2.8, "M3": 3.4, "M4": 4.5, "M5": 5.5, "M6": 6.6, "M8": 8.6, "M12": 12.6}
# Hex nut across-flats, plus a pocket allowance.
NUT_AF = {"M3": 5.5, "M4": 7.0, "M5": 8.0, "M6": 10.0, "M8": 13.0, "M12": 19.0}
NUT_T = {"M3": 2.4, "M4": 3.2, "M5": 4.7, "M6": 5.2, "M8": 6.8, "M12": 10.8}
NUT_FIT = 0.4
# Bolt head (socket cap) diameter for counterbores.
HEAD_D = {"M3": 5.5, "M4": 7.0, "M5": 8.5, "M6": 10.0, "M8": 13.0, "M12": 18.0}

# Ball bearings: (bore, OD, width).
BEARING = {
    "6808": (40.0, 52.0, 7.0),   # drive wheel hub, two per wheel
    "6004": (20.0, 42.0, 12.0),  # caster spindle, two per tower
    "51104": (20.0, 35.0, 10.0), # caster thrust bearing, one per caster
    "608": (8.0, 22.0, 7.0),     # caster wheel axle, two per wheel
}
BEARING_SEAT_FIT = 0.25   # added to OD for a press fit in PETG after a light ream
SHAFT_FIT = -0.15         # printed shaft that a bearing bore slides onto
DOWEL_D = 6.0
DOWEL_FIT = 0.3

# ---- Motor: goBILDA 5203 Yellow Jacket, 71.2:1 ------------------------------
MOTOR_FACE_D = 37.0        # gearbox OD plus clearance
MOTOR_PATTERN = 16.0       # 4x M4 on a 16 mm square
MOTOR_SHAFT_D = 8.0        # 8 mm REX
MOTOR_BOSS_D = 13.0        # pilot boss on the gearbox face
MOTOR_LENGTH = 120.0       # motor plus gearbox, for clearance checks

# ---- Low chassis -------------------------------------------------------------
CH_REAR = -280.0
CH_FRONT = 70.0
CH_W = 300.0
CH_H = 90.0
CH_BOTTOM = 90.0           # ground clearance
CH_WALL = 5.0
CH_FLOOR = 5.0
CH_L = CH_FRONT - CH_REAR  # 350
CH_CX = (CH_FRONT + CH_REAR) / 2.0
CH_TOP = CH_BOTTOM + CH_H  # 180
MOD_L = CH_L / 2.0         # 175, one module
MOD_W = CH_W / 2.0         # 150
LID_T = 6.0
CH_LID_TOP = CH_TOP + LID_T

BATTERY = (180.0, 150.0, 75.0)   # max pack envelope, lying flat on the chassis lid under the deck
BATTERY_X = -100.0               # centre; tray spans -196..-4, between the deck legs and the riser feet
BATTERY_FEET = [(-140.0, 83.0), (-140.0, -83.0), (-60.0, 83.0), (-60.0, -83.0)]   # tray tabs, outside the battery, inside the brace feet

# ---- Drive wheels ----------------------------------------------------------------
WHEEL_D = 300.0
WHEEL_W = 80.0
TRACK = 404.0                    # leaves 2 mm between the housing flange and the wheel hub
AXLE_X = -160.0                  # motor mount plate must clear the module corner boss at x = -119
AXLE_Z = WHEEL_D / 2.0           # 150
RIM_D = 284.0                    # printed rim OD
TREAD_T = (WHEEL_D - RIM_D) / 2  # 8 mm of TPU
HUB_OD = 68.0
AXLE_HOUSING_OD = BEARING["6808"][0]          # 40 (bearing bore)
AXLE_HOUSING_BORE = 12.0         # only the 8 mm REX extension shaft passes through
AXLE_FLANGE = (70.0, 60.0)       # x by z, must stay inside the 90 mm wall and clear the corner boss
AXLE_FLANGE_T = 10.0             # bolt heads counterbored into it from the outside, so nothing touches the hub
AXLE_FLANGE_PATTERN = (50.0, 36.0)   # 4x M5, shared with the motor mount bracket inside
WHEEL_INNER_Y = TRACK / 2 - WHEEL_W / 2       # 160
AXLE_HOUSING_LEN = 85.0          # flange plus tube, from the chassis wall outward; stops short of the hub web
WHEEL_WEB_T = 6.0                # outer web of the wheel hub that carries the REX hub
MOTOR_MOUNT_STANDOFF = 10.0      # motor face sits this far inboard of the wall; the coupler lives in the housing bore
AXLE_HOUSING_COUPLER_BORE = 20.0 # wider bore for the first 30 mm so the clamping coupler (max 18 mm OD) fits
AXLE_HOUSING_COUPLER_LEN = 30.0
SEAM_WALL = 8.0                  # module walls that mate with another module
REX_HUB_PATTERN = 16.0           # goBILDA hub: 4x M4 on 16 mm square
REX_HUB_CLEAR_D = 24.0

# ---- Front casters (11x4.00-5 mower size) -----------------------------------------
CASTER_X = 280.0
CASTER_Y = 205.0
CASTER_TIRE_D = 280.0
CASTER_W = 100.0
CASTER_RIM_D = 258.0
CASTER_TRAIL = 50.0
CASTER_AXLE = "M8"
FORK_LEG_T = 14.0
FORK_LEG_GAP = 10.0              # each side between tire and leg
SPINDLE_OD = BEARING["6004"][0]  # 20
TOWER_OD = 64.0
TOWER_H = 110.0
TOWER_FLANGE = 100.0
TOWER_FLANGE_T = 8.0
TOWER_PATTERN = 64.0             # 4x M6 into the arm pad
CROWN_T = 14.0
CROWN_TOP = 305.0                # thrust bearing sits on this
BOOM_Z = CROWN_TOP + BEARING["51104"][2]      # 315, boom underside
SPINDLE_HOLE = 22.0              # through the arm pad

# ---- Boom and upper deck -------------------------------------------------------------
BOOM_SEC = 40.0
BOOM_WALL = 4.0
BOOM_ARM_X0 = 10.0
BOOM_ARM_X1 = 320.0              # 310 long, fits the bed
BOOM_TOP = BOOM_Z + BOOM_SEC     # 355
TOWER_Z0 = BOOM_TOP              # tower sits on the arm pad; spindle passes through the pad
PAD_L = 100.0                    # tower pad at the front of each arm
PAD_W = 100.0
PAD_Y_IN = 155.0                 # pad inner face (global |y|)
CROSS_FRONT_X = CASTER_X         # 280
CROSS_REAR_X = 30.0
CROSS_REAR_HALF_L = 180.0        # center splice to the arm inner face
CROSS_FRONT_HALF_L = 155.0       # center splice to the arm pad inner face
CROSS_INSERTS = {"front": (60.0, 120.0), "rear": (60.0, 150.0)}   # deck bolt inserts, from the center (rear clears the riser bosses)
CROSS_TAB_L = 60.0               # lap splice tab, centred on the member centre
RISER_X = 30.0
RISER_Y = 105.0
RISER_SEC = (40.0, 40.0)
RISER_PATTERN = (52.0, 52.0)     # foot bolts sit outside the column so a driver reaches them; flange is pattern + 12
RISER_TOP_DX = 12.0              # the two top bolts, along x, inside the column
RISER_H = BOOM_Z - CH_LID_TOP    # 129
BRACE_X = -70.0                  # brace foot on the lid
LEG_X = CH_REAR + 50.0           # -230
LEG_Y = 105.0
LEG_SEC = (40.0, 30.0)
LEG_PATTERN = (52.0, 42.0)       # outside the column; flange is pattern + 12
LEG_TOP_DX = 12.0
DECK_T = 6.0
DECK_X0 = CH_REAR + 10.0         # -270
DECK_X1 = 300.0                  # over the front cross member
DECK_W = 290.0
DECK_Z0 = BOOM_TOP               # 355, deck plate sits on the boom
DECK_TOP = DECK_Z0 + DECK_T      # 361
DECK_CORNER_R = 40.0
DECK_RIB = 18.0
DECK_GRID = 40.0                 # M4 insert grid on the deck
DECK_GRID_X0 = -230.0
DECK_GRID_Y0 = 20.0

# ---- Enclosure ----------------------------------------------------------------------
ENC_L, ENC_W, ENC_H = 250.0, 190.0, 80.0
ENC_X = 10.0                     # feet land on the deck grid at x = -110, 130 and y = +/-100
ENC_FEET = (240.0, 200.0)
ENC_WALL = 4.0
ENC_LID_T = 8.0
GASKET_W, GASKET_T = 4.0, 2.0
GLAND_D = 15.5                   # PG9

# ---- Shell ----------------------------------------------------------------------
SKIRT_T = 3.0
SKIRT_Z0 = CH_LID_TOP            # 186
SKIRT_Z1 = BOOM_Z - 2.0          # 313, stays under the cross members
CANOPY_X0 = CH_REAR - 5.0        # -285
CANOPY_X1 = CASTER_X + 55.0      # 335
CANOPY_W = 307.0                 # sits just outside the skirts (150) and inside the arm pads (155)
CANOPY_Z0 = 290.0                # overlaps the skirt tops by 23 mm
CANOPY_Z1 = 460.0
CANOPY_WALL = 3.0
CANOPY_R = 10.0                  # plan-view corner radius; must stay outside the square skirt corners
CANOPY_FRONT_CUT_X = 165.0       # ahead of here the canopy bottom band is removed for the caster crown sweep
CANOPY_FRONT_CUT_Z = 320.0
FENDER_R = 168.0
FENDER_FLANGE_ANGLES = (70.0, 90.0, 110.0)   # bolt points, keep them above the canopy bottom edge
FENDER_W = WHEEL_W + 24.0
BUMPER_W = 300.0
BUMPER_Z = CANOPY_Z0 + 45.0
OAK_TILT_DEG = 10.0

# ---- Mast and head ----------------------------------------------------------------
MAST_X = -190.0
MAST_OD = 40.0
MAST_WALL = 4.0
MAST_SEG_L = 200.0
MAST_SEGMENTS = 2
SERVO = (40.5, 20.5, 40.0)       # standard-size servo body, with clearance
CAM_BOARD = (25.5, 24.5)         # Pi Camera Module 3
GPS_PUCK_D = 61.0                # u-blox ANN-MB class puck
ESTOP_Y = 95.0                   # E-stop (+y) and charge port (-y) on the canopy roof, rear

# ---- Dock ----------------------------------------------------------------------
DOCK_TILE = (255.0, 290.0, 14.0)  # 275 x 310 with the lap tabs
DOCK_RAIL_L = 220.0
