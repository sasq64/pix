import asyncio
import json
import queue
import threading
import uuid
import websockets
from pathlib import Path
from typing import Callable, Literal, NotRequired, TypedDict

MsgType = Literal[
    "joined", "error", "join", "user_joined", "user_left", "switch_room", "chat_message"
]


class Message(TypedDict):
    type: MsgType
    userId: str
    roomId: NotRequired[str]
    content: NotRequired[str]


class Chat:
    """
    Fixed version of the WebSocket chat client for PixIDE.
    Handles connection to chat server with proper async management.
    """

    def __init__(self, server_url: str = "wss://pixide-chat-server.fly.dev"):
        self.server_url = server_url
        self.user_id: str = self._load_or_create_user_id()
        self.current_room: str | None = None
        self.websocket: websockets.ClientConnection | None = None
        self.connected = False
        self.message_handler: Callable[[Message], None] | None = None
        self.listener_task: asyncio.Task[None] | None = None

        # Threading support
        self.message_queue: queue.Queue[Message] = queue.Queue()
        self.chat_thread: threading.Thread | None = None
        self.chat_loop: asyncio.AbstractEventLoop | None = None
        self.threaded_enabled = False

    def _load_or_create_user_id(self) -> str:
        """Load user ID from file or create a new one."""
        user_file = Path.home() / ".pixide_user_id"
        id: str | None = None

        if user_file.exists():
            try:
                id = user_file.read_text().strip()
                print(f"Loaded user ID: {id}")
            except Exception as e:
                print(f"Error loading user ID: {e}")

        if not id:
            id = f"user_{uuid.uuid4().hex[:8]}"
            try:
                user_file.write_text(id)
                print(f"Created new user ID: {id}")
            except Exception as e:
                print(f"Error saving user ID: {e}")
        return id

    def set_message_handler(self, handler: Callable[[Message], None]):
        """Set callback function to handle incoming messages."""
        self.message_handler = handler

    async def connect(self, room_id: str | None = None) -> bool:
        """
        Connect to the chat server and join a room.
        If no room_id provided, joins user's own room.
        """
        try:
            print(f"Connecting to {self.server_url}...")
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True
            print("Connected to chat server")

            # Join room (defaults to user's own room)
            target_room = room_id or self.user_id
            await self._join_room(target_room)

            # Start message listener in background (KEY FIX!)
            self.listener_task = asyncio.create_task(self._listen_for_messages())

            # Wait briefly for join confirmation
            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
            return False

        return True

    async def _join_room(self, room_id: str):
        """Join a specific room."""
        message: Message = {"type": "join", "userId": self.user_id, "roomId": room_id}

        await self._send_message(message)
        self.current_room = room_id
        print(f"Joining room: {room_id}")

    async def switch_room(self, room_id: str):
        """Switch to a different room."""
        if not self.connected:
            print("Not connected to server")
            return False

        message: Message = {
            "type": "switch_room",
            "userId": self.user_id,
            "roomId": room_id,
        }

        await self._send_message(message)
        self.current_room = room_id
        print(f"Switching to room: {room_id}")
        return True

    async def send_chat_message(self, content: str):
        """Send a chat message to the current room."""
        if not self.connected:
            print("Not connected to server")
            return False

        message: Message = {
            "type": "chat_message",
            "userId": self.user_id,
            "content": content,
        }

        await self._send_message(message)
        return True

    async def _send_message(self, message: Message):
        """Send a message through the WebSocket."""
        if self.websocket and self.connected:
            await self.websocket.send(json.dumps(message))

    async def _listen_for_messages(self):
        """Listen for incoming messages from the server."""
        try:
            while self.connected and self.websocket:
                message_data = await self.websocket.recv()
                message: Message = json.loads(message_data)

                # Handle message internally
                await self._handle_message(message)

                # Call external handler if set
                if self.message_handler:
                    self.message_handler(message)

        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server")
            self.connected = False
        except asyncio.CancelledError:
            print("Message listener cancelled")
        except Exception as e:
            print(f"Error receiving message: {e}")
            self.connected = False

    async def _handle_message(self, message: Message):
        """Handle incoming messages internally."""
        msg_type = message.get("type")

        if msg_type == "joined":
            self.current_room = message.get("roomId")
            print(f"✓ {message.get('message', 'Joined room')}")

        elif msg_type == "error":
            print(f"Error: {message.get('message', 'Unknown error')}")

        elif msg_type == "user_joined":
            user = message.get("userId")
            if user != self.user_id:  # Don't show our own join
                print(f"+ {user} joined the room")

        elif msg_type == "user_left":
            user = message.get("userId")
            print(f"- {user} left the room")

        elif msg_type == "chat_message":
            user = message.get("userId")
            content = message.get("content")
            timestamp = message.get("timestamp", "")

            # Don't echo our own messages
            if user != self.user_id:
                time_str = timestamp.split("T")[1][:8] if timestamp else ""
                print(f"[{time_str}] {user}: {content}")

    async def disconnect(self):
        """Disconnect from the chat server."""
        self.connected = False

        # Cancel listener task (KEY FIX!)
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass

        if self.websocket:
            await self.websocket.close()
        print("Disconnected from chat server")

    def get_user_id(self) -> str:
        """Get the current user ID."""
        return self.user_id or "unknown"

    def get_current_room(self) -> str | None:
        """Get the current room ID."""
        return self.current_room

    def is_connected(self) -> bool:
        """Check if connected to the server."""
        return self.connected

    # Threaded API methods
    def start_threaded(self, room_id: str | None = None):
        """Start chat functionality in a dedicated thread."""
        if self.threaded_enabled:
            return

        self.threaded_enabled = True
        self.chat_thread = threading.Thread(
            target=self._run_chat_thread, args=(room_id,), daemon=True
        )
        self.chat_thread.start()

    def stop_threaded(self):
        """Stop threaded chat functionality and cleanup."""
        if not self.threaded_enabled:
            return

        self.threaded_enabled = False

        if self.chat_loop and not self.chat_loop.is_closed():
            # Schedule disconnect in the chat thread's event loop
            asyncio.run_coroutine_threadsafe(
                self._threaded_disconnect(), self.chat_loop
            )

        if self.chat_thread:
            self.chat_thread.join(timeout=2.0)

    def send_message_threaded(self, content: str):
        """Send a chat message from main thread when using threaded mode."""
        if not self.threaded_enabled or not self.chat_loop:
            print("Threaded chat not enabled")
            return

        # Schedule the async send in the chat thread
        try:
            future = asyncio.run_coroutine_threadsafe(
                self._threaded_send_message(content), self.chat_loop
            )
            # Don't wait for result to avoid blocking main thread
        except Exception as e:
            print(f"Failed to send chat message: {e}")

    def get_messages(self) -> list[Message]:
        """Get all pending messages from the queue (non-blocking)."""
        messages: list[Message] = []
        while not self.message_queue.empty():
            try:
                message = self.message_queue.get_nowait()
                messages.append(message)
            except queue.Empty:
                break
        return messages

    def _run_chat_thread(self, room_id: str | None):
        """Run the chat functionality in a dedicated thread with its own event loop."""
        try:
            # Create new event loop for this thread
            self.chat_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.chat_loop)

            # Run the async chat logic
            self.chat_loop.run_until_complete(self._threaded_main(room_id))
        except Exception as e:
            print(f"Chat thread error: {e}")
        finally:
            if self.chat_loop:
                try:
                    self.chat_loop.close()
                except:
                    pass

    async def _threaded_main(self, room_id: str | None):
        """Main chat async function - runs in dedicated thread."""
        try:
            # Set up a message handler that puts messages in the queue
            original_handler = self.message_handler
            self.set_message_handler(self._queue_message_handler)

            # Connect to chat server
            connected = await self.connect(room_id)
            if not connected:
                print("Failed to connect to chat server")
                return

            print(f"Connected to chat room: {self.get_current_room()}")

            # Keep the connection alive while threaded mode is enabled
            while self.threaded_enabled and self.is_connected():
                await asyncio.sleep(0.1)

            # Restore original handler
            self.message_handler = original_handler

        except Exception as e:
            print(f"Chat connection error: {e}")

    async def _threaded_disconnect(self):
        """Disconnect from chat server in threaded mode."""
        await self.disconnect()

    async def _threaded_send_message(self, content: str):
        """Send chat message in threaded mode."""
        await self.send_chat_message(content)

    def _queue_message_handler(self, message: Message):
        """Message handler that puts messages in queue for main thread."""
        try:
            self.message_queue.put_nowait(message)
        except queue.Full:
            print("Chat message queue is full, dropping message")
