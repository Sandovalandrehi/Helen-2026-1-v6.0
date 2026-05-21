"""
Builders de resumen para el LCD del reloj.

Por ahora devuelve placeholders. Cuando se cablee con fuentes reales (API
de clima, storage de alarmas), solo cambian estas funciones — las rutas
(routes.py) no se tocan.
"""


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
        return _placeholder_alarms()

    return {'icon': 'none'}


def _placeholder_weather() -> dict:
    """
    Placeholder de clima.

    TODO: cablear con la fuente real que use el frontend en WeatherScreen
    (probablemente OpenWeather con una API key en env var).
    """
    return {
        'icon': 'sun',
        'temp_c': 22,
        'city': 'Tijuana',
    }


def _placeholder_alarms() -> dict:
    """
    Placeholder de alarmas.

    TODO: persistir alarmas en el backend (archivo o SQLite) cuando se
    creen desde AlarmScreen del frontend, y leer top 3 aquí.
    """
    return {
        'alarms': [
            {'time': '07:30', 'label': 'despertar'},
            {'time': '12:00', 'label': 'medicina'},
        ],
    }
