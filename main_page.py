from tkinter import *
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
        self.pins = [p for p in load_pins() if "lat" in p and "lon" in p]
        self.add_pin_mode = False
        self.dot_ids = []
        self.init_ui()

    def init_ui(self):
        # Sidebar (same as before)
        left_panel = Frame(self, width=300, bg="#f0f0f0")
        left_panel.pack(side=LEFT, fill=Y)
        left_panel.pack_propagate(False)
        Button(left_panel, text="Add Pin", command=self.enable_pin_mode).pack(pady=10, padx=10)

        # Map widget
        map_frame = Frame(self)
        map_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.map_widget = TkinterMapView(map_frame, width=800, height=600, corner_radius=0)
        self.map_widget.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.map_widget.set_position(37.7749, -122.4194)
        self.map_widget.set_zoom(10)

        # Transparent overlay canvas
        self.overlay = Canvas(map_frame, bg='', highlightthickness=0)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.bind("<Button-1>", self.on_overlay_click)

        # Redraw pins when map moves/zooms/resizes
        self.map_widget.canvas.bind("<Configure>", lambda e: self.redraw_overlay())
        self.map_widget.add_position_changed_event(self.redraw_overlay)
        self.map_widget.add_zoom_changed_event(self.redraw_overlay)

        self.redraw_overlay()

    def enable_pin_mode(self):
        self.add_pin_mode = True

    def on_overlay_click(self, event):
        # Convert overlay click to map coordinates
        lat, lon = self.map_widget.convert_canvas_xy_to_coordinates(event.x, event.y)
        # Check if clicked on a pin
        for idx, pin in enumerate(self.pins):
            px, py = self.map_widget.convert_coordinates_to_canvas_xy(pin["lat"], pin["lon"])
            if (event.x - px) ** 2 + (event.y - py) ** 2 < 12 ** 2:
                self.open_pin_view(pin)
                return
        # If in add mode, add pin
        if self.add_pin_mode:
            self.open_pin_form(lat, lon)
            self.add_pin_mode = False

    def redraw_overlay(self, *args):
        self.overlay.delete("all")
        dot_radius = 12
        for pin in self.pins:
            x, y = self.map_widget.convert_coordinates_to_canvas_xy(pin["lat"], pin["lon"])
            self.overlay.create_oval(
                x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius,
                fill="red", outline="black", width=2
            )

    def open_pin_form(self, lat, lon):
        win = Toplevel(self)
        win.title("Create a new memory")
        Label(win, text="Where? (Coordinates)").pack()
        coords_entry = Entry(win)
        coords_entry.insert(0, f"{lat:.6f}, {lon:.6f}")
        coords_entry.config(state="readonly")
        coords_entry.pack()
        Label(win, text="What happened?").pack()
        desc_text = Text(win, height=4, width=40)
        desc_text.pack()
        media_var = StringVar()
        def upload_file():
            path = filedialog.askopenfilename()
            if path:
                media_var.set(path)
        Button(win, text="Upload", command=upload_file).pack()
        media_label = Label(win, textvariable=media_var)
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
                "media": media_var.get(),
                "time": time_var.get(),
                "privacy": "public" if privacy_var.get() else "private"
            }
            self.pins.append(pin)
            save_pins(self.pins)
            win.destroy()
            self.redraw_overlay()
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
        if pin.get("media"):
            def open_media():
                try:
                    os.startfile(pin["media"])
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {e}")
            Button(win, text="Open Media", command=open_media).pack(pady=5)

if __name__ == "__main__":
    root = Tk()
    root.title("LocalLoom Map Memories")
    app = MainPage(root)
    root.mainloop()