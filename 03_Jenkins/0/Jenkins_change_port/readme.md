# If Jenkins fails to start because a 8080 port is in use, set Jenkins to listen on port 5000  demo. 
### Ref : https://www.jenkins.io/doc/book/installing/linux/

If Jenkins fails to start because a port is in use, run systemctl edit jenkins and add the following:


1. Override the Jenkins Service Configuration
```
sudo systemctl edit jenkins
```

2. Add or Modify the ExecStart Command 

```
[Service]
Environment="JENKINS_PORT=5000"
```



3.Reload the Systemd Daemon
```
sudo systemctl daemon-reload
```


4. Restart the Jenkins service to apply the changes
```
sudo service jenkins restart
```
