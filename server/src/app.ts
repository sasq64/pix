import express from 'express';
import { WebSocketServer, WebSocket } from 'ws';
import http from 'http';
import { v4 as uuidv4 } from 'uuid';

interface ClientInfo {
  userId: string;
  roomId: string;
}

interface Message {
  type: 'join' | 'chat_message' | 'switch_room';
  userId?: string;
  roomId?: string;
  content?: string;
}

interface ServerMessage {
  type: 'joined' | 'chat_message' | 'user_joined' | 'user_left' | 'error';
  userId?: string;
  roomId?: string;
  content?: string;
  message?: string;
  timestamp?: string;
}

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

// Store active connections and rooms
const clients = new Map<WebSocket, ClientInfo>(); // websocket -> { userId, roomId }
const rooms = new Map<string, Set<WebSocket>>();   // roomId -> Set of websockets
const userRooms = new Map<string, string>(); // userId -> roomId

// Middleware
app.use(express.json());

// Basic health check
app.get('/', (_req, res) => {
  res.json({
    status: 'Chat server running',
    clients: clients.size,
    rooms: rooms.size
  });
});

// WebSocket connection handler
wss.on('connection', (ws: WebSocket) => {
  console.log('New client connected');

  ws.on('message', (data) => {
    try {
      const message: Message = JSON.parse(data.toString());
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

/**
 * Routes incoming WebSocket messages to appropriate handlers based on message type
 * @param ws - The WebSocket connection that sent the message
 * @param message - The parsed message object containing type and data
 */
function handleMessage(ws: WebSocket, message: Message): void {
  console.log('Got message');
  const { type, userId, roomId, content } = message;
  console.log(`type ${type}`);

  switch (type) {
    case 'join':
      if (userId) {
        handleJoin(ws, userId, roomId);
      } else {
        sendError(ws, 'userId is required for join message');
      }
      break;
    case 'chat_message':
      if (content) {
        handleChatMessage(ws, content);
      } else {
        sendError(ws, 'content is required for chat_message');
      }
      break;
    case 'switch_room':
      if (roomId) {
        handleSwitchRoom(ws, roomId);
      } else {
        sendError(ws, 'roomId is required for switch_room message');
      }
      break;
    default:
      sendError(ws, `Unknown message type: ${type}`);
  }
}

/**
 * Handles user joining a chat room. Creates room if it doesn't exist.
 * If no roomId provided, uses userId as the default room name.
 * @param ws - The WebSocket connection of the joining user
 * @param userId - Unique identifier for the user
 * @param roomId - Optional room identifier (defaults to userId if not provided)
 */
function handleJoin(ws: WebSocket, userId: string, roomId: string | null = null): void {
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
  rooms.get(targetRoom)!.add(ws);

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

/**
 * Processes and broadcasts a chat message to all users in the sender's room
 * @param ws - The WebSocket connection of the message sender
 * @param content - The message content to broadcast
 */
function handleChatMessage(ws: WebSocket, content: string): void {
  const client = clients.get(ws);
  if (!client) {
    sendError(ws, 'Not connected to any room');
    return;
  }

  const { userId, roomId } = client;
  const message: ServerMessage = {
    type: 'chat_message',
    userId: userId,
    roomId: roomId,
    content: content,
    timestamp: new Date().toISOString()
  };

  broadcastToRoom(roomId, message);
  console.log(`Message from ${userId} in room ${roomId}: ${content}`);
}

/**
 * Moves a user from their current room to a new room
 * @param ws - The WebSocket connection of the user switching rooms
 * @param newRoomId - The ID of the room to switch to
 */
function handleSwitchRoom(ws: WebSocket, newRoomId: string): void {
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

/**
 * Removes a user from their current room and cleans up empty rooms
 * Notifies other room members when a user leaves
 * @param ws - The WebSocket connection to remove from the room
 */
function leaveCurrentRoom(ws: WebSocket): void {
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

/**
 * Handles WebSocket disconnection by cleaning up user's room membership
 * @param ws - The disconnected WebSocket connection
 */
function handleDisconnect(ws: WebSocket): void {
  leaveCurrentRoom(ws);
  console.log('Client disconnected');
}

/**
 * Sends a message to all active connections in a specific room
 * @param roomId - The ID of the room to broadcast to
 * @param message - The message object to send
 * @param excludeWs - Optional WebSocket connection to exclude from broadcast (e.g., message sender)
 */
function broadcastToRoom(roomId: string, message: ServerMessage, excludeWs: WebSocket | null = null): void {
  const roomClients = rooms.get(roomId);
  if (!roomClients) return;

  roomClients.forEach(clientWs => {
    if (clientWs !== excludeWs && clientWs.readyState === WebSocket.OPEN) {
      sendMessage(clientWs, message);
    }
  });
}

/**
 * Safely sends a JSON message to a WebSocket connection if it's open
 * @param ws - The WebSocket connection to send to
 * @param message - The message object to serialize and send
 */
function sendMessage(ws: WebSocket, message: ServerMessage): void {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message));
  }
}

/**
 * Sends an error message to a WebSocket connection
 * @param ws - The WebSocket connection to send the error to
 * @param error - The error message text
 */
function sendError(ws: WebSocket, error: string): void {
  sendMessage(ws, { type: 'error', message: error });
}

// Start server
const PORT = parseInt(process.env.PORT || '8080', 10);
server.listen(PORT, '0.0.0.0', () => {
  console.log(`Chat server running on port ${PORT}`);
});
