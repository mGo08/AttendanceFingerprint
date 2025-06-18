import serial
import threading
import time
from typing import Callable, Optional


class ArduinoComm:
    def __init__(self, port: str = "COM4", baudrate: int = 9600):  # Changed from COM3 to COM4
        self.port = port
        self.baudrate = baudrate
        self.serial_conn: Optional[serial.Serial] = None
        self.is_connected = False
        self.detection_callback: Optional[Callable] = None
        self.listening = False
        self.listen_thread: Optional[threading.Thread] = None

    def connect(self) -> bool:
        """Connect to Arduino"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to Arduino: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """Disconnect from Arduino"""
        self.stop_listening()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.is_connected = False

    def send_command(self, command: str) -> bool:
        """Send command to Arduino"""
        if not self.is_connected or not self.serial_conn:
            return False

        try:
            self.serial_conn.write(f"{command}\n".encode())
            return True
        except Exception as e:
            print(f"Failed to send command: {e}")
            return False

    def start_detection_mode(self):
        """Start fingerprint detection mode"""
        if self.send_command("d"):
            self.start_listening()

    def start_enrollment_mode(self, fingerprint_id: int):
        """Start fingerprint enrollment mode"""
        if self.send_command("e"):
            time.sleep(0.5)
            self.send_command(str(fingerprint_id))

    def set_detection_callback(self, callback: Callable):
        """Set callback function for detection events"""
        self.detection_callback = callback

    def start_listening(self):
        """Start listening for Arduino messages"""
        if not self.listening and self.is_connected:
            self.listening = True
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()

    def stop_listening(self):
        """Stop listening for Arduino messages"""
        self.listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1)

    def _listen_loop(self):
        """Main listening loop"""
        while self.listening and self.is_connected and self.serial_conn:
            try:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode().strip()
                    if line:
                        self._process_message(line)
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in listen loop: {e}")
                break

    def _process_message(self, message: str):
        """Process incoming Arduino messages"""
        print(f"Arduino: {message}")

        # Check for successful detection
        if "ACCESS GRANTED - ID #" in message:
            try:
                # Extract ID from message like "✓ ACCESS GRANTED - ID #3 detected!"
                parts = message.split("ID #")
                if len(parts) > 1:
                    id_part = parts[1].split()[0]
                    fingerprint_id = int(id_part)
                    if self.detection_callback:
                        self.detection_callback(fingerprint_id)
            except (ValueError, IndexError) as e:
                print(f"Error parsing fingerprint ID: {e}")

        # Check for enrollment success
        elif "Enrollment successful!" in message:
            print("Fingerprint enrolled successfully")

        # Check for enrollment failure
        elif "Fingerprints did not match" in message:
            print("Enrollment failed - fingerprints didn't match")

    def get_available_ports(self) -> list:
        """Get list of available serial ports"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]