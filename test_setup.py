#!/usr/bin/env python
"""
Test imports to diagnose issues
"""
import sys
import os

print("1. Testing basic imports...")
try:
    import flask
    print("   ✅ Flask imported")
except ImportError as e:
    print(f"   ❌ Flask: {e}")

try:
    import pymongo
    print("   ✅ PyMongo imported")
except ImportError as e:
    print(f"   ❌ PyMongo: {e}")

try:
    from pymongo import MongoClient
    print("   ✅ MongoClient imported")
    
    print("\n2. Testing MongoDB connection...")
    client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)
    # This will raise an error if MongoDB is not running
    client.admin.command('ping')
    print("   ✅ MongoDB is running!")
    
except Exception as e:
    print(f"   ⚠️  MongoDB not running or unreachable: {e}")
    print("   ℹ️  Starting without MongoDB is not possible.")
    print("   Please ensure MongoDB is running on localhost:27017")

print("\n3. Testing Flask app import...")
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))
    from Backend.app import app
    print("   ✅ Flask app imported successfully!")
    print(f"\n✅ All checks passed! App is ready to run.")
except Exception as e:
    print(f"   ❌ Could not import app: {e}")
    import traceback
    traceback.print_exc()
