"""
Sube el .htaccess corregido y el index.html actual al VPS via SFTP.
Uso: py upload_fix.py
"""
import paramiko
import getpass
import os

HOSTNAME = 'softint.com.mx'
SSH_PORT = 22

# Ruta base en el VPS (ajustar si es diferente)
REMOTE_BASE = '/home/softint/public_html/helen.softint.com.mx/public_html'

LOCAL_DIST = r'C:\Users\andre\HELEN-v5.0\Helen-Web\frontend\web-app\dist'

HTACCESS = """\
# ── Deshabilitar caché de LiteSpeed globalmente ──────────────────────────────
<IfModule LiteSpeed>
    CacheLookup off
</IfModule>

# ── No-cache para todos los responses (Apache + LiteSpeed) ────────────────────
<IfModule mod_headers.c>
    Header always set Cache-Control "no-cache, no-store, must-revalidate"
    Header always set Pragma "no-cache"
    Header always set Expires "0"
</IfModule>

# ── SPA routing: rutas no existentes → index.html ─────────────────────────────
Options -Indexes
DirectoryIndex index.html

<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^ index.html [L]
</IfModule>
"""

def upload():
    username = input("Usuario SSH/FTP del VPS (probablemente: helen o softint): ").strip()
    password = getpass.getpass("Contraseña: ")

    print(f"Conectando a {HOSTNAME}:{SSH_PORT}...")
    try:
        transport = paramiko.Transport((HOSTNAME, SSH_PORT))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("✅ Conectado!")

        # 1. Subir .htaccess con CacheLookup off
        htaccess_path = f"{REMOTE_BASE}/.htaccess"
        with sftp.open(htaccess_path, 'w') as f:
            f.write(HTACCESS)
        print(f"✅ .htaccess subido: {htaccess_path}")

        # 2. Subir index.html fresco
        local_index = os.path.join(LOCAL_DIST, 'index.html')
        remote_index = f"{REMOTE_BASE}/index.html"
        sftp.put(local_index, remote_index)
        print(f"✅ index.html subido: {remote_index}")

        sftp.close()
        transport.close()
        print("\n🎉 ¡Listo! Recarga Helen en el Pi con Ctrl+Shift+R")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nSi falla, intenta con usuario 'helen' o revisa el hostname en cPanel")

if __name__ == '__main__':
    upload()
