# 📅 Calendar Module

The **Calendar** module displays a monthly calendar along with optional upcoming events parsed from one or more iCalendar (`.ics`) feeds.  
It is one of the most popular Inkycal modules and is fully configurable via the web-UI.

This page explains:

- What the module does  
- How configuration works  
- How calendar rendering is performed  
- How event parsing works  
- How to debug issues with calendars  
- How to write custom ICS preprocessing logic  

---

## 🧭 Overview

The Calendar module:

- Renders a **6×7 monthly grid**
- Displays weekday names in your chosen language
- Highlights **today’s date** with a colored circle
- Marks days containing events
- Displays **upcoming events** below the calendar
- Supports multiple `.ics` URLs or local files
- Handles all-day events and multi-day events cleanly

---

## 📦 Example Output

*(You can later replace these mock images with actual screenshots)*

```
+--------------------------------------------+
|                 March 2025                 |
+--------------------------------------------+
| Mon   Tue   Wed   Thu   Fri   Sat   Sun    |
|  3     4     5     6     7     8     9     |
| ...                                        |
|           [ ● 12 ]                         |
| ...                                        |
+--------------------------------------------+
| Upcoming Events:                           |
| 12 Mar – Doctor appointment 10:00          |
| 14 Mar – Anna’s Birthday                   |
| ...                                        |
+--------------------------------------------+
```

Today’s date is drawn with a **circle** and white number.  
Days with events receive a **border highlight**.

---

## ⚙️ Configuration Options

These options appear in the Web-UI under module settings.

### **Required configuration**
The Calendar module has **no required parameters**. It runs out-of-the-box.

---

### **Optional configuration**

| Key              | Description                                    | Type                   | Default    |
|------------------|------------------------------------------------|------------------------|------------|
| `week_starts_on` | Choose whether weeks start on Monday or Sunday | `"Monday"`, `"Sunday"` | `"Monday"` |
| `show_events`    | Whether to show upcoming events                | `bool`                 | `True`     |
| `ical_urls`      | One or more ICS URLs (comma-separated)         | `str`                  | None       |
| `ical_files`     | One or more local ICS files                    | `str`                  | None       |
| `date_format`    | Arrow format string for dates                  | `str`                  | `"D MMM"`  |
| `time_format`    | Arrow format string for event times            | `str`                  | `"HH:mm"`  |
| `language`       | Locale used for month and weekday names        | `str`                  | `"en"`     |

---

## 🧠 How Rendering Works

### 1️⃣ Layout allocation  
The module receives a rendering area:

```
(width, height)
```

After subtracting padding, the area is split into:

1. **Month title**
2. **Weekday header row**
3. **Calendar grid (6 × 7)**
4. **Events section** (only if `show_events = True`)

---

### 2️⃣ Drawing the calendar grid

Each day is placed in a cell:

```
row = week index
col = day index
```

Bounding boxes for all grid cells are precomputed:

```python
grid_coordinates = [
    (grid_start_x + icon_width * x, grid_start_y + icon_height * y)
    for y in range(calendar_rows)
    for x in range(calendar_cols)
]
```

---

### 3️⃣ Highlighting today

A separate temporary `Canvas` is used to draw:

- A circle centered in the day cell
- The day number in white
- Properly centered using `anchor="mm"`

This ensures pixel-perfect alignment across displays.

---

### 4️⃣ Marking event days

Every event is expanded into **all days between start and end**:

```python
for day in arrow.Arrow.range('day', start, end):
    days_with_events.append(day.day)
```

All unique days then receive a rounded border.

---

### 5️⃣ Event rendering

Upcoming events (up to 4 weeks in advance) are shown below the calendar:

- Date is drawn left-aligned
- Time (if not all-day) is drawn next to date
- Title fills the remaining space
- Multi-day events display a human-readable duration:
  
Example:
```
2 days → "(in 2 days)"
```

Line wrapping is handled by the Canvas engine.

---

---

## 📖 How to Get iCalendar URLs

### Google Calendar (Recommended)

1. Open [Google Calendar](https://calendar.google.com)
2. Find the calendar you want to use in the left sidebar
3. Click the **three-dot menu** next to the calendar name
4. Select **"Settings and sharing"**
5. Scroll down to **"Integrate calendar"** section
6. Copy the link from **"Secret address in iCal format"**
7. Paste into the Calendar module's `ical_urls` field

**Example:** `https://calendar.google.com/calendar/ical/...%40group.calendar.google.com/public/basic.ics`

### Other Calendar Services

Most services support iCalendar export:
- **Outlook/Microsoft 365:** Settings → Calendar → iCalendar link
- **Apple Calendar:** Right-click calendar → Export
- **CalDAV servers:** Export or subscribe to iCalendar URL

### Validate Your iCalendar URL

Before using, test it works:

```bash
curl -s "YOUR_ICAL_URL" | head -20
```

You should see lines starting with `BEGIN:VCALENDAR`. If you get an error, verify:
- URL is public (not requiring authentication)
- URL is HTTPS (not HTTP)
- Calendar actually contains events

### Multiple Calendars

Separate multiple URLs with commas:

```json
"ical_urls": "https://calendar.google.com/...1.ics, https://calendar.google.com/...2.ics"
```

---

## 🎂 Adding Birthdays from Google Contacts to iCalendar

By default, Google Contacts birthdays don't sync to iCalendar. You can convert them using a Google Apps Script:

1. Open [Google Apps Script](https://script.google.com/home)
2. Create a **New project**
3. Paste this script:
   ```javascript
   function addBdayNotifications() {
     const cal = CalendarApp.getCalendarById("YOUR_CALENDAR_ID");
     const contacts = ContactsApp.getContactGroup("Contacts");
     contacts.getContacts().forEach(contact => {
       const date = contact.getDates(ContactsApp.Field.BIRTHDAY)[0];
       if (date) {
         cal.createAllDayEvent(`Birthday: ${contact.getFullName()}`, date);
       }
     });
   }
   ```
4. Click **Run** (authorize when prompted)
5. Go to your Google Calendar → **Settings** → **Calendars** → find "Birthdays" or the calendar you created
6. Get the iCalendar link (same process as above)

---

## 🔗 Parsing iCalendar Files

The module uses:

```
inkycal.utils.ical_parser.iCalendar
```

This parser:

- Loads `.ics` URLs
- Loads local `.ics` files
- Sorts events by start date
- Normalizes timezone-aware values
- Detects all-day events via:
  
```python
parser.all_day(event)
```

You can pass **multiple** calendar URLs or files.

---

## 📘 Full Rendering Flow

```
Calendar.generate_image()
    |
    +--> Compute layout regions
    +--> Create Canvas
    +--> Draw month & weekdays
    +--> Build month grid
    +--> Highlight today
    +--> Retrieve + parse ICS events
    +--> Draw event-day borders
    +--> Draw upcoming events list
    +--> Return (black_img, colour_img)
```

---

## 🔧 Tips for Better Calendar Results

### ✔ Choose readable fonts  
If using languages like Chinese, Japanese, Korean—ensure CJK fonts are installed.

### ✔ Ensure ICS URLs support HTTPS  
Many servers block plain HTTP.

### ✔ Verify timezones  
If events show at wrong times:
- Confirm Raspberry Pi timezone via  
  ```
  sudo dpkg-reconfigure tzdata
  ```
- Check ICS feed timezone fields

### ✔ Reduce event clutter  
Use filters in your calendar service if available.

---

## 🧪 Troubleshooting

### ❌ Events are missing  
Checklist:

- Does ICS feed load in the browser?
- Are there events in the next 4 weeks? (default range)
- Is `show_events` enabled?

### ❌ Wrong date formatting  
Your locale may not support certain month abbreviations.  
Try a standard format:

```
D MMMM
MMM DD
```

### ❌ Today circle misaligned  
This usually means:

- Canvas font height was oversized  
- Day cell height too small  
- Incorrect DPI scaling on custom displays  

Try lowering font size by 10–20%.

---

## 🧩 Extending the Calendar Module

You may want to:

- Add holiday highlights
- Add weather integration into each day cell
- Display week numbers
- Replace circle highlight with a rectangle or icon

All changes should be made in:

```
inkycal/modules/calendar.py
```

And rendered using:

```
Canvas.write(...)
Canvas.draw_icon(...)
Canvas utilities
```

---

## 📄 Summary

The Calendar module is a powerful, flexible, and highly customizable component.  
It makes heavy use of the Canvas abstraction to guarantee:

- Consistent rendering  
- Alignment across displays  
- Efficient pixel usage  
- Multi-language support  

It remains one of the most mature and well-tested parts of Inkycal.

If you are creating your own module, studying this one is an excellent place to start.