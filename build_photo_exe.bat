@echo off
REM ---------------------------------------------------------------------------
REM  Build PythonPhotoAlbum.exe with PyInstaller.
REM
REM  Keep these three files in one folder, then double-click this .bat:
REM      PythonPhotoAlbum.py
REM      txt_studio.ico
REM      build_exe.bat
REM
REM  Result:  dist\PythonPhotoAlbum.exe  - runs on any Windows PC, no Python needed.
REM  For a folder build instead of one file, run:  build_exe.bat dir
REM ---------------------------------------------------------------------------
setlocal
cd /d "%~dp0"

REM  --onefile = a single .exe (slower start, more antivirus false positives)
REM  --onedir  = a folder containing the .exe (faster start, fewer flags)
set MODE=--onefile
if /I "%~1"=="dir" set MODE=--onedir

set ICON=
if exist "txt_studio.ico" set ICON=--icon "txt_studio.ico"

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo Python was not found on PATH.
    echo Install it from https://www.python.org/downloads/windows/ and tick
    echo "Add python.exe to PATH" during setup, then run this file again.
    echo.
    pause
    exit /b 1
)

if not exist "PythonPhotoAlbum.py" (
    echo.
    echo PythonPhotoAlbum.py is not in this folder: %CD%
    echo Put this .bat next to PythonPhotoAlbum.py and try again.
    echo.
    pause
    exit /b 1
)

echo Checking PyInstaller...
python -m pip install --upgrade --quiet pyinstaller
if errorlevel 1 goto failed

echo.
echo Building %MODE% - this takes a minute or two...
echo.
python -m PyInstaller --noconfirm --clean --noconsole --name PythonPhotoAlbum %MODE% %ICON% PythonPhotoAlbum.py
if errorlevel 1 goto failed

echo.
echo Build finished.
if /I "%MODE%"=="--onedir" (
    echo Your program: %CD%\dist\txt_studio\PythonPhotoAlbum.exe
    echo Copy the whole dist\PythonPhotoAlbum folder.
) else (
    echo Your program: %CD%\dist\PythonPhotoAlbum.exe
    echo Copy that single file.
)
echo.
echo Python is not needed on the PC that runs it.
echo.
pause
exit /b 0

:failed
echo.
echo The build failed - scroll up for the error message.
echo If pip was the problem, try:  python -m pip install --user pyinstaller
echo.
pause
exit /b 1
