# DirSim

DirSim is a comprehensive project consisting of three main modules: DirSim Controller, DirSim Port, and DirSim Visual. This repository contains the implementation of these modules, designed to work together for an integrated experience.

## Modules

### DirSim Controller

The DirSim Controller module is responsible for tracking hand movements and gestures to control various aspects of the system. It includes the following key features:

- Hand tracking using computer vision
- BPM (Beats Per Minute) calculation based on hand movements
- OSC (Open Sound Control) communication for sending control messages
- GUI for real-time visualization and configuration

### DirSim Port

[Placeholder for DirSim Port description]

### DirSim Visual

[Placeholder for DirSim Visual description]

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/DirSim.git
   ```

2. Navigate to the project directory:
   ```
   cd DirSim
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the DirSim Controller:

1. Navigate to the DirSim Controller directory:
   ```
   cd DirSim_Controller
   ```

2. Run the main application:
   ```
   python gui.py
   ```

[Placeholder for instructions]

## Configuration

The DirSim Controller can be configured through the GUI. Key configurable parameters include:

- Initial, minimum, and maximum BPM
- OSC server address and port
- Camera selection
- Debug mode

## Acknowledgements

- This project uses the cvzone library for hand tracking.
- OSC communication is handled using the python-osc library.
