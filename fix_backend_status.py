import os
import re

app_path = r'C:\Users\Usuario\.gemini\antigravity\scratch\VULCAN.01\app.py'

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

status_endpoint = """
@app.route('/api/user/check-status', methods=['POST'])
def check_status():
    try:
        data = request.json
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Missing email'}), 400
            
        response = supabase.table('vulcan_users').select('is_blocked').eq('email', email).execute()
        if not response.data:
            return jsonify({'error': 'User not found'}), 404
            
        is_blocked = response.data[0].get('is_blocked', False)
        return jsonify({'is_blocked': is_blocked}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/toggle-block'
"""

if '/api/user/check-status' not in content:
    content = content.replace("@app.route('/api/admin/toggle-block'", status_endpoint)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Backend check-status endpoint added.")
