# WebSocket Chat Server - Message Sequence Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    Note over C,S: Authentication Flow
    
    C->>S: get_challenge
    S->>C: challenge { challenge: "base64_challenge" }
    
    Note over C: Generate key pair if not exists
    Note over C: Sign challenge with private key
    
    C->>S: register { userId: "user123", publicKey: "pem_public_key" }
    S->>C: registered { userId: "user123", message: "Registration successful" }
    
    C->>S: authenticate { userId: "user123", signature: "signed_challenge" }
    S->>C: authenticated { userId: "user123", message: "Authentication successful" }
    
    Note over C,S: Room Management & Chat Flow
    
    C->>S: join { userId: "user123", roomId: "general" }
    S->>C: joined { roomId: "general", userId: "user123", message: "Joined room: general" }
    Note over S: Broadcast to other room members
    S-->>C2: user_joined { userId: "user123", roomId: "general", message: "user123 joined the room" }
    
    Note over C,S: Chat Messages
    
    C->>S: chat_message { content: "Hello everyone!" }
    Note over S: Broadcast to all room members
    S->>C: chat_message { userId: "user123", roomId: "general", content: "Hello everyone!", timestamp: "ISO_date" }
    S->>C2: chat_message { userId: "user123", roomId: "general", content: "Hello everyone!", timestamp: "ISO_date" }
    
    Note over C,S: Room Switching
    
    C->>S: switch_room { roomId: "development" }
    Note over S: Leave current room, join new room
    S-->>C2: user_left { userId: "user123", roomId: "general", message: "user123 left the room" }
    S->>C: joined { roomId: "development", userId: "user123", message: "Joined room: development" }
    S-->>C3: user_joined { userId: "user123", roomId: "development", message: "user123 joined the room" }
    
    Note over C,S: Error Handling
    
    C->>S: invalid_message_type
    S->>C: error { message: "Unknown message type: invalid_message_type" }
    
    C->>S: chat_message { content: "msg" } (without authentication)
    S->>C: error { message: "Authentication required" }
    
    Note over C,S: Connection Cleanup
    
    Note over C: WebSocket disconnects
    Note over S: Auto cleanup - remove from rooms
    S-->>C2: user_left { userId: "user123", roomId: "development", message: "user123 left the room" }
```

## Message Flow Details

### 1. Authentication Sequence
- Client requests challenge for cryptographic authentication
- Server generates random challenge and stores it temporarily
- Client registers with userId and RSA public key (if not already registered)
- Client signs the challenge with private key and sends signature
- Server verifies signature against stored public key

### 2. Room Management
- After authentication, client joins a room (defaults to userId if no roomId specified)
- Server notifies other room members when users join/leave
- Users can switch rooms, which triggers leave/join sequence
- Empty rooms are automatically cleaned up

### 3. Chat Flow
- Authenticated users can send messages to their current room
- Server broadcasts messages to all room members with timestamp
- Messages include sender info and room context

### 4. Error Scenarios
- Invalid message types return error responses
- Unauthenticated requests are rejected
- Missing required fields trigger validation errors
- Rate limiting prevents spam registration attempts

### 5. Connection Lifecycle
- WebSocket connections are tracked with user/room state
- Disconnections automatically trigger room cleanup
- Challenge data is cleaned up on disconnect or timeout

## Key Security Features
- **RSA Authentication**: 2048-bit minimum key requirement
- **Challenge-Response**: Prevents replay attacks
- **Rate Limiting**: Registration attempts limited by IP
- **Session Management**: Authentication state tied to WebSocket connection