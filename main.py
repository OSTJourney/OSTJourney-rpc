import asyncio
import websockets
from dotenv import load_dotenv
import json
import time
import os
from pypresence import AioPresence, ActivityType

# Load environment variables\load_dotenv()
load_dotenv()

CLIENT_ID = os.getenv("RPC_CLIENT_ID")
PORT = int(os.getenv("WEB_SOCKET_PORT", 4242))
IMG_DOMAIN = os.getenv("IMG_DOMAIN", "https://ostjourney.xyz/")

# Create the async RPC client
rpc = AioPresence(CLIENT_ID)

current_song = {
	"title": None,
	"artist": None,
	"image": None,
	"link": None,
	"duration": None,
	"paused": False,
	"start_time": None,
	"paused_time": None,
}


async def handler(websocket):
	global current_song

	async for message in websocket:
		try:
			payload = json.loads(message)
			print("Received payload:", payload)

			paused = payload.get("paused")
			title = payload.get("title")
			artist = payload.get("artist")
			image = payload.get("image")
			link = payload.get("link")
			duration = payload.get("duration")

			# Prepend domain to image path if needed
			if image and not image.startswith("http"):
				image = IMG_DOMAIN + image

			# Initialize new song on metadata change
			if title and artist and image and duration:
				current_song = {
					"title": title,
					"artist": artist,
					"image": image,
					"link": link,
					"duration": duration,
					"paused": False,
					"start_time": int(time.time()),
					"paused_time": None,
				}

			# Handle pause/resume
			if paused is not None:
				current_song['paused'] = paused
				if paused:
					current_song['paused_time'] = int(time.time())
					await rpc.clear()
					await websocket.send("paused")
				else:
					# Reset start time on resume
					if current_song['paused_time'] is not None:
						time_diff = int(time.time()) - current_song['paused_time']
						current_song['start_time'] += time_diff
						current_song['paused_time'] = None
					await rpc.update(
						activity_type = ActivityType.LISTENING,
						details=current_song['title'],
						state=current_song['artist'],
						start=current_song['start_time'],
						end=current_song['start_time'] + current_song['duration'],
						large_image=current_song['image'],
						large_text="OST Journey",
						buttons=[{"label": "Listen", "url": current_song['link']}]
					)
					await websocket.send("updated")
			else:
				await websocket.send("invalid")

		except websockets.ConnectionClosed:
			print("Client disconnected")
			break
		except Exception as e:
			# Send error back to client
			await websocket.send(f"error: {e}")

async def main():
	# Connect to Discord RPC
	await rpc.connect()
	print(f"Connected to Discord RPC (client id: {CLIENT_ID})")

	# Start WebSocket server
	async with websockets.serve(handler, 'localhost', PORT):
		print(f"WebSocket RPC Server running on ws://localhost:{PORT}")
		await asyncio.Future()  # Run forever

if __name__ == "__main__":
	asyncio.run(main())
