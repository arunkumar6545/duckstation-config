# DuckStation Config Backup

Backup of DuckStation PS1 emulator configuration on macOS.

## Files

- `settings.ini` — Main DuckStation settings (2 controllers configured)
- `settings.ini.backup` — Same backup copy
- `Tekken3_SLUS-00402.cht` — Tekken 3 (USA) cheat file with all cheats including "Absolutely Everything Unlocked"

## Controllers

- **Port 1:** Twin USB Joystick (SDL-0) — Digital Controller
- **Port 2:** Second joystick

## BIOS Location
`~/Games/BIOS/scph1001.bin`

## Games Location
`~/Games/PSX/`

## Restore Instructions

```bash
cp settings.ini ~/Library/Application\ Support/DuckStation/settings.ini
cp Tekken3_SLUS-00402.cht ~/Library/Application\ Support/DuckStation/cheats/SLUS-00402.cht
```
