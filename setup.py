#!/usr/bin/env python3
"""
Setup script for Dhan MCP Server
Automated installation and configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_colored(message: str, color: str = Colors.OKGREEN) -> None:
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.ENDC}")


def print_header(message: str) -> None:
    """Print header with formatting"""
    print("\n" + "=" * 60)
    print_colored(f" {message} ", Colors.HEADER + Colors.BOLD)
    print("=" * 60)


def run_command(command: str, description: str = "", check: bool = True) -> bool:
    """Run a shell command and return success status"""
    if description:
        print(f"📦 {description}")

    print(f"   Running: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            print_colored("   ✅ Success", Colors.OKGREEN)
            return True
        else:
            print_colored(f"   ❌ Error: {result.stderr}", Colors.FAIL)
            if check:
                return False
            return True

    except subprocess.TimeoutExpired:
        print_colored("   ❌ Command timed out", Colors.FAIL)
        return False
    except Exception as e:
        print_colored(f"   ❌ Exception: {str(e)}", Colors.FAIL)
        return False


def check_python_version() -> bool:
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_colored(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible", Colors.OKGREEN)
        return True
    else:
        print_colored(f"❌ Python {version.major}.{version.minor} is not supported. Requires Python 3.8+", Colors.FAIL)
        return False


def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH"""
    return shutil.which(command) is not None


def install_uv() -> bool:
    """Install uv package manager"""
    if check_command_exists("uv"):
        print_colored("✅ uv is already installed", Colors.OKGREEN)
        return True

    print_colored("📦 Installing uv package manager...", Colors.OKBLUE)

    if sys.platform.startswith('win'):
        print_colored("For Windows, please install uv manually:", Colors.WARNING)
        print("powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        print("Then run this script again.")
        return False
    else:
        install_cmd = "curl -LsSf https://astral.sh/uv/install.sh | sh"
        success = run_command(install_cmd, "Installing uv via curl")

        if success:
            # Try to source the shell profile to make uv available
            shell_files = ["~/.bashrc", "~/.zshrc", "~/.profile"]
            for shell_file in shell_files:
                expanded_path = os.path.expanduser(shell_file)
                if os.path.exists(expanded_path):
                    run_command(f"source {expanded_path}", check=False)

            # Check if uv is now available
            if check_command_exists("uv"):
                print_colored("✅ uv installed successfully", Colors.OKGREEN)
                return True
            else:
                print_colored("⚠️  uv installed but not in PATH. You may need to restart your terminal.",
                              Colors.WARNING)
                return True

        return False


def create_project_structure() -> bool:
    """Create the project directory structure"""
    print_colored("📁 Creating project structure...", Colors.OKBLUE)

    directories = [
        "dhan_mcp_server",
        "tests",
        "examples",
        "docs"
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   Created: {directory}/")

    # Create __init__.py files
    init_files = [
        "dhan_mcp_server/__init__.py",
        "tests/__init__.py"
    ]

    init_content = '''"""
Dhan MCP Server - A Model Context Protocol server for Dhan trading platform
"""

__version__ = "0.1.0"
__author__ = "Dhan MCP Server Team"
__description__ = "Complete MCP server for Dhan trading platform integration"
'''

    for init_file in init_files:
        if not Path(init_file).exists():
            with open(init_file, "w") as f:
                f.write(init_content)
            print(f"   Created: {init_file}")

    print_colored("✅ Project structure created", Colors.OKGREEN)
    return True


def create_env_file() -> bool:
    """Create .env file from .env.example if it doesn't exist"""
    if Path(".env").exists():
        print_colored("✅ .env file already exists", Colors.OKGREEN)
        return True

    if not Path(".env.example").exists():
        print_colored("⚠️  .env.example not found, creating template...", Colors.WARNING)

        env_template = """# Dhan MCP Server Configuration
# REQUIRED: Get your access token from https://web.dhan.co
DHAN_ACCESS_TOKEN=your-dhan-access-token-here

# Optional Configuration
DHAN_BASE_URL=https://api.dhan.co/v2
DHAN_REQUEST_TIMEOUT=30

# Partner Configuration (if applicable)
DHAN_PARTNER_ID=
DHAN_PARTNER_SECRET=
DHAN_REDIRECT_URL=

# Server Configuration
LOG_LEVEL=INFO
DEBUG=false
"""

        with open(".env.example", "w") as f:
            f.write(env_template)
        print("   Created: .env.example")

    # Copy .env.example to .env
    shutil.copy(".env.example", ".env")
    print_colored("✅ Created .env file from template", Colors.OKGREEN)
    return True


def install_dependencies() -> bool:
    """Install project dependencies using uv"""
    print_colored("📦 Installing dependencies...", Colors.OKBLUE)

    if not Path("pyproject.toml").exists():
        print_colored("❌ pyproject.toml not found. Please ensure all project files are present.", Colors.FAIL)
        return False

    # Install dependencies
    if not run_command("uv sync", "Installing project dependencies"):
        # Fallback to pip if uv fails
        print_colored("⚠️  uv sync failed, trying pip install...", Colors.WARNING)
        return run_command("pip install -e .", "Installing with pip")

    # Install development dependencies
    if not run_command("uv sync --extra dev", "Installing development dependencies", check=False):
        print_colored("⚠️  Development dependencies installation failed (optional)", Colors.WARNING)

    print_colored("✅ Dependencies installed", Colors.OKGREEN)
    return True


def create_run_scripts() -> bool:
    """Create platform-specific run scripts"""
    print_colored("Creating run scripts...", Colors.OKBLUE)

    # Unix/Linux/macOS script
    unix_script = """#!/bin/bash
# Dhan MCP Server Run Script

set -e

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo -e "${GREEN}Dhan MCP Server${NC}"
echo "================================"

# Check if .env file exists
if [ ! -f .env ]; then
    if [ ! -f .env.example ]; then
        echo -e "${RED}Error: Neither .env nor .env.example found${NC}"
        exit 1
    fi
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your Dhan API credentials${NC}"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Check if DHAN_ACCESS_TOKEN is set
if [ -z "$DHAN_ACCESS_TOKEN" ] || [ "$DHAN_ACCESS_TOKEN" = "your-dhan-access-token-here" ]; then
    echo -e "${RED}Error: Please set DHAN_ACCESS_TOKEN in .env file${NC}"
    echo "Get your token from: https://web.dhan.co → My Profile → Access DhanHQ APIs"
    exit 1
fi

echo -e "${GREEN}Configuration loaded${NC}"
echo "Access Token: ${DHAN_ACCESS_TOKEN:0:10}***"
echo ""
echo -e "${GREEN}Starting Dhan MCP Server...${NC}"
echo "Press Ctrl+C to stop"
echo ""

# Start the server
uv run python -m dhan_mcp_server.server
"""

    # Windows script
    windows_script = """@echo off
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
"""

    # Write scripts with proper encoding
    try:
        with open("run_server.sh", "w", encoding='utf-8', newline='\n') as f:
            f.write(unix_script)

        with open("run_server.bat", "w", encoding='utf-8', newline='\r\n') as f:
            f.write(windows_script)

        # Make Unix script executable
        if not sys.platform.startswith('win'):
            os.chmod("run_server.sh", 0o755)

        print("   Created: run_server.sh")
        print("   Created: run_server.bat")
        print_colored("Run scripts created", Colors.OKGREEN)
        return True

    except UnicodeEncodeError as e:
        print_colored(f"Unicode encoding error: {e}", Colors.FAIL)
        return False
    except Exception as e:
        print_colored(f"Error creating run scripts: {e}", Colors.FAIL)
        return False


def validate_installation() -> bool:
    """Validate that the installation was successful"""
    print_colored("🔍 Validating installation...", Colors.OKBLUE)

    # Check critical files exist
    critical_files = [
        "dhan_mcp_server/__init__.py",
        "dhan_mcp_server/server.py",
        "pyproject.toml",
        ".env",
        "run_server.sh",
        "run_server.bat"
    ]

    missing_files = []
    for file in critical_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print_colored(f"❌ Missing files: {', '.join(missing_files)}", Colors.FAIL)
        return False

    # Try to import the package
    try:
        sys.path.insert(0, ".")
        import dhan_mcp_server
        print_colored("✅ Package import successful", Colors.OKGREEN)
    except ImportError as e:
        print_colored(f"❌ Package import failed: {e}", Colors.FAIL)
        return False

    print_colored("✅ Installation validated", Colors.OKGREEN)
    return True


def print_next_steps() -> None:
    """Print next steps for the user"""
    print_header("SETUP COMPLETE!")

    print_colored("Next steps:", Colors.OKBLUE)
    print("\n1. Configure your Dhan API access token:")
    print_colored("   • Login to https://web.dhan.co", Colors.OKCYAN)
    print_colored("   • Go to My Profile → Access DhanHQ APIs", Colors.OKCYAN)
    print_colored("   • Generate your access token", Colors.OKCYAN)
    print_colored("   • Edit .env file and set DHAN_ACCESS_TOKEN", Colors.OKCYAN)

    print("\n2. Start the server:")
    if sys.platform.startswith('win'):
        print_colored("   run_server.bat", Colors.OKGREEN)
    else:
        print_colored("   ./run_server.sh", Colors.OKGREEN)

    print("\n3. Test the installation:")
    print_colored("   uv run python examples/example_usage.py", Colors.OKGREEN)

    print("\n4. Development commands:")
    print_colored("   uv run pytest              # Run tests", Colors.OKCYAN)
    print_colored("   uv run black .             # Format code", Colors.OKCYAN)
    print_colored("   uv run mypy .              # Type checking", Colors.OKCYAN)

    print("\nDocumentation:")
    print_colored("   • README.md - Complete documentation", Colors.OKCYAN)
    print_colored("   • examples/ - Usage examples", Colors.OKCYAN)
    print_colored("   • API docs: https://dhanhq.co/docs/", Colors.OKCYAN)

    print("\nImportant Security Notes:")
    print_colored("   • Keep your API token secure and private", Colors.WARNING)
    print_colored("   • Never commit .env files to version control", Colors.WARNING)
    print_colored("   • Test with small quantities before live trading", Colors.WARNING)

    print("\n" + "=" * 60)
    print_colored("Dhan MCP Server is ready for production use!", Colors.OKGREEN + Colors.BOLD)
    print("=" * 60)


def main() -> int:
    """Main setup function"""
    print_header("Dhan MCP Server Setup")

    try:
        # Check Python version
        if not check_python_version():
            return 1

        # Install uv package manager
        if not install_uv():
            print_colored("❌ Failed to install uv. Please install manually.", Colors.FAIL)
            return 1

        # Create project structure
        if not create_project_structure():
            return 1

        # Create environment file
        if not create_env_file():
            return 1

        # Install dependencies
        if not install_dependencies():
            return 1

        # Create run scripts
        if not create_run_scripts():
            return 1

        # Validate installation
        if not validate_installation():
            return 1

        # Print success message and next steps
        print_next_steps()

        return 0

    except KeyboardInterrupt:
        print_colored("\n\n❌ Setup interrupted by user.", Colors.FAIL)
        return 1
    except Exception as e:
        print_colored(f"\n❌ Setup failed with error: {e}", Colors.FAIL)
        return 1


if __name__ == "__main__":
    sys.exit(main())