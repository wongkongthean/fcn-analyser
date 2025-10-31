#!/usr/bin/env python3
"""
USCAN INSTALLATION CHECKER
Comprehensive check of all dependencies and setup
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

def check_python():
    """Check Python version"""
    try:
        version = sys.version_info
        print_status(f"Python {version.major}.{version.minor}.{version.micro}", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"Python check failed: {e}", "ERROR")
        return False

def check_pip():
    """Check pip availability"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        pip_version = result.stdout.split()[1]
        print_status(f"Pip {pip_version}", "SUCCESS")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_status("Pip not found or not working", "ERROR")
        return False

def check_directory_structure():
    """Check required directories"""
    required_dirs = [
        "app",
        "app/config",
        "app/db", 
        "static",
        "tests",
        ".streamlit"
    ]
    
    current_dir = Path.cwd()
    print_status(f"Current directory: {current_dir}", "INFO")
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_status(f"Directory: {dir_path}", "SUCCESS")
        else:
            print_status(f"Directory: {dir_path} - MISSING", "ERROR")
            all_exist = False
            
    return all_exist

def check_required_files():
    """Check required files exist"""
    required_files = [
        "requirements.txt",
        "README.md", 
        "app/scanner.py",
        ".streamlit/config.toml"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_status(f"File: {file_path}", "SUCCESS")
        else:
            print_status(f"File: {file_path} - MISSING", "ERROR")
            all_exist = False
            
    return all_exist

def check_python_packages():
    """Check all required Python packages"""
    required_packages = [
        "streamlit",
        "fastapi",
        "uvicorn", 
        "pydantic",
        "requests",
        "python-multipart"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print_status(f"Package: {package}", "SUCCESS")
        except ImportError:
            print_status(f"Package: {package} - NOT INSTALLED", "ERROR")
            missing_packages.append(package)
            
    return missing_packages

def check_streamlit():
    """Check Streamlit functionality"""
    try:
        result = subprocess.run(["streamlit", "--version"], 
                              capture_output=True, text=True, check=True)
        version_line = result.stdout.strip()
        print_status(f"Streamlit: {version_line}", "SUCCESS")
        
        # Test scanner module import
        try:
            sys.path.append('app')
            from scanner import main
            print_status("Scanner module: Can be imported", "SUCCESS")
            return True
        except Exception as e:
            print_status(f"Scanner module: Import failed - {e}", "ERROR")
            return False
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_status("Streamlit not found or not working", "ERROR")
        return False

def main():
    """Main check function"""
    print("\n🔍 USCAN INSTALLATION CHECK")
    print("=" * 50)
    
    checks = {
        "Python": check_python(),
        "Pip": check_pip(),
        "Directory Structure": check_directory_structure(),
        "Required Files": check_required_files(),
        "Streamlit": check_streamlit()
    }
    
    missing_packages = check_python_packages()
    checks["Python Packages"] = len(missing_packages) == 0
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 50)
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check_name, status in checks.items():
        status_text = "SUCCESS" if status else "ERROR"
        print_status(f"{check_name}: {'PASS' if status else 'FAIL'}", status_text)
    
    print(f"\n🎯 RESULT: {passed}/{total} checks passed")
    
    if passed == total and not missing_packages:
        print_status("🚀 USCAN IS READY TO LAUNCH!", "SUCCESS")
        print_status("Run: streamlit run app/scanner.py", "INFO")
    else:
        print_status("⚠️ Some issues need to be fixed:", "WARNING")
        
        if missing_packages:
            print_status(f"Missing packages: {', '.join(missing_packages)}", "INFO")
            print_status(f"Run: pip install {' '.join(missing_packages)}", "INFO")
            
        if not Path("requirements.txt").exists():
            print_status("Create requirements.txt file", "INFO")
            
        if not Path("app/scanner.py").exists():
            print_status("Create app/scanner.py file", "INFO")

if __name__ == "__main__":
    main()