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
| text archive validation | PASS | 47 archives passed |
| Build readiness | WARN | missing requirements: docker |

## Tool Availability

- `git`: available at C:\msys64\usr\bin\git.EXE
- `make`: available at C:\msys64\usr\bin\make.EXE
- `cmake`: available at C:\msys64\ucrt64\bin\cmake.EXE
- `armips`: available at C:\Users\jimmy\Documents\pokemon_romhacks\perfect_johto\hg-engine-main\hg-engine-main\tools\armips.EXE
- `docker`: missing on PATH
- `arm-none-eabi-gcc`: available at C:\msys64\ucrt64\bin\arm-none-eabi-gcc.EXE
- `python`: available at C:\Users\jimmy\AppData\Local\Programs\Python\Python312\python.exe

## ROM Inputs

- `hg-engine-main/hg-engine-main/rom.nds`: present.
- `pokeheartgold-master/baserom.nds`: missing.

Do not commit or redistribute `rom.nds`, `baserom.nds`, pre-patched ROMs, or copyrighted ROM data.

## Recommended Build Routes

- Docker route: install Docker Desktop, then run `docker build . -t hg-engine` from `hg-engine-main/hg-engine-main`, followed by `docker-makerom.cmd`.
- Native route: install Git, GNU Make, CMake, Python 3, `armips`, and the ARM toolchain expected by HG-Engine. WSL or MSYS2 is recommended over raw PowerShell for native Makefile use.
- `make -n` status: echo "Done.  See output test.nds.".
- Dojo `armips` assembly status: completed.
