# Fyle QuickBooks Desktop API
Django Rest Framework API for Fyle Quickbooks Desktop Integration


### Setup

* Download and install Docker desktop for Mac from [here.](https://www.docker.com/products/docker-desktop)

* If you're using a linux machine, please download docker according to the distrubution you're on.

* Copy docker-compose.yml.template as docker-compose.yml and add required secrets

    ```
    $ cp docker-compose.yml.template docker-compose.yml
    ```
  
* Setup environment variables in docker_compose.yml

    ```yaml
    environment:
      SECRET_KEY: thisisthedjangosecretkey
      ALLOWED_HOSTS: "*"
      DEBUG: "False"
      FYLE_TOKEN_URI: https://localhost:1234/oauth/token
      FYLE_BASE_URL: https://localhost:1234
      API_URL: http://localhost:8000/api
      FYLE_CLIENT_ID: client_id
      FYLE_CLIENT_SECRET: client_secret
      DB_NAME: qbd_db
      DB_USER: postgres
      DB_PASSWORD: postgres
      DB_HOST: db
      DB_PORT: 5432
   ```
  
* Build docker images

    ```
    docker-compose build api worker
    ```

* Run docker containers

    ```
    docker-compose up -d db api worker
    ```

* The database can be accessed by this command, on password prompt type `postgres`

    ```
    docker-compose run -e PGPASSWORD=postgres db psql -h db -U postgres qbd_db
    ```

* To tail the logs of a service you can do
    
    ```
    docker-compose logs -f <api / worker>
    ```

* To stop the containers

    ```
    docker-compose stop api worker
    ```

* To restart any containers - `would usually be needed with qcluster after you make any code changes`

    ```
    docker-compose restart worker
    ```

* To run bash inside any container for purpose of debugging do

    ```
    docker-compose exec api /bin/bash
    ```

### Running Tests

* Run the following commands

    1. docker-compose -f docker-compose-pipeline.yml build
    2. docker-compose -f docker-compose-pipeline.yml up -d
    3. docker-compose -f docker-compose-pipeline.yml exec api pytest tests/
