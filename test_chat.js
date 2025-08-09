const WebSocket = require('ws');

function createSyncWebSocket(url, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const ws = new WebSocket(url);
        const timer = setTimeout(() => {
            ws.close();
            reject(new Error(`Connection timeout after ${timeout}ms`));
        }, timeout);

        ws.on('open', () => {
            clearTimeout(timer);
            resolve(ws);
        });

        ws.on('error', (error) => {
            clearTimeout(timer);
            reject(error);
        });
    });
}

function sendMessage(ws, message, timeout = 2000) {
    return new Promise((resolve, reject) => {
        let responseReceived = false;
        
        const timer = setTimeout(() => {
            if (!responseReceived) {
                reject(new Error(`No response received within ${timeout}ms`));
            }
        }, timeout);

        const messageHandler = (data) => {
            try {
                const response = JSON.parse(data.toString());
                responseReceived = true;
                clearTimeout(timer);
                ws.off('message', messageHandler);
                resolve(response);
            } catch (error) {
                clearTimeout(timer);
                ws.off('message', messageHandler);
                reject(new Error('Invalid JSON response'));
            }
        };

        ws.on('message', messageHandler);
        ws.send(JSON.stringify(message));
    });
}

function waitForMessage(ws, timeout = 2000) {
    return new Promise((resolve, reject) => {
        const timer = setTimeout(() => {
            ws.off('message', messageHandler);
            reject(new Error(`No message received within ${timeout}ms`));
        }, timeout);

        const messageHandler = (data) => {
            try {
                const message = JSON.parse(data.toString());
                clearTimeout(timer);
                ws.off('message', messageHandler);
                resolve(message);
            } catch (error) {
                clearTimeout(timer);
                ws.off('message', messageHandler);
                reject(new Error('Invalid JSON message'));
            }
        };

        ws.on('message', messageHandler);
    });
}

async function testChatServer() {
    console.log('Starting WebSocket chat server test...');
    
    try {
        // 1. Connect to server
        console.log('1. Connecting to WebSocket server...');
        const ws = await createSyncWebSocket('ws://localhost:8080', 3000);
        console.log('✓ Connected successfully');

        // 2. Join a room
        console.log('2. Joining room...');
        const joinResponse = await sendMessage(ws, {
            type: 'join',
            userId: 'test-user-' + Date.now(),
            roomId: 'test-room'
        }, 2000);
        console.log('✓ Joined room:', joinResponse.roomId);

        // 3. Send a chat message
        console.log('3. Sending chat message...');
        
        // Set up message listener before sending
        const messagePromise = waitForMessage(ws, 2000);
        
        ws.send(JSON.stringify({
            type: 'chat_message',
            userId: joinResponse.userId,
            content: 'Hello, this is a test message!'
        }));
        
        // Wait for the message to be broadcast back
        const messageResponse = await messagePromise;
        console.log('✓ Message sent and received:', messageResponse.content);

        // 4. Disconnect cleanly
        console.log('4. Disconnecting...');
        ws.close();
        
        // Wait a moment for clean disconnection
        await new Promise(resolve => setTimeout(resolve, 500));
        console.log('✓ Disconnected cleanly');

        console.log('\n🎉 All tests passed successfully!');
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        process.exit(1);
    }
}

// Run the test
testChatServer();