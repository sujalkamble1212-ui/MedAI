import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

print("Loading dataset...")
df = pd.read_csv("dataset.csv")

print("Total columns:", len(df.columns))
print(df.columns)

# Make sure Prognosis column exists
X = df.drop("prognosis", axis=1)
y = df["prognosis"]

print("Training model...")
model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, "disease_model.pkl")

print("Model saved successfully!")
