@echo off
setlocal

echo --- Python Virtual Environment Manager ---

:PROMPT_NAME
set /p ENV_NAME="Enter the desired environment name: "

if "%ENV_NAME%"=="" goto PROMPT_NAME

echo.
echo Checking for environment: "%ENV_NAME%"

REM Check if the environment directory already exists
if exist "%ENV_NAME%\" (
    echo Found existing environment: **%ENV_NAME%**.
    call :ACTIVATE_ENV
) else (
    echo Environment "%ENV_NAME%" not found. Creating a new one...
    call :CREATE_ENV
)

REM --- The crucial change: Restart the shell to persist activation ---
REM The /k switch executes the command string (which is now empty) and keeps the window open.
echo.
echo ✅ Environment activated. You now have full control over the console.
cmd.exe /k

goto :EOF


:CREATE_ENV
    REM Use 'python -m venv' to create the environment
    python -m venv "%ENV_NAME%"
    
    REM Check the error code from the venv creation command
    if errorlevel 1 (
        echo.
        echo ❌ Error: Failed to create environment **%ENV_NAME%**.
        echo Please ensure 'python' is in your PATH.
        pause
        exit /b 1
    ) else (
        echo.
        echo 🎉 Environment **%ENV_NAME%** created successfully.
        call :ACTIVATE_ENV
    )
    exit /b 0

:ACTIVATE_ENV
    REM The 'call' command executes the activation script and returns control back.
    if exist "%ENV_NAME%\Scripts\activate.bat" (
        call "%ENV_NAME%\Scripts\activate.bat"
        echo.
    ) else (
        echo.
        echo ❌ Error: Cannot find the activation script for **%ENV_NAME%**.
        pause
        exit /b 1
    )
    exit /b 0