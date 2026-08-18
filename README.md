# FlyRankAi-Backend-assignment7

A FastAPI application integrated with [Inngest](https://www.inngest.com/) for durable background functions.

## How to run

1. Start the Inngest Dev Server:
   ```bash
   npx inngest-cli@latest dev
   ```

2. Start the FastAPI app:
   ```bash
   uv run uvicorn main:app --reload
   ```

3. Open the Inngest Dev Server UI at `http://localhost:8288`, find the `say-hello` function, and click **Invoke**.

---

## What the logs mean

When you invoke the `say-hello` function, you will see 3 requests in the FastAPI logs:

```
POST /api/inngest?fnId=report-api-say-hello&stepId=step  →  206 Partial Content
PUT  /api/inngest                                         →  200 OK
POST /api/inngest?fnId=report-api-say-hello&stepId=step  →  200 OK
```

### Request 1 — `POST` → `206 Partial Content`

The Inngest Dev Server calls your function for the first time.  
The function hits `step.sleep(...)`, which tells Inngest *"pause here and come back later"*.  
The `206` response means: **"I ran part of the work, but I'm not done yet — please wait and call me again."**

### Request 2 — `PUT` → `200 OK`

the Inngest Dev Server re-syncs with your app to check it is still running and reachable.  
The `200` response means: **"App is alive and ready."**

### Request 3 — `POST` → `200 OK`

The Inngest Dev Server calls your function again to resume from where it paused (after the sleep).  
This time the function runs to completion and returns its result.  
The `200` response means: **"Function completed successfully."**

---

## Project structure

```
├── main.py              # FastAPI app entry point
├── inngest_client.py    # Shared Inngest client
└── functions/
    ├── __init__.py      # Exports all Inngest functions
    └── say_hello.py     # "say-hello" background function
```
