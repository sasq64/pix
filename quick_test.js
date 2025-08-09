const WebSocket = require('ws');

async function quickTest() {
    const ws = new WebSocket('ws://localhost:8080');
    const userId = 'test-' + Math.random().toString(36).substr(2, 5);
    
    await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error('Connection timeout')), 1000);
        ws.on('open', () => { clearTimeout(timeout); resolve(); });
        ws.on('error', reject);
    });

    // Join room
    ws.send(JSON.stringify({ type: 'join', userId, roomId: 'test' }));
    await new Promise(resolve => ws.once('message', resolve));
    
    // Send message and wait for echo
    const messagePromise = new Promise(resolve => ws.once('message', resolve));
    ws.send(JSON.stringify({ type: 'chat_message', userId, content: 'Quick test!' }));
    await messagePromise;
    
    ws.close();
    console.log('✓ Quick test passed');
}

quickTest().catch(console.error);