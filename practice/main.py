
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
from payments import PaymentTracker
from email_service import EmailService
from sms_service import SMSService
from document_handler import DocumentHandler
from reviews_system import ReviewsSystem
from translation_service import TranslationService
import stripe
import json

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize services
payment_tracker = PaymentTracker()
email_service = EmailService()
sms_service = SMSService()
document_handler = DocumentHandler()
reviews_system = ReviewsSystem()
translation_service = TranslationService()

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_stripe_key')

@app.route('/')
def home():
    language = request.args.get('lang', 'en')
    reviews = reviews_system.get_approved_reviews()[-3:]  # Latest 3 reviews
    return render_template('index.html', reviews=reviews, language=language)

@app.route('/services')
def services():
    language = request.args.get('lang', 'en')
    return render_template('services.html', language=language)

@app.route('/packages')
def packages():
    language = request.args.get('lang', 'en')
    return render_template('packages.html', language=language)

@app.route('/contact')
def contact():
    language = request.args.get('lang', 'en')
    return render_template('contact.html', language=language)

@app.route('/reviews')
def reviews():
    language = request.args.get('lang', 'en')
    all_reviews = reviews_system.get_approved_reviews()
    return render_template('reviews.html', reviews=all_reviews, language=language)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.get_json()
    review = reviews_system.add_review(
        customer_name=data.get('name'),
        customer_email=data.get('email'),
        rating=data.get('rating'),
        comment=data.get('comment'),
        package_type=data.get('package_type', 'General')
    )
    return jsonify({'status': 'success', 'message': 'Review submitted for approval'})

@app.route('/book', methods=['POST'])
def book():
    data = request.get_json()
    
    # Extract package pricing
    package_prices = {
        'Hajj Premium': 4999,
        'Hajj Standard': 3499,
        'Hajj Economy': 2499,
        'Umrah Premium': 1999,
        'Umrah Standard': 1499,
        'Umrah Economy': 999
    }
    
    package_name = data.get('package')
    amount = package_prices.get(package_name, 0)
    
    # Store booking data in session
    session['booking_data'] = {
        'customer_name': data.get('fullName'),
        'customer_email': data.get('email'),
        'customer_phone': data.get('phone'),
        'package_type': package_name,
        'amount': amount
    }
    
    return jsonify({
        'status': 'success', 
        'message': 'Redirecting to payment...',
        'redirect_url': '/payment'
    })

@app.route('/payment')
def payment():
    booking_data = session.get('booking_data', {})
    if not booking_data:
        return redirect(url_for('packages'))
    return render_template('payment.html', booking_data=booking_data)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.get_json()
    booking_data = session.get('booking_data', {})
    
    # Record the payment
    payment_record = payment_tracker.add_payment(
        customer_name=booking_data.get('customer_name'),
        customer_email=booking_data.get('customer_email'),
        package_type=booking_data.get('package_type'),
        amount=booking_data.get('amount'),
        transaction_id=data.get('transaction_id', 'EP' + str(len(payment_tracker.get_payment_summary()['recent_payments']) + 1))
    )
    
    # Send confirmation email
    email_service.send_booking_confirmation(
        booking_data.get('customer_email'),
        booking_data.get('customer_name'),
        booking_data.get('package_type'),
        booking_data.get('amount')
    )
    
    # Send SMS notification
    sms_service.send_booking_sms(
        booking_data.get('customer_phone'),
        booking_data.get('customer_name'),
        booking_data.get('package_type')
    )
    
    # Clear session
    session.pop('booking_data', None)
    
    return jsonify({'status': 'success', 'payment_id': payment_record['id']})

@app.route('/upload_documents', methods=['GET', 'POST'])
def upload_documents():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        uploaded_files = []
        
        for doc_type in ['passport', 'visa', 'photo', 'medical']:
            if doc_type in request.files:
                file = request.files[doc_type]
                if file.filename:
                    filename = document_handler.save_document(file, customer_id, doc_type)
                    if filename:
                        uploaded_files.append(f"{doc_type}: {filename}")
        
        if uploaded_files:
            flash(f"Documents uploaded successfully: {', '.join(uploaded_files)}")
        else:
            flash("No documents were uploaded.")
        
        return redirect(url_for('upload_documents'))
    
    return render_template('upload_documents.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/payments')
def admin_payments():
    summary = payment_tracker.get_payment_summary()
    return render_template('admin_payments.html', summary=summary)

@app.route('/admin/reviews')
def admin_reviews():
    with open('reviews.json', 'r') as f:
        all_reviews = json.load(f)
    return render_template('admin_reviews.html', reviews=all_reviews)

@app.route('/admin/approve_review/<int:review_id>')
def approve_review(review_id):
    reviews_system.approve_review(review_id)
    flash("Review approved successfully!")
    return redirect(url_for('admin_reviews'))

@app.route('/admin/documents')
def admin_documents():
    if os.path.exists('documents.json'):
        with open('documents.json', 'r') as f:
            documents = json.load(f)
    else:
        documents = []
    return render_template('admin_documents.html', documents=documents)

@app.route('/stripe_payment', methods=['POST'])
def stripe_payment():
    try:
        data = request.get_json()
        booking_data = session.get('booking_data', {})
        
        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(booking_data.get('amount', 0) * 100),  # Convert to cents
            currency='usd',
            metadata={
                'customer_name': booking_data.get('customer_name'),
                'package_type': booking_data.get('package_type')
            }
        )
        
        return jsonify({'client_secret': intent.client_secret})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/translate', methods=['POST'])
def translate_api():
    data = request.get_json()
    text = data.get('text', '')
    target_language = data.get('language', 'ar')
    
    translated_text = translation_service.translate_text(text, target_language)
    return jsonify({'translated_text': translated_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
