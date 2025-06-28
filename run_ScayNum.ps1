# ScayNum PowerShell Launcher
# Advanced OSINT Tool by Scayar

param(
    [switch]$Install,
    [switch]$Update,
    [switch]$Test,
    [switch]$Help
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Cyan = "Cyan"
$White = "White"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = $White
    )
    Write-Host $Message -ForegroundColor $Color
}

function Show-Banner {
    Write-ColorOutput "========================================" $Cyan
    Write-ColorOutput "           ScayNum by Scayar" $Cyan
    Write-ColorOutput "========================================" $Cyan
    Write-Host ""
}

function Show-Help {
    Show-Banner
    Write-ColorOutput "Available commands:" $White
    Write-ColorOutput "  .\run_ScayNum.ps1 -Install    - Install dependencies" $White
    Write-ColorOutput "  .\run_ScayNum.ps1 -Update     - Update ScayNum" $White
    Write-ColorOutput "  .\run_ScayNum.ps1 -Test       - Test installation" $White
    Write-ColorOutput "  .\run_ScayNum.ps1 -Help       - Show this help" $White
    Write-ColorOutput "  .\run_ScayNum.ps1             - Run ScayNum" $White
    Write-Host ""
    Write-ColorOutput "Quick start:" $Yellow
    Write-ColorOutput "  .\run_ScayNum.ps1 -Install" $Yellow
    Write-ColorOutput "  .\run_ScayNum.ps1" $Yellow
}

function Install-Dependencies {
    Write-ColorOutput "📦 Installing ScayNum dependencies..." $Cyan
    
    try {
        # Upgrade pip
        Write-ColorOutput "   Upgrading pip..." $White
        python -m pip install --upgrade pip
        
        # Install requirements
        Write-ColorOutput "   Installing requirements..." $White
        pip install -r requirements.txt
        
        Write-ColorOutput "✅ Installation completed!" $Green
    }
    catch {
        Write-ColorOutput "❌ Installation failed: $($_.Exception.Message)" $Red
        exit 1
    }
}

function Update-ScayNum {
    Write-ColorOutput "🔄 Updating ScayNum..." $Cyan
    
    try {
        # Check if git is available
        $gitVersion = git --version 2>$null
        if (-not $gitVersion) {
            Write-ColorOutput "❌ Git is not installed" $Red
            Write-ColorOutput "💡 Please install Git from: https://git-scm.com/" $Yellow
            exit 1
        }
        
        # Pull latest changes
        Write-ColorOutput "   Pulling latest changes..." $White
        git pull origin main
        
        # Install updated requirements
        Write-ColorOutput "   Installing updated requirements..." $White
        pip install -r requirements.txt
        
        Write-ColorOutput "✅ Update completed!" $Green
    }
    catch {
        Write-ColorOutput "❌ Update failed: $($_.Exception.Message)" $Red
        exit 1
    }
}

function Test-Installation {
    Write-ColorOutput "🧪 Testing ScayNum installation..." $Cyan
    
    try {
        # Test Python imports
        $testScript = @"
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
"@
        
        python -c $testScript
        
        Write-ColorOutput "✅ Test completed!" $Green
    }
    catch {
        Write-ColorOutput "❌ Test failed: $($_.Exception.Message)" $Red
        exit 1
    }
}

function Start-ScayNum {
    Write-ColorOutput "🚀 Starting ScayNum..." $Cyan
    
    try {
        # Check if Python is available
        $pythonVersion = python --version 2>$null
        if (-not $pythonVersion) {
            Write-ColorOutput "❌ Python is not installed or not in PATH" $Red
            Write-ColorOutput "💡 Please install Python from: https://python.org/" $Yellow
            exit 1
        }
        
        # Run ScayNum
        python main.py
    }
    catch {
        Write-ColorOutput "❌ Failed to start ScayNum: $($_.Exception.Message)" $Red
        exit 1
    }
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Show-Banner

if ($Install) {
    Install-Dependencies
}
elseif ($Update) {
    Update-ScayNum
}
elseif ($Test) {
    Test-Installation
}
else {
    Start-ScayNum
} 