from app import app
from database import Customer, QuizResponse, Order
import json

with app.app_context():
    customer = Customer.query.get(3)
    if customer:
        print(f'Customer: {customer.name}')
        print(f'Baby Name in Customer table: {customer.baby_name}')
        print('\n' + '='*70)

        # Check quiz responses
        if customer.quiz_responses:
            for qr in customer.quiz_responses:
                print(f'\nQuiz Response ID: {qr.id}')
                print(f'Created: {qr.created_at}')
                if hasattr(qr, 'quiz_data') and qr.quiz_data:
                    print('\nQuiz Data:')
                    data = json.loads(qr.quiz_data) if isinstance(qr.quiz_data, str) else qr.quiz_data
                    for key, value in data.items():
                        print(f'  {key}: {value}')

        print('\n' + '='*70)

        # Check orders
        if customer.orders:
            for order in customer.orders:
                print(f'\nOrder ID: {order.id}')
                print(f'Created: {order.created_at}')
                if hasattr(order, 'personalization_data') and order.personalization_data:
                    print('\nPersonalization Data:')
                    data = json.loads(order.personalization_data) if isinstance(order.personalization_data, str) else order.personalization_data
                    for key, value in data.items():
                        print(f'  {key}: {value}')
