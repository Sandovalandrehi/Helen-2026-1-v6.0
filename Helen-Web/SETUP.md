# Helen Web — Setup del Foco RGB

## Requisitos
- Python instalado (`py --version` debe funcionar)
- Node.js instalado (`npm --version` debe funcionar)
- Git

---

## Paso 1 — Conectarse al hotspot
Antes de cualquier cosa, conecta tu laptop al hotspot:

- **Red:** `S25 Ultra de Andrehi`
- **Contraseña:** `andrehi9153`
- **Banda:** 2.4 GHz

> El foco y la laptop deben estar en la misma red para que el control funcione.

---

## Paso 2 — Clonar o actualizar el repositorio

```bash
git clone https://github.com/Mrc002/Uabc_Helen_2026_1.git
cd Uabc_Helen_2026_1
git checkout Sashil-RS
```

Si ya tienes el repo:
```bash
git checkout Sashil-RS
git pull origin Sashil-RS
```

---

## Paso 3 — Configurar el backend

```bash
cd Helen-Web/backend/websocket-server
```

Copia el archivo de credenciales:
```bash
cp .env.example .env
```

Instala las dependencias:
```bash
pip install -r requirements.txt
```

Inicia el servidor:
```bash
py server.py
```

> Si el servidor inicia correctamente verás:
> `Running on http://0.0.0.0:5001`

---

## Paso 4 — Iniciar el frontend

Abre una segunda terminal:

```bash
cd Helen-Web/frontend/web-app
npm install
npm run dev
```

Abre el navegador en `http://localhost:3000`

---

## Paso 5 — Verificar el foco

En la pantalla **Mis Dispositivos** el indicador del Foco RGB debe mostrar **ENCENDIDO** o **APAGADO**.

Si dice **SIN CONEXIÓN**, verifica:
- ¿Estás conectado al hotspot `S25 Ultra de Andrehi`?
- ¿El servidor backend está corriendo?
- El IP del foco puede haber cambiado — pídele a Sashil el IP actualizado y cambia `TUYA_IP` en el archivo `.env`

---

## Comandos para controlar el foco desde la terminal

Con el backend corriendo, abre una tercera terminal en `Helen-Web/backend/websocket-server`:

**Encender:**
```bash
py -c "import tinytuya; d = tinytuya.BulbDevice('ebe997370c6c715b97qsgw', '10.92.117.35', 'jU2w`$ER0nHBIPS;9', version=3.5); d.set_socketPersistent(False); print(d.set_status(True, 20))"
```

**Apagar:**
```bash
py -c "import tinytuya; d = tinytuya.BulbDevice('ebe997370c6c715b97qsgw', '10.92.117.35', 'jU2w`$ER0nHBIPS;9', version=3.5); d.set_socketPersistent(False); print(d.set_status(False, 20))"
```

> Si el IP cambió, reemplaza `10.92.117.35` con el nuevo IP en los comandos y en el archivo `.env`.
