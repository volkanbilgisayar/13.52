import http.server
import socketserver
import os
import mimetypes
import sys
import datetime
import socket

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# PS4 WebKit ve AppCache için kritik MIME türleri
mimetypes.add_type('text/cache-manifest', '.appcache')
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/html', '.html')
mimetypes.add_type('application/octet-stream', '.bin')
mimetypes.add_type('application/octet-stream', '.elf')
mimetypes.add_type('image/png', '.png')

class PS4HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()

    def guess_type(self, path):
        if path.endswith('.appcache'):
            return 'text/cache-manifest'
        if path.endswith('.bin'):
            return 'application/octet-stream'
        if path.endswith('.js'):
            return 'application/javascript; charset=utf-8'
        return super().guess_type(path)

    def do_POST(self):
        # jb.js içindeki post("TAG", detail) log çağrılarını karşıla
        if self.path == '/t':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8', errors='ignore')
            now = datetime.datetime.now().strftime('%H:%M:%S')
            print(f"[{now}] [PS4 LOG] {post_data}")
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return
        super().do_POST()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    ip = get_local_ip()
    print("=" * 65)
    print("      PS4 13.52 / 13.50 / 13.02 RAW GAME KIRMA SUNUCUSU")
    print("=" * 65)
    print(f" Bilgisayar Yerel IP: {ip}")
    print(f" PS4 Tarayicisina Yazilacak Adres:")
    print(f"       http://{ip}:{PORT}")
    print("=" * 65)
    print("Sunucu hazir, istekler bekleniyor...")

    try:
        with ReusableTCPServer(("", PORT), PS4HTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except OSError:
        ALT_PORT = 8081
        print(f"Port {PORT} mesgul, {ALT_PORT} uzerinden baslatiliyor...")
        print(f"PS4 Adresi: http://{ip}:{ALT_PORT}")
        with ReusableTCPServer(("", ALT_PORT), PS4HTTPRequestHandler) as httpd:
            httpd.serve_forever()
