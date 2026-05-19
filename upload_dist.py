"""
Sube todos los archivos de dist/ al VPS via SFTP.
"""
import paramiko, getpass, os
from pathlib import Path

HOSTNAME = 'softint.com.mx'
REMOTE_BASE = '/home/softint/domains/helen.softint.com.mx/public_html'
LOCAL_DIST = Path(r'C:\Users\andre\HELEN-v5.0\Helen-Web\frontend\web-app\dist')

username = input("Usuario VPS: ").strip()
password = getpass.getpass("Contrasena: ")

transport = paramiko.Transport((HOSTNAME, 22))
transport.connect(username=username, password=password)
sftp = paramiko.SFTPClient.from_transport(transport)

def mkdir_p(sftp, remote_path):
    try:
        sftp.stat(remote_path)
    except FileNotFoundError:
        sftp.mkdir(remote_path)
    sftp.chmod(remote_path, 0o755)

def upload_dir(sftp, local_dir, remote_dir):
    mkdir_p(sftp, remote_dir)
    for item in local_dir.iterdir():
        remote_path = f"{remote_dir}/{item.name}"
        if item.is_dir():
            upload_dir(sftp, item, remote_path)
        else:
            sftp.put(str(item), remote_path)
            sftp.chmod(remote_path, 0o644)
            print(f"  {item.name}")

print("Subiendo dist/...")
upload_dir(sftp, LOCAL_DIST, REMOTE_BASE)

sftp.close()
transport.close()
print("\nListo! Recarga Helen en el Pi.")
