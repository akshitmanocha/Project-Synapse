#!/usr/bin/env python3
"""
Cross-platform installer for Project Synapse

This script automatically detects your platform and installs dependencies
with the correct commands for your operating system.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def detect_platform():
    """Detect the current platform and return appropriate commands."""
    system = platform.system().lower()
    
    if system == "windows":
        return {
            "python": "python",
            "pip": "pip",
            "venv_activate": ".venv\\Scripts\\activate",
            "copy": "copy",
            "shell": "cmd"
        }
    else:  # macOS and Linux
        return {
            "python": "python3",
            "pip": "pip",
            "venv_activate": "source .venv/bin/activate",
            "copy": "cp",
            "shell": "bash"
        }


def run_command(command, description=""):
    """Run a command and handle errors gracefully."""
    print(f"🔄 {description}...")
    print(f"   Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check git
    try:
        result = subprocess.run("git --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git available: {result.stdout.strip()}")
        else:
            print("❌ Git not found. Please install Git first.")
            return False
    except:
        print("❌ Git not found. Please install Git first.")
        return False
    
    return True


def install_synapse():
    """Main installation function."""
    print("🚀 Project Synapse Cross-Platform Installer")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Detect platform
    platform_info = detect_platform()
    system_name = platform.system()
    print(f"🖥️  Detected platform: {system_name}")
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Please run this from the Project-Synapse directory.")
        return False
    
    # Install steps
    steps = [
        (f"{platform_info['python']} -m venv .venv", "Creating virtual environment"),
        (f"{platform_info['pip']} install -r requirements.txt", "Installing dependencies"),
        (f"{platform_info['copy']} .env.template .env", "Setting up environment file")
    ]
    
    # Special handling for virtual environment activation
    if system_name.lower() == "windows":
        steps.insert(1, (".venv\\Scripts\\activate && pip install -r requirements.txt", "Activating venv and installing"))
        steps.pop(2)  # Remove duplicate install step
    else:
        steps.insert(1, ("source .venv/bin/activate && pip install -r requirements.txt", "Activating venv and installing"))
        steps.pop(2)  # Remove duplicate install step
    
    # Execute installation steps
    for command, description in steps:
        if not run_command(command, description):
            print(f"\n❌ Installation failed at: {description}")
            return False
    
    # Verify installation
    print("\n🔍 Verifying installation...")
    
    # Check if synapse can be imported
    test_command = f"{platform_info['python']} -c \"import synapse; print('✅ Synapse installed successfully')\""
    if not run_command(test_command, "Testing synapse import"):
        print("⚠️  Warning: Installation may be incomplete")
    
    # Final instructions
    print("\n" + "=" * 50)
    print("🎉 Installation completed!")
    print("\n📝 Next steps:")
    print("1. Add your Gemini API key to .env file")
    print("   Get your free key from: https://ai.google.dev/")
    print("\n2. Test the installation:")
    print(f"   {platform_info['python']} main.py --help")
    print("\n3. Run your first scenario:")
    print(f"   {platform_info['python']} main.py \"Driver stuck in traffic\"")
    
    return True


def show_help():
    """Show help information."""
    print("""
🚀 Project Synapse Installer

Usage:
    python install.py          # Run installation
    python install.py --help   # Show this help

This installer will:
✅ Check your system requirements
✅ Create a virtual environment
✅ Install all dependencies
✅ Set up configuration files
✅ Verify the installation

Supported platforms:
- Windows (PowerShell, Command Prompt)
- macOS (Terminal)
- Linux (Bash)

Requirements:
- Python 3.8+
- Git
- Internet connection
    """)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        show_help()
    else:
        try:
            success = install_synapse()
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\n\n⏸️  Installation cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            sys.exit(1)