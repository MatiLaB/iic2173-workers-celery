# project/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import json
import boto3 


def load_config_from_secrets_manager(secret_name):
    region_name = os.getenv("AWS_REGION", "us-east-1") 

    client = boto3.client('secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        print(f"ERROR: No se pudo recuperar el secreto '{secret_name}' de Secrets Manager: {e}")
        raise

    if 'SecretString' in get_secret_value_response:
        return json.loads(get_secret_value_response['SecretString'])
    else:
        raise ValueError("El secreto no contiene SecretString (posiblemente es binario o está vacío).")


APP_CONFIG_SECRET_NAME = 'jobmaster-worker' 
_app_config = {}
try:
    _app_config = load_config_from_secrets_manager(APP_CONFIG_SECRET_NAME)
    print("INFO: Configuración cargada exitosamente desde AWS Secrets Manager.")
except Exception as e:
    print(f"ADVERTENCIA: No se pudo cargar la configuración de AWS Secrets Manager. La aplicación intentará usar variables de entorno del sistema. Error: {e}")


DB_NAME = _app_config.get("DB_NAME", os.getenv("DB_NAME", "name_db_stocks"))
DB_USER = _app_config.get("DB_USER", os.getenv("DB_USER", "user_stocks"))
DB_PASSWORD = _app_config.get("DB_PASSWORD", os.getenv("DB_PASSWORD", "stock_password"))
DB_HOST = _app_config.get("DB_HOST", os.getenv("DB_HOST", "postgres"))
DB_PORT = _app_config.get("DB_PORT", os.getenv("DB_PORT", "5432"))

REDIS_HOST = _app_config.get("REDIS_HOST", os.getenv("REDIS_HOST", "redis-broker"))
REDIS_PORT = _app_config.get("REDIS_PORT", os.getenv("REDIS_PORT", "6379"))
REDIS_DB = _app_config.get("REDIS_DB", os.getenv("REDIS_DB", "0"))
CELERY_BROKER_URL = _app_config.get("CELERY_BROKER_URL", os.getenv("CELERY_BROKER_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"))
CELERY_RESULT_BACKEND = _app_config.get("CELERY_RESULT_BACKEND", os.getenv("CELERY_RESULT_BACKEND", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"))
JWT_SECRET = _app_config.get("JWT_SECRET", os.getenv("JWT_SECRET", "default_jwt_secret"))
GROUP_ID = _app_config.get("GROUP_ID", os.getenv("GROUP_ID", "10"))
PORT = _app_config.get("PORT", os.getenv("PORT", "8000"))


print(f"DEBUG: DB_HOST: {DB_HOST}, DB_PORT: {DB_PORT}, DB_NAME: {DB_NAME}")
print(f"DEBUG: REDIS_HOST: {REDIS_HOST}, REDIS_PORT: {REDIS_PORT}, REDIS_DB: {REDIS_DB}")
print(f"DEBUG: CELERY_BROKER_URL: {CELERY_BROKER_URL}")
print(f"DEBUG: CELERY_RESULT_BACKEND: {CELERY_RESULT_BACKEND}")
print(f"DEBUG: SQLALCHEMY_DATABASE_URL: {SQLALCHEMY_DATABASE_URL}")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()