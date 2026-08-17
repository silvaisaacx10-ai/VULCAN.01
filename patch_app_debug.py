import re

app_path = r'C:\Users\Usuario\.gemini\antigravity\scratch\VULCAN.01\app.py'

with open(app_path, 'r', encoding='utf-8') as f:
    app_py = f.read()

# Capture the error
init_code = """
SUPABASE_INIT_ERROR = None
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Failed to initialize Supabase client: {e}")
    import traceback
    SUPABASE_INIT_ERROR = str(e) + " | " + traceback.format_exc()
    supabase = None
"""

# We replace the try/except block
app_py = re.sub(r'try:\n\s*supabase: Client = create_client\(SUPABASE_URL, SUPABASE_KEY\)\nexcept Exception as e:\n\s*print\(f"Failed to initialize Supabase client: \{e\}"\)\n\s*supabase = None', init_code, app_py)

# In api/auth/login, return the error
login_check = """@app.route('/api/auth/login', methods=['POST'])
def login():
    if supabase is None:
        return jsonify({'error': f"CRITICAL SUPABASE INIT ERROR: {SUPABASE_INIT_ERROR}"}), 500
"""
app_py = re.sub(r"@app\.route\('/api/auth/login', methods=\['POST'\]\)\ndef login\(\):", login_check, app_py)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_py)

print("app.py patched for debugging.")
