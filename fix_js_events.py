import os
import re

js_path = r'C:\Users\Usuario\.gemini\antigravity\scratch\VULCAN.01\static\js\app.js'

with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the broken login form listener
new_auth_js = """
// --- Login Logic ---
let authMode = 'login';
window.setAuthMode = function(mode) {
    authMode = mode;
    document.getElementById('tab-login').classList.toggle('active', mode === 'login');
    document.getElementById('tab-register').classList.toggle('active', mode === 'register');
    document.getElementById('group-name').style.display = mode === 'register' ? 'flex' : 'none';
    document.getElementById('btn-auth').textContent = mode === 'register' ? 'Criar Conta' : 'Entrar';
    document.getElementById('auth-error').classList.add('hidden');
};

const loginForm = document.getElementById('login-form');
if(loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('auth-email').value;
        const password = document.getElementById('auth-password').value;
        const nameInput = document.getElementById('auth-name');
        const name = nameInput ? nameInput.value : '';
        const errorEl = document.getElementById('auth-error');

        errorEl.classList.add('hidden');

        try {
            if (authMode === 'register') {
                const res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email, password, name })
                });
                const data = await res.json();
                if(!res.ok) throw new Error(data.error || 'Erro ao criar conta');
                
                alert('Conta criada com sucesso! Por favor, faça login.');
                setAuthMode('login');
            } else {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if(!res.ok) throw new Error(data.error || 'Credenciais inválidas');
                
                currentUser = { email: email, name: data.name || email.split('@')[0] };
                localStorage.setItem('vulcan_user', email);
                
                // Hide login screen
                document.getElementById('login-screen').classList.remove('active');
                
                // Try load plan
                const planRes = await fetch('/api/user/load-plan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email })
                });
                if(planRes.ok) {
                    const planData = await planRes.json();
                    if(planData.plan) {
                        currentPlan = planData.plan;
                        document.getElementById('dashboard-screen').classList.add('active');
                        renderDashboard();
                        startBlockPolling();
                        return;
                    }
                }
                
                // If no plan, show onboarding
                document.getElementById('onboarding-screen').classList.add('active');
                if(document.getElementById('header-username')) document.getElementById('header-username').textContent = currentUser.name;
                if(document.getElementById('profile-name')) document.getElementById('profile-name').textContent = currentUser.name;
            }
        } catch(err) {
            errorEl.textContent = err.message;
            errorEl.classList.remove('hidden');
            if (err.message.includes('not found') || err.message.includes('inválidas')) {
                // If user doesn't exist, tell them
                alert('Conta não encontrada ou dados incorretos! Se você é novo, clique em "Criar Conta".');
            }
        }
    });
}

// Polling for Block Status
let pollingInterval = null;
function startBlockPolling() {
    if(pollingInterval) clearInterval(pollingInterval);
    pollingInterval = setInterval(async () => {
        if(!currentUser || !currentUser.email) return;
        try {
            const res = await fetch('/api/user/check-status', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email: currentUser.email })
            });
            if(res.ok) {
                const data = await res.json();
                if(data.is_blocked) {
                    alert('Sua conta foi bloqueada ou seu acesso de 21 dias expirou. Entre em contato com o suporte.');
                    localStorage.removeItem('vulcan_user');
                    location.reload();
                }
            }
        } catch(e) { console.error('Erro ao verificar status', e); }
    }, 60000);
}

"""

# Regex to safely replace the old login logic
js = re.sub(r'// --- Login Logic ---.*?const loginForm = document\.getElementById\(\'login-form\'\).*?errorEl\.classList\.remove\(\'hidden\'\);\n\s*\}\n\s*\} catch.*?\n\s*\}\n\s*\}\);\n', new_auth_js, js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("JS Auth logic updated successfully!")
