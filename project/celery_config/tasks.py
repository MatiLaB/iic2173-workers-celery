# celery
from celery import shared_task
from .controllers import (
    calculate_linear_approximation,
    get_stock_data_from_db,
    save_estimation_to_db,
    sum_to_n,
    fetch_stock_data_from_api
)

# standard
import time
import math 
import numpy as np 
import requests 
import os
from datetime import datetime 

# The "shared_task" decorator allows creation
# of Celery tasks for reusable apps as it doesn't
# need the instance of the Celery app.
# @celery_app.task()
@shared_task()
def add(x, y):
    return x + y

@shared_task
def wait_and_return():
    time.sleep(20)
    return 'Hello World!'

@shared_task
def sum_to_n_job(number):
    result = sum_to_n(number)
    return result

@shared_task
def estimate_stock_gains_job(user_id: str, purchase_id: str, stocks_purchased: dict, purchase_prices: dict):
    
    total_estimated_gain = 0
    detailed_estimations = {}

    for symbol, quantity in stocks_purchased.items():
        print(f"Procesando stock: {symbol} (cantidad: {quantity})")
        try:
            historical_prices = fetch_stock_data_from_api(symbol)
            current_purchase_price = purchase_prices.get(symbol)
            if current_purchase_price is None:
                print(f"Advertencia: Precio de compra no encontrado para {symbol}. Saltando estimación para este stock.")
                detailed_estimations[symbol] = {
                    'quantity': quantity,
                    'estimated_price_next_month': None,
                    'estimated_gain': None,
                    'status': 'Purchase price missing'
                }
                continue

            if not historical_prices or len(historical_prices) < 2:
                print(f"Advertencia: No hay suficientes datos históricos para {symbol}. Saltando proyección.")
                detailed_estimations[symbol] = {
                    'quantity': quantity,
                    'purchase_price': current_purchase_price, 
                    'estimated_price_next_month': None,
                    'estimated_gain': None,
                    'status': 'Not enough historical data for projection'
                }
                continue

            processed_historical_data = []
            for item in historical_prices:
                try:
                    dt_object = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                    processed_historical_data.append((dt_object.timestamp(), item['price']))
                except (ValueError, KeyError) as ve:
                    print(f"Error procesando timestamp/precio para {symbol}: {ve} en item {item}")
                    continue


            projected_price_next_month_np = calculate_linear_approximation(processed_historical_data)
            projected_price_next_month = float(projected_price_next_month_np)

            estimated_gain_per_stock = (projected_price_next_month - current_purchase_price) * quantity
            estimated_gain_per_stock = float(estimated_gain_per_stock)
            
            total_estimated_gain += estimated_gain_per_stock

            detailed_estimations[symbol] = {
                'quantity': quantity,
                'purchase_price': current_purchase_price, 
                'estimated_price_next_month': projected_price_next_month,
                'estimated_gain': estimated_gain_per_stock,
                'status': 'Completed'
            }
            print(f"Estimación para {symbol}: Ganancia estimada = {estimated_gain_per_stock:.2f}")

        except Exception as e:
            print(f"    Error al estimar {symbol}: {e}")
            detailed_estimations[symbol] = {
                'quantity': quantity,
                'purchase_price': current_purchase_price,
                'estimated_price_next_month': None,
                'estimated_gain': None,
                'status': f'Error: {str(e)}'
            }

    estimation_result = {
        'total_estimated_gain': total_estimated_gain,
        'detailed_estimations': detailed_estimations
    }
    
    save_estimation_to_db(user_id, purchase_id, estimation_result)
    
    print(f"Estimación completa para user_id: {user_id}, purchase_id: {purchase_id}. Total: {total_estimated_gain:.2f}")
    return estimation_result
