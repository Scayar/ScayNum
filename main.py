#!/usr/bin/env python3
"""
ScayNum - Advanced OSINT Tool
Main entry point for easy execution
"""

import os
import sys

# Add scripts directory to path
scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
sys.path.insert(0, scripts_dir)

# Import and run the main ScayNum application
if __name__ == "__main__":
    try:
        from core import main
        main()
    except ImportError as e:
        print("❌ Error: Could not import ScayNum modules")
        print(f"   Details: {e}")
        print("\n💡 Make sure you're running this from the ScayNum root directory")
        print("   and all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 