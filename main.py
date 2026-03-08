from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from fpdf import FPDF
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)

# Student Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    seat_number = db.Column(db.String(10), unique=True)
    monthly_fees = db.Column(db.Float, default=500.0)
    total_paid = db.Column(db.Float, default=0.0)

    @property
    def dues(self):
        return self.monthly_fees - self.total_paid

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form.get('name')
    seat = request.form.get('seat')
    new_student = Student(name=name, seat_number=seat)
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('index'))

# Fees Update karne ka route
@app.route('/pay/<int:id>', methods=['POST'])
def pay_fees(id):
    student = Student.query.get(id)
    amount = float(request.form.get('amount'))
    student.total_paid += amount
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
