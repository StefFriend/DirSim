import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QLineEdit
from PyQt5.QtGui import QColor, QPainter, QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect
import cv2
import numpy as np

from main import MainProgram
from config import INITIAL_BPM, MIN_BPM, MAX_BPM, OSC_SERVER, OSC_PORT

class DynamicRangeBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.min_value = MIN_BPM
        self.max_value = MAX_BPM
        self.setMinimumHeight(20)

    def setRange(self, min_value, max_value):
        # Set the range of the dynamic range bar
        self.min_value = min_value
        self.max_value = max_value
        self.update()

    def paintEvent(self, event):
        # Paint the dynamic range bar
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor(200, 200, 200))

        # Calculate color based on range
        dynamic_range = self.max_value - self.min_value
        if dynamic_range <= 15:
            color = QColor(0, 255, 0)  # Green
        elif dynamic_range <= 30:
            color = QColor(255, 165, 0)  # Orange
        else:
            color = QColor(255, 0, 0)  # Red

        # Draw colored bar
        painter.fillRect(self.rect(), color)

        # Draw text
        painter.setPen(Qt.white)
        painter.drawText(self.rect(), Qt.AlignCenter, f"{dynamic_range} BPM")

class MainThread(QThread):
    update_bpm = pyqtSignal(float)
    update_frame = pyqtSignal(np.ndarray)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.main_program = None

    def run(self):
        # Run the main program in a separate thread
        self.main_program = MainProgram(self.update_bpm.emit, self.update_frame.emit, self.config)
        self.main_program.run()

    def stop(self):
        # Stop the main program
        if self.main_program:
            self.main_program.stop()

    def send_key(self, key):
        # Send a key press to the main program
        if self.main_program:
            self.main_program.handle_key(key)

    def update_config(self, key, value):
        # Update the configuration of the main program
        if self.main_program:
            self.main_program.update_config(key, value)

class HandTrackingGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DirSim Controller")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left side: camera feed and BPM display
        left_layout = QVBoxLayout()
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(960, 540)  # 75% of 1280x720
        left_layout.addWidget(self.camera_label)

        self.bpm_label = QLabel(f"BPM: {INITIAL_BPM}")
        self.bpm_label.setStyleSheet("font-size: 120px; font-weight: bold;")
        self.bpm_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.bpm_label)

        main_layout.addLayout(left_layout)

        # Right side: configuration parameters
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Configuration"))

        # Create sliders for BPM configuration
        self.initial_bpm_slider, self.initial_bpm_label = self.create_slider("Initial BPM", INITIAL_BPM, 60, 200, right_layout)
        self.min_bpm_slider, self.min_bpm_label = self.create_slider("Min BPM", MIN_BPM, 60, 200, right_layout)
        self.max_bpm_slider, self.max_bpm_label = self.create_slider("Max BPM", MAX_BPM, 60, 200, right_layout)

        # Create dynamic range bar
        self.dynamic_range_bar = DynamicRangeBar()
        right_layout.addWidget(QLabel("Tempo Dynamic"))
        right_layout.addWidget(self.dynamic_range_bar)

        # Create input fields for OSC configuration
        self.osc_server_input = QLineEdit(OSC_SERVER)
        right_layout.addWidget(QLabel("OSC Server:"))
        right_layout.addWidget(self.osc_server_input)

        self.osc_port_input = QLineEdit(str(OSC_PORT))
        right_layout.addWidget(QLabel("OSC Port:"))
        right_layout.addWidget(self.osc_port_input)

        # Create control buttons
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_main_program)
        right_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_main_program)
        self.stop_button.setEnabled(False)
        right_layout.addWidget(self.stop_button)

        self.mode_button = QPushButton("Switch Mode (M)")
        self.mode_button.clicked.connect(lambda: self.send_key('m'))
        self.mode_button.setEnabled(False)
        right_layout.addWidget(self.mode_button)

        self.reset_button = QPushButton("Reset (S)")
        self.reset_button.clicked.connect(lambda: self.send_key('s'))
        self.reset_button.setEnabled(False)
        right_layout.addWidget(self.reset_button)

        main_layout.addLayout(right_layout)

        self.main_thread = None

    def create_slider(self, name, initial_value, min_value, max_value, layout):
        # Create a slider with label
        layout.addWidget(QLabel(name))
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(initial_value)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(10)
        slider.valueChanged.connect(lambda value: self.update_config_label(name, value))
        layout.addWidget(slider)
        label = QLabel(f"Current: {initial_value}")
        layout.addWidget(label)
        return slider, label

    def update_config_label(self, name, value):
        # Update configuration labels and values
        if name == "Min BPM":
            if value <= self.max_bpm_slider.value():
                self.min_bpm_label.setText(f"Current: {value}")
                if self.main_thread:
                    self.main_thread.update_config('MIN_BPM', value)
                self.check_initial_bpm()
            else:
                self.min_bpm_slider.setValue(self.max_bpm_slider.value())
        elif name == "Max BPM":
            if value >= self.min_bpm_slider.value():
                self.max_bpm_label.setText(f"Current: {value}")
                if self.main_thread:
                    self.main_thread.update_config('MAX_BPM', value)
                self.check_initial_bpm()
            else:
                self.max_bpm_slider.setValue(self.min_bpm_slider.value())
        elif name == "Initial BPM":
            if self.min_bpm_slider.value() <= value <= self.max_bpm_slider.value():
                self.initial_bpm_label.setText(f"Current: {value}")
                if self.main_thread:
                    self.main_thread.update_config('INITIAL_BPM', value)
            else:
                self.check_initial_bpm()
        
        self.update_dynamic_range_bar()

    def check_initial_bpm(self):
        # Ensure Initial BPM is within Min and Max BPM range
        current_value = self.initial_bpm_slider.value()
        min_bpm = self.min_bpm_slider.value()
        max_bpm = self.max_bpm_slider.value()

        if current_value < min_bpm:
            self.initial_bpm_slider.setValue(min_bpm)
        elif current_value > max_bpm:
            self.initial_bpm_slider.setValue(max_bpm)

        self.initial_bpm_label.setText(f"Current: {self.initial_bpm_slider.value()}")
        if self.main_thread:
            self.main_thread.update_config('INITIAL_BPM', self.initial_bpm_slider.value())

    def update_dynamic_range_bar(self):
        # Update the dynamic range bar
        min_bpm = self.min_bpm_slider.value()
        max_bpm = self.max_bpm_slider.value()
        self.dynamic_range_bar.setRange(min_bpm, max_bpm)

    def update_frame(self, frame):
        # Update the camera feed display
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(960, 540, Qt.KeepAspectRatio)
        self.camera_label.setPixmap(scaled_pixmap)

    def start_main_program(self):
        # Start the main program
        config = {
            'INITIAL_BPM': self.initial_bpm_slider.value(),
            'MIN_BPM': self.min_bpm_slider.value(),
            'MAX_BPM': self.max_bpm_slider.value(),
            'OSC_SERVER': self.osc_server_input.text(),
            'OSC_PORT': int(self.osc_port_input.text())
        }
        self.main_thread = MainThread(config)
        self.main_thread.update_bpm.connect(self.update_bpm_display)
        self.main_thread.update_frame.connect(self.update_frame)
        self.main_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.mode_button.setEnabled(True)
        self.reset_button.setEnabled(True)

    def stop_main_program(self):
        # Stop the main program
        if self.main_thread:
            self.main_thread.stop()
            self.main_thread.wait()
            self.main_thread = None
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.mode_button.setEnabled(False)
        self.reset_button.setEnabled(False)

    def update_bpm_display(self, bpm):
        # Update the BPM display
        self.bpm_label.setText(f"BPM: {bpm:.1f}")

    def send_key(self, key):
        # Send a key press to the main program
        if self.main_thread and self.main_thread.main_program:
            self.main_thread.send_key(key)

    def keyPressEvent(self, event):
        # Handle key press events
        if self.main_thread and self.main_thread.main_program:
            if event.key() == Qt.Key_M:
                self.send_key('m')
            elif event.key() == Qt.Key_S:
                self.send_key('s')

    def closeEvent(self, event):
        # Handle window close event
        self.stop_main_program()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HandTrackingGUI()
    window.show()
    sys.exit(app.exec_())