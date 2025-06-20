from tkinter import Tk, Frame, Label, Entry, Button, StringVar, messagebox
import json
import os
from auth import signup, login
from main_page import MainPage  
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_FILE = os.path.join(BASE_DIR, "data", "user.json")

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file)

class GeotaggingApp:
    def __init__(self, master):
        self.master = master
        master.title("Geotagging App")

        self.frame = Frame(master)
        self.frame.pack(padx=10, pady=10)

        self.label = Label(self.frame, text="Welcome to Geotagging App")
        self.label.pack()

        self.username_var = StringVar()
        self.password_var = StringVar()

        self.username_label = Label(self.frame, text="Username:")
        self.username_label.pack()
        self.username_entry = Entry(self.frame, textvariable=self.username_var)
        self.username_entry.pack()

        self.password_label = Label(self.frame, text="Password:")
        self.password_label.pack()
        self.password_entry = Entry(self.frame, textvariable=self.password_var, show='*')
        self.password_entry.pack()

        self.signup_button = Button(self.frame, text="Sign Up", command=self.signup)
        self.signup_button.pack(pady=5)

        self.login_button = Button(self.frame, text="Login", command=self.login)
        self.login_button.pack(pady=5)

    def signup(self):
        username = self.username_var.get()
        password = self.password_var.get()
        result = signup(username, password)
        if result == "success":
            messagebox.showinfo("Success", "Account created successfully!")
        elif result == "duplicate":
            messagebox.showerror("Error", "Username already exists. Please choose another.")
        elif result == "invalid_password":
            messagebox.showerror(
                "Error",
                "Password must be at least 8 characters long and contain both letters and numbers."
            )
        else:
            messagebox.showerror("Error", "Unknown error occurred.")

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        if login(username, password):
            messagebox.showinfo("Success", "Logged in successfully!")
            self.frame.destroy()  # Remove login frame
            MainPage(self.master)  # Show main page
        else:
            messagebox.showerror("Error", "Invalid username or password.")

if __name__ == "__main__":
    root = Tk()
    app = GeotaggingApp(root)
    root.mainloop()