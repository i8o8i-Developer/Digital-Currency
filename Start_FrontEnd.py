"""
Start_FrontEnd.py
Frontend Server Startup Script
"""

import os
import sys
import http.server
import socketserver
import webbrowser
import socket
from pathlib import Path

PORT = 8080
FRONTEND_DIR = Path(__file__).parent / 'FrontEnd'

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[{self.log_date_time_string()}] {format % args}")

def print_header():
    """Print Startup Header"""
    print("=" * 60)
    print("  I8o8iCoin Digital Currency System - Frontend Server")
    print("=" * 60)
    print()

def find_available_port(start_port=8080, max_attempts=10):
    """Find An Available Port Starting From Start_Port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            # Try To Bind To The Port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

def start_server():
    """Start Frontend HTTP Server"""
    global PORT
    
    print_header()
    
    # Check If Default Port Is Available, Otherwise Find Another
    original_port = PORT
    available_port = find_available_port(PORT)
    
    if available_port is None:
        print(f"[ERROR] Could Not Find Available Port Between {PORT} And {PORT + 10}")
        print(f"[ERROR] Please Close Some Applications And Try Again")
        print()
        sys.exit(1)
    
    if available_port != original_port:
        print(f"[WARNING] Port {original_port} Is Already In Use")
        print(f"[INFO] Using Port {available_port} Instead")
        print()
        PORT = available_port
    
    print(f"[INFO] Starting HTTP Server For Frontend...")
    print(f"[INFO] Serving Files From: {FRONTEND_DIR}")
    print()
    print(f"Server Running On: http://localhost:{PORT}")
    print()
    print("Open Your Browser And Navigate To:")
    print(f"  http://localhost:{PORT}")
    print()
    print("Press Ctrl+C To Stop The Server")
    print()
    print("-" * 60)
    print()
    
    # Open browser automatically
    try:
        webbrowser.open(f'http://localhost:{PORT}')
    except:
        pass
    
    # Start server
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print()
        print()
        print("=" * 60)
        print("  Server Stopped")
        print("=" * 60)
    except OSError as e:
        print()
        print(f"ERROR: {e}")
        print()
        sys.exit(1)

def main():
    """Main Startup Function"""
    try:
        start_server()
    except Exception as e:
        print()
        print(f"ERROR: {e}")
        print()
        sys.exit(1)

if __name__ == '__main__':
    main()
