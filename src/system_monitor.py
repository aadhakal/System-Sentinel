import json
import logging
import psutil
from datetime import datetime

class SystemMonitor:
    def __init__(self, config_path="config/monitoring_rules.json"):
        self.config = self._load_config(config_path)
        self.alerts = []
        self.use_real_metrics = True
        
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Config file not found: {config_path}")
            return {"thresholds": {"cpu_usage": 80, "memory_usage": 85, "disk_usage": 90}}
    
    def get_system_metrics(self):
        if self.use_real_metrics:
            # Get REAL system metrics
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            net_io = psutil.net_io_counters()
            process_count = len(psutil.pids())
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': cpu,
                'memory_usage': memory,
                'disk_usage': disk,
                'network_io': {'bytes_sent': net_io.bytes_sent, 'bytes_recv': net_io.bytes_recv},
                'process_count': process_count
            }
        else:
            # Fallback simulation
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': 45.0,
                'memory_usage': 60.0,
                'disk_usage': 55.0,
                'network_io': {'bytes_sent': 5000, 'bytes_recv': 5000},
                'process_count': 150
            }
    
    def check_thresholds(self, metrics):
        alerts = []
        thresholds = self.config['thresholds']
        
        if metrics['cpu_usage'] > thresholds['cpu_usage']:
            alerts.append(f"High CPU usage: {metrics['cpu_usage']:.1f}%")
        
        if metrics['memory_usage'] > thresholds['memory_usage']:
            alerts.append(f"High memory usage: {metrics['memory_usage']:.1f}%")
        
        if metrics['disk_usage'] > thresholds['disk_usage']:
            alerts.append(f"High disk usage: {metrics['disk_usage']:.1f}%")
        
        return alerts
    
    def monitor_system(self):
        metrics = self.get_system_metrics()
        alerts = self.check_thresholds(metrics)
        
        if alerts:
            self.alerts.extend(alerts)
            for alert in alerts:
                logging.warning(f"ALERT: {alert}")
        
        return metrics, alerts
    
    def get_current_metrics(self):
        return self.get_system_metrics()
    
    def get_process_info(self):
        if self.use_real_metrics:
            # Get REAL top processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            # Return top 10 by CPU
            return sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:10]
        else:
            return []