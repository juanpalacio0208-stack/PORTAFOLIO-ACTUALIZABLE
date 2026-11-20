"""Servicio de recuperación: token aleatorio, 15 min, un solo uso.

El modo de demostración guarda enlaces en el TEMPORAL DEL USUARIO y nunca
se debe habilitar en producción. El endpoint nunca devuelve el token.
"""

import hashlib
import logging
import os
import secrets
import smtplib
import tempfile
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import quote, urlsplit

from fastapi import HTTPException

from hu11 import repository
from hu12.security import inicializar_sesiones

logger = logging.getLogger(__name__)
DURACION_TOKEN_SEGUNDOS = 15 * 60
INTERVALO_SOLICITUD_SEGUNDOS = 60
RUTA_BUZON_DEMO = Path(tempfile.gettempdir()) / "portafolio_hu18_correo_demo.txt"
MENSAJE_GENERICO = (
    "Si el correo está registrado y activo, recibirás instrucciones para "
    "restablecer tu contraseña."
)


def inicializar_recuperaciones() -> None:
    inicializar_sesiones()
    with repository.conectar() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS recuperaciones_contrasena (
                token_hash TEXT PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                vence_en INTEGER NOT NULL,
                creado_en INTEGER NOT NULL,
                usado INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            """
        )


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _url_restauracion(token: str) -> str:
    frontal = os.getenv("HU18_FRONTEND_URL", "http://localhost:5173").rstrip("/")
    # Fragmento (#): el token no se envía al servidor web mediante GET.
    return f"{frontal}/#recuperar_token={quote(token, safe='')}"


def _entregar_enlace(correo: str, token: str) -> None:
    url = _url_restauracion(token)
    modo_demo = os.getenv("HU18_MODO_DEMO") == "1"
    host_frontal = urlsplit(url).hostname

    if modo_demo:
        # Limitado explícitamente al ambiente local.
        if host_frontal not in {"localhost", "127.0.0.1"}:
            logger.error("HU-18: modo demo requiere frontend local.")
            return
        RUTA_BUZON_DEMO.parent.mkdir(parents=True, exist_ok=True)
        with RUTA_BUZON_DEMO.open("a", encoding="utf-8") as archivo:
            archivo.write(
                f"\n[{datetime.now(timezone.utc).isoformat()}] "
                f"Correo destino: {correo}\nEnlace: {url}\n"
            )
        logger.info("HU-18: enlace de prueba disponible en el buzón TEMP local.")
        return

    host = os.getenv("HU18_SMTP_HOST")
    remitente = os.getenv("HU18_SMTP_FROM")
    if not host or not remitente:
        logger.warning("HU-18: SMTP no configurado; correo no enviado.")
        return

    mensaje = EmailMessage()
    mensaje["From"] = remitente
    mensaje["To"] = correo
    mensaje["Subject"] = "Recuperación de contraseña - Portafolio Actualizable"
    mensaje.set_content(
        "Solicitaste recuperar tu contraseña.\n\n"
        f"Abre este enlace dentro de los próximos 15 minutos:\n{url}\n\n"
        "Si no solicitaste esto, ignora el mensaje."
    )

    try:
        puerto = int(os.getenv("HU18_SMTP_PORT", "587"))
        with smtplib.SMTP(host, puerto, timeout=10) as smtp:
            smtp.starttls()
            usuario_smtp = os.getenv("HU18_SMTP_USER")
            clave_smtp = os.getenv("HU18_SMTP_PASSWORD")
            if usuario_smtp and clave_smtp:
                smtp.login(usuario_smtp, clave_smtp)
            smtp.send_message(mensaje)
    except (OSError, smtplib.SMTPException, ValueError):
        # El usuario nunca recibe información sobre la existencia del correo.
        logger.exception("HU-18: no se pudo entregar el correo de recuperación.")


def solicitar_recuperacion(correo: str) -> str:
    """Respuesta uniforme exista o no el usuario; máximo 1 token/min por usuario."""
    inicializar_recuperaciones()
    usuario = repository.buscar_usuario_por_correo(correo)
    if not usuario or not usuario["activo"]:
        return MENSAJE_GENERICO

    ahora = int(time.time())
    token = secrets.token_urlsafe(32)

    with repository.conectar() as conexion:
        conexion.execute("BEGIN IMMEDIATE")
        reciente = conexion.execute(
            """
            SELECT 1 FROM recuperaciones_contrasena
            WHERE usuario_id = ? AND creado_en > ?
            LIMIT 1
            """,
            (usuario["id"], ahora - INTERVALO_SOLICITUD_SEGUNDOS),
        ).fetchone()
        if reciente:
            return MENSAJE_GENERICO

        # Un nuevo enlace invalida los anteriores.
        conexion.execute(
            "UPDATE recuperaciones_contrasena SET usado = 1 WHERE usuario_id = ?",
            (usuario["id"],),
        )
        conexion.execute(
            """
            INSERT INTO recuperaciones_contrasena
              (token_hash, usuario_id, vence_en, creado_en)
            VALUES (?, ?, ?, ?)
            """,
            (
                _hash_token(token),
                usuario["id"],
                ahora + DURACION_TOKEN_SEGUNDOS,
                ahora,
            ),
        )

    _entregar_enlace(str(usuario["correo"]), token)
    return MENSAJE_GENERICO


def _consultar_token(conexion, token_hash: str):
    return conexion.execute(
        """
        SELECT r.usuario_id, r.vence_en, r.usado, u.activo
        FROM recuperaciones_contrasena r
        JOIN usuarios u ON u.id = r.usuario_id
        WHERE r.token_hash = ?
        """,
        (token_hash,),
    ).fetchone()


def _token_valido(fila, ahora: int) -> bool:
    return bool(
        fila is not None
        and not fila["usado"]
        and fila["vence_en"] > ahora
        and fila["activo"]
    )


def restablecer_contrasena(token: str, nueva_contrasena: str) -> None:
    """Consume el enlace en una transacción e invalida sesiones activas."""
    inicializar_recuperaciones()
    ahora = int(time.time())
    token_hash = _hash_token(token)

    # Primero se comprueba el token para no gastar Argon2 con tokens inválidos.
    with repository.conectar() as conexion:
        fila = _consultar_token(conexion, token_hash)
    if not _token_valido(fila, ahora):
        raise HTTPException(
            status_code=400,
            detail="El enlace no es válido o ya venció. Solicita uno nuevo.",
        )

    hash_nuevo = repository.password_hash.hash(nueva_contrasena)

    with repository.conectar() as conexion:
        conexion.execute("BEGIN IMMEDIATE")
        # Segunda comprobación bajo bloqueo: evita reutilización simultánea.
        fila = _consultar_token(conexion, token_hash)
        if not _token_valido(fila, int(time.time())):
            raise HTTPException(
                status_code=400,
                detail="El enlace no es válido o ya venció. Solicita uno nuevo.",
            )

        conexion.execute(
            "UPDATE usuarios SET contrasena_hash = ? WHERE id = ?",
            (hash_nuevo, fila["usuario_id"]),
        )
        conexion.execute(
            "UPDATE recuperaciones_contrasena SET usado = 1 WHERE usuario_id = ?",
            (fila["usuario_id"],),
        )
        conexion.execute(
            "DELETE FROM sesiones WHERE usuario_id = ?",
            (fila["usuario_id"],),
        )
