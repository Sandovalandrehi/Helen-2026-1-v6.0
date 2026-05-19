"""
Merge gestures recolectados de varias personas al formato de data_prep.py.

Estructura esperada de entrada:
    drive_downloads/
        persona1/
            home/
                home_1.mp4
                ...
            dispositivos/
                ...
        persona2/
            home/
                ...

Salida:
    gesture_dataset/
        home/
            persona1_home_1.mp4
            persona2_home_1.mp4
            ...

Uso:
    python merge_gestures.py <carpeta_origen> <carpeta_destino>

Ejemplo:
    python merge_gestures.py ./drive_downloads ./Helen-Web/backend/ml-service/gesture_dataset
"""

import sys
import shutil
from pathlib import Path
from collections import defaultdict


def main():
    if len(sys.argv) < 3:
        print("Uso: python merge_gestures.py <origen> <destino>")
        print("Ejemplo: python merge_gestures.py ./drive_downloads ./Helen-Web/backend/ml-service/gesture_dataset")
        sys.exit(1)

    origen = Path(sys.argv[1])
    destino = Path(sys.argv[2])

    if not origen.exists():
        print(f"ERROR: No existe la carpeta origen: {origen}")
        sys.exit(1)

    destino.mkdir(parents=True, exist_ok=True)

    stats = defaultdict(lambda: defaultdict(int))
    total = 0

    print(f"\nProcesando origen: {origen}")
    print(f"Destino: {destino}\n")

    for persona_dir in sorted(origen.iterdir()):
        if not persona_dir.is_dir():
            continue
        persona = persona_dir.name
        print(f"Persona: {persona}")

        for gesto_dir in sorted(persona_dir.iterdir()):
            if not gesto_dir.is_dir():
                continue
            gesto = gesto_dir.name.lower()

            destino_gesto = destino / gesto
            destino_gesto.mkdir(parents=True, exist_ok=True)

            videos = list(gesto_dir.glob("*.mp4"))
            for i, video in enumerate(videos, start=1):
                # Nombre nuevo: persona_gesto_N.mp4
                nuevo_nombre = f"{persona}_{gesto}_{i}.mp4"
                destino_archivo = destino_gesto / nuevo_nombre

                # Si ya existe (re-run), saltar
                if destino_archivo.exists():
                    continue

                shutil.copy2(video, destino_archivo)
                stats[gesto][persona] += 1
                total += 1

            print(f"  {gesto}: {len(videos)} videos")

    print(f"\n{'='*60}")
    print(f"Total videos copiados: {total}")
    print(f"{'='*60}\n")

    print("Resumen por gesto:")
    for gesto in sorted(stats.keys()):
        total_gesto = sum(stats[gesto].values())
        personas_str = ", ".join(f"{p}({n})" for p, n in stats[gesto].items())
        print(f"  {gesto}: {total_gesto} videos ({personas_str})")

    print("\nListo. Ahora corre data_prep.py:")
    print(f"  python data_prep.py --dataset {destino} --output ./data")


if __name__ == "__main__":
    main()
