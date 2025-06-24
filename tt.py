import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import calendar
import json
import os
import platform
import shutil
import sys
import subprocess
import webbrowser
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class ModernTravelCalendar:
    def __init__(self, root):
        self.root = root
        self.root.title("Travel Tracker")
        self.root.geometry("1000x720")

        # Set calendar to start with Sunday
        calendar.setfirstweekday(6)  # Sunday = 6

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
            'max_comment_length': 1000,
            # Status toggle defaults
            'default_show_past': False,
            'default_show_current': True,
            'default_show_future': True,
            # Year filter default
            'default_year_filter': 'Current Year',  # Options: 'All Years', 'Current Year'
            # Export settings
            'export_delimiter': ',',  # Default to comma
            'export_directory': str(Path.home() / 'Downloads') if (Path.home() / 'Downloads').exists() else str(Path.home())  # Default to Downloads or Home folder
        }
        self.load_config()  # Load saved settings from config file
        
        self.setup_modern_styles()
        self.setup_menu()
        self.setup_ui()
        self.update_calendar_display()
        self.update_location_dropdown()
    
    def calculate_trip_days(self, start_date_str: str, end_date_str: str) -> int:
        """Calculate the number of days for a trip (inclusive of both start and end dates)"""
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            return (end_date - start_date).days + 1
        except ValueError:
            return 0
    
    def format_date_for_display(self, date_str: str) -> str:
        """Convert YYYY-MM-DD format to MM-DD-YYYY for display in reports"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%m-%d-%Y')
        except ValueError:
            return date_str  # Return original if parsing fails
    
    def format_date_for_entry(self, date_str: str) -> str:
        """Convert YYYY-MM-DD format to MM/DD/YYYY for entry fields"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%m/%d/%Y')
        except ValueError:
            return date_str  # Return original if parsing fails
    
    def parse_display_date_to_storage(self, date_str: str) -> str:
        """Convert MM-DD-YYYY display format back to YYYY-MM-DD storage format"""
        try:
            date_obj = datetime.strptime(date_str, '%m-%d-%Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            return date_str  # Return original if parsing fails
    
    def parse_entry_date_to_storage(self, date_str: str) -> str:
        """Convert MM/DD/YYYY entry format back to YYYY-MM-DD storage format"""
        try:
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            return date_str  # Return original if parsing fails
    
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
        
        # Try multiple date formats - Updated to prioritize MM/DD/YYYY for entry fields
        formats = ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y']
        
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
        
        return False, None, f"Invalid date format. Please use MM/DD/YYYY, MM-DD-YYYY, YYYY-MM-DD, or DD/MM/YYYY"
    
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
            start_str = self.format_date_for_display(record['start_date'])
            end_str = self.format_date_for_display(record['end_date'])
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
        
        tk.Label(message_frame, text="Error", 
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
        
        tk.Label(message_frame, text="Warnings", 
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
    
    def get_default_export_directory(self):
        """Get the default export directory, falling back to safe alternatives"""
        try:
            # Try the user's configured directory first
            configured_dir = Path(self.validation_settings['export_directory'])
            if configured_dir.exists() and configured_dir.is_dir():
                return str(configured_dir)
        except:
            pass
        
        # Try common directories as fallbacks
        fallback_dirs = [
            Path.home() / 'Documents',
            Path.home() / 'Downloads', 
            Path.home() / 'Desktop',
            Path.home(),
            Path.cwd()
        ]
        
        for directory in fallback_dirs:
            try:
                if directory.exists() and directory.is_dir():
                    return str(directory)
            except:
                continue
        
        # Last resort - current working directory
        return str(Path.cwd())
    
    def export_travel_records(self):
        """Export currently filtered travel records to CSV"""
        # Check if we have the necessary references from the report window
        if not (hasattr(self, '_current_filter_vars') and hasattr(self, '_current_year_var') and 
                hasattr(self, '_current_search_var')):
            messagebox.showerror("Export Error", "Please open the Travel Report window before exporting.")
            return
        
        # Get filtered records using the same logic as the display
        filtered_records = self.get_filtered_records(
            self._current_filter_vars, 
            self._current_year_var, 
            self._current_search_var
        )
        
        if not filtered_records:
            messagebox.showwarning("No Data", "No records match the current filters. Nothing to export.")
            return
        
        # Get export settings
        delimiter = self.validation_settings['export_delimiter']
        delimiter_char = '|' if delimiter == '|' else ','
        
        # Prepare default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"travel_records_{timestamp}.csv"
        
        # Get initial directory
        initial_dir = self.get_default_export_directory()
        
        # Open file dialog
        file_path = filedialog.asksaveasfilename(
            title="Export Travel Records",
            initialdir=initial_dir,
            initialfile=default_filename,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Write CSV file
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                if delimiter_char == ',':
                    writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                else:
                    writer = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL)
                
                # Write header
                writer.writerow(['Departure Date', 'Return Date', 'Days', 'Location', 'Notes'])
                
                # Write data
                for record in filtered_records:
                    days = self.calculate_trip_days(record['start_date'], record['end_date'])
                    writer.writerow([
                        self.format_date_for_display(record['start_date']),
                        self.format_date_for_display(record['end_date']),
                        str(days),
                        record['location'],
                        record.get('comment', '')
                    ])
            
            # Show success message
            messagebox.showinfo("Export Successful", 
                               f"✅ Successfully exported {len(filtered_records)} records to:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export records:\n{str(e)}")
    
    def get_filtered_records(self, filter_vars, year_var=None, search_var=None):
        """Get records that match the current filters (same logic as display filtering)"""
        # Get enabled filters
        enabled_filters = []
        if filter_vars['past'].get():
            enabled_filters.append('past')
        if filter_vars['current'].get():
            enabled_filters.append('current')
        if filter_vars['future'].get():
            enabled_filters.append('future')
        
        # If no filters are enabled, return empty list
        if not enabled_filters:
            return []
        
        # Get selected year
        selected_year = None
        if year_var and year_var.get() != "All Years":
            try:
                selected_year = int(year_var.get())
            except:
                pass
        
        # Get search text
        search_text = ""
        if search_var:
            search_text = search_var.get().strip().lower()
            # Don't search if it's the placeholder text
            if search_text == "search locations, dates, or notes...":
                search_text = ""
        
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
            
            # Check search filter
            if search_text:
                # Search in location, dates, and comments
                searchable_text = (
                    record['location'].lower() + " " +
                    record['start_date'].lower() + " " +
                    record['end_date'].lower() + " " +
                    record.get('comment', '').lower()
                )
                
                if search_text not in searchable_text:
                    continue
            
            filtered_records.append(record)
        
        # Apply sorting if there is an active sort column
        if self.sort_column:
            # Define sort keys for different columns
            def sort_key(record):
                if self.sort_column == 'Start':
                    return record['start_date']
                elif self.sort_column == 'End':
                    return record['end_date']
                elif self.sort_column == 'Days':
                    return self.calculate_trip_days(record['start_date'], record['end_date'])
                elif self.sort_column == 'Location':
                    return record['location'].lower()
                return ''
            
            # Sort the filtered records
            filtered_records = sorted(filtered_records, key=sort_key, reverse=self.sort_reverse)
        else:
            # Default sort by start date (oldest first) when no column sorting is active
            filtered_records = sorted(filtered_records, key=lambda x: x['start_date'], reverse=False)
        
        return filtered_records
    
    # ========== END EXPORT METHODS ==========
    
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
        file_menu.add_command(label="Open Data Directory", command=self.open_data_location, accelerator="(Ctrl+O)")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application, accelerator="(Ctrl+Q)")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Travel Report", command=self.show_report, accelerator="(Ctrl+R)")
        view_menu.add_separator()

        view_menu.add_command(label="Settings", command=self.show_validation_settings, accelerator="(Ctrl+S)")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.open_documentation, accelerator="(Ctrl+D)")
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-q>', lambda e: self.exit_application())
        self.root.bind('<Control-r>', lambda e: self.show_report())
        self.root.bind('<Control-s>', lambda e: self.show_validation_settings())
        self.root.bind('<Control-o>', lambda e: self.open_data_location())
        self.root.bind('<Control-d>', lambda e: self.open_documentation())
    
    def show_validation_settings(self):
        """Show dialog for configuring validation settings"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚙️ Settings")
        dialog.geometry("400x475")  # Increased height for new Year filter setting
        dialog.configure(bg=self.colors['background'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 50))
        
        # Main frame
        main_frame = tk.Frame(dialog, bg=self.colors['background'], padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Settings variables
        settings_vars = {}
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # ========== VALIDATION TAB ==========
        validation_tab = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(validation_tab, text="Validation")
        
        validation_content = tk.Frame(validation_tab, bg=self.colors['surface'], padx=20, pady=20)
        validation_content.pack(fill=tk.BOTH, expand=True)
        
        # Allow overlaps setting
        settings_vars['allow_overlaps'] = tk.BooleanVar(value=self.validation_settings['allow_overlaps'])
        tk.Checkbutton(validation_content, text="Allow Overlapping Dates",
                      variable=settings_vars['allow_overlaps'],
                      bg=self.colors['surface'],
                      font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 20))
        
        # Future date warnings
        settings_vars['warn_future_dates'] = tk.BooleanVar(value=self.validation_settings['warn_future_dates'])
        
        def toggle_future_entry():
            """Enable/disable future days entry based on checkbox state"""
            if settings_vars['warn_future_dates'].get():
                future_entry.config(state='normal')
            else:
                future_entry.config(state='disabled')
        
        tk.Checkbutton(validation_content, text="Limit Future Dates",
                      variable=settings_vars['warn_future_dates'],
                      bg=self.colors['surface'],
                      font=('Segoe UI', 11),
                      command=toggle_future_entry).pack(anchor=tk.W, pady=(0, 10))
        
        # Future days setting - horizontal layout
        future_days_frame = tk.Frame(validation_content, bg=self.colors['surface'])
        future_days_frame.pack(fill=tk.X, padx=(20, 0), pady=(0, 20))
        
        tk.Label(future_days_frame, text="Future Limit:",
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
        
        tk.Checkbutton(validation_content, text="Limit Past Dates",
                      variable=settings_vars['warn_past_dates'],
                      bg=self.colors['surface'],
                      font=('Segoe UI', 11),
                      command=toggle_past_entry).pack(anchor=tk.W, pady=(0, 10))
        
        # Past days setting - horizontal layout
        past_days_frame = tk.Frame(validation_content, bg=self.colors['surface'])
        past_days_frame.pack(fill=tk.X, padx=(20, 0))
        
        tk.Label(past_days_frame, text="Past Limit:",
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
        
        # ========== REPORT TAB ==========
        report_tab = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(report_tab, text="Report")
        
        report_content = tk.Frame(report_tab, bg=self.colors['surface'], padx=20, pady=20)
        report_content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(report_content, text="Set Default Status Toggles",
                font=('Segoe UI', 11),
                fg=self.colors['text_light'],
                bg=self.colors['surface']).pack(anchor=tk.W, pady=(0, 20))
        
        # Past toggle default
        settings_vars['default_show_past'] = tk.BooleanVar(value=self.validation_settings['default_show_past'])
        tk.Checkbutton(report_content, text="Past Trips",
                      variable=settings_vars['default_show_past'],
                      bg=self.colors['surface'],
                      font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 15))
        
        # Current toggle default
        settings_vars['default_show_current'] = tk.BooleanVar(value=self.validation_settings['default_show_current'])
        tk.Checkbutton(report_content, text="Current Trips",
                      variable=settings_vars['default_show_current'],
                      bg=self.colors['surface'],
                      font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 15))
        
        # Future toggle default
        settings_vars['default_show_future'] = tk.BooleanVar(value=self.validation_settings['default_show_future'])
        tk.Checkbutton(report_content, text="Future Trips",
                      variable=settings_vars['default_show_future'],
                      bg=self.colors['surface'],
                      font=('Segoe UI', 11)).pack(anchor=tk.W, pady=(0, 20))
        
        # Year filter default setting
        tk.Label(report_content, text="Set Default Year Filter",
                font=('Segoe UI', 11),
                fg=self.colors['text_light'],
                bg=self.colors['surface']).pack(anchor=tk.W, pady=(0, 10))
        
        year_filter_frame = tk.Frame(report_content, bg=self.colors['surface'])
        year_filter_frame.pack(fill=tk.X)
        
        tk.Label(year_filter_frame, text="Default Year:",
                font=('Segoe UI', 11),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(side=tk.LEFT)
        
        settings_vars['default_year_filter'] = tk.StringVar(value=self.validation_settings['default_year_filter'])
        year_filter_combo = ttk.Combobox(year_filter_frame, textvariable=settings_vars['default_year_filter'],
                                        values=["All Years", "Current Year"],
                                        state="readonly", width=15, font=('Segoe UI', 10))
        year_filter_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # ========== INPUT TAB ==========
        input_tab = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(input_tab, text="Input")
        
        input_content = tk.Frame(input_tab, bg=self.colors['surface'], padx=20, pady=20)
        input_content.pack(fill=tk.BOTH, expand=True)
        
        # Location length - horizontal layout
        location_frame = tk.Frame(input_content, bg=self.colors['surface'])
        location_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(location_frame, text="Max. Location Length:",
                font=('Segoe UI', 11),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(side=tk.LEFT)
        
        settings_vars['max_location_length'] = tk.StringVar(value=str(self.validation_settings['max_location_length']))
        loc_entry = tk.Entry(location_frame, textvariable=settings_vars['max_location_length'],
                            width=10, font=('Segoe UI', 10))
        loc_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Comment length - horizontal layout
        comment_frame = tk.Frame(input_content, bg=self.colors['surface'])
        comment_frame.pack(fill=tk.X)
        
        tk.Label(comment_frame, text="Max. Notes Length:",
                font=('Segoe UI', 11),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(side=tk.LEFT)
        
        settings_vars['max_comment_length'] = tk.StringVar(value=str(self.validation_settings['max_comment_length']))
        comment_entry = tk.Entry(comment_frame, textvariable=settings_vars['max_comment_length'],
                                width=10, font=('Segoe UI', 10))
        comment_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # ========== EXPORT TAB ==========
        export_tab = tk.Frame(notebook, bg=self.colors['surface'])
        notebook.add(export_tab, text="Export")
        
        export_content = tk.Frame(export_tab, bg=self.colors['surface'], padx=20, pady=20)
        export_content.pack(fill=tk.BOTH, expand=True)
        
        # Delimiter setting - horizontal layout
        delimiter_frame = tk.Frame(export_content, bg=self.colors['surface'])
        delimiter_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(delimiter_frame, text="Delimiter:",
                font=('Segoe UI', 11),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(side=tk.LEFT)
        
        settings_vars['export_delimiter'] = tk.StringVar(value=self.validation_settings['export_delimiter'])
        delimiter_combo = ttk.Combobox(delimiter_frame, textvariable=settings_vars['export_delimiter'],
                                      values=["Comma ( , )", "Pipe ( | )"],
                                      state="readonly", width=15, font=('Segoe UI', 10))
        
        # Set the display value based on the stored delimiter
        if self.validation_settings['export_delimiter'] == ',':
            delimiter_combo.set("Comma ( , )")
        else:
            delimiter_combo.set("Pipe ( | )")
        
        delimiter_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Export directory setting
        directory_frame = tk.Frame(export_content, bg=self.colors['surface'])
        directory_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(directory_frame, text="Export Directory:",
                font=('Segoe UI', 11),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(anchor=tk.W, pady=(0, 5))
        
        directory_entry_frame = tk.Frame(directory_frame, bg=self.colors['surface'])
        directory_entry_frame.pack(fill=tk.X)
        
        settings_vars['export_directory'] = tk.StringVar(value=self.validation_settings['export_directory'])
        directory_entry = tk.Entry(directory_entry_frame, textvariable=settings_vars['export_directory'],
                                  font=('Segoe UI', 10))
        directory_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def browse_directory():
            """Browse for export directory"""
            current_dir = settings_vars['export_directory'].get()
            if not os.path.exists(current_dir):
                current_dir = str(Path.home())
            
            new_dir = filedialog.askdirectory(
                title="Select Export Directory",
                initialdir=current_dir
            )
            
            if new_dir:
                settings_vars['export_directory'].set(new_dir)
        
        browse_btn = tk.Button(directory_entry_frame, text="Browse...",
                              bg=self.colors['primary'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', bd=0, padx=12, pady=6,
                              command=browse_directory)
        browse_btn.pack(side=tk.RIGHT)
        
        # Buttons
        buttons_frame = tk.Frame(main_frame, bg=self.colors['background'])
        buttons_frame.grid(row=1, column=0, pady=(20, 0))
        
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
                
                # Update status toggle defaults
                self.validation_settings['default_show_past'] = settings_vars['default_show_past'].get()
                self.validation_settings['default_show_current'] = settings_vars['default_show_current'].get()
                self.validation_settings['default_show_future'] = settings_vars['default_show_future'].get()
                
                # Update year filter default
                self.validation_settings['default_year_filter'] = settings_vars['default_year_filter'].get()
                
                # Update export settings
                delimiter_choice = settings_vars['export_delimiter'].get()
                if delimiter_choice == "Pipe ( | )":
                    self.validation_settings['export_delimiter'] = '|'
                else:
                    self.validation_settings['export_delimiter'] = ','
                
                self.validation_settings['export_directory'] = settings_vars['export_directory'].get()
                
                # Save settings to config file
                self.save_config()
                
                dialog.destroy()
                messagebox.showinfo("Settings Saved", "✅ Settings have been updated and saved.")
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
        
        # Travel days counter (between calendar and trips for month)
        travel_days_frame = tk.Frame(calendar_frame, bg=self.colors['surface'])
        travel_days_frame.pack(fill=tk.X, pady=(15, 10))
        
        self.travel_days_label = tk.Label(travel_days_frame, 
                                         font=('Segoe UI', 11, 'bold'),
                                         fg=self.colors['primary'],
                                         bg=self.colors['surface'])
        self.travel_days_label.pack()
        
        # Trips for month info (between travel days and legend)
        trips_frame = tk.Frame(calendar_frame, bg=self.colors['surface'])
        trips_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.trips_for_month_label = tk.Label(trips_frame, 
                                             font=('Segoe UI', 11, 'bold'),
                                             fg=self.colors['success'],
                                             bg=self.colors['surface'],
                                             wraplength=450,  # Wrap text to fit calendar width
                                             justify=tk.LEFT)
        self.trips_for_month_label.pack()
        
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
    
    def get_trips_for_month(self, year: int, month: int) -> List[Dict]:
        """Get travel records that occur within the specified month and year"""
        month_trips = []
        
        # Get the first and last day of the month
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        for record in self.travel_records:
            try:
                trip_start = datetime.strptime(record['start_date'], '%Y-%m-%d')
                trip_end = datetime.strptime(record['end_date'], '%Y-%m-%d')
                
                # Check if trip overlaps with the month
                if trip_start <= month_end and trip_end >= month_start:
                    month_trips.append(record)
                    
            except ValueError:
                # Skip records with invalid dates
                continue
        
        # Sort trips by start date
        month_trips.sort(key=lambda x: x['start_date'])
        return month_trips
    
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
    
    def get_default_year_selection(self, available_years):
        """Get the default year selection based on user preference"""
        current_year = datetime.now().year
        preference = self.validation_settings['default_year_filter']
        
        if preference == "All Years":
            return "All Years"
        elif preference == "Current Year":
            # Use current year if it's in the available years, otherwise fall back to "All Years"
            if str(current_year) in [str(year) for year in available_years]:
                return str(current_year)
            else:
                return "All Years"
        else:
            # Fallback for unknown preference
            return "All Years"
        """Get the default year selection based on user preference"""
        current_year = datetime.now().year
        preference = self.validation_settings['default_year_filter']
        
        if preference == "All Years":
            return "All Years"
        elif preference == "Current Year":
            # Use current year if it's in the available years, otherwise fall back to "All Years"
            if str(current_year) in [str(year) for year in available_years]:
                return str(current_year)
            else:
                return "All Years"
        elif preference == "Most Recent Year":
            # Use the most recent year with travel data, otherwise fall back to current year or "All Years"
            if available_years:
                return str(available_years[0])  # available_years is already sorted newest first
            elif str(current_year) in [str(year) for year in available_years]:
                return str(current_year)
            else:
                return "All Years"
        else:
            # Fallback for unknown preference
            return "All Years"
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
        
        # Day headers - Updated to start with Sunday
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
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
        
        # Update travel days counter
        travel_days = self.get_travel_days_for_month(self.current_year, self.current_month)
        month_name = calendar.month_name[self.current_month]
        
        if travel_days == 0:
            days_text = f"No travel days in {month_name} {self.current_year}"
        elif travel_days == 1:
            days_text = f"1 travel day in {month_name} {self.current_year}"
        else:
            days_text = f"{travel_days} travel days in {month_name} {self.current_year}"
        
        self.travel_days_label.config(text=f"✈️ {days_text}")
        
        # Update trips for month info
        month_trips = self.get_trips_for_month(self.current_year, self.current_month)
        if month_trips:
            trips_text_parts = []
            for trip in month_trips:
                location = trip['location']
                notes = trip.get('comment', '').strip()
                
                if notes:
                    # If notes are too long, truncate them
                    if len(notes) > 50:
                        notes = notes[:47] + "..."
                    trip_text = f"📍 {location} - {notes}"
                else:
                    trip_text = f"📍 {location}"
                
                trips_text_parts.append(trip_text)
            
            # Combine all trips with line breaks
            all_trips_text = "\n".join(trips_text_parts)
            self.trips_for_month_label.config(text=all_trips_text)
        else:
            # CHANGE: Instead of showing "No trips in [month]", set text to empty
            self.trips_for_month_label.config(text="")
    
    def get_travel_days_for_month(self, year: int, month: int) -> int:
        """Calculate total travel days for a specific month and year"""
        travel_days = 0
        
        # Get the first and last day of the month
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        for record in self.travel_records:
            try:
                trip_start = datetime.strptime(record['start_date'], '%Y-%m-%d')
                trip_end = datetime.strptime(record['end_date'], '%Y-%m-%d')
                
                # Calculate overlap between trip and month
                overlap_start = max(trip_start, month_start)
                overlap_end = min(trip_end, month_end)
                
                # If there's an overlap, count the days
                if overlap_start <= overlap_end:
                    days_in_month = (overlap_end - overlap_start).days + 1
                    travel_days += days_in_month
                    
            except ValueError:
                # Skip records with invalid dates
                continue
        
        return travel_days
    
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
            self.start_date_entry.insert(0, self.format_date_for_entry(clicked_date.strftime('%Y-%m-%d')))
            self.selecting_range = True
        elif self.selecting_range:
            # Second click - set end date
            if clicked_date >= self.selected_start_date:
                self.selected_end_date = clicked_date
                self.end_date_entry.delete(0, tk.END)
                self.end_date_entry.insert(0, self.format_date_for_entry(clicked_date.strftime('%Y-%m-%d')))
            else:
                # If clicked date is before start date, swap them
                self.selected_end_date = self.selected_start_date
                self.selected_start_date = clicked_date
                self.start_date_entry.delete(0, tk.END)
                self.start_date_entry.insert(0, self.format_date_for_entry(clicked_date.strftime('%Y-%m-%d')))
                self.end_date_entry.delete(0, tk.END)
                self.end_date_entry.insert(0, self.format_date_for_entry(self.selected_end_date.strftime('%Y-%m-%d')))
            self.selecting_range = False
        else:
            # Start new selection
            self.selected_start_date = clicked_date
            self.selected_end_date = None
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, self.format_date_for_entry(clicked_date.strftime('%Y-%m-%d')))
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
        
        # Validate end date - FIXED: Now requires end date instead of defaulting to start date
        if end_date_str:
            is_valid, parsed_date, error_msg = self.validate_date_format(end_date_str)
            if is_valid:
                end_date = parsed_date
            else:
                all_errors.append(f"End date: {error_msg}")
        elif self.selected_end_date:
            end_date = self.selected_end_date
        else:
            all_errors.append("Please select or enter a return date")
        
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
        
        # Update statistics cards if report window is open
        self.update_statistics_cards()
        
        # Update year dropdown in report window if it's open
        if (hasattr(self, '_current_year_combo') and hasattr(self, '_current_year_var') and 
            hasattr(self, '_current_filter_vars') and hasattr(self, '_current_records_tree') and
            hasattr(self, '_current_search_var') and 
            self.report_window and self.report_window.winfo_exists()):
            self.update_year_dropdown(self._current_year_combo, self._current_year_var, 
                                     self._current_filter_vars, self._current_records_tree, self._current_search_var)
        
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
                                  background='#dbeafe', 
                                  foreground='#1e40af')
        records_tree.tag_configure('current', 
                                  background='#dcfce7', 
                                  foreground='#15803d')
        records_tree.tag_configure('future', 
                                  background='#fef3c7', 
                                  foreground='#d97706')
    
    def update_records_display_filtered(self, records_tree, filter_vars, year_var=None, search_var=None):
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
        
        # Get search text
        search_text = ""
        if search_var:
            search_text = search_var.get().strip().lower()
            # Don't search if it's the placeholder text
            if search_text == "search locations, dates, or notes...":
                search_text = ""
        
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
            
            # Check search filter
            if search_text:
                # Search in location, dates, and comments
                searchable_text = (
                    record['location'].lower() + " " +
                    record['start_date'].lower() + " " +
                    record['end_date'].lower() + " " +
                    record.get('comment', '').lower()
                )
                
                if search_text not in searchable_text:
                    continue
            
            filtered_records.append(record)
        
        # Apply sorting if there is an active sort column
        if self.sort_column:
            # Define sort keys for different columns
            def sort_key(record):
                if self.sort_column == 'Start':
                    return record['start_date']
                elif self.sort_column == 'End':
                    return record['end_date']
                elif self.sort_column == 'Days':
                    return self.calculate_trip_days(record['start_date'], record['end_date'])
                elif self.sort_column == 'Location':
                    return record['location'].lower()
                return ''
            
            # Sort the filtered records
            filtered_records = sorted(filtered_records, key=sort_key, reverse=self.sort_reverse)
        else:
            # Default sort by start date (oldest first) when no column sorting is active
            filtered_records = sorted(filtered_records, key=lambda x: x['start_date'], reverse=False)
        
        # Add filtered records to tree
        for record in filtered_records:
            # Calculate days for the trip
            days = self.calculate_trip_days(record['start_date'], record['end_date'])
            
            # Truncate comment if it's too long for display
            comment = record.get('comment', '')
            if len(comment) > 50:
                comment = comment[:47] + "..."
            
            # Get the appropriate color tag
            color_tag = self.get_record_color_tag(record)
            
            records_tree.insert('', tk.END, values=(
                self.format_date_for_display(record['start_date']),
                self.format_date_for_display(record['end_date']),
                str(days),
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
        
        # Add records sorted by start date (oldest first)
        sorted_records = sorted(self.travel_records, key=lambda x: x['start_date'], reverse=False)
        for record in sorted_records:
            # Calculate days for the trip
            days = self.calculate_trip_days(record['start_date'], record['end_date'])
            
            # Truncate comment if it's too long for display
            comment = record.get('comment', '')
            if len(comment) > 50:
                comment = comment[:47] + "..."
            
            # Get the appropriate color tag
            color_tag = self.get_record_color_tag(record)
            
            records_tree.insert('', tk.END, values=(
                self.format_date_for_display(record['start_date']),
                self.format_date_for_display(record['end_date']),
                str(days),
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
        start_date_display = values[0]
        end_date_display = values[1]
        days_display = values[2]  # New: days column
        location_str = values[3]  # Updated index
        comment_display = values[4]  # Updated index
        
        # Convert display dates back to storage format for matching
        start_date_storage = self.parse_display_date_to_storage(start_date_display)
        end_date_storage = self.parse_display_date_to_storage(end_date_display)
        
        # Find the matching record
        for i, record in enumerate(self.travel_records):
            record_comment = record.get('comment', '')
            display_comment = record_comment[:47] + "..." if len(record_comment) > 50 else record_comment
            
            if (record['start_date'] == start_date_storage and 
                record['end_date'] == end_date_storage and 
                record['location'] == location_str and
                display_comment == comment_display):
                
                # Populate main window with record data
                self.start_date_entry.delete(0, tk.END)
                self.start_date_entry.insert(0, self.format_date_for_entry(record['start_date']))
                
                self.end_date_entry.delete(0, tk.END)
                self.end_date_entry.insert(0, self.format_date_for_entry(record['end_date']))
                
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
    
    def update_year_dropdown(self, year_combo, year_var, filter_vars, records_tree, search_var=None):
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
        self.update_records_display_filtered(records_tree, filter_vars, year_var, search_var)

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
            
            # Convert display dates back to storage format for matching
            start_date_storage = self.parse_display_date_to_storage(values[0])
            end_date_storage = self.parse_display_date_to_storage(values[1])
            # Note: values[2] is days column, values[3] is location, values[4] is comment
            
            # Find and remove the record
            for i, record in enumerate(self.travel_records):
                record_comment = record.get('comment', '')
                display_comment = record_comment[:47] + "..." if len(record_comment) > 50 else record_comment
                
                if (record['start_date'] == start_date_storage and 
                    record['end_date'] == end_date_storage and 
                    record['location'] == values[3] and
                    display_comment == values[4]):
                    del self.travel_records[i]
                    break
            
            self.save_data()
            self.update_calendar_display()
            self.update_location_dropdown()
            
            # Update statistics cards if report window is open
            self.update_statistics_cards()
            
            # Update year dropdown and records display
            if (hasattr(self, '_current_year_combo') and hasattr(self, '_current_year_var') and 
                hasattr(self, '_current_filter_vars') and hasattr(self, '_current_records_tree') and
                hasattr(self, '_current_search_var')):
                self.update_year_dropdown(self._current_year_combo, self._current_year_var, 
                                         self._current_filter_vars, self._current_records_tree, self._current_search_var)
            else:
                # Fallback: just update records display
                self.update_records_display(records_tree)
        
        if self.report_window:
            self.report_window.lift()
            self.report_window.focus_force()
    
    def sort_records(self, records_tree, column):
        """Sort records by the specified column while respecting current filters"""
        # Toggle sort direction if clicking the same column
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Update column heading to show sort direction
        self.update_column_headers(records_tree, column)
        
        # Use the stored filter variables from the report window if available
        if (hasattr(self, '_current_filter_vars') and hasattr(self, '_current_year_var') and 
            hasattr(self, '_current_search_var')):
            # Use the filtered display method which now includes sorting logic
            self.update_records_display_filtered(records_tree, self._current_filter_vars, 
                                                self._current_year_var, self._current_search_var)
        else:
            # Fallback - this shouldn't happen in normal operation
            self.update_records_display(records_tree)
    
    def update_records_display_sorted(self, records_tree, sorted_records):
        """Update the travel records display with sorted records"""
        # Clear existing items
        for item in records_tree.get_children():
            records_tree.delete(item)
        
        # Configure color tags
        self.configure_treeview_tags(records_tree)
        
        # Add sorted records
        for record in sorted_records:
            # Calculate days for the trip
            days = self.calculate_trip_days(record['start_date'], record['end_date'])
            
            # Truncate comment if it's too long for display
            comment = record.get('comment', '')
            if len(comment) > 50:
                comment = comment[:47] + "..."
            
            # Get the appropriate color tag
            color_tag = self.get_record_color_tag(record)
            
            records_tree.insert('', tk.END, values=(
                self.format_date_for_display(record['start_date']),
                self.format_date_for_display(record['end_date']),
                str(days),
                record['location'],
                comment
            ), tags=(color_tag,))
    
    def update_column_headers(self, records_tree, sorted_column):
        """Update column headers to show sort indicators"""
        # Reset all headers first
        records_tree.heading('Start', text='Depart', anchor='w')
        records_tree.heading('End', text='Return', anchor='w')
        records_tree.heading('Days', text='Days', anchor='w')
        records_tree.heading('Location', text='Location', anchor='w')
        records_tree.heading('Comment', text='Notes', anchor='w')
        
        # Add sort indicator to the sorted column
        if sorted_column:
            arrow = ' ↓' if self.sort_reverse else ' ↑'
            if sorted_column == 'Start':
                records_tree.heading('Start', text=f'Depart{arrow}', anchor='w')
            elif sorted_column == 'End':
                records_tree.heading('End', text=f'Return{arrow}', anchor='w')
            elif sorted_column == 'Days':
                records_tree.heading('Days', text=f'Days{arrow}', anchor='w')
            elif sorted_column == 'Location':
                records_tree.heading('Location', text=f'Location{arrow}', anchor='w')
    
    def calculate_travel_statistics(self):
        """Calculate travel statistics for the current year"""
        total_days = 0
        trips_taken = 0  # count trips_taken (only past and current)
        future_trips = 0  # count future trips
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
        
        return {
            'total_days': total_days,
            'trips_taken': trips_taken,
            'future_trips': future_trips,
            'locations_count': len(locations),
            'percentage': percentage,
            'current_year': current_date.year
        }
    
    def update_statistics_cards(self):
        """Update the statistics cards in the report window"""
        if not (self.report_window and self.report_window.winfo_exists() and 
                hasattr(self, '_stats_labels')):
            return
        
        # Recalculate statistics
        stats = self.calculate_travel_statistics()
        
        # Update the labels
        self._stats_labels['trips_taken'].config(text=str(stats['trips_taken']))
        self._stats_labels['future_trips'].config(text=str(stats['future_trips']))
        self._stats_labels['total_days'].config(text=str(stats['total_days']))
        self._stats_labels['percentage'].config(text=f"{stats['percentage']:.1f}%")
        self._stats_labels['locations'].config(text=str(stats['locations_count']))
    
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
        stats = self.calculate_travel_statistics()
        
        # Create modern report window
        report_window = tk.Toplevel(self.root)
        report_window.title("Travel Report")
        report_window.geometry("860x800")  # Increased width to accommodate Days column
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
        
        # Initialize dictionary to store label references
        self._stats_labels = {}
        
        # Trips Taken card 
        trips_card = tk.Frame(stats_frame, bg='#EA3680', relief='solid', bd=0, padx=16, pady=12)
        trips_card.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 4))
        
        tk.Label(trips_card, text="🚀", font=('Segoe UI', 20), 
                bg='#EA3680', fg='white', anchor='center', justify='center').pack()
        self._stats_labels['trips_taken'] = tk.Label(trips_card, text=str(stats['trips_taken']), font=('Segoe UI', 24, 'bold'),
                bg='#EA3680', fg='white')
        self._stats_labels['trips_taken'].pack()
        tk.Label(trips_card, text=f"Trips Taken ({stats['current_year']})", font=('Segoe UI', 10),
                bg='#EA3680', fg='white').pack()
        
        # Future trips card (second position)
        future_card = tk.Frame(stats_frame, bg='#E5B32D', relief='solid', bd=0, padx=16, pady=12)
        future_card.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=4)
        
        tk.Label(future_card, text=" 📅 ", font=('Segoe UI', 20),
                bg='#E5B32D', fg='white', anchor='center').pack()
        self._stats_labels['future_trips'] = tk.Label(future_card, text=str(stats['future_trips']), font=('Segoe UI', 24, 'bold'),
                bg='#E5B32D', fg='white')
        self._stats_labels['future_trips'].pack()
        tk.Label(future_card, text="Upcoming Trips", font=('Segoe UI', 10),
                bg='#E5B32D', fg='white').pack()
        
        # Days traveled card (moved to third position)
        days_card = tk.Frame(stats_frame, bg=self.colors['primary'], relief='solid', bd=0, padx=16, pady=12)
        days_card.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=4)
        
        tk.Label(days_card, text="✈️", font=('Segoe UI', 20), 
                bg=self.colors['primary'], fg='white', anchor='center', justify='center').pack()
        self._stats_labels['total_days'] = tk.Label(days_card, text=str(stats['total_days']), font=('Segoe UI', 24, 'bold'),
                bg=self.colors['primary'], fg='white')
        self._stats_labels['total_days'].pack()
        tk.Label(days_card, text=f"Days Traveled ({stats['current_year']})", font=('Segoe UI', 10),
                bg=self.colors['primary'], fg='white').pack()
        
        # Percentage card (moved to fourth position)
        percent_card = tk.Frame(stats_frame, bg=self.colors['success'], relief='solid', bd=0, padx=16, pady=12)
        percent_card.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=4)
        
        tk.Label(percent_card, text="📈", font=('Segoe UI', 20),
                bg=self.colors['success'], fg='white', anchor='center', justify='center').pack()
        self._stats_labels['percentage'] = tk.Label(percent_card, text=f"{stats['percentage']:.1f}%", font=('Segoe UI', 24, 'bold'),
                bg=self.colors['success'], fg='white')
        self._stats_labels['percentage'].pack()
        tk.Label(percent_card, text="Percentage of Year", font=('Segoe UI', 10),
                bg=self.colors['success'], fg='white').pack()
        
        # Locations card (moved to fifth position)
        locations_card = tk.Frame(stats_frame, bg=self.colors['accent'], relief='solid', bd=0, padx=16, pady=12)
        locations_card.grid(row=0, column=4, sticky=(tk.W, tk.E), padx=(4, 0))
        
        tk.Label(locations_card, text="🌍", font=('Segoe UI', 20),
                bg=self.colors['accent'], fg='white', anchor='center', justify='center').pack()
        self._stats_labels['locations'] = tk.Label(locations_card, text=str(stats['locations_count']), font=('Segoe UI', 24, 'bold'),
                bg=self.colors['accent'], fg='white')
        self._stats_labels['locations'].pack()
        tk.Label(locations_card, text="Locations Visited ", font=('Segoe UI', 10),
                bg=self.colors['accent'], fg='white').pack()
        
        # Filter section
        filter_frame = ttk.LabelFrame(main_container, text="☰ Record Filter", style='Card.TLabelframe')
        filter_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        filter_inner = tk.Frame(filter_frame, bg=self.colors['surface'])
        filter_inner.pack(fill=tk.X, pady=10)
        
        # Create filter variables using user's saved preferences
        filter_vars = {
            'past': tk.BooleanVar(value=self.validation_settings['default_show_past']),
            'current': tk.BooleanVar(value=self.validation_settings['default_show_current']),
            'future': tk.BooleanVar(value=self.validation_settings['default_show_future'])
        }
        
        # Get available years
        available_years = self.get_available_years()
        current_year = datetime.now().year
        
        # Search variable (define early so it's available in toggle button functions)
        search_var = tk.StringVar()
        
        # Search field (first row - above Year and Status)
        search_frame = tk.Frame(filter_inner, bg=self.colors['surface'])
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(search_frame, text="🔍 Search:", 
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(side=tk.LEFT, padx=(0, 15))
        
        # Create a styled frame for the search entry
        search_entry_frame = tk.Frame(search_frame, bg=self.colors['background'], 
                                     relief='solid', bd=2, padx=2, pady=2)
        search_entry_frame.pack(side=tk.LEFT)
        
        # Search entry with enhanced styling
        search_entry = tk.Entry(search_entry_frame, textvariable=search_var,
                               font=('Segoe UI', 11),
                               width=35,
                               bg=self.colors['surface'],
                               fg=self.colors['text'],
                               relief='flat', bd=0,
                               insertbackground=self.colors['primary'])
        search_entry.pack(padx=8, pady=6)
        
        # Add placeholder text behavior
        placeholder_text = "Search locations, dates, or notes..."
        
        def on_search_focus_in(event):
            if search_var.get() == placeholder_text:
                search_var.set("")
                search_entry.config(fg=self.colors['text'])
                search_entry_frame.config(bg='#e0f2fe', bd=2)  # Much lighter blue
        
        def on_search_focus_out(event):
            if not search_var.get().strip():
                search_var.set(placeholder_text)
                search_entry.config(fg=self.colors['text_light'])
            search_entry_frame.config(bg=self.colors['background'], bd=2)
        
        def on_search_change(*args):
            # Don't filter if showing placeholder text
            if search_var.get() == placeholder_text:
                return
            # Filter records in real time
            self.update_records_display_filtered(records_tree, filter_vars, year_var, search_var)
        
        # Set initial placeholder
        search_var.set(placeholder_text)
        search_entry.config(fg=self.colors['text_light'])
        
        # Bind events
        search_entry.bind('<FocusIn>', on_search_focus_in)
        search_entry.bind('<FocusOut>', on_search_focus_out)
        search_var.trace('w', on_search_change)
        
        # Year and Status filters (second row - below Search)
        year_status_frame = tk.Frame(filter_inner, bg=self.colors['surface'])
        year_status_frame.pack(fill=tk.X)
        
        # Status toggle buttons (first on the row)
        tk.Label(year_status_frame, text="📊 Status Toggle:", 
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(side=tk.LEFT, padx=(0, 10))
        
        # Create toggle buttons
        toggle_buttons = {}
        
        def create_toggle_button(parent, text, var_name, bg_color, text_color):
            """Create a modern toggle button"""
            def toggle_state():
                # Toggle the variable
                filter_vars[var_name].set(not filter_vars[var_name].get())
                # Update button appearance
                update_button_appearance()
                # Update records display
                self.update_records_display_filtered(records_tree, filter_vars, year_var, search_var)
            
            # Create the button
            btn = tk.Button(parent, text=text,
                          font=('Segoe UI', 10, 'bold'),
                          relief='flat', bd=0, padx=16, pady=8,
                          cursor='hand2',
                          command=toggle_state)
            
            # Store button reference and colors
            toggle_buttons[var_name] = {
                'button': btn,
                'active_bg': bg_color,
                'active_fg': text_color,
                'inactive_bg': '#e2e8f0',  # Light gray
                'inactive_fg': '#64748b'   # Darker gray text
            }
            
            return btn
        
        def update_button_appearance():
            """Update the appearance of all toggle buttons based on their state"""
            for var_name, btn_info in toggle_buttons.items():
                btn = btn_info['button']
                is_active = filter_vars[var_name].get()
                
                if is_active:
                    # Active state - colored
                    btn.config(
                        bg=btn_info['active_bg'],
                        fg=btn_info['active_fg'],
                        activebackground=btn_info['active_bg'],
                        activeforeground=btn_info['active_fg']
                    )
                else:
                    # Inactive state - gray
                    btn.config(
                        bg=btn_info['inactive_bg'],
                        fg=btn_info['inactive_fg'],
                        activebackground='#cbd5e1',
                        activeforeground=btn_info['inactive_fg']
                    )
        
        # Create the toggle buttons
        past_btn = create_toggle_button(year_status_frame, "Past", "past", "#dbeafe", "#1e40af")
        past_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        current_btn = create_toggle_button(year_status_frame, "Current", "current", "#dcfce7", "#15803d")
        current_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        future_btn = create_toggle_button(year_status_frame, "Future", "future", "#fef3c7", "#d97706")
        future_btn.pack(side=tk.LEFT, padx=(0, 30))
        
        # Set initial button appearances
        update_button_appearance()
        
        # Year filter (second on the row, to the right of Status)
        tk.Label(year_status_frame, text="📅 Year:", 
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']).pack(side=tk.LEFT, padx=(0, 10))
        
        year_var = tk.StringVar()
        year_combo = ttk.Combobox(year_status_frame, textvariable=year_var, 
                                 style='Modern.TCombobox', 
                                 font=('Segoe UI', 10),
                                 width=12, state="readonly")
        
        # Populate year dropdown
        year_options = ["All Years"] + [str(year) for year in available_years]
        year_combo['values'] = year_options
        
        # Set default based on user preference
        default_year = self.get_default_year_selection(available_years)
        year_var.set(default_year)
        
        year_combo.pack(side=tk.LEFT)
        
        # Store references for updating when records are modified
        self._current_year_combo = year_combo
        self._current_year_var = year_var
        self._current_filter_vars = filter_vars
        
        # Bind year selection change
        def on_year_change(event):
            # Check if selected year is in the past/future and automatically enable appropriate toggle
            selected_year_str = year_var.get()
            current_year = datetime.now().year
            
            if selected_year_str != "All Years":
                try:
                    selected_year = int(selected_year_str)
                    if selected_year < current_year:
                        # Automatically enable Past toggle for previous years
                        if not filter_vars['past'].get():
                            filter_vars['past'].set(True)
                            update_button_appearance()
                    elif selected_year > current_year:
                        # Automatically enable Future toggle for future years
                        if not filter_vars['future'].get():
                            filter_vars['future'].set(True)
                            update_button_appearance()
                except ValueError:
                    pass
            
            # Update the records display
            self.update_records_display_filtered(records_tree, filter_vars, year_var, search_var)
        
        year_combo.bind('<<ComboboxSelected>>', on_year_change)
        
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
        
        records_tree = ttk.Treeview(tree_frame, columns=('Start', 'End', 'Days', 'Location', 'Comment'), 
                                   show='headings', height=15)
        
        # Configure headers with sorting functionality
        records_tree.heading('Start', text='Depart', anchor='w',
                           command=lambda: self.sort_records(records_tree, 'Start'))
        records_tree.heading('End', text='Return', anchor='w',
                           command=lambda: self.sort_records(records_tree, 'End'))
        records_tree.heading('Days', text='Days', anchor='w',
                           command=lambda: self.sort_records(records_tree, 'Days'))
        records_tree.heading('Location', text='Location', anchor='w',
                           command=lambda: self.sort_records(records_tree, 'Location'))
        records_tree.heading('Comment', text='Notes', anchor='w')
        
        # Set column widths (adjusted for the new Days column)
        records_tree.column('Start', width=100)
        records_tree.column('End', width=100)
        records_tree.column('Days', width=60)
        records_tree.column('Location', width=180)
        records_tree.column('Comment', width=400)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=records_tree.yview)
        records_tree.configure(yscrollcommand=scrollbar.set)
        
        records_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Store reference to records tree for updates
        self._current_records_tree = records_tree
        
        # Store search variable reference
        self._current_search_var = search_var
        
        # Initial records display with filtering
        self.update_records_display_filtered(records_tree, filter_vars, year_var, search_var)
        
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
        
        export_btn = tk.Button(buttons_frame, text="📤 Export",
                              bg=self.colors['accent'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', bd=0, padx=12, pady=8,
                              activebackground='#0891b2', activeforeground='white',
                              command=self.export_travel_records)
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        analytics_btn = tk.Button(buttons_frame, text="📊 Analytics Dashboard",
                                 bg='#8b5cf6', fg='white',  # Purple color
                                 font=('Segoe UI', 10, 'bold'),
                                 relief='flat', bd=0, padx=12, pady=8,
                                 activebackground='#7c3aed', activeforeground='white',
                                 command=self.show_analytics_dashboard)
        analytics_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(buttons_frame, text="✖️ Close",
                             bg=self.colors['secondary'], fg='white',
                             font=('Segoe UI', 10, 'bold'),
                             relief='flat', bd=0, padx=12, pady=8,
                             activebackground='#475569', activeforeground='white',
                             command=self._on_report_window_close)
        close_btn.pack(side=tk.LEFT)

    def get_available_past_years(self):
        """Get list of years with past travel data"""
        current_year = datetime.now().year
        years = set()
        
        for record in self.travel_records:
            try:
                start_date = datetime.strptime(record['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(record['end_date'], '%Y-%m-%d')
                
                # Include years for trips that have started (past or current)
                if start_date <= datetime.now():
                    years.add(start_date.year)
                    years.add(end_date.year)
                    # Add any years in between for multi-year trips
                    for year in range(start_date.year, min(end_date.year, current_year) + 1):
                        years.add(year)
            except ValueError:
                continue
        
        # Only include years up to current year
        past_years = [year for year in years if year <= current_year]
        return sorted(past_years, reverse=True)  # Most recent first
    
    def get_available_future_years(self):
        """Get list of years with future travel data"""
        current_year = datetime.now().year
        years = set()
        
        for record in self.travel_records:
            try:
                start_date = datetime.strptime(record['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(record['end_date'], '%Y-%m-%d')
                
                # Include years for trips that start in the future or overlap with future
                if end_date >= datetime.now():
                    years.add(start_date.year)
                    years.add(end_date.year)
                    # Add any years in between for multi-year trips
                    for year in range(max(start_date.year, current_year), end_date.year + 1):
                        years.add(year)
            except ValueError:
                continue
        
        # Only include years from current year forward
        future_years = [year for year in years if year >= current_year]
        return sorted(future_years)  # Earliest first
    
    def calculate_year_specific_analytics(self, selected_past_year, selected_future_year):
        """Calculate analytics for specific years"""
        current_date = datetime.now()
        current_year = current_date.year
        
        # Initialize data structures
        analytics = {
            'past': {
                'trips': 0,
                'days': 0,
                'locations': set(),
                'weekend_days': 0,
                'trip_lengths': [],
                'months': {},
                'selected_year': selected_past_year
            },
            'future': {
                'trips': 0,
                'days': 0,
                'locations': set(),
                'weekend_days': 0,
                'trip_lengths': [],
                'months': {},
                'selected_year': selected_future_year
            },
            'overall': {
                'total_records': len(self.travel_records),
                'earliest_trip': None,
                'latest_trip': None,
                'most_visited_location': '',
                'location_counts': {}
            }
        }
        
        # Calculate year boundaries
        past_year_start = datetime(selected_past_year, 1, 1)
        past_year_end = datetime(selected_past_year, 12, 31)
        future_year_start = datetime(selected_future_year, 1, 1)
        future_year_end = datetime(selected_future_year, 12, 31)
        
        # Determine how much of the selected past year has elapsed
        if selected_past_year == current_year:
            days_elapsed_in_past_year = (current_date - past_year_start).days + 1
        else:
            days_elapsed_in_past_year = 365 + (1 if selected_past_year % 4 == 0 and (selected_past_year % 100 != 0 or selected_past_year % 400 == 0) else 0)
        
        for record in self.travel_records:
            try:
                start_date = datetime.strptime(record['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(record['end_date'], '%Y-%m-%d')
                trip_length = (end_date - start_date).days + 1
                location = record['location']
                
                # Update overall statistics (unchanged)
                if analytics['overall']['earliest_trip'] is None or start_date < analytics['overall']['earliest_trip']:
                    analytics['overall']['earliest_trip'] = start_date
                if analytics['overall']['latest_trip'] is None or end_date > analytics['overall']['latest_trip']:
                    analytics['overall']['latest_trip'] = end_date
                
                analytics['overall']['location_counts'][location] = analytics['overall']['location_counts'].get(location, 0) + 1
                
                # Calculate travel days per year for most traveled year
                if 'year_travel_days' not in analytics['overall']:
                    analytics['overall']['year_travel_days'] = {}
                
                # Count days for each year the trip overlaps
                for year in range(start_date.year, end_date.year + 1):
                    year_start_date = datetime(year, 1, 1)
                    year_end_date = datetime(year, 12, 31)
                    
                    # Calculate overlap with this year
                    overlap_start = max(start_date, year_start_date)
                    overlap_end = min(end_date, year_end_date)
                    
                    if overlap_start <= overlap_end:
                        days_in_year = (overlap_end - overlap_start).days + 1
                        analytics['overall']['year_travel_days'][year] = analytics['overall']['year_travel_days'].get(year, 0) + days_in_year
                
                # Check if trip overlaps with selected past year and has started
                past_year_overlap = (start_date <= past_year_end and end_date >= past_year_start and start_date <= current_date)
                
                # Check if trip overlaps with selected future year and hasn't ended yet
                future_year_overlap = (start_date <= future_year_end and end_date >= future_year_start and end_date >= current_date)
                
                if past_year_overlap:
                    analytics['past']['trips'] += 1
                    analytics['past']['locations'].add(location)
                    analytics['past']['trip_lengths'].append(trip_length)
                    
                    # Calculate days within the selected past year that have elapsed
                    overlap_start = max(start_date, past_year_start)
                    overlap_end = min(end_date, past_year_end, current_date)
                    
                    if overlap_start <= overlap_end:
                        days_in_past_year = (overlap_end - overlap_start).days + 1
                        analytics['past']['days'] += days_in_past_year
                        
                        # Count weekend days
                        current_day = overlap_start
                        while current_day <= overlap_end:
                            if current_day.weekday() in [5, 6]:
                                analytics['past']['weekend_days'] += 1
                            current_day += timedelta(days=1)
                    
                    # Count months
                    month_name = start_date.strftime('%B')
                    analytics['past']['months'][month_name] = analytics['past']['months'].get(month_name, 0) + 1
                
                if future_year_overlap:
                    analytics['future']['trips'] += 1
                    analytics['future']['locations'].add(location)
                    analytics['future']['trip_lengths'].append(trip_length)
                    
                    # Calculate days within the selected future year
                    overlap_start = max(start_date, future_year_start)
                    overlap_end = min(end_date, future_year_end)
                    
                    if overlap_start <= overlap_end:
                        days_in_future_year = (overlap_end - overlap_start).days + 1
                        analytics['future']['days'] += days_in_future_year
                        
                        # Count weekend days
                        current_day = overlap_start
                        while current_day <= overlap_end:
                            if current_day.weekday() in [5, 6]:
                                analytics['future']['weekend_days'] += 1
                            current_day += timedelta(days=1)
                    
                    # Count months
                    month_name = start_date.strftime('%B')
                    analytics['future']['months'][month_name] = analytics['future']['months'].get(month_name, 0) + 1
                    
            except ValueError:
                continue
        
        # Calculate derived statistics
        for category in ['past', 'future']:
            cat_data = analytics[category]
            cat_data['locations_count'] = len(cat_data['locations'])
            cat_data['avg_trip_length'] = sum(cat_data['trip_lengths']) / len(cat_data['trip_lengths']) if cat_data['trip_lengths'] else 0
            cat_data['longest_trip'] = max(cat_data['trip_lengths']) if cat_data['trip_lengths'] else 0
            cat_data['shortest_trip'] = min(cat_data['trip_lengths']) if cat_data['trip_lengths'] else 0
        
        # Calculate percentage for past year
        analytics['past']['percentage_of_year'] = (analytics['past']['days'] / days_elapsed_in_past_year) * 100 if days_elapsed_in_past_year > 0 else 0
        
        # Most visited location (overall)
        if analytics['overall']['location_counts']:
            analytics['overall']['most_visited_location'] = max(
                analytics['overall']['location_counts'].items(), 
                key=lambda x: x[1]
            )[0]
        
        # Most traveled year
        if analytics['overall'].get('year_travel_days'):
            analytics['overall']['most_traveled_year'] = max(
                analytics['overall']['year_travel_days'].items(),
                key=lambda x: x[1]
            )[0]
        else:
            analytics['overall']['most_traveled_year'] = current_year
        
        return analytics
        """Calculate comprehensive travel analytics broken down by past and future"""
        current_date = datetime.now()
        current_year = current_date.year
        year_start = datetime(current_year, 1, 1)
        days_in_year_so_far = (current_date - year_start).days + 1
        
        # Initialize data structures
        analytics = {
            'past': {
                'trips': 0,
                'days': 0,
                'locations': set(),
                'weekend_days': 0,
                'trip_lengths': [],
                'months': {}
            },
            'future': {
                'trips': 0,
                'days': 0,
                'locations': set(),
                'weekend_days': 0,
                'trip_lengths': [],
                'months': {}
            },
            'overall': {
                'total_records': len(self.travel_records),
                'earliest_trip': None,
                'latest_trip': None,
                'most_visited_location': '',
                'location_counts': {}
            }
        }
        
        for record in self.travel_records:
            try:
                start_date = datetime.strptime(record['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(record['end_date'], '%Y-%m-%d')
                trip_length = (end_date - start_date).days + 1
                location = record['location']
                
                # Update overall statistics
                if analytics['overall']['earliest_trip'] is None or start_date < analytics['overall']['earliest_trip']:
                    analytics['overall']['earliest_trip'] = start_date
                if analytics['overall']['latest_trip'] is None or end_date > analytics['overall']['latest_trip']:
                    analytics['overall']['latest_trip'] = end_date
                
                # Count location visits
                analytics['overall']['location_counts'][location] = analytics['overall']['location_counts'].get(location, 0) + 1
                
                # Calculate travel days per year for most traveled year
                if 'year_travel_days' not in analytics['overall']:
                    analytics['overall']['year_travel_days'] = {}
                
                # Count days for each year the trip overlaps
                for year in range(start_date.year, end_date.year + 1):
                    year_start = datetime(year, 1, 1)
                    year_end = datetime(year, 12, 31)
                    
                    # Calculate overlap with this year
                    overlap_start = max(start_date, year_start)
                    overlap_end = min(end_date, year_end)
                    
                    if overlap_start <= overlap_end:
                        days_in_year = (overlap_end - overlap_start).days + 1
                        analytics['overall']['year_travel_days'][year] = analytics['overall']['year_travel_days'].get(year, 0) + days_in_year
                
                # Rest of the existing logic...
                # Determine trip category (past includes current trips)
                if start_date > current_date:
                    category = 'future'
                else:
                    category = 'past'  # Includes trips that have started (past and current)
                
                # Update category statistics
                analytics[category]['trips'] += 1
                analytics[category]['locations'].add(location)
                analytics[category]['trip_lengths'].append(trip_length)
                
                # Count days (for current year only for past trips, all days for future)
                if category == 'past' and start_date.year <= current_year and end_date.year >= current_year:
                    count_start = max(start_date, year_start)
                    count_end = min(end_date, current_date)
                    if count_start <= count_end:
                        days = (count_end - count_start).days + 1
                        analytics[category]['days'] += days
                        
                        # Count weekend days
                        current_day = count_start
                        while current_day <= count_end:
                            if current_day.weekday() in [5, 6]:  # Saturday=5, Sunday=6
                                analytics[category]['weekend_days'] += 1
                            current_day += timedelta(days=1)
                elif category == 'future':
                    # For future trips, count all days
                    analytics[category]['days'] += trip_length
                    
                    # Count weekend days for future trips
                    current_day = start_date
                    while current_day <= end_date:
                        if current_day.weekday() in [5, 6]:  # Saturday=5, Sunday=6
                            analytics[category]['weekend_days'] += 1
                        current_day += timedelta(days=1)
                
                # Count months for all categories
                trip_months = set()
                current_month = start_date.replace(day=1)
                end_month = end_date.replace(day=1)
                while current_month <= end_month:
                    month_name = current_month.strftime('%B')
                    analytics[category]['months'][month_name] = analytics[category]['months'].get(month_name, 0) + 1
                    current_month = (current_month + timedelta(days=32)).replace(day=1)
                    
            except ValueError:
                continue
        
        # Calculate derived statistics
        for category in ['past', 'future']:
            cat_data = analytics[category]
            cat_data['locations_count'] = len(cat_data['locations'])
            cat_data['avg_trip_length'] = sum(cat_data['trip_lengths']) / len(cat_data['trip_lengths']) if cat_data['trip_lengths'] else 0
            cat_data['longest_trip'] = max(cat_data['trip_lengths']) if cat_data['trip_lengths'] else 0
            cat_data['shortest_trip'] = min(cat_data['trip_lengths']) if cat_data['trip_lengths'] else 0
            
            # Only calculate percentage for past trips
            if category == 'past':
                cat_data['percentage_of_year'] = (cat_data['days'] / days_in_year_so_far) * 100 if days_in_year_so_far > 0 else 0
        
        # Most visited location
        if analytics['overall']['location_counts']:
            analytics['overall']['most_visited_location'] = max(
                analytics['overall']['location_counts'].items(), 
                key=lambda x: x[1]
            )[0]
        
        # Most traveled year
        if analytics['overall'].get('year_travel_days'):
            analytics['overall']['most_traveled_year'] = max(
                analytics['overall']['year_travel_days'].items(),
                key=lambda x: x[1]
            )[0]
        else:
            analytics['overall']['most_traveled_year'] = current_year
        
        return analytics
    
    def show_analytics_dashboard(self):
        """Show comprehensive analytics dashboard in a new window"""
        if not self.travel_records:
            messagebox.showinfo("Analytics", "📊 No travel records found for analytics.")
            return
        
        # Get available years
        past_years = self.get_available_past_years()
        future_years = self.get_available_future_years()
        
        if not past_years and not future_years:
            messagebox.showinfo("Analytics", "📊 No travel records found for analytics.")
            return
        
        # Create analytics window
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("📊 Travel Analytics Dashboard")
        analytics_window.geometry("800x780")  # Reduced from 1200x800
        analytics_window.configure(bg=self.colors['background'])
        
        # Main container with scrollable content
        main_container = tk.Frame(analytics_window, bg=self.colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # Reduced from 30, 30
        
        # Title
        title_label = tk.Label(main_container, 
                              text="📊 Comprehensive Travel Analytics", 
                              font=('Segoe UI', 16, 'bold'),  # Reduced from 18
                              fg=self.colors['primary'],
                              bg=self.colors['background'])
        title_label.pack(pady=(0, 20))  # Reduced from 30
        
        # Year selection variables
        current_year = datetime.now().year
        past_year_var = tk.StringVar(value=str(current_year) if current_year in past_years else str(past_years[0]) if past_years else str(current_year))
        future_year_var = tk.StringVar(value=str(current_year) if current_year in future_years else str(future_years[0]) if future_years else str(current_year))
        
        # Function to update analytics when year selection changes
        def update_analytics():
            try:
                selected_past_year = int(past_year_var.get())
                selected_future_year = int(future_year_var.get())
                analytics = self.calculate_year_specific_analytics(selected_past_year, selected_future_year)
                
                # Update the sections
                self.update_analytics_section(past_section_content, analytics['past'], '#dbeafe', '#1e40af')
                self.update_analytics_section(future_section_content, analytics['future'], '#fef3c7', '#d97706')
                
            except ValueError:
                pass
        
        # Create sections for Past and Future
        sections_frame = tk.Frame(main_container, bg=self.colors['background'])
        sections_frame.pack(fill=tk.BOTH, expand=True)
        sections_frame.columnconfigure(0, weight=1)
        sections_frame.columnconfigure(1, weight=1)
        
        # Past Section with year dropdown
        past_section_frame = ttk.LabelFrame(sections_frame, text="Past Travel", style='Card.TLabelframe')
        past_section_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Past year selection
        past_year_frame = tk.Frame(past_section_frame, bg=self.colors['surface'])
        past_year_frame.pack(fill=tk.X, padx=15, pady=(10, 5))  # Reduced padding
        
        tk.Label(past_year_frame, text="Year:", font=('Segoe UI', 10, 'bold'),  # Reduced font
                fg=self.colors['text'], bg=self.colors['surface']).pack(side=tk.LEFT)
        
        past_year_combo = ttk.Combobox(past_year_frame, textvariable=past_year_var,
                                      values=[str(year) for year in past_years] if past_years else [str(current_year)],
                                      state="readonly", width=8, font=('Segoe UI', 9))  # Reduced font
        past_year_combo.pack(side=tk.LEFT, padx=(10, 0))
        past_year_combo.bind('<<ComboboxSelected>>', lambda e: update_analytics())
        
        past_section_content = tk.Frame(past_section_frame, bg=self.colors['surface'])
        past_section_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))  # Reduced padding
        
        # Future Section with year dropdown
        future_section_frame = ttk.LabelFrame(sections_frame, text="Future Travel", style='Card.TLabelframe')
        future_section_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Future year selection
        future_year_frame = tk.Frame(future_section_frame, bg=self.colors['surface'])
        future_year_frame.pack(fill=tk.X, padx=15, pady=(10, 5))  # Reduced padding
        
        tk.Label(future_year_frame, text="Year:", font=('Segoe UI', 10, 'bold'),  # Reduced font
                fg=self.colors['text'], bg=self.colors['surface']).pack(side=tk.LEFT)
        
        future_year_combo = ttk.Combobox(future_year_frame, textvariable=future_year_var,
                                        values=[str(year) for year in future_years] if future_years else [str(current_year)],
                                        state="readonly", width=8, font=('Segoe UI', 9))  # Reduced font
        future_year_combo.pack(side=tk.LEFT, padx=(10, 0))
        future_year_combo.bind('<<ComboboxSelected>>', lambda e: update_analytics())
        
        future_section_content = tk.Frame(future_section_frame, bg=self.colors['surface'])
        future_section_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))  # Reduced padding
        
        # Calculate initial analytics
        initial_past_year = int(past_year_var.get())
        initial_future_year = int(future_year_var.get())
        analytics = self.calculate_year_specific_analytics(initial_past_year, initial_future_year)
        
        # Populate initial data
        self.update_analytics_section(past_section_content, analytics['past'], '#dbeafe', '#1e40af')
        self.update_analytics_section(future_section_content, analytics['future'], '#fef3c7', '#d97706')
        
        # Overall Statistics Section (unchanged)
        overall_frame = ttk.LabelFrame(main_container, text="🌍 Overall Statistics", style='Card.TLabelframe')
        overall_frame.pack(fill=tk.X, pady=(20, 0))  # Reduced from 30
        
        overall_content = tk.Frame(overall_frame, bg=self.colors['surface'])
        overall_content.pack(fill=tk.X, padx=15, pady=15)  # Reduced from 20, 20
        
        # Overall stats cards
        overall_stats_frame = tk.Frame(overall_content, bg=self.colors['surface'])
        overall_stats_frame.pack(fill=tk.X)
        overall_stats_frame.columnconfigure(0, weight=1)
        overall_stats_frame.columnconfigure(1, weight=1)
        overall_stats_frame.columnconfigure(2, weight=1)
        overall_stats_frame.columnconfigure(3, weight=1)
        
        # Total Records
        total_card = tk.Frame(overall_stats_frame, bg='#6366f1', relief='solid', bd=0, padx=16, pady=12)
        total_card.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        tk.Label(total_card, text="📋", font=('Segoe UI', 16), 
                bg='#6366f1', fg='white').pack()
        tk.Label(total_card, text=str(analytics['overall']['total_records']), 
                font=('Segoe UI', 20, 'bold'), bg='#6366f1', fg='white').pack()
        tk.Label(total_card, text="Total Trips", font=('Segoe UI', 9),
                bg='#6366f1', fg='white').pack()
        
        # Most Traveled Year
        year_card = tk.Frame(overall_stats_frame, bg='#ec4899', relief='solid', bd=0, padx=16, pady=12)
        year_card.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        tk.Label(year_card, text="🏆", font=('Segoe UI', 16), 
                bg='#ec4899', fg='white').pack()
        tk.Label(year_card, text=str(analytics['overall']['most_traveled_year']), 
                font=('Segoe UI', 20, 'bold'), bg='#ec4899', fg='white').pack()
        tk.Label(year_card, text="Most Traveled Year", font=('Segoe UI', 9),
                bg='#ec4899', fg='white').pack()
        
        # Travel Span
        span_card = tk.Frame(overall_stats_frame, bg='#10b981', relief='solid', bd=0, padx=16, pady=12)
        span_card.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=5)
        
        tk.Label(span_card, text="📅", font=('Segoe UI', 16), 
                bg='#10b981', fg='white').pack()
        
        if analytics['overall']['earliest_trip'] and analytics['overall']['latest_trip']:
            span_years = analytics['overall']['latest_trip'].year - analytics['overall']['earliest_trip'].year + 1
            tk.Label(span_card, text=f"{span_years}", 
                    font=('Segoe UI', 20, 'bold'), bg='#10b981', fg='white').pack()
            tk.Label(span_card, text="Years of Travel", font=('Segoe UI', 9),
                    bg='#10b981', fg='white').pack()
        else:
            tk.Label(span_card, text="0", 
                    font=('Segoe UI', 20, 'bold'), bg='#10b981', fg='white').pack()
            tk.Label(span_card, text="Years of Travel", font=('Segoe UI', 9),
                    bg='#10b981', fg='white').pack()
        
        # Unique Locations
        unique_card = tk.Frame(overall_stats_frame, bg='#f59e0b', relief='solid', bd=0, padx=16, pady=12)
        unique_card.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(5, 0))
        
        tk.Label(unique_card, text="🌟", font=('Segoe UI', 16), 
                bg='#f59e0b', fg='white').pack()
        all_locations = set()
        for category in ['past', 'future']:
            all_locations.update(analytics[category]['locations'])
        tk.Label(unique_card, text=str(len(all_locations)), 
                font=('Segoe UI', 20, 'bold'), bg='#f59e0b', fg='white').pack()
        tk.Label(unique_card, text="Unique Locations", font=('Segoe UI', 9),
                bg='#f59e0b', fg='white').pack()
        
        # Close button
        close_frame = tk.Frame(main_container, bg=self.colors['background'])
        close_frame.pack(pady=(20, 0))  # Reduced from 30
        
        close_btn = tk.Button(close_frame, text="✖️ Close Dashboard",
                             bg=self.colors['secondary'], fg='white',
                             font=('Segoe UI', 11, 'bold'),  # Reduced from 12
                             relief='flat', bd=0, padx=25, pady=10,  # Reduced padding
                             activebackground='#475569', activeforeground='white',
                             command=analytics_window.destroy)
        close_btn.pack()
    
    def update_analytics_section(self, content_frame, data, bg_color, text_color):
        """Update an analytics section with new data using compact grid layout"""
        # Clear existing content
        for widget in content_frame.winfo_children():
            widget.destroy()
        
        # Metrics cards in a 2x3 grid for more compact display
        metrics = [
            ("🚀", "Trips", data['trips']),
            ("📅", "Days", data['days']),
            ("🌍", "Locations", data['locations_count']),
            ("🎯", "Avg Length", f"{data['avg_trip_length']:.1f}" if data['avg_trip_length'] > 0 else "0"),
            ("⏰", "Weekend Days", data['weekend_days']),
        ]
        
        # Add percentage for past only
        if data.get('percentage_of_year', 0) > 0:
            metrics.append(("📊", f"Percent of {data['selected_year']}", f"{data['percentage_of_year']:.1f}%"))
        
        # Create grid container
        metrics_grid = tk.Frame(content_frame, bg=self.colors['surface'])
        metrics_grid.pack(fill=tk.X, pady=(0, 10))
        
        # Configure grid columns to be equal width
        metrics_grid.columnconfigure(0, weight=1)
        metrics_grid.columnconfigure(1, weight=1)
        
        # Place metrics in 2-column grid
        for i, (icon, label, value) in enumerate(metrics):
            row = i // 2
            col = i % 2
            
            metric_card = tk.Frame(metrics_grid, bg=bg_color, relief='solid', bd=0, padx=8, pady=6)  # Reduced padding
            metric_card.grid(row=row, column=col, sticky=(tk.W, tk.E), padx=2, pady=2)
            
            # Icon and value on same line
            info_frame = tk.Frame(metric_card, bg=bg_color)
            info_frame.pack(fill=tk.X)
            
            tk.Label(info_frame, text=icon, font=('Segoe UI', 12), 
                    bg=bg_color, fg=text_color).pack(side=tk.LEFT)
            
            tk.Label(info_frame, text=str(value), font=('Segoe UI', 12, 'bold'), 
                    bg=bg_color, fg=text_color).pack(side=tk.RIGHT)
            
            tk.Label(metric_card, text=label, font=('Segoe UI', 9),  # Reduced font
                    bg=bg_color, fg=text_color).pack()
        
        # Trip extremes (if any trips exist) - more compact
        if data['trip_lengths']:
            extremes_frame = tk.Frame(content_frame, bg=self.colors['surface'])
            extremes_frame.pack(fill=tk.X, pady=(5, 0))  # Reduced padding
            
            tk.Label(extremes_frame, text="Trip Extremes", font=('Segoe UI', 10, 'bold'),  # Reduced font
                    fg=self.colors['text'], bg=self.colors['surface']).pack()
            
            # Put extremes in a horizontal layout to save space
            extremes_grid = tk.Frame(extremes_frame, bg=self.colors['surface'])
            extremes_grid.pack(fill=tk.X, pady=(2, 0))
            extremes_grid.columnconfigure(0, weight=1)
            extremes_grid.columnconfigure(1, weight=1)
            
            longest_card = tk.Frame(extremes_grid, bg='#a3a3a3', relief='solid', bd=0, padx=6, pady=3)  # Reduced padding
            longest_card.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 1))
            tk.Label(longest_card, text=f"Longest: {data['longest_trip']} days", 
                    font=('Segoe UI', 8), bg='#a3a3a3', fg='white').pack()  # Reduced font
            
            shortest_card = tk.Frame(extremes_grid, bg='#71717a', relief='solid', bd=0, padx=6, pady=3)  # Reduced padding
            shortest_card.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(1, 0))
            tk.Label(shortest_card, text=f"Shortest: {data['shortest_trip']} days", 
                    font=('Segoe UI', 8), bg='#71717a', fg='white').pack()  # Reduced font

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
        if hasattr(self, '_current_search_var'):
            delattr(self, '_current_search_var')
        if hasattr(self, '_stats_labels'):
            delattr(self, '_stats_labels')

def main():
    root = tk.Tk()
    app = ModernTravelCalendar(root)
    root.mainloop()

if __name__ == "__main__":
    main()