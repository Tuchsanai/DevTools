const express = require('express');
const os = require('os');

const app = express();
const port = 3000;
const hostname = os.hostname();
const name = process.env.NAME || 'Express Server';

app.get('/', (req, res) => {
  res.send(`Hello from ${name} on ${hostname}!`);
});

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
