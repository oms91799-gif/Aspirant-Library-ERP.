from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from fpdf import FPDF
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    seat_number = db.Column(db.String(10), unique=True)
    monthly_fees = db.Column(db.Float, default=500.0)
    total_paid = db.Column(db.Float, default=0.0)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)

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

@app.route('/pay/<int:id>', methods=['POST'])
def pay_fees(id):
    student = Student.query.get(id)
    amount = float(request.form.get('amount'))
    student.total_paid += amount
    db.session.commit()
    return redirect(url_for('index'))

# --- PDF Receipt Logic ---
@app.route('/receipt/<int:id>')
def download_receipt(id):
    student = Student.query.get(id)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Header
    pdf.cell(190, 10, "ASPIRANT LIBRARY - FEE RECEIPT", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, "Aharpura Road, Kashipur, Uttarakhand", ln=True, align='C')
    pdf.ln(10)
    
    # Details
    pdf.cell(100, 10, f"Student Name: {student.name}")
    pdf.cell(90, 10, f"Date: {datetime.now().strftime('%d-%m-%Y')}", ln=True)
    pdf.cell(100, 10, f"Seat Number: {student.seat_number}")
    pdf.cell(90, 10, f"Receipt ID: LIB-{student.id}", ln=True)
    pdf.ln(5)
    
    # Table-like Structure
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(95, 10, "Description", border=1, fill=True)
    pdf.cell(95, 10, "Amount (INR)", border=1, fill=True, ln=True)
    
    pdf.cell(95, 10, "Monthly Fees", border=1)
    pdf.cell(95, 10, f"Rs. {student.monthly_fees}", border=1, ln=True)
    
    pdf.cell(95, 10, "Total Paid", border=1)
    pdf.cell(95, 10, f"Rs. {student.total_paid}", border=1, ln=True)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(95, 10, "Remaining Dues", border=1)
    pdf.cell(95, 10, f"Rs. {student.dues}", border=1, ln=True)
    
    pdf.ln(20)
    pdf.cell(190, 10, "Authorized Signatory", align='R')

    # Send PDF as response
    output = io.BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin-1')
    output.write(pdf_output)
    output.seek(0)
    
    return send_file(output, as_attachment=True, download_name=f"Receipt_{student.name}.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
