#!/usr/bin/env python3
"""HTTP server for Seelampur Fire Risk Map (Local & Render compatible)."""
import http.server
import socketserver
import os
import sys

PORT = int(os.environ.get("PORT", 8000))
DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(DIR)

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Default root '/' request serves index.html
        if self.path == "/" or self.path == "":
            self.path = "/index.html"
        return super().do_GET()

print("=" * 50)
print(" Seelampur Fire Risk Geospatial Analysis")
print("=" * 50)
print(f" Serving at: http://0.0.0.0:{PORT}")
print(f" Default path: http://0.0.0.0:{PORT}/index.html")
print("=" * 50)

# Allow port reuse immediately
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
