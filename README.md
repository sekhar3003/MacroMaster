MacroMaster
A lightweight Windows macro tool. Record mouse clicks, replay them automatically, and loop sequences — no installation needed.
![Download](https://img.shields.io/github/v/release/sekhar3003/MacroMaster?style=flat-square&label=Download&color=2dd4bf)
[![Platform](https://img.shields.io/badge/Windows-only-blue?style=flat-square)]()
---
Download
👉 Get MacroMaster.exe
Just download and double-click. No install required.
---
What it does
Records your mouse clicks in real time
Replays them with smooth, natural movement
Set custom delays between each action
Loop sequences any number of times
Supports clicks, right-clicks, drags, holds, and waits
Saves and loads macros as `.json` files
Sits on top of any window (always visible)
Minimises to system tray
---
How to use
Key	Action
`F6`	Start / Stop recording
`F7`	Stop
`F8`	Play
Press F6 → click wherever you want → press F7 to stop recording
Press F8 to replay
Use Export to save your macro, Import to load it later
---
Build it yourself
```bash
pip install pynput pystray Pillow pyinstaller
```
Then run `BUILD_EXE.bat` — the EXE will appear in the same folder.
---
Notes
Windows 10 / 11 only
If hotkeys don't work, run as Administrator
Antivirus may flag it — source code is fully visible here for review
