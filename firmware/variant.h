// ESP32-S3-DevKitC-1 + Ebyte E22-400M22S (SX1268 + PA/LNA) + GY-NEO8MV2 + SSD1306
//
// Avoids GPIO0/3/45/46 (strapping), GPIO19/20 (native USB), GPIO26-37 (flash and
// octal PSRAM on N8R8/N16R8 parts), GPIO38/48 (onboard RGB LED).

#define HAS_GPS 1

// I2C — the SSD1306 is autodetected on the bus
#define I2C_SDA 8
#define I2C_SCL 9

// GPS. GPS_RX_PIN is the ESP32 input, so it goes to the NEO-8M's TX pad.
#define GPS_RX_PIN 4
#define GPS_TX_PIN 5

// AO3401A high-side switch on the GPS 3V3 feed: source to 3V3, drain to GPS VCC,
// gate to GPIO6 with 100k to 3V3. Low = GPS powered. The GY-NEO8MV2 has no enable
// pin, so this is the only way to stop it drawing 30-45 mA around the clock.
#define PIN_GPS_EN 6
#define GPS_EN_ACTIVE 0

// Panel-mounted button to GND. Internal pull-up is enabled by the firmware.
#define BUTTON_PIN 16

// Radio. SX1268, not SX1262 — the 900 MHz sibling is the SX1262 part.
#define USE_SX1268

#define LORA_SCK 12
#define LORA_MISO 13
#define LORA_MOSI 11
#define LORA_CS 10
#define LORA_RESET 21
#define LORA_DIO1 15

#define SX126X_CS LORA_CS
#define SX126X_SCK LORA_SCK
#define SX126X_MOSI LORA_MOSI
#define SX126X_MISO LORA_MISO
#define SX126X_RESET LORA_RESET
#define SX126X_DIO1 LORA_DIO1
#define SX126X_BUSY 14

// TXEN is bonded to DIO2 on the module itself, so the chip drives the TX side of
// the RF switch. Leave the TXEN pad unconnected; only RXEN needs a GPIO.
#define SX126X_DIO2_AS_RF_SWITCH
#define SX126X_TXEN RADIOLIB_NC
#define SX126X_RXEN 17

// 32 MHz TCXO fed from DIO3. TCXO_OPTIONAL retries without it if init fails.
#define SX126X_DIO3_TCXO_VOLTAGE 1.8
#define TCXO_OPTIONAL

// Clamped down to the regional limit anyway, which for EU_433 is well under this.
#define SX126X_MAX_POWER 22

// 100k/100k divider from the pack (after the switch) to GPIO1, 100nF to GND.
// ADC_CHANNEL must be an adc_channel_t enum, not the IDF's ADC1_GPIOn_CHANNEL
// macro — those are plain ints now and Power.cpp won't take them. ESP32-S3 ADC1
// maps GPIO1..GPIO10 to channels 0..9.
#define BATTERY_PIN 1
#define ADC_CHANNEL ADC_CHANNEL_0
#define ADC_MULTIPLIER 2.0
#define BATTERY_SENSE_RESOLUTION_BITS 12
