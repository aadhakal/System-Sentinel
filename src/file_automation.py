import os
import shutil
import logging
from datetime import datetime, timedelta
import glob

class FileAutomation:
    def __init__(self, backup_dir="backups", logs_dir="logs"):
        self.backup_dir = backup_dir
        self.logs_dir = logs_dir
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)
    
    def backup_directory(self, source_dir, backup_name=None):
        """Create a backup of a directory"""
        if not os.path.exists(source_dir):
            logging.error(f"Source directory not found: {source_dir}")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = backup_name or os.path.basename(source_dir)
        backup_path = os.path.join(self.backup_dir, f"{backup_name}_{timestamp}")
        
        try:
            shutil.copytree(source_dir, backup_path)
            logging.info(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logging.error(f"Backup failed: {e}")
            return None
    
    def cleanup_old_backups(self, hours=3):
        """Delete backups older than specified hours"""
        cutoff_date = datetime.now() - timedelta(hours=hours)
        deleted_count = 0
        
        for backup in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, backup)
            if os.path.isdir(backup_path):
                mtime = datetime.fromtimestamp(os.path.getmtime(backup_path))
                if mtime < cutoff_date:
                    try:
                        shutil.rmtree(backup_path)
                        deleted_count += 1
                        logging.info(f"Deleted old backup: {backup}")
                    except Exception as e:
                        logging.error(f"Failed to delete {backup}: {e}")
        
        logging.info(f"Cleaned up {deleted_count} old backups")
        return deleted_count
    
    def rotate_logs(self, max_size_mb=10):
        """Rotate log files larger than max_size_mb"""
        rotated_count = 0
        max_size_bytes = max_size_mb * 1024 * 1024
        
        for log_file in glob.glob(os.path.join(self.logs_dir, "*.log")):
            try:
                if os.path.getsize(log_file) > max_size_bytes:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    rotated_name = f"{log_file}.{timestamp}"
                    shutil.move(log_file, rotated_name)
                    rotated_count += 1
                    logging.info(f"Rotated log: {log_file}")
            except Exception as e:
                logging.error(f"Failed to rotate {log_file}: {e}")
        
        return rotated_count
    
    def cleanup_temp_files(self, directory, pattern="*.tmp"):
        """Delete temporary files matching pattern"""
        deleted_count = 0
        
        for temp_file in glob.glob(os.path.join(directory, pattern)):
            try:
                os.remove(temp_file)
                deleted_count += 1
                logging.info(f"Deleted temp file: {temp_file}")
            except Exception as e:
                logging.error(f"Failed to delete {temp_file}: {e}")
        
        return deleted_count
    
    def get_directory_size(self, directory):
        """Calculate total size of directory in MB"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            logging.error(f"Failed to calculate size: {e}")
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        for backup in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, backup)
            if os.path.isdir(backup_path):
                size_mb = self.get_directory_size(backup_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(backup_path))
                backups.append({
                    'name': backup,
                    'path': backup_path,
                    'size_mb': round(size_mb, 2),
                    'created': mtime.isoformat()
                })
        return sorted(backups, key=lambda x: x['created'], reverse=True)
