@echo off
color 0a

echo ========================================
echo           ScayNum by Scayar
echo ========================================
echo.

:: Check if venv folder already exists
if not exist venv (
    echo Creating virtual environment...
    :: For Windows
    python -m venv venv
    venv\Scripts\activate
) else (
    echo Virtual environment found, activating...
    :: For Linux and MacOS
    python3 -m venv venv
    source venv/bin/activate
)

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

:: Run the script
echo Starting ScayNum...
python main.py

:: Pause to keep the command prompt open
echo.
echo Press any key to exit...
pause 