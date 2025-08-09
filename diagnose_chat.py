#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add pixide to path
sys.path.insert(0, str(Path(__file__).parent / "pixide"))

from chat import Chat


async def diagnose_connect_method():
    """Diagnose the connect method issue"""
    print("🔍 Diagnosing Chat.connect() method...")
    
    chat = Chat("ws://localhost:8080")
    
    print("Chat object created")
    print(f"Server URL: {chat.server_url}")
    print(f"User ID: {chat.user_id}")
    print(f"Connected: {chat.connected}")
    
    # The issue is likely in the connect method - it calls _listen_for_messages()
    # which runs an infinite loop, blocking the coroutine
    print("\n❌ IDENTIFIED ISSUE:")
    print("The Chat.connect() method calls await self._listen_for_messages()")
    print("which contains 'while self.connected and self.websocket:' infinite loop")
    print("This blocks the connect() coroutine and never returns!")
    
    return False


async def test_fixed_approach():
    """Test a working approach by manually managing the connection"""
    print("\n🔧 Testing manual connection management...")
    
    import websockets
    import json
    
    try:
        # Direct WebSocket connection
        websocket = await websockets.connect("ws://localhost:8080")
        print("✅ WebSocket connected directly")
        
        # Send join message
        join_message = {
            "type": "join",
            "userId": "diagnostic-user",
            "roomId": "diagnostic-room"
        }
        
        await websocket.send(json.dumps(join_message))
        print("✅ Join message sent")
        
        # Receive join confirmation
        response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
        message = json.loads(response)
        print(f"✅ Received: {message}")
        
        # Send chat message
        chat_message = {
            "type": "chat_message",
            "userId": "diagnostic-user",
            "content": "Diagnostic test message"
        }
        
        await websocket.send(json.dumps(chat_message))
        print("✅ Chat message sent")
        
        # Receive echo
        response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
        echo = json.loads(response)
        print(f"✅ Echo received: {echo}")
        
        # Clean disconnect
        await websocket.close()
        print("✅ Disconnected cleanly")
        
        return True
        
    except Exception as e:
        print(f"❌ Manual test failed: {e}")
        return False


async def suggest_fixes():
    """Suggest fixes for the Chat class"""
    print("\n💡 SUGGESTED FIXES for Chat class:")
    print()
    print("1. MAIN ISSUE: connect() method blocks indefinitely")
    print("   - The _listen_for_messages() call should run in background")
    print("   - Use asyncio.create_task() to run listener concurrently")
    print()
    print("2. Separate connection from message listening:")
    print("   async def connect(self, room_id=None):")
    print("       # Connect to WebSocket")
    print("       # Join room") 
    print("       # Start listener task (don't await it)")
    print("       # Return True/False")
    print()
    print("3. Store listener task for proper cleanup:")
    print("   self.listener_task = asyncio.create_task(self._listen_for_messages())")
    print()
    print("4. Update disconnect() to cancel listener task:")
    print("   if self.listener_task:")
    print("       self.listener_task.cancel()")


async def main():
    print("🧪 Diagnosing async Chat class issues...")
    
    # Diagnose the main issue
    await diagnose_connect_method()
    
    # Test working approach
    success = await test_fixed_approach()
    
    # Suggest fixes
    await suggest_fixes()
    
    if success:
        print("\n✅ Direct WebSocket communication works fine")
        print("❌ The issue is in Chat class architecture")
    else:
        print("\n❌ Even direct WebSocket communication failed")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)