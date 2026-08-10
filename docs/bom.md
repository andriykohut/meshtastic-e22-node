# BOM

Excludes the main modules (ESP32-S3-DevKitC-1, E22-400M22S, GY-NEO8MV2, SSD1306, TP4056),
which I already had, and the antenna and pigtail.

| Qty | Part | Notes |
|---|---|---|
| 2 | 18650, protected, 3400–3500 mAh | Same make and batch. Anything claiming 5000 mAh+ is fake. |
| 2 | 18650 holder, PCB mount | Keystone 1043 style. Two singles wired in parallel — check any "dual" holder isn't series. |
| 1 | TPS63020 buck-boost module | Must be buck-*boost*. Set to 3.30 V before connecting anything. |
| 1 | KCD1-101 rocker switch | Two pins means ON-OFF. Three means changeover, which won't disconnect anything. |
| 1 | 470 µF electrolytic, low-ESR, 105 °C | 330–1000 µF and 6.3–25 V all fine. Low-ESR and 105 °C matter more than the exact numbers. |
| 10 | 10 µF ceramic, 25 V, X7R, 1206 | 16–50 V, 0805–1210. Ceramics lose capacitance under DC bias, so bigger package and higher voltage is better here. Three 10 µF 6.3 V in parallel works if that's all there is. |
| 20 | 100 nF ceramic, 50 V, X7R, 0805 | 16–100 V, 47–220 nF, any package. Not Y5V. |
| 10 | 100 kΩ, 1%, metal film | Any matched pair 47–220 kΩ works; only the ratio matters. R3 is uncritical, 10 kΩ–1 MΩ. |
| 2 | AO3401A P-MOSFET, SOT-23 | Or AO3407, SI2301, DMG2301L, IRLML6402. Needs a gate threshold under ~1.5 V so it turns on at 3.3 V. Optional — skip it and you just lose runtime. |
| 1 | Perfboard, double-sided, plated holes, 80×120 mm | Isolated pads, not stripboard. See build notes. |
| 1 | 2.54 mm female header strip, 40 pin | Cut to length to socket the DevKitC. |
| 1 | 30 AWG silicone wire, assorted | Signals. 22 AWG for power rails. |
| 1 | 12 mm momentary pushbutton, NO | Momentary, not latching — «без фіксації». |
| 1 | M3 brass heat-set inserts | For the printed enclosure. |

Tools that aren't optional: a multimeter (you cannot set the converter or check cell balance
without one), a temperature-controlled iron with a fine tip, and no-clean flux for the E22's
1.27 mm pads.

## Check before ordering

The GPS breakout's regulator. If it's an **AMS1117-3.3** its 1.1 V dropout means 3.3 V in gives
~2.2 V out, below the NEO-8M's 2.7 V minimum, and it will never get a fix. MIC5205 or HT7333
are fine. If it is an AMS1117, bridge its input to output — it has no job on a clean 3.3 V rail.

Also worth having: a second, commercial 433 MHz node. One node on its own shows you an empty
node list and nothing else, so you can't tell a broken radio from an empty mesh. Check the band
variant really covers 433 — plenty of "433/470 MHz" boards are matched for 470–510.
