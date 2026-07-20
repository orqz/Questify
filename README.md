<p align="center"> 
  <img 
    src="https://i.pinimg.com/originals/b6/07/6b/b6076bb4df9a3532e01ad33b4e563643.jpg"
    style="width:1000px; height:250px; object-fit:cover;"
  >
</p>

<h1 align="center">Questify</h1>

<p align="center">
  Easily complete Quest on discord without downloading or owning any games!<br>
  (<3)
</p>

<!-- Badges -->
<p align="center">
  <img src="https://img.shields.io/github/v/release/orqz/questify?style=for-the-badge&cacheSeconds=3600">
  <img src="https://img.shields.io/github/downloads/orqz/questify/total?style=for-the-badge&cacheSeconds=86400&v=2">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge">
</p>



---

## About

Questify is a simple Python tool that generates a custom `.exe`
with a matching folder name so Discord detects it as a running game.

---

## Features

- creates an exe
- creates the folder
- auto-launches and starts a timer
- press 7 to reset (moves exe to a new path and relaunches)
- what else do u expect?

---

## Warning

> **Important**
> The executable must be named `questify.exe`.
> Any other name will cause the program to not work correctly.


---

## Installation

### Download (recommended)

Download the latest ready-to-use `.exe` from [Releases](https://github.com/orqz/questify/releases):

No setup required. Just download and run.

---

### Don't trust the `.exe`? (fair i wouldnt either)

You can compile the source yourself using Nuitka (recommended) or PyInstaller.

### Option A — Nuitka (recommended, less antivirus false positives)

```bash
pip install nuitka requests
```

```bash
python -m nuitka --onefile --output-filename=questify.exe questify.py
```

### Option B — PyInstaller

```bash
pip install requests pyinstaller
```

```bash
pyinstaller --onefile questify.py
```

### Done

Your compiled file will be in the output folder. Rename it to `questify.exe` if needed and run it.
