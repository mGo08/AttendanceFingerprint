import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv
from PIL import Image, ImageTk
import io


class RecordsFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.setup_ui()
        self.refresh_logs()

    def setup_ui(self):
        # Title
        self.title_label = ttk.Label(
            self,
            text="Attendance Records",
            font=("Arial", 20, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=(20, 30))

        # Control panel
        self.control_frame = ttk.LabelFrame(self, text="Filters & Controls", padding=20)
        self.control_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 20))
        self.control_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Date filter
        self.date_label = ttk.Label(self.control_frame, text="Date Filter:")
        self.date_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.date_var = tk.StringVar(value="today")
        self.date_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.date_var,
            values=["today", "yesterday", "last_week", "last_month", "all"],
            state="readonly",
            width=12
        )
        self.date_combo.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.date_combo.bind("<<ComboboxSelected>>", self.on_date_filter_changed)

        # Student filter
        self.student_label = ttk.Label(self.control_frame, text="Student Filter:")
        self.student_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.student_var = tk.StringVar()
        self.student_entry = ttk.Entry(
            self.control_frame,
            textvariable=self.student_var,
            width=15
        )
        self.student_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.student_entry.bind("<KeyRelease>", self.on_student_filter_changed)

        # Search button
        self.search_btn = ttk.Button(
            self.control_frame,
            text="🔍 Search",
            command=self.apply_filters
        )
        self.search_btn.grid(row=1, column=2, padx=10, pady=5, sticky="ew")

        # Refresh button
        self.refresh_btn = ttk.Button(
            self.control_frame,
            text="🔄 Refresh",
            command=self.refresh_logs
        )
        self.refresh_btn.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # Export button
        self.export_btn = ttk.Button(
            self.control_frame,
            text="📥 Export CSV",
            command=self.export_to_csv
        )
        self.export_btn.grid(row=1, column=4, padx=5, pady=5, sticky="ew")

        # Records display area
        self.records_frame = ttk.LabelFrame(self, text="Attendance Logs", padding=10)
        self.records_frame.grid(row=2, column=0, sticky="nsew", padx=40, pady=(0, 20))
        self.records_frame.grid_columnconfigure(0, weight=1)
        self.records_frame.grid_rowconfigure(1, weight=1)

        # Summary frame
        self.summary_frame = ttk.Frame(self.records_frame)
        self.summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.summary_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Summary labels
        self.total_label = ttk.Label(
            self.summary_frame,
            text="Total Records: 0",
            font=("Arial", 12, "bold")
        )
        self.total_label.grid(row=0, column=0, padx=10, pady=5)

        self.unique_students_label = ttk.Label(
            self.summary_frame,
            text="Unique Students: 0",
            font=("Arial", 12, "bold")
        )
        self.unique_students_label.grid(row=0, column=1, padx=10, pady=5)

        self.today_label = ttk.Label(
            self.summary_frame,
            text="Today's Records: 0",
            font=("Arial", 12, "bold")
        )
        self.today_label.grid(row=0, column=2, padx=10, pady=5)

        self.last_update_label = ttk.Label(
            self.summary_frame,
            text="Last Updated: -",
            font=("Arial", 10)
        )
        self.last_update_label.grid(row=0, column=3, padx=10, pady=5)

        # Treeview for records
        self.tree_frame = ttk.Frame(self.records_frame)
        self.tree_frame.grid(row=1, column=0, sticky="nsew")
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

        # Define columns
        columns = ("ID", "Name", "School ID", "Date", "Time", "Status")
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings",
            height=15
        )

        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Student Name")
        self.tree.heading("School ID", text="School ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Status", text="Status")

        # Set column widths
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=200, anchor="w")
        self.tree.column("School ID", width=120, anchor="center")
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Time", width=100, anchor="center")
        self.tree.column("Status", width=100, anchor="center")

        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.h_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Grid treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_record_double_click)

        # Context menu
        self.setup_context_menu()

    def setup_context_menu(self):
        """Setup right-click context menu"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self.view_record_details)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Record", command=self.delete_record)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Export Selected", command=self.export_selected)

        # Bind right-click
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Show context menu"""
        # Select the item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def refresh_logs(self):
        """Refresh attendance logs"""
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Get logs from database
            logs = self.db.get_attendance_logs()

            if logs:
                for log in logs:
                    # Format datetime
                    timestamp = datetime.fromisoformat(log['timestamp'])
                    date_str = timestamp.strftime("%Y-%m-%d")
                    time_str = timestamp.strftime("%H:%M:%S")

                    # Insert into treeview
                    self.tree.insert("", "end", values=(
                        log['id'],
                        log['name'],
                        log['school_id'],
                        date_str,
                        time_str,
                        "Present"
                    ))

            # Update summary
            self.update_summary(logs)
            self.last_update_label.configure(
                text=f"Last Updated: {datetime.now().strftime('%H:%M:%S')}"
            )

        except Exception as e:
            self.show_error(f"Error loading records: {e}")

    def update_summary(self, logs):
        """Update summary statistics"""
        if not logs:
            self.total_label.configure(text="Total Records: 0")
            self.unique_students_label.configure(text="Unique Students: 0")
            self.today_label.configure(text="Today's Records: 0")
            return

        total_records = len(logs)
        unique_students = len(set(log['school_id'] for log in logs))

        # Count today's records
        today = datetime.now().date()
        today_records = sum(1 for log in logs
                            if datetime.fromisoformat(log['timestamp']).date() == today)

        self.total_label.configure(text=f"Total Records: {total_records}")
        self.unique_students_label.configure(text=f"Unique Students: {unique_students}")
        self.today_label.configure(text=f"Today's Records: {today_records}")

    def on_date_filter_changed(self, event=None):
        """Handle date filter change"""
        self.apply_filters()

    def on_student_filter_changed(self, event=None):
        """Handle student filter change"""
        # Apply filter after a short delay to avoid excessive filtering
        if hasattr(self, '_filter_timer'):
            self.after_cancel(self._filter_timer)
        self._filter_timer = self.after(500, self.apply_filters)

    def apply_filters(self):
        """Apply current filters to the records"""
        try:
            # Get filter values
            date_filter = self.date_var.get()
            student_filter = self.student_var.get().strip().lower()

            # Calculate date range
            end_date = datetime.now()
            if date_filter == "today":
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_filter == "yesterday":
                start_date = (end_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
            elif date_filter == "last_week":
                start_date = end_date - timedelta(days=7)
            elif date_filter == "last_month":
                start_date = end_date - timedelta(days=30)
            else:  # all
                start_date = None

            # Get filtered logs
            logs = self.db.get_attendance_logs(start_date, end_date, student_filter)

            # Clear and populate treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            if logs:
                for log in logs:
                    timestamp = datetime.fromisoformat(log['timestamp'])
                    date_str = timestamp.strftime("%Y-%m-%d")
                    time_str = timestamp.strftime("%H:%M:%S")

                    self.tree.insert("", "end", values=(
                        log['id'],
                        log['name'],
                        log['school_id'],
                        date_str,
                        time_str,
                        "Present"
                    ))

            # Update summary
            self.update_summary(logs)

        except Exception as e:
            self.show_error(f"Error applying filters: {e}")

    def on_record_double_click(self, event):
        """Handle double-click on record"""
        self.view_record_details()

    def view_record_details(self):
        """View detailed information about selected record"""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        values = item['values']

        if not values:
            return

        # Get full record details
        record_id = values[0]
        try:
            record = self.db.get_attendance_record(record_id)
            if record:
                self.show_record_details_dialog(record)
        except Exception as e:
            self.show_error(f"Error loading record details: {e}")

    def show_record_details_dialog(self, record):
        """Show detailed record information in a dialog"""
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Record Details")
        dialog.geometry("400x500")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center the dialog
        dialog.geometry("+%d+%d" % (
            self.winfo_rootx() + 50,
            self.winfo_rooty() + 50
        ))

        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Attendance Record Details",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Profile picture (if available)
        if record.get('profile_picture'):
            try:
                image = Image.open(io.BytesIO(record['profile_picture']))
                image = image.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                profile_label = ttk.Label(main_frame, image=photo)
                profile_label.image = photo  # Keep reference
                profile_label.pack(pady=10)
            except Exception:
                pass

        # Record details
        details = [
            ("Record ID:", record['id']),
            ("Student Name:", record['name']),
            ("School ID:", record['school_id']),
            ("Fingerprint ID:", record['fingerprint_id']),
            ("Date:", datetime.fromisoformat(record['timestamp']).strftime("%Y-%m-%d")),
            ("Time:", datetime.fromisoformat(record['timestamp']).strftime("%H:%M:%S")),
            ("Status:", "Present")
        ]

        for label, value in details:
            detail_frame = ttk.Frame(main_frame)
            detail_frame.pack(fill="x", pady=5)

            ttk.Label(detail_frame, text=label, font=("Arial", 10, "bold")).pack(side="left")
            ttk.Label(detail_frame, text=str(value)).pack(side="left", padx=(10, 0))

        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            command=dialog.destroy
        ).pack(pady=20)

    def delete_record(self):
        """Delete selected record"""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        values = item['values']

        if not values:
            return

        # Confirm deletion
        if messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to delete the record for {values[1]}?\n\n"
                f"This action cannot be undone."
        ):
            try:
                record_id = values[0]
                if self.db.delete_attendance_record(record_id):
                    self.tree.delete(selection[0])
                    messagebox.showinfo("Success", "Record deleted successfully!")
                    self.refresh_logs()
                else:
                    self.show_error("Failed to delete record")
            except Exception as e:
                self.show_error(f"Error deleting record: {e}")

    def export_to_csv(self):
        """Export all records to CSV"""
        try:
            # Get filename from user
            filename = filedialog.asksaveasfilename(
                title="Export Attendance Records",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if not filename:
                return

            # Get all records
            logs = self.db.get_attendance_logs()

            if not logs:
                messagebox.showwarning("No Data", "No records to export!")
                return

            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(['ID', 'Student Name', 'School ID', 'Fingerprint ID',
                                 'Date', 'Time', 'Full Timestamp', 'Status'])

                # Write data
                for log in logs:
                    timestamp = datetime.fromisoformat(log['timestamp'])
                    writer.writerow([
                        log['id'],
                        log['name'],
                        log['school_id'],
                        log['fingerprint_id'],
                        timestamp.strftime("%Y-%m-%d"),
                        timestamp.strftime("%H:%M:%S"),
                        log['timestamp'],
                        'Present'
                    ])

            messagebox.showinfo("Success", f"Records exported to {filename}")

        except Exception as e:
            self.show_error(f"Error exporting records: {e}")

    def export_selected(self):
        """Export only selected records"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select records to export!")
            return

        try:
            # Get filename from user
            filename = filedialog.asksaveasfilename(
                title="Export Selected Records",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if not filename:
                return

            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(['ID', 'Student Name', 'School ID', 'Date', 'Time', 'Status'])

                # Write selected data
                for item_id in selection:
                    item = self.tree.item(item_id)
                    values = item['values']
                    writer.writerow(values)

            messagebox.showinfo("Success", f"Selected records exported to {filename}")

        except Exception as e:
            self.show_error(f"Error exporting selected records: {e}")

    def show_error(self, message: str):
        """Show error message"""
        messagebox.showerror("Error", message)