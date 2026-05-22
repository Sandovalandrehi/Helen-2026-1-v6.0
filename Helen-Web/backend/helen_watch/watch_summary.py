"""
Builders de resumen para el LCD del reloj.

Las alarmas reales viven en el localStorage del navegador (frontend). El
frontend las sincroniza a este backend via POST /watch_alarms; aqui se
guardan en memoria y el reloj las consulta via GET /watch_summary?cmd=alarma.

Si el frontend nunca sincronizo (backend recien arrancado), se devuelve un
placeholder para que el reloj no muestre una pantalla vacia.
"""

# None = el frontend nunca sincronizo. Lista = alarmas reales del frontend.
_synced_alarms = None


def set_alarms(alarms: list) -> None:
    """
    Guarda la lista de alarmas que el frontend sincronizo.

    Args:
        alarms: lista de dicts, cada uno con al menos 'time' y 'label'.
    """
    global _synced_alarms
    _synced_alarms = alarms


def build_summary(cmd: str) -> dict:
    """
    Construye el payload de resumen según el comando del reloj.

    Args:
        cmd: 'home', 'clima', 'alarma' o cualquier otro string.

    Returns:
        Diccionario JSON-serializable listo para devolver al reloj.
    """
    if cmd == 'home':
        return {'icon': 'home'}

    if cmd == 'clima':
        return _placeholder_weather()

    if cmd == 'alarma':
        if _synced_alarms is not None:
            return {'alarms': _synced_alarms}
        return _placeholder_alarms()

    return {'icon': 'none'}


def _placeholder_weather() -> dict:
    """
    Placeholder de clima.

    TODO: cablear con la fuente real que use el frontend en WeatherScreen.
    """
    return {
        'icon': 'sun',
        'temp_c': 22,
        'city': 'Tijuana',
    }


def _placeholder_alarms() -> dict:
    """
    Placeholder de alarmas: solo se usa si el frontend aun no sincronizo.
    """
    return {
        'alarms': [
            {'time': '07:30', 'label': 'despertar'},
            {'time': '12:00', 'label': 'medicina'},
        ],
    }
