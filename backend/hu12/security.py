
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status

from hu11 import repository

NOMBRE_COOKIE = "portafolio_sesion"
DURACION_SESION = timedelta(hours=8)


def inicializar_sesiones():
    repository.inicializar_base_datos()

    with repository.conectar() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS sesiones (
                token_hash TEXT PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                fecha_expiracion TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            """
        )


def crear_sesion(usuario_id: int) -> str:
    inicializar_sesiones()

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    expiracion = datetime.now(timezone.utc) + DURACION_SESION

    with repository.conectar() as conexion:
        conexion.execute(
            """
            INSERT INTO sesiones (
                token_hash,
                usuario_id,
                fecha_expiracion
            )
            VALUES (?, ?, ?)
            """,
            (token_hash, usuario_id, expiracion.isoformat()),
        )

    return token


def obtener_usuario_autenticado(request: Request) -> dict:
    token = request.cookies.get(NOMBRE_COOKIE)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes iniciar sesión.",
        )

    token_hash = hashlib.sha256(token.encode()).hexdigest()

    inicializar_sesiones()

    with repository.conectar() as conexion:
        fila = conexion.execute(
            """
            SELECT
                usuarios.id,
                usuarios.nombre_completo,
                usuarios.correo,
                usuarios.activo,
                sesiones.fecha_expiracion
            FROM sesiones
            JOIN usuarios
                ON usuarios.id = sesiones.usuario_id
            WHERE sesiones.token_hash = ?
            """,
            (token_hash,),
        ).fetchone()

    if fila is None:
        raise HTTPException(
            status_code=401,
            detail="La sesión no es válida.",
        )

    expiracion = datetime.fromisoformat(fila["fecha_expiracion"])

    if datetime.now(timezone.utc) >= expiracion:
        eliminar_sesion(token)
        raise HTTPException(
            status_code=401,
            detail="La sesión ha expirado.",
        )

    if not fila["activo"]:
        raise HTTPException(
            status_code=403,
            detail="La cuenta está desactivada.",
        )

    return {
        "id": fila["id"],
        "nombre_completo": fila["nombre_completo"],
        "correo": fila["correo"],
        "activo": bool(fila["activo"]),
    }


def eliminar_sesion(token: str | None):
    if not token:
        return

    inicializar_sesiones()
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    with repository.conectar() as conexion:
        conexion.execute(
            "DELETE FROM sesiones WHERE token_hash = ?",
            (token_hash,),
        )
