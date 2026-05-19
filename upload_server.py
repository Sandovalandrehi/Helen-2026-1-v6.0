import paramiko, getpass

HOSTNAME = "softint.com.mx"
LOCAL = r"C:\Users\andre\HELEN-v5.0\helen-pi-server.py"
REMOTE = "/home/softint/domains/helen.softint.com.mx/public_html/helen-pi-server.py"

username = input("Usuario VPS: ").strip()
password = getpass.getpass("Contrasena VPS: ")

transport = paramiko.Transport((HOSTNAME, 22))
transport.connect(username=username, password=password)
sftp = paramiko.SFTPClient.from_transport(transport)
sftp.put(LOCAL, REMOTE)
sftp.chmod(REMOTE, 0o644)
sftp.close()
transport.close()
print("Subido: https://helen.softint.com.mx/helen-pi-server.py")
