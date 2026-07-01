@echo off
cd /d "%~dp0"
streamlit run src\restaurant\dashboard.py --server.port 8502
