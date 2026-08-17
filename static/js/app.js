document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons
    lucide.createIcons();

    // Elements
    const loginScreen = document.getElementById('login-screen');
    const onboardingScreen = document.getElementById('onboarding-screen');
    const dashboardScreen = document.getElementById('dashboard-screen');
    
    // Navigation & Views
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');
    const viewTitle = document.getElementById('view-title');
    
    // Check if user is already logged in (mock logic for demo, typically check token)
    let currentUser = null;
    let currentPlan = null;

    
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
                document.getElementById('login-screen').classList.add('hidden');
                
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
                        document.getElementById('dashboard-screen').classList.remove('hidden');
                        document.getElementById('dashboard-screen').classList.add('active');
                        renderDashboard();
                        startBlockPolling();
                        return;
                    }
                }
                
                // If no plan, show onboarding
                document.getElementById('onboarding-screen').classList.remove('hidden');
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


    // --- Onboarding Logic ---
    const nextBtns = document.querySelectorAll('.next-step');
    const prevBtns = document.querySelectorAll('.prev-step');
    const steps = document.querySelectorAll('.onboarding-step');

    nextBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const nextStepId = btn.getAttribute('data-next');
            switchStep(nextStepId);
        });
    });

    prevBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const prevStepId = btn.getAttribute('data-prev');
            switchStep(prevStepId);
        });
    });

    function switchStep(targetId) {
        steps.forEach(step => {
            if (step.id === targetId) {
                step.classList.remove('hidden');
                step.classList.add('active');
            } else {
                step.classList.add('hidden');
                step.classList.remove('active');
            }
        });
    }

    // Card Selection Logic
    function setupCardSelector(containerId, inputId) {
        const container = document.getElementById(containerId);
        const cards = container.querySelectorAll('.selection-card');
        const hiddenInput = document.getElementById(inputId);

        cards.forEach(card => {
            card.addEventListener('click', () => {
                cards.forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                hiddenInput.value = card.getAttribute('data-value');
            });
        });
    }

    setupCardSelector('goal-selector', 'user-goal');
    setupCardSelector('diet-selector', 'user-diet');

    // Generate Plan
    const onboardingForm = document.getElementById('onboarding-form');
    onboardingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const age = document.getElementById('user-age').value;
        const weight = document.getElementById('user-weight').value;
        const height = document.getElementById('user-height').value;
        const goal = document.getElementById('user-goal').value;
        const diet = document.getElementById('user-diet').value;

        if (!goal || !diet) {
            alert('Por favor, selecione seu objetivo e dieta.');
            return;
        }

        const payload = { age, weight, height, goal, diet };
        
        // Show loading
        document.getElementById('loading-overlay').classList.remove('hidden');

        try {
            const res = await fetch('/api/generate-plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            let planData;
            if (res.ok) {
                planData = await res.json();
                
                // Save plan
                await fetch('/api/user/save-plan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ plan: planData })
                });

            } else {
                // Mock fallback for UI demonstration
                planData = mockGeneratePlan(payload);
            }

            currentPlan = planData;
            
            // Set Profile Data
            document.getElementById('profile-age').textContent = `${age} anos`;
            document.getElementById('profile-weight').textContent = `${weight} kg`;
            document.getElementById('profile-height').textContent = `${height} cm`;
            document.getElementById('profile-diet-badge').textContent = `Dieta: ${diet} - ${goal}`;
            
            setTimeout(() => {
                document.getElementById('loading-overlay').classList.add('hidden');
                onboardingScreen.classList.remove('active');
                onboardingScreen.classList.add('hidden');
                dashboardScreen.classList.add('active');
                renderDashboard();
            }, 1500);

        } catch (error) {
            console.error("Plan generation error", error);
            document.getElementById('loading-overlay').classList.add('hidden');
        }
    });

    // --- Dashboard Navigation ---
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const target = item.getAttribute('data-target');
            
            // Update nav active state
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            
            // Update title
            viewTitle.textContent = item.textContent.trim();

            // Switch view
            views.forEach(view => {
                if (view.id === target) {
                    view.classList.remove('hidden');
                    view.classList.add('active');
                } else {
                    view.classList.add('hidden');
                    view.classList.remove('active');
                }
            });
        });
    });

    // --- Logout ---
    document.getElementById('btn-logout').addEventListener('click', () => {
        dashboardScreen.classList.remove('active');
        dashboardScreen.classList.add('hidden');
        loginScreen.classList.add('active');
        loginForm.reset();
    });

    // --- Avatar Upload ---
    document.getElementById('avatar-input').addEventListener('change', function(e) {
        if (e.target.files && e.target.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const url = e.target.result;
                const imgStr = `<img src="${url}" alt="Avatar">`;
                document.getElementById('avatar-preview').innerHTML = imgStr;
                document.getElementById('header-avatar').innerHTML = imgStr;
            }
            reader.readAsDataURL(e.target.files[0]);
        }
    });

    // --- Recalculate ---
    document.getElementById('btn-recalculate').addEventListener('click', () => {
        dashboardScreen.classList.remove('active');
        dashboardScreen.classList.add('hidden');
        onboardingScreen.classList.remove('hidden');
        onboardingScreen.classList.add('active');
        switchStep('step-1');
    });

    // --- Render Functions ---
    function renderDashboard() {
        if (!currentPlan) return;

        // Overview
        document.getElementById('overview-calories').textContent = `${currentPlan.calories || 2500} kcal`;
        document.getElementById('overview-goal').textContent = currentPlan.goal || 'Manutenção';

        // Diet
        const mealsContainer = document.getElementById('meals-container');
        mealsContainer.innerHTML = '';
        if (currentPlan.meals) {
            currentPlan.meals.forEach((meal, mIndex) => {
                let itemsHtml = '';
                meal.items.forEach((item, iIndex) => {
                    itemsHtml += `
                        <div class="food-item">
                            <span>${item.amount} ${item.name}</span>
                            <button class="btn-secondary btn-small" onclick="swapFood('${meal.type}', ${mIndex}, ${iIndex})">
                                <i data-lucide="refresh-cw"></i> Trocar
                            </button>
                        </div>
                    `;
                });

                mealsContainer.innerHTML += `
                    <div class="meal-card">
                        <div class="meal-header">
                            <div class="meal-title"><i data-lucide="coffee"></i> ${meal.type}</div>
                        </div>
                        <div class="meal-items">${itemsHtml}</div>
                    </div>
                `;
            });
        }

        // Workouts
        const workoutsContainer = document.getElementById('workouts-container');
        workoutsContainer.innerHTML = '';
        if (currentPlan.workouts) {
            currentPlan.workouts.forEach(workout => {
                let exHtml = '';
                workout.exercises.forEach(ex => {
                    exHtml += `
                        <div class="exercise-item">
                            <span>${ex.name}</span>
                            <span class="text-muted">${ex.sets}x${ex.reps}</span>
                        </div>
                    `;
                });

                workoutsContainer.innerHTML += `
                    <div class="workout-card">
                        <div class="workout-header-inner">
                            <div class="workout-title"><i data-lucide="dumbbell"></i> ${workout.day} - ${workout.group}</div>
                        </div>
                        <div class="exercise-items">${exHtml}</div>
                    </div>
                `;
            });
        }

        lucide.createIcons();
    }

    // --- Food Swapping Logic ---
    window.swapFood = function(mealType, mealIndex, itemIndex) {
        if (!currentPlan) return;
        
        const item = currentPlan.meals[mealIndex].items[itemIndex];
        let newOption = "";

        // Intelligent Swap Logic
        const isBreakfastOrSnack = mealType.toLowerCase().includes('manhã') || mealType.toLowerCase().includes('lanche');

        if (isBreakfastOrSnack) {
            const options = ["Ovos Mexidos", "Whey Protein", "Iogurte Natural", "Queijo Branco"];
            newOption = options[Math.floor(Math.random() * options.length)];
        } else {
            const options = ["Frango Grelhado", "Patinho Moído", "Tilápia", "Tofu"];
            newOption = options[Math.floor(Math.random() * options.length)];
        }

        currentPlan.meals[mealIndex].items[itemIndex].name = newOption;
        
        // Re-render
        renderDashboard();

        // Update Backend
        fetch('/api/user/update-progress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'food_swap', plan: currentPlan })
        }).catch(err => console.error("Update failed", err));
    };

    // --- Mock Data Generator (Fallback) ---
    function mockGeneratePlan(data) {
        return {
            goal: data.goal,
            calories: 2200,
            meals: [
                {
                    type: "Café da Manhã",
                    items: [{amount: "2 un.", name: "Ovos Mexidos"}, {amount: "30g", name: "Aveia"}]
                },
                {
                    type: "Almoço",
                    items: [{amount: "150g", name: "Frango Grelhado"}, {amount: "100g", name: "Arroz Integral"}]
                },
                {
                    type: "Lanche",
                    items: [{amount: "1 dose", name: "Whey Protein"}]
                },
                {
                    type: "Jantar",
                    items: [{amount: "150g", name: "Patinho Moído"}, {amount: "100g", name: "Batata Doce"}]
                }
            ],
            workouts: [
                { day: "Segunda", group: "Peito e Tríceps", exercises: [{name: "Supino Reto", sets: 4, reps: 10}, {name: "Tríceps Polia", sets: 3, reps: 12}] },
                { day: "Terça", group: "Costas e Bíceps", exercises: [{name: "Puxada Frontal", sets: 4, reps: 10}, {name: "Rosca Direta", sets: 3, reps: 12}] }
            ]
        };
    }
});
