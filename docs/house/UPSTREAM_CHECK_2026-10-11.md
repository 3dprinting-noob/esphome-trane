# Upstream check — dewbot6/esphome-trane, 2026-10-11

The household firmware (CB2.1) still pins dewbot6's `trane_hvac` component at **v0.1.0** (2026-06-05), for the
display-only "Trane Climate" card. Upstream has moved on since then:

| Upstream change | Household firmware | Action |
|---|---|---|
| v0.2.0 (09-16): climate entity moved to `platform: template`; the custom `trane_hvac` C++ component was removed | Still fetches `trane_hvac` at v0.1.0. The tag still exists, so the build still works, but it will get no fixes. | Optional: drop the external component and copy upstream's template climate (display only, no transmit). |
| v0.2.0 (09-17): SystemOpStatus.E is always indoor humidity | Already fixed in CB2 (E → humidity, not SC360 Outdoor Temp). | None. |
| v0.3.0 (09-18): 0x283 "AHU Inlet Air Temp" and "Indoor Coil Temp" are refrigerant temperatures (indoor liquid line, indoor coil refrigerant), not air | CB2 keeps the old names so entity IDs stay stable; the header notes f1 is coil refrigerant. Climate Brain does not read either. | Add HA `customize` friendly names, like the other renamed Trane sensors. No control impact. |
| v0.4.0 (09-18): duct static pressure from 0x310 | Already decoded. | None. |
| 09-29: **0x3D0 = wireless remote temperature sensors**, float °C; bytes 4–7 = sensor 1, bytes 0–3 = sensor 2; 0 = unpaired | **Conflicts with our notes.** `TELEMETRY_HOUSE.md` lists 0x3D0 f1 as "compressor minimum speed, rps, Strong", seen at 18.8–19.3 over 3 h. 19 °C = 66 °F, a plausible room temperature, and a value that drifts 0.5 is odd for a fixed speed limit. | **Downgrade our label to Candidate.** Settle it with multi-day data: a room temperature follows the house through the day; a speed limit stays put. f0 reading 0 would mean only one remote sensor is paired. |
| 09-29: `zone-panel-re/` Trane Link zone panel is a CANopen node. Its COB-IDs are `base + node_id`, assigned by the SC360 at commissioning (LSS). 0x2C8 is the panel's fastest per-zone status PDO. | Supports our 0x2C8 damper-position decode (CB2.1). | **Caveat:** the 0x2C0–0x2D0 IDs belong to whichever panel the SC360 assigned first. Re-commissioning or adding a panel can move them. Re-verify the damper decode after any zone-panel service. |

None of these changes affect Climate Brain's control path. Climate Brain only reads Trane CAN sensors as shadow or
diagnostic inputs, and CAN never writes (constitution CB-CAN rules).

## uncharted9898/esphome-trane `dev` (40 commits, 2026-10-07..11) and the house capture

Full review: climate-brain `4.2.9-Claude:docs/reviews/UPSTREAM_CAN_REVIEW_20261011.md`. For this firmware:

- **0x281 b7**: uncharted's "blower active" reading is now disproved: in a fan-only test the blower ran while b7 stayed
  0. That supports our reading (operating mode 0 idle / 1 cool / 2 heat).
- **SystemOpStatus.E = indoor humidity** is now Confirmed upstream, matching CB2.
- **0x649 JSON reassembly (CB2.1) has three defects**, measured on the 2026-09-28 capture (3 h, 736 transfers):
  1. a frame lost by the listener corrupts the message, and the fields are still extracted from it. 49 transfers
     (6.7%) lost a segment and 47 were malformed;
  2. the final-segment byte count is taken from the segment *number* (`(seq & 0x7F) - 1`) and relies on a trailing
     NUL. An exact-length message (uncharted saw these) would get stale bytes appended. None occurred in this
     capture;
  3. the end-block frame (`0xD5`) also matches the "final segment" test, so every message is published twice
     (1,694 trace records for 736 transfers, 723 of them empty).

  Proposed **CB2.2**:
  - take the size from the initiate frame;
  - track the expected sequence and drop the whole transfer on a gap;
  - trim the last segment by the end-block's unused-byte count;
  - publish once, on the end-block.

  Still LISTENONLY.
