"""HU-15/16/19: notificaciones internas y solicitudes por cuenta.

El canal es la bandeja dentro de la aplicación (no correo ni push).
La autorización de HU-14 se consulta en la base de datos en cada envío.
"""
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from hu11 import repository
from hu12.security import obtener_usuario_autenticado
from hu08 import router as solicitudes

router = APIRouter(prefix="/api", tags=["HU-15, HU-16, HU-19"])


def preparar_bd():
    repository.inicializar_base_datos()
    with repository.conectar() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            titulo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            creada TEXT NOT NULL,
            leida INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )""")


class Consentimiento(BaseModel):
    autorizado: bool


class Envio(BaseModel):
    tipo: str
    titulo: str = Field(min_length=3, max_length=120)
    mensaje: str = Field(min_length=3, max_length=1000)


@router.get("/notificaciones/consentimiento")
def consultar_consentimiento(usuario=Depends(obtener_usuario_autenticado)):
    preparar_bd()
    with repository.conectar() as db:
        row = db.execute("SELECT notificaciones_autorizadas FROM usuarios WHERE id=?", (usuario["id"],)).fetchone()
    return {"autorizado": bool(row[0]) if row else False}


@router.put("/notificaciones/consentimiento")
def guardar_consentimiento(datos: Consentimiento, usuario=Depends(obtener_usuario_autenticado)):
    preparar_bd()
    with repository.conectar() as db:
        db.execute("UPDATE usuarios SET notificaciones_autorizadas=? WHERE id=?", (int(datos.autorizado), usuario["id"]))
    return {"autorizado": datos.autorizado}


@router.get("/notificaciones/mias")
def mis_notificaciones(usuario=Depends(obtener_usuario_autenticado)):
    preparar_bd()
    with repository.conectar() as db:
        rows = db.execute("""SELECT id, tipo, titulo, mensaje, creada, leida FROM notificaciones
             WHERE usuario_id=? ORDER BY id DESC LIMIT 100""", (usuario["id"],)).fetchall()
    return [dict(row) for row in rows]


@router.patch("/notificaciones/{notificacion_id}/leida")
def marcar_leida(notificacion_id: int, usuario=Depends(obtener_usuario_autenticado)):
    preparar_bd()
    with repository.conectar() as db:
        cursor = db.execute("UPDATE notificaciones SET leida=1 WHERE id=? AND usuario_id=?", (notificacion_id, usuario["id"]))
    if not cursor.rowcount:
        raise HTTPException(404, "Notificación no encontrada")
    return {"mensaje": "Notificación marcada como leída"}


def exigir_administradora(usuario):
    # Solo correos autorizados por variable de entorno del servidor.
    correos = {x.strip().lower() for x in os.getenv("PORTAFOLIO_ADMIN_EMAILS", "").split(",") if x.strip()}
    if usuario["correo"].lower() not in correos:
        raise HTTPException(403, "Solo la administradora puede enviar notificaciones")


@router.get("/admin/notificaciones/permiso")
def permiso_administradora(usuario=Depends(obtener_usuario_autenticado)):
    exigir_administradora(usuario)
    return {"administradora": True}


@router.post("/admin/notificaciones", status_code=201)
def enviar_notificaciones(datos: Envio, usuario=Depends(obtener_usuario_autenticado)):
    exigir_administradora(usuario)
    if datos.tipo not in {"nuevo_producto", "descuento", "promocion"}:
        raise HTTPException(422, "Tipo de notificación no permitido")
    preparar_bd()
    fecha = datetime.now(timezone.utc).isoformat()
    with repository.conectar() as db:
        destinatarios = db.execute("SELECT id FROM usuarios WHERE activo=1 AND notificaciones_autorizadas=1").fetchall()
        db.executemany("""INSERT INTO notificaciones (usuario_id,tipo,titulo,mensaje,creada)
            VALUES (?,?,?,?,?)""", [(r[0], datos.tipo, datos.titulo.strip(), datos.mensaje.strip(), fecha) for r in destinatarios])
    return {"mensaje": "Notificaciones entregadas en la bandeja interna", "destinatarios": len(destinatarios)}


@router.get("/solicitudes/mias")
def historial_solicitudes(usuario=Depends(obtener_usuario_autenticado)):
    # No atribuye pedidos anónimos previos mediante correo o teléfono.
    with solicitudes._bloqueo:
        try:
            archivo = solicitudes.ARCHIVO_SOLICITUDES
            registros = json.loads(archivo.read_text(encoding="utf-8")) if archivo.exists() else []
            if not isinstance(registros, list):
                raise ValueError("Formato inválido")
        except (OSError, ValueError) as exc:
            raise HTTPException(500, "No se pudo consultar el historial") from exc
    return sorted([
        {k: item.get(k) for k in ("id", "producto_id", "producto_nombre", "estado", "fecha_creacion", "fecha_actualizacion")}
        for item in registros if item.get("usuario_id") == usuario["id"]
    ], key=lambda x: x.get("fecha_creacion") or "", reverse=True)
