To set up monitoring for server performance using Prometheus, Grafana, and Node Exporter in Docker containers, follow these steps.

### Step 1: Create a Docker Network
First, create a Docker network to connect the containers:
```bash
docker network create monitoring
```

### Step 2: Run Node Exporter
Run Node Exporter in a Docker container:
```bash
docker run -d --name=node-exporter --net=monitoring prom/node-exporter
```

### Step 3: Prometheus Configuration
Create a file named `prometheus.yml` with the following content:
```yaml
global:
  scrape_interval: 1s

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

Run Prometheus in a Docker container, mounting the configuration file:
```bash
docker run -d --name=prometheus --net=monitoring -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
```

### Step 4: Grafana Configuration
For Grafana, you'll need two files: `datasources.yaml` and `dashboards.yaml`.

#### datasources.yaml
```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

#### dashboards.yaml
```yaml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    folderUid: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

#### Running Grafana with Configuration
Create a directory for Grafana dashboards:
```bash
mkdir -p grafana-dashboards
```

Download the dashboard with ID 1860 (you'll need to do this step manually as I can't perform downloads):
```bash
# Download the dashboard JSON file from Grafana's website and save it in the grafana-dashboards directory
```

Run Grafana, mounting the configuration files and dashboard directory:
```bash
docker run -d --name=grafana --net=monitoring -p 3000:3000 -v $(pwd)/datasources.yaml:/etc/grafana/provisioning/datasources/datasources.yaml -v $(pwd)/dashboards.yaml:/etc/grafana/provisioning/dashboards/dashboards.yaml -v $(pwd)/grafana-dashboards:/var/lib/grafana/dashboards grafana/grafana
```

### Accessing the Services
- **Prometheus:** Access Prometheus at `http://localhost:9090`
- **Grafana:** Access Grafana at `http://localhost:3000` (default login is `admin`/`admin`, which you'll be prompted to change)

This setup will get you started with monitoring server performance using Docker containers for Prometheus, Grafana, and Node Exporter. Remember, you might need to adjust firewall rules or Docker settings depending on your server configuration.