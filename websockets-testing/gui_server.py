import tkinter as tk
import asyncio
import websockets

# WebSocket URL
WEBSOCKET_URL = "ws://localhost:8765"  # Replace with your WebSocket server URL

# Function to send a message via WebSocket
async def send_message():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await websocket.send("pressed")
        print("Message sent: 'pressed'")

# Tkinter button callback
def on_button_press():
    asyncio.run(send_message())  # Run the WebSocket message in the event loop

# Tkinter GUI setup
root = tk.Tk()
root.title("Simple WebSocket Sender")

button = tk.Button(root, text="Press Me", command=on_button_press)
button.pack(pady=20)

root.mainloop()

