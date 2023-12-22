### To setup ngrok on Ubuntu 22.04, there are two primary methods you can follow.


1. **Create an Ngrok Account**:
   - If you don't have an ngrok account, create one on the [official ngrok website](https://dashboard.ngrok.com).

2. **Download ngrok**:
   - You can download ngrok directly from the Setup & Installation page on the ngrok dashboard or use the following command in the terminal to download the binary file:
     ```bash
     wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
     ```
3. **Decompress & Install Ngrok Tunnel**:
   - Extract the downloaded file with the following command:
     ```bash
     tar zxvf ngrok-v3-stable-linux-amd64.tgz
     ```
4. **Connect Ubuntu to the ngrok account**:
   - Run the following command to add the auth token to the default Ngrok.yml configuration file (replace the token with your own):
     ```bash
     ./ngrok config add-authtoken <YourAuthToken>
     ```
5. **Usage**:
   - To create a tunnel to your local server or port forwarding using ngrok, use the following command (replace `8080` with your desired port):
     ```bash
     ./ngrok http 8080
     ```
   - This will provide you with a URL accessible on any device having internet connectivity. The URL of your local Web Interface will be like “http://127.0.0.1:8080,” and the URL provided by ngrok to access this web server worldwide will be something like “https://<random-hash>.in.ngrok.io”】.
