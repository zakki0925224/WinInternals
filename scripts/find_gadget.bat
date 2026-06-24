@echo off
setlocal

set RP_PATH=rp-win.exe
set MAX_DEPTH=6
set DLL_PATH=%~1
set KEYWORD=%~2

if "%DLL_PATH%"=="" (
    echo Usage: find_gadget.bat "C:\path\to\image.dll" ["keyword"]
    exit /b 1
)

if "%KEYWORD%"=="" (
    for %%k in ("pop rcx" "pop rdx" "pop r8" "pop r9") do (
        echo.
        echo [*] Searching for "%%~k" ...
        call :search "%DLL_PATH%" "%%~k"
    )
    exit /b 0
)

call :search "%DLL_PATH%" "%KEYWORD%"
exit /b 0

:search
set _DLL=%~1
set _KW=%~2
for /L %%d in (1,1,%MAX_DEPTH%) do (
    echo [*] Searching with -r %%d ...
    %RP_PATH% --print-bytes --unique -r %%d -f "%_DLL%" | findstr /c:"%_KW%" > tmp_result.txt
    for %%s in (tmp_result.txt) do if %%~zs gtr 0 (
        echo [+] Found with -r %%d
        type tmp_result.txt
        del tmp_result.txt
        exit /b 0
    )
)
echo [-] Not found up to -r %MAX_DEPTH%
del tmp_result.txt 2>nul
exit /b 0
