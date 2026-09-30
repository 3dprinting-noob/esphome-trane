# Duct static node: Sensirion SDP31 + ESP32 (drawing DS-01)

A separate Wi-Fi device from the Trane CAN recorder, with no CAN connection.
It measures total external static pressure: P+ goes to the supply plenum
and P− to the return, on the room side of the filter. It reports to Home
Assistant through ESPHome.

Full drawing: `schematic.html`, published at
https://claude.ai/artifact/VHARER1yg1nKfbYYpHPqwD. It holds the schematic
sheets, netlist, BOM, layout rules, plumbing and bring-up steps.

## Rev B: single board for JLCPCB (current)

| File | What |
|---|---|
| `jlcpcb_bom.csv` | JLCPCB BOM upload: Comment, Designator, Footprint, LCSC Part # (13 lines, 20 placements) |
| `duct-static.yaml` | ESPHome for the Rev B board (ESP32-C3, I²C on GPIO4/5, USB Serial/JTAG) |
| `schematic_svg.py` | Generator for the three schematic sheets on the page |

The parts are:
- U1: ESP32-C3-MINI-1-N4 (C2838502);
- U2: SDP31-500Pa (C7075281, or the C7461776 reel);
- U3: AMS1117-3.3 (C6186);
- U4: USBLC6-2SC6 (C7519);
- J1: USB-C 16P (C2765186);
- SW1, SW2: TS-1187A-B-A-B (C318884);
- 0402/0603/0805 passives.

Every LCSC number was checked against its JLCPCB/LCSC listing on
2026-09-30.

Before you order:
- Check the SDP31's stock. If it's out, use Global Sourcing or pre-order it
  into your JLCPCB inventory.
- Add "no washing, no conformal coating" to the order notes, because the
  SDP31 has open ports.
- Check part rotation in the CPL preview.

These are not produced here, so draw the board in EasyEDA or KiCad:
- Gerbers;
- the CPL (placement) file.

In EasyEDA, placing each part by its LCSC number gives the exact footprint.

## Rev A: breadboard prototype

`duct-static-devkitc.yaml`: an ESP32-DevKitC plus an SDP31 breakout,
wired as follows.

| Net | ESP32-DevKitC | SDP31 pin |
|---|---|---|
| +3V3 | 3V3 | 7 VDD |
| GND | GND | 1 2 3 6 10 11 |
| SDA | GPIO21 | 8 |
| SCL | GPIO22 | 5 |
| ADDR | — | 9 → GND (0x21) |
| IRQn | — | 4, not connected |

## Part name

Sensirion doesn't make an "STB 31"; the matching part is the SDP31
(±500 Pa). Don't use the SDP32: its ±125 Pa range is below the ~1.0 inWC
(249 Pa) seen at maximum blower.

## Sources

- The SDP31 pin numbers come from Sensirion's SDP3x-Digital datasheet,
  read through search results. Verify them against the footprint you place.
- ESP32-C3 strapping behaviour comes from Espressif's ESP32-C3-MINI-1
  datasheet: GPIO2 and GPIO8 float, and GPIO9 is pulled up.
- Driver behaviour comes from ESPHome's own `sdp3x` source.
