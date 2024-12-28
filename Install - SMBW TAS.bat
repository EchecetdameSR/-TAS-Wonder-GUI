@echo off

pip install -r Install Folder\requirements.txt
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
echo Le fichier batch va maintenant s'autodétruire.

del /f /q "%batch_file%" > nul 2>&1
exit