import inngest.fast_api
from fastapi import FastAPI

from functions import all_functions
from inngest_client import inngest_client

app = FastAPI()

inngest.fast_api.serve(app, inngest_client, all_functions)


@app.get("/health")
def health_check():
    return {"status": "ok"}