import inngest.fast_api
from fastapi import FastAPI , status
from schemas.reportsSchema import ReportRequest
from functions import all_functions
from inngest_client import inngest_client
import uuid
from database import reports_db
from fastapi import HTTPException

app = FastAPI()

inngest.fast_api.serve(app, inngest_client, all_functions)


@app.get("/health")
def health_check():
    return {"status": "ok"}




@app.post("/reports", status_code=status.HTTP_202_ACCEPTED)
async def create_report(payload: ReportRequest):
    report_id = str(uuid.uuid4())  
    print("==============report_id", report_id)
    reports_db[report_id] = {
        "id": report_id,
        "topic": payload.topic,
        "status": "pending",
    }


    await inngest_client.send(
        inngest.Event(
            name="report/requested",
            data={
                "id": report_id,
                "topic": payload.topic,
            },
        )
    )

    return reports_db[report_id]




@app.get("/reports/{report_id}")
async def get_report(report_id: str):
     
    report = reports_db.get(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id '{report_id}' not found",
        )

    return report


    