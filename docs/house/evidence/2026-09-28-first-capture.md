# 2026-09-28 first household capture (cooling + heating)

Source: `trane-capture-20260928-1309-8h.tar.gz`, sha256
`e403ec1d9b31b3f733fec0f19e011cdfcf2bad8928010ed6d01a3e0bfae8f426`.
Kitchen Pi collector, firmware CB1, 10:14:29–13:09 EDT (2 h 55 min, one
continuous connection). 410,887 records: ~409,000 CAN frames on 101 standard
IDs (~37 frames/s) and 1,694 JSON messages (971 parsed; the rest empty or
truncated reassemblies). Outdoor 61–68 °F.

Scripts: `tools/analysis/` (`load_cap.py <dir>` first; `phases.py`,
`phases16.py` and `lead.py` have this capture's phase windows hard-coded).

## Timeline (from the capture)

| Time (EDT) | State | Compressor | Notes |
|---|---|---|---|
| 10:14–10:47 | Idle | 0 | Pressures equalised 184.7 / 186.6 |
| 10:48–10:51 | Cooling start, stopped after ~3 min | 45 → 22 rps | Short cycle |
| 10:58–11:45 | Cooling | ~26 rps at demand 99–100 % | Supply ~51 °F, return 68–70 °F; ~630 W input |
| 11:46–11:57 | Idle | 0 | Pressures re-equalise in ~8 min |
| 11:58–13:01 | Heating | 45 → 57 → 46 rps | Supply 105–109 °F; up to 3.6 kW input; blower to 1810 rpm |
| 13:02–13:09 | Idle | 0 | Discharge temperature decays |

No furnace, defrost, stator-heat or fan-only operation in this window.

## Method and results

1. **Known-value correlation (JSON → binary):**
   - ZoneStatus.1.H vs 0x490 f0: 8/8 matched within 3 s → room temperature confirmed.
   - OdStatus CompDemandPercent vs 0x281 b6: 46/67 exact, remainder within 4 during ramps → demand mirror confirmed.
   - IndoorStatus.E blower % vs 0x200 u16@2: constant ratio 19.8–20.2 rpm per % → blower request.
   - SystemOpStatus.E ("59.00"–"62.00") = 0x490 b4 at every sample; did not follow the
     outdoor rise to 68 °F after 13:02 → indoor humidity, not outdoor temperature or a
     speed ceiling.
2. **Lead/lag at the two starts and two stops (`lead.py`):** compressor request
   (0x280) → demand/mode (0x281 b6/b7) → blower request (0x200) → input power (0x38C)
   → actual compressor speed (0x384) / blower rpm (0x318) → blower power (0x320) →
   outdoor fan actual (0x384 u16@6). Outdoor fan request (0x281 u16@0) leads its actual
   by 9–15 s. Stops run in the reverse order; actual compressor speed takes ~50 s to
   reach 0 after the heating request drops.
3. **Physics checks:**
   - 0x383 f0/f1 equal within 2 psi at idle; split to 134/207 (cool) and 150/391 (heat);
     re-converge after each stop → low/high pressure pair.
   - Input power = line voltage × input current within 3 %.
   - Blower power ratio heat/cool 3.7 vs cube of speed ratio 3.8; static pressure ratio
     2.14 vs square 2.11 → blower power and duct static pressure behave per fan laws.
   - Outdoor coil (0x381 f0) 10 °F below ambient in heating, ~1 °F above in cooling.
4. **Constants:** 0x387 f0 = 55, 0x386 = 2 / 50, 0x3D0 f1 ≈ 19, 0x491–0x495 = 70.

## Firmware issues found

- CB1 "Compressor Power" accepted only < 20 (kW, per uncharted); this system reports W
  (560 / 3000) → the entity stayed 0 while running.
- Decimal SystemOpStatus.E is published as "SC360 Outdoor Temp" — it is humidity.
- "Indoor Humidity" gets no value (its integer branch never occurs on this bus).
- JSON-only entities (room temperature, demand, blower %) go Unknown after a restart
  until a JSON update arrives; binary sources above are continuous.
