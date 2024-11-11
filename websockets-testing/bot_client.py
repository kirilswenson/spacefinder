import discord
import asyncio
import websockets
from ../config import TOKEN

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

async def listen():
    print("Connecting to WebSocket server...")
    async with websockets.connect("ws://localhost:5678") as websocket:
        while True:
            message = await websocket.recv()
            if message == "button_pressed":
                # Send message to Discord channel when button is pressed
                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    await channel.send("Button was pressed in the GUI!")


async def start():
    print("Starting Discord client...")
    # Start the Discord client
    await client.start(TOKEN)

# Run the bot
loop = asyncio.get_event_loop()
loop.create_task(start())
loop.create_task(listen())
loop.run_forever()

