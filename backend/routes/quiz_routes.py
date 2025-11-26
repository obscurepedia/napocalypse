from flask import request, jsonify
from . import quiz_bp
from database import db, Customer, QuizResponse
from datetime import datetime

@quiz_bp.route('/submit', methods=['POST'])
def submit_quiz():
    """
    Submit quiz responses and create/update customer
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'email', 'baby_age', 'sleep_situation', 'sleep_philosophy',
            'living_situation', 'parenting_setup', 'work_schedule',
            'biggest_challenge', 'sleep_associations'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get or create customer
        customer = Customer.query.filter_by(email=data['email']).first()
        
        if not customer:
            customer = Customer(
                email=data['email'],
                name=data.get('name', '')
            )
            db.session.add(customer)
            db.session.flush()  # Get customer ID
        
        # Create quiz response
        quiz_response = QuizResponse(
            customer_id=customer.id,
            baby_age=data['baby_age'],
            sleep_situation=data['sleep_situation'],
            sleep_philosophy=data['sleep_philosophy'],
            living_situation=data['living_situation'],
            parenting_setup=data['parenting_setup'],
            work_schedule=data['work_schedule'],
            biggest_challenge=data['biggest_challenge'],
            sleep_associations=data['sleep_associations']
        )
        
        db.session.add(quiz_response)
        db.session.commit()

        # Send Facebook CAPI Lead event (server-side)
        try:
            from services.facebook_capi import send_lead_event
            send_lead_event(
                user_email=customer.email,
                event_id=data.get('event_id'),  # For deduplication with browser pixel
                user_ip=request.headers.get('X-Forwarded-For', request.remote_addr),
                user_agent=request.headers.get('User-Agent'),
                event_source_url=request.headers.get('Referer'),
                fbc=data.get('fbc'),  # Facebook click ID
                fbp=data.get('fbp'),  # Facebook browser ID
                customer_id=customer.id
            )
        except Exception as fb_error:
            # Don't fail the request if Facebook tracking fails
            print(f"Facebook CAPI error (non-critical): {fb_error}")

        return jsonify({
            'success': True,
            'customer_id': customer.id,
            'quiz_id': quiz_response.id,
            'message': 'Quiz submitted successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error submitting quiz: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to submit quiz', 'details': str(e), 'success': False}), 500

@quiz_bp.route('/<int:quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    """
    Get quiz response by ID
    """
    try:
        quiz_response = QuizResponse.query.get(quiz_id)
        
        if not quiz_response:
            return jsonify({'error': 'Quiz not found'}), 404
        
        return jsonify({
            'success': True,
            'quiz': quiz_response.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error getting quiz: {str(e)}")
        return jsonify({'error': 'Failed to get quiz'}), 500

@quiz_bp.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer_quizzes(customer_id):
    """
    Get all quiz responses for a customer
    """
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        quizzes = QuizResponse.query.filter_by(customer_id=customer_id).all()
        
        return jsonify({
            'success': True,
            'customer': customer.to_dict(),
            'quizzes': [quiz.to_dict() for quiz in quizzes]
        }), 200
        
    except Exception as e:
        print(f"Error getting customer quizzes: {str(e)}")
        return jsonify({'error': 'Failed to get quizzes'}), 500