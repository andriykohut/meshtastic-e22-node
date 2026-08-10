# Troubleshooting

## Won't flash

`Failed to connect to ESP32-S3: No serial data received` means esptool never got a reply from
the ROM bootloader.

Force download mode: hold BOOT, press and release RST, release BOOT. The board then waits there
indefinitely. On the native USB port this re-enumerates, so check `pio device list` again before
running.

If that doesn't do it, try the other USB port. On macOS a CP2102N shows up as
`/dev/cu.usbserial-*`, but boards fitted with a CH343 show as `/dev/cu.usbmodem*` — same as the
native USB peripheral — so the port name doesn't tell you which one you're on. Unplug,
`ls /dev/cu.*`, plug one in, list again.

Then pin the port and slow it down:

```ini
upload_port = /dev/cu.usbmodemXXXXXXX
upload_speed = 115200
```

Disconnect everything else while flashing, including the external 3.3 V rail — two supplies
fighting on the `3V3` pin produces exactly this. `-t erase` is optional; skip it on a fresh board.

None of the pins in this variant are ESP32-S3 strapping pins, so a soldering mistake on the LoRa,
GPS, I²C, button or ADC lines can't cause a flashing failure. Look at the cable, the port and
download mode, not your joints.

## Won't compile

`invalid conversion from 'int' to 'adc_channel_t'` in `Power.cpp` — `ADC_CHANNEL` needs an
`adc_channel_t` enum constant, not the IDF's `ADC1_GPIOn_CHANNEL` macro. On ESP32-S3, ADC1 maps
GPIO1–GPIO10 to channels 0–9, so GPIO1 is `ADC_CHANNEL_0`.

Variant macros drift between Meshtastic releases and one the firmware never reads produces no
error at all — it just silently does nothing. Worth checking the less universal ones:

```bash
grep -rn "TCXO_OPTIONAL\|GPS_EN_ACTIVE\|PIN_GPS_EN\|SX126X_RXEN" src/ | head
```

## Radio

| Symptom | Cause |
|---|---|
| Radio init failed | `USE_SX1262` instead of `USE_SX1268`; BUSY/NRST/DIO1 miswired; SPI run too long; TCXO define missing |
| Inits, transmits, never receives | RXEN not wired, or on the wrong GPIO |
| Reboots when transmitting | Not enough bulk capacitance at the E22, or the converter is undersized |
| Frequency offset, patchy links | TCXO voltage — try 1.8, then 3.3, then remove the define |
| BUSY stuck high, locks up after working | Known with this module under RadioLib. More bulk capacitance, shorter SPI, `TCXO_OPTIONAL`. See meshtastic/firmware#6692 |

## GPS

No fix ever: TX/RX swapped, no view of the sky, or the breakout's AMS1117 regulator dropping the
rail below 2.7 V. Check which LDO is fitted.

GPS never powers down: `PIN_GPS_EN` or `GPS_EN_ACTIVE` not supported in your firmware version, so
the P-FET gate is left to the pull-up. Grep for them.

## Other

Blank screen — wrong I²C pins, missing pull-ups, or a display at 0x3D rather than 0x3C.

Nonsense battery percentage — `ADC_MULTIPLIER` wrong, divider tapped before the switch, or the
100 nF on the ADC node missing. With 5% resistors, measure the pair and set `ADC_MULTIPLIER` to
the ratio you actually built.

Long press doesn't power off — it can't. There's no PMU or latch circuit here, so "shutdown" is
deep sleep and the dev board's USB-UART bridge keeps drawing. The rocker switch is the real off.
