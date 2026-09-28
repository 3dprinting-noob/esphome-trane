# 2026-09-28 zone damper decode (same capture as first-capture.md)

Question (household): when one zone shuts down, duct static pressure should
rise — which CAN signals show the two modulating zone dampers?

## Result

| Field | Meaning | Confidence | Evidence |
|---|---|---|---|
| 0x250 b0 | Zone 1 damper command, % | Confirmed | = JSON ZoneStatus.1.E at 27/27 updates |
| 0x250 b1 | Zone 2 damper command, % | Confirmed | = JSON ZoneStatus.2.E at 121/121 updates |
| 0x250 b2 | Zone 3 slot command (100) | Raw | constant; no zone 3 |
| 0x250 b3 | Unknown (1) | Raw | constant |
| 0x2C8 b1 | Zone 1 damper position, % | Strong | follows 0x250 b0 at ~1.5 %/s (actuator stroke), lags the command |
| 0x2C8 b3 | Zone 2 damper position, % | Strong | follows 0x250 b1 the same way |
| 0x2C8 b5 | Zone 3 slot position (100) | Raw | constant |

0x2C8 is 7 bytes: `00 Z1 00 Z2 00 Z3 00` (the zero bytes behave as high
bytes of big-endian pairs). 0x251 / 0x252 stayed `64 64 64 00` throughout.
So JSON `ZoneStatus.n.E` is the damper **command**, not only an abstract
airflow allocation; 0x2C8 is the ramped damper position that follows it.

## The static-pressure step

- Heating run: Zone 1 damper 100 % throughout; Zone 2 commanded 64 % → down to
  its 25 % floor by 12:44 as it approached setpoint. Duct resistance stayed
  0.27–0.28 while Zone 2 was ≥ 25 %.
- 12:48:36 Zone 2 HcStatus `1` → `C` (satisfied); 0x250 b1 → 0; 0x2C8 b3 falls to
  0–7 %. Duct resistance steps 0.275 → **0.305–0.317** from 12:48:48 at a steady
  ~1,410 rpm, and static pressure holds ~0.62 inWC on a slower blower.
- 12:48–13:01 Zone 2 then **hunts**: HcStatus flips `1`↔`C` 33 times and its damper
  command 0↔25 32 times in 13 minutes; the position byte only reaches 0–18 %.
- Short cooling start 10:48–10:51 with only Zone 2 open (Z1 command 0, Z2 100):
  resistance 0.33–0.37 — one zone alone is the most restrictive state seen.
- Cooling 10:58–11:45: dampers traded smoothly (Z2 42 → 100 while Z1 100 → 69);
  resistance stayed 0.27–0.28.

Resistance barely moves while one damper stays fully open and the other is at
25 % or more; it rises when the second zone closes below ~10 % or only one
zone is open. That is the expected damper curve (most restriction change near
closed).

## HcStatus codes seen (zone 1 and 2)

`1` idle, `2` cooling, `3` heating, `4` end of cycle, `A` once at 10:55,
`C` zone satisfied during a call. Candidate meanings from sequence only.
