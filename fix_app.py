with open('static/js/app.js', 'rb') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if b'// INICIALIZA' in line:
        lines[i] = b'// INICIALIZA\xc3\x87\xc3\x83O DO APP\n'
    if b'// AUTENTICA' in line:
        lines[i] = b'// AUTENTICA\xc3\x87\xc3\x83O\n'
    if b'// VALIDA' in line:
        lines[i] = b'// VALIDA\xc3\x87\xc3\x83O FRONTEND\n'
    if b'// HIDRATA' in line:
        lines[i] = b'// HIDRATA\xc3\x87\xc3\x83O (RASTREADOR DE \xc3\x81GUA)\n'
    if b'// GERADOR E A' in line and b'DIETA' in line:
        lines[i] = b'// GERADOR E A\xc3\x87\xc3\x95ES DA ABA: DIETA\n'
    if b'// GERADOR E A' in line and b'TREINO' in line:
        lines[i] = b'// GERADOR E A\xc3\x87\xc3\x95ES DA ABA: TREINO\n'
    if b'// NAVEGA' in line:
        lines[i] = b'// NAVEGA\xc3\x87\xc3\x83O DE ABAS\n'
    if b'// MICRO-INTERA' in line:
        lines[i] = b'// MICRO-INTERA\xc3\x87\xc3\x95ES: ANIMA\xc3\x87\xc3\x83O DE CONFETES\n'
    if b'badge.innerHTML =' in line and b'Fogo' in line:
        lines[i] = b'        badge.innerHTML = `Fogo \xf0\x9f\x94\xa5 ${streak} dias`;\n'
    if b'showToast' in line and b'Parab' in line:
        lines[i] = b"            showToast('Parab\xc3\xa9ns! Voc\xc3\xaa completou todas as miss\xc3\xb5es do dia! \xf0\x9f\x8f\x86', 'success');\n"
    if b'<h2 style' in line and b'Lista de Compras' in line:
        lines[i] = b'            <h2 style="font-family:var(--font-heading);">\xf0\x9f\x9b\x92 Lista de Compras (7 Dias)</h2>\n'
    if b'<h2 style' in line and b'Substituir Alimento' in line:
        lines[i] = b'            <h2 style="font-family:var(--font-heading);">\xf0\x9f\x94\x84 Substituir Alimento</h2>\n'
    if b'showToast' in line and b'precisa estar logado' in line:
        lines[i] = b"                showToast('Voc\xc3\xaa precisa estar logado!', 'error');\n"

with open('static/js/app.js', 'wb') as f:
    f.writelines(lines)
