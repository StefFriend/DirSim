import rtmidi
from pythonosc import udp_client
from pythonosc import osc_message_builder
import sys
import time
import msvcrt  # Used for detecting keypress on Windows

def list_midi_ports():
    available_ports = midi_in.get_ports()
    if available_ports:
        print("Available MIDI input ports:")
        for i, port_name in enumerate(available_ports):
            print(f"{i}: {port_name}")
        return available_ports
    else:
        print("No MIDI input ports available.")
        sys.exit()

def select_midi_port(ports):
    while True:
        port_index = input("Enter the index of the MIDI port to use: ")
        if port_index.isdigit() and int(port_index) < len(ports):
            return int(port_index)
        else:
            print("Invalid index. Please enter a valid port index.")

def check_for_exit_key():
    if msvcrt.kbhit():
        if ord(msvcrt.getch()) == 27:  # ESC key
            print("Exiting...")
            sys.exit()

midi_in = rtmidi.MidiIn()
ports = list_midi_ports()
selected_port_index = select_midi_port(ports)
midi_in.open_port(selected_port_index)

osc_client = udp_client.SimpleUDPClient("127.0.0.1", 57120)  # replace port if needed

def midi_callback(message, time_stamp):
    message, deltatime = message
    status_byte = message[0]
    midi_channel = (status_byte & 0x0F) + 1  # Extracting MIDI channel (0-15) and converting to 1-16
    message_type = status_byte & 0xF0

    print(f"MIDI message on channel {midi_channel}: {message}")

    osc_msg = osc_message_builder.OscMessageBuilder(address=f"/midi/{midi_channel}")
    osc_msg.add_arg(message_type)  # MIDI status (with channel stripped)
    osc_msg.add_arg(message[1])    # MIDI note
    osc_msg.add_arg(message[2])    # MIDI velocity
    osc_msg = osc_msg.build()

    osc_client.send(osc_msg)

midi_in.set_callback(midi_callback)

print("Press 'ESC' to exit.")

try:
    while True:
        check_for_exit_key()
        time.sleep(0.1)  # To reduce CPU usage
except KeyboardInterrupt:
    pass
finally:
    midi_in.close_port()
    del midi_in
