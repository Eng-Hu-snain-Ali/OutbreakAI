from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import json
import os
import random
import requests
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Configuration
# Use Neon URL if provided, otherwise fallback to local SQLite
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ── Database Model ───────────────────────────────────────────────────────────
class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    risk = db.Column(db.String(20), nullable=False)
    active_cases = db.Column(db.Integer, default=0)
    active_trend = db.Column(db.String(20), default="+0%")
    patients = db.Column(db.Integer, default=0)
    patients_trend = db.Column(db.String(20), default="+0%")
    history = db.Column(db.Text, default="[]") # JSON string of last 7 days cases
    disease = db.Column(db.String(100), nullable=True)
    population_density = db.Column(db.Float, nullable=True)
    hospital_capacity = db.Column(db.Float, nullable=True)
    vaccination_rate = db.Column(db.Float, nullable=True)
    recommendations = db.Column(db.Text, nullable=True) # JSON string
    last_week_cases = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        try:
            hist_list = json.loads(self.history)
        except:
            hist_list = []
            
        try:
            recs_list = json.loads(self.recommendations) if self.recommendations else []
        except:
            recs_list = []
        
        return {
            "id": self.id,
            "city": self.city,
            "risk": self.risk,
            "activeCases": self.active_cases,
            "activeTrend": self.active_trend,
            "patients": f"{self.patients:,}",
            "patientsTrend": self.patients_trend,
            "history": hist_list,
            "disease": self.disease,
            "populationDensity": self.population_density,
            "hospitalCapacity": self.hospital_capacity,
            "vaccinationRate": self.vaccination_rate,
            "recommendations": recs_list,
            "lastWeekCases": self.last_week_cases
        }

# Create tables and insert default data if empty
with app.app_context():
    db.create_all()
    if Region.query.count() == 0:
        default_regions = [
            {"city": "Karachi", "risk": "High", "cases": 642, "cases_trend": "+14%", "patients": 1847, "pat_trend": "+12%", "hist": [410, 448, 487, 521, 558, 601, 642]},
            {"city": "Lahore", "risk": "Medium", "cases": 284, "cases_trend": "+5%", "patients": 923, "pat_trend": "+5%", "hist": [220, 235, 248, 261, 270, 278, 284]},
            {"city": "Islamabad", "risk": "Low", "cases": 47, "cases_trend": "-2%", "patients": 134, "pat_trend": "-3%", "hist": [62, 58, 55, 52, 50, 48, 47]},
            {"city": "Peshawar", "risk": "Medium", "cases": 198, "cases_trend": "+8%", "patients": 567, "pat_trend": "+8%", "hist": [150, 160, 165, 175, 182, 190, 198]},
            {"city": "Quetta", "risk": "Low", "cases": 31, "cases_trend": "-1%", "patients": 89, "pat_trend": "-2%", "hist": [40, 38, 36, 35, 33, 32, 31]},
            {"city": "Multan", "risk": "High", "cases": 521, "cases_trend": "+18%", "patients": 1423, "pat_trend": "+19%", "hist": [300, 340, 390, 430, 470, 500, 521]}
        ]
        for r in default_regions:
            new_reg = Region(
                city=r["city"],
                risk=r["risk"],
                active_cases=r["cases"],
                active_trend=r["cases_trend"],
                patients=r["patients"],
                patients_trend=r["pat_trend"],
                history=json.dumps(r["hist"])
            )
            db.session.add(new_reg)
        db.session.commit()

# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "success",
        "message": "Health Guard Backend API is running.",
        "endpoints": {
            "GET /api/regions": "Get all regions and stats",
            "POST /api/regions": "Add a new region",
            "PUT /api/regions/<id>": "Edit a region",
            "DELETE /api/regions/<id>": "Delete a region"
        }
    })

def calculate_risk(patients, disease=None, pop_density=None, hosp_capacity=None, vax_rate=None):
    # Base risk from patients
    risk_score = 0
    if patients > 500: risk_score += 50
    elif patients > 200: risk_score += 30
    else: risk_score += 10
    
    # Epidemiological factors
    if pop_density and pop_density > 10000: risk_score += 20  # High density increases risk
    if hosp_capacity and hosp_capacity < 30: risk_score += 30  # Low capacity increases risk
    elif hosp_capacity and hosp_capacity > 80: risk_score -= 10
    if vax_rate and vax_rate < 40: risk_score += 20
    elif vax_rate and vax_rate > 70: risk_score -= 20
    
    # Disease specific weights
    if disease:
        d = disease.lower()
        if d in ["covid-19", "influenza"]: risk_score += 15 # Airborne
        elif d in ["dengue", "malaria"]: risk_score += 10 # Vector-borne
        
    if risk_score > 70: return "High"
    if risk_score > 40: return "Medium"
    return "Low"

def generate_recommendations(risk, disease, hosp_capacity, vax_rate):
    recs = []
    if risk == "High":
        recs.append("Critical Alert: Declare local health emergency.")
        recs.append("Restrict public gatherings and enforce preventive measures.")
    elif risk == "Medium":
        recs.append("Increase public awareness campaigns.")
        
    if hosp_capacity and hosp_capacity < 40:
        recs.append("Prepare overflow medical facilities. Divert non-critical patients.")
        
    if vax_rate and vax_rate < 50 and disease and disease.lower() in ["covid-19", "influenza"]:
        recs.append(f"Initiate emergency {disease} vaccination drives in high-density areas.")
        
    if disease:
        d = disease.lower()
        if d == "dengue" or d == "malaria":
            recs.append("Initiate immediate vector control and fumigation.")
        elif d == "heatstroke":
            recs.append("Issue heat advisories and setup public cooling centers.")
            
    if not recs:
        recs.append("Continue standard surveillance protocols.")
        
    return recs

def generate_history(current_cases):
    """Generates a synthetic 7-day ascending history ending at current_cases"""
    if current_cases == 0: return [0]*7
    hist = []
    val = current_cases * 0.5
    step = (current_cases - val) / 6
    for i in range(6):
        hist.append(int(val))
        val += step
    hist.append(current_cases)
    return hist

@app.route("/api/regions", methods=["GET"])
def get_regions():
    regions = Region.query.all()
    regions_list = [r.to_dict() for r in regions]

    # Calculate Top Stats
    total_cases = sum(r.active_cases for r in regions)
    total_patients = sum(r.patients for r in regions)
    high_risk_zones = sum(1 for r in regions if r.risk == "High")
    
    # Calculate Chart Data (combining histories by date)
    # We'll mock dates for the last 7 days ending today
    from datetime import timedelta
    today = datetime.now()
    dates = [(today - timedelta(days=6-i)).strftime("%b %d") for i in range(7)]
    
    chart_data = []
    # Only show top 3 highest cases regions in chart to avoid clutter
    top_regions = sorted(regions, key=lambda x: x.active_cases, reverse=True)[:3]
    
    for i in range(7):
        day_data = {"date": dates[i]}
        for tr in top_regions:
            hist = json.loads(tr.history)
            if len(hist) > i:
                day_data[tr.city] = hist[i]
            else:
                day_data[tr.city] = tr.active_cases
        chart_data.append(day_data)
        
    return jsonify({
        "regions": regions_list,
        "stats": {
            "total_cases": f"{total_cases:,}",
            "total_patients": f"{total_patients:,}",
            "regions_monitored": len(regions),
            "high_risk_zones": high_risk_zones
        },
        "chart_data": chart_data,
        "chart_keys": [r.city for r in top_regions]
    })

@app.route("/api/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City parameter is required"}), 400
    
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
    if not api_key:
        return jsonify({"error": "Weather API key not configured"}), 500

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        resp = requests.get(url).json()
        
        if resp.get("cod") != 200:
            return jsonify({"error": resp.get("message", "City not found")}), 404
            
        return jsonify({
            "temperature": resp.get("main", {}).get("temp", 0),
            "humidity": resp.get("main", {}).get("humidity", 0),
            "wind": resp.get("wind", {}).get("speed", 0) * 3.6, # Convert m/s to km/h
            "rain": resp.get("rain", {}).get("1h", 0) # mm in last 1 hour
        })
    except Exception as e:
        print("Weather API error:", e)
        return jsonify({"error": "Failed to fetch weather data"}), 500

@app.route("/api/regions", methods=["POST"])
def add_region():
    data = request.json
    city = data.get("city", "").strip()
    cases = int(data.get("activeCases", 0))
    patients = int(data.get("patients", 0))
    
    disease = data.get("disease", None)
    pop_density = float(data.get("populationDensity", 0)) if data.get("populationDensity") else None
    hosp_capacity = float(data.get("hospitalCapacity", 0)) if data.get("hospitalCapacity") else None
    vax_rate = float(data.get("vaccinationRate", 0)) if data.get("vaccinationRate") else None
    
    risk = calculate_risk(patients, disease, pop_density, hosp_capacity, vax_rate)
    recs = generate_recommendations(risk, disease, hosp_capacity, vax_rate)
    
    # Check if city already exists (case-insensitive)
    from sqlalchemy import func
    existing_reg = Region.query.filter(func.lower(Region.city) == city.lower()).first()
    
    if existing_reg:
        # Update existing region instead of adding duplicate
        if existing_reg.active_cases > 0:
            c_trend = ((cases - existing_reg.active_cases) / existing_reg.active_cases) * 100
            existing_reg.active_trend = f"{'+' if c_trend >= 0 else ''}{int(c_trend)}%"
        
        if existing_reg.patients > 0:
            p_trend = ((patients - existing_reg.patients) / existing_reg.patients) * 100
            existing_reg.patients_trend = f"{'+' if p_trend >= 0 else ''}{int(p_trend)}%"
            
        existing_reg.last_week_cases = existing_reg.active_cases
        existing_reg.active_cases = cases
        existing_reg.patients = patients
        existing_reg.risk = risk
        existing_reg.disease = disease
        existing_reg.population_density = pop_density
        existing_reg.hospital_capacity = hosp_capacity
        existing_reg.vaccination_rate = vax_rate
        existing_reg.recommendations = json.dumps(recs)
        
        hist = json.loads(existing_reg.history)
        hist.pop(0)
        hist.append(cases)
        existing_reg.history = json.dumps(hist)
        
        db.session.commit()
        return jsonify({"message": "Region updated successfully", "region": existing_reg.to_dict()}), 200
    else:
        # Create new region
        history = generate_history(cases)
        new_reg = Region(
            city=city,
            risk=risk,
            active_cases=cases,
            active_trend="+0%",
            patients=patients,
            patients_trend="+0%",
            history=json.dumps(history),
            disease=disease,
            population_density=pop_density,
            hospital_capacity=hosp_capacity,
            vaccination_rate=vax_rate,
            recommendations=json.dumps(recs),
            last_week_cases=0
        )
        db.session.add(new_reg)
        db.session.commit()
        return jsonify({"message": "Region added successfully", "region": new_reg.to_dict()}), 201

@app.route("/api/regions/<int:region_id>", methods=["PUT"])
def edit_region(region_id):
    region = Region.query.get_or_404(region_id)
    data = request.json
    
    new_cases = int(data.get("activeCases", region.active_cases))
    new_patients = int(data.get("patients", region.patients))
    
    disease = data.get("disease", region.disease)
    pop_density = float(data.get("populationDensity")) if data.get("populationDensity") is not None else region.population_density
    hosp_capacity = float(data.get("hospitalCapacity")) if data.get("hospitalCapacity") is not None else region.hospital_capacity
    vax_rate = float(data.get("vaccinationRate")) if data.get("vaccinationRate") is not None else region.vaccination_rate
    
    # Calculate trends
    if region.active_cases > 0:
        c_trend = ((new_cases - region.active_cases) / region.active_cases) * 100
        region.active_trend = f"{'+' if c_trend >= 0 else ''}{int(c_trend)}%"
    
    if region.patients > 0:
        p_trend = ((new_patients - region.patients) / region.patients) * 100
        region.patients_trend = f"{'+' if p_trend >= 0 else ''}{int(p_trend)}%"
        
    region.last_week_cases = region.active_cases
    region.active_cases = new_cases
    region.patients = new_patients
    region.disease = disease
    region.population_density = pop_density
    region.hospital_capacity = hosp_capacity
    region.vaccination_rate = vax_rate
    
    region.risk = calculate_risk(new_patients, disease, pop_density, hosp_capacity, vax_rate)
    recs = generate_recommendations(region.risk, disease, hosp_capacity, vax_rate)
    region.recommendations = json.dumps(recs)
    
    # Update history
    hist = json.loads(region.history)
    hist.pop(0) # remove oldest
    hist.append(new_cases) # add newest
    region.history = json.dumps(hist)
    
    db.session.commit()
    return jsonify({"message": "Region updated successfully", "region": region.to_dict()})

@app.route("/api/regions/<int:region_id>", methods=["DELETE"])
def delete_region(region_id):
    region = Region.query.get_or_404(region_id)
    db.session.delete(region)
    db.session.commit()
    return jsonify({"message": "Region deleted successfully"})

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
