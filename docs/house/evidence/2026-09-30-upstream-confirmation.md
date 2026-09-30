# 2026-09-30 — upstream findings tested on this house

Sources:
- **Pi capture** `trane-capture-20260930-0935-48h.tar.gz` (sha256 `14bb9f9c…`):
  2026-09-28 10:14–14:35 EDT, 595,486 frames on 101 IDs, 1,105 JSON messages;
  one cooling and one heating run. The recorder then stopped; see Notes.
- **HA packet** `engineering_packet_20260930_092846_48h.tar.gz` (sha256
  `a5c65f02…`): 48 h of HA history.

Tool: `3dprinting-noob/climate-brain`
`tools/hvac_diagnostics/collate_engineering_packet.py`, tests T1–T6.

| Claim | Source | Result here |
|---|---|---|
| 0x3D0 = wireless remote temperature sensors, °C (bytes 4–7 = sensor 1) | dewbot6 | **NOT CONFIRMED.** f1 18.8–19.3 (≈66 °F), rises ~0.4 while the plant runs in cooling and heating, r = +0.80 with compressor rps, −0.86 with zone 1 room; f0 = 0; no sensor serials seen. Temperature-like near the equipment, not a conditioned room |
| IndoorStatus.E is the blower speed request | uncharted9898 | **CONFIRMED.** r = 0.999 with 0x200 u16@2, 19.97 rpm per %; E > 0 before motor feedback at 3/3 starts |
| 0x385 f1 65535 startup sentinel | uncharted9898 | **CONFIRMED** (1 occurrence in 4.4 h) |
| 0x383 f0/f1 suction/high-side pair | uncharted9898 | **CONFIRMED.** Equalises to 0.9 in long idle; running split median 147; suction minimum 111.4. No Err 185.x in window. Gauge vs absolute unresolved |
| Sixth CANopen node = zone panel (node 5) | dewbot6 | **CONFIRMED.** 0x705 heartbeat, TPDOs 0x2C0/0x2C4/0x2C8/0x2CC/0x2D0, LSS scan traffic 0x7E4/0x7E5 |
| House: 0x310 static follows blower rpm² | house map | **CONFIRMED.** R² = 0.984, slope 0.271; resistance median 0.28 (baseline 0.27–0.28) |

## Notes

- **The recorder stopped early.** It ran 10:14–14:35 on 09-28. It was
  reinstalled on 09-29 15:30 with the address typo `10.70.1.94E` and could
  not connect until corrected on 09-30. The installer on the Pi predates the
  typo check in this repo; copy the current `tools/pi/` scripts to the Pi.
- **ESP32 Wi-Fi.** RSSI fell from −58 dBm to −81…−97 dBm at a reconnect on
  09-28 22:51 and stayed there. There were 61 API drops in 48 h but only two
  reboots (the OTA installs).
- **CB2.1 unit bug.** `Compressor Power` carries W but is labelled kW
  (running median 551, max 3,147).
