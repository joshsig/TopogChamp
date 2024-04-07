#!/bin/bash

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

# Run live-server with index.html file
cd frontend || exit
npx live-server


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

cd kathara_temp/Tacata-master/lab || exit

if [! -f "net-vis-localhost-win.exe" ]; then
    echo "net-vis-localhost-win.exe not found."
    exit 1
fi


./net-vis-localhost-win.exe