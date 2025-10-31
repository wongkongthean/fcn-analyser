import sys
import subprocess
import os

def check_package_installation():
    print("🔍 PACKAGE INSTALLATION DIAGNOSTIC")
    print("=" * 50)
    
    # Check Python path
    print(f"Python executable: {sys.executable}")
    print(f"Virtual env: {os.getenv('VIRTUAL_ENV', 'Not detected')}")
    
    # Try multiple import methods
    packages_to_check = ["python_multipart", "multipart"]
    
    for package in packages_to_check:
        try:
            __import__(package)
            print(f"✅ {package}: Successfully imported")
        except ImportError as e:
            print(f"❌ {package}: Import failed - {e}")
    
    # Check pip list
    print("\n📦 Checking pip list for multipart:")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "list", "--format=freeze"
        ], capture_output=True, text=True, check=True)
        
        multipart_packages = [pkg for pkg in result.stdout.split('\n') if 'multipart' in pkg.lower()]
        if multipart_packages:
            for pkg in multipart_packages:
                print(f"✅ Found: {pkg}")
        else:
            print("❌ No multipart packages found in pip list")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking pip list: {e}")

if __name__ == "__main__":
    check_package_installation()