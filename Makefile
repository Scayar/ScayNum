# ScayNum Makefile
# Advanced OSINT Tool by Scayar

.PHONY: help install run clean update test

# Default target
help:
	@echo "🚀 ScayNum - Advanced OSINT Tool"
	@echo "=================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install ScayNum and dependencies"
	@echo "  make run        - Run ScayNum"
	@echo "  make clean      - Clean up temporary files"
	@echo "  make update     - Update ScayNum to latest version"
	@echo "  make test       - Test ScayNum installation"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Quick start:"
	@echo "  make install && make run"

# Install ScayNum
install:
	@echo "📦 Installing ScayNum..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Installation completed!"

# Run ScayNum
run:
	@echo "🚀 Starting ScayNum..."
	python main.py

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "✅ Cleanup completed!"

# Update ScayNum
update:
	@echo "🔄 Updating ScayNum..."
	git pull origin main
	pip install -r requirements.txt
	@echo "✅ Update completed!"

# Test installation
test:
	@echo "🧪 Testing ScayNum installation..."
	python -c "import pyfiglet, colorama, requests, beautifulsoup4; print('✅ All dependencies installed successfully!')"
	@echo "✅ Test completed!"

# Install as package
install-package:
	@echo "📦 Installing ScayNum as package..."
	pip install -e .
	@echo "✅ Package installation completed!"

# Uninstall package
uninstall-package:
	@echo "🗑️  Uninstalling ScayNum package..."
	pip uninstall scaynum -y
	@echo "✅ Package uninstallation completed!" 