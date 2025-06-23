from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from celery import Celery
from celery.result import AsyncResult
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware 
from database import SessionLocal
from celery_config import config
from datetime import datetime
from models import StockPriceHistory

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

origins = [
    "http://localhost",
    "http://localhost:3000", 
    "http://localhost:3001",
    "http://localhost:3002", 
    "http://127.0.0.1:3002",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
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
    
    db: Session = SessionLocal()
    try: 
        current_timestamp = datetime.now()

        for symbol, quantity in purchase_data.stocks.items():
            if hasattr(purchase_data, 'prices') and isinstance(purchase_data.prices, dict) and symbol in purchase_data.prices:
                price_at_purchase = purchase_data.prices[symbol]
            else:
                price_at_purchase = 0 

            new_price_record = StockPriceHistory(
                user_id=purchase_data.user_id,
                symbol=symbol,
                timestamp=current_timestamp,
                price=price_at_purchase
            )
            db.add(new_price_record)

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Error al guardar datos de compra en StockPriceHistory: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al procesar el job: {e}")
    finally:
        db.close()

    task = celery_app.send_task(
        'celery_config.tasks.estimate_stock_gains_job',
        args=[purchase_data.user_id, purchase_data.purchase_id, purchase_data.stocks]
    )
    
    return {"job_id": task.id, "message": "Job enqueued successfully."}

@app.get("/job/{job_id}", summary="Get job status y resultado")
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


