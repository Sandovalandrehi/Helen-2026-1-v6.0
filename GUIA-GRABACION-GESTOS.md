# Guia de Grabacion de Gestos - Helen

## Para que es esto

Necesitamos grabar videos de gestos para entrenar el modelo de IA de Helen. Mientras mas personas distintas graben los gestos, mejor reconocera Helen a cualquier usuario.

## Que necesitas

- Una computadora con webcam
- Python instalado
- Clonar el repo: `git clone https://github.com/Mrc002/Uabc_Helen_2026_1.git`
- Cambiar a la rama: `git checkout Sashil-RS`

## Setup inicial

```bash
cd Helen-Web/backend/ml-service
pip install opencv-python mediapipe numpy
```

## Como grabar

Comando para grabar un gesto especifico:

```bash
python grabarVideo.py <nombre_gesto> ./gesture_dataset
```

Ejemplo:
```bash
python grabarVideo.py home ./gesture_dataset
```

Controles dentro de la ventana:
- **Tecla `s`**: graba un clip de 3 segundos
- **Tecla `q`**: salir cuando termines

## Gestos a grabar (12 en total)

### Prioridad ALTA (criticos para el demo) - graben 50+ videos por gesto

| Gesto | Para que sirve |
|-------|----------------|
| `home` | Volver a la pantalla principal |
| `dispositivos` | Ir a la pantalla de dispositivos |
| `apagar` | Apagar el foco RGB |
| `encender` | Encender el foco RGB |

### Prioridad MEDIA - graben 30+ videos por gesto

| Gesto | Para que sirve |
|-------|----------------|
| `clima` | Ver el clima |
| `alarma` | Ir a alarmas |
| `agregar` | Agregar nueva alarma/dispositivo |
| `editar` | Editar elemento existente |
| `configuracion` | Abrir ajustes |
| `camara` | Activar/desactivar camara |
| `colores` | Cambiar colores del foco |
| `wifi` | Configurar wifi |

## Buenas practicas para grabar

1. **Iluminacion**: luz frontal, NO de techo directo
2. **Fondo**: simple, sin movimiento
3. **Distancia**: manos a ~50cm de la camara
4. **Variacion**: cambia un poco la posicion/angulo entre grabaciones
5. **Manos visibles**: que se vean COMPLETAS las dos manos (o la que uses)
6. **Mantente quieto/a**: solo se mueve la mano haciendo el gesto

## Como entregar

1. Despues de grabar, los videos quedan en `Helen-Web/backend/ml-service/gesture_dataset/<gesto>/`
2. Haz commit y push:
   ```bash
   git add Helen-Web/backend/ml-service/gesture_dataset/
   git commit -m "Agregar videos de gestos - <tu_nombre>"
   git push origin Sashil-RS
   ```

## Que pasa despues

Cuando todos hayan grabado:
1. Andre procesa los videos con `data_prep.py`
2. Reentrena el modelo con `train_solid.py`
3. Sube el modelo nuevo al VPS
4. Helen detectara mejor los gestos de todas las personas
