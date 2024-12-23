pip install -r requirements.txt

IF %ERRORLEVEL% NEQ 0 (
    echo L'installation des dépendances a échoué. Veuillez vérifier les erreurs ci-dessus.
    pause
    exit /b
)

REM Création du fichier Launch.bat
echo start python WonderGUI.py >> Launch.bat

del /f /q "%~f0"

REM Fin
exit
