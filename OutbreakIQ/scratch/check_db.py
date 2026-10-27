import os
from app import app, db, Region
from sqlalchemy import inspect
from dotenv import load_dotenv

load_dotenv()

def check_schema():
    with app.app_context():
        inspector = inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('region')]
        print(f"Columns in 'region' table: {columns}")
        
        expected_columns = ['disease', 'population_density', 'hospital_capacity', 'vaccination_rate', 'recommendations', 'last_week_cases']
        missing = [c for c in expected_columns if c not in columns]
        
        if missing:
            print(f"MISSING COLUMNS: {missing}")
        else:
            print("Schema is up to date!")

if __name__ == "__main__":
    check_schema()
