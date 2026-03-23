import os
import sqlite3
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, 'users.db')

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'elearning_analytics')
MONGO_USERS_COLLECTION = 'users'


def main():
    if not os.path.exists(SQLITE_PATH):
        raise FileNotFoundError(f'SQLite DB not found at {SQLITE_PATH}')

    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client[MONGO_DB_NAME]
    users_collection = mongo_db[MONGO_USERS_COLLECTION]
    users_collection.create_index('email', unique=True)

    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, password, created_at FROM users')
    rows = cursor.fetchall()
    conn.close()

    inserted = 0
    skipped = 0

    for row in rows:
        legacy_id, name, email, password_hash, created_at = row
        doc = {
            'name': name,
            'email': email,
            'password': password_hash,
            'created_at': created_at or datetime.utcnow().isoformat(),
            'legacy_id': legacy_id
        }
        try:
            result = users_collection.update_one(
                {'email': email},
                {'$setOnInsert': doc},
                upsert=True
            )
            if result.upserted_id is not None:
                inserted += 1
            else:
                skipped += 1
        except DuplicateKeyError:
            skipped += 1

    print(f'Migrated users: {inserted}')
    print(f'Skipped existing: {skipped}')


if __name__ == '__main__':
    main()
