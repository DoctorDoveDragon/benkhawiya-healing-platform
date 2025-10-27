from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
from datetime import datetime
from contextlib import contextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('benkhawiya.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

FOUR_LANDS = {
    "white_land": {
        "name": "White Land of Origins",
        "element": "Spirit", 
        "direction": "Center",
        "teaching": "Pure Consciousness & Ancestral Memory",
        "animal": "White Buffalo",
        "color": "White",
        "symbol": "🦬",
        "blessing": "May the White Land awaken your ancestral memory and pure consciousness"
    },
    "black_land": {
        "name": "Black Land of Potential",
        "element": "Void",
        "direction": "Within", 
        "teaching": "Unmanifest Potential & Quantum Possibility",
        "animal": "Black Panther", 
        "color": "Black",
        "symbol": "🐆",
        "blessing": "May the Black Land reveal the infinite possibilities within the void"
    },
    "red_land": {
        "name": "Red Land of Manifestation",
        "element": "Blood/Fire",
        "direction": "Manifest",
        "teaching": "Life Force & Physical Creation", 
        "animal": "Red Hawk",
        "color": "Red",
        "symbol": "🦅", 
        "blessing": "May the Red Land ignite your creative life force and power to manifest"
    },
    "green_land": {
        "name": "Green Land of Growth",
        "element": "Earth/Life", 
        "direction": "Expand",
        "teaching": "Regeneration & Collective Life",
        "animal": "Green Serpent",
        "color": "Green",
        "symbol": "🐍",
        "blessing": "May the Green Land connect you to all living beings and cycles of regeneration"
    }
}

class BenkhawiyaHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "benkhawiya-healing-platform",
                "cosmology": "Four Lands Tradition" 
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/four-lands':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(FOUR_LANDS).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        if self.path == '/auth/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "message": "Welcome to the Benkhawiya journey",
                "email": data.get('email'),
                "spiritual_name": data.get('spiritual_name'),
                "status": "registered"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    port = 8000
    server = HTTPServer(('0.0.0.0', port), BenkhawiyaHandler)
    logger.info(f"Benkhawiya Healing Platform running on port {port}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
