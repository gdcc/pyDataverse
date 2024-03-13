# Running Dataverse in containers

Review the settings file:

```
cat .env
```

Start the containers:

```
docker-compose -f docker-compose-dev.yml up
```

Check the version returned by Dataverse:

```
curl http://localhost:8080/api/info/version
```

TODO: Set up Dataverse. Instructions for developers of Dataverse itself are at https://preview.guides.gdcc.io/en/develop/container/dev-usage.html

Please note that `.env` and `docker-compose-dev.yml` can be found upstream at https://github.com/IQSS/dataverse
