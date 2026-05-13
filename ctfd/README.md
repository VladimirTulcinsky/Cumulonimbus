# CTFd for Cumulonimbus

Two independent CTFd instances — one per cloud provider.

| Instance | URL                   |
|----------|-----------------------|
| AWS      | http://localhost:8000 |
| Azure    | http://localhost:8001 |

## Usage

```bash
python setup.py aws
python setup.py azure
```

That's it. Each command starts the containers, waits for CTFd to become ready,
completes the setup wizard, and seeds all matching challenges automatically.

Default credentials: `admin` / `cumulonimbus`.

## Existing install (custom password)

If CTFd was previously set up with a different password:

```bash
python setup.py aws   --admin-password <password>
python setup.py azure --admin-password <password>
```

## Teardown

```bash
docker compose down -v   # stops everything and wipes all data
```
