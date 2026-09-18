@echo off
title MD Fuar Takip - Windows Baslangicina Ekle
cd /d "%~dp0"

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\MDFuarTakipWeb.bat"

echo ========================================================
echo   MD FUAR TAKIP - WINDOWS OTOMATIK BASLATMA KURULUMU
echo ========================================================
echo.
echo Bu islem bilgisayar her acildiginda mobil web sunucusunu
echo otomatik olarak arka planda baslatacaktir.
echo.

(
echo @echo off
echo cd /d "%~dp0"
echo "C:\Users\ahmet\AppData\Local\Programs\Python\Python312\python.exe" web_app.py
) > "%SHORTCUT_PATH%"

echo [BASARILI] Otomatik baslatma kisayolu eklendi:
echo %SHORTCUT_PATH%
echo.
echo Artık bilgisayar her acildiginda telefonlar kesintisiz baglanabilir!
pause
