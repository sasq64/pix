# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a WebSocket-based chat server for PixIDE, designed to run on Fly.io. It provides real-time communication capabilities with room-based messaging, user management, and automatic room cleanup.

## Development Commands

### Local Development
```bash
# Install dependencies
npm install

# Build the server (from typescript)
npm run build

# Start the server (development or production)
npm start

# Run tests
npm run test
```

The server runs on port 8080 by default (configurable via PORT environment variable).

### Deployment Commands
```bash
# Deploy to Fly.io (first time)
fly launch

# Subsequent deployments
fly deploy

# Login to Fly.io
fly auth login
```

## Architecture

### Core Components

- **Express Server** (`app.js`): HTTP server with health check endpoint at `/`
- **WebSocket Server**: Real-time bidirectional communication on the same port
- **Connection Management**: Three main data structures:
  - `clients`: Maps WebSocket connections to user/room info
  - `rooms`: Maps room IDs to sets of WebSocket connections
  - `userRooms`: Maps user IDs to their current room

### Message Flow Architecture

**Client-to-Server Messages:**
- `join`: Connect to a room (defaults to userId if no roomId specified)
- `chat_message`: Send a message to current room
- `switch_room`: Move to a different room

**Server-to-Client Messages:**
- `joined`: Confirmation of successful room join
- `chat_message`: Chat message with timestamp and room info
- `user_joined`/`user_left`: Room membership notifications
- `error`: Error responses for invalid requests

### Room Management System

- Rooms are created dynamically when users join them
- Users automatically get their own default room (using their userId)
- Empty rooms are automatically cleaned up when the last user leaves
- Users can switch between rooms without reconnecting

## Key Implementation Details

### Connection Lifecycle
1. WebSocket connection established
2. Client sends `join` message with userId (and optional roomId)
3. Server adds client to room and broadcasts join notification
4. Client can send chat messages or switch rooms
5. On disconnect, client is removed and others are notified

### State Management
The server maintains in-memory state with automatic cleanup:
- Connections are tracked per WebSocket
- Room membership is bidirectionally mapped
- Disconnections trigger cascading cleanup

### Error Handling
- JSON parsing errors are caught and reported
- Invalid message types return error responses
- WebSocket errors are logged but don't crash the server

## Deployment Configuration

- **Fly.io Config** (`fly.toml`): Configured for auto-scaling with connection-based concurrency
- **Docker** (`Dockerfile`): Node.js 18 Alpine with production dependencies only
- **Health Check**: Available at `GET /` returning server status and connection counts
