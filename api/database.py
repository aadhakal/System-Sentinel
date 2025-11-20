import sqlite3
import json
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='data/infrastructure.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS servers
                     (id INTEGER PRIMARY KEY, name TEXT, type TEXT, 
                      status TEXT, ip TEXT, deployed_at TEXT, data TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS metrics
                     (id INTEGER PRIMARY KEY, timestamp TEXT, 
                      cpu_usage REAL, memory_usage REAL, disk_usage REAL, data TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS alerts
                     (id INTEGER PRIMARY KEY, timestamp TEXT, 
                      severity TEXT, message TEXT)''')
        conn.commit()
        conn.close()
    
    def save_server(self, server):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO servers (name, type, status, ip, deployed_at, data)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (server['name'], server.get('type', 'unknown'), server['status'],
                   server.get('ip', ''), server['deployed_at'], json.dumps(server)))
        conn.commit()
        conn.close()
    
    def save_metrics(self, metrics):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO metrics (timestamp, cpu_usage, memory_usage, disk_usage, data)
                     VALUES (?, ?, ?, ?, ?)''',
                  (metrics['timestamp'], metrics['cpu_usage'], metrics['memory_usage'],
                   metrics['disk_usage'], json.dumps(metrics)))
        conn.commit()
        conn.close()
    
    def get_metrics_history(self, limit=50):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT data FROM metrics ORDER BY id DESC LIMIT ?', (limit,))
        rows = c.fetchall()
        conn.close()
        return [json.loads(row[0]) for row in rows][::-1]
    
    def get_recent_alerts(self, limit=20):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT timestamp, severity, message FROM alerts ORDER BY id DESC LIMIT ?', (limit,))
        rows = c.fetchall()
        conn.close()
        return [{'timestamp': r[0], 'severity': r[1], 'message': r[2]} for r in rows]
