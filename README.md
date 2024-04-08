# TOPOGCHAMP

A network topology simulation and educational game.

> Made as a project for COMP4300 - Computer Networks

## Contributors

- [Andrii Provozin](github.com/developik)
- [Josh Sigurdson](github.com/joshsig)
- [Darwin Ross](github.com/darross)

## Dependencies

User must be connected to the University of Manitoba network to run the project.

- Windows
- Browser (Google Chrome recommended)
- Python 3.6
- pip3
  - pandas
  - psutil
  - scapy
  - flask
  - flask-cors
- npm
  - live-server
- [Kathara](https://github.com/KatharaFramework/Kathara-Labs)

## Libraries Used

- [Tacata](https://github.com/damiano-massarelli/Tacata)
- [Net-Vis](https://github.com/Friscobuffo/net-vis-localhost)
- [vis.js](https://visjs.org/)

## How to Run

1. Clone the repository
2. Run the following commands in the root directory of the project:
    ```bash
    chmod +x run.sh
    ./run.sh
    ```
3. Browser _should_ open automatically, if not, navigate to `localhost:8080` in your browser

## FAQ

1. If run.sh script does not run try replacing all python3 instances with python and pip3 with pip inside run.sh script.
