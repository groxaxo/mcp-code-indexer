#!/bin/bash
# Setup script for mcp-code-indexer testing environment

set -e

echo "Setting up mcp-code-indexer testing environment..."

# Create conda environment
echo "Creating conda environment 'mcp-test'..."
conda create -n mcp-test python=3.10 -y

# Activate environment
echo "Activating conda environment..."
eval "$(conda shell.bash hook)"
conda activate mcp-test

# Install project in development mode
echo "Installing mcp-code-indexer in development mode..."
pip install -e .

# Install testing dependencies
echo "Installing testing dependencies..."
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Install additional dependencies for full functionality
echo "Installing additional dependencies..."
pip install sentence-transformers  # For cross-encoder reranking tests

echo ""
echo "Setup complete! To activate the environment:"
echo "  conda activate mcp-test"
echo ""
echo "To run tests:"
echo "  python simple_test.py                    # Simple test runner"
echo "  python -m pytest tests/ -v               # Run all tests with pytest"
echo "  python -m pytest tests/unit/ -v          # Run unit tests only"
echo "  python -m pytest tests/ --cov=mcp_code_indexer  # Run with coverage"