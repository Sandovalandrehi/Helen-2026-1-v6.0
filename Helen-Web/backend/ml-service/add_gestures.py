"""
Agrega gestos nuevos al dataset existente y re-guarda listo para entrenar.
Uso: py add_gestures.py
"""
import json
import numpy as np
from pathlib import Path
from data_prep import DataPreparator

DATA_DIR      = Path('data')
NEW_DATASET   = Path('gesture_dataset')
NEW_GESTURES  = ['apagar', 'encender']   # los que grabaste

# ── 1. Cargar dataset existente ───────────────────────────────────────────────
print("Cargando dataset existente...")
X_old = np.load(DATA_DIR / 'X_data.npy')
Y_old = np.load(DATA_DIR / 'Y_labels.npy')
with open(DATA_DIR / 'gestures_map.json') as f:
    gestures_map = json.load(f)

print(f"  Existentes: {X_old.shape[0]} muestras, {len(gestures_map)} gestos")
print(f"  Gestos: {list(gestures_map.keys())}")

# ── 2. Procesar videos nuevos ─────────────────────────────────────────────────
print("\nProcesando videos nuevos...")
prep = DataPreparator(NEW_DATASET, seq_length=40)
X_new, Y_new = prep.process_dataset()

# data_prep asigna IDs 0,1 (orden alfabético: apagar=0, encender=1)
# Necesitamos remapear a IDs continuos del dataset existente
next_id = max(gestures_map.values()) + 1
id_remap = {}
for gesture_name, temp_id in prep.gestures_map.items():
    if gesture_name not in gestures_map:
        gestures_map[gesture_name] = next_id
        id_remap[temp_id] = next_id
        print(f"  Nuevo gesto '{gesture_name}' → ID {next_id}")
        next_id += 1
    else:
        print(f"  '{gesture_name}' ya existe (ID {gestures_map[gesture_name]}), omitido")

# Aplicar remap de IDs
Y_new_remapped = np.array([id_remap.get(y, y) for y in Y_new])

# ── 3. Fusionar ───────────────────────────────────────────────────────────────
X_combined = np.concatenate([X_old, X_new], axis=0)
Y_combined  = np.concatenate([Y_old, Y_new_remapped], axis=0)

print(f"\nDataset combinado: {X_combined.shape[0]} muestras, {len(gestures_map)} gestos")
for name, idx in sorted(gestures_map.items(), key=lambda x: x[1]):
    count = np.sum(Y_combined == idx)
    print(f"  {idx}: {name} = {count} muestras")

# ── 4. Guardar ────────────────────────────────────────────────────────────────
np.save(DATA_DIR / 'X_data.npy', X_combined)
np.save(DATA_DIR / 'Y_labels.npy', Y_combined)
with open(DATA_DIR / 'gestures_map.json', 'w') as f:
    json.dump(gestures_map, f, indent=2, ensure_ascii=False)

print(f"\n✅ Dataset actualizado en {DATA_DIR}/")
print(f"   X_data.npy: {X_combined.shape}")
print(f"   gestures_map.json: {len(gestures_map)} gestos")
print("\nYa puedes entrenar con: py train_solid.py")
