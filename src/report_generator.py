import json
import csv
from datetime import datetime, timedelta
import os
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class ReportGenerator:
    def __init__(self, reports_dir="reports"):
        self.reports_dir = reports_dir
        os.makedirs(reports_dir, exist_ok=True)
    
    def generate_system_report(self, metrics_data, alerts_data):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate JSON report
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_alerts': len(alerts_data),
                'avg_cpu_usage': sum(m.get('cpu_usage', 0) for m in metrics_data) / len(metrics_data) if metrics_data else 0,
                'avg_memory_usage': sum(m.get('memory_usage', 0) for m in metrics_data) / len(metrics_data) if metrics_data else 0
            },
            'metrics': metrics_data,
            'alerts': alerts_data
        }
        
        json_path = os.path.join(self.reports_dir, f'system_report_{timestamp}.json')
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return json_path
    
    def generate_server_inventory_report(self, servers):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if not servers:
            return None
        
        # Generate CSV report manually
        csv_path = os.path.join(self.reports_dir, f'server_inventory_{timestamp}.csv')
        with open(csv_path, 'w') as f:
            if servers:
                headers = servers[0].keys()
                f.write(','.join(headers) + '\n')
                for server in servers:
                    f.write(','.join(str(server.get(h, '')) for h in headers) + '\n')
        
        # Generate summary statistics
        summary = {
            'total_servers': len(servers),
            'running_servers': len([s for s in servers if s.get('status') == 'running']),
            'server_types': {}
        }
        
        return csv_path, summary
    
    def create_performance_chart(self, metrics_data):
        if not metrics_data:
            return None
        
        # Generate text-based chart data
        chart_path = os.path.join(self.reports_dir, f'performance_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        
        with open(chart_path, 'w') as f:
            f.write('Performance Metrics Over Time\n')
            f.write('=' * 40 + '\n')
            for i, m in enumerate(metrics_data):
                f.write(f"Point {i+1}: CPU {m.get('cpu_usage', 0):.1f}%, Memory {m.get('memory_usage', 0):.1f}%\n")
        
        return chart_path
    
    def generate_html_report(self, metrics, servers):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>System Sentinel Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 5px; text-align: center; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #007bff; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #007bff; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f8f9fa; }}
        .status {{ padding: 4px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; }}
        .status-running {{ background: #28a745; color: white; }}
        .status-stopped {{ background: #ffc107; color: black; }}
        .status-terminated {{ background: #dc3545; color: white; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>System Sentinel - Infrastructure Report</h1>
        <p><strong>Generated:</strong> {timestamp}</p>
        
        <h2>System Metrics</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{metrics.get('cpu_usage', 0):.1f}%</div>
                <div class="metric-label">CPU Usage</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('memory_usage', 0):.1f}%</div>
                <div class="metric-label">Memory Usage</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('disk_usage', 0):.1f}%</div>
                <div class="metric-label">Disk Usage</div>
            </div>
        </div>
        
        <h2>Container Inventory</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Status</th>
                    <th>IP Address</th>
                    <th>Type</th>
                    <th>Deployed At</th>
                </tr>
            </thead>
            <tbody>
'''
        
        if servers:
            for server in servers:
                status_class = f"status-{server.get('status', 'unknown')}"
                real_badge = '🐳' if server.get('real') else '💭'
                html += f'''                <tr>
                    <td>{real_badge} {server.get('name', 'N/A')}</td>
                    <td><span class="status {status_class}">{server.get('status', 'unknown').upper()}</span></td>
                    <td>{server.get('ip', 'N/A')}</td>
                    <td>{server.get('type', 'N/A')}</td>
                    <td>{server.get('deployed_at', 'N/A')[:19]}</td>
                </tr>
'''
        else:
            html += '                <tr><td colspan="5" style="text-align: center; color: #999;">No containers deployed</td></tr>\n'
        
        html += f'''            </tbody>
        </table>
        
        <h2>Summary</h2>
        <ul>
            <li><strong>Total Containers:</strong> {len(servers)}</li>
            <li><strong>Running:</strong> {len([s for s in servers if s.get('status') == 'running'])}</li>
            <li><strong>Stopped:</strong> {len([s for s in servers if s.get('status') == 'stopped'])}</li>
            <li><strong>Real Docker Containers:</strong> {len([s for s in servers if s.get('real')])}</li>
        </ul>
        
        <div class="footer">
            <p>Generated by System Sentinel</p>
        </div>
    </div>
</body>
</html>'''
        
        filename = f'system_sentinel_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(html)
        
        return filename
    
    def generate_json_report(self, metrics, servers):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = {
            'generated_at': timestamp,
            'system_metrics': {
                'cpu_usage': metrics.get('cpu_usage', 0),
                'memory_usage': metrics.get('memory_usage', 0),
                'disk_usage': metrics.get('disk_usage', 0)
            },
            'containers': servers,
            'summary': {
                'total_containers': len(servers),
                'running': len([s for s in servers if s.get('status') == 'running']),
                'stopped': len([s for s in servers if s.get('status') == 'stopped']),
                'real_containers': len([s for s in servers if s.get('real')])
            }
        }
        
        filename = f'system_sentinel_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename
    
    def generate_csv_report(self, metrics, servers):
        filename = f'system_sentinel_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Report header
            writer.writerow(['System Sentinel - Infrastructure Report'])
            writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])
            
            # System metrics section
            writer.writerow(['SYSTEM METRICS'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['CPU Usage', f"{metrics.get('cpu_usage', 0):.1f}%"])
            writer.writerow(['Memory Usage', f"{metrics.get('memory_usage', 0):.1f}%"])
            writer.writerow(['Disk Usage', f"{metrics.get('disk_usage', 0):.1f}%"])
            writer.writerow([])
            
            # Container inventory section
            writer.writerow(['CONTAINER INVENTORY'])
            writer.writerow(['Name', 'Status', 'IP Address', 'Real Docker', 'Deployed At'])
            
            if servers:
                for server in servers:
                    writer.writerow([
                        server.get('name', 'N/A'),
                        server.get('status', 'unknown').upper(),
                        server.get('ip', 'N/A'),
                        'Yes' if server.get('real') else 'No',
                        server.get('deployed_at', 'N/A')[:19] if server.get('deployed_at') else 'N/A'
                    ])
            else:
                writer.writerow(['No containers deployed', '', '', '', ''])
            
            writer.writerow([])
            
            # Summary section
            writer.writerow(['SUMMARY'])
            writer.writerow(['Total Containers', len(servers)])
            writer.writerow(['Running', len([s for s in servers if s.get('status') == 'running'])])
            writer.writerow(['Stopped', len([s for s in servers if s.get('status') == 'stopped'])])
            writer.writerow(['Real Docker Containers', len([s for s in servers if s.get('real')])])
        
        return filename
    
    def generate_pdf_report(self, metrics, servers):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab not installed. Run: pip install reportlab")
        
        filename = f'system_sentinel_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        filepath = os.path.join(self.reports_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph("System Sentinel - Infrastructure Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Timestamp
        timestamp = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
        elements.append(timestamp)
        elements.append(Spacer(1, 20))
        
        # System Metrics
        metrics_title = Paragraph("System Metrics", styles['Heading2'])
        elements.append(metrics_title)
        elements.append(Spacer(1, 12))
        
        metrics_data = [
            ['Metric', 'Value'],
            ['CPU Usage', f"{metrics.get('cpu_usage', 0):.1f}%"],
            ['Memory Usage', f"{metrics.get('memory_usage', 0):.1f}%"],
            ['Disk Usage', f"{metrics.get('disk_usage', 0):.1f}%"]
        ]
        
        metrics_table = Table(metrics_data)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 20))
        
        # Container Inventory
        inventory_title = Paragraph("Container Inventory", styles['Heading2'])
        elements.append(inventory_title)
        elements.append(Spacer(1, 12))
        
        if servers:
            inventory_data = [['Name', 'Status', 'IP', 'Type']]
            for server in servers:
                real_badge = '🐳' if server.get('real') else '💭'
                inventory_data.append([
                    f"{real_badge} {server.get('name', 'N/A')}",
                    server.get('status', 'unknown').upper(),
                    server.get('ip', 'N/A'),
                    server.get('type', 'N/A')
                ])
            
            inventory_table = Table(inventory_data)
            inventory_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(inventory_table)
        else:
            no_containers = Paragraph("No containers deployed", styles['Normal'])
            elements.append(no_containers)
        
        elements.append(Spacer(1, 20))
        
        # Summary
        summary_title = Paragraph("Summary", styles['Heading2'])
        elements.append(summary_title)
        elements.append(Spacer(1, 12))
        
        summary_text = f"""<br/>
        Total Containers: {len(servers)}<br/>
        Running: {len([s for s in servers if s.get('status') == 'running'])}<br/>
        Stopped: {len([s for s in servers if s.get('status') == 'stopped'])}<br/>
        Real Docker Containers: {len([s for s in servers if s.get('real')])}
        """
        summary = Paragraph(summary_text, styles['Normal'])
        elements.append(summary)
        
        doc.build(elements)
        return filename