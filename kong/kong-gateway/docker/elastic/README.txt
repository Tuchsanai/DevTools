I. RUN CONTAINERS 

Open terminal, and run this command

#> docker-compose down && docker-compose up -d

Wait about 5 minutes for all the elastic container to starts

------------------------------------------------------------------------------------------------------------------

II. SETUP KIBANA

Elasticsearch 8 security is enabled by default.
Follow these steps to connect Kibana with elasticsearch.


A. Get Kibana enrollment token
1. From terminal, run this command

   #> docker exec -ti elasticsearch /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token --scope kibana
   ... 
   eyJ2ZXIiOiI4L...

2. Copy and save the enrollment token


----------


B. Get Kibana verification code
1. From terminal, run this command
  
   #> docker exec -ti kibana /usr/share/kibana/bin/kibana-verification-code
   ...
   Your verification code is:  263 042

2. Copy and save the verification code

----------


C. Get Elasticsearch credentials
1. From terminal, run this command

   #> docker exec -ti elasticsearch /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
   ...
   Password for the [elastic] user successfully reset.
   New value: 1My0...

2. Copy and save the password


----------


C. Configure Kibana UI

1. From web browser, open http://localhost:5601
2. Paste enrollment token from step II.A
3. Kibana UI will ask for verification code. Use the 6 digits number from step II.B
4. Login to Kibana using username "elastic" and password from step II.C
5. Choose an option "Explore on my own"


------------------------------------------------------------------------------------------------------------------

III. CONFIGURE LOGSTASH PIPELINE

For complete instruction please see https://www.elastic.co/guide/en/logstash/8.11/ls-security.html


Run the following steps from terminal:

1. On the file elastic/logstash/pipeline.conf, change the password on "output" section (around line 35 on the file) to the elasticsearch password (from step II.C).


2. Find the self-signed Elasticsearch certificate
 
   #> docker exec -it elasticsearch sh -c "ls /usr/share/elasticsearch/config/certs/*.crt"
   ...
   /usr/share/elasticsearch/config/certs/http_ca.crt
    
   You will get the output indicating a file .crt. Copy the output, and use it on next step

3. Copy self-signed Elasticsearch certificate to current folder. 
   If required, replace the /usr/share/... using response from step #1
   
   #> docker cp elasticsearch:/usr/share/elasticsearch/config/certs/http_ca.crt .
   ...
   Successfully copied xxxkB to <local-folder>

   Make sure on your local folder, there is a file http_ca.crt

4. Create the directory in the logstash container to store the certificate

   #> docker exec -it logstash mkdir -p /usr/share/logstash/certs

5. Copy the crt file to logstash container 

   #> docker cp http_ca.crt logstash:/usr/share/logstash/certs/
   ...
   Successfully copied xxxkB to logstash:/usr/share/logstash/cert/

6. restart the docker logstash container
   
   #> docker restart logstash

