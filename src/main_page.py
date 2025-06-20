from tkinter import *
from tkinter import filedialog, messagebox
from tkintermapview import TkinterMapView
import os, json, datetime, threading, time

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PINS_FILE = os.path.join(DATA_DIR, "pins.json")

def load_pins():
    if not os.path.exists(PINS_FILE):
        return []
    with open(PINS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_pins(pins):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PINS_FILE, "w", encoding="utf-8") as f:
        json.dump(pins, f, indent=2)

class MainPage(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=BOTH, expand=True)
        self.pins = [
    {**p, "media": [] if p.get("media", "") == "" else p.get("media")}
    for p in load_pins() if "lat" in p and "lon" in p
]
        self.last_pins = list(self.pins)
        self.add_pin_mode = False
        self.filter_text = StringVar()
        self.filtered_pins = self.pins.copy()
        self.markers = []
        self.init_ui()
        self.media_filters = {
    "jpg": BooleanVar(),
    "png": BooleanVar(),
    "mp4": BooleanVar(),
    "mp3": BooleanVar(),
    "wav": BooleanVar(),
    "avi": BooleanVar(),
    "mov": BooleanVar(),
}


    def init_ui(self):
        # Sidebar
        left_panel = Frame(self, width=300, bg="#f0f0f0")
        left_panel.pack(side=LEFT, fill=Y)
        left_panel.pack_propagate(False)

        Button(left_panel, text="Add Pin", command=self.enable_pin_mode).pack(pady=10, padx=10)
        Button(left_panel, text="Refresh", command=self.refresh_pins).pack(pady=5, padx=10)

        Label(left_panel, text="Name Filter:").pack(pady=5)
        Entry(left_panel, textvariable=self.filter_text).pack(pady=2, padx=10)

        Label(left_panel, text="Media Presence Filters:").pack(pady=5)
        for ext, var in self.media_filters.items():
            Checkbutton(left_panel, text=ext.upper(), variable=var, command=self.apply_filter).pack(anchor="w", padx=20)

        Button(left_panel, text="Apply Filter", command=self.apply_filter).pack(pady=5, padx=10)

        Label(left_panel, text="Memories:").pack(pady=5)
        self.memories_listbox = Listbox(left_panel, width=40)
        self.memories_listbox.pack(padx=10, pady=2, fill=Y, expand=True)
        self.memories_listbox.bind("<<ListboxSelect>>", self.on_memory_select)
        self.update_memories_listbox()

        # Map widget
        self.map_widget = TkinterMapView(self, width=800, height=600, corner_radius=0)
        self.map_widget.pack(side=LEFT, fill=BOTH, expand=True)
        self.map_widget.set_position(37.7749, -122.4194)
        self.map_widget.set_zoom(10)
        self.map_widget.add_left_click_map_command(self.on_map_click)

        self.refresh_markers()

    def enable_pin_mode(self):
        self.add_pin_mode = True
        # Optionally show a message to user

    def on_map_click(self, coords):
        if self.add_pin_mode:
            lat, lon = coords
            self.open_pin_form(lat, lon)
            self.add_pin_mode = False

    def refresh_markers(self):
        # Remove old markers
        for m in self.markers:
            m.delete()
        self.markers = []
        for pin in self.filtered_pins:
            marker = self.map_widget.set_marker(
                pin["lat"], pin["lon"],
                text=pin.get("description", "")[:20] or "Memory"
            )
            marker.data = pin
            # Use a function that takes marker as argument
            def marker_command(m, self=self):
                self.open_pin_view(m.data)
            marker.command = marker_command
            self.markers.append(marker)

    def open_pin_form(self, lat, lon):
        win = Toplevel(self)
        win.title("Create a new memory")

        # Force window to foreground
        win.lift()
        win.attributes('-topmost', True)
        win.after(100, lambda: win.attributes('-topmost', False))

        Label(win, text="Where? (Coordinates)").pack()
        coords_entry = Entry(win)
        coords_entry.insert(0, f"{lat:.6f}, {lon:.6f}")
        coords_entry.config(state="readonly")
        coords_entry.pack()
        Label(win, text="What happened?").pack()
        desc_text = Text(win, height=4, width=40)
        desc_text.pack()
        media_var = StringVar()
        media_files = []

        def upload_file():
            try:
                paths = filedialog.askopenfilenames(
                    title="Select media files",
                    filetypes=[("Media files", "*.jpg *.png *.mp4 *.avi *.mov *.mp3 *.wav"), ("All files", "*.*")]
                )
                if paths:
                    media_files.clear()
                    media_files.extend(paths)
                    media_var.set("; ".join(os.path.basename(p) for p in media_files))

                    # Bring window to foreground after file dialog
                    win.lift()
                    win.attributes('-topmost', True)
                    win.after(100, lambda: win.attributes('-topmost', False))

            except Exception as e:
                messagebox.showerror("Error", f"File selection failed: {e}")

        Button(win, text="Upload", command=upload_file).pack()
        media_label = Label(win, textvariable=media_var, wraplength=300, justify=LEFT)
        media_label.pack()
        time_var = StringVar(value=datetime.datetime.now().isoformat(timespec="seconds"))
        Entry(win, textvariable=time_var).pack()
        privacy_var = BooleanVar(value=True)
        Checkbutton(win, text="Public", variable=privacy_var).pack()

        def save_pin():
            pin = {
                "lat": lat,
                "lon": lon,
                "description": desc_text.get("1.0", "end").strip(),
                "media": list(media_files),
                "time": time_var.get(),
                "privacy": "public" if privacy_var.get() else "private"
            }
            self.pins.append(pin)
            save_pins(self.pins)
            win.destroy()
            self.apply_filter()
            self.refresh_markers()
        Button(win, text="Save", command=save_pin).pack(pady=10)

    def open_pin_view(self, pin):
        win = Toplevel(self)
        win.title("Memory Details")
        Label(win, text=f"Coordinates: {pin['lat']:.6f}, {pin['lon']:.6f}").pack()
        Label(win, text=f"Time: {pin.get('time', '')}").pack()
        Label(win, text=f"Privacy: {pin.get('privacy', '')}").pack()
        Label(win, text="Description:").pack()
        desc = Text(win, height=4, width=40)
        desc.insert("1.0", pin.get("description", ""))
        desc.config(state="disabled")
        desc.pack()
        # Show media files as a list of buttons
        if pin.get("media"):
            media_files = pin["media"] if isinstance(pin["media"], list) else [pin["media"]]
            if media_files:
                Label(win, text="Media files:").pack()
                for path in media_files:
                    fname = os.path.basename(path)
                    def open_media(p=path):
                        try:
                            os.startfile(p)
                        except Exception as e:
                            messagebox.showerror("Error", f"Could not open file: {e}")
                    Button(win, text=fname, command=open_media).pack(anchor="w", padx=10)

    def update_memories_listbox(self):
        self.memories_listbox.delete(0, END)
        for idx, pin in enumerate(self.filtered_pins):
            desc = pin.get("description", "")
            time_str = pin.get("time", "")
            self.memories_listbox.insert(END, f"{idx+1}. {desc[:30]}... @ {time_str}")

    def apply_filter(self):
        keyword = self.filter_text.get().lower().strip()
        active_media_exts = [ext for ext, var in self.media_filters.items() if var.get()]

        def media_match(pin):
            # Handle empty or string media fields
            media_list = pin.get("media", [])
            if isinstance(media_list, str):
                if not media_list.strip():
                    media_list = []
                else:
                    media_list = [media_list]
            if not active_media_exts:
                return True  # No media filter applied
            for path in media_list:
                ext = os.path.splitext(path)[1][1:].lower()
                if ext in active_media_exts:
                    return True
            return False

        def keyword_match(pin):
            if not keyword:
                return True
            return (keyword in pin.get("description", "").lower() or
                    keyword in pin.get("time", "").lower())

        self.filtered_pins = [
            p for p in self.pins
            if keyword_match(p) and media_match(p)
        ]

        self.update_memories_listbox()
        self.refresh_markers()

    def on_memory_select(self, event):
        selection = event.widget.curselection()
        if selection:
            idx = selection[0]
            pin = self.filtered_pins[idx]
            self.open_pin_view(pin)

    def refresh_pins(self):
        new_pins = [p for p in load_pins() if "lat" in p and "lon" in p]
        changes = self.detect_pin_changes(self.last_pins, new_pins)
        self.pins = new_pins
        self.last_pins = list(new_pins)
        self.apply_filter()
        if changes:
            self.show_notification(changes)

    def detect_pin_changes(self, old, new):
        changes = []
        old_map = {(p["lat"], p["lon"]): p for p in old}
        new_map = {(p["lat"], p["lon"]): p for p in new}
        for key in new_map:
            if key not in old_map:
                changes.append(f"memory at {key} added")
            else:
                old_pin = old_map[key]
                new_pin = new_map[key]
                if old_pin.get("time") != new_pin.get("time"):
                    changes.append(f"memory at {key} time changed")
                if old_pin.get("media") != new_pin.get("media"):
                    changes.append(f"memory at {key} new mediafiles")
        return changes

    def show_notification(self, changes):
        msg = "changed data: " + ", ".join(changes)
        notif = Toplevel(self)
        notif.overrideredirect(True)
        notif.geometry(f"300x60+{self.master.winfo_x()+320}+{self.master.winfo_y()+40}")
        Label(notif, text=msg, bg="yellow", wraplength=280).pack(fill=BOTH, expand=True)
        def close():
            time.sleep(2.5)
            notif.destroy()
        threading.Thread(target=close, daemon=True).start()

if __name__ == "__main__":
    root = Tk()
    root.title("LocalLoom Map Memories")
    app = MainPage(root)
    root.mainloop()