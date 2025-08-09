#!/usr/bin/env python3

import sys
import time
import threading
from typing import Dict, Any, List
from pathlib import Path

# Add pixide to path
sys.path.insert(0, str(Path(__file__).parent / "pixide"))

from chat import SyncChat


class TestSyncChat:
    def __init__(self):
        self.received_messages: List[Dict[str, Any]] = []
        self.message_lock = threading.Lock()
        
    def message_handler(self, message: Dict[str, Any]):
        """Handle incoming messages during testing"""
        with self.message_lock:
            self.received_messages.append(message)
            print(f"📨 Received: {message.get('type')} - {message.get('content', message.get('message', ''))}")
    
    def wait_for_message(self, timeout: float = 3.0, message_type: str = None) -> Dict[str, Any]:
        """Wait for a specific type of message or any message"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self.message_lock:
                if self.received_messages:
                    if message_type is None:
                        return self.received_messages.pop(0)
                    
                    for i, msg in enumerate(self.received_messages):
                        if msg.get('type') == message_type:
                            return self.received_messages.pop(i)
            
            time.sleep(0.1)
        
        raise TimeoutError(f"No {'message' if message_type is None else message_type} received within {timeout}s")
    
    def clear_messages(self):
        """Clear received messages buffer"""
        with self.message_lock:
            self.received_messages.clear()

    def test_connection(self):
        """Test basic connection to localhost:8080"""
        print("\n🔌 Testing connection...")
        
        chat = SyncChat("ws://localhost:8080")
        chat.set_message_handler(self.message_handler)
        
        # Test connection
        connected = chat.connect("test-room")
        assert connected, "Failed to connect to server"
        print("✅ Connected successfully")
        
        # Wait for join confirmation
        join_msg = self.wait_for_message(timeout=3.0, message_type='joined')
        assert join_msg['roomId'] == 'test-room', f"Expected room 'test-room', got {join_msg['roomId']}"
        print(f"✅ Joined room: {join_msg['roomId']}")
        
        chat.disconnect()
        time.sleep(0.5)  # Allow clean disconnect
        print("✅ Disconnected cleanly")
        
        return chat

    def test_messaging(self):
        """Test sending and receiving messages"""
        print("\n💬 Testing messaging...")
        
        chat = SyncChat("ws://localhost:8080")
        chat.set_message_handler(self.message_handler)
        
        # Connect and join room
        connected = chat.connect("messaging-test")
        assert connected, "Failed to connect"
        
        # Wait for join confirmation and clear messages
        self.wait_for_message(message_type='joined')
        self.clear_messages()
        
        # Send a test message
        test_message = "Hello from SyncChat test!"
        chat.send_message(test_message)
        
        # Wait for the message to be echoed back
        echo_msg = self.wait_for_message(timeout=3.0, message_type='chat_message')
        assert echo_msg['content'] == test_message, f"Message content mismatch: {echo_msg['content']}"
        assert echo_msg['userId'] == chat.get_user_id(), "User ID mismatch in echoed message"
        
        print(f"✅ Message sent and received: '{test_message}'")
        
        chat.disconnect()
        time.sleep(0.5)

    def test_room_switching(self):
        """Test switching between rooms"""
        print("\n🏠 Testing room switching...")
        
        chat = SyncChat("ws://localhost:8080")
        chat.set_message_handler(self.message_handler)
        
        # Connect to initial room
        connected = chat.connect("room1")
        assert connected, "Failed to connect"
        
        # Wait for join confirmation
        join_msg = self.wait_for_message(message_type='joined')
        assert join_msg['roomId'] == 'room1', "Failed to join room1"
        print(f"✅ Joined initial room: {join_msg['roomId']}")
        
        # Switch to different room
        self.clear_messages()
        chat.switch_room("room2")
        
        # Wait for new join confirmation
        join_msg2 = self.wait_for_message(timeout=3.0, message_type='joined')
        assert join_msg2['roomId'] == 'room2', f"Expected room2, got {join_msg2['roomId']}"
        print(f"✅ Switched to room: {join_msg2['roomId']}")
        
        # Verify current room is updated
        assert chat.get_current_room() == 'room2', "Current room not updated after switch"
        
        chat.disconnect()
        time.sleep(0.5)

    def test_user_id_persistence(self):
        """Test that user ID is consistent"""
        print("\n👤 Testing user ID...")
        
        chat1 = SyncChat("ws://localhost:8080")
        user_id1 = chat1.get_user_id()
        print(f"✅ User ID 1: {user_id1}")
        
        chat2 = SyncChat("ws://localhost:8080")
        user_id2 = chat2.get_user_id()
        print(f"✅ User ID 2: {user_id2}")
        
        # User IDs should be the same (loaded from file)
        assert user_id1 == user_id2, f"User IDs should match: {user_id1} != {user_id2}"
        print("✅ User ID persistence confirmed")

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        print("\n❌ Testing error handling...")
        
        chat = SyncChat("ws://localhost:8080")
        chat.set_message_handler(self.message_handler)
        
        # Try sending message without connecting
        chat.send_message("This should not work")
        print("✅ Handled disconnected send gracefully")
        
        # Try switching room without connecting
        chat.switch_room("invalid")
        print("✅ Handled disconnected room switch gracefully")

    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting SyncChat tests...")
        print(f"🎯 Target server: ws://localhost:8080")
        
        try:
            self.test_connection()
            self.test_messaging()
            self.test_room_switching()
            self.test_user_id_persistence()
            self.test_error_handling()
            
            print("\n🎉 All SyncChat tests passed!")
            return True
            
        except Exception as e:
            print(f"\n💥 Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    tester = TestSyncChat()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)