# Firmware profile CB1 — listen-only recorder (household AtomS3R)

`esphome-trane.cb1.yaml` replaces `installed/esphome-trane.atoms3r.yaml` on the
household device. Same device name (`esphome-trane`), same board, display and
CAN pins.

## What changed from the installed baseline

| Area | Change |
|---|---|
| Transmit | `mode: LISTENONLY` kept. Transmit script, `set_temperature` / `set_mode` API actions and the climate card's set actions removed |
| Trane Climate card | Kept as **display only** (`climate.trane_thermostat_ux360_trane_climate`, on a dashboard). Uses dewbot6's `trane_hvac` component fetched from GitHub at `v0.1.0` (Device Builder has no local copy). Changes made on the card do nothing and are overwritten by the bus within ~5 s |
| Entity IDs | Every existing sensor keeps its name, so `sensor.trane_*` IDs and Climate Brain bindings are unchanged |
| Stale values | `Compressor Frequency` and `Indoor Blower Speed` now publish 0 (they previously froze at the last running value). `Supply Air Fault` clears to `none` once numeric IndoorStatus resumes (`TA_INV_HI` is a normal startup token) |
| Raw capture | Every frame logged as `TRANE_CAN_LIVE,S,<ms>,<id>,<dlc>,<hex>`; JSON as `TRANE_JSON,<id>,<json>` — the format `tools/pi/pi_trane_capture_install.sh` records |
| New sensors | Candidates from uncharted9898 `docs/TELEMETRY.md` (see below), plus `System Op Status E` (raw, disputed field) and `CAN Frames Received` |
| Security | OTA password (`ota_password`) and web page login `admin` / `web_password` |

**Behaviour change for Climate Brain:** blower and compressor-frequency values
now return to 0 when idle. Health baselines and the `OPEN-CAN-004` "35 % resting
floor" were learned from the frozen values; re-check them after this flash.

## Validation

`esphome config` (ESPHome 2026.6.5, same as the installed build) reports the
configuration valid. A full compile could not run in the authoring sandbox
(PlatformIO registry blocked by its network policy), so the first real compile
is the Device Builder install; a compile error there stops before any upload.

## Candidate sensors (unverified on this system)

Mapped from a different Trane system (5TWV0X24 + 5TAMX air handler). The outdoor
IDs match this house's data so far; indoor IDs may not exist here (a sensor
that stays `unknown` means the frame is not on this bus).

| Entity | Source |
|---|---|
| Compressor Speed Request / Actual (rps) | 0x280 f0 / 0x384 f0 |
| Compressor Power (kW) | 0x385 f0 |
| Outdoor Input Power (W) / Input Current (A) | 0x38C f1 / 0x389 f1 |
| Line Voltage (V) | 0x38F f0 (also still feeds "Refrigerant Pressure") |
| Drive DC Voltage / Outdoor Fan Speed | 0x384 u16@4 / u16@6 |
| Suction / Liquid Pressure Abs | 0x383 f0 / f1 (f0 also still feeds "Discharge Temp") |
| Compressor Discharge Temp | 0x381 f1 |
| Suction / Liquid Line Temp | 0x382 f0 / f1 |
| Duct Static Pressure (inH₂O) | 0x310 f0 |
| Blower Power (W) / Motor Speed (rpm) | 0x320 f0 / 0x318 u16@4 |
| Stator Heat Active | 0x282 byte1 |

## Install (Home Assistant → ESPHome Device Builder)

1. **Secrets** (top right in Device Builder): keep `wifi_ssid` / `wifi_password`
   and add

   ```yaml
   ota_password: "<long random string>"
   web_password: "<another one>"
   ```

2. **+ New device → Continue → skip** (or open the existing `esphome-trane`
   card if Device Builder already shows one) so there is a config named
   `esphome-trane.yaml`; **Edit**, select all, paste `esphome-trane.cb1.yaml`,
   **Save**.
3. **Install → Wirelessly.** The first compile downloads the ESP32 toolchain
   and takes several minutes. The current firmware has no OTA password, so this
   upload is accepted; later uploads use `ota_password`.
   If Device Builder cannot find the device by name, add under `wifi:`
   `use_address: 10.70.1.94` and install again.
4. Check: the screen shows `LISTEN ONLY CB1`; in Home Assistant the Trane
   sensors keep updating; `Compressor Frequency` / `Indoor Blower Speed` read 0
   when the system is idle; the ESPHome device page shows `CAN Frames Received`
   rising.

**Undo:** paste `installed/esphome-trane.atoms3r.yaml` back, changing its
`type: local` component source to the same GitHub `v0.1.0` source used here,
or flash the previous build from your Mac/PC.

## Raw capture on the kitchen Pi

After the flash, copy the two scripts from `tools/pi/` to the Pi (the repo is
private, so the Pi cannot download them itself). From the Mac, in the folder
holding them:

```bash
scp pi_trane_capture_install.sh pi_trane_capture_pack.sh kitchen-panel-pi@10.70.1.88:~/
```

Then on the Pi (`kitchen-panel-pi@kitchen-panel`):

```bash
bash pi_trane_capture_install.sh 10.70.1.94 '<api encryption key>'
```

(Leave the key out if API encryption is off.)

Then after a heating/cooling cycle:

```bash
bash pi_trane_capture_pack.sh 6     # last 6 hours
```

## Install log

- 2026-09-28 09:56 -04:00 — CB1 compiled in Home Assistant ESPHome Device Builder
  (ESPHome 2026.9.0, board ESP32-S3 DevKitC-1) and uploaded over the air to
  10.70.1.94: "OTA successful". Flash 74.1 % (1,360,639 of 1,835,008 bytes),
  RAM 43.0 %. Post-install checks pending.
