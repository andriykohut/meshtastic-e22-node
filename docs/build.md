# Build notes

## Power

A single Li-ion cell swings 4.2 V down to 3.0 V, which straddles 3.3 V. That rules out a plain
buck converter, which drops out around 3.6–3.7 V and throws away most of the capacity. The
TPS63020 takes 1.8–5.5 V in and holds 3.3 V across the whole curve.

```
2× 18650 (parallel) → TP4056 → rocker switch → TPS63020 @ 3.3 V → DevKitC 3V3 pin
```

Feeding the `3V3` pin bypasses the DevKitC's own regulator, which can't run from a cell anyway.
The switch is there so the external rail isn't fighting that regulator when USB is plugged in —
switch off before connecting USB. It sits after the charger, so the pack still charges with the
node off.

Set the converter to 3.30 V with a multimeter, output unloaded, before it touches anything else.
These modules arrive at arbitrary trim and 5 V on that rail takes out the ESP32-S3, the E22 and
the GPS in one go.

### Decoupling

470 µF + 10 µF + 100 nF from VCC to GND, all within 10 mm of the E22's VCC pad. The electrolytic
handles the PA current bursts, the 100 nF handles the fast edges, and the 10 µF covers the gap
between them where the SX1268's internal switcher lives. A rail that sags under transmit is the
usual reason a radio initialises fine and then has no range.

Solder the 100 nF directly across the module's VCC and GND pads. Long legs add inductance and
defeat the point.

### The 2P pack

Charge both cells individually and get them within ~50 mV of each other before wiring them in
parallel. Connecting a full cell to an empty one puts the difference across nothing but internal
resistance and your wiring. After that they stay balanced on their own.

Series would have meant replacing the TP4056 (single-cell only) and the TPS63020 (5.5 V absolute
max input), and gained nothing, since EU_433 clamps output power far below what the module can do.

## Construction

Isolated-pad perfboard, double-sided, plated through-holes. Not stripboard and not
breadboard-pattern board — the DevKitC's PCB body overhangs its pin rows and covers the holes
you'd otherwise connect through. On perfboard every connection is made on the solder side, so
the overhang doesn't matter.

An 80 × 120 mm board is about 31 × 47 holes; the DevKitC eats under 20% of that.

For the power rails, lay bare tinned 22 AWG wire along a row of pads and solder it at every pad.
Fifteen minutes and you have rails wherever you want them.

To get the header spacing right, mate the female headers onto the DevKitC's pins first, then
lower the whole thing onto the board and solder from underneath while still mated. Alignment
comes out automatic and the headers stay perpendicular, which freehand soldering never does.

E22 and its capacitors at one end, DevKitC socketed in the middle, converter and battery input
at the other. Solder the E22's 1.27 mm pads first while the board is still bare and you can get
an iron in from any angle.

## Antenna

Never key the transmitter without a 50 Ω load on ANT. +22 dBm into an open circuit will kill the
PA and it can happen on the first beacon after boot.

Watch connector gender. RP-SMA male threads happily into an SMA female bulkhead and makes no
centre contact at all, which looks exactly like a working assembly. Look inside: SMA female has a
socket, SMA male has a pin. If the bulkhead has a pin and the antenna has a socket, it's RP-SMA.

## Bring-up

Stage it, or you'll be debugging four things at once.

1. Bare board — flash, check the boot log, check for brownout resets
2. OLED only — Meshtastic splash should appear. I²C scan first if not.
3. GPS — watch for NMEA detection. First cold fix outdoors can take 15 minutes.
4. LoRa, **antenna attached** — look for SX1268 init in the log

## Region

EU_433 caps transmit power well below the module's 22 dBm, because the European 433 MHz
allocation is around 10 mW ERP. The firmware handles the clamping. The E22-400M22S only covers
410–493 MHz so 868 isn't an option with this hardware.

Worth knowing that 433 is heavily congested — RC gear, telemetry, and assorted noise. Expect a
worse noise floor than the link budget suggests.
