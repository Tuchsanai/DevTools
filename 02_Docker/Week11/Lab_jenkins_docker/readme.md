## Configuring GitHub
### Step 1: go to your GitHub repository and click on ‘Settings’.

### Step 2: Click on Webhooks and then click on ‘Add webhook’.

### Step 3: In the ‘Payload URL’ field, paste your Jenkins environment URL. At the end of this URL add /github-webhook/. In the ‘Content type’ select: ‘application/json’ and leave the ‘Secret’ field empty.
```
http://ip-address:8080/github-webhook/
```

### Jenkins plugins
Install the following plugins for the demo.

* Docker plugin
* Docker Pipeline
