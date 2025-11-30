from app import app
from database import Customer

with app.app_context():
    customer = Customer.query.get(3)
    if customer:
        print(f'Customer ID: {customer.id}')
        print(f'Name: {customer.name}')
        print(f'Email: {customer.email}')
        print(f'Baby Name: {customer.baby_name}')
        print('\nAll customer attributes:')
        for attr in dir(customer):
            if not attr.startswith('_') and not callable(getattr(customer, attr)):
                try:
                    value = getattr(customer, attr)
                    if value is not None and attr not in ['metadata', 'registry']:
                        print(f'  {attr}: {value}')
                except:
                    pass
