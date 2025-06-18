# Fingerprint Attendance System

Fingerprint Attendance System is a desktop app to help you track student attendance using fingerprint scanning with Arduino and R307 sensor.

---

## Features

- Track student attendance with fingerprint scanning and timestamps.
- Enroll students with names, IDs, and profile pictures.
- View attendance records with filtering and export capabilities.
- Real-time fingerprint detection with visual feedback.
- Modern dark-themed interface with easy navigation.

---

## Getting Started

### Requirements

- Python 3.8+
- Tkinter (usually included with Python)
- `sv_ttk` for modern theming (`pip install sv_ttk`)
---

### Running the App

1. Clone or download the repository.
2. Ensure all dependencies are installed.
3. Run the main script:
   ```bash
   python main.py
   
## Troubleshooting
### Configuration
Arduino COM Port
The default COM port is set to COM3. To change it:

Open arduino/arduino_comm.py
Modify the default port in the 
   ```bash __init__ method:
pythondef __init__(self, port: str = "YOUR_PORT", baudrate: int = 9600):