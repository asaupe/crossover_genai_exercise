#!/usr/bin/env python3
"""
Pre-Assessment Checklist for GenAI Email Processing System
Run this before starting your assessment to ensure everything is ready.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_file_exists(filepath, description):
    """Check if a file exists."""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {'Found' if exists else 'Missing'}")
    return exists

def check_environment():
    """Check environment setup."""
    print("🔍 Environment Check")
    print("=" * 50)
    
    # Check Python version
    version = sys.version.split()[0]
    print(f"✅ Python version: {version}")
    
    # Check virtual environment
    venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print(f"{'✅' if venv_active else '⚠️ '} Virtual environment: {'Active' if venv_active else 'Not detected'}")
    
    return True

def check_dependencies():
    """Check required dependencies."""
    print("\n📦 Dependencies Check")
    print("=" * 50)
    
    required_packages = [
        'fastapi', 'uvicorn', 'openai', 'langchain', 'chromadb', 
        'pydantic', 'sqlalchemy', 'pytest', 'python-dotenv'
    ]
    
    all_good = True
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"❌ {package}: Missing")
            all_good = False
    
    return all_good

def check_configuration():
    """Check configuration files."""
    print("\n⚙️  Configuration Check")
    print("=" * 50)
    
    checks = [
        ('.env', 'Environment variables file'),
        ('src/config/settings.py', 'Settings module'),
        ('requirements.txt', 'Requirements file'),
        ('README.md', 'Documentation'),
        ('pytest.ini', 'Test configuration'),
    ]
    
    all_good = True
    for filepath, description in checks:
        if not check_file_exists(filepath, description):
            all_good = False
    
    return all_good

def check_api_key():
    """Check OpenAI API key."""
    print("\n🔑 API Key Check")
    print("=" * 50)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return False
        
        # Basic format check
        if not api_key.startswith('sk-'):
            print("❌ API key format appears incorrect (should start with 'sk-')")
            return False
        
        print("✅ API key found and format looks correct")
        
        # Test API call
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            print("✅ API key validated with successful test call")
            return True
        except Exception as e:
            print(f"❌ API key validation failed: {str(e)[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error checking API key: {e}")
        return False

def check_application():
    """Check if the application can start."""
    print("\n🚀 Application Check")
    print("=" * 50)
    
    try:
        # Test imports
        from src.main import app
        from src.config.settings import settings
        print("✅ Application modules import successfully")
        
        # Check key settings
        print(f"✅ App name: {settings.APP_NAME}")
        print(f"✅ Model: {settings.OPENAI_MODEL}")
        print(f"✅ Supported languages: {settings.SUPPORTED_LANGUAGES}")
        
        return True
    except Exception as e:
        print(f"❌ Application check failed: {e}")
        return False

def check_project_structure():
    """Check project structure."""
    print("\n📁 Project Structure Check")
    print("=" * 50)
    
    required_dirs = [
        'src/api', 'src/core', 'src/ai', 'src/data', 'src/config', 'src/utils',
        'tests', 'docs', 'examples', 'scripts'
    ]
    
    all_good = True
    for directory in required_dirs:
        exists = Path(directory).is_dir()
        status = "✅" if exists else "❌"
        print(f"{status} {directory}/")
        if not exists:
            all_good = False
    
    return all_good

def main():
    """Run all checks."""
    print("🎯 GenAI Email Processor - Pre-Assessment Checklist")
    print("=" * 60)
    print("This script validates your setup before starting the assessment.\n")
    
    checks = [
        ("Environment", check_environment),
        ("Project Structure", check_project_structure),
        ("Configuration", check_configuration),
        ("Dependencies", check_dependencies),
        ("API Key", check_api_key),
        ("Application", check_application),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! You're ready to start the assessment!")
        print("\n🚀 Quick Start Commands:")
        print("   Start server: python -m src.main")
        print("   Run tests: pytest")
        print("   API docs: http://localhost:8000/docs")
    else:
        print("⚠️  Some checks failed. Please fix the issues above before starting.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
