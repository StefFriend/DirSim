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

Components:

1. `main.py`: The core logic of the Controller, integrating all components and managing the main program loop.
2. `gui.py`: Implements the graphical user interface for the Controller.
3. `hand_tracker.py`: Handles hand detection and tracking logic.
4. `bpm_calculators.py`: Contains classes for different BPM calculation methods.
5. `slider_controller.py`: Manages the virtual slider controls.

The DirSim Controller is designed to be flexible and extensible, allowing for easy integration with various audio production setups (actually tested with Cockos Reaper) and potential expansion to control other parameters beyond BPM and volume.

### DirSim Port
The DirSim Port module serves as a bridge between MIDI input devices and OSC-compatible software, facilitating seamless communication in audio production environments.

Key Features:
1. **MIDI Input Processing**:
   - Utilizes the `python-rtmidi` library for real-time MIDI message handling.
   - Supports a wide range of MIDI input devices.
   - Capable of processing various MIDI message types (e.g., Note On/Off, Control Change).

2. **OSC (Open Sound Control) Output**:
   - Converts MIDI messages to OSC format using the `python-osc` library.
   - Configurable OSC server address and port for flexible integration with various audio software.

3. **GUI (Graphical User Interface)**:
   - Built with PyQt6 for a modern and responsive user interface.
   - Dropdown menu for easy selection of available MIDI input devices.
   - Real-time display of incoming MIDI messages and outgoing OSC messages.

4. **Dynamic Configuration**:
   - Allows users to change MIDI input and OSC output settings on the fly.
   - Provides immediate feedback on configuration changes.

5. **Error Handling and Logging**:
   - Robust error handling for MIDI device connections and OSC message transmission.
   - Detailed logging of all activities for easy troubleshooting and monitoring.

Components:
1. `dirsim_port.py`: The main script containing the GUI implementation and core logic for MIDI to OSC conversion.


### DirSim Visual

DirSim Visual is a Processing-based visualization module designed to provide a dynamic, real-time representation of an orchestra based on MIDI input. It serves as the visual component of the DirSim project, creating an engaging and intuitive display of musical activity.

Key Features:

1. **Orchestra Layout Visualization**:
   - Displays a semicircular arrangement of instrument sections, mimicking a real orchestra setup.
   - Each section is represented by a circular node, positioned according to typical orchestra seating.

2. **Real-time MIDI Visualization**:
   - Responds to MIDI input in real-time, lighting up corresponding instrument sections.
   - The intensity and size of each section's visual representation change based on MIDI velocity.

3. **Color-coded Instrument Families**:
   - Uses distinct color schemes for different instrument families (strings, woodwinds, brass, percussion).
   - Enhances visual differentiation between various orchestra sections.

4. **Dynamic Background**:
   - Features a subtle, animated background that responds to overall musical activity.

5. **Conductor Representation**:
   - Includes a visual element representing the conductor's position.

6. **Debug Mode**:
   - Offers a toggleable debug mode for displaying technical information such as FPS, active sections, and last received MIDI message.

7. **Customizable Layout**:
   - Allows for easy adjustment of the orchestra layout, colors, and sizes through code modifications.

Components:

1. `particle10.pde`: The main Processing sketch containing all the visualization logic.

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

To run the DirSim Port:
1. Navigate to the DirSim Port directory:
   ```
   cd DirSim_Port
   ```
2. Run the main application:
   ```
   python dirsim_port.py


To run DirSim Visual:

1. Ensure you have Processing installed on your system.

2. Open the `particle3.pde` file in the Processing IDE.

3. Click the "Run" button or press Ctrl+R (Cmd+R on Mac) to start the visualization.

4. Ensure that MIDI messages are being sent to the correct port (default is 57120) for the visualization to respond.


## Configuration

The DirSim Controller can be configured through the GUI. Key configurable parameters include:

- Initial, minimum, and maximum BPM
- OSC server address and port
- Camera selection
- Debug mode
- Mode selection (Hand Speed or Pattern)
- Sensitivity settings for hand tracking

For DirSim Port, configuration is done through the GUI:
- Select the desired MIDI input device from the dropdown menu.
- Set the OSC server address and port in the provided fields.
- Click the "Apply" button to confirm OSC settings.
- Use the "Start" button to begin MIDI to OSC conversion.

For DirSim Visual, configuration is primarily done through code adjustments:

- Modify the `sectionFamilies` and `familyColors` arrays to change the instrument layout and color scheme.
- Adjust the `radius` and angle calculations in the `setup()` function to alter the overall layout.
- Change the `backgroundColor` value to set a different background color.
- Modify the `Section` class to alter the behavior and appearance of individual instrument representations.


## Acknowledgements

- This project uses the cvzone library for hand tracking and face detection.
- OSC communication is handled using the python-osc library.
- GUI is built with PyQt5.
- MIDI input processing in DirSim Port is facilitated by the python-rtmidi library.
- DirSim Visual is implemented using Processing.
