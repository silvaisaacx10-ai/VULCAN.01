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

// Configurações do Círculo de Progresso
const CIRCLE_RADIUS = 70;
const CIRCLE_CIRCUMFERENCE = 2 * Math.PI * CIRCLE_RADIUS;

// DOM ELEMENTS
const onboardingScreen = document.getElementById('onboarding-screen');
const loadingScreen = document.getElementById('loading-screen');
const mainScreen = document.getElementById('main-screen');
const profileForm = document.getElementById('profile-form');
const loadingMessage = document.getElementById('loading-message');
const btnSubmitWizard = document.getElementById('btn-submit-wizard');
const btnResetPlan = document.getElementById('btn-reset-plan');

// INICIALIZAÇÃO DO APP
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar Lucide Icons
    lucide.createIcons();

    // Configurar o progresso do círculo
    const progressCircle = document.getElementById('calorie-progress-circle');
    if (progressCircle) {
        progressCircle.style.strokeDasharray = `${CIRCLE_CIRCUMFERENCE} ${CIRCLE_CIRCUMFERENCE}`;
        progressCircle.style.strokeDashoffset = CIRCLE_CIRCUMFERENCE;
    }

    // Carregar dados salvos
    loadSavedData();

    // Configurar navegação do Wizard
    setupWizard();

    // Configurar navegação entre abas
    setupTabs();

    // Configurar botões extras
    if (btnResetPlan) {
        btnResetPlan.addEventListener('click', resetAllData);
    }
});

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
        const pct = ((currentStepIdx + 1) / steps.length) * 100;
        progressFill.style.width = `${pct}%`;
    }

    nextButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const currentStep = steps[currentStepIdx];
            // Validar inputs do passo atual
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
    const gender = document.querySelector('input[name="gender"]:checked').value;
    const weight = parseFloat(document.getElementById('input-weight').value);
    const height = parseFloat(document.getElementById('input-height').value);
    const activity = document.getElementById('input-activity').value;
    const goal = document.querySelector('input[name="goal"]:checked').value;
    const dietPreference = document.querySelector('input[name="diet_preference"]:checked').value;

    // Transição de tela: Onboarding -> Loading
    onboardingScreen.classList.remove('active');
    loadingScreen.classList.add('active');

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
        loadingMessage.textContent = messages[msgIdx];
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
        loadingScreen.classList.remove('active');
        mainScreen.classList.add('active');

    } catch (err) {
        clearInterval(msgInterval);
        alert('Erro ao gerar plano. Por favor, verifique seus dados e tente novamente.');
        loadingScreen.classList.remove('active');
        onboardingScreen.classList.add('active');
    }
}

// ========================================================
// CONTROLE DE ESTADO E LOCAL STORAGE
// ========================================================
function loadSavedData() {
    const savedState = localStorage.getItem('shredded_app_state');
    if (savedState) {
        const parsed = JSON.parse(savedState);
        if (parsed && parsed.plan) {
            appState = parsed;

            // Verificar se o dia mudou para resetar trackers diários
            const today = getTodayDateString();
            if (appState.daily.date !== today) {
                appState.daily.date = today;
                appState.daily.water = 0;
                appState.daily.eatenMeals = [];
                appState.daily.completedExercises = {};
                appState.daily.checklist = {
                    diet: false,
                    workout: false,
                    water: false,
                    sleep: false
                };
                saveStateToStorage();
            }

            renderApp();
            onboardingScreen.classList.remove('active');
            mainScreen.classList.add('active');
        }
    }
}

function saveStateToStorage() {
    localStorage.setItem('shredded_app_state', JSON.stringify(appState));
}

function resetAllData() {
    if (confirm('Tem certeza que deseja apagar seus dados e gerar um novo plano?')) {
        localStorage.removeItem('shredded_app_state');
        location.reload();
    }
}

function getTodayDateString() {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

// ========================================================
// RENDERIZADOR COMPLETO DA INTERFACE (MAIN SCREEN)
// ========================================================
function renderApp() {
    if (!appState.plan) return;

    const plan = appState.plan;

    // 1. Atualizar Textos Gerais
    document.getElementById('display-user-name').textContent = plan.user.name;
    document.getElementById('profile-user-name').textContent = plan.user.name;
    
    let goalText = "Objetivo: Manutenção / Definição";
    if (plan.user.goal === 'lose') goalText = "Foco: Perda de Peso / Definição";
    else if (plan.user.goal === 'gain') goalText = "Foco: Ganho de Massa / Hipertrofia";
    
    document.getElementById('profile-user-goal').textContent = goalText;
    document.getElementById('workout-goal-desc').textContent = goalText + ` (${plan.user.diet_preference.toUpperCase()})`;

    // 2. Renderizar Estatísticas de Perfil
    document.getElementById('prof-weight').textContent = `${plan.user.weight} kg`;
    document.getElementById('prof-height').textContent = `${plan.user.height} cm`;
    document.getElementById('prof-bmr').textContent = `${plan.nutrition.bmr} kcal`;
    document.getElementById('prof-tdee').textContent = `${plan.nutrition.tdee} kcal`;

    // 3. Atualizar Alvos do Dashboard
    document.getElementById('dash-calories-target').textContent = plan.nutrition.target_calories;
    document.getElementById('diet-pill-cal').textContent = plan.nutrition.target_calories;
    document.getElementById('diet-pill-prot').textContent = plan.nutrition.protein;
    document.getElementById('diet-pill-carb').textContent = plan.nutrition.carbs;
    document.getElementById('diet-pill-fat').textContent = plan.nutrition.fats;

    // Meta de água padrão com base no peso (35ml por kg)
    const waterTarget = Math.round(plan.user.weight * 35);
    document.getElementById('water-target-val').textContent = waterTarget;

    // 4. Renderizar Abas de Dieta e Treino
    renderDietTab();
    renderWorkoutTab();

    // 5. Atualizar Dashboard (Calorias, Macros, Água, Checklist)
    updateDashboardVisuals();
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
    document.getElementById('dash-calories-eaten').textContent = Math.round(eatenCal);

    // Atualizar progress ring SVG
    const progressCircle = document.getElementById('calorie-progress-circle');
    const pctCal = Math.min(1.0, eatenCal / nutrition.target_calories);
    const offset = CIRCLE_CIRCUMFERENCE - (pctCal * CIRCLE_CIRCUMFERENCE);
    progressCircle.style.strokeDashoffset = offset;

    // Mudar cor do círculo caso ultrapasse as calorias
    if (eatenCal > nutrition.target_calories && appState.plan.user.goal === 'lose') {
        progressCircle.style.stroke = '#ff4757'; // Vermelho se furar a dieta de corte
    } else {
        progressCircle.style.stroke = '#d2ff00'; // Volt Neon
    }

    // Atualizar barras de macros
    updateMacroBar('protein', eatenProt, nutrition.protein);
    updateMacroBar('carbs', eatenCarb, nutrition.carbs);
    updateMacroBar('fats', eatenFat, nutrition.fats);

    // Atualizar visualizador de Água
    const waterTarget = Math.round(appState.plan.user.weight * 35);
    document.getElementById('water-amount-txt').textContent = `${appState.daily.water} ml`;
    const waterPct = Math.min(100, (appState.daily.water / waterTarget) * 100);
    document.getElementById('water-wave').style.bottom = `calc(${waterPct}% - 100px)`;

    // Se bateu meta de água, marca na checklist
    appState.daily.checklist.water = (appState.daily.water >= waterTarget);
    document.getElementById('chk-water').checked = appState.daily.checklist.water;

    // Se seguiu toda a dieta, marca
    appState.daily.checklist.diet = (appState.daily.eatenMeals.length === meals.length);
    document.getElementById('chk-diet').checked = appState.daily.checklist.diet;

    // Atualizar Checkboxes da Checklist Diária
    document.getElementById('chk-workout').checked = appState.daily.checklist.workout;
    document.getElementById('chk-sleep').checked = appState.daily.checklist.sleep;

    // Ouvintes para salvar cliques da Checklist do Dashboard
    setupChecklistListeners();
}

function updateMacroBar(macroKey, current, target) {
    const textEl = document.getElementById(`dash-macro-${macroKey}-txt`);
    const barEl = document.getElementById(`dash-macro-${macroKey}-bar`);
    
    textEl.textContent = `${Math.round(current)}/${target}g`;
    const pct = Math.min(100, (current / target) * 100);
    barEl.style.width = `${pct}%`;
}

function setupChecklistListeners() {
    const chkSleep = document.getElementById('chk-sleep');
    chkSleep.onchange = () => {
        appState.daily.checklist.sleep = chkSleep.checked;
        saveStateToStorage();
        if (chkSleep.checked) triggerConfetti();
    };

    // Os outros checkboxes (água, dieta, treino) são controlados pelas ações das respectivas abas,
    // mas deixamos eles visuais no dashboard
    const chkDiet = document.getElementById('chk-diet');
    const chkWorkout = document.getElementById('chk-workout');
    const chkWater = document.getElementById('chk-water');
    
    chkDiet.onclick = (e) => e.preventDefault();
    chkWorkout.onclick = (e) => e.preventDefault();
    chkWater.onclick = (e) => e.preventDefault();
}

// ========================================================
// HIDRATAÇÃO (RASTREADOR DE ÁGUA)
// ========================================================
function addWater(amount) {
    if (!appState.plan) return;

    const waterTarget = Math.round(appState.plan.user.weight * 35);
    const oldWater = appState.daily.water;
    appState.daily.water += amount;
    
    // Efeito cascata / confetti ao bater meta
    if (oldWater < waterTarget && appState.daily.water >= waterTarget) {
        triggerConfetti();
        appState.daily.checklist.water = true;
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
                    ${meal.items.map(item => `
                        <li class="food-item">
                            <div>
                                <div class="food-item-name">${item.name}</div>
                                <span class="food-item-macros">P: ${item.prot}g | C: ${item.carb}g | G: ${item.fat}g</span>
                            </div>
                            <div class="food-item-qty">${item.quantity} ${item.unit}</div>
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
    
    // Obter o dia da semana atual (0: Segunda, 6: Domingo)
    // Javascript standard: 0 = Domingo, 1 = Segunda, etc.
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
    const workoutDay = plan.workout_plan[dayIdx];
    const exercisesContainer = document.getElementById('exercises-container');
    
    document.getElementById('workout-day-name').textContent = workoutDay.title;

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
        document.getElementById('chk-workout').checked = true;
        saveStateToStorage();
        lucide.createIcons();
        return;
    }

    // Carregar exercícios concluídos para este dia
    const completedIdxs = appState.daily.completedExercises[dayIdx] || [];

    workoutDay.exercises.forEach((ex, exIdx) => {
        const isCompleted = completedIdxs.includes(exIdx);

        const card = document.createElement('div');
        card.className = `exercise-card ${isCompleted ? 'completed' : ''}`;
        card.innerHTML = `
            <div class="exercise-card-header">
                <label class="checkbox-container" style="padding-left: 28px;">
                    <input type="checkbox" class="chk-exercise-done" data-day="${dayIdx}" data-idx="${exIdx}" ${isCompleted ? 'checked' : ''}>
                    <span class="checkmark"></span>
                </label>
                <div class="exercise-info">
                    <span class="exercise-target-badge">${ex.focus}</span>
                    <h4 class="exercise-name">${ex.name}</h4>
                    <div class="exercise-meta">
                        <span><i data-lucide="layers"></i> ${ex.sets} séries</span>
                        <span><i data-lucide="hash"></i> ${ex.reps} reps</span>
                        <span><i data-lucide="clock"></i> ${ex.rest}</span>
                    </div>
                </div>
                <button class="btn-toggle-desc" onclick="toggleExerciseDesc(this)">
                    <i data-lucide="chevron-down"></i>
                </button>
            </div>
            <div class="exercise-collapse">
                <strong>Instruções de Execução:</strong>
                <p style="margin-top: 4px;">${ex.notes}</p>
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
            
            // Só marcamos o treino na checklist se concluímos todos os exercícios de hoje (dia físico real)
            let todayIdx = new Date().getDay();
            let apiDayIdx = todayIdx === 0 ? 6 : todayIdx - 1;
            
            if (d === apiDayIdx) {
                appState.daily.checklist.workout = (completedCount === totalExercises);
            }

            saveStateToStorage();
            updateDashboardVisuals();

            // Confete por finalizar o treino completo
            if (completedCount === totalExercises) {
                triggerConfetti();
            }
        });
    });

    lucide.createIcons();
}

function toggleExerciseDesc(btn) {
    const card = btn.closest('.exercise-card');
    card.classList.toggle('expanded');
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
