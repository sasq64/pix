#!/usr/bin/env python3
"""
Command-line test interface for PixIDE chat functionality.
Usage: python chat_test.py [server_url]
"""

import asyncio
import sys
import threading
from typing import Dict, Any
from pixide.chat import Chat


class ChatTestInterface:
    """Interactive command-line chat interface."""
    
    def __init__(self, server_url: str = "ws://localhost:8080"):
        self.chat = Chat(server_url)
        self.running = False
        self.chat.set_message_handler(self._handle_message)
    
    def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming messages (already handled by Chat class)."""
        pass  # Chat class handles printing, we just need this for the callback
    
    async def start(self):
        """Start the chat interface."""
        print("=" * 50)
        print("PixIDE Chat Test Interface")
        print("=" * 50)
        print(f"Your User ID: {self.chat.get_user_id()}")
        print(f"Server: {self.chat.server_url}")
        print()
        print("Commands:")
        print("  /join <room_id> - Switch to a different room")
        print("  /whoami         - Show your user ID and current room")
        print("  /help           - Show this help")
        print("  /quit           - Exit the chat")
        print("  <message>       - Send a message to the current room")
        print("=" * 50)
        
        # Connect to server
        print("Connecting to server...")
        success = await self.chat.connect()
        
        if not success:
            print("Failed to connect to server. Exiting.")
            return
        
        print(f"Connected! You're in room: {self.chat.get_current_room()}")
        print("Type messages or commands:")
        print()
        
        self.running = True
        
        # Start input handler in separate thread
        input_thread = threading.Thread(target=self._input_handler, daemon=True)
        input_thread.start()
        
        # Keep the async loop running
        try:
            while self.running:
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            print("\nReceived Ctrl+C, shutting down...")
        finally:
            await self._shutdown()
    
    def _input_handler(self):
        """Handle user input in a separate thread."""
        while self.running:
            try:
                user_input = input().strip()
                print(user_input)
                
                if not user_input:
                    continue
                
                if user_input.startswith('/'):
                    asyncio.create_task(self._handle_command(user_input))
                else:
                    asyncio.create_task(self._send_message(user_input))
                    
            except (EOFError, KeyboardInterrupt):
                self.running = False
                break
            except Exception as e:
                print(f"Input error: {e}")
    
    async def _handle_command(self, command: str):
        """Handle chat commands."""
        parts = command[1:].split(' ', 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == 'quit' or cmd == 'exit':
            print("Goodbye!")
            self.running = False
            
        elif cmd == 'join':
            if not args:
                print("Usage: /join <room_id>")
                return
            
            room_id = args.strip()
            print(f"Switching to room: {room_id}")
            await self.chat.switch_room(room_id)
            
        elif cmd == 'whoami':
            print(f"User ID: {self.chat.get_user_id()}")
            print(f"Current room: {self.chat.get_current_room()}")
            print(f"Connected: {self.chat.is_connected()}")
            
        elif cmd == 'help':
            print("\nCommands:")
            print("  /join <room_id> - Switch to a different room")
            print("  /whoami         - Show your user ID and current room")
            print("  /help           - Show this help")
            print("  /quit           - Exit the chat")
            print("  <message>       - Send a message to the current room")
            print()
            
        else:
            print(f"Unknown command: /{cmd}")
            print("Type /help for available commands")
    
    async def _send_message(self, content: str):
        """Send a chat message."""
        if not self.chat.is_connected():
            print("Not connected to server!")
            return
        
        # Echo our own message locally
        print(f"[You]: {content}")
        await self.chat.send_chat_message(content)
    
    async def _shutdown(self):
        """Clean shutdown."""
        self.running = False
        if self.chat.is_connected():
            await self.chat.disconnect()


async def main():
    """Main entry point."""
    server_url = "ws://localhost:8080"  # Default to local development
    
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    
    # If no protocol specified, assume WebSocket
    if not server_url.startswith(('ws://', 'wss://')):
        server_url = f"ws://{server_url}"
    
    interface = ChatTestInterface(server_url)
    
    try:
        await interface.start()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("Starting chat test interface...")
    print("Note: Make sure the chat server is running!")
    print("For local testing: node server/app.js")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
