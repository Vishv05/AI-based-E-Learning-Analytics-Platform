#!/usr/bin/env python
"""
Simple script to run the Flask application with error handling
"""
import sys
import os

# Add Backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

try:
    print("=" * 70)
    print("Starting AI E-Learning Analytics Platform...")
    print("=" * 70)
    
    # Import and run the app
    from Backend.app import app
    
    print("\n✅ Flask app imported successfully")
    print("\n🌐 Starting server...")
    print("   Login:     http://127.0.0.1:5000/login")
    print("   Register:  http://127.0.0.1:5000/register") 
    print("   Dashboard: http://127.0.0.1:5000/dashboard")
    print("\n⏸️  Press CTRL+C to stop\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nMissing module. Please install dependencies:")
    print("  pip install flask pymongo python-dotenv pandas numpy")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error running app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
