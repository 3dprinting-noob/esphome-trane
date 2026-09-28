# Installed configuration (household device)

`esphome-trane.atoms3r.yaml` is the configuration believed to be running on the
household device, recovered from the build machine on 2026-09-28. It was never
committed before; this is the baseline for all later changes.

Device (matches the Home Assistant device page):

- ESPHome name `esphome-trane`, friendly name "ESPHome Trane", firmware `dev`
  (built locally, ESPHome 2026.6.5), IP 10.70.1.94
- M5Stack AtomS3R + M5Stack CAN module; CAN TX GPIO5 / RX GPIO6, 50 kbps
- Display: ST7735 128x128 on SPI (CLK GPIO15, MOSI GPIO21, DC GPIO42,
  RST GPIO48, CS GPIO14); backlight via LP5562 on I2C (SDA GPIO45, SCL GPIO0)

Safety state:

- `canbus: mode: LISTENONLY` — the CAN controller cannot transmit.
- The boot `GetProfile` request is commented out.
- The transmit script, `set_temperature` / `set_mode` API services and the
  `trane_climate` control actions are still present but inert under
  LISTENONLY (the `trane_tx` "Sent:" log line is misleading).

Not included: the local `components/trane_hvac` folder the climate entity
needs, and `secrets.yaml` (Wi-Fi only; there is no API encryption key and no
OTA password).

Known mislabels (cross-checked against Climate Brain's 2026-09-10
`trane_engineering.csv` and uncharted9898/esphome-trane `docs/TELEMETRY.md`):

| Entity | Source | Actually |
|---|---|---|
| Refrigerant Pressure | 0x38F float0 | line voltage (flat 231–237) |
| Discharge Temp | 0x383 float0 | suction pressure, absolute (falls when running) |
| Refrig Sensor B | 0x386 float1 | fixed constant 50 |
| Refrig Circuit Temp | 0x387 float0 | fixed compressor speed reference (~55 RPS) |
| Suction Temp | 0x381 float0 | likely outdoor coil temperature |
| Supply Air Fault = TA_INV_HI | IndoorStatus.E | normal startup token, not a fault |
| Indoor Humidity (integer E) | SystemOpStatus.E | disputed: uncharted reads E as compressor speed ceiling |

## History

`history/esphome-trane-before-display-test.yaml` is the earlier version. It
differs from the current file only in the display section: ST7789V at 40 MHz
without padding, a static "Waiting for CAN" line, and no received-frame counter.
The current file switched to the ST7735 model (20 MHz, padded) and added the
`can_rx_count` / `last_can_rx_ms` counter shown on the screen. The CAN, sensor
and LISTENONLY settings are identical in both.
