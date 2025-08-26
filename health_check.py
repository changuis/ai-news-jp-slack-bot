#!/usr/bin/env python3
"""
Simple health check server for Railway deployment
"""

import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging

logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple health check handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_status = {
                'status': 'healthy',
                'service': 'ai-news-jp-slack-bot',
                'timestamp': time.time(),
                'uptime': time.time() - getattr(self.server, 'start_time', time.time())
            }
            
            self.wfile.write(json.dumps(health_status).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

class HealthCheckServer:
    """Health check server for Railway"""
    
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.thread = None
        
    def start(self):
        """Start the health check server"""
        try:
            self.server = HTTPServer(('0.0.0.0', self.port), HealthCheckHandler)
            self.server.start_time = time.time()
            
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            
            logger.info(f"Health check server started on port {self.port}")
        except Exception as e:
            logger.warning(f"Failed to start health check server: {e}")
    
    def stop(self):
        """Stop the health check server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Health check server stopped")

# Global health check server instance
health_server = None

def start_health_check():
    """Start the health check server"""
    global health_server
    if health_server is None:
        health_server = HealthCheckServer()
        health_server.start()

def stop_health_check():
    """Stop the health check server"""
    global health_server
    if health_server:
        health_server.stop()
        health_server = None
