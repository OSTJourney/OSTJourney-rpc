import asyncio
import websockets
from dotenv import load_dotenv
import json
import time
import os
from pypresence import AioPresence, ActivityType

# Load environment variables
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

async def reconnectRpc():
	while True:
		try:
			await rpc.connect()
			print("Connected to Discord RPC")
			break
		except Exception as e:
			print(f"Failed to connect to Discord RPC: {e}. Retrying in 10 seconds...")
			await asyncio.sleep(10)

async def safeClear():
	try:
		await rpc.clear()
	except Exception as e:
		print(f"RPC clear failed: {e}. Attempting reconnect...")
		await reconnectRpc()

async def safeUpdate():
	try:
		link = current_song['link']
		if not link or not link.startswith("http"):
			link = "https://ostjourney.xyz/"

		await rpc.update(
			activity_type=ActivityType.LISTENING,
			details=current_song['title'],
			state=current_song['artist'],
			start=current_song['start_time'],
			end=current_song['start_time'] + current_song['duration'],
			large_image=current_song['image'],
			large_text="OST Journey",
			buttons=[{"label": "Listen", "url": link}]
		)
	except Exception as e:
		print(f"RPC update failed: {e}. Attempting reconnect...")
		await reconnectRpc()


async def handler(websocket):
	global current_song

	async for message in websocket:
		try:
			payload = json.loads(message)
			print("Received payload:", payload)

			# Data extraction
			paused = payload.get("paused")
			title = payload.get("title")
			artist = payload.get("artist")
			image = payload.get("cover")
			link = payload.get("link")
			duration = payload.get("duration")
			current_time = payload.get("currentTime")

			# If image is a relative path, prepend the domain
			if image and not image.startswith("http"):
				image = IMG_DOMAIN + image

			# Handle new song with optional currentTime
			if title and artist and image and duration:
				start_time = int(time.time())

				if isinstance(current_time, (int, float)) and current_time >= 0:
					start_time -= int(current_time)

				current_song = {
					"title": title,
					"artist": artist,
					"image": image,
					"link": link,
					"duration": duration,
					"paused": paused if paused is not None else False,
					"start_time": start_time,
					"paused_time": None,
				}

				if current_song['paused']:
					await safeClear()
				else:
					await safeUpdate()

				continue

			# Handle seek update only
			if isinstance(current_time, (int, float)) and current_time >= 0:
				current_song["start_time"] = int(time.time()) - int(current_time)
				await safeUpdate()
				continue

			# Handle pause/resume
			if paused is not None:
				current_song['paused'] = paused
				if paused:
					current_song['paused_time'] = int(time.time())
					await safeClear()
				else:
					if current_song['paused_time'] is not None:
						time_diff = int(time.time()) - current_song['paused_time']
						current_song['start_time'] += time_diff
						current_song['paused_time'] = None
					await safeUpdate()
				continue


		except websockets.ConnectionClosed:
			print("Client disconnected")
			break
		except Exception as e:
			print(f"Error: {e}")

async def main():
	await reconnectRpc()
	async with websockets.serve(handler, 'localhost', PORT):
		print(f"WebSocket RPC Server running on ws://localhost:{PORT}")
		await asyncio.Future()  # Run forever

if __name__ == "__main__":
	asyncio.run(main())
