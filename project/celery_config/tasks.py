# celery
from celery import shared_task
from project.celery_config.controllers import (
    calculate_linear_approximation,
    get_stock_data_from_db,
    save_estimation_to_db,
    sum_to_n # Si lo mantienes
)

# standard
import time
import math 

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
def estimate_stock_gains_job(user_id: str, purchase_id: str, stocks_purchased: dict):
   
    print(f"Iniciando estimación para user_id: {user_id}, purchase_id: {purchase_id}")
    
    total_estimated_gain = 0
    detailed_estimations = {}

    for symbol, quantity in stocks_purchased.items():
        print(f"Procesando stock: {symbol} (cantidad: {quantity})")
        try:
            # Obtener datos históricos de precios para el stock.
            historical_prices = get_stock_data_from_db(user_id, symbol)
            
            if not historical_prices or len(historical_prices) < 2:
                print(f"Advertencia: No hay suficientes datos para {symbol}. Saltando estimación.")
                detailed_estimations[symbol] = {
                    'quantity': quantity,
                    'estimated_price_next_month': None,
                    'estimated_gain': None,
                    'status': 'Not enough data'
                }
                continue

            #Calcular la aproximación lineal y proyectar el precio.
            projected_price_next_month = calculate_linear_approximation(
                [(item['timestamp'], item['price']) for item in historical_prices]
            )

            #Multiplicar por la cantidad comprada
            current_price = historical_prices[-1]['price']
            estimated_gain_per_stock = (projected_price_next_month - current_price) * quantity
            
            total_estimated_gain += estimated_gain_per_stock

            detailed_estimations[symbol] = {
                'quantity': quantity,
                'current_price': current_price,
                'estimated_price_next_month': projected_price_next_month,
                'estimated_gain': estimated_gain_per_stock,
                'status': 'Completed'
            }
            print(f"    Estimación para {symbol}: {estimated_gain_per_stock:.2f}")

        except Exception as e:
            print(f"    Error al estimar {symbol}: {e}")
            detailed_estimations[symbol] = {
                'quantity': quantity,
                'estimated_price_next_month': None,
                'estimated_gain': None,
                'status': f'Error: {str(e)}'
            }

    #Enviar las aproximaciones y el total para que se guarden
    estimation_result = {
        'total_estimated_gain': total_estimated_gain,
        'detailed_estimations': detailed_estimations
    }
    
    save_estimation_to_db(user_id, purchase_id, estimation_result)
    
    print(f"Estimación completa para user_id: {user_id}, purchase_id: {purchase_id}. Total: {total_estimated_gain:.2f}")
    return estimation_result
