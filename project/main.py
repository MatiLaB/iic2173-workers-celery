from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from celery import Celery
from celery.result import AsyncResult
import os
import uuid

from celery_config import config

celery_app = Celery(
    'job_master_celery_app',
    broker=config.broker_url,
    backend=config.result_backend
)
celery_app.conf.update(
    accept_content=config.accept_content,
    task_serializer=config.CELERY_SERIALIZER,
    result_serializer=config.result_serializer,
    timezone=config.timezone,
    imports=config.imports,
    beat_schedule=config.CELERY_BEAT_SCHEDULE
)

app = FastAPI(
    title="JobMaster Service for Stock Estimations",
    description="API for managing and tracking asynchronous stock estimation jobs.",
    version="1.0.0"
)

# Modelo de Pydantic para la entrada del POST /job
class StockPurchaseData(BaseModel):
    user_id: str
    purchase_id: str = None # Puede ser generado por el frontend o aquí
    stocks: dict # e.g., {"AAPL": 10, "GOOG": 5}



@app.get("/heartbeat", summary="Check service operational status")
async def heartbeat():
    return {"status": True, "message": "JobMaster service está operando."}

@app.post("/job", summary="Submit a new job for stock estimation")
async def create_job(purchase_data: StockPurchaseData):
    if not purchase_data.purchase_id:
        purchase_data.purchase_id = str(uuid.uuid4()) 
    task = celery_app.send_task(
        'celery_config.tasks.estimate_stock_gains_job',
        args=[purchase_data.user_id, purchase_data.purchase_id, purchase_data.stocks]
    )
    
    return {"job_id": task.id, "message": "Job enqueued successfully."}

@app.get("/job/{job_id}", summary="Get job status and result")
async def get_job_status(job_id: str):
    task_result = AsyncResult(job_id, app=celery_app)

    if not task_result.ready():
        return {
            "job_id": job_id,
            "status": task_result.status,
            "result": None,
            "message": f"Job is currently {task_result.status.lower()}."
        }
    else:
        if task_result.successful():
            return {
                "job_id": job_id,
                "status": task_result.status,
                "result": task_result.get(),
                "message": "Job completed successfully."
            }
        else:
            
            return {
                "job_id": job_id,
                "status": task_result.status,
                "result": None,
                "error": str(task_result.info), # Información del error
                "message": "Job failed."
            }