import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

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

def get_stock_data_from_db(user_id, symbol):
    # Último mes de datos (simulados)
    today = datetime.now()
    one_month_ago = today - timedelta(days=30)
    #falta terminar esto

def save_estimation_to_db(user_id, purchase_id, estimations):

    print(f"Guardando estimaciones para usuario {user_id}, compra {purchase_id}: {estimations}")
    #Falta terminar esto
    # Aquí iría la lógica para interactuar con tu ORM/DB

    pass