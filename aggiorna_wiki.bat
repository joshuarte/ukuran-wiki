@echo off
SETLOCAL EnableDelayedExpansion

:: --- CONFIGURAZIONE ---
SET "SOURCE_DIR=c:\Users\joshu\Desktop\ukuran-wiki"
SET "SITE_DIR=%SOURCE_DIR%\quartz-site"
SET "CONTENT_DIR=%SITE_DIR%\content"

echo --------------------------------------------------
echo 🚀 UKURAN WIKI - SINCRONIZZAZIONE E AGGIORNAMENTO
echo --------------------------------------------------

:: 1. Pulizia e Sincronizzazione file
echo [1/3] Sincronizzazione file da Obsidian...
:: Copia tutte le cartelle numerate e gli allegati, escludendo file di sistema e la cartella del sito stessa
robocopy "%SOURCE_DIR%" "%CONTENT_DIR%" /E /Z /PURGE /XD .git .obsidian .smart-env quartz-site /XF *.py *.bat *.sh .DS_Store /R:2 /W:5 /MT:8

:: 2. Build del sito
echo.
echo [2/3] Generazione sito con Quartz...
cd /d "%SITE_DIR%"
call npx quartz build

:: 3. Fine
echo.
echo [3/3] Operazione completata!
echo.
echo 👉 Il sito e pronto nella cartella: %SITE_DIR%\public
echo 👉 Puoi fare il PUSH su GitHub per aggiornare la versione online.
echo.
pause
