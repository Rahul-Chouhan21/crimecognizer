import pandas as pd
from deep_translator import GoogleTranslator
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import pickle
from functools import wraps
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random value

# Database configuration for MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/crimecognizer'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Models
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(50), primary_key=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Now stores plain text password
    name = db.Column(db.String(100))
    role = db.Column(db.String(50))

class Complaint(db.Model):
    __tablename__ = 'complaint'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15))
    incident_description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class FIR(db.Model):
    __tablename__ = 'fir'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    father_name = db.Column(db.String(100))
    present_address = db.Column(db.Text)
    district = db.Column(db.String(100))
    police_station = db.Column(db.String(100))
    incident_district = db.Column(db.String(100))
    incident_police_station = db.Column(db.String(100))
    nature_of_complaint = db.Column(db.Text)
    complaint_type = db.Column(db.String(100))
    fir_content = db.Column(db.Text)
    fir_file_path = db.Column(db.String(255))
    evidence_file_path = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

with app.app_context():
    db.create_all()

# DEMO USERS (run once to insert demo users)
def insert_demo_users():
    demo_users = [
        {"user_id": "bhopal01", "password": "@Bhopal2025", "name": "Bhopal Officer", "role": "Inspector"},
        {"user_id": "indore02", "password": "@Indore2025", "name": "Indore Officer", "role": "Inspector"},
        {"user_id": "gwalior03", "password": "@Gwalior2025", "name": "Gwalior Officer", "role": "Inspector"},
        {"user_id": "jabalpur04", "password": "@Jabalpur2025", "name": "Jabalpur Officer", "role": "Inspector"},
        {"user_id": "ujjain05", "password": "@Ujjain2025", "name": "Ujjain Officer", "role": "Inspector"}
    ]
    for u in demo_users:
        user = User.query.filter_by(user_id=u["user_id"]).first()
        if not user:
            user = User(
                user_id=u["user_id"],
                password_hash=u["password"],
                name=u["name"],
                role=u["role"]
            )
            db.session.add(user)
        else:
            user.password_hash = u["password"]
            user.name = u["name"]
            user.role = u["role"]
    db.session.commit()
# Uncomment the next line and run once to insert demo users, then comment again
with app.app_context(): insert_demo_users()

# Load model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# Load original dataset for lookups
df = pd.read_csv("IPC_Complaint_Synthetic_Dataset_Enhanced.csv")

def get_info(ipc_section):
    row = df[df['ipc_section'] == ipc_section].iloc[0]
    return row['explanation'], row['punishment'], row['crime_intensity'], row['suggested_ipcs'], row['category'], row['act_name']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/complaint_page')
@login_required
def complaint_page():
    return render_template('complaint_page.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        user = User.query.filter_by(user_id=user_id).first()
        if user and user.password_hash == password:
            session['user_id'] = user.user_id
            session['name'] = user.name
            session['role'] = user.role
            return redirect(url_for('complaint_page'))
        else:
            flash('Invalid user ID or password')
            return redirect(url_for('login'))
    # If already logged in, redirect to complaint_page
    if 'user_id' in session:
        return redirect(url_for('complaint_page'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/complaint')
def complaint():
    return render_template('complaint.html')


@app.route('/fir_registration', methods=['POST'])
def store_fir():
    form = request.form
    files = request.files
    fir_file = files.get('fir_file')
    evidence_file = files.get('evidence_file')
    fir_file_path = None
    evidence_file_path = None
    if fir_file:
        fir_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(fir_file.filename))
        fir_file.save(fir_file_path)
    if evidence_file:
        evidence_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(evidence_file.filename))
        evidence_file.save(evidence_file_path)
    fir = FIR(
        name=form.get('name'),
        email=form.get('email'),
        age=form.get('age'),
        gender=form.get('gender'),
        father_name=form.get('father_name'),
        present_address=form.get('present_address'),
        district=form.get('district'),
        police_station=form.get('police_station'),
        incident_district=form.get('incident_district'),
        incident_police_station=form.get('incident_police_station'),
        nature_of_complaint=form.get('nature_of_complaint'),
        complaint_type=form.get('complaint_type'),
        fir_content=form.get('fir_content'),
        fir_file_path=fir_file_path,
        evidence_file_path=evidence_file_path
    )
    db.session.add(fir)
    db.session.commit()
    flash('FIR stored successfully!')
    return redirect(url_for('thankyou'))

@app.route('/fir_registration')
def fir_registration():
    return render_template('fir_registration.html')

@app.route('/analyse')
def analyse():
    return render_template('analyse.html')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')
# Restore /complaint POST route
@app.route('/complaint', methods=['POST'])
def store_complaint():
    name = request.form.get('name')
    contact = request.form.get('contact')
    incident_description = request.form.get('complaint') or request.form.get('incident_description')
    if not name or not incident_description:
        flash('Name and description are required.')
        return redirect(url_for('complaint_page'))
    complaint = Complaint(name=name, contact=contact, incident_description=incident_description)
    db.session.add(complaint)
    db.session.commit()
    flash('Complaint stored successfully!')
    try:
        complaint_original = incident_description
        complaint_translated = GoogleTranslator(source='auto', target='en').translate(complaint_original)
        predicted_ipc = model.predict([complaint_translated])[0]
        explanation, punishment, crime_intensity, suggested_ipcs, category, act_name = get_info(predicted_ipc)
        return render_template("result.html", complaint=complaint_original, translated=complaint_translated, ipc=predicted_ipc,
                               explanation=explanation, punishment=punishment,
                               intensity=crime_intensity, suggested_ipcs=suggested_ipcs, category=category, act_name=act_name)
    except Exception as e:
        print("Error:", e)
        return render_template('erroe.html')
@app.route('/error')
def error():
    return render_template('erroe.html')

@app.route("/result", methods=["POST"])
def result():
    try:
        complaint_original = request.form['complaint']
        complaint_translated = GoogleTranslator(source='auto', target='en').translate(complaint_original)
        predicted_ipc = model.predict([complaint_translated])[0]

        explanation, punishment, crime_intensity, suggested_ipcs, category, act_name = get_info(predicted_ipc)

        return render_template("result.html", complaint=complaint_original, translated=complaint_translated, ipc=predicted_ipc,
                               explanation=explanation, punishment=punishment,
                               intensity=crime_intensity, suggested_ipcs=suggested_ipcs, category=category, act_name=act_name)
    except Exception as e:
        print("Error:", e)
        return render_template('erroe.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin Panel Routes
@app.route('/admin')
@login_required
def admin_panel():
    # Check if user has admin privileges
    if session.get('role') != 'Inspector':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('complaint_page'))
    
    # Get all complaints and FIRs
    complaints = Complaint.query.order_by(Complaint.timestamp.desc()).all()
    firs = FIR.query.order_by(FIR.timestamp.desc()).all()
    
    return render_template('admin_panel.html', complaints=complaints, firs=firs)

@app.route('/admin/complaints')
@login_required
def admin_complaints():
    if session.get('role') != 'Inspector':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('complaint_page'))
    
    complaints = Complaint.query.order_by(Complaint.timestamp.desc()).all()
    return render_template('admin_complaints.html', complaints=complaints)

@app.route('/admin/firs')
@login_required
def admin_firs():
    if session.get('role') != 'Inspector':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('complaint_page'))
    
    firs = FIR.query.order_by(FIR.timestamp.desc()).all()
    return render_template('admin_firs.html', firs=firs)

@app.route('/admin/complaint/<int:complaint_id>')
@login_required
def view_complaint(complaint_id):
    if session.get('role') != 'Inspector':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('complaint_page'))
    
    complaint = Complaint.query.get_or_404(complaint_id)
    return render_template('view_complaint.html', complaint=complaint)

@app.route('/admin/fir/<int:fir_id>')
@login_required
def view_fir(fir_id):
    if session.get('role') != 'Inspector':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('complaint_page'))
    
    fir = FIR.query.get_or_404(fir_id)
    return render_template('view_fir.html', fir=fir)

@app.route('/admin/delete_complaint/<int:complaint_id>', methods=['POST'])
@login_required
def delete_complaint(complaint_id):
    if session.get('role') != 'Inspector':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('admin_panel'))
    
    complaint = Complaint.query.get_or_404(complaint_id)
    db.session.delete(complaint)
    db.session.commit()
    flash('Complaint deleted successfully!')
    return redirect(url_for('admin_complaints'))

@app.route('/admin/delete_fir/<int:fir_id>', methods=['POST'])
@login_required
def delete_fir(fir_id):
    if session.get('role') != 'Inspector':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('admin_panel'))
    
    fir = FIR.query.get_or_404(fir_id)
    
    # Delete associated files
    if fir.fir_file_path and os.path.exists(fir.fir_file_path):
        os.remove(fir.fir_file_path)
    if fir.evidence_file_path and os.path.exists(fir.evidence_file_path):
        os.remove(fir.evidence_file_path)
    
    db.session.delete(fir)
    db.session.commit()
    flash('FIR deleted successfully!')
    return redirect(url_for('admin_firs'))

# Serve uploaded files
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
