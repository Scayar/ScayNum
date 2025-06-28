#!/bin/bash

# ScayNum Shell Launcher
# Advanced OSINT Tool by Scayar

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to show banner
show_banner() {
    print_color $CYAN "========================================"
    print_color $CYAN "           ScayNum by Scayar"
    print_color $CYAN "========================================"
    echo ""
}

# Function to show help
show_help() {
    show_banner
    print_color $WHITE "Available commands:"
    print_color $WHITE "  ./run_ScayNum.sh install    - Install dependencies"
    print_color $WHITE "  ./run_ScayNum.sh update     - Update ScayNum"
    print_color $WHITE "  ./run_ScayNum.sh test       - Test installation"
    print_color $WHITE "  ./run_ScayNum.sh help       - Show this help"
    print_color $WHITE "  ./run_ScayNum.sh            - Run ScayNum"
    echo ""
    print_color $YELLOW "Quick start:"
    print_color $YELLOW "  ./run_ScayNum.sh install"
    print_color $YELLOW "  ./run_ScayNum.sh"
}

# Function to install dependencies
install_dependencies() {
    print_color $CYAN "📦 Installing ScayNum dependencies..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        print_color $RED "❌ Python3 is not installed"
        print_color $YELLOW "💡 Please install Python3 from: https://python.org/"
        exit 1
    fi
    
    # Upgrade pip
    print_color $WHITE "   Upgrading pip..."
    python3 -m pip install --upgrade pip
    
    # Install requirements
    print_color $WHITE "   Installing requirements..."
    pip3 install -r requirements.txt
    
    print_color $GREEN "✅ Installation completed!"
}

# Function to update ScayNum
update_scaynum() {
    print_color $CYAN "🔄 Updating ScayNum..."
    
    # Check if git is available
    if ! command -v git &> /dev/null; then
        print_color $RED "❌ Git is not installed"
        print_color $YELLOW "💡 Please install Git from: https://git-scm.com/"
        exit 1
    fi
    
    # Pull latest changes
    print_color $WHITE "   Pulling latest changes..."
    git pull origin main
    
    # Install updated requirements
    print_color $WHITE "   Installing updated requirements..."
    pip3 install -r requirements.txt
    
    print_color $GREEN "✅ Update completed!"
}

# Function to test installation
test_installation() {
    print_color $CYAN "🧪 Testing ScayNum installation..."
    
    # Test Python imports
    python3 -c "
import sys
try:
    import pyfiglet
    import colorama
    import requests
    import beautifulsoup4
    print('✅ All dependencies installed successfully!')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Test completed!"
    else
        print_color $RED "❌ Test failed!"
        exit 1
    fi
}

# Function to start ScayNum
start_scaynum() {
    print_color $CYAN "🚀 Starting ScayNum..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_color $RED "❌ Python3 is not installed or not in PATH"
        print_color $YELLOW "💡 Please install Python3 from: https://python.org/"
        exit 1
    fi
    
    # Run ScayNum
    python3 main.py
}

# Main execution
case "${1:-}" in
    "install")
        install_dependencies
        ;;
    "update")
        update_scaynum
        ;;
    "test")
        test_installation
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        start_scaynum
        ;;
    *)
        print_color $RED "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 