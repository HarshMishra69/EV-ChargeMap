from flask import Flask, jsonify, render_template, request, redirect, session
from flask_cors import CORS
import mysql.connector
import pickle

model = pickle.load(open("model.pkl", "rb"))

app = Flask(__name__)
CORS(app)
app.secret_key = "ev_secret"

# Local MySQL connection
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Harsh8340",   # your local MySQL password
        database="ev_chargemap",
        port=3306
    )

# Driver View
@app.route("/")
def home():
    return render_template("index.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            session["role"] = user["role"]
            return redirect("/admin" if user["role"] == "admin" else "/")
        else:
            return "Invalid login"

    return render_template("login.html")

# Admin Dashboard
@app.route("/admin")
def admin_page():
    if session.get("role") != "admin":
        return redirect("/login")
    return render_template("admin.html")

# Stations API
@app.route("/stations")
def stations():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM stations")
    return jsonify(cursor.fetchall())

# Analytics API
@app.route("/analytics")
def analytics():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name, daily_users, revenue, status FROM stations")
    return jsonify(cursor.fetchall())

# AI Demand Prediction
@app.route("/predict-demand")
def predict_demand():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT name, total_slots FROM stations")
    stations = cursor.fetchall()

    predictions = []

    for s in stations:
        predicted_users = model.predict([[s["total_slots"]]])[0]
        predictions.append({
            "name": s["name"],
            "predicted_users": round(predicted_users, 2)
        })

    return jsonify(predictions)

# Admin Summary Cards
@app.route("/admin-data")
def admin_data():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM stations")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as repair FROM stations WHERE status='repair'")
    repair = cursor.fetchone()["repair"]

    cursor.execute("SELECT name FROM stations ORDER BY daily_users DESC LIMIT 1")
    most_used = cursor.fetchone()["name"]

    cursor.execute("SELECT SUM(revenue) as revenue FROM stations")
    revenue = cursor.fetchone()["revenue"]

    return jsonify({
        "total_stations": total,
        "repair_needed": repair,
        "most_used": most_used,
        "total_revenue": revenue
    })

# Business Insights
@app.route("/insights")
def insights():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT name FROM stations WHERE status='repair'")
    repair = cursor.fetchall()

    cursor.execute("SELECT name, daily_users FROM stations WHERE daily_users > 130")
    upgrade = cursor.fetchall()

    cursor.execute("SELECT latitude, longitude FROM stations")
    locations = cursor.fetchall()

    return jsonify({
        "repair_stations": repair,
        "upgrade_stations": upgrade,
        "new_station_areas": locations
    })

if __name__ == "__main__":
    app.run(debug=True)
