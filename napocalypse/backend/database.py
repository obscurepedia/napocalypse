from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()

# Models
class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    stripe_customer_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quiz_responses = db.relationship('QuizResponse', backref='customer', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }

class QuizResponse(db.Model):
    __tablename__ = 'quiz_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    baby_age = db.Column(db.String(50), nullable=False)
    sleep_situation = db.Column(db.String(100), nullable=False)
    sleep_philosophy = db.Column(db.String(100), nullable=False)
    living_situation = db.Column(db.String(100), nullable=False)
    parenting_setup = db.Column(db.String(100), nullable=False)
    work_schedule = db.Column(db.String(100), nullable=False)
    biggest_challenge = db.Column(db.String(100), nullable=False)
    sleep_associations = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'baby_age': self.baby_age,
            'sleep_situation': self.sleep_situation,
            'sleep_philosophy': self.sleep_philosophy,
            'living_situation': self.living_situation,
            'parenting_setup': self.parenting_setup,
            'work_schedule': self.work_schedule,
            'biggest_challenge': self.biggest_challenge,
            'sleep_associations': self.sleep_associations,
            'created_at': self.created_at.isoformat()
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    stripe_payment_intent_id = db.Column(db.String(255), unique=True)
    stripe_checkout_session_id = db.Column(db.String(255), unique=True)
    amount = db.Column(db.Integer, nullable=False)  # in cents
    currency = db.Column(db.String(3), default='usd')
    status = db.Column(db.String(50), default='pending')
    pdf_generated = db.Column(db.Boolean, default=False)
    pdf_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    modules = db.relationship('ModuleAssigned', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'pdf_generated': self.pdf_generated,
            'created_at': self.created_at.isoformat()
        }

class ModuleAssigned(db.Model):
    __tablename__ = 'modules_assigned'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    module_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'module_name': self.module_name,
            'created_at': self.created_at.isoformat()
        }

class EmailSequence(db.Model):
    __tablename__ = 'email_sequences'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    email_type = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(255))
    sent_at = db.Column(db.DateTime)
    opened = db.Column(db.Boolean, default=False)
    clicked = db.Column(db.Boolean, default=False)
    scheduled_for = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='pending')
    
    def to_dict(self):
        return {
            'id': self.id,
            'day_number': self.day_number,
            'email_type': self.email_type,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }