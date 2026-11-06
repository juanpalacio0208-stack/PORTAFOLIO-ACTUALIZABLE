
import sqlite3
from pathlib import Path

from pwdlib import PasswordHash

from .models import UsuarioRegistro

BASE_DATOS = Path(__file__).resolve().parent / "usuarios.db"

password_hash = PasswordHash.recommended()


def conectar():
    conexion = sqlite3.connect(BASE_DATOS, timeout=10)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_base_datos():
    BASE_DATOS.parent.mkdir(parents=True, exist_ok=True)

    with conectar() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_completo TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE COLLATE NOCASE,
                contrasena_hash TEXT NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1,
                fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def buscar_usuario_por_correo(correo: str):
    inicializar_base_datos()

    with conectar() as conexion:
        fila = conexion.execute(
            "SELECT * FROM usuarios WHERE correo = ?",
            (correo.strip().lower(),),
        ).fetchone()

    return dict(fila) if fila else None


def crear_usuario(datos: UsuarioRegistro):
    inicializar_base_datos()

    correo = str(datos.correo).strip().lower()

    # La contraseña nunca se guarda en texto plano.
    contrasena_segura = password_hash.hash(datos.contrasena)

    with conectar() as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO usuarios (
                nombre_completo,
                correo,
                contrasena_hash
            )
            VALUES (?, ?, ?)
            """,
            (
                datos.nombre_completo,
                correo,
                contrasena_segura,
            ),
        )

        usuario_id = cursor.lastrowid

        fila = conexion.execute(
            """
            SELECT id, nombre_completo, correo, activo
            FROM usuarios
            WHERE id = ?
            """,
            (usuario_id,),
        ).fetchone()

    return dict(fila)
