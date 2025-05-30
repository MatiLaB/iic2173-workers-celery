import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import StockPriceHistory, UserEstimatio

def sum_to_n(number):
    sum = 0
    for i in range(1, number + 1):
        sum += i
    return sum

def calculate_linear_approximation(prices_and_dates):
    if len(prices_and_dates) < 2:
        raise ValueError("Not enough data points for linear approximation.")

    prices_and_dates.sort(key=lambda x: x[0])

    df = pd.DataFrame(prices_and_dates, columns=['timestamp', 'price'])

    df['days_since_start'] = (df['timestamp'] - df['timestamp'].min()) / (24 * 60 * 60)

    X = df[['days_since_start']].values
    y = df['price'].values

    model = LinearRegression()
    model.fit(X, y)

    last_day_relative = df['days_since_start'].max()
    next_month_day_relative = last_day_relative + 30 # Proyectar 30 días hacia adelante

    # Predecir el precio para el próximo mes
    projected_price = model.predict(np.array([[next_month_day_relative]]))[0]

    return projected_price

def get_stock_data_from_db(symbol: str, num_points: int = 100):
    db: Session = SessionLocal() 
    try:
        today = datetime.now()
        one_month_ago = today - timedelta(days=30)
        historical_records = db.query(StockPriceHistory).\
            filter(StockPriceHistory.symbol == symbol,
                   StockPriceHistory.timestamp >= one_month_ago).\
            order_by(StockPriceHistory.timestamp.asc()).\
            limit(num_points).all() # Limitamos para la regresión lineal

        if not historical_records:
            print(f"No se encontraron datos históricos para {symbol} en el último mes.")
            return [] # Retorna una lista vacía si no hay datos

    
        return [{'timestamp': record.timestamp.timestamp(), 'price': record.price}
                for record in historical_records]
    except Exception as e:
        print(f"Error al obtener datos históricos para {symbol}: {e}")
        return []
    finally:
        db.close() 


def save_estimation_to_db(user_id: str, purchase_id: str, estimations: dict):

    db: Session = SessionLocal()
    try:
        new_estimation = UserEstimation(
            user_id=user_id,
            purchase_id=purchase_id,
            total_estimated_gain=estimations['total_estimated_gain'],
            detailed_estimations_json=estimations['detailed_estimations'], 
            created_at=datetime.now()
        )
        db.add(new_estimation)
        db.commit() 
        db.refresh(new_estimation) 
        print(f"Estimaciones guardadas exitosamente en la DB para compra {purchase_id}")
    except Exception as e:
        db.rollback() 
        print(f"Error al guardar estimaciones en la DB para compra {purchase_id}: {e}")
    finally:
        db.close()