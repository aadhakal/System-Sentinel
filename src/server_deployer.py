import json
import logging
import time
import subprocess
from datetime import datetime

class ServerDeployer:
    def __init__(self, config_path="config/server_templates.json"):
        self.config_path = config_path
        self.templates = self._load_templates()
        self.deployed_servers = []
        self.use_docker = self._check_docker()
        if self.use_docker:
            self._load_existing_containers()
        
    def _check_docker(self):
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, check=True)
            logging.info("Docker is available - using real containers")
            return True
        except:
            logging.warning("Docker not available - using simulation mode")
            return False
    
    def _load_existing_containers(self):
        """Load existing containers that match our naming pattern"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', 'name=web_server', '--filter', 'name=database_server', 
                 '--filter', 'name=monitoring_server', '--format', '{{.Names}}|{{.ID}}|{{.Status}}|{{.Image}}'],
                capture_output=True, text=True, check=True
            )
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split('|')
                if len(parts) >= 4:
                    name, container_id, status, image = parts[0], parts[1], parts[2], parts[3]
                    
                    # Determine server type from name
                    server_type = 'web_server' if 'web_server' in name else \
                                 'database_server' if 'database_server' in name else 'monitoring_server'
                    
                    # Determine status
                    if 'Up' in status:
                        server_status = 'running'
                    elif 'Exited' in status:
                        server_status = 'stopped'
                    else:
                        server_status = 'terminated'
                    
                    server = {
                        'name': name,
                        'container_id': container_id,
                        'status': server_status,
                        'ip': self._get_container_ip(container_id) if server_status == 'running' else 'N/A',
                        'deployed_at': datetime.now().isoformat(),
                        'real': True,
                        'image': image
                    }
                    self.deployed_servers.append(server)
                    logging.info(f"Loaded existing container: {name} ({server_status})")
            
            if self.deployed_servers:
                logging.info(f"Loaded {len(self.deployed_servers)} existing containers")
        except Exception as e:
            logging.error(f"Failed to load existing containers: {e}")
    
    def _load_templates(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Template file not found: {self.config_path}")
            return {}
    
    def deploy_server(self, server_type, server_id=None):
        if server_type not in self.templates:
            raise ValueError(f"Unknown server type: {server_type}")
        
        template = self.templates[server_type].copy()
        server_id = server_id or int(time.time())
        template['name'] = template['name'].format(id=server_id)
        template['deployed_at'] = datetime.now().isoformat()
        template['status'] = 'deploying'
        
        if self.use_docker:
            # Deploy REAL Docker container
            container_id = self._deploy_docker_container(template['name'], server_type)
            if container_id:
                template['container_id'] = container_id
                template['status'] = 'running'
                template['ip'] = self._get_container_ip(container_id)
                template['real'] = True
                logging.info(f"Real container {template['name']} deployed: {container_id[:12]}")
            else:
                template['status'] = 'failed'
                template['real'] = False
        else:
            # Simulation fallback
            logging.info(f"Simulating deployment of {template['name']}...")
            time.sleep(2)
            template['status'] = 'running'
            template['ip'] = f"192.168.1.{len(self.deployed_servers) + 10}"
            template['real'] = False
        
        self.deployed_servers.append(template)
        return template
    
    def _deploy_docker_container(self, name, server_type):
        try:
            # Map server types to Docker images
            image_map = {
                'web_server': 'nginx:alpine',
                'database_server': 'redis:alpine',
                'monitoring_server': 'busybox:latest'
            }
            image = image_map.get(server_type, 'busybox:latest')
            
            # Run container
            result = subprocess.run(
                ['docker', 'run', '-d', '--name', name, image, 'sleep', '3600'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to deploy container: {e.stderr}")
            return None
    
    def _get_container_ip(self, container_id):
        try:
            result = subprocess.run(
                ['docker', 'inspect', '-f', '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}', container_id],
                capture_output=True, text=True, check=True
            )
            ip = result.stdout.strip()
            return ip if ip else 'N/A'
        except:
            return 'N/A'
    
    def get_server_status(self, server_name):
        for server in self.deployed_servers:
            if server['name'] == server_name:
                return server
        return None
    
    def list_servers(self):
        return self.deployed_servers
    
    def stop_server(self, server_name):
        for server in self.deployed_servers:
            if server['name'] == server_name and server['status'] == 'running':
                # Update status immediately
                server['status'] = 'stopped'
                if self.use_docker and server.get('container_id'):
                    try:
                        # Use timeout to avoid long waits
                        subprocess.run(['docker', 'stop', '-t', '2', server['container_id']], 
                                     check=True, capture_output=True, timeout=5)
                        logging.info(f"Real container {server_name} stopped")
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                        logging.error(f"Failed to stop container {server_name}")
                return True
        return False
    
    def restart_server(self, server_name):
        for server in self.deployed_servers:
            if server['name'] == server_name and server['status'] == 'stopped':
                if self.use_docker and server.get('container_id'):
                    try:
                        subprocess.run(['docker', 'start', server['container_id']], check=True, capture_output=True)
                        logging.info(f"Real container {server_name} restarted")
                    except subprocess.CalledProcessError:
                        logging.error(f"Failed to restart container {server_name}")
                server['status'] = 'running'
                return True
        return False
    
    def terminate_server(self, server_name):
        for server in self.deployed_servers:
            if server['name'] == server_name:
                if self.use_docker and server.get('container_id'):
                    try:
                        subprocess.run(['docker', 'stop', server['container_id']], check=True, capture_output=True)
                        logging.info(f"Real container {server_name} terminated")
                    except subprocess.CalledProcessError:
                        pass
                server['status'] = 'terminated'
                return True
        return False
    
    def delete_server(self, server_name):
        for server in self.deployed_servers:
            if server['name'] == server_name:
                if self.use_docker and server.get('container_id'):
                    try:
                        subprocess.run(['docker', 'rm', '-f', server['container_id']], check=True, capture_output=True)
                        logging.info(f"Real container {server_name} deleted")
                    except subprocess.CalledProcessError:
                        logging.error(f"Failed to delete container {server_name}")
                self.deployed_servers.remove(server)
                return True
        return False