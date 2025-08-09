import asyncio
import json
import uuid
import websockets
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import threading
import time


class Chat:
    """
    WebSocket chat client for PixIDE.
    Handles connection to Fly.io chat server with room management.
    """
    
    def __init__(self, server_url: str = "wss://pixide-chat-server.fly.dev"):
        self.server_url = server_url
        self.user_id: Optional[str] = None
        self.current_room: Optional[str] = None
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.message_handler: Optional[Callable[[Dict[str, Any]], None]] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._running = False
        
        # Load or generate user ID
        self._load_or_create_user_id()
    
    def _load_or_create_user_id(self):
        """Load user ID from file or create a new one."""
        user_file = Path.home() / ".pixide_user_id"
        
        if user_file.exists():
            try:
                self.user_id = user_file.read_text().strip()
                print(f"Loaded user ID: {self.user_id}")
            except Exception as e:
                print(f"Error loading user ID: {e}")
                self.user_id = None
        
        if not self.user_id:
            self.user_id = f"user_{uuid.uuid4().hex[:8]}"
            try:
                user_file.write_text(self.user_id)
                print(f"Created new user ID: {self.user_id}")
            except Exception as e:
                print(f"Error saving user ID: {e}")
    
    def set_message_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Set callback function to handle incoming messages."""
        self.message_handler = handler
    
    async def connect(self, room_id: Optional[str] = None) -> bool:
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
            
            # Start message listener
            await self._listen_for_messages()
            
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
            return False
        
        return True
    
    async def _join_room(self, room_id: str):
        """Join a specific room."""
        message = {
            "type": "join",
            "userId": self.user_id,
            "roomId": room_id
        }
        
        await self._send_message(message)
        self.current_room = room_id
        print(f"Joining room: {room_id}")
    
    async def switch_room(self, room_id: str):
        """Switch to a different room."""
        if not self.connected:
            print("Not connected to server")
            return False
        
        message = {
            "type": "switch_room",
            "userId": self.user_id,
            "roomId": room_id
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
        
        message = {
            "type": "chat_message",
            "userId": self.user_id,
            "content": content
        }
        
        await self._send_message(message)
        return True
    
    async def _send_message(self, message: Dict[str, Any]):
        """Send a message through the WebSocket."""
        if self.websocket and self.connected:
            await self.websocket.send(json.dumps(message))
    
    async def _listen_for_messages(self):
        """Listen for incoming messages from the server."""
        try:
            while self.connected and self.websocket:
                message_data = await self.websocket.recv()
                message = json.loads(message_data)
                
                # Handle message internally
                await self._handle_message(message)
                
                # Call external handler if set
                if self.message_handler:
                    self.message_handler(message)
                    
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server")
            self.connected = False
        except Exception as e:
            print(f"Error receiving message: {e}")
            self.connected = False
    
    async def _handle_message(self, message: Dict[str, Any]):
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
                time_str = timestamp.split('T')[1][:8] if timestamp else ""
                print(f"[{time_str}] {user}: {content}")
    
    async def disconnect(self):
        """Disconnect from the chat server."""
        self.connected = False
        if self.websocket:
            await self.websocket.close()
        print("Disconnected from chat server")
    
    def get_user_id(self) -> str:
        """Get the current user ID."""
        return self.user_id or "unknown"
    
    def get_current_room(self) -> Optional[str]:
        """Get the current room ID."""
        return self.current_room
    
    def is_connected(self) -> bool:
        """Check if connected to the server."""
        return self.connected


# Synchronous wrapper for easier use
class SyncChat:
    """Synchronous wrapper for the Chat class."""
    
    def __init__(self, server_url: str = "wss://pixide-chat-server.fly.dev"):
        self.chat = Chat(server_url)
        self.thread: Optional[threading.Thread] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
    
    def connect(self, room_id: Optional[str] = None) -> bool:
        """Connect to chat server synchronously."""
        def run_chat():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.chat.connect(room_id))
        
        self.thread = threading.Thread(target=run_chat, daemon=True)
        self.thread.start()
        
        # Wait a moment for connection
        time.sleep(1)
        return self.chat.is_connected()
    
    def send_message(self, content: str):
        """Send message synchronously."""
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self.chat.send_chat_message(content), self.loop
            )
    
    def switch_room(self, room_id: str):
        """Switch room synchronously."""
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self.chat.switch_room(room_id), self.loop
            )
    
    def disconnect(self):
        """Disconnect synchronously."""
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.chat.disconnect(), self.loop)
    
    def set_message_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Set message handler."""
        self.chat.set_message_handler(handler)
    
    def get_user_id(self) -> str:
        return self.chat.get_user_id()
    
    def get_current_room(self) -> Optional[str]:
        return self.chat.get_current_room()
    
    def is_connected(self) -> bool:
        return self.chat.is_connected()