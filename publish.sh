#!/bin/bash
#
# Automated PyPI publishing script for TPWUtils
# This script builds and uploads the package to PyPI
#
# Usage:
#   ./publish.sh              # Upload to PyPI
#   ./publish.sh --test       # Upload to TestPyPI
#   ./publish.sh --build-only # Only build, don't upload
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
REPO="pypi"
BUILD_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --test)
            REPO="testpypi"
            shift
            ;;
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --test        Upload to TestPyPI instead of PyPI"
            echo "  --build-only  Only build the package, don't upload"
            echo "  -h, --help    Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}=== TPWUtils PyPI Publishing Script ===${NC}"
echo ""

# Get version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo -e "Package version: ${YELLOW}${VERSION}${NC}"
echo ""

# Check if tools are installed
echo -e "${GREEN}Checking required tools...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found${NC}"
    exit 1
fi

if ! python3 -c "import build" 2>/dev/null; then
    echo -e "${YELLOW}Installing build...${NC}"
    pip install build
fi

if ! python3 -c "import twine" 2>/dev/null; then
    echo -e "${YELLOW}Installing twine...${NC}"
    pip install twine
fi

# Run tests
echo -e "${GREEN}Running tests...${NC}"
if command -v pytest &> /dev/null; then
    pytest tests/ -v || {
        echo -e "${RED}Tests failed! Aborting.${NC}"
        exit 1
    }
else
    echo -e "${YELLOW}Warning: pytest not found, skipping tests${NC}"
fi

# Clean previous builds
echo -e "${GREEN}Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info

# Build the package
echo -e "${GREEN}Building package...${NC}"
python3 -m build --no-isolation

# Check the build
echo -e "${GREEN}Checking package...${NC}"
python3 -m twine check dist/*

# Show package contents
echo ""
echo -e "${GREEN}Package contents:${NC}"
ls -lh dist/
echo ""
tar -tzf dist/tpwutils-${VERSION}.tar.gz | head -20
echo "..."

if [ "$BUILD_ONLY" = true ]; then
    echo ""
    echo -e "${GREEN}Build complete! Package files in dist/${NC}"
    echo "To upload manually, run:"
    echo "  twine upload dist/*"
    exit 0
fi

# Confirm upload
echo ""
if [ "$REPO" = "testpypi" ]; then
    echo -e "${YELLOW}Ready to upload to TestPyPI${NC}"
else
    echo -e "${YELLOW}Ready to upload to PyPI (PRODUCTION)${NC}"
fi
echo -e "Version: ${VERSION}"
echo ""
read -p "Continue with upload? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Upload
echo -e "${GREEN}Uploading to ${REPO}...${NC}"
if [ "$REPO" = "testpypi" ]; then
    python3 -m twine upload --repository testpypi dist/*
else
    python3 -m twine upload dist/*
fi

echo ""
echo -e "${GREEN}Upload complete!${NC}"

# Show next steps
echo ""
echo -e "${GREEN}Next steps:${NC}"
if [ "$REPO" = "testpypi" ]; then
    echo "1. Test installation:"
    echo "   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ TPWUtils"
    echo ""
    echo "2. Test import:"
    echo "   python3 -c 'from TPWUtils import Logger; print(\"Success!\")'"
    echo ""
    echo "3. If tests pass, upload to production PyPI:"
    echo "   ./publish.sh"
else
    echo "1. Verify on PyPI:"
    echo "   https://pypi.org/project/TPWUtils/${VERSION}/"
    echo ""
    echo "2. Test installation:"
    echo "   pip install TPWUtils==${VERSION}"
    echo ""
    echo "3. Create git tag:"
    echo "   git tag -a v${VERSION} -m 'Release version ${VERSION}'"
    echo "   git push origin v${VERSION}"
    echo ""
    echo "4. Create GitHub release at:"
    echo "   https://github.com/mousebrains/TPWUtils/releases/new"
fi
