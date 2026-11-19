# Firmware notes

## First boot & calibration
1. Flash `STM32G431CBT6` over SWD (`25 MHz` HSE → `170 MHz`).
2. Verify `M24C64` (`0x50`), `BQ25756` (`0x6B`), `BQ76952` (`0x08`), `ADS1256`, and `AD9833` SPI write.
3. Calibrate `1 kHz` AC IR gain/phase offset using known `10 mΩ` and `100 mΩ` 4-wire reference resistors, plus DC voltage/current across `ADS1256` and `BQ25756`; store into `M24C64` with `CRC32`.

## Hardware limits the firmware must respect
- **`1 kHz` AC IR relay sequencing:** before enabling `AD9833` measurement, set `BQ25756` charge disable (`EN_CHG = 0`) and `IRFP250N` `I_DISCHARGE = 0`, open `TQ2-5V` isolation relay, wait `15 ms` for AC-coupling film caps to settle, run synchronous `1 kHz` lock-in integration (`100–200 ms`), then close `TQ2-5V` only when charger/load targets are zero.
- **Reverse-polarity & cell-count detection:** read `XT60` polarity (`ADS1256`) and balance taps (`BQ76952`) before engaging `TQ2-5V` or `BQ25756`; abort immediately if `V_BAT < -0.1 V` or `|V_PACK - sum(V_CELLS)| > 0.3 V`.
- **Safe Li-ion cutoffs:** enforce `V_CELL_MAX <= 4.25 V` (Li-ion) / `3.65 V` (LiFePO4), `V_CELL_MIN >= 2.50 V`, heatsink/cell NTC `<= 60 °C` during charge and `<= 70 °C` heatsink during `100 W` discharge.
- **Linear discharge power limit:** cap `V_BAT * I_DISCHARGE <= 100 W` continuously (`<= 4.0 A` at `25.2 V` `6S`, `10.0 A` at `1S–2S`).
