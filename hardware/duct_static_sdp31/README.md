# Duct static node: Sensirion SDP31 + ESP32 (drawing DS-01, rev A)

A separate Wi-Fi device from the Trane CAN recorder, with no CAN connection.
It measures total external static pressure: P+ goes to the supply plenum
and P− to the return, on the room side of the filter. It reports to Home
Assistant through ESPHome.

- `schematic.html`: schematic, duct plumbing, parts list, install and
  check-out steps. Published at https://claude.ai/artifact/VHARER1yg1nKfbYYpHPqwD
- `duct-static.yaml`: ESPHome config. It passes `esphome config` on
  ESPHome 2026.6.5.
  - It uses the `sdp3x` driver: address 0x21, reports in hPa, and the
    config converts to Pa and inWC.
  - Secrets: `wifi_ssid`, `wifi_password`, `ota_password` and
    `duct_static_api_key`.

## Wiring

| Net | ESP32-DevKitC | SDP31 pin |
|---|---|---|
| +3V3 | 3V3 | 7 VDD |
| GND | GND | 1 2 3 6 10 11 |
| SDA | GPIO21 | 8 |
| SCL | GPIO22 | 5 |
| ADDR | — | 9 → GND (0x21) |
| IRQn | — | 4, not connected |

- Pull-ups: 4.7 kΩ to 3.3 V.
- Decoupling: 100 nF next to VDD. Most breakouts already carry these parts.
- Never tie ADDR to VDD.

## Part name and alternatives

The household asked for an "STB 31". Sensirion's matching part is the
SDP31 (±500 Pa). Do not substitute the SDP32: its ±125 Pa range is below
the ~1.0 inWC (249 Pa) seen at maximum blower. The SDP810-500Pa (barbed
ports) is a drop-in replacement at address 0x25.

## Sources

- Pin numbers and ADDR rules: Sensirion's SDP3x-Digital datasheet, read
  through search results because the datasheet host was blocked from the
  authoring sandbox. Verify the numbers before laying out a custom PCB.
- Driver behaviour: ESPHome's own `sdp3x` source.
