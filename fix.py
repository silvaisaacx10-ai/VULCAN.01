with open('templates/index.html', 'rb') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    s = line.decode('utf-8', errors='ignore')
    if 'Econ' in s and 'mica' in s:
        lines[i] = b'                                    <span style="font-weight:600; color:var(--accent);">Quero uma Dieta Econ\xc3\xb4mica</span>\n'
    if 'Prioriza ingredientes' in s and 'salm' in s:
        lines[i] = b'                                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 4px; line-height: 1.4;">Prioriza ingredientes baratos como frango, patinho, batata, arroz e aveia, evitando itens caros como salm\xc3\xa3o ou castanhas.</p>\n'
    if 'Usu' in s and 'rio' in s and 'profile-display-name' in s:
        lines[i] = b'                            <h2 style="font-family: var(--font-heading);" id="profile-display-name">Usu\xc3\xa1rio</h2>\n'
    if 'Card' in s and 'pio' in s and 'Personalizado' in s:
        lines[i] = b'                        <h2>Card\xc3\xa1pio Personalizado</h2>\n'
    if 's' in s and 'ries' in s and 'Descanso entre' in s:
        lines[i] = b'            <p style="color:var(--text-secondary);margin-bottom:20px;font-family:var(--font-heading);font-weight:700;">Descanso entre s\xc3\xa9ries</p>\n'
    if 'Prote' in s and 'nas (4' in s:
        lines[i] = b'                                    <p><strong style="color:var(--color-protein);">\xf0\x9f\xa5\xa9 Prote\xc3\xadnas (4 kcal/g):</strong> Essenciais para repara\xc3\xa7\xc3\xa3o e crescimento muscular. Consuma distribu\xc3\xaddas ao longo do dia.</p>\n'
    if 'Carboidratos (4' in s:
        lines[i] = b'                                    <p style="margin-top:8px;"><strong style="color:var(--color-carbs);">\xf0\x9f\x8d\x9a Carboidratos (4 kcal/g):</strong> Principal fonte de energia para treinos intensos. Priorize fontes complexas (arroz integral, batata doce, aveia).</p>\n'
    if 'Gorduras (9' in s:
        lines[i] = b'                                    <p style="margin-top:8px;"><strong style="color:var(--color-fats);">\xf0\x9f\xa5\x91 Gorduras (9 kcal/g):</strong> Fundamentais para produ\xc3\xa7\xc3\xa3o hormonal (testosterona). Fontes: azeite, abacate, castanhas, peixes.</p>\n'
    if 'M' in s and 'nimo 6' in s:
        lines[i] = b'                                <input type="password" id="input-new-password" placeholder="M\xc3\xadnimo 6 caracteres">\n'
    if 'Fogo' in s and '0 dias' in s:
        lines[i] = b'                            <div class="streak-badge">Fogo \xf0\x9f\x94\xa5 0 dias</div>\n'
    if 'Completa (Sem restr' in s:
        lines[i] = b'                                  <div class="diet-title">\xf0\x9f\x8d\x96 Completa (Sem restri\xc3\xa7\xc3\xb5es)</div>\n'
    if 'Vegetariana' in s and 'diet-title' in s:
        lines[i] = b'                                  <div class="diet-title">\xf0\x9f\xa5\x97 Vegetariana</div>\n'
    if 'Vegana' in s and 'diet-title' in s:
        lines[i] = b'                                  <div class="diet-title">\xf0\x9f\x8c\xb1 Vegana</div>\n'
    if 'Low Carb' in s and 'diet-title' in s:
        lines[i] = b'                                  <div class="diet-title">\xf0\x9f\xa5\x91 Low Carb</div>\n'

with open('templates/index.html', 'wb') as f:
    f.writelines(lines)
