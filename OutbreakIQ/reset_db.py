import os
from app import app, db, Region
from dotenv import load_dotenv

load_dotenv()

def reset_database():
    print("Connecting to database...")
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables with new schema...")
        db.create_all()
        print("Database reset successfully! You can now start the Flask server.")

if __name__ == "__main__":
    confirm = input("WARNING: This will drop all tables and delete all existing data. Are you sure? (y/n): ")
    if confirm.lower() == 'y':
        reset_database()
    else:
        print("Operation cancelled.")
