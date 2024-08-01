import sys
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QPushButton, QLineEdit, QComboBox, QGroupBox, QFormLayout, QSizePolicy, QCheckBox)
from PyQt5.QtGui import QColor, QPainter, QImage, QPixmap, QFont, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect

import numpy as np

from main import MainProgram
from config import INITIAL_BPM, MIN_BPM, MAX_BPM, OSC_SERVER, OSC_PORT

class ColorPalette:
    PRIMARY = "#2980b9"  # Darker blue
    SECONDARY = "#27ae60"  # Darker green
    ACCENT = "#c0392b"  # Darker red
    BACKGROUND = "#f5f5f5"  # Light grey
    TEXT = "#2c3e50"  # Dark blue-grey
    LIGHT_TEXT = "#ecf0f1"  # Very light grey, almost white

class StyleSheet:
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {ColorPalette.BACKGROUND};
        }}
    """
    GROUP_BOX = f"""
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {ColorPalette.PRIMARY};
            border-radius: 5px;
            margin-top: 10px;
            color: {ColorPalette.TEXT};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }}
    """
    SLIDER = f"""
        QSlider::groove:horizontal {{
            border: 1px solid {ColorPalette.PRIMARY};
            height: 8px;
            background: white;
            margin: 2px 0;
        }}
        QSlider::handle:horizontal {{
            background: {ColorPalette.PRIMARY};
            border: 1px solid {ColorPalette.PRIMARY};
            width: 18px;
            margin: -2px 0;
            border-radius: 3px;
        }}
    """
    BUTTON = f"""
        QPushButton {{
            background-color: {ColorPalette.PRIMARY};
            color: {ColorPalette.LIGHT_TEXT};
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {ColorPalette.SECONDARY};
        }}
        QPushButton:pressed {{
            background-color: {ColorPalette.ACCENT};
        }}
        QPushButton:disabled {{
            background-color: #bdc3c7;
            color: #7f8c8d;
        }}
    """
    COMBOBOX = f"""
        QComboBox {{
            border: 1px solid {ColorPalette.PRIMARY};
            border-radius: 3px;
            padding: 1px 18px 1px 3px;
            min-width: 6em;
            color: {ColorPalette.TEXT};
            background-color: white;
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: {ColorPalette.PRIMARY};
            border-left-style: solid;
        }}
        QComboBox QAbstractItemView {{
            background-color: {ColorPalette.BACKGROUND};
            border: 1px solid {ColorPalette.PRIMARY};
            selection-background-color: {ColorPalette.SECONDARY};
            color: {ColorPalette.TEXT};
        }}
    """
    LABEL = f"""
        QLabel {{
            color: {ColorPalette.TEXT};
        }}
    """
    APPLY_BUTTON = f"""
        QPushButton {{
            background-color: {ColorPalette.SECONDARY};
            color: {ColorPalette.LIGHT_TEXT};
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {ColorPalette.PRIMARY};
        }}
        QPushButton:pressed {{
            background-color: {ColorPalette.ACCENT};
        }}
    """
    CHECKBOX = f"""
        QCheckBox {{
            color: {ColorPalette.TEXT};
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
        }}
        QCheckBox::indicator:unchecked {{
            border: 1px solid {ColorPalette.PRIMARY};
            background-color: white;
        }}
        QCheckBox::indicator:unchecked:hover {{
            border: 1px solid {ColorPalette.SECONDARY};
            background-color: {ColorPalette.LIGHT_TEXT};
        }}
        QCheckBox::indicator:checked {{
            border: 1px solid {ColorPalette.PRIMARY};
            background-color: {ColorPalette.PRIMARY};
        }}
    """


class DynamicRangeBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.min_value = MIN_BPM
        self.max_value = MAX_BPM
        self.setMinimumHeight(40)  # Increased height for larger font

    def setRange(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor(ColorPalette.BACKGROUND))

        dynamic_range = self.max_value - self.min_value
        if dynamic_range <= 15:
            color = QColor("#2ecc71")  # Green
        elif dynamic_range <= 30:
            color = QColor("#f39c12")  # Orange
        else:
            color = QColor("#e74c3c")  # Red

        painter.fillRect(self.rect(), color)

        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 16, QFont.Bold))  # Increased font size
        painter.drawText(self.rect(), Qt.AlignCenter, f"{dynamic_range} BPM")

class MainThread(QThread):
    update_bpm = pyqtSignal(float)
    update_frame = pyqtSignal(np.ndarray)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.main_program = None

    def run(self):
        self.main_program = MainProgram(self.update_bpm.emit, self.update_frame.emit, self.config)
        self.main_program.run()

    def stop(self):
        if self.main_program:
            self.main_program.stop()

    def send_key(self, key):
        if self.main_program:
            self.main_program.handle_key(key)

    def update_config(self, key, value):
        if self.main_program:
            self.main_program.update_config(key, value)

class HandTrackingGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DirSim Controller")
        self.setGeometry(100, 100, 1280, 720)
        self.setStyleSheet(StyleSheet.MAIN_WINDOW)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left side: camera feed and BPM display
        left_layout = QVBoxLayout()
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(960, 540)
        self.camera_label.setStyleSheet(f"border: 2px solid {ColorPalette.PRIMARY}; border-radius: 5px;")
        left_layout.addWidget(self.camera_label)

        self.bpm_label = QLabel(f"{INITIAL_BPM} BPM")
        bpm_font = QFont("Arial", 120, QFont.Bold)
        self.bpm_label.setFont(bpm_font)
        self.bpm_label.setStyleSheet(f"color: {ColorPalette.PRIMARY};")
        self.bpm_label.setAlignment(Qt.AlignCenter)
        self.bpm_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(self.bpm_label)

        main_layout.addLayout(left_layout, 2)

        # Right side: configuration parameters
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)

        # BPM Configuration
        bpm_group = QGroupBox("BPM Configuration")
        bpm_group.setStyleSheet(StyleSheet.GROUP_BOX)
        bpm_layout = QFormLayout()
        self.initial_bpm_slider, self.initial_bpm_label = self.create_slider("Initial BPM", INITIAL_BPM, 60, 200)
        self.min_bpm_slider, self.min_bpm_label = self.create_slider("Min BPM", MIN_BPM, 60, 200)
        self.max_bpm_slider, self.max_bpm_label = self.create_slider("Max BPM", MAX_BPM, 60, 200)
        bpm_layout.addRow("Initial BPM:", self.initial_bpm_slider)
        bpm_layout.addRow("", self.initial_bpm_label)
        bpm_layout.addRow("Min BPM:", self.min_bpm_slider)
        bpm_layout.addRow("", self.min_bpm_label)
        bpm_layout.addRow("Max BPM:", self.max_bpm_slider)
        bpm_layout.addRow("", self.max_bpm_label)
        bpm_group.setLayout(bpm_layout)
        right_layout.addWidget(bpm_group)

        # Mode Configuration
        mode_group = QGroupBox("Mode Configuration")
        mode_group.setStyleSheet(StyleSheet.GROUP_BOX)
        mode_layout = QVBoxLayout()
        
        mode1_layout = QVBoxLayout()
        mode1_layout.addWidget(QLabel("Mode 1 Sensitivity:"))
        self.sensitivity_slider, self.sensitivity_label = self.create_slider("Mode 1 Sensitivity", 5, 1, 10)
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity)
        mode1_layout.addWidget(self.sensitivity_slider)
        mode1_layout.addWidget(self.sensitivity_label)
        
        mode2_layout = QVBoxLayout()
        mode2_layout.addWidget(QLabel("Mode 2 Touch Count:"))
        self.touch_count_combo = QComboBox()
        self.touch_count_combo.addItems(['2 touches', '4 touches'])
        self.touch_count_combo.setCurrentIndex(1)
        self.touch_count_combo.currentIndexChanged.connect(self.update_touch_count)
        self.touch_count_combo.setStyleSheet(StyleSheet.COMBOBOX)
        mode2_layout.addWidget(self.touch_count_combo)
        
        mode_layout.addLayout(mode1_layout)
        mode_layout.addSpacing(10)
        mode_layout.addLayout(mode2_layout)
        mode_group.setLayout(mode_layout)
        right_layout.addWidget(mode_group)

        # Dynamic Range
        range_group = QGroupBox("Tempo Dynamic")
        range_group.setStyleSheet(StyleSheet.GROUP_BOX)
        range_layout = QVBoxLayout()
        self.dynamic_range_bar = DynamicRangeBar()
        range_layout.addWidget(self.dynamic_range_bar)
        range_group.setLayout(range_layout)
        range_group.setMaximumHeight(100)  # Limit the height
        right_layout.addWidget(range_group)

        # Advanced Module
        advanced_group = QGroupBox("Advanced")
        advanced_group.setStyleSheet(StyleSheet.GROUP_BOX)
        advanced_layout = QFormLayout()

        # Camera selection
        self.camera_combo = QComboBox()
        self.camera_combo.setStyleSheet(StyleSheet.COMBOBOX)
        self.populate_camera_list()
        self.camera_combo.currentIndexChanged.connect(self.change_camera)
        advanced_layout.addRow("Camera:", self.camera_combo)

        # Debug mode toggle
        self.debug_checkbox = QCheckBox("Debug Mode")
        self.debug_checkbox.setStyleSheet(StyleSheet.CHECKBOX) 
        self.debug_checkbox.stateChanged.connect(self.toggle_debug_mode)
        advanced_layout.addRow(self.debug_checkbox)

        advanced_group.setLayout(advanced_layout)
        right_layout.addWidget(advanced_group)
        # OSC Configuration
        osc_group = QGroupBox("OSC Configuration")
        osc_group.setStyleSheet(StyleSheet.GROUP_BOX)
        osc_layout = QFormLayout()
        self.osc_server_input = QLineEdit(OSC_SERVER)
        self.osc_port_input = QLineEdit(str(OSC_PORT))
        osc_layout.addRow("OSC Server:", self.osc_server_input)
        osc_layout.addRow("OSC Port:", self.osc_port_input)
        
        # Add Apply button
        self.apply_osc_button = QPushButton("Apply")
        self.apply_osc_button.setStyleSheet(StyleSheet.APPLY_BUTTON)
        self.apply_osc_button.clicked.connect(self.apply_osc_settings)
        #self.apply_osc_button.clicked.connect(lambda: self.send_key('s'))
        osc_layout.addRow("", self.apply_osc_button)
        
        osc_group.setLayout(osc_layout)
        right_layout.addWidget(osc_group)

        # Control Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.mode_button = QPushButton("Switch Mode (M)")
        self.reset_button = QPushButton("Reset (S)")
        
        for button in [self.start_button, self.stop_button, self.mode_button, self.reset_button]:
            button.setStyleSheet(StyleSheet.BUTTON)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.start_button.clicked.connect(self.start_main_program)
        self.stop_button.clicked.connect(self.stop_main_program)
        self.stop_button.setEnabled(False)
        self.mode_button.clicked.connect(lambda: self.send_key('m'))
        self.mode_button.setEnabled(False)
        self.reset_button.clicked.connect(lambda: self.send_key('s'))
        self.reset_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.mode_button)
        button_layout.addWidget(self.reset_button)
        right_layout.addLayout(button_layout)

        main_layout.addLayout(right_layout, 1)

        self.main_thread = None
    
    def populate_camera_list(self):
        self.camera_combo.clear()
        for i in range(10):  # Check first 10 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.camera_combo.addItem(f"Camera {i}")
                cap.release()

    def change_camera(self, index):
        if self.main_thread and self.main_thread.main_program:
            self.main_thread.main_program.change_camera(index)

    def toggle_debug_mode(self, state):
        if self.main_thread and self.main_thread.main_program:
            self.main_thread.main_program.set_debug_mode(state == Qt.Checked)

    def create_slider(self, name, initial_value, min_value, max_value):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(initial_value)
        slider.setStyleSheet(StyleSheet.SLIDER)
        
        if name != "Mode 1 Sensitivity":
            slider.setTickPosition(QSlider.TicksBelow)
            slider.setTickInterval(10)
        
        slider.valueChanged.connect(lambda value: self.update_config_label(name, value))
        label = QLabel(f"Current: {initial_value}")
        label.setStyleSheet(StyleSheet.LABEL)
        return slider, label

    def update_config_label(self, name, value):
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

    def update_sensitivity(self, value):
        self.sensitivity_label.setText(f"Current: {value}")
        if self.main_thread:
            # Convert the slider value (1-10) to speed_threshold (2000-100)
            speed_threshold = 2100 - (value * 200)
            self.main_thread.update_config('SENSITIVITY', speed_threshold)

    def update_touch_count(self, index):
        touch_count = 2 if index == 0 else 4
        if self.main_thread:
            self.main_thread.update_config('TOUCH_COUNT', touch_count)

    def check_initial_bpm(self):
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
        min_bpm = self.min_bpm_slider.value()
        max_bpm = self.max_bpm_slider.value()
        self.dynamic_range_bar.setRange(min_bpm, max_bpm)

    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(960, 540, Qt.KeepAspectRatio)
        self.camera_label.setPixmap(scaled_pixmap)

    def apply_osc_settings(self):
        if self.main_thread and self.main_thread.main_program:
            new_server = self.osc_server_input.text()
            new_port = int(self.osc_port_input.text())
            self.main_thread.update_config('OSC_SERVER', new_server)
            self.main_thread.update_config('OSC_PORT', new_port)
            print(f"OSC settings updated - Server: {new_server}, Port: {new_port}")
        else:
            print("Cannot update OSC settings. Main program is not running.")
        

    def start_main_program(self):
        config = {
            'INITIAL_BPM': self.initial_bpm_slider.value(),
            'MIN_BPM': self.min_bpm_slider.value(),
            'MAX_BPM': self.max_bpm_slider.value(),
            'OSC_SERVER': self.osc_server_input.text(),
            'OSC_PORT': int(self.osc_port_input.text()),
            'SENSITIVITY': 2100 - (self.sensitivity_slider.value() * 200),
            'TOUCH_COUNT': 4 if self.touch_count_combo.currentIndex() == 1 else 2,
            'CAMERA_INDEX': self.camera_combo.currentIndex(),
            'DEBUG_MODE': self.debug_checkbox.isChecked()
        }
        self.main_thread = MainThread(config)
        self.main_thread.update_bpm.connect(self.update_bpm_display)
        self.main_thread.update_frame.connect(self.update_frame)
        self.main_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.mode_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.apply_osc_button.setEnabled(True)

    def stop_main_program(self):
        if self.main_thread:
            self.main_thread.stop()
            self.main_thread.wait()
            self.main_thread = None
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.mode_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.apply_osc_button.setEnabled(False)

    def update_bpm_display(self, bpm):
        self.bpm_label.setText(f"{bpm:.1f} BPM")

    def send_key(self, key):
        if self.main_thread and self.main_thread.main_program:
            self.main_thread.send_key(key)

    def keyPressEvent(self, event):
        if self.main_thread and self.main_thread.main_program:
            if event.key() == Qt.Key_M:
                self.send_key('m')
            elif event.key() == Qt.Key_S:
                self.send_key('s')

    def closeEvent(self, event):
        self.stop_main_program()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # This can help with consistent cross-platform appearance
    window = HandTrackingGUI()
    
    # Apply label style to all labels except BPM label
    for widget in window.findChildren(QLabel):
        if widget != window.bpm_label:
            widget.setStyleSheet(StyleSheet.LABEL)
    
    window.show()
    sys.exit(app.exec_())