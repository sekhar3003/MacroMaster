MacroMaster
<div align="center">
A lightweight, always-on-top Windows macro tool for automating mouse actions.  
Record, replay, and loop click sequences with precise control over timing and movement.
![Release](https://img.shields.io/github/v/release/sekhar3003/MacroMaster?style=flat-square&color=2dd4bf)
![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
Download Latest · Report Bug · Request Feature
</div>
---
What is MacroMaster?
MacroMaster is a compact overlay tool that sits on top of any application and lets you automate repetitive mouse actions. It supports recording real mouse input, replaying it with smooth movement, looping sequences, and fine-tuning individual actions — all from a minimal, always-visible interface.
---

Features
Record real mouse input live — clicks, right-clicks, drags, and holds
Smooth mouse movement — natural easing so it looks human
Per-action timing — set a delay before each individual action
Action types — Click, Right-click, Middle-click, Drag, Hold, Wait
Loop playback — repeat a sequence any number of times or forever
Import / Export — save macros as JSON and reload them later
System tray — minimise to tray and keep running in the background
Always on top — overlay stays visible over any app
Global hotkeys — F6 (record), F7 (stop), F8 (play) work in any window
Single EXE — no installation, no dependencies, just run it
---

Download
> **Quickest way: just download the EXE.**
Go to Releases
Download `MacroMaster.exe`
Double-click to run — no install needed
---

How to Use
Basic workflow
```
1. Open MacroMaster (stays on top of your other apps)
2. Click Record (or press F6) → perform your clicks
3. Click Stop (or press F7) when done
4. Click Play (or press F8) to replay
```

Hotkeys
Key	Action
`F6`	Start / Stop recording
`F7`	Stop playback or recording
`F8`	Play current macro
Adding actions manually
Click + Add in the Actions section
Choose action type (Click, Drag, Hold, etc.)
Set X/Y position — type it or click Pick to capture from screen
Set delay (seconds before this action fires)
Click Save
Saving and loading macros
Click Export to save your sequence as a `.json` file
Click Import to load a previously saved macro
JSON files can be shared or backed up
---

Action Types
Type	What it does
`click`	Left-click at position
`right_click`	Right-click at position
`middle_click`	Middle-click at position
`drag`	Click and drag from (X,Y) to (X2,Y2)
`hold`	Press and hold button for a set duration
`delay`	Pause for a set number of seconds
---
Building from Source
If you want to build the EXE yourself:
Requirements
```
Python 3.8 or higher
```

Steps
```bash
# 1. Clone the repo
git clone https://github.com/sekhar3003/MacroMaster.git
cd MacroMaster

# 2. Install dependencies
pip install pynput pystray Pillow pyinstaller

# 3. Run the builder
BUILD_EXE.bat
```

The `MacroMaster.exe` will appear in the root folder when done.
Running without building
```bash
pip install pynput pystray Pillow
python macro_master.pyw
```
---
Requirements
Windows 10 or 11 (64-bit)
No installation required for the EXE
---

FAQ
Does it work in games?  
It uses standard Windows input (`SendInput`) which works in most applications. Kernel-level anti-cheats (e.g. Vanguard) may detect it.
Why does it need admin rights sometimes?  
Global hotkeys (F6/F7/F8) may require elevated permissions on some systems. Right-click the EXE → Run as Administrator if hotkeys aren't responding.
My antivirus flagged it — is it safe?  
Automation tools that simulate input are sometimes flagged by heuristic scanners. The full source code is in this repo — you can review it and build it yourself.
Can I run multiple macros?  
One macro sequence at a time. Use the JSON export/import to switch between saved macros.
---

License
MIT License — see LICENSE for details.
---
<div align="center">
Made for automating the boring stuff.
</div>
