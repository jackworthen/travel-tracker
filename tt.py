import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import calendar
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class TravelCalendar:
    def __init__(self, root):
        self.root = root
        self.root.title("Travel Calendar Tracker")
        self.root.geometry("600x460")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.data_file = "travel_data.json"
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
        
        # Current display
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        
        self.setup_ui()
        self.update_calendar_display()
        self.update_location_dropdown()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Travel Calendar Tracker", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel for controls
        control_frame = ttk.LabelFrame(main_frame, text="Travel Entry", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Manual date entry
        date_entry_frame = ttk.Frame(control_frame)
        date_entry_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(date_entry_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W)
        self.start_date_entry = ttk.Entry(date_entry_frame, width=15)
        self.start_date_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(date_entry_frame, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W)
        self.end_date_entry = ttk.Entry(date_entry_frame, width=15)
        self.end_date_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Clear button for dates
        ttk.Button(date_entry_frame, text="Clear", command=self.clear_dates).grid(row=4, column=0, pady=5)
        
        # Location and comment
        ttk.Label(control_frame, text="Location (City, State):").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.location_entry = ttk.Combobox(control_frame, width=27)
        self.location_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(control_frame, text="Comment:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        self.comment_text = tk.Text(control_frame, height=4, width=30)
        self.comment_text.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.add_travel).grid(row=0, column=0, padx=2)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).grid(row=0, column=1, padx=2)
        ttk.Button(button_frame, text="View Report", command=self.show_report).grid(row=0, column=2, padx=2)
        
        # Calendar frame
        calendar_frame = ttk.LabelFrame(main_frame, text="Calendar", padding="10")
        calendar_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        calendar_frame.columnconfigure(0, weight=1)
        
        # Month navigation
        nav_frame = ttk.Frame(calendar_frame)
        nav_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        nav_frame.columnconfigure(1, weight=1)
        
        ttk.Button(nav_frame, text="<", command=self.prev_month).grid(row=0, column=0)
        self.month_label = ttk.Label(nav_frame, font=('Arial', 12, 'bold'))
        self.month_label.grid(row=0, column=1)
        ttk.Button(nav_frame, text=">", command=self.next_month).grid(row=0, column=2)
        
        # Calendar grid
        self.calendar_frame = ttk.Frame(calendar_frame)
        self.calendar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def update_location_dropdown(self):
        """Update the location combobox with unique locations from travel records"""
        # Get unique locations and sort them alphabetically
        locations = set()
        for record in self.travel_records:
            if record['location'].strip():
                locations.add(record['location'])
        
        sorted_locations = sorted(list(locations))
        self.location_entry['values'] = sorted_locations
    
    def load_data(self) -> List[Dict]:
        """Load travel data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(self):
        """Save travel data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.travel_records, f, indent=2)
    
    def update_calendar_display(self):
        """Update the calendar display for current month/year"""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Update month label
        month_name = calendar.month_name[self.current_month]
        self.month_label.config(text=f"{month_name} {self.current_year}")
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            label = ttk.Label(self.calendar_frame, text=day, font=('Arial', 9, 'bold'))
            label.grid(row=0, column=i, padx=1, pady=1)
        
        # Get calendar data
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # Create date buttons
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell for days not in current month
                    label = ttk.Label(self.calendar_frame, text="")
                    label.grid(row=week_num + 1, column=day_num, padx=1, pady=1)
                else:
                    date_obj = datetime(self.current_year, self.current_month, day)
                    
                    # Check if this date has travel
                    has_travel = self.date_has_travel(date_obj)
                    is_selected = self.date_is_selected(date_obj)
                    
                    # Style the button
                    style = 'Travel.TButton' if has_travel else 'Normal.TButton'
                    if is_selected:
                        style = 'Selected.TButton'
                    
                    btn = ttk.Button(self.calendar_frame, text=str(day), width=4,
                                   command=lambda d=day: self.date_clicked(d))
                    btn.grid(row=week_num + 1, column=day_num, padx=1, pady=1)
                    
                    # Configure button styles
                    if has_travel:
                        btn.configure(style='Travel.TButton')
                    if is_selected:
                        btn.configure(style='Selected.TButton')
        
        # Configure styles
        style = ttk.Style()
        style.configure('Travel.TButton', background='lightblue')
        style.configure('Selected.TButton', background='orange')
        style.configure('Normal.TButton', background='white')
    
    def date_has_travel(self, date_obj: datetime) -> bool:
        """Check if a date has travel records"""
        date_str = date_obj.strftime('%Y-%m-%d')
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
    
    def clear_selection(self):
        """Clear date selection"""
        self.selected_start_date = None
        self.selected_end_date = None
        self.selecting_range = False
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
        """Add a new travel record or update existing one if in edit mode"""
        # Try to get dates from entry fields first
        start_date_str = self.start_date_entry.get().strip()
        end_date_str = self.end_date_entry.get().strip()
        
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            elif self.selected_start_date:
                start_date = self.selected_start_date
            else:
                messagebox.showerror("Error", "Please select or enter a start date")
                return
            
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            elif self.selected_end_date:
                end_date = self.selected_end_date
            else:
                end_date = start_date
            
            # Ensure end date is not before start date
            if end_date < start_date:
                messagebox.showerror("Error", "End date cannot be before start date")
                return
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in YYYY-MM-DD format")
            return
        
        # Get location and comment
        location = self.location_entry.get().strip()
        comment = self.comment_text.get(1.0, tk.END).strip()
        
        if not location:
            messagebox.showerror("Error", "Please enter a location")
            return
        
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
            success_message = "Travel record updated successfully!"
        else:
            # Add new record
            self.travel_records.append(record)
            success_message = "Travel record added successfully!"
        
        self.save_data()
        self.update_calendar_display()
        self.update_location_dropdown()
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
    
    def update_records_display(self, records_tree):
        """Update the travel records display in the report window"""
        # Clear existing items
        for item in records_tree.get_children():
            records_tree.delete(item)
        
        # Add records sorted by start date
        sorted_records = sorted(self.travel_records, key=lambda x: x['start_date'], reverse=True)
        for record in sorted_records:
            # Truncate comment if it's too long for display
            comment = record.get('comment', '')
            if len(comment) > 50:
                comment = comment[:47] + "..."
            
            records_tree.insert('', tk.END, values=(
                record['start_date'],
                record['end_date'],
                record['location'],
                comment
            ))
    
    def edit_record(self, records_tree, report_window):
        """Edit selected travel record by populating main window"""
        selection = records_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to edit")
            # Restore focus to report window after messagebox
            report_window.lift()
            report_window.focus_force()
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
                
                # Set edit mode
                self.edit_mode = True
                self.edit_index = i
                
                # Update calendar display and close report window
                self.update_calendar_display()
                report_window.destroy()
                
                messagebox.showinfo("Edit Mode", "Record loaded for editing. Click 'Save' to update the record.")
                break
    
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
        
        # Add sorted records
        for record in sorted_records:
            # Truncate comment if it's too long for display
            comment = record.get('comment', '')
            if len(comment) > 50:
                comment = comment[:47] + "..."
            
            records_tree.insert('', tk.END, values=(
                record['start_date'],
                record['end_date'],
                record['location'],
                comment
            ))
    
    def update_column_headers(self, records_tree, sorted_column):
        """Update column headers to show sort indicators"""
        # Reset all headers first
        records_tree.heading('Start', text='Start Date')
        records_tree.heading('End', text='End Date')
        records_tree.heading('Location', text='Location')
        records_tree.heading('Comment', text='Comment')
        
        # Add sort indicator to the sorted column
        if sorted_column:
            arrow = ' ↓' if self.sort_reverse else ' ↑'
            if sorted_column == 'Start':
                records_tree.heading('Start', text=f'Start Date{arrow}')
            elif sorted_column == 'End':
                records_tree.heading('End', text=f'End Date{arrow}')
            elif sorted_column == 'Location':
                records_tree.heading('Location', text=f'Location{arrow}')
    
    
    def delete_record(self, records_tree, report_window):
        """Delete selected travel record from the report window"""
        selection = records_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to delete")
            # Restore focus to report window after messagebox
            report_window.lift()
            report_window.focus_force()
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
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
            self.update_records_display(records_tree)
            self.update_calendar_display()
            self.update_location_dropdown()
        
        # Restore focus to report window after any messagebox interaction
        report_window.lift()
        report_window.focus_force()
    
    def show_report(self):
        """Show travel report in a new window"""
        if not self.travel_records:
            messagebox.showinfo("Report", "No travel records found.")
            return
        
        # Reset sorting state
        self.sort_column = None
        self.sort_reverse = False
        
        # Calculate statistics
        total_days = 0
        locations = set()
        current_date = datetime.now()
        year_start = datetime(current_date.year, 1, 1)
        days_in_year_so_far = (current_date - year_start).days + 1
        
        for record in self.travel_records:
            start_date = datetime.strptime(record['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(record['end_date'], '%Y-%m-%d')
            
            # Only count days in current year
            if start_date.year <= current_date.year and end_date.year >= current_date.year:
                # Adjust dates to current year if needed
                count_start = max(start_date, year_start)
                count_end = min(end_date, current_date)
                
                if count_start <= count_end:
                    days = (count_end - count_start).days + 1
                    total_days += days
                    locations.add(record['location'])
        
        percentage = (total_days / days_in_year_so_far) * 100 if days_in_year_so_far > 0 else 0
        
        # Create report window
        report_window = tk.Toplevel(self.root)
        report_window.title("Travel Report")
        report_window.geometry("800x675")
        report_window.configure(bg='#f0f0f0')
        
        # Report content
        report_frame = ttk.Frame(report_window, padding="20")
        report_frame.pack(fill=tk.BOTH, expand=True)
        report_frame.columnconfigure(0, weight=1)
        report_frame.rowconfigure(2, weight=1)
        
        ttk.Label(report_frame, text="Travel Report", font=('Arial', 16, 'bold')).grid(row=0, column=0, pady=(0, 20))
        
        # Statistics frame
        stats_frame = ttk.Frame(report_frame)
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(stats_frame, text=f"Total Days Traveled (This Year): {total_days}", 
                 font=('Arial', 12)).pack(anchor=tk.W, pady=2)
        
        ttk.Label(stats_frame, text=f"Percentage of Year Traveled: {percentage:.1f}%", 
                 font=('Arial', 12)).pack(anchor=tk.W, pady=2)
        
        # Travel records section
        records_label_frame = ttk.LabelFrame(report_frame, text="Travel Records", padding="10")
        records_label_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        records_label_frame.columnconfigure(0, weight=1)
        records_label_frame.rowconfigure(0, weight=1)
        
        # Treeview for records
        records_tree = ttk.Treeview(records_label_frame, columns=('Start', 'End', 'Location', 'Comment'), show='headings', height=15)
        records_tree.heading('Start', text='Start Date')
        records_tree.heading('End', text='End Date')
        records_tree.heading('Location', text='Location')
        records_tree.heading('Comment', text='Comment')
        
        # Add click handlers for sortable columns
        records_tree.heading('Start', command=lambda: self.sort_records(records_tree, 'Start'))
        records_tree.heading('End', command=lambda: self.sort_records(records_tree, 'End'))
        records_tree.heading('Location', command=lambda: self.sort_records(records_tree, 'Location'))
        # Note: Comment column is intentionally not sortable
        
        # Set column widths
        records_tree.column('Start', width=100)
        records_tree.column('End', width=100)
        records_tree.column('Location', width=200)
        records_tree.column('Comment', width=300)
        
        scrollbar = ttk.Scrollbar(records_label_frame, orient=tk.VERTICAL, command=records_tree.yview)
        records_tree.configure(yscrollcommand=scrollbar.set)
        
        records_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Update records display
        self.update_records_display(records_tree)
        
        # Buttons frame
        buttons_frame = ttk.Frame(report_frame)
        buttons_frame.grid(row=3, column=0, pady=10)
        
        ttk.Button(buttons_frame, text="Edit Record", 
                  command=lambda: self.edit_record(records_tree, report_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete Record", 
                  command=lambda: self.delete_record(records_tree, report_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Close", command=report_window.destroy).pack(side=tk.LEFT, padx=5)

def main():
    root = tk.Tk()
    app = TravelCalendar(root)
    root.mainloop()

if __name__ == "__main__":
    main()