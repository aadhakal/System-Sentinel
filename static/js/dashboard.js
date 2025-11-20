let metricsChart;
const API_BASE = '';

async function fetchStats() {
    const response = await fetch(`${API_BASE}/api/stats`);
    const data = await response.json();
    
    document.getElementById('totalServers').textContent = data.total_servers;
    document.getElementById('activeServers').textContent = data.active_servers;
    document.getElementById('totalAlerts').textContent = data.total_alerts;
    document.getElementById('uptime').textContent = data.uptime_percentage + '%';
    
    // Show Docker status
    const dockerBadge = document.getElementById('dockerStatus');
    if (dockerBadge) {
        dockerBadge.textContent = data.docker_enabled ? '🐳 Docker Active' : '⚠️ Simulation Mode';
        dockerBadge.className = data.docker_enabled ? 'badge bg-success' : 'badge bg-warning';
    }
}

async function fetchServers() {
    const response = await fetch(`${API_BASE}/api/servers`);
    const data = await response.json();
    
    const tbody = document.getElementById('serversList');
    tbody.innerHTML = data.servers.map(server => {
        let buttons = '';
        const realBadge = server.real ? '<span class="badge bg-success" title="Real Docker Container">🐳</span>' : '<span class="badge bg-secondary" title="Simulated">💭</span>';
        
        if (server.status === 'running') {
            buttons = `
                <button class="btn btn-sm btn-warning" onclick="stopServer('${server.name}')" title="Stop">
                    <i class="bi bi-pause-circle"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="terminateServer('${server.name}')" title="Terminate">
                    <i class="bi bi-x-circle"></i>
                </button>
            `;
        } else if (server.status === 'stopped') {
            buttons = `
                <button class="btn btn-sm btn-success" onclick="restartServer('${server.name}')" title="Restart">
                    <i class="bi bi-play-circle"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="terminateServer('${server.name}')" title="Terminate">
                    <i class="bi bi-x-circle"></i>
                </button>
            `;
        } else if (server.status === 'terminated') {
            buttons = `
                <button class="btn btn-sm btn-dark" onclick="deleteServer('${server.name}')" title="Delete">
                    <i class="bi bi-trash"></i>
                </button>
            `;
        }
        
        return `
            <tr>
                <td>${server.name} ${realBadge}</td>
                <td>${server.ip || 'N/A'}</td>
                <td><span class="status-badge status-${server.status}">${server.status}</span></td>
                <td>${buttons}</td>
            </tr>
        `;
    }).join('');
}

async function deployServer() {
    const types = ['web_server', 'database_server', 'monitoring_server'];
    const type = types[Math.floor(Math.random() * types.length)];
    
    showNotification('🚀 Deploying server...', 'info', 'deploy-loading');
    const response = await fetch(`${API_BASE}/api/servers/deploy`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type})
    });
    const data = await response.json();
    
    if (data.success) {
        const badge = data.server.real ? '🐳' : '💭';
        showNotification(`${badge} Server deployed: <strong>${data.server.name}</strong>`, 'success', 'deploy-loading');
    }
    
    fetchServers();
    fetchStats();
}

async function stopServer(name) {
    const response = await fetch(`${API_BASE}/api/servers/${name}/stop`, {method: 'POST'});
    await response.json();
    showNotification(`⏸️ Server stopped: <strong>${name}</strong>`, 'warning');
    await fetchServers();
    await fetchStats();
}

async function restartServer(name) {
    const response = await fetch(`${API_BASE}/api/servers/${name}/restart`, {method: 'POST'});
    await response.json();
    showNotification(`▶️ Server restarted: <strong>${name}</strong>`, 'success');
    await fetchServers();
    await fetchStats();
}

async function terminateServer(name) {
    const response = await fetch(`${API_BASE}/api/servers/${name}/terminate`, {method: 'POST'});
    await response.json();
    showNotification(`🛑 Server terminated: <strong>${name}</strong>`, 'danger');
    await fetchServers();
    await fetchStats();
}

async function deleteServer(name) {
    const response = await fetch(`${API_BASE}/api/servers/${name}/delete`, {method: 'DELETE'});
    await response.json();
    showNotification(`🗑️ Server deleted: <strong>${name}</strong>`, 'dark');
    await fetchServers();
    await fetchStats();
}

function showNotification(message, type = 'success', id = null) {
    const alertsList = document.getElementById('alertsList');
    
    // Remove loading message if this is a completion
    if (id) {
        const loading = document.getElementById(id);
        if (loading) loading.remove();
    }
    
    const div = document.createElement('div');
    div.className = `alert alert-${type} alert-dismissible fade show mb-2`;
    div.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
    if (id) div.id = id;
    alertsList.insertBefore(div, alertsList.firstChild);
    
    // Manual close button handler
    const closeBtn = div.querySelector('.btn-close');
    closeBtn.addEventListener('click', () => div.remove());
    
    setTimeout(() => div.remove(), 15000);
}

async function createBackup() {
    showNotification('⏳ Creating backup...', 'info', 'backup-loading');
    const response = await fetch(`${API_BASE}/api/automation/backup`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({source: 'config'})
    });
    const data = await response.json();
    if (data.success) {
        const backupName = data.path.split('/').pop();
        showNotification(`✅ <strong>Backup Created!</strong><br>📁 ${backupName}<br><small>📂 Location: backups/ folder</small>`, 'success', 'backup-loading');
        console.log(`📦 Backup Details:\n  Folder: ${backupName}\n  Path: ${data.path}\n  Open backups/ folder to verify`);
    } else {
        showNotification('❌ Backup failed!', 'danger', 'backup-loading');
    }
}

async function runCleanup() {
    showNotification('⏳ Running cleanup...', 'info', 'cleanup-loading');
    const response = await fetch(`${API_BASE}/api/automation/cleanup`, {method: 'POST'});
    const data = await response.json();
    
    if (data.deleted_backups === 0 && data.rotated_logs === 0) {
        showNotification('✨ <strong>System is Clean!</strong><br>💡 No backups >3 hours old<br>💡 No logs >10MB<br><small>Nothing to delete - your system is optimized!</small>', 'success', 'cleanup-loading');
    } else {
        showNotification(`🧹 <strong>Cleanup Complete!</strong><br>📦 Deleted: ${data.deleted_backups} backups<br>📄 Rotated: ${data.rotated_logs} logs`, 'success', 'cleanup-loading');
    }
    console.log(`🧹 Cleanup Results:\n  Backups deleted: ${data.deleted_backups}\n  Logs rotated: ${data.rotated_logs}`);
}

async function downloadReport() {
    const format = document.getElementById('reportFormat').value;
    const formatLabels = {html: 'HTML', pdf: 'PDF', json: 'JSON', csv: 'CSV'};
    
    showNotification(`📊 Generating ${formatLabels[format]} report...`, 'info', 'report-loading');
    try {
        const response = await fetch(`${API_BASE}/api/report/generate?format=${format}`);
        const data = await response.json();
        
        if (data.success) {
            showNotification(`✅ <strong>${formatLabels[format]} Report Generated!</strong><br>📥 Downloading...`, 'success', 'report-loading');
            window.location.href = `${API_BASE}/api/report/download/${data.filename}`;
        } else {
            const errorMsg = data.error.includes('reportlab') ? 
                '❌ PDF requires reportlab. Run: <code>pip install reportlab</code>' : 
                '❌ Report generation failed!';
            showNotification(errorMsg, 'danger', 'report-loading');
        }
    } catch (error) {
        showNotification('❌ Error generating report!', 'danger', 'report-loading');
    }
}

async function updateMetrics() {
    const response = await fetch(`${API_BASE}/api/metrics`);
    const data = await response.json();
    
    if (data.alerts.length > 0) {
        const alertsList = document.getElementById('alertsList');
        data.alerts.forEach(alert => {
            const div = document.createElement('div');
            div.className = 'alert-item';
            div.textContent = alert;
            alertsList.insertBefore(div, alertsList.firstChild);
        });
    }
}

async function initChart() {
    const response = await fetch(`${API_BASE}/api/metrics/history?limit=20`);
    const data = await response.json();
    
    const ctx = document.getElementById('metricsChart').getContext('2d');
    metricsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.history.map((_, i) => i),
            datasets: [
                {
                    label: 'CPU Usage (%)',
                    data: data.history.map(m => m.cpu_usage),
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                },
                {
                    label: 'Memory Usage (%)',
                    data: data.history.map(m => m.memory_usage),
                    borderColor: 'rgb(54, 162, 235)',
                    tension: 0.1
                },
                {
                    label: 'Disk Usage (%)',
                    data: data.history.map(m => m.disk_usage),
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time (last 20 samples)'
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Usage (%)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

async function updateChart() {
    const response = await fetch(`${API_BASE}/api/metrics/history?limit=20`);
    const data = await response.json();
    
    metricsChart.data.labels = data.history.map((_, i) => i);
    metricsChart.data.datasets[0].data = data.history.map(m => m.cpu_usage);
    metricsChart.data.datasets[1].data = data.history.map(m => m.memory_usage);
    metricsChart.data.datasets[2].data = data.history.map(m => m.disk_usage);
    
    // Update legend with current values
    if (data.history.length > 0) {
        const latest = data.history[data.history.length - 1];
        metricsChart.data.datasets[0].label = `CPU Usage: ${latest.cpu_usage.toFixed(1)}%`;
        metricsChart.data.datasets[1].label = `Memory Usage: ${latest.memory_usage.toFixed(1)}%`;
        metricsChart.data.datasets[2].label = `Disk Usage: ${latest.disk_usage.toFixed(1)}%`;
    }
    
    metricsChart.update();
}

document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    fetchServers();
    initChart();
    
    setInterval(() => {
        updateMetrics();
        updateChart();
        fetchStats();
    }, 5000);
});
