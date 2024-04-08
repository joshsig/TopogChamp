#!/bin/bash
c
cleanup() {
    echo "Cleaning up..."
    taskkill /IM "python3.exe" /F >nul 2>&1
    taskkill /IM "live-server.cmd" /F >nul 2>&1
    taskkill /IM "net-vis-localhost-win.exe" /F >nul 2>&1
    exit 0
}

# Trap the EXIT signal to run the cleanup function
trap cleanup EXIT

# Python dependencies
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install it by running: sudo apt install python3"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install it by running: sudo apt install python3-pip"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
python3 -m pip install -r backend/requirements.txt

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to install Python dependencies."
    exit 1
fi

# Run backend
if [ ! -d "backend" ]; then
    echo "backend directory not found."
    exit 1
fi

cd backend || exit
python3 getNetworkData.py &

cd Tacata-master || exit

# Check if lab directory exists, if exists remove it
if [ -d "lab" ]; then
    rm -rf lab
fi

# Copy lab.confu into Tacata-master folder
cd ..
cp lab.confu Tacata-master

# Run Tacata.py
cd Tacata-master || exit
python3 Tacata.py

# Run Lab
kathara lstart

# Run Netvis inside lab folder
cd lab || exit
mv net-vis-localhost-win.exe .

if [ ! -f "net-vis-localhost-win.exe" ]; then
    echo "net-vis-localhost-win.exe not found."
    exit 1
fi

echo "Running net-vis-localhost-win.exe"
start "" "net-vis-localhost-win.exe"
sleep 5

cd ../.. || exit

# Check if live-server is installed
if ! command -v live-server &> /dev/null; then
    echo "live-server is not installed. Please install it by running: npm install -g live-server"
    exit 1
fi

cd ..
# Check if the frontend directory exists
if [ ! -d "frontend" ]; then
    echo "frontend directory not found."
    exit 1
fi

# Check if the index.html file exists in the frontend directory
if [ ! -f "frontend/index.html" ]; then
    echo "index.html file not found in the frontend directory."
    exit 1
fi

cd frontend || exit
# Open another terminal and run live-server with index.html file
start "" "live-server"

echo "Press Enter to exit..."
read -r