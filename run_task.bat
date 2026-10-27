@echo off
setlocal

REM Ensure we run inside the project folder where this .bat file is located
cd /d "%~dp0"

REM Use the first argument as the markdown file if provided, otherwise default to prompt.md
set "MD_FILE=%~1"
if "%MD_FILE%"=="" set "MD_FILE=prompt.md"

if not exist "%MD_FILE%" (
    echo [ERROR] Instruction file "%MD_FILE%" not found in %CD%
    exit /b 1
)

REM Locate agy executable (use full path if available, otherwise fallback to PATH)
set "AGY_EXE=C:\Users\micha\AppData\Local\agy\bin\agy.exe"
if not exist "%AGY_EXE%" (
    set "AGY_EXE=agy"
)

echo ===================================================
echo Running Antigravity Unattended Task
echo Working Directory : %CD%
echo Instruction File  : %MD_FILE%
echo ===================================================

"%AGY_EXE%" -p "Read the file '%MD_FILE%' in the current directory and execute all instructions inside it completely. Do not ask for confirmation; complete all file creation and verification steps and then finish." --dangerously-skip-permissions --output-format stream-json

echo ===================================================
echo Finished with exit code: %ERRORLEVEL%
echo ===================================================
endlocal
