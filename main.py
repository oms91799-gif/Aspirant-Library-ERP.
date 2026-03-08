from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from fpdf import FPDF
import io
import os

app = Flask(__name__)
app.secret_key = 'aspirant_kashipur_pro_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aspirant_final_v4.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True)
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
        return 500.0 - self.total_paid

class PaymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    student_record_id = db.Column(db.Integer, db.ForeignKey('student.id'))

with app.app_context():
    db.create_all()

# --- Helpers ---
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
    uid = request.form.get('username')
    pwd = request.form.get('password')
    if uid == "admin" and pwd == "kashipur123":
        session['user'] = 'admin'
        return redirect(url_for('admin_dashboard'))
    student = Student.query.filter_by(student_id=uid, password=pwd).first()
    if student:
        session['user'] = student.id
        return redirect(url_for('student_portal', id=student.id))
    return "Ghalat ID ya Password! <a href='/'>Wapas jayein</a>"

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
    amt_str = request.form.get('amount')
    if amt_str:
        pay_rec = PaymentHistory(amount=float(amt_str), student_record_id=id)
        db.session.add(pay_rec)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/student/<int:id>')
def student_portal(id):
    if not session.get('user'): return redirect(url_for('home'))
    student = Student.query.get(id)
    return render_template('student_view.html', student=student)

@app.route('/receipt/<int:pay_id>')
def download_receipt(pay_id):
    payment = PaymentHistory.query.get(pay_id)
    student = Student.query.get(payment.student_record_id)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "ASPIRANT LIBRARY - FEE RECEIPT", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, "Kashipur, Uttarakhand", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(100, 10, f"Student: {student.name}")
    pdf.cell(90, 10, f"Date: {payment.date.strftime('%d-%m-%Y')}", ln=True)
    pdf.cell(100, 10, f"ID: {student.student_id}")
    pdf.cell(90, 10, f"Amount: Rs. {payment.amount}", ln=True)
    pdf.ln(10)
    pdf.cell(190, 10, f"Current Dues: Rs. {student.dues}", ln=True)
    output = io.BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin-1')
    output.write(pdf_output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f"Slip_{student.student_id}.pdf", mimetype='application/pdf')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
