import re

# Fix index.html
with open(r'C:\Users\Usuario\.gemini\antigravity\scratch\VULCAN.01\templates\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_login_form = """
                <form id="login-form" class="glass-panel">
                    <div style="display:flex; justify-content:space-between; margin-bottom: 20px;">
                        <button type="button" class="tab-btn active" id="tab-login" onclick="setAuthMode('login')">Entrar</button>
                        <button type="button" class="tab-btn" id="tab-register" onclick="setAuthMode('register')">Criar Conta</button>
                    </div>
                    <div class="input-group" id="group-name" style="display:none;">
                        <i data-lucide="user"></i>
                        <input type="text" id="auth-name" placeholder="Seu Nome Completo">
                    </div>
                    <div class="input-group">
                        <i data-lucide="mail"></i>
                        <input type="email" id="auth-email" placeholder="E-mail" required>
                    </div>
                    <div class="input-group">
                        <i data-lucide="lock"></i>
                        <input type="password" id="auth-password" placeholder="Senha" required>
                    </div>
                    <button type="submit" class="btn-primary" id="btn-auth">Entrar</button>
                    <div id="auth-error" class="error-text hidden"></div>
                </form>
"""

html = re.sub(r'<form id="login-form".*?</form>', new_login_form, html, flags=re.DOTALL)

with open(r'C:\Users\Usuario\.gemini\antigravity\scratch\VULCAN.01\templates\index.html', 'w', encoding='utf-8') as f:
    f.write(html)


# Fix app.js
with open(r'C:\Users\Usuario\.gemini\antigravity\scratch\VULCAN.01\static\js\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

new_auth_js = """
// Auth Mode
let authMode = 'login';
function setAuthMode(mode) {
    authMode = mode;
    document.getElementById('tab-login').classList.toggle('active', mode === 'login');
    document.getElementById('tab-register').classList.toggle('active', mode === 'register');
    document.getElementById('group-name').style.display = mode === 'register' ? 'flex' : 'none';
    document.getElementById('btn-auth').textContent = mode === 'register' ? 'Criar Conta' : 'Entrar';
    document.getElementById('auth-error').classList.add('hidden');
}

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('auth-email').value;
    const password = document.getElementById('auth-password').value;
    const name = document.getElementById('auth-name').value;
    const errorDiv = document.getElementById('auth-error');
    
    errorDiv.classList.add('hidden');
    
    try {
        if (authMode === 'register') {
            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email, password, name })
            });
            const data = await res.json();
            if(!res.ok) throw new Error(data.error);
            // Auto login after register
            setAuthMode('login');
            alert('Conta criada com sucesso! Faça login.');
        } else {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if(!res.ok) throw new Error(data.error || 'Credenciais inválidas');
            
            // Login success
            document.getElementById('login-screen').classList.remove('active');
            document.getElementById('login-screen').classList.add('hidden');
            
            // Try to load plan
            const planRes = await fetch('/api/user/load-plan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email })
            });
            if (planRes.ok) {
                const planData = await planRes.json();
                if(planData.plan) {
                    currentPlan = planData.plan;
                    document.getElementById('main-dashboard').classList.remove('hidden');
                    document.getElementById('main-dashboard').classList.add('active');
                    renderDashboard();
                    return;
                }
            }
            
            // No plan, go to onboarding
            document.getElementById('onboarding-screen').classList.remove('hidden');
            document.getElementById('onboarding-screen').classList.add('active');
        }
    } catch(err) {
        errorDiv.textContent = err.message;
        errorDiv.classList.remove('hidden');
    }
});
"""

# Replace the login form event listener in app.js
js = re.sub(r'document\.getElementById\(\'login-form\'\)\.addEventListener\(\'submit\', async \(e\) => \{.*?\n\}\);', new_auth_js, js, flags=re.DOTALL)

with open(r'C:\Users\Usuario\.gemini\antigravity\scratch\VULCAN.01\static\js\app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Auth JS and HTML updated.")
