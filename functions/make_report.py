import inngest
from inngest_client import inngest_client
from database import reports_db
from datetime import timedelta

@inngest_client.create_function(
    fn_id="make-report",
    trigger=inngest.TriggerEvent(event="report/requested"),
    retries=2
)
async def make_report(ctx: inngest.Context) -> dict:

    report_id = ctx.event.data["id"]
    topic = ctx.event.data["topic"]


    # Step 1
    
    await ctx.step.sleep("do-the-slow-work", timedelta(seconds=15))
    

    # Step 2 
    async def build_and_save():
        print("Step 2")
        if topic == "fail":
            raise ValueError("The report oven is broken!")
        if report_id in reports_db:
            reports_db[report_id]["status"] = "done"
            reports_db[report_id]["result"] = f"Report generated successfully for the topic : {topic}"
        return reports_db.get(report_id)

    
    report = await ctx.step.run(
        "build-report",
        build_and_save,
    )
    print("Step 2 done")

    return {"status": "completed", "report": report}