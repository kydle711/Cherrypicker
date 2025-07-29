import os
import traceback
import logging
import tkinter as tk
import customtkinter as ctk
from datetime import date
from tkinter import filedialog, messagebox
from tkcalendar import Calendar

from utils import update_config_json, load_config_json, initialize_config_json
from main import (daily_download, initialize_storage_folder, request_work_orders,
                  create_work_orders_list, perform_full_download, sync_customer_list)
from method_request import MethodRequest as mr


logger = logging.getLogger()
logging.basicConfig(filename='info.log',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

logger.info("\n=====GUI DOWNLOADER RUNNING=====\n")

# Ensure checklists folder exists for gui file browser
initialize_storage_folder()
initialize_config_json()

# Don't need to update customer list often. This will limit the number of slow startups due to sync
if date.today().day % 10 == 0 or load_config_json(param="customers") is None:
    messagebox.showinfo(title='Syncing',
                        message="Syncing customer data... please wait for window to open")
    sync_customer_list()

def gui_daily_download():
    try:
        daily_download()
    except Exception as e:
        logger.error(f"Daily download failed! {e}\n{traceback.format_exc()}")


def gui_range_download(start_date, end_date):
    try:
        perform_full_download(start=start_date, end=end_date)
    except Exception as e:
        logger.error(f"Download by range failed! {e}\n{traceback.format_exc()}")


def gui_num_download(work_order_num):
    try:
        wo_request = mr.get_request_by_num(work_order_num)
        data = request_work_orders(wo_request)
        wo_list = create_work_orders_list(data)
        for wo in wo_list:
            wo.download_files()
    except Exception as e:
        logger.error(f"Download by number failed: {e} for wo: {work_order_num}\n{traceback.format_exc()}")

def gui_audit_download(customer_name, start, end):
    print(customer_name, start, end)


class DownloaderGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cherrypicker")
        self.geometry("500x350")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        ctk.set_window_scaling(1.2)
        ctk.set_widget_scaling(1.2)

        # --- Main layout container ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Request type ---
        self.request_type = ctk.StringVar(value="Date Range")
        ctk.CTkLabel(self.main_frame, text="Request Type:").pack(anchor="center", pady=(10, 0))
        self.type_menu = ctk.CTkOptionMenu(self.main_frame,
                                           values=["Date Range", "Work Order Number",
                                                   "Daily Scan", "PM Audit"],
                                           variable=self.request_type,
                                           command=self.update_visible_fields)
        self.type_menu.pack()

        # --- Work Order ---
        self.work_order_entry_label = ctk.CTkLabel(self.main_frame, text="Work Order Number:")
        self.work_order_entry = ctk.CTkEntry(self.main_frame, width=200)

        # --- Date Frame ---
        self.date_frame = ctk.CTkFrame(self.main_frame)
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()

        self.start_label = ctk.CTkLabel(self.date_frame, text="Start Date:")
        self.start_btn = ctk.CTkButton(self.date_frame, text="Select",
                                       command=lambda: self.select_date(self.start_date_var))
        self.start_display = ctk.CTkLabel(self.date_frame, textvariable=self.start_date_var, width=100)

        self.end_label = ctk.CTkLabel(self.date_frame, text="End Date:")
        self.end_btn = ctk.CTkButton(self.date_frame, text="Select",
                                     command=lambda: self.select_date(self.end_date_var))
        self.end_display = ctk.CTkLabel(self.date_frame, textvariable=self.end_date_var, width=100)

        self.start_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.start_btn.grid(row=0, column=1, padx=5)
        self.start_display.grid(row=0, column=2, padx=5)

        self.end_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.end_btn.grid(row=1, column=1, padx=5)
        self.end_display.grid(row=1, column=2, padx=5)

        # --- Customer dropdown ---
        self.customer_combobox_label = ctk.CTkLabel(self.main_frame, text='Customer')
        self.customer_combobox = ctk.CTkComboBox(self.main_frame, dropdown_font=('Arial', 12), values=[''], width=300)
        self.customer_combobox.bind("<KeyRelease>", self.update_customer_box)

        self.filter_dropdown_label = ctk.CTkLabel(self.main_frame, text="Filter Type")
        self.filter_dropdown = ctk.CTkOptionMenu(self.main_frame, width=200, values=["PWD:PM", "PWD:Service", "None"])

        # --- Save Location ---
        ctk.CTkLabel(self.main_frame, text="Save Location:").pack(anchor="w", pady=(10, 0))
        save_frame = ctk.CTkFrame(self.main_frame)
        save_frame.pack(fill="x")

        config_save_dir = load_config_json(param="save_dir")
        self.save_path_var = tk.StringVar(value=config_save_dir)
        self.save_entry = ctk.CTkEntry(save_frame, textvariable=self.save_path_var)
        self.save_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        browse_btn = ctk.CTkButton(save_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side="left")

        # --- Submit Button ---
        self.submit_btn = ctk.CTkButton(self, text="Submit", command=self.submit_form)
        self.submit_btn.pack(side="bottom", pady=15)

        # Initialize view
        self.update_visible_fields("Date Range")

    def update_customer_box(self, key_event):
        substring = self.customer_combobox.get().upper()
        print(substring)
        customer_list = load_config_json(param="customers")
        self.customer_combobox.configure(values=[name for name in customer_list.keys() if substring in name])
        self.customer_combobox.event_generate("<Button-1>")

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
        top.geometry("480x450")
        top.configure(background='white')
        top.grab_set()

        # Force light mode
        try:
            import tkinter.ttk as ttk
            style = ttk.Style(top)
            style.theme_use('default')
        except Exception as e:
            logger.error(f"Calendar Theme: Error: {e}\nTraceback:{traceback.format_exc()}")

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
        enter_date = ctk.CTkButton(top, text="OK", command=get_date).pack(pady=5)
        enter_date.pack(paxy=5)

    def update_visible_fields(self, choice):
        self.work_order_entry_label.pack_forget()
        self.work_order_entry.pack_forget()
        self.date_frame.pack_forget()
        self.customer_combobox.pack_forget()
        self.customer_combobox_label.pack_forget()

        if choice == "Date Range":
            self.date_frame.pack(pady=(10, 0))
        elif choice == "Work Order Number":
            self.work_order_entry_label.pack(pady=(10, 0))
            self.work_order_entry.pack()
        elif choice == "PM Audit":
            self.date_frame.pack(pady=(10, 0))
            self.customer_combobox_label.pack(pady=(4, 0))
            self.customer_combobox.pack(pady=(4, 0))
        elif choice == "Daily Scan":
            pass

    def get_date_request(self):
        logger.debug("DATE RANGE DOWNLOAD INITIATED")
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        if not start_date or not end_date:
            logger.debug("MISSING START OR END DATE")
            messagebox.showerror("Missing Date", "Please select both start and end dates.")
            return
        if start_date > end_date:
            logger.debug("INVALID DATE RANGE")
            messagebox.showerror("Invalid Date Range", "Start date cannot be after end date.")
            return
        messagebox.showinfo(message=f"Download Running for range: {start_date} --- {end_date}")
        gui_range_download(start_date, end_date)

    def get_num_request(self):
        work_order = self.work_order_entry.get()
        if not work_order.strip():
            messagebox.showerror("Missing Input", "Please enter a work order number.")
            return
        if not work_order.isdigit():
            messagebox.showerror("Invalid Work Order Number", "Please enter a valid number.")
            return
        messagebox.showinfo(message=f"Download running for work order: {work_order}")
        gui_num_download(int(work_order))

    def get_daily_request(self):
        logger.info("\n=====RUNNING DAILY SCAN THROUGH GUI=====\n")
        messagebox.showinfo(message=f"Daily download running...")
        gui_daily_download()

    def get_pm_audit_request(self):
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        customer_list = load_config_json(param="customers")
        customer = self.customer_combobox.get()
        if not customer in customer_list.keys():
            logger.debug(f"CUSTOMER NOT IN CUSTOMER LIST: {customer}")
            messagebox.showerror("Invalid customer", "Customer not in customer list")
            return
        customer = customer_list[customer]
        logger.debug(f"Full customer name: {customer}")
        logger.info(f"Downloading PM audit for customer {customer}")
        messagebox.showinfo(title="PM Audit", message=f"PM audit for customer {customer}")
        gui_audit_download(customer_name=customer, start=start_date, end=end_date)


    def submit_form(self):
        request_type = self.request_type.get()
        save_path = self.save_path_var.get()

        update_config_json(param="save_dir", new_value=save_path)
        if not os.path.isdir(save_path):
            messagebox.showerror("Invalid Path", "Selected save location is not a valid directory.")
            return

        if request_type == "Date Range":
            self.get_date_request()
        elif request_type == "Work Order Number":
            self.get_num_request()
        elif request_type == "Daily Scan":
            self.get_daily_request()
        elif request_type == "PM Audit":
            self.get_pm_audit_request()
        messagebox.showinfo(message="Download complete!")


if __name__ == '__main__':
    try:
        app = DownloaderGUI()
        app.mainloop()
    except Exception as e:
        logger.error(f"GUI Downloader failed for unknown reason: {traceback.format_exc()}")