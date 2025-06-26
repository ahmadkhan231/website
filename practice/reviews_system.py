
import json
import os
from datetime import datetime

class ReviewsSystem:
    def __init__(self, reviews_file='reviews.json'):
        self.reviews_file = reviews_file
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        if not os.path.exists(self.reviews_file):
            with open(self.reviews_file, 'w') as f:
                json.dump([], f)
    
    def add_review(self, customer_name, customer_email, rating, comment, package_type):
        with open(self.reviews_file, 'r') as f:
            reviews = json.load(f)
        
        review = {
            'id': len(reviews) + 1,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'rating': rating,
            'comment': comment,
            'package_type': package_type,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'approved': False
        }
        
        reviews.append(review)
        
        with open(self.reviews_file, 'w') as f:
            json.dump(reviews, f, indent=4)
        
        return review
    
    def get_approved_reviews(self):
        with open(self.reviews_file, 'r') as f:
            reviews = json.load(f)
        
        return [review for review in reviews if review.get('approved', False)]
    
    def approve_review(self, review_id):
        with open(self.reviews_file, 'r') as f:
            reviews = json.load(f)
        
        for review in reviews:
            if review['id'] == review_id:
                review['approved'] = True
                break
        
        with open(self.reviews_file, 'w') as f:
            json.dump(reviews, f, indent=4)
