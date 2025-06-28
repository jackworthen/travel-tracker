# ✈️ Travel Tracker

> **Track your adventures with style! 🌍**

A beautiful, modern desktop application built with Python and tkinter that helps you visualize and manage your travel history with an intuitive calendar interface, powerful search capabilities, comprehensive validation features, advanced analytics, and flexible export options.

---

## 🎯 Features

### 📅 **Interactive Calendar View**
- **Visual date selection** - Click dates to select travel periods
- **Color-coded travel days** - See your trips at a glance with cyan highlighting
- **Today indicator** - Current date displayed in blue for easy orientation
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

### 📊 **Comprehensive Analytics Dashboard**
- 📈 **Year-specific analytics** - Analyze past and future travel by selected years
- 🎯 **Detailed metrics** - Track trips, days, locations, average trip length, and weekend travel days
- 🏆 **Trip extremes** - Identify your longest and shortest trips
- 🌟 **Overall statistics** - Total trips, total travel days across all years, travel span, and most traveled year
- 📊 **Percentage tracking** - See what percentage of each year you've spent traveling
- 🗓️ **Flexible year selection** - Compare different years or focus on specific time periods
- 🎨 **Visual data cards** - Modern, color-coded cards for easy data interpretation

### 📤 **Flexible Export System**
- **Records export** - Export your filtered travel data to spreadsheet-compatible files (CSV, TXT, XML, JSON)
- **Multiple delimiter options** - Choose from Comma or Pipe delimiters
- **Smart filtering** - Export exactly what you see based on current filters
- **Custom export directory** - Set your preferred save location
- **International compatibility** - Pipe option for data containing commas
- **Complete data export** - Includes departure dates, return dates, trip duration, locations, and notes
- **Intelligent file naming** - Automatic timestamp-based file names

### 🛡️ **Smart Validation System**
- ⚠️ **Overlap detection** - Prevents conflicting travel dates with user choice dialogs
- 🔮 **Future date warnings** - Intelligent alerts for trips scheduled too far ahead
- 📜 **Past date warnings** - Notifications for very old travel entries
- 📏 **Input length limits** - Configurable limits for locations and notes
- ✅ **Format validation** - Ensures data consistency and quality
- 🎛️ **Advanced date format support** - Accepts MM/DD/YYYY, MM-DD-YYYY, YYYY-MM-DD, DD/MM/YYYY formats
- ⚙️ **Streamlined settings** - Clean, intuitive configuration interface

### 🎨 **Modern, Intuitive Interface**
- **Clean, professional design** with modern color schemes and premium styling
- **Enhanced search experience** - Beautiful search box with focus effects and placeholder text
- **Toggle button filtering** - Modern, responsive filter controls with active/inactive states
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
- **Real-time search** - Type to instantly filter trips by location, date, or notes with placeholder text guidance
- **Smart toggle filters** - Click Past/Current/Future buttons to show/hide trip categories with visual active/inactive states
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
- 📤 **Export filtered data** - Save your travel records with custom formatting
- 🎨 **Visual status indicators** - Clear color coding for trip status

### Accessing the Analytics Dashboard

Click **"📊 Analytics Dashboard"** from the Travel Report or use **Ctrl+A** to open the comprehensive analytics dashboard:

#### 📊 **Year-Specific Analytics**
- **Past Travel Analysis** - Select any past year to see detailed metrics including trips, days, locations, weekend travel, and percentage of year spent traveling
- **Future Travel Analysis** - Analyze planned trips for any future year
- **Trip Extremes** - View your longest and shortest trips for each selected year
- **Location Tracking** - Count unique destinations per year

#### 🏆 **Overall Travel Statistics**
- **Total Trips** - Complete count of all travel records
- **Total Travel Days** - Sum of all travel days across your entire history
- **Total Weekend Days** - Shows how number of weekend travel days (Sat/Sunday)
- **Most Traveled Year** - Identifies which year had the most travel days
- **Unique Locations** - Total count of different destinations visited
- **Peak Month** - Shows busiest travel monmth

### Exporting Your Travel Data

The **📤 Export** button in the Travel Report allows you to save your travel records:

#### 📤 **Export Features**
- **Respects current filters** - Only exports what you see in the current view
- **Multiple file formats** - CSV or TXT files with your choice of delimiter
- **Complete data export** - Includes all trip details: dates, duration, location, and notes
- **Smart file naming** - Automatic timestamp-based file names (travel_records_YYYYMMDD_HHMMSS.csv)
- **Custom save location** - Choose where to save your files

#### 🔧 **Export Configuration**
Configure export settings in **Settings → Export**:
- **Delimiter Options**: 
  - **Comma ( , )** - Standard CSV format (default)
  - **Pipe ( | )** - Alternative delimiter for data containing commas
- **Export Directory** - Set your preferred save location with directory browser

### Configuring Settings

Use **View → Settings** (Ctrl+S) to customize your experience with four comprehensive tabs:

#### 🛡️ **Validation Settings**
- **Allow Overlapping Dates** - Choose whether trips can overlap with smart conflict resolution
- **Limit Future Dates** - Set warnings for trips scheduled too far ahead
- **Limit Past Dates** - Configure alerts for very old travel entries
- **Intelligent thresholds** - Precise day-based warning calculations

#### 📊 **Report Settings**
- **Default Status Toggles** - Set which trip types show by default in reports
- **Past Trips** - Show completed travel by default
- **Current Trips** - Display ongoing trips by default
- **Future Trips** - Include planned trips by default
- **Default Year Filter** - Set whether reports open showing "All Years" or "Current Year"

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

- **Ctrl+A** - Open Analytics Dashboard
- **Ctrl+R** - Open Travel Report
- **Ctrl+S** - Open Settings  
- **Ctrl+O** - Open Data Directory
- **Ctrl+D** - Open Documentation
- **Ctrl+Q** - Exit Application

---

## 🎨 Visual Guide

### Calendar Color Legend
- 🏠 **White** - Regular days (no travel)
- 📅 **Blue** - Today's date
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

## 🔧 Customization

The application offers extensive customization through the four-tab Settings panel:

- **Date Overlap Control**: Choose whether to allow overlapping travel dates with smart conflict resolution
- **Future/Past Warnings**: Configure intelligent thresholds for date warnings
- **Text Input Limits**: Set maximum lengths for location names and notes
- **Report Defaults**: Configure which trip types show by default and default year filter
- **Export Preferences**: Choose delimiter and default save location
- **Validation Behavior**: Adjust how strict the validation system should be

All settings are automatically saved and restored between sessions, with immediate visual feedback.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Star History

If this project helped you track your adventures, please consider giving it a star! ⭐

---

**Developed by Jack Worthen [jackworthen](https://github.com/jackworthen)**
