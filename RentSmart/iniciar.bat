@echo off
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
  py -3 -m venv venv 2>nul || python -m venv venv
)
if not exist venv\Scripts\python.exe (
  echo Python 3 nao encontrado. Instale em https://www.python.org/downloads/ e marque "Add to PATH".
  pause
  exit /b 1
)
venv\Scripts\python.exe -m pip install -q -r requirements.txt
echo RentSmart em http://127.0.0.1:5000 ^(feche esta janela para encerrar^)
venv\Scripts\python.exe main.py
pause
