// 1. Import the HTTP module
const http = require('http');

// 2. Define the server logic
const server = http.createServer((req, res) => {
  // Set the response header (Status 200 = OK)
  res.writeHead(200, {'Content-Type': 'text/plain'});
  
  // Send the message
  res.end('Hello, World! This is my first Node.js server.\n');
});

// 3. Tell the server to listen on port 3000
server.listen(3000, '127.0.0.1', () => {
  console.log('Server running at http://127.0.0.1:3000/');
});