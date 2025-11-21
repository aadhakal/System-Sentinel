# Infrastructure Automation Platform

Python-based infrastructure automation system with real-time web dashboard for server deployment, monitoring, and management.

## Features in Action

| Demo | ![Deploy Demo](media/demo.gif) |



## Features

- **Automated Server Deployment** - One-click infrastructure provisioning
- **Real-Time Monitoring** - Live system metrics (CPU, Memory, Disk)
- **Web Dashboard** - Professional UI with Bootstrap and Chart.js
- **REST API** - 8 endpoints for system integration
- **Data Persistence** - SQLite database for historical tracking
- **Intelligent Alerting** - Threshold-based notifications

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start web application
python app.py

# Open browser
http://localhost:5000
```

## CLI Usage

```bash
# Deploy and monitor
python main.py --deploy --monitor --report

# Run demo
python main.py --demo
```

## Technologies

- Python 3.x
- Flask (Web framework)
- SQLite (Database)
- Bootstrap 5 (UI)
- Chart.js (Visualization)
- psutil (System monitoring)

## Project Structure

```
├── app.py              # Flask web application
├── main.py             # CLI automation tool
├── api/                # Database layer
├── src/                # Core automation modules
├── templates/          # HTML templates
├── static/             # CSS and JavaScript
└── config/             # Configuration files
```

## API Endpoints

```
GET    /api/servers              # List all servers
POST   /api/servers/deploy       # Deploy new server
DELETE /api/servers/<name>/terminate
GET    /api/metrics              # Current system metrics
GET    /api/metrics/history      # Historical data
GET    /api/stats                # Dashboard statistics
```

## License

MIT
