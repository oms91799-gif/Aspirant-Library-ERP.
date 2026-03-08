class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True) # Unique ID
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(20), default="12345") # Default login
    seat_number = db.Column(db.String(10), unique=True)
    joining_date = db.Column(db.DateTime, default=datetime.utcnow)
    monthly_fees = db.Column(db.Float, default=500.0)
    
    # Relationship to history
    payments = db.relationship('PaymentHistory', backref='student', lazy=True)

class PaymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
