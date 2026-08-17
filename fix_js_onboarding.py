import re

js_path = r'C:\Users\Usuario\.gemini\antigravity\scratch\VULCAN.01\static\js\app.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Fix the onboarding transition
js = js.replace("onboardingScreen.classList.remove('active');\n                dashboardScreen.classList.add('active');", 
                "onboardingScreen.classList.remove('active');\n                onboardingScreen.classList.add('hidden');\n                dashboardScreen.classList.remove('hidden');\n                dashboardScreen.classList.add('active');")

# Also ensure it removes the animation classes if any, though hidden/active should be enough.

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js onboarding transition fixed.")
