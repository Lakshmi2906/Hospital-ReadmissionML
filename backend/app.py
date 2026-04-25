from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import joblib
import pandas as pd
import numpy as np
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
from datetime import datetime
import os
import threading

# Import your voice agent directly — no env flag needed
from twilio_integration import notify_caregiver as twilio_notify

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# ─── MongoDB ──────────────────────────────────────────────────────────────────
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client['hospital_readmission']
    users_collection       = db['users']
    patients_collection    = db['patients']
    predictions_collection = db['predictions']
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    users_collection       = None
    patients_collection    = None
    predictions_collection = None

# ─── ML Model ─────────────────────────────────────────────────────────────────
model_data = joblib.load('model.pkl')
model    = model_data['model']
scaler   = model_data['scaler']
features = model_data['features']

# ─── Demo users ───────────────────────────────────────────────────────────────
DEMO_USERS = {
    'admin':  'admin123',
    'doctor': 'doctor123',
    'nurse':  'nurse123'
}

# ─── Auth routes ──────────────────────────────────────────────────────────────
@app.route('/')
def login_page():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    fullname         = request.form.get('fullname')
    email            = request.form.get('email')
    username         = request.form.get('username')
    role             = request.form.get('role')
    specialization   = request.form.get('specialization', '')
    hospital         = request.form.get('hospital')
    password         = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        return render_template('register.html', error='Passwords do not match!')

    if users_collection is not None:
        if users_collection.find_one({'username': username}):
            return render_template('register.html', error='Username already exists!')
        if users_collection.find_one({'email': email}):
            return render_template('register.html', error='Email already registered!')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({
            'fullname':       fullname,
            'email':          email,
            'username':       username,
            'role':           role,
            'specialization': specialization if role in ['doctor', 'nurse'] else None,
            'hospital':       hospital,
            'password':       hashed_password,
            'created_at':     datetime.now()
        })
        return render_template('register.html', success='Registration successful! Please login.')
    else:
        return render_template('register.html', error='Database not available.')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in DEMO_USERS and DEMO_USERS[username] == password:
        session['username'] = username
        session['role']     = 'admin'
        return redirect(url_for('home'))

    if users_collection is not None:
        user = users_collection.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['username'] = username
            session['fullname'] = user['fullname']
            session['role']     = user.get('role', 'doctor')
            return redirect(url_for('home'))

    return render_template('login.html', error='Invalid username or password!')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ─── Dashboard routes ─────────────────────────────────────────────────────────
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    if session.get('role') == 'front_desk':
        return redirect(url_for('patient_dashboard'))
    return redirect(url_for('prediction_dashboard'))

@app.route('/patient-dashboard')
def patient_dashboard():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    if session.get('role') != 'front_desk':
        return redirect(url_for('home'))

    patients = []
    if patients_collection is not None:
        patients = list(patients_collection.find().sort('registered_at', -1))
    return render_template('patient_dashboard.html',
                           username=session.get('fullname', session['username']),
                           patients=patients)

@app.route('/prediction-dashboard')
def prediction_dashboard():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    if session.get('role') not in ['doctor', 'nurse', 'admin']:
        return redirect(url_for('home'))

    patients = []
    if patients_collection is not None:
        patients = list(patients_collection.find().sort('registered_at', -1))
    return render_template('index.html',
                           username=session.get('fullname', session['username']),
                           patients=patients)

# ─── Add patient ──────────────────────────────────────────────────────────────
@app.route('/add-patient', methods=['POST'])
def add_patient():
    if 'username' not in session or session.get('role') != 'front_desk':
        return jsonify({'error': 'Unauthorized'}), 403
    if patients_collection is None:
        return jsonify({'error': 'Database not available'}), 500

    try:
        patient_data = {
            'patient_name':             request.form.get('patient_name'),
            'age':                      int(request.form.get('age')),
            'gender':                   request.form.get('gender'),
            'phone':                    request.form.get('phone'),
            'address':                  request.form.get('address'),
            'language':                 request.form.get('language'),
            'literacy_level':           request.form.get('literacy_level'),
            'location_type':            request.form.get('location_type'),
            'has_phone':                request.form.get('has_phone') == 'yes',
            'caregiver_name':           request.form.get('caregiver_name'),
            'caregiver_phone':          request.form.get('caregiver_phone'),
            'caregiver_relationship':   request.form.get('caregiver_relationship'),
            'caregiver_can_read':       request.form.get('caregiver_can_read') == 'yes',
            'preferred_contact':        request.form.get('preferred_contact'),
            'alternative_contact_name': request.form.get('alternative_contact_name', ''),
            'alternative_contact_phone':request.form.get('alternative_contact_phone', ''),
            'hospital':                 session.get('hospital', 'City Hospital'),
            'registered_by':            session['username'],
            'registered_at':            datetime.now()
        }
        result = patients_collection.insert_one(patient_data)
        return jsonify({'success': True, 'patient_id': str(result.inserted_id)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ─── Predict ──────────────────────────────────────────────────────────────────
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.form

        input_data = {
            'age':              float(data['age']),
            'time_in_hospital': float(data['time_in_hospital']),
            'n_lab_procedures': float(data['n_lab_procedures']),
            'n_procedures':     float(data['n_procedures']),
            'n_medications':    float(data['n_medications']),
            'n_outpatient':     float(data['n_outpatient']),
            'n_inpatient':      float(data['n_inpatient']),
            'n_emergency':      float(data['n_emergency'])
        }

        df        = pd.DataFrame([input_data], columns=features)
        df_scaled = scaler.transform(df)

        prediction      = model.predict(df_scaled)[0]
        probability     = model.predict_proba(df_scaled)[0]
        result_label    = "Readmitted within 30 days" if prediction == 1 else "Not Readmitted"
        prob_percentage = probability[1] * 100

        # Save prediction to DB (without calling Twilio here — button does that)
        if predictions_collection is not None:
            prediction_doc = {
                'doctor_username':   session.get('username'),
                'prediction_date':   datetime.now(),
                'clinical_data':     input_data,
                'prediction_result': 'High Risk' if prediction == 1 else 'Low Risk',
                'probability':       prob_percentage,
                'caregiver_notified': False
            }
            patient_id = request.form.get('patient_id')
            if patient_id:
                prediction_doc['patient_id'] = ObjectId(patient_id)
            predictions_collection.insert_one(prediction_doc)

        return jsonify({
            'prediction':  result_label,
            'probability': f"{prob_percentage:.2f}%"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ─── Notify caregiver (triggered by the Notify button) ───────────────────────
@app.route('/notify-caregiver-call', methods=['POST'])
def notify_caregiver_call():

    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        patient_id        = request.form.get('patient_id', '').strip()
        prediction_result = request.form.get('prediction_result', '')

        if not patient_id:
            return jsonify({'success': False, 'error': 'No patient selected'}), 400

        if patients_collection is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 500

        # ── Fetch patient ──
        patient = patients_collection.find_one({'_id': ObjectId(patient_id)})
        if not patient:
            return jsonify({'success': False, 'error': 'Patient not found'}), 404

        # ── Risk logic ──
        is_high_risk = (
            'Readmitted' in prediction_result or
            'High Risk' in prediction_result
        )

        # ── Prepare data ──
        patient_data = {
            'patient_name':   patient.get('patient_name', 'Patient'),
            'age':            patient.get('age', ''),
            'caregiver_name': patient.get('caregiver_name', 'Caregiver'),
            'caregiver_phone':patient.get('caregiver_phone', ''),
            'hospital':       patient.get('hospital', 'City Hospital'),
            'language':       patient.get('language', 'English'),
            'literacy_level': patient.get('literacy_level', 'Literate'),
        }

        if not patient_data['caregiver_phone']:
            return jsonify({'success': False, 'error': 'No caregiver phone number'}), 400

        # ── Background call ──
        def run_call():
            try:
                result = twilio_notify(
                    patient_data=patient_data,
                    is_high_risk=is_high_risk
                )

                if predictions_collection is not None:

                    # ✅ Step 1: find latest prediction
                    latest = predictions_collection.find_one(
                        {
                            'patient_id': ObjectId(patient_id),
                            'caregiver_notified': False
                        },
                        sort=[('prediction_date', -1)]
                    )

                    # ✅ Step 2: update safely
                    if latest:
                        predictions_collection.update_one(
                            {'_id': latest['_id']},
                            {
                                '$set': {
                                    'caregiver_notified': result.get('success', False),
                                    'notification_method': result.get('method'),
                                    'notification_status': result.get('final_status'),
                                    'call_answered': result.get('call_answered', False),
                                    'notification_attempts': result.get('attempts', 1),
                                    'notification_sent_at': datetime.now()
                                }
                            }
                        )

            except Exception:
                import traceback
                traceback.print_exc()

        # ✅ START THREAD
        thread = threading.Thread(target=run_call, daemon=True)
        thread.start()

        # ✅ RESPONSE
        return jsonify({
            'success': True,
            'message': f"Call started for {patient_data['caregiver_name']}"
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

        # ── Run Twilio call in background thread ───────────────────────────────
        # This returns the HTTP response to the browser immediately.
        # The actual call (which can take 1-3 min with retries) runs in background.
        def run_call():
            try:
                result = twilio_notify(
                    patient_data = patient_data,
                    is_high_risk = is_high_risk,
                    max_retries  = 3,
                    retry_wait   = 120
                )
                # Update the prediction record with notification outcome
                if predictions_collection is not None:
                    predictions_collection.update_one(
                        {
                            'patient_id': ObjectId(patient_id),
                            'caregiver_notified': False
                        },
                        {'$set': {
                            'caregiver_notified':      result.get('success', False),
                            'notification_method':     result.get('method'),
                            'notification_status':     result.get('final_status'),
                            'call_answered':           result.get('call_answered', False),
                            'notification_attempts':   result.get('attempts', 0),
                            'notification_sent_at':    datetime.now()
                        }},
                        sort={'prediction_date', -1}   # update the most recent prediction
                    )
            except Exception as ex:
                print(f"❌ Background call error: {ex}")

        thread = threading.Thread(target=run_call, daemon=True)
        thread.start()

        # ── Respond immediately to the browser ────────────────────────────────
        return jsonify({
            'success':      True,
            'final_status': f"Call started for {patient_data['caregiver_name']} "
                            f"({phone}) in {patient_data['language']}. "
                            f"Risk: {'HIGH' if is_high_risk else 'LOW'}."
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)