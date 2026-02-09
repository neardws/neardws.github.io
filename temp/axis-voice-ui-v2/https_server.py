import http.server
import ssl
import os
import json
import urllib.request
import urllib.parse
import traceback

os.chdir('/tmp/axis-voice-ui')

ASR_URL = 'http://127.0.0.1:9001/transcribe'
TTS_URL = 'http://127.0.0.1:5100/tts'

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/asr':
            self.proxy_asr()
        elif self.path == '/api/tts':
            self.proxy_tts()
        else:
            self.send_error(404)
    
    def proxy_asr(self):
        try:
            content_length = int(self.headers['Content-Length'])
            content_type = self.headers['Content-Type']
            body = self.rfile.read(content_length)
            
            print(f'ASR request: {content_length} bytes, type: {content_type}')
            
            req = urllib.request.Request(ASR_URL, data=body)
            req.add_header('Content-Type', content_type)
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = resp.read()
                print(f'ASR response: {result[:200]}')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(result)
        except Exception as e:
            print(f'ASR error: {e}')
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def proxy_tts(self):
        try:
            content_length = int(self.headers['Content-Length'])
            content_type = self.headers['Content-Type']
            body = self.rfile.read(content_length)
            
            print(f'TTS request: {content_length} bytes, type: {content_type}')
            
            req = urllib.request.Request(TTS_URL, data=body)
            req.add_header('Content-Type', content_type)
            
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = resp.read()
                print(f'TTS response: {len(result)} bytes')
                self.send_response(200)
                self.send_header('Content-Type', 'audio/wav')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(result)
        except Exception as e:
            print(f'TTS error: {e}')
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

server_address = ('0.0.0.0', 8443)
httpd = http.server.HTTPServer(server_address, ProxyHandler)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print(f'HTTPS server with proxy running on port 8443')
httpd.serve_forever()
