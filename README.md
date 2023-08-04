# Cumulonimbus: A Vulnerable Azure Environment

## How to use?

The application has only been tested on Linux (Ubuntu 22.04). The best option is to use the container which contains every required dependency. The container is available at: [Link to Container](TODO)

```shell
docker run -it --entrypoint /bin/bash cumulonimbus:latest
```


### How to authenticate?

**On Azure:**

```shell
./cnimbus.py azure authenticate --service-principal --client-id <client-id> --client-secret <client-secret> --tenant-id <tenant-id> --subscription-id <subscription-id>
```

**On AWS:**

```shell
./cnimbus.py aws authenticate --access-key-id <access-key-id> --secret-access-key <secret-access-key> [--session-token <session-token>]
```

### How to create a vulnerable app?

**On Azure:**

```shell
./cnimbus.py azure create --app-id <app-id>
```

**On AWS:**

```shell
./cnimbus.py aws create --app-id <app-id>
```

### How to destroy a vulnerable app?

**On Azure:**

```shell
./cnimbus.py azure destroy --app-id <app-id>
```
### Where is the information needed to start the scenario?
When a scenario is being created, essential information like user credentials, objectives, and more will be displayed in the terminal.

**For more help:**

**Bold:** For more help, run `./cnimbus.py -h`.
