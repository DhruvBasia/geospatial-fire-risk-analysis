#!/usr/bin/env python3
"""Simple HTTP server for the Seelampur Fire Risk Map."""
import http.server
import socketserver
import webbrowser
import os

PORT = 8000
DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(DIR)

Handler = http.server.SimpleHTTPRequestHandler

print("=" * 50)
print(" Seelampur Fire Risk Map")
print("=" * 50)
print(f" Serving at: http://localhost:{PORT}")
print(f" Open in browser: http://localhost:{PORT}/index.html")
print(" Press Ctrl+C to stop")
print("=" * 50)

webbrowser.open(f"http://localhost:{PORT}/index.html")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
