"""Catálogos fijos (listas de opciones) usados por formularios y plantillas."""

CATEGORIAS_MATERIAL = {
    "vidrio": "Vidrio", "perfil_aluminio": "Perfil de aluminio", "perfil_pvc": "Perfil de PVC",
    "herraje": "Herraje", "accesorio": "Accesorio", "silicon": "Silicón", "tornillo": "Tornillería",
    "empaque": "Empaque / burlete", "rodamiento": "Rodamiento", "cerradura": "Cerradura",
    "consumible": "Otro consumible",
}
CATEGORIAS_PERFIL = ("perfil_aluminio", "perfil_pvc")
UNIDADES = {
    "unidad": "unidad", "ml": "metro lineal (ml)", "m2": "metro cuadrado (m²)",
    "tubo": "tubo", "juego": "juego", "plancha": "plancha", "barra": "barra",
}
ESTADOS_DATOS = {
    "demostracion": "Datos de demostración",
    "supuesto": "Supuesto — pendiente de confirmar",
    "confirmado": "Confirmado por el negocio",
}
ESTADOS = {"pendiente": "Pendiente", "aprobada": "Aprobada", "rechazada": "Rechazada", "cancelada": "Cancelada"}
BASES_MARGEN = {
    "recargo_sobre_costo": "Recargo sobre el costo",
    "margen_sobre_precio": "Margen sobre el precio de venta",
}
ORIGENES_MEDIDA = {
    "cliente": "Proporcionada por el cliente", "tomada": "Tomada por nosotros",
    "fabricacion": "Final de fabricación",
}
REGLAS = {
    "perimetro": "Perímetro (m) × factor", "area": "Área (m²) × factor", "ancho": "Ancho (m) × factor",
    "alto": "Alto (m) × factor", "fijo": "Cantidad fija (= factor)", "por_hoja": "Nº de hojas × factor",
}
TIPOS_INVENTARIO = {"existencia": "Existencia", "sobrante": "Sobrante"}
FORMAS = {"lineal": "Lineal (perfil: largo)", "plana": "Plana (vidrio: ancho × alto)", "unidades": "Por unidades"}
ESTADOS_INVENTARIO = {
    "disponible": "Disponible", "reservado": "Reservado", "reutilizado": "Reutilizado", "baja": "Baja / desperdicio",
}
