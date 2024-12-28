@echo off

pip install -r "Install Folder/requirements.txt"
mkdir Scripts
echo Local IP - 127.0.0.1 > "Local IP - 127.0.0.1.txt"

set "batch_folder=%~dp0"
set "batch_file=%~f0"

set "source=%batch_folder%Install Folder"
xcopy "%source%\*" "%batch_folder%" /E /H /C /I
echo Les fichiers ont été copiés dans le dossier du script batch.
if exist "%batch_folder%requirements.txt" (
    del "%batch_folder%requirements.txt"
    echo requirements.txt a été supprimé.
)
rd /s /q "%batch_folder%Install Folder"

@echo off

:: Définir le chemin relatif vers la cible, le raccourci et l'icône
set cible=%~dp0py\start.bat
set raccourci=%~dp0NSMW TAS.lnk
set icone=%~dp0img\wonder-flower-ico.ico
set dossier_de_demarrage=%~dp0py

:: Créer le fichier VBScript pour créer le raccourci
echo Set WshShell = WScript.CreateObject("WScript.Shell") > create_shortcut.vbs
echo Set shortcut = WshShell.CreateShortcut("%raccourci%") >> create_shortcut.vbs
echo shortcut.TargetPath = "%cible%" >> create_shortcut.vbs
echo shortcut.IconLocation = "%icone%" >> create_shortcut.vbs
echo shortcut.WorkingDirectory = "%dossier_de_demarrage%" >> create_shortcut.vbs
echo shortcut.Save >> create_shortcut.vbs

:: Exécuter le script VBScript pour créer le raccourci
cscript //nologo create_shortcut.vbs

:: Supprimer le script VBScript après utilisation
del create_shortcut.vbs

echo Raccourci "NSMW TAS" créé avec l'icône et démarrant dans le dossier py !

del /f /q "%batch_file%" > nul 2>&1
exit
