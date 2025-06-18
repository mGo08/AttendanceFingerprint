import tkinter as tk
from tkinter import ttk, messagebox

import sv_ttk
from PIL import Image, ImageTk
import io
from datetime import datetime


class DetectionFrame(ttk.Frame):
    def __init__(self, parent, arduino, db):
        super().__init__(parent)
        self.arduino = arduino
        self.db = db

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()
        self.detection_active = False

    def setup_ui(self):
        # Header section
        self.header_frame = ttk.Frame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(1, weight=1)

        # Title with modern typography
        self.title_label = ttk.Label(
            self.header_frame,
            text="🔍 Fingerprint Detection",
            font=("Segoe UI", 24, "bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        # Status indicator
        self.header_status = ttk.Label(
            self.header_frame,
            text="Ready",
            font=("Segoe UI", 12)
        )
        self.header_status.grid(row=0, column=1, sticky="e")

        # Main content area
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure((0, 1), weight=1)
        self.content_frame.grid_rowconfigure(0, weight=2)
        self.content_frame.grid_rowconfigure(1, weight=1)

        # Left panel - Detection control
        self.control_panel = ttk.LabelFrame(
            self.content_frame,
            text="🎛️ Detection Control",
            padding=20
        )
        self.control_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Detection status with larger, more prominent display
        self.status_frame = ttk.Frame(self.control_panel)
        self.status_frame.pack(fill="x", pady=(0, 20))

        self.status_label = ttk.Label(
            self.status_frame,
            text="Ready for Detection",
            font=("Segoe UI", 16, "bold"),
            anchor="center"
        )
        self.status_label.pack()

        # Modern fingerprint visualization
        self.visual_frame = ttk.Frame(self.control_panel)
        self.visual_frame.pack(expand=True, fill="both", pady=20)

        self.fingerprint_canvas = tk.Canvas(
            self.visual_frame,
            height=200,
            bg="#2d2d30" if sv_ttk.get_theme() == "dark" else "#ffffff",
            highlightthickness=0
        )
        self.fingerprint_canvas.pack(expand=True, fill="both")

        # Control buttons with modern styling
        self.button_frame = ttk.Frame(self.control_panel)
        self.button_frame.pack(fill="x", pady=(20, 0))

        self.start_btn = ttk.Button(
            self.button_frame,
            text="▶️ Start Detection",
            command=self.toggle_detection,
            style="Accent.TButton"
        )
        self.start_btn.pack(fill="x", pady=5)

        # Right panel - User information
        self.info_panel = ttk.LabelFrame(
            self.content_frame,
            text="👤 User Information",
            padding=20
        )
        self.info_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Profile section with modern card-like design
        self.profile_card = ttk.Frame(self.info_panel)
        self.profile_card.pack(fill="x", pady=(0, 20))

        self.profile_frame = ttk.Frame(self.profile_card)
        self.profile_frame.pack(pady=10)

        self.profile_label = ttk.Label(
            self.profile_frame,
            text="👤",
            font=("Segoe UI", 48),
            anchor="center"
        )
        self.profile_label.pack()

        # User details with improved spacing and typography
        self.details_frame = ttk.Frame(self.info_panel)
        self.details_frame.pack(fill="x", pady=10)

        detail_font = ("Segoe UI", 11)

        self.name_label = ttk.Label(
            self.details_frame,
            text="📝 Name: Not detected",
            font=detail_font
        )
        self.name_label.pack(anchor="w", pady=5)

        self.school_id_label = ttk.Label(
            self.details_frame,
            text="🆔 School ID: Not detected",
            font=detail_font
        )
        self.school_id_label.pack(anchor="w", pady=5)

        self.timestamp_label = ttk.Label(
            self.details_frame,
            text="🕐 Last Detection: Never",
            font=("Segoe UI", 10),
            foreground="gray"
        )
        self.timestamp_label.pack(anchor="w", pady=10)

        # Activity log section
        self.log_panel = ttk.LabelFrame(
            self.content_frame,
            text="📋 Activity Log",
            padding=15
        )
        self.log_panel.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(20, 0))
        self.log_panel.grid_columnconfigure(0, weight=1)
        self.log_panel.grid_rowconfigure(0, weight=1)

        # Modern log display with scrollbar
        self.log_frame = ttk.Frame(self.log_panel)
        self.log_frame.grid(row=0, column=0, sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)

        self.log_text = tk.Text(
            self.log_frame,
            height=6,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state="disabled"
        )
        self.log_scrollbar = ttk.Scrollbar(
            self.log_frame,
            orient="vertical",
            command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=self.log_scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.log_scrollbar.grid(row=0, column=1, sticky="ns")

    def draw_fingerprint_icon(self):
        """Draw a modern fingerprint icon on canvas"""
        canvas = self.fingerprint_canvas
        canvas.delete("all")

        # Get canvas dimensions
        width = canvas.winfo_reqwidth() if canvas.winfo_reqwidth() > 1 else 200
        height = canvas.winfo_reqheight() if canvas.winfo_reqheight() > 1 else 200

        center_x, center_y = width // 2, height // 2

        # Draw concentric fingerprint lines
        colors = ["#4a9eff", "#66b3ff", "#80ccff", "#99d6ff"]
        for i, color in enumerate(colors):
            radius = 30 + (i * 15)
            canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                outline=color, width=2, fill=""
            )

    def toggle_detection(self):
        """Toggle fingerprint detection"""
        if not self.arduino.is_connected:
            self.show_error("Arduino not connected!")
            return

        if not self.detection_active:
            self.start_detection()
        else:
            self.stop_detection()

    def start_detection(self):
        """Start fingerprint detection"""
        self.detection_active = True
        self.start_btn.configure(text="⏹️ Stop Detection")
        self.status_label.configure(text="Scanning... Place finger on sensor")
        self.header_status.configure(text="🔍 Scanning")

        # Start Arduino detection mode
        self.arduino.start_detection_mode()

        # Start UI animation
        self.animate_scanning()

    def stop_detection(self):
        """Stop fingerprint detection"""
        self.detection_active = False
        self.start_btn.configure(text="▶️ Start Detection")
        self.status_label.configure(text="Detection Stopped")
        self.header_status.configure(text="⏸️ Stopped")

        # Send menu command to stop detection
        self.arduino.send_command("m")

    def animate_scanning(self):
        """Animate scanning indicator"""
        if self.detection_active:
            # Create a pulsing effect on the canvas
            canvas = self.fingerprint_canvas
            canvas.delete("pulse")

            width = canvas.winfo_width()
            height = canvas.winfo_height()
            center_x, center_y = width // 2, height // 2

            # Draw pulsing circle
            import math
            pulse_radius = 20 + (10 * math.sin(tk._default_root.tk.call("clock", "seconds") * 3))
            canvas.create_oval(
                center_x - pulse_radius, center_y - pulse_radius,
                center_x + pulse_radius, center_y + pulse_radius,
                outline="#ff6b6b", width=3, tags="pulse"
            )

            # Schedule next animation frame
            self.after(100, self.animate_scanning)

    def on_fingerprint_detected(self, fingerprint_id: int):
        """Handle successful fingerprint detection"""
        self.after(0, self._process_detection, fingerprint_id)

    def _process_detection(self, fingerprint_id: int):
        """Process fingerprint detection in main thread"""
        user = self.db.get_user_by_fingerprint(fingerprint_id)

        if user:
            self.db.log_attendance(user['id'])
            self.display_user_info(user)
            self.add_to_log(user['name'], user['school_id'], "✅ Access Granted")
            self.flash_success()
        else:
            self.status_label.configure(text="❌ Unknown fingerprint detected!")
            self.header_status.configure(text="❌ Unknown")
            self.add_to_log("Unknown User", f"ID: {fingerprint_id}", "❌ Access Denied")
            self.after(3000, self.reset_display)

    def display_user_info(self, user):
        """Display detected user information"""
        self.name_label.configure(text=f"📝 Name: {user['name']}")
        self.school_id_label.configure(text=f"🆔 School ID: {user['school_id']}")
        self.timestamp_label.configure(text=f"🕐 Detected: {datetime.now().strftime('%H:%M:%S')}")

        # Display profile picture if available
        if user.get('profile_picture'):
            try:
                image = Image.open(io.BytesIO(user['profile_picture']))
                image = image.resize((80, 80), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.profile_label.configure(image=photo, text="")
                self.profile_label.image = photo  # Keep reference
            except Exception as e:
                print(f"Error loading profile picture: {e}")
                self.profile_label.configure(text="👤", image="")
        else:
            self.profile_label.configure(text="👤", image="")

    def flash_success(self):
        """Flash success indication"""
        self.status_label.configure(text="✅ Access Granted!")
        self.header_status.configure(text="✅ Success")
        self.after(3000, self.reset_display)

    def reset_display(self):
        """Reset display to scanning state"""
        if self.detection_active:
            self.status_label.configure(text="Scanning... Place finger on sensor")
            self.header_status.configure(text="🔍 Scanning")
        else:
            self.status_label.configure(text="Ready for Detection")
            self.header_status.configure(text="Ready")

    def add_to_log(self, name: str, school_id: str, status: str):
        """Add detection to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {name} ({school_id}) - {status}\n"

        self.log_text.configure(state="normal")
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def show_error(self, message: str):
        """Show error message"""
        messagebox.showerror("Error", message)
