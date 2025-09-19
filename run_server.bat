@echo off
REM Dhan MCP Server Run Script

echo Dhan MCP Server
echo ================================

REM Check if .env file exists
if not exist .env (
    if not exist .env.example (
        echo Error: Neither .env nor .env.example found
        exit /b 1
    )
    echo Creating .env file from .env.example...
    copy .env.example .env >nul
    echo Please edit .env file with your Dhan API credentials
    exit /b 1
)

REM Simple environment variable loading for Windows
for /f "usebackq delims=" %%a in (".env") do (
    for /f "tokens=1,2 delims==" %%b in ("%%a") do (
        if not "%%b"=="" if not "%%c"=="" set "%%b=%%c"
    )
)

REM Check if DHAN_ACCESS_TOKEN is set
if "%DHAN_ACCESS_TOKEN%"=="" (
    echo Error: Please set DHAN_ACCESS_TOKEN in .env file
    echo Get your token from: https://web.dhan.co
    exit /b 1
)

if "%DHAN_ACCESS_TOKEN%"=="your-dhan-access-token-here" (
    echo Error: Please set DHAN_ACCESS_TOKEN in .env file
    echo Get your token from: https://web.dhan.co
    exit /b 1
)

echo Configuration loaded
echo Access Token: %DHAN_ACCESS_TOKEN:~0,10%***
echo.
echo Starting Dhan MCP Server...
echo Press Ctrl+C to stop
echo.

REM Start the server
uv run python -m dhan_mcp_server.server
