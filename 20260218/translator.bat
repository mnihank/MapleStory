@echo off
:: 切換到 Anaconda 安裝目錄 (視你的安裝位置而定)
call C:\Users\09192\AppData\Local\Python\.forLearning\Scripts\activate.bat OCR

:: 執行 Python 腳本
python GUI_control.py

:: 保持視窗開啟以查看輸出
pause