#!/usr/bin/env python3
"""
Servidor HTTP simple para servir el frontend de FixeatAI.

Uso:
    python3 server.py
    
Luego abre: http://localhost:3000/chat.html
"""

import http.server
import socketserver
from pathlib import Path

PORT = 3000
DIRECTORY = Path(__file__).parent

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler que agrega headers CORS."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def main():
    print("=" * 70)
    print("🚀 Servidor FixeatAI Frontend")
    print("=" * 70)
    print(f"\n📂 Sirviendo archivos desde: {DIRECTORY}")
    print(f"🌐 URL: http://localhost:{PORT}/chat.html")
    print(f"\n💡 Presiona Ctrl+C para detener el servidor\n")
    print("=" * 70)
    
    with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ Servidor detenido")

if __name__ == "__main__":
    main()


