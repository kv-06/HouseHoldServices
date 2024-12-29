from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(25), nullable=False)
    status = db.Column(db.String(10), default='active') 




class Service(db.Model):
    __tablename__ = 'services'
    service_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    base_price = db.Column(db.Integer, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)  
    description = db.Column(db.String(40))

class Professional(db.Model):
    __tablename__ = 'professional'
    professional_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(30), unique=True)
    status = db.Column(db.String(10), default='active')  
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    approved = db.Column(db.String(10), default=False)
    proof = db.Column(db.String(70), default=False)

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    request_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.professional_id'), nullable=True)
    date_of_request = db.Column(db.String(20), nullable=False)
    date_of_completion = db.Column(db.String(20), nullable=True)
    service_status = db.Column(db.String(20), default='requested')  
    location = db.Column(db.String(30))

class Reviews(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('service_requests.request_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(50))
