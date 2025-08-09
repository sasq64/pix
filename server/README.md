# PixIDE Chat Server

WebSocket-based chat server for PixIDE, designed to run on Fly.io.

## Features

- Real-time WebSocket communication
- Room-based messaging system
- User management with persistent IDs
- Automatic room creation and cleanup
- Health check endpoint

## Local Development

1. Install dependencies:
```bash
cd server
npm install
```

2. Start the server:
```bash
npm start
```

The server will run on `http://localhost:8080` by default.

## Deployment to Fly.io

1. Install Fly CLI: https://fly.io/docs/getting-started/installing-flyctl/

2. Login to Fly.io:
```bash
fly auth login
```

3. Deploy the application:
```bash
cd server
fly launch
```

Follow the prompts to configure your app name, region, etc.

4. For subsequent deployments:
```bash
fly deploy
```

## API Endpoints

### WebSocket: `/`
Main WebSocket endpoint for chat communication.

### HTTP: `GET /`
Health check endpoint returning server status.

## WebSocket Message Format

All messages are JSON objects with the following structure:

### Client to Server Messages

**Join Room:**
```json
{
  "type": "join",
  "userId": "user_abc123",
  "roomId": "room_name"  // optional, defaults to userId
}
```

**Send Chat Message:**
```json
{
  "type": "chat_message",
  "userId": "user_abc123",
  "content": "Hello everyone!"
}
```

**Switch Room:**
```json
{
  "type": "switch_room",
  "userId": "user_abc123",
  "roomId": "new_room"
}
```

### Server to Client Messages

**Join Confirmation:**
```json
{
  "type": "joined",
  "roomId": "room_name",
  "userId": "user_abc123",
  "message": "Joined room: room_name"
}
```

**Chat Message:**
```json
{
  "type": "chat_message",
  "userId": "user_abc123",
  "roomId": "room_name",
  "content": "Hello everyone!",
  "timestamp": "2023-12-07T10:30:00.000Z"
}
```

**User Events:**
```json
{
  "type": "user_joined",
  "userId": "user_xyz789",
  "roomId": "room_name",
  "message": "user_xyz789 joined the room"
}
```

**Error:**
```json
{
  "type": "error",
  "message": "Error description"
}
```

## Room Management

- Users automatically join their own room (using their userId) when first connecting
- Rooms are created dynamically when users join them
- Empty rooms are automatically cleaned up when the last user leaves
- Users can switch between rooms using the `switch_room` message type

## Testing

Use the Python test client:

```bash
# Test with local server
python chat_test.py ws://localhost:8080

# Test with deployed server
python chat_test.py wss://your-app.fly.dev
```

## Environment Variables

- `PORT`: Server port (default: 8080)

## Scaling Considerations

For production use with multiple instances, consider:
- Adding Redis for shared state management
- Implementing session persistence
- Load balancer configuration for WebSocket sticky sessions