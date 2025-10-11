#!/usr/bin/env python3
"""
ENTERPRISE MONITORING DASHBOARD

Single unified tracker for all AI Agent Suite enterprise components:
- LSP/MCP server status
- Enterprise metrics (Prometheus)
- Distributed tracing (Jaeger)
- Cache performance (Redis)
- Database health (PostgreSQL)
- Docker orchestration status
- Enterprise pattern usage

Usage:
    python enterprise_dashboard.py          # Terminal dashboard
    python enterprise_dashboard.py --web    # Web interface
"""

import asyncio
import json
import os
import time
import aiohttp
import redis.asyncio as redis
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import curses
import curses.textpad
import threading
from pathlib import Path


class EnterpriseDashboard:
    """Unified monitoring dashboard for AI Agent Suite."""

    def __init__(self):
        self.metrics = {}
        self.services = {
            "lsp_server": {"port": 3000, "status": "unknown"},
            "mcp_server": {"port": 3001, "status": "unknown"},
            "prometheus": {"port": 9090, "status": "unknown"},
            "grafana": {"port": 3000, "status": "unknown"},
            "jaeger": {"port": 16686, "status": "unknown"},
            "redis": {"port": 6379, "status": "unknown"},
            "postgres": {"port": 5432, "status": "unknown"}
        }

    async def collect_metrics(self) -> None:
        """Collect metrics from all enterprise components."""
        tasks = [
            self._check_service_health(),
            self._collect_prometheus_metrics(),
            self._collect_cache_metrics(),
            self._collect_database_metrics(),
            self._collect_tracing_metrics(),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "services": results[0] if not isinstance(results[0], Exception) else {},
            "prometheus": results[1] if not isinstance(results[1], Exception) else {},
            "cache": results[2] if not isinstance(results[2], Exception) else {},
            "database": results[3] if not isinstance(results[3], Exception) else {},
            "tracing": results[4] if not isinstance(results[4], Exception) else {},
        }

    async def _check_service_health(self) -> Dict[str, Any]:
        """Check health of all services."""
        health_status = {}

        for service_name, info in self.services.items():
            try:
                # Basic TCP connection check
                sock = await asyncio.open_connection("localhost", info["port"])
                sock[0].close()
                health_status[service_name] = {
                    "status": "healthy",
                    "response_time": 0,
                    "last_check": datetime.now().isoformat()
                }
            except Exception as e:
                health_status[service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                }

        return health_status

    async def _collect_prometheus_metrics(self) -> Dict[str, Any]:
        """Collect key metrics from Prometheus."""
        try:
            async with aiohttp.ClientSession() as session:
                # Query key enterprise metrics
                queries = {
                    "total_requests": 'sum(aiagentsuite_requests_total)',
                    "success_rate": 'rate(aiagentsuite_requests_total{status="success"}[5m]) / rate(aiagentsuite_requests_total[5m]) * 100',
                    "avg_response_time": 'histogram_quantile(0.95, rate(aiagentsuite_request_duration_seconds_bucket[5m]))',
                    "formal_verifications": 'sum(aiagentsuite_verifications_total)',
                    "chaos_experiments": 'sum(aiagentsuite_chaos_experiments_total)',
                    "cache_hit_ratio": 'aiagentsuite_cache_hit_ratio',
                    "active_connections": 'aiagentsuite_connections_active',
                }

                metrics = {}
                for name, query in queries.items():
                    try:
                        async with session.get(f"http://localhost:9090/api/v1/query", params={"query": query}) as response:
                            data = await response.json()
                            if data["data"]["result"]:
                                value = data["data"]["result"][0]["value"][1]
                                metrics[name] = float(value)
                            else:
                                metrics[name] = 0
                    except:
                        metrics[name] = 0

                return metrics

        except Exception as e:
            return {"error": str(e)}

    async def _collect_cache_metrics(self) -> Dict[str, Any]:
        """Collect Redis cache metrics."""
        try:
            r = redis.Redis(host="localhost", port=6379, decode_responses=True)
            info = await r.info()

            # Get AI Agent Suite keys
            ai_keys = await r.keys("aiagentsuite:*")
            ai_keys_count = len(ai_keys)

            # Cache hit/miss stats (if available)
            cache_stats = {
                "total_keys": info.get("keyspace", {}).get("db0", "0").split(",")[0],
                "ai_suite_keys": ai_keys_count,
                "memory_used": info.get("used_memory_human", "0B"),
                "connections": info.get("connected_clients", 0),
                "uptime_seconds": info.get("uptime_in_seconds", 0)
            }

            await r.close()
            return cache_stats

        except Exception as e:
            return {"error": str(e)}

    async def _collect_database_metrics(self) -> Dict[str, Any]:
        """Collect PostgreSQL database metrics."""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user=os.getenv("POSTGRES_USER", "aiagentsuite"),
                password=os.getenv("POSTGRES_PASSWORD", "aiagentsuite"),
                database="aiagentsuite"
            )

            cursor = conn.cursor()

            # Get database statistics
            cursor.execute("""
                SELECT
                    (SELECT count(*) FROM users) as user_count,
                    (SELECT count(*) FROM audit_events WHERE created_at > now() - interval '1 hour') as recent_events,
                    (SELECT count(*) FROM verification_proofs WHERE created_at > now() - interval '1 day') as proofs_today
            """)

            result = cursor.fetchone()
            db_metrics = {
                "total_users": result[0] or 0,
                "audit_events_hour": result[1] or 0,
                "verification_proofs_day": result[2] or 0,
                "connection_status": "healthy"
            }

            cursor.close()
            conn.close()

            return db_metrics

        except Exception as e:
            return {"error": str(e)}

    async def _collect_tracing_metrics(self) -> Dict[str, Any]:
        """Collect Jaeger tracing metrics."""
        try:
            async with aiohttp.ClientSession() as session:
                # Get recent traces (last hour)
                params = {
                    "service": "aiagentsuite",
                    "lookback": "1h",
                    "operation": "all"
                }

                async with session.get("http://localhost:16686/api/traces", params=params) as response:
                    data = await response.json()

                    trace_count = len(data.get("data", []))
                    return {"active_traces": trace_count, "status": "healthy"}

        except Exception as e:
            return {"error": str(e)}


class TerminalDashboard:
    """Text-based terminal dashboard."""

    def __init__(self, dashboard: EnterpriseDashboard):
        self.dashboard = dashboard
        self.stdscr = None

    def run(self):
        """Run the terminal dashboard."""
        curses.wrapper(self._main_loop)

    def _main_loop(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(1000)  # Refresh every second

        while True:
            try:
                # Collect fresh metrics
                asyncio.run(self.dashboard.collect_metrics())

                # Clear screen
                stdscr.clear()

                # Draw dashboard
                self._draw_header()
                self._draw_service_status()
                self._draw_enterprise_metrics()
                self._draw_system_health()

                # Refresh display
                stdscr.refresh()

                # Check for quit key
                key = stdscr.getch()
                if key == ord('q'):
                    break

                time.sleep(1)

            except KeyboardInterrupt:
                break

    def _draw_header(self):
        """Draw dashboard header."""
        self.stdscr.addstr(0, 2, "🤖 AI AGENT SUITE - ENTERPRISE MONITORING DASHBOARD", curses.A_BOLD)
        self.stdscr.addstr(1, 2, f"🕐 Last Update: {datetime.now().strftime('%H:%M:%S')}", curses.A_DIM)
        self.stdscr.addstr(2, 2, "=" * 70, curses.A_DIM)

    def _draw_service_status(self):
        """Draw service health status."""
        self.stdscr.addstr(4, 2, "🚀 SERVICE STATUS", curses.A_BOLD)

        row = 6
        for service, info in self.dashboard.services.items():
            status = self.metrics.get("services", {}).get(service, {}).get("status", "unknown")
            color = curses.color_pair(1) if status == "healthy" else curses.color_pair(2)

            status_icon = "✅" if status == "healthy" else "❌"

            self.stdscr.addstr(row, 2, f"{status_icon} {service}")
            self.stdscr.addstr(row, 25, f":{info['port']}")
            self.stdscr.addstr(row, 35, status.upper(), color)
            row += 1

    def _draw_enterprise_metrics(self):
        """Draw key enterprise metrics."""
        self.stdscr.addstr(15, 2, "📊 ENTERPRISE METRICS", curses.A_BOLD)

        metrics = self.metrics.get("prometheus", {})

        row = 17
        metric_display = [
            (f"Total Requests", f"{metrics.get('total_requests', 0):.0f}"),
            (f"Success Rate", ".1f" if metrics.get('success_rate') else "N/A"),
            (f"Avg Response", ".1f" if metrics.get('avg_response_time') else "N/A"),
            (f"Formal Verifications", f"{metrics.get('formal_verifications', 0):.0f}"),
            (f"Chaos Experiments", f"{metrics.get('chaos_experiments', 0):.0f}"),
            (f"Cache Hit Ratio", ".1f" if metrics.get('cache_hit_ratio') else "N/A"),
        ]

        for label, value in metric_display:
            self.stdscr.addstr(row, 2, f"{label}:")
            self.stdscr.addstr(row, 25, str(value))
            row += 1

    def _draw_system_health(self):
        """Draw system health indicators."""
        self.stdscr.addstr(25, 2, "🏥 SYSTEM HEALTH", curses.A_BOLD)

        # Cache status
        cache = self.metrics.get("cache", {})
        row = 27
        self.stdscr.addstr(row, 2, f"Redis Memory: {cache.get('memory_used', 'N/A')}")
        self.stdscr.addstr(row + 1, 2, f"AI Suite Keys: {cache.get('ai_suite_keys', 0)}")

        # Database status
        db = self.metrics.get("database", {})
        self.stdscr.addstr(row + 3, 2, f"Total Users: {db.get('total_users', 0)}")
        self.stdscr.addstr(row + 4, 2, f"Audit Events/Hour: {db.get('audit_events_hour', 0)}")
        self.stdscr.addstr(row + 5, 2, f"Verifications/Day: {db.get('verification_proofs_day', 0)}")

        # Tracing
        tracing = self.metrics.get("tracing", {})
        self.stdscr.addstr(row + 7, 2, f"Active Traces: {tracing.get('active_traces', 0)}")

        # Quit instruction
        self.stdscr.addstr(35, 2, "Press 'q' to quit", curses.A_DIM)


class WebDashboard:
    """Web-based dashboard using simple HTTP server."""

    def __init__(self, dashboard: EnterpriseDashboard):
        self.dashboard = dashboard

    def _generate_html(self, metrics: Dict[str, Any]) -> str:
        """Generate HTML dashboard."""
        services = metrics.get("services", {})
        prometheus = metrics.get("prometheus", {})
        cache = metrics.get("cache", {})
        database = metrics.get("database", {})
        tracing = metrics.get("tracing", {})

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI Agent Suite - Enterprise Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .card h3 {{
            margin-top: 0;
            color: #ffd700;
            border-bottom: 2px solid #ffd700;
            padding-bottom: 10px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 5px 0;
        }}
        .metric-label {{
            font-weight: bold;
        }}
        .metric-value {{
            color: {('#4CAF50' if 'error' not in str(value).lower() else '#f44336') for value in [prometheus.get('success_rate', 0)]};
        }}
        .status-healthy {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .status-unhealthy {{
            color: #f44336;
            font-weight: bold;
        }}
        .refresh-info {{
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Agent Suite - Enterprise Monitoring Dashboard</h1>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="grid">
            <!-- Service Status -->
            <div class="card">
                <h3>🚀 Service Status</h3>
                {"".join(f'''
                <div class="metric">
                    <span class="metric-label">{service.replace('_', ' ').title()}</span>
                    <span class="metric-value {'status-healthy' if info.get('status') == 'healthy' else 'status-unhealthy'}">
                        {"✅" if info.get('status') == 'healthy' else "❌"} {info.get('status', 'unknown').upper()}
                    </span>
                </div>
                ''' for service, info in services.items())}
            </div>

            <!-- Enterprise Metrics -->
            <div class="card">
                <h3>📊 Enterprise Metrics</h3>
                <div class="metric">
                    <span class="metric-label">Total Requests</span>
                    <span class="metric-value">{prometheus.get('total_requests', 0):.0f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Success Rate</span>
                    <span class="metric-value">{prometheus.get('success_rate', 0):.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Avg Response Time</span>
                    <span class="metric-value">{prometheus.get('avg_response_time', 0):.1f}s</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Formal Verifications</span>
                    <span class="metric-value">{prometheus.get('formal_verifications', 0):.0f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Chaos Experiments</span>
                    <span class="metric-value">{prometheus.get('chaos_experiments', 0):.0f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Cache Hit Ratio</span>
                    <span class="metric-value">{prometheus.get('cache_hit_ratio', 0):.1f}%</span>
                </div>
            </div>

            <!-- System Health -->
            <div class="card">
                <h3>🏥 System Health</h3>
                <div class="metric">
                    <span class="metric-label">Redis Memory Used</span>
                    <span class="metric-value">{cache.get('memory_used', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">AI Suite Cache Keys</span>
                    <span class="metric-value">{cache.get('ai_suite_keys', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Users</span>
                    <span class="metric-value">{database.get('total_users', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Audit Events/Hour</span>
                    <span class="metric-value">{database.get('audit_events_hour', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Verifications/Day</span>
                    <span class="metric-value">{database.get('verification_proofs_day', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Traces</span>
                    <span class="metric-value">{tracing.get('active_traces', 0)}</span>
                </div>
            </div>

            <!-- Quick Links -->
            <div class="card">
                <h3>🔗 Quick Links</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <a href="http://localhost:3000" style="background: rgba(255,255,255,0.2); padding: 8px; border-radius: 5px; text-decoration: none; color: white; display: block; text-align: center;">📊 Grafana</a>
                    <a href="http://localhost:9090" style="background: rgba(255,255,255,0.2); padding: 8px; border-radius: 5px; text-decoration: none; color: white; display: block; text-align: center;">📈 Prometheus</a>
                    <a href="http://localhost:16686" style="background: rgba(255,255,255,0.2); padding: 8px; border-radius: 5px; text-decoration: none; color: white; display: block; text-align: center;">🌐 Jaeger</a>
                    <a href="http://localhost:8000/docs" style="background: rgba(255,255,255,0.2); padding: 8px; border-radius: 5px; text-decoration: none; color: white; display: block; text-align: center;">📚 API Docs</a>
                </div>
            </div>
        </div>

        <div class="refresh-info">
            ⏰ Metrics refresh automatically - Auto-reload page for live updates<br>
            🔧 Bootstrap with <code>python bootstrap.py</code> to start the full enterprise suite
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {{
            window.location.reload();
        }}, 30000);
    </script>
</body>
</html>
"""
        return html

    async def run(self, host="localhost", port=8080):
        """Run web dashboard."""
        print(f"🌐 Starting web dashboard at http://{host}:{port}")
        print("Open your browser to view the enterprise monitoring dashboard")

        await self.dashboard.collect_metrics()

        # Simple HTML template
        html_template = self._generate_html(self.dashboard.metrics)

        # Serve static HTML (in a real implementation, you'd want a proper web framework)
        with open("dashboard.html", "w") as f:
            f.write(html_template)

        print("📄 Dashboard HTML generated: dashboard.html")
        print("💡 In a production setup, this would be a proper web application")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AI Agent Suite Enterprise Monitoring Dashboard")
    parser.add_argument("--web", action="store_true", help="Run web dashboard instead of terminal")
    parser.add_argument("--port", type=int, default=8080, help="Web dashboard port")

    args = parser.parse_args()

    dashboard = EnterpriseDashboard()

    if args.web:
        # Web dashboard
        web_dash = WebDashboard(dashboard)
        asyncio.run(web_dash.run(port=args.port))
    else:
        # Terminal dashboard
        term_dash = TerminalDashboard(dashboard)
        term_dash.run()


if __name__ == "__main__":
    main()
