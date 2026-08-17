import os

path = r'C:\Users\Usuario\.gemini\antigravity\scratch\VULCAN.01\templates\admin.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

old_render = """        function renderAdmin() {
            const total = usersData.length;
            const blocked = usersData.filter(u => u.is_blocked).length;
            document.getElementById('kpi-total-users').textContent = total;
            document.getElementById('kpi-blocked').textContent = blocked;
            document.getElementById('kpi-avg-time').textContent = '24 min/dia';

            const tbody = document.getElementById('admin-users-table');
            tbody.innerHTML = '';
            
            usersData.forEach(u => {
                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #242431';
                
                const statusHtml = u.is_blocked 
                    ? `<span class="badge inactive">Bloqueado (${u.blocked_by || 'Auto'})</span>`
                    : `<span class="badge active">Ativo</span>`;
                    
                const btnHtml = u.is_blocked
                    ? `<button style="padding:5px 10px; background:#28a745; color:#fff; border:none; border-radius:4px; cursor:pointer;" onclick="toggleBlock('${u.email}')">Desbloquear</button>`
                    : `<button style="padding:5px 10px; background:#dc3545; color:#fff; border:none; border-radius:4px; cursor:pointer;" onclick="toggleBlock('${u.email}')">Bloquear</button>`;

                tr.innerHTML = `
                    <td style="padding:10px;">
                        <strong>${u.name}</strong><br>
                        <small style="color:#9ea0ab;">${u.email}</small>
                    </td>
                    <td style="padding:10px;">${new Date(u.created_at).toLocaleDateString()}</td>
                    <td style="padding:10px;">${statusHtml}</td>
                    <td style="padding:10px;">${btnHtml}</td>
                `;
                tbody.appendChild(tr);
            });

            renderChart();
        }"""

new_render = """        function formatDateTime(isoString) {
            if (!isoString) return '<span style="color:#ff4757;">Ainda não acessou</span>';
            const d = new Date(isoString);
            return d.toLocaleDateString('pt-BR') + ' às ' + d.toLocaleTimeString('pt-BR');
        }

        function renderAdmin() {
            const total = usersData.length;
            const blocked = usersData.filter(u => u.is_blocked).length;
            document.getElementById('kpi-total-users').textContent = total;
            document.getElementById('kpi-blocked').textContent = blocked;
            document.getElementById('kpi-avg-time').textContent = '24 min/dia';

            const tbody = document.getElementById('admin-users-table');
            tbody.innerHTML = '';
            
            usersData.forEach(u => {
                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #242431';
                
                const statusHtml = u.is_blocked 
                    ? `<span class="badge inactive">Bloqueado (${u.blocked_by || 'Auto'})</span>`
                    : `<span class="badge active">Ativo</span>`;
                    
                const btnHtml = u.is_blocked
                    ? `<button style="padding:5px 10px; background:#28a745; color:#fff; border:none; border-radius:4px; cursor:pointer;" onclick="toggleBlock('${u.email}')">Desbloquear</button>`
                    : `<button style="padding:5px 10px; background:#dc3545; color:#fff; border:none; border-radius:4px; cursor:pointer;" onclick="toggleBlock('${u.email}')">Bloquear</button>`;

                tr.innerHTML = `
                    <td style="padding:10px;">
                        <strong>${u.name}</strong><br>
                        <small style="color:#9ea0ab;">${u.email}</small>
                    </td>
                    <td style="padding:10px;">
                        <small style="color:#9ea0ab;">Criado em: ${new Date(u.created_at).toLocaleDateString('pt-BR')}</small><br>
                        <strong>Último acesso:</strong> ${formatDateTime(u.last_active)}
                    </td>
                    <td style="padding:10px;">${statusHtml}</td>
                    <td style="padding:10px;">${btnHtml}</td>
                `;
                tbody.appendChild(tr);
            });

            renderChart();
        }"""

html = html.replace(old_render, new_render)

old_toggle = """        async function toggleBlock(targetEmail) {
            try {
                const res = await fetch('/api/admin/toggle-block', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({admin_email: adminEmail, admin_password: adminPass, target_email: targetEmail})
                });
                const data = await res.json();
                if(res.ok) {
                    const u = usersData.find(x => x.email === targetEmail);
                    u.is_blocked = data.is_blocked;
                    u.blocked_by = data.is_blocked ? 'Admin' : null;
                    renderAdmin();
                } else {
                    alert('Erro: ' + data.error);
                }
            } catch(e) {
                alert('Erro de conexǜo');
            }
        }"""

new_toggle = """        async function toggleBlock(targetEmail) {
            try {
                const res = await fetch('/api/admin/toggle-block', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({admin_email: adminEmail, admin_password: adminPass, target_email: targetEmail})
                });
                const data = await res.json();
                if(res.ok) {
                    const u = usersData.find(x => x.email === targetEmail);
                    u.is_blocked = !u.is_blocked; // flip manual logic
                    u.blocked_by = u.is_blocked ? 'Admin' : null;
                    renderAdmin();
                } else {
                    alert('Erro: ' + data.error);
                }
            } catch(e) {
                alert('Erro de conexão');
            }
        }"""

html = html.replace(old_toggle, new_toggle)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
