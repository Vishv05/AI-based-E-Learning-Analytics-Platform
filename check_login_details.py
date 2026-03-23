from pymongo import MongoClient
from datetime import datetime

try:
    client = MongoClient('mongodb://localhost:27017')
    db = client['elearning_analytics']
    users = list(db['users'].find())
    
    print(f'=' * 80)
    print(f'TOTAL REGISTERED USERS: {len(users)}')
    print(f'=' * 80)
    print()
    
    # Categorize by role
    admins = []
    students = []
    teachers = []
    no_role = []
    
    for user in users:
        user_info = {
            'name': user.get('name'),
            'email': user.get('email'),
            'created_at': user.get('created_at', 'N/A')
        }
        
        role = user.get('role')
        if role == 'admin':
            admins.append(user_info)
        elif role == 'student':
            students.append(user_info)
        elif role == 'teacher':
            teachers.append(user_info)
        else:
            no_role.append(user_info)
    
    # Print Admin accounts
    print(f'\n🔐 ADMIN ACCOUNTS ({len(admins)}):')
    print('-' * 80)
    for idx, admin in enumerate(admins, 1):
        print(f'{idx}. Name: {admin["name"]}')
        print(f'   Email: {admin["email"]}')
        print(f'   Registered: {admin["created_at"]}')
        print()
    
    # Print Student accounts
    print(f'\n📚 STUDENT ACCOUNTS ({len(students)}):')
    print('-' * 80)
    for idx, student in enumerate(students, 1):
        print(f'{idx}. Name: {student["name"]}')
        print(f'   Email: {student["email"]}')
        print(f'   Registered: {student["created_at"]}')
        print()
    
    # Print Teacher accounts (if any)
    if teachers:
        print(f'\n👨‍🏫 TEACHER ACCOUNTS ({len(teachers)}):')
        print('-' * 80)
        for idx, teacher in enumerate(teachers, 1):
            print(f'{idx}. Name: {teacher["name"]}')
            print(f'   Email: {teacher["email"]}')
            print(f'   Registered: {teacher["created_at"]}')
            print()
    
    # Print accounts without role
    if no_role:
        print(f'\n⚠️  ACCOUNTS WITHOUT ROLE ({len(no_role)}):')
        print('-' * 80)
        for idx, user in enumerate(no_role, 1):
            print(f'{idx}. Name: {user["name"]}')
            print(f'   Email: {user["email"]}')
            print(f'   Registered: {user["created_at"]}')
            print()
    
    print('=' * 80)
    print(f'SUMMARY: {len(admins)} Admins | {len(students)} Students | {len(teachers)} Teachers | {len(no_role)} No Role')
    print('=' * 80)
    
except Exception as e:
    print(f'Error connecting to MongoDB: {e}')
    import traceback
    traceback.print_exc()
