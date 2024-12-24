pip install -r requirements.txt

IF %ERRORLEVEL% NEQ 0 (
    echo .
    pause
    exit /b
)

REM Création du fichier LaunchGUI.bat
echo start python WonderGUI.py >> LaunchGUI.bat

del /f /q "%~f0"

REM Fin
exit
