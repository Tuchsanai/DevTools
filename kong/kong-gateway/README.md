


# Kong Docker Setup

## 1. Getting Started With The Fast API Application

```sh
$ git clone https://github.com/raj713335/kong-gateway.git
$ cd kong-gateway
$ pip install -r requirements.txt
$ python main.py
```

## Run & Go
For easy installation and setup run a single command below.
```docker-compose
 docker-compose up -d --build
```

----------

## Prepare the database

### 1. Create a custom Docker network to allow the containers to discover and communicate with each other:

```
docker network create kong-net
```
You can name this network anything you want. We use kong-net as an example throughout this guide.

### 2. Start a PostgreSQL container:

```
docker run -d --name kong-database \
 --network=kong-net \
 -p 5432:5432 \
 -e "POSTGRES_USER=kong" \
 -e "POSTGRES_DB=kong" \
 -e "POSTGRES_PASSWORD=kongpass" \
 postgres:13
```

- POSTGRES_USER and POSTGRES_DB: Set these values to kong. This is the default value that Kong Gateway expects.
- POSTGRES_PASSWORD: Set the database password to any string.

In this example, the Postgres container named kong-database can communicate with any containers on the kong-net network.


### 3. Prepare the Kong database:

```
docker run --rm --network=kong-net \
 -e "KONG_DATABASE=postgres" \
 -e "KONG_PG_HOST=kong-database" \
 -e "KONG_PG_PASSWORD=kongpass" \
 -e "KONG_PASSWORD=test" \
kong/kong-gateway:3.5.0.2 kong migrations bootstrap
```

Where:

- KONG_DATABASE: Specifies the type of database that Kong is using.
- KONG_PG_HOST: The name of the Postgres Docker container that is communicating over the kong-net network, from the previous step.
- KONG_PG_PASSWORD: The password that you set when bringing up the Postgres container in the previous step.
- KONG_PASSWORD (Enterprise only): The default password for the admin super user for Kong Gateway.
- {IMAGE-NAME:TAG} kong migrations bootstrap: In order, this is the Kong Gateway container name and tag, followed by the command to Kong to prepare the Postgres database.

#### Start Kong Gateway

```
Important: The settings below are intended for non-production use only, as they override the default admin_listen setting to listen for requests from any source. Do not use these settings in environments directly exposed to the internet.


If you need to expose the admin_listen port to the internet in a production environment,
```

<a href="https://docs.konghq.com/gateway/3.5.x/production/running-kong/secure-admin-api/">secure it with authentication.</a>

### 4. (Optional) If you have an Enterprise license for Kong Gateway, export the license key to a variable:

The license data must contain straight quotes to be considered valid JSON (' and ", not ’ or “).

```
export KONG_LICENSE_DATA='{"license":{"payload":{"admin_seats":"1","customer":"Example Company, Inc","dataplanes":"1","license_creation_date":"2017-07-20","license_expiration_date":"2017-07-20","license_key":"00141000017ODj3AAG_a1V41000004wT0OEAU","product_subscription":"Konnect Enterprise","support_plan":"None"},"signature":"6985968131533a967fcc721244a979948b1066967f1e9cd65dbd8eeabe060fc32d894a2945f5e4a03c1cd2198c74e058ac63d28b045c2f1fcec95877bd790e1b","version":"1"}}'
```

### 5. Run the following command to start a container with Kong Gateway:

```
docker run -d --name kong-gateway \
--network=kong-net \
-e "KONG_DATABASE=postgres" \
-e "KONG_PG_HOST=kong-database" \
-e "KONG_PG_USER=kong" \
-e "KONG_PG_PASSWORD=kongpass" \
-e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
-e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
-e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
-e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
-e "KONG_ADMIN_LISTEN=0.0.0.0:8001" \
-e "KONG_ADMIN_GUI_URL=http://localhost:8002" \
-e KONG_LICENSE_DATA \
-p 8000:8000 \
-p 8443:8443 \
-p 8001:8001 \
-p 8444:8444 \
-p 8002:8002 \
-p 8445:8445 \
-p 8003:8003 \
-p 8004:8004 \
kong/kong-gateway:3.5.0.2
```

Where:

- --name and --network: The name of the container to create, and the Docker network it communicates on.
- KONG_DATABASE: Specifies the type of database that Kong is using.
- KONG_PG_HOST: The name of the Postgres Docker container that is communicating over the kong-net network.
- KONG_PG_USER and KONG_PG_PASSWORD: The Postgres username and password. Kong Gateway needs the login information to store configuration data in the KONG_PG_HOST database.
- All _LOG parameters: set filepaths for the logs to output to, or use the values in the example to print messages and errors to stdout and stderr.
- KONG_ADMIN_LISTEN: The port that the Kong Admin API listens on for requests.
- KONG_ADMIN_GUI_URL: The URL for accessing Kong Manager, preceded by a protocol (for example, http://).
- KONG_LICENSE_DATA: (Enterprise only) If you have a license file and have saved it as an environment variable, this parameter pulls the license from your environment.


### 6. Verify your installation:

Access the /services endpoint using the Admin API:

```
curl -i -X GET --url http://localhost:8001/services
```
You should receive a 200 status code.

### 7. Verify that Kong Manager is running by accessing it using the URL specified in KONG_ADMIN_GUI_URL:

```
http://localhost:8002
```

## Get started with Kong Gateway

Now that you have a running Gateway instance, Kong provides a series of <a href="https://docs.konghq.com/gateway/3.5.x/get-started/services-and-routes/">getting started guides</a> to help you set up and enhance your first Service.

In particular, right after installation you might want to:

- <a href="https://docs.konghq.com/gateway/3.5.x/get-started/services-and-routes/">Create a service and a route</a>
- <a href="https://docs.konghq.com/gateway/3.5.x/get-started/rate-limiting/">Configure a plugin</a>
- <a href="https://docs.konghq.com/gateway/3.5.x/get-started/key-authentication/">Secure your services with authentication</a>

## Clean up containers

```
docker kill kong-gateway
docker kill kong-database
docker container rm kong-gateway
docker container rm kong-database
docker network rm kong-net
```


# Konga Setup

```
$ docker pull pantsel/konga
$ docker run -p 1337:1337 \
             --network {{kong-network}} \ // optional
             --name konga \
             -e "NODE_ENV=production" \ // or "development" | defaults to 'development'
             -e "TOKEN_SECRET={{somerandomstring}}" \
             pantsel/konga
```

Connect this Kong with Konga via configuring in the connection section,
use the host as http://host.docker.internal:8001 in case Kong is local. Create a service and route.

There is an example configuration file on the root folder.

```
.env_example
```

Just copy this to `.env` and make necessary changes to it. Note that this
`.env` file is in .gitignore so it won't go to VCS at any point.

## Environment variables
These are the general environment variables Konga uses.

| VAR                | DESCRIPTION                                                                                                                | VALUES                                 | DEFAULT                                      |
|--------------------|----------------------------------------------------------------------------------------------------------------------------|----------------------------------------|----------------------------------------------|
| HOST               | The IP address that will be bind by Konga's server                                                                               | -                                      | '0.0.0.0'                                         |
| PORT               | The port that will be used by Konga's server                                                                               | -                                      | 1337                                         |
| NODE_ENV           | The environment                                                                                                            | `production`,`development`             | `development`                                |
| SSL_KEY_PATH       | If you want to use SSL, this will be the absolute path to the .key file. Both `SSL_KEY_PATH` & `SSL_CRT_PATH` must be set. | -                                      | null                                         |
| SSL_CRT_PATH       | If you want to use SSL, this will be the absolute path to the .crt file. Both `SSL_KEY_PATH` & `SSL_CRT_PATH` must be set. | -                                      | null                                         |
| KONGA_HOOK_TIMEOUT | The time in ms that Konga will wait for startup tasks to finish before exiting the process.                                | -                                      | 60000                                        |
| DB_ADAPTER         | The database that Konga will use. If not set, the localDisk db will be used.              | `mongo`,`mysql`,`postgres`     | -                                            |
| DB_URI             | The full db connection string. Depends on `DB_ADAPTER`. If this is set, no other DB related var is needed.                 | -                                      | -                                            |
| DB_HOST            | If `DB_URI` is not specified, this is the database host. Depends on `DB_ADAPTER`.                                          | -                                      | localhost                                    |
| DB_PORT            | If `DB_URI` is not specified, this is the database port.  Depends on `DB_ADAPTER`.                                         | -                                      | DB default.                                  |
| DB_USER            | If `DB_URI` is not specified, this is the database user. Depends on `DB_ADAPTER`.                                          | -                                      | -                                            |
| DB_PASSWORD        | If `DB_URI` is not specified, this is the database user's password. Depends on `DB_ADAPTER`.                               | -                                      | -                                            |
| DB_DATABASE        | If `DB_URI` is not specified, this is the name of Konga's db.  Depends on `DB_ADAPTER`.                                    | -                                      | `konga_database`                             |
| DB_PG_SCHEMA       | If using postgres as a database, this is the schema that will be used.                                                     | -                                      | `public`                                     |
| KONGA_LOG_LEVEL    | The logging level                                                                                                          | `silly`,`debug`,`info`,`warn`,`error`  | `debug` on dev environment & `warn` on prod. |
| TOKEN_SECRET       | The secret that will be used to sign JWT tokens issued by Konga | - | - |
| NO_AUTH            | Run Konga without Authentication                                                                                           | true/false                             | -                                         |
| BASE_URL           | Define a base URL or relative path that Konga will be loaded from. Ex: www.example.com/konga                               | <string>                                     | -                                         |
| KONGA_SEED_USER_DATA_SOURCE_FILE           | Seed default users on first run. [Docs](./docs/SEED_DEFAULT_DATA.md).                               | <string>                                     | -                                         |
| KONGA_SEED_KONG_NODE_DATA_SOURCE_FILE      | Seed default Kong Admin API connections on first run [Docs](./docs/SEED_DEFAULT_DATA.md)                               | <string>                                     | -                                         |


```
docker run -p 1337:1337 --network kong-net --name konga -e "NODE_ENV=development" -e "TOKEN_SECRET=secret" pantsel/konga
```

- Connect this Kong with Konga via configuring in the connection section,
use the host as http://host.docker.internal:8001 in case Kong is local. Create a service and route.

# Kong Manager 

The quickest way to get started is using the quickstart script:

```
curl -Ls https://get.konghq.com/quickstart | bash -s -- -i kong -t latest
```

Finally, visit https://localhost:8002 to view Kong Manager.


# Add Custom Plugin to Kong

Create a folder say mandate_header and play both lua files inside it and copy this folder to Kong’s container in docker via the below command.

```
docker cp {path}/mandate_header kong_gateway:/usr/local/share/lua/5.1/kong/plugins
```

Create a kong.conf and add your newly created plugin and copy this as well.

```
plugins = bundled,mandate_header


docker cp {path}/kong.conf kong_gateway:/etc/kong/kong.conf
```

Restart Kong to load the plugin

```
docker restart kong_gateway
```
