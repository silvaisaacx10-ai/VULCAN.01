import os
from werkzeug.security import generate_password_hash

app_path = r'C:\Users\Usuario\.gemini\antigravity\scratch\VULCAN.01\app.py'

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Add the /api/admin/users route
admin_users_route = """
@app.route('/api/admin/users', methods=['POST'])
def get_admin_users():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        # Admin Authentication
        if email == 'silvaisaacx10@gmail.com' and password == 'vidanova':
            pass
        elif email == 'joaoeduardodeassuncao@gmail.com' and password == 'leticio':
            pass
        else:
            return jsonify({'error': 'Acesso negado'}), 401
            
        users_res = supabase.table('vulcan_users').select('name, email, created_at, last_active, is_blocked, blocked_by').execute()
        return jsonify({'users': users_res.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/toggle-block'"""

if '/api/admin/users' not in content:
    content = content.replace("@app.route('/api/admin/toggle-block'", admin_users_route)

# Now fix generate_plan to return 6 days and tips
new_generate_plan = """def generate_plan():
    try:
        data = request.json
        name = data.get('name', 'User')
        age = int(data.get('age', 25))
        weight = float(data.get('weight', 70))
        height = float(data.get('height', 175))
        gender = data.get('gender', 'male').lower()
        freq = int(data.get('exercise_frequency', 3))
        goal = data.get('goal', 'maintenance').lower()
        diet_pref = data.get('diet_preference', 'standard').lower()

        # BMR calc
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        multipliers = {0: 1.2, 1: 1.375, 2: 1.375, 3: 1.55, 4: 1.55, 5: 1.725, 6: 1.725, 7: 1.9}
        tdee = bmr * multipliers.get(min(freq, 7), 1.2)

        if 'cutting' in goal or 'emagrecimento' in goal or 'lose' in goal:
            target_cals = tdee - 500
        elif 'hypertrophy' in goal or 'hipertrofia' in goal or 'gain' in goal:
            target_cals = tdee + 500
        else:
            target_cals = tdee
            
        protein = weight * 2.2 # 2.2g per kg
        fat = (target_cals * 0.25) / 9
        carbs = (target_cals - (protein * 4) - (fat * 9)) / 4
        
        water = weight * 35 # 35ml per kg
        
        bmi = round(weight / ((height/100)**2), 1)
        bmi_class = 'Abaixo do peso' if bmi < 18.5 else 'Normal' if bmi < 25 else 'Sobrepeso' if bmi < 30 else 'Obesidade'

        diet_plan = [
            {'meal': 'Café da Manhã', 'items': [{'name': 'Ovos', 'qty': '3 un'}, {'name': 'Aveia', 'qty': '40g'}]},
            {'meal': 'Almoço', 'items': [{'name': 'Frango', 'qty': '150g'}, {'name': 'Arroz', 'qty': '100g'}, {'name': 'Brócolis', 'qty': '50g'}]},
            {'meal': 'Lanche da Tarde', 'items': [{'name': 'Whey Protein', 'qty': '30g'}, {'name': 'Banana', 'qty': '1 un'}]},
            {'meal': 'Jantar', 'items': [{'name': 'Carne Vermelha', 'qty': '150g'}, {'name': 'Mandioca', 'qty': '100g'}, {'name': 'Salada Verde', 'qty': 'À vontade'}]}
        ]
        
        if diet_pref == 'low carb':
            diet_plan[1]['items'][1] = {'name': 'Azeite', 'qty': '1 colher'}
            diet_plan[3]['items'][1] = {'name': 'Abacate', 'qty': '100g'}
            
        if diet_pref == 'vegano' or diet_pref == 'vegetariano':
            diet_plan[0]['items'][0] = {'name': 'Tofu', 'qty': '100g'}
            diet_plan[1]['items'][0] = {'name': 'Grão de Bico', 'qty': '150g'}
            diet_plan[3]['items'][0] = {'name': 'Soja', 'qty': '100g'}
        
        workout_plan = [
            {
                'day': 'Treino A', 'title': 'Peito, Ombro e Tríceps', 'desc': 'Foco em exercícios de empurrar.',
                'exercises': [
                    {'name': 'Supino Reto 4x10', 'tutorial': 'Mantenha os pés firmes e cotovelos a 45 graus.'},
                    {'name': 'Crucifixo 3x12', 'tutorial': 'Movimento controlado, foque no alongamento.'},
                    {'name': 'Desenvolvimento 3x10', 'tutorial': 'Coluna reta, não utilize impulso.'},
                    {'name': 'Tríceps Pulley 4x12', 'tutorial': 'Mantenha os cotovelos colados ao corpo.'}
                ]
            },
            {
                'day': 'Treino B', 'title': 'Costas e Bíceps', 'desc': 'Foco em exercícios de puxar.',
                'exercises': [
                    {'name': 'Puxada Frente 4x10', 'tutorial': 'Estufe o peito e puxe a barra com as dorsais.'},
                    {'name': 'Remada Curvada 3x12', 'tutorial': 'Costas retas, puxe o peso em direção ao umbigo.'},
                    {'name': 'Rosca Direta 4x12', 'tutorial': 'Evite balançar o tronco. Foque apenas no bíceps.'}
                ]
            },
            {
                'day': 'Treino C', 'title': 'Pernas Completas', 'desc': 'Foco em volume alto.',
                'exercises': [
                    {'name': 'Agachamento Livre 4x10', 'tutorial': 'Desça até quebrar a paralela.'},
                    {'name': 'Leg Press 3x12', 'tutorial': 'Não estique os joelhos completamente no topo.'},
                    {'name': 'Cadeira Extensora 4x15', 'tutorial': 'Segure o peso por 1 segundo no topo do movimento.'},
                    {'name': 'Mesa Flexora 4x12', 'tutorial': 'Controle a descida.'}
                ]
            },
            {
                'day': 'Treino D', 'title': 'Upper Body (Membros Superiores)', 'desc': 'Força e estímulo extra.',
                'exercises': [
                    {'name': 'Supino Inclinado 3x10', 'tutorial': 'Foque na parte superior do peito.'},
                    {'name': 'Barra Fixa 3x Falha', 'tutorial': 'Controle a descida.'},
                    {'name': 'Elevação Lateral 4x15', 'tutorial': 'Braços levemente flexionados.'}
                ]
            },
            {
                'day': 'Treino E', 'title': 'Lower Body (Membros Inferiores)', 'desc': 'Estímulo de hipertrofia.',
                'exercises': [
                    {'name': 'Stiff 4x10', 'tutorial': 'Sinta o alongamento no posterior de coxa.'},
                    {'name': 'Passada 3x12', 'tutorial': 'Mantenha o tronco reto.'},
                    {'name': 'Panturrilha 5x15', 'tutorial': 'Máxima amplitude de movimento.'}
                ]
            },
            {
                'day': 'Treino F', 'title': 'Cardio e Abs', 'desc': 'Recuperação ativa.',
                'exercises': [
                    {'name': 'Cardio 40 min', 'tutorial': 'Caminhada acelerada ou bicicleta leve.'},
                    {'name': 'Prancha 3x 1min', 'tutorial': 'Contração total do abdômen.'}
                ]
            }
        ]
        
        tips = [
            "Beba muita água: a hipertrofia e a perda de gordura dependem de hidratação.",
            "O descanso é crucial: os músculos crescem enquanto você dorme.",
            "Não pule o aquecimento: prepare as articulações para o treino.",
            "Seja consistente: a disciplina vence a motivação a longo prazo."
        ]
        
        return jsonify({
            'user': data,
            'nutrition': {
                'bmi': bmi,
                'bmi_class': bmi_class,
                'target_calories': round(target_cals),
                'protein': round(protein),
                'carbs': round(carbs),
                'fat': round(fat)
            },
            'water_target': round(water),
            'diet_plan': diet_plan,
            'workout_plan': workout_plan,
            'tips': tips
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500"""

content = re.sub(r'def generate_plan\(\):.*?return jsonify\(\{.*?\}\), 200\n    except Exception as e:\n        return jsonify\(\{\'error\': str\(e\)\}\), 500', new_generate_plan, content, flags=re.DOTALL)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Update the passwords for admins to the ones requested
from supabase import create_client
SUPABASE_URL = 'https://vttftmbzhieocsnrltuf.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0dGZ0bWJ6aGllb2NzbnJsdHVmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjM5MTA1NSwiZXhwIjoyMTAxOTY3MDU1fQ.psEljKT4TsxWWPONVStGKWuEDEwm7Ip8ieUkLiRGreE'
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

pwd1 = generate_password_hash('vidanova')
supabase.table('vulcan_users').update({'password_hash': pwd1}).eq('email', 'silvaisaacx10@gmail.com').execute()

pwd2 = generate_password_hash('leticio')
supabase.table('vulcan_users').update({'password_hash': pwd2}).eq('email', 'joaoeduardodeassuncao@gmail.com').execute()

print("Backend features added and admin passwords forcibly reset.")
