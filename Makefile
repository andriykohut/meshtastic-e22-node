.PHONY: setup harness kicad validate firmware-clone firmware-install build upload monitor ports configure clean

UV := uv
PIO := pio
MESHTASTIC := meshtastic
FIRMWARE_DIR := build/firmware
PIO_ENV := esp32s3-e22-433
REGION := EU_433
MODEM_PRESET := LONG_FAST

# --- Python tooling (WireViz, kiutils) ---

setup:
	$(UV) sync

harness: setup
	$(UV) run wireviz hardware/harness.yml -f ps -o docs -O harness

kicad: setup
	cd hardware/kicad && $(UV) --project ../.. run python3 gen_kicad.py

# --- Firmware build ---

firmware-clone:
	if [ ! -d $(FIRMWARE_DIR) ]; then \
		git clone https://github.com/meshtastic/firmware.git $(FIRMWARE_DIR); \
	fi
	cd $(FIRMWARE_DIR) && git submodule update --init --recursive

firmware-install: firmware-clone
	mkdir -p $(FIRMWARE_DIR)/variants/$(PIO_ENV)
	cp firmware/variant.h $(FIRMWARE_DIR)/variants/$(PIO_ENV)/
	cp firmware/platformio-env.ini $(FIRMWARE_DIR)/variants/$(PIO_ENV)/platformio.ini

build: firmware-install
	$(PIO) run -d $(FIRMWARE_DIR) -e $(PIO_ENV)

upload: firmware-install
	$(PIO) run -d $(FIRMWARE_DIR) -e $(PIO_ENV) -t upload

monitor:
	$(PIO) run -d $(FIRMWARE_DIR) -e $(PIO_ENV) -t monitor

ports:
	$(PIO) device list

configure:
	$(MESHTASTIC) --set lora.region $(REGION)
	$(MESHTASTIC) --set lora.modem_preset $(MODEM_PRESET)

validate: firmware-clone
	grep -rn "TCXO_OPTIONAL\|GPS_EN_ACTIVE\|PIN_GPS_EN\|SX126X_RXEN" $(FIRMWARE_DIR)/src/

# --- Cleanup ---

clean:
	rm -rf .venv

distclean: clean
	rm -rf $(FIRMWARE_DIR)
