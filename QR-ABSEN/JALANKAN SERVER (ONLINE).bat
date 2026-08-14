@echo off
title QR Absen OKK (Mode Online Internet)
color 0A

echo.
echo  ====================================================
echo    QR ABSEN DINAMIS - OKK ETHIVATION (ANTI DROP)
echo    Universitas Dinamika Surabaya
echo  ====================================================
echo.
echo  Memulai sistem absensi...
echo.
cd /d "%~dp0"

python launcher_internet.py

pause
