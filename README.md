# battery-tester

![KiCad](https://img.shields.io/badge/KiCad-10-314CB0?logo=kicad&logoColor=white)
![Battery](https://img.shields.io/badge/Range-1S--6S%20%2B%201kHz%20AC%20IR-informational)
![Status](https://img.shields.io/badge/status-pre--schematic-orange)
![License](https://img.shields.io/badge/license-MIT-green)

A `1S–6S` battery capacity analyzer and cell sorter combining **4-wire `1 kHz` AC internal resistance** measurement (`YR1035+` style) with programmable **CC/CV charging (`BQ25756`)** and **linear CC discharging (`100 W`)** — built into the shared bench instrument enclosure family.

## Highlights

- **1S–6S Li-ion / LiFePO4 / LTO** (`0.5–26 V`): tests single `18650`/`21700` cells and full multi-cell packs (`XT60` + `JST-XH` balance port + Kelvin clips)
- **4-wire `1 kHz` AC IR**: `AD9833` `1 kHz` excitation + `INA826` Kelvin amp + synchronous lock-in readout (`TQ2-5V` relay isolates charger/load capacitance during IR pulses)
- **Charge & discharge analyzer**: `BQ25756` (`5 A` CC/CV) + `2× IRFP250N` linear sink (`10 A / 100 W` down to `0.5 V`), `BQ76952` per-cell tap monitoring
- **Automated sorting mode**: Charge → Rest → `1 kHz` IR → Discharge (`mAh`/`Wh`) → Storage charge, plotted live on screen
- **Shared family UI**: `3.5"` `480×320` IPS TFT (`ST7796S`), `2× EC11`, `6` keys, `M24C64` EEPROM calibration, isolated USB-C CSV/SCPI

## How it works

```
XT60 / Kelvin 4W ─► TQ2-5V Isolate ─┬─ BQ25756 (1S–6S CC/CV Charge) ◄─ Mean Well LRS-150-24
                                    └─ 2x IRFP250N + OPA2188 (100W Linear Discharge)
                  (Relay Open) ────► AD9833 1kHz Sine ─► INA826 ─► ADS1256 24-bit ─► STM32G431
```

Full architecture, BOM with live JLCPCB stock/prices, cost estimate, and calibration procedures are in **[battery_tester.md](battery_tester.md)**.

## Specs (planned)

| | |
|---|---|
| Cell / Pack range | `1S–6S` (`0.5–26.0 V`) |
| AC Internal Resistance | `4-wire` Kelvin `1 kHz` synchronous, `0.1 mΩ` target resolution |
| Charge / Discharge | `BQ25756` up to `5 A` CC/CV / Linear sink up to `10 A` (`100 W`) |
| Precision & BMS | `ADS1256` (24-bit), `REF5025`, `BQ76952` `6S` cell monitor |
| Display & UI | `3.5"` `480×320` IPS TFT (`ST7796S`), `2× EC11`, `6` keys |
| Calibration & AC | `M24C64` EEPROM, isolated USB-C SCPI, `Mean Well LRS-150-24` |

## Repo layout

```
battery_tester.md          project documentation (start here)
battery_tester.kicad_*     KiCad 10 project
code.md                    firmware limits & relay sequencing
lib/                       symbols, footprints, 3D models
datasheets/                datasheets for all 35 chosen parts
battery_tester.tex         printable writeup
```

## Status

- [x] Requirements, architecture, full BOM (`2026-11-19`)
- [x] KiCad libraries (`lib/`) + datasheets (`datasheets/`)
- [ ] Enclosure CAD & Kelvin fixture (`enclosure/`)
- [ ] Schematic & 4-layer PCB
- [ ] Firmware & EEPROM calibration

## License

[MIT](LICENSE) for design files and documentation. Datasheets in `datasheets/` belong to their manufacturers. Footprints and 3D models in `lib/` were generated from EasyEDA/LCSC data.
