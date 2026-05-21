import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import mongo_db
from data.careers import FALLBACK_CAREERS
from data.courses import FALLBACK_COURSES

def seed():
    if mongo_db is None:
        print("Error: Database connection is not available.")
        sys.exit(1)

    try:
        print("Clearing existing 'careers' collection...")
        mongo_db.careers.delete_many({})
        print(f"Inserting {len(FALLBACK_CAREERS)} careers into database...")
        mongo_db.careers.insert_many(FALLBACK_CAREERS)
        print("Careers inserted successfully!\n")

        print("Clearing existing 'courses' collection...")
        mongo_db.courses.delete_many({})
        print(f"Inserting {len(FALLBACK_COURSES)} courses into database...")
        mongo_db.courses.insert_many(FALLBACK_COURSES)
        print("Courses inserted successfully!\n")

        print("Database seeding complete!")
    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        sys.exit(1)

if __name__ == "__main__":
    seed()
