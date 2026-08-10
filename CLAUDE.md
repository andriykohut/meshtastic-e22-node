# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hardware design + firmware variant project for a custom [Meshtastic](https://meshtastic.org/) mesh networking node built around an ESP32-S3-DevKitC-1 and an Ebyte E22-400M22S (SX1268) LoRa radio module. It is **not** a standalone firmware — it extends the official Meshtastic firmware by contributing a variant definition.

## Build Setup

All commands are wrapped in the `Makefile`. It clones the Meshtastic firmware into
`build/firmware` (gitignored) and copies `variant.h` / `platformio-env.ini` into it before
every build:

```bash
make build      # or: pio run -d build/firmware -e esp32s3-e22-433
make upload     # or: pio run -d build/firmware -e esp32s3-e22-433 -t upload
make monitor    # or: pio run -d build/firmware -e esp32s3-e22-433 -t monitor
make ports      # or: pio device list — find the correct USB port
```

Equivalent manual steps, if you'd rather manage the firmware checkout yourself:

```bash
git clone https://github.com/meshtastic/firmware.git
cd firmware
git submodule update --init --recursive

mkdir -p variants/esp32s3-e22-433
cp /path/to/this/repo/firmware/variant.h variants/esp32s3-e22-433/
cat /path/to/this/repo/firmware/platformio-env.ini >> platformio.ini
```

Post-flash Meshtastic configuration:

```bash
make configure   # or: meshtastic --set lora.region EU_433 && meshtastic --set lora.modem_preset LONG_FAST
```

## Hardware Documentation Tools

Python tooling (WireViz, kiutils) is managed with [uv](https://github.com/astral-sh/uv) via
`pyproject.toml`. Install dependencies into a local `.venv` with:

```bash
make setup   # or: uv sync
```

Regenerate the signal harness diagram from `hardware/harness.yml`:

```bash
make harness   # or: uv run wireviz hardware/harness.yml
```

Regenerate the KiCad schematic from `hardware/kicad/gen_kicad.py`:

```bash
make kicad   # or: cd hardware/kicad && uv run python3 gen_kicad.py
```

Validate the firmware compiles cleanly after changes:

```bash
make validate   # or: grep -rn "TCXO_OPTIONAL\|GPS_EN_ACTIVE\|PIN_GPS_EN\|SX126X_RXEN" build/firmware/src/
```

## Architecture

There is no runtime logic here. The repo has three parts:

**`firmware/`** — Two files that extend Meshtastic firmware:
- `variant.h`: All GPIO pin assignments and hardware parameters as C preprocessor defines. This is the only file the Meshtastic build system reads.
- `platformio-env.ini`: A single PlatformIO environment snippet to append to the firmware's `platformio.ini`.

**`hardware/`** — Hardware design sources:
- `harness.yml`: WireViz YAML describing all wiring between modules (16 signal nets). The SVG/PNG renders live in `docs/`.
- `netlist.txt`: Authoritative electrical connectivity reference (118 pins across all components).
- `kicad/gen_kicad.py`: Python script that programmatically constructs a KiCad `.kicad_sch` schematic using the `kiutils` library. The generated schematic is committed alongside the script.

**`docs/`** — Build, BOM, and troubleshooting documentation in Markdown.

## Critical Design Decisions

**SX1268, not SX1262.** The E22-400M22S uses the SX1268 (410–493 MHz variant). Using `USE_SX1262` in the firmware kills the radio silently.

**TXEN is bonded internally.** The E22 module bonds TXEN to DIO2 internally. Only RXEN (GPIO17) needs MCU control; the TXEN pad on the module must be left unconnected.

**ADC channel is an enum, not a macro.** `ADC_CHANNEL` in `variant.h` must be `ADC_CHANNEL_0` (the ESP-IDF enum value), not a raw integer or IDF macro — the Meshtastic codebase expects the enum form.

**`TCXO_OPTIONAL` is required.** Without this define, a TCXO init failure on first boot halts radio initialization entirely rather than falling back gracefully.

**Power architecture.** The node uses a TPS63020 buck-boost converter fed from 2× 18650 cells in parallel. The DevKitC's onboard 3.3V regulator is bypassed by feeding the 3.3V pin directly. A plain buck converter would drop out around 3.6–3.7V, wasting most of the battery capacity.

**GPS power switch.** GPIO6 drives an AO3401A P-FET high-side switch (`GPS_EN_ACTIVE 0` = low is powered). This cuts the ~35mA idle GPS draw when not needed.

**Bulk decoupling for E22 PA.** The E22 needs 470µF + 10µF + 100nF within ~10mm of its VCC pin to handle PA current spikes during transmission. Insufficient capacitance causes brownout resets on TX.

## Staged Bring-Up Order

When building or debugging hardware, follow this sequence to isolate failures:

1. Bare board + USB — verify boot log, no brownout resets
2. Add OLED — check for splash screen; run I²C scan if blank (expected addr: 0x3C)
3. Add GPS — watch for NMEA detection in serial log; first cold fix takes ~15 min outdoors
4. Add LoRa — antenna **must** be attached before any TX; look for SX1268 init in logs
