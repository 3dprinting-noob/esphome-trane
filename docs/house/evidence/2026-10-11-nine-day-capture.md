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
