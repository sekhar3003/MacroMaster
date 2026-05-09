@echo off
cd /d "%~dp0"
title MacroMaster Builder
color 0A
cls
echo.
echo   ============================================
echo    MacroMaster v3.1  ^|  Building EXE...
echo   ============================================
echo.

:: ── Python check ─────────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Python not found.
    echo   Download it from https://python.org
    echo   Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo   [OK] Python found.

:: ── PyInstaller ───────────────────────────────────────────────────────────────
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo   Installing PyInstaller...
    python -m pip install --quiet pyinstaller
    if errorlevel 1 (
        echo   [ERROR] Failed to install PyInstaller.
        pause
        exit /b 1
    )
)
echo   [OK] PyInstaller ready.

:: ── Dependencies ─────────────────────────────────────────────────────────────
python -c "import pynput" >nul 2>&1
if errorlevel 1 (
    echo   Installing pynput...
    python -m pip install --quiet pynput
)

python -c "import pystray" >nul 2>&1
if errorlevel 1 (
    echo   Installing pystray...
    python -m pip install --quiet pystray
)

python -c "from PIL import Image" >nul 2>&1
if errorlevel 1 (
    echo   Installing Pillow...
    python -m pip install --quiet Pillow
)
echo   [OK] All dependencies ready.

:: ── Clean previous build ─────────────────────────────────────────────────────
if exist "build"           rmdir /s /q "build"
if exist "dist"            rmdir /s /q "dist"
if exist "MacroMaster.spec" del /f /q "MacroMaster.spec"
echo   [OK] Cleaned previous build.

:: ── Build ────────────────────────────────────────────────────────────────────
echo.
echo   Building... (this takes 30-60 seconds)
echo   ============================================
echo.

pyinstaller --onefile --noconsole ^
    --name "MacroMaster" ^
    --icon "icon.ico" ^
    --add-data "icon.ico;." ^
    --hidden-import "pynput.keyboard._win32" ^
    --hidden-import "pynput.mouse._win32" ^
    --hidden-import "pystray._win32" ^
    --collect-all "pynput" ^
    --clean ^
    "macro_master.pyw"

if errorlevel 1 (
    echo.
    echo   [ERROR] Build failed. Check output above for errors.
    pause
    exit /b 1
)

:: ── Copy to root ──────────────────────────────────────────────────────────────
if exist "dist\MacroMaster.exe" (
    copy /y "dist\MacroMaster.exe" "MacroMaster.exe" >nul
    echo.
    echo   ============================================
    echo   [DONE] MacroMaster.exe is ready!
    echo   ============================================
    echo.
    for %%F in ("MacroMaster.exe") do echo   Size: %%~zF bytes
    echo.
    echo   You can now:
    echo    1. Double-click MacroMaster.exe to run it
    echo    2. Upload MacroMaster.exe to GitHub Releases
    echo.
) else (
    echo   [ERROR] EXE not found in dist folder.
)

pause
