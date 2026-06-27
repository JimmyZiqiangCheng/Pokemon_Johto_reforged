# Build And Testing

## Static Validation

Run from the repository root:

```powershell
python tools/perfect_johto/validate_project.py
```

To regenerate static exports and documentation:

```powershell
python tools/perfect_johto/validate_project.py --write
```

## Current Build Readiness

| Check | Status | Details |
| --- | --- | --- |
| Learnset JSON parse | PASS | data/learnsets/learnsets.json parsed |
| text archive validation | PASS | 46 archives passed |
| Build readiness | WARN | missing requirements: git, make, cmake, armips, docker, arm-none-eabi-gcc, rom.nds |

## Tool Availability

- `git`: missing on PATH
- `make`: missing on PATH
- `cmake`: missing on PATH
- `armips`: missing on PATH
- `docker`: missing on PATH
- `arm-none-eabi-gcc`: missing on PATH
- `python`: available at C:\Users\jimmy\AppData\Local\Programs\Python\Python312\python.exe

## ROM Inputs

- `hg-engine-main/hg-engine-main/rom.nds`: missing.
- `pokeheartgold-master/baserom.nds`: missing.

Do not commit or redistribute `rom.nds`, `baserom.nds`, pre-patched ROMs, or copyrighted ROM data.

## Recommended Build Routes

- Docker route: install Docker Desktop, then run `docker build . -t hg-engine` from `hg-engine-main/hg-engine-main`, followed by `docker-makerom.cmd`.
- Native route: install Git, GNU Make, CMake, Python 3, `armips`, and the ARM toolchain expected by HG-Engine. WSL or MSYS2 is recommended over raw PowerShell for native Makefile use.
- `make -n` status: make is not available on PATH.
- Dojo `armips` assembly status: armips is not available on PATH.
