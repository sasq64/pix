const express = require('express');
const { WebSocketServer } = require('ws');
const http = require('http');
const { v4: uuidv4 } = require('uuid');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

// Store active connections and rooms
const clients = new Map(); // websocket -> { userId, roomId }
const rooms = new Map();   // roomId -> Set of websockets
const userRooms = new Map(); // userId -> roomId

// Middleware
app.use(express.json());

// Basic health check
app.get('/', (req, res) => {
  res.json({
    status: 'Chat server running',
    clients: clients.size,
    rooms: rooms.size
  });
});

// WebSocket connection handler
wss.on('connection', (ws) => {
  console.log('New client connected');

  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data.toString());
      handleMessage(ws, message);
    } catch (error) {
      console.error('Error parsing message:', error);
      sendError(ws, 'Invalid JSON format');
    }
  });

  ws.on('close', () => {
    handleDisconnect(ws);
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

function handleMessage(ws, message) {
  console.log('Got message');
  const { type, userId, roomId, content } = message;
  console.log(`type ${type}`);

  switch (type) {
    case 'join':
      handleJoin(ws, userId, roomId);
      break;
    case 'chat_message':
      handleChatMessage(ws, content);
      break;
    case 'switch_room':
      handleSwitchRoom(ws, roomId);
      break;
    default:
      sendError(ws, `Unknown message type: ${type}`);
  }
}

function handleJoin(ws, userId, roomId = null) {
  // If no roomId provided, use userId as default room
  const targetRoom = roomId || userId;

  // Remove from previous room if connected
  if (clients.has(ws)) {
    leaveCurrentRoom(ws);
  }

  // Join new room
  clients.set(ws, { userId, roomId: targetRoom });
  userRooms.set(userId, targetRoom);

  if (!rooms.has(targetRoom)) {
    rooms.set(targetRoom, new Set());
  }
  rooms.get(targetRoom).add(ws);

  // Notify user of successful join
  sendMessage(ws, {
    type: 'joined',
    roomId: targetRoom,
    userId: userId,
    message: `Joined room: ${targetRoom}`
  });

  // Notify others in room
  broadcastToRoom(targetRoom, {
    type: 'user_joined',
    userId: userId,
    roomId: targetRoom,
    message: `${userId} joined the room`
  }, ws);

  console.log(`User ${userId} joined room ${targetRoom}`);
}

function handleChatMessage(ws, content) {
  const client = clients.get(ws);
  if (!client) {
    sendError(ws, 'Not connected to any room');
    return;
  }

  const { userId, roomId } = client;
  const message = {
    type: 'chat_message',
    userId: userId,
    roomId: roomId,
    content: content,
    timestamp: new Date().toISOString()
  };

  broadcastToRoom(roomId, message);
  console.log(`Message from ${userId} in room ${roomId}: ${content}`);
}

function handleSwitchRoom(ws, newRoomId) {
  const client = clients.get(ws);
  if (!client) {
    sendError(ws, 'Not connected to any room');
    return;
  }

  const { userId } = client;

  // Leave current room
  leaveCurrentRoom(ws);

  // Join new room
  handleJoin(ws, userId, newRoomId);
}

function leaveCurrentRoom(ws) {
  const client = clients.get(ws);
  if (!client) return;

  const { userId, roomId } = client;
  const roomClients = rooms.get(roomId);

  if (roomClients) {
    roomClients.delete(ws);

    // Clean up empty rooms
    if (roomClients.size === 0) {
      rooms.delete(roomId);
    } else {
      // Notify others in room
      broadcastToRoom(roomId, {
        type: 'user_left',
        userId: userId,
        roomId: roomId,
        message: `${userId} left the room`
      });
    }
  }

  clients.delete(ws);
  userRooms.delete(userId);
  console.log(`User ${userId} left room ${roomId}`);
}

function handleDisconnect(ws) {
  leaveCurrentRoom(ws);
  console.log('Client disconnected');
}

function broadcastToRoom(roomId, message, excludeWs = null) {
  const roomClients = rooms.get(roomId);
  if (!roomClients) return;

  roomClients.forEach(clientWs => {
    if (clientWs !== excludeWs && clientWs.readyState === clientWs.OPEN) {
      sendMessage(clientWs, message);
    }
  });
}

function sendMessage(ws, message) {
  if (ws.readyState === ws.OPEN) {
    ws.send(JSON.stringify(message));
  }
}

function sendError(ws, error) {
  sendMessage(ws, { type: 'error', message: error });
}

// Start server
const PORT = process.env.PORT || 8080;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`Chat server running on port ${PORT}`);
});
