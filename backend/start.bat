@echo off
echo ===============================================
echo  Starting Advanced Agentic RAG System
echo ===============================================
echo.

REM Set UTF-8 encoding
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Start the application
python start.py

pause