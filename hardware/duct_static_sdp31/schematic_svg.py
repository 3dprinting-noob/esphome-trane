"""Generate the rev B schematic sheets (inline SVG) for the SDP31 duct static node."""

W = 1.6


def line(*pts):
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    return f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="{W}"/>'


def text(x, y, s, anchor="start", cls="", weight=None, size=None):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    c = f' class="{cls}"' if cls else ""
    w = f' font-weight="{weight}"' if weight else ""
    z = f' font-size="{size}"' if size else ""
    return f'<text x="{x}" y="{y}"{a}{c}{w}{z}>{s}</text>'


def dot(x, y):
    return f'<circle cx="{x}" cy="{y}" r="3.6" fill="currentColor"/>'


def box(x0, y0, x1, y1):
    return f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="2" fill="none" stroke="currentColor" stroke-width="{W}"/>'


def gnd(x, y):
    """Ground symbol hanging from (x, y)."""
    return line((x, y), (x, y + 12)) + line((x - 12, y + 12), (x + 12, y + 12)) + \
        line((x - 7, y + 17), (x + 7, y + 17)) + line((x - 3, y + 22), (x + 3, y + 22))


def pwr(x, y, name="+3V3"):
    """Power flag rising from (x, y)."""
    return line((x, y), (x, y - 14)) + line((x - 11, y - 14), (x + 11, y - 14)) + \
        text(x, y - 20, name, "middle", "nf", 500)


def res_v(x, y0, y1):
    """Vertical resistor from y0 to y1 (zigzag in the middle 30 px)."""
    m = (y0 + y1) / 2
    z0, z1 = m - 15, m + 15
    pts = [(x, y0), (x, z0)]
    ys = [z0 + 2.5 + 5 * i for i in range(6)]
    for i, yy in enumerate(ys):
        pts.append((x - 7 if i % 2 == 0 else x + 7, yy))
    pts += [(x, z1), (x, y1)]
    return line(*pts)


def res_h(y, x0, x1):
    m = (x0 + x1) / 2
    z0, z1 = m - 15, m + 15
    pts = [(x0, y), (z0, y)]
    xs = [z0 + 2.5 + 5 * i for i in range(6)]
    for i, xx in enumerate(xs):
        pts.append((xx, y - 7 if i % 2 == 0 else y + 7))
    pts += [(z1, y), (x1, y)]
    return line(*pts)


def cap_v(x, y0, y1):
    m = (y0 + y1) / 2
    return line((x, y0), (x, m - 4)) + \
        f'<path d="M{x - 14} {m - 4} H{x + 14} M{x - 14} {m + 4} H{x + 14}" stroke="currentColor" stroke-width="2.4" fill="none"/>' + \
        line((x, m + 4), (x, y1))


def sw_h(y, x0, x1):
    """Horizontal push-button between x0 and x1."""
    a, b = x0 + 8, x1 - 8
    return line((x0, y), (a - 3, y)) + line((b + 3, y), (x1, y)) + \
        f'<circle cx="{a}" cy="{y}" r="3" fill="none" stroke="currentColor" stroke-width="{W}"/>' + \
        f'<circle cx="{b}" cy="{y}" r="3" fill="none" stroke="currentColor" stroke-width="{W}"/>' + \
        line((a - 2, y - 10), (b + 2, y - 10)) + line(((a + b) / 2, y - 10), ((a + b) / 2, y - 17))


def sw_v(x, y0, y1):
    a, b = y0 + 8, y1 - 8
    return line((x, y0), (x, a - 3)) + line((x, b + 3), (x, y1)) + \
        f'<circle cx="{x}" cy="{a}" r="3" fill="none" stroke="currentColor" stroke-width="{W}"/>' + \
        f'<circle cx="{x}" cy="{b}" r="3" fill="none" stroke="currentColor" stroke-width="{W}"/>' + \
        line((x - 10, a - 2), (x - 10, b + 2)) + line((x - 10, (a + b) / 2), (x - 17, (a + b) / 2))


def tag(x, y, name, side="right"):
    """Net label; the wire meets it at (x, y). side = which way the label extends."""
    w = 8 * len(name) + 14
    if side == "right":
        x0, x1 = x, x + w
        pts = f"{x0},{y} {x0 + 7},{y - 9} {x1},{y - 9} {x1},{y + 9} {x0 + 7},{y + 9}"
        tx = (x0 + 7 + x1) / 2
    else:
        x0, x1 = x - w, x
        pts = f"{x1},{y} {x1 - 7},{y - 9} {x0},{y - 9} {x0},{y + 9} {x1 - 7},{y + 9}"
        tx = (x0 + x1 - 7) / 2
    return f'<polygon points="{pts}" fill="none" class="ns" stroke-width="1.2"/>' + \
        text(tx, y + 4, name, "middle", "nf", 500, 12)


def nc(x, y):
    return f'<path d="M{x - 5} {y - 5} L{x + 5} {y + 5} M{x + 5} {y - 5} L{x - 5} {y + 5}" stroke="currentColor" stroke-width="1.6"/>'


def svg(w, h, label, body):
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
            f'<g font-size="12.5" fill="currentColor">{body}</g></svg>')


# ---------------- Sheet 1: USB-C power + ESD ----------------
def sheet_power():
    b = []
    b.append(box(40, 40, 150, 320))
    b += [text(95, 116, "J1", "middle", weight=600, size=14), text(95, 132, "USB-C 16P", "middle", "mu"),
          text(95, 148, "C2765186", "middle", "mu")]
    pins = [(70, "VBUS"), (180, "D+"), (210, "D−"), (250, "CC1"), (280, "CC2")]
    for y, n in pins:
        b.append(text(140, y + 4, n, "end"))
    b.append(text(95, 312, "GND, shell", "middle", "mu", size=11))
    b.append(line((95, 320), (95, 330)) + gnd(95, 330))
    # VBUS -> U3
    b.append(line((150, 70), (300, 70)))
    b.append(dot(200, 70) + cap_v(200, 70, 118) + gnd(200, 118))
    b.append(text(222, 92, "C3") + text(222, 106, "10 µF", cls="mu"))
    b.append(text(258, 62, "VBUS 5 V", "middle", "nf", 500, 12))
    b.append(box(300, 40, 410, 115))
    b += [text(355, 62, "U3", "middle", weight=600, size=14), text(355, 78, "AMS1117-3.3", "middle", "mu"),
          text(355, 94, "C6186", "middle", "mu")]
    b += [text(306, 110, "IN", size=10.5), text(404, 110, "OUT", "end", size=10.5)]
    b.append(line((355, 115), (355, 125)) + gnd(355, 125))
    b.append(line((410, 70), (560, 70)))
    b.append(dot(470, 70) + cap_v(470, 70, 118) + gnd(470, 118))
    b.append(text(492, 92, "C4") + text(492, 106, "22 µF", cls="mu"))
    b.append(pwr(560, 70))
    # D+/D- through U4
    b.append(line((150, 180), (300, 180)) + line((150, 210), (300, 210)))
    b.append(box(300, 160, 410, 240))
    b += [text(355, 190, "U4", "middle", weight=600, size=14), text(355, 206, "USBLC6-2SC6", "middle", "mu"),
          text(355, 222, "C7519", "middle", "mu")]
    b += [text(294, 175, "1", "end", size=10.5), text(416, 175, size=10.5, s="6"),
          text(294, 205, "3", "end", size=10.5), text(416, 205, size=10.5, s="4")]
    b.append(line((410, 180), (470, 180)) + tag(470, 180, "USB_DP"))
    b.append(line((410, 210), (470, 210)) + tag(470, 210, "USB_DM"))
    b.append(line((330, 240), (330, 271)) + text(338, 256, "5", size=10.5) + tag(330, 271, "VBUS", "left"))
    b.append(line((380, 240), (380, 256)) + text(388, 252, "2", size=10.5) + gnd(380, 256))
    # CC pull-downs
    b.append(line((150, 250), (240, 250)) + res_v(240, 250, 312) + gnd(240, 312))
    b.append(text(250, 285, "R3") + text(250, 299, "5.1 kΩ", cls="mu"))
    b.append(line((150, 280), (200, 280)) + res_v(200, 280, 342) + gnd(200, 342))
    b.append(text(190, 372, "R4 5.1 kΩ", "end"))
    return svg(700, 390, "Sheet 1, USB-C power: J1 VBUS feeds the AMS1117-3.3 regulator U3 with C3 10 microfarad in and C4 22 microfarad out, making +3V3; CC1 and CC2 each have a 5.1 kilohm pull-down so a USB-C charger supplies 5 volts; D+ and D− pass through the USBLC6-2SC6 ESD protector U4 to the nets USB_DP and USB_DM.", "".join(b))


# ---------------- Sheet 2: ESP32-C3 module ----------------
def sheet_mcu():
    b = []
    b.append(box(280, 40, 600, 340))
    b += [text(440, 250, "U1", "middle", weight=600, size=14),
          text(440, 267, "ESP32-C3-MINI-1-N4", "middle", "mu"), text(440, 283, "C2838502", "middle", "mu"),
          text(440, 299, "Wi-Fi, native USB", "middle", "mu")]
    left = [(70, "3V3"), (120, "GPIO19 · USB D+"), (160, "GPIO18 · USB D−"), (220, "GPIO9 · BOOT"), (280, "EN")]
    right = [(70, "GPIO2"), (110, "GPIO8"), (180, "GPIO4 · SDA"), (220, "GPIO5 · SCL"), (310, "GND")]
    for y, n in left:
        b.append(line((250, y), (280, y)) + text(290, y + 4, n))
    for y, n in right:
        b.append(line((600, y), (630, y)) + text(590, y + 4, n, "end"))
    # 3V3 with decoupling
    b.append(line((60, 70), (250, 70)) + pwr(60, 70))
    b.append(dot(100, 70) + cap_v(100, 70, 110) + gnd(100, 110))
    b.append(dot(160, 70) + cap_v(160, 70, 110) + gnd(160, 110))
    b.append(text(118, 92, "C5", size=12) + text(118, 106, "10 µF", cls="mu", size=11))
    b.append(text(178, 92, "C2", size=12) + text(178, 106, "100 nF", cls="mu", size=11))
    # USB
    b.append(tag(250, 120, "USB_DP", "left") + tag(250, 160, "USB_DM", "left"))
    # BOOT
    b.append(line((250, 220), (200, 220)) + sw_h(220, 160, 200) + line((160, 220), (150, 220), (150, 232)) + gnd(150, 232))
    b.append(text(180, 200, "SW2 BOOT", "middle"))
    # EN
    b.append(line((250, 280), (60, 280)))
    b.append(res_v(60, 280, 236) + pwr(60, 236))
    b.append(text(72, 252, "R5") + text(72, 266, "10 kΩ", cls="mu", size=11))
    b.append(dot(120, 280) + sw_v(120, 280, 320) + gnd(120, 320))
    b.append(text(92, 366, "SW1 RESET", "middle", size=11.5))
    b.append(dot(190, 280) + cap_v(190, 280, 320) + gnd(190, 320))
    b.append(text(202, 302, "C6") + text(202, 316, "1 µF", cls="mu", size=11))
    # strapping pull-ups
    b.append(line((630, 70), (670, 70)) + res_h(70, 670, 730) + line((730, 70), (760, 70)) + pwr(760, 70))
    b.append(text(700, 56, "R6 10 kΩ", "middle", size=11.5))
    b.append(line((630, 110), (670, 110)) + res_h(110, 670, 730) + line((730, 110), (800, 110)) + pwr(800, 110))
    b.append(text(700, 96, "R7 10 kΩ", "middle", size=11.5))
    # I2C + GND
    b.append(line((630, 180), (660, 180)) + tag(660, 180, "SDA"))
    b.append(line((630, 220), (660, 220)) + tag(660, 220, "SCL"))
    b.append(line((630, 310), (650, 310)) + gnd(650, 310))
    b.append(text(680, 262, "GPIO2 and GPIO8 are", cls="mu", size=11.5))
    b.append(text(680, 278, "strapping pins that float;", cls="mu", size=11.5))
    b.append(text(680, 294, "R6 and R7 hold them high.", cls="mu", size=11.5))
    return svg(860, 380, "Sheet 2, microcontroller: the ESP32-C3-MINI-1 module U1 runs from +3V3 with C5 10 microfarad and C2 100 nanofarad; USB_DP and USB_DM go to GPIO19 and GPIO18; SW2 pulls GPIO9 low for boot mode; EN has R5 10 kilohm pull-up, C6 1 microfarad delay and SW1 reset; R6 and R7 pull strapping pins GPIO2 and GPIO8 high; GPIO4 and GPIO5 are SDA and SCL.", "".join(b))


# ---------------- Sheet 3: SDP31 ----------------
def sheet_sensor():
    b = []
    b.append(box(400, 80, 640, 360))
    b += [text(520, 214, "U2", "middle", weight=600, size=14), text(520, 232, "SDP31-500Pa", "middle", "mu"),
          text(520, 248, "C7075281", "middle", "mu")]
    # VDD top
    b.append(line((460, 80), (460, 40)) + line((360, 40), (700, 40)) + pwr(360, 40) + dot(460, 40))
    b.append(text(470, 100, "VDD · 7"))
    b.append(cap_v(700, 40, 90) + gnd(700, 90))
    b.append(text(722, 62, "C1") + text(722, 76, "100 nF", cls="mu"))
    # ports
    b.append('<path d="M560 80 V56 M610 80 V56" class="as" stroke-width="3" stroke-linecap="round" fill="none"/>')
    b.append(text(560 - 14, 70, "P+", "end", "af", 600) + text(610 + 14, 70, "P−", "start", "af", 600))
    # SDA / SCL
    b.append(tag(120, 170, "SDA", "left") + line((120, 170), (282, 170)) +
             '<path d="M282 170 A8 8 0 0 1 298 170" fill="none" stroke="currentColor" stroke-width="1.6"/>' +
             line((298, 170), (400, 170)))
    b.append(tag(120, 230, "SCL", "left") + line((120, 230), (400, 230)))
    b.append(text(412, 174, "SDA · 8") + text(412, 234, "SCL · 5"))
    b.append(dot(220, 170) + res_v(220, 170, 104) + pwr(220, 104))
    b.append(text(232, 132, "R1") + text(232, 146, "4.7 kΩ", cls="mu"))
    b.append(dot(290, 230) + line((290, 230), (290, 158)) + res_v(290, 158, 104) + pwr(290, 104))
    b.append(text(302, 126, "R2") + text(302, 140, "4.7 kΩ", cls="mu"))
    # ADDR
    b.append(line((400, 290), (370, 290), (370, 312)) + gnd(370, 312))
    b.append(text(412, 294, "ADDR · 9") + text(362, 284, "0x21", "end", "mu"))
    # IRQn NC
    b.append(line((640, 290), (664, 290)) + nc(668, 290) + text(628, 294, "IRQn · 4", "end") + text(680, 294, "NC", cls="mu"))
    b.append(text(628, 330, "12–16 NC", "end", "mu"))
    # GND
    b.append(line((520, 360), (520, 372)) + gnd(520, 372))
    b.append(text(520, 348, "GND · 1 2 3 6 10 11", "middle"))
    return svg(790, 410, "Sheet 3, sensor: the SDP31 U2 takes +3V3 on VDD pin 7 with C1 100 nanofarad; SDA pin 8 and SCL pin 5 have R1 and R2 4.7 kilohm pull-ups to +3V3; ADDR pin 9 to ground selects address 0x21; IRQn pin 4 is not connected; the P+ and P− ports face up for tubing.", "".join(b))


if __name__ == "__main__":
    import sys
    print(len(sheet_power()), len(sheet_mcu()), len(sheet_sensor()), file=sys.stderr)
