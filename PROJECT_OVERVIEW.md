# Hospital Readmission Prediction System - Complete Overview

## Problem Statement

### The Challenge:
Hospital readmissions within 30 days of discharge are a critical healthcare issue:
- **High Cost**: Readmissions cost hospitals millions annually
- **Patient Safety**: Indicates inadequate discharge planning or post-discharge care
- **Quality Indicator**: Used to measure hospital performance
- **Preventable**: Many readmissions can be avoided with proper intervention

### Specific Problems:
1. **Lack of Risk Assessment**: Hospitals discharge patients without knowing readmission risk
2. **Poor Caregiver Communication**: Caregivers don't receive proper discharge instructions
3. **Language Barriers**: Rural/village caregivers don't understand English instructions
4. **Literacy Issues**: Illiterate caregivers can't read SMS or written instructions
5. **No Follow-up System**: No automated way to ensure caregivers understand care requirements

---

## Solution Overview

### Our System Provides:

#### 1. **AI-Powered Risk Prediction**
- Predicts 30-day readmission risk using machine learning
- 8 clinical features: age, hospital stay, procedures, medications, visits
- 4 ML models tested: Logistic Regression, Decision Tree, Random Forest, SVM
- Automatic selection of best model based on F1-score

#### 2. **Two-Role User System**
- **Front Desk Staff**: Register patients with comprehensive caregiver information
- **Doctors/Nurses**: Make predictions and system auto-notifies caregivers

#### 3. **Smart Caregiver Notification**
- **Multi-language**: English, Hindi, Tamil, Telugu, Kannada
- **Literacy-aware**: Voice calls for illiterate, SMS for literate
- **Retry Logic**: 3 call attempts, then SMS fallback
- **Status Tracking**: Know if caregiver received and understood message

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HOSPITAL STAFF                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Front Desk Staff              Doctors/Nurses              │
│  ┌──────────────┐              ┌──────────────┐           │
│  │   Register   │              │    Select    │           │
│  │   Patient    │              │   Patient    │           │
│  │      +       │              │      +       │           │
│  │  Caregiver   │              │   Clinical   │           │
│  │     Info     │              │     Data     │           │
│  └──────┬───────┘              └──────┬───────┘           │
│         │                             │                    │
└─────────┼─────────────────────────────┼────────────────────┘
          │                             │
          ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLASK BACKEND                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────┐ │
│  │   MongoDB    │    │  ML Model    │    │   Twilio    │ │
│  │   Database   │    │  Prediction  │    │ Voice/SMS   │ │
│  │              │    │              │    │             │ │
│  │ • users      │    │ • Random     │    │ • Voice     │ │
│  │ • patients   │    │   Forest     │    │   Calls     │ │
│  │ • predictions│    │ • Scaler     │    │ • SMS       │ │
│  └──────────────┘    └──────────────┘    └─────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
          │                             │
          │                             ▼
          │                   ┌──────────────────┐
          │                   │  CAREGIVER       │
          │                   │  NOTIFICATION    │
          │                   ├──────────────────┤
          │                   │                  │
          │                   │  IF Illiterate:  │
          │                   │  → Voice Call    │
          │                   │  → 3 Attempts    │
          │                   │  → SMS Fallback  │
          │                   │                  │
          │                   │  IF Literate:    │
          │                   │  → SMS Direct    │
          │                   │                  │
          │                   └──────────────────┘
          │                             │
          ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    OUTCOMES                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Caregiver informed in their language                   │
│  ✅ Understands care requirements                          │
│  ✅ Knows when to follow-up                                │
│  ✅ Knows warning signs                                    │
│  ✅ Reduced readmission risk                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 1. Machine Learning
- **Dataset**: hospital_readmissions.csv
- **Target**: Binary classification (readmitted <30 days: Yes/No)
- **Features**: 8 clinical indicators
- **Models**: 4 algorithms compared
- **Evaluation**: Accuracy, Precision, Recall, F1-score
- **Selection**: Best model auto-selected

### 2. User Authentication
- **Secure**: Bcrypt password hashing
- **Role-based**: Front desk vs Medical staff
- **Session Management**: Secure user sessions
- **MongoDB**: Persistent user storage

### 3. Patient Management
- **Comprehensive Profile**: Patient + Caregiver information
- **Language Preference**: 8+ Indian languages
- **Literacy Level**: Literate/Semi-literate/Illiterate
- **Location Type**: Urban/Rural/Village
- **Contact Preferences**: SMS/Voice/WhatsApp/Home Visit

### 4. Intelligent Notification
- **Multi-language**: Automated translation
- **Literacy-aware**: Voice for illiterate, text for literate
- **Retry Logic**: 3 attempts before fallback
- **Status Tracking**: Know if message received
- **Fallback System**: SMS if calls fail

### 5. Prediction History
- **Complete Tracking**: All predictions saved
- **Notification Status**: Method, attempts, success
- **Call Analytics**: Answered/not answered
- **Audit Trail**: Who, when, what

---

## Technology Stack

### Backend:
- **Python 3.9+**
- **Flask**: Web framework
- **scikit-learn**: Machine learning
- **pandas/numpy**: Data processing
- **joblib**: Model serialization

### Database:
- **MongoDB**: NoSQL database
- **pymongo**: Python driver
- **bcrypt**: Password hashing

### Communication:
- **Twilio**: Voice calls + SMS
- **Multi-language TTS**: Text-to-speech

### Frontend:
- **HTML5/CSS3**: Modern UI
- **JavaScript**: Interactive features
- **Font Awesome**: Icons
- **Responsive Design**: Mobile-friendly

### Deployment:
- **Docker**: Containerization
- **GitHub Actions**: CI/CD pipeline

---

## Workflow Example

### Scenario: Village Patient with Illiterate Caregiver

**Step 1: Admission (Front Desk)**
```
Patient: Ramu (70 years old)
Location: Village
Language: Tamil
Literacy: Illiterate

Caregiver: Lakshmi (Wife)
Phone: +919876543210
Can Read: No
Preferred Contact: Voice Call
```

**Step 2: Discharge (Doctor)**
```
Doctor enters clinical data:
- Time in hospital: 7 days
- Lab procedures: 45
- Medications: 18
- Previous visits: 2 inpatient, 1 emergency

System predicts: HIGH RISK (78% probability)
```

**Step 3: Automatic Notification**
```
System calls Lakshmi's phone (3 attempts):

Attempt 1: No answer → Wait 10 sec
Attempt 2: Answered! ✅

Voice message in Tamil:
"வணக்கம் Lakshmi, Ramu மருத்துவமனையிலிருந்து வெளியேறினார்.
முக்கியம்: மீண்டும் சேர்க்கப்படும் ஆபத்து.
தினசரி மருந்து, 3 நாட்களில் மருத்துவரை பார்க்கவும்."

Status saved: "Call answered on attempt 2"
```

**Step 4: Database Record**
```json
{
  "patient": "Ramu",
  "risk": "High",
  "probability": 78.5,
  "caregiver_notified": true,
  "notification_method": "Voice Call",
  "call_answered": true,
  "attempts": 2,
  "language": "Tamil"
}
```

**Result**: Lakshmi understands care requirements in her language! ✅

---

## Impact & Benefits

### For Hospitals:
- ✅ **Reduced Readmissions**: Early intervention for high-risk patients
- ✅ **Better Quality Scores**: Improved hospital performance metrics
- ✅ **Cost Savings**: Prevent expensive readmissions
- ✅ **Efficient Workflow**: Automated caregiver communication
- ✅ **Audit Trail**: Complete documentation

### For Patients:
- ✅ **Better Care**: Caregivers know what to do
- ✅ **Language Access**: Instructions in native language
- ✅ **Reduced Risk**: Proper follow-up care
- ✅ **Safety**: Early warning signs communicated

### For Caregivers:
- ✅ **Clear Instructions**: Understand care requirements
- ✅ **Native Language**: No language barriers
- ✅ **Accessible**: Voice calls for illiterate
- ✅ **Timely**: Immediate notification

---

## Unique Selling Points

### 1. **Literacy-Aware Communication**
- First system to handle illiterate caregivers
- Voice calls in local languages
- No other system does this!

### 2. **Rural/Village Focus**
- Designed for Indian healthcare reality
- 70% of India is rural
- Addresses real-world challenges

### 3. **Complete Automation**
- No manual follow-up needed
- Automatic retry logic
- Fallback mechanisms

### 4. **Production-Ready**
- Real Twilio integration
- Database tracking
- Scalable architecture

---

## Future Enhancements

1. **WhatsApp Integration**: Business API for messaging
2. **Appointment Scheduling**: Auto-book follow-ups
3. **Medication Reminders**: Daily SMS/calls
4. **Health Worker Portal**: Community health worker interface
5. **Analytics Dashboard**: Readmission trends, success rates
6. **More Languages**: Add regional languages
7. **Offline Mode**: SMS-based system for no-internet areas
8. **Integration**: Connect with hospital EMR systems

---

## Project Statistics

- **Lines of Code**: ~2,500
- **Files**: 15+
- **Languages Supported**: 5+
- **ML Models**: 4
- **Database Collections**: 3
- **API Endpoints**: 10+
- **Features**: 8 clinical + 15 patient profile

---

## Conclusion

This system solves a real healthcare problem by combining:
- **AI/ML**: Accurate risk prediction
- **Smart Communication**: Literacy-aware, multi-language
- **Automation**: No manual intervention needed
- **Scalability**: Ready for production deployment

**Perfect for Indian hospitals serving diverse populations!** 🏥🇮🇳

---

## Quick Links

- **Setup Guide**: README.md
- **Twilio Integration**: TWILIO_SETUP_GUIDE.md
- **Call Tracking**: TWILIO_CALL_TRACKING.md
- **Two-Role System**: TWO_ROLE_SYSTEM_GUIDE.md
- **MongoDB Setup**: MONGODB_SETUP.md

---

**Built with ❤️ for better healthcare outcomes**
