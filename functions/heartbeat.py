import logging
import inngest
from inngest_client import inngest_client
from database import reports_db

logger = logging.getLogger("uvicorn.error")


@inngest_client.create_function(
    fn_id="heartbeat",
    trigger=inngest.TriggerCron(cron="* * * * *"),
)
async def heartbeat(ctx: inngest.Context) -> dict:
    async def log_summary():
        pending = sum(1 for r in reports_db.values() if r.get("status") == "pending")
        done = sum(1 for r in reports_db.values() if r.get("status") == "done")
        failed = sum(1 for r in reports_db.values() if r.get("status") == "failed")

        summary_msg = f"📊 Reports Summary -> Pending: {pending} | Done: {done} | Failed: {failed}"
        logger.info(summary_msg)

        return {"pending": pending, "done": done, "failed": failed}


    counts = await ctx.step.run("log-report-summary", log_summary)

    return {"status": "ok", "summary": counts}