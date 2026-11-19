# Battery Capacity Tester

Author: Stefan Jipa

## Goal
A `1S–6S` battery analyzer and cell-sorting instrument combining **4-wire `1 kHz` AC internal resistance** measurement (`YR1035+` class, `0.1 mΩ` resolution) with a programmable **CC/CV charger and CC discharge cycler**, built into the shared bench instrument enclosure family.

## Requirements
- **Cell & pack range:** **`1S–6S` (`0.5–26.0 V`)** Li-ion / LiFePO4 / LTO via front `XT60` + `7-pin` `JST-XH` balance port + `4-wire` Kelvin test leads (`FORCE+/-`, `SENSE+/-`), decided `2026-11-19`
- **4-wire `1 kHz` AC internal resistance (IR):** `AD9833` `1 kHz` sine excitation (`~50 mA pk-pk` AC-coupled) + `INA826` Kelvin sensing + synchronous demodulation in `ADS1256`/`STM32G431`, **relay-isolated (`TQ2-5V`)** from charger/load bulk capacitors during the `200 ms` IR pulse (`2026-11-19`)
- **Charge & discharge cycling:**
  - **Charge (`BQ25756`):** programmable `0.1–5.0 A` CC/CV up to `25.2 V` (`6S`) with `BQ76952` per-cell voltage monitoring and balancing
  - **Discharge (`2× IRFP250N` linear sink):** programmable `0.1–10.0 A` (`100 W` continuous on heatsink + fan), operates cleanly down to `0.5 V` for `1S` deep-discharge curves
- **Automated cell-sorting / cycle mode:** Charge → Rest (1 h) → 1 kHz AC IR → CC Discharge (`mAh`/`Wh`) → Recharge to storage (`3.85 V/cell`) with curve plotting on the `3.5"` screen and CSV export over isolated USB-C
- **Mains powered (`230 V AC`):** rear IEC C14 fused/switched inlet + PE earth → internal **Mean Well LRS-150-24** (`24 V / 6.5 A`, `159 × 97 × 30 mm`), decided `2026-11-19`
- **Shared bench instrument enclosure family (`2026-11-19`):**
  - Angled (`~15°`) desktop shell (`185 × 165 × 88 mm`), `2-PCB` modular split (`Front Panel 168 × 72 mm` + `Mainboard 168 × 125 mm`)
  - **Shared display:** **3.5" 480×320 IPS TFT (`ST7796S`, non-touch)** + `2× EC11` encoders + `6` tactile keys
- **Calibration from day one (`PROJECTS.md`):** `M24C64` EEPROM storing voltage, current, per-cell tap, and `1 kHz` AC IR magnitude/phase calibration coefficients + `CRC32`

## Architecture

```
230 V AC ─ IEC C14 (fuse + switch + PE) ─► Mean Well LRS-150-24 (24 V / 6.5 A)
   ├──► BQ25756 (4x BSC070N10NS5, 10 µH) ──► Charge Path ──┐
   └──► LMR36520 (12 V fan) ─► TPS54331 (5 V) ─► 3.3 V D/A │
                                                           ├──► TQ2-5V Isolate ─► XT60 + Kelvin 4W
2x IRFP250N + 50mΩ + 2x OPA2188 ─────────► Discharge Sink ─┘         ▲
                                                                     │ (Relay disconnects C_bulk during IR!)
AD9833 (1 kHz Sine) ─► AC-Coupled I_SRC ────────────────────► FORCE+/-
SENSE+/- (DC-block film caps) ─► INA826 ─► ADS1256 (24-bit) ◄── 1 kHz Sync Demod
Balance Header (JST-XH 7P) ─► BQ76952 (6S Monitor / Balance) ── I2C ──► STM32G431CBT6
                                                                         ├── SPI ─► ADS1256, AD9833
                                                                         ├── I2C ─► M24C64, BQ25756
                                                                         ├── 2x15 ─► ST7796S 3.5" + UI
                                                                         └── ISO7741 + CH343P ─► USB-C
```

- **Why relay-disconnect (`TQ2-5V`) the charger and load during `1 kHz` AC IR:** `BQ25756`'s output ceramic/electrolytic capacitor bank has `~10–30 mΩ` ESR at `1 kHz` — in parallel with a `15 mΩ` 18650 cell, it would cut the measured IR reading in half! Opening the `TQ2-5V` relay disconnects the power stages completely during the `200 ms` `AD9833` `1 kHz` Kelvin measurement.
- **Why `BQ25756` + `BQ76952`:** shared directly with `powerbank/` (`powerbank` uses the exact same pair for `6S` Li-ion packs); `BQ25756` charges `1S` through `6S` seamlessly from `24 V` via 4-switch buck-boost, while `BQ76952` monitors individual cell taps and temperature during `2S–6S` cycling.
- **Why linear `2× IRFP250N` discharge instead of switching load:** a linear sink maintains accurate `0.1–10.0 A` discharge all the way down to `0.5 V` (`1S` deeply discharged cell) with zero current ripple corrupting the capacity curve.
- **Power budget:** `LRS-150-24` (`156 W`) covers `100 W` charging (`25.2 V @ 4 A` or `4.2 V @ 5 A`) plus `12 V` heatsink fan (`~5 W`) and control logic (`~1.5 W`).

## Enclosure & Mechanical
- **Outer shell:** `185 mm (W) × 165 mm (D) × 88 mm (H)` angled (`~15°`) shared family shell (`LRS-150-24` is `159 × 97 × 30 mm`, fitting horizontally in the lower chassis cavity beneath/behind the Mainboard with thermal standoff clearance).
- **Front Panel (`168 × 72 mm`):** `3.5"` `480×320` IPS TFT, `2× EC11`, `6` keys (`IR TEST`, `CHG`, `DSG`, `CYCLE`, `CELLS`, `START/STOP`), front `XT60` + `JST-XH 7P` balance socket + `4× 4 mm` banana sockets for 4-wire Kelvin probes (`FORCE+`, `SENSE+`, `SENSE-`, `FORCE-`).

## Components (BOM v1)

JLC prices / stock checked on `2026-11-19` (qty 1–9).

### Power, Charger & Discharger
| What | Part | LCSC | Package | Stock | Price | Qty | Type |
|---|---|---|---|---|---|---|---|
| 1S–6S charger | **BQ25756RRVR** | C19272232 | VQFN-36 (5×6) | 3347 | $4.89 | 1 | extended |
| buck-boost FETs | **BSC070N10NS5** | C534364 | TDSON-8 (5×6) | 20466 | $0.57 | 4 | extended |
| charger inductor | **TMPC1265HP-100MG-D** (10 µH) | C305223 | SMD 13.5×12.5 | 4597 | $0.72 | 1 | extended |
| chg shunts (5 mΩ) | **LR2512-22R005F4** | C108931 | 2512 | 18806 | $0.13 | 2 | extended |
| 6S tap monitor/BMS | **BQ76952PFBR** | C2862742 | TQFP-48 | 11670 | $2.99 | 1 | extended |
| linear discharge FETs | **IRFP250N** | C20624228 | TO-247 | 495 | $0.82 | 2 | extended |
| discharge shunts (50 mΩ) | **WSL2512R0500FEA** | C413486 | 2512 | 37174 | $0.20 | 2 | extended |
| zero-drift loop amp | **OPA2188AIDR** | C17271 | SOIC-8 | 39831 | $0.96 | 2 | extended |
| 24 V → 12 V aux buck | **LMR36520ADDAR** | C2879422 | SO-8-EP | 2430 | $1.21 | 1 | extended |
| 12 V → 5 V buck | **TPS54331DR** | C9865 | SOIC-8 | 346905 | $0.29 | 1 | extended |
| 3.3 V D/A LDOs | **AMS1117-3.3** / **LP5907MFX-3.3** | C6186 / C5370990 | SOT-223 / SOT-23-5 | >176k | $0.20 / $0.10 | 1+1 | basic / ext |

### 1 kHz AC IR & Precision Readback
| What | Part | LCSC | Package | Stock | Price | Qty | Type |
|---|---|---|---|---|---|---|---|
| 1 kHz sine DDS | **AD9833BRMZ-REEL7** | C9652 | MSOP-10 | 1359 | $11.25 | 1 | extended |
| Kelvin IR inst-amp | **INA826AIDR** | C38433 | SOIC-8 | 19102 | $1.38 | 1 | extended |
| IR isolation relays | **TQ2-5V** | C46047 | DIP | 25565 | $1.20 | 2 | extended |
| 24-bit ADC | **ADS1256IDBR** | C28186 | SSOP-28 | 5206 | $5.71 | 1 | extended |
| 2.5 V ref | **REF5025AIDR** | C11341 | SOIC-8 | 22708 | $0.91 | 1 | extended |
| NTC thermistors | **NCP18XH103F03RB** | C13564 | 0603 | 255884 | $0.05 | 3 | extended |

### Control, Isolation & UI
| What | Part | LCSC | Package | Stock | Price | Qty | Type |
|---|---|---|---|---|---|---|---|
| MCU | **STM32G431CBT6** | C529355 | LQFP-48 | 5152 | $4.77 | 1 | extended |
| 25 MHz crystal | **XXCEELNANF-25MHZ** | C117869 | SMD3225-4P | 4002 | $0.15 | 1 | extended |
| cal EEPROM | **M24C64-RMN6TP** | C79988 | SOIC-8 | 92991 | $0.17 | 1 | extended |
| USB-UART / isolator | **CH343P** / **ISO7741DWR** / **B0505S-1WR3** | C2846043 / C571196 / C497204 | TQFN / SOIC / SIP | >34 | $3.55 | 1 | extended |
| USB-C / ESD | **TYPE-C-31-M-12** + **USBLC6-2SC6** | C165948 / C7519 | SMD / SOT-23-6 | >30k | $0.35 | 1 | extended |
| IO / glue diodes | **74HC595D** / **SS14** / **B5819W** / **BAV99** | C5947 / C2480 / C8598 / C2500 | SO-16 / SMA / SOT23 | >316k | ~$0.25 | 8 | **basic** |
| encoders / keys / display | **EC11E18244AU** (×2), **K2-1102SP** (×6), **FH12-40S**, **2×15** | C202365 / C83916 / C202114 / C5337168 | THT / SMD | >1100 | $6.61 | 1 set | extended |

### External / Mechanical (non-LCSC)
| What | Part | Source | Price | Qty | Notes |
|---|---|---|---|---|---|
| 24 V / 6.5 A AC-DC | **Mean Well LRS-150-24** | TME / DigiKey | ~$15 | 1 | `159 × 97 × 30 mm` |
| shared display | **3.5" 480×320 IPS TFT (`ST7796S`)** | AliExpress | ~$7 | 1 | Non-touch |
| Kelvin clips / heatsink | 4-wire Kelvin probe clips, heatsink + 60 mm fan, XT60, JST-XH 7P, IEC C14 | AliExpress / TME | ~$18 | 1 | For 1S–6S cells & packs |

## Who solders what

### JLC (assembly) — ~9 extended types (~$27 fees)
`BQ25756RRVR`, `BSC070N10NS5` (×4), `TMPC1265HP-100MG-D`, `LR2512-22R005F4` (×2), `WSL2512R0500FEA` (×2), `LMR36520ADDAR`, `XXCEELNANF-25MHZ`, `CH343P`, `NCP18XH103F03RB` (×3), plus `basic` (`AMS1117-3.3`, `74HC595D`, `SS14`, `B5819W`, `BAV99`, passives).

### Me (iron + flux)
`STM32G431CBT6`, `BQ76952PFBR`, `ADS1256IDBR`, `AD9833BRMZ` (MSOP-10), `INA826`, `OPA2188`, `REF5025`, `M24C64`, `TPS54331`, `ISO7741DWR`, `FH12-40S`, `IRFP250N` (×2 TO-247), `TQ2-5V`, `B0505S`, `EC11` (×2), `2×15` header.

## Cost estimate (`2026-11-19`, to re-check when ordering)

LCSC/JLC board parts per unit (qty 1–9): **~$58**

Prototype batch (5× 4-layer Mainboards, 2 assembled at JLC; 5× 2-layer Front Panel bare):
| What | ~$ |
|---|---|
| 4-layer Mainboard ×5 + 2-layer Front Panel ×5 | 35 |
| PCBA setup + stencil | 10 |
| extended fees (~9 × $3) | 27 |
| LCSC parts for 2 boards | 116 |
| shipping to RO | 16 |
| VAT 21% | 43 |
| **total (PCBs + PCBA + LCSC)** | **~247 (~1,135 lei)** |

External per unit: `LRS-150-24` (~$15), 3.5" IPS TFT (~$7), heatsink/fan/Kelvin clips/XT60/IEC (~$18) = **~$40 (~185 lei)**.

## Design notes
- **AC-coupling film caps for `1 kHz` IR:** use `1 µF – 10 µF` `50 V` polypropylene/X7R (with low DC leakage) on `FORCE+/-` and `SENSE+/-` so connecting a `25.2 V` `6S` pack never feeds DC into `AD9833` or `INA826`, and clamp `INA826` inputs with series resistors + `BAV99` against capacitor charging transients when plugging in a pack!
- **Reverse cell protection:** verify `BQ76952` `VC` input protection resistors and pre-check polarity via `ADS1256` before closing `TQ2-5V` or enabling `BQ25756`/`IRFP250N`.
- **Test pads:** `24V_IN`, `VBAT_DUT`, `1KHZ_EXC`, `INA826_OUT`, `V_REF_2V5`, `BQ_INT`, `SWD`.

## Status (`2026-11-19`)

Done:
- [x] Requirements & architecture defined (`1S–6S`, `1 kHz` 4W AC IR + `BQ25756` charge + `100 W` linear discharge)
- [x] BOM v1 verified live on JLCPCB/LCSC (`2026-11-19`)
- [x] `35/35` datasheets saved in `datasheets/`
- [x] KiCad library generated in `lib/` via `easyeda2kicad`

Next:
- [ ] Verify `AD9833` + `INA826` + `ADS1256` synchronous 1 kHz demodulation math & film-cap settling time
- [ ] Safety Wave 0 mains wiring check (`LRS-150-24` + Li-ion cell fuse/protection)
- [ ] Hierarchical schematic sheets (`mains_aux`, `charger_bq25756`, `discharge_sink`, `ir_1khz`, `bms_taps`, `mcu_iso`, `front_panel`)

## Schematic
`battery_tester.kicad_sch`

## Software
`code.md`

## Tests
1. **Safety Wave 0:** PE continuity `< 0.1 Ω` on `LRS-150-24` chassis; verify `15 A` fuse on `XT60` battery port.
2. **1 kHz AC IR precision check:** measure precision `10 mΩ`, `50 mΩ`, `100 mΩ`, `1 Ω` four-terminal shunts and compare against `YR1035+`; verify `< 0.3 mΩ` repeatability even with `0 V` vs `25.2 V` DC bias superimposed.
3. **Charge / Discharge calibration:** calibrate `BQ25756` charge current & `IRFP250N` discharge current against `5.5-digit multimeter`; test full automatic cycle on an `EVE ICR18650/26V` cell from `powerbank/`.

## Resources
- Datasheets: `datasheets/` (all 35 LCSC parts)
- TI BQ25756 & BQ76952: https://www.ti.com/product/BQ25756
- Repo: https://github.com/stefanVanadium/battery-tester

## KiCad libraries
- `lib/battery_tester.kicad_sym` + `lib/battery_tester.pretty` + `lib/battery_tester.3dshapes`, registered in `sym-lib-table` / `fp-lib-table`
- Generated with `easyeda2kicad --full --lcsc_id Cxxxx --output $PWD/lib/battery_tester --project-relative`
