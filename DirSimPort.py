import sys
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QComboBox, 
                             QPushButton, QLabel, QTextEdit, QLineEdit)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QColor, QPalette
import rtmidi
from pythonosc import udp_client
from pythonosc import osc_message_builder

class MidiThread(QThread):
    midi_signal = pyqtSignal(list, float)

    def __init__(self, midi_in):
        super().__init__()
        self.midi_in = midi_in
        self.running = True

    def run(self):
        while self.running:
            msg = self.midi_in.get_message()
            if msg:
                message, timestamp = msg
                self.midi_signal.emit(message, timestamp)
            time.sleep(0.001)

    def stop(self):
        self.running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DirSim Port")
        self.setGeometry(100, 100, 400, 300)

        self.midi_in = rtmidi.MidiIn()
        self.osc_client = None

        self.init_ui()
        self.set_color_scheme()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # MIDI Interface selection
        midi_layout = QHBoxLayout()
        midi_layout.addWidget(QLabel("MIDI Interface:"))
        self.midi_combo = QComboBox()
        self.update_midi_ports()
        midi_layout.addWidget(self.midi_combo)
        layout.addLayout(midi_layout)

        # OSC Configuration
        osc_layout = QHBoxLayout()
        osc_layout.addWidget(QLabel("OSC Server:"))
        self.osc_server = QLineEdit("127.0.0.1")
        osc_layout.addWidget(self.osc_server)
        osc_layout.addWidget(QLabel("Port:"))
        self.osc_port = QLineEdit("57121")
        osc_layout.addWidget(self.osc_port)
        self.apply_osc_button = QPushButton("Apply")
        self.apply_osc_button.clicked.connect(self.apply_osc_settings)
        osc_layout.addWidget(self.apply_osc_button)
        layout.addLayout(osc_layout)

        # Start/Stop button
        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.clicked.connect(self.toggle_midi)
        layout.addWidget(self.start_stop_button)

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.midi_thread = None

    def set_color_scheme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))  # White background
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))  # Black text
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))  # White background for input fields
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))  # Blue highlight
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)

        # Set blue color for buttons
        button_style = """
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #004c82;
            }
        """
        self.start_stop_button.setStyleSheet(button_style)
        self.apply_osc_button.setStyleSheet(button_style)

        # Set custom style for dropdown menu
        self.midi_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #0078D7;
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
                background: white;
                color: black;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #0078D7;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }


            QComboBox QAbstractItemView {
                border: 1px solid #0078D7;
                selection-background-color: #E5F1FB;
                selection-color: black;
                background-color: white;
                outline: 0px;
            }

            QComboBox QAbstractItemView::item {
                padding: 4px;
                margin: 0px;
            }

            QComboBox QAbstractItemView::item:hover {
                background-color: #E5F1FB;
            }

            QComboBox QAbstractItemView::item:selected {
                background-color: #CCE4F7;
            }
        """)

    def update_midi_ports(self):
        self.midi_combo.clear()
        ports = self.midi_in.get_ports()
        self.midi_combo.addItems(ports)

    def apply_osc_settings(self):
        server = self.osc_server.text()
        port = int(self.osc_port.text())
        self.osc_client = udp_client.SimpleUDPClient(server, port)
        self.log_area.append(f"OSC settings applied: {server}:{port}")

    def toggle_midi(self):
        if self.midi_thread is None:
            self.start_midi()
        else:
            self.stop_midi()

    def start_midi(self):
        if self.osc_client is None:
            self.log_area.append("Please apply OSC settings before starting.")
            return

        port_index = self.midi_combo.currentIndex()
        if port_index >= 0:
            self.midi_in.open_port(port_index)
            self.midi_thread = MidiThread(self.midi_in)
            self.midi_thread.midi_signal.connect(self.handle_midi_message)
            self.midi_thread.start()
            self.start_stop_button.setText("Stop")
            self.log_area.append("MIDI processing started.")
        else:
            self.log_area.append("Please select a MIDI port.")

    def stop_midi(self):
        if self.midi_thread:
            self.midi_thread.stop()
            self.midi_thread.wait()
            self.midi_thread = None
            self.midi_in.close_port()
            self.start_stop_button.setText("Start")
            self.log_area.append("MIDI processing stopped.")

    def handle_midi_message(self, message, timestamp):
        if not message:
            return

        status_byte = message[0]
        midi_channel = (status_byte & 0x0F) + 1
        message_type = status_byte & 0xF0

        log_message = f"MIDI message on channel {midi_channel}: {message}"
        self.log_area.append(log_message)

        osc_msg = osc_message_builder.OscMessageBuilder(address=f"/midi/{midi_channel}")
        osc_msg.add_arg(message_type)
        
        # Add data bytes if they exist
        for i in range(1, len(message)):
            osc_msg.add_arg(message[i])

        osc_msg = osc_msg.build()
        self.osc_client.send(osc_msg)

    def closeEvent(self, event):
        self.stop_midi()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())