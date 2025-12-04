
import os
import traceback
import logging
import tkinter as tk
import customtkinter as ctk

from datetime import date, timedelta
from tkinter import filedialog, messagebox
from tkcalendar import Calendar

from app_config import LOG_FILE, SYNC_INTERVAL
from src.app_config import CONFIG_FILE
from utils import update_config_json, load_config_json, initialize_config_json
from main import daily_download, initialize_storage_folder, perform_full_download
from logic import request_data, sync_customer_list, create_work_order_list, add_to_signature_list, remove_from_signature_list
from method_request import MethodRequest as mr


logger = logging.getLogger()
logging.basicConfig(filename=LOG_FILE,
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

logger.info("\n=====GUI DOWNLOADER RUNNING=====\n")

# Ensure checklists folder exists for gui file browser
initialize_storage_folder()
initialize_config_json()


def update_customer_list():
    last_sync = load_config_json(param="last_customer_sync")
    today = date.today()
    difference = today - date.fromisoformat(last_sync)
    if difference >= timedelta(SYNC_INTERVAL):
        messagebox.showinfo(title='Syncing',
                            message="Performing customer sync... please wait for window to open\nClick 'OK' to begin sync")
        sync_customer_list()
        update_config_json(param="last_customer_sync", new_value=today.isoformat())

def gui_daily_download():
    try:
        daily_download()
        messagebox.showinfo(message="Download complete!")
    except Exception as e:
        logger.error(f"Daily download failed! {e}\n{traceback.format_exc()}")


def gui_range_download(start_date, end_date, include_signatures, filter_type=None):
    try:
        range_request = mr.get_request_by_range(start_date=start_date, end_date=end_date)
        perform_full_download(request_type=range_request, wo_filter=filter_type, get_sigs=include_signatures)
        messagebox.showinfo(message="Download complete!")
    except Exception as e:
        logger.error(f"Download by range failed! {e}\n{traceback.format_exc()}")


def gui_num_download(work_order_num):
    try:
        wo_request = mr.get_request_by_num(work_order_num)
        data = request_data(wo_request)
        wo_list = create_work_order_list(data)
        for wo in wo_list:
            wo.download_files()
        messagebox.showinfo(message="Download complete!")
    except Exception as e:
        logger.error(f"Download by number failed: {e} for wo: {work_order_num}\n{traceback.format_exc()}")

def gui_audit_download(customer_name, start, end, filter_type, include_signatures):
    try:
        print(customer_name, start, end, filter_type, include_signatures)
        messagebox.showinfo(message="Download complete!")
    except Exception as e:
        logger.error(f"Download by audit failed! {e}\n{traceback.format_exc()}")

class DownloaderGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cherrypicker")
        self.base_geometry = "500x300"
        self.set_geometry(self.base_geometry)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        ctk.set_window_scaling(1.2)
        ctk.set_widget_scaling(1.2)

        # Main layout container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Request type
        self.request_type = ctk.StringVar(value="Date Range")
        ctk.CTkLabel(self.main_frame, text="Request Type:").pack(anchor="center", pady=(10, 0))
        self.type_menu = ctk.CTkOptionMenu(self.main_frame,
                                           values=["Date Range", "Work Order Number", "Daily Scan",
                                                   "PM Audit", "Add Signatures", "Remove Signatures"],
                                           variable=self.request_type,
                                           command=self.update_visible_fields)
        self.type_menu.pack()

        # Work Order Entry
        self.work_order_entry_label = ctk.CTkLabel(self.main_frame, text="Work Order Number:")
        self.work_order_entry = ctk.CTkEntry(self.main_frame, width=200)

        # Date Frame
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

        # Customer Frame
        self.customer_frame = ctk.CTkFrame(self.main_frame)
        self.customer_combobox_label = ctk.CTkLabel(self.customer_frame, text="Company Name:")
        self.customer_combobox = ctk.CTkComboBox(self.customer_frame, dropdown_font=('Arial', 12),
                                                 values=[''], width=300)
        self.customer_combobox.bind("<KeyRelease>", self.update_customer_box)
        self.customer_combobox_label.pack(pady=(4, 0), padx=(20, 5), side='left')
        self.customer_combobox.pack(pady=(4, 0), padx=(5, 20), side='right')

        # Signature Frame
        self.signature_frame = ctk.CTkFrame(self.main_frame)
        self.signature_combobox_label = ctk.CTkLabel(self.signature_frame, text="Signature list:")
        self.signature_combobox = ctk.CTkComboBox(self.signature_frame, dropdown_font=('Arial', 12),
                                                  values=[''], width=300)
        sig_list = load_config_json(param="signature_list", config_file=CONFIG_FILE)
        self.signature_combobox.configure(values=[customer for customer in sig_list])
        self.signature_combobox.bind("<KeyRelease>", self.update_signature_box)
        self.signature_combobox_label.pack(pady=(4, 0), padx=(20, 5), side='left')
        self.signature_combobox.pack(pady=(4, 0), padx=(5, 20))

        # Filter Frame
        self.filter_frame = ctk.CTkFrame(self.main_frame)
        self.filter_dropdown_label = ctk.CTkLabel(self.filter_frame, text="Filter Type:")
        self.filter_dropdown = ctk.CTkOptionMenu(self.filter_frame, width=120, values=["PWD:PM", "PWD:Service", "None"])
        self.filter_dropdown_label.pack(pady=(4, 0), padx=(5, 20), side='left')
        self.filter_dropdown.pack(pady=(4, 0), padx=(5, 20))

        # Signatures checkbox
        self.signatures_box = ctk.CTkCheckBox(self.filter_frame, text='Include Signatures')
        self.signatures_box.pack(pady=(4, 0), padx=(5, 20), side='right')

        # Save Location
        ctk.CTkLabel(self.main_frame, text="Save Location:").pack(anchor="w", pady=(10, 0))
        save_frame = ctk.CTkFrame(self.main_frame)
        save_frame.pack(fill="x")

        config_save_dir = load_config_json(param="save_dir")
        self.save_path_var = tk.StringVar(value=config_save_dir)
        self.save_entry = ctk.CTkEntry(save_frame, textvariable=self.save_path_var)
        self.save_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        browse_btn = ctk.CTkButton(save_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side="left")

        # Submit Button
        self.submit_btn = ctk.CTkButton(self, text="Submit", command=self.submit_form)
        self.submit_btn.pack(side="bottom", pady=15)

        # Initialize view
        self.update_visible_fields("Date Range")

    def set_geometry(self, geo=None):
        if geo is None:
            self.geometry(self.base_geometry)
        else:
            self.geometry(geo)

    # Unused key_event parameter needed to bind box to func
    def update_customer_box(self, key_event=None):
        substring = self.customer_combobox.get().upper()
        customer_list = load_config_json(param="customers")
        self.customer_combobox.configure(values=[name for name in customer_list.keys() if substring in name])
        self.customer_combobox.event_generate("<Button-1>")

    def update_signature_box(self, key_event=None):
        substring = self.signature_combobox.get().upper()
        signature_list = load_config_json(param="signature_list")
        self.signature_combobox.configure(values=[name for name in signature_list if substring in name])
        self.signature_combobox.event_generate("<Button-1>")

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

        # Force light mode - dark mode looks terrible for some reason
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

    def update_visible_fields(self, choice):
        self.work_order_entry_label.pack_forget()
        self.work_order_entry.pack_forget()
        self.date_frame.pack_forget()
        self.customer_frame.pack_forget()
        self.filter_frame.pack_forget()
        self.signature_frame.pack_forget()

        if choice == "Date Range":
            self.set_geometry()
            self.date_frame.pack(pady=(10, 0))
        elif choice == "Work Order Number":
            self.set_geometry()
            self.work_order_entry_label.pack(pady=(10, 0))
            self.work_order_entry.pack()
        elif choice == "PM Audit":
            self.set_geometry("500x440")
            self.date_frame.pack(pady=(10, 0))
            self.customer_frame.pack(pady=(10, 0))
            self.filter_frame.pack(pady=(10, 0))
        elif choice == "Daily Scan":
            self.set_geometry()
            pass
        elif choice == "Add Signatures":
            self.set_geometry()
            self.customer_frame.pack(pady=(10, 0))
        elif choice == "Remove Signatures":
            self.set_geometry()
            self.signature_frame.pack(pady=(10,0))

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

    @staticmethod
    def get_daily_request():
        logger.info("\n=====RUNNING DAILY SCAN THROUGH GUI=====\n")
        messagebox.showinfo(message=f"Daily download running...")
        gui_daily_download()

    def get_pm_audit_request(self):
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        filter_type = self.filter_dropdown.get()
        download_sigs = self.signatures_box.get()
        customer_list = load_config_json(param="customers")
        customer = self.customer_combobox.get()

        if not customer in customer_list.keys():
            logger.debug(f"CUSTOMER NOT IN CUSTOMER LIST: {customer}")
            messagebox.showerror("Invalid customer", "Customer not in customer list")
            return

        if filter_type == "None":
            filter_type = None
        # customer_name param needs the full customer name from config.json lookup table to match in method
        customer_full_name = customer_list[customer]
        logger.debug(f"Full customer name: {customer}")
        logger.info(f"Downloading PM audit for customer {customer}")
        messagebox.showinfo(title="PM Audit", message=f"PM audit for customer {customer}")

        gui_audit_download(customer_name=customer_full_name, start=start_date, end=end_date,
                           include_signatures=download_sigs, filter_type=filter_type)

    def request_add_signature(self):
        customer = self.customer_combobox.get()
        signature_list = list(load_config_json(param="signature_list"))
        if customer not in signature_list:
            signature_list.append(customer)
            update_config_json(param="signature_list", new_value=signature_list)
            self.update_signature_box()
            messagebox.showinfo(title="Update complete!", message=f"Successfully added {customer} to signature list")
        else:
            messagebox.showinfo(title="Already exists!", message=f"Customer: {customer} is already in signature list")

    def request_remove_signature(self):
        customer = self.signature_combobox.get()
        signature_list = list(load_config_json(param="signature_list"))
        if customer in signature_list:
            signature_list.remove(customer)
            update_config_json(param="signature_list", new_value=signature_list)
            self.update_signature_box()
            messagebox.showinfo(title="Update complete!", message=f"Successfully removed {customer} from signature list")
        else:
            messagebox.showinfo(title="Invalid entry", message=f"Customer: {customer} is not valid")
    def submit_form(self):
        request_type = self.request_type.get()
        save_path = self.save_path_var.get()

        if not os.path.isdir(save_path):
            messagebox.showerror("Invalid Path", "Selected save location is not a valid directory.")
            return
        update_config_json(param="save_dir", new_value=save_path)

        if request_type == "Date Range":
            self.get_date_request()
        elif request_type == "Work Order Number":
            self.get_num_request()
        elif request_type == "Daily Scan":
            self.get_daily_request()
        elif request_type == "PM Audit":
            self.get_pm_audit_request()
        elif request_type == "Add Signatures":
            self.request_add_signature()
        elif request_type == "Remove Signatures":
            self.request_remove_signature()


if __name__ == '__main__':
    try:
        update_customer_list()
        app = DownloaderGUI()
        app.mainloop()
    except Exception as e:
        logger.error(f"GUI Downloader failed for unknown reason: {traceback.format_exc()}")