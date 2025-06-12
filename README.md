# ✈️ Travel Tracker

> **Track your adventures with style! 🌍**

A beautiful, modern desktop application built with Python and tkinter that helps you visualize and manage your travel history with an intuitive calendar interface and powerful validation features.

---

## 🎯 Features

### 📅 **Interactive Calendar View**
- **Visual date selection** - Click dates to select travel periods
- **Color-coded travel days** - See your trips at a glance with cyan highlighting
- **Today indicator** - Current date highlighted in red for easy orientation
- **Range selection** - Easily pick start and end dates
- **Month navigation** - Browse through different months effortlessly
- **Smart date handling** - Supports multiple date formats (YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY)

### 📊 **Advanced Travel Analytics**
- 🚀 **Total trips taken** this year (completed trips only)
- 🗓️ **Upcoming trips** counter for future adventures
- ✈️ **Days traveled** statistics with precise calculations
- 📈 **Percentage of year** spent traveling
- 🌍 **Unique locations** visited counter
- 🎯 **Flexible filtering** - View trips by year and status (past, current, future)
- 📋 **Sortable columns** - Sort by date, location, or other criteria

### 🛡️ **Smart Validation System**
- ⚠️ **Overlap detection** - Prevents conflicting travel dates
- 🔮 **Future date warnings** - Alerts for trips scheduled too far ahead
- 📜 **Past date warnings** - Notifications for very old travel entries
- 📏 **Input length limits** - Configurable limits for locations and notes
- ✅ **Format validation** - Ensures data consistency and quality
- ⚙️ **Customizable settings** - Adjust validation rules to your preferences

### 🎨 **Modern, Intuitive Interface**
- **Clean, professional design** with modern color schemes and styling
- **Responsive layout** that adapts to your screen size
- **Visual status indicators** for past, current, and future travel
- **Smooth user experience** with helpful feedback and confirmations
- **Keyboard shortcuts** - Quick access to common functions
- **Enhanced dialogs** - Beautiful, informative validation and confirmation dialogs

### 💾 **Robust Data Management**
- **OS-specific storage** - Data saved in appropriate system directories
- **Persistent settings** - Validation preferences saved automatically
- **Edit existing trips** - Update your travel records anytime with validation
- **Delete unwanted entries** - Keep your data clean with confirmation dialogs
- **Auto-complete locations** - Reuse previous destinations for faster entry
- **Rich notes support** - Add detailed comments about your trips
- **Data migration** - Automatic migration from legacy storage locations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- tkinter (usually comes with Python)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jackworthen/travel-tracker.git
   cd travel-tracker
   ```

2. **Run the application**
   ```bash
   python tt.py
   ```

That's it! No additional dependencies required. 🎉

---

## 🎮 How to Use

### Adding a New Trip

1. **📅 Select Dates**
   - Click on the calendar to pick your departure date
   - Click again to select your return date
   - Or manually type dates in various formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
   - Clear dates anytime with the "Clear Dates" button

2. **📍 Enter Location**
   - Type your destination in the location field
   - Previous locations will auto-suggest for quick entry
   - Location length is validated based on your settings

3. **📝 Add Notes** (Optional)
   - Include flight details, hotel info, or trip highlights
   - Perfect for keeping track of important travel information
   - Note length is validated to ensure database consistency

4. **💾 Save Your Trip**
   - Click "Save Travel" to add your trip to the calendar
   - Smart validation checks for overlaps and date issues
   - Watch as your calendar updates with beautiful color coding!

### Viewing Your Travel Report

Click **"📊 View Travel Report"** to access:
- 📊 **Travel statistics** with 5 key metrics for the current year
- 📅 **Year filtering** - Focus on specific years or view all data
- 🎨 **Status filtering** - Show past, current, or future trips
- 📋 **Complete trip history** with sortable columns
- ✏️ **Edit/Delete options** for managing your data
- 🔍 **Visual indicators** showing trip status with color coding

### Configuring Validation Settings

Use **View → Validation Settings** (Ctrl+S) to customize:
- 📅 **Date validation rules** - Overlap detection and date warnings
- 📏 **Text length limits** - Maximum length for locations and notes
- ⏰ **Warning thresholds** - How far in the future/past to warn about dates
- 🔧 **Overlap behavior** - Allow or prevent conflicting travel dates

---

## ⌨️ Keyboard Shortcuts

- **Ctrl+R** - Open Travel Report
- **Ctrl+S** - Open Validation Settings  
- **Ctrl+D** - Open Data Directory
- **Ctrl+Q** - Exit Application

---

## 🎨 Visual Guide

### Calendar Color Legend
- 🏠 **White** - Regular days (no travel)
- 📅 **Red** - Today's date
- ✈️ **Cyan** - Travel days
- 📍 **Orange** - Selected date range

### Report Color Legend
- 🕐 **Light Gray** - Past trips (completed)
- ✅ **Light Green** - Current/ongoing trips  
- 🔮 **Light Yellow** - Future trips (planned)

---

## 📁 Data Storage

Your data is automatically stored in OS-appropriate locations:

### Windows
```
%APPDATA%\TravelTracker\
├── travel_data.json    # Your travel records
└── config.json         # Validation settings
```

### macOS
```
~/Library/Application Support/TravelTracker/
├── travel_data.json    # Your travel records
└── config.json         # Validation settings
```

### Linux
```
~/.local/share/TravelTracker/
├── travel_data.json    # Your travel records
└── config.json         # Validation settings
```

**Data Migration**: If you're upgrading from an older version, your data will be automatically migrated to the new location.

---

## 🛠️ Technical Details

- **Built with**: Python 3.7+ and tkinter
- **Data Storage**: JSON format for easy backup and portability
- **UI Framework**: Modern ttk styling with custom themes and professional design
- **Architecture**: Object-oriented design with comprehensive validation system
- **Cross-platform**: Runs on Windows, macOS, and Linux with OS-specific optimizations

### Validation Features
- **Date format validation** with support for multiple international formats
- **Date range validation** preventing impossible date combinations
- **Overlap detection** with user-configurable behavior
- **Input sanitization** for location and notes fields
- **Configurable warning system** for unusual date ranges

---

## 🚀 Recent Updates

### Version 2.0 Features
- ✨ **Smart validation system** with customizable rules
- 🎯 **Enhanced travel report** with filtering and sorting
- ⚙️ **Persistent settings** stored in config.json
- 📅 **Today highlighting** on calendar for better orientation
- ⌨️ **Keyboard shortcuts** for power users
- 🗂️ **OS-specific data storage** with automatic migration
- 🎨 **Improved UI/UX** with better dialogs and feedback

---

## 🔧 Customization

The application offers extensive customization through the Validation Settings:

- **Overlap Prevention**: Choose whether to allow overlapping travel dates
- **Date Warnings**: Configure how far in the future/past to warn about unusual dates
- **Text Limits**: Set maximum lengths for location names and notes
- **Validation Behavior**: Adjust how strict the validation system should be

All settings are automatically saved and restored between sessions.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Star History

If this project helped you track your adventures, please consider giving it a star! ⭐

---

**Developed by Jack Worthen [jackworthen](https://github.com/jackworthen)**