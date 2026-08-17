import re

js_path = r'C:\Users\Usuario\.gemini\antigravity\scratch\VULCAN.01\static\js\app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Fix hide login screen
js = js.replace("document.getElementById('login-screen').classList.remove('active');", 
                "document.getElementById('login-screen').classList.remove('active');\n                document.getElementById('login-screen').classList.add('hidden');")

# Fix show dashboard
js = js.replace("document.getElementById('dashboard-screen').classList.add('active');", 
                "document.getElementById('dashboard-screen').classList.remove('hidden');\n                        document.getElementById('dashboard-screen').classList.add('active');")

# Fix show onboarding
js = js.replace("document.getElementById('onboarding-screen').classList.add('active');", 
                "document.getElementById('onboarding-screen').classList.remove('hidden');\n                document.getElementById('onboarding-screen').classList.add('active');")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("JS UI toggles fixed.")
