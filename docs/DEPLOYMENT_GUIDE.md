# Deployment Guide

## Prerequisites

### System Requirements
- **OS:** macOS, Linux, or Windows
- **Python:** 3.6 or higher
- **Docker:** Optional (for real container management)
- **RAM:** 2GB minimum
- **Disk:** 500MB free space

### Software Dependencies
- Python 3.6+
- pip (Python package manager)
- Git (for cloning repository)
- Docker Desktop (optional)

---

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/infrastructure-automation.git
cd infrastructure-automation
```

### 2. Install Dependencies
```bash
# Automatic installation (recommended)
./START.sh

# Manual installation
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
# Check Python version
python --version  # Should be 3.6+

# Check installed packages
pip list

# Test Docker (optional)
docker --version
docker ps
```

---

## Configuration

### 1. Server Templates
Edit `config/server_templates.json`:
```json
{
  "web_server": {
    "type": "web_server",
    "image": "nginx:alpine",
    "name": "web_server_{id}"
  }
}
```

### 2. Monitoring Rules
Edit `config/monitoring_rules.json`:
```json
{
  "thresholds": {
    "cpu_usage": 80,
    "memory_usage": 85,
    "disk_usage": 90
  }
}
```

### 3. Environment Variables (Optional)
Create `.env` file:
```bash
FLASK_ENV=production
FLASK_PORT=5000
LOG_LEVEL=INFO
```

---

## Deployment Options

### Option 1: Web Dashboard (Recommended)
```bash
# Start the web application
./START.sh

# Access dashboard
open http://localhost:5000
```

**Features:**
- Real-time monitoring
- One-click operations
- Visual reports
- Activity logs

### Option 2: CLI Tool
```bash
# Run demo
python main.py --demo

# Deploy infrastructure
python main.py --deploy

# Start monitoring
python main.py --monitor

# Generate reports
python main.py --report

# Run scheduled tasks
python main.py --schedule
```

### Option 3: API Integration
```bash
# Start Flask server
python app.py

# Use REST API
curl http://localhost:5000/api/servers
curl -X POST http://localhost:5000/api/servers/deploy
```

---

## Testing Procedures

### 1. Unit Testing
```bash
# Test system monitor
python -c "from src.system_monitor import SystemMonitor; m = SystemMonitor(); print(m.get_system_metrics())"

# Test file automation
python -c "from src.file_automation import FileAutomation; f = FileAutomation(); print(f.list_backups())"
```

### 2. Integration Testing
```bash
# Test full workflow
1. Start dashboard: ./START.sh
2. Deploy container: Click "Deploy" button
3. Verify: docker ps -a
4. Create backup: Click "Create Backup"
5. Verify: ls backups/
6. Generate report: Select format, click "Download Report"
```

### 3. Load Testing
```bash
# Deploy multiple containers
for i in {1..10}; do
  curl -X POST http://localhost:5000/api/servers/deploy \
    -H "Content-Type: application/json" \
    -d '{"type":"web_server"}'
done
```

---

## Scheduling Automation

### Option 1: Built-in Scheduler
```bash
# Run with schedule
python main.py --schedule

# Monitors every 5 minutes
# Reports every hour
```

### Option 2: Cron (Linux/macOS)
```bash
# Edit crontab
crontab -e

# Add entries
*/5 * * * * cd /path/to/infrastructure-automation && python main.py --monitor
0 * * * * cd /path/to/infrastructure-automation && python main.py --report
0 0 * * * cd /path/to/infrastructure-automation && python -c "from src.file_automation import FileAutomation; FileAutomation().cleanup_old_backups()"
```

### Option 3: Task Scheduler (Windows)
```powershell
# Create scheduled task
schtasks /create /tn "InfraMonitor" /tr "python C:\path\to\main.py --monitor" /sc minute /mo 5
schtasks /create /tn "InfraReport" /tr "python C:\path\to\main.py --report" /sc hourly
```

---

## Maintenance Procedures

### Daily Tasks
- ✅ Check dashboard for alerts
- ✅ Review activity log
- ✅ Verify container status

### Weekly Tasks
- ✅ Review generated reports
- ✅ Check backup storage
- ✅ Update dependencies: `pip install -r requirements.txt --upgrade`

### Monthly Tasks
- ✅ Review logs: `tail -100 logs/*.log`
- ✅ Clean old reports: `rm reports/*_old.html`
- ✅ Update documentation
- ✅ Security audit

### Quarterly Tasks
- ✅ Performance review
- ✅ Capacity planning
- ✅ Feature requests
- ✅ Code refactoring

---

## Troubleshooting

### Issue: Flask won't start
```bash
# Check port availability
lsof -i :5000

# Kill existing process
kill -9 $(lsof -t -i:5000)

# Restart
./START.sh
```

### Issue: Docker containers not deploying
```bash
# Check Docker status
docker info

# Start Docker Desktop
open -a Docker  # macOS
# Or start Docker service on Linux

# Verify
docker ps
```

### Issue: Reports not generating
```bash
# Check reports directory
ls -la reports/

# Create if missing
mkdir -p reports

# Check permissions
chmod 755 reports/

# Test manually
python -c "from src.report_generator import ReportGenerator; r = ReportGenerator(); print('OK')"
```

### Issue: High memory usage
```bash
# Check process
ps aux | grep python

# Restart application
pkill -f "python app.py"
./START.sh
```

---

## Security Considerations

### 1. Network Security
- Run on localhost only (default)
- Use firewall rules for production
- Enable HTTPS for external access

### 2. Access Control
- Implement authentication (not included)
- Use environment variables for secrets
- Restrict API endpoints

### 3. Data Protection
- Backup database regularly
- Encrypt sensitive data
- Secure log files

---

## Rollback Procedures

### If deployment fails:
```bash
# Stop application
pkill -f "python app.py"

# Restore from backup
cp backups/config_backup_YYYYMMDD/* config/

# Restart
./START.sh
```

### If data corruption:
```bash
# Remove database
rm data/infrastructure.db

# Restart (will recreate)
./START.sh
```

---

## Production Deployment

### Using systemd (Linux)
```bash
# Create service file
sudo nano /etc/systemd/system/infra-automation.service

[Unit]
Description=System Sentinel
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/infrastructure-automation
ExecStart=/path/to/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable infra-automation
sudo systemctl start infra-automation
```

### Using Docker
```bash
# Create Dockerfile (not included)
# Build image
docker build -t infra-automation .

# Run container
docker run -d -p 5000:5000 -v /var/run/docker.sock:/var/run/docker.sock infra-automation
```

---

## Support

### Getting Help
- Check logs: `tail -f logs/*.log`
- Review documentation: `docs/`
- Check GitHub issues
- Contact: support@example.com

### Reporting Bugs
1. Check existing issues
2. Provide error logs
3. Include system info
4. Steps to reproduce
