import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

# Load dataset
df = pd.read_csv("IPC_Complaint_Dataset_Contextual_Fix_42k.csv")

# 🔥 Drop rows with missing complaint or label
df = df.dropna(subset=['complaint_text', 'ipc_section'])

# Features and label
X = df['complaint_text']
y = df['ipc_section']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=5000)),
    ('clf', LogisticRegression(max_iter=1000))
])

# Train model
pipeline.fit(X_train, y_train)

# Save model
with open("model.pkl", "wb") as f:
    pickle.dump(pipeline, f)

print("✅ Model trained and saved as model.pkl")
