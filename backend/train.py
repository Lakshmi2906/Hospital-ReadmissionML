import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

df = pd.read_csv('hospital_readmissions.csv')

print("Unique values in 'readmitted' column:")
print(df['readmitted'].unique())
print(f"\nValue counts:")
print(df['readmitted'].value_counts())

df['readmitted'] = df['readmitted'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)

if df['age'].dtype == 'object':
    df['age'] = df['age'].str.extract(r'(\d+)').astype(float)

features = ['age', 'time_in_hospital', 'n_lab_procedures', 'n_procedures', 
            'n_medications', 'n_outpatient', 'n_inpatient', 'n_emergency']

X = df[features]
y = df['readmitted']

for col in X.columns:
    if X[col].dtype == 'object':
        X[col] = pd.to_numeric(X[col], errors='coerce')

X = X.fillna(X.mean())

print(f"Total samples: {len(y)}")
print(f"Class distribution:")
print(y.value_counts())
print(f"\nClass 0 (Not readmitted): {(y == 0).sum()}")
print(f"Class 1 (Readmitted <30): {(y == 1).sum()}")

if y.nunique() < 2:
    print("\nError: Dataset contains only one class. Please check:")
    print("1. The 'readmitted' column values in your CSV")
    print("2. Make sure there are '<30' values in the readmitted column")
    exit(1)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

models = {
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(class_weight='balanced', random_state=42),
    'SVM': SVC(probability=True, random_state=42)
}

results = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    results[name] = {
        'model': model,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }
    
    print(f"\n{name}:")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")

best_model_name = max(results, key=lambda x: results[x]['f1'])
best_model = results[best_model_name]['model']

print(f"\n{'='*50}")
print(f"Best Model: {best_model_name}")
print(f"F1-Score: {results[best_model_name]['f1']:.4f}")
print(f"{'='*50}")

joblib.dump({'model': best_model, 'scaler': scaler, 'features': features}, 'model.pkl')
print("\nModel saved as model.pkl")
