import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import StockPriceHistory, UserEstimation
import requests 
import os 

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
    next_month_day_relative = last_day_relative + 30

    # Predecir el precio para el próximo mes
    projected_price = model.predict(np.array([[next_month_day_relative]]))[0]

    return projected_price

def get_stock_data_from_db(user_id: str, symbol: str, num_points: int = 100):
    db: Session = SessionLocal()
    try:
        today = datetime.now()
        one_month_ago = today - timedelta(days=30)
        historical_records = db.query(StockPriceHistory).\
            filter(
                StockPriceHistory.user_id == user_id,
                StockPriceHistory.symbol == symbol,
                StockPriceHistory.timestamp >= one_month_ago
            ).\
            order_by(StockPriceHistory.timestamp.asc()).\
            limit(num_points).all()

        if not historical_records:
            print(f"No se encontraron datos históricos para {symbol} del usuario {user_id} en el último mes.")
            return []

        return [{'timestamp': record.timestamp.timestamp(), 'price': record.price}
                for record in historical_records]
    except Exception as e:
        print(f"Error al obtener datos históricos para {symbol} del usuario {user_id}: {e}")
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

def fetch_stock_data_from_api(symbol: str) -> list:
    API_URL = os.getenv('API_URL', 'http://107.22.21.165:3000') 
    url = f"{API_URL}/stock_events/{symbol}"
    all_historical_data = []
    page = 1
    count = 100

       
    while True:
        params = {'page': page, 'count': count}
        print(f"Fetching stock data from {url} with params {params}")
        try:
            response = requests.get(url, params=params, timeout=15) 
            response.raise_for_status() 

            data = response.json()
                
            if 'data' in data and isinstance(data['data'], list):
                if not data['data']: 
                    break
                all_historical_data.extend(data['data'])
                    
                if len(data['data']) < count:
                    break
                page += 1
            else:
                print(f"Error: Formato de respuesta inesperado de la API de stocks: {data}")
                break 
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos históricos para {symbol} de la API externa: {e}")
            break
        except ValueError as e: # Error al decodificar JSON
            print(f"Error al decodificar JSON de la API de stocks: {e}")
            break
                
        return all_historical_data