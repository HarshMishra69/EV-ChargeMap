import pandas as pd
import mysql.connector
from sklearn.linear_model import LinearRegression
import pickle

# DB Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Harsh8340",
    database="ev_chargemap"
)

# Load data
data = pd.read_sql("SELECT total_slots, daily_users FROM stations", db)

X = data[["total_slots"]]
y = data["daily_users"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ AI Model Trained & Saved as model.pkl")
