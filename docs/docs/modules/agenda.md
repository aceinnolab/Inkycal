# 🗓️ Agenda Module

The **Agenda** module displays a list of upcoming events from one or more iCalendar (`.ics`) feeds. It is designed to be a clean, list-based alternative to the full monthly calendar view.

This page explains:

- What the module does
- How to configure it, including the two-column layout
- How event rendering and wrapping works
- How to debug common issues

---

## 🧭 Overview

The Agenda module:

- Renders a **chronological list** of upcoming events
- Displays date headers to group events by day
- Supports a **single or two-column layout**
- Fetches events from multiple `.ics` URLs or local files
- Handles all-day events with a dedicated icon
- Wraps long event titles to fit the available space

---

## 📦 Example Output

### Single-Column Layout

```
+--------------------------------------------+
| Mon 10 Mar                                 |
+--------------------------------------------+
|   10:00   • Doctor appointment             |
|           • Team meeting that has a very   |
|             long title and wraps to the    |
|             next line                      |
|   All-day • Anna’s Birthday                |
+--------------------------------------------+
| Tue 11 Mar                                 |
+--------------------------------------------+
|   14:30   • Project Deadline               |
+--------------------------------------------+
```

### Two-Column Layout

```
+----------------------+-----------------------+
| Mon 10 Mar           | Tue 11 Mar            |
+----------------------+-----------------------+
|   10:00   • Doctor   |   14:30   • Project   |
|             appoint- |             Deadline|
|             ment     |                       |
|           • Team     |                       |
|             meeting  |                       |
+----------------------+-----------------------+
```

---

## ⚙️ Configuration Options

These options appear in the Web-UI under module settings.

### **Required configuration**

| Key         | Description                            | Type  | Default |
|-------------|----------------------------------------|-------|---------|
| `ical_urls` | One or more ICS URLs (comma-separated) | `str` | None    |

---

### **Optional configuration**

| Key           | Description                                    | Type                   | Default       |
|---------------|------------------------------------------------|------------------------|---------------|
| `ical_files`  | One or more local ICS files                    | `str`                  | None          |
| `date_format` | Arrow format string for date headers           | `str`                  | `"ddd D MMM"` |
| `time_format` | Arrow format string for event times            | `str`                  | `"HH:mm"`     |
| `language`    | Locale used for date formatting                | `str`                  | `"en"`        |
| `columns`     | Number of columns (1 or 2 supported)           | `int`                  | `1`           |

---

## 🧠 How Rendering Works

### 1️⃣ Layout and Data Fetching
The module first calculates the available space and divides it into one or two columns based on the `columns` configuration. It then fetches all upcoming events from the provided iCalendar sources.

### 2️⃣ Flow Layout
Unlike a fixed grid, the Agenda module uses a **flow layout**:
1.  It iterates through a chronologically sorted list of items (date headers and events).
2.  For each item, it calculates the required height, accounting for text wrapping.
3.  If the item fits in the current column, it is rendered.
4.  If it does not fit, the module moves to the next column and resets the vertical position.

### 3️⃣ Text and Icon Rendering
- **Date Headers**: Rendered with a horizontal line.
- **Event Times**: Right-aligned within a dedicated time area.
- **All-Day Events**: Represented by a calendar icon (`\ue878` from Material Icons), rendered using `canvas.draw_icon` for proper scaling and centering.
- **Event Titles**: Rendered with a bullet point. Long titles are automatically wrapped to the next line.

### 4️⃣ Orphan Prevention
To avoid leaving a date header stranded at the bottom of a column, the module uses **look-ahead logic**:
- Before rendering a date header, it checks if the *next* event can also fit in the remaining space.
- If the event does not fit, the date header is moved to the top of the next column along with its event.

---

## 📖 How to Get iCalendar URLs

### Google Calendar (Recommended)

1. Open [Google Calendar](https://calendar.google.com)
2. Find the calendar you want to use in the left sidebar
3. Click the **three-dot menu** next to the calendar name
4. Select **"Settings and sharing"**
5. Scroll down to **"Integrate calendar"** section
6. Copy the link from **"Secret address in iCal format"**
7. Paste into the Agenda module's `ical_urls` field

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

The module uses the same `inkycal.utils.ical_parser.iCalendar` as the Calendar module. This parser handles loading, sorting, and normalizing events from `.ics` files and URLs.

---

## 🔧 Troubleshooting

### ❌ Events are overlapping or cut off
- This can happen if the `size` of the module in `settings.json` is too small for the content.
- If using two columns, ensure the width is sufficient. A good starting point is at least 600-800 pixels wide for a two-column layout.
- The text wrapping logic depends on the `event_width` calculation. If you have modified the code, ensure this calculation is correct.

### ❌ All-Day icon is too small or misaligned
- The icon is rendered using `canvas.draw_icon`. Its size is based on the `line_height`.
- If the icon appears too small, you can adjust the `fill_ratio` parameter in the `draw_icon` call within `inkycal_agenda.py`.

### ❌ Date headers are repeated unnecessarily
- The logic to repeat date headers at the top of a new column is designed to provide context.
- If a date header is repeated when you don't expect it, it means an event from that day was the first item to be rendered in the new column. This is the intended behavior.

---

## 📄 Summary

The Agenda module provides a clean, readable list of your upcoming events. Its support for multi-column layouts and intelligent text wrapping makes it a versatile choice for various display sizes and orientations. By leveraging the `Canvas` class for rendering, it ensures a consistent and polished look.