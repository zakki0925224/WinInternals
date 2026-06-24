@echo off
setlocal

:: Find Visual Studio via vswhere
for /f "usebackq delims=" %%i in (
    `"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`
) do set VS_PATH=%%i

if not defined VS_PATH (
    echo [!] Visual Studio not found
    exit /b 1
)

if exist build rmdir /s /q build

:: Build x86
call "%VS_PATH%\VC\Auxiliary\Build\vcvarsall.bat" x86
cmake --preset x86-debug
if errorlevel 1 exit /b 1
cmake --build build\x86-debug
if errorlevel 1 exit /b 1

:: Build x64
call "%VS_PATH%\VC\Auxiliary\Build\vcvarsall.bat" x64
cmake --preset x64-debug
if errorlevel 1 exit /b 1
cmake --build build\x64-debug
if errorlevel 1 exit /b 1

python deploy.py --preset x86-debug x64-debug
