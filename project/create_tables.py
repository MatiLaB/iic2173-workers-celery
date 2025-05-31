from database import engine
from models import Base, StockPriceHistory, UserEstimation 
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

def init_db_and_insert_sample_data():
    print("Intentando crear tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas verificadas/creadas exitosamente.")

    db = Session(bind=engine)
    try:
        print("Eliminando datos existentes para insertar nuevos ejemplos...")
        db.query(StockPriceHistory).delete()
        db.query(UserEstimation).delete()
        db.commit()
        print("Datos existentes eliminados.")

        print("Insertando datos de ejemplo en stock_price_history...")
        today = datetime.now()
        sample_user_id = "test_user_1235"
        for symbol in ['AAPL', 'GOOG', 'MSFT']:
            for i in range(100):
                date_offset_days = i * 30 / 99
                date = today - timedelta(days=30 - date_offset_days)

                if symbol == 'AAPL': price = 150 + (date_offset_days * 0.5) + random.uniform(-2, 2)
                elif symbol == 'GOOG': price = 100 + (date_offset_days * 0.3) + random.uniform(-1, 1)
                elif symbol == 'MSFT': price = 200 + (date_offset_days * 0.7) + random.uniform(-3, 3)
                else: price = random.uniform(50, 250) # Precio base para otros símbolos

                db.add(StockPriceHistory(user_id=sample_user_id, symbol=symbol, timestamp=date, price=price))
        db.commit()
        print("Datos de ejemplo insertados en stock_price_history.")
    except Exception as e:
        db.rollback()
        print(f"Error durante la inicialización de la DB e inserción de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db_and_insert_sample_data()