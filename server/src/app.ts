import express from 'express';
import { WebSocketServer, WebSocket } from 'ws';
import http from 'http';
import * as forge from 'node-forge';

interface ClientInfo {
  userId: string;
  roomId: string;
  authenticated: boolean;
}

interface AuthenticatedUser {
  userId: string;
  publicKey: string;
  registrationTime: string;
}

interface AuthChallenge {
  challenge: string;
  timestamp: number;
}

interface Message {
  type: 'join' | 'chat_message' | 'switch_room' | 'register' | 'authenticate' | 'get_challenge';
  userId?: string;
  roomId?: string;
  content?: string;
  publicKey?: string;
  signature?: string;
}

interface ServerMessage {
  type: 'joined' | 'chat_message' | 'user_joined' | 'user_left' | 'error' | 'challenge' | 'registered' | 'authenticated';
  userId?: string;
  roomId?: string;
  content?: string;
  message?: string;
  timestamp?: string;
  challenge?: string;
}

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

// Store active connections and rooms
const clients = new Map<WebSocket, ClientInfo>(); // websocket -> { userId, roomId, authenticated }
const rooms = new Map<string, Set<WebSocket>>();   // roomId -> Set of websockets
const userRooms = new Map<string, string>(); // userId -> roomId

// Store registered users and their public keys
const registeredUsers = new Map<string, AuthenticatedUser>(); // userId -> user data
const activeChallenges = new Map<WebSocket, AuthChallenge>(); // websocket -> challenge data
const registrationAttempts = new Map<string, number[]>(); // IP -> timestamps
const CHALLENGE_TIMEOUT = 5 * 60 * 1000; // 5 minutes
const RATE_LIMIT_WINDOW = 15 * 60 * 1000; // 15 minutes
const MAX_REGISTRATIONS_PER_WINDOW = 5;
const MIN_USERID_LENGTH = 3;
const MAX_USERID_LENGTH = 32;

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
    case 'get_challenge':
      handleGetChallenge(ws);
      break;
    case 'register':
      if (userId && message.publicKey) {
        handleRegister(ws, userId, message.publicKey);
      } else {
        sendError(ws, 'userId and publicKey are required for register message');
      }
      break;
    case 'authenticate':
      if (userId && message.signature) {
        handleAuthenticate(ws, userId, message.signature);
      } else {
        sendError(ws, 'userId and signature are required for authenticate message');
      }
      break;
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
 * Generates and sends a cryptographic challenge to the client for authentication
 * @param ws - The WebSocket connection requesting the challenge
 */
function handleGetChallenge(ws: WebSocket): void {
  const challenge = forge.random.getBytesSync(32);
  const challengeBase64 = forge.util.encode64(challenge);
  
  activeChallenges.set(ws, {
    challenge: challengeBase64,
    timestamp: Date.now()
  });
  
  sendMessage(ws, {
    type: 'challenge',
    challenge: challengeBase64
  });
  
  console.log(`Challenge sent to client`);
}

/**
 * Handles user registration by storing their public key
 * @param ws - The WebSocket connection of the registering user
 * @param userId - Unique identifier chosen by the user
 * @param publicKeyPem - The user's public key in PEM format
 */
function handleRegister(ws: WebSocket, userId: string, publicKeyPem: string): void {
  try {
    // Rate limiting by IP (approximate using connection)
    const clientIP = getClientIP(ws);
    if (!isWithinRateLimit(clientIP)) {
      sendError(ws, 'Too many registration attempts. Please try again later.');
      return;
    }
    
    // Validate user ID
    if (!isValidUserId(userId)) {
      sendError(ws, `User ID must be ${MIN_USERID_LENGTH}-${MAX_USERID_LENGTH} alphanumeric characters`);
      return;
    }
    
    // Check if user already exists
    if (registeredUsers.has(userId)) {
      sendError(ws, 'User ID already exists');
      return;
    }
    
    // Validate public key format and strength
    const publicKey = forge.pki.publicKeyFromPem(publicKeyPem);
    if ((publicKey as any).n.bitLength() < 2048) {
      sendError(ws, 'Public key must be at least 2048 bits');
      return;
    }
    
    // Store the user
    registeredUsers.set(userId, {
      userId,
      publicKey: publicKeyPem,
      registrationTime: new Date().toISOString()
    });
    
    sendMessage(ws, {
      type: 'registered',
      userId: userId,
      message: 'Registration successful'
    });
    
    console.log(`User ${userId} registered successfully`);
  } catch (error) {
    console.error('Registration error:', error);
    sendError(ws, 'Invalid public key format');
  }
}

/**
 * Handles user authentication by verifying their signature
 * @param ws - The WebSocket connection of the authenticating user
 * @param userId - The user's registered ID
 * @param signatureBase64 - The signature of the challenge in base64 format
 */
function handleAuthenticate(ws: WebSocket, userId: string, signatureBase64: string): void {
  try {
    // Check if user is registered
    const user = registeredUsers.get(userId);
    if (!user) {
      sendError(ws, 'User not registered');
      return;
    }
    
    // Check if we have a valid challenge
    const challengeData = activeChallenges.get(ws);
    if (!challengeData) {
      sendError(ws, 'No challenge issued. Request a challenge first.');
      return;
    }
    
    // Check challenge timeout
    if (Date.now() - challengeData.timestamp > CHALLENGE_TIMEOUT) {
      activeChallenges.delete(ws);
      sendError(ws, 'Challenge expired. Request a new challenge.');
      return;
    }
    
    // Verify the signature
    const publicKey = forge.pki.publicKeyFromPem(user.publicKey);
    const signature = forge.util.decode64(signatureBase64);
    const challenge = forge.util.decode64(challengeData.challenge);
    
    const md = forge.md.sha256.create();
    md.update(challenge);
    const isValid = publicKey.verify(md.digest().bytes(), signature);
    
    if (isValid) {
      // Authentication successful
      clients.set(ws, { userId, roomId: '', authenticated: true });
      activeChallenges.delete(ws);
      
      sendMessage(ws, {
        type: 'authenticated',
        userId: userId,
        message: 'Authentication successful'
      });
      
      console.log(`User ${userId} authenticated successfully`);
    } else {
      sendError(ws, 'Invalid signature');
    }
  } catch (error) {
    console.error('Authentication error:', error);
    sendError(ws, 'Authentication failed');
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

  // Check if user is authenticated
  const client = clients.get(ws);
  if (!client || !client.authenticated) {
    sendError(ws, 'Authentication required before joining rooms');
    return;
  }
  
  // Verify the authenticated user ID matches
  if (client.userId !== userId) {
    sendError(ws, 'User ID mismatch');
    return;
  }

  // Remove from previous room if connected
  if (client.roomId) {
    leaveCurrentRoom(ws);
  }

  // Join new room
  clients.set(ws, { userId, roomId: targetRoom, authenticated: true });
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
  if (!client || !client.authenticated) {
    sendError(ws, 'Authentication required');
    return;
  }
  
  if (!client.roomId) {
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
  if (!client || !client.authenticated) {
    sendError(ws, 'Authentication required');
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
 * Handles WebSocket disconnection by cleaning up user's room membership and challenges
 * @param ws - The disconnected WebSocket connection
 */
function handleDisconnect(ws: WebSocket): void {
  leaveCurrentRoom(ws);
  activeChallenges.delete(ws);
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
 * Validates a user ID for length and allowed characters
 * @param userId - The user ID to validate
 * @returns true if valid, false otherwise
 */
function isValidUserId(userId: string): boolean {
  if (userId.length < MIN_USERID_LENGTH || userId.length > MAX_USERID_LENGTH) {
    return false;
  }
  
  // Allow alphanumeric characters, underscores, and hyphens
  const validPattern = /^[a-zA-Z0-9_-]+$/;
  return validPattern.test(userId);
}

/**
 * Gets the client IP address from WebSocket (simplified)
 * @param ws - The WebSocket connection
 * @returns A string identifier for rate limiting
 */
function getClientIP(ws: WebSocket): string {
  // In a real implementation, you'd extract the actual IP
  // For now, use a connection-based identifier
  return (ws as any)._socket?.remoteAddress || 'unknown';
}

/**
 * Checks if a client is within rate limits for registration
 * @param clientIP - The client identifier
 * @returns true if within limits, false otherwise
 */
function isWithinRateLimit(clientIP: string): boolean {
  const now = Date.now();
  const attempts = registrationAttempts.get(clientIP) || [];
  
  // Remove old attempts outside the window
  const recentAttempts = attempts.filter(timestamp => now - timestamp < RATE_LIMIT_WINDOW);
  
  if (recentAttempts.length >= MAX_REGISTRATIONS_PER_WINDOW) {
    return false;
  }
  
  // Record this attempt
  recentAttempts.push(now);
  registrationAttempts.set(clientIP, recentAttempts);
  
  return true;
}

/**
 * Cleans up expired challenges periodically
 */
function cleanupExpiredChallenges(): void {
  const now = Date.now();
  for (const [ws, challenge] of activeChallenges.entries()) {
    if (now - challenge.timestamp > CHALLENGE_TIMEOUT) {
      activeChallenges.delete(ws);
    }
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

/**
 * Creates and configures the server without starting it
 * @param port - Optional port number (0 for random port in tests)
 * @returns The configured HTTP server
 */
export function createChatServer(port: number = parseInt(process.env.PORT || '8080', 10)) {
  // Cleanup expired challenges every 5 minutes
  const cleanupInterval = setInterval(cleanupExpiredChallenges, 5 * 60 * 1000);
  
  // Store cleanup interval for potential cleanup in tests
  (server as any).cleanupInterval = cleanupInterval;
  
  return server;
}

// Export server state for testing
export { clients, rooms, userRooms, registeredUsers, activeChallenges, registrationAttempts };

// Start server if this file is run directly
if (require.main === module) {
  const PORT = parseInt(process.env.PORT || '8080', 10);
  server.listen(PORT, '0.0.0.0', () => {
    console.log(`Chat server running on port ${PORT}`);
    console.log('Authentication features enabled:');
    console.log('- Public/private key authentication');
    console.log('- Challenge-response protocol');
    console.log('- Rate limiting for registrations');
  });
}
