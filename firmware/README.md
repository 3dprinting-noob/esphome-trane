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
- 2026-09-28 10:14 -04:00 — Kitchen Pi recorder running (`trane-capture.service`,
  no API key): 1,106 CAN frames + 4 JSON messages in the first 30 s
  (~37 frames/s, ~10 KB/s of JSONL before daily compression). Pi has 23 GB free.
- Reported 2026-09-30 by the household: the device now runs **CB2.1**
  (`esphome-trane.cb2.yaml`, version `cb2.1-listen-2026.09.28`, LISTENONLY),
  installed from the Home Assistant ESPHome Device Builder app. The config is
  named `esphome-trane.yaml` in Device Builder. Install time and compile stats
  were not recorded. Whether the Device Builder copy is byte-identical to
  `esphome-trane.cb2.yaml` has not been checked; secrets and `use_address`
  may differ.

## Profile CB2 (2026-09-28)

`esphome-trane.cb2.yaml` = CB1 plus the fixes from the first household capture
(`docs/house/TELEMETRY_HOUSE.md`): room temperature, compressor demand and
indoor humidity from continuous binary frames; SystemOpStatus.E treated as
humidity ("SC360 Outdoor Temp" no longer updates); Compressor Power in W; new
Operating Mode, Outdoor Fan Speed Request, Blower Speed Request and Compressor
Phase Current. CB2.1 adds Zone 1/2 Damper Command (0x250) and Position (0x2C8). Same install path as CB1 (paste, Save, Install → Wirelessly;
OTA now uses `ota_password`). `esphome config` valid (2026.6.5).

## Profile CB2.2 (2026-09-30)

`esphome-trane.cb22.yaml` = CB2.1 plus label fixes from the 48 h household
packet and the 09-28 capture (`docs/house/evidence/2026-09-30-upstream-confirmation.md`).
`esphome-trane.cb2.yaml` (CB2.1) stays in the repo for rollback.

Entity **names are unchanged**, so every HA entity ID and Climate Brain binding
stays the same. Only units and device classes change; the corrected display
names come from Climate Brain 4.2.15 (HA `customize`).

| Entity (name kept) | Frame | Was | Now | What it really is |
|---|---|---|---|---|
| Refrigerant Pressure | 0x38F f0 | PSI | V (voltage) | line voltage, ~241 in every state |
| Discharge Temp | 0x383 f0 | °F (temperature) | psi (pressure) | suction pressure (raw; gauge/abs unresolved) |
| Compressor Frequency | OdStatus.B | Hz | % | compressor demand-type % |
| Refrig Circuit Temp | 0x387 f0 | °F (temperature) | rps | fixed ~55 speed reference |

**EXPERIMENTAL — Remote Temp Sensor 1 / 2** (`sensor.trane_thermostat_ux360_remote_temp_sensor_1` / `_2`):
0x3D0 decoded as dewbot6's SC360 wireless remote sensors (two float32 LE, °C;
bytes 4–7 = sensor 1, bytes 0–3 = sensor 2; 0 = empty slot, not published).
**Not confirmed on this house:** on 09-28 slot 2 read ~66 °F and moved with the
equipment, not with the ThirdReality upstairs-corridor sensor it sits next to.
The household will reposition the Trane sensor (it may be out of range). The
dashboard graph "EXPERIMENTAL remote sensor check" plots both slots against
the corridor sensor. Confirmed = tracks the corridor within ~1–2 °F for a day,
including when the system is idle. Otherwise the decode is removed in the next
profile. Nothing in Climate Brain reads these sensors.

Still `mode: LISTENONLY`; no transmit path.

**Validation:** `esphome config` (ESPHome 2026.6.5) reports the configuration
valid. A full compile could not run in the authoring sandbox (the PlatformIO
registry is blocked by its network policy), so the first real compile is the
Device Builder install. A compile error stops there, before any upload.

### Install (Device Builder)

1. Open **esphome-trane** in Device Builder → **Edit**.
2. Replace everything with `firmware/esphome-trane.cb22.yaml`. Keep your
   `use_address` / Wi-Fi lines if your copy differs from the repo.
3. **Save → Install → Wirelessly.** The screen shows `LISTEN ONLY CB2.2`.

### After the flash

- **Settings → Repairs:** HA may report that the unit of `Refrigerant
  Pressure`, `Discharge Temp`, `Compressor Frequency` and `Refrig Circuit
  Temp` changed. Choose **"Update the unit of the historic statistic
  values"**, or delete the old statistics. Either is fine; the values were
  never those units.
- **Compressor Power** should read in **W**. If the entity settings in HA
  still show kW (the household saw kW with watt-sized values on CB2.1), set
  the display unit back to W in the entity's settings.
- The two Remote Temp Sensors appear on the Thermostat UX360 device. `unknown`
  means no non-zero 0x3D0 slot arrived.
- **Rollback:** paste `esphome-trane.cb2.yaml` and install.
