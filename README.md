# Travel Tracker: Your Personal Voyage Companion

This **Travel Tracker** is a sleek, modern desktop application designed to help you organize your journeys, manage travel history, and visualize your adventures through an intuitive calendar and analytics dashboard.

---

## 🚀 Key Features

* **Interactive Calendar**: Select dates directly on the grid to log new trips.
* **Smart Validation**: Prevents overlapping trips and alerts you to excessively long durations or suspicious dates.
* **Dynamic Analytics**: View detailed statistics for the current year, including total days traveled, percentage of the year away, and unique locations visited.
* **Dual-Type Logging**: Categorize your travels into **Work** or **Personal** trips.
* **Advanced Reporting**: Filter, search, and sort your entire travel history.
* **Cross-Platform Data Storage**: Automatically saves your data in OS-specific folders (AppData/Roaming for Windows, Application Support for macOS) to keep your records safe.

---

## 🎨 Interface Overview

| Feature | Description |
| :--- | :--- |
| **Blue Days** | Represents **Today's** current date. |
| **Cyan Days** | Represents scheduled **Travel Days**. |
| **Orange Days** | Shows your current **Selection** on the calendar. |
| **Green Alerts** | Successful saves and updates. |
| **Red/Amber Alerts** | Critical errors or travel overlaps. |

---

## 🛠️ How to Use

### 1. Adding a Trip
1.  **Select Dates**: Click a start date and then an end date on the calendar.
2.  **Enter Details**: Provide a location, select the travel type (Work/Personal), and add any notes.
3.  **Save**: Click **Save Travel**. The calendar will instantly update with Cyan highlights.

### 2. Viewing Reports
* Click **View Travel Report** to see a searchable list of all trips.
* Use the **Status Toggles** to show only Past, Current, or Future trips.
* **Edit or Delete** entries directly from the report table.

### 3. Analyzing Your Travels
* Open the **Analytics Dashboard** to see your "Most Traveled Year," "Peak Travel Month," and "Total Weekend Days" spent away.

---

## ⚙️ Customization & Settings

Access the **Settings** menu (Ctrl+S) to personalize your experience:
* **Date Formats**: Choose how dates appear (e.g., `MM/DD/YYYY` or `Month DD, YYYY`).
* **Color Schemes**: Change the colors for Today, Travel Days, and Selection.
* **Export Preferences**: Configure default export formats (CSV, JSON, XML, or TXT).
* **Backups**: Enable automatic backups of your data and configurations.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| **Ctrl + R** | Open Travel Report |
| **Ctrl + A** | Open Analytics Dashboard |
| **Ctrl + S** | Open Settings |
| **Ctrl + O** | Open Data Folder (on your computer) |
| **Ctrl + D** | View Documentation |
| **Ctrl + Q** | Exit Application |

---

## 📂 Technical Requirements
* **Language**: Python 3.x
* **Libraries**: Uses standard libraries (`tkinter`, `json`, `sqlite3`, etc.)—no heavy external dependencies required!

> **Pro Tip**: To keep your data safe, use the **Backup** tab in Settings to save a copy of your travel history to your Documents or a cloud-synced folder!
