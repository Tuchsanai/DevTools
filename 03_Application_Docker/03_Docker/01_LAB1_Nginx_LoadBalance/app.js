const express = require('express');
const os = require('os');

const app = express();
const port = 3000;

app.get('/', (req, res) => {
    const currentTime = new Date().toLocaleTimeString();

    res.send(`<div>
                <span style="font-size: 24px;">hostname: ${os.hostname()}</span><br>
                <span>platform: ${os.platform()}</span><br>
                <span>current time: ${currentTime}</span>
              </div>`);
});

app.listen(port, () => {
    console.log(`Express app listening on port ${port}`);
});
