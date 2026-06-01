@echo off
setlocal

set RP_PATH=rp-win.exe
set DLL_PATH=C:\Windows\System32\ntdll.dll
set MAX_DEPTH=6
set KEYWORD=%~1

if "%KEYWORD%"=="" (
    echo Usage: find_gadget.bat "pop rcx"
    exit /b 1
)

for /L %%d in (1,1,%MAX_DEPTH%) do (
    echo [*] Searching with -r %%d ...
    %RP_PATH% --print-bytes --unique -r %%d -f %DLL_PATH% | findstr /c:"%KEYWORD%" > tmp_result.txt
    for %%s in (tmp_result.txt) do if %%~zs gtr 0 (
        echo [+] Found with -r %%d
        type tmp_result.txt
        del tmp_result.txt
        exit /b 0
    )
)

echo [-] Not found up to -r %MAX_DEPTH%
del tmp_result.txt 2>nul
exit /b 1