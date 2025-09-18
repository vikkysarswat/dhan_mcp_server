@echo off
REM Dhan MCP Server Run Script
REM Send banners to stderr so they don't break MCP JSON
>&2 echo Dhan MCP Server
>&2 echo ================================

setlocal enabledelayedexpansion

REM Ensure we're in the correct directory
cd /d "D:\Python_projects\Dhan_mcp_server"

REM Activate virtual environment
call .venv\Scripts\activate

REM Check if .env file exists
if not exist ".env" (
    if not exist ".env.example" (
        >&2 echo Error: Neither .env nor .env.example found
        exit /b 1
    )
    >&2 echo Creating .env file from .env.example...
    copy ".env.example" ".env" >nul
    >&2 echo Please edit .env file with your Dhan API credentials
    exit /b 1
)

REM Load variables from .env
for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
    if not "%%a"=="" (
        set "%%a=%%b"
    )
)

REM Check if DHAN_ACCESS_TOKEN is set
if "%DHAN_ACCESS_TOKEN%"=="" (
    >&2 echo Error: Please set DHAN_ACCESS_TOKEN in .env file
    exit /b 1
)

if "%DHAN_ACCESS_TOKEN%"=="your-dhan-access-token-here" (
    >&2 echo Error: Please set DHAN_ACCESS_TOKEN in .env file
    exit /b 1
)

>&2 echo Configuration loaded
>&2 echo Access Token: %DHAN_ACCESS_TOKEN:~0,10%***
>&2 echo Starting Dhan MCP Server...
>&2 echo Press Ctrl+C to stop
>&2 echo.

REM Start the server using the activated virtual environment's Python
python -m dhan_mcp_server.server