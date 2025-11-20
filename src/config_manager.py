import json
import os
import logging
from datetime import datetime

class ConfigManager:
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        self.configs = {}
        self.load_all_configs()
    
    def load_all_configs(self):
        if not os.path.exists(self.config_dir):
            logging.error(f"Config directory not found: {self.config_dir}")
            return
        
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                config_name = filename[:-5]  # Remove .json extension
                self.load_config(config_name)
    
    def load_config(self, config_name):
        config_path = os.path.join(self.config_dir, f"{config_name}.json")
        try:
            with open(config_path, 'r') as f:
                self.configs[config_name] = json.load(f)
            logging.info(f"Loaded config: {config_name}")
        except FileNotFoundError:
            logging.error(f"Config file not found: {config_path}")
    
    def get_config(self, config_name):
        return self.configs.get(config_name, {})
    
    def update_config(self, config_name, updates):
        if config_name in self.configs:
            self.configs[config_name].update(updates)
            self.save_config(config_name)
            logging.info(f"Updated config: {config_name}")
        else:
            logging.error(f"Config not found: {config_name}")
    
    def save_config(self, config_name):
        config_path = os.path.join(self.config_dir, f"{config_name}.json")
        try:
            with open(config_path, 'w') as f:
                json.dump(self.configs[config_name], f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save config {config_name}: {e}")
    
    def backup_configs(self):
        backup_dir = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        for config_name, config_data in self.configs.items():
            backup_path = os.path.join(backup_dir, f"{config_name}.json")
            with open(backup_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        
        logging.info(f"Configs backed up to: {backup_dir}")
        return backup_dir