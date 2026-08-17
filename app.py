import os
import json
import hashlib
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client

app = Flask(__name__)

SUPABASE_URL = 'https://vttftmbzhieocsnrltuf.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0dGZ0bWJ6aGllb2NzbnJsdHVmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjM5MTA1NSwiZXhwIjoyMTAxOTY3MDU1fQ.psEljKT4TsxWWPONVStGKWuEDEwm7Ip8ieUkLiRGreE'


SUPABASE_INIT_ERROR = None
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Failed to initialize Supabase client: {e}")
    import traceback
    SUPABASE_INIT_ERROR = str(e) + " | " + traceback.format_exc()
    supabase = None


EXEMPT_EMAILS = ['silvaisaacx10@gmail.com', 'joaoeduardodeassuncao@gmail.com']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')

        if not email or not name or not password:
            return jsonify({'error': 'Missing required fields'}), 400

        hashed_password = generate_password_hash(password)
        
        # Check if user exists
        existing = supabase.table('vulcan_users').select('*').eq('email', email).execute()
        if existing.data:
            return jsonify({'error': 'User already exists'}), 400

        new_user = {
            'email': email,
            'name': name,
            'password_hash': hashed_password,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'is_blocked': False,
            'plan': None,
            'progressHistory': []
        }

        response = supabase.table('vulcan_users').insert(new_user).execute()
        return jsonify({'message': 'Registration successful', 'user': response.data[0]}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    if supabase is None:
        return jsonify({'error': f"CRITICAL SUPABASE INIT ERROR: {SUPABASE_INIT_ERROR}"}), 500

    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Missing required fields'}), 400

        response = supabase.table('vulcan_users').select('*').eq('email', email).execute()
        if not response.data:
            return jsonify({'error': 'Invalid credentials'}), 401

        user = response.data[0]
        
        db_hash = user['password_hash']
        is_valid = False
        
        # New format (werkzeug scrypt)
        if db_hash.startswith('scrypt:') or db_hash.startswith('pbkdf2:'):
            is_valid = check_password_hash(db_hash, password)
        else:
            # Old format (raw SHA-256)
            old_hash = hashlib.sha256(password.encode()).hexdigest()
            if db_hash == old_hash:
                is_valid = True
            elif db_hash == password: # In case some were plaintext
                is_valid = True
                
        if not is_valid:
            return jsonify({'error': 'Senha incorreta!'}), 401

        # Check for auto-block logic
        if user.get('is_blocked'):
            return jsonify({'error': 'Account blocked', 'blocked_by': user.get('blocked_by')}), 403

        if email not in EXEMPT_EMAILS:
            created_at_str = user.get('created_at')
            if created_at_str:
                try:
                    # Parse the ISO format string
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    if datetime.now(timezone.utc) - created_at > timedelta(days=21):
                        # Auto block
                        supabase.table('vulcan_users').update({'is_blocked': True, 'blocked_by': 'Auto 21 Dias'}).eq('email', email).execute()
                        return jsonify({'error': 'Account blocked', 'blocked_by': 'Auto 21 Dias'}), 403
                except Exception as parse_err:
                    print(f"Date parsing error: {parse_err}")
        
        # update last active
        supabase.table('vulcan_users').update({'last_active': datetime.now(timezone.utc).isoformat()}).eq('email', email).execute()
        
        return jsonify({
            'message': 'Login successful', 
            'user': {
                'email': user.get('email'),
                'name': user.get('name'),
                'plan': user.get('plan'),
                'progressHistory': user.get('progressHistory', []),
                'streak': user.get('streak', 0)
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/save-plan', methods=['POST'])
def save_plan():
    try:
        data = request.json
        email = data.get('email')
        plan = data.get('plan')
        if not email or not plan:
            return jsonify({'error': 'Missing email or plan'}), 400

        supabase.table('vulcan_users').update({'plan': plan}).eq('email', email).execute()
        return jsonify({'message': 'Plan saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/load-plan', methods=['POST'])
def load_plan():
    try:
        data = request.json
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Missing email'}), 400

        response = supabase.table('vulcan_users').select('plan, progressHistory, streak').eq('email', email).execute()
        if not response.data:
            return jsonify({'error': 'User not found'}), 404
        
        user = response.data[0]
        return jsonify({
            'plan': user.get('plan'),
            'progressHistory': user.get('progressHistory', []),
            'streak': user.get('streak', 0)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/update-progress', methods=['POST'])
def update_progress():
    try:
        data = request.json
        email = data.get('email')
        weight = data.get('weight')
        arms = data.get('arms')
        legs = data.get('legs')
        hips = data.get('hips')
        
        if not email:
            return jsonify({'error': 'Missing email'}), 400

        response = supabase.table('vulcan_users').select('progressHistory').eq('email', email).execute()
        if not response.data:
            return jsonify({'error': 'User not found'}), 404
        
        history = response.data[0].get('progressHistory') or []
        new_entry = {
            'date': datetime.now(timezone.utc).isoformat(),
            'weight': weight,
            'arms': arms,
            'legs': legs,
            'hips': hips
        }
        history.append(new_entry)
        
        supabase.table('vulcan_users').update({'progressHistory': history}).eq('email', email).execute()
        return jsonify({'message': 'Progress updated', 'progressHistory': history}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
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
        return jsonify({'error': str(e)}), 500


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
, methods=['POST'])
def toggle_block():
    try:
        data = request.json
        target_email = data.get('target_email')
        if not target_email:
            return jsonify({'error': 'Missing target_email'}), 400
            
        user_res = supabase.table('vulcan_users').select('is_blocked').eq('email', target_email).execute()
        if not user_res.data:
            return jsonify({'error': 'User not found'}), 404
            
        current_status = user_res.data[0].get('is_blocked', False)
        new_status = not current_status
        blocked_by = 'Admin' if new_status else None
        
        supabase.table('vulcan_users').update({'is_blocked': new_status, 'blocked_by': blocked_by}).eq('email', target_email).execute()
        return jsonify({'message': f"User blocked status set to {new_status}"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
