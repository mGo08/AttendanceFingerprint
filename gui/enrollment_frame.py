import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading


class EnrollmentFrame(ttk.Frame):
    def __init__(self, parent, arduino, db):
        super().__init__(parent)
        self.arduino = arduino
        self.db = db
        self.selected_image_path = None
        self.profile_photo = None  # Keep reference to prevent garbage collection

        # Configure grid
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()

    def setup_ui(self):
        # Title
        self.title_label = ttk.Label(
            self,
            text="Fingerprint Enrollment",
            font=("Arial", 24, "bold"),
            anchor="center"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 30))

        # Left panel - Form
        self.form_frame = ttk.LabelFrame(self, text="Student Information", padding=20)
        self.form_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=20)

        # Name field
        self.name_label = ttk.Label(self.form_frame, text="Full Name:", font=("Arial", 11, "bold"))
        self.name_label.pack(anchor="w", pady=(10, 5))

        self.name_entry = ttk.Entry(
            self.form_frame,
            font=("Arial", 11),
            width=35
        )
        self.name_entry.pack(fill="x", pady=(0, 15))

        # School ID field
        self.school_id_label = ttk.Label(self.form_frame, text="School ID:", font=("Arial", 11, "bold"))
        self.school_id_label.pack(anchor="w", pady=(0, 5))

        self.school_id_entry = ttk.Entry(
            self.form_frame,
            font=("Arial", 11),
            width=35
        )
        self.school_id_entry.pack(fill="x", pady=(0, 15))

        # Fingerprint ID field
        self.fingerprint_id_label = ttk.Label(self.form_frame, text="Fingerprint ID (1-127):",
                                              font=("Arial", 11, "bold"))
        self.fingerprint_id_label.pack(anchor="w", pady=(0, 5))

        self.fingerprint_id_entry = ttk.Entry(
            self.form_frame,
            font=("Arial", 11),
            width=35
        )
        self.fingerprint_id_entry.pack(fill="x", pady=(0, 15))

        # Profile picture section
        self.picture_label = ttk.Label(self.form_frame, text="Profile Picture:", font=("Arial", 11, "bold"))
        self.picture_label.pack(anchor="w", pady=(0, 5))

        self.picture_btn = ttk.Button(
            self.form_frame,
            text="Select Image",
            command=self.select_image
        )
        self.picture_btn.pack(fill="x", pady=(0, 20))

        # Enroll button
        self.enroll_btn = ttk.Button(
            self.form_frame,
            text="Start Enrollment",
            command=self.start_enrollment
        )
        self.enroll_btn.pack(fill="x", pady=20)

        # Right panel - Preview and status
        self.preview_frame = ttk.LabelFrame(self, text="Preview & Status", padding=20)
        self.preview_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=20)

        # Profile picture preview
        self.picture_frame = ttk.Frame(self.preview_frame)
        self.picture_frame.pack(pady=15)

        self.picture_display = ttk.Label(
            self.picture_frame,
            text="No Image\nSelected",
            font=("Arial", 12),
            anchor="center",
            background="white",
            relief="sunken",
            borderwidth=2
        )
        self.picture_display.pack(ipadx=50, ipady=50)

        # Status area
        self.status_frame = ttk.LabelFrame(self.preview_frame, text="Enrollment Status", padding=15)
        self.status_frame.pack(fill="x", pady=15)

        self.status_label = ttk.Label(
            self.status_frame,
            text="Ready for enrollment",
            font=("Arial", 12, "bold"),
            anchor="center"
        )
        self.status_label.pack(pady=10)

        # Progress indicator
        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(pady=10, fill="x")

        # Enrolled users list
        self.users_frame = ttk.LabelFrame(self.preview_frame, text="Enrolled Users", padding=10)
        self.users_frame.pack(fill="both", expand=True, pady=(15, 0))

        # Create scrollable text widget with scrollbar
        self.users_text_frame = ttk.Frame(self.users_frame)
        self.users_text_frame.pack(fill="both", expand=True)

        self.users_text = tk.Text(
            self.users_text_frame,
            height=8,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.users_scrollbar = ttk.Scrollbar(
            self.users_text_frame,
            orient="vertical",
            command=self.users_text.yview
        )
        self.users_text.configure(yscrollcommand=self.users_scrollbar.set)

        self.users_text.pack(side="left", fill="both", expand=True)
        self.users_scrollbar.pack(side="right", fill="y")

        # Load existing users
        self.refresh_ui()

    def select_image(self):
        """Select profile picture"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=filetypes
        )

        if filename:
            self.selected_image_path = filename
            self.display_selected_image(filename)
            self.picture_btn.configure(text="Image Selected ✓")

    def display_selected_image(self, image_path):
        """Display selected image in preview"""
        try:
            image = Image.open(image_path)
            image = image.resize((150, 150), Image.Resampling.LANCZOS)
            self.profile_photo = ImageTk.PhotoImage(image)
            self.picture_display.configure(image=self.profile_photo, text="")
        except Exception as e:
            print(f"Error loading image: {e}")
            self.picture_display.configure(text="Error loading\nimage", image="")

    def validate_form(self):
        """Validate form inputs"""
        name = self.name_entry.get().strip()
        school_id = self.school_id_entry.get().strip()
        fingerprint_id = self.fingerprint_id_entry.get().strip()

        if not name:
            self.show_error("Please enter student's name")
            return False

        if not school_id:
            self.show_error("Please enter school ID")
            return False

        if not fingerprint_id:
            self.show_error("Please enter fingerprint ID")
            return False

        try:
            fid = int(fingerprint_id)
            if fid < 1 or fid > 127:
                self.show_error("Fingerprint ID must be between 1 and 127")
                return False
        except ValueError:
            self.show_error("Fingerprint ID must be a number")
            return False

        # Check if IDs already exist
        if self.db.fingerprint_id_exists(fid):
            self.show_error(f"Fingerprint ID {fid} already exists")
            return False

        if self.db.school_id_exists(school_id):
            self.show_error(f"School ID {school_id} already exists")
            return False

        return True

    def start_enrollment(self):
        """Start fingerprint enrollment process"""
        if not self.arduino.is_connected:
            self.show_error("Arduino not connected!")
            return

        if not self.validate_form():
            return

        # Disable form during enrollment
        self.set_form_enabled(False)
        self.progress_bar['value'] = 0
        self.status_label.configure(text="Starting enrollment...")

        # Start enrollment in separate thread
        fingerprint_id = int(self.fingerprint_id_entry.get())
        thread = threading.Thread(
            target=self.enrollment_process,
            args=(fingerprint_id,),
            daemon=True
        )
        thread.start()

    def enrollment_process(self, fingerprint_id):
        """Handle enrollment process"""
        try:
            # Update status
            self.after(0, self.update_status, "Preparing enrollment...", 10)

            # Start Arduino enrollment
            self.arduino.start_enrollment_mode(fingerprint_id)

            # Update status
            self.after(0, self.update_status, "Place finger on sensor...", 30)

            # Wait for enrollment completion (simplified - in real implementation,
            # you'd want to listen for Arduino responses)
            import time
            time.sleep(2)
            self.after(0, self.update_status, "Processing first scan...", 50)

            time.sleep(3)
            self.after(0, self.update_status, "Remove finger...", 70)

            time.sleep(2)
            self.after(0, self.update_status, "Place finger again...", 80)

            time.sleep(3)
            self.after(0, self.update_status, "Creating fingerprint model...", 90)

            time.sleep(2)

            # Simulate successful enrollment
            self.after(0, self.enrollment_success)

        except Exception as e:
            self.after(0, self.enrollment_failed, str(e))

    def enrollment_success(self):
        """Handle successful enrollment"""
        # Save to database
        name = self.name_entry.get().strip()
        school_id = self.school_id_entry.get().strip()
        fingerprint_id = int(self.fingerprint_id_entry.get())

        success = self.db.add_user(
            fingerprint_id,
            name,
            school_id,
            self.selected_image_path
        )

        if success:
            self.update_status("✅ Enrollment successful!", 100)
            self.clear_form()
            self.refresh_users_list()
            messagebox.showinfo("Success", f"Successfully enrolled {name}!")
        else:
            self.update_status("❌ Database error", 0)
            messagebox.showerror("Error", "Failed to save to database")

        self.set_form_enabled(True)

    def enrollment_failed(self, error):
        """Handle failed enrollment"""
        self.update_status(f"❌ Enrollment failed: {error}", 0)
        self.set_form_enabled(True)
        messagebox.showerror("Enrollment Failed", f"Error: {error}")

    def update_status(self, message, progress):
        """Update status and progress"""
        self.status_label.configure(text=message)
        self.progress_bar['value'] = progress

    def set_form_enabled(self, enabled):
        """Enable/disable form controls"""
        state = "normal" if enabled else "disabled"
        self.name_entry.configure(state=state)
        self.school_id_entry.configure(state=state)
        self.fingerprint_id_entry.configure(state=state)
        self.picture_btn.configure(state=state)
        self.enroll_btn.configure(state=state)

    def clear_form(self):
        """Clear form fields"""
        self.name_entry.delete(0, "end")
        self.school_id_entry.delete(0, "end")
        self.fingerprint_id_entry.delete(0, "end")
        self.selected_image_path = None
        self.profile_photo = None
        self.picture_display.configure(image="", text="No Image\nSelected")
        self.picture_btn.configure(text="Select Image")
        self.progress_bar['value'] = 0
        self.status_label.configure(text="Ready for enrollment")

    def refresh_users_list(self):
        """Refresh the enrolled users list"""
        users = self.db.get_all_users()
        self.users_text.configure(state="normal")
        self.users_text.delete("1.0", "end")

        if users:
            for user in users:
                line = f"ID: {user['fingerprint_id']} - {user['name']} ({user['school_id']})\n"
                self.users_text.insert("end", line)
        else:
            self.users_text.insert("end", "No users enrolled yet.")

        self.users_text.configure(state="disabled")

    def refresh_ui(self):
        """Refresh UI components"""
        self.refresh_users_list()

    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)