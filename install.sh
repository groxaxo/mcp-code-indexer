#!/bin/bash

# Automated Installation Script for mcp-code-indexer
# This script handles the complete setup of mcp-code-indexer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Display banner
echo "======================================================================"
echo "   mcp-code-indexer - Automated Installation"
echo "======================================================================"
echo ""

# Check Python version
print_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    print_error "Python 3.10 or higher is required. You have Python $PYTHON_VERSION"
    exit 1
fi

print_success "Python $PYTHON_VERSION detected"

# Check Docker
print_info "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_warning "Docker is not installed. Qdrant will need to be installed separately."
    DOCKER_AVAILABLE=false
else
    if docker ps &> /dev/null; then
        print_success "Docker is installed and running"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker is installed but not running. Please start Docker daemon."
        DOCKER_AVAILABLE=false
    fi
fi

# Installation options
echo ""
echo "Installation Options:"
echo "  1. Full installation (recommended)"
echo "  2. Install package only (no Qdrant)"
echo "  3. Install for development (with test dependencies)"
echo ""
read -p "Select installation type [1-3] (default: 1): " INSTALL_TYPE
INSTALL_TYPE=${INSTALL_TYPE:-1}

# Create virtual environment option
echo ""
read -p "Create a virtual environment? [y/N]: " CREATE_VENV
CREATE_VENV=${CREATE_VENV:-N}

if [[ "$CREATE_VENV" =~ ^[Yy]$ ]]; then
    VENV_DIR=".venv"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "Remove and recreate? [y/N]: " RECREATE_VENV
        if [[ "$RECREATE_VENV" =~ ^[Yy]$ ]]; then
            print_info "Removing existing virtual environment..."
            rm -rf "$VENV_DIR"
        fi
    fi
    
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created at $VENV_DIR"
    fi
    
    print_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
fi

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Install package
case $INSTALL_TYPE in
    1)
        print_info "Installing mcp-code-indexer (full installation)..."
        pip install -e . > /dev/null 2>&1
        print_success "Package installed successfully"
        ;;
    2)
        print_info "Installing mcp-code-indexer (package only)..."
        pip install -e . > /dev/null 2>&1
        print_success "Package installed successfully"
        ;;
    3)
        print_info "Installing mcp-code-indexer (development mode)..."
        pip install -e . > /dev/null 2>&1
        
        print_info "Installing development dependencies..."
        pip install pytest pytest-asyncio pytest-cov pytest-mock ruff > /dev/null 2>&1
        print_success "Development environment set up successfully"
        ;;
    *)
        print_error "Invalid installation type"
        exit 1
        ;;
esac

# Start Qdrant if Docker is available and full installation selected
if [ "$INSTALL_TYPE" -eq 1 ] && [ "$DOCKER_AVAILABLE" = true ]; then
    echo ""
    read -p "Start Qdrant vector database with Docker? [Y/n]: " START_QDRANT
    START_QDRANT=${START_QDRANT:-Y}
    
    if [[ "$START_QDRANT" =~ ^[Yy]$ ]]; then
        print_info "Starting Qdrant with Docker Compose..."
        docker compose up -d
        
        # Wait for Qdrant to be ready
        print_info "Waiting for Qdrant to start..."
        for i in {1..30}; do
            if curl -s http://localhost:6333/health > /dev/null 2>&1; then
                print_success "Qdrant is running at http://localhost:6333"
                break
            fi
            sleep 1
        done
        
        if ! curl -s http://localhost:6333/health > /dev/null 2>&1; then
            print_warning "Qdrant did not start within 30 seconds. Check Docker logs: docker compose logs qdrant"
        fi
    fi
fi

# Run tests if development installation
if [ "$INSTALL_TYPE" -eq 3 ]; then
    echo ""
    read -p "Run tests to verify installation? [Y/n]: " RUN_TESTS
    RUN_TESTS=${RUN_TESTS:-Y}
    
    if [[ "$RUN_TESTS" =~ ^[Yy]$ ]]; then
        print_info "Running tests..."
        if python -m pytest tests/ -v --tb=short; then
            print_success "All tests passed!"
        else
            print_warning "Some tests failed. This may be expected if Qdrant is not running."
        fi
    fi
fi

# Configuration instructions
echo ""
echo "======================================================================"
print_success "Installation completed successfully!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo ""

if [[ "$CREATE_VENV" =~ ^[Yy]$ ]]; then
    echo "1. Activate the virtual environment (if not already active):"
    echo "   source .venv/bin/activate"
    echo ""
fi

echo "2. Configure allowed repository roots:"
echo "   export MCP_ALLOWED_ROOTS=\"\$HOME/projects:\$HOME/work\""
echo ""

echo "3. Start the MCP server:"
echo "   python -m mcp_code_indexer"
echo ""

echo "4. Configure your AI assistant (Claude, Cursor, etc.):"
echo "   See README.md for detailed configuration instructions"
echo ""

if [ "$DOCKER_AVAILABLE" = false ]; then
    print_warning "Docker is not available. You'll need to install Qdrant manually:"
    echo "   docker compose up -d"
    echo ""
fi

if [ "$INSTALL_TYPE" -eq 3 ]; then
    echo "Development commands:"
    echo "  pytest tests/ -v              # Run all tests"
    echo "  pytest tests/unit/ -v         # Run unit tests"
    echo "  pytest --cov=mcp_code_indexer # Run with coverage"
    echo "  ruff format .                 # Format code"
    echo ""
fi

print_info "For more information, see README.md"
echo ""
