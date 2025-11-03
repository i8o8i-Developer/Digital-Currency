"""
Start_BackEnd.py
Backend Server Startup Script With Virtual Environment Setup
"""

import os
import sys
import subprocess
import platform

def print_header():
    """Print Startup Header"""
    print("=" * 60)
    print("  I8o8iCoin Digital Currency System - Backend Server")
    print("=" * 60)
    print()

def check_python():
    """Check Python Installation"""
    print("[1/4] Checking Python Installation...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR: Python 3.8 Or Higher Required")
        print(f"Current Version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro} Detected")
    print()

def setup_venv():
    """Setup Virtual Environment"""
    print("[2/4] Setting Up Virtual Environment...")
    venv_path = os.path.join(os.path.dirname(__file__), 'venv')
    
    if not os.path.exists(venv_path):
        print("Creating Virtual Environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("[OK] Virtual Environment Created")
    else:
        print("[OK] Virtual Environment Already Exists")
    print()
    
    return venv_path

def get_venv_python(venv_path):
    """Get Virtual Environment Python Executable"""
    if platform.system() == 'Windows':
        return os.path.join(venv_path, 'Scripts', 'python.exe')
    else:
        return os.path.join(venv_path, 'bin', 'python')

def install_dependencies(venv_python):
    """Install Python Dependencies"""
    print("[3/4] Installing Dependencies...")
    requirements_file = os.path.join(os.path.dirname(__file__), 'Requirements.txt')
    
    if os.path.exists(requirements_file):
        print("Installing Packages From Requirements.txt...")
        subprocess.run([venv_python, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=False)
        subprocess.run([venv_python, '-m', 'pip', 'install', '-r', requirements_file], 
                      check=True)
        print("[OK] Dependencies Installed")
    else:
        print("[WARNING] Requirements.txt Not Found")
    print()

def start_server(venv_python):
    """Start Backend Server"""
    print("[4/4] Starting I8o8iCoin Backend Server...")
    print()
    print("Server Starting On http://localhost:5000")
    print("Press Ctrl+C To Stop The Server")
    print()
    print("-" * 60)
    print()
    
    app_path = os.path.join(os.path.dirname(__file__), 'BackEnd', 'App.py')
    
    try:
        subprocess.run([venv_python, app_path])
    except KeyboardInterrupt:
        print()
        print()
        print("=" * 60)
        print("  Server Stopped")
        print("=" * 60)

def main():
    """Main Startup Function"""
    try:
        print_header()
        check_python()
        venv_path = setup_venv()
        venv_python = get_venv_python(venv_path)
        install_dependencies(venv_python)
        start_server(venv_python)
    except subprocess.CalledProcessError as e:
        print()
        print(f"ERROR: {e}")
        print()
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print("Setup Cancelled")
        sys.exit(0)
    except Exception as e:
        print()
        print(f"UNEXPECTED ERROR: {e}")
        print()
        sys.exit(1)

if __name__ == '__main__':
    main()
