@echo off
REM 激活conda环境并运行服务器
call conda activate travel
cd /d "%~dp0"
python main.py
pause
