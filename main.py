from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from fpdf import FPDF
import io

app = Flask(__name__)
app.secret_key = 'aspirant_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_v2.db'
db = SQLAlchemy(app)

# --- Database Models ---
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True)  # Format: ASP2026-OM01
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(20), default="12345") 
    seat_number = db.Column(db.String(10), unique=True)
    monthly_fees = db.Column(db.Float, default=500.0)
    joining_date = db.Column(db.DateTime, default=datetime.utcnow)
    payments = db.relationship('PaymentHistory', backref='student', lazy=True)

    @property
    def total_paid(self):
        return sum(p.amount for p in self.payments)

    @property
    def dues(self):
        return self.monthly_fees - self.total_paid

class PaymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    student_record_id = db.Column(db.Integer, db.ForeignKey('student.id'))

with app.app_context():
    db.create_all()

# --- Helper: Auto ID Generator ---
def generate_id(name):
    count = Student.query.count() + 1
    year = datetime.now().year
    initials = "".join([n[0] for n in name.split()]).upper()
    return f"ASP{year}-{initials}{count:02d}"

# --- Routes ---

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Owner Login (Hardcoded for now)
    if username == "admin" and password == "kashipur123":
        session['user'] = 'admin'
        return redirect(url_for('admin_dashboard'))
    
    # Student Login
    student = Student.query.filter_by(student_id=username, password=password).first()
    if student:
        session['user'] = student.id
        return redirect(url_for('student_portal', id=student.id))
    
    return "Invalid Credentials!"

@app.route('/admin')
def admin_dashboard():
    if session.get('user') != 'admin': return redirect(url_for('home'))
    students = Student.query.all()
    return render_template('admin.html', students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form.get('name')
    seat = request.form.get('seat')
    sid = generate_id(name)
    new_s = Student(name=name, seat_number=seat, student_id=sid)
    db.session.add(new_s)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/pay/<int:id>', methods=['POST'])
def pay(id):
    amt = float(request.form.get('amount'))
    pay_rec = PaymentHistory(amount=amt, student_record_id=id)
    db.session.add(pay_rec)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/student/<int:id>')
def student_portal(id):
    student = Student.query.get(id)
    return render_template('student_view.html', student=student)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
