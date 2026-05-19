"""
Sube .htaccess actualizado al VPS via SFTP para limpiar caché de LiteSpeed.
Uso: py upload_htaccess.py
"""
import paramiko
import getpass
import sys

HOSTNAME = 'softint.com.mx'
PORT = 21  # Algunos hosting usan 22, prueba ambos
REMOTE_PATH = '/home/softint/public_html/helen.softint.com.mx/public_html/.htaccess'

HTACCESS_CONTENT = """\
# ── Disable server-side cache for all HTML (LiteSpeed + Apache) ───────────────
<IfModule mod_headers.c>
    Header always set Cache-Control "no-cache, no-store, must-revalidate"
    Header always set Pragma "no-cache"
    Header always set Expires "0"
</IfModule>

# LiteSpeed: desactivar caché para este directorio
<IfModule LiteSpeed>
    CacheLookup off
    RewriteEngine on
    RewriteRule .* - [E=Cache-Control:no-store]
</IfModule>

# Forzar carga de index.html fresco cuando se accede a /
Options -Indexes
DirectoryIndex index.html

# SPA routing: redirigir rutas no existentes a index.html
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^ index.html [L]
</IfModule>
"""

def upload():
    username = input("Usuario FTP/SSH del VPS (ej: softint): ").strip()
    password = getpass.getpass("Contraseña SFTP: ")

    # Try SSH port 22 first
    for port in [22, 21]:
        try:
            print(f"Intentando puerto {port}...")
            transport = paramiko.Transport((HOSTNAME, port))
            transport.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)

            # Write the .htaccess
            with sftp.open(REMOTE_PATH, 'w') as f:
                f.write(HTACCESS_CONTENT)

            print(f"✅ .htaccess subido exitosamente via puerto {port}")
            sftp.close()
            transport.close()
            return
        except Exception as e:
            print(f"  Puerto {port} falló: {e}")

    print("❌ No se pudo conectar. Verifica usuario/contraseña y que el hosting permita SFTP.")

if __name__ == '__main__':
    upload()
