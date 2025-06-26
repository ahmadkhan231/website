
import json
import os
from datetime import datetime

class PaymentTracker:
    def __init__(self, filename='payments.json'):
        self.filename = filename
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        if not os.path.exists(self.filename):
            initial_data = {
                'total_payments': 0,
                'total_amount': 0,
                'payments': []
            }
            with open(self.filename, 'w') as f:
                json.dump(initial_data, f, indent=4)
    
    def add_payment(self, customer_name, customer_email, package_type, amount, transaction_id=None):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        
        payment_record = {
            'id': len(data['payments']) + 1,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'package_type': package_type,
            'amount': amount,
            'transaction_id': transaction_id,
            'payment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'payment_method': 'EasyPaisa',
            'status': 'completed'
        }
        
        data['payments'].append(payment_record)
        data['total_payments'] += 1
        data['total_amount'] += amount
        
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)
        
        return payment_record
    
    def get_payment_summary(self):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        return {
            'total_payments': data['total_payments'],
            'total_amount': data['total_amount'],
            'recent_payments': data['payments'][-5:]  # Last 5 payments
        }
