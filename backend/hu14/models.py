"""Esquemas de la preferencia de notificaciones de un comprador autenticado."""

from pydantic import BaseModel, StrictBool


class ConsentimientoActualizacion(BaseModel):
    autorizado: StrictBool


class ConsentimientoRespuesta(BaseModel):
    autorizado: bool
    actualizado_en: str | None = None
