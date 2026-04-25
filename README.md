# Hospital Readmission Prediction System

A production-ready machine learning web application that predicts whether a patient will be readmitted within 30 days after discharge.

## Project Structure

```
project/
│
├── backend/
│   ├── app.py
│   ├── train.py
│   ├── model.pkl
│   ├── hospital_readmissions.csv
│   ├── requirements.txt
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   │   └── style.css
│
├── Dockerfile
├── .github/workflows/ci-cd.yml
└── README.md
```

## Features

- **Two-Role User System**: 
  - **Front Desk Staff**: Register patients with caregiver information
  - **Doctors/Nurses**: Make predictions and auto-notify caregivers
- **Patient Profile Management**: Comprehensive patient and caregiver data collection
- **Smart Caregiver Notification System**: 
  - Multi-language support (English, Hindi, Tamil, Telugu, etc.)
  - Literacy-aware messaging (SMS for literate, Voice call for illiterate)
  - Multiple contact methods (SMS, Voice Call, WhatsApp, Home Visit)
  - Village/Rural patient support with alternative contacts
- **User Authentication**: Secure login and registration with role-based access
- **MongoDB Integration**: Three collections (users, patients, predictions)
- **Password Encryption**: Bcrypt hashing for secure passwords
- **8 Input Features**: age, time_in_hospital, n_lab_procedures, n_procedures, n_medications, n_outpatient, n_inpatient, n_emergency
- **4 ML Models**: Logistic Regression, Decision Tree, Random Forest, SVM
- **Best Model Selection**: Automatically selects best model based on F1-score
- **Prediction History**: Track all predictions with caregiver notification status
- **Flask Backend**: RESTful API for predictions and patient management
- **Modern UI**: Responsive HTML/CSS frontend with medical theme
- **Session Management**: Secure user sessions with role-based routing
- **Docker Support**: Containerized deployment
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

## Prerequisites

- Python 3.9+
- MongoDB (local or Atlas)
- Docker (optional)
- hospital_readmissions.csv dataset

## Step-by-Step Setup

### Step 0: Install MongoDB

See [MONGODB_SETUP.md](MONGODB_SETUP.md) for detailed MongoDB installation instructions.

**Quick Start:**
- Windows: Download from https://www.mongodb.com/try/download/community
- Mac: `brew install mongodb-community`
- Linux: `sudo apt-get install mongodb`

Or use MongoDB Atlas (free cloud): https://www.mongodb.com/cloud/atlas

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Prepare Dataset

Place `hospital_readmissions.csv` in the `backend/` directory.

### Step 3: Train Models

```bash
cd backend
python train.py
```

This will:
- Load the dataset
- Convert target to binary (1 for "<30", 0 for others)
- Train 4 models
- Evaluate each model (Accuracy, Precision, Recall, F1-score)
- Select best model based on F1-score
- Save best model as `model.pkl`

### Step 4: Run Flask Application

```bash
cd backend
python app.py
```

The application will start at `http://localhost:5000`

### Step 5: Access Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

**Two User Types:**

1. **Front Desk Staff**:
   - Register with role "Front Desk Staff"
   - Login → Patient Admission Dashboard
   - Register patients with caregiver information
   - View registered patients

2. **Doctors/Nurses**:
   - Register with role "Doctor" or "Nurse" + Specialization
   - Login → Prediction Dashboard
   - Select registered patient OR enter details manually
   - Make prediction → System auto-notifies caregiver
   - View results with risk assessment

**Demo Accounts (No Registration Needed):**
- Username: `admin` | Password: `admin123` (Doctor access)
- Username: `doctor` | Password: `doctor123` (Doctor access)
- Username: `nurse` | Password: `nurse123` (Nurse access)

**Caregiver Notification:**
- When doctor makes prediction for registered patient
- System automatically sends notification to caregiver
- Message in caregiver's language (English/Hindi/Tamil/etc)
- Method based on literacy (SMS/Voice Call/Home Visit)
- Notification logged in console (production: SMS/Call API)

## Docker Deployment

### Build Docker Image

```bash
docker build -t hospital-readmission .
```

### Run Docker Container

```bash
docker run -p 5000:5000 hospital-readmission
```

Access at `http://localhost:5000`

## CI/CD Pipeline Setup

### GitHub Actions Configuration

1. Create GitHub repository
2. Add secrets in repository settings:
   - `DOCKERHUB_USERNAME`: Your DockerHub username
   - `DOCKERHUB_TOKEN`: Your DockerHub access token

3. Push code to main branch:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

The CI/CD pipeline will automatically:
- Install dependencies
- Train the model
- Test model loading
- Build Docker image
- Push to DockerHub

## API Endpoints

### GET /
Returns the login page

### POST /register
Register new user (front desk staff, doctor, or nurse)

### POST /login
Authenticate user and create session

### GET /patient-dashboard
Patient admission dashboard (front desk staff only)

### POST /add-patient
Register new patient with caregiver information

### GET /prediction-dashboard
Prediction interface (doctors/nurses only)

### POST /predict
Accepts clinical data and returns prediction + notifies caregiver

**Request Body:**
```json
{
  "age": 65,
  "time_in_hospital": 5,
  "n_lab_procedures": 50,
  "n_procedures": 3,
  "n_medications": 15,
  "n_outpatient": 2,
  "n_inpatient": 1,
  "n_emergency": 0
}
```

**Response:**
```json
{
  "prediction": "Readmitted within 30 days",
  "probability": "75.32%"
}
```

## Model Evaluation

The training script evaluates 4 models:

1. **Logistic Regression**
2. **Decision Tree**
3. **Random Forest** (with class_weight="balanced")
4. **SVM** (with probability=True)

Each model is evaluated using:
- Accuracy
- Precision
- Recall
- F1-Score

The model with the highest F1-score is automatically selected and saved.

## Caregiver Notification System

### How It Works:

1. **Front desk** registers patient with caregiver details:
   - Caregiver name, phone, relationship
   - Language preference (English, Hindi, Tamil, etc.)
   - Literacy level (Literate, Semi-literate, Illiterate)
   - Location type (Urban, Rural, Village)
   - Preferred contact method (SMS, Voice Call, WhatsApp, Home Visit)

2. **Doctor** makes prediction:
   - Selects patient from dropdown
   - Enters clinical data
   - System predicts risk level

3. **System automatically notifies caregiver**:
   - Generates message in caregiver's language
   - Chooses method based on literacy:
     - **Literate**: SMS/WhatsApp
     - **Semi-literate**: Simple SMS + Voice call
     - **Illiterate**: Voice call in local language
     - **No phone**: Schedule home visit
   - Logs notification in database

### Message Examples:

**High Risk - Hindi (for village/illiterate caregiver):**
```
नमस्ते [Caregiver], [Patient] को अस्पताल से छुट्टी मिल गई है।
ज़रूरी: दोबारा भर्ती का खतरा।
कृपया ध्यान दें: रोज़ दवाई, 3 दिन में डॉक्टर को दिखाएं,
तबीयत बिगड़े तो तुरंत अस्पताल लाएं।
```

**Low Risk - English:**
```
Hello [Caregiver], [Patient] has been discharged.
Please ensure: Regular medication, Follow-up in 7 days.
Contact hospital if needed.
```

### Current Status:
- ✅ Notification system fully functional
- ✅ Multi-language support (English, Hindi, Tamil)
- ✅ Literacy-aware messaging
- ⚠️ Currently logs to console (production: integrate SMS/Call API)

### Production Integration:
Ready for integration with:
- **Twilio** (SMS + Voice calls)
- **AWS SNS** (SMS)
- **WhatsApp Business API**

See [TWO_ROLE_SYSTEM_GUIDE.md](TWO_ROLE_SYSTEM_GUIDE.md) for integration details.

## Tech Stack

- **ML**: Python, pandas, numpy, scikit-learn
- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Docker
- **CI/CD**: GitHub Actions

## Troubleshooting

### Model not found error
Ensure you run `train.py` before starting the Flask app.

### Port already in use
Change the port in `app.py` or kill the process using port 5000.

### Docker build fails
Ensure all files are in correct directories as per project structure.

## License

MIT License
