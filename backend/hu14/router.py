"""GET/PATCH de la decisión del usuario autenticado (cookie HU-12)."""

from fastapi import APIRouter, Depends

from hu12.security import obtener_usuario_autenticado
from .models import ConsentimientoActualizacion, ConsentimientoRespuesta
from .service import consultar_consentimiento, guardar_consentimiento

router = APIRouter(prefix="/api/notificaciones", tags=["HU-14 Autorizar notificaciones"])


@router.get("/consentimiento", response_model=ConsentimientoRespuesta)
def mi_consentimiento(usuario: dict = Depends(obtener_usuario_autenticado)):
    return consultar_consentimiento(int(usuario["id"]))


@router.patch("/consentimiento", response_model=ConsentimientoRespuesta)
def actualizar_mi_consentimiento(
    datos: ConsentimientoActualizacion,
    usuario: dict = Depends(obtener_usuario_autenticado),
):
    return guardar_consentimiento(int(usuario["id"]), datos.autorizado)
