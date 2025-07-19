import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkcalendar import Calendar
from datetime import datetime

class APICallerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Method File Downloader")
        self.geometry("500x350")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        ctk.set_window_scaling(1.2)
        ctk.set_widget_scaling(1.2)

        self.default_path = os.path.join(os.path.expanduser("~"), "Documents")

        # --- Main layout container ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Request type ---
        self.request_type = ctk.StringVar(value="Date Range")
        ctk.CTkLabel(self.main_frame, text="Request Type:").pack(anchor="center", pady=(10, 0))
        self.type_menu = ctk.CTkOptionMenu(self.main_frame, values=["Date Range", "Work Order Number", "Daily Scan"],
                                           variable=self.request_type, command=self.update_visible_fields)
        self.type_menu.pack()

        # --- Work Order ---
        self.work_order_entry_label = ctk.CTkLabel(self.main_frame, text="Work Order Number:")
        self.work_order_entry = ctk.CTkEntry(self.main_frame, width=200)

        # --- Date Frame ---
        self.date_frame = ctk.CTkFrame(self.main_frame)
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()

        self.start_label = ctk.CTkLabel(self.date_frame, text="Start Date:")
        self.start_btn = ctk.CTkButton(self.date_frame, text="Select", command=lambda: self.select_date(self.start_date_var))
        self.start_display = ctk.CTkLabel(self.date_frame, textvariable=self.start_date_var, width=100)

        self.end_label = ctk.CTkLabel(self.date_frame, text="End Date:")
        self.end_btn = ctk.CTkButton(self.date_frame, text="Select", command=lambda: self.select_date(self.end_date_var))
        self.end_display = ctk.CTkLabel(self.date_frame, textvariable=self.end_date_var, width=100)

        self.start_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.start_btn.grid(row=0, column=1, padx=5)
        self.start_display.grid(row=0, column=2, padx=5)

        self.end_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.end_btn.grid(row=1, column=1, padx=5)
        self.end_display.grid(row=1, column=2, padx=5)

        # --- Save Location ---
        ctk.CTkLabel(self.main_frame, text="Save Location:").pack(anchor="w", pady=(10, 0))
        save_frame = ctk.CTkFrame(self.main_frame)
        save_frame.pack(fill="x")
        self.save_path_var = tk.StringVar(value=self.default_path)
        self.save_entry = ctk.CTkEntry(save_frame, textvariable=self.save_path_var)
        self.save_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        browse_btn = ctk.CTkButton(save_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side="left")

        # --- Submit Button ---
        self.submit_btn = ctk.CTkButton(self, text="Submit", command=self.submit_form)
        self.submit_btn.pack(side="bottom", pady=15)

        # Initialize view
        self.update_visible_fields("Date Range")

    def browse_folder(self):
        selected = filedialog.askdirectory()
        if selected:
            self.save_path_var.set(selected)

    def select_date(self, target_var):
        def get_date():
            selected = cal.get_date()
            target_var.set(selected)
            top.destroy()

        top = tk.Toplevel(self)
        top.title("Select Date")
        top.geometry("420x320")
        top.configure(background='white')
        top.grab_set()

        try:
            import tkinter.ttk as ttk
            style = ttk.Style(top)
            style.theme_use('default')
        except:
            pass

        cal = Calendar(
            top,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            font=("Segoe UI", 16),
            background="white",
            foreground="black",
            headersbackground="lightgray",
            headersforeground="black",
            selectbackground="#007acc",
            selectforeground="white",
            weekendbackground="white",
            weekendforeground="gray20",
            disabledbackground="gray90",
            othermonthforeground="gray50",
            bordercolor="lightgray"
        )
        cal.pack(padx=10, pady=10)
        ctk.CTkButton(top, text="OK", command=get_date).pack(pady=5)

    def update_visible_fields(self, choice):
        self.work_order_entry_label.pack_forget()
        self.work_order_entry.pack_forget()
        self.date_frame.pack_forget()

        if choice == "Date Range":
            self.date_frame.pack(pady=(10, 0))
        elif choice == "Work Order Number":
            self.work_order_entry_label.pack(pady=(10, 0))
            self.work_order_entry.pack()
        elif choice == "Daily Scan":
            pass

    def submit_form(self):
        request_type = self.request_type.get()
        work_order = self.work_order_entry.get()
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        save_path = self.save_path_var.get()

        if not os.path.isdir(save_path):
            messagebox.showerror("Invalid Path", "Selected save location is not a valid directory.")
            return

        if request_type == "Date Range":
            if not start_date or not end_date:
                messagebox.showerror("Missing Date", "Please select both start and end dates.")
                return
            if start_date > end_date:
                messagebox.showerror("Invalid Date Range", "Start date cannot be after end date.")
                return

        if request_type == "Work Order Number" and not work_order.strip():
            messagebox.showerror("Missing Input", "Please enter a work order number.")
            return

        summary = f"Request Type: {request_type}\n"
        if request_type == "Work Order Number":
            summary += f"Work Order: {work_order}\n"
        elif request_type == "Date Range":
            summary += f"Start Date: {start_date}\nEnd Date: {end_date}\n"
        summary += f"Save Location: {save_path}"

        messagebox.showinfo("Form Submitted", summary)
        print(summary)

if __name__ == "__main__":
    app = APICallerGUI()
    app.mainloop()
