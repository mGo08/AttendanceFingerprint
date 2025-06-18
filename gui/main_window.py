
from tkinter import ttk, messagebox
from gui.enrollment_frame import EnrollmentFrame
from gui.detection_frame import DetectionFrame
from gui.records_frame import RecordsFrame
from arduino.arduino_comm import ArduinoComm
from database.db_manager import DatabaseManager


class MainWindow:
    def __init__(self, root):
        self.root = root

        # Initialize components
        self.arduino = ArduinoComm()
        self.db = DatabaseManager()

        # Configure window
        self.root.title("Fingerprint Attendance System")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)

        # Configure grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.setup_ui()
        self.setup_arduino()

        # Setup window closing protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # Create sidebar frame with modern styling
        self.sidebar = ttk.Frame(self.root, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(15, 8), pady=15)
        self.sidebar.grid_rowconfigure(7, weight=1)
        self.sidebar.grid_propagate(False)

        # Header section
        self.header_frame = ttk.LabelFrame(self.sidebar, text="System Status", padding=15)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 15))

        # System title with modern styling
        self.sidebar_title = ttk.Label(
            self.header_frame,
            text="Fingerprint\nAttendance System",
            font=("Segoe UI", 12, "bold"),
            anchor="center"
        )
        self.sidebar_title.pack(pady=(0, 10))

        # Connection status with improved indicators
        self.status_frame = ttk.Frame(self.header_frame)
        self.status_frame.pack(fill="x", pady=5)

        self.connection_status = ttk.Label(
            self.status_frame,
            text="⚫ Disconnected",
            font=("Segoe UI", 9)
        )
        self.connection_status.pack()

        # Connect button with modern styling
        self.connect_btn = ttk.Button(
            self.header_frame,
            text="🔌 Connect Arduino",
            command=self.toggle_arduino_connection
        )
        self.connect_btn.pack(fill="x", pady=(10, 0))

        # Navigation section
        self.nav_frame = ttk.LabelFrame(self.sidebar, text="Navigation", padding=15)
        self.nav_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        # Navigation buttons with icons and modern styling
        self.detection_btn = ttk.Button(
            self.nav_frame,
            text="👁️ Detection",
            command=self.show_detection
        )
        self.detection_btn.pack(fill="x", pady=5)

        self.enrollment_btn = ttk.Button(
            self.nav_frame,
            text="📝 Enrollment",
            command=self.show_enrollment
        )
        self.enrollment_btn.pack(fill="x", pady=5)

        self.records_btn = ttk.Button(
            self.nav_frame,
            text="📊 Records",
            command=self.show_records
        )
        self.records_btn.pack(fill="x", pady=5)

        # Quick stats section
        self.stats_frame = ttk.LabelFrame(self.sidebar, text="Quick Stats", padding=15)
        self.stats_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        self.total_users_label = ttk.Label(
            self.stats_frame,
            text="👥 Total Users: 0",
            font=("Segoe UI", 9)
        )
        self.total_users_label.pack(anchor="w", pady=2)

        self.today_attendance_label = ttk.Label(
            self.stats_frame,
            text="📅 Today's Attendance: 0",
            font=("Segoe UI", 9)
        )
        self.today_attendance_label.pack(anchor="w", pady=2)

        # Main content area with modern frame
        self.main_container = ttk.Frame(self.root)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=(8, 15), pady=15)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.main_frame = ttk.Frame(self.main_container)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Initialize frames
        self.detection_frame = DetectionFrame(self.main_frame, self.arduino, self.db)
        self.enrollment_frame = EnrollmentFrame(self.main_frame, self.arduino, self.db)
        self.records_frame = RecordsFrame(self.main_frame, self.db)

        # Show detection frame by default
        self.show_detection()
        self.update_stats()

    def setup_arduino(self):
        """Setup Arduino communication"""
        self.arduino.set_detection_callback(self.on_fingerprint_detected)

    def toggle_arduino_connection(self):
        """Toggle Arduino connection"""
        if not self.arduino.is_connected:
            if self.arduino.connect():
                self.connection_status.configure(text="🟢 Connected")
                self.connect_btn.configure(text="🔌 Disconnect")
            else:
                self.show_error("Failed to connect to Arduino")
        else:
            self.arduino.disconnect()
            self.connection_status.configure(text="⚫ Disconnected")
            self.connect_btn.configure(text="🔌 Connect Arduino")

    def update_stats(self):
        """Update sidebar statistics"""
        total_users = len(self.db.get_all_users()) if hasattr(self.db, 'get_all_users') else 0
        # You can implement today's attendance count similarly
        today_count = 0  # Implement this based on your database structure

        self.total_users_label.configure(text=f"👥 Total Users: {total_users}")
        self.today_attendance_label.configure(text=f"📅 Today's Attendance: {today_count}")

    def on_fingerprint_detected(self, fingerprint_id: int):
        """Handle fingerprint detection"""
        self.detection_frame.on_fingerprint_detected(fingerprint_id)
        self.update_stats()

    def show_detection(self):
        """Show detection frame"""
        self.hide_all_frames()
        self.detection_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.update_button_states("detection")

    def show_enrollment(self):
        """Show enrollment frame"""
        self.hide_all_frames()
        self.enrollment_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.enrollment_frame.refresh_ui()
        self.update_button_states("enrollment")

    def show_records(self):
        """Show records frame"""
        self.hide_all_frames()
        self.records_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        if hasattr(self.records_frame, 'refresh_logs'):
            self.records_frame.refresh_logs()
        self.update_button_states("records")

    def update_button_states(self, active_button):
        """Update button states to show active button"""
        # Reset all buttons
        buttons = {
            "detection": self.detection_btn,
            "enrollment": self.enrollment_btn,
            "records": self.records_btn
        }

        for name, btn in buttons.items():
            if name == active_button:
                btn.state(['pressed'])
            else:
                btn.state(['!pressed'])

    def hide_all_frames(self):
        """Hide all content frames"""
        self.detection_frame.grid_forget()
        self.enrollment_frame.grid_forget()
        self.records_frame.grid_forget()

    def show_error(self, message: str):
        """Show error dialog"""
        messagebox.showerror("Error", message)

    def on_closing(self):
        """Handle window closing"""
        self.arduino.disconnect()
        self.root.destroy()