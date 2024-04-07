#!/bin/bash

cleanup() {
    echo "Cleaning up..."
    pkill -TERM -f "xterm -e ./net-vis-localhost-win.exe"
    pkill -TERM -f "xterm -e cd frontend && npx live-server"
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
pip install -r backend/requirements.txt

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
cd ..

# Run Kathara
if [ ! -d "kathara" ]; then
    echo "kathara directory not found."
    exit 1
fi

if [ ! -d "kathara/Tacata-master" ]; then
    echo "Tacata-master directory not found."
    exit 1
fi

if [ ! -d "kathara/Tacata-master/lab" ]; then
    echo "lab directory not found."
    exit 1
fi

cd kathara/Tacata-master/lab || exit

if [ ! -f "net-vis-localhost-win.exe" ]; then
    echo "net-vis-localhost-win.exe not found."
    exit 1
fi

echo "Running net-vis-localhost-win.exe"
xterm -e "./net-vis-localhost-win.exe" &
sleep 5

cd ../../.. || exit

# Check if live-server is installed
if ! command -v live-server &> /dev/null; then
    echo "live-server is not installed. Please install it by running: npm install -g live-server"
    exit 1
fi

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

# Open another terminal and run live-server with index.html file
xterm -e "cd frontend && npx live-server" &

echo "Press Ctrl+C to exit..."
while true; do
    sleep 1
done