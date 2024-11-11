import sqlite3
import tkinter as tk
from tkinter import messagebox
import RPi.GPIO as GPIO
import time
import discord
from discord.ext import commands
from config import WEBHOOK_URL
import requests


from pn532 import *

# Initialize Raspberry Pi GPIO pins for the rotary encoder
GPIO.setmode(GPIO.BCM)
MSB_PIN = 27
LSB_PIN = 17
GPIO.setup(MSB_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LSB_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_db_connection():
    conn = sqlite3.connect('discord_bot.db')
    return conn

class SpaceFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', False)
        self.root.configure(bg="white")
        
        self.encoder_ticks = 0
        self.event_id = None
        self.selected_user = None
        self.create_main_window()

    def create_main_window(self):
        # Display the welcome message
        self.clear_screen()
        welcome_label = tk.Label(self.root, text="Welcome to SpaceFinder!", font=("Arial", 24), bg="white")
        welcome_label.pack(pady=20)

        events = self.get_events()
        if not events:
            no_event_label = tk.Label(self.root, text="To get started, schedule an event with the SpaceFinder Discord bot.",
                                      font=("Arial", 14), bg="white")
            no_event_label.pack(pady=10)
        else:
            for event in events:
                event_button = tk.Button(self.root, text=event[2], font=("Arial", 14), command=lambda e=event: self.start_event(e))
                event_button.pack(pady=5)

    def get_events(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM events")
        events = c.fetchall()
        conn.close()
        return events

    def start_event(self, event):
        self.event_id = event[0]
        # Update database to indicate event has started
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE events SET status='started' WHERE event_id=?", (self.event_id,))
        conn.commit()
        conn.close()
        
        # Send message to Discord webhook
        self.post_to_webhook(f"Starting event: {event[2]}\nDescription: {event[3]}")
        
        # Update display
        self.clear_screen()
        event_label = tk.Label(self.root, text=f"Welcome to Spacefinder!\n{event[2]}\n{event[3]}", font=("Arial", 24), bg="white")
        event_label.pack(pady=20)
        
        scan_button = tk.Button(self.root, text="Scan your U Card to register for the event", font=("Arial", 14), command=self.scan_card)
        scan_button.pack(pady=10)

    def post_to_webhook(self, content):
        data = {"content": content}
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code != 204:
            print("Failed to send webhook:", response.status_code, response.text)

    def scan_card(self):
        # Implement card scanning code here
        # Assume card ID and user ID retrieval, then move to the user selection screen
        self.show_user_selection()

    def show_user_selection(self):
        self.clear_screen()
        users = self.get_event_users(self.event_id)
        user_buttons = []
        
        for user in users:
            button_color = "green" if not user[4] else "red"
            user_button = tk.Button(self.root, text=user[1], font=("Arial", 14), bg=button_color,
                                    command=lambda u=user: self.select_user(u))
            user_button.pack(pady=5)
            user_buttons.append(user_button)

    def select_user(self, user):
        if user[4]:  # Already signed in, so confirm sign-out
            self.confirm_signout(user)
        else:
            self.confirm_user(user)

    def confirm_signout(self, user):
        result = messagebox.askyesno("Sign Out", f"Are you sure you'd like to sign out {user[1]}?")
        if result:
            # Update database to sign out user
            self.post_to_webhook(f"{user[1]} has signed out of event ID {self.event_id}.")

    def confirm_user(self, user):
        # Mark user as present and update Discord
        self.clear_screen()
        duration_label = tk.Label(self.root, text="Choose the amount of time you'd like to stay:", font=("Arial", 18), bg="white")
        duration_label.pack(pady=20)
        
        self.current_duration = 30
        duration_value = tk.Label(self.root, text=f"{self.current_duration} minutes", font=("Arial", 16), bg="white")
        duration_value.pack(pady=10)
        
        confirm_button = tk.Button(self.root, text="Confirm", command=lambda: self.confirm_registration(user))
        confirm_button.pack(pady=20)
        
        GPIO.add_event_detect(MSB_PIN, GPIO.BOTH, callback=self.update_duration)
        GPIO.add_event_detect(LSB_PIN, GPIO.BOTH, callback=self.update_duration)

    def update_duration(self, channel):
        # Read encoder input, update duration
        pass

    def confirm_registration(self, user):
        # Finalize user registration in database
        self.clear_screen()
        success_label = tk.Label(self.root, text=f"You've successfully registered for {self.event_id}!", font=("Arial", 18), bg="white")
        success_label.pack(pady=20)
        self.post_to_webhook(f"{user[1]} is now present at event ID {self.event_id}. Duration: {self.current_duration} minutes.")
        self.root.after(3000, self.create_main_window)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpaceFinderApp(root)
    root.mainloop()


# Database connection

# #### NFC SETUP
# 
# pn532 = PN532_SPI(debug=False, reset=20, cs=4)
# ic, ver, rev, support = pn532.get_firmware_version()
# print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
# 
# # Configure PN532 to communicate with MiFare cards
# pn532.SAM_configuration()
# 
# def update_message(new_message):
#     instruction_label.config(text=new_message)
#     root.update_idletasks()  # Update display immediately
# 
# # Poll for card detection
# def check_for_card():
#     uid = pn532.read_passive_target(timeout=0.5)
#     if uid:
#         print("Card detected with UID:", [hex(i) for i in uid])
#         update_message("You have been registered for the event!")
#     root.after(500, check_for_card)  # Repeat check every 500ms
# 
# # Start polling for NFC card scans
# root.after(500, check_for_card)
# 
# # Bind the Escape key to close the application
# root.bind("<Escape>", lambda e: root.destroy())
# 
# # Run the application
# root.mainloop()
