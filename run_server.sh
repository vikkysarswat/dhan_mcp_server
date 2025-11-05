#!/bin/bash
# Dhan MCP Server Run Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
