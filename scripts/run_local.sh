#!/bin/bash

# run_local.sh - Local development helper script for GhostWire Refractory
# Sets up a virtual environment, installs the package in editable mode,
# copies .env.example to .env if no .env present, and runs the app module.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}⚡️ GhostWire Refractory - Local Development Helper${NC}"
echo "==================================================="

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo -e "${RED}Error: pyproject.toml not found. Please run this script from the project root.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [[ ! -d ".venv" ]]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}Virtual environment created.${NC}"
else
    echo -e "${GREEN}Using existing virtual environment.${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install the package in editable mode
echo -e "${YELLOW}Installing package in editable mode...${NC}"
pip install -e .

# Copy .env.example to .env if .env doesn't exist
if [[ ! -f ".env" ]]; then
    echo -e "${YELLOW}Copying .env.example to .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env file created. Please review and modify as needed.${NC}"
else
    echo -e "${GREEN}.env file already exists.${NC}"
fi

# Run the application
echo -e "${GREEN}Starting GhostWire Refractory...${NC}"
echo "==================================================="
PYTHONPATH=python uv run python -m python.ghostwire.main