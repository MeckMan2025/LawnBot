# ClaudeBot

A fully 3D-printed outdoor patrol robot: two 300 mm rear drive wheels, two zero-turn-mower-size front casters, a Raspberry Pi 5 brain and Claude for judgement. See `PLAN.md` for the design and `docs/` for the generated guides.

Live build guide: [lawnbot.meckman.org](https://lawnbot.meckman.org)

## Working with the CAD

All CAD is CadQuery (Python). Run everything from the project root with the project virtualenv:

```
.venv/bin/python cad/export.py        # builds all 68 parts -> cad/out/step, cad/out/stl, docs/guide/models
.venv/bin/python cad/assembly.py      # places every part, checks for interferences, writes assembly.step/.json
.venv/bin/python cad/audit.py         # virtual build: insertion sweeps, bolt alignment, driver access
.venv/bin/python cad/print_guide.py   # regenerates docs/print-guide.md
```

Run all four after any change to `cad/params.py` or a part file. Each one exits non-zero if something is wrong.

## Illustrated build guide

`docs/guide/index.html` loads the models with `fetch`, so open it through a local server rather than as a file:

```
cd docs/guide && python3 -m http.server 8000
```

then browse to `http://localhost:8000/`. The published copy on claude.ai needs no server.

## Publishing the site

`site/` is the deployable copy of the guide (the same page wrapped as a standalone HTML document, plus the models). Rebuild it after the models or the guide change, then deploy it as a Cloudflare Worker with static assets:

```
.venv/bin/python scripts/build_site.py
npx wrangler@4 deploy
```

`wrangler.toml` names the Worker `lawnbot` and routes `lawnbot.meckman.org` to it.

## Where things are

| | |
|---|---|
| `cad/params.py` | every dimension, fit and fastener size |
| `cad/parts/*.py` | one module per subsystem |
| `cad/out/step`, `cad/out/stl` | print-ready and CAD-ready part files |
| `electronics/BOM.csv` | everything to buy |
| `docs/print-guide.md` | per-part material, orientation, walls, infill, mass |
| `docs/assembly-audit.md` | results of the virtual build |
| `docs/drivetrain-sizing.md` | torque, speed, traction, runtime |
| `docs/guide/` | the illustrated build guide (artifact form) |
| `site/`, `scripts/build_site.py` | the deployable site and the script that builds it |
