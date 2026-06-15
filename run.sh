#!/bin/bash

# Luxify Assistant - Voice Control AI Startup Script for macOS/Linux

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed"
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "code.py" ]; then
    echo "Error: code.py not found in current directory"
    echo "Please run this script from the voice_ai/ui_test directory"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
pip3 list | grep PyQt6 > /dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies"
        exit 1
    fi
fi

# Run the application
echo "Starting Luxify Assistant..."
python3 code.py
