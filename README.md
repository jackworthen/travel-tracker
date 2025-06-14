# ✈️ Travel Tracker

> **Track your adventures with style! 🌍**

A beautiful, modern desktop application built with Python and tkinter that helps you visualize and manage your travel history with an intuitive calendar interface, powerful search capabilities, comprehensive validation features, and flexible export options.

---

## 🎯 Features

### 📅 **Interactive Calendar View**
- **Visual date selection** - Click dates to select travel periods
- **Color-coded travel days** - See your trips at a glance with cyan highlighting
- **Today indicator** - Current date highlighted in red for easy orientation
- **Range selection** - Easily pick start and end dates
- **Month navigation** - Browse through different months effortlessly
- **Sunday-first layout** - Standard US calendar format for familiar navigation
- **Smart date handling** - Supports multiple date formats (YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY)

### 📊 **Advanced Travel Analytics with Smart Filtering**
- 🚀 **Total trips taken** this year (completed trips only)
- 🗓️ **Upcoming trips** counter for future adventures
- ✈️ **Days traveled** statistics with precise calculations
- 📈 **Percentage of year** spent traveling
- 🌍 **Unique locations** visited counter
- 🔍 **Real-time search** - Instantly find trips by location, date, or notes
- 🎯 **Modern toggle filters** - Elegant Past/Current/Future status filtering
- 📅 **Year filtering** - Focus on specific years or view all data
- 📋 **Sortable columns** - Sort by date, location, or other criteria
- 🎨 **Enhanced color coding** - Clear visual distinction between trip statuses

### 📤 **Flexible Export System**
- **CSV export** - Export your filtered travel data to spreadsheet-compatible files
- **Multiple delimiter options** - Choose from Comma, Tab, Semicolon, or Pipe delimiters
- **Smart filtering** - Export exactly what you see based on current filters
- **Custom export directory** - Set your preferred save location
- **International compatibility** - Semicolon and Tab options for European/international use
- **Complete data export** - Includes departure dates, return dates, trip duration, locations, and notes
- **Intelligent file naming** - Automatic timestamp-based file names

### 🛡️ **Smart Validation System**
- ⚠️ **Overlap detection** - Prevents conflicting travel dates
- 🔮 **Future date warnings** - Intelligent alerts for trips scheduled too far ahead
- 📜 **Past date warnings** - Notifications for very old travel entries
- 📏 **Input length limits** - Configurable limits for locations and notes
- ✅ **Format validation** - Ensures data consistency and quality
- ⚙️ **Streamlined settings** - Clean, intuitive configuration interface

### 🎨 **Modern, Intuitive Interface**
- **Clean, professional design** with modern color schemes and premium styling
- **Enhanced search experience** - Beautiful search box with focus effects
- **Toggle button filtering** - Modern, responsive filter controls
- **Responsive layout** that adapts to your screen size
- **Visual status indicators** for past, current, and future travel
- **Smooth user experience** with helpful feedback and confirmations
- **Keyboard shortcuts** - Quick access to common functions
- **Enhanced dialogs** - Beautiful, informative validation and confirmation dialogs

### 💾 **Robust Data Management**
- **OS-specific storage** - Data saved in appropriate system directories
- **Persistent settings** - All preferences saved automatically
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
   - Click on the calendar to pick your departure date (Sunday-first layout)
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

### Exploring Your Travel Report

Click **"📊 View Travel Report"** to access the enhanced analytics dashboard:

#### 🔍 **Powerful Search & Filtering**
- **Real-time search** - Type to instantly filter trips by location, date, or notes
- **Smart toggle filters** - Click Past/Current/Future buttons to show/hide trip categories
- **Year selector** - Focus on specific years or view your entire travel history
- **Combined filtering** - Use search, status, and year filters together for precise results

#### 📊 **Rich Travel Statistics**
- 📈 **5 key metrics** for the current year with colorful visual cards
- 🎯 **Intelligent calculations** - Only counts completed trips for accurate statistics
- 📅 **Future trip planning** - See upcoming adventures at a glance

#### 📋 **Trip Management**
- **Complete trip history** with sortable columns
- ✏️ **Edit trips** - Modify any travel record with full validation
- 🗑️ **Delete entries** - Remove unwanted trips with confirmation
- 📤 **Export filtered data** - Save your travel records to CSV with custom formatting
- 🎨 **Visual status indicators** - Clear color coding for trip status

### Exporting Your Travel Data

The **📤 Export** button in the Travel Report allows you to save your travel records:

#### 📤 **Export Features**
- **Respects current filters** - Only exports what you see in the current view
- **Multiple file formats** - CSV files with your choice of delimiter
- **Complete data export** - Includes all trip details: dates, duration, location, and notes
- **Smart file naming** - Automatic timestamp-based file names (travel_records_YYYYMMDD_HHMMSS.csv)
- **Custom save location** - Choose where to save your files

#### 🔧 **Export Configuration**
Configure export settings in **Settings → Export**:
- **Delimiter Options**: 
  - **Comma ( , )** - Standard CSV format (default)
  - **Tab ( \t )** - TSV format, ideal when data contains commas
  - **Semicolon ( ; )** - European standard, perfect for international use
  - **Pipe ( | )** - Alternative delimiter for special cases
- **Export Directory** - Set your preferred save location with directory browser

### Configuring Settings

Use **View → Settings** (Ctrl+S) to customize your experience with three comprehensive tabs:

#### 🛡️ **Validation Settings**
- **Allow Overlapping Dates** - Choose whether trips can overlap
- **Limit Future Dates** - Set warnings for trips scheduled too far ahead
- **Limit Past Dates** - Configure alerts for very old travel entries
- **Intelligent thresholds** - Precise day-based warning calculations

#### 📊 **Report Settings**
- **Default Status Toggles** - Set which trip types show by default in reports
- **Past Trips** - Show completed travel by default
- **Current Trips** - Display ongoing trips by default
- **Future Trips** - Include planned trips by default

#### 📝 **Input Settings**
- **Max. Location Length** - Control location name limits
- **Max. Notes Length** - Set maximum comment length
- **Input validation** - Ensure data consistency across all entries

#### 📤 **Export Settings**
- **Delimiter Selection** - Choose your preferred CSV delimiter
- **Export Directory** - Set default save location for exported files
- **Persistent preferences** - All settings saved automatically

---

## ⌨️ Keyboard Shortcuts

- **Ctrl+R** - Open Travel Report
- **Ctrl+S** - Open Settings  
- **Ctrl+O** - Open Data Directory
- **Ctrl+Q** - Exit Application

---

## 🎨 Visual Guide

### Calendar Color Legend
- 🏠 **White** - Regular days (no travel)
- 📅 **Red** - Today's date
- ✈️ **Cyan** - Travel days
- 📍 **Orange** - Selected date range

### Report Color Legend
- 🔵 **Light Blue** - Past trips (completed)
- ✅ **Light Green** - Current/ongoing trips  
- 🟡 **Light Amber** - Future trips (planned)

### Filter Controls
- **Active toggle buttons** - Colored backgrounds indicate enabled filters
- **Inactive toggle buttons** - Gray appearance when filters are disabled
- **Focus effects** - Search box highlights with subtle blue border when active

---

## 📁 Data Storage

Your data is automatically stored in OS-appropriate locations:

### Windows
```
%APPDATA%\TravelTracker\
├── travel_data.json    # Your travel records
└── config.json         # Application settings
```

### macOS
```
~/Library/Application Support/TravelTracker/
├── travel_data.json    # Your travel records
└── config.json         # Application settings
```

### Linux
```
~/.local/share/TravelTracker/
├── travel_data.json    # Your travel records
└── config.json         # Application settings
```

**Data Migration**: If you're upgrading from an older version, your data will be automatically migrated to the new location.

---

## 📤 Export File Format

Exported CSV files include the following columns:
- **Departure Date** - Trip start date (MM-DD-YYYY format)
- **Return Date** - Trip end date (MM-DD-YYYY format)  
- **Days** - Total trip duration (calculated automatically)
- **Location** - Destination name
- **Notes** - Complete trip notes and comments

Example export with comma delimiter:
```csv
Departure Date,Return Date,Days,Location,Notes
01-15-2024,01-22-2024,8,Paris,Flight AA123, Hotel du Louvre
03-10-2024,03-17-2024,8,Tokyo,Cherry blossom season trip
```

---

## 🛠️ Technical Details

- **Built with**: Python 3.7+ and tkinter
- **Data Storage**: JSON format for easy backup and portability
- **Export Format**: CSV with configurable delimiters for maximum compatibility
- **UI Framework**: Modern ttk styling with custom themes and professional design
- **Architecture**: Object-oriented design with comprehensive validation system
- **Cross-platform**: Runs on Windows, macOS, and Linux with OS-specific optimizations

### Advanced Search Features
- **Multi-field search** across locations, dates, and notes
- **Real-time filtering** with instant results as you type
- **Case-insensitive matching** for flexible searching
- **Integrated with existing filters** for powerful query combinations

### Enhanced Validation Features
- **Date format validation** with support for multiple international formats
- **Intelligent date warnings** with precise day/year calculations
- **Date range validation** preventing impossible date combinations
- **Smart overlap detection** with user-configurable behavior
- **Input sanitization** for location and notes fields
- **Customizable warning thresholds** for unusual date ranges

### Export System Features
- **Flexible delimiter support** for international compatibility
- **Real-time filtering integration** - exports match current view exactly
- **UTF-8 encoding** for international character support
- **Configurable output location** with directory validation
- **Error handling** with informative user feedback

---

## 🚀 Recent Updates

### Version 3.0 Features
- 📤 **CSV Export System** - Export your travel data with flexible formatting options
- 🌍 **Multiple delimiter support** - Comma, Tab, Semicolon, and Pipe options for international compatibility
- ⚙️ **Enhanced settings panel** - New Export tab with comprehensive export configuration
- 📁 **Custom export directory** - Set your preferred save location with directory browser
- 📅 **Sunday-first calendar** - Standard US calendar layout for familiar navigation
- 🎯 **Smart export filtering** - Export exactly what you see based on current filters

### Version 2.5 Features
- 🔍 **Real-time search functionality** - Find trips instantly across all data
- 🎨 **Modern toggle button filters** - Replaced checkboxes with sleek toggle controls
- 🎯 **Enhanced visual design** - Improved color schemes and focus effects
- ⚙️ **Streamlined settings interface** - Cleaner, more intuitive configuration
- 🐛 **Improved date warnings** - Fixed calculation bugs for accurate messaging
- 📊 **Better status filtering** - More intuitive Past/Current/Future categorization
- 🔧 **UI refinements** - Enhanced spacing, colors, and interactive elements

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

The application offers extensive customization through the four-tab Settings panel:

- **Date Overlap Control**: Choose whether to allow overlapping travel dates
- **Future/Past Warnings**: Configure intelligent thresholds for date warnings
- **Text Input Limits**: Set maximum lengths for location names and notes
- **Report Defaults**: Configure which trip types show by default
- **Export Preferences**: Choose delimiter and default save location
- **Validation Behavior**: Adjust how strict the validation system should be

All settings are automatically saved and restored between sessions, with immediate visual feedback.

---

## 🔍 Pro Tips

### Search Like a Pro
- Use **partial matches** - Type "par" to find "Paris" trips
- Search by **year** - Type "2023" to find all trips from that year  
- Find **keywords in notes** - Search flight numbers, hotel names, or any detail
- **Combine filters** - Use search with status toggles and year selection

### Efficient Trip Management
- **Toggle status filters** to focus on specific trip types
- **Sort columns** by clicking headers for organized viewing
- **Edit from report** - Double-click any trip to modify it
- **Use keyboard shortcuts** for faster navigation

### Export Best Practices
- **Filter before exporting** - Use search and toggles to export exactly what you need
- **Choose the right delimiter** - Use Tab for data with commas, Semicolon for European compatibility
- **Set a consistent export directory** - Configure once in Settings for streamlined workflow
- **Check file names** - Automatic timestamps prevent accidental overwrites

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Star History

If this project helped you track your adventures, please consider giving it a star! ⭐

---

**Developed by Jack Worthen [jackworthen](https://github.com/jackworthen)**