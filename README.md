# DuckStation Config Backup

Backup of DuckStation PS1 emulator configuration on macOS.

## Files

| File | Description |
|---|---|
| `settings.ini` | Digital Controller config (stable, no analog) |
| `settings.ini.backup` | Same as above — backup copy |
| `settings_analog.ini` | Analog Controller config (both pads, lever + D-Pad working) |
| `Tekken3_SLUS-00402.cht` | Tekken 3 (USA) cheat file — includes "Absolutely Everything Unlocked" |

## Controller Configs

### Digital (settings.ini / settings.ini.backup)
- **Port 1:** SDL-0 — DigitalController — D-Pad + face buttons
- **Port 2:** SDL-1 — DigitalController — D-Pad + face buttons

### Analog (settings_analog.ini) ✅ Currently Active
- **Port 1:** SDL-0 — AnalogController — D-Pad + face buttons + lever (Axis0/Axis1)
- **Port 2:** SDL-1 — AnalogController — D-Pad + face buttons + lever (Axis0/Axis1)
- No Analog toggle button mapped (prevents mode-switching popup)

## BIOS Location
`~/Games/BIOS/scph1001.bin`

## Games Location
`~/Games/PSX/`

## Restore Instructions

### Restore Digital config
```bash
cp settings.ini ~/Library/Application\ Support/DuckStation/settings.ini
```

### Restore Analog config
```bash
cp settings_analog.ini ~/Library/Application\ Support/DuckStation/settings.ini
```

### Restore Tekken 3 cheats
```bash
cp Tekken3_SLUS-00402.cht ~/Library/Application\ Support/DuckStation/cheats/SLUS-00402.cht
```
