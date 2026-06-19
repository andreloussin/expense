@echo off

pyinstaller ^
--name expense-server ^
--clean ^
--onedir ^
--hidden-import=config.settings_desktop ^
--add-data "config;config" ^
--add-data "expenses;expenses" ^
server.py

pause