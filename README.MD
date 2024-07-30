# DirSim

DirSim is a comprehensive project consisting of three main modules: DirSim Controller, DirSim Port, and DirSim Visual. This repository contains the implementation of these modules, designed to work together for an integrated experience.

## Modules

### DirSim Controller

The DirSim Controller module is a sophisticated system for tracking hand movements and gestures to control various aspects of audio production and performance. It utilizes computer vision techniques and machine learning models to interpret hand positions and movements, translating them into meaningful control signals.

Key Features:

1. **Hand Tracking**: 
   - Utilizes the cvzone library's HandTrackingModule for real-time hand detection and tracking.
   - Capable of tracking multiple hands simultaneously.
   - Extracts key points of the hand for precise gesture recognition.

2. **BPM (Beats Per Minute) Calculation**:
   - Two modes of BPM calculation:
     a. Hand Speed Mode: Calculates BPM based on the speed of hand movements.
     b. Pattern Mode: Determines BPM by timing a specific sequence of hand positions.
   - Adaptive BPM range with configurable minimum and maximum values.

3. **OSC (Open Sound Control) Communication**:
   - Sends control messages using the python-osc library.
   - Communicates BPM changes, play/stop commands, and other control signals to compatible audio software.

4. **GUI (Graphical User Interface)**:
   - Built with PyQt5 for a responsive and intuitive user experience.
   - Real-time visualization of hand tracking and BPM.
   - Configuration panels for adjusting BPM ranges, OSC settings, and other parameters.
   - Live camera feed display with overlay of tracking information.

5. **Dual Slider Control**:
   - Virtual sliders controlled by individual finger positions.
   - Allows simultaneous control of two independent parameters (e.g., volume levels).

6. **Mode Switching**:
   - Supports switching between Hand Speed Mode and Pattern Mode for BPM calculation.
   - Each mode offers unique interaction methods for controlling the BPM.

7. **Debug Mode**:
   - Provides additional visual feedback and logging for troubleshooting and development.

8. **Face Detection**:
   - Includes face detection capabilities using cvzone's FaceDetectionModule.
   - Can be toggled on/off for additional visual feedback or future feature expansion.

Components:

1. `main.py`: The core logic of the Controller, integrating all components and managing the main program loop.
2. `gui.py`: Implements the graphical user interface for the Controller.
3. `hand_tracker.py`: Handles hand detection and tracking logic.
4. `bpm_calculators.py`: Contains classes for different BPM calculation methods.
5. `slider_controller.py`: Manages the virtual slider controls.

The DirSim Controller is designed to be flexible and extensible, allowing for easy integration with various audio production setups (actually tested with Cockos Reaper) and potential expansion to control other parameters beyond BPM and volume.

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

## Configuration

The DirSim Controller can be configured through the GUI. Key configurable parameters include:

- Initial, minimum, and maximum BPM
- OSC server address and port
- Camera selection
- Debug mode
- Mode selection (Hand Speed or Pattern)
- Sensitivity settings for hand tracking

## Acknowledgements

- This project uses the cvzone library for hand tracking and face detection.
- OSC communication is handled using the python-osc library.
- GUI is built with PyQt5.
