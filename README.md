<div align="center">

# 🦠 OutbreakAI

### Disease Outbreak Monitoring & Risk Analysis — Backend API (OutbreakIQ)

A Flask REST API that tracks disease activity across regions, scores outbreak risk from epidemiological factors, and generates actionable public-health recommendations.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-Flask--SQLAlchemy_3.1.1-D71F00)
![PostgreSQL](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL_(Neon)-4169E1?logo=postgresql&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.2-F7931E?logo=scikitlearn&logoColor=white)

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [How Risk Scoring Works](#-how-risk-scoring-works)
- [Data & Model Artifacts](#-data--model-artifacts)
- [Database](#-database)
- [Known Limitations](#-known-limitations)
- [Suggested Next Steps](#-suggested-next-steps)
- [Author](#-author)

---

## 🔎 Overview

**OutbreakAI** helps health authorities monitor and anticipate disease outbreaks across multiple cities or regions. The backend (this repository, package name **OutbreakIQ**) stores per-region case data, calculates a **Low / Medium / High** risk level from epidemiological indicators, produces tailored response recommendations, and exposes everything through a clean JSON API ready to feed a dashboard.

The API also returns pre-aggregated dashboard statistics (totals, high-risk zone count, 7-day trend data for the three most affected regions) so a frontend can render charts with a single request.

> **Scope:** this repository contains the **backend only**. JSON responses use `camelCase` keys and CORS is enabled so a separate frontend can consume the API directly.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Region management** | Full CRUD for monitored regions (`GET`, `POST`, `PUT`, `DELETE`). |
| **Automated risk scoring** | Rule-based engine combining patient load, population density, hospital capacity, vaccination rate, and disease type. |
| **Smart recommendations** | Context-aware response actions (emergency declaration, overflow facilities, vaccination drives, vector control, heat advisories). |
| **Trend tracking** | Automatic percentage trends for active cases and patients on every update, plus a rolling 7-day case history. |
| **Dashboard-ready payload** | `GET /api/regions` returns region list, summary stats, and chart series in one response. |
| **Live weather lookup** | Proxy endpoint for current temperature, humidity, wind and rainfall via OpenWeatherMap. |
| **Upsert behaviour** | Posting an existing city (case-insensitive) updates it instead of creating a duplicate. |
| **Zero-config database** | Falls back to local SQLite; switches to PostgreSQL (e.g., Neon) when `DATABASE_URL` is set. |
| **Auto-seeding** | Tables are created on startup and seeded with six sample regions when empty. |

---

## 🏗 Architecture

```mermaid
flowchart LR
    C["Client / Dashboard"] -->|JSON over HTTP| A["Flask API<br/>(app.py)"]
    A --> R["Risk Engine<br/>calculate_risk()"]
    A --> G["Recommendation Engine<br/>generate_recommendations()"]
    A -->|SQLAlchemy ORM| D[("SQLite (default)<br/>or PostgreSQL / Neon")]
    A -->|"/api/weather"| W["OpenWeatherMap API"]
```

**Request flow for creating or updating a region:** the API validates the payload → computes the risk level → generates recommendations → calculates trends against the previous record → rolls the 7-day history forward → commits to the database → returns the updated region.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Web framework | Flask 3.0.0, Flask-CORS 4.0.0 |
| ORM / Database | Flask-SQLAlchemy 3.1.1, SQLite (default), PostgreSQL via psycopg2-binary 2.9.9 |
| Data / ML tooling | scikit-learn 1.3.2, pandas 2.1.4, NumPy 1.26.2, joblib 1.3.2 |
| Configuration | python-dotenv 1.0.1 |
| HTTP client | requests 2.31.0 |
| Production server | gunicorn 21.2.0 |

---

## 📂 Project Structure

```text
OutbreakIQ/
├── app.py                 # Flask app: models, risk logic, API routes
├── generate_models.py     # Generates placeholder ML artifacts (synthetic data)
├── reset_db.py            # ⚠️ Drops and recreates all tables (asks for confirmation)
├── neon_queries.sql       # SQL schema + seed data for PostgreSQL / Neon
├── requirements.txt       # Pinned dependencies
├── data/
│   └── final.csv          # 120 daily weather/case records (Jan–Apr 2023)
├── models/
│   ├── risk_model.pkl     # Model artifacts (stored with Git LFS)
│   ├── label_encoder.pkl
│   └── feature_cols.pkl
└── scratch/
    └── check_db.py        # Verifies the `region` table has the expected columns
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.12** (the version this README's setup steps were verified with)
- `pip`
- *(Optional)* a PostgreSQL database such as [Neon](https://neon.tech)
- *(Optional)* an [OpenWeatherMap](https://openweathermap.org/api) API key for the weather endpoint
- *(Optional)* [Git LFS](https://git-lfs.com) if you want the committed model files

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Eng-Hu-snain-Ali/OutbreakAI.git
cd OutbreakAI/OutbreakIQ

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file in the `OutbreakIQ/` folder (both variables are optional — see [Configuration](#-configuration)):

```env
DATABASE_URL=postgresql://user:password@host/dbname
OPENWEATHERMAP_API_KEY=your_api_key_here
```

### Run the server

```bash
python app.py
```

The API starts at **http://localhost:5000**. On first launch the database tables are created and seeded with six sample regions automatically.

Quick check:

```bash
curl http://localhost:5000/api/regions
```

For a production-style process, point gunicorn at the Flask app object: `gunicorn app:app`.

---

## ⚙️ Configuration

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `DATABASE_URL` | No | `sqlite:///local.db` | Database connection string. A `postgres://` prefix is automatically rewritten to `postgresql://`. |
| `OPENWEATHERMAP_API_KEY` | Only for `/api/weather` | — | Without it, `/api/weather` returns HTTP 500 with `"Weather API key not configured"`. |

---

## 📡 API Reference

**Base URL:** `http://localhost:5000`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check and endpoint index |
| `GET` | `/api/regions` | All regions + dashboard stats + chart data |
| `POST` | `/api/regions` | Create a region (or update it if the city already exists) |
| `PUT` | `/api/regions/<id>` | Update an existing region |
| `DELETE` | `/api/regions/<id>` | Delete a region |
| `GET` | `/api/weather?city=<name>` | Current weather for a city |

### `GET /api/regions`

Returns regions, summary statistics and chart series.

```json
{
  "regions": [
    {
      "id": 1,
      "city": "Karachi",
      "risk": "High",
      "activeCases": 642,
      "activeTrend": "+14%",
      "patients": "1,847",
      "patientsTrend": "+12%",
      "history": [410, 448, 487, 521, 558, 601, 642],
      "disease": null,
      "populationDensity": null,
      "hospitalCapacity": null,
      "vaccinationRate": null,
      "recommendations": [],
      "lastWeekCases": null
    }
  ],
  "stats": {
    "total_cases": "1,723",
    "total_patients": "4,983",
    "regions_monitored": 6,
    "high_risk_zones": 2
  },
  "chart_data": [{ "date": "Oct 23", "Karachi": 410, "Multan": 300, "Lahore": 220 }],
  "chart_keys": ["Karachi", "Multan", "Lahore"]
}
```

> `patients` is returned as a comma-formatted **string**. `chart_data` covers the 7 days ending today and includes the three regions with the most active cases.

### `POST /api/regions`

**Request body**

| Field | Type | Description |
|---|---|---|
| `city` | string | Region name (matched case-insensitively) |
| `activeCases` | integer | Current active cases |
| `patients` | integer | Total patients — **the base input for risk scoring** |
| `disease` | string, optional | e.g. `"Dengue"`, `"COVID-19"`, `"Influenza"`, `"Malaria"`, `"Heatstroke"` |
| `populationDensity` | number, optional | Population density |
| `hospitalCapacity` | number, optional | Hospital capacity (thresholds in code assume a 0–100 scale) |
| `vaccinationRate` | number, optional | Vaccination rate (thresholds in code assume a 0–100 scale) |

**Example**

```bash
curl -X POST http://localhost:5000/api/regions \
  -H "Content-Type: application/json" \
  -d '{
        "city": "Faisalabad",
        "activeCases": 300,
        "patients": 600,
        "disease": "Dengue",
        "populationDensity": 12000,
        "hospitalCapacity": 25,
        "vaccinationRate": 35
      }'
```

**Response — `201 Created`** (returns `200 OK` with `"Region updated successfully"` if the city already exists)

```json
{
  "message": "Region added successfully",
  "region": {
    "city": "Faisalabad",
    "risk": "High",
    "activeCases": 300,
    "patients": "600",
    "history": [150, 175, 200, 225, 250, 275, 300],
    "recommendations": [
      "Critical Alert: Declare local health emergency.",
      "Restrict public gatherings and enforce preventive measures.",
      "Prepare overflow medical facilities. Divert non-critical patients.",
      "Initiate immediate vector control and fumigation."
    ]
  }
}
```

*(Response abbreviated; the full object contains every field shown in the `GET` example.)*

### `PUT /api/regions/<id>`

Accepts any subset of the fields above. Omitted fields keep their stored values. On update the API:

1. recalculates the active-case and patient **trends** against the previous values,
2. stores the previous active-case count in `lastWeekCases`,
3. recomputes **risk** and **recommendations**,
4. shifts the 7-day `history` window (drops the oldest value, appends the new one).

Returns `404` if the ID does not exist.

### `DELETE /api/regions/<id>`

Returns `{"message": "Region deleted successfully"}`, or `404` if the ID does not exist.

### `GET /api/weather?city=<name>`

```json
{ "temperature": 31.2, "humidity": 58, "wind": 14.4, "rain": 0 }
```

Units: temperature in °C, humidity in %, wind in km/h (converted from m/s), rain in mm over the last hour.

| Status | Meaning |
|---|---|
| `400` | `city` parameter missing |
| `404` | City not found |
| `500` | API key not configured, or upstream request failed |

---

## 🧮 How Risk Scoring Works

Each region receives a numeric score built from the factors below. The final level is derived from the total.

| Factor | Condition | Score |
|---|---|---:|
| **Patients** | > 500 | +50 |
| | > 200 | +30 |
| | otherwise | +10 |
| **Population density** | > 10,000 | +20 |
| **Hospital capacity** | < 30 | +30 |
| | > 80 | −10 |
| **Vaccination rate** | < 40 | +20 |
| | > 70 | −20 |
| **Disease type** | COVID-19, Influenza | +15 |
| | Dengue, Malaria | +10 |

| Total score | Risk level |
|---|---|
| > 70 | 🔴 **High** |
| > 40 | 🟠 **Medium** |
| ≤ 40 | 🟢 **Low** |

### Recommendation rules

| Trigger | Recommendation |
|---|---|
| Risk = High | Declare local health emergency; restrict public gatherings and enforce preventive measures |
| Risk = Medium | Increase public awareness campaigns |
| Hospital capacity < 40 | Prepare overflow medical facilities; divert non-critical patients |
| Vaccination < 50 **and** disease is COVID-19 / Influenza | Initiate emergency vaccination drives in high-density areas |
| Disease is Dengue or Malaria | Initiate immediate vector control and fumigation |
| Disease is Heatstroke | Issue heat advisories and set up public cooling centers |
| None of the above | Continue standard surveillance protocols |

---

## 🗂 Data & Model Artifacts

### Dataset — `data/final.csv`

- **120 daily records**, 1 Jan 2023 – 30 Apr 2023, no missing values
- **Columns:** `date`, `tempmax`, `tempmin`, `temp`, `humidity`, `precip`, `precipprob`, `windspeed`, `cloudcover`, `visibility`, `uvindex`, `dew`, `sealevelpressure`, `cases`, `risk_level`
- **Label distribution:** Medium 48 · High 39 · Low 33
- The file has no location column.

### Model artifacts — `models/`

`generate_models.py` creates three files from **synthetic data** (600 random samples, 12 weather features, rule-based labels) using a `RandomForestClassifier` (100 trees, seed 42):

| File | Contents |
|---|---|
| `risk_model.pkl` | Trained classifier |
| `label_encoder.pkl` | Maps class labels (`High`, `Low`, `Medium`) to integers |
| `feature_cols.pkl` | Ordered feature list: `tempmax, tempmin, temp, humidity, precip, precipprob, windspeed, cloudcover, visibility, uvindex, dew, sealevelpressure` |

```bash
python generate_models.py   # ⚠️ overwrites the files in models/ with placeholder models
```

> The `.pkl` files in this repository are tracked with **Git LFS**. Run `git lfs pull` after cloning to download them.

---

## 🗄 Database

### Schema — table `region`

| Column | Type | Notes |
|---|---|---|
| `id` | integer, PK | Auto-increment |
| `city` | varchar(100) | Required |
| `risk` | varchar(20) | `Low` / `Medium` / `High` |
| `active_cases` | integer | Default 0 |
| `active_trend` | varchar(20) | e.g. `+14%` |
| `patients` | integer | Default 0 |
| `patients_trend` | varchar(20) | e.g. `-3%` |
| `history` | text | JSON array of the last 7 case counts |
| `disease` | varchar(100) | Nullable |
| `population_density` | float | Nullable |
| `hospital_capacity` | float | Nullable |
| `vaccination_rate` | float | Nullable |
| `recommendations` | text | JSON array of strings |
| `last_week_cases` | integer | Nullable |

### Helper scripts

| Script | Purpose |
|---|---|
| `neon_queries.sql` | Creates the `region` table and inserts six sample regions (Karachi, Lahore, Islamabad, Peshawar, Quetta, Multan) in PostgreSQL / Neon. |
| `scratch/check_db.py` | Confirms the table contains all expected columns. Run from the project folder: `python scratch/check_db.py`. |
| `reset_db.py` | ⚠️ **Destructive.** Drops and recreates every table after an interactive `y/n` confirmation. |

---

## ⚠️ Known Limitations

- **Risk levels come from the rule-based engine.** `app.py` does not load the `.pkl` files in `models/`; the machine-learning artifacts are not yet part of the API's decision path.
- **Thresholds are heuristic.** The scoring weights and cut-offs are hand-set; no validation against real outbreak data is included in this repository.
- **Synthetic history for new regions.** A newly created region gets a generated ascending 7-day history (starting from 50% of the current cases), not real historical data. Chart dates are generated relative to the current day rather than stored.
- **Risk is driven by `patients`.** The patient count is the only case-load input to the score; `activeCases` does not affect it.
- **No authentication, and CORS is open to all origins.** The `__main__` block starts Flask with `debug=True` on `0.0.0.0`. Harden these before any public deployment.
- **No automated tests** are included.

---

## 🛣 Suggested Next Steps

- [ ] Integrate a trained model into `calculate_risk()` using `feature_cols.pkl` and live weather input
- [ ] Add authentication and restrict CORS to known origins
- [ ] Store real daily case history instead of generating it
- [ ] Add unit and API tests
- [ ] Add a Dockerfile / deployment configuration
- [ ] Add input validation and clearer error responses for malformed payloads

---

## 👤 Author

**Gulam Husnain Ali** — Software Engineering student, University of Agriculture, Faisalabad

- GitHub: [@Eng-Hu-snain-Ali](https://github.com/Eng-Hu-snain-Ali)
- LinkedIn: [Husnain Ali](http://www.linkedin.com/in/husnain-ali-039092317)

Built for the **HEC Pakistan Generative AI Cohort 3 Hackathon**.

---

<div align="center">

**Disclaimer:** OutbreakAI is a prototype for decision support and demonstration. It does not replace official public-health guidance.

</div>
