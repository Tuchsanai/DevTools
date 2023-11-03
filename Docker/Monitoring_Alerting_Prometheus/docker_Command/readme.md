


```

docker run -d  --name node_exporter \
  -p 9100:9100 \
  -v "/:/host:ro,rslave" \
  quay.io/prometheus/node-exporter:latest \
  --path.rootfs=/host
 
```

```
docker run --restart=always -d --name cct_prometheus \
    -p 9090:9090 \
    -v ./prometheus-node-exporter.yml:/etc/prometheus/prometheus.yml \
    prom/prometheus
```


```
docker run -d \
  -p 3000:3000 \
  --name=grafana \
  -e "GF_SERVER_ROOT_URL=http://grafana.server.name" \
  -e "GF_SECURITY_ADMIN_PASSWORD=secret" \
  grafana/grafana

```