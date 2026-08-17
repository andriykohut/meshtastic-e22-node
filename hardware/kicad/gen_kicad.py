#!/usr/bin/env python3
"""
Generates meshtastic-node.kicad_sch.

Every pin gets a local label sitting on its connection point, so connectivity
comes from labels rather than routed wires and placement only affects readability.
If the labels come out mirrored top-to-bottom, flip `sy - py` to `sy + py` in the
label loop near the bottom.
"""
import uuid as U
from kiutils.schematic import Schematic
from kiutils.symbol import Symbol, SymbolPin
from kiutils.items.common import Position, Stroke, Property, Effects, Font, Justify
from kiutils.items.syitems import SyRect, Fill
from kiutils.items.schitems import SchematicSymbol, LocalLabel, SymbolInstance

PITCH = 2.54
NICK = "meshnode"


def make_symbol(name, left_pins, right_pins, ref_prefix, value, half_w=12.7):
    """Rectangle symbol; pins evenly spaced down each side."""
    rows = max(len(left_pins), len(right_pins), 1)
    half_h = max((rows - 1) * PITCH / 2 + PITCH, PITCH * 2)

    sym = Symbol.create_new(id=f"{NICK}:{name}", reference=ref_prefix, value=value)
    sym.properties[0].position = Position(0, half_h + 2.54, 0)
    sym.properties[1].position = Position(0, -half_h - 2.54, 0)

    g = Symbol(entryName=name, unitId=0, styleId=1)
    g.graphicItems.append(SyRect(
        start=Position(-half_w, half_h), end=Position(half_w, -half_h),
        stroke=Stroke(width=0.254, type='default'), fill=Fill(type='background')))

    p = Symbol(entryName=name, unitId=1, styleId=1)
    geometry = {}

    def add(pins, side):
        n = len(pins)
        if not n:
            return
        top = (n - 1) * PITCH / 2
        for i, pin_name in enumerate(pins):
            y = top - i * PITCH
            if side == 'L':
                pos, rot = Position(-half_w - PITCH, y, 0), 0
            else:
                pos, rot = Position(half_w + PITCH, y, 180), 180
            p.pins.append(SymbolPin(
                electricalType='passive', graphicalStyle='line',
                position=Position(pos.X, pos.Y, rot), length=PITCH,
                name=pin_name, number=pin_name))
            geometry[pin_name] = (pos.X, pos.Y)

    add(left_pins, 'L')
    add(right_pins, 'R')
    sym.units += [g, p]
    return sym, geometry


# ---------------------------------------------------------------- definitions
DEFS = {
    "ESP32-S3-DevKitC-1": (
        ["3V3", "GND"],
        ["GPIO1", "GPIO4", "GPIO5", "GPIO6", "GPIO8", "GPIO9", "GPIO10", "GPIO11",
         "GPIO12", "GPIO13", "GPIO14", "GPIO15", "GPIO16", "GPIO17", "GPIO21"],
        "U", "ESP32-S3-DevKitC-1", 17.78),
    "E22-400M22S": (
        ["VCC", "GND"],
        ["NSS", "SCK", "MOSI", "MISO", "BUSY", "DIO1", "NRST", "RXEN"],
        "U", "E22-400M22S (SX1268)", 17.78),
    "GY-NEO8MV2": (["VCC", "GND"], ["TX", "RX"], "U", "GY-NEO8MV2", 12.7),
    "SSD1306": (["VCC", "GND"], ["SDA", "SCL"], "U", "SSD1306 128x64", 12.7),
    "TP4056": (["IN+", "IN-", "B+", "B-"], ["OUT+", "OUT-"], "U", "TP4056", 12.7),
    "TPS63020": (["VIN", "GND"], ["VOUT"], "U", "TPS63020 buck-boost", 15.24),
    "AO3401A": (["G"], ["S", "D"], "Q", "AO3401A", 10.16),
    "R": (["1"], ["2"], "R", "100k", 5.08),
    "C": (["1"], ["2"], "C", "100n", 5.08),
    "CP": (["1"], ["2"], "C", "470u", 5.08),
    "SW": (["1"], ["2"], "SW", "switch", 6.35),
    "BATT": (["+"], ["-"], "BT", "18650", 6.35),
}

symbols, geoms = {}, {}
for name, (lp, rp, pref, val, hw) in DEFS.items():
    s, g = make_symbol(name, lp, rp, pref, val, hw)
    symbols[name], geoms[name] = s, g

# ------------------------------------------------------------------ placement
# (ref, symbol, x, y, value)
PLACED = [
    ("U1", "ESP32-S3-DevKitC-1", 90, 120, "ESP32-S3-DevKitC-1"),
    ("U2", "E22-400M22S", 200, 105, "E22-400M22S (SX1268)"),
    ("U3", "GY-NEO8MV2", 200, 185, "GY-NEO8MV2"),
    ("U4", "SSD1306", 200, 225, "SSD1306 128x64"),
    ("U5", "TP4056", 90, 220, "TP4056"),
    ("U6", "TPS63020", 150, 265, "TPS63020"),
    ("Q1", "AO3401A", 265, 185, "AO3401A"),
    ("R1", "R", 310, 100, "100k 1%"),
    ("R2", "R", 310, 125, "100k 1%"),
    ("R3", "R", 310, 150, "100k"),
    ("C1", "CP", 350, 100, "470u 10V low-ESR"),
    ("C2", "C", 350, 125, "10u 25V X7R"),
    ("C3", "C", 350, 150, "100n 50V X7R"),
    ("C4", "C", 350, 175, "100n 50V X7R"),
    ("SW1", "SW", 90, 265, "rocker ON/OFF"),
    ("SW2", "SW", 265, 240, "user button"),
    ("BT1", "BATT", 40, 205, "18650 protected"),
    ("BT2", "BATT", 40, 235, "18650 protected"),
]

# --------------------------------------------------------------------- nets
NETS = {
    "+3V3":      [("U1", "3V3"), ("U2", "VCC"), ("U4", "VCC"), ("Q1", "S"),
                  ("R3", "2"), ("C1", "1"), ("C2", "1"), ("C3", "1"), ("U6", "VOUT")],
    "GND":       [("U1", "GND"), ("U2", "GND"), ("U3", "GND"), ("U4", "GND"),
                  ("U5", "OUT-"), ("U5", "IN-"), ("U6", "GND"), ("C1", "2"),
                  ("C2", "2"), ("C3", "2"), ("C4", "2"), ("R2", "2"), ("SW2", "2")],
    "VBAT":      [("U5", "OUT+"), ("SW1", "1")],
    "VBAT_SW":   [("SW1", "2"), ("U6", "VIN"), ("R1", "1")],
    "BATT+":     [("BT1", "+"), ("BT2", "+"), ("U5", "B+")],
    "BATT-":     [("BT1", "-"), ("BT2", "-"), ("U5", "B-")],
    "USB_5V":    [("U5", "IN+")],
    "ADC_BATT":  [("R1", "2"), ("R2", "1"), ("C4", "1"), ("U1", "GPIO1")],
    "LORA_NSS":  [("U1", "GPIO10"), ("U2", "NSS")],
    "LORA_SCK":  [("U1", "GPIO12"), ("U2", "SCK")],
    "LORA_MOSI": [("U1", "GPIO11"), ("U2", "MOSI")],
    "LORA_MISO": [("U1", "GPIO13"), ("U2", "MISO")],
    "LORA_BUSY": [("U1", "GPIO14"), ("U2", "BUSY")],
    "LORA_DIO1": [("U1", "GPIO17"), ("U2", "DIO1")],
    "LORA_NRST": [("U1", "GPIO21"), ("U2", "NRST")],
    # RXEN (U2) is left unconnected — DIO2_AS_RF_SWITCH handles RX/TX switching
    # internally, so no GPIO drives it. GPIO15 (U1) is likewise unused.
    "I2C_SDA":   [("U1", "GPIO8"), ("U4", "SDA")],
    "I2C_SCL":   [("U1", "GPIO9"), ("U4", "SCL")],
    "GPS_TX":    [("U1", "GPIO4"), ("U3", "TX")],
    "GPS_RX":    [("U1", "GPIO5"), ("U3", "RX")],
    "GPS_EN":    [("U1", "GPIO6"), ("Q1", "G"), ("R3", "1")],
    "GPS_3V3_SW":[("Q1", "D"), ("U3", "VCC")],
    "BTN":       [("U1", "GPIO16"), ("SW2", "1")],
}

# ------------------------------------------------------------------- assemble
sch = Schematic.create_new()
from kiutils.items.common import PageSettings
sch.paper = PageSettings(paperSize="A2")
from kiutils.items.common import TitleBlock
sch.titleBlock = TitleBlock()
sch.titleBlock.title = "Meshtastic node - ESP32-S3 + E22-400M22S"
sch.titleBlock.comment = {1: "Net-label schematic; labels sit on pin connection points"}
for s in symbols.values():
    sch.libSymbols.append(s)

placement = {r: (n, x, y) for r, n, x, y, v in PLACED}
uuids = {}

for ref, name, x, y, val in PLACED:
    inst_uuid = str(U.uuid4())
    uuids[ref] = inst_uuid
    ss = SchematicSymbol(
        libraryNickname=NICK, entryName=name, position=Position(x, y, 0),
        unit=1, inBom=True, onBoard=True, uuid=inst_uuid)
    hw_map = {n: d[4] for n, d in DEFS.items()}
    off = hw_map[name] + 6
    ss.properties.append(Property(key="Reference", value=ref, id=0,
                                  position=Position(x - off, y - 4, 0),
                                  effects=Effects(font=Font(width=1.27, height=1.27))))
    ss.properties.append(Property(key="Value", value=val, id=1,
                                  position=Position(x - off, y - 1, 0),
                                  effects=Effects(font=Font(width=1.27, height=1.27),
                                                  justify=Justify(horizontally="left"))))
    ss.properties.append(Property(key="Footprint", value="", id=2,
                                  position=Position(x, y, 0),
                                  effects=Effects(font=Font(width=1.27, height=1.27), hide=True)))
    ss.properties.append(Property(key="Datasheet", value="", id=3,
                                  position=Position(x, y, 0),
                                  effects=Effects(font=Font(width=1.27, height=1.27), hide=True)))
    for pin_name in geoms[name]:
        ss.pins[pin_name] = str(U.uuid4())
    sch.schematicSymbols.append(ss)
    sch.symbolInstances.append(SymbolInstance(
        path=f"/{inst_uuid}", reference=ref, unit=1, value=val, footprint=""))

# labels on pin connection points. Schematic Y is inverted vs symbol library Y.
check = []
for net, pins in NETS.items():
    for ref, pin_name in pins:
        name, sx, sy = placement[ref]
        px, py = geoms[name][pin_name]
        lx, ly = sx + px, sy - py
        rot = 0 if px < 0 else 180
        just = "right" if px < 0 else "left"
        sch.labels.append(LocalLabel(
            text=net, position=Position(lx, ly, rot),
            effects=Effects(font=Font(width=1.27, height=1.27),
                            justify=Justify(horizontally=just))))
        check.append((net, ref, pin_name, round(lx, 3), round(ly, 3)))

sch.to_file("meshtastic-node.kicad_sch")

# ------------------------------------------------- self-check and netlist dump
seen = {}
collisions = 0
for net, ref, pin, x, y in check:
    key = (x, y)
    if key in seen and seen[key][0] != net:
        print(f"!! COLLISION at {key}: {seen[key]} vs {(net, ref, pin)}")
        collisions += 1
    seen[key] = (net, ref, pin)

allpins = {(r, p) for n, pl in NETS.items() for r, p in pl}
declared = {(r, p) for r, nm, x, y, v in PLACED for p in geoms[nm]}
missing = declared - allpins
print(f"symbols: {len(PLACED)}  nets: {len(NETS)}  labelled pins: {len(check)}")
print(f"coordinate collisions: {collisions}")
print(f"pins with no net: {sorted(missing) if missing else 'none'}")

with open("netlist.txt", "w") as f:
    f.write("Meshtastic node - intended netlist\n")
    f.write("Compare against KiCad's ERC / netlist export to verify the schematic.\n\n")
    for net, pins in NETS.items():
        f.write(f"{net}\n")
        for r, p in pins:
            f.write(f"    {r}.{p}\n")
        f.write("\n")
print("wrote meshtastic-node.kicad_sch and netlist.txt")
