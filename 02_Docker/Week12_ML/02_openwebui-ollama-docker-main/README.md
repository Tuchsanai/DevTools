


# openwebui-ollama-docker
# Basic Open WebUI + Ollama stack for Local ChatGPT.

---


![Alt text](./images/2024-09-04_11-57-24.jpg)



## What's inside?

* **Services:**
  * **Ollama**: A Large Language Model (LLM) engine and model catalog. For available models, visit the [Ollama Library](https://ollama.com/library).
  * **Open WebUI**: A user interface for Ollama, compatible with Ollama/OpenAI APIs. For more details, check the [Open WebUI documentation](https://docs.openwebui.com/).
  * **Postgres**: A widely used open-source SQL database known for its extensibility.

## Docker Compose Configuration

In file . env
```env
# postgres
TIMEZONE=Asia/Bangkok
PG_MAJOR=latest
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=< $ openssl rand -hex 64 >
POSTGRES_DB=postgres

# open-webui
WEBUI_SECRET_KEY=< $ openssl rand -base64 64 >
USE_CUDA_DOCKER=false
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
OLLAMA_BASE_URL=http://ollama:11434
```

In file docker-compose.yanl

```yaml
version: '3.3'

services:
  ollama:
    container_name: ollama-service
    image: ollama/ollama:latest
    restart: unless-stopped
    volumes:
      - ollama:/root/.ollama
    networks:
      - default

  open-webui:
    container_name: open-webui-service
    image: ghcr.io/open-webui/open-webui:latest
    ports:
      - "9003:8080"
    depends_on:
      - postgres
      - ollama
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - OAUTH_MERGE_ACCOUNTS_BY_EMAIL
      - WEBUI_SECRET_KEY
      - USE_CUDA_DOCKER
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
    restart: unless-stopped
    volumes:
      - open_webui:/app/backend/data
    networks:
      - default

  postgres:
    container_name: postgres-service
    image: postgres:${PG_MAJOR:-15}
    environment:
      - TZ
      - POSTGRES_DB
      - POSTGRES_USER
      - POSTGRES_PASSWORD
    restart: always
    volumes:
      - postgres:/var/lib/postgresql/data:rw
    networks:
      - default

networks:
  default:
    driver: bridge

volumes:
  ollama:
  open_webui:
  postgres:
```

## Basic Usage

1. Clone this repository:

   ```
   mkdir 02_openwebui-ollama-docker-main

   cd    02_openwebui-ollama-docker-main

   ```  

   ```bash

    git clone -b dev https://github.com/Tuchsanai/DevTools.git
  
    cd DevTools/02_Docker/Week12_ML/02_openwebui-ollama-docker-main

   ``` 

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Start the services using Docker Compose:
   ```bash
   docker-compose up -d
   ```
  
   check docker 
   ```
   docker ps -a
   ```

   you may see like this
   
   ```bash
   
      CONTAINER ID   IMAGE                                  COMMAND                  CREATED         STATUS                   PORTS                                         NAMES
    8d448a2269c9   ghcr.io/open-webui/open-webui:latest   "bash start.sh"          5 minutes ago   Up 5 minutes (healthy)   0.0.0.0:9003->8080/tcp, [::]:9003->8080/tcp   open-webui-service
    ace052e2eab7   postgres:latest                        "docker-entrypoint.s…"   6 minutes ago   Up 5 minutes             5432/tcp                                      postgres-service
    abbc077bf4ff   ollama/ollama:latest                   "/bin/ollama serve"      6 minutes ago   Up 5 minutes             11434/tcp                                     ollama-service

   ```

4. Connect to the Ollama service:
   
   ```bash
   
   docker exec -it ollama-service bash
   
   ```
   * install llm model 
   
   ```
   
   ollama pull llama3.1:8b
   
   ```
   
   ```
   
   exit
   
   ```


Note you can see all ollama model by https://ollama.com/


![Facebook post image 1](./images/ollama_web.jpg)


5. Open your browser and go to 


```
http://localhost:9003
```



---

Let me know if you need further adjustments!

## Initial Settings in Open WebUI
* Sign up as the first user -> this guy will be the super admin
<img width="441" alt="Screenshot 2567-07-23 at 22 50 17" src="https://github.com/user-attachments/assets/2af2c24a-0715-4111-b78b-d88489dd57df">

* Sign in and see your first login
<img width="1715" alt="Screenshot 2567-07-23 at 23 10 16" src="https://github.com/user-attachments/assets/a7c17cb3-d63a-460b-bad1-f3ffca190234">


Stop all container

```
docker-compose down --volumes --rmi all

```



```
docker stop $(docker ps -a -q)  
docker rm $(docker ps -a -q) 
docker rmi $(docker images -q) 
docker volume rm $(docker volume ls -q)  
docker network prune -f
```