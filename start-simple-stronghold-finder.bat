@echo off

:: py-file needs to be in same folder as this batch file
wt.exe -w new --size 70,15 cmd /k "cd /d ""%~dp0"" && python simple-stronghold-finder.py & pause"
