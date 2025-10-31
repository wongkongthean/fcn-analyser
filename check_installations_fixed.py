#!/usr/bin/env python3
"""
USCAN INSTALLATION CHECKER - FIXED VERSION
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

def print_status(message, status="INFO"):
    """Print colored status messages"""
    colors = {
        "SUCCESS": "\033[92m",  # Green
        "ERROR": "\033[91m",    # Red  
        "WARNING": "\033[93m",  # Yellow
        "INFO": "\033[94m",     # Blue
        "END": "\033[0m"        # Reset
    }
    print(f"{colors.get(status, colors['INFO'])}[{status}]{colors['END']} {message}")

def check_python_packages_fixed():
    """Check all required Python packages - FIXED VERSION"""
    required_packages = {
        "streamlit": "streamlit",
        "fastapi": "fastapi",
        "uvicorn": "uvicorn", 
        "pydantic": "pydantic",
        "requests": "requests",
        "python-multipart": "python_multipart"  # Correct import name
    }
    
    missing_packages = []
    for pip_name, import_name in required_packages.items():
        try:
            importlib.import_module(import_name)
            print_status(f"Package: {pip_name}", "SUCCESS")
        except ImportError:
            print_status(f"Package: {pip_name} - NOT INSTALLED", "ERROR")
            missing_packages.append(pip_name)
            
    return missing_packages

def main():
    """Main check function"""
    print("\n🔍 USCAN INSTALLATION CHECK - FIXED")
    print("=" * 50)
    
    # Check packages with corrected import names
    missing_packages = check_python_packages_fixed()
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 50)
    
    if not missing_packages:
        print_status("✅ ALL PACKAGES INSTALLED", "SUCCESS")
        print_status("🚀 USCAN IS READY TO LAUNCH!", "SUCCESS")
        print_status("Run: streamlit run app/scanner.py", "INFO")
    else:
        print_status(f"Missing packages: {', '.join(missing_packages)}", "WARNING")

if __name__ == "__main__":
    main()