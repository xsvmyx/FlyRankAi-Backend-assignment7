# FlyRankAi-Backend-assignment7

A FastAPI application integrated with [Inngest](https://www.inngest.com/) for durable background functions.

The app exposes a **Reports API** that lets you request background-generated reports, poll their status, and monitors itself with a scheduled heartbeat — all powered by Inngest's durable execution engine.

---

## How to run

1. Start the Inngest Dev Server:
   ```bash
   npx inngest-cli@latest dev
   ```

2. Start the FastAPI app:
   ```bash
   uv run uvicorn main:app --reload
   ```

3. Open the Inngest Dev Server UI at `http://localhost:8288` to monitor function runs.

---

## API Endpoints

### `GET /health`
Returns the health status of the application.

**Response:**
```json
{ "status": "ok" }
```

---

### `POST /reports`
Submit a new report request. Triggers an Inngest background job that will generate the report asynchronously.

**Request body:**
```json
{ "topic": "your topic here" }
```

**Response** (`202 Accepted`):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "your topic here",
  "status": "pending"
}
```

> **Tip:** Send `"topic": "fail"` to intentionally trigger a failure and observe Inngest's retry behaviour.

---

### `GET /reports/{report_id}`
Poll the status of a report by its ID.

**Response (pending):**
```json
{
  "id": "550e8400-...",
  "topic": "your topic here",
  "status": "pending"
}
```

**Response (done):**
```json
{
  "id": "550e8400-...",
  "topic": "your topic here",
  "status": "done",
  "result": "Report generated successfully for the topic : your topic here"
}
```

**Response (not found):** `404 Not Found`

---

## Inngest Functions

### `make-report` — triggered by `report/requested`

This is the core background function that processes a report. It runs in two durable steps:

| Step | Name | What it does |
|------|------|-------------|
| 1 | `do-the-slow-work` | Sleeps for 15 seconds (simulates heavy work) |
| 2 | `build-report` | Writes the result to the in-memory DB, marks status as `"done"` |

- **Retries:** 2
- **Failure mode:** if `topic == "fail"`, step 2 raises a `ValueError` and Inngest retries up to 2 times before marking the run as failed.

---

### `heartbeat` — triggered every minute (cron)

A scheduled Inngest function that runs every minute and logs a summary of all reports in the in-memory database.

**Logged output example:**
```
📊 Reports Summary -> Pending: 1 | Done: 3 | Failed: 0
```

Returns `{ "status": "ok", "summary": { "pending": 1, "done": 3, "failed": 0 } }`.

---

### `say-hello` — manual invocation

A simple demo function you can invoke manually from the Inngest Dev Server UI to test that the integration is working correctly.

---

## What the logs mean

When a report is created and Inngest processes it, you will see requests like this in the FastAPI logs:

```
POST /api/inngest?fnId=report-api-make-report&stepId=do-the-slow-work  →  206 Partial Content
PUT  /api/inngest                                                        →  200 OK
POST /api/inngest?fnId=report-api-make-report&stepId=build-report       →  200 OK
```

### Request 1 — `POST` → `206 Partial Content`

Inngest calls your function for the first time.  
The function hits `step.sleep(...)`, which tells Inngest _"pause here and come back after 15 seconds"_.  
The `206` response means: **"I ran part of the work, but I'm not done yet — please wait and call me again."**

### Request 2 — `PUT` → `200 OK`

Inngest re-syncs with your app to confirm it is still alive.  
The `200` response means: **"App is alive and ready."**

### Request 3 — `POST` → `200 OK`

Inngest calls your function again to resume from the saved checkpoint (after the sleep).  
This time the function runs step 2 to completion.  
The `200` response means: **"Function completed successfully."**

---

## Project structure

```
├── main.py                    # FastAPI app — routes & Inngest serve()
├── inngest_client.py          # Shared Inngest client instance
├── database.py                # In-memory reports store (dict)
├── schemas/
│   └── reportsSchema.py       # Pydantic model for POST /reports
└── functions/
    ├── __init__.py            # Exports all Inngest functions
    ├── say_hello.py           # Demo "say-hello" function
    ├── make_report.py         # "make-report" — core report pipeline
    └── heartbeat.py          # "heartbeat" — cron every minute
```

---

### Cron Schedule Reference

* To run the heartbeat function every day at 08:00, use the cron expression `0 8 * * *`.
* To run the heartbeat function every Sunday at 22:00, use the cron expression `0 22 * * 0`.



