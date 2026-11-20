"""Persistencia de consentimiento, inicialmente denegado (opt-in explícito).

HU-15/HU-16 deben consultar tiene_autorizacion(usuario_id) ANTES de
registrar, seleccionar destinatarios o enviar promociones. No envía avisos.
"""

from datetime import datetime, timezone

from hu11 import repository


def inicializar_consentimientos() -> None:
    repository.inicializar_base_datos()
    with repository.conectar() as conexion:
        conexion.execute(
            """CREATE TABLE IF NOT EXISTS consentimientos_notificaciones (
                usuario_id INTEGER PRIMARY KEY,
                autorizado INTEGER NOT NULL DEFAULT 0 CHECK (autorizado IN (0, 1)),
                actualizado_en TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )"""
        )


def consultar_consentimiento(usuario_id: int) -> dict:
    inicializar_consentimientos()
    with repository.conectar() as conexion:
        fila = conexion.execute(
            "SELECT autorizado, actualizado_en "
            "FROM consentimientos_notificaciones WHERE usuario_id = ?",
            (usuario_id,),
        ).fetchone()
    if fila is None:
        return {"autorizado": False, "actualizado_en": None}
    return {"autorizado": bool(fila["autorizado"]), "actualizado_en": fila["actualizado_en"]}


def guardar_consentimiento(usuario_id: int, autorizado: bool) -> dict:
    if type(autorizado) is not bool:
        raise ValueError("La autorización debe ser booleana")
    inicializar_consentimientos()
    actualizado_en = datetime.now(timezone.utc).isoformat()
    with repository.conectar() as conexion:
        conexion.execute(
            """INSERT INTO consentimientos_notificaciones
                   (usuario_id, autorizado, actualizado_en) VALUES (?, ?, ?)
                   ON CONFLICT(usuario_id) DO UPDATE SET
                   autorizado = excluded.autorizado,
                   actualizado_en = excluded.actualizado_en""",
            (usuario_id, int(autorizado), actualizado_en),
        )
    return {"autorizado": autorizado, "actualizado_en": actualizado_en}


def tiene_autorizacion(usuario_id: int) -> bool:
    """Puerta de seguridad para HU-15/HU-16 (no enviar si es False)."""
    return consultar_consentimiento(usuario_id)["autorizado"]
