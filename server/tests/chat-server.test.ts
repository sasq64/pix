import WebSocket from 'ws';
import http from 'http';
import * as forge from 'node-forge';
import { createChatServer, clients, rooms, userRooms, registeredUsers, activeChallenges, registrationAttempts } from '../src/app';

describe('Chat Server Authentication Tests', () => {
  let server: http.Server;
  let port: number;

  beforeAll((done) => {
    // Create the actual server with authentication
    server = createChatServer(0); // Use port 0 for random port

    // Start server on random port
    server.listen(0, () => {
      const address = server.address();
      if (address && typeof address === 'object') {
        port = address.port;
        console.log(`Test server started on port ${port}`);
        done();
      }
    });
  });

  afterAll((done) => {
    // Clean up the cleanup interval
    if ((server as any).cleanupInterval) {
      clearInterval((server as any).cleanupInterval);
    }
    server.close(done);
  });

  afterEach(() => {
    // Clean up any remaining connections and state
    clients.clear();
    rooms.clear();
    userRooms.clear();
    registeredUsers.clear();
    activeChallenges.clear();
    registrationAttempts.clear();
  });

  // Helper function to generate RSA key pair
  function generateKeyPair() {
    const keys = forge.pki.rsa.generateKeyPair(2048);
    return {
      publicKey: forge.pki.publicKeyToPem(keys.publicKey),
      privateKey: forge.pki.privateKeyToPem(keys.privateKey),
      publicKeyObj: keys.publicKey,
      privateKeyObj: keys.privateKey
    };
  }

  // Helper function to sign a challenge
  function signChallenge(privateKey: any, challenge: string): string {
    const challengeBytes = forge.util.decode64(challenge);
    const md = forge.md.sha256.create();
    md.update(challengeBytes);
    const signature = privateKey.sign(md);
    return forge.util.encode64(signature);
  }

  test('should allow client to connect and disconnect', (done) => {
    const client = new WebSocket(`ws://localhost:${port}`);

    client.on('open', () => {
      expect(client.readyState).toBe(WebSocket.OPEN);
      client.close();
    });

    client.on('close', () => {
      expect(client.readyState).toBe(WebSocket.CLOSED);
      done();
    });

    client.on('error', (error) => {
      done(error);
    });
  });

  test('should reject join message without authentication', (done) => {
    const client = new WebSocket(`ws://localhost:${port}`);

    client.on('open', () => {
      // Try to join without authentication
      client.send(JSON.stringify({
        type: 'join',
        userId: 'testUser'
      }));
    });

    client.on('message', (data) => {
      const message = JSON.parse(data.toString());
      expect(message.type).toBe('error');
      expect(message.message).toContain('Authentication required');
      client.close();
      done();
    });

    client.on('error', (error) => {
      done(error);
    });
  });

  test('should allow user registration with valid public key', (done) => {
    const client = new WebSocket(`ws://localhost:${port}`);
    const { publicKey } = generateKeyPair();
    const userId = 'testUser123';

    client.on('open', () => {
      // Register user
      client.send(JSON.stringify({
        type: 'register',
        userId: userId,
        publicKey: publicKey
      }));
    });

    client.on('message', (data) => {
      const message = JSON.parse(data.toString());
      expect(message.type).toBe('registered');
      expect(message.userId).toBe(userId);
      expect(registeredUsers.has(userId)).toBe(true);
      client.close();
      done();
    });

    client.on('error', (error) => {
      done(error);
    });
  });

  test('should reject registration with invalid public key', (done) => {
    const client = new WebSocket(`ws://localhost:${port}`);

    client.on('open', () => {
      // Register with invalid public key
      client.send(JSON.stringify({
        type: 'register',
        userId: 'testUser123',
        publicKey: 'invalid-key'
      }));
    });

    client.on('message', (data) => {
      const message = JSON.parse(data.toString());
      expect(message.type).toBe('error');
      expect(message.message).toContain('Invalid public key');
      client.close();
      done();
    });

    client.on('error', (error) => {
      done(error);
    });
  });

  test('should reject registration with duplicate user ID', (done) => {
    const client1 = new WebSocket(`ws://localhost:${port}`);
    const client2 = new WebSocket(`ws://localhost:${port}`);
    const { publicKey: publicKey1 } = generateKeyPair();
    const { publicKey: publicKey2 } = generateKeyPair();
    const userId = 'duplicateUser';
    let client1Registered = false;

    client1.on('open', () => {
      client1.send(JSON.stringify({
        type: 'register',
        userId: userId,
        publicKey: publicKey1
      }));
    });

    client1.on('message', (data) => {
      const message = JSON.parse(data.toString());
      if (message.type === 'registered') {
        client1Registered = true;
        client1.close();
        
        // Now try to register with same user ID from second client
        client2.send(JSON.stringify({
          type: 'register',
          userId: userId,
          publicKey: publicKey2
        }));
      }
    });

    client2.on('open', () => {
      // Wait for first client to register
    });

    client2.on('message', (data) => {
      const message = JSON.parse(data.toString());
      expect(client1Registered).toBe(true);
      expect(message.type).toBe('error');
      expect(message.message).toContain('User ID already exists');
      client2.close();
      done();
    });

    client1.on('error', (error) => done(error));
    client2.on('error', (error) => done(error));
  });

  test('should complete full authentication flow', (done) => {
    const client = new WebSocket(`ws://localhost:${port}`);
    const keyPair = generateKeyPair();
    const userId = 'authUser123';
    let challenge: string;

    let step = 0; // Track which step we're in

    client.on('open', () => {
      // Step 1: Register
      client.send(JSON.stringify({
        type: 'register',
        userId: userId,
        publicKey: keyPair.publicKey
      }));
      step = 1;
    });

    client.on('message', (data) => {
      const message = JSON.parse(data.toString());

      if (step === 1 && message.type === 'registered') {
        // Step 2: Get challenge
        client.send(JSON.stringify({
          type: 'get_challenge'
        }));
        step = 2;

      } else if (step === 2 && message.type === 'challenge') {
        // Step 3: Authenticate
        challenge = message.challenge!;
        const signature = signChallenge(keyPair.privateKeyObj, challenge);
        
        client.send(JSON.stringify({
          type: 'authenticate',
          userId: userId,
          signature: signature
        }));
        step = 3;

      } else if (step === 3 && message.type === 'authenticated') {
        // Step 4: Now try to join a room
        client.send(JSON.stringify({
          type: 'join',
          userId: userId,
          roomId: 'testRoom'
        }));
        step = 4;

      } else if (step === 4 && message.type === 'joined') {
        // Success! Full flow completed
        expect(message.userId).toBe(userId);
        expect(message.roomId).toBe('testRoom');
        expect(clients.size).toBe(1);
        expect(rooms.size).toBe(1);
        client.close();
        done();
      } else {
        done(new Error(`Unexpected message at step ${step}: ${JSON.stringify(message)}`));
      }
    });

    client.on('error', (error) => {
      done(error);
    });
  }, 10000); // Increase timeout for this complex test

  test('should reject authentication with invalid signature', (done) => {
    const client = new WebSocket(`ws://localhost:${port}`);
    const keyPair = generateKeyPair();
    const userId = 'invalidSigUser';
    let step = 0;

    client.on('open', () => {
      // Register first
      client.send(JSON.stringify({
        type: 'register',
        userId: userId,
        publicKey: keyPair.publicKey
      }));
      step = 1;
    });

    client.on('message', (data) => {
      const message = JSON.parse(data.toString());

      if (step === 1 && message.type === 'registered') {
        // Get challenge
        client.send(JSON.stringify({
          type: 'get_challenge'
        }));
        step = 2;

      } else if (step === 2 && message.type === 'challenge') {
        // Send invalid signature
        client.send(JSON.stringify({
          type: 'authenticate',
          userId: userId,
          signature: 'invalid-signature'
        }));
        step = 3;

      } else if (step === 3) {
        expect(message.type).toBe('error');
        expect(message.message).toContain('Authentication failed');
        client.close();
        done();
      }
    });

    client.on('error', (error) => {
      done(error);
    });
  }, 8000);

  test('should reject invalid user ID formats', (done) => {
    const client = new WebSocket(`ws://localhost:${port}`);
    const { publicKey } = generateKeyPair();

    client.on('open', () => {
      // Try to register with invalid user ID (too short)
      client.send(JSON.stringify({
        type: 'register',
        userId: 'ab', // Too short
        publicKey: publicKey
      }));
    });

    client.on('message', (data) => {
      const message = JSON.parse(data.toString());
      expect(message.type).toBe('error');
      expect(message.message).toMatch(/User ID must be|Too many registration/);
      client.close();
      done();
    });

    client.on('error', (error) => {
      done(error);
    });
  }, 8000);

  test('should clean up on disconnect', (done) => {
    const client = new WebSocket(`ws://localhost:${port}`);
    const keyPair = generateKeyPair();
    const userId = 'cleanupUser';
    let authenticated = false;

    client.on('open', () => {
      client.send(JSON.stringify({
        type: 'register',
        userId: userId,
        publicKey: keyPair.publicKey
      }));
    });

    client.on('message', (data) => {
      const message = JSON.parse(data.toString());

      if (message.type === 'registered') {
        client.send(JSON.stringify({ type: 'get_challenge' }));
      } else if (message.type === 'challenge') {
        const signature = signChallenge(keyPair.privateKeyObj, message.challenge!);
        client.send(JSON.stringify({
          type: 'authenticate',
          userId: userId,
          signature: signature
        }));
      } else if (message.type === 'authenticated') {
        authenticated = true;
        client.send(JSON.stringify({
          type: 'join',
          userId: userId
        }));
      } else if (message.type === 'joined') {
        // Verify client is connected
        expect(clients.size).toBe(1);
        expect(rooms.size).toBe(1);
        
        // Now disconnect
        client.close();
      }
    });

    client.on('close', () => {
      expect(authenticated).toBe(true);
      
      // Verify cleanup happened
      setTimeout(() => {
        expect(clients.size).toBe(0);
        expect(rooms.size).toBe(0);
        expect(userRooms.size).toBe(0);
        expect(activeChallenges.size).toBe(0);
        done();
      }, 10);
    });

    client.on('error', (error) => {
      done(error);
    });
  }, 8000);
});