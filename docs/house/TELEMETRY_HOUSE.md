# Household Trane CAN signal map

System: two-zone Trane/Nexia communicating dual-fuel plant, UX360 + SC360,
M5Stack AtomS3R listen-only tap (firmware CB1). Built with uncharted9898's
method (long capture, known-value correlation, request→actual lead/lag,
physics checks). Evidence: `evidence/2026-09-28-first-capture.md`.

Confidence: **Confirmed** = matched to an independent reference on this
system; **Strong** = consistent physics + ordering, OEM label unverified;
**Candidate** = plausible; **Raw** = no meaning assigned.
Where this differs from uncharted9898 `docs/TELEMETRY.md` (different
equipment), the difference is called out.

## Compressor / outdoor unit

| Field | Meaning | Confidence | Evidence (2026-09-28) |
|---|---|---|---|
| 0x280 f0 | Compressor speed request, rps | Confirmed | Leads 0x384 f0 at every start (0–11 s) and stop; cooling ~26, heating 45–57 |
| 0x384 f0 | Compressor speed actual, rps | Confirmed | Follows 0x280; ramps down ~50 s after heat request drops |
| 0x281 b6 | Compressor demand % (mirror of OdStatus CompDemandPercent) | Confirmed | 46/67 JSON updates exact within 2.5 s, rest off by 1–4 during ramps |
| OdStatus.B (JSON) | Demand-type %, **not Hz** (entity "Compressor Frequency") | Strong | 99 at 26 rps (cool) and at 57 rps (heat) |
| 0x281 b7 | Operating mode: 0 idle, 1 cooling, 2 heating | Strong | Constant per phase. **uncharted reads it as blower-active flag** |
| 0x385 f0 | Compressor power, **W** | Strong | ~560 W cool / ~3000 W heat, always below 0x38C f1 input power. **uncharted used kW**; CB1 filter (<20) drops every running value — fixed in CB2 |
| 0x385 f1 | Unknown | Raw | 0 idle, ~24 cool, ~160 heat — not a speed ceiling here |
| 0x38C f1 | Outdoor input power, W | Confirmed | 17–22 W standby, ~630 W cool, ~3340 W heat; = V × I (0x38F f0 × 0x389 f1) within 3 % |
| 0x389 f1 | Outdoor input current, A | Confirmed | 2.7 A cool / 13.9 A heat, consistent with power/voltage |
| 0x38F f0 | Line voltage, V (entity "Refrigerant Pressure") | Confirmed | 234–243 V, sags ~2 V under 3.3 kW |
| 0x38F f1 | Compressor current family, A | Candidate | 3.4 cool / 8.7 heat |
| 0x388 f0, f1, 0x389 f0 | Compressor phase currents, A | Strong | Identical triplet: 3.3 A cool, 8.4 A heat, 0 idle |
| 0x387 f0 | Constant 55 (entity "Refrig Circuit Temp") | Confirmed constant | 55.0 in every phase |
| 0x387 f1 | Outdoor fan current, A | Candidate | 0.2 cool / 0.9 heat |
| 0x384 u16@4 | Drive DC bus voltage, V | Strong | 322–354 V, rises when running |
| 0x281 u16@0 | Outdoor fan speed **request**, rpm | Strong | Equals 0x384 u16@6 in steady state (365/360 cool, 766/762 heat) and leads it by 9–15 s. **uncharted reads it as airflow target** |
| 0x384 u16@6 | Outdoor fan speed actual, rpm | Strong | Follows 0x281 u16@0 |
| 0x383 f0 | Suction (low-side) pressure, absolute | Strong | 185 idle equalised with f1; ~134 cool, ~150 heat; re-equalises within ~8 min after stop. Entity "Discharge Temp" |
| 0x383 f1 | Liquid / high-side pressure, absolute | Strong | ~207 cool, ~391 heat (indoor coil condensing in heat; supply air 105 °F fits) |
| 0x381 f0 | Outdoor coil temperature, °F (entity "Suction Temp") | Strong | ≈ ambient idle, 1 °F above in cooling, 10 °F below in heating (outdoor coil is the evaporator) |
| 0x381 f1 | Compressor discharge temperature, °F | Strong | 94–118 cool (low speed), 167–179 heat, slow decay after stop |
| 0x382 f0 | Suction line temperature, °F | Strong | Consistent superheat vs. saturation from 0x383 f0 |
| 0x382 f1 | Liquid line temperature, °F | Strong | ~87 °F in heating ≈ indoor liquid 0x283 f1 (83.5 °F) |
| 0x380 f1 | Outdoor air temperature, °F | Confirmed | Matches ambient; f0 always −99 (unavailable) |
| 0x386 | f0 = 2, f1 = 50 constants (entity "Refrig Sensor B" = f1) | Confirmed constant | |
| 0x282 b1 | Stator heat active | Candidate | 0 throughout (no stator-heat cycle in 3 h at 61–68 °F) |
| 0x3D0 f1 | Compressor minimum speed, rps | Strong | 18.8–19.3 constant |
| 0x410 f0/f1, 0x430 f0, 0x460 f0 | Outdoor electronics temperatures? | Candidate | 76–93 °F, nearly flat even at 3.3 kW — **not** the drive IPM trend uncharted saw |
| 0x430 f1, 0x450 f0/f1 | Unknown | Raw | Noisy 237–362 in every phase |

## Indoor / blower

| Field | Meaning | Confidence | Evidence |
|---|---|---|---|
| 0x200 u16@2 | Blower speed request, rpm | Strong | ≈ 19.9 × IndoorStatus.E % (e.g. 89 % → 1771); leads 0x318 by ~6 s |
| 0x318 u16@4 | Blower motor speed actual, rpm | Strong | Follows request; 1100–1160 cool, 1300–1810 heat |
| IndoorStatus.E (JSON) | Blower % (numeric) or startup token `TA_INV_HI` | Confirmed | Token at start of run, numeric after |
| 0x320 f0 | Blower power, W | Strong | ~180 W at 1150 rpm, ~665 W at 1800 rpm: ratio 3.7 vs fan-law 3.8 |
| 0x310 f0 | Duct static pressure, inWC | Strong | median 0.35 cool, 0.75 heat (0.5–0.9); ratio 2.14 vs fan-law (rpm²) 2.11 on median blower speed. Higher than both community systems (0.09–0.19) |
| 0x308 f0 / f1 | Return / supply air, °F | Confirmed | ΔT ~18 °F cool, ~30 °F heat |
| 0x283 f1 | Indoor coil refrigerant temperature, **°C** | Candidate | 5.6 °C (42 °F) cool ≈ saturation from suction pressure; 28.6 °C heat |
| 0x283 f0 | Indoor gas-line temperature? °C | Raw | 18 °C cool (≈ 0x382 f0), but 7.8 °C in heat and −4.6 °C idle — unexplained. Entity "AHU Inlet Air Temp" is not air |
| 0x300 | — | Absent | uncharted's indoor gas/liquid temperatures are not on this bus (different indoor unit) |

## Zone / thermostat

| Field | Meaning | Confidence | Evidence |
|---|---|---|---|
| 0x490 f0 | Zone 1 room temperature, °F | Confirmed | All 8 ZoneStatus.1.H updates matched within 3 s |
| 0x490 b4 | Indoor humidity, % | Strong | Equals SystemOpStatus.E; stayed 60–61 while outdoor rose 62 → 68 °F |
| SystemOpStatus.E (JSON) | Indoor humidity, %, decimal formatted ("61.00") | Strong | As above. **CB1 routes decimal E to "SC360 Outdoor Temp" — that entity is humidity.** uncharted's "speed ceiling" reading does not apply here |
| 0x491–0x495 f0 | Zone 2–6 temperature slots | Raw | Constant 70.0 for 3 h (placeholders?) |
| 0x4B2 f0/f1 | Unknown pair | Raw | Constant 70 / 70 |

## Zone dampers (`evidence/2026-09-28-zone-dampers.md`)

| Field | Meaning | Confidence | Evidence |
|---|---|---|---|
| 0x250 b0 / b1 | Zone 1 / Zone 2 damper command, % | Confirmed | = JSON ZoneStatus.n.E at 27/27 and 121/121 updates |
| 0x2C8 b1 / b3 | Zone 1 / Zone 2 damper position, % | Strong | ramps after the command at ~1.5 %/s |
| 0x250 b2, 0x2C8 b5 | Zone 3 slot (100) | Raw | no third zone |
| ZoneStatus.n.HcStatus (JSON) | 1 idle, 2 cool, 3 heat, 4 end, C satisfied | Candidate | sequence only |

Zone 2 closing below ~10 % (satisfied) raised duct resistance 0.275 → 0.31.

## Bus / network

- 101 standard IDs, ~37 frames/s. CANopen heartbeats 0x701–0x706: **six nodes**
  (uncharted documents 0x701–0x705); the extra node is unidentified — possibly
  the gas furnace side of the dual-fuel plant.
- JSON via SDO pairs 0x601/0x581, 0x621/0x5A1, 0x641/0x5C1, 0x649/0x5C9, as
  uncharted documents.

## Not yet covered

Furnace (dual-fuel) operation, defrost, stator heat, fan-only circulation,
Zone 2 calls. Capture below ~35 °F outdoor for the furnace side.
