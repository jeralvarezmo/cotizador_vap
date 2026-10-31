"""Estados COMERCIALES de una cotización y transiciones permitidas (PURO).

Los estados operativos del trabajo (producción, instalación, finalización)
pertenecen a una etapa posterior y se mantienen separados.
SUPUESTO PENDIENTE DE CONFIRMAR: una cotización aprobada todavía puede cancelarse.
"""

# Cada estado apunta a la lista de estados a los que puede pasar.
TRANSICIONES = {
    "pendiente": ["aprobada", "rechazada", "cancelada"],
    "aprobada": ["cancelada"],
    "rechazada": [],
    "cancelada": [],
}


def validar_transicion(actual, nuevo):
    """Lanza ValueError si el cambio de estado no está permitido."""
    if actual not in TRANSICIONES:
        raise ValueError(f"Estado actual desconocido: {actual}")
    if nuevo not in TRANSICIONES[actual]:
        raise ValueError(f"No se puede pasar de «{actual}» a «{nuevo}».")
