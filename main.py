#!/usr/bin/env python3
import argparse
import logging
import schedule
import time
from datetime import datetime
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from server_deployer import ServerDeployer
from system_monitor import SystemMonitor
from config_manager import ConfigManager
from report_generator import ReportGenerator

class InfrastructureAutomation:
    def __init__(self):
        self.setup_logging()
        self.deployer = ServerDeployer()
        self.monitor = SystemMonitor()
        self.config_manager = ConfigManager()
        self.report_generator = ReportGenerator()
        self.metrics_history = []
        self.alerts_history = []
    
    def setup_logging(self):
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/automation_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
    
    def deploy_infrastructure(self):
        logging.info("Starting infrastructure deployment...")
        
        # Deploy different server types
        servers = [
            self.deployer.deploy_server('web_server'),
            self.deployer.deploy_server('database_server'),
            self.deployer.deploy_server('monitoring_server')
        ]
        
        logging.info(f"Deployed {len(servers)} servers successfully")
        return servers
    
    def monitor_systems(self):
        logging.info("Running system monitoring...")
        metrics, alerts = self.monitor.monitor_system()
        
        self.metrics_history.append(metrics)
        self.alerts_history.extend(alerts)
        
        # Keep only last 100 metrics
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        return metrics, alerts
    
    def generate_reports(self):
        logging.info("Generating reports...")
        
        # System performance report
        system_report = self.report_generator.generate_system_report(
            self.metrics_history, self.alerts_history
        )
        
        # Server inventory report
        servers = self.deployer.list_servers()
        if servers:
            inventory_report, summary = self.report_generator.generate_server_inventory_report(servers)
            logging.info(f"Server inventory: {summary}")
        
        # Performance chart
        if self.metrics_history:
            chart_path = self.report_generator.create_performance_chart(self.metrics_history)
            if chart_path:
                logging.info(f"Performance chart saved: {chart_path}")
        
        logging.info(f"System report saved: {system_report}")
    
    def run_scheduled_tasks(self):
        # Schedule monitoring every 5 minutes
        schedule.every(5).minutes.do(self.monitor_systems)
        
        # Schedule reports every hour
        schedule.every().hour.do(self.generate_reports)
        
        logging.info("Scheduled tasks configured. Running...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def run_demo(self):
        logging.info("Running System Sentinel demo...")
        
        # Deploy infrastructure
        servers = self.deploy_infrastructure()
        
        # Run monitoring for demo
        for i in range(5):
            metrics, alerts = self.monitor_systems()
            logging.info(f"Monitoring cycle {i+1}: CPU {metrics['cpu_usage']:.1f}%, Memory {metrics['memory_usage']:.1f}%")
            time.sleep(2)
        
        # Generate reports
        self.generate_reports()
        
        logging.info("Demo completed successfully!")

def main():
    parser = argparse.ArgumentParser(description=' System Sentinel')
    parser.add_argument('--deploy', action='store_true', help='Deploy infrastructure')
    parser.add_argument('--monitor', action='store_true', help='Start monitoring')
    parser.add_argument('--report', action='store_true', help='Generate reports')
    parser.add_argument('--schedule', action='store_true', help='Run scheduled tasks')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    
    args = parser.parse_args()
    automation = InfrastructureAutomation()
    
    if args.demo:
        automation.run_demo()
    elif args.schedule:
        automation.run_scheduled_tasks()
    else:
        if args.deploy:
            automation.deploy_infrastructure()
        if args.monitor:
            automation.monitor_systems()
        if args.report:
            automation.generate_reports()
        
        if not any([args.deploy, args.monitor, args.report]):
            automation.run_demo()

if __name__ == "__main__":
    main()