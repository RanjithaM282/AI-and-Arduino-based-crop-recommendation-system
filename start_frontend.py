#!/usr/bin/env python3
"""
Quick start script for the Tea Production Prediction Frontend
"""
import os
import sys
import subprocess

def main():
    print("🚀 Starting Tea Production Prediction Frontend...")
    
    # Check if we're in the right directory
    if not os.path.exists('package.json'):
        print("❌ package.json not found")
        print("Please run this script from the frontend directory")
        sys.exit(1)
    
    print("✅ package.json found")
    
    # Check if node_modules exists
    if not os.path.exists('node_modules'):
        print("📦 Installing dependencies...")
        try:
            subprocess.run(['npm', 'install'], check=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            print("Please ensure Node.js and npm are installed")
            sys.exit(1)
        except FileNotFoundError:
            print("❌ npm not found")
            print("Please install Node.js and npm first")
            sys.exit(1)
    else:
        print("✅ Dependencies already installed")
    
    # Start the React development server
    try:
        print("🌐 Starting React development server...")
        print("📱 The app will be available at http://localhost:3000")
        print("🗺️  Make sure the backend is running on http://localhost:5000")
        print("\n" + "="*50)
        print("Press Ctrl+C to stop the server")
        print("="*50)
        
        subprocess.run(['npm', 'start'])
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ npm not found")
        print("Please install Node.js and npm first")
        sys.exit(1)

if __name__ == '__main__':
    main()
