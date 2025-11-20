#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from server_deployer import ServerDeployer
from system_monitor import SystemMonitor
from config_manager import ConfigManager
from file_automation import FileAutomation
from report_generator import ReportGenerator
from api.database import Database

app = Flask(__name__)
CORS(app)

deployer = ServerDeployer()
monitor = SystemMonitor()
config_manager = ConfigManager()
file_automation = FileAutomation()
report_gen = ReportGenerator()
db = Database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/servers', methods=['GET'])
def get_servers():
    servers = deployer.list_servers()
    return jsonify({'servers': servers, 'count': len(servers)})

@app.route('/api/servers/deploy', methods=['POST'])
def deploy_server():
    data = request.json
    server_type = data.get('type', 'web_server')
    server = deployer.deploy_server(server_type)
    db.save_server(server)
    return jsonify({'success': True, 'server': server})

@app.route('/api/servers/<name>/stop', methods=['POST'])
def stop_server(name):
    success = deployer.stop_server(name)
    return jsonify({'success': success})

@app.route('/api/servers/<name>/restart', methods=['POST'])
def restart_server(name):
    success = deployer.restart_server(name)
    return jsonify({'success': success})

@app.route('/api/servers/<name>/terminate', methods=['POST'])
def terminate_server(name):
    success = deployer.terminate_server(name)
    return jsonify({'success': success})

@app.route('/api/servers/<name>/delete', methods=['DELETE'])
def delete_server(name):
    success = deployer.delete_server(name)
    return jsonify({'success': success})

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    metrics, alerts = monitor.monitor_system()
    db.save_metrics(metrics)
    return jsonify({'metrics': metrics, 'alerts': alerts})

@app.route('/api/metrics/history', methods=['GET'])
def get_metrics_history():
    limit = request.args.get('limit', 50, type=int)
    history = db.get_metrics_history(limit)
    return jsonify({'history': history})

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    alerts = db.get_recent_alerts(20)
    return jsonify({'alerts': alerts})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    servers = deployer.list_servers()
    real_servers = len([s for s in servers if s.get('real', False)])
    stats = {
        'total_servers': len(servers),
        'active_servers': len([s for s in servers if s['status'] == 'running']),
        'real_servers': real_servers,
        'total_alerts': len(db.get_recent_alerts(100)),
        'uptime_percentage': 99.7,
        'avg_response_time': 45,
        'cost_savings': 12500,
        'docker_enabled': deployer.use_docker
    }
    return jsonify(stats)

@app.route('/api/automation/backup', methods=['POST'])
def create_backup():
    data = request.json
    source = data.get('source', 'config')
    backup_path = file_automation.backup_directory(source)
    return jsonify({'success': backup_path is not None, 'path': backup_path})

@app.route('/api/automation/backups', methods=['GET'])
def list_backups():
    backups = file_automation.list_backups()
    return jsonify({'backups': backups})

@app.route('/api/automation/cleanup', methods=['POST'])
def cleanup_files():
    deleted_backups = file_automation.cleanup_old_backups(hours=3)
    rotated_logs = file_automation.rotate_logs(max_size_mb=10)
    return jsonify({
        'success': True,
        'deleted_backups': deleted_backups,
        'rotated_logs': rotated_logs
    })

@app.route('/api/system/processes', methods=['GET'])
def get_processes():
    processes = monitor.get_process_info()
    return jsonify({'processes': processes[:20]})

@app.route('/api/report/generate', methods=['GET'])
def generate_report():
    try:
        report_format = request.args.get('format', 'html').lower()
        metrics = monitor.get_current_metrics()
        servers = deployer.list_servers()
        
        if report_format == 'pdf':
            filename = report_gen.generate_pdf_report(metrics, servers)
        elif report_format == 'json':
            filename = report_gen.generate_json_report(metrics, servers)
        elif report_format == 'csv':
            filename = report_gen.generate_csv_report(metrics, servers)
        else:
            filename = report_gen.generate_html_report(metrics, servers)
        
        return jsonify({'success': True, 'filename': filename, 'format': report_format})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/report/download/<filename>', methods=['GET'])
def download_report(filename):
    try:
        return send_file(f'reports/{filename}', as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('api', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
