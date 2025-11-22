## Turn apps ON (web + worker)
```
heroku ps:scale web=1 worker=1 -a flynnt-knapp
```

```
heroku ps:scale web=1 worker=1 -a planit-mini-dev
```

```
heroku ps:scale web=1 worker=1 -a planit-mini-prod
```

## Turn apps OFF (save money)

```
heroku ps:scale web=0 worker=0 -a flynnt-knapp
```

```
heroku ps:scale web=0 worker=0 -a planit-mini-dev
```

```
heroku ps:scale web=0 worker=0 -a planit-mini-prod
```

## Web-only mode (no Celery)
```
heroku ps:scale web=1 worker=0 -a flynnt-knapp
```

```
heroku ps:scale web=1 worker=0 -a planit-mini-dev
```

```
heroku ps:scale web=1 worker=0 -a planit-mini-prod
```

---

## Commands with explanations

### 1. Turn apps **ON** for demo/testing (web + Celery)

Use these when you want to **use the site and run background tasks** (emails, scheduled jobs, etc.):

```bash
heroku ps:scale web=1 worker=1 -a flynnt-knapp
heroku ps:scale web=1 worker=1 -a planit-mini-dev
heroku ps:scale web=1 worker=1 -a planit-mini-prod
```

- `web=1` → Django web app is live.
- `worker=1` → Celery worker **and beat** are running (because of your Procfile).

---

### 2. Turn apps **OFF** to save money (your safest default)

Use these **after you’re done** testing or demoing:

```bash
heroku ps:scale web=0 worker=0 -a flynnt-knapp
heroku ps:scale web=0 worker=0 -a planit-mini-dev
heroku ps:scale web=0 worker=0 -a planit-mini-prod
```

- `web=0` → No web dyno; visiting the URL shows “no web dynos running.”
- `worker=0` → No Celery worker or scheduled tasks.
- This is the **state you want most of the time** to minimize cost.

---

### 3. Web-only mode (no Celery / scheduled tasks)

Use these if you ever want to **just click around the site** without running any background tasks:

```bash
heroku ps:scale web=1 worker=0 -a flynnt-knapp
heroku ps:scale web=1 worker=0 -a planit-mini-dev
heroku ps:scale web=1 worker=0 -a planit-mini-prod
```

- `web=1` → Site works.
- `worker=0` → No Celery jobs or beat schedules run.

---

### 4. Eco dynos: sleep vs OFF

For all three apps, your dynos are **Eco**:

- If you set `web=1` (and/or `worker=1`) and then **do nothing**, the dyno will:
    - **Auto-sleep after ~30 minutes of inactivity.**
    - Stay at `=1` (just sleeping).
    - **Wake up automatically** when you visit the URL (small cold-start delay).

- If you run the OFF commands (`web=0 worker=0`):
    - The app is **truly off**.
    - It will **not** wake up by itself; you must run the ON commands again.

**Tiny rule of thumb for you:**

- Before using an app → `web=1 worker=1`
- After you’re done → `web=0 worker=0`

- If you forget, Eco will still sleep, but the OFF commands are your “belt and suspenders” to really keep costs down.
