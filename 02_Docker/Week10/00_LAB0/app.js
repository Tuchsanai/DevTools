const express = require('express');
const os = require('os');

const app = express();
const port = 3000;

app.get('/', (req, res) => {
    const currentTime = new Date().toLocaleTimeString();

    res.send("hostname: " + os.hostname() + "<br>");
    res.send("platform: " + os.platform() + "<br>");
    res.send("current time: " + currentTime);
});

app.listen(port, () => {
    console.log(`Express app listening on port ${port}`);
});
