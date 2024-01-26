const express = require('express');
const os = require('os');

const app = express();
const port = 3000;

app.get('/', (req, res) => {
    res.send(`Host IP: ${req.ip} - Host Name: ${os.hostname()}`);
});

app.listen(port, () => {
    console.log(`Express app listening on port ${port}`);
});
