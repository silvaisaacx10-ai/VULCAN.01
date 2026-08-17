import os
import re

html_path = r'C:\Users\Usuario\.gemini\antigravity\scratch\VULCAN.01\templates\admin.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

new_render_admin = """
        function formatDateTime(isoString) {
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
        }

        async function toggleBlock(targetEmail) {
            try {
                const res = await fetch('/api/admin/toggle-block', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({admin_email: adminEmail, admin_password: adminPass, target_email: targetEmail})
                });
                const data = await res.json();
                if(res.ok) {
                    const u = usersData.find(x => x.email === targetEmail);
                    u.is_blocked = !u.is_blocked; // flip the logic manually since backend doesn't return it cleanly
                    u.blocked_by = u.is_blocked ? 'Admin' : null;
                    renderAdmin();
                } else {
                    alert('Erro: ' + data.error);
                }
            } catch(e) {
                alert('Erro de conexão');
            }
        }
"""

html = re.sub(r'function renderAdmin\(\) \{.*?\n        \} catch\(e\) \{\n                alert\(\'Erro de conexão\'\);\n            \}\n        \}', new_render_admin, html, flags=re.DOTALL)

# Add headers change in the html table as well
new_table_head = """
                                <thead>
                                    <tr style="border-bottom:1px solid #242431;">
                                        <th style="padding:10px;">Nome / Email</th>
                                        <th style="padding:10px;">Acesso e Cadastro</th>
                                        <th style="padding:10px;">Status</th>
                                        <th style="padding:10px;">Ação</th>
                                    </tr>
                                </thead>
"""

html = re.sub(r'<thead>.*?</thead>', new_table_head, html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Admin panel patched.")
