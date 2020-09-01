@echo off
echo check game whether started ...
:again
netstat -aon|findstr 8000
if ERRORLEVEL 1 (
    echo not started, try again ...
    timeout /t 3
    goto again
) else (
    echo already started
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --chrome --kiosk http://localhost:8000 --disable-pinch --no-user-gesture-required --overscroll-history-navigation=0
)
exit