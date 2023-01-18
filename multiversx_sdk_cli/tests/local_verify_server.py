from http.server import HTTPServer, BaseHTTPRequestHandler
import json

HOST = 'localhost'
PORT = 7777


class HTTP(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        if self.path == "/initialise":
            response = {'token': 7890}
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        
        if self.path == "/verify":
            response = {'status': 'sent to verification'}
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))


server = HTTPServer((HOST, PORT), HTTP)
print('Server running...')

server.serve_forever()
server.server_close()

print('Server closed!')
