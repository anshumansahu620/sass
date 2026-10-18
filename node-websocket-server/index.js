const { WebSocketServer, WebSocket } = require('ws');

const PORT = process.env.PORT || 8080;

const wss = new WebSocketServer({ port: PORT });

console.log(`[WebSocket Server] Starting on port ${PORT}...`);

wss.on('connection', (ws, req) => {
  const ip = req.socket.remoteAddress;
  console.log(`[WebSocket Server] Client connected from ${ip}`);

  ws.isAlive = true;
  ws.on('pong', () => {
    ws.isAlive = true;
  });

  ws.on('message', (data, isBinary) => {
    const message = isBinary ? data : data.toString();
    console.log(`[WebSocket Server] Received: ${message}`);

    // Echo back or broadcast
    ws.send(JSON.stringify({
      type: 'ack',
      data: isBinary ? 'binary data' : message,
      timestamp: new Date().toISOString()
    }));
  });

  ws.on('close', (code, reason) => {
    console.log(`[WebSocket Server] Client disconnected (${code}: ${reason || 'no reason'})`);
  });

  ws.on('error', (err) => {
    console.error('[WebSocket Server] Client error:', err.message);
  });

  // Welcome message
  ws.send(JSON.stringify({
    type: 'welcome',
    message: 'Connected to WebSocket server',
    timestamp: new Date().toISOString()
  }));
});

// Heartbeat to clear broken connections every 30s
const interval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (ws.isAlive === false) {
      console.log('[WebSocket Server] Terminating inactive client');
      return ws.terminate();
    }
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);

wss.on('close', () => {
  clearInterval(interval);
});

// Graceful shutdown
process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));

function shutdown(signal) {
  console.log(`\n[WebSocket Server] Received ${signal}, closing server...`);
  wss.close(() => {
    console.log('[WebSocket Server] Server closed cleanly.');
    process.exit(0);
  });
}
