# Twilio Voice Call Setup - Complete Guide

## What You Get:

✅ **Automated voice calls** to caregivers
✅ **Call status tracking** (answered/not answered)
✅ **Retry logic** (3 attempts if no answer)
✅ **SMS fallback** (if all calls fail)
✅ **Database logging** (complete notification history)
✅ **Multi-language** (Hindi, Tamil, Telugu, English)

---

## Quick Setup (5 Minutes)

### Step 1: Create Twilio Account (2 min)
1. Go to: https://www.twilio.com/try-twilio
2. Sign up FREE ($15 credit = ~500 calls)
3. Verify your phone number

### Step 2: Get Credentials (1 min)
1. Dashboard shows:
   - **Account SID**: `ACxxxx...`
   - **Auth Token**: `xxxx...`
2. Buy phone number (FREE with trial credit)

### Step 3: Configure (1 min)
Edit `backend/twilio_integration.py` lines 6-8:

```python
TWILIO_ACCOUNT_SID = 'ACxxxx...'  # Paste your SID here
TWILIO_AUTH_TOKEN = 'xxxx...'     # Paste your token here
TWILIO_PHONE_NUMBER = '+1234...'  # Paste your Twilio number
```

### Step 4: Enable (30 sec)
```bash
# Windows
set TWILIO_ENABLED=true

# Mac/Linux
export TWILIO_ENABLED=true

# Then run
python app.py
```

**Done! Real calls now work!** 📞

---

## How It Works:

### When Doctor Makes Prediction:

```
1. Doctor selects patient
2. Enters clinical data
3. Clicks "Predict"
   ↓
4. System checks patient's literacy level
   ↓
5. IF Illiterate/Semi-literate:
   → Make voice call (Attempt 1)
   → Wait 10 seconds
   → Check if answered
   → If NO: Retry (Attempt 2)
   → If NO: Retry (Attempt 3)
   → If still NO: Send SMS
   ↓
6. Save complete status to database:
   - Method used (Voice/SMS)
   - Call answered? (Yes/No)
   - Number of attempts
   - Final status
```

---

## Call Status Tracking:

### What Gets Saved in Database:

```json
{
  "caregiver_notified": true,
  "notification_method": "Voice Call",
  "notification_status": "Call answered on attempt 2",
  "call_answered": true,
  "notification_attempts": 2,
  "notification_sent_at": "2024-01-15 10:30:00"
}
```

### Possible Statuses:

1. **"Call answered on attempt 1"** ✅
   - First call successful
   
2. **"Call answered on attempt 2"** ✅
   - Second call successful
   
3. **"SMS sent after 3 failed call attempts"** ⚠️
   - All calls failed, SMS sent
   
4. **"All attempts failed - needs manual follow-up"** ❌
   - Everything failed, manual action needed

---

## Console Output Example:

```
======================================================================
CAREGIVER NOTIFICATION SYSTEM
======================================================================
Patient: Ramu
Caregiver: Lakshmi (+919876543210)
Risk Level: HIGH RISK ⚠️
Language: Hindi
Literacy: Illiterate
======================================================================

🎯 Strategy: Voice Call (Literacy: Illiterate)

📞 Attempt 1/3
   Making call to Lakshmi (+919876543210)...
   Call SID: CA1234567890abcdef
   Status: no-answer
   Duration: 0 seconds
   ⚠️ Call made but not answered (Status: no-answer)
   ⏳ Waiting 10 seconds before retry...

📞 Attempt 2/3
   Making call to Lakshmi (+919876543210)...
   Call SID: CA0987654321fedcba
   Status: completed
   Duration: 45 seconds

✅ SUCCESS! Caregiver answered the call.
======================================================================

FINAL STATUS: Call answered on attempt 2
======================================================================
```

---

## Testing Without Twilio (FREE):

Current system works in **DEMO MODE**:
- Shows notification in console
- No actual calls made
- Perfect for testing/demo

To test:
1. Register patient (front desk)
2. Make prediction (doctor)
3. See notification in console ✅

---

## Cost Breakdown:

### India Pricing:
- **Voice Call**: ₹0.60/minute
- **SMS**: ₹0.50/message

### Example Costs:
- 100 patients/day = ₹60/day = ₹1,800/month
- 500 patients/day = ₹300/day = ₹9,000/month

**Very affordable for hospitals!**

---

## Smart Notification Logic:

```
IF patient.literacy == "Illiterate":
    → Voice Call (3 attempts)
    → If fails: SMS fallback
    
ELIF patient.literacy == "Semi-literate":
    → Voice Call (3 attempts)
    → If fails: SMS fallback
    
ELSE (Literate):
    → SMS directly
```

---

## Database Schema:

### predictions collection:
```json
{
  "_id": ObjectId,
  "patient_id": ObjectId,
  "doctor_username": "doctor1",
  "prediction_date": DateTime,
  "prediction_result": "High Risk",
  "probability": 75.32,
  
  // Notification tracking:
  "caregiver_notified": true,
  "notification_method": "Voice Call",
  "notification_status": "Call answered on attempt 2",
  "call_answered": true,
  "notification_attempts": 2,
  "notification_sent_at": DateTime
}
```

---

## Troubleshooting:

### Issue: "Unable to create record: The number is unverified"
**Solution:** 
- Trial account can only call verified numbers
- Add number at: https://console.twilio.com/us1/develop/phone-numbers/manage/verified
- OR upgrade account (no minimum, pay-as-you-go)

### Issue: Call not connecting
**Solution:**
- Check phone format: +919876543210 (no spaces)
- Verify Twilio number has Voice capability
- Check Twilio console logs

### Issue: "TWILIO_ENABLED not working"
**Solution:**
```bash
# Set environment variable before running
set TWILIO_ENABLED=true
python app.py
```

---

## Summary:

✅ **Demo Mode** (Current): FREE, console logging
✅ **Production Mode** (Twilio): Real calls, $15 free trial
✅ **Call Tracking**: Know if caregiver answered
✅ **Retry Logic**: 3 attempts before giving up
✅ **SMS Fallback**: Automatic if calls fail
✅ **Database Logging**: Complete notification history
✅ **Multi-language**: Hindi, Tamil, Telugu, English

**Your system is production-ready!** 🚀

---

## Next Steps:

1. **For Demo**: Already working! Just use it.
2. **For Production**: 
   - Create Twilio account
   - Add credentials
   - Set TWILIO_ENABLED=true
   - Test with verified number
   - Go live!

**Questions? Check TWILIO_SETUP_GUIDE.md for detailed instructions.**
