# Nine-day capture analysis (2026-09-28 .. 2026-10-06), analysed 2026-10-11

Source: kitchen-panel Pi recorder. The archive `trane-capture-all.tar` (sha256 da053178…b310b88e) holds daily
archives 09-28 .. 10-06. About 10.8 M records.

**Coverage gaps:**
- 09-28 after 14:35, and all of 09-29 (that day's archive is 347 bytes);
- 09-30 before 09:43;
- **nothing after 2026-10-06 19:22.** The recorder restarted 10-10 16:27 and has logged only its start line since.
  Diagnosis pending.

## 0x3D0: not a room temperature in this house
- Slot 1 (bytes 0–3, upstream "sensor 2") is **0.0 in every frame**.
- f1 (bytes 4–7) stays at **18.7–19.7** for nine days and nights, with no daily cycle. As °C that is 65.6–66.8 °F.
- Against the thermostat's own zone temperatures (`ZoneStatus.n.H`, 10/01–10/02), the zones range 68–74 °F while
  0x3D0 sits about **5 °F below both**:
  - zone 1: r = −0.17, n = 32;
  - zone 2: r = 0.73, but only n = 9.
- It does not track either zone, and its flatness rules out an unconditioned space.

**Verdict:** dewbot6's "wireless remote sensor" decode does not describe this system's frame. A paired sensor would
read a room. Keep **Candidate**; the original "compressor minimum speed" reading is plausible again.

**Decisive check:** does the UX360 list any paired wireless remote sensor? If none is paired, the remote-sensor
reading is ruled out.

## 0x649 JSON transport, 9 days
| day | transfers | lost a segment | malformed | exact-length (no NUL) |
|---|---|---|---|---|
| 09-28 | 984 | 59 | 57 | 1 |
| 09-30 | 182 | 2 | 2 | 0 |
| 10-01 | 520 | 20 | 19 | 0 |
| 10-02 | 2333 | 126 | 120 | 3 |
| 10-03 | 264 | 13 | 14 | 0 |
| 10-04 | 273 | 15 | 13 | 0 |
| 10-05 | 314 | 16 | 15 | 0 |
| 10-06 | 1290 | 71 | 66 | 1 |
| **total** | **6160** | **322 (5.2%)** | **306** | **6** |

- **Exact-length transfers do occur here (6).** CB2.1 appends stale bytes to these.
- The firmware's own `TRANE_JSON` output: 10,294 records, **4,033 empty or unparseable** (double publish plus broken
  transfers).
- **Effect on the zone-2 cooling setpoint**, the value Climate Brain's verified-CAN shadow compares: 30 extractions
  in 9 days, 1 from a malformed transfer, and its value (74) matched the readings either side. **No wrong setpoint
  observed so far.** The risk is real but has not yet shown up as a bad value.
- CB2.2 reassembly is still recommended, but it is not urgent for Climate Brain.

## Recorder outage cause (diagnosed 2026-10-11)
- On 2026-10-06, 18:19–18:58, the board's API connection dropped every 1–2 min. After that it stopped answering at
  10.70.1.94.
- The Pi lost its own network at 19:04 and rebooted at 19:22.
- The board came back by DHCP at **10.70.1.92**. The recorder was pinned to the old IP, so it kept running and
  recorded nothing for 5 days, with no warning.
- Ping to the board is 83–317 ms, which points to weak Wi-Fi. That could also explain some of the disconnects, and
  part of the frame loss in the log stream.
- Fixes:
  - point the recorder at `esphome-trane.local`, which is now the installer default;
  - reserve the address in the router.

## Cross-check with Climate Brain's engineering log (21,355 rows, 2026-09-10 .. 10-11)

**0x3D0 is settled: it is not a temperature.** Matched within 5 min:

| reference | range | r with 0x3D0 | mean 0x3D0 − reference |
|---|---|---|---|
| thermostat room temp | 68–73 °F | −0.42 | −4.6 °F |
| ThirdReality bedroom | 66.7–75.3 | −0.29 | −5.3 |
| ThirdReality upstairs corridor | 67.1–75.0 | −0.20 | −4.6 |
| ThirdReality office | 67.9–75.3 | −0.28 | −5.6 |
| return air | 61.3–76.5 | +0.09 | −3.5 |
| outdoor | 46–86 | −0.24 | +1.0 |

**CAN validation** (Climate Brain's writer request vs UX360 setpoints read from the bus): 2,236 disagreement
samples.
- **207 were garbled CAN values** (heat setpoint "6.0 °F", a truncated 68/69). They occurred only on 09-10 and 09-14,
  zone 1, under the old pre-CB1 firmware. **None since CB1/CB2 (09-28).**
- **1,330** differ only in the mode label (bus heat/cool vs heat_cool) and/or by ≤1 °F: the known Nexia deadband
  normalisation. Benign.
- **~250 since 09-28 are real, sustained differences of about 2 °F.** Examples:
  - zone 2, Climate Brain wrote heat_cool 69/72 while the bus showed heat 67/72, from 10-05 19:20 to 10-06 15:34;
  - zone 2, Climate Brain wrote heat 67 while the bus showed 69/74, on 10-03 20:28–23:48.

  These are not transport errors: the values are plausible and persist for hours. Either the thermostat held a
  different setpoint (a wall/app change or a write that did not stick), or the comparison is stale. Next step: the
  writer log (`climate_brain_writer.csv`) for those windows.
- Since 10-08: only `legacy_can_match` / `not_tested`.

Engineering-log gaps over 1 h: 09-23 23:26 (15.4 h), 09-25 05:26 (11.6 h), 09-26 05:06 (7.3 h).

## CORRECTION, same day: 0x3D0 IS the wireless remote sensor
The household linked the wireless remote thermometer to the SC360 at about 15:00 on 2026-10-11, while the recorder
was running:
- 0x3D0 slot 1 (bytes 4–7) was 19.1 °C at 14:46.
- It **started changing at 14:58:27**, rose steadily to 24.4 °C (75.9 °F) by 15:07 (the sensor warmed in the hand
  during pairing), then fell back: 20.6 °C (69.2 °F) at 15:16 and still dropping.
- Slot 0 stayed 0.0 throughout (no second sensor).

The verdicts above ("not a room temperature", "not a temperature") were **wrong**. They showed only that it was not a
temperature *of the conditioned rooms*. The flat 18.7–19.7 °C for nine days was this sensor, unlinked, reporting from
a steady location. dewbot6's decode is **confirmed** for this house. Lesson: no correlation with the rooms rules out
"room temperature here", not "temperature".

## SECOND CORRECTION (capture 14:43–20:00, analysed 2026-10-12): 0x3D0 is NOT the new wireless sensor
The pairing as the JSON stream recorded it (UX360 technician mode):
- **14:57:42:** technician profiles opened.
- **14:58:25:** Z-Wave bridge put into inclusion (`Bridge Put A=E`).
- **15:02:20:** `EquipmentDetails` reports the new device: `ZSENS930AW00MAA`, "Zwave Sensor", serial 2615R7DDHX,
  firmware 2.02. `SensorInfo` names it "Wireless Sensor 1".
- **15:05:02:** `SensorInfo Put` saves the sensor list:
  - "UX360 Thermostat 01": zone 1, weight 100.0;
  - "Wired Sensor 02" (2615DT020X): zone 2, weight 50.0;
  - wireless 2615R7DDHX, renamed **"Upstairs"**: zone 2, weight 50.0.

  **Zone 2 is now the 50/50 average of the wired and the upstairs sensors.**
- **15:05:26–15:08:28:** technician cooling test (compressor demand up to 89%).
- **19:23–19:25:** a CANopen node reboot and re-commission (NMT, LSS on 0x7E4, "AOC Secondary Bootloader v1.0" on
  0x6F0).

0x3D0 slot 1:
- It began rising at 14:58:27, **before the sensor existed on the system**, and peaked at 24.4 °C at about 15:07.
- It rose again 15:45–16:30, then returned to **exactly its old 19.0 °C baseline** and stayed there all evening.
  Meanwhile zone 2 (50% "Upstairs") read 70–73 °F.
- 0x3E0 f0 follows it, lagged and smoothed.

So it is a real temperature from a fixed, normally steady place, **not** the upstairs sensor. The first correction
("0x3D0 IS the remote sensor") was wrong. The upstairs sensor's own reading does not appear as any new or changed
CAN field. It is visible only through zone 2's averaged temperature (`ZoneStatus.2.H`). Still open: which sensor
0x3D0/0x3E0 is. The likely candidate is a sensor near the equipment, warmed by someone being there and by the test
run.

## Move test (2026-10-11 evening): 0x3D0 is not the Z-Wave sensor
The household moved the Z-Wave "Upstairs" sensor from the kitchen to an upstairs room at about 20:00–20:15.
0x3D0 slot 1 did not react: 19.04–19.11 °C (66.3–66.4 °F) every 10 min from 19:33 to 20:50. Explanation 1 (Z-Wave
sensor relayed by the bridge) is **ruled out**.

Remaining explanation: a fixed sensor at or near the **SC360 remote panel in the kitchen**. It normally reads a few
°F below the room, and it warmed during both oven-on periods (14:58–15:30, 15:45–16:30), when the household was at
the panel. Confirmation test: warm the panel by hand for 2 min at a noted time.
