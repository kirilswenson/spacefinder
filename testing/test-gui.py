import tkinter as tk
from tkinter import font
import RPi.GPIO as GPIO

from pn532 import *

# Create the main application window
root = tk.Tk()
root.title("SpaceFinder")

# Set fullscreen mode
root.attributes('-fullscreen', False)

# Set the background color
root.configure(bg="black")

# Add welcome message
welcome_label = tk.Label(root, text="Welcome to SpaceFinder!", fg="white", bg="black")
welcome_label_font = font.Font(family="Helvetica", size=36, weight="bold")
welcome_label.config(font=welcome_label_font)
welcome_label.pack(pady=50)

# Add instruction message
instruction_label = tk.Label(root, text="Please scan your U-Card to buzz yourself in.", fg="white", bg="black")
instruction_label_font = font.Font(family="Helvetica", size=24)
instruction_label.config(font=instruction_label_font)
instruction_label.pack(pady=20)


pn532 = PN532_SPI(debug=False, reset=20, cs=4)
ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

def update_message(new_message):
    instruction_label.config(text=new_message)
    root.update_idletasks()  # Update display immediately

# Poll for card detection
def check_for_card():
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        print("Card detected with UID:", [hex(i) for i in uid])
        update_message("You have been registered for the event!")
    root.after(500, check_for_card)  # Repeat check every 500ms

# Start polling for NFC card scans
root.after(500, check_for_card)


# Bind the Escape key to close the application
root.bind("<Escape>", lambda e: root.destroy())

# Run the application
root.mainloop()
