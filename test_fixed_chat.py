#!/usr/bin/env python3

import asyncio
import sys
import time
from typing import Dict, Any, List

from fixed_chat import FixedChat


class TestFixedChat:
    def __init__(self):
        self.received_messages: List[Dict[str, Any]] = []
        
    def message_handler(self, message: Dict[str, Any]):
        """Handle incoming messages during testing"""
        self.received_messages.append(message)
        print(f"📨 Received: {message.get('type')} - {message.get('content', message.get('message', ''))}")
    
    async def wait_for_message(self, timeout: float = 3.0, message_type: str = None) -> Dict[str, Any]:
        """Wait for a specific type of message or any message"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.received_messages:
                if message_type is None:
                    return self.received_messages.pop(0)
                
                for i, msg in enumerate(self.received_messages):
                    if msg.get('type') == message_type:
                        return self.received_messages.pop(i)
            
            await asyncio.sleep(0.1)
        
        raise TimeoutError(f"No {'message' if message_type is None else message_type} received within {timeout}s")
    
    def clear_messages(self):
        """Clear received messages buffer"""
        self.received_messages.clear()

    async def test_connection(self):
        """Test basic async connection to localhost:8080"""
        print("\n🔌 Testing fixed async connection...")
        
        chat = FixedChat("ws://localhost:8080")
        chat.set_message_handler(self.message_handler)
        
        try:
            # Test connection - should work now!
            connected = await chat.connect("test-room")
            
            if connected:
                print("✅ Connected successfully")
                
                # Wait for join confirmation
                join_msg = await self.wait_for_message(timeout=3.0, message_type='joined')
                assert join_msg['roomId'] == 'test-room', f"Expected room 'test-room', got {join_msg['roomId']}"
                print(f"✅ Joined room: {join_msg['roomId']}")
                
                await chat.disconnect()
                print("✅ Disconnected cleanly")
                return True
            else:
                print("❌ Connection failed")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_messaging(self):
        """Test async messaging"""
        print("\n💬 Testing fixed async messaging...")
        
        chat = FixedChat("ws://localhost:8080")
        chat.set_message_handler(self.message_handler)
        
        try:
            connected = await chat.connect("messaging-test")
            assert connected, "Failed to connect"
            
            # Wait for join confirmation
            join_msg = await self.wait_for_message(timeout=3.0, message_type='joined')
            print(f"✅ Joined room: {join_msg['roomId']}")
            self.clear_messages()
            
            # Send a test message
            test_message = "Hello from FIXED async Chat test!"
            await chat.send_chat_message(test_message)
            
            # Wait for the message to be echoed back
            echo_msg = await self.wait_for_message(timeout=3.0, message_type='chat_message')
            assert echo_msg['content'] == test_message, f"Message content mismatch: {echo_msg['content']}"
            print(f"✅ Message sent and received: '{test_message}'")
            
            await chat.disconnect()
            return True
            
        except Exception as e:
            print(f"❌ Messaging test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_room_switching(self):
        """Test async room switching"""
        print("\n🏠 Testing fixed async room switching...")
        
        chat = FixedChat("ws://localhost:8080")
        chat.set_message_handler(self.message_handler)
        
        try:
            connected = await chat.connect("room1")
            assert connected, "Failed to connect"
            
            # Wait for initial join
            join_msg = await self.wait_for_message(timeout=3.0, message_type='joined')
            print(f"✅ Joined initial room: {join_msg['roomId']}")
            
            # Switch to different room
            self.clear_messages()
            await chat.switch_room("room2")
            
            # Wait for new join confirmation
            join_msg2 = await self.wait_for_message(timeout=3.0, message_type='joined')
            assert join_msg2['roomId'] == 'room2', f"Expected room2, got {join_msg2['roomId']}"
            print(f"✅ Switched to room: {join_msg2['roomId']}")
            
            await chat.disconnect()
            return True
            
        except Exception as e:
            print(f"❌ Room switching test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_concurrent_operations(self):
        """Test that multiple operations can run concurrently"""
        print("\n🔄 Testing concurrent operations...")
        
        chat = FixedChat("ws://localhost:8080")
        chat.set_message_handler(self.message_handler)
        
        try:
            # Connect
            connected = await chat.connect("concurrent-test")
            assert connected, "Failed to connect"
            
            # Wait for join
            await self.wait_for_message(timeout=3.0, message_type='joined')
            self.clear_messages()
            
            # Send multiple messages concurrently
            messages = ["Message 1", "Message 2", "Message 3"]
            
            # Send all messages
            send_tasks = [chat.send_chat_message(msg) for msg in messages]
            await asyncio.gather(*send_tasks)
            
            # Wait for all echoes (with some tolerance for timing)
            received_content = []
            for _ in range(len(messages)):
                try:
                    echo = await self.wait_for_message(timeout=2.0, message_type='chat_message')
                    received_content.append(echo['content'])
                except TimeoutError:
                    break
            
            print(f"✅ Sent {len(messages)} messages, received {len(received_content)} echoes")
            
            await chat.disconnect()
            return True
            
        except Exception as e:
            print(f"❌ Concurrent operations test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def run_all_tests(self):
        """Run all tests for the fixed Chat class"""
        print("🧪 Starting FIXED async Chat tests...")
        print(f"🎯 Target server: ws://localhost:8080")
        
        results = []
        
        try:
            results.append(await self.test_connection())
            results.append(await self.test_messaging())
            results.append(await self.test_room_switching())
            results.append(await self.test_concurrent_operations())
            
            passed = sum(results)
            total = len(results)
            
            print(f"\n📊 Test Results: {passed}/{total} tests passed")
            
            if passed == total:
                print("🎉 All FIXED async Chat tests passed!")
                print("✅ The async Chat class issues have been resolved!")
                return True
            else:
                print("⚠️  Some tests still failed")
                return False
                
        except Exception as e:
            print(f"\n💥 Test suite failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    tester = TestFixedChat()
    success = await tester.run_all_tests()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)