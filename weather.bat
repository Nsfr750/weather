python -m nuitka ^
--onefile ^
--plugin-enable=tk-inter ^
--windows-console-mode=disable ^
--windows-icon-from-ico=icon.ico ^
weather_app.py
pause
ren weather_app.exe Weather.exe