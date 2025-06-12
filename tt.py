import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import calendar
import json
import os
import platform
import shutil
import sys
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class ModernTravelCalendar:
    def __init__(self, root):
        self.root = root
        self.root.title("Travel Tracker")
        self.root.geometry("1000x720")

        # Modern color scheme
        self.colors = {
            'primary': '#2563eb',      # Modern blue
            'primary_light': '#3b82f6',
            'primary_dark': '#1d4ed8',
            'secondary': '#64748b',    # Slate gray
            'accent': '#06b6d4',       # Cyan
            'success': '#10b981',      # Green
            'warning': '#f59e0b',      # Amber
            'danger': '#ef4444',       # Red
            'background': '#f8fafc',   # Light gray
            'surface': '#ffffff',      # White
            'text': '#1e293b',         # Dark gray
            'text_light': '#64748b',   # Light gray
            'border': '#e2e8f0'        # Light border
        }
        
        self.root.configure(bg=self.colors['background'])

        # Data storage - now uses OS-specific paths
        self.data_file = self.get_data_file_path()
        self.config_file = self.get_config_file_path()
        self.travel_records = self.load_data()
        self.selected_start_date = None
        self.selected_end_date = None
        self.selecting_range = False
        
        # Edit mode tracking
        self.edit_mode = False
        self.edit_index = None
        
        # Sorting state
        self.sort_column = None
        self.sort_reverse = False
        
        # Report window tracking
        self.report_window = None
        
        # Current display
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        
        # Validation settings - set defaults first, then load from config
        self.validation_settings = {
            'allow_overlaps': False,
            'warn_future_dates': True,
            'future_warning_days': 730,  # 2 years
            'warn_past_dates': True,
            'past_warning_days': 1095,   # 3 years
            'max_location_length': 100,
            'max_comment_length': 1000
        }
        self.load_config()  # Load saved settings from config file
        
        self.setup_modern_styles()
        self.setup_menu()
        self.setup_ui()
        self.update_calendar_display()
        self.update_location_dropdown()
    
    def get_data_directory(self):
        """Get the appropriate data directory for the current OS"""
        app_name = "TravelTracker"
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Check if we're running in Microsoft Store Python (sandboxed environment)
                if "Packages" in sys.executable and "PythonSoftwareFoundation" in sys.executable:
                    # We're in Microsoft Store Python sandbox, use actual user AppData
                    user_profile = os.environ.get('USERPROFILE')
                    if user_profile:
                        # Use USERPROFILE which should point to C:\Users\username
                        data_dir = Path(user_profile) / 'AppData' / 'Roaming' / app_name
                    else:
                        # Fallback: try to extract username from USERPROFILE or other methods
                        username = os.environ.get('USERNAME', '')
                        if username:
                            data_dir = Path(f"C:/Users/{username}/AppData/Roaming") / app_name
                        else:
                            # Last resort fallback
                            data_dir = Path.home() / 'AppData' / 'Roaming' / app_name
                else:
                    if 'APPDATA' in os.environ:
                        # Regular Python installation
                        data_dir = Path(os.environ['APPDATA']) / app_name
                    else:
                        # Fallback for Windows
                        data_dir = Path.home() / 'AppData' / 'Roaming' / app_name
            
            elif system == "Darwin":  # macOS
                # Use ~/Library/Application Support/TravelTracker
                data_dir = Path.home() / 'Library' / 'Application Support' / app_name
            
            elif system == "Linux":
                # Use XDG_DATA_HOME or ~/.local/share/TravelTracker
                if 'XDG_DATA_HOME' in os.environ:
                    data_dir = Path(os.environ['XDG_DATA_HOME']) / app_name
                else:
                    data_dir = Path.home() / '.local' / 'share' / app_name
            
            else:
                # Unknown OS - use current directory as fallback
                print(f"Unknown operating system: {system}. Using current directory for data storage.")
                return Path.cwd()
            
            # Create directory if it doesn't exist
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir
            
        except Exception as e:
            print(f"Error creating data directory: {e}. Using current directory as fallback.")
            return Path.cwd()
    
    def get_data_file_path(self):
        """Get the full path to the travel_data.json file"""
        data_dir = self.get_data_directory()
        new_data_file = data_dir / "travel_data.json"
        
        # Check for migration from old location
        old_data_file = Path.cwd() / "travel_data.json"
        
        if old_data_file.exists() and not new_data_file.exists():
            # Migrate data from old location to new location
            try:
                shutil.copy2(old_data_file, new_data_file)
                print(f"Migrated travel data from {old_data_file} to {new_data_file}")
                
                # Optionally remove old file after successful migration
                # Commenting out to be safe - user can manually delete if desired
                # old_data_file.unlink()
                
            except Exception as e:
                print(f"Error migrating data file: {e}. Using old location.")
                return str(old_data_file)
        
        return str(new_data_file)
    
    def get_config_file_path(self):
        """Get the full path to the config.json file"""
        data_dir = self.get_data_directory()
        return str(data_dir / "config.json")
    
    def load_config(self):
        """Load configuration settings from config.json file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    # Update validation settings with saved values
                    if 'validation_settings' in config_data:
                        self.validation_settings.update(config_data['validation_settings'])
                        print(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                print(f"Error loading config: {e}. Using default settings.")
    
    def save_config(self):
        """Save configuration settings to config.json file"""
        try:
            config_data = {
                'validation_settings': self.validation_settings
            }
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
            messagebox.showerror("Save Error", f"Could not save configuration: {e}")
    
    # ========== VALIDATION METHODS ==========
    
    def validate_date_format(self, date_string: str) -> Tuple[bool, Optional[datetime], str]:
        """
        Validate date format and return parsed date.
        Returns: (is_valid, parsed_date, error_message)
        """
        if not date_string or not date_string.strip():
            return False, None, "Date cannot be empty"
        
        date_string = date_string.strip()
        
        # Try multiple date formats
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%m-%d-%Y', '%d-%m-%Y']
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_string, fmt)
                # Check for reasonable date range (not too far in past/future)
                min_date = datetime(1900, 1, 1)
                max_date = datetime(2100, 12, 31)
                
                if parsed_date < min_date:
                    return False, None, f"Date cannot be before {min_date.strftime('%Y-%m-%d')}"
                if parsed_date > max_date:
                    return False, None, f"Date cannot be after {max_date.strftime('%Y-%m-%d')}"
                
                return True, parsed_date, ""
            except ValueError:
                continue
        
        return False, None, f"Invalid date format. Please use YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY"
    
    def validate_date_range(self, start_date: datetime, end_date: datetime) -> Tuple[bool, str]:
        """
        Validate date range logic.
        Returns: (is_valid, error_message)
        """
        if end_date < start_date:
            return False, "End date cannot be before start date"
        
        # Check for excessively long trips (more than 2 years)
        if (end_date - start_date).days > 730:
            return False, "Trip duration cannot exceed 2 years. Please split into multiple trips."
        
        return True, ""
    
    def validate_date_warnings(self, start_date: datetime, end_date: datetime) -> List[str]:
        """
        Check for date-related warnings (not blocking errors).
        Returns: list of warning messages
        """
        warnings = []
        current_date = datetime.now()
        
        # Future date warnings
        if self.validation_settings['warn_future_dates']:
            future_limit = current_date + timedelta(days=self.validation_settings['future_warning_days'])
            if start_date > future_limit:
                days = self.validation_settings['future_warning_days']
                if days >= 365:
                    years = days // 365
                    remaining_days = days % 365
                    if remaining_days == 0:
                        time_desc = f"{years} year{'s' if years != 1 else ''}"
                    else:
                        time_desc = f"{years} year{'s' if years != 1 else ''} and {remaining_days} day{'s' if remaining_days != 1 else ''}"
                else:
                    time_desc = f"{days} day{'s' if days != 1 else ''}"
                warnings.append(f"Start date is more than {time_desc} in the future")
        
        # Past date warnings
        if self.validation_settings['warn_past_dates']:
            past_limit = current_date - timedelta(days=self.validation_settings['past_warning_days'])
            if end_date < past_limit:
                days = self.validation_settings['past_warning_days']
                if days >= 365:
                    years = days // 365
                    remaining_days = days % 365
                    if remaining_days == 0:
                        time_desc = f"{years} year{'s' if years != 1 else ''}"
                    else:
                        time_desc = f"{years} year{'s' if years != 1 else ''} and {remaining_days} day{'s' if remaining_days != 1 else ''}"
                else:
                    time_desc = f"{days} day{'s' if days != 1 else ''}"
                warnings.append(f"End date is more than {time_desc} in the past")
        
        return warnings
    
    def check_date_overlap(self, start_date: datetime, end_date: datetime, exclude_index: Optional[int] = None) -> Tuple[bool, List[Dict]]:
        """
        Check if the given date range overlaps with existing travel records.
        Returns: (has_overlap, list_of_conflicting_records)
        """
        if self.validation_settings['allow_overlaps']:
            return False, []
        
        conflicting_records = []
        
        for i, record in enumerate(self.travel_records):
            # Skip the record being edited
            if exclude_index is not None and i == exclude_index:
                continue
            
            try:
                existing_start = datetime.strptime(record['start_date'], '%Y-%m-%d')
                existing_end = datetime.strptime(record['end_date'], '%Y-%m-%d')
                
                # Check for overlap: two ranges overlap if start1 <= end2 and start2 <= end1
                if start_date <= existing_end and existing_start <= end_date:
                    conflicting_records.append({
                        'index': i,
                        'record': record,
                        'start_date': existing_start,
                        'end_date': existing_end
                    })
            except ValueError:
                # Skip records with invalid dates
                continue
        
        return len(conflicting_records) > 0, conflicting_records
    
    def validate_location(self, location: str) -> Tuple[bool, str, List[str]]:
        """
        Validate location input.
        Returns: (is_valid, cleaned_location, warnings)
        """
        if not location or not location.strip():
            return False, "", ["Location cannot be empty"]
        
        cleaned_location = location.strip()
        warnings = []
        
        # Check length
        if len(cleaned_location) > self.validation_settings['max_location_length']:
            return False, cleaned_location, [f"Location name too long (max {self.validation_settings['max_location_length']} characters)"]
        
        # Check for suspicious characters
        suspicious_chars = ['<', '>', '"', "'", '\\', '/', '|']
        if any(char in cleaned_location for char in suspicious_chars):
            warnings.append("Location contains special characters that might cause issues")
        
        # Check for all caps (suggest proper case)
        if cleaned_location.isupper() and len(cleaned_location) > 3:
            warnings.append("Consider using proper case instead of ALL CAPS")
        
        return True, cleaned_location, warnings
    
    def validate_comment(self, comment: str) -> Tuple[bool, str, List[str]]:
        """
        Validate comment/notes input.
        Returns: (is_valid, cleaned_comment, warnings)
        """
        cleaned_comment = comment.strip() if comment else ""
        warnings = []
        
        # Check length
        if len(cleaned_comment) > self.validation_settings['max_comment_length']:
            return False, cleaned_comment, [f"Notes too long (max {self.validation_settings['max_comment_length']} characters)"]
        
        return True, cleaned_comment, warnings
    
    def show_overlap_dialog(self, conflicting_records: List[Dict]) -> str:
        """
        Show dialog for handling overlapping dates.
        Returns: 'cancel', 'ignore', or 'adjust'
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("⚠️ Overlapping Travel Dates")
        dialog.geometry("600x400")
        dialog.configure(bg=self.colors['background'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        result = {'action': 'cancel'}
        
        # Main frame
        main_frame = tk.Frame(dialog, bg=self.colors['background'], padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning icon and message
        header_frame = tk.Frame(main_frame, bg=self.colors['background'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header_frame, text="⚠️", 
                font=('Segoe UI', 32), 
                fg=self.colors['warning'],
                bg=self.colors['background']).pack(side=tk.LEFT, padx=(0, 15))
        
        message_frame = tk.Frame(header_frame, bg=self.colors['background'])
        message_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(message_frame, text="Overlapping Travel Dates Detected", 
                font=('Segoe UI', 16, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['background']).pack(anchor=tk.W)
        
        tk.Label(message_frame, text="The dates you entered overlap with existing travel records:", 
                font=('Segoe UI', 11),
                fg=self.colors['text_light'],
                bg=self.colors['background']).pack(anchor=tk.W, pady=(5, 0))
        
        # Conflicts list
        conflicts_frame = ttk.LabelFrame(main_frame, text="Conflicting Records", style='Card.TLabelframe')
        conflicts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        conflicts_text = tk.Text(conflicts_frame, height=8, wrap=tk.WORD,
                               font=('Segoe UI', 10),
                               bg=self.colors['surface'],
                               fg=self.colors['text'],
                               relief='flat', padx=15, pady=15)
        conflicts_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for i, conflict in enumerate(conflicting_records, 1):
            record = conflict['record']
            start_str = conflict['start_date'].strftime('%Y-%m-%d')
            end_str = conflict['end_date'].strftime('%Y-%m-%d')
            location = record['location']
            
            conflict_text = f"{i}. {start_str} to {end_str} - {location}\n"
            if record.get('comment'):
                conflict_text += f"   Notes: {record['comment'][:100]}{'...' if len(record['comment']) > 100 else ''}\n"
            conflict_text += "\n"
            
            conflicts_text.insert(tk.END, conflict_text)
        
        conflicts_text.config(state=tk.DISABLED)
        
        # Buttons
        buttons_frame = tk.Frame(main_frame, bg=self.colors['background'])
        buttons_frame.pack(fill=tk.X)
        
        def on_cancel():
            result['action'] = 'cancel'
            dialog.destroy()
        
        def on_ignore():
            result['action'] = 'ignore'
            dialog.destroy()
        
        def on_adjust():
            result['action'] = 'adjust'
            dialog.destroy()
        
        tk.Button(buttons_frame, text="❌ Cancel",
                 bg=self.colors['secondary'], fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat', bd=0, padx=20, pady=10,
                 command=on_cancel).pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(buttons_frame, text="⚠️ Save Anyway",
                 bg=self.colors['warning'], fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat', bd=0, padx=20, pady=10,
                 command=on_ignore).pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(buttons_frame, text="✏️ Adjust Dates",
                 bg=self.colors['primary'], fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat', bd=0, padx=20, pady=10,
                 command=on_adjust).pack(side=tk.RIGHT)
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        return result['action']
    
    def show_validation_errors_dialog(self, errors: List[str]) -> None:
        """
        Show styled dialog for validation errors.
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("❌ Validation Errors")
        dialog.geometry("550x400")
        dialog.configure(bg=self.colors['background'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Main frame
        main_frame = tk.Frame(dialog, bg=self.colors['background'], padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Error icon and message
        header_frame = tk.Frame(main_frame, bg=self.colors['background'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header_frame, text="❌", 
                font=('Segoe UI', 32), 
                fg=self.colors['danger'],
                bg=self.colors['background']).pack(side=tk.LEFT, padx=(0, 15))
        
        message_frame = tk.Frame(header_frame, bg=self.colors['background'])
        message_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(message_frame, text="Validation Errors", 
                font=('Segoe UI', 16, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['background']).pack(anchor=tk.W)
        
        tk.Label(message_frame, text="Please fix the following issues before saving:", 
                font=('Segoe UI', 11),
                fg=self.colors['text_light'],
                bg=self.colors['background']).pack(anchor=tk.W, pady=(5, 0))
        
        # Errors list
        errors_frame = ttk.LabelFrame(main_frame, text="Issues Found", style='Card.TLabelframe')
        errors_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        errors_text = tk.Text(errors_frame, height=10, wrap=tk.WORD,
                             font=('Segoe UI', 11),
                             bg=self.colors['surface'],
                             fg=self.colors['text'],
                             relief='flat', padx=20, pady=15)
        errors_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for i, error in enumerate(errors, 1):
            error_text = f"• {error}\n\n"
            errors_text.insert(tk.END, error_text)
        
        errors_text.config(state=tk.DISABLED)
        
        # OK button
        buttons_frame = tk.Frame(main_frame, bg=self.colors['background'])
        buttons_frame.pack(fill=tk.X)
        
        def on_ok():
            dialog.destroy()
        
        tk.Button(buttons_frame, text="✅ OK",
                 bg=self.colors['primary'], fg='white',
                 font=('Segoe UI', 12, 'bold'),
                 relief='flat', bd=0, padx=30, pady=12,
                 command=on_ok).pack()
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
    
    def show_warnings_dialog(self, warnings: List[str]) -> bool:
        """
        Show styled dialog for validation warnings.
        Returns: True to continue, False to cancel
        """
        if not warnings:
            return True
        
        dialog = tk.Toplevel(self.root)
        dialog.title("⚠️ Validation Warnings")
        dialog.geometry("550x400")
        dialog.configure(bg=self.colors['background'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        result = {'continue': False}
        
        # Main frame
        main_frame = tk.Frame(dialog, bg=self.colors['background'], padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning icon and message
        header_frame = tk.Frame(main_frame, bg=self.colors['background'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header_frame, text="⚠️", 
                font=('Segoe UI', 32), 
                fg=self.colors['warning'],
                bg=self.colors['background']).pack(side=tk.LEFT, padx=(0, 15))
        
        message_frame = tk.Frame(header_frame, bg=self.colors['background'])
        message_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(message_frame, text="Validation Warnings", 
                font=('Segoe UI', 16, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['background']).pack(anchor=tk.W)
        
        tk.Label(message_frame, text="The following issues were detected:", 
                font=('Segoe UI', 11),
                fg=self.colors['text_light'],
                bg=self.colors['background']).pack(anchor=tk.W, pady=(5, 0))
        
        # Warnings list
        warnings_frame = ttk.LabelFrame(main_frame, text="Warnings", style='Card.TLabelframe')
        warnings_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        warnings_text = tk.Text(warnings_frame, height=8, wrap=tk.WORD,
                               font=('Segoe UI', 11),
                               bg=self.colors['surface'],
                               fg=self.colors['text'],
                               relief='flat', padx=20, pady=15)
        warnings_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for i, warning in enumerate(warnings, 1):
            warning_text = f"• {warning}\n\n"
            warnings_text.insert(tk.END, warning_text)
        
        warnings_text.config(state=tk.DISABLED)
        
        # Buttons
        buttons_frame = tk.Frame(main_frame, bg=self.colors['background'])
        buttons_frame.pack(fill=tk.X)
        
        def on_cancel():
            result['continue'] = False
            dialog.destroy()
        
        def on_continue():
            result['continue'] = True
            dialog.destroy()
        
        tk.Button(buttons_frame, text="❌ Cancel",
                 bg=self.colors['secondary'], fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat', bd=0, padx=20, pady=10,
                 command=on_cancel).pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(buttons_frame, text="⚠️ Continue Anyway",
                 bg=self.colors['warning'], fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat', bd=0, padx=20, pady=10,
                 command=on_continue).pack(side=tk.RIGHT)
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        return result['continue']
    
    # ========== END VALIDATION METHODS ==========
    
    def setup_modern_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        
        # Configure modern button styles
        style.configure('Modern.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(12, 8),
                       font=('Segoe UI', 10, 'bold'))
        style.map('Modern.TButton',
                 background=[('active', self.colors['primary_light']),
                           ('pressed', self.colors['primary_dark'])],
                 foreground=[('active', 'white'), ('pressed', 'white')])
        
        style.configure('Secondary.TButton',
                       background=self.colors['secondary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(12, 8),
                       font=('Segoe UI', 10, 'bold'))
        style.map('Secondary.TButton',
                 background=[('active', '#475569'),
                           ('pressed', '#334155')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(12, 8),
                       font=('Segoe UI', 10, 'bold'))
        style.map('Success.TButton',
                 background=[('active', '#059669'),
                           ('pressed', '#047857')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
        
        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(12, 8),
                       font=('Segoe UI', 10, 'bold'))
        style.map('Danger.TButton',
                 background=[('active', '#dc2626'),
                           ('pressed', '#b91c1c')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
        
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(12, 8),
                       font=('Segoe UI', 10, 'bold'))
        style.map('Warning.TButton',
                 background=[('active', '#d97706'),
                           ('pressed', '#b45309')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
        
        # Calendar button styles
        style.configure('Calendar.TButton',
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       borderwidth=1,
                       relief='solid',
                       padding=(8, 8),
                       font=('Segoe UI', 10))
        style.map('Calendar.TButton',
                 background=[('active', self.colors['primary_light']),
                           ('pressed', self.colors['primary'])])
        
        style.configure('CalendarTravel.TButton',
                       background=self.colors['accent'],
                       foreground=self.colors['text'],  # Changed from 'white' to dark text
                       borderwidth=1,
                       relief='solid',
                       padding=(8, 8),
                       font=('Segoe UI', 10, 'bold'))
        style.map('CalendarTravel.TButton',
                 background=[('active', '#0891b2'),
                           ('pressed', '#0e7490')],
                 foreground=[('active', self.colors['text']),
                           ('pressed', self.colors['text'])])
        
        style.configure('CalendarSelected.TButton',
                       background=self.colors['warning'],
                       foreground=self.colors['text'],  # Changed from 'white' to dark text
                       borderwidth=1,
                       relief='solid',
                       padding=(8, 8),
                       font=('Segoe UI', 10, 'bold'))
        style.map('CalendarSelected.TButton',
                 background=[('active', '#d97706'),
                           ('pressed', '#b45309')],
                 foreground=[('active', self.colors['text']),
                           ('pressed', self.colors['text'])])
        
        # Current date button style
        style.configure('CalendarCurrent.TButton',
                       background=self.colors['danger'],
                       foreground=self.colors['text'],
                       borderwidth=1,
                       relief='solid',
                       padding=(8, 8),
                       font=('Segoe UI', 10, 'bold'))
        style.map('CalendarCurrent.TButton',
                 background=[('active', '#dc2626'),
                           ('pressed', '#b91c1c')],
                 foreground=[('active', self.colors['text']),
                           ('pressed', self.colors['text'])])
        
        # Navigation button styles
        style.configure('Nav.TButton',
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       borderwidth=1,
                       relief='solid',
                       padding=(16, 8),
                       font=('Segoe UI', 12, 'bold'))
        style.map('Nav.TButton',
                 background=[('active', self.colors['border']),
                           ('pressed', self.colors['secondary'])])
        
        # Frame styles
        style.configure('Card.TLabelframe',
                       background=self.colors['surface'],
                       borderwidth=2,
                       relief='solid',
                       padding=20)
        style.configure('Card.TLabelframe.Label',
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 12, 'bold'))
        
        # Entry styles
        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['surface'],
                       borderwidth=2,
                       relief='solid',
                       insertcolor=self.colors['primary'],
                       padding=(12, 8))
        
        # Combobox styles
        style.configure('Modern.TCombobox',
                       fieldbackground=self.colors['surface'],
                       borderwidth=2,
                       relief='solid',
                       padding=(12, 8))
    
    def setup_menu(self):
        """Setup the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.exit_application, accelerator="(Ctrl+Q)")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Travel Report", command=self.show_report, accelerator="(Ctrl+R)")
        view_menu.add_separator()
        view_menu.add_command(label="Settings", command=self.show_validation_settings, accelerator="(Ctrl+S)")
        view_menu.add_command(label="Data Directory", command=self.open_data_location, accelerator="(Ctrl+D)")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.open_documentation)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-q>', lambda e: self.exit_application())
        self.root.bind('<Control-r>', lambda e: self.show_report())
        self.root.bind('<Control-s>', lambda e: self.show_validation_settings())
        self.root.bind('<Control-d>', lambda e: self.open_data_location())
    
    def show_validation_settings(self):
        """Show dialog for configuring validation settings"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚙️ Settings")
        dialog.geometry("500x690")
        dialog.configure(bg=self.colors['background'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 50))
        
        # Main frame
        main_frame = tk.Frame(dialog, bg=self.colors['background'], padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Settings variables
        settings_vars = {}
        
        # Date Validation Settings Frame
        date_frame = ttk.LabelFrame(main_frame, text="📅 Date Validation", style='Card.TLabelframe')
        date_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        date_inner = tk.Frame(date_frame, bg=self.colors['surface'])
        date_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Allow overlaps setting
        settings_vars['allow_overlaps'] = tk.BooleanVar(value=self.validation_settings['allow_overlaps'])
        tk.Checkbutton(date_inner, text="Allow overlapping travel dates",
                      variable=settings_vars['allow_overlaps'],
                      bg=self.colors['surface'],
                      font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 15))
        
        # Future date warnings
        settings_vars['warn_future_dates'] = tk.BooleanVar(value=self.validation_settings['warn_future_dates'])
        
        def toggle_future_entry():
            """Enable/disable future days entry based on checkbox state"""
            if settings_vars['warn_future_dates'].get():
                future_entry.config(state='normal')
            else:
                future_entry.config(state='disabled')
        
        tk.Checkbutton(date_inner, text="Warn about far future dates",
                      variable=settings_vars['warn_future_dates'],
                      bg=self.colors['surface'],
                      font=('Segoe UI', 11),
                      command=toggle_future_entry).pack(anchor=tk.W, pady=(0, 5))
        
        # Future days setting - horizontal layout
        future_days_frame = tk.Frame(date_inner, bg=self.colors['surface'])
        future_days_frame.pack(fill=tk.X, padx=(20, 0), pady=(0, 15))
        
        tk.Label(future_days_frame, text="Days in future to warn:",
                font=('Segoe UI', 10),
                fg=self.colors['text_light'],
                bg=self.colors['surface']).pack(side=tk.LEFT)
        
        settings_vars['future_warning_days'] = tk.StringVar(value=str(self.validation_settings['future_warning_days']))
        future_entry = tk.Entry(future_days_frame, textvariable=settings_vars['future_warning_days'],
                               width=10, font=('Segoe UI', 10))
        future_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Set initial state of future entry
        if not settings_vars['warn_future_dates'].get():
            future_entry.config(state='disabled')
        
        # Past date warnings
        settings_vars['warn_past_dates'] = tk.BooleanVar(value=self.validation_settings['warn_past_dates'])
        
        def toggle_past_entry():
            """Enable/disable past days entry based on checkbox state"""
            if settings_vars['warn_past_dates'].get():
                past_entry.config(state='normal')
            else:
                past_entry.config(state='disabled')
        
        tk.Checkbutton(date_inner, text="Warn about old past dates",
                      variable=settings_vars['warn_past_dates'],
                      bg=self.colors['surface'],
                      font=('Segoe UI', 11),
                      command=toggle_past_entry).pack(anchor=tk.W, pady=(0, 5))
        
        # Past days setting - horizontal layout
        past_days_frame = tk.Frame(date_inner, bg=self.colors['surface'])
        past_days_frame.pack(fill=tk.X, padx=(20, 0))
        
        tk.Label(past_days_frame, text="Days in past to warn:",
                font=('Segoe UI', 10),
                fg=self.colors['text_light'],
                bg=self.colors['surface']).pack(side=tk.LEFT)
        
        settings_vars['past_warning_days'] = tk.StringVar(value=str(self.validation_settings['past_warning_days']))
        past_entry = tk.Entry(past_days_frame, textvariable=settings_vars['past_warning_days'],
                             width=10, font=('Segoe UI', 10))
        past_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Set initial state of past entry
        if not settings_vars['warn_past_dates'].get():
            past_entry.config(state='disabled')
        
        # Text Length Limits Frame
        length_frame = ttk.LabelFrame(main_frame, text="📝 Text Length Limits", style='Card.TLabelframe')
        length_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        length_inner = tk.Frame(length_frame, bg=self.colors['surface'])
        length_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Location length - horizontal layout
        location_frame = tk.Frame(length_inner, bg=self.colors['surface'])
        location_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(location_frame, text="Maximum location length:",
                font=('Segoe UI', 11),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(side=tk.LEFT)
        
        settings_vars['max_location_length'] = tk.StringVar(value=str(self.validation_settings['max_location_length']))
        loc_entry = tk.Entry(location_frame, textvariable=settings_vars['max_location_length'],
                            width=10, font=('Segoe UI', 10))
        loc_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Comment length - horizontal layout
        comment_frame = tk.Frame(length_inner, bg=self.colors['surface'])
        comment_frame.pack(fill=tk.X)
        
        tk.Label(comment_frame, text="Maximum comment length:",
                font=('Segoe UI', 11),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(side=tk.LEFT)
        
        settings_vars['max_comment_length'] = tk.StringVar(value=str(self.validation_settings['max_comment_length']))
        comment_entry = tk.Entry(comment_frame, textvariable=settings_vars['max_comment_length'],
                                width=10, font=('Segoe UI', 10))
        comment_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Buttons
        buttons_frame = tk.Frame(main_frame, bg=self.colors['background'])
        buttons_frame.grid(row=4, column=0, pady=(20, 0))
        
        def save_settings():
            try:
                # Update settings
                self.validation_settings['allow_overlaps'] = settings_vars['allow_overlaps'].get()
                self.validation_settings['warn_future_dates'] = settings_vars['warn_future_dates'].get()
                self.validation_settings['warn_past_dates'] = settings_vars['warn_past_dates'].get()
                self.validation_settings['future_warning_days'] = int(settings_vars['future_warning_days'].get())
                self.validation_settings['past_warning_days'] = int(settings_vars['past_warning_days'].get())
                self.validation_settings['max_location_length'] = int(settings_vars['max_location_length'].get())
                self.validation_settings['max_comment_length'] = int(settings_vars['max_comment_length'].get())
                
                # Save settings to config file
                self.save_config()
                
                dialog.destroy()
                messagebox.showinfo("Settings Saved", "✅ Validation settings have been updated and saved.")
            except ValueError as e:
                messagebox.showerror("Invalid Input", f"Please enter valid numbers for all numeric fields.")
        
        tk.Button(buttons_frame, text="💾 Save Settings",
                 bg=self.colors['success'], fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat', bd=0, padx=20, pady=10,
                 command=save_settings).pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(buttons_frame, text="❌ Cancel",
                 bg=self.colors['secondary'], fg='white',
                 font=('Segoe UI', 11, 'bold'),
                 relief='flat', bd=0, padx=20, pady=10,
                 command=dialog.destroy).pack(side=tk.RIGHT)
    
    def open_data_location(self):
        """Open the directory containing the travel data file"""
        data_dir = Path(self.data_file).parent
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows - use os.startfile to open directory
                os.startfile(str(data_dir))
            elif system == "Darwin":  # macOS
                # macOS - use 'open' command
                subprocess.run(['open', str(data_dir)], check=True)
            elif system == "Linux":
                # Linux - use 'xdg-open' command
                subprocess.run(['xdg-open', str(data_dir)], check=True)
            else:
                # Unknown OS - fallback to showing the path
                messagebox.showinfo("Data Location", 
                                   f"Travel data directory:\n{data_dir}\n\n"
                                   f"Cannot automatically open directory on {system}")
                
        except Exception as e:
            # If opening fails, show the path in a message box as fallback
            messagebox.showerror("Error", 
                               f"Could not open data directory:\n{data_dir}\n\n"
                               f"Error: {e}")
    
    def open_documentation(self):
        """Open the documentation URL in the default web browser"""
        documentation_url = "https://github.com/jackworthen/travel-tracker"
        
        try:
            webbrowser.open(documentation_url)
        except Exception as e:
            # If opening fails, show the URL in a message box as fallback
            messagebox.showinfo("Documentation", 
                               f"Could not open web browser automatically.\n\n"
                               f"Please visit the documentation at:\n{documentation_url}")
    
    def exit_application(self):
        """Exit the application"""
        self.root.quit()
        self.root.destroy()
    
    def setup_ui(self):
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.colors['background'], padx=30, pady=30)
        main_container.pack(fill=tk.BOTH, expand=True)
                     
        # Main content area
        content_frame = tk.Frame(main_container, bg=self.colors['background'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=1, minsize=400)
        content_frame.columnconfigure(1, weight=1, minsize=500)
        content_frame.rowconfigure(0, weight=1)
        
        # Left panel - Travel Entry
        self.setup_travel_entry_panel(content_frame)
        
        # Right panel - Calendar
        self.setup_calendar_panel(content_frame)
    
    def setup_travel_entry_panel(self, parent):
        entry_frame = ttk.LabelFrame(parent, text="✈️ New Travel Entry", style='Card.TLabelframe')
        entry_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        entry_frame.columnconfigure(0, weight=1)
        
        # Date section
        date_section = tk.Frame(entry_frame, bg=self.colors['surface'])
        date_section.pack(fill=tk.X, pady=(0, 20))
        date_section.columnconfigure(0, weight=1)
        
        # Start date
        tk.Label(date_section, text="Departure Date", 
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.start_date_entry = ttk.Entry(date_section, style='Modern.TEntry', font=('Segoe UI', 11))
        self.start_date_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # End date
        tk.Label(date_section, text="Return Date", 
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.end_date_entry = ttk.Entry(date_section, style='Modern.TEntry', font=('Segoe UI', 11))
        self.end_date_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Clear dates button
        clear_btn = tk.Button(date_section, text="Clear Dates",
                             bg=self.colors['warning'], fg='white',
                             font=('Segoe UI', 10, 'bold'),
                             relief='flat', bd=0, padx=12, pady=8,
                             activebackground='#d97706', activeforeground='white',
                             command=self.clear_dates)
        clear_btn.grid(row=4, column=0, pady=(0, 20))
        
        # Location section
        tk.Label(entry_frame, text="Location", 
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(anchor=tk.W, pady=(0, 5))
        
        self.location_entry = ttk.Combobox(entry_frame, style='Modern.TCombobox', font=('Segoe UI', 11))
        self.location_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Comment section
        tk.Label(entry_frame, text="Notes", 
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(anchor=tk.W, pady=(0, 5))
        
        # Comment text with modern styling
        comment_frame = tk.Frame(entry_frame, bg=self.colors['surface'], relief='solid', bd=2)
        comment_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.comment_text = tk.Text(comment_frame, height=4, 
                                   font=('Segoe UI', 10),
                                   bg=self.colors['surface'],
                                   fg=self.colors['text'],
                                   relief='flat',
                                   padx=12, pady=8,
                                   wrap=tk.WORD)
        self.comment_text.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        button_frame = tk.Frame(entry_frame, bg=self.colors['surface'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        save_btn = tk.Button(button_frame, text="💾 Save Travel",
                            bg=self.colors['success'], fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            relief='flat', bd=0, padx=12, pady=8,
                            activebackground='#059669', activeforeground='white',
                            command=self.add_travel)
        save_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        clear_btn = tk.Button(button_frame, text="🧹 Clear Form",
                             bg=self.colors['secondary'], fg='white',
                             font=('Segoe UI', 10, 'bold'),
                             relief='flat', bd=0, padx=12, pady=8,
                             activebackground='#475569', activeforeground='white',
                             command=self.clear_form)
        clear_btn.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        report_btn = tk.Button(button_frame, text="📊 View Travel Report",
                              bg=self.colors['primary'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', bd=0, padx=12, pady=8,
                              activebackground=self.colors['primary_light'], activeforeground='white',
                              command=self.show_report)
        report_btn.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def setup_calendar_panel(self, parent):
        calendar_frame = ttk.LabelFrame(parent, text="📅 Calendar View", style='Card.TLabelframe')
        calendar_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        calendar_frame.columnconfigure(0, weight=1)
        calendar_frame.rowconfigure(1, weight=1)
        
        # Navigation
        nav_frame = tk.Frame(calendar_frame, bg=self.colors['surface'])
        nav_frame.pack(fill=tk.X, pady=(0, 20))
        nav_frame.columnconfigure(1, weight=1)
        
        ttk.Button(nav_frame, text="◀", style='Nav.TButton',
                  command=self.prev_month).grid(row=0, column=0, padx=(0, 10))
        
        self.month_label = tk.Label(nav_frame,
                                   font=('Segoe UI', 16, 'bold'),
                                   fg=self.colors['primary'],  # Changed to blue
                                   bg=self.colors['surface'])
        self.month_label.grid(row=0, column=1)
        
        ttk.Button(nav_frame, text="▶", style='Nav.TButton',
                  command=self.next_month).grid(row=0, column=2, padx=(10, 0))
        
        # Calendar grid container
        calendar_container = tk.Frame(calendar_frame, bg=self.colors['surface'])
        calendar_container.pack(fill=tk.BOTH, expand=True)
        
        self.calendar_frame_inner = tk.Frame(calendar_container, bg=self.colors['surface'])
        self.calendar_frame_inner.pack(expand=True)
        
        # Legend
        legend_frame = tk.Frame(calendar_frame, bg=self.colors['surface'])
        legend_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(legend_frame, text="Legend:", 
                font=('Segoe UI', 10, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(side=tk.LEFT)
        
        legend_items = [
            ("🏠 No Travel", self.colors['surface']),
            ("📅 Today", self.colors['danger']),
            ("✈️ Travel Days", self.colors['accent']),
            ("📍 Selected", self.colors['warning'])
        ]
        
        for text, color in legend_items:
            legend_item = tk.Label(legend_frame, text=text,
                                  font=('Segoe UI', 9),
                                  bg=color,
                                  fg='white' if color != self.colors['surface'] else self.colors['text'],
                                  padx=8, pady=4,
                                  relief='solid', bd=1)
            legend_item.pack(side=tk.LEFT, padx=(10, 0))
    
    def load_data(self) -> List[Dict]:
        """Load travel data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
                return []
        return []
    
    def save_data(self):
        """Save travel data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.travel_records, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
            messagebox.showerror("Save Error", f"Could not save data: {e}")
    
    def get_available_years(self) -> List[int]:
        """Get list of years from travel records"""
        years = set()
        for record in self.travel_records:
            try:
                start_year = datetime.strptime(record['start_date'], '%Y-%m-%d').year
                end_year = datetime.strptime(record['end_date'], '%Y-%m-%d').year
                years.add(start_year)
                years.add(end_year)
            except:
                continue
        return sorted(list(years), reverse=True)  # Most recent years first
    
    def update_location_dropdown(self):
        """Update the location combobox with unique locations from travel records"""
        locations = set()
        for record in self.travel_records:
            if record['location'].strip():
                locations.add(record['location'])
        
        sorted_locations = sorted(list(locations))
        self.location_entry['values'] = sorted_locations
    
    def update_calendar_display(self):
        """Update the calendar display for current month/year"""
        # Clear existing calendar
        for widget in self.calendar_frame_inner.winfo_children():
            widget.destroy()
        
        # Update month label
        month_name = calendar.month_name[self.current_month]
        self.month_label.config(text=f"{month_name} {self.current_year}")
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            label = tk.Label(self.calendar_frame_inner, text=day, 
                           font=('Segoe UI', 10, 'bold'),
                           fg=self.colors['text_light'],
                           bg=self.colors['surface'],
                           width=8, height=2)
            label.grid(row=0, column=i, padx=2, pady=2)
        
        # Get calendar data
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # Create date buttons
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell for days not in current month
                    label = tk.Label(self.calendar_frame_inner, text="",
                                   bg=self.colors['surface'], width=8, height=2)
                    label.grid(row=week_num + 1, column=day_num, padx=2, pady=2)
                else:
                    date_obj = datetime(self.current_year, self.current_month, day)
                    
                    # Check status
                    has_travel = self.date_has_travel(date_obj)
                    is_selected = self.date_is_selected(date_obj)
                    is_current = self.date_is_current(date_obj)
                    
                    # Determine style (priority: selected > current > travel > normal)
                    if is_selected:
                        style = 'CalendarSelected.TButton'
                    elif is_current:
                        style = 'CalendarCurrent.TButton'
                    elif has_travel:
                        style = 'CalendarTravel.TButton'
                    else:
                        style = 'Calendar.TButton'
                    
                    btn = ttk.Button(self.calendar_frame_inner, text=str(day), 
                                   style=style,
                                   command=lambda d=day: self.date_clicked(d))
                    btn.grid(row=week_num + 1, column=day_num, padx=2, pady=2, sticky='nsew')
        
        # Configure grid weights for responsive layout
        for i in range(7):
            self.calendar_frame_inner.columnconfigure(i, weight=1)
        for i in range(len(cal) + 1):
            self.calendar_frame_inner.rowconfigure(i, weight=1)
    
    def date_has_travel(self, date_obj: datetime) -> bool:
        """Check if a date has travel records"""
        for record in self.travel_records:
            start_date = datetime.strptime(record['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(record['end_date'], '%Y-%m-%d')
            if start_date <= date_obj <= end_date:
                return True
        return False
    
    def date_is_selected(self, date_obj: datetime) -> bool:
        """Check if a date is in the selected range"""
        if not self.selected_start_date:
            return False
        
        if self.selected_end_date:
            return self.selected_start_date <= date_obj <= self.selected_end_date
        else:
            return date_obj == self.selected_start_date
    
    def date_is_current(self, date_obj: datetime) -> bool:
        """Check if a date is the current date (today)"""
        current_date = datetime.now().date()
        return date_obj.date() == current_date
    
    def date_clicked(self, day: int):
        """Handle date button clicks"""
        clicked_date = datetime(self.current_year, self.current_month, day)
        
        if not self.selected_start_date:
            # First click - set start date
            self.selected_start_date = clicked_date
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, clicked_date.strftime('%Y-%m-%d'))
            self.selecting_range = True
        elif self.selecting_range:
            # Second click - set end date
            if clicked_date >= self.selected_start_date:
                self.selected_end_date = clicked_date
                self.end_date_entry.delete(0, tk.END)
                self.end_date_entry.insert(0, clicked_date.strftime('%Y-%m-%d'))
            else:
                # If clicked date is before start date, swap them
                self.selected_end_date = self.selected_start_date
                self.selected_start_date = clicked_date
                self.start_date_entry.delete(0, tk.END)
                self.start_date_entry.insert(0, clicked_date.strftime('%Y-%m-%d'))
                self.end_date_entry.delete(0, tk.END)
                self.end_date_entry.insert(0, self.selected_end_date.strftime('%Y-%m-%d'))
            self.selecting_range = False
        else:
            # Start new selection
            self.selected_start_date = clicked_date
            self.selected_end_date = None
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, clicked_date.strftime('%Y-%m-%d'))
            self.end_date_entry.delete(0, tk.END)
            self.selecting_range = True
        
        self.update_calendar_display()
    
    def clear_dates(self):
        """Clear date selection and entry fields"""
        self.selected_start_date = None
        self.selected_end_date = None
        self.selecting_range = False
        self.start_date_entry.delete(0, tk.END)
        self.end_date_entry.delete(0, tk.END)
        self.update_calendar_display()
    
    def prev_month(self):
        """Navigate to previous month"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_calendar_display()
    
    def next_month(self):
        """Navigate to next month"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_calendar_display()
    
    def add_travel(self):
        """Add a new travel record or update existing one if in edit mode - with enhanced validation"""
        # Collect all validation errors and warnings
        all_errors = []
        all_warnings = []
        
        # === DATE VALIDATION ===
        
        # Try to get dates from entry fields first
        start_date_str = self.start_date_entry.get().strip()
        end_date_str = self.end_date_entry.get().strip()
        
        start_date = None
        end_date = None
        
        # Validate start date
        if start_date_str:
            is_valid, parsed_date, error_msg = self.validate_date_format(start_date_str)
            if is_valid:
                start_date = parsed_date
            else:
                all_errors.append(f"Start date: {error_msg}")
        elif self.selected_start_date:
            start_date = self.selected_start_date
        else:
            all_errors.append("Please select or enter a start date")
        
        # Validate end date
        if end_date_str:
            is_valid, parsed_date, error_msg = self.validate_date_format(end_date_str)
            if is_valid:
                end_date = parsed_date
            else:
                all_errors.append(f"End date: {error_msg}")
        elif self.selected_end_date:
            end_date = self.selected_end_date
        else:
            end_date = start_date  # Single day trip
        
        # Validate date range if both dates are valid
        if start_date and end_date:
            is_valid, error_msg = self.validate_date_range(start_date, end_date)
            if not is_valid:
                all_errors.append(error_msg)
            else:
                # Check for date warnings
                warnings = self.validate_date_warnings(start_date, end_date)
                all_warnings.extend(warnings)
                
                # Check for overlapping dates
                exclude_index = self.edit_index if self.edit_mode else None
                has_overlap, conflicts = self.check_date_overlap(start_date, end_date, exclude_index)
                
                if has_overlap:
                    # Show overlap dialog
                    action = self.show_overlap_dialog(conflicts)
                    if action == 'cancel':
                        return
                    elif action == 'adjust':
                        # User wants to adjust dates - focus on start date field
                        self.start_date_entry.focus_set()
                        return
                    # If action == 'ignore', continue with saving
        
        # === LOCATION VALIDATION ===
        
        location = self.location_entry.get()
        is_valid, cleaned_location, location_warnings = self.validate_location(location)
        if not is_valid:
            all_errors.extend(location_warnings)
        else:
            all_warnings.extend(location_warnings)
            location = cleaned_location
        
        # === COMMENT VALIDATION ===
        
        comment = self.comment_text.get(1.0, tk.END)
        is_valid, cleaned_comment, comment_warnings = self.validate_comment(comment)
        if not is_valid:
            all_errors.extend(comment_warnings)
        else:
            all_warnings.extend(comment_warnings)
            comment = cleaned_comment
        
        # === HANDLE ERRORS ===
        
        if all_errors:
            self.show_validation_errors_dialog(all_errors)
            return
        
        # === HANDLE WARNINGS ===
        
        if all_warnings:
            if not self.show_warnings_dialog(all_warnings):
                return
        
        # === SAVE RECORD ===
        
        # Create record
        record = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'location': location,
            'comment': comment
        }
        
        if self.edit_mode and self.edit_index is not None:
            # Update existing record
            self.travel_records[self.edit_index] = record
            self.edit_mode = False
            self.edit_index = None
            success_message = "✅ Travel record updated successfully!"
        else:
            # Add new record
            self.travel_records.append(record)
            success_message = "✅ Travel record added successfully!"
        
        self.save_data()
        self.update_calendar_display()
        self.update_location_dropdown()
        
        # Update year dropdown in report window if it's open
        if (hasattr(self, '_current_year_combo') and hasattr(self, '_current_year_var') and 
            hasattr(self, '_current_filter_vars') and hasattr(self, '_current_records_tree') and 
            self.report_window and self.report_window.winfo_exists()):
            self.update_year_dropdown(self._current_year_combo, self._current_year_var, 
                                     self._current_filter_vars, self._current_records_tree)
        
        self.clear_form()
        
        messagebox.showinfo("Success", success_message)
    
    def clear_form(self):
        """Clear the form fields"""
        self.location_entry.delete(0, tk.END)
        self.comment_text.delete(1.0, tk.END)
        self.clear_dates()
        # Reset edit mode
        self.edit_mode = False
        self.edit_index = None
    
    def get_record_color_tag(self, record):
        """Determine the color tag for a record based on its date range"""
        current_date = datetime.now().date()
        start_date = datetime.strptime(record['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(record['end_date'], '%Y-%m-%d').date()
        
        if end_date < current_date:
            return 'past'
        elif start_date <= current_date <= end_date:
            return 'current'
        else:
            return 'future'
    
    def configure_treeview_tags(self, records_tree):
        """Configure modern color tags for the treeview"""
        records_tree.tag_configure('past', 
                                  background='#f1f5f9', 
                                  foreground='#64748b')
        records_tree.tag_configure('current', 
                                  background='#dcfce7', 
                                  foreground='#15803d')
        records_tree.tag_configure('future', 
                                  background='#fef3c7', 
                                  foreground='#d97706')
    
    def update_records_display_filtered(self, records_tree, filter_vars, year_var=None):
        """Update the travel records display with filtering applied"""
        # Clear existing items
        for item in records_tree.get_children():
            records_tree.delete(item)
        
        # Configure color tags
        self.configure_treeview_tags(records_tree)
        
        # Get enabled filters
        enabled_filters = []
        if filter_vars['past'].get():
            enabled_filters.append('past')
        if filter_vars['current'].get():
            enabled_filters.append('current')
        if filter_vars['future'].get():
            enabled_filters.append('future')
        
        # If no filters are enabled, show nothing
        if not enabled_filters:
            return
        
        # Get selected year
        selected_year = None
        if year_var and year_var.get() != "All Years":
            try:
                selected_year = int(year_var.get())
            except:
                pass
        
        # Filter records
        filtered_records = []
        for record in self.travel_records:
            # Check status filter
            record_type = self.get_record_color_tag(record)
            if record_type not in enabled_filters:
                continue
            
            # Check year filter
            if selected_year is not None:
                try:
                    start_date = datetime.strptime(record['start_date'], '%Y-%m-%d')
                    end_date = datetime.strptime(record['end_date'], '%Y-%m-%d')
                    
                    # Include record if it overlaps with the selected year
                    if not (start_date.year <= selected_year <= end_date.year):
                        continue
                except:
                    continue
            
            filtered_records.append(record)
        
        # Sort by start date (most recent first)
        sorted_records = sorted(filtered_records, key=lambda x: x['start_date'], reverse=True)
        
        # Add filtered records to tree
        for record in sorted_records:
            # Truncate comment if it's too long for display
            comment = record.get('comment', '')
            if len(comment) > 50:
                comment = comment[:47] + "..."
            
            # Get the appropriate color tag
            color_tag = self.get_record_color_tag(record)
            
            records_tree.insert('', tk.END, values=(
                record['start_date'],
                record['end_date'],
                record['location'],
                comment
            ), tags=(color_tag,))
    
    def update_records_display(self, records_tree):
        """Update the travel records display in the report window"""
        # Clear existing items
        for item in records_tree.get_children():
            records_tree.delete(item)
        
        # Configure color tags
        self.configure_treeview_tags(records_tree)
        
        # Add records sorted by start date
        sorted_records = sorted(self.travel_records, key=lambda x: x['start_date'], reverse=True)
        for record in sorted_records:
            # Truncate comment if it's too long for display
            comment = record.get('comment', '')
            if len(comment) > 50:
                comment = comment[:47] + "..."
            
            # Get the appropriate color tag
            color_tag = self.get_record_color_tag(record)
            
            records_tree.insert('', tk.END, values=(
                record['start_date'],
                record['end_date'],
                record['location'],
                comment
            ), tags=(color_tag,))
    
    def edit_record(self, records_tree, report_window=None):
        """Edit selected travel record by populating main window"""
        selection = records_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to edit")
            if self.report_window:
                self.report_window.lift()
                self.report_window.focus_force()
            return
        
        item = selection[0]
        values = records_tree.item(item, 'values')
        
        # Find the actual record index
        start_date_str = values[0]
        end_date_str = values[1]
        location_str = values[2]
        comment_display = values[3]
        
        # Find the matching record
        for i, record in enumerate(self.travel_records):
            record_comment = record.get('comment', '')
            display_comment = record_comment[:47] + "..." if len(record_comment) > 50 else record_comment
            
            if (record['start_date'] == start_date_str and 
                record['end_date'] == end_date_str and 
                record['location'] == location_str and
                display_comment == comment_display):
                
                # Populate main window with record data
                self.start_date_entry.delete(0, tk.END)
                self.start_date_entry.insert(0, record['start_date'])
                
                self.end_date_entry.delete(0, tk.END)
                self.end_date_entry.insert(0, record['end_date'])
                
                self.location_entry.delete(0, tk.END)
                self.location_entry.insert(0, record['location'])
                
                self.comment_text.delete(1.0, tk.END)
                self.comment_text.insert(1.0, record.get('comment', ''))
                
                # Set selected dates for calendar display
                self.selected_start_date = datetime.strptime(record['start_date'], '%Y-%m-%d')
                self.selected_end_date = datetime.strptime(record['end_date'], '%Y-%m-%d')
                self.selecting_range = False
                
                # Navigate calendar to the start date's month/year
                start_date_obj = datetime.strptime(record['start_date'], '%Y-%m-%d')
                self.current_month = start_date_obj.month
                self.current_year = start_date_obj.year
                
                # Set edit mode
                self.edit_mode = True
                self.edit_index = i
                
                # Update calendar display and close report window
                self.update_calendar_display()
                self._on_report_window_close()
                
                messagebox.showinfo("Edit Mode", "✏️ Record loaded for editing. Calendar navigated to travel dates. Click 'Save Travel' to update.")
                break
    
    def update_year_dropdown(self, year_combo, year_var, filter_vars, records_tree):
        """Update the year dropdown with current available years"""
        # Get available years
        available_years = self.get_available_years()
        current_year = datetime.now().year
        
        # Store currently selected year
        current_selection = year_var.get()
        
        # Update dropdown options
        year_options = ["All Years"] + [str(year) for year in available_years]
        year_combo['values'] = year_options
        
        # Preserve selection if still valid, otherwise reset to sensible default
        if current_selection in year_options:
            year_var.set(current_selection)
        elif str(current_year) in year_options:
            year_var.set(str(current_year))
        else:
            year_var.set("All Years")
        
        # Refresh the records display with updated year filter
        self.update_records_display_filtered(records_tree, filter_vars, year_var)

    def delete_record(self, records_tree, report_window=None):
        """Delete selected travel record from the report window"""
        selection = records_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to delete")
            if self.report_window:
                self.report_window.lift()
                self.report_window.focus_force()
            return
        
        if messagebox.askyesno("Confirm", "🗑️ Are you sure you want to delete this record?"):
            item = selection[0]
            values = records_tree.item(item, 'values')
            
            # Find and remove the record
            for i, record in enumerate(self.travel_records):
                record_comment = record.get('comment', '')
                display_comment = record_comment[:47] + "..." if len(record_comment) > 50 else record_comment
                
                if (record['start_date'] == values[0] and 
                    record['end_date'] == values[1] and 
                    record['location'] == values[2] and
                    display_comment == values[3]):
                    del self.travel_records[i]
                    break
            
            self.save_data()
            self.update_calendar_display()
            self.update_location_dropdown()
            
            # Update year dropdown and records display
            if (hasattr(self, '_current_year_combo') and hasattr(self, '_current_year_var') and 
                hasattr(self, '_current_filter_vars') and hasattr(self, '_current_records_tree')):
                self.update_year_dropdown(self._current_year_combo, self._current_year_var, 
                                         self._current_filter_vars, self._current_records_tree)
            else:
                # Fallback: just update records display
                self.update_records_display(records_tree)
        
        if self.report_window:
            self.report_window.lift()
            self.report_window.focus_force()
    
    def sort_records(self, records_tree, column):
        """Sort records by the specified column"""
        # Toggle sort direction if clicking the same column
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Define sort keys for different columns
        def sort_key(record):
            if column == 'Start':
                return record['start_date']
            elif column == 'End':
                return record['end_date']
            elif column == 'Location':
                return record['location'].lower()
            return ''
        
        # Sort the records
        sorted_records = sorted(self.travel_records, key=sort_key, reverse=self.sort_reverse)
        
        # Update the display with sorted records
        self.update_records_display_sorted(records_tree, sorted_records)
        
        # Update column heading to show sort direction
        self.update_column_headers(records_tree, column)
    
    def update_records_display_sorted(self, records_tree, sorted_records):
        """Update the travel records display with sorted records"""
        # Clear existing items
        for item in records_tree.get_children():
            records_tree.delete(item)
        
        # Configure color tags
        self.configure_treeview_tags(records_tree)
        
        # Add sorted records
        for record in sorted_records:
            # Truncate comment if it's too long for display
            comment = record.get('comment', '')
            if len(comment) > 50:
                comment = comment[:47] + "..."
            
            # Get the appropriate color tag
            color_tag = self.get_record_color_tag(record)
            
            records_tree.insert('', tk.END, values=(
                record['start_date'],
                record['end_date'],
                record['location'],
                comment
            ), tags=(color_tag,))
    
    def update_column_headers(self, records_tree, sorted_column):
        """Update column headers to show sort indicators"""
        # Reset all headers first
        records_tree.heading('Start', text='Start Date', anchor='w')
        records_tree.heading('End', text='End Date', anchor='w')
        records_tree.heading('Location', text='Location', anchor='w')
        records_tree.heading('Comment', text='Notes', anchor='w')
        
        # Add sort indicator to the sorted column
        if sorted_column:
            arrow = ' ↓' if self.sort_reverse else ' ↑'
            if sorted_column == 'Start':
                records_tree.heading('Start', text=f'Start Date{arrow}', anchor='w')
            elif sorted_column == 'End':
                records_tree.heading('End', text=f'End Date{arrow}', anchor='w')
            elif sorted_column == 'Location':
                records_tree.heading('Location', text=f'Location{arrow}', anchor='w')
    
    def show_report(self):
        """Show modern travel report in a new window"""
        if not self.travel_records:
            messagebox.showinfo("Report", "📈 No travel records found.")
            return
        
        # Check if report window already exists
        if self.report_window and self.report_window.winfo_exists():
            # Bring existing window to front
            self.report_window.lift()
            self.report_window.focus_force()
            return
        
        # Reset sorting state
        self.sort_column = None
        self.sort_reverse = False
        
        # Calculate statistics
        total_days = 0
        trips_taken = 0  # New: count trips_taken (only past and current)
        future_trips = 0  # New: count future trips
        locations = set()
        current_date = datetime.now()
        year_start = datetime(current_date.year, 1, 1)
        days_in_year_so_far = (current_date - year_start).days + 1
        
        for record in self.travel_records:
            start_date = datetime.strptime(record['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(record['end_date'], '%Y-%m-%d')
            
            # Count future trips (trips that haven't started yet)
            if start_date > current_date:
                future_trips += 1
            
            # Only count trips and days in current year
            if start_date.year <= current_date.year and end_date.year >= current_date.year:
                # Only count as a trip if it has already started (past or current travel)
                if start_date <= current_date:
                    trips_taken += 1
                
                # Adjust dates to current year if needed
                count_start = max(start_date, year_start)
                count_end = min(end_date, current_date)
                
                if count_start <= count_end:
                    days = (count_end - count_start).days + 1
                    total_days += days
                    locations.add(record['location'])
        
        percentage = (total_days / days_in_year_so_far) * 100 if days_in_year_so_far > 0 else 0
        
        # Create modern report window
        report_window = tk.Toplevel(self.root)
        report_window.title("Travel Report")
        report_window.geometry("785x800")
        report_window.configure(bg=self.colors['background'])
        
        # Store reference and set up cleanup
        self.report_window = report_window
        report_window.protocol("WM_DELETE_WINDOW", self._on_report_window_close)
        
        # Main container
        main_container = tk.Frame(report_window, bg=self.colors['background'], padx=30, pady=30)
        main_container.pack(fill=tk.BOTH, expand=True)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(3, weight=1)
               
        # Statistics cards
        stats_frame = tk.Frame(main_container, bg=self.colors['background'])
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 30))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        stats_frame.columnconfigure(4, weight=1)  # New: 5th column
        
        # Trips Taken card 
        trips_card = tk.Frame(stats_frame, bg='#EA3680', relief='solid', bd=0, padx=16, pady=12)
        trips_card.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 4))
        
        tk.Label(trips_card, text="🚀", font=('Segoe UI', 20), 
                bg='#EA3680', fg='white').pack()
        tk.Label(trips_card, text=str(trips_taken), font=('Segoe UI', 24, 'bold'),
                bg='#EA3680', fg='white').pack()
        tk.Label(trips_card, text=f"Trips Taken ({current_date.year})", font=('Segoe UI', 10),
                bg='#EA3680', fg='white').pack()
        
        # Future trips card (second position)
        future_card = tk.Frame(stats_frame, bg='#E5B32D', relief='solid', bd=0, padx=16, pady=12)
        future_card.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=4)
        
        tk.Label(future_card, text="🗓️", font=('Segoe UI', 20),
                bg='#E5B32D', fg='white').pack()
        tk.Label(future_card, text=str(future_trips), font=('Segoe UI', 24, 'bold'),
                bg='#E5B32D', fg='white').pack()
        tk.Label(future_card, text="Upcoming Trips", font=('Segoe UI', 10),
                bg='#E5B32D', fg='white').pack()
        
        # Days traveled card (moved to third position)
        days_card = tk.Frame(stats_frame, bg=self.colors['primary'], relief='solid', bd=0, padx=16, pady=12)
        days_card.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=4)
        
        tk.Label(days_card, text="✈️", font=('Segoe UI', 20), 
                bg=self.colors['primary'], fg='white').pack()
        tk.Label(days_card, text=str(total_days), font=('Segoe UI', 24, 'bold'),
                bg=self.colors['primary'], fg='white').pack()
        tk.Label(days_card, text=f"Days Traveled ({current_date.year})", font=('Segoe UI', 10),
                bg=self.colors['primary'], fg='white').pack()
        
        # Percentage card (moved to fourth position)
        percent_card = tk.Frame(stats_frame, bg=self.colors['success'], relief='solid', bd=0, padx=16, pady=12)
        percent_card.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=4)
        
        tk.Label(percent_card, text="📈", font=('Segoe UI', 20),
                bg=self.colors['success'], fg='white').pack()
        tk.Label(percent_card, text=f"{percentage:.1f}%", font=('Segoe UI', 24, 'bold'),
                bg=self.colors['success'], fg='white').pack()
        tk.Label(percent_card, text="Percentage of Year", font=('Segoe UI', 10),
                bg=self.colors['success'], fg='white').pack()
        
        # Locations card (moved to fifth position)
        locations_card = tk.Frame(stats_frame, bg=self.colors['accent'], relief='solid', bd=0, padx=16, pady=12)
        locations_card.grid(row=0, column=4, sticky=(tk.W, tk.E), padx=(4, 0))
        
        tk.Label(locations_card, text="🌍", font=('Segoe UI', 20),
                bg=self.colors['accent'], fg='white').pack()
        tk.Label(locations_card, text=str(len(locations)), font=('Segoe UI', 24, 'bold'),
                bg=self.colors['accent'], fg='white').pack()
        tk.Label(locations_card, text="Locations Visited ", font=('Segoe UI', 10),
                bg=self.colors['accent'], fg='white').pack()
        
        # Filter section
        filter_frame = ttk.LabelFrame(main_container, text="🔍 Record Filter", style='Card.TLabelframe')
        filter_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        filter_inner = tk.Frame(filter_frame, bg=self.colors['surface'])
        filter_inner.pack(fill=tk.X, pady=10)
        
        # Create filter variables (all enabled by default)
        filter_vars = {
            'past': tk.BooleanVar(value=True),
            'current': tk.BooleanVar(value=True),
            'future': tk.BooleanVar(value=True)
        }
        
        # Get available years
        available_years = self.get_available_years()
        current_year = datetime.now().year
        
        # Year filter
        tk.Label(filter_inner, text="📅 Year:", 
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(side=tk.LEFT, padx=(0, 10))
        
        year_var = tk.StringVar()
        year_combo = ttk.Combobox(filter_inner, textvariable=year_var, 
                                 style='Modern.TCombobox', 
                                 font=('Segoe UI', 10),
                                 width=12, state="readonly")
        
        # Populate year dropdown
        year_options = ["All Years"] + [str(year) for year in available_years]
        year_combo['values'] = year_options
        
        # Set default to current year if available, otherwise "All Years"
        if str(current_year) in year_options:
            year_var.set(str(current_year))
        else:
            year_var.set("All Years")
        
        year_combo.pack(side=tk.LEFT, padx=(0, 30))
        
        # Store references for updating when records are modified
        self._current_year_combo = year_combo
        self._current_year_var = year_var
        self._current_filter_vars = filter_vars
        
        # Status filters (same row)
        filter_items = [
            ("Past", "#f1f5f9", "#64748b", filter_vars['past']),
            ("Current", "#dcfce7", "#15803d", filter_vars['current']),
            ("Future", "#fef3c7", "#d97706", filter_vars['future'])
        ]
        
        # Create filter checkboxes with labels
        for i, (text, bg_color, fg_color, var) in enumerate(filter_items):
            # Container for checkbox and label
            filter_container = tk.Frame(filter_inner, bg=self.colors['surface'])
            filter_container.pack(side=tk.LEFT, padx=(0, 30))
            
            # Checkbox to the left of label
            checkbox = tk.Checkbutton(filter_container, 
                                    variable=var,
                                    bg=self.colors['surface'],
                                    activebackground=self.colors['surface'],
                                    relief='flat',
                                    command=lambda: self.update_records_display_filtered(records_tree, filter_vars, year_var))
            checkbox.pack(side=tk.LEFT, padx=(0, 2))
            
            # Color-coded label to the right of checkbox
            filter_label = tk.Label(filter_container, text=f"  {text}  ",
                                  bg=bg_color, fg=fg_color,
                                  relief="solid", borderwidth=1,
                                  font=('Segoe UI', 10))
            filter_label.pack(side=tk.LEFT)
        
        # Bind year selection change
        year_combo.bind('<<ComboboxSelected>>', 
                       lambda e: self.update_records_display_filtered(records_tree, filter_vars, year_var))
        
        # Travel records
        records_frame = ttk.LabelFrame(main_container, text="📋 Travel Records", style='Card.TLabelframe')
        records_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        records_frame.columnconfigure(0, weight=1)
        records_frame.rowconfigure(0, weight=1)
        
        # Treeview with modern styling
        tree_frame = tk.Frame(records_frame, bg=self.colors['surface'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        records_tree = ttk.Treeview(tree_frame, columns=('Start', 'End', 'Location', 'Comment'), 
                                   show='headings', height=15)
        
        # Configure headers
        records_tree.heading('Start', text='Start Date', anchor='w')
        records_tree.heading('End', text='End Date', anchor='w')
        records_tree.heading('Location', text='Location', anchor='w')
        records_tree.heading('Comment', text='Notes', anchor='w')
        
        # Add click handlers for sortable columns
        records_tree.heading('Start', command=lambda: self.sort_records(records_tree, 'Start'))
        records_tree.heading('End', command=lambda: self.sort_records(records_tree, 'End'))
        records_tree.heading('Location', command=lambda: self.sort_records(records_tree, 'Location'))
        
        # Set column widths
        records_tree.column('Start', width=120)
        records_tree.column('End', width=120)
        records_tree.column('Location', width=200)
        records_tree.column('Comment', width=400)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=records_tree.yview)
        records_tree.configure(yscrollcommand=scrollbar.set)
        
        records_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Store reference to records tree for updates
        self._current_records_tree = records_tree
        
        # Initial records display with filtering
        self.update_records_display_filtered(records_tree, filter_vars, year_var)
        
        # Action buttons
        buttons_frame = tk.Frame(main_container, bg=self.colors['background'])
        buttons_frame.grid(row=4, column=0, pady=(20, 0))
        
        edit_btn = tk.Button(buttons_frame, text="✏️ Edit Record",
                            bg=self.colors['success'], fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            relief='flat', bd=0, padx=12, pady=8,
                            activebackground='#059669', activeforeground='white',
                            command=lambda: self.edit_record(records_tree))
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = tk.Button(buttons_frame, text="🗑️ Delete Record",
                              bg=self.colors['danger'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', bd=0, padx=12, pady=8,
                              activebackground='#dc2626', activeforeground='white',
                              command=lambda: self.delete_record(records_tree))
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(buttons_frame, text="✖️ Close",
                             bg=self.colors['secondary'], fg='white',
                             font=('Segoe UI', 10, 'bold'),
                             relief='flat', bd=0, padx=12, pady=8,
                             activebackground='#475569', activeforeground='white',
                             command=self._on_report_window_close)
        close_btn.pack(side=tk.LEFT)

    def _on_report_window_close(self):
        """Handle report window close event"""
        if self.report_window:
            self.report_window.destroy()
            self.report_window = None
            
        # Clear stored references
        if hasattr(self, '_current_year_combo'):
            delattr(self, '_current_year_combo')
        if hasattr(self, '_current_year_var'):
            delattr(self, '_current_year_var')
        if hasattr(self, '_current_filter_vars'):
            delattr(self, '_current_filter_vars')
        if hasattr(self, '_current_records_tree'):
            delattr(self, '_current_records_tree')

def main():
    root = tk.Tk()
    app = ModernTravelCalendar(root)
    root.mainloop()

if __name__ == "__main__":
    main()