from pymongo import MongoClient

try:
    client = MongoClient('mongodb://localhost:27017')
    db = client['elearning_analytics']
    users = list(db['users'].find())
    print(f'Total users: {len(users)}\n')
    for user in users:
        has_password = 'password' in user and user.get('password') is not None
        password_hash = user.get('password', 'MISSING')[:30] + '...' if has_password else 'NO PASSWORD'
        print(f'Email: {user.get("email")}')
        print(f'  Role: {user.get("role")}')
        print(f'  Password: {password_hash}')
        print()
except Exception as e:
    print(f'Error connecting to MongoDB: {e}')
    import traceback
    traceback.print_exc()
