// STATE E DATA DO APP
let appState = {
    plan: null, // Plano recebido do Backend
    daily: {
        date: "",
        water: 0,
        eatenMeals: [], // Lista de índices das refeições consumidas
        completedExercises: {}, // Mapeia { "dia_da_semana": [indices_exercicios] }
        checklist: {
            diet: false,
            workout: false,
            water: false,
            sleep: false
        }
    }
};

let authState = {
    isLoggedIn: false,
    email: '',
    token: '',
    name: ''
};

// Configurações do Círculo de Progresso
const CIRCLE_RADIUS = 70;
const CIRCLE_CIRCUMFERENCE = 2 * Math.PI * CIRCLE_RADIUS;

// DOM ELEMENTS (lazy loaded where possible, except constants)
let loginScreen, onboardingScreen, loadingScreen, mainScreen;
let profileForm, loadingMessage, btnSubmitWizard, btnResetPlan;

// INICIALIZAÇÃO DO APP
document.addEventListener('DOMContentLoaded', async () => {
    // Pegar elementos globais
    loginScreen = document.getElementById('login-screen');
    onboardingScreen = document.getElementById('onboarding-screen');
    loadingScreen = document.getElementById('loading-screen');
    mainScreen = document.getElementById('main-screen');
    
    loadingMessage = document.getElementById('loading-message');
    btnSubmitWizard = document.getElementById('btn-submit-wizard');
    btnResetPlan = document.getElementById('btn-reset-plan');

    // Inicializar Lucide Icons
    lucide.createIcons();

    // Configurar o progresso do círculo
    const progressCircle = document.getElementById('calorie-progress-circle');
    if (progressCircle) {
        progressCircle.style.strokeDasharray = `${CIRCLE_CIRCUMFERENCE} ${CIRCLE_CIRCUMFERENCE}`;
        progressCircle.style.strokeDashoffset = CIRCLE_CIRCUMFERENCE;
    }

    // Configurar navegação do Wizard
    setupWizard();

    // Configurar navegação entre abas
    setupTabs();

    // Configurar Auth Tabs
    setupAuthTabs();

    // Configurar botões extras
    if (btnResetPlan) {
        btnResetPlan.addEventListener('click', resetAllData);
    }
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }

    // Carregar estado de autenticação
    loadAuthState();

    // INIT FLOW UPDATE
    if (authState.isLoggedIn && authState.email) {
        // Tentar carregar plano do servidor
        try {
            const resp = await fetch('/api/user/load-plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: authState.email })
            });
            if (resp.ok) {
                const data = await resp.json();
                if (data.plan) {
                    appState.plan = data.plan;
                    checkDailyReset();
                    saveStateToStorage();
                    renderApp();
                    if(loginScreen) loginScreen.classList.remove('active');
                    if(onboardingScreen) onboardingScreen.classList.remove('active');
                    if(mainScreen) mainScreen.classList.add('active');
                    return;
                }
            }
        } catch (e) {
            console.error("Erro ao carregar plano:", e);
        }
        // Se não conseguiu ou não tem plano, vai pro onboarding
        if(loginScreen) loginScreen.classList.remove('active');
        if(mainScreen) mainScreen.classList.remove('active');
        if(onboardingScreen) onboardingScreen.classList.add('active');
    } else {
        // Se não está logado, verifica localStorage
        const savedState = localStorage.getItem('shredded_app_state');
        if (savedState) {
            const parsed = JSON.parse(savedState);
            if (parsed && parsed.plan) {
                appState = parsed;
                checkDailyReset();
                renderApp();
                if(loginScreen) loginScreen.classList.remove('active');
                if(onboardingScreen) onboardingScreen.classList.remove('active');
                if(mainScreen) mainScreen.classList.add('active');
                return;
            }
        }
        // Se nada, mostra login screen
        if(onboardingScreen) onboardingScreen.classList.remove('active');
        if(mainScreen) mainScreen.classList.remove('active');
        if(loginScreen) loginScreen.classList.add('active');
    }
});

// ========================================================
// CONTROLE DE ESTADO E LOCAL STORAGE (APP & AUTH)
// ========================================================
function loadAuthState() {
    const saved = localStorage.getItem('shredded_auth_state');
    if (saved) {
        try { authState = JSON.parse(saved); } catch(e){}
    }
}

function saveAuthState() {
    localStorage.setItem('shredded_auth_state', JSON.stringify(authState));
}

function saveStateToStorage() {
    localStorage.setItem('shredded_app_state', JSON.stringify(appState));
}

function checkDailyReset() {
    const today = getTodayDateString();
    if (appState.daily.date !== today) {
        appState.daily.date = today;
        appState.daily.water = 0;
        appState.daily.eatenMeals = [];
        appState.daily.completedExercises = {};
        appState.daily.checklist = { diet: false, workout: false, water: false, sleep: false };
        saveStateToStorage();
    }
}

function getTodayDateString() {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function resetAllData() {
    if (confirm('Tem certeza que deseja apagar seus dados e gerar um novo plano?')) {
        localStorage.removeItem('shredded_app_state');
        location.reload();
    }
}

// ========================================================
// AUTENTICAÇÃO
// ========================================================
function setupAuthTabs() {
    const tabs = document.querySelectorAll('[data-auth-tab]');
    tabs.forEach(t => {
        t.addEventListener('click', (e) => {
            switchAuthTab(e.target.closest('[data-auth-tab]').getAttribute('data-auth-tab'));
        });
    });
}

function switchAuthTab(tab) {
    const loginForm = document.getElementById('auth-login-form');
    const registerForm = document.getElementById('auth-register-form');
    if (tab === 'login') {
        if(loginForm) loginForm.style.display = 'block';
        if(registerForm) registerForm.style.display = 'none';
    } else {
        if(loginForm) loginForm.style.display = 'none';
        if(registerForm) registerForm.style.display = 'block';
    }

    const tabs = document.querySelectorAll('[data-auth-tab]');
    tabs.forEach(t => {
        if(t.getAttribute('data-auth-tab') === tab) {
            t.classList.add('active');
        } else {
            t.classList.remove('active');
        }
    });
}

async function handleLogin(e) {
    if(e) e.preventDefault();
    const email = document.getElementById('login-email')?.value;
    const password = document.getElementById('login-password')?.value;
    
    if(!email || !password) {
        showToast('Preencha email e senha', 'error');
        return;
    }
    
    try {
        const resp = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        const data = await resp.json();
        
        if(!resp.ok) {
            showToast(data.message || 'Erro ao fazer login', 'error');
            return;
        }
        
        authState = { isLoggedIn: true, email: email, token: data.token, name: data.name };
        saveAuthState();
        
        // Try load plan
        const planResp = await fetch('/api/user/load-plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: authState.email })
        });
        
        if (planResp.ok) {
            const planData = await planResp.json();
            if (planData.plan) {
                appState.plan = planData.plan;
                checkDailyReset();
                saveStateToStorage();
                renderApp();
                if(loginScreen) loginScreen.classList.remove('active');
                if(mainScreen) mainScreen.classList.add('active');
                return;
            }
        }
        
        if(loginScreen) loginScreen.classList.remove('active');
        if(onboardingScreen) onboardingScreen.classList.add('active');
        
    } catch(err) {
        showToast('Erro de conexão', 'error');
    }
}

async function handleRegister(e) {
    if(e) e.preventDefault();
    const name = document.getElementById('register-name')?.value;
    const email = document.getElementById('register-email')?.value;
    const password = document.getElementById('register-password')?.value;
    
    if(!name || !email || !password) {
        showToast('Preencha todos os campos', 'error');
        return;
    }
    
    try {
        const resp = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, email, password})
        });
        const data = await resp.json();
        
        if(!resp.ok) {
            showToast(data.message || 'Erro ao registrar', 'error');
            return;
        }
        
        showToast('Registrado com sucesso!', 'success');
        
        const loginEmail = document.getElementById('login-email');
        const loginPass = document.getElementById('login-password');
        if(loginEmail) loginEmail.value = email;
        if(loginPass) loginPass.value = password;
        
        await handleLogin();
        
    } catch(err) {
        showToast('Erro de conexão', 'error');
    }
}

function handleLogout() {
    authState = { isLoggedIn: false, email: '', token: '', name: '' };
    saveAuthState();
    localStorage.removeItem('shredded_app_state');
    location.reload();
}

function skipLogin() {
    authState.isLoggedIn = false;
    saveAuthState();
    if(loginScreen) loginScreen.classList.remove('active');
    if(onboardingScreen) onboardingScreen.classList.add('active');
}

// ========================================================
// TOAST NOTIFICATION
// ========================================================
let toastTimeout = null;
function showToast(message, type='error') {
    const toast = document.getElementById('validation-toast');
    const msg = document.getElementById('validation-toast-msg');
    if(!toast || !msg) return;
    
    msg.textContent = message;
    if(type === 'success') {
        toast.classList.add('success');
    } else {
        toast.classList.remove('success');
    }
    
    toast.classList.remove('hidden');
    toast.classList.add('visible');
    
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        hideToast();
    }, 4000);
}

function hideToast() {
    const toast = document.getElementById('validation-toast');
    if(toast) {
        toast.classList.remove('visible');
        toast.classList.add('hidden');
    }
}

// ========================================================
// VALIDAÇÃO FRONTEND
// ========================================================
function validateFormData(name, age, weight, height) {
    let valid = true;
    
    document.querySelectorAll('.input-error').forEach(el => el.classList.remove('input-error'));
    
    if(!name || name.length < 2 || name.length > 50) {
        document.getElementById('input-name')?.classList.add('input-error');
        valid = false;
    }
    if(isNaN(age) || age < 14 || age > 80) {
        document.getElementById('input-age')?.classList.add('input-error');
        valid = false;
    }
    if(isNaN(weight) || weight < 30 || weight > 250) {
        document.getElementById('input-weight')?.classList.add('input-error');
        valid = false;
    }
    if(isNaN(height) || height < 100 || height > 230) {
        document.getElementById('input-height')?.classList.add('input-error');
        valid = false;
    }
    
    if(!valid) {
        showToast('Preencha os campos corretamente', 'error');
        return false;
    }
    
    const heightM = height / 100;
    const bmi = weight / (heightM * heightM);
    if(bmi < 12 || bmi > 60) {
        showToast('Valores de peso/altura parecem inválidos.', 'error');
        return false;
    }
    
    return true;
}

// ========================================================
// LÓGICA DO ONBOARDING / WIZARD (FORMULÁRIO MULTI-ETAPAS)
// ========================================================
function setupWizard() {
    const steps = document.querySelectorAll('.wizard-step');
    const nextButtons = document.querySelectorAll('.btn-next');
    const prevButtons = document.querySelectorAll('.btn-prev');
    const progressFill = document.getElementById('wizard-progress');
    let currentStepIdx = 0;

    function updateStepVisibility() {
        steps.forEach((step, idx) => {
            if (idx === currentStepIdx) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });

        // Atualizar barra de progresso do wizard
        if (progressFill) {
            const pct = ((currentStepIdx + 1) / steps.length) * 100;
            progressFill.style.width = `${pct}%`;
        }
    }

    nextButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const currentStep = steps[currentStepIdx];
            // Validar inputs do passo atual (HTML5 simple validation)
            const inputs = currentStep.querySelectorAll('input[required], select[required]');
            let valid = true;
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.reportValidity();
                    valid = false;
                }
            });

            if (valid) {
                currentStepIdx++;
                updateStepVisibility();
            }
        });
    });

    prevButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            if (currentStepIdx > 0) {
                currentStepIdx--;
                updateStepVisibility();
            }
        });
    });

    if (btnSubmitWizard) {
        btnSubmitWizard.addEventListener('click', submitOnboardingForm);
    }
}

// SUBMISSÃO DO FORMULÁRIO DE ONBOARDING PARA O BACKEND
async function submitOnboardingForm() {
    // Coleta dos dados do formulário
    const name = document.getElementById('input-name').value;
    const age = parseInt(document.getElementById('input-age').value);
    const gender = document.querySelector('input[name="gender"]:checked')?.value || 'm';
    const weight = parseFloat(document.getElementById('input-weight').value);
    const height = parseFloat(document.getElementById('input-height').value);
    const activity = document.getElementById('input-activity').value;
    const goal = document.querySelector('input[name="goal"]:checked')?.value || 'maintain';
    const dietPreference = document.querySelector('input[name="diet_preference"]:checked')?.value || 'omnivore';

    if(!validateFormData(name, age, weight, height)) {
        return;
    }

    // Transição de tela: Onboarding -> Loading
    if(onboardingScreen) onboardingScreen.classList.remove('active');
    if(loadingScreen) loadingScreen.classList.add('active');

    // Mensagens de carregamento simuladas
    const messages = [
        "Calculando sua taxa metabólica basal (BMR)...",
        "Ajustando gasto calórico diário (TDEE)...",
        "Dividindo seus macronutrientes sob medida...",
        "Montando sua rotina semanal de treinos...",
        "Calculando porções da dieta..."
    ];
    let msgIdx = 0;
    const msgInterval = setInterval(() => {
        if(loadingMessage) loadingMessage.textContent = messages[msgIdx];
        msgIdx = (msgIdx + 1) % messages.length;
    }, 600);

    try {
        const response = await fetch('/api/generate-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                gender,
                weight,
                height,
                age,
                activity_level: activity,
                goal,
                diet_preference: dietPreference
            })
        });

        if (!response.ok) {
            throw new Error('Falha ao gerar plano no servidor.');
        }

        const data = await response.json();

        // Save plan to server if logged in
        if (authState.isLoggedIn && authState.email) {
            try {
                await fetch('/api/user/save-plan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email: authState.email, plan: data })
                });
            } catch (e) {
                console.error("Erro ao salvar plano no servidor", e);
            }
        }

        // Salvar plano gerado no estado
        appState.plan = data;
        appState.daily.date = getTodayDateString();
        appState.daily.water = 0;
        appState.daily.eatenMeals = [];
        appState.daily.completedExercises = {};
        appState.daily.checklist = { diet: false, workout: false, water: false, sleep: false };

        saveStateToStorage();

        // Parar animação e ir para o Dashboard
        clearInterval(msgInterval);
        
        // Efeito Confete de sucesso
        triggerConfetti();

        // Renderizar interface
        renderApp();

        // Trocar telas
        if(loadingScreen) loadingScreen.classList.remove('active');
        if(mainScreen) mainScreen.classList.add('active');

    } catch (err) {
        clearInterval(msgInterval);
        showToast('Erro ao gerar plano. Verifique seus dados.', 'error');
        if(loadingScreen) loadingScreen.classList.remove('active');
        if(onboardingScreen) onboardingScreen.classList.add('active');
    }
}

// ========================================================
// RENDERIZADOR COMPLETO DA INTERFACE (MAIN SCREEN)
// ========================================================
function renderApp() {
    if (!appState.plan) return;

    const plan = appState.plan;

    // 1. Atualizar Textos Gerais
    const dUserName = document.getElementById('display-user-name');
    if(dUserName) dUserName.textContent = plan.user.name;
    
    const pUserName = document.getElementById('profile-user-name');
    if(pUserName) pUserName.textContent = plan.user.name;
    
    const pUserEmail = document.getElementById('profile-user-email');
    if(pUserEmail) {
        if(authState.isLoggedIn) {
            pUserEmail.textContent = authState.email;
        } else {
            pUserEmail.textContent = "Visitante";
        }
    }
    
    const btnLogout = document.getElementById('btn-logout');
    if(btnLogout) {
        btnLogout.style.display = authState.isLoggedIn ? 'block' : 'none';
    }
    
    let goalText = "Objetivo: Manutenção / Definição";
    if (plan.user.goal === 'lose') goalText = "Foco: Perda de Peso / Definição";
    else if (plan.user.goal === 'gain') goalText = "Foco: Ganho de Massa / Hipertrofia";
    
    const pUserGoal = document.getElementById('profile-user-goal');
    if(pUserGoal) pUserGoal.textContent = goalText;
    
    const wGoalDesc = document.getElementById('workout-goal-desc');
    if(wGoalDesc) wGoalDesc.textContent = goalText + ` (${(plan.user.diet_preference || '').toUpperCase()})`;

    // 2. Renderizar Estatísticas de Perfil e BMI
    const pWeight = document.getElementById('prof-weight');
    if(pWeight) pWeight.textContent = `${plan.user.weight} kg`;
    
    const pHeight = document.getElementById('prof-height');
    if(pHeight) pHeight.textContent = `${plan.user.height} cm`;
    
    const pBmr = document.getElementById('prof-bmr');
    if(pBmr) pBmr.textContent = `${plan.nutrition.bmr} kcal`;
    
    const pTdee = document.getElementById('prof-tdee');
    if(pTdee) pTdee.textContent = `${plan.nutrition.tdee} kcal`;
    
    // BMI Logic
    if (plan.nutrition.bmi) {
        const bmiVal = document.getElementById('dash-bmi-value');
        if(bmiVal) bmiVal.textContent = plan.nutrition.bmi;
        
        const bmiBadge = document.getElementById('dash-bmi-badge');
        if(bmiBadge) bmiBadge.textContent = plan.nutrition.bmi_class;
        
        const profBmi = document.getElementById('prof-bmi');
        if(profBmi) profBmi.textContent = plan.nutrition.bmi;
        
        const profBmiClass = document.getElementById('prof-bmi-class');
        if(profBmiClass) profBmiClass.textContent = plan.nutrition.bmi_class;
        
        const bmiContainer = document.getElementById('bmi-card-container');
        if (bmiContainer) {
            let status = 'normal';
            if (plan.nutrition.bmi < 25) status = 'normal';
            else if (plan.nutrition.bmi >= 25 && plan.nutrition.bmi < 30) status = 'overweight';
            else status = 'obese';
            bmiContainer.setAttribute('data-status', status);
        }
        
        const bmiIndicator = document.getElementById('bmi-indicator');
        if (bmiIndicator) {
            let val = plan.nutrition.bmi;
            if(val < 15) val = 15;
            if(val > 45) val = 45;
            const pct = ((val - 15) / 30) * 100;
            bmiIndicator.style.left = `${pct}%`;
        }
    }

    // 3. Atualizar Alvos do Dashboard
    const dCal = document.getElementById('dash-calories-target');
    if(dCal) dCal.textContent = plan.nutrition.target_calories;
    
    const dpCal = document.getElementById('diet-pill-cal');
    if(dpCal) dpCal.textContent = plan.nutrition.target_calories;
    
    const dpProt = document.getElementById('diet-pill-prot');
    if(dpProt) dpProt.textContent = plan.nutrition.protein;
    
    const dpCarb = document.getElementById('diet-pill-carb');
    if(dpCarb) dpCarb.textContent = plan.nutrition.carbs;
    
    const dpFat = document.getElementById('diet-pill-fat');
    if(dpFat) dpFat.textContent = plan.nutrition.fats;

    // Meta de água padrão
    const waterTarget = plan.water_target || Math.round(plan.user.weight * 35);
    const wtVal = document.getElementById('water-target-val');
    if(wtVal) wtVal.textContent = waterTarget;

    // 4. Renderizar Abas Principais e Adicionais
    renderDietTab();
    renderWorkoutTab();
    renderTips();
    renderSupplements();
    renderProgress();

    // 5. Atualizar Dashboard (Calorias, Macros, Água, Checklist)
    updateDashboardVisuals();
}

function renderTips() {
    const container = document.getElementById('tips-container');
    if(!container || !appState.plan.tips) return;
    
    const header = container.firstElementChild;
    container.innerHTML = '';
    if(header) container.appendChild(header);
    
    appState.plan.tips.forEach(tipText => {
        const div = document.createElement('div');
        div.className = 'tip-item';
        div.innerHTML = `<i data-lucide="lightbulb"></i><span>${tipText}</span>`;
        container.appendChild(div);
    });
    // Re-iniciar UI e icones
    lucide.createIcons();
    setupPhase2Features();
}

function renderSupplements() {
    const container = document.getElementById('supplements-container');
    if(!container || !appState.plan.supplements) return;
    
    // Clear old ones (preserve header if needed, but normally just cards)
    const header = container.querySelector('h2, h3, .section-header');
    container.innerHTML = '';
    if(header) container.appendChild(header);
    
    appState.plan.supplements.forEach(sup => {
        const div = document.createElement('div');
        div.className = 'supplement-card';
        // sup priority can be used as class
        const prioClass = sup.priority ? sup.priority.toLowerCase() : 'optional';
        div.innerHTML = `
            <span class="priority-badge ${prioClass}">${sup.priority || 'Opcional'}</span>
            <div style="font-weight: bold; margin-bottom: 4px; font-size: 1.1em;">${sup.name}</div>
            <div style="font-size: 0.9em; color: var(--text-secondary); line-height: 1.4;">
                <div><strong>Dose:</strong> ${sup.dose}</div>
                <div><strong>Quando:</strong> ${sup.when}</div>
                <div style="margin-top: 4px;"><strong>Por que:</strong> ${sup.why}</div>
            </div>
        `;
        container.appendChild(div);
    });
}

function renderProgress() {
    const prog = appState.plan.progress;
    if(!prog) return;
    
    const weekly = document.getElementById('progress-weekly');
    if(weekly) weekly.textContent = prog.weekly_change;
    
    const monthly = document.getElementById('progress-monthly');
    if(monthly) monthly.textContent = prog.monthly_change;
    
    const timeline = document.getElementById('progress-timeline');
    if(timeline) timeline.textContent = prog.expected_timeline;
    
    const disclaimer = document.getElementById('progress-disclaimer');
    if(disclaimer) disclaimer.textContent = prog.disclaimer;
}

// ========================================================
// CONTROLE DO PAINEL / DASHBOARD
// ========================================================
function updateDashboardVisuals() {
    if (!appState.plan) return;

    const nutrition = appState.plan.nutrition;
    const meals = appState.plan.diet_plan;

    // Calcular calorias e macros ingeridas no dia
    let eatenCal = 0;
    let eatenProt = 0;
    let eatenCarb = 0;
    let eatenFat = 0;

    appState.daily.eatenMeals.forEach(mealIdx => {
        const meal = meals[mealIdx];
        if (meal) {
            eatenCal += meal.calories;
            eatenProt += meal.protein;
            eatenCarb += meal.carbs;
            eatenFat += meal.fats;
        }
    });

    // Atualizar números de Calorias
    const dCeaten = document.getElementById('dash-calories-eaten');
    if(dCeaten) dCeaten.textContent = Math.round(eatenCal);

    // Atualizar progress ring SVG
    const progressCircle = document.getElementById('calorie-progress-circle');
    if (progressCircle) {
        const pctCal = Math.min(1.0, eatenCal / nutrition.target_calories);
        const offset = CIRCLE_CIRCUMFERENCE - (pctCal * CIRCLE_CIRCUMFERENCE);
        progressCircle.style.strokeDashoffset = offset;

        // Mudar cor do círculo caso ultrapasse as calorias
        if (eatenCal > nutrition.target_calories && appState.plan.user.goal === 'lose') {
            progressCircle.style.stroke = '#ff4757'; // Vermelho se furar a dieta de corte
        } else {
            progressCircle.style.stroke = '#d2ff00'; // Volt Neon
        }
    }

    // Atualizar barras de macros
    updateMacroBar('protein', eatenProt, nutrition.protein);
    updateMacroBar('carbs', eatenCarb, nutrition.carbs);
    updateMacroBar('fats', eatenFat, nutrition.fats);

    // Atualizar visualizador de Água
    const waterTarget = appState.plan.water_target || Math.round(appState.plan.user.weight * 35);
    const wAmt = document.getElementById('water-amount-txt');
    if(wAmt) wAmt.textContent = `${appState.daily.water} ml`;
    
    const wWave = document.getElementById('water-wave');
    if (wWave) {
        const waterPct = Math.min(100, (appState.daily.water / waterTarget) * 100);
        wWave.style.bottom = `calc(${waterPct}% - 100px)`;
    }

    // Se bateu meta de água, marca na checklist
    appState.daily.checklist.water = (appState.daily.water >= waterTarget);
    const chkWater = document.getElementById('chk-water');
    if(chkWater) chkWater.checked = appState.daily.checklist.water;

    // Se seguiu toda a dieta, marca
    appState.daily.checklist.diet = (appState.daily.eatenMeals.length === meals.length);
    const chkDiet = document.getElementById('chk-diet');
    if(chkDiet) chkDiet.checked = appState.daily.checklist.diet;

    // Atualizar Checkboxes da Checklist Diária
    const chkWorkout = document.getElementById('chk-workout');
    if(chkWorkout) chkWorkout.checked = appState.daily.checklist.workout;
    
    const chkSleep = document.getElementById('chk-sleep');
    if(chkSleep) chkSleep.checked = appState.daily.checklist.sleep;

    // Ouvintes para salvar cliques da Checklist do Dashboard
    setupChecklistListeners();
}

function updateMacroBar(macroKey, current, target) {
    const textEl = document.getElementById(`dash-macro-${macroKey}-txt`);
    const barEl = document.getElementById(`dash-macro-${macroKey}-bar`);
    
    if(textEl) textEl.textContent = `${Math.round(current)}/${target}g`;
    if(barEl) {
        const pct = Math.min(100, (current / target) * 100);
        barEl.style.width = `${pct}%`;
    }
}

function setupChecklistListeners() {
    const chkSleep = document.getElementById('chk-sleep');
    if (chkSleep) {
        chkSleep.onchange = () => {
            appState.daily.checklist.sleep = chkSleep.checked;
            saveStateToStorage();
            if (chkSleep.checked) triggerConfetti();
            checkAndIncrementStreak();
        };
    }

    const chkDiet = document.getElementById('chk-diet');
    if(chkDiet) chkDiet.onclick = (e) => e.preventDefault();
    
    const chkWorkout = document.getElementById('chk-workout');
    if(chkWorkout) chkWorkout.onclick = (e) => e.preventDefault();
    
    const chkWater = document.getElementById('chk-water');
    if(chkWater) chkWater.onclick = (e) => e.preventDefault();
}

// ========================================================
// HIDRATAÇÃO (RASTREADOR DE ÁGUA)
// ========================================================
function addWater(amount) {
    if (!appState.plan) return;

    const waterTarget = appState.plan.water_target || Math.round(appState.plan.user.weight * 35);
    const oldWater = appState.daily.water;
    appState.daily.water += amount;
    
    // Efeito cascata / confetti ao bater meta
    if (oldWater < waterTarget && appState.daily.water >= waterTarget) {
        triggerConfetti();
        appState.daily.checklist.water = true;
        checkAndIncrementStreak();
    }

    saveStateToStorage();
    updateDashboardVisuals();
}

function resetWater() {
    appState.daily.water = 0;
    appState.daily.checklist.water = false;
    saveStateToStorage();
    updateDashboardVisuals();
}

// ========================================================
// GERADOR E AÇÕES DA ABA: DIETA
// ========================================================
function renderDietTab() {
    const mealsContainer = document.getElementById('meals-container');
    if(!mealsContainer) return;
    
    mealsContainer.innerHTML = '';

    appState.plan.diet_plan.forEach((meal, mealIdx) => {
        const isEaten = appState.daily.eatenMeals.includes(mealIdx);

        const card = document.createElement('div');
        card.className = 'meal-card';
        card.innerHTML = `
            <div class="meal-card-header">
                <div class="meal-title-group">
                    <h3>${meal.name}</h3>
                    <span class="meal-time"><i data-lucide="clock"></i> ${meal.time}</span>
                </div>
                <div class="meal-header-macros">
                    <span class="meal-header-cal">${meal.calories} kcal</span>
                    <span class="meal-header-macros-txt">P: ${meal.protein}g | C: ${meal.carbs}g | G: ${meal.fats}g</span>
                </div>
            </div>
            <div class="meal-card-body">
                <ul class="meal-food-items">
                    ${meal.items.map((item, itemIdx) => `
                        <li class="food-item">
                            <div>
                                <div class="food-item-name">${item.name}</div>
                                <span class="food-item-macros">P: ${item.prot}g | C: ${item.carb}g | G: ${item.fat}g</span>
                            </div>
                            <div style="display:flex;align-items:center;gap:10px;">
                                <div class="food-item-qty">${item.quantity} ${item.unit}</div>
                                <button class="btn btn-icon" onclick="openSwapModal(${mealIdx}, ${itemIdx})" style="padding:4px;color:var(--text-muted);"><i data-lucide="repeat"></i></button>
                            </div>
                        </li>
                    `).join('')}
                </ul>
                <div class="meal-track-box">
                    <label class="checkbox-container">
                        <input type="checkbox" class="chk-meal-eaten" data-idx="${mealIdx}" ${isEaten ? 'checked' : ''}>
                        <span class="checkmark"></span>
                        <span>Marcar como Consumida</span>
                    </label>
                </div>
            </div>
        `;
        mealsContainer.appendChild(card);
    });

    // Registrar eventos dos checkboxes de refeição
    const mealCheckboxes = document.querySelectorAll('.chk-meal-eaten');
    mealCheckboxes.forEach(chk => {
        chk.addEventListener('change', (e) => {
            const idx = parseInt(e.target.getAttribute('data-idx'));
            if (e.target.checked) {
                if (!appState.daily.eatenMeals.includes(idx)) {
                    appState.daily.eatenMeals.push(idx);
                }
            } else {
                appState.daily.eatenMeals = appState.daily.eatenMeals.filter(i => i !== idx);
            }
            
            saveStateToStorage();
            updateDashboardVisuals();
            
            // Efeito confete se todas refeições foram consumidas
            if (appState.daily.eatenMeals.length === appState.plan.diet_plan.length) {
                triggerConfetti();
                appState.daily.checklist.diet = true;
                checkAndIncrementStreak();
            }
        });
    });

    lucide.createIcons();
}

// ========================================================
// GERADOR E AÇÕES DA ABA: TREINO
// ========================================================
function renderWorkoutTab() {
    const dayButtons = document.querySelectorAll('.day-btn');
    if(!dayButtons.length) return;
    
    // Obter o dia da semana atual (0: Segunda, 6: Domingo)
    let todayIdx = new Date().getDay();
    let apiDayIdx = todayIdx === 0 ? 6 : todayIdx - 1; // Converter para Seg=0 ... Dom=6

    // Selecionar o dia do calendário
    dayButtons.forEach(btn => {
        const dayVal = parseInt(btn.getAttribute('data-day'));
        if (dayVal === apiDayIdx) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }

        btn.onclick = () => {
            dayButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderWorkoutDay(dayVal);
        };
    });

    // Renderizar o dia atual inicialmente
    renderWorkoutDay(apiDayIdx);
}

function renderWorkoutDay(dayIdx) {
    const plan = appState.plan;
    if(!plan.workout_plan) return;
    
    const workoutDay = plan.workout_plan[dayIdx];
    const exercisesContainer = document.getElementById('exercises-container');
    if(!exercisesContainer) return;
    
    const wDayName = document.getElementById('workout-day-name');
    if(wDayName) wDayName.textContent = workoutDay.title;

    // Limpar container
    exercisesContainer.innerHTML = '';

    if (!workoutDay.exercises || workoutDay.exercises.length === 0 || workoutDay.exercises[0].name === 'Repouso Absoluto' || workoutDay.exercises[0].name === 'Descanso') {
        exercisesContainer.innerHTML = `
            <div style="text-align: center; padding: 30px 10px; color: var(--text-secondary);">
                <i data-lucide="coffee" style="width: 48px; height: 48px; margin-bottom: 12px; color: var(--accent);"></i>
                <h4 style="font-family: var(--font-heading); font-size: 1.1rem; color: #fff; margin-bottom: 4px;">Dia de Recuperação</h4>
                <p style="font-size: 0.85rem;">Seu corpo cresce no descanso! Siga a alimentação e aproveite para recuperar as fibras musculares hoje.</p>
            </div>
        `;
        
        // Registrar conclusão automática de descanso
        appState.daily.checklist.workout = true;
        const cWork = document.getElementById('chk-workout');
        if(cWork) cWork.checked = true;
        saveStateToStorage();
        lucide.createIcons();
        return;
    }

    // Carregar exercícios concluídos para este dia
    const completedIdxs = appState.daily.completedExercises[dayIdx] || [];

    workoutDay.exercises.forEach((ex, exIdx) => {
        const isCompleted = completedIdxs.includes(exIdx);
        
        let restSecs = 60;
        if(ex.rest) {
            const m = String(ex.rest).match(/(\d+)/);
            if(m) restSecs = parseInt(m[1]);
        }

        const card = document.createElement('div');
        card.className = `exercise-card ${isCompleted ? 'completed' : ''}`;
        card.innerHTML = `
            <div class="exercise-card-header">
                <label class="checkbox-container" style="padding-left: 28px;">
                    <input type="checkbox" class="chk-exercise-done" data-day="${dayIdx}" data-idx="${exIdx}" ${isCompleted ? 'checked' : ''}>
                    <span class="checkmark"></span>
                </label>
                <div class="exercise-info">
                    <span class="exercise-target-badge">${ex.focus || ''}</span>
                    <h4 class="exercise-name">${ex.name}</h4>
                    <div class="exercise-meta">
                        <span><i data-lucide="layers"></i> ${ex.sets} séries</span>
                        <span><i data-lucide="hash"></i> ${ex.reps} reps</span>
                        <span><i data-lucide="clock"></i> ${ex.rest}</span>
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-icon" onclick="startRestTimer(${restSecs})" style="background: none; border: none; color: var(--accent); cursor: pointer; display: flex; align-items: center; padding: 4px;">
                        <i data-lucide="timer"></i>
                    </button>
                    <button class="btn-toggle-desc" onclick="toggleExerciseDesc(this)" style="background: none; border: none; color: white; cursor: pointer; display: flex; align-items: center; padding: 4px;">
                        <i data-lucide="chevron-down"></i>
                    </button>
                </div>
            </div>
            <div class="exercise-collapse">
                <strong>Instruções de Execução:</strong>
                <p style="margin-top: 4px;">${ex.notes || 'Sem instruções adicionais.'}</p>
            </div>
        `;
        exercisesContainer.appendChild(card);
    });

    // Configurar listeners para checkboxes de exercícios
    const exerciseCheckboxes = document.querySelectorAll('.chk-exercise-done');
    exerciseCheckboxes.forEach(chk => {
        chk.addEventListener('change', (e) => {
            const d = parseInt(e.target.getAttribute('data-day'));
            const idx = parseInt(e.target.getAttribute('data-idx'));
            const card = e.target.closest('.exercise-card');

            if (!appState.daily.completedExercises[d]) {
                appState.daily.completedExercises[d] = [];
            }

            if (e.target.checked) {
                card.classList.add('completed');
                if (!appState.daily.completedExercises[d].includes(idx)) {
                    appState.daily.completedExercises[d].push(idx);
                }
            } else {
                card.classList.remove('completed');
                appState.daily.completedExercises[d] = appState.daily.completedExercises[d].filter(i => i !== idx);
            }

            // Validar se completou o treino inteiro do dia selecionado
            const totalExercises = workoutDay.exercises.length;
            const completedCount = appState.daily.completedExercises[d].length;
            
            let todayIdx = new Date().getDay();
            let apiDayIdx = todayIdx === 0 ? 6 : todayIdx - 1;
            
            if (d === apiDayIdx) {
                appState.daily.checklist.workout = (completedCount === totalExercises);
            }

            saveStateToStorage();
            updateDashboardVisuals();

            // Confete por finalizar o treino completo
            if (completedCount === totalExercises && completedCount > 0) {
                triggerConfetti();
            }
        });
    });

    lucide.createIcons();
}

function toggleExerciseDesc(btn) {
    const card = btn.closest('.exercise-card');
    if(card) {
        card.classList.toggle('expanded');
    }
}

// ========================================================
// REST TIMER
// ========================================================
let restTimerInterval = null;

function startRestTimer(seconds) {
    const overlay = document.getElementById('rest-timer-overlay');
    const display = document.getElementById('rest-timer-display');
    if(!overlay || !display) return;
    
    overlay.classList.remove('hidden');
    overlay.style.display = 'flex';
    
    let left = seconds;
    display.textContent = formatTime(left);
    
    clearInterval(restTimerInterval);
    restTimerInterval = setInterval(() => {
        left--;
        if(left <= 0) {
            stopRestTimer();
            triggerConfetti();
        } else {
            display.textContent = formatTime(left);
        }
    }, 1000);
}

function stopRestTimer() {
    clearInterval(restTimerInterval);
    const overlay = document.getElementById('rest-timer-overlay');
    if(overlay) {
        overlay.classList.add('hidden');
        overlay.style.display = 'none';
    }
}

function formatTime(sec) {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
}

// ========================================================
// NAVEGAÇÃO DE ABAS
// ========================================================
function setupTabs() {
    const navItems = document.querySelectorAll('.bottom-nav .nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');

            // Atualizar botões de navegação
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Atualizar abas visíveis
            tabContents.forEach(tab => {
                const tabId = tab.getAttribute('id');
                if (tabId === `tab-${targetTab}`) {
                    tab.classList.add('active');
                } else {
                    tab.classList.remove('active');
                }
            });
        });
    });
}

// ========================================================
// MICRO-INTERAÇÕES: ANIMAÇÃO DE CONFETES
// ========================================================
function triggerConfetti() {
    if (typeof confetti === 'function') {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.8 },
            colors: ['#d2ff00', '#ffffff', '#20d3fe']
        });
    }
}

// ========================================================
// PHASE 2 FEATURES (Premium)
// ========================================================
function setupPhase2Features() {
    renderStreaks();
    renderChart();
    
    // PDF Export
    const btnPdf = document.getElementById('btn-export-pdf');
    if(btnPdf) {
        btnPdf.onclick = () => {
            const el = document.getElementById('main-screen');
            const opt = {
                margin:       10,
                filename:     'Plano_SHREDDED.pdf',
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2 },
                jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };
            html2pdf().set(opt).from(el).save();
        };
    }
    
    // Grocery List
    const btnGrocery = document.getElementById('btn-grocery-list');
    if(btnGrocery) {
        btnGrocery.onclick = openGroceryModal;
    }
    
    // Measurements
    const btnMeas = document.getElementById('btn-save-measurements');
    if(btnMeas) {
        btnMeas.onclick = saveMeasurements;
    }
    
    // Close Modals on click outside
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.onclick = (e) => {
            if(e.target === overlay) {
                overlay.style.display = 'none';
            }
        };
    });
}

function renderStreaks() {
    const badge = document.querySelector('.streak-badge');
    if(badge) {
        const streak = appState.streak || 0;
        badge.innerHTML = `Fogo 🔥 ${streak} dias`;
    }
}

function checkAndIncrementStreak() {
    const chk = appState.daily.checklist;
    if(chk.diet && chk.workout && chk.water && chk.sleep) {
        if(!appState.daily.streakIncremented) {
            appState.streak = (appState.streak || 0) + 1;
            appState.daily.streakIncremented = true;
            saveStateToStorage();
            renderStreaks();
            triggerConfetti();
            showToast('Parabéns! Você completou todas as missões do dia! 🔥', 'success');
        }
    }
}

function openGroceryModal() {
    const modal = document.getElementById('grocery-modal');
    const box = modal.querySelector('.modal-box');
    
    let groceryMap = {};
    
    appState.plan.diet_plan.forEach(meal => {
        meal.items.forEach(item => {
            if(!groceryMap[item.name]) {
                groceryMap[item.name] = { qty: 0, unit: item.unit };
            }
            groceryMap[item.name].qty += item.quantity * 7;
        });
    });
    
    let html = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
            <h2 style="font-family:var(--font-heading);">🛒 Lista de Compras (7 Dias)</h2>
            <button class="btn btn-icon" onclick="document.getElementById('grocery-modal').style.display='none'"><i data-lucide="x"></i></button>
        </div>
        <div style="max-height:60vh;overflow-y:auto;padding-right:10px;">
    `;
    
    for(let name in groceryMap) {
        const data = groceryMap[name];
        html += `
            <div class="grocery-item">
                <span style="font-weight:600;color:var(--text-primary);">${name}</span>
                <span style="color:var(--accent);">${Math.round(data.qty)} ${data.unit}</span>
            </div>
        `;
    }
    
    html += `</div>
        <button class="btn btn-primary btn-block" style="margin-top:20px;" onclick="document.getElementById('grocery-modal').style.display='none'">Fechar</button>
    `;
    
    box.innerHTML = html;
    lucide.createIcons();
    modal.style.display = 'flex';
}

function openSwapModal(mealIdx, itemIdx) {
    const meal = appState.plan.diet_plan[mealIdx];
    const item = meal.items[itemIdx];
    
    const modal = document.getElementById('swap-modal');
    const box = modal.querySelector('.modal-box');
    
    let swaps = [];
    if(item.carb > item.prot) {
        swaps = [
            { name: 'Batata Doce Cozida', mult: 1.5 },
            { name: 'Arroz Branco', mult: 1.0 },
            { name: 'Mandioca', mult: 1.2 }
        ];
    } else if(item.prot > item.fat) {
        swaps = [
            { name: 'Peito de Frango', mult: 1.0 },
            { name: 'Patinho', mult: 1.0 },
            { name: 'Tilápia', mult: 1.3 }
        ];
    } else {
        swaps = [
            { name: 'Abacate', mult: 1.5 },
            { name: 'Azeite', mult: 0.2 },
            { name: 'Pasta de Amendoim', mult: 0.3 }
        ];
    }
    
    let html = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
            <h2 style="font-family:var(--font-heading);">🔁 Substituir Alimento</h2>
            <button class="btn btn-icon" onclick="document.getElementById('swap-modal').style.display='none'"><i data-lucide="x"></i></button>
        </div>
        <p style="color:var(--text-secondary);margin-bottom:16px;">Trocando: <strong>${item.name}</strong></p>
        <div style="display:flex;flex-direction:column;gap:10px;">
    `;
    
    swaps.forEach((swap, i) => {
        if(swap.name !== item.name) {
            html += `
                <div class="grocery-item" style="cursor:pointer;" onclick="performSwap(${mealIdx}, ${itemIdx}, '${swap.name}', ${swap.mult})">
                    <span>${swap.name}</span>
                    <span style="color:var(--text-muted);font-size:0.8rem;">(Equivalente: ${Math.round(item.quantity * swap.mult)} ${item.unit})</span>
                </div>
            `;
        }
    });
    
    html += `</div>`;
    box.innerHTML = html;
    lucide.createIcons();
    modal.style.display = 'flex';
}

function performSwap(mealIdx, itemIdx, newName, multiplier) {
    const item = appState.plan.diet_plan[mealIdx].items[itemIdx];
    item.name = newName;
    item.quantity = Math.round(item.quantity * multiplier);
    saveStateToStorage();
    renderDietTab();
    document.getElementById('swap-modal').style.display = 'none';
    showToast('Alimento substituído com sucesso!', 'success');
}

function saveMeasurements() {
    const weight = parseFloat(document.getElementById('meas-weight').value);
    const arm = parseFloat(document.getElementById('meas-arm').value) || 0;
    const leg = parseFloat(document.getElementById('meas-leg').value) || 0;
    const hip = parseFloat(document.getElementById('meas-hip').value) || 0;
    const waist = parseFloat(document.getElementById('meas-waist').value) || 0;
    
    if(isNaN(weight)) {
        showToast('Peso é obrigatório!', 'error');
        return;
    }
    
    if(!appState.progressHistory) appState.progressHistory = [];
    
    appState.progressHistory.push({
        date: getTodayDateString(),
        weight, arm, leg, hip, waist
    });
    
    appState.plan.user.weight = weight;
    
    saveStateToStorage();
    showToast('Medidas salvas com sucesso!', 'success');
    
    renderApp();
    renderChart();
    
    if(authState.isLoggedIn && authState.email) {
        fetch('/api/user/save-plan', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                email: authState.email, 
                plan: appState.plan,
                progressHistory: appState.progressHistory,
                streak: appState.streak
            })
        });
    }
}

let weightChartInstance = null;
function renderChart() {
    const ctx = document.getElementById('weight-chart');
    if(!ctx) return;
    
    const history = appState.progressHistory || [];
    if(history.length === 0) return;
    
    const labels = history.map(h => h.date.substring(5)); // MM-DD
    const data = history.map(h => h.weight);
    
    if(weightChartInstance) {
        weightChartInstance.destroy();
    }
    
    weightChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Peso (kg)',
                data: data,
                borderColor: '#d2ff00',
                backgroundColor: 'rgba(210, 255, 0, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: '#242431' }, ticks: { color: '#9ea0ab' } },
                x: { grid: { display: false }, ticks: { color: '#9ea0ab' } }
            }
        }
    });
}
