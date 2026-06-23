import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configurações do App
app.config['SECRET_KEY'] = 'gym-aesthetic-secret-key-12345'

# Banco de dados de Alimentos Base para dimensionamento dinâmico
FOOD_TEMPLATES = {
    'standard': {
        'cafe_da_manha': [
            {'name': 'Ovos inteiros mexidos/cozidos', 'base_qty': 2, 'unit': 'unidades', 'prot_per_unit': 6, 'carb_per_unit': 0.6, 'fat_per_unit': 5, 'base_cal': 70},
            {'name': 'Pão de forma integral', 'base_qty': 50, 'unit': 'g', 'prot_per_unit': 0.08, 'carb_per_unit': 0.45, 'fat_per_unit': 0.015, 'base_cal': 2.3},
            {'name': 'Fruta (Mamão ou Banana)', 'base_qty': 120, 'unit': 'g', 'prot_per_unit': 0.006, 'carb_per_unit': 0.15, 'fat_per_unit': 0.001, 'base_cal': 0.6}
        ],
        'almoco': [
            {'name': 'Peito de frango grelhado', 'base_qty': 120, 'unit': 'g', 'prot_per_unit': 0.31, 'carb_per_unit': 0, 'fat_per_unit': 0.036, 'base_cal': 1.65},
            {'name': 'Arroz integral cozido', 'base_qty': 150, 'unit': 'g', 'prot_per_unit': 0.026, 'carb_per_unit': 0.25, 'fat_per_unit': 0.01, 'base_cal': 1.2},
            {'name': 'Feijão carioca cozido', 'base_qty': 100, 'unit': 'g', 'prot_per_unit': 0.05, 'carb_per_unit': 0.14, 'fat_per_unit': 0.005, 'base_cal': 0.8},
            {'name': 'Salada de folhas verdes e tomate', 'base_qty': 1, 'unit': 'prato cheio', 'prot_per_unit': 1, 'carb_per_unit': 3, 'fat_per_unit': 0, 'base_cal': 15},
            {'name': 'Azeite de oliva extra virgem', 'base_qty': 8, 'unit': 'ml', 'prot_per_unit': 0, 'carb_per_unit': 0, 'fat_per_unit': 0.92, 'base_cal': 8.3}
        ],
        'lanche_da_tarde': [
            {'name': 'Whey Protein (Concentrado/Isolado)', 'base_qty': 30, 'unit': 'g', 'prot_per_unit': 0.8, 'carb_per_unit': 0.1, 'fat_per_unit': 0.06, 'base_cal': 4.1},
            {'name': 'Aveia em flocos', 'base_qty': 30, 'unit': 'g', 'prot_per_unit': 0.14, 'carb_per_unit': 0.6, 'fat_per_unit': 0.07, 'base_cal': 3.6},
            {'name': 'Iogurte natural desnatado', 'base_qty': 150, 'unit': 'g', 'prot_per_unit': 0.04, 'carb_per_unit': 0.05, 'fat_per_unit': 0.002, 'base_cal': 0.4}
        ],
        'jantar': [
            {'name': 'Patinho bovino grelhado ou filé de peixe', 'base_qty': 120, 'unit': 'g', 'prot_per_unit': 0.28, 'carb_per_unit': 0, 'fat_per_unit': 0.07, 'base_cal': 1.8},
            {'name': 'Batata doce cozida ou mandioca', 'base_qty': 120, 'unit': 'g', 'prot_per_unit': 0.015, 'carb_per_unit': 0.2, 'fat_per_unit': 0.001, 'base_cal': 0.86},
            {'name': 'Vegetais cozidos (Brócolis, Cenoura)', 'base_qty': 100, 'unit': 'g', 'prot_per_unit': 0.02, 'carb_per_unit': 0.07, 'fat_per_unit': 0.002, 'base_cal': 0.4}
        ]
    },
    'vegetarian': {
        'cafe_da_manha': [
            {'name': 'Ovos inteiros mexidos/cozidos', 'base_qty': 2, 'unit': 'unidades', 'prot_per_unit': 6, 'carb_per_unit': 0.6, 'fat_per_unit': 5, 'base_cal': 70},
            {'name': 'Pão de forma integral', 'base_qty': 50, 'unit': 'g', 'prot_per_unit': 0.08, 'carb_per_unit': 0.45, 'fat_per_unit': 0.015, 'base_cal': 2.3},
            {'name': 'Queijo branco cottage', 'base_qty': 60, 'unit': 'g', 'prot_per_unit': 0.11, 'carb_per_unit': 0.03, 'fat_per_unit': 0.04, 'base_cal': 1.0}
        ],
        'almoco': [
            {'name': 'Tofu grelhado ou Hambúrguer de Lentilha', 'base_qty': 150, 'unit': 'g', 'prot_per_unit': 0.15, 'carb_per_unit': 0.05, 'fat_per_unit': 0.08, 'base_cal': 1.5},
            {'name': 'Arroz integral cozido', 'base_qty': 150, 'unit': 'g', 'prot_per_unit': 0.026, 'carb_per_unit': 0.25, 'fat_per_unit': 0.01, 'base_cal': 1.2},
            {'name': 'Feijão preto cozido', 'base_qty': 120, 'unit': 'g', 'prot_per_unit': 0.05, 'carb_per_unit': 0.14, 'fat_per_unit': 0.005, 'base_cal': 0.8},
            {'name': 'Salada verde com sementes de abóbora', 'base_qty': 1, 'unit': 'prato', 'prot_per_unit': 2, 'carb_per_unit': 4, 'fat_per_unit': 3, 'base_cal': 50},
            {'name': 'Azeite de oliva', 'base_qty': 8, 'unit': 'ml', 'prot_per_unit': 0, 'carb_per_unit': 0, 'fat_per_unit': 0.92, 'base_cal': 8.3}
        ],
        'lanche_da_tarde': [
            {'name': 'Proteína vegetal em pó (Ervilha/Arroz)', 'base_qty': 30, 'unit': 'g', 'prot_per_unit': 0.75, 'carb_per_unit': 0.1, 'fat_per_unit': 0.05, 'base_cal': 3.9},
            {'name': 'Banana prata', 'base_qty': 1, 'unit': 'unidade', 'prot_per_unit': 1.3, 'carb_per_unit': 23, 'fat_per_unit': 0.3, 'base_cal': 90},
            {'name': 'Pasta de amendoim integral', 'base_qty': 15, 'unit': 'g', 'prot_per_unit': 0.25, 'carb_per_unit': 0.15, 'fat_per_unit': 0.5, 'base_cal': 5.9}
        ],
        'jantar': [
            {'name': 'Omelete de 3 claras e 1 ovo inteiro', 'base_qty': 1, 'unit': 'unidade', 'prot_per_unit': 18, 'carb_per_unit': 1.5, 'fat_per_unit': 6, 'base_cal': 140},
            {'name': 'Batata doce ou Mandioca grelhada', 'base_qty': 120, 'unit': 'g', 'prot_per_unit': 0.015, 'carb_per_unit': 0.2, 'fat_per_unit': 0.001, 'base_cal': 0.86},
            {'name': 'Mix de legumes (Brócolis, Couve-Flor)', 'base_qty': 150, 'unit': 'g', 'prot_per_unit': 0.03, 'carb_per_unit': 0.08, 'fat_per_unit': 0.002, 'base_cal': 0.45}
        ]
    },
    'vegan': {
        'cafe_da_manha': [
            {'name': 'Tofu Mexido com cúrcuma e sal negro', 'base_qty': 120, 'unit': 'g', 'prot_per_unit': 0.12, 'carb_per_unit': 0.02, 'fat_per_unit': 0.06, 'base_cal': 1.1},
            {'name': 'Pão de fermentação natural (Sourdough)', 'base_qty': 60, 'unit': 'g', 'prot_per_unit': 0.08, 'carb_per_unit': 0.5, 'fat_per_unit': 0.01, 'base_cal': 2.4},
            {'name': 'Abacate (Avocado)', 'base_qty': 50, 'unit': 'g', 'prot_per_unit': 0.01, 'carb_per_unit': 0.08, 'fat_per_unit': 0.15, 'base_cal': 1.6}
        ],
        'almoco': [
            {'name': 'Tempeh grelhado ou Hambúrguer de Grão de Bico', 'base_qty': 120, 'unit': 'g', 'prot_per_unit': 0.19, 'carb_per_unit': 0.09, 'fat_per_unit': 0.11, 'base_cal': 2.0},
            {'name': 'Arroz integral ou Quinoa cozida', 'base_qty': 150, 'unit': 'g', 'prot_per_unit': 0.04, 'carb_per_unit': 0.23, 'fat_per_unit': 0.02, 'base_cal': 1.3},
            {'name': 'Lentilha cozida', 'base_qty': 100, 'unit': 'g', 'prot_per_unit': 0.06, 'carb_per_unit': 0.15, 'fat_per_unit': 0.005, 'base_cal': 0.9},
            {'name': 'Salada de folhas verdes e brócolis picado', 'base_qty': 1, 'unit': 'prato', 'prot_per_unit': 2, 'carb_per_unit': 4, 'fat_per_unit': 0, 'base_cal': 25},
            {'name': 'Sementes de girassol tostadas', 'base_qty': 10, 'unit': 'g', 'prot_per_unit': 0.2, 'carb_per_unit': 0.2, 'fat_per_unit': 0.5, 'base_cal': 5.8}
        ],
        'lanche_da_tarde': [
            {'name': 'Proteína vegana isolada (Ervilha/Arroz)', 'base_qty': 30, 'unit': 'g', 'prot_per_unit': 0.75, 'carb_per_unit': 0.1, 'fat_per_unit': 0.05, 'base_cal': 3.9},
            {'name': 'Aveia em flocos finos', 'base_qty': 30, 'unit': 'g', 'prot_per_unit': 0.14, 'carb_per_unit': 0.6, 'fat_per_unit': 0.07, 'base_cal': 3.6},
            {'name': 'Castanhas de Caju', 'base_qty': 15, 'unit': 'g', 'prot_per_unit': 0.18, 'carb_per_unit': 0.3, 'fat_per_unit': 0.44, 'base_cal': 5.5}
        ],
        'jantar': [
            {'name': 'Proteína Texturizada de Soja (PTS) refogada', 'base_qty': 80, 'unit': 'g', 'prot_per_unit': 0.45, 'carb_per_unit': 0.25, 'fat_per_unit': 0.01, 'base_cal': 2.9},
            {'name': 'Batata cozida com casca ou Abóbora cabotiá', 'base_qty': 150, 'unit': 'g', 'prot_per_unit': 0.02, 'carb_per_unit': 0.15, 'fat_per_unit': 0.001, 'base_cal': 0.7},
            {'name': 'Salada de repolho, cenoura e gergelim', 'base_qty': 1, 'unit': 'prato', 'prot_per_unit': 1.5, 'carb_per_unit': 5, 'fat_per_unit': 2, 'base_cal': 40}
        ]
    },
    'low_carb': {
        'cafe_da_manha': [
            {'name': 'Ovos mexidos na manteiga', 'base_qty': 3, 'unit': 'unidades', 'prot_per_unit': 6, 'carb_per_unit': 0.6, 'fat_per_unit': 6.5, 'base_cal': 85},
            {'name': 'Bacon grelhado', 'base_qty': 20, 'unit': 'g', 'prot_per_unit': 0.37, 'carb_per_unit': 0.01, 'fat_per_unit': 0.42, 'base_cal': 5.4},
            {'name': 'Morangos frescos', 'base_qty': 80, 'unit': 'g', 'prot_per_unit': 0.007, 'carb_per_unit': 0.07, 'fat_per_unit': 0.003, 'base_cal': 0.32}
        ],
        'almoco': [
            {'name': 'Corte bovino gordo (Contrafilé/Picanha) ou Coxa de Frango', 'base_qty': 150, 'unit': 'g', 'prot_per_unit': 0.26, 'carb_per_unit': 0, 'fat_per_unit': 0.15, 'base_cal': 2.4},
            {'name': 'Arroz de couve-flor refogado', 'base_qty': 150, 'unit': 'g', 'prot_per_unit': 0.02, 'carb_per_unit': 0.04, 'fat_per_unit': 0.01, 'base_cal': 0.3},
            {'name': 'Salada verde (Rúcula, Agrião) com queijo parmesão', 'base_qty': 1, 'unit': 'prato', 'prot_per_unit': 4, 'carb_per_unit': 1, 'fat_per_unit': 6, 'base_cal': 75},
            {'name': 'Azeite de oliva extra virgem', 'base_qty': 10, 'unit': 'ml', 'prot_per_unit': 0, 'carb_per_unit': 0, 'fat_per_unit': 0.92, 'base_cal': 8.3}
        ],
        'lanche_da_tarde': [
            {'name': 'Whey Protein Isolado batido com água', 'base_qty': 30, 'unit': 'g', 'prot_per_unit': 0.85, 'carb_per_unit': 0.02, 'fat_per_unit': 0.01, 'base_cal': 3.6},
            {'name': 'Mix de Oleaginosas (Amêndoas/Nozes)', 'base_qty': 25, 'unit': 'g', 'prot_per_unit': 0.18, 'carb_per_unit': 0.16, 'fat_per_unit': 0.52, 'base_cal': 6.0}
        ],
        'jantar': [
            {'name': 'Filé de Salmão ou Sobrecoxa de Frango grelhada', 'base_qty': 150, 'unit': 'g', 'prot_per_unit': 0.22, 'carb_per_unit': 0, 'fat_per_unit': 0.12, 'base_cal': 2.0},
            {'name': 'Abobrinha e Brócolis grelhados na manteiga', 'base_qty': 150, 'unit': 'g', 'prot_per_unit': 0.02, 'carb_per_unit': 0.05, 'fat_per_unit': 0.04, 'base_cal': 0.6}
        ]
    }
}

# Exercícios por tipo de treino e grupo muscular
EXERCISES_DATABASE = {
    'push': [
        {'name': 'Supino Reto com Barra', 'focus': 'Peito Integral', 'rest': '90s', 'description': 'Deitado no banco, descer a barra até o peito e empurrar com força.'},
        {'name': 'Supino Inclinado com Halteres', 'focus': 'Peito Superior', 'rest': '90s', 'description': 'Banco inclinado a 30°, focar na contração do peito superior.'},
        {'name': 'Desenvolvimento Militar com Halteres', 'focus': 'Ombros Anterior', 'rest': '90s', 'description': 'Sentado ou em pé, empurrar os halteres verticalmente.'},
        {'name': 'Elevação Lateral com Halteres', 'focus': 'Ombros Lateral', 'rest': '60s', 'description': 'Elevar os halteres lateralmente até a linha dos ombros, mantendo o cotovelo levemente flexionado.'},
        {'name': 'Tríceps na Polia com Barra Reta', 'focus': 'Tríceps', 'rest': '60s', 'description': 'Estender completamente os braços na polia, mantendo os cotovelos fixos ao lado do corpo.'},
        {'name': 'Tríceps Testa com Halteres', 'focus': 'Tríceps Cabeça Longa', 'rest': '75s', 'description': 'Deitado, flexionar os cotovelos trazendo os halteres ao lado da testa.'}
    ],
    'pull': [
        {'name': 'Puxada Aberta na Polia Alta', 'focus': 'Dorsais (Costas)', 'rest': '90s', 'description': 'Puxar a barra em direção ao peitoral superior, contraindo as escápulas.'},
        {'name': 'Remada Curvada com Barra (Pronada)', 'focus': 'Costas Espessura', 'rest': '90s', 'description': 'Tronco inclinado, puxar a barra na altura do umbigo mantendo a coluna ereta.'},
        {'name': 'Remada Baixa Triângulo', 'focus': 'Costas Centro/Lombar', 'rest': '75s', 'description': 'Sentado na máquina de remada, puxar o triângulo rente ao abdômen.'},
        {'name': 'Crucifixo Invertido com Halteres', 'focus': 'Deltoide Posterior', 'rest': '60s', 'description': 'Tronco inclinado para frente, abrir os braços lateralmente focando nas costas superiores.'},
        {'name': 'Rosca Direta com Barra W', 'focus': 'Bíceps Cabeça Curta', 'rest': '75s', 'description': 'Flexionar os braços erguendo a barra, esmagando o bíceps no topo.'},
        {'name': 'Rosca Martelo com Halteres', 'focus': 'Bíceps/Braquiorradial', 'rest': '60s', 'description': 'Pegada neutra (palmas viradas para dentro), flexionar os braços alternadamente.'}
    ],
    'legs': [
        {'name': 'Agachamento Livre com Barra', 'focus': 'Quadríceps/Glúteos', 'rest': '120s', 'description': 'Barra nas costas, agachar até que as coxas fiquem paralelas ao chão ou mais.'},
        {'name': 'Leg Press 45°', 'focus': 'Quadríceps/Cadeia Posterior', 'rest': '90s', 'description': 'Pressione a plataforma controlando a descida até 90 graus de flexão.'},
        {'name': 'Cadeira Extensora', 'focus': 'Quadríceps Isolado', 'rest': '60s', 'description': 'Extensão completa dos joelhos na máquina, contraindo o quadríceps por 1 segundo no topo.'},
        {'name': 'Mesa Flexora', 'focus': 'Posteriores de Coxa', 'rest': '60s', 'description': 'Deitado na máquina, flexionar os joelhos trazendo o rolo até a linha dos glúteos.'},
        {'name': 'Stiff com Halteres ou Barra', 'focus': 'Posteriores/Glúteos', 'rest': '90s', 'description': 'Descer a barra rente às pernas flexionando levemente os joelhos e empurrando o quadril para trás.'},
        {'name': 'Gêmeos Sentado (Panturrilhas)', 'focus': 'Panturrilhas', 'rest': '60s', 'description': 'Realizar a flexão plantar na máquina com amplitude máxima.'}
    ],
    'full_body': [
        {'name': 'Agachamento com Halteres', 'focus': 'Pernas Completo', 'rest': '90s', 'description': 'Agachamento com halteres ao lado do corpo ou na altura dos ombros.'},
        {'name': 'Supino Reto com Halteres', 'focus': 'Peito/Ombro/Tríceps', 'rest': '90s', 'description': 'Empurrar os halteres verticalmente deitado no banco plano.'},
        {'name': 'Remada Serrote com Halter', 'focus': 'Costas/Bíceps', 'rest': '75s', 'description': 'Apoiado em um banco, puxar o halter na lateral do tronco focando na dorsal.'},
        {'name': 'Desenvolvimento com Halteres Sentado', 'focus': 'Ombros', 'rest': '75s', 'description': 'Sentado com apoio nas costas, empurrar os halteres para cima.'},
        {'name': 'Rosca Inclinada com Halteres', 'focus': 'Bíceps', 'rest': '60s', 'description': 'Sentado no banco inclinado a 45°, realizar a rosca simultânea.'},
        {'name': 'Prancha Abdominal', 'focus': 'Core', 'rest': '60s', 'description': 'Manter o corpo alinhado apoiado nos antebraços e ponta dos pés pelo tempo estipulado.'}
    ],
    'cardio_hiit': [
        {'name': 'Corrida na Esteira (Intervalado)', 'focus': 'Cardio/HIIT', 'rest': 'Sem descanso entre tiros', 'description': 'Aquecer 3 min. Fazer 10 tiros de 45 segundos em velocidade máxima com 1 minuto de caminhada leve de descanso.'},
        {'name': 'Bicicleta Ergométrica', 'focus': 'Cardio/Resistência', 'rest': 'Contínuo', 'description': 'Pedalar em ritmo moderado/intenso por 20 a 30 minutos.'},
        {'name': 'Burpees', 'focus': 'Metabólico/Fullbody', 'rest': '30s', 'description': 'Realizar 4 séries de 12 a 15 repetições com máxima intensidade metabólica.'},
        {'name': 'Pular Corda', 'focus': 'Agilidade/Cardio', 'rest': '45s', 'description': 'Pular corda continuamente por 2 minutos. Repetir 5 vezes.'}
    ]
}


def calculate_nutrition(gender, weight, height, age, activity_level, goal):
    """
    Calcula o gasto energético e divide os macronutrientes do usuário.
    Usa a fórmula Mifflin-St Jeor.
    """
    # 1. BMR
    if gender == 'male':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
    # 2. TDEE
    activity_factors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'extreme': 1.9
    }
    factor = activity_factors.get(activity_level, 1.2)
    tdee = bmr * factor
    
    # 3. Ajuste de Calorias por Objetivo
    if goal == 'lose':
        target_calories = tdee - 500
        # Mínimo seguro de calorias
        min_cal = 1200 if gender == 'female' else 1500
        if target_calories < min_cal:
            target_calories = min_cal
    elif goal == 'gain':
        target_calories = tdee + 350
    else:  # maintain
        target_calories = tdee
        
    # 4. Distribuição de Macros
    # Proteína: 2.0g por kg de peso corporal (4 kcal/g)
    protein_g = weight * 2.0
    protein_kcal = protein_g * 4
    
    # Gordura: 0.9g por kg de peso corporal (9 kcal/g)
    fat_g = weight * 0.9
    fat_kcal = fat_g * 9
    
    # Carboidrato: restante das calorias (4 kcal/g)
    carb_kcal = target_calories - (protein_kcal + fat_kcal)
    carb_g = carb_kcal / 4
    
    # Se carboidratos ficarem abaixo do mínimo saudável ou negativos, fazemos um ajuste proporcional
    if carb_g < 50:
        # Ajusta gorduras para baixo e proteínas para cima
        carb_g = 50
        carb_kcal = carb_g * 4
        # Distribui o restante (Target - Carb_kcal) em 65% proteína e 35% gordura
        remaining = target_calories - carb_kcal
        protein_kcal = remaining * 0.65
        protein_g = protein_kcal / 4
        fat_kcal = remaining * 0.35
        fat_g = fat_kcal / 9

    return {
        'bmr': round(bmr),
        'tdee': round(tdee),
        'target_calories': round(target_calories),
        'protein': round(protein_g),
        'carbs': round(carb_g),
        'fats': round(fat_g)
    }


def generate_meals(target_calories, macros, diet_preference):
    """
    Gera um plano alimentar ajustando as porções dos alimentos proporcionalmente
    com base no total de calorias alvo do usuário e sua preferência de dieta.
    """
    pref = diet_preference if diet_preference in FOOD_TEMPLATES else 'standard'
    template = FOOD_TEMPLATES[pref]
    
    # Vamos dividir as calorias e macros aproximadamente em:
    # Café da Manhã: 25% | Almoço: 35% | Lanche da Tarde: 15% | Jantar: 25%
    meal_distributions = {
        'cafe_da_manha': {'pct_cal': 0.25, 'name': '☕ Café da Manhã', 'time': '07:30'},
        'almoco': {'pct_cal': 0.35, 'name': '🍗 Almoço', 'time': '12:30'},
        'lanche_da_tarde': {'pct_cal': 0.15, 'name': '🍌 Lanche da Tarde', 'time': '16:00'},
        'jantar': {'pct_cal': 0.25, 'name': '🥗 Jantar', 'time': '20:00'}
    }
    
    meals_plan = []
    
    for meal_key, dist in meal_distributions.items():
        meal_target_cal = target_calories * dist['pct_cal']
        items = template.get(meal_key, [])
        
        # Calcular calorias base do prato de exemplo
        base_total_cal = 0
        for item in items:
            if item['unit'] == 'g' or item['unit'] == 'ml':
                base_total_cal += item['base_qty'] * item['base_cal'] if item['base_qty'] > 10 else item['base_qty'] * item['base_cal']
            else:
                base_total_cal += item['base_qty'] * item['base_cal']
                
        # Fator de escala para ajustar o tamanho da porção ao alvo do prato
        # Protegendo contra divisão por zero
        scale_factor = meal_target_cal / base_total_cal if base_total_cal > 0 else 1.0
        
        # Se for dieta low_carb e o item for pão/arroz, podemos reduzir o fator ou substituir, 
        # mas como já temos o template low_carb específico, a escala funciona bem.
        
        formatted_items = []
        meal_actual_cal = 0
        meal_actual_prot = 0
        meal_actual_carb = 0
        meal_actual_fat = 0
        
        for item in items:
            adjusted_qty = item['base_qty'] * scale_factor
            
            # Arredondamentos inteligentes
            if item['unit'] == 'g' or item['unit'] == 'ml':
                # Arredondar para o múltiplo de 5 ou 10 mais próximo para facilitar medição em balança
                adjusted_qty = round(adjusted_qty / 10) * 10
                if adjusted_qty < 10:
                    adjusted_qty = 10
            else:
                # Frações de unidade como 1.5 ovos ou 2 ovos
                adjusted_qty = round(adjusted_qty * 2) / 2
                if adjusted_qty < 0.5:
                    adjusted_qty = 0.5
            
            # Calcular macros do ingrediente com a quantidade ajustada
            if item['unit'] == 'g' or item['unit'] == 'ml':
                # Para gramas/ml, os valores prot_per_unit, etc. são calculados por 1 unidade do loop base,
                # precisamos saber se o multiplicador é direto por grama ou se era valor total do base_qty.
                # No nosso dicionário, se base_qty era 120 e base_cal 1.65, isso é kcal/grama.
                # Vamos padronizar:
                # Se prot_per_unit é decimal pequeno (< 1), indica g/grama do alimento.
                # Se for inteiro ou maior (como whey 30g com prot 0.8), prot_per_unit é por grama.
                # Na verdade, no FOOD_TEMPLATES criamos:
                # - 'Pão integral': 50g base_qty, prot_per_unit = 0.08 (8% proteína, ou seja, g por grama).
                # - 'Peito de frango': 120g, prot_per_unit = 0.31 (31% proteína, ou seja, g por grama).
                # - 'Ovos': 2 base_qty, prot_per_unit = 6 (6g por unidade).
                is_unit = item['unit'] not in ['g', 'ml']
                
                if is_unit:
                    item_prot = adjusted_qty * item['prot_per_unit']
                    item_carb = adjusted_qty * item['carb_per_unit']
                    item_fat = adjusted_qty * item['fat_per_unit']
                    item_cal = adjusted_qty * item['base_cal']
                else:
                    item_prot = adjusted_qty * item['prot_per_unit']
                    item_carb = adjusted_qty * item['carb_per_unit']
                    item_fat = adjusted_qty * item['fat_per_unit']
                    item_cal = adjusted_qty * item['base_cal']
            else:
                item_prot = adjusted_qty * item['prot_per_unit']
                item_carb = adjusted_qty * item['carb_per_unit']
                item_fat = adjusted_qty * item['fat_per_unit']
                item_cal = adjusted_qty * item['base_cal']
                
            meal_actual_cal += item_cal
            meal_actual_prot += item_prot
            meal_actual_carb += item_carb
            meal_actual_fat += item_fat
            
            formatted_items.append({
                'name': item['name'],
                'quantity': adjusted_qty,
                'unit': item['unit'],
                'calories': round(item_cal),
                'prot': round(item_prot, 1),
                'carb': round(item_carb, 1),
                'fat': round(item_fat, 1)
            })
            
        meals_plan.append({
            'name': dist['name'],
            'time': dist['time'],
            'calories': round(meal_actual_cal),
            'protein': round(meal_actual_prot),
            'carbs': round(meal_actual_carb),
            'fats': round(meal_actual_fat),
            'items': formatted_items
        })
        
    return meals_plan


def generate_workout(goal):
    """
    Gera um cronograma de treino semanal com exercícios específicos
    baseado no objetivo do usuário.
    """
    weekly_plan = []
    
    if goal == 'gain':
        # Hipertrofia: Divisão ABC de 5 dias (PPL com rodízio)
        weekly_plan = [
            {
                'day': 'Segunda-feira',
                'title': '🔥 Treino A - Empurrar (Peito, Ombros e Tríceps)',
                'exercises': [
                    {'name': EXERCISES_DATABASE['push'][0]['name'], 'sets': 4, 'reps': '8-10', 'rest': EXERCISES_DATABASE['push'][0]['rest'], 'notes': EXERCISES_DATABASE['push'][0]['description']},
                    {'name': EXERCISES_DATABASE['push'][1]['name'], 'sets': 3, 'reps': '10-12', 'rest': EXERCISES_DATABASE['push'][1]['rest'], 'notes': EXERCISES_DATABASE['push'][1]['description']},
                    {'name': EXERCISES_DATABASE['push'][2]['name'], 'sets': 3, 'reps': '8-10', 'rest': EXERCISES_DATABASE['push'][2]['rest'], 'notes': EXERCISES_DATABASE['push'][2]['description']},
                    {'name': EXERCISES_DATABASE['push'][3]['name'], 'sets': 4, 'reps': '12-15', 'rest': EXERCISES_DATABASE['push'][3]['rest'], 'notes': EXERCISES_DATABASE['push'][3]['description']},
                    {'name': EXERCISES_DATABASE['push'][4]['name'], 'sets': 3, 'reps': '10-12', 'rest': EXERCISES_DATABASE['push'][4]['rest'], 'notes': EXERCISES_DATABASE['push'][4]['description']},
                    {'name': EXERCISES_DATABASE['push'][5]['name'], 'sets': 3, 'reps': '10-12', 'rest': EXERCISES_DATABASE['push'][5]['rest'], 'notes': EXERCISES_DATABASE['push'][5]['description']}
                ]
            },
            {
                'day': 'Terça-feira',
                'title': '⚡ Treino B - Puxar (Costas, Deltoide Post. e Bíceps)',
                'exercises': [
                    {'name': EXERCISES_DATABASE['pull'][0]['name'], 'sets': 4, 'reps': '8-10', 'rest': EXERCISES_DATABASE['pull'][0]['rest'], 'notes': EXERCISES_DATABASE['pull'][0]['description']},
                    {'name': EXERCISES_DATABASE['pull'][1]['name'], 'sets': 3, 'reps': '10-12', 'rest': EXERCISES_DATABASE['pull'][1]['rest'], 'notes': EXERCISES_DATABASE['pull'][1]['description']},
                    {'name': EXERCISES_DATABASE['pull'][2]['name'], 'sets': 3, 'reps': '10-12', 'rest': EXERCISES_DATABASE['pull'][2]['rest'], 'notes': EXERCISES_DATABASE['pull'][2]['description']},
                    {'name': EXERCISES_DATABASE['pull'][3]['name'], 'sets': 3, 'reps': '12-15', 'rest': EXERCISES_DATABASE['pull'][3]['rest'], 'notes': EXERCISES_DATABASE['pull'][3]['description']},
                    {'name': EXERCISES_DATABASE['pull'][4]['name'], 'sets': 3, 'reps': '8-10', 'rest': EXERCISES_DATABASE['pull'][4]['rest'], 'notes': EXERCISES_DATABASE['pull'][4]['description']},
                    {'name': EXERCISES_DATABASE['pull'][5]['name'], 'sets': 3, 'reps': '10-12', 'rest': EXERCISES_DATABASE['pull'][5]['rest'], 'notes': EXERCISES_DATABASE['pull'][5]['description']}
                ]
            },
            {
                'day': 'Quarta-feira',
                'title': '🏃 Cardio Regenerativo e Core',
                'exercises': [
                    {'name': EXERCISES_DATABASE['cardio_hiit'][1]['name'], 'sets': 1, 'reps': '30 min', 'rest': 'Contínuo', 'notes': 'Pedalar em ritmo moderado para recuperar as fibras musculares.'},
                    {'name': EXERCISES_DATABASE['full_body'][5]['name'], 'sets': 3, 'reps': '60 seg', 'rest': '60s', 'notes': EXERCISES_DATABASE['full_body'][5]['description']}
                ]
            },
            {
                'day': 'Quinta-feira',
                'title': '🍗 Treino C - Pernas Completo',
                'exercises': [
                    {'name': EXERCISES_DATABASE['legs'][0]['name'], 'sets': 4, 'reps': '8-10', 'rest': EXERCISES_DATABASE['legs'][0]['rest'], 'notes': EXERCISES_DATABASE['legs'][0]['description']},
                    {'name': EXERCISES_DATABASE['legs'][1]['name'], 'sets': 3, 'reps': '10-12', 'rest': EXERCISES_DATABASE['legs'][1]['rest'], 'notes': EXERCISES_DATABASE['legs'][1]['description']},
                    {'name': EXERCISES_DATABASE['legs'][4]['name'], 'sets': 3, 'reps': '10-12', 'rest': EXERCISES_DATABASE['legs'][4]['rest'], 'notes': EXERCISES_DATABASE['legs'][4]['description']},
                    {'name': EXERCISES_DATABASE['legs'][3]['name'], 'sets': 3, 'reps': '12-15', 'rest': EXERCISES_DATABASE['legs'][3]['rest'], 'notes': EXERCISES_DATABASE['legs'][3]['description']},
                    {'name': EXERCISES_DATABASE['legs'][2]['name'], 'sets': 3, 'reps': '12', 'rest': EXERCISES_DATABASE['legs'][2]['rest'], 'notes': EXERCISES_DATABASE['legs'][2]['description']},
                    {'name': EXERCISES_DATABASE['legs'][5]['name'], 'sets': 4, 'reps': '15-20', 'rest': EXERCISES_DATABASE['legs'][5]['rest'], 'notes': EXERCISES_DATABASE['legs'][5]['description']}
                ]
            },
            {
                'day': 'Sexta-feira',
                'title': '💥 Treino Superior Híbrido (Peito & Costas foco Pump)',
                'exercises': [
                    {'name': EXERCISES_DATABASE['push'][0]['name'], 'sets': 3, 'reps': '10', 'rest': '90s', 'notes': 'Supino focado em cadência controlada na descida.'},
                    {'name': EXERCISES_DATABASE['pull'][0]['name'], 'sets': 3, 'reps': '10', 'rest': '90s', 'notes': 'Puxada aberta trabalhando expansão da dorsal.'},
                    {'name': EXERCISES_DATABASE['push'][1]['name'], 'sets': 3, 'reps': '12', 'rest': '75s', 'notes': 'Supino inclinado com halteres.'},
                    {'name': EXERCISES_DATABASE['pull'][2]['name'], 'sets': 3, 'reps': '12', 'rest': '75s', 'notes': 'Remada baixa cabo.'},
                    {'name': EXERCISES_DATABASE['push'][3]['name'], 'sets': 3, 'reps': '15', 'rest': '60s', 'notes': 'Elevação lateral.'},
                    {'name': EXERCISES_DATABASE['full_body'][5]['name'], 'sets': 3, 'reps': '45 seg', 'rest': '45s', 'notes': EXERCISES_DATABASE['full_body'][5]['description']}
                ]
            },
            {
                'day': 'Sábado',
                'title': '💤 Descanso Ativo / Alongamentos',
                'exercises': [
                    {'name': 'Caminhada ao ar livre', 'sets': 1, 'reps': '40 min', 'rest': 'Livre', 'notes': 'Caminhada de baixa intensidade para bem-estar mental e circulatório.'}
                ]
            },
            {
                'day': 'Domingo',
                'title': '💤 Descanso Total (Recuperação Muscular)',
                'exercises': [
                    {'name': 'Repouso Absoluto', 'sets': 0, 'reps': '-', 'rest': '-', 'notes': 'Durma bem, alimente-se e prepare-se para a próxima semana de treinos.'}
                ]
            }
        ]
    elif goal == 'lose':
        # Definição/Emagrecimento: Treinos de alta densidade (Super-sets) + Cardio HIIT focado
        weekly_plan = [
            {
                'day': 'Segunda-feira',
                'title': '⚡ Full Body A (Metabólico e Força)',
                'exercises': [
                    {'name': EXERCISES_DATABASE['full_body'][0]['name'], 'sets': 4, 'reps': '12-15', 'rest': '60s', 'notes': EXERCISES_DATABASE['full_body'][0]['description']},
                    {'name': EXERCISES_DATABASE['full_body'][1]['name'], 'sets': 4, 'reps': '12', 'rest': '60s', 'notes': EXERCISES_DATABASE['full_body'][1]['description']},
                    {'name': EXERCISES_DATABASE['full_body'][2]['name'], 'sets': 3, 'reps': '12-15', 'rest': '60s', 'notes': EXERCISES_DATABASE['full_body'][2]['description']},
                    {'name': EXERCISES_DATABASE['full_body'][3]['name'], 'sets': 3, 'reps': '12', 'rest': '60s', 'notes': EXERCISES_DATABASE['full_body'][3]['description']},
                    {'name': EXERCISES_DATABASE['legs'][3]['name'], 'sets': 3, 'reps': '15', 'rest': '45s', 'notes': 'Mesa flexora para isolar posterior.'},
                    {'name': EXERCISES_DATABASE['full_body'][5]['name'], 'sets': 4, 'reps': '45 seg', 'rest': '45s', 'notes': EXERCISES_DATABASE['full_body'][5]['description']}
                ]
            },
            {
                'day': 'Terça-feira',
                'title': '💦 Queima de Gordura - HIIT & Cardio',
                'exercises': [
                    {'name': EXERCISES_DATABASE['cardio_hiit'][0]['name'], 'sets': 1, 'reps': '20 min', 'rest': 'Intervalado', 'notes': EXERCISES_DATABASE['cardio_hiit'][0]['description']},
                    {'name': EXERCISES_DATABASE['cardio_hiit'][2]['name'], 'sets': 4, 'reps': '15 reps', 'rest': '30s', 'notes': EXERCISES_DATABASE['cardio_hiit'][2]['description']},
                    {'name': EXERCISES_DATABASE['cardio_hiit'][3]['name'], 'sets': 4, 'reps': '2 min', 'rest': '45s', 'notes': EXERCISES_DATABASE['cardio_hiit'][3]['description']}
                ]
            },
            {
                'day': 'Quarta-feira',
                'title': '⚡ Full Body B (Metabólico e Força)',
                'exercises': [
                    {'name': EXERCISES_DATABASE['legs'][1]['name'], 'sets': 4, 'reps': '15', 'rest': '75s', 'notes': 'Leg Press controlando bem a descida.'},
                    {'name': EXERCISES_DATABASE['pull'][0]['name'], 'sets': 3, 'reps': '12-15', 'rest': '60s', 'notes': EXERCISES_DATABASE['pull'][0]['description']},
                    {'name': EXERCISES_DATABASE['push'][2]['name'], 'sets': 3, 'reps': '12', 'rest': '60s', 'notes': EXERCISES_DATABASE['push'][2]['description']},
                    {'name': EXERCISES_DATABASE['pull'][4]['name'], 'sets': 3, 'reps': '12', 'rest': '60s', 'notes': EXERCISES_DATABASE['pull'][4]['description']},
                    {'name': EXERCISES_DATABASE['push'][4]['name'], 'sets': 3, 'reps': '12-15', 'rest': '45s', 'notes': EXERCISES_DATABASE['push'][4]['description']},
                    {'name': EXERCISES_DATABASE['full_body'][5]['name'], 'sets': 4, 'reps': '60 seg', 'rest': '45s', 'notes': EXERCISES_DATABASE['full_body'][5]['description']}
                ]
            },
            {
                'day': 'Quinta-feira',
                'title': '🏃 Cardio Contínuo (LISS) & Mobilidade',
                'exercises': [
                    {'name': 'Esteira - Caminhada Inclinada', 'sets': 1, 'reps': '45 min', 'rest': 'Contínuo', 'notes': 'Velocidade de 5.5 a 6.0 km/h com inclinação de 5% a 8%.'},
                    {'name': 'Alongamentos Gerais e Mobilidade Quadril/Tornozelo', 'sets': 1, 'reps': '15 min', 'rest': 'Livre', 'notes': 'Soltura de articulações e aumento de flexibilidade.'}
                ]
            },
            {
                'day': 'Sexta-feira',
                'title': '⚡ Full Body C (Foco Circuito)',
                'exercises': [
                    {'name': EXERCISES_DATABASE['legs'][4]['name'], 'sets': 3, 'reps': '15', 'rest': '60s', 'notes': 'Stiff com halteres.'},
                    {'name': EXERCISES_DATABASE['push'][1]['name'], 'sets': 3, 'reps': '12', 'rest': '60s', 'notes': 'Supino inclinado halteres.'},
                    {'name': EXERCISES_DATABASE['pull'][1]['name'], 'sets': 3, 'reps': '12', 'rest': '60s', 'notes': 'Remada curvada barra.'},
                    {'name': EXERCISES_DATABASE['push'][3]['name'], 'sets': 3, 'reps': '15', 'rest': '45s', 'notes': 'Elevação lateral ombros.'},
                    {'name': EXERCISES_DATABASE['pull'][5]['name'], 'sets': 3, 'reps': '12', 'rest': '45s', 'notes': 'Rosca martelo bíceps.'},
                    {'name': EXERCISES_DATABASE['cardio_hiit'][2]['name'], 'sets': 3, 'reps': '10 reps', 'rest': '30s', 'notes': 'Burpees para pico de queima calórica.'}
                ]
            },
            {
                'day': 'Sábado',
                'title': '💦 Cardio Livre de Fim de Semana',
                'exercises': [
                    {'name': 'Esporte livre ou Corrida leve ao ar livre', 'sets': 1, 'reps': '30-40 min', 'rest': 'Livre', 'notes': 'Ciclismo, corrida, futebol, natação ou caminhada rápida.'}
                ]
            },
            {
                'day': 'Domingo',
                'title': '💤 Descanso Total (Recuperação)',
                'exercises': [
                    {'name': 'Repouso', 'sets': 0, 'reps': '-', 'rest': '-', 'notes': 'Recupere sua musculatura e hidrate-se bem para a próxima semana.'}
                ]
            }
        ]
    else:
        # Condicionamento / Manutenção: Divisão AB Superior/Inferior 4 dias
        weekly_plan = [
            {
                'day': 'Segunda-feira',
                'title': '💪 Treino A - Membros Superiores (Foco Tonificação)',
                'exercises': [
                    {'name': EXERCISES_DATABASE['push'][0]['name'], 'sets': 3, 'reps': '10-12', 'rest': '90s', 'notes': EXERCISES_DATABASE['push'][0]['description']},
                    {'name': EXERCISES_DATABASE['pull'][0]['name'], 'sets': 3, 'reps': '10-12', 'rest': '90s', 'notes': EXERCISES_DATABASE['pull'][0]['description']},
                    {'name': EXERCISES_DATABASE['push'][2]['name'], 'sets': 3, 'reps': '10-12', 'rest': '75s', 'notes': EXERCISES_DATABASE['push'][2]['description']},
                    {'name': EXERCISES_DATABASE['pull'][2]['name'], 'sets': 3, 'reps': '10-12', 'rest': '75s', 'notes': EXERCISES_DATABASE['pull'][2]['description']},
                    {'name': EXERCISES_DATABASE['push'][4]['name'], 'sets': 3, 'reps': '12', 'rest': '60s', 'notes': EXERCISES_DATABASE['push'][4]['description']},
                    {'name': EXERCISES_DATABASE['pull'][4]['name'], 'sets': 3, 'reps': '12', 'rest': '60s', 'notes': EXERCISES_DATABASE['pull'][4]['description']}
                ]
            },
            {
                'day': 'Terça-feira',
                'title': '🦵 Treino B - Membros Inferiores e Core',
                'exercises': [
                    {'name': EXERCISES_DATABASE['legs'][0]['name'], 'sets': 3, 'reps': '10-12', 'rest': '90s', 'notes': EXERCISES_DATABASE['legs'][0]['description']},
                    {'name': EXERCISES_DATABASE['legs'][4]['name'], 'sets': 3, 'reps': '10-12', 'rest': '90s', 'notes': EXERCISES_DATABASE['legs'][4]['description']},
                    {'name': EXERCISES_DATABASE['legs'][1]['name'], 'sets': 3, 'reps': '12', 'rest': '75s', 'notes': EXERCISES_DATABASE['legs'][1]['description']},
                    {'name': EXERCISES_DATABASE['legs'][3]['name'], 'sets': 3, 'reps': '12', 'rest': '60s', 'notes': EXERCISES_DATABASE['legs'][3]['description']},
                    {'name': EXERCISES_DATABASE['legs'][5]['name'], 'sets': 3, 'reps': '15', 'rest': '60s', 'notes': EXERCISES_DATABASE['legs'][5]['description']},
                    {'name': EXERCISES_DATABASE['full_body'][5]['name'], 'sets': 3, 'reps': '60 seg', 'rest': '45s', 'notes': EXERCISES_DATABASE['full_body'][5]['description']}
                ]
            },
            {
                'day': 'Quarta-feira',
                'title': '🏃 Cardio Moderado LISS',
                'exercises': [
                    {'name': EXERCISES_DATABASE['cardio_hiit'][1]['name'], 'sets': 1, 'reps': '30-40 min', 'rest': 'Contínuo', 'notes': 'Manter frequência cardíaca em zona de queima de gordura aeróbica.'}
                ]
            },
            {
                'day': 'Quinta-feira',
                'title': '💪 Treino A - Membros Superiores (Variação)',
                'exercises': [
                    {'name': EXERCISES_DATABASE['push'][1]['name'], 'sets': 3, 'reps': '10-12', 'rest': '90s', 'notes': EXERCISES_DATABASE['push'][1]['description']},
                    {'name': EXERCISES_DATABASE['pull'][1]['name'], 'sets': 3, 'reps': '10-12', 'rest': '90s', 'notes': EXERCISES_DATABASE['pull'][1]['description']},
                    {'name': EXERCISES_DATABASE['push'][3]['name'], 'sets': 3, 'reps': '12-15', 'rest': '60s', 'notes': EXERCISES_DATABASE['push'][3]['description']},
                    {'name': EXERCISES_DATABASE['pull'][3]['name'], 'sets': 3, 'reps': '12-15', 'rest': '60s', 'notes': EXERCISES_DATABASE['pull'][3]['description']},
                    {'name': EXERCISES_DATABASE['push'][5]['name'], 'sets': 3, 'reps': '12', 'rest': '60s', 'notes': EXERCISES_DATABASE['push'][5]['description']},
                    {'name': EXERCISES_DATABASE['pull'][5]['name'], 'sets': 3, 'reps': '12', 'rest': '60s', 'notes': EXERCISES_DATABASE['pull'][5]['description']}
                ]
            },
            {
                'day': 'Sexta-feira',
                'title': '🦵 Treino B - Membros Inferiores (Variação)',
                'exercises': [
                    {'name': EXERCISES_DATABASE['legs'][1]['name'], 'sets': 3, 'reps': '12', 'rest': '90s', 'notes': 'Foco em amplitude máxima controlada.'},
                    {'name': EXERCISES_DATABASE['legs'][3]['name'], 'sets': 3, 'reps': '12', 'rest': '60s', 'notes': EXERCISES_DATABASE['legs'][3]['description']},
                    {'name': EXERCISES_DATABASE['legs'][2]['name'], 'sets': 3, 'reps': '12-15', 'rest': '60s', 'notes': EXERCISES_DATABASE['legs'][2]['description']},
                    {'name': EXERCISES_DATABASE['legs'][5]['name'], 'sets': 3, 'reps': '15', 'rest': '60s', 'notes': EXERCISES_DATABASE['legs'][5]['description']},
                    {'name': EXERCISES_DATABASE['cardio_hiit'][2]['name'], 'sets': 3, 'reps': '10 reps', 'rest': '45s', 'notes': EXERCISES_DATABASE['cardio_hiit'][2]['description']}
                ]
            },
            {
                'day': 'Sábado',
                'title': '🏃 Cardio HIIT Curto',
                'exercises': [
                    {'name': EXERCISES_DATABASE['cardio_hiit'][0]['name'], 'sets': 1, 'reps': '15 min', 'rest': 'Tiros intensos', 'notes': '15 minutos de corrida de alta intensidade no formato de tiros rápidos.'}
                ]
            },
            {
                'day': 'Domingo',
                'title': '💤 Descanso Total',
                'exercises': [
                    {'name': 'Descanso', 'sets': 0, 'reps': '-', 'rest': '-', 'notes': 'Dia de recuperar as energias.'}
                ]
            }
        ]
        
    return weekly_plan


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/generate-plan', methods=['POST'])
def handle_generate_plan():
    try:
        data = request.get_json()
        
        # Validar dados de entrada
        name = data.get('name', 'Campeão')
        gender = data.get('gender', 'male')
        weight = float(data.get('weight', 70))
        height = float(data.get('height', 170))
        age = int(data.get('age', 25))
        activity_level = data.get('activity_level', 'moderate')
        goal = data.get('goal', 'maintain')
        diet_preference = data.get('diet_preference', 'standard')
        
        # 1. Calcular Necessidades Energéticas e Macronutrientes
        nutrition = calculate_nutrition(gender, weight, height, age, activity_level, goal)
        
        # 2. Gerar Plano de Refeições
        meals = generate_meals(nutrition['target_calories'], nutrition, diet_preference)
        
        # 3. Gerar Plano de Treino Semanal
        workout = generate_workout(goal)
        
        # 4. Retornar resposta formatada
        response_data = {
            'user': {
                'name': name,
                'weight': weight,
                'height': height,
                'goal': goal,
                'diet_preference': diet_preference
            },
            'nutrition': nutrition,
            'diet_plan': meals,
            'workout_plan': workout
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    # Roda localmente na porta 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
