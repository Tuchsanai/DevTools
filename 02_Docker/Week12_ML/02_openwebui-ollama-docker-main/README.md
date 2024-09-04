

# openwebui-ollama-docker

Basic Open WebUI + Ollama stack for Local ChatGPT

## What is inside?

* **Services**
  * **Ollama**: A Large Language Model (LLM) engine and model catalog. For available models, visit [Ollama Library](https://ollama.com/library).
  * **Open WebUI**: User interface for Ollama and API compatible with Ollama/OpenAI. For more details, check out the [Open WebUI documentation](https://docs.openwebui.com/).
  * **Postgres**: A widely-used open-source SQL database known for its extensible functionalities.



## Basic Usage

1. Clone this repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:

   ```bash
   cd 02_openwebui-ollama-docker-main
   ```

3. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

4. Start the services using Docker Compose:

   ```bash
   docker-compose up -d
   ```

5. Open your browser and go to [http://localhost:8080](http://localhost:8080).


## Initial Settings in Open WebUI
* Sign up as the first user -> this guy will be the super admin
<img width="441" alt="Screenshot 2567-07-23 at 22 50 17" src="https://github.com/user-attachments/assets/2af2c24a-0715-4111-b78b-d88489dd57df">

* Sign in and see your first login
<img width="1715" alt="Screenshot 2567-07-23 at 23 10 16" src="https://github.com/user-attachments/assets/a7c17cb3-d63a-460b-bad1-f3ffca190234">

* Go get model in ollama.com
![Facebook post image (1)](https://github.com/user-attachments/assets/dc7d3120-6a93-4388-963f-2581f0d53ef6)

* Access 'models' in Admin Panel
<img width="372" alt="Screenshot 2567-07-23 at 23 10 57" src="https://github.com/user-attachments/assets/6679836b-dea9-40f0-8d45-e48204fa926d">

* Download
<img width="1291" alt="Screenshot 2567-07-23 at 23 11 54" src="https://github.com/user-attachments/assets/306ae91d-a9c4-46bb-a40a-ee96bc1e9997">

* for Search Engine capabilities. please delete starting and endind " if it is there. Press save
* <img width="1302" alt="Screenshot 2567-07-23 at 23 19 17" src="https://github.com/user-attachments/assets/c750f27a-3995-49a2-a780-772c1d869c03">
