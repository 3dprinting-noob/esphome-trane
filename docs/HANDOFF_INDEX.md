# Handoff index (2026-10-01)

**Newest work in this repo is on branch `claude/github-private-repos-memory-0f6kbf`** (it contains this branch's history plus firmware CB2.2, the duct static
pressure nodes under `hardware/`, and later findings). This branch (`claude/content-review-testing-mxginz`) holds firmware profiles CB1 → CB2 → CB2.1, the
installed-config baseline, the kitchen-Pi capture scripts and `docs/house/TELEMETRY_HOUSE.md`.

Household rules for this repo: the ESPHome device (M5Stack AtomS3R + CAN module, GPIO5/6, 50 kbps, 10.70.1.94) runs `canbus: mode: LISTENONLY` — **never add a
transmit path**; the kitchen Pi also runs the capture service (`tools/pi/pi_trane_capture_install.sh`) and is the same Pi that runs the wall panel and will power the
ReSpeaker voice board + C4002 radar.

Where the rest of the household's work is documented (all private repos, account `3dprinting-noob`):

| Topic | Read | Where |
|---|---|---|
| Kitchen wall panel, 3D-printed frame, whole-home audio, family location, ReSpeaker voice + C4002 radar | `home-automation/docs/handoffs/2026-10-01_MASTER_HANDOFF.md`, `home-automation/docs/PLANS.md`, `home-automation/voice/README.md` | `climate-brain`, branch **`home-automation`** |
| Climate Brain controller (active line, RCs) | `docs/handoffs/LATEST.md` | `climate-brain`, branch **`4.2.9-Claude`** |
| CAN requalification plan, upstream-CAN-watch rule, handoff index | `docs/reviews/CAN_REQUALIFICATION_PLAN_20260928.md`, `docs/handoffs/HANDOFF_INDEX_20261001.md` | `climate-brain`, branch `claude/content-review-testing-mxginz` |
| Sandbox / Arrival Lab | `README.md` | `climate-playground` |
| Listen-only CAN HAT hardware | `CURRENT.md` | `universal-can-bus-hat` |

Cross-project coupling: Climate Brain reads phone presence (occupancy authority); the home-automation line adds location polling and may change person/tracker data —
coordinate before changing either. Never guess Home Assistant entity IDs.
